"""Tests for pipeline.lfs_pumf.harmonize.

Tests fail-closed behavior on missing columns, bad codes, and NaN.
Uses harmonize_df() (accepts DataFrame directly) to avoid needing parquet files.
Also tests harmonize() (reads from parquet) for survyear/survmnth validation.
"""

from __future__ import annotations

import pandas as pd
import pytest

from pipeline.lfs_pumf.harmonize import (
    harmonize_df,
    _REQUIRED_SOURCE_COLS,
    _validate_survyear_survmnth_on_read,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_valid_row(n: int = 100) -> pd.DataFrame:
    """Return a DataFrame with n valid rows (all paid employees, no missing)."""
    rows = []
    for i in range(n):
        rows.append({
            "survyear": 2026, "survmnth": 4,
            "lfsstat": 1 if i % 2 == 0 else 2,
            "cowmain": 1 if i % 3 == 0 else 2,
            "hrlyearn": 3100,
            "finalwt": 500,
            "gender": 1 if i % 2 == 0 else 2,
            "age_12": (i % 12) + 1,
            "educ": i % 7,
            "tenure": (i % 240) + 1,
            "noc_43": (i % 43) + 1,
            "naics_21": (i % 21) + 1,
            "union": (i % 3) + 1,
            "ftptmain": 1,
            "mjh": 1,
            "permtemp": 1,
            "marstat": (i % 6) + 1,
            "immig": (i % 3) + 1,
            "estsize": (i % 4) + 1,
            "prov": [10, 11, 12, 13, 24, 35, 46, 47, 48, 59][i % 10],
        })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------

def test_harmonize_df_happy_path():
    """Valid DataFrame produces canonical schema with correct column names."""
    df = _make_valid_row(100)
    result = harmonize_df(df)

    expected_cols = {
        "wage", "weight", "gender", "age_12", "educ", "tenure_bin",
        "noc_43", "naics_21", "union_status", "ftptmain", "mjh",
        "permtemp", "marstat", "immig", "estsize", "prov", "cowmain_pub",
    }
    assert expected_cols.issubset(set(result.columns))
    assert len(result) > 0
    assert (result["wage"] > 0).all()


def test_harmonize_df_wage_conversion():
    """hrlyearn raw 3100 -> wage $31.00 (divide by 100)."""
    df = _make_valid_row(10)
    df["hrlyearn"] = 3100
    result = harmonize_df(df)
    assert (result["wage"] == 31.0).all()


def test_harmonize_df_employee_filter():
    """Only lfsstat in {1,2} AND cowmain in {1,2} rows survive."""
    df = _make_valid_row(10)
    # Add non-employee rows
    non_emp = df.iloc[0:1].copy()
    non_emp["lfsstat"] = 3   # unemployed
    non_emp["cowmain"] = 5   # self-employed
    df = pd.concat([df, non_emp], ignore_index=True)
    result = harmonize_df(df)
    # Non-employee rows must not appear; only the original 10 employees survive
    assert len(result) == 10


def test_harmonize_df_tenure_bins():
    """TENURE values are correctly binned into 5 brackets."""
    df = _make_valid_row(5)
    df["tenure"] = [1, 12, 36, 60, 120]
    result = harmonize_df(df, validate_codes=False)
    # tenure bin labels from harmonize._TENURE_LABELS
    expected = ["<12m", "12-35m", "36-59m", "60-119m", "120m+"]
    assert list(result["tenure_bin"]) == expected


# ---------------------------------------------------------------------------
# Fail-closed: missing columns
# ---------------------------------------------------------------------------

def test_harmonize_df_missing_column_raises():
    """Missing required column raises ValueError immediately."""
    df = _make_valid_row(10)
    df = df.drop(columns=["noc_43"])
    with pytest.raises(ValueError, match="required columns absent"):
        harmonize_df(df)


def test_harmonize_df_missing_hrlyearn_raises():
    """Missing hrlyearn (the key wage variable) raises ValueError."""
    df = _make_valid_row(10)
    df = df.drop(columns=["hrlyearn"])
    with pytest.raises(ValueError, match="required columns absent"):
        harmonize_df(df)


# ---------------------------------------------------------------------------
# Fail-closed: bad codes
# ---------------------------------------------------------------------------

def test_harmonize_df_unknown_gender_code_raises():
    """Unknown gender code (e.g. 9) raises ValueError on validation."""
    df = _make_valid_row(10)
    df.loc[0, "gender"] = 9  # not in {1, 2}
    with pytest.raises(ValueError, match="unknown codes"):
        harmonize_df(df)


def test_harmonize_df_unknown_prov_code_raises():
    """Unknown province code (e.g. 99) raises ValueError on validation."""
    df = _make_valid_row(10)
    df.loc[0, "prov"] = 99
    with pytest.raises(ValueError, match="unknown codes"):
        harmonize_df(df)


def test_harmonize_df_unknown_noc_raises():
    """NOC_43 code outside 1-43 raises ValueError."""
    df = _make_valid_row(10)
    df.loc[0, "noc_43"] = 50
    with pytest.raises(ValueError, match="unknown codes"):
        harmonize_df(df)


# ---------------------------------------------------------------------------
# Fail-closed: empty sample
# ---------------------------------------------------------------------------

def test_harmonize_df_empty_employee_sample_raises():
    """If all rows are filtered out (no employees), raise ValueError."""
    df = _make_valid_row(10)
    df["lfsstat"] = 3   # all unemployed
    with pytest.raises(ValueError, match="empty DataFrame"):
        harmonize_df(df)


# ---------------------------------------------------------------------------
# Case insensitivity
# ---------------------------------------------------------------------------

def test_harmonize_df_uppercase_columns_normalized():
    """Column names are normalized to lowercase before processing."""
    df = _make_valid_row(10)
    df.columns = df.columns.str.upper()
    result = harmonize_df(df)
    assert len(result) > 0
    assert "wage" in result.columns


# ---------------------------------------------------------------------------
# Phase A item 2: survyear/survmnth validation on read (harmonize path)
# ---------------------------------------------------------------------------

def test_validate_survyear_survmnth_on_read_passes_when_correct(tmp_path):
    """No exception when survyear/survmnth match the expected year/month."""
    df = _make_valid_row(10)
    df["survyear"] = 2024
    df["survmnth"] = 6
    # Should not raise
    from pathlib import Path
    _validate_survyear_survmnth_on_read(df, 2024, 6, Path(tmp_path / "2024-06.parquet"))


def test_validate_survyear_survmnth_on_read_raises_on_mismatch(tmp_path):
    """RuntimeError raised when survyear/survmnth disagree with filename."""
    df = _make_valid_row(10)
    df["survyear"] = 2026  # wrong year
    df["survmnth"] = 4     # wrong month
    from pathlib import Path
    with pytest.raises(RuntimeError, match="cache integrity check failed"):
        _validate_survyear_survmnth_on_read(df, 2024, 6, Path(tmp_path / "2024-06.parquet"))


def test_validate_survyear_survmnth_on_read_skips_when_cols_absent(tmp_path):
    """No exception when survyear/survmnth columns are absent (old format)."""
    df = _make_valid_row(10).drop(columns=["survyear", "survmnth"], errors="ignore")
    from pathlib import Path
    # Should not raise
    _validate_survyear_survmnth_on_read(df, 2024, 6, Path(tmp_path / "2024-06.parquet"))


def test_harmonize_parquet_raises_on_survyear_mismatch(tmp_path):
    """harmonize() raises RuntimeError if parquet filename vs survyear/survmnth disagree."""
    from pipeline.lfs_pumf.harmonize import harmonize
    from pathlib import Path

    df = _make_valid_row(100)
    # Set survyear/survmnth to April 2026 (wrong for a 2024-06 parquet)
    df["survyear"] = 2026
    df["survmnth"] = 4

    parquet_path = tmp_path / "2024-06.parquet"
    df.to_parquet(parquet_path, index=False, engine="pyarrow")

    with pytest.raises(RuntimeError, match="cache integrity check failed"):
        harmonize(parquet_path, validate_codes=False)
