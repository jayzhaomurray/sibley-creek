"""Tests for pipeline.lfs_micro.engine.

End-to-end test on synthetic fixture DataFrames with known composition shifts.
Verifies:
  - Output columns present
  - y/y months correctly computed (12-month offset)
  - Smoothing (ma3) applied correctly
  - Missing base month skipped gracefully
  - Known composition shift produces correct sign
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from pipeline.lfs_micro.engine import run_engine, _subtract_12_months
from pipeline.lfs_micro.spec import Spec


# ---------------------------------------------------------------------------
# Helper: synthetic harmonized DataFrame
# ---------------------------------------------------------------------------

def _make_df(n: int = 300, seed: int = 42, wage_premium: float = 0.0) -> pd.DataFrame:
    """Synthetic harmonized DataFrame for the engine.

    wage_premium: additional log-wage premium (to test sign of composition/underlying).
    """
    rng = np.random.default_rng(seed)
    wage = np.exp(rng.normal(np.log(30) + wage_premium, 0.4, n))
    return pd.DataFrame({
        "wage":         wage,
        "weight":       rng.integers(100, 2000, n).astype(float),
        "gender":       rng.choice([1, 2], n),
        "age_12":       rng.choice(range(1, 13), n),
        "educ":         rng.choice(range(0, 7), n),
        "tenure_bin":   rng.choice(["<12m", "12-35m", "36-59m", "60-119m", "120m+"], n),
        "noc_43":       rng.choice(range(1, 6), n),   # small universe
        "naics_21":     rng.choice(range(1, 5), n),
        "union_status": rng.choice([1, 2, 3], n),
        "ftptmain":     rng.choice([1, 2], n),
        "mjh":          rng.choice([1, 2], n),
        "permtemp":     rng.choice([1, 2, 3, 4], n),
        "marstat":      rng.choice(range(1, 7), n),
        "immig":        rng.choice([1, 2, 3], n),
        "estsize":      rng.choice([1, 2, 3, 4], n),
        "prov":         rng.choice([10, 24, 35, 48, 59], n),
        "cowmain_pub":  rng.choice([1, 2], n),
    })


# ---------------------------------------------------------------------------
# _subtract_12_months
# ---------------------------------------------------------------------------

def test_subtract_12_months_basic():
    assert _subtract_12_months("2026-04") == "2025-04"


def test_subtract_12_months_year_boundary():
    assert _subtract_12_months("2026-01") == "2025-01"


def test_subtract_12_months_december():
    assert _subtract_12_months("2025-12") == "2024-12"


# ---------------------------------------------------------------------------
# run_engine: output structure
# ---------------------------------------------------------------------------

def test_run_engine_output_columns():
    """run_engine returns a DataFrame with the expected core columns."""
    # Build 14 months: 2025-01 through 2026-02 (gives 2 y/y obs: Jan/Feb 2026)
    frames = {}
    for y in [2025, 2026]:
        months = range(1, 13) if y == 2025 else range(1, 3)
        for m in months:
            frames[f"{y:04d}-{m:02d}"] = _make_df(200, seed=y * 100 + m)

    spec = Spec(weighted=False, smoothing="raw", ob_reference="base", min_cell_count=5)
    result = run_engine(frames, spec=spec)

    assert not result.empty
    expected_cols = {
        "date", "underlying_lp", "composition_lp",
        "raw_mean_lp", "total_fitted_lp",
        "underlying_pct", "composition_pct",
        "n_obs_curr", "n_obs_base", "r2_curr", "r2_base",
    }
    assert expected_cols.issubset(set(result.columns))


def test_run_engine_date_column_format():
    """Date column values are ISO date strings (YYYY-MM-01)."""
    frames = {}
    for y in [2025, 2026]:
        for m in range(1, 4):
            frames[f"{y:04d}-{m:02d}"] = _make_df(200, seed=y * 100 + m)

    spec = Spec(weighted=False, smoothing="raw", min_cell_count=5)
    result = run_engine(frames, spec=spec)

    for d in result["date"]:
        assert d.endswith("-01"), f"Date '{d}' does not end in -01"
        year, month, day = d.split("-")
        assert 2015 <= int(year) <= 2030
        assert 1 <= int(month) <= 12


def test_run_engine_skips_missing_base_month():
    """Months without a base 12 months prior are silently skipped."""
    # Only 3 months of data — no y/y pairs possible
    frames = {
        "2026-01": _make_df(200, seed=1),
        "2026-02": _make_df(200, seed=2),
        "2026-03": _make_df(200, seed=3),
    }
    spec = Spec(weighted=False, smoothing="raw", min_cell_count=5)
    result = run_engine(frames, spec=spec)
    assert result.empty


def test_run_engine_empty_input():
    """Empty frames dict returns empty DataFrame."""
    result = run_engine({}, Spec(weighted=False, smoothing="raw", min_cell_count=5))
    assert result.empty


# ---------------------------------------------------------------------------
# run_engine: smoothing
# ---------------------------------------------------------------------------

def test_run_engine_ma3_produces_nan_at_edges():
    """MA3 smoothing produces NaN at the first and last observation (edge effect)."""
    # Build 15 months to produce 3 y/y obs; MA3 needs >=3 to produce a non-NaN
    frames = {}
    for y in [2025, 2026]:
        months = range(1, 13) if y == 2025 else range(1, 4)
        for m in months:
            frames[f"{y:04d}-{m:02d}"] = _make_df(200, seed=y * 100 + m)

    spec = Spec(weighted=False, smoothing="ma3", min_cell_count=5)
    result = run_engine(frames, spec=spec)

    # With 3 y/y obs, MA3 (center) produces NaN for the first and last rows
    assert result["underlying_lp"].isna().sum() == 2  # first + last
    assert result["underlying_lp"].notna().sum() == 1  # only the middle


def test_run_engine_raw_no_nan_at_edges():
    """Raw smoothing does not introduce NaN at the edges."""
    frames = {}
    for y in [2025, 2026]:
        months = range(1, 13) if y == 2025 else range(1, 4)
        for m in months:
            frames[f"{y:04d}-{m:02d}"] = _make_df(200, seed=y * 100 + m)

    spec = Spec(weighted=False, smoothing="raw", min_cell_count=5)
    result = run_engine(frames, spec=spec)
    assert result["underlying_lp"].notna().all()


# ---------------------------------------------------------------------------
# run_engine: log-point to percent conversion
# ---------------------------------------------------------------------------

def test_run_engine_pct_conversion():
    """underlying_pct = (exp(underlying_lp) - 1) * 100."""
    frames = {}
    for y in [2025, 2026]:
        months = range(1, 13) if y == 2025 else range(1, 3)
        for m in months:
            frames[f"{y:04d}-{m:02d}"] = _make_df(300, seed=y * 100 + m)

    spec = Spec(weighted=False, smoothing="raw", min_cell_count=5)
    result = run_engine(frames, spec=spec)

    for _, row in result.iterrows():
        expected = (np.exp(row["underlying_lp"]) - 1.0) * 100.0
        assert abs(row["underlying_pct"] - expected) < 1e-10


# ---------------------------------------------------------------------------
# run_engine: ob_reference convention both work
# ---------------------------------------------------------------------------

def test_run_engine_both_reference_conventions_run():
    """Both 'base' and 'current' ob_reference produce valid results."""
    frames = {}
    for y in [2025, 2026]:
        months = range(1, 13) if y == 2025 else range(1, 3)
        for m in months:
            frames[f"{y:04d}-{m:02d}"] = _make_df(200, seed=y * 100 + m)

    for ref in ("base", "current"):
        spec = Spec(weighted=False, smoothing="raw", ob_reference=ref, min_cell_count=5)
        result = run_engine(frames, spec=spec)
        assert not result.empty, f"Empty result for ob_reference='{ref}'"
