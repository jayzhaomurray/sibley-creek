"""Regression tests for panel_data integrity gates."""

from __future__ import annotations

import math
from datetime import date
from pathlib import Path

import pandas as pd

from pipeline.io.panel_data import _business_days_since, _df_to_records, validate_panel_data_file


FIXTURES = Path(__file__).parent / "fixtures" / "panel_integrity"


def test_df_to_records_never_emits_nan_or_infinity():
    records = _df_to_records(
        pd.DataFrame(
            {
                "date": pd.to_datetime(["2026-01-01", "2026-01-02"]),
                "value": [math.inf, math.nan],
            }
        )
    )

    assert records == [
        {"date": "2026-01-01", "value": None},
        {"date": "2026-01-02", "value": None},
    ]


def test_validate_panel_data_fails_stale_daily_market_series():
    violations = validate_panel_data_file(FIXTURES / "stale_daily.json", today=date(2026, 6, 2))

    assert violations
    assert "yield_2yr" in violations[0]
    assert "business days old" in violations[0]


def test_business_day_age_skips_market_holidays():
    assert _business_days_since(date(2026, 5, 22), date(2026, 5, 27)) == 1


def test_validate_panel_data_allows_slow_reference_period_series():
    assert validate_panel_data_file(FIXTURES / "slow_monthly.json", today=date(2026, 6, 2)) == []


def test_validate_panel_data_fails_trailing_null():
    violations = validate_panel_data_file(FIXTURES / "trailing_null.json", today=date(2026, 6, 2))

    assert violations
    assert "most recent data point has null value" in violations[0]
