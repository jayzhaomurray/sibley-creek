/*
 * Site sections — the top-level navigation.
 *
 * OWNER: editorial-director. This is the section list that drives the
 * primary nav (and eventually section index pages). Edit freely.
 *
 * Frontend reads this; do not bake section identity into nav markup.
 *
 * The placeholders below are the leading working hypothesis as of
 * 2026-05-10. Treat them as draft until editorial-director confirms.
 *
 * Shape:
 *   slug   - URL fragment under "/", lowercase, no spaces. ASCII only.
 *   label  - Display label in the nav. EN-CA. Title case.
 *   kicker - Optional one-line description; not currently rendered in
 *            primary nav but used on the homepage section grid and on
 *            section index pages.
 */

export interface Section {
  slug: string;
  label: string;
  kicker?: string;
}

export const sections: Section[] = [
  {
    slug: "gdp",
    label: "GDP",
    kicker: "Output, expenditure, and the quarterly arithmetic of growth.",
  },
  {
    slug: "inflation",
    label: "Inflation",
    kicker: "Headline, core, and the breadth of price pressure.",
  },
  {
    slug: "labour",
    label: "Labour and Demographics",
    kicker: "Jobs, wages, participation, and the workforce that backs them.",
  },
  {
    slug: "housing",
    label: "Housing",
    kicker: "Starts, sales, prices, and household leverage.",
  },
  {
    slug: "policy",
    label: "Policy",
    kicker: "The Bank of Canada, the federal fiscal stance, and what they signal.",
  },
  {
    slug: "financial",
    label: "Financial Conditions",
    kicker: "Yields, spreads, the loonie, and the cost of capital.",
  },
  {
    slug: "trade",
    label: "Trade",
    kicker: "Exports, imports, and the terms by which Canada sells its work.",
  },
];

/*
 * Site-level metadata. Used by BaseLayout and SEO tags. Edit by
 * editorial-director / art-director as the brand crystallizes.
 */
export const site = {
  name: "Macro Research Department",
  shortName: "MRD",
  tagline: "Canadian macroeconomic research, set with care.",
  description:
    "A reading-first dashboard for Canadian macroeconomic indicators. Written for analysts, policymakers, and serious citizens.",
  locale: "en-CA",
  url: "https://example.invalid",
};
