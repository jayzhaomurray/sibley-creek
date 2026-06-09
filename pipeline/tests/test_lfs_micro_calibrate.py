"""Tests for pipeline.lfs_micro.calibrate — units-convention benchmark math.

Background (audit 2026-06-09): the BoC publishes INDINF_LFSMICRO_M in log
points (100*dlog); our headline is geometric percent ((exp(lp)-1)*100).
Mixing the conventions injects a level-dependent convexity bias.
calibrate._score_both_conventions scores lp-vs-lp (canonical) and
geo-vs-geo, never mixed. Pure-math tests — no downloads, no production data.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from pipeline.lfs_micro.calibrate import (
    _lp_to_geometric,
    _score,
    _score_both_conventions,
)


def _make_replication(lp_values: list[float]) -> pd.DataFrame:
    """Engine-output-shaped frame from underlying_lp values (natural-log units).

    underlying_pct is derived exactly as the engine does: (exp(lp)-1)*100.
    """
    dates = pd.date_range("2020-01-01", periods=len(lp_values), freq="MS")
    lp = np.asarray(lp_values, dtype=float)
    return pd.DataFrame({
        "date": dates.strftime("%Y-%m-01"),
        "underlying_lp": lp,
        "underlying_pct": (np.exp(lp) - 1.0) * 100.0,
    })


def _make_benchmark(lp100_values: list[float], n: int) -> pd.Series:
    """BoC-shaped benchmark: log points x100, indexed by YYYY-MM-01 strings."""
    dates = pd.date_range("2020-01-01", periods=n, freq="MS")
    return pd.Series(
        np.asarray(lp100_values, dtype=float),
        index=dates.strftime("%Y-%m-01"),
    )


class TestLpToGeometric:
    def test_known_value(self):
        # 3.5 log points -> (exp(0.035) - 1) * 100 = 3.56198...
        out = _lp_to_geometric([3.5])
        assert out[0] == pytest.approx((np.exp(0.035) - 1.0) * 100.0, abs=1e-12)
        assert out[0] == pytest.approx(3.56198, abs=1e-5)

    def test_zero_maps_to_zero(self):
        assert _lp_to_geometric([0.0])[0] == pytest.approx(0.0, abs=1e-15)

    def test_convexity_positive_above_lp(self):
        # exp()-1 > lp for lp > 0: the geometric value always exceeds the
        # log-point value (this wedge IS the old mixed-units bias).
        lp = np.array([1.0, 2.0, 3.5, 5.0])
        geo = _lp_to_geometric(lp)
        assert (geo > lp).all()
        # and the wedge grows with the level
        assert np.all(np.diff(geo - lp) > 0)


class TestScoreBothConventions:
    def test_exact_lp_match_scores_zero_in_both_conventions(self):
        # Ours in natural-log units; benchmark = exactly our lp x 100.
        lp = [0.030, 0.032, 0.035, 0.034, 0.036, 0.033,
              0.031, 0.035, 0.037, 0.034, 0.032, 0.030]
        rep = _make_replication(lp)
        bench = _make_benchmark([v * 100.0 for v in lp], len(lp))

        both = _score_both_conventions(rep, bench)
        assert both["lp"]["rmse"] == pytest.approx(0.0, abs=1e-9)
        assert both["geo"]["rmse"] == pytest.approx(0.0, abs=1e-9)
        assert both["lp"]["n_overlap"] == len(lp)

    def test_mixed_units_comparison_shows_convexity_bias(self):
        # Same exact-match series: the OLD mixed comparison (our geometric
        # pct vs BoC lp as published) is biased by the convexity wedge,
        # while both same-units comparisons are exact. This is the audit
        # finding that motivated the change.
        lp = [0.035] * 12
        rep = _make_replication(lp)
        bench = _make_benchmark([3.5] * 12, 12)

        both = _score_both_conventions(rep, bench)
        mixed = _score(rep, bench, col="underlying_pct")  # mixed units (old)

        wedge = (np.exp(0.035) - 1.0) * 100.0 - 3.5  # ~0.062pp
        assert both["lp"]["rmse"] == pytest.approx(0.0, abs=1e-9)
        assert both["geo"]["rmse"] == pytest.approx(0.0, abs=1e-9)
        # _score rounds to 4 decimals
        assert mixed["rmse"] == pytest.approx(wedge, abs=1e-4)
        assert mixed["rmse"] > 0.05

    def test_known_offset_recovered_in_lp_units(self):
        # ours lp100 = benchmark + 0.05pp uniformly -> lp RMSE 0.05 exactly.
        lp = [0.030, 0.032, 0.035, 0.034, 0.036, 0.033,
              0.031, 0.035, 0.037, 0.034, 0.032, 0.030]
        rep = _make_replication(lp)
        bench = _make_benchmark([v * 100.0 - 0.05 for v in lp], len(lp))

        both = _score_both_conventions(rep, bench)
        assert both["lp"]["rmse"] == pytest.approx(0.05, abs=1e-9)
        assert both["lp"]["mae"] == pytest.approx(0.05, abs=1e-9)

    def test_empty_replication_returns_nan_scores(self):
        bench = _make_benchmark([3.5] * 12, 12)
        both = _score_both_conventions(pd.DataFrame(), bench)
        assert np.isnan(both["lp"]["rmse"])
        assert np.isnan(both["geo"]["rmse"])
        assert both["lp"]["n_overlap"] == 0
