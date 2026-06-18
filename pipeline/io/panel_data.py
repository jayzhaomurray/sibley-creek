"""Per-section panel data exporter.

Reads the on-disk catalog of <section>/<panel>.<series> mappings (PANEL_SPECS
below) and writes one JSON file per section:

    data/site/panel_data/<section>.json

Shape (one file per section):

    {
      "section": "gdp",
      "generatedAt": "2026-05-11T...",
      "panels": {
        "panel-1": {
          "primary":   { "key": "<series>", "data": [...], "asOfISO": "...", "unit": "%" },
          "secondary": { "key": "<series>", "data": [...], "asOfISO": "...", "unit": "%" } | null,
          "tertiary":  ...
        },
        ...
      }
    }

Per-slot `data` is the raw on-disk series body (list of {date, value} points,
truncated to a recent window). Panel-specific reshape (bucketing, dumbbell
deltas, force-layout positioning, etc.) is chart-builder's responsibility;
this module exposes the primary time series + provenance only.

Failure policy
--------------
Per-panel construction is wrapped in try/except: a missing CSV produces an
`error` sentinel for that panel, never sinks the section file. Wire to
pipeline/build.py last so derivations + lifts have already populated disk.
"""

from __future__ import annotations

import json
import logging
import math
from dataclasses import dataclass
from datetime import datetime, date, timedelta, timezone
from functools import lru_cache
from pathlib import Path
from typing import Optional

import pandas as pd

logger = logging.getLogger("pipeline.io.panel_data")

ROOT = Path(__file__).resolve().parents[2]
DATA_ROOT = ROOT / "data"

# How many recent points to ship per cadence. Charts re-bin / re-window as
# needed; we cap to keep the per-section JSON files compact.
RECENT_WINDOW: dict[str, int] = {
    "daily":     520,   # ~2 years of business days
    "weekly":    260,   # ~5 years
    "monthly":   240,   # 20 years
    "quarterly": 120,   # 30 years
    "annual":    60,
    "irregular": 1000,  # ship the lot
}


# --------------------------------------------------------------------------- #
# Per-panel specs
# --------------------------------------------------------------------------- #

@dataclass(frozen=True)
class SlotSpec:
    """One time-series slot for a panel (primary / secondary / tertiary)."""
    series: str                 # filename slug (without .csv)
    tier: str = "raw"           # "raw" | "processed" | "derived"
    label: Optional[str] = None # display hint for the chart
    unit_override: Optional[str] = None  # if None, read from meta.units
    # Override the cadence-based RECENT_WINDOW cap. Use sparingly: charts
    # whose context requires the full history (e.g. breadth panels that
    # compare to 1996-2019 historical averages) need more than the default
    # 20 years of monthly data. None = use the cadence-based default.
    window_override: Optional[int] = None


@dataclass(frozen=True)
class PanelSpec:
    panel_id: str
    section: str
    panel_num: int
    file: str   # filename of the Panel*.astro (relative to src/components/charts/)
    primary: Optional[SlotSpec] = None
    secondary: Optional[SlotSpec] = None
    tertiary: Optional[SlotSpec] = None
    extras: tuple[SlotSpec, ...] = ()  # ordered additional slots
    # Optional companion JSON in data/derived/ surfaced verbatim under the
    # panel's `metadata` field. Use this for scalar reference values that
    # don't fit the {date, value} time-series schema (e.g. historical
    # averages for reference bands). Path is relative to data/derived/.
    metadata_path: Optional[str] = None
    # Status against current disk:
    #   "WIRED" - every named slot has a CSV on disk somewhere
    #   "NEAR"  - partial; some slots present, some missing -- see notes
    #   "MISSING" - nothing on disk; chart will render placeholder
    expected_status: str = "WIRED"
    notes: Optional[str] = None


# Section -> [PanelSpec, ...]. Keep ordered by panel number for deterministic
# output. Each PanelSpec mirrors the Props interface in the corresponding
# Panel*.astro file; gaps and missing series are flagged in `notes`.
PANEL_SPECS: dict[str, list[PanelSpec]] = {
    "output": [
        PanelSpec(
            panel_id="panel-1", section="output", panel_num=1,
            file="output/Panel1HeadlineGDP.astro",
            primary=SlotSpec("gdp_monthly", "raw", label="Monthly real GDP (level)"),
            secondary=SlotSpec("gdp_quarterly", "raw", label="Quarterly real GDP (level)"),
            notes="Panel needs m/m % and Q/Q SAAR. Chart-builder derives both from levels; or wire processed/gdp_monthly_mom (not on disk yet).",
        ),
        PanelSpec(
            panel_id="panel-2", section="output", panel_num=2,
            file="output/Panel2IndustryAggregate.astro",
            primary=SlotSpec(
                "gdp_industry_services", "raw",
                label="Services (level, monthly)",
            ),
            secondary=SlotSpec(
                "gdp_industry_goods", "raw",
                label="Goods (level, monthly)",
            ),
            notes=(
                "Industry split: services vs goods, both monthly real GDP "
                "levels (StatCan 36-10-0434-01). Chart wrapper derives Y/Y "
                "from levels and renders two lines on a 36-month window. "
                "The two-series gap carries the cyclical split between the "
                "structural and cyclical halves of the Canadian economy."
            ),
        ),
        PanelSpec(
            panel_id="panel-3", section="output", panel_num=3,
            file="output/Panel3Contributions.astro",
            primary=SlotSpec("gdp_total_contribution", "raw", label="Total contribution (pp)"),
            extras=(
                SlotSpec("gdp_contrib_consumption", "raw", label="Consumption"),
                SlotSpec("gdp_contrib_govt", "raw", label="Government"),
                SlotSpec("gdp_contrib_investment", "raw", label="GFCF"),
                SlotSpec("gdp_contrib_inventories", "raw", label="Inventories"),
                SlotSpec("gdp_contrib_exports", "raw", label="Exports"),
                SlotSpec("gdp_contrib_imports", "raw", label="Less imports"),
            ),
        ),
        PanelSpec(
            panel_id="panel-4", section="output", panel_num=4,
            file="output/Panel4PerCapita.astro",
            primary=SlotSpec("gdp_quarterly", "raw", label="Aggregate real GDP (quarterly)"),
            secondary=SlotSpec("pop_total", "raw", label="Canada total population (quarterly)"),
            expected_status="WIRED",
            notes=(
                "Aggregate quarterly real GDP + Canada-total quarterly population "
                "(v1, Table 17-10-0009-01). The derived per-capita Y/Y companion lives "
                "at data/processed/gdp_per_capita_yoy.csv via derive_gdp_per_capita_yoy()."
            ),
        ),
        PanelSpec(
            panel_id="panel-5", section="output", panel_num=5,
            file="output/Panel5OutputGap.astro",
            primary=SlotSpec("output_gap_mpr", "raw",
                             label="BoC MPR output gap (%, quarterly)"),
            secondary=SlotSpec("capacity_util_total", "raw",
                               label="Industrial capacity utilization (slack toggle)"),
            tertiary=SlotSpec("capacity_util_mfg", "raw",
                              label="Manufacturing capacity utilization (slack toggle)"),
            extras=(
                SlotSpec("gdp_quarterly", "raw", label="Real GDP level (context)"),
            ),
            expected_status="WIRED",
            notes=(
                "Wave 5 methodology resolution (Section C.1): BoC MPR "
                "INDINF_OUTGAPMPR_Q is the canonical output-gap series (NOT an "
                "HP-filter derivation). Quarterly, runs from 1990. Capacity "
                "utilization (total + manufacturing) added as secondary "
                "slack-measure toggles per Section A.5 fold. If a BoC MPR cycle "
                "does not refresh the output gap, the panel shows a stale-vintage "
                "badge; we do not substitute an HP-filter."
            ),
        ),
        PanelSpec(
            panel_id="panel-6", section="output", panel_num=6,
            file="output/Panel6IndustryCyclical.astro",
            primary=SlotSpec(
                "gdp_industry_manufacturing", "raw",
                label="Manufacturing (level, monthly)",
            ),
            secondary=SlotSpec(
                "gdp_industry_mining_oil", "raw",
                label="Mining and oil & gas (level, monthly)",
            ),
            expected_status="WIRED",
            notes=(
                "Cyclical subsectors inside goods: manufacturing vs mining "
                "and oil & gas, both monthly real GDP levels (StatCan "
                "36-10-0434-01). The two are moving in opposite directions "
                "in 2025-26 - manufacturing in a sustained slump (~-3% Y/Y), "
                "mining/oil in clean expansion (~+3.5% Y/Y) - and the "
                "regional shadow of this is Ontario/Quebec vs Alberta/SK. "
                "Chart wrapper derives Y/Y from levels and renders two "
                "lines on a 36-month window."
            ),
        ),
    ],
    "inflation": [
        PanelSpec(
            panel_id="panel-1", section="inflation", panel_num=1,
            file="inflation/Panel1HeadlineCPI.astro",
            primary=SlotSpec("cpi_all_items_nsa_yoy", "processed", label="Headline CPI Y/Y"),
            secondary=SlotSpec("cpi_all_items", "raw", label="Headline CPI level (for 3M annualized)"),
            notes="Panel needs `yoy` and optional `mom3_ar` (3-month annualized). Y/Y is in processed/; 3M-AR derives from the raw level via annualize_period_growth(period_lag=3, periods_per_year=12).",
        ),
        PanelSpec(
            panel_id="panel-2", section="inflation", panel_num=2,
            file="inflation/Panel2CoreTrio.astro",
            primary=SlotSpec("cpi_trim", "raw", label="CPI-trim Y/Y"),
            secondary=SlotSpec("cpi_median", "raw", label="CPI-median Y/Y"),
            tertiary=SlotSpec("cpi_common", "raw", label="CPI-common Y/Y"),
        ),
        PanelSpec(
            panel_id="panel-3", section="inflation", panel_num=3,
            file="inflation/Panel3Breadth.astro",
            primary=SlotSpec("cpi_breadth_above3", "processed",
                             label="Share of basket with Y/Y > 3% (weighted)",
                             window_override=420),  # ~35 years; covers 1995-12-present
            secondary=SlotSpec("cpi_breadth_below1", "processed",
                               label="Share of basket with Y/Y < 1% (weighted)",
                               window_override=420),
            metadata_path="cpi_breadth_band_metadata.json",
            expected_status="WIRED",
            notes=(
                "Boc-tracker breadth recipe ported into pipeline.build."
                "derive_cpi_breadth_band(). Two monthly time series (above3, "
                "below1) plus a scalar metadata payload carrying the "
                "1996-2019 historical averages for reference bands on the "
                "chart. Weights from data/derived/cpi_component_weights_"
                "canada.json; per-component levels from data/raw/cpi_"
                "components.csv (must be force-added to git for CI deploys)."
            ),
        ),
        PanelSpec(
            panel_id="panel-4", section="inflation", panel_num=4,
            file="inflation/Panel4SubAggregates.astro",
            primary=SlotSpec("cpi_shelter_yoy", "processed", label="Shelter Y/Y"),
            extras=(
                SlotSpec("cpi_food_yoy", "processed", label="Food Y/Y"),
                SlotSpec("cpi_energy_yoy", "processed", label="Energy Y/Y"),
                SlotSpec("cpi_goods_yoy", "processed", label="Goods Y/Y"),
                SlotSpec("cpi_services_yoy", "processed", label="Services Y/Y"),
                SlotSpec("cpi_rent_yoy", "processed", label="Rent Y/Y"),
                SlotSpec("cpi_mortgage_interest_yoy", "processed", label="Mortgage interest Y/Y"),
                SlotSpec("cpi_owned_accommodation_yoy", "processed", label="Owned accommodation Y/Y"),
            ),
            notes="Shelter decomposition (exMIC vs MIC) needs cpi_rented_accommodation_yoy + cpi_mortgage_interest_yoy; both on disk.",
        ),
        PanelSpec(
            panel_id="panel-5", section="inflation", panel_num=5,
            file="inflation/Panel5Expectations.astro",
            primary=SlotSpec("infl_exp_consumer_1y", "raw", label="CSCE 1Y consumer expectations"),
            secondary=SlotSpec("infl_exp_consumer_5y", "raw", label="CSCE 5Y consumer expectations"),
            tertiary=SlotSpec("infl_exp_above3", "raw", label="BOS share > 3%"),
            extras=(
                SlotSpec("bos_dist_below1", "raw", label="BOS dist < 1%"),
                SlotSpec("bos_dist_1to2", "raw", label="BOS dist 1-2%"),
                SlotSpec("bos_dist_2to3", "raw", label="BOS dist 2-3%"),
                SlotSpec("bos_dist_above3", "raw", label="BOS dist > 3%"),
            ),
        ),
    ],
    "labour": [
        PanelSpec(
            panel_id="panel-1", section="labour", panel_num=1,
            file="labour/Panel1HeadlinePrint.astro",
            primary=SlotSpec("employment_level", "raw",
                             label="Employment level (SA, monthly, millions)"),
            secondary=SlotSpec("unemployment_rate", "raw",
                               label="Unemployment rate (SA, monthly, %)"),
            tertiary=SlotSpec("employment_rate", "raw",
                              label="Employment rate (archival, retired triptych)"),
            extras=(
                SlotSpec("participation_rate", "raw",
                         label="Participation rate (archival, retired triptych)"),
            ),
            expected_status="WIRED",
            notes=(
                "Headline-print plate (2026-05-12). Primary = employment_level "
                "(StatCan Table 14-10-0287-01 v2062811, employed persons 15+ SA "
                "monthly in millions); the chart wrapper derives m/m delta in "
                "thousands of persons for the bar geometry. Secondary = "
                "unemployment_rate (same table, SA %) for the right-axis line. "
                "Tertiary + participation_rate retained as archival slots from "
                "the retired Panel1LFSHeadlineSmallMultiples triptych (now at "
                "_alternatives/labour/Alt_Panel1LFSHeadlineSmallMultiples.astro); "
                "the live plate does not consume them."
            ),
        ),
        PanelSpec(
            panel_id="panel-2", section="labour", panel_num=2,
            file="labour/Panel2LabourStocksPerCapita.astro",
            # Per-capita stocks plate (2026-05-13 rebuild per user direction).
            # Same three-stocks structure as the retired Panel2LabourStocks,
            # but each series rendered as a share of pop_15+ instead of as a
            # level in millions. Three side-by-side line panels:
            #   Employed share   = employment_rate (published directly)
            #   Unemployed share = unemployment_level / pop_15plus * 100
            #   NILF share       = 100 - employed_share - unemployed_share
            # pop_15plus is the published StatCan series (v2062809, SA monthly,
            # millions); no longer back-derived from employment / employment_rate.
            primary=SlotSpec("employment_level", "raw",
                             label="Employment level (SA, monthly, millions)"),
            secondary=SlotSpec("unemployment_level", "raw",
                               label="Unemployment level (SA, monthly, millions)"),
            tertiary=SlotSpec("employment_rate", "raw",
                              label="Employment rate (SA, monthly, %)"),
            extras=(
                SlotSpec("pop_15plus", "raw",
                         label="Population 15+ (SA, monthly, millions)"),
            ),
            expected_status="WIRED",
            notes=(
                "Three-stocks-per-capita plate. Chart deflates each level by "
                "pop_15plus to render shares of working-age population. The three "
                "shares sum to 100%. Employed share equals the published employment "
                "rate directly; unemployed share = unemp / pop_15plus; NILF "
                "share = 100 - emp_share - unemp_share. pop_15plus is StatCan "
                "Table 14-10-0287-01 v2062809 (SA monthly, millions). Tertiary "
                "slot (employment_rate) retained for reconciliation cross-check."
            ),
        ),
        PanelSpec(
            panel_id="panel-3", section="labour", panel_num=3,
            file="labour/Panel3WageBandV3.astro",
            # V3 wage chart (chart-builder, 2026-05-12, art-director ratified):
            # two-series treatment, BoC LFS-Micro vs LFS-all. SEPH and the
            # services-ex-shelter CPI reference have been pulled from the
            # consumed slots; the editorial payload is the ~1pp gap between
            # the headline and the composition-adjusted read. SEPH +
            # lfs_wages_permanent stay listed under extras for archival only
            # and are not rendered. Services-CPI-ex-shelter reference moves
            # off this plate (lives on a future inflation/household plate).
            primary=SlotSpec("lfs_micro", "raw", label="LFS-Micro Y/Y (BoC)"),
            secondary=SlotSpec("lfs_wages_all", "raw", label="LFS, all employees"),
            extras=(
                SlotSpec("seph_earnings", "raw", label="SEPH avg weekly earnings (archival)"),
                SlotSpec("lfs_wages_permanent", "raw", label="LFS, permanent employees (archival)"),
            ),
            notes="V3 chart: two-series only. lfs_micro arrives already in Y/Y %; chart-builder derives Y/Y on lfs_wages_all at render time. Extras are archival; not consumed.",
        ),
        PanelSpec(
            panel_id="panel-4", section="labour", panel_num=4,
            file="labour/Panel4VacanciesSlack.astro",
            primary=SlotSpec("job_vacancy_rate", "raw", label="Job vacancy rate"),
            secondary=SlotSpec("job_vacancy_level", "raw", label="Job vacancy level"),
            tertiary=SlotSpec("unemployment_rate", "raw", label="Unemployment rate (Beveridge axis)"),
            extras=(
                SlotSpec("indeed_postings_ca_monthly", "raw", label="Indeed Canada postings (monthly mean)"),
            ),
            notes="V/U ratio = vacancies / unemployed; chart-builder computes from job_vacancy_level / unemployment_level (both on disk).",
        ),
        PanelSpec(
            panel_id="panel-6", section="labour", panel_num=6,
            file="labour/Panel8LabourFlowRates.astro",
            primary=SlotSpec("labour_separation_rate", "derived", label="Separation rate"),
            secondary=SlotSpec("labour_job_finding_rate", "derived", label="Job finding rate"),
            notes=(
                "Flow-rate chart derives monthly transition probabilities from "
                "LFS unemployment stocks, unemployment rate, and short-duration "
                "unemployment using the Elsby-Michaels-Solon approximation. "
                "The final LFS month is dropped because the t+1 short-duration "
                "stock is required."
            ),
        ),
        # New plate (2026-05-12): hours-vs-headcount dual-panel. Lines left
        # (hours Y/Y, employment Y/Y), signed-spread bars right (hours Y/Y
        # minus employment Y/Y). Editorial payload: per-worker-hours channel.
        # When hours Y/Y slows below employment Y/Y, employers are cutting
        # shifts before they cut bodies -- the leading-softening signal that
        # precedes a headcount rollover. At the April 2026 print the spread
        # is -0.83pp (hours Y/Y -0.51%, employment Y/Y +0.32%); the story
        # has landed and is visible on the chart.
        PanelSpec(
            panel_id="panel-8", section="labour", panel_num=8,
            file="labour/Panel8HoursVsHeadcount.astro",
            primary=SlotSpec("aggregate_hours", "raw",
                             label="Total actual hours worked (SA, monthly)"),
            secondary=SlotSpec("employment_level", "raw",
                               label="Employment level (SA, monthly, millions)"),
            expected_status="WIRED",
            notes=(
                "Hours-vs-headcount dual-panel plate. Primary: aggregate_hours "
                "(StatCan Table 14-10-0289-01 v4391505, total actual hours worked "
                "all industries, SA monthly, thousands of hours; main-job basis -- "
                "no SA all-jobs cube exists). Secondary: employment_level (StatCan "
                "Table 14-10-0287-01 v2062811, employed persons 15+, SA monthly, "
                "millions). Chart wrapper derives Y/Y of both at render time and "
                "computes the signed spread (hours_yoy - emp_yoy) for the right-"
                "panel bars. Both series taken directly from source; no "
                "transforms applied at pipeline tier."
            ),
        ),
    ],
    "housing": [
        PanelSpec(
            panel_id="panel-1", section="housing", panel_num=1,
            file="housing/Panel1Prices.astro",
            primary=SlotSpec("crea_hpi_canada_yoy", "processed", label="Canada HPI Y/Y"),
            extras=(
                SlotSpec("crea_hpi_toronto_yoy", "processed", label="Toronto"),
                SlotSpec("crea_hpi_vancouver_yoy", "processed", label="Vancouver"),
                SlotSpec("crea_hpi_montreal_yoy", "processed", label="Montreal"),
                SlotSpec("crea_hpi_calgary_yoy", "processed", label="Calgary"),
                SlotSpec("crea_hpi_ottawa_yoy", "processed", label="Ottawa"),
                SlotSpec("crea_hpi_edmonton_yoy", "processed", label="Edmonton"),
            ),
        ),
        PanelSpec(
            panel_id="panel-2", section="housing", panel_num=2,
            file="housing/Panel2Activity.astro",
            primary=SlotSpec("housing_starts", "raw", label="Housing starts SAAR"),
            secondary=SlotSpec("units_under_construction", "raw", label="Units under construction"),
            tertiary=SlotSpec("residential_permits", "raw", label="Residential permits"),
            expected_status="NEAR",
            notes="Panel expects starts + completions + permits, all SAAR. completions_saar is MISSING (StatCan Table 34-10-0158 has it; vector ID TBD).",
        ),
        PanelSpec(
            panel_id="panel-3", section="housing", panel_num=3,
            file="housing/Panel3Inventory.astro",
            primary=SlotSpec("crea_snlr", "raw", label="Canada SNLR"),
            secondary=SlotSpec("crea_resales", "raw", label="Canada resales (indexed)"),
            extras=(
                SlotSpec("crea_resales_toronto", "raw", label="Toronto resales 12M"),
                SlotSpec("crea_resales_vancouver", "raw", label="Vancouver resales 12M"),
                SlotSpec("crea_resales_calgary", "raw", label="Calgary resales 12M"),
            ),
            expected_status="NEAR",
            notes="Months-of-inventory by CMA is MISSING (CREA publishes; not in pipeline). SNLR is on disk; chart-builder can use SNLR as the v1 inventory tightness proxy.",
        ),
        PanelSpec(
            panel_id="panel-6", section="housing", panel_num=6,
            file="housing/Panel6FinancialStress.astro",
            primary=SlotSpec(
                "cba_mortgage_arrears_national", "raw",
                label="Mortgage arrears rate (CBA, national)",
            ),
            secondary=SlotSpec(
                "household_dsr", "raw",
                label="Household debt service ratio (% of disposable income, SA)",
            ),
            expected_status="WIRED",
            notes=(
                "Financial-stress plate (plate-6). Two household-stress series: "
                "primary = CBA residential mortgage arrears rate, national, monthly, "
                "% of total mortgages 3+ months past due. Chartered banks + "
                "Manulife/Laurentian/Equitable (~75% of stock). Back to ~1995. "
                "~2.5-month publication lag. Source: CBA DB50 PUBLIC table (PDF). "
                "secondary = StatCan Table 11-10-0065-01 v1001696813, total household "
                "debt service ratio (principal + interest / disposable income), Canada SA, "
                "quarterly. Back to 1990-Q1. Latest: Q4 2025 = 14.57%. "
                "Chart-builder note: two different cadences (monthly vs quarterly); "
                "DSR points should be displayed step-wise on the same axis as arrears."
            ),
        ),
        # Wave 5 add: Housing Affordability (Housing Panel 7). Single-series
        # quarterly line, max history (1981 onward). BoC qualifying-mortgage-
        # payment-to-income ratio. Values are decimal ratios on disk; chart-
        # builder renders as % (multiply by 100) and adds historical-tightening
        # shaded bands (researcher supplies band dates).
        PanelSpec(
            panel_id="panel-7", section="housing", panel_num=7,
            file="housing/Panel7Affordability.astro",
            primary=SlotSpec("housing_affordability", "raw",
                             label="Housing affordability index (ratio)"),
            expected_status="WIRED",
            notes=(
                "Wave 5 canon: BoC qualifying-mortgage-payment-to-income ratio "
                "(INDINF_AFFORD_Q), quarterly. Source values are decimals "
                "(0.43 = 43% of income to qualify for payment); chart-builder "
                "multiplies by 100 for display. Default window: max range. "
                "Historical-tightening shaded bands (1989-1991, 2007-2008, "
                "2022-2024) supplied by researcher as static annotation."
            ),
        ),
    ],
    "monetary": [
        PanelSpec(
            panel_id="panel-1", section="monetary", panel_num=1,
            file="monetary/Panel1OvernightRate.astro",
            primary=SlotSpec("overnight_rate", "raw", label="BoC overnight rate target"),
            secondary=SlotSpec("overnight_rate_daily", "raw", label="Daily overnight rate"),
            notes="MPR neutral band (low/high) is editorial; chart-builder takes it as a prop.",
        ),
        PanelSpec(
            panel_id="panel-2", section="monetary", panel_num=2,
            file="monetary/Panel2MarketPath.astro",
            primary=SlotSpec("yield_2yr", "raw", label="GoC 2-yr yield"),
            secondary=SlotSpec("overnight_rate_daily", "raw", label="Overnight rate"),
            tertiary=SlotSpec(
                "boc_fed_spread_monthly", "processed",
                label="BoC-Fed spread (bps, monthly)",
                unit_override="basis points",
            ),
        ),
        # panel-3 (Canada 2y - US 2y spread) relocated to markets section per
        # editorial reorder 2026-05-13. Slot intentionally vacant to preserve
        # downstream panel numbering (chartRegistry / .astro pickPanel calls).
        PanelSpec(
            panel_id="panel-4", section="monetary", panel_num=4,
            file="monetary/Panel4BalanceSheet.astro",
            primary=SlotSpec("boc_settlement_balances", "raw", label="Settlement balances"),
            secondary=SlotSpec("boc_total_assets", "raw", label="Total assets", window_override=340),
            extras=(
                SlotSpec("boc_goc_bonds", "raw", label="GoC bonds", window_override=340),
                SlotSpec("boc_tbills", "raw", label="T-bills", window_override=340),
                SlotSpec("boc_advances", "raw", label="Advances", window_override=340),
                SlotSpec("boc_repos", "raw", label="Repos (asset)", window_override=340),
                SlotSpec("boc_reverse_repos", "raw", label="Reverse repos (liab)"),
                SlotSpec("boc_banknotes", "raw", label="Banknotes"),
                SlotSpec("boc_goc_deposits", "raw", label="GoC deposits"),
                # Wave 5 fold: CORRA-target spread, daily (derived). Surfaces
                # as the panel's secondary view (toggle) per Section A.3 of
                # editorial/wave5_boc_tracker_chart_decisions.md. 20-day
                # smoothing applied chart-side. Spread already in basis points.
                SlotSpec("corra_overnight_spread_bps", "processed",
                         label="CORRA-target spread (bps, daily)",
                         unit_override="basis points"),
            ),
            notes=(
                "QE/QT phase markers are editorial fixture (chart accepts "
                "`phases` prop). Wave 5 fold: panel becomes a two-view tile; "
                "default is settlement-balances + asset composition, secondary "
                "(toggle) is the CORRA-target spread (20-day smoothing, last "
                "2 years) -- diagnostic that confirms or falsifies the floor-"
                "maintenance call. See data/processed/corra_overnight_spread_bps.csv."
            ),
        ),
        PanelSpec(
            panel_id="panel-5", section="monetary", panel_num=5,
            file="monetary/Panel5LiabilityCompositionSmallMults.astro",
            # Liability composition (Mode B small-multiples). Five components +
            # derived Other liabilities residual (handled chart-side).
            primary=SlotSpec("boc_total_liabilities", "raw", label="Total liabilities", window_override=340),
            extras=(
                SlotSpec("boc_banknotes", "raw", label="Banknotes", window_override=340),
                SlotSpec("boc_goc_deposits", "raw", label="GoC deposits", window_override=340),
                SlotSpec("boc_settlement_balances", "raw", label="Settlement balances", window_override=340),
                SlotSpec("boc_reverse_repos", "raw", label="Reverse repos", window_override=340),
            ),
            notes=(
                "BoC liability composition (Mode B small-multiples, 6 sub-panels). "
                "Six = primary + 4 extras + chart-derived Other-liabilities residual. "
                "Window since 2020-01-01 (340 weekly points)."
            ),
        ),
        PanelSpec(
            panel_id="panel-6", section="monetary", panel_num=6,
            file="monetary/Panel6FederalTrajectorySplit.astro",
            primary=SlotSpec("dof_fiscal_monthly_balance", "raw", label="Federal monthly balance"),
            secondary=SlotSpec("dof_fiscal_ytd_balance", "raw", label="Federal fiscal-YTD balance"),
            tertiary=SlotSpec("dof_fiscal_ytd_summary", "raw", label="Fiscal Monitor YTD summary"),
            notes=(
                "DoF Fiscal Monitor. Retained on monetary section as cross-domain "
                "fiscal-context panel. Full fiscal chartbook is at /fiscal/. "
                "Two-panel side-by-side composite: monthly bars (left) + YTD line "
                "(right), each with own y-axis."
            ),
        ),
        # panel-7-alt: Fiscal stance (long-history). NOT a live plate yet.
        # Source: IMF WEO DataMapper API (annual, general government).
        # Scope caveat: both series are GENERAL GOVERNMENT (all levels),
        # not federal-only. Document in caption before any live promotion.
        # IMF GGXWNG_NGDP (net debt) returns null for Canada; gross debt
        # (GGXWDG_NGDP) is used as the secondary slot with the label
        # "Gross debt (% GDP, general govt)" to avoid implying net-debt.
        PanelSpec(
            panel_id="panel-7-alt", section="monetary", panel_num=7,
            file="monetary/Panel7AltFiscalStance.astro",
            primary=SlotSpec(
                "imf_can_gg_balance_pct_gdp", "raw",
                label="Fiscal balance (% GDP, general govt)",
                unit_override="% of GDP",
            ),
            secondary=SlotSpec(
                "imf_can_gg_gross_debt_pct_gdp", "raw",
                label="Gross debt (% GDP, general govt)",
                unit_override="% of GDP",
            ),
            notes=(
                "ALT chart -- NOT a live plate. Fiscal stance long-history view "
                "(1980-present, annual). Source: IMF World Economic Outlook "
                "DataMapper API. SCOPE CAVEAT: both series are general government "
                "(federal + provincial + local + social-security), not federal-only. "
                "Primary = net lending/borrowing % GDP (negative = deficit). "
                "Secondary = gross debt % GDP (NOT net debt; IMF does not publish "
                "Canada net debt; label must say 'gross' in any chart caption). "
                "WEO vintages include IMF forward projections; chart-builder should "
                "visually distinguish projected years (from current year onward). "
                "For federal-only framing, DoF Fiscal Reference Tables (PDF annual) "
                "are the authoritative source -- extraction deferred to v1.5."
            ),
        ),
    ],
    "fiscal": [
        # Plate 1 — Federal trajectory. Ported from policy panel-6 (same series).
        # DoF Fiscal Monitor: monthly balance + fiscal-YTD balance.
        PanelSpec(
            panel_id="panel-1", section="fiscal", panel_num=1,
            file="fiscal/Panel1FederalTrajectory.astro",
            primary=SlotSpec("dof_fiscal_monthly_balance", "raw", label="Federal monthly balance"),
            secondary=SlotSpec("dof_fiscal_ytd_balance", "raw", label="Federal fiscal-YTD balance"),
            tertiary=SlotSpec("dof_fiscal_ytd_summary", "raw", label="Fiscal Monitor YTD summary"),
            expected_status="WIRED",
            notes=(
                "Port of policy panel-6. DoF Fiscal Monitor. Monthly bars (left) + "
                "YTD line (right). Source: pipeline:dof:dof_fiscal_ytd_balance + "
                "pipeline:dof:dof_fiscal_monthly_balance. Source card: plate-1.yaml "
                "(inherits from policy section, Tier A verified)."
            ),
        ),
        # Plate 2 — Debt service / revenues ratio with 5-year trailing same-month band.
        # Derived series emitted by pipeline.build.derive_fiscal_plate2_band():
        #   primary:   debt_service_ratio        -- ratio_pct, all available months
        #   secondary: debt_service_ratio_band_lo -- 5-yr same-month trailing min
        #   tertiary:  debt_service_ratio_band_hi -- 5-yr same-month trailing max
        # History source: dof_fiscal_ratio_history.csv (FY2019-20 onward, built by
        #   pipeline.build.fetch_dof_fiscal_history()).
        # PBO names this the 'interest burden' sustainability indicator;
        # latest value: rising toward 13.2% by 2030-31 per PBO May 2026 forecast.
        PanelSpec(
            panel_id="panel-2", section="fiscal", panel_num=2,
            file="fiscal/Panel2DebtServiceRevenues.astro",
            primary=SlotSpec(
                "debt_service_ratio", "derived",
                label="Debt service / revenues ratio (%)",
                unit_override="%",
            ),
            secondary=SlotSpec(
                "debt_service_ratio_band_lo", "derived",
                label="5-year same-month trailing min (%)",
                unit_override="%",
            ),
            tertiary=SlotSpec(
                "debt_service_ratio_band_hi", "derived",
                label="5-year same-month trailing max (%)",
                unit_override="%",
            ),
            expected_status="WIRED",
            notes=(
                "Plate 2: debt-service / revenues ratio (%). Pre-computed pipeline-side "
                "from DoF Fiscal Monitor multi-year history (FY2019-20 onward). "
                "primary=debt_service_ratio (the ratio itself, monthly); "
                "secondary=debt_service_ratio_band_lo (5-yr same-month trailing min); "
                "tertiary=debt_service_ratio_band_hi (5-yr same-month trailing max). "
                "Band methodology: for month m, use the 5 most-recent prior occurrences "
                "of the same calendar month (e.g. Feb 2026 band = Feb 2021-2025); "
                "requires >=2 prior same-month observations. "
                "Source card: plate-2.yaml (Tier A). "
                "PBO's 'interest burden' indicator: 10.3c per dollar of revenue "
                "currently; rising to 13.2% by 2030-31 (PBO Main Estimates May 2026). "
                "PBO endpoint rendered as named anchor in the chart component."
            ),
        ),
        # Plate 3 — PBO EFO Sept 2025 vs DoF SEU April 2026 baseline delta.
        # Static JSON of two five-year-forward deficit projections.
        # Source card: plate-3.yaml (Tier B, pending user_confirmed_at).
        PanelSpec(
            panel_id="panel-3", section="fiscal", panel_num=3,
            file="fiscal/Panel3PBOvsDoF.astro",
            primary=None,  # no live time-series; chart reads from metadata_path
            metadata_path="fiscal_pbo_dof_baseline.json",
            expected_status="NEAR",
            notes=(
                "Plate 3: PBO EFO Sept 2025 vs DoF SEU April 2026 five-year "
                "deficit projection comparison. Two static series, each vintage-stamped. "
                "Emitted by pipeline.build.derive_fiscal_pbo_dof_baseline() from "
                "data/derived/fiscal_pbo_dof_baseline.json. "
                "Source card: plate-3.yaml (Tier B, user_confirmed_at pending). "
                "Methodology footnote required: different macro envelopes and "
                "private-sector survey vintages. Chart-builder: consider adding "
                "PBO May 2026 SEU assessment as a third trace once machine-readable."
            ),
        ),
        # Plate 4 — Provincial net debt-to-GDP: ON / QC / AB / BC.
        # Static JSON from most-recent provincial budgets. Publisher's-own basis
        # per Bartlett + Page consensus (see fiscal_phase1_bartlett_lapointe.md Q1).
        # BC annotated as taxpayer-supported basis (different denominator).
        # QC vintage updated to Budget 2026-2027 (March 18, 2026; 38.8% confirmed).
        PanelSpec(
            panel_id="panel-4", section="fiscal", panel_num=4,
            file="fiscal/Panel4ProvincialDebt.astro",
            primary=None,  # no live time-series; chart reads from metadata_path
            metadata_path="fiscal_provincial_debt.json",
            expected_status="NEAR",
            notes=(
                "Plate 4: four-province net debt-to-GDP from most-recent budgets. "
                "ON: 37.7% (Fall Economic Outlook Nov 2025); "
                "QC: 38.8% (Budget 2026-2027, March 18 2026 -- Tier A verified); "
                "AB: 10.5% (Budget 2026, Feb 26 2026); "
                "BC: 30.6% taxpayer-supported basis (Budget 2026, Feb 17 2026). "
                "Publisher's-own basis per Bartlett/IFSD recommendation; each bar "
                "annotated with vintage stamp and basis badge. "
                "Source card: plate-4.yaml (Tier B, user_confirmed_at pending). "
                "Emitted by pipeline.build.derive_fiscal_provincial_debt()."
            ),
        ),
        # Plate 5 — Operating vs capital balance under Carney's bifurcated budget.
        # SUPERSEDES the original CAPB spec from fiscal_section_plan_2026-05-24.md.
        # Per Bartlett-Lapointe-Page-Khan methodology brief (Q4): CAPB is off-radar
        # for 3 of 4 experts. Operating-vs-capital is the framing Page, PBO, IFSD,
        # and Bartlett are converging on in spring 2026.
        # Two series:
        #   (1) DoF's operating + capital decomposition from SEU April 2026.
        #   (2) PBO's reclassified version from Nov 17 2025 assessment
        #       (PBO identifies ~$94B gap between DoF's 'capital' definition and
        #       PBO's stricter international standard).
        # Source card: RESEARCHER FOLLOW-UP REQUIRED -- see notes below.
        PanelSpec(
            panel_id="panel-5", section="fiscal", panel_num=5,
            file="fiscal/Panel5OperatingVsCapital.astro",
            primary=None,  # static JSON; reads from metadata_path
            metadata_path="fiscal_operating_capital.json",
            expected_status="NEAR",
            notes=(
                "Plate 5: operating vs capital balance under Carney bifurcated budget. "
                "SUPERSEDES CAPB spec. Two series: (1) DoF SEU April 2026 operating "
                "+ capital decomposition; (2) PBO Nov 17 2025 reclassified decomposition "
                "(stricter international-standard definition, ~$94B gap identified). "
                "SOURCE CARD: RESEARCHER FOLLOW-UP REQUIRED. The PBO Nov 17 2025 "
                "assessment (thehub.ca/2025/11/17/...) is the primary reference; "
                "the exact DoF SEU decomposition table reference needs retrieval. "
                "A skeleton source card for this plate is at "
                "editorial/source_cards/_pending/fiscal/plate-5.yaml "
                "(auto-generated by backend -- researcher must fill values before "
                "chart-builder can finalize the component). "
                "Chart-builder: render two-trace comparison; annotate the gap band; "
                "title verb: 'Most of the fiscal dividend went to operating spending, "
                "not capital.' "
            ),
        ),
        # ---- NEW PLATES (fiscal_redo_chart_spec.md Revision 2, 2026-06-02) --------
        # Panel 6 — Budget balance total ($B, full history) + opex/capex decomposition.
        # Primary: frt_federal_balance_total (FY1983-84 → FY2030-31, history + SEU 2026 forecast).
        # Secondary: frt_federal_balance_opex (SEU 2026, forecast only FY2025-26+).
        # Tertiary: frt_federal_balance_capex (SEU 2026, forecast only FY2025-26+).
        PanelSpec(
            panel_id="panel-6", section="fiscal", panel_num=6,
            file="fiscal/Panel6BalanceOpexCapex.astro",
            primary=SlotSpec(
                "frt_federal_balance_total", "derived",
                label="Total budgetary balance ($B)",
                unit_override="CAD billions",
            ),
            secondary=SlotSpec(
                "frt_federal_balance_opex", "derived",
                label="Operating balance ($B, SEU 2026)",
                unit_override="CAD billions",
            ),
            tertiary=SlotSpec(
                "frt_federal_balance_capex", "derived",
                label="Capital investment ($B, SEU 2026)",
                unit_override="CAD billions",
            ),
            expected_status="WIRED",
            notes=(
                "Plate 6: federal budget balance total (primary) + opex/capex decomposition "
                "(secondary + tertiary). PRIMARY (frt_federal_balance_total): FRT 2025 Table 1 "
                "actuals FY2006-07 to FY2024-25 (pypdf extract, Tier A) + SEU 2026 Annex 1 "
                "A1.7 total-balance forecast FY2025-26 to FY2030-31 (WebFetched + verified, "
                "Tier A). Units: $B CAD; deficit negative. SECONDARY (frt_federal_balance_opex): "
                "operating balance, SEU 2026 A1.5. TERTIARY (frt_federal_balance_capex): capital "
                "investment, SEU 2026 A1.4. Opex/capex exist ONLY from FY2025-26 (Capital "
                "Budgeting Framework new in Budget 2025); FY2024-25 opex/capex are null "
                "(pre-framework actual). is_forecast field in each data record (0=history, "
                "1=projected). Chart-builder guidance: plot total balance bars/line full range; "
                "overlay opex/capex stacked composition for the forecast segment (FY2025-26+). "
                "PBO reclassification dispute (~$94B gap, RP-2526-017-S Nov 2025): PBO stricter "
                "capital definition shows opex deficits in all forecast years. Secondary/tertiary "
                "= DoF official; PBO view is an annotation, not a series here. "
                "Source: pipeline/fetch/frt_fiscal_series.py."
            ),
        ),
        # Panel 7 — Federal revenues as % of GDP, long history + SEU 2026 forecast.
        PanelSpec(
            panel_id="panel-7", section="fiscal", panel_num=7,
            file="fiscal/Panel7RevenuesPctGDP.astro",
            primary=SlotSpec(
                "frt_revenues_pct_gdp", "derived",
                label="Federal revenues (% of GDP)",
                unit_override="% of GDP",
            ),
            expected_status="WIRED",
            notes=(
                "Plate 7: federal revenues as % of GDP, long history + SEU 2026 forecast. "
                "History: FRT 2025 Table 2 actuals (Oct-2025 GDP vintage). Forecast: derived "
                "from SEU 2026 Annex 1 revenues $B / SEU nominal GDP $B (Apr-2026 GDP vintage). "
                "SEAM: FRT FY2024-25 actual = 16.6%; SEU FY2025-26 forecast = 15.77%. The ~0.9pp "
                "step is partly genuine projected decline, partly GDP vintage offset. Chart must "
                "carry vintage-seam annotation at the FY2024-25/FY2025-26 boundary. "
                "is_forecast field in each record. Matched-pair with panel-8 (program expenses) "
                "-- chart-builder should use identical y-domain (art-director Plate 2+3 matched-pair "
                "rule). Source: pipeline/fetch/frt_fiscal_series.py."
            ),
        ),
        # Panel 8 — Federal program expenses as % of GDP, long history + SEU 2026 forecast.
        PanelSpec(
            panel_id="panel-8", section="fiscal", panel_num=8,
            file="fiscal/Panel8ProgramExpPctGDP.astro",
            primary=SlotSpec(
                "frt_program_exp_pct_gdp", "derived",
                label="Program expenses excl. debt charges (% of GDP)",
                unit_override="% of GDP",
            ),
            expected_status="WIRED",
            notes=(
                "Plate 8: federal program expenses (excl. net actuarial losses AND excl. public "
                "debt charges) as % of GDP. Long history + SEU 2026 forecast. History: FRT 2025 "
                "Table 8 actuals. Forecast: derived from SEU 2026 Annex 1 program-expenses-ex-"
                "actuarial $B / SEU nominal GDP $B. FY2020-21 = 28.1% is real (COVID spike, not "
                "a basis break) -- annotate. MATCHED PAIR with panel-7 (revenues): chart-builder "
                "must use identical y-domain across both plates (art-director Plate 2+3 spec). "
                "The gap between the two series at any year represents the fiscal surplus/deficit. "
                "is_forecast field in each record. Source: pipeline/fetch/frt_fiscal_series.py."
            ),
        ),
        # Panel 9 — Federal debt (accumulated deficit) as % of GDP.
        # PRIMARY:   frt_federal_debt_pct_gdp     -- DoF FRT/SEU, 40-year history + SEU forecast
        # SECONDARY: frt_federal_debt_pct_gdp_pbo -- PBO EFO June 2026 (RP-2627-002-S), Table 2
        #            FY2024-25 to FY2030-31, all is_forecast=1. Same concept; directly comparable.
        #            PBO gap vs DoF ~1pp; PBO calls own track "flat over the medium term."
        PanelSpec(
            panel_id="panel-9", section="fiscal", panel_num=9,
            file="fiscal/Panel9FederalDebtPctGDP.astro",
            primary=SlotSpec(
                "frt_federal_debt_pct_gdp", "derived",
                label="Federal debt / accumulated deficit (% of GDP)",
                unit_override="% of GDP",
            ),
            secondary=SlotSpec(
                "frt_federal_debt_pct_gdp_pbo", "derived",
                label="PBO forecast (June 2026 EFO)",
                unit_override="% of GDP",
            ),
            expected_status="WIRED",
            notes=(
                "Plate 9: federal debt (accumulated deficit) as % of GDP, FY2006-07 to FY2030-31. "
                "REBUILT CLEAN -- do NOT use data/derived/fiscal_debt_to_gdp.csv (that file "
                "carries Budget 2025 projections with an incompatible GDP vintage). "
                "PRIMARY (frt_federal_debt_pct_gdp): History FRT 2025 Table 2 (Oct-2025 GDP "
                "vintage). Forecast: SEU 2026 Annex 1 Table A1.7 published %GDP row (Apr-2026 "
                "vintage). Seam at FY2024-25/FY2025-26: FRT 41.2% -> SEU 41.1% (~0.1pp, benign). "
                "SECONDARY (frt_federal_debt_pct_gdp_pbo): PBO EFO June 2026 (RP-2627-002-S), "
                "Table 2. FY2024-25 to FY2030-31, all is_forecast=1. Same concept (federal "
                "accumulated deficit % GDP); PBO uses own macro denominators. Gap vs DoF ~1pp; "
                "PBO's own characterization: 'flat over the medium term' (p. 9). "
                "GDP VINTAGE: PBO denominator differs from both FRT and SEU vintages; the ~1pp "
                "gap reflects higher PBO deficit projections AND different denominators -- do NOT "
                "present as purely deficit-driven. "
                "Federal-only basis (NOT general-government gross debt; Fitch/OECD/IMF general-"
                "govt figures ~91-107% are NOT comparable). "
                "Historical reference points: pre-GFC trough 28.2% (FY2008-09), COVID peak "
                "47.2% (FY2020-21). Source: pipeline/fetch/frt_fiscal_series.py Series 5 + 17."
            ),
        ),
        # Panel 10 — Federal GROSS ISSUANCE FLOW by maturity bucket.
        # REBUILT 2026-06-02: was outstanding market-debt STOCK (frt_issuance_bonds/
        # tbills/retail); repointed to GROSS ISSUANCE FLOW (frt_issuance_flow_*). The
        # old stock series remain in pipeline/fetch/frt_fiscal_series.py and as CSVs
        # but are NO LONGER WIRED to this plate (different metric).
        PanelSpec(
            panel_id="panel-10", section="fiscal", panel_num=10,
            file="fiscal/Panel10IssuanceStock.astro",
            primary=SlotSpec(
                "frt_issuance_flow_bonds", "derived",
                label="Long bonds issued (10yr+, RRB, Green) ($B/FY)",
                unit_override="CAD billions",
            ),
            secondary=SlotSpec(
                "frt_issuance_flow_bills", "derived",
                label="Treasury bills (year-end stock) ($B/FY)",
                unit_override="CAD billions",
            ),
            tertiary=SlotSpec(
                "frt_issuance_flow_notes", "derived",
                label="Short/medium bonds issued (2/3/5yr) ($B/FY)",
                unit_override="CAD billions",
            ),
            expected_status="WIRED",
            notes=(
                "Plate 10: federal GROSS ISSUANCE FLOW by maturity bucket, FY2019-20 to "
                "FY2026-27. History (FY2019-20 to FY2024-25): Debt Management Report Table 4.1. "
                "Forecast (FY2025-26, FY2026-27, is_forecast=1): DMS 2025-26 + SEU 2026 Annex 3 "
                "plan -- chart gets a forecast divider. THREE buckets stacked: BONDS = 10yr+ + "
                "RRB + Green (= DMR 'Long' + Green); BILLS = treasury bills; NOTES = 2/3/5yr "
                "bonds (= DMR 'Short'; OUR label, not a GoC instrument class). Reconciliation: "
                "BILLS+NOTES+BONDS = DMR 'Total Gross Issuance' each year (FY2024-25: 526). "
                "*** CRITICAL CAVEAT for slot-binding / writer pipeline: the BILLS bucket is the "
                "year-end T-bill STOCK (DMR's own Table 4.1 convention), NOT gross bill auctions. "
                "Do NOT label BILLS as 'auctioned'/'issued' in the flow sense (gross bill auctions "
                "were ~$663B in FY2024-25, ~2.3x the $285B stock). Safe framing follows the DMR "
                "label: 'gross issuance of bonds and bills.' *** REPLACES the old outstanding-stock "
                "series (frt_issuance_bonds/tbills/retail), which remain in the module but are no "
                "longer wired here. Full source ledger: "
                "claude-ref/research/fiscal_redo/issuance_flow_series.md. "
                "Source: pipeline/fetch/frt_fiscal_series.py."
            ),
        ),
        # Panel 11 — Budget 2025 as-presented vs PBO recast operating balance (signed bars).
        # REDESIGN 2026-06-04: repointed to same-vintage pair (both Nov 2025 Budget 2025
        # baseline). The year-by-year gap between the two is PURELY the capital-definition
        # wedge (~$94B cumulative), with no vintage-mismatch compound.
        # PRIMARY:   frt_operating_balance_b2025 (Budget 2025 as-presented, Nov 2025 vintage,
        #                                          FY2024-25 to FY2029-30; PBO Table 4 p.7)
        # SECONDARY: frt_operating_balance_pbo    (PBO recast of Budget 2025, Nov 2025 vintage,
        #                                          FY2024-25 to FY2029-30; PBO Table 4 p.7)
        # Both series sourced from pipeline/fetch/frt_fiscal_series.py Series 18+16.
        # Vintage labels for chart attribution:
        #   primary source_label:   "Budget 2025, as presented"
        #   secondary source_label: "Same budget, PBO definition"
        # NOTE: frt_operating_balance_dof (Series 15, SEU 2026) is RETAINED in the pipeline
        # for other consumers; it is simply no longer the primary here.
        PanelSpec(
            panel_id="panel-11", section="fiscal", panel_num=11,
            file="fiscal/Panel11OperatingBalanceDoFvsPBO.astro",
            primary=SlotSpec(
                "frt_operating_balance_b2025", "derived",
                label="Budget 2025, as presented",
                unit_override="CAD billions",
            ),
            secondary=SlotSpec(
                "frt_operating_balance_pbo", "derived",
                label="Same budget, PBO definition",
                unit_override="CAD billions",
            ),
            expected_status="WIRED",
            notes=(
                "Plate 11 (redesigned 2026-06-04): same-vintage pair comparison -- "
                "Budget 2025 operating balance as-presented vs PBO recast. "
                "PRIMARY = frt_operating_balance_b2025: Budget 2025 day-to-day operating "
                "balance as presented by the Government (PBO RP-2526-017-S Table 4, p.7). "
                "FY2024-25 to FY2029-30, all is_forecast=1. "
                "Source label: 'Budget 2025, as presented'. "
                "SECONDARY = frt_operating_balance_pbo: PBO recast of the same budget "
                "under a stricter international capital standard (IMF GFS 2014). "
                "FY2024-25 to FY2029-30, all is_forecast=1. "
                "Source label: 'Same budget, PBO definition'. "
                "SINGLE VINTAGE: both series are on the Nov 2025 Budget 2025 baseline. "
                "NO vintage-mismatch compound. The year-by-year gap is PURELY the "
                "capital-definition wedge: "
                "FY2024-25 +6.4, FY2025-26 +12.8, FY2026-27 +16.6, "
                "FY2027-28 +17.8, FY2028-29 +19.8, FY2029-30 +20.6 => cumulative ~94.0B. "
                "Government anchor: operating balance crosses zero in FY2028-29 (+1.7B). "
                "PBO recast: never reaches zero (stays at -17.6B in FY2029-30, last year). "
                "Units: CAD billions (positive = surplus, negative = deficit). "
                "Source: pipeline/fetch/frt_fiscal_series.py Series 18 (primary) + 16 (secondary). "
                "frt_operating_balance_dof (Series 15, SEU 2026) remains materialized for "
                "other consumers but is no longer the primary on this panel."
            ),
        ),
    ],
    "markets": [
        PanelSpec(
            panel_id="panel-1", section="markets", panel_num=1,
            file="markets/Panel1CAD.astro",
            primary=SlotSpec("fxusdcad", "raw", label="USDCAD spot"),
            expected_status="NEAR",
            notes="Panel expects BoC CEER index. CEER is MISSING (BoC Valet, key TBD; pipeline.build_financial may fetch in daily run).",
        ),
        PanelSpec(
            panel_id="panel-2", section="markets", panel_num=2,
            file="markets/Panel2Equities.astro",
            primary=SlotSpec("tsx_composite", "raw", label="S&P/TSX Composite"),
            notes="S&P/TSX Composite daily close. Yahoo Finance ^GSPTSE. Added 2026-05-13 per editorial directive.",
        ),
        PanelSpec(
            panel_id="panel-3", section="markets", panel_num=3,
            file="markets/Panel2GoCCurve.astro",
            primary=SlotSpec("yield_2yr", "raw", label="GoC 2y"),
            secondary=SlotSpec("yield_5yr", "raw", label="GoC 5y"),
            tertiary=SlotSpec("yield_10yr", "raw", label="GoC 10y"),
            extras=(
                SlotSpec("yield_30yr", "raw", label="GoC 30y"),
            ),
        ),
        PanelSpec(
            panel_id="panel-6", section="markets", panel_num=6,
            file="markets/Panel4Energy.astro",
            primary=SlotSpec("wti", "raw", label="WTI"),
            extras=(
                SlotSpec("natural_gas_alberta", "raw", label="AECO natural gas (Alberta reference)"),
            ),
        ),
    ],
    "trade": [
        PanelSpec(
            panel_id="panel-3", section="trade", panel_num=3,
            file="trade/Panel3PartnerShares.astro",
            primary=SlotSpec("trade_exports_total", "raw", label="Exports, all countries"),
            secondary=SlotSpec("trade_exports_us", "raw", label="Exports to US"),
            expected_status="NEAR",
            notes="Panel expects shares to US/China/UK/Japan/Mexico. Only trade_exports_us is on disk in raw/; per-partner (china/uk/japan/mexico) MISSING. StatCan Table 12-10-0119 has the vectors; S effort to add 4 vectors to catalog.",
        ),
        # panel-7-alt: Sectoral exports by destination (US vs non-US).
        # NOT a live plate yet — alt channel only.
        # Sources all from StatCan Table 12-10-0182-01, NSA monthly.
        # Non-US series are derived (total - US); stored in data/processed/.
        # See derive_sectoral_exports_by_destination() in pipeline/build.py
        # for the full NAPCS-to-HS mapping rationale and unit notes.
        PanelSpec(
            panel_id="panel-7-alt", section="trade", panel_num=7,
            file="trade/Panel7AltSectoralExports.astro",
            primary=SlotSpec(
                "exports_steel_us", "processed",
                label="Steel exports to US (C$M, NSA)",
                unit_override="C$ millions",
            ),
            secondary=SlotSpec(
                "exports_steel_nonus", "processed",
                label="Steel exports to non-US (C$M, NSA)",
                unit_override="C$ millions",
            ),
            extras=(
                SlotSpec("exports_aluminum_us", "processed",
                         label="Aluminum exports to US (C$M, NSA)",
                         unit_override="C$ millions"),
                SlotSpec("exports_aluminum_nonus", "processed",
                         label="Aluminum exports to non-US (C$M, NSA)",
                         unit_override="C$ millions"),
                SlotSpec("exports_softwood_us", "processed",
                         label="Softwood lumber exports to US (C$M, NSA)",
                         unit_override="C$ millions"),
                SlotSpec("exports_softwood_nonus", "processed",
                         label="Softwood lumber exports to non-US (C$M, NSA)",
                         unit_override="C$ millions"),
                SlotSpec("exports_autos_us", "processed",
                         label="Autos+parts exports to US (C$M, NSA)",
                         unit_override="C$ millions"),
                SlotSpec("exports_autos_nonus", "processed",
                         label="Autos+parts exports to non-US (C$M, NSA)",
                         unit_override="C$ millions"),
            ),
            expected_status="MISSING",
            notes=(
                "ALT chart — NOT a live plate. Sectoral merchandise exports by "
                "destination (US vs non-US), four tariff-exposed sectors: steel, "
                "aluminum, softwood lumber, autos+parts. Monthly NSA, C$ millions, "
                "back to 1997-01. Source: StatCan Table 12-10-0182-01 (NAPCS "
                "sub-chapter level, 113 commodities x 29 partners). "
                "NAPCS-to-HS mapping: Steel = NAPCS 30+31 (HS 72); "
                "Aluminum = NAPCS 32+38 (HS 76); "
                "Softwood = NAPCS 55 (HS 4407, no coniferous/deciduous split); "
                "Autos = NAPCS 81+84 (HS 8703+8708). "
                "Non-US = all-countries total minus US (derived). "
                "MISSING: chart component Panel7AltSectoralExports.astro does "
                "not exist yet; frontend dispatch required before live promotion. "
                "Data is present in data/processed/ after any build that includes "
                "the trade section."
            ),
        ),
        PanelSpec(
            panel_id="panel-8", section="trade", panel_num=8,
            file="trade/Panel8BilateralFlows.astro",
            # Primary = exports to US (highest volume; anchors the panel scale).
            # Secondary = imports from US. All per-country extras listed in ISO-
            # alpha-3 slug order so the chart layer can iterate them uniformly.
            # The customs-basis unadjusted series (Table 12-10-0011-01) are used
            # here rather than the BOP-SA series (12-10-0119-01) because:
            #   (a) Customs basis covers all 27 named partners; BOP-SA partner
            #       breakdown is more limited.
            #   (b) Frontend is computing partner shares (country / all_customs);
            #       unadjusted is correct for share computations where seasonality
            #       largely cancels in numerator / denominator.
            # For trend analysis the chart layer should apply a trailing-3-month
            # average to smooth unadjusted monthly noise before display.
            # GCC gap: UAE, Qatar, Kuwait, Bahrain, Oman are NOT in Table
            # 12-10-0011-01 (not in the 27-principal-partner list based on 2012
            # trade weights). Only Saudi Arabia is available. Frontend should
            # render "data not available" for missing GCC members.
            primary=SlotSpec("trade_exports_us_customs", "raw",
                             label="Exports to United States (customs, NSA)"),
            secondary=SlotSpec("trade_imports_us_customs", "raw",
                               label="Imports from United States (customs, NSA)"),
            tertiary=SlotSpec("trade_exports_all_customs", "raw",
                              label="Total exports, all countries (denominator)"),
            extras=(
                SlotSpec("trade_imports_all_customs", "raw",
                         label="Total imports, all countries (denominator)"),
                # China
                SlotSpec("trade_exports_chn", "raw", label="Exports to China"),
                SlotSpec("trade_imports_chn", "raw", label="Imports from China"),
                # United Kingdom
                SlotSpec("trade_exports_gbr", "raw", label="Exports to United Kingdom"),
                SlotSpec("trade_imports_gbr", "raw", label="Imports from United Kingdom"),
                # Germany
                SlotSpec("trade_exports_deu", "raw", label="Exports to Germany"),
                SlotSpec("trade_imports_deu", "raw", label="Imports from Germany"),
                # France
                SlotSpec("trade_exports_fra", "raw", label="Exports to France"),
                SlotSpec("trade_imports_fra", "raw", label="Imports from France"),
                # Netherlands
                SlotSpec("trade_exports_nld", "raw", label="Exports to Netherlands"),
                SlotSpec("trade_imports_nld", "raw", label="Imports from Netherlands"),
                # Japan
                SlotSpec("trade_exports_jpn", "raw", label="Exports to Japan"),
                SlotSpec("trade_imports_jpn", "raw", label="Imports from Japan"),
                # Mexico
                SlotSpec("trade_exports_mex", "raw", label="Exports to Mexico"),
                SlotSpec("trade_imports_mex", "raw", label="Imports from Mexico"),
                # South Korea
                SlotSpec("trade_exports_kor", "raw", label="Exports to South Korea"),
                SlotSpec("trade_imports_kor", "raw", label="Imports from South Korea"),
                # India (Carney diplomatic-focus)
                SlotSpec("trade_exports_ind", "raw", label="Exports to India"),
                SlotSpec("trade_imports_ind", "raw", label="Imports from India"),
                # Australia (Carney diplomatic-focus)
                SlotSpec("trade_exports_aus", "raw", label="Exports to Australia"),
                SlotSpec("trade_imports_aus", "raw", label="Imports from Australia"),
                # Indonesia (ASEAN, Carney diplomatic-focus)
                SlotSpec("trade_exports_idn", "raw", label="Exports to Indonesia"),
                SlotSpec("trade_imports_idn", "raw", label="Imports from Indonesia"),
                # Singapore (ASEAN hub, Carney diplomatic-focus)
                SlotSpec("trade_exports_sgp", "raw", label="Exports to Singapore"),
                SlotSpec("trade_imports_sgp", "raw", label="Imports from Singapore"),
                # Saudi Arabia (only available GCC member in the 27-partner table)
                SlotSpec("trade_exports_sau", "raw", label="Exports to Saudi Arabia"),
                SlotSpec("trade_imports_sau", "raw", label="Imports from Saudi Arabia"),
                # Taiwan + Hong Kong (supply-chain + re-export proxy)
                SlotSpec("trade_exports_twn", "raw", label="Exports to Taiwan"),
                SlotSpec("trade_imports_twn", "raw", label="Imports from Taiwan"),
                SlotSpec("trade_exports_hkg", "raw", label="Exports to Hong Kong"),
                SlotSpec("trade_imports_hkg", "raw", label="Imports from Hong Kong"),
            ),
            expected_status="WIRED",
            notes=(
                "Bilateral merchandise trade flows, customs basis, unadjusted. "
                "Source: StatCan Table 12-10-0011-01 (CANSIM 228-0069). Monthly, "
                "1997-01 to present (latest: 2026-03). 27 principal trading partners "
                "based on 2012 annual trade weights. Vectors resolved 2026-05-14 via "
                "bulk CSV download (getCubeMetadata returns 404 for this table -- "
                "same WDS quirk as Table 11-10-0065-01; data fetch works via "
                "getDataFromVectorsAndLatestNPeriods batch endpoint). "
                "COVERAGE GAPS: Vietnam, Thailand (ASEAN) and UAE, Qatar, Kuwait, "
                "Bahrain, Oman (GCC) are NOT in the 27-partner list -- no StatCan "
                "vector-based alternative exists for these countries within this "
                "table. Only Saudi Arabia is available from the GCC. Frontend should "
                "render 'data not available' for missing partners. "
                "STRUCTURAL BREAK: UK series (dim5=4) runs unbroken 1997+, but "
                "the EU aggregate (dim5=3) excluded UK from Jan-2021 onward. "
                "Chart-builder notes: "
                "(1) Partner share = country series / all_customs total x 100. "
                "(2) Apply 3-month trailing average to smooth NSA monthly noise. "
                "(3) Bucket logic (Carney targets, GCC, ASEAN) is chart-internal. "
                "See panel-7-alt for sectoral US-vs-non-US breakdown."
            ),
        ),
        PanelSpec(
            panel_id="panel-9", section="trade", panel_num=9,
            file="trade/Panel9GoldExports.astro",
            # Primary slot: gold/PGM exports level (total all countries)
            # Secondary: gold to UK (London Bullion Market — typically 90-97% of total)
            # Tertiary: gold to US
            # Extras: gold spot price (USD/oz, monthly, right-axis companion)
            # Chart-builder note: two-panel composite recommended —
            #   Left panel: gold exports level (C$M) with UK and total series
            #   Right panel: gold price (USD/oz) on shared time axis
            # Do NOT use dual-axis on a single panel; the unit mismatch (C$M vs USD/oz)
            # is visually deceptive at the scale involved. Two adjacent panels with
            # a shared x-axis (synchronized zoom) is the correct form.
            # NAPCS 35 editorial caveat: includes silver and PGM alongside gold.
            # No finer gold-only sub-chapter available in WDS at this granularity.
            primary=SlotSpec("exports_gold_total", "processed",
                             label="Gold/PGM exports, all countries (C$M)"),
            secondary=SlotSpec("exports_gold_uk", "processed",
                               label="Gold/PGM exports to UK (C$M)"),
            tertiary=SlotSpec("exports_gold_us", "processed",
                              label="Gold/PGM exports to US (C$M)"),
            extras=(
                SlotSpec("gold_price_monthly", "processed",
                         label="Gold price (USD/oz, monthly last-obs)"),
            ),
            expected_status="WIRED",
            notes=(
                "Gold/PGM exports (NAPCS 35) by destination + COMEX gold price. "
                "Source: StatCan Table 12-10-0182-01 (exports) and Yahoo GC=F (price). "
                "NSA monthly, 1997-01 to present. "
                "Key editorial finding: UK absorbs ~90-97% of all Canadian gold/PGM "
                "exports in most months (London Bullion Market clearing). The March 2026 "
                "spike in Canada-UK merchandise trade is almost entirely this series "
                "re-routing gold through London as COMEX US tariff risk rose. "
                "NAPCS 35 caveat: bundles gold + silver + PGM; no finer cut available "
                "in 12-10-0182-01. For context, gold is ~85-90% of NAPCS 35 value "
                "based on historical HS 7108 share of HS 71xx (not directly verifiable "
                "in this table -- editorial should note the bundling). "
                "Vectors: v1863625573 (total), v1863625693 (UK), v1863625603 (US). "
                "Resolved 2026-05-14."
            ),
        ),
    ],
}


# --------------------------------------------------------------------------- #
# Disk readers
# --------------------------------------------------------------------------- #

LABOUR_FLOW_SOURCE_FILES = [
    "data/raw/unemployment_level.csv",
    "data/raw/unemployment_rate.csv",
    "data/raw/unemployment_1_to_4_weeks.csv",
]


def _read_labour_flow_slot(slot: SlotSpec, data_root: Path) -> Optional[dict]:
    """Derive labour-market transition rates for the flow-rate panel.

    The chart uses the Elsby-Michaels-Solon stock-flow approximation:
      separation_t ~= U_short_{t+1} / E_t
      finding_t = 1 - (U_{t+1} - U_short_{t+1}) / U_t

    Values are emitted in monthly percent units.
    """
    try:
        u = pd.read_csv(data_root / "raw" / "unemployment_level.csv", parse_dates=["date"])
        ur = pd.read_csv(data_root / "raw" / "unemployment_rate.csv", parse_dates=["date"])
        short = pd.read_csv(data_root / "raw" / "unemployment_1_to_4_weeks.csv", parse_dates=["date"])
    except Exception as exc:  # noqa: BLE001
        logger.warning("panel_data: failed to derive labour flow slot %s: %s: %s",
                       slot.series, type(exc).__name__, exc)
        return None

    merged = (
        u.rename(columns={"value": "U"})
        .merge(ur.rename(columns={"value": "UR"}), on="date", how="inner")
        .merge(short.rename(columns={"value": "U_short"}), on="date", how="inner")
        .sort_values("date")
        .reset_index(drop=True)
    )
    if merged.empty:
        return None

    rows: list[dict] = []
    for i in range(len(merged) - 1):
        t = merged.iloc[i]
        t1 = merged.iloc[i + 1]
        try:
            u_t = float(t["U"])
            ur_t = float(t["UR"])
            u_t1 = float(t1["U"])
            u_short_t1 = float(t1["U_short"])
        except (TypeError, ValueError):
            continue
        if pd.isna(u_t) or pd.isna(ur_t) or pd.isna(u_t1) or pd.isna(u_short_t1):
            continue
        if u_t <= 0 or ur_t <= 0:
            continue
        labour_force = u_t / (ur_t / 100)
        employment = labour_force - u_t
        if employment <= 0:
            continue
        if slot.series == "labour_separation_rate":
            value = (u_short_t1 / employment) * 100
        elif slot.series == "labour_job_finding_rate":
            value = (1 - (u_t1 - u_short_t1) / u_t) * 100
        else:
            return None
        rows.append({"date": t["date"], "value": value})

    df = pd.DataFrame(rows)
    if df.empty:
        return None
    df = df.sort_values("date").tail(RECENT_WINDOW["monthly"]).reset_index(drop=True)
    as_of_iso = pd.to_datetime(df["date"].iloc[-1]).date().isoformat()
    return {
        "key": slot.series,
        "label": slot.label,
        "tier": "derived",
        "data": _df_to_records(df),
        "unit": "%",
        "frequency": "monthly",
        "asOfISO": as_of_iso,
        "source": "Statistics Canada Labour Force Survey; Sibley Creek derived flow rates",
        "sourceUrl": None,
        "sourceId": "14-10-0287-01; 14-10-0342-01",
        "releaseDate": None,
    }


def _resolve_slot_path(slot: SlotSpec, data_root: Path) -> Optional[str]:
    """Return the relative-to-ROOT path of the CSV that backs this slot.

    Walks the same tier-fallback order as _read_slot. Returns a POSIX-style
    relative path string (e.g. "data/raw/cpi_all_items.csv") or None if no
    file is found on disk.

    Labour-flow derived slots are not backed by a single CSV; callers should
    use LABOUR_FLOW_SOURCE_FILES directly for those series.
    """
    if slot.series in {"labour_separation_rate", "labour_job_finding_rate"}:
        return None  # handled via LABOUR_FLOW_SOURCE_FILES

    tiers = [slot.tier] + [t for t in ("processed", "derived", "raw") if t != slot.tier]
    for tier in tiers:
        csv_path = data_root / tier / f"{slot.series}.csv"
        if csv_path.exists():
            # Return path relative to project root using forward slashes
            return f"data/{tier}/{slot.series}.csv"
    return None


def _read_slot(slot: SlotSpec, data_root: Path) -> Optional[dict]:
    """Read one slot's CSV (with .meta.json) and return the per-panel payload.

    Returns None if the CSV is not on disk in any of the three tiers.
    """
    if slot.series in {"labour_separation_rate", "labour_job_finding_rate"}:
        return _read_labour_flow_slot(slot, data_root)

    tiers = [slot.tier] + [t for t in ("processed", "derived", "raw") if t != slot.tier]
    for tier in tiers:
        csv_path = data_root / tier / f"{slot.series}.csv"
        meta_path = data_root / tier / f"{slot.series}.meta.json"
        if not csv_path.exists():
            continue
        try:
            df = pd.read_csv(csv_path, parse_dates=["date"])
        except Exception as exc:  # noqa: BLE001
            logger.warning("panel_data: failed to parse %s: %s: %s", csv_path, type(exc).__name__, exc)
            return None
        meta: dict = {}
        if meta_path.exists():
            try:
                meta = json.loads(meta_path.read_text(encoding="utf-8"))
            except Exception as exc:  # noqa: BLE001
                logger.warning("panel_data: failed to parse meta %s: %s: %s",
                               meta_path, type(exc).__name__, exc)
                meta = {}
        # Window the data to keep file sizes sane. Per-slot override allows
        # panels that need deeper history (e.g. inflation Panel 3 breadth,
        # which references 1996-2019 averages) to opt out of the default.
        freq = (meta.get("frequency") or "monthly").lower()
        default_window = RECENT_WINDOW.get(freq, RECENT_WINDOW["monthly"])
        window = slot.window_override if slot.window_override is not None else default_window
        if "date" in df.columns and not df.empty:
            df = df.sort_values("date").tail(window).reset_index(drop=True)
        as_of_iso = None
        if "date" in df.columns and not df.empty:
            try:
                as_of_iso = pd.to_datetime(df["date"].iloc[-1]).date().isoformat()
            except Exception:
                as_of_iso = None
        records = _df_to_records(df)
        return {
            "key": slot.series,
            "label": slot.label,
            "tier": tier,
            "data": records,
            "unit": slot.unit_override or meta.get("units"),
            "frequency": freq,
            "asOfISO": as_of_iso,
            "source": meta.get("source"),
            "sourceUrl": meta.get("source_url"),
            "sourceId": meta.get("source_id"),
            "releaseDate": meta.get("release_date"),
        }
    logger.warning("panel_data: slot '%s' not found in any tier", slot.series)
    return None


def _df_to_records(df: pd.DataFrame) -> list[dict]:
    """Render a DataFrame as a list of JSON-safe records.

    Date column is ISO-formatted. Other columns are floats / strings / None.

    Safety contract: no NaN or Infinity is ever emitted in the output.
    Both map to None (JSON null). This prevents invalid JSON output
    (json.dumps() silently emits 'Infinity'/'NaN' which are not valid
    JSON; browsers parse them as undefined, producing blank charts).
    """
    import math
    if df.empty:
        return []
    out: list[dict] = []
    cols = list(df.columns)
    for _, row in df.iterrows():
        rec: dict = {}
        for c in cols:
            v = row[c]
            if c == "date":
                try:
                    rec[c] = pd.Timestamp(v).date().isoformat()
                except Exception:
                    rec[c] = str(v)
            else:
                try:
                    fv = float(v)
                except (TypeError, ValueError):
                    rec[c] = None if pd.isna(v) else str(v)
                    continue
                # Both NaN and Infinity are disallowed in JSON output.
                # pd.isna(float('inf')) == False, so we must also check
                # math.isinf() explicitly.
                if pd.isna(fv) or math.isinf(fv):
                    rec[c] = None
                else:
                    rec[c] = fv
        out.append(rec)
    return out


# --------------------------------------------------------------------------- #
# Per-section emitter
# --------------------------------------------------------------------------- #

def _read_metadata(path_rel: str, data_root: Path) -> Optional[dict]:
    """Load a companion JSON from data/derived/<path_rel> for a panel.

    Returns the parsed dict, or None if the file is missing / unparseable.
    Per-panel-metadata is for scalar reference values that don't fit the
    {date, value} time-series schema (e.g. historical averages for the
    breadth chart's reference bands).
    """
    p = data_root / "derived" / path_rel
    if not p.exists():
        logger.warning("panel_data: metadata file not found: %s", p)
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        logger.warning("panel_data: failed to parse metadata %s: %s: %s",
                       p, type(exc).__name__, exc)
        return None


def _collect_source_files(spec: "PanelSpec", data_root: Path) -> list[str]:
    """Collect the set of disk-resident source file paths for a panel.

    Returns a deduplicated, sorted list of project-root-relative POSIX paths
    (e.g. ["data/raw/crea_resales.csv", "data/raw/crea_snlr.csv"]).

    Rules:
    - Each SlotSpec resolves to a CSV via _resolve_slot_path (tier fallback).
    - Labour-flow derived slots resolve to LABOUR_FLOW_SOURCE_FILES.
    - metadata_path resolves to data/derived/<metadata_path>.
    - BoC Valet / IMF / FRED series that land on disk as raw CSVs are captured
      automatically by _resolve_slot_path if the file exists.
    - Slots that have no file on disk (slot not yet fetched, or backed purely by
      an in-memory derivation without a CSV) contribute nothing -- the gate will
      not fire on missing-and-untracked slots for un-wired panels.
    """
    paths: set[str] = set()

    all_slots: list["SlotSpec"] = []
    if spec.primary is not None:
        all_slots.append(spec.primary)
    if spec.secondary is not None:
        all_slots.append(spec.secondary)
    if spec.tertiary is not None:
        all_slots.append(spec.tertiary)
    all_slots.extend(spec.extras)

    for slot in all_slots:
        if slot.series in {"labour_separation_rate", "labour_job_finding_rate"}:
            paths.update(LABOUR_FLOW_SOURCE_FILES)
        else:
            p = _resolve_slot_path(slot, data_root)
            if p is not None:
                paths.add(p)

    if spec.metadata_path is not None:
        meta_disk = data_root / "derived" / spec.metadata_path
        if meta_disk.exists():
            paths.add(f"data/derived/{spec.metadata_path}")

    return sorted(paths)


# --------------------------------------------------------------------------- #
# Co-dated slot groups
# --------------------------------------------------------------------------- #

# Series that are quoted together as a single-date snapshot must share a final
# observation date. The markets curve prose stamps all three maturities with
# one date ("The GoC 2-year closed at X, the 5-year at Y, and the 10-year at
# Z on {date}") -- BoC Valet can publish one maturity a day behind the others,
# and in that state the sentence would assert a close on a date that maturity
# never printed (fact-check gate item B3, 2026-06-09).
#
# Resolution: degrade gracefully, do NOT fail the build. Trim each series in
# the group to the most recent date ALL of them share, so the prose quotes a
# coherent, truthful single-date snapshot (one day stale at worst) and the
# chart plots the same aligned curve. A benign one-day Valet lag must never
# take the page down. When trimming occurs the panel carries a
# `coDatedAlignment` record so scripts/check_panel_data_integrity.mjs can
# WARN (visibility for a persistent lag) without failing the build.
#
# Scope is deliberately per-panel-group: only series quoted as one snapshot
# are co-dated. Do not add unrelated series (e.g. yield_30yr is on the curve
# chart but never date-stamped in prose; a 30y publish lag should not degrade
# the headline maturities).
CO_DATED_SLOT_GROUPS: dict[tuple[str, str], tuple[str, ...]] = {
    ("markets", "panel-3"): ("yield_2yr", "yield_5yr", "yield_10yr"),
}


def _align_co_dated_slots(panel_obj: dict, group: tuple[str, ...],
                          *, section: str, panel_id: str) -> None:
    """Trim a panel's co-dated slots to their most recent common date.

    Mutates the slot payloads in place. No-op when the group's final
    observation dates already agree, or when fewer than two group members
    are present. Composes with upstream guards: the intraday-partial guard
    (pipeline/fetch/yahoo.py) has already dropped partial bars before data
    lands on disk, so this sees completed closes only.

    On trim, records `panel_obj["coDatedAlignment"]` with the aligned-to
    date and which series lost trailing observations -- the integrity gate
    surfaces this as a WARN so a persistent upstream lag is visible in
    build logs rather than silent.
    """
    members: list[dict] = []
    named = [panel_obj.get(n) for n in ("primary", "secondary", "tertiary")]
    for payload in named + list(panel_obj.get("extras") or []):
        if payload and payload.get("key") in group and payload.get("data"):
            members.append(payload)
    if len(members) < 2:
        return

    latest_by_key = {m["key"]: m["data"][-1]["date"] for m in members}
    if len(set(latest_by_key.values())) == 1:
        return  # already co-dated; nothing to do

    # Most recent date present in EVERY member (robust to mid-series gaps,
    # not just a trailing one-day lag).
    common_dates = set(r["date"] for r in members[0]["data"])
    for m in members[1:]:
        common_dates &= {r["date"] for r in m["data"]}
    if not common_dates:
        # Pathological (windowed series with zero overlap). Leave data as-is;
        # the staleness / trailing-null integrity checks will surface the
        # underlying problem. Log loudly either way.
        logger.error(
            "panel_data: %s/%s co-dated group %s has NO common observation "
            "date -- cannot align; latest dates: %s",
            section, panel_id, group, latest_by_key,
        )
        return

    common = max(common_dates)  # ISO dates: lexicographic == chronological
    trimmed_from: dict[str, str] = {}
    for m in members:
        last = m["data"][-1]["date"]
        if last > common:
            m["data"] = [r for r in m["data"] if r["date"] <= common]
            m["asOfISO"] = m["data"][-1]["date"]
            trimmed_from[m["key"]] = last

    panel_obj["coDatedAlignment"] = {
        "group": sorted(latest_by_key),
        "alignedTo": common,
        "trimmedFrom": trimmed_from,
    }
    logger.warning(
        "panel_data: %s/%s co-dated alignment trimmed %s to common date %s "
        "(upstream published maturities mis-dated: %s)",
        section, panel_id, sorted(trimmed_from), common, latest_by_key,
    )


def build_section_payload(section: str, data_root: Path) -> dict:
    """Build the per-section panel data payload for one section."""
    specs = PANEL_SPECS.get(section, [])
    panels: dict[str, dict] = {}
    for spec in specs:
        panel_obj: dict = {
            "panelNum": spec.panel_num,
            "file": spec.file,
            "expectedStatus": spec.expected_status,
            "notes": spec.notes,
            "primary": None,
            "secondary": None,
            "tertiary": None,
            "extras": [],
            "source_files": _collect_source_files(spec, data_root),
        }
        try:
            if spec.primary is not None:
                panel_obj["primary"] = _read_slot(spec.primary, data_root)
            if spec.secondary is not None:
                panel_obj["secondary"] = _read_slot(spec.secondary, data_root)
            if spec.tertiary is not None:
                panel_obj["tertiary"] = _read_slot(spec.tertiary, data_root)
            for extra in spec.extras:
                payload = _read_slot(extra, data_root)
                if payload is not None:
                    panel_obj["extras"].append(payload)
            if spec.metadata_path is not None:
                meta_payload = _read_metadata(spec.metadata_path, data_root)
                if meta_payload is not None:
                    panel_obj["metadata"] = meta_payload
            co_dated_group = CO_DATED_SLOT_GROUPS.get((section, spec.panel_id))
            if co_dated_group is not None:
                _align_co_dated_slots(panel_obj, co_dated_group,
                                      section=section, panel_id=spec.panel_id)
        except Exception as exc:  # noqa: BLE001
            logger.error("panel_data: panel %s/%s construction failed: %s: %s",
                         section, spec.panel_id, type(exc).__name__, exc)
            panel_obj["error"] = f"{type(exc).__name__}: {exc}"
        panels[spec.panel_id] = panel_obj
    return {
        "section": section,
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "panels": panels,
    }


# --------------------------------------------------------------------------- #
# Data integrity validator
# --------------------------------------------------------------------------- #

# Per-series sane-value ranges. Catches obvious corruptions (e.g. a yield of
# 999% or a TSX value of 0). These are deliberately wide: the goal is to
# catch data pipeline failures, not normal macro variability.
# Format: series_slug -> (min_allowed, max_allowed) or None to skip range check.
SERIES_SANE_RANGES: dict[str, tuple[float, float]] = {
    # GoC bond yields (%)
    "yield_2yr":  (0.0, 25.0),
    "yield_5yr":  (0.0, 25.0),
    "yield_10yr": (0.0, 25.0),
    "yield_30yr": (0.0, 25.0),
    # Overnight rate (%)
    "overnight_rate":       (0.0, 25.0),
    "overnight_rate_daily": (0.0, 25.0),
    # CPI (index level, 2002=100 base; range reflects post-2002 era)
    "cpi_all_items":     (90.0, 250.0),
    "cpi_all_items_nsa": (90.0, 250.0),
    # USDCAD (spot)
    "fxusdcad": (0.5, 2.5),
    # TSX Composite level
    "tsx_composite": (1000.0, 200000.0),
    # WTI (USD/bbl)
    "wti": (0.0, 500.0),
    # Unemployment rate (%)
    "unemployment_rate": (0.0, 30.0),
    # Employment level (millions)
    "employment_level": (5.0, 30.0),
    # GoC-UST spreads (percentage points)
    "goc_ust_spread_2y":  (-10.0, 10.0),
    "goc_ust_spread_10y": (-10.0, 10.0),
    # BoC-Fed spread (basis points)
    "boc_fed_spread_monthly": (-500.0, 500.0),
    # CORRA spread (basis points)
    "corra_overnight_spread_bps": (-100.0, 100.0),
}

# Staleness thresholds by series frequency.
# A series is stale if its most recent date is more than N calendar days ago.
# These are defaults; daily market series are held to a tighter standard.
FRESHNESS_THRESHOLDS_DAYS: dict[str, int] = {
    "daily":     3,    # North American market business days
    "weekly":    21,   # 3 weeks (BoC balance sheet publishes with ~1-week lag)
    "monthly":   105,  # reference-month stamps can run ~60d after month-end
    "quarterly": 220,  # reference-quarter stamps can run ~90d after quarter-end
    "annual":    400,  # annual publications run 3-12 months late
    "irregular": 400,
}

STALENESS_FAIL_SERIES: set[str] = {
    "yield_2yr",
    "yield_5yr",
    "yield_10yr",
    "yield_30yr",
    "overnight_rate_daily",
    "fxusdcad",
    "tsx_composite",
    "wti",
    "brent",
    "us_2yr",
    "us_10yr",
    "goc_ust_spread_2y",
    "goc_ust_spread_10y",
    "corra_overnight_spread_bps",
}

# Per-series staleness overrides for sources with atypical publication lags.
# StatCan bilateral trade data (Table 12-10-0011-01 customs basis, 27-partner)
# runs ~90 days behind. CREA HPI runs ~30 days. DoF Fiscal Monitor ~70 days.
# Override format: series_slug -> max_age_days.
SERIES_STALENESS_OVERRIDES: dict[str, int] = {
    # StatCan Table 12-10-0011-01 (customs bilateral trade, 27 partners)
    # Releases ~60-90 days after reference month.
    "trade_exports_us_customs":    120,
    "trade_imports_us_customs":    120,
    "trade_exports_all_customs":   120,
    "trade_imports_all_customs":   120,
    "trade_exports_chn": 120, "trade_imports_chn": 120,
    "trade_exports_gbr": 120, "trade_imports_gbr": 120,
    "trade_exports_deu": 120, "trade_imports_deu": 120,
    "trade_exports_fra": 120, "trade_imports_fra": 120,
    "trade_exports_nld": 120, "trade_imports_nld": 120,
    "trade_exports_jpn": 120, "trade_imports_jpn": 120,
    "trade_exports_mex": 120, "trade_imports_mex": 120,
    "trade_exports_kor": 120, "trade_imports_kor": 120,
    "trade_exports_ind": 120, "trade_imports_ind": 120,
    "trade_exports_aus": 120, "trade_imports_aus": 120,
    "trade_exports_idn": 120, "trade_imports_idn": 120,
    "trade_exports_sgp": 120, "trade_imports_sgp": 120,
    "trade_exports_sau": 120, "trade_imports_sau": 120,
    "trade_exports_twn": 120, "trade_imports_twn": 120,
    "trade_exports_hkg": 120, "trade_imports_hkg": 120,
    # StatCan Table 12-10-0182-01 (sectoral merchandise exports)
    # Same ~90-day lag as bilateral customs data.
    "exports_steel_us":      120, "exports_steel_nonus":    120,
    "exports_aluminum_us":   120, "exports_aluminum_nonus": 120,
    "exports_softwood_us":   120, "exports_softwood_nonus": 120,
    "exports_autos_us":      120, "exports_autos_nonus":    120,
    "exports_gold_total":    120, "exports_gold_uk":        120,
    "exports_gold_us":       120,
    # CREA HPI: typically ~30-35 days after reference month. Some geo series
    # (resales by CMA) have much longer gaps; set conservatively at 270 days.
    "crea_hpi_canada_yoy":    70, "crea_hpi_toronto_yoy":    70,
    "crea_hpi_vancouver_yoy": 70, "crea_hpi_montreal_yoy":   70,
    "crea_hpi_calgary_yoy":   70, "crea_hpi_ottawa_yoy":     70,
    "crea_hpi_edmonton_yoy":  70,
    "crea_snlr":              150,
    "crea_resales":           150, "crea_resales_toronto": 300,
    "crea_resales_vancouver": 300, "crea_resales_calgary": 300,
    # CBA mortgage arrears: ~75-day lag.
    "cba_mortgage_arrears_national": 100,
    # DoF Fiscal Monitor: ~60-100 days (varies by March year-end vs mid-year).
    "dof_fiscal_monthly_balance":  120,
    "dof_fiscal_ytd_balance":      120,
    "dof_fiscal_ytd_summary":      120,
    "debt_service_ratio":          120,
    "debt_service_ratio_band_lo":  120,
    "debt_service_ratio_band_hi":  120,
    # IMF WEO: annual publication, ~4-6 months post-year-end.
    "imf_can_gg_balance_pct_gdp":    400,
    "imf_can_gg_gross_debt_pct_gdp": 400,
    # BoC balance sheet: weekly, typically 1-2 week lag.
    "boc_settlement_balances": 21,
    "boc_total_assets": 21, "boc_total_liabilities": 21,
    "boc_goc_bonds": 21, "boc_tbills": 21, "boc_advances": 21,
    "boc_repos": 21, "boc_reverse_repos": 21,
    "boc_banknotes": 21, "boc_goc_deposits": 21,
    # BoC output gap (MPR vintage): can lag when an MPR does not refresh it.
    "output_gap_mpr": 270,
    # JVWS (StatCan Table 14-10-0325): monthly, ~75-day lag.
    "job_vacancy_rate":  90,
    "job_vacancy_level": 90,
    # Housing starts / permits: monthly, ~30-35 day lag for starts, longer for permits.
    "housing_starts":           75,
    "units_under_construction": 75,
    "residential_permits":      120,
    # Household DSR (StatCan 11-10-0065-01): quarterly, ~75-day lag.
    "household_dsr": 270,
    # BoC housing affordability index: quarterly, ~75-day lag.
    "housing_affordability": 270,
    # AECO natural gas (Alberta Economic Dashboard): monthly, ~60-day lag.
    "natural_gas_alberta": 120,
    # BoC-Fed spread: derived from monthly rate data; same lag as overnight rate.
    "boc_fed_spread_monthly": 75,
    # Trade exports total (StatCan 12-10-0119, BOP basis): ~90-day lag.
    "trade_exports_total": 120,
    "trade_exports_us":    120,
    # GoC-UST spreads (derived, limited by FRED DGS2/DGS10 availability)
    "goc_ust_spread_2y":  10,
    "goc_ust_spread_10y": 10,
}


def _observed_fixed_holiday(year: int, month: int, day: int) -> date:
    d = date(year, month, day)
    if d.weekday() == 5:
        return d - timedelta(days=1)
    if d.weekday() == 6:
        return d + timedelta(days=1)
    return d


def _nth_weekday_of_month(year: int, month: int, weekday: int, n: int) -> date:
    d = date(year, month, 1)
    offset = (weekday - d.weekday()) % 7
    return d + timedelta(days=offset + ((n - 1) * 7))


def _last_weekday_of_month(year: int, month: int, weekday: int) -> date:
    if month == 12:
        d = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        d = date(year, month + 1, 1) - timedelta(days=1)
    offset = (d.weekday() - weekday) % 7
    return d - timedelta(days=offset)


def _easter_date(year: int) -> date:
    a = year % 19
    b = year // 100
    c = year % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = ((19 * a) + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + (2 * e) + (2 * i) - h - k) % 7
    m = (a + (11 * h) + (22 * l)) // 451
    month = (h + l - (7 * m) + 114) // 31
    day = ((h + l - (7 * m) + 114) % 31) + 1
    return date(year, month, day)


@lru_cache(maxsize=None)
def _market_holidays(year: int) -> frozenset[date]:
    holidays = {
        _observed_fixed_holiday(year, 1, 1),       # New Year's Day
        _nth_weekday_of_month(year, 1, 0, 3),      # MLK Day
        _nth_weekday_of_month(year, 2, 0, 3),      # Family Day / Presidents' Day
        _easter_date(year) - timedelta(days=2),    # Good Friday
        _last_weekday_of_month(year, 5, 0),        # US Memorial Day
        _nth_weekday_of_month(year, 5, 0, 3),      # Victoria Day
        _observed_fixed_holiday(year, 6, 19),      # Juneteenth
        _observed_fixed_holiday(year, 7, 1),       # Canada Day
        _observed_fixed_holiday(year, 7, 4),       # US Independence Day
        _nth_weekday_of_month(year, 8, 0, 1),      # Civic Holiday
        _nth_weekday_of_month(year, 9, 0, 1),      # Labour Day
        _observed_fixed_holiday(year, 9, 30),      # Truth and Reconciliation Day
        _nth_weekday_of_month(year, 10, 0, 2),     # Canadian Thanksgiving / US Columbus Day
        _observed_fixed_holiday(year, 11, 11),     # Remembrance Day / US Veterans Day
        _nth_weekday_of_month(year, 11, 3, 4),     # US Thanksgiving
        _observed_fixed_holiday(year, 12, 25),     # Christmas Day
        _observed_fixed_holiday(year, 12, 26),     # Boxing Day
    }
    return frozenset(holidays)


def _is_market_business_day(d: date) -> bool:
    if d.weekday() >= 5:
        return False
    return not (
        d in _market_holidays(d.year - 1)
        or d in _market_holidays(d.year)
        or d in _market_holidays(d.year + 1)
    )


def _business_days_since(as_of_date: date, today: date) -> int:
    """Count market business days after as_of_date through today-exclusive."""
    days = 0
    cursor = as_of_date
    while cursor < today:
        cursor = cursor + timedelta(days=1)
        if cursor >= today:
            break
        if _is_market_business_day(cursor):
            days += 1
    return days


def _age_for_cadence(as_of_date: date, today: date, freq: str) -> int:
    if freq == "daily":
        return _business_days_since(as_of_date, today)
    return (today - as_of_date).days


def _check_slot_integrity(
    slot: dict,
    violations: list[str],
    today: date,
    *,
    section: str,
    panel_id: str,
    slot_name: str,
) -> None:
    """Check one slot dict for NaN, Infinity, range violations, and staleness."""
    if slot is None:
        return
    key = slot.get("key", "?")
    data = slot.get("data")
    if not data:
        return

    freq = (slot.get("frequency") or "monthly").lower()
    # Per-series override takes precedence; fall back to frequency-based threshold.
    max_age_days = SERIES_STALENESS_OVERRIDES.get(
        key, FRESHNESS_THRESHOLDS_DAYS.get(freq, 400)
    )
    sane_range = SERIES_SANE_RANGES.get(key)

    # Check each record value
    for i, record in enumerate(data):
        for field, val in record.items():
            if field == "date":
                continue
            if val is None:
                continue  # Allowed nulls (suppressed historical data, etc.)
            if not isinstance(val, (int, float)):
                continue
            fv = float(val)
            if math.isnan(fv):
                violations.append(
                    f"{section}/{panel_id}/{slot_name}/{key}: record[{i}].{field} is NaN"
                )
            elif math.isinf(fv):
                violations.append(
                    f"{section}/{panel_id}/{slot_name}/{key}: record[{i}].{field} is Infinity"
                )
            elif sane_range is not None and field == "value":
                lo, hi = sane_range
                if fv < lo or fv > hi:
                    violations.append(
                        f"{section}/{panel_id}/{slot_name}/{key}: "
                        f"record[{i}].value={fv:.4g} outside sane range [{lo}, {hi}]"
                    )

    # Multi-column slots (e.g. dof_fiscal_ytd_summary) have no "value" field;
    # only flag when the key exists and is null — mirrors the JS gate, where
    # `lastRecord.value === null` is false for a missing key (undefined).
    last_record = data[-1]
    if isinstance(last_record, dict) and "value" in last_record and last_record["value"] is None:
        violations.append(
            f"{section}/{panel_id}/{slot_name}/{key}: "
            "most recent data point has null value (possible stale fetch)"
        )

    # Check staleness via asOfISO. Daily market/yield data fails closed;
    # slower reference-period series are warning-only in the JS gate.
    as_of = slot.get("asOfISO")
    if as_of:
        try:
            as_of_date = date.fromisoformat(as_of[:10])
            age_days = _age_for_cadence(as_of_date, today, freq)
            if key in STALENESS_FAIL_SERIES and age_days > max_age_days:
                suffix = " business days" if freq == "daily" else " days"
                violations.append(
                    f"{section}/{panel_id}/{slot_name}/{key}: "
                    f"asOfISO={as_of} is {age_days}{suffix} old "
                    f"(threshold {max_age_days}d for {freq})"
                )
        except ValueError:
            pass  # Unparseable asOfISO; not a validation concern here


def validate_panel_data_file(path: Path, today: Optional[date] = None) -> list[str]:
    """Validate a single panel_data JSON file for NaN, Infinity, range, and staleness.

    Returns a list of violation strings (empty = clean). Does not raise;
    callers decide whether to warn or fail.
    """
    if today is None:
        today = date.today()

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"{path.name}: invalid JSON ({exc}) -- likely contains NaN or Infinity literals"]
    except Exception as exc:  # noqa: BLE001
        return [f"{path.name}: could not read file ({exc})"]

    section = payload.get("section", path.stem)
    violations: list[str] = []

    for panel_id, panel in payload.get("panels", {}).items():
        for slot_name in ("primary", "secondary", "tertiary"):
            slot = panel.get(slot_name)
            if slot:
                _check_slot_integrity(
                    slot, violations, today,
                    section=section, panel_id=panel_id, slot_name=slot_name,
                )
        for extra in panel.get("extras", []):
            if extra:
                _check_slot_integrity(
                    extra, violations, today,
                    section=section, panel_id=panel_id, slot_name="extra",
                )

    return violations


def build_all_panel_data(
    data_root: Path = DATA_ROOT,
    out_dir: Optional[Path] = None,
) -> dict[str, Path]:
    """Emit one panel-data JSON per section.

    After writing each file, runs the data integrity validator. Any violations
    are logged as errors so the pipeline exits non-zero and the failure is
    visible in CI. This is the systemic gate that prevents NaN/Infinity/stale
    data from reaching the deploy step.

    Returns: section -> written path.
    """
    data_root = Path(data_root)
    if out_dir is None:
        out_dir = data_root / "site" / "panel_data"
    out_dir.mkdir(parents=True, exist_ok=True)
    written: dict[str, Path] = {}
    today = date.today()
    all_violations: list[str] = []

    for section in PANEL_SPECS:
        payload = build_section_payload(section, data_root)
        out_path = out_dir / f"{section}.json"
        out_path.write_text(json.dumps(payload, indent=2, sort_keys=False), encoding="utf-8")
        written[section] = out_path
        logger.info("panel_data: wrote %s (%d panels)", out_path, len(payload["panels"]))

        # Validate the file we just wrote
        violations = validate_panel_data_file(out_path, today=today)
        if violations:
            for v in violations:
                logger.error("panel_data integrity VIOLATION: %s", v)
            all_violations.extend(violations)

    if all_violations:
        logger.error(
            "panel_data: %d integrity violation(s) across %d section(s). "
            "Run `node scripts/check_panel_data_integrity.mjs` for a full report.",
            len(all_violations), len(written),
        )
        raise RuntimeError(
            f"panel_data integrity check failed with {len(all_violations)} violation(s)"
        )
    else:
        logger.info("panel_data: all %d section(s) passed integrity check.", len(written))

    return written


def main() -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    build_all_panel_data()
    return 0


if __name__ == "__main__":
    import sys
    from pipeline.notifications.failure import notify_on_failure
    with notify_on_failure("panel_data"):
        sys.exit(main())
