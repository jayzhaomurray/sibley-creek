/*
 * _archive/labour/index.ts — chart-archive manifest for Labour.
 * See _archive/gdp/index.ts for the pattern.
 */

import type { ChartShelfEntry } from "../../_alternatives/_shared/shelfEntry";
import labourPanelData from "../../../../../data/site/panel_data/labour.json";
import { pickPanel } from "../../_shared/panelData";

import Panel2PerCapita from "../../labour/Panel2PerCapita.astro";

const labour2Data = pickPanel(labourPanelData, 2);

export const entries: ChartShelfEntry[] = [
  {
    Component: Panel2PerCapita,
    file: "labour/Panel2PerCapita.astro",
    title: "Per-capita employment (V1 mislabelled — retired from production)",
    whatDifferent:
      "Original Panel 2. Plotted unemployment (millions) and aggregate hours (thousands) — two unrelated levels with no per-capita arithmetic. V2 derived per-capita employment Y/Y from the employment-rate series (employment over 15+ population) as a single % Y/Y line.",
    whyBetter:
      "Parked from the 2026-05-11 editorial audit. The V2 derived-per-capita-Y/Y framing won and shipped (Panel2LabourStocks is now live, Panel2PerCapitaV2 covers the per-capita Y/Y story). Original retained so the level-form misread is documented.",
    dataFields: "data/site/panel_data/labour.json panel-2.",
    addedAt: "2026-05-12",
    data: labour2Data,
  },
];
