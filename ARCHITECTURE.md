# Architecture Decisions

Short ADR-style entries. Newest at the bottom.

---

## ADR-0001: Astro static site, no UI framework integration

**Date:** 2026-05-10
**Status:** Accepted

### Context
This is a content-and-charts dashboard, not an interactive web app. We need
fast page loads, easy authoring of long-form text alongside charts, and the
flexibility to drop in D3 or Astro Plot inside specific pages or components.

### Decision
- Astro 6.x with the official `minimal` template
- TypeScript in `strict` mode (extending `astro/tsconfigs/strict`)
- No React / Vue / Svelte integration at bootstrap
- No CSS framework at bootstrap (Tailwind etc.) - art-director will dictate
  the styling approach in the design system

### Consequences
- Charts will be authored as Astro components, with D3 or Astro Plot used
  inline where needed. If a future chart genuinely needs a reactive UI
  framework, we can `astro add` one then, scoped to those components only.
- Bundle stays close to zero JS by default. Good for Lighthouse.
- frontend-designer owns ongoing `astro.config.mjs` changes; the backend
  agent only set the initial scaffold.

---

## ADR-0002: Monorepo with Python pipeline at `pipeline/`

**Date:** 2026-05-10
**Status:** Accepted

### Context
We need to fetch data (Python is the better ecosystem: pandas, requests,
StatCan/BoC client patterns) and render a static site (Node/Astro). A split
repo would force manual coordination of data contracts.

### Decision
Single repo. Python lives under `pipeline/`. Processed outputs land in
`data/processed/` as CSV + sibling `.meta.json`. The Astro side reads from
`data/processed/` at build time.

### Consequences
- One `git clone`, one place for issues, one CI.
- Two dependency managers: `npm` for Node, `pip` for Python.
- CI will need both runtimes. Cache both lockfiles.
- The disk layout (`data/processed/*.csv` + `*.meta.json`) is the contract
  between the two halves. Treat it as a public API.

---

## ADR-0003: Node 22.12+, Python 3.11+, npm

**Date:** 2026-05-10
**Status:** Accepted

### Context
Astro 6 requires Node >= 22.12.0. Local dev box is on Node 24.15.0 and
Python 3.14.4. We need to fix floors so CI and contributors stay in sync.

### Decision
- Node floor: 22.12.0 (set in `package.json` `engines`)
- Python floor: 3.11 (no pinned `pyproject.toml` yet - will add when the
  first source lands and dependencies need locking)
- Package manager: npm (ships with Node, no extra tooling)

### Consequences
- `pyproject.toml` deferred until there is something to pin. `requirements.txt`
  is a placeholder for now.
- If a contributor lands a dependency that needs Python 3.12+ features, bump
  the floor here first.

---

## ADR-0004: Pipeline reuse from boc-tracker; two-step build

**Date:** 2026-05-10
**Status:** Accepted

### Context
A prior project, `boc-tracker` (at `C:\Users\jayzh\Documents\boc-tracker`),
has 600+ lines of working Python that fetches Canadian macro data from the
same sources we need (StatCan WDS, BoC Valet, FRED, BIS, Alberta WCS,
Indeed Hiring Lab Canada). The user explicitly authorized reuse of that
data infrastructure for this project. boc-tracker also bundles editorial
interpretation (tier classifications, hardcoded narrative thresholds,
blurb prompts) that we do NOT want to inherit - this project's editorial
direction is its own.

### Decision

**Lifted wholesale from boc-tracker:**
- StatCan WDS access pattern: POST to `getDataFromVectorsAndLatestNPeriods`
  with `[{vectorId, latestN}]`, parse `[{status, object: {vectorDataPoint}}]`.
- BoC Valet access pattern: GET `observations/{key}/json?start_date=...`,
  parse `{seriesDetail, observations: [{d, KEY:{v}}]}`.
- The per-series failure isolation pattern (one source down doesn't sink
  the build; failures collected and reported at the end).
- NaN-preserving parsing for StatCan WDS observations with `statusCode=1`
  (structural gaps survive into CSV; chart lines auto-break).

**Adapted (different shape from boc-tracker):**
- Decomposed boc-tracker's monolithic `fetch.py` into `pipeline/fetch/<source>.py`
  modules. One source per file scales as we add CMHC, OSFI, FRED, BIS.
- Replaced the hand-rolled retry loop with `tenacity`-based backoff (cleaner,
  honors 429 / 5xx / network errors, fails fast on 4xx-other).
- Replaced `requests` with `httpx` (per agent file's tooling preferences;
  explicit timeouts, connection pooling).
- Added pydantic validation at the JSON boundary (StatCan and Valet
  responses are now schema-checked before they're trusted).
- Replaced ad-hoc on-disk format (bare CSVs in `data/`) with the ADR-0002
  contract: every CSV has a sibling `.meta.json` recording source URL,
  fetched-at, release date, reference period, units, schema version.
- Replaced inline `pct_change(12)*100` patterns scattered across
  `analyze.py` with a clean `pipeline/transform/timeseries.py` module:
  `yoy_pct`, `pct_change_at_horizon`, `qoq_annualized_pct`,
  `annualize_period_growth`, `moving_average`, `index_to_base`,
  `rebase_to_first`. Editorial interpretation does not live in transforms.

**Intentionally NOT lifted:**
- boc-tracker's series catalog (80+ hardcoded vectors / Valet keys). Series
  scope is editorial-director's call per section; the fetchers take IDs as
  arguments so any caller can register what they want.
- All tier-classifier functions (`_classify_headline_cpi`,
  `_classify_inflation_momentum`, etc.). Those are editorial interpretation
  with hardcoded thresholds; researcher / editorial-director will rebuild
  per the new project's voice.
- `analyze.py`'s blurb-generation harness (Claude prompts + framework
  reading). The new project's editorial workflow is different.
- `build.py`'s Plotly HTML emission. The Astro site renders charts; the
  Python build prepares data only.
- `statsmodels` (HP filter). Not needed for the pipeline core; can be
  added when an editorial use-case requires it.
- The "wait for new release" polling mode (`fetch.py --wait`). Adds
  complexity; if we need it for scheduled-release-morning runs, GitHub
  Actions can retry the workflow rather than baking polling into Python.

### Two-step build
`build.py` in boc-tracker did fetch + transform + render-HTML in one Python
process. We split that here:

1. **Python step** (`python -m pipeline.build`): fetch -> validate ->
   transform -> write CSV + `.meta.json` to `data/raw/` and `data/processed/`.
2. **Node step** (`npm run build`): Astro reads `data/processed/` at build
   time, renders charts and pages, emits the static site to `dist/`.

The two halves share the on-disk contract from ADR-0002. They run
sequentially in CI but are independently runnable for local development.

### Consequences
- Faster CI: the Python step caches its output to `data/`; iterating on
  Astro pages does not re-fetch upstream data.
- Cleaner deploy: only `dist/` ships to GitHub Pages. The `data/processed/`
  files are intermediate artifacts.
- Two dependency managers, two CI cache lanes (already accepted in ADR-0002).
- When editorial-director scopes new series, the work is additive: a new
  task function in `pipeline/build.py` (or a section-specific submodule),
  not a redesign of orchestration.
- Open question for editorial-director / researcher: which sections to
  scope first, and within each, which canonical vector / series key
  expresses the headline indicator. The pipeline is ready to accept that
  list; nothing more is needed on the backend side until it lands.
