/*
 * _alternatives/trade/index.ts — chart-alternatives manifest for the
 * Trade section. See _alternatives/gdp/index.ts for the pattern.
 */

import type { ChartShelfEntry } from "../_shared/shelfEntry";

import Alt1_ExportsImports from "./Alt1_ExportsImports.astro";
import Alt2_UsExportShare from "./Alt2_UsExportShare.astro";
import Alt3_BalanceSmoothing from "./Alt3_BalanceSmoothing.astro";
import Alt4_TermsTradeVsWti from "./Alt4_TermsTradeVsWti.astro";
import Alt_TariffSectorPivot from "./Alt_TariffSectorPivot.astro";

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
    Component: Alt_TariffSectorPivot,
    file: "trade/Alt_TariffSectorPivot.astro",
    title: "Are tariff-exposed sectors pivoting? — 4-panel sector export diversification",
    whatDifferent:
      "Four 2x2 panels (steel, aluminum, softwood, autos); each shows US and non-US exports as 12mma indexed to Jan 2020 = 100. Divergence between the two lines is the editorial signal.",
    whyBetter:
      "The 'pivot question' is the most live trade story in Canadian macro. Raw level panels obscure non-US movement because US flows dwarf them by 6-10x. Indexing surfaces whether non-US is actually rising to offset US losses — the question no raw-level chart can answer.",
    dataFields:
      "trade.json panel-7-alt (primary + secondary + extras[0-5]), 12mma indexed to Jan 2020 = 100",
    addedAt: "2026-05-14",
  },
];
