"""Weighted log-wage regression for one LFS PUMF month.

Implements the log-wage Mincer-style regression described in BoC SAN 2024-23:

    log(wage_i) = X_i' * B + epsilon_i

where X_i is a vector of categorical dummies (occupation, education, tenure
bracket, age, gender, union status, full/part-time, province, job permanency,
marital status, immigration status, industry, public/private sector,
establishment size) and epsilon_i is a residual.

Estimation by Weighted Least Squares (WLS) using numpy.linalg.lstsq on
sqrt-weight-scaled rows:

    sqrt(w_i) * log(wage_i) = sqrt(w_i) * X_i' * B + sqrt(w_i) * epsilon_i

This is standard WLS: pre-multiplying by sqrt(w) converts WLS to OLS on
the scaled system, which lstsq solves exactly.

Design matrix conventions:
  - All categorical regressors are one-hot encoded via pd.get_dummies with
    drop_first=False (no baseline dropped here — we drop the first category
    after ensuring stable column ordering to avoid rank deficiency from
    the intercept).
  - Column ordering is stable across calls with the same category universe.
    When comparing two months (t vs t-12), the caller passes the union of
    both months' categories so B_t and B_{t-12} are conformable vectors.
  - An explicit intercept column (all-ones) is prepended.
  - Empty cells (categories with fewer than min_cell_count observations) are
    dropped before encoding to avoid near-singular matrices; each drop is logged.
  - After encoding, the first dummy of each regressor group is dropped to
    avoid the dummy variable trap (full rank design).
  - A rank check is performed; if the design is still rank-deficient, the
    problematic columns are dropped iteratively (rare in practice).

Output: RegressionResult containing the coefficient vector, column names,
mean log-wage (weighted), and mean regressor vector (weighted).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Optional

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Regressor groups: (canonical column name, human label for reporting)
# ---------------------------------------------------------------------------

# Each entry: (column_name_in_harmonized_df, group_label_for_decomposition)
# Order matters: it determines the order of coefficient blocks.
REGRESSOR_GROUPS: list[tuple[str, str]] = [
    ("noc_43",       "occupation"),
    ("educ",         "education"),
    ("tenure_bin",   "tenure"),
    ("age_12",       "age"),
    ("gender",       "gender"),
    ("union_status", "union"),
    ("ftptmain",     "fullparttime"),
    ("prov",         "province"),
    ("permtemp",     "jobpermanency"),
    ("marstat",      "maritalstatus"),
    ("immig",        "immigration"),
    ("naics_21",     "industry"),
    ("cowmain_pub",  "sector"),
    ("estsize",      "estsize"),
    ("mjh",          "multijob"),
    # Phase B: firm size (BoC SAN 2024-23 explicitly lists both establishment
    # and firm size as covariates). firmsize uses the same 4-level scale as
    # estsize but measured at the firm level. Absent from pre-Phase-B parquets
    # (NaN-filled column); _prepare_categoricals skips columns where all values
    # are NaN, so old parquets degrade gracefully without firmsize in the design.
    ("firmsize",     "firmsize"),
]

# Map from column name to group label (used in decompose.py)
COL_TO_GROUP: dict[str, str] = {col: grp for col, grp in REGRESSOR_GROUPS}


@dataclass
class RegressionResult:
    """Output of run_wls() for one PUMF month.

    Attributes:
        coef:           Coefficient vector B (length = n_design_cols).
        col_names:      Column names of the design matrix, matching coef 1:1.
        mean_log_wage:  Weighted mean of log(wage) over the sample.
        mean_X:         Weighted mean of X (shape = n_design_cols), i.e.
                        the weighted share of each dummy category in the
                        employment distribution.
        n_obs:          Number of observations in the regression.
        r_squared:      R^2 of the WLS fit.
        dropped_cells:  Dict of {column: [dropped_category_codes]} logged
                        during empty-cell removal.
        category_universe: Dict {column: list_of_category_values} capturing
                        the union of categories seen — needed to align
                        design matrices across months.
    """
    coef: np.ndarray
    col_names: list[str]
    mean_log_wage: float
    mean_X: np.ndarray
    n_obs: int
    r_squared: float
    dropped_cells: dict = field(default_factory=dict)
    category_universe: dict = field(default_factory=dict)


def run_wls(
    df: pd.DataFrame,
    spec_weighted: bool = True,
    min_cell_count: int = 30,
    category_universe: Optional[dict] = None,
) -> RegressionResult:
    """Run the WLS log-wage regression for one month's harmonized DataFrame.

    Args:
        df:                  Harmonized DataFrame from harmonize.harmonize().
        spec_weighted:       If True, use FINALWT as regression weights (WLS).
                             If False, all weights = 1 (OLS).
        min_cell_count:      Drop categories with fewer than this many obs.
        category_universe:   Optional dict {column: sorted_list_of_categories}
                             used to build a conformable design matrix across
                             months. If None, use only categories present in df.

    Returns:
        RegressionResult with all fields populated.
    """
    df = df.copy()

    # Drop empty cells FIRST, then derive y and weights from the filtered
    # frame itself. df_clean has a reset RangeIndex, so indexing arrays
    # built from the pre-filter df by df_clean.index silently selects the
    # WRONG rows whenever thin-category pruning dropped any (observed:
    # 2015-02/2016-02/2021-02/2022-02 — misaligned y vs X gave R^2~0.004
    # and a poisoned O-B decomposition).
    df_clean, dropped_cells, cat_universe = _prepare_categoricals(
        df, min_cell_count=min_cell_count, category_universe=category_universe
    )

    # Log-transform the wage (raw dollars, already divided by 100 in harmonize)
    # log(wage) is finite for wage > 0; harmonize ensures wage > 0.
    log_wage = np.log(df_clean["wage"].values.astype(float))

    # Weights: sqrt for the WLS scaling trick
    if spec_weighted:
        weights_clean = df_clean["weight"].values.astype(float)
    else:
        weights_clean = np.ones(len(df_clean), dtype=float)

    sqrt_w = np.sqrt(weights_clean)

    X = _build_design_matrix(df_clean, cat_universe)

    # WLS: scale rows by sqrt(w)
    X_scaled = X * sqrt_w[:, np.newaxis]
    y_scaled = log_wage * sqrt_w

    # Solve WLS via lstsq (numpy's most stable least-squares solver)
    coef, _, rank, _ = np.linalg.lstsq(X_scaled, y_scaled, rcond=None)

    # Rank-deficiency guard: if rank < n_cols, drop the offending column(s)
    n_cols = X_scaled.shape[1]
    if rank < n_cols:
        logger.warning(
            "WLS design matrix is rank-deficient: rank=%d, n_cols=%d. "
            "Applying iterative column removal.",
            rank, n_cols
        )
        X, col_names_list, coef = _fix_rank_deficiency(X_scaled, y_scaled, X)
    else:
        col_names_list = list(X.columns) if hasattr(X, "columns") else [str(i) for i in range(n_cols)]

    # Compute weighted mean of X (shares of employment distribution)
    # Note: X is the un-scaled design matrix; use original weights for means
    X_unscaled = X if not hasattr(X, "values") else X.values
    total_w = weights_clean.sum()
    mean_X = (X_unscaled * weights_clean[:, np.newaxis]).sum(axis=0) / total_w

    # Weighted mean log wage
    mean_log_wage = float((log_wage * weights_clean).sum() / total_w)

    # R^2 (weighted)
    y_hat = X_unscaled @ coef
    ss_res = float((weights_clean * (log_wage - y_hat) ** 2).sum())
    ss_tot = float((weights_clean * (log_wage - mean_log_wage) ** 2).sum())
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else 0.0

    return RegressionResult(
        coef=coef,
        col_names=col_names_list,
        mean_log_wage=mean_log_wage,
        mean_X=mean_X,
        n_obs=len(df_clean),
        r_squared=r2,
        dropped_cells=dropped_cells,
        category_universe=cat_universe,
    )


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _prepare_categoricals(
    df: pd.DataFrame,
    min_cell_count: int,
    category_universe: Optional[dict],
) -> tuple[pd.DataFrame, dict, dict]:
    """Drop empty cells and determine the category universe.

    Returns:
        (df_filtered, dropped_cells, category_universe)
        df_filtered retains only rows whose categories are in the universe.
        category_universe is {column: sorted_list_of_category_values}.
    """
    dropped_cells: dict = {}
    cat_universe: dict = {}

    for col, _grp in REGRESSOR_GROUPS:
        if col not in df.columns:
            continue

        # Skip columns that are entirely NaN (e.g. firmsize in pre-Phase-B parquets).
        # These contribute no information and would cause downstream issues.
        if df[col].isna().all():
            logger.debug("column '%s': all NaN, skipping (absent from this parquet).", col)
            continue

        if category_universe is not None and col in category_universe:
            # Use the provided universe (cross-month conformability)
            cat_universe[col] = list(category_universe[col])
        else:
            # Compute from this DataFrame, dropping thin cells
            # Drop NaN before counting (NaN rows are excluded from the universe)
            counts = df[col].dropna().value_counts()
            valid_cats = sorted(counts[counts >= min_cell_count].index.tolist())
            thin_cats = sorted(counts[counts < min_cell_count].index.tolist())
            if thin_cats:
                logger.info(
                    "column '%s': dropping thin categories %s "
                    "(fewer than %d obs each).",
                    col, thin_cats, min_cell_count
                )
                dropped_cells[col] = thin_cats
            cat_universe[col] = valid_cats

        # Filter df to only rows with known categories
        # isin() returns False for NaN values, so NaN rows are excluded here
        df = df[df[col].isin(cat_universe[col])]

    return df.reset_index(drop=True), dropped_cells, cat_universe


def _build_design_matrix(df: pd.DataFrame, cat_universe: dict) -> pd.DataFrame:
    """Build the one-hot design matrix with an intercept and stable column order.

    Procedure:
      1. Prepend an intercept column.
      2. For each regressor group, create dummies restricted to the category
         universe (missing categories in df become all-zero columns).
      3. Drop the first dummy of each group (standard baseline exclusion to
         avoid dummy variable trap given the intercept).
      4. Column order is deterministic: intercept, then groups in
         REGRESSOR_GROUPS order, then alphabetically within each group.

    Returns a DataFrame with float64 columns.
    """
    parts = [pd.DataFrame({"intercept": np.ones(len(df), dtype=float)})]

    for col, _grp in REGRESSOR_GROUPS:
        if col not in df.columns or col not in cat_universe:
            continue

        cats = cat_universe[col]
        if len(cats) < 2:
            logger.info("column '%s': only 1 category remaining; skipped.", col)
            continue

        # Convert to string for stable pd.get_dummies behavior
        series = df[col].astype(str)
        cat_strings = [str(c) for c in cats]

        # Build dummies for each category in the universe
        # (categories absent from df produce all-zero columns)
        dummies = pd.get_dummies(series, prefix=col, dtype=float)

        # Reindex to the universe so absent categories become all-zero
        expected_cols = [f"{col}_{c}" for c in cat_strings]
        dummies = dummies.reindex(columns=expected_cols, fill_value=0.0)

        # Drop first dummy (baseline category) to avoid dummy variable trap
        dummies = dummies.iloc[:, 1:]

        parts.append(dummies)

    design = pd.concat(parts, axis=1)
    design = design.reset_index(drop=True)
    return design


def _fix_rank_deficiency(
    X_scaled: np.ndarray,
    y_scaled: np.ndarray,
    X_df: pd.DataFrame,
) -> tuple[pd.DataFrame, list[str], np.ndarray]:
    """Iteratively drop columns until X_scaled is full rank.

    Identifies linearly dependent columns using QR decomposition and removes
    them one at a time. Each removal is logged. Returns the pruned design
    matrix DataFrame, column name list, and new coefficient vector.
    """
    col_names = list(X_df.columns) if hasattr(X_df, "columns") else [str(i) for i in range(X_scaled.shape[1])]
    X_arr = X_scaled.copy()

    while True:
        _, R = np.linalg.qr(X_arr)
        diag = np.abs(np.diag(R))
        threshold = diag.max() * 1e-12
        bad_idx = np.where(diag < threshold)[0]
        if len(bad_idx) == 0:
            break
        drop_idx = bad_idx[-1]  # drop the last offending column
        logger.warning(
            "Dropping rank-deficient column '%s' (diag R=%.2e).",
            col_names[drop_idx], diag[drop_idx]
        )
        X_arr = np.delete(X_arr, drop_idx, axis=1)
        col_names = [c for i, c in enumerate(col_names) if i != drop_idx]

    coef, _, _, _ = np.linalg.lstsq(X_arr, y_scaled, rcond=None)

    # Return the pruned UNSCALED design matrix: the caller computes mean_X
    # (composition shares), fitted values, and R^2 from it. Returning the
    # sqrt-weight-scaled array here poisoned the O-B decomposition for any
    # rank-deficient month (observed: 2016-02, 2022-02 — degenerate R^2,
    # wrong composition shares).
    if not hasattr(X_df, "columns"):
        raise TypeError("X_df must be a DataFrame with named columns")
    pruned_df = X_df[col_names].copy()
    return pruned_df, col_names, coef


def detect_deficient_columns(X_scaled: np.ndarray, col_names: list[str]) -> list[str]:
    """Return the column names that are rank-deficient (to be dropped) in X_scaled.

    Uses QR decomposition. Returns the list of column names that would be
    dropped by _fix_rank_deficiency, without actually modifying anything.
    Iterative: removes one column at a time from the QR (same order as the fix).
    """
    X_arr = X_scaled.copy()
    names = list(col_names)
    dropped: list[str] = []
    while True:
        _, R = np.linalg.qr(X_arr)
        diag = np.abs(np.diag(R))
        threshold = diag.max() * 1e-12
        bad_idx = np.where(diag < threshold)[0]
        if len(bad_idx) == 0:
            break
        drop_idx = bad_idx[-1]
        dropped.append(names[drop_idx])
        X_arr = np.delete(X_arr, drop_idx, axis=1)
        names = [c for i, c in enumerate(names) if i != drop_idx]
    return dropped


def union_category_universe(
    result_a: RegressionResult,
    result_b: RegressionResult,
) -> dict:
    """Return the union of two regression results' category universes.

    Used by engine.py to align B_t and B_{t-12} to the same design matrix
    before the Oaxaca-Blinder decomposition.

    For each column, takes the union of observed categories, sorted.
    """
    universe: dict = {}
    all_cols = set(result_a.category_universe) | set(result_b.category_universe)
    for col in all_cols:
        cats_a = set(result_a.category_universe.get(col, []))
        cats_b = set(result_b.category_universe.get(col, []))
        universe[col] = sorted(cats_a | cats_b)
    return universe
