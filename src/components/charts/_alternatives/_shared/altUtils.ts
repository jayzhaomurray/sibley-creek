/*
 * altUtils - shared helpers for the chart-alternatives review page.
 *
 * Used ONLY by components under src/components/charts/_alternatives/.
 * Not part of the production canon.
 *
 * These helpers read raw CSVs from data/raw/ at build time (Node fs) so
 * alternatives can experiment with series that the pipeline does not
 * surface through data/site/panel_data/<section>.json. Production
 * components must NOT call these helpers - they exist to make the
 * alternatives-review iteration fast.
 */

import { readFileSync } from "node:fs";
import { resolve } from "node:path";

export interface AltPoint {
  date: string;
  value: number | null;
}

/** Read a two-column date,value CSV from data/raw/. */
export function readCsv(name: string): AltPoint[] {
  const p = resolve(process.cwd(), "data", "raw", name);
  const txt = readFileSync(p, "utf-8");
  const lines = txt.split(/\r?\n/).filter((l) => l.length > 0);
  const out: AltPoint[] = [];
  for (let i = 1; i < lines.length; i++) {
    const line = lines[i]!;
    const idx = line.indexOf(",");
    if (idx < 0) continue;
    const date = line.slice(0, idx).trim();
    const raw = line.slice(idx + 1).trim();
    if (!date) continue;
    const value = raw === "" || raw === "NA" || raw === "null" ? null : Number(raw);
    out.push({ date, value: typeof value === "number" && !Number.isNaN(value) ? value : null });
  }
  return out;
}

/** Parse YYYY-MM-DD or YYYY-MM into a decimal year. */
export function decYear(date: string): number {
  const m = date.match(/^(\d{4})-(\d{2})(?:-(\d{2}))?/);
  if (!m) return NaN;
  const y = parseInt(m[1]!, 10);
  const mm = parseInt(m[2]!, 10);
  const dd = m[3] !== undefined ? parseInt(m[3], 10) : NaN;
  if (!Number.isNaN(dd)) {
    const isLeap = (y % 4 === 0 && y % 100 !== 0) || y % 400 === 0;
    const monthDays = [31, isLeap ? 29 : 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
    let doy = dd;
    for (let i = 0; i < mm - 1; i++) doy += monthDays[i]!;
    const totalDays = isLeap ? 366 : 365;
    return y + (doy - 0.5) / totalDays;
  }
  return y + (mm - 0.5) / 12;
}

/** Keep last n observations. */
export function tail<T>(arr: T[], n: number): T[] {
  if (arr.length <= n) return arr;
  return arr.slice(arr.length - n);
}

/** Year-over-year percent change (12-period lag, monthly). */
export function yoy(series: AltPoint[]): AltPoint[] {
  const out: AltPoint[] = [];
  for (let i = 0; i < series.length; i++) {
    const here = series[i]!;
    const prev = series[i - 12];
    if (!prev || prev.value === null || here.value === null || prev.value === 0) {
      out.push({ date: here.date, value: null });
    } else {
      out.push({ date: here.date, value: ((here.value - prev.value) / prev.value) * 100 });
    }
  }
  return out;
}

/** Trailing 3-period moving average. */
export function tma(series: AltPoint[], window: number): AltPoint[] {
  const out: AltPoint[] = [];
  for (let i = 0; i < series.length; i++) {
    if (i < window - 1) {
      out.push({ date: series[i]!.date, value: null });
      continue;
    }
    let sum = 0;
    let n = 0;
    for (let k = 0; k < window; k++) {
      const v = series[i - k]!.value;
      if (typeof v === "number" && !Number.isNaN(v)) {
        sum += v;
        n += 1;
      }
    }
    out.push({ date: series[i]!.date, value: n > 0 ? sum / n : null });
  }
  return out;
}

/**
 * Subtract series-B from series-A on aligned dates. Both must share the
 * same date grid; returns the spread A - B where both are non-null.
 */
export function diff(a: AltPoint[], b: AltPoint[]): AltPoint[] {
  const map = new Map<string, number>();
  for (const p of b) if (p.value !== null) map.set(p.date, p.value);
  const out: AltPoint[] = [];
  for (const p of a) {
    const bv = map.get(p.date);
    if (p.value === null || bv === undefined) {
      out.push({ date: p.date, value: null });
    } else {
      out.push({ date: p.date, value: p.value - bv });
    }
  }
  return out;
}

/** Compute min/max ignoring nulls. */
export function minMax(values: Array<number | null>): [number, number] {
  let lo = Infinity;
  let hi = -Infinity;
  for (const v of values) {
    if (typeof v !== "number" || Number.isNaN(v)) continue;
    if (v < lo) lo = v;
    if (v > hi) hi = v;
  }
  if (!Number.isFinite(lo)) lo = 0;
  if (!Number.isFinite(hi)) hi = 1;
  return [lo, hi];
}

/** Index a series to first non-null observation = 100. */
export function indexTo100(series: AltPoint[]): AltPoint[] {
  let base: number | null = null;
  for (const p of series) {
    if (typeof p.value === "number" && !Number.isNaN(p.value)) {
      base = p.value;
      break;
    }
  }
  if (base === null || base === 0) return series.map((p) => ({ date: p.date, value: null }));
  return series.map((p) => ({
    date: p.date,
    value: p.value !== null ? (p.value / base!) * 100 : null,
  }));
}

/** Index a series to value=100 at a chosen anchor date (or nearest before). */
export function indexAt(series: AltPoint[], anchorDate: string): AltPoint[] {
  let base: number | null = null;
  for (const p of series) {
    if (p.date <= anchorDate && typeof p.value === "number" && !Number.isNaN(p.value)) {
      base = p.value;
    } else if (p.date > anchorDate) break;
  }
  if (base === null || base === 0) return series.map((p) => ({ date: p.date, value: null }));
  return series.map((p) => ({
    date: p.date,
    value: p.value !== null ? (p.value / base!) * 100 : null,
  }));
}

/** Drop leading/trailing nulls for clean line termination. */
export function trimNulls(series: AltPoint[]): AltPoint[] {
  let lo = 0;
  let hi = series.length - 1;
  while (lo < series.length && series[lo]!.value === null) lo++;
  while (hi >= 0 && series[hi]!.value === null) hi--;
  if (lo > hi) return [];
  return series.slice(lo, hi + 1);
}

/** Canon viewbox + margins, exported as constants for alternative SVGs. */
export const VB = {
  W: 720,
  H: 405,
  ML: 56,
  MR: 96,
  MT: 44,
  MB: 40,
};
export const PLOT = {
  X0: VB.ML,
  Y0: VB.MT,
  W: VB.W - VB.ML - VB.MR,
  H: VB.H - VB.MT - VB.MB,
  X1: VB.ML + (VB.W - VB.ML - VB.MR),
  Y1: VB.MT + (VB.H - VB.MT - VB.MB),
};

/** Pick a y-tick stride that yields 3-5 ticks. */
export function pickStride(lo: number, hi: number): number {
  const span = hi - lo;
  const candidates = [0.05, 0.1, 0.25, 0.5, 1, 2, 2.5, 5, 10, 20, 25, 50, 100, 200, 500, 1000, 2000, 5000, 10000];
  for (const s of candidates) {
    const n = Math.round(span / s);
    if (n >= 3 && n <= 6) return s;
  }
  return Math.max(0.01, span / 4);
}

/** Format a y-axis tick value. */
export function fmtTick(v: number, decimals = 1): string {
  const a = Math.abs(v);
  if (a >= 10000) return v.toFixed(0);
  if (a >= 1000) return v.toFixed(0);
  if (a >= 100) return v.toFixed(0);
  if (a >= 10) return v.toFixed(decimals);
  if (a >= 1) return v.toFixed(decimals);
  return v.toFixed(Math.max(decimals, 2));
}

/** Generate year-anchor x-ticks, capped at 5. */
export function yearTicksFromX(xMin: number, xMax: number, xScale: (yr: number) => number) {
  const yearStart = Math.ceil(xMin);
  const yearEnd = Math.floor(xMax);
  const all: Array<{ x: number; label: string }> = [];
  for (let yr = yearStart; yr <= yearEnd; yr++) {
    const decY = yr + (1 - 0.5) / 12;
    if (decY < xMin || decY > xMax) continue;
    all.push({ x: xScale(decY), label: String(yr) });
  }
  const stride = Math.max(1, Math.ceil(all.length / 5));
  return all.filter((_, i) => i % stride === 0);
}
