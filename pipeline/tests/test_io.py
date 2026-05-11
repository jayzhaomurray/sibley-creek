"""Tests for the sidecar metadata writer."""

from __future__ import annotations

import json

import pandas as pd

from pipeline.io import SCHEMA_VERSION, SeriesMeta, write_series


def test_write_series_writes_csv_and_meta_json(tmp_path):
    df = pd.DataFrame(
        {
            "date": pd.to_datetime(["2025-01-01", "2025-02-01", "2025-03-01"]),
            "value": [1.0, 2.0, 3.0],
        }
    )
    meta = SeriesMeta(
        name="test_series",
        source="Test Source",
        source_url="https://example.com/test",
        source_id="TEST_ID",
        units="%",
        frequency="monthly",
    )

    csv_path, meta_path = write_series(df, meta, tmp_path)

    assert csv_path.exists()
    assert meta_path.exists()

    # CSV round-trips
    loaded = pd.read_csv(csv_path, parse_dates=["date"])
    assert len(loaded) == 3
    assert (loaded["value"] == [1.0, 2.0, 3.0]).all()

    # Meta JSON has the expected shape
    meta_loaded = json.loads(meta_path.read_text())
    assert meta_loaded["name"] == "test_series"
    assert meta_loaded["source"] == "Test Source"
    assert meta_loaded["schema_version"] == SCHEMA_VERSION
    # Reference period auto-derived from the date column
    assert meta_loaded["reference_period_start"] == "2025-01-01"
    assert meta_loaded["reference_period_end"] == "2025-03-01"
    # fetched_at populated automatically
    assert meta_loaded["fetched_at"]


def test_write_series_preserves_explicit_reference_period(tmp_path):
    df = pd.DataFrame(
        {
            "date": pd.to_datetime(["2025-01-01", "2025-02-01"]),
            "value": [1.0, 2.0],
        }
    )
    meta = SeriesMeta(
        name="explicit",
        source="x",
        source_url="https://example.com/x",
        source_id="X",
        units="x",
        frequency="monthly",
        reference_period_start="2020-01-01",
        reference_period_end="2020-12-31",
    )
    _, meta_path = write_series(df, meta, tmp_path)
    loaded = json.loads(meta_path.read_text())
    assert loaded["reference_period_start"] == "2020-01-01"
    assert loaded["reference_period_end"] == "2020-12-31"
