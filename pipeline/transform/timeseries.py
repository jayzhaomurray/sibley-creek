"""Section-agnostic time-series transforms.

All functions take a pandas Series (or DataFrame) indexed by date and return
the same shape. Any function that needs to know about cadence takes an
explicit `periods` argument; we do NOT infer from index frequency, because
StatCan / BoC release calendars produce irregular gaps that fool inference.

Conventions:
    - Output for *_pct functions is in percentage points (e.g. 2.5 means 2.5%),
      not decimals. This matches editorial usage; researchers and charts
      consume "%". Conversion to decimals happens at the boundary if ever needed.
    - NaN handling: we propagate NaN. Leading observations that can't compute
      a window will be NaN, not dropped. Callers can .dropna() if they prefer.
    - Infinity handling: Infinity is NEVER emitted. Any transform that would
      produce +/-Inf (zero denominator, division-by-zero in pct_change) instead
      emits NaN so the callers .dropna() removes the offending row rather than
      propagating an invalid value into the JSON output. This is the fail-closed
      contract: a missing data point is better than a broken chart.
    - Source series are never mutated; every function returns a new object.
"""

from __future__ import annotations

from typing import Union

import numpy as np
import pandas as pd

SeriesLike = Union[pd.Series, pd.DataFrame]


def _replace_inf(result: SeriesLike) -> SeriesLike:
    """Replace +/-Infinity with NaN in any Series or DataFrame.

    Internal helper used by all percent-change functions to enforce the
    Infinity-free output contract. Zero denominators in pct_change / ratio
    computations produce Inf; we convert those to NaN so downstream callers
    see a missing value (which .dropna() or panel_data.py safely handles)
    rather than invalid JSON output.
    """
    if isinstance(result, pd.Series):
        return result.replace([np.inf, -np.inf], np.nan)
    return result.replace([np.inf, -np.inf], np.nan)


def pct_change_at_horizon(s: SeriesLike, periods: int) -> SeriesLike:
    """Percent change over `periods` observations, expressed in percent (not fraction).

    For a monthly series, periods=12 is the YoY change; periods=1 is the MoM.
    For a quarterly series, periods=4 is the YoY; periods=1 is the QoQ.

    Equivalent to `s.pct_change(periods) * 100`, but with an explicit name and
    no surprise about units. Infinity (zero denominator) is replaced with NaN.
    """
    return _replace_inf(s.pct_change(periods, fill_method=None) * 100)


def yoy_pct(s: SeriesLike, *, periods_per_year: int) -> SeriesLike:
    """Year-over-year percent change.

    `periods_per_year` is the number of observations per year for this series:
        12 for monthly, 4 for quarterly, 252 for daily business days,
        365 for daily calendar days, 52 for weekly.

    Editorial note: for a daily series, "YoY" is conventionally "value today
    vs value on the same calendar day one year ago". Computing that exactly
    needs a date-aligned shift, not a positional shift. For now, callers who
    need calendar-aware YoY on daily data should use `align_yoy` (TODO when
    a use-case lands) rather than this function.

    Infinity (zero denominator) is replaced with NaN.
    """
    return _replace_inf(s.pct_change(periods_per_year, fill_method=None) * 100)


def qoq_annualized_pct(s: SeriesLike) -> SeriesLike:
    """Quarter-over-quarter growth, annualized, in percent.

    The standard "Q/Q SAAR" definition used by StatCan, BoC, and the BEA:
        ( (s_t / s_{t-1}) ** 4 - 1 ) * 100

    Assumes `s` is quarterly. If you have monthly data and want a 3-month
    annualized rate, use `annualize_period_growth(s, period_lag=3, periods_per_year=12)`.

    Infinity (zero denominator) is replaced with NaN.
    """
    return _replace_inf(((s / s.shift(1)) ** 4 - 1) * 100)


def annualize_period_growth(
    s: SeriesLike, *, period_lag: int, periods_per_year: int
) -> SeriesLike:
    """Annualize the growth between `s_t` and `s_{t-period_lag}`.

    Used for things like "3-month annualized rate of headline CPI" on a
    monthly series: period_lag=3, periods_per_year=12.

    Formula: ( (s_t / s_{t-period_lag}) ** (periods_per_year / period_lag) - 1 ) * 100

    Infinity (zero denominator) is replaced with NaN.
    """
    if period_lag <= 0:
        raise ValueError(f"period_lag must be positive; got {period_lag}")
    if periods_per_year <= 0:
        raise ValueError(f"periods_per_year must be positive; got {periods_per_year}")
    return _replace_inf(((s / s.shift(period_lag)) ** (periods_per_year / period_lag) - 1) * 100)


def moving_average(
    s: SeriesLike, *, window: int, min_periods: int | None = None
) -> SeriesLike:
    """Trailing moving average over `window` observations.

    `min_periods` defaults to `window` (strict: no value emitted until the
    window is full). Pass an integer < window if you want a partial-window
    average to fill in early; useful for smoothing without a long burn-in,
    e.g. min_periods=window//2 for a "warm-up" view.
    """
    if min_periods is None:
        min_periods = window
    return s.rolling(window, min_periods=min_periods).mean()


def index_to_base(s: pd.Series, *, base_value: float = 100.0, base_date: pd.Timestamp | str | None = None) -> pd.Series:
    """Rebase a series so that `base_date` equals `base_value`.

    Equivalent to multiplying the whole series by `base_value / s[base_date]`.
    Useful when comparing series with different native units on the same axis
    ("everything = 100 at January 2020").

    Args:
        s: input series, indexed by date.
        base_value: target value at the base date. Defaults to 100.
        base_date: which date to anchor at. If None, uses the first
                   non-NaN observation in `s`.
    """
    if not isinstance(s, pd.Series):
        raise TypeError("index_to_base only operates on a Series; pass each column separately.")
    if s.empty:
        return s.copy()
    if base_date is None:
        first_valid = s.first_valid_index()
        if first_valid is None:
            return s.copy()
        anchor = s.loc[first_valid]
    else:
        anchor_idx = pd.Timestamp(base_date) if not isinstance(base_date, pd.Timestamp) else base_date
        if anchor_idx not in s.index:
            # Fall back to as-of (nearest prior observation).
            sub = s[s.index <= anchor_idx].dropna()
            if sub.empty:
                raise ValueError(f"base_date {base_date!r} is before any observation in the series.")
            anchor = float(sub.iloc[-1])
        else:
            anchor = float(s.loc[anchor_idx])
    if anchor == 0:
        raise ValueError("Cannot rebase: anchor value is zero.")
    return s * (base_value / anchor)


def rebase_to_first(s: pd.Series, *, base_value: float = 100.0) -> pd.Series:
    """Shorthand for `index_to_base(s, base_value=base_value, base_date=None)`."""
    return index_to_base(s, base_value=base_value, base_date=None)
