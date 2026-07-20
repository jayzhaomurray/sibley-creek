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
  | "output"
  | "inflation"
  | "labour"
  | "housing"
  | "monetary"
  | "fiscal"
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
   * Examples: "CPI", "LFS", "BoC rate decision", "Daily close",
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
    slug: "output",
    label: "Output",
    accentVar: "--section-accent-gdp",
    kicker: "Output, expenditure, and the quarterly arithmetic of growth.",
    headlineQuestion:
      "How fast is Canada's economy growing?",
    cadence: "Monthly + quarterly",
    // Most recent monthly GDP print released Jun 30, 2026 (Apr 2026 reference period).
    updatedAt: Date.UTC(2026, 5, 30, 8, 30),
    chartSeriesKey: "gdp-yoy",
    heroKicker: "April & Q1 GDP",
    heroKickerPrefix: "GDP",
    latestReleasePrefix: "Monthly GDP by industry",
    tileLine:
      "Growth picked up to 1.1% in April, led by the goods sector.",
    tileLineCitations: [
      { phrase: "1.1% in April", source: "pipeline:statcan:gdp_monthly_yoy", note: "Monthly real GDP y/y: 1.12% Apr 2026, up from 0.44% Mar 2026 (data/processed/gdp_monthly_yoy.csv)." },
    ],
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
      date: "June 30, 2026",
      body:
        "Growth is running at 1.1% year-over-year, just below potential. Real GDP rose 0.5% in April after a soft first quarter, and while momentum is uneven, the data don't point to a recession underway.",
    },
    abstractCitations: [
      { phrase: "1.1% year-over-year", source: "pipeline:statcan:36-10-0434-01", note: "Real GDP Y/Y, April 2026 monthly print = 1.12%." },
      { phrase: "0.5% in April", source: "pipeline:statcan:36-10-0434-01", note: "April 2026 monthly real GDP m/m = +0.547%." },
      { phrase: "just below potential", source: "card:boc_mpr_potential_growth", note: "BoC near-term potential growth 1.2% (MPR April 2026); 1.1% y/y sits just below." },
    ],
  },
  {
    slug: "inflation",
    label: "Inflation",
    accentVar: "--section-accent-inflation",
    kicker: "Headline, core, and the breadth of price pressure.",
    headlineQuestion:
      "How close is Canadian inflation to the 2% target?",
    cadence: "Monthly",
    // Most recent CPI print released Jun 22, 2026 (May 2026 reference period).
    updatedAt: Date.UTC(2026, 5, 22, 8, 30),
    chartSeriesKey: "cpi-yoy",
    heroKicker: "May CPI",
    heroKickerPrefix: "CPI",
    latestReleasePrefix: "CPI",
    tileLine:
      "Headline CPI hit 3.2% in May; cores held at 2.0-2.1%.",
    tileLineCitations: [
      { phrase: "3.2%", source: "pipeline:statcan:18-10-0004-01", note: "Headline CPI NSA Y/Y, May 2026." },
      { phrase: "2.0-2.1%", source: "pipeline:statcan:cpi_trim", note: "CPI-trim 2.0% and CPI-median 2.1% Y/Y, May 2026; BoC Valet preferred-core series." },
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
      date: "Jun 22, 2026",
      body:
        "Headline CPI moved above the Bank of Canada's control band in May, rising to 3.2% year-over-year as energy inflation reached 22.2%. The underlying signal was steadier: CPI-trim held at 2.0%, CPI-median held at 2.1%, and goods excluding energy slowed to 0.7%. Breadth widened to 33.6% of the basket running above 3%, so the print is harder to dismiss than April's, but it is still led by energy rather than a broad core re-acceleration.",
    },
    abstractCitations: [
      { phrase: "3.2% year-over-year", source: "pipeline:statcan:18-10-0004-01", note: "Headline CPI NSA Y/Y, May 2026." },
      { phrase: "22.2%", source: "pipeline:statcan:18-10-0004-01", note: "Energy CPI Y/Y, May 2026." },
      { phrase: "CPI-trim held at 2.0%", source: "pipeline:statcan:cpi_trim", note: "CPI-trim Y/Y, May 2026; unchanged from April 2026." },
      { phrase: "CPI-median held at 2.1%", source: "pipeline:statcan:cpi_median", note: "CPI-median Y/Y, May 2026; unchanged from April 2026." },
      { phrase: "goods excluding energy slowed to 0.7%", source: "pipeline:statcan:18-10-0004-01", note: "Goods excluding energy CPI Y/Y, May 2026 = 0.7147%; April 2026 = 0.9439%." },
      { phrase: "33.6%", source: "derived", note: "Share of valid CPI components with Y/Y > 3%, May 2026 = 33.5858%." },
      { phrase: "above 3%", source: "card:boc_inflation_mandate", note: "3% is the upper edge of the Bank of Canada's 1-3% inflation-control range." },
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
      "Is the labour market loosening?",
    cadence: "Monthly",
    // Most recent LFS landed Jul 10, 2026 (Jun 2026 reference period).
    updatedAt: Date.UTC(2026, 6, 10, 8, 30),
    chartSeriesKey: "unrate",
    heroKicker: "June LFS",
    heroKickerPrefix: "LFS",
    latestReleasePrefix: "LFS",
    tileLine:
      "Canada added 18k jobs in June and unemployment fell to 6.5%.",
    tileLineCitations: [
      { phrase: "18k jobs in June", source: "pipeline:statcan:14-10-0287-01", note: "LFS employment change, SA, June 2026: +18.2k m/m (21.1397M from 21.1215M)." },
      { phrase: "6.5%", source: "pipeline:statcan:14-10-0287-01", note: "LFS unemployment rate, SA, June 2026." },
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
      date: "Jul 10, 2026",
      body:
        "Less than before. Canada added 18,200 jobs in June and the unemployment rate eased to 6.5%, while the employment rate rose to 60.8% and participation held at 65.0%. Hours worked barely moved and LFS-Micro wage growth is still running at 2.6%, so the print looks like a modest firming rather than a broad labour-market re-acceleration.",
    },
    abstractCitations: [
      { phrase: "18,200 jobs in June", source: "pipeline:statcan:14-10-0287-01", note: "LFS employment change, SA, June 2026: 21.1397M minus 21.1215M = +18.2k." },
      { phrase: "unemployment rate eased to 6.5%", source: "pipeline:statcan:14-10-0287-01", note: "LFS unemployment rate, SA: June 2026 = 6.5%, down from 6.6% in May." },
      { phrase: "employment rate rose to 60.8%", source: "pipeline:statcan:14-10-0287-01", note: "LFS employment rate, SA: June 2026 = 60.8%, up from 60.7% in May." },
      { phrase: "participation held at 65.0%", source: "pipeline:statcan:14-10-0287-01", note: "LFS participation rate, SA: June 2026 = 65.0%, unchanged from May." },
      { phrase: "Hours worked barely moved", source: "pipeline:statcan:14-10-0287-01", note: "Aggregate hours worked Y/Y slowed to 0.16% in June 2026 from 0.30% in May." },
      { phrase: "LFS-Micro wage growth is still running at 2.6%", source: "pipeline:boc:lfs_micro", note: "BoC LFS-Micro wage growth, May 2026 = 2.6% Y/Y; June observation not yet available in the Valet series at this refresh." },
    ],
  },
  {
    slug: "monetary",
    label: "Monetary",
    accentVar: "--section-accent-monetary",
    kicker: "The Bank of Canada: rate decisions, balance sheet, and market pricing.",
    headlineQuestion:
      "What is Canada's monetary policy stance?",
    cadence: "Event-driven + monthly",
    // Jul 15 rate decision is the primary event; daily yields refresh
    // continuously but the policy stance is anchored to the rate decision.
    updatedAt: Date.UTC(2026, 6, 15, 13, 45),
    chartSeriesKey: "policy-rate",
    heroKicker: "July rate decision",
    // Policy's primary event is the rate decision, not the pipeline's
    // monthly `policy-rate` print. heroKickerPrefix is hand-set to the
    // event-month phrasing; the page-level "Latest release" date is
    // hand-overridden via latestReleaseDateOverride since the rate
    // decision doesn't sit in `prints[]` directly.
    heroKickerPrefix: "Rate decision",
    latestReleasePrefix: "BoC rate decision",
    latestReleaseDateOverride: "Jul 15, 2026",
    tileLine:
      "BoC stayed at 2.25%; 2y GoCs are near 2.88% and the Canada-US spread is -138 bps.",
    tileLineCitations: [
      { phrase: "2.25%", source: "pipeline:boc:V39079", note: "BoC overnight target rate, July 15 2026 FAD decision, via Valet V39079." },
      { phrase: "2.88%", source: "pipeline:boc:yield_2yr", note: "GoC 2y benchmark yield, July 13 2026 daily close." },
      { phrase: "-138 bps", source: "derived", note: "Canada-US 2y spread, July 13 2026: GoC 2y 2.88% minus UST 2y 4.26% = -138 bps." },
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
        indicator: "Canada-US 2y spread",
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
      date: "Jul 15, 2026",
      body:
        "On hold. The Bank of Canada has stayed at 2.25% through six straight decisions, still at the floor of its 2.25 to 3.25% neutral range, and now calls the rate appropriate. Markets see it the same way: the 2-year GoC yield sits at 2.88%, well above the overnight rate, while the Canada-US 2-year spread is still deeply negative at -138 bps.",
    },
    abstractCitations: [
      { phrase: "2.25%", source: "pipeline:boc:V39079", note: "BoC overnight target rate, July 15 2026 FAD decision, via Valet V39079." },
      { phrase: "six straight decisions", source: "card:boc_fad_holds_post_oct_2025_cut", expected_count: 6, note: "Enumerated FAD holds since Oct 29, 2025 cut: Dec 10, Jan 28, Mar 18, Apr 29, Jun 10, Jul 15." },
      { phrase: "2.25 to 3.25% neutral range", source: "card:boc_mpr_neutral_range" },
      { phrase: "calls the rate appropriate", source: "derived", note: "BoC July 15 2026 press release, verbatim: 'Governing Council judges the current policy rate remains appropriate to sustain the economic recovery and bring inflation back to the 2% target.' FLAG: migrate to a source card for the July 15 statement when it lands." },
      { phrase: "2-year GoC yield sits at 2.88%", source: "pipeline:boc:yield_2yr", note: "GoC 2y benchmark yield, July 13 2026 daily close." },
      { phrase: "well above the overnight rate", source: "derived", note: "GoC 2y 2.88% minus overnight target 2.25% = 63 bps; a 2y yield sitting above the overnight rate means the market prices no near-term easing (same claim covered in monetary.astro plate-3)." },
      { phrase: "-138 bps", source: "derived", note: "Canada-US 2y spread, July 13 2026: GoC 2y 2.88% minus UST 2y 4.26% = -138 bps." },
    ],
  },
  {
    slug: "fiscal",
    label: "Fiscal",
    accentVar: "--section-accent-fiscal",
    kicker: "Balance trajectory, operating-balance commitment, and the PBO reclassification fight.",
    headlineQuestion:
      "What is Canada's fiscal policy stance?",
    cadence: "Monthly (Fiscal Monitor) + annual (budgets)",
    // Fiscal Monitor Mar 2026 is the latest monthly issue in the pipeline.
    updatedAt: Date.UTC(2026, 5, 16, 16, 5),
    chartSeriesKey: "fiscal-ytd-balance",
    tileChartKind: "bars",
    heroKicker: "Fiscal Monitor Mar '26",
    heroKickerPrefix: "Fiscal Monitor",
    latestReleasePrefix: "Fiscal Monitor",
    tileLine:
      "The federal deficit reached $55.3B through March, wider than last year.",
    tileLineCitations: [
      { phrase: "$55.3B through March", source: "pipeline:dof:fiscal_monitor", note: "DoF Fiscal Monitor March 2026: FY2025-26 budgetary deficit YTD = -C$55.277bn." },
      { phrase: "wider than last year", source: "pipeline:dof:fiscal_monitor", note: "DoF Fiscal Monitor March 2026: FY2025-26 YTD deficit -C$55.277bn versus FY2024-25 full-year deficit -C$43.154bn in the comparable source series." },
    ],
    prints: [
      {
        key: "fiscal-ytd-balance",
        indicator: "Federal budget balance",
        value: "TK",
        delta: "TK",
        deltaDir: "neutral",
        asOf: "TK",
        spark: [],
      },
      {
        key: "fiscal-debt-gdp",
        indicator: "Federal debt, % of GDP",
        value: "TK",
        delta: "TK",
        deltaDir: "neutral",
        asOf: "TK",
        spark: [],
      },
      {
        key: "fiscal-program-exp-gdp",
        indicator: "Program expenses, % of GDP",
        value: "TK",
        delta: "TK",
        deltaDir: "neutral",
        asOf: "TK",
        spark: [],
      },
      {
        key: "fiscal-interest-rev",
        indicator: "Interest, % of revenue",
        value: "TK",
        delta: "TK",
        deltaDir: "neutral",
        asOf: "TK",
        spark: [],
      },
    ],
    blurb: {
      kind: "last",
      date: "Jun 16, 2026",
      body:
        "Fiscal policy is modestly stimulative. The March Fiscal Monitor put the FY2025-26 deficit at $55.3 billion on a cash basis, while the Spring Economic Update estimate is $66.9 billion, up from $36.3 billion the year before. Debt is still expected to sit near 41.1% of GDP, but public debt charges are taking 10.6% of revenue.",
    },
    abstractCitations: [
      { phrase: "Fiscal policy is modestly stimulative", source: "card:claim_dof_deficit_larger_than_handoff_below_pandemic", note: "Analytical read backed by the deficit widening from C$36.3bn in FY2024-25 to C$66.9bn in FY2025-26." },
      { phrase: "FY2025-26 deficit at $55.3 billion", source: "pipeline:dof:fiscal_monitor", note: "DoF Fiscal Monitor March 2026: FY2025-26 budgetary deficit YTD = -C$55.277bn." },
      { phrase: "Spring Economic Update estimate is $66.9 billion", source: "card:claim_dof_deficit_larger_than_handoff_below_pandemic", note: "DoF SEU April 2026 Annex 1 Table A1.7: FY2025-26 budgetary balance = -C$66.9bn." },
      { phrase: "$36.3 billion the year before", source: "card:claim_dof_deficit_larger_than_handoff_below_pandemic", note: "DoF FRT/SEU: FY2024-25 actual deficit C$36.3bn." },
      { phrase: "41.1% of GDP", source: "pipeline:dof:fiscal_reference_tables", note: "Federal debt, % of GDP, FY2025-26 estimate = 41.1%." },
      { phrase: "10.6% of revenue", source: "pipeline:dof:fiscal_reference_tables", note: "Public debt charges / revenues, FY2025-26 estimate = 10.6%." },
    ],
  },
  {
    slug: "housing",
    label: "Housing",
    accentVar: "--section-accent-housing",
    kicker: "Starts, sales, prices, and household leverage.",
    headlineQuestion:
      "What's the state of Canada's housing market?",
    cadence: "Monthly",
    // CREA May 2026 release is latest available; HPI reference period is April.
    updatedAt: Date.UTC(2026, 6, 10, 10, 24),
    chartSeriesKey: "hpi-yoy",
    heroKicker: "April home prices",
    heroKickerPrefix: "Home prices",
    latestReleasePrefix: "Home prices",
    tileLine:
      "Composite home prices were down 4.0% Y/Y; starts held near 260k.",
    tileLineCitations: [
      { phrase: "4.0%", source: "pipeline:crea:mls_hpi_national", note: "CREA MLS HPI composite, Y/Y, April 2026 = -3.98%." },
      { phrase: "260k", source: "pipeline:statcan:34-10-0158-01", note: "Total housing starts, SAAR 3mma, May 2026 = 259.9k." },
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
      date: "Jul 10, 2026",
      body:
        "Home prices are still falling, but the decline is becoming less severe. The national MLS HPI was down 4.0% year-over-year in April, compared with 4.6% in March. Starts held near 260k on a 3-month average in May, mortgage arrears stayed at 0.28% in April, and affordability improved to 42.3% of household income in Q1.",
    },
    abstractCitations: [
      { phrase: "national MLS HPI was down 4.0% year-over-year in April", source: "pipeline:crea:mls_hpi_national", note: "CREA MLS HPI composite, Y/Y, Apr 2026 = -3.98%." },
      { phrase: "4.6% in March", source: "pipeline:crea:mls_hpi_national", note: "CREA MLS HPI composite, Y/Y, Mar 2026 = -4.60%." },
      { phrase: "Starts held near 260k", source: "pipeline:statcan:34-10-0158-01", note: "Total housing starts, SAAR 3mma, May 2026 = 259.9k." },
      { phrase: "mortgage arrears stayed at 0.28%", source: "pipeline:cba:mortgage_arrears", note: "CBA national residential mortgages in arrears, April 2026 = 0.28%, unchanged from March." },
      { phrase: "42.3% of household income in Q1", source: "pipeline:boc:INDINF_AFFORD_Q", note: "BoC housing affordability index, qualifying payment / income, 2026Q1." },
    ],
  },
  {
    slug: "trade",
    label: "Trade",
    accentVar: "--section-accent-trade",
    kicker: "Exports, imports, and the terms by which Canada sells its work.",
    headlineQuestion:
      "Is Canada's trade pivot working?",
    cadence: "Monthly + event",
    // May merch-trade release landed July 7, 2026.
    updatedAt: Date.UTC(2026, 6, 7, 8, 30),
    chartSeriesKey: "trade-balance",
    heroKicker: "May balance",
    heroKickerPrefix: "Trade balance",
    latestReleasePrefix: "Merchandise trade",
    tileLine:
      "Goods surplus widened to $4.2B in May; US export share rebounded to 70.0%.",
    tileLineCitations: [
      { phrase: "$4.2B in May", source: "pipeline:statcan:12-10-0119-01", note: "Goods trade balance, May 2026 monthly print: +$4,243M, up from +$3,405M in April." },
      { phrase: "70.0%", source: "pipeline:statcan:12-10-0121-01", note: "US share of total Canadian goods exports, May 2026: 70.0%." },
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
      date: "July 7, 2026",
      body:
        "Not really. The trade surplus widened again in May, but the US export share is back at 70.0% and looks little changed from a year ago. The apparent diversification pulse was still mostly gold routed to London; that flow is cooling, and among tariff-exposed sectors aluminum is the only clear shift away from the US while copper leaned more heavily toward it.",
    },
    abstractCitations: [
      { phrase: "surplus widened again in May", source: "pipeline:statcan:12-10-0119-01", note: "Goods trade balance: +C$3,405M in April 2026 and +C$4,243M in May 2026." },
      { phrase: "back at 70.0%", source: "pipeline:statcan:12-10-0121-01", note: "US share of total Canadian goods exports, May 2026: 70.0%." },
      { phrase: "little changed from a year ago", source: "pipeline:statcan:12-10-0121-01", note: "US share of total Canadian goods exports: 69.6% in May 2025 and 70.0% in May 2026." },
      { phrase: "gold routed to London", source: "derived", note: "NAPCS 35 gold/silver/PGM exports to the UK were C$4.6B in May 2026, 82.6% of total NAPCS 35 exports. Source: StatCan 12-10-0182-01." },
      { phrase: "that flow is cooling", source: "pipeline:statcan:12-10-0182-01", note: "NAPCS 35 exports to the UK fell from C$7.8B in March to C$5.6B in April and C$4.6B in May 2026." },
      { phrase: "aluminum is the only clear shift away from the US", source: "derived", note: "Aluminum US share fell from 88.7% in May 2025 to 62.9% in May 2026; steel, softwood, and autos moved away by under five percentage points. Source: StatCan 12-10-0182-01." },
      { phrase: "copper leaned more heavily toward it", source: "derived", note: "Copper US share rose from 88.9% in May 2025 to 90.6% in May 2026. Source: StatCan 12-10-0182-01." },
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
      "How are financial markets affecting Canada?",
    cadence: "Daily (light) + weekly synthesis",
    // Markets data refreshes daily; latest market-data stamp Jul 9, 2026.
    updatedAt: Date.UTC(2026, 6, 9, 23, 0),
    chartSeriesKey: "usdcad",
    heroKicker: "Weekly close",
    // Markets refreshes daily; the kicker phrase "Daily close" + the
    // pipeline's daily-cadence date reads as the current convention
    // ("Daily close Jul 9, 2026").
    heroKickerPrefix: "Daily close",
    latestReleasePrefix: "Daily close",
    tileLine:
      "USDCAD is near 1.417, WTI is back below $72, and the TSX is near 35.2k.",
    tileLineCitations: [
      { phrase: "1.417", source: "pipeline:boc:fxusdcad", note: "USDCAD daily close, July 9 2026 = 1.4169 per BoC Valet FXUSDCAD." },
      { phrase: "$72", source: "pipeline:yahoo:wti", note: "WTI daily close, July 9 2026 = US$71.84." },
      { phrase: "35.2k", source: "pipeline:yahoo:tsx_composite", note: "S&P/TSX Composite daily close, July 9 2026 = 35,200.45." },
    ],
    prints: [
      {
        // Pipeline produces a real value for this row (USDCAD, currently 1.417
        // Jul 9, 2026); loader overwrites canon scaffold with real data before
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
      date: "Jul 9, 2026",
      body:
        "Markets have steadied after the June energy shock. USDCAD closed at 1.4169 on July 9, down 0.1% on the week, while WTI settled at US$71.84, still up 4.6% week-over-week but far below its June spike. Canadian yields moved higher, with the 10-year GoC at 3.56%, and the TSX Composite is near 35.2k.",
    },
    abstractCitations: [
      { phrase: "USDCAD closed at 1.4169 on July 9", source: "pipeline:boc:fxusdcad", note: "USDCAD daily close, July 9 2026 = 1.4169 per BoC Valet FXUSDCAD." },
      { phrase: "down 0.1% on the week", source: "pipeline:boc:fxusdcad", note: "USDCAD weekly change in the site payload, July 9 2026 = -0.1%." },
      { phrase: "WTI settled at US$71.84", source: "pipeline:yahoo:wti", note: "WTI daily close, July 9 2026 = US$71.84." },
      { phrase: "up 4.6% week-over-week", source: "pipeline:yahoo:wti", note: "WTI weekly change in the site payload, July 9 2026 = +4.6%." },
      { phrase: "10-year GoC at 3.56%", source: "pipeline:boc:yield_10yr", note: "GoC 10y benchmark yield, July 8 2026 daily close." },
      { phrase: "TSX Composite is near 35.2k", source: "pipeline:yahoo:tsx_composite", note: "S&P/TSX Composite daily close, July 9 2026 = 35,200.45." },
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

/*
 * Data commentaries — the same-day notes published as PDFs on every major
 * Canadian macro print.
 *
 * Authoring source-of-truth is work/published/commentaries/<slug>.docx
 * (Jay's working folder). The exported .pdf is copied to public/research/commentaries/
 * so it's served at /research/commentaries/<slug>.pdf. Adding a new
 * commentary = (a) export the .pdf, (b) drop it in public/research/commentaries/,
 * (c) add a row to the array below.
 *
 * Ordering: most recent first by publishedAt.
 */
export interface DataCommentary {
  /** URL slug, matches the PDF filename (without .pdf). */
  slug: string;
  /** Section the commentary belongs to (for the section badge and sort). */
  section: SectionSlug;
  /** Headline from the PDF cover. Used as the listing title. */
  title: string;
  /** ISO date string (YYYY-MM-DD) of publication. */
  publishedAt: string;
  /** Path to the served PDF, relative to site root with leading slash. */
  pdfPath: string;
  /**
   * One- or two-sentence preview of the take. Pulled from page 1 of the
   * PDF (the "THE TAKE" block). Surfaces under the row title in the
   * research listings so readers can scan the take before clicking
   * through to the PDF. Plain text, no markup.
   */
  excerpt: string;
  /**
   * Optional correction notice. When present, the commentary wrapper
   * page renders it as a labelled "Correction" note above the take,
   * and the Article JSON-LD dateModified picks up correctedAt.
   * Plain text, no markup.
   */
  correction?: string;
  /** ISO date string (YYYY-MM-DD) the correction was posted. */
  correctedAt?: string;
  /**
   * Optional press coverage of this commentary. Each entry renders as an
   * "In the news" line on the wrapper page: the outlet name links to the
   * article. Only add entries where the outlet quoted or cited this
   * commentary directly.
   */
  coverage?: {
    /** Outlet name as displayed, e.g. "Reuters". */
    outlet: string;
    /** URL of the article that quotes the commentary. */
    url: string;
    /** ISO date string (YYYY-MM-DD) of the article. */
    date: string;
  }[];
}

export const commentaries: DataCommentary[] = [
  {
    slug: "cpi-2026-07-20",
    section: "inflation",
    title: "Inflation falls to 2.8% on lower gas prices.",
    publishedAt: "2026-07-20",
    pdfPath: "/research/commentaries/cpi-2026-07-20.pdf",
    excerpt:
      "Inflation cooled to 2.8% in June as gasoline prices fell 10% on the month following an interim Middle East ceasefire, pulling both of the Bank of Canada's core measures below 2%. The relief looks temporary: the conflict has since reignited and oil prices are already back up $14 a barrel from their lows.",
  },
  {
    slug: "boc-2026-07-15",
    section: "monetary",
    title: "Bank of Canada stays on hold at 2.25%.",
    publishedAt: "2026-07-15",
    pdfPath: "/research/commentaries/boc-2026-07-15.pdf",
    excerpt:
      "The Bank of Canada held its policy rate at 2.25% for the sixth consecutive meeting and called the rate appropriate. Officials sounded more upbeat about the economy and more comfortable with their stance than in June, with both main risks easing.",
  },
  {
    slug: "lfs-2026-07-10",
    section: "labour",
    title: "Canada adds 18k jobs as youth market improves.",
    publishedAt: "2026-07-10",
    pdfPath: "/research/commentaries/lfs-2026-07-10.pdf",
    excerpt:
      "Young people are starting to find jobs again in what's been a tough summer market. The World Cup effect may also be showing up, with much of the hiring happening in the hospitality industry.",
  },
  {
    slug: "trade-2026-07-07",
    section: "trade",
    title: "Canada posts widest trade surplus in four years.",
    publishedAt: "2026-07-07",
    pdfPath: "/research/commentaries/trade-2026-07-07.pdf",
    excerpt:
      "May's report is a positive terms of trade story: Canada is getting a better deal from the world, selling at higher prices and buying at lower prices. Export diversification is still limited, with US-bound exports back to 70%.",
  },
  {
    slug: "gdp-2026-06-30",
    section: "output",
    title: "Canada's economy grows 0.5%, lifted by oil sands.",
    publishedAt: "2026-06-30",
    pdfPath: "/research/commentaries/gdp-2026-06-30.pdf",
    excerpt:
      "Canada's economy expanded 0.5% in April, its fastest pace in almost a year, cutting through the recession talk that followed last month's quarterly data. But more than half the gain came from a temporary rebound in oil sands extraction, and advance tracking already points to the bounce fizzling out in May.",
  },
  {
    slug: "cpi-2026-06-22",
    section: "inflation",
    title: "Inflation hits 3.2% as gasoline climbs.",
    publishedAt: "2026-06-22",
    pdfPath: "/research/commentaries/cpi-2026-06-22.pdf",
    excerpt:
      "Inflation broke out of the Bank of Canada's control band as gas prices rose to levels not seen since Russia invaded Ukraine. Still, with an Iran peace deal in the works and energy markets pulling back, the bank will be able to argue that it should continue to look through the shock.",
  },
  {
    slug: "retail-2026-06-19",
    section: "output",
    title: "Retail sales rise 0.5% as gas prices still lead.",
    publishedAt: "2026-06-19",
    pdfPath: "/research/commentaries/retail-2026-06-19.pdf",
    excerpt:
      "April data tells the same story as March: Canadians look like they're spending more, but they're mostly paying more for gasoline. Looking ahead, Canadians will start to see relief in prices at the pump, giving them a boost in overall spending power.",
  },
  {
    slug: "boc-2026-06-10",
    section: "monetary",
    title: "The Bank of Canada holds at 2.25% and keeps its guidance.",
    publishedAt: "2026-06-10",
    pdfPath: "/research/commentaries/boc-2026-06-10.pdf",
    excerpt:
      "The Bank of Canada is getting closer to ending its hold, and will likely not wait longer than September to pick a direction. Officials were clear that the most important indicators to watch are core inflation, the share of the CPI basket running above 3%, and medium-to-long-term inflation expectations.",
    coverage: [
      {
        outlet: "Financial Post",
        url: "https://financialpost.com/news/bank-of-canada-end-interest-rate-pause",
        date: "2026-06-11",
      },
    ],
  },
  {
    slug: "trade-2026-06-09",
    section: "trade",
    title: "Oil exports boost Canada's trade surplus.",
    publishedAt: "2026-06-09",
    pdfPath: "/research/commentaries/trade-2026-06-09.pdf",
    excerpt:
      "Canada is selling more to the world, with exports hitting an all-time high of C$75 billion in April. Still, the month's export gains were driven by higher sales to the US, going against Prime Minister Carney's aim to diversify trade.",
    coverage: [
      {
        outlet: "Financial Post",
        url: "https://financialpost.com/news/economy/biggest-knock-canada-trade-carney-economic-pillars",
        date: "2026-06-09",
      },
    ],
  },
  {
    slug: "boc-preview-june-2026",
    section: "monetary",
    title: "The Bank of Canada is set to hold in June.",
    publishedAt: "2026-06-08",
    pdfPath: "/research/commentaries/boc-preview-june-2026.pdf",
    excerpt:
      "We expect the Bank to hold for a fifth straight meeting on Wednesday. Looking further out, markets are pricing too many hikes: our estimate of the Bank's internal rate path settles 25 to 50 basis points below what the market expects.",
  },
  {
    slug: "jobs-may-2026",
    section: "labour",
    title: "Blowout Canada jobs report shows 88k gain.",
    publishedAt: "2026-06-05",
    pdfPath: "/research/commentaries/jobs-may-2026.pdf",
    excerpt:
      "Today's jobs data showed strength all across the board, making up most of the employment shortfall from the start of the year. This should dispel much of the recession talk we've heard since last week's GDP release.",
    correction:
      "An earlier version of this commentary said May's gain returned employment to an all-time high, completely making up the shortfall from the start of the year. Employment is at its highest level this year but remains about 25,000 short of the December 2025 record. The commentary and PDF have been updated.",
    correctedAt: "2026-06-05",
    coverage: [
      {
        outlet: "Reuters",
        url: "https://www.reuters.com/business/world-at-work/canada-adds-87800-jobs-jobless-rate-down-66-beating-may-estimates-2026-06-05/",
        date: "2026-06-05",
      },
    ],
  },
  {
    slug: "two-quarter-rule",
    section: "output",
    title: "Two negative quarters of real GDP growth is just a rule of thumb.",
    publishedAt: "2026-06-01",
    pdfPath: "/research/commentaries/two-quarter-rule.pdf",
    excerpt:
      "The media often defines a recession as two consecutive quarters of negative real GDP growth. Since 1961 that rule has fired eight times — but Canada has had only five official recessions.",
  },
  {
    slug: "gdp-march-q1-2026",
    section: "output",
    title: "Economy edges down 0.1% annualized in first quarter.",
    publishedAt: "2026-05-29",
    pdfPath: "/research/commentaries/gdp-march-q1-2026.pdf",
    excerpt:
      "Sounding the alarm on a so-called 'technical recession' is premature, but further economic weakness this year could force the Bank of Canada back into easing mode.",
  },
  {
    slug: "retail-march-2026",
    section: "output",
    title: "Retail sales jump 0.9%, driven by higher gas prices.",
    publishedAt: "2026-05-22",
    pdfPath: "/research/commentaries/retail-march-2026.pdf",
    excerpt:
      "The Canadian consumer showed signs of weakness in March, with both core sales and volumes declining. The headline jump reflects higher prices at the pump, not a genuine increase in demand.",
  },
  {
    slug: "cpi-april-2026",
    section: "inflation",
    title: "Inflation rose to 2.8% on higher gasoline prices.",
    publishedAt: "2026-05-19",
    pdfPath: "/research/commentaries/cpi-april-2026.pdf",
    excerpt:
      "Headline wasn't so bad given the energy shock. Cores ticked down two-tenths each. The Bank should be able to stay on hold.",
  },
];

/**
 * Slug-derived path to a commentary's cover image (page 1 of the PDF
 * rendered as PNG). The splash showcase 03 perspective stack consumes
 * this. Convention: `public/showcase/commentary-<slug>-cover.png`.
 */
export function commentaryCoverPath(c: DataCommentary): string {
  return `/showcase/commentary-${c.slug}-cover.png`;
}

/**
 * Slug-derived path to a commentary's page-2 image (the chart + analysis
 * page rendered as PNG). Used as the back-sheet of the splash perspective
 * stack. Convention: `public/showcase/commentary-<slug>-page2.png`.
 */
export function commentaryPage2Path(c: DataCommentary): string {
  return `/showcase/commentary-${c.slug}-page2.png`;
}

/**
 * Returns commentaries that belong to a given section slug, sorted
 * newest-first. Used by section pages (when Phase 3 cross-links land)
 * to surface "Recent commentaries on [section]" footers.
 */
export function getCommentariesBySection(
  slug: SectionSlug,
): DataCommentary[] {
  return commentaries
    .filter((c) => c.section === slug)
    .sort((a, b) => b.publishedAt.localeCompare(a.publishedAt));
}

/**
 * The most-recently-published commentary. Splash showcase 03 consumes
 * this so the front-page promo auto-rotates as new pieces land. Returns
 * `null` only if the commentaries array is empty (shouldn't happen in
 * production but guarded for safety).
 */
export function latestCommentary(): DataCommentary | null {
  if (commentaries.length === 0) return null;
  return [...commentaries].sort((a, b) =>
    b.publishedAt.localeCompare(a.publishedAt),
  )[0];
}

export const deepDives: DeepDive[] = [
  {
    slug: "mortgage-renewal-wall",
    section: "housing",
    title: "The mortgage renewal wall has peaked",
    deck:
      "The 2026 renewal cohort is the largest single tranche in the stack. We map where the residual transmission lands through 2027.",
    publishedAt: "2026-05-08",
    lastUpdated: "TK",
    // Latest dated source in the data-stamp paragraph is the BoC April 2026
    // MPR (April 29, 2026); CREA MLS HPI April 2026 ties on month but the
    // MPR release date is the most specific anchor.
    dataVintage: "2026-04-29",
    draftPath: "editorial/drafts/deepdive_pillar_a_mortgage_renewal_wall_v1.md",
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
    section: "monetary",
    title: "The BoC-Fed divergence is wide, but FX is not binding",
    deck:
      "The policy spread sits at the 8th percentile of three decades; USDCAD is at the 67th and strengthening. The binding constraint is not the loonie but the expectations chain.",
    publishedAt: "2026-05-10",
    lastUpdated: "2026-05-10",
    dataVintage: "2026-05-11",
    draftPath: "editorial/drafts/deepdive_pillar_b_boc_fed_divergence_v1.md",
        pillar: "B",
    status: "drafted",
    draftStatus: "draft",
  },
  {
    slug: "per-capita-output",
    section: "labour",
    title: "The per-capita output gap is a denominator story",
    deck:
      "The headline labour print is flattering. The per-capita series is not. We separate the population-deceleration story from the cyclical weakness story.",
    publishedAt: "2026-05-09",
    lastUpdated: "2026-05-09",
    dataVintage: "2026-05-11",
    draftPath: "editorial/drafts/deepdive_pillar_e_per_capita_output_v1.md",
        pillar: "E",
    status: "drafted",
    draftStatus: "draft",
  },
  {
    slug: "us-tariff-repricing",
    section: "trade",
    title: "Canada's trade pivot that wasn't",
    deck:
      "Strip out gold and most of the apparent pivot is gone. Among the tariffed sectors, only aluminum managed to meaningfully diversify. Autos haven't dodged the hit at all.",
    publishedAt: "2026-05-11",
    lastUpdated: "2026-05-11",
    dataVintage: "2026-05-11",
    draftPath: "editorial/drafts/deepdive_trade_tariffs_v1.md",
        status: "drafted",
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
    "The story now is the price of oil coming down. With the Strait of Hormuz standoff easing, crude has retreated. That cuts two ways for Canada. It slows down the oil and gas extraction that drove the recent pickup in growth, but it also reduces the inflation pressure coming from gasoline.",
  citations: [
    { phrase: "the price of oil coming down", source: "derived", note: "NYMEX WTI front-month (CL=F, data/raw/wti.csv): $84.88 Jun 12 2026 falling to $70.35 Jun 29, down 17.1% on the month (peaked ~$108 mid-May; the slide tracks the Strait of Hormuz de-escalation)." },
    { phrase: "the Strait of Hormuz standoff easing", source: "derived", note: "US-Iran MOU to end the war/strait blockade signed Jun 17 2026; US Navy JMIC widened the Hormuz transit route Jun 27 (en.wikipedia.org/wiki/2026_Strait_of_Hormuz_crisis; Al Jazeera, Jun 2026). Fragile de-escalation — Iran briefly reclosed the strait Jun 20 — net late-June trajectory is easing, not resolved." },
    { phrase: "crude has retreated", source: "derived", note: "Same WTI series: front-month down from the mid-June high to ~$70 by end-June 2026." },
    { phrase: "oil and gas extraction that drove the recent pickup in growth", source: "pipeline:statcan:36-10-0434-01", note: "Mining, quarrying, and oil and gas extraction led April 2026 monthly real GDP (+0.5% m/m), up 2.9% — its largest gain since Feb 2024; oil sands extraction rebounded 6.6% (StatCan Daily dq260630a, Table 36-10-0434-01)." },
    { phrase: "reduces the inflation pressure coming from gasoline", source: "derived", note: "Gasoline drove the recent CPI breakout (May 2026 all-items CPI 3.2%, gasoline-led); a lower crude price relieves forward gasoline and headline-CPI pressure." },
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
    "Sibley Creek - Canadian macroeconomic indicators and analysis. Independent research on GDP, inflation, labour, monetary policy, fiscal policy, housing, trade, and markets.",
  locale: "en-CA",
  url: "https://sibleycreek.ca",
};
