/**
 * Type declarations for loader.mjs. Keep in sync with the implementation.
 */

import type { ProseRenderResult } from "./engine.mjs";

export interface RenderSectionOptions {
  /** project root; defaults to process.cwd() (Astro builds run from root) */
  root?: string;
  /** override editorial/prose_templates/<section>.yaml */
  templatePath?: string;
  /** override data/site/panel_data/<section>.json */
  panelDataPath?: string;
}

export interface SectionProseResult extends ProseRenderResult {
  templatePath: string;
  panelDataPath: string;
}

export declare function renderSectionProse(
  section: string,
  options?: RenderSectionOptions
): SectionProseResult;
