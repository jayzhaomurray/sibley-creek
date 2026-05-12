/*
 * derivedLabels.ts - shared helpers that turn the pipeline's panel_data /
 * sections.json payloads into the date-stamped strings that page-level
 * "Latest release", plate `asOf`, and plate `callout` slots consume.
 *
 * Rationale
 * ---------
 * Before this module, every section page hand-set strings like
 *   asOf: "Mar 2026"
 *   asOf: "May 8, 2026"
 *   asOf: "Mar 2026 (starts) / Feb 2026 (permits)"
 *   latestReleaseLabel: "Headline CPI, Mar 2026"
 *
 * which drifted as the pipeline refreshed. The pipeline already emits
 * `asOfISO` + `frequency` per series in `data/site/panel_data/<section>.json`
 * and per print in `data/site/sections.json`. This helper formats those
 * fields the same way the page authors did by hand - so every refresh of
 * the JSON moves the visible string automatically.
 *
 * Editorial overrides
 * -------------------
 * Some plates carry editorial context inside their date stamp (e.g.
 * `"April 29, 2026 (rate decision)"`, `"Pending wiring"`, `"Current as of
 * May 11, 2026"`). For those, the page omits the auto-derivation and
 * passes the hand-set string straight through. The plate type makes
 * `asOf` optional precisely to support this opt-out.
 *
 * Editorial-coupled fields LEFT untouched (per backend-engineer scope):
 *   - `callout.delta` (release-day narrative)
 *   - `callout.direction` (editorial sign)
 *   - `interpretation` / `title` / `source` / `indicator` (editorial)
 */

import type { PanelData, PanelSeries } from "../../charts/_shared/panelData";

// ---------------------------------------------------------------------------
// ISO -> display formatting (frequency-aware)
// ---------------------------------------------------------------------------

const MONTHS_SHORT = [
  "Jan", "Feb", "Mar", "Apr", "May", "Jun",
  "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
];

const MONTHS_LONG = [
  "January", "February", "March", "April", "May", "June",
  "July", "August", "September", "October", "November", "December",
];

interface IsoParts {
  year: number;
  month: number; // 1-12
  day: number;   // 1-31 (defaults to 1 when input has no day component)
  hasDay: boolean;
}

function parseISO(iso: string): IsoParts | null {
  // Match YYYY-MM-DD or YYYY-MM (forgiving).
  const m = iso.match(/^(\d{4})-(\d{2})(?:-(\d{2}))?/);
  if (!m) return null;
  const year = parseInt(m[1]!, 10);
  const month = parseInt(m[2]!, 10);
  const dayStr = m[3];
  return {
    year,
    month,
    day: dayStr ? parseInt(dayStr, 10) : 1,
    hasDay: Boolean(dayStr),
  };
}

/**
 * Convert an ISO date + cadence into the same display stamp the section
 * pages used to hand-set:
 *   - daily / weekly       -> "May 8, 2026"
 *   - monthly              -> "Mar 2026"
 *   - quarterly            -> "Q4 2025"
 * Unknown / null cadence defaults to monthly grain, which matches the
 * commonest path through the pipeline.
 */
export function formatAsOf(
  asOfISO: string | null | undefined,
  frequency: string | null | undefined,
): string | null {
  if (!asOfISO) return null;
  const parts = parseISO(asOfISO);
  if (!parts) return null;
  const f = (frequency ?? "").toLowerCase();
  if (f === "daily" || f === "weekly") {
    // Weekly cadences land on a specific Wednesday / Friday / etc. - the
    // pipeline emits the specific date so we render the day.
    const monthName = MONTHS_LONG[parts.month - 1] ?? "";
    return `${monthName} ${parts.day}, ${parts.year}`;
  }
  if (f === "quarterly") {
    const q = Math.ceil(parts.month / 3);
    return `Q${q} ${parts.year}`;
  }
  // Monthly (default).
  const monShort = MONTHS_SHORT[parts.month - 1] ?? "";
  return `${monShort} ${parts.year}`;
}

/**
 * Format an ISO date as a short "Mar 2026" / "Q4 2025" / "May 8, 2026"
 * stamp matching the splash-tile asOf convention. Identical to
 * formatAsOf, exposed under a callout-specific name so the call sites
 * read clearly.
 */
export function formatCalloutDate(
  asOfISO: string | null | undefined,
  frequency: string | null | undefined,
): string | null {
  return formatAsOf(asOfISO, frequency);
}

// ---------------------------------------------------------------------------
// Plate-level: derive asOf from the panel's primary/secondary/tertiary
// ---------------------------------------------------------------------------

interface SeriesPick {
  series: PanelSeries;
  asOfISO: string;
  frequency: string;
  groupKey: string; // cadence + asOfISO bucket, for "are these all the same?"
}

function pickSeriesEntries(data: PanelData | null | undefined): SeriesPick[] {
  if (!data) return [];
  const out: SeriesPick[] = [];
  const candidates: Array<PanelSeries | null | undefined> = [
    data.primary,
    data.secondary,
    data.tertiary ?? null,
  ];
  for (const s of candidates) {
    if (!s) continue;
    const iso = s.asOfISO;
    if (!iso) continue;
    const freq = (s.frequency ?? "").toLowerCase();
    out.push({
      series: s,
      asOfISO: iso,
      frequency: freq,
      groupKey: `${freq}::${iso}`,
    });
  }
  return out;
}

function compareISO(a: string, b: string): number {
  // ISO dates sort lexicographically. Pad day if missing.
  const pa = parseISO(a);
  const pb = parseISO(b);
  if (!pa && !pb) return 0;
  if (!pa) return -1;
  if (!pb) return 1;
  if (pa.year !== pb.year) return pa.year - pb.year;
  if (pa.month !== pb.month) return pa.month - pb.month;
  return pa.day - pb.day;
}

/**
 * Group series by display cadence so daily + weekly collapse to "daily-style"
 * (we already render both as "May 8, 2026") and monthly stays its own bucket.
 * Quarterly is its own bucket.
 */
function cadenceBucket(frequency: string): "daily" | "monthly" | "quarterly" | "other" {
  if (frequency === "daily" || frequency === "weekly") return "daily";
  if (frequency === "monthly") return "monthly";
  if (frequency === "quarterly") return "quarterly";
  return "other";
}

/**
 * Derive a plate-level "as of" string from a `PanelData` payload.
 *
 * Rules:
 *   1. If the panel has no usable series (no asOfISO anywhere), returns null
 *      so the caller can fall back to its hand-set string or a placeholder.
 *   2. If every series lives in the same cadence bucket, return the latest
 *      observation date formatted per that cadence ("Mar 2026", "May 8,
 *      2026", "Q4 2025").
 *   3. If series straddle cadence buckets (e.g. monthly starts + quarterly
 *      UCC; daily WTI + monthly WCS), name each cadence with its series
 *      label: `"<latest> (<labelA>) / <latest> (<labelB>)"`. Labels are
 *      lightly cleaned to drop noisy suffixes the pipeline carries (e.g.
 *      `"Housing starts SAAR"` -> `"starts"`).
 *
 * Returns null when no derivation is possible.
 */
export function derivePlateAsOf(
  data: PanelData | null | undefined,
): string | null {
  const picks = pickSeriesEntries(data);
  if (picks.length === 0) return null;

  // Group by display cadence bucket.
  const groups = new Map<string, SeriesPick[]>();
  for (const p of picks) {
    const bucket = cadenceBucket(p.frequency);
    const arr = groups.get(bucket) ?? [];
    arr.push(p);
    groups.set(bucket, arr);
  }

  // Single-cadence: pick the latest across all picks.
  if (groups.size <= 1) {
    const latest = picks.reduce((best, p) =>
      compareISO(p.asOfISO, best.asOfISO) > 0 ? p : best,
    );
    return formatAsOf(latest.asOfISO, latest.frequency);
  }

  // Multi-cadence: emit "<date> (<labelA>) / <date> (<labelB>) / ...".
  // Preserve the order of buckets as picks first appeared so the highest-
  // priority series (primary) is named first.
  const seen = new Set<string>();
  const orderedBuckets: string[] = [];
  for (const p of picks) {
    const b = cadenceBucket(p.frequency);
    if (!seen.has(b)) {
      seen.add(b);
      orderedBuckets.push(b);
    }
  }
  const parts: string[] = [];
  for (const bucket of orderedBuckets) {
    const arr = groups.get(bucket)!;
    const latest = arr.reduce((best, p) =>
      compareISO(p.asOfISO, best.asOfISO) > 0 ? p : best,
    );
    const dateStr = formatAsOf(latest.asOfISO, latest.frequency);
    if (!dateStr) continue;
    const tag = compactSeriesLabel(latest.series.label ?? "");
    parts.push(tag ? `${dateStr} (${tag})` : dateStr);
  }
  if (parts.length === 0) return null;
  return parts.join(" / ");
}

/**
 * Squash a pipeline series label down to a single-word tag suitable for
 * inline parenthetical use. The pipeline labels are full-text ("Housing
 * starts SAAR", "Residential permits", "WTI spot"); inside an asOf stamp
 * we want the shortest distinctive token.
 *
 * Heuristic: keep the first noun-ish token, drop common modifiers (SAAR,
 * spot, Y/Y, index, monthly). Returns "" when the input is empty.
 */
function compactSeriesLabel(label: string): string {
  if (!label) return "";
  // Drop modifiers: cadence words ("monthly", "quarterly"), units ("rate",
  // "ratio", "%"), and generic head-nouns that don't disambiguate ("housing",
  // "real", "total", "national"). The remaining first token tends to be the
  // distinguishing noun ("starts", "permits", "WCS", "immigrant", "rent").
  const dropTokens = new Set([
    "saar", "spot", "y/y", "yoy", "q/q", "qoq", "m/m", "mom",
    "index", "monthly", "quarterly", "daily", "weekly", "rate",
    "ratio", "annualized", "annual", "the", "real", "nominal",
    "national", "canada", "canadian", "total", "headline", "housing",
    "level", "share", "growth",
  ]);
  const cleaned = label
    .replace(/[(),.]/g, " ")
    .split(/\s+/)
    .filter(Boolean)
    .filter((tok) => !dropTokens.has(tok.toLowerCase()));
  if (cleaned.length === 0) return label.trim();
  // Keep the first meaningful word, lowercase it for editorial fit
  // ("starts", "permits", "WCS"). Preserve all-caps acronyms (>= 3 caps).
  const first = cleaned[0]!;
  if (/^[A-Z]{2,}$/.test(first)) return first;
  return first.toLowerCase();
}

// ---------------------------------------------------------------------------
// Page-level: derive `latestReleaseLabel` from sections.json
// ---------------------------------------------------------------------------

interface SectionsJsonPrint {
  key?: string;
  asOf?: string;
  asOfISO?: string;
}

interface SectionsJsonSection {
  slug: string;
  chartSeriesKey?: string;
  prints?: SectionsJsonPrint[];
  releaseDate?: string | null;
  frequency?: string | null;
}

interface SectionsJsonPayload {
  sections?: Record<string, SectionsJsonSection>;
}

/**
 * Compose the page-level "Latest release" stamp from a static editorial
 * prefix + the auto-derived date of the section's load-bearing print.
 *
 * - `prefix`     - editorial, e.g. "Headline CPI", "LFS", "Daily close".
 * - `payload`    - the imported sections.json file (RawPayload-equivalent).
 * - `slug`       - section slug to look up.
 * - `printKey`   - which print to pull the date from. Defaults to the
 *                  section's `chartSeriesKey`; fallback to `prints[0]`.
 *
 * Returns null when no usable date is available so the caller can flow the
 * placeholder treatment in SectionPageHeader (gray "[ NOT WIRED ]" stamp).
 *
 * The pipeline already pre-formats `asOf` per print ("Mar 2026", "Feb 2026",
 * "2025Q4"), so we use that string directly when present. If only the ISO
 * is available, we fall back to formatAsOf() with the section frequency.
 */
export function deriveLatestReleaseLabel(
  prefix: string,
  payload: unknown,
  slug: string,
  printKey?: string,
): string | null {
  if (!prefix) return null;
  const pj = (payload ?? {}) as SectionsJsonPayload;
  const sec = pj.sections?.[slug];
  if (!sec) return null;
  const prints = sec.prints ?? [];
  if (prints.length === 0) return null;
  const targetKey = printKey ?? sec.chartSeriesKey;
  let p: SectionsJsonPrint | undefined;
  if (targetKey) {
    p = prints.find((x) => x.key === targetKey);
  }
  if (!p) p = prints[0];
  if (!p) return null;
  // Prefer the pre-formatted `asOf` the pipeline already emitted; fall
  // back to ISO + frequency formatting.
  const dateStr = p.asOf
    ?? formatAsOf(p.asOfISO ?? null, sec.frequency ?? null)
    ?? null;
  if (!dateStr) return null;
  return `${prefix}, ${dateStr}`;
}

/**
 * Compose a hero kicker string from a static prefix + the auto-derived
 * load-bearing print date. Same date-formatting logic as
 * deriveLatestReleaseLabel but renders as "Mar 2026 CPI" style (date first,
 * prefix after) since the eyebrow rail reads as "{SECTION} | {KICKER}".
 *
 * Actually we keep the original "{Prefix} {date}" pattern to match what was
 * hand-set ("March CPI", "Weekly close"). Caller can also pass a date-only
 * `prefix` if the date IS the kicker (e.g. "Weekly close" is the static
 * label even when daily closes drive the prefix).
 *
 * Returns null when payload has no usable date and lets the caller fall
 * back to the legacy static `section.heroKicker` field.
 */
export function deriveHeroKicker(
  prefix: string,
  payload: unknown,
  slug: string,
  printKey?: string,
): string | null {
  if (!prefix) return null;
  const pj = (payload ?? {}) as SectionsJsonPayload;
  const sec = pj.sections?.[slug];
  if (!sec) return null;
  const prints = sec.prints ?? [];
  if (prints.length === 0) return null;
  const targetKey = printKey ?? sec.chartSeriesKey;
  let p: SectionsJsonPrint | undefined;
  if (targetKey) {
    p = prints.find((x) => x.key === targetKey);
  }
  if (!p) p = prints[0];
  if (!p) return null;
  // Reuse the pipeline's pre-formatted `asOf` when present. The kicker
  // pattern is "{prefix} {date}" — prefix first then date.
  const dateStr = p.asOf
    ?? formatAsOf(p.asOfISO ?? null, sec.frequency ?? null)
    ?? null;
  if (!dateStr) return null;
  return `${prefix} ${dateStr}`;
}
