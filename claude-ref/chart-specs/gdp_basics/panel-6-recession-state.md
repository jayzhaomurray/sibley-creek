## Panel 6 -- Recession state

Status: spec-only, v0.1. Owner: chart-builder.

EDR element: 4.1 #6. Template ref: basics-layer-template.md Section 9,
Panel 6.

---

### Purpose

A horizontal Gantt-style timeline of Canadian business-cycle state over
the last 20+ years, with C.D. Howe Business Cycle Council-dated
recessions as shaded blocks and expansions as the unfilled background.
The current state (Expansion since 2020Q3) is highlighted at the right
end. Not a numeric panel -- editorial status surface.

### Data inputs

No catalog series. This panel is driven by a small editorially-curated
JSON file maintained by editorial-director / writer with each BCC
communique:

`data/derived/cdhowe_bcc_cycles.json` (shape):

```json
{
  "as_of": "2026-03-15",
  "communique_url": "https://www.cdhowe.org/...",
  "cycles": [
    {"state": "recession", "start": "2008-10-01", "end": "2009-06-30",
     "label": "2008-09",
     "amplitude": "...", "duration_months": 8, "scope": "..."},
    {"state": "expansion", "start": "2009-07-01", "end": "2020-03-31"},
    {"state": "recession", "start": "2020-03-01", "end": "2020-06-30",
     "label": "2020Q1-Q2",
     "amplitude": "...", "duration_months": 2, "scope": "..."},
    {"state": "expansion", "start": "2020-07-01", "end": null,
     "current": true}
  ]
}
```

Sibling `.meta.json` carries the BCC communique date and the
reference URL.

Backend-engineer wires the JSON; chart-builder reads it.

### Chart type

**Horizontal Gantt / timeline.**

- A single horizontal track spanning ~20 years (e.g., 2005-01-01 to
  today + 6 months padding).
- Recession periods rendered as `rgba(21,23,26,0.12)` rectangles
  (slightly heavier than the chart-background recession tint at 6%,
  because here the band IS the data, not the context).
- Expansion periods rendered as the paper background (unfilled).
- The current expansion's right edge is a 2px solid `series-1` (deep
  blue, section accent) vertical bar terminating at "today" with a
  4px filled marker.
- Date labels for each recession at the top edge of the band.

Plot/D3 choice: **D3 + custom SVG in a React component**. This is a
layout problem more than a chart problem: the cycles are non-uniform
in duration, the labels need collision avoidance, the "current state"
right-end marker is a custom composite glyph. Plot's `Plot.rect` would
work but spending two hours coaxing label placement out of Plot when
direct SVG is 30 lines is the wrong trade.

The D3 work is minimal: one `d3.scaleTime` x-axis, fixed y, SVG rects
and text. No animation.

### Axes

- **X.** Time, 20+ years. Year-start ticks at every January, labeled
  `YYYY` at every 5th year (`2005`, `2010`, `2015`, `2020`, `2025`),
  unlabeled at intermediate years. Axis line `rule` 1px along the
  *bottom* of the track.
- **Y.** None. The track is a single horizontal band, ~24px tall,
  centered vertically in the chart canvas.

### Series colors

- Recession bands: `rgba(21,23,26,0.12)` (heavier than the standard
  chart-background recession tint).
- Expansion periods: unfilled (paper background, `#FBF8F2`). Per
  design-system, no fill.
- Current expansion right-end marker: 2px solid `series-1` vertical
  bar + 4px filled `series-1` dot at "today."
- Current-state callout label band (see annotations below): `series-1`
  at 100% (the only place section accent appears inside chart data,
  permitted because this panel's editorial point is the current
  state, and `series-1` is the section accent).

### Direct labels

- **Per-recession labels.** Above each recession band, at the band's
  horizontal midpoint: `2008-09` and `2020Q1-Q2` in Inter `micro`
  (12px) weight 400 `ink-faint`. The 2020 label may collide with
  the 2008-09 label depending on x-scale compression; chart-builder
  applies leader-line offset (single-elbow leader to band top edge)
  if collision risk.
- **Current-state label.** Above the current expansion's right edge,
  in Inter `body-sm` (15px) weight 500 `ink`: e.g., `Expansion since
  2020Q3`. Anchored to the current marker, leader optional.

### Annotation slots

- **BCC communique annotation.** A single dated annotation at chart
  bottom-right, in Inter `body-sm` (15px) weight 400 `ink-muted`:
  
  > *C.D. Howe BCC, [date]: classification unchanged; expansion
  > continues from [start date].*
  
  Wording is writer's; chart-builder reserves the slot below the
  track, separated by `s-3` (12px). Hangs free without a leader
  (the chart context provides the anchor implicitly).

- **Cycle metadata on hover.** Each recession band hover surfaces a
  small `body-sm` tooltip with the band's `amplitude`, `duration_months`,
  and `scope` strings from the JSON. Per design-system Section 8,
  tooltips give precision, not narrative. Tooltip background
  `surface`, 1px `rule` border, no shadow.

### Recession bands

This panel IS the recession-band view. No standard recession-band
treatment behind data (no "data" in the time-series sense).

### Revision visual treatment

Per template Section 5: the BCC occasionally re-dates a cycle when it
revisits older communiques. When the current release re-dates a band:

- The previously-dated band edge is rendered as a 1px dashed `2 2`
  `ink-faint` vertical line at the prior edge date.
- The current edge is the solid band edge.
- A short footnote-style annotation in `body-sm` italic `ink-muted`
  next to the band: e.g., *Trough re-dated from Apr to Jun 2020 in
  this communique.* Wording is writer's.

This is an unusual case; most communiques confirm existing dates.
When unrevised, no dashed-line treatment renders.

### Callout treatment

Editorial-status callout per template Section 3 ("Panel without a
callout"). The numeric callout block is replaced by:

> *Current state: **Expansion** since 2020Q3. Amplitude, duration,
> scope at trough: per BCC's most recent dating committee minutes.*

`body-sm` weight 500 `ink`, with `Expansion` bolded. Wording is
writer's; chart-builder reserves the slot.

### Responsive variants

- **xl / lg.** Full 20-year window (2005-today + padding). All
  recession bands labeled. Current-state label and communique
  annotation rendered.
- **md.** Same 20-year window. Labels may move below the track if
  collision avoidance forces it.
- **sm.** Compress to **10-year window** (2015-today + padding).
  Recessions before the window collapse to a compact left-edge
  indicator: a small `<<` glyph in `ink-faint` at the left margin,
  with a hover/tap-revealed text `+ 1 earlier recession (2008-09)`.
  The 2020 band remains visible. Current expansion + marker fully
  rendered. Communique annotation collapses to a single line of
  `micro` text below the track.

### Open questions

For art-director:
- Expansion-period fill: unfilled (paper background, current spec) vs
  `pos-soft` (`#D4E5D8`) wash at low opacity. Spec defaults to
  unfilled (calmer, lets the recession bands carry the visual
  weight). AD confirm.
- Recession band opacity: 12% (current spec) vs 8%. 12% is heavier
  than the standard chart-background recession tint (6%) because
  here the band is the data. AD confirm.
- Use of `series-1` (section accent) on the current-state marker
  inside chart data. This is a controlled exception to the "section
  accent does not color data" rule. Spec argues it is justified
  because the section accent is *the* visual signature of "current
  state in this section." AD confirm.

For editorial-director / writer:
- Confirm the BCC JSON structure above (`data/derived/cdhowe_bcc_
  cycles.json`). The `amplitude`, `duration_months`, `scope` fields
  are BCC's canonical wording -- writer to verify the exact strings
  copied from the most recent communique.

For backend-engineer:
- Wire the BCC JSON read into the data layer. The JSON is small (one
  object, ~5 cycles); a static fetch alongside other panel data
  files is fine.
