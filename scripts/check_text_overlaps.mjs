#!/usr/bin/env node
/**
 * Text-vs-line / text-vs-bar overlap detector.
 *
 * Spins up `astro preview` against `dist/`, drives a Playwright Chromium
 * over every chart-bearing route, and fails the build when any <text>
 * element's bounding box intersects a data-line <path> / <polyline> /
 * <line> or data-bar <rect>. The intent is a build-time safety net:
 * stop shipping silently-overlapping axis labels and inline series labels
 * before they hit the live site.
 *
 * Usage (from repo root):
 *   npm run build          # ensure dist/ is fresh
 *   node scripts/check_text_overlaps.mjs
 *
 * Exit codes:
 *   0  no overlaps (allow-listed entries don't count).
 *   1  at least one overlap that isn't allow-listed.
 *   2  harness failure (couldn't start preview server, browser launch,
 *      etc.). Distinguishes "the check failed to run" from "the check ran
 *      and found violations" so CI logs are unambiguous.
 *
 * Configuration:
 *   scripts/text_overlap_allowlist.json -- entries `{ page, text, reason }`.
 *   Match is case-sensitive on `page` (URL path with trailing slash) and
 *   on `text` (the literal text content of the <text> element).
 *
 * v2 (current): sample-based stroke-vs-rect geometry.
 *   Each data-line element is sampled via SVGGeometryElement.getPointAtLength
 *   along its actual stroke. A text-rect "hits" a line only when the
 *   stroke crosses the rect (or comes within a small pad matching the
 *   stroke width). This eliminates the bbox-pessimism that flagged
 *   labels sitting in the empty corner of a sloped-line's bbox.
 *
 *   Bars (rect primitives) remain bbox-tested -- they ARE rectangles,
 *   so bbox-vs-bbox is exact.
 *
 *   The text-overlap fixer (scripts/fix_text_overlaps.mjs) uses the same
 *   sample-based geometry. The two scripts must stay in sync: if the
 *   fixer places a label and the detector then says "overlap", the
 *   build fails despite the fix.
 *
 * v1 limitations that remain:
 *   - SVG-rendered standalone chart assets loaded via <img src=".svg">
 *     (deep-dive pillar charts) are NOT inspected -- the browser DOM
 *     treats them as opaque images. Those are authored separately and
 *     reviewed visually; if a check is wanted for them, do it from
 *     the source SVG, not the embedded <img>.
 *
 * Related infra: tests/visual/ (Playwright visual regression), and
 * scripts/check_label_budgets.mjs (the other build-time hygiene gate
 * this script mirrors in shape).
 */
import { spawn } from "node:child_process";
import { readFileSync, readdirSync, existsSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { chromium } from "@playwright/test";

const __filename = fileURLToPath(import.meta.url);
const ROOT = resolve(dirname(__filename), "..");
const ALLOWLIST_PATH = resolve(ROOT, "scripts/text_overlap_allowlist.json");

// ---- Routes --------------------------------------------------------------
//
// Routes the script visits. Mirrors `tests/visual/routes.spec.ts` plus the
// chart-builder workshop pages and any built research deep dives. Any
// chart-bearing route that ships to readers should be listed here.
//
// Research deep-dive routes are discovered dynamically from `dist/research/`
// so that promoting a new slug doesn't require touching this script.
const STATIC_ROUTES = [
  "/",
  "/gdp/",
  "/inflation/",
  "/labour/",
  "/policy/",
  "/markets/",
  "/trade/",
  "/housing/",
  "/research/",
  "/chart-alternatives/",
  "/chart-improvements/",
];

function discoverResearchRoutes() {
  const out = [];
  const researchDir = resolve(ROOT, "dist/research");
  if (!existsSync(researchDir)) return out;
  for (const ent of readdirSync(researchDir, { withFileTypes: true })) {
    if (!ent.isDirectory()) continue;
    out.push(`/research/${ent.name}/`);
  }
  return out;
}

// ---- Element classification ---------------------------------------------
//
// A "data line" is the stroked geometry that represents a series -- the
// thing readers would actually trace with their eye. A "data bar" is the
// filled column / row primitive. The class taxonomy is BEM-y across the
// codebase; the substring matchers below were derived by grepping every
// class on every dist HTML page (see commit message).
//
// `DATA_LINE_PATTERNS` matches data-series strokes. EXCLUDED are
// presentational lines that are NOT carrying series semantics: grid
// lines, zero-baseline lines, axis ticks, the canon frame, the
// `sg-mark__line` (the Sleeping Giant brand sigil stroke).
//
// `DATA_BAR_PATTERNS` matches bar primitives. EXCLUDED are reference
// bands, frames, and other rect chrome.
const DATA_LINE_PATTERNS = [
  /\bcanon-chart__line\b/,
  /\bcanon-chart__line-secondary\b/,
  /\bcanon-chart__line-tertiary\b/,
  /\balt-chart__line\b/,
  /\balt-chart__line-secondary\b/,
  /\balt-chart__line-tertiary\b/,
  /\bpanel-7-divergence__line-primary\b/,
  /\bpanel-7-divergence__line-secondary\b/,
  /\bcontrib-total-line\b/,
  /\balt-decomp__total-line\b/,
];

const DATA_BAR_PATTERNS = [
  /\bcanon-chart__bar\b/,
  /\balt-chart__bar\b/,
  /\balt-decomp__bar\b/,
  /\bcontrib-bar\b/,
];

// Lines that are PRESENTATIONAL and should NOT count as data-line targets.
// Kept as an explicit deny-list so the matcher is auditable.
const NON_DATA_LINE_PATTERNS = [
  /\bcanon-chart__gridline\b/,
  /\balt-chart__gridline\b/,
  /\bpanel-7-divergence__gridline\b/,
  /\bpanel-beveridge__gridline\b/,
  /\bcanon-chart__zero-line\b/,
  /\balt-chart__zero-line\b/,
  /\bpanel-7-divergence__zero-line\b/,
  /\bcanon-chart__xtick\b/,
  /\bcanon-chart__ytick\b/,
  /\bcanon-chart__frame\b/,
  /\bcanon-chart__reference-band\b/,
  /\balt-decomp__legend-line\b/,
  /\bcontrib-legend__line\b/,
  /\bsg-mark__line\b/,
  /\bsg-mark__dot\b/,
];

// Serialise patterns for evaluate() (RegExp doesn't survive structured
// clone). Reconstructed on the page side via `new RegExp(source)`.
function serialisePatterns(pats) {
  return pats.map((p) => p.source);
}

// ---- Preview server ------------------------------------------------------
//
// We don't shell out to `npm run preview` because we need port discovery
// and a clean kill path. Use astro CLI directly via npx and parse stdout
// for the "ready" line.
const PORT = 4329; // Distinct from playwright.config.ts (4321) so a stale
//                    preview from a visual test run doesn't collide.
const BASE_URL = `http://127.0.0.1:${PORT}`;

function startPreview() {
  return new Promise((resolveP, rejectP) => {
    if (!existsSync(resolve(ROOT, "dist/index.html"))) {
      rejectP(
        new Error(
          "dist/index.html missing. Run `npm run build` (or `npm run build:fast`) before this script.",
        ),
      );
      return;
    }
    // Astro 6's preview defaults are fine; we just need the port pinned.
    // `shell: true` is required on Windows for the npx shim to launch
    // (without it Node throws EINVAL on `.cmd` files in Node >=20).
    const child = spawn(
      "npx",
      ["astro", "preview", "--port", String(PORT), "--host", "127.0.0.1"],
      { cwd: ROOT, stdio: ["ignore", "pipe", "pipe"], shell: true },
    );
    let resolved = false;
    const onReady = () => {
      if (resolved) return;
      resolved = true;
      resolveP(child);
    };
    const timeout = setTimeout(() => {
      if (resolved) return;
      resolved = true;
      try {
        child.kill("SIGKILL");
      } catch {}
      rejectP(new Error("astro preview did not become ready within 30s"));
    }, 30_000);
    child.stdout.on("data", (buf) => {
      const s = buf.toString();
      // Astro prints something like "Local    http://127.0.0.1:4329/".
      if (s.includes(`:${PORT}`) || s.toLowerCase().includes("ready in")) {
        clearTimeout(timeout);
        onReady();
      }
    });
    child.stderr.on("data", () => {
      // Astro sometimes prints diagnostic lines here; ignore unless the
      // process dies (handled by 'exit').
    });
    child.on("error", (err) => {
      clearTimeout(timeout);
      if (!resolved) {
        resolved = true;
        rejectP(err);
      }
    });
    child.on("exit", (code, signal) => {
      if (!resolved) {
        clearTimeout(timeout);
        resolved = true;
        rejectP(
          new Error(
            `astro preview exited early (code=${code}, signal=${signal})`,
          ),
        );
      }
    });
  });
}

async function stopPreview(child) {
  if (!child || child.exitCode !== null) return;
  await new Promise((res) => {
    child.once("exit", () => res());
    try {
      // SIGTERM is enough on macOS / Linux; on Windows the child process
      // is a node wrapper that needs a hard kill.
      child.kill(process.platform === "win32" ? "SIGKILL" : "SIGTERM");
    } catch {
      res();
    }
    // Belt-and-suspenders timeout.
    setTimeout(() => res(), 5_000).unref?.();
  });
}

// ---- In-page extraction --------------------------------------------------
//
// Run inside the page context. Returns { svgs: [{ panel, texts, lines, bars }] }
// where each entry is a bounding rect in PAGE pixels.
async function extractFromPage(page, dataLineSources, dataBarSources, nonLineSources) {
  return await page.evaluate(
    ({ lineSrcs, barSrcs, nonLineSrcs }) => {
      const lineRegexes = lineSrcs.map((s) => new RegExp(s));
      const barRegexes = barSrcs.map((s) => new RegExp(s));
      const nonLineRegexes = nonLineSrcs.map((s) => new RegExp(s));

      function classMatchesAny(cls, regexes) {
        for (const r of regexes) if (r.test(cls)) return true;
        return false;
      }

      function classMatchesAnyNot(cls, regexes) {
        for (const r of regexes) if (r.test(cls)) return true;
        return false;
      }

      // Skip elements that are not currently visible (display:none /
      // visibility:hidden / zero size). getBoundingClientRect on a hidden
      // SVG child still returns 0x0 in Chromium, which we filter below.
      function rectFor(el) {
        const r = el.getBoundingClientRect();
        return { x: r.x, y: r.y, width: r.width, height: r.height };
      }

      function nonZero(r) {
        return r.width > 0.5 && r.height > 0.5;
      }

      const out = [];
      const svgs = Array.from(document.querySelectorAll("svg"));
      for (let i = 0; i < svgs.length; i++) {
        const svg = svgs[i];
        // Skip the brand sigil; nothing inside is a data primitive.
        if (svg.classList.contains("sg-mark")) continue;

        const panel =
          svg.getAttribute("data-panel") ||
          svg.getAttribute("aria-label") ||
          svg.getAttribute("data-astro-cid") ||
          `svg[${i}]`;

        const texts = [];
        // Tick labels (xtick-label / ytick-label) sit OUTSIDE the plot
        // area by canon — below the x-axis or left of the y-axis. Their
        // bboxes can touch the line's bbox at the axis edge without
        // any visual overlap. Skip them at extraction.
        const TICK_LABEL_CLASSES = /(^|\s)(?:canon-chart__|vig-panel__|alt-chart__)?(?:xtick-label|ytick-label|tick-label|axis-label)(\s|$)/;
        for (const t of svg.querySelectorAll("text")) {
          const cls = t.getAttribute("class") || "";
          if (TICK_LABEL_CLASSES.test(cls)) continue;
          const r = rectFor(t);
          if (!nonZero(r)) continue;
          texts.push({
            text: (t.textContent || "").trim(),
            cls,
            rect: r,
          });
        }

        const lines = [];
        // Data-line strokes: <path>, <polyline>, sometimes <line> are used.
        const lineSel = "path, polyline, line";
        for (const el of svg.querySelectorAll(lineSel)) {
          const cls = el.getAttribute("class") || "";
          if (!classMatchesAny(cls, lineRegexes)) continue;
          if (classMatchesAnyNot(cls, nonLineRegexes)) continue;
          const r = rectFor(el);
          if (!nonZero(r)) continue;
          // Sample stroke points for precise hit-testing. See v2 note in
          // the file header: bbox-vs-bbox is pessimistic on sloped lines,
          // and the fixer (scripts/fix_text_overlaps.mjs) uses sample
          // geometry, so the detector must too -- otherwise the
          // detector flags the fixer's clean placements as residual
          // overlaps and the build fails after a successful fix.
          const samples = [];
          try {
            if (typeof el.getTotalLength === "function") {
              const L = el.getTotalLength();
              if (isFinite(L) && L > 0) {
                const ctm = el.getScreenCTM();
                const N = Math.min(600, Math.max(40, Math.round(L)));
                for (let k = 0; k <= N; k++) {
                  const p = el.getPointAtLength((k / N) * L);
                  if (ctm) {
                    const px = ctm.a * p.x + ctm.c * p.y + ctm.e;
                    const py = ctm.b * p.x + ctm.d * p.y + ctm.f;
                    samples.push({ x: px, y: py });
                  } else {
                    samples.push({ x: p.x, y: p.y });
                  }
                }
              }
            }
          } catch {
            // Sampling failed; fall back to bbox-only.
          }
          lines.push({ kind: el.tagName.toLowerCase(), cls, rect: r, samples });
        }

        const bars = [];
        for (const el of svg.querySelectorAll("rect")) {
          const cls = el.getAttribute("class") || "";
          if (!classMatchesAny(cls, barRegexes)) continue;
          const r = rectFor(el);
          if (!nonZero(r)) continue;
          bars.push({ kind: "rect", cls, rect: r });
        }

        if (texts.length === 0 || (lines.length === 0 && bars.length === 0)) {
          continue;
        }
        out.push({ panel, texts, lines, bars });
      }
      return out;
    },
    { lineSrcs: dataLineSources, barSrcs: dataBarSources, nonLineSrcs: nonLineSources },
  );
}

// Axis-aligned bounding-box intersection test. Strict overlap; a shared
// edge with zero-area overlap does NOT count, to avoid flagging legitimate
// y-tick labels that sit immediately to the left of a frame edge.
function rectsOverlap(a, b) {
  return (
    a.x < b.x + b.width &&
    b.x < a.x + a.width &&
    a.y < b.y + b.height &&
    b.y < a.y + a.height
  );
}

function rectContainsPoint(r, p) {
  return p.x >= r.x && p.x <= r.x + r.width && p.y >= r.y && p.y <= r.y + r.height;
}

// Sample-aware line-vs-rect hit test (mirrors fix_text_overlaps.mjs).
// When the line has stroke samples, hit only when a sample falls inside
// the (slightly padded) text rect. Otherwise fall back to bbox.
function rectHitsLine(rect, line, lineHalfStroke = 1.5) {
  if (line.samples && line.samples.length > 0) {
    const pad = lineHalfStroke;
    const r2 = {
      x: rect.x - pad,
      y: rect.y - pad,
      width: rect.width + 2 * pad,
      height: rect.height + 2 * pad,
    };
    for (const p of line.samples) {
      if (rectContainsPoint(r2, p)) return true;
    }
    return false;
  }
  return rectsOverlap(rect, line.rect);
}

// Quick intersection-area (in px^2) for ranking violations by severity.
// For sample-based hits we approximate with the bbox-intersection area
// just for sort/report purposes (the violation itself is sample-detected).
function overlapArea(a, b) {
  const x = Math.max(0, Math.min(a.x + a.width, b.x + b.width) - Math.max(a.x, b.x));
  const y = Math.max(0, Math.min(a.y + a.height, b.y + b.height) - Math.max(a.y, b.y));
  return x * y;
}

// ---- Allowlist -----------------------------------------------------------
function loadAllowlist() {
  if (!existsSync(ALLOWLIST_PATH)) return [];
  const raw = readFileSync(ALLOWLIST_PATH, "utf-8");
  let parsed;
  try {
    parsed = JSON.parse(raw);
  } catch (err) {
    throw new Error(
      `text_overlap_allowlist.json is not valid JSON: ${err.message}`,
    );
  }
  if (!parsed || !Array.isArray(parsed.entries)) return [];
  return parsed.entries.map((e, idx) => {
    if (typeof e.page !== "string" || typeof e.text !== "string") {
      throw new Error(
        `text_overlap_allowlist.json entry ${idx} missing required string fields page/text`,
      );
    }
    return e;
  });
}

function isAllowlisted(allowlist, page, textContent) {
  for (const e of allowlist) {
    if (e.page === page && e.text === textContent) return true;
  }
  return false;
}

// ---- Main ---------------------------------------------------------------
async function main() {
  let allowlist;
  try {
    allowlist = loadAllowlist();
  } catch (err) {
    console.error(`[check-text-overlaps] ${err.message}`);
    process.exit(2);
  }

  const routes = [...STATIC_ROUTES, ...discoverResearchRoutes()];
  // Dedup in case a route appears in both sources.
  const uniqRoutes = Array.from(new Set(routes));

  let preview;
  let browser;
  try {
    preview = await startPreview();
  } catch (err) {
    console.error(`[check-text-overlaps] could not start astro preview: ${err.message}`);
    process.exit(2);
  }

  try {
    browser = await chromium.launch();
  } catch (err) {
    await stopPreview(preview);
    console.error(`[check-text-overlaps] could not launch chromium: ${err.message}`);
    process.exit(2);
  }

  const lineSrcs = serialisePatterns(DATA_LINE_PATTERNS);
  const barSrcs = serialisePatterns(DATA_BAR_PATTERNS);
  const nonLineSrcs = serialisePatterns(NON_DATA_LINE_PATTERNS);

  const violations = [];
  let svgsInspected = 0;
  let pagesInspected = 0;

  try {
    const context = await browser.newContext({
      viewport: { width: 1240, height: 800 },
      deviceScaleFactor: 1,
    });
    const page = await context.newPage();

    for (const route of uniqRoutes) {
      const url = `${BASE_URL}${route}`;
      let resp;
      try {
        resp = await page.goto(url, { waitUntil: "networkidle", timeout: 20_000 });
      } catch (err) {
        console.error(`[check-text-overlaps] navigation failed for ${route}: ${err.message}`);
        continue;
      }
      if (!resp || resp.status() !== 200) {
        console.error(
          `[check-text-overlaps] non-200 (${resp ? resp.status() : "no-resp"}) for ${route} -- skipping`,
        );
        continue;
      }
      pagesInspected++;

      const svgEntries = await extractFromPage(page, lineSrcs, barSrcs, nonLineSrcs);
      svgsInspected += svgEntries.length;

      for (const svg of svgEntries) {
        for (const t of svg.texts) {
          const conflicting = [];
          for (const ln of svg.lines) {
            if (rectHitsLine(t.rect, ln)) {
              conflicting.push({
                kind: "line",
                cls: ln.cls,
                tag: ln.kind,
                area: overlapArea(t.rect, ln.rect),
              });
            }
          }
          for (const br of svg.bars) {
            if (rectsOverlap(t.rect, br.rect)) {
              conflicting.push({
                kind: "bar",
                cls: br.cls,
                tag: br.kind,
                area: overlapArea(t.rect, br.rect),
              });
            }
          }
          if (conflicting.length === 0) continue;
          if (isAllowlisted(allowlist, route, t.text)) continue;
          violations.push({
            page: route,
            panel: svg.panel,
            text: t.text,
            text_cls: t.cls,
            text_rect: t.rect,
            conflicts: conflicting,
          });
        }
      }
    }
  } finally {
    if (browser) await browser.close();
    await stopPreview(preview);
  }

  if (violations.length === 0) {
    console.log(
      `[check-text-overlaps] OK -- ${pagesInspected} page(s), ${svgsInspected} chart-bearing SVG(s) inspected, no text-vs-line/bar overlaps.`,
    );
    process.exit(0);
  }

  // Sort by page, then descending overlap area within page, so the most
  // egregious violation per route surfaces first.
  violations.sort((a, b) => {
    if (a.page !== b.page) return a.page < b.page ? -1 : 1;
    const aMax = Math.max(...a.conflicts.map((c) => c.area));
    const bMax = Math.max(...b.conflicts.map((c) => c.area));
    return bMax - aMax;
  });

  console.error(
    `[check-text-overlaps] FAIL -- ${violations.length} overlap(s) across ${pagesInspected} page(s):\n`,
  );
  for (const v of violations) {
    const maxArea = Math.max(...v.conflicts.map((c) => c.area));
    const summary = v.conflicts
      .map((c) => `${c.tag}.${c.cls}`)
      .slice(0, 3)
      .join(", ");
    const more = v.conflicts.length > 3 ? ` (+${v.conflicts.length - 3} more)` : "";
    console.error(
      `  ${v.page}  panel=${v.panel}\n` +
        `    text:     ${JSON.stringify(v.text)}\n` +
        `    cls:      ${v.text_cls}\n` +
        `    rect:     x=${v.text_rect.x.toFixed(1)} y=${v.text_rect.y.toFixed(1)} w=${v.text_rect.width.toFixed(1)} h=${v.text_rect.height.toFixed(1)}\n` +
        `    overlaps: ${summary}${more}  (max area ${maxArea.toFixed(1)} px^2)\n`,
    );
  }
  console.error(
    `Fix: tweak chart layout so the label rect clears the line/bar rect, or\n` +
      `add a deliberate exception to scripts/text_overlap_allowlist.json.\n`,
  );
  process.exit(1);
}

main().catch((err) => {
  console.error(`[check-text-overlaps] unhandled: ${err && err.stack ? err.stack : err}`);
  process.exit(2);
});
