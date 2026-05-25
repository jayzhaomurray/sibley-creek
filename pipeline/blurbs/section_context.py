"""Per-section research-context seeds for the auto-blurb pipeline.

The researcher agent is dispatched once per release-cycle and needs to
know what data sources, primary series, plates, and known facts the
section operates against. The `.claude/commands/auto-blurb-researcher.md`
prompt template is intentionally section-agnostic; this module is the
seam where section-specific context is injected at fan-out time.

Each section has one canonical release-key today (CPI -> inflation,
LFS -> labour, etc). If the editorial scope grows to multiple
release-keys per section (e.g. a separate `cpi_core_only` mini-cycle),
register the secondary keys in `registry.py` and extend
`section_to_release_key`.

The `SectionContext` object carries:

- `section_slug` -- matches `data/site/panel_data/<slug>.json`
- `release_key` -- the registry's canonical release-key for this section
- `label` -- human-friendly section name for inbox / email subjects
- `primary_series` -- the headline indicator(s) the researcher should
  open the cycle with
- `canonical_sources` -- a brief notes block describing where the
  primary numbers come from (Statistics Canada table, BoC press
  release URL pattern, etc). Verbatim from `data/SOURCES.md` where
  possible.
- `quirks` -- short notes on the release's quirks (revision pattern,
  publication cadence, common pitfalls).
- `plate_inventory` -- ordered tuple of `(plate_id, plate_label,
  chart_key, indicator)` mirroring the live `src/pages/<slug>.astro`
  plates. The fan-out walks this when generating per-plate surfaces.

Used by:
  - `registry.py` to enumerate plate surfaces.
  - `run.py` to resolve `--section` to a release-key.
  - The researcher dispatch (production wiring) to seed the prompt
    with section-specific facts before the LLM is invoked.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class PlateEntry:
    """One plate on a section page -> one plate-interpretation surface."""

    plate_id: str           # e.g. "plate-1" (matches astro file id)
    surface_slug: str       # kebab-case for filesystem paths
    label: str              # short human label for inbox / logs
    chart_key: str          # matches the astro chartKey
    indicator: str          # one-line description of what the plate shows


@dataclass(frozen=True)
class SectionContext:
    """One section's research-context seed."""

    section_slug: str
    release_key: str
    label: str
    primary_series: tuple[str, ...]
    canonical_sources: str
    quirks: str
    plate_inventory: tuple[PlateEntry, ...]
    series_inputs: tuple[str, ...] = field(default_factory=tuple)
    primary_meta_files: tuple[str, ...] = field(default_factory=tuple)


# ---------------------------------------------------------------------------
# Section -> context map
# ---------------------------------------------------------------------------
#
# The plate inventories below mirror the live pages at
# `src/pages/<slug>.astro` as of 2026-05-12. When a section page gains or
# loses a plate, update here -- the registry surfaces and run-time dry-
# run output will follow.

SECTION_CONTEXTS: dict[str, SectionContext] = {
    "inflation": SectionContext(
        section_slug="inflation",
        release_key="cpi_monthly",
        label="Inflation",
        primary_series=(
            "cpi_all_items_yoy",
            "cpi_all_items_nsa_yoy",
            "cpi_trim_yoy",
            "cpi_median_yoy",
        ),
        canonical_sources=(
            "Statistics Canada Table 18-10-0004-01 (CPI, monthly, all-items "
            "SA Y/Y, NSA Y/Y); BoC core-trim and core-median preferred-core "
            "measures via the Valet API."
        ),
        quirks=(
            "CPI lands ~3 weeks after the reference month. NSA Y/Y is the "
            "BoC's published headline; SA Y/Y is for momentum reads. Both "
            "are reported."
        ),
        plate_inventory=(
            PlateEntry("plate-1", "panel-1-headline-cpi",
                       "Headline CPI",
                       "inflation-panel-1",
                       "Headline CPI, m/m and Y/Y"),
            PlateEntry("plate-2", "panel-2-core-measures",
                       "Core measures",
                       "inflation-panel-2",
                       "Core-trim and core-median, Y/Y"),
            PlateEntry("plate-3", "panel-3-breadth",
                       "Breadth",
                       "inflation-panel-3",
                       "Share of CPI basket above 3% Y/Y"),
            PlateEntry("plate-4", "panel-4-subaggregates",
                       "Sub-aggregates",
                       "inflation-panel-4",
                       "Shelter, services, goods, food, energy, Y/Y"),
        ),
        series_inputs=(
            "cpi_all_items_yoy",
            "cpi_all_items_nsa_yoy",
            "cpi_trim_yoy",
            "cpi_median_yoy",
            "cpi_common_yoy",
            "cpi_shelter_yoy",
            "cpi_goods_yoy",
            "cpi_services_yoy",
            "cpi_food_yoy",
            "cpi_energy_yoy",
            "cpi_mortgage_interest_yoy",
        ),
        primary_meta_files=(
            "data/processed/cpi_all_items_yoy.meta.json",
            "data/processed/cpi_all_items_nsa_yoy.meta.json",
        ),
    ),
    "labour": SectionContext(
        section_slug="labour",
        release_key="lfs_monthly",
        label="Labour",
        primary_series=(
            "employment_level",
            "unemployment_rate",
        ),
        canonical_sources=(
            "Statistics Canada Table 14-10-0287-01 (LFS: employment level, "
            "unemployment rate, participation rate, SA monthly). Table "
            "14-10-0064-01 (LFS hourly wages). BoC LFS-Micro composition-"
            "adjusted wage series. Table 14-10-0432-01 (JVWS vacancy "
            "rate). Table 14-10-0011-01 (EI regular beneficiaries)."
        ),
        quirks=(
            "LFS lands the first Friday of the following month. Headline "
            "m/m employment is in thousands of persons (chart-wrapper "
            "derived). Wage growth has two flavours: LFS-all (headline) "
            "vs BoC LFS-Micro (composition-adjusted) -- the gap is the "
            "Bank's preferred read. JVWS is two months lagged. EI "
            "beneficiaries (deflated by labour-force-ex-NPRs) is the "
            "leading caseload indicator."
        ),
        plate_inventory=(
            PlateEntry("plate-1", "panel-1-headline-jobs",
                       "Headline jobs print",
                       "labour-panel-1",
                       "Monthly job change and the unemployment rate"),
            PlateEntry("plate-2", "panel-2-stocks",
                       "Labour-force stocks",
                       "labour-panel-2",
                       "Employed, unemployed, not-in-labour-force"),
            PlateEntry("plate-3", "panel-3-wage-band",
                       "Wage band",
                       "labour-panel-3",
                       "Composition-adjusted vs headline wage growth"),
            PlateEntry("plate-4a", "panel-4a-vacancies-slack",
                       "Vacancies and slack",
                       "labour-panel-4-levels",
                       "Vacancy and unemployment rate, plus spread"),
            PlateEntry("plate-4b", "panel-4b-beveridge",
                       "Beveridge curve",
                       "labour-panel-4",
                       "Vacancy rate vs unemployment rate, time-path"),
            PlateEntry("plate-4c", "panel-4c-flow-rates",
                       "Flow rates",
                       "labour-panel-flow-rates",
                       "Job finding and separation rates"),
            PlateEntry("plate-5", "panel-5-supply",
                       "Supply trajectory",
                       "labour-panel-5",
                       "PR landings and net NPR vs IRCC plan"),
            PlateEntry("plate-6", "panel-6-regional",
                       "Regional dispersion",
                       "labour-panel-6",
                       "Provincial UR gap to national rate"),
            PlateEntry("plate-7", "panel-7-ei",
                       "EI beneficiaries",
                       "labour-panel-7",
                       "EI claimants per 1k labour-force-ex-NPRs"),
            PlateEntry("plate-8", "panel-8-hours",
                       "Hours vs headcount",
                       "labour-panel-8",
                       "Aggregate hours worked vs employment, Y/Y"),
        ),
        series_inputs=(
            "employment_level",
            "unemployment_rate",
            "participation_rate",
            "labour_force_ex_npr",
        ),
        primary_meta_files=(
            "data/processed/labour_force_ex_npr.meta.json",
        ),
    ),
    "gdp": SectionContext(
        section_slug="gdp",
        release_key="gdp_monthly",
        label="GDP",
        primary_series=(
            "gdp_monthly_yoy",
            "gdp_per_capita_yoy",
        ),
        canonical_sources=(
            "Statistics Canada Table 36-10-0434-01 (Monthly GDP by "
            "industry, chained 2017 dollars). Table 36-10-0104-01 "
            "(Quarterly GDP, expenditure-based, SAAR). BoC MPR output "
            "gap series. Productivity from Table 36-10-0480-01."
        ),
        quirks=(
            "Monthly GDP is two months lagged; the second-month flash "
            "estimate is released with the prior month's hard print. "
            "Quarterly GDP is SAAR Q/Q by convention. The first-cut "
            "industry vintage gets revised meaningfully one month later."
        ),
        plate_inventory=(
            PlateEntry("plate-1", "panel-1-headline-gdp",
                       "Headline GDP",
                       "gdp-panel-1",
                       "Headline real GDP, m/m and Y/Y"),
            PlateEntry("plate-2", "panel-2-contributions",
                       "Contributions",
                       "gdp-panel-2",
                       "Contributions to quarterly growth, by bucket"),
            PlateEntry("plate-3", "panel-3-industry-split",
                       "Industry split",
                       "gdp-panel-3",
                       "Real GDP by industry, services vs goods, Y/Y"),
            PlateEntry("plate-4", "panel-4-cyclical-drivers",
                       "Cyclical drivers",
                       "gdp-panel-4",
                       "Manufacturing vs mining and oil, indexed"),
            PlateEntry("plate-5", "panel-5-output-gap",
                       "Output gap",
                       "gdp-panel-5",
                       "BoC MPR output gap"),
            PlateEntry("plate-6", "panel-6-per-capita",
                       "Per capita",
                       "gdp-panel-6",
                       "Total vs per-capita real GDP, indexed"),
        ),
        series_inputs=(
            "gdp_monthly_yoy",
            "gdp_per_capita_yoy",
            "productivity_business_per_hour_yoy",
        ),
        primary_meta_files=(
            "data/processed/gdp_monthly_yoy.meta.json",
            "data/processed/gdp_per_capita_yoy.meta.json",
        ),
    ),
    "housing": SectionContext(
        section_slug="housing",
        release_key="crea_monthly",
        label="Housing",
        primary_series=(
            "crea_hpi_canada_yoy",
            "crea_hpi_canada_6m_ar",
        ),
        canonical_sources=(
            "CREA Stats (national + CMA HPI, sales, new listings, sales-"
            "to-new-listings ratio). CMHC SCSS for starts. Statistics "
            "Canada Table 34-10-0066-01 (residential building permits). "
            "CPI rent + rented accommodation via StatCan Table "
            "18-10-0004-01. BoC qualifying-mortgage-payment-to-income "
            "from the BoC Indicators of Financial Vulnerabilities. "
            "5-year conventional mortgage rate from BoC Valet."
        ),
        quirks=(
            "CREA lands mid-month for the prior month. The 6-month "
            "annualized HPI is the BoC-preferred momentum read; Y/Y "
            "lags actual price action by 4-6 months in this cycle. "
            "Starts are SAAR; m/m is volatile (multiples drive it). "
            "Affordability ratio is BoC quarterly with a one-quarter lag."
        ),
        plate_inventory=(
            PlateEntry("plate-1", "panel-1-mls-hpi",
                       "MLS HPI",
                       "housing-panel-1",
                       "MLS HPI, national + six CMAs, Y/Y"),
            PlateEntry("plate-2", "panel-2-activity",
                       "Activity",
                       "housing-panel-2",
                       "Starts, units under construction, permits"),
            PlateEntry("plate-3", "panel-3-inventory",
                       "Inventory",
                       "housing-panel-3",
                       "Sales-to-new-listings ratio, Canada"),
            PlateEntry("plate-4", "panel-4-rent",
                       "Rent",
                       "housing-panel-4",
                       "CPI rent and rented accommodation, Y/Y"),
            PlateEntry("plate-5", "panel-5-mortgage-stack",
                       "Mortgage stack",
                       "housing-panel-5",
                       "5-year conventional mortgage rate"),
            PlateEntry("plate-6", "panel-6-supply-ratio",
                       "Supply ratio",
                       "housing-panel-6",
                       "Immigrant flow proxy and housing starts"),
            PlateEntry("plate-7", "panel-7-affordability",
                       "Affordability",
                       "housing-panel-7",
                       "BoC qualifying mortgage payment to income"),
        ),
        series_inputs=(
            "crea_hpi_canada_yoy",
            "crea_hpi_canada_6m_ar",
            "crea_hpi_toronto_yoy",
            "crea_hpi_vancouver_yoy",
            "crea_hpi_calgary_yoy",
            "crea_hpi_montreal_yoy",
            "crea_hpi_ottawa_yoy",
            "crea_hpi_edmonton_yoy",
            "cpi_rent_yoy",
            "cpi_rented_accommodation_yoy",
        ),
        primary_meta_files=(
            "data/processed/crea_hpi_canada_yoy.meta.json",
        ),
    ),
    "markets": SectionContext(
        section_slug="markets",
        release_key="markets_daily",
        label="Markets",
        primary_series=(
            "usdcad",
            "yield_2yr",
        ),
        canonical_sources=(
            "BoC Valet for daily FX (USDCAD), GoC nominal yield curve "
            "(2y/5y/10y/30y), CORRA, and BoC settlement balances. "
            "TSX composite + WTI from FRED. Corporate credit spreads "
            "are BoC-derived from market data. Financial conditions "
            "is a composite indicator (BoC FCI or a derived proxy)."
        ),
        quirks=(
            "Markets are daily-close. The pipeline runs after NYSE/TSX "
            "close. USDCAD is BoC noon-equivalent (closing rate). The "
            "BoC-Fed 2y spread shares a series with the policy section's "
            "plate-3 (cross-section ripple). Cross-asset / FCI rebuilds "
            "from constituent series and may lag a session if any input "
            "is stale."
        ),
        plate_inventory=(
            PlateEntry("plate-1", "panel-1-usdcad",
                       "USDCAD",
                       "markets-panel-1",
                       "USDCAD spot"),
            PlateEntry("plate-2", "panel-2-yields",
                       "Yields",
                       "markets-panel-2",
                       "GoC yield curve"),
            PlateEntry("plate-3", "panel-3-credit-spreads",
                       "Credit spreads",
                       "markets-panel-3",
                       "Canadian corporate credit spreads"),
            PlateEntry("plate-4", "panel-4-oil",
                       "Oil",
                       "markets-panel-4",
                       "WTI, Brent, and WCS oil prices"),
            PlateEntry("plate-5", "panel-5-settlement-balances",
                       "Settlement balances",
                       "markets-panel-5",
                       "BoC settlement balances"),
            PlateEntry("plate-6", "panel-6-financial-conditions",
                       "Financial conditions",
                       "markets-panel-6",
                       "Financial conditions index"),
        ),
        series_inputs=(
            "usdcad",
            "yield_2yr",
            "yield_10yr",
            "goc_ust_spread_2y",
            "goc_ust_spread_10y",
            "wti",
            "boc_settlement_balances",
            "corra_overnight_spread_bps",
        ),
        primary_meta_files=(
            # Markets-daily does not have a single canonical meta sidecar
            # today; the data refresh runs daily and we treat each CLI
            # invocation as a release assertion. The detect_release_landed
            # helper falls back to the system date when no sidecar
            # reports a release_date.
        ),
    ),
    "monetary": SectionContext(
        section_slug="monetary",
        release_key="boc_decision",
        label="Monetary",
        primary_series=(
            "overnight_rate_target",
            "yield_2yr",
        ),
        canonical_sources=(
            "BoC FAD press releases (overnight rate target), BoC MPR "
            "(forecasts, output gap), BoC Valet for daily yields and "
            "settlement balances. Department of Finance Fiscal Monitor "
            "for monthly federal balance. Statistics Canada Table "
            "36-10-0207-01 (industrial capacity utilization)."
        ),
        quirks=(
            "Eight scheduled BoC decisions per year (roughly Q1: Jan/Mar, "
            "Q2: Apr/Jun, Q3: Jul/Sep, Q4: Oct/Dec). MPR lands on alternate "
            "decisions (Jan, Apr, Jul, Oct). The fiscal monitor is two "
            "months lagged. The BoC-Fed 2y spread shares the underlying "
            "series with markets section plate-3."
        ),
        plate_inventory=(
            PlateEntry("plate-1", "panel-1-overnight-rate",
                       "Overnight rate",
                       "policy-panel-1",
                       "Overnight rate"),
            PlateEntry("plate-2", "panel-2-market-path",
                       "Market path",
                       "policy-panel-2",
                       "2y GoC vs overnight"),
            PlateEntry("plate-3", "panel-3-boc-fed-spread",
                       "BoC-Fed spread",
                       "policy-panel-3",
                       "Canada 2y minus US 2y"),
            PlateEntry("plate-4", "panel-4-balance-sheet",
                       "Balance sheet",
                       "policy-panel-4",
                       "Settlement balances and assets"),
            PlateEntry("plate-5", "panel-5-liability-composition",
                       "Liability composition",
                       "policy-panel-5",
                       "BoC liability composition"),
            PlateEntry("plate-6", "panel-6-federal-trajectory",
                       "Federal trajectory",
                       "policy-panel-6",
                       "Federal deficit YTD and debt charges"),
            PlateEntry("plate-7", "panel-7-policy-divergence",
                       "Policy divergence",
                       "policy-panel-7",
                       "BoC and Fed policy paths over time"),
        ),
        series_inputs=(
            "overnight_rate_target",
            "yield_2yr",
            "goc_ust_spread_2y",
            "boc_settlement_balances",
            "federal_budget_ytd",
        ),
        primary_meta_files=(
            "data/processed/overnight_rate_target.meta.json",
        ),
    ),
    "trade": SectionContext(
        section_slug="trade",
        release_key="trade_monthly",
        label="Trade",
        primary_series=(
            "trade_balance_total_3m_ma",
            "current_account_components_sum",
        ),
        canonical_sources=(
            "Statistics Canada Table 12-10-0011-01 (International "
            "merchandise trade, monthly customs basis), Table "
            "36-10-0014-01 (Balance of international payments, current "
            "account). US tariff state from CBP / USTR proclamations. "
            "Terms of trade from Table 36-10-0125-01."
        ),
        quirks=(
            "Trade balance lands roughly six weeks after the reference "
            "month. Monthly is volatile; the 3-month moving average is "
            "the cleaner cyclical read. Current account is quarterly. "
            "US export-share is a derivation from country-pair flow "
            "data."
        ),
        plate_inventory=(
            PlateEntry("plate-1", "panel-1-balance",
                       "Trade balance",
                       "trade-panel-1",
                       "Goods trade balance, monthly + 3mma"),
            PlateEntry("plate-2", "panel-2-current-account",
                       "Current account",
                       "trade-panel-2",
                       "Goods, services, primary income"),
            PlateEntry("plate-3", "panel-3-us-share",
                       "US share",
                       "trade-panel-3",
                       "US export share of total goods exports"),
            PlateEntry("plate-4", "panel-4-tariff-state",
                       "Tariff state",
                       "trade-panel-4",
                       "US trade actions affecting Canada"),
            PlateEntry("plate-5", "panel-5-terms-of-trade",
                       "Terms of trade",
                       "trade-panel-5",
                       "Terms of trade, national accounts"),
            PlateEntry("plate-6", "panel-6-fdi",
                       "FDI",
                       "trade-panel-6",
                       "FDI by sector: inward and outward"),
        ),
        series_inputs=(
            "trade_balance_total_3m_ma",
            "current_account_components_sum",
            "trade_exports_share_us",
            "trade_exports_share_china",
            "trade_exports_share_uk",
            "trade_exports_share_mexico",
            "terms_of_trade",
            "terms_of_trade_yoy",
        ),
        primary_meta_files=(
            "data/processed/trade_balance_total_3m_ma.meta.json",
        ),
    ),
}


# ---------------------------------------------------------------------------
# Lookup helpers
# ---------------------------------------------------------------------------

def get_section_context(section_slug: str) -> SectionContext:
    """Look up a section's context block; raise KeyError with the list."""
    if section_slug not in SECTION_CONTEXTS:
        raise KeyError(
            f"Unknown section {section_slug!r}; known sections: "
            f"{sorted(SECTION_CONTEXTS)}"
        )
    return SECTION_CONTEXTS[section_slug]


def section_to_release_key(section_slug: str) -> str:
    """Return the canonical release-key for a section.

    Convention: one release-key per section. If a section ever needs
    multiple (e.g. a CPI-only mini-cycle vs the full inflation cycle),
    extend the registry directly and route via `--release-id` rather
    than `--section`.
    """
    return get_section_context(section_slug).release_key


def render_researcher_context_block(section_slug: str) -> str:
    """Render the section-context block injected into the researcher prompt.

    The `.claude/commands/auto-blurb-researcher.md` template is section-
    agnostic; the orchestrator passes the rendered output of this
    function as a section-context preamble at fan-out time. Researcher
    consumes this together with the registry's release-key spec.

    Output is plain Markdown with stable section headers so a prompt
    composer can wedge it under a `## Section context` heading.
    """
    ctx = get_section_context(section_slug)
    plates = "\n".join(
        f"- `{p.plate_id}` ({p.surface_slug}): {p.indicator}"
        for p in ctx.plate_inventory
    )
    primary_series = ", ".join(f"`{s}`" for s in ctx.primary_series)
    series_inputs = ", ".join(f"`{s}`" for s in ctx.series_inputs) or "(none)"
    return (
        f"### Section: {ctx.label} (slug `{ctx.section_slug}`)\n\n"
        f"**Release-key:** `{ctx.release_key}`\n\n"
        f"**Primary series:** {primary_series}\n\n"
        f"**Canonical sources:**\n{ctx.canonical_sources}\n\n"
        f"**Release quirks:**\n{ctx.quirks}\n\n"
        f"**Section plates (this release fans out one interpretation "
        f"surface per plate):**\n{plates}\n\n"
        f"**Series the researcher should load for context:** "
        f"{series_inputs}\n"
    )
