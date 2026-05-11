"""Tests for the site-data builder.

The builder reads pipeline output (CSV + .meta.json) and emits a single
JSON file the Astro side imports at build time. Tests cover:

    - all canon sections appear in the output
    - schema is stable (top-level keys, per-section keys, print shape)
    - per-section construction succeeds with realistic monthly data
    - graceful fallback when a series CSV is missing
    - sampling convention per frequency (monthly -> 24, quarterly -> 8,
      daily -> weekly-sampled tail of 30)
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest

from pipeline.io.site_data import (
    SCHEMA_VERSION,
    SECTION_SLUGS,
    SECTION_CONFIGS,
    _sample_spark,
    build_site_data,
)


# --------------------------------------------------------------------------- #
# Helpers: synthesize the on-disk shape the builder expects.
# --------------------------------------------------------------------------- #

def _write_pair(
    data_root: Path,
    tier: str,
    name: str,
    df: pd.DataFrame,
    meta: dict,
) -> None:
    """Write `<name>.csv` and `<name>.meta.json` under data/<tier>/."""
    tier_dir = data_root / tier
    tier_dir.mkdir(parents=True, exist_ok=True)
    df.to_csv(tier_dir / f"{name}.csv", index=False)
    (tier_dir / f"{name}.meta.json").write_text(json.dumps(meta), encoding="utf-8")


def _monthly_df(values: list[float], start: str = "2024-04-01") -> pd.DataFrame:
    idx = pd.date_range(start=start, periods=len(values), freq="MS")
    return pd.DataFrame({"date": idx, "value": values})


def _daily_df(values: list[float], start: str = "2026-01-02") -> pd.DataFrame:
    idx = pd.bdate_range(start=start, periods=len(values))
    return pd.DataFrame({"date": idx, "value": values})


def _seed_minimal_pipeline(data_root: Path) -> None:
    """Land plausible CSVs for every canon section so a full build succeeds."""
    # inflation -> processed/cpi_all_items_yoy
    _write_pair(
        data_root, "processed", "cpi_all_items_yoy",
        _monthly_df([3.5, 3.3, 3.1, 2.9, 2.7, 2.6, 2.5, 2.4, 2.5, 2.3, 2.4,
                     2.3, 2.4, 2.2, 2.3, 2.1, 2.0, 2.2, 2.1, 2.3, 2.2, 2.3,
                     2.2, 2.32], start="2024-04-01"),
        {
            "name": "cpi_all_items_yoy", "source": "Statistics Canada",
            "source_url": "https://example.invalid/cpi", "source_id": "v41690914",
            "units": "%", "frequency": "monthly",
            "fetched_at": "2026-05-11T00:00:00+00:00",
            "release_date": "2026-04-15",
        },
    )
    # labour -> raw/lfs_ca_unemployment_rate
    _write_pair(
        data_root, "raw", "lfs_ca_unemployment_rate",
        _monthly_df([5.6, 5.7, 5.8, 5.9, 6.0, 6.0, 6.1, 6.2, 6.3, 6.4, 6.5,
                     6.5, 6.6, 6.7, 6.8, 6.7, 6.8, 6.9, 6.8, 6.7, 6.8, 6.7,
                     6.7, 6.9], start="2024-05-01"),
        {
            "name": "lfs_ca_unemployment_rate", "source": "Statistics Canada",
            "source_url": "https://example.invalid/lfs", "source_id": "v2062815",
            "units": "%", "frequency": "monthly",
            "fetched_at": "2026-05-11T00:00:00+00:00",
            "release_date": "2026-05-08",
        },
    )
    # policy -> processed/overnight_rate_target
    _write_pair(
        data_root, "processed", "overnight_rate_target",
        _monthly_df([5.0, 5.0, 4.75, 4.75, 4.5, 4.5, 4.25, 4.0, 4.0, 3.75,
                     3.5, 3.25, 3.0, 3.0, 2.75, 2.75, 2.75, 2.5, 2.5, 2.25,
                     2.25, 2.25, 2.25, 2.25], start="2024-05-01"),
        {
            "name": "overnight_rate_target", "source": "Bank of Canada",
            "source_url": "https://example.invalid/policy", "source_id": "STATIC_ATABLE_V39079",
            "units": "%", "frequency": "monthly",
            "fetched_at": "2026-05-11T00:00:00+00:00",
            "release_date": None,
        },
    )
    # markets -> raw/fxusdcad (daily)
    daily = _daily_df(
        [1.350 + 0.001 * i for i in range(200)],
        start="2025-08-01",
    )
    _write_pair(
        data_root, "raw", "fxusdcad",
        daily,
        {
            "name": "fxusdcad", "source": "Bank of Canada",
            "source_url": "https://example.invalid/fx", "source_id": "FXUSDCAD",
            "units": "CAD per USD", "frequency": "daily",
            "fetched_at": "2026-05-11T00:00:00+00:00",
            "release_date": None,
        },
    )


# --------------------------------------------------------------------------- #
# Schema-level tests
# --------------------------------------------------------------------------- #

def test_section_slugs_match_frontend_canon():
    """The seven canon section slugs are stable; the frontend TypeScript
    `SectionSlug` union must match this tuple exactly."""
    assert SECTION_SLUGS == (
        "gdp", "inflation", "labour", "housing", "policy", "markets", "trade",
    )
    # SECTION_CONFIGS covers every slug.
    for slug in SECTION_SLUGS:
        assert slug in SECTION_CONFIGS
        assert SECTION_CONFIGS[slug].slug == slug


def test_build_site_data_writes_all_seven_sections(tmp_path):
    """A full minimal build emits sections.json with every canon slug."""
    data_root = tmp_path / "data"
    _seed_minimal_pipeline(data_root)

    payload = build_site_data(data_root)

    out_path = data_root / "site" / "sections.json"
    assert out_path.exists()

    loaded = json.loads(out_path.read_text(encoding="utf-8"))
    assert loaded == payload
    assert loaded["schemaVersion"] == SCHEMA_VERSION
    assert "generatedAt" in loaded
    assert set(loaded["sections"].keys()) == set(SECTION_SLUGS)


def test_inflation_section_has_real_value_and_spark(tmp_path):
    """Inflation tile carries a value derived from the latest CSV row,
    a reference rule (BoC target 2%), and a 24-point sparkline."""
    data_root = tmp_path / "data"
    _seed_minimal_pipeline(data_root)
    payload = build_site_data(data_root)

    inflation = payload["sections"]["inflation"]
    assert inflation["slug"] == "inflation"
    assert inflation["chartSeriesKey"] == "cpi-yoy"
    assert inflation["primarySeries"] == "cpi_all_items_yoy"
    assert "error" not in inflation

    # One canonical print, matching the chart series key.
    assert len(inflation["prints"]) == 1
    p = inflation["prints"][0]
    assert p["key"] == "cpi-yoy"
    assert p["indicator"] == "Headline CPI, y/y"
    # Latest value is 2.32 -> formatted to one decimal
    assert p["value"] == "2.3%"
    # Raw scalar preserved
    assert p["valueRaw"] == pytest.approx(2.32, rel=1e-6)
    # Sparkline is 24 points (the seeded series has 24 rows)
    assert isinstance(p["spark"], list)
    assert len(p["spark"]) == 24

    # Reference rule plumbed through
    assert inflation["reference"] == {"value": 2.0, "label": "BoC target 2%"}

    # updatedAt resolves to release_date (2026-04-15) in epoch ms
    assert isinstance(inflation["updatedAt"], int)
    # 2026-04-15 UTC midnight ~ 1776470400000 ms
    expected_ms = int(pd.Timestamp("2026-04-15", tz="UTC").timestamp() * 1000)
    assert inflation["updatedAt"] == expected_ms


def test_policy_section_renders_in_basis_points(tmp_path):
    """Policy delta is rendered in bps, not pp, even though the underlying
    series is in percent. Reference is the neutral midpoint."""
    data_root = tmp_path / "data"
    _seed_minimal_pipeline(data_root)
    payload = build_site_data(data_root)

    policy = payload["sections"]["policy"]
    assert policy["primarySeries"] == "overnight_rate_target"
    p = policy["prints"][0]
    assert p["value"] == "2.25%"
    # Latest 2.25, prior 2.25 -> 0 bps delta -> neutral direction
    assert p["delta"] == "+0 bps"
    assert p["deltaDir"] == "neutral"
    assert policy["reference"] == {"value": 2.75, "label": "Neutral midpoint 2.75%"}


def test_markets_section_weekly_samples_daily_series(tmp_path):
    """FXUSDCAD is daily; the spark should resample weekly with a 30-point cap."""
    data_root = tmp_path / "data"
    _seed_minimal_pipeline(data_root)
    payload = build_site_data(data_root)

    markets = payload["sections"]["markets"]
    p = markets["prints"][0]
    assert p["key"] == "usdcad"
    # 30 weekly observations is the convention; the seed has ~200 business
    # days starting Aug 2025, which yields >30 weeks. Cap honored.
    assert len(p["spark"]) == 30
    # Delta is a percent string with '%' suffix
    assert p["delta"].endswith("%")
    # Value has 3 decimals, no '%' suffix
    assert "%" not in p["value"]
    assert p["value"].count(".") == 1


def test_missing_series_yields_error_sentinel(tmp_path):
    """If a section's primary CSV is missing, the section emits a sentinel
    with prints=[] and an `error` string. The build does NOT raise."""
    data_root = tmp_path / "data"
    # Seed only inflation; gdp/labour/housing/policy/markets/trade missing.
    _write_pair(
        data_root, "processed", "cpi_all_items_yoy",
        _monthly_df([2.5, 2.6, 2.4, 2.5, 2.3, 2.4], start="2025-10-01"),
        {
            "name": "cpi_all_items_yoy", "source": "Statistics Canada",
            "source_url": "https://example.invalid/cpi", "source_id": "v41690914",
            "units": "%", "frequency": "monthly",
            "fetched_at": "2026-05-11T00:00:00+00:00",
            "release_date": None,
        },
    )

    payload = build_site_data(data_root)

    # All 7 sections present; only inflation has real data.
    assert set(payload["sections"].keys()) == set(SECTION_SLUGS)
    inflation = payload["sections"]["inflation"]
    assert "error" not in inflation
    assert len(inflation["prints"]) == 1

    for slug in ("gdp", "labour", "housing", "policy", "markets", "trade"):
        section = payload["sections"][slug]
        assert section["prints"] == [], f"{slug} should have empty prints when series missing"
        assert "error" in section, f"{slug} should carry an error sentinel"
        assert section["updatedAt"] is None


def test_print_shape_matches_frontend_section_print_type(tmp_path):
    """The fields on each print[] entry must be the superset the frontend's
    `SectionPrint` interface accepts: key, indicator, value, delta, deltaDir,
    asOf, spark. Extra fields (valueRaw, priorRaw, asOfISO) are tolerated."""
    data_root = tmp_path / "data"
    _seed_minimal_pipeline(data_root)
    payload = build_site_data(data_root)

    required_keys = {"key", "indicator", "value", "delta", "deltaDir", "asOf", "spark"}
    for slug in SECTION_SLUGS:
        prints = payload["sections"][slug]["prints"]
        if not prints:
            continue
        p = prints[0]
        missing = required_keys - set(p.keys())
        assert not missing, f"{slug} print missing keys: {missing}"
        assert p["deltaDir"] in {"pos", "neg", "neutral"}, f"{slug} bad deltaDir"
        assert isinstance(p["spark"], list)


# --------------------------------------------------------------------------- #
# Sampling tests
# --------------------------------------------------------------------------- #

def test_sample_spark_monthly_returns_last_24():
    df = _monthly_df([float(i) for i in range(60)], start="2020-01-01")
    spark = _sample_spark(df, "monthly")
    assert len(spark) == 24
    # Most-recent 24 values; the 60-point series tail is 36..59
    assert spark[0] == 36.0
    assert spark[-1] == 59.0


def test_sample_spark_quarterly_returns_last_8():
    idx = pd.date_range(start="2020-01-01", periods=20, freq="QS")
    df = pd.DataFrame({"date": idx, "value": [float(i) for i in range(20)]})
    spark = _sample_spark(df, "quarterly")
    assert len(spark) == 8
    assert spark[-1] == 19.0


def test_sample_spark_daily_returns_30_weekly_points():
    daily = _daily_df([float(i) for i in range(400)], start="2025-01-01")
    spark = _sample_spark(daily, "daily")
    assert len(spark) == 30


def test_sample_spark_handles_empty_input():
    assert _sample_spark(pd.DataFrame(columns=["date", "value"]), "monthly") == []
    assert _sample_spark(pd.DataFrame(columns=["date", "value"]), "daily") == []
