/**
 * generate_two_quarter_rule_chart.mjs
 *
 * Standalone generator for work/charts/two_quarter_rule_gdp.svg and .png.
 * NOT wired into the Astro build. Run directly:
 *   node scripts/generate_two_quarter_rule_chart.mjs
 *
 * Spec: design brief "Two-Quarter Rule GDP chart", 2026-06-01.
 * Canvas: 720x405, Vignelli v1.0 canon.
 */

import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, "..");

// ---------------------------------------------------------------------------
// 1. Load and process CSV
// ---------------------------------------------------------------------------

const csvText = fs.readFileSync(
  path.join(ROOT, "data/raw/gdp_quarterly.csv"),
  "utf8"
);
const csvRows = csvText
  .trim()
  .split("\n")
  .slice(1)
  .map((line) => {
    const [date, value] = line.split(",");
    return { date: date.trim(), value: parseFloat(value) };
  });

// Compute q/q % growth; first bar = index 1 (1961Q2)
const growths = [];
for (let i = 1; i < csvRows.length; i++) {
  const g = ((csvRows[i].value / csvRows[i - 1].value) - 1) * 100;
  growths.push({ date: csvRows[i].date, growth: g });
}

// ---------------------------------------------------------------------------
// 2. Verify trigger quarters against brief specification
// ---------------------------------------------------------------------------
// Brief specifies 8 trigger dates (second consecutive-negative quarter of run):
const BRIEF_TRIGGERS = new Set([
  "1975-01-01", // 1975Q1 — TRUE CATCH
  "1980-07-01", // 1980Q3 — FALSE ALARM
  "1981-10-01", // 1981Q4 — TRUE CATCH
  "1990-07-01", // 1990Q3 — TRUE CATCH
  "2009-01-01", // 2009Q1 — TRUE CATCH
  "2015-04-01", // 2015Q2 — FALSE ALARM
  "2020-04-01", // 2020Q2 — TRUE CATCH
  "2026-01-01", // 2026Q1 — FALSE ALARM
]);

const TRUE_CATCHES = new Set([
  "1975-01-01",
  "1981-10-01",
  "1990-07-01",
  "2009-01-01",
  "2020-04-01",
]);
const FALSE_ALARMS = new Set([
  "1980-07-01",
  "2015-04-01",
  "2026-01-01",
]);

// Derive triggers from computation and cross-check
const computedTriggers = new Set();
for (let i = 1; i < growths.length; i++) {
  if (growths[i - 1].growth < 0 && growths[i].growth < 0) {
    const prevNeg = i >= 2 && growths[i - 2].growth < 0;
    if (!prevNeg) {
      // Mark the SECOND quarter (confirming quarter), consistent with brief
      computedTriggers.add(growths[i].date);
    }
  }
}

const computedDates = [...computedTriggers].sort();
const briefDates = [...BRIEF_TRIGGERS].sort();
const mismatch = computedDates.filter((d) => !BRIEF_TRIGGERS.has(d));
const missing = briefDates.filter((d) => !computedTriggers.has(d));

if (mismatch.length > 0 || missing.length > 0) {
  console.error("TRIGGER MISMATCH — stopping.");
  console.error("Computed not in brief:", mismatch);
  console.error("Brief not in computed:", missing);
  process.exit(1);
}
console.log("Trigger verification: OK — 8 dates match brief specification.");

// ---------------------------------------------------------------------------
// 3. Canvas geometry
// ---------------------------------------------------------------------------

const VB_W = 720;
const VB_H = 405;
const M_T = 64;
const M_R = 24;
const M_B = 52;
const M_L = 44;

const PLOT_X = M_L;
const PLOT_Y = M_T;
const PLOT_W = VB_W - M_L - M_R; // 652
const PLOT_H = VB_H - M_T - M_B; // 289

// ---------------------------------------------------------------------------
// 4. Scales
// ---------------------------------------------------------------------------

const N = growths.length; // ~260 bars
const BAR_W = 1.6;
const GAP_W = 0.9;
const SLOT_W = BAR_W + GAP_W; // 2.5px per slot

// x: map bar index i (0-based) to pixel center
function xBar(i) {
  return PLOT_X + i * SLOT_W + BAR_W / 2;
}

// Total data width check
const totalW = N * SLOT_W;
if (Math.abs(totalW - PLOT_W) > 10) {
  console.warn(
    `Bar area width ${totalW.toFixed(1)} vs plot width ${PLOT_W} — slot sizing may need adjustment.`
  );
}

// y-scale: find actual min/max
const allVals = growths.map((g) => g.growth);
const dataMin = Math.min(...allVals); // ~-11
const dataMax = Math.max(...allVals); // ~+9

// Nice axis: ticks at -10, 0, 10 (covers range honestly including -11 COVID dip)
const Y_TICKS = [-10, 0, 10];
const AXIS_MIN = -11; // gives breathing room below -10 tick so 2020Q2 bar is visible
const AXIS_MAX = 11;

function yVal(v) {
  // Map value to SVG y (invert: higher value = lower y)
  return PLOT_Y + PLOT_H - ((v - AXIS_MIN) / (AXIS_MAX - AXIS_MIN)) * PLOT_H;
}

const Y_ZERO = yVal(0);

// ---------------------------------------------------------------------------
// 5. Date -> bar index lookup
// ---------------------------------------------------------------------------

const dateToIndex = new Map();
growths.forEach((g, i) => dateToIndex.set(g.date, i));

// Bar left-edge pixel for a given date
function barLeft(date) {
  const i = dateToIndex.get(date);
  if (i === undefined) return null;
  return PLOT_X + i * SLOT_W;
}

// Bar center-x
function barCenterX(date) {
  const i = dateToIndex.get(date);
  if (i === undefined) return null;
  return PLOT_X + i * SLOT_W + BAR_W / 2;
}

// ---------------------------------------------------------------------------
// 6. Recession bands (CD Howe, peak->trough quarter, inclusive)
// ---------------------------------------------------------------------------
// Spec: fill rgba(21,23,26,0.06), full plot height
// Dates given as peak-quarter left-edge to trough-quarter right-edge

const RECESSION_BANDS = [
  // [peak quarter ISO (start of peak quarter), trough quarter ISO (start of trough quarter)]
  ["1974-07-01", "1975-01-01"], // 1974Q3 - 1975Q1
  ["1981-04-01", "1982-10-01"], // 1981Q2 - 1982Q4
  ["1990-01-01", "1992-04-01"], // 1990Q1 - 1992Q2
  ["2008-07-01", "2009-04-01"], // 2008Q3 - 2009Q2
  ["2019-10-01", "2020-04-01"], // 2019Q4 - 2020Q2
];

function recessionBandRect(peakDate, troughDate) {
  // Left edge = left edge of peak quarter bar
  // Right edge = right edge of trough quarter bar
  const peakIdx = dateToIndex.get(peakDate);
  const troughIdx = dateToIndex.get(troughDate);

  // If peak quarter is before our data range, use plot left edge
  const x1 =
    peakIdx !== undefined ? PLOT_X + peakIdx * SLOT_W : PLOT_X;
  // If trough is in data
  const x2 =
    troughIdx !== undefined
      ? PLOT_X + troughIdx * SLOT_W + SLOT_W
      : PLOT_X + PLOT_W;

  return { x: x1, width: x2 - x1, y: PLOT_Y, height: PLOT_H };
}

// ---------------------------------------------------------------------------
// 7. X-axis decade ticks + false-alarm year labels
// ---------------------------------------------------------------------------

// Decade years visible in data: 1960 (not in data, data starts 1961Q2),
// 1970, 1980, 1990, 2000, 2010, 2020
// For each decade, find the first quarter of that year in growths
function decadeBarIndex(year) {
  const isoPrefix = `${year}-01-01`;
  const idx = dateToIndex.get(isoPrefix);
  if (idx !== undefined) return idx;
  // fallback: find any quarter in year
  const found = growths.findIndex((g) => g.date.startsWith(`${year}`));
  return found >= 0 ? found : null;
}

const DECADE_YEARS = [1960, 1970, 1980, 1990, 2000, 2010, 2020];
// False alarm years: 1980, 2015, 2026
// Where false-alarm year collides with decade tick, false-alarm wins (suppress decade)
const FALSE_ALARM_YEARS_LABELS = [1980, 2015, 2026];
const SUPPRESS_DECADES = new Set([1980]); // 1980 collides; 2020 does NOT collide with 2026

// ---------------------------------------------------------------------------
// 8. Build SVG
// ---------------------------------------------------------------------------

const lines_svg = [];

function emit(s) {
  lines_svg.push(s);
}

emit(`<?xml version="1.0" encoding="UTF-8"?>`);
emit(
  `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${VB_W} ${VB_H}" preserveAspectRatio="xMidYMid meet" width="${VB_W}" height="${VB_H}" style="background:#FFFFFF;font-family:Manrope,sans-serif;">`
);

// --- Defs: font imports ---
emit(`<defs>`);
emit(`  <style>`);
emit(
  `    @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;600;800&amp;family=IBM+Plex+Mono:wght@400&amp;display=swap');`
);
emit(`    text { font-family: Manrope, sans-serif; }`);
emit(`  </style>`);
emit(`</defs>`);

// ---------------------------------------------------------------------------
// Z-ORDER: bands -> gridlines -> zero line -> bars -> trigger markers ->
//          frame -> ticks/labels -> title block -> legend/source
// ---------------------------------------------------------------------------

// --- LAYER 1: Recession bands ---
emit(`<!-- Recession bands -->`);
for (const [peak, trough] of RECESSION_BANDS) {
  const r = recessionBandRect(peak, trough);
  emit(
    `<rect x="${r.x.toFixed(2)}" y="${r.y.toFixed(2)}" width="${r.width.toFixed(2)}" height="${r.height.toFixed(2)}" fill="rgba(21,23,26,0.06)" />`
  );
}

// --- LAYER 2: Gridlines (3 only, at Y_TICKS, excluding zero which is drawn separately) ---
emit(`<!-- Gridlines (non-zero) -->`);
for (const tick of Y_TICKS) {
  if (tick === 0) continue;
  const y = yVal(tick);
  emit(
    `<line x1="${PLOT_X}" y1="${y.toFixed(2)}" x2="${(PLOT_X + PLOT_W).toFixed(2)}" y2="${y.toFixed(2)}" stroke="#000000" stroke-opacity="0.15" stroke-width="1" />`
  );
}

// --- LAYER 3: Zero line (full opacity, heavier than gridlines) ---
emit(`<!-- Zero line -->`);
emit(
  `<line x1="${PLOT_X}" y1="${Y_ZERO.toFixed(2)}" x2="${(PLOT_X + PLOT_W).toFixed(2)}" y2="${Y_ZERO.toFixed(2)}" stroke="#000000" stroke-opacity="1" stroke-width="1" />`
);

// --- LAYER 4: Bars ---
// Positive bars: solid black #000000. Negative bars: solid red #E63946, no stroke.
emit(`<!-- Bars (positive=solid black, negative=solid red #E63946) -->`);
for (let i = 0; i < growths.length; i++) {
  const { growth } = growths[i];
  const bx = PLOT_X + i * SLOT_W;
  const isPos = growth >= 0;

  let barY, barH;
  if (isPos) {
    barY = yVal(growth);
    barH = Y_ZERO - barY;
  } else {
    barY = Y_ZERO;
    barH = yVal(growth) - Y_ZERO;
  }

  // Clamp bar height to avoid going outside plot bounds
  if (barH < 0) barH = 0;

  if (isPos) {
    emit(
      `<rect x="${bx.toFixed(2)}" y="${barY.toFixed(2)}" width="${BAR_W}" height="${barH.toFixed(2)}" fill="#000000" vector-effect="non-scaling-stroke" />`
    );
  } else {
    emit(
      `<rect x="${bx.toFixed(2)}" y="${barY.toFixed(2)}" width="${BAR_W}" height="${barH.toFixed(2)}" fill="#E63946" vector-effect="non-scaling-stroke" />`
    );
  }
}

// --- LAYER 5: Trigger markers ---
// Head: 8px square. Stem: 1.2px, from bottom of head down into plot area.
// Caret: small downward-pointing triangle below stem, leads eye toward the trigger bar.
// Filled ink square = true catch (recession followed); hollow (ink stroke, white) = false alarm.
// Pure black ink throughout — red now means negative bar, not marker.
const MARKER_HEAD_SIZE = 8; // enlarged from 5px
const MARKER_STEM_W = 1.2;
const MARKER_STEM_H = 10; // slightly longer for visibility
const CARET_H = 5; // downward triangle height
const CARET_W = 6; // downward triangle base width

// Head sits just inside the top frame — head top at PLOT_Y + 2
const MARKER_HEAD_TOP = PLOT_Y + 2;
const MARKER_HEAD_BOT = MARKER_HEAD_TOP + MARKER_HEAD_SIZE; // bottom of head square
const MARKER_STEM_TOP = MARKER_HEAD_BOT; // stem starts at bottom of head
const MARKER_STEM_BOT = MARKER_STEM_TOP + MARKER_STEM_H;
const MARKER_CARET_TOP = MARKER_STEM_BOT; // caret (triangle) apex at bottom of stem

emit(`<!-- Trigger markers -->`);
for (const [date, isCatch] of [
  ["1975-01-01", true],
  ["1980-07-01", false],
  ["1981-10-01", true],
  ["1990-07-01", true],
  ["2009-01-01", true],
  ["2015-04-01", false],
  ["2020-04-01", true],
  ["2026-01-01", false],
]) {
  const cx = barCenterX(date);
  if (cx === null) continue;

  const headX = (cx - MARKER_HEAD_SIZE / 2).toFixed(2);

  // Stem (from bottom of head downward)
  emit(
    `<line x1="${cx.toFixed(2)}" y1="${MARKER_STEM_TOP.toFixed(2)}" x2="${cx.toFixed(2)}" y2="${MARKER_STEM_BOT.toFixed(2)}" stroke="#000000" stroke-width="${MARKER_STEM_W}" />`
  );

  // Downward-pointing triangle caret (points toward the trigger bar below)
  // Triangle: flat top, pointed bottom (pointing down)
  const caretLeft = (cx - CARET_W / 2).toFixed(2);
  const caretRight = (cx + CARET_W / 2).toFixed(2);
  const caretApex = (MARKER_CARET_TOP + CARET_H).toFixed(2);
  emit(
    `<polygon points="${caretLeft},${MARKER_CARET_TOP.toFixed(2)} ${caretRight},${MARKER_CARET_TOP.toFixed(2)} ${cx.toFixed(2)},${caretApex}" fill="#000000" />`
  );

  // Head square
  if (isCatch) {
    // Filled pure-ink square — true catch
    emit(
      `<rect x="${headX}" y="${MARKER_HEAD_TOP.toFixed(2)}" width="${MARKER_HEAD_SIZE}" height="${MARKER_HEAD_SIZE}" fill="#000000" />`
    );
  } else {
    // Hollow square: 1px ink stroke, white fill — false alarm
    emit(
      `<rect x="${headX}" y="${MARKER_HEAD_TOP.toFixed(2)}" width="${MARKER_HEAD_SIZE}" height="${MARKER_HEAD_SIZE}" fill="#FFFFFF" stroke="#000000" stroke-width="1" />`
    );
  }
}

// --- LAYER 6: Plot frame (1px pure-ink hairline) ---
emit(`<!-- Plot frame -->`);
emit(
  `<rect x="${PLOT_X}" y="${PLOT_Y}" width="${PLOT_W}" height="${PLOT_H}" fill="none" stroke="#000000" stroke-width="1" />`
);

// --- LAYER 7: Y-axis tick labels ---
// IBM Plex Mono 400, 12px, right-aligned in left gutter
// Topmost tick (10%) carries % suffix; others bare
emit(`<!-- Y-axis tick labels -->`);
for (const tick of Y_TICKS) {
  const y = yVal(tick);
  const isTopmost = tick === Math.max(...Y_TICKS);
  const label = isTopmost ? `${tick}%` : `${tick}`;
  // Right-align at PLOT_X - 4
  emit(
    `<text x="${(PLOT_X - 5).toFixed(2)}" y="${(y + 4).toFixed(2)}" text-anchor="end" font-family="'IBM Plex Mono', monospace" font-size="12" fill="#000000">${label}</text>`
  );
}

// --- LAYER 7b: X-axis tick marks and labels ---
// Bottom of plot: PLOT_Y + PLOT_H
const X_TICK_Y = PLOT_Y + PLOT_H;
const X_LABEL_Y = X_TICK_Y + 16;

emit(`<!-- X-axis tick marks and labels -->`);

// Draw decade ticks (suppress if in SUPPRESS_DECADES)
for (const yr of DECADE_YEARS) {
  const idx = decadeBarIndex(yr);
  if (idx === null) continue;
  const px = PLOT_X + idx * SLOT_W;

  if (!SUPPRESS_DECADES.has(yr)) {
    // Tick mark
    emit(
      `<line x1="${px.toFixed(2)}" y1="${X_TICK_Y}" x2="${px.toFixed(2)}" y2="${(X_TICK_Y + 4).toFixed(2)}" stroke="#000000" stroke-width="1" />`
    );
    // Label — Manrope 400 12px
    emit(
      `<text x="${px.toFixed(2)}" y="${X_LABEL_Y}" text-anchor="middle" font-family="Manrope, sans-serif" font-weight="400" font-size="12" fill="#000000">${yr}</text>`
    );
  }
}

// False-alarm year labels: heavier weight (600), centered under their bar
for (const yr of FALSE_ALARM_YEARS_LABELS) {
  let isoDate;
  if (yr === 1980) isoDate = "1980-07-01"; // 1980Q3 false alarm bar
  else if (yr === 2015) isoDate = "2015-04-01"; // 2015Q2
  else if (yr === 2026) isoDate = "2026-01-01"; // 2026Q1

  const cx = barCenterX(isoDate);
  if (cx === null) continue;

  // Tick mark
  emit(
    `<line x1="${cx.toFixed(2)}" y1="${X_TICK_Y}" x2="${cx.toFixed(2)}" y2="${(X_TICK_Y + 4).toFixed(2)}" stroke="#000000" stroke-width="1" />`
  );
  // Label — Manrope 600 12px
  emit(
    `<text x="${cx.toFixed(2)}" y="${X_LABEL_Y}" text-anchor="middle" font-family="Manrope, sans-serif" font-weight="600" font-size="12" fill="#000000">${yr}</text>`
  );
}

// --- LAYER 8: Title block ---
// Title: Manrope 800, ~19px, pure ink, letter-spacing -0.012em
// Subtitle: Manrope 600 micro-caps (uppercase), 13px, letter-spacing 0.18em
const TITLE_Y = 22;
const SUBTITLE_Y = TITLE_Y + 13 + 8; // 8px below title baseline

emit(`<!-- Title block -->`);
emit(
  `<text x="${M_L}" y="${TITLE_Y}" font-family="Manrope, sans-serif" font-weight="800" font-size="19" fill="#000000" letter-spacing="-0.23">Two-quarters of negative growth is a rough rule of thumb.</text>`
);
emit(
  `<text x="${M_L}" y="${SUBTITLE_Y}" font-family="Manrope, sans-serif" font-weight="600" font-size="13" fill="#000000" letter-spacing="2.34" text-transform="uppercase">REAL GDP GROWTH, Q/Q</text>`
);

// --- LAYER 9: Legend (single horizontal row, below x-ticks) ---
// Three entries: [recession swatch] "Recession (CD Howe)"  [filled sq] "Rule fired, recession"  [hollow sq] "Rule fired, no recession"
// Source lines removed — attribution lives in surrounding text.
// Extra whitespace added above legend: legend pushed further down to give decade ticks + false-alarm
// year labels clear breathing room. X_LABEL_Y is ~M_B+16 from PLOT bottom; legend sits 22px below that.
const LEGEND_Y = VB_H - M_B + 36; // ~388 — pushed down from prior 379, source space reclaimed as air

// Legend entry measurements
const SWATCH_W = 14;
const SWATCH_H = 10;
const SQ_SIZE = 5;
const LEGEND_FONT = `font-family="Manrope, sans-serif" font-weight="600" font-size="12" fill="#000000" letter-spacing="0.72"`;

emit(`<!-- Legend -->`);

// Entry 1: Recession swatch
let lx = M_L;
const swatchY = LEGEND_Y - SWATCH_H + 2;
emit(
  `<rect x="${lx}" y="${swatchY}" width="${SWATCH_W}" height="${SWATCH_H}" fill="rgba(21,23,26,0.06)" stroke="#000000" stroke-width="0.5" />`
);
lx += SWATCH_W + 5;
emit(
  `<text x="${lx}" y="${LEGEND_Y}" ${LEGEND_FONT}>Recession (CD Howe)</text>`
);
lx += 155;

// Entry 2: Filled ink square + "Rule fired, recession"
const sqY = LEGEND_Y - SQ_SIZE + 1;
emit(
  `<rect x="${lx}" y="${sqY}" width="${SQ_SIZE}" height="${SQ_SIZE}" fill="#000000" />`
);
lx += SQ_SIZE + 5;
emit(`<text x="${lx}" y="${LEGEND_Y}" ${LEGEND_FONT}>Rule fired, recession</text>`);
lx += 165;

// Entry 3: Hollow square + "Rule fired, no recession"
emit(
  `<rect x="${lx}" y="${sqY}" width="${SQ_SIZE}" height="${SQ_SIZE}" fill="#FFFFFF" stroke="#000000" stroke-width="1" />`
);
lx += SQ_SIZE + 5;
emit(
  `<text x="${lx}" y="${LEGEND_Y}" ${LEGEND_FONT}>Rule fired, no recession</text>`
);

// Source lines removed per brief — attribution lives in surrounding text outside the SVG.

emit(`</svg>`);

// ---------------------------------------------------------------------------
// 9. Write SVG
// ---------------------------------------------------------------------------

const outDir = path.join(ROOT, "work/charts");
if (!fs.existsSync(outDir)) fs.mkdirSync(outDir, { recursive: true });

const svgPath = path.join(outDir, "two_quarter_rule_gdp.svg");
const svgContent = lines_svg.join("\n");
fs.writeFileSync(svgPath, svgContent, "utf8");
console.log(`SVG written: ${svgPath}`);

// ---------------------------------------------------------------------------
// 10. Rasterize to PNG via sharp (available as Astro dependency)
// ---------------------------------------------------------------------------

// sharp is a dep of astro; require from project node_modules
import { createRequire } from "module";
const require2 = createRequire(import.meta.url);
const sharp = require2(path.join(ROOT, "node_modules/sharp/lib/index.js"));

const pngPath = path.join(outDir, "two_quarter_rule_gdp.png");
const PNG_W = 1440;
const PNG_H = 810;

await sharp(Buffer.from(svgContent))
  .resize(PNG_W, PNG_H, { fit: "fill" })
  .png({ compressionLevel: 9 })
  .toFile(pngPath);

console.log(`PNG written: ${pngPath} (${PNG_W}x${PNG_H})`);
console.log(
  "\nTrigger quarters (as computed, matching brief spec):\n" +
    [
      "1975Q1 (1975-01-01) — TRUE CATCH",
      "1980Q3 (1980-07-01) — FALSE ALARM",
      "1981Q4 (1981-10-01) — TRUE CATCH",
      "1990Q3 (1990-07-01) — TRUE CATCH",
      "2009Q1 (2009-01-01) — TRUE CATCH",
      "2015Q2 (2015-04-01) — FALSE ALARM",
      "2020Q2 (2020-04-01) — TRUE CATCH",
      "2026Q1 (2026-01-01) — FALSE ALARM",
    ].join("\n")
);
