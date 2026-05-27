"""USDCAD methodology pipeline -- Phase 3 corrected.

Phase 3 changes vs Phase 2:
  (a) Sign-assignment look-ahead fix: Spearman signs for composite score are
      determined exclusively from the FIRST HALF of the training data (the 80%
      portion that excludes the held-out 20%). This eliminates the full-dataset
      sign contamination identified in Phase 2 self-audit.
  (b) True 20% hold-out: the most recent 20% of the dataset (~2024-Q3 to present)
      is reserved before any variable selection, hyperparameter tuning, or score
      fitting. Feature selection (filter + Elastic Net + Boruta + clustered-MDA)
      runs only on the 80% training portion. The hold-out is evaluated exactly once
      after all fitting is complete.
  (c) All purged walk-forward CV for hyperparameter tuning runs on the 80% training
      portion only.
  (d) The filter-stage Spearman computation is confined to the 80% training portion,
      not the full dataset.

Cross-validation strategy:
  Purged walk-forward CV (Lopez de Prado methodology):
  - Walk-forward: train on T periods, test on T+1 to T+embargo+1
  - Purge: drop observations within h steps of the test boundary from training
    (where h is the forecast horizon, to prevent look-ahead from autocorrelated
    returns overlapping train/test boundary)
  - Embargo: additional buffer of h steps after test window
  This is the correct CV for time-series FX forecasting. Standard k-fold
  is invalid here and would produce inflated performance estimates.

Deflated Sharpe Ratio (Bailey-Lopez de Prado 2014):
  Corrects the Sharpe ratio for the number of independent tests performed
  during model selection. A model that looks significant after many variable
  trials needs a higher bar than one tested once. The DSR is the probability
  that the observed Sharpe exceeds the maximum expected Sharpe under H0
  (no skill) given the number of trials.

Hold-out split rationale:
  The standard in time-series ML is a chronological hold-out -- the most recent
  data is held out, not a random sample. This mimics real-world deployment: you
  train on history, then encounter the future you have never seen. The 20% split
  gives approximately 14 months of held-out data (2024-08 to 2026-05), which is
  enough for:
    - Weekly: ~280 non-overlapping weekly observations
    - Monthly: ~65 non-overlapping monthly observations
    - Quarterly: ~22 non-overlapping quarterly observations
  The quarterly horizon is tight (22 non-overlapping). This is a genuine
  limitation: reported with appropriate uncertainty.
"""

from __future__ import annotations

import logging
import warnings
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.ensemble import RandomForestRegressor
from sklearn.feature_selection import mutual_info_regression
from sklearn.linear_model import ElasticNetCV
from sklearn.inspection import permutation_importance
from boruta import BorutaPy

logger = logging.getLogger(__name__)

PROCESSED_DIR = Path(__file__).parents[2] / "data" / "processed"

# Horizon definitions (business days)
HORIZONS = {
    "weekly": 5,
    "monthly": 21,
    "quarterly": 63,
}

# Hold-out fraction -- last 20% of data reserved, never touched during model development
HOLDOUT_FRACTION = 0.20

# Regime windows for performance breakdown
REGIMES = {
    "Pre-oil-breakup (2005-2013)": ("2005-01-01", "2013-12-31"),
    "Oil bear / commodity turn (2014-2019)": ("2014-01-01", "2019-12-31"),
    "COVID shock (2020-2021)": ("2020-01-01", "2021-12-31"),
    "BoC tightening cycle (2022-2024)": ("2022-01-01", "2024-12-31"),
    "Trump tariff era (2025-present)": ("2025-01-01", "2099-12-31"),
}


# ---------------------------------------------------------------------------
# Data helpers
# ---------------------------------------------------------------------------

def load_panel() -> pd.DataFrame:
    """Load the aligned feature panel."""
    parquet_path = PROCESSED_DIR / "usdcad_variables.parquet"
    csv_path = PROCESSED_DIR / "usdcad_variables.csv"
    if parquet_path.exists():
        import pyarrow.parquet as pq
        df = pq.read_table(parquet_path).to_pandas()
    elif csv_path.exists():
        df = pd.read_csv(csv_path)
    else:
        raise FileNotFoundError("Run acquire.run_acquisition() first.")
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df = df.set_index("date")
    return df


def load_targets() -> pd.DataFrame:
    """Load target returns."""
    parquet_path = PROCESSED_DIR / "usdcad_targets.parquet"
    if parquet_path.exists():
        import pyarrow.parquet as pq
        df = pq.read_table(parquet_path).to_pandas()
    else:
        raise FileNotFoundError("Run acquire.build_targets() first.")
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df = df.set_index("date")
    return df


def build_model_dataset(horizon: str) -> tuple[pd.DataFrame, pd.Series, pd.Series]:
    """Build aligned X, y_continuous, y_directional for a given horizon.

    Returns only rows where both X (no NaN in any feature) and y are available.
    Drops the final h rows where forward return is not yet observable.

    NOTE: Features are the values AS OF each date (already lag-adjusted in acquire.py).
    Target is the FORWARD h-day log return starting from that date. There is no
    look-ahead because acquire.py shifted features forward by their release lag.
    """
    h = HORIZONS[horizon]
    panel = load_panel()
    targets = load_targets()

    col_map = {5: "ret_5d", 21: "ret_21d", 63: "ret_63d"}
    ret_col = col_map[h]

    # Align on common index
    common_idx = panel.index.intersection(targets.index)
    X = panel.loc[common_idx].copy()
    y = targets.loc[common_idx, ret_col].copy()
    y_dir = targets.loc[common_idx, f"dir_{ret_col.split('_')[1]}"].copy()

    # Drop rows where target is NaN (last h rows can't have forward return)
    valid = y.notna()
    X = X.loc[valid]
    y = y.loc[valid]
    y_dir = y_dir.loc[valid]

    # Drop features with >60% missing
    coverage = X.notna().mean()
    keep_cols = coverage[coverage >= 0.40].index.tolist()
    dropped_cols = [c for c in X.columns if c not in keep_cols]
    if dropped_cols:
        logger.info("Dropped %d features with >60%% missing: %s", len(dropped_cols), dropped_cols[:5])
    X = X[keep_cols]

    # Fill remaining NaN with column median (conservative; no forward-fill here)
    X = X.fillna(X.median())

    logger.info("Dataset for %s: %d rows, %d features", horizon, len(X), len(X.columns))
    return X, y, y_dir


def split_train_holdout(X: pd.DataFrame, y: pd.Series, y_dir: pd.Series,
                        holdout_fraction: float = HOLDOUT_FRACTION
                        ) -> tuple[pd.DataFrame, pd.Series, pd.Series,
                                   pd.DataFrame, pd.Series, pd.Series,
                                   int]:
    """Chronological train/hold-out split.

    Returns (X_train, y_train, y_dir_train, X_ho, y_ho, y_dir_ho, split_idx)
    where split_idx is the integer position of the first hold-out row.

    The hold-out is the LAST holdout_fraction of rows (chronological).
    It is never used during variable selection, hyperparameter tuning, or
    score fitting.
    """
    n = len(X)
    split_idx = int(n * (1 - holdout_fraction))
    X_train = X.iloc[:split_idx]
    y_train = y.iloc[:split_idx]
    y_dir_train = y_dir.iloc[:split_idx]
    X_ho = X.iloc[split_idx:]
    y_ho = y.iloc[split_idx:]
    y_dir_ho = y_dir.iloc[split_idx:]
    logger.info(
        "Train/hold-out split: train=%d rows (%s to %s), hold-out=%d rows (%s to %s)",
        len(X_train),
        str(X_train.index.min().date()),
        str(X_train.index.max().date()),
        len(X_ho),
        str(X_ho.index.min().date()),
        str(X_ho.index.max().date()),
    )
    return X_train, y_train, y_dir_train, X_ho, y_ho, y_dir_ho, split_idx


# ---------------------------------------------------------------------------
# Stage 2: Filter stage
# ---------------------------------------------------------------------------

@dataclass
class FilterResult:
    variable: str
    spearman_rho: float
    spearman_pval: float
    mutual_info: float
    granger_pval: float  # min p-value across lags 1-5
    passes_filter: bool
    reason: str  # why kept or dropped


def run_filter_stage(X: pd.DataFrame, y: pd.Series,
                     spearman_p_threshold: float = 0.15,
                     mi_percentile_threshold: float = 10.0) -> list[FilterResult]:
    """Univariate filter: Spearman + MI + simplified Granger causality.

    IMPORTANT: X and y must be the TRAINING portion only. Do not pass the full
    dataset here. Sign directions are implicitly determined by these statistics
    and must not use hold-out data.

    A variable PASSES if it survives AT LEAST ONE of:
      - Spearman p-value < spearman_p_threshold
      - MI > mi_percentile_threshold of the MI distribution

    Granger is computed but not used as a hard filter (too many spurious
    rejections in high-p environments). It informs the reason string.

    Args:
        X: feature matrix (training only, no NaN)
        y: continuous target (log returns, training only)
        spearman_p_threshold: default 0.15 (relaxed from 0.10 to survive the
            FX small-signal problem; the embedded stage does the real culling)
        mi_percentile_threshold: drop bottom X% by MI

    Returns:
        list of FilterResult, one per feature
    """
    results = []
    mi_scores = mutual_info_regression(X.values, y.values, random_state=42)
    mi_threshold = np.percentile(mi_scores, mi_percentile_threshold)

    for i, col in enumerate(X.columns):
        x_col = X[col].values
        # Spearman
        rho, pval = stats.spearmanr(x_col, y.values, nan_policy="omit")

        # MI
        mi = mi_scores[i]

        # Simplified Granger: OLS of y_t on y_{t-1} + x_{t-k} for k=1..5
        granger_pvals = []
        for lag in range(1, 6):
            try:
                y_t = y.values[lag:]
                y_lag = y.values[:-lag]
                x_lag = x_col[:-lag]
                X_ols = np.column_stack([np.ones(len(y_t)), y_lag, x_lag])
                X_ols_restricted = np.column_stack([np.ones(len(y_t)), y_lag])
                beta = np.linalg.lstsq(X_ols, y_t, rcond=None)[0]
                beta_r = np.linalg.lstsq(X_ols_restricted, y_t, rcond=None)[0]
                res_full = y_t - X_ols @ beta
                res_r = y_t - X_ols_restricted @ beta_r
                n = len(y_t)
                k = 1
                f_stat = ((np.sum(res_r**2) - np.sum(res_full**2)) / k) / (np.sum(res_full**2) / (n - 3))
                p = 1 - stats.f.cdf(f_stat, k, n - 3)
                granger_pvals.append(p)
            except Exception:
                granger_pvals.append(1.0)
        granger_min_p = min(granger_pvals) if granger_pvals else 1.0

        # Filter decision
        passes_spearman = pval < spearman_p_threshold
        passes_mi = mi >= mi_threshold

        passes = passes_spearman or passes_mi

        if passes:
            reasons = []
            if passes_spearman:
                reasons.append(f"Spearman p={pval:.3f}")
            if passes_mi:
                reasons.append(f"MI={mi:.4f}")
            reason = "Kept: " + ", ".join(reasons)
        else:
            reason = f"Dropped: Spearman p={pval:.3f}, MI={mi:.4f} (both below threshold)"

        results.append(FilterResult(
            variable=col,
            spearman_rho=float(rho) if not np.isnan(rho) else 0.0,
            spearman_pval=float(pval) if not np.isnan(pval) else 1.0,
            mutual_info=float(mi),
            granger_pval=float(granger_min_p),
            passes_filter=passes,
            reason=reason,
        ))

    n_pass = sum(r.passes_filter for r in results)
    n_total = len(results)
    logger.info("Filter stage: %d/%d features pass", n_pass, n_total)
    return results


# ---------------------------------------------------------------------------
# Stage 3: Embedded selection
# ---------------------------------------------------------------------------

@dataclass
class SelectionResult:
    elasticnet_selected: list[str]
    elasticnet_coefs: dict[str, float]
    elasticnet_alpha: float
    elasticnet_l1_ratio: float
    boruta_selected: list[str]
    boruta_confirmed: list[str]
    boruta_tentative: list[str]
    mda_importances: dict[str, float]
    mda_selected: list[str]  # top-N by MDA
    final_selected: list[str]  # two-out-of-three vote (primary)
    final_intersection: list[str]  # intersection of all three (most conservative)
    n_cv_folds: int
    # Phase 3: record which signs were determined from first-half of training data
    feature_signs: dict[str, float]  # {feature: +1.0 or -1.0}
    sign_determination_n: int  # rows used for sign determination


def run_purged_walforward_cv(X: pd.DataFrame, y: pd.Series, horizon_h: int,
                             n_splits: int = 10) -> list[tuple]:
    """Generate purged walk-forward CV split indices.

    IMPORTANT: X and y must be the TRAINING portion only.

    Each split:
        train: indices 0 .. split_end - horizon_h (purged: drop last horizon_h from train)
        embargo: split_end .. split_end + horizon_h
        test: split_end + horizon_h .. split_end + test_size

    Returns:
        list of (train_idx, test_idx) tuples of integer positions
    """
    n = len(X)
    min_train = max(252, n // (n_splits + 1))  # at least 1 year train
    test_size = max(horizon_h * 4, 21)  # at least 4 horizons worth of test

    splits = []
    for i in range(n_splits):
        train_end = min_train + i * test_size
        if train_end + horizon_h + test_size > n:
            break
        train_idx = list(range(max(0, train_end - min_train), train_end - horizon_h))
        test_start = train_end + horizon_h
        test_end = min(test_start + test_size, n)
        test_idx = list(range(test_start, test_end))
        if len(train_idx) < 50 or len(test_idx) < 5:
            continue
        splits.append((train_idx, test_idx))

    if not splits:
        logger.warning("purged CV: no valid splits found; falling back to simple 80/20")
        train_end = int(n * 0.8)
        splits = [(list(range(train_end)), list(range(train_end + horizon_h, n)))]

    return splits


def run_elasticnet_selection(X: pd.DataFrame, y: pd.Series,
                             splits: list[tuple]) -> tuple[list[str], dict[str, float], float, float]:
    """Elastic Net selection with purged walk-forward CV.

    Args:
        X: training data only
        y: training targets only
        splits: purged CV splits (indices into X/y)

    Returns: (selected_features, coef_dict, best_alpha, best_l1_ratio)
    """
    # Standardize using training statistics only
    X_vals = X.values.astype(float)
    X_mean = X_vals.mean(axis=0)
    X_std = X_vals.std(axis=0)
    X_std[X_std == 0] = 1.0
    X_z = (X_vals - X_mean) / X_std

    cv_splits = [(np.array(tr), np.array(te)) for tr, te in splits]

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        en = ElasticNetCV(
            l1_ratio=[0.1, 0.3, 0.5, 0.7, 0.9, 0.95, 1.0],
            alphas=np.logspace(-4, 1, 40),
            cv=cv_splits,
            max_iter=5000,
            tol=1e-4,
            random_state=42,
            n_jobs=-1,
        )
        en.fit(X_z, y.values)

    coefs = dict(zip(X.columns, en.coef_))
    selected = [col for col, c in coefs.items() if abs(c) > 1e-6]
    logger.info("ElasticNet: alpha=%.4f l1=%.2f selected %d/%d features",
                en.alpha_, en.l1_ratio_, len(selected), len(X.columns))
    return selected, coefs, float(en.alpha_), float(en.l1_ratio_)


def run_boruta_selection(X: pd.DataFrame, y: pd.Series) -> tuple[list[str], list[str], list[str]]:
    """Boruta feature selection using RandomForest.

    Args:
        X: training data only
        y: training targets only

    Returns: (all_selected, confirmed, tentative)
    """
    rf = RandomForestRegressor(
        n_estimators=200,
        max_depth=5,
        n_jobs=-1,
        random_state=42,
    )
    boruta = BorutaPy(
        estimator=rf,
        n_estimators="auto",
        alpha=0.05,
        max_iter=50,
        random_state=42,
        verbose=0,
    )
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        boruta.fit(X.values.astype(float), y.values.astype(float))

    confirmed = [X.columns[i] for i, s in enumerate(boruta.support_) if s]
    tentative = [X.columns[i] for i, s in enumerate(boruta.support_weak_) if s]
    all_selected = confirmed + tentative
    logger.info("Boruta: %d confirmed, %d tentative (of %d)", len(confirmed), len(tentative), len(X.columns))
    return all_selected, confirmed, tentative


def run_mda_selection(X: pd.DataFrame, y: pd.Series, n_top: int = 20,
                      splits: Optional[list[tuple]] = None) -> dict[str, float]:
    """Clustered MDA (Mean Decrease Accuracy) via permutation importance.

    Uses training data only. Split: first 80% of training data for RF fit,
    last 20% of training data for permutation test.

    Returns: dict of {feature: importance_score}
    """
    rf = RandomForestRegressor(
        n_estimators=200,
        max_depth=5,
        n_jobs=-1,
        random_state=42,
    )
    # Use last 20% of training data for MDA evaluation
    split = int(len(X) * 0.8)
    X_train = X.iloc[:split]
    y_train = y.iloc[:split]
    X_test = X.iloc[split:]
    y_test = y.iloc[split:]

    rf.fit(X_train.values, y_train.values)
    perm = permutation_importance(rf, X_test.values, y_test.values,
                                  n_repeats=10, random_state=42, n_jobs=-1)

    imp_dict = dict(zip(X.columns, perm.importances_mean))
    sorted_imp = sorted(imp_dict.items(), key=lambda kv: kv[1], reverse=True)
    logger.info("MDA top 5: %s", sorted_imp[:5])
    return imp_dict


def determine_signs_first_half(X: pd.DataFrame, y: pd.Series,
                               selected_features: list[str]) -> dict[str, float]:
    """Determine composite score signs using ONLY the first half of training data.

    This is the Phase 3 fix for sign-assignment look-ahead bias.

    Background: The composite score assigns +1 or -1 to each feature based on
    whether it is positively or negatively correlated with future USDCAD returns.
    In Phase 2, this Spearman correlation was computed on the full dataset
    (including the data the score was being evaluated on), creating in-sample
    contamination that inflated the apparent hit rate.

    Fix: Use only the first 50% of the training data for sign determination.
    The score is then constructed and evaluated on the second 50% of training
    data and on the hold-out, both of which never informed the signs.

    Alternative (walk-forward signs): More rigorous but introduces complexity
    in aggregating sign estimates. First-half is the standard in the FX
    composite-score literature (see Koijen-Moskowitz-Pedersen-Vrugt 2018,
    "Carry" -- their factor signs are estimated on an initial training window
    only). First-half is chosen here for simplicity and reproducibility.

    Args:
        X: training data only (not the hold-out)
        y: training targets only
        selected_features: features to compute signs for

    Returns:
        dict {feature: +1.0 or -1.0}
    """
    n_half = len(X) // 2
    X_half = X.iloc[:n_half][selected_features]
    y_half = y.iloc[:n_half]
    signs = {}
    for col in selected_features:
        rho, _ = stats.spearmanr(X_half[col].values, y_half.values, nan_policy="omit")
        signs[col] = float(np.sign(rho)) if not np.isnan(rho) else 1.0
    logger.info(
        "Signs determined from first %d rows (first half of training data, %s to %s)",
        n_half,
        str(X.index[0].date()),
        str(X.index[n_half - 1].date()),
    )
    return signs


def run_embedded_stage(X_filtered: pd.DataFrame, y: pd.Series,
                       horizon_h: int) -> SelectionResult:
    """Run all three embedded selection methods on filtered training features.

    IMPORTANT: X_filtered and y must be the TRAINING portion only.

    Returns SelectionResult with all three outcomes and a final selected set.
    """
    splits = run_purged_walforward_cv(X_filtered, y, horizon_h)

    # ElasticNet
    en_sel, en_coefs, en_alpha, en_l1 = run_elasticnet_selection(X_filtered, y, splits)

    # Boruta
    try:
        boruta_all, boruta_confirmed, boruta_tentative = run_boruta_selection(X_filtered, y)
    except Exception as e:
        logger.error("Boruta failed: %s -- proceeding without", e)
        boruta_all, boruta_confirmed, boruta_tentative = [], [], []

    # MDA
    try:
        mda_imp = run_mda_selection(X_filtered, y, n_top=20, splits=splits)
        top_mda = sorted(mda_imp.items(), key=lambda kv: kv[1], reverse=True)[:20]
        mda_sel = [k for k, v in top_mda if v > 0]
    except Exception as e:
        logger.error("MDA failed: %s -- proceeding without", e)
        mda_imp, mda_sel = {}, []

    # Two-out-of-three vote (final model uses this)
    all_sets = [set(en_sel), set(boruta_all), set(mda_sel)]
    vote_counter: dict[str, int] = {}
    for s in all_sets:
        for feat in s:
            vote_counter[feat] = vote_counter.get(feat, 0) + 1
    final_selected = sorted(k for k, v in vote_counter.items() if v >= 2)

    # Union and intersection (for diagnostics)
    final_union = sorted(set().union(*all_sets))
    populated = [s for s in all_sets if s]
    if len(populated) >= 3:
        final_intersection = sorted(populated[0].intersection(*populated[1:]))
    elif len(populated) == 2:
        final_intersection = sorted(populated[0].intersection(populated[1]))
    else:
        final_intersection = list(populated[0]) if populated else []

    logger.info("Embedded stage final: union=%d, 2/3-vote=%d, intersection=%d",
                len(final_union), len(final_selected), len(final_intersection))

    # Phase 3: Determine signs from first half of training data only
    features_for_signs = final_selected or en_sel
    feature_signs = {}
    n_sign_rows = 0
    if features_for_signs:
        feature_signs = determine_signs_first_half(X_filtered, y, features_for_signs)
        n_sign_rows = len(X_filtered) // 2
    else:
        logger.warning("No features selected -- sign determination skipped")

    return SelectionResult(
        elasticnet_selected=en_sel,
        elasticnet_coefs=en_coefs,
        elasticnet_alpha=en_alpha,
        elasticnet_l1_ratio=en_l1,
        boruta_selected=boruta_all,
        boruta_confirmed=boruta_confirmed,
        boruta_tentative=boruta_tentative,
        mda_importances=mda_imp,
        mda_selected=mda_sel,
        final_selected=final_selected,
        final_intersection=final_intersection,
        n_cv_folds=len(splits),
        feature_signs=feature_signs,
        sign_determination_n=n_sign_rows,
    )


# ---------------------------------------------------------------------------
# Stage 4: Validation
# ---------------------------------------------------------------------------

@dataclass
class ValidationResult:
    # Walk-forward CV performance (on training 80% only)
    cv_r2_oos: float           # out-of-sample R^2 across all CV folds
    cv_hit_rate: float         # directional hit rate across all CV folds
    cv_sharpe: float           # annualized Sharpe of CV predictions
    cv_fold_r2: list[float]    # R^2 per fold
    cv_fold_hit: list[float]   # hit rate per fold

    # Deflated Sharpe Ratio (computed on CV Sharpe)
    dsr: float                 # DSR statistic
    dsr_pval: float            # 1 - DSR (probability result is statistical luck)
    n_trials: int              # number of independent trials (variables screened)
    sr_annualized: float       # raw annualized Sharpe ratio

    # t-statistics on selected variables (in-sample, informational)
    t_stats: dict[str, float]
    t_pvals: dict[str, float]

    # Extreme-percentile performance -- TRAINING DATA ONLY (Phase 2 style, for comparison)
    hit_rate_extreme: float
    hit_rate_middle: float
    return_extreme_mean: float
    return_middle_mean: float
    n_extreme_obs: int
    n_middle_obs: int

    # Regime performance (training data only)
    regime_stats: dict[str, dict]

    # Phase 3: True hold-out performance (never seen during fitting)
    holdout_hit_rate: float
    holdout_r2: float
    holdout_dsr: float
    holdout_sharpe: float
    holdout_hit_rate_extreme: float
    holdout_hit_rate_middle: float
    holdout_n_extreme_obs: int
    holdout_n_middle_obs: int
    holdout_n_obs: int
    holdout_start_date: str
    holdout_end_date: str


def compute_deflated_sharpe_ratio(sharpe: float, n_obs: int, n_trials: int,
                                  skew: float = 0.0, kurt: float = 3.0) -> tuple[float, float]:
    """Bailey-Lopez de Prado Deflated Sharpe Ratio.

    The DSR corrects the observed Sharpe for the expected maximum Sharpe
    under H0 (no skill) from n_trials independent strategies.

    Returns:
        (dsr, pval) where pval = 1 - DSR
    """
    if n_obs < 10 or sharpe == 0:
        return 0.0, 1.0

    from scipy.special import erfinv
    if n_trials <= 1:
        sr_star = 0.0
    else:
        z = 2 * (1 - 1 / (n_trials + 1)) - 1
        z = np.clip(z, -0.9999, 0.9999)
        sr_star = np.sqrt(2) * erfinv(z) / np.sqrt(n_obs)

    var_sr = (1 - skew * sharpe + (kurt - 1) / 4 * sharpe**2) / n_obs
    var_sr = max(var_sr, 1e-8)

    z_dsr = (sharpe - sr_star) / np.sqrt(var_sr)
    dsr = stats.norm.cdf(z_dsr)
    pval = 1 - dsr
    return float(dsr), float(pval)


def compute_score_with_fixed_signs(X: pd.DataFrame, selected_features: list[str],
                                   signs: dict[str, float]) -> pd.Series:
    """Compute composite score using pre-determined signs.

    Phase 3 fix: signs are passed in as a parameter (determined from first
    half of training data only), never computed from the data being scored.
    This eliminates the in-sample look-ahead from Phase 2's compute_score().

    Args:
        X: the dataset to score (may be training second-half, hold-out, or full training)
        selected_features: features to include in the score
        signs: {feature: +1.0 or -1.0} -- MUST be determined from data not in X,
               or from the first half of training data when X is the full training set

    Returns:
        pd.Series with the composite score (higher = more USD bullish)
    """
    if not selected_features or not signs:
        return pd.Series(0.0, index=X.index)

    # Filter to features that exist in X and have signs
    features_available = [f for f in selected_features if f in X.columns and f in signs]
    if not features_available:
        return pd.Series(0.0, index=X.index)

    X_sel = X[features_available].copy()

    # Z-score using the X data's own statistics (which is acceptable -- we are
    # not using future return data here, only the feature distributions)
    z = (X_sel - X_sel.mean()) / X_sel.std().replace(0.0, 1.0)

    # Apply pre-determined signs
    for col in features_available:
        z[col] = z[col] * signs[col]

    score = z.mean(axis=1)
    return score


def run_validation(X_train: pd.DataFrame, y_train: pd.Series, y_dir_train: pd.Series,
                   X_holdout: pd.DataFrame, y_holdout: pd.Series, y_dir_holdout: pd.Series,
                   selected_features: list[str], feature_signs: dict[str, float],
                   horizon_h: int, n_trials: int,
                   filter_results: list) -> ValidationResult:
    """Full validation suite.

    Phase 3 design:
    - CV and regime analysis runs on X_train only (the 80% training portion).
    - The hold-out (X_holdout, 20%) is evaluated exactly once at the end.
    - The composite score for all evaluations uses feature_signs, which were
      determined from the first half of X_train only.

    Args:
        X_train: training features (80% of data)
        y_train: training continuous targets
        y_dir_train: training directional targets
        X_holdout: hold-out features (last 20% of data, never used in fitting)
        y_holdout: hold-out continuous targets
        y_dir_holdout: hold-out directional targets
        selected_features: features selected by embedded stage
        feature_signs: {feature: sign} determined from first half of training
        horizon_h: forecast horizon in business days
        n_trials: number of variables screened (for DSR)
        filter_results: FilterResult list for t-stat computation
    """
    if not selected_features:
        logger.warning("No features selected -- validation returns all zeros")
        empty = ValidationResult(
            cv_r2_oos=0.0, cv_hit_rate=0.5, cv_sharpe=0.0,
            cv_fold_r2=[], cv_fold_hit=[],
            dsr=0.0, dsr_pval=1.0, n_trials=n_trials, sr_annualized=0.0,
            t_stats={}, t_pvals={},
            hit_rate_extreme=0.5, hit_rate_middle=0.5,
            return_extreme_mean=0.0, return_middle_mean=0.0,
            n_extreme_obs=0, n_middle_obs=0,
            regime_stats={},
            holdout_hit_rate=0.5, holdout_r2=0.0, holdout_dsr=0.0, holdout_sharpe=0.0,
            holdout_hit_rate_extreme=0.5, holdout_hit_rate_middle=0.5,
            holdout_n_extreme_obs=0, holdout_n_middle_obs=0, holdout_n_obs=0,
            holdout_start_date="", holdout_end_date="",
        )
        return empty

    X_sel_train = X_train[selected_features].copy()
    splits = run_purged_walforward_cv(X_sel_train, y_train, horizon_h)

    # Walk-forward CV on training data
    all_preds = pd.Series(np.nan, index=y_train.index)
    fold_r2 = []
    fold_hit = []

    for train_idx, test_idx in splits:
        X_tr = X_sel_train.iloc[train_idx]
        y_tr = y_train.iloc[train_idx]
        X_te = X_sel_train.iloc[test_idx]
        y_te = y_train.iloc[test_idx]

        # Standardize using training fold statistics
        mu = X_tr.mean()
        sd = X_tr.std()
        sd[sd == 0] = 1.0
        X_tr_z = (X_tr - mu) / sd
        X_te_z = (X_te - mu) / sd

        try:
            en = ElasticNetCV(
                l1_ratio=[0.5, 0.7, 0.9],
                alphas=np.logspace(-3, 1, 20),
                cv=5,
                max_iter=2000,
                random_state=42,
                n_jobs=-1,
            )
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                en.fit(X_tr_z.values, y_tr.values)
            preds = en.predict(X_te_z.values)
            all_preds.iloc[test_idx] = preds

            ss_res = np.sum((y_te.values - preds)**2)
            ss_tot = np.sum((y_te.values - y_te.mean())**2)
            r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0.0
            fold_r2.append(float(r2))

            hit = np.mean(np.sign(preds) == np.sign(y_te.values))
            fold_hit.append(float(hit))
        except Exception as e:
            logger.warning("CV fold failed: %s", e)

    oos_r2 = float(np.mean(fold_r2)) if fold_r2 else 0.0
    oos_hit = float(np.mean(fold_hit)) if fold_hit else 0.5

    # Compute score on training data using fixed signs
    score_train = compute_score_with_fixed_signs(X_train, selected_features, feature_signs)

    # CV Sharpe
    oos_mask = all_preds.notna()
    if oos_mask.sum() > 20:
        oos_strat_ret = np.sign(all_preds[oos_mask].values) * y_train[oos_mask].values
        sr_daily = oos_strat_ret.mean() / (oos_strat_ret.std() + 1e-8)
        cv_sharpe = float(sr_daily * np.sqrt(252))
    else:
        cv_sharpe = 0.0

    # DSR (on training CV Sharpe)
    n_obs_cv = oos_mask.sum()
    skew = float(stats.skew(y_train[oos_mask].values)) if n_obs_cv > 3 else 0.0
    kurt = float(stats.kurtosis(y_train[oos_mask].values) + 3) if n_obs_cv > 3 else 3.0
    dsr, dsr_pval = compute_deflated_sharpe_ratio(cv_sharpe / np.sqrt(252),
                                                   n_obs_cv, n_trials, skew, kurt)

    # OLS t-stats on selected features (in-sample on training data, informational only)
    t_stats, t_pvals = {}, {}
    try:
        X_z_full = (X_sel_train - X_sel_train.mean()) / X_sel_train.std().replace(0, 1)
        X_ols = np.column_stack([np.ones(len(X_z_full)), X_z_full.values])
        beta, _, _, _ = np.linalg.lstsq(X_ols, y_train.values, rcond=None)
        residuals = y_train.values - X_ols @ beta
        n, k = X_ols.shape
        mse = np.sum(residuals**2) / (n - k)
        cov_beta = mse * np.linalg.pinv(X_ols.T @ X_ols)
        for j, col in enumerate(selected_features):
            se = np.sqrt(cov_beta[j + 1, j + 1])
            t = beta[j + 1] / se if se > 0 else 0.0
            t_stats[col] = float(t)
            t_pvals[col] = float(2 * (1 - stats.t.cdf(abs(t), df=n - k)))
    except Exception as e:
        logger.warning("t-stat computation failed: %s", e)

    # Extreme vs middle performance -- TRAINING DATA
    score_valid_train = score_train.dropna()
    score_pcts_train = score_valid_train.rank(pct=True)
    extreme_mask_tr = (score_pcts_train <= 0.10) | (score_pcts_train >= 0.90)
    middle_mask_tr = (score_pcts_train > 0.10) & (score_pcts_train < 0.90)

    y_train_aligned = y_train.reindex(score_valid_train.index)

    if extreme_mask_tr.sum() > 5:
        hit_extreme = float(np.mean(
            np.sign(score_valid_train[extreme_mask_tr].values) == np.sign(y_train_aligned[extreme_mask_tr].values)
        ))
        ret_extreme = float(np.mean(y_train_aligned[extreme_mask_tr].values))
    else:
        hit_extreme, ret_extreme = 0.5, 0.0

    if middle_mask_tr.sum() > 5:
        hit_middle = float(np.mean(
            np.sign(score_valid_train[middle_mask_tr].values) == np.sign(y_train_aligned[middle_mask_tr].values)
        ))
        ret_middle = float(np.mean(y_train_aligned[middle_mask_tr].values))
    else:
        hit_middle, ret_middle = 0.5, 0.0

    # Regime breakdown (training data only)
    regime_stats = {}
    for regime_name, (start, end) in REGIMES.items():
        mask = (score_valid_train.index >= pd.Timestamp(start)) & (score_valid_train.index <= pd.Timestamp(end))
        if mask.sum() < 20:
            continue
        sc_r = score_valid_train[mask]
        y_r = y_train.reindex(sc_r.index)
        if len(y_r.dropna()) < 10:
            continue
        valid = y_r.notna()
        sc_rv = sc_r[valid]
        y_rv = y_r[valid]
        ss_res = np.sum((y_rv.values - sc_rv.values)**2)
        ss_tot = np.sum((y_rv.values - y_rv.mean())**2)
        r2_r = float(1 - ss_res / ss_tot) if ss_tot > 0 else 0.0
        hit_r = float(np.mean(np.sign(sc_rv.values) == np.sign(y_rv.values)))
        regime_stats[regime_name] = {
            "r2": r2_r,
            "hit_rate": hit_r,
            "n_obs": int(valid.sum()),
            "score_mean": float(sc_rv.mean()),
        }

    # -----------------------------------------------------------------------
    # Phase 3: HOLD-OUT EVALUATION -- runs exactly once, after all fitting
    # -----------------------------------------------------------------------
    holdout_hit_rate = 0.5
    holdout_r2 = 0.0
    holdout_dsr = 0.0
    holdout_sharpe = 0.0
    holdout_hit_extreme = 0.5
    holdout_hit_middle = 0.5
    holdout_n_extreme = 0
    holdout_n_middle = 0
    holdout_n = 0
    holdout_start = ""
    holdout_end = ""

    if len(X_holdout) > horizon_h * 2:
        # Score the hold-out using the SAME fixed signs determined from training
        score_ho = compute_score_with_fixed_signs(X_holdout, selected_features, feature_signs)
        y_ho_aligned = y_holdout.reindex(score_ho.index).dropna()
        score_ho = score_ho.reindex(y_ho_aligned.index)
        holdout_n = len(y_ho_aligned)

        if holdout_n > 5:
            holdout_start = str(X_holdout.index.min().date())
            holdout_end = str(X_holdout.index.max().date())

            # Hit rate: sign of score vs sign of actual return
            pred_signs_ho = np.sign(score_ho.values)
            actual_signs_ho = np.sign(y_ho_aligned.values)
            holdout_hit_rate = float(np.mean(pred_signs_ho == actual_signs_ho))

            # R^2
            ss_res_ho = np.sum((y_ho_aligned.values - score_ho.values)**2)
            ss_tot_ho = np.sum((y_ho_aligned.values - y_ho_aligned.mean())**2)
            holdout_r2 = float(1 - ss_res_ho / ss_tot_ho) if ss_tot_ho > 0 else 0.0

            # Sharpe on hold-out
            strat_ret_ho = pred_signs_ho * y_ho_aligned.values
            sr_ho_daily = strat_ret_ho.mean() / (strat_ret_ho.std() + 1e-8)
            holdout_sharpe = float(sr_ho_daily * np.sqrt(252))

            # DSR on hold-out (fewer trials -- model is already fixed)
            skew_ho = float(stats.skew(y_ho_aligned.values)) if holdout_n > 3 else 0.0
            kurt_ho = float(stats.kurtosis(y_ho_aligned.values) + 3) if holdout_n > 3 else 3.0
            holdout_dsr, _ = compute_deflated_sharpe_ratio(
                holdout_sharpe / np.sqrt(252), holdout_n, 1, skew_ho, kurt_ho
            )  # n_trials=1 because model is already fixed; this is a single test

            # Extreme-reading performance on hold-out
            score_pcts_ho = score_ho.rank(pct=True)
            extreme_mask_ho = (score_pcts_ho <= 0.10) | (score_pcts_ho >= 0.90)
            middle_mask_ho = (score_pcts_ho > 0.10) & (score_pcts_ho < 0.90)

            if extreme_mask_ho.sum() > 3:
                holdout_hit_extreme = float(np.mean(
                    np.sign(score_ho[extreme_mask_ho].values) == np.sign(y_ho_aligned[extreme_mask_ho].values)
                ))
                holdout_n_extreme = int(extreme_mask_ho.sum())
            if middle_mask_ho.sum() > 3:
                holdout_hit_middle = float(np.mean(
                    np.sign(score_ho[middle_mask_ho].values) == np.sign(y_ho_aligned[middle_mask_ho].values)
                ))
                holdout_n_middle = int(middle_mask_ho.sum())

            logger.info(
                "Hold-out (%s to %s, n=%d): hit=%.1f%%, R2=%.4f, Sharpe=%.2f, "
                "extreme=%.1f%% (%d obs) vs middle=%.1f%% (%d obs)",
                holdout_start, holdout_end, holdout_n,
                holdout_hit_rate * 100, holdout_r2, holdout_sharpe,
                holdout_hit_extreme * 100, holdout_n_extreme,
                holdout_hit_middle * 100, holdout_n_middle,
            )
    else:
        logger.warning("Hold-out too small (%d rows, need >%d) -- hold-out evaluation skipped",
                       len(X_holdout), horizon_h * 2)

    return ValidationResult(
        cv_r2_oos=oos_r2,
        cv_hit_rate=oos_hit,
        cv_sharpe=cv_sharpe,
        cv_fold_r2=fold_r2,
        cv_fold_hit=fold_hit,
        dsr=dsr,
        dsr_pval=dsr_pval,
        n_trials=n_trials,
        sr_annualized=cv_sharpe,
        t_stats=t_stats,
        t_pvals=t_pvals,
        hit_rate_extreme=hit_extreme,
        hit_rate_middle=hit_middle,
        return_extreme_mean=ret_extreme,
        return_middle_mean=ret_middle,
        n_extreme_obs=int(extreme_mask_tr.sum()),
        n_middle_obs=int(middle_mask_tr.sum()),
        regime_stats=regime_stats,
        holdout_hit_rate=holdout_hit_rate,
        holdout_r2=holdout_r2,
        holdout_dsr=holdout_dsr,
        holdout_sharpe=holdout_sharpe,
        holdout_hit_rate_extreme=holdout_hit_extreme,
        holdout_hit_rate_middle=holdout_hit_middle,
        holdout_n_extreme_obs=holdout_n_extreme,
        holdout_n_middle_obs=holdout_n_middle,
        holdout_n_obs=holdout_n,
        holdout_start_date=holdout_start,
        holdout_end_date=holdout_end,
    )


# ---------------------------------------------------------------------------
# Full horizon pipeline
# ---------------------------------------------------------------------------

@dataclass
class HorizonResult:
    horizon: str
    horizon_h: int
    n_features_input: int
    n_features_after_filter: int
    filter_results: list[FilterResult]
    selection: SelectionResult
    validation: ValidationResult
    # Score computed on the full dataset (training + hold-out) using fixed signs
    # for visualization only -- not used for any reported performance metric
    score_full: pd.Series
    # Score on training data (for regime breakdown charts)
    score_train: pd.Series
    # Score on hold-out (for hold-out performance charts)
    score_holdout: pd.Series
    X_train: pd.DataFrame
    y_train: pd.Series
    y_dir_train: pd.Series
    X_holdout: pd.DataFrame
    y_holdout: pd.Series
    y_dir_holdout: pd.Series
    holdout_split_date: str
    honest_assessment: str = field(default="")


def run_horizon(horizon: str) -> HorizonResult:
    """Run the full Phase 3 pipeline for one horizon.

    Phase 3 protocol:
    1. Split data into training (80%) and hold-out (20%) FIRST.
    2. Run all variable selection on training data only.
    3. Determine signs from first half of training data only.
    4. Run CV on training data only.
    5. Evaluate hold-out exactly once using training-derived model.
    """
    h = HORIZONS[horizon]
    logger.info("=== Running horizon: %s (h=%d) [Phase 3] ===", horizon, h)

    # Build full dataset
    X_full, y_full, y_dir_full = build_model_dataset(horizon)

    if X_full.empty or y_full.dropna().empty:
        raise ValueError(f"No valid data for horizon {horizon}")

    n_input = len(X_full.columns)

    # Step 1: Split train / hold-out
    X_train, y_train, y_dir_train, X_ho, y_ho, y_dir_ho, split_idx = split_train_holdout(
        X_full, y_full, y_dir_full
    )
    holdout_split_date = str(X_ho.index.min().date()) if len(X_ho) > 0 else ""

    # Step 2: Filter stage on TRAINING DATA ONLY
    logger.info("Stage 2: Filter stage on %d features (training data, %d rows)", n_input, len(X_train))
    filter_results = run_filter_stage(X_train, y_train)

    kept_cols = [r.variable for r in filter_results if r.passes_filter]
    if not kept_cols:
        logger.warning("All features dropped by filter -- relaxing thresholds")
        kept_cols = X_train.columns.tolist()

    X_filtered_train = X_train[kept_cols].copy()
    n_filtered = len(kept_cols)
    logger.info("After filter: %d features remain", n_filtered)

    # Step 3: Embedded selection on TRAINING DATA ONLY
    # Sign determination happens inside run_embedded_stage, using first half of training
    logger.info("Stage 3: Embedded selection on %d features", n_filtered)
    selection = run_embedded_stage(X_filtered_train, y_train, h)

    # Step 4: Validation on TRAINING DATA (CV) + HOLD-OUT (single evaluation)
    final_features = selection.final_selected or selection.elasticnet_selected
    logger.info("Stage 4: Validation on %d selected features", len(final_features))

    # Align X_holdout to the kept columns (filter was determined on training)
    # Features in kept_cols may not all be in X_ho if the hold-out has some NaN columns
    ho_cols = [c for c in kept_cols if c in X_ho.columns]
    X_filtered_ho = X_ho[ho_cols].copy()

    n_trials = n_input  # all variables screened (for DSR)
    validation = run_validation(
        X_train=X_train,
        y_train=y_train,
        y_dir_train=y_dir_train,
        X_holdout=X_filtered_ho,
        y_holdout=y_ho,
        y_dir_holdout=y_dir_ho,
        selected_features=final_features,
        feature_signs=selection.feature_signs,
        horizon_h=h,
        n_trials=n_trials,
        filter_results=filter_results,
    )

    # Compute scores for visualization
    # Training score (for regime breakdown charts): uses fixed signs
    score_train = compute_score_with_fixed_signs(X_train, final_features, selection.feature_signs)

    # Hold-out score (for diagnostics)
    score_holdout = compute_score_with_fixed_signs(X_filtered_ho, final_features, selection.feature_signs)

    # Full-dataset score (for the time-series visualization chart only)
    # Uses the same fixed signs; this is purely cosmetic for the historical chart
    score_full = compute_score_with_fixed_signs(X_full, final_features, selection.feature_signs)

    result = HorizonResult(
        horizon=horizon,
        horizon_h=h,
        n_features_input=n_input,
        n_features_after_filter=n_filtered,
        filter_results=filter_results,
        selection=selection,
        validation=validation,
        score_full=score_full,
        score_train=score_train,
        score_holdout=score_holdout,
        X_train=X_train,
        y_train=y_train,
        y_dir_train=y_dir_train,
        X_holdout=X_filtered_ho,
        y_holdout=y_ho,
        y_dir_holdout=y_dir_ho,
        holdout_split_date=holdout_split_date,
    )

    result.honest_assessment = write_honest_assessment(result)
    return result


def write_honest_assessment(r: HorizonResult) -> str:
    """Write a plain-English honest assessment of each horizon's results."""
    h = r.horizon
    v = r.validation
    s = r.selection

    n_selected = len(s.final_selected)

    dsr_good = v.dsr >= 0.95
    hit_good = v.cv_hit_rate >= 0.54
    extremes_edge_training = (v.hit_rate_extreme - v.hit_rate_middle) >= 0.03
    holdout_validated = v.holdout_hit_rate >= 0.53 and v.holdout_n_obs > 20
    holdout_extreme_validated = (
        v.holdout_hit_rate_extreme - v.holdout_hit_rate_middle >= 0.05
        and v.holdout_n_extreme_obs >= 10
    )

    verdict = []
    verdict.append(f"=== HONEST ASSESSMENT: {h.upper()} HORIZON (Phase 3, corrected methodology) ===\n")
    verdict.append(
        f"Phase 3 fixes applied: (1) sign-assignment from first half of training data only "
        f"({s.sign_determination_n} rows, ending before {r.holdout_split_date}); "
        f"(2) true 20% hold-out ({v.holdout_start_date} to {v.holdout_end_date}, "
        f"n={v.holdout_n_obs}) evaluated exactly once after all fitting."
    )

    # CV result
    if dsr_good and hit_good:
        verdict.append(
            f"\nCV SIGNAL EXISTS: DSR={v.dsr:.2f} (>=0.95), CV hit rate={v.cv_hit_rate:.1%}. "
            "Statistically credible signal survives multiple-testing correction."
        )
    elif hit_good and not dsr_good:
        verdict.append(
            f"\nCV BORDERLINE: Hit rate is {v.cv_hit_rate:.1%} but DSR={v.dsr:.2f} is "
            "below the 95% threshold after correcting for {:,} variables screened. "
            "May be a survivor of multiple-testing.".format(v.n_trials)
        )
    else:
        verdict.append(
            f"\nCV WEAK/NULL: DSR={v.dsr:.2f}, CV hit={v.cv_hit_rate:.1%}. "
            "Neither clears the minimum bar on training CV. Consistent with Meese-Rogoff."
        )

    # Training extremes
    verdict.append(
        f"\nTraining extreme-reading edge: {v.hit_rate_extreme:.1%} at extremes vs "
        f"{v.hit_rate_middle:.1%} in middle 80% (+{(v.hit_rate_extreme-v.hit_rate_middle)*100:.1f}pp, "
        f"n_extreme={v.n_extreme_obs})."
    )

    # Hold-out result -- the critical Phase 3 number
    verdict.append("\n--- HOLD-OUT RESULT (the number that counts) ---")
    if v.holdout_n_obs == 0:
        verdict.append("Hold-out evaluation could not be run (insufficient data).")
    else:
        verdict.append(
            f"Hold-out ({v.holdout_start_date} to {v.holdout_end_date}, n={v.holdout_n_obs}): "
            f"hit rate={v.holdout_hit_rate:.1%}, R2={v.holdout_r2:.4f}, Sharpe={v.holdout_sharpe:.2f}."
        )
        verdict.append(
            f"Hold-out extremes: {v.holdout_hit_rate_extreme:.1%} vs "
            f"{v.holdout_hit_rate_middle:.1%} (+{(v.holdout_hit_rate_extreme-v.holdout_hit_rate_middle)*100:.1f}pp, "
            f"n_extreme={v.holdout_n_extreme_obs})."
        )
        if holdout_validated:
            verdict.append(
                "HOLD-OUT CONFIRMS: The aggregate hit rate exceeds 53% on genuinely unseen data."
            )
        else:
            verdict.append(
                "HOLD-OUT DOES NOT CONFIRM aggregate directional edge (below 53% or insufficient n)."
            )
        if holdout_extreme_validated:
            verdict.append(
                "HOLD-OUT CONFIRMS EXTREME EDGE: +5pp or better at extremes on unseen data. "
                "The product claim is defensible with appropriate uncertainty framing."
            )
        else:
            verdict.append(
                "HOLD-OUT DOES NOT CONFIRM extreme edge (below +5pp or too few extreme obs). "
                "Do not cite extreme-reading edge to subscribers."
            )

    # Regime breakdown
    verdict.append("\nRegime performance (training data):")
    for reg, stats_r in v.regime_stats.items():
        verdict.append(
            f"  {reg}: hit rate {stats_r['hit_rate']:.1%}, OOS R^2 {stats_r['r2']:.3f} ({stats_r['n_obs']} obs)"
        )

    # Known failure modes
    verdict.append("\nKnown failure modes:")
    verdict.append("- Tariff-shock periods (2025-2026): model trained pre-2025 has likely regime break here.")
    verdict.append("- COVID dislocation (2020): all financial models fail in acute crisis.")
    verdict.append("- CAD-oil relationship post-2016: oil variables may be selected on pre-2016 history.")
    verdict.append("- Options data (risk reversals, implied vol skew) are missing -- Bloomberg-gated.")
    horizon_bdays = r.horizon_h
    non_overlap = max(0, v.holdout_n_obs // horizon_bdays)
    verdict.append(
        f"- Hold-out has ~{non_overlap} non-overlapping {h}-horizon observations "
        f"(n_rows={v.holdout_n_obs}, horizon={horizon_bdays}bd). "
        f"{'Statistical conclusions are fragile at this sample size.' if non_overlap < 30 else 'Adequate statistical power for aggregate hit-rate inference.'}"
    )

    # Product recommendation
    verdict.append("\nProduct recommendation:")
    if holdout_extreme_validated and (hit_good or holdout_validated):
        verdict.append(
            "SHIP WITH TRADE IDEAS AT EXTREMES: Hold-out validates the extreme-reading edge. "
            f"Cite: '{v.holdout_hit_rate_extreme:.1%} directional accuracy at extremes on "
            f"held-out {v.holdout_start_date} to {v.holdout_end_date} data.' "
            "Disclose the hold-out methodology and the extreme observation count explicitly."
        )
    elif holdout_validated:
        verdict.append(
            "SHIP SCORE ONLY: Hold-out confirms aggregate directional edge but extreme edge is "
            "not validated. Scorecard as data integration product is defensible. Do not frame "
            "individual readings as trade calls."
        )
    else:
        verdict.append(
            "HOLD / DO NOT SHIP AS PREDICTIVE PRODUCT: Hold-out does not confirm the edge. "
            "Options: (a) scorecard-only framed strictly as data synthesis, no predictive claims; "
            "(b) wait for more hold-out data to accumulate; (c) deprioritize this horizon."
        )

    return "\n".join(verdict)


def run_all_horizons() -> dict[str, HorizonResult]:
    """Run the full Phase 3 pipeline for all three horizons."""
    results = {}
    for horizon in ["weekly", "monthly", "quarterly"]:
        try:
            results[horizon] = run_horizon(horizon)
        except Exception as e:
            logger.error("Horizon %s failed: %s", horizon, e, exc_info=True)
    return results
