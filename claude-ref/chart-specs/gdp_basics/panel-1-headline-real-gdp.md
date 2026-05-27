## Panel 1 -- Headline real GDP

Status: spec-only, v0.1. Owner: chart-builder.

EDR element: 4.1 #1. Template ref: basics-layer-template.md Section 9,
Panel 1.

---

### Purpose

Dual-frequency state-of-the-headline: monthly m/m % alongside quarterly
Q/Q SAAR over the last 5 years, with revision direction surfaced on the
most recent monthly point.

### Data inputs

From `pipeline/catalog/statcan_series.py`:

- `gdp_monthly` (vector `v65201210`, Table `36-10-0434-01`) -- monthly
  real GDP by industry, chained 2017$, SAAR. Backend-engineer derives
  m/m % series from this and writes `gdp_monthly_mom` column.
- `gdp_quarterly` (vector `v62305752`, Table `36-10-0104-01`) -- quarterly
  real GDP by expenditure, chained 2017$, SAAR. Backend-engineer derives
  Q/Q SAAR % series and writes `gdp_quarterly_qq_saar` column.

Backend output: `data/derived/gdp_basics/panel-1.csv` with columns:
`date` (monthly), `mom_pct` (nullable on non-print months), `qq_saar_pct`
(nullable except quarter-end months when the quarterly print exists),
`mom_pct_prior_vintage` (nullable; only populated on the most recent
monthly observation if the prior vintage differs from current).

Sibling `panel-1.meta.json` carries: `as_of_date` (release date),
`reference_period` (e.g., `Mar 2026`), revision flag, source table IDs.

### Chart type

**Dual-frequency time series, single y-axis.**

- Monthly m/m % as thin vertical columns. Column width = ~50% of the
  per-month x-spacing (so columns look like bars, not a histogram block).
- Quarterly Q/Q SAAR as a 1.5px solid line, weight 500, with filled 3px
  markers at each quarter-end month.

Single shared y-axis in percent.

Plot/D3 choice: **Observable Plot**. `Plot.barY` (or `Plot.rectY` with
explicit bar widths) + `Plot.line` + `Plot.dot` overlaid on a `Plot.plot`.
The dual-frequency single-axis layout is a standard Plot composition.

### Axes

- **X.** Monthly axis spanning ~60 months ending at the most recent
  monthly print. Tick interval: every January (year start), label `YYYY`.
  Minor ticks at quarter starts (4 per year), unlabeled, 2px outward.
  Axis line in `rule` (`#D9D3C7`), 1px.
- **Y.** Percent. Range: data-driven, padded to symmetric around zero
  (e.g., `[-1.2, +1.2]` if data is `[-1.0, +1.0]`); minimum range
  `[-1.0, +1.0]` so a flat period does not visually exaggerate.
  Zero line: 1px `ink-muted` (`#4A4F57`). Horizontal gridlines at
  every 0.5pp in `rule-faint` (`#ECE7DC`), 4-6 total.
  Unit annotation: `% per month / quarter` at top-left of plot area,
  `micro` `ink-faint`. (Yes, both units share the axis; the prose +
  direct labels make clear which is which.)
- **Zero line.** Required (negative values likely in 5-year window).

### Series colors

- Monthly m/m bars: `series-1` (`#1F4E79`, deep blue, section accent).
- Quarterly Q/Q SAAR line: `series-1` 1.5px solid; line marker dots
  same color, 3px filled.
- Monthly bar that is the *most recent print* (the m/m % for the latest
  month): same fill, but with a 1px `surface` (`#FFFFFF`) outline to
  separate it from the prior-month bar. Optional.

Color logic: this is a one-narrative panel (the monthly print + the
quarterly context). Both series in the same color reinforces "same
data, different frequency view." The y-position carries the value;
the column-vs-line carries the frequency.

### Direct labels

- `Monthly m/m` -- placed in whitespace above the bar series, near the
  middle-right of the plot. Inter `label` (13px) weight 500, color =
  `series-1`. Avoids the most recent bar so it does not collide with
  the revision marker.
- `Quarterly Q/Q SAAR` -- placed `s-2` (8px) to the right of the line's
  right terminus. Same type treatment.

### Annotation slots

- **Most-recent print annotation.** Always rendered. Anchors to the
  most recent monthly bar. Format (wording is writer's):
  `Mar 2026 / +0.2% m/m / Revised up from +0.1%`.
  Inter `body-sm` (15px) weight 400 for the date and value, weight 500
  for the revision verb. Color: `ink` for value, `pos`/`neg`/`ink-faint`
  for the revision verb. 1px `ink-muted` leader, single-elbow, ending
  4px short of the bar top.
  Placement: upper-right whitespace, anchored to the top of the most
  recent bar. If the print is positive, annotation sits above; if
  negative, below.

- **Recession band label slot.** If the 5-year window includes the
  2020Q1-Q2 BCC recession, label at top edge in `micro` `ink-faint`:
  `Recession (2020Q1-Q2)`. Otherwise no recession-band label.

- **Optional consensus tick.** Open question for AD (see manifest).
  If rendered: 1px `ink-faint` short horizontal tick at the consensus
  value at the most recent month's x-position, ~10px long, centered on
  the bar.

### Recession bands

C.D. Howe BCC dated recessions in the 5-year window. As of 2026-05-11,
this is the 2020Q1-2020Q2 band only. Render: `rgba(21,23,26,0.06)`
rectangle behind data, full y-axis height. Label at top edge per
above.

### Revision visual treatment

Per template Section 5: the most recent monthly bar shows revision
state on the bar itself, not as an open-circle marker (this is the bar-
chart variant). Implementation:

- If `mom_pct_prior_vintage` is present and differs from `mom_pct` by
  > 0.05pp:
  - Draw a 1px dashed `ink-faint` (`2 2`) horizontal line at the
    prior-vintage value, spanning the most recent bar's width.
  - The bar itself draws to the current value as normal.
  - The annotation (above) names the revision direction.
- If unrevised or revision <= 0.05pp: no dashed line; annotation still
  renders the date and value but omits the revision clause.

The open-circle treatment (template Section 5) applies to *line-chart*
panels (panel 4, panel 5). On the bar in panel 1, the dashed line is
the equivalent affordance.

### Responsive variants

- **xl / lg (desktop / large tablet).** Full 60-month window. All
  ticks, all annotations.
- **md (tablet narrow, 640-959px).** Drop to 36-month window. Same
  marks. Annotation may need to drop the revision clause if it pushes
  the leader past the plot edge.
- **sm (mobile, <640px).** Drop to 24-month window (or last 8 monthly
  bars + last 4 quarterly markers, whichever spans the longer time
  window). Direct labels move to a single-row legend below the chart
  in `micro` size -- this is the one place we permit a legend on a
  basics panel, because the direct-label placement does not survive
  mobile compression. Annotation collapses to date + value only;
  the revision clause moves to the callout below the chart (per
  template Section 5, point 2).

### Open questions

For art-director:
- Optional consensus tick on the most recent bar -- yes / no? Spec
  defaults to no.
- On `sm`, is the legend fallback OK, or should we drop a series
  instead (keep monthly, drop quarterly)? Spec recommends legend
  fallback; the panel's editorial point is the dual-frequency
  comparison.

For backend-engineer:
- Confirm `mom_pct_prior_vintage` is computable as
  `(prior_vintage_level / prior_vintage_level.shift(1) - 1) * 100`
  from the previous monthly release file. If the prior vintage is
  not retained, spec degrades to "no revision visual rendered,
  callout still reports the revision."
