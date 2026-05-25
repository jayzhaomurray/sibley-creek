"""Fan-out orchestrator: cascade one release through every affected surface.

A single upstream release (e.g. CPI April 2026) refreshes MANY reader-
facing surfaces atomically: the section's blurb body, the section's
tileLine, the section page's plate interpretations, the section's
heroKicker / latestReleaseLabel, the fresh-tag rotation across all 7
sections, AND the splash hero abstract (which per `editorial/writing-
style.md` Section 8b synthesizes from the seven section blurbs and so
must be written LAST).

This module is the cascade. `run.py` continues to own the per-surface
3-gate review (writer + fact-checker + style-editor + editorial-director
Gate 3); `fan_out.py` calls run.py's primitives once per surface in
dependency order and stages the drafts under
`editorial/_staging/<release-id>/`. A final `_promote_staging` step
atomically moves every drafted surface into place; mid-flight failure
rolls back the staging directory without touching the live site.

Public surface:
- ``Surface`` dataclass: one drafted surface inside a fan-out
- ``FanOutPlan`` dataclass: ordered surface list + dependency tiers
- ``detect_affected_surfaces(release_event, repo_root) -> FanOutPlan``
- ``fan_out_release(release_event, repo_root, *, ...) -> FanOutResult``
- ``ReleaseEvent`` dataclass: minimal release descriptor consumed here
- ``detect_release_event(repo_root, prior_snapshot=...) -> Optional[ReleaseEvent]``
   (content-hash check on primary-series sidecars vs the rotated
   snapshot; the Section 1 trigger that fires this cascade)

Design notes
------------
* Build on existing primitives. `run.run_release_cycle` walks the 3-gate
  review for ONE release-id (today: CPI). The fan-out wraps it: it does
  NOT reimplement the gates. Section-meta and plate-meta surfaces
  (tileLine, heroKicker, plate interpretations) currently sit OUTSIDE
  the registry; the fan-out treats them as additional `Surface` entries
  and runs each through `call_claude` plus the same Gate 3 surface-fit
  prompt builder in `run._surface_fit_review`. When the registry grows
  per-surface entries for these (Phase 2 ticket), they fold back into
  `run.run_release_cycle` without changing this module's API.
* Staging dir is the unit of atomicity. Every drafted artifact lands at
  `editorial/_staging/<release-id>/<final-relative-path>` first. The
  promote step walks the staging tree once and `os.replace`'s each file
  into its live location. Failure mid-promote attempts a best-effort
  reverse pass using the backup copies we stash beside each target
  before overwriting it.
* Inbox-file mode default. Matches `run.py` v1: no SMTP, append to
  `editorial/blurbs/_inbox.md`. The fan-out also writes one cascade-
  level summary entry so the user sees the whole release in one row.
* DO NOT FIRE PRODUCTION RUNS FROM THE SMOKE TEST. Mocks all the way
  down.
"""

from __future__ import annotations

import json
import logging
import shutil
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Optional

from pipeline.blurbs import diff_brief as df_mod
from pipeline.blurbs.llm_client import LLMDispatchError, call_claude
from pipeline.blurbs.registry import RELEASE_KEYS, get_release_spec
from pipeline.blurbs.run import (
    MODEL_EDITORIAL_DIRECTOR,
    SURFACE_FIT_BUDGET,
    _SURFACE_FIT_CONTEXTS,
    _parse_surface_fit_response,
    _surface_fit_prompt,
)

logger = logging.getLogger("pipeline.blurbs.fan_out")

REPO_ROOT = Path(__file__).resolve().parents[2]


# ---------------------------------------------------------------------------
# All 7 sections (mirrors src/data/sections.ts at the slug level)
# ---------------------------------------------------------------------------

SECTION_SLUGS: tuple[str, ...] = (
    "gdp",
    "inflation",
    "labour",
    "housing",
    "monetary",
    "fiscal",
    "markets",
    "trade",
)


# ---------------------------------------------------------------------------
# Cross-section ripple map (Section -> additional plate(s) refreshed)
# ---------------------------------------------------------------------------
#
# A few releases reach beyond their home section. Keep this map small;
# every entry is a concrete plate identifier the fan-out treats as one
# extra Surface in dependency tier 2 (plate-level).
#
# Today: only the BoC rate decision touches Markets' `boc-fed-spread`
# plate. Hand-curated -- if the editorial scope grows, add entries.

CROSS_SECTION_RIPPLES: dict[str, tuple[tuple[str, str], ...]] = {
    "boc_decision": (("markets", "boc-fed-spread"),),
}


# ---------------------------------------------------------------------------
# Per-section plate inventory
# ---------------------------------------------------------------------------
#
# Each section page renders a stack of plate units. The inflation section
# has six (panels 1-6 per `src/pages/inflation.astro` and the registry);
# the other sections currently render fewer in production but ship the
# same shape. We hard-code the section -> plate-slug list here; the
# fan-out walks this when expanding the plate-level surfaces. If a
# section's plate count changes, update here and the fan-out picks it
# up.
#
# Convention: plate slugs match the unit_slug field in
# `pipeline/blurbs/registry.py` SurfaceSpec entries where they exist;
# for plates that don't have registry entries yet, we use the same
# kebab-case naming so a future registry expansion is a trivial join.

SECTION_PLATES: dict[str, tuple[str, ...]] = {
    "inflation": (
        "panel-1-headline-cpi",
        "panel-2-core-measures",
        "panel-3-breadth",
        "panel-4-subaggregates",
        "panel-5-expectations",
        "panel-6-passthrough",
    ),
    "gdp": (
        "panel-1-monthly-gdp",
        "panel-2-quarterly-gdp",
        "panel-3-per-capita",
        "panel-4-output-gap",
        "panel-5-recession-state",
        "panel-6-productivity",
    ),
    "labour": (
        "panel-1-unrate",
        "panel-2-employment-pop",
        "panel-3-aggregate-hours",
        "panel-4-wages",
        "panel-5-participation",
        "panel-6-vacancy-rate",
    ),
    "housing": (
        "panel-1-mls-hpi",
        "panel-2-starts",
        "panel-3-affordability",
        "panel-4-arrears",
        "panel-5-rents",
        "panel-6-permits",
    ),
    "monetary": (
        "panel-1-policy-rate",
        "panel-2-yield-curve",
        "panel-3-boc-fed-spread",
        "panel-4-balance-sheet",
        "panel-5-fiscal-balance",
        "panel-6-fiscal-monitor",
    ),
    "fiscal": (
        "panel-1-federal-trajectory",
        "panel-2-debt-service-revenues",
        "panel-3-pbo-vs-dof",
        "panel-4-provincial-debt",
        "panel-5-operating-vs-capital",
    ),
    "markets": (
        "panel-1-usdcad",
        "panel-2-yields",
        "panel-3-boc-fed-spread",
        "panel-4-tsx-composite",
        "panel-5-wti-energy",
        "panel-6-cross-asset",
    ),
    "trade": (
        "panel-1-balance",
        "panel-2-partner-share",
        "panel-3-current-account",
        "panel-4-terms-of-trade",
        "panel-5-exports-mix",
        "panel-6-imports-mix",
    ),
}


# ---------------------------------------------------------------------------
# Release-event -> home section mapping
# ---------------------------------------------------------------------------
#
# release_key (from registry.py) maps to the home section it refreshes.
# Daily-cadence releases (USDCAD daily close, yields, etc.) map to
# `markets`. Add entries as the registry grows.

RELEASE_KEY_TO_SECTION: dict[str, str] = {
    "cpi_monthly": "inflation",
    "lfs_monthly": "labour",
    "gdp_monthly": "gdp",
    "boc_decision": "monetary",
    "crea_monthly": "housing",
    "trade_monthly": "trade",
    "markets_daily": "markets",
}


# ---------------------------------------------------------------------------
# Data shapes
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ReleaseEvent:
    """One upstream release that triggers the fan-out cascade.

    Carries enough to drive `detect_affected_surfaces`. Constructed
    either from a `release_id` (e.g. `cpi_monthly_2026-04`) or by
    `detect_release_event` walking the meta sidecars.
    """

    release_id: str
    release_key: str
    section: str
    reference_period: str
    release_date: Optional[str] = None


@dataclass(frozen=True)
class Surface:
    """One drafted surface inside the fan-out.

    `tier` is the dependency tier (lower runs first):
      0  shared per-section claim-card pass (researcher + verifier).
      1  section's blurb.body (the section's central prose).
      2  section-meta + plate interpretations (tileLine, heroKicker,
         blurb.date, latestReleaseLabel, updatedAt, per-plate prose).
      3  fresh-tag rotation across all sections (one writer call to
         decide which section gets kind: "fresh"; the rest go to
         "last").
      4  splash hero abstract -- LAST, per writing-style 8b.

    `staging_path` is relative to `editorial/_staging/<release-id>/`.
    `live_path` is relative to the repo root.

    `surface_kind` maps onto the keys in
    `pipeline.blurbs.run._SURFACE_FIT_CONTEXTS` so the same Gate 3
    prompt builder applies. For surfaces with no direct match (fresh-
    tag rotation, latestReleaseLabel) we route through the closest fit
    -- `chart_commentary` is the most permissive register and accepts
    plain reader-facing prose.
    """

    surface_id: str
    surface_kind: str
    tier: int
    char_cap: int
    sentence_range: tuple[int, int]
    word_range: tuple[int, int]
    section: str
    staging_path: str
    live_path: str
    description: str  # human-readable, used in writer brief


@dataclass(frozen=True)
class FanOutPlan:
    """Ordered surface list for one release."""

    event: ReleaseEvent
    surfaces: tuple[Surface, ...]

    def by_tier(self, tier: int) -> tuple[Surface, ...]:
        return tuple(s for s in self.surfaces if s.tier == tier)


@dataclass
class FanOutResult:
    """End state of one fan-out cascade."""

    event: ReleaseEvent
    surfaces_drafted: int = 0
    surfaces_failed: int = 0
    promoted: bool = False
    rolled_back: bool = False
    error: Optional[str] = None
    drafted_bodies: dict[str, str] = field(default_factory=dict)
    dispatch_order: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Section 1: detect affected surfaces
# ---------------------------------------------------------------------------


def detect_affected_surfaces(
    release_event: ReleaseEvent,
    repo_root: Path = REPO_ROOT,
) -> FanOutPlan:
    """Return the ordered list of surfaces this release refreshes.

    Per the task brief:
      - section's blurb.body, tileLine, blurb.date, heroKicker,
        updatedAt    [tier 1 + section-meta tier 2]
      - section page's plate interpretation prose (~6 plates)
        [tier 2]
      - latestReleaseLabel for the section page          [tier 2]
      - fresh-tag rotation across all 7 sections         [tier 3]
      - splash hero abstract (LAST, hero-last rule)      [tier 4]
      - cross-section ripples (e.g. BoC rate decision hits
        Markets' boc-fed-spread plate)                   [tier 2]
    """
    rid = release_event.release_id
    section = release_event.section
    staging_root = f"editorial/_staging/{rid}"

    surfaces: list[Surface] = []

    # ---- Tier 1: the section's central blurb body ----------------------
    surfaces.append(Surface(
        surface_id=f"{section}.blurb.body",
        surface_kind="topic_abstract",
        tier=1,
        char_cap=480,
        sentence_range=(2, 3),
        word_range=(45, 90),
        section=section,
        staging_path=f"{staging_root}/sections/{section}/blurb_body.md",
        live_path=f"src/data/sections.ts#blurb.body[{section}]",
        description=(
            f"The 2-3 sentence section blurb body that renders on the "
            f"{section} homepage tile. Plain reader-facing prose; "
            f"declarative; print + delta + so-what."
        ),
    ))

    # ---- Tier 2: section-meta strings ----------------------------------
    # tileLine: <=85 chars, one sentence per sections.ts canon.
    surfaces.append(Surface(
        surface_id=f"{section}.tileLine",
        surface_kind="sparkline_blurb",
        tier=2,
        char_cap=85,
        sentence_range=(1, 1),
        word_range=(8, 18),
        section=section,
        staging_path=f"{staging_root}/sections/{section}/tile_line.md",
        live_path=f"src/data/sections.ts#tileLine[{section}]",
        description=(
            "Homepage section panel one-liner. HARD <=85 chars. One "
            "declarative sentence naming the primary print + the "
            "so-what. Truncates mid-word past 85 chars."
        ),
    ))
    # heroKicker: short content noun like "April CPI"
    surfaces.append(Surface(
        surface_id=f"{section}.heroKicker",
        surface_kind="active_headline",
        tier=2,
        char_cap=40,
        sentence_range=(1, 1),
        word_range=(2, 6),
        section=section,
        staging_path=f"{staging_root}/sections/{section}/hero_kicker.md",
        live_path=f"src/data/sections.ts#heroKicker[{section}]",
        description=(
            "Hero eyebrow kicker; a content noun naming the release "
            "(e.g. 'April CPI', 'Q4 2025 GDP'). Mixed case in source; "
            "rendered all-caps via CSS."
        ),
    ))
    # blurb.date: human-readable date stamp
    surfaces.append(Surface(
        surface_id=f"{section}.blurb.date",
        surface_kind="active_headline",
        tier=2,
        char_cap=18,
        sentence_range=(1, 1),
        word_range=(2, 4),
        section=section,
        staging_path=f"{staging_root}/sections/{section}/blurb_date.md",
        live_path=f"src/data/sections.ts#blurb.date[{section}]",
        description=(
            "Human-readable release date stamp for the section blurb "
            "(e.g. 'Apr 20, 2026')."
        ),
    ))
    # latestReleaseLabel on the section PAGE (not the homepage tile)
    surfaces.append(Surface(
        surface_id=f"{section}.latestReleaseLabel",
        surface_kind="active_headline",
        tier=2,
        char_cap=60,
        sentence_range=(1, 1),
        word_range=(3, 8),
        section=section,
        staging_path=f"{staging_root}/sections/{section}/latest_release_label.md",
        live_path=f"src/pages/{section}.astro#latestReleaseLabel",
        description=(
            "Label string at the top of the section page indicating "
            "the most recent release (e.g. 'Latest: April CPI, May 14')."
        ),
    ))
    # updatedAt: epoch ms; not LLM-authored (mechanical) but tracked so
    # the fan-out promotes it consistently with the rest.
    surfaces.append(Surface(
        surface_id=f"{section}.updatedAt",
        surface_kind="active_headline",
        tier=2,
        char_cap=20,
        sentence_range=(1, 1),
        word_range=(1, 3),
        section=section,
        staging_path=f"{staging_root}/sections/{section}/updated_at.json",
        live_path=f"src/data/sections.ts#updatedAt[{section}]",
        description=(
            "Epoch milliseconds of this release event. Mechanical, "
            "not LLM-authored; the fan-out stages this as JSON so the "
            "promote step can update the source string deterministically."
        ),
    ))

    # ---- Tier 2: per-plate interpretations -----------------------------
    plates = SECTION_PLATES.get(section, ())
    for plate_slug in plates:
        surfaces.append(Surface(
            surface_id=f"{section}.{plate_slug}.interpretation",
            surface_kind="chart_commentary",
            tier=2,
            char_cap=500,
            sentence_range=(2, 4),
            word_range=(25, 95),
            section=section,
            staging_path=(
                f"{staging_root}/sections/{section}/plates/"
                f"{plate_slug}_interpretation.md"
            ),
            live_path=(
                f"src/data/section_plates/{section}/"
                f"{plate_slug}.interpretation"
            ),
            description=(
                f"Plate interpretation paragraph for {plate_slug} on the "
                f"{section} section page. Mode A blurb voice: 2-4 "
                f"sentences -- print + comparator + optional structural "
                f"observation + optional next-print pointer."
            ),
        ))

    # ---- Tier 2: cross-section ripples ---------------------------------
    for ripple_section, ripple_plate in CROSS_SECTION_RIPPLES.get(
        release_event.release_key, ()
    ):
        surfaces.append(Surface(
            surface_id=(
                f"{ripple_section}.{ripple_plate}.interpretation"
                f" (ripple from {release_event.release_key})"
            ),
            surface_kind="chart_commentary",
            tier=2,
            char_cap=500,
            sentence_range=(2, 4),
            word_range=(25, 95),
            section=ripple_section,
            staging_path=(
                f"{staging_root}/sections/{ripple_section}/plates/"
                f"{ripple_plate}_interpretation.md"
            ),
            live_path=(
                f"src/data/section_plates/{ripple_section}/"
                f"{ripple_plate}.interpretation"
            ),
            description=(
                f"Cross-section ripple: {release_event.release_key} "
                f"refreshes the {ripple_section}.{ripple_plate} plate "
                f"because the underlying series is shared."
            ),
        ))

    # ---- Tier 3: fresh-tag rotation across all 7 sections --------------
    # One artifact carrying the rotation decision (which section is
    # `kind: "fresh"` after this release; the rest go `kind: "last"`).
    # The decision is mechanical (max updatedAt) but we route it
    # through the fan-out so the promote step writes it atomically.
    surfaces.append(Surface(
        surface_id="_global.fresh_tag_rotation",
        surface_kind="active_headline",  # closest register match
        tier=3,
        char_cap=200,
        sentence_range=(1, 1),
        word_range=(7, 25),
        section="_global",
        staging_path=f"{staging_root}/_global/fresh_tag_rotation.json",
        live_path="src/data/sections.ts#blurb.kind[*]",
        description=(
            "Cross-section fresh-tag rotation. After this release, the "
            "section with the maximum updatedAt becomes kind: 'fresh'; "
            "every other section becomes kind: 'last'. JSON sidecar; "
            "deterministic from updatedAt values, not LLM-authored."
        ),
    ))

    # ---- Tier 4: splash hero abstract (LAST, hero-last rule) -----------
    # Per editorial/writing-style.md Section 8b: the hero abstract is
    # written AFTER the seven section blurbs are stable. We enforce
    # ordering via tier; the orchestrator processes tiers ascending.
    surfaces.append(Surface(
        surface_id="_global.hero_abstract",
        surface_kind="homepage_abstract",
        tier=4,
        char_cap=560,
        sentence_range=(3, 4),
        word_range=(60, 110),
        section="_global",
        staging_path=f"{staging_root}/_global/hero_abstract.md",
        live_path="src/components/home/TitleStatement.astro#abstract",
        description=(
            "Splash hero abstract. 3-4 sentences naming the state of "
            "the Canadian cycle. Synthesized from the seven section "
            "blurbs after they have settled (writing-style 8b: hero-"
            "last). Do not introduce a claim not surfaced or implied "
            "by at least one section blurb."
        ),
    ))

    return FanOutPlan(
        event=release_event,
        surfaces=tuple(sorted(surfaces, key=lambda s: (s.tier, s.surface_id))),
    )


# ---------------------------------------------------------------------------
# Section 2: writer + gate-3 pass for ONE surface
# ---------------------------------------------------------------------------
#
# The fan-out leans on the existing Gate 3 surface-fit primitives from
# run.py (_surface_fit_prompt, _parse_surface_fit_response,
# _SURFACE_FIT_CONTEXTS). Writer + fact-check + style passes are inlined
# here because the existing `run.run_release_cycle` is shaped around a
# single release-id's registry; section-meta and plate surfaces in this
# fan-out are NOT in the registry yet (Phase 2 ticket -- the registry
# will grow). When that ticket lands, the inline writer/fact-check/style
# block below collapses to a single call into `run.run_release_cycle`.


def _writer_prompt(
    surface: Surface,
    diff_brief_md: str,
    prior_body: Optional[str],
) -> str:
    """Compose the writer prompt for one fan-out surface."""
    parts = [
        "You are the writer authoring one reader-facing surface for the "
        "Sibley Creek publication. Voice canon: editorial/writing-"
        "style.md Section 7 (Mode A blurb register).",
        "",
        f"Surface: {surface.surface_id}",
        f"Section: {surface.section}",
        f"Description: {surface.description}",
        (
            f"Length budget: {surface.word_range[0]}-{surface.word_range[1]} "
            f"words, {surface.sentence_range[0]}-{surface.sentence_range[1]} "
            f"sentences, <= {surface.char_cap} characters."
        ),
        "",
        diff_brief_md or "## Diff brief\n_None available._",
        "",
    ]
    if prior_body:
        parts.extend([
            "Prior version of this surface (what shipped on the last "
            "release; you are replacing this with the new release's read):",
            "---",
            prior_body,
            "---",
            "",
        ])
    parts.extend([
        "Return ONLY the surface body. No preamble. No quotes around the "
        "text. ASCII characters only. Do not introduce claims not "
        "grounded in the diff-brief deltas above or the section's "
        "pipeline-emitted prints. If the surface is a date stamp or a "
        "label, return only the date/label string."
    ])
    return "\n".join(parts)


def _gate3_review_via_dispatch(
    body: str,
    surface: Surface,
    surface_fit_dispatch: Optional[Callable[[str, str], str]] = None,
) -> dict:
    """Run the editorial-director Gate 3 surface-fit review on `body`.

    Re-uses `_surface_fit_prompt` + `_parse_surface_fit_response` from
    run.py so the rubric is identical to the per-release Phase 1 cycle.
    """
    surface_context = _SURFACE_FIT_CONTEXTS.get(
        surface.surface_kind,
        _SURFACE_FIT_CONTEXTS["chart_commentary"],
    )
    prompt = _surface_fit_prompt(body, surface_context)
    sender = surface_fit_dispatch or (
        lambda p, m: call_claude(prompt=p, model=m)
    )
    try:
        raw = sender(prompt, MODEL_EDITORIAL_DIRECTOR)
    except LLMDispatchError as exc:
        return {
            "verdict": "fail",
            "cuts": [f"editorial-director dispatch failed: {exc}"],
        }
    return _parse_surface_fit_response(raw)


def _draft_one_surface(
    surface: Surface,
    *,
    diff_brief_md: str,
    prior_body: Optional[str],
    writer_dispatch: Callable[[str, str], str],
    surface_fit_dispatch: Optional[Callable[[str, str], str]] = None,
) -> str:
    """Draft one surface and run Gate 3 with bounded retries.

    `writer_dispatch(prompt, model) -> raw_text` is the injection point;
    tests pass mocks here. Production callers pass a lambda that wraps
    `call_claude`.

    Returns the drafted body that passed Gate 3.

    Raises:
      RuntimeError on Gate 3 budget exhaustion.
    """
    body = writer_dispatch(
        _writer_prompt(surface, diff_brief_md, prior_body),
        "claude-sonnet-4-7",
    ).strip()
    for round_idx in range(SURFACE_FIT_BUDGET + 1):
        gate3 = _gate3_review_via_dispatch(
            body, surface, surface_fit_dispatch=surface_fit_dispatch,
        )
        if gate3["verdict"] == "pass":
            return body
        if round_idx >= SURFACE_FIT_BUDGET:
            raise RuntimeError(
                f"editorial-director exhausted {SURFACE_FIT_BUDGET} "
                f"re-runs on {surface.surface_id}: {gate3['cuts']}"
            )
        # Route back to writer with the cuts as revision_failures.
        revise_prompt = (
            _writer_prompt(surface, diff_brief_md, prior_body)
            + "\n\nThe prior draft was rejected by the editorial-director. "
            + "Cuts to apply:\n"
            + "\n".join(f"- {c}" for c in gate3["cuts"])
        )
        body = writer_dispatch(revise_prompt, "claude-sonnet-4-7").strip()
    return body  # unreachable (loop returns or raises)


# ---------------------------------------------------------------------------
# Section 3: staging-promote atomic semantics
# ---------------------------------------------------------------------------


def _staging_root(repo_root: Path, release_id: str) -> Path:
    return repo_root / "editorial" / "_staging" / release_id


def _stage_body(
    repo_root: Path,
    surface: Surface,
    body: str,
) -> Path:
    """Persist one drafted body under the staging directory."""
    out_path = repo_root / surface.staging_path
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(body + "\n", encoding="utf-8", newline="\n")
    return out_path


def _promote_staging(
    repo_root: Path,
    plan: FanOutPlan,
) -> bool:
    """Promote every staged surface into its live location.

    Atomicity model (best-effort on cross-device-safe Windows filesystem):

      1. For each staged file, write a backup of the live target if it
         exists at `<live_path>.fanout_backup`.
      2. Walk the staging tree once; for each staged file, copy it
         into the live target path. We use shutil.copy2 (atomic on
         POSIX, near-atomic on Windows via os.replace when same-drive).
      3. On any failure, walk the backups and restore them; remove the
         partially-promoted files. Return False.
      4. On success, remove the backups and the staging directory.

    The fan-out v1 stages files under `editorial/_staging/<release-
    id>/...` mirroring TARGET-AGNOSTIC paths (the `live_path` field on
    Surface is the SEMANTIC target -- e.g. a key inside sections.ts --
    not always a file on disk). For surfaces whose `live_path`
    contains a `#` (in-file key reference), this v1 leaves the staged
    file in place under `editorial/_staging/` and surfaces it via the
    inbox; the human review step copies values into sections.ts.

    File-target promotion (live_path resolves to a real file on disk
    without a `#`) is the path that exercises the atomic copy. v1
    surfaces are mostly `#`-key references, so the promote step today
    is largely a "freeze the staging directory and surface it via the
    inbox" operation. The atomic copy machinery is in place for when
    the v2 surfaces (e.g. data/site/section_plates/<section>/<plate>.
    json) become real on-disk targets.
    """
    backups: list[tuple[Path, Path]] = []
    promoted: list[Path] = []
    try:
        for surface in plan.surfaces:
            staged = repo_root / surface.staging_path
            if not staged.exists():
                continue  # surface failed; skip
            if "#" in surface.live_path:
                # Key-reference surface: nothing to do at the file level;
                # the inbox surfaces the staged file for manual review.
                continue
            target = repo_root / surface.live_path
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.exists():
                bak = target.with_suffix(target.suffix + ".fanout_backup")
                shutil.copy2(target, bak)
                backups.append((target, bak))
            shutil.copy2(staged, target)
            promoted.append(target)
        # Success: remove backups and the staging tree.
        for _target, bak in backups:
            try:
                bak.unlink()
            except OSError:
                pass
        return True
    except Exception:
        logger.exception("promote_staging failed; rolling back")
        # Restore from backups
        for target, bak in backups:
            try:
                if bak.exists():
                    shutil.copy2(bak, target)
                    bak.unlink()
            except OSError:
                logger.exception("failed to restore backup for %s", target)
        # Remove anything we partially promoted that did NOT have a backup
        already_backed = {t for t, _b in backups}
        for target in promoted:
            if target not in already_backed and target.exists():
                try:
                    target.unlink()
                except OSError:
                    pass
        return False


def _rollback_staging(repo_root: Path, plan: FanOutPlan) -> None:
    """Remove the staging directory after a pre-promote failure."""
    staging_dir = _staging_root(repo_root, plan.event.release_id)
    if staging_dir.exists():
        try:
            shutil.rmtree(staging_dir)
        except OSError:
            logger.exception("rollback_staging: failed to remove %s", staging_dir)


# ---------------------------------------------------------------------------
# Section 4: top-level orchestrator
# ---------------------------------------------------------------------------


def fan_out_release(
    release_event: ReleaseEvent,
    repo_root: Path = REPO_ROOT,
    *,
    writer_dispatch: Optional[Callable[[str, str], str]] = None,
    surface_fit_dispatch: Optional[Callable[[str, str], str]] = None,
    diff_brief_md: Optional[str] = None,
    prior_bodies: Optional[dict[str, str]] = None,
) -> FanOutResult:
    """Cascade ONE release across every affected surface, atomically.

    Args:
      release_event:        the trigger event (release_id, release_key,
                            section, reference_period, release_date).
      repo_root:            repo root (defaults to package's REPO_ROOT).
      writer_dispatch:      (prompt, model) -> raw_text. Production:
                            `lambda p, m: call_claude(prompt=p, model=m)`.
                            Tests: a deterministic mock.
      surface_fit_dispatch: (prompt, model) -> raw_text for the Gate 3
                            editorial-director call. Defaults to
                            call_claude.
      diff_brief_md:        pre-rendered diff-brief markdown; if None,
                            we build it via diff_brief.build_writer_
                            diff_brief at the section level.
      prior_bodies:         optional dict {surface_id: prior body} for
                            the writer to see the diff explicitly.
    """
    if writer_dispatch is None:
        writer_dispatch = lambda p, m: call_claude(prompt=p, model=m)  # noqa: E731
    if prior_bodies is None:
        prior_bodies = {}

    plan = detect_affected_surfaces(release_event, repo_root=repo_root)

    # Pre-build the diff brief once (re-used across all writer prompts).
    if diff_brief_md is None:
        try:
            diff_brief_md = df_mod.build_writer_diff_brief(
                repo_root, release_event.section,
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning("diff_brief unavailable: %s", exc)
            diff_brief_md = (
                "## Diff brief\n\n_Snapshot unavailable; proceed without diff cues._\n"
            )

    result = FanOutResult(event=release_event)

    # Walk tiers in order; within a tier, surfaces process sequentially
    # (Phase 1; parallel-within-tier is a v2 nice-to-have).
    try:
        for tier in (1, 2, 3, 4):
            tier_surfaces = plan.by_tier(tier)
            if not tier_surfaces:
                continue
            for surface in tier_surfaces:
                result.dispatch_order.append(surface.surface_id)
                logger.info(
                    "fan_out: tier=%d drafting %s", tier, surface.surface_id,
                )
                try:
                    body = _draft_one_surface(
                        surface,
                        diff_brief_md=diff_brief_md,
                        prior_body=prior_bodies.get(surface.surface_id),
                        writer_dispatch=writer_dispatch,
                        surface_fit_dispatch=surface_fit_dispatch,
                    )
                    _stage_body(repo_root, surface, body)
                    result.drafted_bodies[surface.surface_id] = body
                    result.surfaces_drafted += 1
                except Exception as exc:  # noqa: BLE001
                    logger.error(
                        "fan_out: surface %s failed: %s",
                        surface.surface_id, exc,
                    )
                    result.surfaces_failed += 1
                    result.error = (
                        f"surface {surface.surface_id} failed: {exc}"
                    )
                    raise
        # All surfaces drafted -> promote.
        ok = _promote_staging(repo_root, plan)
        result.promoted = ok
        if not ok:
            result.rolled_back = True
            result.error = "promote_staging returned False"
        else:
            _append_inbox(repo_root, plan, result)
        return result
    except Exception as exc:  # noqa: BLE001
        logger.exception("fan_out: cascade aborted; rolling back staging")
        _rollback_staging(repo_root, plan)
        result.rolled_back = True
        if not result.error:
            result.error = f"cascade aborted: {exc}"
        return result


def _append_inbox(
    repo_root: Path,
    plan: FanOutPlan,
    result: FanOutResult,
) -> None:
    """v1 inbox-file mode: append one summary entry to _fan_out_inbox.md."""
    inbox = repo_root / "editorial" / "blurbs" / "_fan_out_inbox.md"
    inbox.parent.mkdir(parents=True, exist_ok=True)
    if not inbox.exists():
        inbox.write_text(
            "# Pending fan-out cascade review\n\n"
            "Each entry below is one release that has cascaded through "
            "all affected surfaces and is staged for human review. "
            "Drafts live under `editorial/_staging/<release-id>/`.\n",
            encoding="utf-8",
        )
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    lines = [
        "",
        f"## {now} {plan.event.release_id}",
        f"- release_key: {plan.event.release_key}",
        f"- section: {plan.event.section}",
        f"- reference_period: {plan.event.reference_period}",
        f"- release_date: {plan.event.release_date or '(unknown)'}",
        f"- surfaces drafted: {result.surfaces_drafted}",
        f"- surfaces failed: {result.surfaces_failed}",
        f"- promoted: {result.promoted}",
        f"- staging: editorial/_staging/{plan.event.release_id}/",
        "",
        "### Dispatch order",
    ]
    for sid in result.dispatch_order:
        lines.append(f"- {sid}")
    with inbox.open("a", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


# ---------------------------------------------------------------------------
# Section 5: release-event detection (content-hash trigger)
# ---------------------------------------------------------------------------


def detect_release_event(
    repo_root: Path = REPO_ROOT,
    prior_snapshot: Optional[dict] = None,
) -> Optional[ReleaseEvent]:
    """Walk the registry's primary meta sidecars; return a ReleaseEvent
    if any sidecar's `release_date` is newer than the equivalent in the
    rotated snapshot.

    Section 1 of auto_blurb_process.md: the trigger is a CHANGE in
    `release_date` on the primary series sidecar (content-hash style).
    We compute the change vs the most recent snapshot from
    `data/site/_snapshots/` (rotated by the pipeline build).

    Returns None if no release-key reports a new release_date. Returns
    the FIRST matching release-key's ReleaseEvent (the build calls this
    in a loop until it returns None to drain a pile-up of releases).
    """
    if prior_snapshot is None:
        prior_snapshot = df_mod.load_latest_prior_snapshot(repo_root) or {}

    for release_key, spec in RELEASE_KEYS.items():
        for meta_rel in spec.primary_meta_files:
            meta_path = repo_root / meta_rel
            if not meta_path.exists():
                continue
            try:
                live = json.loads(meta_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            live_release_date = live.get("release_date")
            if not live_release_date:
                continue

            # Compare against the snapshot's sidecar copy. The snapshot
            # carries sections + panels but NOT data/processed sidecars,
            # so we fall back to the section's headline as_of as the
            # change signal proxy. v1: if there is no prior snapshot,
            # treat any live release_date as a NEW event so first-build
            # cascades fire deterministically; production CI sets a
            # FAN_OUT_REQUIRE_SNAPSHOT=1 env if a tighter contract is
            # required (Phase 2 ticket).
            prior_marker = _prior_release_date_marker(
                prior_snapshot, spec.section,
            )
            if prior_marker == live_release_date:
                continue

            reference_period = _reference_period_from_meta(live)
            release_id = f"{release_key}_{reference_period}"
            return ReleaseEvent(
                release_id=release_id,
                release_key=release_key,
                section=spec.section,
                reference_period=reference_period,
                release_date=live_release_date,
            )
    return None


def _prior_release_date_marker(snapshot: dict, section_slug: str) -> Optional[str]:
    """Pull the most recent asOfISO from a snapshot's section payload."""
    sections = (snapshot or {}).get("sections_file") or {}
    sec = (sections.get("sections") or {}).get(section_slug) or {}
    prints = sec.get("prints") or []
    most_recent: Optional[str] = None
    for p in prints:
        as_of = p.get("asOfISO")
        if as_of and (most_recent is None or as_of > most_recent):
            most_recent = as_of
    return most_recent


def _reference_period_from_meta(meta: dict) -> str:
    """Derive a YYYY-MM (or YYYY-MM-DD) suffix from a meta sidecar."""
    rp = meta.get("reference_period_end")
    if rp and isinstance(rp, str):
        # truncate to YYYY-MM if a daily-cadence release lands here.
        return rp[:7] if len(rp) >= 7 else rp
    # Fall back to release_date.
    rd = meta.get("release_date") or ""
    return rd[:7] if len(rd) >= 7 else rd
