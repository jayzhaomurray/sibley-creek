"""Static annual fiscal series: FRT 2025 + SEU 2026 vetted data.

These are STATIC data modules, not live HTTP fetchers. The values here are
transcribed from primary sources verified by the researcher in the session
documented at claude-ref/research/fiscal_redo/source_and_series.md.

IMPORTANT: Do NOT add live HTTP calls to this module. The data sources are:
  - FRT 2025 (Fiscal Reference Tables, October 2025) -- cached PDF at
    data/raw/fiscal/frt_2025.pdf; canada.ca returns 403 to automated fetch.
    Table numbers and page references are noted inline.
  - SEU 2026 (Spring Economic Update, April 28 2026) -- Annex 1 and Annex 3
    WebFetched and verified by researcher 2026-06-02.
  - Debt Management Report 2024-2025 -- search-verified; Tier B pending
    human PDF re-pull for decimals.

When a future official data release supersedes these values, update the
relevant constant block below AND the corresponding .meta.json sidecar.
Never silently overwrite -- update the fetched_at / vintage_note fields too.

ACCOUNTING-BASIS BREAKS (apply to every series in this module):
  (a) FY1983-84: full accrual accounting introduced. Pre-1983-84 data are on a
      modified-cash/hybrid basis and are NOT comparable with FY1983-84 onward.
      All long-history series here begin at FY1983-84 (the first full accrual year)
      unless a narrower window is documented. Each series carries a `basis_break`
      metadata entry so chart-builders can annotate the start-year boundary.
  (b) FY2019-20: "net actuarial losses" split into a separate expense category;
      FY2008-09 to FY2018-19 restated. The TOTAL budgetary balance is consistent
      across all years because actuarial losses are included in every year's total.
  (c) FY2017-18: discount-rate methodology change for unfunded future benefits;
      FY2008-09 to FY2016-17 restated. Affects program-expense subcomponents but
      NOT the total budgetary balance or the %GDP aggregates used here.
  (d) FY2021-22 (April 2022): PS 3280 (Asset Retirement Obligations) added
      $5,379M to the accumulated deficit as an opening-balance adjustment.
      This lifts the debt LEVEL but does NOT affect annual budgetary balance.
  (e) FY2022-23: financial-instruments standard added remeasurement gains/losses
      (excluded from budgetary balance by definition) and a $2,563M
      opening-balance adjustment to the accumulated deficit.
  The accrual-era window (FY1983-84 to present) is internally consistent for
  debt-%GDP and balance-%GDP charts. The COVID step (FY2019-20 to FY2020-21)
  is a real event, not a basis break.

Series emitted by build_frt_fiscal_series():
  1. frt_federal_balance_opex    -- operating balance ($B, SEU 2026 Annex 1 A1.5)
  2. frt_federal_balance_capex   -- capital investment ($B, SEU 2026 Annex 1 A1.4)
  3. frt_revenues_pct_gdp        -- revenues % of GDP (FRT 2025 Table 2 HISTORY
                                     from FY1983-84; SEU 2026 computed forecast)
  4. frt_program_exp_pct_gdp     -- program expenses excl. net actuarial losses
                                     % of GDP (FRT 2025 Table 8 HISTORY from
                                     FY1983-84; SEU 2026 forecast)
  5. frt_federal_debt_pct_gdp    -- federal debt (accumulated deficit) % of GDP
                                     (FRT 2025 Table 2 HISTORY from FY1983-84;
                                     SEU 2026 Annex 1 forecast). Extends to the
                                     ~66.6% post-accrual peak (FY1995-96).
  6. frt_issuance_bonds          -- outstanding marketable bonds stock ($M, FRT 2025
                                     Table 16 from FY2015-16, history only)
  7. frt_issuance_tbills         -- outstanding treasury bills stock ($M, FRT 2025
                                     Table 16 from FY2015-16, history + SEU 2026
                                     Annex 3 T-bill stock target forward points)
  8. frt_issuance_retail         -- outstanding retail debt stock ($M, FRT 2025
                                     Table 16 from FY2015-16, history only)
  9. frt_federal_balance_total   -- TOTAL annual budgetary balance ($B, deficit
                                     negative): FRT 2025 Table 1 HISTORY from
                                     FY1983-84 (extended from prior FY2006-07
                                     start), plus SEU 2026 Annex 1 A1.7 forecast
                                     FY2025-26 to FY2030-31.
  10. frt_federal_balance_pct_gdp -- budgetary balance % of GDP (deficit negative):
                                     FRT 2025 Table 2 HISTORY from FY1983-84 plus
                                     SEU 2026 Annex 1 A1.7 balance $B / SEU GDP.
                                     This is the companion to frt_federal_balance_total
                                     for a 40-year chart -- the $B series loses
                                     meaning across inflation/economy-size changes
                                     (COVID $328B vs GFC $56B; as %GDP: -14.8% vs
                                     -3.4%). Use this series for long-horizon charts.
  11. frt_issuance_flow_bills    -- GROSS ISSUANCE FLOW, BILLS bucket ($B/FY). DMR
                                     Table 4.1 "Treasury Bills" line. NOTE: this is the
                                     year-end T-bill STOCK (DMR convention), NOT gross
                                     bill auctions. FY2019-20 to FY2026-27; FY2025-26 &
                                     FY2026-27 is_forecast=1 (DMS/SEU plan).
  12. frt_issuance_flow_notes    -- GROSS ISSUANCE FLOW, NOTES bucket ($B/FY) = 2/3/5yr
                                     bonds (= DMR "Short" bucket). True gross flow.
                                     "NOTES" is our label, not a GoC instrument class.
  13. frt_issuance_flow_bonds    -- GROSS ISSUANCE FLOW, BONDS bucket ($B/FY) = 10yr +
                                     30yr + ultra-long + RRB + Green (= DMR "Long" +
                                     Green). True gross flow.

  Series 11/12/13 are a DIFFERENT METRIC from Series 6/7/8: they plot the annual
  GROSS ISSUANCE FLOW (primary-market funding raised each fiscal year), not the
  year-end outstanding STOCK. They replaced Series 6/7/8 on panel-10. Series 6/7/8
  are retained but no longer wired to the issuance plate. Source-of-truth file:
  claude-ref/research/fiscal_redo/issuance_flow_series.md.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import pandas as pd

logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[2]
DATA_DERIVED = ROOT / "data" / "derived"

# ---------------------------------------------------------------------------
# FISCAL YEAR -> ISO DATE HELPER
# ---------------------------------------------------------------------------
# Convention: a fiscal year label like "2025-26" means the year ending
# 31 March 2026. The ISO date used for the data point is the last day of
# that fiscal year: 2026-03-31.
# All annual series in the pipeline use the fiscal-year-end date.


def _fy_to_iso(fy_label: str) -> str:
    """Convert "YYYY-YY" fiscal year label to fiscal-year-end ISO date.

    "2024-25" -> "2025-03-31" (year ending 31 March 2025).
    """
    end_year = int(fy_label[:4]) + 1
    return f"{end_year}-03-31"


# ---------------------------------------------------------------------------
# SOURCE DATA CONSTANTS
# ---------------------------------------------------------------------------
# Every block below is annotated with:
#   SOURCE: publication name, table/annex reference, URL (if public)
#   VINTAGE: release date of the publication
#   TIER:    A = primary-verified from official DoF/BoC document;
#             B = search-verified pending human PDF re-pull

# ---------------------------------------------------------------------------
# SERIES 1+2: Operating balance + capital investment ($B)
# SOURCE: SEU 2026 (Spring Economic Update 2026), Annex 1, Tables A1.4 and A1.5
# VINTAGE: 2026-04-28
# URL: https://budget.canada.ca/update-miseajour/2026/report-rapport/anx1-en.html
# TIER: A (WebFetched + verified by researcher 2026-06-02)
# NOTE: The Capital Budgeting Framework was introduced in Budget 2025 (Nov 4 2025).
#       No official pre-FY2025-26 operating/capital back-series exists. Do NOT
#       fabricate pre-2025 operating or capital points.
# NOTE: FY2024-25 total balance = -$36.3B (actual; from SEU/FRT); the
#       operating/capital decomposition does NOT exist for FY2024-25 (pre-framework
#       actual). Only FY2025-26 onward has the official split. FY2024-25 is
#       included as total-balance-only context (opex=None, capex=None).
# ---------------------------------------------------------------------------

# FY label -> (operating_balance_cad_bn, capital_investment_cad_bn, is_forecast)
# operating_balance: surplus(+) / deficit(-); capital_investment: always positive ($B spent)
# SEU 2026 Annex 1 Table A1.5 (operating balance) and A1.4 (capital investment)
BALANCE_OPEX_CAPEX: list[tuple[str, Optional[float], Optional[float], int]] = [
    # (fy_label, operating_balance_bn, capital_investment_bn, is_forecast)
    # FY2024-25: actual total balance -$36.3B; no official opex/capex split (pre-framework)
    # Carried here as NaN to anchor the chart time axis; chart-builder may omit or annotate.
    ("2024-25", None, None, 0),
    # FY2025-26 onward: SEU 2026 Annex 1 official decomposition
    ("2025-26", -26.4,  40.5, 1),   # A1.5: opex = -26.4; A1.4: capex = 40.5; total = -66.9
    ("2026-27", -10.5,  54.9, 1),   # A1.5: -10.5; A1.4: 54.9; total = -65.3 (rounding: -10.5-54.9=-65.4)
    ("2027-28",  -5.2,  57.9, 1),   # A1.5: -5.2;  A1.4: 57.9; total = -63.1
    ("2028-29",   0.9,  58.6, 1),   # A1.5: +0.9;  A1.4: 58.6; total = -57.7 (first anchor: opex balanced)
    ("2029-30",   4.5,  60.6, 1),   # A1.5: +4.5;  A1.4: 60.6; total = -56.2
    ("2030-31",   6.1,  59.3, 1),   # A1.5: +6.1;  A1.4: 59.3; total = -53.2
]

# ---------------------------------------------------------------------------
# SERIES 9: Federal budgetary balance TOTAL ($B, deficit negative)
# History:  FRT 2025 Table 1 ("Fiscal transactions, millions of dollars"),
#           "Budgetary surplus or deficit (-)" TOTAL column.
#           SOURCE: Fiscal Reference Tables 2025, Table 1, PDF page 8
#           VINTAGE: October 2025
#           URL: data/raw/fiscal/frt_2025.pdf (canada.ca 403 to WebFetch)
#           TIER: A (pypdf extract from locally-cached primary PDF, 2026-06-02)
#           HISTORY WINDOW: FY1983-84 to FY2024-25 (42 years, full accrual era).
#
#           DERIVATION: For FY2008-09 onward the column is explicitly labelled
#             "Budgetary surplus or deficit (-)" including net actuarial losses.
#           For FY1983-84 to FY2007-08 the column is the simple:
#             revenues - program_expenses - public_debt_charges = total balance.
#           Cross-checks:
#             FY2024-25: 510,951 - 489,869 - 53,410 - 4,020 = -36,348M = -36.3B (matches SEU).
#             FY1983-84: 65,261 - 77,194 - 20,430 = -32,363M = -32.4B.
#             FY1997-98: 160,864 - 114,785 - 43,120 = +2,959M = +3.0B (first surplus year).
#
#           ACCOUNTING NOTE: "net actuarial losses" reclassified as a separate
#           expense category in FY2019-20; FY2008-09 to FY2018-19 restated.
#           The TOTAL budgetary balance is consistent across the full window.
#           Pre-1983-84 excluded: full accrual accounting introduced 1983-84.
#
# Forecast: SEU 2026 Annex 1 Table A1.7, "Budgetary balance" row ($B, signed).
#           SOURCE: SEU 2026 Annex 1
#           VINTAGE: 2026-04-28
#           TIER: A (WebFetched + verified by researcher 2026-06-02)
#           NOTE: the total equals opex + (-capex) within rounding.
#
# UNITS: $B CAD (billions); deficit = negative, surplus = positive.
#        Values converted from $M (Table 1) to $B with one-decimal rounding.
#        The $M originals are preserved in inline comments for traceability.
#
# EDITORIAL NOTE ON BALANCE $B vs %GDP:
#   For a long-horizon chart (40+ years) the $B series loses interpretive value
#   because economy size has grown 6-7x since 1983-84. The GFC deficit was
#   -$56.4B vs COVID's -$327.7B, but as %GDP they were -3.4% vs -14.8%. The
#   $B series is kept for record completeness and for the near-term chart window
#   (2006-07 onward). For long-horizon analysis use frt_federal_balance_pct_gdp.
# ---------------------------------------------------------------------------

# FY label -> (total_balance_cad_bn, is_forecast)
BALANCE_TOTAL: list[tuple[str, float, int]] = [
    # --- FRT 2025 Table 1 actuals (HISTORY, full accrual era FY1983-84 onward) ---
    # Values in $B rounded to 1 decimal (raw $M in brackets for traceability).
    # BASIS BREAK NOTE: FY1983-84 is the START of the clean comparable series.
    ("1983-84", -32.4, 0),   # FRT Table 1: -32,363 M
    ("1984-85", -37.2, 0),   # FRT Table 1: -37,167 M
    ("1985-86", -33.4, 0),   # FRT Table 1: -33,389 M
    ("1986-87", -29.8, 0),   # FRT Table 1: -29,842 M
    ("1987-88", -29.0, 0),   # FRT Table 1: -29,017 M
    ("1988-89", -27.9, 0),   # FRT Table 1: -27,947 M
    ("1989-90", -29.1, 0),   # FRT Table 1: -29,143 M
    ("1990-91", -33.9, 0),   # FRT Table 1: -33,899 M
    ("1991-92", -32.3, 0),   # FRT Table 1: -32,319 M
    ("1992-93", -39.0, 0),   # FRT Table 1: -39,019 M
    ("1993-94", -38.5, 0),   # FRT Table 1: -38,530 M
    ("1994-95", -36.6, 0),   # FRT Table 1: -36,632 M
    ("1995-96", -30.0, 0),   # FRT Table 1: -30,006 M
    ("1996-97",  -8.7, 0),   # FRT Table 1:  -8,719 M
    ("1997-98",   3.0, 0),   # FRT Table 1:  +2,959 M (first surplus post-accrual era)
    ("1998-99",   5.8, 0),   # FRT Table 1:  +5,779 M
    ("1999-00",  14.3, 0),   # FRT Table 1: +14,258 M
    ("2000-01",  19.9, 0),   # FRT Table 1: +19,891 M
    ("2001-02",   8.0, 0),   # FRT Table 1:  +8,048 M
    ("2002-03",   6.6, 0),   # FRT Table 1:  +6,621 M
    ("2003-04",   9.1, 0),   # FRT Table 1:  +9,145 M
    ("2004-05",   1.5, 0),   # FRT Table 1:  +1,463 M
    ("2005-06",  13.2, 0),   # FRT Table 1: +13,218 M
    ("2006-07",  13.8, 0),   # FRT Table 1: +13,752 M (surplus)
    ("2007-08",   9.6, 0),   # FRT Table 1: +9,597 M (surplus, last pre-GFC surplus)
    ("2008-09",  -9.1, 0),   # FRT Table 1: -9,116 M (GFC onset)
    ("2009-10", -56.4, 0),   # FRT Table 1: -56,368 M (GFC stimulus peak)
    ("2010-11", -35.0, 0),   # FRT Table 1: -34,953 M
    ("2011-12", -28.0, 0),   # FRT Table 1: -28,033 M
    ("2012-13", -21.3, 0),   # FRT Table 1: -21,293 M
    ("2013-14",  -8.1, 0),   # FRT Table 1: -8,050 M
    ("2014-15",  -0.6, 0),   # FRT Table 1: -550 M (near-balance)
    ("2015-16",  -2.9, 0),   # FRT Table 1: -2,861 M
    ("2016-17", -19.0, 0),   # FRT Table 1: -18,957 M (Liberal fiscal expansion)
    ("2017-18", -19.0, 0),   # FRT Table 1: -18,961 M
    ("2018-19", -14.0, 0),   # FRT Table 1: -13,964 M
    ("2019-20", -39.4, 0),   # FRT Table 1: -39,392 M (pre-COVID; includes early shutdowns)
    ("2020-21",-327.7, 0),   # FRT Table 1: -327,729 M (COVID emergency spending peak)
    ("2021-22", -90.3, 0),   # FRT Table 1: -90,315 M (COVID wind-down + CEWS tail)
    ("2022-23", -35.3, 0),   # FRT Table 1: -35,322 M
    ("2023-24", -61.9, 0),   # FRT Table 1: -61,876 M
    ("2024-25", -36.3, 0),   # FRT Table 1: -36,348 M (confirmed vs SEU actual: -36.3B)
    # --- SEU 2026 Annex 1 Table A1.7 total balance (FORECAST) ---
    # SEU's own published budgetary balance row; same source as opex/capex
    ("2025-26", -66.9, 1),   # SEU A1.7: -66.9B (= opex -26.4 + capex -40.5)
    ("2026-27", -65.3, 1),   # SEU A1.7: -65.3B (= opex -10.5 + capex -54.9, rounding -65.4)
    ("2027-28", -63.1, 1),   # SEU A1.7: -63.1B (= opex -5.2 + capex -57.9)
    ("2028-29", -57.7, 1),   # SEU A1.7: -57.7B (= opex +0.9 + capex -58.6)
    ("2029-30", -56.2, 1),   # SEU A1.7: -56.2B (= opex +4.5 + capex -60.6, rounding: -56.1)
    ("2030-31", -53.2, 1),   # SEU A1.7: -53.2B (= opex +6.1 + capex -59.3)
]

# ---------------------------------------------------------------------------
# SERIES 3: Federal revenues as % of GDP
# History:  FRT 2025 Table 2 ("Fiscal transactions, per cent of GDP")
#           SOURCE: Fiscal Reference Tables 2025, Department of Finance Canada
#           VINTAGE: October 2025
#           URL: data/raw/fiscal/frt_2025.pdf page 10 (PDF page 9)
#                (canada.ca 403 to WebFetch; locally cached)
#           TIER: A (pypdf extract from locally-cached primary PDF, 2026-06-02)
#           HISTORY WINDOW: FY1983-84 to FY2024-25 (42 years).
#           FY1983-84 is the first full accrual year; pre-1983-84 not comparable.
#           Values read from the "Revenues" column of Table 2 (= Table 4 %GDP
#           revenues total column, cross-check consistent).
# Forecast: SEU 2026 Annex 1 Table A1.7 revenues $B divided by SEU nominal GDP $B
#           SOURCE: SEU 2026 Annex 1
#           VINTAGE: 2026-04-28
#           NOTE: computed ratio -- numerator (revenue $B) and denominator (SEU
#           nominal GDP $B) both from SEU 2026 Annex 1; GDP denominator is the
#           CALENDAR YEAR that the FISCAL YEAR begins in (verified by back-out
#           from SEU's own debt $B / debt %GDP rows -- see research file).
# ---------------------------------------------------------------------------
# FY label -> (rev_pct_gdp, is_forecast)
REVENUES_PCT_GDP: list[tuple[str, float, int]] = [
    # --- FRT 2025 Table 2 actuals (HISTORY, full accrual era FY1983-84 onward) ---
    # Values from the "Revenues (per cent of GDP)" column, FRT 2025 Table 2 / Table 4.
    # Pre-1983-84 excluded: full accrual accounting introduced 1983-84 (FRT footnote).
    # BASIS BREAK NOTE: FY1983-84 is the START of the clean comparable series.
    ("1983-84", 15.5, 0),   # FRT Table 2: 15.5 -- first full accrual year
    ("1984-85", 15.6, 0),
    ("1985-86", 15.5, 0),
    ("1986-87", 16.5, 0),
    ("1987-88", 16.9, 0),
    ("1988-89", 17.0, 0),
    ("1989-90", 17.3, 0),
    ("1990-91", 17.2, 0),
    ("1991-92", 18.0, 0),
    ("1992-93", 17.3, 0),
    ("1993-94", 16.6, 0),
    ("1994-95", 16.5, 0),
    ("1995-96", 16.9, 0),
    ("1996-97", 17.4, 0),
    ("1997-98", 17.7, 0),
    ("1998-99", 17.6, 0),
    ("1999-00", 17.5, 0),
    ("2000-01", 17.6, 0),
    ("2001-02", 16.1, 0),
    ("2002-03", 16.0, 0),
    ("2003-04", 16.0, 0),
    ("2004-05", 16.0, 0),
    ("2005-06", 15.8, 0),
    ("2006-07", 15.9, 0),
    ("2007-08", 15.6, 0),
    ("2008-09", 14.3, 0),
    ("2009-10", 14.0, 0),
    ("2010-11", 14.4, 0),
    ("2011-12", 13.9, 0),
    ("2012-13", 13.9, 0),
    ("2013-14", 14.2, 0),
    ("2014-15", 14.0, 0),
    ("2015-16", 14.7, 0),
    ("2016-17", 14.4, 0),
    ("2017-18", 14.5, 0),
    ("2018-19", 14.9, 0),
    ("2019-20", 14.4, 0),
    ("2020-21", 14.3, 0),  # COVID fiscal year (transfer payments exploded, but revenue held)
    ("2021-22", 16.3, 0),  # post-COVID nominal-GDP and corporate-tax surge
    ("2022-23", 15.7, 0),
    ("2023-24", 15.7, 0),
    ("2024-25", 16.6, 0),  # FRT 2025 Table 2 actual; SEU shows 40.7% GDP vintage vs FRT 41.2%
    # --- SEU 2026 forward profile (FORECAST) ---
    # Numerators: SEU 2026 Annex 1 Table A1.7 revenues $B
    # Denominators: SEU stated calendar-year nominal GDP $B (same vintage)
    # Computed ratios (numerator / denominator * 100):
    #   511.5 / 3243 * 100 = 15.77; 529.6 / 3372 = 15.71; 546.8 / 3496 = 15.64
    #   565.9 / 3630 = 15.59; 589.8 / 3772 = 15.64; 613.7 / 3917 = 15.67
    # SEAM NOTE: FRT FY2024-25 actual = 16.6% (FRT 2025 Oct-2025 GDP vintage);
    #            SEU FY2025-26 forecast = 15.77% (SEU Apr-2026 GDP vintage).
    #            The 0.9pp step is PARTLY a genuine projected decline AND PARTLY
    #            a vintage-denominator offset. Chart must carry a seam annotation.
    ("2025-26", 15.77, 1),
    ("2026-27", 15.71, 1),
    ("2027-28", 15.64, 1),
    ("2028-29", 15.59, 1),
    ("2029-30", 15.64, 1),
    ("2030-31", 15.67, 1),
]

# ---------------------------------------------------------------------------
# SERIES 4: Program expenses excl. net actuarial losses as % of GDP
# History:  FRT 2025 Table 8 ("Expenses, per cent of GDP")
#           SOURCE: Fiscal Reference Tables 2025, Table 8, PDF page 15
#                   (canada.ca 403 to WebFetch; locally cached)
#           VINTAGE: October 2025
#           TIER: A (pypdf extract from locally-cached primary PDF, 2026-06-02)
#           HISTORY WINDOW: FY1983-84 to FY2024-25 (42 years).
#           FY1983-84 is the first full accrual year; pre-1983-84 not comparable.
#           The "Total program expenses" column is used, which equals the sum of
#           major transfers to persons, transfers to provinces/territories/
#           municipalities, pollution pricing proceeds, and direct program expenses,
#           EXCLUDING public debt charges AND (from 2008-09) net actuarial losses.
#           Pre-2008-09 the net-actuarial sub-category did not exist as a separate
#           line; the FRT restated 2008-09 to 2018-19 but FY1983-84 to FY2007-08
#           values are the pre-reclassification totals. The total-program-expenses
#           column is internally consistent across the full accrual window.
#           NOTE: The FY2020-21 spike to 28.1% is real (COVID emergency spending),
#           not a basis break. Annotate on chart.
#           NOTE: The pre-2008-09 "Total program expenses" %GDP figures are READ
#           from Table 8 "Total program expenses" column directly. These years
#           predate the actuarial reclassification, so "excl. actuarial" and
#           "incl. actuarial" are the same number (no separate actuarial line existed).
# Forecast: SEU 2026 Annex 1 Table A1.7 program-expenses-ex-actuarial $B / SEU nominal GDP $B
#           SOURCE: SEU 2026 Annex 1; same GDP denominator as Series 3
#           VINTAGE: 2026-04-28
#           Computed: 512.8/3243=15.81; 536.1/3372=15.90; 543.9/3496=15.56
#                     555.9/3630=15.31; 575.4/3772=15.25; 591.6/3917=15.10
# ---------------------------------------------------------------------------
PROGRAM_EXP_PCT_GDP: list[tuple[str, float, int]] = [
    # --- FRT 2025 Table 8 actuals (HISTORY, full accrual era FY1983-84 onward) ---
    # "Total program expenses" column (excl. public debt charges; excl. actuarial
    # losses from FY2008-09 onward per the FRT reclassification footnote).
    # BASIS BREAK NOTE: FY1983-84 is the START of the clean comparable series.
    ("1983-84", 18.3, 0),   # FRT Table 8 -- first full accrual year
    ("1984-85", 18.2, 0),
    ("1985-86", 16.7, 0),
    ("1986-87", 16.7, 0),
    ("1987-88", 16.5, 0),
    ("1988-89", 15.8, 0),
    ("1989-90", 15.5, 0),
    ("1990-91", 15.6, 0),
    ("1991-92", 16.3, 0),
    ("1992-93", 17.0, 0),
    ("1993-94", 16.4, 0),
    ("1994-95", 15.6, 0),
    ("1995-96", 14.5, 0),   # consolidation era: Chretien/Martin spending cuts
    ("1996-97", 12.9, 0),
    ("1997-98", 12.7, 0),
    ("1998-99", 12.4, 0),
    ("1999-00", 11.8, 0),
    ("2000-01", 11.8, 0),
    ("2001-02", 11.9, 0),
    ("2002-03", 12.3, 0),
    ("2003-04", 12.4, 0),
    ("2004-05", 13.4, 0),
    ("2005-06", 12.5, 0),
    ("2006-07", 12.7, 0),
    ("2007-08", 12.8, 0),
    ("2008-09", 12.3, 0),   # FRT Table 8 -- post-reclassification era (actuarial now separate)
    ("2009-10", 14.0, 0),
    ("2010-11", 13.4, 0),
    ("2011-12", 13.0, 0),
    ("2012-13", 12.8, 0),
    ("2013-14", 12.7, 0),
    ("2014-15", 12.6, 0),
    ("2015-16", 13.5, 0),
    ("2016-17", 13.3, 0),
    ("2017-18", 13.0, 0),
    ("2018-19", 14.4, 0),
    ("2019-20", 15.1, 0),
    ("2020-21", 28.1, 0),   # COVID emergency spending spike -- annotate on chart
    ("2021-22", 18.9, 0),
    ("2022-23", 15.7, 0),
    ("2023-24", 16.2, 0),
    ("2024-25", 16.1, 0),   # FRT 2025 Table 8 actual
    # --- SEU 2026 forward profile (FORECAST) ---
    # Program expenses declining toward ~15.1% as nominal GDP outgrows restrained track
    ("2025-26", 15.81, 1),
    ("2026-27", 15.90, 1),
    ("2027-28", 15.56, 1),
    ("2028-29", 15.31, 1),
    ("2029-30", 15.25, 1),
    ("2030-31", 15.10, 1),
]

# ---------------------------------------------------------------------------
# SERIES 5: Federal debt (accumulated deficit) as % of GDP
# History:  FRT 2025 Table 2, "Accumulated deficit" %GDP column
#           SOURCE: Fiscal Reference Tables 2025, Table 2, PDF page 9
#                   (canada.ca 403 to WebFetch; locally cached)
#           VINTAGE: October 2025; GDP denominator = Oct-2025 StatCan vintage
#           TIER: A (pypdf extract from locally-cached primary PDF, 2026-06-02)
#           HISTORY WINDOW: FY1983-84 to FY2024-25 (42 years, full accrual era).
#           Pre-1983-84 excluded: full accrual accounting introduced 1983-84.
#           Post-accrual peak: FY1995-96 at 66.6% (verified from primary table --
#           NOTE: the research file claude-ref/research/fiscal_redo/source_and_series.md
#           stated "66.6% in FY1994-95" but FRT Table 2 primary data shows
#           FY1994-95 = 66.2% and FY1995-96 = 66.6%. FRT primary is authoritative.
#           Pre-GFC trough: FY2008-09 at 28.2%. COVID peak: FY2020-21 at 47.2%.
# Forecast: SEU 2026 Annex 1 Table A1.7 published %GDP row (use as-is -- Tier A,
#           no derivation needed; these are SEU's own stated ratios)
#           SOURCE: SEU 2026 Annex 1
#           VINTAGE: 2026-04-28; GDP denominator = Apr-2026 SEU vintage
# SEAM NOTE: FRT FY2024-25 actual = 41.2% (Oct-2025 GDP vintage)
#            SEU FY2024-25 revised = 40.7% (Apr-2026 GDP vintage, same debt level ~$1,266.5B)
#            The pipeline uses FRT 41.2% for the history line and SEU 41.1% for
#            FY2025-26 onward. This is a ~0.1pp seam (benign vs the 0.9pp revenue seam).
# DO NOT splice the Budget 2025 Chart A1.5 series (data/derived/fiscal_debt_to_gdp.csv) --
# that CSV uses a different GDP vintage and the denominators are incompatible with FRT.
# ---------------------------------------------------------------------------
FEDERAL_DEBT_PCT_GDP: list[tuple[str, float, int]] = [
    # --- FRT 2025 Table 2 actuals (HISTORY, full accrual era FY1983-84 onward) ---
    # Federal debt (accumulated deficit) % of GDP, Oct-2025 GDP vintage.
    # Read from the "Accumulated deficit" column of FRT 2025 Table 2 (PDF page 9).
    # BASIS BREAK NOTE: FY1983-84 is the START of the clean comparable series.
    #   Chart-builders: annotate this boundary; pre-1983-84 is a different accounting basis.
    ("1983-84", 37.3, 0),   # FRT Table 2: 37.3 -- first full accrual year
    ("1984-85", 42.1, 0),
    ("1985-86", 45.6, 0),
    ("1986-87", 48.9, 0),
    ("1987-88", 49.9, 0),
    ("1988-89", 50.2, 0),
    ("1989-90", 51.2, 0),
    ("1990-91", 54.3, 0),
    ("1991-92", 58.4, 0),
    ("1992-93", 62.5, 0),
    ("1993-94", 65.3, 0),
    ("1994-95", 66.2, 0),
    ("1995-96", 66.6, 0),   # POST-ACCRUAL PEAK: highest in the comparable era
    ("1996-97", 65.5, 0),
    ("1997-98", 61.7, 0),
    ("1998-99", 58.9, 0),
    ("1999-00", 53.6, 0),
    ("2000-01", 47.0, 0),
    ("2001-02", 44.7, 0),
    ("2002-03", 42.3, 0),
    ("2003-04", 39.5, 0),
    ("2004-05", 37.0, 0),
    ("2005-06", 33.9, 0),
    ("2006-07", 31.2, 0),
    ("2007-08", 29.0, 0),
    ("2008-09", 28.2, 0),   # pre-GFC trough (post-accrual era)
    ("2009-10", 33.4, 0),
    ("2010-11", 33.4, 0),
    ("2011-12", 33.4, 0),
    ("2012-13", 34.0, 0),
    ("2013-14", 32.9, 0),
    ("2014-15", 31.5, 0),
    ("2015-16", 31.9, 0),
    ("2016-17", 32.2, 0),
    ("2017-18", 31.4, 0),
    ("2018-19", 30.7, 0),
    ("2019-20", 31.2, 0),
    ("2020-21", 47.2, 0),   # COVID peak
    ("2021-22", 45.0, 0),
    ("2022-23", 41.1, 0),
    ("2023-24", 42.1, 0),
    ("2024-25", 41.2, 0),   # FRT 2025 actual; SEU reads 40.7% (different GDP vintage)
    # --- SEU 2026 Annex 1 Table A1.7 published %GDP (FORECAST) ---
    # SEU's own stated ratios (use as-is; computed ratios reproduce to 0.1pp -- see research file)
    ("2025-26", 41.1, 1),
    ("2026-27", 41.5, 1),
    ("2027-28", 41.8, 1),
    ("2028-29", 41.9, 1),   # approximate peak (second fiscal anchor: declining debt/GDP)
    ("2029-30", 41.8, 1),
    ("2030-31", 41.6, 1),
]

# ---------------------------------------------------------------------------
# SERIES 10: Budgetary balance as % of GDP (deficit negative)
# History:  FRT 2025 Table 2, "Budgetary surplus or deficit (-)" %GDP column.
#           SOURCE: Fiscal Reference Tables 2025, Table 2, PDF page 9
#                   (canada.ca 403 to WebFetch; locally cached)
#           VINTAGE: October 2025
#           TIER: A (pypdf extract from locally-cached primary PDF, 2026-06-02)
#           HISTORY WINDOW: FY1983-84 to FY2024-25 (42 years, full accrual era).
#           Pre-1983-84 excluded. Pre-2008-09 values are the "surplus/deficit excl.
#           actuarial" column (actuarial not yet a separate category); post-2008-09
#           values are the total balance including actuarial. Consistent because
#           pre-2008-09 actuarial gains/losses were folded into direct program
#           expenses -- the TOTAL is the same across both regimes.
#
# Forecast: Computed from SEU 2026 Annex 1 A1.7 total balance $B divided by
#           SEU calendar-year nominal GDP $B (same denominator as Series 3/4/5).
#           VINTAGE: 2026-04-28.
#           DERIVATION: balance $B from BALANCE_TOTAL forecast rows / SEU GDP $B
#             FY2025-26: -66.9 / 3243 * 100 = -2.06
#             FY2026-27: -65.3 / 3372 * 100 = -1.94
#             FY2027-28: -63.1 / 3496 * 100 = -1.80
#             FY2028-29: -57.7 / 3630 * 100 = -1.59
#             FY2029-30: -56.2 / 3772 * 100 = -1.49
#             FY2030-31: -53.2 / 3917 * 100 = -1.36
#
# WHY THIS SERIES: The $B balance (Series 9) is the right near-term series
#   (last 15-20 years). For a 40-year chart the economy grew ~6-7x in nominal
#   terms, so a $B deficit in 1984 and one in 2020 are not comparable in scale.
#   The %GDP series is the clean long-horizon comparator.
# ---------------------------------------------------------------------------
# FY label -> (balance_pct_gdp, is_forecast)
BALANCE_PCT_GDP: list[tuple[str, float, int]] = [
    # --- FRT 2025 Table 2 actuals (HISTORY, full accrual era FY1983-84 onward) ---
    # Read from "Budgetary surplus or deficit (-)" %GDP column in Table 2 (PDF p.9).
    # Pre-2008-09: excl. actuarial (no separate actuarial line existed; consistent).
    # BASIS BREAK NOTE: FY1983-84 is the START of the clean comparable series.
    ("1983-84",  -7.7, 0),   # FRT Table 2
    ("1984-85",  -8.0, 0),
    ("1985-86",  -6.7, 0),
    ("1986-87",  -5.7, 0),
    ("1987-88",  -5.1, 0),
    ("1988-89",  -4.5, 0),
    ("1989-90",  -4.3, 0),
    ("1990-91",  -4.9, 0),
    ("1991-92",  -4.6, 0),
    ("1992-93",  -5.4, 0),
    ("1993-94",  -5.2, 0),
    ("1994-95",  -4.6, 0),
    ("1995-96",  -3.6, 0),
    ("1996-97",  -1.0, 0),
    ("1997-98",   0.3, 0),   # first surplus post-accrual era
    ("1998-99",   0.6, 0),
    ("1999-00",   1.4, 0),
    ("2000-01",   1.8, 0),
    ("2001-02",   0.7, 0),
    ("2002-03",   0.6, 0),
    ("2003-04",   0.7, 0),
    ("2004-05",   0.1, 0),
    ("2005-06",   0.9, 0),
    ("2006-07",   0.9, 0),
    ("2007-08",   0.6, 0),
    # From FY2008-09 onward: total balance including net actuarial losses.
    # Values from FRT 2025 Table 2 "Budgetary surplus or deficit (-)" %GDP column.
    ("2008-09",  -0.6, 0),
    ("2009-10",  -3.6, 0),   # Note: Table 2 says -3.6; Table 17 "actual" is -3.4%
                              # potential GDP. Use Table 2 (%actual GDP) here.
    ("2010-11",  -2.1, 0),
    ("2011-12",  -1.6, 0),
    ("2012-13",  -1.2, 0),
    ("2013-14",  -0.4, 0),
    ("2014-15",  -0.0, 0),
    ("2015-16",  -0.1, 0),
    ("2016-17",  -0.9, 0),
    ("2017-18",  -0.9, 0),
    ("2018-19",  -0.6, 0),
    ("2019-20",  -1.7, 0),
    ("2020-21", -14.8, 0),   # COVID emergency spending peak -- annotate on chart
    ("2021-22",  -3.6, 0),
    ("2022-23",  -1.2, 0),
    ("2023-24",  -2.1, 0),
    ("2024-25",  -1.2, 0),   # FRT 2025 Table 2 actual
    # --- SEU 2026 computed forecast (FORECAST) ---
    # Derived: SEU A1.7 total balance $B / SEU calendar-year nominal GDP $B * 100.
    # Denominator = calendar year the fiscal year begins in (same as Series 3/4/5).
    # (rounded to 2 decimal places for precision; chart may display 1 decimal)
    ("2025-26",  -2.06, 1),  # -66.9 / 3243 * 100
    ("2026-27",  -1.94, 1),  # -65.3 / 3372 * 100
    ("2027-28",  -1.80, 1),  # -63.1 / 3496 * 100
    ("2028-29",  -1.59, 1),  # -57.7 / 3630 * 100
    ("2029-30",  -1.49, 1),  # -56.2 / 3772 * 100
    ("2030-31",  -1.36, 1),  # -53.2 / 3917 * 100
]

# ---------------------------------------------------------------------------
# SERIES 6+7+8: Outstanding market debt by instrument ($M, end of fiscal year)
# SOURCE: FRT 2025 Table 16 ("Unmatured debt held by outside parties")
# VINTAGE: October 2025
# TIER: A (pypdf extract from locally-cached primary PDF)
# NOTE: FY2015-16 to FY2017-18 are TIER A PENDING RE-PULL (same pypdf extract but
#       not in the researcher's published subset; the FY2018-19+ rows have higher
#       confidence). Flag any reader-facing decimal call-out for human re-pull.
# NOTE: Marketable bonds = domestic ($M) + foreign ($M) combined.
#       FY2024-25: 1,163,045 domestic + 29,383 foreign = 1,192,428 combined.
# NOTE: The three buckets (bonds, bills, retail) do NOT sum to FRT Table 16 Total
#       ($1,485,887 FY2024-25) because Total includes Canada Pension Plan bonds,
#       other unmatured debt, and amortized-cost/own-holdings adjustments.
# NOTE: Retail debt (CSB/CPB) is a wound-down program. The FY2021-22 to FY2023-24
#       zero readings and the FY2024-25 $4,681M re-appearance may be a reclassification;
#       confirm on re-pull.
#
# T-BILL FORWARD POINTS (FORECAST, SEU 2026 Annex 3):
#   FY2025-26 end: ~$286B (~$286,000M) T-bill stock target
#   FY2026-27 end: ~$268B (~$268,000M) T-bill stock target (revised down from $291B Budget 2025)
#   SOURCE: SEU 2026 Annex 3, WebFetched and verified 2026-06-02
#   TIER: A
#   NOTE: These are forward STOCK targets for T-bills only. The bond program for
#         FY2025-26 ($317B) and FY2026-27 ($298B) are forward FLOW (gross issuance),
#         not stock -- do NOT add them to the bond stock series.
# ---------------------------------------------------------------------------
# FY label -> (marketable_bonds_m, is_forecast)
ISSUANCE_BONDS: list[tuple[str, float, int]] = [
    # FRT 2025 Table 16, domestic + foreign marketable bonds combined ($M, HISTORY)
    ("2015-16",  487714, 0),   # TIER A PENDING RE-PULL (3 earliest rows)
    ("2016-17",  504653, 0),   # TIER A PENDING RE-PULL
    ("2017-18",  545317, 0),   # TIER A PENDING RE-PULL
    ("2018-19",  585184, 0),
    ("2019-20",  612481, 0),
    ("2020-21",  890450, 0),   # COVID issuance surge
    ("2021-22", 1045085, 0),
    ("2022-23", 1053878, 0),
    ("2023-24", 1102530, 0),
    ("2024-25", 1192428, 0),   # 1,163,045 domestic + 29,383 foreign
    # No forward bond stock available (forward data is gross flow, not stock)
]

# FY label -> (treasury_bills_m, is_forecast)
ISSUANCE_TBILLS: list[tuple[str, float, int]] = [
    # FRT 2025 Table 16, treasury bills ($M, HISTORY)
    ("2015-16",  138100, 0),   # TIER A PENDING RE-PULL
    ("2016-17",  136663, 0),   # TIER A PENDING RE-PULL
    ("2017-18",  110738, 0),   # TIER A PENDING RE-PULL
    ("2018-19",  134300, 0),
    ("2019-20",  151867, 0),
    ("2020-21",  218800, 0),   # COVID money-market funding
    ("2021-22",  187400, 0),
    ("2022-23",  201800, 0),
    ("2023-24",  267400, 0),
    ("2024-25",  285200, 0),
    # SEU 2026 Annex 3 forward stock TARGETS (FORECAST -- T-bills only)
    # Note: SEU quotes ~$286B and ~$268B; using 286000 and 268000 as integer millions
    ("2025-26",  286000, 1),   # SEU 2026 Annex 3: end-FY2025-26 T-bill stock target ~$286B
    ("2026-27",  268000, 1),   # SEU 2026 Annex 3: end-FY2026-27 T-bill stock target ~$268B
]

# FY label -> (retail_debt_m, is_forecast)
ISSUANCE_RETAIL: list[tuple[str, float, int]] = [
    # FRT 2025 Table 16, retail debt (CSB/CPB), wound-down program ($M, HISTORY)
    ("2015-16",    5302, 0),   # TIER A PENDING RE-PULL
    ("2016-17",    5138, 0),   # TIER A PENDING RE-PULL
    ("2017-18",    4725, 0),   # TIER A PENDING RE-PULL
    ("2018-19",    1237, 0),
    ("2019-20",     497, 0),
    ("2020-21",     299, 0),
    ("2021-22",       0, 0),   # FRT Table 16 shows "--" (program effectively wound down)
    ("2022-23",       0, 0),
    ("2023-24",       0, 0),
    ("2024-25",    4681, 0),   # Possible reclassification -- confirm on re-pull
    # No forward retail stock (program in run-off; zero planned issuance)
]

# ---------------------------------------------------------------------------
# SERIES 11+12+13: GROSS ISSUANCE FLOW by maturity bucket ($B, per fiscal year)
# ===========================================================================
# THIS IS A DIFFERENT METRIC FROM SERIES 6/7/8 (outstanding STOCK).
# Series 6/7/8 plot the year-end OUTSTANDING STOCK of market debt. These three
# series (11/12/13) plot the annual GROSS ISSUANCE FLOW -- how much the GoC
# raises in the primary market each fiscal year -- by maturity bucket. The old
# stock series are LEFT IN PLACE (no longer wired to the issuance plate); these
# new flow series replace them on panel-10.
#
# SOURCE: Debt Management Report (DMR) Table 4.1 "Gross Issuance of Bonds and
#         Bills" per-tenor lines (ACTUALS, FY2019-20 to FY2024-25) +
#         DMS 2025-26 / SEU 2026 Annex 3 forward plan (FORECAST, FY2025-26,
#         FY2026-27). This is the same series Desjardins' Graph 6 benchmarks.
# VINTAGE: DMR actuals = latest-vintage DMR per year (pub. 2020 through 2025);
#          forecast = DMS 2025-26 (pub. w/ Budget 2025, 4 Nov 2025) for FY2025-26
#          and SEU 2026 Annex 3 (28 Apr 2026) for FY2026-27.
# TIER: A (primary DMR/DMS PDFs downloaded + pdfplumber-extracted 2026-06-02;
#          SEU 2026 Annex 3 WebFetched 2026-06-02).
# FULL PROVENANCE + per-cell source ledger:
#   claude-ref/research/fiscal_redo/issuance_flow_series.md (the source of truth).
#
# BUCKET MAPPING (OUR aggregation; "NOTES" is NOT a GoC instrument class):
#   BILLS = Treasury bills            (DMR "Treasury Bills" line)
#   NOTES = 2yr + 3yr + 5yr bonds     (= DMR "Short (2,3,5-year sectors)" bucket)
#   BONDS = 10yr + 30yr + ultra-long + Real Return Bonds + Green bonds
#                                     (= DMR "Long (10-year+)" bucket + Green)
#   Reconciliation: BILLS + NOTES + BONDS = DMR "Total Gross Issuance" each year
#   (e.g. FY2024-25: 285 + 157 + 84 = 526; FY2023-24: 267 + 139 + 65 = 471).
#
# *** CRITICAL METHODOLOGY CAVEAT -- DO NOT LOSE THIS ***
# The BILLS bucket is the YEAR-END TREASURY-BILL STOCK, *NOT* the gross T-bill
# auction flow. This is the DMR's own published convention (Table 4.1 is titled
# "... end of fiscal year") and Desjardins uses the same convention. The BOND
# lines (NOTES + BONDS) ARE true gross issuance flow, but the bill line is a
# year-end stock snapshot, because the gross bill roll (~$663B in FY2024-25,
# ~2.3x the $285B stock) would swamp the chart and overstate the funding need.
# CONSEQUENCE: the headline "Total Gross Issuance" is a HYBRID (gross bond flow +
# year-end bill stock). The slot-binding / writer pipeline MUST NOT describe the
# BILLS bucket as "auctioned" or "issued" in the flow sense. Safe framing follows
# the DMR label: "gross issuance of bonds and bills." See research file Section 7,
# caveat 1 (the single most important caveat in the rebuild).
#
# UNITS: $B CAD (billions). FORECAST = planned issuance (DMS/SEU plan, not outturn).
# FY2025-26 BILLS uses the DMS $296B plan target (SEU later revised the estimated
# outturn to ~$286B; we carry the DMS plan for the forward line per the research
# file). No FY2027-28 tenor-level plan exists yet, so the series stops at FY2026-27.
# ---------------------------------------------------------------------------

# FY label -> (bills_bn, is_forecast)  -- BILLS = year-end T-bill STOCK (DMR convention; see caveat above)
ISSUANCE_FLOW_BILLS: list[tuple[str, float, int]] = [
    # --- DMR Table 4.1 "Treasury Bills" line (HISTORY, year-end bill STOCK) ---
    ("2019-20", 152, 0),   # DMR 2020-2021 Table 4.1
    ("2020-21", 219, 0),   # DMR 2020-2021 / 2021-2022 Table 4.1 (COVID money-market funding)
    ("2021-22", 187, 0),   # DMR 2021-2022 / 2022-2023 Table 4.1
    ("2022-23", 202, 0),   # DMR 2022-2023 Table 4.1
    ("2023-24", 267, 0),   # DMR 2023-2024 / 2024-2025 Table 4.1
    ("2024-25", 285, 0),   # DMR 2024-2025 Table 4.1
    # --- DMS 2025-26 / SEU 2026 Annex 3 forward STOCK TARGET (FORECAST) ---
    ("2025-26", 296, 1),   # DMS 2025-26 Table (p6): end-FY2025-26 T-bill stock TARGET $296B
                           #   (SEU 2026 later revised the estimated outturn to ~$286B; plan = 296)
    ("2026-27", 268, 1),   # SEU 2026 Annex 3: "revised down moderately to $268 billion"
]

# FY label -> (notes_bn, is_forecast)  -- NOTES = 2yr + 3yr + 5yr bonds (= DMR "Short" bucket); TRUE gross flow
ISSUANCE_FLOW_NOTES: list[tuple[str, float, int]] = [
    # --- DMR Table 4.1 short-sector bonds, gross FLOW (HISTORY) ---
    ("2019-20", 107, 0),   # DMR 2020-2021 Table 4.1: 53 (2yr) + 20 (3yr) + 34 (5yr)
    ("2020-21", 264, 0),   # 129 + 57 + 78 (COVID issuance surge)
    ("2021-22", 140, 0),   # 67 + 29 + 44
    ("2022-23", 118, 0),   # 67 + 20 + 31  (= DMR 2022-2023 Table 4.2 "Short" = 118)
    ("2023-24", 139, 0),   # 86 + 6 + 47   (= DMR Table 4.2 "Short" = 139; 3yr nearly phased out)
    ("2024-25", 157, 0),   # 94 + 0 + 63   (= DMR 2024-2025 Table 4.2 "Short" = 157; 3yr fully gone)
    # --- DMS 2025-26 / SEU 2026 Annex 3 forward bond plan (FORECAST; no 3yr in forward plan) ---
    ("2025-26", 204, 1),   # DMS 2025-26 Table (p6): 120 (2yr) + 84 (5yr)
    ("2026-27", 190, 1),   # SEU 2026 Annex 3 plan: 110 (2yr) + 80 (5yr)
]

# FY label -> (bonds_bn, is_forecast)  -- BONDS = 10yr+30yr+ultra+RRB+Green (= DMR "Long" + Green); TRUE gross flow
ISSUANCE_FLOW_BONDS: list[tuple[str, float, int]] = [
    # --- DMR Table 4.1 long-sector bonds + Green, gross FLOW (HISTORY) ---
    # (10yr + 30yr + ultra-long + Real Return Bonds + Green; ultra-long $0 since
    #  FY2022-23; RRB program discontinued Nov 2022; Green folded in per research file.)
    ("2019-20", 21, 0),    # DMR 2020-2021 Table 4.1: 14 (10yr) + 6 (30yr) + 0 + 1.8 (RRB) + 0 (Green)
    ("2020-21", 107, 0),   # 74 + 32 + 0 + 1.4 + 0
    ("2021-22", 117, 0),   # 79 + 28 + 4 (ultra) + 1 (RRB) + 5 (Green)
    ("2022-23", 67, 0),    # 52 + 15 + 0 + 1 + 0
    ("2023-24", 65, 0),    # 47 + 14 + 0 + 0 + 4 (Green)  (= DMR Table 4.2 "Long" 61 + Green 4)
    ("2024-25", 84, 0),    # 63 + 17 + 0 + 0 + 4 (Green)  (= DMR Table 4.2 "Long" 80 + Green 4)
    # --- DMS 2025-26 / SEU 2026 Annex 3 forward bond plan (FORECAST; no ultra-long or RRB planned) ---
    ("2025-26", 112, 1),   # DMS 2025-26 Table (p6): 84 (10yr) + 24 (30yr) + 4 (Green)
    ("2026-27", 108, 1),   # SEU 2026 Annex 3 plan: 80 (10yr) + 24 (30yr) + 4 (Green)
]


# ---------------------------------------------------------------------------
# CSV + META WRITERS
# ---------------------------------------------------------------------------

def _write_csv_and_meta(
    slug: str,
    rows: list[dict],
    meta: dict,
    out_dir: Path,
) -> tuple[Path, Path]:
    """Write <slug>.csv and <slug>.meta.json to out_dir. Return (csv_path, meta_path)."""
    out_dir.mkdir(parents=True, exist_ok=True)

    df = pd.DataFrame(rows)
    csv_path = out_dir / f"{slug}.csv"
    df.to_csv(csv_path, index=False)
    logger.info("frt_fiscal: wrote %s (%d rows)", csv_path, len(df))

    meta_path = out_dir / f"{slug}.meta.json"
    meta_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info("frt_fiscal: wrote %s", meta_path)

    return csv_path, meta_path


def build_frt_fiscal_series(out_dir: Optional[Path] = None) -> dict[str, Path]:
    """Materialize all ten indicator series (10 CSVs + 10 meta.json files).

    Returns a dict of slug -> csv_path for the caller to report.
    """
    if out_dir is None:
        out_dir = DATA_DERIVED

    now_iso = datetime.now(timezone.utc).isoformat()
    written: dict[str, Path] = {}

    # --- Series 1: operating balance ($B) ---
    rows = [
        {
            "date": _fy_to_iso(fy),
            "value": opex_bn,
            "is_forecast": is_fc,
            "fy_label": fy,
        }
        for fy, opex_bn, _capex, is_fc in BALANCE_OPEX_CAPEX
    ]
    meta = {
        "name": "frt_federal_balance_opex",
        "source": (
            "Department of Finance Canada -- Spring Economic Update 2026, "
            "Annex 1, Table A1.5 (Operating Balance)"
        ),
        "source_url": (
            "https://budget.canada.ca/update-miseajour/2026/"
            "report-rapport/anx1-en.html"
        ),
        "units": "CAD billions (signed: positive = surplus, negative = deficit)",
        "frequency": "annual",
        "vintage": "2026-04-28",
        "fetched_at": now_iso,
        "schema_version": 1,
        "is_forecast_field": "is_forecast",
        "is_forecast_note": (
            "is_forecast=0 means actual/history; is_forecast=1 means SEU 2026 projection. "
            "FY2024-25 (is_forecast=0) has null value -- no official opex/capex split "
            "exists for that year (Capital Budgeting Framework introduced FY2025-26)."
        ),
        "notes": (
            "SEU 2026 Annex 1 Table A1.5 official DoF operating balance series. "
            "The operating balance excludes capital investment (A1.4); the two sum "
            "(within rounding) to the total budgetary balance (A1.7). "
            "PBO identifies a ~$94B reclassification gap vs DoF over the 2024-25 "
            "to 2029-30 horizon -- the PBO view would show deeper operating deficits. "
            "This series is the PRIMARY DoF official view; PBO reclassification is a "
            "contested-definition annotation, not a competing primary series."
        ),
    }
    csv_path, _ = _write_csv_and_meta("frt_federal_balance_opex", rows, meta, out_dir)
    written["frt_federal_balance_opex"] = csv_path

    # --- Series 2: capital investment ($B) ---
    rows = [
        {
            "date": _fy_to_iso(fy),
            "value": capex_bn,
            "is_forecast": is_fc,
            "fy_label": fy,
        }
        for fy, _opex, capex_bn, is_fc in BALANCE_OPEX_CAPEX
    ]
    meta = {
        "name": "frt_federal_balance_capex",
        "source": (
            "Department of Finance Canada -- Spring Economic Update 2026, "
            "Annex 1, Table A1.4 (Capital Investments)"
        ),
        "source_url": (
            "https://budget.canada.ca/update-miseajour/2026/"
            "report-rapport/anx1-en.html"
        ),
        "units": "CAD billions (positive = spending)",
        "frequency": "annual",
        "vintage": "2026-04-28",
        "fetched_at": now_iso,
        "schema_version": 1,
        "is_forecast_field": "is_forecast",
        "is_forecast_note": (
            "is_forecast=0 means actual/history; is_forecast=1 means SEU 2026 projection. "
            "FY2024-25 has null value -- no official opex/capex split for pre-framework year."
        ),
        "notes": (
            "SEU 2026 Annex 1 Table A1.4 official capital investment series. "
            "The total $311.3B DoF capital claim over FY2024-25 to FY2029-30 is contested "
            "by PBO (~$217.3B under stricter international-standard definition, a ~$94B gap). "
            "See pipeline comment block for PBO reclassification context."
        ),
    }
    csv_path, _ = _write_csv_and_meta("frt_federal_balance_capex", rows, meta, out_dir)
    written["frt_federal_balance_capex"] = csv_path

    # --- Series 3: revenues % of GDP ---
    rows = [
        {
            "date": _fy_to_iso(fy),
            "value": pct,
            "is_forecast": is_fc,
            "fy_label": fy,
        }
        for fy, pct, is_fc in REVENUES_PCT_GDP
    ]
    meta = {
        "name": "frt_revenues_pct_gdp",
        "source": (
            "History: FRT 2025 (Fiscal Reference Tables, October 2025), Table 2. "
            "Forecast: computed from SEU 2026 Annex 1 Table A1.7 revenues $B "
            "divided by SEU 2026 stated nominal GDP $B (calendar-year-start denominator)."
        ),
        "source_url": (
            "https://www.canada.ca/en/department-finance/services/publications/"
            "fiscal-reference-tables/2025.html"
        ),
        "units": "percent of GDP",
        "frequency": "annual",
        "vintage": "History: October 2025 (FRT 2025). Forecast: April 2026 (SEU 2026).",
        "fetched_at": now_iso,
        "schema_version": 1,
        "is_forecast_field": "is_forecast",
        "is_forecast_note": (
            "is_forecast=0 means FRT 2025 actual. is_forecast=1 means derived "
            "from SEU 2026 Annex 1 (numerator from A1.7 revenues $B; denominator "
            "from SEU calendar-year nominal GDP $B). History and forecast use different "
            "GDP vintages (Oct-2025 vs Apr-2026); a vintage-seam annotation is required "
            "at the FY2024-25/FY2025-26 boundary."
        ),
        "vintage_seam_note": (
            "FRT FY2024-25 actual = 16.6% (Oct-2025 GDP vintage). "
            "SEU FY2025-26 forecast = 15.77% (Apr-2026 GDP vintage). "
            "The 0.9pp step is partly a genuine projected decline and partly "
            "the GDP-vintage offset (~0.1-0.5pp). Chart must carry a seam annotation."
        ),
        "notes": (
            "FRT 2025 Table 2 actuals verified via pypdf extract from locally-cached "
            "data/raw/fiscal/frt_2025.pdf. History extended to FY1983-84 (first full "
            "accrual year) in 2026-06-02 update. SEU 2026 Annex 1 WebFetched and "
            "verified by researcher 2026-06-02. Forecast %GDP denominators independently "
            "verified by back-out from SEU's own debt $B / debt %GDP row (reproduces SEU "
            "debt ratios exactly to 0.1pp -- see research file)."
        ),
        "basis_break": {
            "year": "1983-84",
            "description": (
                "Full accrual accounting introduced FY1983-84. Pre-1983-84 data excluded. "
                "Revenues %GDP is the most stable indicator across accounting regimes "
                "(revenues are accrual-neutral vs expenses), but the series is bounded at "
                "FY1983-84 to match the other indicators on the same axis."
            ),
        },
    }
    csv_path, _ = _write_csv_and_meta("frt_revenues_pct_gdp", rows, meta, out_dir)
    written["frt_revenues_pct_gdp"] = csv_path

    # --- Series 4: program expenses % of GDP ---
    rows = [
        {
            "date": _fy_to_iso(fy),
            "value": pct,
            "is_forecast": is_fc,
            "fy_label": fy,
        }
        for fy, pct, is_fc in PROGRAM_EXP_PCT_GDP
    ]
    meta = {
        "name": "frt_program_exp_pct_gdp",
        "source": (
            "History: FRT 2025 (Fiscal Reference Tables, October 2025), Table 8 "
            "('Expenses, per cent of GDP'), program expenses excl. net actuarial losses column. "
            "Forecast: computed from SEU 2026 Annex 1 Table A1.7 program-expenses-ex-actuarial "
            "$B divided by SEU 2026 stated nominal GDP $B."
        ),
        "source_url": (
            "https://www.canada.ca/en/department-finance/services/publications/"
            "fiscal-reference-tables/2025.html"
        ),
        "units": "percent of GDP",
        "frequency": "annual",
        "vintage": "History: October 2025 (FRT 2025). Forecast: April 2026 (SEU 2026).",
        "fetched_at": now_iso,
        "schema_version": 1,
        "is_forecast_field": "is_forecast",
        "is_forecast_note": (
            "is_forecast=0 means FRT 2025 actual. is_forecast=1 means derived "
            "from SEU 2026 Annex 1. Same GDP vintage conventions as frt_revenues_pct_gdp."
        ),
        "covid_note": (
            "FY2020-21 value = 28.1% is a genuine spike (COVID emergency spending), "
            "not a basis break. Chart should annotate this data point."
        ),
        "metric_definition": (
            "Program expenses EXCLUDING net actuarial losses and EXCLUDING public debt charges. "
            "This is the preferred indicator for discretionary + transfer spending because it "
            "isolates policy choices from debt-service cost (public debt charges are rate-driven "
            "and shown separately in other indicators). Pre-2008-09 the actuarial sub-category "
            "did not exist as a separate line; the series is internally consistent."
        ),
        "basis_break": {
            "year": "1983-84",
            "description": (
                "Full accrual accounting introduced FY1983-84. Pre-1983-84 data excluded. "
                "Additionally, the FY2008-09 reclassification of net actuarial losses into a "
                "separate category affects the sub-components but NOT this series' total, because "
                "the total program-expenses line is used throughout (pre-2008-09 actuals had "
                "actuarial folded into direct program expenses; the total is consistent)."
            ),
        },
        "historical_context": (
            "Spending consolidation 1992-93 to 1999-00: program expenses fell from 17.0% to "
            "11.8% of GDP (Chretien/Martin cuts). Post-2001-02 expansion (health transfers, "
            "social spending): rose from 11.9% to 13.4% by 2004-05. "
            "GFC stimulus: peaked at 15.9% in 2009-10 (stimulus), then consolidated. "
            "COVID peak: 28.1% in FY2020-21 (CERB + wage subsidies). "
            "Post-COVID normalization: 15.7-16.2% range FY2022-25."
        ),
    }
    csv_path, _ = _write_csv_and_meta("frt_program_exp_pct_gdp", rows, meta, out_dir)
    written["frt_program_exp_pct_gdp"] = csv_path

    # --- Series 5: federal debt % of GDP ---
    rows = [
        {
            "date": _fy_to_iso(fy),
            "value": pct,
            "is_forecast": is_fc,
            "fy_label": fy,
        }
        for fy, pct, is_fc in FEDERAL_DEBT_PCT_GDP
    ]
    meta = {
        "name": "frt_federal_debt_pct_gdp",
        "source": (
            "History: FRT 2025 (Fiscal Reference Tables, October 2025), Table 2, "
            "federal debt (accumulated deficit) % of GDP column. "
            "Forecast: SEU 2026 Annex 1 Table A1.7 published %GDP row (Tier A -- used as-is)."
        ),
        "source_url": (
            "https://www.canada.ca/en/department-finance/services/publications/"
            "fiscal-reference-tables/2025.html"
        ),
        "units": "percent of GDP",
        "frequency": "annual",
        "vintage": "History: October 2025 (FRT 2025). Forecast: April 2026 (SEU 2026).",
        "fetched_at": now_iso,
        "schema_version": 1,
        "is_forecast_field": "is_forecast",
        "is_forecast_note": (
            "is_forecast=0 means FRT 2025 actual (Oct-2025 GDP vintage). "
            "is_forecast=1 means SEU 2026 Annex 1 published ratio (Apr-2026 GDP vintage). "
            "The history/forecast GDP denominator seam at FY2024-25/FY2025-26 is ~0.1pp "
            "(FRT 41.2% vs SEU 41.1% for FY2024-25) -- benign for a line chart."
        ),
        "metric_definition": (
            "Federal debt = accumulated deficit = net debt minus net non-financial assets. "
            "FEDERAL ONLY (excludes provincial/territorial/local and CPP/QPP). "
            "NOT comparable to general-government gross debt (~91-107% from Fitch/OECD/IMF). "
            "This is the Government of Canada's own headline measure used in all Budget "
            "and FES documents, and the denominator for the fiscal anchors."
        ),
        "vintage_reconciliation": (
            "FY2024-25 federal debt ~$1,266.5B in all vintages (level agrees). "
            "%GDP differs: FRT 41.2% / SEU 40.7% / Budget 2025 42.4% -- "
            "three GDP denominators. This series: FRT actuals through FY2024-25 "
            "(41.2%), SEU forecast from FY2025-26 (41.1% onward). "
            "Do NOT use the existing data/derived/fiscal_debt_to_gdp.csv -- "
            "that file carries Budget 2025 projections with an incompatible GDP vintage."
        ),
        "historical_context": (
            "Post-accrual series (full accrual introduced 1983-84); pre-1983-84 not comparable. "
            "Post-accrual peak: 66.6% in FY1995-96 (FRT Table 2 primary -- earlier research "
            "note stated FY1994-95 at 66.2%; FY1995-96 is the true peak per the primary table). "
            "Pre-GFC trough: 28.2% in FY2008-09. COVID peak: 47.2% in FY2020-21. "
            "History extends from FY1983-84 (42 years of comparable accrual-basis data)."
        ),
        "basis_break": {
            "year": "1983-84",
            "description": (
                "Full accrual accounting introduced FY1983-84. Data before this year are on a "
                "modified-cash/hybrid basis and are NOT plotted in this series. Chart-builders "
                "should annotate the start of the series at FY1983-84 if needed."
            ),
        },
    }
    csv_path, _ = _write_csv_and_meta("frt_federal_debt_pct_gdp", rows, meta, out_dir)
    written["frt_federal_debt_pct_gdp"] = csv_path

    # --- Series 6: outstanding marketable bonds stock ($M) ---
    rows = [
        {
            "date": _fy_to_iso(fy),
            "value": bonds_m,
            "is_forecast": is_fc,
            "fy_label": fy,
        }
        for fy, bonds_m, is_fc in ISSUANCE_BONDS
    ]
    meta = {
        "name": "frt_issuance_bonds",
        "source": (
            "FRT 2025 (Fiscal Reference Tables, October 2025), Table 16 "
            "'Unmatured debt held by outside parties' -- "
            "domestic + foreign marketable bonds combined."
        ),
        "source_url": (
            "https://www.canada.ca/en/department-finance/services/publications/"
            "fiscal-reference-tables/2025.html"
        ),
        "units": "CAD millions (end of fiscal year)",
        "frequency": "annual",
        "vintage": "October 2025 (FRT 2025)",
        "fetched_at": now_iso,
        "schema_version": 1,
        "is_forecast_field": "is_forecast",
        "is_forecast_note": (
            "All points is_forecast=0 (HISTORY). No forward bond stock available -- "
            "SEU 2026 Annex 3 bond data is gross issuance flow, not end-year stock."
        ),
        "notes": (
            "Domestic bonds + foreign bonds combined. FY2024-25 split: "
            "1,163,045M domestic + 29,383M foreign = 1,192,428M combined. "
            "FY2015-16 to FY2017-18 rows are TIER A PENDING RE-PULL "
            "(same pypdf extract as FY2018-19+ but not in researcher's published subset). "
            "The three buckets (bonds + bills + retail) do NOT sum to FRT Table 16 Total "
            "(which also includes CPP bonds and amortized-cost adjustments)."
        ),
    }
    csv_path, _ = _write_csv_and_meta("frt_issuance_bonds", rows, meta, out_dir)
    written["frt_issuance_bonds"] = csv_path

    # --- Series 7: outstanding treasury bills stock ($M) ---
    rows = [
        {
            "date": _fy_to_iso(fy),
            "value": bills_m,
            "is_forecast": is_fc,
            "fy_label": fy,
        }
        for fy, bills_m, is_fc in ISSUANCE_TBILLS
    ]
    meta = {
        "name": "frt_issuance_tbills",
        "source": (
            "History: FRT 2025 Table 16, treasury bills column. "
            "Forecast: SEU 2026 Annex 3 T-bill stock end-year targets "
            "(~$286B FY2025-26, ~$268B FY2026-27)."
        ),
        "source_url": (
            "https://www.canada.ca/en/department-finance/services/publications/"
            "fiscal-reference-tables/2025.html"
        ),
        "units": "CAD millions (end of fiscal year)",
        "frequency": "annual",
        "vintage": "History: October 2025 (FRT 2025). Forecast: April 2026 (SEU 2026 Annex 3).",
        "fetched_at": now_iso,
        "schema_version": 1,
        "is_forecast_field": "is_forecast",
        "is_forecast_note": (
            "is_forecast=0 means FRT 2025 actual. is_forecast=1 means SEU 2026 Annex 3 "
            "T-bill STOCK TARGET (not gross flow). SEU says ~$286B end-FY2025-26 and "
            "~$268B end-FY2026-27 (revised down from $291B Budget 2025). "
            "These are the only forward stock points available; no forward bond stock exists."
        ),
        "notes": (
            "T-bill stock (not gross issuance). T-bills are money-market instruments (<1yr) "
            "that roll multiple times per year; gross annual T-bill issuance is far larger "
            "than the outstanding stock. FY2015-16 to FY2017-18: TIER A PENDING RE-PULL."
        ),
    }
    csv_path, _ = _write_csv_and_meta("frt_issuance_tbills", rows, meta, out_dir)
    written["frt_issuance_tbills"] = csv_path

    # --- Series 8: outstanding retail debt stock ($M) ---
    rows = [
        {
            "date": _fy_to_iso(fy),
            "value": retail_m,
            "is_forecast": is_fc,
            "fy_label": fy,
        }
        for fy, retail_m, is_fc in ISSUANCE_RETAIL
    ]
    meta = {
        "name": "frt_issuance_retail",
        "source": (
            "FRT 2025 (Fiscal Reference Tables, October 2025), Table 16, "
            "retail debt column (Canada Savings Bonds / Canada Premium Bonds)."
        ),
        "source_url": (
            "https://www.canada.ca/en/department-finance/services/publications/"
            "fiscal-reference-tables/2025.html"
        ),
        "units": "CAD millions (end of fiscal year)",
        "frequency": "annual",
        "vintage": "October 2025 (FRT 2025)",
        "fetched_at": now_iso,
        "schema_version": 1,
        "is_forecast_field": "is_forecast",
        "is_forecast_note": (
            "All points is_forecast=0 (HISTORY). No forward retail stock -- "
            "CSB/CPB program in run-off; no new issuance planned."
        ),
        "notes": (
            "Canada Savings Bonds (CSB) and Canada Premium Bonds (CPB) -- program wound down. "
            "FY2021-22 to FY2023-24 show 0 (program effectively closed). "
            "FY2024-25 $4,681M re-appearance may be a reclassification in Table 16 -- "
            "CONFIRM ON HUMAN PDF RE-PULL. FY2015-16 to FY2017-18: TIER A PENDING RE-PULL."
        ),
    }
    csv_path, _ = _write_csv_and_meta("frt_issuance_retail", rows, meta, out_dir)
    written["frt_issuance_retail"] = csv_path

    # --- Series 11/12/13: GROSS ISSUANCE FLOW by maturity bucket ($B) ---
    # Different metric from Series 6/7/8 (stock). These three are wired to panel-10.
    _flow_caveat = (
        "BILLS bucket = year-end Treasury-bill STOCK (DMR's own Table 4.1 convention), "
        "NOT gross T-bill auction flow. The NOTES and BONDS buckets ARE true gross "
        "issuance flow. Do NOT label the BILLS bucket as 'auctioned' or 'issued' in the "
        "flow sense -- gross bill auctions were ~$663B in FY2024-25 (~2.3x the $285B "
        "stock). Safe framing follows the DMR label: 'gross issuance of bonds and bills.' "
        "Headline total (BILLS+NOTES+BONDS) is a hybrid: gross bond flow + year-end bill stock."
    )
    _flow_source_url = "https://budget.canada.ca/update-miseajour/2026/report-rapport/anx3-en.html"
    _flow_vintage = (
        "History: latest-vintage Debt Management Report Table 4.1 (pub. 2020-2025). "
        "Forecast: DMS 2025-26 (4 Nov 2025) for FY2025-26; SEU 2026 Annex 3 (28 Apr 2026) "
        "for FY2026-27."
    )

    # Series 12: BILLS (T-bill year-end stock; DMR convention)
    rows = [
        {"date": _fy_to_iso(fy), "value": val, "is_forecast": is_fc, "fy_label": fy}
        for fy, val, is_fc in ISSUANCE_FLOW_BILLS
    ]
    meta = {
        "name": "frt_issuance_flow_bills",
        "source": (
            "GROSS ISSUANCE FLOW, BILLS bucket. History: Debt Management Report "
            "Table 4.1 'Treasury Bills' line (year-end bill STOCK -- DMR convention). "
            "Forecast: DMS 2025-26 / SEU 2026 Annex 3 T-bill stock target."
        ),
        "source_url": _flow_source_url,
        "units": "CAD billions (gross issuance per fiscal year; BILLS = year-end T-bill stock)",
        "frequency": "annual",
        "vintage": _flow_vintage,
        "fetched_at": now_iso,
        "schema_version": 1,
        "is_forecast_field": "is_forecast",
        "is_forecast_note": (
            "is_forecast=0 = DMR actual (FY2019-20 to FY2024-25). is_forecast=1 = planned "
            "(FY2025-26 DMS plan $296B target; FY2026-27 SEU 2026 Annex 3 $268B target)."
        ),
        "methodology_caveat": _flow_caveat,
        "notes": (
            "Tier A. Full per-cell source ledger in "
            "claude-ref/research/fiscal_redo/issuance_flow_series.md. BILLS = Treasury bills "
            "(<1yr). This is the year-end bill STOCK, the same line the DMR carries in its "
            "'Bonds and Bills' Table 4.1; NOT gross bill auctions. See methodology_caveat."
        ),
    }
    csv_path, _ = _write_csv_and_meta("frt_issuance_flow_bills", rows, meta, out_dir)
    written["frt_issuance_flow_bills"] = csv_path

    # Series 12b: NOTES (2/3/5yr bonds = DMR "Short" bucket; true gross flow)
    rows = [
        {"date": _fy_to_iso(fy), "value": val, "is_forecast": is_fc, "fy_label": fy}
        for fy, val, is_fc in ISSUANCE_FLOW_NOTES
    ]
    meta = {
        "name": "frt_issuance_flow_notes",
        "source": (
            "GROSS ISSUANCE FLOW, NOTES bucket (= 2yr + 3yr + 5yr bonds = DMR 'Short "
            "(2,3,5-year sectors)' bucket). History: DMR Table 4.1 short-sector lines. "
            "Forecast: DMS 2025-26 / SEU 2026 Annex 3 short-bond plan."
        ),
        "source_url": _flow_source_url,
        "units": "CAD billions (gross issuance flow per fiscal year)",
        "frequency": "annual",
        "vintage": _flow_vintage,
        "fetched_at": now_iso,
        "schema_version": 1,
        "is_forecast_field": "is_forecast",
        "is_forecast_note": (
            "is_forecast=0 = DMR actual (FY2019-20 to FY2024-25). is_forecast=1 = planned "
            "(FY2025-26 DMS plan; FY2026-27 SEU 2026 Annex 3 plan). No 3yr in forward plan "
            "(phased out after FY2023-24); forward NOTES = 2yr + 5yr only."
        ),
        "methodology_caveat": _flow_caveat,
        "notes": (
            "Tier A. Full per-cell source ledger in "
            "claude-ref/research/fiscal_redo/issuance_flow_series.md. 'NOTES' is OUR "
            "aggregation label, NOT a GoC instrument class -- Canada issues T-bills, "
            "marketable bonds by tenor, RRB and Green bonds; there is no 'note'. NOTES = "
            "the 2/3/5-year bond sectors (= the DMR's 'Short' bucket). TRUE gross flow."
        ),
    }
    csv_path, _ = _write_csv_and_meta("frt_issuance_flow_notes", rows, meta, out_dir)
    written["frt_issuance_flow_notes"] = csv_path

    # Series 13: BONDS (10yr+30yr+ultra+RRB+Green = DMR "Long" + Green; true gross flow)
    rows = [
        {"date": _fy_to_iso(fy), "value": val, "is_forecast": is_fc, "fy_label": fy}
        for fy, val, is_fc in ISSUANCE_FLOW_BONDS
    ]
    meta = {
        "name": "frt_issuance_flow_bonds",
        "source": (
            "GROSS ISSUANCE FLOW, BONDS bucket (= 10yr + 30yr + ultra-long + Real Return "
            "Bonds + Green bonds = DMR 'Long (10-year+)' bucket + Green). History: DMR "
            "Table 4.1 long-sector lines. Forecast: DMS 2025-26 / SEU 2026 Annex 3 long-bond plan."
        ),
        "source_url": _flow_source_url,
        "units": "CAD billions (gross issuance flow per fiscal year)",
        "frequency": "annual",
        "vintage": _flow_vintage,
        "fetched_at": now_iso,
        "schema_version": 1,
        "is_forecast_field": "is_forecast",
        "is_forecast_note": (
            "is_forecast=0 = DMR actual (FY2019-20 to FY2024-25). is_forecast=1 = planned "
            "(FY2025-26 DMS plan; FY2026-27 SEU 2026 Annex 3 plan). No ultra-long or RRB "
            "in forward plan; forward BONDS = 10yr + 30yr + Green."
        ),
        "methodology_caveat": _flow_caveat,
        "notes": (
            "Tier A. Full per-cell source ledger in "
            "claude-ref/research/fiscal_redo/issuance_flow_series.md. BONDS = DMR 'Long "
            "(10-year+)' line + Green bonds (issued at 10yr+ tenors in Canada). Ultra-long "
            "$0 since FY2022-23; RRB program discontinued Nov 2022. TRUE gross flow. "
            "Reconciliation: BILLS + NOTES + BONDS = DMR 'Total Gross Issuance' each year "
            "(FY2024-25: 285+157+84=526; FY2023-24: 267+139+65=471)."
        ),
    }
    csv_path, _ = _write_csv_and_meta("frt_issuance_flow_bonds", rows, meta, out_dir)
    written["frt_issuance_flow_bonds"] = csv_path

    # --- Series 9: federal budgetary balance TOTAL ($B) ---
    rows = [
        {
            "date": _fy_to_iso(fy),
            "value": balance_bn,
            "is_forecast": is_fc,
            "fy_label": fy,
        }
        for fy, balance_bn, is_fc in BALANCE_TOTAL
    ]
    meta = {
        "name": "frt_federal_balance_total",
        "source": (
            "History: FRT 2025 (Fiscal Reference Tables, October 2025), Table 1 "
            "('Fiscal transactions, millions of dollars'), 'Budgetary surplus or "
            "deficit (-)' total column (revenues minus program expenses excl. "
            "actuarial minus public debt charges minus net actuarial losses). "
            "Forecast: SEU 2026 (Spring Economic Update, April 28 2026), Annex 1 "
            "Table A1.7, budgetary balance row."
        ),
        "source_url": (
            "https://www.canada.ca/en/department-finance/services/publications/"
            "fiscal-reference-tables/2025.html"
        ),
        "units": "CAD billions (signed: positive = surplus, negative = deficit)",
        "frequency": "annual",
        "vintage": "History: October 2025 (FRT 2025). Forecast: April 2026 (SEU 2026).",
        "fetched_at": now_iso,
        "schema_version": 1,
        "is_forecast_field": "is_forecast",
        "is_forecast_note": (
            "is_forecast=0 means FRT 2025 actual (FY1983-84 to FY2024-25, extended from "
            "prior FY2006-07 start). is_forecast=1 means SEU 2026 Annex 1 Table A1.7 "
            "published projection (FY2025-26 to FY2030-31)."
        ),
        "derivation_note": (
            "History values converted from $M (FRT Table 1) to $B, rounded to 1 "
            "decimal. Raw $M values preserved in pipeline/fetch/frt_fiscal_series.py "
            "inline comments for traceability. Cross-checks: "
            "FY2024-25: 510,951 - 489,869 - 53,410 - 4,020 = -36,348M = -36.3B (matches SEU). "
            "FY1983-84: 65,261 - 77,194 - 20,430 = -32,363M = -32.4B. "
            "FY1997-98: 160,864 - 114,785 - 43,120 = +2,959M = +3.0B (first surplus). "
            "Forecast values are the SEU's own published budgetary balance row."
        ),
        "historical_context": (
            "Deepest pre-accrual-era deficit: FY1984-85 (-$37.2B / -8.0% GDP). "
            "Consolidation era: FY1995-96 to FY2000-01 (deficits to surpluses). "
            "First surplus post-accrual: FY1997-98 (+$3.0B / +0.3% GDP). "
            "Surplus peak: FY2000-01 (+$19.9B / +1.8% GDP). "
            "GFC trough: FY2009-10 (-$56.4B / -3.6% GDP). "
            "COVID peak: FY2020-21 (-$327.7B / -14.8% GDP). "
            "NOTE: $B comparisons across the full 40-year history are misleading due to "
            "economy-size growth (~6-7x). Use frt_federal_balance_pct_gdp for long-horizon charts."
        ),
        "accounting_notes": (
            "Full accrual accounting from FY1983-84; pre-1983-84 not comparable. "
            "Net actuarial losses reclassified as a separate expense category in "
            "FY2019-20; FY2008-09 to FY2018-19 restated -- the total budgetary balance "
            "is consistent across the full history because it includes net actuarial "
            "losses in all years. PS 3280 (Asset Retirement Obligations) added "
            "$5,379M to the accumulated deficit in FY2021-22 but does NOT affect the "
            "annual budgetary balance (it is an opening-balance adjustment). "
            "Financial-instruments standard (FY2022-23) excludes remeasurement gains/"
            "losses from the budgetary balance by definition -- no impact on this series."
        ),
    }
    csv_path, _ = _write_csv_and_meta("frt_federal_balance_total", rows, meta, out_dir)
    written["frt_federal_balance_total"] = csv_path

    # --- Series 10: budgetary balance % of GDP ---
    rows = [
        {
            "date": _fy_to_iso(fy),
            "value": pct,
            "is_forecast": is_fc,
            "fy_label": fy,
        }
        for fy, pct, is_fc in BALANCE_PCT_GDP
    ]
    meta = {
        "name": "frt_federal_balance_pct_gdp",
        "source": (
            "History: FRT 2025 (Fiscal Reference Tables, October 2025), Table 2, "
            "'Budgetary surplus or deficit (-)' per cent of GDP column, PDF page 9. "
            "Forecast: computed from SEU 2026 Annex 1 Table A1.7 total balance $B "
            "divided by SEU 2026 stated nominal GDP $B (calendar-year-start denominator)."
        ),
        "source_url": (
            "https://www.canada.ca/en/department-finance/services/publications/"
            "fiscal-reference-tables/2025.html"
        ),
        "units": "percent of GDP (signed: positive = surplus, negative = deficit)",
        "frequency": "annual",
        "vintage": "History: October 2025 (FRT 2025). Forecast: April 2026 (SEU 2026).",
        "fetched_at": now_iso,
        "schema_version": 1,
        "is_forecast_field": "is_forecast",
        "is_forecast_note": (
            "is_forecast=0 means FRT 2025 actual (FY1983-84 to FY2024-25, 42 years). "
            "is_forecast=1 means derived from SEU 2026 (total balance $B / SEU GDP $B). "
            "Same GDP vintage conventions as frt_revenues_pct_gdp and frt_federal_debt_pct_gdp."
        ),
        "derivation_note": (
            "History: read directly from FRT 2025 Table 2 %GDP column (Tier A, primary source). "
            "Pre-2008-09 values are the 'surplus/deficit excl. actuarial' column (no separate "
            "actuarial line existed; these are the total balance figures). "
            "Forecast: SEU A1.7 total balance $B / SEU calendar-year nominal GDP $B * 100. "
            "Denominator: calendar year the fiscal year begins in (same as frt_revenues_pct_gdp). "
            "Derivation: -66.9/3243=-2.06, -65.3/3372=-1.94, -63.1/3496=-1.80, "
            "-57.7/3630=-1.59, -56.2/3772=-1.49, -53.2/3917=-1.36."
        ),
        "vintage_seam_note": (
            "History through FY2024-25 uses FRT 2025 Oct-2025 GDP vintage (-1.2%). "
            "SEU FY2025-26 forecast uses Apr-2026 GDP vintage (-2.06%). "
            "The step at the boundary is a genuine projected widening (SEU total deficit "
            "-$66.9B vs FY2024-25 -$36.3B actuals) -- larger than the ~0.1pp GDP-vintage "
            "offset. No seam annotation required (the step is real, not an artifact)."
        ),
        "historical_context": (
            "Full accrual era (FY1983-84 onward). Deepest: FY1984-85 at -8.0% GDP. "
            "Consolidation: Mulroney-era cuts narrowed the deficit from -8.0% (1984-85) "
            "to -3.6% (1995-96); Chretien/Martin eliminated it by 1997-98. "
            "Surplus era: FY1997-98 (+0.3%) to FY2007-08 (+0.6%), peaking +1.8% (2000-01). "
            "GFC: -3.6% in FY2009-10. COVID: -14.8% in FY2020-21 (all-era record). "
            "Recent: stabilizing at -1.2% in FY2024-25."
        ),
        "basis_break": {
            "year": "1983-84",
            "description": (
                "Full accrual accounting introduced FY1983-84. Data before this year are not "
                "plotted. Chart-builders should annotate the series start at FY1983-84."
            ),
        },
        "covid_note": (
            "FY2020-21 value = -14.8% of GDP is a genuine event (COVID emergency spending), "
            "not a basis break. Chart should annotate this data point."
        ),
    }
    csv_path, _ = _write_csv_and_meta("frt_federal_balance_pct_gdp", rows, meta, out_dir)
    written["frt_federal_balance_pct_gdp"] = csv_path

    logger.info("frt_fiscal: materialized %d series", len(written))
    return written


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    result = build_frt_fiscal_series()
    for slug, p in result.items():
        print(f"  {slug}: {p}")
