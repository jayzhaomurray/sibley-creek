/**
 * check_mechanical_tilelines.mjs -- guard homepage section notes against
 * drifting hand-authored copy.
 *
 * Every section with data/site/panel_data/<slug>.json must have a prose
 * template at editorial/prose_templates/<slug>.yaml, and that template must
 * render a non-empty required `tileline` surface from current panel data.
 */

import { existsSync, readFileSync, readdirSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

import { renderSectionProse } from "../src/lib/prose/loader.mjs";

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = join(__dirname, "..");
const SECTIONS_TS = join(ROOT, "src", "data", "sections.ts");
const PANEL_DATA_DIR = join(ROOT, "data", "site", "panel_data");
const TEMPLATE_DIR = join(ROOT, "editorial", "prose_templates");

function sectionSlugs() {
  const src = readFileSync(SECTIONS_TS, "utf-8");
  return [...src.matchAll(/slug:\s*"([^"]+)"/g)].map((m) => m[1]);
}

const panelSlugs = new Set(
  readdirSync(PANEL_DATA_DIR)
    .filter((f) => f.endsWith(".json"))
    .map((f) => f.replace(/\.json$/, ""))
);

let failures = 0;
for (const slug of sectionSlugs()) {
  if (!panelSlugs.has(slug)) continue;
  const templatePath = join(TEMPLATE_DIR, `${slug}.yaml`);
  if (!existsSync(templatePath)) {
    console.error(`FAIL: ${slug}: missing ${templatePath}`);
    failures++;
    continue;
  }

  try {
    const result = renderSectionProse(slug, { root: ROOT });
    const text = result.surfaces.tileline?.text?.trim();
    if (!text) {
      console.error(`FAIL: ${slug}: template rendered an empty tileline`);
      failures++;
    }
  } catch (e) {
    console.error(`FAIL: ${slug}: ${e.message}`);
    failures++;
  }
}

if (failures > 0) {
  console.error(`[check_mechanical_tilelines] FAIL: ${failures} section(s).`);
  process.exit(1);
}

console.log(`[check_mechanical_tilelines] OK: ${panelSlugs.size} mechanical tileline template(s).`);
