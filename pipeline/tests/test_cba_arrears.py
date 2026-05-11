"""Tests for the CBA mortgage-arrears PDF parser.

The parser side is fully covered by synthetic page-text fixtures so the
tests never touch the live CBA URL. The HTTP layer (find_and_download_latest)
is mocked via pytest-httpx in the integration test.
"""

from __future__ import annotations

import pandas as pd
import pytest

from pipeline.fetch import cba_arrears


# --------------------------------------------------------------------------- #
# Fixtures: synthetic page-text strings shaped like the real CBA PDF
# --------------------------------------------------------------------------- #

PAGE0_TEXT = """CANADIAN BANKERS ASSOCIATION DB50 PUBLIC
Number of Residential Mortgages in Arrears
LOCATION Total Number of \
Mortgages
Number of Mortgages in \
Arrears*
% of Arrears to Total \
Number of Mortgages
ATLANTIC 336,691 1,045 0.31%
QUEBEC 931,452 1,809 0.19%
ONTARIO 2,156,908 6,555 0.30%
MANITOBA 114,849 408 0.36%
SASKATCHEWAN 120,856 640 0.53%
ALBERTA 573,734 1,564 0.27%
BRITISH COLUMBIA 692,142 1,728 0.25%
TERRITORIES 10,603
CANADA 4,937,235 13,749 0.28%
Includes data from BMO, CIBC, National Bank of Canada, RBC Royal Bank, Scotiabank, TD Canada Trust,
Manulife Bank (as of April 2004), Laurentian Bank (as of October 2010), Equitable Bank (as of November 2020)
* Mortgage arrears is three or more months
** Data for Yukon included in British Columbia. Data for NWT and NU included in Alberta.
Month Ended February 28, 2026
"""

PAGE1_TEXT = """CANADIAN BANKERS ASSOCIATION DB50 PUBLIC
Number of Residential Mortgages in Arrears REGION: CANADA
1995-01 2,184,443 11,014 0.50% 2011-01 4,192,307 18,702 0.45%
1995-02 2,187,413 10,907 0.50% 2011-02 4,192,738 18,624 0.44%
2025-12 4,954,886 12,900 0.26% 2026-12
2026-01 4,945,454 13,442 0.27%
2026-02 4,937,235 13,749 0.28%
"""

PAGE2_TEXT = """REGION: ATLANTIC
2025-12 380,000 1,000 0.26%
2026-01 381,000 1,020 0.27%
"""


def test_parse_as_of_date():
    d = cba_arrears._parse_as_of_date(PAGE0_TEXT)
    assert d == pd.Timestamp("2026-02-28")


def test_parse_as_of_date_missing_raises():
    with pytest.raises(ValueError, match="Month Ended"):
        cba_arrears._parse_as_of_date("totally unrelated text")


def test_parse_provincial_snapshot_extracts_all_seven_provinces():
    as_of = pd.Timestamp("2026-02-28")
    df = cba_arrears._parse_provincial_snapshot(PAGE0_TEXT, as_of)
    assert set(df["province"]) == {
        "atlantic", "quebec", "ontario", "manitoba",
        "saskatchewan", "alberta", "british_columbia",
    }
    by_prov = dict(zip(df["province"], df["value"]))
    assert by_prov["saskatchewan"] == pytest.approx(0.53)
    assert by_prov["quebec"] == pytest.approx(0.19)
    # All rows carry the as_of timestamp.
    assert (df["date"] == as_of).all()
    # TERRITORIES is intentionally skipped (no arrears count published).
    assert "territories" not in set(df["province"])


def test_parse_national_history_stitches_columns_and_drops_empty_future_rows():
    df = cba_arrears._parse_national_history([PAGE0_TEXT, PAGE1_TEXT, PAGE2_TEXT])
    # 7 valid time-series rows: the two-column page layout has 1995-01 +
    # 2011-01 on line 1 (older column + newer column), 1995-02 + 2011-02
    # on line 2, then three trailing rows in the newer column (2025-12,
    # 2026-01, 2026-02). The "2026-12" with no values is a layout
    # placeholder for an unpublished future month and must NOT match.
    assert len(df) == 7
    # Chronological order.
    assert list(df["date"]) == list(df["date"].sort_values())
    # Latest value is 0.28% (Feb 2026).
    latest = df.iloc[-1]
    assert latest["date"] == pd.Timestamp("2026-02-01")
    assert latest["value"] == pytest.approx(0.28)
    # The province-history page (PAGE2_TEXT) must NOT contribute rows --
    # parsing stops at the first REGION header that isn't CANADA.
    # Atlantic's 2025-12 row would have been 0.26%; assert no duplicate
    # by counting unique 2025-12 entries.
    dec25 = df[df["date"] == pd.Timestamp("2025-12-01")]
    assert len(dec25) == 1
    assert dec25.iloc[0]["value"] == pytest.approx(0.26)  # CANADA, not Atlantic


def test_parse_cba_arrears_pdf_assembles_full_result(monkeypatch):
    """parse_cba_arrears_pdf composes parse_as_of + provincial + national."""
    # Bypass the pypdf round-trip by stubbing _extract_pdf_text.
    monkeypatch.setattr(
        cba_arrears,
        "_extract_pdf_text",
        lambda _bytes: [PAGE0_TEXT, PAGE1_TEXT, PAGE2_TEXT],
    )
    result = cba_arrears.parse_cba_arrears_pdf(b"<irrelevant>")
    assert result.as_of_date == pd.Timestamp("2026-02-28")
    assert result.release_label == (2026, "february")
    # National history latest matches the cross-section CANADA cell (0.28%).
    assert result.national_history.iloc[-1]["value"] == pytest.approx(0.28)
    assert len(result.provincial_snapshot) == 7


def test_latest_release_candidates_walks_back_from_lag():
    """Candidates begin at today - 2 months (CBA's typical publication lag)
    and walk further back. Most-recent candidate is listed first."""
    candidates = cba_arrears.latest_release_candidates(
        today=pd.Timestamp("2026-05-11").date(), lookback=3,
    )
    # First candidate: 2026-05-11 minus 2 months -> March 2026.
    assert candidates[0] == (2026, "march")
    # Last candidate: 2 + 3 = 5 months back -> December 2025.
    assert candidates[-1] == (2025, "december")
    # lookback+1 entries.
    assert len(candidates) == 4


def test_release_url_for_lowercases_month():
    url = cba_arrears.release_url_for(2026, "February")
    assert "stat-mortgages-arrears-february-2026-en.pdf" in url


def test_find_and_download_latest_probes_in_order(httpx_mock):
    """Probe most-recent candidate first; if it 404s, walk back. Stop at
    the first 200 with application/pdf content type."""
    # today=2026-05-11, lookback=2 -> probe 2026-03, 2026-02, 2026-01, 2025-12.
    # First 200 hit is the second probe (2026-02).
    httpx_mock.add_response(
        url=cba_arrears.release_url_for(2026, "march"),
        status_code=404,
    )
    httpx_mock.add_response(
        url=cba_arrears.release_url_for(2026, "february"),
        status_code=200,
        content=b"%PDF-fake",
        headers={"content-type": "application/pdf"},
    )
    pdf_bytes, label = cba_arrears.find_and_download_latest(
        today=pd.Timestamp("2026-05-11").date(),
        lookback=2,
    )
    assert pdf_bytes == b"%PDF-fake"
    assert label == (2026, "february")


def test_find_and_download_latest_raises_when_none_found(httpx_mock):
    """All candidates 404 -> FileNotFoundError so the build's _safe wrapper
    surfaces the failure rather than silently returning empty data."""
    for (year, month) in cba_arrears.latest_release_candidates(
        today=pd.Timestamp("2026-05-11").date(), lookback=1,
    ):
        httpx_mock.add_response(
            url=cba_arrears.release_url_for(year, month),
            status_code=404,
        )
    with pytest.raises(FileNotFoundError, match="No CBA arrears PDF found"):
        cba_arrears.find_and_download_latest(
            today=pd.Timestamp("2026-05-11").date(),
            lookback=1,
        )
