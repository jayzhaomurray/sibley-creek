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
