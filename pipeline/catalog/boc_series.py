"""BoC Valet series catalog.

Each entry maps an output `name` (filename slug under `data/raw/`) to a
BocSpec carrying the Valet series key, start_date, units, frequency, section,
cadence-tag (daily / monthly / etc.) and any quirks.

Probe outcomes (recorded for audit):
    - INDINF_OUTGAPMPR_Q       : FOUND (Current MPR output gap, %). Re-verified 2026-05-11:
                                  rows return through Q4 2025, value -1.0 (negative output gap).
    - MPR_2025M04_CPI_TAX_S1    : FOUND (Total CPI excluding indirect taxes; April-2025-MPR vintage).
                                  Re-verified 2026-05-11: 15 rows, tail 2025-03-01 = 2.1%.
    - MPR_2026M01/04_CPI_TAX_S1 : NOT FOUND (no newer vintage exists yet as of 2026-05-10/11).
    - FXUSDCAD / FXEURCAD / FXGBPCAD / FXJPYCAD : ALL FOUND. fxusdcad re-verified 2026-05-11.
    - CEER family (CEER_BROADN, CEER_BROADNM, CEER_BROAD_XUSM, ...) : FOUND. CEER_BROADN
                                  re-verified 2026-05-11: 615 rows through 2026-05-08, value 113.51.
    - V80691344 (3-month T-bill, weekly) : FOUND. Re-verified 2026-05-11: 123 rows through
                                  2026-05-06, value 2.29.
    - M.BCPI (commodity index, daily) : FOUND. Re-verified 2026-05-11: tail 2026-04-01 = 757.06.
    - M.BCNEI (non-energy commodity index) : NOT FOUND under that key. Re-probed 2026-05-12
      via /valet/lists/series/json; the correct Valet identifier is **M.BCNE**
      (label "Monthly BCPI Excluding Energy - v52673497"). The legacy key M.BCNEI
      404s on /observations. Catalog updated to M.BCNE; the slot keeps the
      `bcnei` slug for stable filenames and existing references.
    - Financial Conditions Index (FCI) : NOT FOUND in Valet (0 matches across 15,538 series).
      Per canon 4.6 element 6, v1 basics defers FCI to US-comparator FCIs with caveat.
    - Term Premium 10-year (GoC) : FOUND under the FVI_ namespace (re-probed 2026-05-11).
      Two flavours: FVI_TP_GOC_10Y_ACM (Adrian-Crump-Moench) and FVI_TP_GOC_10Y_SHADOWRATE
      (shadow-rate model). Both are daily, in %. Earlier probe missed these because the
      regex did not include the FVI_TP_GOC_ prefix. Per canon 4.6 element 2, register the
      ACM flavour as the headline series and the shadow-rate as a companion. No need to
      scrape the FSI page; Valet exposes the underlying series directly.
    - Canadian Financial Stress Index (FVI_FSI_CAN) : FOUND. Daily index; surfaced as a
      companion to the term-premium read on the Financial section.
    - Alberta Energy Regulator / NGX AECO (weekly bid-week) : NOT in Valet (regex match
      list on AECO|HENRY|NATGAS returned only CES "Gasoline" survey rows). NGX itself
      blocks anonymous HTTP. Alberta Economic Dashboard exposes a monthly AECO-equivalent
      Alberta reference price at C$/GJ; that is the v1 fallback (see pipeline/fetch/alberta.py).
      Weekly bid-week defers to v1.5 per canon 4.6 element 4.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class BocSpec:
    name: str                # CSV filename slug
    series_key: str          # Valet series key
    start_date: str          # ISO date string
    units: str
    frequency: str           # "daily", "weekly", "monthly", "quarterly"
    section: str
    cadence: str             # "daily" | "intraday-trading-day" | "monthly" | "quarterly"
    scale: float = 1.0
    notes: str = ""
    # MPR vintage rotation: if set, the orchestrator will attempt this list in order
    # and use the first key that returns 200-OK observations.
    vintage_fallbacks: Optional[tuple[str, ...]] = None


# ---------------------------------------------------------------------------
# Series registrations
# ---------------------------------------------------------------------------

BOC_VALET_SERIES: dict[str, BocSpec] = {

    # ----- GoC yields (Section 4.6 element 2) -----------------------------
    "yield_2yr":      BocSpec("yield_2yr",  "BD.CDN.2YR.DQ.YLD",  "1990-01-01", "%", "daily", "financial", "daily"),
    "yield_5yr":      BocSpec("yield_5yr",  "BD.CDN.5YR.DQ.YLD",  "1990-01-01", "%", "daily", "financial", "daily"),
    "yield_10yr":     BocSpec("yield_10yr", "BD.CDN.10YR.DQ.YLD", "1990-01-01", "%", "daily", "financial", "daily"),
    "yield_30yr":     BocSpec("yield_30yr", "BD.CDN.LONG.DQ.YLD", "1990-01-01", "%", "daily", "financial", "daily"),
    # 3-month T-bill (canon 4.6 -- "3-month T-bill yield" gap-fill, verified V80691344 2026-05-10)
    "tbill_3m":       BocSpec("tbill_3m", "V80691344", "1990-01-01", "%", "weekly", "financial", "daily",
                              notes="3-month Treasury bill yield, weekly. Verified label='3 month' under 'Treasury bills' description."),
    "corra_daily":    BocSpec("corra_daily", "AVG.INTWO", "2009-01-01", "%", "daily", "financial", "daily"),

    # ----- Policy rate / monetary (Section 4.5a) --------------------------
    "overnight_rate":       BocSpec("overnight_rate", "STATIC_ATABLE_V39079", "1990-01-01", "%", "monthly", "policy", "monthly"),
    "overnight_rate_daily": BocSpec("overnight_rate_daily", "V39079", "2009-04-21", "%", "daily", "policy", "daily"),

    # ----- CPI core (Section 4.2 element 2) -------------------------------
    # cpi_trim, cpi_median, cpi_common moved to StatCan catalog 2026-05-19
    # (Table 18-10-0256-01) so they refresh at the 8:30 ET CPI release rather
    # than waiting for BoC Valet's afternoon update.
    "cpix":       BocSpec("cpix", "ATOM_V41693242", "1990-01-01", "% Y/Y", "monthly", "inflation", "monthly"),
    "cpixfet":    BocSpec("cpixfet", "STATIC_CPIXFET", "1990-01-01", "% Y/Y", "monthly", "inflation", "monthly"),
    # CPI ex indirect taxes — MPR-vintage rotation (researcher memo: each MPR ships a new key).
    # We try the most recent known good key first, then fall back through the vintage history.
    "cpi_ex_indirect_taxes": BocSpec(
        name="cpi_ex_indirect_taxes",
        series_key="MPR_2025M04_CPI_TAX_S1",
        start_date="1990-01-01",
        units="Index", frequency="monthly", section="inflation", cadence="monthly",
        notes=(
            "CPI excluding indirect taxes (BoC MPR series; rotates each MPR vintage). "
            "Probe 2026-05-10: MPR_2025M04_CPI_TAX_S1 was found; MPR_2026M01 and MPR_2026M04 vintages "
            "did NOT publish a CPI_TAX series in this slot."
        ),
        vintage_fallbacks=(
            "MPR_2026M04_CPI_TAX_S1",
            "MPR_2026M01_CPI_TAX_S1",
            "MPR_2025M10_CPI_TAX_S1",
            "MPR_2025M07_CPI_TAX_S1",
            "MPR_2025M04_CPI_TAX_S1",  # last known good as of probe
        ),
    ),

    # ----- Inflation expectations -----------------------------------------
    "infl_exp_consumer_1y": BocSpec("infl_exp_consumer_1y", "CES_C1_SHORT_TERM", "2014-01-01", "%", "quarterly", "inflation", "quarterly"),
    "infl_exp_consumer_5y": BocSpec("infl_exp_consumer_5y", "CES_C1_LONG_TERM",  "2014-01-01", "%", "quarterly", "inflation", "quarterly"),
    "infl_exp_above3":      BocSpec("infl_exp_above3", "ABOVE3", "2013-01-01", "%", "quarterly", "inflation", "quarterly"),
    "bos_dist_below1": BocSpec("bos_dist_below1", "INDINF_BOSBELOW1_Q", "2003-01-01", "%", "quarterly", "inflation", "quarterly"),
    "bos_dist_1to2":   BocSpec("bos_dist_1to2", "INDINF_BOS1TO2_Q", "2003-01-01", "%", "quarterly", "inflation", "quarterly"),
    "bos_dist_2to3":   BocSpec("bos_dist_2to3", "INDINF_BOS2TO3_Q", "2003-01-01", "%", "quarterly", "inflation", "quarterly"),
    "bos_dist_above3": BocSpec("bos_dist_above3", "INDINF_BOSOVER3_Q", "2003-01-01", "%", "quarterly", "inflation", "quarterly"),

    # ----- Labour / Wages -------------------------------------------------
    "lfs_micro":        BocSpec("lfs_micro", "INDINF_LFSMICRO_M", "2000-01-01", "% Y/Y", "monthly", "labour", "monthly"),

    # ----- Output gap (Section 4.1 element 5) -----------------------------
    "output_gap_mpr": BocSpec(
        name="output_gap_mpr", series_key="INDINF_OUTGAPMPR_Q", start_date="1990-01-01",
        units="%", frequency="quarterly", section="gdp", cadence="quarterly",
        notes="Current MPR output gap (%, quarterly). Verified 2026-05-10.",
    ),

    # ----- Housing (CREA via BoC FVI; cross-section duplicates ok) --------
    "crea_mls_hpi":          BocSpec("crea_mls_hpi", "FVI_CREA_MLS_HPI_CANADA", "2014-01-01",
                                     "Index, 2019=100", "monthly", "housing", "monthly",
                                     notes="National-level only via FVI. CMA-level HPI ships via CREA XLSX (pipeline.fetch.crea)."),
    "crea_snlr":             BocSpec("crea_snlr", "FVI_CREA_HOUSE_SALES_TO_NEW_LISTINGS_CANADA", "2014-01-01",
                                     "%", "monthly", "housing", "monthly"),
    "housing_affordability": BocSpec("housing_affordability", "INDINF_AFFORD_Q", "2000-01-01",
                                     "Ratio", "quarterly", "housing", "quarterly"),
    "mortgage_rate_5yr":     BocSpec("mortgage_rate_5yr", "V80691335", "1990-01-01", "%", "weekly", "housing", "weekly"),

    # ----- FX (Section 4.6 element 1) -------------------------------------
    "fxusdcad": BocSpec("fxusdcad", "FXUSDCAD", "2017-01-01", "CAD per USD", "daily", "financial", "daily",
                        notes="BoC's indicative daily close for USD/CAD. Replaces FRED DEXCAUS (which is NY noon, discontinued by BoC in 2017)."),
    "fxeurcad": BocSpec("fxeurcad", "FXEURCAD", "2017-01-01", "CAD per EUR", "daily", "financial", "daily"),
    "fxgbpcad": BocSpec("fxgbpcad", "FXGBPCAD", "2017-01-01", "CAD per GBP", "daily", "financial", "daily"),
    "fxjpycad": BocSpec("fxjpycad", "FXJPYCAD", "2017-01-01", "CAD per JPY", "daily", "financial", "daily"),

    # ----- CEER (Section 4.6 element 1) -----------------------------------
    # CEER family probed 2026-05-10. Daily nominal is what the BoC publishes on the same cadence
    # as the FX crosses; monthly real/nominal are also available if needed.
    "ceer_broad_daily":           BocSpec("ceer_broad_daily", "CEER_BROADN", "2017-01-01",
                                          "Index", "daily", "financial", "daily",
                                          notes="Daily Nominal Canadian Effective Exchange Rate (broad basket)."),
    "ceer_broad_monthly_real":    BocSpec("ceer_broad_monthly_real", "CEER_BROADM", "1992-01-01",
                                          "Index", "monthly", "financial", "monthly",
                                          notes="Monthly Real CEER (broad basket); longer history than daily."),
    "ceer_broad_excl_us_daily":   BocSpec("ceer_broad_excl_us_daily", "CEER_BROADN_XUS", "2017-01-01",
                                          "Index", "daily", "financial", "daily"),

    # ----- BoC commodity price index (Section 4.7 element 5) --------------
    "bcpi":     BocSpec("bcpi", "M.BCPI", "1972-01-01", "Index, 1972=100", "daily", "trade", "daily",
                       notes="BoC commodity price index, daily."),
    "bcnei":    BocSpec("bcnei", "M.BCNE", "1972-01-01", "Index, 1972=100", "daily", "trade", "daily",
                       notes=(
                           "BoC commodity price index, non-energy (excluding energy). "
                           "Valet key is M.BCNE (label 'Monthly BCPI Excluding Energy - v52673497'); "
                           "legacy M.BCNEI key 404s. Filename slug kept as bcnei for stability."
                       )),

    # ----- BoC Financial Stability / Vulnerability Indicators (Section 4.6 elements 2, 6) ----
    # Canon 4.6 element 2 calls for the BoC-published Canadian term-premium series at
    # the 10y, with deferral to citing the FSI page if it were not in Valet. Re-probe
    # 2026-05-11 confirmed it IS in Valet under the FVI_TP_GOC_ namespace -- so we wire
    # it directly rather than scraping the page. Two methodology variants are available;
    # ACM (Adrian-Crump-Moench) is the headline standard.
    "term_premium_10y_acm": BocSpec(
        name="term_premium_10y_acm", series_key="FVI_TP_GOC_10Y_ACM",
        start_date="2000-01-01",  # BoC FVI page hosts the ACM model from early 2000s
        units="%", frequency="daily", section="financial", cadence="daily",
        notes=(
            "BoC's Adrian-Crump-Moench (ACM) estimate of the term premium on 10-year "
            "Government of Canada bonds. Published as part of the BoC Financial "
            "Stability Indicators page. Methodology note: ACM is one model among "
            "several; cite as 'BoC ACM estimate' rather than 'the term premium'."
        ),
    ),
    "term_premium_10y_shadow": BocSpec(
        name="term_premium_10y_shadow", series_key="FVI_TP_GOC_10Y_SHADOWRATE",
        start_date="2000-01-01",
        units="%", frequency="daily", section="financial", cadence="daily",
        notes=(
            "BoC shadow-rate model estimate of the term premium on 10-year GoC bonds. "
            "Companion to the ACM estimate; the two diverge in regimes where short-rate "
            "policy is at or near the effective lower bound. Cite both when ELB-relevant."
        ),
    ),
    "financial_stress_index_can": BocSpec(
        name="financial_stress_index_can", series_key="FVI_FSI_CAN",
        start_date="2000-01-01",
        units="Index", frequency="monthly", section="financial", cadence="monthly",
        notes=(
            "BoC Canadian Financial Stress Index (CFSI), aggregating stress indicators "
            "across seven broad markets. Probe 2026-05-11 confirmed MONTHLY cadence "
            "(despite the broader FVI page describing it as a real-time stress measure -- "
            "the published series itself is month-end). Useful as a regime classifier "
            "alongside the daily term-premium read; canon 4.6 element 6 references this "
            "as the BoC-published Canadian FCI/FSI anchor. Routes through the monthly "
            "build, not the daily Financial build."
        ),
    ),

    # ----- BoC balance sheet (Section 4.5a element M4) --------------------
    "boc_total_assets":        BocSpec("boc_total_assets", "V36610", "2000-01-01", "C$ billions", "weekly", "policy", "weekly", scale=0.001),
    "boc_goc_bonds":           BocSpec("boc_goc_bonds", "V36613", "2000-01-01", "C$ billions", "weekly", "policy", "weekly", scale=0.001),
    "boc_settlement_balances": BocSpec("boc_settlement_balances", "V36636", "2000-01-01", "C$ billions", "weekly", "policy", "weekly", scale=0.001),
    "boc_tbills":              BocSpec("boc_tbills", "V36612", "2000-01-01", "C$ billions", "weekly", "policy", "weekly", scale=0.001),
    "boc_repos":               BocSpec("boc_repos", "V44201362", "2000-01-01", "C$ billions", "weekly", "policy", "weekly", scale=0.001),
    "boc_advances":            BocSpec("boc_advances", "V36634", "2000-01-01", "C$ billions", "weekly", "policy", "weekly", scale=0.001),
    "boc_total_liabilities":   BocSpec("boc_total_liabilities", "V36624", "2000-01-01", "C$ billions", "weekly", "policy", "weekly", scale=0.001),
    "boc_banknotes":           BocSpec("boc_banknotes", "V36625", "2000-01-01", "C$ billions", "weekly", "policy", "weekly", scale=0.001),
    "boc_goc_deposits":        BocSpec("boc_goc_deposits", "V36628", "2000-01-01", "C$ billions", "weekly", "policy", "weekly", scale=0.001),
    "boc_reverse_repos":       BocSpec("boc_reverse_repos", "V1203435186", "2000-01-01", "C$ billions", "weekly", "policy", "weekly", scale=0.001),
}


# Subset views the build orchestrator iterates over.
def by_cadence(cadence: str) -> dict[str, BocSpec]:
    return {k: v for k, v in BOC_VALET_SERIES.items() if v.cadence == cadence}


def by_section(section: str) -> dict[str, BocSpec]:
    return {k: v for k, v in BOC_VALET_SERIES.items() if v.section == section}
