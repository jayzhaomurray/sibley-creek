// TEMP one-shot: render the canon house-style policy-paths chart to PNG.
// No dev server. Reads CSVs -> builds canon SVG -> screenshots via Chromium.
import { readFileSync, writeFileSync, unlinkSync } from "node:fs";
import { pathToFileURL } from "node:url";
import { chromium } from "@playwright/test";

const ROOT = "C:/Users/jayzh/projects/macro-research-department/";
const OUT = ROOT + "work/research/shadow_rate/boc_policy_paths_chartbook.png";
const TMP = ROOT + "work/research/shadow_rate/_chart_tmp.html";

// ---- data ----------------------------------------------------------------
function readCsv(rel) {
  const txt = readFileSync(ROOT + rel, "utf-8").trim();
  const [head, ...rows] = txt.split(/\r?\n/);
  const cols = head.split(",");
  return rows.map((r) => {
    const c = r.split(",");
    const o = {};
    cols.forEach((k, i) => (o[k] = c[i]));
    return o;
  });
}
function qToDate(q) {
  const y = q.slice(0, 4), n = parseInt(q[5], 10);
  return `${y}-${String((n - 1) * 3 + 1).padStart(2, "0")}-01`;
}
function decYear(date) {
  const m = date.match(/^(\d{4})-(\d{2})(?:-(\d{2}))?/);
  const y = +m[1], mm = +m[2], dd = m[3] !== undefined ? +m[3] : NaN;
  if (!Number.isNaN(dd)) {
    const leap = (y % 4 === 0 && y % 100 !== 0) || y % 400 === 0;
    const md = [31, leap ? 29 : 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
    let doy = dd; for (let i = 0; i < mm - 1; i++) doy += md[i];
    return y + (doy - 0.5) / (leap ? 366 : 365);
  }
  return y + (mm - 0.5) / 12;
}
function tail(series, nMonths, freq) {
  const n = freq === "quarterly" ? Math.max(8, Math.ceil(nMonths / 3)) : nMonths;
  return series.length <= n ? series : series.slice(series.length - n);
}

const hist = readCsv("data/processed/overnight_rate_target.csv").map((r) => ({ date: r.date, value: +r.value }));
const staff = readCsv("data/processed/boc_shadow_rate.csv").map((r) => ({ date: r.date, value: +r.value }));
const mkt = readCsv("data/raw/corra_futures_curve.csv").map((r) => ({ date: qToDate(r.quarter), value: +r.implied_target }));

// Extend the staff path flat at its terminal value out to the market path's
// last date so both forward lines reach the same right edge (Jay's ask:
// "assume it keeps holding flat once it reaches terminal").
const mktLastDate = mkt[mkt.length - 1].date;
const staffLast = staff[staff.length - 1];
if (mktLastDate > staffLast.date) staff.push({ date: mktLastDate, value: staffLast.value });

const primData = tail(hist, 60, "monthly");
const secData = tail(staff, 60, "quarterly");
const terData = tail(mkt, 60, "quarterly");

// ---- geometry (pinned to canon) ------------------------------------------
const VB_W = 720, VB_H = 405, M_L = 56, M_R = 96, M_T = 18, M_B = 40;
const X0 = M_L, Y0 = M_T, PW = VB_W - M_L - M_R, PH = VB_H - M_T - M_B;
const X1 = X0 + PW, Y1 = Y0 + PH;

const allX = [...primData, ...secData, ...terData].map((d) => decYear(d.date));
const xMin = Math.min(...allX), xMax = Math.max(...allX);
const vals = [...primData, ...secData, ...terData].map((d) => d.value);
let yLo = Math.min(...vals), yHi = Math.max(...vals);
const span = (yHi - yLo) || 1;
yLo -= span * 0.10; yHi += span * 0.10;
// reference band expansion
if (2.25 < yLo) yLo = 2.25 - span * 0.05;
if (3.25 > yHi) yHi = 3.25 + span * 0.05;
const yRange = yHi - yLo;
const xS = (yr) => X0 + ((yr - xMin) / (xMax - xMin)) * PW;
const yS = (v) => Y0 + PH - ((v - yLo) / yRange) * PH;

// nice y ticks (stride 1 over this domain)
function pickStride(lo, hi, t = 5) {
  const s = (hi - lo) / t, mag = Math.pow(10, Math.floor(Math.log10(s))), nrm = s / mag;
  const nice = nrm < 1.5 ? 1 : nrm < 3 ? 2 : nrm < 4 ? 2.5 : nrm < 7 ? 5 : 10;
  return nice * mag;
}
const stride = pickStride(yLo, yHi);
const yTicks = [];
for (let v = Math.ceil(yLo / stride) * stride; v <= yHi + 1e-9; v += stride) yTicks.push(+v.toFixed(6));

// x year ticks
const yrTicks = [];
for (let yr = Math.ceil(xMin); yr <= Math.floor(xMax); yr++) {
  const d = yr + (1 - 0.5) / 12;
  if (d >= xMin && d <= xMax) yrTicks.push({ x: xS(d), label: String(yr) });
}
const xStride = Math.max(1, Math.ceil(yrTicks.length / 5));
const xTicks = yrTicks.filter((_, i) => i % xStride === 0);

// Band-label x: align the start of the lettering with the 2026 x-axis tick.
const tick2026 = yrTicks.find((t) => t.label === "2026");
const bandLabelX = tick2026 ? tick2026.x : X0 + 6;

// paths
function line(series, step) {
  let d = "", started = false, prevY = null;
  for (const p of series) {
    const x = xS(decYear(p.date)), y = yS(p.value);
    if (!started) { d += `M${x.toFixed(2)} ${y.toFixed(2)} `; started = true; }
    else if (step && prevY !== null) { d += `L${x.toFixed(2)} ${prevY.toFixed(2)} L${x.toFixed(2)} ${y.toFixed(2)} `; }
    else d += `L${x.toFixed(2)} ${y.toFixed(2)} `;
    prevY = y;
  }
  return d.trim();
}
const primPath = line(primData, true);
const secPath = line(secData, false);
const terPath = line(terData, false);
const lastP = primData[primData.length - 1];
const lastS = secData[secData.length - 1];
const lastT = terData[terData.length - 1];
const pX = xS(decYear(lastP.date)), pY = yS(lastP.value);
const sX = xS(decYear(lastS.date)), sY = yS(lastS.value);
const tX = xS(decYear(lastT.date)), tY = yS(lastT.value);

// band
const bandTop = yS(3.25), bandBot = yS(2.25);

const svg = `
<svg viewBox="0 0 ${VB_W} ${VB_H}" class="cc" xmlns="http://www.w3.org/2000/svg">
  <rect class="cc-band" x="${X0}" y="${bandTop.toFixed(2)}" width="${PW}" height="${(bandBot - bandTop).toFixed(2)}"/>
  <text class="cc-band-label" x="${bandLabelX.toFixed(2)}" y="${Math.max(Y0 + 10, bandTop - 4).toFixed(2)}">NEUTRAL RANGE</text>
  ${yTicks.map((v) => `<line class="cc-grid" x1="${X0}" y1="${yS(v).toFixed(2)}" x2="${X1}" y2="${yS(v).toFixed(2)}"/>`).join("")}
  <path class="cc-tertiary" d="${terPath}" fill="none"/>
  <path class="cc-secondary" d="${secPath}" fill="none"/>
  <path class="cc-line" d="${primPath}" fill="none"/>
  <circle class="cc-dot-ink" cx="${sX.toFixed(2)}" cy="${sY.toFixed(2)}" r="3"/>
  <circle class="cc-dot-ink" cx="${tX.toFixed(2)}" cy="${tY.toFixed(2)}" r="3"/>
  <circle class="cc-dot" cx="${pX.toFixed(2)}" cy="${pY.toFixed(2)}" r="4"/>
  <rect class="cc-frame" x="${X0}" y="${Y0}" width="${PW}" height="${PH}"/>
  ${xTicks.map((t) => `<line class="cc-xtick" x1="${t.x.toFixed(2)}" y1="${Y1}" x2="${t.x.toFixed(2)}" y2="${Y1 + 4}"/><text class="cc-xtick-label" x="${t.x.toFixed(2)}" y="${Y1 + 18}" text-anchor="middle">${t.label}</text>`).join("")}
  ${yTicks.map((v, i) => { const top = i === yTicks.length - 1; const txt = (Number.isInteger(v) ? v.toFixed(0) : v.toFixed(1)) + (top ? "%" : "%"); return `<text class="cc-ytick-label" x="${X0 - 8}" y="${(yS(v) + 4).toFixed(2)}" text-anchor="end">${txt}</text>`; }).join("")}
  <text class="cc-dl-sec" x="${(sX + 10).toFixed(2)}" y="${(sY + 4).toFixed(2)}" text-anchor="start"><tspan x="${(sX + 10).toFixed(2)}">BoC staff path</tspan><tspan x="${(sX + 10).toFixed(2)}" dy="14" class="cc-dl-sub">(Sibley Creek est.)</tspan></text>
  <text class="cc-dl-ter" x="${(tX + 10).toFixed(2)}" y="${(tY + 4).toFixed(2)}" text-anchor="start">CORRA futures</text>
</svg>`;

const TITLE = "Markets are pricing too many hikes.";
const SUBHEAD = "Bank of Canada overnight rate, %";

const html = `<!doctype html><html><head><meta charset="utf-8">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Manrope:wght@200;400;600;800&family=IBM+Plex+Mono:wght@400&display=swap" rel="stylesheet">
<style>
  :root{--ink:#000;--accent:#E63946;--paper:#fff;--sans:'Manrope','Helvetica Neue',Arial,sans-serif;--mono:'IBM Plex Mono',Consolas,monospace;}
  body{margin:0;background:#fff;}
  #plate{display:inline-block;background:#fff;padding:18px 52px 10px 14px;}
  .title{margin:0 0 3px 34px;font-family:var(--sans);font-weight:800;font-size:23px;letter-spacing:-0.012em;color:var(--ink);line-height:1.12;}
  .subhead{margin:0 0 6px 34px;font-family:var(--sans);font-weight:600;font-size:12px;letter-spacing:0.18em;text-transform:uppercase;color:var(--ink);opacity:0.6;}
  .cc{display:block;width:760px;height:auto;overflow:visible;font-family:var(--sans);}
  .cc-band{fill:rgba(21,23,26,0.14);}
  .cc-band-label{fill:var(--ink);font-family:var(--sans);font-size:10px;font-weight:600;letter-spacing:0.16em;fill-opacity:0.7;}
  .cc-grid{stroke:var(--ink);stroke-width:1;stroke-opacity:0.18;shape-rendering:crispEdges;}
  .cc-line{stroke:var(--ink);stroke-width:1.5;stroke-linejoin:round;stroke-linecap:round;vector-effect:non-scaling-stroke;}
  .cc-secondary{stroke:var(--ink);stroke-width:1;stroke-dasharray:4 2;stroke-linejoin:round;vector-effect:non-scaling-stroke;}
  .cc-tertiary{stroke:var(--ink);stroke-width:1;stroke-dasharray:2 3;stroke-linejoin:round;vector-effect:non-scaling-stroke;}
  .cc-dot{fill:var(--accent);}
  .cc-dot-ink{fill:var(--ink);}
  .cc-frame{fill:none;stroke:var(--ink);stroke-width:1;shape-rendering:crispEdges;}
  .cc-xtick{stroke:var(--ink);stroke-width:1;shape-rendering:crispEdges;}
  .cc-xtick-label{fill:var(--ink);font-family:var(--sans);font-size:12px;font-weight:400;font-variant-numeric:tabular-nums;}
  .cc-ytick-label{fill:var(--ink);font-family:var(--mono);font-size:12px;font-weight:400;font-variant-numeric:tabular-nums;}
  .cc-dl-sec{fill:var(--ink);font-family:var(--sans);font-size:13px;font-weight:600;}
  .cc-dl-ter{fill:var(--ink);font-family:var(--sans);font-size:13px;font-weight:400;}
  .cc-dl-sub{font-weight:400;fill-opacity:0.75;}
</style></head><body><div id="plate"><div class="title">${TITLE}</div><div class="subhead">${SUBHEAD}</div>${svg}</div></body></html>`;

writeFileSync(TMP, html, "utf-8");

const browser = await chromium.launch();
const page = await browser.newPage({ deviceScaleFactor: 3 });
await page.goto(pathToFileURL(TMP).href, { waitUntil: "load" });
await page.evaluate(() => document.fonts.ready);
await page.waitForTimeout(500);
const el = await page.$("#plate");
await el.screenshot({ path: OUT });
await browser.close();
unlinkSync(TMP);
console.log("wrote", OUT);
console.log("staff terminal", lastS.value, "market terminal", lastT.value);
