/*
 * _alternatives/housing/index.ts — chart-alternatives manifest for the
 * Housing section. See _alternatives/gdp/index.ts for the pattern.
 */

import type { ChartShelfEntry } from "../_shared/shelfEntry";

import Alt1_HpiMultiCity from "./Alt1_HpiMultiCity.astro";
import Alt2_StartsSmoothing from "./Alt2_StartsSmoothing.astro";
import Alt3_MortgageVsHpi from "./Alt3_MortgageVsHpi.astro";
import Alt4_SnlrVsHpi from "./Alt4_SnlrVsHpi.astro";
import Panel5MortgageStack from "./Panel5MortgageStack.astro";
import Panel6PopulationStock from "./Panel6PopulationStock.astro";
import Panel1Prices_YoY_SmallMults from "./Panel1Prices_YoY_SmallMults.astro";
import Alt7_HousingActivityUC from "./Alt7_HousingActivityUC.astro";
import Panel3Inventory_V1 from "./Panel3Inventory_V1.astro";

export const entries: ChartShelfEntry[] = [
  {
    Component: Panel3Inventory_V1,
    file: "housing/Panel3Inventory_V1.astro",
    title: "Panel3Inventory V1 (retired — single-series SNLR via PanelLiveChart)",
    whatDifferent:
      "Single-series SNLR line via shared PanelLiveChart. Secondary slot wired to crea_resales (indexed) as a comparator overlay. No balanced-market band. No 12mma treatment on the sales series.",
    whyBetter:
      "Replaced by Panel3SalesComposite (two-panel, per-panel y-axis): left panel carries CREA sales index with 12mma + raw comparator; right panel carries SNLR with 40-60 balanced-market band. More editorial information per plate.",
    dataFields:
      "data/site/panel_data/housing.json panel-3 (crea_snlr primary, crea_resales secondary).",
    addedAt: "2026-05-13",
  },
  {
    Component: Alt7_HousingActivityUC,
    file: "housing/Alt7_HousingActivityUC.astro",
    title: "Housing starts + units under construction composite (V1 — retired from production)",
    whatDifferent:
      "Two-panel composite, shared y-axis. Left: housing starts (12mma main + raw comparator). Right: units under construction (4qma main + raw comparator). CMHC 430-480k band in left panel. Pandemic vertical band 2020-03 to 2022-03 in both panels.",
    whyBetter:
      "Editorial pivot to a per-capita lens — UC shows pipeline drainage but says nothing about per-person supply adequacy.",
    dataFields:
      "data/site/panel_data/housing.json panel-2 (housing_starts monthly, units_under_construction quarterly).",
    addedAt: "2026-05-13",
  },
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
  {
    Component: Panel1Prices_YoY_SmallMults,
    file: "housing/Panel1Prices_YoY_SmallMults.astro",
    title: "Six-CMA MLS HPI Y/Y, small-multiples (alternative to plate-1 levels view)",
    whatDifferent:
      "Y/Y % change view. Shows cyclical direction (decline / rise) directly; levels view shows structural distance from 2005 baseline.",
    whyBetter:
      "Same chart, complementary view; reader can compare. Y/Y answers the momentum question; levels answer the structural-state question. Both are valid depending on editorial purpose.",
    dataFields:
      "panel_data housing panel-1: primary crea_hpi_canada_yoy, extras crea_hpi_{toronto,vancouver,montreal,calgary,ottawa,edmonton}_yoy",
    addedAt: "2026-05-13",
  },
];
