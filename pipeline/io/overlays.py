"""In-memory series overlays for shadow builds.

Overlay helpers are deliberately narrow: callers pass a map of one provisional
row per series, and the helper appends that row to the dataframe only when it is
newer than the canonical on-disk latest observation. It never writes to raw CSVs.
"""

from __future__ import annotations

from typing import Any, Optional

import pandas as pd


SeriesOverlayMap = dict[str, dict[str, Any]]


def apply_series_overlay(
    series_name: str,
    df: pd.DataFrame,
    meta: dict,
    overlays: Optional[SeriesOverlayMap],
) -> tuple[pd.DataFrame, dict, Optional[dict[str, Any]]]:
    """Return (df, meta, overlay_info) with a newer provisional row appended.

    If no overlay exists, or the overlay date is not newer than the canonical
    latest date, the input frame is returned unchanged and overlay_info is None.
    """
    if not overlays or series_name not in overlays:
        return df, meta, None

    point = overlays[series_name]
    overlay_date = pd.to_datetime(point.get("date"), errors="coerce")
    if pd.isna(overlay_date):
        return df, meta, None
    overlay_value = float(point["value"])

    out = df.copy()
    if "date" in out.columns and not out.empty:
        out["date"] = pd.to_datetime(out["date"], errors="coerce")
        latest_date = out["date"].dropna().max()
        if pd.notna(latest_date) and overlay_date <= latest_date:
            return df, meta, None

    appended = pd.DataFrame([{"date": overlay_date, "value": overlay_value}])
    out = pd.concat([out, appended], ignore_index=True, sort=False)
    out["date"] = pd.to_datetime(out["date"], errors="coerce")
    out = out.sort_values("date", kind="stable").reset_index(drop=True)

    overlay_info = {
        "date": overlay_date.date().isoformat(),
        "value": overlay_value,
        "status": point.get("status", "provisional"),
        "source": point.get("source"),
        "sourceUrl": point.get("sourceUrl"),
        "sourceId": point.get("sourceId"),
        "sourceKind": point.get("sourceKind"),
        "fetchedAt": point.get("fetchedAt"),
        "canonicalSource": meta.get("source"),
        "canonicalSourceUrl": meta.get("source_url"),
        "canonicalSourceId": meta.get("source_id"),
    }

    next_meta = dict(meta)
    next_meta["provisional_overlay"] = overlay_info
    next_meta["reference_period_end"] = overlay_info["date"]
    return out, next_meta, overlay_info
