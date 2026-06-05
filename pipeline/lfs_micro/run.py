"""CLI entry point for the LFS-micro replication tool.

    python -m pipeline.lfs_micro.run                    # auto-discovers newest PUMF
    python -m pipeline.lfs_micro.run --month 2026-05    # pin to a specific month
    python -m pipeline.lfs_micro.run --force-download   # re-download all PUMF zips
    python -m pipeline.lfs_micro.run --zip PATH         # inject a local zip (escape hatch)

Flow:
  1. Discover the latest available PUMF month (probes StatCan URLs backward).
  2. Download/parquet any months not already cached.
  3. Run the sanity gate on new months.
  4. Compute engine results for new month(s) ONLY, using the per-month cache
     at data/raw/lfs_pumf/_engine_cache/{YYYY-MM}.json for all prior months.
     This keeps a monthly refresh to seconds rather than 36 minutes.
  5. Assemble the full series (cached + new), apply MA3 smoothing, convert to pct.
  6. Rewrite outputs:
       data/processed/lfs_micro_replication.csv + meta sidecar
       vintage-stamped copy: data/processed/lfs_micro_replication_<YYYY-MM>.csv
       work/research/lfs_micro/lfs_micro_replication.xlsx
       work/research/lfs_micro/lfs_micro_<YYYY-MM>.svg
       work/research/lfs_micro/lfs_micro_<YYYY-MM>.html

If no new PUMF month: prints "latest is still YYYY-MM" and exits 0 without
rewriting any outputs (idempotent).

Engine cache format: data/raw/lfs_pumf/_engine_cache/{YYYY-MM}.json
  {
    "date": "YYYY-MM-01",
    "underlying_lp": float,
    "composition_lp": float,
    "raw_mean_lp": float,
    "total_fitted_lp": float,
    "n_obs_curr": int,
    "n_obs_base": int,
    "r2_curr": float,
    "r2_base": float,
    "<group>_comp_lp": float,   # per GROUP_LABELS
    "spec": { ... },            # serialized Spec
    "computed_at": "ISO timestamp"
  }
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import zipfile
import io
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

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
from pipeline.lfs_micro.engine import _compute_one_yoy, _GROUP_LABELS  # noqa: E402
from pipeline.lfs_micro.spec import DEFAULT_SPEC  # noqa: E402

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("lfs_micro.run")

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

_RAW_PUMF_DIR = _PROJECT_ROOT / "data" / "raw" / "lfs_pumf"
_PROCESSED_DIR = _PROJECT_ROOT / "data" / "processed"
_WORK_DIR = _PROJECT_ROOT / "work" / "research" / "lfs_micro"


# ---------------------------------------------------------------------------
# Engine cache: per-month JSON files
# ---------------------------------------------------------------------------

# Plausibility floors for cached engine results. A monthly LFS employee
# sample is ~37-58k and the wage regression R^2 sits around 0.61; entries
# far below these were computed from truncated/corrupted inputs (observed
# 2026-06: a stale 2025-01 entry with n=325, R^2=0.09 inflated the headline
# by +1.5pp across the Dec-Feb MA3 window). Implausible entries are treated
# as cache misses and recomputed.
_MIN_PLAUSIBLE_N_OBS = 20_000
_MIN_PLAUSIBLE_R2 = 0.40


def _engine_cache_dir() -> Path:
    """Engine cache dir, derived from _RAW_PUMF_DIR at call time.

    Derived (not a module-level constant) so tests that patch _RAW_PUMF_DIR
    get an isolated cache too. A previous module-level binding meant pytest
    runs wrote synthetic engine results into the PRODUCTION cache — the
    source of the stale 2025-01 entry that inflated the Dec-Feb headline.
    """
    return _RAW_PUMF_DIR / "_engine_cache"


def _cache_path(year_month: str) -> Path:
    """Return the cache JSON path for a YYYY-MM key."""
    d = _engine_cache_dir()
    d.mkdir(parents=True, exist_ok=True)
    return d / f"{year_month}.json"


def _parquet_fingerprints(year_month: str) -> dict[str, int]:
    """File-size fingerprints of the parquets behind one y/y result.

    Keyed on the current month and its t-12 base. If either parquet is
    later re-downloaded or repaired, its size changes and the cache entry
    is invalidated. Missing parquet -> size -1 (never matches a real file).
    """
    fps: dict[str, int] = {}
    for key in (year_month, _subtract_12_months(year_month)):
        p = _RAW_PUMF_DIR / f"{key}.parquet"
        fps[key] = p.stat().st_size if p.exists() else -1
    return fps


def _load_cache(year_month: str) -> Optional[dict]:
    """Return cached engine result for year_month, or None if not cached.

    Treated as a miss (recompute) when:
      - the spec changed,
      - the underlying parquets changed since the entry was computed
        (file-size fingerprint mismatch, or no fingerprint recorded),
      - the entry is implausible (tiny sample / degenerate R^2),
        which marks a result computed from corrupted input.
    """
    p = _cache_path(year_month)
    if not p.exists():
        return None
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        # Validate that the cache was computed with the current spec
        cached_spec = data.get("spec", {})
        current_spec = DEFAULT_SPEC.as_dict()
        # Key spec fields that invalidate the cache if changed
        for field in ("weighted", "smoothing", "ob_reference", "min_cell_count"):
            if cached_spec.get(field) != current_spec.get(field):
                logger.debug(
                    "Cache miss for %s: spec.%s changed (%s -> %s)",
                    year_month, field, cached_spec.get(field), current_spec.get(field)
                )
                return None
        # Fail-closed: entries must carry parquet fingerprints that match
        # the files on disk, else the inputs may have changed under them.
        if data.get("parquet_fingerprints") != _parquet_fingerprints(year_month):
            logger.info(
                "Cache miss for %s: parquet fingerprint mismatch (inputs changed).",
                year_month,
            )
            return None
        # Plausibility gate: reject garbage computed from corrupted input.
        if (
            min(data.get("n_obs_curr", 0), data.get("n_obs_base", 0)) < _MIN_PLAUSIBLE_N_OBS
            or min(data.get("r2_curr", 0.0), data.get("r2_base", 0.0)) < _MIN_PLAUSIBLE_R2
        ):
            logger.warning(
                "Cache miss for %s: implausible entry (n_obs=%s/%s, r2=%s/%s) — recomputing.",
                year_month,
                data.get("n_obs_curr"), data.get("n_obs_base"),
                data.get("r2_curr"), data.get("r2_base"),
            )
            return None
        return data
    except Exception as exc:
        logger.warning("Failed to load cache for %s: %s", year_month, exc)
        return None


def _save_cache(year_month: str, row: dict) -> None:
    """Save one engine result row to the per-month cache.

    Refuses to persist implausible rows — a result computed from corrupted
    input must fail loudly at compute time, not poison the series later.
    """
    if (
        min(row.get("n_obs_curr", 0), row.get("n_obs_base", 0)) < _MIN_PLAUSIBLE_N_OBS
        or min(row.get("r2_curr", 0.0), row.get("r2_base", 0.0)) < _MIN_PLAUSIBLE_R2
    ):
        raise RuntimeError(
            f"Implausible engine result for {year_month} "
            f"(n_obs={row.get('n_obs_curr')}/{row.get('n_obs_base')}, "
            f"r2={row.get('r2_curr')}/{row.get('r2_base')}) — refusing to cache. "
            f"Check the parquet inputs for {year_month} and its t-12 base."
        )
    p = _cache_path(year_month)
    data = dict(row)
    data["spec"] = DEFAULT_SPEC.as_dict()
    data["parquet_fingerprints"] = _parquet_fingerprints(year_month)
    data["computed_at"] = datetime.now(timezone.utc).isoformat()
    # Ensure JSON-serializable
    for k, v in data.items():
        if isinstance(v, float) and (np.isnan(v) or np.isinf(v)):
            data[k] = None
    p.write_text(json.dumps(data, indent=2), encoding="utf-8")


def _load_all_cache() -> dict[str, dict]:
    """Load all cached engine results. Returns {YYYY-MM: row_dict}."""
    results: dict[str, dict] = {}
    if not _engine_cache_dir().exists():
        return results
    for f in sorted(_engine_cache_dir().glob("*.json")):
        key = f.stem
        row = _load_cache(key)
        if row is not None:
            results[key] = row
    return results


# ---------------------------------------------------------------------------
# Smoothing + conversion (mirrors engine.py, but on assembled dict of rows)
# ---------------------------------------------------------------------------

def _assemble_series(cache: dict[str, dict]) -> pd.DataFrame:
    """Assemble cached rows into a DataFrame, apply MA3, convert to pct.

    Args:
        cache: {YYYY-MM: row_dict} from _load_all_cache() merged with new rows.

    Returns:
        DataFrame with date, underlying_pct, composition_pct, raw_mean_pct, etc.
        (Same schema as lfs_micro_replication.csv)
    """
    if not cache:
        return pd.DataFrame()

    rows = list(cache.values())
    df = pd.DataFrame(rows).sort_values("date").reset_index(drop=True)

    # Apply centered MA3 to log-point columns
    lp_cols = [c for c in df.columns if c.endswith("_lp")]
    for col in lp_cols:
        df[col] = df[col].rolling(window=3, center=True, min_periods=3).mean()

    # Convert to pct
    for col in lp_cols:
        pct_col = col.replace("_lp", "_pct")
        df[pct_col] = (np.exp(df[col].astype(float)) - 1.0) * 100.0

    return df


# ---------------------------------------------------------------------------
# Incremental engine: compute only missing months
# ---------------------------------------------------------------------------

def _subtract_12_months(key: str) -> str:
    y, m = int(key[:4]), int(key[5:7])
    m -= 12
    if m <= 0:
        m += 12
        y -= 1
    return f"{y:04d}-{m:02d}"


def _compute_new_months(
    new_months: list[str],
    existing_cache: dict[str, dict],
) -> dict[str, dict]:
    """Compute O-B results for months not in existing_cache.

    Loads harmonized frames for each new month and its base (t-12), reusing
    cached frames for the base when available.

    Args:
        new_months:     Sorted list of YYYY-MM keys to compute.
        existing_cache: Already-cached engine results (read-only here).

    Returns:
        Dict {YYYY-MM: row_dict} for newly computed months only.
    """
    new_results: dict[str, dict] = {}

    # We need to load harmonized frames for: new_months + their t-12 bases
    needed_keys: set[str] = set()
    for key in new_months:
        needed_keys.add(key)
        base = _subtract_12_months(key)
        needed_keys.add(base)

    # Load harmonized frames
    frames: dict[str, pd.DataFrame] = {}
    for key in sorted(needed_keys):
        p = _RAW_PUMF_DIR / f"{key}.parquet"
        if not p.exists():
            logger.warning("Parquet not found for %s — skipping.", key)
            continue
        try:
            frames[key] = harmonize(p)
        except Exception as exc:
            logger.error("Harmonize failed for %s: %s", key, exc)

    # Compute each new month
    for key_curr in sorted(new_months):
        key_base = _subtract_12_months(key_curr)
        if key_curr not in frames or key_base not in frames:
            logger.warning(
                "Cannot compute %s: missing frame for %s or %s",
                key_curr, key_curr, key_base
            )
            continue

        logger.info("  Computing O-B for %s (vs %s)...", key_curr, key_base)
        row = _compute_one_yoy(
            key_curr, frames[key_curr], frames[key_base], DEFAULT_SPEC
        )
        if row is None:
            logger.error("O-B failed for %s.", key_curr)
            continue

        _save_cache(key_curr, row)
        new_results[key_curr] = row
        logger.info("    underlying_lp=%.4f n_obs_curr=%d", row["underlying_lp"], row["n_obs_curr"])

    return new_results


# ---------------------------------------------------------------------------
# PUMF acquisition helpers
# ---------------------------------------------------------------------------

def _acquire_month(year: int, month: int, force: bool = False) -> Optional[Path]:
    """Download/cache a PUMF month. Returns parquet path or None on failure."""
    try:
        return get_month(year, month, force=force)
    except Exception as exc:
        logger.error("Failed to acquire PUMF %04d-%02d: %s", year, month, exc)
        return None


def _sanity_check_month(parquet_path: Path) -> bool:
    """Run sanity gate on a parquet. Returns True if OK."""
    try:
        import pyarrow.parquet as pq_io
        df = harmonize(parquet_path)
        total_rows = pq_io.read_metadata(parquet_path).num_rows
        run_sanity_checks(df, parquet_path=parquet_path, total_row_count=total_rows)
        return True
    except SanityError as exc:
        logger.error("Sanity check FAILED for %s: %s", parquet_path.stem, exc)
        return False
    except Exception as exc:
        logger.error("Sanity check error for %s: %s", parquet_path.stem, exc)
        return False


def _inject_zip(zip_path: Path, target_year_month: str) -> Optional[Path]:
    """Extract a manually-provided zip to the PUMF cache (escape hatch).

    Writes the parquet without checking survyear/survmnth so the caller
    can inject unofficial or advance-release data. The meta sidecar records
    the local zip path as source_url.

    Args:
        zip_path:          Local zip file to extract.
        target_year_month: YYYY-MM key to write the parquet as.

    Returns:
        Parquet path on success, None on failure.
    """
    from pipeline.lfs_pumf.download import (
        _extract_monthly_from_zip_bytes,
        _trim_columns,
        _write_meta,
    )
    from datetime import datetime, timezone

    year = int(target_year_month[:4])
    month = int(target_year_month[5:7])
    parquet_path = _RAW_PUMF_DIR / f"{target_year_month}.parquet"

    try:
        zip_bytes = zip_path.read_bytes()
        df = _extract_monthly_from_zip_bytes(zip_bytes, year, month)
        if df is None:
            # Try accepting any single CSV in the zip
            with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
                csvs = [n for n in zf.namelist()
                        if n.lower().endswith(".csv") and not n.lower().startswith("documents")]
                if len(csvs) == 1:
                    with zf.open(csvs[0]) as f:
                        df = pd.read_csv(f, low_memory=False)
                    df.columns = df.columns.str.lower()
                else:
                    raise RuntimeError(f"Cannot identify CSV in {zip_path}: {csvs}")

        df = _trim_columns(df)
        # NOTE: intentionally skip _validate_survyear_survmnth for manual injection
        df.to_parquet(parquet_path, index=False, engine="pyarrow")
        _write_meta(
            parquet_path, year, month,
            source_url=f"local:{zip_path}",
            fetched_at=datetime.now(timezone.utc).isoformat(),
            n_rows=len(df),
        )
        logger.info("Injected %s from %s (%d rows)", target_year_month, zip_path, len(df))
        return parquet_path
    except Exception as exc:
        logger.error("Failed to inject %s from %s: %s", target_year_month, zip_path, exc)
        return None


# ---------------------------------------------------------------------------
# Output writers
# ---------------------------------------------------------------------------

def _write_replication_series(df: pd.DataFrame, latest_month: str) -> tuple[Path, Path]:
    """Write stable + vintage-stamped replication CSVs with meta sidecars."""
    out_cols = [
        "date", "underlying_pct", "composition_pct", "raw_mean_pct",
        "total_fitted_pct", "n_obs_curr", "n_obs_base", "r2_curr", "r2_base",
    ]
    out_cols = [c for c in out_cols if c in df.columns]
    out = df[out_cols].copy()
    out = out.dropna(subset=["underlying_pct"])
    if "date" in out.columns:
        out["date"] = pd.to_datetime(out["date"]).dt.strftime("%Y-%m-%d")

    spec = DEFAULT_SPEC
    notes = (
        f"Oaxaca-Blinder two-fold decomposition of WLS log-wage regression on "
        f"LFS PUMF monthly cross-sections. "
        f"Spec: weighted={spec.weighted}, smoothing={spec.smoothing}, "
        f"ob_reference={spec.ob_reference}. "
        f"Calibrated vs BoC Valet INDINF_LFSMICRO_M. "
        f"Log-points converted to pct via exp()-1. "
        f"Reference: Bounajm/Devakos/Galassi, BoC SAN 2024-23. "
        f"PUMF vintage: {latest_month}."
    )

    meta = SeriesMeta(
        name="lfs_micro_replication",
        source="Statistics Canada LFS PUMF (Sibley Creek O-B replication of BoC SAN 2024-23)",
        source_url="https://www150.statcan.gc.ca/n1/pub/71m0001x/71m0001x2021001-eng.htm",
        source_id=f"LFS PUMF via annual bundles + monthly; PUMF vintage {latest_month}",
        units="% y/y (composition-adjusted underlying wage growth)",
        frequency="monthly",
        notes=notes,
        transform="oaxaca_blinder_lfs_micro",
    )

    # Stable current-vintage
    csv_path, meta_path = write_series(out, meta, _PROCESSED_DIR, date_col="date")
    logger.info("Wrote %s", csv_path)
    logger.info("Wrote %s", meta_path)

    # Vintage-stamped copy
    meta_v = SeriesMeta(
        name=f"lfs_micro_replication_{latest_month}",
        source=meta.source,
        source_url=meta.source_url,
        source_id=meta.source_id,
        units=meta.units,
        frequency=meta.frequency,
        notes=meta.notes,
        transform=meta.transform,
    )
    v_csv, v_meta = write_series(out, meta_v, _PROCESSED_DIR, date_col="date")
    logger.info("Wrote %s", v_csv)
    logger.info("Wrote %s", v_meta)

    return csv_path, meta_path


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run(
    pinned_month: Optional[str] = None,
    force_download: bool = False,
    zip_path: Optional[Path] = None,
) -> int:
    """Main refresh logic. Returns 0 on success, non-zero on failure."""

    # --- Step 1: Discover latest available PUMF month ---
    if pinned_month:
        year = int(pinned_month[:4])
        month = int(pinned_month[5:7])
        latest_year, latest_month_n = year, month
        logger.info("Pinned to %04d-%02d", year, month)
    else:
        logger.info("Probing for latest available PUMF month...")
        try:
            latest_year, latest_month_n = latest_available_month()
        except RuntimeError as exc:
            logger.error("Cannot determine latest PUMF month: %s", exc)
            return 1
        logger.info("Latest PUMF available: %04d-%02d", latest_year, latest_month_n)

    latest_key = f"{latest_year:04d}-{latest_month_n:02d}"

    # --- Step 2: Check what's already cached in the engine cache ---
    existing_cache = _load_all_cache()
    logger.info("Engine cache: %d months already computed.", len(existing_cache))

    # We need all PUMF months from 2015-01 through latest_key for the engine.
    # Determine which engine outputs are missing (those needing new computation).
    # The engine needs a month and its t-12 base; we only compute new ones.

    # Identify the full set of months that should be computed
    # (all months from 2016-01 — the first y/y month — through latest_key)
    def _all_yoy_keys(end_year: int, end_month: int) -> list[str]:
        """All YYYY-MM keys that CAN be computed as y/y (i.e. t-12 exists from 2015+)."""
        keys = []
        for y in range(2016, end_year + 1):
            for m in range(1, 13):
                if y == end_year and m > end_month:
                    break
                keys.append(f"{y:04d}-{m:02d}")
        return keys

    all_expected = _all_yoy_keys(latest_year, latest_month_n)
    missing_engine = [k for k in all_expected if k not in existing_cache]

    if not missing_engine and not force_download:
        logger.info("latest is still %s — no new months to compute.", latest_key)
        print(f"latest is still {latest_key}")
        return 0

    # --- Step 3: Inject zip if provided (escape hatch) ---
    if zip_path:
        logger.info("Injecting %s from %s...", latest_key, zip_path)
        injected = _inject_zip(zip_path, latest_key)
        if injected is None:
            logger.error("Zip injection failed. Aborting.")
            return 1

    # --- Step 4: Acquire any missing PUMF parquets ---
    # For incremental refresh, only acquire months needed for missing engine keys
    # (the new month + its base month)
    months_to_acquire: set[str] = set()
    for key in missing_engine:
        months_to_acquire.add(key)
        months_to_acquire.add(_subtract_12_months(key))

    new_parquets: set[str] = set()
    for key in sorted(months_to_acquire):
        p = _RAW_PUMF_DIR / f"{key}.parquet"
        if not p.exists() or force_download:
            y, m = int(key[:4]), int(key[5:7])
            logger.info("Acquiring PUMF %s...", key)
            path = _acquire_month(y, m, force=force_download)
            if path is None:
                logger.warning("Could not acquire %s — skipping.", key)
                continue
            new_parquets.add(key)
        else:
            pass  # already have the parquet

    # --- Step 5: Sanity gate on newly acquired parquets ---
    for key in sorted(new_parquets):
        p = _RAW_PUMF_DIR / f"{key}.parquet"
        if p.exists():
            ok = _sanity_check_month(p)
            if not ok:
                logger.error(
                    "Sanity check failed for %s. Aborting to protect output integrity.",
                    key
                )
                return 1

    # --- Step 6: Compute engine for missing months ---
    if missing_engine:
        logger.info("Computing engine for %d missing month(s)...", len(missing_engine))
        new_results = _compute_new_months(missing_engine, existing_cache)
        logger.info("Computed %d new months.", len(new_results))
        existing_cache.update(new_results)
    else:
        logger.info("All engine months already cached; skipping computation.")

    if not existing_cache:
        logger.error("No engine results available. Cannot write outputs.")
        return 1

    # --- Step 7: Assemble full series with MA3 + pct conversion ---
    logger.info("Assembling %d-month series with MA3 smoothing...", len(existing_cache))
    df = _assemble_series(existing_cache)

    if df.empty or "underlying_pct" not in df.columns:
        logger.error("Assembly produced an empty or invalid DataFrame.")
        return 1

    # --- Step 8: Write outputs ---
    logger.info("Writing replication series...")
    _write_replication_series(df, latest_key)

    logger.info("Building workbook...")
    try:
        from pipeline.lfs_micro.output_sheet import write_output_sheet
        xlsx_path = _WORK_DIR / "lfs_micro_replication.xlsx"
        out = write_output_sheet(xlsx_path)
        if out.used_companion:
            logger.info(
                "Workbook locked by Excel — wrote companion file %s", out.path
            )
        else:
            logger.info("Wrote workbook %s", out.path)
    except Exception as exc:
        logger.error("Workbook write failed: %s", exc)
        # Non-fatal: series CSV is the primary output

    logger.info("Rendering chart...")
    try:
        from pipeline.lfs_micro.chart import render_chart
        svg, html = render_chart()
        logger.info("Wrote %s", svg)
        logger.info("Wrote %s", html)
    except Exception as exc:
        logger.error("Chart render failed: %s", exc)

    # --- Step 9: Print headline summary ---
    _print_summary(df, latest_key)

    return 0


def _print_summary(df: pd.DataFrame, latest_key: str) -> None:
    """Print a brief summary to stdout."""
    from pipeline.fetch.boc import fetch_series
    print()
    print(f"=== LFS-micro refresh: {latest_key} ===")

    df_sorted = df.sort_values("date")
    last = df_sorted[df_sorted["underlying_pct"].notna()].iloc[-1]

    print(f"Latest month in replication: {last['date'][:7]}")
    print(f"  Underlying wage growth (ours):    {last['underlying_pct']:.3f}% y/y")
    if "composition_pct" in last:
        print(f"  Composition effect:               {last['composition_pct']:.3f}% y/y")
    if "raw_mean_pct" in last:
        print(f"  Raw mean wage growth:             {last['raw_mean_pct']:.3f}% y/y")
    if "n_obs_curr" in last and pd.notna(last.get("n_obs_curr")):
        print(f"  Sample size (current month):      {int(last['n_obs_curr']):,}")

    # Compare to BoC if available
    try:
        boc = pd.read_csv(
            _PROJECT_ROOT / "data" / "raw" / "lfs_micro.csv",
            parse_dates=["date"]
        )
        boc_latest_date = boc["date"].max()
        boc_latest_val = float(boc.loc[boc["date"] == boc_latest_date, "value"].iloc[0])
        print(f"  BoC INDINF_LFSMICRO_M ({boc_latest_date.strftime('%Y-%m')}): {boc_latest_val:.1f}% y/y")
        last_date = pd.Timestamp(last["date"][:10])
        if last_date in boc.set_index("date").index:
            diff = last["underlying_pct"] - boc_latest_val
            print(f"  Difference (ours minus BoC):      {diff:+.3f} pp")
    except Exception:
        pass

    print()
    print("Outputs:")
    print(f"  {_PROCESSED_DIR / 'lfs_micro_replication.csv'}")
    print(f"  {_WORK_DIR / 'lfs_micro_replication.xlsx'}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="LFS-micro replication refresh"
    )
    parser.add_argument(
        "--month", default=None, metavar="YYYY-MM",
        help="Pin to a specific PUMF month (default: auto-discover latest)",
    )
    parser.add_argument(
        "--force-download", action="store_true",
        help="Re-download PUMF zips even if cached",
    )
    parser.add_argument(
        "--zip", default=None, metavar="PATH",
        help="Inject a local PUMF zip for the latest month (escape hatch)",
    )
    args = parser.parse_args(argv)

    zip_path = Path(args.zip) if args.zip else None
    return run(
        pinned_month=args.month,
        force_download=args.force_download,
        zip_path=zip_path,
    )


if __name__ == "__main__":
    raise SystemExit(main())
