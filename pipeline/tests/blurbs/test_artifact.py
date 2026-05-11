"""Tests for the per-surface cycle artifact (front-matter + body) round-trip."""

from __future__ import annotations

from pathlib import Path

import pytest

from pipeline.blurbs.artifact import CycleArtifact, read_artifact, write_artifact
from pipeline.blurbs.release_cycle import StateEvent


def _make_artifact() -> CycleArtifact:
    return CycleArtifact(
        release_id="cpi_monthly_2026-04",
        release_key="cpi_monthly",
        section="inflation",
        unit_slug="panel-1-headline-cpi",
        surface="chart_commentary",
        reference_period="2026-04",
        release_date="2026-05-20",
        created_at="2026-05-20T08:30:00Z",
        char_cap=500,
        voice_register_variant="chart_commentary",
        last_state="release_landed",
        state_history=[
            StateEvent(
                state="release_landed", timestamp="2026-05-20T08:30:00Z",
                actor="scheduler", note="cycle_init",
            ),
        ],
        shared_cards_path="research/blurb_context/cpi_monthly_2026-04/_shared_cards.yaml",
    )


def test_write_read_round_trip(tmp_path):
    art = _make_artifact()
    body = "Headline CPI rose 2.3% Y/Y in April."
    path = tmp_path / "test.md"
    write_artifact(path, art, body)
    art2, body2 = read_artifact(path)
    assert art2.release_id == art.release_id
    assert art2.surface == art.surface
    assert art2.char_cap == 500
    assert body2.strip() == body


def test_write_artifact_rejects_non_ascii(tmp_path):
    art = _make_artifact()
    # inject explicit non-ASCII char (U+2014 em-dash)
    body_bad = "Headline CPI rose 2.3 percent in April" + chr(0x2014) + " a 0.1pp acceleration."
    path = tmp_path / "bad.md"
    with pytest.raises(ValueError):
        write_artifact(path, art, body_bad)


def test_read_artifact_missing_fence_raises(tmp_path):
    path = tmp_path / "no_fence.md"
    path.write_text("just a body, no front matter\n", encoding="utf-8")
    with pytest.raises(ValueError):
        read_artifact(path)


def test_state_history_preserved_in_round_trip(tmp_path):
    art = _make_artifact()
    art.state_history.append(StateEvent(
        state="context_drafted",
        timestamp="2026-05-20T08:35:00Z",
        actor="researcher",
    ))
    art.last_state = "context_drafted"
    path = tmp_path / "hist.md"
    write_artifact(path, art, "")
    art2, _ = read_artifact(path)
    assert art2.last_state == "context_drafted"
    assert len(art2.state_history) == 2
    assert art2.state_history[1].state == "context_drafted"
