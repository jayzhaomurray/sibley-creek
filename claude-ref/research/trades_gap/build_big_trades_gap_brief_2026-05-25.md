# Build-Big skilled-trades gap — research brief

**For:** Sibley Creek economist
**Date:** 2026-05-25
**Status:** Pre-build. BuildForce verification complete; methodology locked.

---

## 1. What we're doing

Sibley Creek is producing an analytical research piece on whether Canada has the skilled-trades workforce to execute the Carney government's "Build Canada" agenda on the schedule announced.

**Build Canada (also called "Build-Big")** is the Carney government's signature economic agenda since taking office in March 2025. Headline: ~$1 trillion in new infrastructure — a new west-coast oil pipeline, LNG export terminals, nuclear small modular reactors, transmission lines, mines, ports, plus a pledge to double home construction to 500,000 starts a year. Federal government commits ~$280 billion; expects to mobilize another ~$720 billion from private capital, provinces, and Indigenous equity. ~15 major projects have been formally referred to the federal Major Projects Office (MPO) across three tranches (Sept 2025, Nov 2025, March 2026).

The federal labour response is **Team Canada Strong**, announced April 29, 2026: $6 billion to train 80,000-100,000 new Red Seal trades workers over five years.

**The piece will argue:** Team Canada Strong is sized to fix Canada's pre-existing trades shortfall (BuildForce's published ~108,000 baseline residual through 2034). It does NOT address the incremental labour demand from the Build Canada project portfolio. The federal government has published no bridge between the trades program and Build Canada's project demand. Sibley computes that bridge.

**Headline output:** aggregate person-year gap by province and trade-priority overlay, anchored to peak project concurrence 2027-2029.

---

## 2. The arithmetic spine

**Supply side (BuildForce Canada):**
- Most recent forecast: Construction and Maintenance Looking Forward (CMLF) 2025-2034, released April 4, 2025
- Headline national numbers: 380,500 total hiring needed through 2034; ~270,000 retirements; 111,600 growth demand; ~108,300 residual shortfall absent intervention
- Published only in aggregate (residential + non-residential, by province). Trade-level detail is in the paid product ($10K subscription — not needed for this piece)
- Provincial Highlights publish a **5-tier NOC classification** ranking which trades are most stressed by province

**Federal labour response (Team Canada Strong):**
- $6B / 80,000-100,000 new Red Seal workers over 5 years
- ~16-20K net new workers per year
- Roughly equal to the BuildForce baseline residual shortfall — closes the pre-existing gap, no headroom for Build-Big incremental

**Inferential foundation:**

BuildForce's April 2025 forecast was modelled with a late-2024 cutoff. The MPO didn't launch until August 29, 2025. The first project tranche came September 11, 2025. Build Canada is the federal response to US-Canada trade tensions that emerged in late 2024 / early 2025.

**Therefore BuildForce's baseline cannot include MPO projects — the MPO project list didn't exist when they modelled.** This is the analytical foundation: the Build Canada incremental layer exists definitionally outside the BuildForce baseline.

---

## 3. Methodology

The structure is arithmetic. Supply minus demand equals gap. No econometric modelling.

### Supply side

Take BuildForce's published numbers as given. Source: their CMLF 2025-2034 national + provincial Highlights (free, public, on buildforce.ca).

### Demand side — two-method framing

For each Build Canada project, estimate workforce demand using ONE of two methods, in order of preference:

**Method 1 — Take the project's own published numbers.**

Source documents:
- Federal IAAC environmental assessment filings
- Provincial EA filings
- Regulatory body filings (CER for pipelines, CNSC for nuclear, provincial mining ministries)
- Proponent investor/IR disclosures (annual reports, presentations, regulatory filings)

EA Project Description sections almost always include peak workforce and total person-years. Some include trade-level breakdowns.

**Method 2 — Analog-plus-scaling from a comparable completed project.**

When the project hasn't filed an EA yet (no FID, pre-proposal stage):

1. Identify the closest analog by project class — Canadian first, US / Australia / Europe second
2. Pull the analog's published workforce numbers (peak workforce, total person-years, trade mix where available)
3. Scale linearly by the matching unit (see table below)
4. Flag the analog choice and linearity assumption transparently

### Trade breakdown

Same two-method logic:
- If the project EA breaks it out, take it directly
- If not, use the analog project's trade mix (or industry-standard ratios for that project class)

Trade-level priority for the piece's interpretation comes SEPARATELY from BuildForce's 5-tier provincial classification — NOT from Sibley-invented quantitative trade-by-trade gap math.

### Scaling units by project class

| Project class | Scaling unit | Reference projects |
|---|---|---|
| Oil/gas pipelines | per km | TMX: ~58 person-years/km (67,423 person-years / ~1,150 km); Coastal GasLink |
| LNG facilities | per MTPA | LNG Canada Phase 1: ~535 peak workers/MTPA (7,500 peak / 14 MTPA) |
| Nuclear (SMR) | per MW | Vogtle (US, conventional): ~4 peak workers/MW; SMR analogs limited — flag |
| Transmission lines | per km × kV | Site C transmission; Hydro One Bruce-to-Milton |
| Hydroelectric dams | per MW | Site C: ~7 person-years/MW main civils |
| Mines | per tonne capacity or $-capex | McIlvenna Bay EA; Highland Valley; Voisey's Bay |
| Highways (northern) | per km | Inuvik-Tuktoyaktuk; past Mackenzie Valley segments |
| Ports | per berth or $-capex | Port of Vancouver expansions; Contrecœur EA |
| Critical minerals processing | per tonne processed | Sayona Lithium; Vital Battery Materials |
| Housing (residential) | per dwelling unit | BuildForce: 5.8M homes → +83% workforce / 1,030,000 workers |

### Honest caveats baked in

- **Linearity.** Analog scaling is linear by default. Real projects don't scale perfectly linearly (mobilization economies; remote terrain diseconomies). Use ranges, not point estimates. Prefer analogs close in scale.
- **Industry ratios are imperfect.** Every project has unique features. Piece doesn't claim trade-level quantitative precision.
- **Geographic mismatch.** Workers in Alberta don't automatically deploy to Ontario.
- **Time-phasing.** Site mobilization → peak → demob. Peak workforce ≠ total person-years.

### What we deliberately DON'T model

- C/D-grade projects with neither published numbers nor close analogs (very small or genuinely unprecedented). These would only ADD to the gap, not subtract — flag as "additional gap not modelled."
- Productivity changes beyond a documented modular adjustment for housing (~30% labour-per-unit reduction, cited).
- Schedule-slippage scenarios. The piece's claim is about the AT-ANNOUNCED-PACE gap.

---

## 4. Data sources

**Supply side:**
- BuildForce CMLF 2025-2034 national + provincial Highlights — [buildforce.ca/en/resource-centre/](https://www.buildforce.ca/en/resource-centre/)
- Statistics Canada Labour Force Survey by NOC code — Table 14-10-0022-01
- BuildForce's 5-tier provincial NOC classification — embedded in provincial Highlights PDFs

**Demand side (project workforce):**
- MPO project list — [canada.ca/en/privy-council/major-projects-office/projects/national.html](https://www.canada.ca/en/privy-council/major-projects-office/projects/national.html)
- Federal IAAC environmental assessments — [iaac-aeic.gc.ca](https://www.canada.ca/en/impact-assessment-agency.html)
- Provincial EA registries (varies by province)
- Project proponent IR disclosures (company websites, SEDAR filings)
- Key analogs to pull: TMX (CER); LNG Canada Phase 1 (BC EAO); Site C (BC EAO); Coastal GasLink; Vogtle (US NRC for nuclear conventional); Hydro One Bruce-to-Milton (OEB) for transmission

**Validation (phone calls):**
- BuildForce themselves — research / forecast lead
- Provincial apprenticeship boards (Skilled Trades Ontario, AIT Alberta, ITA BC)
- Union locals — business managers / secretary-treasurers (UA pipefitters, IBEW electricians, Boilermakers, Operating Engineers, Iron Workers)
- Construction firm HR leads (PCL, EllisDon, Aecon, Ledcor)
- Project IR/comms (Cedar LNG, OPG, Pembina)
- College trades-program faculty (BCIT, NAIT, SAIT, Algonquin, Conestoga)
- First Nations economic-development corps via Fasken / Torys Indigenous-equity counsel

---

## 5. Piece scaffolding

Target: **~2,500 words body + ~200-word methodology box + 1-page executive summary**. 5-7 charts. PDF format for embargo distribution + web version. ~10 minute read.

### Six-section structure

1. **Open** (~200-300 words) — concrete hook + central claim + stakes
2. **Setup** (~400-500 words) — what Build Canada is, BuildForce baseline, Team Canada Strong sizing, the inferential timing argument
3. **The math** (~600-700 words) — Sibley's central calculation walked through; supply baseline + demand overlay; the headline gap number
4. **The work** (~600-700 words) — how each project was estimated; scaling logic; trade-priority overlay; phone-call texture
5. **The implications** (~300-400 words) — schedule slippage vs wage inflation; geographic concentration; the missing federal bridge; the incremental-vs-displacement question
6. **Caveats + forward look** (~200-300 words) — modular adjustment for housing; schedule-slippage-being-endogenous; what would change the picture

### Charts (5-7)

- **Hero:** supply curve vs demand curve with Build-Big incremental layer overlaid, geographically anchored
- BuildForce baseline by province (residential + non-residential)
- MPO project portfolio workforce stack (peak workforce by project)
- Team Canada Strong delivery rate vs BuildForce baseline gap
- Trade-priority overlay (BuildForce 5-tier) mapped to project mix
- Peak concurrency timeline 2027-2029
- (Optional) Geographic heat map: project demand × province × trade

### Methodology box (~200 words, at the foot)

*"For each Build Canada project, we used the proponent's own published workforce numbers where available — sourced from federal and provincial environmental assessment filings, regulatory body filings, and proponent investor disclosures. Where no published numbers exist, we applied a labour-intensity coefficient from a comparable completed project, scaled to the new project's announced size in the matching unit (kilometres for pipelines, MTPA for LNG, MW for nuclear and hydro, etc.). All analog assumptions are flagged. For trade-level priority, we anchor to BuildForce Canada's published 5-tier provincial NOC classification, rolled up nationally by mapping projects to their geography. Validation comes from phone-call interviews with named sources at building-trades unions, provincial apprenticeship authorities, construction-firm HR leads, college trades-program faculty, and project IR/comms. The piece deliberately does not model smaller projects that lack both published numbers and comparable analogs — those would only ADD to the gap we report."*

---

## 6. Supporting research files (in `business/research/`)

Already done — these provide context but don't need to be re-derived:

- `build_big_trades_gap_working_2026-05-25.md` — full working doc with editorial reasoning, skeptic responses, timing strategy
- `build_big_answered_vs_open_2026-05.md` — Build Canada landscape (all components, what's answered vs open)
- `buildforce_canada_verification_2026-05.md` — BuildForce verification, methodology, governance, what's free vs paid
- `skilled_trades_gap_methodology_2026-05.md` — full methodology note with data quality grades + comparable prior analyses
- `team_canada_strong_reactions_sweep_2026-05.md` — 4-week reaction sweep; confirms nobody has made the comparison Sibley will make
- `canadian_macro_coverage_landscape_2026-05.md` — Canadian macro publisher landscape
- `biggest_canadian_macro_question_2026-05.md` — empirical triangulation of topically hottest Canadian macro question (Build-Big)

---

## 7. First steps

Suggested order of operations:

1. **Read the supporting files.** Priority: BuildForce verification → skilled-trades methodology → Build-Big answered-vs-open.
2. **Pull the MPO project list** from canada.ca and triage by data-availability. For each project: tranche date, proponent, location, capex estimate, EA status (filed / in progress / not yet).
3. **For each project, identify the best workforce-data source.** Method 1 (published) where possible; Method 2 (analog) where not. Document the analog choice and scaling assumption explicitly.
4. **Pull the analog data.** TMX, Site C, LNG Canada Phase 1, Coastal GasLink, Vogtle, Hydro One Bruce-to-Milton (as needed by project class).
5. **Build the project-by-project workforce table.** Columns: project, location (province), tranche, capex, scale (km/MTPA/MW/etc.), peak workforce, total person-years, trade mix (from EA if available, analog otherwise), construction schedule (start/peak/demob year), data source.
6. **Aggregate by province and by year.** Build the peak-concurrence chart for 2027-2029.
7. **Pull BuildForce's provincial 5-tier NOC classifications.** Overlay on project demand to identify trade-priority alignment.
8. **Compare against BuildForce supply baseline by province.** That's the gap.

### Methodology defense

Every quantitative claim should cite either BuildForce, a government EA filing, a regulatory body filing, or a proponent disclosure. No Sibley-invented numbers. Every analog scaling assumption flagged transparently.

### Timeline

Aim for completion of demand-side build in 2 weeks. Validation phone calls overlap. Draft within 4 weeks total.

### Contact for editorial questions

Jay Zhao-Murray (Sibley Creek founder). Reach out as questions arise.
