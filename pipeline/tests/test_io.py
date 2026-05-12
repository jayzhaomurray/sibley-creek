"""Tests for the sidecar metadata writer."""

from __future__ import annotations

import json

import pandas as pd

from pipeline.io import SCHEMA_VERSION, SeriesMeta, write_series, write_series_merge


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


def _make_meta(name: str = "wti") -> SeriesMeta:
    return SeriesMeta(
        name=name,
        source="Test",
        source_url="https://example.com",
        source_id="X",
        units="USD/barrel",
        frequency="daily",
    )


def test_write_series_merge_no_existing_file_writes_fresh(tmp_path):
    df = pd.DataFrame(
        {
            "date": pd.to_datetime(["2025-01-01", "2025-01-02"]),
            "value": [10.0, 11.0],
        }
    )
    csv_path, _ = write_series_merge(df, _make_meta(), tmp_path)
    loaded = pd.read_csv(csv_path, parse_dates=["date"])
    assert len(loaded) == 2
    assert list(loaded["value"]) == [10.0, 11.0]


def test_write_series_merge_unions_disjoint_dates(tmp_path):
    # Pre-existing 2-row file
    existing = pd.DataFrame(
        {
            "date": pd.to_datetime(["2025-01-01", "2025-01-02"]),
            "value": [10.0, 11.0],
        }
    )
    write_series(existing, _make_meta(), tmp_path)

    # Fresh fetch returns ONE new row on a different date
    fresh = pd.DataFrame(
        {
            "date": pd.to_datetime(["2025-01-03"]),
            "value": [12.0],
        }
    )
    csv_path, _ = write_series_merge(fresh, _make_meta(), tmp_path)
    loaded = pd.read_csv(csv_path, parse_dates=["date"])
    assert len(loaded) == 3
    assert list(loaded["value"]) == [10.0, 11.0, 12.0]


def test_write_series_merge_prefers_new_on_overlap(tmp_path):
    existing = pd.DataFrame(
        {
            "date": pd.to_datetime(["2025-01-01", "2025-01-02"]),
            "value": [10.0, 11.0],
        }
    )
    write_series(existing, _make_meta(), tmp_path)

    # Fresh row revises the value for 2025-01-02 and adds 2025-01-03
    fresh = pd.DataFrame(
        {
            "date": pd.to_datetime(["2025-01-02", "2025-01-03"]),
            "value": [99.0, 12.0],
        }
    )
    csv_path, _ = write_series_merge(fresh, _make_meta(), tmp_path)
    loaded = pd.read_csv(csv_path, parse_dates=["date"])
    assert len(loaded) == 3
    assert list(loaded["value"]) == [10.0, 99.0, 12.0]


def test_write_series_merge_preserves_dates_dropped_by_source(tmp_path):
    """The regression case: Yahoo returns a mixed-cadence response, dropping
    most of the historical daily rows. Merge must NOT silently truncate the
    on-disk history.
    """
    # Simulate the pre-regression file: many daily rows
    existing = pd.DataFrame(
        {
            "date": pd.date_range("2024-01-01", periods=200, freq="D"),
            "value": [float(i) for i in range(200)],
        }
    )
    write_series(existing, _make_meta(), tmp_path)

    # Source now returns only 3 days. The first (2024-07-18) overlaps with
    # the existing tail; the other two (2024-07-19, 2024-07-20) extend it.
    fresh = pd.DataFrame(
        {
            "date": pd.to_datetime(["2024-07-18", "2024-07-19", "2024-07-20"]),
            "value": [999.0, 1000.0, 1001.0],
        }
    )
    csv_path, meta_path = write_series_merge(fresh, _make_meta(), tmp_path)
    loaded = pd.read_csv(csv_path, parse_dates=["date"])
    # 200 original rows; one date (2024-07-18) overlaps and is replaced;
    # two new dates (2024-07-19, 2024-07-20) are appended -> 202 rows.
    assert len(loaded) == 202
    # Latest row is the appended fresh tail
    assert loaded["date"].max() == pd.Timestamp("2024-07-20")
    assert loaded.loc[loaded["date"] == pd.Timestamp("2024-07-20"), "value"].iloc[0] == 1001.0
    # The overlap date carries the FRESH value, not the historical one
    overlap_val = loaded.loc[loaded["date"] == pd.Timestamp("2024-07-18"), "value"].iloc[0]
    assert overlap_val == 999.0

    meta_loaded = json.loads(meta_path.read_text())
    # reference_period spans the full merged frame, not just the fresh response
    assert meta_loaded["reference_period_start"] == "2024-01-01"
    assert meta_loaded["reference_period_end"] == "2024-07-20"
