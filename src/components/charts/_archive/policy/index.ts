/*
 * _archive/policy/index.ts — chart-archive manifest for Policy.
 * See _archive/gdp/index.ts for the pattern.
 */

import type { ChartShelfEntry } from "../../_alternatives/_shared/shelfEntry";
import policyPanelData from "../../../../../data/site/panel_data/monetary.json";
import { pickPanel } from "../../_shared/panelData";

import Panel4BalanceSheet from "./Panel4BalanceSheet.astro";
import Panel5FederalTrajectory from "./Panel5FederalTrajectory.astro";
import Panel6FiscalStanceCycle from "./Panel6FiscalStanceCycle.astro";

const policy4Data = pickPanel(policyPanelData, 4);

export const entries: ChartShelfEntry[] = [
  {
    Component: Panel4BalanceSheet,
    file: "policy/Panel4BalanceSheet.astro",
    title: "Settlement balances + total assets dual-line (V1 — retired from production)",
    whatDifferent:
      "Original Panel 4. Plotted settlement balances (primary, liability side) against total Bank assets (secondary). V2 retired the dual-line view and rebuilt as a five-panel small-multiples grid of the asset-side composition (Total assets, GoC bonds, T-bills, Advances, Repos).",
    whyBetter:
      "Asset composition is the structural story after QT completion; the dual-line view conflated a liability-side gauge (settlement balances) with an asset-side total and gave neither story room to breathe.",
    dataFields: "data/site/panel_data/monetary.json panel-4.",
    addedAt: "2026-05-12",
    data: policy4Data,
  },
  {
    Component: Panel5FederalTrajectory,
    file: "policy/Panel5FederalTrajectory.astro",
    title: "Federal trajectory dual-series (V1 — retired from production)",
    whatDifferent:
      "Original Panel 5. Rendered monthly fiscal balance as bars and YTD balance as a dashed line on a shared y-axis. V2 (Panel6FederalTrajectorySplit) put the two series in separate side-by-side sub-panels with per-panel y-axes so each reads on its own scale.",
    whyBetter:
      "Splitting clarifies the read — monthly bars are noisy month to month, YTD accumulates monotonically within each fiscal year. The shared-axis form compromised both.",
    dataFields:
      "data/site/panel_data/monetary.json panel-6 (post-renumber); primary=dof_fiscal_monthly_balance, secondary=dof_fiscal_ytd_balance.",
    addedAt: "2026-05-13",
  },
  {
    Component: Panel6FiscalStanceCycle,
    file: "policy/Panel6FiscalStanceCycle.astro",
    title: "Fiscal stance proxy (V1 — retired from production)",
    whatDifferent:
      "Tracked total-economy capacity utilization (output-gap proxy) against the Fiscal Monitor YTD summary. Always carried NEAR status because a proper fiscal-stance read needs cyclically-adjusted primary balance (CAPB), which Department of Finance does not publish.",
    whyBetter:
      "Editorial call to drop the plate rather than ship a thin proxy. Future revival would require IMF Article IV CAPB ingestion.",
    dataFields:
      "primary=capacity_util_total; secondary=dof_fiscal_ytd_summary (residual reference; not currently emitted to a panel slot).",
    addedAt: "2026-05-13",
  },
];
