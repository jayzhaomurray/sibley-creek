/**
 * check_prose_vintage.mjs -- site-wide guard against the markets-2026-06
 * failure class: hand-authored prose drifting weeks behind the data it
 * narrates ("oil still over $100" live at $92, blurb stamped May 13 against
 * June 9 charts).
 *
 * What it does
 * ------------
 * For every section in src/data/sections.ts that has a panel_data JSON:
 *   text vintage  = the section blurb's `date:` stamp (the hand-authored
 *                   prose vintage; updatedAt tracks data, not prose)
 *   data vintage  = max asOfISO across all slots in
 *                   data/site/panel_data/<slug>.json
 * WARN when data leads text by more than the threshold (default 35 days,
 * per-section overridable). Sections rendered mechanically (prose is a
 * function of the data, re-rendered every build) are exempt via config.
 *
 * Modes
 * -----
 * Default: warn-only, always exits 0 -- this gate must not break other
 * sections' builds on day one. `--strict`: exits 1 on any warning (future
 * tightening; also useful in a scheduled audit job).
 *
 * Wiring: npm run build (before astro check), warn-only.
 */

import { readFileSync, existsSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = join(__dirname, "..");
const SECTIONS_TS = join(ROOT, "src", "data", "sections.ts");
const PANEL_DATA_DIR = join(ROOT, "data", "site", "panel_data");

const STRICT = process.argv.includes("--strict");

// ---------------------------------------------------------------------------
// Config
// ---------------------------------------------------------------------------

const DEFAULT_MAX_LAG_DAYS = 35;

/**
 * Per-section overrides.
 *   mechanical: true   -- prose is rendered deterministically from panel
 *                         data at build time (src/lib/prose); the hand-
 *                         authored blurb stamp no longer governs the page
 *                         and this check does not apply. Add a section here
 *                         WHEN ITS PAGE IS CUT OVER, not before.
 *   maxLagDays: number -- looser/tighter threshold for slow-release
 *                         sections whose prose legitimately outlives the
 *                         default window.
 */
const SECTION_CONFIG = {
  // Cut over 2026-06-10: /markets/ prose renders from
  // editorial/prose_templates/markets.yaml on every build.
  markets: { mechanical: true },
};

// ---------------------------------------------------------------------------

function parseSections(srcText) {
  // Section blocks: from each `slug: "<x>"` to the next one. The blurb's
  // `date:` stamp is the first date field inside the block. Deep-dive
  // registry entries also match the slug pattern but have no panel_data
  // JSON, so they are skipped naturally at the lookup step.
  const out = [];
  const re = /slug:\s*"([^"]+)"/g;
  const hits = [];
  let m;
  while ((m = re.exec(srcText)) !== null) hits.push({ slug: m[1], index: m.index });
  for (let i = 0; i < hits.length; i++) {
    const block = srcText.slice(hits[i].index, hits[i + 1]?.index ?? srcText.length);
    const dateMatch = /date:\s*"([^"]+)"/.exec(block);
    out.push({ slug: hits[i].slug, blurbDate: dateMatch ? dateMatch[1] : null });
  }
  return out;
}

function maxAsOf(panelPath) {
  let payload;
  try {
    payload = JSON.parse(readFileSync(panelPath, "utf-8"));
  } catch {
    return null;
  }
  // Projection slots (policy-path scenarios, MPR paths) carry future-dated
  // asOfISO stamps; they say nothing about how fresh the OBSERVED data is.
  // Cap the data vintage at today.
  const todayISO = new Date().toISOString().slice(0, 10);
  let best = null;
  for (const p of Object.values(payload.panels ?? {})) {
    for (const slot of [p.primary, p.secondary, p.tertiary, ...(p.extras ?? [])]) {
      const v = slot?.asOfISO;
      if (typeof v === "string" && v.slice(0, 10) <= todayISO && (!best || v > best)) best = v;
    }
  }
  return best;
}

function daysBetween(fromMs, toMs) {
  return Math.floor((toMs - fromMs) / 86400000);
}

let warnings = 0;
let checked = 0;

const srcText = readFileSync(SECTIONS_TS, "utf-8");

for (const { slug, blurbDate } of parseSections(srcText)) {
  const cfg = SECTION_CONFIG[slug] ?? {};
  const panelPath = join(PANEL_DATA_DIR, `${slug}.json`);
  if (!existsSync(panelPath)) continue; // deep-dive entries, future sections
  checked++;

  if (cfg.mechanical) {
    console.log(`[check_prose_vintage] ${slug}: mechanical prose, exempt.`);
    continue;
  }
  if (!blurbDate || blurbDate === "TK") {
    console.warn(`  WARN: ${slug}: no parseable blurb date stamp in sections.ts`);
    warnings++;
    continue;
  }
  // Force UTC parsing -- bare `Date.parse(blurbDate)` on a non-ISO string
  // like "Jul 15, 2026" uses the LOCAL system timezone, while dataISO below
  // (ISO date-only) always parses as UTC. That mismatch made the day-lag
  // computation timezone-dependent: a build machine west of UTC could
  // compute one fewer day of lag than a UTC CI runner, silently masking a
  // --strict failure in local dev while it hard-fails in CI.
  const textMs = Date.parse(`${blurbDate} UTC`);
  if (Number.isNaN(textMs)) {
    console.warn(`  WARN: ${slug}: unparseable blurb date "${blurbDate}"`);
    warnings++;
    continue;
  }
  const dataISO = maxAsOf(panelPath);
  if (!dataISO) continue;
  const dataMs = Date.parse(dataISO.slice(0, 10));

  const lag = daysBetween(textMs, dataMs);
  const threshold = cfg.maxLagDays ?? DEFAULT_MAX_LAG_DAYS;
  if (lag > threshold) {
    console.warn(
      `  WARN: ${slug}: hand-authored prose dated "${blurbDate}" lags panel data ` +
      `(asOf ${dataISO.slice(0, 10)}) by ${lag} days (threshold ${threshold}d). ` +
      `The blurb may assert claims the charts no longer show -- refresh the prose ` +
      `or cut the section over to mechanical rendering.`
    );
    warnings++;
  }
}

if (warnings > 0 && STRICT) {
  console.error(`[check_prose_vintage] FAIL (--strict): ${warnings} stale-prose warning(s).`);
  process.exit(1);
}
console.log(
  `[check_prose_vintage] ${warnings > 0 ? `${warnings} warning(s), ` : "OK: "}` +
  `${checked} section(s) checked${STRICT ? " (strict)" : ""}.`
);
