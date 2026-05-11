/*
 * Site sections — the top-level navigation and homepage tile content.
 *
 * OWNER: editorial-director owns slug / label / kicker / cadence /
 * headlineQuestion. writer + style-editor own blurb prose. Section accent
 * tokens are owned by art-director (declared in src/styles/tokens.css).
 *
 * Frontend reads this; do not bake section identity into nav markup.
 *
 * Shape:
 *   slug              - URL fragment under "/", lowercase, no spaces. ASCII only.
 *   label             - Short display label in the primary nav. EN-CA, title case.
 *   tileLabel         - The display name on the homepage tile header. Usually
 *                       the same as `label` but allowed to differ (e.g., Labour
 *                       drops the "and Demographics" tail in the tile header
 *                       to keep the row scannable).
 *   accentVar         - CSS variable name for the section accent. The tile and
 *                       any per-section chrome consume this token; the value
 *                       lives in tokens.css. Stored as the unwrapped name so
 *                       components can wrap it as `var(--...)` once.
 *   kicker            - One-line description for nav menus, sitemap, etc.
 *   headlineQuestion  - The section's load-bearing question, per
 *                       editorial/dashboard_purpose.md sec 4. Rendered as
 *                       the tile deck (serif italic, one line on desktop).
 *   cadence           - Short string for the "As of [date] . [cadence]" tile
 *                       footer line (per editorial/dashboard_purpose.md sec 6).
 *   prints            - 2-3 most load-bearing prints surfaced on the tile.
 *                       Placeholder values for v1; backend pipeline replaces
 *                       these at build time once the data layer lands.
 *   blurb             - The event note slot at the bottom of the tile.
 *                       `kind: "fresh"` -> accent kicker, full readability.
 *                       `kind: "last"`  -> ink-faint kicker, muted treatment.
 *                       `kind: "none"`  -> the slot is reserved but empty
 *                                          (no blurb has ever been written
 *                                          for this section). v1 should not
 *                                          ship this state — every section
 *                                          has at least a last note.
 *
 * NOTE on placeholder values: prints, blurbs, and deep dives below are
 * placeholders sourced from the art-director's R1 ASCII mockup. They will
 * be wired through the backend pipeline (prints) and the writer/
 * editorial-director (blurbs, deep-dive titles) in subsequent passes.
 */

export type SectionSlug =
  | "gdp"
  | "inflation"
  | "labour"
  | "housing"
  | "policy"
  | "markets"
  | "trade";

export interface SectionPrint {
  /**
   * Optional stable key for this print, used to identify the load-bearing
   * series when a downstream consumer (e.g. the homepage hero chart) needs
   * to pick one print from `prints[]` without depending on array order.
   * Conventional values: "cpi-yoy", "gdp-mm", "unrate", "policy-rate", etc.
   * Free-form; the section's `chartSeriesKey` matches against this. If
   * omitted on every print, hero fallback is `prints[0]`.
   */
  key?: string;
  /** Indicator name, e.g. "Real GDP, m/m". */
  indicator: string;
  /** Display value, pre-formatted. e.g. "+0.2%". */
  value: string;
  /** Delta vs prior period, pre-formatted. e.g. "-0.1 pp". */
  delta: string;
  /** Direction the delta represents — drives semantic color on the delta. */
  deltaDir: "pos" | "neg" | "neutral";
  /** Short "as of" stamp, e.g. "Feb 2026". */
  asOf: string;
  /**
   * Sparkline series — oldest-to-newest, ~20-30 numeric points in the
   * indicator's native units. The component (src/components/Sparkline.astro)
   * normalizes to its own min/max, so absolute scale here is informational
   * only (a future backend pipeline may use it for tooltips).
   *
   * v1 carries placeholder shapes that loosely match the delta direction;
   * backend-engineer will replace these with real series from the data
   * pipeline. The last value of `spark` should equal the numeric content
   * of `value` once wired through real data.
   */
  spark?: number[];
}

export interface SectionBlurb {
  kind: "fresh" | "last" | "none";
  /** Display date, e.g. "Apr 16, 2026". */
  date?: string;
  /** Blurb body — 2-3 sentences. Plain text in v1. */
  body?: string;
}

export interface Section {
  slug: SectionSlug;
  label: string;
  tileLabel?: string;
  accentVar: string;
  kicker?: string;
  headlineQuestion: string;
  cadence: string;
  prints: SectionPrint[];
  blurb: SectionBlurb;
  /**
   * Epoch milliseconds for the section's most-recently-updated print or
   * event. Drives the homepage hero selection (Layout B): the section with
   * the maximum `updatedAt` value is rendered as the hero; the rest fall
   * into the compressed 6-grid. Placeholder values for v1 — backend will
   * derive these from release-calendar landings (e.g. CPI on CPI day flips
   * Inflation to the top; rate-decision day flips Policy; etc.). The
   * homepage computes `Math.max(...sections.map(s => s.updatedAt))` at
   * build time; rotation is automatic as values change.
   */
  updatedAt: number;
  /**
   * Key into this section's `prints[]` identifying the load-bearing time
   * series for the homepage hero chart. The hero only renders ONE chart;
   * this tells it which series to use. Examples per section:
   *   inflation: "cpi-yoy"        (headline CPI YoY)
   *   gdp:       "gdp-mm"         (Real GDP m/m)
   *   labour:    "unrate"         (Unemployment rate)
   *   policy:    "policy-rate"    (BoC overnight rate path)
   *   housing:   "hpi-yoy"
   *   markets:   "usdcad"
   *   trade:     "trade-balance"
   * Resolution: scan `prints[]` for the entry whose `key` matches; if no
   * match, fall back to `prints[0]`.
   */
  chartSeriesKey?: string;
  /**
   * Hero eyebrow kicker — the right-hand side of the "SECTION | KICKER" rail
   * at the top of the homepage hero tile. Should name the specific recent
   * release or event (e.g. "APRIL CPI", "Q4 2025 GDP", "APRIL RATE
   * DECISION"), not refresh-light metadata ("MOST RECENT UPDATE").
   *
   * Art-director re-eval (2026-05-11) item 3: replaced the hardcoded "MOST
   * RECENT UPDATE" string with a content-noun pattern that is data-driven
   * per section. Backend pipeline can keep this current alongside
   * `updatedAt` as new prints land. v1 placeholders match the latest
   * release in each section.
   *
   * Rendered in all-caps via CSS; supply the source string in title-ish
   * mixed case ("April CPI") so a future bilingual variant can keep its
   * casing. CSS does the `text-transform: uppercase` on render.
   */
  heroKicker?: string;
  /**
   * Homepage compact (index) tile's editorial line.
   *
   * STATUS (2026-05-11): NOT CURRENTLY READ. Path C reversal removed the
   * editorial-line slot from CompactTile; the tile now renders the load-
   * bearing print's `indicator` field (e.g. "Headline CPI, y/y") in that
   * slot instead of a sentence. The field is retained on the Section type
   * so the data shape stays stable (and so writer/style-editor work
   * already done isn't lost) but is ignored at render. If a later
   * editorial direction reinstates a tile-level sentence, this is the
   * field to wire back in.
   *
   * Historical: one sentence, ~12-16 words, body-sm Inter weight 500,
   * clamped to 2 lines. Authored by writer + style-editor.
   */
  tileLine?: string;
}

export const sections: Section[] = [
  {
    slug: "gdp",
    label: "GDP",
    accentVar: "--section-accent-gdp",
    kicker: "Output, expenditure, and the quarterly arithmetic of growth.",
    headlineQuestion:
      "Is the Canadian economy at potential, growing, or contracting?",
    cadence: "Monthly + quarterly",
    // Most recent monthly GDP print landed May 1, 2026 (StatCan ~60d lag).
    updatedAt: Date.UTC(2026, 4, 1, 8, 30),
    chartSeriesKey: "gdp-yoy",
    heroKicker: "February GDP",
    tileLine:
      "February GDP came in soft on goods-producing industries; services held up.",
    prints: [
      {
        // Real GDP y/y is the load-bearing print — first row, matches the
        // pipeline output (key gdp-yoy) so the loader enriches it in place.
        key: "gdp-yoy",
        indicator: "Real GDP, y/y",
        value: "TK",
        delta: "TK",
        deltaDir: "neutral",
        asOf: "TK",
      spark: [],
      },
      {
        key: "gdp-mm",
        indicator: "Real GDP, m/m",
        value: "TK",
        delta: "TK",
        deltaDir: "neutral",
        asOf: "TK",
      spark: [],
      },
      {
        key: "gdp-percap-yoy",
        indicator: "Per-capita GDP, y/y",
        value: "TK",
        delta: "TK",
        deltaDir: "neutral",
        asOf: "TK",
      spark: [],
      },
      {
        key: "output-gap",
        indicator: "Output gap",
        value: "TK",
        delta: "TK",
        deltaDir: "neutral",
        asOf: "TK",
      spark: [],
      },
    ],
    blurb: {
      kind: "last",
      date: "Mar 28, 2026",
      body:
        "February's monthly GDP came in soft on goods-producing industries; services held. The output gap is closing more slowly than the BoC's April MPR projected, but the per-capita series remains the harder read.",
    },
  },
  {
    slug: "inflation",
    label: "Inflation",
    accentVar: "--section-accent-inflation",
    kicker: "Headline, core, and the breadth of price pressure.",
    headlineQuestion:
      "Is the 2% target being met, and on what measures and what breadth?",
    cadence: "Monthly",
    // Most recent CPI print landed May 14, 2026 (April 2026 release). This
    // is currently the freshest section on the page; the homepage hero
    // selection picks it up automatically.
    updatedAt: Date.UTC(2026, 4, 14, 8, 30),
    chartSeriesKey: "cpi-yoy",
    heroKicker: "April CPI",
    tileLine:
      "Headline CPI ticked up to 2.3% in April, shelter still doing the work.",
    prints: [
      {
        // The pipeline produces a real value for this row (data/site/sections.json:
        // headline CPI y/y, currently 2.3% as of Mar 2026). The fields below are
        // canon scaffold defaults that the loader overwrites with pipeline data
        // before render — TK markers here are visible only when the pipeline
        // payload is unavailable.
        key: "cpi-yoy",
        indicator: "Headline CPI, y/y",
        value: "TK",
        delta: "TK",
        deltaDir: "neutral",
        asOf: "TK",
      spark: [],
      },
      {
        key: "core-trim-yoy",
        indicator: "Core-trim, y/y",
        value: "TK",
        delta: "TK",
        deltaDir: "neutral",
        asOf: "TK",
      spark: [],
      },
      {
        key: "core-median-yoy",
        indicator: "Core-median, y/y",
        value: "TK",
        delta: "TK",
        deltaDir: "neutral",
        asOf: "TK",
      spark: [],
      },
      {
        key: "cpi-breadth-gt3",
        indicator: "CPI breadth >3%",
        value: "TK",
        delta: "TK",
        deltaDir: "neutral",
        asOf: "TK",
      spark: [],
      },
    ],
    blurb: {
      kind: "fresh",
      date: "May 14, 2026",
      body:
        "April CPI surprised the consensus to the upside by a tenth, but the BoC's preferred cores eased again on a 3-month annualized basis. Shelter is still doing most of the work, with mortgage interest cost the largest single contributor.",
    },
  },
  {
    slug: "labour",
    // Renamed from "Labour and Demographics" to "Labour" per art-director's
    // F8 fix. Canon agrees: no Demographics subheading on the nav. The tile
    // header followed the same shortening, so `tileLabel` is now redundant
    // and dropped.
    label: "Labour",
    accentVar: "--section-accent-labour",
    kicker: "Jobs, wages, participation, and the workforce that backs them.",
    headlineQuestion:
      "How tight is the labour market, and is per-capita output recovering?",
    cadence: "Monthly",
    // Most recent LFS landed May 2, 2026 (April 2026 reference period).
    updatedAt: Date.UTC(2026, 4, 2, 8, 30),
    chartSeriesKey: "unrate",
    heroKicker: "April LFS",
    tileLine:
      "April employment softened against consensus; unemployment held at 6.1% as participation slipped.",
    prints: [
      {
        // Pipeline produces a real value for this row (unemployment rate,
        // currently 6.9% Apr 2026); loader overwrites canon scaffold with
        // real data before render. TK is a fallback marker.
        key: "unrate",
        indicator: "Unemployment rate",
        value: "TK",
        delta: "TK",
        deltaDir: "neutral",
        asOf: "TK",
      spark: [],
      },
      {
        key: "emp-percap-yoy",
        indicator: "Per-capita employment, y/y",
        value: "TK",
        delta: "TK",
        deltaDir: "neutral",
        asOf: "TK",
      spark: [],
      },
      {
        key: "agg-hours-yoy",
        indicator: "Aggregate hours, y/y",
        value: "TK",
        delta: "TK",
        deltaDir: "neutral",
        asOf: "TK",
      spark: [],
      },
      {
        key: "wage-lfs-micro",
        indicator: "Wage growth (LFS-Micro)",
        value: "TK",
        delta: "TK",
        deltaDir: "neutral",
        asOf: "TK",
      spark: [],
      },
    ],
    blurb: {
      kind: "last",
      date: "May 2, 2026",
      body:
        "April's LFS came in soft on employment but the unemployment rate held flat as participation slipped. The per-capita employment story keeps drifting; the IRCC plan vintage matters here more than the headline.",
    },
  },
  {
    slug: "policy",
    label: "Policy",
    accentVar: "--section-accent-policy",
    kicker: "The Bank of Canada and the federal fiscal stance.",
    headlineQuestion:
      "What is the policy stance, and is it consistent with the cycle?",
    cadence: "Event-driven + monthly",
    // BoC-Fed spread refreshes daily (May 9, 2026); rate decision was
    // Apr 29. Use the later of the two as the stamp.
    updatedAt: Date.UTC(2026, 4, 9, 14, 0),
    chartSeriesKey: "policy-rate",
    heroKicker: "April rate decision",
    tileLine:
      "BoC cut 25 bps to 2.75% and dropped the line about needing more evidence on services inflation.",
    prints: [
      {
        // Pipeline produces a real value for this row (BoC overnight rate,
        // currently 2.25% Apr 2026); loader overwrites canon scaffold with
        // real data before render. TK is a fallback marker.
        key: "policy-rate",
        indicator: "BoC overnight rate",
        value: "TK",
        delta: "TK",
        deltaDir: "neutral",
        asOf: "TK",
      spark: [],
      },
      {
        key: "goc-2y",
        indicator: "2y GoC yield",
        value: "TK",
        delta: "TK",
        deltaDir: "neutral",
        asOf: "TK",
      spark: [],
      },
      {
        key: "boc-fed-spread",
        indicator: "BoC-Fed spread, 2y",
        value: "TK",
        delta: "TK",
        deltaDir: "neutral",
        asOf: "TK",
      spark: [],
      },
      {
        key: "federal-budget-balance",
        indicator: "Federal budget balance",
        value: "TK",
        delta: "TK",
        deltaDir: "neutral",
        asOf: "TK",
      spark: [],
      },
    ],
    blurb: {
      kind: "fresh",
      date: "Apr 29, 2026",
      body:
        "The Bank cut 25 bps as expected and dropped the line about needing more evidence on services inflation. The MPR's neutral-rate refresh ticked the midpoint down by ten basis points; the press conference leaned into the per-capita weakness more than the inflation print.",
    },
  },
  {
    /*
     * Slug is "markets" (route: /markets/). The section was previously named
     * "Financial Conditions" / "Financial"; editorial scope is unchanged
     * (CAD, yields, spreads, cross-asset) — only the label and slug
     * changed. Accent token renamed accordingly in styles/tokens.css.
     */
    slug: "markets",
    label: "Markets",
    tileLabel: "Markets",
    accentVar: "--section-accent-markets",
    kicker: "Yields, spreads, the loonie, and the cost of capital.",
    headlineQuestion:
      "What external winds are pushing on Canadian inflation, growth, and the CAD?",
    cadence: "Daily (light) + weekly synthesis",
    // Markets data refreshes daily; latest stamp May 9, 2026.
    updatedAt: Date.UTC(2026, 4, 9, 21, 0),
    chartSeriesKey: "usdcad",
    heroKicker: "Weekly close",
    tileLine:
      "USDCAD pushed to 1.378 on the week as the BoC-Fed spread ground wider on divergent paths.",
    prints: [
      {
        // Pipeline produces a real value for this row (USDCAD, currently 1.369
        // May 8, 2026); loader overwrites canon scaffold with real data before
        // render. TK is a fallback marker.
        key: "usdcad",
        indicator: "USDCAD",
        value: "TK",
        delta: "TK",
        deltaDir: "neutral",
        asOf: "TK",
      spark: [],
      },
      {
        key: "goc-10y",
        indicator: "10y GoC yield",
        value: "TK",
        delta: "TK",
        deltaDir: "neutral",
        asOf: "TK",
      spark: [],
      },
      {
        key: "tsx-composite",
        indicator: "TSX Composite",
        value: "TK",
        delta: "TK",
        deltaDir: "neutral",
        asOf: "TK",
      spark: [],
      },
      {
        key: "wti",
        indicator: "WTI",
        value: "TK",
        delta: "TK",
        deltaDir: "neutral",
        asOf: "TK",
      spark: [],
      },
    ],
    blurb: {
      kind: "last",
      date: "May 3, 2026",
      body:
        "USDCAD is sitting at the 80th percentile of the post-1990 distribution; not stress yet, but no longer benign. GoC-UST 10y spread continues to grind wider on the BoC-Fed divergence and term premium has done some of the work.",
    },
  },
  {
    slug: "trade",
    label: "Trade",
    accentVar: "--section-accent-trade",
    kicker: "Exports, imports, and the terms by which Canada sells its work.",
    headlineQuestion:
      "Is Canada's external position structurally shifting under US repricing?",
    cadence: "Monthly + event",
    // March merch-trade release landed Apr 3, 2026.
    updatedAt: Date.UTC(2026, 3, 3, 8, 30),
    chartSeriesKey: "trade-balance",
    heroKicker: "March balance",
    tileLine:
      "March merch trade balance widened to -$2.3B, with auto and energy pulling in opposite directions.",
    prints: [
      {
        key: "trade-balance",
        indicator: "Goods trade balance",
        value: "TK",
        delta: "TK",
        deltaDir: "neutral",
        asOf: "TK",
      spark: [],
      },
      {
        key: "current-account",
        indicator: "Current account",
        value: "TK",
        delta: "TK",
        deltaDir: "neutral",
        asOf: "TK",
      spark: [],
      },
      {
        key: "us-partner-share",
        indicator: "US partner share",
        value: "TK",
        delta: "TK",
        deltaDir: "neutral",
        asOf: "TK",
      spark: [],
      },
      {
        key: "terms-of-trade",
        indicator: "Terms of trade",
        value: "TK",
        delta: "TK",
        deltaDir: "neutral",
        asOf: "TK",
      spark: [],
      },
    ],
    blurb: {
      kind: "last",
      date: "Apr 3, 2026",
      body:
        "Auto and energy carried the March print on opposite shoulders. The US share keeps drifting, but the Section 232 follow-on actions named in March are the variable that matters into the summer USMCA review window.",
    },
  },
  {
    slug: "housing",
    label: "Housing",
    accentVar: "--section-accent-housing",
    kicker: "Starts, sales, prices, and household leverage.",
    headlineQuestion:
      "Is the rate-sensitive sector amplifying or dampening policy?",
    cadence: "Monthly",
    // CREA April release lands mid-month; placeholder Apr 15, 2026.
    updatedAt: Date.UTC(2026, 3, 15, 9, 0),
    chartSeriesKey: "hpi-yoy",
    heroKicker: "April MLS HPI",
    tileLine:
      "Composite HPI slipped further into negative territory, Toronto and Vancouver leading the drift.",
    prints: [
      {
        key: "hpi-yoy",
        indicator: "MLS HPI, y/y",
        value: "TK",
        delta: "TK",
        deltaDir: "neutral",
        asOf: "TK",
      spark: [],
      },
      {
        key: "housing-starts-3mma",
        indicator: "Housing starts, 3mma",
        value: "TK",
        delta: "TK",
        deltaDir: "neutral",
        asOf: "TK",
      spark: [],
      },
      {
        key: "cmhc-arrears",
        indicator: "CMHC arrears rate",
        value: "TK",
        delta: "TK",
        deltaDir: "neutral",
        asOf: "TK",
      spark: [],
      },
      {
        key: "months-inventory",
        indicator: "Months of inventory",
        value: "TK",
        delta: "TK",
        deltaDir: "neutral",
        asOf: "TK",
      spark: [],
      },
    ],
    blurb: {
      kind: "last",
      date: "Apr 15, 2026",
      body:
        "Toronto and Vancouver kept loosening into the spring market; Calgary held firm. The renewal cohort that prints over the summer is the one to watch, and we still expect the residual transmission to land mostly through consumption.",
    },
  },
];

/*
 * Deep-dive registry — the "Current Deep Dives" strip on the homepage.
 *
 * OWNER: editorial-director owns home-section assignment and status;
 * writer owns title + deck. Pillar codes A-H are inherited from the editorial
 * canon (editorial/dashboard_purpose.md sec 5). Status values match the
 * editorial workflow: research -> drafted -> shipped.
 *
 * Homepage surfaces up to three at a time, ordered by recency of last
 * update. Anything beyond three lives on a future /deep-dives/ index.
 */

/**
 * Legacy enum kept for experiments only. Production does not render status;
 * the deep-dive lifecycle states are not surfaced to readers.
 */
export type DeepDiveStatus = "research" | "drafted" | "shipped";

export interface DeepDive {
  /** URL slug for /research/<slug>/. Lowercase, hyphenated, no trailing slash. */
  slug: string;
  /** Home section slug — used for section badge / grouping. */
  section: SectionSlug;
  /** Short title, set as display Manrope 800. */
  title: string;
  /** One-sentence deck; sub-display Manrope 200. */
  deck: string;
  /** ISO date string (YYYY-MM-DD) for sort + display. */
  publishedAt?: string;
  /** Display string for the "Updated" stamp. */
  lastUpdated: string;
  /**
   * Writer's working markdown body under `editorial/drafts/`. NOT rendered
   * on the public site — this is the scratchpad with TKs, voice notes,
   * and unresolved fact-check items.
   */
  draftPath?: string;
  /**
   * Publication-ready markdown body under `editorial/published/`. THIS is
   * what /research/<slug>/ renders. Set only after the piece has cleared
   * fact-check + style-edit. Entries with no `publishedPath` are filtered
   * out of getStaticPaths — no slug route is built, no public URL exists.
   */
  publishedPath?: string;
  /** Resolved destination; computed from slug when omitted. */
  href?: string;
  /**
   * @deprecated Editorial canon pillar letter (A-H). Not surfaced in
   * production — letters were judged meaningless to the reader. Kept
   * optional on the type so legacy /experiments/* renders don't break.
   */
  pillar?: string;
  /**
   * @deprecated Lifecycle status (research / drafted / shipped). Not
   * surfaced in production. Kept optional on the type so legacy
   * /experiments/* renders don't break.
   */
  status?: DeepDiveStatus;
}

export const deepDives: DeepDive[] = [
  {
    slug: "mortgage-renewal-wall",
    section: "housing",
    title: "Mortgage renewal wall: has it peaked?",
    deck:
      "The 2026 renewal cohort is the largest single tranche in the stack. We map where the residual transmission lands through 2027.",
    publishedAt: "2026-05-11",
    lastUpdated: "TK",
    draftPath: "editorial/drafts/deepdive_pillar_a_mortgage_renewal_wall_v1.md",
    // Legacy fields retained so /experiments/* keeps building. Not rendered in production.
    pillar: "A",
    status: "drafted",
  },
  {
    slug: "boc-fed-divergence",
    section: "policy",
    title: "BoC vs. Fed: how far can the divergence run?",
    deck:
      "TK basis points and counting. We trace the CAD, GoC curve, and credit channels that would force a back-off, and where the breakpoints sit.",
    publishedAt: "TK",
    lastUpdated: "TK",
    pillar: "B",
    status: "shipped",
  },
  {
    slug: "per-capita-output",
    section: "labour",
    title: "Per-capita output: deceleration or weakness?",
    deck:
      "The headline labour print is flattering. The per-capita series is not. We separate the population-deceleration story from the cyclical weakness story.",
    publishedAt: "TK",
    lastUpdated: "TK",
    pillar: "E",
    status: "research",
  },
];

/*
 * Next-release indicator for the homepage date strip.
 * OWNER: backend pipeline will derive this from the Canadian release
 * calendar at build time. v1 placeholder values per the May 2026 calendar
 * in editorial/dashboard_purpose.md sec 6.
 */
export const nextRelease = {
  label: "TK",
  date: "TK",
  agency: "Statistics Canada",
};

/*
 * Site-level metadata. Used by BaseLayout and SEO tags. Edit by
 * editorial-director / art-director as the brand crystallizes.
 */
export const site = {
  // Publication brand. Folder/path name (macro-research-department) is the
  // project slug on disk and stays as-is; only the human-facing brand name
  // changed in the 2026-05-11 rename pass. Wordmark renders all-caps via CSS
  // (text-transform: uppercase); keep the source string in title case.
  name: "Sibley Creek",
  shortName: "Sibley Creek",
  // F7 (art-director): the previous italic tagline competed with the wordmark
  // and the section names. Replaced with a short all-caps label rail; the
  // wordmark below renders it in label-sized sans with letter-spacing so it
  // reads as a category line, not a slogan. Rebrand pass shortened the
  // tagline to "Canadian macro" - confident, label-sized.
  tagline: "Canadian macro",
  description:
    "Sibley Creek - Canadian macroeconomic indicators and analysis. A reading-first dashboard for analysts, policymakers, and serious citizens.",
  locale: "en-CA",
  url: "https://example.invalid",
};
