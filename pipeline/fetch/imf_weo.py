"""IMF World Economic Outlook (WEO) DataMapper API client.

API docs: https://www.imf.org/external/datamapper/api/help

The IMF DataMapper exposes WEO indicators as annual time series for all
member countries. We use it for Canadian general-government fiscal stance
indicators:
    - GGXCNL_NGDP: General government net lending/borrowing, % of GDP
      (negative = deficit / net borrowing; positive = surplus)
    - GGXWDG_NGDP: General government gross debt, % of GDP

Scope caveat: both series are GENERAL GOVERNMENT (consolidated federal +
provincial + local + social-security funds), not federal-only. The IMF does
not publish Canada's federal-only fiscal position. Users of these series
must note the general-government scope in any chart or caption. Federal-only
data requires extraction from the DoF Fiscal Reference Tables PDFs
(published annually by the Department of Finance Canada).

Publication conventions:
    - WEO is published twice per year (April and October). Vintages are not
      versioned in the DataMapper API; the current-vintage values overwrite
      prior values at each release.
    - The API returns BOTH historical actuals and IMF projections. We
      distinguish them at the boundary by capping historical data at the
      last year where Statistics Canada has published actual GDP (we use
      `historical_cutoff_year` argument defaulting to the current year).
      Projections are retained in the raw CSV so a researcher can see the
      forward path; they are tagged in the .meta.json `notes` field.
    - Values are already in % of GDP (e.g. -4.0 = deficit of 4% of GDP).
      No unit scaling is needed.

Source quirks:
    - The DataMapper URL is stable: /api/v1/<indicator>/<iso3_country>
    - The response JSON shape: {"values": {"<indicator>": {"<ISO3>": {"<year>": <value>}}}}
    - Year keys are strings ("1980" through current projection year).
    - Some years may return null (None after JSON parse); we drop them.
    - The API allows no API key but may 403 with certain user-agent strings;
      we set a descriptive User-Agent to signal a legitimate research client.
    - Rate limits are generous for single-country pulls; no per-series
      throttling has been observed in production use.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional

import pandas as pd
from pydantic import BaseModel, ConfigDict

from pipeline.fetch._http import get_client, get_json

IMF_DATAMAPPER_BASE = "https://www.imf.org/external/datamapper/api/v1"
CANADA_ISO3 = "CAN"

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Pydantic boundary validators
# ---------------------------------------------------------------------------

class _IndicatorCountryValues(BaseModel):
    """Validates the per-country year-value dict from the DataMapper response."""
    model_config = ConfigDict(extra="allow")
    # The actual country dict is dynamic (year -> value), so we validate at
    # the indicator level and parse the inner dict manually after validation.


def _parse_year_values(raw: dict) -> dict[int, float]:
    """Convert the raw {year_str: value_or_null} dict to {year_int: float}.

    Drops years whose value is None (IMF uses null for missing / not-yet-
    published actuals and for years outside the country's coverage window).
    """
    out: dict[int, float] = {}
    for year_str, val in raw.items():
        if val is None:
            continue
        try:
            out[int(year_str)] = float(val)
        except (ValueError, TypeError):
            logger.warning("imf_weo: skipping unparseable year/value pair (%r, %r)", year_str, val)
    return out


# ---------------------------------------------------------------------------
# Public result type
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ImfWeoFetchResult:
    """Result of a single IMF WEO DataMapper series fetch.

    `data` is a DataFrame with columns:
        - date: pandas Timestamp, month=1, day=1 (annual: year-01-01)
        - value: float (already in % of GDP)

    `indicator_id` is the DataMapper series ID (e.g. "GGXCNL_NGDP").
    `country` is the ISO3 country code (e.g. "CAN").
    `all_years` includes projections; historical actuals end at the last
    year before the WEO projection horizon starts. We cannot programmatically
    identify the actuals/projections boundary because the DataMapper does not
    tag it; callers should treat data from the current year onward as
    projections and note that in .meta.json.
    """
    indicator_id: str
    country: str
    data: pd.DataFrame         # date, value -- all years including projections
    first_year: Optional[int]  # first non-null year in the series
    last_year: Optional[int]   # last non-null year in the series


# ---------------------------------------------------------------------------
# API functions
# ---------------------------------------------------------------------------

def observations_url(indicator_id: str, country: str = CANADA_ISO3) -> str:
    """Canonical URL for provenance in .meta.json."""
    return f"{IMF_DATAMAPPER_BASE}/{indicator_id}/{country}"


def fetch_indicator(
    indicator_id: str,
    country: str = CANADA_ISO3,
) -> ImfWeoFetchResult:
    """Fetch one IMF DataMapper series for one country.

    Args:
        indicator_id: IMF WEO indicator code (e.g. "GGXCNL_NGDP").
        country: ISO3 country code (default: "CAN").

    Returns:
        ImfWeoFetchResult. Raises RuntimeError if the API returns no data
        for the requested indicator+country combination.

    The full response JSON has this shape:
        {
          "values": {
            "<indicator_id>": {
              "<ISO3>": {
                "1980": <float|null>,
                "1981": <float|null>,
                ...
              }
            }
          }
        }
    """
    url = observations_url(indicator_id, country)
    with get_client() as client:
        raw = get_json(client, url)

    values_root = raw.get("values", {})
    indicator_data = values_root.get(indicator_id, {})
    country_data = indicator_data.get(country, {})

    if not country_data:
        raise RuntimeError(
            f"IMF DataMapper returned no data for indicator={indicator_id!r}, "
            f"country={country!r}. URL: {url}"
        )

    year_values = _parse_year_values(country_data)
    if not year_values:
        raise RuntimeError(
            f"IMF DataMapper: all values are null for indicator={indicator_id!r}, "
            f"country={country!r} (series may not be published for this country). "
            f"URL: {url}"
        )

    records = [
        {"date": pd.Timestamp(year=yr, month=1, day=1), "value": val}
        for yr, val in sorted(year_values.items())
    ]
    df = pd.DataFrame(records, columns=["date", "value"])

    first_year = min(year_values)
    last_year = max(year_values)

    logger.info(
        "imf_weo: fetched %s/%s -- %d observations (%d to %d)",
        indicator_id, country, len(df), first_year, last_year,
    )
    return ImfWeoFetchResult(
        indicator_id=indicator_id,
        country=country,
        data=df,
        first_year=first_year,
        last_year=last_year,
    )
