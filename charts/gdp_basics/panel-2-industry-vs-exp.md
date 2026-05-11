## Panel 2 -- Industry vs expenditure cross-check

Status: spec-only, v0.1. Owner: chart-builder.

EDR element: 4.1 #2. Template ref: basics-layer-template.md Section 9,
Panel 2.

---

### Purpose

Eye-comparable two-line view of the two GDP cuts (monthly by industry,
quarterly by expenditure) so a reader can see at a glance whether the
two cuts agree on direction and approximately on level.

### Data inputs

From `pipeline/catalog/statcan_series.py`:

- `gdp_monthly` (v65201210, Table 36-10-0434-01) -- monthly real GDP
  by industry, level (chained 2017$, SAAR, indexed downstream).
- `gdp_quarterly` (v62305752, Table 36-10-0104-01) -- quarterly real
  GDP by expenditure, level.

Backend-engineer indexes both to a common base, **2019Q4 = 100**, and
publishes `data/derived/gdp_basics/panel-2.csv` with columns:
`date` (monthly axis), `industry_idx` (monthly value, indexed),
`expenditure_idx` (nullable except quarter-end months, indexed,
step-held forward across the quarter in a separate column
`expenditure_idx_step` for the visual). Both columns 2019Q4 = 100.

Window: 2018Q1 through latest available monthly point (~8 years).
This window straddles the 2020 recession so the band is meaningful.

### Chart type

**Two-line overlay, single y-axis (indexed level).**

- Industry: continuous monthly line, 1.5px, `series-1`.
- Expenditure: step-line (each quarterly value held flat across the
  quarter's three months), 1px dashed `2 2`, `series-7` (slate).
  Quarter-end month markers as 3px filled dots.

Plot/D3 choice: **Observable Plot**. `Plot.line` + `Plot.lineY` with
`curve: "step-after"` for the expenditure line. Simple primitives.

Why a step line for expenditure: quarterly data on a monthly x-axis
needs a visual treatment that does not pretend to monthly resolution.
The step holds the level until the next quarterly print, which is the
honest visual.

### Axes

- **X.** Monthly axis from 2018Q1 to latest monthly print. Year ticks
  labeled `YYYY`. Quarter ticks unlabeled. Axis line `rule` 1px.
- **Y.** Index, 2019Q4 = 100. Range padded above and below observed
  data; ~`[92, 108]` typical. Gridlines every 2 index points in
  `rule-faint`, 4-6 lines. No zero line (origin is 100, not 0).
  Reference line at 100: 1px `ink-faint` (`#7A7F88`), dashed `4 2`,
  labeled `2019Q4 = 100` at the right side in `micro` `ink-faint`.

### Series colors

- Industry: `series-1` (`#1F4E79`, deep blue, lead).
- Expenditure: `series-7` (`#4A4F57`, slate, contextual).

The two-series-with-comparison convention from design-system Section 5:
one focus + one context. Industry is the focus because it is the
monthly headline; expenditure is the slower, smaller-print companion.

### Direct labels

Both at line termini, placed `s-2` (8px) right of the last data point:
- `By industry` (monthly), `series-1`.
- `By expenditure` (quarterly, step-held), `series-7`.

Inter `label` (13px), weight 500.

### Annotation slots

- **Disagreement region annotation.** A single `ink @ 6%` rectangle
  wash over the most recent quarter where the two cuts diverge by
  more than 0.3 index points (threshold backend-curated; writer may
  override). Inside the wash, a one-clause annotation: e.g.,
  `Industry runs 0.3pt ahead in Q1 2026`. Inter `body-sm` 15px weight
  400, `ink`. Leader to the midpoint of the gap.

- **Recession band label.** `Recession (2020Q1-Q2)` at top edge in
  `micro` `ink-faint`.

### Recession bands

2020Q1-Q2 BCC band. `rgba(21,23,26,0.06)` rect behind data, full
y-height.

### Revision visual treatment

Monthly industry series is revised more frequently than the quarterly
expenditure series. Apply open-circle treatment per template Section 5
to the most recent industry data point only:

- Prior vintage: 4px open circle, 1px `series-1` stroke, transparent
  fill.
- Current vintage: 4px filled circle, `series-1`.
- 1px dashed `2 2` `ink-faint` connector.

Render only if `industry_idx_prior_vintage` differs from current by
more than 0.05 index points on the latest point.

Expenditure series: revisions render the same way, but in `series-7`.
Render only if a quarterly revision actually occurred in this release.
Both can render simultaneously.

### Callout treatment

This panel is one of the two basics-layer panels without a numeric
headline callout (per template Section 3, "Panel without a callout").
The callout block is replaced by an **editorial status line** in
`body-sm` weight 500 `ink`. Wording is writer's; structure is fixed:

> *Cross-check: industry and expenditure cuts agree in direction this
> [quarter / month]; gap of [N] index points at the level, within
> typical [range / acceptable] range.*

Chart-builder ensures the panel layout reserves the callout-block
vertical slot so the panel aligns with panels 1, 3, 4, 5 in the grid.

### Responsive variants

- **xl / lg.** Full 8-year window, both series.
- **md.** 5-year window. Both series.
- **sm.** Open question: spec defaults to dropping the expenditure
  line if the eye-comparison becomes illegible at the smaller chart
  width. A reader on mobile gets the monthly industry line with the
  annotation, plus a `body-sm` note below the chart:
  > *Quarterly expenditure cut not shown on this view; agreement with
  > industry is verified for the latest quarter (see methodology).*
  
  AD to confirm whether dropping the comparator on `sm` is acceptable.
  Alternative: keep both lines, drop the disagreement-region wash and
  the line termini labels, and rely on color alone.

### Open questions

For art-director:
- On `sm`: drop the expenditure line, or keep both and drop the wash?
  Spec defaults to dropping the line.
- Step-line vs straight-line interpolation for expenditure: spec uses
  step (honest about quarterly resolution). AD confirm.

For backend-engineer:
- Confirm 2019Q4 = 100 as the index base. Alternative: 2019 average =
  100 (less precise but more common). Spec assumes 2019Q4 (matches
  the BoC's MPR potential-level chart convention, useful for panel 5).
- Confirm the disagreement-region threshold (0.3 index pts) as the
  trigger for the annotation; this is editorial-curated, not derived.
