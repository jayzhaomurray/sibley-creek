"""Unit tests for the USDCAD adversarial validation suite.

Tests cover:
- Bootstrap null distribution logic (Test 3 internals)
- Block bootstrap CI construction (Test 6 internals)
- Synthetic null X generation (Test 2 internals)
- Report builder with known inputs (no compute required)

End-to-end tests are excluded -- they take ~9 minutes per horizon run and
are covered by running the validation suite itself.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

# Add project root
_root = Path(__file__).parents[4]
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))


class TestBootstrapNull:
    """Test 3: bootstrap null distribution for hit rates."""

    def test_null_mean_near_50_pct(self):
        """Bootstrap draws under H0 should average ~50% hit rate."""
        from pipeline.usdcad.validation.adversarial import _bootstrap_null_hit_rate
        null_dist = _bootstrap_null_hit_rate(200, 200, seed=0, n_bootstrap=2000)
        mean_null = np.mean(null_dist)
        assert abs(mean_null - 0.50) < 0.02, f"Null mean {mean_null:.3f} too far from 0.5"

    def test_high_obs_has_low_p_value(self):
        """A 70% hit rate on 200 obs should have p < 0.001 under H0."""
        from pipeline.usdcad.validation.adversarial import _bootstrap_null_hit_rate
        null_dist = _bootstrap_null_hit_rate(200, 200, seed=42, n_bootstrap=5000)
        obs_hit = 0.70
        raw_p = sum(1 for x in null_dist if x >= obs_hit) / len(null_dist)
        assert raw_p < 0.001, f"p={raw_p:.4f} is too high for 70% hit on n=200"

    def test_50_pct_obs_not_significant(self):
        """A 50% hit rate should have p > 0.40."""
        from pipeline.usdcad.validation.adversarial import _bootstrap_null_hit_rate
        null_dist = _bootstrap_null_hit_rate(200, 200, seed=42, n_bootstrap=2000)
        obs_hit = 0.50
        raw_p = sum(1 for x in null_dist if x >= obs_hit) / len(null_dist)
        assert raw_p > 0.40, f"p={raw_p:.4f} for 50% hit should be > 0.40"

    def test_output_length_matches_n_bootstrap(self):
        from pipeline.usdcad.validation.adversarial import _bootstrap_null_hit_rate
        result = _bootstrap_null_hit_rate(100, 100, seed=0, n_bootstrap=500)
        assert len(result) == 500

    def test_deterministic_with_same_seed(self):
        from pipeline.usdcad.validation.adversarial import _bootstrap_null_hit_rate
        r1 = _bootstrap_null_hit_rate(100, 100, seed=7, n_bootstrap=200)
        r2 = _bootstrap_null_hit_rate(100, 100, seed=7, n_bootstrap=200)
        assert r1 == r2


class TestBlockBootstrap:
    """Test 6: stationary block bootstrap CI."""

    def test_ci_contains_true_mean(self):
        """The 95% CI should contain the true mean of the indicator series."""
        from pipeline.usdcad.validation.adversarial import _stationary_block_bootstrap
        # 65% hit rate series
        rng = np.random.RandomState(42)
        data = rng.binomial(1, 0.65, 200).astype(float)
        obs_mean = data.mean()
        bstraps = _stationary_block_bootstrap(data, block_size=10, n_bootstrap=2000, seed=42)
        ci_lo = np.percentile(bstraps, 2.5)
        ci_hi = np.percentile(bstraps, 97.5)
        assert ci_lo <= obs_mean <= ci_hi, (
            f"CI [{ci_lo:.3f}, {ci_hi:.3f}] does not contain obs mean {obs_mean:.3f}"
        )

    def test_ci_wider_than_iid_bootstrap(self):
        """Block bootstrap CI should be >= iid bootstrap CI for autocorrelated data."""
        from pipeline.usdcad.validation.adversarial import _stationary_block_bootstrap
        # Generate autocorrelated 0/1 series: runs of 1s and 0s
        data = np.array([1] * 10 + [0] * 10 + [1] * 10 + [0] * 10 + [1] * 10 +
                        [0] * 10 + [1] * 10 + [0] * 10 + [1] * 10 + [0] * 10, dtype=float)
        assert len(data) == 100

        # Block bootstrap (block=10, respects autocorrelation)
        b_block = _stationary_block_bootstrap(data, block_size=10, n_bootstrap=2000, seed=42)
        ci_block = np.percentile(b_block, 97.5) - np.percentile(b_block, 2.5)

        # iid bootstrap (block=1, ignores autocorrelation)
        b_iid = _stationary_block_bootstrap(data, block_size=1, n_bootstrap=2000, seed=42)
        ci_iid = np.percentile(b_iid, 97.5) - np.percentile(b_iid, 2.5)

        # Block CI should be wider (more conservative) than iid for autocorrelated data
        assert ci_block >= ci_iid * 0.9, (
            f"Block CI width {ci_block:.4f} should be >= iid CI width {ci_iid:.4f}"
        )

    def test_deterministic_with_same_seed(self):
        from pipeline.usdcad.validation.adversarial import _stationary_block_bootstrap
        data = np.array([1, 0, 1, 1, 0] * 40, dtype=float)
        r1 = _stationary_block_bootstrap(data, block_size=5, n_bootstrap=100, seed=99)
        r2 = _stationary_block_bootstrap(data, block_size=5, n_bootstrap=100, seed=99)
        assert r1 == r2

    def test_output_values_in_01_range(self):
        from pipeline.usdcad.validation.adversarial import _stationary_block_bootstrap
        data = np.array([1, 0, 1, 1, 0, 0, 1, 1, 0, 1] * 20, dtype=float)
        bstraps = _stationary_block_bootstrap(data, block_size=5, n_bootstrap=200, seed=0)
        assert all(0.0 <= v <= 1.0 for v in bstraps), "Bootstrap means must be in [0,1]"


class TestSyntheticNullX:
    """Test 2: covariance-preserving synthetic X generation."""

    def test_output_shape_matches_input(self):
        from pipeline.usdcad.validation.adversarial import _simulate_null_X
        rng = np.random.RandomState(0)
        X_real = pd.DataFrame(
            rng.randn(500, 10),
            columns=[f"var_{i}" for i in range(10)]
        )
        X_null = _simulate_null_X(X_real, seed=0)
        assert X_null.shape == X_real.shape

    def test_output_columns_preserved(self):
        from pipeline.usdcad.validation.adversarial import _simulate_null_X
        rng = np.random.RandomState(0)
        X_real = pd.DataFrame(
            rng.randn(200, 5),
            columns=["A", "B", "C", "D", "E"]
        )
        X_null = _simulate_null_X(X_real, seed=0)
        assert list(X_null.columns) == list(X_real.columns)

    def test_output_index_preserved(self):
        from pipeline.usdcad.validation.adversarial import _simulate_null_X
        idx = pd.date_range("2005-01-01", periods=100)
        X_real = pd.DataFrame(np.random.randn(100, 5), index=idx)
        X_null = _simulate_null_X(X_real, seed=0)
        assert list(X_null.index) == list(X_real.index)

    def test_marginal_mean_approximately_preserved(self):
        """Simulated X should have approximately the same column means as real X."""
        from pipeline.usdcad.validation.adversarial import _simulate_null_X
        rng = np.random.RandomState(0)
        X_real = pd.DataFrame(
            rng.randn(1000, 5) * 2 + 3,  # mean ~3, std ~2
            columns=list("ABCDE")
        )
        X_null = _simulate_null_X(X_real, seed=0)
        real_means = X_real.mean()
        null_means = X_null.mean()
        for col in X_real.columns:
            assert abs(real_means[col] - null_means[col]) < 1.0, (
                f"Column {col}: real mean {real_means[col]:.2f} vs null mean {null_means[col]:.2f}"
            )

    def test_no_nan_in_output(self):
        from pipeline.usdcad.validation.adversarial import _simulate_null_X
        rng = np.random.RandomState(0)
        X_real = pd.DataFrame(rng.randn(200, 8), columns=[f"v{i}" for i in range(8)])
        # Inject some NaN into X_real (as in the real data)
        X_real.iloc[5:10, 2] = np.nan
        X_null = _simulate_null_X(X_real, seed=0)
        assert not X_null.isna().any().any(), "Synthetic X should not contain NaN"

    def test_deterministic_with_same_seed(self):
        from pipeline.usdcad.validation.adversarial import _simulate_null_X
        rng = np.random.RandomState(1)
        X_real = pd.DataFrame(rng.randn(100, 4), columns=list("WXYZ"))
        X1 = _simulate_null_X(X_real, seed=5)
        X2 = _simulate_null_X(X_real, seed=5)
        pd.testing.assert_frame_equal(X1, X2)


class TestReportBuilder:
    """Report builder: check structure and handling of empty/partial results."""

    def test_empty_results_produces_not_run_stubs(self):
        from pipeline.usdcad.validation.report import build_report
        text = build_report({}, {})
        assert "Test 1 was not run" in text
        assert "Test 2 was not run" in text
        assert "Test 3 was not run" in text
        assert "Test 4 was not run" in text
        assert "Test 5 was not run" in text
        assert "Test 6 was not run" in text

    def test_fast_mode_banner_present(self):
        from pipeline.usdcad.validation.report import build_report
        text = build_report({}, {}, fast_mode=True)
        assert "FAST MODE" in text

    def test_overall_verdict_section_present(self):
        from pipeline.usdcad.validation.report import build_report
        text = build_report({}, {})
        assert "## Overall Verdict by Horizon" in text

    def test_all_three_horizons_in_overall_verdict(self):
        from pipeline.usdcad.validation.report import build_report
        text = build_report({}, {})
        assert "### Weekly" in text
        assert "### Monthly" in text
        assert "### Quarterly" in text

    def test_fmt_nan_renders_as_na(self):
        from pipeline.usdcad.validation.report import _fmt
        assert _fmt(float("nan")) == "n/a"
        assert _fmt(float("nan"), pct=True) == "n/a"

    def test_edge_str_sign_prefix(self):
        from pipeline.usdcad.validation.report import _edge_str
        assert _edge_str(5.3).startswith("+")
        assert _edge_str(-2.1).startswith("-")
        assert _edge_str(float("nan")) == "n/a"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
