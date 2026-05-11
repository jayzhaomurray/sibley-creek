# boc-tracker Chart Inventory and Sibley Creek Coverage Mapping

Researcher pass for the coverage-parity workstream. Source of truth for
"what boc-tracker tracks" so Sibley Creek can hit indicator parity
without inheriting the visual treatment. Read-only on boc-tracker.

Author: researcher. 2026-05-11.

## What this is

A chart-by-chart inventory across every boc-tracker HTML page, with a
proposed Sibley Creek mapping (already exists / needs adapt / new panel /
new section / skip) for each chart. The mapping is editorial proposal —
final landing decisions are editorial-director's.

The user direction is **coverage parity, not visual replication**.
Every indicator boc-tracker surfaces should also appear on Sibley Creek;
how it looks stays on the Vignelli canon governed by the Sibley
component library.

## Methodology

1. Enumerated the nine boc-tracker HTML pages: `index.html`, `gdp.html`,
   `inflation.html`, `labour.html`, `housing.html`, `policy.html`,
   `financial.html`, `trade.html`, `demographics.html`. (The `v2/`
   directory was inspected separately — see Appendix A. v2 is a UI
   redesign mock, not an indicator superset.)
2. Each page's chart count was confirmed by counting `<div id="chart-N">`
   anchors in the rendered HTML.
3. Chart subjects, series bindings, transforms, and footnotes were
   extracted from `build.py`'s `PAGES` definition (lines 2984-3837) —
   the load-bearing source of truth. Each page's chart list in `build.py`
   is rendered in order into the page's `<div id="chart-N">` slots.
4. Sibley side: matched against the panel canon enumerated in
   `editorial/dashboard_purpose.md` Section 4 and the Astro components
   under `src/components/charts/<section>/Panel<N>*.astro`.
5. v2 React mocks under `boc-tracker/v2/` were diffed against v1; v2 does
   not add new indicator subjects. The Sibley adoption recommendation
   is to follow v1 (build.py PAGES) as the indicator-set ground truth.

## Inventory

Columns: page | chart # | subject (1-line) | data series (CSV
filename or derived) | chart type | special treatment | Sibley
mapping.

Chart numbering is the on-page render order (0-indexed in HTML; this
inventory uses 1-indexed for human readability — chart-0 = #1 here).

### index.html (homepage, 5 charts)

| # | Subject | Data series | Type | Special treatment | Sibley mapping |
|---|---|---|---|---|---|
| 1 | Policy Rates (BoC vs Fed, with BoC-Fed spread toggle) | overnight_rate, fed_funds, bocfed_spread (derived) | Step line, multi-series, dual-axis | Neutral band shade 2.25-3.25%; secondary-axis spread toggle | policy/Panel1OvernightRate + policy/Panel3BoCFedSpread together cover this. Sibley homepage tile will be a thumbnail of Panel1OvernightRate. **already exists** (split across two Sibley panels by design) |
| 2 | Core Inflation band (trim/median/common/CPIX/CPIXFET) + headline | cpi_trim, cpi_median, cpi_common, cpix, cpixfet, cpi_all_items (derived Y/Y) | Band envelope + comparator line | 2% reference rule; Y/Y; 10y window | inflation/Panel2CoreTrio — **already exists** (Sibley canon retires common to footnote per Section 4.2; trim/median lead) |
| 3 | Real GDP level + HP-filter potential | gdp_monthly, gdp_potential_hp (derived) | Two-line level chart | HP-filter trend overlay (lambda=129600); C$ trillions SAAR | gdp/Panel5OutputGap covers the gap-from-potential read; gdp/Panel1HeadlineGDP covers the level. **already exists** (level in Panel1, gap in Panel5 — Sibley uses BoC MPR potential per Section 4.1, not HP-filter; that's an editorial methodology upgrade, not a coverage gap) |
| 4 | Unemployment rate + Job vacancies rate (12M MA) | unemployment_rate, job_vacancy_rate_12m (derived), job_vacancy_rate, with alt-views unemployment_level, job_vacancy_level | Dual-axis multi-line; rate/level toggle | 12M MA smoothing on vacancies; rate-vs-level toggle on entire chart | labour/Panel1LFSHeadline (unemployment) + labour/Panel4VacanciesSlack (V/U) together — **already exists** (vacancies live in Panel4 per Section 4.3) |
| 5 | Wage Growth band (LFS-Micro featured + LFS all + LFS perm + SEPH) vs services CPI | lfs_micro, lfs_wages_all_yoy, lfs_wages_permanent_yoy, seph_earnings_yoy (all Y/Y derived), cpi_services_yoy (comparator) | Band envelope + featured line + comparator | 0% reference; featured-line emphasis on LFS-Micro; services-CPI dashed | labour/Panel3WageBand — **already exists** (canon spec matches exactly: four-measure band + CPI services comparator) |

### gdp.html (6 charts)

| # | Subject | Data series | Type | Special treatment | Sibley mapping |
|---|---|---|---|---|---|
| 1 | Real GDP level + HP potential | gdp_monthly, gdp_potential_hp (derived) | Two-line level | HP filter overlay | gdp/Panel1HeadlineGDP + gdp/Panel5OutputGap — **already exists** (duplicate of index.html #3) |
| 2 | Output Gap, HP-filter estimate | gdp_monthly (derived gap series via custom builder) | Filled area, single-series | Custom native builder (`_build_output_gap_panel`); zero-line reference | gdp/Panel5OutputGap — **needs adapt** (Sibley canon uses BoC MPR `INDINF_OUTGAPMPR_Q` as the benchmark, not HP-filter. Current Panel5 wiring should be confirmed against canon; if it's HP-filter, swap to MPR series) |
| 3 | Productivity Decomposition | (placeholder, no lines wired) | (Coming soon stub) | "[Coming soon]" footnote | gdp/Panel<NEW> or **skip** (boc-tracker shipped this as a stub; Sibley Section 4.1 routes the business-vs-residential / productivity split to Pillar D deep-dive, not basics. Recommend **skip** at basics layer; productivity attribution belongs in the productivity deep-dive workstream) |
| 4 | Industrial Capacity Utilization (total + manufacturing) | capacity_util_total, capacity_util_mfg | Two-line, quarterly | None | gdp/Panel<NEW> — **new panel** (Sibley GDP canon does not include capacity utilization; this is a real omission. Recommend a new Panel7 or merge into Panel5OutputGap as a side reference. **Editorial decision needed**: capacity utilization is a slack-side read that competes with labour's V/U panel; could equally live in Labour/Panel4VacanciesSlack as a secondary track) |
| 5 | Real GDP monthly with overlays (goods, services, mfg, mining/oil) | gdp_monthly, gdp_industry_goods, gdp_industry_services, gdp_industry_manufacturing, gdp_industry_mining_oil | Single-series with toggleable industry overlays | Industry overlay toggle; level/MoM/3M-AR/YoY transform toggle | gdp/Panel2IndustryVsExpenditure — **needs adapt** (Sibley Section 4.1 unit 2 is the "industry vs expenditure cross-check" — boc-tracker shows industry breakdown only; expenditure cross-check is genuinely a Sibley add. boc-tracker's industry-overlay toggle pattern is worth preserving in Panel2) |
| 6 | GDP Growth Contributions (six-bar) | gdp_contrib_consumption, _investment, _govt, _exports, _imports, _inventories, gdp_total_contribution (overlay) | Stacked bar + headline line overlay | Imports sign-flipped; quarterly AR; default 2y window | gdp/Panel3Contributions — **already exists** (canon spec matches: six-bar GFCF decomposition per Section 4.1 unit 3) |

### inflation.html (7 charts)

| # | Subject | Data series | Type | Special treatment | Sibley mapping |
|---|---|---|---|---|---|
| 1 | Headline vs Ex-Indirect-Taxes | cpi_all_items (only; ex-indirect-taxes series not wired) | Multi-line stub | "[Coming soon]" footnote | inflation/Panel1HeadlineCPI — **needs adapt** (Sibley Panel1 ships with Y/Y + 3M AR; the ex-indirect-taxes overlay is an editorial add. Recommend adding ex-indirect-taxes as toggle in Panel1 when StatCan series is wired — methodology-relevant for GST/HST and tariff pass-through reads. **Flag for editorial-director**) |
| 2 | Core Inflation — Individual Measures (trim, median, common, CPIX, CPIXFET) | cpi_trim, cpi_median, cpi_common, cpix, cpixfet | Multi-line (toggleable, only trim visible by default) | None | inflation/Panel2CoreTrio — **already exists** (Sibley canon leads with trim/median, common as footnote; CPIX/CPIXFET legacy measures could be hidden toggles. Substantively covered) |
| 3 | CPI Component Contributions | (placeholder, no lines wired) | (Coming soon stub) | "[Coming soon]" footnote | inflation/Panel<NEW> — **needs adapt** (the 60-component decomposition view. Sibley Section 4.2 has no direct equivalent; Panel4SubAggregates is the closest — it shows shelter / services / goods / food / energy at aggregate level, not 60-component. Recommend keeping at aggregate level for basics-layer; full 60-component decomposition is methodology-page territory) |
| 4 | CPI Components (headline + headline NSA + food + energy + shelter + goods + services) | cpi_all_items, cpi_all_items_nsa, cpi_food, cpi_energy, cpi_shelter, cpi_goods, cpi_services | Multi-line CPI panel with YoY/MoM/3M-AR transform toggle | Custom CpiSpec builder | inflation/Panel4SubAggregates — **already exists** (Sibley canon matches: shelter, services, goods, food, energy. The "ex-" derivations — services ex-shelter, goods ex-energy — are Sibley adds gated on basket-weight reproducibility per Section 4.2 unit 4) |
| 5 | CPI Breadth (share above 3% / below 1%) | (custom CpiBreadthSpec; computed from 60-component CPI table) | Custom breadth panel | Deviation from 1996-2019 average; weighted shares | inflation/Panel3Breadth — **already exists** (Sibley canon: share >3% / 1-3% / <1%. boc-tracker shows >3% and <1% only; Sibley adds the middle bucket. Already adapted in Panel3) |
| 6 | Consumer Inflation Expectations (1y + 5y) | infl_exp_consumer_1y, infl_exp_consumer_5y | Two-line quarterly | None | inflation/Panel5Expectations — **already exists** (canon spec matches: CSCE 1y + 5y) |
| 7 | Business Inflation Expectations (BOS distribution buckets) | bos_dist_below1, bos_dist_1to2, bos_dist_2to3, bos_dist_above3, infl_exp_above3 | Multi-line (four BOS buckets sum to 100%) | None | inflation/Panel5Expectations — **needs adapt** (Sibley Section 4.2 unit 5 says "BOS firms expecting >3% as primary; BOS distribution buckets as secondary view." Panel5 should carry both views with a toggle, or split into Panel5 + Panel<NEW>. Currently Panel5 covers consumer side; BOS coverage needs verification in the .astro file) |

### labour.html (9 charts)

| # | Subject | Data series | Type | Special treatment | Sibley mapping |
|---|---|---|---|---|---|
| 1 | Unemployment by Age (youth + prime + total) | youth_unemployment_rate, prime_age_unemployment_rate, unemployment_rate | Three-line | None | labour/Panel1LFSHeadline + labour/Panel<adapt> — **needs adapt** (Sibley Panel1 is headline U/E/P/EmpRate; the age breakdown is not in canon as a standalone unit. Could land as secondary toggle on Panel1 or as a new sub-panel inside Panel6RegionalDumbbell's analytical neighbourhood. Recommend: youth + prime as a hover/toggle view on Panel1) |
| 2 | Beveridge Curve | unemployment_rate, job_vacancy_rate | Custom phase-space scatter | Native builder; 12-month trail | labour/Panel4VacanciesSlack — **already exists** (Sibley canon Section 4.3 unit 4 explicitly includes "Beveridge-curve scatter with the most recent point highlighted and a 12-month trail." Direct match) |
| 3 | LFS R-Indicators (R3 / R7 / R8) | unemployment_rate (placeholder; R7/R8 not yet wired) | Multi-line stub | "[Coming soon]" footnote | labour/Panel<NEW> or **skip** (Sibley canon does not include R-indicators. Editorial call: R7 and R8 are useful when the U3 headline understates slack; they're not in the panel canon. Recommend **skip** at basics; surface in deep-dive on labour-slack read when needed) |
| 4 | EI Regular Beneficiaries | ei_regular_beneficiaries (display in thousands via _k derived) | Single-series with level/MoM/YoY toggle | None | labour/Panel<NEW> — **new panel** (EI beneficiaries is a real coverage gap. Sibley canon's six-panel set covers stocks/wages/slack/supply/regional but not EI. Recommend either: (a) new Panel7 dedicated to EI, or (b) fold EI as secondary track on Panel4VacanciesSlack — EI uptake is the demand-side mirror of vacancy decline. **Flag for editorial-director** — EI is a leading recession indicator and worth carrying in basics) |
| 5 | Prime-Age Labour Market (participation + employment + unemployment, 25-54) | lf_participation_prime, lf_employment_prime, prime_age_unemployment_rate | Three-line | None | labour/Panel<NEW> or fold into Panel1 — **needs adapt** (Prime-age is the BoC's preferred denominator-adjusted slack read; it sharpens what Panel1 obscures. Recommend: prime-age view as a toggle on Panel1LFSHeadline, OR as a secondary slot on Panel2PerCapita. Currently neither Panel1 nor Panel2's Props interface carries this — confirm) |
| 6 | Youth Labour Market (participation + employment + unemployment, 15-24) | lf_participation_youth, lf_employment_youth, youth_unemployment_rate | Three-line | None | labour/Panel<adapt> — **needs adapt** (Same logic as #5. Recommend: youth as a sibling toggle alongside prime-age on Panel1 — both views available, prime-age default) |
| 7 | Aggregate Participation and Employment (total 15+) | participation_rate, employment_rate | Two-line | None | labour/Panel1LFSHeadline — **already exists** (Sibley Panel1 canon is "employment, unemployment rate, participation, employment rate" — direct match) |
| 8 | Indeed Job Postings Index | job_vacancy_rate (placeholder; Indeed series not wired) | Multi-line stub | "[Coming soon]" footnote | labour/Panel<NEW> or **skip** (Indeed postings is a real-time vacancy proxy useful when JVWS lags by 2-3 months. Sibley canon Section 4.3 unit 4 uses JVWS as primary. Recommend **skip** at basics-layer until/unless JVWS lag becomes an editorial pain point) |
| 9 | Unit Labour Costs | unit_labour_cost | Single-series with level/QoQ/QoQ-AR/YoY toggle | Quarterly | labour/Panel<NEW> — **new panel** (ULC is a productivity-adjusted wage read — wage growth net of productivity. Real coverage gap. Sibley canon does not include ULC. Could land as secondary track on Panel3WageBand — ULC is exactly the "what is the inflation-relevant wage signal" question Panel3 already asks. Recommend: ULC as toggle/overlay on Panel3) |

### housing.html (9 charts)

| # | Subject | Data series | Type | Special treatment | Sibley mapping |
|---|---|---|---|---|---|
| 1 | CREA Sales Activity (SNLR + resales index) | crea_snlr, crea_resales | Two-line | None | housing/Panel3Inventory — **already exists** (Sibley canon Section 4.4 unit 3 is "MLS sales-to-new-listings" plus months of inventory. SNLR direct match; resales index is the volume side) |
| 2 | 5Y Mortgage Rate vs 5Y GoC + spread | mortgage_rate_5yr, yield_5yr, mortgage_5yr_goc_5yr_spread (derived) | Two-line + spread toggle | 4-week smoothing | housing/Panel5MortgageStack — **needs adapt** (Sibley canon Section 4.4 unit 5 is the mortgage-stack snapshot citing BoC chartpack + OSFI + CMHC arrears. The 5Y-vs-5Y-GoC spread is the marginal-borrower cost view, not the stack view. Recommend: 5Y mortgage rate as a panel element on Panel5; the spread is a deep-dive variable for Pillar A. **Flag** — Panel5's current implementation should be audited against what canon describes) |
| 3 | Units Under Construction | units_under_construction | Single-series | None | housing/Panel2Activity — **already exists** (Sibley canon Section 4.4 unit 2 is "starts, completions, permits" — completions and units-under-construction are closely related; Panel2 should carry both. Confirm units-under-construction is included; if not, it's a one-line add) |
| 4 | Resale Activity by CMA (Toronto + Vancouver + Calgary) | crea_resales_toronto, crea_resales_vancouver, crea_resales_calgary | Three-line, 12M rolling | None | housing/Panel1Prices — **needs adapt** (Sibley canon Section 4.4 unit 1 is MLS HPI for "national plus six CMAs (Toronto, Vancouver, Montreal, Calgary, Ottawa, Edmonton)" — that's prices, not resale counts. CMA resale counts deserve a dedicated panel slot. Recommend new Panel<NEW> for activity-by-CMA OR fold into Panel2Activity with a CMA toggle. Sibley canon does NOT currently carry CMA-level resale counts — **new panel candidate**) |
| 5 | Housing Starts (level + 3M MA + 12M MA), CMHC supply-target context | housing_starts, housing_starts_3m (derived), housing_starts_12m (derived) | Three-line | 3M MA default per Sibley voice principle on noise filtering | housing/Panel2Activity — **already exists** (Sibley canon unit 2 = starts with 3M MA. Direct match) |
| 6 | Mortgage Renewal Payment Shock | (custom MortgageShockSpec; BoC SAN 2025-21 chart reproduction) | Custom bar/distribution panel | Static citation chart | housing/Panel5MortgageStack — **needs adapt** (this is a stylized reproduction of a BoC chart for Pillar A — the mortgage renewal wall deep-dive. At basics layer, Sibley Panel5 cites the BoC chartpack rather than reconstructing. **Recommend: keep at basics as cited-static chart, OR home in the Pillar A deep-dive page where it's argumentatively load-bearing**) |
| 7 | Housing Prices (NHPI + CREA MLS HPI; YoY default, Index toggle) | nhpi_yoy (derived), crea_mls_hpi_yoy (derived); alt: nhpi_rebased, crea_mls_hpi_rebased | Two-line, YoY/Index toggle | Rebased to Jan 2020 = 100 in index view | housing/Panel1Prices — **already exists** (canon match. Sibley spec calls for national + six CMAs, which is a broader cut than boc-tracker's national-only. Sibley extension, not regression) |
| 8 | Residential Building Permits (level) | residential_permits_b (derived from residential_permits, M to B) | Single-series, max-range default | None | housing/Panel2Activity — **already exists** (canon match: "permits as the leading indicator" in Panel2) |
| 9 | Housing Affordability | housing_affordability | Single-series, quarterly | Static; BoC affordability index | housing/Panel<NEW> — **new panel** (BoC affordability index — qualifying-mortgage-payment as share of income — is a real coverage gap. Sibley canon Section 4.4 does not include it. Could land as Panel7 affordability OR as secondary track on Panel5MortgageStack — Panel5 is the natural home for "what does carrying a mortgage cost." **Strong candidate for new panel slot**) |

### policy.html (5 charts)

| # | Subject | Data series | Type | Special treatment | Sibley mapping |
|---|---|---|---|---|---|
| 1 | Peer Central Bank Policy Rates (BoC + Fed + ECB + BoE + RBA) | overnight_rate, fed_funds, ecb_rate, boe_rate, rba_rate | Multi-line step | None | policy/Panel1OvernightRate — **needs adapt** (Sibley Panel1 is BoC-only with neutral band. Peer-bank rates are the spread context for Panel3BoCFedSpread. Recommend: ECB/BoE/RBA either as secondary toggle on Panel1 OR fold into Panel3 as multi-peer panel. **Editorial call**: P1 readers care most about BoC-Fed; BoE/RBA/ECB are second-tier. Recommend secondary toggle on Panel1) |
| 2 | BoC Assets (total + GoC bonds + T-bills + repos + advances) | boc_total_assets, boc_goc_bonds, boc_tbills, boc_repos, boc_advances | Multi-line, weekly | None | policy/Panel4BalanceSheet — **already exists** (Sibley canon Section 4.5 unit 4 is "BoC settlement balances and asset composition; phase QE/reinvestment/passive QT/floor maintenance." Asset composition direct match) |
| 3 | BoC Liabilities (total + settlement balances + banknotes + GoC deposits + reverse repos) | boc_total_liabilities, boc_settlement_balances, boc_banknotes, boc_goc_deposits, boc_reverse_repos | Multi-line, weekly | None | policy/Panel4BalanceSheet — **already exists** (settlement balances is the load-bearing series for the phase call; canon match. Recommend Panel4 carry both assets and liabilities views with a toggle) |
| 4 | CORRA vs Overnight Rate Target (default: spread only) | corra_target_spread (derived), corra_daily, overnight_rate_daily | Multi-line, daily, 20-day smoothing | Spread is featured; raw lines available as toggles | policy/Panel<NEW> — **new panel** (CORRA-vs-target is the BoC's funding-market plumbing read — picks up overnight-market dysfunction signals like the late-2024 episode. Sibley canon Section 4.5 monetary slate does not include it. Recommend **new panel** OR fold into Panel4BalanceSheet — the settlement-balances-vs-floor framing connects directly to CORRA dispersion. Editorial decision needed. **Top 5 candidate**: this is exactly the kind of underloved BoC-internals signal Sibley should carry to stand apart from Big-Six notes) |
| 5 | Real Policy Rate (overnight - headline CPI Y/Y) | real_overnight_rate (derived) | Single-series | None | policy/Panel<NEW> or fold into Panel1 — **needs adapt** (Real policy rate is the headline-CPI-deflated read of stance; sharper than the nominal rate alone. Sibley canon Panel1 shows overnight + neutral band but does not currently carry the real-rate transform. Recommend: real-rate as secondary toggle on Panel1OvernightRate — same chart, transform switch. Low-effort coverage win) |

### financial.html (7 charts; the Sibley-equivalent "Markets" section)

| # | Subject | Data series | Type | Special treatment | Sibley mapping |
|---|---|---|---|---|---|
| 1 | USD/CAD (Bilateral) | usdcad | Single-series, daily | None | markets/Panel1CAD — **already exists** (Sibley canon Section 4.6 unit 1: USDCAD level + CEER + USDCAD percentile classifier. USDCAD bilateral is the core series) |
| 2 | CEER (Trade-Weighted CAD) | (placeholder, no lines wired) | Multi-line stub | "[Coming soon]" footnote | markets/Panel1CAD — **needs adapt** (Sibley canon already specifies CEER. boc-tracker shipped this as a stub; Sibley is committing to wire it. Coverage gap that Sibley already addresses by canon) |
| 3 | WTI - WCS Differential | wcs, wti (derived differential) | Custom native panel (`_build_wcs_wti_panel`) | Differential as primary view | markets/Panel4Energy — **already exists** (Sibley canon Section 4.6 unit 4: WTI, Brent, WCS at monthly cadence with "do-not-surface-daily-comparison-differential" caveat per Section 4.6. boc-tracker shows the daily differential; Sibley canon explicitly cautions against this. **Methodology call to make in the panel**: boc-tracker's daily differential is the wrong cadence per Sibley voice; monthly WCS is the right one) |
| 4 | 2-Year Yields (Canada + US + can2y-overnight spread + can-us 2y spread) | yield_2yr, us_2yr, can2y_overnight_spread (derived), can_us_2y_spread (derived) | Multi-line, daily, 20-day smoothing | None | markets/Panel2GoCCurve + policy/Panel3BoCFedSpread — **already exists** (yields split across two Sibley panels — Panel2 for the GoC curve, Panel3 for BoC-Fed/Can-US spread; Sibley's split is canon-correct) |
| 5 | Oil Prices (WTI + Brent + WCS) | wti, brent, wcs | Multi-line, daily smoothing on WTI/Brent, monthly WCS | ymin=0; 20-day smoothing | markets/Panel4Energy — **already exists** (canon match) |
| 6 | GoC Yield Curve (2Y + 5Y + 10Y + 30Y) | yield_2yr, yield_5yr, yield_10yr, yield_30yr | Four-line, daily, 20-day smoothing | None | markets/Panel2GoCCurve — **already exists** (Sibley canon Section 4.6 unit 2: "2y, 5y, 10y, 30y; spread to UST at the 2y and 10y; term premium where decomposable." Direct match) |
| 7 | 2Y-10Y Spread | yield_10y_2y_spread (derived) | Single-series | None | markets/Panel2GoCCurve — **already exists** (yield-curve spread is a derivation off Panel2's series; surface as toggle on Panel2 rather than separate panel) |

### trade.html (2 charts)

| # | Subject | Data series | Type | Special treatment | Sibley mapping |
|---|---|---|---|---|---|
| 1 | Canada-US Bilateral Trade (exports + imports + balance) | trade_exports_us_b (derived), trade_imports_us_b (derived), trade_balance_us_b (derived) | Three-line, monthly | None | trade/Panel3PartnerShares — **already exists** (Sibley canon Section 4.7 unit 3: "US bilateral, plus China, UK, Japan, Mexico, Germany." Sibley extension — boc-tracker is US-only) |
| 2 | Total Merchandise Trade (total exports + imports + balance) | trade_exports_total_b (derived), trade_imports_total_b (derived), trade_balance_total_b (derived) | Three-line, monthly | None | trade/Panel1TradeBalance — **already exists** (Sibley canon Section 4.7 unit 1: BOP-basis merchandise trade with three-month MA + HS-section decomposition. Sibley's spec is the substantive extension of boc-tracker's headline view) |

### demographics.html (2 charts)

| # | Subject | Data series | Type | Special treatment | Sibley mapping |
|---|---|---|---|---|---|
| 1 | International Migration Components (immigrants + NPR inflows + emigrants + net emigration + net NPR) | pop_immigrants, pop_npr_inflows, pop_emigrants, pop_net_emigration, pop_net_npr | Five-line, quarterly | None | labour/Panel5IRCCSupplyTrajectory — **already exists** (Sibley canon folds demographics into labour. Section 4.3 unit 5: "stacked-composition chart of PR inflows and NPR inflows (four-quarter trailing sum), with dated annotations at each IRCC levels-plan vintage." Sibley canon extends boc-tracker with IRCC-plan annotations and trailing-sum smoothing) |
| 2 | Labour Force by Age Group (youth + prime-age unemployment) | youth_unemployment_rate, prime_age_unemployment_rate | Two-line | None | labour/Panel1LFSHeadline — **already exists** (duplicate of labour.html #1 in a different framing; folded under labour per Sibley canon's Section 4 consolidation) |

## Summary by Sibley section

Coverage delta vs canon. Counts: boc-tracker total = 51 charts (with 5
homepage charts overlapping six pages, so unique subject count is
lower — see notes).

### GDP (Sibley canon: 6 panels)

- **Already covered (mapped to existing Sibley panel):**
  - boc-tracker gdp #1 / index #3 (Real GDP level + potential) -> Panel1HeadlineGDP + Panel5OutputGap
  - boc-tracker gdp #6 (Contributions stacked bar) -> Panel3Contributions

- **Needs adapt:**
  - boc-tracker gdp #2 (Output Gap, HP-filter) -> Panel5OutputGap **methodology swap** (HP-filter to BoC MPR potential per Section 4.1)
  - boc-tracker gdp #5 (Monthly GDP + industry overlays) -> Panel2IndustryVsExpenditure **adopt the industry-overlay toggle pattern**

- **New panel candidates:**
  - boc-tracker gdp #4 (Capacity Utilization total + manufacturing) -> Panel<NEW> or cross-section to Labour
  - boc-tracker gdp #3 (Productivity decomposition stub) -> Pillar D deep-dive, **skip at basics**

- **Net delta:** +0 to +1 panels (capacity utilization is the only real coverage gap; could fold elsewhere). **GDP coverage parity is essentially achieved by the existing six-panel canon.**

### Inflation (Sibley canon: 6 panels)

- **Already covered:**
  - boc-tracker inflation #2 / index #2 (Core measures) -> Panel2CoreTrio
  - boc-tracker inflation #4 (CPI components) -> Panel4SubAggregates
  - boc-tracker inflation #5 (CPI Breadth) -> Panel3Breadth
  - boc-tracker inflation #6 (Consumer Expectations) -> Panel5Expectations
  - boc-tracker inflation #7 (BOS distribution) -> Panel5Expectations **partial — needs BOS view added**

- **Needs adapt:**
  - boc-tracker inflation #1 (Headline vs ex-indirect-taxes stub) -> Panel1HeadlineCPI **add ex-indirect-taxes toggle**
  - boc-tracker inflation #7 (BOS distribution) -> Panel5Expectations **add BOS view, currently consumer-only**
  - boc-tracker inflation #3 (60-component decomposition stub) -> Panel4SubAggregates **decision: stay aggregate (recommended) or build full component view**

- **New panel candidates:** none material at basics layer

- **Pass-through panel (Panel6PassThrough)** — Sibley canon-only addition (not in boc-tracker); USDCAD-vs-goods CPI and wages-vs-services CPI strip charts. This is Sibley extending coverage, not boc-tracker coverage Sibley is missing.

- **Net delta:** 0 panels. Inflation coverage parity is achieved; gap is in implementation completeness on Panel5 (consumer + BOS) and Panel1 (ex-indirect-taxes toggle).

### Labour (Sibley canon: 6 panels; absorbs demographics)

- **Already covered:**
  - boc-tracker labour #7 (Aggregate participation/employment) -> Panel1LFSHeadline
  - boc-tracker labour #2 (Beveridge curve) -> Panel4VacanciesSlack
  - boc-tracker labour vacancy chart (index #4 part) -> Panel4VacanciesSlack
  - boc-tracker demographics #1 (Migration components) -> Panel5IRCCSupplyTrajectory
  - boc-tracker demographics #2 (Age-group unemployment) -> Panel1LFSHeadline (overlaps with labour #1)

- **Needs adapt:**
  - boc-tracker labour #1 (Unemployment by age) -> Panel1LFSHeadline **add youth/prime-age toggle**
  - boc-tracker labour #5 (Prime-age labour market) -> Panel1 or Panel2 **add prime-age triplet view**
  - boc-tracker labour #6 (Youth labour market) -> Panel1 or Panel2 **add youth triplet view, paired with prime-age**

- **New panel candidates:**
  - boc-tracker labour #4 (EI Regular Beneficiaries) -> **NEW panel or fold into Panel4VacanciesSlack** (strong editorial case — leading recession indicator)
  - boc-tracker labour #9 (Unit Labour Costs) -> **fold into Panel3WageBand as toggle** (productivity-adjusted wage read)

- **Skip:**
  - boc-tracker labour #3 (R-indicators stub) — defer to deep-dive on slack
  - boc-tracker labour #8 (Indeed postings stub) — JVWS is canon primary

- **Wage band (Sibley Panel3) already exists and matches** boc-tracker index #5 / labour wage chart.

- **Sibley canon-only additions:** Panel2PerCapita (per-capita employment + hours; signature panel per Section 4.3), Panel6RegionalDumbbell (four-province dumbbell). These are Sibley extending boc-tracker, not coverage gaps Sibley needs to close.

- **Net delta:** +1 panel realistically (EI beneficiaries). ULC can fold into Panel3 as a toggle. Youth/prime age splits can fold into Panel1 as toggles.

### Housing (Sibley canon: 6 panels)

- **Already covered:**
  - boc-tracker housing #1 (CREA SNLR + resales) -> Panel3Inventory
  - boc-tracker housing #3 (Units under construction) -> Panel2Activity **verify coverage**
  - boc-tracker housing #5 (Housing starts + 3M MA) -> Panel2Activity
  - boc-tracker housing #7 (Housing prices NHPI + MLS) -> Panel1Prices
  - boc-tracker housing #8 (Residential permits) -> Panel2Activity

- **Needs adapt:**
  - boc-tracker housing #2 (5Y mortgage vs 5Y GoC) -> Panel5MortgageStack **decide: include cost-of-borrowing view in Panel5**
  - boc-tracker housing #6 (Mortgage renewal shock, BoC SAN repro) -> Panel5MortgageStack OR Pillar A deep-dive

- **New panel candidates:**
  - boc-tracker housing #4 (Resale activity by CMA, three cities) -> **NEW panel** or fold into Panel2 (CMA-level activity is genuinely not covered; Sibley canon covers CMA-level only for prices)
  - boc-tracker housing #9 (Housing Affordability index) -> **NEW panel** or fold into Panel5 (BoC affordability index — qualifying-mortgage-payment-to-income; strong editorial case)

- **Sibley canon-only additions:** Panel4Rent (CMHC RMS rents), Panel6PopulationStock (population-to-housing-stock ratio). Sibley extensions.

- **Net delta:** +1 to +2 panels (CMA resale activity + affordability, depending on whether both get standalone slots or fold into existing panels).

### Policy (Sibley canon: 8 panels — 4 monetary + 4 fiscal)

- **Already covered (monetary):**
  - boc-tracker policy #1 (Peer policy rates) -> Panel1OvernightRate **add peer view as secondary toggle**
  - boc-tracker policy #2 (BoC Assets) -> Panel4BalanceSheet
  - boc-tracker policy #3 (BoC Liabilities) -> Panel4BalanceSheet
  - boc-tracker index #1 / policy implicit (BoC-Fed spread) -> Panel3BoCFedSpread

- **Needs adapt:**
  - boc-tracker policy #5 (Real policy rate) -> Panel1OvernightRate **add real-rate transform toggle**

- **New panel candidates:**
  - boc-tracker policy #4 (CORRA vs target spread) -> **NEW panel OR fold into Panel4** (top-5 editorial case below)

- **Skip:** none in policy.

- **Sibley canon-only additions (fiscal slate, none in boc-tracker):** Panel5FederalTrajectory, Panel6FiscalStanceCycle, plus two more fiscal panels per Section 4.5. **The entire fiscal slate is Sibley extending coverage — boc-tracker has no fiscal page.**

- **Net delta:** 0-1 monetary panels (CORRA). Fiscal is +4 panels by Sibley canon (already accounted for in the eight-panel canon spec).

### Markets (Sibley canon: 6 panels; was "Financial Conditions" in boc-tracker)

- **Already covered:**
  - boc-tracker financial #1 (USDCAD) -> Panel1CAD
  - boc-tracker financial #3 (WTI-WCS differential) -> Panel4Energy **with cadence correction per Sibley canon**
  - boc-tracker financial #4 (2Y yields + spreads) -> Panel2GoCCurve + policy/Panel3BoCFedSpread
  - boc-tracker financial #5 (Oil prices WTI/Brent/WCS) -> Panel4Energy
  - boc-tracker financial #6 (GoC curve 2/5/10/30) -> Panel2GoCCurve
  - boc-tracker financial #7 (2Y-10Y spread) -> Panel2GoCCurve (toggle)

- **Needs adapt:**
  - boc-tracker financial #2 (CEER stub) -> Panel1CAD **Sibley canon wires what boc-tracker stubbed**

- **Sibley canon-only additions:** Panel3CreditSpreads (US IG/HY OAS), Panel5BankStability (PCL builds + CET1 + uninsured residential), Panel6FCI (financial conditions index). These are Sibley extending coverage.

- **Net delta:** 0 panels. Markets coverage parity is achieved; gaps are in implementation (CEER wiring).

### Trade (Sibley canon: 6 panels)

- **Already covered:**
  - boc-tracker trade #1 (CA-US bilateral) -> Panel3PartnerShares **with partner extension to China/UK/Japan/Mexico/Germany**
  - boc-tracker trade #2 (Total merchandise) -> Panel1TradeBalance **with three-month MA + HS-section decomposition extensions**

- **Sibley canon-only additions:** Panel2CurrentAccount, Panel4TariffState, Panel5TermsOfTrade, Panel6FDIBySector. All Sibley extensions.

- **Net delta:** 0 panels. Trade coverage parity is trivially achieved (boc-tracker had only 2 trade charts).

### Total delta across all sections

| Section | Sibley canon panels | boc-tracker charts | New panels needed | Folds into existing |
|---|---|---|---|---|
| GDP | 6 | 6 | 0-1 (capacity util) | 1 (HP-filter -> MPR methodology) |
| Inflation | 6 | 7 | 0 | 2 (ex-indirect-taxes toggle, BOS view) |
| Labour | 6 | 9 + 2 demo | 1 (EI beneficiaries) | 3-4 (age splits, ULC) |
| Housing | 6 | 9 | 1-2 (affordability, CMA resales) | 1 (5Y mortgage vs GoC) |
| Policy | 8 (4M+4F) | 5 (mon. only) | 1 (CORRA) | 1 (real rate, peer rates) |
| Markets | 6 | 7 | 0 | 0 (CEER wiring only) |
| Trade | 6 | 2 | 0 | 0 |
| **Total** | **44** | **45** | **3-5** | **8-10** |

Coverage-parity gap is genuinely small: Sibley canon already accounts for most boc-tracker subjects through equal or extended coverage. The real new-panel candidates number 3-5, concentrated in Labour (EI), Housing (affordability, CMA resales), Policy (CORRA), and possibly GDP (capacity utilization).

## Top 5 "new panel needed" recommendations, ranked

1. **EI Regular Beneficiaries (Labour)** — Strongest editorial case. Leading recession indicator that fires before LFS unemployment turns. Monthly StatCan series, already in pipeline (`ei_regular_beneficiaries.csv`). Pairs naturally with Panel4VacanciesSlack as the demand-side mirror — vacancies fall, EI rises. Recommended: new Panel7Labour or secondary track on Panel4. **Editorial weight: P1 readers track EI for cyclical inflection; carrying this puts Sibley ahead of Big-Six labour notes that rarely surface it.**

2. **CORRA vs Overnight Rate Target (Policy/Monetary)** — Funding-market plumbing read; picks up overnight-market dysfunction (late-2024 episode). BoC daily series (`corra_daily.csv`, `overnight_rate_daily.csv`). Maps directly to the BoC's settlement-balances framing in Panel4BalanceSheet. Recommended: surface as a sub-panel inside Panel4 (settlement balances and CORRA dispersion are the two sides of the same balance-sheet plumbing read). **Editorial weight: Sibley earns its keep against Big-Six by carrying internal-plumbing signals; CORRA is exactly that kind of signal.**

3. **Housing Affordability index (Housing)** — BoC's quarterly qualifying-mortgage-payment-to-income ratio. Directly addresses the "what does carrying a mortgage actually cost" question that Panel5MortgageStack frames at the snapshot level. Series in pipeline (`housing_affordability.csv`). Recommended: secondary track on Panel5 OR new Panel7Housing. **Editorial weight: Bay Street housing reads almost always cite affordability; not carrying it would be a noticeable omission.**

4. **CMA-level Resale Activity (Housing)** — Toronto/Vancouver/Calgary monthly resale counts (Sibley canon Section 4.4 carries CMA-level for prices but not activity). Real coverage gap. Series in pipeline (`crea_resales_toronto.csv` etc.). Recommended: new Panel slot OR fold into Panel2Activity with a CMA toggle. **Editorial weight: Activity-by-CMA is the leading indicator for CMA prices; covering one cut without the other reads inconsistent.**

5. **Capacity Utilization (GDP or Labour)** — Quarterly StatCan series for total industry + manufacturing. Sibley canon does not include it. Slack-side read that competes with V/U for the same analytical job; an editorial decision is required on home section. Recommended: secondary track on Panel5OutputGap (gap-from-potential + slack-from-utilization belong together). **Editorial weight: moderate — capacity utilization is more useful when manufacturing is the binding constraint, less when services are. Worth carrying given the StatCan series is free and the build cost is low.**

## Charts deemed candidates for "skip" at basics

- **GDP productivity-decomposition stub (gdp #3)** — Pillar D deep-dive territory; basics-layer would be empty until full hours-worked and decomposition pipeline is built.
- **LFS R-indicators stub (labour #3)** — Sibley canon uses U3 as headline; R7/R8 expansions belong in a labour-slack deep-dive.
- **Indeed Job Postings stub (labour #8)** — JVWS is the canon vacancy series per Section 4.3 unit 4. Indeed is a real-time proxy useful only if JVWS lag becomes editorial.

## Charts that are duplicates across boc-tracker pages

- **Real GDP level + HP potential**: index #3 = gdp #1 (homepage thumbnail of the deep-dive chart)
- **Policy rates (BoC + Fed)**: index #1 = policy #1 partial (homepage uses two-line, policy page extends to five-bank peer)
- **Core inflation band**: index #2 = inflation #2 partial (homepage band, inflation page individual lines)
- **Unemployment + vacancies**: index #4 = labour #1 + #2 partial (homepage combines headline + Beveridge view)
- **Wage growth band**: index #5 = (no exact duplicate, but related to labour wage panel)
- **Age-group unemployment**: labour #1 = demographics #2 (same data, two pages)

Treat boc-tracker's homepage as a thumbnail summary of subject-page deep dives; Sibley's homepage panel grid plays the same role, sourcing thumbnails from section panels.

## Appendix A: v2/ directory

`boc-tracker/v2/` is a UI redesign mock authored as a React + CSS-variable
exploration of a Vignelli-leaning visual canon. Findings:

- `v2/index.html` is a high-fidelity recreation of `index.html`'s **same five charts** (policy rates / core inflation / real GDP / unemployment+vacancies / wage growth) — UI changes only, no new indicators.
- `v2/inflation.html` is a React mount that renders a stylized inflation page; the chart **subjects are a subset** of `inflation.html` (core measures and CPI components only). A new addition is a **sub-aggregate breadth table** with rows for each CPI category and columns Y/Y, 3M-AR, M/M, contribution to headline, status. **This table view is not in v1 boc-tracker; it is a v2-only UI element.** Worth flagging: the same data can be derived from the existing CPI series + basket weights; could land as a methodology-page table on Sibley's `/inflation/` page rather than a chartbook unit.
- No v2 versions exist for gdp, labour, housing, policy, financial, trade, demographics. v2 is incomplete and was clearly paused before full conversion.

**Recommendation**: **Sibley adopts v1 (`build.py PAGES`) as the indicator-set ground truth.** v2 contributes no new indicator subjects, only UI mocks. The sub-aggregate breadth table is a methodology-page candidate, not a chartbook unit.

## Appendix B: data series inventory

51 raw CSVs in `boc-tracker/data/raw/` map to the chart subjects above.
The Sibley `data/raw/` directory is the same shape (already inspected
during research). The derived-series mapping in `build.py` line 3845-3873
(`_DERIVED_SERIES_SOURCES` dict) enumerates the 18 build-time
transformations Sibley should preserve when wiring panels.

## File path

`C:\Users\jayzh\projects\macro-research-department\research\boc_tracker_chart_inventory.md`
