/*
 * render-og-card.mjs
 *
 * Generates public/og-default.png from the /og-preview/ render target.
 *
 * Usage:
 *   1. Start `npm run dev` (Astro dev server on http://localhost:4321).
 *   2. Run `node scripts/render-og-card.mjs`.
 *
 * Or run this script directly - it boots the dev server, waits for ready,
 * screenshots, and tears the server down cleanly.
 *
 * Discipline:
 *   - viewport: 1200x630, deviceScaleFactor: 1 (1x raster - sharp at the
 *     canonical OG size; LinkedIn/Twitter downscale themselves).
 *   - document.fonts.ready awaited so Manrope 400/900 are loaded before
 *     screenshot. Without this, the fallback Helvetica Neue collapses the
 *     wordmark register.
 *   - PNG, no transparency, no clip beyond the 1200x630 viewport.
 */

import { chromium } from "playwright";
import { spawn } from "node:child_process";
import { setTimeout as wait } from "node:timers/promises";
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const projectRoot = resolve(__dirname, "..");

const DEV_URL = "http://localhost:4321/og-preview/";
const OUTPUT_PATH = resolve(projectRoot, "public", "og-default.png");

async function waitForServer(url, timeoutMs = 60000) {
  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline) {
    try {
      const res = await fetch(url, { method: "GET" });
      if (res.ok) return true;
    } catch {
      // server not up yet
    }
    await wait(500);
  }
  throw new Error(`Dev server did not become ready at ${url} within ${timeoutMs}ms`);
}

async function main() {
  console.log("[og] starting Astro dev server...");
  const isWin = process.platform === "win32";
  const npmCmd = isWin ? "npm.cmd" : "npm";
  const dev = spawn(npmCmd, ["run", "dev", "--", "--port", "4321"], {
    cwd: projectRoot,
    stdio: ["ignore", "pipe", "pipe"],
    // shell: true on Windows so the .cmd wrapper resolves; required by
    // Node >=20 which tightened spawn() on Windows shims (EINVAL otherwise).
    shell: isWin,
  });

  dev.stdout.on("data", (chunk) => {
    process.stdout.write(`[astro] ${chunk}`);
  });
  dev.stderr.on("data", (chunk) => {
    process.stderr.write(`[astro:err] ${chunk}`);
  });

  let browser;
  let exitCode = 0;
  try {
    await waitForServer(DEV_URL);
    console.log("[og] dev server ready, launching Chromium...");

    browser = await chromium.launch();
    const context = await browser.newContext({
      viewport: { width: 1200, height: 630 },
      deviceScaleFactor: 1,
    });
    const page = await context.newPage();

    await page.goto(DEV_URL, { waitUntil: "networkidle" });
    await page.evaluate(() => document.fonts.ready);

    // Astro 6 dev toolbar is a custom element in light DOM
    // (<astro-dev-toolbar>). It docks at the bottom of the viewport and
    // would otherwise clip into the 1200x630 screenshot. Remove it
    // outright before capture - hiding via CSS misses its outer wrapper
    // in some Astro versions.
    await page.evaluate(() => {
      for (const sel of ["astro-dev-toolbar", "astro-dev-overlay"]) {
        document.querySelectorAll(sel).forEach((el) => el.remove());
      }
    });

    // small settle frame after fonts.ready resolves
    await page.waitForTimeout(200);

    await page.screenshot({
      path: OUTPUT_PATH,
      type: "png",
      omitBackground: false,
      clip: { x: 0, y: 0, width: 1200, height: 630 },
    });

    console.log(`[og] screenshot written: ${OUTPUT_PATH}`);
  } catch (err) {
    console.error("[og] error:", err);
    exitCode = 1;
  } finally {
    if (browser) {
      try {
        await browser.close();
      } catch {
        /* ignore */
      }
    }
    console.log("[og] killing dev server...");
    // On Windows, sending SIGTERM to the npm wrapper does not always
    // cascade to the astro child. Use taskkill /T /F to take the whole
    // tree down cleanly so we don't leave a port-4321 listener behind.
    if (process.platform === "win32" && dev.pid) {
      try {
        const { spawnSync } = await import("node:child_process");
        spawnSync("taskkill", ["/pid", String(dev.pid), "/T", "/F"], {
          stdio: "ignore",
        });
      } catch {
        /* ignore */
      }
    } else {
      dev.kill("SIGTERM");
    }
    // give the OS a beat to release the port
    await wait(500);
  }

  process.exit(exitCode);
}

main();
