/*
 * _alternatives/policy/index.ts — chart-alternatives manifest for the
 * Policy section. See _alternatives/gdp/index.ts for the pattern.
 */

import type { ChartShelfEntry } from "../_shared/shelfEntry";

import Alt_FiscalStanceRatios from "./Alt_FiscalStanceRatios.astro";
import Alt2_BalanceSheetOverlay from "./Alt2_BalanceSheetOverlay.astro";
import Alt3_YieldCurveTriple from "./Alt3_YieldCurveTriple.astro";
import Alt4_TwosTensSlope from "./Alt4_TwosTensSlope.astro";

export const entries: ChartShelfEntry[] = [
  {
    Component: Alt_FiscalStanceRatios,
    file: "policy/Alt_FiscalStanceRatios.astro",
    title: "Fiscal stance ratios: general-government balance and gross debt to GDP",
    whatDifferent:
      "Two-panel composite: left panel shows general-government net lending/borrowing (flow) as % GDP; right panel shows general-government gross debt (stock) as % GDP. Both panels carry 1980-2024 observed (solid) + 2025-2031 IMF WEO projections (dashed). MTA red dot at the last observed point (2024) in each panel. Zero line in the balance panel.",
    whyBetter:
      "Production policy section carries no fiscal panel. The balance-and-debt pair is the canonical fiscal-stance read: balance shows the flow, debt shows the stock trajectory. The dashed projection extension makes the IMF's forward outlook legible without a separate chart.",
    dataFields: "imf_can_gg_balance_pct_gdp + imf_can_gg_gross_debt_pct_gdp (IMF WEO).",
    addedAt: "2026-05-14",
  },
  {
    Component: Alt2_BalanceSheetOverlay,
    file: "policy/Alt2_BalanceSheetOverlay.astro",
    title: "BoC total assets and settlement balances, side-by-side",
    whatDifferent:
      "Small multiples: total assets path and settlement balances path each in their own frame.",
    whyBetter:
      "A one-axis dual overlay is misleading; the two move on related but different mechanisms.",
    dataFields:
      "boc_total_assets.csv + boc_settlement_balances.csv",
    addedAt: "2026-05-12",
  },
  {
    Component: Alt3_YieldCurveTriple,
    file: "policy/Alt3_YieldCurveTriple.astro",
    title: "GoC 2y / 5y / 10y overlay",
    whatDifferent:
      "Three yield curves on shared % axis: 2y primary, 5y secondary dashed, 10y tertiary sparse-dashed. The morning desk read.",
    whyBetter:
      "Curve shape and parallel shifts both visible. Production Panel 2 pairs 2y with overnight only.",
    dataFields: "yield_2yr.csv + yield_5yr.csv + yield_10yr.csv",
    addedAt: "2026-05-12",
  },
  {
    Component: Alt4_TwosTensSlope,
    file: "policy/Alt4_TwosTensSlope.astro",
    title: "GoC 2s10s slope",
    whatDifferent:
      "10y minus 2y as a single line with zero (inversion) line. The canonical recession-signal chart.",
    whyBetter:
      "Slope is the diagnostic; the level chart (Alt 3) shows context, this one tells the story.",
    dataFields: "yield_10yr.csv - yield_2yr.csv",
    addedAt: "2026-05-12",
  },
];
