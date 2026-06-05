"""LFS-micro calibration: find the Spec that best fits the BoC Valet series.

Dev tool — not part of the monthly refresh. Run once to tune parameters;
the winning Spec is then frozen as DEFAULT_SPEC in spec.py.

What this module does:

  1. Download all PUMF months from 2015 to the latest available
     (11 annual bundles + recent monthlies, ~322 MB total).

  2. Harmonize each month to the canonical employee DataFrame.

  3. Run the engine under a grid of Spec candidates:
     weighted:     True, False
     smoothing:    "raw", "ma3"
     ob_reference: "base", "current"
     (8 combinations total)

  4. Score each candidate against data/raw/lfs_micro.csv (BoC Valet
     INDINF_LFSMICRO_M, monthly y/y %) over the overlap window.
     Metrics: RMSE, MAE, Pearson correlation.

  5. NAICS spot-check: compare NAICS_21 code distributions between a
     2015 month and 2026-04 to verify the Feb 2025 re-release consistently
     applied NAICS 2022 codes throughout history.

  6. Write the calibration report to:
       claude-ref/research/lfs_micro/calibration_report.md

  7. Write the replicated series (winning Spec) via pipeline.io.meta.write_series
     to data/processed/lfs_micro_replication.csv + meta sidecar.

Run:
    python -m pipeline.lfs_micro.calibrate [--start-year 2015] [--force-download]

The --start-year default is 2015 (earliest PUMF in the Feb 2025 re-release).
Calibration overlap starts 2016-01 (first y/y requires 2015 as base year).
"""

from __future__ import annotations

import argparse
import logging
import sys
import time
from datetime import datetime, timezone
from itertools import product
from pathlib import Path
from typing import Iterator

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------

_PROJECT_ROOT = Path(__file__).parents[2]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from pipeline.io.meta import SeriesMeta, write_series  # noqa: E402
from pipeline.lfs_pumf.download import (  # noqa: E402
    get_month,
    latest_available_month,
)
from pipeline.lfs_pumf.harmonize import harmonize  # noqa: E402
from pipeline.lfs_pumf.sanity import SanityError, run_sanity_checks  # noqa: E402
from pipeline.lfs_micro.engine import run_engine  # noqa: E402
from pipeline.lfs_micro.spec import Spec  # noqa: E402

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("lfs_micro.calibrate")

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

_BOC_BENCHMARK_PATH = _PROJECT_ROOT / "data" / "raw" / "lfs_micro.csv"
_PROCESSED_DIR = _PROJECT_ROOT / "data" / "processed"
_REPORT_DIR = _PROJECT_ROOT / "claude-ref" / "research" / "lfs_micro"
_RAW_PUMF_DIR = _PROJECT_ROOT / "data" / "raw" / "lfs_pumf"


# ---------------------------------------------------------------------------
# Spec grid
# ---------------------------------------------------------------------------

def _spec_grid() -> list[Spec]:
    """Return all 8 Spec candidates for the calibration grid."""
    specs = []
    for weighted, smoothing, ob_ref in product(
        [True, False],
        ["raw", "ma3"],
        ["base", "current"],
    ):
        specs.append(Spec(
            weighted=weighted,
            smoothing=smoothing,
            ob_reference=ob_ref,
            min_cell_count=30,
        ))
    return specs


# ---------------------------------------------------------------------------
# Download and harmonize all months
# ---------------------------------------------------------------------------

def _iter_year_months(start_year: int, end_year: int, end_month: int) -> Iterator[tuple[int, int]]:
    """Yield (year, month) pairs from start_year-01 through end_year-end_month."""
    for y in range(start_year, end_year + 1):
        for m in range(1, 13):
            if y == end_year and m > end_month:
                break
            yield y, m


def acquire_all_months(
    start_year: int = 2015,
    force_download: bool = False,
) -> dict[str, Path]:
    """Download and sanity-check all PUMF months from start_year to latest.

    Returns:
        Dict {YYYY-MM: parquet_path} for every successfully acquired month.
    """
    logger.info("Probing for latest available PUMF month...")
    end_year, end_month = latest_available_month()
    logger.info("Latest PUMF: %04d-%02d", end_year, end_month)

    paths: dict[str, Path] = {}
    failed: list[str] = []

    for year, month in _iter_year_months(start_year, end_year, end_month):
        key = f"{year:04d}-{month:02d}"
        try:
            path = get_month(year, month, force=force_download)
            paths[key] = path
            logger.info("  acquired %s", key)
        except Exception as exc:
            logger.error("  FAILED to acquire %s: %s", key, exc)
            failed.append(key)

    if failed:
        logger.warning(
            "%d months failed to download: %s", len(failed), failed[:10]
        )
        if len(failed) > len(paths) * 0.1:
            raise RuntimeError(
                f"Too many download failures ({len(failed)} of "
                f"{len(paths)+len(failed)}). "
                "StatCan may be down. Aborting calibration."
            )

    return paths


def harmonize_all_months(
    parquet_paths: dict[str, Path],
) -> dict[str, pd.DataFrame]:
    """Harmonize all parquet files, running sanity checks on each.

    Skips months that fail harmonization or sanity checks (logs the failure).
    Returns only successfully harmonized months.
    """
    frames: dict[str, pd.DataFrame] = {}

    for key, path in sorted(parquet_paths.items()):
        try:
            df = harmonize(path)
            # Read total row count from parquet for employee-share check
            import pyarrow.parquet as pq_io
            total_rows = pq_io.read_metadata(path).num_rows
            run_sanity_checks(df, parquet_path=path, total_row_count=total_rows)
            frames[key] = df
        except SanityError as exc:
            logger.error("Sanity check failed for %s: %s", key, exc)
        except Exception as exc:
            logger.error("Harmonize failed for %s: %s", key, exc)

    logger.info(
        "Harmonized %d/%d months successfully.", len(frames), len(parquet_paths)
    )
    return frames


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

def _load_boc_benchmark() -> pd.Series:
    """Load BoC Valet INDINF_LFSMICRO_M from local CSV.

    Returns a Series indexed by ISO date strings (YYYY-MM-01) with float values
    (y/y percent change).
    """
    df = pd.read_csv(_BOC_BENCHMARK_PATH, parse_dates=["date"])
    df = df.set_index("date").sort_index()
    # Normalize index to YYYY-MM-01 strings for alignment
    df.index = df.index.strftime("%Y-%m-01")
    return df["value"].astype(float)


def _score(
    replication: pd.DataFrame,
    benchmark: pd.Series,
    col: str = "underlying_pct",
) -> dict:
    """Score the replication series against the BoC benchmark.

    Args:
        replication: Engine output DataFrame (must have 'date' and col columns).
        benchmark:   BoC Valet series (index = YYYY-MM-01 strings, values = pct).
        col:         Column in replication to compare (default: 'underlying_pct').

    Returns:
        Dict with keys: rmse, mae, corr, n_overlap, overlap_start, overlap_end.
    """
    if replication.empty or col not in replication.columns:
        return {"rmse": np.nan, "mae": np.nan, "corr": np.nan, "n_overlap": 0}

    rep = replication.set_index("date")[col].dropna()
    common = rep.index.intersection(benchmark.index)

    if len(common) < 6:
        return {"rmse": np.nan, "mae": np.nan, "corr": np.nan, "n_overlap": len(common)}

    r = rep.loc[common]
    b = benchmark.loc[common]

    diff = r - b
    rmse = float(np.sqrt((diff ** 2).mean()))
    mae = float(diff.abs().mean())
    corr = float(r.corr(b))

    return {
        "rmse": round(rmse, 4),
        "mae": round(mae, 4),
        "corr": round(corr, 4),
        "n_overlap": len(common),
        "overlap_start": common.min(),
        "overlap_end": common.max(),
    }


# ---------------------------------------------------------------------------
# NAICS spot-check
# ---------------------------------------------------------------------------

def naics_spot_check(
    frames: dict[str, pd.DataFrame],
    early_year: int = 2015,
    late_key: str = "2026-04",
) -> dict:
    """Compare NAICS_21 distributions between earliest and latest month.

    Checks:
      - Same set of NAICS codes in both periods.
      - Code counts roughly consistent (no codes completely absent in one era).

    Returns:
        Dict with 'consistent' (bool), 'codes_early', 'codes_late',
        'codes_only_early', 'codes_only_late', 'note'.
    """
    # Find the earliest month for the given early_year
    early_key = None
    for m in range(1, 13):
        k = f"{early_year:04d}-{m:02d}"
        if k in frames:
            early_key = k
            break

    if early_key is None:
        return {
            "consistent": None,
            "note": f"No data for {early_year} to compare.",
        }

    if late_key not in frames:
        late_key = max(frames.keys())

    df_early = frames[early_key]
    df_late = frames[late_key]

    codes_early = set(df_early["naics_21"].dropna().unique().astype(int))
    codes_late = set(df_late["naics_21"].dropna().unique().astype(int))

    only_early = sorted(codes_early - codes_late)
    only_late = sorted(codes_late - codes_early)
    consistent = (only_early == [] and only_late == [])

    note = (
        "NAICS_21 codes are identical between "
        f"{early_key} and {late_key} — Feb 2025 re-release consistently "
        "applied NAICS 2022 throughout history."
        if consistent else
        f"NAICS_21 divergence: codes in {early_key} only: {only_early}; "
        f"codes in {late_key} only: {only_late}. "
        "Pre/post-2025 industry comparability is compromised."
    )

    return {
        "consistent": consistent,
        "early_key": early_key,
        "late_key": late_key,
        "codes_early": sorted(codes_early),
        "codes_late": sorted(codes_late),
        "codes_only_early": only_early,
        "codes_only_late": only_late,
        "note": note,
    }


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------

def _last_12_comparison(
    replication: pd.DataFrame,
    benchmark: pd.Series,
    col: str = "underlying_pct",
) -> list[dict]:
    """Return per-month comparison for the last 12 available months."""
    if replication.empty or col not in replication.columns:
        return []

    rep = replication.set_index("date")[col].dropna()
    common = rep.index.intersection(benchmark.index)
    if common.empty:
        return []

    last_12 = sorted(common)[-12:]
    rows = []
    for d in last_12:
        rows.append({
            "date": d,
            "ours": round(float(rep.loc[d]), 3),
            "boc": round(float(benchmark.loc[d]), 3),
            "diff": round(float(rep.loc[d] - benchmark.loc[d]), 3),
        })
    return rows


def _write_report(
    grid_results: list[dict],
    winner_spec: Spec,
    winner_scores: dict,
    winner_series: pd.DataFrame,
    benchmark: pd.Series,
    naics_check: dict,
    runtime_sec: float,
    report_path: Path,
) -> None:
    """Write the calibration report to a markdown file."""
    report_path.parent.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    lines = [
        "# LFS-micro Calibration Report",
        f"",
        f"Generated: {now}",
        f"",
        f"## Calibration grid results",
        f"",
        f"Benchmark: BoC Valet `INDINF_LFSMICRO_M` (y/y %, monthly)",
        f"Overlap window: 2016-01 onwards (PUMF y/y starts 2016 with 2015 base year)",
        f"",
        "| weighted | smoothing | ob_reference | RMSE | MAE | corr | n |",
        "|----------|-----------|--------------|------|-----|------|---|",
    ]

    for r in sorted(grid_results, key=lambda x: x.get("rmse", 99) or 99):
        spec = r["spec"]
        scores = r["scores"]
        rmse = f"{scores.get('rmse', 'n/a')}" if scores.get("rmse") is not None else "n/a"
        mae = f"{scores.get('mae', 'n/a')}" if scores.get("mae") is not None else "n/a"
        corr = f"{scores.get('corr', 'n/a')}" if scores.get("corr") is not None else "n/a"
        n = scores.get("n_overlap", "n/a")
        marker = " **WINNER**" if r.get("winner") else ""
        lines.append(
            f"| {spec.weighted} | {spec.smoothing} | {spec.ob_reference} "
            f"| {rmse} | {mae} | {corr} | {n} |{marker}"
        )

    lines += [
        "",
        "## Winning Spec",
        "",
        f"- weighted: {winner_spec.weighted}",
        f"- smoothing: {winner_spec.smoothing}",
        f"- ob_reference: {winner_spec.ob_reference}",
        f"- min_cell_count: {winner_spec.min_cell_count}",
        "",
        f"RMSE: {winner_scores.get('rmse')} pp",
        f"MAE:  {winner_scores.get('mae')} pp",
        f"corr: {winner_scores.get('corr')}",
        f"Overlap: {winner_scores.get('overlap_start')} to {winner_scores.get('overlap_end')} "
        f"(n={winner_scores.get('n_overlap')})",
        "",
        "## Last 12 months comparison (ours vs BoC)",
        "",
        "| date | ours | BoC | diff |",
        "|------|------|-----|------|",
    ]

    for row in _last_12_comparison(winner_series, benchmark):
        lines.append(
            f"| {row['date']} | {row['ours']} | {row['boc']} | {row['diff']:+.3f} |"
        )

    lines += [
        "",
        "## NAICS spot-check",
        "",
        naics_check.get("note", "No NAICS check performed."),
        "",
        f"- Early month: {naics_check.get('early_key', 'n/a')}",
        f"- Late month:  {naics_check.get('late_key', 'n/a')}",
        f"- Consistent:  {naics_check.get('consistent', 'n/a')}",
    ]

    if not naics_check.get("consistent"):
        lines += [
            f"- Codes only in early: {naics_check.get('codes_only_early')}",
            f"- Codes only in late:  {naics_check.get('codes_only_late')}",
        ]

    lines += [
        "",
        f"## Runtime",
        "",
        f"Full refresh (download + harmonize + 8-spec grid): {runtime_sec:.0f} seconds",
        "",
        "## Notes",
        "",
        "- Composition effect captures employment-share shifts across categories.",
        "- Underlying wage growth = wage-return changes for a fixed worker mix.",
        "- BoC SAN 2024-23 uses y/y % on the same PUMF data; near-exact replication",
        "  is achievable since we use the same source. Residual divergence comes from",
        "  exact spec choices (reference convention, smoothing, bin granularity).",
        "- Log-point to percent conversion: pct = (exp(log_pt) - 1) * 100.",
        "  For values near 3-4%, this differs from raw log-points by <0.1pp.",
    ]

    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    logger.info("Calibration report written to %s", report_path)


# ---------------------------------------------------------------------------
# Main calibration routine
# ---------------------------------------------------------------------------

def run_calibration(
    start_year: int = 2015,
    force_download: bool = False,
) -> Spec:
    """Run the full calibration and return the winning Spec.

    Side effects:
      - Downloads all PUMF months (content-addressable; idempotent).
      - Writes claude-ref/research/lfs_micro/calibration_report.md.
      - Writes data/processed/lfs_micro_replication.csv + meta sidecar.

    Returns:
        The winning Spec (best RMSE vs BoC benchmark).
    """
    t0 = time.time()

    # --- Step 1: Acquire all months ---
    logger.info("=== LFS-micro calibration: acquiring PUMF months ===")
    parquet_paths = acquire_all_months(start_year=start_year, force_download=force_download)

    # --- Step 2: Harmonize ---
    logger.info("=== Harmonizing %d months ===", len(parquet_paths))
    frames = harmonize_all_months(parquet_paths)
    if len(frames) < 14:
        raise RuntimeError(
            f"Only {len(frames)} months harmonized successfully. "
            "Need at least 14 for any y/y observations. Aborting."
        )

    # --- Step 3: NAICS spot-check ---
    logger.info("=== NAICS spot-check ===")
    late_key = max(frames.keys())
    naics_check = naics_spot_check(frames, early_year=start_year, late_key=late_key)
    logger.info("NAICS check: %s", naics_check["note"])

    # --- Step 4: Load BoC benchmark ---
    logger.info("=== Loading BoC benchmark ===")
    benchmark = _load_boc_benchmark()
    logger.info(
        "BoC benchmark: %d obs, %s to %s",
        len(benchmark), benchmark.index.min(), benchmark.index.max()
    )

    # --- Step 5: Grid search ---
    specs = _spec_grid()
    logger.info("=== Running %d-spec grid ===", len(specs))

    grid_results = []
    best_spec = None
    best_scores = {"rmse": float("inf")}
    best_series = None

    for i, spec in enumerate(specs, 1):
        logger.info(
            "  [%d/%d] weighted=%s smoothing=%s ob_ref=%s",
            i, len(specs), spec.weighted, spec.smoothing, spec.ob_reference
        )
        try:
            series = run_engine(frames, spec=spec)
            scores = _score(series, benchmark, col="underlying_pct")
        except Exception as exc:
            logger.error("    Engine failed: %s", exc)
            scores = {"rmse": np.nan, "mae": np.nan, "corr": np.nan, "n_overlap": 0}
            series = pd.DataFrame()

        logger.info(
            "    RMSE=%.3f MAE=%.3f corr=%.3f n=%d",
            scores.get("rmse") or float("nan"),
            scores.get("mae") or float("nan"),
            scores.get("corr") or float("nan"),
            scores.get("n_overlap", 0),
        )

        is_winner = (
            scores.get("rmse") is not None
            and not np.isnan(scores["rmse"])
            and scores["rmse"] < best_scores["rmse"]
        )
        if is_winner:
            best_spec = spec
            best_scores = scores
            best_series = series

        grid_results.append({
            "spec": spec,
            "scores": scores,
            "winner": False,  # updated below
        })

    if best_spec is None:
        raise RuntimeError("All Spec candidates failed calibration. Check data and engine.")

    # Mark the winner in grid_results
    for r in grid_results:
        if r["spec"] == best_spec:
            r["winner"] = True

    runtime_sec = time.time() - t0
    logger.info(
        "=== Winner: weighted=%s smoothing=%s ob_ref=%s "
        "RMSE=%.3f corr=%.3f (%.0fs) ===",
        best_spec.weighted, best_spec.smoothing, best_spec.ob_reference,
        best_scores["rmse"], best_scores["corr"], runtime_sec
    )

    # --- Step 6: Write calibration report ---
    report_path = _REPORT_DIR / "calibration_report.md"
    _write_report(
        grid_results=grid_results,
        winner_spec=best_spec,
        winner_scores=best_scores,
        winner_series=best_series,
        benchmark=benchmark,
        naics_check=naics_check,
        runtime_sec=runtime_sec,
        report_path=report_path,
    )

    # --- Step 7: Write replicated series ---
    _write_replication_series(best_spec, best_series, best_scores)

    return best_spec


def _write_replication_series(
    spec: Spec,
    series: pd.DataFrame,
    scores: dict,
) -> None:
    """Write the winning replication series to data/processed/."""
    if series is None or series.empty:
        logger.warning("No replication series to write.")
        return

    # Canonical output: date, underlying_pct (the headline composition-adjusted series)
    out = series[["date", "underlying_pct", "composition_pct", "raw_mean_pct",
                  "total_fitted_pct", "n_obs_curr", "n_obs_base",
                  "r2_curr", "r2_base"]].copy()
    out = out.dropna(subset=["underlying_pct"])

    meta = SeriesMeta(
        name="lfs_micro_replication",
        source="Statistics Canada LFS PUMF (Sibley Creek O-B replication of BoC SAN 2024-23)",
        source_url=(
            "https://www150.statcan.gc.ca/n1/pub/71m0001x/71m0001x2021001-eng.htm"
        ),
        source_id=(
            f"LFS PUMF 2015-{max(series['date'])[:7]} via annual hist/ bundles + recent monthly; "
            f"BoC SAN 2024-23 methodology"
        ),
        units="% y/y (composition-adjusted underlying wage growth)",
        frequency="monthly",
        notes=(
            f"Oaxaca-Blinder two-fold decomposition of WLS log-wage regression on "
            f"LFS PUMF monthly cross-sections. "
            f"Spec: weighted={spec.weighted}, smoothing={spec.smoothing}, "
            f"ob_reference={spec.ob_reference}. "
            f"Calibrated vs BoC Valet INDINF_LFSMICRO_M: "
            f"RMSE={scores.get('rmse')}pp, corr={scores.get('corr')}, "
            f"n_overlap={scores.get('n_overlap')}. "
            f"Log-points converted to pct via exp()-1. "
            f"Reference: Bounajm/Devakos/Galassi, BoC SAN 2024-23."
        ),
        transform="oaxaca_blinder_lfs_micro",
    )

    csv_path, meta_path = write_series(out, meta, _PROCESSED_DIR, date_col="date")
    logger.info("Wrote replication series: %s", csv_path)
    logger.info("Wrote meta sidecar:       %s", meta_path)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="LFS-micro calibration: find best Spec vs BoC INDINF_LFSMICRO_M"
    )
    parser.add_argument(
        "--start-year", type=int, default=2015,
        help="Earliest PUMF year to download (default: 2015)"
    )
    parser.add_argument(
        "--force-download", action="store_true",
        help="Re-download all PUMF files even if cached"
    )
    args = parser.parse_args(argv)

    winner = run_calibration(
        start_year=args.start_year,
        force_download=args.force_download,
    )

    print("\nCalibration complete.")
    print(f"Winning Spec: {winner.as_dict()}")
    print("Report: claude-ref/research/lfs_micro/calibration_report.md")
    print("Series: data/processed/lfs_micro_replication.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
