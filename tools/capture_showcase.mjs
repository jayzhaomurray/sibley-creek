/**
 * Capture showcase screenshots for the Sibley Creek v3 splash.
 *
 * Captures:
 *   1. public/showcase/dashboard.png       — dashboard at /
 *   2. public/showcase/chart-research.png  — /labour/ topic page
 *
 * Run: node tools/capture_showcase.mjs
 */

import { chromium } from 'playwright';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, '..');
const SHOWCASE = path.join(ROOT, 'public', 'showcase');

const BASE_URL = 'http://localhost:4321';
const VIEWPORT = { width: 1440, height: 900 };

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

  const shot = await page.screenshot({ path: outPath, fullPage: true });
  console.log(`[${label}] saved ${outPath}`);
  return shot;
}

(async () => {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ viewport: VIEWPORT });
  const page = await context.newPage();

  // 1. Dashboard at /overview/ (splash is now at /, dashboard moved to /overview/)
  const dashOut = path.join(SHOWCASE, 'dashboard.png');
  await capture(page, `${BASE_URL}/overview/`, dashOut, 'dashboard');

  // 2. /labour/ topic page
  const labourOut = path.join(SHOWCASE, 'chart-research.png');
  await capture(page, `${BASE_URL}/labour/`, labourOut, 'labour');

  await browser.close();

  // Report dimensions via sharp if available, otherwise skip
  try {
    const { default: sharp } = await import('sharp');
    for (const [label, p] of [['dashboard', dashOut], ['labour', labourOut]]) {
      const meta = await sharp(p).metadata();
      console.log(`[${label}] dimensions: ${meta.width} x ${meta.height}`);
    }
  } catch {
    console.log('sharp not available — skipping dimension report (files saved)');
  }

  console.log('Done.');
})();
