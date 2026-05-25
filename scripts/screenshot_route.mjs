// Full-page screenshot of a local-preview route via Playwright + Chromium.
//
// Used to refresh splash showcase carousel images when a section page's
// content materially changes (slug rename, new section, etc).
//
// Usage:
//   node scripts/screenshot_route.mjs <url> <output.png>
//
// Conventions:
//   viewport         1440 wide (matches existing chartbook-*.png assets)
//   deviceScaleFactor 1 (1:1 pixels; the splash carousel renders these
//                       at smaller sizes anyway via object-fit: cover)
//   fullPage          true (captures the entire scroll length, like the
//                          existing chartbook screenshots at 1440 x 2800+
//                          px tall)
//   waits for         document.fonts.ready (Manrope must load before shot)

import { chromium } from "playwright";
import { resolve } from "node:path";

const [, , urlArg, outputArg] = process.argv;
if (!urlArg || !outputArg) {
  console.error("usage: node scripts/screenshot_route.mjs <url> <output.png>");
  process.exit(1);
}

const outputPath = resolve(process.cwd(), outputArg);

const browser = await chromium.launch();
const ctx = await browser.newContext({
  viewport: { width: 1440, height: 900 },
  deviceScaleFactor: 1,
  colorScheme: "light",
});
const page = await ctx.newPage();

await page.goto(urlArg, { waitUntil: "networkidle" });
await page.evaluate(() => document.fonts.ready);
// Small extra wait for any client-side chart-rendering / lazy-load to settle
await page.waitForTimeout(1500);

await page.screenshot({
  path: outputPath,
  type: "png",
  fullPage: true,
});

await browser.close();
console.log(`wrote: ${outputPath}`);
