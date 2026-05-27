# Build-Big trades gap — quick brief (v2)

**For:** Sibley Creek economist
**Date:** 2026-05-26

---

## What we're proving

The federal government has promised about $1 trillion of new infrastructure — pipelines, LNG terminals, nuclear plants, transmission lines, mines, ports, plus a pledge to double housing construction. They call it "Build Canada." They've also announced a $6 billion program to train 80,000-100,000 new skilled tradespeople over five years.

Here's the problem: Canada was already short about 108,000 tradespeople by 2034, *before* any of this was announced. The new training program is sized to fill that pre-existing hole. It doesn't add any workers for the actual Build Canada projects.

**The piece's argument:** the federal training program addresses Canada's old trades shortage, not the new one Build Canada creates. The government has published no bridge between the program and the projects. Sibley builds that bridge.

---

## Why we know the gap is real

BuildForce Canada (the industry's workforce forecaster) published its most recent forecast in April 2025. That forecast doesn't include Build Canada projects, because the federal Major Projects Office didn't exist until August 2025 — five months after BuildForce modelled. So the 108,000 shortfall is Canada's *baseline* — before Build Canada. Anything Build Canada adds is on top.

---

## The methodology

Simple arithmetic. Supply minus demand equals gap.

**Supply** — take BuildForce's published numbers as-is. They've done the supply forecast for us, free.

**Demand** — for each Build Canada project, two methods in order:

1. **If the project has published workforce numbers, use them.** Most major projects file environmental assessments that say how many workers they need, sometimes broken out by trade. Sources: federal IAAC, provincial registries, regulatory filings (Canada Energy Regulator for pipelines, Canadian Nuclear Safety Commission for nuclear, etc.), company investor materials.

2. **If the project hasn't been formally proposed yet, find a comparable completed project and scale.** TMX is the reference for any new oil pipeline (we know it took 67,423 person-years over ~1,150 km). LNG Canada Phase 1 is the reference for LNG. Site C is the reference for hydro. Scale linearly by the matching unit — kilometres for pipelines, megawatts for nuclear and hydro, MTPA for LNG, etc. Flag every analog assumption transparently.

**Trade priority** — use BuildForce's published 5-tier ranking by province (which trades are most stressed where). Don't invent a new ranking.

**Validation** — call union halls, apprenticeship boards, construction firms, trades college faculty. They confirm whether the math matches the ground reality.

---

## What you're building

For each project on the federal Major Projects Office list (about 15 of them as of now), build a row of a table:

- project name
- location (province)
- capex estimate
- scale (km / MTPA / MW / etc.)
- peak workforce
- total person-years
- trade mix (from EA if available, analog otherwise)
- construction schedule (start / peak / demob years)
- source

Then aggregate by province and by year. Compare against BuildForce's published supply numbers. That's the gap.

---

## First steps

1. Read the supporting files in `business/research/`, especially `buildforce_canada_verification_2026-05.md` and `build_big_trades_gap_working_2026-05-25.md`. They contain the context already done.
2. Pull the MPO project list from canada.ca/en/privy-council/major-projects-office/projects/national.html.
3. For each project, find published workforce numbers if they exist. If not, identify the analog.
4. Build the table above.
5. Aggregate provincially.

For the full methodology spec, scaling-unit reference table, and complete data-source list, see the longer brief (`build_big_trades_gap_brief_2026-05-25.md`).

---

## Contact

Jay Zhao-Murray (Sibley Creek founder). Ask as questions come up.
