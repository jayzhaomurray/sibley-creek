"""FRED (Federal Reserve Bank of St. Louis) API client.

API docs: https://fred.stlouisfed.org/docs/api/fred/

Used for US comparators that Canadian macro hinges on: US 10y Treasury, US IG/HY
OAS spreads, VIX, broad trade-weighted USD. Per dashboard_purpose section 4.6,
these enter as transmission channels into Canada, not as US-macro standalone
content.

Conventions:
    - Address by FRED series ID (e.g. "DGS10", "VIXCLS").
    - Pull from a start_date; FRED returns ALL observations from that date forward.
    - Skip "." values (FRED's missing-data marker on holidays / pre-series).
    - Requires FRED_API_KEY environment variable. If unset, the catalog skips
      FRED entries with a logged warning rather than failing the build.

Source quirks:
    - Series can be discontinued or renamed; the API returns 400 with a clear
      "series does not exist" body. Caller decides whether that's a build failure.
    - FRED's S&P 500 series (SP500) is restricted to the last 10 years by S&P
      Dow Jones licensing. For deeper history use Yahoo (^GSPC). We use Yahoo.
    - LBMA gold series (GOLDAMGBD228NLBM, GOLDPMGBD228NLBM) was discontinued by
      ICE Benchmark Administration on FRED; switch to Yahoo (GC=F) for daily gold.
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from typing import Optional

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pipeline.fetch._http import get_client, get_json

FRED_BASE_URL = "https://api.stlouisfed.org/fred"

logger = logging.getLogger(__name__)


class _FredObservation(BaseModel):
    model_config = ConfigDict(extra="allow")
    date: str
    value: str  # FRED returns "." for missing; we coerce later


class _FredResponse(BaseModel):
    model_config = ConfigDict(extra="allow")
    observations: list[_FredObservation] = Field(default_factory=list)


@dataclass(frozen=True)
class FredFetchResult:
    series_id: str
    data: pd.DataFrame


def get_api_key() -> Optional[str]:
    """Return FRED_API_KEY from the environment, or None if unset.

    Caller decides what to do: the build orchestrator skips FRED tasks with a
    log line; tests inject a dummy key via monkeypatch.
    """
    return os.environ.get("FRED_API_KEY") or None


def fetch_series(
    series_id: str, *, start_date: Optional[str] = None, api_key: Optional[str] = None
) -> FredFetchResult:
    """Fetch one FRED series.

    Args:
        series_id: FRED series ID (e.g. "DGS10").
        start_date: ISO date string. None = full history.
        api_key: explicit override; falls back to FRED_API_KEY env var.

    Returns:
        FredFetchResult with DataFrame columns date, value. Missing values
        (FRED "." markers) are dropped, not preserved as NaN, because FRED
        emits them densely for daily series on weekends/holidays and the
        resulting NaN forest is noise not signal.

    Raises:
        ValueError if no API key is configured.
        httpx.HTTPStatusError on 4xx other than 429 (e.g. series ID typo).
    """
    api_key = api_key or get_api_key()
    if not api_key:
        raise ValueError(
            "FRED_API_KEY is not set. Either configure the env var or pass api_key= explicitly."
        )

    params: dict = {
        "series_id": series_id,
        "api_key": api_key,
        "file_type": "json",
    }
    if start_date is not None:
        params["observation_start"] = start_date

    url = f"{FRED_BASE_URL}/series/observations"
    with get_client() as client:
        payload = get_json(client, url, params=params)

    parsed = _FredResponse.model_validate(payload)
    records: list[dict] = []
    for ob in parsed.observations:
        if ob.value in (".", "", None):
            continue
        try:
            records.append({"date": ob.date, "value": float(ob.value)})
        except (TypeError, ValueError):
            continue

    df = pd.DataFrame(records, columns=["date", "value"])
    if not df.empty:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df = df.dropna(subset=["date"]).sort_values("date").reset_index(drop=True)

    return FredFetchResult(series_id=series_id, data=df)


def fetch_fed_funds_target() -> pd.DataFrame:
    """Composite Fed funds target rate: FEDFUNDS monthly pre-2008 + DFEDTARU (upper bound) post-2008.

    Carried over from boc-tracker; the pre-2008 effective rate is an acceptable
    proxy for the target before the Fed adopted a target range in Dec 2008.

    Switched from midpoint (upper+lower)/2 to upper bound on 2026-05-11. The
    upper bound is the rate the Fed PUBLISHES as the headline policy
    reference and is the value financial press cites. "Midpoint" is a
    derived synthesis that no Fed statement uses and that conflates the
    target range with the effective rate. Reader prose now says "Fed funds
    at 3.75%, the upper bound of its 3.50 to 3.75% target range" rather
    than "Fed funds at 3.625%, the midpoint."
    """
    monthly = fetch_series("FEDFUNDS", start_date="1990-01-01").data
    upper = fetch_series("DFEDTARU", start_date="2008-01-01").data

    if upper.empty:
        raise ValueError("Fed funds upper-bound post-2008 fetch returned empty data.")

    post = upper.copy()
    cutoff = post["date"].min()
    pre = monthly[monthly["date"] < cutoff]
    combined = pd.concat([pre, post], ignore_index=True).sort_values("date").reset_index(drop=True)
    return combined


def series_url(series_id: str) -> str:
    """Return the human-facing FRED series page for .meta.json provenance."""
    return f"https://fred.stlouisfed.org/series/{series_id}"
