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
    SUPPORTING_PRINTS,
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
    # inflation -> processed/cpi_all_items_nsa_yoy (NSA matches StatCan headline)
    _write_pair(
        data_root, "processed", "cpi_all_items_nsa_yoy",
        _monthly_df([3.5, 3.3, 3.1, 2.9, 2.7, 2.6, 2.5, 2.4, 2.5, 2.3, 2.4,
                     2.3, 2.4, 2.2, 2.3, 2.1, 2.0, 2.2, 2.1, 2.3, 2.2, 2.3,
                     2.2, 2.32], start="2024-04-01"),
        {
            "name": "cpi_all_items_nsa_yoy", "source": "Statistics Canada",
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
        "output", "inflation", "labour", "housing", "policy", "markets", "trade",
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
    a reference rule (BoC target 2%), and a 24-point sparkline.

    The primary print is always prints[0]; supporting prints follow
    when SUPPORTING_PRINTS declares them for the section. When the
    sandbox doesn't seed supporting series, they render as TK sentinels
    (available=False) but the primary read still succeeds.
    """
    data_root = tmp_path / "data"
    _seed_minimal_pipeline(data_root)
    payload = build_site_data(data_root)

    inflation = payload["sections"]["inflation"]
    assert inflation["slug"] == "inflation"
    assert inflation["chartSeriesKey"] == "cpi-yoy"
    assert inflation["primarySeries"] == "cpi_all_items_nsa_yoy"
    assert "error" not in inflation

    # Primary print at index 0 always carries the section's anchor series.
    assert len(inflation["prints"]) >= 1
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
    # Delta is a percent string with '%' (may carry ' w/w' suffix for daily series)
    assert "%" in p["delta"]
    # Value has 3 decimals, no '%' suffix
    assert "%" not in p["value"]
    assert p["value"].count(".") == 1


def test_missing_series_yields_error_sentinel(tmp_path):
    """If a section's primary CSV is missing, the section emits a sentinel
    with prints=[] and an `error` string. The build does NOT raise."""
    data_root = tmp_path / "data"
    # Seed only inflation; output/labour/housing/policy/markets/trade missing.
    _write_pair(
        data_root, "processed", "cpi_all_items_nsa_yoy",
        _monthly_df([2.5, 2.6, 2.4, 2.5, 2.3, 2.4], start="2025-10-01"),
        {
            "name": "cpi_all_items_nsa_yoy", "source": "Statistics Canada",
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
    # Primary print is the anchor; supporting prints are TK
    # sentinels in this sandbox (their CSVs aren't seeded).
    assert len(inflation["prints"]) >= 1
    assert inflation["prints"][0]["key"] == "cpi-yoy"

    for slug in ("output", "labour", "housing", "policy", "markets", "trade"):
        section = payload["sections"][slug]
        assert section["prints"] == [], f"{slug} should have empty prints when series missing"
        assert "error" in section, f"{slug} should carry an error sentinel"
        assert section["updatedAt"] is None


def test_delta_dir_encodes_direction_of_change_not_goodness(tmp_path):
    """Canon (design-system.md Section 4): the glyph encodes direction-of-
    change, NOT direction-of-goodness. A rise in inflation, unemployment,
    or USDCAD renders 'pos' because the value went up -- the editorial
    'this is bad news' framing is carried in prose, not in the glyph.

    Regression guard for the 2026-05-11 bug where deltaDir was being
    flipped by `positive_is_good` and producing combinations like
    "[down-triangle] +0.5 pp" on the homepage.
    """
    data_root = tmp_path / "data"
    _seed_minimal_pipeline(data_root)
    payload = build_site_data(data_root)

    # Inflation rose 2.2 -> 2.32 -> +0.1 pp; positive_is_good=False on the
    # catalog. New canon: deltaDir follows the sign, so this is "pos".
    inflation = payload["sections"]["inflation"]["prints"][0]
    assert inflation["delta"].startswith("+")
    assert inflation["deltaDir"] == "pos"

    # Labour: unemployment 6.7 -> 6.9 -> +0.2 pp; positive_is_good=False.
    # Glyph follows the change, so "pos".
    labour = payload["sections"]["labour"]["prints"][0]
    assert labour["delta"].startswith("+")
    assert labour["deltaDir"] == "pos"

    # Markets: USDCAD rose across the daily seed; positive_is_good=False
    # on the catalog. Glyph follows the change, so "pos".
    markets = payload["sections"]["markets"]["prints"][0]
    assert markets["delta"].startswith("+")
    assert markets["deltaDir"] == "pos"

    # Policy: 2.25 -> 2.25 -> 0 bps. Below the half-decimal threshold, so
    # "neutral" regardless of positive_is_good.
    policy = payload["sections"]["policy"]["prints"][0]
    assert policy["deltaDir"] == "neutral"


def test_delta_dir_neutral_for_ambient_series_when_change_below_threshold(tmp_path):
    """A section whose catalog flag is `positive_is_good=None` (housing,
    in v1) used to short-circuit to 'neutral' for ALL prints under the
    old logic. Under canon, the None flag stops mattering for deltaDir;
    only the magnitude of the change does.
    """
    data_root = tmp_path / "data"
    # Seed housing with a clear monthly rise of +0.3 pp on the YoY series.
    _write_pair(
        data_root, "processed", "crea_hpi_canada_yoy",
        _monthly_df(
            [-1.0, -1.5, -2.0, -2.4, -2.9, -3.3, -3.5, -3.6, -3.7, -3.8,
             -3.9, -4.0, -4.1, -4.2, -4.3, -4.4, -4.5, -4.6, -4.7, -4.8,
             -4.9, -5.0, -4.9, -4.6],
            start="2024-04-01",
        ),
        {
            "name": "crea_hpi_canada_yoy", "source": "CREA",
            "source_url": "https://example.invalid/hpi", "source_id": "CREA-HPI-AGGREGATE",
            "units": "%", "frequency": "monthly",
            "fetched_at": "2026-05-11T00:00:00+00:00",
            "release_date": None,
        },
    )
    payload = build_site_data(data_root)
    housing = payload["sections"]["housing"]["prints"][0]
    # -4.9 -> -4.6 is +0.3 pp; well above the 0.05 pp half-decimal threshold.
    assert housing["delta"].startswith("+")
    assert housing["deltaDir"] == "pos"


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


# --------------------------------------------------------------------------- #
# Supporting-print tests
# --------------------------------------------------------------------------- #

def test_supporting_prints_catalog_covers_every_section():
    """SUPPORTING_PRINTS must have an entry (possibly empty) for every canon
    section slug so the loader can iterate without slug-mismatch surprises."""
    for slug in SECTION_SLUGS:
        assert slug in SUPPORTING_PRINTS, f"{slug} missing from SUPPORTING_PRINTS"
        # Every spec's key must be unique within the section to keep the
        # frontend `key`-lookup deterministic.
        keys = [s.key for s in SUPPORTING_PRINTS[slug]]
        assert len(keys) == len(set(keys)), f"{slug}: duplicate supporting print key in {keys}"


def test_supporting_prints_tk_sentinel_when_source_missing(tmp_path):
    """If a supporting print's underlying CSV is not on disk, the print is
    still emitted as a TK sentinel with `available: False`. This keeps the
    homepage tile layout (one row per canon key) stable across pipeline runs.
    """
    data_root = tmp_path / "data"
    _seed_minimal_pipeline(data_root)
    payload = build_site_data(data_root)

    # inflation: cpi-yoy primary is real; core-trim/median/breadth supporting
    # series were not seeded -> TK sentinels expected.
    inflation = payload["sections"]["inflation"]
    keys = [p["key"] for p in inflation["prints"]]
    assert keys[0] == "cpi-yoy"
    assert "core-trim-yoy" in keys
    assert "core-median-yoy" in keys
    assert "cpi-breadth-gt3" in keys

    by_key = {p["key"]: p for p in inflation["prints"]}
    # Primary is real
    assert by_key["cpi-yoy"]["value"] != "TK"
    assert by_key["cpi-yoy"].get("available", True) is True
    # Supporting (no seed) are TK
    for k in ("core-trim-yoy", "core-median-yoy", "cpi-breadth-gt3"):
        assert by_key[k]["value"] == "TK"
        assert by_key[k]["delta"] == "TK"
        assert by_key[k]["available"] is False
        assert by_key[k]["spark"] == []


def test_supporting_print_yoy_transform(tmp_path):
    """A supporting print with `transform='yoy'` computes year-over-year %
    on a raw monthly level and renders the latest value + delta.

    Uses labour's `agg-hours-yoy` spec which reads `aggregate_hours` raw
    and applies pct_change(12) * 100.
    """
    data_root = tmp_path / "data"
    _seed_minimal_pipeline(data_root)
    # Seed 18 months of aggregate_hours starting Nov 2024 (so latest is
    # Apr 2026, with a Y/Y comparison vs Apr 2025).
    levels = list(range(100, 118))  # values 100..117 across 18 months
    _write_pair(
        data_root, "raw", "aggregate_hours",
        _monthly_df([float(v) for v in levels], start="2024-11-01"),
        {
            "name": "aggregate_hours", "source": "Statistics Canada",
            "source_url": "https://example.invalid/hours",
            "source_id": "v4391505",
            "units": "Thousands of hours", "frequency": "monthly",
            "fetched_at": "2026-05-11T00:00:00+00:00",
            "release_date": None,
        },
    )
    payload = build_site_data(data_root)
    labour = payload["sections"]["labour"]
    by_key = {p["key"]: p for p in labour["prints"]}
    assert "agg-hours-yoy" in by_key
    p = by_key["agg-hours-yoy"]
    assert p["available"] is True
    # Apr 2025 = 105, Apr 2026 = 117 -> (117/105 - 1) * 100 = 11.43%
    assert p["valueRaw"] == pytest.approx(11.428571, rel=1e-3)
    assert p["value"].endswith("%")
    assert p["deltaDir"] in {"pos", "neg", "neutral"}


def test_supporting_print_3m_ma_transform(tmp_path):
    """A supporting print with `transform='3m_ma'` smooths the level series."""
    data_root = tmp_path / "data"
    _seed_minimal_pipeline(data_root)
    # Seed housing prices (primary) and housing_starts (raw).
    _write_pair(
        data_root, "processed", "crea_hpi_canada_yoy",
        _monthly_df([-5.0, -4.5, -4.0, -3.5, -3.0, -2.5, -2.0, -1.5, -1.0,
                     -0.5, 0.0, 0.5, 0.7, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4,
                     1.5, 1.6, 1.7, 1.8, 1.9],
                    start="2024-04-01"),
        {
            "name": "crea_hpi_canada_yoy", "source": "CREA",
            "source_url": "https://example.invalid",
            "source_id": "CREA-HPI-AGGREGATE",
            "units": "%", "frequency": "monthly",
            "fetched_at": "2026-05-11T00:00:00+00:00",
            "release_date": None,
        },
    )
    starts = [240.0, 245.0, 250.0, 248.0, 246.0, 244.0]
    _write_pair(
        data_root, "raw", "housing_starts",
        _monthly_df(starts, start="2025-11-01"),
        {
            "name": "housing_starts", "source": "Statistics Canada",
            "source_url": "https://example.invalid",
            "source_id": "v52300157",
            "units": "Units, SAAR", "frequency": "monthly",
            "fetched_at": "2026-05-11T00:00:00+00:00",
            "release_date": None,
        },
    )
    payload = build_site_data(data_root)
    housing = payload["sections"]["housing"]
    by_key = {p["key"]: p for p in housing["prints"]}
    p = by_key["housing-starts-3mma"]
    assert p["available"] is True
    # 3M MA of last three (Feb, Mar, Apr) = (248+246+244)/3 = 246.0
    assert p["valueRaw"] == pytest.approx(246.0, rel=1e-6)
    assert p["value"].endswith("k")


def test_supporting_print_spread_bps(tmp_path):
    """A spread_bps transform yields a basis-point value derived as
    (primary - secondary) * 100 in the SAME percent->bps direction the
    delta formatter expects, so no double-conversion happens."""
    data_root = tmp_path / "data"
    _seed_minimal_pipeline(data_root)
    # Land 30 business days of yield_2yr and us_2yr.
    daily_dates = pd.bdate_range(start="2026-04-01", periods=30)
    _write_pair(
        data_root, "raw", "yield_2yr",
        pd.DataFrame({"date": daily_dates, "value": [3.00 + 0.01 * i for i in range(30)]}),
        {
            "name": "yield_2yr", "source": "Bank of Canada",
            "source_url": "https://example.invalid", "source_id": "BD.CDN.2YR.DQ.YLD",
            "units": "%", "frequency": "daily",
            "fetched_at": "2026-05-11T00:00:00+00:00",
            "release_date": None,
        },
    )
    _write_pair(
        data_root, "raw", "us_2yr",
        pd.DataFrame({"date": daily_dates, "value": [4.00 + 0.005 * i for i in range(30)]}),
        {
            "name": "us_2yr", "source": "FRED",
            "source_url": "https://example.invalid", "source_id": "DGS2",
            "units": "%", "frequency": "daily",
            "fetched_at": "2026-05-11T00:00:00+00:00",
            "release_date": None,
        },
    )
    payload = build_site_data(data_root)
    policy = payload["sections"]["policy"]
    by_key = {p["key"]: p for p in policy["prints"]}
    p = by_key["boc-fed-spread"]
    assert p["available"] is True
    # day 29 (last): CAD 3.29, US 4.145 -> spread = -0.855% = -85.5 bps
    assert p["valueRaw"] == pytest.approx(-85.5, rel=1e-2)
    # Value renders in bps with " bps" label
    assert p["value"].endswith(" bps")
    # Delta is the bps step day-over-day: CAD +1bp, US +0.5bp -> spread +0.5bp.
    # The renderer should print "+1 bps" or "+0 bps" given decimals=0.
    assert p["delta"].endswith(" bps")


def test_supporting_print_partner_share(tmp_path):
    """A partner_share transform divides the primary series by the secondary
    and multiplies by 100, yielding a percent share."""
    data_root = tmp_path / "data"
    _seed_minimal_pipeline(data_root)
    # Trade balance (primary) + US exports + total exports.
    _write_pair(
        data_root, "processed", "trade_balance_total_3m_ma",
        _monthly_df([-1000.0, -1100.0, -1200.0, -2000.0, -2100.0, -2200.0],
                    start="2025-10-01"),
        {
            "name": "trade_balance_total_3m_ma", "source": "Statistics Canada",
            "source_url": "https://example.invalid", "source_id": "v87008984",
            "units": "CAD millions", "frequency": "monthly",
            "fetched_at": "2026-05-11T00:00:00+00:00",
            "release_date": None,
        },
    )
    _write_pair(
        data_root, "raw", "trade_exports_us",
        _monthly_df([40000.0, 41000.0, 42000.0], start="2026-01-01"),
        {
            "name": "trade_exports_us", "source": "Statistics Canada",
            "source_url": "https://example.invalid", "source_id": "v87008898",
            "units": "CAD millions, SA", "frequency": "monthly",
            "fetched_at": "2026-05-11T00:00:00+00:00",
            "release_date": None,
        },
    )
    _write_pair(
        data_root, "raw", "trade_exports_total",
        _monthly_df([55000.0, 56000.0, 60000.0], start="2026-01-01"),
        {
            "name": "trade_exports_total", "source": "Statistics Canada",
            "source_url": "https://example.invalid", "source_id": "v87008897",
            "units": "CAD millions, SA", "frequency": "monthly",
            "fetched_at": "2026-05-11T00:00:00+00:00",
            "release_date": None,
        },
    )
    payload = build_site_data(data_root)
    trade = payload["sections"]["trade"]
    by_key = {p["key"]: p for p in trade["prints"]}
    p = by_key["us-partner-share"]
    assert p["available"] is True
    # Last: 42000 / 60000 = 0.7 = 70%
    assert p["valueRaw"] == pytest.approx(70.0, rel=1e-3)
    assert p["value"] == "70.0%"


def test_supporting_print_fy_ytd_yoy_vs_prior_fy_at_same_month(tmp_path):
    """The Policy panel's federal-budget-balance row reads from the FY-YTD
    cumulative series and compares the latest point to the PRIOR FY's YTD
    through the SAME month (not the prior calendar month, which would just
    re-expose the noisy single-month balance the swap was meant to suppress).

    This is the DoF Fiscal Monitor headline framing. Seed two full Canadian
    fiscal years of cumulative-YTD points and assert the latest's delta is
    against the 12-month-lag observation.
    """
    data_root = tmp_path / "data"
    _seed_minimal_pipeline(data_root)
    # Seed the cumulative FY-YTD series: 12 months of prior FY (Apr 2024 to
    # Mar 2025, FY25, finalizes at -43_154) + 11 months of current FY (Apr
    # 2025 to Feb 2026, FY26 YTD at -25_550 through Feb).
    # Using exactly the on-disk values so the test asserts the same
    # production numbers reported on the tile.
    fy_ytd_values = [
        -4994.0, -3822.0, -2883.0, -7295.0, -9841.0, -13010.0, -14503.0,
        -22716.0, -21714.0, -26848.0, -19274.0, -43154.0,
        -7711.0, -9905.0, -6276.0, -7788.0, -11068.0, -16091.0, -18369.0,
        -26386.0, -26141.0, -31209.0, -25550.0,
    ]
    _write_pair(
        data_root, "processed", "federal_budget_ytd",
        _monthly_df(fy_ytd_values, start="2024-04-01"),
        {
            "name": "federal_budget_ytd",
            "source": "Department of Finance Canada -- Fiscal Monitor (derived)",
            "source_url": "https://example.invalid/fiscal-monitor",
            "source_id": "federal_budget_balance:cumsum-by-fy",
            "units": "CAD millions", "frequency": "monthly",
            "fetched_at": "2026-05-11T00:00:00+00:00",
            "release_date": None,
        },
    )
    payload = build_site_data(data_root)
    policy = payload["sections"]["policy"]
    by_key = {p["key"]: p for p in policy["prints"]}
    assert "federal-budget-balance" in by_key
    p = by_key["federal-budget-balance"]
    assert p["available"] is True
    # Latest: FY26 YTD through Feb 2026 = -25,550 CAD millions -> "-$25.6B"
    assert p["valueRaw"] == pytest.approx(-25550.0, rel=1e-6)
    assert p["value"] == "-$25.6B"
    # Prior: FY25 YTD through Feb 2025 = -19,274 (NOT the Jan 2026 point
    # which is -31,209). This is the central assertion: comparator is
    # 12 months back, not iloc[-2].
    assert p["priorRaw"] == pytest.approx(-19274.0, rel=1e-6)
    # Delta = -25,550 - (-19,274) = -6,276 millions -> "-$6.3B"
    assert p["delta"] == "-$6.3B"
    # Sign of change (deficit widened) -> 'neg'
    assert p["deltaDir"] == "neg"
    # as_of_format='fy-ytd-month' renders "FYTD Feb 26"
    assert p["asOf"] == "FYTD Feb 26"


def test_supporting_print_fy_ytd_falls_back_when_prior_fy_missing(tmp_path):
    """When the FY-YTD series only carries the current FY (12-month-lag
    point not on disk), the print should still render -- it falls back to
    iloc[-2] for the comparator rather than dropping the row.

    Editorial-side requirement: never sink the row layout because of
    insufficient history; v1 may legitimately ship before the full prior-
    FY landed on disk.
    """
    data_root = tmp_path / "data"
    _seed_minimal_pipeline(data_root)
    # Only 3 months of current-FY YTD, no prior-FY history.
    _write_pair(
        data_root, "processed", "federal_budget_ytd",
        _monthly_df([-7711.0, -9905.0, -6276.0], start="2025-04-01"),
        {
            "name": "federal_budget_ytd",
            "source": "Department of Finance Canada -- Fiscal Monitor (derived)",
            "source_url": "https://example.invalid/fiscal-monitor",
            "source_id": "federal_budget_balance:cumsum-by-fy",
            "units": "CAD millions", "frequency": "monthly",
            "fetched_at": "2026-05-11T00:00:00+00:00",
            "release_date": None,
        },
    )
    payload = build_site_data(data_root)
    policy = payload["sections"]["policy"]
    by_key = {p["key"]: p for p in policy["prints"]}
    p = by_key["federal-budget-balance"]
    assert p["available"] is True
    # No 12-month-lag observation; comparator falls back to iloc[-2] (May).
    assert p["priorRaw"] == pytest.approx(-9905.0, rel=1e-6)
    assert p["valueRaw"] == pytest.approx(-6276.0, rel=1e-6)


def test_format_as_of_fy_ytd_month_label_boundary(tmp_path):
    """The 'fy-ytd-month' label assigns the FY-END year as the FY tag.

    Canadian federal FY = April-March. Feb 2026 belongs to FY26 (the FY
    that ends March 2026). March 2025 belongs to FY25. April 2025 starts
    FY26. Regression guard for the boundary handling.
    """
    from pipeline.io.site_data import _format_as_of
    assert _format_as_of(pd.Timestamp("2026-02-28"), "fy-ytd-month") == "FYTD Feb 26"
    assert _format_as_of(pd.Timestamp("2025-03-31"), "fy-ytd-month") == "FYTD Mar 25"
    assert _format_as_of(pd.Timestamp("2025-04-30"), "fy-ytd-month") == "FYTD Apr 26"
    assert _format_as_of(pd.Timestamp("2024-12-31"), "fy-ytd-month") == "FYTD Dec 25"


def test_supporting_print_primary_always_first(tmp_path):
    """The primary print is always prints[0]; supporting prints follow.
    Frontend relies on prints[0] being the chartSeriesKey-matching row."""
    data_root = tmp_path / "data"
    _seed_minimal_pipeline(data_root)
    payload = build_site_data(data_root)
    for slug in SECTION_SLUGS:
        section = payload["sections"][slug]
        prints = section.get("prints", [])
        if not prints:
            continue
        cfg = SECTION_CONFIGS[slug]
        assert prints[0]["key"] == cfg.print_key, \
            f"{slug}: first print should be the primary {cfg.print_key}"


# --------------------------------------------------------------------------- #
# Canonical formatter tests (pipeline.io.format)
#
# Round-trip raw -> formatted for each kind, plus character-cap assertions.
# Mirrors the rule set chart-builder enforces in src/components/charts/_shared/
# format.ts -- both implementations must agree on the same outputs.
# --------------------------------------------------------------------------- #

from pipeline.io.format import (
    DELTA_CAP,
    HEADLINE_CAP,
    TICK_CAP,
    fmt_delta,
    fmt_tick,
    fmt_value,
)


def test_fmt_value_percent():
    assert fmt_value(2.3241590214, kind="percent") == "2.3%"
    assert fmt_value(6.9, kind="percent") == "6.9%"
    assert fmt_value(-4.595336, kind="percent") == "-4.6%"
    # Zero
    assert fmt_value(0.0, kind="percent") == "0.0%"


def test_fmt_value_rate_level_uses_two_decimals_when_small():
    assert fmt_value(2.25, kind="rate_level", decimals=2) == "2.25%"
    # >= 10 collapses to 1 decimal under the default
    assert fmt_value(12.55, kind="rate_level") == "12.6%"


def test_fmt_value_basis_points():
    # Signed, integer, " bps" suffix.
    assert fmt_value(25.0, kind="basis_points") == "+25 bps"
    assert fmt_value(-100.0, kind="basis_points") == "-100 bps"
    # +0 still signed by canon (caller decides neutrality glyph separately).
    assert fmt_value(0.0, kind="basis_points") == "+0 bps"


def test_fmt_value_currency_cad_scales_to_billions():
    # Federal budget balance, +5659 CAD millions -> "$5.7B".
    assert fmt_value(5659.0, kind="currency_cad") == "$5.7B"
    # Trade balance, -2175.6 millions -> "-$2.2B".
    assert fmt_value(-2175.6, kind="currency_cad") == "-$2.2B"
    # Sub-billion stays in millions per canon (e.g. -706 -> "-$706M").
    assert fmt_value(-706.0, kind="currency_cad") == "-$706M"


def test_fmt_value_fx_three_decimals_for_unit_range():
    assert fmt_value(1.3686, kind="fx") == "1.369"
    assert fmt_value(1.3613, kind="fx") == "1.361"


def test_fmt_value_index_level_scales_at_ten_thousand():
    # TSX Composite ~34,077.76 -> "34.1k" (the brief's headline offender fix).
    assert fmt_value(34077.76, kind="index_level") == "34.1k"
    # Sub-thousand keeps decimals.
    assert fmt_value(109.76, kind="index_level") == "109.8"
    # Comma-grouped in the 1000-9999 band.
    assert fmt_value(5_234.0, kind="index_level") == "5,234"


def test_fmt_value_count_scales_persons():
    # EI beneficiaries 1.16M-style.
    assert fmt_value(1_160_000.0, kind="count") == "1.2M"
    assert fmt_value(455_000.0, kind="count") == "455k"
    # Below 1k stays integer.
    assert fmt_value(240.0, kind="count") == "240"


def test_fmt_value_count_thousands_treats_input_as_thousands():
    # Housing starts on disk: 241.3 means 241,272 units SAAR -> "241k".
    assert fmt_value(241.27, kind="count_thousands") == "241k"
    # When the thousands-scaled value crosses 1000, escalate to M.
    assert fmt_value(1500.0, kind="count_thousands") == "1.5M"


def test_fmt_value_ratio_multiplies_by_one_hundred():
    # BoC housing affordability decimal 0.43 -> "43.0%".
    assert fmt_value(0.43, kind="ratio") == "43.0%"


def test_fmt_value_returns_tk_for_none_or_nan():
    assert fmt_value(None, kind="percent") == "TK"
    assert fmt_value(float("nan"), kind="percent") == "TK"


def test_fmt_value_respects_headline_cap_of_eight_chars():
    """Every kind, for plausible upper-end inputs, must fit within 8 chars."""
    cases: list[tuple[str, float, str]] = [
        ("percent", 99.9, ""),
        ("percent", -99.9, ""),
        ("percent_pp", 99.9, ""),
        # Plausible policy-move scale; a single 999 bp move is the editorial
        # upper bound (a >9.99 percentage-point step is implausible in
        # practice and would warrant a special break-glass renderer anyway).
        ("basis_points", -999.0, ""),
        ("rate_level", 12.45, ""),
        ("currency_cad", 9876.5, ""),   # -> "$9.9B"
        ("currency_cad", -9876.5, ""),
        ("fx", 1.3686, ""),
        ("index_level", 34_077.76, ""),  # -> "34.1k"
        ("index_level", 999_999.0, ""),  # -> "1000.0k" -> 7 chars
        ("count", 1_160_000.0, ""),
        ("count_thousands", 241.27, ""),
        ("ratio", 0.43, ""),
    ]
    for kind, value, _ in cases:
        out = fmt_value(value, kind=kind)
        assert len(out) <= HEADLINE_CAP, f"fmt_value({value!r}, {kind}) -> {out!r} > {HEADLINE_CAP}"


def test_fmt_delta_signed_with_unit_suffix():
    assert fmt_delta(0.5, kind="percent_pp") == "+0.5 pp"
    assert fmt_delta(-0.2, kind="percent_pp") == "-0.2 pp"
    assert fmt_delta(25.0, kind="basis_points") == "+25 bps"
    assert fmt_delta(-100.0, kind="basis_points") == "-100 bps"
    assert fmt_delta(10727.0, kind="currency_cad") == "+$10.7B"
    assert fmt_delta(900.0, kind="currency_cad") == "+$900M"


def test_fmt_delta_returns_empty_for_none_or_nan():
    assert fmt_delta(None, kind="percent_pp") == ""
    assert fmt_delta(float("nan"), kind="percent_pp") == ""


def test_fmt_delta_respects_delta_cap_of_eight_chars():
    """Plausible upper-end deltas must fit within DELTA_CAP."""
    cases: list[tuple[str, float]] = [
        ("percent", 99.9),
        ("percent_pp", -9.9),
        ("basis_points", 999.0),
        ("basis_points", -999.0),
        ("currency_cad", -1234.0),  # -> "-$1.2B" 6 chars
        ("currency_cad", 10727.0),  # -> "+$10.7B" 7 chars
        ("count", -1_160_000.0),
        ("count_thousands", -150.0),
        ("ratio", 0.05),
        ("fx", -0.0042),
    ]
    for kind, value in cases:
        out = fmt_delta(value, kind=kind)
        assert len(out) <= DELTA_CAP, f"fmt_delta({value!r}, {kind}) -> {out!r} > {DELTA_CAP}"


def test_fmt_tick_bare_number_unless_top():
    # Mid-axis tick (no unit).
    assert fmt_tick(2.3, kind="percent") == "2.3"
    # Topmost tick carries the unit per canon.
    assert fmt_tick(2.3, kind="percent", is_top=True) == "2.3%"
    # bps tick suppresses suffix off-top.
    assert fmt_tick(25.0, kind="basis_points") == "25"
    assert fmt_tick(25.0, kind="basis_points", is_top=True) == "25 bps"


def test_fmt_tick_respects_tick_cap_of_six_chars():
    """Tick labels for plausible inputs must fit TICK_CAP."""
    cases: list[tuple[str, float, bool]] = [
        ("percent", 12.4, False),
        ("percent", 12.4, True),
        ("rate_level", 5.25, False),
        ("rate_level", 5.25, True),
        ("currency_cad", 9.8, False),   # "$10M" -> 4 chars after strip
        ("currency_cad", 5_659.0, True),  # "$5.7B"
        ("index_level", 34_078.0, False),  # "34.1k"
        ("fx", 1.3686, False),
        ("count_thousands", 241.0, False),
    ]
    for kind, value, top in cases:
        out = fmt_tick(value, kind=kind, is_top=top)
        assert len(out) <= TICK_CAP, \
            f"fmt_tick({value!r}, {kind}, is_top={top}) -> {out!r} > {TICK_CAP}"


def test_formatter_canonical_offender_table_now_fits():
    """The five long-string offenders in sections.json before this change,
    expressed as a tabular round-trip:

      raw value              kind             -> new formatted string

    TSX 34,077.76 (was "34,078" 6 chars)  -> "34.1k" 5 chars (index_level)
    Trade balance -2175.6M millions       -> "-$2.2B" 6 chars (currency_cad)
    Federal budget +5659.0 millions       -> "$5.7B"  5 chars (currency_cad)
    BoC-Fed spread -98 bps                -> "-98 bps" 7 chars (basis_points)
    EI beneficiaries 1,160,000 persons    -> "1.2M"   4 chars (count)
    """
    assert fmt_value(34_077.76, kind="index_level") == "34.1k"
    assert fmt_value(-2175.6, kind="currency_cad") == "-$2.2B"
    assert fmt_value(5659.0, kind="currency_cad") == "$5.7B"
    assert fmt_value(-98.0, kind="basis_points") == "-98 bps"
    assert fmt_value(1_160_000.0, kind="count") == "1.2M"
    # And the related deltas:
    assert fmt_delta(10727.0, kind="currency_cad") == "+$10.7B"
    assert fmt_delta(900.0, kind="currency_cad") == "+$900M"


def test_sections_json_strings_now_within_caps(tmp_path):
    """After regenerating sections.json, every emitted value/delta string
    fits its respective character cap. Guards against editorial drift."""
    data_root = tmp_path / "data"
    _seed_minimal_pipeline(data_root)
    payload = build_site_data(data_root)
    for slug, section in payload["sections"].items():
        for p in section.get("prints", []):
            value = p.get("value")
            delta = p.get("delta")
            if value and value != "TK":
                assert len(value) <= HEADLINE_CAP, \
                    f"{slug}/{p.get('key')}: value {value!r} exceeds {HEADLINE_CAP} chars"
            if delta and delta != "TK":
                assert len(delta) <= DELTA_CAP, \
                    f"{slug}/{p.get('key')}: delta {delta!r} exceeds {DELTA_CAP} chars"
