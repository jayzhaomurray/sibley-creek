# Homepage Hero Chart — Per-Chart Visual Spec

Status: v0.1. Author: art-director.
Last updated: 2026-05-11.

This document is the visual spec for the **homepage hero chart** in Layout B.
It is a *compressed* hero: the canvas is small (~280x140 CSS px) but the
chart must still read as a hero — title, deck, value callout, direct labels,
recession context, source line — all legible at a glance.

Cites `design/design-system.md` (canon) and `design/basics-layer-template.md`
(the per-section panel template). Where this doc proposes a new token or
treatment, it is flagged `[TOKEN PROPOSAL]` for review.

Inheritance:
- All chart-aesthetic rules in design-system.md Section 5 apply UNLESS this
  doc explicitly overrides them for the compressed size.
- Treatments that the basics-layer panels enjoy (annotation typography,
  vintage stamps, methodology drawer) do **not** all survive at 280x140;
  Section 10 below is honest about what gets cut.

---

## 0. What the homepage hero is

Per Layout B: a single hero section auto-selects based on the most-recently-
updated data slice (Inflation, Labour, Policy, GDP, Housing, Trade, or
Markets). The hero tile holds:

- A serif title and italic deck (writer's wording, art-director's typography)
- A big-number callout (the latest print)
- A small chart, **~280x140 CSS px**, of the load-bearing time series
- A source line and a single-line provenance / vintage strip

The hero tile is the page's first visual event. The chart inside it is a
*visual proof* of the headline, not the headline itself. Title and number
do the editorial work; the chart shows the reader "yes, that is the shape
of it."

Reference lane for the *tile* (not the chart): FT homepage above-the-fold
lead chart panels (small, headline + chart + one number, almost a
broadsheet teaser block); NYT Upshot's morning-newsletter lead-chart blocks.

---

## 1. Dimensions

### Confirmed canvas: 280 x 140 CSS px

Frontend-designer reserved 280x140. This is a 2:1 aspect (wider than the
16:9 we use for time-series in basics-layer panels, which at 432px would be
432x243). The squatter aspect is the right call for a homepage hero strip
where vertical real estate is precious — but it means the chart must not
crowd vertical labels.

I confirm 280x140 as the *target* canvas dimensions, with two caveats:

1. **Plot area is smaller than canvas.** Inside the 280x140 box, reserve:
   - Left gutter: 32px for y-axis tick labels (`micro` size).
   - Right gutter: 44px for the direct label at the line terminus.
   - Top: 8px (no in-canvas title — title lives in the tile chrome above).
   - Bottom: 18px for the x-axis rule + tick labels.

   Net plot area: **~204 x 114 CSS px.** That is the working drawing space.

2. **DPR-aware rendering.** Render at 2x device pixels (560x280 backing
   store) so lines do not soften on retina. Chart-builder owns this.

### Responsive behavior

- **xl / 2xl (>=1200px):** Canvas at 280x140. Plot area as above.
- **lg (960-1199px):** Canvas at 280x140. Same.
- **md (640-959px):** Hero tile reflows; chart canvas grows to **360x160**.
  Plot area: ~284x134. One additional y-tick may appear.
- **sm (<640px):** Hero tile becomes full-width; chart canvas at
  **(viewport - 32px gutters) x 180**. The chart goes from compressed-hero
  to "small full chart" — closer to basics-layer-panel chrome. Add: 4 y-
  ticks instead of 3; a second annotation may render; direct label uses
  the section's section-accent token if applicable.

`[TOKEN PROPOSAL]` Hero canvas size tokens (added to system Appendix A):

```
--hero-chart-w-desktop: 280px;
--hero-chart-h-desktop: 140px;
--hero-chart-w-tablet:  360px;
--hero-chart-h-tablet:  160px;
--hero-chart-h-mobile:  180px;  /* width follows container */
```

### Why not 16:9

A 280x158 (16:9) version would give the line more vertical drama but eat
18px from the headline tile. The hero tile is a horizontal teaser block;
2:1 keeps the chart visually subordinate to the headline+number stack
above it, which is correct. A 16:9 hero chart would compete with the
headline. We want it to support the headline.

---

## 2. Title and deck

### Where title and deck live

**Outside the 280x140 canvas, above it, in the hero tile chrome.** The
chart canvas itself contains no title. This is different from basics-
layer panels (where the panel title is the chart title). It is the right
call here because:

- 140px of vertical space is too little to host both a serif title and a
  data shape.
- The hero tile is a *composition* — headline + number + chart — and the
  chart is one of three peers, not a wrapper.

### Title typography

- Family / size / weight: `display-md` (28px) Source Serif, weight 600,
  color `ink`. (Per design-system.md, `display-md` is "Chart title (hero
  charts only)" — this is exactly that case.)
- Line-height: 1.20.
- Max width: matches hero tile content width (typically ~520px on
  desktop). Wraps to two lines maximum.
- **Max characters: ~62 for one line, ~120 across two lines.** Writer
  must hit that budget. Anything longer pushes the chart below the fold
  or compresses it.

### Deck typography

- Family / size / weight: `deck` (19px) Source Serif italic, weight 400,
  color `ink-muted`.
- Line-height: 1.45.
- **Max characters: ~150 (one short paragraph, ~2 lines).** Writer's
  wording, art-director's typesetting.
- Vertical spacing: `s-3` (12px) below the title. `s-4` (16px) below the
  deck before the callout-and-chart row begins.

### Why title is serif at this size

`display-md` (28px serif) above a 280x140 sans/data chart creates the
"set, not assembled" feel of the design-system Section 1 vow. A sans
title would make the tile read as a UI card. Serif title makes it read
as a feature.

---

## 3. Big-number callout treatment

### Placement: top-left of the chart row, not over the chart

The callout sits **to the left of the chart canvas**, not above it or
inside it. The hero tile interior layout reads:

```
+-------- hero tile interior (max ~860px wide) --------+
| [section eyebrow]                       [vintage]    |
|                                                      |
| HEADLINE (display-md serif, 28px, up to two lines)   |
| Deck (deck, 19px serif italic, ink-muted, ~2 lines)  |
|                                                      |
| +------ callout col -----+  +---- chart 280x140 ---+ |
| | 2.4%                   |  |                      | |
| | year-over-year, Apr 26 |  |  [hero chart canvas] | |
| | ^ +0.1pp vs Mar        |  |                      | |
| | Beat consensus 0.1pp[c]|  |                      | |
| +------------------------+  +----------------------+ |
|                                                      |
| Source: ...               Methodology >              |
+------------------------------------------------------+
```

The callout column is ~200px wide. The chart sits to its right, separated
by `s-5` (24px). On `md` breakpoint the callout stacks above the chart;
on `sm` the callout stacks above the chart with reduced spacing.

### Why left, not above

Two reasons:

1. **Reading order.** The reader's eye drops from the headline to the
   big number (the answer), then sweeps right across the chart (the
   evidence). Right-then-down works because English reads L-to-R.
2. **Vertical economy.** Putting the callout above the chart would push
   the chart canvas down by ~80px. We do not have those pixels above the
   fold.

### Callout typography (reuses basics-layer-template Section 3 atoms)

Identical to basics-layer panel callout, with one tweak: this is the
homepage hero, so the **big number is `display-md` (28px)** — same size
as in basics panels. It does not get bigger. The size hierarchy is
held by the headline above (which is `display-md` too), not by inflating
the callout number.

- **Big number.** `display-md` (28px) serif, weight 600, tabular figures,
  `ink`. Example: `2.4%`.
- **Unit / period label.** `body-sm` (15px) Inter, `ink-muted`,
  immediately below the big number. Example:
  `year-over-year, April 2026`.
- **Direction + surprise row.** `label` (13px) Inter, weight 500.
  - Direction arrow glyph in `pos`/`neg`/`neutral` (Lucide `arrow-up` /
    `arrow-down` / `minus` at 14px).
  - Delta vs prior, in direction color, tabular figures.
  - Pipe glyph in `ink-faint`.
  - Surprise verb + magnitude + subscript anchor (`[c]` consensus or
    `[m]` MPR fallback), per basics-layer-template Section 4.

Vertical stack tight: `s-1` (4px) between big number and unit, `s-2`
(8px) between unit and direction row.

### Units in label size

Units never share weight/size with the big number. Always one size step
down (`body-sm`) and one weight step down (400 italic-free) and in
`ink-muted`. The number is the headline; the unit is the apostille.

---

## 4. Axis treatment at this size

The plot area is ~204x114. Most axis chrome from the design-system
Section 5 still applies, but at compressed densities:

### Y-axis

- **No axis line** (consistent with canon).
- **Tick labels: 3 only.** Min, midpoint, max — chosen by chart-builder
  to round to "nice" numbers (5s, 0.5s). Not 4-6 as in basics-layer
  panels. Three is the minimum that conveys range without crowding.
- **Tick label typography:** `micro` (12px) Inter, `ink-faint`. Tabular.
- **Tick label position:** Right-aligned, sitting in the 32px left
  gutter, 4px from the plot area's left edge.
- **Topmost tick carries the unit.** Per design-system.md Section 5,
  Axes rule: the topmost y-tick gets the unit appended in `micro`
  `ink-faint`. Example: `4%`. The other ticks are bare numbers (`2`,
  `0`).
- **Zero line.** If the series includes negatives or hovers near zero,
  draw the zero line at 1px `ink-muted` (canon). Otherwise omit.

### X-axis

- **One 1px rule** in `rule` color along the bottom of the plot area.
- **Tick marks: 4 max, outward, 3px** (one less than canon's 4px — at
  this size 4px reads as a hairline cilium).
- **Tick labels: 3-4 only,** year-only where the series spans >=3
  years, year-quarter where shorter. `micro` (12px) Inter `ink-faint`.
- **No minor ticks.**

### Gridlines

- **Horizontal only,** consistent with canon.
- **Color: `rule-faint` (#ECE7DC).**
- **Count: 2-3,** matching the y-tick count minus one. At small size,
  even gridlines verge on noise; we keep them because the eye needs an
  anchor for the y-position of the latest point, but we use the minimum
  needed.
- **Zero-line override:** if drawn, `ink-muted` not `rule-faint`.

### Axis title

Never. The unit on the topmost y-tick covers it.

---

## 5. Direct labels vs legend

### Rule: one direct label, no legend, ever, at this size

The hero chart shows **one series** by default — the load-bearing time
series for the hero section (CPI YoY, unemployment rate, BoC overnight,
GDP m/m, MLS HPI YoY, trade balance 3M MA, USDCAD). With one series,
a legend would be absurd. Direct-label the line at its right terminus.

### Direct label specification

- **Position:** Right end of the line, in the 44px right gutter.
- **Typography:** `label` (13px) Inter, weight 500, color = series
  color (`series-1` deep blue by default, or the section-accent if
  applicable — see Section 9 chart-type matrix).
- **Anchor:** The label's baseline sits at the y-pixel of the final
  data point. If the label would clip the canvas top/bottom, nudge by
  up to 8px and add a 1px leader line in `ink-muted` from label to
  point.
- **Wording:** One token. `CPI YoY`, `Unemployment`, `Overnight rate`,
  `GDP m/m`, `HPI YoY`, `Trade balance`, `USDCAD`. Writer can refine,
  but it must fit in 44px (~7-8 characters at `label` size).

### Why not a legend

A 280x140 canvas literally cannot afford a legend without losing 12-15%
of plot area. Direct labels are also the design-system canon (Section 1:
"direct labels over legends"). The canvas size doesn't change the
principle — it enforces it.

### What if writer / EDR wants a second series?

Push back. At this size a second series compromises every other element.
If a comparison is editorially load-bearing (e.g., CPI vs core CPI),
move the comparison to the section's basics-layer page and use this
hero chart for the single-series headline. The hero is a *teaser*, not
a comprehensive view.

If the second series is truly mandatory, the fallback is:
- Series 1 in `series-1` (deep blue) or section-accent.
- Series 2 in `series-7` (slate), 1px not 1.5px, no direct label —
  reads as context.
- This costs the recession bands or the consensus marker — one of those
  has to go. Default sacrifice: recession bands. (We do not lose
  consensus, because consensus is the editorial point of the hero.)

---

## 6. Recession shading

### Rule: keep the 6% ink opacity, drop the label

Design-system.md Section 5 specifies recession bands at `ink` 6% opacity
sitting behind gridlines and data. We hold the opacity rule exactly.

At 280x140, **we do not label recession bands.** The basics-layer rule
of labeling only the most recent recession does not survive here —
there isn't room. The band reads as a tint and the reader who recognizes
it will pattern-match; the reader who doesn't will not be misled.

Treatment:
- Band fill: `rgba(21,23,26,0.06)`.
- Band borders: none. The fill is the band.
- Render order: under gridlines, under data line, under markers.
- Coverage: only recessions whose endpoint falls within the chart's
  x-range. Bands that span off the left edge are clipped to the plot
  area (no faded edge).

### Why we keep them at all

Recessions are the highest-information context a macro time-series can
carry. They tell the reader "this dip is not an oopsie, this is 2008."
Removing them to save 6% of the visual budget would be a false economy.
We keep the tint, we drop the label.

### Exception: tooltip

On hover over a recession band, the tooltip (Section 7) gains a one-line
band identifier: `Recession: 2008Q4-2009Q2 (CD Howe BCC)`. Wording is
writer's. This is how the label survives — as hover content, not as
ink on the canvas.

---

## 7. Hover / tooltip behavior

### Decision: tooltips ON, but minimal

Design-system.md Section 8 says: "Default state shows the story. Hover
is for precise values, not for the takeaway. Tooltips give precision,
not narrative."

For the homepage hero, tooltips are appropriate because:
- The hero is interactive territory — readers expect to be able to
  probe a chart that's prominent on the page.
- The default visual already carries the story (title, callout, recent
  point marker). Hover adds *precision* on dates earlier than the latest
  print.

### Specification

- **Trigger:** mouse hover (desktop) or tap (touch). Tap-elsewhere
  dismisses.
- **Marker on trigger:** a 4px filled circle in the series color
  appears at the nearest data point. No crosshair.
- **Tooltip box:** floats just above-right of the marker, 12px offset.
  - Background: `surface` (#FFFFFF).
  - 1px `rule` border.
  - 4px radius (consistent with cards).
  - Padding: `s-3` (12px) all sides.
  - No shadow.
- **Tooltip content (three lines, tight):**
  - Line 1: Date in `body-sm` Inter weight 500 `ink`. Format
    `Apr 2026` for monthly, `2026Q1` for quarterly.
  - Line 2: Value in `display-sm` (23px) Inter weight 600, tabular,
    `ink`. Example: `2.4%`.
  - Line 3 (optional, only on recession-band hover): one-line band
    identifier in `micro` `ink-faint`.
- **Reveal animation:** 120ms ease-out fade-in (canon). Under
  `prefers-reduced-motion`, instant.

### What tooltips do NOT contain

- No "vs prior" delta. The callout shows the most recent delta; the
  reader is hovering for precision on a *different* point, not for
  narrative.
- No consensus comparison. Consensus only applies to the latest print,
  which is visible by default (Section 8).
- No source citation. Source line is the source line's job.

### Mobile

Tap reveals the tooltip; tap elsewhere dismisses. Same content as
desktop. No drag-scrub. The hero chart is not a scrubbing chart.

---

## 8. Consensus / surprise marker — the latest print vs expectation

This is the most-load-bearing element of the hero chart and deserves
careful treatment. Per basics-layer-template Section 4 and the
2026-05-10 EDR override: consensus-first (Bloomberg/Reuters median),
BoC MPR fallback. The hero chart must surface (a) what the latest
print is, (b) where consensus expected it to land, (c) which anchor
was used.

### The tension at 280x140

In a basics-layer panel (chart canvas ~432px wide) we have room for the
print-vs-consensus comparison both inside the chart (as a marker pair)
and in the callout (as text). At 280x140, doing both is overkill and
the inside-chart marker pair fights with the recession band and the
data line.

### Decision: consensus tick inside the chart, surprise text in the callout

The chart canvas carries a **single visual element** for consensus: a
small open tick at the consensus-expected value, anchored to the
x-position of the latest print. The callout (which lives outside the
canvas, see Section 3) carries the verbal surprise statement and the
anchor subscript.

### Visual specification — consensus tick

The latest data point is a **filled circle**, 5px diameter, in the
series color, sitting on the line.

Adjacent to it, at the same x-position but at the y-pixel of the
consensus value, sits a **consensus tick**: a 1px horizontal dash, 12px
wide, centered on the x-axis position of the print, color `ink-muted`,
stroke 1px solid. **No fill, no circle around it** — it is a *line of
expectation*, not another data point.

A connecting 1px vertical line in `ink-faint`, dashed `2 2`, joins the
consensus tick to the latest-print filled circle. This is the "where
consensus was, where the print landed" visual hop, analogous to the
revision-marker hop in basics-layer-template Section 5.

```
                  o   <- consensus tick (1px dash, 12px wide, ink-muted)
                  :
                  :   <- 1px dashed ink-faint connector
                  :
                  *   <- latest print (5px filled, series color)
```

When the print is *above* consensus (a beat on growth, a miss on
inflation depending on writer's framing), the print sits above the
tick. When *below*, the print sits below. The hop length is the visual
magnitude of the surprise.

### Why this and not a "consensus envelope" or candlestick

Two alternatives considered and rejected:

1. **Consensus envelope** (gray band showing forecaster range across
   the trailing N quarters). At 280x140, the envelope crushes the
   recession band into invisibility and reads as a chart-of-its-own.
2. **Candlestick or error-bar marker** on the latest point. Too
   financialized. Reads as "trading dashboard," not editorial. Violates
   the design-system Section 1 stance.

The tick + dashed connector is the lightest mark that carries the
information. It is visually quiet enough to coexist with the recession
bands; it is unmistakable enough that the eye finds it.

### Surprise text in the callout

The callout's third row (per Section 3) carries the full surprise verb:

```
^ +0.1pp vs Mar | Beat consensus by 0.1pp[c]
```

Same format as basics-layer-template Section 4. The `[c]` subscript
hovers to reveal the consensus provenance tooltip.

### When the consensus mark would mislead

For sections where consensus is unavailable or inappropriate:

- **GDP monthly m/m:** consensus available — render mark.
- **Inflation headline CPI YoY:** consensus available — render mark.
- **Unemployment rate:** consensus available — render mark.
- **BoC overnight rate:** the rate is a decision, not a forecast outcome.
  We render an `[m]` mark for the MPR-implied path if EDR wants it; by
  default, NO mark at all on a policy-rate hero chart. The rate is the
  rate; the surprise is whether the decision matched OIS-implied
  pricing, which is a different chart.
- **GDP quarterly Q/Q SAAR:** consensus available — render mark.
- **MLS HPI YoY:** consensus rarely surveyed publicly. **Default: no
  mark.** If we develop an in-house consensus, revisit.
- **Trade balance 3M MA:** consensus available on monthly trade
  release — render mark on the latest underlying month, not on the 3M
  MA endpoint (which is a derived value).
- **USDCAD:** there is no "consensus" for a real-time FX rate. **No
  mark.** This hero chart is a level/trend display, not a surprise
  display.

When no mark renders, the callout's third row shows only the delta vs
prior, no pipe, no surprise verb. The convention is consistent with
basics-layer-template Section 4 ("when there is no surprise to show").

### When MPR fallback is used

The MPR fallback only applies in practice to inflation and GDP-quarterly,
when consensus is genuinely unavailable for that release. The visual
treatment is identical (tick + dashed connector). The subscript becomes
`[m]` and the tooltip discloses the MPR vintage.

---

## 9. Per-section chart-type matrix

What chart shape fits each hero, at 280x140.

| Section   | Series                  | Chart type           | Notes                                                                 |
|-----------|-------------------------|----------------------|-----------------------------------------------------------------------|
| Inflation | Headline CPI YoY        | Line                 | 5-year window. Direct label `CPI YoY`. Consensus tick. BoC 2% band.   |
| Labour    | Unemployment rate       | Line                 | 8-year window. Direct label `Unemployment`. Consensus tick.           |
| Policy    | BoC overnight rate      | **Step function**    | 8-year window. Right-angle steps. No consensus tick. Direct label.    |
| GDP       | Monthly real GDP m/m    | **Bars (thin cols)** | 3-year window. Bars in series color. Consensus tick on last bar.      |
| Housing   | MLS HPI YoY             | Line                 | 5-year window. Direct label `HPI YoY`. No consensus tick (no feed).   |
| Trade     | Trade balance 3M MA     | Line with zero band  | 5-year window. Zero line in `ink-muted`. Consensus tick on last m.    |
| Markets   | USDCAD                  | Line                 | 1-year window (rolling). Direct label `USDCAD`. No consensus tick.    |

### Specifics by section

**Inflation — CPI YoY line.**
A 5-year window is long enough to show the 2021-23 inflation episode and
the disinflation since. The BoC's 2% target may be drawn as a 1px solid
`ink-muted` horizontal reference line, labeled `2% target` in `micro`
`ink-faint` at right margin. Series color: section-accent (`series-2`
burnt orange) if the hero is the Inflation section; otherwise `series-1`.
Optional control-band: `+/-1pp` around 2% as `ink-muted` 4% opacity wash
— but only if the chart has room (test in implementation; if it crowds
the recession band, drop it).

**Labour — unemployment line.**
8-year window catches 2018 normalcy, 2020 spike, 2021-22 normalization,
and the 2024-26 trajectory. No "natural rate" reference line — the BoC
does not publish a hard u-star and a soft estimate would over-claim.
Series color: section-accent (`series-3` sage) if Labour is hero; else
`series-1`.

**Policy — BoC overnight step function.**
This is the one shape difference. The overnight rate moves in discrete
25bp (occasionally 50bp) steps; a smoothed line would lie about the
data. Render as a step function (right-angle corners, no interpolation
between meetings). No consensus tick (see Section 8). Optional event
ticks above the plot at decision dates for the most recent year only,
1px `ink-faint` dashed, height 6px. Direct label `Overnight rate`.
Series color: section-accent (`series-5` teal) if Policy is hero; else
`series-1`.

**GDP — monthly m/m bars.**
Bars (thin columns, ~4px wide with 1px gap) better convey the discrete
month-to-month nature of GDP than a line. 3-year window keeps each bar
visible (~36 bars). Recession bands behind. Latest bar carries the
filled-marker treatment differently: the bar itself becomes the marker,
and the consensus tick sits horizontally across the top of the consensus-
expected bar height with a dashed connector down to the actual bar top.
Direct label is omitted (there's no terminal point to label) — instead,
the y-axis topmost tick reads `% m/m` in `micro` `ink-faint`. Series
color: section-accent (`series-1` deep blue) since GDP's accent IS
series-1; alternatively, accept that GDP-as-hero is unusually
consonant with the default chart color.

**Housing — MLS HPI YoY line.**
5-year window. Direct label `HPI YoY`. No consensus tick (Section 8;
MLS HPI is not consensus-forecasted in any public feed we have access
to). Series color: section-accent (`series-4` plum) if Housing is hero;
else `series-1`. Zero line in `ink-muted` if the series goes negative
(YoY HPI did in 2023).

**Trade — trade balance 3M MA line with zero band.**
5-year window. Trade balance crosses zero frequently; the zero line is
load-bearing and rendered in `ink-muted` 1px solid. Fill between line
and zero in `pos-soft` (where line > 0) and `neg-soft` (where line < 0),
at 35% opacity — this is a deviation-from-zero shading that doubles as
visual signage. Direct label `Trade balance, 3M MA`. Consensus tick
applies to the latest *underlying month*, not the MA endpoint (be
explicit in the tooltip). Series color: section-accent (`series-7`
slate) if Trade is hero; else `series-1`. **Override:** if the slate
makes the fill-against-zero unreadable, use `series-1` for the line
even when Trade is hero, and let the section accent live in the
eyebrow only. (Slate + slate-tinted fills compete; this is the one
section where wayfinding-color has to yield to chart legibility.)

**Markets — USDCAD line.**
1-year rolling window (FX moves daily and a 5-year window crushes the
recent action). No consensus tick (Section 8 — there is no consensus
on a real-time FX print). No recession bands either — at 1y window
they would dominate inappropriately. Direct label `USDCAD`. Series
color: section-accent if Markets is its own section (per the EDR map,
Markets isn't currently in the 7-section list and may live under
Financial — confirm with editorial-director). If hero, use whichever
series-N is assigned; else `series-1`.

---

## 10. What the chart CAN NOT do at this size

Honesty discipline. The basics-layer-template gives a chart canvas
~432x243; the homepage hero gives ~204x114 of plot area. Things that
work at 432 do not all work at 204. Specifically:

### Cut entirely from the hero chart

- **Small multiples.** Out. If a hero section needs multiples (Inflation
  with core/headline/trim), they live on the section's basics page or
  in a deep dive. The hero is one series.
- **Second series.** Out by default; permitted only with sacrifice (see
  Section 5). Headline+core inflation is the most common reason to ask,
  and the answer is: hero shows headline, basics-layer panel shows the
  pair.
- **Stacked or layered shapes** (stacked area, contribution bars).
  Reserved for basics-layer panels with the room.
- **In-canvas annotations with leader lines and prose** (the
  design-system Section 5 hand-tuned annotation treatment). Out — there
  is no white space to place 12 words of prose at this canvas size.
  Annotation moves to the deck above the chart, where the writer
  controls the wording in serif italic.
- **Recession-band labels.** Out (Section 6).
- **Methodology link in the chart frame.** The link lives in the hero
  tile chrome below the source line (`Methodology >` right-aligned, per
  basics-layer-template Section 7). Not inside the chart canvas itself.
- **Vintage stamp inside the chart.** Lives in the hero tile chrome,
  upper-right of the tile (same position as the basics-layer panel
  vintage stamp). Not over the chart canvas.

### Compressed but retained

- **Recession bands** (tint only, no labels — Section 6).
- **Direct label** (one, right terminus — Section 5).
- **Consensus tick + dashed connector** (one only, on the latest point —
  Section 8).
- **Y-axis ticks** (three, with unit on the top — Section 4).
- **X-axis** (one rule, 3-4 ticks — Section 4).
- **Tooltips** (minimal precision-only — Section 7).
- **Latest-point filled marker** (5px circle in series color).

### Treatments that explicitly downgrade vs basics-layer panels

| Element                | Basics-layer panel       | Homepage hero (this spec)              |
|------------------------|--------------------------|-----------------------------------------|
| Y-tick count           | 4-6                      | 3                                       |
| X-tick count           | 5-8                      | 3-4                                     |
| Tick mark length       | 4px                      | 3px                                     |
| Series count           | up to 5                  | 1 (2 only with explicit sacrifice)      |
| In-canvas annotation   | yes, hand-tuned          | none; moved to deck                     |
| Recession label        | most recent labeled      | none (tooltip discloses)                |
| Direct labels          | each series at terminus  | one, at terminus                        |
| Latest-print marker    | 4-5px filled circle      | 5px filled circle (same)                |
| Consensus indicator    | tick + dashed + callout  | tick + dashed + callout (same)          |
| Revision marker        | open circle + dashed     | omitted (hero is current vintage only)  |
| Methodology link       | in panel foot row        | in hero tile foot row (outside canvas)  |
| Vintage stamp          | top-right of card        | top-right of hero tile (outside canvas) |

The pattern: chart-internal narrative gets compressed; chart-external
chrome (title, deck, callout, source line, methodology) does the
narrative work the chart used to. The hero is more of a **typographic
composition with a chart inside it** than a chart with chrome around
it.

---

## 11. ASCII mockup — one hero chart rendered to this spec

Hero section: **Inflation**. Latest print: headline CPI YoY for April
2026, hypothetically 2.4% (vs March 2.3%, consensus 2.3%, so a 0.1pp
upside surprise). Recession bands: 2020Q1-Q2 (would be partly visible
at left of 5-year window if we extend).

```
+------------------------------------------------------------------------+
| INFLATION                                            AS OF May 8, 2026 |
|                                                      Reference: Apr 26 |
|                                                                        |
| Headline CPI rose to 2.4% in April, a tenth above consensus and        |
| the third consecutive print at or above 2%.                            |
|                                                                        |
| Disinflation has stalled near target, with shelter and services        |
| inflation still running hotter than goods.                             |
|                                                                        |
| +-----------------------+ +------------------------------------------+ |
| |                       | |                                          | |
| | 2.4%                  | |  4%                                      | |
| | year-over-year,       | |       _                                  | |
| |   April 2026          | |      / \                                 | |
| |                       | |     /   \_                  --- 2% tgt   | |
| | ^ +0.1pp vs Mar       | |  _ /      \__/\           _              | |
| |   Beat consensus      | | / V          v \   __    / o  <-consens. | |
| |   by 0.1pp [c]        | |/                \_/  \__/  *  CPI YoY    | |
| |                       | | 2%                                       | |
| |                       | |                                          | |
| |                       | | 0%                                       | |
| |                       | |   ____________________________________   | |
| |                       | |   '21    '22    '23    '24    '25  '26   | |
| +-----------------------+ +------------------------------------------+ |
|                                                                        |
| Source: Statistics Canada Table 18-10-0004-01;                         |
| consensus via Bloomberg.                          Methodology >        |
+------------------------------------------------------------------------+
```

Layout legend for the mockup (ASCII compresses):

- The hero tile is the entire bordered region.
- Top-left: section eyebrow (`INFLATION`, `label` all-caps, color =
  section-accent / `series-2` burnt orange).
- Top-right: two-line vintage stamp (per basics-layer-template Section
  6).
- Below, the serif headline (`display-md`) and italic deck (`deck`).
- Then the callout column (left, ~200px) and the 280x140 chart canvas
  (right).
- Inside the canvas: three y-ticks (4%, 2%, 0%), a 2% target reference
  line labeled `2% tgt`, the CPI line in `series-2`, the latest-print
  marker `*`, the consensus tick `o` above it (March 2026 hypothesis:
  consensus 2.3%, print 2.4% — print sits above tick), a dashed
  vertical connector between them, and the direct label `CPI YoY` at
  the right terminus.
- The recession band would be a 6% `ink` tint over 2020Q1-Q2 if it
  fell within the window; in this 2021-2026 view it does not appear.
- Bottom: source line left, methodology link right.

(ASCII renders the consensus tick as `o` and the print marker as `*`;
in implementation, the tick is a 12px horizontal dash and the marker
is a 5px filled circle, per Section 8.)

---

## 12. Token-extension proposals

Two new tokens proposed for inclusion in design-system.md Appendix A
after main-Claude review:

```
/* Hero chart canvas dimensions */
--hero-chart-w-desktop: 280px;
--hero-chart-h-desktop: 140px;
--hero-chart-w-tablet:  360px;
--hero-chart-h-tablet:  160px;
--hero-chart-h-mobile:  180px;  /* width follows container */

/* Hero chart internal layout */
--hero-chart-gutter-left:  32px;  /* y-axis tick label region */
--hero-chart-gutter-right: 44px;  /* direct label region */
--hero-chart-gutter-top:   8px;
--hero-chart-gutter-bot:   18px;  /* x-axis rule + tick labels */
```

No new colors are introduced. No new type sizes. The hero chart reuses
the canonical palette and type scale; what is new is the size
constraint and the compression rules that derive from it.

`[TOKEN PROPOSAL]` Also: a `--hero-tile-callout-w: 200px` for the
callout column width inside the hero tile. If frontend-designer
implements the tile as a CSS grid with `200px var(--hero-chart-w-*)`
column tracks, no token is needed; if it prefers a token, this is the
spec.

---

## 13. Open questions

**For editorial-director:**

1. **Markets as a section.** The hero rotation list includes Markets
   with USDCAD as the load-bearing series, but the basics-layer-template
   maps Trade to `series-7` slate and does not list a Markets section.
   Is Markets a hero candidate at all in v1, or is it folded into
   Financial / Trade? If folded, this spec collapses one row of the
   Section 9 matrix.
2. **Consensus availability per section.** Section 9 marks Inflation,
   Labour, Policy, GDP, Trade as "consensus available" and Housing,
   Markets, plus the Policy rate itself, as "no consensus tick." Confirm
   this maps to the actual feeds we have (or will have) in v1.

**For chart-builder:**

1. **Consensus tick rendering.** The spec calls for a 12px horizontal
   1px dash centered on the x-position of the latest print, in
   `ink-muted`, with a dashed vertical connector to the print marker.
   If this is awkward in the chart library of choice (Observable Plot,
   D3 directly, etc.), propose an alternative that preserves the
   semantics: "where consensus was, where the print landed, lightly
   marked, not loud."
2. **Step function for the BoC overnight chart.** Confirm the rendering
   library supports a true right-angle step function (not a linear
   interpolation between meeting dates). If not, this is a constraint
   to surface back to art-director.
3. **Bar/tick consensus on GDP.** The GDP m/m bars hero raises a
   rendering question: the consensus tick on bars sits across the top
   of the consensus-expected bar height (not over a single x-point as
   on lines). Confirm this is implementable, or propose alternative.

**For frontend-designer:**

1. **Hero tile responsive layout.** At `md` and `sm` breakpoints the
   callout stacks above the chart. Confirm the tile is built with this
   reflow, not with two fixed columns.
2. **Section accent in hero context.** When the hero is Inflation, the
   section accent is `series-2` burnt orange — and the chart's primary
   series is also burnt orange. That's intentional consonance. When the
   hero is Trade, the section accent is slate (`series-7`) but the
   chart line may need to be `series-1` to remain legible against the
   zero-band fill (Section 9 override). Confirm the eyebrow color can
   diverge from the chart series color on a per-section basis without
   the wiring becoming gnarly.

---

End of homepage hero chart visual spec v0.1.
