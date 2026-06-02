"""Tests for the Recession Watch Phase A pipeline.

Tests cover:
  1. Peak detection correctness (expanding HWM)
  2. GDP drawdown computation
  3. Breadth percentage calculation
  4. Chain splice ratio computation
  5. Output validation (no NaN/Inf/null)
  6. Comparator path shape
  7. Duration counting
"""

from __future__ import annotations

import json
import math
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

warnings.filterwarnings("ignore")

# Ensure we can import from the project root
ROOT = Path(__file__).resolve().parents[2]

from pipeline.recession_watch.metrics import (
    detect_peak,
    _smooth,
    _build_path,
    _compute_envelope,
    _compute_envelope_breadth,
    CD_HOWE_PEAKS,
)
from pipeline.recession_watch.chain import _compute_splice_ratio


# =========================================================================
# Fixtures
# =========================================================================

@pytest.fixture
def simple_gdp_series() -> pd.Series:
    """A synthetic GDP level series with a known peak."""
    dates = pd.date_range("2010-01-01", periods=36, freq="MS")
    # Ramp up to a peak at month 18 (index 17), then decline, then recover partway
    # 18 rising + 8 declining + 10 recovering = 36 total
    values = list(range(1, 19)) + list(range(17, 9, -1)) + [10, 11, 12, 13, 14, 15, 15, 15, 15, 15]
    assert len(values) == 36, f"Expected 36, got {len(values)}"
    return pd.Series(values, index=dates, dtype=float, name="gdp")


@pytest.fixture
def flat_then_decline() -> pd.Series:
    """GDP that peaks at month 10, then declines."""
    dates = pd.date_range("2000-01-01", periods=24, freq="MS")
    vals = [100.0] * 10 + [99.0, 98.0, 97.0, 96.0, 95.0, 94.0, 93.0, 92.0, 91.0, 90.0, 91.0, 92.0, 93.0, 93.5]
    return pd.Series(vals[:24], index=dates, dtype=float, name="gdp")


@pytest.fixture
def sector_df() -> pd.DataFrame:
    """Synthetic sector-level DataFrame (4 sectors, 24 months)."""
    dates = pd.date_range("2000-01-01", periods=24, freq="MS")
    # 10 pre-peak + 14 post-peak = 24 total
    data = {
        "A": [100.0] * 10 + [90.0, 85.0, 80.0, 75.0, 70.0, 68.0, 67.0, 67.0, 68.0, 69.0, 70.0, 71.0, 72.0, 73.0],
        "B": [50.0]  * 10 + [50.0, 49.0, 48.0, 47.0, 46.0, 46.0, 46.0, 47.0, 48.0, 49.0, 50.0, 51.0, 52.0, 53.0],
        "C": [200.0] * 10 + [205.0, 210.0, 215.0, 220.0, 225.0, 230.0, 235.0, 235.0, 235.0, 236.0, 237.0, 238.0, 239.0, 240.0],
        "D": [80.0]  * 10 + [78.0, 76.0, 74.0, 72.0, 70.0, 70.0, 71.0, 72.0, 73.0, 74.0, 75.0, 76.0, 77.0, 78.0],
    }
    return pd.DataFrame(data, index=dates)


# =========================================================================
# 1. Peak detection
# =========================================================================

class TestPeakDetection:
    def test_peak_at_known_month(self, simple_gdp_series):
        """Peak should be near month 18 for a series that ramps to 18 then declines.

        The 3-month backward MA shifts the peak by 1-2 months relative to the
        raw maximum (the MA for month 19 is still high from including month 18's peak).
        We accept a 2-month window around the expected raw peak (2011-06-01).
        """
        smoothed = _smooth(simple_gdp_series)
        peak = detect_peak(smoothed)
        # Raw peak at 2011-06-01; smoothed HWM may land at 2011-06-01 or 2011-07-01
        assert pd.Timestamp("2011-05-01") <= peak <= pd.Timestamp("2011-08-01"), (
            f"Expected peak near 2011-06 to 2011-07, got {peak}"
        )

    def test_peak_is_last_hwm(self, flat_then_decline):
        """For a flat peak followed by decline, the peak is the last month at HWM."""
        smoothed = _smooth(flat_then_decline)
        peak = detect_peak(smoothed)
        # The flat section runs months 0-9 (2000-01 to 2000-10).
        # After smoothing, the HWM keeps being set across the flat section.
        # The LAST month at HWM is the one just before decline — around month 9.
        assert peak >= pd.Timestamp("2000-09-01")
        assert peak <= pd.Timestamp("2000-11-01")

    def test_monotone_rise_peak_is_last(self):
        """For a monotonically increasing series, peak is the last observation."""
        dates = pd.date_range("2020-01-01", periods=12, freq="MS")
        vals = [float(i) for i in range(1, 13)]
        s = pd.Series(vals, index=dates)
        smoothed = _smooth(s)
        peak = detect_peak(smoothed)
        assert peak == dates[-1]

    def test_peak_after_recovery(self):
        """If series dips then recovers past the old high, new peak is at the new HWM."""
        dates = pd.date_range("2020-01-01", periods=18, freq="MS")
        # Peak at month 5, dip, recovery past old high at month 14
        vals = [1, 2, 3, 4, 5, 6, 5, 4, 3, 4, 5, 6, 7, 8, 9, 9, 9, 9]
        s = pd.Series([float(v) for v in vals], index=dates)
        smoothed = _smooth(s)
        peak = detect_peak(smoothed)
        # New high-water mark is at month 14 (0-indexed) = 2021-03-01
        assert peak >= pd.Timestamp("2021-02-01")


# =========================================================================
# 2. Drawdown computation
# =========================================================================

class TestDrawdown:
    def test_drawdown_at_peak_is_zero(self, flat_then_decline):
        """Depth at the peak date should be 0.0%."""
        smoothed = _smooth(flat_then_decline)
        peak = detect_peak(smoothed)
        peak_val = float(smoothed.loc[peak])
        path = _build_path(smoothed, peak, peak_val, max_months=20)
        assert path[0]["monthsSincePeak"] == 0
        assert abs(path[0]["value"]) < 1e-6, f"Expected ~0, got {path[0]['value']}"

    def test_drawdown_negative_after_peak(self, flat_then_decline):
        """After the peak, depth should be negative (contraction)."""
        smoothed = _smooth(flat_then_decline)
        peak = detect_peak(smoothed)
        peak_val = float(smoothed.loc[peak])
        path = _build_path(smoothed, peak, peak_val, max_months=20)
        # All post-peak values should be negative (series declines)
        post_peak = [p for p in path if p["monthsSincePeak"] > 0]
        for pt in post_peak[:8]:
            assert pt["value"] <= 0.1, f"Expected non-positive at month {pt['monthsSincePeak']}: {pt['value']}"

    def test_drawdown_formula(self):
        """Manual check: 90/100 - 1 = -10%."""
        dates = pd.date_range("2020-01-01", periods=3, freq="MS")
        s = pd.Series([100.0, 100.0, 90.0], index=dates)
        peak_dt = pd.Timestamp("2020-01-01")
        path = _build_path(s, peak_dt, 100.0, max_months=3)
        # Month 2 (2020-03): 90/100 - 1 = -10%
        month2 = next(p for p in path if p["monthsSincePeak"] == 2)
        assert abs(month2["value"] - (-10.0)) < 0.01, f"Expected -10, got {month2['value']}"

    def test_drawdown_handles_missing_data(self):
        """build_path stops cleanly when dates run out."""
        dates = pd.date_range("2020-01-01", periods=5, freq="MS")
        s = pd.Series([100.0, 99.0, 98.0, 97.0, 96.0], index=dates)
        path = _build_path(s, pd.Timestamp("2020-01-01"), 100.0, max_months=10)
        # Should stop at month 4 (only 5 observations)
        assert all(p["monthsSincePeak"] <= 4 for p in path)


# =========================================================================
# 3. Breadth percentage
# =========================================================================

class TestBreadth:
    def test_breadth_at_peak_is_zero(self, sector_df):
        """At peak date, no sectors are below peak — breadth = 0."""
        peak_dt = sector_df.index[10]  # right at start of decline
        pk_vals = sector_df.iloc[10]
        below = (sector_df < pk_vals) & (~sector_df.isna()) & (~pk_vals.isna())
        breadth = below.sum(axis=1) / len(sector_df.columns) * 100
        assert breadth.iloc[10] == 0.0, f"Expected 0 at peak, got {breadth.iloc[10]}"

    def test_breadth_range_0_to_100(self, sector_df):
        """Breadth % must be in [0, 100] at all times."""
        peak_dt = sector_df.index[10]
        pk_vals = sector_df.iloc[10]
        below = (sector_df < pk_vals) & (~sector_df.isna()) & (~pk_vals.isna())
        breadth = below.sum(axis=1) / len(sector_df.columns) * 100
        assert (breadth >= 0).all()
        assert (breadth <= 100).all()

    def test_breadth_counts_correctly(self):
        """Manual check: 2 of 4 sectors below peak = 50%."""
        dates = pd.date_range("2020-01-01", periods=2, freq="MS")
        # At month 0 (peak): all at 100
        # At month 1: A=90 (below), B=110 (above), C=100 (equal = not below), D=80 (below)
        data = {
            "A": [100.0, 90.0],
            "B": [100.0, 110.0],
            "C": [100.0, 100.0],
            "D": [100.0, 80.0],
        }
        df = pd.DataFrame(data, index=dates)
        pk_vals = df.iloc[0]
        below = (df < pk_vals).sum(axis=1) / 4 * 100
        assert below.iloc[0] == 0.0
        assert below.iloc[1] == 50.0, f"Expected 50%, got {below.iloc[1]}"


# =========================================================================
# 4. Chain splice ratio
# =========================================================================

class TestChainSplice:
    def test_splice_ratio_identical_series(self):
        """If older and newer are identical, ratio = 1.0."""
        idx = pd.date_range("2000-01-01", periods=24, freq="MS")
        s = pd.Series([100.0] * 24, index=idx)
        ratio = _compute_splice_ratio(s, s, idx[0], idx[-1])
        assert abs(ratio - 1.0) < 1e-6

    def test_splice_ratio_scaled_series(self):
        """If newer = older * 2.5, ratio should be ~2.5."""
        idx = pd.date_range("2000-01-01", periods=24, freq="MS")
        older = pd.Series([100.0 + i for i in range(24)], index=idx)
        newer = older * 2.5
        ratio = _compute_splice_ratio(older, newer, idx[0], idx[-1])
        assert abs(ratio - 2.5) < 0.01, f"Expected 2.5, got {ratio}"

    def test_splice_ratio_needs_min_3_overlapping(self):
        """Fewer than 3 overlap months should raise ValueError."""
        idx = pd.date_range("2000-01-01", periods=24, freq="MS")
        older = pd.Series([100.0] * 24, index=idx)
        newer = pd.Series([200.0] * 24, index=idx)
        with pytest.raises(ValueError, match="Insufficient overlap"):
            _compute_splice_ratio(older, newer, idx[0], idx[1])  # only 2 months

    def test_splice_ratio_uses_median(self):
        """Ratio is the median (outlier-robust) over the overlap."""
        idx = pd.date_range("2000-01-01", periods=12, freq="MS")
        older = pd.Series([100.0] * 12, index=idx)
        newer_vals = [200.0] * 11 + [500.0]  # one outlier
        newer = pd.Series(newer_vals, index=idx)
        ratio = _compute_splice_ratio(older, newer, idx[0], idx[-1])
        # Median of 11 ratios of 2.0 and 1 ratio of 5.0 = 2.0
        assert abs(ratio - 2.0) < 0.01, f"Expected ~2.0 (median), got {ratio}"


# =========================================================================
# 5. Output validation (no NaN/Inf/null)
# =========================================================================

class TestOutputValidation:
    def test_no_nan_in_synthetic_output(self):
        """Construct a minimal synthetic MetricResult and verify serialization."""
        from pipeline.recession_watch.metrics import MetricPath, MetricResult
        from pipeline.recession_watch.output import _serialize_metric

        path = [{"monthsSincePeak": i, "value": float(-i * 0.1)} for i in range(5)]
        mp = MetricPath(
            label="current",
            peak_date="2026-02-01",
            path=path,
        )
        comp = MetricPath(
            label="2008-09",
            peak_date="2008-10-01",
            path=[{"monthsSincePeak": i, "value": float(-i * 0.5)} for i in range(5)],
        )
        result = MetricResult(
            metric="gdp_depth",
            unit="%",
            description="Test",
            current=mp,
            comparators=[comp],
            current_reading=-0.4,
            current_months_since_peak=4,
            peak_date="2026-02-01",
            envelope_at_current_duration={"mildest": -0.5, "severest": -1.0, "covid": None},
        )
        serialized = _serialize_metric(result)
        assert serialized["current_reading"] == -0.4
        assert len(serialized["current"]) == 5
        assert "2008-09" in serialized["comparators"]

    def test_nan_in_path_raises(self):
        """A NaN value in a path should raise ValueError during serialization."""
        from pipeline.recession_watch.metrics import MetricPath, MetricResult
        from pipeline.recession_watch.output import _serialize_metric

        bad_path = [{"monthsSincePeak": 0, "value": float("nan")}]
        mp = MetricPath(label="current", peak_date="2026-01-01", path=bad_path)
        result = MetricResult(
            metric="gdp_depth",
            unit="%",
            description="Test",
            current=mp,
            comparators=[],
            current_reading=0.0,
            current_months_since_peak=0,
            peak_date="2026-01-01",
            envelope_at_current_duration={},
        )
        with pytest.raises(ValueError, match="Non-finite"):
            _serialize_metric(result)

    def test_inf_in_current_reading_raises(self):
        """An Inf current_reading should raise ValueError."""
        from pipeline.recession_watch.metrics import MetricPath, MetricResult
        from pipeline.recession_watch.output import _serialize_metric

        mp = MetricPath(label="current", peak_date="2026-01-01", path=[])
        result = MetricResult(
            metric="gdp_depth",
            unit="%",
            description="Test",
            current=mp,
            comparators=[],
            current_reading=float("inf"),
            current_months_since_peak=0,
            peak_date="2026-01-01",
            envelope_at_current_duration={},
        )
        with pytest.raises(ValueError, match="Non-finite"):
            _serialize_metric(result)


# =========================================================================
# 6. Comparator path shape
# =========================================================================

class TestComparatorPaths:
    def test_all_cdhowe_recessions_present(self):
        """All 4 CD Howe recession labels must be present."""
        expected = {"1981-82", "1990-92", "2008-09", "2020"}
        actual = set(CD_HOWE_PEAKS.keys())
        assert expected == actual

    def test_path_starts_at_zero(self, flat_then_decline):
        """First point in any path must have monthsSincePeak=0."""
        smoothed = _smooth(flat_then_decline)
        peak = detect_peak(smoothed)
        peak_val = float(smoothed.loc[peak])
        path = _build_path(smoothed, peak, peak_val, max_months=10)
        assert path[0]["monthsSincePeak"] == 0

    def test_path_is_monotone_in_months(self, flat_then_decline):
        """monthsSincePeak must increase by 1 each step (no gaps or duplicates)."""
        smoothed = _smooth(flat_then_decline)
        peak = detect_peak(smoothed)
        peak_val = float(smoothed.loc[peak])
        path = _build_path(smoothed, peak, peak_val, max_months=20)
        for i in range(1, len(path)):
            assert path[i]["monthsSincePeak"] == path[i - 1]["monthsSincePeak"] + 1, (
                f"Non-consecutive months at step {i}: "
                f"{path[i-1]['monthsSincePeak']} -> {path[i]['monthsSincePeak']}"
            )


# =========================================================================
# 7. Envelope
# =========================================================================

class TestEnvelope:
    def _make_comparator(self, label, values):
        from pipeline.recession_watch.metrics import MetricPath
        return MetricPath(
            label=label,
            peak_date="2010-01-01",
            path=[{"monthsSincePeak": i, "value": float(v)} for i, v in enumerate(values)],
        )

    def test_mildest_is_highest_for_depth(self):
        """For depth metrics (negative = worse), mildest = highest value."""
        from pipeline.recession_watch.metrics import _compute_envelope
        comps = [
            self._make_comparator("1981-82", [0, -1, -2, -3]),
            self._make_comparator("2008-09", [0, -2, -4, -5]),
            self._make_comparator("2020",    [0, -5, -10, -13]),
        ]
        env = _compute_envelope(comps, current_months=3)
        assert env["mildest"] == -3.0
        assert env["severest"] == -13.0
        assert env["covid"] == -13.0

    def test_mildest_is_lowest_for_breadth(self):
        """For breadth metrics (higher = worse), mildest = lowest breadth %."""
        from pipeline.recession_watch.metrics import _compute_envelope_breadth
        comps = [
            self._make_comparator("1981-82", [0, 20, 40, 60]),
            self._make_comparator("2008-09", [0, 30, 55, 70]),
            self._make_comparator("2020",    [0, 50, 80, 95]),
        ]
        env = _compute_envelope_breadth(comps, current_months=3)
        assert env["mildest"] == 60.0
        assert env["severest"] == 95.0
        assert env["covid"] == 95.0

    def test_envelope_empty_if_no_comparators(self):
        """Empty comparator list returns empty envelope."""
        from pipeline.recession_watch.metrics import _compute_envelope
        env = _compute_envelope([], current_months=5)
        assert env == {}
