"""Release-key registry for the auto-blurb pipeline.

The registry maps every supported release-key (e.g. `cpi_monthly`) to the
set of surfaces that re-fire on that release plus the primary data-side
series IDs the researcher should read.

Scope (2026-05-12 extension): one release-key per section across all
seven Sibley Creek sections -- `cpi_monthly` (inflation), `lfs_monthly`
(labour), `gdp_monthly` (gdp), `crea_monthly` (housing), `markets_daily`
(markets), `boc_decision` (policy), `trade_monthly` (trade). Plate
inventories come from `pipeline/blurbs/section_context.py`; that module
is the single source of truth for "what plates live on the
`<section>.astro` page right now."

Per-section surfaces:
  - one homepage abstract (`<section>_homepage_abstract`) -- the splash
    hero is rewritten on every section's release (writing-style.md
    Section 8b: hero synthesises from section blurbs)
  - one section-page abstract (`<section>_topic_abstract`)
  - one section sparkline (the splash tile-line for that section)
  - one active headline (the section page's hero line)
  - one plate-interpretation surface per plate in the section's
    `plate_inventory`

The shape here is the contract `run.py` reads to drive a release-cycle's
fan-out. Adding a section means adding a `SectionContext` entry in
section_context.py plus a `ReleaseKeySpec` here; the orchestrator stays
section-agnostic.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from pipeline.blurbs.section_context import (
    SECTION_CONTEXTS,
    SectionContext,
)


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


# ---------------------------------------------------------------------------
# Standard length budgets (mirrors voice canon in editorial/writing-style.md)
# ---------------------------------------------------------------------------
#
# These caps are shared across every section -- the writer's job is the
# same shape regardless of which release fires. If editorial canon
# updates a budget, change it here once and every section's spec follows.

_BUDGET_HOMEPAGE_ABSTRACT = dict(
    char_cap=560, word_range=(60, 110), sentence_range=(3, 4),
)
_BUDGET_TOPIC_ABSTRACT = dict(
    char_cap=480, word_range=(45, 90), sentence_range=(2, 3),
)
_BUDGET_SPARKLINE_BLURB = dict(
    char_cap=120, word_range=(10, 25), sentence_range=(1, 2),
)
_BUDGET_ACTIVE_HEADLINE = dict(
    char_cap=140, word_range=(8, 22), sentence_range=(1, 1),
)
_BUDGET_CHART_COMMENTARY = dict(
    char_cap=500, word_range=(25, 95), sentence_range=(2, 4),
)


def _build_section_surfaces(ctx: SectionContext) -> list[SurfaceSpec]:
    """Generate the canonical surface set for one section.

    Generated set per section:
      - one homepage_abstract (the splash hero abstract; rewritten on
        every section's release because the hero synthesises from
        section blurbs per writing-style 8b)
      - one topic_abstract (the section page's abstract)
      - one sparkline_blurb (the splash tile-line for that section)
      - one active_headline (the section page's hero line)
      - N chart_commentary surfaces (one per plate in
        ctx.plate_inventory)

    Surface IDs are namespaced by section slug to avoid collisions
    across the registry. Inflation keeps its legacy surface IDs
    (`panel_1_headline_cpi` etc) because those are referenced by
    `.claude/commands/auto-blurb-researcher.md` and existing tests.
    """
    s = ctx.section_slug

    surfaces: list[SurfaceSpec] = [
        SurfaceSpec(
            surface_id=f"{s}_homepage_abstract",
            kind="homepage_abstract",
            section="_global",
            unit_slug="homepage-abstract",
            path_template=(
                "editorial/blurbs/_global/homepage-abstract/{release_id}.md"
            ),
            **_BUDGET_HOMEPAGE_ABSTRACT,
        ),
        SurfaceSpec(
            surface_id=f"{s}_topic_abstract",
            kind="topic_abstract",
            section=s,
            unit_slug="_topic-abstract",
            path_template=(
                f"editorial/blurbs/{s}/_topic-abstract/{{release_id}}.md"
            ),
            **_BUDGET_TOPIC_ABSTRACT,
        ),
        SurfaceSpec(
            surface_id=f"{s}_sparkline_blurb",
            kind="sparkline_blurb",
            section=s,
            unit_slug="_sparkline",
            path_template=(
                f"editorial/blurbs/{s}/_sparkline/{{release_id}}.md"
            ),
            **_BUDGET_SPARKLINE_BLURB,
        ),
        SurfaceSpec(
            surface_id=f"{s}_active_headline",
            kind="active_headline",
            section=s,
            unit_slug="_headline",
            path_template=(
                f"editorial/blurbs/{s}/_headline/{{release_id}}.md"
            ),
            **_BUDGET_ACTIVE_HEADLINE,
        ),
    ]
    for plate in ctx.plate_inventory:
        surfaces.append(SurfaceSpec(
            surface_id=f"{s}_{plate.surface_slug.replace('-', '_')}",
            kind="chart_commentary",
            section=s,
            unit_slug=plate.surface_slug,
            path_template=(
                f"editorial/blurbs/{s}/{plate.surface_slug}/{{release_id}}.md"
            ),
            **_BUDGET_CHART_COMMENTARY,
        ))
    return surfaces


def _build_panels_map(ctx: SectionContext) -> dict[str, bool]:
    """Default every plate to True for non-inflation sections.

    The inflation `cpi_monthly` keeps its hand-curated panels map below
    (panel-5 expectations and panel-6 passthrough are gated False).
    Other sections currently have no gate exclusions; if one shows up,
    flip the bit here.
    """
    return {plate.surface_slug: True for plate in ctx.plate_inventory}


# ---------------------------------------------------------------------------
# Per-section release-key registrations
# ---------------------------------------------------------------------------

# Inflation: keeps legacy surface IDs (`panel_1_headline_cpi` etc) that the
# .claude/commands/auto-blurb-researcher.md template references explicitly
# and that the existing CPI cycle artifacts are written under. Do NOT
# rename without porting the prompt template + any landed cycles.
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


# ---------------------------------------------------------------------------
# Section -> release-key registration (generated from section_context)
# ---------------------------------------------------------------------------
#
# Labour / GDP / Housing / Markets / Policy / Trade share a generated
# surface set; the per-section context object is the single source of
# truth for plates, primary series, and canonical sources. The inflation
# entry above is hand-curated for backwards compatibility with the
# Phase 1 surface IDs that the researcher template references.

_SECTION_LABELS_FOR_RELEASE: dict[str, str] = {
    "labour": "LFS monthly print",
    "gdp": "Monthly GDP print",
    "housing": "CREA monthly print",
    "markets": "Daily market close",
    "monetary": "BoC rate decision",
    "trade": "Monthly international trade",
}

for _section_slug, _ctx in SECTION_CONTEXTS.items():
    if _ctx.release_key in RELEASE_KEYS:
        # Inflation already registered hand-curated above.
        continue
    RELEASE_KEYS[_ctx.release_key] = ReleaseKeySpec(
        release_key=_ctx.release_key,
        section=_ctx.section_slug,
        label=_SECTION_LABELS_FOR_RELEASE.get(_section_slug, _ctx.label),
        primary_meta_files=list(_ctx.primary_meta_files),
        series_inputs=list(_ctx.series_inputs),
        panels=_build_panels_map(_ctx),
        surfaces=_build_section_surfaces(_ctx),
    )


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
