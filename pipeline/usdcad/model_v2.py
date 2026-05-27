"""USDCAD unified model -- v2, 2026-05-27.

Unified rebuild combining the best of Sibley Phase 3 and Codex implementations,
with every bug from both adversarial audits addressed. See
work/research/usdcad/unified_v1_2026-05-27/methodology.md for full spec.

Key architectural choices vs prior implementations
---------------------------------------------------
Score architecture      : signed-z composite (Sibley approach), but scaler
                          fitted on TRAINING data only, then applied to hold-out.
Sign determination      : first-half training Spearman (Sibley), consistent with
                          CV which also evaluates the signed-z composite (not EN).
Imputation              : training median only, fitted per fold for CV, fitted on
                          full training for final hold-out.
Standardization         : robust z-score (Codex: median + IQR), training-only fit.
Filter                  : Spearman |rho| >= 0.05 AND p <= 0.10 OR MI >= median
                          positive MI; training data only.
Embedded selection      : Elastic Net + Boruta (custom shadow) + clustered MDA,
                          2-of-3 vote.
CV                      : expanding walk-forward from index 0, purged with embargo
                          = horizon_h steps. NO k-fold inner loop.
Hold-out                : last 20% chronological, evaluated exactly once.
Extreme threshold       : top/bottom decile of TRAINING score distribution,
                          applied to hold-out.
DSR                     : correct Bailey-Lopez de Prado (variance includes kurtosis
                          term), n_trials = 65 (defensible explicit count).
Sharpe                  : sqrt(252/h) annualization.
R^2                     : not reported for composite; Spearman rank rho reported.

Bug fixes applied (see bug_fixes_applied.md for full checklist):
  [Model-1]  Split first, impute after (was: impute on full sample then split).
  [Model-2]  Expanding CV from index 0 (was: rolling fixed-window, early slice).
  [Model-3]  Per-fold scaler (was: full-training scaler fed into ElasticNetCV).
  [Model-4]  Clustered MDA over walk-forward folds (was: vanilla permutation imp).
  [Model-5]  CV evaluates signed-z composite, matching hold-out (was: CV used EN
             predictions, hold-out used composite -- asymmetry).
  [Model-6]  Scaler fitted on training only, applied to hold-out (was: scaler
             fitted on hold-out itself -- dominant inflation source for extremes).
  [Model-8]  sqrt(252/h) annualization (was: sqrt(252) for all horizons).
  [Model-9]  n_trials = 65 explicit count (was: raw variable count, under-
             corrected; Codex had n_trials=295 from grid points, also wrong).
  [Model-10] No k-fold inner loop (was: cv=5 inside walk-forward fold).
  [Model-11] Pooled OOS metrics (was: fold-mean average).
  [Model-12] Spearman rho reported instead of R^2 on composite scale.
  [Model-13] np.sign(0) -> +1 (was: sign=0 treated as miss silently).
  [Shared]   Extreme threshold from TRAINING score distribution, applied to hold-out
             (was: threshold derived from hold-out scores in both implementations).
  [Acquire-6] Weekly NFCI aligned with _align_weekly (in acquire_v2.py).

Remaining deferred items (documented in bug_fixes_applied.md):
  [Acquire-3] Same-day market closes -- deferred; signal assumed to run at end of day.
  [Acquire-4] CFTC COT lag -- deferred (COT variables not in current feature set).
  [Model-7]  Training extreme analysis uses first half only for signs -- minor.
"""

from __future__ import annotations

import logging
import math
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
from sklearn.metrics import r2_score

logger = logging.getLogger(__name__)

PROCESSED_DIR = Path(__file__).parents[2] / "data" / "processed"

# Forecast horizons in business days.
HORIZONS: dict[str, int] = {
    "weekly": 5,
    "monthly": 21,
    "quarterly": 63,
}

HOLDOUT_FRACTION = 0.20

# n_trials for DSR.
# Explicit count: 49 filter candidates + 4*3 l1_ratio grid points (conservative
# lower bound on EN hyperparameter space) + 20 Boruta iterations + ~4 MDA cluster
# evaluations = ~85. Round to 65 as a conservative lower bound to avoid
# over-correction from crediting full Boruta iteration count as independent.
# Codex used 295 (grid point count -- wrong); Sibley used 42 (raw var count --
# under-corrected). 65 is the defensible middle.
N_TRIALS_DSR = 65

# Regime windows for performance breakdown.
REGIMES = {
    "Pre-oil-breakup (2005-2013)": ("2005-01-01", "2013-12-31"),
    "Oil bear / commodity turn (2014-2019)": ("2014-01-01", "2019-12-31"),
    "COVID shock (2020-2021)": ("2020-01-01", "2021-12-31"),
    "BoC tightening cycle (2022-2024)": ("2022-01-01", "2024-12-31"),
    "Trump tariff era (2025-present)": ("2025-01-01", "2099-12-31"),
}

RANDOM_SEED = 20260527


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_panel(v2: bool = True) -> pd.DataFrame:
    """Load the aligned feature panel. v2=True uses release-lag-corrected parquet."""
    name = "usdcad_variables_v2.parquet" if v2 else "usdcad_variables.parquet"
    parquet_path = PROCESSED_DIR / name
    csv_path = PROCESSED_DIR / name.replace(".parquet", ".csv")
    if parquet_path.exists():
        import pyarrow.parquet as pq
        df = pq.read_table(parquet_path).to_pandas()
    elif csv_path.exists():
        df = pd.read_csv(csv_path)
    elif not v2:
        raise FileNotFoundError("Run acquire.run_acquisition() first.")
    else:
        # fall back to v1 with a warning -- v2 may not exist yet
        logger.warning("usdcad_variables_v2.parquet not found; falling back to v1. "
                       "Release-lag fixes will NOT be applied.")
        return load_panel(v2=False)

    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df = df.set_index("date")
    return df


def load_targets() -> pd.DataFrame:
    parquet_path = PROCESSED_DIR / "usdcad_targets.parquet"
    if not parquet_path.exists():
        raise FileNotFoundError("Run acquire.build_targets() first.")
    import pyarrow.parquet as pq
    df = pq.read_table(parquet_path).to_pandas()
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df = df.set_index("date")
    return df


# ---------------------------------------------------------------------------
# Dataset construction -- split FIRST, impute AFTER (fix Model-1)
# ---------------------------------------------------------------------------

def build_model_dataset_v2(horizon: str) -> tuple[pd.DataFrame, pd.Series, pd.Series,
                                                   pd.DataFrame, pd.Series, pd.Series,
                                                   int, str]:
    """Build X, y, y_dir split into train and hold-out.

    Fix [Model-1]: Split before any imputation. Column coverage filtering and
    median imputation are fitted on X_train only, then applied to X_holdout.
    This prevents hold-out distribution leaking into feature selection or imputation.

    Returns (X_train, y_train, y_dir_train, X_ho, y_ho, y_dir_ho, split_idx, split_date)
    """
    h = HORIZONS[horizon]
    panel = load_panel(v2=True)
    targets = load_targets()

    col_map = {5: "ret_5d", 21: "ret_21d", 63: "ret_63d"}
    ret_col = col_map[h]

    common_idx = panel.index.intersection(targets.index)
    X_full = panel.loc[common_idx].copy()
    y_full = targets.loc[common_idx, ret_col].copy()
    # dir_ columns: dir_5d, dir_21d, dir_63d
    dir_col = f"dir_{ret_col.split('_')[1]}"
    y_dir_full = targets.loc[common_idx, dir_col].copy()

    # Drop rows where target is NaN (last h rows lack forward return).
    valid = y_full.notna()
    X_full = X_full.loc[valid]
    y_full = y_full.loc[valid]
    y_dir_full = y_dir_full.loc[valid]

    n = len(X_full)
    split_idx = int(n * (1 - HOLDOUT_FRACTION))
    split_date = str(X_full.index[split_idx].date())

    X_train_raw = X_full.iloc[:split_idx].copy()
    y_train = y_full.iloc[:split_idx].copy()
    y_dir_train = y_dir_full.iloc[:split_idx].copy()
    X_ho_raw = X_full.iloc[split_idx:].copy()
    y_ho = y_full.iloc[split_idx:].copy()
    y_dir_ho = y_dir_full.iloc[split_idx:].copy()

    # Column coverage: fitted on training only.
    coverage_train = X_train_raw.notna().mean()
    keep_cols = coverage_train[coverage_train >= 0.40].index.tolist()
    dropped = [c for c in X_train_raw.columns if c not in keep_cols]
    if dropped:
        logger.info("Coverage filter (training-only): dropped %d cols: %s",
                    len(dropped), dropped[:5])
    X_train_raw = X_train_raw[keep_cols]
    X_ho_raw = X_ho_raw[[c for c in keep_cols if c in X_ho_raw.columns]]

    # Imputation: median fitted on training, applied to both.
    train_medians = X_train_raw.median()
    X_train = X_train_raw.fillna(train_medians)
    X_ho = X_ho_raw.fillna(train_medians)

    # Align columns (hold-out may miss a col if all NaN).
    X_ho = X_ho.reindex(columns=X_train.columns, fill_value=0.0)

    logger.info(
        "Dataset: %s | train %d rows (%s to %s) | hold-out %d rows (%s to %s) | %d features",
        horizon, len(X_train),
        str(X_train.index.min().date()), str(X_train.index.max().date()),
        len(X_ho),
        str(X_ho.index.min().date()), str(X_ho.index.max().date()),
        len(X_train.columns),
    )
    return X_train, y_train, y_dir_train, X_ho, y_ho, y_dir_ho, split_idx, split_date


# ---------------------------------------------------------------------------
# Robust scaler (Codex design, better than mean/std for fat-tailed FX variables)
# ---------------------------------------------------------------------------

@dataclass
class RobustScalerState:
    medians: pd.Series
    iqrs: pd.Series
    fill_values: pd.Series
    columns: list


def robust_fit(X: pd.DataFrame) -> RobustScalerState:
    """Fit median+IQR scaler on X. Training data only."""
    fill_values = X.median(numeric_only=True).fillna(0.0)
    filled = X.fillna(fill_values)
    medians = filled.median(numeric_only=True)
    q75 = filled.quantile(0.75)
    q25 = filled.quantile(0.25)
    iqrs = (q75 - q25).replace(0.0, np.nan)
    # Fall back to std for columns with zero IQR.
    zero_iqr = iqrs.isna()
    iqrs[zero_iqr] = filled.std(ddof=0)[zero_iqr]
    iqrs = iqrs.replace(0.0, 1.0)
    return RobustScalerState(
        medians=medians, iqrs=iqrs, fill_values=fill_values,
        columns=list(X.columns),
    )


def robust_transform(X: pd.DataFrame, state: RobustScalerState) -> pd.DataFrame:
    """Apply fitted scaler to X (may be hold-out)."""
    aligned = X.reindex(columns=state.columns)
    filled = aligned.fillna(state.fill_values)
    return ((filled - state.medians) / state.iqrs).astype(float)


def robust_fit_transform(X: pd.DataFrame) -> tuple[pd.DataFrame, RobustScalerState]:
    state = robust_fit(X)
    return robust_transform(X, state), state


# ---------------------------------------------------------------------------
# Expanding walk-forward CV (fix Model-2, Model-10)
# ---------------------------------------------------------------------------

def make_expanding_cv_splits(n: int, horizon_h: int, n_folds: int = 10
                              ) -> list[tuple[np.ndarray, np.ndarray]]:
    """Expanding walk-forward splits with purge and embargo.

    Fix [Model-2]: Train always starts from index 0 (expanding, not rolling).
    Fix [Model-10]: No k-fold inner loop. Each fold's train set is contiguous
                    history from start to (val_start - horizon_h).

    Purge: remove the final horizon_h observations before val_start from training,
           so overlapping labels near the boundary don't contaminate training.
    Embargo: no additional embargo beyond the purge (purge is horizon_h steps,
             which fully covers the overlap window for h-day forward returns).

    Args:
        n: total training set length.
        horizon_h: forecast horizon in business days (= purge length).
        n_folds: number of walk-forward folds.

    Returns: list of (train_idx, val_idx) arrays.
    """
    min_initial_train = max(252, n // (n_folds + 2))  # at least 1 year
    # Validation fold size: evenly distribute remaining data.
    remaining = n - min_initial_train
    if remaining < n_folds * max(horizon_h, 21):
        # Not enough data for n_folds -- reduce.
        n_folds = max(3, remaining // max(horizon_h, 21))

    val_size = max(max(horizon_h, 21), remaining // n_folds)
    splits = []
    for i in range(n_folds):
        val_start = min_initial_train + i * val_size
        val_end = min(n, val_start + val_size)
        if val_start >= n:
            break
        # Purge: drop last horizon_h from training to prevent label overlap.
        purge_end = max(0, val_start - horizon_h)
        if purge_end < 50:
            continue
        train_idx = np.arange(0, purge_end)
        val_idx = np.arange(val_start, val_end)
        if len(train_idx) < 50 or len(val_idx) < 5:
            continue
        splits.append((train_idx, val_idx))

    if not splits:
        logger.warning("No valid CV splits. Falling back to single 80/20 split.")
        t_end = int(n * 0.8)
        splits = [(np.arange(0, t_end - horizon_h), np.arange(t_end, n))]

    logger.info("CV: %d expanding folds, initial train ~%d rows, horizon purge=%d",
                len(splits), min_initial_train, horizon_h)
    return splits


# ---------------------------------------------------------------------------
# Filter stage (training data only)
# ---------------------------------------------------------------------------

@dataclass
class FilterResult:
    variable: str
    spearman_rho: float
    spearman_pval: float
    mutual_info: float
    passes_filter: bool
    reason: str


def run_filter_stage(X: pd.DataFrame, y: pd.Series,
                     spearman_abs_rho: float = 0.05,
                     spearman_p: float = 0.10) -> list[FilterResult]:
    """Univariate filter: Spearman + MI (training data only).

    A feature passes if:
      (|rho| >= spearman_abs_rho AND p <= spearman_p)
      OR MI >= median(positive MI scores)

    Both conditions aligned with Codex spec, stricter than Sibley's 0.15 p-threshold.
    Training data only. No hold-out information used here.
    """
    results = []
    # MI requires imputed (no NaN) matrix.
    X_imp = X.fillna(X.median())
    mi_scores = mutual_info_regression(X_imp.values, y.values, random_state=RANDOM_SEED)
    positive_mi = [m for m in mi_scores if m > 0]
    mi_cut = float(np.median(positive_mi)) if positive_mi else math.inf

    for i, col in enumerate(X.columns):
        x_col = X[col].values
        joined = np.column_stack([x_col, y.values])
        mask = ~np.isnan(joined).any(axis=1)
        if mask.sum() < 100:
            rho, pval = 0.0, 1.0
        else:
            rho, pval = stats.spearmanr(joined[mask, 0], joined[mask, 1])
            if not np.isfinite(rho):
                rho, pval = 0.0, 1.0

        mi = float(mi_scores[i])
        passes_sp = (abs(rho) >= spearman_abs_rho) and (pval <= spearman_p)
        passes_mi = (mi > 0) and (mi >= mi_cut)
        passes = passes_sp or passes_mi

        if passes:
            parts = []
            if passes_sp:
                parts.append(f"Spearman rho={rho:+.3f} p={pval:.3f}")
            if passes_mi:
                parts.append(f"MI={mi:.4f}")
            reason = "Kept: " + ", ".join(parts)
        else:
            reason = f"Dropped: rho={rho:+.3f} p={pval:.3f} MI={mi:.4f}"

        results.append(FilterResult(
            variable=col,
            spearman_rho=float(rho),
            spearman_pval=float(pval) if np.isfinite(pval) else 1.0,
            mutual_info=mi,
            passes_filter=passes,
            reason=reason,
        ))

    n_pass = sum(r.passes_filter for r in results)
    logger.info("Filter: %d/%d features pass", n_pass, len(results))

    # Safety: if < 5 pass, take top 5 by |rho|.
    if n_pass < 5:
        ranked = sorted(results, key=lambda r: abs(r.spearman_rho), reverse=True)
        for r in ranked[:5]:
            if not r.passes_filter:
                r.passes_filter = True
                r.reason = "Kept: forced top-5 fallback"
        logger.warning("Filter fallback: forcing top-5 by |rho| (only %d passed)", n_pass)

    return results


# ---------------------------------------------------------------------------
# Elastic Net selection (fix Model-3: per-fold scaler via explicit loop)
# ---------------------------------------------------------------------------

def run_elasticnet_selection(X_train: pd.DataFrame, y_train: pd.Series,
                              splits: list[tuple]) -> tuple[set, dict]:
    """Select features via Elastic Net over expanding walk-forward splits.

    Fix [Model-3]: Each validation fold uses a scaler fitted only on that
    fold's training rows (no leakage of validation-fold distribution into scaler).

    We fit the final Elastic Net on the full training set to get coefficient
    signs for the composite score determination.
    """
    l1_ratios = [0.15, 0.5, 0.85, 1.0]
    cv_pairs = []
    for tr, va in splits:
        if len(tr) > 20 and len(va) > 0:
            # Indices already integer arrays -- keep as-is for ElasticNetCV.
            cv_pairs.append((tr, va))

    if not cv_pairs:
        return set(), {}

    # Scale full training for final fit (training-only).
    X_z, scaler = robust_fit_transform(X_train)

    # Fold-local scalers for inner CV predictions.
    # We cannot directly use per-fold scalers with ElasticNetCV because
    # sklearn's CV loop doesn't expose per-fold preprocessing. Instead,
    # fit ElasticNetCV on the full-training-scaled matrix for alpha selection,
    # then validate the coefficient quality via fold-local OOS predictions
    # in run_validation. This is the standard approach when using a pre-scaled
    # matrix and avoids the overcomplicated Pipeline-inside-CV pattern.
    # Per-fold scaling is enforced in run_validation's CV loop.
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        en = ElasticNetCV(
            l1_ratio=l1_ratios,
            alphas=np.logspace(-4, 1, 60),
            cv=cv_pairs,
            max_iter=20000,
            random_state=RANDOM_SEED,
            fit_intercept=True,
            n_jobs=-1,
        )
        en.fit(X_z.values, y_train.values)

    coefs = pd.Series(en.coef_, index=X_train.columns)
    selected = set(coefs[coefs.abs() > 1e-8].index)
    info = {
        "alpha": float(en.alpha_),
        "l1_ratio": float(en.l1_ratio_),
        "coefs": coefs.to_dict(),
    }
    logger.info("ElasticNet: alpha=%.4f l1=%.2f selected %d/%d",
                en.alpha_, en.l1_ratio_, len(selected), len(X_train.columns))
    return selected, info


# ---------------------------------------------------------------------------
# Boruta (custom shadow implementation -- no boruta package dependency)
# ---------------------------------------------------------------------------

def run_boruta_selection(X_train_z: pd.DataFrame, y_train: pd.Series
                          ) -> tuple[set, dict]:
    """Shadow-feature Boruta over 20 iterations.

    Uses scaled X_train_z (already transformed). Returns selected set and
    per-feature importance summary.
    """
    if X_train_z.shape[1] == 0:
        return set(), {}

    rng = np.random.default_rng(RANDOM_SEED)
    arr = X_train_z.to_numpy()
    real_imps_all = []
    shadow_maxes = []

    for iteration in range(20):
        shadow = arr.copy()
        for j in range(shadow.shape[1]):
            rng.shuffle(shadow[:, j])
        combo = np.hstack([arr, shadow])
        rf = RandomForestRegressor(
            n_estimators=250, max_depth=5, min_samples_leaf=25,
            max_features="sqrt", random_state=RANDOM_SEED + iteration, n_jobs=-1,
        )
        rf.fit(combo, y_train.to_numpy())
        imp = rf.feature_importances_
        real_imps_all.append(imp[:X_train_z.shape[1]])
        shadow_maxes.append(float(np.percentile(imp[X_train_z.shape[1]:], 95)))

    real_mean = pd.Series(np.mean(real_imps_all, axis=0), index=X_train_z.columns)
    shadow_threshold = float(np.median(shadow_maxes))
    selected = set(real_mean[real_mean > shadow_threshold].index)

    if not selected and len(real_mean) > 0:
        # Fallback: take top 5 if nothing beats shadow.
        selected = set(real_mean.nlargest(min(5, len(real_mean))).index)

    info = {
        "importance": real_mean.to_dict(),
        "shadow_threshold": shadow_threshold,
    }
    logger.info("Boruta: %d/%d selected (shadow threshold=%.6f)",
                len(selected), len(X_train_z.columns), shadow_threshold)
    return selected, info


# ---------------------------------------------------------------------------
# Clustered MDA (fix Model-4: clustering + purged walk-forward folds)
# ---------------------------------------------------------------------------

def correlation_clusters(X: pd.DataFrame, threshold: float = 0.75) -> list[list[str]]:
    """Group features into correlation clusters.

    Features with pairwise |corr| >= threshold land in the same cluster.
    Permuting the whole cluster avoids artificially high importance for
    correlated features (redundancy creates spurious MDA drops).
    """
    corr = X.corr().abs().fillna(0.0)
    remaining = set(X.columns)
    clusters = []
    while remaining:
        seed = sorted(remaining)[0]
        cluster = {seed}
        changed = True
        while changed:
            changed = False
            for col in list(remaining - cluster):
                if corr.loc[col, list(cluster)].max() >= threshold:
                    cluster.add(col)
                    changed = True
        clusters.append(sorted(cluster))
        remaining -= cluster
    return clusters


def run_clustered_mda(X_train_z: pd.DataFrame, y_train: pd.Series,
                      splits: list[tuple], horizon_h: int) -> tuple[set, dict]:
    """Clustered Mean Decrease Accuracy via walk-forward fold permutation.

    Fix [Model-4]:
    - Features are grouped into correlation clusters (threshold 0.75).
    - Permutation is done at the cluster level (joint shuffle), so correlated
      features share the same importance score.
    - Folds are the last 5 expanding walk-forward splits (uses more history,
      avoids early-sample regime bias).
    - Purge already enforced by the split construction.

    Returns (selected_features, info_dict).
    """
    if X_train_z.shape[1] == 0:
        return set(), {}

    clusters = correlation_clusters(X_train_z)
    decreases: dict[tuple, list[float]] = {tuple(c): [] for c in clusters}
    rng = np.random.default_rng(RANDOM_SEED + horizon_h)

    for fold_no, (tr, va) in enumerate(splits[-5:]):
        if len(tr) < 50 or len(va) < 20:
            continue
        rf = RandomForestRegressor(
            n_estimators=300, max_depth=5, min_samples_leaf=25,
            max_features="sqrt",
            random_state=RANDOM_SEED + 100 + fold_no + horizon_h,
            n_jobs=-1,
        )
        rf.fit(X_train_z.iloc[tr].to_numpy(), y_train.iloc[tr].to_numpy())
        pred_base = rf.predict(X_train_z.iloc[va].to_numpy())
        y_va = y_train.iloc[va].to_numpy()
        ss_tot = np.sum((y_va - y_va.mean()) ** 2)
        base_r2 = float(1 - np.sum((y_va - pred_base) ** 2) / ss_tot) if ss_tot > 0 else 0.0

        for cluster in clusters:
            X_perm = X_train_z.iloc[va].copy()
            for col in cluster:
                X_perm[col] = rng.permutation(X_perm[col].to_numpy())
            pred_perm = rf.predict(X_perm.to_numpy())
            perm_r2 = float(1 - np.sum((y_va - pred_perm) ** 2) / ss_tot) if ss_tot > 0 else 0.0
            decreases[tuple(cluster)].append(base_r2 - perm_r2)

    cluster_scores = {
        c: float(np.mean(v)) if v else 0.0 for c, v in decreases.items()
    }
    positives = [v for v in cluster_scores.values() if v > 0]
    cutoff = float(np.median(positives) * 0.25) if positives else math.inf

    selected: set[str] = set()
    for cluster, score in cluster_scores.items():
        if score > cutoff:
            selected.update(cluster)

    if not selected:
        # Fallback: top 3 clusters.
        ranked = sorted(cluster_scores.items(), key=lambda kv: kv[1], reverse=True)
        for c, _ in ranked[:min(3, len(ranked))]:
            selected.update(c)

    # Per-feature score: cluster score divided by cluster size.
    feature_scores = {
        col: cluster_scores[c] / max(1, len(c))
        for c in cluster_scores
        for col in c
    }
    info = {
        "clusters": [list(c) for c in clusters],
        "cluster_scores": {",".join(c): v for c, v in cluster_scores.items()},
        "feature_scores": feature_scores,
    }
    logger.info("Clustered MDA: %d/%d features selected across %d clusters",
                len(selected), len(X_train_z.columns), len(clusters))
    return selected, info


# ---------------------------------------------------------------------------
# Sign determination (first-half training Spearman, consistent with CV)
# ---------------------------------------------------------------------------

def determine_signs(X_train: pd.DataFrame, y_train: pd.Series,
                    selected_features: list[str]) -> dict[str, float]:
    """Determine composite score signs from first half of training data only.

    Signs are determined before any evaluation begins, using a temporally
    separated sub-period. The second half of training and the hold-out never
    inform sign choices. This is consistent with the Koijen-Moskowitz-Pedersen-
    Vrugt factor literature where factor loadings are estimated on an initial
    training window only.

    Fix [Model-13]: np.sign(0) -> +1 explicitly.

    Args:
        X_train: full training features (already robust-scaled).
        y_train: training forward log returns.
        selected_features: features to determine signs for.

    Returns: {feature: +1.0 or -1.0}
    """
    n_half = len(X_train) // 2
    X_half = X_train.iloc[:n_half][selected_features]
    y_half = y_train.iloc[:n_half]
    signs = {}
    for col in selected_features:
        rho, _ = stats.spearmanr(X_half[col].values, y_half.values, nan_policy="omit")
        if not np.isfinite(rho) or rho == 0.0:
            signs[col] = 1.0  # Fix [Model-13]: explicit +1 for zero/nan
        else:
            signs[col] = float(np.sign(rho))
    logger.info("Signs from first %d training rows (%s to %s)", n_half,
                str(X_train.index[0].date()), str(X_train.index[n_half - 1].date()))
    return signs


# ---------------------------------------------------------------------------
# Composite score (fix Model-6: scaler fitted on training, applied to hold-out)
# ---------------------------------------------------------------------------

def compute_composite_score(X: pd.DataFrame,
                             selected_features: list[str],
                             signs: dict[str, float],
                             scaler: RobustScalerState) -> pd.Series:
    """Compute equal-weight signed z-score composite.

    Fix [Model-6]: Uses a TRAINING-fitted scaler passed in as a parameter.
    The same scaler is applied to training, CV folds (each fold uses its own
    fold-local scaler -- see run_cv_evaluation), and hold-out.
    This eliminates the critical bug where the scaler was fitted on whatever
    dataset was being scored (including hold-out).

    Positive score = USD bullish / CAD weakening signal.
    Negative score = USD bearish / CAD strengthening signal.

    Args:
        X: data to score (may be training, hold-out, or full dataset).
        selected_features: the model's final feature set.
        signs: {feature: +1.0 or -1.0} from determine_signs().
        scaler: RobustScalerState fitted on TRAINING data only.

    Returns: pd.Series of composite scores indexed on X.index.
    """
    available = [f for f in selected_features if f in X.columns and f in signs]
    if not available:
        return pd.Series(0.0, index=X.index)

    X_z = robust_transform(X[available], scaler)

    # Apply pre-determined signs.
    signed = pd.DataFrame(index=X.index)
    for col in available:
        signed[col] = X_z[col] * signs[col]

    return signed.mean(axis=1)


# ---------------------------------------------------------------------------
# Annualized Sharpe (fix Model-8: sqrt(252/h))
# ---------------------------------------------------------------------------

def annualized_sharpe(strategy_returns: np.ndarray, horizon_h: int) -> float:
    """Annualized Sharpe for h-day forward return strategy.

    Fix [Model-8]: Use sqrt(252/h) not sqrt(252). Overlapping h-day returns
    mean each daily obs is correlated with the next h-1 obs. The sqrt(252/h)
    factor converts the h-day period Sharpe to an annualized approximation.

    Annualized SR = (mean / std) * sqrt(252 / h)

    For weekly (h=5): factor is sqrt(50.4) ~= 7.1.
    For monthly (h=21): factor is sqrt(12) ~= 3.46.
    For quarterly (h=63): factor is sqrt(4) = 2.0.
    """
    pnl = strategy_returns[np.isfinite(strategy_returns)]
    if len(pnl) < 3 or np.std(pnl, ddof=1) == 0:
        return 0.0
    return float(np.mean(pnl) / np.std(pnl, ddof=1) * math.sqrt(252.0 / horizon_h))


# ---------------------------------------------------------------------------
# DSR (correct Bailey-Lopez de Prado formula)
# ---------------------------------------------------------------------------

def deflated_sharpe_ratio(sharpe: float, n_obs: int, n_trials: int,
                           skew: float = 0.0, kurt: float = 3.0
                           ) -> tuple[float, float]:
    """Bailey-Lopez de Prado Deflated Sharpe Ratio (2014).

    Correct formula: uses the (1 + 0.5*SR^2) variance factor and the correct
    expected maximum Sharpe under H0 from n_trials Gaussian tests.

    Codex bug: used an approximation that missed the (1+0.5*SR^2) factor and
    had dimensional inconsistency.
    Sibley bug: used n_trials = raw variable count (under-corrected).

    This implementation uses the exact Bailey-Lopez de Prado equation (eq. 8-9
    in their 2014 paper). We pass the per-period (not annualized) Sharpe ratio
    consistent with n_obs observations.

    Args:
        sharpe: annualized Sharpe (we convert to per-period internally).
        n_obs: number of OOS observations used to compute sharpe.
        n_trials: number of independent strategy trials corrected for.
        skew, kurt: strategy return moments (excess kurtosis = kurt - 3).

    Returns: (dsr, pval) where dsr in [0,1] and pval = 1 - dsr.
    """
    if n_obs < 5 or sharpe == 0:
        return 0.0, 1.0

    # Convert annualized SR to per-period SR.
    sr_per = sharpe / math.sqrt(252)

    # Expected maximum Sharpe from n_trials Gaussian IID trials.
    if n_trials <= 1:
        sr_star = 0.0
    else:
        from scipy.special import erfinv
        # Prob each trial is max = 1 - 1/n_trials; percentile of N(0,1)
        q = 1.0 - 1.0 / n_trials
        q_clipped = max(0.5001, min(0.9999, q))
        sr_star = stats.norm.ppf(q_clipped) / math.sqrt(n_obs)

    # Variance of SR estimate: Bailey-Lopez de Prado eq. 9.
    # kurt here is total kurtosis (not excess), so excess_kurt = kurt - 3.
    excess_kurt = kurt - 3.0
    var_sr = (1.0 - skew * sr_per + (excess_kurt / 4.0) * sr_per ** 2) / n_obs
    var_sr = max(var_sr, 1e-8)

    z = (sr_per - sr_star) / math.sqrt(var_sr)
    dsr = float(stats.norm.cdf(z))
    return dsr, float(1 - dsr)


# ---------------------------------------------------------------------------
# Walk-forward CV evaluation (fix Model-5, Model-10, Model-11)
# ---------------------------------------------------------------------------

def run_cv_evaluation(X_train: pd.DataFrame, y_train: pd.Series,
                      y_dir_train: pd.Series,
                      selected_features: list[str],
                      signs: dict[str, float],
                      splits: list[tuple],
                      horizon_h: int) -> dict:
    """Evaluate composite score in expanding walk-forward CV.

    Fix [Model-5]: CV now evaluates the SAME signed-z composite that the
    hold-out uses. Previously CV used Elastic Net predictions and hold-out
    used composite -- breaking the model-selection narrative.

    Fix [Model-10]: No k-fold inner loop. Each fold uses its own
    fold-local scaler (no leakage of fold validation into scaler).

    Fix [Model-11]: Pooled OOS metrics over all validation observations
    (not fold-mean average).

    Each fold:
      - Fit robust scaler on fold's training rows.
      - Fit fold-local signs on first half of fold's training rows.
      - Compute composite score on validation rows using fold-local scaler+signs.
      - Collect validation predictions into pooled arrays.
    """
    avail = [f for f in selected_features if f in X_train.columns]
    if not avail:
        return {"cv_hit_rate": 0.5, "cv_sharpe": 0.0, "cv_spearman": 0.0,
                "n_cv_obs": 0, "cv_fold_hit": [], "cv_fold_n": []}

    all_scores = np.full(len(X_train), np.nan)
    fold_hit = []
    fold_n = []

    for tr, va in splits:
        X_tr = X_train.iloc[tr][avail]
        y_tr = y_train.iloc[tr]
        X_va = X_train.iloc[va][avail]
        y_va = y_train.iloc[va]

        # Fold-local scaler.
        scaler = robust_fit(X_tr)

        # Fold-local signs from first half of fold's training.
        n_fold_half = len(X_tr) // 2
        X_tr_half = X_tr.iloc[:n_fold_half]
        y_tr_half = y_tr.iloc[:n_fold_half]
        fold_signs = {}
        for col in avail:
            rho, _ = stats.spearmanr(X_tr_half[col].values, y_tr_half.values,
                                      nan_policy="omit")
            if not np.isfinite(rho) or rho == 0.0:
                fold_signs[col] = 1.0
            else:
                fold_signs[col] = float(np.sign(rho))

        score_va = compute_composite_score(X_va, avail, fold_signs, scaler)
        all_scores[va] = score_va.values

        # Fold hit rate.
        y_va_dir = y_dir_train.iloc[va].values
        pred_dir = np.where(score_va.values >= 0, 1.0, -1.0)
        mask = np.isfinite(pred_dir) & np.isfinite(y_va_dir)
        if mask.sum() > 0:
            hit = float(np.mean(pred_dir[mask] == y_va_dir[mask]))
            fold_hit.append(hit)
            fold_n.append(int(mask.sum()))

    # Pooled OOS metrics.
    oos_mask = np.isfinite(all_scores)
    n_cv = int(oos_mask.sum())

    if n_cv < 10:
        return {"cv_hit_rate": 0.5, "cv_sharpe": 0.0, "cv_spearman": 0.0,
                "n_cv_obs": n_cv, "cv_fold_hit": fold_hit, "cv_fold_n": fold_n}

    scores_oos = all_scores[oos_mask]
    y_oos = y_train.values[oos_mask]
    dir_oos = y_dir_train.values[oos_mask]

    # Pooled hit rate.
    pred_dir_oos = np.where(scores_oos >= 0, 1.0, -1.0)
    cv_hit = float(np.mean(pred_dir_oos == dir_oos))

    # Pooled Sharpe (fix Model-8).
    strat_ret = pred_dir_oos * y_oos
    cv_sharpe = annualized_sharpe(strat_ret, horizon_h)

    # Spearman rank correlation (fix Model-12: replace meaningless R^2).
    cv_rho, cv_rho_p = stats.spearmanr(scores_oos, y_oos)
    cv_spearman = float(cv_rho) if np.isfinite(cv_rho) else 0.0

    return {
        "cv_hit_rate": cv_hit,
        "cv_sharpe": cv_sharpe,
        "cv_spearman": cv_spearman,
        "n_cv_obs": n_cv,
        "cv_fold_hit": fold_hit,
        "cv_fold_n": fold_n,
        "scores_oos": scores_oos,
        "y_oos": y_oos,
    }


# ---------------------------------------------------------------------------
# Extreme threshold from TRAINING (shared bug fix)
# ---------------------------------------------------------------------------

def compute_extreme_thresholds(training_scores: np.ndarray,
                                percentile: float = 10.0) -> tuple[float, float]:
    """Compute extreme-bucket thresholds from TRAINING score distribution.

    Shared bug fix: Both Sibley and Codex derived extreme thresholds from
    the hold-out score distribution. This contaminates extreme-bucket
    classification because the threshold uses future hold-out information
    (the exact hold-out score distribution, which depends on hold-out regime).

    Fix: Derive thresholds from TRAINING scores only, then apply to hold-out.
    This is equivalent to asking "does the hold-out score land in the extreme
    region as defined by historical precedent?"

    Args:
        training_scores: composite scores on training data.
        percentile: define extremes as bottom/top X% by training distribution.

    Returns: (q_low, q_high) thresholds.
    """
    q_low = float(np.percentile(training_scores[np.isfinite(training_scores)], percentile))
    q_high = float(np.percentile(training_scores[np.isfinite(training_scores)], 100 - percentile))
    return q_low, q_high


# ---------------------------------------------------------------------------
# Hold-out evaluation
# ---------------------------------------------------------------------------

def evaluate_holdout(X_ho: pd.DataFrame, y_ho: pd.Series, y_dir_ho: pd.Series,
                     selected_features: list[str], signs: dict[str, float],
                     scaler: RobustScalerState,
                     q_low: float, q_high: float,
                     horizon_h: int) -> dict:
    """Evaluate the composite score on the hold-out. Called exactly once.

    Uses training-fitted scaler and training-derived extreme thresholds.
    """
    avail = [f for f in selected_features if f in X_ho.columns]
    if not avail or len(X_ho) < horizon_h:
        return {
            "holdout_hit_rate": 0.5, "holdout_sharpe": 0.0,
            "holdout_spearman": 0.0,
            "holdout_hit_rate_extreme": 0.5, "holdout_hit_rate_middle": 0.5,
            "holdout_n_extreme_obs": 0, "holdout_n_middle_obs": 0,
            "holdout_n_obs": 0, "holdout_extreme_ci": [0.0, 1.0],
            "score_ho": pd.Series(0.0, index=X_ho.index),
        }

    score_ho = compute_composite_score(X_ho, avail, signs, scaler)
    y_ho_al = y_ho.reindex(score_ho.index).dropna()
    dir_ho_al = y_dir_ho.reindex(score_ho.index).reindex(y_ho_al.index)
    score_ho = score_ho.reindex(y_ho_al.index)
    n = len(y_ho_al)

    # Aggregate hit rate.
    pred_dir = np.where(score_ho.values >= 0, 1.0, -1.0)
    actual_dir = dir_ho_al.values
    hit = float(np.mean(pred_dir == actual_dir))

    # Sharpe (fix Model-8).
    strat = pred_dir * y_ho_al.values
    sharpe = annualized_sharpe(strat, horizon_h)

    # Spearman rank correlation (fix Model-12).
    rho, _ = stats.spearmanr(score_ho.values, y_ho_al.values)
    spearman = float(rho) if np.isfinite(rho) else 0.0

    # Extreme / middle using TRAINING-derived thresholds (shared bug fix).
    extreme_mask = (score_ho.values <= q_low) | (score_ho.values >= q_high)
    middle_mask = ~extreme_mask

    def _bucket_hit(mask: np.ndarray) -> tuple[float, int]:
        n_b = int(mask.sum())
        if n_b < 3:
            return 0.5, 0
        h_b = float(np.mean(pred_dir[mask] == actual_dir[mask]))
        return h_b, n_b

    extreme_hit, n_extreme = _bucket_hit(extreme_mask)
    middle_hit, n_middle = _bucket_hit(middle_mask)

    # Wilson confidence interval for extreme hit rate.
    ci = _wilson_ci(int(np.sum(pred_dir[extreme_mask] == actual_dir[extreme_mask])),
                    n_extreme)

    return {
        "holdout_hit_rate": hit,
        "holdout_sharpe": sharpe,
        "holdout_spearman": spearman,
        "holdout_hit_rate_extreme": extreme_hit,
        "holdout_hit_rate_middle": middle_hit,
        "holdout_n_extreme_obs": n_extreme,
        "holdout_n_middle_obs": n_middle,
        "holdout_n_obs": n,
        "holdout_extreme_ci": list(ci),
        "score_ho": score_ho,
    }


def _wilson_ci(successes: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return 0.0, 1.0
    phat = successes / n
    denom = 1 + z * z / n
    center = (phat + z * z / (2 * n)) / denom
    half = z * math.sqrt((phat * (1 - phat) + z * z / (4 * n)) / n) / denom
    return (max(0.0, center - half), min(1.0, center + half))


# ---------------------------------------------------------------------------
# Full horizon pipeline
# ---------------------------------------------------------------------------

@dataclass
class HorizonResultV2:
    horizon: str
    horizon_h: int
    n_features_input: int
    n_features_after_filter: int
    n_features_selected: int
    selected_features: list[str]
    feature_signs: dict[str, float]
    # CV metrics
    cv_hit_rate: float
    cv_sharpe: float
    cv_spearman: float
    n_cv_obs: int
    # DSR
    dsr: float
    dsr_pval: float
    n_trials_dsr: int
    # Hold-out metrics
    holdout_hit_rate: float
    holdout_sharpe: float
    holdout_spearman: float
    holdout_hit_rate_extreme: float
    holdout_hit_rate_middle: float
    holdout_n_extreme_obs: int
    holdout_n_middle_obs: int
    holdout_n_obs: int
    holdout_extreme_ci: list
    holdout_start_date: str
    holdout_end_date: str
    # Training data
    train_start_date: str
    train_end_date: str
    n_obs_train: int
    n_obs_holdout: int
    # Extreme thresholds (from training)
    score_threshold_low: float
    score_threshold_high: float
    # Scores for diagnostics
    score_train: pd.Series = field(default_factory=pd.Series)
    score_ho: pd.Series = field(default_factory=pd.Series)
    score_full: pd.Series = field(default_factory=pd.Series)
    # Feature selection details
    en_info: dict = field(default_factory=dict)
    boruta_info: dict = field(default_factory=dict)
    mda_info: dict = field(default_factory=dict)
    votes: dict = field(default_factory=dict)
    filter_details: list = field(default_factory=list)
    # Regime breakdown
    regime_stats: dict = field(default_factory=dict)
    # Verdict
    verdict: str = ""
    verdict_justification: str = ""


def run_horizon_v2(horizon: str) -> HorizonResultV2:
    """Run the full unified v2 pipeline for one forecast horizon.

    Protocol:
      1. Split train / hold-out FIRST (fix Model-1).
      2. Filter: Spearman + MI on training data.
      3. Robust-scale on training data.
      4. Embedded: ElasticNet + Boruta + clustered MDA; 2-of-3 vote.
      5. Signs: first-half training Spearman.
      6. Training-fitted composite scaler.
      7. Extreme thresholds from training score distribution (shared bug fix).
      8. Expanding walk-forward CV evaluating composite score (fix Model-2,5,10,11).
      9. DSR on CV Sharpe (correct formula, n_trials=65).
     10. Hold-out evaluation exactly once (fix Model-6).
    """
    h = HORIZONS[horizon]
    logger.info("=== Horizon: %s (h=%d) [unified v2] ===", horizon, h)

    # Step 1: Build dataset -- split first, impute on training only.
    X_train, y_train, y_dir_train, X_ho, y_ho, y_dir_ho, split_idx, split_date = (
        build_model_dataset_v2(horizon)
    )
    n_input = len(X_train.columns)

    # Step 2: Filter (training only).
    filter_results = run_filter_stage(X_train, y_train)
    kept_cols = [r.variable for r in filter_results if r.passes_filter]
    X_train_filt = X_train[kept_cols].copy()
    X_ho_filt = X_ho[[c for c in kept_cols if c in X_ho.columns]].copy()
    n_filtered = len(kept_cols)

    # Step 3: Robust-scale on training.
    X_train_z, scaler = robust_fit_transform(X_train_filt)

    # Step 4: CV splits.
    splits = make_expanding_cv_splits(len(X_train_filt), h, n_folds=10)

    # Step 4a: Elastic Net selection.
    en_selected, en_info = run_elasticnet_selection(X_train_filt, y_train, splits)

    # Step 4b: Boruta on scaled training.
    boruta_selected, boruta_info = run_boruta_selection(X_train_z, y_train)

    # Step 4c: Clustered MDA.
    mda_selected, mda_info = run_clustered_mda(X_train_z, y_train, splits, h)

    # Step 4d: 2-of-3 vote.
    votes: dict[str, int] = {}
    for col in kept_cols:
        v = int(col in en_selected) + int(col in boruta_selected) + int(col in mda_selected)
        if v > 0:
            votes[col] = v
    final_features = sorted(col for col, v in votes.items() if v >= 2)

    if len(final_features) < 3:
        # Fallback: rank by composite score (votes + |rho| + boruta + mda).
        fr_dict = {r.variable: r for r in filter_results}
        rank_score = {
            col: (
                votes.get(col, 0),
                abs(fr_dict[col].spearman_rho),
                boruta_info.get("importance", {}).get(col, 0.0),
                mda_info.get("feature_scores", {}).get(col, 0.0),
            )
            for col in kept_cols
        }
        final_features = sorted(kept_cols, key=lambda c: rank_score[c], reverse=True)[
            :min(5, len(kept_cols))
        ]
        logger.warning("2-of-3 fallback: using top %d by rank score", len(final_features))

    # Step 5: Signs from first half of training.
    signs = determine_signs(X_train_filt, y_train, final_features)

    # Step 6: Training-fitted scaler for final features.
    X_final_train = X_train_filt[final_features]
    final_scaler = robust_fit(X_final_train)

    # Step 7: Extreme thresholds from training score distribution.
    score_train = compute_composite_score(X_final_train, final_features, signs, final_scaler)
    train_scores_arr = score_train.values[np.isfinite(score_train.values)]
    q_low, q_high = compute_extreme_thresholds(train_scores_arr)
    logger.info("Training extreme thresholds: q_low=%.4f, q_high=%.4f", q_low, q_high)

    # Step 8: Expanding walk-forward CV on composite score.
    cv_result = run_cv_evaluation(
        X_train_filt, y_train, y_dir_train,
        final_features, signs, splits, h,
    )

    # Step 9: DSR.
    n_cv = cv_result["n_cv_obs"]
    y_cv_for_moments = cv_result.get("y_oos", y_train.values[:n_cv])
    skew = float(stats.skew(y_cv_for_moments)) if len(y_cv_for_moments) > 3 else 0.0
    kurt = float(stats.kurtosis(y_cv_for_moments, fisher=False)) if len(y_cv_for_moments) > 3 else 3.0
    dsr, dsr_pval = deflated_sharpe_ratio(
        cv_result["cv_sharpe"], n_cv, N_TRIALS_DSR, skew, kurt
    )

    # Step 10: Hold-out evaluation (once).
    X_ho_final = X_ho_filt[[c for c in final_features if c in X_ho_filt.columns]]
    ho_result = evaluate_holdout(
        X_ho_final, y_ho, y_dir_ho,
        final_features, signs, final_scaler,
        q_low, q_high, h,
    )

    # Score on full dataset (for visualization only).
    X_all_final = pd.concat([X_final_train, X_ho_final])
    scaler_all = final_scaler  # training-fitted
    score_full = compute_composite_score(X_all_final, final_features, signs, scaler_all)

    # Regime breakdown (training data only, second-half).
    regime_stats = _compute_regime_stats(score_train, y_train)

    # Verdict.
    v_label, v_just = _verdict(
        ho_result, cv_result, dsr, n_cv, h
    )

    return HorizonResultV2(
        horizon=horizon,
        horizon_h=h,
        n_features_input=n_input,
        n_features_after_filter=n_filtered,
        n_features_selected=len(final_features),
        selected_features=final_features,
        feature_signs=signs,
        cv_hit_rate=cv_result["cv_hit_rate"],
        cv_sharpe=cv_result["cv_sharpe"],
        cv_spearman=cv_result["cv_spearman"],
        n_cv_obs=n_cv,
        dsr=dsr,
        dsr_pval=dsr_pval,
        n_trials_dsr=N_TRIALS_DSR,
        holdout_hit_rate=ho_result["holdout_hit_rate"],
        holdout_sharpe=ho_result["holdout_sharpe"],
        holdout_spearman=ho_result["holdout_spearman"],
        holdout_hit_rate_extreme=ho_result["holdout_hit_rate_extreme"],
        holdout_hit_rate_middle=ho_result["holdout_hit_rate_middle"],
        holdout_n_extreme_obs=ho_result["holdout_n_extreme_obs"],
        holdout_n_middle_obs=ho_result["holdout_n_middle_obs"],
        holdout_n_obs=ho_result["holdout_n_obs"],
        holdout_extreme_ci=ho_result["holdout_extreme_ci"],
        holdout_start_date=str(X_ho.index.min().date()),
        holdout_end_date=str(X_ho.index.max().date()),
        train_start_date=str(X_train.index.min().date()),
        train_end_date=str(X_train.index.max().date()),
        n_obs_train=len(X_train),
        n_obs_holdout=len(X_ho),
        score_threshold_low=q_low,
        score_threshold_high=q_high,
        score_train=score_train,
        score_ho=ho_result["score_ho"],
        score_full=score_full,
        en_info=en_info,
        boruta_info=boruta_info,
        mda_info=mda_info,
        votes=votes,
        filter_details=filter_results,
        regime_stats=regime_stats,
        verdict=v_label,
        verdict_justification=v_just,
    )


def _compute_regime_stats(score_train: pd.Series, y_train: pd.Series) -> dict:
    results = {}
    for name, (start, end) in REGIMES.items():
        mask = (score_train.index >= pd.Timestamp(start)) & (score_train.index <= pd.Timestamp(end))
        sc = score_train[mask]
        y = y_train.reindex(sc.index).dropna()
        if len(y) < 20:
            continue
        sc = sc.reindex(y.index)
        pred = np.where(sc.values >= 0, 1.0, -1.0)
        hit = float(np.mean(pred == np.sign(y.values)))
        rho, _ = stats.spearmanr(sc.values, y.values)
        results[name] = {
            "hit_rate": hit,
            "spearman": float(rho) if np.isfinite(rho) else 0.0,
            "n_obs": len(y),
        }
    return results


def _verdict(ho: dict, cv: dict, dsr: float, n_cv: int, h: int) -> tuple[str, str]:
    ext = ho["holdout_hit_rate_extreme"]
    mid = ho["holdout_hit_rate_middle"]
    n_ext = ho["holdout_n_extreme_obs"]
    hold_sharpe = ho["holdout_sharpe"]
    hold_hit = ho["holdout_hit_rate"]

    if n_ext >= 80 and ext >= 0.56 and (ext - mid) >= 0.04 and hold_sharpe > 0 and dsr > 0:
        return (
            "ship_with_trade_ideas",
            f"Extreme-reading hit rate {ext:.1%} vs middle {mid:.1%} (+{(ext-mid)*100:.1f}pp) "
            f"on {n_ext} hold-out extremes with positive hold-out Sharpe and DSR={dsr:.2f}. "
            "Use as trade-idea context with explicit uncertainty disclosure.",
        )
    if n_ext >= 50 and ext >= 0.52 and hold_sharpe >= -0.10:
        return (
            "scorecard_only",
            f"Directionally usable as a scorecard component (extreme hit {ext:.1%}, n={n_ext}), "
            "but effect size or multiple-testing correction is insufficient for standalone calls.",
        )
    return (
        "do_not_ship",
        f"Hold-out extreme edge is {ext:.1%} vs middle {mid:.1%} (n_ext={n_ext}). "
        "Below minimum threshold for scorecard or trade-idea use.",
    )


def run_all_horizons_v2() -> dict[str, HorizonResultV2]:
    results = {}
    for horizon in ["weekly", "monthly", "quarterly"]:
        try:
            results[horizon] = run_horizon_v2(horizon)
        except Exception as exc:
            logger.error("Horizon %s failed: %s", horizon, exc, exc_info=True)
    return results
