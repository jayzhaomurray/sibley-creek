"""Department of Finance Fiscal Monitor scraper.

The Fiscal Monitor is published monthly with ~2-month lag at predictable URLs:
    https://www.canada.ca/en/department-finance/services/publications/fiscal-monitor/{YYYY}/{MM}.html

Each issue carries ~10 HTML tables covering monthly budgetary balance, fiscal-
year-to-date balance, revenues + expenses with year-over-year change, financial
source/requirement, and the federal debt summary. Per dashboard_purpose section
4.5b element F1, we surface: federal deficit YTD, public debt charges, revenues,
expenses, all for the most recent reference period.

Publication conventions:
    - Federal fiscal year runs April-to-March. "April to February" YTD on the
      Feb-2026 issue covers April 2025 through February 2026 (fiscal year 2025-26).
    - Figures are in C$ millions throughout; we preserve millions in the CSV
      (charts can rescale to billions for display).
    - Prior-year comparator column is always present; both years are kept.
    - Some FY-end revisions: each Public Accounts release (typically Dec for
      the prior fiscal year) restates the year. Fiscal Monitor revises the
      prior 1-2 months at each issue as accruals settle.

Source quirks:
    - The Fiscal Monitor HTML uses two- and three-level row headers nested in
      the same column ("Tax revenues" header rows are tbody-level group labels,
      not data). We detect and drop them as rows where the value columns are
      all NaN or all identical to the header label.
    - February-month files sometimes carry a one-row footnote about strike or
      legislative-anomaly adjustments; we capture this in the `notes` field of
      the .meta.json sidecar.
    - The page sometimes shows tables with column-header colspans causing
      pandas.read_html to emit MultiIndex columns. The parser below flattens
      them to a single row with predictable names.
"""

from __future__ import annotations

import io
import logging
import re
from dataclasses import dataclass
from datetime import date
from typing import Optional

import pandas as pd

from pipeline.fetch._http import get_client

BASE_URL = "https://www.canada.ca/en/department-finance/services/publications/fiscal-monitor"

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class FiscalMonitorIssue:
    """One issue of the Fiscal Monitor, identified by its reference period.

    `reference_year` and `reference_month` are the calendar year and month the
    issue covers (e.g. 2026, 2; the Feb-2026 issue, published around late
    April 2026 with data through February 2026).

    `fiscal_year_label` is the federal FY this issue's YTD column belongs to
    (e.g. "2025-26" for the FY running April 2025 to March 2026).
    """

    reference_year: int
    reference_month: int
    url: str
    fiscal_year_label: str
    # Headline series, in CAD millions, parsed from the page tables:
    monthly_balance: pd.DataFrame      # date, value (monthly budgetary balance, current FY only)
    ytd_balance: pd.DataFrame          # date, value (fiscal-YTD balance through this issue, current FY)
    # Two-FY continuous monthly balance: prior-FY (full 12 months) + current-FY (months
    # reported so far). Built from the same monthly-balance HTML table as `monthly_balance`,
    # but pulls BOTH prior- and current-FY columns to give a continuous ~12-24 month
    # series suitable for a sparkline / supporting print. CAD millions.
    monthly_balance_two_fy: pd.DataFrame
    revenues_ytd: Optional[float]      # FY-YTD revenues, C$ millions
    expenses_ytd: Optional[float]      # FY-YTD expenses, C$ millions
    public_debt_charges_ytd: Optional[float]  # FY-YTD public debt charges, C$ millions
    raw_tables: list[pd.DataFrame]     # all parsed tables, for downstream inspection / fact-check


def latest_issue_url(today: Optional[date] = None) -> str:
    """Return the candidate URL for the issue most likely to be the latest.

    Fiscal Monitor is typically published 8-10 weeks after the reference
    month closes. By a given date D, the most-recent CANDIDATE issue is the
    one ~2 months prior to D. Caller should fall back via
    `find_available_issue()` if the candidate 404s.
    """
    today = today or date.today()
    ref = pd.Timestamp(today) - pd.DateOffset(months=2)
    return f"{BASE_URL}/{ref.year}/{ref.month:02d}.html"


def find_available_issue(
    today: Optional[date] = None, *, lookback_months: int = 6
) -> tuple[bytes, int, int]:
    """Walk back from the candidate latest URL to find the first 200-OK issue.

    Returns (response_bytes, reference_year, reference_month).
    """
    today = today or date.today()
    tried: list[str] = []
    last_status = None
    with get_client(headers={"User-Agent": "Mozilla/5.0 macro-research-department"}) as client:
        for offset in range(2, 2 + lookback_months + 1):
            ref = pd.Timestamp(today) - pd.DateOffset(months=offset)
            url = f"{BASE_URL}/{ref.year}/{ref.month:02d}.html"
            tried.append(url)
            r = client.get(url)
            if r.status_code == 200:
                logger.info("Fiscal Monitor issue found: %d-%02d", ref.year, ref.month)
                return r.content, ref.year, ref.month
            last_status = r.status_code
    raise FileNotFoundError(
        f"No Fiscal Monitor issue 200-OK within lookback={lookback_months} months. "
        f"Tried: {tried}. Last status: {last_status}"
    )


def fetch_issue(year: int, month: int) -> bytes:
    """Fetch the raw HTML for a specific issue. Returns bytes."""
    url = f"{BASE_URL}/{year}/{month:02d}.html"
    with get_client(headers={"User-Agent": "Mozilla/5.0 macro-research-department"}) as client:
        r = client.get(url)
        r.raise_for_status()
        return r.content


def parse_issue(html_bytes: bytes, reference_year: int, reference_month: int) -> FiscalMonitorIssue:
    """Parse one Fiscal Monitor HTML page into a structured result.

    Strategy: read all tables with pandas.read_html, then identify them by
    contextual signals (header text, row labels) since the HTML doesn't tag
    tables with stable IDs.

    Tables we extract:
        Table 0 = monthly budgetary balance, by month, prior-year vs current-year columns
        Table 1 = YTD cumulative balance, same column shape
        Table 2 = budgetary transactions summary (revenues, expenses, balance for month + YTD)
        Tables 3-5 = revenue / expense detail
        Table 6 = revenue composition pie summary
        Tables 7-9 = financial source/requirement, financing, debt summary

    The two derived headline series we publish into long-form CSVs are:
        - monthly_balance (deficit/surplus per month, fiscal year)
        - ytd_balance (fiscal-YTD balance through each month)
    Both keyed by month-end date. Revenue / expense / debt-charge YTD scalars
    are pulled from Table 2 (the summary).
    """
    text = html_bytes.decode("utf-8", errors="replace")
    raw_tables = pd.read_html(io.StringIO(text))
    if len(raw_tables) < 3:
        raise ValueError(
            f"Fiscal Monitor parse: expected >=3 tables, got {len(raw_tables)}. "
            "Page structure may have changed."
        )

    # Federal fiscal year label derivation: Apr2025-Mar2026 = "2025-26".
    # The YTD columns in tables 0/1/2 are labeled e.g. "2025-26".
    # The "current FY" is the year containing the reference month, treating
    # April-Dec as fiscal-year starting that calendar year, and Jan-Mar as
    # fiscal year ending that calendar year.
    if reference_month >= 4:
        fy_start = reference_year
    else:
        fy_start = reference_year - 1
    fy_label = f"{fy_start}-{(fy_start + 1) % 100:02d}"

    # Tables 0 and 1 share the same column shape: [Month/YTD label, FY1, FY2, FY1_excl_actuarial, FY2_excl_actuarial]
    # Identify by looking at the first column header.
    monthly_balance_df = _extract_monthly_balance(raw_tables[0], fy_start)
    ytd_balance_df = _extract_ytd_balance(raw_tables[1], fy_start)
    # Two-FY continuous monthly balance (prior FY full 12 months + current FY
    # months-to-date) for sparkline-friendly history.
    monthly_balance_two_fy_df = _extract_two_fy_monthly_balance(raw_tables[0], fy_start)

    revenues_ytd, expenses_ytd, pdc_ytd = _extract_ytd_summary(
        raw_tables, fy_label, html_text=text
    )

    return FiscalMonitorIssue(
        reference_year=reference_year,
        reference_month=reference_month,
        url=f"{BASE_URL}/{reference_year}/{reference_month:02d}.html",
        fiscal_year_label=fy_label,
        monthly_balance=monthly_balance_df,
        ytd_balance=ytd_balance_df,
        monthly_balance_two_fy=monthly_balance_two_fy_df,
        revenues_ytd=revenues_ytd,
        expenses_ytd=expenses_ytd,
        public_debt_charges_ytd=pdc_ytd,
        raw_tables=raw_tables,
    )


def _to_float(value) -> Optional[float]:
    """Parse a Fiscal Monitor numeric cell to float.

    The HTML tables publish accounting-style numerals: thousands separated
    with commas and negatives wrapped in parentheses, e.g. "(1,046)" = -1046.
    Positive cells parse as plain ints ("989", "3629"), so a bare float()
    silently drops every negative month — an all-deficit FY column comes
    back empty (this is what happened with the FY2026-27 columns in the
    June 2026 issue).
    """
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    s = str(value).strip().replace(",", "").replace("−", "-").replace("$", "")
    if not s or s.lower() in ("nan", "n/a", "-", "–", "—"):
        return None
    negative = s.startswith("(") and s.endswith(")")
    if negative:
        s = s[1:-1]
    try:
        parsed = float(s)
    except ValueError:
        return None
    return -parsed if negative else parsed


def _extract_monthly_balance(df: pd.DataFrame, fy_start: int) -> pd.DataFrame:
    """Pull (date, value) pairs from the per-month balance table for the current FY.

    First column is the month name (April, May, ...). The current-FY column
    is normally the second numeric column. Empty cells (months not yet
    reported) are dropped.
    """
    # Standardize column accessor: month name is always the first column.
    month_col = df.columns[0]
    # Heuristic: the current-FY column is the second column. The HTML emits
    # the prior FY first, current FY second.
    fy_col_candidates = [c for c in df.columns if str(c) != str(month_col)]
    if len(fy_col_candidates) < 2:
        raise ValueError(
            f"Monthly-balance table doesn't have expected FY columns: {list(df.columns)}"
        )
    current_fy_col = fy_col_candidates[1]  # second column = current FY

    records: list[dict] = []
    for _, row in df.iterrows():
        month_name = str(row[month_col]).strip()
        value = row[current_fy_col]
        if pd.isna(value):
            continue
        date_ts = _month_name_to_date(month_name, fy_start)
        if date_ts is None:
            continue
        value_f = _to_float(value)
        if value_f is None:
            continue
        records.append({"date": date_ts, "value": value_f})
    return pd.DataFrame(records, columns=["date", "value"]).sort_values("date").reset_index(drop=True)


def _extract_ytd_balance(df: pd.DataFrame, fy_start: int) -> pd.DataFrame:
    """Pull (date, value) pairs from the YTD-cumulative balance table.

    Same shape as monthly balance, but values are cumulative through that
    month from the start of the FY (April).
    """
    return _extract_monthly_balance(df, fy_start)  # identical column shape


def _extract_two_fy_monthly_balance(df: pd.DataFrame, fy_start: int) -> pd.DataFrame:
    """Build a continuous monthly balance series spanning prior FY + current FY.

    The Fiscal Monitor monthly-balance HTML table emits two FY columns side
    by side:
        - First numeric column: prior FY (full 12 months, finalized).
        - Second numeric column: current FY (months reported so far).
    This helper concatenates the two into one continuous date-indexed series,
    yielding 12-24 months depending on where we are in the current FY.
    Values are in C$ millions; both FYs share the same units.

    Used by the supporting-print spec for the Policy panel's federal-budget
    balance row, which needs enough history for a sparkline.
    """
    month_col = df.columns[0]
    fy_col_candidates = [c for c in df.columns if str(c) != str(month_col)]
    if len(fy_col_candidates) < 2:
        raise ValueError(
            f"Two-FY monthly-balance table doesn't have expected FY columns: {list(df.columns)}"
        )
    prior_fy_col = fy_col_candidates[0]
    current_fy_col = fy_col_candidates[1]
    prior_fy_start = fy_start - 1

    records: list[dict] = []
    for _, row in df.iterrows():
        month_name = str(row[month_col]).strip()
        # Prior-FY observation (always populated; finalized year)
        prior_f = _to_float(row[prior_fy_col])
        if prior_f is not None:
            d_prior = _month_name_to_date(month_name, prior_fy_start)
            if d_prior is not None:
                records.append({"date": d_prior, "value": prior_f})
        # Current-FY observation (may be NaN for months not yet reported)
        cur_f = _to_float(row[current_fy_col])
        if cur_f is not None:
            d_cur = _month_name_to_date(month_name, fy_start)
            if d_cur is not None:
                records.append({"date": d_cur, "value": cur_f})
    out = pd.DataFrame(records, columns=["date", "value"])
    if out.empty:
        return out
    return out.drop_duplicates(subset=["date"], keep="last").sort_values("date").reset_index(drop=True)


def _month_name_to_date(month_name: str, fy_start: int) -> Optional[pd.Timestamp]:
    """Map a federal-FY month name (April through March) to a calendar date.

    fy_start is the calendar year in which April-of-FY falls.
    April-December -> calendar year = fy_start.
    January-March  -> calendar year = fy_start + 1.
    Returns a month-end Timestamp; None if month_name doesn't parse.
    """
    months_to_num = {
        "April": 4, "May": 5, "June": 6, "July": 7, "August": 8, "September": 9,
        "October": 10, "November": 11, "December": 12,
        "January": 1, "February": 2, "March": 3,
    }
    name = month_name.strip()
    num = months_to_num.get(name)
    if num is None:
        return None
    year = fy_start if num >= 4 else fy_start + 1
    return pd.Timestamp(year=year, month=num, day=1) + pd.offsets.MonthEnd(0)


def _extract_ytd_summary(
    raw_tables: list[pd.DataFrame], fy_label: str, *, html_text: str
) -> tuple[Optional[float], Optional[float], Optional[float]]:
    """Pull headline revenue / expense / public-debt-charge YTD values.

    Strategy: search every table for a row whose first-cell label matches
    "Revenues", "Total expenses", "Public debt charges", and within that row
    pick the column whose header matches the current FY label.
    """
    revenues = expenses = pdc = None
    for tbl in raw_tables:
        try:
            label_col = tbl.columns[0]
        except Exception:  # noqa: BLE001
            continue
        # Build a flat-string label per column to find current-FY columns
        label_strings = [str(c) for c in tbl.columns]
        # Match FY label across compound headers (MultiIndex repr like "(April to February, 2025-26)")
        fy_col_idx = [i for i, s in enumerate(label_strings) if fy_label in s]
        if not fy_col_idx:
            continue
        # Iterate rows
        for _, row in tbl.iterrows():
            first = str(row.iloc[0]).strip().lower()
            for i in fy_col_idx:
                cell_val = _to_float(row.iloc[i])
                if cell_val is None:
                    continue
                # Match labels
                if first == "revenues" and revenues is None:
                    revenues = cell_val
                elif first in ("total expenses", "expenses (excluding net actuarial losses)") and expenses is None:
                    expenses = cell_val
                elif first == "public debt charges" and pdc is None:
                    pdc = cell_val
    return revenues, expenses, pdc


def issue_url(year: int, month: int) -> str:
    """Human-readable issue URL for .meta.json provenance."""
    return f"{BASE_URL}/{year}/{month:02d}.html"
