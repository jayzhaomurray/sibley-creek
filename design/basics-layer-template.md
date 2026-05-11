# Basics-Layer Page Template

Status: v0.3, living document. Author: art-director.
Last updated: 2026-05-11.

Changelog:
- v0.3 (2026-05-11): Added Sections 9.C (Housing), 9.D (Policy: Monetary +
  Fiscal), 9.E (Markets), 9.F (Trade). All four sections follow the panel
  grammar established in Sections 1-8 and the per-section conventions
  established in 9, 9.A, 9.B. No new design-system tokens proposed; all
  visual treatments reuse existing palette and type tokens. Three section-
  scoped conventions formalized: (a) Housing CMA-strip layout for CMA-by-
  CMA reads; (b) Policy two-sub-surface delimiter (Monetary block + visual
  divider rule + Fiscal block) designed for 8 panels with graceful 6-panel
  fallback; (c) Markets higher-cadence vintage stamping (date + time-of-day
  for the daily/weekly series); (d) Trade non-chart reference-table panel
  treatment (Tariff state).
- v0.2 (2026-05-11): Added 9.A (Inflation) and 9.B (Labour).
- v0.1 (2026-05-11): Initial template with GDP worked example.

This document specifies the visual template for **per-section basics-layer
pages** (GDP, Inflation, Labour, Housing, Policy, Markets, Trade). It is
distinct from the R1 homepage. It is the page a Bay Street allocator opens at
7am to see where one section of the Canadian economy stands.

Worked example throughout: **GDP**, per `editorial/dashboard_purpose.md`
Section 4.1.

All tokens cited here are defined in `design/design-system.md`. Where this
template requires a token extension, it is flagged with `[TOKEN PROPOSAL]`
for main Claude to fold into the canon after review.

---

## 0. What a basics-layer page is, and what it is not

A basics-layer page is the **state-of-the-section view**. It is not an essay,
not a deep dive, not a homepage. The reader has navigated here because they
want to know: what does Canadian GDP look like right now? They want six
clean panels, each answering one tight question, each anchored to the most
recent print, each with provenance visible.

Reference lane: think of an FT "Markets Data" landing page crossed with an
NYT Upshot section index, set in the broadsheet voice we established in
`design/design-system.md`. Specific exemplars worth keeping open:

- **FT Markets Data pages** (ft.com/markets) — for the discipline of "every
  panel earns its place, every number has a timestamp, no panel is
  decorative." Take: panel grid that breathes; per-panel vintage stamp.
- **NYT Upshot "Economy at a Glance" landing** (when it has run) — for the
  willingness to put six small charts on one page and let each one carry one
  idea. Take: each panel is a complete chart with title, deck, source — not
  a stripped sparkline.
- **Reuters Graphics quarterly economy round-ups** — for the way they handle
  vintage stamps and revision callouts without breaking the reading flow.
  Take: revision treatment as a typographic event, not an icon.
- **Bank of Canada Indicators page** (bankofcanada.ca/rates/indicators) —
  consulted as restraint reference. Their typography is plain; we set our
  bar higher, but we share their citation discipline.

What a basics-layer page is **not**:

- Not a KPI dashboard. No big-number tiles with up/down arrows as the entire
  panel. Every panel is a chart, with a number called out from inside the
  chart.
- Not an essay landing page. Prose is reserved for the section blurb at top
  and the per-panel deck. No 400-word paragraphs between panels.
- Not a feed. Panels do not stream; they are dated and stable until the
  next release.
- Not a homepage. The homepage greets all readers; the basics page assumes
  a reader who chose this section.

---

## 1. Page header

The header establishes: which section you are in, what the section asks,
when it was last updated.

### Structure (top-down)

```
[ KICKER ROW            ]   eyebrow + accent rule + nav crumb
[ SECTION NAME          ]   serif display-xl
[ HEADLINE QUESTION     ]   serif deck italic
[ SECTION-AS-OF STAMP   ]   micro mono, ink-faint
[ HAIRLINE RULE         ]   1px, section-accent at 40% opacity
```

### Kicker row

A single-line eyebrow at the very top of the content area, set in `label`
size all-caps with `0.08em` letter-spacing. Three elements, separated by a
thin vertical rule glyph (`|`) at `ink-faint`:

```
MACRO RESEARCH DEPARTMENT  |  SECTION 1 OF 7  |  GDP
```

The third element is the section name and is colored in the **section
accent**. The kicker is `label` size; the section name within the kicker is
weight 600 (same size, same caps, same letter-spacing — just heavier).

### Section name

The big serif title of the page. `display-xl` (40px) serif, weight 600,
color `ink`. One word where possible: **GDP**, not "Gross Domestic Product."
Where a section title must be two tokens (e.g., **Policy / Monetary +
Fiscal**), the slash separates and the secondary tokens drop to `display-lg`
in the same line.

### Headline question

Directly below the section name, separated by `s-3` (12px). The section's
EDR-canonical headline question, set in `deck` (19px serif italic, weight
400, `ink-muted`).

For GDP:

> *Is the Canadian economy at potential, growing, or contracting — and what
> is driving it?*

This is the orienting sentence. The reader who answers this question after
looking at the panels has gotten what they came for. Wording is locked by
EDR; art-director does not edit it. We just set it.

### Section accent rule

A **section accent** is the one color signifier that distinguishes this
section's basics page from the other six. It is **not** a brand color; it is
a *wayfinding* color. Used in: the kicker section name, the hairline rule
beneath the header, the panel index dots (see Section 2), the section
breadcrumb in nav. It does **not** color data (data colors are the chart
palette).

Mapping (drawn from the existing categorical chart palette, deliberately
re-using `series-N` so we are not introducing a new color system):

| Section    | Accent token | Hex       | Source         |
|------------|--------------|-----------|----------------|
| GDP        | `series-1`   | `#1F4E79` | Deep blue      |
| Inflation  | `series-2`   | `#C9772A` | Burnt orange   |
| Labour     | `series-3`   | `#5B7553` | Sage green     |
| Housing    | `series-4`   | `#7A3E65` | Plum           |
| Policy     | `series-5`   | `#3F7D7C` | Teal           |
| Markets    | `series-6`   | `#8A6A2C` | Olive gold     |
| Trade      | `series-7`   | `#4A4F57` | Slate          |

**Rationale.** Re-using `series-1` through `series-7` for section wayfinding
keeps the system tight: when the GDP basics page shows a chart whose primary
series is deep blue, it reinforces the section identity rather than fights
it. The slate accent for Trade is intentional — Trade is the most visually
"neutral" section and slate is the gentlest of the seven.

`[TOKEN PROPOSAL]` Add to `design/design-system.md` Appendix A:

```
--section-accent: <set per page via inline style on <body data-section="gdp">>
```

A page sets `--section-accent` once at the page root; downstream styles
reference `var(--section-accent)`. This avoids hard-coding `series-1` in
GDP's stylesheet and keeps the wayfinding logic local to one declaration.

### Section-as-of stamp

The **least-recent** panel update on this page, surfaced once at the header
level so a reader sees worst-case freshness before they scroll. Per EDR
ruling (2026-05-11), the page is "as stale as its stalest panel" — the
allocator at 7am wants the conservative answer. Format:

```
OLDEST PANEL  BoC potential output (MPR), Q1 2026 (released Apr 16, 2026)
```

Or, when all panels are within one release-cycle of each other:

```
LATEST RELEASE  Monthly GDP by industry, Mar 2026 (released May 1, 2026)
```

Kicker-word selection (`OLDEST PANEL` vs `LATEST RELEASE`) is `writer`'s
on each refresh; the two-state visual treatment is identical (same type,
same color, same placement). See Section 6 for the page-level vs per-
panel logic.

Set in `micro` Inter weight 500 for the kicker word, `micro` Inter weight
400 for the rest, color `ink-faint`. Sits `s-4` (16px) below the headline
question, left-aligned to the body column.

A **page-level** as-of stamp is distinct from **per-panel** as-of stamps
(Section 6). The page-level stamp answers "is the page fresh enough."
The per-panel stamp answers "is this specific chart fresh."

### Hairline rule

A 1px horizontal rule in the section accent at 40% opacity, spanning the
body column (680px). Below the rule, `s-7` (48px) of space, then the panel
grid begins.

---

## 2. Panel grid

The basics layer is a grid of 4-6 panels. For GDP, six. Each panel is a
self-contained chart-card with title, deck, primary chart, latest-print
callout, vintage stamp, source line, and methodology affordance.

### Grid behavior

The grid lives in the **wide track** (1040px max) so panels can breathe.
Body prose (the section blurb at top of the page and any inter-panel notes)
stays in the **body column** (680px).

**Desktop (`xl`, >=1200px):** Two columns of panels. Each panel ~496px
wide (1040px - 24px gutter, halved, minus 16px panel padding). Panels stack
in reading order:

```
[ Panel 1 ] [ Panel 2 ]
[ Panel 3 ] [ Panel 4 ]
[ Panel 5 ] [ Panel 6 ]
```

**Tablet (`lg`, 960-1199px):** Two columns at narrower panel widths.

**Tablet landscape narrow (`md`, 640-959px):** Single column at full body
width. Each panel becomes a wide-aspect chart card.

**Mobile (`sm`, <640px):** Single column at full viewport minus 16px
margins. Panels stack. Charts use the small-screen variants designed by
art-director per chart.

Gutter between panels: `s-6` (32px) vertical, `s-5` (24px) horizontal.
Generous; do not crowd.

### Panel index dots

Above the grid, a horizontal row of 4-6 small dots, one per panel, in the
**section accent**. The dots are clickable anchors that jump to each panel.
Each dot is 8px diameter, separated by `s-3` (12px). On hover, the dot
expands a small label below it with the panel title.

This is the only navigation aid inside a basics page. We do not need a left
sidebar. We do not need a sticky in-page TOC. Six dots is enough.

```
. . . . . .                    [labelled on hover]
1 2 3 4 5 6
```

Color when current/in-view: section accent solid. Color when not: section
accent at 30% opacity. The dot for the panel currently in viewport (more
than 50% visible) is solid.

### Panel reading order

The EDR fixes the panel order in each section. For GDP per Section 4.1:

1. Headline real GDP (monthly + quarterly)
2. Industry vs expenditure cross-check
3. Contributions to quarterly growth (six-bar GFCF)
4. Per-capita real GDP
5. Versus BoC potential
6. Recession state (C.D. Howe BCC)

The grid renders them in that order, left-to-right, top-to-bottom. Do not
reorder for visual balance — the EDR's order is the editorial argument of
the page.

---

## 3. Per-panel structure

Every panel is the same structural object, every time. A reader who learns
the panel grammar on GDP transfers it directly to Inflation, Labour,
Housing, Policy, Markets, Trade.

### Anatomy

```
+----------------------------------------------------------+
|  [PANEL EYEBROW]                       [VINTAGE STAMP]   |   <- top row
|                                                          |
|  Panel title (display-sm serif)                          |
|  Panel deck (body-sm italic, ink-muted, 1 sentence)      |
|                                                          |
|  +----------------------------------------------------+  |
|  |                                                    |  |
|  |           PRIMARY CHART (with all chart-aesthetic  |  |
|  |           rules from design-system.md section 5)   |  |
|  |                                                    |  |
|  +----------------------------------------------------+  |
|                                                          |
|  LATEST PRINT CALLOUT                                    |
|  [Big number]  [unit]                                    |
|  [Direction badge] [delta vs prior] [surprise vs cons.]  |
|                                                          |
|  --                                                      |   <- 1px rule
|                                                          |   in rule-faint
|  Source: [primary cite]               [Methodology >]    |
|                                                          |
+----------------------------------------------------------+
```

Panel card visual treatment is the **card pattern** from
`design/design-system.md` Section 6: `surface` background, 1px `rule`
border, 4px radius, **no shadow ever**. Padding: `s-6` (32px) all sides,
`s-7` (48px) top.

### Component details

**Panel eyebrow.** All-caps `label` size, letter-spacing `0.08em`, color
**section accent**. Names the panel by its EDR designation, e.g.,
`HEADLINE REAL GDP`, `CONTRIBUTIONS TO GROWTH`. Same color logic as the
header kicker — the section accent appears at the kicker and at each panel
eyebrow, and only there. Inside the chart, color is data color.

**Panel title.** `display-sm` (23px) serif, weight 600, `ink`. Active voice.
For GDP panel 1, e.g.: *"Monthly GDP rose 0.2% in March, on consensus."*
Wording is owned by `writer`; we just set it. Maximum two lines at panel
width (~440px text column inside the card). If a panel title runs longer,
push back to writer.

**Panel deck.** `body-sm` (15px) serif **italic**, weight 400, `ink-muted`.
One sentence answering "so what." For GDP panel 1, e.g.:
*"The economy advanced for the second consecutive month, but the year-over-
year pace remains below the BoC's potential estimate."*

**Primary chart.** Built by `chart-builder` to a per-chart visual spec from
art-director. All chart-aesthetic rules from `design/design-system.md`
Section 5 apply: muted axes, horizontal gridlines only, direct labels, no
legends where avoidable, annotations in white space.

Chart canvas inside the panel: 432px wide on desktop (panel width minus
padding). Aspect ratio: 16:9 default for time-series; 4:3 for bar
decompositions; square for scatter / Beveridge-curve style.

**Latest-print callout.** A typographic block sitting between the chart and
the source line. Three elements stacked tight:

1. **Big number.** `display-md` (28px) serif, weight 600, tabular figures,
   `ink`. The most recent value of the headline series. E.g., `0.2%`.
2. **Unit / period label.** `body-sm` (15px) sans, `ink-muted`, sitting
   immediately below the big number. E.g., `month-over-month, March 2026`.
3. **Direction + surprise row.** Three pieces of metadata in a single row:
   - **Direction badge** (`pos` / `neg` / `neutral` color + arrow glyph)
   - **Delta vs prior** in `label` size sans, tabular, color = direction
     color. E.g., `+0.1pp vs Feb`.
   - **Surprise vs consensus** in `label` size sans, color = direction
     color, with a small subscript indicating consensus source. See
     Section 4.

**Source line.** Below a 1px `rule-faint` separator, sitting at the panel
foot. Format and treatment per Section 8.

**Methodology link.** Right-aligned on the source-line row. See Section 7.

### Panel without a callout? — the editorial-status-panel pattern

Some basics-layer panels are not headline-number panels. The "Recession
state" panel (GDP element 6) is editorial status, not a chart. The
"Industry vs expenditure cross-check" (element 2) may render as a two-line
comparison chart with no single headline number. The Inflation breadth
panel and the Labour Beveridge-curve panel also fall in this family on
some refreshes (no single number summarizes the visual).

**EDR ownership split (ruling 2026-05-11).** Art-director defines the
*structure* of the editorial-status block; `writer` defines the *wording*
on each refresh. The wording slot is not silently editable by art-director
between briefs, and the structure is not silently extensible by writer.

**Structure (art-director).** A status block sits in the same vertical
slot as the latest-print callout, with the same outer dimensions so the
grid aligns. It has three typographic slots:

1. **Status label.** `label` size all-caps, weight 500, letter-spacing
   `0.08em`, color `ink-muted`. Names the kind of status, e.g.,
   `CURRENT STATE` / `CROSS-CHECK` / `BREADTH READ`. Maximum two words.
2. **Status line.** `body-sm` (15px) Inter weight 500, color `ink`. One
   sentence, target 12-20 words, hard cap 28 words. Active voice.
3. **Context line (optional).** `body-sm` (15px) Inter weight 400, color
   `ink-muted`. One sentence carrying the parenthetical (dating-committee
   reference, methodology hint, vintage qualifier). May be omitted; when
   omitted, the slot collapses.

```
CURRENT STATE
Expansion since 2020Q3, per C.D. Howe BCC.
Amplitude, duration, scope at trough: per BCC committee minutes.
```

**Wording (writer).** Verb choice, framing, what to call out, what to
leave to the chart. Writer fills slots 2 and 3 on each refresh; the
labels in slot 1 are stable across refreshes within a section (writer
proposes the label list to art-director once per section, and it stays
locked thereafter).

The structural slot is preserved (same vertical position, same height) so
the panels align across the grid even when slot 3 is absent.

---

## 4. Surprise-vs-consensus visual treatment

Per `editorial/dashboard_purpose.md` Section 4.1, element 1 (and the
2026-05-10 override): the surprise framing is **consensus-first** (Bloomberg
/ Reuters median, or aggregated forecaster median where the paid feed is
unavailable), with **BoC MPR central projection** as the fallback when
consensus is genuinely unavailable. The same logic applies in Inflation
element 1 and Labour element 1.

The design must surface (a) the surprise direction and magnitude, and (b)
which anchor was used.

### Visual specification

The surprise lives in the **callout's third row** (direction + surprise
row). Inline format:

```
[arrow] +0.1pp vs Feb    |    Beat consensus by 0.1pp[c]
```

Where:

- The pipe is a `|` glyph in `ink-faint`, separating "delta vs prior"
  from "surprise vs anchor."
- `Beat` / `Missed` / `In line with` is the verb. Lowercase except when
  starting a callout sentence. Selection rule (mechanical): difference
  outside +/-0.05pp on growth rates is beat/miss; inside is in-line.
  Refinements owned by `writer`.
- The number is the delta in the same units as the series.
- The **subscript glyph** `[c]` or `[m]` indicates the anchor:
  - `[c]` = consensus (Bloomberg / Reuters median or aggregated forecaster
    median).
  - `[m]` = BoC MPR central projection (used when consensus is
    unavailable).

Subscript treatment: `mono-xs` (12px) Plex Mono, color `ink-faint`, set
slightly below the baseline (CSS `vertical-align: -0.25em`). The square
brackets are part of the glyph and read as a citation marker, not a
formatting accident.

### Hover / tap behavior

Hovering or tapping the subscript reveals a small tooltip in `body-sm`
weight 400 `ink` on `surface` background, 1px `rule` border:

For `[c]`:
> *Consensus = Bloomberg/Reuters median forecast as of [date]. Sample
> size: N forecasters.*

For `[m]`:
> *MPR fallback used. Consensus unavailable for this release. Anchor:
> Bank of Canada Monetary Policy Report, [Jan/Apr/Jul/Oct] 2026
> projection.*

This is the only place on the basics page where we use a hover tooltip
for narrative. Everywhere else, tooltips give precision (numbers, dates).
This one tooltip gives provenance. It is small enough to earn its keep.

### Color encoding

The verb and the number on the surprise side use the same direction color
as the delta-vs-prior on the left:

- `pos` (`#1F6B3A`) for a beat that is directionally positive (above
  consensus on a growth measure, below consensus on an inflation measure
  where lower-is-better — but this gets contentious and is `writer`'s call
  per-section, not art-director's).
- `neg` (`#B23A2F`) for a miss in the same logic.
- `neutral` (`#5A6470`) for in-line.

Note: there is a tension here on inflation, where "above consensus" is
typically interpreted as bad (above-target persistence), not good (growth).
We **do not** flip the color encoding by section. Color always encodes the
*direction of the print* relative to expectations, not the editorial
valence of that direction. The deck and writer's prose carry the
"is-this-good-or-bad" interpretation. This is a hard rule.

### When there is no surprise to show

Some panels in the GDP basics page have no consensus reference. Per-capita
real GDP (element 4) is a derived series; BoC potential comparison (element
5) is a benchmark, not a forecastable print; recession state (element 6) is
not a numeric release. For these panels, the third row of the callout
collapses to just the delta-vs-prior (or, for the BoC-potential panel, the
output-gap percentage). The pipe and the surprise verb simply do not
render.

---

## 5. Revision-direction visual

StatCan revises monthly GDP estimates on every subsequent release. A March
2026 estimate at +0.2% may be revised to +0.3% or +0.1% when the April
release lands. Per EDR section 4.1 element 1, "revision direction" is part
of the basics-layer surface.

Revisions matter editorially because:
- A persistent upward revision pattern suggests the agency is under-
  estimating early.
- A downward revision into the previous quarter's print can change the
  quarterly Q/Q SAAR materially.
- Readers who anchored on the prior vintage need to be told the data
  moved.

### Visual specification

When the current release revises a previously-published estimate, we mark
it in **two places**:

**(1) In the chart itself.** The revised data point (the previously-
published value) is rendered as a small open circle (4px diameter, 1px
stroke in the series color, transparent fill) at its original position. A
thin connecting line in `ink-faint` 1px dashed (`2 2`) connects it to the
current value's filled marker. This creates a "where it was, where it is"
visual hop.

```
  prior vintage
       o
       :
       :  <- 1px dashed ink-faint, length = revision magnitude
       :
       *  <- current vintage, filled series-color
   current vintage
```

This treatment only renders for the **single most recently revised point**.
Older revisions are silently absorbed into the chart; we do not render the
revision history as a fanned-out cloud (that is deep-dive territory).

**(2) In the callout's direction-badge row.** When a revision happened,
append a small revision tag to the right of the surprise field:

```
[arrow] +0.1pp vs Feb    |    Beat consensus by 0.1pp[c]   [Revised up]
```

`Revised up` / `Revised down` / `Unrevised` in `label` size, weight 500,
color: `pos` / `neg` / `ink-faint` respectively. The tag is preceded by
`s-3` (12px) gap. Optional small caret glyph (`^` / `v`) before the word.

### When the revision spans multiple periods

**EDR ruling (2026-05-11).** Revision-tag scope on the basics layer is
**single point** — the most recently revised observation — with a
**multi-period footnote** in chart whitespace when prior months were also
revised. Multi-period revision visualization (fan, ribbon, vintage-stack)
is strictly deep-dive territory and does not enter the basics layer.

In practice: the chart treats only the immediate prior month with the
open-circle treatment, and a footnote-style annotation (`body-sm` italic,
`ink-muted`) sits in chart whitespace:

> *Also revises Jan and Feb downward by 0.05pp each.*

Annotation wording is `writer`'s; placement is art-director's per chart.
The callout's `[Revised up/down]` tag reflects the most recent point only;
the footnote carries the multi-period detail.

### No-revision case

When no revision occurred, the chart shows only filled markers and the
callout tag reads `Unrevised` in `ink-faint`. The tag is never omitted —
its absence would be ambiguous.

---

## 6. Vintage stamp ("as of") treatment

Every panel carries a vintage stamp. The reader must always be able to ask
"is this fresh?" and get an answer from the panel without leaving it.

### Specification

**Placement.** Top-right of the panel card, on the same baseline as the
panel eyebrow (so the eyebrow is left-rail, the vintage is right-rail).

**Format.**
```
AS OF May 1, 2026
```

`AS OF` in `label` size, weight 500, letter-spacing `0.08em`, color
`ink-faint`. The date in `body-sm` (15px) Inter weight 400, color
`ink-muted`. Date format: `MMM D, YYYY` (Canadian editorial convention —
month abbreviated, ordinal omitted, comma separator).

For panels where the release date and the reference-period date are both
load-bearing (almost all of them), the stamp expands to two lines:

```
AS OF
May 1, 2026
Reference: Mar 2026
```

Three short lines, right-aligned, line-height tight (1.3). Reference
period in `micro` (12px) Inter weight 400 `ink-faint`. The two-line stamp
is the default for the GDP basics page.

### When the data is stale

If the most recent print is older than the section's stated cadence
(monthly GDP > 65 days since release, for example), the vintage stamp
gets an inline warning: a small `neg` color caret glyph (`!`) immediately
preceding the date. Hover reveals a tooltip:

> *This data has not refreshed within its expected cadence. Last expected
> update: [date].*

The caret is `body-sm` `neg` weight 500. We do not use a red box, a banner,
or a toast. The caret is the typographic event.

This is consistent with our broader stance from `design/design-system.md`
Section 8: motion serves comprehension, never decoration. A staleness
warning is a fact, and we display it as a fact.

### Page-level vs panel-level

The page-level as-of stamp in the header (Section 1) shows the **least
recent** vintage across all panels — i.e., the page is "as stale as its
stalest panel." Per-panel stamps are the truth for each panel.

**EDR ruling (2026-05-11).** Least-recent at the page level. The Bay
Street allocator at 7am needs the worst-case freshness answer, not the
best-case. A page that surfaces its freshest stamp at the header would
imply uniformity it does not have. Least-recent is the honest answer.

Implementation: the page-level stamp reads the **maximum days-since-
release** across all panels' release-date stamps, and surfaces that
panel's release date and reference period. Format unchanged from
Section 1 spec; the header copy `LATEST RELEASE` is replaced with
`OLDEST PANEL` when the least-recent stamp is more than one release-
cycle behind any other panel on the page, and with `LATEST RELEASE` when
all panels are within one cycle of each other (the typical case).
Writer owns the kicker-word choice on each refresh; art-director owns
the two-state visual treatment.

---

## 7. Methodology-note pattern

Per EDR voice principle (Section 7): *"If a chart is constructed
(decomposed, detrended, seasonally adjusted by us, or built from microdata),
the methodology note is one click away."* This is a hard requirement.

### Specification

Every panel has a methodology link in the **panel foot row**, right-aligned
on the same line as the source citation:

```
Source: Statistics Canada Table 36-10-0434-01.       Methodology >
```

`Methodology` in `label` size, weight 500, color `ink` (not muted — it is a
real affordance), with a single-character right caret `>` in `ink-muted`.
The link is underlined with a 1px offset 2px underline in `accent` (our
editorial red), per design-system.md Section 6 tertiary-link rule.

### Affordance behavior

Click opens a **right-side drawer** (not a modal, not a new page). The
drawer slides in from the right edge of the viewport, max-width 480px,
overlays the panel grid at 90% opacity backdrop, contains:

- **Drawer title.** Panel name in `display-sm` serif. E.g.,
  *"Monthly GDP by industry — methodology"*.
- **Body.** `body` (17px) sans Inter, in the 680px body-column scale.
  Contains: data source(s) with primary citation, vintage logic
  (which release vintage drives which slice), any seasonal adjustment or
  construction the project applies on top of the raw release, sensitivity
  notes, and links to the underlying StatCan/BoC table.
- **Close affordance.** Top-right `X` glyph (Lucide `x`, 20px,
  `ink-muted`), or click anywhere outside the drawer.

Drawer slide animation: 200ms ease-out from the right. Under
`prefers-reduced-motion`, instant. Per design-system motion rules.

### When methodology is trivial

For panels that simply chart a single StatCan series with no construction
on top (e.g., headline GDP m/m), the methodology link still exists but the
drawer is short:

> *Series: StatCan Table 36-10-0434-01, monthly GDP by industry, seasonally
> adjusted, chained 2017 dollars. No construction on top. Released ~60
> days after the reference month.*

We never omit the link, because the existence of the link is the editorial
contract. Even a trivial methodology page reinforces that the reader can
trust where every number comes from.

### Methodology link styling — open question

The right caret `>` is a placeholder. Alternative: a Lucide `external-link`
glyph if the drawer is replaced by a methodology page (a v1.5 question if
methodology pages get long enough to deserve their own URL). Flag as
**open question for frontend-designer**.

---

## 8. Source-citation pattern

Per EDR Section 7: *"Cite primary sources."* Every panel cites its primary
source on the panel foot row, every time.

### Specification

**Placement.** Below the panel callout, separated by a 1px `rule-faint`
horizontal line. Left-aligned, sharing the row with the methodology link
(right-aligned).

**Format.**

```
Source: Statistics Canada Table 36-10-0434-01; consensus via Bloomberg.
```

`Source:` in `micro` Inter weight 500 `ink-faint`. The citation in `micro`
Inter weight 400 `ink-faint`. Multiple sources separated by `; ` (semicolon
+ space).

### Citation rules

- **Primary first.** The Canadian primary source (StatCan, BoC, OSFI,
  CMHC, DoF, PBO, provincial finance, C.D. Howe BCC) always leads.
- **Derived inputs second.** Consensus / market data feeds (Bloomberg,
  Reuters, FRED for US comparators) come after, semicolon-separated,
  uncapitalized as a continuation clause.
- **Table number where applicable.** For StatCan: `Table NN-NN-NNNN-NN`.
  For BoC Valet: `BoC Valet [series_id]`. We are precise.
- **No bank morning-note citations.** Hard rule from EDR.

### Source-line as a typographic ritual

The Economist's Daily Chart treats its source line as a typographic
signature — a small, consistent, citation-as-discipline element. We adopt
that posture. Our source line is small, gray, lowercase except for proper
nouns, single line where possible. It is not styled to be impressive; it
is styled to be **invariant**. Readers learn to trust it.

### Link affordance

Where a primary source has a stable URL (e.g., a StatCan table page), the
table number is a link, styled per design-system.md Section 6 tertiary-
link rule: `ink-faint` text with `accent` underline at 1px offset 2px. Hover
darkens the underline. We do not blue-link inside the source line; the
underline carries the affordance.

Bloomberg / Reuters consensus feeds typically do not have a stable public
URL — the citation is plain text, not linked. That is honest.

---

## 9. Worked example: GDP basics page, all six panels blocked out

Per Section 4.1 of `editorial/dashboard_purpose.md`. For each panel, the
art-director spec is:

- Panel eyebrow / title slot
- Chart type and primary series
- Latest-print callout structure (or editorial status line)
- Annotations / direct labels concept (visual treatment only — wording is
  `writer`'s)
- Color assignments from the chart palette
- Vintage and source

> Sections 9.A and 9.B (below) extend the same per-panel spec format to
> the Inflation and Labour basics pages. The GDP worked example here
> remains the canonical reference for the panel grammar; Inflation and
> Labour inherit the grammar and add per-section visual rules.

### Panel 1 — Headline real GDP

- **Eyebrow:** `HEADLINE REAL GDP`
- **Title slot:** active-voice sentence about the latest m/m + q/q print.
  Two-line max.
- **Chart type:** Dual-frequency time series. Monthly bars (or thin
  columns) for monthly m/m %; quarterly Q/Q SAAR overlaid as a thicker
  line. Last 5 years on the x-axis. Y-axis: percent, zero line drawn in
  `ink-muted`.
- **Series colors:**
  - Monthly m/m bars: `series-1` (deep blue, the section accent).
  - Quarterly Q/Q SAAR line: `series-1` at 1.5px solid, weight 500.
  - Recession bands per design-system.md: `ink` at 6% opacity.
- **Direct labels:** "Monthly m/m" on the bars (placed in whitespace at
  most recent bar); "Quarterly Q/Q SAAR" on the line (placed at right
  terminus, in `series-1`, weight 500).
- **Annotations:** One annotation on the most recent monthly print:
  date, value, and revision tag if applicable. Anchor by leader to the
  bar.
- **Callout:**
  - Big number: latest m/m, e.g., `+0.2%`
  - Unit: `month-over-month, March 2026`
  - Direction row: `[arrow up] +0.1pp vs Feb  |  Beat consensus by
    0.1pp[c]   [Revised up]`
- **Vintage:** `AS OF May 1, 2026 / Reference: Mar 2026`
- **Source:** `Statistics Canada Table 36-10-0434-01; consensus via
  Bloomberg.`

### Panel 2 — Industry vs expenditure cross-check

- **Eyebrow:** `INDUSTRY VS EXPENDITURE`
- **Title slot:** active-voice sentence comparing the two cuts.
- **Chart type:** Two-line time series, same plot. Monthly GDP by
  industry vs. quarterly GDP by expenditure (resampled to the same
  frequency by either using the quarterly series step-held or annotated
  appropriately — chart-builder's call after seeing the data, but the
  spec is "two lines, eye-comparable").
- **Series colors:**
  - Industry: `series-1` (deep blue, lead series).
  - Expenditure: `series-7` (slate, contextual).
- **Direct labels:** "By industry" and "By expenditure" at the line
  termini.
- **Annotations:** A single highlighted region (light `ink` 6% opacity
  wash) over the most recent quarter where the two cuts disagree, with
  an annotation showing the reconciliation gap.
- **Callout:** Editorial status line, not a numeric callout:
  > *Cross-check: Industry and expenditure cuts agree in direction this
  > quarter; gap of 0.1pp on the level, within typical range.*
- **Vintage:** Two stamps stacked because two series:
  ```
  AS OF
  Industry: May 1, 2026 (Mar 2026)
  Expenditure: May 30, 2026 (Q1 2026)
  ```
- **Source:** `Statistics Canada Tables 36-10-0434-01 and 36-10-0104-01.`

### Panel 3 — Contributions to quarterly growth

- **Eyebrow:** `CONTRIBUTIONS TO GROWTH`
- **Title slot:** active-voice sentence about what drove the latest
  quarter.
- **Chart type:** Stacked / diverging horizontal bar chart. Six bars
  for the most recent quarter: consumption, government, GFCF, inventories,
  exports, imports. Imports shown as negative. Sum equals the headline
  Q/Q SAAR (annotated at the top as a total bar).
- **Series colors:** Categorical — `series-1` through `series-6` mapped
  to the six categories in EDR order. Imports rendered with negative
  values so the bar extends leftward from the zero axis in `series-6`.
- **Direct labels:** Each bar labeled at its terminus with the category
  name (Inter `label` 13px, color = series color) and the contribution
  value (Inter `mono-sm` tabular, `ink`).
- **Annotations:** A small annotation under the total bar indicating the
  full Q/Q SAAR: e.g., `Total Q/Q SAAR: +1.4%`.
- **Callout:**
  - Big number: `+1.4%`
  - Unit: `quarterly, annualized, Q1 2026`
  - Direction row: `[arrow up] +0.6pp vs Q4 2025  |  Beat consensus by
    0.2pp[c]`
- **Vintage:** `AS OF May 30, 2026 / Reference: Q1 2026`
- **Source:** `Statistics Canada Table 36-10-0104-01.`

### Panel 4 — Per-capita real GDP

- **Eyebrow:** `PER-CAPITA REAL GDP`
- **Title slot:** active-voice sentence about per-capita vs aggregate
  divergence.
- **Chart type:** Side-by-side dual-line time series in one plot:
  aggregate real GDP Y/Y vs per-capita real GDP Y/Y. Last 8 years.
- **Series colors:**
  - Aggregate: `series-7` (slate, contextual).
  - Per-capita: `series-1` (deep blue, the focus).
- **Direct labels:** Line termini.
- **Annotations:** A small region label (whitespace placement) calling
  out the consecutive-quarter contraction count, with a leader to the
  most recent per-capita data point.
- **Callout:**
  - Big number: per-capita Y/Y, e.g., `-1.0%`
  - Unit: `year-over-year, Q1 2026`
  - Direction row: `[arrow down] 7 consecutive quarters of contraction`
  - (No surprise field — per-capita is a derived calculation not directly
    forecast.)
- **Vintage:** `AS OF May 30, 2026 / Reference: Q1 2026`
- **Source:** `Statistics Canada Tables 36-10-0104-01 and 17-10-0009-01;
  per-capita calculation by macro-research-department.`
- **Methodology link:** Important here — open the drawer to explain the
  population denominator choice (mid-period estimate vs end-period;
  total population vs working-age).

### Panel 5 — Versus BoC potential

- **Eyebrow:** `OUTPUT GAP`
- **Title slot:** active-voice sentence about the gap to potential.
- **Chart type:** Two-line plot with a fan or shaded difference between
  them. Real GDP level vs BoC potential-output level, both indexed to
  2019Q4 = 100. The shaded area between them in `ink` 6% opacity
  represents the gap.
- **Series colors:**
  - Real GDP: `series-1` (deep blue).
  - BoC potential: `series-7` (slate, dashed `4 2`).
- **Direct labels:** Both line termini. The shaded region carries a
  rotated label `Output gap` in `micro` `ink-faint`.
- **Annotations:** The most recent output-gap value annotated directly,
  with vintage of the BoC potential estimate (since it updates
  quarterly on MPR cadence).
- **Callout:**
  - Big number: output gap %, e.g., `-0.5%`
  - Unit: `Q1 2026, BoC central estimate`
  - Direction row: `[arrow up] +0.2pp vs Q4 2025`
  - (Surprise field collapsed — no consensus on output gap.)
- **Vintage:** Two-anchor:
  ```
  AS OF
  Real GDP: May 30, 2026 (Q1 2026)
  Potential: Apr 16, 2026 MPR
  ```
- **Source:** `BoC Valet INDINF_OUTGAPMPR_Q; Statistics Canada Table
  36-10-0104-01.`

### Panel 6 — Recession state

- **Eyebrow:** `RECESSION STATE`
- **Title slot:** active-voice sentence about current cycle state.
- **Chart type:** Small horizontal timeline / Gantt-like visual showing
  C.D. Howe BCC-dated recessions and expansions over the last 20+
  years. Current state highlighted at the right end.
- **Series colors:** Recession bands in `ink` 12% opacity (slightly
  heavier than chart-background recession bands because here they are
  the data, not the context). Expansion periods unfilled. Current
  state's marker in section accent (`series-1`).
- **Direct labels:** Each recession labeled with its dates in `micro`
  `ink-faint`. The current state labeled with its start date.
- **Annotations:** A single dated annotation on the most recent BCC
  communique:
  > *C.D. Howe BCC, [date]: classification unchanged; expansion
  > continues from [start date].*
- **Callout:** Editorial status line, not numeric:
  > *Current state: **Expansion** since 2020Q3. Amplitude, duration,
  > scope at trough: per BCC's most recent dating committee minutes.*
- **Vintage:** `AS OF [most recent BCC communique date]`
- **Source:** `C.D. Howe Business Cycle Council communiques.`

---

---

## 9.A Inflation basics page, all six panels blocked out

Per Section 4.2 of `editorial/dashboard_purpose.md`. Section accent:
`series-2` (burnt orange, `#C9772A`).

**Section-level visual rules (Inflation only).**

- **Color encoding stays direction-of-print, not editorial valence.** A
  CPI print *above* consensus prints `neg` color on the surprise field
  only when the editorial section convention is "above-target persistence
  is bad" — which Inflation prose typically reads that way. Per Section 4
  of this template, art-director does not flip color encoding by section;
  the per-section direction-vs-valence call is `writer`'s on each refresh.
  Inflation is the section where this tension is loudest. Hold the line:
  color follows direction-of-print, prose carries valence.
- **Target reference line.** Every time-series chart on the Inflation
  page renders the 2% BoC target as a horizontal reference line at
  `ink-faint`, 1px solid, with a small right-rail label `BoC target 2%`
  in `micro` `ink-faint`. The 1% and 3% control-range bounds appear as
  1px dashed (`2 2`) lines in `rule` color, no label. This reference
  scaffold appears on panels 1, 2, 4, 6 (every chart with a Y/Y %
  vertical axis). It does not appear on panel 3 (breadth, which is a
  share-of-basket composition, not a Y/Y rate) or on panel 5
  (expectations, which has different axis logic — see below).
- **3M annualized vs Y/Y display.** Where 3M AR is shown (panel 1, panel
  2 if v1 ships it), 3M AR is `series-2` weight 500 1.5px solid, Y/Y is
  `series-2` at 60% opacity, 1.5px solid. The two reads share a y-axis
  and color family; the lighter line is the slower, the heavier is the
  faster. No legend; line termini direct-label `3M annualized` and
  `year-over-year`.

### Inflation Panel 1 — Headline CPI

- **Eyebrow:** `HEADLINE CPI`
- **Title slot:** active-voice sentence about the latest m/m or Y/Y +
  3M AR pair. Writer.
- **Chart type:** Dual-line time series. Y/Y headline CPI as the lighter
  weight; 3M annualized headline CPI as the heavier weight. Last 5 years
  on the x-axis. Y-axis: percent. Horizontal reference scaffold: 2%
  target solid `ink-faint`, 1% and 3% bounds dashed `rule`.
- **Series colors:**
  - 3M AR: `series-2` (burnt orange, section accent), 1.5px solid, weight 500.
  - Y/Y: `series-2` at 60% opacity, 1.5px solid.
- **Direct labels:** `3M annualized` and `year-over-year` at line
  termini.
- **Annotations:** Most recent print annotated with date + value on the
  Y/Y line (the headline read). One small whitespace annotation calling
  out a notable acceleration or deceleration episode in the trailing 12
  months when present; placement is right-rail or left-rail in the
  margin gutter, never overlaying the data.
- **Callout:**
  - Big number: latest Y/Y, e.g., `2.4%`
  - Unit: `year-over-year, March 2026 (3M AR: +2.1%)`
  - Direction row: `[arrow flat] +0.0pp vs Feb  |  In line with consensus[c]`
- **Vintage:** `AS OF Apr 15, 2026 / Reference: Mar 2026`
- **Source:** `Statistics Canada Table 18-10-0004-01; consensus via
  Bloomberg.`

### Inflation Panel 2 — BoC preferred core measures

- **Eyebrow:** `CORE-TRIM AND CORE-MEDIAN`
- **Title slot:** active-voice sentence on the trim+median lead. Writer.
- **Chart type:** Time-series **trio**, but visual hierarchy is
  deliberately uneven. Core-trim and core-median lead at full
  prominence; common is shown as a **faded historical anchor** that
  defaults to invisible on first render and surfaces on hover/footnote.
  Per EDR 4.2 element 2: trim+median is the BoC's currently preferred
  pair; common has been deprioritized since late 2022. The chart honors
  that hierarchy visually.
- **Series colors:**
  - Core-trim: `series-2` (burnt orange), 1.5px solid, weight 500.
  - Core-median: `series-3` (sage green), 1.5px solid, weight 500.
  - Core-common (faded historical): `series-7` (slate) at 30% opacity,
    1px solid, **rendered behind** trim and median in z-order.
- **Common-treatment rule.** The common line is present but visually
  recedes. A one-line note in the chart-foot reads (writer): *"Core-
  common shown faded; BoC has deprioritized it since late 2022."*
  Hover over the common line raises a tooltip with its current value
  and the deprioritization note. The chart does NOT hide common
  entirely (we are honest about the data history) and does NOT promote
  common to equal weight (we follow the BoC's lead).
- **Direct labels:** `Trim` and `Median` at line termini in their
  series colors, weight 500. `Common` label optional, at terminus in
  `series-7` 60% opacity weight 400 — small enough to read as
  historical context, not as a third primary read.
- **Annotations:** Most recent print annotated on the **higher of trim
  vs median** (the load-bearing read), single annotation only — not
  three.
- **Callout:**
  - Big number: average of trim and median, e.g., `2.8%`
  - Unit: `core-trim & core-median average, Y/Y, March 2026`
  - Direction row: `[arrow down] -0.1pp vs Feb  |  In line with
    consensus[c]`
- **Vintage:** `AS OF Apr 15, 2026 / Reference: Mar 2026`
- **Source:** `Statistics Canada Table 18-10-0256-01; consensus via
  Bloomberg.`
- **Methodology link:** Important — drawer explains trim/median/common
  construction and the BoC's 2022 deprioritization of common.

### Inflation Panel 3 — Breadth

- **Eyebrow:** `BREADTH`
- **Title slot:** active-voice sentence on the share of basket
  components running above 3%. Writer.
- **Chart type:** **Stacked-area composition** chart over time
  showing the three-band basket-share decomposition: share of CPI
  basket components with Y/Y above 3%, between 1-3%, below 1%. Last
  5 years on x-axis. Y-axis: share of basket (0% to 100%). The
  three bands stack to 100% at every t.

  **Explicitly NOT a four-state classifier visual.** Per EDR 4.2
  element 3 (and the May 2026 verification resolution), the
  four-state typology (broad-based pressure, broad-based softening,
  clustered near target, polarized) was retired as a forced
  classification. It survives as prose vocabulary when the data
  *happens* to match a state cleanly; it does not survive as a chart
  shape. The breadth chart shows the three basket shares directly
  over time and lets the reader see what they see. Writer may invoke
  the four-state words in prose when warranted; the chart does not
  pre-classify.

- **Series colors / band fills:**
  - Above 3% (top band): `series-2` (burnt orange, section accent),
    fill at 70% opacity.
  - 1-3% (middle band): `neutral-soft` (`#DDE0E4`), fill at 100%.
  - Below 1% (bottom band): `series-5` (teal), fill at 50% opacity.
  - Band edges (where bands meet): 1px in `surface` (the page
    surface, drawn over the bands so the boundary reads cleanly).
- **Direct labels:** Each band labeled at the right rail with its
  current share, e.g., `Above 3%: 28%` / `1-3%: 54%` / `Below 1%:
  18%`. Labels in `label` size, weight 500, color matching the band
  fill at full opacity.
- **Annotations:** A single annotation on the most recent vertical
  slice marking the current above-3% share. No annotation on
  historical episodes in basics (deep-dive territory).
- **Callout:**
  - Big number: above-3% share, e.g., `28%`
  - Unit: `of CPI basket components, Y/Y above 3%, March 2026`
  - Direction row: `[arrow down] -3pp vs Feb` (no consensus on
    breadth — surprise field collapses)
- **Vintage:** `AS OF Apr 15, 2026 / Reference: Mar 2026`
- **Source:** `Statistics Canada Table 18-10-0004-01; component-share
  calculation by macro-research-department.`
- **Methodology link:** Important — drawer explains basket-share
  construction (weighted vs unweighted; which sub-aggregates are
  included).

### Inflation Panel 4 — Sub-aggregates

- **Eyebrow:** `SUB-AGGREGATES`
- **Title slot:** active-voice sentence on which sub-aggregate is
  carrying the print. Writer.
- **Chart type:** **Small-multiple grid** of five mini time series,
  one per sub-aggregate (shelter, services ex-shelter, goods ex-energy,
  food, energy). 2-column-by-3-row grid inside the panel card; the
  sixth cell is occupied by a small legend / scale reference.
  Each mini-chart is a Y/Y line at 2-year window with the 2% target
  reference line.

  Where the "ex-" aggregates (services-ex-shelter, goods-ex-energy)
  do not ship in v1 (per EDR 4.2 element 4: gated on reproducible
  basket-weight construction), the relevant cells render the all-
  services and all-goods series directly with a `micro` `ink-faint`
  cell-foot note: *"All-services shown; services ex-shelter deferred
  to v1.5."* Writer owns the note wording; art-director owns the
  presence of the slot.

- **Series colors:** All five mini-lines use `series-2` (the section
  accent) at 1.5px solid weight 500. This is a deliberate restraint
  decision: the small-multiple grid is the comparison; rainbow-
  encoding the sub-aggregates would compete with the grid structure.
- **Direct labels:** Each mini-chart titled at its top-left in
  `label` size weight 500 `ink`: `Shelter` / `Services ex-shelter` /
  etc. Most recent value labeled at the right terminus of each line
  in `mono-sm` tabular `ink`.
- **Annotations:** None inside cells (the grid is the annotation).
  A single chart-level annotation in the gutter calls out which cell
  is currently the driver of the headline.
- **Callout:** Editorial status block (no single number summarizes
  the grid):
  - Status label: `SUB-AGGREGATE DRIVER`
  - Status line: writer-filled, e.g., *"Shelter and services drive
    the residual stickiness; goods deflation continues."*
  - Context line: writer-filled, mortgage-interest-cost decomposition
    note where relevant.
- **Vintage:** `AS OF Apr 15, 2026 / Reference: Mar 2026`
- **Source:** `Statistics Canada Table 18-10-0004-01.`
- **Methodology link:** Drawer explains shelter decomposition
  (mortgage interest cost via Table 18-10-0004-01 sub-components)
  and any basket-weighted derivations.

### Inflation Panel 5 — Inflation expectations

- **Eyebrow:** `EXPECTATIONS`
- **Title slot:** active-voice sentence on CSCE consumer 1y/5y and
  BOS firms expecting >3%. Writer.
- **Chart type:** **Split-panel composite** — two stacked mini-charts
  inside one panel card.
  - Top mini: CSCE consumer expectations, 1-year and 5-year, time
    series over last 5 years.
  - Bottom mini: BOS share of firms expecting CPI >3%, time series
    over last 5 years, with a small bar-strip companion showing the
    current BOS distribution buckets (% expecting 0-1%, 1-2%, 2-3%,
    >3%) at the right rail of the bottom mini.
- **Series colors:**
  - CSCE 1y: `series-2` (burnt orange), 1.5px solid weight 500.
  - CSCE 5y: `series-2` at 60% opacity, 1.5px solid.
  - BOS share >3% (bottom mini line): `series-4` (plum), 1.5px solid
    weight 500.
  - BOS distribution bars (right rail of bottom mini): single-color
    `series-4` fill at increasing opacity per bucket (20% / 40% /
    60% / 80% / 100%) so the >3% bucket reads heaviest.
- **Reference lines:** Both minis carry the 2% target line at
  `ink-faint` solid.
- **Direct labels:** Line termini on all three time-series lines.
  BOS distribution bars labeled with bucket name and current %.
- **Annotations:** Top mini gets an annotation on the most recent
  CSCE 1y point (the more cyclically active series). Bottom mini
  annotates the most recent BOS reading.
- **Callout:**
  - Big number: BOS share of firms expecting >3%, e.g., `38%`
  - Unit: `BOS firms expecting CPI >3%, Q1 2026`
  - Direction row: `[arrow down] -4pp vs Q4 2025` (no consensus on
    BOS — surprise field collapses)
- **Vintage:** Two stamps:
  ```
  AS OF
  CSCE: Apr 21, 2026 (Q1 2026)
  BOS: Apr 7, 2026 (Q1 2026)
  ```
- **Source:** `Bank of Canada Canadian Survey of Consumer Expectations;
  Bank of Canada Business Outlook Survey.`

### Inflation Panel 6 — Pass-through watch

- **Eyebrow:** `PASS-THROUGH WATCH`
- **Title slot:** active-voice sentence on which pass-through channel
  is active. Writer.
- **Chart type:** **Side-by-side strip charts** — two narrow time
  series sitting in a 2-column sub-grid inside the panel card. Each
  strip plots two series on a shared y-axis.

  Strip A (left): USDCAD Y/Y vs goods-ex-energy CPI Y/Y.
  Strip B (right): LFS-Micro composition-adjusted wage growth Y/Y
  vs services-ex-shelter CPI Y/Y.

  **Explicitly no regression in basics.** Per EDR 4.2 element 6: no
  regression line, no R-squared, no coefficient called out. The
  visual is the *co-movement read*; the interpretation lives in
  writer prose. If the chart begs for a regression, it's deep-dive
  territory.

- **Series colors (consistent across the two strips so the eye
  carries the convention):**
  - Driver (USDCAD in A, wage growth in B): `series-7` (slate),
    1.5px solid weight 500.
  - Response (goods-ex-energy CPI in A, services-ex-shelter CPI
    in B): `series-2` (burnt orange, section accent), 1.5px solid
    weight 500.
- **Strip layout.** Each strip is ~200px wide, 120px tall (narrower
  aspect than the standard panel chart). The two strips share the
  panel card and sit `s-4` (16px) apart horizontally. They do **not**
  share a y-axis (different units; USDCAD Y/Y and wage growth Y/Y
  are not directly comparable). Each strip carries its own y-axis on
  its left edge, light treatment (no axis line; just tick labels in
  `mono-xs` `ink-faint`).
- **Direct labels:** Each strip titled at the top-left in `label`
  weight 500: `USDCAD vs goods ex-energy` and `Wages vs services
  ex-shelter`. Line termini direct-labeled in series colors weight
  500.
- **Annotations:** A single annotation per strip marking the most
  recent values of both lines, placed in the right gutter.
- **Callout:** Editorial status block (no single number):
  - Status label: `PASS-THROUGH READ`
  - Status line: writer-filled, e.g., *"Goods-ex-energy CPI follows
    USDCAD weakness with a 6-month lag; services-ex-shelter sticky
    against wage moderation."*
  - Context line: writer-filled methodological caveat.
- **Vintage:** Two stamps:
  ```
  AS OF
  CPI: Apr 15, 2026 (Mar 2026)
  USDCAD/Wages: May 1, 2026 (Apr 2026)
  ```
- **Source:** `Statistics Canada Tables 18-10-0004-01 and 14-10-0064-01;
  Bank of Canada Valet FXUSDCAD; LFS-Micro composition-adjusted wage
  series, macro-research-department construction.`
- **Methodology link:** Important — drawer explains co-movement reads
  are descriptive, not causal, and points to Pillar D (productivity
  gap) for the structural pass-through story.

---

## 9.B Labour basics page, all six panels blocked out

Per Section 4.3 of `editorial/dashboard_purpose.md` and
`research/wave2_labour_methodology.md`. Section accent: `series-3` (sage
green, `#5B7553`).

**Section-level visual rules (Labour only).**

- **Per-capita is the signature visual.** Panel 2 (per-capita) is the
  section's analytical centerpiece. Where other sections distribute
  visual weight across panels, the Labour basics page deliberately
  invests in panel 2's visual treatment — the headline question of the
  section ("is per-capita output recovering through population
  deceleration or through aggregate weakness?") sits in that panel. See
  Panel 2 spec below for the elevated treatment.
- **NSA/SA mixing is disclosed visually.** Panels mixing NSA (JVWS
  vacancies) and SA (LFS) series carry an explicit chart-foot note in
  `micro` `ink-faint` stating the mix: e.g., *"Vacancy rate: NSA, 3M MA.
  Unemployment rate: SA, 3M MA."* Per Wave 2 methodology Section 2.2.
  This is not optional; it appears on panels 4 and on the Beveridge-
  curve subview within panel 4.
- **Population denominator stamping.** Where a per-capita measure is
  shown, the panel methodology link's drawer always names the
  denominator: total population, mid-period interpolated to monthly,
  per Wave 2 Section 1.3. The drawer is the place for this; the chart
  does not need to inline-cite the denominator.
- **3M-MA convention.** V/U and the Beveridge curve are both
  3M-MA-smoothed per Wave 2 Section 2.1 and 3.1. The chart legend (or
  chart-foot note) always names the smoothing window.

### Labour Panel 1 — LFS headline

- **Eyebrow:** `LFS HEADLINE`
- **Title slot:** active-voice sentence on employment, unemployment,
  participation. Writer.
- **Chart type:** **Layered time-series with secondary axis**. Primary
  axis (left, percent): unemployment rate (the institutional headline
  anchor per EDR 4.3) and employment rate, last 5 years. Secondary
  axis (right, percent): participation rate, scaled tighter
  (62-68% typical range) to make moves readable. Employment level
  Y/Y is not on this chart — it lives in Panel 2 as the per-capita
  driver.
- **Series colors:**
  - Unemployment rate: `series-3` (sage green, section accent), 1.5px
    solid weight 500. The headline series.
  - Employment rate: `series-7` (slate), 1.5px solid weight 400.
  - Participation rate: `series-3` at 60% opacity, 1px dashed
    (`4 2`), weight 400. Secondary axis; visually subordinate.
- **Direct labels:** Line termini for all three. Participation
  labeled with `(right axis)` in `micro` `ink-faint` immediately
  after the series name.
- **Annotations:** Most recent print annotated on the unemployment
  line only — the headline read. Other two lines carry just terminus
  labels.
- **Callout:**
  - Big number: unemployment rate, e.g., `6.4%`
  - Unit: `unemployment rate, April 2026`
  - Direction row: `[arrow up] +0.1pp vs Mar  |  In line with
    consensus[c]`
- **Vintage:** `AS OF May 8, 2026 / Reference: Apr 2026`
- **Source:** `Statistics Canada Table 14-10-0287-01; consensus via
  Bloomberg.`

### Labour Panel 2 — Per-capita panel (signature)

This is the section's signature visual. Treatment is elevated relative
to the other five panels.

- **Eyebrow:** `PER-CAPITA — SIGNATURE` (the suffix is permanent and
  appears only on this panel; it signals to the reader that this is
  the analytical centerpiece of the section).
- **Title slot:** active-voice sentence on the aggregate-vs-per-capita
  divergence. Writer.
- **Chart type:** **Side-by-side small multiples**, two cells, per
  Wave 2 Section 1.5.
  - Left cell: employment Y/Y (line) and per-capita employment Y/Y
    (line) on a shared y-axis.
  - Right cell: aggregate hours Y/Y (line) and per-capita hours Y/Y
    (line) on a shared y-axis.

  Each cell is ~210px wide, 200px tall (taller than the standard
  panel chart aspect — the small-multiple cells are deliberately
  larger here than the strip-charts on Inflation Panel 6, because
  this is the signature visual and gets the breathing room). The
  two cells share the panel card and sit `s-4` (16px) apart.

- **Series colors (consistent across the two cells so the eye carries
  the aggregate-vs-per-capita read across both):**
  - Aggregate series (emp Y/Y in left, hours Y/Y in right): `series-7`
    (slate), 1.5px solid weight 400. The denominator-irrelevant series.
  - Per-capita series (per-capita emp Y/Y in left, per-capita hours
    Y/Y in right): `series-3` (sage green, section accent), 2px solid
    weight 600. The load-bearing series; deliberately the **heaviest
    line on the entire Labour basics page**, signaling its centrality.
- **Zero-line treatment.** Each cell has a horizontal zero line in
  `ink-muted`, 1px solid. The visual hop from positive to negative on
  per-capita is the editorial drama of this panel; the zero line earns
  its full-prominence treatment here (other panels can be subtler).
- **Shaded contraction regions.** Where per-capita is below zero, the
  area between the per-capita line and the zero line fills with
  `neg-soft` (`#EAD3CE`) at 40% opacity. This is the only place on
  the basics layer where a soft-color area fill carries editorial
  weight — restricted to this panel by design.
- **Direct labels:** Line termini in their series colors. Aggregate
  series labeled `Aggregate` in slate weight 400; per-capita series
  labeled `Per-capita` in sage green weight 600 (matching its line
  weight prominence).
- **Annotations:** Each cell carries one annotation: the
  consecutive-quarter (or month, for monthly series) count of per-
  capita contraction, placed at the right rail with a thin leader
  to the most recent per-capita data point. Wording owned by writer.
  Per EDR 4.3 boundary rule: the annotation surfaces the divergence;
  it does not adjudicate cause. Population-deceleration-vs-aggregate-
  weakness adjudication is Pillar E.
- **Callout:**
  - Big number: per-capita employment Y/Y, e.g., `-0.6%`
  - Unit: `per-capita employment Y/Y, April 2026`
  - Direction row: `[arrow down] N months of per-capita contraction`
  - (No surprise field — per-capita is a derived calculation, not
    directly forecast.)
- **Vintage:** Two stamps (population estimates and LFS print on
  different cadences):
  ```
  AS OF
  LFS: May 8, 2026 (Apr 2026)
  Population: Mar 28, 2026 (Q1 2026, interpolated)
  ```
- **Source:** `Statistics Canada Tables 14-10-0287-01, 14-10-0289-01,
  17-10-0009-01; per-capita construction by macro-research-department
  per Wave 2 Brief 2A.5.`
- **Methodology link:** Important — drawer explains the subtractive
  form, the linear interpolation of quarterly population to monthly,
  the open-quarter extrapolation, and the vintage-stamp logic on
  per-capita observations (per Wave 2 Section 1.5 and open question
  1 resolution).

### Labour Panel 3 — Wage band

- **Eyebrow:** `WAGE BAND`
- **Title slot:** active-voice sentence on wage dispersion across the
  four measures and comparison to services CPI. Writer.
- **Chart type:** **Time-series band** — four wage measures (LFS all-
  employee, LFS permanent, SEPH, BoC composition-adjusted LFS-Micro)
  plotted as a single shaded band defined by min-to-max envelope at
  each t. A median line through the band carries the central read.
  CPI services Y/Y plotted as a comparator line in a different color.
  Last 5 years on x-axis.
- **Series colors:**
  - Band fill: `series-3` at 20% opacity. The envelope of the four
    wage measures.
  - Band edges (min and max): `series-3` at 40% opacity, 1px solid.
  - Median wage line: `series-3` (sage green), 1.5px solid weight 500.
    The load-bearing read inside the band.
  - CPI services Y/Y comparator: `series-2` (burnt orange — the
    Inflation section accent, deliberately referenced so the reader
    sees this is the comparator-from-another-section), 1.5px solid
    weight 500.
- **Direct labels:** `Wage band (4 measures)` and `Median wage` at
  the line termini in `series-3`; `CPI services Y/Y` at its terminus
  in `series-2`. A small caption in chart whitespace identifies the
  four measures in the band: `LFS all-emp / LFS perm / SEPH / LFS-
  Micro adj.`
- **Annotations:** Annotation on the most recent median wage point
  and the most recent CPI services point — the wage-versus-prices
  read is the editorial point of this panel.
- **Callout:**
  - Big number: median wage growth Y/Y, e.g., `3.8%`
  - Unit: `median of four wage measures, Y/Y, April 2026`
  - Direction row: `[arrow down] -0.2pp vs Mar  |  Range: 3.2-4.4%`
    (no consensus on the band median — surprise field replaced by
    the range read)
- **Vintage:** Stacked stamps for the four cadences (LFS monthly,
  SEPH monthly with longer lag, LFS-Micro quarterly):
  ```
  AS OF
  LFS: May 8, 2026 (Apr 2026)
  SEPH: May 29, 2026 (Feb 2026)
  LFS-Micro: Apr 30, 2026 (Q1 2026)
  ```
- **Source:** `Statistics Canada Tables 14-10-0064-01 and 14-10-0203-
  01; LFS-Micro composition-adjusted wage series, macro-research-
  department construction; CPI services from Table 18-10-0004-01.`
- **Methodology link:** Drawer explains the four-measure band
  construction and LFS-Micro composition adjustment.

### Labour Panel 4 — Vacancies and slack

This panel ships as a **composite** — V/U time series + Beveridge-curve
scatter — because the two reads are conceptually paired (both speak to
labour-market tightness) and Wave 2 methodology Section 2 and Section 3
spec them together.

- **Eyebrow:** `VACANCIES AND SLACK`
- **Title slot:** active-voice sentence on V/U state and Beveridge-
  curve position. Writer.
- **Chart type:** **Composite two-sub-view layout** inside one panel
  card.
  - Sub-view A (top, ~60% of panel chart height): V/U ratio time
    series, 3M MA, last ~10 years (JVWS series begins 2015 per Wave 2
    Section 2.4 caveat 1). Historical-anchor bands shaded as
    horizontal background regions (NOT current-state classifier — per
    Wave 2 Section 2.3 and the documented propagation defect against
    US-transferred thresholds).
  - Sub-view B (bottom, ~40% of panel chart height): Beveridge-curve
    scatter. X-axis: SA unemployment rate, 3M MA. Y-axis: NSA vacancy
    rate, 3M MA. 12-month trail as connected path; latest month
    highlighted; prior history (2015-present, minus the Apr-Sep 2020
    JVWS structural gap) shown as faded background points color-coded
    by year.
- **Series colors:**
  - V/U line (sub-view A): `series-3` (sage green), 1.5px solid
    weight 500.
  - Historical-anchor band fills (sub-view A): single-color graduated
    fill — `rule-faint` at 100% for `<0.30` slack band, increasing
    opacity through bands, peaking at `series-3` at 15% for the
    `>=0.80` exceptionally-tight band. Bands are background, not data.
  - Beveridge-curve background points (sub-view B): faded, color-coded
    by year using the sequential `series-1` ramp (deep-blue ramp from
    the design-system Section 5.2: `#EDF2F7 -> ... -> #1F4E79`).
    Earlier years are paler; recent years darker. This is the
    canonical use of the sequential ramp on the basics layer.
  - Beveridge-curve trail (sub-view B): `series-3` (sage green) line,
    1.5px solid weight 500, connecting the most recent 12 months.
  - Latest month point (sub-view B): `series-3` filled circle, 6px
    diameter with 1.5px `surface` halo so it reads cleanly against
    the trail.
- **Reference labels (sub-view A):** Band labels at the right rail in
  `micro` `ink-faint`: `Slack` / `Below balance` / `Approaching
  balance` / `Tight` / `Exceptionally tight`. Per Wave 2 Section 2.3
  band names — strictly historical anchors, not classification claims.
- **Direct labels:** V/U line terminus labeled with current value
  in `series-3` weight 500. Beveridge-curve latest point labeled with
  date (month/year).
- **Annotations:** One annotation on the V/U sub-view marking the
  most recent reading. One annotation on the Beveridge-curve trail
  marking the direction of motion over the last 6 months (writer:
  "loosening toward 2018-2019 territory" or similar). The post-COVID
  outward Beveridge-curve shift is permanently annotated in
  whitespace per Wave 2 Section 3.4 caveat.
- **NSA/SA disclosure note (chart-foot):** *"Vacancy rate: NSA, 3M MA
  (JVWS, structural gap Apr-Sep 2020). Unemployment rate: SA, 3M MA
  (LFS)."* Writer-styled wording; art-director-styled placement and
  typography.
- **Callout:**
  - Big number: V/U ratio, e.g., `0.47`
  - Unit: `V/U ratio, 3M MA, April 2026 (in 2018-2019 BoC tightening
    cycle range)`
  - Direction row: `[arrow down] -0.04 vs prior 3M  |  Below balance`
    (no consensus on V/U — surprise field replaced by the band
    reference)
- **Vintage:** Two stamps:
  ```
  AS OF
  Vacancy: May 1, 2026 (Feb 2026 print; ~3-month lag)
  Unemployment: May 8, 2026 (Apr 2026)
  ```
- **Source:** `Statistics Canada Tables 14-10-0371-01 (JVWS) and
  14-10-0287-01 (LFS).`
- **Methodology link:** Important — drawer explains 3M MA convention,
  NSA/SA mix, Canadian-calibrated historical-anchor bands (NOT current-
  state classifier), 2015 series start, Apr-Sep 2020 structural gap,
  post-COVID Beveridge-curve outward shift, and NAIRU framing per
  Wave 2 Sections 2.3-2.5 and 3.4.

### Labour Panel 5 — Population and immigration (supply trajectory)

- **Eyebrow:** `SUPPLY TRAJECTORY`
- **Title slot:** active-voice sentence on PR + NPR composition and
  IRCC plan trajectory. Writer.
- **Chart type:** **Stacked-composition area chart** over time
  showing PR inflows and NPR inflows as a four-quarter trailing sum.
  PR stacked at the bottom, NPR on top. Last ~8 years to encompass
  the post-2022 NPR surge and the Oct 2024 levels-plan pivot. Y-axis:
  trailing-4Q inflow count (absolute numbers, not rates).
  Three **dated annotation lines** anchored at IRCC plan release
  dates, per Wave 2 Section 4.4: vertical dashed lines at each
  `release_date` in `ircc_levels_plan.json`, labeled with the plan
  vintage and short PR-target indicator. The Oct 2024 structural-
  break pivot gets a **heavier annotation style** (per Wave 2 Section
  4.4 item 2).
- **Series colors / band fills:**
  - PR (bottom band): `series-3` (sage green, section accent), fill
    at 60% opacity.
  - NPR (top band): `series-4` (plum), fill at 50% opacity.
  - Band edges: 1px `surface` overdraw at the boundary so the
    composition is legible.
- **IRCC annotation treatment.**
  - Standard plan-release annotation (e.g., 2023-2025 plan, 2024-2026
    plan): vertical dashed line in `ink-faint`, 1px dashed (`4 2`),
    spanning the chart height. Label at top of line in `label` size
    weight 400 `ink-faint`: e.g., `Nov 2022: 2023-2025 plan`. Date and
    label wording per writer.
  - Structural-break plan-release annotation (Oct 2024 pivot, marked
    `structural_break: true` in the JSON): vertical solid line in
    `accent` (the editorial red `#A6192E`), 1.5px solid, spanning
    chart height. Label at top in `label` size weight 500 `accent`:
    e.g., `Oct 2024: 2025-2027 plan — PR cap cut to 395k, NPR cap
    introduced`. This is the **only place on the basics layer** where
    `accent` color carries data-adjacent meaning; it is reserved for
    structural-break events and is intentionally rare. The reader
    learns the convention here and carries it forward.
  - Per Wave 2 Section 4.4 item 1, the annotation reads `release_date`
    + plan `vintage` + short PR-target indicator; writer composes the
    string from the JSON object's fields.
- **Companion target-table widget.** Per Wave 2 Section 4.4 item 3,
  a small table sits immediately below the chart inside the panel
  card, listing the current plan's PR and NPR targets for the next
  three years. Treatment: zebra-table per design-system.md Section 6
  table conventions, `surface-sunk` background, `micro` Inter mono
  for numerics, three rows: current plan year, next year, year after.
  Caption: `IRCC levels plan, vintage [plan_vintage], released
  [release_date].` Caption in `label` `ink-faint`.
- **Direct labels:** PR and NPR bands labeled at the right rail with
  their current trailing-4Q values, in band colors weight 500.
- **Callout:**
  - Big number: trailing-4Q total inflows, e.g., `975k`
  - Unit: `PR + NPR trailing-4Q inflows, through Q1 2026`
  - Direction row: `[arrow down] -85k vs prior 4Q` (no consensus —
    surprise field collapses)
- **Vintage:** Two stamps:
  ```
  AS OF
  Inflows: Mar 28, 2026 (Q1 2026)
  IRCC plan: Oct 24, 2024 (2025-2027 vintage)
  ```
- **Source:** `Statistics Canada Table 17-10-0040-01 (PR + NPR
  estimates); IRCC supplementary information for the 2025-2027
  Immigration Levels Plan; macro-research-department editorial
  maintenance of ircc_levels_plan.json.`
- **Methodology link:** Drawer explains the trailing-4Q construction,
  the PR/NPR category definitions, and the IRCC JSON structure (the
  drawer is the place for editorial-vs-pipeline-data distinction).

### Labour Panel 6 — Regional dispersion (four-province dumbbell)

- **Eyebrow:** `REGIONAL DISPERSION`
- **Title slot:** active-voice sentence on the four-province
  dispersion and the "loosening fastest" call-out. Writer.
- **Chart type:** **Four-row dumbbell** — one row per province (ON,
  QC, AB, BC). Each row plots two points connected by a line: current
  month unemployment rate (filled circle) and value 12 months ago
  (open circle). Per Wave 2 Section 5: concurrent national rate
  overlaid as a single horizontal reference line; trailing national
  rate is NOT a second overlay (Wave 2 Section 5.2 rationale).
- **Series colors:**
  - Current-month points (filled): `series-3` (sage green, section
    accent), 6px diameter circles.
  - 12-months-ago points (open): `series-3`, 5px diameter, 1.5px
    stroke, transparent fill — the "where it was" marker.
  - Dumbbell connecting lines: `series-3` at 60% opacity, 1.5px solid.
  - Direction-of-motion encoded in line: when the current value is
    *higher* than 12 months ago (rate rose, market loosened), the line
    is drawn in `neg` (`#B23A2F`) at 60% opacity; when current is
    *lower* (rate fell, market tightened), the line is `pos`
    (`#1F6B3A`) at 60% opacity; when within `0.3pp` tolerance per
    Wave 2 Section 5.3, the line stays `series-3` at 40% (no
    directional call). This is the only panel on the page where
    `pos`/`neg` color encoding appears on a line-as-data element,
    and it earns its place because the dumbbell IS a directional
    change visual.
  - National-rate overlay: vertical 1px solid line in `ink-muted`,
    spanning all four rows. Labeled `Canada: X.X%` at the top.
- **Province labels:** Province names at the left rail in `body-sm`
  weight 500 `ink`. Current values at the right of each filled circle
  in `mono-sm` tabular `ink`. 12-months-ago values at the left of
  each open circle in `mono-sm` tabular `ink-muted`.
- **Annotations:** A single annotation in the panel gutter calling
  out the "loosening fastest" province per Wave 2 Section 5.3 — only
  fires when `|delta_pct_pts| >= 0.3pp`, per the computed tolerance.
  Writer composes the wording from the computed CSV. Wave 2 fact-
  checker cross-references.
- **Callout:** Editorial status block (no single number summarizes
  four provinces):
  - Status label: `LOOSENING FASTEST` (or `TIGHTENING FASTEST` when
    that case fires; or `WITHIN NOISE BAND` when no province qualifies)
  - Status line: writer-filled, e.g., *"Alberta's unemployment rate
    rose 0.8 pp over the past year, the most among the four largest
    provinces."*
  - Context line: writer-filled, optionally referencing the national
    delta for comparison.
- **Vintage:** `AS OF May 8, 2026 / Reference: Apr 2026`
- **Source:** `Statistics Canada Table 14-10-0287-03 (provincial LFS).`
- **Methodology link:** Drawer explains the concurrent-vs-trailing
  overlay decision (Wave 2 Section 5.2), the 0.3pp call-out tolerance
  (Wave 2 Section 5.3), and the four-province cut rationale (Wave 2
  Section 5.5).

---

## 9.C Housing basics page, all six panels blocked out

Per Section 4.4 of `editorial/dashboard_purpose.md`. Section accent:
`series-4` (plum, `#7A3E65`).

**Section-level visual rules (Housing only).**

- **CMA-strip layout convention.** Three of the six Housing panels carry
  a CMA-by-CMA read (prices, inventory/absorption, population-to-stock
  ratio). For these we adopt a **CMA-strip** sub-layout: a horizontal
  row of seven slim panels (national + six CMAs in EDR-canonical order:
  Toronto, Vancouver, Montreal, Calgary, Ottawa, Edmonton). Each strip
  is ~58px wide, with the national strip 1.4x wider (~82px) and slightly
  recessed left of the six-CMA row. This is the Housing section's
  signature visual rhythm — the eye learns the CMA order on panel 1 and
  carries it across panels 3 and 6.
- **No national-average headline.** Per EDR 4.4 element 1, the Housing
  basics page deliberately does **not** publish a national HPI average
  number on the prices panel. The national strip in the CMA-strip
  layout shows the national index for *visual orientation* only; the
  big-number callout on panel 1 surfaces the **six-CMA range** read
  (highest / lowest Y/Y), not a national mean. This is a hard rule;
  national-average shorthand obscures the CMA-level dispersion that is
  the Canadian housing story.
- **Rate-sensitivity reference scaffold.** Panels 1 (prices), 2
  (activity), and 5 (mortgage stack) carry a thin secondary axis or
  reference annotation tying back to the BoC overnight rate trajectory
  — typically a faded `series-5` (teal) thin dashed line at 1px in the
  chart-background z-order. The reference is faint, present, and
  consistent across the three rate-sensitive panels. Other panels do
  not carry it. This is the visual realization of EDR 4.4's headline
  question ("is the rate-sensitive sector amplifying or dampening
  policy").
- **Cadence mismatch is disclosed.** Housing panels span monthly (MLS,
  starts, permits, CPI rent), quarterly (CMHC arrears), annual (CMHC
  RMS, population-to-stock ratio). Each panel's vintage stamp names its
  cadence explicitly in the reference-period line, and the page-level
  stamp (per Section 6) will typically read `OLDEST PANEL` on Housing
  because annual data trails monthly by 9-15 months.

### Housing Panel 1 — Prices (CMA-strip)

- **Eyebrow:** `PRICES`
- **Title slot:** active-voice sentence on the six-CMA range and any
  CMA leading or lagging. Writer. Example shape: "*Toronto and
  Vancouver lead the deceleration; Calgary alone prints positive
  Y/Y.*"
- **Chart type:** **CMA-strip composite** — a horizontal row of seven
  slim time-series panels. Each strip plots a single CMA's (or the
  national's) MLS HPI Y/Y on the upper half, 6-month annualized on the
  lower half, last 3 years on a shared x-axis. Strips share x-axis
  alignment; y-axes are independent per strip (so each CMA's range
  reads cleanly) but synchronized in scale per the design-system
  small-multiple convention.
- **Series colors:**
  - Y/Y line (upper half of each strip): `series-4` (plum, section
    accent), 1.5px solid weight 500.
  - 6-month annualized line (lower half of each strip): `series-4`
    at 60% opacity, 1.5px solid weight 400. The faster read; visually
    secondary so the Y/Y headline leads.
  - National strip: lines in `series-7` (slate), same weights. The
    national exists for visual orientation; it is not the editorial
    lead.
  - BoC rate reference: 1px dashed (`4 2`) `series-5` (teal) at 25%
    opacity in chart-background z-order, present on each strip.
    Labeled once at the right rail of the rightmost strip in `micro`
    `ink-faint` (`BoC rate, ref`).
- **Direct labels:** Each strip titled at the top in `label` size
  weight 500 with the CMA name (`Toronto`, `Vancouver`, etc.); the
  national strip labeled `Canada` in slate weight 400. Most recent
  Y/Y value displayed at the right terminus of each Y/Y line in
  `mono-sm` tabular. 6-month annualized value at the right terminus
  of its line in `mono-sm` tabular at 60% opacity.
- **Annotations:** A single page-level annotation in chart whitespace
  identifying the high-Y/Y CMA and the low-Y/Y CMA. No per-strip
  annotation (the strip IS the annotation).
- **Recession bands:** `ink` at 6% opacity, spanning all seven strips
  in vertical alignment. The cross-strip alignment is the point — the
  reader sees which CMAs were rate-sensitive in past cycles.
- **Callout:**
  - Big number: the six-CMA range, e.g., `-3.2% to +1.4%`
  - Unit: `MLS HPI Y/Y range across six CMAs, March 2026`
  - Direction row: `[arrow down] Five of six CMAs in Y/Y contraction
    | Range tightened vs prior month` (no consensus on CMA range)
- **Vintage:** `AS OF Apr 15, 2026 / Reference: Mar 2026`
- **Source:** `Canadian Real Estate Association MLS Home Price Index;
  national series via Bank of Canada Financial Variables Indicators;
  CMA-level via CREA XLSX bulk download.`
- **Methodology link:** Important — drawer explains the no-national-
  average rule, the six-CMA selection, the 6-month annualization
  construction, and the CREA-vs-BoC-FVI vintage reconciliation.

### Housing Panel 2 — Activity

- **Eyebrow:** `ACTIVITY`
- **Title slot:** active-voice sentence on starts trajectory, permits
  lead, and rental vs ownership mix. Writer.
- **Chart type:** **Two-row composite** inside the panel card.
  - Row A (top, ~55% of panel chart height): three-line time series
    of housing starts (with 3M MA overlay), completions, and permits.
    Permits leads visually; the 3M MA on starts is the headline read.
    Last 5 years on x-axis. Y-axis: monthly units (thousands).
  - Row B (bottom, ~45% of panel chart height): stacked-column
    composition showing CMHC intended-market breakdown (rental vs
    ownership share) over the same x-axis window, monthly columns.
- **Series colors:**
  - Starts: `series-4` (plum, section accent), 1.5px solid weight 500.
    3M MA overlay: `series-4` at 2px solid weight 600 — the heaviest
    line.
  - Completions: `series-7` (slate), 1.5px solid weight 400.
  - Permits: `series-4` at 60% opacity, 1px dashed (`2 2`), weight
    400. Dashed treatment signals leading-indicator status.
  - Rental share (row B bottom band): `series-5` (teal), fill at
    60% opacity.
  - Ownership share (row B top band): `series-4` (plum), fill at
    60% opacity.
  - BoC rate reference: 1px dashed (`4 2`) `series-5` at 25% opacity
    in background of row A.
- **Direct labels:** Line termini for starts/completions/permits in
  row A. Row B band labels at the right rail (`Rental` / `Ownership`)
  with current share %.
- **Annotations:** Row A carries one annotation calling out the
  permits-vs-starts lead/lag relationship at the most recent print.
  Row B annotates a notable shift in rental-vs-ownership mix in the
  last 12 months when present.
- **Recession bands:** `ink` at 6% opacity, both rows.
- **Callout:**
  - Big number: starts 3M MA, e.g., `218k`
  - Unit: `housing starts SAAR, 3M MA, March 2026`
  - Direction row: `[arrow down] -12k vs prior 3M | Beat
    consensus by 8k[c]`
- **Vintage:** `AS OF Apr 17, 2026 / Reference: Mar 2026`
- **Source:** `Canada Mortgage and Housing Corporation housing
  starts; Statistics Canada Table 34-10-0135 (completions); CMHC
  Starts and Completions Survey (intended-market breakdown).`
- **Methodology link:** Drawer explains 3M MA construction, the
  permits-as-leading-indicator convention, and CMHC intended-market
  category definitions.

### Housing Panel 3 — Inventory and absorption (CMA-strip)

- **Eyebrow:** `INVENTORY AND ABSORPTION`
- **Title slot:** active-voice sentence on SNLR (sales-to-new-listings)
  state and months-of-inventory by CMA. Writer.
- **Chart type:** **CMA-strip composite, two-metric variant** — same
  horizontal seven-strip rhythm as panel 1, but each strip plots two
  series: SNLR (upper half of strip, 0-100% axis) and months of
  inventory (lower half of strip, 0-12 month axis). Last 3 years.
- **Series colors:**
  - SNLR line: `series-4` (plum), 1.5px solid weight 500.
  - Months of inventory: `series-4` at 60% opacity, 1.5px solid
    weight 400.
  - National strip: both lines in `series-7` (slate).
  - SNLR reference bands (background): two horizontal bands per
    strip's SNLR half marking the BoC's documented balanced-market
    range (40-60% SNLR per CREA convention). Bands in `ink` at 4%
    opacity, labeled once at the right rail of the rightmost strip
    in `micro` `ink-faint`: `Balanced 40-60%`. NOT a classifier —
    a historical-anchor reference, per the same restraint applied to
    Labour panel 4's V/U bands.
- **Direct labels:** Strip titles at top (CMA name); current SNLR
  and current months-of-inventory at the right terminus of each
  strip in `mono-sm` tabular.
- **Annotations:** Page-level annotation in whitespace identifying
  the tightest-SNLR CMA and the loosest-SNLR CMA.
- **Recession bands:** `ink` at 6% opacity, vertical alignment
  across strips.
- **Callout:**
  - Big number: tightest CMA's SNLR, e.g., `72%`
  - Unit: `highest CMA SNLR (Calgary), March 2026; range 38-72%
    across six CMAs`
  - Direction row: `[arrow up] +3pp vs Feb | Three CMAs above
    balanced range`
- **Vintage:** `AS OF Apr 15, 2026 / Reference: Mar 2026`
- **Source:** `CREA MLS sales-to-new-listings (national via BoC FVI;
  CMA via CREA XLSX); months of inventory constructed as active
  listings divided by monthly sales by macro-research-department.`
- **Methodology link:** Important — drawer explains the
  active-listings / monthly-sales construction for months of
  inventory, the CREA balanced-market band history, and the CMA
  selection.

### Housing Panel 4 — Rent

- **Eyebrow:** `RENT`
- **Title slot:** active-voice sentence on the CMHC RMS annual
  picture, the CPI monthly direction, and Toronto/Vancouver loosening
  visibility. Writer.
- **Chart type:** **Dual-cadence composite** inside the panel card.
  - Sub-view A (top, ~60% of panel chart height): two-line time
    series. CMHC RMS purpose-built rental Y/Y rent change (annual,
    one observation per year) plotted as connected points-and-line,
    alongside StatCan CPI rented-accommodation Y/Y (monthly,
    continuous line). Last 10 years.
  - Sub-view B (bottom, ~40% of panel chart height): horizontal bar
    chart, six bars, showing CPI rent Y/Y by CMA (Toronto, Vancouver,
    Montreal, Calgary, Ottawa, Edmonton) at the most recent month.
    Bars in EDR-canonical CMA order.
- **Series colors:**
  - CMHC RMS rent change (sub-view A): `series-4` (plum), 1.5px
    solid line connecting annual observations, with 5px filled
    circles at each observation. Annual cadence read as discrete
    events.
  - CPI rent Y/Y (sub-view A): `series-4` at 60% opacity, 1.5px
    solid continuous line. The monthly direction read.
  - CMA bars (sub-view B): all six in `series-4`, 60% opacity,
    with the highest-Y/Y CMA highlighted at 100% opacity weight
    500. The bar order is fixed (EDR-canonical); the highlight is
    data-driven.
- **Direct labels:** Sub-view A: line termini for both. Sub-view B:
  each bar labeled at its terminus with CMA name and Y/Y value in
  `mono-sm` tabular.
- **Annotations:** Sub-view A annotates the most recent CMHC RMS
  observation (the annual headline). Sub-view B carries a single
  annotation in whitespace identifying the loosening direction
  (Toronto / Vancouver per EDR 4.4 element 4 if visible).
- **Recession bands:** `ink` at 6% opacity, sub-view A only (sub-view
  B is a single-point-in-time bar chart and has no time axis).
- **Callout:**
  - Big number: CPI rented-accommodation Y/Y, e.g., `5.2%`
  - Unit: `CPI rented-accommodation, Y/Y, March 2026; CMHC RMS
    +6.8% in 2025`
  - Direction row: `[arrow down] -0.4pp vs Feb | Toronto and
    Vancouver loosening visible at monthly cadence`
- **Vintage:** Two stamps (cadence mismatch is the point):
  ```
  AS OF
  CPI rent: Apr 15, 2026 (Mar 2026)
  CMHC RMS: Jan 28, 2026 (2025 survey)
  ```
- **Source:** `CMHC Rental Market Survey, October 2025 cycle;
  Statistics Canada Table 18-10-0004-01 rent sub-series.`
- **Methodology link:** Drawer explains CMHC RMS as the annual primary
  citation for rent levels, CPI rent as the monthly direction read,
  the purpose-built-vs-secondary distinction, and the per-CMA
  decomposition.

### Housing Panel 5 — Mortgage stack snapshot

- **Eyebrow:** `MORTGAGE STACK SNAPSHOT`
- **Title slot:** active-voice sentence on the BoC chartpack vintage
  composition, the OSFI residential mortgage line, and the CMHC RMIR
  arrears state. Writer.
- **Chart type:** **Three-block composite** inside the panel card —
  this is the busiest panel on the Housing page, by design, because the
  v1 basics treatment is a *cited snapshot* from primary sources rather
  than an own-construction. The three blocks are visually distinct so
  the reader sees three pieces of evidence rather than one homogenized
  read.
  - Block A (top-left, ~45% width / 55% height): **vintage composition
    horizontal stacked bar** — a single horizontal bar segmented by
    fixed-rate term (5y, 3y, 1y, variable) based on the BoC's most
    recently published Residential Mortgage Market chartpack. The bar
    is the BoC's reproduced composition; sourcing is to that chartpack
    issue.
  - Block B (top-right, ~55% width / 55% height): **OSFI Bank Financial
    Data residential mortgage line** plotted as a single time series
    over the last 5 years, monthly. Outstanding residential mortgages
    on Big-Six balance sheets.
  - Block C (bottom, full width / 45% height): **arrears time series**
    — CMHC RMIR (quarterly, the primary citation) plotted as connected
    points-and-line, with CBA chartered-bank arrears (monthly, the
    proxy) plotted as a faded background line. Last 8 years.
- **Series colors:**
  - Block A segments: `series-4` ramped at 100% / 75% / 50% / 25%
    opacity for the four term categories, longest term darkest. This
    is a one-time use of opacity-ramping on a single-series-color
    categorical encoding; it works because four-or-fewer categories
    on a single horizontal bar read cleanly with opacity.
  - Block B (OSFI line): `series-4` at 1.5px solid weight 500.
  - Block C: CMHC RMIR in `series-4` 1.5px solid weight 500 with
    5px filled circles at each quarterly observation; CBA proxy in
    `series-7` at 50% opacity, 1px solid weight 400.
  - BoC rate reference: 1px dashed (`4 2`) `series-5` at 25%
    opacity in chart-background of block B and block C — present on
    the two time-series blocks, not on block A (which is a snapshot,
    not a trajectory).
- **Direct labels:** Block A: each segment labeled with term name
  (`5-year fixed`, `3-year fixed`, etc.) and current % share in
  `label` size weight 500. Block B: line terminus with current value.
  Block C: both line termini.
- **Annotations:** Block A carries a small caption naming the BoC
  chartpack issue and vintage. Block C annotates the most recent
  RMIR observation.
- **Recession bands:** `ink` at 6% opacity, blocks B and C only.
- **Callout:**
  - Big number: CMHC RMIR arrears rate, e.g., `0.21%`
  - Unit: `CMHC residential mortgages in arrears, Q4 2025`
  - Direction row: `[arrow up] +0.02pp vs Q3 2025 | CBA monthly
    proxy continues rising`
- **Vintage:** Three stamps:
  ```
  AS OF
  BoC chartpack: [most recent issue date]
  OSFI: Apr 22, 2026 (Feb 2026)
  CMHC RMIR: Mar 30, 2026 (Q4 2025)
  ```
- **Source:** `Bank of Canada Residential Mortgage Market chartpack;
  OSFI Bank Financial Data residential mortgage line; CMHC Residential
  Mortgages in Arrears (RMIR); Canadian Bankers Association chartered
  bank arrears (monthly proxy).`
- **Methodology link:** Important — drawer flags this as a cited-
  snapshot panel rather than own construction, names the Pillar A
  deferral for full mortgage-stack reconstruction, and explains the
  RMIR-vs-CBA-proxy reconciliation.

### Housing Panel 6 — Population-to-housing-stock ratio by CMA
  (CMA-strip)

- **Eyebrow:** `POPULATION-TO-STOCK RATIO`
- **Title slot:** active-voice sentence on which CMAs have the
  tightest population-to-stock ratio and how the trajectory is
  moving. Writer.
- **Chart type:** **CMA-strip composite, single-metric variant** —
  the same horizontal seven-strip rhythm as panels 1 and 3, but each
  strip plots a single line: persons per dwelling, last 10 years
  (annual cadence). The longer x-axis window reflects the annual
  cadence — 10 annual observations is enough to read trajectory.
- **Series colors:**
  - Persons-per-dwelling line: `series-4` (plum), 1.5px solid
    weight 500. 5px filled circles at each annual observation to
    emphasize the discrete-annual cadence (this is not a continuous
    monthly series; we visually disclose that).
  - National strip: `series-7` (slate), same treatment.
  - No rate-reference dashed line here — population-to-stock is a
    supply-response measure, not a rate-sensitive one.
- **Direct labels:** Strip titles at top (CMA name); current ratio
  at the right terminus of each line in `mono-sm` tabular. A small
  caption at the bottom of the strip row: `Persons per dwelling,
  annual, last 10 years.`
- **Annotations:** Page-level annotation in whitespace identifying
  the tightest-ratio CMA and the loosest-ratio CMA, with a note on
  trajectory direction.
- **Recession bands:** None (the annual cadence does not align
  cleanly with recession-band placement; we acknowledge this by
  omission rather than approximating).
- **Callout:**
  - Big number: tightest CMA's ratio, e.g., `2.51`
  - Unit: `persons per dwelling, Toronto, 2024; range 2.10-2.51
    across six CMAs`
  - Direction row: `[arrow up] +0.08 vs 2019 baseline | Tightening
    in five of six CMAs`
- **Vintage:** `AS OF Apr 30, 2025 / Reference: 2024 (annual)`
  Note: this panel will typically be the page's `OLDEST PANEL`
  because annual data trails monthly by 12+ months.
- **Source:** `Statistics Canada Table 17-10-0135 (annual CMA
  population); Statistics Canada Table 36-10-0688 (housing stock);
  ratio construction by macro-research-department.`
- **Methodology link:** Important — drawer explains the base year
  selection, intercensal interpolation logic, and Pillar C cross-
  reference (housing cycle and supply response).

---

## 9.D Policy basics page, all eight elements blocked out

Per Section 4.5 of `editorial/dashboard_purpose.md`. Section accent:
`series-5` (teal, `#3F7D7C`).

**Section-level visual rules (Policy only).**

- **Two-sub-surface page architecture.** The Policy page is the only
  one of the seven that hosts two analytically distinct sub-surfaces
  (monetary and fiscal). The page is rendered as a single basics page
  with a **visual divider** separating the two blocks. Architecture:
  - Page header (Section 1) and panel index dots (Section 2) apply
    once at the top, treating all 8 panels (4 monetary + 4 fiscal)
    as a single panel sequence. The dots are 8 in number, in two
    visually grouped clusters of 4 separated by `s-3` (12px) extra
    gap.
  - A **sub-surface header rule** appears between the monetary block
    (panels 1-4) and the fiscal block (panels 5-8). Treatment: a
    full-width hairline rule in `series-5` (teal, section accent) at
    40% opacity, identical to the page-header hairline. Above the
    rule, a small sub-surface eyebrow in `label` size weight 500
    letter-spacing `0.08em` color `series-5`: `MONETARY` /
    `FISCAL`. Below the rule, `s-7` (48px) of space, then the next
    block of panels begins.
  - The sub-surface eyebrows function as in-page section markers.
    They are the only typographic ritual that distinguishes this page
    from the other six. The reader sees clearly that two distinct
    surfaces share one page.
- **Graceful 6-panel fallback.** Per the active EDR adjudication, the
  spec is designed for 8 panels (4 monetary + 4 fiscal). If EDR rules
  for 6 (e.g., 3+3), the page drops one panel from each block; the
  drop candidates are flagged per panel below. The sub-surface
  architecture and divider rule remain unchanged — they are the
  invariant page structure.
- **MPR-cadence vs Fiscal-Monitor-cadence asymmetry.** Monetary block
  panels refresh at BoC fixed-announcement-date or MPR cadence
  (event-driven, ~8 events/year + 4 MPRs). Fiscal block panels refresh
  on Fiscal Monitor monthly (with ~2-month lag) plus PBO and provincial
  budget events. Both blocks display their own as-of stamps per panel;
  the page-level stamp (Section 6) takes the least-recent across all
  8 panels per the standard rule. On this page, that will frequently
  be a fiscal panel (Budget / FES / Article IV vintages).
- **No accent-color-on-data rule, with one exception.** The teal
  section accent does **not** color data series on this page (per the
  cohesion rule from Section 11). The exception is the BoC overnight
  rate itself, which is plotted in `series-5` on panel 1, because
  teal IS the section accent and the overnight rate IS the section's
  central object. This is the same logic that put deep blue on GDP's
  headline real GDP line, sage green on Labour's per-capita signature,
  and plum on Housing's MLS HPI. One color, one role.

---

### MONETARY sub-surface (panels 1-4)

### Policy Panel 1 (Monetary) — BoC overnight rate

- **Eyebrow:** `OVERNIGHT RATE`
- **Title slot:** active-voice sentence on current rate level,
  distance to neutral, and consecutive-meeting action state. Writer.
- **Chart type:** **Stepped time-series with shaded neutral band**.
  BoC overnight rate plotted as a stepped line (rate decisions are
  discrete events, not continuous changes — the step treatment is the
  honest visualization). Last 5 years on x-axis. Y-axis: percent. A
  horizontal shaded band marks the BoC's estimated neutral range
  (researcher-curated, vintage-stamped, drawn at the *current* MPR
  vintage value, not historical neutral estimates which drift).
- **Series colors:**
  - Overnight rate stepped line: `series-5` (teal, section accent),
    2px solid weight 600. The section's central object earns the
    heaviest stroke on the page.
  - Neutral-range band: `series-5` at 12% opacity fill, with 1px
    `series-5` solid edges at the band boundaries. Labeled at the
    right rail `BoC neutral est. [low]-[high]%` in `micro` weight 500
    `series-5`.
  - Rate decision event markers: 4px filled circles in `series-5` at
    each decision date, sitting on the stepped line. Hold decisions
    use open circles (1.5px stroke, transparent fill).
- **Direct labels:** Line terminus shows current rate in `mono-sm`
  weight 500 `series-5`. Neutral-range label as above.
- **Annotations:** A single annotation on the most recent decision
  date, showing the action (hold/cut/hike) and the consecutive-
  meeting state. Writer composes the wording.
- **Recession bands:** `ink` at 6% opacity.
- **Callout:**
  - Big number: current overnight rate, e.g., `2.75%`
  - Unit: `BoC overnight rate, set Apr 29, 2026; neutral est. 2.25-
    3.25% (Apr 2026 MPR)`
  - Direction row: `[arrow flat] Hold for second consecutive meeting
    | 50 bps above neutral midpoint`
- **Vintage:** Two stamps:
  ```
  AS OF
  Rate: Apr 29, 2026 (decision date)
  Neutral: Apr 16, 2026 MPR
  ```
- **Source:** `Bank of Canada policy interest rate; Bank of Canada
  Monetary Policy Report neutral-rate estimate (researcher-curated).`
- **Methodology link:** Important — drawer explains that the neutral
  estimate is researcher-curated from the most recent MPR refresh
  rather than an API series, with the vintage stamp logic.
- **6-panel drop candidate?** No. This panel is the section's
  foundation — never drop.

### Policy Panel 2 (Monetary) — Market path

- **Eyebrow:** `MARKET PATH`
- **Title slot:** active-voice sentence on the 2-year GoC vs overnight
  read and the OIS-implied path from the most recent MPR. Writer.
- **Chart type:** **Two-row composite** inside the panel card.
  - Row A (top, ~60% height): 2-year GoC yield and BoC overnight
    rate plotted as two time-series lines, last 5 years. The
    *spread* between them is the basics-layer term-structure read on
    expectations (positive spread = market pricing hikes; negative =
    pricing cuts).
  - Row B (bottom, ~40% height): **OIS-implied BoC path snapshot** —
    a horizontal step chart showing the market-implied path from the
    most recent MPR's chart, going forward 8 quarters. This is a
    *cited* snapshot from the BoC's MPR market-implied curve chart,
    NOT own OIS forwards construction.
- **Series colors:**
  - 2-year GoC (row A): `series-5` (teal), 1.5px solid weight 500.
  - Overnight rate (row A): `series-5` at 50% opacity, 2px stepped,
    weight 500.
  - Spread shading (row A): the region between the two lines fills
    with `series-5` at 8% opacity. This is the editorial point of
    the row.
  - OIS-implied path (row B): `series-5` stepped at 1.5px solid
    weight 500.
  - OIS-implied path forward window: rendered with light vertical
    grid markers in `rule-faint` every 2 quarters; the path itself
    is the read.
- **Direct labels:** Row A: line termini for both. Row B: each step's
  level labeled at its midpoint in `mono-sm` tabular.
- **Annotations:** Row A annotates the current spread value. Row B
  carries a single caption identifying the MPR vintage from which the
  path is cited.
- **Recession bands:** `ink` at 6% opacity, row A only.
- **Callout:**
  - Big number: 2y GoC minus overnight rate spread, e.g., `-0.15pp`
  - Unit: `2-year GoC minus overnight, May 8, 2026; OIS-implied 12mo
    path: 2 cuts (Apr MPR)`
  - Direction row: `[arrow down] -0.20pp vs prior month |
    Market pricing easing`
- **Vintage:** Two stamps:
  ```
  AS OF
  GoC 2y: May 8, 2026 (daily)
  OIS path: Apr 16, 2026 MPR
  ```
- **Source:** `Bank of Canada Valet 2-year GoC yield; Bank of Canada
  policy rate; OIS-implied path cited from BoC Monetary Policy Report
  market-implied curve chart.`
- **Methodology link:** Drawer explains the cited-snapshot logic for
  OIS-implied path (no own forwards construction in v1) and points to
  Pillar B deep-dive.
- **6-panel drop candidate?** Possibly. If EDR rules 6 panels, this
  is a drop candidate because the OIS path is a cited snapshot rather
  than own construction; the 2y-vs-overnight spread could fold into
  panel 1 as a second axis.

### Policy Panel 3 (Monetary) — BoC-Fed spread

- **Eyebrow:** `BOC-FED SPREAD`
- **Title slot:** active-voice sentence on current spread, distribution
  context, and regime classification. Writer.
- **Chart type:** **Time-series with distribution-percentile reference
  scaffold**. BoC overnight rate minus Fed funds upper bound plotted as
  a single time series, last 35+ years (the full Valet history).
  Horizontal reference lines mark P50 / P80 / P95 / P99 of the
  distribution, drawn at `ink-faint` 1px solid with right-rail labels.
- **Series colors:**
  - Spread line: `series-5` (teal), 1.5px solid weight 500.
  - Zero line: `ink-muted`, 1px solid (the spread crosses zero
    historically and the crossing is editorially meaningful).
  - Percentile reference lines: `ink-faint` 1px solid, with labels
    at right rail in `micro` `ink-faint`: `P50` / `P80` / `P95` /
    `P99`. Symmetric below zero for negative spreads.
- **Direct labels:** Line terminus with current spread value in
  `mono-sm` weight 500. Percentile labels at right rail.
- **Annotations:** A single annotation on the most recent value,
  noting which percentile band it falls in (the regime classification).
- **Recession bands:** `ink` at 6% opacity.
- **Callout:**
  - Big number: current spread, e.g., `-1.50pp`
  - Unit: `BoC minus Fed funds upper, May 8, 2026 (P95 negative)`
  - Direction row: `[arrow flat] Unchanged vs prior week |
    Within P95 historical band`
- **Vintage:** `AS OF May 8, 2026 (daily)`
- **Source:** `Bank of Canada policy interest rate; Federal Reserve
  H.15 federal funds target range upper bound.`
- **Methodology link:** Drawer explains the distribution computation
  (35+ years daily), the percentile-band logic, and the regime-
  classification framing.
- **6-panel drop candidate?** No. The BoC-Fed spread is load-bearing
  for the Markets section's CAD and GoC reads; deep-dive Pillar B
  refers to this panel. Keep.

### Policy Panel 4 (Monetary) — Balance sheet

- **Eyebrow:** `BALANCE SHEET`
- **Title slot:** active-voice sentence on settlement balances level,
  asset composition, and current phase (QE / reinvestment / passive
  QT / floor maintenance). Writer.
- **Chart type:** **Stacked-area asset composition** time series. BoC
  balance-sheet assets stacked by category (settlement balances,
  Government of Canada securities, term repos, other) over last 8
  years (covers the COVID QE expansion and subsequent QT).
- **Series colors:**
  - Settlement balances: `series-5` (teal, section accent), fill at
    60% opacity. Bottom of the stack.
  - GoC securities: `series-1` (deep blue), fill at 60% opacity.
  - Term repos: `series-7` (slate), fill at 60% opacity.
  - Other: `series-6` (olive gold), fill at 40% opacity. Top of the
    stack.
  - Band edges: 1px `surface` overdraw at boundaries for legibility.
  - Phase-call vertical markers: 1px solid lines in `ink-faint` at
    each phase transition date, labeled in `label` weight 500
    `ink-faint` at the top of the chart: `QE start`, `QE end`,
    `Passive QT`, `Floor maintenance`. Per EDR 4.5 monetary element
    4: these are editorial-curated phase calls with cite-to-statement
    references, not algorithmic classifications.
- **Direct labels:** Each stack band labeled at the right rail with
  its current $-value in `mono-sm` tabular, color matching the band
  fill at full opacity.
- **Annotations:** A single chart-level annotation in whitespace
  identifying the current phase and the cite-to-statement reference
  (writer composes; example: *"Floor maintenance per BoC statement,
  Mar 2025."*).
- **Recession bands:** `ink` at 6% opacity, but recession bands on
  this panel are visually subordinate to phase markers (phases are
  the editorial frame, not recessions).
- **Callout:**
  - Big number: settlement balances, e.g., `$58B`
  - Unit: `settlement balances, May 1, 2026; total assets $X.XXT`
  - Direction row: `[arrow flat] +$2B vs prior week | Phase: Floor
    maintenance`
- **Vintage:** `AS OF May 1, 2026 (weekly)`
- **Source:** `Bank of Canada balance sheet, weekly statistical
  reports.`
- **Methodology link:** Important — drawer explains the phase-call
  curation logic, the cite-to-statement convention for each phase
  transition, and the asset-category definitions.
- **6-panel drop candidate?** Yes (secondary candidate). The balance
  sheet is currently in floor-maintenance — a low-news phase. If EDR
  rules 6 panels, this is the second drop candidate after panel 2.
  Restore when balance-sheet news becomes load-bearing again.

---

### FISCAL sub-surface (panels 5-8)

(Sub-surface divider rule and `FISCAL` eyebrow appear above these
panels per the page architecture rule.)

### Policy Panel 5 (Fiscal) — Federal trajectory

- **Eyebrow:** `FEDERAL TRAJECTORY`
- **Title slot:** active-voice sentence on YTD deficit, debt-service
  ratio, and PBO-vs-FES baseline delta. Writer.
- **Chart type:** **Three-block composite** inside the panel card.
  - Block A (top, ~50% height, full width): Federal deficit YTD time
    series, monthly cadence from Fiscal Monitor, last 5 fiscal years
    overlaid as five lines (or as a single cumulative-by-fiscal-year
    line with terminus markers per year).
  - Block B (bottom-left, ~50% width / 50% height): Debt-service costs
    as % of revenues, time series, last 10 years, annual or quarterly.
  - Block C (bottom-right, ~50% width / 50% height): PBO vs FES
    baseline projection lines, going forward 5 fiscal years from the
    current vintage. Two lines with the delta region shaded.
- **Series colors:**
  - Block A YTD lines: `series-5` (teal) for current fiscal year at
    2px weight 600; prior 4 fiscal years in `series-5` at 30/40/
    50/60% opacity, oldest palest. Sequential opacity ramp on a
    single hue.
  - Block B: `series-5` 1.5px solid weight 500.
  - Block C: PBO line in `series-5` 1.5px solid weight 500; FES
    baseline in `series-7` (slate) 1.5px solid weight 500. Delta
    region filled in `series-5` at 15% opacity.
- **Direct labels:** Block A: each fiscal year line labeled at its
  terminus with fiscal-year-end value in `mono-sm` tabular. Block B:
  line terminus. Block C: both line termini labeled with vintage
  (`PBO Mar 2026`, `FES Nov 2025`).
- **Annotations:** Block C carries one annotation on the projection
  delta at year 3 or 5 (writer composes).
- **Recession bands:** `ink` at 6% opacity, block A only.
- **Callout:**
  - Big number: YTD deficit, e.g., `-$32B`
  - Unit: `federal deficit YTD through Feb 2026; debt service 12.4%
    of revenues`
  - Direction row: `[arrow down] -$5B vs prior fiscal year YTD | PBO
    baseline diverges from FES by $14B at FY28`
- **Vintage:** Three stamps:
  ```
  AS OF
  Fiscal Monitor: Apr 30, 2026 (Feb 2026)
  PBO EFO: Mar 5, 2026
  FES: Nov 21, 2025
  ```
- **Source:** `Department of Finance Fiscal Monitor; Parliamentary
  Budget Officer Economic and Fiscal Outlook; Department of Finance
  Fall Economic Statement.`
- **Methodology link:** Important — drawer explains the YTD-by-fiscal-
  year construction, debt-service-to-revenues definition, and the
  cited-projection-vintages logic.
- **6-panel drop candidate?** No. Federal trajectory is the fiscal
  foundation panel; never drop.

### Policy Panel 6 (Fiscal) — Provincial

- **Eyebrow:** `PROVINCIAL`
- **Title slot:** active-voice sentence on net debt-to-GDP across the
  four provinces, latest budget balance vs plan, and any active credit-
  watch flags. Writer.
- **Chart type:** **Four-row dumbbell** — same dumbbell pattern as
  Labour panel 6, here showing net debt-to-GDP for ON, QC, AB, BC.
  Each row plots current value (filled circle) and value 4 years ago
  or vs plan (open circle).
- **Series colors:**
  - Current values (filled): `series-5` (teal), 6px circles.
  - Prior/plan values (open): `series-5`, 5px circles, 1.5px stroke
    transparent fill.
  - Connecting lines: `series-5` at 60% opacity, 1.5px solid. No
    pos/neg color encoding on this panel (the editorial valence of
    rising debt-to-GDP is contestable; we leave color encoding to the
    Labour-dumbbell precedent and present this panel as a neutral
    state visual).
  - Credit-watch flag indicators: where a province has an active flag
    from Moody's / S&P / Fitch / DBRS Morningstar, a small `accent`
    (`#A6192E`) caret glyph (`!`) appears immediately right of the
    province name. `body-sm` `accent` weight 500. Tooltip on hover
    names the rating agency and action date.
- **Direct labels:** Province names at left rail in `body-sm` weight
  500 `ink`. Current values right of filled circle in `mono-sm`
  tabular. Prior values left of open circle in `mono-sm` tabular
  `ink-muted`.
- **Annotations:** A single annotation in chart whitespace identifying
  the highest-debt province and the trajectory direction.
- **Recession bands:** None (this is a snapshot, not a time series).
- **Callout:** Editorial status block (no single number summarizes
  four provinces):
  - Status label: `PROVINCIAL DEBT STATE`
  - Status line: writer-filled, e.g., *"Quebec and Ontario continue
    to trail Alberta on debt-to-GDP; British Columbia diverged after
    2023."*
  - Context line: writer-filled, optionally referencing active
    credit-watch flags.
- **Vintage:** Stacked stamps (each province on its own budget
  cadence):
  ```
  AS OF
  ON: [latest budget date]
  QC: [latest budget date]
  AB: [latest budget date]
  BC: [latest budget date]
  ```
- **Source:** `Provincial Budgets (ON, QC, AB, BC); Moody's / S&P /
  Fitch / DBRS Morningstar rating actions.`
- **Methodology link:** Drawer explains the net-debt-to-GDP
  definition, the four-province selection, and the rating-action
  inclusion criteria.
- **6-panel drop candidate?** No. Provincial fiscal capacity is a
  load-bearing read; keep.

### Policy Panel 7 (Fiscal) — Debt management

- **Eyebrow:** `DEBT MANAGEMENT`
- **Title slot:** active-voice sentence on GoC issuance trajectory,
  average term, and redemption profile. Writer.
- **Chart type:** **Two-block composite**.
  - Block A (top, ~50% height): GoC gross issuance time series,
    annual, last 10 years, bar chart. Color-coded by term bucket
    (T-bills, 2y, 5y, 10y, 30y+).
  - Block B (bottom, ~50% height): Redemption profile bar chart,
    forward 10 years, showing maturities by fiscal year.
- **Series colors:**
  - Issuance bars (block A): five-color categorical from the design-
    system palette, in EDR-canonical term order: T-bills `series-7`
    (slate), 2y `series-5` (teal), 5y `series-1` (deep blue), 10y
    `series-4` (plum), 30y+ `series-6` (olive gold). Stacked.
  - Redemption bars (block B): `series-5` (teal) at 70% opacity, all
    same color (the data dimension is fiscal-year, not term).
  - Average-term overlay line (block A): `ink-muted` 1px solid line
    on a secondary right-axis showing average issuance term in years.
- **Direct labels:** Block A: each term-bucket band in the most
  recent bar labeled at its segment with term name and current
  $-value. Block B: redemption peaks labeled with fiscal year and
  $-value.
- **Annotations:** A single annotation referencing the DMS document
  vintage and any narrative-relevant coupon-roll callout (writer per
  EDR 4.5 fiscal element 3 — no own coupon-roll math in v1).
- **Recession bands:** None (fiscal-year cadence; recession-band
  alignment is not editorially useful here).
- **Callout:**
  - Big number: current fiscal year gross issuance, e.g., `$420B`
  - Unit: `gross issuance FY26; average term 7.2 years`
  - Direction row: `[arrow up] +$35B vs FY25 | FY28-FY30 redemption
    peak: $186B`
- **Vintage:** `AS OF [most recent DMS publication date]`
- **Source:** `Department of Finance Debt Management Strategy Annex.`
- **Methodology link:** Important — drawer explains the cited-from-DMS
  logic, the term-bucket definitions, and the coupon-roll-deferred
  scope.
- **6-panel drop candidate?** Possibly. If EDR rules 6 panels, this is
  a fiscal-side drop candidate (debt management is steady-state and
  the DMS Annex itself is the primary citation; the basics-layer chart
  adds visualization but not analytical lift in normal times).

### Policy Panel 8 (Fiscal) — Fiscal stance vs cycle

- **Eyebrow:** `FISCAL STANCE VS CYCLE`
- **Title slot:** active-voice sentence on CAPB level, fiscal impulse
  direction, and consistency-with-monetary-stance read. Writer.
- **Chart type:** **Two-line time series with shaded impulse**.
  Cyclically-adjusted primary balance (CAPB) plotted as a single time
  series, last 10 years, with the year-over-year change (fiscal
  impulse) shown as a thin secondary series. The cycle reference
  (output gap from GDP panel 5) overlaid as a contextual line.
- **Series colors:**
  - CAPB level: `series-5` (teal), 1.5px solid weight 500. Primary.
  - Fiscal impulse (Y/Y change in CAPB): `series-5` at 60% opacity,
    1.5px solid weight 400. Secondary; on a secondary axis.
  - Output gap (contextual): `series-7` (slate), 1px dashed (`4 2`),
    weight 400. Tertiary; explicitly subordinate so the reader sees
    the cyclical reference without confusing it with the CAPB read.
- **Direct labels:** Three line termini. CAPB labeled `CAPB level`
  in teal weight 500; impulse labeled `Fiscal impulse (Y/Y)` in teal
  60% weight 400; output gap labeled `Output gap (ref)` in slate
  weight 400 with `(ref)` italicized.
- **Annotations:** A single annotation on the most recent CAPB point
  and a separate annotation on the impulse direction at the most
  recent observation.
- **Recession bands:** `ink` at 6% opacity.
- **Callout:** Editorial status block (no single number summarizes
  the consistency read):
  - Status label: `FISCAL-MONETARY CONSISTENCY`
  - Status line: writer-filled, e.g., *"Fiscal impulse moderately
    positive (+0.4pp of GDP, IMF Article IV) while monetary stance
    held restrictive — divergent through 2026."*
  - Context line: writer-filled, naming the cited CAPB source (IMF
    Article IV vs OECD).
- **Vintage:** `AS OF [most recent IMF Article IV or OECD vintage]`
- **Source:** `IMF Article IV Canada (CAPB); OECD Economic Survey of
  Canada (alternative CAPB citation); macro-research-department
  fiscal-impulse one-line transform.`
- **Methodology link:** Important — drawer explains the cited-CAPB
  logic (no own construction in v1), the fiscal-impulse one-line
  transform, the consistency-with-monetary-stance as prose-level not
  quantified, and Pillar F deep-dive deferral.
- **6-panel drop candidate?** Possibly. If EDR rules 6 panels, this
  is a fiscal-side drop candidate (the CAPB is itself a cited
  number; the basics-layer chart adds context but not analytical
  construction). Restore when our own CAPB construction lands in v1.5.

---

## 9.E Markets basics page, all six panels blocked out

Per Section 4.6 of `editorial/dashboard_purpose.md`. Section accent:
`series-6` (olive gold, `#8A6A2C`).

**Section-level visual rules (Markets only).**

- **Higher-cadence vintage stamping.** Markets is the only section with
  a daily/weekly cadence on most series per EDR 4.6. The vintage stamp
  on this page extends from the two-line `AS OF + Reference` format to a
  **three-line variant** including time-of-day:
  ```
  AS OF
  May 8, 2026
  Close 16:00 ET
  ```
  The third line is in `micro` (12px) Inter weight 400 `ink-faint`,
  same color/family as the reference line on other sections. The
  market-close time stamp is the Bay Street allocator's signal that
  the data is end-of-day, not intraday.
- **Daily vs weekly vs monthly mix is explicit.** Some Markets panels
  carry daily series (USDCAD, GoC yields, energy prices), others
  weekly (Bank stability, FCI), others monthly (CET1, M4 mortgage
  exposure). Each panel's vintage stamp names its cadence in the
  third line: `Daily close` / `Weekly close` / `Monthly close`. The
  page-level stamp (per Section 6) reads the least-recent across all
  6 panels — typically a monthly panel.
- **Distribution-percentile reference scaffold convention.** Markets is
  the section where distribution-context framing matters most (USDCAD
  P50/P80/P95/P99 per EDR 4.6 element 1; BoC-Fed spread percentiles
  per Policy panel 3 cross-reference). Where a panel surfaces a
  percentile classifier, the visual scaffold is identical to Policy
  Panel 3's: horizontal reference lines in `ink-faint` 1px solid with
  right-rail labels in `micro` `ink-faint`. This is a cross-section
  visual ritual — the reader learns it on Policy Panel 3 and re-
  encounters it on Markets Panel 1.
- **Canadian-blind-spot caveat treatment.** Two panels (Credit spreads,
  FCI) ship with v1 caveats that the Canadian variant is deferred to
  v1.5. Per design-system Section 6 caveat-treatment convention: a
  small caveat banner sits at the bottom of the panel chart, inside
  the panel card, above the source line. Treatment: `body-sm` italic
  `ink-muted`, prefixed with a `series-7` (slate) caret glyph (`>`).
  No box around the caveat; it reads as a typographic footnote, not
  a warning.

### Markets Panel 1 — CAD (USDCAD + CEER + percentile classifier)

- **Eyebrow:** `CAD`
- **Title slot:** active-voice sentence on USDCAD level, CEER trajectory,
  and percentile-band classification. Writer.
- **Chart type:** **Two-row composite** inside the panel card.
  - Row A (top, ~65% height): USDCAD level time series, last 10 years,
    with percentile reference scaffold (P50/P80/P95/P99 since 1990
    drawn as horizontal `ink-faint` lines).
  - Row B (bottom, ~35% height): BoC CEER (nominal effective index)
    time series, last 10 years, plotted on its own scale.
- **Series colors:**
  - USDCAD line (row A): `series-6` (olive gold, section accent),
    1.5px solid weight 500.
  - Percentile reference lines (row A): `ink-faint` 1px solid; labels
    at right rail `P50` / `P80` / `P95` / `P99` in `micro` `ink-faint`.
  - CEER line (row B): `series-6` at 60% opacity, 1.5px solid weight
    500. Lighter weight signals secondary read.
- **Direct labels:** USDCAD line terminus with current level in
  `mono-sm` weight 500 `series-6`. CEER terminus with current index
  value.
- **Annotations:** Row A annotates the current USDCAD value with its
  percentile band classification (writer composes; example: *"USDCAD
  1.39, P80-P95 historical band — elevated stress, not extreme."*).
  Row B annotates the CEER trajectory direction over the last 6 months.
- **Recession bands:** `ink` at 6% opacity, both rows.
- **Callout:**
  - Big number: USDCAD level, e.g., `1.3850`
  - Unit: `USDCAD spot, May 8, 2026 close; P80-P95 band`
  - Direction row: `[arrow up] +0.5% vs prior week | CEER -1.2% Y/Y`
- **Vintage:** Three-line:
  ```
  AS OF
  May 8, 2026
  Daily close 16:00 ET
  ```
- **Source:** `Bank of Canada Valet FXUSDCAD (USDCAD); Bank of Canada
  CEER nominal effective index.`
- **Methodology link:** Important — drawer explains the P50/P80/P95/P99
  computation (35+ years daily data), the percentile-band logic, and
  the fair-value-model deferral to v1.5 / deep-dive per EDR 4.6
  element 1.

### Markets Panel 2 — GoC curve (and UST spread)

- **Eyebrow:** `GOC CURVE`
- **Title slot:** active-voice sentence on curve shape, 10y-2y spread,
  and GoC-UST 10y spread. Writer.
- **Chart type:** **Two-block composite**.
  - Block A (top, ~55% height): four-line time series of 2y, 5y, 10y,
    30y GoC yields, last 5 years.
  - Block B (bottom, ~45% height): two-line time series of GoC-UST 2y
    spread and GoC-UST 10y spread, last 5 years. Term premium overlaid
    where decomposable (BoC's published series, Valet key TBD per EDR
    4.6 element 2).
- **Series colors:**
  - GoC 2y: `series-6` (olive gold) at 100%, 1.5px solid weight 500.
  - GoC 5y: `series-6` at 75% opacity, 1.5px solid weight 400.
  - GoC 10y: `series-6` at 50% opacity, 1.5px solid weight 400.
  - GoC 30y: `series-6` at 30% opacity, 1.5px solid weight 400.
    The opacity ramp encodes term — shorter darker, longer paler.
    Direct labels carry the term names so the encoding is explicit.
  - GoC-UST 2y spread (block B): `series-6` 1.5px solid weight 500.
  - GoC-UST 10y spread (block B): `series-6` at 60% opacity, 1.5px
    solid weight 500.
  - Term premium overlay (if available): `series-7` (slate) 1px
    dashed (`4 2`), weight 400. Subordinate visual treatment.
- **Direct labels:** Each curve line labeled at its terminus with term
  name (`2y`, `5y`, `10y`, `30y`) and current yield. Spread lines
  labeled with their full names at termini.
- **Annotations:** Block A annotates the 10y-2y spread sign (positive
  / inverted) at the most recent date. Block B annotates current
  spreads.
- **Recession bands:** `ink` at 6% opacity, both blocks.
- **Callout:**
  - Big number: 10y GoC yield, e.g., `3.42%`
  - Unit: `10-year GoC, May 8, 2026 close; 10y-2y spread +0.18pp`
  - Direction row: `[arrow up] +5bp vs prior week | GoC-UST 10y
    spread -0.78pp`
- **Vintage:** Three-line: `AS OF May 8, 2026 / Daily close 16:00 ET`
- **Source:** `Bank of Canada Valet GoC yields; Federal Reserve H.15
  US Treasury yields (FRED DGS10, DGS2); BoC term-premium series
  where available.`
- **Methodology link:** Drawer explains the term-premium decomposition
  status (Valet key probed; defer own ACM-style decomposition).

### Markets Panel 3 — Credit spreads

- **Eyebrow:** `CREDIT SPREADS`
- **Title slot:** active-voice sentence on US IG and HY OAS levels and
  the Canadian-spread blind-spot caveat. Writer.
- **Chart type:** **Two-line time series**. US IG OAS and US HY OAS
  plotted on the same x-axis (last 10 years), on a shared y-axis
  (percent) — though HY runs higher in absolute level, the shared
  axis is editorially honest about the magnitude difference.
- **Series colors:**
  - US IG OAS: `series-6` (olive gold), 1.5px solid weight 500.
  - US HY OAS: `series-2` (burnt orange — reused as a "risk premium"
    visual signal across sections; deliberate cross-section color
    reference), 1.5px solid weight 500.
- **Direct labels:** Both line termini with current values.
- **Annotations:** A single annotation on the most recent IG-vs-HY
  ratio or the most recent absolute level shift.
- **Recession bands:** `ink` at 6% opacity.
- **Caveat banner (panel-foot, above source line):**
  > *> Canadian credit spreads (senior-unsecured-vs-GoC, IG/HY
  > proxies) deferred to v1.5; US IG/HY OAS shown as risk-appetite
  > proxy in v1.*
  Caveat in `body-sm` italic `ink-muted` with the `>` caret in
  `series-7` (slate) weight 500.
- **Callout:**
  - Big number: US IG OAS, e.g., `132bp`
  - Unit: `ICE BofA US Corporate IG OAS, May 8, 2026`
  - Direction row: `[arrow up] +6bp vs prior week | US HY OAS +18bp`
- **Vintage:** Three-line: `AS OF May 8, 2026 / Daily close`
- **Source:** `FRED BAMLC0A0CM (US IG OAS); FRED BAMLH0A0HYM2 (US HY
  OAS).`
- **Methodology link:** Important — drawer explains the Canadian-
  blind-spot status, the v1.5 plan for Canadian senior-unsecured-vs-
  GoC, and the FSR scraping approach for Canadian IG/HY proxies.

### Markets Panel 4 — Energy prices

- **Eyebrow:** `ENERGY PRICES`
- **Title slot:** active-voice sentence on oil benchmarks, WCS
  differential, AECO gas, and gasoline-channel CPI impulse. Writer.
- **Chart type:** **Two-block composite**.
  - Block A (top, ~65% height): four-line time series of WTI, Brent,
    WCS, and AECO gas (or AECO substitute per EDR 4.6 element 4
    deferral). Last 5 years. Oil prices on a left axis ($USD/bbl);
    AECO on a right axis ($CAD/GJ) to accommodate the scale
    difference.
  - Block B (bottom, ~35% height): a small horizontal bar showing the
    *currently constructed* gasoline-channel CPI impulse (per EDR 4.6
    element 4: already constructed). Bar plotted as a signed
    contribution to CPI in `series-2` (burnt orange — cross-section
    reference to Inflation).
- **Series colors:**
  - WTI: `series-6` (olive gold), 1.5px solid weight 500.
  - Brent: `series-6` at 60% opacity, 1.5px solid weight 400.
  - WCS: `series-6` at 30% opacity, 1.5px solid weight 400. Per EDR
    4.6 element 4 caveat: "do not surface daily-comparison
    differential" — the visualization shows WCS in the four-line
    stack but does NOT show a daily WTI-WCS differential as a
    separate series.
  - AECO (right-axis): `series-5` (teal) at 60% opacity, 1.5px solid
    weight 400. Different hue signals different unit (gas vs oil).
  - Gasoline-channel CPI bar (block B): `series-2` (burnt orange,
    pointing right for positive contribution, left for negative).
- **Direct labels:** Block A: four line termini with current prices.
  AECO terminus labeled `AECO (right axis)`. Block B: bar labeled
  with the current impulse value.
- **Annotations:** Block A annotates the most recent WCS differential
  in chart whitespace (monthly cadence, per EDR 4.6 element 4 — NOT
  daily). Block B caption: `Gasoline-channel CPI impulse,
  trailing 12 months.`
- **Recession bands:** `ink` at 6% opacity, block A only.
- **Callout:**
  - Big number: WTI level, e.g., `$72.40`
  - Unit: `WTI front-month, May 8, 2026 close; WCS differential
    -$14.20 (Apr monthly)`
  - Direction row: `[arrow down] -$1.20 vs prior week | Gasoline-
    channel CPI impulse +0.08pp`
- **Vintage:** Three-line variants per series cadence:
  ```
  AS OF
  Oil: May 8, 2026 (daily close)
  WCS: Apr 30, 2026 (monthly avg)
  AECO: May 2, 2026 (weekly bid-week)
  ```
- **Source:** `EIA / Bloomberg WTI front-month; ICE Brent; Government
  of Alberta WCS monthly average; NGX AECO bid-week (or substitute
  per EDR 4.6 element 4 deferral).`
- **Methodology link:** Drawer explains the WCS monthly-vs-daily
  caveat, the AECO data-source status, and the gasoline-channel CPI
  impulse construction.

### Markets Panel 5 — Bank stability

- **Eyebrow:** `BANK STABILITY`
- **Title slot:** active-voice sentence on Big-Six PCL builds, CET1
  vs DSB, and uninsured residential exposure. Writer.
- **Chart type:** **Three-block composite** — the busiest Markets
  panel because three different bank-stability reads each need their
  own visualization.
  - Block A (top, ~40% height, full width): Big-Six PCL build time
    series, quarterly, last 5 years. Plotted as a stacked or
    side-by-side bar chart of six banks, or as a single aggregated
    line with a range envelope (chart-builder's call after seeing the
    data shape).
  - Block B (middle, ~30% height, full width): CET1 ratio range across
    Big-Six vs OSFI Domestic Stability Buffer threshold. Plotted as a
    horizontal range bar showing min-mean-max CET1 across the six,
    with the DSB threshold (current 3.5% per OSFI per EDR 4.6 element
    5) as a vertical reference line.
  - Block C (bottom, ~30% height, full width): Uninsured residential
    exposure (OSFI M4) time series, semi-annual cadence, last 5 years.
- **Series colors:**
  - Block A: `series-6` (olive gold) for the aggregated read; if
    side-by-side six bars, `series-6` at 100/85/70/55/40/25% opacity
    for the six banks in alphabetical or rotating order (no
    individual bank gets a permanent color identity — they rotate so
    no bank gets editorial prominence).
  - Block B: range bar in `series-6` 60% opacity fill; mean point
    as 6px filled circle in `series-6` 100%; DSB threshold as 1.5px
    solid `accent` (`#A6192E`) vertical line labeled `OSFI DSB 3.5%`
    in `accent` weight 500.
  - Block C: `series-6` 1.5px solid weight 500.
  - BoC rate reference: 1px dashed (`4 2`) `series-5` (teal) at 25%
    opacity in background of block A — rate-sensitive linkage.
- **Direct labels:** Block A: line/bar termini. Block B: min, mean,
  max labels at their positions; DSB threshold labeled. Block C:
  line terminus.
- **Annotations:** Block A annotates the most recent quarter's
  aggregate PCL build. Block B annotates the lowest-CET1 bank's
  buffer vs the threshold.
- **Recession bands:** `ink` at 6% opacity, blocks A and C.
- **Callout:**
  - Big number: aggregate Big-Six PCL, e.g., `$3.2B`
  - Unit: `Big-Six aggregate PCL build, Q1 2026; CET1 range 12.8-
    14.2%`
  - Direction row: `[arrow up] +$0.4B vs Q4 2025 | All Big-Six above
    OSFI DSB`
- **Vintage:** Three stamps:
  ```
  AS OF
  PCL: [most recent earnings release date] (Q1 2026)
  CET1: [most recent Pillar 3 disclosure date]
  M4 uninsured: Mar 31, 2026 (Feb 2026, semi-annual)
  ```
- **Source:** `Big-Six earnings releases (PCL builds, manual capture);
  Big-Six Pillar 3 disclosures (CET1); OSFI Bank Financial Data M4
  (uninsured residential).`
- **Methodology link:** Important — drawer explains manual-capture
  cadence for PCL, the no-permanent-bank-color rule, the DSB
  reference (current 3.5% level), and the semi-annual M4 scrape
  status.

### Markets Panel 6 — Financial conditions index

- **Eyebrow:** `FINANCIAL CONDITIONS`
- **Title slot:** active-voice sentence on the FCI level and what is
  driving it. Writer.
- **Chart type:** **Single-line time series with decomposition strip
  below** — IF BoC FCI is available via Valet (per EDR 4.6 element 6).
  If unavailable, ships as **two lines** (Chicago Fed NFCI + Canadian
  prose-only caveat).
  - Variant A (BoC FCI available): BoC FCI as a single line over last
    10 years on the main chart; below it, a small contribution-decomp
    strip showing which sub-components (rates, credit, FX, equities)
    are driving the level. Decomp strip is a small horizontal stacked
    bar at a single point in time (most recent observation).
  - Variant B (BoC FCI unavailable, v1 default): Chicago Fed NFCI as
    a single line over last 10 years; Canadian-blind-spot caveat
    banner per the section-level convention.
- **Series colors:**
  - FCI line (either variant): `series-6` (olive gold), 1.5px solid
    weight 500.
  - Zero line: `ink-muted` 1px solid (FCIs are typically anchored to
    zero = neutral conditions; the crossing is editorially
    meaningful).
  - Tight / loose region shading (variant A only): regions where FCI
    > 0 (tight) shaded in `neg-soft` at 30% opacity; regions where
    FCI < 0 (loose) shaded in `pos-soft` at 30% opacity. This is the
    one place on the Markets page where pos/neg color encoding
    appears on a chart-background region — it earns its place because
    the FCI IS a tight/loose state read.
  - Decomp strip bars (variant A): four categorical colors from the
    palette in canonical order: rates `series-5`, credit `series-2`,
    FX `series-6`, equities `series-1`.
- **Direct labels:** Line terminus with current level. Decomp strip
  segments labeled with sub-component names and current contributions.
- **Annotations:** A single annotation on the most recent FCI level
  with its tight/loose state classification.
- **Recession bands:** `ink` at 6% opacity.
- **Caveat banner (variant B only, panel-foot above source line):**
  > *> Bank of Canada Financial Conditions Index not yet available via
  > Valet; v1 ships with Chicago Fed NFCI as comparator. Own Canadian
  > FCI composite deferred to v1.5.*
- **Callout:**
  - Big number: FCI level, e.g., `+0.42`
  - Unit: `BoC FCI (or NFCI proxy), May 8, 2026; tight conditions`
  - Direction row: `[arrow up] +0.08 vs prior week | Rates dominant
    contributor`
- **Vintage:** Three-line: `AS OF May 8, 2026 / Weekly close`
- **Source:** `Bank of Canada Financial Conditions Index via Valet
  (if available); else Chicago Fed National Financial Conditions
  Index via FRED NFCI.`
- **Methodology link:** Important — drawer explains the FCI source
  decision tree, the Canadian-FCI-deferred status, and the v1.5 plan
  for own composite construction.

---

## 9.F Trade basics page, all six panels blocked out

Per Section 4.7 of `editorial/dashboard_purpose.md`. Section accent:
`series-7` (slate, `#4A4F57`).

**Section-level visual rules (Trade only).**

- **The slate accent is the gentlest of the seven.** Trade's section
  accent is `series-7` slate (which is also `ink-muted`). This was a
  deliberate Section 1 mapping decision: Trade is the visually most
  neutral section and slate is the quietest of the seven hues. The
  consequence on this page is that the visual identity comes more
  from the **layout patterns** (partner-share stacking, by-category
  decomposition, the non-chart Tariff table) than from a strong
  section-color signal. The slate accent appears in kicker, eyebrow,
  hairline rule, and panel-index dots — and stays out of the way.
- **Non-chart reference-table panel.** Panel 4 (Tariff state) is the
  only non-chart panel on the entire basics layer across all seven
  sections. Per EDR 4.7 element 4: "Maintained as an editorial
  reference table... Not a numeric series." The visual treatment is a
  formal **reference-table card** with the same panel-card outer
  dimensions as the other Trade panels, so the grid alignment holds.
  Internal layout per panel 4 spec below.
- **By-category decomposition is a recurring shape.** Panels 1
  (merchandise trade decomposition), 2 (current account components),
  and 6 (FDI by sector) all use a categorical-decomposition pattern.
  Visual consistency across these three panels: same column-stacking
  rhythm, same EDR-canonical category order per panel, same
  direct-labeling treatment. The reader's eye learns the pattern on
  panel 1 and re-encounters it on 2 and 6.
- **Partner-share treatment is restrained.** Panel 3 (Partner shares)
  shows the US dominance + five peer partners. Visual restraint: the
  US share gets the section accent (slate); the five peer partners
  share a single muted secondary color (`series-7` at varying
  opacities). We do NOT rainbow-encode partners — the editorial point
  is US dominance and the rest, not a six-country comparison.

### Trade Panel 1 — Merchandise trade balance

- **Eyebrow:** `MERCHANDISE TRADE BALANCE`
- **Title slot:** active-voice sentence on the monthly balance, 3M MA
  direction, and which HS-section product category is driving.
  Writer.
- **Chart type:** **Two-block composite**.
  - Block A (top, ~55% height): trade balance time series, monthly,
    last 5 years, plotted as columns (positive surplus columns above
    zero, negative deficit columns below zero, divergent from zero
    line). 3M MA overlaid as a line. Headline series and ex-non-
    monetary-gold variant shown as two lines (per EDR 4.7 element 1).
  - Block B (bottom, ~45% height): by-category decomposition for the
    most recent month — a horizontal diverging bar chart, ~12 bars,
    one per HS-section product category, ordered from largest surplus
    contributor to largest deficit contributor.
- **Series colors:**
  - Block A columns: `series-7` (slate, section accent) at 60% opacity
    fill, with positive-surplus columns at 100% opacity (slate top
    of stack) and negative-deficit columns drawn from zero downward.
    Zero line in `ink-muted` 1px solid.
  - 3M MA overlay: `series-7` 2px solid weight 600 — the heaviest
    line on the page.
  - Ex-non-monetary-gold variant: `series-7` at 50% opacity, 1.5px
    dashed (`2 2`) weight 400.
  - Block B bars: each bar in `series-7` at 60% opacity if positive
    (surplus); same color but pointing leftward if negative (deficit).
    No category-color encoding — the editorial point is which
    categories are driving the balance, not which category each is.
    Most recent month's largest-magnitude category gets a 100% opacity
    highlight.
- **Direct labels:** Block A: line termini for both lines (headline
  and ex-gold). Block B: each bar labeled at its terminus with category
  name and $-value.
- **Annotations:** Block A annotates the most recent month's headline
  balance and 3M MA. Block B caption identifies the largest surplus
  category and the largest deficit category in chart whitespace.
- **Recession bands:** `ink` at 6% opacity, block A only.
- **Callout:**
  - Big number: most recent month's trade balance, e.g., `+$1.4B`
  - Unit: `merchandise trade balance, March 2026; 3M MA +$0.9B`
  - Direction row: `[arrow up] +$0.5B vs Feb | Energy products
    largest surplus contributor`
- **Vintage:** `AS OF May 6, 2026 / Reference: Mar 2026 (monthly)`
- **Source:** `Statistics Canada Tables 12-10-0119-01 (trade balance,
  BOP basis), 12-10-0121-01 (exports), 12-10-0122-01 (imports);
  non-monetary-gold-stripped variant constructed by macro-research-
  department.`
- **Methodology link:** Important — drawer explains the BOP-basis
  convention, the 3M MA construction, the non-monetary-gold strip
  logic, and the HS-section category aggregation.

### Trade Panel 2 — Current account

- **Eyebrow:** `CURRENT ACCOUNT`
- **Title slot:** active-voice sentence on quarterly current account
  level, goods/services split, and primary/secondary income reads.
  Writer.
- **Chart type:** **Stacked-column composition** time series. Quarterly
  current account components (goods balance, services balance, primary
  income, secondary income) stacked as columns over the last 5 years.
  Total current account balance plotted as a line overlay.
- **Series colors:**
  - Goods (bottom band): `series-7` (slate, section accent) at 80%
    opacity. The largest component in absolute magnitude.
  - Services: `series-7` at 50% opacity.
  - Primary income: `series-7` at 30% opacity.
  - Secondary income: `series-7` at 15% opacity. Top of stack /
    smallest contributor.
  - Total current account overlay line: `series-7` 2px solid weight
    600. The headline read.
  - Negative components drawn extending downward from zero line; zero
    line in `ink-muted` 1px solid.
- **Direct labels:** Each component band labeled at the right rail
  with component name and most recent quarter's contribution. Total
  line terminus labeled `Current account` in slate weight 600.
- **Annotations:** A single annotation in chart whitespace identifying
  the largest contributor to the most recent quarter's reading and
  the goods-vs-services split.
- **Recession bands:** `ink` at 6% opacity.
- **Callout:**
  - Big number: most recent quarter's current account, e.g., `-$8.2B`
  - Unit: `current account balance, Q4 2025; goods +$2.1B, services
    -$3.4B`
  - Direction row: `[arrow down] -$2.1B vs Q3 2025 | Services deficit
    widened`
- **Vintage:** `AS OF Feb 27, 2026 / Reference: Q4 2025 (quarterly)`
- **Source:** `Statistics Canada Table 36-10-0014-01.`
- **Methodology link:** Drawer explains the BPM6 framework, the
  four-component definitions, and the sustained-vs-one-off prose-
  level call-out logic per EDR 4.7 element 2.

### Trade Panel 3 — Partner shares

- **Eyebrow:** `PARTNER SHARES`
- **Title slot:** active-voice sentence on rolling US share trajectory
  and any structural shifts. Writer.
- **Chart type:** **Two-row composite**.
  - Row A (top, ~60% height): rolling-12-month US share of total
    Canadian merchandise exports + imports, time series, last 15 years.
    The structural-shift narrative lives here per EDR 4.7 element 3.
  - Row B (bottom, ~40% height): five-row horizontal bar chart for
    the most recent 12 months, showing share by peer partner (China,
    UK, Japan, Mexico, Germany).
- **Series colors:**
  - US share line (row A): `series-7` (slate, section accent), 2px
    solid weight 600. The thickest line on the page.
  - Peer partner bars (row B): all five in `series-7` at 40% opacity.
    Equal visual weight; no rainbow encoding.
  - Reference line at the US share's historical mean: `ink-faint`
    1px dashed (`4 2`), labeled at right rail `15y mean: X%` in
    `micro` `ink-faint`.
- **Direct labels:** Row A: line terminus with current US share value.
  Row B: each bar labeled with partner name and current share %.
- **Annotations:** Row A carries one structural-shift annotation in
  chart whitespace identifying any sustained departure from the
  15y mean (writer composes).
- **Recession bands:** `ink` at 6% opacity, row A only.
- **Callout:**
  - Big number: US share rolling-12M, e.g., `74.8%`
  - Unit: `US share of Canadian merchandise trade, rolling 12M, Mar
    2026`
  - Direction row: `[arrow down] -1.4pp vs prior year | China share
    next-largest at 4.2%`
- **Vintage:** `AS OF May 6, 2026 / Reference: Mar 2026 rolling 12M`
- **Source:** `Statistics Canada Tables 12-10-0121-01 (exports) and
  12-10-0122-01 (imports), bilateral.`
- **Methodology link:** Drawer explains the rolling-12M construction,
  the structural-shift call-out logic, and the Pillar G/H deep-dive
  deferrals for energy export decomposition and the US trade
  relationship.

### Trade Panel 4 — Tariff state (non-chart reference table)

This is the only non-chart panel on the entire basics layer across
all seven sections.

- **Eyebrow:** `TARIFF STATE`
- **Title slot:** active-voice sentence on the current US tariff
  posture and USMCA review milestone status. Writer.
- **Chart type:** **Reference table**, not a chart. Layout: a formal
  table inside the panel card, occupying the same canvas the chart
  would in other panels (~432px wide, ~280px tall on desktop).
  Treatment per design-system Section 6 table conventions; zebra
  rows in `surface-sunk`; column headers in `label` size weight 500
  letter-spacing `0.08em` `ink-muted`.
- **Table structure:**
  ```
  | PRODUCT GROUP    | RATE   | EFFECTIVE   | STATUS / NOTE   |
  |------------------|--------|-------------|-----------------|
  | Steel (Sec 232)  | 25%    | Mar 12, 2025| In effect       |
  | Aluminum (S 232) | 10%    | Mar 12, 2025| In effect       |
  | Softwood lumber  | 14.5%  | Aug 14, 2025| In effect       |
  | [further rows...]                                          |
  ```
  Plus a footer row in `body-sm` italic `ink-muted` naming the
  USMCA review milestone status: e.g., *"USMCA review: joint
  review window opens July 2026."*
- **Series colors:** None (table). Rate cells with active duty-deposit
  flags get a small `accent` (`#A6192E`) caret glyph (`!`) immediately
  after the rate value; hover reveals deposit-status tooltip.
- **Direct labels:** Table headers as above. No chart, no series
  labels.
- **Annotations:** A single chart-foot annotation in `body-sm` italic
  `ink-muted` immediately below the table, identifying the most
  recent USTR proclamation date and the next scheduled review event
  (writer composes).
- **Recession bands:** None (no chart).
- **Callout:** Editorial status block (no single number):
  - Status label: `TARIFF STATE`
  - Status line: writer-filled, e.g., *"Section 232 steel and
    aluminum duties remain in effect; softwood lumber AD/CVD
    duties at 14.5% combined; no new product groups added since
    August 2025."*
  - Context line: writer-filled, optionally referencing the USMCA
    joint-review timing.
- **Vintage:** `AS OF [most recent USTR proclamation or CBSA notice
  date]`
- **Source:** `USTR proclamations; Canada Border Services Agency
  tariff classifications; Department of Finance retaliatory-tariff
  notices.`
- **Methodology link:** Important — drawer explains the editorial-
  maintenance posture (this is a curated reference table, not a
  derived numeric series), the inclusion criteria for tariff actions,
  and the USMCA review milestone definition.
- **Open question for chart-builder:** Confirm the table-as-panel
  pattern fits within the standard panel-card structural slot. The
  callout-equivalent (`TARIFF STATE` editorial status block) sits in
  the same vertical position as the latest-print callout on other
  panels, so the grid alignment should hold — but flag any rendering
  edge cases on mobile (the table may need horizontal scrolling at
  `sm` breakpoint).

### Trade Panel 5 — Terms of trade

- **Eyebrow:** `TERMS OF TRADE`
- **Title slot:** active-voice sentence on the StatCan ToT direction
  and the BoC commodity price index lead. Writer.
- **Chart type:** **Two-line time series** — StatCan terms of trade
  index (quarterly) plotted alongside BoC commodity price index
  (BCPI or BCNE, daily resampled to monthly for visual alignment).
  Both indexed to a common base year. Last 10 years.
- **Series colors:**
  - StatCan ToT: `series-7` (slate, section accent), 1.5px solid
    weight 500. Discrete-quarterly cadence — connected points-and-
    line treatment with 5px filled circles at each quarterly
    observation, signaling the lower-frequency series.
  - BoC commodity price index (BCPI/BCNE): `series-6` (olive gold —
    cross-section color reference to Markets/Energy), 1.5px solid
    weight 500. Continuous monthly line; the higher-frequency
    leading line.
- **Direct labels:** Both line termini with current index values and
  series names (`Terms of trade`, `BoC commodity index`).
- **Annotations:** A single annotation in chart whitespace identifying
  the BoC commodity index's lead time vs the ToT (writer composes
  example: *"BoC commodity index typically leads ToT by ~6 months;
  current divergence consistent with that pattern."*).
- **Recession bands:** `ink` at 6% opacity.
- **Callout:**
  - Big number: ToT index level, e.g., `108.4`
  - Unit: `StatCan terms of trade, Q4 2025 (2017 = 100); BoC
    commodity index +4.2% Y/Y`
  - Direction row: `[arrow up] +2.1 vs Q3 2025 | BoC commodity index
    leads`
- **Vintage:** Two stamps:
  ```
  AS OF
  ToT: Feb 27, 2026 (Q4 2025)
  BCPI: May 7, 2026 (Apr 2026, monthly avg)
  ```
- **Source:** `Statistics Canada Table 36-10-0103-01 (terms of
  trade); Bank of Canada commodity price index (BCPI / BCNE, Valet).`
- **Methodology link:** Drawer explains the base-year convention,
  the BoC commodity index variants (BCPI vs BCNE), and the cadence-
  mismatch handling (quarterly vs daily resampled).

### Trade Panel 6 — FDI by sector

- **Eyebrow:** `FDI BY SECTOR`
- **Title slot:** active-voice sentence on FDI inflows and outflows
  by sector, with any M&A one-off flags. Writer.
- **Chart type:** **Two-block composite, by-sector decomposition**.
  - Block A (top, ~50% height): FDI inflows by sector, quarterly,
    last 5 years. Stacked-column composition by sector (top ~5
    sectors by absolute size + "other").
  - Block B (bottom, ~50% height): FDI outflows by sector, same
    visual treatment, last 5 years.
- **Series colors:**
  - Sector bands (both blocks): six-color categorical from the design-
    system palette in canonical sector order. Top 5 sectors get
    `series-1` through `series-5`; "other" gets `series-7` (slate).
    Same color = same sector across inflows and outflows so the eye
    carries the encoding across both blocks.
  - Total FDI line overlay (each block): `series-7` (slate) 1.5px
    solid weight 600. The headline read on each block.
- **Direct labels:** Each sector band labeled at the right rail in
  the most recent column with sector name and $-value. Total line
  termini labeled `Total inflows` / `Total outflows`.
- **Annotations:** Per EDR 4.7 element 6 — known M&A-driven one-offs
  flagged in chart whitespace with a small `series-4` (plum) caret
  glyph (`*`) at the affected quarter, hover tooltip naming the deal
  and amount. The `*` glyph is a quiet annotation; the editorial
  caveat is in the methodology drawer.
- **Recession bands:** `ink` at 6% opacity, both blocks.
- **Callout:**
  - Big number: net FDI (inflows - outflows) most recent quarter,
    e.g., `-$2.4B`
  - Unit: `net FDI, Q4 2025; inflows $18B, outflows $20.4B`
  - Direction row: `[arrow down] -$5B vs Q3 2025 | Resources sector
    largest inflow contributor`
- **Vintage:** `AS OF Mar 25, 2026 / Reference: Q4 2025 (quarterly)`
- **Source:** `Statistics Canada Table 36-10-0008-01 (FDI inflows
  and outflows by sector).`
- **Methodology link:** Important — drawer explains the sector
  aggregation rules, the M&A one-off identification logic, and the
  flag-glyph convention.

---

## 10. ASCII mockup — GDP basics page

```
+------------------------------------------------------------------------+
|                                                                        |
|  MACRO RESEARCH DEPARTMENT  |  SECTION 1 OF 7  |  GDP                  |
|                                                                        |
|  GDP                                                                   |
|                                                                        |
|  Is the Canadian economy at potential, growing, or contracting --     |
|  and what is driving it?                                               |
|                                                                        |
|  LATEST RELEASE  Monthly GDP by industry, Mar 2026 (released May 1)    |
|  --------------------------------------------------------- (accent)    |
|                                                                        |
|                                                                        |
|                 .  .  .  .  .  .                                       |
|                 1  2  3  4  5  6                                       |
|                                                                        |
|                                                                        |
|  +---------------------------------+  +-----------------------------+  |
|  | HEADLINE REAL GDP    AS OF      |  | INDUSTRY VS EXPENDITURE     |  |
|  |                      May 1, 2026|  |               AS OF May/30  |  |
|  |                      Ref Mar 26 |  |               Industry/Exp  |  |
|  |                                 |  |                             |  |
|  | Monthly GDP rose 0.2%           |  | Industry and expenditure    |  |
|  | in March, on consensus.         |  | cuts agree on direction.    |  |
|  | The economy advanced for the    |  | A 0.1pp level gap sits      |  |
|  | second consecutive month...     |  | within typical range.       |  |
|  |                                 |  |                             |  |
|  | [chart: dual-frequency bar+line]|  | [chart: two-line overlay]   |  |
|  |                                 |  |                             |  |
|  | +0.2%                           |  | Cross-check: in agreement;  |  |
|  | month-over-month, March 2026    |  | gap 0.1pp on the level.     |  |
|  | ^ +0.1pp vs Feb | Beat con.[c]  |  |                             |  |
|  |   [Revised up]                  |  |                             |  |
|  | -----------------------------   |  | -----------------------     |  |
|  | Source: StatCan 36-10-0434-01;  |  | Source: StatCan 36-10-0434, |  |
|  | consensus via Bloomberg.        |  | 36-10-0104.                 |  |
|  |                  Methodology >  |  |              Methodology >  |  |
|  +---------------------------------+  +-----------------------------+  |
|                                                                        |
|  +---------------------------------+  +-----------------------------+  |
|  | CONTRIBUTIONS TO GROWTH         |  | PER-CAPITA REAL GDP         |  |
|  |                  AS OF May/30   |  |                AS OF May/30 |  |
|  |                  Ref Q1 2026    |  |                Ref Q1 2026  |  |
|  |                                 |  |                             |  |
|  | Q1 growth led by consumption    |  | Per-capita output remains   |  |
|  | and exports; imports drag.      |  | in contraction for the      |  |
|  |                                 |  | seventh consecutive quarter.|  |
|  |                                 |  |                             |  |
|  | [chart: 6 horizontal bars,      |  | [chart: aggregate vs        |  |
|  |  diverging from zero]           |  |  per-capita Y/Y two lines]  |  |
|  |                                 |  |                             |  |
|  | +1.4%                           |  | -1.0%                       |  |
|  | quarterly, annualized, Q1 2026  |  | year-over-year, Q1 2026     |  |
|  | ^ +0.6pp vs Q4 | Beat con[c]    |  | v 7 consecutive Q in        |  |
|  |                                 |  |   contraction               |  |
|  | -----------------------------   |  | -----------------------     |  |
|  | Source: StatCan 36-10-0104-01.  |  | Source: StatCan 36-10-0104, |  |
|  |                  Methodology >  |  | 17-10-0009.  Methodology >  |  |
|  +---------------------------------+  +-----------------------------+  |
|                                                                        |
|  +---------------------------------+  +-----------------------------+  |
|  | OUTPUT GAP                      |  | RECESSION STATE             |  |
|  |                  AS OF          |  |                AS OF        |  |
|  |                  GDP May/30     |  |                BCC Mar 2026 |  |
|  |                  MPR Apr/16     |  |                             |  |
|  |                                 |  |                             |  |
|  | Output sits 0.5% below BoC's    |  | Expansion continues from    |  |
|  | central potential estimate.     |  | Q3 2020 per C.D. Howe BCC.  |  |
|  |                                 |  |                             |  |
|  | [chart: GDP vs potential, gap   |  | [chart: 20-year cycle       |  |
|  |  shaded ink @ 6%]               |  |  timeline, current expand   |  |
|  |                                 |  |  in section accent]         |  |
|  |                                 |  |                             |  |
|  | -0.5%                           |  | Current state: Expansion    |  |
|  | Q1 2026, BoC central estimate   |  | since 2020Q3. BCC: dating   |  |
|  | ^ +0.2pp vs Q4 2025             |  | committee minutes most       |  |
|  |                                 |  | recent communique.          |  |
|  | -----------------------------   |  | -----------------------     |  |
|  | Source: BoC INDINF_OUTGAPMPR_Q; |  | Source: C.D. Howe Business  |  |
|  | StatCan 36-10-0104. Method >    |  | Cycle Council. Method >     |  |
|  +---------------------------------+  +-----------------------------+  |
|                                                                        |
+------------------------------------------------------------------------+
```

(The ASCII mockup compresses layout for legibility. In implementation: card
padding `s-6` (32px), inter-panel gutter `s-6` vertical / `s-5` horizontal,
charts at full panel-content width. The mockup also represents arrows as
`^` and `v` glyphs for ASCII — in implementation, these are Lucide
`arrow-up` / `arrow-down` at 14px in pos / neg colors.)

---

## 11. Cohesion rules

How does this template stay coherent with the rest of the site?

- **Page background:** `paper` (`#FBF8F2`). Same as homepage, same as deep-
  dive pages. No section gets its own background color.
- **Card background:** `surface` (`#FFFFFF`). Same as all cards site-wide.
- **Type families:** Serif display, sans body, mono numerics — exact same
  pairing as homepage and as deep dives. Never substitute.
- **Section identity comes from one color and one place.** The section
  accent appears in: the kicker, the panel eyebrows, the section breadcrumb
  in nav, the hairline rule beneath the header. It does **not** color
  charts. It does **not** color card borders. It does **not** color the
  card background. This restraint is the difference between editorial-
  grade and "themed dashboard."
- **Charts in a panel are full charts.** They get titles (the panel title
  is the chart title), decks, direct labels, source lines, methodology.
  They are not sparklines. They are not "KPI tiles." Per
  `design/design-system.md` Section 5: a small chart in a card is still a
  full chart and gets full chrome.
- **Spacing rhythm.** Inter-panel spacing is `s-6` / `s-7` (32 / 48px),
  matching the inter-section spacing on deep-dive pages. The page does not
  read denser than a deep dive; it reads as serious as a deep dive.
- **Source-line ritual.** Same format, same typography, same placement on
  every panel, every page. The source line is the publication's signature.

---

## Open questions

### EDR rulings folded in (2026-05-11)

The three open questions previously held open for editorial-director have
been adjudicated. The spec is updated in-line above; the rulings are
recorded here as canonical:

1. **Page-level vintage stamp = least-recent.** Per EDR ruling
   2026-05-11. The header stamp surfaces the *stalest* panel on the page,
   not the freshest. Rationale: conservative answer for the 7am allocator.
   Spec updated in Section 1 (header) and Section 6 (page-level vs
   panel-level). Writer owns the two-state kicker word (`OLDEST PANEL` vs
   `LATEST RELEASE`); art-director owns the visual treatment.
2. **Editorial-status-panel ownership = split.** Per EDR ruling
   2026-05-11. Art-director defines the three-slot structure (status
   label / status line / optional context line); writer defines the
   wording on each refresh; the label list per section is locked once
   between writer and art-director and does not silently drift. Spec
   updated in Section 3 ("Panel without a callout?").
3. **Revision-tag scope = single point with multi-period footnote.** Per
   EDR ruling 2026-05-11. The basics layer marks only the most recently
   revised point in the chart; multi-period revisions get a footnote-
   style chart-whitespace annotation. Fan/ribbon/vintage-stack revision
   visuals are strictly deep-dive. Spec updated in Section 5 ("When the
   revision spans multiple periods").

### Remaining open questions for EDR

(none at v0.2; raise new ones here on next round)

For **frontend-designer (FD):**

1. **Section accent token wiring.** Spec proposes `--section-accent` set
   once at page root via `<body data-section="gdp">`. Confirm this is the
   ergonomics you want; alternative is a CSS class per section
   (`.section-gdp`). Either works for me — your call on implementation.
2. **Methodology drawer vs page.** Spec proposes a right-side drawer
   (slide-in, max-width 480px). Question: when methodology pages get long
   (some deep-dive constructions in v1.5+ will), do you want the drawer to
   degrade into a full page at a content-length threshold, or do we always
   commit to drawer-only? Recommend always-drawer for v1; defer to page if
   we have a 1000+ word methodology.
3. **Panel index dots responsive behavior.** On mobile, 6 dots in a row
   is fine, but the hover-label affordance does not exist on touch. Spec
   says: on `sm` breakpoint, dots become tap-to-scroll-to-anchor with no
   label-on-hover (the panel title appears below the dot at all times in
   `micro` size, abbreviated). Confirm.
4. **Reduced-motion behavior on the revision-open-circle marker.** The
   spec uses a static dashed line, no motion involved, so reduced-motion
   is fine. Just flagging that we are not animating the "where it was ->
   where it is" hop. Static dashed line conveys it.

---

## Appendix — token extension request

For main Claude to fold into `design/design-system.md` after user review:

```
/* Section wayfinding accent */
--section-accent: var(--series-1);  /* default; overridden per page */

/* Per-page override pattern: */
body[data-section="gdp"]        { --section-accent: var(--series-1); }
body[data-section="inflation"]  { --section-accent: var(--series-2); }
body[data-section="labour"]     { --section-accent: var(--series-3); }
body[data-section="housing"]    { --section-accent: var(--series-4); }
body[data-section="policy"]     { --section-accent: var(--series-5); }
body[data-section="markets"]    { --section-accent: var(--series-6); }
body[data-section="trade"]      { --section-accent: var(--series-7); }
```

No new hex values are introduced. The section accent is a *reference* to
existing palette tokens. This keeps the system tight: every color on the
site is one of the original palette entries.

---

End of basics-layer template v0.3.
