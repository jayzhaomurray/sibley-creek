/*
 * _alternatives/trade/index.ts — chart-alternatives manifest for the
 * Trade section. See _alternatives/gdp/index.ts for the pattern.
 */

import type { ChartShelfEntry } from "../_shared/shelfEntry";
import tradePanelData from "../../../../../data/site/panel_data/trade.json";
import { pickPanel } from "../../_shared/panelData";

import Alt1_ExportsImports from "./Alt1_ExportsImports.astro";
import Alt2_UsExportShare from "./Alt2_UsExportShare.astro";
import Alt3_BalanceSmoothing from "./Alt3_BalanceSmoothing.astro";
import Alt4_TermsTradeVsWti from "./Alt4_TermsTradeVsWti.astro";

// Demoted-from-production: kept on the alt shelf for reference.
import TradePanel1TradeBalance from "../../trade/Panel1TradeBalance.astro";
import TradePanel2CurrentAccount from "../../trade/Panel2CurrentAccountV2.astro";
import TradePanel4TariffState from "../../trade/Panel4TariffState.astro";
import TradePanel5TermsOfTrade from "../../trade/Panel5TermsOfTradeV2.astro";
import TradePanel6FDIBySector from "../../trade/Panel6FDIBySector.astro";

const tradePanel1Data = pickPanel(tradePanelData, 1);
const tradePanel2Data = pickPanel(tradePanelData, 2);
const tradePanel5Data = pickPanel(tradePanelData, 5);
const tradePanel6Data = pickPanel(tradePanelData, 6);

export const entries: ChartShelfEntry[] = [
  {
    Component: Alt1_ExportsImports,
    file: "trade/Alt1_ExportsImports.astro",
    title: "Total exports + total imports overlay",
    whatDifferent:
      "Both flows in CAD billions on shared axis; the visible gap is the trade balance.",
    whyBetter:
      "Level of trade flows matters as much as the balance. Production Panel 1 carries the balance alone.",
    dataFields: "trade_exports_total.csv + trade_imports_total.csv",
    addedAt: "2026-05-12",
  },
  {
    Component: Alt2_UsExportShare,
    file: "trade/Alt2_UsExportShare.astro",
    title: "US share of exports with 12mma",
    whatDifferent:
      "Computed share US/Total with a 12-month moving average overlay. The dependence chart.",
    whyBetter:
      "The single most-cited Canadian fact (\"75% to US\") deserves its own chart.",
    dataFields: "trade_exports_us.csv / trade_exports_total.csv",
    addedAt: "2026-05-12",
  },
  {
    Component: Alt3_BalanceSmoothing,
    file: "trade/Alt3_BalanceSmoothing.astro",
    title: "Trade balance: 3mma + 12mma + monthly",
    whatDifferent:
      "Three temporal scales on one chart: monthly noise, 3mma cycle, 12mma trend.",
    whyBetter:
      "Trade prints are revision-noisy; three smoothings discipline the reader away from over-reading one month.",
    dataFields: "trade_balance_total.csv with derived 3mma + 12mma",
    addedAt: "2026-05-12",
  },
  {
    Component: Alt4_TermsTradeVsWti,
    file: "trade/Alt4_TermsTradeVsWti.astro",
    title: "Terms of trade with WTI overlay",
    whatDifferent:
      "Both indexed to 2017 = 100 on a shared axis. Canadian terms-of-trade is essentially a leveraged bet on oil.",
    whyBetter:
      "Production Panel 5 carries terms-of-trade alone; the WTI overlay makes the mechanism explicit.",
    dataFields:
      "trade.json panel-5 (terms_of_trade) + wti.csv indexed",
    addedAt: "2026-05-12",
  },
  {
    Component: TradePanel4TariffState,
    file: "trade/Panel4TariffState.astro",
    title: "Tariff state: US trade actions affecting Canada (V2 — retired from production)",
    whatDifferent:
      "Horizontal-bar tracker filtered to in-force tariff actions only, deduped by sector to the most recent proclamation, with under-review actions in a footer line. Successor to V1 (Alt_Panel4TariffState_V1) which mixed in-force and superseded rows.",
    whyBetter:
      "Demoted on 2026-05-14: source-card-driven content carries staleness risk that we just got bit by (the IEEPA cards were three months stale when the underlying authority was struck down by SCOTUS in Feb 2026). The other four trade plates are all StatCan + Yahoo data-driven, no manual maintenance required. The tariff tracker would belong in a Tariff page or methodology page with explicit verification cadence, not on a trade topic page where data-driven plates already carry the pivot thesis.",
    dataFields: "data/derived/tariff_state.json (filtered to status === 'in_force')",
    addedAt: "2026-05-14",
  },
  {
    Component: TradePanel1TradeBalance,
    file: "trade/Panel1TradeBalance.astro",
    title: "Goods trade balance, monthly + 3mma (V1 — retired from production)",
    whatDifferent:
      "Headline merchandise balance with monthly bar + 3-month moving average line. Standard cycle anchor.",
    whyBetter:
      "Demoted on 2026-05-14: too high-level for the 'is the pivot working?' editorial frame the trade section is now organized around. Reads well as a cycle anchor but doesn't speak to the section's central question.",
    dataFields: "trade.json panel-1 (trade balance, exports, imports)",
    data: tradePanel1Data,
    addedAt: "2026-05-14",
  },
  {
    Component: TradePanel2CurrentAccount,
    file: "trade/Panel2CurrentAccountV2.astro",
    title: "Current account: goods, services, primary income (V1 — retired from production)",
    whatDifferent:
      "Quarterly current-account decomposition with goods, services, and primary-income components.",
    whyBetter:
      "Demoted on 2026-05-14: too aggregated for the pivot-question framing; primary-income surplus is editorially interesting but orthogonal to the trade-reorientation story.",
    dataFields: "trade.json panel-2 (current account components)",
    data: tradePanel2Data,
    addedAt: "2026-05-14",
  },
  {
    Component: TradePanel5TermsOfTrade,
    file: "trade/Panel5TermsOfTradeV2.astro",
    title: "Terms of trade, national accounts (V1 — retired from production)",
    whatDifferent:
      "Quarterly terms-of-trade index (2017 = 100). Export prices relative to import prices.",
    whyBetter:
      "Demoted on 2026-05-14: flat at ~105 with little cycle movement; doesn't speak to whether the pivot is working. Better suited to a macro-cycle deep dive than the trade topic page.",
    dataFields: "trade.json panel-5 (terms_of_trade)",
    data: tradePanel5Data,
    addedAt: "2026-05-14",
  },
  {
    Component: TradePanel6FDIBySector,
    file: "trade/Panel6FDIBySector.astro",
    title: "FDI by sector: inward and outward (V1 — retired from production)",
    whatDifferent:
      "Sectoral foreign direct-investment flows from StatCan 36-10-0659-01.",
    whyBetter:
      "Demoted on 2026-05-14: annual frequency, disconnected from the current tariff cycle. Chart component was placeholder when promoted to alts.",
    dataFields: "trade.json panel-6 (fdi_inward + fdi_outward by industry)",
    data: tradePanel6Data,
    addedAt: "2026-05-14",
  },
];
