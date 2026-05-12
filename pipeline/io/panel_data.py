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
from dataclasses import dataclass
from datetime import datetime, timezone
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
    "gdp": [
        PanelSpec(
            panel_id="panel-1", section="gdp", panel_num=1,
            file="gdp/Panel1HeadlineGDP.astro",
            primary=SlotSpec("gdp_monthly", "raw", label="Monthly real GDP (level)"),
            secondary=SlotSpec("gdp_quarterly", "raw", label="Quarterly real GDP (level)"),
            notes="Panel needs m/m % and Q/Q SAAR. Chart-builder derives both from levels; or wire processed/gdp_monthly_mom (not on disk yet).",
        ),
        PanelSpec(
            panel_id="panel-2", section="gdp", panel_num=2,
            file="gdp/Panel2IndustryAggregate.astro",
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
            panel_id="panel-3", section="gdp", panel_num=3,
            file="gdp/Panel3Contributions.astro",
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
            panel_id="panel-4", section="gdp", panel_num=4,
            file="gdp/Panel4PerCapita.astro",
            primary=SlotSpec("gdp_quarterly", "raw", label="Aggregate real GDP (quarterly)"),
            secondary=SlotSpec("pop_immigrants", "raw", label="Population proxy (component)"),
            expected_status="NEAR",
            notes="Needs pop_total quarterly level; pipeline currently lacks a Canada-total population vector (pop_total V1 excluded from boc-tracker per fetch.py comment). Per-capita YoY derivation requires it. MISSING: pop_total quarterly level.",
        ),
        PanelSpec(
            panel_id="panel-5", section="gdp", panel_num=5,
            file="gdp/Panel5OutputGap.astro",
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
            panel_id="panel-6", section="gdp", panel_num=6,
            file="gdp/Panel6IndustryCyclical.astro",
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
            primary=SlotSpec("cpi_all_items_yoy", "processed", label="Headline CPI Y/Y"),
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
        PanelSpec(
            panel_id="panel-6", section="inflation", panel_num=6,
            file="inflation/Panel6PassThrough.astro",
            # Canon (editorial/dashboard_purpose.md Section 4.2 element 6):
            # side-by-side strip-chart panel,
            #   pane A: USDCAD Y/Y vs goods-ex-energy CPI Y/Y
            #   pane B: LFS-Micro wage Y/Y vs services-ex-shelter CPI Y/Y
            # Gated per canon: "if they slip, pass-through defers to v1.5."
            #
            # Status (2026-05-11): all four pass-through derivations MISSING.
            # The chart renders PanelEmpty until backend lands them. The
            # SlotSpecs below are the target wiring once the four processed
            # CSVs exist; expected_status="MISSING" so _read_slot logs a
            # warning today instead of silently falling back.
            primary=SlotSpec("usdcad_yoy", "processed",
                             label="USDCAD Y/Y"),
            secondary=SlotSpec("cpi_goods_ex_energy_yoy", "processed",
                               label="Goods ex-energy CPI Y/Y"),
            tertiary=SlotSpec("lfs_micro_yoy", "processed",
                              label="LFS-Micro wage Y/Y"),
            extras=(
                SlotSpec("cpi_services_ex_shelter_yoy", "processed",
                         label="Services ex-shelter CPI Y/Y"),
            ),
            expected_status="MISSING",
            notes=(
                "Pass-through panel gated on four backend derivations - none on "
                "disk yet. Required: processed/usdcad_yoy (monthly-mean FX, Y/Y), "
                "processed/lfs_micro_yoy (BoC LFS-Micro Y/Y), "
                "processed/cpi_goods_ex_energy_yoy and "
                "processed/cpi_services_ex_shelter_yoy (basket-weighted ex-aggregates "
                "per canon 4.2 element 4 methodology gate). Chart renders PanelEmpty "
                "until all four land. See Panel6PassThrough.astro header for the "
                "paste-ready backend brief."
            ),
        ),
    ],
    "labour": [
        PanelSpec(
            panel_id="panel-1", section="labour", panel_num=1,
            file="labour/Panel1LFSHeadline.astro",
            primary=SlotSpec("unemployment_rate", "raw", label="Unemployment rate"),
            secondary=SlotSpec("employment_rate", "raw", label="Employment rate"),
            tertiary=SlotSpec("participation_rate", "raw", label="Participation rate"),
        ),
        PanelSpec(
            panel_id="panel-2", section="labour", panel_num=2,
            file="labour/Panel2PerCapita.astro",
            primary=SlotSpec("unemployment_level", "raw", label="Employment level (proxy)"),
            secondary=SlotSpec("aggregate_hours", "raw", label="Aggregate hours worked"),
            expected_status="NEAR",
            notes="Needs employment_level (StatCan v2062811) and pop_total to compute per-capita YoY. employment_level is MISSING (StatCan catalog has it but boc-tracker did not lift; can fetch via existing pipeline.fetch.statcan). aggregate_hours.csv exists in data/raw/ (Sibley-fetched).",
        ),
        PanelSpec(
            panel_id="panel-3", section="labour", panel_num=3,
            file="labour/Panel3WageBand.astro",
            primary=SlotSpec("lfs_wages_all", "raw", label="LFS wages, all"),
            secondary=SlotSpec("lfs_wages_permanent", "raw", label="LFS wages, permanent"),
            tertiary=SlotSpec("seph_earnings", "raw", label="SEPH earnings"),
            extras=(
                SlotSpec("lfs_micro", "raw", label="BoC LFS-Micro composition-adj. wage"),
                SlotSpec("cpi_services_yoy", "processed", label="Services CPI Y/Y (real-wage anchor)"),
            ),
            notes="Chart-builder computes Y/Y on each level series at render time; or backend can add processed/<wage>_yoy companions.",
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
            panel_id="panel-5", section="labour", panel_num=5,
            file="labour/Panel5IRCCSupplyTrajectory.astro",
            primary=SlotSpec("pop_immigrants", "raw", label="Immigrants (PR proxy)"),
            secondary=SlotSpec("pop_net_npr", "raw", label="Net NPR"),
            tertiary=SlotSpec("pop_npr_inflows", "raw", label="NPR inflows"),
            expected_status="NEAR",
            notes="IRCC plans live in data/ircc_levels_plan.json (already in repo). Trailing-4Q PR/NPR derivation needs rolling sums on raw quarterly inflows; chart-builder applies. Plan vintages: WIRED (in repo).",
        ),
        PanelSpec(
            panel_id="panel-6", section="labour", panel_num=6,
            file="labour/Panel6RegionalDumbbell.astro",
            primary=SlotSpec("lfs_on_unemployment_rate", "raw", label="ON unemployment rate"),
            secondary=SlotSpec("lfs_qc_unemployment_rate", "raw", label="QC unemployment rate"),
            tertiary=SlotSpec("lfs_ab_unemployment_rate", "raw", label="AB unemployment rate"),
            extras=(
                SlotSpec("lfs_bc_unemployment_rate", "raw", label="BC unemployment rate"),
                SlotSpec("lfs_ca_unemployment_rate", "raw", label="Canada unemployment rate (national)"),
            ),
        ),
        # Wave 5 add: EI Regular Beneficiaries (Labour Panel 7). Single-series
        # line chart with level / Y/Y / MoM toggles handled chart-side. The
        # raw level is in persons; chart-builder divides by 1000 for default
        # "thousands" display per Wave 5 brief (Section 5 backend item 1).
        PanelSpec(
            panel_id="panel-7", section="labour", panel_num=7,
            file="labour/Panel7EIBeneficiaries.astro",
            primary=SlotSpec("ei_regular_beneficiaries", "raw",
                             label="EI regular beneficiaries (persons)"),
            expected_status="WIRED",
            notes=(
                "Wave 5 canon: cyclical-inflection signal (demand-side mirror "
                "of LFS unemployment). StatCan Table 14-10-0011 v64549350, "
                "Canada total SA monthly. Chart-side: divide by 1000 for "
                "default thousands display; Y/Y and MoM toggles applied at "
                "render time. Peak-to-trough annotation supplied by researcher."
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
            panel_id="panel-4", section="housing", panel_num=4,
            file="housing/Panel4Rent.astro",
            primary=SlotSpec("cpi_rent_yoy", "processed", label="CPI rent Y/Y"),
            secondary=SlotSpec("cpi_rented_accommodation_yoy", "processed", label="CPI rented accommodation Y/Y"),
            expected_status="NEAR",
            notes="Panel expects CPI rent + CMHC RMS annual rent growth. RMS annual is MISSING (CMHC publishes annually; needs separate fetcher).",
        ),
        PanelSpec(
            panel_id="panel-5", section="housing", panel_num=5,
            file="housing/Panel5MortgageStack.astro",
            primary=SlotSpec("mortgage_rate_5yr", "raw", label="5yr conventional mortgage rate"),
            expected_status="NEAR",
            notes="Renewal-wall bucket shares + 90+ day delinquency rate are MISSING (BoC / CMHC; data licensing needs check). Chart can render the rate level alone in v1.",
        ),
        PanelSpec(
            panel_id="panel-6", section="housing", panel_num=6,
            file="housing/Panel6PopulationStock.astro",
            primary=SlotSpec("pop_immigrants", "raw", label="Immigrants flow proxy"),
            secondary=SlotSpec("housing_starts", "raw", label="Housing starts (stock additions)"),
            expected_status="NEAR",
            notes="Panel expects persons-per-housing-unit ratios by CMA. Both numerator (population by CMA) and denominator (housing stock by CMA) are MISSING for cross-CMA comparison. pop_cma_toronto.csv exists in raw/ as a Sibley-fetched stub; full set: MISSING (S/M effort).",
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
    "policy": [
        PanelSpec(
            panel_id="panel-1", section="policy", panel_num=1,
            file="policy/Panel1OvernightRate.astro",
            primary=SlotSpec("overnight_rate", "raw", label="BoC overnight rate target"),
            secondary=SlotSpec("overnight_rate_daily", "raw", label="Daily overnight rate"),
            notes="MPR neutral band (low/high) is editorial; chart-builder takes it as a prop.",
        ),
        PanelSpec(
            panel_id="panel-2", section="policy", panel_num=2,
            file="policy/Panel2MarketPath.astro",
            primary=SlotSpec("yield_2yr", "raw", label="GoC 2-yr yield"),
            secondary=SlotSpec("overnight_rate_daily", "raw", label="Overnight rate"),
        ),
        PanelSpec(
            panel_id="panel-3", section="policy", panel_num=3,
            file="policy/Panel3BoCFedSpread.astro",
            primary=SlotSpec("yield_2yr", "raw", label="Canada 2y"),
            secondary=SlotSpec("us_2yr", "raw", label="US 2y"),
            notes="Spread = Canada 2y - US 2y. Chart-builder joins on date and converts to bp.",
        ),
        PanelSpec(
            panel_id="panel-4", section="policy", panel_num=4,
            file="policy/Panel4BalanceSheet.astro",
            primary=SlotSpec("boc_settlement_balances", "raw", label="Settlement balances"),
            secondary=SlotSpec("boc_total_assets", "raw", label="Total assets"),
            extras=(
                SlotSpec("boc_goc_bonds", "raw", label="GoC bonds"),
                SlotSpec("boc_repos", "raw", label="Repos (asset)"),
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
            panel_id="panel-5", section="policy", panel_num=5,
            file="policy/Panel5FederalTrajectory.astro",
            primary=SlotSpec("dof_fiscal_monthly_balance", "raw", label="Federal monthly balance"),
            secondary=SlotSpec("dof_fiscal_ytd_balance", "raw", label="Federal fiscal-YTD balance"),
            tertiary=SlotSpec("dof_fiscal_ytd_summary", "raw", label="Fiscal Monitor YTD summary"),
            notes="DoF Fiscal Monitor; revenues + debt service indexed to FY19/20 are derivable from the YTD summary across past issues. Multi-issue back-fill: NEAR.",
        ),
        PanelSpec(
            panel_id="panel-6", section="policy", panel_num=6,
            file="policy/Panel6FiscalStanceCycle.astro",
            primary=SlotSpec("capacity_util_total", "raw", label="Output gap proxy"),
            secondary=SlotSpec("dof_fiscal_ytd_summary", "raw", label="Fiscal stance proxy"),
            expected_status="NEAR",
            notes="Panel expects output gap + cyclically-adjusted primary balance (CAPB). True output gap and CAPB are MISSING; capacity-util + Fiscal-Monitor YTD provide a v1 proxy.",
        ),
    ],
    "markets": [
        PanelSpec(
            panel_id="panel-1", section="markets", panel_num=1,
            file="markets/Panel1CAD.astro",
            primary=SlotSpec("usdcad", "raw", label="USDCAD spot"),
            secondary=SlotSpec("fxusdcad", "raw", label="USDCAD spot (BoC)"),
            expected_status="NEAR",
            notes="Panel expects BoC CEER index. CEER is MISSING (BoC Valet, key TBD; pipeline.build_financial may fetch in daily run).",
        ),
        PanelSpec(
            panel_id="panel-2", section="markets", panel_num=2,
            file="markets/Panel2GoCCurve.astro",
            primary=SlotSpec("yield_2yr", "raw", label="GoC 2y"),
            secondary=SlotSpec("yield_5yr", "raw", label="GoC 5y"),
            tertiary=SlotSpec("yield_10yr", "raw", label="GoC 10y"),
            extras=(
                SlotSpec("yield_30yr", "raw", label="GoC 30y"),
            ),
        ),
        PanelSpec(
            panel_id="panel-3", section="markets", panel_num=3,
            file="markets/Panel3CreditSpreads.astro",
            primary=SlotSpec("yield_10yr", "raw", label="GoC 10y (proxy denominator)"),
            expected_status="MISSING",
            notes="Panel expects IG OAS bp and HY OAS bp (Canada IG/HY indices). Both MISSING -- need FTSE Canada Universe Corporate OAS or ICE BofA Canada series (licensed; M/L effort). FRED publishes US BAMLC0A0CM and BAMLH0A0HYM2 OAS daily; could proxy as v1 fallback (M).",
        ),
        PanelSpec(
            panel_id="panel-4", section="markets", panel_num=4,
            file="markets/Panel4Energy.astro",
            primary=SlotSpec("wti", "raw", label="WTI"),
            secondary=SlotSpec("brent", "raw", label="Brent"),
            tertiary=SlotSpec("wcs", "raw", label="WCS"),
            extras=(
                SlotSpec("natural_gas_alberta", "raw", label="AECO natural gas (Alberta reference)"),
            ),
        ),
        PanelSpec(
            panel_id="panel-5", section="markets", panel_num=5,
            file="markets/Panel5BankStability.astro",
            primary=SlotSpec("boc_settlement_balances", "raw", label="Settlement balances (system liquidity proxy)"),
            expected_status="MISSING",
            notes="Panel expects Big-Six PCL build and avg CET1 ratio (quarterly bank earnings). Both MISSING -- need OSFI / per-bank disclosure or manual fixture (M/L).",
        ),
        PanelSpec(
            panel_id="panel-6", section="markets", panel_num=6,
            file="markets/Panel6FCI.astro",
            primary=SlotSpec("yield_10yr", "raw", label="GoC 10y (proxy for FCI)"),
            secondary=SlotSpec("usdcad", "raw", label="USDCAD spot"),
            expected_status="MISSING",
            notes="Panel expects a standardized FCI (BoC FCI or Chicago Fed NFCI). BoC FCI: MISSING (Valet may publish; key TBD). Chicago NFCI: available via FRED (NFCI series) -- S effort to add.",
        ),
    ],
    "trade": [
        PanelSpec(
            panel_id="panel-1", section="trade", panel_num=1,
            file="trade/Panel1TradeBalance.astro",
            primary=SlotSpec("trade_balance_total", "raw", label="Trade balance, all countries"),
            secondary=SlotSpec("trade_balance_total_3m_ma", "processed", label="3mma"),
            tertiary=SlotSpec("trade_balance_us", "raw", label="Trade balance with US"),
        ),
        PanelSpec(
            panel_id="panel-2", section="trade", panel_num=2,
            file="trade/Panel2CurrentAccount.astro",
            primary=SlotSpec("current_account_balance", "raw", label="Current account balance (headline)"),
            secondary=SlotSpec("ca_goods_balance_q", "raw", label="Goods balance"),
            tertiary=SlotSpec("ca_services_balance_q", "raw", label="Services balance"),
            extras=(
                SlotSpec("ca_primary_income_q", "raw", label="Primary income balance"),
                SlotSpec("ca_secondary_income_q", "raw", label="Secondary income balance"),
                SlotSpec("current_account_components_sum", "processed", label="Components sum (reconciliation)"),
            ),
            expected_status="WIRED",
            notes=(
                "Quarterly SA from StatCan Table 36-10-0018. Headline + four "
                "sub-component balances support the stacked-bar decomposition. "
                "Annual companions ca_*_income (Table 36-10-0014) remain on disk "
                "if a longer back-history is needed."
            ),
        ),
        PanelSpec(
            panel_id="panel-3", section="trade", panel_num=3,
            file="trade/Panel3PartnerShares.astro",
            primary=SlotSpec("trade_exports_total", "raw", label="Exports, all countries"),
            secondary=SlotSpec("trade_exports_us", "raw", label="Exports to US"),
            expected_status="NEAR",
            notes="Panel expects shares to US/China/UK/Japan/Mexico. Only trade_exports_us is on disk in raw/; per-partner (china/uk/japan/mexico) MISSING. StatCan Table 12-10-0119 has the vectors; S effort to add 4 vectors to catalog.",
        ),
        PanelSpec(
            panel_id="panel-4", section="trade", panel_num=4,
            file="trade/Panel4TariffState.astro",
            primary=None,
            expected_status="MISSING",
            notes="Tariff state is editorial / written content, not a time series. Chart accepts a `rows` prop authored by researcher. No backend data needed; backend may emit a static JSON fixture later.",
        ),
        PanelSpec(
            panel_id="panel-5", section="trade", panel_num=5,
            file="trade/Panel5TermsOfTrade.astro",
            primary=SlotSpec("terms_of_trade", "processed", label="Terms of trade (national-accounts ratio)"),
            secondary=SlotSpec("terms_of_trade_yoy", "processed", label="ToT Y/Y %"),
            tertiary=SlotSpec("tot_exports_ipi", "raw", label="Exports IPI"),
            extras=(
                SlotSpec("tot_imports_ipi", "raw", label="Imports IPI"),
                SlotSpec("wti", "raw", label="WTI (commodity ToT cross-check)"),
            ),
            expected_status="WIRED",
            notes=(
                "ToT = exports IPI / imports IPI x 100, derived in "
                "pipeline.build.derive_terms_of_trade from StatCan Table 36-10-0106 "
                "(GDP price indexes, quarterly SA). WTI kept as a commodity-ToT "
                "cross-check overlay."
            ),
        ),
        PanelSpec(
            panel_id="panel-6", section="trade", panel_num=6,
            file="trade/Panel6FDIBySector.astro",
            primary=None,
            expected_status="MISSING",
            notes="FDI inward/outward by sector is annual, multi-sector. Source: StatCan Table 36-10-0008. MISSING from catalog. M effort (one quarterly table, multiple coordinates).",
        ),
    ],
}


# --------------------------------------------------------------------------- #
# Disk readers
# --------------------------------------------------------------------------- #

def _read_slot(slot: SlotSpec, data_root: Path) -> Optional[dict]:
    """Read one slot's CSV (with .meta.json) and return the per-panel payload.

    Returns None if the CSV is not on disk in any of the three tiers.
    """
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
    """
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
                if pd.isna(fv):
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


def build_all_panel_data(
    data_root: Path = DATA_ROOT,
    out_dir: Optional[Path] = None,
) -> dict[str, Path]:
    """Emit one panel-data JSON per section.

    Returns: section -> written path.
    """
    data_root = Path(data_root)
    if out_dir is None:
        out_dir = data_root / "site" / "panel_data"
    out_dir.mkdir(parents=True, exist_ok=True)
    written: dict[str, Path] = {}
    for section in PANEL_SPECS:
        payload = build_section_payload(section, data_root)
        out_path = out_dir / f"{section}.json"
        out_path.write_text(json.dumps(payload, indent=2, sort_keys=False), encoding="utf-8")
        written[section] = out_path
        logger.info("panel_data: wrote %s (%d panels)", out_path, len(payload["panels"]))
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
    sys.exit(main())
