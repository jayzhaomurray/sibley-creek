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
    // Most recent monthly GDP print released Apr 30, 2026 (Feb 2026 reference period).
    updatedAt: Date.UTC(2026, 3, 30, 8, 30),
    chartSeriesKey: "gdp-yoy",
    heroKicker: "March & Q1 GDP",
    heroKickerPrefix: "GDP",
    latestReleasePrefix: "Monthly GDP by industry",
    tileLine:
      "Growth slowed to 0.4% in March, driven by the goods sector.",
    tileLineCitations: [
      { phrase: "0.4% in March", source: "pipeline:statcan:gdp_monthly_yoy", note: "Monthly real GDP y/y: 0.41% Mar 2026, down from 0.78% Feb 2026 (data/processed/gdp_monthly_yoy.csv)." },
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
      date: "May 29, 2026",
      body:
        "Stalled at the headline, but the composition is more nuanced. Real GDP edged down 0.1% annualized in Q1 and slipped another 0.1% in March, leaving year-over-year growth at just 0.4%. The Q1 drag came from a surge in imports and contracting government spending — not from collapsing household demand. Calls of a technical recession remain premature.",
    },
    abstractCitations: [
      { phrase: "0.1% annualized in Q1", source: "pipeline:statcan:36-10-0104-01", note: "Q1 2026 real GDP quarterly q/q SAAR." },
      { phrase: "0.1% in March", source: "pipeline:statcan:36-10-0434-01", note: "March 2026 monthly real GDP m/m." },
      { phrase: "0.4%", source: "pipeline:statcan:36-10-0434-01", note: "Real GDP Y/Y, March 2026 monthly print." },
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
    // Most recent LFS landed Jun 5, 2026 (May 2026 reference period).
    updatedAt: Date.UTC(2026, 5, 5, 8, 30),
    chartSeriesKey: "unrate",
    heroKicker: "May LFS",
    heroKickerPrefix: "LFS",
    latestReleasePrefix: "LFS",
    tileLine:
      "Hiring snapped back in May and unemployment fell to 6.6%.",
    tileLineCitations: [
      { phrase: "Hiring snapped back in May", source: "pipeline:statcan:14-10-0287-01", note: "LFS employment change, SA, May 2026: +87.8k m/m (21.1215M from 21.0337M), largest gain since Dec 2024." },
      { phrase: "6.6%", source: "pipeline:statcan:14-10-0287-01", note: "LFS unemployment rate, SA, May 2026." },
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
      date: "Jun 5, 2026",
      body:
        "Not in May — the headline broke the loosening story. Employment jumped 87,800, the fastest gain in a year and a half, lifting jobs to their highest level this year — still shy of December's peak — and pulling the unemployment rate down to 6.6% from 6.9%. Slack clears slowly, so it remains the lagging piece, but the cyclical alarm that followed last week's GDP print now reads overdone.",
    },
    abstractCitations: [
      { phrase: "Employment jumped 87,800", source: "pipeline:statcan:14-10-0287-01", note: "LFS employment change, SA, May 2026: 21.1215M minus 21.0337M = +87.8k." },
      { phrase: "fastest gain in a year and a half", source: "derived", note: "Enumerated LFS m/m employment changes: last gain >= +87.8k was Dec 2024 (+92.7k), 17 months before May 2026." },
      { phrase: "highest level this year — still shy of December's peak", source: "derived", note: "May 2026 employment 21.1215M exceeds every other 2026 month (Jan 21.1212M the next highest) but sits ~24.5k below Dec 2025 (21.146M). Per the published correction notice: not an all-time high." },
      { phrase: "down to 6.6% from 6.9%", source: "pipeline:statcan:14-10-0287-01", note: "LFS unemployment rate, SA: May 6.6%, April 6.9%." },
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
      "BoC parked at the floor of neutral, 150 bps below the Fed and holding.",
    tileLineCitations: [
      { phrase: "floor of neutral", source: "card:boc_mpr_neutral_range", note: "BoC stated nominal neutral range 2.25-3.25%; overnight at 2.25% sits at the floor." },
      { phrase: "150 bps below the Fed", source: "derived", note: "BoC overnight 2.25% minus Fed upper bound 3.75% = -150 bps." },
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
      date: "Jun 10, 2026",
      body:
        "On hold. The Bank of Canada has stayed at 2.25% through five straight decisions, sitting at the floor of its 2.25 to 3.25% neutral range. Activity is softening at the same time the Iran-war oil shock is feeding energy inflation. The call hinges on persistence — how long the Strait of Hormuz stays closed, and whether the shock seeps into expectations.",
    },
    abstractCitations: [
      { phrase: "2.25%", source: "pipeline:boc:V39079", note: "BoC overnight target rate, Apr 29 2026 FAD decision, via Valet V39079." },
      { phrase: "five straight decisions", source: "card:boc_fad_holds_post_oct_2025_cut", expected_count: 5, note: "Enumerated FAD holds since Oct 29, 2025 cut: Dec 10, Jan 28, Mar 18, Apr 29, Jun 10." },
      { phrase: "2.25 to 3.25% neutral range", source: "card:boc_mpr_neutral_range" },
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
    // Fiscal Monitor Feb 2026 (released ~Apr 24 2026) is the primary event.
    updatedAt: Date.UTC(2026, 3, 24, 8, 30),
    chartSeriesKey: "fiscal-ytd-balance",
    tileChartKind: "bars",
    heroKicker: "Fiscal Monitor Feb '26",
    heroKickerPrefix: "Fiscal Monitor",
    latestReleasePrefix: "Fiscal Monitor",
    tileLine:
      "The federal deficit is running wider this fiscal year than last.",
    tileLineCitations: [
      { phrase: "running wider this fiscal year than last", source: "card:dof_fiscal_monitor_debt_service_share", note: "DoF Fiscal Monitor Feb 2026: FY2025-26 budgetary deficit ran to -$25.5bn through February, ahead of the FY2024-25 year-to-date pace; the running FY-to-date deficit exceeds the prior fiscal year across the months the sparkline shows." },
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
      date: "Jun 4, 2026",
      body:
        "Fiscal policy is modestly stimulative. Carney's government is running a larger deficit than he inherited, but nothing near pandemic-level extremes. The government has split the budget in two and says it will balance the operating books by 2028-29. The PBO disputes this, suggesting the government has misclassified C$94 billion in operating expenses as capital investment.",
    },
    abstractCitations: [
      { phrase: "Fiscal policy is modestly stimulative", source: "card:claim_dof_deficit_larger_than_handoff_below_pandemic", note: "Analytical read backed by the deficit widening from C$36.3bn in FY2024-25 to C$66.9bn in FY2025-26." },
      { phrase: "larger deficit than he inherited", source: "card:claim_dof_deficit_larger_than_handoff_below_pandemic", note: "DoF FRT/SEU: FY2024-25 actual deficit C$36.3bn; FY2025-26 forecast deficit C$66.9bn." },
      { phrase: "nothing near pandemic-level extremes", source: "card:claim_dof_deficit_larger_than_handoff_below_pandemic", note: "DoF FRT/SEU: FY2025-26 forecast deficit C$66.9bn vs FY2020-21 pandemic deficit C$327.7bn." },
      { phrase: "balance the operating books by 2028-29", source: "card:claim_dof_operating_surplus_2028_29", note: "DoF SEU April 2026 Annex 1 Table A1.5: day-to-day operating balance crosses zero in FY2028-29 (+$0.9bn)." },
      { phrase: "PBO disputes this", source: "card:claim_pbo_anchor_cannot_verify", note: "PBO May 2026 fiscal-anchor assessment says it is not possible to advise in depth on how the updates support the government's assertion that the operating-balance anchor remains in balance." },
      { phrase: "suggesting the government has misclassified C$94 billion in operating expenses as capital investment", source: "card:claim_pbo_94bn_reclassified", note: "PBO RP-2526-017-S: PBO's capital total is C$217.3bn versus Budget 2025's C$311.5bn over FY2024-25 to FY2029-30, a roughly C$94bn wedge." },
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
      "Is Canada's trade pivot working?",
    cadence: "Monthly + event",
    // March merch-trade release landed May 5, 2026.
    updatedAt: Date.UTC(2026, 4, 5, 8, 30),
    chartSeriesKey: "trade-balance",
    heroKicker: "March balance",
    heroKickerPrefix: "Trade balance",
    latestReleasePrefix: "Merchandise trade",
    tileLine:
      "Goods balance flipped to $1.8B surplus in March; US export share fell to 66.1%.",
    tileLineCitations: [
      { phrase: "$1.8B surplus in March", source: "pipeline:statcan:12-10-0119-01", note: "Goods trade balance, March 2026 monthly print: +$1,779M (swung from -$5,113M deficit in February)." },
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
        "Not really. The US export share dropped from three quarters to two thirds in a year, but most of that is gold being routed to London at record prices; strip it out and the underlying share is down about three percentage points. Among the tariffed sectors, only aluminum has meaningfully diversified — autos lost over a billion dollars in US sales with almost no offset elsewhere.",
    },
    abstractCitations: [
      { phrase: "from three quarters to two thirds in a year", source: "pipeline:statcan:12-10-0121-01", note: "US share of total Canadian goods exports: 74.4% (Mar 2025) ≈ three quarters; 66.1% (Mar 2026) ≈ two thirds." },
      { phrase: "gold being routed to London at record prices", source: "derived", note: "NAPCS 35 (unwrought gold, silver, PGM) total exports March 2026: C$8.0B, of which C$7.8B (97.4%) to UK. Gold futures (GC=F) May 2026 monthly close ~$4,676/oz, a record. Sources: StatCan 12-10-0182-01 + Yahoo Finance GC=F." },
      { phrase: "the underlying share is down about three percentage points", source: "derived", note: "Ex-gold US share: Mar 2025 = 77.7%; Mar 2026 = 74.6%; Δ = -3.1pp. NAPCS 35 stripped from both numerator and denominator. Sources: StatCan 12-10-0121-01 + 12-10-0182-01." },
      { phrase: "only aluminum has meaningfully diversified", source: "derived", note: "Aluminum (NAPCS 32+38) US share: Mar 2025 = 96.9%; Mar 2026 = 86.0%; Δ = -10.9pp. Steel, softwood, cars each shed under 5pp. Source: StatCan 12-10-0182-01." },
      { phrase: "autos lost over a billion dollars in US sales with almost no offset elsewhere", source: "derived", note: "NAPCS 81 (passenger cars and light trucks) Δ exports Mar 2026 vs Mar 2025: US -C$1,247M; non-US +C$42M. Source: StatCan 12-10-0182-01." },
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
      "USDCAD closed the week at 1.369 as the Canada-US 2y spread held near -98 bps.",
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
      date: "May 13, 2026",
      body:
        "USDCAD has spent the past month inside a 1.36 to 1.38 band, closing at 1.3686 on May 8. The 10y GoC yield is at 3.53%, with the front end up roughly 10 bps over the past two weeks. WTI round-tripped to a US$109.76 peak on May 4 and settled at US$101.12 on May 13; the TSX Composite is near 34,000.",
    },
    abstractCitations: [
      { phrase: "USDCAD has spent the past month inside a 1.36 to 1.38 band", source: "pipeline:boc:fxusdcad", note: "USDCAD daily-close range across April 13 to May 12, 2026: 1.357 to 1.388 per BoC Valet FXUSDCAD." },
      { phrase: "closing at 1.3686 on May 8", source: "pipeline:boc:fxusdcad", note: "USDCAD daily close, May 8, 2026 per BoC Valet FXUSDCAD." },
      { phrase: "10y GoC yield is at 3.53%", source: "pipeline:boc:yield_10yr", note: "GoC 10y benchmark yield, latest daily close." },
      { phrase: "front end up roughly 10 bps over the past two weeks", source: "pipeline:boc:yield_2yr", note: "GoC 2y up roughly 10 bps over the trailing 2-week window (~2.83 to 2.93)." },
      { phrase: "WTI round-tripped to a US$109.76 peak on May 4", source: "pipeline:fred:DCOILWTICO", note: "WTI spot daily-close peak in early May 2026: 109.76 on May 4. Subsequent close on May 13 at 101.12 returned the price to early-month levels." },
      { phrase: "settled at US$101.12 on May 13", source: "pipeline:fred:DCOILWTICO", note: "WTI spot, May 13, 2026 daily close." },
      { phrase: "TSX Composite is near 34,000", source: "pipeline:yahoo:tsx_composite", note: "S&P/TSX Composite daily close, May 12 2026 (33,994.87), via Yahoo Finance ^GSPTSE." },
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
    "Stuck below its potential, on two fronts at once. Cyclically, growth is running at 0.4% as the job market slackens and core inflation sits at target. Gas prices are high due to the closing of the Strait of Hormuz. Structurally, immigration reforms and tariffs are forcing a realignment. Population growth has levelled off, which is showing up clearly in the housing market, while new exports are narrowly redirecting away from the US.",
  citations: [
    { phrase: "0.4%", source: "pipeline:statcan:36-10-0434-01", note: "Real GDP by industry, Y/Y, March 2026 monthly print." },
    { phrase: "the job market slackens", source: "derived", note: "LFS data: unemployment rate has drifted up to 6.9% (April 2026) with aggregate hours worked negative year-over-year; intensive margin is leading the loosening." },
    { phrase: "core inflation sits at target", source: "derived", note: "Preferred cores (CPI-trim, CPI-median) near 2% in April 2026; CPI-trim 2.2%, CPI-median 2.3%." },
    { phrase: "Gas prices are high due to the closing of the Strait of Hormuz", source: "card:iran_oil_conflict_2026_05", note: "User-confirmed Tier B card: Strait of Hormuz impasse -> global oil -> Canadian gasoline transmission (CIBC Week Ahead May 18-22 2026, multi-author)." },
    { phrase: "immigration reforms", source: "card:ircc_levels_plan_2026_2028", note: "IRCC 2026-2028 Immigration Levels Plan (announced November 2025) caps permanent residents at 380,000 per year with sub-caps on international students and temporary workers. Card in _pending/per-capita-output/ — gate blocks until user-approved." },
    { phrase: "tariffs", source: "card:pp_section_232_steel_alum_50pct", note: "US Section 232 measures (50% steel and aluminum since June 2025, copper added April 2026); broader tariff stack and USMCA review covered in trade section." },
    { phrase: "Population growth has levelled off", source: "pipeline:statcan:17-10-0009-01", note: "Quarterly population Y/Y peaked at 3.18% in Q2 2024 and printed -0.25% in Q1 2026 per StatCan demographic estimates." },
    { phrase: "new exports are narrowly redirecting away from the US", source: "derived", note: "US share of Canadian merchandise exports moved from ~76% (2024 average) to ~66% (March 2026) per StatCan 12-10-0121-01 — the shift is real but concentrated in gold." },
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
