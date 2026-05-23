/*
 * _archive/gdp/index.ts — chart-archive manifest for the GDP section.
 *
 * Holding zone for charts the user wants to keep but isn't actively
 * iterating on. Entries with `pinned: true` render in the Pinned zone
 * at the top of /chart-archive; the rest render in the Archive zone
 * below, sorted by `addedAt` desc when set, else alphabetically.
 *
 * See _alternatives/_shared/shelfEntry.ts for the entry shape and
 * _alternatives/gdp/index.ts for the live-iteration counterpart.
 */

import type { ChartShelfEntry } from "../../_alternatives/_shared/shelfEntry";
import gdpPanelData from "../../../../../data/site/panel_data/output.json";
import { pickPanel } from "../../_shared/panelData";

import Panel1HeadlineGDP from "../../gdp/Panel1HeadlineGDP.astro";
import Panel4PerCapita from "../../gdp/Panel4PerCapita.astro";
import Panel2IndustryAggregate from "./Panel2IndustryAggregate.astro";
import Panel6IndustryCyclical from "./Panel6IndustryCyclical.astro";

const gdp1Data = pickPanel(gdpPanelData, 1);
const gdp4Data = pickPanel(gdpPanelData, 4);

export const entries: ChartShelfEntry[] = [
  {
    Component: Panel1HeadlineGDP,
    file: "gdp/Panel1HeadlineGDP.astro",
    title: "Headline GDP (V1 levels — retired from production)",
    whatDifferent:
      "Original headline GDP plate. Plotted monthly and quarterly levels as smooth rising lines; the section asks about growth rates, not levels. V2 derived m/m % as the primary solid line and Q/Q SAAR % as the dashed secondary with a zero-line reference; V3 is now live.",
    whyBetter:
      "Parked from the 2026-05-11 editorial audit. The V2 (growth-rate framing) won and shipped; V3 is now live. Original retained as a record of the level-form chart in case the framing is revisited.",
    dataFields: "data/site/panel_data/gdp.json panel-1.",
    addedAt: "2026-05-12",
    data: gdp1Data,
  },
  {
    Component: Panel4PerCapita,
    file: "gdp/Panel4PerCapita.astro",
    title: "Per-capita GDP (V1 two-level form — retired from production)",
    whatDifferent:
      "Original per-capita GDP plate. Rendered quarterly real GDP and an immigrant-flow proxy for population as two unrelated levels mislabelled as per-capita. V2 derived per-capita GDP Y/Y from gdp_quarterly / pop_total at build as a single % Y/Y line with a zero-line reference.",
    whyBetter:
      "Parked from the 2026-05-11 editorial audit. The V2 derived-per-capita-Y/Y framing won and shipped (via PanelTotalVsPerCapita / Panel4PerCapitaV2). Original retained as a record of the mislabelled two-level form so the misread is documented.",
    dataFields: "data/site/panel_data/gdp.json panel-4.",
    addedAt: "2026-05-12",
    data: gdp4Data,
  },
  {
    Component: Panel2IndustryAggregate,
    file: "gdp/Panel2IndustryAggregate.astro",
    title: "Panel2IndustryAggregate (retired from production — TODO describe)",
    whatDifferent:
      "TODO: describe what made this version distinct.",
    whyBetter:
      "TODO: describe what won out and why this was parked.",
    dataFields: "TODO: list source panel_data slot or CSV file(s).",
    addedAt: "2026-05-13",
  },
  {
    Component: Panel6IndustryCyclical,
    file: "gdp/Panel6IndustryCyclical.astro",
    title: "Panel6IndustryCyclical (retired from production — TODO describe)",
    whatDifferent:
      "TODO: describe what made this version distinct.",
    whyBetter:
      "TODO: describe what won out and why this was parked.",
    dataFields: "TODO: list source panel_data slot or CSV file(s).",
    addedAt: "2026-05-13",
  },
];
