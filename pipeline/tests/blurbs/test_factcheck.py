"""Tests for Mode B fact-check helpers."""

from __future__ import annotations

from pipeline.blurbs import factcheck as fc


def test_extract_numeric_tokens_basic():
    body = "Headline CPI rose 2.3% Y/Y in April, 0.1pp above consensus of 2.2%."
    tokens = fc.extract_numeric_tokens(body)
    raws = [t.raw for t in tokens]
    assert any("2.3%" in r for r in raws)
    assert any("0.1pp" in r for r in raws)
    assert any("2.2%" in r for r in raws)


def test_extract_numeric_tokens_handles_bps():
    body = "Spread tightened 5 bps in April."
    tokens = fc.extract_numeric_tokens(body)
    assert len(tokens) >= 1
    assert any(t.unit == "bps" for t in tokens)


def test_extract_numeric_tokens_skips_years():
    body = "Since 2023, CPI has held within band. April 2026 was no exception."
    tokens = fc.extract_numeric_tokens(body)
    # Year 2023 should NOT appear; 2026 also a year
    values = [t.value for t in tokens]
    assert 2023 not in values
    assert 2026 not in values


def _passing_card(claim_id: str, value: float | None, unit: str = "percent") -> fc.ClaimCardLike:
    return fc.ClaimCardLike(
        claim_id=claim_id, value=value, unit=unit, verifier_status="passed",
    )


def test_verify_token_finds_matching_card():
    cards = [_passing_card("headline", 2.3), _passing_card("prior", 1.8)]
    tok = fc.extract_numeric_tokens("CPI rose 2.3% in April.")[0]
    v = fc.verify_token(tok, cards)
    assert v.match_status == "match"
    assert v.backing_claim_id == "headline"


def test_verify_token_no_backing_card():
    cards = [_passing_card("headline", 2.3)]
    tok = fc.extract_numeric_tokens("CPI rose 7.1% in April.")[0]
    v = fc.verify_token(tok, cards)
    assert v.match_status == "no_backing_card"


def test_verify_token_rejects_unverified_cards():
    cards = [
        fc.ClaimCardLike(claim_id="bad", value=2.3, verifier_status="pending"),
        fc.ClaimCardLike(claim_id="bad2", value=2.3, verifier_status="failed:url_404"),
    ]
    tok = fc.extract_numeric_tokens("CPI rose 2.3% in April.")[0]
    v = fc.verify_token(tok, cards)
    assert v.match_status == "no_backing_card"


def test_factcheck_body_happy_path():
    cards = [_passing_card("h", 2.3), _passing_card("p", 1.8)]
    body = "Headline CPI rose 2.3% Y/Y in April, up from 1.8% in March."
    r = fc.factcheck_body(body, cards, surface_id="x", char_cap=500)
    assert r.ok
    assert r.body_chars < 500
    assert not r.tk_leakage


def test_factcheck_body_cap_exceeded():
    cards = [_passing_card("h", 2.3)]
    body = "x" * 121
    r = fc.factcheck_body(body, cards, surface_id="sparkline", char_cap=120)
    assert not r.ok
    assert r.cap_exceeded


def test_factcheck_body_tk_leakage():
    cards = [_passing_card("h", 2.3)]
    body = "Headline CPI rose 2.3% in April. TK consensus comparison."
    r = fc.factcheck_body(body, cards, surface_id="x", char_cap=500)
    assert not r.ok
    assert r.tk_leakage
