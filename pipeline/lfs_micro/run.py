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
    "spec": { ... },            # serialized Spec + regressor_set
    "methodology_version": int, # engine.METHODOLOGY_VERSION at compute time
    "parquet_fingerprints": { "YYYY-MM": sha256, ... },
    "computed_at": "ISO timestamp"
  }
"""

from __future__ import annotations

import argparse
import hashlib
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
import pipeline.lfs_micro.engine as _engine_mod  # noqa: E402
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


def _sha256_file(path: Path) -> str:
    """Return the SHA-256 hex digest of a file, or '' if it does not exist."""
    if not path.exists():
        return ""
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _parquet_fingerprints(year_month: str) -> dict[str, str]:
    """SHA-256 content hashes of the parquets behind one y/y result.

    Keyed on the current month and its t-12 base. Content hashing catches
    re-downloads that produce same-size but different-content files (e.g. a
    corrected PUMF release from StatCan). Missing parquet -> '' (never matches
    a real file).

    NOTE: backward-incompatible with the old file-size fingerprints — existing
    cache entries will all miss once on the first run after this change, then
    be recomputed and stored with SHA-256 fingerprints.
    """
    fps: dict[str, str] = {}
    for key in (year_month, _subtract_12_months(year_month)):
        p = _RAW_PUMF_DIR / f"{key}.parquet"
        fps[key] = _sha256_file(p)
    return fps


def _load_cache(year_month: str) -> Optional[dict]:
    """Return cached engine result for year_month, or None if not cached.

    Treated as a miss (recompute) when:
      - the spec changed (weighted / ob_reference / min_cell_count),
      - the regressor set changed,
      - engine.METHODOLOGY_VERSION changed (a code edit to harmonize /
        regression / decompose / engine logic — see the bump instructions
        on the constant in pipeline/lfs_micro/engine.py),
      - the underlying parquets changed since the entry was computed
        (SHA-256 content-fingerprint mismatch, or no fingerprint recorded),
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
        # Key spec fields that invalidate the cache if changed.
        # NOTE: "smoothing" is deliberately NOT compared — cached entries hold
        # pre-smoothing single-month lp values; smoothing is applied at
        # assembly time, so a smoothing change does not invalidate them.
        for field in ("weighted", "ob_reference", "min_cell_count"):
            if cached_spec.get(field) != current_spec.get(field):
                logger.debug(
                    "Cache miss for %s: spec.%s changed (%s -> %s)",
                    year_month, field, cached_spec.get(field), current_spec.get(field)
                )
                return None
        # Regressor-set invalidation: adding/removing a regressor changes the
        # design matrix; the spec fields above do not capture this.
        from pipeline.lfs_micro.regression import REGRESSOR_GROUPS as _REGS
        current_reg_set = sorted(col for col, _grp in _REGS)
        cached_reg_set = cached_spec.get("regressor_set", None)
        if cached_reg_set != current_reg_set:
            logger.info(
                "Cache miss for %s: regressor_set changed (%s -> %s)",
                year_month, cached_reg_set, current_reg_set,
            )
            return None
        # Methodology code-version invalidation: parquet fingerprints catch
        # DATA changes; this catches CODE changes (harmonize / regression /
        # decompose / engine edits). Entries without a recorded version
        # (pre-2026-06-09) never match.
        if data.get("methodology_version") != _engine_mod.METHODOLOGY_VERSION:
            logger.info(
                "Cache miss for %s: methodology_version %s != current %s "
                "(engine/harmonize/regression/decompose code changed) — recomputing.",
                year_month,
                data.get("methodology_version"),
                _engine_mod.METHODOLOGY_VERSION,
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
    spec_dict = DEFAULT_SPEC.as_dict()
    # Embed regressor set so design-matrix changes invalidate the cache.
    from pipeline.lfs_micro.regression import REGRESSOR_GROUPS as _REGS
    spec_dict["regressor_set"] = sorted(col for col, _grp in _REGS)
    data["spec"] = spec_dict
    # Code-version key: see METHODOLOGY_VERSION in engine.py (bump on any
    # harmonize/regression/decompose/engine logic change).
    data["methodology_version"] = _engine_mod.METHODOLOGY_VERSION
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

    Fail-closed: after sorting, the date index is reindexed to the complete
    monthly calendar between the first and last computed month. Any gap (a month
    with no cached result) raises RuntimeError before MA3 is applied, because
    rolling() on a gapped series would silently treat non-adjacent months as
    adjacent and produce wrong smoothed values.

    Args:
        cache: {YYYY-MM: row_dict} from _load_all_cache() merged with new rows.

    Returns:
        DataFrame with date, underlying_pct, composition_pct, raw_mean_pct, etc.
        (Same schema as lfs_micro_replication.csv). Also includes unsmoothed
        _raw_pct columns (pre-MA3 single-month values) and interaction_lp.
    """
    if not cache:
        return pd.DataFrame()

    rows = list(cache.values())
    df = pd.DataFrame(rows).sort_values("date").reset_index(drop=True)

    # Preserve pre-MA3 single-month log-point values as _raw columns.
    lp_cols = [c for c in df.columns if c.endswith("_lp")]
    for col in lp_cols:
        raw_col = col.replace("_lp", "_raw_lp")
        df[raw_col] = df[col].copy()

    # Compute interaction term (O-B two-fold: total_fitted - underlying - composition)
    if all(c in df.columns for c in ("total_fitted_lp", "underlying_lp", "composition_lp")):
        df["interaction_lp"] = df["total_fitted_lp"] - df["underlying_lp"] - df["composition_lp"]

    # Fail-closed: reindex to complete monthly calendar and check for gaps.
    # Rolling MA3 on a non-contiguous series treats non-adjacent months as adjacent;
    # a gap in the middle would silently produce a wrong smoothed value.
    first_date = pd.Timestamp(df["date"].iloc[0][:10])
    last_date = pd.Timestamp(df["date"].iloc[-1][:10])
    expected_months = pd.date_range(first_date, last_date, freq="MS")
    actual_dates = pd.to_datetime(df["date"].str[:10])
    missing_months = sorted(set(expected_months) - set(actual_dates))
    if missing_months:
        missing_str = ", ".join(d.strftime("%Y-%m") for d in missing_months)
        raise RuntimeError(
            f"Calendar gap detected in assembled series: {missing_str}.\n"
            f"These months are missing from the engine cache. Run with "
            f"--force-download to recompute, or check the engine cache at "
            f"{_engine_cache_dir()} for corrupt/missing entries."
        )

    # Apply smoothing per the spec. With smoothing="raw" (the recalibrated
    # default — the BoC series is unsmoothed; see spec.py) the headline
    # columns equal the single-month values and the newest month carries a
    # headline reading directly.
    if DEFAULT_SPEC.smoothing == "ma3":
        for col in lp_cols:
            df[col] = df[col].rolling(window=3, center=True, min_periods=3).mean()
        if "interaction_lp" in df.columns:
            df["interaction_lp"] = df["interaction_lp"].rolling(window=3, center=True, min_periods=3).mean()

    # Convert to pct: smoothed headline columns
    for col in lp_cols:
        pct_col = col.replace("_lp", "_pct")
        df[pct_col] = (np.exp(df[col].astype(float)) - 1.0) * 100.0

    # Convert to pct: unsmoothed raw columns
    raw_lp_cols = [c for c in df.columns if c.endswith("_raw_lp")]
    for col in raw_lp_cols:
        pct_col = col.replace("_raw_lp", "_raw_pct")
        df[pct_col] = (np.exp(df[col].astype(float)) - 1.0) * 100.0

    # Convert interaction term to pct
    if "interaction_lp" in df.columns:
        df["interaction_pct"] = (np.exp(df["interaction_lp"].astype(float)) - 1.0) * 100.0

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
            raise RuntimeError(
                f"O-B decomposition returned None for {key_curr} (vs {key_base}). "
                f"This is a data integrity or regressor failure — aborting to prevent "
                f"a calendar gap in the assembled series. "
                f"Check parquets for {key_curr} and {key_base}."
            )

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
    """Write stable + vintage-stamped replication CSVs with meta sidecars.

    CSV column conventions:
      Smoothed headline columns (centered MA3):
        underlying_pct, composition_pct, raw_mean_pct, total_fitted_pct
      Unsmoothed single-month columns (pre-MA3, same calendar month):
        underlying_raw_pct, composition_raw_pct, raw_mean_raw_pct, total_fitted_raw_pct
      Interaction term (O-B two-fold residual = total_fitted - underlying - composition):
        interaction_lp, interaction_pct
      Diagnostic columns:
        n_obs_curr, n_obs_base, r2_curr, r2_base

    MA3 timing convention:
      Headline smoothed columns use a centered 3-month window: the value for
      month T is the average of (T-1, T, T+1). This means the last available
      month in the series (newest PUMF) and the first month are always NaN in
      the smoothed series. The most recent non-NaN headline observation
      corresponds to newest_PUMF_month - 1.

    Labelling note:
      'raw_mean_pct' / 'raw_mean_raw_pct' is the weighted mean log-wage growth
      (geometric mean ratio), NOT the LFS headline arithmetic average hourly
      wage growth. The column name is kept for CSV consumer compatibility.
      Human-facing labels (workbook, chart) read "mean log-wage growth
      (geometric)".
    """
    out_cols = [
        "date",
        # Smoothed (MA3) headline columns
        "underlying_pct", "composition_pct", "raw_mean_pct", "total_fitted_pct",
        # Unsmoothed single-month columns (pre-MA3)
        "underlying_raw_pct", "composition_raw_pct", "raw_mean_raw_pct",
        # Interaction term (O-B two-fold)
        "interaction_lp", "interaction_pct",
        # Diagnostics
        "n_obs_curr", "n_obs_base", "r2_curr", "r2_base",
    ]
    out_cols = [c for c in out_cols if c in df.columns]
    out = df[out_cols].copy()
    # Keep rows that have EITHER a smoothed or a raw estimate. The newest
    # month always has NaN smoothed (centered MA3 needs t+1) but a valid
    # single-month raw estimate — that raw value IS the release-morning
    # signal and must not be dropped from the CSV.
    keep_subset = [c for c in ("underlying_pct", "underlying_raw_pct") if c in out.columns]
    out = out.dropna(subset=keep_subset, how="all")
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
        + (
            "Headline columns are unsmoothed single-month estimates (the BoC "
            "series is unsmoothed: matching roughness, no MA signature); "
            "_raw_pct columns duplicate them under this spec. "
            if spec.smoothing == "raw" else
            "Smoothed columns use centered MA3; unsmoothed (_raw_pct) are "
            "pre-MA3 single-month point estimates. MA3 timing: headline month "
            "= newest PUMF month minus 1 (centered window requires T+1 which "
            "is not yet available). "
        )
        +
        f"interaction_lp/pct: O-B two-fold residual (total_fitted - underlying - composition). "
        f"raw_mean_pct is weighted mean log-wage growth (geometric mean ratio), "
        f"not the LFS headline arithmetic average wage growth. "
        f"Scope: 2016+ replication (release-morning PUMF tool; not a full-history "
        f"replication of the published paper). "
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
    rebuild_outputs: bool = False,
) -> int:
    """Main refresh logic. Returns 0 on success, non-zero on failure.

    rebuild_outputs: skip the no-new-months early exit and rewrite the CSV,
    workbook, and chart from the existing engine cache (use after a change
    to output formatting code; computes nothing new).
    """

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

    if not missing_engine and not force_download and not rebuild_outputs:
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

    # --- Step 7: Assemble full series (spec smoothing) + pct conversion ---
    logger.info(
        "Assembling %d-month series (smoothing=%s)...",
        len(existing_cache), DEFAULT_SPEC.smoothing,
    )
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
        print(f"  Mean log-wage growth (geometric): {last['raw_mean_pct']:.3f}% y/y")
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
    parser.add_argument(
        "--rebuild", action="store_true",
        help="Rewrite CSV/workbook/chart from the engine cache even if no "
             "new PUMF month (use after output-code changes)",
    )
    args = parser.parse_args(argv)

    zip_path = Path(args.zip) if args.zip else None
    return run(
        pinned_month=args.month,
        force_download=args.force_download,
        zip_path=zip_path,
        rebuild_outputs=args.rebuild,
    )


if __name__ == "__main__":
    raise SystemExit(main())
