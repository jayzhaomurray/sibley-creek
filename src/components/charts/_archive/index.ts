/*
 * _archive/index.ts — aggregate manifest of every chart-archive section,
 * in chart-archive page order. Mirrors _alternatives/index.ts.
 *
 * Each section's entries flow into two zones on /chart-archive:
 *   - Pinned (pinned: true) — rendered first.
 *   - Archive (the rest)    — rendered after.
 * Within each zone, entries sort by addedAt desc when set, else by title.
 */

import type { ChartShelfEntry } from "../_alternatives/_shared/shelfEntry";

import { entries as gdpEntries } from "./gdp/index";
import { entries as inflationEntries } from "./inflation/index";
import { entries as labourEntries } from "./labour/index";
import { entries as policyEntries } from "./policy/index";
import { entries as marketsEntries } from "./markets/index";
import { entries as tradeEntries } from "./trade/index";
import { entries as housingEntries } from "./housing/index";

export interface ArchiveShelf {
  slug: string;
  name: string;
  entries: ChartShelfEntry[];
}

export const shelves: ArchiveShelf[] = [
  { slug: "gdp", name: "Output", entries: gdpEntries },
  { slug: "inflation", name: "Inflation", entries: inflationEntries },
  { slug: "labour", name: "Labour", entries: labourEntries },
  { slug: "policy", name: "Policy", entries: policyEntries },
  { slug: "markets", name: "Markets", entries: marketsEntries },
  { slug: "trade", name: "Trade", entries: tradeEntries },
  { slug: "housing", name: "Housing", entries: housingEntries },
];
