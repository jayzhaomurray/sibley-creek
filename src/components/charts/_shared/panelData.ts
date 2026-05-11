/*
 * panelData.ts - shared types + helpers for panels consuming the
 * pipeline's data/site/panel_data/<section>.json files.
 *
 * The pipeline emits a uniform per-panel shape:
 *
 *   {
 *     "panel-N": {
 *       "panelNum": N,
 *       "file": "...",
 *       "expectedStatus": "WIRED" | "NEAR" | "MISSING",
 *       "primary":   { key, label, tier, data, unit, frequency, asOfISO, source, sourceUrl, sourceId, releaseDate } | null,
 *       "secondary": { ...same shape... } | null
 *     }
 *   }
 *
 * Each series' `data` is an array of { date: "YYYY-MM-DD", value: number }.
 * Panels can either render the primary series directly (when its semantic
 * matches the panel's editorial argument, e.g. an already-% Y/Y line) or
 * render the "DATA NOT YET WIRED" empty state when the panel requires
 * processing that the pipeline has not yet produced.
 *
 * Helpers here are intentionally minimal - they keep the section-page
 * frontmatter terse and avoid copy-pasting the same null-coalescing logic
 * into every Panel component.
 */

export interface SeriesPoint {
  date: string;
  value: number | null;
}

export interface PanelSeries {
  key: string;
  label: string;
  tier?: string;
  data: SeriesPoint[];
  unit: string | null;
  /**
   * Canonical ValueKind (from format.ts) when the backend emits one.
   * Optional during the transition: PanelLiveChart falls back to
   * inferKindFromUnit(unit) when this is absent.
   */
  kind?: string | null;
  /**
   * Pre-formatted scalar string for the latest print, when the backend
   * pre-renders it. Optional; PanelLiveChart uses this when present in
   * preference to running fmtValue locally.
   */
  formatted?: string | null;
  frequency?: string | null;
  asOfISO?: string | null;
  source?: string | null;
  sourceUrl?: string | null;
  sourceId?: string | null;
  releaseDate?: string | null;
}

export interface PanelData {
  panelNum: number;
  file?: string;
  expectedStatus?: "WIRED" | "NEAR" | "MISSING" | string;
  notes?: string | null;
  primary: PanelSeries | null;
  secondary: PanelSeries | null;
  /**
   * Third series, when the panel's editorial argument calls for one
   * (e.g. the markets-2 GoC curve view: 2y / 5y / 10y). Most panels
   * leave this null. Consumed by PanelLiveChart via its `tertiary` prop.
   */
  tertiary?: PanelSeries | null;
  /** Pipeline emits additional fields (extras) which we ignore. */
  [key: string]: unknown;
}

export interface PanelDataFile {
  section: string;
  generatedAt: string;
  panels: Record<string, PanelData>;
  [key: string]: unknown;
}

/**
 * Pull a panel entry out of the section JSON file. Returns null when the
 * key is absent OR when the entry has no usable primary series (no data
 * points). Either condition triggers the "DATA NOT YET WIRED" path.
 *
 * Accepts `unknown` because the JSON-imported shape carries extra fields
 * (tertiary, extras) and nullable `notes` that the strict typed
 * `PanelDataFile` interface narrows away. Runtime shape is validated.
 */
export function pickPanel(
  file: unknown,
  panelNum: number,
): PanelData | null {
  if (!file || typeof file !== "object") return null;
  const panels = (file as { panels?: unknown }).panels;
  if (!panels || typeof panels !== "object") return null;
  const key = `panel-${panelNum}`;
  const entry = (panels as Record<string, unknown>)[key];
  if (!entry || typeof entry !== "object") return null;
  const e = entry as PanelData;
  const prim = e.primary;
  if (!prim || !Array.isArray(prim.data) || prim.data.length === 0) return null;
  return e;
}

/**
 * Parse a YYYY-MM-DD (or YYYY-MM) date into a decimal year value usable
 * by x-scale math. Defensive against malformed strings - returns NaN if
 * the date is unparseable.
 *
 * BOTH grains must round-trip through the same scale: daily and monthly
 * series often share a chart axis, and we cannot collapse all daily
 * observations within a month onto a single x-coordinate (the prior
 * `y + (mm - 0.5)/12` formula did exactly that, producing vertical
 * stair-stack polylines on every daily series - see chart-builder
 * 2026-05-11 diagnosis).
 *
 *   - YYYY-MM-DD: year + dayOfYear / daysInYear (leap-aware).
 *   - YYYY-MM:    year + (month - 0.5) / 12. Mid-month anchor matches
 *                 the monthly-data convention used by every section.
 */
export function decYear(date: string): number {
  const m = date.match(/^(\d{4})-(\d{2})(?:-(\d{2}))?/);
  if (!m) return NaN;
  const y = parseInt(m[1]!, 10);
  const mm = parseInt(m[2]!, 10);
  const dd = m[3] !== undefined ? parseInt(m[3], 10) : NaN;
  if (!Number.isNaN(dd)) {
    // Daily grain: convert to day-of-year (1-indexed) and divide by the
    // year's day count. Anchor each day at its mid-point so the first
    // and last days of a year sit a hair inside the year boundary.
    const isLeap = (y % 4 === 0 && y % 100 !== 0) || y % 400 === 0;
    const monthDays = [31, isLeap ? 29 : 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
    let doy = dd; // day within current month
    for (let i = 0; i < mm - 1; i++) doy += monthDays[i]!;
    const totalDays = isLeap ? 366 : 365;
    return y + (doy - 0.5) / totalDays;
  }
  // Monthly grain (no day component): mid-month anchor.
  return y + (mm - 0.5) / 12;
}

/**
 * Map a pipeline unit string (eg "%", "CAD billions", "C$ trillions,
 * chained 2017", "CAD per USD", "USD/barrel") to a short y-tick suffix
 * for the topmost tick. Matches the homepage tile convention so panels
 * read consistently across the site.
 */
export function unitSuffix(unit: string | null | undefined): string {
  if (!unit) return "";
  const u = unit.toLowerCase();
  if (u === "%" || u.startsWith("% ") || u.includes(" %")) return "%";
  if (u.includes("cad per usd")) return "";
  if (u.includes("cad billions") || u.includes("c$ billions")) return "B";
  if (u.includes("cad millions") || u.includes("c$ millions")) return "M";
  if (u.includes("c$ trillions") || u.includes("cad trillions")) return "T";
  if (u.includes("usd/barrel")) return "";
  if (u.includes("cad/hour")) return "";
  if (u.includes("persons")) return "";
  if (u.includes("units")) return "";
  if (u.includes("index")) return "";
  if (u.includes("pp")) return "pp";
  return "";
}

/**
 * Format a numeric value for a y-tick label given the series unit. Picks
 * decimal precision adaptively based on magnitude.
 */
export function fmtTick(v: number): string {
  const a = Math.abs(v);
  if (a >= 1000) return v.toFixed(0);
  if (a >= 100) return v.toFixed(0);
  if (a >= 10) return v.toFixed(1);
  if (a >= 1) return v.toFixed(2);
  return v.toFixed(3);
}

/**
 * Trim a series to the last `nMonths` monthly observations (or
 * approximate equivalent for daily/quarterly). For daily, keeps
 * `nMonths * 22` observations. For quarterly, keeps `nMonths / 3`.
 * Useful when the pipeline emits 20+ years of history but the panel
 * wants a 5-year window.
 */
export function tailWindow(
  series: SeriesPoint[],
  nMonths: number,
  frequency?: string | null,
): SeriesPoint[] {
  let n: number;
  if (frequency === "daily") n = nMonths * 22;
  else if (frequency === "quarterly") n = Math.max(8, Math.ceil(nMonths / 3));
  else n = nMonths;
  if (series.length <= n) return series;
  return series.slice(series.length - n);
}
