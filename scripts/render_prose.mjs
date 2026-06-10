/**
 * render_prose.mjs -- dump every rendered prose surface for a section.
 *
 * The review gates (fact-check / style / surface-fit) and any debugging
 * session use this to see exactly what the deterministic renderer produces
 * from the CURRENT panel data, including which variant fired and the
 * predicate that selected it.
 *
 * Usage:
 *   node scripts/render_prose.mjs <section>
 *   node scripts/render_prose.mjs markets --template editorial/prose_templates/_stub_markets_test.yaml
 *
 * Exit codes: 0 rendered cleanly; 1 template/render error (same failure the
 * site build would hit).
 */

import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { renderSectionProse } from "../src/lib/prose/loader.mjs";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");

const args = process.argv.slice(2);
const section = args.find((a) => !a.startsWith("--"));
const templateFlagIdx = args.indexOf("--template");
const templatePath =
  templateFlagIdx >= 0 && args[templateFlagIdx + 1]
    ? resolve(ROOT, args[templateFlagIdx + 1])
    : undefined;

if (!section) {
  console.error("usage: node scripts/render_prose.mjs <section> [--template <path>]");
  process.exit(1);
}

let result;
try {
  result = renderSectionProse(section, { root: ROOT, templatePath });
} catch (e) {
  console.error(`RENDER FAILED for section "${section}":`);
  console.error(`  ${e.message}`);
  process.exit(1);
}

console.log(`section:    ${result.section}`);
console.log(`template:   ${result.templatePath}`);
console.log(`panel data: ${result.panelDataPath} (generatedAt ${result.generatedAt})`);
console.log("");

for (const surface of Object.values(result.surfaces)) {
  const flag = surface.required ? " (required)" : "";
  console.log(`== ${surface.id}${flag} ==`);
  if (surface.parts.length === 0) {
    console.log("   <empty -- every sentence/variant dropped>");
  }
  for (const part of surface.parts) {
    const where =
      part.sentenceIndex === null
        ? `variant[${part.variantIndex}]`
        : `sentence[${part.sentenceIndex}] variant[${part.variantIndex}]`;
    console.log(`   ${where} when: ${part.predicate}`);
  }
  console.log(`   text: ${surface.text}`);
  console.log("");
}

if (result.warnings.length > 0) {
  console.log("warnings:");
  for (const w of result.warnings) console.log(`  WARN: ${w}`);
}
