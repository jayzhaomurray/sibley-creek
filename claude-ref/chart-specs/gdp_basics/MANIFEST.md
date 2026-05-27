## claude-ref/chart-specs/gdp_basics/ -- manifest

Status: v0.1, spec-only (no implementation yet). Author: chart-builder.
Last updated: 2026-05-11.

Six per-panel chart specs for the GDP basics page (`/gdp/`), one .md per
panel. Drawn against:
- `design/basics-layer-template.md` Section 9 (GDP worked example)
- `design/design-system.md` Section 5 (chart aesthetic principles)
- `editorial/dashboard_purpose.md` Section 4.1 (six panel scopes)
- `pipeline/catalog/statcan_series.py` and `pipeline/catalog/boc_series.py`

This is the spec-only deliverable for Wave 3 Brief W3-CB1. Implementation
ships after EDR + art-director review.

---

### Panel reading order (locked by EDR section 4.1)

| # | Panel slug                    | EDR element                       | Chart type                       | Primary library       |
|---|-------------------------------|-----------------------------------|----------------------------------|-----------------------|
| 1 | `panel-1-headline-real-gdp`   | Headline real GDP                 | Dual-frequency bars + line       | Observable Plot       |
| 2 | `panel-2-industry-vs-exp`     | Industry vs expenditure           | Two-line overlay, indexed        | Observable Plot       |
| 3 | `panel-3-contributions`       | Contributions to quarterly growth | Diverging horizontal bars        | Observable Plot       |
| 4 | `panel-4-per-capita`          | Per-capita real GDP               | Two-line Y/Y                     | Observable Plot       |
| 5 | `panel-5-output-gap`          | Versus BoC potential              | Two-line + shaded gap            | D3 + custom SVG       |
| 6 | `panel-6-recession-state`     | Recession state                   | Horizontal Gantt timeline        | D3 + custom SVG       |

---

### Plot vs D3 rationale

**Observable Plot for panels 1-4.** These are standard editorial primitives
(time-series bars, two-line overlays, diverging bars, Y/Y comparisons).
Plot's defaults sit close to FT/Reuters aesthetics; the chart-aesthetic
rules (`design-system.md` Section 5) map onto Plot's `axis`, `marks`,
`scale`, and `style` props with no awkward escape hatches. Direct labels
ship via `Plot.text()` placed by hand. Recession bands via `Plot.rect()`
behind data marks.

**D3 + custom SVG for panels 5 and 6.** Panel 5 needs a hand-tuned shaded
gap polygon between two lines with a rotated annotation inside the
shaded region, plus dual-vintage staggered labels; Plot's `Plot.areaY()`
treats both lines as the same area boundary and the rotated-label-inside-
region treatment is fiddly through Plot's marks system. Panel 6 is a
Gantt-style cycle-state timeline with non-uniform recession bands of
specific dated widths; this is essentially a layout problem, not a chart
problem, and D3 + JSX SVG expresses it more directly than coercing it
into a Plot mark.

**Plotly: not used.** Per agent file, Plotly is forbidden in production.

---

### Cross-panel conventions

All six panels share:

- **Section accent.** Panels carry GDP's section accent (`series-1` /
  `#1F4E79`) only at the *panel eyebrow* (per template Section 3). Inside
  the chart, color is data color. The section accent never colors data
  except where a series happens to be `series-1` (which is how the section
  identity reinforces, not via a re-colored mark).

- **Recession bands.** All time-series panels (1, 2, 4, 5; not 3, which
  is a single-quarter decomposition; not 6, which IS the recession-state
  panel) render C.D. Howe BCC-dated recessions as `rgba(21,23,26,0.06)`
  rectangles behind data. Bands are unlabeled inside the chart area
  except for the most recent (2020Q1-2020Q2), which carries a `micro`
  `ink-faint` label `Recession (2020Q1-Q2)` at the top edge of the band.
  BCC dates are maintained as a small versioned JSON at
  `data/derived/cdhowe_bcc_recessions.json` (backend-engineer to wire);
  chart-builder reads it.

- **Time axis.** All time-series panels use `MMM YYYY` tick format on
  monthly axes, `YYYY` on multi-year quarterly axes (panels 4, 5, 6).
  Year boundaries are emphasized: each January gets a slightly heavier
  tick mark (1px `ink-faint` vs the 0.5px between-year ticks) and the
  year label sits at the year-start tick.

- **Value axis.** Per design-system Section 5: no axis line; horizontal
  gridlines in `rule-faint` (`#ECE7DC`); zero line in `ink-muted` if
  negative values present; 4-6 horizontal gridlines max; unit annotated
  on topmost tick (e.g., `%` or `Index, 2019Q4=100`) rather than as an
  axis title.

- **Direct labels at line termini** for all multi-series time series
  (panels 1, 2, 4, 5). `label` size (13px) Inter weight 500, color =
  series color, placed `s-2` (8px) right of the last data point.
  Replaces legends.

- **Latest-print marker.** All time-series panels mark the most recent
  data point with a filled 4px circle in series color, 1px `surface`
  ring (so it reads as a marker against possible gridline overlap).

- **Revision visual.** Per template Section 5: most recently revised
  point only. Previous vintage = open 4px circle, 1px series-color
  stroke, transparent fill. Current vintage = filled 4px circle, series
  color. Dashed `2 2` `ink-faint` 1px connector. Backend provides
  `vintage_prev` value alongside `vintage_current` on the latest point;
  if `vintage_prev` is null, the open circle does not render.

- **Surprise / consensus.** Surprise glyph treatment lives in the
  *callout* (page-level template), not in the chart. Charts do not
  render a consensus dot. The exception: panel 1 may optionally render a
  small `ink-faint` 1px horizontal tick at the consensus value at the
  most recent bar's x-position, only if the surprise is material
  (`|delta| > 0.05pp`). Open question for art-director: include or not?
  Default: not, until AD decides.

- **Annotations.** Inter `body-sm` 15px, weight 400, `ink` (primary) or
  `ink-muted` (secondary); 1px `ink-muted` leader, no arrowhead, single-
  elbow max, ending 4px short of anchor point. Wording is `writer`'s;
  placement is per-panel below.

- **Vintage stamp** is panel-level chrome (page template Section 6), not
  chart-internal. Chart-builder does not render it.

- **Aspect ratios.** Per template Section 3: 16:9 for time-series
  (panels 1, 2, 4, 5), 4:3 for the bar decomposition (panel 3), and 16:9
  for the Gantt timeline (panel 6). Chart canvas width inside the panel
  card: 432px on desktop (panel width minus `s-6` padding), 320px on
  `md`, full-bleed-minus-32px on `sm`.

- **Tabular figures.** All numeric labels inside charts use Inter with
  `font-feature-settings: "tnum"`. No serif numerics.

---

### Data-input convention

Backend-engineer provides prepared data as:
- A `.csv` or `.parquet` file under `data/derived/gdp_basics/<panel-slug>.csv`
- A sibling `.meta.json` with: `as_of_date`, `reference_period`,
  `vintage_prev_date`, `vintage_current_date`, `source_table_ids[]`,
  `source_table_urls[]`, `transforms_applied[]`.

Chart-builder consumes both. The `.meta.json` flows into the panel-card
chrome (vintage stamp, source line, methodology drawer); chart-builder
does not parse it for chart-internal logic, only for the chart's
recession-band dates and the revision-marker conditional.

Where a series needs an analytical transform (Y/Y, Q/Q SAAR, indexing
to 2019Q4=100), backend-engineer applies it upstream and writes the
transformed column. Chart-builder applies *chart-shape* transforms only
(histogram binning if any, area-fill polygon construction, label-
placement collision avoidance).

---

### Responsive variants

All six panels carry small-screen variants per template Section 2
(`sm` breakpoint, <640px). The compression strategy per panel:

| Panel | sm compression                                                              |
|-------|-----------------------------------------------------------------------------|
| 1     | Drop monthly bars below 8 most recent months; keep quarterly line full      |
| 2     | Drop `series-7` (expenditure) line if eye-comparison becomes illegible      |
| 3     | Stack the six bars vertically (each labeled inline)                         |
| 4     | Both lines retained, label both at line terminus on a single row           |
| 5     | Drop the rotated `Output gap` shaded-region label; keep gap polygon         |
| 6     | Compress 20-year timeline to 10-year; older recessions become `+N earlier` |

Each panel's spec carries the full sm variant detail.

---

### Open questions for art-director

Flagged across the six panel specs:

1. **Panel 1.** Whether to render a consensus-value tick at the most
   recent monthly bar. Spec defaults to "no" (the surprise lives in
   the callout, not the chart) — AD confirm?
2. **Panel 2.** Whether the expenditure cut renders as a step-held
   monthly resample or stays at quarterly resolution. Spec defaults to
   quarterly-step-line; AD confirm.
3. **Panel 3.** Order of the six bars. Spec follows EDR order
   (consumption, government, GFCF, inventories, exports, imports).
   Some FT precedents sort by magnitude. EDR order wins until AD says
   otherwise.
4. **Panel 5.** The shaded gap polygon: solid `ink @ 6%` tint or
   sequential blue ramp by gap magnitude? Spec defaults to solid tint
   (calmer); AD confirm.
5. **Panel 6.** Whether expansion periods get any fill at all (current
   spec: unfilled / paper background) or a very faint pos-soft wash.
   Spec defaults to unfilled.

---

### File index

- `MANIFEST.md` (this file)
- `panel-1-headline-real-gdp.md`
- `panel-2-industry-vs-exp.md`
- `panel-3-contributions.md`
- `panel-4-per-capita.md`
- `panel-5-output-gap.md`
- `panel-6-recession-state.md`
