# Visual regression harness

Playwright + image-snapshot diffing over the static Astro build. Lives at the
repo root (alongside `pipeline/tests/`) so the test command is one line and
the harness sits outside both `src/` and `pipeline/`.

## What it covers (v1)

9 routes, desktop viewport (1240x800), full-page screenshots:

| Route                          | What it captures                                     |
|--------------------------------|-------------------------------------------------------|
| `/`                            | Homepage hero + 7 SectionPanel mini-charts            |
| `/gdp/`                        | Panels 1-6 stacked                                    |
| `/inflation/`                  | Panels 1-6 stacked                                    |
| `/labour/`                     | Panels 1-6 stacked                                    |
| `/policy/`                     | Panels 1-8 stacked                                    |
| `/markets/`                    | Panels 1-6 stacked                                    |
| `/trade/`                      | Panels 1-6 stacked (Panel 4 = hairline table)         |
| `/housing/`                    | Panels 1-6 stacked                                    |
| `/research/`                   | Research index page                                   |

Deep-dive slug pages (`/research/<slug>/`) are intentionally NOT in the suite.
`src/pages/research/[slug].astro` `getStaticPaths()` filters `deepDives` on
`publishedPath`. No entry carries `publishedPath` yet (drafts only), so those
routes do not build. When a deep dive is promoted to `editorial/published/`,
add its `/research/<slug>/` to `ROUTES` in `routes.spec.ts` and regenerate the
baseline.

Tablet + mobile viewports are explicitly deferred to v2 -- one viewport at a
time keeps baseline maintenance tractable while panels are still moving.

## First-time setup

On a fresh checkout you need both the npm deps AND the Chromium binary that
Playwright drives. `@playwright/test` declares Chromium as a peer install but
does NOT auto-fetch it.

```
npm install
npx playwright install chromium
```

CI's `npm ci` covers step 1; step 2 is required separately and is cached by
the workflow keyed on the pinned `@playwright/test` version.

## How to run

| Command                       | What it does                                                      |
|-------------------------------|-------------------------------------------------------------------|
| `npm run test:visual`         | Overlays fixtures, builds, serves, runs Playwright, restores `data/site/`. |
| `npm run test:visual:update`  | Same flow but regenerates baseline PNGs in `__snapshots__/`.      |
| `npm run test:visual:debug`   | Opens Playwright UI mode (interactive run + diff inspector).      |
| `npm run test:visual:freeze`  | Snapshot current `data/site/` into `data/fixtures/site/` (one-shot). |

The freeze + restore steps are wrapped in `tests/visual/fixture-utils.mjs` so
the orchestration is platform-portable (Windows + ubuntu-latest).

## Fixture mode

The harness is NOT allowed to depend on live data. Live data drift would
generate diffs every day. Instead:

1. The pipeline runs as normal, writing `data/site/sections.json` and
   `data/site/panel_data/*.json`.
2. Once the visuals are stable, an operator runs
   `npm run test:visual:freeze` to copy that snapshot to
   `data/fixtures/site/`. This becomes the fixture corpus committed
   alongside the baseline PNGs.
3. Every `test:visual` run:
   - Saves the current `data/site/` to a temp dir (rollback safety).
   - Copies `data/fixtures/site/` -> `data/site/`.
   - Runs `astro build` and Playwright.
   - Restores `data/site/` from the temp dir, even on failure.

No changes to `pipeline/build.py` are required for fixture mode. Production
builds always run against the real pipeline output; fixture mode is a
test-time overlay.

## Baseline policy

Baselines are committed under `tests/visual/__snapshots__/<spec>/`. PNGs are
already marked `binary` in `.gitattributes`.

**Initial baselines are NOT committed yet** (as of the harness landing, this
file). Per the user brief, "baselines will lock in once panels are visually
stable." The harness sits in CI as a no-op until the first baseline batch
lands. Once chart-builder marks the panels visually stable and the editorial-
director / art-director sign off, run `npm run test:visual:update` and commit
the resulting PNGs in a dedicated commit titled
`test(visual): seed initial baselines`.

## Build-time-date nondeterminism

A handful of components call `new Date()` at build time (`VignelliColophon`,
`HeroChart`, `index.astro`). Those regions are masked in the spec via the
Playwright `mask:` option (see `MASK_SELECTORS` in `visual.spec.ts`).

If the design system later adds a `data-vt-mask` attribute to time-bound
regions, the spec's mask list can be tightened to that single selector.
Until then, the spec masks pragmatic selectors (`time`, `.colophon`, the
hero "as of" stamp) which are sufficient to prevent date-driven flake at
the cost of leaving a small uncovered surface area on the colophon row.

## CI

The visual harness is wired as a separate GitHub Actions workflow
(`.github/workflows/visual-regression.yml`) that runs on `pull_request`
against `main` and on `workflow_dispatch`. It does NOT run on the monthly
data-refresh cron -- visual tests do not exercise data freshness, they
exercise component rendering.

The workflow caches the Playwright browser binary keyed on the Playwright
version pinned in `package.json` so re-installs only happen on a version
bump.

## Debugging a diff

1. Open the HTML report: `npx playwright show-report tests/visual/.playwright-report`
2. Per failed test, the report attaches three PNGs: expected, actual, diff
   (the diff is the pixel-difference image).
3. If the diff is intended (a real visual change), regenerate baselines
   with `npm run test:visual:update`.
4. If the diff is a regression, fix it before merging. The CI job will
   fail until baselines match.
