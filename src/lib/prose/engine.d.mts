/**
 * Type declarations for engine.mjs (the deterministic prose renderer).
 * Keep in sync with the implementation; engine.mjs is the source of truth.
 */

export class ProseTemplateError extends Error {}
export class ProseRenderError extends Error {}

/** One named output format for {expr|fmt} interpolation. */
export interface ProseFormat {
  kind: "num" | "date";
  render: (value: never) => string;
}

export declare const FORMATS: Record<string, ProseFormat>;

/** A compiled template variant (internal shape; opaque to consumers). */
export interface CompiledTemplate {
  section: string;
  slots: Record<string, string>;
  surfaces: Record<string, unknown>;
}

export interface RenderedPart {
  /** null for single-string (variants) surfaces */
  sentenceIndex: number | null;
  variantIndex: number;
  /** the `when:` predicate source that selected this variant */
  predicate: string;
  text: string;
}

export interface RenderedSurface {
  id: string;
  required: boolean;
  /** final rendered text; "" when every sentence dropped (non-required only) */
  text: string;
  parts: RenderedPart[];
}

export interface ProseRenderResult {
  section: string;
  /** panel_data generatedAt the render was bound to */
  generatedAt: string | null;
  surfaces: Record<string, RenderedSurface>;
  /** non-fatal notes, e.g. predicates skipped on insufficient history */
  warnings: string[];
}

export interface SeriesObservations {
  dates: string[];
  values: number[];
}

export declare function parseTemplate(
  raw: unknown,
  availableSeriesKeys: Iterable<string>
): CompiledTemplate;

export declare function renderTemplate(
  template: CompiledTemplate,
  panelData: unknown
): ProseRenderResult;

export declare function collectSeries(panelData: unknown): Map<string, SeriesObservations>;

export declare function dropSuspectFinalObs(
  series: SeriesObservations,
  generatedAtISO: string | null
): SeriesObservations;
