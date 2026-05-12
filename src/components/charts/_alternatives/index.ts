/*
 * _alternatives/index.ts — aggregate manifest of every chart-alternative
 * section, in chart-alternatives page order.
 *
 * The /chart-alternatives page imports `shelves` from here, iterates,
 * and renders every section. Adding a new section means: create
 * _alternatives/<section>/index.ts, then add one entry below.
 *
 * The display order intentionally matches the prior hand-wired sections
 * array on chart-alternatives.astro so the post-refactor page reads
 * identically.
 */

import type { ChartShelfEntry } from "./_shared/shelfEntry";

import { entries as gdpEntries } from "./gdp/index";
import { entries as inflationEntries } from "./inflation/index";
import { entries as labourEntries } from "./labour/index";
import { entries as policyEntries } from "./policy/index";
import { entries as marketsEntries } from "./markets/index";
import { entries as tradeEntries } from "./trade/index";
import { entries as housingEntries } from "./housing/index";

export interface Shelf {
  slug: string;
  name: string;
  entries: ChartShelfEntry[];
}

export const shelves: Shelf[] = [
  { slug: "gdp", name: "Output", entries: gdpEntries },
  { slug: "inflation", name: "Inflation", entries: inflationEntries },
  { slug: "labour", name: "Labour", entries: labourEntries },
  { slug: "policy", name: "Policy", entries: policyEntries },
  { slug: "markets", name: "Markets", entries: marketsEntries },
  { slug: "trade", name: "Trade", entries: tradeEntries },
  { slug: "housing", name: "Housing", entries: housingEntries },
];
