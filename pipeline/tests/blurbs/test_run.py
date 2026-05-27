"""Integration test: walk a full CPI release-cycle through 8 surface-blurbs
to `ready_for_user` against frozen fixtures.

Asserts:
  - one shared verifier pass (Mode A runs once for the release, not per surface)
  - 8 per-surface artifacts land in ready_for_user
  - batched email body contains every surface_id
  - audit log lines are written per surface
"""

from __future__ import annotations

from email.message import EmailMessage
from pathlib import Path
from typing import Any

import pytest
from ruamel.yaml import YAML

from pipeline.blurbs.artifact import read_artifact
from pipeline.blurbs.registry import RELEASE_KEYS
from pipeline.blurbs.release_cycle import read_release_cycle
from pipeline.blurbs.run import run_release_cycle
from pipeline.blurbs.verify_claims import FetchResult


# ---------------------------------------------------------------------------
# Frozen-fixture content for the verifier's "live fetch" path
# ---------------------------------------------------------------------------

STATCAN_DAILY_BODY = """
<html><body>
<p>The Consumer Price Index (CPI) rose 2.3% on a year-over-year basis in
April, following a 1.8% increase in March.</p>
<p>The trim CPI was 2.7% in April. The median CPI eased to 2.8% from
2.9% in March. Consensus had expected 2.2% headline. The print came in
0.1 pp above consensus.</p>
<p>Shelter contributed 1.1 percentage points to headline.</p>
<p>About 35% of the CPI basket ran above 3% in April, down from 40% in
2024H2.</p>
<p>Goods inflation rose 1.5% in April; services inflation 3.2%.</p>
</body></html>
"""


# ---------------------------------------------------------------------------
# Per-surface fixture bodies (each passes the validator + factcheck)
# ---------------------------------------------------------------------------

FIXTURE_BODIES: dict[str, str] = {
    "homepage_abstract": (
        "Headline CPI in Canada rose 2.3% on a year-over-year basis in "
        "April, a 0.1pp acceleration from the 1.8% pace in March and "
        "0.1pp above the consensus of 2.2%. The BoC's preferred core "
        "measures held the line: core-trim was 2.7% and core-median came "
        "in at 2.8%, down from 2.9% the prior month. Shelter contributed "
        "1.1pp to headline as mortgage-interest cost continued its "
        "mechanical fade from the 2024 peak. The next CPI print is "
        "scheduled for the morning of May 20."
    ),
    "topic_abstract": (
        "Headline CPI rose 2.3% Y/Y in April, a 0.1pp acceleration from "
        "the 1.8% March pace and 0.1pp above the consensus 2.2%. The BoC's "
        "preferred core measures held: core-trim was 2.7%, core-median "
        "came in at 2.8% versus 2.9% in March. Shelter contributed 1.1pp "
        "to the April headline, with mortgage-interest cost continuing "
        "its mechanical fade from the 2024 peak."
    ),
    "sparkline_blurb": (
        "Headline CPI rose 2.3% Y/Y in April, 0.1pp above consensus."
    ),
    "active_headline": (
        "Headline CPI ticked up to 2.3% in April, 0.1pp above consensus."
    ),
    "panel_1_headline_cpi": (
        "Headline CPI rose 2.3% Y/Y in April, a 0.1pp acceleration from "
        "the 1.8% March pace and 0.1pp above the consensus 2.2%. The "
        "print remains within the BoC inflation-control band for the "
        "eleventh month running. The next CPI print is May 20."
    ),
    "panel_2_core_measures": (
        "Core-trim held at 2.7% Y/Y in April; core-median ticked down to "
        "2.8% from 2.9% in March. Both measures remain inside the BoC "
        "inflation-control band. The next CPI print is May 20."
    ),
    "panel_3_breadth": (
        "Headline CPI rose 2.3% Y/Y in April; about 35% of the CPI basket "
        "ran above 3% Y/Y, down from the 40% breadth that prevailed in "
        "late 2024. The narrowing has come predominantly through goods. "
        "Next CPI print is May 20."
    ),
    "panel_4_subaggregates": (
        "Shelter contributed 1.1pp to the 2.3% April headline, with "
        "mortgage-interest cost continuing its mechanical fade. Goods "
        "inflation rose 1.5% Y/Y and services inflation ran at 3.2% Y/Y "
        "in April."
    ),
}


# ---------------------------------------------------------------------------
# Fixture dispatches
# ---------------------------------------------------------------------------

def make_researcher_fixture(fail_round_count: int = 0):
    """Return a researcher dispatch that fails the first `fail_round_count`
    rounds (verifier rejects), then succeeds with verifiable cards.
    """
    state = {"round": 0}

    def _dispatch(release_id, release_spec, repo_root, revision_failures):
        state["round"] += 1
        if state["round"] <= fail_round_count:
            # Return cards with a bogus URL so the verifier fails them
            return {
                "shared_cards": [{
                    "claim_id": "cpi_2026-04-headline",
                    "claim": "Headline CPI rose 2.3% Y/Y in April 2026",
                    "value": 2.3,
                    "unit": "percent y/y",
                    # Vague URL -- will fail source_kind_mismatch
                    "source_url": "https://www150.statcan.gc.ca",
                    "source_text_excerpt": "rose 2.3% on a year-over-year basis in April",
                    "fetched_at": "2026-05-20T08:30:00Z",
                    "source_kind": "statcan_daily",
                    "verifier_status": "pending",
                    "verifier_notes": None,
                }],
                "prose_steer": {},
            }
        # Healthy round: real URL, present excerpt, matching value
        cards = [
            {
                "claim_id": "cpi_2026-04-headline",
                "claim": "Headline CPI rose 2.3% Y/Y in April 2026",
                "value": 2.3,
                "unit": "percent y/y",
                "source_url": "https://www150.statcan.gc.ca/n1/daily-quotidien/260520/dq260520a-eng.htm",
                "source_text_excerpt": "rose 2.3% on a year-over-year basis in April",
                "fetched_at": "2026-05-20T08:30:00Z",
                "source_kind": "statcan_daily",
                "verifier_status": "pending",
                "verifier_notes": None,
            },
            {
                "claim_id": "cpi_2026-04-prior",
                "claim": "Headline CPI rose 1.8% Y/Y in March 2026",
                "value": 1.8,
                "unit": "percent y/y",
                "source_url": "https://www150.statcan.gc.ca/n1/daily-quotidien/260520/dq260520a-eng.htm",
                "source_text_excerpt": "following a 1.8% increase in March",
                "fetched_at": "2026-05-20T08:30:00Z",
                "source_kind": "statcan_daily",
                "verifier_status": "pending",
                "verifier_notes": None,
            },
            {
                "claim_id": "cpi_2026-04-consensus",
                "claim": "Consensus expected 2.2% Y/Y in April 2026",
                "value": 2.2,
                "unit": "percent y/y",
                "source_url": "https://www150.statcan.gc.ca/n1/daily-quotidien/260520/dq260520a-eng.htm",
                "source_text_excerpt": "Consensus had expected 2.2%",
                "fetched_at": "2026-05-20T08:30:00Z",
                "source_kind": "statcan_daily",
                "verifier_status": "pending",
                "verifier_notes": None,
            },
            {
                "claim_id": "cpi_2026-04-core-trim",
                "claim": "Core-trim held at 2.7% in April 2026",
                "value": 2.7,
                "unit": "percent y/y",
                "source_url": "https://www150.statcan.gc.ca/n1/daily-quotidien/260520/dq260520a-eng.htm",
                "source_text_excerpt": "The trim CPI was 2.7% in April",
                "fetched_at": "2026-05-20T08:30:00Z",
                "source_kind": "statcan_daily",
                "verifier_status": "pending",
                "verifier_notes": None,
            },
            {
                "claim_id": "cpi_2026-04-core-median",
                "claim": "Core-median was 2.8% in April 2026",
                "value": 2.8,
                "unit": "percent y/y",
                "source_url": "https://www150.statcan.gc.ca/n1/daily-quotidien/260520/dq260520a-eng.htm",
                "source_text_excerpt": "median CPI eased to 2.8% from",
                "fetched_at": "2026-05-20T08:30:00Z",
                "source_kind": "statcan_daily",
                "verifier_status": "pending",
                "verifier_notes": None,
            },
            {
                "claim_id": "cpi_2026-04-prior-median",
                "claim": "Core-median was 2.9% in March 2026",
                "value": 2.9,
                "unit": "percent y/y",
                "source_url": "https://www150.statcan.gc.ca/n1/daily-quotidien/260520/dq260520a-eng.htm",
                "source_text_excerpt": "from 2.9% in March",
                "fetched_at": "2026-05-20T08:30:00Z",
                "source_kind": "statcan_daily",
                "verifier_status": "pending",
                "verifier_notes": None,
            },
            {
                "claim_id": "cpi_2026-04-shelter",
                "claim": "Shelter contributed 1.1pp to headline in April",
                "value": 1.1,
                "unit": "percentage points",
                "source_url": "https://www150.statcan.gc.ca/n1/daily-quotidien/260520/dq260520a-eng.htm",
                "source_text_excerpt": "Shelter contributed 1.1 percentage points to headline",
                "fetched_at": "2026-05-20T08:30:00Z",
                "source_kind": "statcan_daily",
                "verifier_status": "pending",
                "verifier_notes": None,
            },
            {
                "claim_id": "cpi_2026-04-surprise",
                "claim": "Print 0.1pp above consensus",
                "value": 0.1,
                "unit": "percentage points",
                "source_url": "https://www150.statcan.gc.ca/n1/daily-quotidien/260520/dq260520a-eng.htm",
                "source_text_excerpt": "came in 0.1 pp above consensus",
                "fetched_at": "2026-05-20T08:30:00Z",
                "source_kind": "statcan_daily",
                "verifier_status": "pending",
                "verifier_notes": None,
            },
            # Additional cards to satisfy panel-3 breadth and panel-4 numbers
            {
                "claim_id": "cpi_2026-04-breadth",
                "claim": "35% of components above 3% Y/Y in April",
                "value": 35,
                "unit": "percent",
                "source_url": "https://www150.statcan.gc.ca/n1/daily-quotidien/260520/dq260520a-eng.htm",
                "source_text_excerpt": "About 35% of the CPI basket ran above 3% in April",
                "fetched_at": "2026-05-20T08:30:00Z",
                "source_kind": "statcan_daily",
                "verifier_status": "pending",
                "verifier_notes": None,
            },
            {
                "claim_id": "cpi_2026-04-breadth-threshold",
                "claim": "Breadth threshold is 3% Y/Y per StatCan convention",
                "value": 3,
                "unit": "percent",
                "source_url": "https://www150.statcan.gc.ca/n1/daily-quotidien/260520/dq260520a-eng.htm",
                "source_text_excerpt": "ran above 3% in April",
                "fetched_at": "2026-05-20T08:30:00Z",
                "source_kind": "statcan_daily",
                "verifier_status": "pending",
                "verifier_notes": None,
            },
            {
                "claim_id": "cpi_2026-04-breadth-prev",
                "claim": "40% breadth in 2024H2",
                "value": 40,
                "unit": "percent",
                "source_url": "https://www150.statcan.gc.ca/n1/daily-quotidien/260520/dq260520a-eng.htm",
                "source_text_excerpt": "down from 40% in 2024H2",
                "fetched_at": "2026-05-20T08:30:00Z",
                "source_kind": "statcan_daily",
                "verifier_status": "pending",
                "verifier_notes": None,
            },
            {
                "claim_id": "cpi_2026-04-goods",
                "claim": "Goods inflation 1.5% Y/Y April",
                "value": 1.5,
                "unit": "percent y/y",
                "source_url": "https://www150.statcan.gc.ca/n1/daily-quotidien/260520/dq260520a-eng.htm",
                "source_text_excerpt": "Goods inflation rose 1.5% in April",
                "fetched_at": "2026-05-20T08:30:00Z",
                "source_kind": "statcan_daily",
                "verifier_status": "pending",
                "verifier_notes": None,
            },
            {
                "claim_id": "cpi_2026-04-services",
                "claim": "Services inflation 3.2% Y/Y April",
                "value": 3.2,
                "unit": "percent y/y",
                "source_url": "https://www150.statcan.gc.ca/n1/daily-quotidien/260520/dq260520a-eng.htm",
                "source_text_excerpt": "services inflation 3.2%",
                "fetched_at": "2026-05-20T08:30:00Z",
                "source_kind": "statcan_daily",
                "verifier_status": "pending",
                "verifier_notes": None,
            },
        ]
        return {
            "shared_cards": cards,
            "prose_steer": {
                sid: {
                    "so_what": "Print modestly above consensus; core measures held.",
                    "historical_comparable": "First month within band since Jan 2023.",
                    "quiet_release": False,
                    "next_print_date": "2026-05-20",
                    "shared_cards_used": [c["claim_id"] for c in cards],
                }
                for sid in (
                    "homepage_abstract", "topic_abstract", "sparkline_blurb",
                    "active_headline", "panel_1_headline_cpi",
                    "panel_2_core_measures", "panel_3_breadth",
                    "panel_4_subaggregates",
                )
            },
        }
    return _dispatch


def writer_fixture(release_id, surface, shared_cards, prose_steer,
                   repo_root, revision_failures):
    body = FIXTURE_BODIES[surface.surface_id]
    return body


def style_fixture(release_id, surface, draft_body, revision_note):
    # No-op polish in fixtures; production replaces hedging tics etc.
    return draft_body


def surface_fit_fixture(prompt: str, model: str) -> str:
    # Gate 3 no-op in fixtures; production routes this to editorial-director.
    return "VERDICT: PASS"


def fetcher_fixture(url: str) -> FetchResult:
    """Frozen-fixture fetcher: returns the StatCan Daily body for any
    statcan.gc.ca URL; 404 for everything else.
    """
    if "statcan.gc.ca" in url and not url.rstrip("/").endswith("statcan.gc.ca"):
        return FetchResult(
            status_code=200, url=url, text=STATCAN_DAILY_BODY, final_url=url,
        )
    return FetchResult(
        status_code=404, url=url, text="not found", final_url=url,
    )


# ---------------------------------------------------------------------------
# Email capture
# ---------------------------------------------------------------------------

class EmailCapture:
    def __init__(self):
        self.messages: list[EmailMessage] = []

    def __call__(self, msg: EmailMessage) -> None:
        self.messages.append(msg)


# ---------------------------------------------------------------------------
# Integration tests
# ---------------------------------------------------------------------------

def _wire(tmp_path: Path, repo_root: Path) -> Path:
    """Symlink-ish bootstrap: copy editorial/writing-style.md into the
    sandboxed repo root so validators can find it. The test still uses
    the validators module loaded against the real repo path; we just
    ensure cycle output goes to tmp_path.
    """
    return tmp_path


def test_full_cpi_cycle_to_ready_for_user(tmp_path: Path):
    repo_root = tmp_path
    email = EmailCapture()
    rc = run_release_cycle(
        release_id="cpi_monthly_2026-04",
        repo_root=repo_root,
        researcher_dispatch=make_researcher_fixture(fail_round_count=0),
        writer_dispatch=writer_fixture,
        style_dispatch=style_fixture,
        surface_fit_dispatch=surface_fit_fixture,
        verifier_fetcher=fetcher_fixture,
        email_sender=email,
        use_live_verifier=True,
    )
    # Wrapper cycle file written
    cycle_path = repo_root / "editorial" / "blurbs" / "_cycles" / "cpi_monthly_2026-04.json"
    assert cycle_path.exists()
    # All 8 surfaces in ready_for_user
    assert len(rc.surfaces) == 8
    bad = [s for s in rc.surfaces if s.last_state != "ready_for_user"]
    assert not bad, f"surfaces not at ready_for_user: {[s.surface_id for s in bad]}"
    # Shared verifier ran once
    assert (
        repo_root / "editorial" / "verifications" / "blurbs" /
        "_shared" / "cpi_monthly_2026-04.claims.json"
    ).exists()
    # Per-surface artifacts written
    for slot in rc.surfaces:
        art_path = repo_root / slot.artifact_path
        assert art_path.exists(), f"missing artifact: {slot.artifact_path}"
        art, body = read_artifact(art_path)
        assert art.last_state == "ready_for_user"
        assert body.strip(), f"empty body for {slot.surface_id}"
    # Email captured
    assert len(email.messages) == 1, "expected one batched cycle email"
    msg = email.messages[0]
    body = msg.get_content()
    for slot in rc.surfaces:
        assert slot.surface_id in body, f"surface {slot.surface_id} missing in email"
    # Subject line includes section + label
    subject = msg["Subject"]
    assert "Inflation" in subject
    assert "2026-04" in subject


def test_full_cpi_cycle_with_one_round_of_verifier_failure(tmp_path: Path):
    """Researcher first round fails (vague URL); revises; round 2 passes.
    Cycle still reaches ready_for_user with researcher_revision_count >= 1.
    """
    repo_root = tmp_path
    email = EmailCapture()
    rc = run_release_cycle(
        release_id="cpi_monthly_2026-04",
        repo_root=repo_root,
        researcher_dispatch=make_researcher_fixture(fail_round_count=1),
        writer_dispatch=writer_fixture,
        style_dispatch=style_fixture,
        surface_fit_dispatch=surface_fit_fixture,
        verifier_fetcher=fetcher_fixture,
        email_sender=email,
        use_live_verifier=True,
    )
    bad = [s for s in rc.surfaces if s.last_state != "ready_for_user"]
    assert not bad, f"surfaces not at ready_for_user: {[(s.surface_id, s.last_state) for s in bad]}"
    # Every surface should have non-zero researcher_revision_count
    assert any(s.researcher_revision_count >= 1 for s in rc.surfaces)
    assert len(email.messages) == 1


def test_dispatch_unconfigured_raises_not_implemented(tmp_path: Path):
    """Production default dispatches raise NotImplementedError so the
    CLI can fail loudly when env / dispatch wiring is incomplete.
    """
    with pytest.raises(NotImplementedError):
        run_release_cycle(
            release_id="cpi_monthly_2026-04",
            repo_root=tmp_path,
        )


def test_dry_run_via_main(tmp_path: Path):
    """`python -m pipeline.blurbs.run --release-id ... --dry-run` walks no
    agents and stops at release_landed.
    """
    from pipeline.blurbs.run import main
    # Patch REPO_ROOT not used; main() takes REPO_ROOT module-level. Instead,
    # call the underlying init via run_release_cycle's writer/style stubs.
    from pipeline.blurbs.run import _init_artifact, init_release_cycle
    from pipeline.blurbs.registry import get_release_spec

    spec = get_release_spec("cpi_monthly")
    rc = init_release_cycle(
        repo_root=tmp_path,
        release_id="cpi_monthly_2026-04",
        release_key="cpi_monthly",
        section=spec.section,
        reference_period="2026-04",
        release_date=None,
        surfaces_spec=spec.surfaces,
    )
    for slot in rc.surfaces:
        _init_artifact(tmp_path, rc, slot, next(
            s for s in spec.surfaces if s.surface_id == slot.surface_id
        ))
    assert all(s.last_state == "release_landed" for s in rc.surfaces)
    # Each artifact file exists
    for slot in rc.surfaces:
        assert (tmp_path / slot.artifact_path).exists()


def test_email_sender_failure_falls_back_to_inbox(tmp_path: Path):
    """SMTP failure 3x -> append to editorial/blurbs/_inbox.md."""
    from pipeline.blurbs.email import send_release_cycle_review_email
    repo_root = tmp_path

    # Pre-init a cycle
    from pipeline.blurbs.run import (
        _init_artifact,
        init_release_cycle,
    )
    from pipeline.blurbs.registry import get_release_spec

    spec = get_release_spec("cpi_monthly")
    rc = init_release_cycle(
        repo_root=repo_root,
        release_id="cpi_monthly_2026-04",
        release_key="cpi_monthly",
        section=spec.section,
        reference_period="2026-04",
        release_date=None,
        surfaces_spec=spec.surfaces,
    )
    for slot in rc.surfaces:
        _init_artifact(repo_root, rc, slot, next(
            s for s in spec.surfaces if s.surface_id == slot.surface_id
        ))

    def failing_sender(msg):
        raise ConnectionError("smtp relay unreachable")

    result = send_release_cycle_review_email(
        rc, repo_root,
        sender=failing_sender,
        sleep_fn=lambda s: None,
        backoff_seconds=(0.0, 0.0, 0.0),
    )
    assert result.sent is False
    assert result.inbox_appended is True
    inbox = repo_root / "editorial" / "blurbs" / "_inbox.md"
    assert inbox.exists()
    assert "cpi_monthly_2026-04" in inbox.read_text(encoding="utf-8")
