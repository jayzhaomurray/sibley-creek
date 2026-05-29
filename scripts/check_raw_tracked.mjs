/**
 * check_raw_tracked.mjs
 *
 * Pre-build guard: for every panel key referenced by a section page via
 * pickPanel() or pickPanelByKey(), assert that every path listed in that
 * panel's source_files array is tracked by git.
 *
 * Root-cause context (2026-05-28)
 * --------------------------------
 * /housing/ plate-3 and /markets/ plate-3 rendered "DATA NOT YET WIRED"
 * because crea_resales.csv and tsx_composite.csv were in .gitignore.
 * check_panel_data_wired.mjs catches the *symptom* (null primary data in the
 * committed JSON). This script catches the *root cause* (raw CSV absent from
 * git) so the failure is blocked before it ever reaches the build step.
 *
 * What it checks
 * --------------
 * 1. Scans src/pages/*.astro for pickPanel() / pickPanelByKey() references
 *    using the same wired-detection logic as check_panel_data_wired.mjs.
 * 2. For each (section, panelKey) tuple, reads metadata.source_files from
 *    data/site/panel_data/<section>.json.
 * 3. Collects all source_files paths across all wired panels into a set.
 * 4. For each path, runs `git ls-files <path>` to verify git tracks it.
 * 5. If any path is untracked: exit 1 with the missing file, which panel
 *    needs it, and the fix command (git add -f <path>).
 * 6. If all clean: exit 0 silently.
 *
 * Parse strategy: simple regex on pickPanel / pickPanelByKey patterns --
 * matches the approach in check_panel_data_wired.mjs. Raw panelsById[]
 * lookups are banned access patterns and are not scanned.
 *
 * Note on empty source_files lists
 * ---------------------------------
 * Panels with no disk-resident source files (e.g. a panel whose raw series
 * do not yet exist on disk, or a panel that is purely API-backed with no
 * local cache) will have source_files: []. This script skips those panels
 * -- there is nothing to verify. check_panel_data_wired.mjs catches the
 * downstream consequence (null primary) in that case.
 */

import { readFileSync, existsSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { execSync } from "node:child_process";

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = join(__dirname, "..");
const PAGES_DIR = join(ROOT, "src", "pages");
const PANEL_DATA_DIR = join(ROOT, "data", "site", "panel_data");

// Same regex patterns as check_panel_data_wired.mjs
const PICK_PANEL_RE = /pickPanel\s*\(\s*panelDataFile\s*,\s*(\d+)\s*\)/g;
const PICK_BY_KEY_RE = /pickPanelByKey\s*\(\s*panelDataFile\s*,\s*["']([^"']+)["']\s*\)/g;
const IMPORT_RE = /import\s+panelDataFile\s+from\s+["'][^"']*data\/site\/panel_data\/(\w+)\.json["']/;

// Keep in sync with check_panel_data_wired.mjs SECTION_PAGES
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

// Collect wired references: { pageFile, section, panelKey }[]
const references = [];

for (const pageFile of SECTION_PAGES) {
  const fullPath = join(PAGES_DIR, pageFile);
  if (!existsSync(fullPath)) continue;

  const src = readFileSync(fullPath, "utf-8");

  const importMatch = src.match(IMPORT_RE);
  if (!importMatch) continue;
  const section = importMatch[1];

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
  console.log("[check_raw_tracked] OK: no panel references found in section pages (nothing to check).");
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
  } catch {
    sectionData[section] = null;
  }
  return sectionData[section];
}

// Check whether a path is tracked by git. Returns true if tracked.
function isTrackedByGit(relPath) {
  try {
    const result = execSync(`git ls-files "${relPath}"`, {
      cwd: ROOT,
      encoding: "utf-8",
      stdio: ["pipe", "pipe", "pipe"],
    }).trim();
    return result.length > 0;
  } catch {
    return false;
  }
}

// Collect: path -> [{ section, panelKey, pageFile }, ...]
// Track which panels need each file so the error message is specific.
const pathToPanels = new Map();

for (const { pageFile, section, panelKey } of references) {
  const data = loadSection(section);
  if (!data) continue; // check_panel_data_wired.mjs covers missing JSON

  const panel = (data.panels ?? {})[panelKey];
  if (!panel) continue; // check_panel_data_wired.mjs covers missing panel key

  const sourceFiles = panel.source_files;
  if (!Array.isArray(sourceFiles) || sourceFiles.length === 0) continue;

  for (const relPath of sourceFiles) {
    if (!pathToPanels.has(relPath)) {
      pathToPanels.set(relPath, []);
    }
    pathToPanels.get(relPath).push({ section, panelKey, pageFile });
  }
}

if (pathToPanels.size === 0) {
  console.log("[check_raw_tracked] OK: no source_files entries found across wired panels (nothing to check).");
  process.exit(0);
}

let failures = 0;

for (const [relPath, panels] of pathToPanels) {
  if (!isTrackedByGit(relPath)) {
    const panelList = [...new Set(panels.map(p => `${p.section}/${p.panelKey}`))].join(", ");
    const pageList = [...new Set(panels.map(p => p.pageFile))].join(", ");
    console.error(
      `[check_raw_tracked] ERROR: ${relPath} is NOT tracked by git.\n` +
      `  Required by panel(s): ${panelList}\n` +
      `  Referenced from page(s): ${pageList}\n` +
      `  Fix: git add -f ${relPath}`
    );
    failures++;
  }
}

if (failures > 0) {
  console.error(
    `\n[check_raw_tracked] FAIL: ${failures} source file(s) backing wired panels are not tracked by git.\n` +
    "Root-cause: a pipeline raw CSV (or derived file) is in .gitignore and was not force-added.\n" +
    "Fix checklist:\n" +
    "  1. git add -f <path> for each file listed above\n" +
    "  2. Regenerate panel_data: py -m pipeline.io.panel_data\n" +
    "  3. Re-run this check: npm run audit:raw-tracked"
  );
  process.exit(1);
}

console.log(
  `[check_raw_tracked] OK: ${pathToPanels.size} source file(s) across ` +
  `${references.length} wired panel reference(s) are all tracked by git.`
);
