/*
 * format.ts - canonical scaling + rounding for chart-rendered numbers.
 *
 * Mirrors pipeline/io/format.py (backend). Backend will start emitting
 * `kind` on each panel_data series; until it does, PanelLiveChart infers
 * `kind` from the existing `unit` string (see `inferKindFromUnit` below).
 *
 * Character caps (load-bearing - tied to the 96px right gutter on the
 * 720-wide canon viewBox; Plex Mono 12px gives ~6-7 chars before clip):
 *
 *   - value (headline / direct):  max 8
 *   - tick:                       max 6
 *   - direct label (series name): max 14 (set per panel)
 *   - delta:                      max 8
 *
 * The formatter NEVER produces longer strings: scale up (M -> B), reduce
 * decimals (1 max), drop sign space if still long, round harder.
 *
 * Scaling rules (per dispatch):
 *   - Counts:        <1k -> int; 1k-1M -> "Nk"; >=1M -> "N.NM"; >=1B -> "N.NB"
 *   - Currency CAD (input is millions):
 *       >=1000 -> "$N.NB"; >=1 -> "$NM"; <1 -> "$N.NM"
 *   - Percent:       "N.N%" (1 decimal max); never >2 chars before the
 *                    decimal except for ratios that genuinely run higher
 *   - pp deltas:     always signed, 1 decimal max, e.g. "+0.5 pp"
 *   - bps:           always signed integer, e.g. "+25 bps"
 *   - FX:            "1.369" (3-4 chars, no separator)
 *   - Index:         10k-100k -> "34.1k"; 100k+ -> "N.NM"
 *
 * Backend single-source-of-truth note: if a panel_data emits a
 * pre-formatted string field (`primary.formatted` etc), PanelLiveChart
 * should prefer that string and skip these helpers. Today none do, so
 * we always format here.
 */

export type ValueKind =
  | "percent"        // CPI Y/Y, unrate, HPI Y/Y -> "2.3%", "6.9%", "-4.6%"
  | "percent_pp"     // deltas in pp -> "+0.5 pp", "-0.2 pp"
  | "basis_points"   // rate moves -> "+25 bps"
  | "rate_level"     // overnight rate -> "2.25%"
  | "currency_cad"   // trade balance, fed budget -> "$5.7B"
  | "fx"             // USDCAD -> "1.369"
  | "index_level"    // TSX, productivity index -> "34.1k" or "34,078"
  | "count"          // EI beneficiaries -> "1.16M" or "455k"
  | "ratio";         // DSR, affordability -> "18.0%"

const VALUE_CAP = 8;
const TICK_CAP = 6;
const DELTA_CAP = 8;

// --- helpers --------------------------------------------------------------

function signOf(n: number): string {
  if (n > 0) return "+";
  if (n < 0) return "-";
  return "";
}

function absStr(n: number, decimals: number): string {
  return Math.abs(n).toFixed(decimals);
}

function trimLen(s: string, cap: number): string {
  // Last-resort length guard. Drops decimals one at a time, then drops
  // the leading "+" sign if necessary (never the "-" - a negative number
  // must read as negative).
  if (s.length <= cap) return s;
  // Try collapsing ".X" -> ""
  const decRe = /\.\d+/;
  if (decRe.test(s)) {
    const collapsed = s.replace(decRe, "");
    if (collapsed.length <= cap) return collapsed;
  }
  // Drop leading "+" if it's the only thing pushing us over
  if (s.startsWith("+") && s.length - 1 <= cap) return s.slice(1);
  return s;
}

// --- count: 1234567 -> "1.2M" ---------------------------------------------
function fmtCount(v: number, cap: number, opts: { decimals?: number } = {}): string {
  const dec = opts.decimals ?? 1;
  const a = Math.abs(v);
  const sgn = v < 0 ? "-" : "";
  let body: string;
  if (a >= 1e9) {
    body = `${(a / 1e9).toFixed(dec)}B`;
  } else if (a >= 1e6) {
    body = `${(a / 1e6).toFixed(dec)}M`;
  } else if (a >= 1e3) {
    // 1k-1M: prefer integer "k" if it fits, else "N.Nk"
    const intK = Math.round(a / 1e3);
    if (intK >= 10) {
      body = `${intK}k`;
    } else {
      body = `${(a / 1e3).toFixed(dec)}k`;
    }
  } else {
    body = `${Math.round(a)}`;
  }
  return trimLen(sgn + body, cap);
}

// --- currency_cad: input is millions ---------------------------------------
// >=1000 (i.e. >= 1 B$): "$N.NB"
// >=1   (>= 1 M$):       "$NM"   (round to int) or "$N.NM" for the 1-10 range
// <1    (sub-million):   "$N.NM" or fall back to "$Nk"
function fmtCurrencyCAD(v: number, cap: number): string {
  const a = Math.abs(v);
  const sgn = v < 0 ? "-" : "";
  // Exact zero crossings on currency: render as "$0" (no scale suffix).
  // This shows up on zero-line ticks for diverging series (trade balance,
  // fiscal balance). "$0.00M" reads as a typo; "$0" reads as the axis.
  if (a < 1e-9) return "$0";
  let body: string;
  if (a >= 1_000_000) {
    // value is in M$, so >= 1,000,000 M$ = >= 1 T$
    body = `$${(a / 1_000_000).toFixed(1)}T`;
  } else if (a >= 1000) {
    body = `$${(a / 1000).toFixed(1)}B`;
  } else if (a >= 100) {
    body = `$${Math.round(a)}M`;
  } else if (a >= 10) {
    body = `$${a.toFixed(0)}M`;
  } else if (a >= 1) {
    body = `$${a.toFixed(1)}M`;
  } else if (a >= 0.001) {
    // sub-million; show as thousands of $ ("M is too coarse")
    body = `$${(a * 1000).toFixed(0)}k`;
  } else {
    body = `$${a.toFixed(2)}M`;
  }
  return trimLen(sgn + body, cap);
}

// --- percent / rate_level / ratio -----------------------------------------
function fmtPercent(v: number, cap: number, opts: { decimals?: number; signed?: boolean } = {}): string {
  const dec = opts.decimals ?? 1;
  const a = Math.abs(v);
  let str: string;
  // Drop the decimal when abs >= 100 (3-digit pre-decimal would blow the cap)
  if (a >= 100) {
    str = `${a.toFixed(0)}%`;
  } else {
    str = `${a.toFixed(dec)}%`;
  }
  if (opts.signed) {
    str = signOf(v) + str;
  } else if (v < 0) {
    str = "-" + str;
  }
  return trimLen(str, cap);
}

// --- percent_pp deltas -----------------------------------------------------
function fmtPP(v: number, cap: number): string {
  const dec = Math.abs(v) >= 10 ? 0 : 1;
  const body = `${signOf(v) || "+"}${absStr(v, dec)} pp`;
  return trimLen(body, cap);
}

// --- basis points ---------------------------------------------------------
function fmtBPS(v: number, cap: number): string {
  const body = `${signOf(v) || "+"}${Math.round(Math.abs(v))} bps`;
  return trimLen(body, cap);
}

// --- FX -------------------------------------------------------------------
function fmtFX(v: number, cap: number): string {
  // Default 3 decimals: "1.369". If abs < 0.1, 4 decimals.
  const dec = Math.abs(v) < 0.1 ? 4 : 3;
  const body = (v < 0 ? "-" : "") + Math.abs(v).toFixed(dec);
  return trimLen(body, cap);
}

// --- index_level ----------------------------------------------------------
// 0-1000 -> integer or 1 decimal; 1000-10000 -> integer (no separator);
// 10k-100k -> "34.1k"; 100k+ -> "N.NM"
function fmtIndex(v: number, cap: number): string {
  const a = Math.abs(v);
  const sgn = v < 0 ? "-" : "";
  let body: string;
  if (a >= 1e6) {
    body = `${(a / 1e6).toFixed(1)}M`;
  } else if (a >= 1e4) {
    body = `${(a / 1e3).toFixed(1)}k`;
  } else if (a >= 1000) {
    body = `${Math.round(a)}`;
  } else if (a >= 100) {
    body = `${a.toFixed(0)}`;
  } else if (a >= 10) {
    body = `${a.toFixed(1)}`;
  } else {
    body = `${a.toFixed(2)}`;
  }
  return trimLen(sgn + body, cap);
}

// --- public API -----------------------------------------------------------

/**
 * Format a value for direct on-chart use (headline number, direct label).
 * Cap: 8 chars.
 */
export function fmtValue(value: number, kind: ValueKind): string {
  if (!Number.isFinite(value)) return "-";
  switch (kind) {
    case "percent":
    case "rate_level":
    case "ratio":
      return fmtPercent(value, VALUE_CAP);
    case "percent_pp":
      return fmtPP(value, VALUE_CAP);
    case "basis_points":
      return fmtBPS(value, VALUE_CAP);
    case "currency_cad":
      return fmtCurrencyCAD(value, VALUE_CAP);
    case "fx":
      return fmtFX(value, VALUE_CAP);
    case "index_level":
      return fmtIndex(value, VALUE_CAP);
    case "count":
      return fmtCount(value, VALUE_CAP);
    default:
      return fmtIndex(value, VALUE_CAP);
  }
}

/**
 * Format a delta. Always signed. Cap: 8 chars.
 *
 * Deltas have their own conventions:
 *  - rate-level / percent / ratio deltas read as pp by default
 *  - basis_points stays as bps
 *  - everything else gets the same scaler with a leading "+" or "-"
 */
export function fmtDelta(delta: number, kind: ValueKind): string {
  if (!Number.isFinite(delta)) return "-";
  switch (kind) {
    case "percent":
    case "percent_pp":
    case "rate_level":
    case "ratio":
      return fmtPP(delta, DELTA_CAP);
    case "basis_points":
      return fmtBPS(delta, DELTA_CAP);
    case "currency_cad":
      return fmtCurrencyCAD(delta, DELTA_CAP);
    case "fx":
      return fmtFX(delta, DELTA_CAP);
    case "index_level":
      return fmtIndex(delta, DELTA_CAP);
    case "count":
      return fmtCount(delta, DELTA_CAP);
    default:
      return fmtIndex(delta, DELTA_CAP);
  }
}

/**
 * Format a y-axis tick label. Cap: 6 chars.
 *
 * `isTop` is the canonical "topmost tick carries the unit" hook. When
 * `isTop` is true, the tick body carries the unit suffix glyph (e.g.
 * "2.5%", "$1.2B", "455k"). Non-top ticks drop the suffix when the
 * suffix is implicit (the topmost tick already established the scale),
 * EXCEPT for percent / pp / bps / fx where the glyph is so terse it
 * adds no clutter. Backend pipeline/io/format.py mirrors this.
 */
export function fmtTick(value: number, kind: ValueKind, isTop: boolean): string {
  if (!Number.isFinite(value)) return "-";
  switch (kind) {
    case "percent":
    case "rate_level":
    case "ratio":
      // Always carry "%" - the cheapest scale signal possible.
      return fmtPercent(value, TICK_CAP, { decimals: pickPercentDec(value) });
    case "percent_pp":
      // Mid-axis ticks don't need "pp" decoration; topmost carries it.
      if (isTop) return fmtPP(value, TICK_CAP);
      return trimLen((value >= 0 ? "" : "-") + Math.abs(value).toFixed(1), TICK_CAP);
    case "basis_points":
      if (isTop) return fmtBPS(value, TICK_CAP);
      return trimLen(`${Math.round(value)}`, TICK_CAP);
    case "currency_cad":
      // currency_cad always carries the "$" + scale suffix because
      // dropping it on mid-ticks would leave bare integers that read as
      // raw counts.
      return fmtCurrencyCAD(value, TICK_CAP);
    case "fx":
      return fmtFX(value, TICK_CAP);
    case "index_level":
      return fmtIndex(value, TICK_CAP);
    case "count":
      return fmtCount(value, TICK_CAP);
    default:
      return fmtIndex(value, TICK_CAP);
  }
}

function pickPercentDec(v: number): number {
  const a = Math.abs(v);
  if (a >= 100) return 0;
  if (a >= 10) return 1;
  return 1;
}

// --- inference table: unit-string -> ValueKind ----------------------------
//
// Used by PanelLiveChart until backend emits `kind` on each series.
//
//   "%"                         -> "percent"  (covers CPI Y/Y, unrate,
//                                  HPI Y/Y, vacancy rate, share-above-3,
//                                  rent y/y, GDP y/y, capacity util)
//   "% of firms"                -> "percent"
//   "pp"                        -> "percent_pp"
//   "bps" / "basis points"      -> "basis_points"
//   "CAD per USD"               -> "fx"
//   "CAD millions" /
//     "C$ millions" /
//     "CAD millions, SA" /
//     "C$ millions, chained"    -> "currency_cad"  (units treated as M$)
//   "CAD billions" /
//     "C$ billions"             -> "currency_cad"  (rescaled in formatter)
//   "C$ trillions, chained"     -> "currency_cad"  (rescaled)
//   "USD/barrel"                -> "index_level"   (price-of-thing; no $)
//   "CAD/hour" / "CAD/week"     -> "currency_cad"  (wages, per-period)
//   "CAD thousands"             -> "currency_cad"  (rescaled)
//   "Persons"                   -> "count"
//   "Millions of persons"       -> "count"         (rescaled in formatter)
//   "Thousands of hours"        -> "count"         (rescaled)
//   "Units, SAAR" /
//     "Units (thousands), SAAR" -> "count"
//   "Index" (any "Index..." variant) -> "index_level"
//   "Resales (12M rolling)"     -> "count"
//   anything else / null        -> "index_level"  (safe default)
//
// The unit strings carry implicit scale (e.g. "Millions of persons" means
// the value is already in millions). We respect that by keeping the
// value as-emitted and letting the scaler pick the right glyph. For
// "CAD billions" the value is already in B$; fmtCurrencyCAD will see
// e.g. 5.7 (B$) but the formatter is built for M$ input. So inference
// must rescale to the M$ baseline so fmtCurrencyCAD prints "$5.7B"
// rather than "$5.7M". This is documented per-branch in
// `unitScaleFactor` below.
export function inferKindFromUnit(unit: string | null | undefined): ValueKind {
  if (!unit) return "index_level";
  const u = unit.toLowerCase();
  if (u === "%" || u.startsWith("%") || u.includes(" %") || u.includes("% of")) return "percent";
  if (u === "pp" || u.includes(" pp")) return "percent_pp";
  if (u.includes("bps") || u.includes("basis point")) return "basis_points";
  if (u.includes("cad per usd")) return "fx";
  if (u.includes("usd/barrel")) return "index_level";
  // CAD/hour and CAD/week are wage rates (price-of-labour, not an
  // aggregate). They read as plain dollar amounts (~$30, $40) without
  // the "M" / "B" scale suffix - so route through index_level rather
  // than currency_cad. Backend pipeline/io/format.py mirrors this.
  if (u.includes("cad/hour") || u.includes("cad/week")) return "index_level";
  if (u.includes("cad ") || u.includes("c$") || u.includes("cad thousand") || u.includes("cad million") || u.includes("cad billion")) return "currency_cad";
  if (u.includes("persons") || u.includes("of hours") || u.includes("units") || u.includes("resales") || u.includes("beneficiaries")) return "count";
  if (u.includes("index")) return "index_level";
  return "index_level";
}

/**
 * Some `unit` strings include a magnitude prefix ("Millions of persons",
 * "CAD billions", "C$ trillions"). Values in the panel JSON are already
 * scaled to that prefix; the formatter expects a baseline unit (counts
 * in raw items, currency_cad in M$). This returns the multiplier the
 * caller should apply to the raw JSON value to bring it to the baseline.
 *
 * Examples:
 *   "Persons"               -> 1           (already raw items)
 *   "Millions of persons"   -> 1_000_000   (value 1.5 -> 1,500,000)
 *   "Thousands of hours"    -> 1_000       (value 558k -> 558,000)
 *   "CAD millions"          -> 1           (baseline)
 *   "CAD billions"          -> 1_000       (value 5.7 -> 5,700 M$)
 *   "C$ trillions, ..."     -> 1_000_000   (value 1.65 -> 1.65M M$)
 *   "CAD thousands"         -> 0.001       (value 712 -> 0.712 M$)
 *   "Units (thousands), SAAR" -> 1_000     (value 240 -> 240,000 units)
 *   anything else           -> 1
 */
export function unitScaleFactor(unit: string | null | undefined): number {
  if (!unit) return 1;
  const u = unit.toLowerCase();
  if (u.includes("millions of") || u.includes("c$ millions") || u.includes("cad millions")) {
    // already in baseline for currency (M$) OR rescale needed for counts
    if (u.includes("persons") || u.includes("of hours")) return 1_000_000;
    return 1;
  }
  if (u.includes("billions") || u.includes("billion")) {
    // currency_cad baseline is M$, so multiply by 1000
    return 1_000;
  }
  if (u.includes("trillions") || u.includes("trillion")) {
    return 1_000_000;
  }
  if (u.includes("thousands of") || u.includes("(thousands)") || u.includes(", saar)")) {
    return 1_000;
  }
  if (u.includes("cad thousand")) {
    return 0.001;
  }
  return 1;
}
