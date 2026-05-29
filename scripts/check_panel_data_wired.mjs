/**
 * check_panel_data_wired.mjs
 *
 * Pre-build guard: for every panel key referenced by a section page via
 * pickPanel() or pickPanelByKey(), assert that the corresponding entry in
 * the panel_data JSON has a non-null primary series with at least one data
 * point. Exits 1 with an actionable error if any WIRED panel fails.
 *
 * Root-cause context (2026-05-28)
 * --------------------------------
 * /housing/ plate-3 and /markets/ plate-3 rendered "DATA NOT YET WIRED"
 * on the live site because the raw CSVs backing those panels were gitignored
 * and the committed panel_data JSONs had null primary data. The TK guardrail
 * (check_tk_in_dist.mjs) does NOT catch this because the component renders
 * null panels as a styled empty-state, not a literal TK string. This script
 * closes that gap by asserting wired status BEFORE astro build runs.
 *
 * What it checks
 * --------------
 * 1. Scans src/pages/*.astro for JSON imports from data/site/panel_data/<section>.json
 * 2. Extracts pickPanel(panelDataFile, N) calls -> panel key "panel-N"
 *    Extracts pickPanelByKey(panelDataFile, "key") calls -> panel key "key"
 * 3. For each (section, panelKey) tuple: loads the JSON, finds the panel,
 *    asserts primary != null AND primary.data.length > 0.
 * 4. If any assertion fails: exit 1 with section, page file, panel key, failure reason.
 *
 * Note: panels with expectedStatus "NEAR" or "MISSING" in the JSON are NOT
 * referenced by any page and will not appear in the referenced set. If they
 * somehow do appear (i.e., a page references a panel the pipeline marks NEAR),
 * this script will correctly fail them.
 *
 * Parse strategy: simple regex, not a full AST walker. Sufficient for the
 * structured patterns pickPanel(panelDataFile, N) and
 * pickPanelByKey(panelDataFile, "...") which are the only sanctioned access
 * patterns. Raw panelsById[key] lookups are banned; use pickPanelByKey.
 */

import { readFileSync, readdirSync, existsSync } from "node:fs";
import { join, dirname, basename } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = join(__dirname, "..");
const PAGES_DIR = join(ROOT, "src", "pages");
const PANEL_DATA_DIR = join(ROOT, "data", "site", "panel_data");

// pickPanel(panelDataFile, 7) -> key "panel-7"
const PICK_PANEL_RE = /pickPanel\s*\(\s*panelDataFile\s*,\s*(\d+)\s*\)/g;
// pickPanelByKey(panelDataFile, "panel-7-alt") or 'panel-9'
const PICK_BY_KEY_RE = /pickPanelByKey\s*\(\s*panelDataFile\s*,\s*["']([^"']+)["']\s*\)/g;
// import panelDataFile from "../../data/site/panel_data/<section>.json"
const IMPORT_RE = /import\s+panelDataFile\s+from\s+["'][^"']*data\/site\/panel_data\/(\w+)\.json["']/;

// Section pages to scan. Explicitly listed to avoid scanning every .astro page.
// Keep in sync with CANONICAL_SLUGS in check_sections_slug_alignment.mjs.
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

// Collect references: { pageFile, section, panelKey }[]
const references = [];

for (const pageFile of SECTION_PAGES) {
  const fullPath = join(PAGES_DIR, pageFile);
  if (!existsSync(fullPath)) continue;

  const src = readFileSync(fullPath, "utf-8");

  const importMatch = src.match(IMPORT_RE);
  if (!importMatch) continue; // page does not import a panel_data file
  const section = importMatch[1];

  // Reset lastIndex before each exec loop
  let m;

  PICK_PANEL_RE.lastIndex = 0;
  while ((m = PICK_PANEL_RE.exec(src)) !== null) {
    references.push({ pageFile, section, panelKey: `panel-${m[1]}` });
  }

  PICK_BY_KEY_RE.lastIndex = 0;
  while ((m = PICK_BY_KEY_RE.exec(src)) !== null) {
    references.push({ pageFile, section, panelKey: m[1] });
  }
}

if (references.length === 0) {
  console.log("[check_panel_data_wired] OK: no panel references found in section pages (nothing to check).");
  process.exit(0);
}

// Load JSON files once per section
const sectionData = {};
function loadSection(section) {
  if (section in sectionData) return sectionData[section];
  const jsonPath = join(PANEL_DATA_DIR, `${section}.json`);
  if (!existsSync(jsonPath)) {
    sectionData[section] = null;
    return null;
  }
  try {
    sectionData[section] = JSON.parse(readFileSync(jsonPath, "utf-8"));
  } catch (e) {
    sectionData[section] = null;
  }
  return sectionData[section];
}

let failures = 0;

for (const { pageFile, section, panelKey } of references) {
  const data = loadSection(section);
  if (!data) {
    console.error(
      `[check_panel_data_wired] ERROR: ${pageFile} references ${section}/${panelKey} ` +
      `but data/site/panel_data/${section}.json does not exist or could not be parsed.\n` +
      `  Fix: run the pipeline to regenerate panel_data, or check that the section slug matches.`
    );
    failures++;
    continue;
  }

  const panels = data.panels ?? {};
  const panel = panels[panelKey];

  if (!panel) {
    console.error(
      `[check_panel_data_wired] ERROR: ${pageFile} references ${section}/${panelKey} ` +
      `but that key does not exist in data/site/panel_data/${section}.json.\n` +
      `  Present keys: [${Object.keys(panels).join(", ")}]\n` +
      `  Fix: run the pipeline to regenerate panel_data, or check the panel key spelling.`
    );
    failures++;
    continue;
  }

  const primary = panel.primary;
  if (!primary) {
    console.error(
      `[check_panel_data_wired] ERROR: ${pageFile} / ${section}/${panelKey}: ` +
      `primary is null. The panel will render "DATA NOT YET WIRED".\n` +
      `  expectedStatus in JSON: ${panel.expectedStatus ?? "(none)"}\n` +
      `  Fix: run the pipeline so that the raw source CSV is fetched and panel_data is regenerated. ` +
      `If the raw CSV is not committed to git, force-track it: git add -f data/raw/<file>.csv`
    );
    failures++;
    continue;
  }

  if (!Array.isArray(primary.data) || primary.data.length === 0) {
    console.error(
      `[check_panel_data_wired] ERROR: ${pageFile} / ${section}/${panelKey}: ` +
      `primary.data is empty (length ${Array.isArray(primary.data) ? 0 : "non-array"}). ` +
      `The panel will render "DATA NOT YET WIRED".\n` +
      `  series key: ${primary.key ?? "(none)"}, unit: ${primary.unit ?? "(none)"}\n` +
      `  Fix: run the pipeline so that primary.data is populated before building.`
    );
    failures++;
    continue;
  }
}

if (failures > 0) {
  console.error(
    `\n[check_panel_data_wired] FAIL: ${failures} WIRED panel(s) have null or empty primary data.\n` +
    "Root-cause checklist:\n" +
    "  1. The raw source CSV is not committed to git (fix: git add -f data/raw/<file>.csv)\n" +
    "  2. The pipeline did not run before npm run build (fix: python -m pipeline.build or build_financial.py)\n" +
    "  3. A new panel key was added to a page but the pipeline does not yet emit it"
  );
  process.exit(1);
}

console.log(
  `[check_panel_data_wired] OK: ${references.length} panel reference(s) across ` +
  `${[...new Set(references.map(r => r.section))].length} section(s) all have non-empty primary data.`
);
