"""Reusable analytical derivations that cross multiple series.

These are slightly higher-level than `timeseries.py`: they expect named
inputs and return interpretable outputs (e.g. trade balance 3M MA from
the monthly balance; a partner-share trajectory from per-partner + total).

Editorial interpretation does not live here. A function returns the math;
researcher / chart-builder decides what to call "tightening" or "loosening".
"""

from __future__ import annotations

from typing import Iterable, Optional

import pandas as pd

from pipeline.transform.timeseries import (
    annualize_period_growth,
    moving_average,
    yoy_pct,
)


def trade_balance_3m_ma(balance: pd.DataFrame, *, window: int = 3) -> pd.DataFrame:
    """Apply a trailing N-month moving average to a date/value monthly series.

    Standard noise-suppression for monthly trade data per dashboard_purpose
    section 4.7 element 1. Returns a DataFrame with the same columns as input.
    """
    if not {"date", "value"}.issubset(balance.columns):
        raise ValueError(f"Expected date/value columns; got {list(balance.columns)}")
    s = balance.set_index("date")["value"].sort_index()
    smooth = moving_average(s, window=window, min_periods=window)
    return smooth.dropna().reset_index().rename(columns={s.name or "value": "value"})


def partner_share_trajectory(
    partner: pd.DataFrame, total: pd.DataFrame, *, label_partner: str = "partner",
) -> pd.DataFrame:
    """Rolling share of `partner` in `total`, monthly.

    Returns a DataFrame with columns date, value (% share). NaN-tolerant: if
    either side is missing for a date, that date is omitted from the output.
    """
    for name, df in (("partner", partner), ("total", total)):
        if not {"date", "value"}.issubset(df.columns):
            raise ValueError(f"{name}: expected date/value columns; got {list(df.columns)}")
    p = partner.set_index("date")["value"].sort_index()
    t = total.set_index("date")["value"].sort_index()
    joined = pd.concat([p.rename("partner"), t.rename("total")], axis=1).dropna()
    share = (joined["partner"] / joined["total"]) * 100
    out = share.dropna().reset_index()
    out.columns = ["date", "value"]
    return out


def headline_yoy(s: pd.DataFrame, *, periods_per_year: int) -> pd.DataFrame:
    """Apply YoY % change to a date/value DataFrame.

    Convenience wrapper over `timeseries.yoy_pct` that preserves the
    DataFrame contract.
    """
    if not {"date", "value"}.issubset(s.columns):
        raise ValueError(f"Expected date/value columns; got {list(s.columns)}")
    ss = s.set_index("date")["value"].sort_index()
    yoy = yoy_pct(ss, periods_per_year=periods_per_year)
    out = yoy.dropna().reset_index()
    out.columns = ["date", "value"]
    return out


def six_month_annualized(s: pd.DataFrame, *, periods_per_year: int = 12) -> pd.DataFrame:
    """6-month annualized rate on a monthly date/value series.

    Per dashboard_purpose section 4.4 element 1, CMA HPI Y/Y and 6-month
    annualized are the two cuts. This implements the latter on a monthly
    index series (period_lag=6, periods_per_year=12).
    """
    if not {"date", "value"}.issubset(s.columns):
        raise ValueError(f"Expected date/value columns; got {list(s.columns)}")
    ss = s.set_index("date")["value"].sort_index()
    out = annualize_period_growth(ss, period_lag=6, periods_per_year=periods_per_year)
    out = out.dropna().reset_index()
    out.columns = ["date", "value"]
    return out


def per_capita_growth(
    aggregate: pd.DataFrame, population: pd.DataFrame, *, periods_per_year: int,
) -> pd.DataFrame:
    """Subtractive per-capita growth: aggregate Y/Y - population Y/Y.

    Per researcher memo (Wave 1 brief 1.2 Section D), this is BoC's MPR
    convention for per-capita employment growth. Both inputs are level series
    with date/value columns; cadence must match.
    """
    for name, df in (("aggregate", aggregate), ("population", population)):
        if not {"date", "value"}.issubset(df.columns):
            raise ValueError(f"{name}: expected date/value columns; got {list(df.columns)}")
    a = aggregate.set_index("date")["value"].sort_index()
    p = population.set_index("date")["value"].sort_index()
    a_yoy = yoy_pct(a, periods_per_year=periods_per_year)
    p_yoy = yoy_pct(p, periods_per_year=periods_per_year)
    diff = (a_yoy - p_yoy).dropna()
    out = diff.reset_index()
    out.columns = ["date", "value"]
    return out


def goc_ust_spread(goc: pd.DataFrame, ust: pd.DataFrame) -> pd.DataFrame:
    """GoC yield minus US Treasury yield, aligned on shared trading days.

    Date alignment: inner join on date. Per dashboard_purpose section 4.6
    element 2 cadence note (BoC ~16:30 ET vs FRED ~15:30 ET), a one-day
    stagger is possible at month-end; we accept that, since the spread is
    consumed as a level trajectory, not a precision arbitrage signal.
    """
    for name, df in (("goc", goc), ("ust", ust)):
        if not {"date", "value"}.issubset(df.columns):
            raise ValueError(f"{name}: expected date/value columns; got {list(df.columns)}")
    g = goc.set_index("date")["value"].sort_index()
    u = ust.set_index("date")["value"].sort_index()
    joined = pd.concat([g.rename("goc"), u.rename("ust")], axis=1).dropna()
    spread = (joined["goc"] - joined["ust"]).reset_index()
    spread.columns = ["date", "value"]
    return spread
