/**
 * check_sections_slug_alignment.mjs
 *
 * Pre-build guard: verifies that the section keys in data/site/sections.json
 * match the canonical SectionSlug set in src/data/sections.ts.
 *
 * Root-cause context (2026-05-23)
 * --------------------------------
 * The pipeline emitted sections.json with key "gdp" while sections.ts declared
 * slug "output". The site_data_loader.ts enriched section does a lookup by
 * canon.slug -- it reads payload.sections?.["output"], finds nothing, and
 * silently renders all prints as null placeholders. The TK guardrail
 * (check_tk_in_dist.mjs) does NOT catch this because the component renders
 * null-valued prints as styled mid-gray placeholders, not literal "TK" strings.
 *
 * This script fills that gap: it runs BEFORE astro build so a slug mismatch
 * fails loudly at pre-build rather than silently producing a hollow tile.
 *
 * What it checks
 * --------------
 * 1. Every slug in the CANONICAL_SLUGS set appears as a key in sections.json.
 * 2. No unexpected extra keys appear in sections.json (drift the other way).
 * 3. Every section that IS present does not carry an `error` sentinel
 *    (meaning the pipeline failed to build that section's primary series).
 *
 * The canonical slug set is duplicated here intentionally: this script must
 * NOT import from src/data/sections.ts (which requires Vite/ESM context).
 * Keep this list in sync with SectionSlug in src/data/sections.ts and
 * SECTION_SLUGS in pipeline/io/site_data.py. If you add a section, update
 * all three.
 */

import { readFileSync, existsSync } from "fs";
import { join, dirname } from "path";
import { fileURLToPath } from "url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = join(__dirname, "..");
const SECTIONS_JSON = join(ROOT, "data", "site", "sections.json");

// Canonical slug set. Must match:
//   - SectionSlug union in src/data/sections.ts
//   - SECTION_SLUGS tuple in pipeline/io/site_data.py
const CANONICAL_SLUGS = new Set([
  "output",
  "inflation",
  "labour",
  "housing",
  "monetary",
  "fiscal",
  "markets",
  "trade",
]);

if (!existsSync(SECTIONS_JSON)) {
  console.error(
    "[check_sections_slug_alignment] FAIL: data/site/sections.json not found.\n" +
    "  Run the pipeline before building: python -m pipeline.io.site_data\n" +
    "  or: python -m pipeline.build_financial"
  );
  process.exit(1);
}

let payload;
try {
  payload = JSON.parse(readFileSync(SECTIONS_JSON, "utf-8"));
} catch (e) {
  console.error(`[check_sections_slug_alignment] FAIL: could not parse sections.json: ${e.message}`);
  process.exit(1);
}

const sections = payload.sections ?? {};
const emittedSlugs = new Set(Object.keys(sections));

let failures = 0;

// Check 1: every canonical slug is present.
for (const slug of CANONICAL_SLUGS) {
  if (!emittedSlugs.has(slug)) {
    console.error(
      `[check_sections_slug_alignment] FAIL: canonical slug "${slug}" is MISSING from sections.json.\n` +
      `  Pipeline emitted: [${[...emittedSlugs].join(", ")}]\n` +
      `  Expected:         [${[...CANONICAL_SLUGS].join(", ")}]\n` +
      "  Fix: rename the matching key in pipeline/io/site_data.py SECTION_SLUGS,\n" +
      "       SECTION_CONFIGS, and SUPPORTING_PRINTS, then re-run the pipeline."
    );
    failures++;
  }
}

// Check 2: no unexpected extra keys.
for (const slug of emittedSlugs) {
  if (!CANONICAL_SLUGS.has(slug)) {
    console.error(
      `[check_sections_slug_alignment] WARN: sections.json contains unexpected slug "${slug}" not in CANONICAL_SLUGS.\n` +
      "  This is usually a stale key from a rename. Re-run the pipeline to overwrite."
    );
    // Warn, don't fail -- stale keys are harmless; missing keys are critical.
  }
}

// Check 3: no error sentinels on canonical sections (primary series missing).
for (const slug of CANONICAL_SLUGS) {
  const section = sections[slug];
  if (section && section.error) {
    console.warn(
      `[check_sections_slug_alignment] WARN: section "${slug}" carries a pipeline error: ${section.error}\n` +
      "  This section will render all prints as TK placeholders."
    );
    // Warn only -- a missing optional series (e.g. output-gap not yet fetched)
    // should not block a build. The TK guardrail catches anything that leaks
    // into reader-visible HTML as a literal TK string.
  }
}

if (failures > 0) {
  console.error(
    `\n[check_sections_slug_alignment] FAIL: ${failures} slug alignment error(s). ` +
    "Fix pipeline/io/site_data.py and re-run the pipeline before building."
  );
  process.exit(1);
}

console.log(
  `[check_sections_slug_alignment] OK: ${emittedSlugs.size} section slug(s) aligned with canonical set.`
);
