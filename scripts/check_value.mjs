#!/usr/bin/env node
/*
 * check_value.mjs — chat-time pipeline lookup for user-instructed prose.
 *
 * When the user gives an instruction like "change UR to 7.0%", invoke this
 * before writing to verify the value against the section's pipeline data.
 * If a match exists, the user's value is likely right. If a near-miss
 * exists (e.g., pipeline has 6.9% in the same indicator slot), surface the
 * mismatch so the user can correct or override.
 *
 * Usage:
 *   node scripts/check_value.mjs --section <slug> --value <n>[unit] [--indicator <hint>]
 *
 * Examples:
 *   node scripts/check_value.mjs --section labour --value 6.9
 *   node scripts/check_value.mjs --section gdp --value 1.2 --indicator potential
 *   node scripts/check_value.mjs --section inflation --value 2.3%
 *
 * Output:
 *   MATCH:   series_key=<key>, latest=<value>, asOf=<date>
 *   NEAR:    closest pipeline value within 0.5 of input — flagged as potential typo
 *   NO-MATCH: value does not appear anywhere in the section's pipeline data
 *
 * This is a behavioral hint, not a hard gate. Use the output to decide
 * whether to write the user's value as-stated, challenge them in chat, or
 * surface a different source.
 */

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const repoRoot = path.resolve(__dirname, "..");

function parseArgs(argv) {
  const out = { section: null, value: null, indicator: null };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === "--section") out.section = argv[++i];
    else if (a === "--value") out.value = argv[++i];
    else if (a === "--indicator") out.indicator = argv[++i];
  }
  return out;
}

function parseValue(raw) {
  // Accept forms: 6.9, 6.9%, -98 bps, $25.5bn, 282k
  if (!raw) return null;
  const m = raw.match(/^(-?\d+(?:\.\d+)?)/);
  if (!m) return null;
  return parseFloat(m[1]);
}

function flattenSeries(panelData) {
  // Returns [{key, label, source, latestValue, latestDate, allValues:[]}]
  const out = [];
  if (!panelData || !panelData.panels) return out;
  for (const [panelKey, panel] of Object.entries(panelData.panels)) {
    for (const slotName of ["primary", "secondary", "tertiary"]) {
      const slot = panel[slotName];
      if (slot && Array.isArray(slot.data)) {
        const realPts = slot.data.filter((p) => typeof p.value === "number");
        const last = realPts.length > 0 ? realPts[realPts.length - 1] : null;
        out.push({
          panel: panelKey,
          slot: slotName,
          key: slot.key,
          label: slot.label,
          latestValue: last?.value ?? null,
          latestDate: last?.date ?? null,
          allValues: realPts.map((p) => p.value),
        });
      }
    }
    if (Array.isArray(panel.extras)) {
      for (const ex of panel.extras) {
        if (ex && Array.isArray(ex.data)) {
          const realPts = ex.data.filter((p) => typeof p.value === "number");
          const last = realPts.length > 0 ? realPts[realPts.length - 1] : null;
          out.push({
            panel: panelKey,
            slot: "extras",
            key: ex.key,
            label: ex.label,
            latestValue: last?.value ?? null,
            latestDate: last?.date ?? null,
            allValues: realPts.map((p) => p.value),
          });
        }
      }
    }
  }
  return out;
}

function main() {
  const args = parseArgs(process.argv.slice(2));
  if (!args.section || args.value === null) {
    console.error("usage: check_value.mjs --section <slug> --value <n>[unit] [--indicator <hint>]");
    process.exit(2);
  }
  const target = parseValue(args.value);
  if (target === null || Number.isNaN(target)) {
    console.error(`could not parse --value ${args.value}`);
    process.exit(2);
  }

  const panelDataPath = path.join(repoRoot, "data", "site", "panel_data", `${args.section}.json`);
  if (!fs.existsSync(panelDataPath)) {
    console.error(`no panel_data for section "${args.section}" at ${panelDataPath}`);
    process.exit(2);
  }
  const panelData = JSON.parse(fs.readFileSync(panelDataPath, "utf-8"));
  const series = flattenSeries(panelData);

  const indicatorFilter = (args.indicator || "").toLowerCase();
  const candidates = indicatorFilter
    ? series.filter(
        (s) =>
          (s.key || "").toLowerCase().includes(indicatorFilter) ||
          (s.label || "").toLowerCase().includes(indicatorFilter),
      )
    : series;

  // MATCH: any latestValue within 0.05 of target
  const exact = candidates.filter(
    (s) => s.latestValue !== null && Math.abs(s.latestValue - target) < 0.05,
  );
  if (exact.length > 0) {
    console.log(`MATCH for ${args.value} in ${args.section}:`);
    for (const e of exact) {
      console.log(
        `  ${e.key}  "${e.label}"  latest=${e.latestValue}  asOf=${e.latestDate}  (panel ${e.panel}/${e.slot})`,
      );
    }
    process.exit(0);
  }

  // NEAR: any latestValue within 0.5 of target (potential typo)
  const near = candidates
    .filter(
      (s) => s.latestValue !== null && Math.abs(s.latestValue - target) <= 0.5,
    )
    .sort((a, b) => Math.abs(a.latestValue - target) - Math.abs(b.latestValue - target));
  if (near.length > 0) {
    console.log(`NEAR-MISS for ${args.value} in ${args.section} — possible typo:`);
    for (const n of near.slice(0, 5)) {
      console.log(
        `  ${n.key}  "${n.label}"  latest=${n.latestValue}  asOf=${n.latestDate}  diff=${(n.latestValue - target).toFixed(2)}`,
      );
    }
    process.exit(1);
  }

  // Last resort: check whole historical series for any match
  const histMatch = candidates.filter((s) =>
    s.allValues.some((v) => Math.abs(v - target) < 0.05),
  );
  if (histMatch.length > 0) {
    console.log(`HISTORICAL MATCH for ${args.value} in ${args.section} (not the latest print):`);
    for (const h of histMatch.slice(0, 5)) {
      console.log(
        `  ${h.key}  "${h.label}"  latest=${h.latestValue}  asOf=${h.latestDate}  (value appears earlier in series)`,
      );
    }
    process.exit(1);
  }

  console.log(`NO-MATCH for ${args.value} in ${args.section} pipeline data.`);
  console.log(
    `Could be: an opinion / forecast / external source not piped in / typo.`,
  );
  console.log(
    `Inspected ${series.length} series across ${Object.keys(panelData.panels || {}).length} panels.`,
  );
  process.exit(1);
}

main();
