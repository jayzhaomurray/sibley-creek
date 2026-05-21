/**
 * Capture showcase screenshots for the Sibley Creek splash carousel.
 *
 * Captures:
 *   1. public/showcase/dashboard.png       — dashboard at /
 *   2. public/showcase/chart-research.png  — /labour/ topic page (legacy target)
 *   3. public/showcase/chartbook-<slug>.png — each chartbook section page
 *
 * Run: node tools/capture_showcase.mjs
 *
 * Prerequisites:
 *   - `astro preview` serving on port 4321 (built output, NOT dev server)
 *   - playwright installed (devDependency)
 *
 * Slug list is read from the SECTION_SLUGS constant below. It mirrors the
 * `sections` array in src/data/sections.ts — update both if a new section
 * is added. This avoids a TypeScript parse dependency inside a plain .mjs
 * tool script.
 */

import { chromium } from 'playwright';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, '..');
const SHOWCASE = path.join(ROOT, 'public', 'showcase');

const BASE_URL = 'http://localhost:4321';
const VIEWPORT = { width: 1440, height: 900 };

/**
 * Chartbook section slugs — mirrors sections[] in src/data/sections.ts.
 * Update here when a new section is added to that array.
 */
const SECTION_SLUGS = [
  'output',
  'inflation',
  'labour',
  'housing',
  'policy',
  'markets',
  'trade',
];

// CSS injected before every screenshot to suppress hover/tooltip/transition artifacts
const SUPPRESS_CSS = `
  * { transition: none !important; animation: none !important; }
  [class*="tooltip"],
  [class*="overlay"],
  [class*="toolbar"],
  [data-plot-toolbar],
  [class*="Tooltip"],
  [class*="Overlay"],
  [role="tooltip"] {
    display: none !important;
  }
`;

async function capture(page, url, outPath, label) {
  console.log(`[${label}] navigating to ${url}`);

  // Park mouse at top-left BEFORE navigation so no hover fires during load
  await page.mouse.move(0, 0);

  await page.goto(url, { waitUntil: 'networkidle' });

  // Verify we are NOT looking at the dev server (vite/client present = wrong server)
  const html = await page.content();
  if (html.includes('vite/client')) {
    throw new Error(
      `[${label}] Dev server detected at ${url} — expected astro preview (dist build). ` +
      'Stop astro dev and start astro preview on port 4321.'
    );
  }

  // Inject suppression CSS — covers native SVG <title> tooltip containers,
  // any JS-rendered tooltips, and Astro dev-toolbar (absent in dist builds,
  // but kept defensively).
  await page.addStyleTag({ content: SUPPRESS_CSS });

  // Additional: hide native browser SVG title tooltips by removing <title>
  // elements from the DOM so the browser never queues a tooltip bubble.
  await page.evaluate(() => {
    document.querySelectorAll('svg title').forEach(el => el.remove());
  });

  // Re-park the mouse and wait for any lingering tooltip to dismiss
  await page.mouse.move(0, 0);
  await page.waitForTimeout(800);

  await page.screenshot({ path: outPath, fullPage: true });
  console.log(`[${label}] saved ${outPath}`);
}

(async () => {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ viewport: VIEWPORT });
  const page = await context.newPage();

  // ── Legacy captures (kept for backward compat with splash showcase slots) ──

  // 1. Dashboard at /overview/
  const dashOut = path.join(SHOWCASE, 'dashboard.png');
  await capture(page, `${BASE_URL}/overview/`, dashOut, 'dashboard');

  // 2. /labour/ topic page (original chart-research.png target)
  const labourOut = path.join(SHOWCASE, 'chart-research.png');
  await capture(page, `${BASE_URL}/labour/`, labourOut, 'labour');

  // ── Chartbook captures — all 7 section pages ─────────────────────────────

  const chartbookResults = [];

  for (const slug of SECTION_SLUGS) {
    const outPath = path.join(SHOWCASE, `chartbook-${slug}.png`);
    const url = `${BASE_URL}/${slug}/`;

    try {
      await capture(page, url, outPath, `chartbook-${slug}`);
      chartbookResults.push({ slug, outPath, status: 'ok' });
    } catch (err) {
      console.error(`[chartbook-${slug}] FAILED: ${err.message}`);
      chartbookResults.push({ slug, outPath, status: 'failed', error: err.message });
    }
  }

  await browser.close();

  // ── Dimension report via sharp ────────────────────────────────────────────
  let sharp;
  try {
    ({ default: sharp } = await import('sharp'));
  } catch {
    console.log('sharp not available — skipping dimension/size report');
  }

  if (sharp) {
    console.log('\nChartbook capture results:');
    console.log('==========================');

    for (const r of chartbookResults) {
      if (r.status !== 'ok') {
        console.log(`FAIL chartbook-${r.slug}: ${r.error}`);
        continue;
      }

      try {
        const { statSync } = await import('fs');
        const meta = await sharp(r.outPath).metadata();
        const sizeKb = (statSync(r.outPath).size / 1024).toFixed(1);
        console.log(
          `OK   chartbook-${r.slug}.png  ${meta.width}x${meta.height}  ${sizeKb} KB  ${r.outPath}`
        );
      } catch (err) {
        console.log(`WARN chartbook-${r.slug}: metadata error — ${err.message}`);
      }
    }
  }

  console.log('\nDone.');
})();
