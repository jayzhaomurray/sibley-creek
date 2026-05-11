"""Alberta Economic Dashboard fetcher.

The Government of Alberta publishes a public REST-style data API for the
charts that drive `economicdashboard.alberta.ca`. Each chart on the dashboard
maps to a UUID-coded endpoint of the form:

    https://api.economicdata.alberta.ca/api/data?code=<uuid>

Responses are JSON arrays of one observation per row, with at minimum:
    Date  : ISO 8601 timestamp (e.g. "2026-02-01T00:00:00")
    Value : numeric value
    Unit  : human-readable units string
    Type  : observation type label (note: the API emits the key as "Type "
            with a trailing space; we tolerate this on parse).

Series wired here (probe 2026-05-11):
    - Natural gas (Alberta reference price, C$/GJ, monthly from 1988-01)
      UUID: 666e6195-c509-479b-b79f-b95e05536032

The natural-gas series IS the AECO-equivalent monthly reference price the
Government of Alberta uses for royalty calculations. Canon 4.6 element 4
asks for "AECO gas (weekly bid-week summary if achievable, else defer to
v1.5)"; weekly bid-week is published by NGX behind subscription/login and
is not feasible from CI without a paid feed. We register the monthly series
here as the v1 fallback and surface the cadence limitation in `.meta.json`
notes so downstream charts can label appropriately.

Why a separate module from `pipeline/fetch/alberta.py` being a 'WCS only'
module (per the placeholder note in `pipeline/fetch/__init__.py`): the API
endpoint shape is identical for every Alberta Dashboard chart -- one UUID
per series. Wiring natural gas now does not preclude WCS being added later;
both call `fetch_dashboard_series(uuid)`.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pipeline.fetch._http import get_client, get_json

API_BASE_URL = "https://api.economicdata.alberta.ca/api/data"

# Public dashboard pages backing each series, for human-facing citations.
DASHBOARD_PAGES = {
    "natural-gas-price": "https://economicdashboard.alberta.ca/dashboard/natural-gas-price",
}


class _AlbertaObservation(BaseModel):
    """One row of the Alberta Dashboard API response.

    The API uses "Type " (trailing space) as the key for the observation
    type field. We accept either form via the populate_by_name +
    field-alias mechanism so a future API cleanup does not break parsing.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)
    Date: str
    Value: float | None = None
    Unit: str | None = None
    # The trailing-space key from the live API. Pydantic strips on parse via
    # populate_by_name + alias; we keep this optional so a missing field is
    # not fatal.
    Type: str | None = Field(default=None, alias="Type ")


@dataclass(frozen=True)
class AlbertaFetchResult:
    """Result of a single Alberta Dashboard series fetch."""

    series_code: str
    data: pd.DataFrame
    units: str | None
    type_label: str | None


def series_url(code: str) -> str:
    """Return the canonical Alberta Dashboard API URL for a series UUID."""
    return f"{API_BASE_URL}?code={code}"


def fetch_dashboard_series(code: str) -> AlbertaFetchResult:
    """Fetch one Alberta Economic Dashboard series by its UUID code.

    Args:
        code: the UUID code identifying the chart/series on the dashboard.

    Returns:
        AlbertaFetchResult with a DataFrame (columns: date, value), units
        and type-label hoisted out of the first observation for use in
        `.meta.json` notes.

    Raises:
        ValueError if the response is empty or malformed.
    """
    url = API_BASE_URL
    with get_client() as client:
        payload = get_json(client, url, params={"code": code})

    if not isinstance(payload, list) or not payload:
        raise ValueError(
            f"Alberta Dashboard returned no rows for code {code!r}. "
            f"Probe: {series_url(code)}"
        )

    # Validate row shapes at the boundary. We do this in a list comprehension
    # rather than a model_validate(list[...]) so a single malformed row is
    # surfaced with a clear index in the exception trace.
    rows = []
    for i, raw in enumerate(payload):
        if not isinstance(raw, dict):
            raise ValueError(
                f"Alberta Dashboard row {i} for code {code!r} is not a dict: {raw!r}"
            )
        rows.append(_AlbertaObservation.model_validate(raw))

    records = []
    units: str | None = None
    type_label: str | None = None
    for ob in rows:
        if ob.Unit and units is None:
            units = ob.Unit
        if ob.Type and type_label is None:
            type_label = ob.Type.strip() or None
        if ob.Value is None or not ob.Date:
            # Null values do appear in some Alberta series during data gaps;
            # drop them to keep the CSV dense and let chart code rely on
            # monotonic date strides.
            continue
        records.append({"date": ob.Date, "value": float(ob.Value)})

    df = pd.DataFrame(records, columns=["date", "value"])
    if not df.empty:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df = df.dropna(subset=["date"]).sort_values("date").reset_index(drop=True)

    return AlbertaFetchResult(
        series_code=code,
        data=df,
        units=units,
        type_label=type_label,
    )


# --------------------------------------------------------------------------- #
# Convenience wrappers for the specific series we wire (1 per UUID).
# --------------------------------------------------------------------------- #

NATURAL_GAS_UUID = "666e6195-c509-479b-b79f-b95e05536032"


def fetch_natural_gas_price() -> AlbertaFetchResult:
    """Fetch the Alberta reference natural-gas price (monthly, C$/GJ).

    This is the v1 AECO-equivalent series for canon 4.6 element 4. It is
    a MONTHLY series; weekly bid-week defers to v1.5 (no free feed).
    """
    return fetch_dashboard_series(NATURAL_GAS_UUID)
