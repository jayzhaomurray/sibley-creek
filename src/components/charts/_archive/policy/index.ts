/*
 * _archive/policy/index.ts — chart-archive manifest for Policy.
 * See _archive/gdp/index.ts for the pattern.
 */

import type { ChartShelfEntry } from "../../_alternatives/_shared/shelfEntry";
import policyPanelData from "../../../../../data/site/panel_data/policy.json";
import { pickPanel } from "../../_shared/panelData";

import Panel3BoCFedSpread from "../../policy/Panel3BoCFedSpread.astro";

const policy3Data = pickPanel(policyPanelData, 3);

export const entries: ChartShelfEntry[] = [
  {
    Component: Panel3BoCFedSpread,
    file: "policy/Panel3BoCFedSpread.astro",
    title: "BoC-Fed spread (V1 two-level form — retired from production)",
    whatDifferent:
      "Original Panel 3. Plotted two parallel 2y yields and forced the reader to do the arithmetic. V2 derived Canada-minus-US 2y spread in bps as a single line with a zero-line (parity) reference; cross-zero events read directly.",
    whyBetter:
      "Parked from the 2026-05-11 editorial audit. V2 (derived spread) won and shipped. Original retained as a record of the two-level form.",
    dataFields: "data/site/panel_data/policy.json panel-3.",
    addedAt: "2026-05-12",
    data: policy3Data,
  },
];
