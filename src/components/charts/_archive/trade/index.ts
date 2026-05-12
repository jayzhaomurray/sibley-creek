/*
 * _archive/trade/index.ts — chart-archive manifest for Trade.
 * See _archive/gdp/index.ts for the pattern.
 */

import type { ChartShelfEntry } from "../../_alternatives/_shared/shelfEntry";
import tradePanelData from "../../../../../data/site/panel_data/trade.json";
import { pickPanel } from "../../_shared/panelData";

import Panel2CurrentAccount from "../../trade/Panel2CurrentAccount.astro";
import Panel3PartnerShares from "../../trade/Panel3PartnerShares.astro";
import Panel5TermsOfTrade from "../../trade/Panel5TermsOfTrade.astro";

const trade2Data = pickPanel(tradePanelData, 2);
const trade3Data = pickPanel(tradePanelData, 3);
const trade5Data = pickPanel(tradePanelData, 5);

export const entries: ChartShelfEntry[] = [
  {
    Component: Panel2CurrentAccount,
    file: "trade/Panel2CurrentAccount.astro",
    title: "Current account (V1 with stale label — retired from production)",
    whatDifferent:
      "Original Panel 2. Pipeline emits current_account_balance (StatCan 36-10-0018, quarterly SA, C$ millions) as primary, but the wrapper still labelled the line \"Trade bal.\" (leftover from when the primary was the monthly merchandise balance). V2 keeps the data wiring, corrects the direct label and aria copy, and drops the components-level secondary so the canvas shows a single quarterly headline line.",
    whyBetter:
      "Parked from the 2026-05-11 label-vs-data audit. V2 (honest label) won and shipped. Original retained as the documented mislabelled form.",
    dataFields: "data/site/panel_data/trade.json panel-2.",
    addedAt: "2026-05-12",
    data: trade2Data,
  },
  {
    Component: Panel3PartnerShares,
    file: "trade/Panel3PartnerShares.astro",
    title: "Partner shares (V1 two parallel levels — retired from production)",
    whatDifferent:
      "Original Panel 3. Plotted two parallel rising level lines (US exports + total exports); the reader cannot eyeball \"US share at 66% and falling\" from levels. V2 derived the US share as a single % line; the structural drift becomes visible in the chart shape.",
    whyBetter:
      "Parked from the 2026-05-11 editorial audit. V2 (derived US share) won and shipped. Original retained as a record of the two-level form.",
    dataFields: "data/site/panel_data/trade.json panel-3.",
    addedAt: "2026-05-12",
    data: trade3Data,
  },
  {
    Component: Panel5TermsOfTrade,
    file: "trade/Panel5TermsOfTrade.astro",
    title: "Terms of trade (V1 with WTI/Brent proxy mislabel — retired from production)",
    whatDifferent:
      "Original Panel 5. Labelled the chart \"WTI / Brent\" while the pipeline emits the StatCan terms-of-trade ratio (national-accounts basis, quarterly) as primary, with a Y/Y % secondary. V2 keeps the same primary series, relabels honestly, and drops the Y/Y secondary so the canvas shows a single index line. The title now matches the chart.",
    whyBetter:
      "Parked from the 2026-05-11 label-vs-data audit. V2 (honest label, single index) won and shipped. Original retained as a documented mislabel.",
    dataFields: "data/site/panel_data/trade.json panel-5.",
    addedAt: "2026-05-12",
    data: trade5Data,
  },
];
