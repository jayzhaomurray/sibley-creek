"""Statistics Canada Web Data Service (WDS) client.

API docs:
    https://www.statcan.gc.ca/en/developers/wds/user-guide

Conventions we adopt:
    - Address series by vector ID (the V-prefixed integer in StatCan tables),
      not by Cube/Coordinate. Vectors are stable across the CANSIM-to-Table-ID
      migration; coordinates are not.
    - Pull "latest N periods" rather than full-history range queries; WDS is
      fastest in that mode and gives an unambiguous most-recent window.
    - Preserve NaN observations. WDS flags structural gaps (e.g. the JVWS
      April-September 2020 COVID suspension) with statusCode=1 and a null
      value; charts auto-break lines on NaN and rolling means skip via
      min_periods.
    - The headline endpoint accepts a batch of vector requests; we expose
      both single- and batch-fetch entry points.

Inherited wisdom from boc-tracker:
    - Endpoint `getDataFromVectorsAndLatestNPeriods` is the workhorse.
    - The response payload is `[{status, object: {vectorDataPoint: [...]}}]`.
      Per-item `status != "SUCCESS"` means that vector is bad; raise per-item
      rather than failing the whole batch.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional

import pandas as pd
from pydantic import BaseModel, Field

from pipeline.fetch._http import get_client, post_json

WDS_BASE_URL = "https://www150.statcan.gc.ca/t1/wds/rest"
ENDPOINT_LATEST_N = f"{WDS_BASE_URL}/getDataFromVectorsAndLatestNPeriods"

# Default cap on observations pulled per vector. StatCan caps the per-request
# `latestN` at 1000-ish for some endpoints; we never need that for our use
# cases but expose the parameter so a caller can pull longer history if needed.
DEFAULT_LATEST_N = 600


class _VectorPoint(BaseModel):
    """Schema for one observation in a WDS response."""
    refPer: str
    value: Optional[float] = None
    # Other fields (refPer2, releaseTime, decimals, statusCode, statusEn,
    # symbolCode, symbolEn, frequencyCode) exist but we ignore them at this
    # level. We capture release_time at the response level instead.
    releaseTime: Optional[str] = None
    decimals: Optional[int] = None
    scalarFactorCode: Optional[int] = None


class _VectorObject(BaseModel):
    vectorId: int
    vectorDataPoint: list[_VectorPoint] = Field(default_factory=list)


class _VectorResponseItem(BaseModel):
    status: str
    object: Optional[_VectorObject] = None


@dataclass(frozen=True)
class StatCanFetchResult:
    """One vector's data plus the metadata fields we surface to .meta.json."""

    vector_id: int
    data: pd.DataFrame
    release_date: Optional[str]  # ISO date of the most recent observation's releaseTime, if present


def fetch_vector(vector_id: int, *, latest_n: int = DEFAULT_LATEST_N) -> StatCanFetchResult:
    """Fetch one StatCan vector via WDS.

    Args:
        vector_id: integer vector ID (the V-prefix is stripped; pass the int).
        latest_n: number of most-recent observations to pull.

    Returns:
        StatCanFetchResult with a DataFrame (columns: date, value), NaN-preserving.
        release_date is the maximum `releaseTime` reported by WDS on the
        observations, normalized to ISO date; None if the source didn't supply it.

    Raises:
        ValueError if WDS reports status != "SUCCESS" for this vector.
    """
    with get_client() as client:
        payload = post_json(
            client,
            ENDPOINT_LATEST_N,
            json_body=[{"vectorId": vector_id, "latestN": latest_n}],
        )
    return _parse_one(vector_id, payload[0])


def fetch_vectors(
    vector_ids: Iterable[int], *, latest_n: int = DEFAULT_LATEST_N
) -> dict[int, StatCanFetchResult]:
    """Batch-fetch multiple vectors in one round-trip.

    Returns a dict keyed by vector_id. Per-vector failures raise individually
    so the caller can decide whether to fail the build or proceed with partial
    data. Caller is responsible for that policy.
    """
    vector_ids = list(vector_ids)
    if not vector_ids:
        return {}
    body = [{"vectorId": v, "latestN": latest_n} for v in vector_ids]
    with get_client() as client:
        payload = post_json(client, ENDPOINT_LATEST_N, json_body=body)

    results: dict[int, StatCanFetchResult] = {}
    # WDS returns items in the same order as the request, but defensively
    # match on response.object.vectorId rather than relying on order.
    by_vid: dict[int, _VectorResponseItem] = {}
    for raw in payload:
        item = _VectorResponseItem.model_validate(raw)
        if item.object is not None:
            by_vid[item.object.vectorId] = item
    for vid in vector_ids:
        item = by_vid.get(vid)
        if item is None:
            raise ValueError(
                f"StatCan WDS response missing vector {vid}; "
                f"received vectors: {sorted(by_vid)}"
            )
        results[vid] = _parse_one(vid, item.model_dump())
    return results


def _parse_one(vector_id: int, raw_item: dict) -> StatCanFetchResult:
    item = _VectorResponseItem.model_validate(raw_item)
    if item.status != "SUCCESS" or item.object is None:
        raise ValueError(
            f"StatCan WDS error for vector {vector_id}: status={item.status!r}; "
            f"raw response item: {raw_item}"
        )

    points = item.object.vectorDataPoint
    if not points:
        # SUCCESS but empty - still produce an empty DataFrame; caller decides
        # whether that counts as a failure.
        df = pd.DataFrame(columns=["date", "value"])
        return StatCanFetchResult(vector_id=vector_id, data=df, release_date=None)

    df = pd.DataFrame(
        {
            "date": pd.to_datetime([p.refPer for p in points], errors="coerce"),
            "value": [p.value for p in points],
        }
    )
    df = df.sort_values("date").reset_index(drop=True)

    # Most-recent releaseTime among the observations; this is the upstream
    # vintage that gets pinned in .meta.json.release_date.
    release_dates = [p.releaseTime for p in points if p.releaseTime]
    if release_dates:
        release_date = pd.to_datetime(max(release_dates), errors="coerce")
        release_date_iso = release_date.date().isoformat() if pd.notna(release_date) else None
    else:
        release_date_iso = None

    return StatCanFetchResult(vector_id=vector_id, data=df, release_date=release_date_iso)


def table_url(table_id: str) -> str:
    """Return a human-readable StatCan table URL for inclusion in .meta.json.

    Pass a table ID like "18-10-0006-01" (the format used in StatCan's data tables).
    """
    return f"https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid={table_id.replace('-', '')[:10]}"
