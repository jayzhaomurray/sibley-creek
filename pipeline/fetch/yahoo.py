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

from dataclasses import dataclass
from typing import Optional

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pipeline.fetch._http import get_client, get_json

YAHOO_CHART_URL = "https://query1.finance.yahoo.com/v8/finance/chart"

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


def fetch_daily_close(symbol: str, *, range_: str = "max") -> YahooFetchResult:
    """Fetch daily closes for one Yahoo symbol.

    Args:
        symbol: e.g. "^GSPTSE", "^GSPC", "GC=F".
        range_: Yahoo `range` parameter; default "max" pulls full available history.

    Returns:
        YahooFetchResult with columns date, value. Value is adjusted close
        when Yahoo exposes it; otherwise raw close. NaN closes (rare; usually
        the most recent intraday slot before close) are dropped.
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

    return YahooFetchResult(symbol=symbol, data=df)


def symbol_url(symbol: str) -> str:
    """Human-readable Yahoo Finance quote URL for .meta.json provenance."""
    # URL-encode the caret in ^GSPTSE / ^GSPC
    safe = symbol.replace("^", "%5E")
    return f"https://finance.yahoo.com/quote/{safe}"
