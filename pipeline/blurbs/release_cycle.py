"""Release-cycle state-machine model.

A `ReleaseCycle` is the wrapper object that ties together every per-surface
artifact for one upstream release event. Each surface is a `SurfaceSlot`
with its own `state_history` and `last_state`. The wrapper persists at:

    editorial/blurbs/_cycles/<release-id>.json

Per-surface artifacts (front-matter + body) persist at the path in their
`SurfaceSlot.artifact_path`. State machine enforcement: no skip-forward,
only legal transitions (per Section 1 of editorial/auto_blurb_process.md).
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal, Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# State machine
# ---------------------------------------------------------------------------

SurfaceState = Literal[
    "release_landed",
    "context_drafted",
    "claims_verified",
    "writer_drafted",
    "fact_checked",
    "style_polished",
    "surface_fit_passed",
    "ready_for_user",
    "approved",
    "published",
    "rejected",
    "escalated",
]


# Legal forward transitions. Anything not in this map is rejected.
# `rejected` and `escalated` are terminal-ish: only legal exit is back to
# the user surface (user re-approves or operator re-runs).
LEGAL_TRANSITIONS: dict[str, set[str]] = {
    "release_landed":     {"context_drafted", "escalated"},
    "context_drafted":    {"claims_verified", "escalated"},
    "claims_verified":    {"writer_drafted", "context_drafted", "escalated"},
    # context_drafted re-entry: round-trip back to researcher on
    # verifier failure (bounded by researcher_revision_count).
    "writer_drafted":     {"fact_checked", "writer_drafted", "escalated"},
    "fact_checked":       {"style_polished", "writer_drafted", "escalated"},
    "style_polished":     {"surface_fit_passed", "writer_drafted", "escalated"},
    # surface_fit_passed -> writer_drafted re-entry: round-trip back to
    # writer on editorial-director Gate 3 reject (bounded by Gate 3
    # re-run budget; see pipeline/blurbs/run.py SURFACE_FIT_BUDGET).
    "surface_fit_passed": {"ready_for_user", "escalated"},
    "ready_for_user":     {"approved", "rejected"},
    "approved":           {"published"},
    "published":          set(),
    "rejected":           set(),
    "escalated":          {"ready_for_user"},  # operator may rescue
}


class StateTransitionError(RuntimeError):
    """Raised when transition_surface_state is asked to make an illegal move."""


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------

class StateEvent(BaseModel):
    """One row in a surface's state_history."""

    state: SurfaceState
    timestamp: str
    actor: str = Field(..., description="agent name or 'orchestrator' or 'user'")
    note: str = ""


class SurfaceSlot(BaseModel):
    """Per-surface state in a release-cycle.

    `surface_id` matches registry.SurfaceSpec.surface_id.
    `artifact_path` is the cycle-artifact .md file (front-matter + body).
    `state_history` is append-only.
    """

    surface_id: str
    kind: str
    section: str
    unit_slug: str
    artifact_path: str
    last_state: SurfaceState = "release_landed"
    state_history: list[StateEvent] = Field(default_factory=list)
    researcher_revision_count: int = 0
    writer_revision_count: int = 0
    style_revision_count: int = 0
    flags: list[dict] = Field(default_factory=list)


class ReleaseCycle(BaseModel):
    """Top-level wrapper for one release event.

    Persisted at `editorial/blurbs/_cycles/<release_id>.json`.
    """

    release_id: str
    release_key: str
    section: str
    reference_period: str
    release_date: Optional[str] = None
    created_at: str
    shared_cards_path: str = Field(
        ...,
        description="research/blurb_context/<release-id>/_shared_cards.yaml",
    )
    surfaces: list[SurfaceSlot]

    # Whole-cycle status for the email-summary builder.
    @property
    def is_all_ready(self) -> bool:
        terminal_ok = {"ready_for_user", "approved", "published"}
        return all(s.last_state in terminal_ok for s in self.surfaces)

    @property
    def has_escalation(self) -> bool:
        return any(s.last_state == "escalated" for s in self.surfaces)


# ---------------------------------------------------------------------------
# Persistence helpers
# ---------------------------------------------------------------------------

def cycle_path(repo_root: Path, release_id: str) -> Path:
    return repo_root / "editorial" / "blurbs" / "_cycles" / f"{release_id}.json"


def read_release_cycle(repo_root: Path, release_id: str) -> ReleaseCycle:
    """Read the wrapper JSON; raise FileNotFoundError if missing."""
    path = cycle_path(repo_root, release_id)
    data = json.loads(path.read_text(encoding="utf-8"))
    return ReleaseCycle.model_validate(data)


def write_release_cycle(repo_root: Path, rc: ReleaseCycle) -> Path:
    path = cycle_path(repo_root, rc.release_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = rc.model_dump(mode="json")
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    return path


def init_release_cycle(
    repo_root: Path,
    release_id: str,
    release_key: str,
    section: str,
    reference_period: str,
    release_date: Optional[str],
    surfaces_spec: list,  # list[SurfaceSpec], duck-typed to avoid circular import
) -> ReleaseCycle:
    """Build a fresh ReleaseCycle in `release_landed` state for every surface."""
    now = _now()
    shared_cards_path = (
        f"research/blurb_context/{release_id}/_shared_cards.yaml"
    )
    surfaces: list[SurfaceSlot] = []
    for spec in surfaces_spec:
        artifact_path = spec.path_template.format(release_id=release_id)
        slot = SurfaceSlot(
            surface_id=spec.surface_id,
            kind=spec.kind,
            section=spec.section,
            unit_slug=spec.unit_slug,
            artifact_path=artifact_path,
            last_state="release_landed",
            state_history=[
                StateEvent(
                    state="release_landed",
                    timestamp=now,
                    actor="scheduler",
                    note="cycle_init",
                )
            ],
        )
        surfaces.append(slot)
    rc = ReleaseCycle(
        release_id=release_id,
        release_key=release_key,
        section=section,
        reference_period=reference_period,
        release_date=release_date,
        created_at=now,
        shared_cards_path=shared_cards_path,
        surfaces=surfaces,
    )
    write_release_cycle(repo_root, rc)
    return rc


# ---------------------------------------------------------------------------
# State transition (enforcement)
# ---------------------------------------------------------------------------

def transition_surface_state(
    rc: ReleaseCycle,
    surface_id: str,
    new_state: SurfaceState,
    actor: str,
    note: str = "",
) -> SurfaceSlot:
    """Mutate `rc` in place: move one surface to a new state if legal.

    Raises StateTransitionError on illegal moves. Self-transitions are
    legal when listed in LEGAL_TRANSITIONS (e.g. writer_drafted ->
    writer_drafted on a retry round-trip).
    """
    for slot in rc.surfaces:
        if slot.surface_id == surface_id:
            break
    else:
        raise StateTransitionError(
            f"surface {surface_id!r} not found in release_cycle {rc.release_id!r}"
        )

    allowed = LEGAL_TRANSITIONS.get(slot.last_state, set())
    if new_state not in allowed and new_state != slot.last_state:
        raise StateTransitionError(
            f"illegal transition {slot.last_state!r} -> {new_state!r} "
            f"for surface {surface_id!r}; allowed: {sorted(allowed)}"
        )

    slot.state_history.append(
        StateEvent(
            state=new_state,
            timestamp=_now(),
            actor=actor,
            note=note,
        )
    )
    slot.last_state = new_state
    return slot


def find_surface(rc: ReleaseCycle, surface_id: str) -> SurfaceSlot:
    for slot in rc.surfaces:
        if slot.surface_id == surface_id:
            return slot
    raise KeyError(f"surface {surface_id!r} not in release_cycle {rc.release_id!r}")
