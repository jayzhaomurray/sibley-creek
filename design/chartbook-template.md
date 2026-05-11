# Chartbook Template

Status: v1.0. Author: art-director.
Last updated: 2026-05-11.

This document specifies the visual template for **per-section pages** in
the Vignelli register: the page a Bay Street allocator opens at 7am to see
where one section of the Canadian economy stands.

It replaces the legacy `design/basics-layer-template.md` (v0.x). The
v0.x template was authored against the prior FT / warm-paper / serif
canon; the chartbook template below reflects the production reality in
`src/components/section/SectionPageHeader.astro` and
`src/components/section/ChartbookUnit.astro`.

All tokens cited here are defined in `design/design-system.md`
(Appendix A). Where this template hand-codes a value (e.g. a font size in
clamp(), an opacity for a separator pipe), the call site documents the
choice and the token surface remains the source of truth for colors,
weights, and families.

---

## 0. Reference lineage

The chartbook unit anatomy descends from the **Knoll furniture catalogues
of the 1950s through 1970s** (Vignelli Associates), in which each page
followed a fixed grammar: a plate number, a product name, a one-line
caption, a single photographic plate, and a source line. The reader
turned the catalogue and knew, without thinking, where to look. We
repeat that grammar for indicator plates: a plate number, an indicator
name, a one-line headline, a chart plate (with adjacent interpretation
prose), and a source line.

The section page header descends from the **Vignelli Unimark NYC Subway
specification (1972)**: a kicker that places the reader in the system
(`SECTION 3 OF 7 | INFLATION`), a headline statement of what this
section asks, a lede that frames it for the day, and a plate index that
lets the reader jump directly to a specific indicator without scrolling.

Mueller-Brockmann's grid system anchors the spacing: every margin, gap,
and rhythm is a multiple of 4px from the `--s-*` scale.

---

## 1. Page structure (top to bottom)

```
+------------------------------------------------------------+
| [site masthead]                                             |  VignelliMasthead.astro
| --------------------------------------------------------    |  1px hairline
+------------------------------------------------------------+
| [section page header]                                       |  SectionPageHeader.astro
|   - kicker row                                              |
|   - headline question + latest-release stamp                |
|   - lede                                                    |
|   - plate index                                             |
|   ====================================================      |  2px hairline (section close)
+------------------------------------------------------------+
| [chartbook stack]                                           |
|   ChartbookUnit #1 (Plate 01)                               |  ChartbookUnit.astro
|   --------------------------------------------------------  |  1px hairline (between units)
|   ChartbookUnit #2 (Plate 02)                               |
|   --------------------------------------------------------  |
|   ...                                                       |
|   ChartbookUnit #N (Plate 0N)                               |
|   (last unit drops its bottom rule; page footer closes)     |
+------------------------------------------------------------+
| [page footer]                                               |
+------------------------------------------------------------+
```

A section page is exactly: masthead + header band + stack of chartbook
units + footer. No mid-page essay sections. No hero panel between the
header and the units. Prose lives **inside** a unit (as the
interpretation paragraph adjacent to the chart) or **above** the stack
(as the lede in the header). It does not flow between units.

---

## 2. Section page header band

Production component: `src/components/section/SectionPageHeader.astro`.

### Anatomy

```
RESEARCH NOTE | SECTION 3 OF 7 | INFLATION             <- kicker row, 10px micro-caps 600
============================================================    1px black hairline top

Is Canadian inflation              LATEST RELEASE      <- headline question (800, clamp 28-44px)
returning to target?               April CPI, released   + latest-release stamp (right)
                                   May 14, 2026

A 2- to 3-sentence lede that frames the section for the day.    <- lede (Manrope 200 / 17px)
Sits below the headline at max-width 64ch.

PLATE INDEX                                                     <- plate index
+--------+--------+--------+--------+--------+--------+
| 01     | 02     | 03     | 04     | 05     | 06     |
| Title  | Title  | Title  | Title  | Title  | Title  |
+--------+--------+--------+--------+--------+--------+

============================================================    2px black hairline (section close)
```

### Kicker row

Three tokens, left-aligned, separated by `|` pipe glyphs in pure ink at
`opacity: 0.32`.

- **Publication token:** `RESEARCH NOTE` (or `SIBLEY CREEK`, depending
  on the publication context the parent passes in). Manrope 600 micro-
  caps 10px, `0.22em` tracking, pure ink.
- **Section position token:** `SECTION` + numeral + `of 7`. The numeral
  itself renders in `--accent` (signal red) at 800 weight - this is
  the brand-signal moment in the kicker. The surrounding words are
  pure ink 600.
- **Section name token:** the section name in uppercase, Manrope **800**
  micro-caps (heavier than the other tokens so the eye lands on which
  section you are in). `0.22em` tracking. Pure ink.

The row sits 18px from the top of the header and 18px above the
hairline rule that opens the headline band.

### Headline band: question + latest-release stamp

Sits in a single flex row, baseline-aligned, justified between, with a
1px black hairline above and 18px padding-top.

- **Headline question (h1):** Manrope **800**, size `clamp(28px, 4vw,
  44px)`, line-height 1.05, letter-spacing `-0.018em`, pure ink. Max
  width 22ch so the line breaks editorially. The question is the
  section's editorial purpose statement, e.g. `Is Canadian inflation
  returning to target?` or `Is the Canadian labour market still
  loosening?`. **No period at the end of a question mark question; no
  full stop on a declarative statement that wraps to a single line.**
  Wording owned by `writer` per the editorial canon; visual treatment
  is the 800-weight, tight-tracked typographic event that opens the
  section.
- **Latest-release stamp (right):** two stacked elements -
  - Label: `LATEST RELEASE` in Manrope 600 micro-caps 10px, `0.22em`
    tracking, pure ink.
  - Body: e.g. `April CPI, released May 14, 2026` in Plex Mono 400 at
    12px, line-height 1.3, tabular nums, pure ink. Max width 32ch.
  Right-aligned. Drops to left-aligned and stacks below the headline
  at `<= 720px` viewport.

### Lede

A 2- to 3-sentence paragraph that frames the section for the day.

- Manrope **200** (ExtraLight) at 17px, line-height 1.55, pure ink.
  Max width 64ch.
- Sits 18px below the headline band.
- The Vignelli weight-contrast moment of the header: an 800 headline
  against a 200 lede. The reader's eye reads "headline -> lede -> plate
  index" as a hierarchy carried purely by weight.

### Plate index

A 6- or 8-cell horizontal grid (one cell per plate / chartbook unit on
this page). Each cell links to the corresponding `#plate-N` anchor.

- 1px black hairline rules at top and bottom of the index; 1px black
  vertical rules between cells (right border on each cell except the
  last).
- Each cell is a `<a>` covering its entire box, with:
  - Plate number: Plex Mono 400 at 11px, `0.12em` tracking, pure ink.
    Tabular nums.
  - Plate label: Manrope 600 at 11px, line-height 1.2, `0.04em`
    tracking, pure ink. Not uppercase.
- Cell padding: 10px vertical, 12px horizontal.
- **Hover:** entire cell background transitions to `--ink` (pure
  black), text inverts to `--paper` (white). 80ms linear. The hover
  treatment is the only place on a section page where a Vignelli-style
  inverse (white on black) appears - it reads as "you can click here."
- **Focus:** 2px accent-red outline at `outline-offset: -2px` (inset)
  so the focus ring doesn't extend past the cell.

### Closing rule

A 2px black hairline 28px below the plate index. Closes the header band
and visually separates it from the chartbook stack below. The 2px
weight (heavier than the 1px hairlines used elsewhere) is the only
"section-close" rule weight in the system; it marks transitions
between major page bands.

### Mobile

At `<= 720px`:
- The headline band flex direction switches to column; the latest-
  release stamp drops below the headline and left-aligns.
- The plate index becomes a vertical stack; the vertical rules between
  cells become horizontal rules between rows.

---

## 3. Chartbook unit

Production component: `src/components/section/ChartbookUnit.astro`.

Each chartbook unit is one plate: an indicator, a chart, an
interpretation paragraph, and a source line. Units are stacked
vertically with 1px black hairlines between them; the last unit drops
its bottom hairline.

### Anatomy

```
PLATE 01 | Headline real GDP, m/m                AS OF  Mar 2026; released May 1, 2026
                                                                                       <- eyebrow row
                                                                                          (1px hairline below)
Monthly GDP rose 0.2% in March, in line with consensus.                                <- title row (h2, 800, clamp 22-30)

+--------------------------------------+  +----------------------------+
|                                      |  | Interpretation paragraph,  |
|                                      |  | 2-4 sentences. Manrope     |
|   [Chart plate, 1px black frame,     |  | 400 at 16px. Inline        |
|    1.5fr column on >= 900px ]        |  | <strong> 600 weight on     |
|                                      |  | key numbers.               |
|                                      |  |                            |
+--------------------------------------+  +----------------------------+
                                                                                       <- 2-col body grid

SOURCE:  Statistics Canada Table 36-10-0434-01.                                        <- source line (Plex Mono 11px,
                                                                                          micro-caps prefix)

============================================================                            1px hairline (next unit boundary)
```

### Eyebrow row

A single line, justified between left (plate stamp + indicator name)
and right (`AS OF` stamp).

**Left cluster:**
- **Plate stamp:** `PLATE 01` rendered as:
  - The word `PLATE` in Manrope 600 micro-caps 10px, `0.22em` tracking,
    pure ink.
  - The numeral `01` in Plex Mono **800**, 10px, `0.08em` tracking, in
    `--accent` (signal red). This is the brand-signal moment in the
    chartbook unit eyebrow.
- A pipe separator (`|`) in pure ink at `opacity: 0.32`, with 10px
  horizontal margin on each side.
- **Indicator name:** Manrope 600 at 11px, `0.04em` tracking, pure
  ink, **not uppercase**. The indicator name is a descriptive label,
  not a micro-caps stamp. e.g. `Headline real GDP, m/m` or `Core CPI
  trim, y/y`.

**Right cluster (`AS OF` stamp):**
- Label: `AS OF` in Manrope 600 micro-caps 10px, `0.22em` tracking,
  pure ink.
- Body: Plex Mono 400 at 12px, line-height 1.3, tabular nums, pure
  ink. e.g. `Mar 2026; released May 1, 2026`.

The eyebrow row sits 14px above the title row.

### Title row

A declarative one-sentence headline that summarizes the plate's
finding. Written by `writer`; placeholder text accepted in v1.

- Manrope **800**, size `clamp(22px, 2.4vw, 30px)`, line-height 1.15,
  letter-spacing `-0.012em`, pure ink. Max width 32ch.
- Renders as `<h2>` with the unit's `anchorId` + `-title` id so the
  page nav can target it.
- Sits 22px above the body grid.
- **Rule:** the title is a complete sentence, ends with a period,
  active voice, declares the plate's finding directly (e.g. `Monthly
  GDP rose 0.2% in March, on consensus.` not `GDP - monthly change`).

### Body grid (chart + interpretation)

A 2-column CSS grid at `>= 900px` viewport: chart column
`minmax(0, 1.5fr)` and interpretation column `minmax(0, 1fr)`, 32px
gap. Below 900px the grid collapses to a single column (chart on top,
interpretation below).

**Chart column.**
- The slot named `chart` receives the live chart component (an
  `<svg>` from a panel-specific Astro component, e.g.
  `Panel1HeadlineCPI.astro`).
- Container: 1px black border (the hairline plot frame), background
  `--paper`, no padding, overflow hidden.
- If `hasChart: false` is passed, the slot renders a dashed-border
  placeholder with `Chart to follow` micro-caps centered. The
  placeholder preserves a 5:3 aspect ratio so layout is stable
  between sections that have and have not landed their chart
  component yet.

**Interpretation column.**
- A 2- to 4-sentence interpretation paragraph in publication voice.
  Manrope 400 at 16px, line-height 1.55, pure ink. Max width 360px.
- Inline emphasis via `<strong>` renders in Manrope **600** weight,
  pure ink. Weight contrast is the emphasis device; the paragraph does
  not use italic or color.
- Wording owned by `writer`; placeholder accepted in v1.

### Optional callout strip

**Retired.** The earlier template had a callout strip between the body
grid and the source line carrying a big-number readout (`+0.2%`, `vs
consensus`, etc.). It is **deleted from the production
`ChartbookUnit`** as of v1.0; the per-print numeric story is carried
by the homepage panel's readout column, not by the chartbook unit.

The `CalloutSpec` interface remains in the component's `Props` type
for backward-compatible consumers, but the template does not render it.
**Do not document a callout strip in chartbook unit specs.**

### Source line

A single-line citation 24px below the body grid.

- Prefix: `SOURCE:` in Manrope 600 micro-caps 10px, `0.18em` tracking,
  pure ink. 8px right margin.
- Body: Plex Mono 400 at 11px, line-height 1.4, pure ink. Tabular
  nums. e.g. `Statistics Canada Table 36-10-0434-01.`
- The source citation is a typographic ritual, not a clickable link.
  If the citation needs to link to the underlying source, the link is
  the source body text itself with the canonical link treatment from
  `design-system.md` (text-decoration underline in ink, hover to
  accent).

### Unit boundary rule

1px black hairline at the bottom of every unit. The last unit on the
page drops its hairline (the page footer carries the closing boundary
when present). Convention: the parent stack wraps the units in
`.chartbook-stack`, and a global rule drops the last child's
border-bottom.

### Padding rhythm

- Unit vertical padding: 36px top + 36px bottom.
- Eyebrow row to title: 14px.
- Title to body grid: 22px.
- Body grid to source line: 24px (`--s-5`).
- Body grid column gap (chart to interpretation): 32px desktop,
  20px tablet, 0px (stacked) mobile.

---

## 4. Per-section adaptations

Each section follows the chartbook template above, with section-specific
conventions for which indicators get which plate numbers, what cadence
their `AS OF` stamps reflect, and any chart-shape conventions specific
to the section.

This section names the production conventions per section. All seven
sections use the same `SectionPageHeader.astro` and `ChartbookUnit.astro`
components; the adaptation is in the plate inventory, the cadence
conventions, and the chart shapes consumed in the chart slot.

### 4.1 GDP

- **Headline question:** `Is the Canadian economy growing?` (writer to
  refine).
- **Latest-release stamp cadence:** monthly (the Industry GDP m/m
  release). e.g. `March GDP, released May 1, 2026`.
- **Plates (production: 6):**
  - 01 Headline real GDP, m/m. Chart: monthly bars (thin columns,
    ~4px wide, pure ink fill, MTA red latest-bar dot at the top of the
    last bar).
  - 02 Industry vs expenditure cuts. Chart: 2-panel small multiple,
    each panel a horizontal bar.
  - 03 Contributions to growth. Chart: stacked horizontal bars for the
    most recent quarter; one row per major expenditure category.
  - 04 Per-capita GDP. Chart: dual line (aggregate GDP vs per-capita
    GDP), indexed to a common base year.
  - 05 Output gap. Chart: single line with shaded recession bands.
  - 06 Recession state. Chart: a calendar heat-strip across the
    visible window with months shaded by an in-recession indicator;
    Knoll-catalogue style.
- **Cadence note:** GDP runs on the slowest cadence of the seven
  sections (monthly with a 2-month publication lag). The header's
  latest-release stamp will often read "released ~2 months ago" -
  this is editorially correct, not a stale-data tell.

### 4.2 Inflation

- **Headline question:** `Is Canadian inflation returning to target?`
- **Latest-release stamp cadence:** monthly. e.g. `April CPI, released
  May 14, 2026`.
- **Plates (production: 6):**
  - 01 Headline CPI, y/y. Chart: dual line (headline y/y solid, 3M
    annualized dashed). The 2% target reference rule renders as a 1px
    dashed pure-ink line across the plot area with a 2px micro-caps
    label `2% target` at the right gutter.
  - 02 Core trio (trim / median / common). Chart: 3-line panel; the
    primary core (trim) is the heavier line; the other two recede via
    1px stroke + 0.6 stroke-opacity.
  - 03 Breadth (% basket > 3%). Chart: single line.
  - 04 Sub-aggregates (goods vs services). Chart: dual line.
  - 05 Expectations (consumer / business). Chart: dual line.
  - 06 Pass-through (input prices to output prices). Chart: scatter
    or 2-panel small multiple.
- **Section accent:** Inflation's `--section-accent-inflation` resolves
  to `--accent` (signal red). This is the one section where the
  section accent and the brand accent are the same; Inflation is the
  publication's load-bearing section, and the convergence is
  deliberate.

### 4.3 Labour

- **Headline question:** `Is the Canadian labour market still
  loosening?`
- **Latest-release stamp cadence:** monthly (Labour Force Survey).
  e.g. `April LFS, released May 9, 2026`.
- **Plates (production: 6):**
  - 01 LFS headline (employment, unemployment rate, participation).
  - 02 Per-capita employment.
  - 03 Wage band (average hourly earnings, distribution).
  - 04 Vacancies and slack (V/U ratio).
  - 05 IRCC supply trajectory (immigration intake vs target).
  - 06 Regional dumbbell (provincial unemployment rates).

### 4.4 Housing

- **Headline question:** `Is Canadian housing recovering, stalling, or
  still correcting?` (writer to refine).
- **Latest-release stamp cadence:** monthly (MLS HPI). e.g. `April
  MLS HPI, released May 15, 2026`.
- **Chart status:** plates have not yet landed as bespoke Astro
  components. Chartbook units render with `hasChart: false` (dashed
  placeholder) until the chart-builder lands them.
- **Plates (production: 6 planned):**
  - 01 MLS HPI, y/y.
  - 02 Sales-to-listings ratio.
  - 03 Months of inventory.
  - 04 Mortgage rate trajectory.
  - 05 CMA strip: y/y price change by major CMA (a horizontal strip
    of one-cell-per-CMA bars; Housing-specific layout).
  - 06 Housing starts.

### 4.5 Policy (Monetary + Fiscal)

- **Headline question:** `Is Canadian monetary and fiscal policy on
  hold or in motion?`
- **Latest-release stamp cadence:** event-driven (BoC decisions every
  ~6 weeks; federal fiscal updates seasonally). e.g. `BoC decision,
  April 16, 2026`.
- **Chart status:** plates have not yet landed; placeholders.
- **Plates (production: 6-8 planned):**
  - 01 BoC overnight rate. Chart: step function in pure ink with
    MTA red latest-print dot. Step-after rendering (right-angle
    corners), not smoothed.
  - 02 OIS-implied path (market pricing of future BoC decisions).
  - 03 Yield curve (2y / 5y / 10y).
  - 04 Real rates.
  - 05 Federal fiscal balance.
  - 06 Federal debt trajectory.
- **Section-specific convention:** the Policy section is the one
  section where the chartbook may visually split into two sub-blocks
  (Monetary plates 01-04, Fiscal plates 05-06). A 2px black hairline
  separates the two blocks; the second block carries its own micro-
  heading (`FISCAL`) in Manrope 800 24px, pure ink, centered, with
  18px breathing room above and below.

### 4.6 Markets

- **Headline question:** `What are Canadian financial markets pricing
  in?`
- **Latest-release stamp cadence:** **higher frequency than the other
  sections** - daily for FX and equities, weekly for credit
  spreads. The stamp includes the time of day (closing print). e.g.
  `USDCAD, close May 9, 2026 (5:00pm ET)`.
- **Chart status:** placeholders.
- **Plates (production: 6 planned):**
  - 01 USDCAD spot. Chart: 1-year rolling line in pure ink, no
    recession bands (at 1y window they would dominate
    inappropriately).
  - 02 Equity index (S&P/TSX).
  - 03 Credit spreads.
  - 04 Commodity bellwethers (oil, gold).
  - 05 Term structure (BAX / OIS).
  - 06 Volatility (VIX, BAX vol).

### 4.7 Trade

- **Headline question:** `Is the Canadian trade balance widening or
  narrowing, and with whom?`
- **Latest-release stamp cadence:** monthly. e.g. `March trade,
  released May 6, 2026`.
- **Chart status:** placeholders.
- **Plates (production: 6 planned):**
  - 01 Merchandise trade balance, 3mma. Chart: single line with a
    pure-ink zero line; line crosses zero in the visible window
    (continuous stroke, no segmenting).
  - 02 Exports vs imports.
  - 03 Bilateral balance (US, China, EU).
  - 04 Commodity vs non-commodity exports.
  - 05 Services trade.
  - 06 Tariff state (a reference table rather than a chart). The
    "chart" slot renders a 4-column table: tariff regime / partner /
    rate / effective-since. Trade is the one section with a non-chart
    plate; the unit's chart-slot accepts an arbitrary block, so a
    table renders there with the same 1px black hairline frame.

---

## 5. Visual cohesion within a section page

Two cohesion rules specific to chartbook pages (in addition to the
canonical cohesion rules in `design-system.md` Section 10):

### 5.1 Plate-number rhythm

Every plate number is rendered identically (Manrope 600 `PLATE` word
+ Plex Mono 800 `--accent` numeral). The reader's eye reading
"PLATE 01" at the top of the first unit reads it identically when it
reaches "PLATE 06" at the bottom. The plate-number rhythm down the
page is the section's typographic spine - it should never vary
within a page.

### 5.2 Hairline boundary inventory

A reader scrolling a section page experiences three weights of
horizontal rule:

- 1px black hairline - between units, inside a unit (between eyebrow
  and title band on the section header), around chart plate frames,
  between table rows.
- 2px black hairline - section-close (under the plate index in the
  header) and Policy sub-block divider (between Monetary and Fiscal).

There is no 3px or thicker rule weight. There is no rule color other
than pure black. Section-page wayfinding is carried by these two
weights only; any new rule introduced into the page should be a 1px
unit-boundary rule unless it explicitly closes a major band.

### 5.3 Phase 2 - section accent on the chartbook eyebrow

The current production renders every plate number in `--accent`
(signal red), regardless of which section. Phase 2 may pick up the
per-section `--section-accent-*` token on the plate numeral so the
reader recognizes "I am in Inflation" by the red plate number vs
"I am in Labour" by the sage-green plate number. This is a Phase 2
decision and requires:
- Editorial-director approval that per-section color is desirable
  (vs. one-accent uniformity).
- Adjusting `ChartbookUnit.astro` to consume an `accentVar` prop and
  pipe it into the `.chartbook-unit__plate-n` rule.

Until Phase 2 lands, every plate number is signal red.

---

## 6. What this template does NOT include

Honesty discipline. The chartbook template is constrained: it is the
page a reader visits for one section's state, not an essay landing
page or a tooling surface.

- **No mid-page essay sections.** Prose lives in the lede (above the
  stack) or the interpretation column (alongside each chart). Not
  between units.
- **No mid-page navigation.** The plate index in the header is the
  only intra-page navigation. No floating TOCs, no breadcrumbs above
  individual units.
- **No mid-page filter / sort UI.** A section page is a static
  publication, not a queryable data tool. Filters belong on a
  separate exploration page (Phase 2 or later).
- **No callouts between units.** The unit-interpretation column is
  the callout surface; mid-stack callouts would compete.
- **No methodology drawer per unit.** Methodology is a section-page
  footer concern (or, longer-term, a Methodology page linked from
  the source line). It is not a per-unit affordance.
- **No revision marker visual hop** (the prior basics-template
  Section 5 had an open-circle + dashed-connector for the prior-
  vintage value). The Vignelli register prefers a typographic
  treatment: the interpretation paragraph carries the revision in
  prose ("the March print was revised down 0.1pp from a preliminary
  +0.3%"). If editorial later asks for a visual revision indicator,
  the convention is: a 2px pure-ink open circle at the revised
  point, connected to the new value by a 1px dashed pure-ink line.
  No second color. No animation.

---

## 7. Open questions and Phase 2 hooks

- **Section accent on plate numbers (Phase 2).** See 5.3 above.
- **Per-section masthead chrome.** Currently the masthead is identical
  on every section page. Editorial may decide to vary one masthead
  element (e.g. the wordmark's tracking, or a section-specific
  micro-stamp under the wordmark) per section. Not in v1.
- **Methodology page.** The source lines link to data sources; a
  separate Methodology page (or per-section methodology surface)
  would document data transformations, vintage handling, and
  revision policy. Not in v1; the source line is the v1 methodology
  affordance.
- **Print stylesheet.** Defer until reader request.
- **Localization (FR).** The 22ch headline-question max-width and
  the 64ch lede max-width are tuned for English; French averages
  ~20% longer copy. Re-tune per page when FR pages land.

---

End of chartbook template v1.0.
