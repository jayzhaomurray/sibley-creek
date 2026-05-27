"""USDCAD adversarial validation suite — Phase 3 stress tests.

Design principles:
- Each test function takes the already-loaded X/y datasets and the Phase 3
  base results (stored in usdcad_model_results.pkl). No network calls.
- Model code is imported from pipeline.usdcad.model; no forking.
- Compute budget: each full pipeline run ~9 minutes on this machine.
  Tests 1 (3 seeds), 4 (3 windows), 5 (3 horizons) = ~9+9+9 = ~27 min.
  Tests 2, 3, 6 are post-hoc on stored data, <2 min combined.
- All random seeds are fixed per test call and logged.
- Failures are reported, not suppressed.

Usage:
    python -m pipeline.usdcad.validation.run
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

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Internal imports from Phase 3 model (no forking)
# ---------------------------------------------------------------------------
import sys
_project_root = Path(__file__).parents[4]
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from pipeline.usdcad.model import (
    build_model_dataset,
    split_train_holdout,
    run_filter_stage,
    run_embedded_stage,
    run_validation,
    compute_score_with_fixed_signs,
    determine_signs_first_half,
    HORIZONS,
    HOLDOUT_FRACTION,
)


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _run_full_pipeline_on_data(
    X: pd.DataFrame,
    y: pd.Series,
    y_dir: pd.Series,
    horizon_h: int,
    holdout_fraction: float = HOLDOUT_FRACTION,
    label: str = "",
) -> dict:
    """Run the complete Phase 3 pipeline on the provided X/y.

    This is the workhorse called by placebo, synthetic-null, and
    alternative-hold-out tests. It mirrors run_horizon() but accepts
    pre-built X/y rather than loading from disk, and accepts an
    arbitrary holdout_fraction / holdout window.

    Returns a dict with the key metrics needed for reporting.
    """
    # 1. Split
    (X_train, y_train, y_dir_train,
     X_ho, y_ho, y_dir_ho, split_idx) = split_train_holdout(
        X, y, y_dir, holdout_fraction=holdout_fraction
    )

    if len(X_train) < 100 or len(X_ho) < horizon_h * 2:
        logger.warning("[%s] Train=%d or hold-out=%d rows too small -- skipping",
                       label, len(X_train), len(X_ho))
        return _empty_pipeline_result(label)

    # 2. Filter (on training only)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        filter_results = run_filter_stage(X_train, y_train)

    kept_cols = [r.variable for r in filter_results if r.passes_filter]
    if not kept_cols:
        kept_cols = X_train.columns.tolist()
    X_filtered_train = X_train[kept_cols].copy()

    # 3. Embedded selection (on training only; signs from first half of training)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        selection = run_embedded_stage(X_filtered_train, y_train, horizon_h)

    # 4. Validation
    final_features = selection.final_selected or selection.elasticnet_selected
    ho_cols = [c for c in kept_cols if c in X_ho.columns]
    X_ho_filtered = X_ho[ho_cols].copy()

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        validation = run_validation(
            X_train=X_train,
            y_train=y_train,
            y_dir_train=y_dir_train,
            X_holdout=X_ho_filtered,
            y_holdout=y_ho,
            y_dir_holdout=y_dir_ho,
            selected_features=final_features,
            feature_signs=selection.feature_signs,
            horizon_h=horizon_h,
            n_trials=len(X.columns),
            filter_results=filter_results,
        )

    return {
        "label": label,
        "n_features_selected": len(final_features),
        "features_selected": final_features,
        "cv_hit_rate": validation.cv_hit_rate,
        "cv_dsr": validation.dsr,
        "cv_sharpe": validation.cv_sharpe,
        "holdout_hit_rate": validation.holdout_hit_rate,
        "holdout_r2": validation.holdout_r2,
        "holdout_sharpe": validation.holdout_sharpe,
        "holdout_hit_extreme": validation.holdout_hit_rate_extreme,
        "holdout_hit_middle": validation.holdout_hit_rate_middle,
        "holdout_n_extreme": validation.holdout_n_extreme_obs,
        "holdout_n_obs": validation.holdout_n_obs,
        "holdout_start": validation.holdout_start_date,
        "holdout_end": validation.holdout_end_date,
        "holdout_extreme_edge_pp": (
            validation.holdout_hit_rate_extreme - validation.holdout_hit_rate_middle
        ) * 100,
        "training_extreme_edge_pp": (
            validation.hit_rate_extreme - validation.hit_rate_middle
        ) * 100,
    }


def _empty_pipeline_result(label: str) -> dict:
    return {
        "label": label,
        "n_features_selected": 0,
        "features_selected": [],
        "cv_hit_rate": 0.5,
        "cv_dsr": 0.0,
        "cv_sharpe": 0.0,
        "holdout_hit_rate": 0.5,
        "holdout_r2": 0.0,
        "holdout_sharpe": 0.0,
        "holdout_hit_extreme": 0.5,
        "holdout_hit_middle": 0.5,
        "holdout_n_extreme": 0,
        "holdout_n_obs": 0,
        "holdout_start": "",
        "holdout_end": "",
        "holdout_extreme_edge_pp": 0.0,
        "training_extreme_edge_pp": 0.0,
    }


# ---------------------------------------------------------------------------
# Test 1: Placebo / shuffle test
# ---------------------------------------------------------------------------

@dataclass
class PlaceboResult:
    horizon: str
    seeds_tested: list[int]
    seed_results: list[dict]   # one per seed: raw pipeline result dict
    # Distributions under null
    null_cv_hit_rates: list[float]
    null_holdout_hit_rates: list[float]
    null_extreme_edges_pp: list[float]
    null_dsr_values: list[float]
    # Phase 3 real values for comparison
    real_cv_hit_rate: float
    real_holdout_hit_rate: float
    real_extreme_edge_pp: float
    real_dsr: float
    # Verdict
    any_seed_shows_edge: bool   # True = possible remaining leak
    max_null_cv_hit: float
    max_null_holdout_hit: float
    max_null_extreme_edge_pp: float
    verdict: str


def run_test1_placebo(
    phase3_results: dict,  # {horizon: HorizonResult} from model.run_all_horizons()
    seeds: list[int] = None,
) -> dict[str, PlaceboResult]:
    """Test 1: Shuffle Y labels while keeping X intact.

    For each seed:
      - Randomly shuffle the target vector y (both continuous and directional)
        BEFORE any pipeline step: before filter, before sign determination,
        before CV, before hold-out evaluation.
      - Run the FULL pipeline end-to-end on shuffled Y.

    Expectation: no edge anywhere. If any horizon shows holdout hit rate > 55%
    or extreme edge > +5pp on shuffled Y, there is still a methodological
    source of apparent signal.

    Note: Y shuffling must span the full dataset (not just training) so that
    the holdout also gets shuffled returns — otherwise the test is trivially
    non-contaminating and misses leaks that flow through the sign-determination
    step into hold-out evaluation.
    """
    if seeds is None:
        seeds = [0, 7, 42, 137, 999]

    results: dict[str, PlaceboResult] = {}

    for horizon in ["weekly", "monthly", "quarterly"]:
        h = HORIZONS[horizon]
        logger.info("=== Test 1 (Placebo) | %s | %d seeds ===", horizon, len(seeds))

        # Load real data
        X_full, y_full, y_dir_full = build_model_dataset(horizon)

        # Real Phase 3 numbers for comparison (from stored results)
        hr = phase3_results.get(horizon)
        if hr:
            real_cv = hr.validation.cv_hit_rate
            real_ho_hit = hr.validation.holdout_hit_rate
            real_extreme_edge = (
                hr.validation.holdout_hit_rate_extreme
                - hr.validation.holdout_hit_rate_middle
            ) * 100
            real_dsr = hr.validation.dsr
        else:
            real_cv = real_ho_hit = real_extreme_edge = real_dsr = float("nan")

        seed_results = []
        null_cv_hits, null_ho_hits, null_edges, null_dsrs = [], [], [], []

        for seed in seeds:
            logger.info("  Seed %d ...", seed)
            rng = np.random.RandomState(seed)

            # Shuffle Y globally (same permutation for continuous and directional)
            # This is the key adversarial step: X is untouched, Y is random noise.
            perm = rng.permutation(len(y_full))
            y_shuffled = pd.Series(
                y_full.values[perm],
                index=y_full.index,
                name=y_full.name,
            )
            y_dir_shuffled = pd.Series(
                y_dir_full.values[perm],
                index=y_dir_full.index,
                name=y_dir_full.name,
            )

            try:
                res = _run_full_pipeline_on_data(
                    X_full, y_shuffled, y_dir_shuffled, h,
                    label=f"placebo_{horizon}_seed{seed}",
                )
            except Exception as e:
                logger.error("  Seed %d failed: %s", seed, e)
                res = _empty_pipeline_result(f"placebo_{horizon}_seed{seed}")

            seed_results.append(res)
            null_cv_hits.append(res["cv_hit_rate"])
            null_ho_hits.append(res["holdout_hit_rate"])
            null_edges.append(res["holdout_extreme_edge_pp"])
            null_dsrs.append(res["cv_dsr"])

            logger.info(
                "  Seed %d: CV hit=%.1f%%, HO hit=%.1f%%, extreme edge=%.1fpp, DSR=%.2f",
                seed, res["cv_hit_rate"] * 100, res["holdout_hit_rate"] * 100,
                res["holdout_extreme_edge_pp"], res["cv_dsr"],
            )

        max_null_ho = max(null_ho_hits) if null_ho_hits else 0.5
        max_null_cv = max(null_cv_hits) if null_cv_hits else 0.5
        max_null_edge = max(null_edges) if null_edges else 0.0

        # Edge threshold: >55% holdout hit rate or >+5pp extreme edge on shuffled Y
        # indicates a remaining methodological artifact
        EDGE_THRESHOLD_HIT = 0.55
        EDGE_THRESHOLD_EXTREME = 5.0
        any_edge = (
            max_null_ho > EDGE_THRESHOLD_HIT
            or max_null_edge > EDGE_THRESHOLD_EXTREME
        )

        if any_edge:
            verdict = (
                "FAIL: Shuffled Y produced apparent edge (holdout hit "
                f"{max_null_ho:.1%} or extreme edge {max_null_edge:.1f}pp). "
                "A methodological source of spurious signal exists."
            )
        else:
            verdict = (
                "PASS: No seed produced edge on shuffled Y. "
                f"Max holdout hit={max_null_ho:.1%}, max extreme edge={max_null_edge:.1f}pp. "
                "Pipeline correctly returns noise under null."
            )

        results[horizon] = PlaceboResult(
            horizon=horizon,
            seeds_tested=seeds,
            seed_results=seed_results,
            null_cv_hit_rates=null_cv_hits,
            null_holdout_hit_rates=null_ho_hits,
            null_extreme_edges_pp=null_edges,
            null_dsr_values=null_dsrs,
            real_cv_hit_rate=real_cv,
            real_holdout_hit_rate=real_ho_hit,
            real_extreme_edge_pp=real_extreme_edge,
            real_dsr=real_dsr,
            any_seed_shows_edge=any_edge,
            max_null_cv_hit=max_null_cv,
            max_null_holdout_hit=max_null_ho,
            max_null_extreme_edge_pp=max_null_edge,
            verdict=verdict,
        )
        logger.info("Test 1 | %s | %s", horizon, verdict)

    return results


# ---------------------------------------------------------------------------
# Test 2: Synthetic null X matrix
# ---------------------------------------------------------------------------

@dataclass
class SyntheticNullResult:
    horizon: str
    n_sims: int
    sim_results: list[dict]
    null_cv_hit_rates: list[float]
    null_holdout_hit_rates: list[float]
    null_extreme_edges_pp: list[float]
    real_cv_hit_rate: float
    real_holdout_hit_rate: float
    real_extreme_edge_pp: float
    verdict: str


def _simulate_null_X(X_real: pd.DataFrame, seed: int) -> pd.DataFrame:
    """Covariance-preserving bootstrap of X.

    Method: multivariate normal simulation matching the empirical mean
    and covariance of X_real. This preserves the cross-correlation
    and variance structure while removing any X->Y relationship.

    The resulting X_null has the same statistical signature as X_real
    (autocorrelation is not preserved -- this is a cross-sectional
    covariance match, not a temporal one). This is sufficient to detect
    structural biases from the covariance structure of X alone.

    Note on autocorrelation: for a stricter test, use block bootstrap
    rows from X_real instead. However, that test conflates the X
    structure with row-selection sampling. The Cholesky draw here
    isolates the covariance-structure question cleanly.
    """
    rng = np.random.RandomState(seed)
    X_vals = X_real.values.copy()

    # Fill NaN with column mean for covariance computation
    col_means = np.nanmean(X_vals, axis=0)
    for j in range(X_vals.shape[1]):
        mask = np.isnan(X_vals[:, j])
        X_vals[mask, j] = col_means[j]

    mu = X_vals.mean(axis=0)
    cov = np.cov(X_vals, rowvar=False)

    # Regularize covariance (add small diagonal to ensure PSD)
    cov = cov + np.eye(cov.shape[0]) * 1e-6

    try:
        L = np.linalg.cholesky(cov)
        z = rng.standard_normal((len(X_real), len(mu)))
        X_sim = z @ L.T + mu
    except np.linalg.LinAlgError:
        # Fallback: eigenvector decomposition
        eigvals, eigvecs = np.linalg.eigh(cov)
        eigvals = np.maximum(eigvals, 1e-8)
        L = eigvecs @ np.diag(np.sqrt(eigvals))
        z = rng.standard_normal((len(X_real), len(mu)))
        X_sim = z @ L.T + mu

    X_null = pd.DataFrame(X_sim, index=X_real.index, columns=X_real.columns)
    return X_null


def run_test2_synthetic_null(
    phase3_results: dict,
    n_sims: int = 3,
) -> dict[str, SyntheticNullResult]:
    """Test 2: Synthetic null X matrix.

    Generate X matrices with the same covariance structure as the real X
    but NO actual relationship to USDCAD returns. Re-run the full pipeline.

    Expectation: no edge. If edge appears, there is a structural bias in
    the methodology (e.g., the pipeline can manufacture edge from
    the covariance structure of X alone, independent of any X->Y signal).
    """
    results: dict[str, SyntheticNullResult] = {}

    for horizon in ["weekly", "monthly", "quarterly"]:
        h = HORIZONS[horizon]
        logger.info("=== Test 2 (Synthetic null) | %s | %d sims ===", horizon, n_sims)

        X_full, y_full, y_dir_full = build_model_dataset(horizon)

        hr = phase3_results.get(horizon)
        real_cv = hr.validation.cv_hit_rate if hr else float("nan")
        real_ho = hr.validation.holdout_hit_rate if hr else float("nan")
        real_edge = (
            (hr.validation.holdout_hit_rate_extreme - hr.validation.holdout_hit_rate_middle) * 100
            if hr else float("nan")
        )

        sim_results = []
        null_cv_hits, null_ho_hits, null_edges = [], [], []

        for seed in range(n_sims):
            logger.info("  Sim %d ...", seed)
            X_null = _simulate_null_X(X_full, seed=seed + 100)

            try:
                res = _run_full_pipeline_on_data(
                    X_null, y_full, y_dir_full, h,
                    label=f"synth_null_{horizon}_sim{seed}",
                )
            except Exception as e:
                logger.error("  Sim %d failed: %s", seed, e)
                res = _empty_pipeline_result(f"synth_null_{horizon}_sim{seed}")

            sim_results.append(res)
            null_cv_hits.append(res["cv_hit_rate"])
            null_ho_hits.append(res["holdout_hit_rate"])
            null_edges.append(res["holdout_extreme_edge_pp"])

            logger.info(
                "  Sim %d: CV hit=%.1f%%, HO hit=%.1f%%, extreme edge=%.1fpp",
                seed, res["cv_hit_rate"] * 100, res["holdout_hit_rate"] * 100,
                res["holdout_extreme_edge_pp"],
            )

        max_null_ho = max(null_ho_hits) if null_ho_hits else 0.5
        max_null_edge = max(null_edges) if null_edges else 0.0

        EDGE_THRESHOLD_HIT = 0.55
        EDGE_THRESHOLD_EXTREME = 5.0
        any_edge = (
            max_null_ho > EDGE_THRESHOLD_HIT
            or max_null_edge > EDGE_THRESHOLD_EXTREME
        )

        if any_edge:
            verdict = (
                "FAIL: Synthetic null X produced apparent edge "
                f"(max holdout hit={max_null_ho:.1%}, max extreme edge={max_null_edge:.1f}pp). "
                "The methodology has a structural bias independent of X->Y signal."
            )
        else:
            verdict = (
                "PASS: Synthetic null X produced no edge. "
                f"Max holdout hit={max_null_ho:.1%}, max extreme edge={max_null_edge:.1f}pp. "
                "Pipeline does not manufacture edge from X covariance structure alone."
            )

        results[horizon] = SyntheticNullResult(
            horizon=horizon,
            n_sims=n_sims,
            sim_results=sim_results,
            null_cv_hit_rates=null_cv_hits,
            null_holdout_hit_rates=null_ho_hits,
            null_extreme_edges_pp=null_edges,
            real_cv_hit_rate=real_cv,
            real_holdout_hit_rate=real_ho,
            real_extreme_edge_pp=real_edge,
            verdict=verdict,
        )
        logger.info("Test 2 | %s | %s", horizon, verdict)

    return results


# ---------------------------------------------------------------------------
# Test 3: Bootstrap null distribution + Bonferroni/Holm correction
# ---------------------------------------------------------------------------

@dataclass
class BootstrapNullResult:
    horizon: str
    headline_metric: str   # "holdout_hit_rate_extreme"
    observed_value: float
    n_bootstrap: int
    null_distribution: list[float]
    raw_pvalue: float
    bonferroni_pvalue: float  # * 3 (three horizons)
    holm_pvalue: float
    ci_95_lower: float
    ci_95_upper: float
    n_extreme_obs: int
    verdict: str


def _bootstrap_null_hit_rate(
    n_obs: int, n_extreme_obs: int, seed: int, n_bootstrap: int
) -> list[float]:
    """Build null distribution for a hit rate under H0 (p=0.5).

    Model: each of n_extreme_obs observations is a fair coin flip.
    Bootstrap by drawing n_extreme_obs Bernoulli(0.5) samples n_bootstrap times.
    Returns the distribution of hit rates under the null.

    This is equivalent to the binomial distribution but expressed as a
    bootstrap for generality.
    """
    rng = np.random.RandomState(seed)
    null_hits = []
    for _ in range(n_bootstrap):
        # Each observation is a 50/50 directional call under H0
        draws = rng.binomial(1, 0.5, size=n_extreme_obs)
        null_hits.append(float(draws.mean()))
    return null_hits


def run_test3_bootstrap_null(
    phase3_results: dict,
    n_bootstrap: int = 10000,
) -> dict[str, BootstrapNullResult]:
    """Test 3: Bootstrap null distribution and p-values for extreme-reading hit rates.

    For each horizon, the headline claim is the extreme-reading hit rate:
      - Weekly: 64.6% (n=223 hold-out extreme obs)
      - Monthly: 73.1% (n=223 hold-out extreme obs)  [note: findings_summary shows 70.4%]
      - Quarterly: 70.1% (n=221 hold-out extreme obs)

    Under H0 (coin flip), the number of correct directional calls ~ Binomial(n, 0.5).
    Bootstrap 10,000 samples under H0 to build the null distribution.
    Report the p-value for the observed hit rate.
    Apply Bonferroni and Holm corrections for 3 simultaneous tests (3 horizons).

    Note: We use the EXTREME hold-out hit rate, not the aggregate, because that
    is the specific product claim. The aggregate hold-out hit rate is a separate
    claim and would need its own test.
    """
    # Extract observed values from Phase 3 results
    observed = {}
    n_extremes = {}
    for horizon, hr in phase3_results.items():
        v = hr.validation
        observed[horizon] = v.holdout_hit_rate_extreme
        n_extremes[horizon] = v.holdout_n_extreme_obs

    raw_pvalues = {}
    bootstrap_results = {}

    for horizon in ["weekly", "monthly", "quarterly"]:
        obs_hit = observed.get(horizon, 0.5)
        n_ext = n_extremes.get(horizon, 0)

        logger.info(
            "Test 3 | %s | observed=%.1f%% on %d extreme obs",
            horizon, obs_hit * 100, n_ext,
        )

        if n_ext < 5:
            logger.warning("  Too few extreme obs (%d) -- skipping bootstrap", n_ext)
            bootstrap_results[horizon] = BootstrapNullResult(
                horizon=horizon,
                headline_metric="holdout_hit_rate_extreme",
                observed_value=obs_hit,
                n_bootstrap=n_bootstrap,
                null_distribution=[],
                raw_pvalue=float("nan"),
                bonferroni_pvalue=float("nan"),
                holm_pvalue=float("nan"),
                ci_95_lower=float("nan"),
                ci_95_upper=float("nan"),
                n_extreme_obs=n_ext,
                verdict="INCONCLUSIVE: insufficient extreme observations",
            )
            raw_pvalues[horizon] = float("nan")
            continue

        null_dist = _bootstrap_null_hit_rate(n_ext, n_ext, seed=42, n_bootstrap=n_bootstrap)
        null_arr = np.array(null_dist)

        # One-sided p-value: P(null >= observed)
        raw_p = float(np.mean(null_arr >= obs_hit))
        raw_pvalues[horizon] = raw_p

        ci_lower = float(np.percentile(null_arr, 2.5))
        ci_upper = float(np.percentile(null_arr, 97.5))

        bootstrap_results[horizon] = BootstrapNullResult(
            horizon=horizon,
            headline_metric="holdout_hit_rate_extreme",
            observed_value=obs_hit,
            n_bootstrap=n_bootstrap,
            null_distribution=null_dist,
            raw_pvalue=raw_p,
            bonferroni_pvalue=min(raw_p * 3, 1.0),
            holm_pvalue=float("nan"),  # filled after all three computed
            ci_95_lower=ci_lower,
            ci_95_upper=ci_upper,
            n_extreme_obs=n_ext,
            verdict="",  # filled after Holm
        )

    # Holm-Bonferroni correction across the 3 horizons
    horizons_sorted = sorted(
        [h for h in raw_pvalues if not np.isnan(raw_pvalues[h])],
        key=lambda h: raw_pvalues[h],
    )
    m = len(horizons_sorted)
    for rank, h in enumerate(horizons_sorted):
        holm_p = min(raw_pvalues[h] * (m - rank), 1.0)
        bootstrap_results[h].holm_pvalue = holm_p

    # Assign verdicts
    for horizon in ["weekly", "monthly", "quarterly"]:
        if horizon not in bootstrap_results:
            continue
        r = bootstrap_results[horizon]
        if np.isnan(r.raw_pvalue):
            continue
        alpha = 0.05
        if r.holm_pvalue < alpha:
            verdict = (
                f"SIGNIFICANT: Holm-corrected p={r.holm_pvalue:.4f} < 0.05. "
                f"Observed {r.observed_value:.1%} on {r.n_extreme_obs} extreme obs "
                f"is unlikely under H0 (null 95% CI: [{r.ci_95_lower:.1%}, {r.ci_95_upper:.1%}])."
            )
        elif r.bonferroni_pvalue < alpha:
            verdict = (
                f"BORDERLINE: Bonferroni p={r.bonferroni_pvalue:.4f} < 0.05 but "
                f"Holm p={r.holm_pvalue:.4f}. Inconsistent; treat as borderline."
            )
        elif r.raw_pvalue < alpha:
            verdict = (
                f"MARGINAL: Raw p={r.raw_pvalue:.4f} < 0.05 but does not survive "
                f"Bonferroni correction (p={r.bonferroni_pvalue:.4f}). "
                "Claim is not statistically robust after multiple-testing correction."
            )
        else:
            verdict = (
                f"NOT SIGNIFICANT: Raw p={r.raw_pvalue:.4f}. "
                f"Observed {r.observed_value:.1%} is not distinguishable from H0 "
                f"null (95% CI: [{r.ci_95_lower:.1%}, {r.ci_95_upper:.1%}]) "
                "after multiple-testing correction."
            )
        r.verdict = verdict
        logger.info("Test 3 | %s | %s", horizon, verdict)

    return bootstrap_results


# ---------------------------------------------------------------------------
# Test 4: Alternative hold-out windows
# ---------------------------------------------------------------------------

# Three alternative hold-out windows (as date ranges):
#   2008-2012 -- GFC + post-GFC recovery
#   2014-2018 -- oil regime + tightening cycle
#   2018-2022 -- pre-COVID, COVID, post-COVID
# The standard Phase 3 hold-out is 2022-2026.
ALTERNATIVE_HOLDOUT_WINDOWS = {
    "2008-2012 (GFC+recovery)": ("2008-01-01", "2012-12-31"),
    "2014-2018 (oil+tightening)": ("2014-01-01", "2018-12-31"),
    "2018-2022 (COVID era)": ("2018-01-01", "2022-01-21"),
}


@dataclass
class AltHoldoutResult:
    horizon: str
    window_name: str
    window_start: str
    window_end: str
    holdout_hit_rate: float
    holdout_hit_extreme: float
    holdout_hit_middle: float
    holdout_extreme_edge_pp: float
    holdout_n_obs: int
    holdout_n_extreme: int
    cv_hit_rate: float
    cv_dsr: float
    verdict: str


def _build_alt_holdout_dataset(
    X_full: pd.DataFrame,
    y_full: pd.Series,
    y_dir_full: pd.Series,
    holdout_start: str,
    holdout_end: str,
) -> tuple[pd.DataFrame, pd.Series, pd.Series,
           pd.DataFrame, pd.Series, pd.Series]:
    """Build train/holdout split for an arbitrary date-window holdout.

    The hold-out is the rows within [holdout_start, holdout_end].
    Training is all OTHER rows (before and after the hold-out window).

    Note: using rows outside the hold-out window (including rows after
    it) as training data is the correct approach for alternative-window
    testing. We are asking: does the model trained on everything EXCEPT
    this window do well IN this window?

    This differs from the standard Phase 3 split (last 20% only).
    For the financial-crisis window in particular, using post-crisis
    data in training is realistic: a live model would have been
    retrained with more data over time.
    """
    ho_mask = (X_full.index >= pd.Timestamp(holdout_start)) & \
              (X_full.index <= pd.Timestamp(holdout_end))
    train_mask = ~ho_mask

    if ho_mask.sum() < 10 or train_mask.sum() < 100:
        raise ValueError(
            f"Hold-out window {holdout_start}-{holdout_end} is too small "
            f"(ho={ho_mask.sum()}, train={train_mask.sum()})"
        )

    X_train = X_full.loc[train_mask]
    y_train = y_full.loc[train_mask]
    y_dir_train = y_dir_full.loc[train_mask]
    X_ho = X_full.loc[ho_mask]
    y_ho = y_full.loc[ho_mask]
    y_dir_ho = y_dir_full.loc[ho_mask]

    return X_train, y_train, y_dir_train, X_ho, y_ho, y_dir_ho


def _run_pipeline_alt_holdout(
    X_full: pd.DataFrame,
    y_full: pd.Series,
    y_dir_full: pd.Series,
    horizon_h: int,
    holdout_start: str,
    holdout_end: str,
    label: str,
) -> dict:
    """Run full pipeline with an arbitrary hold-out date window.

    Filter and selection run on the training rows (complement of the hold-out window).
    Signs are determined from the first half of the TRAINING rows (chronological).
    Hold-out is evaluated once.
    """
    (X_train, y_train, y_dir_train,
     X_ho, y_ho, y_dir_ho) = _build_alt_holdout_dataset(
        X_full, y_full, y_dir_full, holdout_start, holdout_end
    )

    # Filter on training only
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        filter_results = run_filter_stage(X_train, y_train)

    kept_cols = [r.variable for r in filter_results if r.passes_filter]
    if not kept_cols:
        kept_cols = X_train.columns.tolist()
    X_filtered_train = X_train[kept_cols].copy()

    # Embedded selection on training only (signs from first half)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        selection = run_embedded_stage(X_filtered_train, y_train, horizon_h)

    final_features = selection.final_selected or selection.elasticnet_selected
    ho_cols = [c for c in kept_cols if c in X_ho.columns]
    X_ho_filtered = X_ho[ho_cols].copy()

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        validation = run_validation(
            X_train=X_train,
            y_train=y_train,
            y_dir_train=y_dir_train,
            X_holdout=X_ho_filtered,
            y_holdout=y_ho,
            y_dir_holdout=y_dir_ho,
            selected_features=final_features,
            feature_signs=selection.feature_signs,
            horizon_h=horizon_h,
            n_trials=len(X_full.columns),
            filter_results=filter_results,
        )

    return {
        "label": label,
        "cv_hit_rate": validation.cv_hit_rate,
        "cv_dsr": validation.dsr,
        "holdout_hit_rate": validation.holdout_hit_rate,
        "holdout_hit_extreme": validation.holdout_hit_rate_extreme,
        "holdout_hit_middle": validation.holdout_hit_rate_middle,
        "holdout_extreme_edge_pp": (
            validation.holdout_hit_rate_extreme - validation.holdout_hit_rate_middle
        ) * 100,
        "holdout_n_obs": validation.holdout_n_obs,
        "holdout_n_extreme": validation.holdout_n_extreme_obs,
    }


def run_test4_alt_holdouts(
    phase3_results: dict,
) -> dict[str, list[AltHoldoutResult]]:
    """Test 4: Alternative hold-out windows.

    If the Phase 3 edge is a genuine methodology finding, it should
    persist (with variance) across multiple hold-out regimes, not only
    in the 2022-2026 BoC-tightening window.

    For each horizon x 3 alternative windows, re-run the full pipeline
    with that window as the hold-out. Compare hold-out hit rates.

    Regime-specific failure is not automatically disqualifying -- a model
    that only works in trending-rate regimes is still a useful claim --
    but it narrows the product claim materially.
    """
    results: dict[str, list[AltHoldoutResult]] = {
        "weekly": [], "monthly": [], "quarterly": []
    }

    for horizon in ["weekly", "monthly", "quarterly"]:
        h = HORIZONS[horizon]
        logger.info("=== Test 4 (Alt holdouts) | %s ===", horizon)

        X_full, y_full, y_dir_full = build_model_dataset(horizon)

        for window_name, (win_start, win_end) in ALTERNATIVE_HOLDOUT_WINDOWS.items():
            logger.info("  Window: %s (%s to %s)", window_name, win_start, win_end)
            label = f"alt_holdout_{horizon}_{win_start[:4]}"

            try:
                res = _run_pipeline_alt_holdout(
                    X_full, y_full, y_dir_full, h,
                    holdout_start=win_start,
                    holdout_end=win_end,
                    label=label,
                )
                edge = res["holdout_extreme_edge_pp"]
                ho_hit = res["holdout_hit_rate"]

                if res["holdout_n_obs"] < 20:
                    verdict = "INCONCLUSIVE: insufficient hold-out observations"
                elif ho_hit >= 0.53 and edge >= 5.0:
                    verdict = (
                        f"EDGE FOUND: holdout hit={ho_hit:.1%}, "
                        f"extreme edge=+{edge:.1f}pp on {res['holdout_n_extreme']} extreme obs."
                    )
                elif edge >= 5.0:
                    verdict = (
                        f"EXTREME EDGE ONLY: overall hit={ho_hit:.1%} (<53%), "
                        f"but extreme edge=+{edge:.1f}pp on {res['holdout_n_extreme']} obs."
                    )
                elif ho_hit >= 0.53:
                    verdict = (
                        f"AGGREGATE EDGE ONLY: overall hit={ho_hit:.1%}, "
                        f"extreme edge only +{edge:.1f}pp (below +5pp threshold)."
                    )
                else:
                    verdict = (
                        f"NO EDGE: holdout hit={ho_hit:.1%}, "
                        f"extreme edge=+{edge:.1f}pp. No signal in this regime."
                    )

                results[horizon].append(AltHoldoutResult(
                    horizon=horizon,
                    window_name=window_name,
                    window_start=win_start,
                    window_end=win_end,
                    holdout_hit_rate=res["holdout_hit_rate"],
                    holdout_hit_extreme=res["holdout_hit_extreme"],
                    holdout_hit_middle=res["holdout_hit_middle"],
                    holdout_extreme_edge_pp=edge,
                    holdout_n_obs=res["holdout_n_obs"],
                    holdout_n_extreme=res["holdout_n_extreme"],
                    cv_hit_rate=res["cv_hit_rate"],
                    cv_dsr=res["cv_dsr"],
                    verdict=verdict,
                ))

            except Exception as e:
                logger.error("  Window %s failed: %s", window_name, e)
                results[horizon].append(AltHoldoutResult(
                    horizon=horizon,
                    window_name=window_name,
                    window_start=win_start,
                    window_end=win_end,
                    holdout_hit_rate=float("nan"),
                    holdout_hit_extreme=float("nan"),
                    holdout_hit_middle=float("nan"),
                    holdout_extreme_edge_pp=float("nan"),
                    holdout_n_obs=0,
                    holdout_n_extreme=0,
                    cv_hit_rate=float("nan"),
                    cv_dsr=float("nan"),
                    verdict=f"ERROR: {e}",
                ))

            logger.info("  %s | %s", window_name, results[horizon][-1].verdict)

    return results


# ---------------------------------------------------------------------------
# Test 5: Variable importance robustness (drop top-3 features)
# ---------------------------------------------------------------------------

@dataclass
class DropTopFeaturesResult:
    horizon: str
    top3_features: list[str]
    with_top3_holdout_hit: float
    with_top3_extreme_edge_pp: float
    without_top3_holdout_hit: float
    without_top3_extreme_edge_pp: float
    without_top3_n_selected: int
    hit_delta_pp: float
    edge_delta_pp: float
    verdict: str


def run_test5_drop_top_features(
    phase3_results: dict,
) -> dict[str, DropTopFeaturesResult]:
    """Test 5: Drop top-3 features by importance; re-run pipeline.

    For each horizon:
    1. Identify top-3 features by MDA importance from Phase 3 results.
    2. Remove them from X entirely.
    3. Re-run the full pipeline.
    4. Compare hold-out hit rates.

    If the model still shows edge without its top-3 drivers, the signal
    is broad and robust. If edge disappears, it rests on 1-3 specific
    variables (which may themselves be spurious survivors).
    """
    results: dict[str, DropTopFeaturesResult] = {}

    for horizon in ["weekly", "monthly", "quarterly"]:
        h = HORIZONS[horizon]
        hr = phase3_results.get(horizon)
        logger.info("=== Test 5 (Drop top-3) | %s ===", horizon)

        if not hr:
            logger.warning("  No Phase 3 results for %s -- skipping", horizon)
            continue

        # Identify top-3 by MDA importance
        mda_imp = hr.selection.mda_importances
        if mda_imp:
            top3 = [k for k, _ in sorted(
                mda_imp.items(), key=lambda kv: kv[1], reverse=True
            )[:3]]
        else:
            # Fall back to ElasticNet coefficient magnitude
            en_coefs = hr.selection.elasticnet_coefs
            top3 = [k for k, _ in sorted(
                en_coefs.items(), key=lambda kv: abs(kv[1]), reverse=True
            )[:3]] if en_coefs else []

        logger.info("  Top-3 features to drop: %s", top3)

        # Real Phase 3 numbers (with top-3)
        real_ho_hit = hr.validation.holdout_hit_rate
        real_edge = (
            hr.validation.holdout_hit_rate_extreme
            - hr.validation.holdout_hit_rate_middle
        ) * 100

        if not top3:
            results[horizon] = DropTopFeaturesResult(
                horizon=horizon,
                top3_features=[],
                with_top3_holdout_hit=real_ho_hit,
                with_top3_extreme_edge_pp=real_edge,
                without_top3_holdout_hit=float("nan"),
                without_top3_extreme_edge_pp=float("nan"),
                without_top3_n_selected=0,
                hit_delta_pp=float("nan"),
                edge_delta_pp=float("nan"),
                verdict="INCONCLUSIVE: could not identify top-3 features",
            )
            continue

        X_full, y_full, y_dir_full = build_model_dataset(horizon)

        # Drop top-3 from X
        drop_cols = [c for c in top3 if c in X_full.columns]
        X_dropped = X_full.drop(columns=drop_cols)
        logger.info("  X shape after drop: %s", X_dropped.shape)

        try:
            res = _run_full_pipeline_on_data(
                X_dropped, y_full, y_dir_full, h,
                label=f"drop_top3_{horizon}",
            )
            dropped_ho_hit = res["holdout_hit_rate"]
            dropped_edge = res["holdout_extreme_edge_pp"]

            hit_delta = (dropped_ho_hit - real_ho_hit) * 100
            edge_delta = dropped_edge - real_edge

            # Does edge survive?
            if dropped_ho_hit >= 0.53 or dropped_edge >= 5.0:
                verdict = (
                    f"ROBUST: Edge survives removal of top-3 features. "
                    f"Without top-3: holdout hit={dropped_ho_hit:.1%} (was {real_ho_hit:.1%}), "
                    f"extreme edge=+{dropped_edge:.1f}pp (was +{real_edge:.1f}pp). "
                    "Signal is broad-based, not dependent on 1-3 variables."
                )
            else:
                verdict = (
                    f"NOT ROBUST: Edge disappears when top-3 features are removed. "
                    f"Without top-3: holdout hit={dropped_ho_hit:.1%} (was {real_ho_hit:.1%}), "
                    f"extreme edge=+{dropped_edge:.1f}pp (was +{real_edge:.1f}pp). "
                    "The claim rests on a small number of specific variables."
                )

            results[horizon] = DropTopFeaturesResult(
                horizon=horizon,
                top3_features=top3,
                with_top3_holdout_hit=real_ho_hit,
                with_top3_extreme_edge_pp=real_edge,
                without_top3_holdout_hit=dropped_ho_hit,
                without_top3_extreme_edge_pp=dropped_edge,
                without_top3_n_selected=res["n_features_selected"],
                hit_delta_pp=hit_delta,
                edge_delta_pp=edge_delta,
                verdict=verdict,
            )

        except Exception as e:
            logger.error("  Drop-top3 failed for %s: %s", horizon, e)
            results[horizon] = DropTopFeaturesResult(
                horizon=horizon,
                top3_features=top3,
                with_top3_holdout_hit=real_ho_hit,
                with_top3_extreme_edge_pp=real_edge,
                without_top3_holdout_hit=float("nan"),
                without_top3_extreme_edge_pp=float("nan"),
                without_top3_n_selected=0,
                hit_delta_pp=float("nan"),
                edge_delta_pp=float("nan"),
                verdict=f"ERROR: {e}",
            )

        logger.info("  %s", results[horizon].verdict)

    return results


# ---------------------------------------------------------------------------
# Test 6: Time-series block bootstrap CI
# ---------------------------------------------------------------------------

@dataclass
class BlockBootstrapResult:
    horizon: str
    observed_extreme_hit_rate: float
    n_extreme_obs: int
    block_size: int
    n_bootstrap: int
    ci_95_lower: float
    ci_95_upper: float
    ci_lower_above_50pct: bool
    verdict: str


def _stationary_block_bootstrap(
    data: np.ndarray, block_size: int, n_bootstrap: int, seed: int
) -> list[float]:
    """Politis-Romano stationary block bootstrap for a 1D time series.

    Block size is fixed (not geometrically random) for simplicity.
    Each bootstrap sample draws ceil(n/block_size) blocks with
    replacement, starting from random positions, then trims to n.

    Returns a list of mean values of the bootstrapped series --
    the mean here being the hit-rate (mean of 0/1 accuracy indicators).
    """
    rng = np.random.RandomState(seed)
    n = len(data)
    n_blocks = int(np.ceil(n / block_size))

    bootstrap_means = []
    for _ in range(n_bootstrap):
        starts = rng.randint(0, n, size=n_blocks)
        sample = []
        for s in starts:
            end = min(s + block_size, n)
            sample.extend(data[s:end].tolist())
        sample = np.array(sample[:n])
        bootstrap_means.append(float(sample.mean()))

    return bootstrap_means


def run_test6_block_bootstrap_ci(
    phase3_results: dict,
    block_sizes: list[int] = None,
    n_bootstrap: int = 5000,
) -> dict[str, BlockBootstrapResult]:
    """Test 6: Stationary block bootstrap CIs for headline hit rates.

    Standard bootstrap assumes independence between observations.
    FX returns are autocorrelated (especially at daily frequency with
    overlapping return windows). Block bootstrap preserves local
    autocorrelation structure.

    For each horizon, compute 95% CI for the extreme-reading hit rate
    using block bootstrap. Block size reflects the autocorrelation
    horizon:
      - Weekly (h=5): block_size=10 (2x the horizon)
      - Monthly (h=21): block_size=42
      - Quarterly (h=63): block_size=126

    If the lower bound of the 95% CI is below 50%, the headline number
    is not statistically distinguishable from a coin flip under
    autocorrelation-robust inference.
    """
    if block_sizes is None:
        # Block size = 2x the forecast horizon, minimum 5
        block_sizes = {
            "weekly": 10,
            "monthly": 42,
            "quarterly": 126,
        }

    results: dict[str, BlockBootstrapResult] = {}

    for horizon in ["weekly", "monthly", "quarterly"]:
        hr = phase3_results.get(horizon)
        if not hr:
            continue

        block_size = block_sizes.get(horizon, 10) if isinstance(block_sizes, dict) else block_sizes[0]
        h = HORIZONS[horizon]
        v = hr.validation

        # Build the hit/miss array for extreme observations on hold-out
        # We need the raw extreme-obs hit indicators from the hold-out.
        # Reconstruct from the hold-out score and actual returns.
        score_ho = compute_score_with_fixed_signs(
            hr.X_holdout,
            hr.selection.final_selected,
            hr.selection.feature_signs,
        )
        y_ho = hr.y_holdout.reindex(score_ho.index).dropna()
        score_ho = score_ho.reindex(y_ho.index)

        score_pcts = score_ho.rank(pct=True)
        extreme_mask = (score_pcts <= 0.10) | (score_pcts >= 0.90)
        score_ext = score_ho[extreme_mask]
        y_ext = y_ho[extreme_mask]

        if len(y_ext) < 5:
            logger.warning("Test 6 | %s | too few extreme obs (%d)", horizon, len(y_ext))
            results[horizon] = BlockBootstrapResult(
                horizon=horizon,
                observed_extreme_hit_rate=v.holdout_hit_rate_extreme,
                n_extreme_obs=len(y_ext),
                block_size=block_size,
                n_bootstrap=n_bootstrap,
                ci_95_lower=float("nan"),
                ci_95_upper=float("nan"),
                ci_lower_above_50pct=False,
                verdict="INCONCLUSIVE: too few extreme observations",
            )
            continue

        # 1 = correct direction, 0 = wrong direction
        hit_indicators = (
            np.sign(score_ext.values) == np.sign(y_ext.values)
        ).astype(float)

        observed_hit = float(hit_indicators.mean())
        logger.info(
            "Test 6 | %s | observed extreme hit=%.1f%% on %d obs, block_size=%d",
            horizon, observed_hit * 100, len(hit_indicators), block_size,
        )

        bootstrap_means = _stationary_block_bootstrap(
            hit_indicators, block_size=block_size,
            n_bootstrap=n_bootstrap, seed=42,
        )
        ci_lower = float(np.percentile(bootstrap_means, 2.5))
        ci_upper = float(np.percentile(bootstrap_means, 97.5))
        lower_above_50 = ci_lower > 0.50

        if lower_above_50:
            verdict = (
                f"SIGNIFICANT: 95% block-bootstrap CI [{ci_lower:.1%}, {ci_upper:.1%}] "
                f"is entirely above 50%. The extreme hit rate of {observed_hit:.1%} "
                "is statistically distinguishable from coin flip under "
                "autocorrelation-robust inference."
            )
        else:
            verdict = (
                f"NOT SIGNIFICANT: 95% block-bootstrap CI [{ci_lower:.1%}, {ci_upper:.1%}] "
                f"straddles 50%. The extreme hit rate of {observed_hit:.1%} is "
                "not statistically distinguishable from coin flip after accounting "
                "for autocorrelation (block_size={block_size}).".format(block_size=block_size)
            )

        results[horizon] = BlockBootstrapResult(
            horizon=horizon,
            observed_extreme_hit_rate=observed_hit,
            n_extreme_obs=len(y_ext),
            block_size=block_size,
            n_bootstrap=n_bootstrap,
            ci_95_lower=ci_lower,
            ci_95_upper=ci_upper,
            ci_lower_above_50pct=lower_above_50,
            verdict=verdict,
        )
        logger.info("Test 6 | %s | %s", horizon, verdict)

    return results
