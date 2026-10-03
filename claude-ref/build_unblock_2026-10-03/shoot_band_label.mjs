// Screenshot + geometry probe for reference-band labels in the built dist/.
// Usage: node claude-ref/build_unblock_2026-10-03/shoot_band_label.mjs <tag>
import { spawn } from "node:child_process";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { chromium } from "@playwright/test";

const HERE = dirname(fileURLToPath(import.meta.url));
const ROOT = resolve(HERE, "..", "..");
const PORT = 4337;
const tag = process.argv[2] || "after";
const routes = ["/monetary/", "/policy/", "/inflation/"];

const child = spawn("npx", ["astro", "preview", "--port", String(PORT), "--host", "127.0.0.1"],
  { cwd: ROOT, stdio: ["ignore", "pipe", "pipe"], shell: true });
await new Promise((res, rej) => {
  const to = setTimeout(() => rej(new Error("preview timeout")), 40000);
  child.stdout.on("data", (b) => { if (b.toString().includes(String(PORT))) { clearTimeout(to); res(); } });
});
const browser = await chromium.launch();
try {
  const page = await browser.newPage({ viewport: { width: 1240, height: 900 }, deviceScaleFactor: 2 });
  for (const route of routes) {
    await page.goto("http://127.0.0.1:" + PORT + route, { waitUntil: "networkidle" });
    const labels = page.locator("text.canon-chart__reference-band-label");
    const n = await labels.count();
    console.log(route, "final url", page.url(), "band labels:", n);
    for (let i = 0; i < n; i++) {
      const info = await labels.nth(i).evaluate((t) => {
        const svg = t.ownerSVGElement;
        const b = t.getBBox();
        const ctm = svg.getScreenCTM();
        const line = svg.querySelector("path.canon-chart__line");
        const pad = 1.5 / ctm.a;
        let hits = 0;
        for (const el of svg.querySelectorAll("path.canon-chart__line, path.canon-chart__line-secondary, path.canon-chart__line-tertiary")) {
          const L = el.getTotalLength();
          const N = Math.round(L * 4);
          for (let k = 0; k <= N; k++) {
            const p = el.getPointAtLength((k / N) * L);
            if (p.x >= b.x - pad && p.x <= b.x + b.width + pad && p.y >= b.y - pad && p.y <= b.y + b.height + pad) hits++;
          }
        }
        return { text: t.textContent, panel: svg.parentElement.getAttribute("data-panel"), scale: ctm.a,
          x: t.getAttribute("x"), y: t.getAttribute("y"), anchor: t.getAttribute("text-anchor"),
          bbox: [b.x, b.y, b.width, b.height].map((v) => +v.toFixed(2)), lineSampleHits: hits };
      });
      console.log(JSON.stringify(info));
      const chart = labels.nth(i).locator("xpath=ancestor::div[contains(@class,'canon-chart')][1]");
      await chart.scrollIntoViewIfNeeded();
      const slug = route.replace(/\//g, "") || "home";
      const out = resolve(HERE, `${tag}_${slug}_${info.panel || i}.png`);
      await chart.screenshot({ path: out });
      console.log("  saved", out);
    }
  }
} finally {
  await browser.close();
  try { spawn("taskkill", ["/pid", String(child.pid), "/T", "/F"], { shell: true }); } catch {}
}
process.exit(0);
