# Inflation Basics Page -- Per-Panel Chart Specs

Status: v0.1. Author: chart-builder (Wave 3 brief W3-CB2).
Last updated: 2026-05-11.

This directory holds the per-panel chart visual specs for the **Inflation
basics page**, per `editorial/dashboard_purpose.md` Section 4.2. Specs cite
`design/design-system.md` (canon) and `design/basics-layer-template.md`
(panel grammar). Wording is owned by `writer`; data is provided by
`backend-engineer` from the catalog (`pipeline/catalog/`).

Six panels, in EDR-fixed order. Section accent: `series-2` (#C9772A,
burnt orange). Section accent appears in panel eyebrows only -- never on
data. Page background `paper`; cards on `surface` with 1px `rule` border,
4px radius, no shadow.

## Manifest

| #  | Panel                       | File                                | Chart type                                | Plot vs D3              |
|----|-----------------------------|-------------------------------------|-------------------------------------------|-------------------------|
| 1  | Headline CPI                | `panel-1-headline-cpi.md`           | Dual-line (Y/Y + 3M AR) time series       | Observable Plot         |
| 2  | BoC preferred core trio     | `panel-2-core-trio.md`              | Two-line time series + faded historical   | Observable Plot         |
| 3  | Breadth (stacked composition) | `panel-3-breadth.md`              | Stacked-area + tilt-percentile ladder     | D3 + SVG (hero)         |
| 4  | Sub-aggregates              | `panel-4-sub-aggregates.md`         | Small-multiple bar/line, shelter cut-out  | Observable Plot         |
| 5  | Inflation expectations      | `panel-5-expectations.md`           | Two-stack: CSCE lines + BOS bucket stack  | Observable Plot         |
| 6  | Pass-through watch          | `panel-6-pass-through.md`           | Side-by-side dual-axis strip charts       | Observable Plot         |

## Plot-vs-D3 rationale

- **Panel 3 (Breadth)** is the only hero chart. It is a composite (stacked
  composition above; continuous tilt-percentile ladder below) with custom
  vertical synchronization, custom annotation typography on regime cuts,
  and a hover-coupled brush across both sub-canvases. Observable Plot's
  marks can render each piece, but the cross-canvas coupling and the
  asymmetric tilt-ladder require enough custom SVG that it ships as a
  React island with D3 scales and hand-tuned annotation positions. This
  is the panel that earns its keep -- the May 2026 retire-the-four-state
  resolution is editorially central, and the visual must read as
  "composition with edge-case affordance," not "stacked area."

- **Panels 1, 2, 4, 5, 6** all sit inside Plot's sweet spot
  (time series with direct labels, faded historical anchor, small
  multiples, stacked bars). No bespoke layout, no unusual interaction.

- **Plotly is not used anywhere on this page.**

## Cross-panel rules (apply to all six)

These come from `design/basics-layer-template.md` Section 3 and
`design/design-system.md` Section 5. Each per-panel spec inherits them
silently; only deviations are called out per-panel.

### Canvas

- Desktop panel-content width: **432 CSS px** (panel 496px minus 32px
  padding each side, per template Section 2).
- Default aspect ratio: **16:9** for time-series (432 x 243 plot area),
  **4:3** for the breadth-stacked-area, **2:1 squat** for the
  pass-through strip charts to allow side-by-side at panel width.
- Inside the canvas: 36px left gutter (y-tick labels), 48px right gutter
  (direct labels at line termini), 24px top, 28px bottom (x-tick labels).

### Axes and grid

- Y-axis: no axis line; 4-6 horizontal gridlines in `rule-faint`
  (#ECE7DC); ticks inferred. Y-tick labels `micro` `ink-faint`.
- X-axis: 1px `rule` bottom rule, 4px outward ticks; labels `micro`
  `ink-faint`. Year labels at January only; quarters labelled only when
  the window is short enough that monthly density allows it.
- Zero line: 1px `ink-muted` when negative values are in range. The
  BoC's 2% target line: 1px `ink-faint` dashed `4 2`, with rotated
  `micro` `ink-faint` label `BoC 2% target` placed at the right gutter,
  baseline aligned to the line.
- 1% and 3% lines: rendered only on the breadth panel (the cut-points
  for the composition). 1px `rule` dashed `2 2`. Tick labels at right.

### Series colors

Default mapping for this section's chart palette:

- `series-1` (#1F4E79, deep blue): **headline CPI** and primary focus
  series in dual-line panels.
- `series-2` (#C9772A, burnt orange): the **section accent**; appears
  in panel eyebrows only. Data uses `series-2` only when the chart is
  making an editorial argument about a single series (sparingly, panel 6
  USDCAD overlay where the argument is the pass-through).
- `series-3` (#5B7553, sage): **core-trim**.
- `series-4` (#7A3E65, plum): **core-median**.
- `series-7` (#4A4F57, slate): faded historical anchor (core-common),
  contextual lines (CPI services as comparator on wage band), and
  "rest-of-category" baselines.

### Recession bands

`ink` at 6% opacity, sitting behind gridlines and behind data. Labelled
only on the most-recent or most-relevant recession with `micro`
`ink-faint` text at the top edge: `Recession (2020Q1-Q2, C.D. Howe BCC)`.

### Direct labels

At line termini, in series color, weight 500, `label` (13px). No
legends unless a stacked-composition chart requires a category swatch
strip (panel 3, panel 5).

### Annotations

`body-sm` (15px) Inter weight 400, `ink` for primary, `ink-muted` for
secondary. 1px `ink-muted` leader, no arrowhead, single-elbow. Placed
in white space. Wording owned by `writer`; placement owned here.

### Vintage stamp

Top-right of panel card. Two-line variant is the default for this page
(release date + reference period). When two source families ship at
different cadences (panel 5: CSCE + BOS), the stamp expands to three
lines.

### Source line

Bottom of panel, `micro` `ink-faint`, prefix `Source:`, primary
Canadian source first, derived inputs semicolon-separated after.

### Methodology link

Right-aligned on the source-line row. Required on **every** panel,
including those with trivial methodology (e.g., panel 1 cites only
StatCan vector 41690914). For panels with construction (panel 3
breadth, panel 4 derived ex-aggregates), the drawer is non-trivial.

### Responsive variants

Two breakpoints to design for per panel:

- **`md`/`sm` (<960px):** single-column layout puts the panel at body-
  column width (max 680px). Charts scale up proportionally; the 16:9
  aspect holds; direct labels stay at the right.
- **`sm` (<640px):** panel at viewport-minus-32. Charts compress to
  ~340px wide. Per-panel small-screen rules in each spec:
  - Reduce number of direct labels (drop secondary series labels).
  - Year labels every 2 years instead of every 1.
  - Annotation copy collapses to its anchor word (writer's call).
  - Side-by-side strip charts (panel 6) stack vertically.
  - Breadth panel's tilt-percentile ladder hides below `sm`; only the
    stacked composition renders, with a "Tap for tilt detail" affordance.

## Files

- `panel-1-headline-cpi.md`
- `panel-2-core-trio.md`
- `panel-3-breadth.md` (hero)
- `panel-4-sub-aggregates.md`
- `panel-5-expectations.md`
- `panel-6-pass-through.md`

## Open questions for art-director

1. **Panel 3 (Breadth) -- color encoding for the three composition
   bands.** Spec proposes `neg-soft` (#EAD3CE) for the above-3% band,
   `surface-sunk` (#F4F0E8) for the between-1-3% target band, and
   `pos-soft` (#D4E5D8) for the below-1% band. This reuses the
   semantic-soft palette but inverts the conventional "high inflation
   = neg-soft" reading depending on whether the reader interprets
   above-3% as bad. Per design-system.md Section 4 (consensus-color
   rule): color encodes the direction of the print, not the editorial
   valence. Confirm `neg-soft` for above-3% is acceptable, or fall back
   to a single-hue sequential ramp (sequential orange) and let
   typography carry the editorial reading. Recommend: ramp.

2. **Panel 2 (Core trio) -- common as faded historical anchor.** Spec
   places common as a 1.5px `series-7` slate line rendered only on
   hover or as a static "ghost" line at 30% opacity always-visible.
   The latter respects the EDR note that common is a historical
   anchor (visible) but BoC-deprioritized (recessive). Recommend the
   30%-opacity always-visible read; flag for art-director.

3. **Panel 5 (Expectations) -- two distinct cadences (CSCE quarterly,
   BOS quarterly but published two weeks after each rate decision).**
   The vintage stamp expands to three lines. Spec proposes stacking
   CSCE and BOS as separate sub-charts within the panel (small
   multiples within the panel), not overlaid on the same plot.
   Confirm the within-panel multiple is the right read versus a single
   panel with overlaid lines + a bucket-bar inset.

4. **Panel 6 (Pass-through) -- side-by-side at panel width.** At 432px
   panel content width, two strip charts side-by-side gives ~196px per
   strip after gutter. That is tight for a 2-line strip chart with
   direct labels. Two options: (a) keep side-by-side at panel width
   with abbreviated termini, or (b) stack the two strip charts
   vertically inside the panel. Spec defaults to (a) for desktop and
   (b) for `<md`. Confirm.

## Open questions for backend-engineer (data prep)

These are flagged for `backend-engineer` and `editorial-director` to
resolve before render. None of them are visual decisions; they affect
whether a spec can be implemented.

1. **Breadth composition (panel 3) requires per-component CPI Y/Y for
   all ~170 basket components from Table 18-10-0004-01 to compute
   share-above-3% / 1-3% / below-1%.** Catalog currently registers
   only aggregate sub-series. Per EDR Section 4.2 element 4, this is
   gated on "basket-weight reproducibility." If unavailable in v1, the
   panel ships as a placeholder with the prose note that the
   composition is deferred to v1.5; we still render the chart
   skeleton with `surface-sunk` empty bands and an `ink-faint`
   "Coming with the May 2026 basket refresh" annotation. Confirm
   handling.

2. **Tilt-percentile ladder (panel 3 sub-canvas)** requires a
   continuous tilt magnitude computed across components. The
   computation is `backend-engineer` territory; chart accepts the
   percentile rank per current month and the historical distribution
   (P10/P50/P90 anchors).

3. **3M annualized core trim/median (panel 2)** requires recoverable
   NSA core index levels. EDR notes this is probe-pending; if NSA
   levels are not recoverable, panel 2 ships Y/Y only (no 3M AR
   strip).

4. **Ex-energy goods CPI and ex-shelter services CPI (panel 4, panel
   6)** require basket-weighted derivations. EDR gates on
   reproducibility script. If unavailable, panel 4 ships all-goods
   and all-services with prose flag; panel 6 defers to v1.5 entirely
   with placeholder.

5. **Wage growth series for panel 6** -- LFS-Micro Y/Y is the EDR
   anchor (`pipeline/catalog/boc_series.py::lfs_micro`).
   Backend-engineer prepares the monthly aligned join with services-
   ex-shelter CPI.

End of README.
