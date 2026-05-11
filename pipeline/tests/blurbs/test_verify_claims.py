"""Tests for Mode A claims verification.

Covers all five failure reasons in the taxonomy:
    url_404 / text_not_present / value_mismatch / claim_overreach /
    source_kind_mismatch
plus the happy path. Uses an injected fake fetcher (frozen fixtures); never
makes real HTTP calls.
"""

from __future__ import annotations

import io
from pathlib import Path

import pytest
from ruamel.yaml import YAML

from pipeline.blurbs.verify_claims import (
    ClaimCard,
    FetchResult,
    VerifyResult,
    verify_claim_file,
)


_y = YAML(typ="rt")
_y.default_flow_style = False


def _write_cards(path: Path, cards: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    buf = io.StringIO()
    _y.dump(cards, buf)
    path.write_text(buf.getvalue(), encoding="utf-8")


def _load_cards(path: Path) -> list[dict]:
    raw = _y.load(path.read_text(encoding="utf-8"))
    return [dict(c) for c in (raw or [])]


# ---------------------------------------------------------------------------
# Frozen-fixture HTML bodies
# ---------------------------------------------------------------------------

STATCAN_DAILY_HTML = """
<html><head><title>The Daily</title></head><body>
<div class="content">
<p>The Consumer Price Index (CPI) rose 2.3% on a year-over-year basis in
April, following a 1.8% increase in March. Excluding gasoline, the CPI
rose 2.4% Y/Y in April.</p>
<p>StatCan release vintage 2026-05-20.</p>
</div></body></html>
"""

BOC_PRESS_HTML = """
<html><body>
<h1>Bank of Canada maintains policy rate</h1>
<p>The Bank of Canada today held its target for the overnight rate at
2.25%, with the Bank Rate at 2.5% and the deposit rate at 2.20%.</p>
</body></html>
"""

GLOBE_ARTICLE_HTML = """
<html><body><h1>BoC pauses</h1>
<p>The Bank of Canada held the line on Wednesday, citing data uncertainty.</p>
</body></html>
"""


def _fake_fetcher(responses: dict[str, FetchResult]):
    def _fetcher(url: str) -> FetchResult:
        if url in responses:
            return responses[url]
        return FetchResult(
            status_code=404, url=url, text="not found", final_url=url,
        )
    return _fetcher


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------

def test_verify_claim_file_happy_path_all_pass(tmp_path):
    cards_path = tmp_path / "research" / "blurb_context" / "cpi_monthly_2026-04" / "_shared_cards.yaml"
    _write_cards(cards_path, [
        {
            "claim_id": "cpi_2026-04-headline",
            "claim": "Headline CPI rose 2.3% Y/Y in April 2026",
            "value": 2.3,
            "unit": "percent y/y",
            "source_url": "https://www150.statcan.gc.ca/n1/daily-quotidien/260520/dq260520a-eng.htm",
            "source_text_excerpt": "The Consumer Price Index (CPI) rose 2.3% on a year-over-year basis in April",
            "fetched_at": "2026-05-20T08:30:00Z",
            "source_kind": "statcan_daily",
            "verifier_status": "pending",
            "verifier_notes": None,
        },
        {
            "claim_id": "boc-rate-2026-04",
            "claim": "BoC held the overnight rate at 2.25% in April 2026",
            "value": 2.25,
            "unit": "percent",
            "source_url": "https://www.bankofcanada.ca/2026/04/fad-press-release-2026-04-29/",
            "source_text_excerpt": "Bank of Canada today held its target for the overnight rate at 2.25%",
            "fetched_at": "2026-05-20T08:30:00Z",
            "source_kind": "boc_press_release",
            "verifier_status": "pending",
            "verifier_notes": None,
        },
    ])
    fetcher = _fake_fetcher({
        "https://www150.statcan.gc.ca/n1/daily-quotidien/260520/dq260520a-eng.htm":
            FetchResult(status_code=200, url="x", text=STATCAN_DAILY_HTML, final_url="x"),
        "https://www.bankofcanada.ca/2026/04/fad-press-release-2026-04-29/":
            FetchResult(status_code=200, url="x", text=BOC_PRESS_HTML, final_url="x"),
    })
    result = verify_claim_file(cards_path, fetcher=fetcher)
    assert result.total_cards == 2
    assert result.passed_count == 2
    assert result.failed_count == 0
    persisted = _load_cards(cards_path)
    assert all(c["verifier_status"] == "passed" for c in persisted)


# ---------------------------------------------------------------------------
# url_404
# ---------------------------------------------------------------------------

def test_verify_url_404(tmp_path):
    cards_path = tmp_path / "_shared_cards.yaml"
    _write_cards(cards_path, [{
        "claim_id": "rotted",
        "claim": "x",
        "value": None,
        "unit": None,
        "source_url": "https://www.bankofcanada.ca/path-that-404s",
        "source_text_excerpt": "anything",
        "fetched_at": "2026-05-20T08:30:00Z",
        "source_kind": "boc_press_release",
        "verifier_status": "pending",
        "verifier_notes": None,
    }])
    fetcher = _fake_fetcher({
        "https://www.bankofcanada.ca/path-that-404s":
            FetchResult(status_code=404, url="x", text="not found", final_url="x"),
    })
    result = verify_claim_file(cards_path, fetcher=fetcher)
    assert result.failed_count == 1
    assert result.failures[0].reason == "url_404"


# ---------------------------------------------------------------------------
# text_not_present
# ---------------------------------------------------------------------------

def test_verify_text_not_present(tmp_path):
    cards_path = tmp_path / "_shared_cards.yaml"
    _write_cards(cards_path, [{
        "claim_id": "tnp",
        "claim": "Made-up claim",
        "value": None,
        "unit": None,
        "source_url": "https://www.bankofcanada.ca/2026/04/fad-press-release-2026-04-29/",
        "source_text_excerpt": "This sentence is not anywhere on the page that was fetched.",
        "fetched_at": "2026-05-20T08:30:00Z",
        "source_kind": "boc_press_release",
        "verifier_status": "pending",
        "verifier_notes": None,
    }])
    fetcher = _fake_fetcher({
        "https://www.bankofcanada.ca/2026/04/fad-press-release-2026-04-29/":
            FetchResult(status_code=200, url="x", text=BOC_PRESS_HTML, final_url="x"),
    })
    result = verify_claim_file(cards_path, fetcher=fetcher)
    assert result.failed_count == 1
    assert result.failures[0].reason == "text_not_present"


# ---------------------------------------------------------------------------
# value_mismatch (the 2.75-vs-2.25 failure mode)
# ---------------------------------------------------------------------------

def test_verify_value_mismatch(tmp_path):
    cards_path = tmp_path / "_shared_cards.yaml"
    _write_cards(cards_path, [{
        "claim_id": "vm",
        "claim": "BoC held rate at 2.75% in April 2026",
        "value": 2.75,  # wrong value; source says 2.25%
        "unit": "percent",
        "source_url": "https://www.bankofcanada.ca/2026/04/fad-press-release-2026-04-29/",
        "source_text_excerpt": "Bank of Canada today held its target for the overnight rate at",
        "fetched_at": "2026-05-20T08:30:00Z",
        "source_kind": "boc_press_release",
        "verifier_status": "pending",
        "verifier_notes": None,
    }])
    fetcher = _fake_fetcher({
        "https://www.bankofcanada.ca/2026/04/fad-press-release-2026-04-29/":
            FetchResult(status_code=200, url="x", text=BOC_PRESS_HTML, final_url="x"),
    })
    result = verify_claim_file(cards_path, fetcher=fetcher)
    assert result.failed_count == 1
    assert result.failures[0].reason == "value_mismatch"


# ---------------------------------------------------------------------------
# source_kind_mismatch
# ---------------------------------------------------------------------------

def test_verify_source_kind_mismatch_wrong_domain(tmp_path):
    cards_path = tmp_path / "_shared_cards.yaml"
    _write_cards(cards_path, [{
        "claim_id": "skm",
        "claim": "BoC paused",
        "value": None,
        "unit": None,
        "source_url": "https://www.theglobeandmail.com/business/article-boc-pauses/",
        "source_text_excerpt": "The Bank of Canada held the line",
        "fetched_at": "2026-05-20T08:30:00Z",
        "source_kind": "boc_press_release",  # wrong: this is a Globe article
        "verifier_status": "pending",
        "verifier_notes": None,
    }])
    fetcher = _fake_fetcher({
        "https://www.theglobeandmail.com/business/article-boc-pauses/":
            FetchResult(status_code=200, url="x", text=GLOBE_ARTICLE_HTML, final_url="x"),
    })
    result = verify_claim_file(cards_path, fetcher=fetcher)
    assert result.failed_count == 1
    assert result.failures[0].reason == "source_kind_mismatch"


def test_verify_source_kind_mismatch_root_domain(tmp_path):
    cards_path = tmp_path / "_shared_cards.yaml"
    _write_cards(cards_path, [{
        "claim_id": "skm-root",
        "claim": "BoC paused",
        "value": None,
        "unit": None,
        "source_url": "https://www.bankofcanada.ca",
        "source_text_excerpt": "something",
        "fetched_at": "2026-05-20T08:30:00Z",
        "source_kind": "boc_press_release",
        "verifier_status": "pending",
        "verifier_notes": None,
    }])
    fetcher = _fake_fetcher({})
    result = verify_claim_file(cards_path, fetcher=fetcher)
    assert result.failed_count == 1
    assert result.failures[0].reason == "source_kind_mismatch"


# ---------------------------------------------------------------------------
# claim_overreach
# ---------------------------------------------------------------------------

def test_verify_claim_overreach_is_flagged_when_pin_supports(tmp_path):
    """The mechanical verifier passes a card if the text + value match.
    claim_overreach detection is an LLM-judgment piece deferred to the
    Opus dispatch; the orchestrator's mechanical layer flags this for
    human review by surfacing the verdict and the verifier_notes.

    For this test we assert that the failure-reason enum *includes*
    `claim_overreach` and that a programmatically-injected
    `claim_overreach` status round-trips through the VerifyResult model.
    """
    from pipeline.blurbs.verify_claims import CardFailure
    f = CardFailure(
        claim_id="x",
        reason="claim_overreach",
        verifier_notes="claim extrapolates beyond source",
    )
    assert f.reason == "claim_overreach"
    # And the full VerifyResult round-trips
    vr = VerifyResult(
        total_cards=1, passed_count=0, failed_count=1,
        failures=[f], cards_path="x",
    )
    payload = vr.model_dump(mode="json")
    assert payload["failures"][0]["reason"] == "claim_overreach"


# ---------------------------------------------------------------------------
# Verdict summary written
# ---------------------------------------------------------------------------

def test_verdict_summary_written(tmp_path):
    cards_path = tmp_path / "_shared_cards.yaml"
    _write_cards(cards_path, [{
        "claim_id": "h",
        "claim": "Headline CPI 2.3%",
        "value": 2.3,
        "unit": "percent y/y",
        "source_url": "https://www150.statcan.gc.ca/n1/daily-quotidien/260520/dq260520a-eng.htm",
        "source_text_excerpt": "The Consumer Price Index (CPI) rose 2.3%",
        "fetched_at": "2026-05-20T08:30:00Z",
        "source_kind": "statcan_daily",
        "verifier_status": "pending",
        "verifier_notes": None,
    }])
    fetcher = _fake_fetcher({
        "https://www150.statcan.gc.ca/n1/daily-quotidien/260520/dq260520a-eng.htm":
            FetchResult(status_code=200, url="x", text=STATCAN_DAILY_HTML, final_url="x"),
    })
    summary_path = tmp_path / "verdict.json"
    result = verify_claim_file(cards_path, fetcher=fetcher, verdict_summary_path=summary_path)
    assert summary_path.exists()
    import json
    payload = json.loads(summary_path.read_text())
    assert payload["passed_count"] == 1


# ---------------------------------------------------------------------------
# Staleness warning
# ---------------------------------------------------------------------------

def test_verify_stale_fetched_at_warns_but_passes(tmp_path):
    cards_path = tmp_path / "_shared_cards.yaml"
    _write_cards(cards_path, [{
        "claim_id": "stale",
        "claim": "Headline CPI 2.3%",
        "value": 2.3,
        "unit": "percent y/y",
        "source_url": "https://www150.statcan.gc.ca/n1/daily-quotidien/260520/dq260520a-eng.htm",
        "source_text_excerpt": "The Consumer Price Index (CPI) rose 2.3%",
        "fetched_at": "2026-04-01T08:30:00Z",  # very old
        "source_kind": "statcan_daily",
        "verifier_status": "pending",
        "verifier_notes": None,
    }])
    fetcher = _fake_fetcher({
        "https://www150.statcan.gc.ca/n1/daily-quotidien/260520/dq260520a-eng.htm":
            FetchResult(status_code=200, url="x", text=STATCAN_DAILY_HTML, final_url="x"),
    })
    result = verify_claim_file(
        cards_path,
        fetcher=fetcher,
        cycle_created_at="2026-05-20T08:30:00Z",
    )
    assert result.failed_count == 0
    cards = _load_cards(cards_path)
    assert cards[0]["verifier_status"] == "passed"
    assert "WARN" in (cards[0]["verifier_notes"] or "")
