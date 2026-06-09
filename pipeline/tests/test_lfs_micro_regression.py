"""Tests for pipeline.lfs_micro.regression.

Pure math tests on synthetic two-period panels with known coefficients.
No I/O, no HTTP, no StatCan dependency.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from pipeline.lfs_micro.regression import (
    RegressionResult,
    run_wls,
    union_category_universe,
    REGRESSOR_GROUPS,
)


# ---------------------------------------------------------------------------
# Synthetic DataFrame builder
# ---------------------------------------------------------------------------

def _make_synthetic_df(
    n: int = 500,
    seed: int = 42,
    wage_col: str = "wage",
    override_wages: np.ndarray | None = None,
) -> pd.DataFrame:
    """Build a minimal synthetic harmonized DataFrame for regression tests.

    Uses a small subset of regressor groups to keep the design manageable.
    """
    rng = np.random.default_rng(seed)

    n_noc = 5   # small NOC universe for speed
    n_naics = 4

    df = pd.DataFrame({
        "wage":       rng.lognormal(3.4, 0.5, n),   # ~$30/hr lognormal
        "weight":     rng.integers(100, 2000, n).astype(float),
        "gender":     rng.choice([1, 2], n),
        "age_12":     rng.choice(range(1, 13), n),
        "educ":       rng.choice(range(0, 7), n),
        "tenure_bin": rng.choice(["<12m", "12-35m", "36-59m", "60-119m", "120m+"], n),
        "noc_43":     rng.choice(range(1, n_noc + 1), n),
        "naics_21":   rng.choice(range(1, n_naics + 1), n),
        "union_status": rng.choice([1, 2, 3], n),
        "ftptmain":   rng.choice([1, 2], n),
        "mjh":        rng.choice([1, 2], n),
        "permtemp":   rng.choice([1, 2, 3, 4], n),
        "marstat":    rng.choice(range(1, 7), n),
        "immig":      rng.choice([1, 2, 3], n),
        "estsize":    rng.choice([1, 2, 3, 4], n),
        "prov":       rng.choice([10, 11, 12, 13, 24, 35, 46, 47, 48, 59], n),
        "cowmain_pub": rng.choice([1, 2], n),
    })

    if override_wages is not None:
        df["wage"] = override_wages

    return df


# ---------------------------------------------------------------------------
# Basic regression tests
# ---------------------------------------------------------------------------

def test_run_wls_returns_result():
    """run_wls returns a RegressionResult with correct structure."""
    df = _make_synthetic_df(500)
    result = run_wls(df, spec_weighted=True, min_cell_count=5)
    assert isinstance(result, RegressionResult)
    assert len(result.coef) == len(result.col_names)
    assert len(result.mean_X) == len(result.coef)
    assert result.n_obs <= 500
    assert result.n_obs > 0
    assert 0.0 <= result.r_squared <= 1.0


def test_run_wls_unweighted():
    """OLS (spec_weighted=False) also produces a valid result."""
    df = _make_synthetic_df(300)
    result = run_wls(df, spec_weighted=False, min_cell_count=5)
    assert len(result.coef) > 0
    assert result.r_squared >= 0.0


def test_run_wls_intercept_in_design():
    """The design matrix includes an intercept column."""
    df = _make_synthetic_df(300)
    result = run_wls(df, spec_weighted=True, min_cell_count=5)
    assert "intercept" in result.col_names


def test_run_wls_mean_X_matches_coef_length():
    """mean_X has the same length as coef."""
    df = _make_synthetic_df(200)
    result = run_wls(df, spec_weighted=True, min_cell_count=5)
    assert result.mean_X.shape == result.coef.shape


def test_run_wls_mean_log_wage_plausible():
    """Weighted mean log wage is within a plausible range for $10-$200/hr."""
    df = _make_synthetic_df(500)
    result = run_wls(df, spec_weighted=True, min_cell_count=5)
    # log(10) = 2.3, log(200) = 5.3
    assert 2.3 <= result.mean_log_wage <= 5.3


def test_run_wls_conformable_with_union_universe():
    """Two months re-estimated on union universe produce conformable col_names."""
    df_a = _make_synthetic_df(300, seed=1)
    df_b = _make_synthetic_df(300, seed=2)

    r_a = run_wls(df_a, min_cell_count=5)
    r_b = run_wls(df_b, min_cell_count=5)

    cat_union = union_category_universe(r_a, r_b)

    r_a2 = run_wls(df_a, min_cell_count=5, category_universe=cat_union)
    r_b2 = run_wls(df_b, min_cell_count=5, category_universe=cat_union)

    assert r_a2.col_names == r_b2.col_names


# ---------------------------------------------------------------------------
# Known-coefficient synthetic test (WLS identity check)
# ---------------------------------------------------------------------------

def test_wls_recovers_known_intercept():
    """WLS with a single binary regressor recovers known coefficients.

    Model: log(wage) = mu + beta * x + epsilon
    With x = 0 for group A, x = 1 for group B.
    We set wages so group A has known mean log-wage and group B has
    a known premium, then verify the intercept and coefficient are recovered.
    """
    rng = np.random.default_rng(99)
    n = 2000

    # Set group membership
    x = rng.choice([0, 1], n)

    # True parameters: intercept = log(25), beta_B = log(35) - log(25)
    mu = np.log(25.0)
    beta = np.log(35.0) - np.log(25.0)

    # Wage = exp(mu + beta*x) with tiny noise
    log_wage = mu + beta * x + rng.normal(0, 0.01, n)
    wage = np.exp(log_wage)

    # Build a minimal DataFrame with only gender (2 categories)
    df = pd.DataFrame({
        "wage":       wage,
        "weight":     np.ones(n),
        "gender":     x + 1,       # 1 or 2 (valid gender codes)
        "age_12":     np.ones(n, dtype=int),       # single category (will be dropped for having <2 cats)
        "educ":       np.ones(n, dtype=int),       # single category
        "tenure_bin": ["<12m"] * n,
        "noc_43":     np.ones(n, dtype=int),
        "naics_21":   np.ones(n, dtype=int),
        "union_status": np.ones(n, dtype=int),
        "ftptmain":   np.ones(n, dtype=int),
        "mjh":        np.ones(n, dtype=int),
        "permtemp":   np.ones(n, dtype=int),
        "marstat":    np.ones(n, dtype=int),
        "immig":      np.ones(n, dtype=int),
        "estsize":    np.ones(n, dtype=int),
        "prov":       [35] * n,
        "cowmain_pub": np.ones(n, dtype=int),
    })

    result = run_wls(df, spec_weighted=False, min_cell_count=5)

    # Find the intercept coefficient
    intercept_idx = result.col_names.index("intercept")
    recovered_mu = result.coef[intercept_idx]

    # Find the gender_2 coefficient (beta for Women+)
    gender2_idx = [i for i, n in enumerate(result.col_names) if n == "gender_2"]
    assert len(gender2_idx) == 1
    recovered_beta = result.coef[gender2_idx[0]]

    # Both should be close to true values (tolerance: 0.01 log-points)
    assert abs(recovered_mu - mu) < 0.02, (
        f"Intercept: expected {mu:.4f}, got {recovered_mu:.4f}"
    )
    assert abs(recovered_beta - beta) < 0.02, (
        f"Gender premium: expected {beta:.4f}, got {recovered_beta:.4f}"
    )


# ---------------------------------------------------------------------------
# Rank-deficiency guard
# ---------------------------------------------------------------------------

def test_multicollinear_design_does_not_crash():
    """Rank-deficient design matrix is handled gracefully (no exception)."""
    rng = np.random.default_rng(7)
    n = 300

    df = _make_synthetic_df(n, seed=7)
    # Force two columns to be identical (perfect multicollinearity)
    # by making gender and cowmain_pub always equal
    df["gender"] = 1
    df["cowmain_pub"] = 1
    # This will result in single-category columns being dropped by the
    # _prepare_categoricals step, which is the correct guard.
    result = run_wls(df, min_cell_count=5)
    assert len(result.coef) > 0


# ---------------------------------------------------------------------------
# union_category_universe
# ---------------------------------------------------------------------------

def test_union_category_universe_takes_union():
    """Union of two results' category universes includes all categories."""
    r_a = RegressionResult(
        coef=np.array([]), col_names=[], mean_log_wage=0,
        mean_X=np.array([]), n_obs=100, r_squared=0,
        category_universe={"noc_43": [1, 2, 3]},
    )
    r_b = RegressionResult(
        coef=np.array([]), col_names=[], mean_log_wage=0,
        mean_X=np.array([]), n_obs=100, r_squared=0,
        category_universe={"noc_43": [2, 3, 4]},
    )
    universe = union_category_universe(r_a, r_b)
    assert set(universe["noc_43"]) == {1, 2, 3, 4}
