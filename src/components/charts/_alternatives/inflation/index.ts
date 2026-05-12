/*
 * _alternatives/inflation/index.ts — chart-alternatives manifest for the
 * Inflation section. See _alternatives/gdp/index.ts for the pattern.
 */

import type { ChartShelfEntry } from "../_shared/shelfEntry";

import Alt1_CoreOverlay from "./Alt1_CoreOverlay.astro";
import Alt2_ComponentsSmallMultiples from "./Alt2_ComponentsSmallMultiples.astro";
import Alt3_BosBreadthStack from "./Alt3_BosBreadthStack.astro";
import Alt4_HeadlineMinusCore from "./Alt4_HeadlineMinusCore.astro";

export const entries: ChartShelfEntry[] = [
  {
    Component: Alt1_CoreOverlay,
    file: "inflation/Alt1_CoreOverlay.astro",
    title: "Three core measures overlay",
    whatDifferent:
      "Trim (primary solid), median (secondary dashed), common (tertiary sparse-dashed) on shared % axis with 2% target reference.",
    whyBetter:
      "Production Panel 2 carries trim + median; adding common shows dispersion across BoC core measures, which is the editorial signal at turning points.",
    dataFields: "cpi_trim.csv + cpi_median.csv + cpi_common.csv",
    addedAt: "2026-05-12",
  },
  {
    Component: Alt2_ComponentsSmallMultiples,
    file: "inflation/Alt2_ComponentsSmallMultiples.astro",
    title: "CPI components 2x2 small multiples",
    whatDifferent:
      "Four indexed-to-2019 component price levels in a 2x2 grid: shelter, food, energy, services. Each has its own frame and direct dot.",
    whyBetter:
      "Cumulative price levels (food up 35%, shelter up 28%) are what the reader wants from a components view; Y/Y momentum lines lose the cumulative read.",
    dataFields:
      "cpi_shelter.csv, cpi_food.csv, cpi_energy.csv, cpi_services.csv",
    addedAt: "2026-05-12",
  },
  {
    Component: Alt3_BosBreadthStack,
    file: "inflation/Alt3_BosBreadthStack.astro",
    title: "BOS breadth distribution stacked",
    whatDifferent:
      "100%-stacked bars per BOS round: below-1% / 1-2% / 2-3% / above-3% buckets. Ink opacity tracks distance from target; above-3% reads heaviest.",
    whyBetter:
      "Distribution beats average. Business price-setters drive realized inflation, and their breadth leads CPI by quarters.",
    dataFields:
      "bos_dist_below1.csv + bos_dist_1to2.csv + bos_dist_2to3.csv + bos_dist_above3.csv",
    addedAt: "2026-05-12",
  },
  {
    Component: Alt4_HeadlineMinusCore,
    file: "inflation/Alt4_HeadlineMinusCore.astro",
    title: "Headline minus core-trim gap",
    whatDifferent:
      "Single zero-crossing line: headline Y/Y minus trim Y/Y. The food/energy noise vs underlying trend diagnostic.",
    whyBetter:
      "One line, one declarative statement. The chart a fixed-income desk reads first.",
    dataFields: "cpi_all_items.csv (Y/Y derived) - cpi_trim.csv",
    addedAt: "2026-05-12",
  },
];
