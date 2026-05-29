/**
 * check_orphan_panels.mjs
 *
 * Warning-only audit: finds panel keys emitted by the pipeline (present in
 * data/site/panel_data/<section>.json) that are NOT referenced by any section
 * page via pickPanel() or pickPanelByKey(). These are panels the pipeline
 * builds but no page renders.
 *
 * Always exits 0. This is an informational tool for pipeline maintainers to
 * spot unreferenced panels (e.g. when a page is refactored and a panel key
 * is dropped, or when the pipeline emits an alternate panel that was never
 * wired into a page). It does NOT fail CI -- use check_panel_data_wired.mjs
 * for the hard gate.
 *
 * Usage: node scripts/check_orphan_panels.mjs
 * Or:    npm run audit:orphans
 *
 * Parse strategy: same regex approach as check_panel_data_wired.mjs.
 * pickPanel(panelDataFile, N) -> "panel-N"
 * pickPanelByKey(panelDataFile, "key") -> "key"
 */

import { readFileSync, readdirSync, existsSync } from "node:fs";
import { join, dirname, basename } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = join(__dirname, "..");
const PAGES_DIR = join(ROOT, "src", "pages");
const PANEL_DATA_DIR = join(ROOT, "data", "site", "panel_data");

const PICK_PANEL_RE = /pickPanel\s*\(\s*panelDataFile\s*,\s*(\d+)\s*\)/g;
const PICK_BY_KEY_RE = /pickPanelByKey\s*\(\s*panelDataFile\s*,\s*["']([^"']+)["']\s*\)/g;
const IMPORT_RE = /import\s+panelDataFile\s+from\s+["'][^"']*data\/site\/panel_data\/(\w+)\.json["']/;

const SECTION_PAGES = [
  "gdp.astro",
  "output.astro",
  "inflation.astro",
  "labour.astro",
  "housing.astro",
  "monetary.astro",
  "fiscal.astro",
  "fiscal-team-review.astro",
  "fiscal-codex-draft.astro",
  "markets.astro",
  "trade.astro",
];

// Build a map: section -> Set<panelKey> of keys referenced by pages
const referencedBySection = {};

for (const pageFile of SECTION_PAGES) {
  const fullPath = join(PAGES_DIR, pageFile);
  if (!existsSync(fullPath)) continue;

  const src = readFileSync(fullPath, "utf-8");
  const importMatch = src.match(IMPORT_RE);
  if (!importMatch) continue;
  const section = importMatch[1];

  if (!referencedBySection[section]) referencedBySection[section] = new Set();

  let m;
  PICK_PANEL_RE.lastIndex = 0;
  while ((m = PICK_PANEL_RE.exec(src)) !== null) {
    referencedBySection[section].add(`panel-${m[1]}`);
  }
  PICK_BY_KEY_RE.lastIndex = 0;
  while ((m = PICK_BY_KEY_RE.exec(src)) !== null) {
    referencedBySection[section].add(m[1]);
  }
}

// Walk all panel_data JSON files and find orphan keys
let orphanCount = 0;

let jsonFiles;
try {
  jsonFiles = readdirSync(PANEL_DATA_DIR).filter((f) => f.endsWith(".json"));
} catch (e) {
  console.warn(`[check_orphan_panels] WARN: could not read ${PANEL_DATA_DIR}: ${e.message}`);
  process.exit(0);
}

for (const jsonFile of jsonFiles) {
  const section = jsonFile.replace(".json", "");
  const jsonPath = join(PANEL_DATA_DIR, jsonFile);
  let data;
  try {
    data = JSON.parse(readFileSync(jsonPath, "utf-8"));
  } catch (e) {
    console.warn(`[check_orphan_panels] WARN: could not parse ${jsonFile}: ${e.message}`);
    continue;
  }

  const panels = data.panels ?? {};
  const referenced = referencedBySection[section] ?? new Set();

  for (const key of Object.keys(panels)) {
    if (!referenced.has(key)) {
      // Find the page that corresponds to this section (may be multiple pages
      // for the same section JSON -- find the first match)
      const matchingPage = SECTION_PAGES.find((p) => {
        const fp = join(PAGES_DIR, p);
        if (!existsSync(fp)) return false;
        const src = readFileSync(fp, "utf-8");
        const m = src.match(IMPORT_RE);
        return m && m[1] === section;
      }) ?? `(no page imports ${section}.json)`;

      console.warn(
        `[check_orphan_panels] WARN: orphan panel ${section}/${key} ` +
        `(built by pipeline, not rendered by ${matchingPage})`
      );
      orphanCount++;
    }
  }
}

if (orphanCount === 0) {
  console.log("[check_orphan_panels] OK: no orphan panels found.");
} else {
  console.log(
    `[check_orphan_panels] ${orphanCount} orphan panel(s) found. ` +
    "These panels are built by the pipeline but not rendered by any section page. " +
    "Review and either wire them into a page or remove them from the pipeline."
  );
}

// Always exit 0 -- this is warning-only
process.exit(0);
