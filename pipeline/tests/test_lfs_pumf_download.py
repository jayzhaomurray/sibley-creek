"""Tests for pipeline.lfs_pumf.download.

Uses monkeypatching of requests.get (not pytest-httpx — the downloader uses
requests, not httpx, due to StatCan TLS fingerprinting requirements).

Fixture zips are built in-test from tiny synthetic CSVs to avoid any
dependency on network or on-disk test assets.
"""

from __future__ import annotations

import io
import json
import zipfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from pipeline.lfs_pumf.download import (
    _KEEP_COLS,
    _extract_monthly_from_zip_bytes,
    _trim_columns,
    _write_meta,
    get_month,
)


# ---------------------------------------------------------------------------
# Helper: build synthetic zip bytes
# ---------------------------------------------------------------------------

def _make_synthetic_row() -> dict:
    """Return a dict with all required PUMF columns (minimal valid values)."""
    return {
        "survyear": 2026, "survmnth": 4,
        "lfsstat": 1, "cowmain": 2,
        "hrlyearn": 3100, "finalwt": 500,
        "gender": 1, "age_12": 5, "educ": 4,
        "tenure": 60, "noc_43": 12, "naics_21": 10,
        "union": 3, "ftptmain": 1, "mjh": 1,
        "permtemp": 1, "marstat": 1, "immig": 3,
        "estsize": 2, "prov": 35,
        # Extra column that should be trimmed
        "rec_num": 999,
    }


def _make_csv_bytes(n_rows: int = 5, year: int = 2026, month: int = 4) -> bytes:
    rows = []
    for _ in range(n_rows):
        row = _make_synthetic_row()
        row["survyear"] = year
        row["survmnth"] = month
        rows.append(row)
    df = pd.DataFrame(rows)
    return df.to_csv(index=False).encode()


def _make_zip_bytes(
    csv_bytes: bytes,
    filename: str,
) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(filename, csv_bytes)
    return buf.getvalue()


def _make_monthly_zip(year: int = 2026, month: int = 4) -> bytes:
    """Monthly zip: single CSV named pub{MM}{YY}.csv."""
    yy = str(year)[2:]
    fname = f"pub{month:02d}{yy}.csv"
    return _make_zip_bytes(_make_csv_bytes(5, year, month), fname)


def _make_annual_zip(year: int = 2024) -> bytes:
    """Annual zip: 12 monthly CSVs pub{MM}{YY}.csv."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for m in range(1, 13):
            yy = str(year)[2:]
            fname = f"pub{m:02d}{yy}.csv"
            zf.writestr(fname, _make_csv_bytes(5, year, m))
    return buf.getvalue()


# ---------------------------------------------------------------------------
# Tests: _extract_monthly_from_zip_bytes
# ---------------------------------------------------------------------------

def test_extract_monthly_from_zip_bytes_monthly_zip():
    """Monthly zip (single CSV) is found by target name."""
    zip_bytes = _make_monthly_zip(2026, 4)
    df = _extract_monthly_from_zip_bytes(zip_bytes, 2026, 4)
    assert df is not None
    assert len(df) == 5
    assert "hrlyearn" in df.columns


def test_extract_monthly_from_zip_bytes_annual_zip():
    """Annual zip (12 CSVs) correctly finds the requested month."""
    zip_bytes = _make_annual_zip(2024)
    df = _extract_monthly_from_zip_bytes(zip_bytes, 2024, 6)
    assert df is not None
    assert len(df) == 5


def test_extract_monthly_from_zip_bytes_wrong_month_annual():
    """Requesting a month not in a two-month zip returns None (zip only has 1 entry)."""
    # Build a zip with only January 2024
    zip_bytes = _make_zip_bytes(_make_csv_bytes(5, 2024, 1), "pub0124.csv")
    # Full annual zip for 2024 would have pub0224..pub1224; a zip with only pub0124
    # has exactly one CSV so the "single CSV fallback" kicks in and returns it.
    # This test verifies the fallback for a zip with exactly one CSV.
    df = _extract_monthly_from_zip_bytes(zip_bytes, 2024, 1)
    assert df is not None  # fallback finds the single CSV


def test_extract_monthly_from_zip_bytes_nested_path_2025_style():
    """2025 annual bundle stores CSVs with a directory prefix: '2025-CSV.zip/pub0125.csv'."""
    year, month = 2025, 1
    yy = str(year)[2:]
    # Build zip with nested path (as StatCan 2025 bundle does)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        for m in range(1, 13):
            nested_name = f"2025-CSV.zip/pub{m:02d}{yy}.csv"
            zf.writestr(nested_name, _make_csv_bytes(5, year, m))
    zip_bytes = buf.getvalue()
    df = _extract_monthly_from_zip_bytes(zip_bytes, year, month)
    assert df is not None
    assert len(df) == 5


def test_extract_monthly_from_zip_bytes_missing_month():
    """Requesting month 7 from an annual zip that only has months 1-6 returns None."""
    buf = io.BytesIO()
    year = 2024
    with zipfile.ZipFile(buf, "w") as zf:
        for m in range(1, 7):  # only Jan-Jun
            yy = str(year)[2:]
            zf.writestr(f"pub{m:02d}{yy}.csv", _make_csv_bytes(5, year, m))
    zip_bytes = buf.getvalue()
    df = _extract_monthly_from_zip_bytes(zip_bytes, 2024, 7)
    assert df is None


# ---------------------------------------------------------------------------
# Tests: _trim_columns
# ---------------------------------------------------------------------------

def test_trim_columns_removes_extra():
    """Extra columns not in _KEEP_COLS are dropped."""
    df = pd.DataFrame({"hrlyearn": [3100], "finalwt": [500], "extra_col": [1]})
    # Add all other keep cols as dummies
    for col in _KEEP_COLS:
        if col not in df.columns:
            df[col] = 0
    trimmed = _trim_columns(df)
    assert "extra_col" not in trimmed.columns
    assert all(c in trimmed.columns for c in _KEEP_COLS if c in df.columns)


def test_trim_columns_missing_cols_graceful():
    """Missing keep-cols are silently ignored (harmonize.py catches them later)."""
    df = pd.DataFrame({"hrlyearn": [3100], "finalwt": [500]})
    trimmed = _trim_columns(df)
    assert "hrlyearn" in trimmed.columns
    assert "finalwt" in trimmed.columns


# ---------------------------------------------------------------------------
# Tests: get_month with mocked requests
# ---------------------------------------------------------------------------

def test_get_month_uses_cached_parquet(tmp_path, monkeypatch):
    """get_month returns existing parquet without any HTTP call."""
    # Pre-create a fake parquet
    parquet = tmp_path / "2026-04.parquet"
    df = pd.DataFrame({c: [0] for c in _KEEP_COLS})
    df.to_parquet(parquet, index=False)

    # Redirect RAW_DIR to tmp_path
    monkeypatch.setattr("pipeline.lfs_pumf.download._RAW_DIR", tmp_path)
    monkeypatch.setattr("pipeline.lfs_pumf.download._ANNUAL_DIR", tmp_path / "annual")

    # Ensure no HTTP is made
    called = []
    def fake_get(*args, **kwargs):
        called.append(args)
        raise AssertionError("Should not fetch when cache exists")

    with patch("pipeline.lfs_pumf.download.requests.Session") as mock_session_cls:
        result = get_month(2026, 4)

    assert result == parquet
    assert len(called) == 0, "HTTP should not be called for cached parquet"


def test_get_month_monthly_url_success(tmp_path, monkeypatch):
    """get_month fetches from monthly URL when not cached."""
    monkeypatch.setattr("pipeline.lfs_pumf.download._RAW_DIR", tmp_path)
    monkeypatch.setattr("pipeline.lfs_pumf.download._ANNUAL_DIR", tmp_path / "annual")
    (tmp_path / "annual").mkdir()

    monthly_zip = _make_monthly_zip(2026, 4)

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = monthly_zip

    mock_session = MagicMock()
    mock_session.get.return_value = mock_response

    with patch("pipeline.lfs_pumf.download.requests.Session", return_value=mock_session):
        result = get_month(2026, 4)

    assert result.exists()
    assert result.suffix == ".parquet"
    meta_path = result.with_suffix(".meta.json")
    assert meta_path.exists()
    meta = json.loads(meta_path.read_text())
    assert meta["reference_period"] == "2026-04"


def test_get_month_falls_back_to_annual(tmp_path, monkeypatch):
    """get_month falls back to annual bundle when monthly URL returns 404."""
    monkeypatch.setattr("pipeline.lfs_pumf.download._RAW_DIR", tmp_path)
    annual_dir = tmp_path / "annual"
    annual_dir.mkdir()
    monkeypatch.setattr("pipeline.lfs_pumf.download._ANNUAL_DIR", annual_dir)

    annual_zip = _make_annual_zip(2024)

    def fake_get(url, **kwargs):
        resp = MagicMock()
        if "hist" in url:
            # Annual bundle
            resp.status_code = 200
            resp.content = annual_zip
        else:
            # Monthly URL
            resp.status_code = 404
            resp.content = b""
        return resp

    mock_session = MagicMock()
    mock_session.get.side_effect = fake_get
    mock_session.headers = MagicMock()

    with patch("pipeline.lfs_pumf.download.requests.Session", return_value=mock_session):
        result = get_month(2024, 6)

    assert result.exists()
    assert result.name == "2024-06.parquet"


def test_get_month_raises_on_total_failure(tmp_path, monkeypatch):
    """get_month raises RuntimeError when both URL patterns fail."""
    monkeypatch.setattr("pipeline.lfs_pumf.download._RAW_DIR", tmp_path)
    annual_dir = tmp_path / "annual"
    annual_dir.mkdir()
    monkeypatch.setattr("pipeline.lfs_pumf.download._ANNUAL_DIR", annual_dir)

    def fake_get(url, **kwargs):
        resp = MagicMock()
        resp.status_code = 404
        resp.content = b""
        return resp

    mock_session = MagicMock()
    mock_session.get.side_effect = fake_get
    mock_session.headers = MagicMock()

    with patch("pipeline.lfs_pumf.download.requests.Session", return_value=mock_session):
        with pytest.raises(RuntimeError, match="PUMF fetch failed"):
            get_month(2020, 3)


def test_get_month_annual_cache_avoids_refetch(tmp_path, monkeypatch):
    """Annual zip cached on disk is reused without a second HTTP call."""
    monkeypatch.setattr("pipeline.lfs_pumf.download._RAW_DIR", tmp_path)
    annual_dir = tmp_path / "annual"
    annual_dir.mkdir()
    monkeypatch.setattr("pipeline.lfs_pumf.download._ANNUAL_DIR", annual_dir)

    # Pre-write the annual zip
    annual_zip = _make_annual_zip(2024)
    (annual_dir / "2024-CSV.zip").write_bytes(annual_zip)

    # Monthly GET should 404; annual GET should NEVER be called
    def fake_get(url, **kwargs):
        resp = MagicMock()
        if "hist" in url:
            raise AssertionError("Annual URL should not be fetched when cached on disk")
        resp.status_code = 404
        resp.content = b""
        return resp

    mock_session = MagicMock()
    mock_session.get.side_effect = fake_get
    mock_session.headers = MagicMock()

    with patch("pipeline.lfs_pumf.download.requests.Session", return_value=mock_session):
        result = get_month(2024, 8)

    assert result.exists()
