# Basics-Layer Page Template

Status: v0.2, living document. Author: art-director.
Last updated: 2026-05-11.

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

End of basics-layer template v0.1.
