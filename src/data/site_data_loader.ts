/*
 * site_data_loader - Build-time bridge between the pipeline output
 * (data/site/sections.json) and the homepage components.
 *
 * Reads the backend payload off disk at Astro build time and merges it with
 * the editorial canon in src/data/sections.ts. Components consume the
 * `enrichedSections` export below; the merged record carries the per-print
 * fields the pipeline produced AND an `isReal` flag so consumers can render
 * an obvious placeholder when a field is not yet wired.
 *
 * Reading strategy
 * ----------------
 * Astro/Vite resolves a static `import payload from "...json"` at build
 * time, which keeps this loader fully synchronous, lets TypeScript type the
 * JSON shape, and avoids pulling @types/node into the project. The JSON
 * file lives at the project root under data/site/sections.json - outside
 * src/ but still inside the Vite-served workspace, so the relative import
 * is stable.
 *
 * Failure policy
 * --------------
 * If the JSON payload is missing or empty for a given slug, that section
 * renders as an all-placeholder shell (every field marked not-wired). The
 * build still succeeds.
 */

// Vite handles the JSON import. tsconfig (astro/strict) sets
// `resolveJsonModule: true`, so the import is fully typed.
import payloadJson from "../../data/site/sections.json";

import { renderSectionProse } from "../lib/prose";
import {
  sections as canonSections,
  type Section,
  type SectionSlug,
} from "./sections";

// ---------------------------------------------------------------------------
// Shape of the JSON payload (mirrors pipeline/io/site_data.py)
// ---------------------------------------------------------------------------

interface RawPrint {
  key?: string;
  indicator?: string;
  value?: string;
  delta?: string;
  deltaDir?: "pos" | "neg" | "neutral";
  asOf?: string;
  spark?: number[];
  valueRaw?: number;
  priorRaw?: number;
  asOfISO?: string;
}

interface RawReference {
  value: number;
  label: string;
}

interface RawSection {
  slug: string;
  chartSeriesKey?: string;
  prints?: RawPrint[];
  reference?: RawReference | null;
  updatedAt?: number | null;
  error?: string;
  primarySeries?: string;
  source?: string | null;
  sourceUrl?: string | null;
  sourceId?: string | null;
  units?: string | null;
  frequency?: string | null;
  releaseDate?: string | null;
}

interface RawPayload {
  schemaVersion?: number;
  generatedAt?: string;
  sections?: Record<string, RawSection>;
}

// ---------------------------------------------------------------------------
// Enriched section type the homepage consumes
// ---------------------------------------------------------------------------

/**
 * A single print, with explicit per-field "is this real or a placeholder"
 * markers. Components render the placeholder strings themselves so the
 * visual treatment stays in one place (CSS).
 */
export interface EnrichedPrint {
  key?: string;
  indicator: string;
  /** Real headline value (e.g. "2.3%") OR null when not wired. */
  value: string | null;
  /** Real delta (e.g. "+0.5 pp") OR null when not wired. */
  delta: string | null;
  /** Real direction OR null when not wired. */
  deltaDir: "pos" | "neg" | "neutral" | null;
  /** Real asOf stamp (e.g. "Mar 2026") OR null when not wired. */
  asOf: string | null;
  /** Real ISO date (e.g. "2026-03-01") OR null. */
  asOfISO: string | null;
  /** Real series points (~24 numbers) OR null when not wired. */
  spark: number[] | null;
  /** True iff every value/delta/asOf/spark slot on this print came from pipeline. */
  isReal: boolean;
}

export interface EnrichedReference {
  value: number;
  label: string;
}

/**
 * Section payload after merging editorial canon (label, accentVar,
 * headlineQuestion, cadence) with pipeline data (prints, reference,
 * releaseDate). `isReal` flags out per-field where placeholders must show.
 */
export interface EnrichedSection {
  // ---- editorial canon (always real, hand-typed) ----
  slug: SectionSlug;
  label: string;
  tileLabel?: string;
  accentVar: string;
  kicker?: string;
  headlineQuestion: string;
  cadence: string;
  /** Original canon section for any consumer that needs unmerged access. */
  canon: Section;

  // ---- pipeline-derived ----
  /** Primary print for the panel chart + readout. Always present
   * (placeholder shape when the pipeline produced no real data). */
  loadBearing: EnrichedPrint;
  /** All prints on this section. Empty array means the pipeline produced
   * none, in which case `loadBearing` is the placeholder shape. */
  prints: EnrichedPrint[];
  /** Reference rule (CPI 2%, Policy 2.75%). Null = not wired or N/A. */
  reference: EnrichedReference | null;
  /** Pipeline `updatedAt` epoch ms. Null when not wired. */
  updatedAt: number | null;
  /** Pipeline `releaseDate` (ISO date) if available. */
  releaseDate: string | null;
  /** Convenience: true iff this section has at least one real print. */
  hasRealData: boolean;
  /** The error string when the pipeline could not build this section. */
  pipelineError: string | null;
  chartSeriesKey?: string;
  /** Build-time prose rendered from editorial/prose_templates/<slug>.yaml. */
  tileLine: string | null;
  /** Series unit as the pipeline names it (e.g. "%", "CAD per USD",
   *  "CAD millions"). Used to render the unit on the topmost y-tick. */
  units: string | null;
  /** Series frequency (e.g. "monthly", "daily", "quarterly"). Drives the
   *  delta-period stamp ("m/m" / "d/d" / "q/q") and the earliest-date
   *  label computation. */
  frequency: string | null;
}

// ---------------------------------------------------------------------------
// Payload
// ---------------------------------------------------------------------------

// The static import resolves at build time; Vite cache-busts on JSON
// changes during dev. Cast through `unknown` because the JSON's literal
// inferred type is narrower than our RawPayload runtime shape (the
// pipeline may produce a section with or without `error`, etc.).
const payload: RawPayload = payloadJson as unknown as RawPayload;

// ---------------------------------------------------------------------------
// Print enrichment
// ---------------------------------------------------------------------------

function emptyPlaceholderPrint(
  cfg: { key?: string; indicator: string },
): EnrichedPrint {
  return {
    key: cfg.key,
    indicator: cfg.indicator,
    value: null,
    delta: null,
    deltaDir: null,
    asOf: null,
    asOfISO: null,
    spark: null,
    isReal: false,
  };
}

function enrichPrint(raw: RawPrint): EnrichedPrint {
  // A real print from the pipeline must carry, at minimum, a numeric value
  // and a spark array of length >= 2. Fall back per-field.
  //
  // The pipeline emits the literal string "TK" (PLACEHOLDER.value) for
  // not-yet-wired rows. Treat those strings as null here so the downstream
  // `value === null -> render PLACEHOLDER.value in gray` path engages
  // automatically. Without this coercion, a string of length > 0 was
  // passing through as a real value and rendering "TK" in pure-ink Plex
  // Mono, indistinguishable from a real "2.3%" reading.
  const isLiteralTk = (v: unknown): boolean =>
    typeof v === "string" && v.trim() === "TK";
  const hasValue =
    typeof raw.value === "string"
    && raw.value.length > 0
    && !isLiteralTk(raw.value);
  const hasDelta =
    typeof raw.delta === "string"
    && raw.delta.length > 0
    && !isLiteralTk(raw.delta);
  const hasAsOf =
    typeof raw.asOf === "string"
    && raw.asOf.length > 0
    && !isLiteralTk(raw.asOf);
  const hasAsOfISO =
    typeof raw.asOfISO === "string"
    && raw.asOfISO.length > 0
    && !isLiteralTk(raw.asOfISO);
  const hasSpark =
    Array.isArray(raw.spark) && raw.spark.filter((v) => Number.isFinite(v)).length >= 2;
  const isReal = hasValue && hasSpark;
  return {
    key: raw.key,
    indicator: raw.indicator ?? "",
    value: hasValue ? (raw.value as string) : null,
    delta: hasDelta ? (raw.delta as string) : null,
    deltaDir: raw.deltaDir ?? null,
    asOf: hasAsOf ? (raw.asOf as string) : null,
    asOfISO: hasAsOfISO ? (raw.asOfISO as string) : null,
    spark: hasSpark ? (raw.spark as number[]) : null,
    isReal,
  };
}

// ---------------------------------------------------------------------------
// Section enrichment
// ---------------------------------------------------------------------------

function enrichSection(canon: Section): EnrichedSection {
  const raw = payload.sections?.[canon.slug];
  const rawPrints = raw?.prints ?? [];
  const renderedTileLine = renderSectionProse(canon.slug).surfaces.tileline?.text ?? null;

  // Resolve the primary print indicator label. Pipeline carries
  // `print_indicator` per series; if no real prints, fall back to canon's
  // first print indicator so the placeholder readout still has a key
  // ("Headline CPI, y/y" etc.) — we are placeholdering values, not labels.
  const canonLeadKey = canon.chartSeriesKey;
  const canonLead =
    canon.prints.find((p) => p.key === canonLeadKey) ?? canon.prints[0];

  // Index the pipeline-produced prints by stable key so we can splice them
  // into the canon row scaffold. If the pipeline emits a print without a
  // key, fall back to indicator-string matching so a legacy payload still
  // lands the right row. Anything the pipeline emits that does NOT match a
  // canon row is appended at the end (so it still appears in the table).
  const rawByKey = new Map<string, RawPrint>();
  const rawByIndicator = new Map<string, RawPrint>();
  for (const r of rawPrints) {
    if (r.key) rawByKey.set(r.key, r);
    if (r.indicator) rawByIndicator.set(r.indicator, r);
  }

  // Build the indicator-row scaffold from canon. Every canon print becomes
  // either (a) the enriched pipeline print if the keys match, or (b) a
  // placeholder row carrying just the indicator label so the table still
  // shows the structure. This is the central change in this pass:
  // canon owns the row list, pipeline data fills it in.
  const matched = new Set<RawPrint>();
  const prints: EnrichedPrint[] = canon.prints.map((cp) => {
    let r: RawPrint | undefined;
    if (cp.key && rawByKey.has(cp.key)) {
      r = rawByKey.get(cp.key);
    } else if (rawByIndicator.has(cp.indicator)) {
      r = rawByIndicator.get(cp.indicator);
    }
    if (r) {
      matched.add(r);
      return enrichPrint({
        // Carry the canon key + indicator string through so the row keeps
        // its scaffold identity even if the pipeline omitted one of them.
        key: cp.key ?? r.key,
        indicator: cp.indicator,
        ...r,
      });
    }
    return emptyPlaceholderPrint({ key: cp.key, indicator: cp.indicator });
  });

  // Surface any pipeline prints that didn't match the canon scaffold so a
  // backend addition doesn't silently vanish from the table.
  for (const r of rawPrints) {
    if (!matched.has(r)) {
      prints.push(enrichPrint(r));
    }
  }

  // Resolve the primary print for the chart + readout. Prefer a real,
  // chart-series-keyed print; fall back to the first real print; finally to
  // the canon-scaffolded first row (which will read as a TK placeholder).
  const realPrints = prints.filter((p) => p.isReal);
  let loadBearing: EnrichedPrint =
    prints.find((p) => p.key === canon.chartSeriesKey && p.isReal) ??
    realPrints[0] ??
    prints.find((p) => p.key === canon.chartSeriesKey) ??
    prints[0] ??
    emptyPlaceholderPrint({
      key: canon.chartSeriesKey,
      indicator: canonLead?.indicator ?? canon.label,
    });

  return {
    slug: canon.slug,
    label: canon.label,
    tileLabel: canon.tileLabel,
    accentVar: canon.accentVar,
    kicker: canon.kicker,
    headlineQuestion: canon.headlineQuestion,
    cadence: canon.cadence,
    canon,
    loadBearing,
    prints,
    reference: raw?.reference ?? null,
    updatedAt: raw?.updatedAt ?? null,
    releaseDate: raw?.releaseDate ?? null,
    hasRealData: prints.some((p) => p.isReal),
    pipelineError: raw?.error ?? null,
    chartSeriesKey: canon.chartSeriesKey,
    tileLine: renderedTileLine,
    units: raw?.units ?? null,
    frequency: raw?.frequency ?? null,
  };
}

// ---------------------------------------------------------------------------
// Public exports
// ---------------------------------------------------------------------------

export const enrichedSections: EnrichedSection[] = canonSections.map(enrichSection);

export const enrichedBySlug: Record<SectionSlug, EnrichedSection> =
  Object.fromEntries(
    enrichedSections.map((s) => [s.slug, s] as const),
  ) as Record<SectionSlug, EnrichedSection>;

/**
 * Pick the section whose real `updatedAt` is most recent. If no section has
 * real data (unlikely in production; possible in dev), fall back to
 * inflation, then to the first section.
 */
export function pickHeroSection(): EnrichedSection {
  const withReal = enrichedSections.filter((s) => s.hasRealData && s.updatedAt !== null);
  if (withReal.length === 0) {
    return (
      enrichedBySlug["inflation"] ?? enrichedSections[0]!
    );
  }
  return withReal.reduce((a, b) => (b.updatedAt! > a.updatedAt! ? b : a));
}

/**
 * Build-time payload meta — exposed so the colophon / build stamp can show
 * when the JSON was generated.
 */
export const payloadMeta = {
  generatedAt: payload.generatedAt ?? null,
  schemaVersion: payload.schemaVersion ?? null,
} as const;

// ---------------------------------------------------------------------------
// Shared placeholder strings — keep markers in one place so audits + tests
// can find them by import.
// ---------------------------------------------------------------------------

export const PLACEHOLDER = {
  /**
   * Journalism convention: TK = "to come". Anywhere a numeric value, delta,
   * or stamp is not yet produced by the pipeline, render this in the cell.
   * Tighter than em-dashes and reads as editorial workflow rather than
   * empty data. Visible softening (mid-gray) comes from the consuming
   * component's placeholder class.
   */
  value: "TK",
  /** As-of / date marker for cells where the pipeline hasn't produced one. */
  notWired: "TK",
  /** Footer "next release" stamp (wider micro-caps slot). */
  nextReleaseNotWired: "TK",
  /** Deep-dive status — pipeline-pending. */
  statusPending: "TK",
  /** Direction glyph when delta is not wired. Render as blank so the cell
   * reads as "TK" without a leading dash competing with it. */
  directionNone: "",
  /** Chart-slot caption when a section has no real series. Kept distinct
   * from cell-level TK because the empty chart slot also carries a
   * dashed-border treatment + diagonal hatch; the long caption is the
   * primary tell at the chart scale. */
  chartEmpty: "DATA NOT YET WIRED",
  /** Visible lorem ipsum prose so editorial blanks are unmistakable. */
  loremShort:
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod " +
    "tempor incididunt ut labore et dolore magna aliqua.",
  loremMid:
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod " +
    "tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim " +
    "veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex " +
    "ea commodo consequat.",
  loremLong:
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod " +
    "tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim " +
    "veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex " +
    "ea commodo consequat. Duis aute irure dolor in reprehenderit in " +
    "voluptate velit esse cillum dolore eu fugiat nulla pariatur.",
} as const;
