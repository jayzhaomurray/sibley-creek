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

---

## ADR-0005: Split daily Financial build from monthly main build

**Date:** 2026-05-11
**Status:** Accepted

### Context

The Financial section (canon 4.6 + the daily "what moved overnight"
absorption per `wave1_data_scope_financial_trade.md` Section 1.3) refreshes
every North American trading day at 18:00 ET. Every other section is at
StatCan monthly cadence (LFS, CPI, GDP) or slower. Running the daily
Financial fetchers on the monthly StatCan rhythm wastes CI minutes and
leaves the Financial section stale between StatCan releases.

### Decision

Two entry points, one shared library:

1. `pipeline.build` (monthly + quarterly + ad-hoc fiscal/housing). Runs
   the StatCan catalog filtered to non-financial sections, the BoC Valet
   catalog filtered to non-daily cadence, the DoF Fiscal Monitor scraper,
   and the CREA MLS HPI bulk download. Drives cross-series derivations
   that depend on StatCan inputs.
2. `pipeline.build_financial` (daily, scheduled 18:00 ET). Runs the BoC
   Valet catalog filtered to daily cadence, the FRED catalog, the Yahoo
   catalog, and Financial-side derivations (GoC-UST spreads).

Both inherit a single failure-isolation primitive (`_safe()`) lifted from
boc-tracker's `fetch.py:484-494`: per-series exceptions are logged and
appended to a `failed` list; the script exits non-zero if anything
failed, so GitHub Actions surfaces the failure list in the run UI without
the rest of the day's data being lost on disk.

### Consequences

- Daily Financial CI is fast and tight: ~15 BoC daily + 10 FRED + 3 Yahoo
  series, plus spread derivations. Should run in under a minute.
- Monthly build re-runs the heavier StatCan catalog (82 series) plus CREA
  XLSX parsing and DoF HTML scraping. Slower, but only at StatCan
  release cadence.
- The on-disk contract (CSV + `.meta.json` in `data/raw/`,
  `data/processed/`) is shared; downstream Astro never sees the split.
- Adding a new daily-cadence series is one catalog entry; adding a new
  monthly series is one catalog entry. Orchestration code does not
  change.
- Open question for ops: GitHub Actions cron for the daily Financial
  build, including weekend skipping (markets closed Sat-Sun; no point
  re-fetching). Deferred until CI lands.

---

## ADR-0006: GitHub Actions cron lands; workflows in ready-to-enable state

**Date:** 2026-05-11
**Status:** Accepted (resolves the open question in ADR-0005)

### Context

ADR-0005 deferred the cron specifics until CI landed. Frontend rebuild is
in flight on the homepage; the pipeline side is unblocked. The repository
does not yet have a `git remote` configured, so we cannot test the
workflows against live GitHub schedulers -- but committing the files now
means the cron starts firing automatically the moment a remote is wired up.

### Decision

Two workflow files under `.github/workflows/`, both in READY-TO-ENABLE
state:

1. `build-financial-daily.yml` -- runs `python -m pipeline.build_financial`
   Mon-Fri at 22:00 UTC (18:00 EDT / 17:00 EST), per ADR-0005 + the
   wave1_data_scope_financial_trade.md Section 1.3 hand-off note.
2. `build-monthly.yml` -- runs `python -m pipeline.build` on the 1st of
   each month at 17:00 UTC. Single-shot monthly refresh; we explicitly
   chose this over per-release-day workflows for v1 simplicity.

Both workflows:
- Use `actions/setup-python@v5` with `python-version: "3.12"` and pip
  caching keyed on `pipeline/requirements.txt`.
- Pass `FRED_API_KEY` from repo secrets; the pipeline's `_safe()` already
  handles its absence as a flagged failure rather than a hard stop.
- Use `continue-on-error: true` on the build step so partial-failure
  exit codes do NOT skip the commit step; the run still surfaces red via
  a final "surface" step that re-raises the build outcome.
- Commit in-place with `git diff --cached --quiet` to skip empty commits.
- **Do not push to a remote**; the repo has no remote yet. Once a remote
  lands, a follow-up ADR can decide whether to push from the workflow
  token or push via a manual PR-then-merge flow.

Concurrency groups prevent overlap (one daily run at a time; one monthly
run at a time). Timeouts: 10 min daily, 30 min monthly.

### Consequences

- Zero remote-side action required to merge these in. They commit, but
  the commits stay local to the runner's checkout until a remote is
  added and a push policy is decided.
- The daily build runs in under a minute against the live APIs (per
  ADR-0005); the 10-min timeout gives wide headroom for FRED rate-limit
  retries.
- GitHub's cron is UTC-only -- the daily slot drifts 1 hour between EST
  and EDT. We accept the drift: 17:00 ET vs 18:00 ET both post-date the
  EDT close (16:30 ET) for BoC daily series and the FRED end-of-day push.
- Adding a remote later: the workflows are intentionally remote-agnostic.
  Once `git remote add origin ...` lands and a default branch lives on
  github.com, the schedules begin firing without any workflow edits.
- The CBA mortgage-arrears blocker is captured in `data/SOURCES.md`
  rather than absorbed into the build; it is a known gap, not a silent
  one. Headless-browser fetching would close it but adds a heavy CI
  dependency for a single monthly indicator; deferred.

### Workstream B catalog additions (recorded here for traceability)

- BoC Valet `FVI_TP_GOC_10Y_ACM` and `FVI_TP_GOC_10Y_SHADOWRATE` --
  Canadian 10-year GoC term premium (ACM + shadow-rate models). An
  earlier catalog comment said "NOT FOUND in Valet"; a re-probe with a
  broader regex (`FVI_TP_GOC_*`) found both. Canon 4.6 element 2 v1
  basics requirement met without scraping the FSI page.
- BoC Valet `FVI_FSI_CAN` -- Canadian Financial Stress Index. Daily.
  Surfaced as a regime classifier next to the term-premium read.
- `pipeline/fetch/alberta.py` + `fetch_natural_gas_price()` -- Alberta
  Economic Dashboard monthly natural-gas reference price (C$/GJ, AECO-
  equivalent monthly settle). Weekly bid-week is gated behind NGX
  subscription; canon 4.6 element 4 v1 fallback to monthly cadence.
- `data/SOURCES.md` -- adds the Alberta Dashboard subsection in full
  (was a TODO stub) and documents the CBA Sucuri-JS-challenge blocker.

---

## ADR-0007: Visual regression via Playwright + fixture-mode overlay

**Date:** 2026-05-11
**Status:** Accepted (harness landed; first baselines NOT yet committed)

### Context

The site renders 43+ hand-rolled SVG chart panels (7 section pages x 6
plates each, plus Policy +2, minus Trade Panel 4 which is a hairline
table). Each panel computes geometry from JSON inputs at build time.
Once `panel_data/*.json` is wired into the section pages, a regression
in any panel -- wrong scale, axis-label clip, misplaced dot, missing
frame -- would ship silently. Live data changing day-to-day would also
flag false positives unless filtered.

### Decision

Adopt Playwright's `@playwright/test` runner with `toHaveScreenshot`
full-page snapshot diffing, with an overlay-style "fixture mode" for
deterministic data.

- **Tool:** `@playwright/test` (^1.49). Vendor-free, single browser
  binary (Chromium), built-in HTML report with diff PNGs. Considered
  Percy / Chromatic / Argos -- rejected for vendor lock-in and the
  fact that none materially beat Playwright for a zero-JS static
  site where the diffs are entirely server-rendered SVG.
- **Harness location:** new `tests/visual/` directory at the repo
  root, distinct from `pipeline/tests/`.
- **Coverage v1:** 12 routes (home, 7 section pages, research index,
  3 research deep-dives), desktop only (1240x800), full-page mode so
  every panel on a section page diffs together.
- **Fixture mode:** the harness copies `data/fixtures/site/` over
  `data/site/` before `astro build`, with a backup that always
  restores (even on Ctrl-C). This avoids modifying `pipeline/build.py`
  and keeps production builds untouched. Operator runs
  `npm run test:visual:freeze` once to seed the corpus from the
  current pipeline output; the corpus is committed alongside the
  baseline PNGs.
- **Build-time-date masking:** `new Date()` is called at build time
  in a few components (VignelliColophon, HeroChart, index.astro hero
  band). Those regions are masked via Playwright's `mask:` option
  using CSS selectors. A `data-vt-mask` attribute hook on src/ would
  tighten this; deferred until art-director / frontend-designer
  decide whether to add the hook.
- **Baseline storage:** `tests/visual/__snapshots__/`. PNGs gated
  binary by `.gitattributes` (already in place).
- **Baseline gating policy:** the CI workflow detects whether any
  baselines exist and no-ops cleanly when they do not. This lets the
  harness land BEFORE chart-builder marks panels visually stable.
- **CI:** new `visual-regression.yml` workflow, triggered on
  pull_request to `main` for `src/**`, `tests/visual/**`,
  `data/fixtures/**`, `playwright.config.ts`, `astro.config.mjs`.
  Caches the Playwright browser binary by version. Uploads HTML
  report + raw diff PNGs on failure.

### Consequences

- The harness sits in CI immediately but is a no-op until baselines
  are seeded. Once chart-builder + editorial-director call panels
  stable, a single commit (`test(visual): seed initial baselines`)
  locks them in, the gate flips, and the regression check goes live.
- Live-data drift never flags the harness because the fixture
  overlay swaps in a pinned snapshot. The corpus IS pinned data, by
  definition; if the editorial team wants a more recent fixture,
  they re-freeze + re-baseline in a single deliberate commit.
- `pipeline/build.py` is untouched. Fixture mode is a test-time file
  overlay, not a pipeline branch.
- The `mask:` approach leaves a small visually-uncovered band around
  the build-time-date regions (colophon, hero stamp). The trade-off
  is documented in `tests/visual/README.md`; tightening to
  `data-vt-mask` is a future src/ change owned by frontend-designer.
- Tablet + mobile viewports defer to v2. One viewport at a time
  keeps baseline maintenance tractable while panel visuals are still
  in flight.
