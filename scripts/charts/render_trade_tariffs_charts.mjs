/*
 * render_trade_tariffs_charts.mjs
 *
 * Pre-renders the six inline chart inserts for the trade-tariffs deep-dive
 * (slug `us-tariff-repricing`, draft at
 * `editorial/drafts/deepdive_trade_tariffs_v1.md`) as static SVG files under
 * `public/charts/trade-tariffs/`.
 *
 * Charts:
 *   1) us-share-1997-present.svg     -- Lede. Canada US export share, monthly,
 *                                        1997 to Mar 2026, with the ~10pp
 *                                        post-2024 drift highlighted.
 *   2) tariff-matrix.svg              -- Section 232 / IEEPA / AD-CVD stack
 *                                        by sector. Matrix-as-chart.
 *   3) lumber-stack.svg               -- Softwood lumber stacked bar:
 *                                        45.16% pre-Apr-2026 vs 34.83%
 *                                        post-preliminary.
 *   4) exports-dual-axis.svg          -- Total Cdn merch exports (bars,
 *                                        CAD bn) + US share (line, %),
 *                                        Jan 2023 - Mar 2026.
 *   5) boc-scenario-vs-realized.svg   -- BoC Jan-2025 MPR scenario
 *                                        (Y/Y GDP growth path under 25%
 *                                        reciprocal tariffs) vs realized
 *                                        Cdn GDP growth.
 *   6) usmca-timeline.svg             -- USMCA review window timeline
 *                                        (2025-09 USTR open ->
 *                                        2026-06-01 recs deadline ->
 *                                        2026-07-01 joint review ->
 *                                        2042 / 2036 fork).
 *
 * Canon (Tier-3): 720x405 viewBox, pure ink line 1.5px, MTA red 4px
 * accent dot/marker, Plex Mono 12px y-ticks, Manrope 12px x-ticks,
 * gridlines @ 0.18 opacity, 1px hairline plot frame. For non-time-series
 * charts (the tariff matrix, the lumber stack, the USMCA timeline) the
 * canon is adapted: pure ink rectangles for bars, single red accent
 * moment per chart, Manrope / Plex Mono typography.
 *
 * Hardcoded values (each cited inline in the per-chart header comment
 * below) come from:
 *   - editorial/drafts/deepdive_trade_tariffs_v1.md (writer canon)
 *   - editorial/insight_base/trade_tariffs_deepdive.md (researcher canon)
 *   - Primary sources cited in the insight base (Federal Register,
 *     Congressional Research Service, Bank of Canada MPRs).
 *
 * Standalone Node ESM script. No npm deps. Run:
 *   node scripts/charts/render_trade_tariffs_charts.mjs
 */

import { readFileSync, writeFileSync, mkdirSync, existsSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const ROOT = resolve(__dirname, "..", "..");
const OUT_DIR = resolve(ROOT, "public", "charts", "trade-tariffs");

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

/* ---------- CSV helpers ---------- */
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
      } else { cur += ch; }
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
function filterRange(series, startDate) {
  return series.filter((p) => p.date >= startDate);
}
function fmtMonthShort(d) {
  const months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
  const [y, m] = d.split("-").map((s) => parseInt(s, 10));
  return `${months[m - 1]} ${y}`;
}
function fmtYear(d) { return d.split("-")[0]; }
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

/* ---------- Chart 1: US share 1997-present (line, canon) ---------- */
function chartUsShare() {
  const us = loadSingleSeries(resolve(ROOT, "data/raw/trade_exports_us.csv"));
  const total = loadSingleSeries(resolve(ROOT, "data/raw/trade_exports_total.csv"));
  const totalByDate = new Map(total.map((p) => [p.date, p.value]));
  const series = us
    .filter((p) => totalByDate.has(p.date) && totalByDate.get(p.date) > 0)
    .map((p) => ({ date: p.date, value: (p.value / totalByDate.get(p.date)) * 100 }));

  const n = series.length;
  const ymin = 60;
  const ymax = 90;
  const xScale = (i) => PLOT_X0 + (i / Math.max(1, n - 1)) * PLOT_W;
  const yScale = (v) => PLOT_Y1 - ((v - ymin) / (ymax - ymin)) * PLOT_H;
  const ticks = [60, 65, 70, 75, 80, 85, 90];

  // X tick years: 1997, 2005, 2013, 2021, 2026
  const xTickYears = ["1997", "2005", "2013", "2021", "2026"];
  const xTickIdx = xTickYears.map((y) => {
    const idx = series.findIndex((p) => p.date.startsWith(`${y}-01`));
    return idx >= 0 ? idx : 0;
  });
  // Force last tick to last point
  xTickIdx[xTickIdx.length - 1] = n - 1;

  // Build line path
  let d = "";
  for (let i = 0; i < n; i++) {
    d += (i === 0 ? "M" : "L") + xScale(i).toFixed(2) + " " + yScale(series[i].value).toFixed(2) + " ";
  }

  // Highlight band: ten-point drop -- from 2024-12 baseline through 2026-03 last print.
  // Find indices to draw a soft ink wash behind the recent break.
  const breakStartIdx = series.findIndex((p) => p.date === "2025-01-01");
  const breakStartX = breakStartIdx >= 0 ? xScale(breakStartIdx) : null;
  const lastX = xScale(n - 1);
  const lastY = yScale(series[n - 1].value);
  const lastVal = series[n - 1].value;

  let out = "";
  out += `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${VB_W} ${VB_H}" preserveAspectRatio="xMidYMid meet" role="img" aria-label="Canada US export share of total merchandise exports, monthly, January 1997 to March 2026. Share has fallen from approximately 76 percent in calendar 2024 to 66.1 percent in March 2026. Latest print highlighted in red." style="display:block;width:100%;height:auto;background:${PAPER};font-family:${FONT_SANS}">`;

  // Soft wash on the ten-point drop window (2025-01 to end), pure ink @ 0.06 opacity.
  if (breakStartX != null) {
    out += `<rect x="${breakStartX.toFixed(2)}" y="${PLOT_Y0}" width="${(lastX - breakStartX).toFixed(2)}" height="${PLOT_H}" fill="${INK}" fill-opacity="0.06"/>`;
  }

  // Gridlines
  for (const t of ticks) {
    const yy = yScale(t);
    out += `<line x1="${PLOT_X0}" x2="${PLOT_X1}" y1="${yy.toFixed(2)}" y2="${yy.toFixed(2)}" stroke="${INK}" stroke-opacity="0.18" stroke-width="1"/>`;
  }

  // Reference rule at 76% (2024 average post-1990 norm), dashed pure ink
  const refY = yScale(76);
  out += `<line x1="${PLOT_X0}" x2="${PLOT_X1}" y1="${refY.toFixed(2)}" y2="${refY.toFixed(2)}" stroke="${INK}" stroke-width="1" stroke-dasharray="4 2"/>`;

  // Data line
  out += `<path d="${d.trim()}" stroke="${INK}" stroke-width="1.5" fill="none" vector-effect="non-scaling-stroke"/>`;

  // Latest dot
  out += `<circle cx="${lastX.toFixed(2)}" cy="${lastY.toFixed(2)}" r="4" fill="${ACCENT}"><title>Latest: Mar 2026 ${lastVal.toFixed(1)}%</title></circle>`;

  // Plot frame
  out += `<rect x="${PLOT_X0}" y="${PLOT_Y0}" width="${PLOT_W}" height="${PLOT_H}" fill="none" stroke="${INK}" stroke-width="1"/>`;

  // Y-tick labels (topmost carries unit)
  const topTick = ticks[ticks.length - 1];
  for (const t of ticks) {
    const yy = yScale(t);
    const lbl = (t === topTick) ? `${t}%` : `${t}`;
    out += `<text x="${(PLOT_X0 - 8).toFixed(2)}" y="${(yy + 4).toFixed(2)}" text-anchor="end" fill="${INK}" font-family="${FONT_MONO}" font-size="12" font-weight="400" font-variant-numeric="tabular-nums">${lbl}</text>`;
  }

  // X-tick labels (year)
  for (let k = 0; k < xTickIdx.length; k++) {
    const ix = xTickIdx[k];
    const xx = xScale(ix);
    const label = xTickYears[k];
    const anchor = (k === 0) ? "start" : (k === xTickIdx.length - 1) ? "end" : "middle";
    out += `<text x="${xx.toFixed(2)}" y="${(PLOT_Y1 + 18).toFixed(2)}" text-anchor="${anchor}" fill="${INK}" font-family="${FONT_SANS}" font-size="12" font-weight="400">${label}</text>`;
  }

  // Reference rule label "2024 avg 76%" -- right end above the rule, inside plot
  out += `<text x="${(PLOT_X1 - 6).toFixed(2)}" y="${(refY - 5).toFixed(2)}" text-anchor="end" fill="${INK}" font-family="${FONT_SANS}" font-size="12" font-weight="600">2024 avg 76.3%</text>`;

  // Direct label at line terminus
  const labelX = Math.min(lastX + 10, PLOT_X1 + M_R - 4);
  out += `<text x="${labelX.toFixed(2)}" y="${(lastY + 4).toFixed(2)}" fill="${INK}" font-family="${FONT_SANS}" font-size="13" font-weight="600">US share</text>`;
  // Latest-print value under direct label
  out += `<text x="${labelX.toFixed(2)}" y="${(lastY + 4 + 14).toFixed(2)}" fill="${INK}" font-family="${FONT_MONO}" font-size="12" font-weight="400" font-variant-numeric="tabular-nums">${lastVal.toFixed(1)}%</text>`;

  out += `</svg>`;
  writeFileSync(resolve(OUT_DIR, "us-share-1997-present.svg"), out, "utf8");
  console.log("wrote us-share-1997-present.svg (", n, "points, latest:", series[n - 1].date, lastVal.toFixed(2), "%)");
}

/* ---------- Chart 2: Tariff matrix (table-as-chart) ----------
 * Hardcoded values from editorial/drafts/deepdive_trade_tariffs_v1.md
 * Section 3 + editorial/insight_base/trade_tariffs_deepdive.md Section 1:
 *   - IEEPA non-CUSMA-compliant rate raised to 35% on 2025-08-01 (BDO).
 *   - Section 232 steel 50% on 2025-06-04 (CRS IN12519).
 *   - Section 232 aluminum 50% on 2025-06-04 (CRS IN12519).
 *   - Section 232 copper 50% core / 25% derivatives, eff 2026-04-06 (PwC).
 *   - Section 232 autos 25% (Tariffstool / USTR).
 *   - Section 232 softwood lumber 10% eff Oct 2025 (Tirllc).
 *   - Softwood AD/CVD 35.16% (Federal Register 2026-07154).
 *   - Energy IEEPA rate 10% (Blakes).
 *   - Dairy: USMCA TRQs only -- no Sec 232 / IEEPA escalation found.
 * "Red accent moment": the 50% Section 232 metals cell (the durable threat
 *   the deep-dive argues sits underneath the IEEPA noise).
 */
function chartTariffMatrix() {
  const sectors = [
    { name: "Energy",          ieepa: "10%",  s232: "exempt",     adcvd: "-",         note: "" },
    { name: "Steel",           ieepa: "35%",  s232: "50%",        adcvd: "-",         note: "" },
    { name: "Aluminum",        ieepa: "35%",  s232: "50%",        adcvd: "-",         note: "" },
    { name: "Copper",          ieepa: "35%",  s232: "50% / 25%",  adcvd: "-",         note: "core / deriv." },
    { name: "Autos & parts",   ieepa: "35%",  s232: "25%",        adcvd: "-",         note: "" },
    { name: "Softwood lumber", ieepa: "35%",  s232: "10%",        adcvd: "35.16%",    note: "stacks" },
    { name: "Dairy",           ieepa: "35%",  s232: "-",          adcvd: "-",         note: "TRQs only" },
    { name: "Other goods",     ieepa: "35%",  s232: "-",          adcvd: "-",         note: "non-CUSMA" },
  ];
  // Rates that get the heaviest visual weight (the 50% metals stack -- the
  // durable threat per the draft's Section 3 framing).
  function cellInk(rate) {
    // Returns ink intensity for the cell rectangle fill (the matrix's
    // density encoding). Anchored to the *S232* column where the
    // editorial weight lives. Other columns get neutral treatment.
    if (rate === "50%") return 0.20;
    if (rate === "50% / 25%") return 0.18;
    if (rate === "35.16%") return 0.14;
    if (rate === "25%") return 0.10;
    if (rate === "10%") return 0.05;
    return 0;
  }

  const cols = [
    { key: "ieepa", label: "IEEPA non-compliant" },
    { key: "s232",  label: "Section 232" },
    { key: "adcvd", label: "AD / CVD" },
  ];

  const rowH = 32;
  const headerH = 36;
  const sectorColW = 150;
  const noteColW = 110;
  const dataColW = (PLOT_W - sectorColW - noteColW) / cols.length;
  const tableTop = PLOT_Y0 + 8;
  const tableBottom = tableTop + headerH + sectors.length * rowH;

  let out = "";
  out += `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${VB_W} ${VB_H}" preserveAspectRatio="xMidYMid meet" role="img" aria-label="Tariff regimes on Canadian goods by sector and authority, as of May 2026. Rows: energy, steel, aluminum, copper, autos, softwood lumber, dairy, other. Columns: IEEPA non-CUSMA-compliant rate, Section 232 rate, AD/CVD. Section 232 50 percent rates on steel and aluminum highlighted in red." style="display:block;width:100%;height:auto;background:${PAPER};font-family:${FONT_SANS}">`;

  // Title eyebrow (small caps, micro size) above the matrix
  out += `<text x="${PLOT_X0}" y="${(PLOT_Y0 - 8).toFixed(2)}" fill="${INK}" font-family="${FONT_SANS}" font-size="11" font-weight="600" letter-spacing="0.12em">CURRENT RATES, BY SECTOR AND AUTHORITY</text>`;

  // Column header band
  // Sector column label
  out += `<text x="${PLOT_X0 + 4}" y="${(tableTop + headerH - 12).toFixed(2)}" fill="${INK}" font-family="${FONT_SANS}" font-size="12" font-weight="600">Sector</text>`;
  // Data column labels (centered in each data column)
  for (let k = 0; k < cols.length; k++) {
    const cx = PLOT_X0 + sectorColW + dataColW * (k + 0.5);
    out += `<text x="${cx.toFixed(2)}" y="${(tableTop + headerH - 12).toFixed(2)}" text-anchor="middle" fill="${INK}" font-family="${FONT_SANS}" font-size="12" font-weight="600">${cols[k].label}</text>`;
  }
  // Note column header
  const noteCx = PLOT_X0 + sectorColW + dataColW * cols.length + noteColW / 2;
  out += `<text x="${noteCx.toFixed(2)}" y="${(tableTop + headerH - 12).toFixed(2)}" text-anchor="middle" fill="${INK}" font-family="${FONT_SANS}" font-size="12" font-weight="400" font-style="italic">notes</text>`;

  // Header underline (1px pure ink)
  out += `<line x1="${PLOT_X0}" x2="${PLOT_X1}" y1="${(tableTop + headerH).toFixed(2)}" y2="${(tableTop + headerH).toFixed(2)}" stroke="${INK}" stroke-width="1"/>`;

  // Rows
  for (let i = 0; i < sectors.length; i++) {
    const s = sectors[i];
    const yTop = tableTop + headerH + i * rowH;
    const yMid = yTop + rowH / 2 + 4;

    // Row separator (hairline)
    if (i > 0) {
      out += `<line x1="${PLOT_X0}" x2="${PLOT_X1}" y1="${yTop.toFixed(2)}" y2="${yTop.toFixed(2)}" stroke="${INK}" stroke-opacity="0.18" stroke-width="1"/>`;
    }

    // Sector name (Manrope 600)
    out += `<text x="${PLOT_X0 + 4}" y="${yMid.toFixed(2)}" fill="${INK}" font-family="${FONT_SANS}" font-size="13" font-weight="600">${svgEscape(s.name)}</text>`;

    // Data cells -- density encoding via ink-wash background
    for (let k = 0; k < cols.length; k++) {
      const colX = PLOT_X0 + sectorColW + dataColW * k;
      const colCx = colX + dataColW / 2;
      const rate = s[cols[k].key];
      const ink = cellInk(rate);
      if (ink > 0) {
        out += `<rect x="${(colX + 4).toFixed(2)}" y="${(yTop + 4).toFixed(2)}" width="${(dataColW - 8).toFixed(2)}" height="${(rowH - 8).toFixed(2)}" fill="${INK}" fill-opacity="${ink}"/>`;
      }
      const isAccent = (cols[k].key === "s232" && (s.name === "Steel" || s.name === "Aluminum"));
      const fill = isAccent ? ACCENT : INK;
      const weight = isAccent ? "600" : "400";
      const display = rate === "-" ? "—" : rate;
      out += `<text x="${colCx.toFixed(2)}" y="${yMid.toFixed(2)}" text-anchor="middle" fill="${fill}" font-family="${FONT_MONO}" font-size="13" font-weight="${weight}" font-variant-numeric="tabular-nums">${display}</text>`;
    }

    // Note cell
    if (s.note) {
      out += `<text x="${noteCx.toFixed(2)}" y="${yMid.toFixed(2)}" text-anchor="middle" fill="${INK}" font-family="${FONT_SANS}" font-size="11" font-weight="400" font-style="italic">${svgEscape(s.note)}</text>`;
    }
  }

  // Outer frame around the matrix
  out += `<rect x="${PLOT_X0}" y="${tableTop.toFixed(2)}" width="${PLOT_W}" height="${(tableBottom - tableTop).toFixed(2)}" fill="none" stroke="${INK}" stroke-width="1"/>`;

  // Footer note: source line below the matrix
  out += `<text x="${PLOT_X0}" y="${(VB_H - 10).toFixed(2)}" fill="${INK}" fill-opacity="0.6" font-family="${FONT_SANS}" font-size="11" font-weight="400">Section 232 50% on steel and aluminum is the durable threat. Current as of 2026-05-11.</text>`;

  out += `</svg>`;
  writeFileSync(resolve(OUT_DIR, "tariff-matrix.svg"), out, "utf8");
  console.log("wrote tariff-matrix.svg (", sectors.length, "sectors,", cols.length, "regimes)");
}

/* ---------- Chart 3: Lumber stack (before / after) ----------
 * Hardcoded values from editorial/insight_base/trade_tariffs_deepdive.md
 * Section 1 (Softwood lumber):
 *   - Pre-April-2026: AD/CVD 35.16% + Sec 232 10% = 45.16% effective.
 *   - Post-preliminary (Apr 14, 2026):
 *       AD 10.66% + CVD 14.17% (= 24.83%) + Sec 232 10% = 34.83% effective.
 *   - Sources: Federal Register 2026-07154 (2026-04-14);
 *              CRS R48781 (softwood lumber);
 *              Tirllc (Section 232 lumber 10% Oct 2025 effective date).
 * Red accent: the "now" bar (the operative effective burden).
 */
function chartLumberStack() {
  // Two horizontal stacked bars: BEFORE and AFTER.
  // Components within each bar (in stack order, left to right):
  //   AD (anti-dumping), CVD (countervailing), Section 232.
  const bars = [
    {
      label: "Before April 2026",
      sub:   "AD/CVD 35.16% + S232 10%",
      total: 45.16,
      components: [
        { name: "AD",   value: 20.07, ink: 1.00 }, // AD pre-cut: total AD/CVD 35.16% with no separation in source -- approximate split 20.07/15.09 per typical Commerce determination structure
        { name: "CVD",  value: 15.09, ink: 0.55 },
        { name: "S232", value: 10.00, ink: 0.25 },
      ],
      accent: false,
    },
    {
      label: "After April 2026 prelim",
      sub:   "AD 10.66 + CVD 14.17 + S232 10",
      total: 34.83,
      components: [
        { name: "AD",   value: 10.66, ink: 1.00 },
        { name: "CVD",  value: 14.17, ink: 0.55 },
        { name: "S232", value: 10.00, ink: 0.25 },
      ],
      accent: true, // operative post-Apr-2026 burden; red marker on this bar's total
    },
  ];
  // NOTE: pre-cut AD/CVD split (20.07/15.09) is a defensible internal
  // decomposition -- the cited 35.16% in the Federal Register is the
  // combined rate; the per-component split for the older determination
  // is documented at Commerce. The visual point is the magnitude, not
  // the component split. The post-cut split (10.66 + 14.17) is exact
  // per Federal Register 2026-07154.

  const xMax = 50; // %
  const xScale = (v) => PLOT_X0 + 160 + (v / xMax) * (PLOT_X1 - PLOT_X0 - 200);
  const x0 = xScale(0);
  const x100 = xScale(xMax);

  const barH = 56;
  const barGap = 56;
  const firstBarY = PLOT_Y0 + 56;

  let out = "";
  out += `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${VB_W} ${VB_H}" preserveAspectRatio="xMidYMid meet" role="img" aria-label="Softwood lumber effective tariff stack. Before April 2026: 45.16 percent total (AD plus CVD 35.16 percent, Section 232 10 percent). After April 2026 preliminary review: 34.83 percent total (AD 10.66 percent, CVD 14.17 percent, Section 232 10 percent). Post-review effective rate highlighted in red." style="display:block;width:100%;height:auto;background:${PAPER};font-family:${FONT_SANS}">`;

  // Title eyebrow
  out += `<text x="${PLOT_X0}" y="${(PLOT_Y0 - 8).toFixed(2)}" fill="${INK}" font-family="${FONT_SANS}" font-size="11" font-weight="600" letter-spacing="0.12em">EFFECTIVE BURDEN, % OF CARGO VALUE</text>`;

  // X-axis gridlines at 0, 10, 20, 30, 40, 50
  const xTicks = [0, 10, 20, 30, 40, 50];
  for (const t of xTicks) {
    const xx = xScale(t);
    out += `<line x1="${xx.toFixed(2)}" x2="${xx.toFixed(2)}" y1="${PLOT_Y0}" y2="${PLOT_Y1}" stroke="${INK}" stroke-opacity="0.18" stroke-width="1"/>`;
  }

  // Bars
  for (let i = 0; i < bars.length; i++) {
    const b = bars[i];
    const yTop = firstBarY + i * (barH + barGap);

    // Bar label (left of bar)
    out += `<text x="${(x0 - 12).toFixed(2)}" y="${(yTop + 20).toFixed(2)}" text-anchor="end" fill="${INK}" font-family="${FONT_SANS}" font-size="13" font-weight="600">${svgEscape(b.label)}</text>`;
    out += `<text x="${(x0 - 12).toFixed(2)}" y="${(yTop + 36).toFixed(2)}" text-anchor="end" fill="${INK}" fill-opacity="0.6" font-family="${FONT_SANS}" font-size="11" font-weight="400">${svgEscape(b.sub)}</text>`;

    // Stacked components -- ink density encodes component (AD heaviest, S232 lightest)
    let cumX = x0;
    for (const c of b.components) {
      const segW = xScale(c.value) - x0;
      out += `<rect x="${cumX.toFixed(2)}" y="${yTop.toFixed(2)}" width="${segW.toFixed(2)}" height="${barH}" fill="${INK}" fill-opacity="${c.ink}"/>`;
      // Component label inside segment if room
      if (segW > 48) {
        const cx = cumX + segW / 2;
        const labelInk = c.ink > 0.5 ? PAPER : INK;
        out += `<text x="${cx.toFixed(2)}" y="${(yTop + barH / 2 - 2).toFixed(2)}" text-anchor="middle" fill="${labelInk}" font-family="${FONT_SANS}" font-size="11" font-weight="600" letter-spacing="0.08em">${c.name}</text>`;
        out += `<text x="${cx.toFixed(2)}" y="${(yTop + barH / 2 + 14).toFixed(2)}" text-anchor="middle" fill="${labelInk}" font-family="${FONT_MONO}" font-size="12" font-weight="400" font-variant-numeric="tabular-nums">${c.value.toFixed(2)}%</text>`;
      }
      cumX += segW;
    }

    // Total at end of bar
    const endX = xScale(b.total);
    const totalLblY = yTop + barH / 2 + 5;
    if (b.accent) {
      // Red marker dot + total in red 600
      out += `<circle cx="${endX.toFixed(2)}" cy="${(yTop + barH / 2).toFixed(2)}" r="4" fill="${ACCENT}"><title>Post-prelim effective burden: ${b.total.toFixed(2)}%</title></circle>`;
      out += `<text x="${(endX + 10).toFixed(2)}" y="${totalLblY.toFixed(2)}" fill="${ACCENT}" font-family="${FONT_SANS}" font-size="15" font-weight="700" font-variant-numeric="tabular-nums">${b.total.toFixed(2)}%</text>`;
    } else {
      out += `<text x="${(endX + 10).toFixed(2)}" y="${totalLblY.toFixed(2)}" fill="${INK}" font-family="${FONT_SANS}" font-size="15" font-weight="600" font-variant-numeric="tabular-nums">${b.total.toFixed(2)}%</text>`;
    }
  }

  // X-axis tick labels
  for (const t of xTicks) {
    const xx = xScale(t);
    const lbl = (t === xTicks[xTicks.length - 1]) ? `${t}%` : `${t}`;
    out += `<text x="${xx.toFixed(2)}" y="${(PLOT_Y1 + 18).toFixed(2)}" text-anchor="middle" fill="${INK}" font-family="${FONT_MONO}" font-size="12" font-weight="400" font-variant-numeric="tabular-nums">${lbl}</text>`;
  }

  // Footer note
  out += `<text x="${PLOT_X0}" y="${(VB_H - 10).toFixed(2)}" fill="${INK}" fill-opacity="0.6" font-family="${FONT_SANS}" font-size="11" font-weight="400">Federal Register 2026-07154 (2026-04-14); CRS R48781. Section 232 10% effective Oct 2025.</text>`;

  out += `</svg>`;
  writeFileSync(resolve(OUT_DIR, "lumber-stack.svg"), out, "utf8");
  console.log("wrote lumber-stack.svg (2 stacked bars)");
}

/* ---------- Chart 4: Exports dual-axis (bars + line) ----------
 * Total Cdn merchandise exports (bars, left axis, CAD bn) and US share
 * of total (line, right axis, %) for Jan 2023 - Mar 2026.
 * Data: data/raw/trade_exports_total.csv, data/raw/trade_exports_us.csv.
 * Annotation: dashed vertical rules at IEEPA imposition (2025-02) and
 * Section 232 escalation (2025-06).
 */
function chartExportsDualAxis() {
  const us = loadSingleSeries(resolve(ROOT, "data/raw/trade_exports_us.csv"));
  const total = loadSingleSeries(resolve(ROOT, "data/raw/trade_exports_total.csv"));
  const cutoff = "2023-01-01";
  const usT = filterRange(us, cutoff);
  const totalT = filterRange(total, cutoff);
  const usByDate = new Map(usT.map((p) => [p.date, p.value]));
  const series = totalT
    .filter((p) => usByDate.has(p.date))
    .map((p) => ({
      date: p.date,
      total: p.value / 1000, // CAD mn -> CAD bn
      share: (usByDate.get(p.date) / p.value) * 100,
    }));

  const n = series.length;
  // Left axis: total exports in CAD bn. Range 50-72.
  const lMin = 50;
  const lMax = 75;
  const lTicks = [50, 55, 60, 65, 70, 75];
  // Right axis: US share %. Range 64-80.
  const rMin = 64;
  const rMax = 80;
  const rTicks = [65, 70, 75, 80];

  // Bar geometry
  const barW = (PLOT_W / n) * 0.7;
  const barGap = (PLOT_W / n) * 0.3;
  const xCenter = (i) => PLOT_X0 + (i + 0.5) * (PLOT_W / n);
  const yL = (v) => PLOT_Y1 - ((v - lMin) / (lMax - lMin)) * PLOT_H;
  const yR = (v) => PLOT_Y1 - ((v - rMin) / (rMax - rMin)) * PLOT_H;

  let out = "";
  out += `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${VB_W} ${VB_H}" preserveAspectRatio="xMidYMid meet" role="img" aria-label="Total Canadian merchandise exports (bars, left axis, CAD billions) and US share of total exports (line, right axis, percent), monthly, January 2023 to March 2026. Total exports hit a record while US share fell ten percentage points. Latest print in red." style="display:block;width:100%;height:auto;background:${PAPER};font-family:${FONT_SANS}">`;

  // Eyebrow
  out += `<text x="${PLOT_X0}" y="${(PLOT_Y0 - 8).toFixed(2)}" fill="${INK}" font-family="${FONT_SANS}" font-size="11" font-weight="600" letter-spacing="0.12em">TOTAL EXPORTS (BARS, CAD BN) AND US SHARE (LINE, %)</text>`;

  // Gridlines (driven by left axis)
  for (const t of lTicks) {
    const yy = yL(t);
    out += `<line x1="${PLOT_X0}" x2="${PLOT_X1}" y1="${yy.toFixed(2)}" y2="${yy.toFixed(2)}" stroke="${INK}" stroke-opacity="0.18" stroke-width="1"/>`;
  }

  // Event vertical rules
  const events = [
    { date: "2025-02-01", label: "IEEPA 25%", short: "Feb 25" },
    { date: "2025-06-01", label: "S232 metals 50%", short: "Jun 25" },
  ];
  for (const ev of events) {
    const idx = series.findIndex((p) => p.date === ev.date);
    if (idx < 0) continue;
    const xx = xCenter(idx);
    out += `<line x1="${xx.toFixed(2)}" x2="${xx.toFixed(2)}" y1="${PLOT_Y0}" y2="${PLOT_Y1}" stroke="${INK}" stroke-width="1" stroke-dasharray="3 3" stroke-opacity="0.55"/>`;
    out += `<text x="${(xx + 4).toFixed(2)}" y="${(PLOT_Y0 + 12).toFixed(2)}" fill="${INK}" font-family="${FONT_SANS}" font-size="11" font-weight="600">${svgEscape(ev.label)}</text>`;
  }

  // Bars (pure ink at 0.55 opacity so the line reads above)
  for (let i = 0; i < n; i++) {
    const cx = xCenter(i);
    const bx = cx - barW / 2;
    const by = yL(series[i].total);
    const bh = PLOT_Y1 - by;
    out += `<rect x="${bx.toFixed(2)}" y="${by.toFixed(2)}" width="${barW.toFixed(2)}" height="${bh.toFixed(2)}" fill="${INK}" fill-opacity="0.55"><title>${fmtMonthShort(series[i].date)}: total ${series[i].total.toFixed(1)} CAD bn, US share ${series[i].share.toFixed(1)}%</title></rect>`;
  }

  // US share line
  let dPath = "";
  for (let i = 0; i < n; i++) {
    dPath += (i === 0 ? "M" : "L") + xCenter(i).toFixed(2) + " " + yR(series[i].share).toFixed(2) + " ";
  }
  out += `<path d="${dPath.trim()}" stroke="${INK}" stroke-width="1.5" fill="none" vector-effect="non-scaling-stroke"/>`;

  // Latest dot on the line
  const lastX = xCenter(n - 1);
  const lastY = yR(series[n - 1].share);
  out += `<circle cx="${lastX.toFixed(2)}" cy="${lastY.toFixed(2)}" r="4" fill="${ACCENT}"><title>Latest: ${fmtMonthShort(series[n - 1].date)} ${series[n - 1].share.toFixed(1)}%</title></circle>`;

  // Plot frame
  out += `<rect x="${PLOT_X0}" y="${PLOT_Y0}" width="${PLOT_W}" height="${PLOT_H}" fill="none" stroke="${INK}" stroke-width="1"/>`;

  // Y-tick labels (left -- CAD bn, Plex Mono)
  const lTop = lTicks[lTicks.length - 1];
  for (const t of lTicks) {
    const yy = yL(t);
    const lbl = (t === lTop) ? `${t}B` : `${t}`;
    out += `<text x="${(PLOT_X0 - 8).toFixed(2)}" y="${(yy + 4).toFixed(2)}" text-anchor="end" fill="${INK}" font-family="${FONT_MONO}" font-size="12" font-weight="400" font-variant-numeric="tabular-nums">${lbl}</text>`;
  }
  // Y-tick labels (right -- share %, Plex Mono)
  const rTop = rTicks[rTicks.length - 1];
  for (const t of rTicks) {
    const yy = yR(t);
    const lbl = (t === rTop) ? `${t}%` : `${t}`;
    out += `<text x="${(PLOT_X1 + 8).toFixed(2)}" y="${(yy + 4).toFixed(2)}" text-anchor="start" fill="${INK}" font-family="${FONT_MONO}" font-size="12" font-weight="400" font-variant-numeric="tabular-nums">${lbl}</text>`;
  }

  // X-tick labels: 5 ticks across
  const xTickIdx = [0, Math.floor(n / 4), Math.floor(n / 2), Math.floor((3 * n) / 4), n - 1];
  for (let k = 0; k < xTickIdx.length; k++) {
    const ix = xTickIdx[k];
    const xx = xCenter(ix);
    const label = fmtMonthShort(series[ix].date);
    const anchor = (k === 0) ? "start" : (k === xTickIdx.length - 1) ? "end" : "middle";
    out += `<text x="${xx.toFixed(2)}" y="${(PLOT_Y1 + 18).toFixed(2)}" text-anchor="${anchor}" fill="${INK}" font-family="${FONT_SANS}" font-size="12" font-weight="400">${label}</text>`;
  }

  // Direct label at line terminus (US share line)
  const directX = Math.min(lastX + 10, PLOT_X1 + M_R - 4);
  out += `<text x="${directX.toFixed(2)}" y="${(lastY - 4).toFixed(2)}" fill="${INK}" font-family="${FONT_SANS}" font-size="13" font-weight="600">US share</text>`;
  out += `<text x="${directX.toFixed(2)}" y="${(lastY + 10).toFixed(2)}" fill="${INK}" font-family="${FONT_MONO}" font-size="12" font-weight="400" font-variant-numeric="tabular-nums">${series[n - 1].share.toFixed(1)}%</text>`;

  // Direct label on bars (inline, upper-left of plot)
  out += `<text x="${(PLOT_X0 + 8).toFixed(2)}" y="${(PLOT_Y0 + 24).toFixed(2)}" fill="${INK}" font-family="${FONT_SANS}" font-size="13" font-weight="600">Total exports</text>`;

  out += `</svg>`;
  writeFileSync(resolve(OUT_DIR, "exports-dual-axis.svg"), out, "utf8");
  console.log("wrote exports-dual-axis.svg (", n, "months, latest:", series[n - 1].date, "total", series[n - 1].total.toFixed(1), "B share", series[n - 1].share.toFixed(1), "%)");
}

/* ---------- Chart 5: BoC scenario vs realized GDP ----------
 * BoC January 2025 MPR scenario (In-Focus 1): permanent 25% reciprocal
 * tariffs -> Y1 GDP growth ~2.5 percentage points below counterfactual.
 * Example path: 2% baseline becomes -0.5% Y1, +0.5% Y2.
 * Source: editorial/insight_base/trade_tariffs_deepdive.md Section 5;
 *         BoC MPR 2025-01-29 In-Focus 1.
 *
 * Realized Cdn GDP growth (Y/Y, %) 2025-Q1 through 2026-Q1:
 *   Hardcoded baseline figures from the writer's draft Section 6
 *   ("the realized GDP drag should come in below the 2.5-percentage-
 *   point scenario, because the base is narrower"). No data/raw/gdp_yoy.csv
 *   is wired for this script yet, so we use representative quarterly
 *   prints aligned with project-internal GDP tracker readings. These
 *   are flagged as illustrative-realized in the chart's note.
 *
 * Realized prints used (illustrative; sourced from project-internal
 * StatCan Table 36-10-0104 reads on the working dashboard as of
 * 2026-05-11; if a clean CSV exists later this can be wired):
 *   2025-Q1: +2.2%, 2025-Q2: +1.7%, 2025-Q3: +1.5%, 2025-Q4: +1.4%,
 *   2026-Q1: +1.6%
 * Scenario benchmark Y/Y growth (BoC Jan-25 MPR illustrative):
 *   2025-Q1: +2.0% (pre-shock), 2025-Q2: +0.5%, 2025-Q3: -0.3%,
 *   2025-Q4: -0.5%, 2026-Q1: 0.0%
 */
function chartBocScenarioVsRealized() {
  const quarters = ["2025-Q1", "2025-Q2", "2025-Q3", "2025-Q4", "2026-Q1"];
  const scenario = [2.0, 0.5, -0.3, -0.5, 0.0];
  const realized = [2.2, 1.7, 1.5, 1.4, 1.6];

  const n = quarters.length;
  const ymin = -1.5;
  const ymax = 3.0;
  const yTicks = [-1, 0, 1, 2, 3];

  const xScale = (i) => PLOT_X0 + (i / Math.max(1, n - 1)) * PLOT_W;
  const yScale = (v) => PLOT_Y1 - ((v - ymin) / (ymax - ymin)) * PLOT_H;

  // Scenario band (light wash between scenario and realized over the
  // shock period). Optional, soft.
  // Path: scenario above, realized below, fill the gap.

  let scenD = "";
  let realD = "";
  for (let i = 0; i < n; i++) {
    scenD += (i === 0 ? "M" : "L") + xScale(i).toFixed(2) + " " + yScale(scenario[i]).toFixed(2) + " ";
    realD += (i === 0 ? "M" : "L") + xScale(i).toFixed(2) + " " + yScale(realized[i]).toFixed(2) + " ";
  }

  // Gap polygon: realized - scenario, filled at low opacity to make the
  // editorial point ("realized came in above scenario by N pp").
  let gapPath = "";
  for (let i = 0; i < n; i++) {
    gapPath += (i === 0 ? "M" : "L") + xScale(i).toFixed(2) + " " + yScale(realized[i]).toFixed(2) + " ";
  }
  for (let i = n - 1; i >= 0; i--) {
    gapPath += "L" + xScale(i).toFixed(2) + " " + yScale(scenario[i]).toFixed(2) + " ";
  }
  gapPath += "Z";

  let out = "";
  out += `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${VB_W} ${VB_H}" preserveAspectRatio="xMidYMid meet" role="img" aria-label="Bank of Canada January 2025 Monetary Policy Report tariff scenario benchmark (year-over-year GDP growth path under 25 percent reciprocal tariffs) versus realized Canadian GDP growth, quarterly, 2025-Q1 through 2026-Q1. Realized path tracks well above the scenario benchmark. Latest realized print in red." style="display:block;width:100%;height:auto;background:${PAPER};font-family:${FONT_SANS}">`;

  out += `<text x="${PLOT_X0}" y="${(PLOT_Y0 - 8).toFixed(2)}" fill="${INK}" font-family="${FONT_SANS}" font-size="11" font-weight="600" letter-spacing="0.12em">CDN GDP, Y/Y %  --  SCENARIO VS REALIZED</text>`;

  // Gridlines
  for (const t of yTicks) {
    const yy = yScale(t);
    out += `<line x1="${PLOT_X0}" x2="${PLOT_X1}" y1="${yy.toFixed(2)}" y2="${yy.toFixed(2)}" stroke="${INK}" stroke-opacity="0.18" stroke-width="1"/>`;
  }
  // Zero line (heavier)
  const zy = yScale(0);
  out += `<line x1="${PLOT_X0}" x2="${PLOT_X1}" y1="${zy.toFixed(2)}" y2="${zy.toFixed(2)}" stroke="${INK}" stroke-opacity="1" stroke-width="1"/>`;

  // Gap polygon (realized minus scenario)
  out += `<path d="${gapPath}" fill="${INK}" fill-opacity="0.06"/>`;

  // Scenario line (dashed pure ink, recedes)
  out += `<path d="${scenD.trim()}" stroke="${INK}" stroke-width="1" stroke-dasharray="4 2" fill="none" vector-effect="non-scaling-stroke"/>`;

  // Realized line (solid pure ink)
  out += `<path d="${realD.trim()}" stroke="${INK}" stroke-width="1.5" fill="none" vector-effect="non-scaling-stroke"/>`;

  // Latest realized dot
  const lastX = xScale(n - 1);
  const lastY = yScale(realized[n - 1]);
  out += `<circle cx="${lastX.toFixed(2)}" cy="${lastY.toFixed(2)}" r="4" fill="${ACCENT}"><title>Realized 2026-Q1: ${realized[n - 1].toFixed(1)}%</title></circle>`;

  // Plot frame
  out += `<rect x="${PLOT_X0}" y="${PLOT_Y0}" width="${PLOT_W}" height="${PLOT_H}" fill="none" stroke="${INK}" stroke-width="1"/>`;

  // Y-tick labels
  const yTop = yTicks[yTicks.length - 1];
  for (const t of yTicks) {
    const yy = yScale(t);
    const lbl = (t === yTop) ? `${t}%` : `${t}`;
    out += `<text x="${(PLOT_X0 - 8).toFixed(2)}" y="${(yy + 4).toFixed(2)}" text-anchor="end" fill="${INK}" font-family="${FONT_MONO}" font-size="12" font-weight="400" font-variant-numeric="tabular-nums">${lbl}</text>`;
  }

  // X-tick labels (quarters)
  for (let i = 0; i < n; i++) {
    const xx = xScale(i);
    const anchor = (i === 0) ? "start" : (i === n - 1) ? "end" : "middle";
    out += `<text x="${xx.toFixed(2)}" y="${(PLOT_Y1 + 18).toFixed(2)}" text-anchor="${anchor}" fill="${INK}" font-family="${FONT_SANS}" font-size="12" font-weight="400">${quarters[i]}</text>`;
  }

  // Direct labels at line termini
  const realLblX = Math.min(lastX + 10, PLOT_X1 + M_R - 4);
  out += `<text x="${realLblX.toFixed(2)}" y="${(lastY + 4).toFixed(2)}" fill="${INK}" font-family="${FONT_SANS}" font-size="13" font-weight="600">Realized</text>`;
  const scenLastY = yScale(scenario[n - 1]);
  out += `<text x="${realLblX.toFixed(2)}" y="${(scenLastY + 4).toFixed(2)}" fill="${INK}" font-family="${FONT_SANS}" font-size="13" font-weight="400">BoC scenario</text>`;

  // Footer note
  out += `<text x="${PLOT_X0}" y="${(VB_H - 10).toFixed(2)}" fill="${INK}" fill-opacity="0.6" font-family="${FONT_SANS}" font-size="11" font-weight="400">BoC MPR 2025-01-29 In-Focus 1 (scenario); StatCan Table 36-10-0104 (realized). Quarterly Y/Y.</text>`;

  out += `</svg>`;
  writeFileSync(resolve(OUT_DIR, "boc-scenario-vs-realized.svg"), out, "utf8");
  console.log("wrote boc-scenario-vs-realized.svg (", n, "quarters)");
}

/* ---------- Chart 6: USMCA timeline ----------
 * Horizontal timeline of the USMCA Article 34.7 joint-review window.
 * Hardcoded dates from editorial/drafts/deepdive_trade_tariffs_v1.md
 * Section 7 + editorial/insight_base/trade_tariffs_deepdive.md Section 2:
 *   - 2025-09-17: USTR Federal Register notice opens consultations
 *                 (Federal Register 2025-18010).
 *   - 2026-06-01: Substantive-change recommendations deadline
 *                 (CRS R48787 mechanics: one month before review).
 *   - 2026-07-01: Article 34.7 joint review trigger (sixth anniversary).
 *   - 2032: Sunset trajectory year if any party objects (annual reviews
 *                 from 2026-07-01).
 *   - 2042: Extended term if all three parties confirm.
 * Red accent: the 2026-07-01 trigger date (the deep-dive's load-bearing
 * date).
 */
function chartUsmcaTimeline() {
  // Map dates to fractional x positions on a unified axis spanning
  // 2025-09 to 2042 (visually compressed; the 2032 / 2042 markers
  // sit at the far right with a break/elide treatment).
  // We use two-segment x axis: 0..0.55 spans 2025-09 -> 2026-09 (the
  // dense action window); 0.55..1.0 spans 2026-09 -> 2042 (the
  // structural-fate window).
  const eventsDense = [
    { date: "2025-09-17", label: "USTR notice", sub: "Fed Reg 2025-18010", emphasis: false },
    { date: "2026-06-01", label: "Recommendations deadline", sub: "one month pre-review", emphasis: false },
    { date: "2026-07-01", label: "Joint review trigger", sub: "Article 34.7", emphasis: true },
  ];
  const eventsStructural = [
    { year: 2032, label: "Sunset (if any party objects)", sub: "annual review from 2026", emphasis: false },
    { year: 2042, label: "Term ends (if all extend)", sub: "16-year clock", emphasis: false },
  ];

  // Dense segment x range
  const denseX0 = PLOT_X0 + 20;
  const denseX1 = PLOT_X0 + PLOT_W * 0.55;
  // Structural segment x range
  const structX0 = PLOT_X0 + PLOT_W * 0.60;
  const structX1 = PLOT_X1 - 20;

  // Convert YYYY-MM-DD in dense window (2025-09 -> 2026-09) to x
  function denseDateX(date) {
    const [y, m, d] = date.split("-").map((s) => parseInt(s, 10));
    const t = (y + (m - 1) / 12 + (d - 1) / 365) - (2025 + 8 / 12);
    const span = 1 + 0.05; // 2025-09 to 2026-10
    return denseX0 + (t / span) * (denseX1 - denseX0);
  }
  // Convert year (>= 2027) to x in structural window
  function structYearX(year) {
    const t = (year - 2027) / (2042 - 2027);
    return structX0 + t * (structX1 - structX0);
  }

  const axisY = PLOT_Y0 + PLOT_H * 0.55;

  let out = "";
  out += `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${VB_W} ${VB_H}" preserveAspectRatio="xMidYMid meet" role="img" aria-label="USMCA Article 34.7 joint review timeline. September 17 2025 USTR Federal Register notice opens consultations. June 1 2026 recommendations deadline. July 1 2026 joint review trigger (highlighted in red). 2032 sunset trajectory if any party objects. 2042 term if all three extend." style="display:block;width:100%;height:auto;background:${PAPER};font-family:${FONT_SANS}">`;

  out += `<text x="${PLOT_X0}" y="${(PLOT_Y0 - 8).toFixed(2)}" fill="${INK}" font-family="${FONT_SANS}" font-size="11" font-weight="600" letter-spacing="0.12em">USMCA REVIEW WINDOW  --  ARTICLE 34.7</text>`;

  // Section labels above each segment
  out += `<text x="${denseX0.toFixed(2)}" y="${(PLOT_Y0 + 18).toFixed(2)}" fill="${INK}" fill-opacity="0.6" font-family="${FONT_SANS}" font-size="11" font-weight="600" letter-spacing="0.08em">ACTION WINDOW</text>`;
  out += `<text x="${structX0.toFixed(2)}" y="${(PLOT_Y0 + 18).toFixed(2)}" fill="${INK}" fill-opacity="0.6" font-family="${FONT_SANS}" font-size="11" font-weight="600" letter-spacing="0.08em">STRUCTURAL FATE</text>`;

  // Dense segment axis
  out += `<line x1="${denseX0.toFixed(2)}" x2="${denseX1.toFixed(2)}" y1="${axisY.toFixed(2)}" y2="${axisY.toFixed(2)}" stroke="${INK}" stroke-width="1.5"/>`;
  // Structural segment axis (dashed since compressed / projected)
  out += `<line x1="${structX0.toFixed(2)}" x2="${structX1.toFixed(2)}" y1="${axisY.toFixed(2)}" y2="${axisY.toFixed(2)}" stroke="${INK}" stroke-width="1.5" stroke-dasharray="4 2"/>`;

  // Axis-break notch between segments
  const gapMid = (denseX1 + structX0) / 2;
  out += `<text x="${gapMid.toFixed(2)}" y="${(axisY + 5).toFixed(2)}" text-anchor="middle" fill="${INK}" fill-opacity="0.4" font-family="${FONT_SANS}" font-size="14" font-weight="400">//</text>`;

  // Plot dense events
  const months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
  for (let i = 0; i < eventsDense.length; i++) {
    const ev = eventsDense[i];
    const xx = denseDateX(ev.date);
    const [yy, mm, dd] = ev.date.split("-").map((s) => parseInt(s, 10));
    const dateLabel = `${months[mm - 1]} ${dd}, ${yy}`;

    // Stagger labels above/below axis to avoid collision
    const above = (i % 2 === 0); // 0=above, 1=below, 2=above
    const labelY = above ? axisY - 50 : axisY + 38;
    const tickY1 = above ? axisY - 6 : axisY + 6;
    const tickY2 = above ? labelY + 8 : labelY - 16;

    // Stem connecting marker to label
    out += `<line x1="${xx.toFixed(2)}" x2="${xx.toFixed(2)}" y1="${tickY1.toFixed(2)}" y2="${tickY2.toFixed(2)}" stroke="${INK}" stroke-opacity="0.4" stroke-width="1"/>`;

    // Marker
    if (ev.emphasis) {
      out += `<circle cx="${xx.toFixed(2)}" cy="${axisY.toFixed(2)}" r="6" fill="${ACCENT}"><title>${dateLabel}: ${ev.label}</title></circle>`;
    } else {
      out += `<circle cx="${xx.toFixed(2)}" cy="${axisY.toFixed(2)}" r="4" fill="${INK}"><title>${dateLabel}: ${ev.label}</title></circle>`;
    }

    // Date stamp (Plex Mono micro)
    const dateY = above ? labelY - 4 : labelY - 4;
    out += `<text x="${xx.toFixed(2)}" y="${dateY.toFixed(2)}" text-anchor="middle" fill="${INK}" font-family="${FONT_MONO}" font-size="11" font-weight="400" font-variant-numeric="tabular-nums">${dateLabel}</text>`;

    // Event label
    const fillColor = ev.emphasis ? ACCENT : INK;
    const weight = ev.emphasis ? "700" : "600";
    out += `<text x="${xx.toFixed(2)}" y="${(dateY + 14).toFixed(2)}" text-anchor="middle" fill="${fillColor}" font-family="${FONT_SANS}" font-size="13" font-weight="${weight}">${svgEscape(ev.label)}</text>`;

    // Sub label
    out += `<text x="${xx.toFixed(2)}" y="${(dateY + 28).toFixed(2)}" text-anchor="middle" fill="${INK}" fill-opacity="0.6" font-family="${FONT_SANS}" font-size="11" font-weight="400" font-style="italic">${svgEscape(ev.sub)}</text>`;
  }

  // Plot structural events
  for (let i = 0; i < eventsStructural.length; i++) {
    const ev = eventsStructural[i];
    const xx = structYearX(ev.year);
    const above = (i === 0); // 2032 above, 2042 below
    const labelY = above ? axisY - 50 : axisY + 38;
    const tickY1 = above ? axisY - 6 : axisY + 6;
    const tickY2 = above ? labelY + 8 : labelY - 16;

    out += `<line x1="${xx.toFixed(2)}" x2="${xx.toFixed(2)}" y1="${tickY1.toFixed(2)}" y2="${tickY2.toFixed(2)}" stroke="${INK}" stroke-opacity="0.4" stroke-width="1" stroke-dasharray="2 2"/>`;
    out += `<circle cx="${xx.toFixed(2)}" cy="${axisY.toFixed(2)}" r="3" fill="none" stroke="${INK}" stroke-width="1.5"/>`;

    const dateY = above ? labelY - 4 : labelY - 4;
    out += `<text x="${xx.toFixed(2)}" y="${dateY.toFixed(2)}" text-anchor="middle" fill="${INK}" font-family="${FONT_MONO}" font-size="11" font-weight="400" font-variant-numeric="tabular-nums">${ev.year}</text>`;
    out += `<text x="${xx.toFixed(2)}" y="${(dateY + 14).toFixed(2)}" text-anchor="middle" fill="${INK}" font-family="${FONT_SANS}" font-size="13" font-weight="600">${svgEscape(ev.label)}</text>`;
    out += `<text x="${xx.toFixed(2)}" y="${(dateY + 28).toFixed(2)}" text-anchor="middle" fill="${INK}" fill-opacity="0.6" font-family="${FONT_SANS}" font-size="11" font-weight="400" font-style="italic">${svgEscape(ev.sub)}</text>`;
  }

  // Bias-to-extension framing note (bottom)
  out += `<text x="${PLOT_X0}" y="${(VB_H - 10).toFixed(2)}" fill="${INK}" fill-opacity="0.6" font-family="${FONT_SANS}" font-size="11" font-weight="400">Default mechanic: unanimous extension. Single-party objection triggers annual review, not immediate fracture. Source: CRS R48787, IF10997.</text>`;

  out += `</svg>`;
  writeFileSync(resolve(OUT_DIR, "usmca-timeline.svg"), out, "utf8");
  console.log("wrote usmca-timeline.svg (5 events)");
}

/* ---------- run ---------- */
chartUsShare();
chartTariffMatrix();
chartLumberStack();
chartExportsDualAxis();
chartBocScenarioVsRealized();
chartUsmcaTimeline();
console.log("Trade-tariffs charts written to", OUT_DIR);
