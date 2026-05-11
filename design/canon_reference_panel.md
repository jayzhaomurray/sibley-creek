# Canon-reference panel - Tier-3 chartbook canon, worked example

Status: blessed. Author: art-director. Last updated: 2026-05-11.

This doc supplements `design/design-system.md` (the canon stays untouched).
It names the worked example, gives the canon-compliance checklist, redlines
the two off-canon precedents, and resolves the one open canon contradiction
that the worked example surfaced.

---

## The blessed reference

`src/components/charts/_canon_reference/PanelCanonReference.astro`

This is the source of truth for every Tier-3 chartbook chart in the
publication. chart-builder copies its structure when authoring any new
panel under `src/components/charts/<section>/`. Deviations require
art-director sign-off in the per-panel visual spec.

Why a reference component and not prose alone: the off-canon Panel files
(GDP Panel 1, Labour Panel 1) read the canon and inadvertently drifted on
every soft rule (line color, dot color, tick family, frame, leader treatment,
multi-series color discipline). A blessed worked example is the cheapest
insurance against that drift across 44 panel components.

The reference scenario is a single-series CPI Y/Y time series with a 2% BoC
target reference rule and a 2020Q1-Q2 recession band. The synthetic data is
not the point; the chart treatment is the point. Copy the file, swap the
indicator, hand-tune the geometry to the new editorial argument.

---

## Canon-compliance checklist

Every Tier-3 panel chart must answer yes to every row, or carry an
art-director-signed deviation in its per-chart visual spec. Run this
checklist before opening a PR.

| #   | Rule                                                                                                                                    | Reference file demonstrates                              |
|-----|-----------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------|
| 1   | Data line is pure ink (`var(--ink)` = `#000000`), stroke-width 1.5px. No section-accent on data, ever.                                  | `.canon-chart__line`                                     |
| 2   | Latest-print dot is MTA red (`var(--accent)` = `#E63946`), 4px radius (3-5px range), filled, no stroke.                                 | `.canon-chart__latest-dot`                               |
| 3   | Plot frame is a 1px pure-ink hairline rectangle around the plot area.                                                                   | `<rect class="canon-chart__frame">`                      |
| 4   | 3-5 horizontal gridlines, pure ink, `stroke-opacity` 0.15-0.20. Vertical gridlines never (small-multiples exception only).              | `.canon-chart__gridline` @ 0.18                          |
| 5   | Y-axis tick labels in IBM Plex Mono 400, 12px (`micro`), pure ink, right-aligned in left gutter; topmost tick carries the unit (`%`).   | `.canon-chart__ytick-label`                              |
| 6   | X-axis tick labels in Manrope 400, 12px (`micro`), pure ink, 3-5 ticks max.                                                             | `.canon-chart__xtick-label`                              |
| 7   | Zero line at 1px pure ink, 100% opacity, heavier than gridlines (only when data crosses zero).                                          | `.canon-chart__zero-line`                                |
| 8   | Optional reference rule (e.g. 2% target, NAIRU): 1px pure ink dashed `4 2`, with a Manrope 600 label on the right side.                 | `.canon-chart__reference-rule` + `__reference-label`     |
| 9   | Optional recession band: `rgba(21, 23, 26, 0.06)` ink wash, behind all data, with a Manrope micro-caps 600 label at top of band.        | `.canon-chart__recession` + `__recession-label`          |
| 10  | One direct end-of-line label per series, Manrope 600 `label` size (13px), pure ink. Replaces any legend. No legend, ever.               | `.canon-chart__direct-label`                             |
| 11  | One hand-tuned annotation: 1px pure ink leader (no arrowhead), Manrope 400 `body-sm` (15px) with anchor word in 600, sitting in white space, ending 4px short of the data point. | `.canon-chart__anno-leader` + `__anno-text` + `__anno-anchor` |
| 12  | Native SVG `<title>` element on every data point. No custom hover, no crosshair, no client JS for the chart.                            | hit-area `<circle>` with `<title>` child                 |
| 13  | viewBox `720 x 405` (16:9), `preserveAspectRatio="xMidYMid meet"`.                                                                      | `<svg viewBox="0 0 720 405" ...>`                        |
| 14  | `aspect-ratio: 16 / 9` on the wrapper so the chartbook-unit slot reserves space before render.                                          | `.canon-chart { aspect-ratio: 16 / 9; }`                 |
| 15  | `aria-label` describing the indicator, frequency, window, and latest-print emphasis.                                                    | `<svg role="img" aria-label="...">`                      |
| 16  | No `--section-accent-*` token on data marks. May appear on chrome elsewhere (plate-number numeral on the chartbook eyebrow), never on the line, dot, marker, or direct label. | (token never referenced in the component)                |
| 17  | No `--series-N` token on a single-series chart. Multi-series adapts via 1px dashed pure-ink secondary, not a second color. See "Multi-series adaptation" below. | (token never referenced in the component)                |
| 18  | Background is `var(--paper)` (pure white). No fill, no card pillow, no border on the wrapper.                                           | `.canon-chart`                                           |
| 19  | Latest-point dot z-order: above the line, above the gridlines, above the frame, below the annotation leader.                            | SVG render order in `<svg>` body                         |
| 20  | Hover model is the browser's native SVG `<title>` tooltip. Zero JS.                                                                     | `<title>` inside each hit `<circle>`                     |

---

## Resolved canon contradiction - y-axis tick typography

**The contradiction.** Section 5.3 of `design/design-system.md` reads:

> "Y-axis tick labels right-aligned in left gutter, **Manrope 400** at
> `micro` size, pure ink. Topmost tick carries the unit (e.g. `4%`)."

Section 10 of the same document reads:

> "The chart's tick labels are the **same Plex Mono regular as the table's
> numeric column**. A reader's eye reading a y-tick reads the same family
> weight and style as a reader reading a table cell - the chart's number
> reads as a measurement, the table's number reads as a measurement, they
> are the same kind of object."

Both are explicit; both cannot be true.

**Decision: Section 10 wins. Y-axis tick labels are IBM Plex Mono 400 at
`micro` (12px), pure ink.**

**Rationale.**

1. **Cohesion is the higher-order rule.** Section 10 exists to enforce
   that chart and page read as one object. The whole publication is a
   chartbook + table dance. If the chart's y-axis numbers read in Manrope
   and the adjacent table's numbers read in Plex Mono, the reader's eye
   parses them as two different *kinds* of measurement, which is exactly
   what Section 10 explicitly prohibits.
2. **Vignelli's own move.** Plex Mono is the publication's "this is a
   measurement, vintaged to a moment" signal (Section 2). A y-tick is a
   measurement. Putting it in the sans family undermines the typographic
   contract.
3. **The Manrope reading in 5.3 is a v0.1 inheritance.** The original
   chart-builder spec predated the full canonicalization of the
   "Plex Mono = data" rule. Section 5.3's tick-label clause is the
   pre-Plex-Mono-on-data-only language. It contradicts the rule the canon
   later settled on.
4. **X-axis ticks stay Manrope.** Dates are not measurements; they are
   calendar labels. The asymmetry is editorially principled: numbers in
   Plex Mono, words and dates in Manrope.

**Action.** This decision is recorded here. The canon document
(`design/design-system.md`) will be updated in its next revision pass to
align Section 5.3 with Section 10; until then, the reference component
and this checklist are authoritative for chart-builder.

The X-axis label rule remains Manrope 400 (a tick label like "2024" is a
year, not a measurement). The y-axis label rule is Plex Mono 400. The two
families coexisting at the same 12px size is fine: the Plex Mono glyphs
visibly read as data; the Manrope dates visibly read as language. The
contrast is the point.

---

## Multi-series adaptation - the canonical pattern

The reference file is single-series. Section 5.3 permits multi-series
panels but is strict: "**One color on data per chart, plus a latest-point
dot.** The secondary series uses 1px ink with a dashed pattern to recede,
not a second color."

For a panel with two series (primary + secondary):

- **Primary series:** pure ink (`var(--ink)`), 1.5px solid stroke. MTA red
  latest-point dot. Direct end-of-line label in Manrope 600.
- **Secondary series:** pure ink (`var(--ink)`), 1px solid (lighter than
  primary), `stroke-dasharray: "4 2"`. NO latest-point dot (the dot is
  reserved for the primary, the indicator that anchors the editorial
  read). Direct end-of-line label in Manrope 400 (lighter than the
  primary's 600).

For a panel with three series (primary + secondary + tertiary), the
tertiary moves to a 1px pure-ink `stroke-dasharray: "2 3"` (a sparser
dash). The two-axis convention is also retired in favor of a single
shared axis where possible; if a second axis is genuinely required (e.g.
participation rate at 65% alongside unemployment rate at 6% would compress
intolerably on a shared scale), bring a per-chart visual spec to
art-director with the justification, and the secondary axis renders in
the same Plex Mono 400 12px treatment as the primary, right-aligned in
the right gutter.

**Hue is never recruited to differentiate series.** Weight, dash pattern,
stroke width, and direct-label weight do the work. This is the canon's
single hardest line: there are no colored multi-series charts in this
publication.

---

## Redline 1 - `src/components/charts/gdp/Panel1HeadlineGDP.astro`

The file is structurally sound (60-month window, 16:9 viewBox, native
`<title>` hover, no client JS) but **violates the visual canon on every
data-color decision and on most chrome typography**. It should be rebuilt
to the reference template. The TS computation layer can be preserved; the
rendering layer should be regenerated.

What to keep (the geometry layer):

- The viewBox dimensions (720x405) and the `M_L/M_R/M_T/M_B` margin scheme.
- The `decYearOf` / `xScale` / `yScale` helpers.
- The recession-band computation (`recStart`/`recEnd`/`recVisible`).
- The latest-point identification.
- The revision-dashed-line concept (this is a defensible chart-specific
  extension; it does not violate canon if it is rendered in pure ink, 1px,
  `stroke-dasharray "2 2"`).

What to delete (the rendering layer):

| Line(s)             | Current                                                                       | Violation                                                                                          | Correction                                                                                                            |
|---------------------|-------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------|
| 459                 | `.gdp-panel-chart__bar { fill: var(--section-accent-gdp); }`                  | Section-accent on data. Canon Section 5.3: "One color on data per chart" = pure ink.               | `fill: var(--ink);` Pure black columns. Period.                                                                        |
| 461-466             | `.gdp-panel-chart__line { stroke: var(--section-accent-gdp); ... }`          | Section-accent on data line. The single biggest violation.                                         | `stroke: var(--ink); stroke-width: 1.5;` and add `vector-effect: non-scaling-stroke;`                                   |
| 468-475             | `.gdp-panel-chart__marker { fill: var(--section-accent-gdp); }` and the same on `--marker-latest` | All quarterly markers are blue. Latest is blue. There is no MTA red brand stamp anywhere.        | Drop `.gdp-panel-chart__marker` (no all-markers; the line conveys the trace). Make `.gdp-panel-chart__marker-latest` the ONLY marker, in `var(--accent)`, 4px radius, no stroke ring on surface (the ring on `--surface` is a transit-map move, not a chart move). |
| 508-513             | `.gdp-panel-chart__direct-label { fill: var(--section-accent-gdp); ... font-weight: var(--fw-medium); }` | Direct label in blue. Should be pure ink Manrope 600. Section 10 says the direct label reads as the same kind of stamp as the eyebrow. | `fill: var(--ink); font-family: var(--font-sans); font-weight: var(--fw-semibold); font-size: 13px;` Drop the `tabular-nums` (this is a label, not a number). |
| 451-454             | `.gdp-panel-chart__gridline { stroke: var(--rule-faint); stroke-width: 1; }`  | `--rule-faint` resolves to pure black at 100% opacity. Gridlines should be 0.15-0.20 ink opacity, not full-strength pure black hairlines. | `stroke: var(--ink); stroke-opacity: 0.18;`                                                                            |
| 455-457             | `.gdp-panel-chart__gridline--zero { stroke: var(--ink-muted); }`              | Zero line is the same `--ink-muted` (pure black) at full opacity. Functionally correct but the visual distinction is fragile - if the gridline opacity stays at 1.0 (as it does now), zero is indistinguishable. | After fixing gridlines to 0.18 opacity above, this rule renders zero at full opacity correctly. Keep the class, ensure it overrides `stroke-opacity` to 1.   |
| 495-501             | `.gdp-panel-chart__ytick-label { fill: var(--ink-faint); font-size: 11px; font-weight: var(--fw-medium); }` and the same on x-tick. | Tick labels in Manrope (the default `.gdp-panel-chart__svg { font-family: var(--font-sans); }`). Y-axis numbers should be Plex Mono 400 per Section 10 cohesion (see "Resolved canon contradiction" above). Also 11px is below the 12px `micro` size. Also `--fw-medium` (600) is wrong - tick labels are 400. | Split into two classes: `__ytick-label` = `font-family: var(--font-mono); font-size: 12px; font-weight: var(--fw-regular);`. `__xtick-label` = `font-family: var(--font-sans); font-size: 12px; font-weight: var(--fw-regular);` |
| 502-507             | `.gdp-panel-chart__unit { ... font-size: 11px; font-weight: var(--fw-medium); }` and the inline "% per month / quarter" text element at line 376-380 | The "unit annotation top-left" duplicates what the topmost y-tick should carry (Section 5.3 "Topmost tick carries the unit"). | DELETE the `__unit` text element and the `__unit` class. The topmost y-tick label renders `+1.0%` etc., carrying the unit on its glyph.                                  |
| (missing)           | No plot frame.                                                                | Section 5.3: "Hairline 1px black plot frame (a rectangle around the plot area)." Section 10: "The chart's plot frame is the same 1px black hairline as the panel table's row dividers." | Add `<rect class="gdp-panel-chart__frame" ...>` with `stroke: var(--ink); stroke-width: 1; fill: none;`                |
| (missing)           | No MTA red anywhere.                                                          | Latest-print dot is the publication's brand-signal moment on every chart. The current file has zero accent ink anywhere on the chart. | The latest quarterly marker becomes the MTA red dot at 4px radius. There is one such dot per chart.                   |
| 519-524             | `.gdp-panel-chart__anno-text { ... font-size: 13px; font-weight: var(--fw-regular); }` | 13px is the `label` size, not `body-sm` (15px). Annotation should be at body-sm. Also the anchor-word weight contrast (one word in 600) is missing - the file does no anchor parsing. | Bump to 15px. Add anchor parsing on `**bold**` substrings (see reference component's `parseAnchor` helper). The anchor word renders at 600.                                       |
| 514-518             | `.gdp-panel-chart__anno-leader { stroke: var(--ink-muted); ... }`             | Acceptable color, but the file draws a 2-segment elbow leader (vertical + horizontal). The canon allows straight or single-elbow but here the elbow is awkward. | Prefer a single straight segment from annotation right-edge to dot-minus-4px. Hand-tune per panel; keep `stroke: var(--ink); stroke-width: 1;` and no arrowhead.                          |
| 476-481             | `.gdp-panel-chart__revision { stroke: var(--ink-faint); stroke-width: 1; stroke-dasharray: 2 2; }` | Acceptable visually (pure ink dashed). The current `stroke-dasharray: 2 2` is the tighter pattern; canon convention for reference rules is `4 2`. For a revision marker `2 2` is fine - the tighter dash reads as a small adjustment. | Keep. This is a chart-specific extension and the dash treatment is internally consistent.                                                   |

**Result.** A GDP Panel 1 with pure black bars, pure black line, one MTA
red dot at the latest quarter, pure ink hairline plot frame, gridlines at
0.18 opacity, Plex Mono y-ticks, Manrope x-ticks, no separate unit
label (unit on topmost tick), one Manrope 600 direct label "Quarterly Q/Q
SAAR" at the line terminus, one Manrope 600 direct label "Monthly m/m" in
upper-left whitespace, and an annotation with a single-segment ink leader
and an anchor word in 600. Identical to the reference template visually,
with the dual-frequency bars + line being the chart's specific editorial
move.

---

## Redline 2 - `src/components/charts/labour/Panel1LFSHeadline.astro`

This is the multi-series stress-test. The file has three series in three
colors (sage, slate, sage-at-60%-opacity) on two y-axes, which is the
exact pattern the canon forbids. The rebuild must obey "one color, weight
and dash do the work."

What to keep (the geometry layer):

- The viewBox, margins, scales, x-tick computation.
- The `buildLine` helper.
- The dual-axis scaffolding (the participation-rate scale is genuinely
  separate from the unemployment-rate scale - canonical exception per the
  "Multi-series adaptation" section above).

What to delete (the rendering layer):

| Line(s)         | Current                                                                                                                       | Violation                                                                                                                                                                            | Correction                                                                                                                                                                                                            |
|-----------------|-------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 367-373         | `.labour-panel-chart__line-un { stroke: var(--series-3); stroke-width: 1.5; ... }`                                            | Series token on the primary. Sage on the headline series. Color-encodes identity.                                                                                                    | `stroke: var(--ink); stroke-width: 1.5;` Primary = pure ink solid.                                                                                                                                                     |
| 374-380         | `.labour-panel-chart__line-emp { stroke: var(--series-7); stroke-width: 1.5; ... }`                                           | Second series in slate; second hue on data.                                                                                                                                          | `stroke: var(--ink); stroke-width: 1; stroke-dasharray: "4 2";` Secondary recedes via 1px dashed pure ink.                                                                                                              |
| 381-389         | `.labour-panel-chart__line-part { stroke: var(--series-3); stroke-opacity: 0.6; stroke-width: 1; stroke-dasharray: 4 2; }` (tertiary) | Tertiary in sage at 60% opacity. The canon does not use opacity to differentiate series (opacity is for gridlines/recession band).                                                  | `stroke: var(--ink); stroke-width: 1; stroke-dasharray: "2 3";` Tertiary differentiates from secondary via sparser dash pattern, not via opacity.                                                                       |
| 390-399         | `.labour-panel-chart__marker-un { fill: var(--series-3); stroke: var(--surface); stroke-width: 1; }` plus emp + part markers | Three colored markers, one per series. Canon: one MTA red dot, on the PRIMARY only.                                                                                                  | Delete `__marker-emp` and `__marker-part` entirely. `__marker-un` becomes `fill: var(--accent); stroke: none;` at `r="4"`. There is exactly one latest-print dot on this chart; it sits on the unemployment-rate primary. |
| 423-433         | `.labour-panel-chart__direct-label--un { fill: var(--series-3); }` and `--emp { fill: var(--series-7); }` and `--part { fill: var(--series-3); fill-opacity: 0.7; }` | Direct labels colored to match their line. Reinforces the color-encoding.                                                                                                            | All direct labels in `fill: var(--ink); font-family: var(--font-sans);`. Primary "Unemployment" at `font-weight: var(--fw-semibold); font-size: 13px;`. Secondary "Emp. rate" at `font-weight: var(--fw-regular); font-size: 13px;`. Tertiary "Participation (R)" at `font-weight: var(--fw-regular); font-size: 12px;`. Weight contrast does the hierarchy work. |
| 410-417         | `.labour-panel-chart__ytick-label, ... .labour-panel-chart__xtick-label { fill: var(--ink-faint); font-size: 11px; font-weight: var(--fw-medium); font-variant-numeric: tabular-nums; }` | Same Manrope-on-y-axis violation as GDP Panel 1, plus 11px and weight 600.                                                                                                          | Split: y-tick labels (primary AND secondary) -> Plex Mono 400 12px, tabular. X-tick labels -> Manrope 400 12px.                                                                                                            |
| 287-298         | Two `__unit` text elements ("% (left: u-rate, emp-rate)" and "% (right: participation)")                                       | Section 5.3: "Topmost tick carries the unit." No separate unit label.                                                                                                                | Delete both `__unit` text elements. Top-left y-tick renders e.g. `9%`; top-right y-tick renders `68%`. The reader reads the gutter, not a separate caption.                                                            |
| 362-366         | `.labour-panel-chart__gridline { stroke: var(--rule-faint); stroke-width: 1; }`                                              | Pure black at 100% opacity.                                                                                                                                                          | `stroke: var(--ink); stroke-opacity: 0.18;`                                                                                                                                                                            |
| (missing)       | No plot frame.                                                                                                                | Same omission as GDP Panel 1.                                                                                                                                                        | Add 1px pure-ink `<rect>` around the plot area.                                                                                                                                                                        |
| 434-444         | `.labour-panel-chart__anno-text { ... font-size: 13px; font-weight: var(--fw-medium); }`                                      | Same as GDP Panel 1: 13px not 15px; weight 600 globally instead of 400 with a 600 anchor word.                                                                                       | Bump to body-sm 15px Manrope 400; parse `**anchor**` substrings to 600. Same `parseAnchor` helper as the canon reference.                                                                                              |
| 197-204         | Render order: participation line drawn first, then emp, then un. Markers drawn after lines. No plot frame, no native title on the line itself. | Drawing the headline line last is correct (top of z-stack). But the file does not put a native `<title>` on each data point - only the three latest markers carry hover. | Add invisible hit-area circles per unrate datum with `<title>` showing date + unrate. Optionally per emprate datum too; participation can stay marker-less since the latest-point treatment is the unrate's. |

**Result.** A labour Panel 1 with one black solid line (unemployment),
one black dashed `4 2` line (employment rate), one black dashed `2 3` line
(participation, on a secondary axis), one MTA red 4px dot on the latest
unemployment print, three Manrope direct labels in pure ink with weight
contrast (600 / 400 / 400), Plex Mono y-ticks on both axes, Manrope
x-ticks, plot frame, gridlines at 0.18 ink opacity, and a 15px Manrope
annotation with a 600 anchor word and a single-segment ink leader.

The three-series-in-three-colors rainbow is gone. Identity comes from
weight and dash pattern. The reader follows the headline (heaviest solid
ink), reads the secondary (dashed but solidly ink), and contextualizes
the tertiary (sparse dash on the right axis). This is exactly the
Vignelli register applied to a multi-series labour chart.

---

## Other canon gaps spotted while writing this reference

These are not deviations from the canon document; they are gaps the
canon document does not currently address. art-director will fold them
into the next revision of `design/design-system.md`. Until then they are
authoritative here.

1. **Z-order convention.** Section 5.3 does not specify the SVG draw
   order. The canonical order (back-to-front): recession band -> reference
   rule -> gridlines -> zero line -> data line -> data-point hit areas
   with `<title>` -> latest-point dot -> plot frame -> tick marks and
   labels -> direct label -> annotation leader -> annotation text. The
   plot frame draws AFTER the data line so the line's caps do not
   overshoot the frame edge visually.

2. **Latest-point dot radius range.** Section 5.3 says "3-5px filled
   circle." The reference uses 4px. Mini-charts (Tier 2) use 3px. Tier-3
   uses 4px by default; 5px only when the chart is the page hero (which
   the publication does not currently have). 3px on Tier-3 reads as too
   delicate at chartbook scale.

3. **Hit-area pattern.** The reference renders invisible 4px-radius
   transparent `<circle>` hit areas with `<title>` children at every data
   point. This is the canonical zero-JS hover. The latest-print dot itself
   carries its own `<title>` with "Latest:" prefix. Earlier panel files
   put `<title>` only on visible markers, which works for charts that draw
   markers everywhere but fails for line-only Tier-3 charts. The hit-area
   pattern is the correct general solution.

4. **Reference-rule label placement.** Section 3 covers event lines but
   not reference rules (like a 2% target). The reference places the label
   on the right side of the plot, in Manrope 600 12px pure ink, with a
   small upward y-offset (5px above the rule). Left-aligned would collide
   with the y-axis tick labels; right-aligned at the right gutter would
   collide with the direct end-of-line label. Right-end inside the plot,
   above the rule, is the cleanest hand-tuned default.

5. **Annotation leader endpoint.** Section 5.3 says "End 4px short of the
   data point." With a 4px-radius MTA red dot, ending the leader 4px short
   of the dot's CENTER means the leader just touches the dot's edge. Better:
   end the leader 7px short of center (= 3px short of the dot's edge),
   so a clear 3px gap of pure paper sits between the leader tip and the
   red dot. This reads as a deliberate Vignelli gap, not a near-miss. The
   reference uses the 7px-from-center convention.

6. **`foreignObject` for annotations with inline weight contrast.** SVG
   `<text>` cannot mix weights inline without `<tspan>` boilerplate. The
   reference uses `<foreignObject>` wrapping an HTML `<p>` with a
   `<strong>` for the anchor word. This is the canonical approach for
   any chart annotation that needs a 600-weighted anchor word inside a
   400-weighted sentence. Native browser support is universal for static
   server-rendered SVG.

---

## Order of operations for chart-builder

When rebuilding any panel in `src/components/charts/<section>/`:

1. Read this doc and `design/design-system.md` Sections 5.3, 10, and 3.
2. Open the reference component.
3. Copy the file. Rename for your section + panel.
4. Replace the synthetic data with the real `MonthlyPoint` / `DataPoint`
   shape, keeping the placeholder generator below the type definition.
5. Adjust the chart-specific geometry (bars instead of lines if it's a
   bar chart, dumbbell if it's a comparison chart, etc.). For each
   deviation, justify in the file header comment why this chart needs
   its specific mark.
6. Walk the canon-compliance checklist line by line in the file header
   comment. Every "yes" is asserted, every "deviation" cites art-director
   approval.
7. Bring the rebuilt file to art-director for a redline pass.

The reference is not a one-size-fits-all template; it is the
typographic and chromatic discipline that every chart inherits. The
chart-specific marks (bars, lines, dumbbells, fan charts, recession-
state heatmaps) vary by panel and ride on top of the same canon.
