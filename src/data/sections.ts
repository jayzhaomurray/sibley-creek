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
    chartSeriesKey: "gdp-mm",
    heroKicker: "February GDP",
    tileLine:
      "February GDP came in soft on goods-producing industries; services held up.",
    prints: [
      {
        key: "gdp-mm",
        indicator: "Real GDP, m/m",
        value: "+0.2%",
        delta: "-0.1 pp",
        deltaDir: "neg",
        asOf: "Feb 2026",
        // m/m % change — wobbling around zero with a recent soft tilt.
        spark: [
          0.4, 0.3, 0.5, 0.2, 0.1, 0.3, 0.4, 0.2, 0.5, 0.3, 0.1, 0.0,
          0.2, 0.4, 0.3, 0.1, 0.2, 0.4, 0.5, 0.3, 0.4, 0.3, 0.3, 0.2,
        ],
      },
      {
        indicator: "Real GDP, q/q SAAR",
        value: "1.4%",
        delta: "-0.3 pp",
        deltaDir: "neg",
        asOf: "2026Q1",
        // Quarterly SAAR — fewer points (8 quarters) to read as quarterly.
        spark: [3.1, 2.7, 2.2, 1.9, 2.4, 2.1, 1.7, 1.4],
      },
      {
        indicator: "Output gap",
        value: "-0.6%",
        delta: "+0.1 pp",
        deltaDir: "pos",
        asOf: "2026Q1",
        // Output gap closing slowly from a deeper trough.
        spark: [
          -1.4, -1.5, -1.4, -1.3, -1.2, -1.1, -1.0, -1.1, -1.0, -0.9, -0.8, -0.9,
          -0.8, -0.7, -0.8, -0.7, -0.7, -0.6,
        ],
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
        key: "cpi-yoy",
        indicator: "Headline CPI, y/y",
        value: "2.3%",
        delta: "+0.1 pp",
        deltaDir: "neutral",
        asOf: "Apr 2026",
        // y/y % — sliding down off a higher plateau toward the 2% target.
        spark: [
          3.6, 3.5, 3.4, 3.1, 2.9, 2.8, 2.7, 2.9, 2.7, 2.6, 2.5, 2.6,
          2.4, 2.3, 2.2, 2.1, 2.0, 2.1, 2.2, 2.1, 2.2, 2.3, 2.2, 2.3,
        ],
      },
      {
        indicator: "Core-trim, y/y",
        value: "2.6%",
        delta: "-0.1 pp",
        deltaDir: "pos",
        asOf: "Apr 2026",
        // Core measures slower to ease but still trending down.
        spark: [
          3.7, 3.6, 3.6, 3.5, 3.4, 3.3, 3.2, 3.2, 3.0, 3.0, 2.9, 2.9,
          2.8, 2.8, 2.7, 2.7, 2.7, 2.7, 2.7, 2.7, 2.7, 2.7, 2.6, 2.6,
        ],
      },
      {
        indicator: "Core-median, y/y",
        value: "2.5%",
        delta: "0.0 pp",
        deltaDir: "neutral",
        asOf: "Apr 2026",
        spark: [
          3.5, 3.4, 3.4, 3.3, 3.2, 3.2, 3.1, 3.0, 3.0, 2.9, 2.9, 2.8,
          2.7, 2.7, 2.6, 2.6, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5,
        ],
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
        key: "unrate",
        indicator: "Unemployment rate",
        value: "6.1%",
        delta: "0.0 pp",
        deltaDir: "neutral",
        asOf: "Apr 2026",
        // U-rate rising slowly off the trough, recently flattening.
        spark: [
          5.0, 5.1, 5.1, 5.2, 5.3, 5.3, 5.4, 5.5, 5.6, 5.6, 5.7, 5.8,
          5.8, 5.9, 5.9, 6.0, 6.0, 6.0, 6.1, 6.1, 6.0, 6.1, 6.1, 6.1,
        ],
      },
      {
        indicator: "Employment, m/m",
        value: "+12k",
        delta: "vs +25k cons.",
        deltaDir: "neg",
        asOf: "Apr 2026",
        // Choppy m/m job gains, recent print softer.
        spark: [
          45, 32, 28, 51, 22, 18, 41, 35, 27, 38, 24, 30,
          19, 33, 28, 22, 31, 26, 18, 24, 20, 22, 15, 12,
        ],
      },
      {
        indicator: "Hourly wages, y/y",
        value: "+3.9%",
        delta: "-0.2 pp",
        deltaDir: "neg",
        asOf: "Apr 2026",
        // Wages easing off cycle highs.
        spark: [
          5.2, 5.1, 5.0, 4.9, 4.9, 5.0, 4.9, 4.8, 4.7, 4.6, 4.6, 4.5,
          4.4, 4.4, 4.3, 4.2, 4.2, 4.1, 4.1, 4.0, 4.0, 4.1, 4.0, 3.9,
        ],
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
        value: "-1.4%",
        delta: "-0.3 pp",
        deltaDir: "neg",
        asOf: "Apr 2026",
        // HPI rolled positive, crossed through zero, now sliding.
        spark: [
          3.2, 2.8, 2.4, 1.9, 1.5, 1.1, 0.8, 0.4, 0.1, -0.2, -0.4, -0.5,
          -0.6, -0.7, -0.8, -0.9, -1.0, -1.0, -1.1, -1.2, -1.2, -1.1, -1.3, -1.4,
        ],
      },
      {
        indicator: "Housing starts, 3M MA",
        value: "238k",
        delta: "-6k",
        deltaDir: "neg",
        asOf: "Apr 2026",
        spark: [
          262, 268, 270, 265, 258, 262, 255, 250, 248, 252, 246, 250,
          244, 248, 250, 246, 244, 246, 242, 248, 246, 244, 244, 238,
        ],
      },
      {
        indicator: "Sales-to-new-listings",
        value: "0.42",
        delta: "-0.03",
        deltaDir: "neg",
        asOf: "Apr 2026",
        spark: [
          0.58, 0.56, 0.55, 0.53, 0.52, 0.54, 0.52, 0.50, 0.49, 0.51, 0.48, 0.47,
          0.49, 0.46, 0.47, 0.45, 0.46, 0.45, 0.46, 0.45, 0.44, 0.43, 0.45, 0.42,
        ],
      },
    ],
    blurb: {
      kind: "last",
      date: "Apr 15, 2026",
      body:
        "Toronto and Vancouver kept loosening into the spring market; Calgary held firm. The renewal cohort that prints over the summer is the one to watch, and we still expect the residual transmission to land mostly through consumption.",
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
        key: "policy-rate",
        indicator: "BoC overnight rate",
        value: "2.75%",
        delta: "-25 bps",
        deltaDir: "pos",
        asOf: "Apr 29, 2026",
        // Staircase cuts off the 5.00 peak, with hold periods between.
        spark: [
          5.00, 5.00, 5.00, 5.00, 4.75, 4.75, 4.50, 4.50, 4.25, 4.25, 4.00, 4.00,
          3.75, 3.75, 3.75, 3.50, 3.50, 3.25, 3.25, 3.00, 3.00, 3.00, 2.75, 2.75,
        ],
      },
      {
        indicator: "BoC-Fed spread, 2y",
        value: "-152 bps",
        delta: "-8 bps",
        deltaDir: "neg",
        asOf: "May 9, 2026",
        // Spread widening more negative as BoC cuts faster than Fed.
        spark: [
          -25, -32, -45, -58, -64, -72, -85, -91, -98, -108, -115, -120,
          -125, -130, -132, -134, -138, -141, -143, -145, -148, -149, -150, -152,
        ],
      },
      {
        indicator: "Federal deficit, YTD",
        value: "$38.2B",
        delta: "+$4.1B vs plan",
        deltaDir: "neg",
        asOf: "Feb 2026",
        // YTD accumulation — fiscal year cumulative, so monotone up.
        spark: [
          2.1, 4.4, 7.2, 10.1, 13.0, 15.8, 18.5, 21.4, 24.3, 27.6, 30.8, 33.6, 38.2,
        ],
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
        key: "usdcad",
        indicator: "USDCAD",
        value: "1.378",
        delta: "+0.4% w/w",
        deltaDir: "neg",
        asOf: "May 9, 2026",
        // CAD weakening; FX walk.
        spark: [
          1.348, 1.352, 1.351, 1.355, 1.358, 1.354, 1.357, 1.361, 1.360, 1.364, 1.366, 1.362,
          1.365, 1.368, 1.371, 1.369, 1.372, 1.370, 1.374, 1.373, 1.376, 1.374, 1.377, 1.378,
        ],
      },
      {
        indicator: "GoC 10y",
        value: "3.41%",
        delta: "+6 bps",
        deltaDir: "neutral",
        asOf: "May 9, 2026",
        // 10y wandering in a 30bp range.
        spark: [
          3.55, 3.52, 3.48, 3.45, 3.42, 3.38, 3.35, 3.32, 3.30, 3.33, 3.36, 3.34,
          3.32, 3.35, 3.38, 3.36, 3.34, 3.36, 3.38, 3.40, 3.37, 3.38, 3.40, 3.41,
        ],
      },
      {
        indicator: "WTI",
        value: "$71.40",
        delta: "-2.1% w/w",
        deltaDir: "neg",
        asOf: "May 9, 2026",
        // Crude drifting lower.
        spark: [
          82.4, 81.2, 80.5, 79.8, 78.6, 79.2, 78.0, 76.9, 77.4, 76.1, 75.3, 74.8,
          75.5, 74.2, 73.6, 74.0, 73.1, 72.4, 73.0, 72.2, 71.8, 72.9, 72.0, 71.4,
        ],
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
        indicator: "Merch trade balance",
        value: "-$2.3B",
        delta: "-$1.1B m/m",
        deltaDir: "neg",
        asOf: "Mar 2026",
        // Swings across zero, lately deeper deficit.
        spark: [
          1.4, 0.8, 1.1, 0.2, -0.3, 0.5, 0.1, -0.4, -0.8, 0.2, -0.6, -1.0,
          -0.5, -1.2, -0.8, -1.5, -1.1, -1.6, -1.2, -1.8, -1.3, -1.6, -1.2, -2.3,
        ],
      },
      {
        indicator: "US export share",
        value: "73.1%",
        delta: "-0.4 pp y/y",
        deltaDir: "neutral",
        asOf: "Mar 2026",
        // Slow secular drift down from mid-70s.
        spark: [
          75.2, 75.0, 74.9, 74.8, 74.6, 74.5, 74.3, 74.4, 74.2, 74.0, 73.9, 73.8,
          73.7, 73.8, 73.6, 73.5, 73.4, 73.5, 73.3, 73.2, 73.3, 73.2, 73.2, 73.1,
        ],
      },
      {
        indicator: "Terms of trade",
        value: "104.6",
        delta: "-0.8",
        deltaDir: "neg",
        asOf: "2026Q1",
        // Quarterly index, fewer points.
        spark: [
          106.2, 106.8, 107.1, 106.5, 105.9, 105.4, 105.2, 104.6,
        ],
      },
    ],
    blurb: {
      kind: "last",
      date: "Apr 3, 2026",
      body:
        "Auto and energy carried the March print on opposite shoulders. The US share keeps drifting, but the Section 232 follow-on actions named in March are the variable that matters into the summer USMCA review window.",
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

export type DeepDiveStatus = "research" | "drafted" | "shipped";

export interface DeepDive {
  /** Pillar code from editorial canon: A through H. */
  pillar: string;
  /** Home section slug — drives the section badge color. */
  section: SectionSlug;
  /** Short title, set as serif display-sm. */
  title: string;
  /** One-sentence deck; serif italic. */
  deck: string;
  status: DeepDiveStatus;
  /** Display string for the "Updated" stamp. */
  lastUpdated: string;
  /** Eventual destination; v1 may resolve to a section page placeholder. */
  href?: string;
}

export const deepDives: DeepDive[] = [
  {
    pillar: "A",
    section: "housing",
    title: "Mortgage renewal wall: has it peaked?",
    deck:
      "The 2026 renewal cohort is the largest single tranche in the stack. We map where the residual transmission lands through 2027.",
    status: "drafted",
    lastUpdated: "May 6, 2026",
  },
  {
    pillar: "B",
    section: "policy",
    title: "BoC vs. Fed: how far can the divergence run?",
    deck:
      "152 basis points and counting. We trace the CAD, GoC curve, and credit channels that would force a back-off, and where the breakpoints sit.",
    status: "shipped",
    lastUpdated: "Apr 30, 2026",
  },
  {
    pillar: "E",
    section: "labour",
    title: "Per-capita output: deceleration or weakness?",
    deck:
      "The headline labour print is flattering. The per-capita series is not. We separate the population-deceleration story from the cyclical weakness story.",
    status: "research",
    lastUpdated: "May 8, 2026",
  },
];

/*
 * Next-release indicator for the homepage date strip.
 * OWNER: backend pipeline will derive this from the Canadian release
 * calendar at build time. v1 placeholder values per the May 2026 calendar
 * in editorial/dashboard_purpose.md sec 6.
 */
export const nextRelease = {
  label: "CPI, April 2026",
  date: "Tue, May 21, 2026",
  agency: "Statistics Canada",
};

/*
 * Site-level metadata. Used by BaseLayout and SEO tags. Edit by
 * editorial-director / art-director as the brand crystallizes.
 */
export const site = {
  name: "Macro Research Department",
  shortName: "MRD",
  // F7 (art-director): the previous italic tagline competed with the wordmark
  // and the section names. Replaced with a short all-caps label rail; the
  // wordmark below renders it in label-sized sans with letter-spacing so it
  // reads as a category line, not a slogan.
  tagline: "Canadian macro research",
  description:
    "A reading-first dashboard for Canadian macroeconomic indicators. Written for analysts, policymakers, and serious citizens.",
  locale: "en-CA",
  url: "https://example.invalid",
};
