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
 *   headlineQuestion  - The section's anchor question, per
 *                       editorial/dashboard_purpose.md sec 4. Rendered as
 *                       the tile deck (serif italic, one line on desktop).
 *   cadence           - Short string for the "As of [date] . [cadence]" tile
 *                       footer line (per editorial/dashboard_purpose.md sec 6).
 *   prints            - 2-3 most important prints surfaced on the tile.
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
   * Optional stable key for this print, used to identify the primary
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
   * Source citations for the section's `blurb.body` (the under-question
   * synthesis on the section page and the sparkline-blurb on the splash).
   */
  abstractCitations?: import("../layouts/SectionLayout.astro").ClaimCitation[];
  /**
   * Source citations for the section's `tileLine` (the 1-sentence summary
   * rendered on the splash tile under the section name + chart).
   */
  tileLineCitations?: import("../layouts/SectionLayout.astro").ClaimCitation[];
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
   * Key into this section's `prints[]` identifying the primary time
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
   * Editorial prefix for the auto-derived hero kicker. When set, downstream
   * components compose `"{heroKickerPrefix} {derivedDate}"` using the
   * section's primary print date from the pipeline payload (e.g.
   * `"CPI"` + `"Mar 2026"` -> `"CPI Mar 2026"`). The static `heroKicker`
   * remains as the fallback when the pipeline payload is unavailable or
   * the prefix is unset.
   *
   * Backend pipeline keeps the derived date in sync as new prints land;
   * `heroKickerPrefix` is editorial-canon-stable (the noun is the print
   * name, e.g. "CPI", "LFS", "Weekly close").
   */
  heroKickerPrefix?: string;
  /**
   * Editorial prefix for the section page's top-level "Latest release"
   * stamp. Composed as `"{latestReleasePrefix}, {derivedDate}"` at build
   * time, where `derivedDate` comes from sections.json's `prints[0]`
   * (or the print matching `chartSeriesKey`).
   *
   * Examples: "Headline CPI", "LFS", "BoC rate decision", "Daily close",
   * "Merchandise trade", "Home prices", "Monthly GDP by industry".
   *
   * Set per section in the canon block below. The Policy section is a
   * special case: the primary event (the rate decision) doesn't sit
   * in `prints[]` — see `latestReleaseDateOverride` for that path.
   */
  latestReleasePrefix?: string;
  /**
   * Optional hand-set "Latest release" date for sections whose load-
   * bearing event is NOT one of the standard pipeline prints (e.g. Policy
   * — the BoC rate decision is the event, but `prints[0]` is the
   * overnight rate, dated to the latest monthly observation, not the
   * decision day). Combined with `latestReleasePrefix` directly:
   *   "{latestReleasePrefix}, {latestReleaseDateOverride}"
   *
   * Keep this updated alongside the canonical event. The default flow
   * uses the auto-derived date from sections.json.
   */
  latestReleaseDateOverride?: string;
  /**
   * Homepage section panel's one-liner. Renders as `<p class="vig-panel__note">`
   * below the readout block on each splash panel.
   *
   * **HARD CHAR BUDGET: <= 85 characters.** The slot is styled with
   * `display: -webkit-box; -webkit-line-clamp: 3; overflow: hidden;
   * max-width: 44ch;` in SectionPanel.astro. Copy longer than ~85
   * chars truncates mid-word without visible ellipsis (the labour
   * tile at 112 chars showed this failure on 2026-05-11).
   *
   * Voice: one sentence, declarative, names the primary print +
   * the editorial so-what. Sibling-compare to the other 6 sections
   * before committing — outliers in length truncate.
   */
  tileLine?: string;
  /**
   * Splash tile chart treatment. Defaults to "line" (canonical sparkline).
   * Set "bars" for signed series where direction is the visual story —
   * e.g. trade balance (deficit / surplus alternation), contributions
   * to growth (mixed-sign components).
   */
  tileChartKind?: "line" | "bars";
}

export const sections: Section[] = [
  {
    slug: "gdp",
    label: "Output",
    accentVar: "--section-accent-gdp",
    kicker: "Output, expenditure, and the quarterly arithmetic of growth.",
    headlineQuestion:
      "How fast is Canada's economy growing, and where?",
    cadence: "Monthly + quarterly",
    // Most recent monthly GDP print released Apr 30, 2026 (Feb 2026 reference period).
    updatedAt: Date.UTC(2026, 3, 30, 8, 30),
    chartSeriesKey: "gdp-yoy",
    heroKicker: "February GDP",
    heroKickerPrefix: "GDP",
    latestReleasePrefix: "Monthly GDP by industry",
    tileLine:
      "February GDP came in soft on goods-producing industries; services held up.",
    prints: [
      {
        // Real GDP y/y is the primary print — first row, matches the
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
      date: "Apr 30, 2026",
      body:
        "Slowly, and mostly in the resource patch. Real GDP is running near 1% Y/Y, just below the Bank of Canada's 1.2% estimate of near-term potential growth. Oil and gas are doing the heavy lifting while manufacturing is in deep recession. Services growth is trundling along. Even that 1% pace relies on population growth more than anything — on a per capita basis, output is scarcely higher than it was before the pandemic.",
    },
    abstractCitations: [
      { phrase: "near 1% Y/Y", source: "pipeline:statcan:36-10-0434-01", note: "Real GDP Y/Y, latest monthly print." },
      { phrase: "1.2% estimate of near-term potential growth", source: "card:boc_mpr_potential_growth" },
    ],
  },
  {
    slug: "inflation",
    label: "Inflation",
    accentVar: "--section-accent-inflation",
    kicker: "Headline, core, and the breadth of price pressure.",
    headlineQuestion:
      "How close is Canadian inflation to the 2% target, and is the anchor holding?",
    cadence: "Monthly",
    // Most recent CPI print released Apr 20, 2026 (March 2026 reference period).
    // April CPI lands May 14; not yet on disk as of 2026-05-11.
    updatedAt: Date.UTC(2026, 3, 20, 8, 30),
    chartSeriesKey: "cpi-yoy",
    heroKicker: "March CPI",
    heroKickerPrefix: "CPI",
    latestReleasePrefix: "Headline CPI",
    tileLine:
      "Headline CPI at 2.3% in March; food and energy carry the above-target weight.",
    tileLineCitations: [
      { phrase: "2.3%", source: "pipeline:statcan:18-10-0004-01", note: "Headline CPI Y/Y, March 2026." },
    ],
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
        indicator: "CPI share >3%, y/y",
        value: "TK",
        delta: "TK",
        deltaDir: "neutral",
        asOf: "TK",
      spark: [],
      },
    ],
    blurb: {
      kind: "last",
      date: "Apr 20, 2026",
      body:
        "Headline CPI sits at 2.3% — a hair above target, with food and energy now carrying the overshoot that shelter used to. Core-trim and core-median, the measures the Bank of Canada actually reacts to, are back at 2.2-2.3%. And consumer and firm expectations have moderated together: the anchor is holding while the composition rotates.",
    },
    abstractCitations: [
      { phrase: "Headline CPI sits at 2.3%", source: "pipeline:statcan:18-10-0004-01", note: "Headline CPI Y/Y, March 2026." },
      { phrase: "back at 2.2-2.3%", source: "pipeline:boc:STATIC_TOTALCPICOMMON_TRIM", note: "CPI-trim and CPI-median Y/Y range, March 2026; BoC Valet preferred-core series." },
    ],
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
      "Is the labour market loosening, and how fast?",
    cadence: "Monthly",
    // Most recent LFS landed May 2, 2026 (April 2026 reference period).
    updatedAt: Date.UTC(2026, 4, 2, 8, 30),
    chartSeriesKey: "unrate",
    heroKicker: "April LFS",
    heroKickerPrefix: "LFS",
    latestReleasePrefix: "LFS",
    tileLine:
      "Unemployment climbed to 6.9% in April; aggregate hours turned negative Y/Y.",
    tileLineCitations: [
      { phrase: "6.9%", source: "pipeline:statcan:14-10-0287-01", note: "LFS unemployment rate, SA, April 2026." },
    ],
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
      kind: "fresh",
      date: "May 8, 2026",
      body:
        "Yes, and the intensive margin is leading. Hours worked are running negative year-over-year while the unemployment rate has drifted up to 6.9%, the pattern of a market that is shedding work before it sheds workers — and one where a population surge is being absorbed straight into not-in-labour-force rather than into jobs. Wages are the lagging piece, with composition-adjusted growth at 3.1% still above where the Bank of Canada wants it, but the cyclical direction is no longer in doubt.",
    },
    abstractCitations: [
      { phrase: "unemployment rate has drifted up to 6.9%", source: "pipeline:statcan:14-10-0287-01", note: "LFS unemployment rate, SA, Apr 2026." },
      { phrase: "composition-adjusted growth at 3.1%", source: "pipeline:boc:INDINF_LFSMICRO_M", note: "BoC LFS-Micro composition-adjusted wage growth, Y/Y, Mar 2026." },
    ],
  },
  {
    slug: "policy",
    label: "Policy",
    accentVar: "--section-accent-policy",
    kicker: "The Bank of Canada and the federal fiscal stance.",
    headlineQuestion:
      "What is the policy stance, and is it consistent with the cycle?",
    cadence: "Event-driven + monthly",
    // Apr 29 rate decision is the primary event; daily yields refresh
    // continuously but the policy stance is anchored to the rate decision.
    updatedAt: Date.UTC(2026, 3, 29, 14, 0),
    chartSeriesKey: "policy-rate",
    heroKicker: "April rate decision",
    // Policy's primary event is the rate decision, not the pipeline's
    // monthly `policy-rate` print. heroKickerPrefix is hand-set to the
    // event-month phrasing; the page-level "Latest release" date is
    // hand-overridden via latestReleaseDateOverride since the rate
    // decision doesn't sit in `prints[]` directly.
    heroKickerPrefix: "Rate decision",
    latestReleasePrefix: "BoC rate decision",
    latestReleaseDateOverride: "Apr 29, 2026",
    tileLine:
      "BoC held at 2.25% on April 29, the fourth straight hold since October's cut.",
    tileLineCitations: [
      { phrase: "2.25%", source: "pipeline:boc:V39079", note: "BoC overnight target rate, Apr 29 2026 FAD decision, via Valet V39079." },
      { phrase: "fourth straight", source: "pipeline:boc:V39079", note: "Enumerated FAD sequence: Jan 29, Mar 12, Apr 16, Apr 29 holds following Oct 29 2025 cut." },
    ],
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
      kind: "last",
      date: "Apr 29, 2026",
      body:
        "The Bank of Canada held the overnight rate at 2.25% on April 29, the fourth straight hold since October's cut and 50 bps below the 2.75% neutral midpoint. The 2y GoC yield closed at 2.94% on May 7, leaving the BoC-Fed 2y spread at -98 bps. The fiscal year-to-date federal budget balance stood at -$25.5B through February, per the Department of Finance Canada fiscal monitor.",
    },
    abstractCitations: [
      { phrase: "overnight rate at 2.25% on April 29", source: "pipeline:boc:V39079", note: "BoC overnight target rate, Apr 29 2026 FAD decision, via Valet V39079." },
      { phrase: "fourth straight hold", source: "pipeline:boc:V39079", note: "Enumerated FAD sequence: Jan 29, Mar 12, Apr 16, Apr 29 holds following Oct 29 2025 cut." },
      { phrase: "50 bps below the 2.75% neutral midpoint", source: "card:boc_mpr_neutral_range", note: "Midpoint of the 2.25-3.25% nominal neutral range; 2.75% - 2.25% overnight = 50 bps gap." },
      { phrase: "2.75% neutral midpoint", source: "card:boc_mpr_neutral_range" },
      { phrase: "2y GoC yield closed at 2.94% on May 7", source: "pipeline:boc:yield_2yr", note: "GoC 2y benchmark yield, May 7 2026 daily close." },
      { phrase: "BoC-Fed 2y spread at -98 bps", source: "derived", note: "GoC 2y 2.94% minus UST 2y 3.92% = -98 bps. Inputs: BoC Valet yield_2yr and FRED DGS2, May 7 2026." },
      { phrase: "$25.5B through February", source: "pipeline:dof:dof_fiscal_ytd_balance", note: "Federal fiscal YTD balance, April 2025 through February 2026, per DoF Fiscal Monitor. -25,549M rounds to -$25.5bn." },
    ],
  },
  {
    slug: "housing",
    label: "Housing",
    accentVar: "--section-accent-housing",
    kicker: "Starts, sales, prices, and household leverage.",
    headlineQuestion:
      "Is the rate-sensitive sector amplifying or dampening policy?",
    cadence: "Monthly",
    // CREA April release (March reference period) landed Apr 15, 2026.
    updatedAt: Date.UTC(2026, 3, 15, 9, 0),
    chartSeriesKey: "hpi-yoy",
    heroKicker: "March home prices",
    heroKickerPrefix: "Home prices",
    latestReleasePrefix: "Home prices",
    tileLine:
      "Composite home prices down 4.6% Y/Y, now two years of negative readings.",
    tileLineCitations: [
      { phrase: "4.6%", source: "pipeline:crea:mls_hpi_national", note: "CREA MLS HPI composite, Y/Y, March 2026." },
      { phrase: "two years of negative readings", source: "pipeline:crea:mls_hpi_national", note: "Enumerated: CREA MLS HPI Y/Y has printed negative every month since April 2024 — 24 consecutive months through March 2026." },
    ],
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
        indicator: "Bank mortgage arrears",
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
        "Home prices fell 4.6% Y/Y on the MLS HPI in the latest print, per the Canadian Real Estate Association, a tenth shallower than the prior month but now two years into negative territory. Housing starts on a 3mma basis stepped down to 241k from 257k, per Canada Mortgage and Housing Corporation. Affordability held at 42.7% of household income in Q4 2025, half a point easier on continued mortgage-cost relief.",
    },
    abstractCitations: [
      { phrase: "fell 4.6% Y/Y on the MLS HPI", source: "pipeline:crea:mls_hpi_national", note: "CREA MLS HPI composite, Y/Y, Mar 2026." },
      { phrase: "two years into negative territory", source: "pipeline:crea:mls_hpi_national", note: "Enumerated: CREA MLS HPI Y/Y has printed negative every month since April 2024 — 24 consecutive months through March 2026." },
      { phrase: "241k from 257k", source: "pipeline:statcan:34-10-0158-01", note: "Total housing starts, SAAR 3mma; latest vs prior month per CMHC release (StatCan table)." },
      { phrase: "42.7% of household income in Q4 2025", source: "pipeline:boc:INDINF_AFFORD_Q", note: "BoC housing affordability index, qualifying payment / income, 2025Q4." },
    ],
  },
  {
    slug: "trade",
    label: "Trade",
    accentVar: "--section-accent-trade",
    kicker: "Exports, imports, and the terms by which Canada sells its work.",
    headlineQuestion:
      "Is Canada's external position structurally shifting under US repricing?",
    cadence: "Monthly + event",
    // March merch-trade release landed May 5, 2026.
    updatedAt: Date.UTC(2026, 4, 5, 8, 30),
    chartSeriesKey: "trade-balance",
    heroKicker: "March balance",
    heroKickerPrefix: "Trade balance",
    latestReleasePrefix: "Merchandise trade",
    tileLine:
      "Goods balance narrowed to -$2.2B; US export share fell to 66.1%.",
    tileLineCitations: [
      { phrase: "-$2.2B", source: "pipeline:statcan:12-10-0119-01", note: "Goods trade balance, 3-month moving average, March 2026." },
      { phrase: "66.1%", source: "pipeline:statcan:12-10-0121-01", note: "US share of total Canadian goods exports, March 2026." },
    ],
    tileChartKind: "bars",
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
      date: "May 6, 2026",
      body:
        "The goods trade balance narrowed to -$2.2B on a 3mma basis in March, per Statistics Canada, an $876M improvement from February. The US export share fell 2.5pp to 66.1%, the lowest reading in the available window and a continuation of the year-long drift down from the 76 to 80% range that held through 2024. The Q4 2025 current account narrowed to -$706M, a $4.6B improvement; terms of trade ticked up 0.6 to 105.5.",
    },
    abstractCitations: [
      { phrase: "narrowed to -$2.2B on a 3mma basis in March", source: "pipeline:statcan:12-10-0119-01", note: "Goods trade balance, 3-month moving average, March 2026." },
      { phrase: "$876M improvement from February", source: "derived", note: "March 2026 3mma minus February 2026 3mma goods balance, StatCan 12-10-0119-01." },
      { phrase: "US export share fell 2.5pp to 66.1%", source: "pipeline:statcan:12-10-0121-01", note: "US share of total Canadian goods exports, March 2026; 2.5pp drop vs prior month." },
      { phrase: "76 to 80% range that held through 2024", source: "pipeline:statcan:12-10-0121-01", note: "Enumerated US export share monthly series: trailing 12-month band sat in the 76-80% range across 2024." },
      { phrase: "Q4 2025 current account narrowed to -$706M", source: "pipeline:statcan:36-10-0014-01", note: "Current account balance, Q4 2025." },
      { phrase: "$4.6B improvement", source: "derived", note: "Q4 2025 current account (-$706M) minus Q3 2025 current account, StatCan 36-10-0014-01." },
    ],
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
    // Markets data refreshes daily; latest BoC noon-rate stamp May 8, 2026.
    updatedAt: Date.UTC(2026, 4, 8, 21, 0),
    chartSeriesKey: "usdcad",
    heroKicker: "Weekly close",
    // Markets refreshes daily; the kicker phrase "Daily close" + the
    // pipeline's daily-cadence date reads as the current convention
    // ("Daily close May 8, 2026").
    heroKickerPrefix: "Daily close",
    latestReleasePrefix: "Daily close",
    tileLine:
      "USDCAD closed the week at 1.369 as the BoC-Fed 2y spread held near -98 bps.",
    tileLineCitations: [
      { phrase: "-98 bps", source: "derived", note: "GoC 2y 2.94% minus UST 2y 3.92% = -98 bps. Inputs: BoC Valet yield_2yr and FRED DGS2, May 7 2026." },
    ],
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
      date: "May 8, 2026",
      body:
        "USDCAD closed May 8 at 1.369, up 0.8% on the week, per Bank of Canada noon rates. The 10y GoC yield closed at 3.53% on May 7, two basis points firmer. WTI rose to $109.76 by May 4, a 9.9% move that put crude back above $100 after dipping briefly below; the TSX Composite closed near 34.1k, flat on the session.",
    },
    abstractCitations: [
      { phrase: "up 0.8% on the week", source: "derived", note: "USDCAD week-over-week change: 1.3576 (May 1) -> 1.3686 (May 8) = +0.81%, rounds to 0.8%. Per BoC Valet FXUSDCAD." },
      { phrase: "10y GoC yield closed at 3.53% on May 7", source: "pipeline:boc:yield_10yr", note: "GoC 10y benchmark yield, May 7 2026 daily close." },
      { phrase: "WTI rose to $109.76 by May 4", source: "pipeline:fred:DCOILWTICO", note: "WTI spot, May 4 2026 daily close." },
      { phrase: "a 9.9% move", source: "derived", note: "WTI week-over-week change: 99.89 (Apr 27) -> 109.76 (May 4) = +9.88%, rounds to 9.9%. Per FRED DCOILWTICO." },
      { phrase: "back above $100 after dipping briefly below", source: "pipeline:fred:DCOILWTICO", note: "WTI closed at 98.07 on May 1, dipping below $100 between Apr 27 (99.89) and May 4 (109.76)." },
      { phrase: "TSX Composite closed near 34.1k", source: "other:TMX Group S&P/TSX Composite Index close, May 8, 2026." },
    ],
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
   * ISO date string (YYYY-MM-DD) representing the latest data vintage the
   * deep-dive's prose was authored against. Rendered on /research/<slug>/
   * as a "Data vintage" stamp below the published-date stamp; auto-computes
   * a freshness warning when more than 90 days stale.
   *
   * Per methodology canon (editorial/insight_base/methodology_page.md
   * Section 3, "show latest vintage as-is, revisions flow through"), the
   * site's section pages always reflect the most recent print. The
   * deep-dive page is the exception: prose was authored against a specific
   * vintage and the argument cannot silently re-anchor as the data
   * underneath revises. This stamp tells the reader how stale the cited
   * values may be vs. the prose argument.
   *
   * Source convention: take the latest dated source named in the
   * piece's data-stamp paragraph (typically in the frontmatter). For
   * pieces with no explicit data-stamp paragraph, use the authoring date.
   */
  dataVintage?: string;
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
  /**
   * Reader-facing draft flag. When set to "draft", the piece is shipped
   * but the prose is AI-generated and pending human revision. The site
   * renders a "DRAFT - HUMAN REVISION PENDING" stamp in the deep-dive
   * header band (under the data-vintage line) and a "DRAFT" chip on the
   * /research/ index row. Omit (or set to undefined) for human-edited
   * pieces — no stamp renders.
   *
   * This is a credibility-protection lever for the reader: machine prose
   * is acknowledged on-surface rather than passed off as authored copy.
   * It is the one place red signals a non-data caveat in the canon.
   */
  draftStatus?: "draft";
}

export const deepDives: DeepDive[] = [
  {
    slug: "mortgage-renewal-wall",
    section: "housing",
    title: "Mortgage renewal wall: has it peaked?",
    deck:
      "The 2026 renewal cohort is the largest single tranche in the stack. We map where the residual transmission lands through 2027.",
    publishedAt: "2026-05-08",
    lastUpdated: "TK",
    // Latest dated source in the data-stamp paragraph is the BoC April 2026
    // MPR (April 29, 2026); CREA MLS HPI April 2026 ties on month but the
    // MPR release date is the most specific anchor.
    dataVintage: "2026-04-29",
    draftPath: "editorial/drafts/deepdive_pillar_a_mortgage_renewal_wall_v1.md",
    publishedPath: "editorial/published/mortgage-renewal-wall.md",
    // Legacy fields retained so /experiments/* keeps building. Not rendered in production.
    pillar: "A",
    status: "drafted",
    // Tagged as a pending-human-review draft so the reader sees the
    // "DRAFT - HUMAN REVISION PENDING" stamp. Matches the other three
    // deep dives in this set — all four pieces were authored or revised
    // by the writer agent and have not been human-finalized.
    draftStatus: "draft",
  },
  {
    slug: "boc-fed-divergence",
    section: "policy",
    title: "BoC vs. Fed: how far can the divergence run?",
    deck:
      "The policy spread sits at the 8th percentile of three decades; USDCAD is at the 67th and strengthening. The binding constraint is not the loonie but the expectations chain.",
    publishedAt: "2026-05-10",
    lastUpdated: "2026-05-10",
    dataVintage: "2026-05-11",
    draftPath: "editorial/drafts/deepdive_pillar_b_boc_fed_divergence_v1.md",
    publishedPath: "editorial/published/boc-fed-divergence.md",
    pillar: "B",
    status: "shipped",
    draftStatus: "draft",
  },
  {
    slug: "per-capita-output",
    section: "labour",
    title: "Per-capita output: deceleration or weakness?",
    deck:
      "The headline labour print is flattering. The per-capita series is not. We separate the population-deceleration story from the cyclical weakness story.",
    publishedAt: "2026-05-09",
    lastUpdated: "2026-05-09",
    dataVintage: "2026-05-11",
    draftPath: "editorial/drafts/deepdive_pillar_e_per_capita_output_v1.md",
    publishedPath: "editorial/published/per-capita-output.md",
    pillar: "E",
    status: "drafted",
    draftStatus: "draft",
  },
  {
    slug: "us-tariff-repricing",
    section: "trade",
    title: "The reorientation has already happened",
    deck:
      "Canada's US export share has dropped ten percentage points in fourteen months. The argument over USMCA is happening on top of a structural break, not in advance of one.",
    publishedAt: "2026-05-11",
    lastUpdated: "2026-05-11",
    dataVintage: "2026-05-11",
    draftPath: "editorial/drafts/deepdive_trade_tariffs_v1.md",
    publishedPath: "editorial/published/us-tariff-repricing.md",
    status: "shipped",
    draftStatus: "draft",
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
 * Splash-page hero abstract. The text rendered under the "Where is Canada's
 * economy?" headline on the homepage (src/components/home/TitleStatement.astro).
 * Lives here so the build-time citation gate
 * (scripts/check_citation_coverage.mjs) can scan it like the section
 * abstracts. TitleStatement imports `splashHero.abstract`.
 */
export const splashHero: {
  abstract: string;
  citations: import("../layouts/SectionLayout.astro").ClaimCitation[];
} = {
  abstract:
    "Cyclically, Canada is slowing down. Disinflation is in the final mile and slack is building in the labour market. Structurally, the economy is readjusting to halted population growth and tariffs. Per-capita output is virtually flat since 2019; the US export share has fallen from three quarters to two thirds over the last year.",
  citations: [
    { phrase: "since 2019", source: "pipeline:statcan:36-10-0104-01", note: "Per-capita real GDP indexed to 2019Q4." },
    { phrase: "from three quarters to two thirds", source: "derived", note: "US share of Canadian merchandise exports moved from ~75% (Y2024 average) to ~66% (latest 3mma) per StatCan 12-10-0121-01." },
    { phrase: "over the last year", source: "pipeline:statcan:12-10-0121-01", note: "12-month window through latest monthly merchandise-trade-by-partner release." },
  ],
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
    "Sibley Creek - Canadian macroeconomic indicators and analysis. Independent research on GDP, inflation, labour, housing, monetary policy, markets, and trade.",
  locale: "en-CA",
  url: "https://example.invalid",
};
