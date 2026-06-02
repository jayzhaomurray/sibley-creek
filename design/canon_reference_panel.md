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
| 2   | Latest-point dot is MTA red (`var(--accent)` = `#E63946`), 4px radius (3-5px range), filled, no stroke. **Line/area charts only — never on bar/column charts.** Sits on the **last plotted observation**, including a forecast point if the series ends in forecast. One dot per chart; on multi-series, primary series only (secondary gets none). | `.canon-chart__latest-dot`                               |
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

---

## Decisions: rebuild redlines (2026-05-11)

After chart-builder's 18-panel rebuild (GDP / Inflation / Labour),
five open questions surfaced where the canon was either silent or
contradictory at the implementation level. Each is decided here. The
canon reference component has been patched where applicable.

### Q1. Inflation Panel 3 (Breadth) band weighting

**Decision: above-3% reads heaviest. Keep the encoding as built**
(`above-3% = 100% ink`, `target band 1-3% = 35% ink`, `below-1% =
12% ink`).

**Rationale.** Section 4.2 of `editorial/dashboard_purpose.md`
frames the inflation section's purpose as: "Is the BoC's 2% target
being met, and on what measures and what breadth?" The headline
question is about target *compliance*; the breadth panel is the
*so-what* on how widely target is being missed. For the Bay Street
allocator (P1, the dominant persona), the editorial payload of the
panel is the share of the basket that is *misbehaving* relative to
target. The target band itself is the comfort zone - by definition
the part of the chart that does not need attention. Heaviest ink on
the part of the distribution that demands attention is the correct
Tufte / Vignelli call: ink density reads as editorial weight.

An alternative argument - "target compliance is the editorial
positive, so reward the eye that lands on the comfort zone" - is
the wrong frame for this publication. Sibley Creek does not exist
to congratulate the BoC; it exists to tell a P1 reader where the
cycle is misbehaving. The breadth chart's job is to surface
out-of-target mass.

The encoding is also internally consistent: ink density tracks
distance-from-target in absolute terms (above-3% and below-1% are
both deviations, and above-3% in the post-2021 regime dominates as
the larger deviation). The 12% / 35% / 100% gradient reads as a
density ramp where the eye correctly weights the largest deviation
heaviest.

**Action.** None. Panel 3 stays as built. No production-component
change required.

### Q2. Panel filenames

**Decision: keep the actual on-disk filenames.** The brief's working
titles in the rebuild brief were drafted before chart-builder named
the production files; the on-disk names are more descriptive of
each chart's editorial argument and are the names referenced from
the section page imports.

Authoritative filenames (locked):

- `src/components/charts/gdp/Panel1HeadlineGDP.astro`
- `src/components/charts/gdp/Panel2IndustryVsExpenditure.astro`
- `src/components/charts/gdp/Panel3Contributions.astro`
- `src/components/charts/gdp/Panel4PerCapita.astro`
- `src/components/charts/gdp/Panel5OutputGap.astro`
- `src/components/charts/gdp/Panel6Recession.astro`
- `src/components/charts/inflation/Panel1Headline.astro`
- `src/components/charts/inflation/Panel2CoreMeasures.astro`
- `src/components/charts/inflation/Panel3Breadth.astro`
- `src/components/charts/inflation/Panel4SubAggregates.astro`
- `src/components/charts/inflation/Panel5Expectations.astro`
- `src/components/charts/inflation/Panel6PassThrough.astro`
- `src/components/charts/labour/Panel1LFSHeadline.astro`
- `src/components/charts/labour/Panel2PerCapita.astro`
- `src/components/charts/labour/Panel3WageBand.astro`
- `src/components/charts/labour/Panel4VacanciesAndSlack.astro`
- `src/components/charts/labour/Panel5IRCCSupplyTrajectory.astro`
- `src/components/charts/labour/Panel6RegionalDispersion.astro`

**Convention.** `PanelN<EditorialShortName>.astro`. The short name
is the chart's editorial argument in PascalCase, not the data
source or the chart shape. "PerCapita" beats "PerCapitaEmpDecomp."
"WageBand" beats "HoursWages." "IRCCSupplyTrajectory" beats
"Demographic."

**Action.** None. No renames required. Future panels follow the same
naming convention.

### Q3. Aspect ratio: 16:9 for ALL non-sparkline charts (canon override 2026-05-11)

**Decision (2026-05-11 supersedes prior 2026-05-11 ruling):
ALL non-sparkline charts use viewBox `720 x 405` (16:9). No
categorical / snapshot / dumbbell exception. No 4:3 (720 x 540)
fallback.** Every Tier-3 chartbook chart shares the canon Tier-3
viewBox.

**Why the override.** Chart dimensions are the cleanest editorial
signal of "this is one publication, set with one discipline." When
a reader scans a section page and sees seven charts of identical
proportions, the page reads as a Knoll catalogue (Section 1).
When chart heights differ - even by a "principled" categorical
exception - the page reads as a Tableau dashboard. The Vignelli
register cannot afford that drift.

The original argument for the 4:3 exception ("forcing every chart
into 16:9 will crush categorical row spacing into illegibility")
proved overstated in production. Six-row dumbbell, six-bar
horizontal, six-CMA snapshot - all fit 16:9 cleanly with a modest
tightening of `ROW_GAP` / `BAR_H` and a small reduction of top/bottom
margins. The trade is real (a 4:3 dumbbell breathes more) but the
cohesion gain across the section page is the larger editorial win.

**Updated checklist row 13.** The canon-compliance checklist (Rule
13) is restated as:

> 13. **All non-sparkline charts:** viewBox `720 x 405` (16:9),
>     `preserveAspectRatio="xMidYMid meet"`. The wrapper carries
>     `aspect-ratio: 16 / 9`. No exceptions.

**The prior 4:3 exception is RETIRED.** Charts that previously used
the 4:3 (or other non-16:9) ratio - GDP Panel 3, Labour Panel 6,
Inflation Panel 3/4/5/6, Labour Panel 2/4, and several housing /
policy / markets / trade panels - were refactored to 720 x 405 on
2026-05-11. Internal sub-canvas heights, row gaps, and bar heights
were tightened to fit the canon canvas.

**Sparkline carve-out.** Tier-1 sparklines (`src/components/Sparkline.astro`)
keep their decorative 160 x 40 viewBox; they are not Tier-3 charts.
This is the only carve-out from the canon.

**Action.** Applied. All production panels are at 720 x 405. The
formal edit to Section 5.3 of `design/design-system.md` is folded
into this canon doc; the design-system document will be revised
in its next pass.

### Q4. BEM scope: panel-scoped, not canon-scoped

**Decision: production panels use panel-scoped class names
(`.panel-N-<shortname>__*`). `.canon-chart__*` is reserved
exclusively for the canon reference component.**

Inflation Panel 4's `.panel-4-sub__*` scope stays. No rename.

**Rationale.** Three reasons:

1. **Canon compliance is enforced by what the rules say, not by
   what the class is named.** The reference component is the
   typographic and chromatic discipline; production panels inherit
   that discipline regardless of the class-name namespace. A panel
   whose `.panel-3-breadth__line` is `stroke: var(--ink);
   stroke-width: 1.5` is canon-compliant exactly as much as a panel
   whose `.canon-chart__line` is the same. The styles enforce the
   canon; the class name is a namespace.
2. **Production panels need chart-specific extensions that the
   canon does not anticipate.** The breadth panel has a three-band
   ladder; the contributions panel has a contribution-bar pair; the
   dumbbell has provinces-as-rows. Panel-scoped class names keep
   these extensions safe from collision with the canon reference's
   classes if a page ever needs to render both (e.g., a methodology
   note that includes the canon reference inline).
3. **Single-source-of-truth discipline.** `.canon-chart__*` on a
   production panel would imply the panel IS the reference, which
   would then make every chart-specific override feel like a
   deviation from the canon rather than a chart-specific extension.
   The namespace separation makes the distinction crisp: the
   reference is the reference; the panels reference the reference.

**Action.** None. Existing panel-scoped namespaces stay. Future
panels follow `.panel-N-<shortname>__*` (e.g., `panel-2-percap__*`,
`panel-5-supply__*`). The shortname should match the filename's
editorial short name (Q2 convention).

### Q5. foreignObject xmlns: pragmatic, not strict

**Decision: remove `xmlns="http://www.w3.org/1999/xhtml"` from the
`<p>` element inside `<foreignObject>`. The canon reference is
patched (2026-05-11); chart-builder's rebuilds were correct.**

**Rationale.**

1. **`astro check` is the toolchain we ship against.** The strict
   reading (xmlns required) raises a TypeScript error on JSX-style
   attribute syntax; the lint gate is real production friction.
2. **Modern browsers infer the XHTML namespace from
   `foreignObject` context.** Render output is identical whether or
   not the xmlns attribute is present. Static server-rendered SVG
   with `foreignObject > p > strong` works in Chromium, WebKit, and
   Gecko without xmlns. This is empirically tested in the rebuilt
   panels.
3. **Spec strictness is a non-goal when the spec compliance breaks
   the toolchain.** We are not delivering raw SVG to an SVG-renderer
   that lives outside a browser context; we are delivering inline
   SVG inside HTML5 documents. The XHTML namespace lineage on
   foreignObject children is an SVG 1.1 / XHTML 1.0 compatibility
   pattern, not a contemporary HTML5+SVG2 requirement.

**Action taken.** `_canon_reference/PanelCanonReference.astro` is
patched: line 426's `<p xmlns="http://www.w3.org/1999/xhtml"
class="canon-chart__anno-text">` is now `<p
class="canon-chart__anno-text">`. The file header comment is
updated to call out the xmlns omission and cross-reference this
decision (rule 11 of the comment block).

**Follow-up notes for chart-builder.** None required. The 18
rebuilds already removed `xmlns`; they were ahead of the canon on
this. If any production panel still carries `xmlns` on a
foreignObject child paragraph, drop it in the next sweep.

---

## Label placement rules (no-overlap canon)

Status: blessed 2026-05-11. Authority: art-director.

A chartbook panel can render up to six distinct label families on one
canvas:

1. Direct end-of-line label, primary series (Manrope 600 13px).
2. Direct end-of-line label, secondary series (Manrope 400 13px).
3. Y-axis tick labels (Plex Mono 400 12px), left gutter, right-aligned.
4. X-axis tick labels (Manrope 400 12px), below plot rule.
5. Recession-band label (Manrope micro-caps 600 11px, 0.18em tracking),
   above band, only on the most recent recession.
6. Reference-rule label (Manrope 600 12px), right end of rule.
7. Optional recent-print annotation callout (Manrope 400 15px, anchor
   word 600, 1px pure ink leader). Deferred until Phase 2 - see Q3
   below.

These can collide with each other and with the data line. The rules
below define the legal placements + the suppression hierarchy when a
collision cannot be resolved by re-placement.

### Geometry constants (pinned)

These are the numeric guards every rule below cites. Pinned to
`PanelLiveChart.astro` geometry. Changing one of these requires
art-director sign-off.

| Constant       | Value | Meaning                                                       |
|----------------|-------|---------------------------------------------------------------|
| `LABEL_GAP_X`  | 10px  | Horizontal gap from last-point dot center to direct label.    |
| `LABEL_PAD_R` | 4px   | Direct label sits at least this many px inside the right margin so it never touches `VB_W`. |
| `LABEL_LH`     | 14px  | Direct label line-height. Used as the vertical-stack center-to-center gap when primary + secondary stack. |
| `LABEL_MIN_DY` | 12px  | If primary and secondary direct labels' baselines are closer than this in y, stack them apart instead. |
| `REF_LABEL_MIN_DY` | 16px | If a direct label is within this y-distance of the reference-rule's y-line, the reference-rule LABEL is suppressed (the rule itself stays). |
| `RECESSION_LABEL_DY` | 6px | Recession label sits this many px above band's top.        |
| `RECESSION_LABEL_GUARD` | 12px | A y-tick label whose baseline is within this many px of the recession-label baseline is suppressed for that tick only. |
| `PLOT_FRAME_PAD` | 2px | Minimum distance any label's nearest stroke must keep from the plot frame edge. |

### Rule L1 - Direct end-of-line label, primary series

**Placement.** Baseline at `lastPrim.y + 4` (vertical-centered on the
dot center). X anchor at `lastPrim.x + LABEL_GAP_X`, text-anchor
`start`. If the natural anchor would push the label's right edge past
`PLOT_X1 + M_R - LABEL_PAD_R` (the rightmost legal column), switch to
text-anchor `end` and anchor at `PLOT_X1 + M_R - LABEL_PAD_R`. In
practice the right margin (`M_R=96`) is sized so this fallback rarely
fires; it is the safety net.

**Collision with secondary direct label.** If `|primaryY - secondaryY|
< LABEL_MIN_DY`, both labels stack: the higher-y-value series stays at
its natural y, the lower-y-value series moves to `(higher.y + LABEL_LH)`
or `(lower.y - LABEL_LH)` whichever keeps both inside the plot+margin
band. See Rule L6.

**Collision with reference-rule label.** If a reference-rule label
exists and `|primaryY - refY| < REF_LABEL_MIN_DY`, the **reference-rule
label is suppressed** (Rule L4). Direct label always wins; the dashed
rule itself stays drawn.

**Collision with the data line.** Not algorithmically resolved in v1.
The 10px x-gap to the right of the last-point dot puts the label in the
right gutter, which is data-free by construction. Edge case: when the
line is rising steeply at the terminus the label can still feel close
to the prior data segment. Acceptable in v1; flagged in known edge
cases below.

### Rule L2 - Direct end-of-line label, secondary series

Identical placement convention to L1 but with Manrope 400 weight (not
600). All collision rules from L1 apply, with one additional rule:

**Collision with primary direct label.** Handled by Rule L6
(multi-series stacking). When stacking, the secondary moves preferentially
(primary stays at its natural anchor, secondary slides). Rationale: the
primary is the editorial argument; preserving its read position keeps
the chart's payload anchored.

**Suppression.** If the secondary line was already suppressed by the
units-don't-match guard, the secondary label is suppressed
automatically.

### Rule L3 - Y-axis tick labels

**Placement.** Right-aligned at `PLOT_X0 - 8`, baseline at `tickY + 4`.
Plex Mono 400 12px pure ink. Topmost tick carries the unit suffix
(`%`, `B`, `pp`, etc).

**Collision with recession-band label.** If a y-tick's baseline is
within `RECESSION_LABEL_GUARD` (12px) of the recession-band-label's
baseline, **suppress that y-tick label** (the tick mark itself, if any,
stays; only the numeric label hides). Recession label wins because it is
hand-tuned editorial; ticks are regular metric chrome. Other y-tick
labels render normally.

**Never inside the plot area.** Y-tick labels live in the left gutter
exclusively. A label that would visually overlap the plot frame is
suppressed.

### Rule L4 - Reference-rule label

**Placement.** Right-anchored at `PLOT_X1 - 6`, baseline at `refY - 5`
(5px above the rule). Manrope 600 12px pure ink. Sits inside the plot
area on its right edge.

**Collision with direct end-of-line label(s).** If any direct label's
baseline is within `REF_LABEL_MIN_DY` (16px) of the reference-rule's
y-line, **suppress the reference-rule label only**. The dashed rule
itself stays drawn. Rationale: a reader scanning the right gutter
reads "CPI Y/Y 2.3%" as the editorial payload; "2% BoC target" is
context that the dashed rule itself conveys without redundant text.

**Edge case: reference value outside plot range.** Already handled by
the existing `showRef` guard.

### Rule L5 - Recession-band label

**Placement.** Centered horizontally on the band's midpoint; baseline
at `PLOT_Y0 + 12` (so the label's top sits `RECESSION_LABEL_DY` =
6px below the top of the plot frame, allowing for the 11px cap height).
Manrope 600 11px micro-caps, 0.18em letter-spacing, pure ink.

**Suppression.** Only render if the recession band itself is visible
(at least partially inside the current x-window). The 2020Q1-Q2
recession falls outside the default 60-month window for builds dated
2025-Q3 or later; in those builds neither the band nor the label
render. No code change needed.

**Y-tick coexistence.** Y-tick labels obey Rule L3 and suppress
themselves to defer to this label.

### Rule L6 - Multi-series direct labels (stacking)

When both `L1` and `L2` would render and `|L1.y - L2.y| < LABEL_MIN_DY`
(12px):

1. The series whose terminal y-value is **higher in plot coordinates**
   (lower visual y - the upper line) anchors at its natural y.
2. The other label moves to `anchor.y + LABEL_LH` (14px below the
   anchor's baseline center).
3. If the moved label would fall below `PLOT_Y1 + M_B - 4`, flip the
   move: the lower-anchor stays put and the higher one moves up to
   `anchor.y - LABEL_LH`.

This is the canon's "stack don't overlap" rule. Vertical stack with
14px center-to-center reads as deliberate; overlapping reads as a bug.

### Rule L7 - Recent-print annotation callout (Phase 2)

Deferred. The old hand-tuned annotation lived in `PanelCanonReference`;
it was removed in the PanelLiveChart collapse because per-panel
positioning cannot be auto-computed without scoring four candidate
positions and a white-space test. Algorithm sketched below for the
Phase 2 restoration:

1. Score 4 candidate positions (top-left, top-right, bottom-left,
   bottom-right of the last-point dot, each at distance 48px).
2. For each candidate, compute the minimum perpendicular distance from
   the candidate's bounding box to the data line, sampled at the last
   24 segments. Higher distance = more whitespace = better score.
3. Pick the highest-scoring position. If max-score is below 32px
   (annotation would sit over data), **suppress the annotation** -
   fall back to native SVG `<title>` for accessibility.

In v1 (current build), PanelLiveChart does not render annotation
callouts. Charts that need an annotation are authored as bespoke
components (see GDP Panel 1, Labour Panel 1 redlines above) rather
than going through PanelLiveChart.

### Suppression hierarchy (when something must hide)

When two labels collide and re-placement is not legal, the loser is
suppressed entirely. Hierarchy from highest priority (always rendered)
to lowest priority (first to hide):

1. **Y-axis tick labels carrying the unit** (topmost tick). Never
   suppressed. The reader must always be able to read the chart's
   scale.
2. **Primary direct end-of-line label.** Suppressed only if the last
   point itself cannot be located (no data). Otherwise always rendered.
3. **Recession-band label.** Suppresses competing y-ticks but never
   itself suppresses.
4. **Secondary direct end-of-line label.** Stacks with primary when
   close; suppressed if the secondary series itself was suppressed
   (units mismatch).
5. **Reference-rule label.** Suppressed when within 16px of any direct
   label. The dashed rule stays.
6. **Non-unit y-tick labels.** Suppressed within 12px of recession-band
   label.
7. **Annotation callout (Phase 2).** Suppressed when no candidate
   position has clear whitespace.

X-axis tick labels live in a dedicated row below the plot frame and
never collide with the above six families. They are not in the
hierarchy.

### Known edge cases not yet resolved

Documented for follow-up. None blocking v1.

1. **Steep terminus.** When the data line ends with a sharp rise or
   fall, the direct label sitting 10px to the right of the last point
   can read visually close to the prior data segment. The right gutter
   is data-free, so the label and line do not actually overlap, but the
   apparent crowding can read as collision. Mitigation: the 10px gap is
   the minimum; chart-builder may bump per-panel to 14px with
   art-director sign-off if the editorial argument requires.
2. **Many y-ticks suppressed near recession label.** If the recession
   label's y-coordinate happens to align with two consecutive y-ticks
   (rare; gridline density 3-5 vs band-label-line-1 means most builds
   have at most one collision), both ticks would hide. The current rule
   suppresses each independently; the editorial cost is at most a
   missing tick label, which the gridline itself still conveys.
3. **Three-or-more series.** PanelLiveChart renders at most two
   series. A three-series panel (e.g. Labour Panel 1 unrate + emprate
   + participation) lives outside PanelLiveChart and is responsible
   for its own multi-series stacking using L6 logic generalized.
4. **Direct label collides with adjacent panel's left-gutter ticks
   (small-multiples grid).** Not applicable in the v1 chartbook layout
   (each ChartbookUnit is full-width); flagged for Phase 2 small-
   multiples.
5. **Last point near the right plot frame edge.** When the dataset's
   final point sits less than `LABEL_GAP_X` (10px) inside the plot
   frame's right edge, the label still anchors at `lastX + 10` and
   crosses the frame into the right gutter (`M_R` = 96px). The frame
   stops at `PLOT_X1`; the gutter is data-free; legal placement.

---

## Resolutions: Q6 - Q9 (frontend-designer questions, 2026-05-11)

### Q6. Direct label phrasing per panel

**Decision: defer the case-by-case phrasing pass to a follow-up sweep
with writer; keep the current short forms in v1.** Direct labels are a
12-15px stamp at the line terminus; they tell the reader which series
their eye is on, not what the series means. The current set (`CPI Y/Y`,
`2y GoC`, `WTI`, `Brent`, `Core-trim`, `Core-median`, `PR inflows`,
`Net NPR`, `Shelter y/y`, etc.) reads as the publication's stenographic
register. A round of style-editor review for tone uniformity is a
Phase 2 polish, not a v1 blocker.

**Action.** None now. Queue a writer pass under "next sweep."

### Q7. Secondary-unit suppression

**Decision: keep the current behavior. Suppress the secondary series
when its unit disagrees with primary.** A panel that wants a true
dual-unit overlay (e.g. CPI Y/Y in % alongside USDCAD in price) needs
a per-panel dual-axis geometry; that is a chart-builder bespoke
component, not a PanelLiveChart responsibility.

**Rationale.** Section 5.3 already permits dual-axis charts but only
with art-director-signed per-chart visual specs (and a Plex Mono 12px
right-gutter tick treatment). Auto-rendering a misleading shared axis
when units don't match is the worst outcome. Suppression is the right
default; bespoke is the escape hatch.

**Action.** None. The `unitsMatch` guard stays.

### Q8. Recent-print annotation callout + leader

**Decision: defer to Phase 2 (Rule L7 above).** The collision algorithm
needed to do this safely - 4 candidate scoring + whitespace test - is
material code (~80 lines) and would re-introduce per-panel hand-tuning
that the PanelLiveChart collapse explicitly eliminated. The Vignelli
canon already prescribes that charts needing a hand-tuned annotation
become bespoke components (see GDP Panel 1, Labour Panel 1 redlines).
PanelLiveChart is the workhorse for the editorial-argument-by-line-
terminus case; an annotated chart should not go through it.

**Rationale.** Rule 11 of the canon-compliance checklist describes the
annotation. It is canon-required only for charts whose editorial
argument *needs* an anchored callout (e.g. "Apr print held at 2.1%,
fourth month at target"). Most PanelLiveChart consumers are surface
indicators where the latest-print dot + direct label already carry the
read; the annotation is editorial decoration that doesn't apply.

**Action.** PanelLiveChart does not render annotations in v1. The
algorithmic placement (Rule L7) is documented for the Phase 2
bespoke-annotation extraction.

### Q9. Categorical bar charts (GDP panel 3, Inflation panel 4)

**Decision: build a shared `PanelBarChart.astro` companion component
in Phase 2.** Lines for categorical data are wrong; the visual canon
calls for bars. PanelLiveChart's geometry (x = continuous time, y =
continuous value) cannot be patched into a categorical layout
without compromising the line case.

**Rationale.** The Vignelli register is precise about chart-type
discipline. A category-by-share chart (e.g. CPI components, Q3 share
of basket above 3%) reads as bars; rendering it as a line implies a
continuous trajectory that doesn't exist. Until `PanelBarChart` is
built, the affected panels (GDP Panel 3 contributions; Inflation Panel
4 sub-aggregate shares) should either remain as bespoke per-panel
components or route to `PanelEmpty` with a "data not yet wired"
reason. They should NOT continue to render through PanelLiveChart-as-
line.

**Action.**
- Queue `PanelBarChart.astro` as a Phase 2 deliverable. Same canvas
  (720x405), same Plex Mono y-ticks, same Manrope x-ticks, same MTA
  red dot/marker for the most-recent or anchor bar.
- Until then: chart-builder converts each affected panel to either a
  bespoke component (preferred for editorial-load panels) or
  `PanelEmpty` (for low-priority panels). Decision per-panel by
  art-director + chart-builder + editorial-director.

---

## Summary of follow-ups for chart-builder

Queued items (non-blocking; apply in the next maintenance pass):

- **None blocking from this redline pass.** Q1 confirms the existing
  breadth encoding. Q2 confirms filenames. Q3 confirms Panel 3 GDP
  aspect ratio. Q4 confirms existing panel-scoped BEM. Q5 confirms
  the xmlns removal already done.
- **Sweep check (one-pass):** grep production panels for any
  remaining `xmlns="http://www.w3.org/1999/xhtml"` on
  foreignObject children and remove if found.
- **Going forward:** new panels follow the Q2 naming convention,
  the Q3 aspect-ratio rule (16:9 for time-series, 4:3 for
  categorical), the Q4 BEM scope (`.panel-N-<shortname>__*`), and
  the Q5 xmlns omission.
