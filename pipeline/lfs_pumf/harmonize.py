"""LFS PUMF harmonizer: raw parquet -> canonical regression-ready DataFrame.

Takes a raw parquet file (as produced by download.py) and applies all
transformations needed before the regression engine sees the data:

  1. Apply employee sample filter: lfsstat in {1,2} AND cowmain in {1,2}.
  2. Convert hrlyearn from raw integer (two decimals implied) to dollars.
  3. Bin tenure (months) into 5 ordered brackets.
  4. Rename all columns to canonical lowercase names matching REGRESSOR_COLS.
  5. Validate: no unexpected NaN in any regressor column; all categorical
     codes in known ranges.

Fail-closed: any missing required column or unmapped code raises ValueError
immediately. Silent coercion is not permitted — schema drift is the top risk.

Output schema (canonical column names):
  wage         float  - hourly wage in dollars (hrlyearn / 100)
  weight       float  - regression weight (finalwt)
  gender       int    - 1=Men+, 2=Women+
  age_12       int    - 5-year age group, codes 1-12
  educ         int    - education level, codes 0-6
  tenure_bin   str    - tenure bracket: '<12m','12-35m','36-59m','60-119m','120m+'
  noc_43       int    - occupation sub-major group, codes 1-43
  naics_21     int    - industry group, codes 1-21
  union_status int    - union status, codes 1-3
  ftptmain     int    - full/part-time, codes 1-2
  mjh          int    - multi-job holder, codes 1-2
  permtemp     int    - job permanency, codes 1-4
  marstat      int    - marital status, codes 1-6
  immig        int    - immigrant status, codes 1-3
  estsize      int    - establishment size, codes 1-4
  firmsize     int    - firm size (parallel to estsize, 4 levels), codes 1-4
                        (absent from parquets downloaded before Phase B; treated
                        as optional — harmonize() passes None-filled column when absent)
  prov         int    - province code (10-digit StatCan codes)
  cowmain_pub  int    - public(1)/private(2) sector flag (from cowmain filter var)
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Tenure bins (ordered)
# ---------------------------------------------------------------------------

# Bins defined in months. Bracket names are human-readable for decomposition
# output. The bin edges are [0, 12, 36, 60, 120, inf) producing labels below.
_TENURE_BINS = [0, 12, 36, 60, 120, float("inf")]
_TENURE_LABELS = ["<12m", "12-35m", "36-59m", "60-119m", "120m+"]

# ---------------------------------------------------------------------------
# Valid code ranges for validation (fail-closed)
# ---------------------------------------------------------------------------

_VALID_CODES: dict[str, set] = {
    "gender":       {1, 2},
    "age_12":       set(range(1, 13)),        # 1-12
    "educ":         set(range(0, 7)),         # 0-6
    "noc_43":       set(range(1, 44)),        # 1-43
    "naics_21":     set(range(1, 22)),        # 1-21
    "union_status": {1, 2, 3},
    "ftptmain":     {1, 2},
    "mjh":          {1, 2},
    "permtemp":     {1, 2, 3, 4},
    "marstat":      set(range(1, 7)),         # 1-6
    "immig":        {1, 2, 3},
    "estsize":      {1, 2, 3, 4},
    # firmsize: same 4-level scale as estsize (1=<20, 2=20-99, 3=100-500, 4=>500)
    # but measured at the firm rather than establishment level. Codes from PUMF codebook.
    "firmsize":     {1, 2, 3, 4},
    "prov":         {10, 11, 12, 13, 24, 35, 46, 47, 48, 59},
    "cowmain_pub":  {1, 2},
}

# ---------------------------------------------------------------------------
# Required source columns (fail-closed if absent)
# ---------------------------------------------------------------------------

_REQUIRED_SOURCE_COLS = [
    "hrlyearn", "finalwt", "lfsstat", "cowmain", "gender", "age_12",
    "educ", "tenure", "noc_43", "naics_21", "union", "ftptmain", "mjh",
    "permtemp", "marstat", "immig", "estsize", "prov",
    # firmsize is optional: PUMF parquets on disk before Phase B re-download
    # will not contain it. harmonize() handles its absence gracefully.
    # "firmsize",  -- NOT added to required; handled in _transform_columns
]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def harmonize(
    parquet_path: Path,
    validate_codes: bool = True,
) -> pd.DataFrame:
    """Load a raw PUMF parquet and return the canonical regression DataFrame.

    Args:
        parquet_path:   Path to the .parquet file produced by download.py.
        validate_codes: If True (default), validate that all category codes
                        are within known ranges. Set False only in tests that
                        exercise synthetic data with non-real codes.

    Returns:
        DataFrame with canonical schema (see module docstring). Only the
        paid-employee regression sample is returned (lfsstat in {1,2},
        cowmain in {1,2}, hrlyearn > 0).

    Raises:
        ValueError: On any missing required column, unexpected NaN in a
                    regressor, or unmapped category code.
        RuntimeError: If the parquet filename implies a YYYY-MM but the
                      embedded survyear/survmnth does not match (corrupt cache).
    """
    df = pd.read_parquet(parquet_path, engine="pyarrow")
    df.columns = df.columns.str.lower()

    # Validate survyear/survmnth against the filename to catch cache corruption.
    # This re-runs the same check that download.py performs at download time,
    # catching parquets that were written before the validation existed.
    # Injected parquets (via --zip escape hatch) intentionally skip the check
    # at injection time; they still carry correct survyear/survmnth in practice,
    # but if they don't, raise with a message pointing at the injection.
    stem = parquet_path.stem  # e.g. "2024-06"
    if len(stem) == 7 and stem[4] == "-":
        try:
            expected_year = int(stem[:4])
            expected_month = int(stem[5:7])
            _validate_survyear_survmnth_on_read(df, expected_year, expected_month, parquet_path)
        except (ValueError, IndexError):
            pass  # non-YYYY-MM filename (e.g. test fixtures) — skip

    _check_required_columns(df)
    df = _apply_employee_filter(df)
    df = _transform_columns(df)
    _check_no_nulls(df)
    if validate_codes:
        _check_code_ranges(df)

    return df


def harmonize_df(
    raw_df: pd.DataFrame,
    validate_codes: bool = True,
) -> pd.DataFrame:
    """Same as harmonize() but accepts a DataFrame directly (for testing).

    Column names are normalized to lowercase before processing.
    """
    df = raw_df.copy()
    df.columns = df.columns.str.lower()

    _check_required_columns(df)
    df = _apply_employee_filter(df)
    df = _transform_columns(df)
    _check_no_nulls(df)
    if validate_codes:
        _check_code_ranges(df)

    return df


# ---------------------------------------------------------------------------
# Internal steps
# ---------------------------------------------------------------------------

def _check_required_columns(df: pd.DataFrame) -> None:
    """Raise ValueError if any required source column is absent."""
    missing = [c for c in _REQUIRED_SOURCE_COLS if c not in df.columns]
    if missing:
        raise ValueError(
            f"PUMF harmonize: required columns absent from parquet — {missing}.\n"
            "This indicates schema drift in the StatCan PUMF. "
            "Update harmonize.py to reflect the new column names."
        )


def _apply_employee_filter(df: pd.DataFrame) -> pd.DataFrame:
    """Retain only paid employees with positive hourly earnings.

    Filter:
      lfsstat in {1, 2}   (employed at work or employed absent)
      cowmain in {1, 2}   (public or private sector paid employee)
      hrlyearn > 0        (positive wage required for log transform)
    """
    mask = (
        df["lfsstat"].isin({1, 2})
        & df["cowmain"].isin({1, 2})
        & (df["hrlyearn"] > 0)
    )
    result = df.loc[mask].copy()
    if result.empty:
        raise ValueError(
            "PUMF employee filter returned an empty DataFrame. "
            "lfsstat/cowmain/hrlyearn encodings may have changed."
        )
    return result


def _bin_tenure(tenure_months: pd.Series) -> pd.Categorical:
    """Bin continuous tenure (months 1-240) into 5 ordered brackets.

    Bracket edges: [0, 12, 36, 60, 120, inf)
    Labels: '<12m', '12-35m', '36-59m', '60-119m', '120m+'
    """
    binned = pd.cut(
        tenure_months,
        bins=_TENURE_BINS,
        labels=_TENURE_LABELS,
        right=False,   # intervals are [left, right)
        include_lowest=True,
    )
    return binned


def _transform_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Apply all column transforms and renaming to produce the canonical schema."""
    out = pd.DataFrame()

    # Wage: divide by 100 (two decimals implied)
    out["wage"] = df["hrlyearn"] / 100.0

    # Weight
    out["weight"] = df["finalwt"].astype(float)

    # Gender (pass through; already 1/2 in all hist/ vintages)
    out["gender"] = df["gender"].astype(int)

    # Age group
    out["age_12"] = df["age_12"].astype(int)

    # Education
    out["educ"] = df["educ"].astype(int)

    # Tenure: bin continuous months into brackets
    out["tenure_bin"] = _bin_tenure(df["tenure"])

    # Occupation (43-group only — NOC_10 excluded to avoid rank deficiency)
    out["noc_43"] = df["noc_43"].astype(int)

    # Industry
    out["naics_21"] = df["naics_21"].astype(int)

    # Union status (renamed from 'union' to avoid shadowing Python built-in)
    out["union_status"] = df["union"].astype(int)

    # Full/part-time
    out["ftptmain"] = df["ftptmain"].astype(int)

    # Multi-job holder
    out["mjh"] = df["mjh"].astype(int)

    # Job permanency
    out["permtemp"] = df["permtemp"].astype(int)

    # Marital status
    out["marstat"] = df["marstat"].astype(int)

    # Immigrant status
    out["immig"] = df["immig"].astype(int)

    # Establishment size
    out["estsize"] = df["estsize"].astype(int)

    # Firm size (Phase B: BoC SAN 2024-23 covariate).
    # Optional: parquets downloaded before Phase B re-download do not contain
    # firmsize. Rows where firmsize is NaN are silently excluded from the
    # regression by _prepare_categoricals (NaN rows don't match any category).
    # After re-download this column will be populated for all paid employees.
    if "firmsize" in df.columns:
        # firmsize may be NaN for some employees (blank in PUMF = not applicable)
        # Cast to nullable Int64 to preserve NaN, then astype int drops NaN rows
        # via the regression filter. Store as object to allow NaN.
        out["firmsize"] = pd.to_numeric(df["firmsize"], errors="coerce")
    else:
        # Column absent (old parquet): fill with NaN so downstream code can
        # detect its absence and skip it in category universe building.
        out["firmsize"] = float("nan")

    # Province
    out["prov"] = df["prov"].astype(int)

    # Public/private sector (from cowmain, already filtered to {1,2})
    out["cowmain_pub"] = df["cowmain"].astype(int)

    return out.reset_index(drop=True)


def _check_no_nulls(df: pd.DataFrame) -> None:
    """Raise ValueError if any required regressor column contains NaN.

    The spike confirmed zero missing among paid employees. If NaN appears,
    the employee filter or an encoding change has introduced a problem.

    Exemption: 'firmsize' is optional (absent from parquets downloaded before
    Phase B re-download). NaN in firmsize is expected and allowed here; the
    regression engine handles it by treating any NaN-firmsize row as having
    no firmsize category, so those rows are excluded from the firmsize dummy
    block but still contribute to all other regressors.
    """
    # firmsize is optional — allow NaN
    _OPTIONAL_NULLABLE = {"firmsize"}
    null_cols = [
        c for c in df.columns
        if df[c].isna().any() and c not in _OPTIONAL_NULLABLE
    ]
    if null_cols:
        counts = {c: int(df[c].isna().sum()) for c in null_cols}
        raise ValueError(
            f"PUMF harmonize: unexpected NaN in regression columns after "
            f"employee filter — {counts}. "
            "Check lfsstat/cowmain filter and PUMF encoding."
        )


def _validate_survyear_survmnth_on_read(
    df: pd.DataFrame,
    expected_year: int,
    expected_month: int,
    parquet_path: Path,
) -> None:
    """Fail-closed: survyear/survmnth embedded in the parquet must match YYYY-MM filename.

    Called by harmonize() on every parquet read to catch cache corruption that
    survived the original download-time check (e.g. parquets written before
    _validate_survyear_survmnth was added, or manually injected files with the
    wrong content).

    Raises:
        RuntimeError: if the embedded survey period does not match the filename.
    """
    if "survyear" not in df.columns or "survmnth" not in df.columns:
        # Cannot validate — old PUMF format or test fixture without these fields.
        return

    actual_years = df["survyear"].dropna().unique().tolist()
    actual_months = df["survmnth"].dropna().unique().tolist()

    year_ok = len(actual_years) == 1 and int(actual_years[0]) == expected_year
    month_ok = len(actual_months) == 1 and int(actual_months[0]) == expected_month

    if not (year_ok and month_ok):
        raise RuntimeError(
            f"PUMF cache integrity check failed for {parquet_path.name}.\n"
            f"  Expected survyear={expected_year} survmnth={expected_month} "
            f"(from filename {parquet_path.stem}).\n"
            f"  Got survyear={actual_years} survmnth={actual_months}.\n"
            f"This parquet contains wrong-month data. Delete it and re-run to "
            f"force a re-download:\n"
            f"  del \"{parquet_path}\"\n"
            f"If this was a manually injected file (--zip), the injected zip "
            f"must contain data matching the target YYYY-MM."
        )


def _check_code_ranges(df: pd.DataFrame) -> None:
    """Raise ValueError if any integer column contains an out-of-range code.

    Unmapped codes indicate either a category expansion (new group added
    by StatCan) or a misread encoding. Either requires a human to extend
    the codebook in harmonize.py before the pipeline continues.
    """
    for col, valid_set in _VALID_CODES.items():
        if col not in df.columns:
            continue
        if col == "tenure_bin":
            # Categorical — handled separately
            continue
        actual_codes = set(df[col].dropna().unique())
        unknown = actual_codes - valid_set
        if unknown:
            raise ValueError(
                f"PUMF harmonize: column '{col}' contains unknown codes {sorted(unknown)}. "
                f"Expected codes in {sorted(valid_set)}. "
                "StatCan may have added a new category. Update _VALID_CODES in harmonize.py."
            )
