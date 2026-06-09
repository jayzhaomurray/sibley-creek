"""Tests for pipeline.lfs_pumf.sanity."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd
import pytest

from pipeline.lfs_pumf.sanity import SanityError, run_sanity_checks


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_harmonized_df(n: int = 55000, median_wage: float = 31.0) -> pd.DataFrame:
    """Return a minimal harmonized DataFrame that passes all sanity checks."""
    import numpy as np
    rng = np.random.default_rng(42)
    return pd.DataFrame({
        "wage":   rng.normal(median_wage, 5, n).clip(10, 200),
        "weight": rng.integers(100, 2000, n).astype(float),
        "gender": rng.choice([1, 2], n),
        "age_12": rng.choice(range(1, 13), n),
        "educ":   rng.choice(range(0, 7), n),
        "tenure_bin": rng.choice(["<12m", "12-35m", "36-59m", "60-119m", "120m+"], n),
        "noc_43": rng.choice(range(1, 44), n),
    })


def _write_fresh_meta(parquet_path: Path) -> None:
    meta = {
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "reference_period": parquet_path.stem,
    }
    parquet_path.with_suffix(".meta.json").write_text(json.dumps(meta))


def _write_stale_meta(parquet_path: Path, days_old: int = 200) -> None:
    stale_ts = (datetime.now(timezone.utc) - timedelta(days=days_old)).isoformat()
    meta = {
        "fetched_at": stale_ts,
        "reference_period": parquet_path.stem,
    }
    parquet_path.with_suffix(".meta.json").write_text(json.dumps(meta))


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------

def test_sanity_checks_pass_on_valid_data(tmp_path):
    """A valid harmonized DataFrame with fresh meta passes all checks."""
    df = _make_harmonized_df(55000)
    pq = tmp_path / "2026-04.parquet"
    pq.touch()
    _write_fresh_meta(pq)
    run_sanity_checks(df, parquet_path=pq, total_row_count=112000)


# ---------------------------------------------------------------------------
# Row count
# ---------------------------------------------------------------------------

def test_sanity_row_count_too_low_raises():
    df = _make_harmonized_df(n=10)  # way too low
    with pytest.raises(SanityError, match="row count"):
        run_sanity_checks(df)


def test_sanity_row_count_too_high_raises():
    df = _make_harmonized_df(n=200_000)  # way too high
    with pytest.raises(SanityError, match="row count"):
        run_sanity_checks(df)


# ---------------------------------------------------------------------------
# Wage plausibility
# ---------------------------------------------------------------------------

def test_sanity_wage_too_low_raises():
    df = _make_harmonized_df(55000)
    df["wage"] = 0.5   # obviously wrong (raw encoding not divided by 100 maybe)
    with pytest.raises(SanityError, match="median wage"):
        run_sanity_checks(df)


def test_sanity_wage_too_high_raises():
    df = _make_harmonized_df(55000)
    df["wage"] = 3100.0   # forgot to divide by 100
    with pytest.raises(SanityError, match="median wage"):
        run_sanity_checks(df)


# ---------------------------------------------------------------------------
# Employee share
# ---------------------------------------------------------------------------

def test_sanity_employee_share_too_low_raises():
    df = _make_harmonized_df(55000)
    with pytest.raises(SanityError, match="employee share"):
        # Total rows = 10 million -> share is 55000/10000000 = 0.55% (too low)
        run_sanity_checks(df, total_row_count=10_000_000)


def test_sanity_employee_share_too_high_raises():
    df = _make_harmonized_df(55000)
    with pytest.raises(SanityError, match="employee share"):
        # Total rows = 60000 -> share is 55000/60000 = 91.7% (too high)
        run_sanity_checks(df, total_row_count=60_000)


# ---------------------------------------------------------------------------
# Freshness
# ---------------------------------------------------------------------------

def test_sanity_freshness_stale_raises(tmp_path):
    df = _make_harmonized_df(55000)
    pq = tmp_path / "2024-01.parquet"
    pq.touch()
    _write_stale_meta(pq, days_old=200)
    with pytest.raises(SanityError, match="fetched .* days ago"):
        run_sanity_checks(df, parquet_path=pq)


def test_sanity_freshness_missing_meta_raises(tmp_path):
    df = _make_harmonized_df(55000)
    pq = tmp_path / "2026-04.parquet"
    pq.touch()
    # No meta.json written
    with pytest.raises(SanityError, match="meta.json sidecar missing"):
        run_sanity_checks(df, parquet_path=pq)


# ---------------------------------------------------------------------------
# All-null column
# ---------------------------------------------------------------------------

def test_sanity_all_null_column_raises():
    df = _make_harmonized_df(55000)
    df["gender"] = None
    with pytest.raises(SanityError, match="entirely null"):
        run_sanity_checks(df)
