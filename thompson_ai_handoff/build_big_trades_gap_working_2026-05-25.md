# Build-Big skilled-trades gap — working doc

**Session date:** 2026-05-25
**Status:** Pre-commit. Expert advisor not yet engaged.

---

## Part I — The piece, in plain English

(Verbatim from the session, saved per Jay's ask.)

### 1. The question

Canada has a new Prime Minister — Mark Carney, ex-Bank of Canada and ex-Bank of England governor, took over from Trudeau in early 2025. His signature economic plan is "Build Canada" / "Build-Big." Headline: ~$1 trillion in new infrastructure — a new west-coast oil pipeline, LNG export terminals, nuclear small modular reactors, transmission lines, mines, ports, plus a pledge to double home construction to 500,000 starts a year. The federal government commits ~$280 billion of its own; expects to mobilize another ~$720 billion from private capital, provinces, and Indigenous equity. The pitch: this fixes Canada's productivity problem, reduces dependence on the US, solves the housing crisis.

**The question we'd answer:** does Canada have enough skilled tradespeople — welders, electricians, pipefitters, ironworkers, millwrights — to actually build all of this on the schedule announced?

### 2. Why it matters

You can't build a pipeline without welders. You can't build a nuclear reactor without instrumentation electricians and millwrights. You can't double housing construction without a near-doubling of the residential trades workforce. These are 3-5 year apprenticeships — you can't hire them on Indeed.

If Canada doesn't have the workforce:
- Projects slip past their announced schedules
- Costs balloon as firms bid up wages for scarce trades
- Some projects don't break ground at all
- The $1 trillion claim doesn't materialize — Canada takes on the debt without the growth
- The case for Build Canada as a substitute for lost US trade weakens

For investors: project IRRs are workforce-dependent. For households: this decides whether Carney's housing pledge is real. For the BoC: productivity gains baked into the macro outlook depend on these projects landing on time.

### 3. How we can answer it

The structure is arithmetic. Supply minus demand equals gap. That's the whole model.

The piece uses public data end-to-end. No paid BuildForce subscription, no methodology replication, no proprietary inputs.

**Supply baseline:** BuildForce Canada's most recent Construction and Maintenance Looking Forward (CMLF) — released April 4, 2025, covering 2025-2034. Their national Highlights say Canada needs 380,500 total hiring through 2034, against ~270,000 retirements + 111,600 growth demand, with a ~108,300 residual shortfall absent intervention. Their provincial Highlights publish a 5-tier classification by NOC code identifying which trades are most stressed, province by province.

**Workforce context:** Statistics Canada Labour Force Survey by NOC code — current employment counts by trade by province. Free, public, scales the magnitudes.

**Demand overlay:** Carney's announcements (MPO project list, Team Canada Strong targets, $1T mobilization claim, Build Canada Homes housing target) + project-by-project labour estimates from publicly filed environmental assessments (TMX: 67,423 person-years; LNG Canada Phase 1: peaked at 7,500 workers; Site C: 8,000 person-years for main civils; analog estimates for projects without EAs yet).

**Trade-level priority:** BuildForce's own 5-tier NOC classification from the provincial Highlights — Sibley uses BuildForce's rankings, not a Sibley-invented ranking. The classification is published only at the provincial level; Sibley's value-add is the national rollup (mapping projects to their geography and aggregating BuildForce's provincial rankings).

**Validation:** phone calls to union halls (UA pipefitters, IBEW electricians, Boilermakers, Operating Engineers, Iron Workers), provincial apprenticeship boards, construction-firm HR (PCL, EllisDon, Aecon, Ledcor), college trades-program faculty, project proponent IR/comms. These functionally do what BuildForce's regional LMI committees do — validate that the math matches what people on the ground are seeing — but with named on-the-record sources.

**The method:**
1. Take BuildForce's supply forecast as published (national + provincial Highlights)
2. Layer Sibley's Build-Big project demand on top, mapped geographically
3. Compute the aggregate gap by province and nationally
4. Anchor trade-level discussion to BuildForce's published 5-tier classification, aggregated across provinces
5. Compare against what Team Canada Strong delivers
6. Validate with phone-call texture

**Headline output:** how much labour Build-Big requires above what BuildForce's baseline already projected, where the demand is concentrated geographically, and which trades BuildForce themselves flag as most stressed in those geographies.

### 4. Why it would be convincing

- **The math is transparent.** Anyone with a bachelor's degree can check the arithmetic. We're not running econometric models — we're adding columns.
- **The inputs come from named primary sources.** BuildForce, government environmental assessments, StatCan LFS, IRCC. Every number traces back to a document the reader can pull up.
- **Sibley uses BuildForce's own classification.** The piece doesn't invent its own ranking of which trades are stressed; it uses BuildForce's 5-tier published ranking and rolls it up nationally.
- **The phone calls add what math can't show.** Union officials, apprenticeship boards, contractors describing what they're actually seeing. Different from analyst spreadsheets.
- **The simplification is conservative.** We model only projects with documented labour profiles. Anything we leave out (mines, Pathways CCS, some critical-minerals projects) would ADD to the gap, not subtract. So if anyone says "your number is too high," the answer is "we deliberately under-modelled — the real gap is worse."

**Inferential foundation that strengthens everything:** BuildForce's April 2025 baseline was modelled before the trade war (cutoff ~late 2024) and predates the federal Major Projects Office launch (August 29, 2025) by 5-11 months. Build Canada is the federal government's response to the trade war, structured around projects that didn't exist as designated federal initiatives when BuildForce modelled their supply path. Therefore BuildForce's labour supply forecast has no Build Canada incremental demand in it. The gap exists definitionally — confirmed by the timing of the public documents.

### 5. Why it might not be convincing

Three remaining risks, none fatal:

**(a) Modular construction.** New techniques (prefab housing, modular substations) could reduce labour-per-unit faster than BuildForce assumes. We apply a documented adjustment to the housing component (~30% reduction in residential labour-per-unit, with citation), but it's a known critique to anticipate. The piece's defense: even with generous modular assumptions, the non-residential energy/infrastructure side doesn't benefit materially.

**(b) Schedule slippage being endogenous.** If labour constraints just cause projects to slip rather than fail, the "gap" doesn't appear as a labour shortfall — it appears as delayed delivery. The story changes from "the math doesn't work" to "the timeline isn't credible." Different story, both publishable, but worth being clear about which one we're telling.

**(c) Labour-intensity coefficient defense.** For projects without published EAs (the new west-coast pipeline, some critical-minerals processing facilities), Sibley uses analog estimates from comparable projects (TMX for pipelines, LNG Canada Phase 1 for LNG, etc.). Each analog assumption needs to be flagged transparently in the methodology box.

The core claim — that the federal labour plan addresses pre-existing shortfall but not the project surge, and the surge is geographically concentrated where the binding-trade shortages already are — survives all three.

---

## Part II — Key decisions and findings (summarized)

### The story is uniquely well-suited to Sibley's "data + phone calls" method

The phone-call layer is load-bearing here. Banks/think tanks can do BuildForce-plus-project-math; only Sibley can also reach union officials, apprenticeship boards, college trades program faculty, and project HR leads. Unions in particular WANT this story told — it's the honest version of what they've been saying publicly for years. Cold-calling friendly because we're not asking sources to attack the government; we're asking them to confirm what they've already said. The phone calls functionally substitute for BuildForce's confidential regional LMI committee validation, just with named on-the-record sources.

### The actually-new claim (not "shortage exists")

Everyone agrees Canada has a trades shortage. The novel claim is:

**Team Canada Strong is sized to fix the trades shortage Canada ALREADY had. It doesn't fix the new shortage that Build-Big creates. Carney announced $1T in projects WITHOUT a workforce plan for the projects themselves.**

The geographic refinement: Build-Big demand is concentrated where the trade shortages already are. BC and Alberta carry the pipeline + LNG + oilsands CCS load. Ontario carries the SMR + transmission + housing load. Quebec carries mining + transit + hydro. Federal labour planning, sized for Canada's aggregate pre-existing shortfall, doesn't address those geographic concentrations.

The compressed extractable: *"Trades shortfall at peak Build-Big concurrence: ~[X]K person-years, concentrated in [the provinces and trades]. Team Canada Strong supplies ~80-100K nationally over five years. The math doesn't close — and money alone can't close it because the binding constraints are non-monetary."*

### The skeptic-hat responses

**Why doesn't Carney just spend more on training?** Money doesn't close the gap. Binding constraints are non-monetary:
1. Apprenticeship time is structural — 3-5 years. First new cohort comes out 2030-2031; Build-Big peak is 2027-2029.
2. Provinces own apprenticeship — federal money flows through provincial throughput constraints.
3. Supervisory-journeyman problem — to train more, pull experienced workers off Build-Big sites.
4. Training infrastructure capacity is fixed (welding booths, instructors, lab space).
5. Candidate pool is demographically + culturally constrained; completion rate ~20% in 2024.
6. Immigration through trades is slow — credential recognition takes 1-2 years; Carney's plan REDUCES total immigration.

**Why hasn't Carney done this math himself?** Likely strategic ambiguity. Admitting the labour math doesn't close undermines the political case for Build Canada and forces awkward conversations about schedule slippage. PBO has explicitly stated it hasn't done the productivity analysis yet (April 2026). The federal government has not published a project-by-project workforce model. Sibley would be first to put the numbers in public.

**Realistic reconciliation:** the announced timeline is aspirational. Schedule slippage is expected. Carney's federal labour program is plausibly sized for the actual delivery timeline (10-12 years), not the announced one (5-7 years). The political narrative survives slippage. The productivity case doesn't survive it as well.

### Reaction sweep finding — the wedge is empirically clean

Comprehensive sweep of public commentary in the 4-week window since Team Canada Strong was announced (April 29 - May 25, 2026) confirmed nobody has made the specific arithmetic comparison Sibley is contemplating. Five closest voices, none of whom did the math:

- **Paul de Jong (PCA CEO), DCN May 4** — verbal alignment about workforce needing to "meet the challenge" but no arithmetic
- **Marc Desormeaux (Business Council of Canada), Globe April 28** — framing-twin ("HR strategy alongside the major projects capital investment strategy") without sizing
- **Canadian Chamber of Commerce, May 12** — closest quantitative gesture; used BuildForce's gross hiring need (380K), not the 108K residual, and didn't separate MPO portfolio
- **Deloitte "Builders, baby, builders?"** — anchor for demand-side numbers; pre-dates Team Canada Strong
- **Mortgage Professionals Canada** — operational sufficiency gesture only

Notable silences: BuildForce themselves published nothing on Team Canada Strong in 4 weeks. CD Howe, IRPP, MLI, IFSD, Fraser all silent. Tombe, Moffatt, Tapp not visibly published. Bank desks notably quiet on the workforce-sizing question.

Full sweep at `business/research/team_canada_strong_reactions_sweep_2026-05.md`.

### The incremental-vs-displacement analytical knife

Sharpest analytical move the sweep surfaced — nobody has asked this question publicly:

**Is Team Canada Strong's 80-100K target incremental to BuildForce's already-counted 272,200 baseline youth-recruitment, or is it the same people the federal program just helps fund?**

Either interpretation strengthens the gap argument but requires different framing:

- **If incremental:** TCS adds 80-100K on top of BuildForce's 272,200 baseline → total new supply ~352-372K vs BuildForce's 380K total hiring need → baseline gap closes a bit; Build-Big incremental still not addressed.
- **If displacement:** TCS just subsidizes apprentices who would have entered anyway → no net new supply → 108K baseline gap stays; Build-Big incremental still not addressed.

The piece must address this explicitly. The methodology choice matters for the headline number.

### Refined methodology

Spec lives in Part VI. Top-line: every MPO project gets the same two-method demand-side treatment (published numbers if available; analog-plus-scaling from a comparable completed project if not). All projects in the portfolio are covered — no project gets dropped from quantitative coverage. BuildForce's 5-tier classification anchors the trade-priority discussion separately.

### Piece anatomy

Target ~2,500 words body + 200-word methodology box + 1-page executive summary. 5-7 charts (killer one: supply curve vs demand curve with Build-Big incremental layer overlaid, with geographic decomposition). 4-6 phone-call quotes. 1 single headline number, geographically anchored. ~10 minute read. PDF format for embargo distribution + web version on the site, total ~10-12 pages.

Full scaffolding spec lives in Part VII.

What we deliberately DON'T claim:
- "Build-Big is impossible" (schedules can slip; wages can rise; technology can shift)
- A precise point estimate (range with named uncertainty)
- Confident timeline-slippage predictions — only the conditions for it

### Publication timing strategy

Target mid-to-late June for publication — about 8 weeks post-Team-Canada-Strong-announcement, but ahead of the next BuildForce CMLF (expected late spring to early fall 2026).

Why this window works:
- Time to do the work properly (~3-4 weeks build)
- Lands BEFORE BuildForce's 2026-2035 CMLF makes the comparison less novel
- Sibley owns the analytical frame before anyone else gets there
- Anchor available: FSR May 28, Q1 GDP May 29, next MPO tranche likely later this year, or a specific Build-Big project milestone

Trade-off: lose the day-one news-reaction halo. Piece must land as structural analysis, not reactive hot-take. Lead with the math, not the news event. Position as "behind the headlines."

Window closes once another voice catches on. Estimated 8-12 weeks of clean-wedge time before someone else gets there. Move.

### Prior art (Jay's earlier question, answered)

- **Infrastructure Australia's Market Capacity Report** — international analogue with 5-year track record. Identical architecture (pipeline → trade × jurisdiction → supply shortfall). Sibley positions as "the Canadian IA report that doesn't exist yet."
- **BuildForce:** publishes supply baseline + 5.8M-homes residential scenario + provincial 5-tier NOC classifications. Pieces Sibley needs are in the public Highlights; the national rollup and project-by-project Build-Big demand overlay are not.
- **Deloitte:** 410K-520K total trades shortfall by 2030. Headline number, not bottom-up.
- **Conference Board (Signal49):** $2.6B GDP loss from labour shortage in 2024. Outcome, not bottom-up.
- **PBO, IMF, Macklem:** flagged labour scarcity as macro theme. None did bottom-up Build-Big.
- **Federal government:** announced Team Canada Strong with 80-100K target. NO published bridge to the broader need.

Nobody has connected the full Build-Big project portfolio to BuildForce-grade gap analysis with geographic concentration overlay. First-mover position confirmed.

### Team and capability honest assessment

Jay (smart econ generalist, ex-Bloomberg) + Claude + fresh M.A. + fresh B.A. CAN deliver this convincingly. The arithmetic is transparent enough that no expert is needed to construct it.

But Sibley needs an expert advisor IN THE LOOP for QA, not as co-author:
- One round of "find what we got wrong" at draft stage
- 2-4 hours of phone calls during the build for assumption-defensibility questions
- Cost: $1-3K or pro-bono via relationship

**Candidates worth approaching:**
- **Trevor Tombe (UCalgary, Productivity Initiative)** — most natural fit. Public-facing academic. Engages with media analyses.
- **Mike Moffatt (Missing Middle / PLACE)** — has Carney-government access; known Liberal sympathizer could complicate framing.
- **Stephen Tapp (Canadian Chamber, ex-PBO)** — labour-supply, fiscal analysis, lots of media engagement. Good independent voice.
- **A retired BuildForce researcher** — no conflict, institutional knowledge. Hard to source without a referral.

---

## Part III — Open questions before commit

1. **Manual prior-art clearance via reporters this week.** Ask Vieira / Rendell / Wall whether they've seen anyone estimate MPO tranche labour requirements. Pair with "if Sibley published this, would you find it interesting?" — costs nothing extra, tests embargo appetite. Plus 10-min LinkedIn scroll on Tombe / Moffatt / BuildForce. Plus paywalled pieces (The Logic, Hill Times-Crane) read directly.

2. **Timing relative to the next BuildForce CMLF release.** Bess (new ED, started March 2 2026) signaled "next era of data integration." The 2026-2035 CMLF hasn't dropped yet (normal cycle would have been April). Realistic window: late spring to early fall 2026. Target publication mid-to-late June to land before BuildForce's next release.

3. **Expert advisor approach.** Reach out to Trevor Tombe (or alternative) with a 1-paragraph pitch: "ex-Bloomberg econ editor, launching independent macro shop, doing [X] — would value your read at draft stage." Likely a $1K honorarium or coffee gets a yes.

4. **Wojtek warm intros.** Ask Wojtek if Sovereign has worked with industrial-trades / construction comms clients. Frame casual.

5. **Source pipeline confirmation.** Once committed:
   - Provincial apprenticeship boards (STO, AIT, ITA) — policy directors
   - Union locals (UA pipefitters, IBEW electricians, Boilermakers, Operating Engineers, Iron Workers) — business managers
   - Construction firm HR leads (PCL, EllisDon, Aecon, Ledcor)
   - Project IR/comms (Cedar LNG, OPG, Pembina)
   - Working tradespeople via local hall intros (BM to senior journeyman)
   - First Nations economic-development corps via Fasken/Torys Indigenous-equity counsel
   - College trades-program faculty (BCIT, NAIT, SAIT, Algonquin, Conestoga)

6. **Vieira embargo discussion.** The piece is naturally suited to embargo distribution. After methodology is locked, separate conversation with Vieira on what an embargo arrangement looks like.

---

## Part IV — Supporting files (all in `business/research/`)

- `build_big_answered_vs_open_2026-05.md` — comprehensive landscape of what's been established about Build-Big across all components + wedge candidates
- `buildforce_canada_verification_2026-05.md` — BuildForce as a primary source, methodology, headline numbers
- `skilled_trades_gap_methodology_2026-05.md` — full methodology note for the gap-analysis piece (data quality grades, comparable prior analyses, falsification risks)
- `team_canada_strong_reactions_sweep_2026-05.md` — 4-week reaction sweep confirming the wedge is clean; closest voices catalogued
- `canadian_macro_coverage_landscape_2026-05.md` — coverage map across Canadian macro publishers (free + paid)
- `biggest_canadian_macro_question_2026-05.md` — empirical triangulation of what's topically hottest in Canadian macro (Build-Big as dominant)

---

## Part V — Whoa-signature reminder (Stream B distilled)

The piece must hit five signature elements to break out:

1. **A single ownable name attached.** Sibley Creek. The number/chart becomes the citation.
2. **Cross-community distribution mechanic.** Embargo to 4-8 trusted reporters; LinkedIn + Vieira + Argitis-tier wires + Bloomberg Canada.
3. **Right-moment timing.** Land it inside a 2-6 week window when the question is live. FSR and Q1 GDP this week may sharpen the cyclical baseline; the piece should land within ~30 days of an MPO-tranche announcement or budget moment.
4. **Format compression.** A single chart (supply vs demand with Build-Big incremental layer, geographically anchored) + a single number ("Canada is short ~[X]K person-years no federal program has a plan to deliver, concentrated in [geography]").
5. **Institutional engagement potential.** Built so BoC/DoF/PBO/BuildForce/bank-econ-desks would want to engage. Methodology fully reproducible. Sources fully primary. Conclusions policy-actionable.

Plus: the piece IMPLICATES someone — the federal government's framing that Team Canada Strong is Build-Big's labour solution. That implication is what makes it break out.

---

## Part VI — Demand-side methodology specification

### Two-method framing

For each Build-Big project, estimate workforce demand using one of two methods, in order of preference:

**Method 1 — Take the project's own published numbers.**

Source documents, in order of preference:
- Federal IAAC environmental assessment filings (free, public)
- Provincial environmental assessment filings (free, public)
- Regulatory body filings (CER for pipelines, CNSC for nuclear, provincial mining ministries)
- Proponent investor / IR disclosures (annual reports, presentations, regulatory filings)

Project Description sections of EAs almost always include peak workforce and total person-years; some include trade-level breakdowns.

**Method 2 — Analog-plus-scaling from a comparable completed project.**

When the project doesn't have published numbers yet (no FID, no EA filed, pre-proposal stage):
1. Identify the closest analog by project class — Canadian first, US/Australia/Europe second
2. Pull the analog's published workforce numbers (peak workforce, person-years, trade mix where available)
3. Scale linearly by the matching unit for the project class (see scaling units table below)
4. Flag the analog choice and the linearity assumption transparently in the methodology box

### Trade breakdown

Same two-method logic:
- If the project EA breaks it out, take it directly
- If not, use the analog project's trade mix (or, if no project-specific analog exists, the industry-standard ratio for that project class)

Trade-level priority overlay comes separately from BuildForce's 5-tier provincial NOC classification — NOT from Sibley-invented quantitative trade-by-trade gap math.

### Scaling units by project class

| Project class | Scaling unit | Reference projects |
|---|---|---|
| Oil/gas pipelines | per km | TMX: ~58 person-years/km (67,423 person-years over ~1,150 km); Coastal GasLink |
| LNG facilities | per MTPA | LNG Canada Phase 1: ~535 peak workers/MTPA (7,500 peak / 14 MTPA) |
| Nuclear (SMR) | per MW | Vogtle (US, conventional): ~4 peak workers/MW; SMR analogs limited — flag |
| Transmission lines | per km × kV | Site C transmission; Hydro One Bruce-to-Milton |
| Hydroelectric dams | per MW | Site C: ~7 person-years/MW main civils |
| Mines | per tonne capacity or $-capex | McIlvenna Bay EA; Highland Valley; Voisey's Bay |
| Highways (northern) | per km | Inuvik-Tuktoyaktuk (recently completed); past Mackenzie Valley segments |
| Ports | per berth or $-capex | Port of Vancouver expansions; Contrecœur EA |
| Critical minerals processing | per tonne processed | Sayona Lithium; Vital Battery Materials |
| Housing (residential) | per dwelling unit | BuildForce already published — 5.8M homes → +83% workforce / 1,030,000 |

### Honest caveats baked into the methodology

- **Linearity.** Analog scaling is linear by default. Real projects don't scale perfectly linearly (mobilization economies; remote terrain diseconomies; specialty trade plateaus). We address this by (a) using ranges, not point estimates; (b) flagging the linearity assumption transparently; (c) preferring analogs that are close in scale.
- **Industry ratios are imperfect.** Every project has unique features. The piece doesn't claim trade-level quantitative precision — only aggregate person-year gaps + qualitative trade priority from BuildForce.
- **Geographic mismatch.** Workers in Alberta don't automatically deploy to Ontario. Interprovincial mobility is real but bounded.
- **Time-phasing.** Site mobilization → peak → demob. Peak workforce ≠ total person-years. Aggregate by peak window (2027-2029) for concurrence math.

### Methodology box for the published piece (~200 words)

*"For each Build Canada project, we used the proponent's own published workforce numbers where available — sourced from federal and provincial environmental assessment filings, regulatory body filings, and proponent investor disclosures. Where no published numbers exist (typically because a project has not yet been formally proposed), we applied a labour-intensity coefficient from a comparable completed project, scaled to the new project's announced size in the matching unit (kilometres for pipelines, MTPA for LNG, MW for nuclear and hydroelectric, dwelling units for housing, etc.). All analog assumptions are flagged. For trade-level priority, we anchor to BuildForce Canada's published 5-tier provincial NOC classification, rolled up nationally by mapping projects to their geography. Validation comes from phone-call interviews with named sources at building-trades unions, provincial apprenticeship authorities, construction-firm HR leads, college trades-program faculty, and project IR/comms. The piece deliberately does not model smaller projects that lack both published numbers and comparable analogs — those would only ADD to the gap we report."*

---

## Part VII — Piece scaffolding

### Six-section structure (~2,500 words body)

**1. Open** (~200-300 words)
- A concrete hook — a specific project, a specific tradesperson, a specific number
- The central claim stated once, plainly
- One sentence that names the stakes

**2. Setup** (~400-500 words)
- What Build Canada is — the $1T mobilization, the MPO project portfolio, the timeline
- Why workforce is the critical input (3-5 year apprenticeships)
- BuildForce's most recent forecast: ~108K residual shortfall through 2034
- Team Canada Strong: $6B / 80-100K over 5 years
- The arithmetic match + the inferential timing that says BuildForce baseline predates Build Canada

**3. The math** (~600-700 words)
- Sibley's central calculation, walked through plainly
- Supply side: BuildForce by province
- Demand side: MPO project portfolio with workforce estimates, analog-plus-scaling for each
- Peak concurrence 2027-2029, geographically anchored
- The gap, expressed as person-years by province
- The headline number

**4. The work** (~600-700 words)
- How we estimated each project (published numbers where available, analog-plus-scaling where not)
- Scaling units by project class (kept light; full table in methodology box)
- Where BuildForce's 5-tier classification maps onto project demand
- The phone-call texture — what union officials, apprenticeship boards, contractors are seeing
- Honest acknowledgment of uncertainty

**5. The implications** (~300-400 words)
- What this means: schedule slippage or wage inflation, probably both
- Geographic concentration of risk
- What the federal government hasn't published (the missing bridge)
- The incremental-vs-displacement question explicitly addressed
- Realistic reconciliation: announced timeline aspirational; actual delivery much longer

**6. Caveats + forward look** (~200-300 words)
- Modular construction adjustment for housing
- Schedule slippage being endogenous (gap shows up as delays, not shortfall)
- What would change the picture (next BuildForce CMLF; significant immigration recalibration; productivity gains)

**Methodology box at the foot** (~200 words) — see Part VI spec.

### Charts (5-7)

- **Hero:** supply curve vs demand curve with Build-Big incremental layer overlaid, geographically anchored
- BuildForce baseline by province (residential + non-residential)
- MPO project portfolio workforce stack (project-by-project peak workforce)
- Team Canada Strong delivery rate vs BuildForce baseline gap
- Trade-priority overlay (BuildForce 5-tier) mapped to project mix
- Peak concurrency timeline 2027-2029
- (Optional) Geographic heat map: project demand × province × trade

### Executive summary (1 page, ~300-400 words)

For embargo distribution. Reporters scan it in 60 seconds to decide whether to engage with the full piece. Hits:
- Central claim in one sentence
- Headline number with its scope (geography + time window)
- Methodology in one or two sentences (BuildForce + project-by-project analog-plus-scaling + phone-call validation)
- Top 3 implications
- One sentence on what we deliberately don't claim
- Link to full piece

### Length and format conventions

- Body: ~2,500 words
- Methodology box: ~200 words
- Executive summary: 1 page, ~300-400 words
- Total reading time: ~10 minutes for body (250 wpm convention)
- PDF format for embargo distribution + web version on the site
- Total PDF: ~10-12 pages (body + 5-7 charts + methodology + sources + exec summary as cover page)
