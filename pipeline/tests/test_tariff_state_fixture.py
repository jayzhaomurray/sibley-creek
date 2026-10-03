"""Tests for pipeline.build.derive_tariff_state_fixture.

The function reads source cards and writes data/derived/tariff_state.json.
Every test points build.ROOT and build.DATA_DERIVED at tmp_path, so the real
registry and the real fixture are never read or written.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from pipeline import build

REGISTRY_YAML = """\
sources:
  - id: eo_14193_ieepa_canada_2025
    title: "EO 14193"
    url: "https://example.invalid/eo-14193"
    excerpt: "25% additional tariff"
    verified_value:
      effective_date: "2025-02-04"
    verified_at: 2026-05-13
    verification_tier: "A"
  - id: eo_14193_amendment_35pct
    title: "EO 14193 amendment"
    url: "https://example.invalid/eo-14193-amendment"
    excerpt: "35 percent"
    verified_value:
      signed_date: "2025-07-31"
      effective_date: "2025-08-01"
    verified_at: 2026-05-13
    verification_tier: "A"
  - id: pp_section_232_steel_alum_50pct
    title: "232 steel"
    url: "https://example.invalid/232-steel"
    excerpt: "25% to 50%"
    verified_value:
      effective_date: "2025-06-04"
    verified_at: 2026-05-13
    verification_tier: "A"
  - id: usmca_article_34_7
    title: "USMCA 34.7"
    url: "https://example.invalid/usmca"
    excerpt: "Joint Review"
    verified_at: 2026-05-13
    verification_tier: "A"
"""

S338_RATE_CARD = """\
id: claim_wh_s338_50pct_tariffs_canada_2026_07_20
url: "https://example.invalid/s338-fact-sheet"
excerpt: |
  impose additional 50% tariffs on certain goods of Canada
verified_value:
  rate_pct: 50
  signed_date: "2026-07-20"
verified_at: 2026-10-03
verification_tier: "A"
status: pending_user
"""

S338_DATE_CARD = """\
id: claim_wh_s338_effective_2026_08_22
url: "https://example.invalid/s338-effective"
excerpt: |
  shall be 12:01 a.m. eastern time on August 22, 2026.
verified_value:
  effective_date: "2026-08-22"
verified_at: 2026-10-03
verification_tier: "A"
status: pending_user
"""

COUNTER_CARD = """\
id: claim_dof_countertariffs_effective_2026_09_08
url: "https://example.invalid/dof-countermeasures"
excerpt: |
  Effective September 8, Canada will impose counter-tariffs of 15, 25 and 50 per cent
verified_value:
  effective_date: "2026-09-08"
verified_at: 2026-10-03
verification_tier: "A"
status: pending_user
"""


@pytest.fixture
def sandbox(tmp_path, monkeypatch):
    """A throwaway repo root with a registry and a _pending/trade folder."""
    cards = tmp_path / "editorial" / "source_cards"
    pending = cards / "_pending" / "trade"
    pending.mkdir(parents=True)
    (cards / "registry.yaml").write_text(REGISTRY_YAML, encoding="utf-8")
    derived = tmp_path / "data" / "derived"
    monkeypatch.setattr(build, "ROOT", tmp_path)
    monkeypatch.setattr(build, "DATA_DERIVED", derived)
    return tmp_path, pending, derived


def _write_pending(pending: Path, *cards: str) -> None:
    for text in cards:
        card_id = text.splitlines()[0].split(":", 1)[1].strip()
        (pending / f"{card_id}.yaml").write_text(text, encoding="utf-8")


def _run(derived: Path) -> dict:
    build.derive_tariff_state_fixture()
    return json.loads((derived / "tariff_state.json").read_text(encoding="utf-8"))


def _rows(fixture: dict) -> dict:
    return {r["id"]: r for r in fixture["rows"]}


def test_writes_only_inside_sandbox(sandbox):
    root, pending, derived = sandbox
    _write_pending(pending, S338_RATE_CARD, S338_DATE_CARD, COUNTER_CARD)
    _run(derived)
    assert (derived / "tariff_state.json").is_file()
    assert derived.is_relative_to(root)


def test_eo_14193_rows_are_terminated_with_historical_values(sandbox):
    _, pending, derived = sandbox
    rows = _rows(_run(derived))
    for card_id, eff in (
        ("eo_14193_ieepa_canada_2025", "2025-02-04"),
        ("eo_14193_amendment_35pct", "2025-08-01"),
    ):
        row = rows[card_id]
        assert row["status"] == "terminated"
        assert row["rate_pct"] == 35
        assert row["effective_date"] == eff
        assert row["status_source_url"].endswith("/2026/02/ending-certain-tariff-actions/")
        assert row["card_status"] == "registry"
        # No termination date is invented.
        assert "terminated_date" not in row


def test_section_338_row_takes_effective_date_from_the_date_card(sandbox):
    _, pending, derived = sandbox
    _write_pending(pending, S338_RATE_CARD, S338_DATE_CARD)
    row = _rows(_run(derived))["claim_wh_s338_50pct_tariffs_canada_2026_07_20"]
    assert row["rate_pct"] == 50
    assert row["status"] == "in_force"
    assert row["effective_date"] == "2026-08-22"  # not the 2026-07-20 signing date
    assert row["source_url"] == "https://example.invalid/s338-fact-sheet"
    assert row["effective_date_source_url"] == "https://example.invalid/s338-effective"
    assert row["card_status"] == "pending_user"
    assert row["imposed_by"] == "United States"
    assert row["excerpt"] == row["excerpt"].strip()


def test_section_338_row_fails_loudly_without_its_date_card(sandbox):
    _, pending, derived = sandbox
    _write_pending(pending, S338_RATE_CARD)
    with pytest.raises(RuntimeError, match="claim_wh_s338_effective_2026_08_22"):
        build.derive_tariff_state_fixture()
    assert not (derived / "tariff_state.json").exists()


def test_counter_tariff_row_has_no_single_rate(sandbox):
    _, pending, derived = sandbox
    _write_pending(pending, COUNTER_CARD)
    row = _rows(_run(derived))["claim_dof_countertariffs_effective_2026_09_08"]
    assert row["rate_pct"] is None
    assert row["rate_label"] == "15% / 25% / 50%"
    assert row["effective_date"] == "2026-09-08"
    assert row["imposed_by"] == "Canada"
    assert row["status"] == "in_force"


def test_unconfirmed_usmca_row_keeps_its_values(sandbox):
    _, pending, derived = sandbox
    row = _rows(_run(derived))["usmca_article_34_7"]
    assert row["status"] == "under_review"
    assert row["rate_pct"] is None
    assert row["rate_label"] == "Review pending"
    assert row["notes"].startswith("UNCONFIRMED")


def test_as_of_ignores_terminated_rows_and_missing_cards_are_skipped(sandbox):
    _, pending, derived = sandbox
    # No pending cards: the two new rows are skipped, the rest still build.
    fixture = _run(derived)
    ids = [r["id"] for r in fixture["rows"]]
    assert "claim_wh_s338_50pct_tariffs_canada_2026_07_20" not in ids
    assert "claim_dof_countertariffs_effective_2026_09_08" not in ids
    # Only in-force row left is 232 steel (2025-06-04); the terminated
    # 2025-08-01 amendment must not set as_of.
    assert fixture["as_of"] == "2025-06-04"
    assert fixture["last_reviewed"] == "2026-10-03"


def test_registry_card_wins_over_pending_copy(sandbox):
    root, pending, derived = sandbox
    _write_pending(pending, COUNTER_CARD)
    registry = root / "editorial" / "source_cards" / "registry.yaml"
    registry.write_text(
        REGISTRY_YAML
        + """\
  - id: claim_dof_countertariffs_effective_2026_09_08
    url: "https://example.invalid/promoted"
    excerpt: "promoted"
    verified_value:
      effective_date: "2026-09-08"
    verified_at: 2026-10-03
    verification_tier: "A"
""",
        encoding="utf-8",
    )
    row = _rows(_run(derived))["claim_dof_countertariffs_effective_2026_09_08"]
    assert row["card_status"] == "registry"
    assert row["source_url"] == "https://example.invalid/promoted"
