// One-off measurement script: confirms the hero column and the 6-tile grid
// column have equal bottom edges at 1440x900.
//
// Usage:
//   1. npm run build && npm run preview (running on http://localhost:4322)
//   2. node scripts/measure-home-columns.mjs
//
// Not part of CI. Lives in scripts/ so it doesn't pollute the source tree.

import { chromium } from "playwright";

const URL = process.env.HOME_URL ?? "http://localhost:4322/";

const browser = await chromium.launch();
const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 } });
const page = await ctx.newPage();
await page.goto(URL, { waitUntil: "networkidle" });

const data = await page.evaluate(() => {
  const hero = document.querySelector(".home__hero");
  const six = document.querySelector(".home__six");
  const heroRect = hero?.getBoundingClientRect();
  const sixRect = six?.getBoundingClientRect();
  const cells = [...document.querySelectorAll(".home__six-cell")].map((el) => {
    const r = el.getBoundingClientRect();
    return { top: r.top, bottom: r.bottom, height: r.height };
  });
  return {
    hero: heroRect && {
      top: heroRect.top,
      bottom: heroRect.bottom,
      height: heroRect.height,
    },
    six: sixRect && {
      top: sixRect.top,
      bottom: sixRect.bottom,
      height: sixRect.height,
    },
    cells,
  };
});

console.log(JSON.stringify(data, null, 2));

await browser.close();
