/**
 * check_chart_tooltips.mjs -- guard against native SVG hover text on live
 * chart components.
 *
 * Browser-native SVG <title> children produce hover popups. Reader-facing
 * chart precision should be visible on the page, not hidden in hover text.
 * Archived/reference/alternative charts are excluded from this live-site
 * guard.
 */

import { readFileSync, readdirSync, statSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = join(__dirname, "..");
const CHARTS_DIR = join(ROOT, "src", "components", "charts");
const EXCLUDED_DIRS = new Set(["_archive", "_alternatives", "_canon_reference"]);

function* walk(dir) {
  for (const name of readdirSync(dir)) {
    if (EXCLUDED_DIRS.has(name)) continue;
    const path = join(dir, name);
    const st = statSync(path);
    if (st.isDirectory()) yield* walk(path);
    else if (path.endsWith(".astro")) yield path;
  }
}

let failures = 0;
for (const file of walk(CHARTS_DIR)) {
  const lines = readFileSync(file, "utf-8").split(/\r?\n/);
  lines.forEach((line, idx) => {
    const trimmed = line.trim();
    const isComment =
      trimmed.startsWith("*") ||
      trimmed.startsWith("/*") ||
      trimmed.startsWith("//") ||
      trimmed.startsWith("{/*");
    if (!isComment && /<title(\s|>)/.test(line)) {
      console.error(`FAIL: ${file}:${idx + 1}: SVG <title> tooltip found`);
      failures++;
    }
  });
}

if (failures > 0) {
  console.error(`[check_chart_tooltips] FAIL: ${failures} tooltip node(s).`);
  process.exit(1);
}

console.log("[check_chart_tooltips] OK: no live SVG <title> tooltip nodes.");
