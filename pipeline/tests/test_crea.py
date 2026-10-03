"""Tests for the CREA MLS HPI fetcher. No live network, no production caches.

Everything here runs against an HTML fixture, an in-memory ZIP and
pytest-httpx; nothing is read from or written to data/.
"""

from __future__ import annotations

import io
import logging
import zipfile
from datetime import date
from pathlib import Path

import httpx
import pandas as pd
import pytest

from pipeline.fetch import crea

FIXTURE_PAGE = Path(__file__).parent / "fixtures" / "crea_hpi_tool_page.html"
SEPT_URL = "https://www.crea.ca/files/mls-hpi-data/MLS_HPI_Sept_2026.zip"


def _make_zip(last_month: str = "2026-08-01", *, drop_column: str | None = None) -> bytes:
    """Build a CREA-shaped ZIP: one SA-monthly workbook, one sheet per geography."""
    dates = pd.date_range(end=last_month, periods=14, freq="MS")
    frame = pd.DataFrame({
        "Date": dates,
        "Composite_HPI_SA": [250.0 + i for i in range(len(dates))],
        "Single_Family_HPI_SA": [260.0 + i for i in range(len(dates))],
        "Composite_Benchmark_SA": [600000 + 1000 * i for i in range(len(dates))],
    })
    if drop_column:
        frame = frame.drop(columns=[drop_column])
    xlsx = io.BytesIO()
    with pd.ExcelWriter(xlsx, engine="openpyxl") as writer:
        for sheet in crea.CMA_SHEETS.values():
            frame.to_excel(writer, sheet_name=sheet, index=False)
    out = io.BytesIO()
    with zipfile.ZipFile(out, "w") as zf:
        zf.writestr("Seasonally Adjusted (M).xlsx", xlsx.getvalue())
    return out.getvalue()


def _serve(httpx_mock, routes: dict[str, httpx.Response]) -> list[str]:
    """Answer every request from `routes`; anything else is CREA's 404 shell."""
    seen: list[str] = []

    def _callback(request: httpx.Request) -> httpx.Response:
        url = str(request.url)
        seen.append(url)
        return routes.get(url) or httpx.Response(404, json={"error": "not found"})

    httpx_mock.add_callback(_callback, is_reusable=True)
    return seen


# --------------------------------------------------------------------------- #
# Label + link parsing
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize("label,expected", [
    ("May_2026", date(2026, 5, 1)),
    ("Aug_2026", date(2026, 8, 1)),
    ("Sept_2026", date(2026, 9, 1)),
    ("Sep_2026", date(2026, 9, 1)),
    ("September_2026", date(2026, 9, 1)),
    ("Q3_2026", None),
    ("Smarch_2026", None),
])
def test_parse_release_label(label, expected):
    assert crea.parse_release_label(label) == expected


def test_month_label_variants_cover_known_spellings():
    assert crea.month_label_variants(2026, 9) == ["September_2026", "Sep_2026", "Sept_2026"]
    assert crea.month_label_variants(2026, 8) == ["August_2026", "Aug_2026"]
    # "May" is its own abbreviation; no duplicate probe.
    assert crea.month_label_variants(2026, 5) == ["May_2026"]


def test_extract_zip_links_from_page_fixture():
    links = crea.extract_zip_links(FIXTURE_PAGE.read_text(encoding="utf-8"))
    # The methodology PDF under the same /files/mls-hpi-data/ path is ignored.
    assert links == [(SEPT_URL, "Sept_2026")]


def test_extract_zip_links_orders_newest_first_and_resolves_relative():
    html = (
        '<a href="/files/mls-hpi-data/MLS_HPI_Aug_2026.zip">old</a>'
        "<a href='/files/mls-hpi-data/MLS_HPI_Sept_2026.zip'>new</a>"
    )
    assert [label for _, label in crea.extract_zip_links(html)] == ["Sept_2026", "Aug_2026"]
    assert crea.extract_zip_links(html)[0][0] == SEPT_URL


# --------------------------------------------------------------------------- #
# Discovery
# --------------------------------------------------------------------------- #

def test_find_available_release_prefers_page_link(httpx_mock):
    payload = _make_zip()
    seen = _serve(httpx_mock, {
        crea.HPI_TOOL_PAGE_URL: httpx.Response(200, text=FIXTURE_PAGE.read_text(encoding="utf-8")),
        SEPT_URL: httpx.Response(
            200, content=payload, headers={"Last-Modified": "Mon, 14 Sep 2026 22:15:52 GMT"},
        ),
    })

    release = crea.find_available_release(today=date(2026, 10, 3))

    assert release.label == "Sept_2026"
    assert release.url == SEPT_URL
    assert release.discovered_via == "page"
    assert release.published == date(2026, 9, 14)
    assert release.zip_bytes == payload
    # No dated-URL guessing when the page answers.
    assert seen == [crea.HPI_TOOL_PAGE_URL, SEPT_URL]


def test_find_available_release_falls_back_to_abbreviated_guess(httpx_mock):
    """Page has lost its link; the Oct 2026 regression case must still resolve.

    The old fetcher only tried full month names, 404ed on September_2026 and
    walked back to a months-old ZIP. The guess must find Sept_2026.
    """
    seen = _serve(httpx_mock, {
        crea.HPI_TOOL_PAGE_URL: httpx.Response(200, text="<html><body>redesigned</body></html>"),
        SEPT_URL: httpx.Response(200, content=_make_zip()),
    })

    release = crea.find_available_release(today=date(2026, 10, 3))

    assert release.label == "Sept_2026"
    assert release.discovered_via == "dated-url-guess"
    assert release.published is None
    base = crea.CREA_BASE_URL
    assert seen == [
        crea.HPI_TOOL_PAGE_URL,
        f"{base}/MLS_HPI_October_2026.zip",
        f"{base}/MLS_HPI_Oct_2026.zip",
        f"{base}/MLS_HPI_September_2026.zip",
        f"{base}/MLS_HPI_Sep_2026.zip",
        SEPT_URL,
    ]


def test_find_available_release_rejects_non_zip_200(httpx_mock):
    """A 200 that is an HTML shell, not an archive, is not a release."""
    _serve(httpx_mock, {
        crea.HPI_TOOL_PAGE_URL: httpx.Response(200, text=FIXTURE_PAGE.read_text(encoding="utf-8")),
        SEPT_URL: httpx.Response(200, text="<html>soft 404</html>"),
    })
    with pytest.raises(FileNotFoundError, match="No CREA MLS HPI ZIP found"):
        crea.find_available_release(today=date(2026, 10, 3), lookback=1)


def test_find_available_release_raises_when_nothing_resolves(httpx_mock):
    _serve(httpx_mock, {})
    with pytest.raises(FileNotFoundError) as excinfo:
        crea.find_available_release(today=date(2026, 10, 3), lookback=1)
    assert "MLS_HPI_Sept_2026.zip" in str(excinfo.value)


# --------------------------------------------------------------------------- #
# Freshness guard
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize("today,lag", [
    (date(2026, 9, 20), 1),   # just after the mid-month release
    (date(2026, 10, 3), 2),   # before the next release: normal
])
def test_freshness_passes_quietly_in_normal_window(today, lag, caplog):
    with caplog.at_level(logging.WARNING, logger="pipeline.fetch.crea"):
        assert crea.check_release_freshness(date(2026, 8, 1), today=today, label="Sept_2026") == lag
    assert caplog.records == []


def test_freshness_warns_at_one_missed_cycle(caplog):
    with caplog.at_level(logging.WARNING, logger="pipeline.fetch.crea"):
        lag = crea.check_release_freshness(date(2026, 8, 1), today=date(2026, 11, 30), label="Sept_2026")
    assert lag == 3
    assert any("late or missed" in r.getMessage() for r in caplog.records)


def test_freshness_fails_on_the_2026_incident():
    """May_2026 ZIP (reference April) must fail from August, not slide to October."""
    # Still tolerated (with a warning) through July ...
    assert crea.check_release_freshness(date(2026, 4, 1), today=date(2026, 7, 31), label="May_2026") == 3
    # ... and a hard failure from the first build of August.
    with pytest.raises(crea.CreaStaleReleaseError, match="2026-04"):
        crea.check_release_freshness(date(2026, 4, 1), today=date(2026, 8, 1), label="May_2026")


def test_freshness_handles_year_boundary():
    assert crea.reference_lag_months(date(2025, 11, 1), date(2026, 1, 10)) == 2


# --------------------------------------------------------------------------- #
# Workbook parsing
# --------------------------------------------------------------------------- #

def test_fetch_geography_parses_all_seven_geographies():
    payload = _make_zip("2026-08-01")
    for geo, sheet in crea.CMA_SHEETS.items():
        result = crea.fetch_geography(payload, geo, "Sept_2026")
        assert result.sheet_name == sheet
        assert list(result.data.columns) == ["date", "value"]
        assert len(result.data) == 14
        assert result.data["value"].iloc[-1] == pytest.approx(263.0)
        assert result.benchmark_data["value"].iloc[-1] == pytest.approx(613000)
        assert crea.latest_reference_month(result) == date(2026, 8, 1)


def test_fetch_geography_names_missing_column():
    payload = _make_zip(drop_column="Composite_HPI_SA")
    with pytest.raises(ValueError, match="Composite_HPI_SA"):
        crea.fetch_geography(payload, "toronto", "Sept_2026")


def test_latest_reference_month_ignores_trailing_blank_rows():
    data = pd.DataFrame({
        "date": pd.to_datetime(["2026-06-01", "2026-07-01", "2026-08-01"]),
        "value": [1.0, 2.0, None],
    })
    result = crea.CreaFetchResult("canada", "AGGREGATE", "Sept_2026", data, data)
    assert crea.latest_reference_month(result) == date(2026, 7, 1)
