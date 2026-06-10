/**
 * src/lib/prose -- deterministic build-time prose rendering.
 *
 * Reader-facing markets text is a function of the data: templates authored
 * by the writer (through the three review gates) are bound to panel_data
 * series and re-rendered on every build. No LLM in the daily loop; a
 * sentence whose predicates no longer match the data drops silently; a
 * required surface or callout that renders empty fails the build.
 *
 * Astro usage (frontmatter, build time):
 *
 *   import { renderSectionProse } from "../lib/prose";
 *   const prose = renderSectionProse("markets");
 *   const title = prose.surfaces["plate-energy-title"].text;
 *
 * Debugging / review gates: `node scripts/render_prose.mjs markets` dumps
 * every surface with the variant index + predicate that selected it.
 *
 * Implementation lives in engine.mjs / loader.mjs (plain ESM shared with
 * bare-node scripts); this module is the typed entry point.
 */

export {
  parseTemplate,
  renderTemplate,
  collectSeries,
  dropSuspectFinalObs,
  ProseTemplateError,
  ProseRenderError,
  FORMATS,
} from "./engine.mjs";

export type {
  ProseRenderResult,
  RenderedSurface,
  RenderedPart,
  SeriesObservations,
  CompiledTemplate,
  ProseFormat,
} from "./engine.mjs";

export { renderSectionProse } from "./loader.mjs";

export type { RenderSectionOptions, SectionProseResult } from "./loader.mjs";
