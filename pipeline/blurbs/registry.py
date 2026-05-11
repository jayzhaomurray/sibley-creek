"""Release-key registry for the auto-blurb pipeline (Phase 1).

The registry maps every supported release-key (e.g. `cpi_monthly`) to the
set of surfaces that re-fire on that release plus the primary data-side
series IDs the researcher should read.

Phase 1 scope: `cpi_monthly` only. Panel 5 (expectations) is skipped because
CSCE / BOS are separate releases; Panel 6 (passthrough) is skipped because
the chart is broken (renders USDCAD instead of CPI passthrough) and will be
fixed in a separate dispatch.

The shape here is the contract `run.py` reads to drive a release-cycle's
fan-out. Adding a section (Phase 2: labour, policy) means adding an entry
here, not changing the orchestrator.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


SurfaceKind = Literal[
    "homepage_abstract",
    "topic_abstract",
    "sparkline_blurb",
    "active_headline",
    "chart_commentary",
]


class SurfaceSpec(BaseModel):
    """One surface in a release-cycle's fan-out.

    `path_template` is the on-disk path for the cycle artifact, relative to
    the repo root, with `{release_id}` placeholder. Section-level surfaces
    (topic abstract, sparkline, headline) live under `_topic-abstract`,
    `_sparkline`, `_headline` inside the section dir; per-panel chart
    commentary lives under the panel's slug. The homepage abstract lives
    under `_global/homepage-abstract`.
    """

    surface_id: str = Field(..., description="Stable id used for routing and tests.")
    kind: SurfaceKind
    section: str = Field(..., description="Section slug or '_global' for homepage.")
    unit_slug: str = Field(..., description="Directory name under the section.")
    char_cap: int
    word_range: tuple[int, int]
    sentence_range: tuple[int, int]
    path_template: str


class ReleaseKeySpec(BaseModel):
    """One upstream release-key (e.g. CPI monthly).

    `primary_meta_files` are the `data/processed/<name>.meta.json` paths
    whose `release_date` field is the trigger signal for this release-key.
    `series_inputs` are the CSV stems the researcher loads for context.

    `panels` is the fan-out gate: per-panel surfaces with `False` here are
    skipped this cycle. Phase 1 ships with panels 5 and 6 as `False` per
    the editorial-director's gate.
    """

    release_key: str
    section: str
    label: str
    primary_meta_files: list[str]
    series_inputs: list[str]
    panels: dict[str, bool]
    surfaces: list[SurfaceSpec]


# ---------------------------------------------------------------------------
# Phase 1: CPI monthly
# ---------------------------------------------------------------------------

_CPI_SURFACES: list[SurfaceSpec] = [
    SurfaceSpec(
        surface_id="homepage_abstract",
        kind="homepage_abstract",
        section="_global",
        unit_slug="homepage-abstract",
        char_cap=560,
        word_range=(60, 110),
        sentence_range=(3, 4),
        path_template="editorial/blurbs/_global/homepage-abstract/{release_id}.md",
    ),
    SurfaceSpec(
        surface_id="topic_abstract",
        kind="topic_abstract",
        section="inflation",
        unit_slug="_topic-abstract",
        char_cap=480,
        word_range=(45, 90),
        sentence_range=(2, 3),
        path_template="editorial/blurbs/inflation/_topic-abstract/{release_id}.md",
    ),
    SurfaceSpec(
        surface_id="sparkline_blurb",
        kind="sparkline_blurb",
        section="inflation",
        unit_slug="_sparkline",
        char_cap=120,
        word_range=(10, 25),
        sentence_range=(1, 2),
        path_template="editorial/blurbs/inflation/_sparkline/{release_id}.md",
    ),
    SurfaceSpec(
        surface_id="active_headline",
        kind="active_headline",
        section="inflation",
        unit_slug="_headline",
        char_cap=140,
        word_range=(8, 22),
        sentence_range=(1, 1),
        path_template="editorial/blurbs/inflation/_headline/{release_id}.md",
    ),
    SurfaceSpec(
        surface_id="panel_1_headline_cpi",
        kind="chart_commentary",
        section="inflation",
        unit_slug="panel-1-headline-cpi",
        char_cap=500,
        word_range=(25, 95),
        sentence_range=(2, 4),
        path_template="editorial/blurbs/inflation/panel-1-headline-cpi/{release_id}.md",
    ),
    SurfaceSpec(
        surface_id="panel_2_core_measures",
        kind="chart_commentary",
        section="inflation",
        unit_slug="panel-2-core-measures",
        char_cap=500,
        word_range=(25, 95),
        sentence_range=(2, 4),
        path_template="editorial/blurbs/inflation/panel-2-core-measures/{release_id}.md",
    ),
    SurfaceSpec(
        surface_id="panel_3_breadth",
        kind="chart_commentary",
        section="inflation",
        unit_slug="panel-3-breadth",
        char_cap=500,
        word_range=(25, 95),
        sentence_range=(2, 4),
        path_template="editorial/blurbs/inflation/panel-3-breadth/{release_id}.md",
    ),
    SurfaceSpec(
        surface_id="panel_4_subaggregates",
        kind="chart_commentary",
        section="inflation",
        unit_slug="panel-4-subaggregates",
        char_cap=500,
        word_range=(25, 95),
        sentence_range=(2, 4),
        path_template="editorial/blurbs/inflation/panel-4-subaggregates/{release_id}.md",
    ),
]


RELEASE_KEYS: dict[str, ReleaseKeySpec] = {
    "cpi_monthly": ReleaseKeySpec(
        release_key="cpi_monthly",
        section="inflation",
        label="Headline CPI",
        primary_meta_files=[
            "data/processed/cpi_all_items_yoy.meta.json",
            "data/processed/cpi_all_items_nsa_yoy.meta.json",
        ],
        series_inputs=[
            "cpi_all_items_yoy",
            "cpi_all_items_nsa_yoy",
            "cpi_trim_yoy",
            "cpi_median_yoy",
            "cpi_common_yoy",
            "cpi_shelter_yoy",
            "cpi_goods_yoy",
            "cpi_services_yoy",
            "cpi_food_yoy",
            "cpi_energy_yoy",
            "cpi_mortgage_interest_yoy",
        ],
        # Panel 5 (expectations) is a separate release (CSCE / BOS).
        # Panel 6 (passthrough) is broken (renders USDCAD); fixed elsewhere.
        panels={
            "panel-1-headline-cpi": True,
            "panel-2-core-measures": True,
            "panel-3-breadth": True,
            "panel-4-subaggregates": True,
            "panel-5-expectations": False,
            "panel-6-passthrough": False,
        },
        surfaces=_CPI_SURFACES,
    ),
}


def get_release_spec(release_key: str) -> ReleaseKeySpec:
    """Look up a release-key spec; raise KeyError with the registry list."""
    if release_key not in RELEASE_KEYS:
        raise KeyError(
            f"Unknown release_key {release_key!r}; registry has: "
            f"{sorted(RELEASE_KEYS)}"
        )
    return RELEASE_KEYS[release_key]


def parse_release_id(release_id: str) -> tuple[str, str]:
    """Split `cpi_monthly_2026-04` into (`cpi_monthly`, `2026-04`).

    Convention: release-key is everything before the last underscore-separated
    suffix that begins with a 4-digit year. Raises ValueError on malformed
    input.
    """
    parts = release_id.rsplit("_", 1)
    if len(parts) != 2 or not parts[1] or not parts[1][:4].isdigit():
        raise ValueError(
            f"Malformed release_id {release_id!r}; expected "
            f"<release_key>_<YYYY-MM> or <release_key>_<YYYY-MM-DD>"
        )
    return parts[0], parts[1]
