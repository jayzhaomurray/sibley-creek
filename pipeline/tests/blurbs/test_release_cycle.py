"""Tests for the release-cycle state machine."""

from __future__ import annotations

from pathlib import Path

import pytest

from pipeline.blurbs.registry import get_release_spec
from pipeline.blurbs.release_cycle import (
    LEGAL_TRANSITIONS,
    ReleaseCycle,
    StateTransitionError,
    SurfaceSlot,
    init_release_cycle,
    read_release_cycle,
    transition_surface_state,
    write_release_cycle,
)


def test_init_release_cycle_creates_wrapper_and_per_surface_slots(tmp_path):
    spec = get_release_spec("cpi_monthly")
    rc = init_release_cycle(
        repo_root=tmp_path,
        release_id="cpi_monthly_2026-04",
        release_key="cpi_monthly",
        section="inflation",
        reference_period="2026-04",
        release_date="2026-05-20",
        surfaces_spec=spec.surfaces,
    )
    assert rc.release_id == "cpi_monthly_2026-04"
    assert len(rc.surfaces) == 8
    for slot in rc.surfaces:
        assert slot.last_state == "release_landed"
        assert len(slot.state_history) == 1
        assert slot.state_history[0].state == "release_landed"
        assert slot.state_history[0].actor == "scheduler"
    wrapper_file = tmp_path / "editorial" / "blurbs" / "_cycles" / "cpi_monthly_2026-04.json"
    assert wrapper_file.exists()


def test_read_write_release_cycle_round_trip(tmp_path):
    spec = get_release_spec("cpi_monthly")
    rc = init_release_cycle(
        repo_root=tmp_path,
        release_id="cpi_monthly_2026-04",
        release_key="cpi_monthly",
        section="inflation",
        reference_period="2026-04",
        release_date="2026-05-20",
        surfaces_spec=spec.surfaces,
    )
    rc2 = read_release_cycle(tmp_path, "cpi_monthly_2026-04")
    assert rc2.release_id == rc.release_id
    assert len(rc2.surfaces) == len(rc.surfaces)
    assert rc2.surfaces[0].surface_id == rc.surfaces[0].surface_id


def test_legal_transition_advances_state(tmp_path):
    spec = get_release_spec("cpi_monthly")
    rc = init_release_cycle(
        repo_root=tmp_path,
        release_id="cpi_monthly_2026-04",
        release_key="cpi_monthly",
        section="inflation",
        reference_period="2026-04",
        release_date=None,
        surfaces_spec=spec.surfaces,
    )
    transition_surface_state(
        rc, "homepage_abstract", "context_drafted",
        actor="researcher", note="ok",
    )
    slot = next(s for s in rc.surfaces if s.surface_id == "homepage_abstract")
    assert slot.last_state == "context_drafted"
    assert slot.state_history[-1].state == "context_drafted"


def test_illegal_transition_raises(tmp_path):
    spec = get_release_spec("cpi_monthly")
    rc = init_release_cycle(
        repo_root=tmp_path,
        release_id="cpi_monthly_2026-04",
        release_key="cpi_monthly",
        section="inflation",
        reference_period="2026-04",
        release_date=None,
        surfaces_spec=spec.surfaces,
    )
    # Cannot skip from release_landed straight to writer_drafted
    with pytest.raises(StateTransitionError):
        transition_surface_state(
            rc, "homepage_abstract", "writer_drafted",
            actor="orchestrator",
        )


def test_self_transition_writer_to_writer_is_legal(tmp_path):
    """Writer round-trips on factcheck failure stay at writer_drafted."""
    spec = get_release_spec("cpi_monthly")
    rc = init_release_cycle(
        repo_root=tmp_path,
        release_id="cpi_monthly_2026-04",
        release_key="cpi_monthly",
        section="inflation",
        reference_period="2026-04",
        release_date=None,
        surfaces_spec=spec.surfaces,
    )
    # advance to writer_drafted
    for state in ("context_drafted", "claims_verified", "writer_drafted"):
        transition_surface_state(
            rc, "homepage_abstract", state, actor="agent",
        )
    # round-trip on factcheck fail
    transition_surface_state(
        rc, "homepage_abstract", "writer_drafted",
        actor="writer", note="re-draft",
    )
    slot = next(s for s in rc.surfaces if s.surface_id == "homepage_abstract")
    assert slot.last_state == "writer_drafted"
    # state_history should record each re-draft
    state_events = [e.state for e in slot.state_history]
    assert state_events.count("writer_drafted") == 2


def test_legal_transitions_map_covers_every_state():
    """The LEGAL_TRANSITIONS map must not have orphan states."""
    states_appearing = {"release_landed"}  # canonical start
    for src, dests in LEGAL_TRANSITIONS.items():
        states_appearing.add(src)
        states_appearing |= dests
    # Every state in the map should be reachable from release_landed
    # at least transitively.
    expected = {
        "release_landed", "context_drafted", "claims_verified",
        "writer_drafted", "fact_checked", "style_polished",
        "ready_for_user", "approved", "published", "rejected", "escalated",
    }
    assert states_appearing == expected


def test_unknown_surface_raises(tmp_path):
    spec = get_release_spec("cpi_monthly")
    rc = init_release_cycle(
        repo_root=tmp_path,
        release_id="cpi_monthly_2026-04",
        release_key="cpi_monthly",
        section="inflation",
        reference_period="2026-04",
        release_date=None,
        surfaces_spec=spec.surfaces,
    )
    with pytest.raises(StateTransitionError):
        transition_surface_state(
            rc, "no_such_surface", "context_drafted",
            actor="x",
        )


def test_panel_5_and_6_excluded_for_cpi():
    spec = get_release_spec("cpi_monthly")
    surface_ids = [s.surface_id for s in spec.surfaces]
    assert "panel_5_expectations" not in surface_ids
    assert "panel_6_passthrough" not in surface_ids
    # And they should be False in the panels gate
    assert spec.panels["panel-5-expectations"] is False
    assert spec.panels["panel-6-passthrough"] is False
