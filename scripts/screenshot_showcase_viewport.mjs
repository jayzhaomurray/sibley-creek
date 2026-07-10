import { chromium } from "playwright";
import { resolve } from "node:path";

const [, , urlArg, outputArg] = process.argv;
if (!urlArg || !outputArg) {
  console.error("usage: node scripts/screenshot_showcase_viewport.mjs <url> <output.png>");
  process.exit(1);
}

const outputPath = resolve(process.cwd(), outputArg);
const browser = await chromium.launch();
const ctx = await browser.newContext({
  viewport: { width: 1440, height: 1800 },
  deviceScaleFactor: 1,
  colorScheme: "light",
});
const page = await ctx.newPage();

await page.goto(urlArg, { waitUntil: "networkidle" });
await page.evaluate(() => document.fonts.ready);
await page.waitForTimeout(1500);
await page.screenshot({ path: outputPath, type: "png", fullPage: false });

await browser.close();
console.log(`wrote: ${outputPath}`);
