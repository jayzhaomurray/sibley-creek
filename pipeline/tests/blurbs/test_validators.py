"""Per-surface validator tests."""

from __future__ import annotations

import pytest

from pipeline.blurbs import validators as vd


# ---------------------------------------------------------------------------
# Happy-path bodies
# ---------------------------------------------------------------------------

SPARKLINE_OK = "Headline CPI rose 2.3% Y/Y in April, 0.1pp above consensus."
HEADLINE_OK = "Headline CPI ticked up to 2.3% in April, 0.1pp above consensus."
TOPIC_OK = (
    "Headline CPI rose 2.3% Y/Y in April, a 0.1pp acceleration from "
    "the 1.8% March pace and 0.1pp above the consensus 2.2%. The BoC's "
    "preferred core measures held: core-trim was 2.7%, core-median "
    "came in at 2.8% versus 2.9% in March. Shelter contributed 1.1pp "
    "to the April headline, with mortgage-interest cost continuing "
    "its mechanical fade from the 2024 peak."
)
HOMEPAGE_OK = (
    "Headline CPI in Canada rose 2.3% on a year-over-year basis in "
    "April, a 0.1pp acceleration from the 1.8% pace in March and "
    "0.1pp above the consensus of 2.2%. The BoC's preferred core "
    "measures held the line: core-trim was 2.7% and core-median came "
    "in at 2.8%, down from 2.9% the prior month. Shelter contributed "
    "1.1pp to headline as mortgage-interest cost continued its "
    "mechanical fade from the 2024 peak. The next CPI print is "
    "scheduled for the morning of May 20."
)
PANEL_OK = (
    "Headline CPI rose 2.3% Y/Y in April, a 0.1pp acceleration from "
    "March and 0.1pp above consensus of 2.2%. Core measures held: "
    "core-trim at 2.7% and core-median at 2.8%. Shelter contributed "
    "1.1pp."
)


def test_sparkline_happy_path_passes():
    r = vd.validate_surface_body("sparkline_blurb", SPARKLINE_OK)
    assert r.ok, r.reasons


def test_headline_happy_path_passes():
    r = vd.validate_surface_body("active_headline", HEADLINE_OK)
    assert r.ok, r.reasons


def test_topic_abstract_happy_path_passes():
    r = vd.validate_surface_body("topic_abstract", TOPIC_OK)
    assert r.ok, r.reasons


def test_homepage_abstract_happy_path_passes():
    r = vd.validate_surface_body("homepage_abstract", HOMEPAGE_OK)
    assert r.ok, r.reasons


def test_chart_commentary_happy_path_passes():
    r = vd.validate_surface_body("chart_commentary", PANEL_OK)
    assert r.ok, r.reasons


# ---------------------------------------------------------------------------
# Cap enforcement
# ---------------------------------------------------------------------------

def test_sparkline_cap_120_rejects_long_body():
    body = "Headline CPI rose 2.3% in April " * 10
    r = vd.validate_surface_body("sparkline_blurb", body)
    assert not r.ok
    assert any("char_cap" in f.rule for f in r.failures)


def test_homepage_cap_560_rejects_long_body():
    body = "Headline CPI rose 2.3%. " * 50
    r = vd.validate_surface_body("homepage_abstract", body)
    assert not r.ok
    assert any("char_cap" in f.rule for f in r.failures)


# ---------------------------------------------------------------------------
# Word count
# ---------------------------------------------------------------------------

def test_sparkline_below_word_min_rejected():
    r = vd.validate_surface_body("sparkline_blurb", "CPI rose.")
    assert not r.ok
    assert any(f.rule == "word_range" for f in r.failures)


def test_headline_above_word_max_rejected():
    body = "Headline CPI rose to 2.3% Y/Y in April " * 5 + "with the BoC watching."
    r = vd.validate_surface_body("active_headline", body)
    assert not r.ok
    assert any(f.rule == "word_range" or f.rule == "sentence_range"
               or f.rule == "char_cap" for f in r.failures)


# ---------------------------------------------------------------------------
# Sentence range
# ---------------------------------------------------------------------------

def test_headline_more_than_one_sentence_rejected():
    body = "CPI rose 2.3%. Core held at 2.7%."
    r = vd.validate_surface_body("active_headline", body)
    assert not r.ok
    assert any(f.rule == "sentence_range" for f in r.failures)


# ---------------------------------------------------------------------------
# active_headline-specific rules
# ---------------------------------------------------------------------------

def test_active_headline_must_end_with_period():
    body = "Headline CPI ticked up to 2.3% in April"
    r = vd.validate_surface_body("active_headline", body)
    assert not r.ok
    assert any(f.rule == "require_period_end" for f in r.failures)


def test_active_headline_needs_numeric_or_institution():
    # No number, no institution, but real prose
    body = "Inflation came in soft against the prior month."
    r = vd.validate_surface_body("active_headline", body)
    assert not r.ok
    assert any(f.rule == "numeric_or_institution_required" for f in r.failures)


def test_active_headline_named_institution_satisfies_rule():
    body = "BoC core-trim measure held its line against the print."
    r = vd.validate_surface_body("active_headline", body)
    # may still fail word range; we only assert the numeric_or_institution
    # rule is satisfied.
    assert not any(
        f.rule == "numeric_or_institution_required" for f in r.failures
    )


# ---------------------------------------------------------------------------
# sparkline subordinate-clause rule
# ---------------------------------------------------------------------------

def test_sparkline_subordinate_opener_rejected():
    body = "Although CPI rose 2.3% in April, consensus was 2.2%."
    r = vd.validate_surface_body("sparkline_blurb", body)
    assert not r.ok
    assert any(f.rule == "opening_subordinate_clause" for f in r.failures)


# ---------------------------------------------------------------------------
# Mode A bans
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "phrase",
    [
        "going forward",
        "at the end of the day",
        "in terms of",
        "the new normal",
        "needless to say",
        "hawkish hold",
        "constructive",
        "soft landing",  # appears in Section 6 as overused
    ],
)
def test_banned_phrase_in_chart_commentary_rejected(phrase):
    body = (
        f"Headline CPI rose 2.3% in April, {phrase} the BoC remains data "
        f"dependent. Core measures held near 2.7%. Watch shelter pass-through."
    )
    r = vd.validate_surface_body("chart_commentary", body)
    assert not r.ok, f"phrase {phrase!r} should have been caught"
    assert any(f.rule == "banned_construction" for f in r.failures), (
        f"phrase {phrase!r} not flagged: {r.reasons}"
    )


def test_bigsix_citation_construction_rejected():
    body = (
        "Headline CPI came in at 2.3% in April, in line with RBC expected "
        "2.2% but a touch above the prior. Core measures held. Next print May 20."
    )
    r = vd.validate_surface_body("chart_commentary", body)
    assert not r.ok
    assert any(f.rule == "bigsix_citation" for f in r.failures)


def test_street_citation_construction_rejected():
    body = (
        "Headline CPI rose 2.3% in April, above where the Street was looking "
        "for 2.2%. Core measures held near 2.7%. Next print May 20."
    )
    r = vd.validate_surface_body("chart_commentary", body)
    assert not r.ok
    assert any(f.rule == "street_citation" for f in r.failures)


def test_tk_leakage_rejected():
    body = (
        "Headline CPI rose 2.3% in April, TK the consensus comparison. "
        "Core measures held."
    )
    r = vd.validate_surface_body("chart_commentary", body)
    assert not r.ok
    assert any(f.rule == "tk_leakage" for f in r.failures)


def test_non_ascii_rejected():
    body = (
        "Headline CPI rose 2.3% in April -- a 0.1pp acceleration. "
        "Core-trim held at 2.7 %."  # contains non-ASCII U+2009 thin space
    )
    r = vd.validate_surface_body("chart_commentary", body)
    assert not r.ok
    assert any(f.rule == "ascii_only" for f in r.failures)


def test_unknown_surface_kind_rejected():
    r = vd.validate_surface_body("not_a_surface", "anything")
    assert not r.ok
    assert any(f.rule == "unknown_surface_kind" for f in r.failures)
