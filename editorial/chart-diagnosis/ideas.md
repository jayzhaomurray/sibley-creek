# Chart ideas — parking lot

Ideas that don't yet have a home, or are too good to lose but aren't
ready to build. Anything substantive that comes out of diagnosis,
strategic discussion, or a late-night thought lands here until it
gets placed.

Each entry: where it came from, the concept in one paragraph,
candidate homes, status.

---

## Productivity: Canada vs US level, indexed to 2000

- **Origin:** chart-diagnosis/gdp.md P6 — deleted from cyclical GDP page 2026-05-12. Productivity is a structural story, not cyclical, so it doesn't earn its place on the GDP page; the idea is too good to lose.
- **Concept:** Long-run productivity level — Canada and the United States, both indexed to 100 at 2000. The widening gap from ~2014 is the structural story (post-oil-collapse, investment drought, regulation, take your pick of hypotheses).
- **Title direction:** "Canadian productivity has stopped converging to US levels." Or sharper.
- **Candidate homes:** Research deep dive on Canadian productivity ("Why Canadian productivity stopped growing"); a structural-economy section if we add one; the Trade page since US comparison is implicit; a labour-page appendix.
- **Status:** parked, awaiting placement decision.

---

## Productivity / Unit Labour Costs deep dive (or recurring section)

- **Origin:** chart-diagnosis labour P2 wage-band scoping 2026-05-13. Editorial-director scoped Labour P2 to LFS-Micro + LFS-all only, cutting SEPH. SEPH belongs on a productivity / ULC surface, not on the Labour tracker. Separately, the productivity Canada-vs-US chart was parked earlier (from GDP P6 cut) for the same future home.
- **Concept:** Sibley's productivity surface answers "Are Canadian unit labour costs growing faster than productivity can absorb — i.e. is the labour share of inflation pressure widening?" ULC = (SEPH weekly earnings / SEPH hours) ÷ (real GDP per hour worked). Companion charts: Canada vs US productivity level since 2000 (indexed); SEPH-derived ULC trajectory; productivity by industry decomposition.
- **Why it earns a deep dive specifically:** Canada's productivity weakness is a multi-year structural story the BoC repeatedly flags. It doesn't fit on a tracker plate (too slow-moving, too analytical). A deep dive can carry the historical context + the cyclical implications + the methodology in one piece.
- **Status:** parked, awaits commission. Two prior parked ideas (productivity Canada-vs-US, SEPH placement) converge here.

---

## Labour gross-flows decomposition for the LFS headline chart

- **Origin:** chart-diagnosis/labour.md P1 — user proposed a third LFS chart that overlays the unemployment rate as a line on top of stacked bars decomposing the cyclical gross flows (entering / exiting the labour force, hired / lost-job). Two of the three replacement charts shipped (small multiples + indexed); the decomp is the third and is tabled.
- **Why parked:** there is no published StatCan cube for the monthly E/U/N transition matrix. The standard 14-10 tables carry stocks only. The canonical way to get gross flows is matched-rotation linking on LFS microdata.
- **PUMF cannot produce true flows (researcher 2026-05-12).** The original 1-2 day estimate was wrong. The Public Use Microdata File (71M0001X) strips the variables needed for individual matched-rotation linking — province × CMA × rotation-group × age × sex × education × household-composition keys are coarsened or suppressed for confidentiality. Source: Brochu (2021), *Canadian Public Policy* 47(3), explicitly: "The variables needed for individual identification are suppressed in the public use files, which means mini-panel analysis can only be carried out using the master files." Corroborated by StatCan RDC documentation; the BoC's Staff Analytical Notes (SAN 2019-4, SAN 2025-17) all use the master file via RDC.
- **Three real paths:**
  - **Path A (current decision, 2026-05-12):** don't build; live page ships the UR identity decomposition in plain English (`Panel2URDecomp.astro`); cite published analyses (BoC SAN 2019-4, StatCan 75-004-M, "Labour market dynamics since the 2008/2009 recession") when the question arises editorially.
  - **Path B:** apply for StatCan RDC access. 3-6 month institutional process (application, deemed-employee oath under the Statistics Act, output vetting before any number leaves the RDC). Unlocks a research-grade flows series, but out of scope for solo v1.
  - **Path C:** build PUMF flow-proxies (duration-based: job tenure < 1mo for recent hires, U-duration = 0 for new U-entrants, with X-13 seasonal adjustment). ~2-3 day backend lift. Outputs are NOT true matched-rotation flows; ships as "flow proxies" with methodology disclosed. Lives in alternates.
- **Status:** parked under Path A. Path C is the only buildable proxy; Path B is institutionally gated.

---

## Pass-through to CPI: FX and wages into goods and services

- **Origin:** chart-diagnosis/inflation.md P6 — cut from inflation page 2026-05-12. Concept "interesting" but USDCAD has been choppy without a clear trend, and a clean pass-through chart probably needs a model rather than a raw two-line overlay.
- **Concept:** Decomposition of what drives inflation pass-through. Real-time identification of channels: FX (USDCAD into goods-ex-energy CPI), wages (LFS-Micro wage growth into services-ex-shelter CPI), commodity (oil into energy CPI).
- **Why it's parked:** the simple "USDCAD Y/Y vs goods-ex-energy CPI" overlay doesn't carry the analytical work the question deserves. A real pass-through view needs estimated elasticities and a structural decomposition (Bayesian VAR, projection method, or similar).
- **Candidate homes:** a Research deep dive on "What's driving the recent inflation reacceleration," not a chartbook plate. The decomposition + a single headline chart could anchor that piece.
- **Status:** parked, awaits modeling work.

---

## Provincial GDP wiring (backend lift)

- **Origin:** chart-diagnosis discussion 2026-05-12. The new industry plate (manufacturing vs mining and oil) carries the regional dimension editorially via title and blurb, but the geometry is industry-only. To show the regional story directly — Alberta and Saskatchewan resource economies vs Ontario and Quebec manufacturing economies — we need provincial real GDP series in the pipeline.
- **Concept:** Wire StatCan Table 36-10-0222 (provincial GDP at basic prices, annual or quarterly real chained 2017) into the data pipeline. Two-line chart: AB+SK total Y/Y vs ON+QC total Y/Y, multi-year. The regional divergence is the geometry.
- **Title direction:** "Alberta and Saskatchewan are growing while Ontario and Quebec are stalling."
- **Required pipeline work:** add provincial GDP fetcher to pipeline/fetch/, add SlotSpec wiring, regenerate panel_data. Could also unlock provincial GDP-by-industry combinations (e.g. Alberta mining + manufacturing vs ON/QC manufacturing).
- **Candidate homes:** GDP page (third industry plate that completes the regional dimension), or its own structural-economy section if we add one.
- **Status:** parked, backend ticket required. Note: provincial GDP is annual or quarterly cadence (slower than monthly industry), which is part of why it didn't make v1.

---

