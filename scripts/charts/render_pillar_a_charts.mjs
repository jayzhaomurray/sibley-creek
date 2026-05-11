/*
 * render_pillar_a_charts.mjs
 *
 * Pre-renders the three Pillar A deep-dive illustrative charts as static
 * SVG files under public/charts/pillar-a/. Run once, ship the SVGs as
 * static assets; reference from the v5 markdown body via standard image
 * syntax.
 *
 * Charts:
 *   1) mic_yoy.svg            -- CPI mortgage interest cost Y/Y, last ~36 months.
 *   2) cba_arrears.svg        -- CBA chartered-bank national arrears rate, monthly.
 *   3) unemployment.svg       -- Headline unemployment + prime-age overlay.
 *
 * Canon (Tier-3): 720x405 viewBox, pure ink line 1.5px, MTA red 4px latest dot,
 * Plex Mono 12px y-ticks, Manrope 12px x-ticks, 4 gridlines @ 0.18 opacity,
 * 1px hairline plot frame. Single-line direct label at line terminus.
 *
 * Standalone Node ESM script. No npm deps. Run:
 *   node scripts/charts/render_pillar_a_charts.mjs
 */

import { readFileSync, writeFileSync, mkdirSync, existsSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const ROOT = resolve(__dirname, "..", "..");
const OUT_DIR = resolve(ROOT, "public", "charts", "pillar-a");

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

/* ---------- helpers ---------- */
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
      } else {
        cur += ch;
      }
    } else {
      if (ch === '"') inQuote = true;
      else if (ch === ',') { out.push(cur); cur = ""; }
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
    const parts = parseCsvLine(lines[i]);
    rows.push(parts);
  }
  return { header, rows };
}

function pickColumn(csvObj, colName) {
  const idx = csvObj.header.indexOf(colName);
  if (idx === -1) throw new Error(`Column ${colName} not found`);
  return csvObj.rows
    .map((r) => ({ date: r[0], value: r[idx] }))
    .filter((p) => p.value !== "" && p.value != null && !Number.isNaN(parseFloat(p.value)))
    .map((p) => ({ date: p.date, value: parseFloat(p.value) }));
}

function loadSingleSeries(path) {
  const c = readCsv(path);
  return c.rows
    .map((r) => ({ date: r[0], value: r[1] }))
    .filter((p) => p.value !== "" && p.value != null && !Number.isNaN(parseFloat(p.value)))
    .map((p) => ({ date: p.date, value: parseFloat(p.value) }));
}

/* Compute Y/Y percent change for a monthly series. */
function yoyMonthly(series) {
  const byDate = new Map(series.map((p) => [p.date, p.value]));
  const out = [];
  for (const p of series) {
    const [y, m, d] = p.date.split("-").map((s) => parseInt(s, 10));
    const priorDate = `${y - 1}-${String(m).padStart(2, "0")}-${String(d).padStart(2, "0")}`;
    const prior = byDate.get(priorDate);
    if (prior == null) continue;
    out.push({ date: p.date, value: ((p.value / prior) - 1) * 100 });
  }
  return out;
}

function filterRange(series, startDate) {
  return series.filter((p) => p.date >= startDate);
}

function fmtMonthShort(d) {
  const months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
  const [y, m] = d.split("-").map((s) => parseInt(s, 10));
  return `${months[m - 1]} ${y}`;
}

/* Scale builders. */
function xScaleByIndex(n) {
  return (i) => PLOT_X0 + (i / Math.max(1, n - 1)) * PLOT_W;
}
function yScale(yMin, yMax) {
  return (v) => PLOT_Y1 - ((v - yMin) / (yMax - yMin)) * PLOT_H;
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

function svgEscape(s) {
  return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

/* ---------- generic single-line chart renderer ---------- */
function renderLineChart({
  series,           // array of {date, value}
  yUnit = "%",
  yDecimals = 1,
  yTicks,           // optional explicit ticks
  yMin,             // optional explicit y-min
  yMax,             // optional explicit y-max
  directLabel,      // string at line terminus
  ariaLabel,
  secondarySeries,  // optional array of {date, value} (must align by index)
  secondaryLabel,
  zeroLine = false,
}) {
  const n = series.length;
  const x = xScaleByIndex(n);
  const allVals = series.map((p) => p.value).concat(
    secondarySeries ? secondarySeries.map((p) => p.value) : []
  );
  const dataMin = Math.min(...allVals);
  const dataMax = Math.max(...allVals);
  const padding = (dataMax - dataMin) * 0.12 || 1;
  const ymin = yMin != null ? yMin : dataMin - padding;
  const ymax = yMax != null ? yMax : dataMax + padding;
  const y = yScale(ymin, ymax);

  const ticks = yTicks || niceTicks(ymin, ymax, 4);

  // X-tick positions: 4 ticks (start, ~1/3, ~2/3, end) by index
  const xTickIdx = [0, Math.floor(n / 3), Math.floor((2 * n) / 3), n - 1];
  const xTickDates = xTickIdx.map((i) => series[i].date);

  // Build path d for primary
  let primaryD = "";
  for (let i = 0; i < n; i++) {
    primaryD += (i === 0 ? "M" : "L") + x(i).toFixed(2) + " " + y(series[i].value).toFixed(2) + " ";
  }
  let secondaryD = "";
  if (secondarySeries) {
    for (let i = 0; i < secondarySeries.length; i++) {
      secondaryD += (i === 0 ? "M" : "L") + x(i).toFixed(2) + " " + y(secondarySeries[i].value).toFixed(2) + " ";
    }
  }

  const lastIdx = n - 1;
  const lastX = x(lastIdx);
  const lastY = y(series[lastIdx].value);

  // y-tick labels: topmost carries unit suffix
  const topmost = ticks[ticks.length - 1];
  function fmtY(v, withUnit) {
    const s = v.toFixed(yDecimals);
    return withUnit ? `${s}${yUnit}` : s;
  }

  // Build SVG
  let out = "";
  out += `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${VB_W} ${VB_H}" preserveAspectRatio="xMidYMid meet" role="img" aria-label="${svgEscape(ariaLabel)}" style="display:block;width:100%;height:auto;background:${PAPER};font-family:${FONT_SANS}">`;

  // Gridlines
  for (const t of ticks) {
    const yy = y(t);
    out += `<line x1="${PLOT_X0}" x2="${PLOT_X1}" y1="${yy.toFixed(2)}" y2="${yy.toFixed(2)}" stroke="${INK}" stroke-opacity="0.18" stroke-width="1"/>`;
  }
  // Zero line if requested and within range
  if (zeroLine && 0 >= ymin && 0 <= ymax) {
    const zy = y(0);
    out += `<line x1="${PLOT_X0}" x2="${PLOT_X1}" y1="${zy.toFixed(2)}" y2="${zy.toFixed(2)}" stroke="${INK}" stroke-opacity="1" stroke-width="1"/>`;
  }

  // Secondary line (1px dashed pure ink) -- draw BEFORE primary so primary sits on top
  if (secondarySeries) {
    out += `<path d="${secondaryD.trim()}" stroke="${INK}" stroke-width="1" stroke-dasharray="4 2" fill="none" vector-effect="non-scaling-stroke"/>`;
  }

  // Primary line
  out += `<path d="${primaryD.trim()}" stroke="${INK}" stroke-width="1.5" fill="none" vector-effect="non-scaling-stroke"/>`;

  // Latest-print dot (primary only)
  out += `<circle cx="${lastX.toFixed(2)}" cy="${lastY.toFixed(2)}" r="4" fill="${ACCENT}"><title>Latest: ${fmtMonthShort(series[lastIdx].date)} ${series[lastIdx].value.toFixed(yDecimals)}${yUnit}</title></circle>`;

  // Plot frame (after data per canon z-order)
  out += `<rect x="${PLOT_X0}" y="${PLOT_Y0}" width="${PLOT_W}" height="${PLOT_H}" fill="none" stroke="${INK}" stroke-width="1"/>`;

  // Y-tick labels (Plex Mono 12px, right-aligned in left gutter)
  for (const t of ticks) {
    const yy = y(t);
    const lbl = (t === topmost) ? fmtY(t, true) : fmtY(t, false);
    out += `<text x="${(PLOT_X0 - 8).toFixed(2)}" y="${(yy + 4).toFixed(2)}" text-anchor="end" fill="${INK}" font-family="${FONT_MONO}" font-size="12" font-weight="400" font-variant-numeric="tabular-nums">${svgEscape(lbl)}</text>`;
  }

  // X-tick labels (Manrope 12px)
  for (let k = 0; k < xTickIdx.length; k++) {
    const ix = xTickIdx[k];
    const xx = x(ix);
    const label = fmtMonthShort(xTickDates[k]);
    const anchor = (k === 0) ? "start" : (k === xTickIdx.length - 1) ? "end" : "middle";
    out += `<text x="${xx.toFixed(2)}" y="${(PLOT_Y1 + 18).toFixed(2)}" text-anchor="${anchor}" fill="${INK}" font-family="${FONT_SANS}" font-size="12" font-weight="400">${svgEscape(label)}</text>`;
  }

  // Direct end-of-line label (primary) -- Manrope 600 13px
  const labelX = Math.min(lastX + 10, PLOT_X1 + M_R - 4);
  out += `<text x="${labelX.toFixed(2)}" y="${(lastY + 4).toFixed(2)}" fill="${INK}" font-family="${FONT_SANS}" font-size="13" font-weight="600">${svgEscape(directLabel)}</text>`;

  // Secondary direct label if applicable (Manrope 400 13px, last point of secondary)
  if (secondarySeries && secondaryLabel) {
    const secLastX = x(secondarySeries.length - 1);
    const secLastY = y(secondarySeries[secondarySeries.length - 1].value);
    // Stack if too close to primary label baseline
    let labelY = secLastY + 4;
    if (Math.abs((secLastY + 4) - (lastY + 4)) < 12) {
      // place below primary
      labelY = (lastY + 4) + 14;
    }
    const secX = Math.min(secLastX + 10, PLOT_X1 + M_R - 4);
    out += `<text x="${secX.toFixed(2)}" y="${labelY.toFixed(2)}" fill="${INK}" font-family="${FONT_SANS}" font-size="13" font-weight="400">${svgEscape(secondaryLabel)}</text>`;
  }

  out += `</svg>`;
  return out;
}

/* ---------- Chart 1: MIC Y/Y ---------- */
function chartMicYoy() {
  const cpiComponents = readCsv(resolve(ROOT, "data/raw/cpi_components.csv"));
  const mic = pickColumn(cpiComponents, "Mortgage interest cost");
  const yoy = yoyMonthly(mic);
  // Last ~48 months for editorial context (covers peak in 2023-24 and fade to 2026)
  const cutoff = "2022-04-01";
  const trimmed = filterRange(yoy, cutoff);

  const svg = renderLineChart({
    series: trimmed,
    yUnit: "%",
    yDecimals: 1,
    yMin: -1,
    yMax: Math.max(10, Math.ceil(Math.max(...trimmed.map((p) => p.value)) / 2) * 2),
    directLabel: "MIC Y/Y",
    ariaLabel: "CPI mortgage interest cost, year-over-year percent change, monthly, last 48 months ending March 2026. Latest print highlighted in red.",
    zeroLine: true,
  });
  writeFileSync(resolve(OUT_DIR, "mic_yoy.svg"), svg, "utf8");
  console.log("wrote mic_yoy.svg (", trimmed.length, "points, latest:", trimmed[trimmed.length - 1].date, trimmed[trimmed.length - 1].value.toFixed(2), "%)");
}

/* ---------- Chart 2: CBA national arrears ---------- */
function chartCbaArrears() {
  const series = loadSingleSeries(resolve(ROOT, "data/raw/cba_mortgage_arrears_national.csv"));
  // Last 36 months for context
  const cutoff = "2023-03-01";
  const trimmed = filterRange(series, cutoff);
  const svg = renderLineChart({
    series: trimmed,
    yUnit: "%",
    yDecimals: 2,
    yMin: 0.12,
    yMax: 0.32,
    directLabel: "Arrears rate",
    ariaLabel: "CBA chartered-bank national mortgage arrears rate, monthly, last 36 months ending February 2026. Latest print highlighted in red.",
  });
  writeFileSync(resolve(OUT_DIR, "cba_arrears.svg"), svg, "utf8");
  console.log("wrote cba_arrears.svg (", trimmed.length, "points, latest:", trimmed[trimmed.length - 1].date, trimmed[trimmed.length - 1].value.toFixed(2), "%)");
}

/* ---------- Chart 3: Unemployment + prime-age overlay ---------- */
function chartUnemployment() {
  const ur = loadSingleSeries(resolve(ROOT, "data/raw/unemployment_rate.csv"));
  const pa = loadSingleSeries(resolve(ROOT, "data/raw/prime_age_unemployment_rate.csv"));
  // Align by date intersect, last 60 months
  const cutoff = "2021-04-01";
  const urT = filterRange(ur, cutoff);
  const paT = filterRange(pa, cutoff);
  // Inner-join by date
  const paByDate = new Map(paT.map((p) => [p.date, p.value]));
  const aligned = urT.filter((p) => paByDate.has(p.date));
  const paAligned = aligned.map((p) => ({ date: p.date, value: paByDate.get(p.date) }));

  const svg = renderLineChart({
    series: aligned,
    secondarySeries: paAligned,
    yUnit: "%",
    yDecimals: 1,
    yMin: 4,
    yMax: 9,
    directLabel: "Headline U/E",
    secondaryLabel: "Prime-age (25-54)",
    ariaLabel: "Canada unemployment rate, monthly, with prime-age (25-54) overlay, last 60 months ending April 2026. Latest headline print highlighted in red.",
  });
  writeFileSync(resolve(OUT_DIR, "unemployment.svg"), svg, "utf8");
  console.log("wrote unemployment.svg (", aligned.length, "points, latest:", aligned[aligned.length - 1].date, aligned[aligned.length - 1].value.toFixed(1), "%; prime", paAligned[paAligned.length - 1].value.toFixed(1), "%)");
}

/* ---------- run ---------- */
chartMicYoy();
chartCbaArrears();
chartUnemployment();
console.log("Pillar A charts written to", OUT_DIR);
