# Trade & Tariffs Deep Dive — Insight Base

**Slug:** `us-tariff-repricing`
**Section:** Trade
**Built:** 2026-05-11
**Author:** researcher
**Status:** Source-verified canon for writer drafting. Each bullet ends with a primary-source citation in brackets. `[INFERRED]` = analyst interpretation. `[OPEN]` = unresolved fact needed before publication.

---

## 1. Current US tariff state on Canadian goods (as of 2026-05-11)

### IEEPA tariffs (the "fentanyl/border" tariffs)
- 2025-02-01: Trump EO under IEEPA imposed 25% on non-CUSMA-compliant Canadian goods, 10% on energy and potash; effective 2025-02-04. [Blakes timeline; PwC Canada tax insights]
- 2025-08-01: IEEPA rate on non-CUSMA-compliant Canadian goods raised from 25% to 35%. [BDO Canada]
- 2026 Q1: US Supreme Court ruled IEEPA tariffs unlawful (the "big" decision SEMA dated 2026-09 — verify exact date). CUSMA-compliant goods remain exempt; non-compliant face 10% residual. [Fasken; Norton Rose Fulbright; SEMA] `[OPEN — confirm exact SCOTUS decision date and remedy mechanics; "September 2026" cited by SEMA conflicts with current date 2026-05-11. Likely a different ruling or date error in the source. Writer must reconcile before publishing.]`
- Practical note: 98%+ of Canada-US tariff lines and 99.9% of bilateral trade qualify as CUSMA-compliant when documented. [Tradecommissioner.gc.ca]

### Section 232 (national security) — separate track, NOT covered by IEEPA ruling
- Steel: 50% (raised from 25% on 2025-06-04). [Congress.gov CRS IN12519; STR Trade]
- Aluminum: 50% (raised from 25% on 2025-06-04). [Congress.gov CRS IN12519]
- Copper: 50% on core articles, 25% on derivatives; added 2026-04-06 per 2026-04-02 proclamation. [PwC Canada]
- Autos: 25%. [Tariffstool.com guide; verify against original USTR/Commerce proclamation]
- April 2026 de minimis: goods with ≤15% subject-metal content exempt. [PwC Canada]
- April 2026 relief path: Canadian/Mexican producers can qualify for reduced 232 rates by committing to build primary capacity in US. [Steel Market Update 2026-04-27]

### Softwood lumber (AD/CVD + Section 232 stacking)
- Combined AD/CVD rate: 35.16% currently; preliminary April 2026 review proposes drop to 24.83% (AD 10.66% + CVD 14.17%) pending August/October 2026 final. [Federal Register 2026-04-14; Commerce press release]
- Section 232 lumber: 10% (effective October 2025) stacks on top. [Tirllc commentary]
- **Effective burden today:** 35.16% AD/CVD + 10% S232 = ~45% total. After preliminary cut: 24.83 + 10 = 34.83%. [INFERRED stacking math from cited components]

### Dairy
- USMCA TRQs (tariff-rate quotas) governing; no new 2025-26 tariff escalation found. `[OPEN — confirm no new dairy tariffs; check USTR 2026 reports]`

---

## 2. What's pending: USMCA Joint Review

- **Trigger date:** 2026-07-01 — sixth anniversary of USMCA entry-into-force, per Article 34.7. [Congress.gov CRS R48787 and IF10997; Brookings; Federal Register 2025-09-17]
- US, Canada, Mexico opened domestic consultation processes in September 2025. [Covington & Burling 2025-09]
- USTR public hearing Federal Register notice published 2025-09-17. [Federal Register 2025-18010]
- **Mechanism:** Each party must confirm in writing whether to extend the 16-year term. If all three confirm, USMCA extended to 2042. If any one objects, the agreement enters annual review mode and is set to sunset in 2036. [CRS R48787]
- **Recommendations** for substantive changes must be submitted at least one month before the review (i.e., by 2026-06-01). [CRS R48787]
- **Provisions widely flagged as at risk:** auto rules of origin (regional value content thresholds, labor-value content), dispute settlement (Chapter 31 panels), dairy TRQ expansion, digital trade carve-outs, anti-circumvention. [White & Case; CSIS USMCA Review 2026]

---

## 3. Canada's US export share — decomposition

**Verified from project data** (`data/raw/trade_exports_us.csv`, `trade_exports_total.csv`; both customs basis, SA, CAD mn):

| Period | US share of total Cdn merchandise exports |
|---|---|
| 1997 (avg) | 81.8% |
| 2000 (avg) | 87.0% (peak) |
| 2010 (avg) | 74.9% |
| 2024 (avg) | 76.3% |
| 2026-Jan | 67.7% |
| 2026-Feb | (computed: 68.6%) |
| 2026-Mar | 66.1% |
| Trailing 12mo (to 2026-03) | 69.75% |

- **Headline observation:** US share collapsed roughly 10 percentage points in 12-14 months — from steady ~76% in 2024 to ~66-70% in Q1 2026. [project data, derived above]
- Total exports rose to record CAD 68.8bn in March 2026 (vs ~61bn pre-tariff baseline), so the share decline is *not* purely a US-volume collapse — non-US destinations grew faster. [project data]
- Trade balance with US widened slightly (CAD 7.1bn in Mar-26 vs 6.4bn yr-ago). Overall trade balance flipped from CAD -2.4bn deficit to +1.8bn surplus year-over-year. [project data]
- `[INFERRED]` The 10pp drop combines: (a) genuine demand diversion (Canadian firms shipping to Europe/Asia to escape tariff exposure), (b) front-loading distortions in 2025 reversing in Q1 2026, (c) USD/CAD dynamics affecting denomination. Decomposition by commodity vs destination requires StatCan Table 12-10-0011 pull which is `[OPEN]` — not yet in project raw data.

---

## 4. Sectoral exposures `[OPEN — partial]`

`[OPEN]` — project raw data is bilateral totals only. The writer needs commodity-level breakdowns from StatCan Table 12-10-0011 or 36-10-0489 (value-added in exports). To commission either a one-shot scraper or manual pull.

Provisional sector picture from public/secondary sources:
- **Energy** (crude oil, natural gas): largest single export to US; majority of Alberta/SK GDP exposure. 10% IEEPA rate during 2025; CUSMA-compliant flows largely exempt post-SCOTUS. [BoC June 2025 trade-impact analysis]
- **Autos & parts:** Section 232 25% across the board; Ontario concentration. Auto rules-of-origin are the central USMCA-review battlefield. [White & Case]
- **Steel/Aluminum:** Section 232 50% — most directly exposed. Quebec hydro-aluminum (~60% of NA primary aluminum supply) and Ontario/Hamilton steel concentrated. `[OPEN — confirm Quebec share of NA primary aluminum]`
- **Softwood lumber:** ~45% combined burden today; BC concentrated; smaller export $ than above. [Fed Register; CRS R48781]
- **Agriculture (incl. canola, beef, dairy):** mixed exposure; dairy protected by USMCA TRQs; canola facing China retaliation in parallel issue. `[OPEN]`

---

## 5. Macro pass-through

### Bank of Canada January 2025 MPR scenario (benchmark for analysis)
- Scenario specification: permanent 25% US tariff on all imports incl. Canada; 25% Canadian retaliation. [BoC MPR 2025-01-29, In-Focus 1]
- Benchmark calibration: Canadian GDP growth in Year 1 is **~2.5 percentage points lower** than counterfactual. Example: 2% growth path becomes -0.5% Year 1, +0.5% Year 2. [BoC MPR 2025-01-29]
- Tariff pass-through to consumer prices is initially low, rises over three years (baseline full pass-through over 3 yrs). [BoC MPR 2025-01-29]
- BoC July 2025 MPR update: actual realized tariffs (mostly Section 232 + initial IEEPA) had limited inflation effect to date; core inflation rose from ~2% (H2 2024) to ~2.5% (June 2025), mostly non-energy goods. [BoC MPR 2025-07-30]
- BoC June 2025 staff analytical note on US trade policy impact on jobs and inflation. [bankofcanada.ca/2025/06/the-impact-of-us-trade-policy-on-jobs-and-inflation-in-canada]

### Tiff Macklem speech on tariffs and structural change
- 2025-02 speech "Tariffs, structural change and monetary policy" — laid out the framework that tariffs are a supply-side shock requiring the BoC to distinguish one-time price-level effects (look through) from second-round expectations (respond). [bankofcanada.ca/2025/02/tariffs-structural-change-and-monetary-policy]

### Terms of trade `[OPEN]`
- No quantified terms-of-trade decomposition assembled here. The writer should commission a calc using StatCan terms-of-trade index (Table 36-10-0103) once sectoral export data is in. `[OPEN]`

---

## 6. BoC reaction function for tariff shocks

- **Stated principle (Macklem, Feb 2025):** Look through first-round price-level effects; respond if inflation expectations de-anchor or wage-price dynamics emerge. [BoC speech 2025-02]
- **Revealed behaviour:** Policy rate held at 2.75% in April 2025 with explicit reference to tariff uncertainty constraining forward guidance. [BoC FAD 2025-04-16 press release]
- BoC has presented **scenario** analysis (vs point forecast) in 2025 MPRs precisely because tariff path is unknowable — first time since COVID. [BoC MPR 2025-04-16 risks section; MPR 2025-07-30]
- `[INFERRED]` This is the most important behavioural shift to flag: BoC has effectively widened its tolerance band for headline inflation conditional on tariff source — a meaningful change in reaction function that's not always made explicit in commentary.

---

## 7. Three scenarios for 2026-07-01 onward

### A. Base case — USMCA renews on broadly current terms
- All three parties confirm 16-year extension to 2042. Section 232 tariffs persist (those are independent of USMCA). Lumber AD/CVD continues in regular review cycle. [INFERRED from CRS R48787 mechanics]
- Canadian export composition stabilizes at ~70-72% US share — partial unwind from current 66-70% as Q1 distortions fade. `[INFERRED]`

### B. Tail — USMCA fractures
- One party (most plausibly US) declines to extend → annual reviews begin, sunset trajectory to 2036, but immediate reversion is not automatic. [CRS R48787]
- If political dynamics push toward MFN reversion, average Canada→US tariff jumps from ~3% (CUSMA preference erosion) to ~3-5% MFN average; sectoral peaks much higher. `[OPEN — need WTO MFN schedule for Canada-US trade-weighted average]`

### C. Selective sectoral escalation without USMCA collapse
- Most likely 2026-2027 outcome `[INFERRED]`: aluminum, lumber, auto rates further adjusted via Section 232 or 301; USMCA structure preserved as political cover.
- Implication for analysis: BoC's tariff scenario work is calibrated to broad 25% — sectoral shocks deliver smaller GDP hit but more concentrated provincial pain (QC aluminum, BC lumber, ON auto).

---

## CLAIM LADDER — candidate load-bearing theses for the writer

Ranked by contestable-ness × defensibility from this source base:

1. **The 10-point US export share drop in 14 months is the largest peacetime reorientation of Canadian trade since the late-1980s FTA negotiations.** Defensible from project data (verified above); contestable because it could be reversed by 2026-H2 if tariffs de-escalate. Load-bearing because it reframes the deep dive from "tariff cost" to "structural reorientation."

2. **BoC's reaction function has shifted: it has widened its tolerance band for tariff-driven inflation in a way it has not formally announced.** Defensible from comparing 2025-04 FAD language to pre-2025 policy framework; contestable because BoC would dispute the framing. High payoff if defended carefully.

3. **The single most important tariff number for Canadian macro is not the 25% IEEPA headline but the 50% Section 232 aluminum/steel rate — because it is durable, sector-concentrated, and untouched by the IEEPA SCOTUS ruling.** Defensible from legal-track distinction.

4. **USMCA's joint review is structurally biased toward continuation, not renegotiation** — the unanimity requirement for changes means default = extension. The market narrative of "USMCA renegotiation 2026" overstates the binary risk. [CRS R48787 mechanics]

5. **Canada's exposure is more provincial than national.** A 25% aluminum tariff that lops 0.3% off national GDP can lop 2-3% off Quebec aluminum-region GDP. The national-aggregate macro framing understates political-economy risk. `[INFERRED — needs provincial GDP-by-sector pull to defend numerically]`

---

## CHART SPECIFICATIONS for the writer

1. **"The reorientation"** — Canada US export share, monthly, 1997-present.
   - Data: `data/raw/trade_exports_us.csv` ÷ `trade_exports_total.csv`.
   - Visual: line chart, single series, with shaded bands at 75% (post-FTA norm) and 85% (NAFTA peak). Annotate 2001 peak, 2009 trough, 2026-Q1 break.
   - Cadence: monthly. Window: 1997-present.
   - Framework Q3.

2. **"Total exports kept rising while US share fell"** — dual-axis: total exports (CAD bn, bars) and US share (%, line), monthly.
   - Data: same two project files.
   - Window: 2023-01 to 2026-03.
   - Visual: combo chart; annotate Section 232 escalations (June 2025) and IEEPA imposition (Feb 2025).
   - Framework Q3.

3. **"The tariff stack on lumber"** — stacked horizontal bar showing softwood lumber rate components: AD + CVD + Section 232. Two bars: pre-April-2026 (35.16 + 10 = 45.16%) and post-preliminary (24.83 + 10 = 34.83%).
   - Data: hand-coded from Federal Register / Commerce announcements.
   - Visual: stacked bar; sourced footnote with FR document numbers.
   - Framework Q1.

4. **"What's actually in force on Canadian goods"** — small-multiples table-as-chart: rows = sector (energy, autos, steel, aluminum, lumber, dairy, other), columns = tariff regime (IEEPA non-compliant, Section 232, AD/CVD), cells = current rate or "exempt."
   - Visual: heat-map / matrix.
   - Framework Q1.

5. **"BoC's 25% scenario vs realized path"** — line chart with two GDP-growth tracks: BoC January 2025 MPR scenario benchmark (Year 1 -0.5%, Year 2 +0.5%) vs realized Statistics Canada GDP growth quarters 2025-Q1 through 2026-Q1.
   - Data: BoC MPR Jan-2025 scenario table + StatCan Table 36-10-0104 (GDP).
   - Visual: line chart, two series; shaded "scenario band."
   - Framework Q5.

6. **"The USMCA review calendar"** — horizontal timeline 2025-2026 with key dates: Sep 2025 USTR consultations open → June 2026 recommendations deadline → July 1 2026 joint review → confirmation deadline.
   - Visual: timeline graphic.
   - Framework Q2.

7. **"US share by province" `[OPEN — needs data pull]`** — bar chart, US share of merchandise exports by province (latest year).
   - Data: StatCan Table 12-10-0099 or equivalent provincial trade detail.
   - Framework Q4.
   - `[OPEN]` Defer if data pull not feasible.

---

## OPEN QUESTIONS — must close before publication

1. SCOTUS IEEPA ruling exact date and remedy mechanics. SEMA's "September 2026" date conflicts with today's 2026-05-11. Verify before any prose claim about post-SCOTUS state.
2. Commodity-level Canadian export decomposition (StatCan 12-10-0011) — needed for sectoral exposure quantification.
3. Provincial GDP-by-export-sector — needed for Claim 5.
4. Auto Section 232 — exact rate verified against original USTR/Commerce proclamation, not third-party summaries.
5. Quebec share of North American primary aluminum supply — flagged in Sec 4 sectoral.
6. Canada-US MFN trade-weighted average tariff — needed for Scenario B quantification.
7. Dairy: confirm no new 2025-26 escalation; check USTR 2026 reports.

---

## CITATIONS (URLs)

**US tariff actions:**
- IEEPA SCOTUS ruling: https://www.fasken.com/en/knowledge/2026/02/us-supreme-court-rejects-ieepa-tariffs ; https://www.nortonrosefulbright.com/en/knowledge/publications/99029733/
- Blakes Canada-US tariff timeline: https://www.blakes.com/insights/us-canada-tariffs-timeline-of-key-dates-and-documents/
- Section 232 CRS: https://www.congress.gov/crs-product/IN12519
- Steel Market Update relief path: https://www.steelmarketupdate.com/2026/04/27/us-opens-new-s232-tariff-relief-path-for-canadian-and-mexican-producers/
- PwC Canada steel/aluminum/copper tariff insights: https://www.pwc.com/ca/en/services/tax/publications/tax-insights/us-tariffs-steel-aluminum-copper-imports-2026.html
- BDO Canada non-CUSMA 35%: https://www.bdo.ca/insights/non-cusma-compliant-goods-subject-to-35-tariffs-effective-august-1-2025

**Softwood lumber:**
- CRS softwood lumber: https://www.congress.gov/crs-product/R48781
- Federal Register 2026-04-14: https://www.federalregister.gov/documents/2026/04/14/2026-07154/
- Global Affairs Canada softwood recent: https://www.international.gc.ca/controls-controles/softwood-bois_oeuvre/recent.aspx?lang=eng

**USMCA review:**
- CRS R48787: https://www.congress.gov/crs-product/R48787
- CRS IF10997: https://www.congress.gov/crs_external_products/IF/HTML/IF10997.web.html
- Federal Register 2025-09-17 USTR notice: https://www.federalregister.gov/documents/2025/09/17/2025-18010/
- Brookings: https://www.brookings.edu/articles/the-us-has-formally-started-joint-review-of-usmca/
- CSIS USMCA Review 2026: https://www.csis.org/analysis/usmca-review-2026
- White & Case: https://www.whitecase.com/insight-alert/north-america-prepares-2026-usmca-review-and-potential-renegotiation

**Bank of Canada research:**
- MPR 2025-01-29 (tariff scenario): https://www.bankofcanada.ca/publications/mpr/mpr-2025-01-29/in-focus-1/
- MPR 2025-07-30: https://www.bankofcanada.ca/publications/mpr/mpr-2025-07-30/
- MPR 2025-10-29: https://www.bankofcanada.ca/publications/mpr/mpr-2025-10-29/
- MPR 2026-01-28: https://www.bankofcanada.ca/wp-content/uploads/2026/01/mpr-2026-01-28.pdf
- Macklem 2025-02 speech: https://www.bankofcanada.ca/2025/02/tariffs-structural-change-and-monetary-policy/
- BoC trade-policy impact note (Jun 2025): https://www.bankofcanada.ca/2025/06/the-impact-of-us-trade-policy-on-jobs-and-inflation-in-canada/
- FAD 2025-04-16: https://www.bankofcanada.ca/2025/04/fad-press-release-2025-04-16/

**StatCan data:**
- Table 12-10-0011 (international merchandise trade by partner): https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1210001101
- Project data sources: `data/raw/trade_exports_us.csv`, `trade_exports_total.csv`, `trade_balance_us.csv`, `trade_balance_total.csv` (all StatCan PID 1210011901, customs basis, SA)
