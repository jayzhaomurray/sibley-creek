/*
 * _archive/policy/index.ts — chart-archive manifest for Policy.
 * See _archive/gdp/index.ts for the pattern.
 */

import type { ChartShelfEntry } from "../../_alternatives/_shared/shelfEntry";
import policyPanelData from "../../../../../data/site/panel_data/policy.json";
import { pickPanel } from "../../_shared/panelData";

import Panel3BoCFedSpread from "../../policy/Panel3BoCFedSpread.astro";
import Panel4BalanceSheet from "./Panel4BalanceSheet.astro";

const policy3Data = pickPanel(policyPanelData, 3);
const policy4Data = pickPanel(policyPanelData, 4);

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
  {
    Component: Panel4BalanceSheet,
    file: "policy/Panel4BalanceSheet.astro",
    title: "Settlement balances + total assets dual-line (V1 — retired from production)",
    whatDifferent:
      "Original Panel 4. Plotted settlement balances (primary, liability side) against total Bank assets (secondary). V2 retired the dual-line view and rebuilt as a five-panel small-multiples grid of the asset-side composition (Total assets, GoC bonds, T-bills, Advances, Repos).",
    whyBetter:
      "Asset composition is the structural story after QT completion; the dual-line view conflated a liability-side gauge (settlement balances) with an asset-side total and gave neither story room to breathe.",
    dataFields: "data/site/panel_data/policy.json panel-4.",
    addedAt: "2026-05-12",
    data: policy4Data,
  },
];
