"""LFS-micro engine: iterate months, assemble the replication series.

Orchestrates the full pipeline for a range of months:

  For each month t with available data for both t and t-12:
    1. Load harmonized DataFrames for t and t-12.
    2. Compute the union category universe (conformable design matrices).
    3. Run WLS regression on both months.
    4. Run the Oaxaca-Blinder decomposition.
    5. Convert log-points to geometric percent (exp()-1) for the headline.
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

Note on log-points vs percent (UNITS — read before comparing to the BoC):
  The BoC publishes INDINF_LFSMICRO_M in LOG POINTS (100*dlog), not
  geometric percent. Established by residual forensics 2026-06-09:
  comparing in matching units removes a systematic, level-dependent
  ~+0.05pp convexity bias and improves the fit from RMSE 0.1178pp to
  0.0885pp (bias +0.088 -> +0.037pp).

  Our reader-facing headline stays in geometric percent — the honest
  "percent" a reader expects:
    underlying_pct = (exp(underlying_lp) - 1.0) * 100

  Every comparison against the BoC series must be same-units:
    - lp-vs-lp: ours underlying_lp*100 vs BoC as published
      (the CANONICAL fidelity metric; see calibrate.py), or
    - geo-vs-geo: BoC converted (exp(lp/100)-1)*100 vs our headline
      (run.py summary, workbook, chart).

  Calibration in calibrate.py scores both conventions against the BoC
  series; the lp-vs-lp numbers are canonical.

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
from .regression import (
    RegressionResult,
    _build_design_matrix,
    _prepare_categoricals,
    detect_deficient_columns,
    run_wls,
    union_category_universe,
)
from .spec import Spec, DEFAULT_SPEC

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# METHODOLOGY_VERSION — engine-cache code-version key.
#
# The per-month engine cache (run.py; data/raw/lfs_pumf/_engine_cache/) keys
# on the raw-parquet SHA-256 fingerprints, the Spec fields, the regressor
# set, AND this constant. The fingerprints catch DATA changes; this constant
# is the ONLY thing that catches CODE changes.
#
# >>> BUMP THIS (+1) ON ANY CHANGE TO NUMBERS-PRODUCING LOGIC IN:          <<<
# >>>   pipeline/lfs_pumf/harmonize.py   (recodes, filters, tenure bins)   <<<
# >>>   pipeline/lfs_micro/regression.py (design matrix, WLS, pruning)     <<<
# >>>   pipeline/lfs_micro/decompose.py  (O-B formulas)                    <<<
# >>>   pipeline/lfs_micro/engine.py     (_compute_one_yoy and helpers)    <<<
#
# Forgetting to bump leaves old months cached under the old methodology while
# new months compute under the new one — a silently mixed series (the exact
# failure mode flagged MAJOR-1 in the 2026-06-09 code-correctness audit).
#
# This is deliberately a manual constant, NOT a hash of the source files:
# hashing would nuke the full cache (a ~36-minute recompute) on every comment
# or docstring edit. A bump invalidates every cached month; the recompute
# flows through the normal plausibility gates in run.py (_load_cache /
# _save_cache refuse implausible entries).
#
# History:
#   1  2026-06-09  introduced (audit fix). Methodology unchanged since the
#                  2026-06-05 full rebuild; the one-time recompute under this
#                  key was verified value-identical to the prior series.
METHODOLOGY_VERSION = 1

# The regressors that get per-group composition columns in the output.
# Order matches REGRESSOR_GROUPS in regression.py (must stay in sync).
_GROUP_LABELS = [
    "occupation", "education", "tenure", "age", "gender", "union",
    "fullparttime", "province", "jobpermanency", "maritalstatus",
    "immigration", "industry", "sector", "estsize", "multijob",
    "firmsize",  # Phase B: firm size (BoC SAN 2024-23 covariate)
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

def _apply_common_column_pruning(
    result_curr: RegressionResult,
    result_base: RegressionResult,
    df_curr: pd.DataFrame,
    df_base: pd.DataFrame,
    spec: Spec,
    cat_union: dict,
) -> tuple[RegressionResult, RegressionResult]:
    """Enforce identical column sets for the two regressions (conformability fix).

    Strategy:
      1. Build the sqrt-weight-scaled design matrices for both months using
         the union category universe.
      2. Detect rank-deficient columns independently for each month.
      3. Take the UNION of dropped column names.
      4. Translate dropped column names back to category exclusions in a
         pruned cat_universe.
      5. Re-estimate BOTH months on the pruned universe.
      6. Belt-and-braces: raise if col_names still mismatch.

    This guarantees identical col_names in the two RegressionResults so
    oaxaca_blinder never sees a shape mismatch, regardless of whether
    rank deficiency appears in one month but not the other.

    When neither month has rank deficiency, returns the inputs unchanged
    (no extra work).
    """
    def _build_scaled_X_from_df(df: pd.DataFrame) -> tuple[np.ndarray, list[str]]:
        """Filter df to cat_union, build design, apply sqrt-weight scaling."""
        df_clean, _, _ = _prepare_categoricals(
            df.copy(),
            min_cell_count=spec.min_cell_count,
            category_universe=cat_union,
        )
        X_df = _build_design_matrix(df_clean, cat_union)
        if spec.weighted:
            w = df_clean["weight"].values.astype(float)
        else:
            w = np.ones(len(df_clean))
        sqrt_w = np.sqrt(w)
        return X_df.values * sqrt_w[:, np.newaxis], list(X_df.columns)

    Xs_curr, cols_curr = _build_scaled_X_from_df(df_curr)
    Xs_base, cols_base = _build_scaled_X_from_df(df_base)

    dropped_curr = set(detect_deficient_columns(Xs_curr, cols_curr))
    dropped_base = set(detect_deficient_columns(Xs_base, cols_base))
    dropped_union = dropped_curr | dropped_base

    if not dropped_union:
        # No rank deficiency in either month; col_names must already match.
        # Belt-and-braces: raise if they don't (should never happen after union pass).
        if result_curr.col_names != result_base.col_names:
            raise ValueError(
                f"Design matrix column mismatch with no detected rank deficiency: "
                f"{len(result_curr.col_names)} vs {len(result_base.col_names)} cols. "
                f"The union_category_universe pass should have aligned these."
            )
        return result_curr, result_base

    # Translate dummy column names back to (regressor_col, category_value) pairs
    # and build a pruned cat_universe that excludes those categories.
    # Column name format: "<reg_col>_<cat_str>", e.g. "noc_43_5".
    pruned_universe = {col: list(cats) for col, cats in cat_union.items()}
    for col_name in dropped_union:
        for reg_col in pruned_universe:
            prefix = f"{reg_col}_"
            if col_name.startswith(prefix):
                cat_val_str = col_name[len(prefix):]
                pruned_universe[reg_col] = [
                    c for c in pruned_universe[reg_col]
                    if str(c) != cat_val_str
                ]
                break

    logger.info(
        "Common-column pruning: dropping %d deficient column(s) from both months: %s",
        len(dropped_union),
        sorted(dropped_union),
    )

    # Re-estimate both months on the pruned universe
    result_curr_pruned = run_wls(
        df_curr,
        spec_weighted=spec.weighted,
        min_cell_count=spec.min_cell_count,
        category_universe=pruned_universe,
    )
    result_base_pruned = run_wls(
        df_base,
        spec_weighted=spec.weighted,
        min_cell_count=spec.min_cell_count,
        category_universe=pruned_universe,
    )

    # Belt-and-braces: col_names must now match
    if result_curr_pruned.col_names != result_base_pruned.col_names:
        raise ValueError(
            f"Common-column pruning failed to align design matrices: "
            f"{len(result_curr_pruned.col_names)} vs {len(result_base_pruned.col_names)} cols "
            f"after dropping {sorted(dropped_union)}."
        )

    return result_curr_pruned, result_base_pruned


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

        # Deterministic common-column pruning: detect rank-deficient columns
        # across BOTH months and re-estimate on the surviving common set.
        # This is the authoritative conformability fix — the union-category pass
        # above aligns categories but cannot guarantee both design matrices will
        # be full-rank. A column deficient in month A but not B would cause the
        # two col_names lists to diverge inside run_wls._fix_rank_deficiency,
        # yielding a shape mismatch in oaxaca_blinder.
        result_curr, result_base = _apply_common_column_pruning(
            result_curr, result_base, df_curr, df_base, spec, cat_union
        )

        # Belt-and-braces: oaxaca_blinder raises if col_names still mismatch.
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
    """Convert log-point columns to geometric y/y percent change.

    Formula: pct = (exp(lp) - 1.0) * 100

    NOTE: the BoC publishes INDINF_LFSMICRO_M in log points (100*dlog) and
    does NOT apply this conversion — never compare these pct columns to the
    BoC series directly (see the module docstring units note).

    NaN values (edge of MA window) propagate as NaN in the pct columns.
    """
    lp_cols = [c for c in df.columns if c.endswith("_lp")]
    for col in lp_cols:
        pct_col = col.replace("_lp", "_pct")
        df[pct_col] = (np.exp(df[col]) - 1.0) * 100.0

    # Also provide the main headline column as 'underlying_pct' (alias for clarity)
    # Already created above; no duplication needed.
    return df
