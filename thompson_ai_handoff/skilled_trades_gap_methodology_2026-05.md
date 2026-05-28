# Skilled-Trades Gap vs. Build-Big — Methodology Feasibility Note (2026-05)

Author: research desk. Status: methodology + feasibility scoping (NOT execution). All quoted coefficients verified at footnoted URLs unless flagged.

---

## 1. TL;DR

**Is the piece feasible?** Yes — but only as a "**defensible-range gap with named uncertainty bands**" piece, not as a single point estimate. The demand-side data is patchy: of the ~15 MPO-referred projects, fewer than half have public, project-specific construction-workforce profiles, and almost none publish a Red-Seal-trade decomposition. The supply-side data is much better — BuildForce 2025–2034 forecast is the consensus reference, and supplements (immigration, mobility, productivity) are individually estimable. The honest framing is: "Even using BuildForce's own scenario and the project portfolio's own labour estimates, the gap by 2028–2030 in welders, pipefitters, electricians, and ironworkers is X, and the federal Team Canada Strong response is sized for ~Y. Here is what would have to be true for the gap to close." That piece is publishable; a single "X welders by 2028" headline number is achievable as the chart's titled finding, but the deck behind it has to carry ranges.

**Is the methodology defensible?** Yes, conditional on three discipline points: (a) every project-level coefficient cited to a specific EA filing, IBA, or industry-study URL — no proxy reasoning hidden in spreadsheets; (b) BuildForce's published baseline used as the supply anchor with explicit Build-Big adjustment, not a Sibley-built parallel model; (c) the demand-side "Build-Big incremental" computed against BuildForce's own *existing* major-projects assumptions so we don't double-count what BuildForce has already absorbed. The cleanest analogue is **Infrastructure Australia's annual Market Capacity Report** — same architecture: pipeline → trade-by-jurisdiction demand → shortfall vs supply scenarios. That methodology survived four years of peer scrutiny in Australia. No Canadian equivalent exists; **first-mover position is real**.

**What's the rough answer likely to be?** The piece will most plausibly find a structural shortage in **3–4 specific trades** (welders/pipefitters in BC and Alberta 2026–2029; electricians and instrumentation in Ontario 2027–2031; ironworkers and millwrights nationally 2026–2030) on the order of **15,000–35,000 person-years per trade-province-year combination** at peak concurrence, against a Team Canada Strong response sized at ~16,000–20,000 net incremental Red Seal workers per year nationally across all 56 designated trades. The gap doesn't close at any wage in the 2026–2030 window because the apprenticeship pipeline takes 3–5 years per trade; wage-clearing is partial via interprovincial mobility but a non-trivial share of MPO project schedules slips by 6–18 months as a result. **That's the publishable finding if the data supports it.**

**Biggest risk to the finding.** Three: (i) BuildForce's "Major Projects" submodule may *already* include most of the MPO portfolio, in which case the "Build-Big incremental" we layer on is small and the gap shrinks; (ii) productivity gains from modularization in housing (Deloitte cites ~40% manpower reduction at industrial scale, [MPA Magazine](https://www.mpamag.com/ca/mortgage-industry/industry-trends/modular-construction-offers-a-path-to-closing-canadas-housing-gap/575663)) could close a meaningful share of the housing-side gap; (iii) project schedule slippage is endogenous to the labour constraint itself — if welders are scarce, projects don't break ground; the gap then never realizes as a hire-rate shortfall but as deferred capex, which is a different (and weaker) headline.

---

## 2. Demand-side modelling

### 2.1 Labour-intensity coefficients by project category — what's verified vs what isn't

| Project category | Peak workforce | Person-years | Trade breakout | Source quality |
|---|---|---|---|---|
| **Major pipelines** (TMX-class) | TMX: ~8,600 peak (Feb 2020); CGL: ~6,000 peak | TMX: **67,423 person-years** over 2018–2023 / ~58,037 person-years (Conference Board) | Mixed (Trans Mountain disclosed "operating engineers, labourers, plumbers, pipefitters, teamsters"; **up to ~20% apprentices** by company admission) | **B-grade**: aggregate strong, trade breakouts weak |
| **LNG export facilities** (Phase-1 class) | LNG Canada Phase 1: ~7,500 peak (some sources 9,400 with shift roll) | Not aggregated publicly | Confirmed welders/pipefitters/electricians/heavy-equipment operators; "more than 380 pipe welders" cumulative | **B-grade** for aggregate; weak for time-phased decomposition |
| **Smaller LNG** (Cedar / Ksi Lisims class) | Cedar: ~500 peak; Ksi Lisims: ~800 peak; 450 avg | Implied modest (300 full-time construction) | Trade categories named but not quantified | **C-grade**: EA-disclosed but high-level |
| **Nuclear SMR** (Darlington BWRX-300, 4-unit) | OPG: ~700 new hires per first phase; **~18,000 jobs/yr fleet average** | Not disclosed in person-years | Confirmed iron workers, millwrights, boilermakers as first cohort | **C-grade**: OPG fleet figures are net of unit-by-unit profile |
| **Nuclear refurbishment** (Pickering 5–8, Bruce C) | Bruce C: ~18,900 over construction; Pickering: ~37,000 total jobs ([Ontario release](https://news.ontario.ca/en/release/1006772/ontario-greenlights-pickering-nuclear-generating-station-refurbishment-to-create-nearly-37000-jobs)) | Provincial press releases only | None disclosed by trade | **D-grade**: press-release sums |
| **Transmission line (HV)** | US literature: **~27 direct jobs/mile** (~17 jobs/km) for major builds ([CleanEnergyGrid](https://www.cleanenergygrid.org/transmission-and-jobs/)) | Not aggregated for Canadian projects | Confirmed: ironworkers, linemen, heavy-equipment operators, surveyors | **C-grade**: US figures, no Canadian equivalent disclosed publicly |
| **Major hydro** (Site C-class) | Site C: **~5,181 peak** (Oct 2021); **~8,000 person-years** for main civil works contract over 8 years | Confirmed for Site C only | Disclosed: most are heavy-equipment operators + entry-level skilled labour; "fewer than 100 in various trades" each (boilermakers, welders, millwrights) | **A-grade for Site C**; **D-grade** for generalization |
| **Critical minerals mining (greenfield)** | Foran McIlvenna Bay: no public peak workforce | Not aggregated by project | None disclosed | **D-grade** |
| **CCS infrastructure** (Pathways) | ~100,000 jobs claimed total ($16.5B GDP during construction) | Not split out by trade or year | None disclosed by trade | **D-grade**: government/proponent headline only |
| **Residential housing** | N/A | Deloitte: **58,000 additional workers in 2026 rising to 290,000 by 2030** (housing alone) ([Deloitte](https://www.deloitte.com/ca/en/our-thinking/future-of-canada-center/builders-baby-builders-the-half-a-million-worker-question.html)) | Categories named (electricians, welders, crane operators, concrete crews) but not quantified | **B-grade**: top-line credible, decomposition weak |
| **Non-residential institutional (BCSF-class)** | N/A | Folded into BuildForce non-residential | None | **B-grade**: in BuildForce aggregate |

**Sources for the verified-good cells:**

- TMX: Trans Mountain's own "Economic Benefits: Jobs & Procurement" brochure ([transmountain.com](https://docs.transmountain.com/1499466826-Economic-Benefits-Jobs_Procurement.pdf)); EY Economic Impact Assessment ([EY-TMEP](https://docs.transmountain.com/EY-Report_TMEP_EN.pdf)); Conference Board reference cited at 58,037 person-years over 7 years from 2012. Narwhal explainer notes Kinder Morgan's earlier NEB filing was **2,500 workers/yr for two years** — much lower than the headline 15,000 figure ([Narwhal](https://thenarwhal.ca/search-trans-mountain-s-15-000-construction-jobs/)).
- LNG Canada Phase 1: Fluor case study + LNG Canada workforce page ([Fluor](https://www.fluor.com/projects/lng-canada-export-facility); [lngcanada.ca](https://www.lngcanada.ca/commitments/workforce-development/)); first cargo June 2025; peak ~7,500–9,400 depending on shift-roll counting.
- Site C: BC Hydro contract documentation; Alaska Highway News tracking ([Alaska Highway News](https://www.alaskahighwaynews.ca/regional-news/site-c/site-c-workforce-nears-5000-3935216)); Narwhal investigative piece on job-number accounting ([Narwhal](https://thenarwhal.ca/digging-truth-site-c-dam-job-numbers/)).
- Cedar LNG: BC EAO; project site ([Cedar LNG](https://www.cedarlng.com/project/)).
- Ksi Lisims: BC EAO; gov.bc.ca release ([BC release](https://news.gov.bc.ca/releases/2025ENV0032-000878)).
- Darlington SMR: OPG project pages; ANS Nuclear Newswire on construction permission ([ANS](https://www.ans.org/news/2025-05-12/article-7014/opg-gets-final-permission-to-construct-first-north-american-smr/)).
- Pathways Alliance: Wikipedia summary referencing 100,000 jobs / $16.5B GDP claim — **this figure is a proponent claim and should not be treated as verified**; needs primary triangulation against Pathways Alliance disclosure or independent industry analysis before use.
- Coastal GasLink: TC Energy + project FAQ; "up to 6,000 workers during peak summer" ([TC Energy](https://www.tcenergy.com/operations/natural-gas/coastal-gaslink/)).

### 2.2 Build-Big project portfolio aggregation — the assembly problem

**The 15 MPO-referred projects** (per `build_big_answered_vs_open_2026-05.md`): roughly LNG Canada Phase 2; Darlington New Nuclear (SMR 4-unit); Port of Montréal Contrecœur; McIlvenna Bay Foran Copper Mine; one unnamed; major HV transmission line + LNG export facility (BC); three mines (nickel ON, graphite QC, tungsten NB); first hydroelectric dam in Nunavut; Grays Bay Road and Port; Mackenzie Valley Highway; plus two more. **Plus** the Carney–Smith pipeline (Alberta-to-BC oil) referred separately; **plus** Pathways Alliance CCS; **plus** Bruce C nuclear and Pickering 5–8 refurbishment in Ontario.

For each project the demand-side workforce estimate has to be:

1. **Time-phased** — site mobilization (~10–15% of peak) → ramp (50%) → peak (100%) → demobilization (40% → 10%) → operations. Most EA documents present *peak* and *operational* numbers but not the year-by-year profile.
2. **Trade-decomposed** — for Sibley's headline (e.g., "welders by 2028"), each peak number must split into Red Seal categories. **This is where the data is thinnest.** TMX and Site C have some disclosure; LNG Canada and CGL have category lists without quantification; SMR-class is barely public.
3. **Geographically tagged** — Alberta (pipeline + LNG feedgas + CCS + oilsands sustaining); BC (LNG + transmission + Site C tail + Cedar/Ksi Lisims); Ontario (SMR + transmission + Contrecœur + Pickering); Quebec (Contrecœur + mines); North (Grays Bay + Mackenzie + Nunavut hydro).
4. **Aggregated across concurrent peaks** — the key methodological move. The same welder cannot weld on TMX, Coastal GasLink Phase 2, *and* the Western Energy Corridor pipeline simultaneously. Inter-provincial mobility eases this but does not eliminate it. **Concurrent-peak overlap is the chart's central finding** — when the Western Energy Corridor (target construction start Sep 2027) coincides with Pathways CCS pipeline-build (2027–2030 if it proceeds) and LNG Canada Phase 2 (mid-decade), the BC + Alberta welder pool gets simultaneous bids.

**Proposed approach to assembly**:

For each Red Seal trade × each year 2026–2033 × each province:
- Demand_baseline = BuildForce 2025–2034 forecast value (province × occupation × year), with the major-projects submodule active.
- Demand_BB_incremental = sum across MPO portfolio of (project peak workforce) × (trade share) × (time-phase weight for year Y) × (province assignment), **only for projects not already in BuildForce's major-projects assumption set**.
- Supply_baseline = BuildForce 2025–2034 supply forecast (apprenticeship completions + recruits under 30 + immigrant inflows + interprovincial entry).
- Supply_supplements = additional inflows attributable to Team Canada Strong, Express Entry skilled-trades stream above BuildForce baseline, accelerated CFTA mobility above baseline, modular-construction productivity reduction in housing demand.

The gap = Demand_baseline + Demand_BB_incremental − Supply_baseline − Supply_supplements.

**The critical methodological audit step:** before assembling, write to BuildForce and ask which MPO projects are in their 2025–2034 baseline major-projects submodule. If LNG Phase 2, Darlington SMR, and the Western Energy Corridor are already in their model, the Build-Big "incremental" is much smaller than the headline implies. If they're not, the gap math gets bigger. **This is the cheapest single test that distinguishes the piece's leading from the second-leading hypothesis.**

### 2.3 Geographic considerations — is the labour market one market or many?

The CFTA labour-mobility provisions came into force January 1, 2026 ([Canada Gazette SI/2025-107](https://gazette.gc.ca/rp-pr/p2/2025/2025-11-19/html/si-tr107-eng.html)). The Red Seal endorsement is mutually recognized across all provinces ([Red Seal](https://www.red-seal.ca/eng/about/pr.4gr.1m.shtml)). **In principle, a certified welder in Newfoundland can work in Kitimat or Fort McMurray.** In practice:

- 56 designated Red Seal trades only; some construction trades remain provincially-only certified ([Red Seal](https://www.red-seal.ca/eng/about/pr.4gr.1m.shtml)).
- Mobility friction is real: cost of relocation, family ties, housing availability in Kitimat or Lac-Megantic or Fort St. John. The SEU 2026 raised the Labour Mobility Deduction from $4,000 to $10,000 and dropped the minimum-distance threshold from 150km to 120km — federal acknowledgement that frictions bind ([Budget 2026 ch 2](https://budget.canada.ca/update-miseajour/2026/report-rapport/chap2-en.html)).
- Empirical: a Springer paper ([Springer](https://link.springer.com/article/10.1007/s12061-022-09445-3)) documents that **interprovincial mobility among construction workers is concentrated in Alberta (in-migration) during boom phases**; during bust phases the workers go home. Historical pattern: Alberta peaks in 2014 had ~30,000 trades workers + 20,000 support, of whom a meaningful share were from Atlantic Canada.

**For the gap chart**: treat the Canadian labour market as **partially unified** — model a mobility-elasticity coefficient (how much does an X% wage premium in Alberta over Ontario draw welders from Ontario) drawn from the BoC or Tombe literature on internal migration, then test the gap under (a) zero mobility (most conservative), (b) historical-baseline mobility, (c) frictionless mobility (most optimistic).

### 2.4 Demand-side authority and what's published

**Searched, not found:** No published Canadian bottom-up Build-Big skilled-trades demand study exists at project-decomposed × trade-decomposed × year-decomposed granularity. 

**What exists:**
- **Deloitte "Builders, Baby, Builders"** ([Deloitte](https://www.deloitte.com/ca/en/our-thinking/future-of-canada-center/builders-baby-builders-the-half-a-million-worker-question.html)) — top-down: housing + public infrastructure + private investment streams, with constant-productivity vs 10%-productivity scenarios. Total: 410K-520K additional workers needed by 2030. Explicitly **excludes mining and oil & gas** from scope. No trade decomposition published. **Closest existing public artifact to what Sibley would produce; methodology disclosure is partial.**
- **BuildForce Canada 2025–2034** ([BuildForce press release](https://www.buildforce.ca/en/press-release/renewed-residential-activity-and-ongoing-work-on-major-non-residential-projects-elevate-construction-demands-to-2034/)) — supply-side anchor. Forecasts 380,500 hiring need over the decade vs 272,200 recruits = 108,300 shortfall. Has a "Major Projects" submodule but **the alternative high-case scenario specific to Build Canada is not public**.
- **Conference Board of Canada — "Emissions Reduction and Demand for Skilled Trades" (Aug 2025)** ([Conference Board](https://www.conferenceboard.ca/product/emissions-reduction-and-demand-for-skilled-trades_aug2025/)) — scenarios for emissions-policy impact on trade demand. Not Build-Big specifically but methodology overlap. **Paywalled, requires verification of substance.**
- **Conference Board "Skilled Trades Shortage and Rising Building Costs" (Nov 2025)** ([Conference Board](https://www.conferenceboard.ca/product/skilled-trades-shortage-and-rising-building-costs_nov2025/)) — cites $2.6B GDP loss in 2024 from the workforce gap; projects shortage at 32,000 by 2045 with 2.3% price impact and $7.9B/yr cost to residential renovations. **Closer to Sibley's framing but not Build-Big-decomposed.**
- **Canada's Building Trades Unions / Sean Strickland — ARC Energy interview** ([ARC Energy](https://www.arcenergyinstitute.com/building-at-record-speed-does-canada-have-the-workforce/)) — Strickland explicitly calls for "trade demand profiles" for every MPO-referred project. His framing: **the bottom-up profile data does not exist in published form for Build-Big**. This is Sibley's opening.
- **CIBC Thought Leadership** ([CIBC](https://thoughtleadership.cibc.com/article/building-the-future-why-a-robust-skilled-trades-industry-is-vital-for-canada/)) — bank framing; useful for benchmarking but not a citable Sibley source per editorial discipline.
- **RBC "Powering Up"** ([RBC](https://www.rbc.com/en/economics/canadian-analysis/featured-analysis/insights/powering-up-preparing-canadas-skilled-trades-for-a-post-pandemic-economy/)) — same; benchmark, not citation.
- **PBO** — has not produced a bottom-up Build-Big trades demand model. Their assessment of Team Canada Strong is supply-program scoring only.
- **BuildForce blog (Apr 2024)** ([Building Excellence](https://buildingexcellence.ca/2024/04/22/women-indigenous-people-and-immigrants-increasingly-important-to-construction-trades/)) — Indigenous workers 4.4% of construction (vs 3.4% all-industry); women 13.6% of construction (vs 47.2% all-industry, ~5% on-site); newcomers ~20%.

**Inference:** Sibley's piece is the **first comprehensive bottom-up Build-Big-specific trades-decomposed gap analysis in Canada**, sitting between Deloitte's top-down (which excludes oil & gas), BuildForce's full supply-side (which lacks Build-Big-specific demand uplift), and Conference Board's emissions-policy frame (which is adjacent, not on-axis). That gap in the literature is real, and the first-mover citation value is high.

---

## 3. Supply-side modelling

### 3.1 BuildForce as baseline

BuildForce Canada's 2025–2034 forecast is the consensus reference. Key public numbers:

- 270,000 retirements over the decade (~21% of current 1.3M workforce).
- Demand growth: +111,600 workers needed.
- Total hiring need: 380,500.
- Expected first-time entrants under 30: 272,200.
- Implied shortfall: **108,300 workers** by 2034.

Source: [BuildForce press release](https://www.buildforce.ca/en/press-release/renewed-residential-activity-and-ongoing-work-on-major-non-residential-projects-elevate-construction-demands-to-2034/); methodology: [BuildForce About the Data](https://www.buildforce.ca/en/about-the-data/) — Labour Market Information Program, used since 2005, pioneered by Construction Owners Association of Alberta and Commission de la construction du Québec.

**Methodological caveat from BuildForce themselves** ([Daily Commercial News forecast story](https://canada.constructconnect.com/dcn/news/economic/2025/04/buildforce-national-forecast-boom-or-bust-uncertainty-reigns-supreme-for-construction-amid-tariffs)): "investment trends and employment projections were developed with industry input prior to the emergence of potential trade tensions." Meaning: the **2025 forecast vintage predates the US tariff escalation and most of the Build-Big designation tranches**. By the **2026 vintage** (likely March/April 2026 release), BuildForce will have absorbed some of this — Sibley should target the new vintage if it's out before publication.

**Province-level shortfalls referenced**: Ontario projected at **52,000-worker shortfall by 2034** ([Link2Build](https://link2build.ca/news/articles/2025/april/buildforce-canada-outlook-projects-shortfall-of-52-000-workers-in-ontario-by-2034/)) — Ontario alone is ~half the national shortfall, reflecting nuclear refurbishment + transmission + housing concentration.

### 3.2 Supplements needed beyond BuildForce

**Immigration through Express Entry + PNP construction streams:**
- BuildForce baseline already assumes "nearly 4.4M new immigrants 2025–2034" feeding into general labour-force growth ([Building Excellence](https://buildingexcellence.ca/2024/04/22/women-indigenous-people-and-immigrants-increasingly-important-to-construction-trades/)).
- BC's PNP has explicit construction-trades streams tied to major-project delivery ([WelcomeBC](https://www.welcomebc.ca/immigrate-to-b-c/about-the-bc-provincial-nominee-program/the-bc-provincial-nominee-program)).
- Federal PR target reduced from 395K (2025) to 380K/yr through 2027–28 (`build_big_answered_vs_open_2026-05.md` §P), with economic-immigration share rising 59% → 64%. Temp residents cut 673K → 385K → 370K.
- **Net effect for trades supply is ambiguous.** The TFW cut (82K → 60K) directly removes labour from low-skill construction; whether the Express Entry trades stream net-adds to *Red Seal* trades faster than that is the empirical question. **No published model reconciles this**.

**Interprovincial mobility (CFTA-enhanced post Jan 1, 2026):**
- The mobility-friction relaxation is recent. Historical pattern is captured in Springer 2022 paper above. Empirical response post-Jan 2026 will not be measurable in StatCan data until late 2026 at earliest.
- Sibley should treat this as **a sensitivity-band parameter**, not a point estimate.

**Apprenticeship completion rates:**
- 2024: 100,000 new apprentices registered; only ~34,000 completed; **19.9% completion rate** ([CBC](https://www.cbc.ca/news/canada/apprenticeships-registrations-certifications-9.7021768)).
- Continuation rate 49.2%, meaning the pipeline is large but discontinuation is meaningful.
- Building construction trades complete at 36% (lowest of major trade groups) vs industrial/mechanical at 63%.
- Team Canada Strong's $5K completion bonus + $400/wk technical-training top-up ($16K total) aims at this margin. **Effect-size unmodelled publicly.**

**Retirement wave:**
- BuildForce 270K over decade is the consensus figure.
- Alternative figures: 245,100 over 10 years per Altus ([Altus](https://www.altusgroup.com/insights/how-will-lost-construction-jobs-impact-canada-housing-affordability/)); some sources cite "approximately 700,000 skilled tradespeople by 2028" — this is **across all industries** not just construction. Important not to conflate.
- Geographic skew: BC 38,000 retirees by 2032; Ontario 80,000+ by 2032.
- Demographic anchor: oldest baby boomers reached 65 in 2011; youngest reach 65 in 2030. **Construction retirement wave runs through 2030, then thins.**

**Indigenous and women's participation:**
- Indigenous: 4.4% of construction (above 3.4% economy-wide) but declining (-4.4% Y/Y 2024); concentrated in heavy and civil engineering ([Building Excellence](https://buildingexcellence.ca/2024/04/22/women-indigenous-people-and-immigrants-increasingly-important-to-construction-trades/)).
- Women: 13.6% of construction employment, ~5% on-site; growing 5% Y/Y.
- Realistic trajectory: small absolute contribution to a 100K+ gap, but politically central to government framing. Sibley should include but not overweight.

### 3.3 Productivity / labour-saving factors

**Modular construction (housing):**
- Reduces manpower up to **40%** at industrial scale ([MPA Magazine](https://www.mpamag.com/ca/mortgage-industry/industry-trends/modular-construction-offers-a-path-to-closing-canadas-housing-gap/575663)); 20–50% timeline compression ([newswire/Globe](https://www.theglobeandmail.com/investing/markets/markets-news/ACCESS%20Newswire/594327/canada-s-housing-crisis-demands-a-manufacturing-revolution-the-case-for-modular-and-prefabricated-construction/)).
- Current modular share: ~7.5% of construction market ($5.1B annual value).
- **Cost savings 20–40% only at volume + standardization** — neither exists in Canada at meaningful scale.
- Build Canada Homes mandate emphasizes modular methods.
- **Realistic 2026–2030 productivity-savings range:** 5–15% of housing labour need at the high end; should not be modelled as closing the gap singlehandedly.

**Heavy-construction productivity:**
- Canada's construction-sector labour productivity **declined 37.3%** between 2001 and 2023 per joint StatCan/CMHC study ([MPA Magazine](https://www.mpamag.com/ca/mortgage-industry/industry-trends/modular-construction-offers-a-path-to-closing-canadas-housing-gap/575663)).
- Suggests baseline assumption should be: **productivity is flat to slightly improving over 2026–2030, not delivering net labour savings against demand**.
- Automation in heavy construction (Site C used some; SMR factory-assembly uses substantial): real but bounded. SMR explicitly designed for factory-assembly to compress on-site labour — Darlington fleet at ~18K/yr is far below CANDU-class refurbishment labour intensity.

### 3.4 What Team Canada Strong actually delivers

- $6B over 5 years ([PM release](https://www.pm.gc.ca/en/news/news-releases/2026/04/29/prime-minister-carney-announces-team-canada-strong-nationwide-plan); [Budget 2026 ch 2](https://budget.canada.ca/update-miseajour/2026/report-rapport/chap2-en.html)).
- Target: 80,000–100,000 new Red Seal workers by 2030–31.
- $2B for paid placements + $10K first-year wage subsidy.
- $3.4B for completion: $5K bonus + $400/wk technical-training top-up.
- $331M to modernize training.
- $10K (raised from $4K) Labour Mobility Deduction; 120km threshold (down from 150km).
- **First cohort completion lands 2029–2031** — apprenticeships are 3–5 years.

**Math against the gap:** If the program delivers at the high end of its target (100K over 5 years = 20K/yr), it offsets BuildForce's projected 108K shortfall over the decade roughly 1:1 if extended at that rate. But (a) it doesn't fully arrive until 2030–31, (b) the structural-gap of 20,000+/yr per various sources keeps reopening, (c) **Build-Big incremental demand sits on top of BuildForce's baseline**, which Team Canada Strong was sized against. The arithmetic is tight to negative depending on how much of Build-Big BuildForce already has in baseline.

---

## 4. Gap analysis structure

### 4.1 Time-phased gap by year and by trade

The natural output is a **multi-dimensional matrix**: trade × year × province × supply scenario × demand scenario.

For publication, **collapse to one chart** that the headline number lives on. Options ranked:

**Option A (recommended):** 100% stacked supply-vs-demand chart for **the four binding trades** (welders, pipefitters, electricians, ironworkers/millwrights) across **2026–2030**, with a small-multiples panel showing each trade × low/central/high gap scenario. Headline: "Canada has X welders for Build-Big; the project portfolio needs Y; gap is Z."

**Option B:** Provincial heatmap — gap as % of trade supply by province × year. Headline: "Alberta's welder gap peaks 2028 at ~40% of supply." Visually appealing; harder to defend a single number.

**Option C:** Implied project-schedule-delay chart — convert gap into delay months. Methodologically harder; requires assuming labour is the binding constraint (often it isn't — Indigenous consultation, regulatory throughput, capital markets are also binding). **Not recommended as primary chart.**

**Recommended single-number framing:** *"Build-Canada's project portfolio implies peak demand of X,XXX welders / pipefitters / electricians / ironworkers in [province] in [year]. The supply forecast under Team Canada Strong delivers Y,YYY. The gap is Z,ZZZ and does not close at any wage by [year] because the apprenticeship pipeline is 3–5 years."*

### 4.2 What does the gap mean operationally

Three honest framings, ranked by defensibility:

1. **"Implicit construction-cost inflation"** — if labour is scarce, wages rise, project capex rises. Most defensible because every project owner experiences it. Statistic anchor: residential building costs rose ~80% 2017–2025, several multiples of CPI ([StatCan, in Globe coverage](https://www.theglobeandmail.com/opinion/editorials/article-how-to-ease-the-price-squeeze-on-the-construction-industry/)).
2. **"Schedule slippage"** — Sibley says X% of MPO portfolio capex won't move in the announced window. Highly defensible if framed in ranges; less defensible as point estimates.
3. **"Outright cancellation"** — least defensible. Projects rarely cancel for labour alone; they re-bid, delay, or substitute. Avoid.

**Best single-number deliverable**: the gap itself, in worker-years, for the 4 binding trades at peak concurrence, with explicit ranges. Secondary deliverable: implied wage premium needed for clearing (drawn from labour-economics literature on local-supply-elasticity).

### 4.3 Falsification path

If the piece is published and challenged, the attacks would be:

| Attack | Strength | Sibley defence |
|---|---|---|
| "BuildForce already has Build-Big in baseline; you double-counted." | **Strong** | The cheap test: write BuildForce; ask which MPO projects are in 2025/2026 vintage. If most are, Sibley *cannot publish* the piece as is — rescope or kill. |
| "Your project-level coefficients are not Canadian." | Medium | Use only Canadian-disclosed EA / IBA / proponent figures; flag US-derived figures (transmission) explicitly. |
| "Productivity gains (modular) close more of the gap than you allow." | Medium | Show sensitivity to 5/15/30% modular adoption; demonstrate gap remains in welders/pipefitters even at 30% modular adoption (which is unrealistic). |
| "Interprovincial mobility closes more gap than you allow." | Medium | Sensitivity-band; demonstrate Alberta peak demand exceeds national pool of certified welders, not just provincial pool. |
| "Apprenticeship pipeline delivers more than 19.9% completion under Team Canada Strong." | Weak | Even doubling completion to 40% is consistent with the gap remaining open in 2026–2029. The pipeline-timing argument (5-yr cycle) is robust. |
| "Schedule slippage is endogenous; you can't claim the gap." | Medium | Concede this is real; frame deliverable as "implied wage premium or implied delay; one or the other has to give." |
| "Pathways/CCS demand figures are proponent claims." | **Strong if used uncritically** | Triangulate or exclude. |
| "Indigenous court challenges and capital-markets risk are the real binding constraints." | Medium-strong | Acknowledge in piece; argue trades is *additional* binding constraint, not *the* one. |

---

## 5. Comparable prior analyses

### 5.1 International — the methodological models

**Infrastructure Australia Market Capacity Report (2021–2025 series).** The single most relevant analogue. Annual federal/state/local pipeline → workforce-skills supply-demand by jurisdiction × occupation × engineer/trades/PM. Five years of methodological track record. ([Infrastructure Australia](https://www.infrastructureaustralia.gov.au/listing/newsletter/infrastructure-market-capacity-report); [OECD review](https://www.oecd.org/content/dam/oecd/en/publications/reports/2023/04/providing-local-actors-with-case-studies-evidence-and-solutions-places_20b385f4/understanding-infrastructure-market-capacity-constraints-in-australia_ee35e44a/fa8dbdbf-en.pdf)). Methodology partners: Nous Group (workforce modelling consultancy) + GlobalData (project pipeline). 2024 report: shortage of 197,000 infrastructure workers; trades & labour shortages growing fastest. 2025 report follows similar architecture. **Sibley should explicitly position the deliverable as "the Canadian Infrastructure Market Capacity report that doesn't exist yet."**

**US Inflation Reduction Act trades-impact analyses.** Less centralized than Australia. Best public-source: **AGC of America Workforce Survey 2024 + 2025** ([AGC 2024](https://www.agc.org/sites/default/files/Files/Communications/2024_Workforce_Survey_Analysis.pdf); [AGC 2025](https://www.agc.org/sites/default/files/users/user21902/2025%20Workforce%20Survey%20Analysis%20(3).pdf)). 79% of US contractors report difficulty filling carpenters/electricians/pipefitters/welders. The IRA accelerated this — UA Plumbers and Pipefitters apprenticeship grew from 50 to ~200 trainees at IRA-funded battery plants ([Jacobin](https://jacobin.com/2025/05/building-trades-ira-climate-biden); [Portside](https://portside.org/2025-05-25/building-trades-want-save-ira)). IRA labour-hour apprenticeship requirement is 15% for construction starting 2024+. **No single bottom-up IRA-aggregate trades-gap analysis at IA's level of rigour exists.**

**Germany energy transition / UK / France.** Searched briefly; none surfaced as methodological exemplars at IA's level. Australia is the model.

### 5.2 Canadian — past major-project labour analyses

- **Site C labour-tracking** — Narwhal's investigative work ([Narwhal Site C](https://thenarwhal.ca/digging-truth-site-c-dam-job-numbers/)) is the methodological standard for *retrospective* fact-checking of proponent labour claims. Useful as a template for skepticism but not a forecast.
- **TMX** — Narwhal again ([Narwhal TMX](https://thenarwhal.ca/search-trans-mountain-s-15-000-construction-jobs/)) showed Kinder Morgan's NEB filing was 2,500 workers × 2 years vs. public claim of 15,000 jobs. Important precedent: **proponent claims systematically overstate**.
- **Petroleum Labour Market Information (PetroLMI) LNG report (2019)** — pre-Build-Big; methodology useful but data stale.
- **No public Canadian bottom-up Build-Big trades model exists.** Confirmed.

---

## 6. Risks and uncertainty

**Highest-confidence claims Sibley could make:**
1. The bottom-up Build-Big trades gap is not publicly modelled by anyone. (Verified across PBO, Conference Board, Deloitte, BuildForce, RBC, CIBC, ARC Energy Strickland interview.)
2. Welder/pipefitter/electrician/ironworker shortages exist now, will worsen 2026–2029. (Verified across multiple sources.)
3. Team Canada Strong's 80–100K target is at the same order of magnitude as the BuildForce baseline gap, not at the order of Build-Big-incremental demand. (Math verified.)
4. Apprenticeship-pipeline timing (3–5 years) means 2026–2029 trades-supply is largely already-locked-in. (Structural fact.)

**Medium-confidence claims:**
1. Specific peak-demand figures by trade × year × province. (Depends on BuildForce baseline reconciliation.)
2. Implied wage premium / schedule slippage. (Depends on labour-supply elasticity assumption.)
3. Productivity adoption rates (modular share). (Range-based.)

**Low-confidence claims to avoid:**
1. Single point estimate of "X welders needed by 2028, Y supplied, gap is Z." Avoid unless explicit ±band.
2. Pathways CCS-specific labour figures. Avoid until triangulated.
3. Specific impact of Indigenous court challenges on project schedules.
4. Specific BC/Alberta peak-concurrence year — depends on Western Energy Corridor schedule which is currently a target, not a commitment.

**What would falsify the eventual finding:**
1. BuildForce's 2026 vintage absorbs most Build-Big into baseline and shows shortfall closes by 2030.
2. Provinces and industry mount a credible coordinated immigration-throughput response (PNP construction streams scale 5–10x).
3. Modular construction adoption hits 30%+ for housing — closes the housing-side gap.
4. MPO project schedules slip on their own (Indigenous consultation, capital markets) such that peak concurrence never materializes.

The piece's defensibility rests on framing the gap as **conditional on Build-Big proceeding at the announced pace**. If the pace slips for reasons other than trades, the gap shrinks — but Sibley is then publishing the right analysis on the wrong scenario. Best to lead with "if Build-Big proceeds at announced pace" as an explicit conditional, and treat the analysis as a stress test of that scenario.

---

## 7. Recommended execution plan

**Pre-greenlight checks (1–3 days):**
1. **Write BuildForce.** Confirm which MPO projects are in their 2025–2034 baseline major-projects submodule. Ask about the 2026 vintage timing. This is the single most important pre-execution test — if BuildForce already absorbs most of Build-Big, the piece's gap math collapses and Sibley should rescope.
2. **Confirm Conference Board paywalled reports.** "Emissions Reduction and Demand for Skilled Trades" (Aug 2025) and "Skilled Trades Shortage and Rising Building Costs" (Nov 2025) — do these include Build-Big-specific demand? Verify before treating them as prior art Sibley is differentiating against.
3. **Verify Pathways Alliance "100K jobs / $16.5B" with primary disclosure** — currently a press-release figure of unknown methodology.

**If greenlit, work-back schedule (~3–4 weeks to publication):**

**Week 1 — Demand-side assembly.**
- Build project-by-project workforce profile spreadsheet for the 15 MPO projects + Western Energy Corridor + Pathways + Pickering + Bruce C. Each row: project name, capex, capex window, peak workforce (cited URL), trade breakout (cited URL or proxy with note), province, time-phase (mob/ramp/peak/demob) by year.
- Where trade breakout is missing, use a defensible proxy from the Building Construction Sector Council's coefficients for similar project class — but tag every proxy explicitly.
- Aggregate to trade × year × province matrix.

**Week 2 — Supply-side assembly.**
- BuildForce 2025–2034 baseline (or 2026 if available).
- Build supplements: Express Entry + PNP trades, modular productivity, interprovincial mobility scenarios.
- Build Team Canada Strong impact model (apprenticeship completions + wage subsidies × completion-rate uplift assumption).
- Document every assumption with sensitivity bands.

**Week 3 — Gap synthesis + chart.**
- Subtract supply from demand at trade × year × province granularity.
- Identify the binding trades (likely welders, pipefitters, electricians, ironworkers/millwrights).
- Identify peak-concurrence years and provinces.
- Author single-chart deliverable (Option A above): 4 trades × 2026–2030 with low/central/high scenarios.
- Draft headline number with ±band.

**Week 4 — Review gates.**
- Fact-check every project coefficient against its primary URL.
- Style polish.
- Surface-fit (Sibley deep-dive register, 1,000–1,750 words per CLAUDE.md).
- External read by a sympathetic but skeptical industry contact — Sean Strickland at CBTU is the natural choice if introduceable; ARC Energy Institute could be secondary. **Skip Big-Six economists per voice doctrine.**

**Data requirements (must-haves):**
- BuildForce 2025–2034 forecast data (province × trade × year). Subscription or freemium.
- StatCan apprenticeship registration + completion tables (Table 37-10-0137-01 and related).
- LFS construction-sector employment by occupation (Red-Seal-trade-tagged where possible).
- EA filings for every MPO project (publicly available via federal/provincial EA registries).
- IBA disclosures where available (limited).

**Data nice-to-haves:**
- Conference Board emissions-reduction + skilled-trades report (paywalled).
- Custom BuildForce major-projects-submodule scenario run.

**Decision gate at end of Week 1:** If demand-side spreadsheet assembly reveals trade-decomposition coverage is below ~50% of total MPO portfolio capex even with proxies, **rescope** — the piece becomes "what the absence of project-level trade profiles means for executing Build-Big" rather than "the bottom-up gap is X."

---

## 8. Bottom line

The piece is feasible. The methodology is defensible if BuildForce's baseline reconciliation works in Sibley's favour (the cheap test in Week 1 settles this). The answer is most likely a defensible gap of 15K–35K worker-years per binding trade × year at peak concurrence, against a Team Canada Strong supply response sized to maybe half-close the structural baseline gap and not close the Build-Big incremental at all. The Infrastructure Australia Market Capacity Report is the methodological model and the positioning anchor — Sibley is producing "the Canadian Infrastructure Market Capacity Report that doesn't exist yet," and that's both the editorial wedge and the institutional reach hook. The piece is launch-flagship-grade if the BuildForce reconciliation closes cleanly.
