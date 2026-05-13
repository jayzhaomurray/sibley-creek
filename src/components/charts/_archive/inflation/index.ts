/*
 * _archive/inflation/index.ts — chart-archive manifest for Inflation.
 * See _archive/gdp/index.ts for the pattern.
 */

import type { ChartShelfEntry } from "../../_alternatives/_shared/shelfEntry";
import PanelHeadlineCPIDual from "./PanelHeadlineCPIDual.astro";

export const entries: ChartShelfEntry[] = [
  {
    Component: PanelHeadlineCPIDual,
    file: "inflation/PanelHeadlineCPIDual.astro",
    title: "Headline CPI dual-panel (V1 — retired from production)",
    whatDifferent:
      "Two-panel composite: m/m bars LEFT, Y/Y line with 1-3% control band RIGHT. The right panel carried Y/Y only as the level read.",
    whyBetter:
      "Retired 2026-05-13 in favour of PanelHeadlineCPITrio which adds a 3M-annualized (3M-AR) dashed line to the right panel — the higher-frequency momentum read alongside the smoothed Y/Y, with the control-band label re-positioned cleanly below the plot frame.",
    dataFields:
      "data/site/panel_data/inflation.json panel-1; primary = m/m %, secondary = cpi_all_items level.",
    addedAt: "2026-05-13",
  },
];
