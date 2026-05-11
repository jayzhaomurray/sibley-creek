/*
 * render_pillar_b_charts.mjs
 *
 * Pre-renders the six Pillar B (BoC vs. Fed divergence) deep-dive inline
 * charts as static SVG files under public/charts/pillar-b/. Run once, ship
 * the SVGs as static assets; reference from the v1 markdown body via
 * standard image syntax.
 *
 * Charts:
 *   1) policy-rate-divergence.svg  -- BoC overnight vs Fed funds, monthly,
 *                                     1996-2026, dual-line + spread inset.
 *   2) 2y-spread-percentile.svg    -- 2y GoC - 2y UST spread, daily 2001-,
 *                                     with 5th/50th/95th percentile rules.
 *   3) usdcad-vs-2y-spread.svg     -- Dual-panel: USDCAD top, 2y spread
 *                                     bottom, daily Jan 2024 - May 2026.
 *   4) expectations-anchor.svg     -- CSCE 1y + 5y (primary) and BOS
 *                                     >3% share (dashed secondary),
 *                                     quarterly Q1 2021 - Q1 2026.
 *   5) passthrough-cascade.svg     -- Schematic horizontal-bar cascade:
 *                                     10% CAD -> 5.9% imports ->
 *                                     1.5-2.0 pp goods CPI ->
 *                                     0.5-0.7 pp headline CPI.
 *   6) precedent-2024-25.svg       -- BoC + Fed (left axis) and USDCAD
 *                                     (dashed secondary), monthly,
 *                                     Jan 2024 - May 2026.
 *
 * Canon (Tier-3): 720x405 viewBox, pure ink line 1.5px, MTA red 4px
 * latest-print dot, Plex Mono 12px y-ticks, Manrope 12px x-ticks,
 * 4 gridlines @ 0.18 opacity, 1px hairline plot frame. Direct labels
 * at line terminus. Multi-series: secondary 1px dashed pure ink, no dot.
 *
 * Standalone Node ESM script. No npm deps. Run:
 *   node scripts/charts/render_pillar_b_charts.mjs
 */

import { readFileSync, writeFileSync, mkdirSync, existsSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const ROOT = resolve(__dirname, "..", "..");
const OUT_DIR = resolve(ROOT, "public", "charts", "pillar-b");

if (!existsSync(OUT_DIR)) mkdirSync(OUT_DIR, { recursive: true });

/* ---------- canon constants ---------- */
const VB_W = 720;
const VB_H = 405;
const M_L = 56;
const M_R = 96;
const M_T = 36;
const M_B = 44;
const PLOT_X0 = M_L;
const PLOT_X1 = VB_W - M_R;
const PLOT_Y0 = M_T;
const PLOT_Y1 = VB_H - M_B;
const PLOT_W = PLOT_X1 - PLOT_X0;
const PLOT_H = PLOT_Y1 - PLOT_Y0;

const INK = "#000000";
const ACCENT = "#E63946";
const PAPER = "#FFFFFF";

const FONT_SANS = "Manrope, system-ui, sans-serif";
const FONT_MONO = "'IBM Plex Mono', Menlo, monospace";

/* ---------- CSV utilities ---------- */
function parseCsvLine(line) {
  const out = [];
  let cur = "";
  let inQuote = false;
  for (let i = 0; i < line.length; i++) {
    const ch = line[i];
    if (inQuote) {
      if (ch === '"') {
        if (line[i + 1] === '"') { cur += '"'; i++; }
        else { inQuote = false; }
      } else cur += ch;
    } else {
      if (ch === '"') inQuote = true;
      else if (ch === ",") { out.push(cur); cur = ""; }
      else cur += ch;
    }
  }
  out.push(cur);
  return out;
}

function readCsv(path) {
  const txt = readFileSync(path, "utf8");
  const lines = txt.split(/\r?\n/).filter((l) => l.length > 0);
  const header = parseCsvLine(lines[0]);
  const rows = [];
  for (let i = 1; i < lines.length; i++) {
    rows.push(parseCsvLine(lines[i]));
  }
  return { header, rows };
}

function loadSingleSeries(path) {
  const c = readCsv(path);
  return c.rows
    .map((r) => ({ date: r[0], value: r[1] }))
    .filter((p) => p.value !== "" && p.value != null && !Number.isNaN(parseFloat(p.value)))
    .map((p) => ({ date: p.date, value: parseFloat(p.value) }));
}

function filterRange(series, startDate, endDate) {
  return series.filter((p) => p.date >= startDate && (endDate == null || p.date <= endDate));
}

/* Resample a daily (or mixed) series to monthly end-of-month last value. */
function resampleMonthlyLast(series) {
  const byMonth = new Map();
  for (const p of series) {
    const ym = p.date.slice(0, 7);
    byMonth.set(ym, p); // overwrites; ordering preserved by Map insertion
  }
  const out = [];
  for (const [ym, p] of byMonth) {
    out.push({ date: `${ym}-01`, value: p.value });
  }
  out.sort((a, b) => (a.date < b.date ? -1 : a.date > b.date ? 1 : 0));
  return out;
}

/* Inner-join two series on date. Returns aligned pair of arrays. */
function innerJoin(a, b) {
  const bByDate = new Map(b.map((p) => [p.date, p.value]));
  const aOut = [];
  const bOut = [];
  for (const p of a) {
    if (bByDate.has(p.date)) {
      aOut.push({ date: p.date, value: p.value });
      bOut.push({ date: p.date, value: bByDate.get(p.date) });
    }
  }
  return [aOut, bOut];
}

function fmtMonthShort(d) {
  const months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
  const [y, m] = d.split("-").map((s) => parseInt(s, 10));
  return `${months[m - 1]} ${y}`;
}

function svgEscape(s) {
  return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

/* Scale builders. */
function xScaleByIndex(n) {
  return (i) => PLOT_X0 + (i / Math.max(1, n - 1)) * PLOT_W;
}
function yScaleRange(yMin, yMax, y0, y1) {
  return (v) => y1 - ((v - yMin) / (yMax - yMin)) * (y1 - y0);
}

function niceTicks(min, max, target = 4) {
  const range = max - min;
  if (range === 0) return [min];
  const rough = range / target;
  const mag = Math.pow(10, Math.floor(Math.log10(rough)));
  const candidates = [1, 2, 2.5, 5, 10].map((m) => m * mag);
  let step = candidates[0];
  for (const c of candidates) {
    if (Math.abs(range / c - target) < Math.abs(range / step - target)) step = c;
  }
  const t0 = Math.ceil(min / step) * step;
  const ticks = [];
  for (let v = t0; v <= max + 1e-9; v += step) ticks.push(+v.toFixed(10));
  return ticks;
}

function percentileRank(sorted, value) {
  // sorted ascending
  let lo = 0, hi = sorted.length;
  while (lo < hi) {
    const mid = (lo + hi) >> 1;
    if (sorted[mid] < value) lo = mid + 1; else hi = mid;
  }
  return lo / sorted.length;
}

function quantile(sorted, q) {
  if (sorted.length === 0) return NaN;
  const pos = q * (sorted.length - 1);
  const lo = Math.floor(pos);
  const hi = Math.ceil(pos);
  if (lo === hi) return sorted[lo];
  return sorted[lo] + (sorted[hi] - sorted[lo]) * (pos - lo);
}

/* ---------- Chart 1: policy-rate-divergence ---------- */
/* Two-panel layout: top panel BoC overnight + Fed funds (monthly, 1996-).
   Single SVG. Top panel = primary BoC (solid 1.5px) + secondary Fed
   (dashed 1px). Bottom slim panel = BoC-Fed spread, with zero line and
   latest-print dot. */
function chartPolicyRateDivergence() {
  const boc = loadSingleSeries(resolve(ROOT, "data/raw/overnight_rate.csv"));
  let fed = loadSingleSeries(resolve(ROOT, "data/raw/fed_funds.csv"));
  // Fed funds is mixed: monthly through 2008, daily 2009+. Resample to
  // monthly using last value per month, then take the first day of month.
  fed = resampleMonthlyLast(fed);
  // Filter to common range starting 1996-01.
  const start = "1996-01-01";
  const bocT = filterRange(boc, start);
  const fedT = filterRange(fed, start);
  const [bocAligned, fedAligned] = innerJoin(bocT, fedT);
  const n = bocAligned.length;
  const spread = bocAligned.map((p, i) => ({ date: p.date, value: p.value - fedAligned[i].value }));

  // Panel split
  const TOP_H = Math.round(PLOT_H * 0.62);
  const BOT_H = PLOT_H - TOP_H - 14;
  const TOP_Y0 = PLOT_Y0;
  const TOP_Y1 = PLOT_Y0 + TOP_H;
  const BOT_Y0 = TOP_Y1 + 14;
  const BOT_Y1 = PLOT_Y1;

  const x = xScaleByIndex(n);

  // Top panel scales
  const topVals = bocAligned.map((p) => p.value).concat(fedAligned.map((p) => p.value));
  const topMax = Math.ceil(Math.max(...topVals));
  const yTop = yScaleRange(0, topMax, TOP_Y0, TOP_Y1);
  const topTicks = niceTicks(0, topMax, 4);

  // Bottom panel scales (spread)
  const spreadMin = Math.min(...spread.map((p) => p.value));
  const spreadMax = Math.max(...spread.map((p) => p.value));
  const spadPad = (spreadMax - spreadMin) * 0.10;
  const sMin = Math.floor(spreadMin - spadPad);
  const sMax = Math.ceil(spreadMax + spadPad);
  const yBot = yScaleRange(sMin, sMax, BOT_Y0, BOT_Y1);
  const botTicks = niceTicks(sMin, sMax, 2);

  // x-tick positions
  const xTickIdx = [0, Math.floor(n / 3), Math.floor((2 * n) / 3), n - 1];
  const xTickDates = xTickIdx.map((i) => bocAligned[i].date);

  // paths
  const pathFor = (arr, yFn) => {
    let d = "";
    for (let i = 0; i < arr.length; i++) {
      d += (i === 0 ? "M" : "L") + x(i).toFixed(2) + " " + yFn(arr[i].value).toFixed(2) + " ";
    }
    return d.trim();
  };
  const bocD = pathFor(bocAligned, yTop);
  const fedD = pathFor(fedAligned, yTop);
  const spreadD = pathFor(spread, yBot);

  const lastIdx = n - 1;
  const lastX = x(lastIdx);
  const lastYBoc = yTop(bocAligned[lastIdx].value);
  const lastYSpread = yBot(spread[lastIdx].value);

  let out = "";
  out += `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${VB_W} ${VB_H}" preserveAspectRatio="xMidYMid meet" role="img" aria-label="BoC overnight rate target and Fed funds effective rate, monthly, January 1996 through April 2026, with the BoC minus Fed spread plotted in a slim bottom panel. Latest spread reading highlighted in red." style="display:block;width:100%;height:auto;background:${PAPER};font-family:${FONT_SANS}">`;

  // Top-panel gridlines
  for (const t of topTicks) {
    const yy = yTop(t);
    out += `<line x1="${PLOT_X0}" x2="${PLOT_X1}" y1="${yy.toFixed(2)}" y2="${yy.toFixed(2)}" stroke="${INK}" stroke-opacity="0.18" stroke-width="1"/>`;
  }
  // Bottom-panel gridlines + zero
  for (const t of botTicks) {
    const yy = yBot(t);
    out += `<line x1="${PLOT_X0}" x2="${PLOT_X1}" y1="${yy.toFixed(2)}" y2="${yy.toFixed(2)}" stroke="${INK}" stroke-opacity="0.18" stroke-width="1"/>`;
  }
  if (0 >= sMin && 0 <= sMax) {
    const zy = yBot(0);
    out += `<line x1="${PLOT_X0}" x2="${PLOT_X1}" y1="${zy.toFixed(2)}" y2="${zy.toFixed(2)}" stroke="${INK}" stroke-opacity="1" stroke-width="1"/>`;
  }

  // Top: Fed funds (dashed secondary)
  out += `<path d="${fedD}" stroke="${INK}" stroke-width="1" stroke-dasharray="4 2" fill="none" vector-effect="non-scaling-stroke"/>`;
  // Top: BoC overnight (primary)
  out += `<path d="${bocD}" stroke="${INK}" stroke-width="1.5" fill="none" vector-effect="non-scaling-stroke"/>`;
  // Latest BoC dot
  out += `<circle cx="${lastX.toFixed(2)}" cy="${lastYBoc.toFixed(2)}" r="4" fill="${ACCENT}"><title>BoC: ${fmtMonthShort(bocAligned[lastIdx].date)} ${bocAligned[lastIdx].value.toFixed(2)}%</title></circle>`;

  // Bottom: spread line
  out += `<path d="${spreadD}" stroke="${INK}" stroke-width="1.5" fill="none" vector-effect="non-scaling-stroke"/>`;
  // Latest spread dot
  out += `<circle cx="${lastX.toFixed(2)}" cy="${lastYSpread.toFixed(2)}" r="4" fill="${ACCENT}"><title>Spread: ${fmtMonthShort(spread[lastIdx].date)} ${spread[lastIdx].value.toFixed(2)} pp</title></circle>`;

  // Frames (both panels)
  out += `<rect x="${PLOT_X0}" y="${TOP_Y0}" width="${PLOT_W}" height="${TOP_H}" fill="none" stroke="${INK}" stroke-width="1"/>`;
  out += `<rect x="${PLOT_X0}" y="${BOT_Y0}" width="${PLOT_W}" height="${BOT_Y1 - BOT_Y0}" fill="none" stroke="${INK}" stroke-width="1"/>`;

  // Top y-ticks
  const topMostTop = topTicks[topTicks.length - 1];
  for (const t of topTicks) {
    const yy = yTop(t);
    const lbl = (t === topMostTop) ? `${t.toFixed(0)}%` : t.toFixed(0);
    out += `<text x="${(PLOT_X0 - 8).toFixed(2)}" y="${(yy + 4).toFixed(2)}" text-anchor="end" fill="${INK}" font-family="${FONT_MONO}" font-size="12" font-weight="400" font-variant-numeric="tabular-nums">${svgEscape(lbl)}</text>`;
  }
  // Bottom y-ticks
  const topMostBot = botTicks[botTicks.length - 1];
  for (const t of botTicks) {
    const yy = yBot(t);
    const lbl = (t === topMostBot) ? `${t.toFixed(1)}pp` : t.toFixed(1);
    out += `<text x="${(PLOT_X0 - 8).toFixed(2)}" y="${(yy + 4).toFixed(2)}" text-anchor="end" fill="${INK}" font-family="${FONT_MONO}" font-size="12" font-weight="400" font-variant-numeric="tabular-nums">${svgEscape(lbl)}</text>`;
  }
  // X-ticks (under bottom panel)
  for (let k = 0; k < xTickIdx.length; k++) {
    const ix = xTickIdx[k];
    const xx = x(ix);
    const label = fmtMonthShort(xTickDates[k]);
    const anchor = (k === 0) ? "start" : (k === xTickIdx.length - 1) ? "end" : "middle";
    out += `<text x="${xx.toFixed(2)}" y="${(BOT_Y1 + 18).toFixed(2)}" text-anchor="${anchor}" fill="${INK}" font-family="${FONT_SANS}" font-size="12" font-weight="400">${svgEscape(label)}</text>`;
  }

  // Direct labels at line termini
  const labelX = Math.min(lastX + 10, PLOT_X1 + M_R - 4);
  // BoC label
  out += `<text x="${labelX.toFixed(2)}" y="${(lastYBoc + 4).toFixed(2)}" fill="${INK}" font-family="${FONT_SANS}" font-size="13" font-weight="600">BoC</text>`;
  // Fed label (stack)
  const lastYFed = yTop(fedAligned[lastIdx].value);
  let fedLabelY = lastYFed + 4;
  if (Math.abs((lastYFed + 4) - (lastYBoc + 4)) < 13) fedLabelY = (lastYBoc + 4) + 14;
  out += `<text x="${labelX.toFixed(2)}" y="${fedLabelY.toFixed(2)}" fill="${INK}" font-family="${FONT_SANS}" font-size="13" font-weight="400">Fed</text>`;
  // Spread label
  out += `<text x="${labelX.toFixed(2)}" y="${(lastYSpread + 4).toFixed(2)}" fill="${INK}" font-family="${FONT_SANS}" font-size="13" font-weight="600">Spread</text>`;

  out += `</svg>`;
  writeFileSync(resolve(OUT_DIR, "policy-rate-divergence.svg"), out, "utf8");
  console.log("wrote policy-rate-divergence.svg (", n, "points, latest:", bocAligned[lastIdx].date, "BoC", bocAligned[lastIdx].value.toFixed(2), "Fed", fedAligned[lastIdx].value.toFixed(2), "Spread", spread[lastIdx].value.toFixed(2), ")");
}

/* ---------- Chart 2: 2y-spread-percentile ---------- */
/* 2y GoC - 2y UST, daily, post-2001. Three horizontal reference rules at
   5th / 50th / 95th percentile (dashed 4 2 pure ink). Latest dot in MTA red.
   Trough-of-Feb-2025 annotated. */
function chart2ySpreadPercentile() {
  const goc = loadSingleSeries(resolve(ROOT, "data/raw/yield_2yr.csv"));
  const ust = loadSingleSeries(resolve(ROOT, "data/raw/us_2yr.csv"));
  const [gocA, ustA] = innerJoin(goc, ust);
  const spread = gocA.map((p, i) => ({ date: p.date, value: p.value - ustA[i].value }));
  // Post-2001 by construction (goc starts 2001-01-02).
  const n = spread.length;
  const x = xScaleByIndex(n);

  // Percentile rules from the empirical distribution.
  const vals = spread.map((p) => p.value).slice().sort((a, b) => a - b);
  const p5 = quantile(vals, 0.05);
  const p50 = quantile(vals, 0.50);
  const p95 = quantile(vals, 0.95);
  const currentP = percentileRank(vals, spread[n - 1].value);

  const yMin = Math.floor(Math.min(...vals) * 10) / 10 - 0.1;
  const yMax = Math.ceil(Math.max(...vals) * 10) / 10 + 0.1;
  const y = yScaleRange(yMin, yMax, PLOT_Y0, PLOT_Y1);
  const ticks = niceTicks(yMin, yMax, 5);

  const xTickIdx = [0, Math.floor(n / 3), Math.floor((2 * n) / 3), n - 1];
  const xTickDates = xTickIdx.map((i) => spread[i].date);

  let d = "";
  for (let i = 0; i < n; i++) {
    d += (i === 0 ? "M" : "L") + x(i).toFixed(2) + " " + y(spread[i].value).toFixed(2) + " ";
  }

  const lastIdx = n - 1;
  const lastX = x(lastIdx);
  const lastY = y(spread[lastIdx].value);

  // Find the trough index (min spread = approx Feb 3 2025 at -170 bps).
  let troughIdx = 0;
  for (let i = 1; i < n; i++) if (spread[i].value < spread[troughIdx].value) troughIdx = i;
  const troughX = x(troughIdx);
  const troughY = y(spread[troughIdx].value);

  let out = "";
  out += `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${VB_W} ${VB_H}" preserveAspectRatio="xMidYMid meet" role="img" aria-label="2-year GoC minus 2-year UST yield spread, daily, January 2001 through May 2026. Horizontal dashes at the post-2001 5th, 50th, and 95th percentiles. Trough of -1.70 percentage points on February 3, 2025 annotated. Latest reading highlighted in red." style="display:block;width:100%;height:auto;background:${PAPER};font-family:${FONT_SANS}">`;

  // Gridlines
  for (const t of ticks) {
    const yy = y(t);
    out += `<line x1="${PLOT_X0}" x2="${PLOT_X1}" y1="${yy.toFixed(2)}" y2="${yy.toFixed(2)}" stroke="${INK}" stroke-opacity="0.18" stroke-width="1"/>`;
  }
  // Zero line (heavier)
  if (0 >= yMin && 0 <= yMax) {
    const zy = y(0);
    out += `<line x1="${PLOT_X0}" x2="${PLOT_X1}" y1="${zy.toFixed(2)}" y2="${zy.toFixed(2)}" stroke="${INK}" stroke-opacity="1" stroke-width="1"/>`;
  }

  // Percentile reference rules (dashed 4 2)
  const rules = [
    { v: p5, label: "p5" },
    { v: p50, label: "p50" },
    { v: p95, label: "p95" },
  ];
  for (const r of rules) {
    const yy = y(r.v);
    out += `<line x1="${PLOT_X0}" x2="${PLOT_X1}" y1="${yy.toFixed(2)}" y2="${yy.toFixed(2)}" stroke="${INK}" stroke-width="1" stroke-dasharray="4 2" stroke-opacity="0.7"/>`;
    // Right-side label
    out += `<text x="${(PLOT_X1 + 6).toFixed(2)}" y="${(yy + 4).toFixed(2)}" fill="${INK}" font-family="${FONT_SANS}" font-size="11" font-weight="500" fill-opacity="0.75">${r.label}</text>`;
  }

  // Data line
  out += `<path d="${d.trim()}" stroke="${INK}" stroke-width="1.5" fill="none" vector-effect="non-scaling-stroke"/>`;

  // Trough annotation: leader from text to point
  // Place annotation text in upper-right white space above zero.
  const annoX = troughX + 10;
  const annoY = troughY - 30;
  out += `<line x1="${(troughX).toFixed(2)}" y1="${(troughY - 6).toFixed(2)}" x2="${(annoX).toFixed(2)}" y2="${(annoY + 6).toFixed(2)}" stroke="${INK}" stroke-width="1"/>`;
  out += `<text x="${(annoX + 2).toFixed(2)}" y="${(annoY).toFixed(2)}" fill="${INK}" font-family="${FONT_SANS}" font-size="13" font-weight="400"><tspan font-weight="600">Feb 3 2025</tspan>: -1.70 pp</text>`;

  // Latest dot
  out += `<circle cx="${lastX.toFixed(2)}" cy="${lastY.toFixed(2)}" r="4" fill="${ACCENT}"><title>Latest: ${fmtMonthShort(spread[lastIdx].date)} ${spread[lastIdx].value.toFixed(2)} pp (${(currentP * 100).toFixed(0)}th pctile)</title></circle>`;

  // Frame
  out += `<rect x="${PLOT_X0}" y="${PLOT_Y0}" width="${PLOT_W}" height="${PLOT_H}" fill="none" stroke="${INK}" stroke-width="1"/>`;

  // Y-ticks
  const topMostTick = ticks[ticks.length - 1];
  for (const t of ticks) {
    const yy = y(t);
    const lbl = (t === topMostTick) ? `${t.toFixed(1)}pp` : t.toFixed(1);
    out += `<text x="${(PLOT_X0 - 8).toFixed(2)}" y="${(yy + 4).toFixed(2)}" text-anchor="end" fill="${INK}" font-family="${FONT_MONO}" font-size="12" font-weight="400" font-variant-numeric="tabular-nums">${svgEscape(lbl)}</text>`;
  }
  // X-ticks
  for (let k = 0; k < xTickIdx.length; k++) {
    const ix = xTickIdx[k];
    const xx = x(ix);
    const label = fmtMonthShort(xTickDates[k]);
    const anchor = (k === 0) ? "start" : (k === xTickIdx.length - 1) ? "end" : "middle";
    out += `<text x="${xx.toFixed(2)}" y="${(PLOT_Y1 + 18).toFixed(2)}" text-anchor="${anchor}" fill="${INK}" font-family="${FONT_SANS}" font-size="12" font-weight="400">${svgEscape(label)}</text>`;
  }

  // Direct end-of-line label: "2y spread"
  const labelX = Math.min(lastX + 10, PLOT_X1 + M_R - 4);
  out += `<text x="${labelX.toFixed(2)}" y="${(lastY + 4).toFixed(2)}" fill="${INK}" font-family="${FONT_SANS}" font-size="13" font-weight="600">2y spread</text>`;

  out += `</svg>`;
  writeFileSync(resolve(OUT_DIR, "2y-spread-percentile.svg"), out, "utf8");
  console.log("wrote 2y-spread-percentile.svg (", n, "days, latest:", spread[lastIdx].date, spread[lastIdx].value.toFixed(2), "pp,", (currentP * 100).toFixed(0), "th pctile, trough:", spread[troughIdx].date, spread[troughIdx].value.toFixed(2), ")");
}

/* ---------- Chart 3: usdcad-vs-2y-spread ---------- */
/* Dual-panel: USDCAD top (primary), 2y spread bottom (primary). Same time
   axis Jan 2024 - May 2026. The visual gag is that they move in opposite
   directions through Q1-Q2 2026. */
function chartUsdcadVs2ySpread() {
  const fx = loadSingleSeries(resolve(ROOT, "data/raw/usdcad.csv"));
  const goc = loadSingleSeries(resolve(ROOT, "data/raw/yield_2yr.csv"));
  const ust = loadSingleSeries(resolve(ROOT, "data/raw/us_2yr.csv"));
  const [gocA, ustA] = innerJoin(goc, ust);
  const spread = gocA.map((p, i) => ({ date: p.date, value: p.value - ustA[i].value }));

  const start = "2024-01-01";
  const fxT = filterRange(fx, start);
  const spT = filterRange(spread, start);
  // Use independent x-scales per panel (they have different sample counts
  // because FX is BoC noon spot and yields are bond settlement days). Map
  // by date-fraction along the window instead of by index.
  const allStart = Math.min(new Date(fxT[0].date).getTime(), new Date(spT[0].date).getTime());
  const allEnd = Math.max(new Date(fxT[fxT.length - 1].date).getTime(), new Date(spT[spT.length - 1].date).getTime());
  const xByDate = (d) => {
    const t = new Date(d).getTime();
    return PLOT_X0 + ((t - allStart) / (allEnd - allStart)) * PLOT_W;
  };

  // Panel split
  const TOP_H = Math.round(PLOT_H * 0.48);
  const BOT_H = PLOT_H - TOP_H - 14;
  const TOP_Y0 = PLOT_Y0;
  const TOP_Y1 = PLOT_Y0 + TOP_H;
  const BOT_Y0 = TOP_Y1 + 14;
  const BOT_Y1 = PLOT_Y1;

  // Scales
  const fxVals = fxT.map((p) => p.value);
  const fxMin = Math.floor(Math.min(...fxVals) * 100) / 100 - 0.005;
  const fxMax = Math.ceil(Math.max(...fxVals) * 100) / 100 + 0.005;
  const yFx = yScaleRange(fxMin, fxMax, TOP_Y0, TOP_Y1);
  const fxTicks = niceTicks(fxMin, fxMax, 3);

  const spVals = spT.map((p) => p.value);
  const spMin = Math.floor(Math.min(...spVals) * 10) / 10 - 0.05;
  const spMax = Math.ceil(Math.max(...spVals) * 10) / 10 + 0.05;
  const ySp = yScaleRange(spMin, spMax, BOT_Y0, BOT_Y1);
  const spTicks = niceTicks(spMin, spMax, 3);

  // Build paths via date scale
  const pathFor = (arr, yFn) => {
    let d = "";
    for (let i = 0; i < arr.length; i++) {
      d += (i === 0 ? "M" : "L") + xByDate(arr[i].date).toFixed(2) + " " + yFn(arr[i].value).toFixed(2) + " ";
    }
    return d.trim();
  };
  const fxD = pathFor(fxT, yFx);
  const spD = pathFor(spT, ySp);

  const fxLast = fxT[fxT.length - 1];
  const spLast = spT[spT.length - 1];
  const fxLastX = xByDate(fxLast.date);
  const fxLastY = yFx(fxLast.value);
  const spLastX = xByDate(spLast.date);
  const spLastY = ySp(spLast.value);

  // X-ticks: 4 evenly spaced dates across the window
  const ms = allEnd - allStart;
  const xTickMs = [allStart, allStart + ms / 3, allStart + (2 * ms) / 3, allEnd];
  const xTickLabels = xTickMs.map((t) => {
    const dt = new Date(t);
    const y = dt.getUTCFullYear();
    const m = dt.getUTCMonth();
    const months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
    return `${months[m]} ${y}`;
  });

  let out = "";
  out += `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${VB_W} ${VB_H}" preserveAspectRatio="xMidYMid meet" role="img" aria-label="USDCAD spot rate (top panel) and 2-year GoC minus 2-year UST spread (bottom panel), daily, January 2024 through May 2026. The two series are moving in opposite directions through Q1 and Q2 of 2026. Latest readings highlighted in red." style="display:block;width:100%;height:auto;background:${PAPER};font-family:${FONT_SANS}">`;

  // Gridlines
  for (const t of fxTicks) {
    const yy = yFx(t);
    out += `<line x1="${PLOT_X0}" x2="${PLOT_X1}" y1="${yy.toFixed(2)}" y2="${yy.toFixed(2)}" stroke="${INK}" stroke-opacity="0.18" stroke-width="1"/>`;
  }
  for (const t of spTicks) {
    const yy = ySp(t);
    out += `<line x1="${PLOT_X0}" x2="${PLOT_X1}" y1="${yy.toFixed(2)}" y2="${yy.toFixed(2)}" stroke="${INK}" stroke-opacity="0.18" stroke-width="1"/>`;
  }
  // Zero line in spread panel
  if (0 >= spMin && 0 <= spMax) {
    const zy = ySp(0);
    out += `<line x1="${PLOT_X0}" x2="${PLOT_X1}" y1="${zy.toFixed(2)}" y2="${zy.toFixed(2)}" stroke="${INK}" stroke-opacity="1" stroke-width="1"/>`;
  }

  // Data lines
  out += `<path d="${fxD}" stroke="${INK}" stroke-width="1.5" fill="none" vector-effect="non-scaling-stroke"/>`;
  out += `<path d="${spD}" stroke="${INK}" stroke-width="1.5" fill="none" vector-effect="non-scaling-stroke"/>`;

  // Latest dots
  out += `<circle cx="${fxLastX.toFixed(2)}" cy="${fxLastY.toFixed(2)}" r="4" fill="${ACCENT}"><title>USDCAD: ${fxLast.date} ${fxLast.value.toFixed(4)}</title></circle>`;
  out += `<circle cx="${spLastX.toFixed(2)}" cy="${spLastY.toFixed(2)}" r="4" fill="${ACCENT}"><title>2y spread: ${spLast.date} ${spLast.value.toFixed(2)} pp</title></circle>`;

  // Frames
  out += `<rect x="${PLOT_X0}" y="${TOP_Y0}" width="${PLOT_W}" height="${TOP_H}" fill="none" stroke="${INK}" stroke-width="1"/>`;
  out += `<rect x="${PLOT_X0}" y="${BOT_Y0}" width="${PLOT_W}" height="${BOT_Y1 - BOT_Y0}" fill="none" stroke="${INK}" stroke-width="1"/>`;

  // Y-ticks
  const fxTopMost = fxTicks[fxTicks.length - 1];
  for (const t of fxTicks) {
    const yy = yFx(t);
    const lbl = (t === fxTopMost) ? `${t.toFixed(2)} CAD` : t.toFixed(2);
    out += `<text x="${(PLOT_X0 - 8).toFixed(2)}" y="${(yy + 4).toFixed(2)}" text-anchor="end" fill="${INK}" font-family="${FONT_MONO}" font-size="12" font-weight="400" font-variant-numeric="tabular-nums">${svgEscape(lbl)}</text>`;
  }
  const spTopMost = spTicks[spTicks.length - 1];
  for (const t of spTicks) {
    const yy = ySp(t);
    const lbl = (t === spTopMost) ? `${t.toFixed(1)}pp` : t.toFixed(1);
    out += `<text x="${(PLOT_X0 - 8).toFixed(2)}" y="${(yy + 4).toFixed(2)}" text-anchor="end" fill="${INK}" font-family="${FONT_MONO}" font-size="12" font-weight="400" font-variant-numeric="tabular-nums">${svgEscape(lbl)}</text>`;
  }
  // X-ticks under bottom panel
  for (let k = 0; k < xTickMs.length; k++) {
    const xx = xByDate(new Date(xTickMs[k]).toISOString().slice(0, 10));
    const anchor = (k === 0) ? "start" : (k === xTickMs.length - 1) ? "end" : "middle";
    out += `<text x="${xx.toFixed(2)}" y="${(BOT_Y1 + 18).toFixed(2)}" text-anchor="${anchor}" fill="${INK}" font-family="${FONT_SANS}" font-size="12" font-weight="400">${svgEscape(xTickLabels[k])}</text>`;
  }

  // Direct labels at line termini
  const labelX = Math.min(fxLastX + 10, PLOT_X1 + M_R - 4);
  out += `<text x="${labelX.toFixed(2)}" y="${(fxLastY + 4).toFixed(2)}" fill="${INK}" font-family="${FONT_SANS}" font-size="13" font-weight="600">USDCAD</text>`;
  const spLabelX = Math.min(spLastX + 10, PLOT_X1 + M_R - 4);
  out += `<text x="${spLabelX.toFixed(2)}" y="${(spLastY + 4).toFixed(2)}" fill="${INK}" font-family="${FONT_SANS}" font-size="13" font-weight="600">2y spread</text>`;

  out += `</svg>`;
  writeFileSync(resolve(OUT_DIR, "usdcad-vs-2y-spread.svg"), out, "utf8");
  console.log("wrote usdcad-vs-2y-spread.svg (FX", fxT.length, ", spread", spT.length, "; latest FX", fxLast.date, fxLast.value, ", spread", spLast.date, spLast.value.toFixed(2), ")");
}

/* ---------- Chart 4: expectations-anchor ---------- */
/* CSCE 1y (primary solid) + CSCE 5y (dashed secondary). BOS share above 3%
   shown as secondary right-axis dashed, with right-axis tick labels.
   Quarterly Q1 2021 - Q1 2026. */
function chartExpectationsAnchor() {
  const csce1 = loadSingleSeries(resolve(ROOT, "data/raw/infl_exp_consumer_1y.csv"));
  const csce5 = loadSingleSeries(resolve(ROOT, "data/raw/infl_exp_consumer_5y.csv"));
  const bos = loadSingleSeries(resolve(ROOT, "data/raw/bos_dist_above3.csv"));

  const start = "2021-01-01";
  const c1 = filterRange(csce1, start);
  const c5 = filterRange(csce5, start);
  const bo = filterRange(bos, start);

  // Build a common quarterly date axis from c1 (canonical for CSCE).
  const dates = c1.map((p) => p.date);
  const c5ByDate = new Map(c5.map((p) => [p.date, p.value]));
  const bosByDate = new Map(bo.map((p) => [p.date, p.value]));
  // Keep only quarters where we have CSCE 1y. Some quarters may not have
  // c5 / BOS; we'll plot what's available with NaN gap handling.
  const c1Aligned = c1;
  const c5Aligned = dates.map((d) => ({ date: d, value: c5ByDate.has(d) ? c5ByDate.get(d) : NaN }));
  const bosAligned = dates.map((d) => ({ date: d, value: bosByDate.has(d) ? bosByDate.get(d) : NaN }));

  const n = c1Aligned.length;
  const x = xScaleByIndex(n);

  // Left axis: CSCE in percent (covers 1y around 2-5, 5y around 2.5-4).
  const leftVals = c1Aligned.map((p) => p.value).concat(c5Aligned.map((p) => p.value).filter((v) => !Number.isNaN(v)));
  const leftMin = Math.floor(Math.min(...leftVals) * 2) / 2;
  const leftMax = Math.ceil(Math.max(...leftVals) * 2) / 2;
  const yLeft = yScaleRange(leftMin, leftMax, PLOT_Y0, PLOT_Y1);
  const leftTicks = niceTicks(leftMin, leftMax, 4);

  // Right axis: BOS share above 3% in percent (covers ~10-90 in stressed periods).
  const bosVals = bosAligned.map((p) => p.value).filter((v) => !Number.isNaN(v));
  const rightMin = 0;
  const rightMax = Math.ceil(Math.max(...bosVals) / 10) * 10;
  const yRight = yScaleRange(rightMin, rightMax, PLOT_Y0, PLOT_Y1);
  const rightTicks = niceTicks(rightMin, rightMax, 4);

  // Path with gap handling
  function pathFor(arr, yFn) {
    let d = "";
    let started = false;
    for (let i = 0; i < arr.length; i++) {
      const v = arr[i].value;
      if (Number.isNaN(v)) { started = false; continue; }
      d += (started ? "L" : "M") + x(i).toFixed(2) + " " + yFn(v).toFixed(2) + " ";
      started = true;
    }
    return d.trim();
  }
  const c1D = pathFor(c1Aligned, yLeft);
  const c5D = pathFor(c5Aligned, yLeft);
  const bosD = pathFor(bosAligned, yRight);

  // 2% target rule
  const targetY = yLeft(2);

  // last indices for direct labels
  const lastIdx = n - 1;
  const lastX = x(lastIdx);
  const c1LastY = yLeft(c1Aligned[lastIdx].value);
  // Find last non-NaN values for c5 and bos
  function lastValidIdx(arr) {
    for (let i = arr.length - 1; i >= 0; i--) if (!Number.isNaN(arr[i].value)) return i;
    return -1;
  }
  const c5LastIdx = lastValidIdx(c5Aligned);
  const bosLastIdx = lastValidIdx(bosAligned);
  const c5LastX = x(c5LastIdx);
  const c5LastY = yLeft(c5Aligned[c5LastIdx].value);
  const bosLastX = x(bosLastIdx);
  const bosLastY = yRight(bosAligned[bosLastIdx].value);

  const xTickIdx = [0, Math.floor(n / 3), Math.floor((2 * n) / 3), n - 1];
  const xTickDates = xTickIdx.map((i) => c1Aligned[i].date);

  let out = "";
  out += `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${VB_W} ${VB_H}" preserveAspectRatio="xMidYMid meet" role="img" aria-label="CSCE 1-year and 5-year consumer inflation expectations on the left axis, and BOS share of firms expecting CPI above 3 percent on the right axis. Quarterly, Q1 2021 through Q1 2026. Latest CSCE 1-year print highlighted in red." style="display:block;width:100%;height:auto;background:${PAPER};font-family:${FONT_SANS}">`;

  // Gridlines (left axis ticks)
  for (const t of leftTicks) {
    const yy = yLeft(t);
    out += `<line x1="${PLOT_X0}" x2="${PLOT_X1}" y1="${yy.toFixed(2)}" y2="${yy.toFixed(2)}" stroke="${INK}" stroke-opacity="0.18" stroke-width="1"/>`;
  }
  // 2% target reference rule (dashed)
  if (2 >= leftMin && 2 <= leftMax) {
    out += `<line x1="${PLOT_X0}" x2="${PLOT_X1}" y1="${targetY.toFixed(2)}" y2="${targetY.toFixed(2)}" stroke="${INK}" stroke-width="1" stroke-dasharray="4 2"/>`;
    out += `<text x="${(PLOT_X1 + 6).toFixed(2)}" y="${(targetY + 4).toFixed(2)}" fill="${INK}" font-family="${FONT_SANS}" font-size="11" font-weight="600">2% target</text>`;
  }

  // BOS line (secondary, dashed, right-axis)
  out += `<path d="${bosD}" stroke="${INK}" stroke-width="1" stroke-dasharray="4 2" fill="none" vector-effect="non-scaling-stroke"/>`;
  // CSCE 5y (secondary, dotted)
  out += `<path d="${c5D}" stroke="${INK}" stroke-width="1" stroke-dasharray="1 3" fill="none" vector-effect="non-scaling-stroke"/>`;
  // CSCE 1y (primary)
  out += `<path d="${c1D}" stroke="${INK}" stroke-width="1.5" fill="none" vector-effect="non-scaling-stroke"/>`;

  // Latest dot on CSCE 1y
  out += `<circle cx="${lastX.toFixed(2)}" cy="${c1LastY.toFixed(2)}" r="4" fill="${ACCENT}"><title>CSCE 1y: ${fmtMonthShort(c1Aligned[lastIdx].date)} ${c1Aligned[lastIdx].value.toFixed(2)}%</title></circle>`;

  // Frame
  out += `<rect x="${PLOT_X0}" y="${PLOT_Y0}" width="${PLOT_W}" height="${PLOT_H}" fill="none" stroke="${INK}" stroke-width="1"/>`;

  // Left y-ticks
  const leftTop = leftTicks[leftTicks.length - 1];
  for (const t of leftTicks) {
    const yy = yLeft(t);
    const lbl = (t === leftTop) ? `${t.toFixed(1)}%` : t.toFixed(1);
    out += `<text x="${(PLOT_X0 - 8).toFixed(2)}" y="${(yy + 4).toFixed(2)}" text-anchor="end" fill="${INK}" font-family="${FONT_MONO}" font-size="12" font-weight="400" font-variant-numeric="tabular-nums">${svgEscape(lbl)}</text>`;
  }
  // Right y-ticks (dashed series; render at left of right gutter)
  const rightTop = rightTicks[rightTicks.length - 1];
  for (const t of rightTicks) {
    const yy = yRight(t);
    const lbl = (t === rightTop) ? `${t.toFixed(0)}%` : t.toFixed(0);
    out += `<text x="${(PLOT_X1 + 8).toFixed(2)}" y="${(yy + 4).toFixed(2)}" text-anchor="start" fill="${INK}" font-family="${FONT_MONO}" font-size="12" font-weight="400" font-variant-numeric="tabular-nums" fill-opacity="0.7">${svgEscape(lbl)}</text>`;
  }
  // X-ticks
  for (let k = 0; k < xTickIdx.length; k++) {
    const ix = xTickIdx[k];
    const xx = x(ix);
    const label = fmtMonthShort(xTickDates[k]);
    const anchor = (k === 0) ? "start" : (k === xTickIdx.length - 1) ? "end" : "middle";
    out += `<text x="${xx.toFixed(2)}" y="${(PLOT_Y1 + 18).toFixed(2)}" text-anchor="${anchor}" fill="${INK}" font-family="${FONT_SANS}" font-size="12" font-weight="400">${svgEscape(label)}</text>`;
  }

  // Direct labels at line termini, stacked to avoid overlap
  // Compute candidate label Ys, sort by position, push apart by 14px.
  const labels = [
    { x: lastX, y: c1LastY, text: "CSCE 1y", weight: 600 },
    { x: c5LastX, y: c5LastY, text: "CSCE 5y", weight: 400 },
    { x: bosLastX, y: bosLastY, text: "BOS >3%", weight: 400 },
  ];
  labels.sort((a, b) => a.y - b.y);
  for (let i = 1; i < labels.length; i++) {
    if (labels[i].y - labels[i - 1].y < 14) labels[i].y = labels[i - 1].y + 14;
  }
  for (const lab of labels) {
    const lx = Math.min(lab.x + 10, PLOT_X1 + M_R - 4);
    out += `<text x="${lx.toFixed(2)}" y="${(lab.y + 4).toFixed(2)}" fill="${INK}" font-family="${FONT_SANS}" font-size="13" font-weight="${lab.weight}">${svgEscape(lab.text)}</text>`;
  }

  out += `</svg>`;
  writeFileSync(resolve(OUT_DIR, "expectations-anchor.svg"), out, "utf8");
  console.log("wrote expectations-anchor.svg (", n, "quarters; latest CSCE 1y", c1Aligned[lastIdx].date, c1Aligned[lastIdx].value.toFixed(2), "; CSCE 5y last", c5Aligned[c5LastIdx].value.toFixed(2), "; BOS last", bosAligned[bosLastIdx].value.toFixed(0), ")");
}

/* ---------- Chart 5: passthrough-cascade (schematic) ---------- */
/* Conceptual horizontal-bar cascade. Four rows top-to-bottom:
   1. CAD depreciation -10%
   2. Import-price lift +5.9%  (via Devereux 0.59 pass-through)
   3. Goods CPI lift +1.5 to +2.0 pp
   4. Headline CPI lift +0.5 to +0.7 pp over 2y
   Each row: row label on left, horizontal bar showing magnitude, right
   number, source annotation under final row. Pure ink, no fill except
   the bars themselves (a low-ink wash to keep it light). */
function chartPassthroughCascade() {
  const rowH = 56;
  const gap = 18;
  const startY = M_T + 20;
  const labelW = 200; // left gutter for row label
  const rowX0 = M_L + labelW;
  const rowX1 = PLOT_X1 - 100; // reserve right for the magnitude figure
  const rowW = rowX1 - rowX0;

  const rows = [
    {
      label: "CAD depreciation",
      sub: "USDCAD: 1.36 -> 1.50",
      value: 10,
      vMin: 0, vMax: 10,
      figure: "-10%",
      source: null,
    },
    {
      label: "Import-price lift",
      sub: "Devereux et al. 0.59 pass-through",
      value: 5.9,
      vMin: 0, vMax: 10,
      figure: "+5.9%",
      source: null,
    },
    {
      label: "Goods CPI lift",
      sub: "x imported share 25-35% of goods basket",
      value: [1.5, 2.0],
      vMin: 0, vMax: 4,
      figure: "+1.5 to +2.0 pp",
      source: null,
    },
    {
      label: "Headline CPI lift",
      sub: "x goods share 47% of headline; over 2 years",
      value: [0.5, 0.7],
      vMin: 0, vMax: 4,
      figure: "+0.5 to +0.7 pp",
      source: "Structural ballpark; BoC MPR tradition",
    },
  ];

  let out = "";
  out += `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${VB_W} ${VB_H}" preserveAspectRatio="xMidYMid meet" role="img" aria-label="Pass-through cascade: a 10 percent CAD depreciation translates through Devereux et al. 0.59 import-price pass-through to a 5.9 percent lift in imports, through the imported-goods share of the CPI basket to a 1.5 to 2.0 percentage-point lift in goods CPI, and through the goods share of headline to a 0.5 to 0.7 percentage-point lift in headline CPI over two years." style="display:block;width:100%;height:auto;background:${PAPER};font-family:${FONT_SANS}">`;

  for (let i = 0; i < rows.length; i++) {
    const r = rows[i];
    const y = startY + i * (rowH + gap);
    const yMid = y + rowH / 2;

    // Row label (left gutter)
    out += `<text x="${M_L}" y="${(yMid - 4).toFixed(2)}" fill="${INK}" font-family="${FONT_SANS}" font-size="14" font-weight="600">${svgEscape(r.label)}</text>`;
    out += `<text x="${M_L}" y="${(yMid + 12).toFixed(2)}" fill="${INK}" font-family="${FONT_SANS}" font-size="11" font-weight="400" fill-opacity="0.65">${svgEscape(r.sub)}</text>`;

    // Bar background (hairline frame)
    out += `<rect x="${rowX0}" y="${(yMid - 8).toFixed(2)}" width="${rowW}" height="16" fill="none" stroke="${INK}" stroke-width="1" stroke-opacity="0.3"/>`;

    // Bar fill -- ink wash for solid value, or two-tone for range
    if (Array.isArray(r.value)) {
      const [vLo, vHi] = r.value;
      const xLo = rowX0 + (vLo / r.vMax) * rowW;
      const xHi = rowX0 + (vHi / r.vMax) * rowW;
      // light wash to vHi
      out += `<rect x="${rowX0}" y="${(yMid - 8).toFixed(2)}" width="${(xHi - rowX0).toFixed(2)}" height="16" fill="${INK}" fill-opacity="0.10"/>`;
      // solid bar to vLo
      out += `<rect x="${rowX0}" y="${(yMid - 8).toFixed(2)}" width="${(xLo - rowX0).toFixed(2)}" height="16" fill="${INK}" fill-opacity="0.45"/>`;
      // range marker
      out += `<line x1="${xHi.toFixed(2)}" x2="${xHi.toFixed(2)}" y1="${(yMid - 12).toFixed(2)}" y2="${(yMid + 12).toFixed(2)}" stroke="${INK}" stroke-width="1"/>`;
    } else {
      const xVal = rowX0 + (r.value / r.vMax) * rowW;
      out += `<rect x="${rowX0}" y="${(yMid - 8).toFixed(2)}" width="${(xVal - rowX0).toFixed(2)}" height="16" fill="${INK}" fill-opacity="0.55"/>`;
      // value marker (vertical tick)
      out += `<line x1="${xVal.toFixed(2)}" x2="${xVal.toFixed(2)}" y1="${(yMid - 12).toFixed(2)}" y2="${(yMid + 12).toFixed(2)}" stroke="${INK}" stroke-width="1"/>`;
    }

    // Figure (right)
    out += `<text x="${(rowX1 + 8).toFixed(2)}" y="${(yMid + 4).toFixed(2)}" fill="${INK}" font-family="${FONT_MONO}" font-size="13" font-weight="500" font-variant-numeric="tabular-nums">${svgEscape(r.figure)}</text>`;

    // Cascade arrow to next row (small downward chevron)
    if (i < rows.length - 1) {
      const arrowX = rowX0 - 20;
      const arrowY0 = y + rowH;
      const arrowY1 = arrowY0 + gap - 2;
      out += `<line x1="${arrowX}" x2="${arrowX}" y1="${arrowY0}" y2="${arrowY1}" stroke="${INK}" stroke-width="1" stroke-opacity="0.5"/>`;
      out += `<line x1="${(arrowX - 4)}" x2="${arrowX}" y1="${(arrowY1 - 4)}" y2="${arrowY1}" stroke="${INK}" stroke-width="1" stroke-opacity="0.5"/>`;
      out += `<line x1="${(arrowX + 4)}" x2="${arrowX}" y1="${(arrowY1 - 4)}" y2="${arrowY1}" stroke="${INK}" stroke-width="1" stroke-opacity="0.5"/>`;
    }
  }

  // Footer source note
  out += `<text x="${M_L}" y="${(VB_H - 14)}" fill="${INK}" font-family="${FONT_SANS}" font-size="11" font-weight="400" fill-opacity="0.65">Schematic. Coefficients: Devereux, Dong, Tomlin (BoC WP 2015-31); StatCan basket weights (Table 18-10-0007-01, 2024 vintage); headline-CPI step a BoC MPR ballpark, not a citable single coefficient.</text>`;

  out += `</svg>`;
  writeFileSync(resolve(OUT_DIR, "passthrough-cascade.svg"), out, "utf8");
  console.log("wrote passthrough-cascade.svg (schematic, 4 rows)");
}

/* ---------- Chart 6: precedent-2024-25 ---------- */
/* BoC + Fed (left axis, primary BoC solid / Fed dashed) and USDCAD on
   right axis (secondary, dashed). Monthly. Jan 2024 - May 2026. Annotations:
   - BoC first cut: June 2024.
   - Fed first cut: September 2024.
   - BoC 2.25% reached: October 2025.
   - Fed convergence into December 2025. */
function chartPrecedent2024_25() {
  const boc = loadSingleSeries(resolve(ROOT, "data/raw/overnight_rate.csv"));
  let fed = loadSingleSeries(resolve(ROOT, "data/raw/fed_funds.csv"));
  fed = resampleMonthlyLast(fed);
  let fx = loadSingleSeries(resolve(ROOT, "data/raw/usdcad.csv"));
  fx = resampleMonthlyLast(fx);

  const start = "2024-01-01";
  const bocT = filterRange(boc, start);
  const fedT = filterRange(fed, start);
  const fxT = filterRange(fx, start);

  // Common monthly axis from BoC dates.
  const dates = bocT.map((p) => p.date);
  const fedByDate = new Map(fedT.map((p) => [p.date, p.value]));
  const fxByDate = new Map(fxT.map((p) => [p.date, p.value]));
  const bocA = bocT;
  const fedA = dates.map((d) => ({ date: d, value: fedByDate.has(d) ? fedByDate.get(d) : NaN }));
  const fxA = dates.map((d) => ({ date: d, value: fxByDate.has(d) ? fxByDate.get(d) : NaN }));

  const n = dates.length;
  const x = xScaleByIndex(n);

  // Left axis (rates)
  const rateVals = bocA.map((p) => p.value).concat(fedA.map((p) => p.value).filter((v) => !Number.isNaN(v)));
  const rateMin = Math.floor(Math.min(...rateVals) - 0.5);
  const rateMax = Math.ceil(Math.max(...rateVals) + 0.5);
  const yLeft = yScaleRange(rateMin, rateMax, PLOT_Y0, PLOT_Y1);
  const leftTicks = niceTicks(rateMin, rateMax, 4);

  // Right axis (FX)
  const fxVals = fxA.map((p) => p.value).filter((v) => !Number.isNaN(v));
  const fxMin = Math.floor(Math.min(...fxVals) * 100) / 100 - 0.01;
  const fxMax = Math.ceil(Math.max(...fxVals) * 100) / 100 + 0.01;
  const yRight = yScaleRange(fxMin, fxMax, PLOT_Y0, PLOT_Y1);
  const rightTicks = niceTicks(fxMin, fxMax, 3);

  function pathFor(arr, yFn) {
    let d = "";
    let started = false;
    for (let i = 0; i < arr.length; i++) {
      const v = arr[i].value;
      if (Number.isNaN(v)) { started = false; continue; }
      d += (started ? "L" : "M") + x(i).toFixed(2) + " " + yFn(v).toFixed(2) + " ";
      started = true;
    }
    return d.trim();
  }
  const bocD = pathFor(bocA, yLeft);
  const fedD = pathFor(fedA, yLeft);
  const fxD = pathFor(fxA, yRight);

  // Latest dot on BoC
  const bocLastIdx = n - 1;
  const bocLastX = x(bocLastIdx);
  const bocLastY = yLeft(bocA[bocLastIdx].value);

  // Last valid indices for fed and fx
  function lastValidIdx(arr) {
    for (let i = arr.length - 1; i >= 0; i--) if (!Number.isNaN(arr[i].value)) return i;
    return -1;
  }
  const fedLastIdx = lastValidIdx(fedA);
  const fedLastX = x(fedLastIdx);
  const fedLastY = yLeft(fedA[fedLastIdx].value);
  const fxLastIdx = lastValidIdx(fxA);
  const fxLastX = x(fxLastIdx);
  const fxLastY = yRight(fxA[fxLastIdx].value);

  const xTickIdx = [0, Math.floor(n / 3), Math.floor((2 * n) / 3), n - 1];
  const xTickDates = xTickIdx.map((i) => dates[i]);

  let out = "";
  out += `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${VB_W} ${VB_H}" preserveAspectRatio="xMidYMid meet" role="img" aria-label="BoC overnight rate target and Fed funds effective rate on the left axis, and USDCAD on the right axis. Monthly, January 2024 through May 2026. BoC first cut June 2024, Fed first cut September 2024, BoC reached 2.25 percent October 2025, Fed converged into December 2025. Latest BoC reading highlighted in red." style="display:block;width:100%;height:auto;background:${PAPER};font-family:${FONT_SANS}">`;

  // Gridlines
  for (const t of leftTicks) {
    const yy = yLeft(t);
    out += `<line x1="${PLOT_X0}" x2="${PLOT_X1}" y1="${yy.toFixed(2)}" y2="${yy.toFixed(2)}" stroke="${INK}" stroke-opacity="0.18" stroke-width="1"/>`;
  }

  // Annotation bands: vertical date markers
  const annoIdx = (targetDate) => {
    for (let i = 0; i < dates.length; i++) if (dates[i] >= targetDate) return i;
    return -1;
  };
  const annos = [
    { date: "2024-06-01", label: "BoC first cut" },
    { date: "2024-09-01", label: "Fed first cut" },
    { date: "2025-10-01", label: "BoC reaches 2.25%" },
  ];
  for (const a of annos) {
    const ix = annoIdx(a.date);
    if (ix < 0) continue;
    const xx = x(ix);
    out += `<line x1="${xx.toFixed(2)}" x2="${xx.toFixed(2)}" y1="${PLOT_Y0}" y2="${PLOT_Y1}" stroke="${INK}" stroke-width="1" stroke-opacity="0.25" stroke-dasharray="2 3"/>`;
  }

  // FX dashed first (background)
  out += `<path d="${fxD}" stroke="${INK}" stroke-width="1" stroke-dasharray="4 2" fill="none" vector-effect="non-scaling-stroke"/>`;
  // Fed dashed
  out += `<path d="${fedD}" stroke="${INK}" stroke-width="1" stroke-dasharray="1 3" fill="none" vector-effect="non-scaling-stroke"/>`;
  // BoC primary
  out += `<path d="${bocD}" stroke="${INK}" stroke-width="1.5" fill="none" vector-effect="non-scaling-stroke"/>`;

  // Latest BoC dot
  out += `<circle cx="${bocLastX.toFixed(2)}" cy="${bocLastY.toFixed(2)}" r="4" fill="${ACCENT}"><title>BoC: ${fmtMonthShort(bocA[bocLastIdx].date)} ${bocA[bocLastIdx].value.toFixed(2)}%</title></circle>`;

  // Frame
  out += `<rect x="${PLOT_X0}" y="${PLOT_Y0}" width="${PLOT_W}" height="${PLOT_H}" fill="none" stroke="${INK}" stroke-width="1"/>`;

  // Left y-ticks
  const leftTop = leftTicks[leftTicks.length - 1];
  for (const t of leftTicks) {
    const yy = yLeft(t);
    const lbl = (t === leftTop) ? `${t.toFixed(0)}%` : t.toFixed(0);
    out += `<text x="${(PLOT_X0 - 8).toFixed(2)}" y="${(yy + 4).toFixed(2)}" text-anchor="end" fill="${INK}" font-family="${FONT_MONO}" font-size="12" font-weight="400" font-variant-numeric="tabular-nums">${svgEscape(lbl)}</text>`;
  }
  // Right y-ticks (FX)
  const rightTop = rightTicks[rightTicks.length - 1];
  for (const t of rightTicks) {
    const yy = yRight(t);
    const lbl = (t === rightTop) ? `${t.toFixed(2)} CAD` : t.toFixed(2);
    out += `<text x="${(PLOT_X1 + 8).toFixed(2)}" y="${(yy + 4).toFixed(2)}" text-anchor="start" fill="${INK}" font-family="${FONT_MONO}" font-size="12" font-weight="400" font-variant-numeric="tabular-nums" fill-opacity="0.7">${svgEscape(lbl)}</text>`;
  }
  // X-ticks
  for (let k = 0; k < xTickIdx.length; k++) {
    const ix = xTickIdx[k];
    const xx = x(ix);
    const label = fmtMonthShort(xTickDates[k]);
    const anchor = (k === 0) ? "start" : (k === xTickIdx.length - 1) ? "end" : "middle";
    out += `<text x="${xx.toFixed(2)}" y="${(PLOT_Y1 + 18).toFixed(2)}" text-anchor="${anchor}" fill="${INK}" font-family="${FONT_SANS}" font-size="12" font-weight="400">${svgEscape(label)}</text>`;
  }

  // Annotation labels at top of plot
  for (const a of annos) {
    const ix = annoIdx(a.date);
    if (ix < 0) continue;
    const xx = x(ix);
    // Stack the label inside the plot, near top, rotated upright
    out += `<text x="${(xx + 4).toFixed(2)}" y="${(PLOT_Y0 + 12).toFixed(2)}" fill="${INK}" font-family="${FONT_SANS}" font-size="11" font-weight="500" fill-opacity="0.75">${svgEscape(a.label)}</text>`;
  }

  // Direct labels
  const labels = [
    { x: bocLastX, y: bocLastY, text: "BoC", weight: 600 },
    { x: fedLastX, y: fedLastY, text: "Fed", weight: 400 },
    { x: fxLastX, y: fxLastY, text: "USDCAD", weight: 400 },
  ];
  labels.sort((a, b) => a.y - b.y);
  for (let i = 1; i < labels.length; i++) {
    if (labels[i].y - labels[i - 1].y < 14) labels[i].y = labels[i - 1].y + 14;
  }
  for (const lab of labels) {
    const lx = Math.min(lab.x + 10, PLOT_X1 + M_R - 4);
    out += `<text x="${lx.toFixed(2)}" y="${(lab.y + 4).toFixed(2)}" fill="${INK}" font-family="${FONT_SANS}" font-size="13" font-weight="${lab.weight}">${svgEscape(lab.text)}</text>`;
  }

  out += `</svg>`;
  writeFileSync(resolve(OUT_DIR, "precedent-2024-25.svg"), out, "utf8");
  console.log("wrote precedent-2024-25.svg (", n, "months; latest BoC", bocA[bocLastIdx].date, bocA[bocLastIdx].value.toFixed(2), "; Fed last", fedA[fedLastIdx].value.toFixed(2), "; FX last", fxA[fxLastIdx].value.toFixed(4), ")");
}

/* ---------- run ---------- */
chartPolicyRateDivergence();
chart2ySpreadPercentile();
chartUsdcadVs2ySpread();
chartExpectationsAnchor();
chartPassthroughCascade();
chartPrecedent2024_25();
console.log("Pillar B charts written to", OUT_DIR);
