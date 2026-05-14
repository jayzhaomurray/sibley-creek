/*
 * _alternatives/housing/index.ts — chart-alternatives manifest for the
 * Housing section. See _alternatives/gdp/index.ts for the pattern.
 */

import type { ChartShelfEntry } from "../_shared/shelfEntry";

import Alt1_HpiMultiCity from "./Alt1_HpiMultiCity.astro";
import Alt2_StartsSmoothing from "./Alt2_StartsSmoothing.astro";
import Alt3_MortgageVsHpi from "./Alt3_MortgageVsHpi.astro";
import Alt4_SnlrVsHpi from "./Alt4_SnlrVsHpi.astro";
import Alt5_HpiCmaLevels from "./Alt5_HpiCmaLevels.astro";
import Panel5MortgageStack from "./Panel5MortgageStack.astro";
import Panel6PopulationStock from "./Panel6PopulationStock.astro";

export const entries: ChartShelfEntry[] = [
  {
    Component: Alt1_HpiMultiCity,
    file: "housing/Alt1_HpiMultiCity.astro",
    title: "MLS HPI Y/Y national + 3 CMAs",
    whatDifferent:
      "National solid, Toronto dashed, Vancouver sparse-dashed, Calgary dotted. All pure ink; weight and dash carry identity.",
    whyBetter:
      "National HPI averages across very different regional cycles. The Calgary-vs-Toronto divergence is the housing story of the past two years.",
    dataFields:
      "crea_hpi_{canada,toronto,vancouver,calgary}.csv, all Y/Y derived",
    addedAt: "2026-05-12",
  },
  {
    Component: Alt2_StartsSmoothing,
    file: "housing/Alt2_StartsSmoothing.astro",
    title: "Housing starts: 6mma + 3mma + monthly",
    whatDifferent:
      "Three smoothings of the SAAR starts series, with monthly noise included.",
    whyBetter:
      "Starts are noisy; the smoothings train the eye on the trend rather than the print.",
    dataFields: "housing_starts.csv with derived 3mma + 6mma",
    addedAt: "2026-05-12",
  },
  {
    Component: Alt3_MortgageVsHpi,
    file: "housing/Alt3_MortgageVsHpi.astro",
    title: "5yr mortgage rate vs HPI Y/Y",
    whatDifferent:
      "Same-axis (both %) dual-series overlay showing the transmission channel.",
    whyBetter:
      "The mortgage rate alone is a level; paired with HPI Y/Y it tells a transmission story. BoC cuts show up here as HPI stabilizing.",
    dataFields: "mortgage_rate_5yr.csv + crea_hpi_canada.csv (Y/Y)",
    addedAt: "2026-05-12",
  },
  {
    Component: Alt4_SnlrVsHpi,
    file: "housing/Alt4_SnlrVsHpi.astro",
    title: "SNLR with HPI Y/Y overlay",
    whatDifferent:
      "SNLR primary with the sellers'-market threshold (60%) as reference; HPI Y/Y secondary. The leading-indicator pair.",
    whyBetter:
      "SNLR > 60 leads HPI acceleration by 3-6 months; the overlay makes the lead visible.",
    dataFields: "crea_snlr.csv + crea_mls_hpi.csv (Y/Y)",
    addedAt: "2026-05-12",
  },
  {
    Component: Alt5_HpiCmaLevels,
    file: "housing/Alt5_HpiCmaLevels.astro",
    title: "Six-CMA MLS HPI in levels (companion to plate-1 Y/Y)",
    whatDifferent:
      "Series is index levels (Jan 2005 = 100) rather than Y/Y percent change. Window extends to 180 months (~15 years) so the full structural arc — pre-pandemic run-up, 2022 peak, correction — is visible in one frame.",
    whyBetter:
      "Y/Y is cyclical-state: it answers 'what is the momentum?' Levels are structural-state: they answer 'how far have prices come from the base?' A reader comparing Toronto 292 to Edmonton 241 to Vancouver 306 in index terms grasps affordability dispersion in one scan that the Y/Y chart cannot deliver.",
    dataFields:
      "crea_hpi_canada.csv, crea_hpi_toronto.csv, crea_hpi_vancouver.csv, crea_hpi_montreal.csv, crea_hpi_calgary.csv, crea_hpi_ottawa.csv, crea_hpi_edmonton.csv — levels direct (no transform)",
    addedAt: "2026-05-13",
  },
  {
    Component: Panel5MortgageStack,
    file: "housing/Panel5MortgageStack.astro",
    title: "Panel5MortgageStack (retired from production — TODO describe)",
    whatDifferent:
      "TODO: describe what made this version distinct.",
    whyBetter:
      "TODO: describe what won out and why this was parked.",
    dataFields: "TODO: list source panel_data slot or CSV file(s).",
    addedAt: "2026-05-13",
  },
  {
    Component: Panel6PopulationStock,
    file: "housing/Panel6PopulationStock.astro",
    title: "Panel6PopulationStock (retired from production — TODO describe)",
    whatDifferent:
      "TODO: describe what made this version distinct.",
    whyBetter:
      "TODO: describe what won out and why this was parked.",
    dataFields: "TODO: list source panel_data slot or CSV file(s).",
    addedAt: "2026-05-13",
  },
];
