"""Tests for the BoC Valet client. No live API calls."""

from __future__ import annotations

import re

import pandas as pd
import pytest

from pipeline.fetch import boc


def test_fetch_series_parses_observations(httpx_mock, sample_valet_payload):
    series_key = "STATIC_ATABLE_V39079"
    httpx_mock.add_response(
        method="GET",
        url=re.compile(r".*/valet/observations/.*"),
        json=sample_valet_payload,
    )

    result = boc.fetch_series(series_key, start_date="1990-01-01")

    assert result.series_key == series_key
    # 4 observations in, 1 has null value -> 3 out
    assert len(result.data) == 3
    assert list(result.data.columns) == ["date", "value"]
    assert (result.data["date"].diff().dropna() > pd.Timedelta(0)).all()
    assert result.data["value"].iloc[0] == pytest.approx(3.25)
    # Series metadata block lifted through
    assert result.label == "Target for the overnight rate"
    assert result.description and "overnight" in result.description.lower()


def test_fetch_series_raises_when_no_observations(httpx_mock):
    httpx_mock.add_response(
        method="GET",
        url=re.compile(r".*/valet/observations/.*"),
        json={"terms": {"url": "..."}, "seriesDetail": {}, "observations": []},
    )
    with pytest.raises(ValueError, match="no observations"):
        boc.fetch_series("DOES_NOT_EXIST", start_date="2020-01-01")


def test_observations_url_format():
    url = boc.observations_url("V39079")
    assert url == "https://www.bankofcanada.ca/valet/observations/V39079/json"


def test_catalog_registers_fvi_term_premium_and_fsi():
    """Guardrail: ensure the FVI-namespace additions (probe 2026-05-11) stay
    wired in the BoC catalog. The series keys ARE in Valet despite an earlier
    catalog note saying 'NOT FOUND'; if a future refactor strips them, this
    test fails so the regression is visible.
    """
    from pipeline.catalog import BOC_VALET_SERIES

    assert "term_premium_10y_acm" in BOC_VALET_SERIES
    assert BOC_VALET_SERIES["term_premium_10y_acm"].series_key == "FVI_TP_GOC_10Y_ACM"
    assert BOC_VALET_SERIES["term_premium_10y_acm"].cadence == "daily"

    assert "term_premium_10y_shadow" in BOC_VALET_SERIES
    assert BOC_VALET_SERIES["term_premium_10y_shadow"].series_key == "FVI_TP_GOC_10Y_SHADOWRATE"

    assert "financial_stress_index_can" in BOC_VALET_SERIES
    assert BOC_VALET_SERIES["financial_stress_index_can"].series_key == "FVI_FSI_CAN"
    assert BOC_VALET_SERIES["financial_stress_index_can"].section == "financial"
    # Probe 2026-05-11 found CFSI is monthly, NOT daily, so it routes through
    # the monthly build (`pipeline.build`), not the daily Financial build.
    assert BOC_VALET_SERIES["financial_stress_index_can"].cadence == "monthly"
