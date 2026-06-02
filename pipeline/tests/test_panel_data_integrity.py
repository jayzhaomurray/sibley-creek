"""Regression tests for panel_data integrity gates."""

from __future__ import annotations

import json
import math
from datetime import date
from pathlib import Path

import pandas as pd

from pipeline.io.panel_data import (
    FRESHNESS_THRESHOLDS_DAYS,
    SERIES_STALENESS_OVERRIDES,
    STALENESS_FAIL_SERIES,
    _business_days_since,
    _df_to_records,
    validate_panel_data_file,
)


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


# ---------------------------------------------------------------------------
# Per-series staleness override tests
#
# goc_ust_spread_2y is in STALENESS_FAIL_SERIES (fail-closed on staleness) AND
# has SERIES_STALENESS_OVERRIDES["goc_ust_spread_2y"] = 10 (business days).
# The default daily threshold is FRESHNESS_THRESHOLDS_DAYS["daily"] = 3.
#
# Without the override, a 7-business-day-old series would fail (7 > 3).
# With the override, it must pass (7 <= 10).
# A 12-business-day-old series must fail under either threshold (12 > 10).
#
# today=date(2026, 6, 2) is used throughout.
# 7 business days before 2026-06-02 = 2026-05-22 (skipping May 18 Victoria Day
#   and weekends): Jun2, Jun1=Sun skip, May29, 28, 27, 26, 23, 22 -> asOf May 22
# 12 business days before 2026-06-02 = 2026-05-15 (same holiday calendar)
# ---------------------------------------------------------------------------

_TODAY = date(2026, 6, 2)

# Confirm the constants this test relies on are still what we think they are.
# If someone accidentally changes the override or the default, this assertion
# will fail loudly before the behavioural tests even run.
def test_staleness_override_constants_are_in_expected_state():
    """Canary: override=10, default-daily=3, series in STALENESS_FAIL_SERIES."""
    assert "goc_ust_spread_2y" in STALENESS_FAIL_SERIES, (
        "goc_ust_spread_2y must be in STALENESS_FAIL_SERIES for the override test to be meaningful"
    )
    assert SERIES_STALENESS_OVERRIDES.get("goc_ust_spread_2y") == 10, (
        "goc_ust_spread_2y override must be 10 business days"
    )
    assert FRESHNESS_THRESHOLDS_DAYS["daily"] == 3, (
        "Default daily threshold must be 3; update this test if the default changes"
    )


def _make_spread_fixture(tmp_path: Path, as_of_iso: str) -> Path:
    """Write a minimal panel_data fixture containing goc_ust_spread_2y."""
    payload = {
        "section": "markets",
        "panels": {
            "panel-spread": {
                "primary": {
                    "key": "goc_ust_spread_2y",
                    "label": "GoC-UST 2y spread",
                    "frequency": "daily",
                    "asOfISO": as_of_iso,
                    "data": [{"date": as_of_iso, "value": -0.5}],
                },
                "secondary": None,
                "tertiary": None,
                "extras": [],
            }
        },
    }
    path = tmp_path / "spread_fixture.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_staleness_override_applied_for_fail_series(tmp_path: Path):
    """goc_ust_spread_2y at 4 business days old must NOT violate when override=10.

    If the override lookup were dropped and the default daily threshold (3) were
    used instead, this test would fail because 4 > 3.

    Date arithmetic verified via _business_days_since:
      2026-05-26 to 2026-06-02 = 4 business days
      (skips: May 31/Jun 1 weekend; Jun 2 is today-exclusive)
    """
    as_of = "2026-05-26"
    age = _business_days_since(date.fromisoformat(as_of), _TODAY)
    assert age == 4, f"Fixture date calculation error: expected 4 bd, got {age}"

    path = _make_spread_fixture(tmp_path, as_of)
    violations = validate_panel_data_file(path, today=_TODAY)

    spread_violations = [v for v in violations if "goc_ust_spread_2y" in v]
    assert spread_violations == [], (
        f"goc_ust_spread_2y at {age} business days old should NOT fail with override=10; "
        f"got: {spread_violations}\n"
        "This likely means the per-series staleness override is not being applied — "
        "the gate is using the default daily threshold (3) instead."
    )


def test_staleness_override_still_fails_when_exceeded(tmp_path: Path):
    """goc_ust_spread_2y at 11 business days old must fail even with override=10.

    Date arithmetic verified via _business_days_since:
      2026-05-13 to 2026-06-02 = 11 business days
      (skips: May 18 Victoria Day, weekends)
    """
    as_of = "2026-05-13"
    age = _business_days_since(date.fromisoformat(as_of), _TODAY)
    assert age == 11, f"Fixture date calculation error: expected 11 bd, got {age}"

    path = _make_spread_fixture(tmp_path, as_of)
    violations = validate_panel_data_file(path, today=_TODAY)

    spread_violations = [v for v in violations if "goc_ust_spread_2y" in v]
    assert spread_violations, (
        f"goc_ust_spread_2y at {age} business days old MUST fail (override threshold=10); "
        "got no violations"
    )
