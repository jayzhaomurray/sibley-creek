// Render an OG card HTML source file to a PNG via Playwright + Chromium.
//
// Usage:  node scripts/render_og_card.mjs <input.html> <output.png>
//
// Defaults:
//   viewport     1200 x 630 (standard OG dimensions)
//   scale factor 1 (OG consumers expect exact-pixel; no Retina doubling)
//   waits for    document.fonts.ready before screenshot (so Manrope is loaded)
//   captures     the page body (not full-page; the body IS the card)

import { chromium } from "playwright";
import { resolve } from "node:path";
import { pathToFileURL } from "node:url";

const [, , inputArg, outputArg] = process.argv;
if (!inputArg || !outputArg) {
  console.error("usage: node scripts/render_og_card.mjs <input.html> <output.png>");
  process.exit(1);
}

const inputPath = resolve(process.cwd(), inputArg);
const outputPath = resolve(process.cwd(), outputArg);

const browser = await chromium.launch();
const ctx = await browser.newContext({
  viewport: { width: 1200, height: 630 },
  deviceScaleFactor: 1,
  colorScheme: "light",
});
const page = await ctx.newPage();

await page.goto(pathToFileURL(inputPath).toString(), { waitUntil: "networkidle" });

await page.evaluate(() => document.fonts.ready);

await page.screenshot({
  path: outputPath,
  type: "png",
  fullPage: false,
  omitBackground: false,
  clip: { x: 0, y: 0, width: 1200, height: 630 },
});

await browser.close();

console.log(`wrote: ${outputPath}`);
