/*
 * render_pillar_e_charts.mjs
 *
 * Pre-renders the five Pillar E deep-dive illustrative charts as static
 * SVG files under public/charts/pillar-e/. Run once, ship the SVGs as
 * static assets; reference from the v1 markdown draft via standard image
 * syntax.
 *
 * Charts:
 *   1) divergence_opens_closes.svg      -- emp rate Y/Y vs total emp Y/Y, monthly.
 *   2) npr_wave.svg                     -- total population Y/Y trajectory, quarterly.
 *   3) youth_carries_participation.svg  -- youth vs prime-age participation, indexed to Dec-19 = 0.
 *   4) denominator_not_productivity.svg -- productivity Y/Y vs per-capita real GDP Y/Y, quarterly.
 *   5) scenarios_2027.svg               -- emp/pop historical + 2 illustrative scenarios through 2027.
 *
 * Canon (Tier-3): 720x405 viewBox, pure ink line 1.5px, MTA red 4px latest dot,
 * Plex Mono 12px y-ticks, Manrope 12px x-ticks, gridlines @ 0.18 opacity,
 * 1px hairline plot frame. Direct end-of-line label per series.
 *
 * Standalone Node ESM script. No npm deps. Run:
 *   node scripts/charts/render_pillar_e_charts.mjs
 */

import { readFileSync, writeFileSync, mkdirSync, existsSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const ROOT = resolve(__dirname, "..", "..");
const OUT_DIR = resolve(ROOT, "public", "charts", "pillar-e");

if (!existsSync(OUT_DIR)) mkdirSync(OUT_DIR, { recursive: true });

/* ---------- canon constants ---------- */
const VB_W = 720;
const VB_H = 405;
const M_L = 56;
const M_R = 110;   // slightly wider right gutter to comfortably seat 2-line direct labels
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
      } else cur += ch;
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
  for (let i = 1; i < lines.length; i++) rows.push(parseCsvLine(lines[i]));
  return { header, rows };
}

function loadSingleSeries(path) {
  const c = readCsv(path);
  return c.rows
    .map((r) => ({ date: r[0], value: r[1] }))
    .filter((p) => p.value !== "" && p.value != null && !Number.isNaN(parseFloat(p.value)))
    .map((p) => ({ date: p.date, value: parseFloat(p.value) }));
}

/* Compute Y/Y percent change for a monthly series (looks back 12 months by date). */
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

/* Compute Y/Y percent change for a quarterly series (looks back 4 quarters by date). */
function yoyQuarterly(series) {
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

function filterRange(series, startDate, endDate) {
  return series.filter((p) => p.date >= startDate && (endDate == null || p.date <= endDate));
}

function fmtMonthShort(d) {
  const months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
  const [y, m] = d.split("-").map((s) => parseInt(s, 10));
  return `${months[m - 1]} ${y}`;
}

function fmtQuarterShort(d) {
  const [y, m] = d.split("-").map((s) => parseInt(s, 10));
  const q = Math.floor((m - 1) / 3) + 1;
  return `Q${q} ${y}`;
}

function fmtYearOnly(d) {
  return d.split("-")[0];
}

/* dateToFractionalYear: maps "YYYY-MM-DD" to a decimal year for time-based x-scale. */
function dateToFractionalYear(d) {
  const [y, m] = d.split("-").map((s) => parseInt(s, 10));
  return y + (m - 1) / 12;
}

function svgEscape(s) {
  return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
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

/* ---------- time-axis chart renderer (continuous x = fractional year) ---------- */
function renderTimeChart({
  primary,            // array of {date, value}
  secondary,          // optional secondary {date, value}
  xMin, xMax,         // fractional-year bounds
  yMin, yMax,
  yUnit = "%",
  yDecimals = 1,
  yTicks,             // optional explicit ticks
  xTickYears,         // optional explicit array of years (integer) to label
  primaryLabel,
  secondaryLabel,
  primaryShowDot = true,     // whether to draw MTA red dot at latest primary point
  zeroLine = false,
  ariaLabel,
  forwardSegments = [],      // optional array of {points, label} -> rendered as dashed forward extension
  refRule,                   // optional {value, label} -> horizontal dashed reference line
  recessionBand,             // optional {x0, x1, label} -> shaded band in fractional-year coords
}) {
  const xScale = (fy) => PLOT_X0 + ((fy - xMin) / (xMax - xMin)) * PLOT_W;
  const yScale = (v) => PLOT_Y1 - ((v - yMin) / (yMax - yMin)) * PLOT_H;

  const ticks = yTicks || niceTicks(yMin, yMax, 4);
  const topmost = ticks[ticks.length - 1];
  const fmtY = (v, withUnit) => {
    const s = v.toFixed(yDecimals);
    return withUnit ? `${s}${yUnit}` : s;
  };

  function pathOf(points) {
    let d = "";
    for (let i = 0; i < points.length; i++) {
      const p = points[i];
      const x = xScale(dateToFractionalYear(p.date));
      const y = yScale(p.value);
      d += (i === 0 ? "M" : "L") + x.toFixed(2) + " " + y.toFixed(2) + " ";
    }
    return d.trim();
  }

  let out = "";
  out += `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${VB_W} ${VB_H}" preserveAspectRatio="xMidYMid meet" role="img" aria-label="${svgEscape(ariaLabel)}" style="display:block;width:100%;height:auto;background:${PAPER};font-family:${FONT_SANS}">`;

  // Recession / shaded band (drawn first, behind everything)
  if (recessionBand) {
    const bx0 = xScale(recessionBand.x0);
    const bx1 = xScale(recessionBand.x1);
    out += `<rect x="${bx0.toFixed(2)}" y="${PLOT_Y0}" width="${(bx1 - bx0).toFixed(2)}" height="${PLOT_H}" fill="${INK}" fill-opacity="0.06"/>`;
    if (recessionBand.label) {
      out += `<text x="${((bx0 + bx1) / 2).toFixed(2)}" y="${(PLOT_Y0 + 14).toFixed(2)}" text-anchor="middle" fill="${INK}" font-family="${FONT_SANS}" font-size="11" font-weight="600" letter-spacing="0.18em" style="text-transform:uppercase">${svgEscape(recessionBand.label)}</text>`;
    }
  }

  // Gridlines
  for (const t of ticks) {
    const yy = yScale(t);
    out += `<line x1="${PLOT_X0}" x2="${PLOT_X1}" y1="${yy.toFixed(2)}" y2="${yy.toFixed(2)}" stroke="${INK}" stroke-opacity="0.18" stroke-width="1"/>`;
  }

  // Zero line if requested and within range
  if (zeroLine && 0 >= yMin && 0 <= yMax) {
    const zy = yScale(0);
    out += `<line x1="${PLOT_X0}" x2="${PLOT_X1}" y1="${zy.toFixed(2)}" y2="${zy.toFixed(2)}" stroke="${INK}" stroke-opacity="1" stroke-width="1"/>`;
  }

  // Reference rule (dashed pure-ink horizontal)
  if (refRule) {
    const ry = yScale(refRule.value);
    out += `<line x1="${PLOT_X0}" x2="${PLOT_X1}" y1="${ry.toFixed(2)}" y2="${ry.toFixed(2)}" stroke="${INK}" stroke-width="1" stroke-dasharray="4 2"/>`;
    if (refRule.label) {
      out += `<text x="${(PLOT_X1 - 6).toFixed(2)}" y="${(ry - 5).toFixed(2)}" text-anchor="end" fill="${INK}" font-family="${FONT_SANS}" font-size="12" font-weight="600">${svgEscape(refRule.label)}</text>`;
    }
  }

  // Secondary line (1px dashed pure ink), drawn BEFORE primary
  if (secondary) {
    out += `<path d="${pathOf(secondary)}" stroke="${INK}" stroke-width="1" stroke-dasharray="4 2" fill="none" vector-effect="non-scaling-stroke"/>`;
  }

  // Primary line
  out += `<path d="${pathOf(primary)}" stroke="${INK}" stroke-width="1.5" fill="none" vector-effect="non-scaling-stroke"/>`;

  // Optional forward segments (dashed continuation, no dot)
  for (const seg of forwardSegments) {
    out += `<path d="${pathOf(seg.points)}" stroke="${INK}" stroke-width="1" stroke-dasharray="2 3" fill="none" vector-effect="non-scaling-stroke"/>`;
  }

  // Latest-print dot (primary only, optional)
  const lastP = primary[primary.length - 1];
  const lastX = xScale(dateToFractionalYear(lastP.date));
  const lastY = yScale(lastP.value);
  if (primaryShowDot) {
    out += `<circle cx="${lastX.toFixed(2)}" cy="${lastY.toFixed(2)}" r="4" fill="${ACCENT}"><title>Latest: ${fmtMonthShort(lastP.date)} ${lastP.value.toFixed(yDecimals)}${yUnit}</title></circle>`;
  }

  // Plot frame
  out += `<rect x="${PLOT_X0}" y="${PLOT_Y0}" width="${PLOT_W}" height="${PLOT_H}" fill="none" stroke="${INK}" stroke-width="1"/>`;

  // Y-tick labels (Plex Mono 12px right-aligned in left gutter)
  for (const t of ticks) {
    const yy = yScale(t);
    const lbl = (t === topmost) ? fmtY(t, true) : fmtY(t, false);
    out += `<text x="${(PLOT_X0 - 8).toFixed(2)}" y="${(yy + 4).toFixed(2)}" text-anchor="end" fill="${INK}" font-family="${FONT_MONO}" font-size="12" font-weight="400" font-variant-numeric="tabular-nums">${svgEscape(lbl)}</text>`;
  }

  // X-tick labels (Manrope 12px, integer years)
  for (let k = 0; k < xTickYears.length; k++) {
    const yr = xTickYears[k];
    const xx = xScale(yr);
    if (xx < PLOT_X0 - 1 || xx > PLOT_X1 + 1) continue;
    let anchor = "middle";
    if (k === 0) anchor = "start";
    else if (k === xTickYears.length - 1) anchor = "end";
    out += `<text x="${xx.toFixed(2)}" y="${(PLOT_Y1 + 18).toFixed(2)}" text-anchor="${anchor}" fill="${INK}" font-family="${FONT_SANS}" font-size="12" font-weight="400">${yr}</text>`;
  }

  // Direct labels at line terminus
  // Primary at end of primary series
  if (primaryLabel) {
    const labelX = Math.min(lastX + 10, VB_W - 4);
    out += `<text x="${labelX.toFixed(2)}" y="${(lastY + 4).toFixed(2)}" fill="${INK}" font-family="${FONT_SANS}" font-size="13" font-weight="600">${svgEscape(primaryLabel)}</text>`;
  }
  // Secondary at end of secondary series
  if (secondary && secondaryLabel) {
    const sLast = secondary[secondary.length - 1];
    const sx = xScale(dateToFractionalYear(sLast.date));
    const sy = yScale(sLast.value);
    let labelY = sy + 4;
    if (Math.abs((sy + 4) - (lastY + 4)) < 14) {
      // stack secondary either above or below primary depending on which is higher
      if (sy < lastY) labelY = (lastY + 4) - 14;
      else labelY = (lastY + 4) + 14;
    }
    const labelX = Math.min(sx + 10, VB_W - 4);
    out += `<text x="${labelX.toFixed(2)}" y="${labelY.toFixed(2)}" fill="${INK}" font-family="${FONT_SANS}" font-size="13" font-weight="400">${svgEscape(secondaryLabel)}</text>`;
  }
  // Forward-segment direct labels
  for (const seg of forwardSegments) {
    if (!seg.label) continue;
    const segLast = seg.points[seg.points.length - 1];
    const sx = xScale(dateToFractionalYear(segLast.date));
    const sy = yScale(segLast.value);
    const labelX = Math.min(sx + 8, VB_W - 4);
    out += `<text x="${labelX.toFixed(2)}" y="${(sy + 4).toFixed(2)}" fill="${INK}" font-family="${FONT_SANS}" font-size="12" font-weight="${seg.weight || 400}">${svgEscape(seg.label)}</text>`;
  }

  out += `</svg>`;
  return out;
}

/* ---------- Chart 1: divergence opens & closes ---------- */
function chartDivergence() {
  // Two series, both Y/Y % monthly: total employment Y/Y (primary, the headline)
  // vs employment rate Y/Y (secondary, the per-capita read). Window Jan 2020 - Apr 2026.
  const empRate = loadSingleSeries(resolve(ROOT, "data/raw/employment_rate.csv"));
  const empLevel = loadSingleSeries(resolve(ROOT, "data/raw/lf_employment_prime.csv"));
  // Use unemployment_level inverted? Actually we want TOTAL employment. lf_employment_prime is prime-age only.
  // Better: construct total employment level from emp_rate * population. But pop is quarterly.
  // Simpler / more faithful to draft: render emp rate Y/Y (per-capita read) as PRIMARY
  // (the editorial argument is about the per-capita series), and total employment Y/Y as SECONDARY.
  // Total employment Y/Y is reasonably proxied by employment level if available; we use
  // emp_rate * pop_total to construct a monthly total employment level. Pop is quarterly,
  // so forward-fill quarterly pop to monthly.
  const popQ = loadSingleSeries(resolve(ROOT, "data/raw/pop_total.csv"));
  // forward-fill monthly: for each emp_rate date, find latest popQ on or before it.
  const popSorted = popQ.slice().sort((a, b) => a.date.localeCompare(b.date));
  function popOnOrBefore(d) {
    let last = null;
    for (const p of popSorted) {
      if (p.date <= d) last = p; else break;
    }
    return last ? last.value : null;
  }
  const totalEmp = empRate
    .map((p) => {
      const pp = popOnOrBefore(p.date);
      return pp == null ? null : { date: p.date, value: (p.value / 100) * pp };
    })
    .filter(Boolean);

  const empRateYoy = yoyMonthly(empRate);
  const totalEmpYoy = yoyMonthly(totalEmp);

  const cutoff = "2020-01-01";
  const primary = filterRange(empRateYoy, cutoff);    // per-capita read (employment rate)
  const secondary = filterRange(totalEmpYoy, cutoff); // headline (total employment)

  // Align endpoints
  const minLast = (primary[primary.length - 1].date < secondary[secondary.length - 1].date)
    ? primary[primary.length - 1].date : secondary[secondary.length - 1].date;
  const pTrim = primary.filter((p) => p.date <= minLast);
  const sTrim = secondary.filter((p) => p.date <= minLast);

  // Determine x range
  const xMin = dateToFractionalYear(pTrim[0].date);
  const xMax = dateToFractionalYear(pTrim[pTrim.length - 1].date) + 0.05;

  // Y range: bracket data with rounded bounds
  const allVals = pTrim.concat(sTrim).map((p) => p.value);
  let yMin = Math.floor(Math.min(...allVals) - 0.5);
  let yMax = Math.ceil(Math.max(...allVals) + 0.5);
  // Cap COVID rebound spike (Apr-21 ~+13%) so the editorial story (2023-26 divergence)
  // reads at scale. The COVID rebound is editorially incidental; clip via window start.
  // Move cutoff to Jan 2022 to drop COVID-rebound spike and put focus on divergence.
  const cutoff2 = "2022-01-01";
  const pTrim2 = pTrim.filter((p) => p.date >= cutoff2);
  const sTrim2 = sTrim.filter((p) => p.date >= cutoff2);
  const xMin2 = dateToFractionalYear(pTrim2[0].date);
  const xMax2 = dateToFractionalYear(pTrim2[pTrim2.length - 1].date) + 0.1;
  const allVals2 = pTrim2.concat(sTrim2).map((p) => p.value);
  yMin = Math.floor(Math.min(...allVals2) - 0.3);
  yMax = Math.ceil(Math.max(...allVals2) + 0.5);

  const svg = renderTimeChart({
    primary: pTrim2,
    secondary: sTrim2,
    xMin: xMin2,
    xMax: xMax2,
    yMin, yMax,
    yUnit: "%",
    yDecimals: 1,
    xTickYears: [2022, 2023, 2024, 2025, 2026],
    primaryLabel: "Emp. rate Y/Y",
    secondaryLabel: "Total emp. Y/Y",
    zeroLine: true,
    ariaLabel: "Year-over-year percent change in Canada's employment rate (per-capita read) and total employment (headline read), monthly, January 2022 through April 2026. The gap between the two series widened through 2023 to 2024 and is closing in 2025 to 2026. Latest employment-rate Y/Y print highlighted in red.",
  });
  writeFileSync(resolve(OUT_DIR, "divergence_opens_closes.svg"), svg, "utf8");
  console.log("wrote divergence_opens_closes.svg (primary points:", pTrim2.length, ", latest emp-rate Y/Y:", pTrim2[pTrim2.length - 1].value.toFixed(2), "%, total-emp Y/Y:", sTrim2[sTrim2.length - 1].value.toFixed(2), "%)");
}

/* ---------- Chart 2: NPR wave / population Y/Y ---------- */
function chartNprWave() {
  // Single-series: total population Y/Y, quarterly, 2019Q1 through Q1 2026.
  // Shows the peak at 3.18% (Q2 2024) and contraction to -0.25% (Q1 2026).
  const popQ = loadSingleSeries(resolve(ROOT, "data/raw/pop_total.csv"));
  const yoy = yoyQuarterly(popQ);
  const cutoff = "2019-01-01";
  const trimmed = filterRange(yoy, cutoff);

  const xMin = dateToFractionalYear(trimmed[0].date);
  const xMax = dateToFractionalYear(trimmed[trimmed.length - 1].date) + 0.2;

  const svg = renderTimeChart({
    primary: trimmed,
    xMin, xMax,
    yMin: -1, yMax: 4,
    yUnit: "%",
    yDecimals: 1,
    xTickYears: [2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026],
    primaryLabel: "Pop. Y/Y",
    zeroLine: true,
    ariaLabel: "Canada total population year-over-year percent change, quarterly, 2019Q1 through 2026Q1. Series peaks at 3.18 percent in 2024Q2 and falls to negative 0.25 percent in 2026Q1, the first multi-quarter contraction in the post-war series. Latest print highlighted in red.",
  });
  writeFileSync(resolve(OUT_DIR, "npr_wave.svg"), svg, "utf8");
  console.log("wrote npr_wave.svg (", trimmed.length, "points, latest:", trimmed[trimmed.length - 1].date, trimmed[trimmed.length - 1].value.toFixed(2), "%)");
}

/* ---------- Chart 3: Youth carries participation ---------- */
function chartYouthParticipation() {
  // Two series: prime-age participation and youth participation, both indexed to Dec 2019 = 0
  // in percentage points. Monthly, Jan 2019 - Apr 2026. Primary = youth (the editorial
  // anchor series); secondary = prime-age (the negative-space counterpoint).
  const prime = loadSingleSeries(resolve(ROOT, "data/raw/lf_participation_prime.csv"));
  const youth = loadSingleSeries(resolve(ROOT, "data/raw/lf_participation_youth.csv"));

  function indexToBase(series, baseDate) {
    const base = series.find((p) => p.date === baseDate);
    if (!base) throw new Error("base not found: " + baseDate);
    return series.map((p) => ({ date: p.date, value: p.value - base.value }));
  }

  const primeIx = indexToBase(prime, "2019-12-01");
  const youthIx = indexToBase(youth, "2019-12-01");
  const cutoff = "2019-01-01";
  const primary = filterRange(youthIx, cutoff);
  const secondary = filterRange(primeIx, cutoff);

  // Align endpoint
  const minLast = (primary[primary.length - 1].date < secondary[secondary.length - 1].date)
    ? primary[primary.length - 1].date : secondary[secondary.length - 1].date;
  const pTrim = primary.filter((p) => p.date <= minLast);
  const sTrim = secondary.filter((p) => p.date <= minLast);

  const xMin = dateToFractionalYear(pTrim[0].date);
  const xMax = dateToFractionalYear(pTrim[pTrim.length - 1].date) + 0.1;

  // Sep-23 student-permit cap shading
  const x0Band = dateToFractionalYear("2023-09-01");
  const x1Band = dateToFractionalYear(pTrim[pTrim.length - 1].date);

  const allVals = pTrim.concat(sTrim).map((p) => p.value);
  const yMin = Math.floor(Math.min(...allVals) - 0.5);
  const yMax = Math.ceil(Math.max(...allVals) + 0.5);

  const svg = renderTimeChart({
    primary: pTrim,
    secondary: sTrim,
    xMin, xMax,
    yMin, yMax,
    yUnit: "pp",
    yDecimals: 1,
    xTickYears: [2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026],
    primaryLabel: "Youth (15-24)",
    secondaryLabel: "Prime-age (25-54)",
    zeroLine: true,
    recessionBand: { x0: x0Band, x1: x1Band, label: "Student-permit cap era" },
    ariaLabel: "Participation rate, prime-age (25-54) and youth (15-24), indexed to December 2019 equals zero in percentage points. Monthly, January 2019 through April 2026. The 2023-2026 aggregate participation decline is concentrated almost entirely in the youth cohort. Shaded region from September 2023 marks the international-student-permit cap announcement.",
  });
  writeFileSync(resolve(OUT_DIR, "youth_carries_participation.svg"), svg, "utf8");
  console.log("wrote youth_carries_participation.svg (", pTrim.length, "points, latest youth:", pTrim[pTrim.length - 1].value.toFixed(2), "pp; prime:", sTrim[sTrim.length - 1].value.toFixed(2), "pp)");
}

/* ---------- Chart 4: Denominator not productivity ---------- */
function chartDenominatorNotProductivity() {
  // Two quarterly Y/Y series:
  //   primary  = labour productivity Y/Y (the "productivity" read)
  //   secondary= per-capita real GDP Y/Y (the "per-capita output" read)
  // Editorial point: productivity is positive in 2025 while per-capita output Y/Y stayed weak.
  const prod = loadSingleSeries(resolve(ROOT, "data/raw/productivity_business_per_hour.csv"));
  const gdp  = loadSingleSeries(resolve(ROOT, "data/raw/gdp_quarterly.csv"));
  const pop  = loadSingleSeries(resolve(ROOT, "data/raw/pop_total.csv"));

  // Build per-capita GDP series (quarterly)
  const popByDate = new Map(pop.map((p) => [p.date, p.value]));
  const perCap = gdp
    .map((p) => {
      const pp = popByDate.get(p.date);
      return pp == null ? null : { date: p.date, value: p.value / pp };
    })
    .filter(Boolean);

  const prodYoy = yoyQuarterly(prod);
  const perCapYoy = yoyQuarterly(perCap);

  const cutoff = "2019-01-01";
  const primary = filterRange(prodYoy, cutoff);
  const secondary = filterRange(perCapYoy, cutoff);

  // Trim to common endpoint
  const minLast = (primary[primary.length - 1].date < secondary[secondary.length - 1].date)
    ? primary[primary.length - 1].date : secondary[secondary.length - 1].date;
  const pTrim = primary.filter((p) => p.date <= minLast);
  const sTrim = secondary.filter((p) => p.date <= minLast);

  // Clip 2020 COVID extremes so the 2023-25 editorial argument reads at scale.
  // Window from 2022Q1 onward.
  const cutoff2 = "2022-01-01";
  const pTrim2 = pTrim.filter((p) => p.date >= cutoff2);
  const sTrim2 = sTrim.filter((p) => p.date >= cutoff2);

  const xMin = dateToFractionalYear(pTrim2[0].date);
  const xMax = dateToFractionalYear(pTrim2[pTrim2.length - 1].date) + 0.2;

  const allVals = pTrim2.concat(sTrim2).map((p) => p.value);
  const yMin = Math.floor(Math.min(...allVals) - 0.5);
  const yMax = Math.ceil(Math.max(...allVals) + 0.5);

  const svg = renderTimeChart({
    primary: pTrim2,
    secondary: sTrim2,
    xMin, xMax,
    yMin, yMax,
    yUnit: "%",
    yDecimals: 1,
    xTickYears: [2022, 2023, 2024, 2025, 2026],
    primaryLabel: "Productivity Y/Y",
    secondaryLabel: "GDP per capita Y/Y",
    zeroLine: true,
    ariaLabel: "Canadian business-sector labour productivity year-over-year percent change versus real GDP per capita year-over-year percent change, quarterly, 2022Q1 through 2025Q4. Productivity rose 1.2 percent in 2025 while per-capita GDP remained weak; the gap is the denominator effect, not a productivity problem. Latest productivity print highlighted in red.",
  });
  writeFileSync(resolve(OUT_DIR, "denominator_not_productivity.svg"), svg, "utf8");
  console.log("wrote denominator_not_productivity.svg (primary points:", pTrim2.length, ", latest prod Y/Y:", pTrim2[pTrim2.length - 1].value.toFixed(2), "%; per-cap Y/Y:", sTrim2[sTrim2.length - 1].value.toFixed(2), "%)");
}

/* ---------- Chart 5: scenarios to end-2027 ---------- */
function chartScenarios2027() {
  // Historical emp/pop (15+, %), monthly Jan 2015 - Apr 2026.
  // Two illustrative scenarios as dashed forward extensions Apr-26 -> Dec-27:
  //   Scenario A (population deceleration only): emp held flat, pop +0.45% pa
  //       implies emp/pop rises by approximately 0.75 pts (mid of 0.6-0.9 pt range).
  //   Scenario C (cyclical recovery + denominator turn): emp/pop rises to ~62.3 (mid of 62.0-62.5).
  // Pre-COVID Dec-19 reference at 62.2%.
  const empRate = loadSingleSeries(resolve(ROOT, "data/raw/employment_rate.csv"));
  const cutoff = "2015-01-01";
  const historical = filterRange(empRate, cutoff);

  const lastP = historical[historical.length - 1];
  // Build scenario points: Apr-26 anchor + intermediate quarterly + Dec-27 endpoint.
  // Use linear-ish interpolation through 7 quarters (Apr-26 to Dec-27).
  const scenarioMonths = ["2026-04-01", "2026-07-01", "2026-10-01", "2027-01-01",
                          "2027-04-01", "2027-07-01", "2027-10-01", "2027-12-01"];

  function buildPath(target) {
    // Linear from lastP.value at Apr-26 to target at Dec-27.
    const start = lastP.value;
    const n = scenarioMonths.length;
    return scenarioMonths.map((d, i) => {
      const frac = i / (n - 1);
      return { date: d, value: start + (target - start) * frac };
    });
  }

  // Scenario A endpoint: mid of 61.1-61.4 = 61.25
  const scenA = buildPath(61.25);
  // Scenario C endpoint: mid of 62.0-62.5 = 62.25
  const scenC = buildPath(62.25);

  const xMin = dateToFractionalYear("2015-01-01");
  const xMax = 2028.05;

  const svg = renderTimeChart({
    primary: historical,
    xMin, xMax,
    yMin: 58, yMax: 63,
    yUnit: "%",
    yDecimals: 1,
    xTickYears: [2015, 2017, 2019, 2021, 2023, 2025, 2027],
    primaryLabel: "Emp/pop",
    primaryShowDot: true,
    refRule: { value: 62.2, label: "Pre-COVID Dec 2019" },
    forwardSegments: [
      { points: scenA, label: "A: pop. decel.", weight: 400 },
      { points: scenC, label: "C: both", weight: 600 },
    ],
    ariaLabel: "Canada employment-population ratio (15 plus, percent), monthly historical from January 2015 through April 2026, with two illustrative scenario paths through December 2027. Scenario A (population deceleration only) lands near 61.3 percent; Scenario C (combined population deceleration and cyclical recovery) lands near 62.3 percent, at the pre-COVID December 2019 baseline of 62.2 percent.",
  });
  writeFileSync(resolve(OUT_DIR, "scenarios_2027.svg"), svg, "utf8");
  console.log("wrote scenarios_2027.svg (historical points:", historical.length, ", latest:", lastP.date, lastP.value.toFixed(2), "%)");
}

/* ---------- run ---------- */
chartDivergence();
chartNprWave();
chartYouthParticipation();
chartDenominatorNotProductivity();
chartScenarios2027();
console.log("Pillar E charts written to", OUT_DIR);
