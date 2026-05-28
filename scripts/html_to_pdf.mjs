// HTML -> PDF renderer via Playwright (Chromium).
//
// Usage:  node scripts/html_to_pdf.mjs <input.html> <output.pdf>
//
// Loads the input HTML file directly (file:// URL) and prints to PDF
// preserving whatever @page CSS the HTML carries. Use for hand-styled
// briefing notes / meeting prep where the HTML is the source of truth.

import { chromium } from "playwright";
import { resolve, isAbsolute } from "node:path";
import { pathToFileURL } from "node:url";

const [, , inputArg, outputArg] = process.argv;
if (!inputArg || !outputArg) {
  console.error("usage: node scripts/html_to_pdf.mjs <input.html> <output.pdf>");
  process.exit(1);
}

const inputPath = isAbsolute(inputArg) ? inputArg : resolve(process.cwd(), inputArg);
const outputPath = isAbsolute(outputArg) ? outputArg : resolve(process.cwd(), outputArg);

const browser = await chromium.launch();
const ctx = await browser.newContext();
const page = await ctx.newPage();
await page.goto(pathToFileURL(inputPath).href, { waitUntil: "networkidle" });
await page.pdf({
  path: outputPath,
  format: "Letter",
  printBackground: true,
  preferCSSPageSize: true,
});
await browser.close();

console.log(`wrote: ${outputPath}`);
