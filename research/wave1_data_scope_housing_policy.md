# Wave 1, Brief 1.3 — Basics-Layer Data Scope: Housing and Policy

Sources of truth for this scope:
- Editorial canon: `editorial/dashboard_purpose.md` Sections 4.4 (Housing) and 4.5 (Policy).
- boc-tracker inventory: `C:\Users\jayzh\Documents\boc-tracker\fetch.py`, `data\*.csv`,
  `housing.html`, `policy.html` (titled "Monetary Policy" — monetary-only).
- Pipeline contract: `ARCHITECTURE.md` ADR-0002 / ADR-0004; `data\SOURCES.md`.

Basics-layer only. Deep dives A / B / C / F are out of scope.

---

## Section 4.4 — Housing

EDR basics elements (6):
H1. Prices: MLS HPI national + 6 CMAs (Toronto, Vancouver, Montreal, Calgary, Ottawa, Edmonton); Y/Y and 6m annualized. No national average.
H2. Activity: starts (3m MA), completions, permits as leading indicator; rental vs ownership split.
H3. Inventory and absorption: MLS sales-to-new-listings; months of inventory by CMA.
H4. Rent: CMHC rental market data + StatCan rent series; Toronto/Vancouver loosening visible.
H5. Mortgage stack snapshot: OSFI residential mortgage data; BoC mortgage stock by vintage and term; CMHC arrears/delinquency.
H6. Population-to-housing-stock ratio by CMA.

### Coverage table

| Element | boc-tracker coverage | Primary source | Cadence | Revision pattern | Gotchas |
|---|---|---|---|---|---|
| H1 — MLS HPI Canada | COVERED. `crea_mls_hpi.csv` via BoC Valet `FVI_CREA_MLS_HPI_CANADA` (2014-) | CREA (republished by BoC FVI) | Monthly | Composite HPI back-revises ~prior 3 months as new sales close late | National only via FVI; CMA-level HPI is NOT in BoC FVI (only resales are). New-Housing-Price-Index (`new_housing_price_index.csv`, StatCan v111955442) is a DIFFERENT series — NHPI tracks builder-set new-construction prices, not the MLS resale benchmark; do not substitute |
| H1 — CMA HPI (6 CMAs Y/Y + 6m annualized) | GAP for benchmark price; PARTIAL for resale volumes (`crea_resales_toronto/vancouver/calgary.csv` via BoC FVI `FVI_HOUSE_RESALES_12M_*`). Montreal, Ottawa, Edmonton resale series NOT in boc-tracker | CREA MLS HPI Tool (`https://www.crea.ca/housing-market-stats/mls-home-price-index/`); per-CMA monthly XLSX | Monthly | Same back-revision as national | CREA bulk download via XLSX, not API; aggregate to "Composite", "Single Family", and seasonally-adjusted vs not — pick deliberately and document. Greater-area definitions (e.g. GTA vs Toronto C01) matter; CREA reports the CMA-equivalent board territory, which is the v1 cut |
| H2 — Starts | COVERED. `housing_starts.csv` via StatCan v52300157 (Table 34-10-0158-01, SAAR, total units). 3m MA is a transform, not a source ask | StatCan Table 34-10-0158 / CMHC | Monthly, ~3-week lag | Prior 1-2 months revise as late permits and field reports arrive | SAAR units, not the trend cycle CMHC also publishes; CMHC's trend (6m MA) is a derived line, easy to reconstruct |
| H2 — Completions | GAP | StatCan Table 34-10-0135 (CMHC completions by intended market, monthly); also CMHC HMIP | Monthly | Same window as starts | Available by intended market (homeowner / rental / condo / co-op) — that is the cut that buys you the "rental vs ownership split" the canon asks for |
| H2 — Permits (leading indicator) | COVERED. `residential_permits.csv` via StatCan v1675119646 (Table 34-10-0292-01, value SA, current $ thousands) | StatCan Table 34-10-0292 | Monthly, ~30-day lag | Prior month revises routinely | Value-basis only in this vector; the canon's framing ("leading indicator") is well served by value, but units-basis (Table 34-10-0066) gives a count-based read if requested |
| H2 — Rental vs ownership split | GAP at the starts level for the headline (housing_starts.csv is total only) | StatCan Table 34-10-0158 alternate vectors (intended market dimension); or CMHC HMIP | Monthly | Same as H2 starts | New vectors needed; CMHC's intended-market breakdown is the cleaner cut |
| H3 — Sales-to-new-listings | COVERED. `crea_snlr.csv` via BoC Valet `FVI_CREA_HOUSE_SALES_TO_NEW_LISTINGS_CANADA` (national, monthly, %) | CREA via BoC FVI | Monthly | Back-revises with listings | National only in FVI; by-CMA SNLR requires CREA XLSX |
| H3 — Months of inventory by CMA | GAP. boc-tracker has resale volumes for 3 CMAs (Toronto/Vancouver/Calgary) but no active listings stock | CREA MLS Statistics XLSX (active listings); MOI = active listings / monthly sales | Monthly | Same as inventory | Construction watch (see below) — derived, not a single endpoint; document the formula |
| H4 — Rent (CMHC) | GAP | CMHC Rental Market Survey / Report (annual primary, October fielding; Rental Market Indicators monthly proxy from Rentals.ca / market reports) | Annual (CMHC RMS); monthly proxy series exist | CMHC RMS is an annual snapshot; vacancy rate revisions on subsequent vintages are rare | CMHC's annual survey is the standing benchmark — primary citation — but the lag is 12 months. For "Toronto and Vancouver loosening visible" you need a monthly read |
| H4 — Rent (StatCan) | GAP for standalone rent — `cpi_shelter.csv` exists but is the broader shelter aggregate (rent + owned accom + mortgage interest + property tax + utilities) | StatCan Table 18-10-0004-01: CPI rented accommodation (v41691073) and rent (v41691074) | Monthly | Standard CPI revision window (small) | CPI rent index is a price-change measure, not a $level. For levels, CMHC RMS is the citation. For change-direction read, CPI rent works |
| H5 — OSFI residential mortgage data | GAP | OSFI Financial Data — Domestic Banks ("Bank Financial Data" CSV; Residential Mortgage data tables); B-20 stress test history | Monthly (Financial Data); periodic (B-20 mechanics) | Standard regulatory reporting | OSFI publishes consolidated bank residential mortgage portfolios; the "mortgage stack snapshot" question is partly here (loan-balance composition) and partly BoC (vintage / term breakdown) |
| H5 — BoC mortgage stock by vintage / term | GAP | BoC Staff Analytical Note + Valet sub-series on outstanding household credit (residential mortgage loans, V36903 family); for vintage-and-term, BoC's Residential Mortgage Market chartpack | Monthly (Valet); periodic (chartpack) | Standard | The "vintage and term" framing tracks BoC's deep-dive chart that breaks the stock into fixed-5yr / fixed-other / variable buckets. Not a single Valet key; reconstruction required. v1 basics can cite BoC's most recent published chart |
| H5 — CMHC arrears / delinquency | GAP | CMHC Residential Mortgage Industry Report (RMIR), quarterly; "Mortgages in Arrears" series | Quarterly | RMIR revises infrequently | RMIR is a PDF + dashboard; the arrears rate (% of mortgages in arrears 90+ days) is the headline. CBA also publishes a chartered-bank-only arrears series monthly — use as a higher-frequency proxy |
| H6 — Population-to-housing-stock ratio by CMA | GAP. boc-tracker has national pop components (`pop_immigrants.csv`, `pop_npr_inflows.csv`, etc.) but no CMA pop and no housing stock | Numerator: StatCan Table 17-10-0135 (annual CMA population). Denominator: StatCan Table 36-10-0688 (housing stock estimates) or CMHC SCHL housing stock | Annual | Annual estimates revise once per cycle | Construction watch — this is a ratio we build; not a single endpoint. EDR's framing is "the supply-response denominator," so the construction is meaningful but defensible from primary StatCan |

### Housing — gap list

1. **CMA-level MLS HPI** (5 of 6 CMAs at price level; Toronto / Vancouver / Calgary only have resale volume coverage). Source: CREA MLS HPI Tool XLSX bulk download.
2. **Completions** (Table 34-10-0135 vector).
3. **Starts by intended market** (rental vs ownership split — additional Table 34-10-0158 vectors).
4. **Months of inventory** by CMA (active listings + sales; CREA XLSX).
5. **CMHC rental market data** (annual RMS vacancy + rent levels; primary cite — RMS report).
6. **StatCan rent CPI** sub-series (v41691073, v41691074) — easy add to pipeline.
7. **OSFI residential mortgage data** (Bank Financial Data CSV).
8. **BoC mortgage stack by vintage / term** (Valet household credit series + the periodic BoC chartpack as primary cite for the v1 basics call-out).
9. **CMHC arrears** (RMIR + CBA chartered-bank arrears for monthly proxy).
10. **Population (CMA) and housing stock (CMA)** for the ratio.

### Housing — construction watchlist

- **Months of inventory by CMA** — active listings / monthly sales; derived, document formula.
- **Population-to-housing-stock ratio by CMA** — annual numerator / annual denominator; document base year and intercensal interpolation method if used.
- **6-month annualized HPI** (national and per CMA) — transform on top of CREA monthly HPI; trivial via `pipeline/transform/timeseries.py` (`pct_change_at_horizon` style).
- **Rental vs ownership split (starts)** — additive over intended-market sub-vectors.
- **Mortgage stack composition** — narrative reconstruction from BoC published chart in v1; full pipeline build is a deep-dive (Pillar A) deliverable, NOT a basics item.

### Housing — coverage estimate

Of the 6 basics elements, boc-tracker fully covers H1 (national HPI only — H1 is partial when CMA-level is in scope), H2 (starts + permits — partial; completions and intended-market split are gaps), H3 (national SNLR; CMA MOI is a gap). H4, H5, H6 are gaps.

**Headline: roughly 35-40% of the Housing basics surface is covered by what boc-tracker has on disk today.** The cheaply-closable gaps are large (CMA HPI via CREA XLSX, StatCan rent CPI sub-series, completions vector). The structurally-harder gaps are H5 mortgage stack (BoC chartpack + Valet stitching) and H6 population-to-stock (own construction).

---

## Section 4.5 — Policy

The EDR specifies two sub-surfaces on one page in v1. Scoped separately below.

### 4.5a — Monetary sub-surface

EDR basics elements (3-4):
M1. BoC overnight rate: current level, distance to estimated neutral band, consecutive-meeting action state (on hold / cutting / hiking).
M2. Market path: OIS-implied BoC path; 2y GoC vs overnight as term-structure read on expectations.
M3. BoC-Fed spread: current level, distribution context, regime classification.
M4. Balance sheet: BoC settlement balances and asset composition; phase (QE / reinvestment / passive QT / floor maintenance).

#### Monetary — coverage table

| Element | boc-tracker coverage | Primary source | Cadence | Revision pattern | Gotchas |
|---|---|---|---|---|---|
| M1 — Overnight rate level | COVERED. `overnight_rate.csv` (monthly, STATIC_ATABLE_V39079) + `overnight_rate_daily.csv` (V39079) | BoC Valet | Event-driven (FAD) + daily | Never revised | The pipeline already lifts these (see `data/processed/overnight_rate_target.csv`) |
| M1 — Distance to neutral | GAP. boc-tracker has no neutral-band series | BoC MPR estimate of nominal neutral (currently published as a range, last refresh April 2026 MPR); cite the MPR directly. CORRA (`corra_daily.csv`) is covered but is the realized overnight, not neutral | Semi-annual (BoC reassesses neutral in April MPR by convention) | Estimate revises with each MPR | The neutral range is an EXTRACTED NUMBER from the MPR PDF/HTML, not an API series. Treat as a researcher-curated value with vintage stamp; cite the MPR page |
| M1 — Consecutive-meeting action state | COVERED via primitives. `fad_calendar.json` + `fad_history.json` + `overnight_rate_daily.csv` together let you compute "consecutive no-change meetings" exactly as boc-tracker does | BoC iCal feed + Valet | Event-driven | None | Logic is a transform; not a series ask |
| M2 — OIS-implied BoC path | GAP. boc-tracker has CORRA but not OIS-implied forwards | BoC publishes the OIS curve in its Indicators of Capacity and Inflation pressures; cleanest endpoint is CanDeal / TMX BondCAD for OIS quotes. For a primary public source: BoC's MPR projection appendix sometimes prints the market-implied curve. Refinitiv / Bloomberg are not citable | Daily (market) / quarterly (MPR snapshot) | Market path resets daily | This is the hardest piece. v1-acceptable substitution: 2y OIS approximation via 2y GoC less term-premium proxy; OR cite the MPR's market-implied path chart and refresh quarterly. Flag as v1 deferral candidate to a Wave deep-dive if a clean primary endpoint is not available |
| M2 — 2y GoC vs overnight (term structure proxy) | COVERED. `yield_2yr.csv` (BD.CDN.2YR.DQ.YLD) + `overnight_rate_daily.csv` | BoC Valet | Daily | None for yield; never for overnight | Pipeline already wired in spirit; spread is a transform |
| M3 — BoC-Fed spread | PARTIAL. `overnight_rate_daily.csv` covered; `fed_funds.csv` covered (boc-tracker fetches FEDFUNDS pre-2008 + DFEDTARU/DFEDTARL midpoint post-2008 — see `fetch_fed_funds_target()` in fetch.py). Distribution context + regime classification are transforms | BoC Valet + FRED (DFEDTARU, DFEDTARL, FEDFUNDS) | Event-driven (FOMC) + daily | None | The "regime classification" is editorial interpretation — researcher constructs the cut, writer phrases it. Historical distribution: 35+ years of daily data is in covered series |
| M4 — Settlement balances | COVERED. `boc_settlement_balances.csv` (V36636, weekly, scaled to billions) | BoC Valet Statement of Financial Position | Weekly (Wednesday) | None | Pipeline-ready |
| M4 — Asset composition | COVERED. `boc_total_assets.csv`, `boc_goc_bonds.csv`, `boc_tbills.csv`, `boc_repos.csv`, `boc_advances.csv`, `boc_reverse_repos.csv` | BoC Valet | Weekly | None | Full SFP asset side already in boc-tracker. Liability side also covered (`boc_total_liabilities`, `boc_banknotes`, `boc_goc_deposits`) |
| M4 — Phase classification (QE / reinvestment / passive QT / floor) | Editorial interpretation, not a series | Derived from asset trajectory + BoC governing council statements + Carolyn Rogers operational speeches | Speech-event-driven | n/a | Researcher curates the phase calls with cite-to-statement timeline; do not try to algorithm this |

#### Monetary — gap list

1. **Neutral rate range** — MPR-extracted number; researcher-curated value with vintage stamp, cite MPR page directly.
2. **OIS-implied BoC path** — no clean primary endpoint; v1 candidates: (a) cite MPR market-implied chart quarterly; (b) approximate via 2y OIS / 2y GoC term-premium-adjusted; (c) defer the OIS-implied path to deep-dive (Pillar B) and use 2y GoC vs overnight as the only basics-layer term-structure read. **Recommend (a) for v1**: cite the BoC MPR's market-implied curve chart on a quarterly cadence; this is primary-source and editorially honest.
3. **Phase classification** — editorial curation, not a series.

#### Monetary — construction watchlist

- **Consecutive-meeting action state** — derived from FAD calendar + rate path.
- **BoC-Fed spread distribution percentile** — derived; transform on covered series.
- **Real policy rate** — already a `policy.html` chart in boc-tracker (overnight minus 1y inflation expectation or minus core); transform on covered series.

#### Monetary — coverage estimate

Of the 4 monetary basics elements, M1 is mostly covered (level + action state primitives present; neutral-band is a researcher-curated value, not a series gap of structural difficulty). M2 is partial (2y GoC vs overnight covered; OIS path is the gap). M3 is covered at the data layer (interpretation is editorial). M4 is fully covered.

**Headline: roughly 80% of the Monetary basics surface is covered by what boc-tracker has on disk today.** The single structural gap is OIS-implied path (M2), and that has a defensible v1 workaround.

---

### 4.5b — Fiscal sub-surface

EDR basics elements (3-4):
F1. Federal trajectory: DoF Fiscal Monitor latest; federal deficit YTD; debt-service costs as % of revenues; PBO vs FES baseline delta.
F2. Provincial: net debt-to-GDP for ON, QC, AB, BC; latest budget balance vs plan; any active credit-watch flags.
F3. Debt management: GoC issuance trajectory; average term; coupon roll into a higher-coupon stock.
F4. Fiscal stance vs cycle: structural balance estimate; cyclically-adjusted primary balance; consistency with monetary stance.

#### Fiscal — coverage table

| Element | boc-tracker coverage | Primary source | Cadence | Revision pattern | Gotchas |
|---|---|---|---|---|---|
| F1 — Federal deficit YTD (Fiscal Monitor) | GAP. ZERO fiscal data in boc-tracker. Confirmed by `fetch.py` and data dir grep | Department of Finance — Fiscal Monitor (`https://www.canada.ca/en/department-finance/services/publications/fiscal-monitor.html`). Published monthly with ~2-month lag. Tables are HTML + linked CSV in the supporting data | Monthly | Prior months revise as accounting closes; final Public Accounts (annual, December) is the authoritative restatement | Fiscal Monitor reports cumulative-fiscal-year-to-date (April-start FY); make sure the comparator is same-period prior year, not calendar |
| F1 — Debt-service costs as % of revenues | GAP | Computed from Fiscal Monitor public-debt-charges line ÷ revenues. Annualized version in Public Accounts and FES Annex 1 | Monthly (FM) / annual (Public Accounts, FES) | Same as FM | Definitional: PDC over revenues vs over GDP are both common; the EDR is explicit about "% of revenues." Document the choice |
| F1 — PBO vs FES baseline delta | GAP | PBO Economic and Fiscal Outlook (`https://www.pbo-dpb.ca/en/publications-publications` — biannual, March/October). DoF projections in FES (Nov-Dec) and Budget (Feb-Mar) | Biannual (PBO EFO); annual + mid-year (FES + Budget) | Each release supersedes the prior; PBO publishes scenarios | PBO Open Data Portal exposes structured projection downloads (`https://www.pbo-dpb.ca/en/data`). The delta is a comparison the writer makes from two cited projection sets; researcher provides both number sets with vintage stamps |
| F2 — Provincial net debt-to-GDP (ON, QC, AB, BC) | GAP | Each provincial budget + public accounts: ON Ministry of Finance, Finances Quebec, Government of Alberta, BC Ministry of Finance. Also OECD Subnational dataset (consolidated). For comparability, RBC Economics publishes a consolidated chart — that's a competitor source per voice principles, NOT citable | Annual budget (Feb-May) + Q3 update | Each budget supersedes plan; Public Accounts (annual) is authoritative | Definitional drift — net debt vs consolidated debt vs gross debt; each province uses its own accounting. The cleanest comparable source is each province's "long-term fiscal sustainability" table in the budget. Federation of Tax Administrators / CCFER do not publish this consolidated freely |
| F2 — Latest budget balance vs plan | GAP | Same provincial budget + quarterly fiscal updates | Annual + quarterly | Plan-vs-actual is naturally non-revising; the plan is fixed at budget date, actuals revise quarterly | Each province has its own timing; budget season Feb-May |
| F2 — Credit-watch flags | GAP | Moody's, S&P, Fitch, DBRS Morningstar published rating actions; CDS spreads if available | Event-driven | n/a | Rating-agency citations are primary-source-grade; their reports are gated but the press releases are public. CDS spreads (e.g. Ontario CDS) are Bloomberg / Markit — not citable without a clean public mirror. Plan to cite rating actions, not market-based credit reads, in v1 |
| F3 — GoC issuance trajectory | GAP. Note: boc-tracker holds GoC YIELDS but not the issuance schedule or outstanding stock by maturity | DoF Debt Management Strategy (annual, accompanying Budget); DoF quarterly debt operations report; BoC publishes auction results (`https://www.bankofcanada.ca/markets/government-securities-auctions/`) | Annual DMS; quarterly debt operations; per-auction | Forward issuance plan revises in the DMS update | The auction-level data on BoC is high-frequency but the editorial cut ("trajectory, term, coupon roll") is best framed off the DMS narrative + the FES/Budget debt management annex |
| F3 — Average term | GAP | DoF Debt Management Strategy + Public Accounts (annual) | Annual | Slow-moving | Average-term-to-maturity (ATM) is a published metric in DMS Annex; no construction needed |
| F3 — Coupon roll into higher-coupon stock | GAP | DoF DMS + BoC auction history | Annual + per-auction | n/a | Editorial framing — the underlying data is the auction tape (BoC site) + DoF maturity profile (DMS Annex). v1 basics can cite the DMS "redemption profile" table directly |
| F4 — Structural balance / cyclically-adjusted primary balance | GAP. **Construction-required.** Not published as an official Canadian series by DoF | IMF Article IV Canada (publishes CAPB estimates), OECD Economic Survey of Canada (also publishes), PBO occasionally publishes a structural balance in its Fiscal Sustainability Report | Annual (IMF, OECD); periodic (PBO) | Each vintage revises with output-gap estimate | The Canadian DoF does NOT publish a CAPB. IMF and OECD do, with their own methodology. C.D. Howe occasionally publishes one. For v1 basics, citing IMF Article IV's CAPB is defensible and primary-source-grade |
| F4 — Consistency with monetary stance | Editorial interpretation, not a series | Composite of fiscal impulse + monetary stance | n/a | n/a | Researcher provides the fiscal-impulse number with cite; writer phrases the consistency call |

#### Fiscal — gap list (everything is a gap)

1. **DoF Fiscal Monitor** — monthly, two-month lag; primary source for federal deficit YTD and debt-service line. Build a lightweight HTML / CSV scraper or curate by-hand monthly. Recommend lightweight automated fetch given monthly cadence.
2. **PBO Economic and Fiscal Outlook** — biannual; PBO Open Data Portal exposes structured downloads. Build a fetcher or curate by-release.
3. **DoF FES + Budget projections** — annual + mid-year; PDF + Annex tables. Curate by-release.
4. **Provincial budgets (ON, QC, AB, BC)** — annual + quarterly. Each ministry's site. Curate by-release; build templated extraction notes per province.
5. **DoF Debt Management Strategy** — annual, with budget. Curate by-release; the ATM and redemption profile tables are the high-value lifts.
6. **BoC auction results** — `https://www.bankofcanada.ca/markets/government-securities-auctions/` — per-auction; available as structured pages or downloads. Optional v1; if researcher cites DMS annex for the structural read this is not load-bearing for basics.
7. **Rating-agency action log** — research-curated, not a feed.
8. **IMF Article IV CAPB and / or OECD CAPB** — for F4; researcher-curated, cite the latest IMF/OECD report.

#### Fiscal — construction watchlist

- **PBO vs FES baseline delta** — comparison computed from two cited projection sets; document vintage and series being compared (revenues, expenses, balance, debt) per the writer's framing.
- **Debt-service as % of revenues** — simple ratio from Fiscal Monitor lines; document numerator (public debt charges) and denominator (revenues) and that this is FY-to-date.
- **CAPB / structural balance** — **NOT a v1 construction**; cite IMF / OECD CAPB rather than building.
- **Fiscal impulse** — change in CAPB year-on-year; if F4 cites IMF CAPB, the impulse is a one-line transform on the cited series. Acceptable as a cited transform with the methodology note one click away.
- **Coupon roll math** — average current-stock coupon vs current-auction yield; researcher can compute from DMS Annex + BoC auctions, but the EDR's v1 framing ("coupon roll into a higher-coupon stock") can stand on DMS narrative + the redemption profile table being cited directly. Not a v1 construction requirement.

#### Fiscal — verdict on v1 basics-only feasibility

**Verdict: Fiscal basics CAN stand up on cited DoF / PBO / IMF numbers alone in v1, with two qualifications.**

What stands on direct cite:
- F1 federal deficit YTD + debt-service as % of revenues: direct from Fiscal Monitor line items each month. Ratio is a trivial transform, not a construction.
- F1 PBO vs FES delta: direct comparison of two cited projection vintages. Researcher provides both; writer phrases the gap.
- F2 provincial net debt-to-GDP + budget vs plan: direct from each provincial budget. No construction.
- F2 credit-watch flags: direct from rating-agency press releases.
- F3 GoC issuance trajectory + average term + redemption profile: direct from DoF DMS Annex.
- F4 structural balance / CAPB: **cite IMF Article IV Canada's CAPB or OECD Economic Survey CAPB.** Do NOT construct our own CAPB for v1. The CAPB methodology (output-gap dependent) is a deep-dive deliverable, not a basics ask.

Qualifications:
1. **Coverage gap to close in pipeline is non-trivial.** boc-tracker carried no fiscal at all. The DoF Fiscal Monitor fetch is the highest-priority Wave-2 pipeline build for fiscal; everything else can be researcher-curated by-release for v1 launch.
2. **F4 "consistency with monetary stance" is editorial interpretation.** The data — fiscal impulse from CAPB year-on-year change, monetary stance from M1-M4 — is citable; the conclusion is a writer's call grounded in those citations. Do not promise a quantified "consistency score" in v1.

**Wave 4 deferral candidates (NOT v1 basics):**
- Our own CAPB / structural balance construction (the EDR's "structural balance estimate" language could be misread as our construction; canon intent per Pillar F context is the cited IMF/OECD number, our construction is the deep-dive).
- A normalized debt-service ratio (e.g. cyclically-adjusted, or interest-rate-shock-adjusted) — this is the Pillar F deep-dive territory, not the basics.
- A formal fiscal-monetary consistency index — deep-dive territory.

#### Fiscal — coverage estimate

**0% of Fiscal basics covered by boc-tracker.** boc-tracker had no fiscal coverage at all (confirmed: `policy.html` titled "Monetary Policy"; data dir contains zero DoF / PBO / provincial files; `fetch.py` contains zero fiscal-source references). All four F-elements require new pipeline or curated-by-release work.

---

## Cross-section summary

### Coverage by section

| Section / sub-surface | boc-tracker basics coverage | Headline |
|---|---|---|
| Housing | ~35-40% | National-level price + activity (starts, permits, national SNLR) covered; CMA breakouts, completions, rent, mortgage stack, arrears, pop-to-stock all gaps |
| Policy — Monetary | ~80% | Overnight rate, balance sheet, GoC yields, BoC-Fed primitives all covered; OIS path is the structural gap; neutral-rate is a curated value |
| Policy — Fiscal | 0% | Zero coverage. Fully new build |

### Construction watchlist (all sections, basics-layer only)

Items where v1 basics requires our own derivation, ranked by deferral risk:

**LOW RISK (transforms on covered or cleanly-sourced data, methodology note suffices):**
- Months of inventory by CMA (active listings / sales).
- 6-month annualized HPI (national + CMA).
- Consecutive-meeting action state.
- BoC-Fed spread distribution / regime classification.
- Real policy rate.
- Debt-service as % of revenues.
- Fiscal impulse from cited CAPB.

**MEDIUM RISK (constructed from primary data, but methodology choices are non-trivial and reviewer-visible):**
- Population-to-housing-stock ratio by CMA (numerator + denominator + interpolation choice).
- OIS-implied BoC path (proxy or MPR-cite required; recommend MPR-cite for v1).
- PBO vs FES baseline delta (vintage and apples-to-apples discipline).

**HIGH RISK — defer to deep-dive (Wave 4+):**
- Cyclically-adjusted primary balance (own construction). **For v1: cite IMF/OECD CAPB instead.**
- Mortgage stack by vintage and term (full reconstruction). **For v1: cite BoC chartpack directly.**
- Normalized debt-service ratio. **For v1: report raw, defer normalization.**
- Formal fiscal-monetary consistency index. **For v1: prose-level interpretation.**

### Explicit verdict — Policy Fiscal sub-surface in v1

**Fiscal basics-only is feasible for v1 using cited DoF / PBO / IMF numbers.** The single deferral required is our own CAPB construction — cite IMF Article IV CAPB or OECD CAPB instead, with a methodology footnote naming the source. No other element on the F1-F4 list requires our own construction at the v1 basics bar. The pipeline work is non-trivial (DoF Fiscal Monitor monthly fetcher is the highest-value add; provincial / PBO / DMS can be researcher-curated by-release for launch), but no F-element is structurally blocked.
