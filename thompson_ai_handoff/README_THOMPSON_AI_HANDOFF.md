# Thompson AI Handoff — Build-Big Trades Gap

**Purpose:** This folder is the self-contained research packet for Thompson's AI assistant.

**Project:** Sibley Creek Build-Big trades-gap piece.

**Core question:** Does Carney's Build Canada / Major Projects Office portfolio create skilled-trades demand beyond the shortage already captured in BuildForce Canada's 2025-2034 construction-labour baseline?

---

## Working Thesis

Carney's recruitment strategy solves the old construction worker shortage while his industrial policy creates another.

BuildForce already projected a large construction-trades shortfall before the Major Projects Office existed. Team Canada Strong is sized to address that pre-existing baseline. The Sibley Creek task is to estimate the incremental labour demand from the MPO project portfolio and test whether the federal labour math closes.

---

## Thompson's Immediate Job

Build the demand-side table.

For every project in `build_big_trades_gap_project_inventory_2026-05-26.md`, produce:

- project name;
- province / geography;
- construction start, peak, and demobilization years;
- peak construction workforce;
- total person-years;
- direct vs indirect jobs split where available;
- trade mix where available;
- source URL and source type;
- method: published source or analog-plus-scaling;
- confidence grade;
- unresolved questions.

The first useful deliverable is not a polished memo. It is a clean, auditable project-level demand table.

---

## Source Hierarchy

Use sources in this order:

1. Environmental assessment filings: IAAC, provincial EA registries, CER, CNSC.
2. Proponent investor relations, annual reports, construction updates, technical reports.
3. Government releases only when they provide project-specific numbers.
4. Trade press only as a pointer to primary sources.
5. Analyst notes / media claims only as context, not authority.

If a number is not verifiable, flag it. Do not launder it into the table.

---

## Demand Methods

### Method 1: Published Workforce Numbers

Use this when a project has public workforce numbers from an EA, regulator, proponent disclosure, or investor material.

Capture whether the number is:

- peak workforce;
- average workforce;
- total jobs;
- direct construction jobs;
- direct + indirect + induced jobs;
- total person-years.

Do not mix these concepts. A "jobs" headline is usually not a person-year estimate.

### Method 2: Analog-Plus-Scaling

Use this when no project-specific workforce number exists.

Pick the closest completed or active analog, then scale by the relevant unit:

- pipelines: per km;
- LNG: per MTPA;
- hydro / nuclear: per MW;
- transmission: per km and voltage class;
- mines: per capacity unit or capex;
- roads: per km;
- ports: per berth or capex.

Every analog assumption must be visible in the table.

---

## High-Priority First Pulls

Start with these because they anchor the whole model:

1. Darlington SMR: OPG / CNSC / OPG communications.
2. LNG Canada Phase 1 and Phase 2: LNG Canada, Fluor, BC filings.
3. Contrecoeur Terminal: IAAC project 80116, Port of Montreal.
4. Canada Nickel Crawford: IAAC project 83857, company materials.
5. TMX: EY Economic Impact Assessment and Trans Mountain jobs/procurement material.
6. Foran McIlvenna Bay: hiring pages and project updates for mining trade mix.

---

## Specific Numbers To Verify

Do not use these until verified and classified:

- Mackenzie Valley Highway: "14,000+ construction jobs."
- Contrecoeur Terminal: "~4,000 construction jobs."
- Darlington SMR: "18,000 jobs/year" fleet construction average.
- TMX: 67,423 person-years over roughly 1,150 km.
- Carney-Smith pipeline route length and construction timing.
- PRGT pipeline status and whether it is already inside BuildForce's baseline.

---

## Do Not Count In The Primary MPO Aggregate

Keep these outside the primary MPO aggregate unless the methodology changes:

- McIlvenna Bay construction demand: mostly already complete; track for trade-mix proxy.
- Pickering 5-8: not MPO-referred; likely in BuildForce baseline.
- Bruce C: not MPO-referred; likely in BuildForce baseline.
- Cedar LNG: not MPO-referred and already under construction.
- Pathways Alliance CCS: not a standalone MPO project; proponent job claims are not verified.
- Alto HSR: likely outside the 2027-2029 peak-concurrence window.

---

## Output Thompson Should Produce First

By the first checkpoint, produce:

1. A populated demand table for all Method 1 projects.
2. A draft analog table for all Method 2 projects.
3. A list of unresolved source gaps.
4. A top-five list of swing assumptions.
5. A "do not count / count separately" list with reasons.

---

## How To Use The Files In This Folder

Read in this order:

1. `thompson_handoff_brief_2026-05-26.md`
2. `build_big_trades_gap_brief_v2_2026-05-26.md`
3. `build_big_trades_gap_project_inventory_2026-05-26.md`
4. `build_big_trades_gap_working_2026-05-25.md`
5. `skilled_trades_gap_methodology_2026-05.md`
6. `buildforce_canada_verification_2026-05.md`
7. `build_big_trades_gap_sources.md`
8. `build_big_answered_vs_open_2026-05.md`
9. `team_canada_strong_reactions_sweep_2026-05.md`
10. `thompson_briefing_agenda_2026-05-27.md`

The project inventory is the working table. The methodology files explain how to fill it. The sources file should be extended as new sources are found.

