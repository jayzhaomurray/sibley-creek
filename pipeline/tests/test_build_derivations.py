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
