"""CPI basket-weights fetcher (StatCan Table 18-10-0007-01).

Per W3-R2 (researcher GO decision, 2026-05-11), the inflation pass-through
panel (canon 4.2 element 6) is gated on landing CPI major-aggregate basket
weights. This module is the bridge: it batches a small set of pre-resolved
basket-weight vectors from StatCan WDS into a long-format DataFrame, with
a wide convenience view available for chart-builder.

Why a dedicated module
----------------------
Basket weights are a different shape from price-index time series:
    - Cadence is "publish on basket refresh" (~once per year since 2022;
      every five years before that). The current 2024 basket applies
      through ~2029.
    - The "value" is a weight share (% of the all-items basket), not a
      price level. Y/Y change is meaningless.
    - Each observation row in the long format is (basket_year,
      major_aggregate, weight_pct).

The major-aggregate set we lift here is the editorial-canonical set used
by the pass-through panel:
    - All-items (denominator; always 100.00)
    - Food
    - Shelter
    - Energy
    - Goods (total, includes food-purchased-from-stores)
    - Services (total, includes shelter services)
    - Goods excluding food purchased from stores and energy
      (closest StatCan-published aggregate to "goods ex-energy" --
      the chart layer can derive the precise "goods ex-energy" slice
      as Goods - Energy if it needs the simpler decomposition)
    - All-items excluding food and energy (core scope)
    - All-items excluding shelter

Provenance
----------
Vector resolution was done 2026-05-11 via WDS
`getSeriesInfoFromCubePidCoord`; resolutions are pinned in the StatCan
catalog as separate `cpi_basket_weight_*` entries. This module simply
groups them so the consolidated view lands as a single derived CSV.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Iterable

import pandas as pd

from pipeline.fetch.statcan import fetch_vectors

logger = logging.getLogger(__name__)

TABLE_ID = "18-10-0007-01"
TABLE_URL = "https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1810000701"

# Major-aggregate basket-weight vectors for Canada, "Distribution to selected
# geographies" (Dim4=1), "Weight at basket link month prices" (Dim3=1).
# Each (vector_id, aggregate_label) pair is the source of truth for the
# consolidated derived CSV; canonical names mirror the slugs in
# `pipeline.catalog.statcan_series` for fact-checker cross-reference.
MAJOR_AGGREGATES: dict[str, int] = {
    "all_items":                  91858736,
    "food":                       91858740,
    "shelter":                    91858892,
    "energy":                     91859272,
    "goods":                      91859278,
    "services":                   91873252,
    "goods_ex_food_energy":       91859292,
    "all_items_ex_food_energy":   91859248,
    "all_items_ex_shelter":       91859258,
    # services_ex_shelter (v91859296) is registered in the catalog but its WDS
    # values are NULL at this slice; we omit it from the consolidated view and
    # rely on chart-layer derivation (services - shelter).
}


@dataclass(frozen=True)
class BasketWeightsResult:
    """Output of `fetch_basket_weights()`.

    long: long-format DataFrame with columns
        date (basket reference year as Jan-1 Timestamp),
        aggregate (the slug, e.g. "shelter"),
        weight_pct (% share of all-items basket).
    wide: same data pivoted with aggregates as columns; convenient for
        chart-builder when each row is one basket cycle.
    release_date: maximum upstream releaseTime across the major aggregates,
        ISO date string; None if WDS did not return one.
    """

    long: pd.DataFrame
    wide: pd.DataFrame
    release_date: str | None


def fetch_basket_weights(
    aggregates: Iterable[str] | None = None,
    *,
    latest_n: int = 50,
) -> BasketWeightsResult:
    """Pull major-aggregate basket weights from StatCan WDS.

    Args:
        aggregates: optional subset of keys from MAJOR_AGGREGATES (e.g. just
            the five panel-6 series). Default is all major aggregates wired.
        latest_n: number of basket cycles to pull. The table currently has
            ~8 cycles (2017-2024); 50 is a comfortable cap.

    Returns:
        BasketWeightsResult. Rows where StatCan returned NULL are preserved
        as NaN in `weight_pct` so the caller can see the gap (rather than
        silently dropping). The denominator row (`all_items`) always
        contains 100.00 by construction.

    Raises:
        ValueError if WDS rejects any of the underlying vectors. (Failure
        of one vector indicates a basket-table reorganization; that is the
        kind of issue we want to surface loudly, not paper over.)
    """
    selected = list(aggregates) if aggregates is not None else list(MAJOR_AGGREGATES)
    unknown = sorted(set(selected) - set(MAJOR_AGGREGATES))
    if unknown:
        raise ValueError(
            f"Unknown basket aggregate slugs requested: {unknown}. "
            f"Allowed: {sorted(MAJOR_AGGREGATES)}"
        )
    vector_to_slug = {MAJOR_AGGREGATES[s]: s for s in selected}
    results = fetch_vectors(list(vector_to_slug), latest_n=latest_n)

    frames: list[pd.DataFrame] = []
    release_dates: list[str] = []
    for vid, res in results.items():
        slug = vector_to_slug[vid]
        if res.release_date:
            release_dates.append(res.release_date)
        if res.data.empty:
            logger.warning(
                "cpi basket: vector v%d (%s) returned SUCCESS but no data", vid, slug
            )
            continue
        block = res.data.copy()
        block["aggregate"] = slug
        block = block.rename(columns={"value": "weight_pct"})[
            ["date", "aggregate", "weight_pct"]
        ]
        frames.append(block)

    if not frames:
        long = pd.DataFrame(columns=["date", "aggregate", "weight_pct"])
        wide = pd.DataFrame()
    else:
        long = (
            pd.concat(frames, ignore_index=True)
            .sort_values(["date", "aggregate"])
            .reset_index(drop=True)
        )
        wide = (
            long.pivot_table(
                index="date", columns="aggregate", values="weight_pct", aggfunc="first"
            )
            .reset_index()
            .rename_axis(None, axis=1)
        )

    release_date = max(release_dates) if release_dates else None
    return BasketWeightsResult(long=long, wide=wide, release_date=release_date)
