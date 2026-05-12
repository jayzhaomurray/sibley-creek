"""Tests for the Indeed Hiring Lab fetcher. No live HTTP calls.

Mirrors the alberta / yahoo fetcher test pattern: a minimal CSV payload
shaped like the real upstream, mocked at the httpx layer; we assert the
fetcher normalizes to the {date, value} contract and surfaces schema
drift loudly.
"""

from __future__ import annotations

import re

import pandas as pd
import pytest

from pipeline.fetch import indeed_hiring_lab


# Minimal payload matching the live schema observed on probe 2026-05-11.
# Two variable slices ("total postings" / "new postings") and both SA / NSA
# measures so we can exercise the slicing logic.
SAMPLE_AGGREGATE_CSV = (
    "date,jobcountry,indeed_job_postings_index_SA,"
    "indeed_job_postings_index_NSA,variable\n"
    "2020-02-01,CA,100,100,total postings\n"
    "2020-02-02,CA,99.93,100.1,total postings\n"
    "2020-02-03,CA,99.84,100.18,total postings\n"
    "2020-02-01,CA,100,100,new postings\n"
    "2020-02-02,CA,99.5,100.4,new postings\n"
)

SAMPLE_PROVINCIAL_CSV = (
    "date,province,indeed_job_postings_index\n"
    "2020-02-01,ab,100\n"
    "2020-02-02,ab,99.78\n"
    "2020-02-01,on,100\n"
    "2020-02-02,on,99.91\n"
)


def test_fetch_aggregate_postings_returns_total_postings_SA_by_default(httpx_mock):
    httpx_mock.add_response(
        method="GET",
        url=re.compile(r".*aggregate_job_postings_CA\.csv$"),
        text=SAMPLE_AGGREGATE_CSV,
        headers={"Content-Type": "text/csv"},
    )

    result = indeed_hiring_lab.fetch_aggregate_postings()

    assert result.name == "indeed_postings_ca"
    assert result.variable == "total postings"
    assert result.source_column == "indeed_job_postings_index_SA"
    assert list(result.data.columns) == ["date", "value"]
    # Three "total postings" rows in the payload.
    assert len(result.data) == 3
    # Values round-trip as floats.
    assert result.data["value"].iloc[0] == pytest.approx(100.0)
    assert result.data["value"].iloc[2] == pytest.approx(99.84)
    # Monotonically increasing dates.
    assert (result.data["date"].diff().dropna() > pd.Timedelta(0)).all()


def test_fetch_aggregate_postings_NSA_measure(httpx_mock):
    httpx_mock.add_response(
        method="GET",
        url=re.compile(r".*aggregate_job_postings_CA\.csv$"),
        text=SAMPLE_AGGREGATE_CSV,
        headers={"Content-Type": "text/csv"},
    )

    result = indeed_hiring_lab.fetch_aggregate_postings(measure="NSA")
    assert result.source_column == "indeed_job_postings_index_NSA"
    # Picks NSA values: 100, 100.1, 100.18
    assert result.data["value"].iloc[1] == pytest.approx(100.1)


def test_fetch_aggregate_postings_new_postings_variable(httpx_mock):
    httpx_mock.add_response(
        method="GET",
        url=re.compile(r".*aggregate_job_postings_CA\.csv$"),
        text=SAMPLE_AGGREGATE_CSV,
        headers={"Content-Type": "text/csv"},
    )

    result = indeed_hiring_lab.fetch_aggregate_postings(variable="new postings")
    assert result.variable == "new postings"
    # Two "new postings" rows.
    assert len(result.data) == 2


def test_fetch_aggregate_postings_rejects_bad_measure():
    with pytest.raises(ValueError, match="measure must be"):
        indeed_hiring_lab.fetch_aggregate_postings(measure="ADJ")


def test_fetch_aggregate_postings_raises_on_schema_drift(httpx_mock):
    """If Indeed renames or drops the SA column we want a loud failure."""
    bad_csv = (
        "date,jobcountry,index_value,variable\n"
        "2020-02-01,CA,100,total postings\n"
    )
    httpx_mock.add_response(
        method="GET",
        url=re.compile(r".*aggregate_job_postings_CA\.csv$"),
        text=bad_csv,
        headers={"Content-Type": "text/csv"},
    )
    with pytest.raises(ValueError, match="schema drift"):
        indeed_hiring_lab.fetch_aggregate_postings()


def test_fetch_aggregate_postings_raises_on_missing_variable(httpx_mock):
    csv_without_variable_match = SAMPLE_AGGREGATE_CSV
    httpx_mock.add_response(
        method="GET",
        url=re.compile(r".*aggregate_job_postings_CA\.csv$"),
        text=csv_without_variable_match,
        headers={"Content-Type": "text/csv"},
    )
    with pytest.raises(ValueError, match="no rows for variable"):
        indeed_hiring_lab.fetch_aggregate_postings(variable="quarterly postings")


def test_fetch_provincial_postings_parses_long_form(httpx_mock):
    httpx_mock.add_response(
        method="GET",
        url=re.compile(r".*provincial_postings_ca\.csv$"),
        text=SAMPLE_PROVINCIAL_CSV,
        headers={"Content-Type": "text/csv"},
    )

    result = indeed_hiring_lab.fetch_provincial_postings()
    assert list(result.data.columns) == ["date", "province", "value"]
    assert set(result.data["province"].unique()) == {"ab", "on"}
    assert len(result.data) == 4


def test_fetch_provincial_postings_raises_on_schema_drift(httpx_mock):
    bad_csv = "date,region,value\n2020-02-01,ab,100\n"
    httpx_mock.add_response(
        method="GET",
        url=re.compile(r".*provincial_postings_ca\.csv$"),
        text=bad_csv,
        headers={"Content-Type": "text/csv"},
    )
    with pytest.raises(ValueError, match="schema drift"):
        indeed_hiring_lab.fetch_provincial_postings()


def test_aggregate_monthly_mean_month_start_convention():
    daily = pd.DataFrame(
        {
            "date": pd.to_datetime(
                ["2024-01-01", "2024-01-15", "2024-01-31", "2024-02-01", "2024-02-15"]
            ),
            "value": [100.0, 102.0, 104.0, 110.0, 112.0],
        }
    )
    monthly = indeed_hiring_lab.aggregate_monthly_mean(daily)
    assert list(monthly.columns) == ["date", "value"]
    # Two months in the sample.
    assert len(monthly) == 2
    # Month-start convention: Jan = 2024-01-01, Feb = 2024-02-01.
    assert monthly["date"].iloc[0] == pd.Timestamp("2024-01-01")
    assert monthly["date"].iloc[1] == pd.Timestamp("2024-02-01")
    # Means: (100+102+104)/3 = 102.0, (110+112)/2 = 111.0
    assert monthly["value"].iloc[0] == pytest.approx(102.0)
    assert monthly["value"].iloc[1] == pytest.approx(111.0)


def test_aggregate_monthly_mean_empty_input_returns_empty():
    empty = pd.DataFrame({"date": pd.to_datetime([]), "value": []})
    out = indeed_hiring_lab.aggregate_monthly_mean(empty)
    assert out.empty


def test_url_helpers_point_to_master_branch():
    """The previous static lift hard-coded the wrong repo path; pin the
    correct one in tests so future renames trip a test failure."""
    assert "hiring-lab/job_postings_tracker" in indeed_hiring_lab.aggregate_url()
    assert "/master/" in indeed_hiring_lab.aggregate_url()
    assert indeed_hiring_lab.aggregate_url().endswith("aggregate_job_postings_CA.csv")
    assert indeed_hiring_lab.provincial_url().endswith("provincial_postings_ca.csv")
