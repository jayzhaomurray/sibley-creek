/*
 * routes.spec.ts - Per-route full-page visual regression.
 *
 * One test per route. Full-page screenshot, masked over time-bound
 * regions, diffed against a committed baseline PNG.
 *
 * Coverage matrix is documented in tests/visual/README.md. Keep ROUTES
 * sorted by section order so a glance at the test list mirrors the site.
 *
 * Threshold reasoning
 * -------------------
 * The Playwright `maxDiffPixels` is 100 (set in playwright.config.ts),
 * which absorbs ~10x10px of anti-aliasing nondeterminism. SVG chart
 * regressions worth catching (wrong scale, wrong tick, missing frame,
 * label clip) blow past that by orders of magnitude. The threshold is
 * NOT a license to be sloppy; it is a floor on machine-level noise.
 *
 * Masking
 * -------
 * A handful of build-time-date components render `new Date()` at build,
 * which would diff every day. We mask those with Playwright's `mask:`
 * option, which paints a solid block over the matched region BEFORE the
 * screenshot snapshot is taken. The mask color is configurable but the
 * default magenta is fine since baselines will include the same blocks.
 *
 * If src/ later gains a single `data-vt-mask` attribute on time-bound
 * regions, replace the conservative selectors below with `[data-vt-mask]`
 * and shrink the mask surface to zero outside the actual date stamps.
 */
import { test, expect } from "@playwright/test";
import type { Locator } from "@playwright/test";

interface RouteCase {
  /** URL path. Astro `trailingSlash: 'always'` so all paths end with /. */
  path: string;
  /** Snapshot filename stem; underscored so PNGs sort by section. */
  name: string;
  /**
   * Extra settle wait (ms) before capture, for pages with one-shot JS
   * animation that must finish (and freeze) before two consecutive
   * screenshots can be stable.
   */
  settleMs?: number;
}

const ROUTES: RouteCase[] = [
  // Splash hero map animation is a one-shot that freezes at ~8.5s; wait it
  // out so toHaveScreenshot can get two stable frames.
  { path: "/", name: "00_home", settleMs: 9500 },
  // /gdp/ and /policy/ are meta-refresh redirect stubs (slugs renamed to
  // /output/ and /monetary/ on master). Screenshotting a 0-second redirect
  // is a race — shoot the real routes instead.
  { path: "/output/", name: "01_output" },
  { path: "/inflation/", name: "02_inflation" },
  { path: "/labour/", name: "03_labour" },
  { path: "/monetary/", name: "04_monetary" },
  { path: "/markets/", name: "05_markets" },
  { path: "/trade/", name: "06_trade" },
  { path: "/housing/", name: "07_housing" },
  { path: "/overview/", name: "09_overview" },
  // /overview-with-fiscal/ removed: the draft page was deleted on master
  // (commit cf2bcb9) after fiscal folded into /overview/; the route 404s.
  { path: "/research/", name: "08_research_index" },
  // When at least one deep dive is promoted to editorial/published/, add the
  // matching /research/<slug>/ route back here. The spec covers only routes
  // that getStaticPaths() actually emits today.
  //
  // src/pages/research/[slug].astro filters deepDives on `publishedPath`.
  // Zero entries carry it as of this commit, so the 3 slugs below intentionally
  // do NOT build and are intentionally NOT asserted here:
  //   - /research/mortgage-renewal-wall/
  //   - /research/boc-fed-divergence/
  //   - /research/per-capita-output/
];

/*
 * Mask selectors. Be conservative: a wider mask is safer than a sub-pixel
 * date stamp breaking the harness. Hit any element that could render a
 * build-time date OR a current-time stamp. Selectors are CSS, evaluated
 * per page; missing selectors are silently ignored by Playwright.
 *
 * Known sources (grep `new Date()` in src/ to verify):
 *   - VignelliColophon.astro             (footer build stamp)
 *   - HeroChart.astro                    (axis "as of" date)
 *   - index.astro hero band              (`const today = new Date()`)
 *   - layouts/BaseLayout.astro <time>    (if any)
 *
 * Add to this list when a new build-time-date region is introduced.
 */
const MASK_SELECTORS = [
  "time",
  "[data-vt-mask]",
  // Pragmatic class / role hooks -- these may or may not exist on a given
  // page. Playwright's locator is happy to mask zero matches.
  ".colophon",
  "[data-colophon]",
  ".hero-as-of",
  "[data-hero-as-of]",
  // Splash hero Canada-map animation (one-shot JS over ~8.5s): the capture
  // lands on a nondeterministic frame. Mask the art, keep the hero copy.
  ".v3-hero__art",
  // Splash showcase 02 chartbook carousel rotates forever — never produces
  // two stable consecutive frames. Mask the rotating slides + URL chip.
  ".v3-carousel",
  "[data-carousel-url]",
];

function maskLocators(page: import("@playwright/test").Page): Locator[] {
  return MASK_SELECTORS.map((sel) => page.locator(sel));
}

for (const route of ROUTES) {
  test(`route ${route.path}`, async ({ page }) => {
    const response = await page.goto(route.path, { waitUntil: "load" });
    // Static site: a non-OK on a known route is itself a regression worth
    // failing loud on. (404 templates would otherwise diff-clean against
    // a 404 baseline and silently pass.)
    expect(response, `no response for ${route.path}`).not.toBeNull();
    expect(response!.status(), `unexpected status for ${route.path}`).toBe(200);

    // Prime lazy-loaded images: fullPage capture scrolls the document, and
    // `loading="lazy"` images (splash showcase screencaps) decode mid-shot
    // otherwise — Playwright then can't get two stable consecutive frames.
    await page.evaluate(async () => {
      const step = window.innerHeight;
      for (let y = 0; y < document.body.scrollHeight; y += step) {
        window.scrollTo(0, y);
        await new Promise((r) => setTimeout(r, 50));
      }
      window.scrollTo(0, 0);
    });
    await page.waitForLoadState("networkidle");

    if (route.settleMs) await page.waitForTimeout(route.settleMs);

    // Belt-and-suspenders: section pages are tall stacks of panels.
    // `fullPage: true` paints the entire scroll height. The viewport
    // height in playwright.config.ts is just the initial paint window.
    await expect(page).toHaveScreenshot(`${route.name}.png`, {
      fullPage: true,
      mask: maskLocators(page),
      // Disable any animations that crept in (none today, but cheap).
      animations: "disabled",
    });
  });
}
