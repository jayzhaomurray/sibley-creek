## Panel 5 -- Output gap (vs BoC potential)

Status: spec-only, v0.1. Owner: chart-builder.

EDR element: 4.1 #5. Template ref: basics-layer-template.md Section 9,
Panel 5.

---

### Purpose

Real GDP level vs the BoC's MPR potential-output level, both indexed
to 2019Q4 = 100, with the gap between them shaded as the editorial
focus. The current output-gap percentage is annotated directly.

### Data inputs

From `pipeline/catalog/statcan_series.py`:
- `gdp_quarterly` (v62305752, Table 36-10-0104-01) -- quarterly real
  GDP level.

From `pipeline/catalog/boc_series.py`:
- `output_gap_mpr` (Valet key `INDINF_OUTGAPMPR_Q`) -- current MPR
  output gap, quarterly %. Vintage stamp travels with the series
  (BoC publishes a new MPR quarterly).

Backend-engineer derives:
1. Real GDP level indexed to 2019Q4 = 100 (`gdp_idx`).
2. **BoC potential level** is not directly published as a series in
   Valet. Construction: backend-engineer reconstructs the potential
   level by inverting the published output gap (`gap = (Y - Y*)/Y*`,
   so `Y* = Y / (1 + gap/100)`), then indexes that derived `Y*` to
   2019Q4 = 100. Document in `.meta.json`.
   - Alternative: read the BoC MPR Appendix's potential-output level
     directly from the most recent MPR (PDF; researcher-curated
     vintage refresh on each MPR). Spec defers this choice to
     backend-engineer; either path is acceptable. Methodology drawer
     names which path.

Backend output: `data/derived/gdp_basics/panel-5.csv` with columns:
`date` (quarterly), `gdp_idx`, `potential_idx`, `output_gap_pct`.

Sibling `.meta.json`: `as_of_gdp` (StatCan release date), `as_of_mpr`
(BoC MPR release date -- distinct vintages, both surfaced in panel
chrome).

Window: 2010Q1 through latest available quarter (~16 years; long
enough to see post-GFC recovery, the 2020 shock and recovery, and
the current state).

### Chart type

**Two-line plot with shaded gap polygon between them.**

- Real GDP: 1.5px solid `series-1`, with quarterly markers (3px) and
  most recent point marker (4px filled, 1px `surface` ring).
- BoC potential: 1.5px dashed `4 2`, `series-7` (slate), no per-
  quarter markers (it is a smoothed estimate, not a print).
- Gap polygon: closed area between the two lines, filled with `ink @
  6%` (`rgba(21,23,26,0.06)`). When real GDP is below potential, the
  polygon sits below the potential line; when above, it sits above.

Plot/D3 choice: **D3 + custom SVG in a React component**. Reasoning:

- The polygon needs to render at the same z-index as the recession
  bands (behind the lines), and Plot's `Plot.areaY` between two
  bounds with a third reference line as the base does not compose
  cleanly when the two bounds cross (the gap flips sign).
- The rotated `Output gap` label inside the shaded region requires
  hand-tuned placement based on the longest contiguous sub-region of
  the gap polygon -- a layout computation easier in custom SVG.
- The dual-vintage stamp at the right edge (GDP vintage on one line,
  MPR vintage on another) ties into chart-internal annotation
  placement.

The D3 work is modest: linear scales for x and y, `d3.line` for the
two series, `d3.area` for the polygon, SVG primitives for everything
else. No animation, no interaction beyond hover tooltips.

### Axes

- **X.** Quarterly axis, ~16 years. Year-start ticks every 2 years
  (`YYYY`), unlabeled at intermediate years; quarter ticks 2px
  outward, unlabeled.
- **Y.** Index, 2019Q4 = 100. Range data-driven; typical
  `[94, 112]`. Gridlines every 2 index points in `rule-faint`.
  Reference line at 100 (the 2019Q4 anchor): 1px `ink-faint`, dashed
  `4 2`, labeled `2019Q4 = 100` at the right side in `micro`
  `ink-faint`.

### Series colors

- Real GDP: `series-1` (`#1F4E79`).
- BoC potential: `series-7` (`#4A4F57`, dashed).
- Gap polygon: `ink @ 6%` (`rgba(21,23,26,0.06)`). Same tint as
  recession bands, but visually distinct via position (between two
  lines vs full y-height behind data).

### Direct labels

Both lines at termini, `s-2` (8px) right of last data point:
- `Real GDP` -- `series-1`
- `BoC potential` -- `series-7`

Inter `label` (13px) weight 500.

### Annotation slots

- **Rotated polygon label.** Inside the shaded gap polygon, a small
  rotated label: `Output gap`, Inter `micro` (12px) weight 400
  `ink-faint`. Rotation angle: align with the local slope of the
  midline between real GDP and potential at the polygon's geometric
  centroid (so the text reads "with" the gap, not perpendicular to
  it). Placement is hand-tuned at build time; chart-builder computes
  the centroid and slope, then nudges by hand if it lands on a marker.

- **Current-gap annotation.** Anchored to the most recent quarterly
  point on the real GDP line, leader to the midpoint of the vertical
  distance between real GDP and potential at that x-position. Format
  (wording is writer's):
  > *Q1 2026: -0.5% gap*
  
  Inter `body-sm` (15px) weight 500 `ink`. Placement: upper-right
  whitespace if gap is negative (real GDP below potential), upper-
  left if positive.

- **Recession band label.** `Recession (2020Q1-Q2)` at top edge in
  `micro` `ink-faint`.

### Recession bands

2020Q1-Q2 BCC band; also 2008Q4-2009Q2 BCC band (within the 16-year
window). Both render as `rgba(21,23,26,0.06)` rects, full y-height.
Only the 2020 band gets a label (per design-system rule: label only
the most recent or most relevant). 2008-09 is unlabeled but the
shading is still informative.

### Revision visual treatment

- Real GDP: open-circle treatment on most recent point per template
  Section 5. If revised, prior vintage = 4px open circle in
  `series-1`, current = 4px filled, dashed connector.
- BoC potential: revisions happen on every MPR (quarterly cadence).
  Treatment: when the MPR vintage is new this release, render the
  *prior MPR's* potential level as a 1px dotted (`1 2`) `series-7`
  line spanning the last 4 quarters. This shows "where the BoC
  thought potential was last quarter" alongside the new estimate.
  No annotation -- the dotted line speaks for itself. Optional;
  AD confirm.

### Callout treatment

Numeric callout, no surprise field (no consensus on output gap):
- Big number: current output gap (e.g., `-0.5%`)
- Unit: `Q1 2026, BoC central estimate`
- Direction row: `[arrow up] +0.2pp vs Q4 2025` (no pipe, no
  surprise verb).

### Vintage handling

This panel has *two* distinct vintages -- the StatCan GDP release
and the BoC MPR release. Panel chrome surfaces both per template
Section 6 (two-line stamp expanded to three):

```
AS OF
Real GDP: May 30, 2026 (Q1 2026)
Potential: Apr 16, 2026 MPR
```

Chart-builder ensures the chart's per-line treatment matches: real
GDP's most recent marker is at the StatCan vintage's most recent
quarter; potential's most recent point is at the MPR vintage's most
recent estimate (may be one quarter ahead -- BoC MPR projects
potential forward).

### Responsive variants

- **xl / lg.** Full 16-year window, both lines, polygon, rotated
  label, current-gap annotation.
- **md.** Drop to 10-year window. All other elements retained.
- **sm.** Drop to 6-year window. Drop the rotated `Output gap`
  label inside the polygon (the polygon still reads as the gap).
  Drop the BoC potential prior-vintage dotted line if rendered.
  Keep both lines, the polygon, the current-gap annotation.

### Open questions

For art-director:
- Polygon fill: solid `ink @ 6%` tint vs diverging-blue ramp by gap
  magnitude. Spec defaults to solid tint (calmer, matches recession-
  band tint and reads as "this is context, not a feature"). AD
  confirm.
- Prior-MPR-vintage dotted line for potential -- include or omit?
  Spec defaults to omit (added complexity; the BoC potential
  vintage stamp in the panel chrome already names the freshness).
- Rotated polygon label: include or omit? Spec defaults to include
  (the chart's editorial point is "this is the gap").

For backend-engineer:
- Confirm the potential-level reconstruction path (invert the
  output-gap series vs read the MPR Appendix). Either is fine;
  document in methodology.
- Confirm the index base 2019Q4 = 100 (matches panel 2).
- Confirm `.meta.json` carries both `as_of_gdp` and `as_of_mpr`
  separately.
