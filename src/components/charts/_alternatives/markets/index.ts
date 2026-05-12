/*
 * _alternatives/markets/index.ts — chart-alternatives manifest for the
 * Markets section. See _alternatives/gdp/index.ts for the pattern.
 */

import type { ChartShelfEntry } from "../_shared/shelfEntry";

import Alt1_GoCUstSpread from "./Alt1_GoCUstSpread.astro";
import Alt2_OilTriple from "./Alt2_OilTriple.astro";
import Alt3_WcsDiscount from "./Alt3_WcsDiscount.astro";
import Alt4_UsdCadVsBocFed from "./Alt4_UsdCadVsBocFed.astro";

export const entries: ChartShelfEntry[] = [
  {
    Component: Alt1_GoCUstSpread,
    file: "markets/Alt1_GoCUstSpread.astro",
    title: "GoC 2y minus UST 2y",
    whatDifferent: "Front-end basis to US. Single zero-crossing line.",
    whyBetter:
      "The basis trades, not the rate. Negative basis = Canada-rich; widening = policy divergence.",
    dataFields: "yield_2yr.csv - us_2yr.csv",
    addedAt: "2026-05-12",
  },
  {
    Component: Alt2_OilTriple,
    file: "markets/Alt2_OilTriple.astro",
    title: "WTI + Brent + WCS triple",
    whatDifferent:
      "Adds Western Canadian Select (heavy crude) to the WTI-Brent pair from production Panel 4.",
    whyBetter:
      "WCS is the Canadian price; the WCS-WTI gap drives Alberta capex and federal royalties.",
    dataFields: "wti.csv + brent.csv + wcs.csv",
    addedAt: "2026-05-12",
  },
  {
    Component: Alt3_WcsDiscount,
    file: "markets/Alt3_WcsDiscount.astro",
    title: "WCS-WTI differential",
    whatDifferent:
      "Single line: WTI minus WCS. The Alberta wellhead-realization story.",
    whyBetter:
      "Wide differential = pipeline constraints; tight = relief. One line, one signal.",
    dataFields: "wti.csv - wcs.csv",
    addedAt: "2026-05-12",
  },
  {
    Component: Alt4_UsdCadVsBocFed,
    file: "markets/Alt4_UsdCadVsBocFed.astro",
    title: "USDCAD vs GoC2-UST2, side-by-side",
    whatDifferent:
      "Small multiples since units differ (price vs %). The policy-driven FX story in one visual scan.",
    whyBetter:
      "The whole loonie story since 2022 is the BoC-Fed rate gap. Side-by-side avoids the dual-unit trap.",
    dataFields: "usdcad.csv + (yield_2yr.csv - us_2yr.csv)",
    addedAt: "2026-05-12",
  },
];
