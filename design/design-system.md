# macro-research-department — Design System

Status: v0.2, living document. Author: art-director.
Last updated: 2026-05-11.

This is the visual constitution. Every page, chart, and component cites this
document. Frontend-designer and chart-builder implement to this spec. When a
constraint forces deviation, raise it back to art-director — do not silently
relax the bar.

---

## 1. Visual identity statement

**Reference lane: FT visual journalism, with Reuters Graphics restraint and a
small dose of Pudding-style hand-tuned annotation.**

We are an **editorial-grade Canadian macro research dashboard**. The reader is
a serious adult — a policy analyst, a journalist, a Bay Street economist, an
informed citizen. They came for a paragraph and a chart that tells them
something true about the Canadian economy. Not a dashboard with KPI tiles. Not
a fintech app with glowing gradients. Not a marketing site with hero
animations. The page should feel like it was set, not assembled.

**What this commits us to:**

- **Off-white page, near-black ink.** The page reads like a printed broadsheet
  feature. Pure white (#FFFFFF) is for product surfaces; we are not a product.
- **A serif for display, a humanist sans for body and UI.** Serif headlines
  signal "this was written by someone." Sans body keeps long reading and
  numeric tables legible at small sizes.
- **Charts that look drawn, not generated.** Direct labels over legends.
  Annotations placed by hand. Axis chrome muted to near-invisible. Recessions
  shaded like a footnote, not like a warning.
- **One accent color, used sparingly.** A single editorial red. Categorical
  palettes are restrained; we use color to mean things, not to decorate.
- **Light mode only, v1.** Dark mode is deferred. Justification in section 3.

**What this commits us against:**

- No neon. No gradients on data. No drop shadows on cards. No glassmorphism.
- No emoji in UI. No icon-driven navigation.
- No "data viz as decoration" — every mark earns its place.
- No animated number tickers, no scroll-jacking, no entrance animations on
  every element.

**Exemplars to study (and what we take from each):**

- *FT — "Climate Graphic of the Week" series.* Take: muted page, single hero
  chart, direct labeling, generous margins, serif headline + sans deck.
- *FT — John Burn-Murdoch's Covid charts (2020-22).* Take: small multiples
  with shared y-axis, country callouts in series color, recession-shading
  discipline.
- *Reuters Graphics — "The Collapse of the Quebec Bridge" (and similar
  long-form).* Take: restrained palette, typographic confidence, willingness to
  let one chart fill the column.
- *NYT Upshot — "How Trump Reshaped..." style pieces.* Take: annotation
  typography that competes with body copy, not chart chrome.
- *The Economist — Daily Chart.* Take: red accent discipline, deck-style
  subtitles in italic, source line as a typographic ritual.
- *The Pudding — "Pockets" / "Wine & Math."* Take (selectively): the courage
  to hand-tune. We borrow the spirit, not the playfulness.

We are **not** The Pudding (too playful), **not** Bloomberg Terminal (too
dense, too dark, too utilitarian), **not** The Economist's website (too
branded-red-everywhere). We sit closest to FT long-form features.

---

## 2. Typography

**Pairing: serif display + humanist sans body + monospace for numerics in
tables.**

### Families

- **Display (headlines, deck, chart titles):**
  `"Source Serif 4", "Source Serif Pro", Georgia, "Times New Roman", serif`
  - Open-source, designed for editorial reading at multiple sizes.
  - Has a true italic (not slanted roman) — required for decks and emphasis.
  - Fallback to Georgia preserves serif feel on systems without webfonts.

- **Body and UI (paragraphs, captions, labels, buttons, navigation):**
  `"Inter", "Inter var", -apple-system, BlinkMacSystemFont, "Segoe UI",
  Roboto, "Helvetica Neue", Arial, sans-serif`
  - Humanist sans with strong numerics, designed for screens.
  - Tabular figures available via `font-feature-settings: "tnum"`.
  - System-font fallback chain keeps render-blocking low if Inter fails.

- **Monospace (data tables, code, inline figures where alignment matters):**
  `"IBM Plex Mono", "JetBrains Mono", "Consolas", "Menlo", monospace`
  - Plex Mono pairs visually with Inter (both humanist).
  - Used for: table numerics, source-code blocks, raw release dates.

**Why this pairing:** Serif heads signal editorial authority and slow the eye
at the top of the page. Inter handles dense numerical context and long
captions without fatigue. Plex Mono is reserved — when readers see it, they
know they are looking at a raw number, not a designed one.

### Scale

Modular scale at ratio 1.20 (minor third), base 16px. Capped on both ends —
we do not need 64px display type for a research site, and we do not need
10px body.

| Token        | Size  | Line height | Weight | Family  | Role                                      |
|--------------|-------|-------------|--------|---------|-------------------------------------------|
| `display-xl` | 40px  | 1.10        | 600    | Serif   | Page hero headline (one per page max)     |
| `display-lg` | 33px  | 1.15        | 600    | Serif   | Section opener                            |
| `display-md` | 28px  | 1.20        | 600    | Serif   | Chart title (hero charts only)            |
| `display-sm` | 23px  | 1.25        | 600    | Serif   | Subsection / card title                   |
| `deck`       | 19px  | 1.45        | 400 it | Serif   | Deck / standfirst under headlines         |
| `body-lg`    | 19px  | 1.55        | 400    | Sans    | Lede paragraph                            |
| `body`       | 17px  | 1.55        | 400    | Sans    | Default body copy                         |
| `body-sm`    | 15px  | 1.50        | 400    | Sans    | Captions, chart titles when inline        |
| `label`      | 13px  | 1.40        | 500    | Sans    | Chart axis labels, UI labels              |
| `micro`      | 12px  | 1.40        | 500    | Sans    | Source lines, footnotes, tick labels      |
| `mono-sm`    | 14px  | 1.45        | 400    | Mono    | Inline numerics in tables                 |
| `mono-xs`    | 12px  | 1.40        | 400    | Mono    | Table cells, dates, ISO codes             |

### Treatment rules

- **Numbers in body prose use Inter with tabular figures.** No exceptions —
  prevents column shimmy in numeric paragraphs.
- **Numbers in charts use Inter, tabular, weight 500 for emphasized
  callouts and 400 for axis ticks.** Never serif — serif numerics in chart
  context read as decorative.
- **Numbers in tables use Plex Mono.** Right-aligned, tabular.
- **Units stay with their number.** `2.4%` not `2.4 %`. `$1.2B` not
  `$1.2 B`. `bps` joined with thin space: `25 bps` in source, rendered
  as `25 bps`.
- **Italic is reserved.** Deck/standfirst, publication names, emphasis in
  prose. Not for UI labels.
- **All caps reserved for eyebrow labels** (`KICKER`, `SECTION`) at
  `label` size with letter-spacing `0.08em`. Never for headlines.
- **Line length: 62-72 characters for body prose.** Enforced via
  `max-width` on text columns, not via per-element widths.

---

## 3. Color palette

**One serious neutral system, one editorial red accent, a disciplined chart
palette. Light mode only in v1.**

### Light mode only — justification

Dark mode doubles the design and test surface. For an editorial site whose
primary reading mode is daytime desktop / morning commute, the cost is not
justified at v1. Charts tuned for dark backgrounds require different palettes
(higher chroma, different contrast targets), different shading patterns for
recessions, and different annotation typography weights. Revisit at v2 only
if reader analytics show meaningful evening/mobile-dark reading.

### Neutrals — the page

| Token          | Hex       | Role                                              |
|----------------|-----------|---------------------------------------------------|
| `paper`        | `#FBF8F2` | Page background. Warm off-white. Broadsheet feel. |
| `surface`      | `#FFFFFF` | Cards, chart canvases. Slightly brighter than page. |
| `surface-sunk` | `#F4F0E8` | Pulled-back panels (footnotes, sidenotes).        |
| `ink`          | `#15171A` | Primary text. Near-black, not pure black.          |
| `ink-muted`    | `#4A4F57` | Secondary text, decks.                            |
| `ink-faint`    | `#7A7F88` | Captions, source lines, axis tick labels.         |
| `rule`         | `#D9D3C7` | Rule lines, table borders, card edges.            |
| `rule-faint`   | `#ECE7DC` | Gridlines, sub-table dividers.                    |

**Why warm off-white (#FBF8F2):** Pure white feels like a product UI. Warm
off-white feels like paper. FT, NYT print supplements, Reuters long-form all
use a warmth in the page color. It also reduces the contrast burn of
near-black text without sacrificing legibility (#15171A on #FBF8F2 is
contrast ratio 15.2:1, well above WCAG AAA for body text).

### Accent — editorial red

| Token         | Hex       | Role                                       |
|---------------|-----------|--------------------------------------------|
| `accent`      | `#A6192E` | Editorial red. Logo, hero kicker, key UI accents. |
| `accent-soft` | `#F1D9DC` | Background wash for callout boxes (sparingly). |

One color. Used to signal "this is the publication's voice." Never used to
encode data values (because that would conflict with semantic red — see
below). Borrowed in spirit from Economist red and Reuters orange, tuned
slightly cooler and more burgundy to feel Canadian-establishment rather than
British-news-magazine.

### Semantic colors — for data

| Token            | Hex       | Role                                          |
|------------------|-----------|-----------------------------------------------|
| `pos`            | `#1F6B3A` | Positive change, growth, beats expectations.  |
| `pos-soft`       | `#D4E5D8` | Positive fill / background wash.              |
| `neg`            | `#B23A2F` | Negative change, contraction, misses.         |
| `neg-soft`       | `#EAD3CE` | Negative fill / background wash.              |
| `neutral`        | `#5A6470` | Flat, no change, "as expected."               |
| `neutral-soft`   | `#DDE0E4` | Neutral fill.                                 |

**Note:** `neg` (`#B23A2F`) is intentionally close to but distinct from
`accent` (`#A6192E`). Accent is brand; neg is data. They should never appear
adjacent — if they would, swap accent to ink for that surface.

**Pos/neg green-red convention:** We use it because the audience is
finance-literate and inversion would create friction. We do not use it
decoratively — only for actual directional data values (change vs prior,
surprise vs consensus). Color-blind-safety is handled via shape and
position, not by abandoning the convention.

### Chart series palette — categorical

Ordered, hand-tuned. Drawn from FT and Economist tradition but rebalanced for
warm off-white background.

| Token       | Hex       | Notes                                          |
|-------------|-----------|------------------------------------------------|
| `series-1`  | `#1F4E79` | Deep blue. Default first series.               |
| `series-2`  | `#C9772A` | Burnt orange. Default second series.           |
| `series-3`  | `#5B7553` | Sage green. Tertiary.                          |
| `series-4`  | `#7A3E65` | Plum. Quaternary.                              |
| `series-5`  | `#3F7D7C` | Teal.                                          |
| `series-6`  | `#8A6A2C` | Olive gold.                                    |
| `series-7`  | `#4A4F57` | Slate (= `ink-muted`). For "other" / baseline. |

Rules:
- Never use more than 5 series in a single chart. If you need more, switch
  to small multiples.
- Series 1 + 2 (deep blue + burnt orange) are the workhorse two-series
  pair. They are color-blind distinguishable (tested against deuteranopia
  and protanopia simulations) and read well against `paper`.
- `series-7` (slate) is reserved for the "rest of category" or "Canada
  average" line — it visually retreats.

### Chart series palette — sequential (for choropleths, heatmaps)

Single-hue ramps. Choose the ramp that matches the encoded meaning:

- **Sequential blue** (e.g., for magnitudes where higher = more):
  `#EDF2F7 -> #C5D5E4 -> #8FB0CC -> #5C8AB1 -> #2E6594 -> #1F4E79`
- **Sequential orange** (for an alternate hue if blue is taken):
  `#FBEBDA -> #F0CDA0 -> #DDA76A -> #C9772A -> #9A5818 -> #6E3D0F`
- **Diverging (signed magnitudes around zero):**
  `#B23A2F -> #D89589 -> #EAD3CE -> #F4F0E8 -> #D4E5D8 -> #7FAE89 -> #1F6B3A`
  Anchored on `surface-sunk` at zero so the page reads through.

5-7 stops max. No 11-step ramps — they pretend to a precision the data does
not have.

### Recession / event shading

- **Recession bands:** `#15171A` at 6% opacity (i.e., `rgba(21,23,26,0.06)`).
  Reads as a tint, never as a block. Label with `micro` size text at the
  top edge of the band, not inside it.
- **Event lines (e.g., rate decision, GDP release):** 1px solid `ink-faint`,
  dashed (`4 2`), with a `micro` label rotated 0deg sitting above the chart
  area, never crossing axis labels.

---

## 4. Density and rhythm

### Spacing scale (base 4px)

| Token    | Value | Use                                                |
|----------|-------|----------------------------------------------------|
| `s-0`    | 0     | -                                                  |
| `s-1`    | 4px   | Inline icon-to-label, tight micro                  |
| `s-2`    | 8px   | Chart tick to label, table cell padding-y          |
| `s-3`    | 12px  | Label to value, dense list rows                    |
| `s-4`    | 16px  | Default paragraph spacing, card padding-y small    |
| `s-5`    | 24px  | Card padding default, between body paragraphs      |
| `s-6`    | 32px  | Chart to caption, section internal                 |
| `s-7`    | 48px  | Between sections within a page                     |
| `s-8`    | 72px  | Major section break, hero margins                  |
| `s-9`    | 112px | Page top/bottom, before footer                     |

Vertical rhythm is paragraph-driven, not grid-locked. Charts break the
rhythm intentionally — they should feel like a different object on the page,
not a flowed block.

### Grid

- **12-column grid**, gutter 24px, with a `content` track and an optional
  `wide` track for hero charts that breathe past the body column.
- **Body column max-width: 680px** (yields ~66 characters at body size — the
  sweet spot for serious reading).
- **Wide chart max-width: 1040px.** Hero charts only. Set the chart at this
  width and let body text live in the 680px column above/below.
- **Page max-width: 1200px** with a 32px gutter on either side at desktop,
  contracting to 16px at mobile.

### Breakpoints

| Token | Min width | Notes                                          |
|-------|-----------|------------------------------------------------|
| `sm`  | 0         | Mobile default. Single column, charts stack.    |
| `md`  | 640px     | Larger phones / small tablets.                  |
| `lg`  | 960px     | Tablet landscape, small laptop.                 |
| `xl`  | 1200px    | Desktop default.                                |
| `2xl` | 1440px    | Large desktop. No wider canvas — just margin.   |

Mobile is a citizen, not an afterthought. Hero charts must have a
small-screen variant designed (typically: fewer series, larger labels, axis
abbreviation). That is `chart-builder`'s job to implement, but the spec
comes from art-director per chart.

---

## 5. Chart aesthetic principles

Principles, not pixel specs. Each hero chart gets its own visual spec from
art-director before `chart-builder` builds.

### Axes

- **Y-axis:** No axis line. Labels float left of the chart area. Ticks
  inferred from gridlines.
- **X-axis:** Single 1px rule in `rule` color along the bottom of the plot
  area. Tick marks 4px, outward. Labels in `micro` size, `ink-faint`.
- **Zero line:** When the chart includes negative values, draw the zero
  line at 1px in `ink-muted` (darker than gridlines but lighter than ink).
  Otherwise omit the zero line — the x-axis is the zero.
- **Axis titles:** Almost never used. Unit belongs in the chart title or
  on the topmost y-tick (e.g., `4% per year`). If you need an axis title to
  understand the chart, the chart title is failing.

### Gridlines

- **Horizontal gridlines only.** Vertical gridlines almost never (exception:
  small multiples with a shared x-time-axis where the eye needs anchor).
- **Color: `rule-faint` (`#ECE7DC`).** They are anchors, not features.
- **Density: 4-6 horizontal gridlines max.** More is noise.
- **The gridline at zero is `ink-muted`, not `rule-faint`** (see above).

### Label hierarchy

In order of importance — title and direct labels first, axis chrome last.

1. **Chart title** (`display-md` for hero, `body-sm` weight 600 for inline).
   Active voice. Owned by `writer`.
2. **Deck / standfirst** (`body-sm` italic, `ink-muted`). One sentence
   answering "so what?"
3. **Direct series labels** at the end of each line, in series color,
   weight 500, `label` size. Replaces legends wherever possible.
4. **Annotations** — see below.
5. **Axis tick labels** (`micro`, `ink-faint`).
6. **Source line** (`micro`, `ink-faint`, prefixed `Source:`).

### Series color rules

- **One series:** `series-1` (deep blue).
- **Two series with comparison:** `series-1` (focus) + `series-7` (slate,
  recedes). Use this when one series is the story and the other is context.
- **Two series with parity:** `series-1` + `series-2`.
- **Three to five series:** `series-1` through `series-5` in order, unless
  semantic encoding (e.g., political party, region) overrides ordering.
- **One highlighted series + many context series:** highlight in `accent`
  (the editorial red), context in `rule` at 1.5px. Only use `accent` on
  data when the chart is making an editorial argument about one series, and
  this must be approved by art-director.

### Annotations

Annotations are the difference between a chart and a story. Treatment rules:

- **Typography:** `body-sm` (15px) Inter, weight 400 normally, weight 500
  for the inline "anchor word." Color: `ink` for the primary annotation,
  `ink-muted` for secondary.
- **Leader lines:** 1px `ink-muted`, no arrowhead. Lines are straight or
  single-elbow — no curves, no S-curves. End the leader 4px short of the
  data point (let the eye close the gap).
- **Placement:** Hand-tuned. Annotations go in white space, not over data.
  If you cannot place an annotation in white space, the chart needs more
  margin.
- **Anchor:** Every annotation anchors to a specific data point or region.
  Floating annotations forbidden.
- **Length:** 1-2 short clauses, max ~12 words. Longer thoughts belong in
  body prose.
- **Wording:** Owned by `writer`. Visual treatment owned here.

### Recession / event shading

See section 3 for the colors. Treatment:

- **Recession bands** sit *behind* gridlines and *behind* data. They are
  context, not features.
- **Recession labels** at top edge in `micro` `ink-faint`. Format:
  `Recession (2008Q4-2009Q2)`. Only label the most recent or most relevant
  recession in any given chart — labeling all of them is noise.
- **Event lines** are foreground. Label rotated 0deg, sitting above the plot
  area in a 16px reserved band. Never crossing other labels.

### Three chart tiers: sparkline, mini-chart, full chart

We run a three-tier chart system. Each tier is a different object with
different rules — confusing one tier for another is the most common visual
failure mode. The tiers are ordered by ambition, from decorative to
editorial.

**Tier 1 — Sparkline (inline, ~80x20px to ~160x40px):**
- No axes, no gridlines, no labels inside the line.
- Single series, single color (`ink-muted` default, or `accent` if it is
  the page's hero metric).
- Last point dot at 3px, in series color.
- Inline number to the right at `mono-sm` size showing the latest value.
- Optional `pos` / `neg` color on the number only, not the line.
- Decorative role: the sparkline supports a number; the number is the
  story.

**Tier 2 — Mini-chart (homepage tiles, ~248x72 plot area):**
- See full mini-chart spec in Section 5.1 below.
- Sits between the sparkline (decorative) and the full chart (editorial).
- Has just enough chrome (x-axis rule, last-point dot+label, optional
  reference rule, optional recession band) to read as a chart, not as
  decoration.
- Single series only. No annotations, no gridlines, no axis labels.
- Lives on the homepage index tiles; never inside a basics-page panel.

**Tier 3 — Full chart (column-width 680px, or hero 1040px):**
- Full annotation treatment, full axis treatment.
- Title, deck, direct labels, source line.
- This is the only tier that carries editorial argument.

**Tier confusion is forbidden.** A "small chart in a basics-page panel" is
still a full chart and gets full chrome (Section 3 of
`basics-layer-template.md`). A "chart on a homepage tile" is a mini-chart
and gets the spec below, not a stripped-down version of a full chart and
not an inflated sparkline.

---

## 5.1 Mini-chart spec

**Role.** The mini-chart is the chart object that lives on a homepage
index tile (Section 6.1 below). It must, at glance, communicate one
shape — the trajectory of one series over the visible window — without
requiring the reader to study it. It is not a stripped-down basics-page
chart. It is a different artifact with its own rules.

**Reference lane.** The Economist's "Daily chart" thumbnail at homepage
scale; FT Markets Data tiles; NYT Upshot "Economy at a glance" mini
panels. These succeed because they treat the small chart as a designed
object, not as a shrunken big chart.

### Plot area and frame

- **Plot area target: 248 x 72 px.** This is the *plotting region*, not
  the full tile width. The tile is 280px wide (Section 6.1); the mini-chart
  reserves 16px of left padding for the optional final-value label and
  hangs the plot from there.
- **No background fill.** The mini-chart sits directly on `surface`
  (`#FFFFFF`) — the tile background. No card-within-a-card.
- **No border, no frame.** The x-axis rule below is the only frame
  element.

### Series

- **One series only.** Mini-charts never carry two series. If the section
  needs a second series to make sense, that signal belongs on the basics
  page, not the tile.
- **Line, not area.** 1.5px stroke. No fill below the line — fills on a
  mini-chart read as decoration at this scale.
- **Color tier:**
  - **Data-first sections** (Inflation, Policy, Labour, GDP) use
    `--series-1` (`#1F4E79`). These are the sections where the chart is
    the narrative on the tile.
  - **Ambient sections** (Markets, Trade, Housing) use `--ink-muted`
    (`#4A4F57`). These are sections where the editorial line and callout
    are the narrative and the chart is context. Drawn in slate, the
    mini-chart visually retreats so the words lead.
  - Assignment rationale: Inflation, Policy, Labour, and GDP are the four
    series where the *shape* of the line is itself the story (CPI
    approaching target, rate path, U-rate trajectory, GDP m/m wobble).
    Markets (USDCAD is a price-level walk), Trade (a noisy balance), and
    Housing (a slow HPI drift) are series where the latest *number* —
    not the shape — leads on the tile.

### Axes

- **X-axis:** 1px solid rule along the bottom of the plot area, in
  `--rule` (`#D9D3C7`). No tick marks. No date labels — the date is
  implicit from the tile's eyebrow "as of" stamp.
- **Y-axis:** No axis line. No gridlines. No tick labels.

### Final-value direct label (optional, recommended)

- A small label sitting to the right of the last-point dot, vertically
  aligned to it.
- Type: `mono-xs` (12px Plex Mono), weight 400, color `--ink`.
- Format: the latest value with units (`2.3%`, `1.378`, `-$2.3B`, `238k`).
- Hand-tuned position: 6px to the right of the dot. If the last point
  sits at the top of the plot area, allow the label to drop down 4px to
  avoid clipping the tile edge.
- Suppressed only when the value would collide with the tile's right
  edge or when the callout row directly below already carries the same
  number prominently. Default: shown.

### Reference rule (optional, max one)

- A single horizontal 1px dashed rule (`2 2` dash pattern), color
  `--ink-faint` (`#7A7F88`).
- Use only when the section has one well-known anchor value that gives
  the line meaning at a glance:
  - **Inflation:** 2.0% (BoC CPI target).
  - **Policy:** 2.75% (current BoC midpoint of neutral range — refreshes
    with the MPR).
  - All other sections: no reference rule (most series do not have a
    single canonical anchor; a rule would read as arbitrary).
- No label on the rule. The eye reads the offset; the page narrative
  carries the meaning.

### Recession band (optional)

- 1 optional recession band when the visible window covers a recession
  (rare on the homepage's typical 24-month window, but possible for
  longer-lookback tiles).
- Fill: `rgba(21,23,26,0.06)` per Section 3.
- Sits behind the line, in front of the x-axis rule.
- No label inside the band on a mini-chart — there is not enough room.

### Last-point dot

- 3px solid circle in the series color (matches the line).
- Always present. Marks "where we are now" without needing an axis label.

### What the mini-chart does NOT have

- No chart title (the tile eyebrow does the naming).
- No deck (the editorial line above does the framing).
- No gridlines, horizontal or vertical.
- No y-axis tick labels.
- No x-axis date labels.
- No annotations, no leader lines, no callouts inside the plot area.
- No legend (single series — no legend possible).
- No tooltip on hover. The mini-chart is read at glance; a tooltip would
  invite study, which belongs on the basics page.
- No source line under the chart. The tile carries no source attribution
  at this density — the section page does.

### Mobile variant

- At `sm` and `md` breakpoints the tile compresses to ~328px wide; the
  mini-chart plot area scales proportionally to ~296 x 72. Stroke,
  dot size, and label size stay constant — only the plot width changes.
- The reference rule and last-point label survive the compression.
- The recession band, if shown, may be clipped at the left edge — that
  is acceptable; the band is context, not a label.

---

## 5.2 Per-section mini-chart specs

One spec per homepage tile. Each names the canonical series, the optional
reference rule, the color tier, and any per-section nuance. Series keys
match `chartSeriesKey` in `src/data/sections.ts`.

### GDP — `gdp-mm`

- Series: Real GDP, m/m % change. 24 monthly points (2-year window).
- Color tier: **data-first**, `--series-1` (deep blue).
- Reference rule: **none.** Zero is implicit; the line wobbles around it.
- Last-point label: `+0.2%`.
- Note: this is a noisy series. The mini-chart reads as "wobble around
  zero with a recent soft tilt" — the editorial line above carries
  the verdict.

### Inflation — `cpi-yoy`

- Series: Headline CPI, y/y % change. 24 monthly points (2-year window).
- Color tier: **data-first**, `--series-1` (deep blue).
- Reference rule: **2.0%**, dashed, `--ink-faint`. The BoC target. This
  is the single most load-bearing reference rule on the homepage —
  reading the line approaching the target is the story of the entire
  section.
- Last-point label: `2.3%`.

### Labour — `unrate`

- Series: Unemployment rate, % of labour force. 24 monthly points.
- Color tier: **data-first**, `--series-1` (deep blue).
- Reference rule: **none.** Full-employment NAIRU is contested and
  drifting; a rule would mislead.
- Last-point label: `6.1%`.
- Note: y-axis range tuned to the visible window (typically ~5.0-6.5%)
  so the rise off the trough is legible. Do not anchor to zero.

### Housing — `hpi-yoy`

- Series: MLS HPI, y/y % change. 24 monthly points.
- Color tier: **ambient**, `--ink-muted` (slate).
- Reference rule: **none.** Zero is implicit; the line crosses through
  it and the crossing reads at a glance.
- Last-point label: `-1.4%`.
- Note: the line crosses zero in the visible window. Style the line as
  a single continuous slate stroke — do not split it into pos/neg
  segments. The crossing point is the visual event.

### Policy — `policy-rate`

- Series: BoC overnight rate, %. 24 monthly points (steps + holds).
- Color tier: **data-first**, `--series-1` (deep blue).
- Reference rule: **2.75% neutral midpoint**, dashed, `--ink-faint`. The
  current BoC neutral-range midpoint per April 2026 MPR. Refresh the
  rule value whenever the MPR refreshes the neutral range.
- Last-point label: `2.75%`.
- Note: this series is a staircase, not a smooth curve. Render as a
  step-after line (changes happen on the meeting date, not between).

### Markets — `usdcad`

- Series: USDCAD spot, daily close. ~24 weekly points (sampled weekly
  Fridays) over the 24-week window.
- Color tier: **ambient**, `--ink-muted` (slate).
- Reference rule: **none.** FX has no canonical anchor; rules would be
  editorial-controversial.
- Last-point label: `1.378`.
- Note: sampling is weekly, not daily, to keep the line readable at
  248px width. Daily data is preserved for the basics page.

### Trade — `trade-balance`

- Series: Merchandise trade balance, $B. 24 monthly points.
- Color tier: **ambient**, `--ink-muted` (slate).
- Reference rule: **none.** Zero is implicit; the line crosses it.
- Last-point label: `-$2.3B`.
- Note: like Housing, the line crosses zero in the visible window. Same
  rule: continuous slate stroke, no segmenting.

---

## 6. Component visual language

### 6.1 Index tile (homepage section tile)

**Role.** The index tile is the homepage's primary unit of section
representation. Seven tiles, one per section, arranged in the homepage
grid. Each tile must, at glance, answer: which section, what is the
latest reading, what shape is the trajectory, what changed.

The index tile is **not** a basics-page panel and **not** a card. It is
its own object with its own anatomy. Confusing the tile with the panel
is a category error — the panel sits on a section page and carries
editorial weight; the tile sits on the homepage and earns the click.

**Reference lane.** FT homepage section tiles; NYT homepage "Section"
strips; Economist daily-chart tile arrangement. The discipline: each
tile is a self-contained piece of evidence, not a teaser graphic.

### Dimensions

- **Width target: 280px.** Tight enough that seven fit in a homepage
  grid at desktop without scrolling; wide enough to host a 248px
  mini-chart plot area with 16px of breathing room on either side.
- **Height target: 190-210px.** Variable within this range based on
  whether the editorial line wraps to one or two lines. The mini-chart
  and the callout row are fixed; the editorial line absorbs the height
  variance.

### Anatomy (top to bottom)

```
[ EYEBROW ROW                                       ]   label + date
[ Editorial line, 2 lines max, ~12-16 words         ]   body-sm 500
[                                                   ]
[ Mini-chart (248x72 plot area, per Section 5.1)    ]
[                                                   ]
[ Value     delta     surprise verb                 ]   callout row
[ ------------------------------------------------- ]   1px rule (top)
```

The 1px rule sits at the **top** of the tile, in `--rule`. It separates
one tile from the one above it in a stacked layout and from the homepage
strip above the tile grid. No bottom rule, no side rules.

### Eyebrow row

- **Two elements, single line, justified left and right.**
- **Left:** Section name. `label` size (13px Inter, weight 500),
  all-caps, letter-spacing `0.08em`, color `--ink-muted`. e.g.,
  `INFLATION`.
- **Right:** As-of date stamp. `micro` size (12px Inter, weight 400),
  tabular figures, color `--ink-faint`. Format: `Apr 2026` or
  `May 9, 2026` depending on cadence. No leading `AS OF` word — that
  ritual belongs on the section page.
- **Spacing:** The eyebrow row sits `s-4` (16px) below the tile's top
  rule.

### Editorial line

- Owned by `writer`; visual treatment owned here.
- Type: `body-sm` (15px Inter, weight 500), color `--ink`.
- 2 lines maximum at the 280px tile width. Aim for ~12-16 words.
- Sits `s-3` (12px) below the eyebrow row.
- Line height tight (1.40) — the line must read as a single editorial
  sentence, not as flowed body copy.
- Wrap discipline: the writer must be able to predict where the line
  breaks. Tile width is fixed; the type is set in a single weight; the
  writer can count.

### Mini-chart

- Per the spec in Section 5.1 above. 248 x 72 plot area, centered in
  the tile with 16px horizontal padding.
- Sits `s-4` (16px) below the editorial line.
- The mini-chart bottom (x-axis rule) sits `s-3` (12px) above the
  callout row.

### Callout row

A single line carrying the three numbers that summarize the tile's
state. Three elements, left-aligned, separated by `s-3` (12px):

- **Value.** The headline number. `display-sm` (23px Inter, weight 600,
  tabular). Color `--ink`. e.g., `2.3%`, `1.378`, `-$2.3B`. Units stay
  with the number.
- **Delta.** Change vs. prior period. `mono-xs` (12px Plex Mono,
  weight 400). Color matches direction: `--pos`, `--neg`, or
  `--neutral`. Format `+0.1 pp`, `-25 bps`, `+0.4% w/w`. Aligned to
  the baseline of the value, not its cap.
- **Surprise verb.** A single-word direction tag from `writer`'s
  vocabulary: e.g., `beat`, `missed`, `held`, `cut`, `cooled`, `eased`,
  `widened`. `label` size (13px Inter, weight 500), all-caps,
  letter-spacing `0.08em`. Color matches direction (`--pos`, `--neg`,
  `--neutral`). Baseline-aligned with the delta.

The callout row is a single line. It does not wrap. If the verb would
push the row to wrap at the tile width, the writer picks a shorter
verb or drops the verb entirely (the delta carries the direction).

### Color and tone

The index tile inherits the design system's restraint:
- Tile background: `--surface` (`#FFFFFF`).
- No shadows, no gradients, no rounded-corner pillows beyond the global
  4px radius.
- Section accent (per Section 1 of `basics-layer-template.md`) does
  **not** color the tile background or any frame element. The section
  identity on the homepage is carried by the eyebrow label only.
- The mini-chart's series color (data-first blue or ambient slate)
  carries the chart-visual identity; the tile's own chrome stays
  monochrome.

### Explicitly NOT on the index tile

These elements belong on the basics-page panel (`basics-layer-template.md`,
Sections 1, 3, 6, 7, 8) and must not bleed onto the homepage tile:

- **Panel eyebrow code** (e.g., `01`, `02`, `03`). The numbered panel
  index is a basics-page wayfinding device. The homepage uses the
  section name, not a number.
- **Italic deck / standfirst.** The homepage tile carries an editorial
  line in sans, not a serif italic deck. Decks belong on basics pages
  where the reader has committed to read.
- **`AS OF` stamp on its own line.** The homepage compresses freshness
  into the eyebrow row date. The full `AS OF <indicator> <date>
  (released <date>)` ritual belongs on the basics page.
- **Revision tag.** Revisions are basics-page typographic events
  (Section 5 of `basics-layer-template.md`). On the tile, a revision
  is invisible — only the latest value shows.
- **Methodology link.** Methodology affordance lives on the basics-page
  panel (Section 7). The tile is too dense to host a `Methodology`
  link without it reading as chartjunk.
- **Source line.** Source attribution lives on the basics-page panel
  (Section 8) where the reader has committed. The homepage tile does
  not carry `Source: Statistics Canada` — the section-page click does.
- **Serif display headline.** The tile uses `body-sm` Inter for its
  editorial line. Serif display is reserved for the page hero
  (`display-xl`) and section openers (`display-lg`/`display-md`).
  A tile-sized serif headline would compete with the page hero and
  weaken both.

If any of these elements feel necessary on a homepage tile, the answer
is almost always: the section page is where they live, and the tile's
job is to earn the click that gets the reader there.

---

### Cards

- Background `surface` (`#FFFFFF`).
- 1px border in `rule` (`#D9D3C7`) — not a shadow, never a shadow.
- Border radius: 4px. Crisp, not pillowy.
- Padding: `s-5` (24px) default, `s-6` (32px) for hero cards.
- Title at top: `display-sm` (23px serif).
- Optional kicker eyebrow above title: `label` all-caps, `accent` color,
  letter-spacing 0.08em.

### Callouts / pull quotes

- Background `surface-sunk` (`#F4F0E8`).
- 4px left rule in `accent` (editorial red).
- Padding `s-5` (24px) all sides.
- Type: `body-lg` (19px sans) for the quote, `label` for the attribution.
- No quote marks rendered as glyphs — typography carries it.

### Tables

- Header row: `label` size, `ink-muted`, weight 500, all caps,
  letter-spacing 0.04em. 1px bottom rule in `ink-muted`.
- Body rows: `body-sm` for text columns, `mono-sm` for numeric columns.
- Numeric columns right-aligned. Text columns left-aligned. Mixed never.
- Row dividers: `rule-faint` (`#ECE7DC`), 1px. Or no dividers if rows are
  short and `s-3` (12px) vertical padding gives enough rhythm.
- No zebra striping. Period.
- Hover row: background `surface-sunk` (subtle). Optional, not required.
- Sortable column indicator: a `mono-xs` arrow glyph (`^` / `v`) in
  `ink-faint`, never a colored icon.

### Blurbs / standfirst

- Below page hero headline.
- Type: `deck` (19px serif italic, weight 400, `ink-muted`).
- Max-width matches body column (680px).
- One paragraph, 2-4 sentences. If longer, it is body prose, not a deck.

### Citations and footnotes

- Inline citation marker: superscript number in `micro` size, `accent`
  color, no brackets. E.g., `(per Statistics Canada<sup>3</sup>)`.
- Footnote block at bottom of article:
  - Heading: `label` all-caps `Notes` or `Sources`.
  - Items: `body-sm`, hanging indent so the number aligns with body,
    text indents past it.
  - `ink-muted` color, but linked terms in `ink`.
- Source line under charts: `micro` `ink-faint`, prefix `Source:` followed
  by the citation. No clickable underline inside the chart frame — the
  source line links via the surrounding caption.

### Buttons (UI, sparingly used)

- Primary: `ink` background, `paper` text, 4px radius, padding `s-3 s-5`.
  Hover: lighten to `ink-muted`.
- Secondary: transparent, 1px `ink` border, `ink` text.
- Tertiary / link: underlined inline link in `ink` with `accent` underline
  color (1px offset 2px). Hover: full underline becomes `accent` text.
- Never gradients. Never shadows. Never icon-only buttons without an
  accessible label.

### Form inputs (when needed)

- 1px `rule` border, `surface` background, `body-sm` Inter, 4px radius.
- Focus: 2px `ink` border, no glow.

---

## 7. Iconography

**Stance: text-first. Icons are exceptions, not a system.**

We are an editorial site. Most navigation, status, and meaning should be
carried by typography and layout, not by a glyph. When we do use an icon,
it is functional, monochrome, and from a single restrained set.

### When we use icons

- **External link indicator** next to outbound links. Small arrow-NE glyph.
- **Expand/collapse** on disclosure components.
- **Sort direction** in tables (the `^` / `v` mentioned above — these are
  type, not icons, which is the point).
- **Share / copy-link** affordances on charts (if requested by editorial).

### When we do not use icons

- No icons in navigation labels. The label is the label.
- No icons in card headers as decoration.
- No "info" `(i)` icons on every chart — if the chart needs explaining, it
  needs a deck, not a tooltip.
- No emoji anywhere in shipped UI.

### Set

**Lucide** (`lucide-icons`), at 16px or 20px, stroke-width 1.5, color
`ink-muted` default, `ink` on hover. Lucide is open, complete, and visually
neutral — it does not impose a brand of its own. Frontend-designer should
import only the specific glyphs used, not the whole set.

---

## 8. Motion and interaction

**Stance: restrained. Motion serves comprehension, never decoration.**

### What we animate

- **Tooltip / annotation reveals on chart hover:** 120ms ease-out fade.
  Tooltip background `surface`, 1px `rule` border, no shadow, `body-sm`
  inside.
- **Disclosure expand/collapse:** 200ms ease-in-out height transition.
- **Page navigation focus rings:** instant (no animation on focus).
- **Link underline thickness on hover:** 100ms color/thickness transition.

### What we never animate

- **Entrance animations on page load.** No fade-up paragraphs, no
  staggered card reveals. The page renders and is there.
- **Number tickers / count-up.** A number is a number. Animating it
  pretends to a discovery moment the reader is not having.
- **Scroll-triggered chart redraws** as the primary interaction. We may
  do a scrollytelling piece occasionally, but it is a deliberate format
  choice, not the default.
- **Hover effects on non-interactive elements.** If it does not do
  something on click, it does not respond on hover.
- **Parallax. Ever.**

### Reduced motion

Respect `prefers-reduced-motion: reduce`. Under reduced motion:
- Disclosure becomes instant.
- Tooltip fade becomes instant.
- Any future scrollytelling pieces fall back to a stacked, all-revealed
  layout.

### Interaction model for charts

- **Default state shows the story.** A chart at rest must communicate its
  point without any hover. Hover is for precise values, not for the
  takeaway.
- **Tooltips give precision, not narrative.** Tooltip content: date, value,
  unit. That is it. The narrative lives in the title, deck, and
  annotations.
- **Mobile: tap to read tooltip, tap-elsewhere to dismiss.** No
  hover-equivalent hacks.
- **No crosshair lines across the full chart on hover** unless the chart
  is a multi-series time-series where comparing values at a date is the
  point. Default: dot + tooltip only.

---

## Appendix A — Token summary (for implementation)

```
/* Colors */
--paper:        #FBF8F2;
--surface:      #FFFFFF;
--surface-sunk: #F4F0E8;
--ink:          #15171A;
--ink-muted:    #4A4F57;
--ink-faint:    #7A7F88;
--rule:         #D9D3C7;
--rule-faint:   #ECE7DC;

--accent:       #A6192E;
--accent-soft:  #F1D9DC;

--pos:          #1F6B3A;
--pos-soft:     #D4E5D8;
--neg:          #B23A2F;
--neg-soft:     #EAD3CE;
--neutral:      #5A6470;
--neutral-soft: #DDE0E4;

--series-1:     #1F4E79;
--series-2:     #C9772A;
--series-3:     #5B7553;
--series-4:     #7A3E65;
--series-5:     #3F7D7C;
--series-6:     #8A6A2C;
--series-7:     #4A4F57;

/* Spacing */
--s-1: 4px;  --s-2: 8px;  --s-3: 12px; --s-4: 16px;
--s-5: 24px; --s-6: 32px; --s-7: 48px; --s-8: 72px; --s-9: 112px;

/* Type families */
--font-serif: "Source Serif 4", "Source Serif Pro", Georgia, "Times New Roman", serif;
--font-sans:  "Inter", "Inter var", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
--font-mono:  "IBM Plex Mono", "JetBrains Mono", "Consolas", "Menlo", monospace;

/* Layout */
--col-body:  680px;
--col-wide:  1040px;
--col-page:  1200px;
```

---

## Appendix B — Open questions / to revisit

- Print stylesheet — defer to v1.1. If we get a "print this page" request
  from readers, design then.
- Dark mode — deferred, see section 3.
- Brand mark / logo — out of scope for v1 visual identity. If editorial
  requests one, art-director will design separately.
- Data table sort/filter UX — defer to first table that actually needs it.
- Localization (FR) — Canadian context, likely needed eventually. Type
  scale and spacing should accommodate French (~20% longer copy on
  average). Body column 680px is generous enough; chart labels will need
  per-chart review.
