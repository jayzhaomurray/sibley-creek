"""Bank of Canada Valet API client.

API docs: https://www.bankofcanada.ca/valet/docs

Conventions:
    - Address series by series key (e.g. "V39079" for the overnight rate
      target, "BD.CDN.2YR.DQ.YLD" for the 2-yr GoC benchmark yield).
    - Pull full observation history via the `/observations/{series}/json`
      endpoint with a `start_date` filter. The response is one record per
      date with the series value under the series-key field.
    - Some series go through long stale periods (e.g. fixed announcement
      dates between FAD meetings produce no observation). We do not interpolate.

Inherited wisdom from boc-tracker:
    - Series keys are not always literal short codes; some require prefixes
      (e.g. "STATIC_ATABLE_V39079" for the long monthly history of the
      overnight rate target).
    - Some observations have a `null` value field; skip those rows but keep
      a record in .meta.json that the source returned them.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pipeline.fetch._http import get_client, get_json

VALET_BASE_URL = "https://www.bankofcanada.ca/valet"


class _SeriesMetaBlock(BaseModel):
    """The `seriesDetail.<key>` block in a Valet observations response.

    Carries the human-readable label and units string the BoC publishes
    alongside the data; lifting it into our .meta.json saves callers
    needing to hardcode units.
    """

    model_config = ConfigDict(extra="allow")
    label: Optional[str] = None
    description: Optional[str] = None
    dimension: Optional[dict] = None


class _ValetObservationsResponse(BaseModel):
    """Minimal validation of the Valet `observations` JSON envelope."""

    model_config = ConfigDict(extra="allow")
    terms: Optional[dict] = None
    seriesDetail: dict[str, _SeriesMetaBlock] = Field(default_factory=dict)
    observations: list[dict] = Field(default_factory=list)


@dataclass(frozen=True)
class BocFetchResult:
    series_key: str
    data: pd.DataFrame
    label: Optional[str]
    description: Optional[str]


def fetch_series(series_key: str, *, start_date: Optional[str] = None) -> BocFetchResult:
    """Fetch one BoC Valet series.

    Args:
        series_key: series identifier (e.g. "V39079").
        start_date: ISO date string, e.g. "1990-01-01". If None, Valet returns
            the full available history.

    Returns:
        BocFetchResult with a DataFrame (columns: date, value), null-value
        observations dropped (with a count surfaced in the log), and the
        label/description from `seriesDetail` for use in .meta.json.

    Raises:
        ValueError if the response has no `observations` field (typically
        an unknown series key).
    """
    url = f"{VALET_BASE_URL}/observations/{series_key}/json"
    params: dict = {}
    if start_date is not None:
        params["start_date"] = start_date

    with get_client() as client:
        payload = get_json(client, url, params=params or None)

    parsed = _ValetObservationsResponse.model_validate(payload)
    if not parsed.observations:
        raise ValueError(
            f"BoC Valet returned no observations for series '{series_key}'. "
            f"Check the key at: {VALET_BASE_URL}/lists/series/json"
        )

    records = []
    for ob in parsed.observations:
        date_str = ob.get("d")
        slot = ob.get(series_key)
        if not date_str or not isinstance(slot, dict):
            continue
        raw_v = slot.get("v")
        if raw_v is None or raw_v == "":
            continue
        try:
            value = float(raw_v)
        except (TypeError, ValueError):
            continue
        records.append({"date": date_str, "value": value})

    df = pd.DataFrame(records, columns=["date", "value"])
    if not df.empty:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df = df.dropna(subset=["date"]).sort_values("date").reset_index(drop=True)

    meta_block = parsed.seriesDetail.get(series_key)
    label = meta_block.label if meta_block else None
    description = meta_block.description if meta_block else None

    return BocFetchResult(
        series_key=series_key,
        data=df,
        label=label,
        description=description,
    )


def observations_url(series_key: str) -> str:
    """Return the canonical Valet observations URL for a series key."""
    return f"{VALET_BASE_URL}/observations/{series_key}/json"
