"""Recession Watch metric computations.

Four metrics, all anchored to a single GDP-defined cycle peak:

  GDP depth      = (3mo-MA GDP level / peak level - 1), %
  GDP breadth    = % of comparator-grade sectors below their peak-date level, %
  Emp depth      = (3mo-MA employment / employment at GDP peak date - 1), %
  Emp breadth    = % of 16 LFS sectors below their GDP-peak-date level, %

Plus:
  Fine GDP breadth = % of ~84 3-digit NAICS industries below peak (1997+ only).

Peak detection
--------------
The cycle clock is the expanding high-water mark of the 3-month moving average
of the all-industries GDP level. The peak = last month at which the 3mo-MA set
a new all-time high (expanding max). Duration = months since peak.

For the CURRENT episode, the peak is the most recent all-time high.
For COMPARATOR recessions, the CD Howe Business Cycle Council peak dates are
used directly — these are authoritative and we calibrate/verify that our
HWM method agrees within 1 month.

CD Howe peak dates (verified):
  1981-06  1990-03  2008-10  2020-02

Comparator envelopes
--------------------
For each metric and each recession, we compute a path of length
{0, 1, 2, ..., max_months} where month 0 is the peak. The envelope is:
  - mildest path (highest value = least negative depth)
  - most severe path (lowest value = most negative depth)
  - COVID path (labelled separately; usually the outlier)

Output format
-------------
One dict per metric:
  {
    "current": [{"monthsSincePeak": 0, "value": 0.0}, ...],
    "comparators": {
      "1981-82": [{"monthsSincePeak": 0, "value": 0.0}, ...],
      ...
    },
    "current_reading": -0.001,
    "current_months_since_peak": 4,
    "envelope_at_current_duration": {
      "mildest": -0.017,
      "severest": -0.131,
      "covid": -0.131
    }
  }
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[2]

# CD Howe recession peak dates (authoritative)
# Label -> peak date
CD_HOWE_PEAKS = {
    "1981-82": pd.Timestamp("1981-06-01"),
    "1990-92": pd.Timestamp("1990-03-01"),
    "2008-09": pd.Timestamp("2008-10-01"),
    "2020":    pd.Timestamp("2020-02-01"),
}

COMPARATOR_LABELS = list(CD_HOWE_PEAKS.keys())

# Smoothing window for depth metrics
SMOOTH_WINDOW = 3

# Minimum depth threshold before duration clock starts ticking
DURATION_START_THRESHOLD = -0.002   # -0.2%


@dataclass
class MetricPath:
    """Path of a metric from peak for one episode."""
    label: str                        # "current" or recession label
    peak_date: str                    # ISO date
    path: list[dict]                  # [{monthsSincePeak: int, value: float}]
    trough_depth: Optional[float] = None    # deepest point in path
    trough_month: Optional[int] = None     # months since peak at trough


@dataclass
class MetricResult:
    """All data for one metric (depth or breadth)."""
    metric: str                       # "gdp_depth" | "gdp_breadth" | "emp_depth" | "emp_breadth"
    unit: str                         # "%" | "% of sectors"
    description: str
    current: MetricPath
    comparators: list[MetricPath]
    current_reading: float            # latest value
    current_months_since_peak: int
    peak_date: str                    # ISO date of current peak
    envelope_at_current_duration: dict  # {mildest, severest, covid}


def _smooth(series: pd.Series, window: int = SMOOTH_WINDOW) -> pd.Series:
    """3-month centred moving average (min_periods=1 for endpoints)."""
    return series.rolling(window, center=False, min_periods=1).mean()


def detect_peak(gdp_smoothed: pd.Series) -> pd.Timestamp:
    """Find the current cycle peak = last date the smoothed GDP set a new HWM.

    The expanding high-water mark is the running maximum. The peak is the
    most recent date at which the series equalled its own running maximum —
    i.e. the last month at which a new high was set.
    """
    hwm = gdp_smoothed.expanding().max()
    # Peak = last date where level == hwm (i.e. a new high was set)
    at_hwm = gdp_smoothed[gdp_smoothed >= hwm - 1e-9]
    if at_hwm.empty:
        raise ValueError("Cannot detect peak: no HWM observations")
    return at_hwm.index[-1]


def _peak_from_cdhowe(label: str) -> pd.Timestamp:
    return CD_HOWE_PEAKS[label]


def _build_path(
    series: pd.Series,
    peak_date: pd.Timestamp,
    reference_value: float,
    max_months: int = 48,
    as_pct: bool = True,
) -> list[dict]:
    """Build a months-since-peak path for a metric.

    Args:
        series: the metric value series (level or breadth %)
        peak_date: date of the cycle peak (month 0)
        reference_value: the peak-date value (used to compute deviation)
        max_months: how many months forward to trace
        as_pct: if True, return (value / reference_value - 1) * 100;
                if False, return value as-is (for breadth %)
    """
    path = []
    for m in range(max_months + 1):
        dt = peak_date + pd.DateOffset(months=m)
        # Find the closest available date
        try:
            idx = series.index.searchsorted(dt)
            if idx >= len(series.index):
                break
            dt_actual = series.index[idx]
            # Only accept if within 15 days (monthly data)
            if abs((dt_actual - dt).days) > 15:
                break
            value = float(series.iloc[idx])
            if not np.isfinite(value):
                continue
            if as_pct:
                pct = (value / reference_value - 1) * 100
            else:
                pct = value  # already a percentage (breadth)
            path.append({"monthsSincePeak": m, "value": round(pct, 4)})
        except (IndexError, KeyError):
            break
    return path


def compute_gdp_depth(
    gdp_level: pd.Series,
    current_peak: pd.Timestamp,
) -> MetricResult:
    """GDP depth for current episode + 4 comparator recessions.

    gdp_level: the chained back-history level series (1981-present), any scale.
    """
    smoothed = _smooth(gdp_level)

    # Current episode
    peak_val = float(smoothed.loc[current_peak])
    current_path = _build_path(smoothed, current_peak, peak_val, max_months=36)
    current_reading = current_path[-1]["value"] if current_path else 0.0
    current_months = current_path[-1]["monthsSincePeak"] if current_path else 0

    # Comparator episodes
    comparators = []
    for label, peak_dt in CD_HOWE_PEAKS.items():
        if peak_dt not in smoothed.index and peak_dt < smoothed.index.min():
            logger.warning("Comparator %s peak %s before series start — skipping", label, peak_dt)
            continue
        # Use nearest available date
        idx = smoothed.index.searchsorted(peak_dt)
        if idx >= len(smoothed.index):
            continue
        pk_actual = smoothed.index[idx]
        pk_val = float(smoothed.iloc[idx])
        path = _build_path(smoothed, pk_actual, pk_val, max_months=48)
        trough = min((p["value"] for p in path), default=0.0)
        trough_m = next((p["monthsSincePeak"] for p in path if p["value"] == trough), None)
        comparators.append(MetricPath(
            label=label,
            peak_date=str(pk_actual.date()),
            path=path,
            trough_depth=round(trough, 4),
            trough_month=trough_m,
        ))

    # Envelope at current duration
    envelope = _compute_envelope(comparators, current_months)

    return MetricResult(
        metric="gdp_depth",
        unit="%",
        description="Real GDP level vs peak (3mo MA), %",
        current=MetricPath(
            label="current",
            peak_date=str(current_peak.date()),
            path=current_path,
            trough_depth=min((p["value"] for p in current_path), default=0.0),
            trough_month=None,
        ),
        comparators=comparators,
        current_reading=round(current_reading, 4),
        current_months_since_peak=current_months,
        peak_date=str(current_peak.date()),
        envelope_at_current_duration=envelope,
    )


def compute_gdp_breadth(
    sector_levels: pd.DataFrame,
    current_peak: pd.Timestamp,
) -> MetricResult:
    """Comparator-grade GDP breadth using the common sector set (1981+).

    Breadth = % of sectors whose current level is below their level at the GDP peak date.
    """
    # For each date, count sectors below peak-date level
    peak_idx = sector_levels.index.searchsorted(current_peak)
    if peak_idx >= len(sector_levels.index):
        raise ValueError(f"Peak date {current_peak} is beyond sector_levels index")
    peak_actual = sector_levels.index[peak_idx]
    peak_levels = sector_levels.iloc[peak_idx]

    n_sectors = len(sector_levels.columns)

    def _breadth_series(pk_dt: pd.Timestamp) -> pd.Series:
        """Compute monthly breadth from a given peak date."""
        idx = sector_levels.index.searchsorted(pk_dt)
        if idx >= len(sector_levels.index):
            return pd.Series(dtype=float)
        pk_vals = sector_levels.iloc[idx]
        # Breadth = fraction below peak, as %
        below = (sector_levels < pk_vals) & (~sector_levels.isna()) & (~pk_vals.isna())
        breadth = below.sum(axis=1) / n_sectors * 100
        return breadth

    # Current episode
    breadth_all = _breadth_series(peak_actual)
    current_path = _build_path(breadth_all, peak_actual, 1.0, max_months=36, as_pct=False)
    current_reading = current_path[-1]["value"] if current_path else 0.0
    current_months = current_path[-1]["monthsSincePeak"] if current_path else 0

    # Comparator episodes
    comparators = []
    for label, peak_dt in CD_HOWE_PEAKS.items():
        idx = sector_levels.index.searchsorted(peak_dt)
        if idx >= len(sector_levels.index):
            continue
        pk_actual = sector_levels.index[idx]
        breadth_c = _breadth_series(pk_actual)
        path = _build_path(breadth_c, pk_actual, 1.0, max_months=48, as_pct=False)
        peak_breadth = path[0]["value"] if path else 0.0
        trough = max((p["value"] for p in path), default=0.0)  # higher = more breadth = worse
        trough_m = next((p["monthsSincePeak"] for p in path if p["value"] == trough), None)
        comparators.append(MetricPath(
            label=label,
            peak_date=str(pk_actual.date()),
            path=path,
            trough_depth=round(trough, 2),
            trough_month=trough_m,
        ))

    envelope = _compute_envelope_breadth(comparators, current_months)

    return MetricResult(
        metric="gdp_breadth",
        unit="% of sectors",
        description=f"% of {n_sectors} common GDP sectors below peak-date level",
        current=MetricPath(
            label="current",
            peak_date=str(peak_actual.date()),
            path=current_path,
            trough_depth=max((p["value"] for p in current_path), default=0.0),
            trough_month=None,
        ),
        comparators=comparators,
        current_reading=round(current_reading, 2),
        current_months_since_peak=current_months,
        peak_date=str(peak_actual.date()),
        envelope_at_current_duration=envelope,
    )


def compute_employment_depth(
    emp_level: pd.Series,
    current_peak: pd.Timestamp,
) -> MetricResult:
    """Employment depth, anchored to the GDP-defined peak date."""
    smoothed = _smooth(emp_level)

    # Use GDP peak as the anchor — find nearest available date in employment series
    idx = smoothed.index.searchsorted(current_peak)
    if idx >= len(smoothed.index):
        raise ValueError(f"GDP peak {current_peak} beyond employment index")
    emp_peak_dt = smoothed.index[idx]
    if abs((emp_peak_dt - current_peak).days) > 45:
        logger.warning(
            "Employment peak date %s differs from GDP peak %s by %d days",
            emp_peak_dt, current_peak, abs((emp_peak_dt - current_peak).days)
        )
    emp_peak_val = float(smoothed.iloc[idx])

    current_path = _build_path(smoothed, emp_peak_dt, emp_peak_val, max_months=36)
    current_reading = current_path[-1]["value"] if current_path else 0.0
    current_months = current_path[-1]["monthsSincePeak"] if current_path else 0

    comparators = []
    for label, gdp_peak_dt in CD_HOWE_PEAKS.items():
        idx = smoothed.index.searchsorted(gdp_peak_dt)
        if idx >= len(smoothed.index):
            continue
        emp_pk_dt = smoothed.index[idx]
        emp_pk_val = float(smoothed.iloc[idx])
        path = _build_path(smoothed, emp_pk_dt, emp_pk_val, max_months=48)
        trough = min((p["value"] for p in path), default=0.0)
        trough_m = next((p["monthsSincePeak"] for p in path if p["value"] == trough), None)
        comparators.append(MetricPath(
            label=label,
            peak_date=str(emp_pk_dt.date()),
            path=path,
            trough_depth=round(trough, 4),
            trough_month=trough_m,
        ))

    envelope = _compute_envelope(comparators, current_months)

    return MetricResult(
        metric="emp_depth",
        unit="%",
        description="Total employment vs GDP-peak level (3mo MA), %",
        current=MetricPath(
            label="current",
            peak_date=str(emp_peak_dt.date()),
            path=current_path,
            trough_depth=min((p["value"] for p in current_path), default=0.0),
            trough_month=None,
        ),
        comparators=comparators,
        current_reading=round(current_reading, 4),
        current_months_since_peak=current_months,
        peak_date=str(current_peak.date()),
        envelope_at_current_duration=envelope,
    )


def compute_employment_breadth(
    sector_emp: pd.DataFrame,
    current_peak: pd.Timestamp,
) -> MetricResult:
    """Employment breadth across 16 LFS sectors, anchored to GDP peak.

    sector_emp: DataFrame indexed by date, columns = sector names, values = levels (thousands).
    """
    n_sectors = len(sector_emp.columns)

    def _emp_breadth_series(pk_dt: pd.Timestamp) -> pd.Series:
        idx = sector_emp.index.searchsorted(pk_dt)
        if idx >= len(sector_emp.index):
            return pd.Series(dtype=float)
        pk_vals = sector_emp.iloc[idx]
        below = (sector_emp < pk_vals) & (~sector_emp.isna()) & (~pk_vals.isna())
        breadth = below.sum(axis=1) / n_sectors * 100
        return breadth

    # Current episode
    idx = sector_emp.index.searchsorted(current_peak)
    if idx >= len(sector_emp.index):
        raise ValueError(f"GDP peak {current_peak} beyond employment breadth index")
    peak_actual = sector_emp.index[idx]

    breadth_all = _emp_breadth_series(peak_actual)
    current_path = _build_path(breadth_all, peak_actual, 1.0, max_months=36, as_pct=False)
    current_reading = current_path[-1]["value"] if current_path else 0.0
    current_months = current_path[-1]["monthsSincePeak"] if current_path else 0

    comparators = []
    for label, gdp_peak_dt in CD_HOWE_PEAKS.items():
        idx = sector_emp.index.searchsorted(gdp_peak_dt)
        if idx >= len(sector_emp.index):
            continue
        pk_actual_c = sector_emp.index[idx]
        breadth_c = _emp_breadth_series(pk_actual_c)
        path = _build_path(breadth_c, pk_actual_c, 1.0, max_months=48, as_pct=False)
        trough = max((p["value"] for p in path), default=0.0)
        trough_m = next((p["monthsSincePeak"] for p in path if p["value"] == trough), None)
        comparators.append(MetricPath(
            label=label,
            peak_date=str(pk_actual_c.date()),
            path=path,
            trough_depth=round(trough, 2),
            trough_month=trough_m,
        ))

    envelope = _compute_envelope_breadth(comparators, current_months)

    return MetricResult(
        metric="emp_breadth",
        unit="% of sectors",
        description=f"% of {n_sectors} LFS sectors below GDP-peak-date employment level",
        current=MetricPath(
            label="current",
            peak_date=str(peak_actual.date()),
            path=current_path,
            trough_depth=max((p["value"] for p in current_path), default=0.0),
            trough_month=None,
        ),
        comparators=comparators,
        current_reading=round(current_reading, 2),
        current_months_since_peak=current_months,
        peak_date=str(current_peak.date()),
        envelope_at_current_duration=envelope,
    )


def compute_fine_gdp_breadth_current(
    gdp_434_df: pd.DataFrame,
    current_peak: pd.Timestamp,
    leaf_codes: list[str],
) -> dict:
    """Fine GDP breadth at ~84 3-digit NAICS industries (current episode only, 1997+).

    Returns a simple dict: {current_reading, n_sectors, peak_date, path[...]}.
    Not cycle-on-cycle comparable (1997 start only).
    """
    # Pivot to wide
    df = gdp_434_df.copy()
    df["canonical"] = df["naics_code"]
    df = df[df["canonical"].isin(leaf_codes)]
    if df.empty:
        return {"error": "No leaf NAICS codes matched in 36100434"}

    pivot = (
        df.groupby(["date", "canonical"])["value"]
        .mean()
        .unstack("canonical")
    )
    n_sectors = len(pivot.columns)

    idx = pivot.index.searchsorted(current_peak)
    if idx >= len(pivot.index):
        return {"error": f"Peak {current_peak} beyond fine GDP index"}
    peak_actual = pivot.index[idx]
    pk_vals = pivot.iloc[idx]

    below = (pivot < pk_vals) & (~pivot.isna()) & (~pk_vals.isna())
    breadth = below.sum(axis=1) / n_sectors * 100

    path = []
    for m in range(37):
        dt = peak_actual + pd.DateOffset(months=m)
        idx2 = breadth.index.searchsorted(dt)
        if idx2 >= len(breadth.index):
            break
        dt_actual = breadth.index[idx2]
        if abs((dt_actual - dt).days) > 15:
            break
        path.append({"monthsSincePeak": m, "value": round(float(breadth.iloc[idx2]), 2)})

    current_reading = path[-1]["value"] if path else 0.0

    return {
        "n_sectors": n_sectors,
        "peak_date": str(peak_actual.date()),
        "current_reading": current_reading,
        "path": path,
        "note": "3-digit NAICS breadth, 1997+ only, not comparable across recession eras",
    }


# ---------------------------------------------------------------------------
# Envelope helpers
# ---------------------------------------------------------------------------

def _compute_envelope(
    comparators: list[MetricPath],
    current_months: int,
) -> dict:
    """Envelope for depth metrics (negative = contraction). At current duration."""
    if not comparators:
        return {}
    values_at_duration = {}
    for c in comparators:
        # Find value at current_months in the comparator path
        match = next(
            (p["value"] for p in c.path if p["monthsSincePeak"] == current_months),
            None
        )
        if match is None:
            # Interpolate nearest
            nearby = [p for p in c.path if abs(p["monthsSincePeak"] - current_months) <= 2]
            if nearby:
                match = min(nearby, key=lambda p: abs(p["monthsSincePeak"] - current_months))["value"]
        if match is not None:
            values_at_duration[c.label] = match

    if not values_at_duration:
        return {}

    return {
        "mildest": round(max(values_at_duration.values()), 4),  # least negative = mildest
        "severest": round(min(values_at_duration.values()), 4),
        "covid": values_at_duration.get("2020"),
        "by_recession": {k: round(v, 4) for k, v in values_at_duration.items()},
    }


def _compute_envelope_breadth(
    comparators: list[MetricPath],
    current_months: int,
) -> dict:
    """Envelope for breadth metrics (higher = more contraction). At current duration."""
    if not comparators:
        return {}
    values_at_duration = {}
    for c in comparators:
        match = next(
            (p["value"] for p in c.path if p["monthsSincePeak"] == current_months),
            None
        )
        if match is None:
            nearby = [p for p in c.path if abs(p["monthsSincePeak"] - current_months) <= 2]
            if nearby:
                match = min(nearby, key=lambda p: abs(p["monthsSincePeak"] - current_months))["value"]
        if match is not None:
            values_at_duration[c.label] = match

    if not values_at_duration:
        return {}

    return {
        "mildest": round(min(values_at_duration.values()), 2),   # lowest breadth = mildest
        "severest": round(max(values_at_duration.values()), 2),  # highest breadth = severest
        "covid": values_at_duration.get("2020"),
        "by_recession": {k: round(v, 2) for k, v in values_at_duration.items()},
    }
