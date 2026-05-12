#!/usr/bin/env node
/**
 * Label-budget hygiene check.
 *
 * Fails CI when known-constrained reader-facing slots carry copy over
 * their character budget. The point is to fail BEFORE deploy rather
 * than let silent mid-word truncation hit the live site.
 *
 * Run from repo root:
 *   node scripts/check_label_budgets.mjs
 *
 * Exit code 0 = OK; 1 = at least one slot is over budget.
 *
 * Budgets are tracked in the BUDGETS table below. To add a new
 * constrained slot, append an entry and extend the extractor.
 *
 * Memory notes:
 *   feedback_constrained_slots_need_char_budget.md
 *   feedback_check_all_pipeline_tiers.md
 */
import { readFileSync, readdirSync } from "node:fs";
import { resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const ROOT = resolve(dirname(__filename), "..");

// ---- Budget table ---------------------------------------------------------
const BUDGETS = [
  {
    name: "tileLine",
    file: "src/data/sections.ts",
    limit: 85,
    extractor: extractTileLines,
    why:
      "Splash tile blurb. Slot was previously line-clamp:3 + max-width:44ch + overflow:hidden which silently truncated mid-word. Line-clamp dropped 2026-05-11; budget enforced here so lines stay readable across the 7-card splash grid.",
  },
  {
    name: "heroKicker",
    file: "src/data/sections.ts",
    limit: 22,
    extractor: extractHeroKickers,
    why:
      "Splash tile eyebrow / hero kicker rail. Rendered in uppercase Manrope 600 micro-caps; rail is tight at typical breakpoints.",
  },
  {
    name: "page pageDescription (OG description)",
    file: "src/pages",
    limit: 160,
    extractor: extractPageDescriptions,
    why:
      "Used as the OG / meta description; longer than ~160 chars truncates in LinkedIn / Twitter previews.",
  },
];

// ---- Main -----------------------------------------------------------------
const failures = [];
let totalChecked = 0;

for (const budget of BUDGETS) {
  const slotEntries = budget.extractor(budget);
  totalChecked += slotEntries.length;
  for (const entry of slotEntries) {
    if (entry.value.length > budget.limit) {
      failures.push({
        budget: budget.name,
        limit: budget.limit,
        actual: entry.value.length,
        location: entry.location,
        value: entry.value,
      });
    }
  }
}

if (failures.length === 0) {
  console.log(
    `[check-label-budgets] OK -- ${totalChecked} slot(s) checked across ${BUDGETS.length} budget type(s), all within their limits.`,
  );
  process.exit(0);
}

console.error(
  `[check-label-budgets] FAIL -- ${failures.length} slot(s) over budget:\n`,
);
for (const f of failures) {
  console.error(
    `  ${f.location}\n    budget: ${f.budget} (limit ${f.limit} chars)\n    actual: ${f.actual} chars\n    value:  ${JSON.stringify(f.value)}\n`,
  );
}
console.error(
  "Fix: shorten the over-budget value(s), or revise the budget in scripts/check_label_budgets.mjs with rationale.\n",
);
process.exit(1);

// ---- Extractors -----------------------------------------------------------

function extractTileLines(budget) {
  const src = readFileSync(resolve(ROOT, budget.file), "utf-8");
  const lines = src.split("\n");
  const out = [];
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    if (!line.match(/^\s*tileLine:/)) continue;
    let candidate = line.replace(/^\s*tileLine:\s*/, "");
    if (candidate.startsWith('"')) {
      out.push({
        location: `${budget.file}:${i + 1}`,
        value: parseQuotedString(candidate),
      });
      continue;
    }
    let j = i + 1;
    while (j < lines.length && lines[j].trim() === "") j++;
    if (j < lines.length && lines[j].trim().startsWith('"')) {
      out.push({
        location: `${budget.file}:${j + 1}`,
        value: parseQuotedString(lines[j].trim()),
      });
    }
  }
  return out;
}

function extractHeroKickers(budget) {
  const src = readFileSync(resolve(ROOT, budget.file), "utf-8");
  const lines = src.split("\n");
  const out = [];
  for (let i = 0; i < lines.length; i++) {
    const m = lines[i].match(/^\s*heroKicker:\s*"([^"]*)"/);
    if (!m) continue;
    out.push({
      location: `${budget.file}:${i + 1}`,
      value: m[1],
    });
  }
  return out;
}

function extractPageDescriptions(budget) {
  const dirPath = resolve(ROOT, budget.file);
  const out = [];
  for (const filePath of walk(dirPath)) {
    if (!filePath.endsWith(".astro")) continue;
    if (filePath.includes("_experiments")) continue;
    if (filePath.includes("og-preview")) continue;
    const src = readFileSync(filePath, "utf-8");
    const m = src.match(/const\s+pageDescription\s*=\s*([\s\S]*?);\s*\n/);
    if (!m) continue;
    const segments = [...m[1].matchAll(/"((?:[^"\\]|\\.)*)"/g)].map(
      (mm) => mm[1].replace(/\\"/g, '"').replace(/\\n/g, "\n"),
    );
    const value = segments.join("");
    if (!value) continue;
    const relPath = filePath.slice(ROOT.length + 1).replace(/\\/g, "/");
    out.push({ location: relPath, value });
  }
  return out;
}

// ---- helpers --------------------------------------------------------------

function parseQuotedString(s) {
  const trimmed = s.replace(/,\s*$/, "").trim();
  if (trimmed.startsWith('"') && trimmed.endsWith('"')) {
    return trimmed.slice(1, -1).replace(/\\"/g, '"');
  }
  return trimmed;
}

function walk(dir) {
  const out = [];
  const entries = readdirSync(dir, { withFileTypes: true });
  for (const ent of entries) {
    const full = resolve(dir, ent.name);
    if (ent.isDirectory()) {
      out.push(...walk(full));
    } else {
      out.push(full);
    }
  }
  return out;
}
