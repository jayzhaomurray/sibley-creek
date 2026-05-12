"""Tests for derivations wired into pipeline.build.

These exercise the IO loop end-to-end: seed a raw CSV + meta.json at the
location the derivation expects, run the derivation function, assert the
processed output CSV and meta land with the expected name/units/transform tag.

The math itself is exhaustively covered by tests/test_transform.py; here we
only assert the wiring (correct input read, correct output filename, correct
meta fields) so a future rename of either the raw slug or the processed slug
fails loudly.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest

from pipeline.io import SeriesMeta, write_series


def _seed_raw(data_root: Path, name: str, values: list[float], start: str = "2024-01-01") -> None:
    """Drop a raw monthly CSV + .meta.json under data/raw/."""
    idx = pd.date_range(start=start, periods=len(values), freq="MS")
    df = pd.DataFrame({"date": idx, "value": values})
    meta = SeriesMeta(
        name=name,
        source="Statistics Canada Web Data Service",
        source_url="https://example.invalid/raw",
        source_id="v00000000",
        units="C$ trillions, chained 2017",
        frequency="monthly",
    )
    write_series(df, meta, data_root / "raw")


def test_derive_gdp_views_writes_processed_yoy(tmp_path, monkeypatch):
    """`derive_gdp_views()` reads data/raw/gdp_monthly and writes
    data/processed/gdp_monthly_yoy.csv with the expected y/y values and a
    meta.json carrying units="%", frequency="monthly", and the canonical
    transform tag.
    """
    data_root = tmp_path / "data"
    # 24 months of 2% YoY growth: every value = prior * 1.02^(1/12)... but
    # easier to assert a flat ratio: 100 for 12 months, then 102 for 12 months
    # -> Y/Y at month 13 onward is +2.0%.
    _seed_raw(data_root, "gdp_monthly", [100.0] * 12 + [102.0] * 12, start="2024-01-01")

    # Repoint build.py's data-tier constants at the tmp_path tree.
    from pipeline import build as build_mod

    monkeypatch.setattr(build_mod, "DATA_RAW", data_root / "raw")
    monkeypatch.setattr(build_mod, "DATA_PROCESSED", data_root / "processed")

    build_mod.derive_gdp_views()

    out_csv = data_root / "processed" / "gdp_monthly_yoy.csv"
    out_meta = data_root / "processed" / "gdp_monthly_yoy.meta.json"
    assert out_csv.exists()
    assert out_meta.exists()

    out_df = pd.read_csv(out_csv, parse_dates=["date"])
    # The first 12 rows have no Y/Y comparator; headline_yoy drops NaN.
    # So we expect rows 13..24, all reading +2.0%.
    assert len(out_df) == 12
    assert all(abs(v - 2.0) < 1e-9 for v in out_df["value"])

    out_meta_dict = json.loads(out_meta.read_text(encoding="utf-8"))
    assert out_meta_dict["name"] == "gdp_monthly_yoy"
    assert out_meta_dict["units"] == "%"
    assert out_meta_dict["frequency"] == "monthly"
    assert out_meta_dict["transform"] == "yoy_pct(periods_per_year=12)"
    # Source provenance carries through from the StatCan catalog.
    assert "statcan.gc.ca" in out_meta_dict["source_url"]
    assert out_meta_dict["source_id"].startswith("v")


def _seed_quarterly_raw(data_root: Path, name: str, values: list[float], start: str = "2020-01-01") -> None:
    """Drop a raw quarterly CSV + .meta.json under data/raw/."""
    idx = pd.date_range(start=start, periods=len(values), freq="QS")
    df = pd.DataFrame({"date": idx, "value": values})
    meta = SeriesMeta(
        name=name,
        source="Statistics Canada Web Data Service",
        source_url="https://example.invalid/raw",
        source_id="v00000000",
        units="Index, 2017=100",
        frequency="quarterly",
    )
    write_series(df, meta, data_root / "raw")


def test_derive_terms_of_trade_writes_ratio_and_yoy(tmp_path, monkeypatch):
    """`derive_terms_of_trade()` reads tot_exports_ipi and tot_imports_ipi and
    writes data/processed/terms_of_trade.csv (ratio x100) and the Y/Y companion.
    """
    data_root = tmp_path / "data"
    # 8 quarters: exports IPI flat at 130, imports IPI flat at 125 -> ToT = 104.0
    _seed_quarterly_raw(data_root, "tot_exports_ipi", [130.0] * 8, start="2024-01-01")
    _seed_quarterly_raw(data_root, "tot_imports_ipi", [125.0] * 8, start="2024-01-01")

    from pipeline import build as build_mod

    monkeypatch.setattr(build_mod, "DATA_RAW", data_root / "raw")
    monkeypatch.setattr(build_mod, "DATA_PROCESSED", data_root / "processed")

    build_mod.derive_terms_of_trade()

    out_csv = data_root / "processed" / "terms_of_trade.csv"
    out_meta = data_root / "processed" / "terms_of_trade.meta.json"
    out_yoy_csv = data_root / "processed" / "terms_of_trade_yoy.csv"
    assert out_csv.exists()
    assert out_meta.exists()
    assert out_yoy_csv.exists()

    out_df = pd.read_csv(out_csv, parse_dates=["date"])
    assert len(out_df) == 8
    expected = 130.0 / 125.0 * 100.0  # = 104.0
    assert all(abs(v - expected) < 1e-9 for v in out_df["value"])

    yoy_df = pd.read_csv(out_yoy_csv, parse_dates=["date"])
    # Y/Y on a flat ratio = 0%
    assert len(yoy_df) == 4  # first 4 quarters drop (no Y/Y comparator)
    assert all(abs(v - 0.0) < 1e-9 for v in yoy_df["value"])

    out_meta_dict = json.loads(out_meta.read_text(encoding="utf-8"))
    assert out_meta_dict["name"] == "terms_of_trade"
    assert out_meta_dict["units"] == "Index, 2017=100"
    assert out_meta_dict["frequency"] == "quarterly"
    assert out_meta_dict["transform"] == "exports_ipi/imports_ipi*100"


def test_derive_terms_of_trade_is_noop_when_inputs_missing(tmp_path, monkeypatch, caplog):
    """ToT derivation requires BOTH IPI series; missing either is a no-op."""
    data_root = tmp_path / "data"
    (data_root / "raw").mkdir(parents=True)
    (data_root / "processed").mkdir(parents=True)
    _seed_quarterly_raw(data_root, "tot_exports_ipi", [130.0] * 8, start="2024-01-01")
    # tot_imports_ipi NOT seeded

    from pipeline import build as build_mod

    monkeypatch.setattr(build_mod, "DATA_RAW", data_root / "raw")
    monkeypatch.setattr(build_mod, "DATA_PROCESSED", data_root / "processed")

    with caplog.at_level("WARNING"):
        build_mod.derive_terms_of_trade()  # should not raise

    assert not (data_root / "processed" / "terms_of_trade.csv").exists()


def test_derive_current_account_views_sums_components(tmp_path, monkeypatch):
    """`derive_current_account_views()` writes the components-sum file from
    the four sub-component balances.
    """
    data_root = tmp_path / "data"
    # 8 quarters; sum of fixed values
    _seed_quarterly_raw(data_root, "ca_goods_balance_q", [-4000.0] * 8, start="2024-01-01")
    _seed_quarterly_raw(data_root, "ca_services_balance_q", [1500.0] * 8, start="2024-01-01")
    _seed_quarterly_raw(data_root, "ca_primary_income_q", [3000.0] * 8, start="2024-01-01")
    _seed_quarterly_raw(data_root, "ca_secondary_income_q", [-800.0] * 8, start="2024-01-01")

    from pipeline import build as build_mod

    monkeypatch.setattr(build_mod, "DATA_RAW", data_root / "raw")
    monkeypatch.setattr(build_mod, "DATA_PROCESSED", data_root / "processed")

    build_mod.derive_current_account_views()

    out_csv = data_root / "processed" / "current_account_components_sum.csv"
    out_meta = data_root / "processed" / "current_account_components_sum.meta.json"
    assert out_csv.exists()
    assert out_meta.exists()

    out_df = pd.read_csv(out_csv, parse_dates=["date"])
    assert len(out_df) == 8
    expected_sum = -4000.0 + 1500.0 + 3000.0 + (-800.0)  # = -300
    assert all(abs(v - expected_sum) < 1e-9 for v in out_df["value"])

    out_meta_dict = json.loads(out_meta.read_text(encoding="utf-8"))
    assert out_meta_dict["name"] == "current_account_components_sum"
    assert out_meta_dict["units"] == "C$ millions"
    assert out_meta_dict["frequency"] == "quarterly"
    assert out_meta_dict["transform"] == "sum_components"


def _seed_daily_raw(
    data_root: Path,
    name: str,
    values: list[float],
    start: str = "2024-01-02",
) -> None:
    """Drop a raw daily (business-day) CSV + .meta.json under data/raw/."""
    idx = pd.bdate_range(start=start, periods=len(values))
    df = pd.DataFrame({"date": idx, "value": values})
    meta = SeriesMeta(
        name=name,
        source="Bank of Canada Valet API",
        source_url=f"https://example.invalid/{name}",
        source_id=name.upper(),
        units="%",
        frequency="daily",
    )
    write_series(df, meta, data_root / "raw")


def test_derive_corra_overnight_spread_writes_bps(tmp_path, monkeypatch):
    """`derive_corra_overnight_spread()` reads daily CORRA and daily overnight
    target, writes data/processed/corra_overnight_spread_bps.csv with the
    spread in basis points and the canonical transform tag.
    """
    data_root = tmp_path / "data"
    # 10 business days. CORRA above target by 0.03 pp on the first day, then
    # by 0.05 pp; expected spread in bps = +3 and +5 respectively. Throw a
    # negative case in the middle to exercise the sign.
    corra_vals = [2.28, 2.30, 2.29, 2.20, 2.20, 2.20, 2.27, 2.27, 2.28, 2.28]
    target_vals = [2.25, 2.25, 2.25, 2.25, 2.25, 2.25, 2.25, 2.25, 2.25, 2.25]
    _seed_daily_raw(data_root, "corra_daily", corra_vals, start="2024-01-02")
    _seed_daily_raw(data_root, "overnight_rate_daily", target_vals, start="2024-01-02")

    from pipeline import build_financial as bf_mod

    monkeypatch.setattr(bf_mod, "DATA_RAW", data_root / "raw")
    monkeypatch.setattr(bf_mod, "DATA_PROCESSED", data_root / "processed")

    bf_mod.derive_corra_overnight_spread()

    out_csv = data_root / "processed" / "corra_overnight_spread_bps.csv"
    out_meta = data_root / "processed" / "corra_overnight_spread_bps.meta.json"
    assert out_csv.exists()
    assert out_meta.exists()

    out_df = pd.read_csv(out_csv, parse_dates=["date"])
    assert len(out_df) == 10
    expected_bps = [
        round((c - t) * 100.0, 2) for c, t in zip(corra_vals, target_vals)
    ]
    # Compare element-wise; round in derivation matches the round here.
    for got, exp in zip(out_df["value"].tolist(), expected_bps):
        assert abs(got - exp) < 1e-9, f"got {got} expected {exp}"
    # Spot-check signs: row 3 (2.20 - 2.25 = -0.05 pp = -5 bps) and row 0
    # (2.28 - 2.25 = +3 bps).
    assert out_df["value"].iloc[0] == 3.0
    assert out_df["value"].iloc[3] == -5.0

    out_meta_dict = json.loads(out_meta.read_text(encoding="utf-8"))
    assert out_meta_dict["name"] == "corra_overnight_spread_bps"
    assert out_meta_dict["units"] == "basis points"
    assert out_meta_dict["frequency"] == "daily"
    assert out_meta_dict["transform"] == "(corra_daily - overnight_rate_daily) * 100"
    assert "AVG.INTWO-minus-V39079" in out_meta_dict["source_id"]


def test_derive_corra_overnight_spread_forward_fills_target(tmp_path, monkeypatch):
    """When the overnight-target series is sparser than CORRA (e.g. a missing
    publication day), the derivation forward-fills the target so every CORRA
    business day still resolves.
    """
    data_root = tmp_path / "data"
    # 5 business days of CORRA; target only has 4 (missing day 3).
    corra_vals = [2.28, 2.29, 2.28, 2.27, 2.28]
    target_vals = [2.25, 2.25, 2.25, 2.25]  # one fewer
    idx_c = pd.bdate_range(start="2024-01-02", periods=5)
    idx_t = pd.bdate_range(start="2024-01-02", periods=4)
    # Drop day-3 (index 2) from target to force ffill on a non-edge day.
    keep_target_dates = [idx_t[0], idx_t[1], idx_t[3]]  # skip index 2
    keep_target_vals = [target_vals[0], target_vals[1], target_vals[3]]
    df_c = pd.DataFrame({"date": idx_c, "value": corra_vals})
    df_t = pd.DataFrame({"date": keep_target_dates, "value": keep_target_vals})
    (data_root / "raw").mkdir(parents=True)
    write_series(df_c, SeriesMeta(
        name="corra_daily",
        source="Bank of Canada Valet API",
        source_url="https://example.invalid/corra",
        source_id="AVG.INTWO",
        units="%", frequency="daily",
    ), data_root / "raw")
    write_series(df_t, SeriesMeta(
        name="overnight_rate_daily",
        source="Bank of Canada Valet API",
        source_url="https://example.invalid/v39079",
        source_id="V39079",
        units="%", frequency="daily",
    ), data_root / "raw")

    from pipeline import build_financial as bf_mod

    monkeypatch.setattr(bf_mod, "DATA_RAW", data_root / "raw")
    monkeypatch.setattr(bf_mod, "DATA_PROCESSED", data_root / "processed")

    bf_mod.derive_corra_overnight_spread()

    out_df = pd.read_csv(
        data_root / "processed" / "corra_overnight_spread_bps.csv",
        parse_dates=["date"],
    )
    # All 5 CORRA business days should resolve via ffill; spread = (corra - 2.25) * 100.
    assert len(out_df) == 5
    expected = [round((c - 2.25) * 100.0, 2) for c in corra_vals]
    for got, exp in zip(out_df["value"].tolist(), expected):
        assert abs(got - exp) < 1e-9


def test_derive_corra_overnight_spread_is_noop_when_inputs_missing(
    tmp_path, monkeypatch, caplog,
):
    """If either input is absent, the derivation logs a warning and returns
    cleanly without writing anything.
    """
    data_root = tmp_path / "data"
    (data_root / "raw").mkdir(parents=True)
    (data_root / "processed").mkdir(parents=True)
    # Seed only CORRA; overnight missing.
    _seed_daily_raw(data_root, "corra_daily", [2.28, 2.29, 2.28], start="2024-01-02")

    from pipeline import build_financial as bf_mod

    monkeypatch.setattr(bf_mod, "DATA_RAW", data_root / "raw")
    monkeypatch.setattr(bf_mod, "DATA_PROCESSED", data_root / "processed")

    with caplog.at_level("WARNING"):
        bf_mod.derive_corra_overnight_spread()  # should NOT raise

    assert not (data_root / "processed" / "corra_overnight_spread_bps.csv").exists()


def test_derive_cpi_breadth_gt3_weighted_share_math(tmp_path, monkeypatch):
    """`derive_cpi_breadth_gt3()` reads wide-format cpi_components.csv and the
    per-component weight mapping JSON, and writes data/processed/
    cpi_breadth_gt3.csv = weighted share of components with Y/Y > 3%.

    Construction: three synthetic components A/B/C with weights 10/20/30 (total
    60). Seed 24 monthly observations. In the latest month, A's Y/Y = 1.0%,
    B's Y/Y = 5.0% (above 3), C's Y/Y = 4.0% (above 3). Expected share =
    (20 + 30) / (10 + 20 + 30) * 100 = 83.333%.
    """
    data_root = tmp_path / "data"
    raw_dir = data_root / "raw"
    derived_dir = data_root / "derived"
    processed_dir = data_root / "processed"
    raw_dir.mkdir(parents=True)
    derived_dir.mkdir(parents=True)
    processed_dir.mkdir(parents=True)

    # 24 months of index levels. For Y/Y, we need months 13..24 to compare
    # to months 1..12.
    dates = pd.date_range(start="2024-04-01", periods=24, freq="MS")
    # Component A: flat 100 -> Y/Y = 0% for all comparison months EXCEPT
    # the latest, where we lift to 101 (Y/Y = 1.0%).
    a_levels = [100.0] * 23 + [101.0]
    # Component B: 100 -> latest is 105 (Y/Y = 5.0%).
    b_levels = [100.0] * 23 + [105.0]
    # Component C: 100 -> latest is 104 (Y/Y = 4.0%).
    c_levels = [100.0] * 23 + [104.0]
    df_components = pd.DataFrame({
        "date": dates,
        "A": a_levels,
        "B": b_levels,
        "C": c_levels,
    })
    df_components.to_csv(raw_dir / "cpi_components.csv", index=False)
    (raw_dir / "cpi_components.meta.json").write_text(json.dumps({
        "name": "cpi_components", "source": "Statistics Canada",
        "source_url": "https://example.invalid", "source_id": "Table 18-10-0004-01",
        "units": "Index, 2002=100", "frequency": "monthly",
        "fetched_at": "2026-05-11T00:00:00+00:00", "release_date": None,
    }), encoding="utf-8")

    weights = [
        {"name": "A", "wt_value": 10.0, "cpi_vector": 1, "wt_refPer": "2024-01-01"},
        {"name": "B", "wt_value": 20.0, "cpi_vector": 2, "wt_refPer": "2024-01-01"},
        {"name": "C", "wt_value": 30.0, "cpi_vector": 3, "wt_refPer": "2024-01-01"},
    ]
    (derived_dir / "cpi_component_weights_canada.json").write_text(
        json.dumps(weights), encoding="utf-8",
    )

    from pipeline import build as build_mod

    monkeypatch.setattr(build_mod, "DATA_RAW", raw_dir)
    monkeypatch.setattr(build_mod, "DATA_PROCESSED", processed_dir)
    monkeypatch.setattr(build_mod, "DATA_DERIVED", derived_dir)

    build_mod.derive_cpi_breadth_gt3()

    out_csv = processed_dir / "cpi_breadth_gt3.csv"
    out_meta = processed_dir / "cpi_breadth_gt3.meta.json"
    assert out_csv.exists()
    assert out_meta.exists()

    out_df = pd.read_csv(out_csv, parse_dates=["date"])
    # 12 Y/Y rows (months 13-24); the first 12 are dropped because of NaN.
    assert len(out_df) == 12
    # Months 13..23 have all components at 0% Y/Y -> share above 3 = 0.
    for v in out_df["value"].iloc[:-1]:
        assert abs(v - 0.0) < 1e-9
    # Latest (month 24): components B (5%) and C (4%) above 3; share =
    # (20 + 30) / (10 + 20 + 30) * 100 = 83.333...
    assert out_df["value"].iloc[-1] == pytest.approx(50.0 / 60.0 * 100.0, rel=1e-9)

    out_meta_dict = json.loads(out_meta.read_text(encoding="utf-8"))
    assert out_meta_dict["name"] == "cpi_breadth_gt3"
    assert out_meta_dict["frequency"] == "monthly"
    assert out_meta_dict["transform"] == "basket_weighted_share(yoy>3, normalize_over_valid)"
    assert out_meta_dict["units"].startswith("%")


def test_derive_cpi_breadth_gt3_normalizes_over_valid_only(tmp_path, monkeypatch):
    """If one component has insufficient history (no Y/Y comparator), it is
    dropped from BOTH the numerator and the denominator so coverage gaps
    don't bias the share toward zero."""
    data_root = tmp_path / "data"
    raw_dir = data_root / "raw"
    derived_dir = data_root / "derived"
    processed_dir = data_root / "processed"
    raw_dir.mkdir(parents=True)
    derived_dir.mkdir(parents=True)
    processed_dir.mkdir(parents=True)

    dates = pd.date_range(start="2024-04-01", periods=24, freq="MS")
    # A: full 24-month history, latest Y/Y = 5% (above 3).
    a_levels = [100.0] * 23 + [105.0]
    # B: only the last 6 months populated (NaN prior). Y/Y in the latest
    # month is undefined -> drop B from numerator AND denominator.
    b_levels = [float("nan")] * 18 + [100.0, 100.0, 100.0, 100.0, 100.0, 105.0]
    df_components = pd.DataFrame({
        "date": dates,
        "A": a_levels,
        "B": b_levels,
    })
    df_components.to_csv(raw_dir / "cpi_components.csv", index=False)
    (raw_dir / "cpi_components.meta.json").write_text(json.dumps({
        "name": "cpi_components", "source": "Statistics Canada",
        "source_url": "https://example.invalid", "source_id": "Table 18-10-0004-01",
        "units": "Index, 2002=100", "frequency": "monthly",
        "fetched_at": "2026-05-11T00:00:00+00:00", "release_date": None,
    }), encoding="utf-8")

    weights = [
        {"name": "A", "wt_value": 30.0, "cpi_vector": 1, "wt_refPer": "2024-01-01"},
        {"name": "B", "wt_value": 70.0, "cpi_vector": 2, "wt_refPer": "2024-01-01"},
    ]
    (derived_dir / "cpi_component_weights_canada.json").write_text(
        json.dumps(weights), encoding="utf-8",
    )

    from pipeline import build as build_mod

    monkeypatch.setattr(build_mod, "DATA_RAW", raw_dir)
    monkeypatch.setattr(build_mod, "DATA_PROCESSED", processed_dir)
    monkeypatch.setattr(build_mod, "DATA_DERIVED", derived_dir)

    build_mod.derive_cpi_breadth_gt3()

    out_df = pd.read_csv(processed_dir / "cpi_breadth_gt3.csv", parse_dates=["date"])
    # Latest month: only A is valid (B has NaN 12 months ago); A is at +5%
    # which is above 3, so share = 30/30 * 100 = 100%. If we incorrectly
    # normalized over the full basket (30 + 70 = 100), we'd get 30%.
    assert out_df["value"].iloc[-1] == pytest.approx(100.0, rel=1e-9)


def test_derive_cpi_breadth_gt3_is_noop_when_inputs_missing(tmp_path, monkeypatch, caplog):
    """Missing cpi_components OR missing the weights JSON -> log + return."""
    data_root = tmp_path / "data"
    (data_root / "raw").mkdir(parents=True)
    (data_root / "processed").mkdir(parents=True)
    (data_root / "derived").mkdir(parents=True)

    from pipeline import build as build_mod

    monkeypatch.setattr(build_mod, "DATA_RAW", data_root / "raw")
    monkeypatch.setattr(build_mod, "DATA_PROCESSED", data_root / "processed")
    monkeypatch.setattr(build_mod, "DATA_DERIVED", data_root / "derived")

    with caplog.at_level("WARNING"):
        build_mod.derive_cpi_breadth_gt3()  # should NOT raise

    assert not (data_root / "processed" / "cpi_breadth_gt3.csv").exists()


def test_derive_cpi_breadth_band_math(tmp_path, monkeypatch):
    """`derive_cpi_breadth_band()` ports the boc-tracker recipe:

      - Keep only components with first_valid_index <= 1995-01-01.
      - Normalize the surviving weights to sum to 1.
      - For each month: above3 = sum(weight x I(yoy > 3)) x 100.
                         below1 = sum(weight x I(yoy < 1)) x 100.
      - Drop months where any kept component is missing Y/Y.
      - 1996-2019 average = mean over that window (inclusive).

    Construction: three deep-history components A/B/C (all start 1994-01) plus
    one young component D (starts 2020) which must be filtered out by the
    cutoff. Inflation pattern: latest month has Y/Y A=0.5% (below 1), B=4%
    (above 3), C=2% (between). With raw weights 10/20/30/40 and D dropped,
    the kept weights are 10/20/30 -> normalized 1/6, 2/6, 3/6. Expected
    latest above3 = (2/6) x 100 x 100 = 33.33%. Expected latest below1 =
    (1/6) x 100 x 100 = 16.67%.
    """
    data_root = tmp_path / "data"
    raw_dir = data_root / "raw"
    derived_dir = data_root / "derived"
    processed_dir = data_root / "processed"
    raw_dir.mkdir(parents=True)
    derived_dir.mkdir(parents=True)
    processed_dir.mkdir(parents=True)

    # 26 monthly observations starting 1994-01. Months 13..26 (1995-01..1996-02)
    # have defined Y/Y. We need at least one observation on or before 1995-01-01
    # for A/B/C so they pass the cutoff filter. D starts in month 25 (2020-style
    # late entrant in the synthetic) so its first_valid_index is well after the
    # cutoff and it gets dropped.
    dates = pd.date_range(start="1994-01-01", periods=26, freq="MS")
    a_levels = [100.0] * 25 + [100.5]  # latest Y/Y = +0.5% (below 1)
    b_levels = [100.0] * 25 + [104.0]  # latest Y/Y = +4.0% (above 3)
    c_levels = [100.0] * 25 + [102.0]  # latest Y/Y = +2.0% (between bands)
    d_levels: list[float] = [float("nan")] * 24 + [100.0, 102.0]  # first_valid after cutoff
    df_components = pd.DataFrame({
        "date": dates,
        "A": a_levels,
        "B": b_levels,
        "C": c_levels,
        "D": d_levels,
    })
    df_components.to_csv(raw_dir / "cpi_components.csv", index=False)

    weights = [
        {"name": "A", "wt_value": 10.0, "cpi_vector": 1, "wt_refPer": "2024-01-01"},
        {"name": "B", "wt_value": 20.0, "cpi_vector": 2, "wt_refPer": "2024-01-01"},
        {"name": "C", "wt_value": 30.0, "cpi_vector": 3, "wt_refPer": "2024-01-01"},
        {"name": "D", "wt_value": 40.0, "cpi_vector": 4, "wt_refPer": "2024-01-01"},
    ]
    (derived_dir / "cpi_component_weights_canada.json").write_text(
        json.dumps(weights), encoding="utf-8",
    )

    from pipeline import build as build_mod

    monkeypatch.setattr(build_mod, "DATA_RAW", raw_dir)
    monkeypatch.setattr(build_mod, "DATA_PROCESSED", processed_dir)
    monkeypatch.setattr(build_mod, "DATA_DERIVED", derived_dir)

    build_mod.derive_cpi_breadth_band()

    above_csv = processed_dir / "cpi_breadth_above3.csv"
    below_csv = processed_dir / "cpi_breadth_below1.csv"
    band_meta = derived_dir / "cpi_breadth_band_metadata.json"
    assert above_csv.exists()
    assert below_csv.exists()
    assert band_meta.exists()

    above_df = pd.read_csv(above_csv, parse_dates=["date"])
    below_df = pd.read_csv(below_csv, parse_dates=["date"])

    # Latest month: B at 4% -> above3 numerator = w_B normalized = 20/60.
    # Multiplied by 100 (gt) then x100 (% scaling) = 33.333%.
    assert above_df["value"].iloc[-1] == pytest.approx(20.0 / 60.0 * 100.0, rel=1e-9)
    # A at 0.5% -> below1 numerator = w_A normalized = 10/60. = 16.667%.
    assert below_df["value"].iloc[-1] == pytest.approx(10.0 / 60.0 * 100.0, rel=1e-9)

    band = json.loads(band_meta.read_text(encoding="utf-8"))
    assert band["components_kept"] == 3  # D was filtered out by the cutoff
    assert band["weights_unnormalised_sum_pct"] == pytest.approx(60.0)
    assert band["latest_above3"] == pytest.approx(20.0 / 60.0 * 100.0, rel=1e-9)
    assert band["latest_below1"] == pytest.approx(10.0 / 60.0 * 100.0, rel=1e-9)
    # The synthetic levels are flat 100 in every comparison month except the
    # last, so Y/Y is 0 for months 1995-01..1996-01. None of those are inside
    # 1996-2019 except 1996-01..1996-02; latest (1996-02) has 4%/0.5%/2%
    # for B/A/C. Historical-window average = mean over those rows.
    assert band["historical_avg_above3_1996_2019"] >= 0.0
    assert band["historical_avg_below1_1996_2019"] >= 0.0


def test_derive_cpi_breadth_band_is_noop_when_inputs_missing(tmp_path, monkeypatch, caplog):
    """Missing cpi_components OR missing the weights JSON -> log + return."""
    data_root = tmp_path / "data"
    (data_root / "raw").mkdir(parents=True)
    (data_root / "processed").mkdir(parents=True)
    (data_root / "derived").mkdir(parents=True)

    from pipeline import build as build_mod

    monkeypatch.setattr(build_mod, "DATA_RAW", data_root / "raw")
    monkeypatch.setattr(build_mod, "DATA_PROCESSED", data_root / "processed")
    monkeypatch.setattr(build_mod, "DATA_DERIVED", data_root / "derived")

    with caplog.at_level("WARNING"):
        build_mod.derive_cpi_breadth_band()  # should NOT raise

    assert not (data_root / "processed" / "cpi_breadth_above3.csv").exists()
    assert not (data_root / "processed" / "cpi_breadth_below1.csv").exists()


def test_derive_labour_force_ex_npr_math(tmp_path, monkeypatch):
    """`derive_labour_force_ex_npr()` reads quarterly NPR flows + quarterly
    pop_total + monthly unemployment_level + monthly unemployment_rate and
    writes data/processed/labour_force_ex_npr.csv = LF * (1 - npr_share).

    Construction:
      - 8 quarters of NPR net flows, each +100,000. Cumulative stock at
        quarter 8 = 800,000.
      - 8 quarters of pop_total flat at 40,000,000. So npr_share at every
        quarter = 800,000 / 40,000,000 = 0.02 (well, only at quarter 8;
        earlier quarters are 100k/40M = 0.0025 etc.).
      - 24 months of unemployment_level flat at 1.5 (M). u_rate flat at 6.0%.
        -> LF = 1.5 / 0.06 = 25.0 (M).
      - At the latest month aligned with quarter 8, npr_share = 0.02 ->
        LF ex-NPR = 25.0 * (1 - 0.02) = 24.5 (M).
    """
    data_root = tmp_path / "data"
    raw_dir = data_root / "raw"
    processed_dir = data_root / "processed"
    raw_dir.mkdir(parents=True)
    processed_dir.mkdir(parents=True)

    # Seed quarterly NPR flows (8 quarters, each +100k).
    q_dates = pd.date_range(start="2024-01-01", periods=8, freq="QS")
    pd.DataFrame({"date": q_dates, "value": [100_000.0] * 8}).to_csv(
        raw_dir / "pop_net_npr.csv", index=False,
    )
    (raw_dir / "pop_net_npr.meta.json").write_text(json.dumps({
        "name": "pop_net_npr", "source": "Statistics Canada",
        "source_url": "https://example.invalid", "source_id": "v29850346",
        "units": "Persons", "frequency": "quarterly",
        "fetched_at": "2026-05-12T00:00:00+00:00", "release_date": None,
    }), encoding="utf-8")

    # Seed quarterly pop_total (flat 40M).
    pd.DataFrame({"date": q_dates, "value": [40_000_000.0] * 8}).to_csv(
        raw_dir / "pop_total.csv", index=False,
    )
    (raw_dir / "pop_total.meta.json").write_text(json.dumps({
        "name": "pop_total", "source": "Statistics Canada",
        "source_url": "https://example.invalid", "source_id": "v1",
        "units": "Persons", "frequency": "quarterly",
        "fetched_at": "2026-05-12T00:00:00+00:00", "release_date": None,
    }), encoding="utf-8")

    # Seed monthly unemployment_level (24 months, flat 1.5 M).
    m_dates = pd.date_range(start="2024-01-01", periods=24, freq="MS")
    pd.DataFrame({"date": m_dates, "value": [1.5] * 24}).to_csv(
        raw_dir / "unemployment_level.csv", index=False,
    )
    (raw_dir / "unemployment_level.meta.json").write_text(json.dumps({
        "name": "unemployment_level", "source": "Statistics Canada",
        "source_url": "https://example.invalid", "source_id": "v2062814",
        "units": "Millions of persons", "frequency": "monthly",
        "fetched_at": "2026-05-12T00:00:00+00:00", "release_date": None,
    }), encoding="utf-8")

    # Seed monthly unemployment_rate (24 months, flat 6.0%).
    pd.DataFrame({"date": m_dates, "value": [6.0] * 24}).to_csv(
        raw_dir / "unemployment_rate.csv", index=False,
    )
    (raw_dir / "unemployment_rate.meta.json").write_text(json.dumps({
        "name": "unemployment_rate", "source": "Statistics Canada",
        "source_url": "https://example.invalid", "source_id": "v2062815",
        "units": "%", "frequency": "monthly",
        "fetched_at": "2026-05-12T00:00:00+00:00", "release_date": None,
    }), encoding="utf-8")

    from pipeline import build as build_mod

    monkeypatch.setattr(build_mod, "DATA_RAW", raw_dir)
    monkeypatch.setattr(build_mod, "DATA_PROCESSED", processed_dir)

    build_mod.derive_labour_force_ex_npr()

    out_csv = processed_dir / "labour_force_ex_npr.csv"
    out_meta = processed_dir / "labour_force_ex_npr.meta.json"
    assert out_csv.exists()
    assert out_meta.exists()

    out_df = pd.read_csv(out_csv, parse_dates=["date"])
    # Latest month is 2025-12-01 (24 months from 2024-01). Latest quarter is
    # 2025-10-01 with cumulative NPR stock = 800,000 / 40M = 0.02 -> LF * 0.98.
    latest = out_df.iloc[-1]
    assert latest["date"] == pd.Timestamp("2025-12-01")
    assert latest["value"] == pytest.approx(25.0 * (1.0 - 0.02), rel=1e-9)
    # Sanity: every value is below the unfiltered LF of 25.0.
    assert (out_df["value"] < 25.0).all()
    # Sanity: monotonically decreasing over time as cumulative NPR stock grows.
    diffs = out_df["value"].diff().dropna()
    assert (diffs <= 0).all()

    out_meta_dict = json.loads(out_meta.read_text(encoding="utf-8"))
    assert out_meta_dict["name"] == "labour_force_ex_npr"
    assert out_meta_dict["units"] == "Millions of persons"
    assert out_meta_dict["frequency"] == "monthly"
    assert "uniform-participation" in out_meta_dict["transform"]
    # Provenance string carries vector ids for all four inputs.
    assert "v2062814" in out_meta_dict["source_id"]
    assert "v2062815" in out_meta_dict["source_id"]
    assert "v1" in out_meta_dict["source_id"]
    assert "v29850346" in out_meta_dict["source_id"]


def test_derive_labour_force_ex_npr_is_noop_when_inputs_missing(tmp_path, monkeypatch, caplog):
    """Missing any of the four inputs -> warn + return, no output written."""
    data_root = tmp_path / "data"
    (data_root / "raw").mkdir(parents=True)
    (data_root / "processed").mkdir(parents=True)

    from pipeline import build as build_mod

    monkeypatch.setattr(build_mod, "DATA_RAW", data_root / "raw")
    monkeypatch.setattr(build_mod, "DATA_PROCESSED", data_root / "processed")

    with caplog.at_level("WARNING"):
        build_mod.derive_labour_force_ex_npr()  # should NOT raise

    assert not (data_root / "processed" / "labour_force_ex_npr.csv").exists()


def test_derive_gdp_views_is_noop_when_raw_missing(tmp_path, monkeypatch, caplog):
    """If `data/raw/gdp_monthly.csv` is absent, derive_gdp_views() emits a
    warning and returns cleanly without writing anything (mirrors the
    other derive_* helpers' contract)."""
    data_root = tmp_path / "data"
    (data_root / "raw").mkdir(parents=True)
    (data_root / "processed").mkdir(parents=True)

    from pipeline import build as build_mod

    monkeypatch.setattr(build_mod, "DATA_RAW", data_root / "raw")
    monkeypatch.setattr(build_mod, "DATA_PROCESSED", data_root / "processed")

    with caplog.at_level("WARNING"):
        build_mod.derive_gdp_views()  # should NOT raise

    assert not (data_root / "processed" / "gdp_monthly_yoy.csv").exists()
    # The "derivation skipped: missing raw ..." warning is emitted by _read_raw.
    assert any("missing raw" in rec.message for rec in caplog.records)
