# Panel 3 -- Breadth (stacked composition + tilt-percentile ladder)

Status: v0.1. Author: chart-builder. **Hero chart of the page.**
Cites `design/basics-layer-template.md`, `design/design-system.md`
Section 5, and EDR Section 4.2 element 3.

## What this panel answers

EDR Section 4.2 element 3 (post May 2026 verification resolution):
share of CPI basket components above 3%, between 1-3%, and below 1%.
The four-state typology (broad-based pressure / softening / clustered /
polarized) is **retired as a forced classification** -- it remains
prose vocabulary for writer when the data clearly matches, but the
panel does **not** present it as an exhaustive partition.

Underneath the stacked composition, a **continuous |tilt|
percentile ladder** for edge cases: when the composition reads
"clustered near target" but the underlying distribution is actually
tilted (e.g., 70% near target but the remaining 30% all on one side),
the ladder catches it.

Reader leaves knowing (a) how broad inflation pressure is, and (b)
whether the breath is symmetric or one-sided.

## Plot vs D3 -- D3 + custom SVG

This is the page's hero. The composite (stacked composition above,
asymmetric percentile ladder below), the cross-canvas hover coupling
(scrubbing the time axis moves both), and the hand-tuned annotation
placement at regime cut-points all justify dropping out of Plot.
Shipped as a React island consuming D3 scales and hand-placed
annotations.

Total chart canvas: **432 x 360 CSS px** (taller than other panels to
hold both sub-canvases). Stacked composition: 432 x 220. Tilt ladder:
432 x 100. 40px reserved between for the divider rule and the ladder
title.

## Panel chrome

- **Eyebrow:** `BREADTH` (`series-2` section accent).
- **Title slot:** writer-supplied (e.g., *"Three in ten basket items
  still printed above 3% in March, with the remainder clustered close
  to target."*).
- **Deck:** writer-supplied (e.g., *"Composition is back to its
  pre-shock shape; the tilt below shows whether the remaining
  pressure is symmetric or one-sided."*).
- **Vintage stamp:**
  ```
  AS OF
  Apr 16, 2026
  Reference: Mar 2026
  ```
- **Source line:** `Source: Statistics Canada Table 18-10-0004-01,
  ~170 basket components, basket weights via CPI methodology
  document; macro-research-department construction.`
- **Methodology link:** important here. Drawer contents: component
  list, basket-weight source and vintage, cut-point definitions
  (above 3% / 1-3% / below 1% Y/Y on the SA equivalent or NSA-as-
  shipped), tilt calculation (per below), May 2026 verification note
  that retired the four-state typology, and the chart's own
  classification-restraint stance (composition is the data; "states"
  are prose).

## Data inputs

| Input                          | Source                                       | Frequency | Catalog key       |
|--------------------------------|----------------------------------------------|-----------|-------------------|
| Per-component CPI Y/Y          | StatCan Table 18-10-0004-01 (~170 components)| Monthly   | (backend; not yet registered) |
| Basket weights                 | StatCan CPI basket update                    | Periodic  | (backend)         |
| Tilt magnitude per component   | Derived: signed distance from 2% target      | Monthly   | (backend)         |
| Historical tilt distribution   | Derived: P10/P50/P90 of |tilt| across history| Static    | (backend, precomputed) |

Backend-engineer ships two tidy frames:

- `breadth_composition` -- `{date, share_above3, share_1_3, share_below1,
  share_missing}`. Shares are basket-weighted, sum to 1.0 plus a
  small missing slice for components with no current print.
- `tilt_ladder` -- `{date, tilt_p10, tilt_p25, tilt_p50, tilt_p75, tilt_p90,
  tilt_current, tilt_hist_p10, tilt_hist_p50, tilt_hist_p90}`. The
  `_current` is this month's median |signed deviation|; the `_hist_*`
  are the long-run distribution of the same statistic.

**Gating:** per EDR Section 4.2 and panel README open question, this
panel is gated on basket-weight reproducibility. If unavailable in
v1, ships with placeholder treatment (see Editorial notes).

## Chart type

### Upper sub-canvas: stacked composition

**Stacked area, three bands.**

- X-axis: monthly, last 8 years (96 months). The 8-year window is
  deliberate -- it shows pre-2020 normal, the 2022 peak, the 2023-24
  cooling, and the current state. This is the only basics panel with
  an 8-year window; the breadth story is a regime story.
- Y-axis: share of basket weight, 0 to 1 (rendered as 0% to 100%).
  Gridlines at 25%, 50%, 75% in `rule-faint`. No zero line (it is
  the x-axis baseline).
- **Cut-point reference lines** at the 1% and 3% Y/Y thresholds do
  **not** apply here (that is per-component Y/Y, not basket share).
  No threshold lines on this sub-canvas.

### Lower sub-canvas: tilt-percentile ladder

**Asymmetric ladder/violin showing the historical distribution of
|tilt| with the current month highlighted.**

- A horizontal lane (100px tall, full panel width) showing the
  long-run distribution of median |tilt| as a faded `surface-sunk`
  fill with `rule` 1px upper/lower boundary.
- Tick marks at the historical P10, P25, P50, P75, P90 in
  `ink-faint` `micro` labels.
- A single solid 2px vertical mark in `series-2` (the section
  accent -- this is the one place data uses the accent, because the
  argument the chart is making here is editorial: "look at the edge
  case the composition misses") at the current month's tilt
  percentile.
- Adjacent annotation in `body-sm` weight 500 `ink` describing the
  percentile rank: e.g., *"Tilt sits at the 78th percentile of its
  history -- pressure that remains is one-sided."* Wording owned by
  writer; placement here.

## Series colors

### Composition bands (proposed -- README open question 1)

Per the open question, the recommendation is a **single-hue
sequential ramp** to avoid the green/red valence dispute:

- **Above 3%:** sequential orange stop 4: `#C9772A` (= `series-2`)
  at 60% opacity fill, 1px upper edge in `series-2` solid.
- **Between 1-3%:** sequential orange stop 2: `#F0CDA0` at 60%
  opacity fill, 1px upper edge in `#DDA76A` solid.
- **Below 1%:** sequential orange stop 1: `#FBEBDA` at 60% opacity
  fill, 1px upper edge in `#F0CDA0` solid.
- **Missing slice** (if non-zero): `rule-faint` `#ECE7DC` fill with
  diagonal hatching at 50% density, `ink-faint` 1px upper edge.

Fallback if art-director rejects the sequential ramp: `neg-soft` /
`surface-sunk` / `pos-soft` per README open question -- legible
semantic encoding, but conflates with editorial valence.

### Tilt ladder

- Historical distribution lane fill: `surface-sunk` (#F4F0E8).
- Lane boundaries: 1px `rule`.
- Percentile ticks: 1px `ink-faint`.
- Current-month marker: 2px `series-2` solid.

## Direct labels and annotations

### Stacked composition

- **Right terminus labels** for each band, placed at the right edge
  of the canvas in the band's edge color, weight 500 `label`:
  `Above 3%`, `1-3% (target band)`, `Below 1%`. Labels are
  vertically centered on each band's current width at the rightmost
  time point.
- **Annotations on regime cuts:** at the 2022 peak (highest
  share-above-3% in window) and the 2023 inflection (first month
  share-above-3% fell below 50%, if applicable). `body-sm` weight 400
  `ink` for the primary annotation; `ink-muted` for secondary. Leader
  lines 1px `ink-muted`, no arrowhead, single-elbow.
- **A horizontal reference line at 0.50** (50% share) in 1px
  `ink-faint` dashed `2 2`. This is the "more than half the basket"
  threshold -- editorially meaningful for the share-above-3% band.
  Right-gutter rotated label `Majority share` in `micro` `ink-faint`.

### Tilt ladder

- Sub-canvas label at top-left: `TILT MAGNITUDE -- HISTORICAL
  DISTRIBUTION` in `label` weight 500 `ink-muted`, 0.04em letter-
  spacing. This is the affordance that explains the second canvas.
- Percentile annotations at P10, P50, P90 in `micro` `ink-faint`
  along the lane.
- Current-month percentile callout (writer's wording) anchored to
  the current marker.

## Cross-canvas coupling (interaction)

The two sub-canvases share the time axis. On hover/scrub:

- Vertical line in 1px `ink-muted` follows the cursor across the
  upper sub-canvas at the hovered date.
- Tilt marker in the lower sub-canvas updates to that date's tilt
  percentile.
- A tooltip in `body-sm` `ink` on `surface` 1px `rule` shows:
  ```
  March 2026
  Above 3%:  29%
  1-3%:      54%
  Below 1%:  17%
  Tilt:      P78 (one-sided)
  ```

Default state (no hover) shows current month. Touch: tap to lock,
tap outside to release.

## Recession bands

`ink` 6% opacity over 2020Q1-Q2 spans **both sub-canvases** (the
band extends through the full 320px chart height; the divider rule
between sub-canvases is omitted in recession columns, or rendered at
`ink-faint` instead of `rule`, so the band reads continuously).

## Latest-print callout

The three composition percentages stacked, with the tilt percentile
as the fourth element:

- **Three big numbers**, comma-separated on one row:
  `29% / 54% / 17%`. `display-md` serif weight 600 tabular `ink`,
  divider slashes in `ink-faint`.
- **Unit row:** `Share of CPI basket: above 3% / 1-3% / below 1%,
  March 2026`. `body-sm` `ink-muted`.
- **Tilt row:** `Tilt: P78 (one-sided)`. `label` weight 500 `ink`,
  with `P78` in mono.

No consensus pipe on this panel -- breadth is not consensus-anchored.

## Editorial-status fallback if gating fails

If basket-weight reproducibility is unavailable for v1, the panel
ships with:

- Upper sub-canvas: empty stacked area at full width in
  `rule-faint`, with diagonal hatching across all three bands and
  a single annotation centered: *"Composition data available with
  the May 2026 basket refresh -- methodology resolved."*
- Lower sub-canvas: hidden.
- Editorial status line in the callout slot: *"Breadth composition
  defers to v1.5 pending basket-weight reproducibility."*
- Vintage stamp shows the gating decision date.

This is **not** the default; v1.5 is the target. Backend-engineer
confirms before render.

## Responsive variants

- **`md` (<960px):** panel widens; both sub-canvases scale. Annotations
  preserved.
- **`sm` (<640px):** lower sub-canvas (tilt ladder) **hides**.
  Composition compresses to ~340px wide. A small affordance below
  the chart: `Tap for tilt detail >` in `label` weight 500 `ink`
  with `accent` underline. Tap opens a fullscreen overlay (not a
  tooltip) with the tilt ladder at full size. This is the one place
  on the page where mobile gets a different interaction; the tilt
  ladder is too small to be legible at 340px.

## Editorial notes for art-director

- **The composition coloring is the open question.** Strong
  recommendation: sequential orange ramp. Diverging semantic
  (neg-soft / surface-sunk / pos-soft) is legible but conflates with
  editorial valence the EDR explicitly wants left to prose.
- **The tilt ladder is the panel's editorial argument.** Without it
  the panel collapses to "stacked area, fine." With it, the panel
  says "composition alone misses one-sidedness, here is the catch."
  The May 2026 retire-the-four-state resolution is what motivates
  the tilt -- losing the partition means we must surface the edge
  case it would have caught.
- **The accent (series-2) is used on data here.** Per design-system.md
  Section 5, this requires art-director approval and is justified
  only when the chart makes an editorial argument about one series.
  The current-month tilt marker is exactly that case. Confirm.
