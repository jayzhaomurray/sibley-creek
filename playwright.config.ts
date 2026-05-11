/*
 * Playwright config for visual regression on macro-research-department.
 *
 * Why Playwright (not Percy/Chromatic/Argos)?
 * --------------------------------------------
 * - Vendor-free: runs against the static build, no hosted service or token.
 * - Native full-page screenshot + diff (`toHaveScreenshot`) with a
 *   `maxDiffPixels` knob; covers our anti-aliasing nondeterminism without
 *   pulling in pixelmatch separately.
 * - Plays nicely with our existing `astro preview` server: the
 *   `webServer` block builds + serves the site for the test run and tears
 *   down on exit, so the harness is one command (`npm run test:visual`).
 * - Single browser binary (Chromium) keeps the CI install footprint low
 *   versus a hosted-service alternative that still requires Playwright on
 *   top.
 *
 * Determinism notes
 * -----------------
 * The site is zero-JS, server-rendered SVG. Charts compute deterministic
 * geometry from JSON inputs. The two nondeterminism sources are:
 *   (1) Live data drift between builds. Handled via fixture mode: tests
 *       overlay `data/fixtures/site/` onto `data/site/` before running
 *       `astro build`. See `tests/visual/fixture-utils.ts`.
 *   (2) Build-time `new Date()` calls in a few components (VignelliColophon,
 *       index.astro hero band, HeroChart axis stamp). These vary by day.
 *       Handled via Playwright `mask:` selectors per spec -- see the spec
 *       file for the canonical list. Once src/ gains a `data-vt-mask`
 *       attribute hook on time-bound regions, the masks tighten up.
 *
 * Viewports
 * ---------
 * v1 captures DESKTOP ONLY (1240x800). Tablet/mobile join in v2 once
 * baselines stabilize at one viewport.
 */
import { defineConfig } from "@playwright/test";

const PORT = 4321;
const BASE_URL = `http://127.0.0.1:${PORT}`;

export default defineConfig({
  testDir: "tests/visual",
  // Snapshots and per-spec snapshot dirs land in tests/visual/__snapshots__/.
  // Marked binary in .gitattributes so git diffs stay sane.
  snapshotDir: "tests/visual/__snapshots__",
  outputDir: "tests/visual/.test-results",
  // Tests stay independent; full parallel locally, single worker on CI for
  // deterministic ordering when triaging diffs.
  fullyParallel: true,
  workers: process.env.CI ? 1 : undefined,
  // No retries: visual regressions should be reproduced on the first run.
  // Flake should be debugged, not papered over.
  retries: 0,
  reporter: [
    ["list"],
    ["html", { outputFolder: "tests/visual/.playwright-report", open: "never" }],
  ],
  use: {
    baseURL: BASE_URL,
    viewport: { width: 1240, height: 800 },
    // Predictable rendering across runners. Astro static pages have no
    // animations to begin with, but the option is cheap insurance.
    deviceScaleFactor: 1,
    // Locale + timezone are fixed so any locale-aware date / number
    // formatting in build output stays consistent across machines.
    locale: "en-CA",
    timezoneId: "America/Toronto",
    // Fail fast on unexpected console errors -- they are usually the first
    // signal of a real regression hiding under a visually-similar page.
    // (Currently zero-JS so this is also a tripwire if a Vite-injected
    // script starts logging.)
  },
  expect: {
    toHaveScreenshot: {
      // ~100px diff tolerance per route. Tuned to absorb sub-pixel anti-
      // aliasing nondeterminism between local and CI Chromium builds,
      // while still catching axis-label-clip / panel-frame-missing /
      // wrong-tick regressions which run thousands of pixels.
      maxDiffPixels: 100,
      // animations: 'disabled' would matter if we had CSS animations; we
      // do not, but the flag is documented for future chart-builder work.
      animations: "disabled",
      // Threshold per-pixel below which a pixel is considered "same color"
      // (0..1 in YIQ space). Tight default; loosen only with cause.
      threshold: 0.2,
    },
  },
  webServer: {
    // The harness assumes `data/fixtures/site/` has already been overlaid
    // onto `data/site/` by the calling npm script (test:visual). We do NOT
    // overlay inside webServer.command because Playwright would race that
    // step against the build on Windows. See package.json `test:visual`.
    //
    // `reuseExistingServer: false` is deliberate: a user-started
    // `npm run preview` would have been built WITHOUT the fixture
    // overlay, which would silently invalidate the diff. Always rebuild
    // under fixture mode for visual tests.
    command: `npm run build:fast && npm run preview -- --port ${PORT} --host 127.0.0.1`,
    url: BASE_URL,
    reuseExistingServer: false,
    timeout: 180_000,
    stdout: "pipe",
    stderr: "pipe",
  },
});
