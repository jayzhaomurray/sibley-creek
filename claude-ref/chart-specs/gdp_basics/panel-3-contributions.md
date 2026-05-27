## Panel 3 -- Contributions to quarterly growth

Status: spec-only, v0.1. Owner: chart-builder.

EDR element: 4.1 #3. Template ref: basics-layer-template.md Section 9,
Panel 3.

---

### Purpose

Six-bar decomposition of what drove the most recent quarter's Q/Q SAAR
growth: consumption, government, GFCF, inventories, exports, less
imports. Sum equals the headline Q/Q SAAR.

### Data inputs

From `pipeline/catalog/statcan_series.py`, all from Table 36-10-0104-01,
quarterly, percentage-point contributions:

- `gdp_contrib_total` (v79448580) -- total Q/Q SAAR growth (the sum).
- `gdp_contrib_consumption` (v79448555)
- `gdp_contrib_govt` (v79448562)
- `gdp_contrib_investment` (v79448563) -- GFCF
- `gdp_contrib_inventories` (v79448572)
- `gdp_contrib_exports` (v79448573)
- `gdp_contrib_imports` (v79448576) -- **already scaled -1** in the
  catalog (positive contribution = imports fell). For this chart we
  want to show imports as a negative contribution to growth in the
  conventional sense: when imports rise, they subtract from GDP. So
  backend-engineer needs to undo the scale (re-multiply by -1) for
  this panel only, and write the column as raw signed pp. Document
  in `.meta.json`.

Backend output: `data/derived/gdp_basics/panel-3.csv` with one row per
component for the most recent quarter:
`component, contribution_pp, q_minus_1_pp` (q_minus_1_pp is prior
quarter's contribution, for a one-glance "is this different from
last quarter" context strip).

Sibling `.meta.json`: `reference_period` (e.g., `Q1 2026`), revision
flag (any of the six contributions revised), total Q/Q SAAR.

### Chart type

**Diverging horizontal bars from a vertical zero axis.**

- Six horizontal bars, one per component, stacked top to bottom in
  EDR order:
  1. Consumption
  2. Government
  3. Gross fixed capital formation (GFCF)
  4. Inventories
  5. Exports
  6. Less imports
- Plus a 7th bar at the top, separated by `s-3` (12px) and a 1px
  `rule` divider rule above: **Total Q/Q SAAR**. Same scale, in
  `ink`, weight 500, slightly thicker bar (8px vs 6px).

Bar height: 6px. Inter-bar gap: `s-3` (12px). Total bars: 6 components
+ 1 total = 7 rows.

Plot/D3 choice: **Observable Plot**. `Plot.barX` with one bar per
component. The total bar is a separate `Plot.barX` mark with custom
height. The category-axis ordering is locked to EDR order.

### Axes

- **X.** Percentage points. Range: symmetric around zero, padded by
  20% of `max(|component|)`. Typical range `[-1.5, +1.5]` for a normal
  quarter. Gridlines every 0.5pp in `rule-faint`. Zero line: 1px
  `ink-muted`, full vertical extent of the plot. No axis at the top
  or bottom -- this is a category chart, the y-axis is just labels.
  Unit annotation at right end of zero line: `pp` in `micro`
  `ink-faint`.
- **Y.** Category axis. Labels at the left of each bar, Inter `label`
  (13px) weight 500, in the bar's series color (see below). Padding
  `s-3` (12px) between label and bar.

### Series colors

Categorical -- one color per component. Drawn from `series-1` through
`series-6`:

| Bar | Component       | Color           | Hex       |
|-----|-----------------|-----------------|-----------|
| 1   | Consumption     | `series-1`      | `#1F4E79` |
| 2   | Government      | `series-2`      | `#C9772A` |
| 3   | GFCF            | `series-3`      | `#5B7553` |
| 4   | Inventories     | `series-4`      | `#7A3E65` |
| 5   | Exports         | `series-5`      | `#3F7D7C` |
| 6   | Less imports    | `series-6`      | `#8A6A2C` |
| Top | Total Q/Q SAAR  | `ink`           | `#15171A` |

Negative-contribution bars use the same color but at 70% opacity
(slight de-emphasis on negative direction; positive is the typical
case). Alternative: leave at full opacity and rely on the leftward
direction from zero to encode sign. Spec defaults to full opacity
(simpler, honest).

### Direct labels

For each bar, at the *terminus* (right end if positive, left end if
negative):

- **Category name** (e.g., `Consumption`) -- already labeled at the y-
  axis on the left. Not duplicated at the bar terminus.
- **Value label** -- at the bar terminus, `s-2` (8px) past the bar end,
  Inter `mono-sm` (14px) tabular, weight 400, color = `ink`. Format:
  `+0.4 pp` or `-0.2 pp` (signed, one decimal, `pp` unit).

For the total bar: value label in `mono-sm` weight 500 `ink`, larger
visual weight.

### Annotation slots

- **Prior-quarter comparison strip.** Each component bar gets a small
  hollow square marker (5px x 5px, 1px stroke in component's color,
  transparent fill) plotted at the prior-quarter's contribution
  value. This is the equivalent of a "what changed from last
  quarter" reference, without adding a second bar. The reader's eye
  picks up "the marker is to the left of the bar end -> this
  contribution grew vs Q-1."
  
  No leader, no label on the marker. The visual is recognizable on
  inspection. If the prior-quarter delta exceeds the bar's current
  value by more than 0.5pp, the marker gets a 1px `ink-faint`
  connector line to the bar end (otherwise too far to read as
  related).

- **Total annotation.** Above the total bar, in `body-sm` weight 500
  `ink`: a one-clause label such as `Total Q/Q SAAR: +1.4%`.
  Replaced by the panel callout's big-number treatment; this in-
  chart label is therefore optional (default: omit, callout carries
  it).

### Recession bands

N/A. This is a single-quarter decomposition, not a time series.

### Revision visual treatment

If any of the six contribution series was revised in the current
release (per `.meta.json` revision flag), the affected bar(s) carry
a 1px dashed `2 2` `ink-faint` vertical tick at the prior-vintage
contribution value, ~6px tall, centered vertically on the bar. The
prior-quarter hollow square is a separate visual (the marker shows
Q-1's current vintage; the dashed tick shows the current quarter's
prior vintage). If both are within 0.3pp of the same x-coordinate,
the dashed tick wins (it is the primary revision marker).

The callout below the chart carries the verbal revision tag
(`Revised up` / `Revised down`).

### Callout treatment

Standard numeric callout (per template Section 3):
- Big number: total Q/Q SAAR (`+1.4%`).
- Unit: `quarterly, annualized, Q1 2026`.
- Direction row: delta vs prior quarter, surprise vs consensus.

### Responsive variants

- **xl / lg / md.** All six component bars + total bar. Full
  treatment.
- **sm.** Bars stack vertically (this is already the layout) but
  the y-axis category labels move to *above* each bar instead of to
  the left (so the bars get the full chart width). The hollow
  square prior-quarter marker is dropped (too small to read at
  mobile bar lengths). Value labels remain at the bar terminus.

### Open questions

For art-director:
- Order of the six bars. Spec follows EDR order (consumption,
  government, GFCF, inventories, exports, less imports). Some FT
  exemplars sort by magnitude (largest contribution at top). EDR
  order wins until AD decides otherwise.
- Prior-quarter hollow-square marker -- include or omit? It is a
  small visual that gives a one-glance "what changed" without
  cluttering. AD confirm.
- Negative-contribution bar opacity: full or 70%? Spec defaults to
  full.

For backend-engineer:
- Confirm the imports re-scaling: catalog `gdp_contrib_imports` has
  `scale=-1.0`. For panel 3 we want the conventional sign (positive
  pp = imports added to growth, negative = imports subtracted).
  Backend writes the unscaled signed value to the panel data file.
- Confirm prior-quarter contribution column is included.
