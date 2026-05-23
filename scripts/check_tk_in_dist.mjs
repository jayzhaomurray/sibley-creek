/**
 * check_tk_in_dist.mjs
 *
 * Post-build guard: fail loudly if any reader-facing page in dist/ contains
 * a raw TK placeholder that escaped into rendered HTML.
 *
 * What it catches
 * ---------------
 * - ">TK<"    -- a TK string rendered as visible text in a DOM node
 * - ">TK "    -- TK at the start of a text node with trailing space (e.g. "TK pp")
 * - " TK<"    -- TK at the end of a text node
 * - value="TK" -- TK in a data-attribute (e.g. callout value rendered into HTML)
 *
 * Root-cause context (2026-05-22 TSX incident)
 * -------------------------------------------
 * build_financial.py fetched tsx_composite.csv daily but did NOT call
 * build_site_data / build_all_panel_data afterward, leaving sections.json and
 * markets.json with stale "available: false" / null primary slots. The TSX
 * Composite print on /markets/ rendered "TK" for value/delta/asOf until the
 * next full pipeline.build run. That structural gap was closed by adding
 * build_site_data + build_all_panel_data calls at the end of build_financial
 * main(). This script is the final safety net: if any stale TK survives into
 * dist/, CI fails before the deploy step.
 *
 * Exclusions
 * ----------
 * - dist/og-preview/ (internal dev route, stripped by strip_dev_routes.mjs)
 * - dist/chart-alternatives/ and dist/chart-archive/ (also stripped)
 * - Any path containing "CLAUDE" or "ARCHITECTURE" (not reader pages)
 * - The script file itself (obviously)
 * - Comments and attribute names that mention "TK" as a concept
 *   (e.g. data-series="goc-10y" does NOT match; only rendered text values)
 */

import { readdirSync, readFileSync, statSync } from "fs";
import { join, relative } from "path";

const DIST_DIR = new URL("../dist", import.meta.url).pathname.replace(/^\/([A-Za-z]:)/, "$1");

// Patterns that indicate a raw TK placeholder survived into rendered HTML.
// We match against the raw HTML string so we can catch TKs in text nodes,
// attribute values, and JSON-in-script blocks.
const TK_PATTERNS = [
  // Visible text node: <span>TK</span> or >TK pp< or > TK<
  />TK</,
  />TK\s/,
  /\sTK</,
  // In attribute value: value="TK" or data-value="TK"
  /="TK"/,
  /='TK'/,
  // In JSON embedded in <script type="application/json"> or astro islands:
  /:\s*"TK"/,
  /:\s*'TK'/,
];

// HTML files to skip — dev-only routes that strip_dev_routes.mjs may have
// already removed. We check for existence so this is safe regardless.
const SKIP_SUBDIRS = new Set([
  "og-preview",
  "chart-alternatives",
  "chart-archive",
]);

function* walkHtml(dir) {
  for (const entry of readdirSync(dir, { withFileTypes: true })) {
    const full = join(dir, entry.name);
    if (entry.isDirectory()) {
      if (SKIP_SUBDIRS.has(entry.name)) continue;
      yield* walkHtml(full);
    } else if (entry.isFile() && entry.name.endsWith(".html")) {
      yield full;
    }
  }
}

let failures = 0;
const checked = [];

for (const htmlPath of walkHtml(DIST_DIR)) {
  const rel = relative(DIST_DIR, htmlPath);
  const html = readFileSync(htmlPath, "utf-8");
  const hits = [];
  for (const pat of TK_PATTERNS) {
    if (pat.test(html)) {
      // Find the line number for easier debugging
      const lines = html.split("\n");
      for (let i = 0; i < lines.length; i++) {
        if (pat.test(lines[i])) {
          // Truncate long lines so the log is scannable
          const excerpt = lines[i].trim().slice(0, 120);
          hits.push({ line: i + 1, pat: pat.toString(), excerpt });
        }
      }
    }
  }
  checked.push(rel);
  if (hits.length > 0) {
    failures += hits.length;
    console.error(`\nTK FOUND in dist/${rel}:`);
    for (const h of hits) {
      console.error(`  line ${h.line} [${h.pat}]: ${h.excerpt}`);
    }
  }
}

if (failures > 0) {
  console.error(
    `\n[check_tk_in_dist] FAIL: ${failures} TK placeholder(s) found across ${checked.length} HTML file(s).`
  );
  console.error(
    "Root-cause checklist:\n" +
    "  1. pipeline.build_financial or pipeline.build did not run before npm run build\n" +
    "  2. A series CSV exists in data/raw/ but sections.json / panel_data/*.json are stale\n" +
    "  3. A new series was added to site_data.py / panel_data.py but its CSV was never fetched\n" +
    "  4. A hard-coded TK string was accidentally committed to a plate title or blurb"
  );
  process.exit(1);
}

console.log(`[check_tk_in_dist] OK: no TK placeholders in ${checked.length} HTML file(s).`);
