## Panel 4 -- Per-capita real GDP

Status: spec-only, v0.1. Owner: chart-builder.

EDR element: 4.1 #4. Template ref: basics-layer-template.md Section 9,
Panel 4.

---

### Purpose

The cut the aggregate headline obscures. Side-by-side aggregate real
GDP Y/Y vs per-capita real GDP Y/Y, over the last 8 years, with the
consecutive-quarter-contraction count called out on the per-capita
line.

### Data inputs

From `pipeline/catalog/statcan_series.py`:

- `gdp_quarterly` (v62305752, Table 36-10-0104-01) -- quarterly real
  GDP level.
- `pop_total` (v1, Table 17-10-0009-01) -- quarterly total population
  (reconciliation target ~41.5M for Q1 2026).

Backend-engineer derives:
1. Aggregate real GDP Y/Y: `(level / level.shift(4) - 1) * 100`.
2. Per-capita real GDP level: `gdp_level / pop_total`.
3. Per-capita real GDP Y/Y: `(per_capita / per_capita.shift(4) - 1) * 100`.
4. Consecutive-quarter contraction count on per-capita Y/Y (the streak
   of consecutive quarters where per-capita Y/Y < 0).

Backend output: `data/derived/gdp_basics/panel-4.csv` with columns:
`date` (quarterly), `aggregate_yoy_pct`, `per_capita_yoy_pct`,
`contraction_streak` (integer, populated only on the most recent row).

Window: 2018Q1 through latest available quarter (~8 years, matching
panel 2).

### Chart type

**Two-line time series, single y-axis (% Y/Y).**

- Aggregate Y/Y: 1.5px solid line, `series-7` (slate, contextual).
- Per-capita Y/Y: 1.5px solid line, `series-1` (deep blue, focus).

Both lines carry 3px filled markers at every quarterly point. Most
recent point on each line: 4px filled marker with 1px `surface` ring.

Plot/D3 choice: **Observable Plot**. Two `Plot.line` marks + `Plot.dot`
overlays. Straightforward.

### Axes

- **X.** Quarterly axis, 8 years. Year-start ticks labeled `YYYY`,
  quarter ticks unlabeled. Axis line `rule` 1px.
- **Y.** Percent Y/Y. Range data-driven, padded ~20% above/below
  observed; minimum range `[-3, +5]`. Zero line: 1px `ink-muted`
  (required -- per-capita series will spend time negative). Horizontal
  gridlines every 1pp in `rule-faint`. Unit annotation `% Y/Y` at top-
  left in `micro` `ink-faint`.

### Series colors

Two-series-with-comparison convention:
- Aggregate Y/Y: `series-7` (`#4A4F57`, slate). Context, recedes.
- Per-capita Y/Y: `series-1` (`#1F4E79`, deep blue). Focus, the story.

### Direct labels

At line termini, `s-2` (8px) right of last data point, Inter `label`
(13px) weight 500, color = series color:
- `Aggregate`
- `Per-capita`

### Annotation slots

- **Consecutive-quarter contraction annotation.** If
  `contraction_streak >= 2` on the most recent per-capita point,
  render an annotation anchored to the most recent per-capita marker:
  
  > *7 consecutive quarters of per-capita contraction*
  
  Wording is writer's; chart-builder reserves the slot. Inter
  `body-sm` 15px weight 500 `ink`. Placement: lower-right whitespace
  if per-capita line is currently negative, upper-right if positive.
  1px `ink-muted` leader, single-elbow, ending 4px short of the
  marker.

- **Divergence emphasis.** Where aggregate Y/Y > 0 and per-capita
  Y/Y < 0 (the recent regime), a 1px `ink-faint` dashed `2 2`
  vertical guide line drops from the aggregate marker down to the
  per-capita marker on the most recent point, with a small
  `mono-sm` label at the midpoint showing the gap (e.g., `-2.0pp
  gap`). Optional; AD confirm.

- **Recession band label.** `Recession (2020Q1-Q2)` at top edge of
  the 2020 band in `micro` `ink-faint`.

### Recession bands

2020Q1-Q2 BCC band, `rgba(21,23,26,0.06)`, full y-height.

### Revision visual treatment

Both lines: open-circle treatment per template Section 5 on the most
recent point if revised.

- Per-capita revision: triggers a revision marker. The denominator
  (`pop_total`) revises rarely (StatCan publishes intercensal
  revisions); when the denominator revises, the per-capita series is
  revised across multiple back-quarters. Per template Section 5,
  multi-period revisions get an inline footnote annotation:
  > *Also revises 2025Q3-Q4 per-capita estimates downward by 0.1pp
  > each (population denominator revision).*
  
  This sits in chart whitespace, `body-sm` italic `ink-muted`,
  anchored only by proximity (no leader). Wording is writer's.

### Callout treatment

Numeric callout, with a special-case: no surprise field. Per template
Section 4 ("When there is no surprise to show"), per-capita is a
derived series with no direct consensus forecast. The callout reads:

- Big number: per-capita Y/Y (e.g., `-1.0%`)
- Unit: `year-over-year, Q1 2026`
- Direction row: `[arrow down] 7 consecutive quarters of contraction`
  (no pipe, no surprise verb, no `[c]`/`[m]` subscript).

Page-template logic handles the collapsed direction row; chart-
builder ensures the chart's annotation does not duplicate the
streak count that the callout already shows.

### Methodology link (important here)

Per template Section 7, this panel's methodology drawer is non-trivial.
Per-capita construction has a denominator choice: mid-period vs end-
period population estimate, total vs working-age. The drawer text
(writer + backend-engineer co-author) names which denominator is used
and why.

### Responsive variants

- **xl / lg.** Full 8-year window, both series, all annotations.
- **md.** 6-year window. Drop the divergence-guide vertical line
  if rendered.
- **sm.** Full 8-year window retained (only two lines, no clutter).
  Direct labels: both labels on a single row above the chart in
  `micro` size if line-terminus placement runs off the right edge.
  Streak annotation collapses to a 1-line callout below the chart.

### Open questions

For art-director:
- Divergence vertical guide on the most recent point -- include or
  omit? Spec defaults to omit (the consecutive-streak annotation
  carries the divergence story).
- Per-capita as `series-1` (focus) vs aggregate as `series-1`. Spec
  follows EDR ("per-capita is the cut the headline obscures") and
  makes per-capita the focus.

For backend-engineer:
- Confirm the population denominator (mid-period vs end-period).
  Spec assumes mid-period (matches OECD convention).
- Confirm the contraction-streak column is computed and published
  on the latest row only (or for every row, with chart-builder
  reading the last value).
- Multi-period revision handling: confirm the panel-4.meta.json
  carries a `revised_periods[]` list for the inline footnote
  annotation to render off.
