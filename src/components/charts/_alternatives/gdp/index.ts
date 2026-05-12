/*
 * _alternatives/gdp/index.ts — chart-alternatives manifest for the GDP
 * section.
 *
 * Single source of truth for the entries rendered under the GDP section
 * on /chart-alternatives. Add a new alt by adding one entry below; the
 * page picks it up automatically on the next build.
 *
 * See _shared/shelfEntry.ts for the entry shape and _archive/<section>/
 * for the parked-indefinitely counterpart.
 */

import type { ChartShelfEntry } from "../_shared/shelfEntry";

import Alt1_ContributionsStacked from "./Alt1_ContributionsStacked.astro";
import Alt2_PerCapitaVsTotal from "./Alt2_PerCapitaVsTotal.astro";
import Alt3_IndustryHeatmap from "./Alt3_IndustryHeatmap.astro";
import Alt4_GdpVsCapacity from "./Alt4_GdpVsCapacity.astro";

export const entries: ChartShelfEntry[] = [
  {
    Component: Alt1_ContributionsStacked,
    file: "gdp/Alt1_ContributionsStacked.astro",
    title: "Contributions stacked",
    whatDifferent:
      "Stacked vertical bars by component (consumption, govt, investment, exports, imports, inventories) per quarter, with total-contrib overlay line.",
    whyBetter:
      "Production Panel 3 falls back to PanelEmpty; this revives the per-component story from raw CSVs.",
    dataFields:
      "gdp_contrib_{consumption,govt,investment,exports,imports,inventories}.csv + gdp_total_contribution.csv",
    addedAt: "2026-05-12",
  },
  {
    Component: Alt2_PerCapitaVsTotal,
    file: "gdp/Alt2_PerCapitaVsTotal.astro",
    title: "Total vs per-capita GDP, side-by-side",
    whatDifferent:
      "Small multiples: total real GDP path and per-capita path indexed to 2019Q4 = 100. Same y-axis for visual comparability.",
    whyBetter:
      "The population-padded-GDP critique is the dominant 2020s Canadian macro story; the small-multiple format makes the divergence impossible to miss.",
    dataFields: "gdp_quarterly.csv + pop_immigrants.csv + pop_net_npr.csv",
    addedAt: "2026-05-12",
  },
  {
    Component: Alt3_IndustryHeatmap,
    file: "gdp/Alt3_IndustryHeatmap.astro",
    title: "Industry Y/Y heatmap",
    whatDifferent:
      "Four industry Y/Y growth rates as stacked diverging bar rows: goods, services, manufacturing, mining/oil. Ink opacity encodes magnitude.",
    whyBetter:
      "Cycle dispersion across industries is invisible in a single-industry line; the heatmap puts dispersion in the foreground.",
    dataFields: "gdp_industry_{goods,services,manufacturing,mining_oil}.csv",
    addedAt: "2026-05-12",
  },
  {
    Component: Alt4_GdpVsCapacity,
    file: "gdp/Alt4_GdpVsCapacity.astro",
    title: "GDP Y/Y with capacity utilization overlay",
    whatDifferent:
      "GDP Y/Y primary line, total capacity utilization secondary dashed line, both quarterly.",
    whyBetter:
      "Capacity utilization alone is a level; paired with GDP Y/Y it tells the cycle-pressure story.",
    dataFields:
      "gdp_quarterly.csv (Y/Y derived) + capacity_util_total.csv",
    addedAt: "2026-05-12",
  },
];
