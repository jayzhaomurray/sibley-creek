"""Yahoo Finance daily-close fetcher.

We use Yahoo for daily equity-index and commodity-futures closes where no clean
primary public source exists or where the primary source is paywalled:
    - TSX Composite (`^GSPTSE`) -- TMX's official S&P/TSX is paid; Yahoo is the
      working free EOD feed.
    - S&P 500 (`^GSPC`) -- FRED has `SP500` but truncated to last 10y per S&P
      Dow Jones licensing; Yahoo carries the deeper history we need.
    - Gold (`GC=F`, COMEX gold futures front month) -- FRED's LBMA series was
      discontinued; GC=F is the daily close most desks reference. Acceptable
      proxy for the LBMA AM fix at the basics-layer cadence.

Source quirks:
    - Yahoo's API is unofficial. Schema can change without notice. We pin to
      the v8 `chart` endpoint, which has been stable since at least 2020.
    - The endpoint returns OHLC + adjusted close + volume. We take adjusted
      close so corporate-action splits don't introduce jumps (relevant for
      individual equities; benign for indices and futures).
    - Timestamps are POSIX (seconds since epoch). Convert with `pd.to_datetime(..., unit="s")`.
    - Range parameter accepts "1d", "5d", "1mo", "3mo", "6mo", "1y", "2y",
      "5y", "10y", "ytd", "max". We use "max" for the catalog; the API
      typically returns ~30 years of history for major indices.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pipeline.fetch._http import get_client, get_json

logger = logging.getLogger("pipeline.fetch.yahoo")

YAHOO_CHART_URL = "https://query1.finance.yahoo.com/v8/finance/chart"

# Completed-close threshold, UTC. A daily bar dated D is only treated as a
# completed close once the wall clock is past 21:30 UTC on D. Rationale:
# every symbol in the catalog has finished trading for date D by then --
# TSX/NYSE cash close 16:00 ET (20:00/21:00 UTC across EDT/EST); NYMEX CL=F /
# COMEX GC=F / ICE BZ=F electronic sessions for trade date D end 17:00 ET
# (21:00/22:00 UTC) -- 21:30 UTC plus the 22:00 UTC cron means the scheduled
# fetch always lands after the threshold. Yahoo's v8 chart endpoint includes
# the CURRENT PARTIAL BAR in its response (observed: a 9:15am ET quote
# recorded as the June 5 2026 "close"; a 20:44 ET Globex evening quote
# recorded as the June 10 2026 "close"), so any final row failing this test
# is an intraday snapshot, not a close, and must never be published.
# Trade-off: a fetch between an early close and 21:30 UTC drops one
# genuinely-final bar for a day; cost is one cycle of latency, benefit is
# that the last published row is always a completed close.
COMPLETED_CLOSE_UTC_HOUR = 21
COMPLETED_CLOSE_UTC_MINUTE = 30

# Yahoo blocks requests without a Mozilla-like User-Agent; pipeline._http
# already sends our project UA, but Yahoo will sometimes 401 it. Send a
# browser-like UA on this specific endpoint.
YAHOO_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    ),
    "Accept": "application/json",
}


class _YahooQuote(BaseModel):
    model_config = ConfigDict(extra="allow")
    close: Optional[list[Optional[float]]] = None
    adjclose: Optional[list[Optional[float]]] = None


class _YahooIndicators(BaseModel):
    model_config = ConfigDict(extra="allow")
    quote: list[_YahooQuote] = Field(default_factory=list)
    adjclose: Optional[list[dict]] = None  # adjclose lives in a separate slot for some symbols


class _YahooResult(BaseModel):
    model_config = ConfigDict(extra="allow")
    timestamp: list[int] = Field(default_factory=list)
    indicators: _YahooIndicators = Field(default_factory=_YahooIndicators)


class _YahooChart(BaseModel):
    model_config = ConfigDict(extra="allow")
    result: Optional[list[_YahooResult]] = None
    error: Optional[dict] = None


class _YahooResponse(BaseModel):
    model_config = ConfigDict(extra="allow")
    chart: _YahooChart = Field(default_factory=_YahooChart)


@dataclass(frozen=True)
class YahooFetchResult:
    symbol: str
    data: pd.DataFrame  # columns: date, value (adjusted close where available, else close)


def _drop_incomplete_final_bars(
    df: pd.DataFrame, *, symbol: str, now: Optional[datetime] = None
) -> pd.DataFrame:
    """Drop trailing rows that cannot yet be completed daily closes.

    Yahoo's v8 chart endpoint returns the current partial bar alongside
    completed history. Rule: a row dated D is kept only if `now` (UTC) is
    past COMPLETED_CLOSE_UTC on D itself. Applied from the tail inward, so
    a partial bar (and any anomalous future-dated bar) is removed while all
    completed history is untouched.

    `now` is injectable for tests; defaults to the real UTC clock.
    """
    if df.empty:
        return df
    if now is None:
        now = datetime.now(timezone.utc)

    keep_until = len(df)
    while keep_until > 0:
        bar_date = pd.Timestamp(df["date"].iloc[keep_until - 1])
        threshold = datetime(
            bar_date.year,
            bar_date.month,
            bar_date.day,
            COMPLETED_CLOSE_UTC_HOUR,
            COMPLETED_CLOSE_UTC_MINUTE,
            tzinfo=timezone.utc,
        )
        if now >= threshold:
            break
        logger.info(
            "dropping incomplete final bar for %s: date=%s value=%s "
            "(fetched %s, before completed-close threshold %s)",
            symbol,
            bar_date.date().isoformat(),
            df["value"].iloc[keep_until - 1],
            now.isoformat(timespec="minutes"),
            threshold.isoformat(timespec="minutes"),
        )
        keep_until -= 1

    if keep_until == len(df):
        return df
    return df.iloc[:keep_until].reset_index(drop=True)


def fetch_daily_close(symbol: str, *, range_: str = "10y") -> YahooFetchResult:
    """Fetch daily closes for one Yahoo symbol.

    Args:
        symbol: e.g. "^GSPTSE", "^GSPC", "GC=F".
        range_: Yahoo `range` parameter; default "10y".
            WARNING on "max": Yahoo silently downsamples `range=max +
            interval=1d` to quarterly for ^GSPTSE (verified 2026-05-19) and
            returns mixed-cadence frames for CL=F / BZ=F futures. Pass
            range_="max" only if you have verified the symbol returns true
            daily cadence at max range and you genuinely need >10y.

    Returns:
        YahooFetchResult with columns date, value. Value is adjusted close
        when Yahoo exposes it; otherwise raw close. NaN closes (rare; usually
        the most recent intraday slot before close) are dropped. The final
        row is additionally dropped when it cannot yet be a completed close
        (Yahoo returns the live partial bar; see _drop_incomplete_final_bars).
    """
    url = f"{YAHOO_CHART_URL}/{symbol}"
    params = {"interval": "1d", "range": range_, "includeAdjustedClose": "true"}
    with get_client(headers=YAHOO_HEADERS) as client:
        payload = get_json(client, url, params=params)

    parsed = _YahooResponse.model_validate(payload)
    if parsed.chart.error:
        raise ValueError(f"Yahoo chart error for {symbol!r}: {parsed.chart.error}")
    if not parsed.chart.result:
        raise ValueError(f"Yahoo returned no result for symbol {symbol!r}")

    result = parsed.chart.result[0]
    timestamps = result.timestamp
    quotes = result.indicators.quote
    if not quotes or not timestamps:
        raise ValueError(f"Yahoo returned no observations for symbol {symbol!r}")

    closes = quotes[0].close or []
    # Prefer adjusted close where present (corporate actions safety on equities)
    adj_block = result.indicators.adjclose or []
    if adj_block and isinstance(adj_block, list) and "adjclose" in adj_block[0]:
        adj = adj_block[0]["adjclose"]
        if isinstance(adj, list) and len(adj) == len(closes):
            closes = adj

    if len(timestamps) != len(closes):
        raise ValueError(
            f"Yahoo length mismatch for {symbol!r}: "
            f"{len(timestamps)} timestamps vs {len(closes)} closes"
        )

    df = pd.DataFrame(
        {
            "date": pd.to_datetime(timestamps, unit="s", utc=True).tz_convert(None).normalize(),
            "value": closes,
        }
    )
    df = df.dropna(subset=["value"]).reset_index(drop=True)
    df = df.sort_values("date").reset_index(drop=True)

    # Never publish an intraday snapshot as a daily close. See
    # COMPLETED_CLOSE_UTC_* above for the threshold rationale.
    df = _drop_incomplete_final_bars(df, symbol=symbol)

    return YahooFetchResult(symbol=symbol, data=df)


def symbol_url(symbol: str) -> str:
    """Human-readable Yahoo Finance quote URL for .meta.json provenance."""
    # URL-encode the caret in ^GSPTSE / ^GSPC
    safe = symbol.replace("^", "%5E")
    return f"https://finance.yahoo.com/quote/{safe}"
