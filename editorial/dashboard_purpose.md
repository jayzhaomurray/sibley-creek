# Dashboard Purpose: Sibley Creek

Foundation document. Authored by editorial-director.
All downstream work (research scoping, prose, charts, design) anchors here.
Quote this doc. Do not reinterpret it.

Project directory and package name remain `macro-research-department` for
continuity of tooling. The publication name is **Sibley Creek**, named
after Sibley Creek on the Sibley Peninsula in Sleeping Giant Provincial
Park (Silver Islet area, Lake Superior). The name signals the
publication's posture: Canadian, geographically specific, quietly
durable, indifferent to fashion.

---

## 1. Mission

**What this is.** Sibley Creek is a standing, opinionated read of the
**Canadian** macro picture, organized as a small set of sections that
mirror how a Canadian institutional desk actually frames the economy,
and refreshed on cadences that match how those sections actually move.
The publication is a **tri-modal product**: a live tracker (daily-
refresh data), automated event blurbs (LLM-generated interpretation
paragraphs on data prints, human-reviewed before publish), and ad-hoc
deep-dive research (human-led long-form pieces on the eight pillars).
The three modes share one set of sections, one voice, one canon. It
exists to help a reader who already knows the basics form a sharper
view of Canada than the median Big-Six economics note: where the Bay
Street consensus on the BoC, the housing cycle, the mortgage stack,
productivity, the external sector, the US trade relationship, the
labour market, or the fiscal trajectory is wrong, where it is right
but priced, and where the honest answer is "we do not yet know."

Canada is the subject. Foreign macro -- the Fed, the US growth pulse,
Chinese demand, global oil -- enters this publication only as a
transmission channel into Canada. We do not publish standalone US
disinflation pieces or standalone China growth pieces. We publish on
what the Fed's path does to the BoC's reaction function, what US growth
and US tariff policy do to Canadian exports, what Chinese demand does
to oil sands realizations and copper. The framing is always: so what
for Canada.

We treat the Big-Six bank economics desks (RBC, TD, BMO, Scotia, CIBC,
National Bank) as competitors to measure against and occasionally
diverge from with stated reasons. They are not sources we cite in
running prose. Primary Canadian data and primary Canadian institutional
publications (BoC, StatCan, OSFI, CMHC, DoF, PBO, provincial finance,
C.D. Howe, IRPP, IMF Article IV, OECD) are the citations of record.

**What this is NOT.**
- Not a data terminal. We do not compete with StatCan tables, the BoC's
  Valet portal, or TradingEconomics. If your goal is to download a CSV
  of Canadian CPI, leave.
- Not a news aggregator. We do not chase headlines. We chase the small
  set of questions that determine whether the Canadian cycle turns.
- Not a forecast factory. We do not publish point estimates dressed up
  as precision. When we put a number on something we show the range
  and the assumptions that move it.
- Not a trade-idea service. We do not recommend positions, tickers, or
  sizes. We describe the Canadian macro state; readers translate to
  portfolios.
- Not evergreen at the deep-dive layer. Deep dives rotate as the
  Canadian regime rotates. The basics tracker is permanent (we will
  always have an Inflation section); the deep dives inside each
  section are not (a deep dive that mattered in 2024 is not guaranteed
  shelf space in 2026).
- Not a US-macro publication with a maple-leaf wrapper. If a piece
  could run unchanged in a US shop, it does not belong here.
- Not a magazine. We do not publish in editions, volumes, or issues.
  There is no monthly cover, no curated lede, no editorial hero on
  the homepage. The dashboard is indicator-first.

**Editorial posture in one line.** Cover the basics of Canadian macro
cleanly. Inside each section, ask a small number of load-bearing
questions harder than anyone else does, and update them when they
actually change.

---

## 2. Audience

Three primary personas. All Canadian. Content is written for these
readers, in this order of priority. If a piece does not serve at least
one of them, it does not ship.

**P1: The Bay Street allocator (primary; dominant persona).**
Multi-asset PM, macro analyst, or strategist at a Canadian institutional
buy-side seat. **The gravitational centre within P1 is CPP Investments'
Total Fund Management group and OTPP's economics and asset-mix team.**
These are the readers whose questions we should be answering first when
in doubt: they think in 5-to-30-year liability streams, they cannot be
told anything they could have learned from a Big-Six morning note, and
they price the difference between a structural and a cyclical call. The
broader P1 includes BCI, PSP, CDPQ, IMCO, AIMCo, HOOPP, OMERS, and the
macro desks at Toronto-based asset managers (RBC GAM, BMO GAM, TDAM,
Mackenzie, Connor Clark, Letko Brosseau, Picton Mahoney). Reads three
to five macro sources before lunch. Already knows what the BoC's
core-trim and core-median measures are. Wants: a contrarian frame on
the Canadian cycle, a clean chart on housing or the mortgage stack, a
number they did not have, a question they had not asked. Does not
want: 101 definitions, the median Big-Six note rewritten, "on the one
hand / on the other hand" paragraphs, or anything that could have
been a TD Securities morning note.

**P2: The policy-adjacent analyst.**
Works at the Bank of Canada's research and Canadian Economic Analysis
departments, the Department of Finance, the Parliamentary Budget
Office, a provincial finance ministry (Ontario, Quebec, Alberta, BC
most often), OSFI, CMHC, or a federal economic-development agency.
May also be at the C.D. Howe Institute, the IRPP, the
Macdonald-Laurier Institute, or a university research centre (Munk,
Rotman, HEC, UBC, Queen's). Reads us to triangulate against their own
internal models and to see Canadian data interpreted by someone
outside their building. Wants: methodological clarity, citations to
primary sources, and a willingness to disagree with the institutional
consensus politely but plainly.

**P3: The serious Canadian independent investor.**
Self-directed, post-career or pre-PM, holds a real Canadian-tilted
portfolio, has the patience to read 1500 words. Reads the Globe ROB
and the FT, not r/PersonalFinanceCanada. Wants: a coherent worldview
on Canada they can stress-test their own thinking against.

Explicitly **not** the audience: retail day-traders looking for TSX
entries, journalists looking for a quote, students looking for
textbook explanations of Canadian fiscal federalism, crypto-curious
readers, housing doomers, housing permabulls, global-generalist
readers who treat Canada as an afterthought.

---

## 3. Architecture: tri-modal product, three surfaces

**Data-driven, by design.** Sibley Creek is not a publication that
happens to include charts; it is a publication built around data, with
prose narrating it. The discipline applies at every surface:

- The dashboard is almost all data — seven section panels each
  surfacing a current print + a sparkline, plus a hero stamp of
  load-bearing headline numbers. The chrome around the data is
  deliberately spare.
- The topic pages are narrated chart packs — a vertical stack of
  charts, each paired with a 2-4 sentence read. The chart is the
  evidence; the paragraph is the read.
- The deep dives are research built around a heart of data analysis —
  long-form essays in which the charts are not decoration but the
  load-bearing scaffolding the argument hangs from. **A deep dive
  without charts is not a Sibley Creek deep dive.**

Every editorial output ladders to data. If a claim cannot be plotted
or cited to a primary source, it does not belong in a Sibley Creek
piece. Prose justifies its existence by interpreting numbers the
reader can verify. This is the publication's single hardest line.

Sibley Creek is one publication with three content modes and three
reader surfaces. The modes and the surfaces map onto each other but
are not identical: the same data print can land on the homepage as a
panel tile, in the section page as a chart with a fresh interpretation
paragraph, and inside a deep-dive essay as a scaffolding atom.

**Three content modes.**

**Mode 1 -- Live tracker.** Daily-refresh data from StatCan, Bank of
Canada Valet, FRED, Yahoo, CREA, and the Department of Finance Fiscal
Monitor. Pipeline-driven, no human in the loop on the data layer.
This is the substrate everything else sits on. The tracker is the
publication's spine: if it goes stale, nothing else matters.

**Mode 2 -- Automated event blurbs.** LLM-generated interpretation
paragraphs triggered on data prints (CPI release, LFS release, BoC
decision, etc.). Two to four sentences, written to the voice canon
in Section 7, human-reviewed before publish. Eventually fully
automated on the data-fetch side; the human review gate stays.
Mode 2 is the bridge between the spine and the prose: it makes the
tracker speakable.

**Mode 3 -- Deep-dive research.** Human-led long-form pieces on the
eight pillars (Section 5). Slow output by design -- one person, one
question at a time, dated and contestable. Mode 3 is where Sibley
Creek earns its keep against the Big-Six consensus.

**Three reader surfaces.**

**Surface 1 -- Homepage (the dashboard).** A 30-second orientation. A
panel grid in the Vignelli visual canon: uniform tiles, no editorial
hero, no curated lede, no magazine-style framing. Seven section
cells plus a working-papers cell for active deep dives.
Indicator-first and indicator-rich: each tile surfaces the most
recent print, the direction, and an anchor chart. The homepage exists
to answer one question -- "where does Canada stand right now?" -- and
to route the reader into the relevant section.

**Surface 2 -- Topic pages (scrolling chartbooks).** One per section
(`/gdp/`, `/inflation/`, `/labour/`, `/housing/`, `/policy/`,
`/markets/`, `/trade/`). Each topic page is a chartbook: a section
header (headline question, current state in one sentence), a plate
index linking to each chart, then a vertical stack of **chartbook
units**. Each chartbook unit is a single indicator's chart paired
with a two-to-four-sentence interpretation paragraph -- the
publication's editorial atom. The chart is the evidence; the
paragraph is the read. Together they are the smallest unit of
content that carries the Sibley Creek voice.

**Surface 3 -- Deep dives.** Long-form essays scaffolded by
chart-paragraph atoms throughout. Each deep dive lives within its
home section (Pillar A inside `/housing/`, Pillar B inside `/policy/`,
etc.) and is reachable from the section's chartbook index and from
the homepage working-papers cell. Cross-references between sections
are allowed; co-ownership is not.

**Why this works.** The chartbook unit (chart + paragraph) is the
editorial atom. It is the same atom in Mode 2 (auto-blurb on a fresh
print, attached to a chart that already exists on the topic page)
and in Mode 3 (deep-dive prose, scaffolded by atoms that the writer
controls). The atom carries the voice; the surfaces arrange the atoms
at different densities -- terse on the homepage, full on the topic
page, sustained inside a deep dive.

What this architecture is not: it is not "boc-tracker but bigger."
The section skeleton is borrowed because it matches how a Canadian
macro desk frames the economy; nothing else about boc-tracker is
inherited. Voice, visual canon, the chartbook unit, the tri-modal
product, and the opinionated deep-dive layer are Sibley Creek's own.

---

## 4. Sections (v1)

Seven sections. The navigation skeleton is the boc-tracker section
list, with one consolidation: **Demographics is folded into Labour.**
Population growth, immigration levels, and temporary-resident flows
are the per-capita-output and labour-supply story, and that story
belongs in the section that already covers employment, wages, and
hours. A standalone Demographics section would either duplicate
Labour or reach into Housing (population-to-stock ratio) and Policy
(fiscal-demographic pressure); both are better served by
cross-references from a unified Labour section.

**On the Policy section.** Policy covers both monetary (BoC) and
fiscal (federal + provincial) under one roof. Rationale: a Bay Street
allocator thinks about "the Canadian policy stance" as one composite
state, and the two sub-surfaces share readers, frameworks, and
falsification logic. The topic page for Policy has two clearly
demarcated surfaces (monetary and fiscal), **eight chartbook units
total: four monetary, four fiscal**, in that order. Section 4.5
below enumerates the eight; the topic page is rendered as a single
vertical stack with a visual divider between the monetary slate
(units 1-4) and the fiscal slate (units 5-8). We will split Policy
into separate Monetary and Fiscal sections in a future pass if
Fiscal earns standalone real estate -- but in v1, one section,
eight units.

**The chartbook unit as editorial atom.** For each section below,
the "basics" enumeration lists the chartbook units of that topic
page. Each element is one chart paired with a two-to-four-sentence
interpretation paragraph; the prose lands in the paragraph, not in
section-level chrome. Headlines and per-unit titles are drafted by
writer and polished by style-editor; this doc owns the scope of
what each headline must communicate.

For each section, the topic-page chartbook is described below. Deep
dives are listed in Section 5 with their home section noted.

### 4.1 GDP

**Headline question.** Is the Canadian economy at potential, growing,
or contracting -- and what is driving it?

**Chartbook units (4-6):**
1. Headline real GDP -- monthly by industry (StatCan, ~60-day lag)
   and quarterly by expenditure (with Q/Q SAAR and Y/Y). Latest
   print: date, value, revision direction, and surprise vs. market
   consensus (Bloomberg / Reuters median, or aggregated forecaster
   median where the paid feed is unavailable). BoC's most-recent
   MPR central projection is the fallback anchor when consensus is
   genuinely unavailable. The consensus number enters as a derived
   numerical input, not as a cited opinion -- the voice principle
   on Big-Six sourcing (Section 7) applies to citation, not to
   forecast aggregation.
2. Industry vs. expenditure cross-check -- where the two cuts agree
   and where they diverge. v1: static methodological footnote on
   typical reconciliation gap; dynamic discrepancy commentary is
   deep-dive territory.
3. Contributions to quarterly growth -- six-bar decomposition:
   consumption, government, gross fixed capital formation (GFCF),
   inventories, exports, imports. The business-vs-residential
   investment split lives in Pillar D (productivity gap) deep-dive,
   not in v1 basics.
4. Per-capita real GDP -- the cut the headline obscures; Y/Y and the
   consecutive-quarter contraction count.
5. Versus BoC potential -- the BoC's latest MPR potential-output
   estimate as the benchmark; current output gap (Valet
   `INDINF_OUTGAPMPR_Q`); potential-growth numbers read off the
   MPR Appendix on each release. Secondary view (toggle):
   industrial capacity utilization (total + manufacturing,
   quarterly) as the firm-side slack complement. If a BoC MPR cycle
   does not refresh the output-gap series, the panel surfaces the
   last-published estimate with a stale-vintage badge; no HP-filter
   substitute is constructed.
6. Recession state -- C.D. Howe Business Cycle Council dating;
   amplitude, duration, scope (BCC's canonical wording, not "depth,
   breadth"; not the two-negatives shorthand). Maintained as a
   one-row editorial status entry refreshed on each BCC communique.

### 4.2 Inflation

**Headline question.** Is the BoC's 2% target being met, and on what
measures and what breadth?

**Chartbook units (4-6):**
1. Headline CPI -- Y/Y and 3-month annualized; latest print with
   surprise vs. market consensus (Bloomberg / Reuters median, or
   aggregated forecaster median where the paid feed is unavailable).
   BoC's MPR central projection is the fallback anchor when
   consensus is genuinely unavailable. CPI ex-indirect-taxes is
   canonized as a Phase-2 secondary toggle (gated on StatCan vector
   wiring); the overlay separates price-level signal from tax-policy
   noise (GST/HST changes, tariff pass-through).
2. BoC preferred core measures -- core-trim and core-median lead
   as the BoC's current preferred pair; common shown as historical
   anchor in hover/footnote with a one-line note that BoC has
   deprioritized common since late 2022. Y/Y is the primary; short-
   window annualized (3M AR) is included if the underlying NSA core
   index levels are recoverable from Valet (probe required) -- if
   not, Y/Y only in v1, 3M AR deferred to v1.5.
3. Breadth -- share of CPI basket components above 3%, between
   1-3%, and below 1% as the breadth element. The four state names
   (broad-based pressure, broad-based softening, clustered near
   target, polarized) remain available as prose vocabulary when
   the data clearly matches one, but are not presented as an
   exhaustive partition. This honors the May 2026 verification
   resolution that retired the four-state typology as a forced
   classification.
4. Sub-aggregates -- shelter (with mortgage interest cost
   decomposed out via Table 18-10-0004-01 sub-components),
   services ex-shelter, goods ex-energy, food, energy. The "ex-"
   aggregates are basket-weighted derivations and ship in v1 only
   if a reproducible analysis script with methodology note is in
   place; otherwise v1 shows all-services and all-goods directly
   with prose noting the dominant sub-component. Residual
   stickiness is one-sentence analyst call-out in the blurb.
5. Inflation expectations -- CSCE consumer 1y and 5y as the
   default view; BOS firms expecting >3% as toggle 1; BOS
   distribution buckets (below 1% / 1-2% / 2-3% / above 3%) as
   toggle 2. All three views must be wired; the panel's current
   consumer-only implementation is incomplete against canon.
6. Pass-through watch -- side-by-side strip-chart panel: (USDCAD
   Y/Y vs goods-ex-energy CPI Y/Y) and (LFS-Micro wage growth vs
   services-ex-shelter CPI Y/Y). No regression in basics; the
   interpretation is analyst prose. Gated on element 4's derived
   aggregates landing; if they slip, pass-through defers to v1.5.

### 4.3 Labour (incl. Demographics)

**Headline question.** How tight is the Canadian labour market, and
is per-capita output recovering through population deceleration or
through aggregate weakness?

**Headline number.** Unemployment rate (the recognized institutional
anchor across BoC, StatCan, OECD, IMF). The per-capita panel
(unit 2 below) is the analytical second look directly beneath
the headline. The two-step structure is deliberate: the unemployment
rate is the *what*; the per-capita panel is the *so what*.

**Demographics placement.** No standalone Demographics subheading.
Population surfaces twice -- as the denominator in the per-capita
panel (unit 2), and as the supply-side trajectory (unit 5).
Labour first, demographics second; never demographics-as-opener.

**Chartbook units (7, in order):**
1. **LFS headline** -- employment, unemployment rate, participation,
   employment rate. Latest print with surprise vs. market consensus
   (Bloomberg / Reuters median, or aggregated forecaster median
   where the paid feed is unavailable); BoC's MPR labour projections
   are the fallback anchor when consensus is genuinely unavailable.
   First-Friday cadence. Secondary view (toggle): youth and prime-age
   unemployment rates as separate lines.
2. **Per-capita panel** (signature) -- side-by-side small multiples:
   employment Y/Y vs employment Y/Y per-capita; aggregate hours Y/Y
   vs per-capita hours Y/Y. This is where the section headline
   question sits. Secondary views (toggles): prime-age triplet
   (participation + employment + unemployment, 25-54) and youth
   triplet (15-24) as denominator-adjusted slack reads.
3. **Wage band** -- four measures (LFS all-employee, LFS permanent,
   SEPH, BoC's composition-adjusted LFS-Micro) shown as a band, with
   dispersion called out; CPI services Y/Y as comparator line.
   Secondary overlay (toggle): Unit Labour Costs as the
   productivity-adjusted wage read.
4. **Vacancies and slack** -- JVWS vacancy rate (3mma, not 12M);
   vacancy-to-unemployment ratio with empirical Canadian-calibrated
   bands as historical anchors (not current-state claims);
   Beveridge-curve scatter with the most recent point highlighted
   and a 12-month trail.
5. **Population and immigration -- the supply trajectory** -- a
   stacked-composition chart of PR inflows and NPR inflows
   (four-quarter trailing sum), with dated annotations at each
   IRCC levels-plan vintage including the Oct 2024 structural-break
   pivot. A small companion table lists the current plan's PR / NPR
   targets for 2026-2028 with vintage. The IRCC plan is maintained
   as a small versioned JSON in the data layer; editorial refreshes
   on each November plan release.
6. **Regional dispersion** -- four-province dumbbell (ON, QC, AB,
   BC) with national rate overlaid; current value and 12-months-ago
   value to surface the "loosening fastest" call-out. Matches
   Housing's six-CMA convention rather than ten-province clutter.
7. **EI Regular Beneficiaries** -- single-series with level (in
   thousands) / Y/Y / MoM transforms. The demand-side mirror of
   vacancy decline and a leading recession indicator: EI uptake
   inflects before LFS unemployment turns. National only in v1;
   provincial breakdown defers to deep-dive. Cadence: monthly,
   ~80-day lag (StatCan Table 14-10-0011-01).

**Boundary with Pillar E (deep-dive).** The Labour blurbs *surface*
the per-capita-vs-aggregate divergence; Pillar E resolves whether
population deceleration or aggregate weakness explains it. The
chartbook layer must not pre-empt the deep-dive.

### 4.4 Housing

**Headline question.** Is the rate-sensitive sector amplifying or
dampening policy, and is supply arriving where population is settling?

**Chartbook units (7, in order):**
1. Prices -- MLS HPI benchmark, national plus six CMAs (Toronto,
   Vancouver, Montreal, Calgary, Ottawa, Edmonton); Y/Y and
   6-month annualized. No national-average headline number. CMA-
   level requires CREA XLSX bulk download (not in BoC FVI).
2. Activity -- starts (with 3-month moving average), completions
   (Table 34-10-0135), permits as the leading indicator; rental
   vs. ownership split via CMHC intended-market breakdown.
   Secondary view (toggle): CMA-level resales (Toronto / Vancouver /
   Calgary, 12M rolling) as the granular-geography activity cut.
3. Inventory and absorption -- MLS sales-to-new-listings (national
   via BoC FVI; CMA via CREA XLSX); months of inventory by CMA
   constructed as active listings / monthly sales, methodology
   note one click away.
4. Rent -- CMHC Rental Market Survey for annual vacancy and rent
   levels (primary citation); StatCan CPI rented-accommodation and
   rent sub-series (Table 18-10-0004-01) for the monthly direction
   read. Toronto / Vancouver loosening direction visible at
   monthly frequency.
5. Mortgage stack snapshot -- v1 cites BoC's most recently
   published Residential Mortgage Market chartpack for the
   vintage / term composition, plus OSFI Bank Financial Data
   residential mortgage line and CMHC arrears (RMIR; with CBA
   chartered-bank arrears as monthly proxy). Secondary element on
   the panel: 5-year fixed mortgage rate and the 5Y-mortgage-to-5Y-
   GoC spread as the marginal-borrower cost-of-borrowing read. Our
   own full reconstruction of mortgage stack by vintage and term is
   Pillar A (mortgage renewal wall) deep-dive territory, deferred
   from v1 basics.
6. Population-to-housing-stock ratio by CMA -- the supply-response
   denominator. Built from StatCan Table 17-10-0135 (annual CMA
   population) and Table 36-10-0688 (housing stock). Annual; v1
   ships with methodology note on base year and intercensal
   interpolation.
7. Housing Affordability -- BoC qualifying-mortgage-payment-to-
   income index (quarterly, from 1981). The flow-side complement to
   Panel 5's stock snapshot: "what would a new borrower pay against
   current income." Historical tightening episodes (1989-1991,
   2007-2008, 2022-2024) overlaid as static reference bands, not
   current-state classifiers. Cadence: quarterly, on the BoC
   Indicators of Capacity and Inflation Pressures release.

### 4.5 Policy (Monetary + Fiscal)

**Headline question.** What is the Canadian policy stance --
monetary and fiscal -- and is it consistent with the cycle?

**Chartbook units, monetary sub-surface (4):**
1. BoC overnight rate -- current level, distance to estimated
   neutral band (researcher-curated value extracted from the most
   recent April-MPR refresh, with vintage stamp; not an API
   series), consecutive-meeting action state (on hold / cutting /
   hiking). Secondary views (toggles): peer central bank rates
   (Fed, ECB, BoE, RBA) for cross-DM stance comparison; real
   policy rate (overnight minus headline CPI Y/Y) as the
   inflation-deflated stance read.
2. Market path -- 2-year GoC vs. overnight as the term-structure
   read on expectations; the OIS-implied BoC path is cited from
   the BoC MPR's market-implied curve chart on a quarterly cadence
   (primary-source-grade; we do not construct our own OIS forwards
   in v1). Full OIS-implied path construction defers to Pillar B
   deep-dive.
3. BoC-Fed spread -- current level, distribution context (P50/P80/
   P95/P99 from 35+ years of daily data), regime classification
   (editorial interpretation grounded in the cited distribution).
4. Balance sheet -- BoC settlement balances and asset composition;
   phase (QE / reinvestment / passive QT / floor maintenance) as
   editorial-curated phase call with cite-to-statement timeline.
   Secondary view (toggle): CORRA-vs-overnight-target spread (daily,
   20-day smoothing), the funding-market plumbing diagnostic that
   confirms or falsifies the floor-maintenance call.

**Chartbook units, fiscal sub-surface (4):**
5. Federal trajectory -- DoF Fiscal Monitor latest (monthly,
   ~2-month lag, fetched by pipeline); federal deficit YTD; debt-
   service costs as % of revenues; PBO Economic and Fiscal Outlook
   vs. FES/Budget baseline delta (researcher-curated comparison of
   two cited projection vintages).
6. Provincial -- net debt-to-GDP for ON, QC, AB, BC from each
   province's budget; latest budget balance vs. plan; any active
   credit-watch flags from Moody's / S&P / Fitch / DBRS
   Morningstar published rating actions.
7. Debt management -- GoC issuance trajectory, average term, and
   redemption profile cited directly from the DoF Debt Management
   Strategy Annex; coupon-roll framing reads off the DMS narrative
   and redemption-profile table. No own construction of coupon-
   roll math in v1.
8. Fiscal stance vs. cycle -- cyclically-adjusted primary balance
   cited from IMF Article IV Canada or OECD Economic Survey of
   Canada with methodology footnote naming the source. Canada's
   DoF does not publish a CAPB; we explicitly do not construct our
   own in v1 basics. Fiscal impulse is a one-line transform on the
   cited CAPB. Consistency-with-monetary-stance is prose-level
   interpretation, not a quantified index. Our own CAPB
   construction and a formal fiscal-monetary consistency index are
   Pillar F deep-dive territory.

The Policy topic page renders as a single eight-unit vertical
stack with a visual divider between unit 4 and unit 5.

### 4.6 Markets

**Headline question.** What external winds are pushing on Canadian
inflation, growth, and the CAD -- and where are Canadian markets and
the financial system tight or loose?

**Chartbook units (4-6):**
1. CAD -- USDCAD level (BoC Valet `FXUSDCAD` for consistency with
   BoC charts); BoC nominal effective index (CEER); USDCAD
   percentile classifier (P50/P80/P95/P99 since 1990) as the
   stress-classification frame, NOT a hardcoded 1.45-1.47
   corridor. The full oil-and-rate-differential fair-value model
   (rolling-window regression with confidence bands) defers to
   v1.5 / deep-dive given documented coefficient instability post-
   2016; v1 shows the percentile classifier instead.
2. GoC curve -- 2y, 5y, 10y, 30y; spread to UST at the 2y and 10y
   (add US 10y via FRED `DGS10`); term premium where decomposable
   (BoC's published Canadian term-premium series at the 10y from
   the Financial Stability Indicators page, Valet key to be
   probed; if unavailable, cite the BoC FSI page directly and
   defer own ACM-style decomposition).
3. Credit spreads -- v1 ships with US IG and HY OAS as the
   risk-appetite proxy (FRED `BAMLC0A0CM`, `BAMLH0A0HYM2`) with
   an explicit Canadian-spread blind-spot caveat. Canadian
   senior-unsecured-vs-GoC and Canadian IG/HY proxies require
   either FSR scraping or own construction from individual issuer
   curves and defer to v1.5.
4. Energy prices -- WTI, Brent; WCS at monthly cadence with the
   "do not surface daily-comparison differential" caveat preserved;
   AECO gas (weekly bid-week summary if achievable, else defer
   to v1.5); implied gasoline-channel CPI impulse already
   constructed.
5. Bank stability -- Big-Six PCL builds (quarterly, manual capture
   from earnings releases); CET1 ratios vs. OSFI Domestic
   Stability Buffer (latest DSB level: 3.5% per OSFI; CET1 from
   Pillar 3 disclosures, shown as range or average); uninsured
   residential exposure from OSFI Bank Financial Data M4
   (semi-annual scrape acceptable).
6. Financial conditions index -- if BoC's published FCI is
   available via Valet (key to be probed), use it directly as the
   primary anchor. If unavailable, v1 ships with US comparator FCIs
   (Chicago Fed NFCI is free and citable) plus prose-level
   Canadian commentary; own Canadian FCI composite construction
   defers to v1.5.

### 4.7 Trade

**Headline question.** Is Canada's external position structurally
shifting, and how is the US trade relationship repricing exporters?

**Chartbook units (4-6):**
1. Merchandise trade balance -- monthly (BOP basis, StatCan
   Table 12-10-0119-01), with three-month moving average;
   surplus/deficit decomposition by major HS-section product
   category (~12 categories from Table 12-10-0121-01 exports and
   12-10-0122-01 imports); non-monetary-gold-stripped variant
   alongside the headline for a cleaner momentum read.
2. Current account -- quarterly (Table 36-10-0014-01); goods,
   services, primary income, secondary income; goods-vs-services
   split surfaced; sustained drivers vs. one-offs called out in
   blurb prose.
3. Partner shares -- US bilateral, plus China, UK, Japan, Mexico,
   Germany. The structural-shift narrative is in the rolling US
   share trajectory. (Energy export decomposition by mode --
   pipeline incl. TMX, rail, marine, LNG netbacks -- is Pillar G
   deep-dive territory; v1 shows aggregate energy export value/
   volume from Table 25-10-0044-01 and 12-10-0121 energy line.)
4. Tariff state -- live US tariff actions on Canadian goods
   (rates, products, duty deposits); USMCA review milestone
   status. Maintained as an editorial reference table sourced
   from USTR proclamations, CBSA tariff classifications, and DoF
   retaliatory-tariff notices. Not a numeric series.
5. Terms of trade -- StatCan ToT index (Table 36-10-0103-01,
   quarterly) plus BoC commodity price index (BCPI and BCNE from
   Valet, daily) as the higher-frequency leading line into ToT.
6. FDI by sector -- inflows and outflows from StatCan
   Table 36-10-0008-01, quarterly; known M&A-driven one-offs
   flagged in methodology note.

Auto and metals as a standalone unit is folded into unit 1's
by-category decomposition; their cross-border production flows
live in Pillar H (US trade relationship) deep-dive.

---

## 5. Current deep dives

Deep dives are the load-bearing questions inside each section. They
are opinionated, dated, and contestable; they ship at the cadence the
underlying question actually moves on; they rotate as the Canadian
regime rotates. The current slate is eight, inherited and unchanged.
Each is homed in exactly one section.

| # | Deep dive | Home section | Cross-references |
|---|---|---|---|
| A | Mortgage renewal wall -- has it peaked, what is the residual transmission through 2027 | Housing | Markets (PCL builds, bank exposure); Inflation (mortgage-interest CPI) |
| B | BoC vs. Fed divergence -- how far can it run before CAD, the GoC curve, or credit conditions force a back-off | Policy (monetary) | Markets (CAD, GoC-UST spreads, credit) |
| C | Housing cycle and supply response -- is it bottoming, is supply arriving where population is settling | Housing | Labour (population-to-stock ratio) |
| D | Business investment and the productivity gap -- cyclical capex inflection vs. structural divergence with the US | GDP | Labour (productivity = output / hours); Trade (FDI) |
| E | Population deceleration vs. labour -- does per-capita output recover through deceleration or through unemployment | Labour | Housing (population-to-stock); Policy (fiscal-demographic pressure) |
| F | Fiscal capacity, federal and provincial -- is the debt-service trajectory consistent with the next downturn | Policy (fiscal) | Markets (GoC term premium, issuance) |
| G | LNG / TMX / external position -- are the structural lifts being absorbed by oil-sands discipline and the WCS differential | Trade | Markets (commodity prices, CAD) |
| H | US trade relationship -- how is USMCA review and Section 232/301 repricing Canadian exporters | Trade | GDP (export contribution); Markets (CAD) |

**Why these eight, now.** Each is load-bearing for the Canadian cycle
as of May 2026, supported by data we can get, and a question where a
sharper view than the Big-Six consensus is achievable. The full
rationale, what-we-track, scope-discipline, and falsification triggers
for each deep dive were established in the prior pass and are
preserved in the project's editorial record; they are not re-listed
in full here to keep this document focused on architecture.

**Rotation.** Deep dives are not evergreen. A deep dive is retired or
merged when its named falsification triggers fire, when the regime it
covers resolves, or when it stops moving relative to its cadence. By
November 2026, the slate should have rotated at least once: most
likely candidates for retirement are A (if the 2026 renewal cohort
clears without tail) and H (if USMCA review resolves into stable
text); most likely candidates to be added are not yet named.

---

## 6. Cadence

Refresh rates are matched to how fast each section's underlying data
and narrative actually move, and to the Canadian release calendar.
Over-refreshing is a tax on the reader. There is no edition,
volume, or issue cadence -- Sibley Creek does not publish in
editions.

The 2026 Canadian release calendar this anchors to:
- BoC fixed announcement dates: Jan 28, Mar 18, Apr 29, Jun 10, Jul
  15, Sep 2, Oct 28, Dec 9. MPR alongside Jan, Apr, Jul, Oct decisions.
- LFS: first Friday of the month (StatCan).
- CPI: mid-month (StatCan), ~two weeks after the reference month.
- Monthly GDP by industry: ~60 days after the reference month.
- BoC Summary of Deliberations: two weeks after each rate decision.
- Financial System Review: typically May and November.
- Federal Budget: Feb-Mar; Fall Economic Statement: Nov-Dec; Fiscal
  Monitor: monthly with a two-month lag.

**Tracker cadence by section:**

| Section | Cadence | Primary trigger |
|---|---|---|
| GDP | Monthly + quarterly | StatCan monthly GDP by industry; quarterly GDP by expenditure |
| Inflation | Monthly | StatCan CPI (mid-month) |
| Labour | Monthly | LFS (first Friday); SEPH; quarterly population estimates |
| Housing | Monthly | StatCan housing starts; CREA MLS HPI; CMHC arrears |
| Policy (Monetary) | Event-driven | BoC rate decisions, MPR, Summary of Deliberations, FSR |
| Policy (Fiscal) | Monthly + event | DoF Fiscal Monitor; Budget; FES; PBO releases; provincial budgets |
| Markets | Daily (light) + weekly synthesis | BoC Valet daily series; weekly close summary |
| Trade | Monthly + event | StatCan merchandise trade; quarterly current account; USMCA / 232 / 301 events |

**Mode 2 (auto-blurb) cadence.** Driven by data prints. When a
release lands, the relevant chartbook unit's interpretation paragraph
is regenerated; the new paragraph passes human review before it
goes live. The chart refreshes on the pipeline cadence; the
paragraph refreshes with each meaningful print.

**Mode 3 (deep-dive) cadence** follows the underlying question, not
a fixed schedule. A deep dive ships when it has something to say.
Cadence guidance per deep dive was established in the prior pass.

**Annual peak periods.** Federal Budget (Feb-Mar), provincial budget
season (Feb-May), Fall Economic Statement (Nov-Dec), and any active
USMCA review or Section 232/301 window. Cadence ramps; we publish off
the listed cycle when these are live.

---

## 7. Voice principles

Directional only. style-editor formalizes. These are the bearings.

**The editorial atom.** The chartbook unit -- one chart plus a
two-to-four-sentence interpretation paragraph -- is where the voice
lands. Voice carries through prose attached to evidence; not through
magazine-style framing, not through a curated lede, not through a
section editor's column. Strip away the chart and the paragraph
should still read as a defensible sentence about Canada; strip away
the paragraph and the chart should still be legible. They are
co-equal.

**Two voice postures by mode.**
- **Mode 2 (auto-blurb on data print).** Posture: terse, factual,
  observation-first. Two to four sentences. State the print, place
  it in context (vs. consensus, vs. prior, vs. cycle), name what it
  changes about the read. No speculation beyond what the print
  supports. Eventually generated automatically and reviewed by a
  human before publish. Cadence: as fast as the data lands.
- **Mode 3 (deep-dive prose, human-led).** Posture: opinionated,
  dated, scaffolded by chart-paragraph atoms throughout the piece.
  Each atom advances the argument; the atoms together do the work
  the prose claims. Cadence: slow. Ships when there is something
  to say. Voice is sharper than Mode 2 but inherits Mode 2's
  discipline on numbers and citation.

**Both modes share the canon below.**

- **Canadian context first.** We do not assume the reader cares about
  US macro for its own sake. US developments are explained only insofar
  as they hit Canada -- the Fed's path through the BoC's reaction
  function, US growth through Canadian exports, US tariff policy
  through Canadian exporter margins.
- **The Big-Six economics desks are competitors, not sources.** We
  read RBC, TD, BMO, Scotia, CIBC, and NBC economics daily. We measure
  ourselves against them and occasionally diverge from them, naming
  the reason and the evidence that would change our mind. We do not
  cite them in running prose. Primary Canadian institutional
  publications are the citations of record.
- **A piece exists to move a reader's view.** If a deep-dive draft
  would leave a P1 reader with the same view they walked in with, it
  does not ship as is. "Confirming the consensus with sharper
  evidence" is acceptable; "restating the consensus" is not. The
  Mode 2 blurbs are held to a different bar -- a blurb exists to
  ground the reader in current state, not to move a view.
- **Skeptical of consensus, but not contrarian for sport.** When we
  agree with the Bay Street consensus we say so. When we disagree we
  say why, and we name what evidence would change our mind.
- **Comfortable saying we do not know.** "The data are consistent
  with both stories" is a legitimate finding and often the most
  honest one. Hedging is bad; calibrated uncertainty is good. Know
  the difference.
- **Numerate, not number-spammy.** Every number earns its place. If
  a chart shows it, the prose does not also recite it.
- **Plain English, technical where it must be.** "Term premium"
  stays. "Core-trim" and "core-median" stay. "Quantitative tightening
  normalization optionality" does not.
- **No breathlessness, no doom, no hype.** No "shocking," no
  "stunning," no "Canada's Lehman moment," no "this changes
  everything." Cycles are long. Most days nothing changes. Say so.
- **Canadian English.** Labour, not labor. Centre, not center.
  Programme is too far; program is fine. Use the Canadian
  spelling where Canadian institutional usage does.
- **Cite primary sources.** Statistics Canada, Bank of Canada, OSFI,
  CMHC, Department of Finance, PBO, provincial finance ministries,
  C.D. Howe Business Cycle Council, IRPP, BIS, IMF Article IV Canada,
  OECD Economic Surveys.
- **Show your work.** If a chart is constructed (decomposed,
  detrended, seasonally adjusted by us, or built from microdata), the
  methodology note is one click away.

---

## 8. Out of scope

Decisions, not deferrals.

- **No editions, volumes, or issues.** Sibley Creek does not publish
  in a magazine cadence. No monthly cover, no "this week's edition,"
  no curated lede. The homepage is indicator-first; deep dives ship
  when they ship.
- **No editorial hero on the homepage.** The homepage is a panel
  grid of indicators. No featured essay slot, no rotating banner,
  no human-curated front-of-book.
- **No standalone US-macro pillars.** US developments appear only as
  transmission channels into Canada. If a piece could run unchanged
  in a US shop, it does not belong here.
- **No standalone single-province pieces** unless the question is
  genuinely about regional dispersion. Single-province political
  coverage is not in scope.
- **No individual equities.** Not as picks, not as themes.
  Sector-level appears only as a macro input. No TSX stock coverage.
- **No crypto.** Bitcoin is not a Canadian macro indicator we cover.
- **No geopolitics qua geopolitics.** Geopolitics enters only
  through its priced macro channel into Canada: oil supply on WCS
  realizations, tariff incidence on Canadian exporters,
  export-control regimes on critical-minerals processing. We do not
  handicap elections, wars, or diplomatic events on their own terms.
  **Exception:** the USMCA 2026 review and US Section 232/301 actions
  affecting Canada are in scope under Trade, because their effect is
  direct and quantitative, not inferential.
- **No FX trade calls.** CAD appears as a Canadian macro variable.
  We do not call USDCAD.
- **No commodities desk.** Oil, copper, gold, and LNG appear where
  they move the Canadian macro story. We do not publish a curve view.
- **No emerging-markets country-by-country.** EM appears only via
  the commodity-demand channel into Canada and dollar-funding
  conditions.
- **No retail-investor 101.** We assume the reader knows what the
  BoC's overnight rate is and how a mortgage renewal works.
- **No live blogs of BoC or FOMC days.** Considered notes after, not
  reaction takes during.
- **No bilingual content in v1.** EN-only at launch. FR is a v2+
  decision, resolved by January 2027 on the basis of reader
  analytics. We will not half-translate.
- **No carbon-pricing standalone pieces.** Industrial carbon pricing
  enters where it moves business investment (GDP), sectoral
  competitiveness (Trade), or fiscal flows (Policy). It is not a
  section.
- **No federal-provincial constitutional commentary.** Equalization,
  resource rents, and provincial fiscal divergence enter Policy as
  budget math, not as constitutional argument.
- **No pension-system policy coverage.** CPP/QPP and the major plans
  are P1 readers, not subjects. We do not handicap CPP contribution
  rates, OAS clawback design, or pension reform.
- **No standalone Demographics section.** Population, immigration,
  and temp-resident flows are housed in Labour.

---

## 9. Success criteria at six months (November 2026)

A healthy Sibley Creek in November 2026 looks like this. Testable;
the editorial-director can be held to them.

1. **All seven sections are live as topic-page chartbooks**, refreshed
   on their stated cadence for three consecutive months ending October
   2026. No section is a stub. No chartbook unit's chart goes stale
   by more than one release cycle; no unit's interpretation paragraph
   is older than the chart it sits on.

2. **The homepage panel grid is live and indicator-first**, with all
   seven section cells plus a working-papers cell rendering current
   data. No editorial hero, no curated lede; the homepage answers
   "where does Canada stand right now" in 30 seconds.

3. **Mode 2 (auto-blurb) is operating on at least three sections** --
   Inflation, Labour, and Policy (monetary) at minimum -- with each
   blurb passing human review before publish. The human review
   gate stays; full automation of the data-fetch side is the path,
   not the destination.

4. **At least five deep dives have shipped substantively**, with at
   least one in each of: Housing (Pillar A or C), Policy (Pillar B
   or F), Labour (Pillar E), GDP (Pillar D), and Trade (Pillar G or
   H). Each shipped deep dive has either been aged well or had its
   post-mortem published if it broke against us.

5. **At least five published deep-dive calls materially diverge
   from the Bay Street consensus**, with named falsification
   conditions, across the BoC terminal rate or BoC-Fed spread,
   Canadian housing trajectory, per-capita real GDP path, federal
   debt-service ratio, and the US-trade-relationship transmission.

6. **Citations are habitual and traceable.** A reader auditing any
   piece can trace every load-bearing number to a primary Canadian
   source within one click. Zero pieces in the November 2026 archive
   cite a bank morning note as a primary source.

7. **Methodology pages exist and are non-trivial.** For every
   constructed chart, a methodology note explains the construction,
   the data vintage, and the sensitivity to key assumptions. No
   black boxes.

8. **Cadence discipline holds.** Tracker layers refresh within 5
   business days of the relevant Canadian release. BoC
   rate-decision tracker updates within 24 hours of the decision;
   the Summary of Deliberations is reflected within 5 business days.

9. **The deep-dive slate has rotated at least once.** Either we have
   added a deep dive (something became load-bearing that was not in
   May 2026) or retired or merged one (a deep dive resolved or
   stopped moving against its named falsification triggers). If the
   November deep-dive list is identical to the May list, we are not
   paying attention.

10. **A reader from any of the three Canadian personas can answer,
    in one sentence, what Sibley Creek is for**, and can name the
    section they would go to for any of the headline questions in
    Section 4. Tested by a one-question reader survey in October
    2026, n>=20 across P1/P2/P3.

11. **No piece has required a correction larger than a footnote.**
    Methodology disagreements are welcome. Factual errors that
    change the conclusion are not. Target: zero conclusion-changing
    corrections in the November 2026 archive.

12. **A v2 roadmap exists.** Specifically: a written decision on FR
    edition (go/no-go by January 2027 based on reader analytics), a
    written decision on splitting Policy into separate Monetary and
    Fiscal sections, and a written decision on international
    expansion (default: no).

---

End of foundation document. Revisions to this file are
editorial-director decisions; they require a dated changelog entry
below.

## Changelog

- 2026-05-10: Initial version. Six pillars established. editorial-director.
- 2026-05-10: Scope corrected to Canadian focus. Pillars fully reworked. editorial-director.
- 2026-05-10: Final pass after role definition sharpened. editorial-director.
- 2026-05-10: Final pass after role definition sharpened and coordinator merged in. editorial-director.
- 2026-05-10: Two-layer architecture adopted -- boc-tracker-style sections as v1 navigation, eight pillars folded under sections as deep dives. editorial-director.
- 2026-05-10: Section 4 adjusted post-Wave-1 to reflect actual data coverage and construction cost. Four-state inflation breadth retired as forced classification (preserved as prose vocabulary). Surprise-vs-consensus reframed to BoC MPR central projection (no Big-Six / Reuters consensus citation). GDP contributions simplified to six-bar GFCF (business-vs-residential split deferred to Pillar D). Inflation 3M-AR core, goods-ex-energy / services-ex-shelter derivations, and pass-through panel gated on basket-weight reproducibility. Labour basics-layer panel order locked: LFS headline, per-capita panel (signature), wage band, V/U + Beveridge, immigration trajectory with IRCC annotations, four-province dumbbell dispersion. Housing mortgage-stack-by-vintage and own CAPB construction deferred to deep-dives; v1 basics cites BoC chartpack and IMF/OECD CAPB directly. Financial CAD fair-value model, own FCI composite, full term-premium decomposition, and Canadian credit-spread proxies deferred to v1.5; v1 basics uses USDCAD percentile classifier and US-side comparators with explicit caveats. Trade adds partner shares (China, UK, Japan, Mexico, Germany) and ToT / BCPI / FDI elements; energy-by-mode and auto/metals folded into deep-dives. editorial-director.
- 2026-05-10: User-override on surprise framing. Surprise is now anchored to market consensus (Bloomberg / Reuters median, or aggregated forecaster median where paid feed unavailable) across GDP, Inflation, and Labour element-1. BoC MPR projection is the fallback when consensus is genuinely unavailable. Reasoning: the voice principle on Big-Six sourcing (Section 7) applies to citation as authority, not to aggregating forecaster numbers as derived consensus inputs. Prior 2026-05-10 framing (BoC MPR as primary anchor) was a too-strict reading of the voice principle. main Claude on user instruction.
- 2026-05-11: Section 4.6 renamed "Financial" -> "Markets" to align with the homepage label rename in flight. Cross-references in Section 5 deep-dive table and Section 6 cadence table updated accordingly. Editorial rationale: "Markets" is the more honest label for what the section actually covers at the basics layer (CAD, GoC curve, credit spreads, commodity prices, bank capital, FCI). Financial-system stability work is deep-dive territory; the basics layer is markets-data-with-Canadian-lens. editorial-director.
- 2026-05-11 (Wave 4 adjudication): Section 4.5 Policy page panel count locked at eight (four monetary + four fiscal), not six. Frontend's six-panel placeholder must grow. Rationale: the canon enumerates four monetary elements (overnight rate, market path, BoC-Fed spread, balance sheet) and four fiscal elements (federal trajectory, provincial, debt management, fiscal stance vs cycle); collapsing to six would force editorial-arbitrary deletions from the canonical slate, and the monetary-fiscal divider is exactly the visual affordance the basics layer of a one-section-two-stance Policy page needs. Implementation note: page renders as a single eight-panel grid with a visual divider between panel 4 and panel 5. editorial-director.
- 2026-05-11 (Wave 5 coverage-parity adjudication): boc-tracker chart inventory adjudicated. Two new panels canonized: Labour grows from 6 to 7 panels with Panel 7 EI Regular Beneficiaries (demand-side mirror of vacancy decline, leading recession indicator); Housing grows from 6 to 7 panels with Panel 7 Housing Affordability (BoC qualifying-mortgage-payment-to-income index, flow-side complement to Panel 5's stock snapshot). Eight folds canonized as toggles/overlays on existing panels: GDP Panel 5 gains capacity-utilization secondary toggle; Inflation Panel 1 gains ex-indirect-taxes Phase-2 toggle; Inflation Panel 5 expanded to three views (CSCE consumer / BOS >3% / BOS distribution); Labour Panel 1 gains youth+prime-age unemployment toggle; Labour Panel 2 gains prime+youth triplet toggles; Labour Panel 3 gains ULC overlay; Housing Panel 2 gains CMA-resales toggle; Housing Panel 5 gains 5Y mortgage rate / GoC spread element; Policy Panel 1 gains peer-bank and real-rate toggles; Policy Panel 4 gains CORRA-target spread toggle. Methodology resolutions: GDP output gap canon stays BoC MPR `INDINF_OUTGAPMPR_Q` (no HP-filter substitute); WCS at monthly cadence, daily differential not surfaced; BOS distribution buckets added to Inflation Panel 5; CPI ex-indirect-taxes deferred to Phase 2. Cuts at basics layer: productivity decomposition, LFS R-indicators, Indeed postings, 60-component CPI decomposition, mortgage-renewal-shock stylized reproduction. Full record: `editorial/wave5_boc_tracker_chart_decisions.md`. editorial-director.
- 2026-05-11: Architecture canonicalized: tri-modal product (dashboard / chartbook / deep-dive), Vignelli visual canon, Sibley Creek name. Prior Layout B / Hero+6 / Path C iterations retired. Publication renamed from "Macro Research Department" placeholder to Sibley Creek (project directory and package.json keep `macro-research-department` for tooling continuity). Section 1 mission rewritten to lead with tri-modal product. Section 3 architecture rewritten as tri-modal product / three reader surfaces (homepage panel grid, topic-page chartbooks, deep dives); two-layer "basics + deep dives" framing absorbed into surfaces. Section 4 reframed: chartbook unit (one chart + one 2-4 sentence interpretation paragraph) named as the editorial atom; "basics layer" / "elements" / "panels" terminology unified to "chartbook units." Section 7 voice: editorial atom defined; Mode A (auto-blurb, eventually automated) and Mode B (deep-dive prose, human-led) postures distinguished; Canadian English principle made explicit. Section 8 out-of-scope: explicit exclusions added for editions / volumes / issues, magazine-style edition framing, and editorial hero on homepage. Section 9 success criteria expanded from 10 to 12 to cover homepage panel grid live (new criterion 2) and Mode 2 operating on at least three sections (new criterion 3); November 2026 horizon preserved. editorial-director.
