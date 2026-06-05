"""LFS PUMF sanity gate.

Automated quality checks run after harmonize.py produces the canonical
DataFrame. Fail-closed: any check that fails raises SanityError with an
explicit message — the pipeline stops rather than silently passing garbage
downstream.

Checks:
  1. Row count: 90k-115k employees expected (spike: 55,933 paid employees
     from 112,707 total; typical range 90k-115k total sample for normal
     survey months; COVID disruption months (2020-2021) may be 80k+).
     The check is on the PAID EMPLOYEE count after filtering.
  2. Employee share: paid employees / total respondents should be ~35-55%
     (spike: 55,933/112,707 = 49.6%).
  3. No all-null regressor: each canonical column must have at least one
     non-null value (redundant with harmonize null check, but explicit).
  4. Wage plausibility: median wage should be between $10 and $200/hr.
  5. Weight sum plausibility: sum of weights should be > 1 million
     (roughly represents the Canadian paid employee population, ~19M).
  6. Vintage freshness: the parquet's meta.json must have been fetched within
     the last 180 days (prevents building on stale/unreplaced data).
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import pandas as pd


class SanityError(Exception):
    """Raised when the PUMF fails an automated sanity check."""
    pass


# ---------------------------------------------------------------------------
# Thresholds
# ---------------------------------------------------------------------------

_MIN_PAID_EMPLOYEE_ROWS = 30_000   # COVID lockdown lows (Apr-May 2020: ~37k); spike normal: 55k
_MAX_PAID_EMPLOYEE_ROWS = 120_000  # headroom for sample expansion
_MIN_EMPLOYEE_SHARE = 0.30
_MAX_EMPLOYEE_SHARE = 0.70
_MIN_MEDIAN_WAGE = 10.0    # dollars/hr
_MAX_MEDIAN_WAGE = 200.0   # dollars/hr
_MIN_WEIGHT_SUM = 5_000_000   # 5M — conservative (paid emp ~18-19M weighted)
_MAX_FRESHNESS_DAYS = 180


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def run_sanity_checks(
    harmonized_df: pd.DataFrame,
    parquet_path: Optional[Path] = None,
    total_row_count: Optional[int] = None,
) -> None:
    """Run all sanity checks on the harmonized paid-employee DataFrame.

    Args:
        harmonized_df:   Output of harmonize.harmonize() (paid employees only).
        parquet_path:    Path to the .parquet file, used to read meta.json for
                         freshness check. Skip if None.
        total_row_count: Total rows in the full PUMF file (before employee filter),
                         used for employee-share check. Skip if None.

    Raises:
        SanityError: On any failed check with a description of what failed.
    """
    _check_row_count(harmonized_df)
    _check_no_all_null(harmonized_df)
    _check_wage_plausibility(harmonized_df)
    _check_weight_sum(harmonized_df)

    if total_row_count is not None:
        _check_employee_share(harmonized_df, total_row_count)

    if parquet_path is not None:
        _check_freshness(parquet_path)


# ---------------------------------------------------------------------------
# Individual checks
# ---------------------------------------------------------------------------

def _check_row_count(df: pd.DataFrame) -> None:
    n = len(df)
    if not (_MIN_PAID_EMPLOYEE_ROWS <= n <= _MAX_PAID_EMPLOYEE_ROWS):
        raise SanityError(
            f"PUMF sanity: paid employee row count {n:,} is outside expected range "
            f"[{_MIN_PAID_EMPLOYEE_ROWS:,}, {_MAX_PAID_EMPLOYEE_ROWS:,}]. "
            "Check employee filter or StatCan sample design change."
        )


def _check_no_all_null(df: pd.DataFrame) -> None:
    all_null = [c for c in df.columns if df[c].isna().all()]
    if all_null:
        raise SanityError(
            f"PUMF sanity: columns are entirely null after harmonization — {all_null}. "
            "Employee filter or column mapping may be broken."
        )


def _check_wage_plausibility(df: pd.DataFrame) -> None:
    if "wage" not in df.columns:
        raise SanityError("PUMF sanity: 'wage' column missing from harmonized DataFrame.")
    median_wage = float(df["wage"].median())
    if not (_MIN_MEDIAN_WAGE <= median_wage <= _MAX_MEDIAN_WAGE):
        raise SanityError(
            f"PUMF sanity: median wage ${median_wage:.2f}/hr is outside plausible range "
            f"[${_MIN_MEDIAN_WAGE}, ${_MAX_MEDIAN_WAGE}]. "
            "hrlyearn encoding (divide-by-100) may be wrong or sample filter broken."
        )


def _check_weight_sum(df: pd.DataFrame) -> None:
    if "weight" not in df.columns:
        raise SanityError("PUMF sanity: 'weight' column missing from harmonized DataFrame.")
    wt_sum = float(df["weight"].sum())
    if wt_sum < _MIN_WEIGHT_SUM:
        raise SanityError(
            f"PUMF sanity: sum of weights {wt_sum:,.0f} is below {_MIN_WEIGHT_SUM:,}. "
            "Weight column or employee filter may be misspecified."
        )


def _check_employee_share(df: pd.DataFrame, total_rows: int) -> None:
    share = len(df) / total_rows
    if not (_MIN_EMPLOYEE_SHARE <= share <= _MAX_EMPLOYEE_SHARE):
        raise SanityError(
            f"PUMF sanity: paid employee share {share:.1%} (={len(df):,}/{total_rows:,}) "
            f"is outside expected range [{_MIN_EMPLOYEE_SHARE:.0%}, {_MAX_EMPLOYEE_SHARE:.0%}]. "
            "lfsstat or cowmain filter may be incorrect."
        )


def _check_freshness(parquet_path: Path) -> None:
    meta_path = parquet_path.with_suffix(".meta.json")
    if not meta_path.exists():
        raise SanityError(
            f"PUMF sanity: meta.json sidecar missing at {meta_path}. "
            "Run download.get_month() to regenerate."
        )
    meta = json.loads(meta_path.read_text())
    fetched_at_str = meta.get("fetched_at", "")
    if not fetched_at_str:
        raise SanityError(
            "PUMF sanity: meta.json missing 'fetched_at' timestamp. "
            "Parquet may have been written by a non-pipeline process."
        )
    try:
        fetched_at = datetime.fromisoformat(fetched_at_str)
        if fetched_at.tzinfo is None:
            fetched_at = fetched_at.replace(tzinfo=timezone.utc)
    except ValueError:
        raise SanityError(
            f"PUMF sanity: could not parse fetched_at timestamp '{fetched_at_str}'."
        )
    age_days = (datetime.now(timezone.utc) - fetched_at).days
    if age_days > _MAX_FRESHNESS_DAYS:
        raise SanityError(
            f"PUMF sanity: parquet for {parquet_path.stem} was fetched {age_days} days ago "
            f"(limit: {_MAX_FRESHNESS_DAYS} days). "
            "Re-run download.get_month(..., force=True) to refresh."
        )
