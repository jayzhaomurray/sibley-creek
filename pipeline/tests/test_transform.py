"""Tests for the time-series transforms."""

from __future__ import annotations

import math

import numpy as np
import pandas as pd
import pytest

from pipeline.transform import (
    annualize_period_growth,
    index_to_base,
    moving_average,
    pct_change_at_horizon,
    qoq_annualized_pct,
    rebase_to_first,
    yoy_pct,
)


def _monthly_series(values: list[float], start: str = "2024-01-01") -> pd.Series:
    idx = pd.date_range(start=start, periods=len(values), freq="MS")
    return pd.Series(values, index=idx, name="value")


def test_yoy_pct_on_monthly_series():
    # 100 -> 102 a year later is +2.0% YoY.
    s = _monthly_series([100.0] * 12 + [102.0] * 12)
    yoy = yoy_pct(s, periods_per_year=12)
    # First 12 obs have no comparator
    assert yoy.iloc[:12].isna().all()
    assert yoy.iloc[12] == pytest.approx(2.0)
    assert yoy.iloc[-1] == pytest.approx(2.0)


def test_qoq_annualized_pct_matches_textbook():
    # 1% QoQ growth annualizes to (1.01)^4 - 1 = ~4.0604%
    q = pd.Series([100.0, 101.0])
    out = qoq_annualized_pct(q)
    assert math.isnan(out.iloc[0])
    assert out.iloc[1] == pytest.approx(((1.01 ** 4) - 1) * 100, rel=1e-9)


def test_annualize_period_growth_three_month_monthly():
    # 1% growth over 3 months annualizes to (1.01)^(12/3) - 1 = (1.01)^4 - 1
    s = _monthly_series([100.0, 100.0, 100.0, 101.0])
    out = annualize_period_growth(s, period_lag=3, periods_per_year=12)
    assert math.isnan(out.iloc[0])
    assert out.iloc[3] == pytest.approx(((1.01 ** 4) - 1) * 100, rel=1e-9)


def test_annualize_period_growth_validates_inputs():
    s = _monthly_series([1.0, 2.0])
    with pytest.raises(ValueError):
        annualize_period_growth(s, period_lag=0, periods_per_year=12)
    with pytest.raises(ValueError):
        annualize_period_growth(s, period_lag=3, periods_per_year=0)


def test_moving_average_strict_window():
    s = _monthly_series(list(range(1, 13)))  # 1..12
    ma = moving_average(s, window=3)
    # First two obs are NaN under strict min_periods=window=3
    assert ma.iloc[:2].isna().all()
    # Third obs is (1+2+3)/3 = 2.0
    assert ma.iloc[2] == pytest.approx(2.0)


def test_moving_average_with_min_periods():
    s = _monthly_series([1.0, 2.0, 3.0, 4.0])
    ma = moving_average(s, window=3, min_periods=1)
    # min_periods=1 emits a value from observation 0 onward
    assert not ma.isna().any()
    assert ma.iloc[0] == pytest.approx(1.0)


def test_pct_change_at_horizon_is_thin_wrapper():
    s = _monthly_series([100.0, 110.0])
    assert pct_change_at_horizon(s, 1).iloc[1] == pytest.approx(10.0)


def test_index_to_base_anchors_to_specified_date():
    idx = pd.date_range(start="2020-01-01", periods=4, freq="MS")
    s = pd.Series([50.0, 100.0, 150.0, 200.0], index=idx)
    out = index_to_base(s, base_value=100.0, base_date="2020-02-01")
    assert out.loc["2020-02-01"] == pytest.approx(100.0)
    assert out.loc["2020-01-01"] == pytest.approx(50.0)
    assert out.loc["2020-04-01"] == pytest.approx(200.0)


def test_index_to_base_falls_back_to_asof_for_missing_date():
    idx = pd.date_range(start="2020-01-01", periods=4, freq="MS")
    s = pd.Series([50.0, 100.0, 150.0, 200.0], index=idx)
    # Date between observations: should anchor on the prior observation (Feb 1).
    out = index_to_base(s, base_value=100.0, base_date="2020-02-15")
    assert out.loc["2020-02-01"] == pytest.approx(100.0)


def test_rebase_to_first_uses_first_valid():
    s = pd.Series([np.nan, 50.0, 100.0])
    out = rebase_to_first(s, base_value=100.0)
    # First valid is index 1 (value 50). After rebase: 50 -> 100, 100 -> 200.
    assert math.isnan(out.iloc[0])
    assert out.iloc[1] == pytest.approx(100.0)
    assert out.iloc[2] == pytest.approx(200.0)


def test_index_to_base_rejects_zero_anchor():
    s = pd.Series([0.0, 1.0, 2.0], index=pd.date_range("2020-01-01", periods=3, freq="MS"))
    with pytest.raises(ValueError, match="zero"):
        index_to_base(s)
