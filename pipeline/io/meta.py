"""Sidecar metadata writer.

Every CSV the pipeline emits gets a sibling .meta.json. This is non-optional
and is the fact-checker's audit trail: source URL, fetched-at timestamp,
release date (when the upstream publisher released it), reference period
(what date the data point describes), units, schema version.

Schema is intentionally narrow and stable. Adding fields is fine; renaming
or removing fields bumps SCHEMA_VERSION.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import pandas as pd

SCHEMA_VERSION = 1


@dataclass
class SeriesMeta:
    """Metadata for one time series stored as <name>.csv + <name>.meta.json.

    Required fields:
        name:           short slug used in the filename (e.g. "cpi_all_items")
        source:         human-readable source name (e.g. "Statistics Canada WDS")
        source_url:     fully-qualified URL or stable identifier resolving to
                        the upstream release. For StatCan this is the table
                        URL; for Valet, the observations endpoint.
        source_id:      upstream identifier (e.g. StatCan vector ID, Valet
                        series key). Lets a fact-checker re-pull the exact
                        series without ambiguity.
        units:          human-readable units (e.g. "Index, 2002=100", "%",
                        "Persons", "CAD millions"). NOT a structured unit
                        system; this string is what appears next to chart axes.
        frequency:      "daily" | "weekly" | "monthly" | "quarterly" | "annual"
                        | "irregular". Editorial-grade; not enforced.

    Optional fields (fill where the source provides them):
        release_date:   date the upstream publisher released this vintage.
                        Different from fetched_at: a daily fetch will pull
                        the same release_date until the next publication.
        reference_period_start, reference_period_end:
                        the date range the dataset covers (oldest to newest
                        observation in the data).
        notes:          free-form gotchas, vintage caveats, SA/NSA flag, etc.
        transform:      if this file is the output of a transform, what
                        transform was applied (e.g. "yoy_pct", "rolling_mean_12").
                        Raw fetches leave this empty.
    """

    name: str
    source: str
    source_url: str
    source_id: str
    units: str
    frequency: str
    fetched_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    release_date: Optional[str] = None
    reference_period_start: Optional[str] = None
    reference_period_end: Optional[str] = None
    notes: Optional[str] = None
    transform: Optional[str] = None
    schema_version: int = SCHEMA_VERSION

    def to_dict(self) -> dict:
        return asdict(self)


def write_series(
    df: pd.DataFrame,
    meta: SeriesMeta,
    out_dir: Path,
    date_col: str = "date",
) -> tuple[Path, Path]:
    """Write a DataFrame as <name>.csv and a sibling <name>.meta.json.

    Auto-derives reference_period_start / reference_period_end from the
    DataFrame's date column if they're not already set on meta. The CSV is
    written index=False so it stays diff-friendly and human-inspectable.

    Returns:
        (csv_path, meta_path)
    """
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    if date_col in df.columns and not df.empty:
        # pandas Timestamps -> ISO date strings, ignoring NaT
        valid_dates = pd.to_datetime(df[date_col], errors="coerce").dropna()
        if not valid_dates.empty:
            if meta.reference_period_start is None:
                meta.reference_period_start = valid_dates.min().date().isoformat()
            if meta.reference_period_end is None:
                meta.reference_period_end = valid_dates.max().date().isoformat()

    csv_path = out_dir / f"{meta.name}.csv"
    meta_path = out_dir / f"{meta.name}.meta.json"

    df.to_csv(csv_path, index=False)
    meta_path.write_text(json.dumps(meta.to_dict(), indent=2, sort_keys=False))

    return csv_path, meta_path


def write_series_merge(
    df: pd.DataFrame,
    meta: SeriesMeta,
    out_dir: Path,
    date_col: str = "date",
) -> tuple[Path, Path]:
    """Write a DataFrame as <name>.csv merged with any existing CSV at that path.

    Like `write_series`, but if an existing CSV is present at
    `out_dir/<name>.csv`, the new frame is UNION-MERGED with it by date:
        - dates in both old + new: prefer the new value (upstream revisions)
        - dates in old only:        keep the old row (preserve history)
        - dates in new only:        append the new row
        - result is sorted by date

    Use this for fetchers where the upstream source has been observed to
    occasionally return a shorter / lower-cadence response than the on-disk
    history (e.g. Yahoo's `range=max` returning monthly aggregations for
    older periods on certain futures symbols). A direct overwrite in that
    case would silently truncate the daily history.

    The meta sidecar is written from scratch (NOT merged); it reflects the
    union frame's reference period and the current fetched_at. Caller's
    `meta` should describe the SOURCE the new rows came from -- because
    going forward, all new data lands from that source.

    Notes:
        - If the existing CSV has columns the new frame lacks (or vice
          versa), the union is taken on the shared columns plus all extras
          (NaN-filled where missing). Callers should keep the schema stable
          across runs.
        - Date parsing uses pd.to_datetime; mixed-format strings in the
          existing CSV are coerced. Bad rows (un-parseable date) are kept
          but sorted to the end and may produce duplicate (date=NaT) rows.

    Returns:
        (csv_path, meta_path)
    """
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    csv_path = out_dir / f"{meta.name}.csv"

    if csv_path.exists():
        existing = pd.read_csv(csv_path)
        if date_col in existing.columns:
            existing[date_col] = pd.to_datetime(existing[date_col], errors="coerce")
        merged = _merge_by_date(existing, df, date_col=date_col)
    else:
        merged = df.copy()

    if date_col in merged.columns:
        merged[date_col] = pd.to_datetime(merged[date_col], errors="coerce")
        merged = merged.sort_values(date_col, kind="stable").reset_index(drop=True)

    return write_series(merged, meta, out_dir, date_col=date_col)


def _merge_by_date(
    old: pd.DataFrame,
    new: pd.DataFrame,
    date_col: str = "date",
) -> pd.DataFrame:
    """Union-merge `old` and `new` by date column, preferring `new` on overlap.

    Internal helper for `write_series_merge`. Keeps every row from `old`
    whose date does not appear in `new`, then appends every row of `new`.
    """
    if date_col not in old.columns or old.empty:
        return new.copy()
    if date_col not in new.columns or new.empty:
        return old.copy()

    new_dates = pd.to_datetime(new[date_col], errors="coerce")
    old_dates = pd.to_datetime(old[date_col], errors="coerce")

    keep_old_mask = ~old_dates.isin(set(new_dates.dropna()))
    kept_old = old.loc[keep_old_mask].copy()
    fresh = new.copy()

    # Normalize date dtype across both halves so the concat doesn't produce
    # an object-dtype date column.
    kept_old[date_col] = pd.to_datetime(kept_old[date_col], errors="coerce")
    fresh[date_col] = pd.to_datetime(fresh[date_col], errors="coerce")

    combined = pd.concat([kept_old, fresh], ignore_index=True, sort=False)
    combined = combined.sort_values(date_col, kind="stable").reset_index(drop=True)
    return combined
