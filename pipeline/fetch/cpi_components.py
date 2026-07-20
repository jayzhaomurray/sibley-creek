"""CPI component-level fetcher for breadth analysis (StatCan Table 18-10-0004-01).

This module fetches 60 per-component NSA CPI index levels from StatCan WDS
and reshapes them into the wide-format CSV consumed by the two CPI breadth
derivations:

    derive_cpi_breadth_gt3()   -- share of basket with Y/Y > 3%
    derive_cpi_breadth_band()  -- BoC-recipe above-3 / below-1 shares

Output shape
------------
    date  |  Meat  |  Fish, seafood ...  |  ...  (60 component columns)

All columns are NSA per-component CPI index levels (2002=100) -- the same
shape that was previously produced by the one-time boc-tracker lift.

Vector registry
---------------
The 60 vectors and their component names are loaded from
`pipeline/catalog/cpi_breadth_mapping.json`, vendored into this repo (copied
verbatim from boc-tracker/data/cpi_breadth_mapping.json on 2026-05-11; see
`data/derived/cpi_component_weights_canada.meta.json` for the lift record).

That file is the canonical source of truth for the vector-to-name mapping.
If it is not present at build time the fetch raises immediately (the
derivations that follow depend on this data and should not run stale).

NOTE (2026-07-20 incident): this used to point at the absolute path
`C:/Users/jayzh/Documents/boc-tracker/data/cpi_breadth_mapping.json` on the
author's machine. That worked locally (the file exists there) but does not
exist on any CI runner, so every `build-data-daily` run raised
FileNotFoundError here from 2026-05-20 onward -- and because `pipeline.build`
fails the whole build on any single fetcher failure, this alone blocked
every scheduled data refresh for two months even though 80+ other series
were fetching fine. Fixed by vendoring the mapping into the repo itself so
there is no machine-local dependency. If this file ever needs to be
regenerated from a fresher boc-tracker lift, copy the JSON in whole --
do not hand-edit vector IDs.

Batching strategy
-----------------
WDS `getDataFromVectorsAndLatestNPeriods` accepts all 60 vectors in a single
POST. We batch them in one round-trip rather than one request per vector.
If any individual vector fails WDS validation, `fetch_vectors` raises on
that item; we surface the failure to the caller rather than silently omitting
a component.

Staleness guard
---------------
`fetch_cpi_components` raises if the batch returns fewer than 55 vectors
with data (a hard floor below which the breadth derivation is meaningless).
This is distinct from individual missing months within a vector, which are
represented as NaN and handled gracefully by the derivations.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import pandas as pd

from pipeline.fetch.statcan import fetch_vectors

logger = logging.getLogger(__name__)

TABLE_ID = "18-10-0004-01"
TABLE_URL = "https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1810000401"

# Path to the canonical vector-to-name mapping, vendored into this repo
# (see module docstring "Vector registry" for provenance). Resolved relative
# to this file so it works identically on any machine / CI runner --
# previously an absolute path onto the author's local disk, which is why
# every CI run raised FileNotFoundError (see 2026-07-20 incident note above).
# Exposed as a module constant so the build step can report it in the
# .meta.json source_id without re-reading the file.
MAPPING_PATH = Path(__file__).resolve().parents[1] / "catalog" / "cpi_breadth_mapping.json"

# Minimum number of vectors that must return data for the result to be
# considered usable. 55 of 60 is a conservative threshold; real-world
# gaps are usually 0-1 vectors for newly introduced sub-categories.
MIN_VECTOR_COUNT = 55

# How far back to pull. 600 observations ~ 50 years of monthly data;
# well beyond what the derivation needs (it starts 1995 for the BoC recipe)
# and within WDS per-request limits.
LATEST_N = 600


@dataclass(frozen=True)
class CpiComponentsResult:
    """Output of `fetch_cpi_components()`.

    wide: wide-format DataFrame with columns:
        date | <component_name_1> | <component_name_2> | ...
        Each component column contains NSA index levels (2002=100).
        NaN cells represent months where WDS returned NULL for that component.

    release_date: maximum upstream releaseTime across all 60 vectors,
        ISO date string; None if WDS did not return release dates.

    source_id: string identifying the batch of vectors, suitable for
        .meta.json source_id (e.g. "cube:18100004; 60 vectors").
    """

    wide: pd.DataFrame
    release_date: Optional[str]
    source_id: str


def load_mapping(mapping_path: Path = MAPPING_PATH) -> list[dict]:
    """Load and validate the cpi_breadth_mapping.json.

    Raises:
        FileNotFoundError if the mapping file is absent.
        ValueError if the file is malformed or contains fewer than 55 entries.
    """
    if not mapping_path.exists():
        raise FileNotFoundError(
            f"CPI breadth mapping not found: {mapping_path}. "
            "This file must exist for the CPI components fetch to proceed. "
            "It is vendored at pipeline/catalog/cpi_breadth_mapping.json; if it "
            "went missing, restore it from git history rather than re-pointing "
            "at a machine-local path."
        )
    raw = json.loads(mapping_path.read_text(encoding="utf-8"))
    if not isinstance(raw, list) or len(raw) < MIN_VECTOR_COUNT:
        raise ValueError(
            f"cpi_breadth_mapping.json: expected a list of >= {MIN_VECTOR_COUNT} entries, "
            f"got {type(raw).__name__} with {len(raw) if isinstance(raw, list) else 'n/a'} items."
        )
    # Validate required keys on a sample to catch schema drift early.
    for i, entry in enumerate(raw[:3]):
        for key in ("name", "cpi_vector"):
            if key not in entry:
                raise ValueError(
                    f"cpi_breadth_mapping.json entry {i} missing required key {key!r}. "
                    "Schema may have changed; re-verify against boc-tracker source."
                )
    return raw


def fetch_cpi_components(
    mapping_path: Path = MAPPING_PATH,
    *,
    latest_n: int = LATEST_N,
) -> CpiComponentsResult:
    """Fetch 60 per-component CPI index levels from StatCan WDS.

    Loads the vector-to-name mapping from `mapping_path`, batches all vectors
    in one WDS request, and reshapes the result to wide format with exact
    component name columns matching what `derive_cpi_breadth_gt3` and
    `derive_cpi_breadth_band` expect.

    Args:
        mapping_path: path to cpi_breadth_mapping.json (default: vendored copy
            at pipeline/catalog/cpi_breadth_mapping.json).
        latest_n: number of most-recent monthly observations to pull per vector.

    Returns:
        CpiComponentsResult with `wide` DataFrame in the canonical shape.

    Raises:
        FileNotFoundError: mapping file is missing.
        ValueError: fewer than MIN_VECTOR_COUNT vectors returned usable data.
        ValueError: WDS returns error status for any vector in the batch.
    """
    mapping = load_mapping(mapping_path)

    # Build vector_id -> component_name map. Duplicate names (none expected
    # in this dataset) would produce column collisions; detect and raise.
    vid_to_name: dict[int, str] = {}
    seen_names: dict[str, int] = {}
    for entry in mapping:
        vid = int(entry["cpi_vector"])
        name = str(entry["name"])
        if name in seen_names:
            raise ValueError(
                f"Duplicate component name {name!r} (vectors {seen_names[name]} and {vid}). "
                "cpi_breadth_mapping.json has changed; verify before proceeding."
            )
        vid_to_name[vid] = name
        seen_names[name] = vid

    vector_ids = list(vid_to_name)
    logger.info(
        "cpi_components: fetching %d vectors from StatCan Table %s",
        len(vector_ids),
        TABLE_ID,
    )

    results = fetch_vectors(vector_ids, latest_n=latest_n)

    # Pivot to wide: one column per component, indexed by date.
    series_map: dict[str, pd.Series] = {}
    release_dates: list[str] = []
    empty_vectors: list[str] = []

    for vid, res in results.items():
        name = vid_to_name[vid]
        if res.release_date:
            release_dates.append(res.release_date)
        if res.data.empty:
            logger.warning(
                "cpi_components: vector v%d (%s) returned SUCCESS but no data",
                vid,
                name,
            )
            empty_vectors.append(name)
            continue
        # res.data has columns [date, value]; set date as index for the pivot.
        s = res.data.set_index("date")["value"].rename(name)
        series_map[name] = s

    n_populated = len(series_map)
    if n_populated < MIN_VECTOR_COUNT:
        raise ValueError(
            f"cpi_components: only {n_populated} of {len(vector_ids)} vectors "
            f"returned data (minimum required: {MIN_VECTOR_COUNT}). "
            f"Empty vectors: {sorted(empty_vectors)}. "
            "Check StatCan WDS for table reorganization or retired vectors."
        )

    if empty_vectors:
        logger.warning(
            "cpi_components: %d vector(s) returned no data and will be NaN in output: %s",
            len(empty_vectors),
            sorted(empty_vectors),
        )

    # Concatenate into a wide DataFrame. The concat produces a DataFrame
    # with one column per component and the union of all dates as the index.
    # Missing component/date intersections become NaN automatically.
    wide = pd.concat(series_map.values(), axis=1)
    wide = wide.sort_index()
    wide.index.name = "date"
    wide = wide.reset_index()

    # Enforce column order: date first, then components in mapping order.
    ordered_names = [vid_to_name[v] for v in vector_ids if vid_to_name[v] in wide.columns]
    missing_cols = [vid_to_name[v] for v in vector_ids if vid_to_name[v] not in wide.columns]
    # missing_cols are the empty vectors; insert them as NaN columns to
    # preserve the full 60-column schema even when a vector has no data.
    for col in missing_cols:
        wide[col] = float("nan")
    wide = wide[["date"] + ordered_names + missing_cols]

    release_date = max(release_dates) if release_dates else None

    source_id = (
        f"Table {TABLE_ID}; "
        f"{len(vector_ids)} vectors from cpi_breadth_mapping.json"
    )

    logger.info(
        "cpi_components: assembled wide frame %d rows x %d component columns; "
        "latest date: %s; release_date: %s",
        len(wide),
        len(wide.columns) - 1,  # exclude the date column
        wide["date"].max().date().isoformat() if not wide.empty else "n/a",
        release_date or "n/a",
    )

    return CpiComponentsResult(wide=wide, release_date=release_date, source_id=source_id)
