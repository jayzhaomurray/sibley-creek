#!/usr/bin/env node
/**
 * Text-vs-line / text-vs-bar overlap AUTO-FIXER.
 *
 * Companion to scripts/check_text_overlaps.mjs (the detector). Where the
 * detector flags overlaps and fails the build, this script flags overlaps
 * and REWRITES the offending <text> y-attribute in the BUILT artifact
 * (dist/**\/*.html) to nudge the label into the nearest whitespace. The
 * detector then re-runs and serves as the safety net for cases the fixer
 * cannot resolve.
 *
 * Order in CI:
 *   1. astro build       -> dist/
 *   2. node fix_text_overlaps.mjs   (this script)
 *   3. node check_text_overlaps.mjs (detector; build fails on residuals)
 *
 * KEY TRADEOFF (v1):
 *   This rewrites the BUILT artifact only. The source components still
 *   produce overlaps on every fresh build; every build also re-runs the
 *   fixer. The deployed site has zero overlaps but the source files are
 *   not edited. A source-level fix is a v2 problem (shared placement
 *   helper in src/components/charts/_shared/). See report for sketch.
 *
 * APPROACH:
 *   - Spin up astro preview against dist/ (same harness as detector).
 *   - For each chart-bearing SVG, extract:
 *       * each candidate <text>'s rect, its source attributes (class,
 *         x, y, text-anchor, data-astro-cid), and its scale factor
 *         (page-px per SVG user-unit) from the SVG's CTM.
 *       * data-line elements: bbox plus ~40-600 SAMPLED POINTS along
 *         the stroke via SVGGeometryElement.getPointAtLength, projected
 *         to page-px via the element's CTM. Sample-based hit testing
 *         is more accurate than bbox-vs-bbox for sloped lines.
 *       * data-bar rects (bbox is exact for bars).
 *   - Initial conflict detection uses the SAME geometry as the detector
 *     (sample-based for lines, bbox for bars) so the fixer flags exactly
 *     what the detector would flag -- no more, no fewer.
 *   - For each overlap, candidate y-offsets in SVG user-space:
 *       Pass 1 (geometry-aware): nudges that just clear each conflicting
 *         line/bar above or below it (smallest magnitude first).
 *       Pass 2 (blind fallback): {5, 10, 15, ..., 50} SVG units up then
 *         down. Cap at +/-50 per the spec.
 *   - Accept the first candidate whose page-pixel rect:
 *       (a) does NOT cross any data line stroke (sample test);
 *       (b) does NOT intersect any data bar (bbox test);
 *       (c) does NOT intersect any OTHER text element (originals or
 *           already-placed fixes within this same SVG);
 *       (d) stays inside the SVG's outer bounds.
 *   - Rewrite the dist HTML file: regex-replace the matching <text>
 *     element's y="..." attribute. Identification anchors on class, x,
 *     ORIGINAL y, text-anchor, and data-astro-cid -- the y anchor is
 *     the disambiguator when two text elements share all other attrs.
 *   - Allowlisted entries are skipped (same allowlist as the detector).
 *   - Conservative: only touches text elements that the detector would
 *     flag. Brand sigils, MTA-red latest dots, ticks, etc., are not
 *     eligible because they aren't <text>-vs-line/bar overlaps.
 *
 * Usage:
 *   npm run build
 *   node scripts/fix_text_overlaps.mjs   # rewrites dist/ in place
 *   node scripts/check_text_overlaps.mjs # verify zero residuals
 *
 * Exit codes:
 *   0  ran cleanly (zero detected overlaps OR fixer attempted every
 *      detected overlap; residuals are the detector's job to fail on).
 *   2  harness failure (couldn't start preview, browser launch, etc.).
 *
 * The fixer never exits non-zero on residuals -- that's the detector's
 * role. Splitting the responsibility keeps the CI log unambiguous:
 *   - "fixer rewrote N labels, M unfixable" -> see this script's stdout
 *   - "build fails because M residual overlaps" -> detector's stderr
 */
import { spawn } from "node:child_process";
import { readFileSync, writeFileSync, readdirSync, existsSync } from "node:fs";
import { dirname, resolve, join } from "node:path";
import { fileURLToPath } from "node:url";
import { chromium } from "@playwright/test";

const __filename = fileURLToPath(import.meta.url);
const ROOT = resolve(dirname(__filename), "..");
const DIST = resolve(ROOT, "dist");
const ALLOWLIST_PATH = resolve(ROOT, "scripts/text_overlap_allowlist.json");

// ---- Routes (mirrors detector) ------------------------------------------
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

// Maps a URL route to the dist HTML file we will rewrite.
function routeToDistFile(route) {
  // "/" -> dist/index.html ; "/gdp/" -> dist/gdp/index.html ; etc.
  const trimmed = route.replace(/^\/+|\/+$/g, "");
  if (trimmed === "") return join(DIST, "index.html");
  return join(DIST, trimmed, "index.html");
}

// ---- Element classification (mirrors detector) --------------------------
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

function serialisePatterns(pats) {
  return pats.map((p) => p.source);
}

// ---- Preview server (mirrors detector, distinct port) -------------------
const PORT = 4330; // detector uses 4329; pick a sibling that won't collide
const BASE_URL = `http://127.0.0.1:${PORT}`;

function startPreview() {
  return new Promise((resolveP, rejectP) => {
    if (!existsSync(resolve(ROOT, "dist/index.html"))) {
      rejectP(new Error("dist/index.html missing. Run `npm run build` first."));
      return;
    }
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
      if (s.includes(`:${PORT}`) || s.toLowerCase().includes("ready in")) {
        clearTimeout(timeout);
        onReady();
      }
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
      child.kill(process.platform === "win32" ? "SIGKILL" : "SIGTERM");
    } catch {
      res();
    }
    setTimeout(() => res(), 5_000).unref?.();
  });
}

// ---- In-page extraction -------------------------------------------------
//
// Returns, for each chart-bearing SVG on the page:
//   {
//     svgRect,                // page-px container rect of the SVG
//     svgScale: {sx, sy},     // page-px per SVG user-unit (from CTM)
//     texts: [{
//       text, cls, rect,      // page-px bbox
//       attrY, attrX,         // source SVG user-space y / x
//       outerSig,             // outerHTML for find-key
//     }],
//     lines: [{cls, rect}],
//     bars: [{cls, rect}],
//   }
async function extractFromPage(page, lineSrcs, barSrcs, nonLineSrcs) {
  return await page.evaluate(
    ({ lineSrcs, barSrcs, nonLineSrcs }) => {
      const lineRegexes = lineSrcs.map((s) => new RegExp(s));
      const barRegexes = barSrcs.map((s) => new RegExp(s));
      const nonLineRegexes = nonLineSrcs.map((s) => new RegExp(s));

      function matchesAny(cls, regexes) {
        for (const r of regexes) if (r.test(cls)) return true;
        return false;
      }
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
        if (svg.classList.contains("sg-mark")) continue;
        const panel =
          svg.getAttribute("data-panel") ||
          svg.getAttribute("aria-label") ||
          svg.getAttribute("data-astro-cid") ||
          `svg[${i}]`;
        const svgRect = rectFor(svg);
        if (!nonZero(svgRect)) continue;

        // page-px per SVG user-unit, via the first child's CTM. Falls back
        // to viewBox math if CTM is unavailable.
        let sx = 1, sy = 1;
        try {
          const ctm = svg.getScreenCTM();
          if (ctm) {
            sx = ctm.a;
            sy = ctm.d;
          }
        } catch {}
        if (!isFinite(sx) || sx === 0) sx = 1;
        if (!isFinite(sy) || sy === 0) sy = 1;

        const TICK_LABEL_CLASSES = /(^|\s)(?:canon-chart__|vig-panel__|alt-chart__)?(?:xtick-label|ytick-label|tick-label|axis-label)(\s|$)/;
        const texts = [];
        for (const t of svg.querySelectorAll("text")) {
          const cls = t.getAttribute("class") || "";
          if (TICK_LABEL_CLASSES.test(cls)) continue;
          const r = rectFor(t);
          if (!nonZero(r)) continue;
          const attrY = parseFloat(t.getAttribute("y"));
          const attrX = parseFloat(t.getAttribute("x"));
          // outerHTML in the live DOM may differ from the file (attribute
          // order, quoting). We capture the file-source-style signature
          // separately via attribute round-trip.
          const attrs = {};
          for (const a of Array.from(t.attributes)) attrs[a.name] = a.value;
          texts.push({
            text: (t.textContent || "").trim(),
            cls,
            rect: r,
            attrY: isFinite(attrY) ? attrY : null,
            attrX: isFinite(attrX) ? attrX : null,
            attrs,
            textContent: t.textContent || "",
          });
        }

        const lines = [];
        for (const el of svg.querySelectorAll("path, polyline, line")) {
          const cls = el.getAttribute("class") || "";
          if (!matchesAny(cls, lineRegexes)) continue;
          if (matchesAny(cls, nonLineRegexes)) continue;
          const r = rectFor(el);
          if (!nonZero(r)) continue;
          // Sample points along the stroke (SVG-space -> page-space) so
          // we can test candidate rects against the actual geometry, not
          // just the bounding-box envelope. This is what dissolves the
          // bbox-pessimism that left ~15 labels "unfixable" in the
          // bbox-only pass: a sloped line has a huge bbox but its
          // stroke only crosses any given vertical band briefly.
          const samples = [];
          try {
            // getTotalLength / getPointAtLength are SVGGeometryElement
            // methods (path / line / polyline / polygon / circle / etc).
            if (typeof el.getTotalLength === "function") {
              const L = el.getTotalLength();
              if (isFinite(L) && L > 0) {
                // ~one sample per 1.5 page-pixels of stroke, clamped.
                // Empirically this keeps the per-line sample count under
                // ~600 for the longest paths in the corpus.
                const ctm = el.getScreenCTM();
                const N = Math.min(600, Math.max(40, Math.round(L)));
                for (let k = 0; k <= N; k++) {
                  const p = el.getPointAtLength((k / N) * L);
                  // Convert SVG-user-space (p.x, p.y) to page-pixels via
                  // the element's CTM.
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
            // Geometry sampling failed; we'll fall back to bbox-only
            // testing for this line.
          }
          lines.push({ cls, rect: r, samples });
        }
        const bars = [];
        for (const el of svg.querySelectorAll("rect")) {
          const cls = el.getAttribute("class") || "";
          if (!matchesAny(cls, barRegexes)) continue;
          const r = rectFor(el);
          if (!nonZero(r)) continue;
          bars.push({ cls, rect: r });
        }

        if (texts.length === 0 || (lines.length === 0 && bars.length === 0)) {
          continue;
        }
        out.push({ panel, svgRect, sx, sy, texts, lines, bars });
      }
      return out;
    },
    { lineSrcs, barSrcs, nonLineSrcs },
  );
}

// ---- Geometry ----------------------------------------------------------
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

// Test whether a text rect intersects a line. When the line has sampled
// stroke geometry, use that (precise; small bbox overlap with no actual
// stroke crossing returns false). Fall back to bbox-vs-bbox when no
// samples are available.
function rectHitsLine(rect, line, lineHalfStroke = 1.5) {
  if (line.samples && line.samples.length > 0) {
    // Inflate the test rect by a small margin matching the stroke half-width
    // so labels don't sit ON the stroke.
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

// Translate a text rect by dy page-pixels. (text's x/width unchanged
// because we only nudge the y-attribute.)
function shiftRect(r, dy) {
  return { x: r.x, y: r.y + dy, width: r.width, height: r.height };
}

// ---- Allowlist (mirrors detector) ---------------------------------------
function loadAllowlist() {
  if (!existsSync(ALLOWLIST_PATH)) return [];
  const raw = readFileSync(ALLOWLIST_PATH, "utf-8");
  const parsed = JSON.parse(raw);
  if (!parsed || !Array.isArray(parsed.entries)) return [];
  return parsed.entries;
}
function isAllowlisted(allowlist, route, textContent) {
  for (const e of allowlist) {
    if (e.page === route && e.text === textContent) return true;
  }
  return false;
}

// ---- Candidate generation ----------------------------------------------
//
// Produces dy offsets in SVG user-space, ordered by preference.
//
// Pass 1 (geometry-aware): for each conflicting line/bar rect, compute
// the minimum vertical nudge that would push the text rect FULLY above
// or FULLY below that rect (plus a 2-px page-space margin). These are
// "just-clear" candidates and tend to look better than blind nudges
// because the label settles next to the line rather than parked far
// from it.
//
// Pass 2 (blind nudges): if none of the just-clear candidates is
// feasible (e.g. they collide with another line or run off the SVG),
// fall back to fixed magnitudes 5, 10, 15, ..., 50 SVG units, up then
// down, smallest first. Smallest first keeps the label as close to its
// authored position as possible.
//
// All offsets are in SVG user-space; the caller translates to page-pixels
// via the SVG's scale factor before testing intersections.
const BLIND_MAGNITUDES_SVG = [5, 10, 15, 20, 25, 30, 35, 40, 45, 50];

function* candidateOffsets(textRectPx, conflicts, scaleY) {
  // Pass 1: just-clear above / below each conflict.
  const seen = new Set();
  function tryEmit(dySvg) {
    const k = Math.round(dySvg * 100) / 100;
    if (seen.has(k)) return;
    seen.add(k);
    return k;
  }
  const candidates = [];
  for (const c of conflicts) {
    // To clear ABOVE c: textRect.y + textRect.height + dyPx <= c.rect.y - margin
    //   => dyPx <= c.rect.y - margin - (textRect.y + textRect.height)
    const aboveDyPx = (c.rect.y - 2) - (textRectPx.y + textRectPx.height);
    // To clear BELOW c: textRect.y + dyPx >= c.rect.y + c.rect.height + margin
    //   => dyPx >= c.rect.y + c.rect.height + 2 - textRect.y
    const belowDyPx = (c.rect.y + c.rect.height + 2) - textRectPx.y;
    candidates.push({ dyPx: aboveDyPx, dir: -1 });
    candidates.push({ dyPx: belowDyPx, dir: 1 });
  }
  // Sort by absolute dy ascending (smallest nudge first).
  candidates.sort((a, b) => Math.abs(a.dyPx) - Math.abs(b.dyPx));
  for (const cand of candidates) {
    const dySvg = cand.dyPx / scaleY;
    if (!isFinite(dySvg)) continue;
    if (Math.abs(dySvg) < 0.1) continue;       // too small to matter
    if (Math.abs(dySvg) > 50) continue;        // policy cap (spec: +/-50 SVG)
    const k = tryEmit(dySvg);
    if (k !== undefined) yield k;
  }
  // Pass 2: blind nudges, smallest first, alternating up/down.
  for (const mag of BLIND_MAGNITUDES_SVG) {
    const a = tryEmit(-mag);
    if (a !== undefined) yield a;
    const b = tryEmit(mag);
    if (b !== undefined) yield b;
  }
}

// ---- Patch the HTML file -----------------------------------------------
//
// Build a regex that matches the exact <text ...>TEXT</text> in the
// minified HTML, then replace just the y="..." value.
//
// Identification strategy: anchor on (class || cls), exact x attribute,
// exact text-anchor, exact data-astro-cid (where present), and the exact
// text content. With all those pinned, collisions are vanishingly rare
// even on dashboards with hundreds of <text> nodes.
function escapeForRegex(s) {
  return s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

function buildTextMatcher(attrs, textContent) {
  // attrs: object as read from the live DOM.
  // The minified file format observed in dist/ is:
  //   <text class="..." x="X.XX" y="Y.YY" text-anchor="..." data-astro-cid-...>TEXT</text>
  // Attribute order varies by Astro version; we match attributes positionally
  // via a tolerant pattern: the `class`, `x`, `text-anchor`, and any
  // data-astro-cid-* must all be present in the tag, in any order, with the
  // observed values. `y` is captured separately.
  //
  // Approach: regex with a capture group around the y-attribute and lookaheads
  // for the other anchoring attributes. Lookaheads work inside <text ...> as
  // long as each is bounded to the tag (no `>`).
  const cls = attrs.class || "";
  const x = attrs.x || "";
  const y = attrs.y || "";
  const textAnchor = attrs["text-anchor"] || "";
  // Find any data-astro-cid-* attribute (it's the per-component scoping key).
  const astroCidEntry = Object.entries(attrs).find(([k]) => k.startsWith("data-astro-cid"));
  const astroCid = astroCidEntry ? astroCidEntry[0] : null;

  // Lookaheads must be tag-bounded: [^>]* before each anchor.
  // We anchor on the ORIGINAL y value too -- otherwise two text elements
  // with the same class/x/anchor/cid/content but different y values
  // (common in indexed-baseline charts where the legend label sits at
  // the start AND end of the line) collapse to the same signature.
  const lookaheads = [];
  if (cls) lookaheads.push(`(?=[^>]*\\bclass="${escapeForRegex(cls)}")`);
  if (x) lookaheads.push(`(?=[^>]*\\bx="${escapeForRegex(x)}")`);
  if (y) lookaheads.push(`(?=[^>]*\\by="${escapeForRegex(y)}")`);
  if (textAnchor) lookaheads.push(`(?=[^>]*\\btext-anchor="${escapeForRegex(textAnchor)}")`);
  if (astroCid) lookaheads.push(`(?=[^>]*\\b${escapeForRegex(astroCid)}\\b)`);

  // Match <text + lookaheads + ... y="CAPTURE" ... > CHILDREN </text>
  // CHILDREN may be bare text (e.g. ">Avg 6.9%<") or wrapped in <tspan>
  // (e.g. "> <tspan ...>Q/Q SAAR</tspan> </text>"). We capture children
  // as an opaque block and re-emit verbatim; only the y-attribute is
  // swapped.
  //
  // We rely on the attribute lookaheads (class + x + ORIGINAL y +
  // text-anchor + astro-cid) to disambiguate. Pinning on textContent is
  // brittle because the DOM-decoded form ("Sellers' mkt") doesn't match
  // the file-encoded form ("Sellers&#39; mkt"). The original-y lookahead
  // is the disambiguating constraint that lets us drop the text-content
  // anchor entirely.

  // Capture groups: 1=before-y-attrs, 2=original-y-value, 3=after-y-attrs,
  // 4=children-block (everything between > and </text>).
  const pattern = new RegExp(
    `<text\\b${lookaheads.join("")}([^>]*?)\\by="([^"]+)"([^>]*)>([\\s\\S]*?)</text>`,
    "g",
  );
  return { pattern };
}

// Format y the same way as the source (2 decimal places observed).
function formatY(y) {
  return y.toFixed(2);
}

// ---- Main --------------------------------------------------------------
async function main() {
  const allowlist = loadAllowlist();
  const routes = Array.from(new Set([...STATIC_ROUTES, ...discoverResearchRoutes()]));

  let preview;
  let browser;
  try {
    preview = await startPreview();
  } catch (err) {
    console.error(`[fix-text-overlaps] could not start astro preview: ${err.message}`);
    process.exit(2);
  }
  try {
    browser = await chromium.launch();
  } catch (err) {
    await stopPreview(preview);
    console.error(`[fix-text-overlaps] could not launch chromium: ${err.message}`);
    process.exit(2);
  }

  const lineSrcs = serialisePatterns(DATA_LINE_PATTERNS);
  const barSrcs = serialisePatterns(DATA_BAR_PATTERNS);
  const nonLineSrcs = serialisePatterns(NON_DATA_LINE_PATTERNS);

  let totalDetected = 0;
  let totalFixed = 0;
  let totalAllowlisted = 0;
  const unfixable = [];

  try {
    const context = await browser.newContext({
      viewport: { width: 1240, height: 800 },
      deviceScaleFactor: 1,
    });
    const page = await context.newPage();

    for (const route of routes) {
      const url = `${BASE_URL}${route}`;
      let resp;
      try {
        resp = await page.goto(url, { waitUntil: "networkidle", timeout: 20_000 });
      } catch (err) {
        console.error(`[fix-text-overlaps] navigation failed for ${route}: ${err.message}`);
        continue;
      }
      if (!resp || resp.status() !== 200) continue;

      // Defensive: belt-and-suspenders against late navigations on CI. If
      // extractFromPage races a navigation triggered by deferred scripts or
      // font reflow, the execution-context-destroyed error fires. Retry once
      // after re-settling.
      let svgEntries;
      try {
        svgEntries = await extractFromPage(page, lineSrcs, barSrcs, nonLineSrcs);
      } catch (err) {
        if (/Execution context was destroyed/i.test(err.message)) {
          try {
            await page.waitForLoadState("networkidle", { timeout: 10_000 });
          } catch {}
          svgEntries = await extractFromPage(page, lineSrcs, barSrcs, nonLineSrcs);
        } else {
          throw err;
        }
      }

      const distFile = routeToDistFile(route);
      if (!existsSync(distFile)) {
        console.error(`[fix-text-overlaps] dist file missing for ${route}: ${distFile}`);
        continue;
      }
      let html = readFileSync(distFile, "utf-8");
      let routeFixed = 0;

      for (const svg of svgEntries) {
        // Track placed-text rects (originals + already-shifted within this
        // SVG) so subsequent candidate evaluations don't collide with a
        // sibling we just moved.
        const placedTexts = svg.texts.map((t) => ({ rect: t.rect, source: t }));

        for (const t of svg.texts) {
          // Identify conflicts the detector would flag. Must use the
          // SAME geometry algorithm as the detector (sample-based for
          // lines, bbox for bars) or the fixer flags cases the detector
          // wouldn't, and vice versa.
          const conflicts = [];
          for (const ln of svg.lines) {
            if (rectHitsLine(t.rect, ln)) conflicts.push({ kind: "line", rect: ln.rect });
          }
          for (const br of svg.bars) {
            if (rectsOverlap(t.rect, br.rect)) conflicts.push({ kind: "bar", rect: br.rect });
          }
          if (conflicts.length === 0) continue;
          totalDetected++;
          if (isAllowlisted(allowlist, route, t.text)) {
            totalAllowlisted++;
            continue;
          }
          if (t.attrY === null) {
            unfixable.push({
              route,
              panel: svg.panel,
              text: t.text,
              reason: "no parseable y attribute on source <text>",
            });
            continue;
          }

          // Try candidates. SVG dy -> page-px dy via svg.sy.
          let chosen = null;
          for (const dySvg of candidateOffsets(t.rect, conflicts, svg.sy)) {
            const dyPx = dySvg * svg.sy;
            const candidateRect = shiftRect(t.rect, dyPx);
            // Stay inside the SVG's outer bounds.
            if (
              candidateRect.y < svg.svgRect.y ||
              candidateRect.y + candidateRect.height > svg.svgRect.y + svg.svgRect.height
            ) {
              continue;
            }
            // No data-line / data-bar intersection. For LINES, prefer
            // sample-based stroke-vs-rect test (precise) over bbox test
            // (pessimistic with sloped lines). For BARS, bbox is exact.
            let hits = false;
            for (const ln of svg.lines) {
              if (rectHitsLine(candidateRect, ln)) {
                hits = true;
                break;
              }
            }
            if (hits) continue;
            for (const br of svg.bars) {
              if (rectsOverlap(candidateRect, br.rect)) {
                hits = true;
                break;
              }
            }
            if (hits) continue;
            // No collision with other placed text (excluding self).
            for (const p of placedTexts) {
              if (p.source === t) continue;
              if (rectsOverlap(candidateRect, p.rect)) {
                hits = true;
                break;
              }
            }
            if (hits) continue;
            chosen = { dySvg, candidateRect };
            break;
          }

          if (!chosen) {
            unfixable.push({
              route,
              panel: svg.panel,
              text: t.text,
              reason: "no clean candidate within +/-50 SVG units",
            });
            continue;
          }

          // Patch the HTML.
          const newY = t.attrY + chosen.dySvg;
          const { pattern: matcher } = buildTextMatcher(t.attrs, t.textContent);
          let replaced = 0;
          html = html.replace(matcher, (full, before, capturedY, after, children) => {
            replaced++;
            return `<text${before} y="${formatY(newY)}"${after}>${children}</text>`;
          });
          if (replaced === 0) {
            unfixable.push({
              route,
              panel: svg.panel,
              text: t.text,
              reason: "matcher did not locate text element in HTML file",
            });
            continue;
          }
          if (replaced > 1) {
            // The signature should be unique. If it isn't, we've nudged
            // multiple identical texts at once -- safer to flag than to
            // silently move both.
            unfixable.push({
              route,
              panel: svg.panel,
              text: t.text,
              reason: `matcher resolved ${replaced} candidates -- signature not unique`,
            });
            // We've already mutated `html`. Best-effort: continue.
          }
          totalFixed++;
          routeFixed++;
          // Update placedTexts so subsequent siblings see the new rect.
          const placedSelf = placedTexts.find((p) => p.source === t);
          if (placedSelf) placedSelf.rect = chosen.candidateRect;
        }
      }

      if (routeFixed > 0) {
        writeFileSync(distFile, html, "utf-8");
        console.log(`[fix-text-overlaps] ${route}: fixed ${routeFixed} label(s)`);
      }
    }
  } finally {
    if (browser) await browser.close();
    await stopPreview(preview);
  }

  console.log(
    `[fix-text-overlaps] summary: detected=${totalDetected} fixed=${totalFixed} allowlisted=${totalAllowlisted} unfixable=${unfixable.length}`,
  );
  if (unfixable.length > 0) {
    console.log(`[fix-text-overlaps] unfixable cases (detector will fail the build on these):`);
    for (const u of unfixable) {
      console.log(`  ${u.route}  panel=${u.panel}  text=${JSON.stringify(u.text)}  reason=${u.reason}`);
    }
  }
  // Always exit 0: residuals are the detector's responsibility.
  process.exit(0);
}

main().catch((err) => {
  console.error(`[fix-text-overlaps] unhandled: ${err && err.stack ? err.stack : err}`);
  process.exit(2);
});
