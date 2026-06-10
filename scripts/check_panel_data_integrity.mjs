/**
 * check_panel_data_integrity.mjs
 *
 * Pre-build guard: scan every data/site/panel_data/<section>.json and
 * data/site/sections.json for data quality violations that would produce
 * broken charts on the live site.
 *
 * What it catches
 * ---------------
 * 1. INVALID JSON -- NaN and Infinity are not valid JSON; json.dumps()
 *    silently emits them from Python float('inf') / float('nan') when
 *    pd.isna() is not checked for Infinity. JSON.parse() in the browser
 *    throws or returns undefined, producing blank charts. This is the
 *    primary confirmed root cause of the recurring broken-chart bug.
 *
 * 2. NaN / Infinity literals inside parsed data -- if the JSON somehow
 *    parses (some parsers are lenient), we catch Infinity/NaN values in
 *    numeric fields.
 *
 * 3. Null values inside data records for "value" field -- a null in the
 *    value column is allowed for historical suppression (StatCan uses this
 *    for LFS sub-provincial data, job vacancy pre-2020, etc.), but a null
 *    for the MOST RECENT data point is a staleness signal and fails.
 *
 * 4. Staleness -- a series whose most recent date is older than the allowed
 *    threshold for its cadence. Daily market/yield series fail closed; slower
 *    release-lag series warn unless explicitly promoted to fail-closed.
 *
 * 5. Sane value ranges -- catches obvious pipeline corruptions (yield of 999%,
 *    TSX of 0, USDCAD of 10). Wide ranges that only fire on egregious errors.
 *
 * 6. Meta-fallback signatures (added 2026-06-09, markets audit F4/item 9) --
 *    a raw- or processed-tier slot with source: null means panel regen could
 *    not read the .meta.json sidecar; in that state frequency also fell back
 *    to "monthly", which silently swapped a daily series onto the 105-day
 *    monthly staleness threshold (the gate was structurally blind to daily
 *    staleness). Two hard failures close this class: null source on a
 *    raw/processed slot, and any series in the fail-closed daily set
 *    reporting a frequency other than "daily". With the frequency correct,
 *    the existing 3-business-day daily threshold binds.
 *
 * Wiring
 * ------
 * Added to npm run build BEFORE astro check && astro build, so bad data fails
 * the build before the heavy TypeScript/Astro compile. Also runs in
 * build-financial-daily.yml and build-data-daily.yml after the pipeline
 * writes panel_data (via the pipeline's own validate_panel_data_file() call).
 *
 * Root cause context
 * ------------------
 * Investigated 2026-06-01. The recurrence mechanism: _df_to_records() in
 * pipeline/io/panel_data.py used pd.isna() to filter NaN but pd.isna(float('inf'))
 * returns False, so Infinity passed through into the JSON output.
 * json.dumps() serializes Python float('inf') as the string "Infinity" which
 * is not valid JSON. See claude-ref/research/data_integrity/root_cause_2026-06-01.md.
 */

import { readFileSync, readdirSync, existsSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = join(__dirname, "..");
const PANEL_DATA_DIR = join(ROOT, "data", "site", "panel_data");
const SECTIONS_JSON = join(ROOT, "data", "site", "sections.json");

// Fail-closed on staleness for series whose scheduled refresh cadence is daily.
// Slower macro releases keep warning-only thresholds unless explicitly listed
// here; their asOfISO is the reference period, not the publication date.
const FAIL_ON_STALE = true;

const STALENESS_FAIL_SERIES = new Set([
  "yield_2yr",
  "yield_5yr",
  "yield_10yr",
  "yield_30yr",
  "overnight_rate_daily",
  "fxusdcad",
  "tsx_composite",
  "wti",
  "brent",
  "us_2yr",
  "us_10yr",
  "goc_ust_spread_2y",
  "goc_ust_spread_10y",
  "corra_overnight_spread_bps",
]);

// Per-series sane-value ranges. Catches obvious corruptions.
// Format: seriesKey -> [min, max]
const SANE_RANGES = {
  yield_2yr:  [0, 25],
  yield_5yr:  [0, 25],
  yield_10yr: [0, 25],
  yield_30yr: [0, 25],
  overnight_rate:       [0, 25],
  overnight_rate_daily: [0, 25],
  cpi_all_items:     [90, 250],
  cpi_all_items_nsa: [90, 250],
  fxusdcad:     [0.5, 2.5],
  tsx_composite: [1000, 200000],
  wti:           [0, 500],
  unemployment_rate: [0, 30],
  employment_level:  [5, 30],
  goc_ust_spread_2y:  [-10, 10],
  goc_ust_spread_10y: [-10, 10],
  boc_fed_spread_monthly: [-500, 500],
  corra_overnight_spread_bps: [-100, 100],
};

// Staleness thresholds by series frequency. Daily is business days; other
// cadences are calendar days because their asOfISO marks a reference period.
const FRESHNESS_DAYS = {
  daily:     3,    // North American market business days
  weekly:    21,   // 3 weeks
  monthly:   105,  // reference-month stamps can run ~60d after month-end
  quarterly: 220,  // reference-quarter stamps can run ~90d after quarter-end
  annual:    400,
  irregular: 400,
};

// Per-series staleness overrides for sources with atypical publication lags.
// Must stay in sync with SERIES_STALENESS_OVERRIDES in pipeline/io/panel_data.py.
const SERIES_STALENESS_OVERRIDES = {
  // StatCan bilateral trade (Table 12-10-0011-01): ~90-day lag
  trade_exports_us_customs: 120, trade_imports_us_customs: 120,
  trade_exports_all_customs: 120, trade_imports_all_customs: 120,
  trade_exports_chn: 120, trade_imports_chn: 120,
  trade_exports_gbr: 120, trade_imports_gbr: 120,
  trade_exports_deu: 120, trade_imports_deu: 120,
  trade_exports_fra: 120, trade_imports_fra: 120,
  trade_exports_nld: 120, trade_imports_nld: 120,
  trade_exports_jpn: 120, trade_imports_jpn: 120,
  trade_exports_mex: 120, trade_imports_mex: 120,
  trade_exports_kor: 120, trade_imports_kor: 120,
  trade_exports_ind: 120, trade_imports_ind: 120,
  trade_exports_aus: 120, trade_imports_aus: 120,
  trade_exports_idn: 120, trade_imports_idn: 120,
  trade_exports_sgp: 120, trade_imports_sgp: 120,
  trade_exports_sau: 120, trade_imports_sau: 120,
  trade_exports_twn: 120, trade_imports_twn: 120,
  trade_exports_hkg: 120, trade_imports_hkg: 120,
  // StatCan sectoral/gold exports (Table 12-10-0182-01): ~90-day lag
  exports_steel_us: 120, exports_steel_nonus: 120,
  exports_aluminum_us: 120, exports_aluminum_nonus: 120,
  exports_softwood_us: 120, exports_softwood_nonus: 120,
  exports_autos_us: 120, exports_autos_nonus: 120,
  exports_gold_total: 120, exports_gold_uk: 120, exports_gold_us: 120,
  // CREA HPI: ~30-35 days after reference month; resales by CMA can be much longer
  crea_hpi_canada_yoy: 70, crea_hpi_toronto_yoy: 70,
  crea_hpi_vancouver_yoy: 70, crea_hpi_montreal_yoy: 70,
  crea_hpi_calgary_yoy: 70, crea_hpi_ottawa_yoy: 70, crea_hpi_edmonton_yoy: 70,
  crea_snlr: 150, crea_resales: 150,
  crea_resales_toronto: 300, crea_resales_vancouver: 300, crea_resales_calgary: 300,
  // CBA mortgage arrears: ~75-day lag
  cba_mortgage_arrears_national: 100,
  // DoF Fiscal Monitor: ~60-120 days
  dof_fiscal_monthly_balance: 120, dof_fiscal_ytd_balance: 120, dof_fiscal_ytd_summary: 120,
  debt_service_ratio: 120, debt_service_ratio_band_lo: 120, debt_service_ratio_band_hi: 120,
  // IMF WEO: annual
  imf_can_gg_balance_pct_gdp: 400, imf_can_gg_gross_debt_pct_gdp: 400,
  // BoC balance sheet: weekly, 1-2 week lag
  boc_settlement_balances: 21, boc_total_assets: 21, boc_total_liabilities: 21,
  boc_goc_bonds: 21, boc_tbills: 21, boc_advances: 21,
  boc_repos: 21, boc_reverse_repos: 21, boc_banknotes: 21, boc_goc_deposits: 21,
  // BoC output gap: quarterly MPR vintage; can lag when an MPR does not refresh it
  output_gap_mpr: 270,
  // JVWS: ~75-day lag
  job_vacancy_rate: 90, job_vacancy_level: 90,
  // Housing starts/permits: monthly, ~35-60 day lag for starts, longer for permits
  housing_starts: 75, units_under_construction: 75, residential_permits: 120,
  // Household DSR: quarterly, published with long lag
  household_dsr: 270,
  // BoC housing affordability: quarterly, published with long lag
  housing_affordability: 270,
  // AECO natural gas: monthly, ~60-day lag
  natural_gas_alberta: 120,
  // BoC-Fed spread: derived, same lag as overnight rate
  boc_fed_spread_monthly: 75,
  // Trade exports total/US (BOP basis): ~90-day lag
  trade_exports_total: 120, trade_exports_us: 120,
  // GoC-UST spreads (derived, limited by FRED availability)
  goc_ust_spread_2y: 10, goc_ust_spread_10y: 10,
};

const SECTION_PRINT_SERIES = {
  "goc-2y": "yield_2yr",
  "boc-fed-spread": "goc_ust_spread_2y",
  "usdcad": "fxusdcad",
  "goc-10y": "yield_10yr",
  "tsx-composite": "tsx_composite",
  "wti": "wti",
};

// Sane-range check for sections.json print valueRaw values.
// Maps print keys (hyphenated dashboard convention) to [min, max] pairs.
// Values are sourced from the same thresholds as SANE_RANGES above — do NOT
// change one without changing the other. Print keys not listed here skip the
// range check (the panel_data gate catches corruption in the underlying series).
const SECTION_PRINT_SANE_RANGES = {
  // Bond yields (%)
  "goc-2y":       [0, 25],
  "goc-10y":      [0, 25],
  "policy-rate":  [0, 25],
  // FX
  "usdcad":       [0.5, 2.5],
  // Equity
  "tsx-composite": [1000, 200000],
  // Commodities
  "wti":          [0, 500],
  // Unemployment (%)
  "unrate":       [0, 30],
  // GoC-UST spreads (bps as stored in sections.json for boc-fed-spread)
  // Note: boc-fed-spread is stored in bps (-500 to +500); goc-2y/goc-10y above cover %-point spreads
  "boc-fed-spread": [-500, 500],
};

const today = new Date();
today.setHours(0, 0, 0, 0);

function daysSince(dateStr) {
  if (!dateStr) return null;
  const d = new Date(dateStr.slice(0, 10));
  if (isNaN(d.getTime())) return null;
  return Math.floor((today - d) / 86400000);
}

const HOLIDAY_CACHE = new Map();

function dateKey(d) {
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return `${y}-${m}-${day}`;
}

function addDays(d, days) {
  const out = new Date(d);
  out.setDate(out.getDate() + days);
  return out;
}

function observedFixedHoliday(year, monthIndex, day) {
  const d = new Date(year, monthIndex, day);
  if (d.getDay() === 6) return addDays(d, -1);
  if (d.getDay() === 0) return addDays(d, 1);
  return d;
}

function nthWeekdayOfMonth(year, monthIndex, weekday, n) {
  const d = new Date(year, monthIndex, 1);
  const offset = (weekday - d.getDay() + 7) % 7;
  d.setDate(1 + offset + ((n - 1) * 7));
  return d;
}

function lastWeekdayOfMonth(year, monthIndex, weekday) {
  const d = new Date(year, monthIndex + 1, 0);
  const offset = (d.getDay() - weekday + 7) % 7;
  d.setDate(d.getDate() - offset);
  return d;
}

function easterDate(year) {
  const a = year % 19;
  const b = Math.floor(year / 100);
  const c = year % 100;
  const d = Math.floor(b / 4);
  const e = b % 4;
  const f = Math.floor((b + 8) / 25);
  const g = Math.floor((b - f + 1) / 3);
  const h = ((19 * a) + b - d - g + 15) % 30;
  const i = Math.floor(c / 4);
  const k = c % 4;
  const l = (32 + (2 * e) + (2 * i) - h - k) % 7;
  const m = Math.floor((a + (11 * h) + (22 * l)) / 451);
  const month = Math.floor((h + l - (7 * m) + 114) / 31);
  const day = ((h + l - (7 * m) + 114) % 31) + 1;
  return new Date(year, month - 1, day);
}

function marketHolidaySet(year) {
  if (HOLIDAY_CACHE.has(year)) return HOLIDAY_CACHE.get(year);
  const holidays = [
    observedFixedHoliday(year, 0, 1),        // New Year's Day
    nthWeekdayOfMonth(year, 0, 1, 3),        // MLK Day
    nthWeekdayOfMonth(year, 1, 1, 3),        // Family Day / Presidents' Day
    addDays(easterDate(year), -2),           // Good Friday
    lastWeekdayOfMonth(year, 4, 1),          // US Memorial Day
    nthWeekdayOfMonth(year, 4, 1, 3),        // Victoria Day
    observedFixedHoliday(year, 5, 19),       // Juneteenth
    observedFixedHoliday(year, 6, 1),        // Canada Day
    observedFixedHoliday(year, 6, 4),        // US Independence Day
    nthWeekdayOfMonth(year, 7, 1, 1),        // Civic Holiday
    nthWeekdayOfMonth(year, 8, 1, 1),        // Labour Day
    observedFixedHoliday(year, 8, 30),       // Truth and Reconciliation Day
    nthWeekdayOfMonth(year, 9, 1, 2),        // Canadian Thanksgiving / US Columbus Day
    observedFixedHoliday(year, 10, 11),      // Remembrance Day / US Veterans Day
    nthWeekdayOfMonth(year, 10, 4, 4),       // US Thanksgiving
    observedFixedHoliday(year, 11, 25),      // Christmas Day
    observedFixedHoliday(year, 11, 26),      // Boxing Day
  ];
  const set = new Set(holidays.map(dateKey));
  HOLIDAY_CACHE.set(year, set);
  return set;
}

function isMarketHoliday(d) {
  const key = dateKey(d);
  const year = d.getFullYear();
  return marketHolidaySet(year - 1).has(key) ||
    marketHolidaySet(year).has(key) ||
    marketHolidaySet(year + 1).has(key);
}

function isBusinessDay(d) {
  const day = d.getDay();
  return day !== 0 && day !== 6 && !isMarketHoliday(d);
}

function businessDaysSince(dateStr) {
  if (!dateStr) return null;
  const start = new Date(dateStr.slice(0, 10));
  if (isNaN(start.getTime())) return null;
  start.setHours(0, 0, 0, 0);
  let count = 0;
  for (const d = new Date(start); d < today; d.setDate(d.getDate() + 1)) {
    if (d.getTime() === start.getTime()) continue;
    if (isBusinessDay(d)) count += 1;
  }
  return count;
}

function ageForCadence(dateStr, freq) {
  return freq === "daily" ? businessDaysSince(dateStr) : daysSince(dateStr);
}

function shouldFailStaleness(key) {
  return FAIL_ON_STALE && STALENESS_FAIL_SERIES.has(key);
}

// --------------------------------------------------------------------------- #
// Per-slot checker
// --------------------------------------------------------------------------- #

function checkSlot(slot, { section, panelId, slotName, violations, warnings }) {
  if (!slot || !Array.isArray(slot.data) || slot.data.length === 0) return;

  const key = slot.key || "?";
  const freq = (slot.frequency || "monthly").toLowerCase();
  const maxAge = SERIES_STALENESS_OVERRIDES[key] ?? (FRESHNESS_DAYS[freq] ?? 400);
  const sane = SANE_RANGES[key];

  // Meta-fallback signatures (see header item 6). A raw/processed-tier slot
  // always gets its source from the .meta.json sidecar; null means the
  // sidecar was missing/unreadable at regen time and the frequency tag on
  // this slot is a fallback, not a fact.
  if ((slot.tier === "raw" || slot.tier === "processed") && !slot.source) {
    violations.push(
      `${section}/${panelId}/${slotName}/${key}: source is null on a ${slot.tier}-tier slot ` +
      `(.meta.json sidecar missing at panel regen; frequency tag untrustworthy -- ` +
      `run check_raw_tracked.mjs and git add -f the meta sibling)`
    );
  }
  if (STALENESS_FAIL_SERIES.has(key) && freq !== "daily") {
    violations.push(
      `${section}/${panelId}/${slotName}/${key}: frequency="${freq}" but this series is daily ` +
      `(meta-fallback signature; the ${FRESHNESS_DAYS[freq] ?? 400}d ${freq} staleness ` +
      `threshold would never trip for a stale daily series)`
    );
  }

  // Check each record
  for (let i = 0; i < slot.data.length; i++) {
    const record = slot.data[i];
    for (const [field, val] of Object.entries(record)) {
      if (field === "date") continue;
      if (val === null || val === undefined) continue;
      if (typeof val !== "number") continue;

      if (!isFinite(val) || isNaN(val)) {
        violations.push(
          `${section}/${panelId}/${slotName}/${key}: record[${i}].${field} = ${val} (NaN or Infinity)`
        );
        continue;
      }

      if (field === "value" && sane) {
        const [lo, hi] = sane;
        if (val < lo || val > hi) {
          violations.push(
            `${section}/${panelId}/${slotName}/${key}: ` +
            `record[${i}].value=${val} outside sane range [${lo}, ${hi}]`
          );
        }
      }
    }
  }

  // Check for trailing null (last value is null = likely stale fetch)
  const lastRecord = slot.data[slot.data.length - 1];
  if (lastRecord && lastRecord.value === null) {
    violations.push(
      `${section}/${panelId}/${slotName}/${key}: most recent data point has null value (possible stale fetch)`
    );
  }

  // Staleness check
  const age = ageForCadence(slot.asOfISO, freq);
  if (age !== null && age > maxAge) {
    const msg =
      `${section}/${panelId}/${slotName}/${key}: ` +
      `asOfISO=${slot.asOfISO} is ${age}${freq === "daily" ? " business " : ""}d old ` +
      `(threshold ${maxAge}d for ${freq})`;
    if (shouldFailStaleness(key)) {
      violations.push(msg);
    } else {
      warnings.push(msg);
    }
  }
}

function checkFiniteNumber(value, path, violations) {
  if (typeof value !== "number") return;
  if (!Number.isFinite(value) || Number.isNaN(value)) {
    violations.push(`${path} = ${value} (NaN or Infinity)`);
  }
}

function checkSectionsPayload(payload) {
  const violations = [];
  const warnings = [];
  for (const [section, sectionPayload] of Object.entries(payload.sections ?? {})) {
    const prints = Array.isArray(sectionPayload.prints) ? sectionPayload.prints : [];
    for (const print of prints) {
      const printKey = print.key || "?";
      checkFiniteNumber(print.valueRaw, `sections/${section}/${printKey}.valueRaw`, violations);
      checkFiniteNumber(print.priorRaw, `sections/${section}/${printKey}.priorRaw`, violations);
      if (Array.isArray(print.spark)) {
        for (let i = 0; i < print.spark.length; i++) {
          checkFiniteNumber(print.spark[i], `sections/${section}/${printKey}.spark[${i}]`, violations);
        }
      }

      // Sane-range check on valueRaw — catches finite-but-absurd values that
      // the NaN/Infinity check above cannot see (e.g. TSX print = 0).
      const printRange = SECTION_PRINT_SANE_RANGES[printKey];
      if (printRange && typeof print.valueRaw === "number" && Number.isFinite(print.valueRaw)) {
        const [lo, hi] = printRange;
        if (print.valueRaw < lo || print.valueRaw > hi) {
          violations.push(
            `sections/${section}/${printKey}.valueRaw=${print.valueRaw} ` +
            `outside sane range [${lo}, ${hi}]`
          );
        }
      }

      const mappedSeries = SECTION_PRINT_SERIES[printKey];
      if (!mappedSeries) continue;
      const freq = "daily";
      const maxAge = SERIES_STALENESS_OVERRIDES[mappedSeries] ?? FRESHNESS_DAYS[freq];
      const age = ageForCadence(print.asOfISO, freq);
      if (age !== null && age > maxAge) {
        const msg =
          `sections/${section}/${printKey}/${mappedSeries}: ` +
          `asOfISO=${print.asOfISO} is ${age} business days old (threshold ${maxAge}d)`;
        if (shouldFailStaleness(mappedSeries)) {
          violations.push(msg);
        } else {
          warnings.push(msg);
        }
      }
    }
  }
  return { violations, warnings };
}

// --------------------------------------------------------------------------- #
// File scanner
// --------------------------------------------------------------------------- #

function checkPanelDataFile(filePath) {
  const section = filePath.replace(/.*panel_data[/\\]/, "").replace(".json", "");
  let payload;

  // Step 1: Try to parse as JSON. NaN/Infinity in the file makes JSON.parse throw.
  let rawText;
  try {
    rawText = readFileSync(filePath, "utf-8");
  } catch (e) {
    return { section, violations: [`${section}.json: could not read file: ${e.message}`], warnings: [] };
  }

  try {
    payload = JSON.parse(rawText);
  } catch (e) {
    // Diagnose: does the file contain the literal strings NaN or Infinity?
    const hasNaN = rawText.includes(": NaN") || rawText.includes(":NaN");
    const hasInf = rawText.includes(": Infinity") || rawText.includes(":Infinity") ||
                   rawText.includes(": -Infinity") || rawText.includes(":-Infinity");
    const detail = hasNaN
      ? " (file contains 'NaN' literals -- Python float NaN emitted by _df_to_records)"
      : hasInf
      ? " (file contains 'Infinity' literals -- Python float Infinity emitted by _df_to_records)"
      : "";
    return {
      section,
      violations: [`${section}.json: invalid JSON -- JSON.parse() failed: ${e.message}${detail}`],
      warnings: [],
    };
  }

  const violations = [];
  const warnings = [];

  for (const [panelId, panel] of Object.entries(payload.panels ?? {})) {
    for (const slotName of ["primary", "secondary", "tertiary"]) {
      checkSlot(panel[slotName], { section, panelId, slotName, violations, warnings });
    }
    for (const extra of panel.extras ?? []) {
      checkSlot(extra, { section, panelId, slotName: "extra", violations, warnings });
    }
    // Co-dated alignment signal (WARN, never fail): panel_data.py trimmed a
    // group of single-snapshot series (e.g. the GoC curve maturities) to their
    // common latest date because the source published them mis-dated. Benign
    // when transient (one-day Valet lag); investigate if it persists.
    const coDated = panel.coDatedAlignment;
    if (coDated && Object.keys(coDated.trimmedFrom ?? {}).length > 0) {
      const trims = Object.entries(coDated.trimmedFrom)
        .map(([k, d]) => `${k} (had ${d})`).join(", ");
      warnings.push(
        `${section}/${panelId}: co-dated alignment trimmed ${trims} to common date ` +
        `${coDated.alignedTo} -- upstream published the group mis-dated; benign if ` +
        `transient, investigate if persistent`
      );
    }
  }

  return { section, violations, warnings };
}

// --------------------------------------------------------------------------- #
// Main
// --------------------------------------------------------------------------- #

let totalViolations = 0;
let totalWarnings = 0;
const checkedFiles = [];

// Check all panel_data/*.json files
if (existsSync(PANEL_DATA_DIR)) {
  for (const fname of readdirSync(PANEL_DATA_DIR)) {
    if (!fname.endsWith(".json")) continue;
    const fullPath = join(PANEL_DATA_DIR, fname);
    const { section, violations, warnings } = checkPanelDataFile(fullPath);
    checkedFiles.push(fname);

    if (violations.length > 0) {
      console.error(`\n[check_panel_data_integrity] VIOLATIONS in ${fname}:`);
      for (const v of violations) {
        console.error(`  ERROR: ${v}`);
      }
      totalViolations += violations.length;
    }

    if (warnings.length > 0) {
      for (const w of warnings) {
        console.warn(`  WARN: ${w}`);
      }
      totalWarnings += warnings.length;
    }
  }
} else {
  console.error(`[check_panel_data_integrity] FAIL: panel_data directory not found: ${PANEL_DATA_DIR}`);
  process.exit(1);
}

// Check sections.json for NaN/Infinity (it embeds sparkline data)
if (existsSync(SECTIONS_JSON)) {
  checkedFiles.push("sections.json");
  try {
    const raw = readFileSync(SECTIONS_JSON, "utf-8");
    const payload = JSON.parse(raw); // throws if invalid
    const { violations, warnings } = checkSectionsPayload(payload);
    if (violations.length > 0) {
      console.error(`\n[check_panel_data_integrity] VIOLATIONS in sections.json:`);
      for (const v of violations) {
        console.error(`  ERROR: ${v}`);
      }
      totalViolations += violations.length;
    }
    if (warnings.length > 0) {
      for (const w of warnings) {
        console.warn(`  WARN: ${w}`);
      }
      totalWarnings += warnings.length;
    }
  } catch (e) {
    const raw = readFileSync(SECTIONS_JSON, "utf-8");
    const hasNaN = raw.includes(": NaN") || raw.includes(":NaN");
    const hasInf = raw.includes("Infinity");
    const detail = hasNaN ? " (contains NaN)" : hasInf ? " (contains Infinity)" : "";
    console.error(`\n[check_panel_data_integrity] VIOLATION in sections.json: invalid JSON${detail} -- ${e.message}`);
    totalViolations++;
  }
}

if (totalViolations > 0) {
  console.error(
    `\n[check_panel_data_integrity] FAIL: ${totalViolations} violation(s) in ${checkedFiles.length} file(s).`
  );
  console.error(
    "Root-cause checklist:\n" +
    "  1. pipeline/io/panel_data.py _df_to_records() emitted Infinity -- check math.isinf() guard\n" +
    "  2. A transform (pct_change / annualize) produced Infinity from a zero denominator\n" +
    "  3. A CSV on disk contains Infinity or NaN values from an upstream API error\n" +
    "  4. See claude-ref/research/data_integrity/root_cause_2026-06-01.md for full diagnosis\n" +
    "Fix: py -m pipeline.io.panel_data to regenerate, then re-run this check."
  );
  process.exit(1);
}

const warnSuffix = totalWarnings > 0 ? ` (${totalWarnings} staleness warning(s))` : "";
console.log(
  `[check_panel_data_integrity] OK: ${checkedFiles.length} file(s) passed integrity check${warnSuffix}.`
);
