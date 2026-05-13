/*
 * _archive/labour/index.ts — chart-archive manifest for Labour.
 * See _archive/gdp/index.ts for the pattern.
 */

import type { ChartShelfEntry } from "../../_alternatives/_shared/shelfEntry";
import labourPanelData from "../../../../../data/site/panel_data/labour.json";
import { pickPanel } from "../../_shared/panelData";

import Panel2PerCapita from "../../labour/Panel2PerCapita.astro";
import Alt1_TripleLabourSeries from "./Alt1_TripleLabourSeries.astro";
import PanelBeveridgeCurve from "./PanelBeveridgeCurve.astro";
import Panel5IRCCSupplyTrajectory from "./Panel5IRCCSupplyTrajectory.astro";
import Panel7EIBeneficiaries from "./Panel7EIBeneficiaries.astro";

const labour2Data = pickPanel(labourPanelData, 2);
const labour4Data = pickPanel(labourPanelData, 4);
const labour5Data = pickPanel(labourPanelData, 5);
const labour7Data = pickPanel(labourPanelData, 7);

export const entries: ChartShelfEntry[] = [
  {
    Component: Alt1_TripleLabourSeries,
    file: "labour/Alt1_TripleLabourSeries.astro",
    title: "Unemp + emp rate + participation triple",
    whatDifferent:
      "Three LFS series overlaid: unrate primary solid, emprate secondary dashed-4-2, participation tertiary sparse-dashed-2-3. Pure ink throughout.",
    whyBetter:
      "The three together tell the full LFS story; participation movement explains how the unemployment and employment rates can move in the same direction.",
    dataFields:
      "unemployment_rate.csv + employment_rate.csv + participation_rate.csv",
    addedAt: "2026-05-12",
  },
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
  {
    Component: PanelBeveridgeCurve,
    file: "labour/PanelBeveridgeCurve.astro",
    title: "Beveridge curve — vacancy rate vs unemployment rate, time-path scatter",
    whatDifferent:
      "Beveridge curve as a 2D plot — vacancy rate on x, unemployment rate on y, time as the path. Hollow dots for the May–Sep 2020 imputed window.",
    whyBetter:
      "Carries the historical cycle-path story (pandemic loose → 2022 peak tightness → 2023-25 loosening to past pre-pandemic equilibrium) that the lines+spread companion in Plate 5 compresses out.",
    dataFields:
      "Statistics Canada Table 14-10-0432-01 (JVWS), Table 14-10-0287-01 (LFS unemployment rate), Indeed Hiring Lab postings (used to impute Apr–Sep 2020 vacancy rate via OLS).",
    addedAt: "2026-05-12",
    data: labour4Data,
  },
  {
    Component: Panel5IRCCSupplyTrajectory,
    file: "labour/Panel5IRCCSupplyTrajectory.astro",
    title: "IRCC supply trajectory — PR landings vs plan, net NPR quarterly",
    whatDifferent:
      "Quarterly population supply trajectory: net PR landings vs IRCC plan, plus net NPR. Quarterly cadence.",
    whyBetter:
      "Captures the supply-side story IRCC plan revisions drive, but doesn’t earn a tracker plate — quarterly cadence doesn’t match the monthly LFS print rhythm. Belongs on a supply-side deep-dive.",
    dataFields:
      "IRCC plan vs landings; StatCan Table 17-10-0040 / 17-10-0059 (population components).",
    addedAt: "2026-05-12",
    data: labour5Data,
  },
  {
    Component: Panel7EIBeneficiaries,
    file: "labour/Panel7EIBeneficiaries.astro",
    title: "EI regular beneficiaries per 1,000 labour force ex-NPRs",
    whatDifferent:
      "Monthly EI regular beneficiaries level, with cyclical context.",
    whyBetter:
      "EI is a redundant cyclical-loosening read once Plates 1–3 and Plate 5 are on the page. Keep for revival if EI ever decouples from the headline read.",
    dataFields:
      "Statistics Canada Table 14-10-0011-01 (EI beneficiaries, monthly).",
    addedAt: "2026-05-12",
    data: labour7Data,
  },
];
