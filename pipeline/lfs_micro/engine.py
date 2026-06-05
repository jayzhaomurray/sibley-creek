"""LFS-micro engine: iterate months, assemble the replication series.

Orchestrates the full pipeline for a range of months:

  For each month t with available data for both t and t-12:
    1. Load harmonized DataFrames for t and t-12.
    2. Compute the union category universe (conformable design matrices).
    3. Run WLS regression on both months.
    4. Run the Oaxaca-Blinder decomposition.
    5. Convert log-points to percent (exp()-1) for BoC series comparability.
    6. Accumulate results.

Output DataFrame columns (one row per month):
  date              ISO date string (first of month, reference period)
  underlying_pct    Underlying wage growth (log-pt -> pct, exp()-1)
  composition_pct   Composition effect (log-pt -> pct, exp()-1)
  raw_mean_pct      Raw mean log-wage change (log-pt -> pct)
  total_fitted_pct  Fitted total O-B change (log-pt -> pct)
  underlying_lp     Underlying in log-points (pre-conversion)
  composition_lp    Composition in log-points (pre-conversion)
  n_obs_curr        Observations in current month regression
  n_obs_base        Observations in base month (t-12) regression
  r2_curr           R^2 of current month WLS
  r2_base           R^2 of base month WLS
  <group>_comp_lp   Per-group contribution to composition (log-points),
                    one column per regressor group in REGRESSOR_GROUPS

Note on log-points vs percent:
  The BoC's INDINF_LFSMICRO_M series is published as y/y percent change.
  Our decomposition yields log-points (natural log). For small changes the
  difference is negligible (<0.1pp for values near 3-4%), but we convert
  consistently for comparability:
    underlying_pct = (exp(underlying_lp) - 1.0) * 100
  The sign convention matches: positive = wage growth.

  Calibration in calibrate.py compares against the BoC series to verify
  the scale is correct and determine whether smoothing improves the fit.

Smoothing (ma3):
  If spec.smoothing == "ma3", a 3-month centred moving average is applied
  to the underlying_lp and composition_lp series BEFORE converting to pct.
  This matches common practice in composition-adjustment literature and is
  one of the calibration parameters.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

from .decompose import oaxaca_blinder
from .regression import RegressionResult, run_wls, union_category_universe
from .spec import Spec, DEFAULT_SPEC

logger = logging.getLogger(__name__)

# The regressors that get per-group composition columns in the output
_GROUP_LABELS = [
    "occupation", "education", "tenure", "age", "gender", "union",
    "fullparttime", "province", "jobpermanency", "maritalstatus",
    "immigration", "industry", "sector", "estsize", "multijob",
]


def run_engine(
    harmonized_frames: dict[str, pd.DataFrame],
    spec: Spec = DEFAULT_SPEC,
) -> pd.DataFrame:
    """Run the O-B engine over a set of harmonized monthly DataFrames.

    Args:
        harmonized_frames: Dict {YYYY-MM: harmonized_df} where each value
                           is the output of harmonize.harmonize() for that
                           month. Must contain at least 13 months of data
                           to produce any y/y observations.
        spec:              Frozen Spec controlling the engine parameters.

    Returns:
        DataFrame with one row per computed y/y month (see column docs above).
        Months where either t or t-12 data is missing are skipped.
    """
    sorted_keys = sorted(harmonized_frames.keys())
    rows = []

    for key_curr in sorted_keys:
        key_base = _subtract_12_months(key_curr)
        if key_base not in harmonized_frames:
            logger.debug("Skipping %s: no data for base month %s.", key_curr, key_base)
            continue

        df_curr = harmonized_frames[key_curr]
        df_base = harmonized_frames[key_base]

        row = _compute_one_yoy(key_curr, df_curr, df_base, spec)
        if row is not None:
            rows.append(row)

    if not rows:
        return pd.DataFrame()

    result = pd.DataFrame(rows)
    result = result.sort_values("date").reset_index(drop=True)

    # Apply smoothing to the log-point series if requested
    if spec.smoothing == "ma3":
        result = _apply_ma3(result)

    # Convert log-points to percent after smoothing
    result = _convert_lp_to_pct(result)

    return result


def run_engine_from_paths(
    parquet_paths: dict[str, Path],
    spec: Spec = DEFAULT_SPEC,
    harmonize_fn=None,
) -> pd.DataFrame:
    """Convenience wrapper: load harmonized frames from parquet paths and run.

    Args:
        parquet_paths:  Dict {YYYY-MM: Path} pointing to .parquet files.
        spec:           Frozen Spec.
        harmonize_fn:   Callable(Path) -> pd.DataFrame. If None, uses
                        pipeline.lfs_pumf.harmonize.harmonize.

    Returns:
        Same as run_engine().
    """
    if harmonize_fn is None:
        from pipeline.lfs_pumf.harmonize import harmonize
        harmonize_fn = harmonize

    frames: dict[str, pd.DataFrame] = {}
    for key, path in parquet_paths.items():
        try:
            frames[key] = harmonize_fn(path)
        except Exception as exc:
            logger.error("Failed to harmonize %s: %s", key, exc)
            raise

    return run_engine(frames, spec=spec)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _compute_one_yoy(
    key_curr: str,
    df_curr: pd.DataFrame,
    df_base: pd.DataFrame,
    spec: Spec,
) -> Optional[dict]:
    """Compute the O-B decomposition for one y/y pair.

    Returns a dict (one row for the result DataFrame), or None on failure.
    """
    try:
        # First pass: estimate each month independently to get category universes
        result_curr_init = run_wls(
            df_curr,
            spec_weighted=spec.weighted,
            min_cell_count=spec.min_cell_count,
        )
        result_base_init = run_wls(
            df_base,
            spec_weighted=spec.weighted,
            min_cell_count=spec.min_cell_count,
        )

        # Build the union category universe for conformability
        cat_union = union_category_universe(result_curr_init, result_base_init)

        # Second pass: re-estimate both months on the same union universe
        result_curr = run_wls(
            df_curr,
            spec_weighted=spec.weighted,
            min_cell_count=spec.min_cell_count,
            category_universe=cat_union,
        )
        result_base = run_wls(
            df_base,
            spec_weighted=spec.weighted,
            min_cell_count=spec.min_cell_count,
            category_universe=cat_union,
        )

        # Oaxaca-Blinder decomposition
        ob = oaxaca_blinder(result_base, result_curr, ob_reference=spec.ob_reference)

    except Exception as exc:
        logger.error("O-B decomposition failed for %s: %s", key_curr, exc)
        return None

    row: dict = {
        "date": f"{key_curr}-01",
        # Log-point columns (smoothed and converted downstream)
        "underlying_lp": ob.underlying,
        "composition_lp": ob.composition,
        "raw_mean_lp": ob.raw_mean_change,
        "total_fitted_lp": ob.total_fitted,
        # Diagnostics
        "n_obs_curr": result_curr.n_obs,
        "n_obs_base": result_base.n_obs,
        "r2_curr": round(result_curr.r_squared, 4),
        "r2_base": round(result_base.r_squared, 4),
    }

    # Per-group composition contributions (log-points)
    for grp in _GROUP_LABELS:
        row[f"{grp}_comp_lp"] = ob.group_contributions.get(grp, 0.0)

    return row


def _subtract_12_months(key: str) -> str:
    """Return the YYYY-MM key 12 months before the given key."""
    year, month = int(key[:4]), int(key[5:7])
    month -= 12
    if month <= 0:
        month += 12
        year -= 1
    return f"{year:04d}-{month:02d}"


def _apply_ma3(df: pd.DataFrame) -> pd.DataFrame:
    """Apply a 3-month centred moving average to log-point columns.

    The MA is applied to the series as a time sequence. 'Centred' means
    the window includes [t-1, t, t+1]; edge observations become NaN.
    """
    lp_cols = [c for c in df.columns if c.endswith("_lp")]
    for col in lp_cols:
        df[col] = df[col].rolling(window=3, center=True, min_periods=3).mean()
    return df


def _convert_lp_to_pct(df: pd.DataFrame) -> pd.DataFrame:
    """Convert log-point columns to y/y percent change.

    Formula: pct = (exp(lp) - 1.0) * 100
    Multiplied by 100 so the scale matches the BoC Valet series
    (published as percent, not fraction).

    NaN values (edge of MA window) propagate as NaN in the pct columns.
    """
    lp_cols = [c for c in df.columns if c.endswith("_lp")]
    for col in lp_cols:
        pct_col = col.replace("_lp", "_pct")
        df[pct_col] = (np.exp(df[col]) - 1.0) * 100.0

    # Also provide the main headline column as 'underlying_pct' (alias for clarity)
    # Already created above; no duplication needed.
    return df
