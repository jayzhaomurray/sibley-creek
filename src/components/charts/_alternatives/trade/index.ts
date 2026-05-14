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
import Alt_GoldExportsAndPrice from "./Alt_GoldExportsAndPrice.astro";
import Alt_AluminumByDestination from "./Alt_AluminumByDestination.astro";

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
  {
    Component: Alt_GoldExportsAndPrice,
    file: "trade/Alt_GoldExportsAndPrice.astro",
    title: "Gold exports surge — price-driven bullion flow, not industrial demand",
    whatDifferent:
      "Two-panel composite (720x405): left shows total and UK-destination gold/PGM exports in CAD millions; right shows gold price in USD/oz. Same x-axis window (2020 to present). UK share ~97% of total in March 2026 — the two left-panel lines nearly overlap, which is the editorial signal.",
    whyBetter:
      "The gold-export surge is the single largest anomaly in the 2025-26 Canadian trade data. Pairing the price chart is the fastest way to establish price-driven causality: both series climb in lockstep, ruling out a structural industrial-export shift.",
    dataFields:
      "exports_gold_total.csv + exports_gold_uk.csv (StatCan 12-10-0182-01 NAPCS 35) + gold_price_monthly.csv",
    addedAt: "2026-05-14",
  },
  {
    Component: Alt_AluminumByDestination,
    file: "trade/Alt_AluminumByDestination.astro",
    title: "Canadian aluminum exports by destination — 4-panel level chart",
    whatDifferent:
      "Four 2x2 panels (US / Netherlands / Mexico / all other non-US) showing 12mma level in CAD millions with per-panel y-axes. US at ~772M dwarfs everything else.",
    whyBetter:
      "Makes the geographic concentration visceral: the 'pivot' from the US is essentially one corridor (Netherlands rising to 141M); Mexico is flat at 22M and all other non-US is flat at 42M. The sector-pivot chart (Alt_TariffSectorPivot) asks 'is there a pivot?'; this chart answers 'to exactly where.'",
    dataFields:
      "exports_aluminum_us/nld/mex/nonus.csv — 12mma, CAD millions, 2020+",
    addedAt: "2026-05-14",
  },
];
