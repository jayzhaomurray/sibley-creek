/**
 * loader.mjs -- file-system entry point for the prose renderer.
 *
 * Separated from engine.mjs so the engine stays pure (no fs, no yaml dep)
 * and unit-testable against in-memory fixtures. This module is the one the
 * consumers actually call:
 *
 *   Astro frontmatter:  import { renderSectionProse } from "../lib/prose";
 *                       const prose = renderSectionProse("markets");
 *                       ...
 *                       <h2>{prose.surfaces["plate-energy-title"].text}</h2>
 *
 *   Node scripts:       import { renderSectionProse } from "../src/lib/prose/loader.mjs";
 *
 * Conventions:
 *   template:   editorial/prose_templates/<section>.yaml
 *   panel data: data/site/panel_data/<section>.json
 *   root:       process.cwd() (the Astro build runs from the project root;
 *               scripts pass an explicit root derived from their own path)
 */

import { readFileSync } from "node:fs";
import { join } from "node:path";
import { parse as parseYaml } from "yaml";

import {
  parseTemplate,
  renderTemplate,
  collectSeries,
  ProseTemplateError,
} from "./engine.mjs";

/**
 * Load template + panel data for a section and render every surface.
 *
 * @param {string} section  e.g. "markets"
 * @param {object} [options]
 * @param {string} [options.root]           project root (default process.cwd())
 * @param {string} [options.templatePath]   override template path
 * @param {string} [options.panelDataPath]  override panel data path
 * @returns render result: { section, generatedAt, surfaces, warnings, templatePath, panelDataPath }
 * @throws ProseTemplateError / ProseRenderError with actionable messages
 */
export function renderSectionProse(section, options = {}) {
  const root = options.root ?? process.cwd();
  const templatePath =
    options.templatePath ?? join(root, "editorial", "prose_templates", `${section}.yaml`);
  const panelDataPath =
    options.panelDataPath ?? join(root, "data", "site", "panel_data", `${section}.json`);

  let templateText;
  try {
    templateText = readFileSync(templatePath, "utf-8");
  } catch (e) {
    throw new ProseTemplateError(`could not read template ${templatePath}: ${e.message}`);
  }
  let panelData;
  try {
    panelData = JSON.parse(readFileSync(panelDataPath, "utf-8"));
  } catch (e) {
    throw new ProseTemplateError(`could not read panel data ${panelDataPath}: ${e.message}`);
  }

  let rawTemplate;
  try {
    rawTemplate = parseYaml(templateText);
  } catch (e) {
    throw new ProseTemplateError(`invalid YAML in ${templatePath}: ${e.message}`);
  }

  const template = parseTemplate(rawTemplate, collectSeries(panelData).keys());
  if (template.section !== section) {
    throw new ProseTemplateError(
      `template ${templatePath} declares section "${template.section}" but was loaded for "${section}"`
    );
  }

  const result = renderTemplate(template, panelData);
  return { ...result, templatePath, panelDataPath };
}
