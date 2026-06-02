#!/usr/bin/env node
/**
 * check_chartbook_contract.mjs
 *
 * Source-level guard for chartbook chart drift. This intentionally scans
 * component source instead of built HTML so it can run before a build and before
 * visual QA.
 *
 * Contract enforced here:
 * - Chartbook SVG text is chart furniture only: axis ticks, direct labels,
 *   compact subpanel labels, numeric callouts, and short data annotations.
 * - Full prose belongs in ChartbookUnit/page slots, not inside chart SVGs.
 * - Chartbook chart components should not use section-accent tokens for data
 *   marks; chart data stays monochrome except allowed latest markers.
 *
 * This is not wired into `npm run build` yet because active fiscal work may be
 * mid-edit. Run manually:
 *
 *   node scripts/check_chartbook_contract.mjs
 */

import { readdirSync, readFileSync } from "node:fs";
import { dirname, resolve, relative } from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const ROOT = resolve(dirname(__filename), "..");
const CHARTS_DIR = resolve(ROOT, "src/components/charts");

const SKIP_DIR_PARTS = [
  `${sep()}_archive${sep()}`,
  `${sep()}_alternatives${sep()}`,
  `${sep()}_canon_reference${sep()}`,
];

const LONG_TEXT_LIMIT = 55;

function sep() {
  return process.platform === "win32" ? "\\" : "/";
}

function walk(dir) {
  const out = [];
  for (const ent of readdirSync(dir, { withFileTypes: true })) {
    const full = resolve(dir, ent.name);
    if (ent.isDirectory()) out.push(...walk(full));
    else if (ent.isFile() && ent.name.endsWith(".astro")) out.push(full);
  }
  return out;
}

function stripAstroComments(src) {
  return src
    .replace(/\/\*[\s\S]*?\*\//g, " ")
    .replace(/<!--[\s\S]*?-->/g, " ");
}

function decodeEntities(s) {
  return s
    .replace(/&amp;/g, "&")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/&nbsp;/g, " ")
    .replace(/&#\d+;/g, " ")
    .replace(/&[a-z]+;/gi, " ");
}

function normalizeText(s) {
  return decodeEntities(s.replace(/<[^>]+>/g, " "))
    .replace(/\s+/g, " ")
    .trim();
}

function isChartbookFile(filePath) {
  const rel = relative(ROOT, filePath);
  if (!rel.startsWith("src")) return false;
  for (const part of SKIP_DIR_PARTS) {
    if (filePath.includes(part)) return false;
  }
  // Root-level MiniChart/HeroChart are not chartbook plates.
  if (rel === "src\\components\\charts\\MiniChart.astro" || rel === "src/components/charts/MiniChart.astro") return false;
  if (rel === "src\\components\\charts\\HeroChart.astro" || rel === "src/components/charts/HeroChart.astro") return false;
  return true;
}

function lineNumber(src, index) {
  return src.slice(0, index).split(/\r?\n/).length;
}

const violations = [];
const warnings = [];

for (const file of walk(CHARTS_DIR).filter(isChartbookFile)) {
  const rel = relative(ROOT, file).replace(/\\/g, "/");
  const raw = readFileSync(file, "utf-8");
  const src = stripAstroComments(raw);

  const textTagRe = /<text\b[^>]*>([\s\S]*?)<\/text>/g;
  let m;
  while ((m = textTagRe.exec(src)) !== null) {
    const inner = m[1] ?? "";
    // Dynamic JSX labels are budgeted by their producing component and often
    // contain source code, tspan maps, or formatting expressions. This source
    // checker enforces literal visible text because that is where agents tend
    // to paste prose into SVGs.
    if (inner.includes("{")) continue;
    const text = normalizeText(inner);
    if (!text) continue;
    if (text.length > LONG_TEXT_LIMIT) {
      violations.push({
        file: rel,
        line: lineNumber(src, m.index),
        label: "long SVG text",
        detail:
          `Visible <text> is ${text.length} chars. Put full prose in the ` +
          `ChartbookUnit title/interpretation slot, not inside the SVG.`,
        excerpt: text,
      });
    }
  }

  const sectionAccentRe = /(?:fill|stroke)\s*:\s*var\(--section-accent-[^)]+\)/g;
  while ((m = sectionAccentRe.exec(src)) !== null) {
    violations.push({
      file: rel,
      line: lineNumber(src, m.index),
      label: "section accent in chart component",
      detail:
        "Chartbook data marks should not use section-accent tokens. Use " +
        "pure ink plus stroke weight/dash/tint unless an art-director " +
        "exception is documented.",
      excerpt: m[0],
    });
  }

  const hasCanonLiteralViewBox = /viewBox\s*=\s*["']0 0 720 405["']/.test(src);
  const hasCanonVariableViewBox =
    /const\s+VB_W\s*=\s*720\b/.test(src) &&
    /const\s+VB_H\s*=\s*405\b/.test(src) &&
    /viewBox=\{`0 0 \$\{VB_W\} \$\{VB_H\}`\}/.test(src);
  const delegatesToLiveChart = /<PanelLiveChart\b/.test(src);
  const hasSvg = /<svg\b/.test(src);
  if (hasSvg && !delegatesToLiveChart && !hasCanonLiteralViewBox && !hasCanonVariableViewBox) {
    warnings.push({
      file: rel,
      line: 1,
      label: "non-standard viewBox",
      detail:
        "Bespoke chartbook SVG does not obviously use 0 0 720 405. " +
        "This may be valid for special forms, but should be intentional.",
      excerpt: "",
    });
  }
}

if (warnings.length > 0) {
  console.error("[check-chartbook-contract] WARNINGS:");
  for (const w of warnings) {
    console.error(`  ${w.file}:${w.line} [${w.label}] ${w.detail}`);
  }
  console.error("");
}

if (violations.length > 0) {
  console.error(`[check-chartbook-contract] FAIL: ${violations.length} violation(s):\n`);
  for (const v of violations) {
    console.error(`  ${v.file}:${v.line} [${v.label}]`);
    console.error(`    ${v.detail}`);
    if (v.excerpt) console.error(`    text: ${JSON.stringify(v.excerpt.slice(0, 160))}`);
  }
  process.exit(1);
}

console.log("[check-chartbook-contract] OK: chartbook SVG contract holds.");
