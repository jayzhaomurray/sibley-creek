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

