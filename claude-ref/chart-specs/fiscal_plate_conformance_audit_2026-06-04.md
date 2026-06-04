# Fiscal Plate Conformance Audit — 2026-06-04

Reference: PanelLiveChart.astro (canonical shared component) vs the four wired
fiscal plates: Plate1BalanceTwoPanel, Plate2RevenuesPctGDP, Plate4FederalDebtPctGDP,
Plate5IssuanceByInstrument.

## Systematic deltas found across all four plates

### 1. `overflow: visible` missing on wrapper div and SVG element (FIXED)

PanelLiveChart sets `overflow: visible` on both the wrapper `.canon-chart` div
and the `.canon-chart__svg` SVG element. This keeps the FORECAST label, y-tick
labels, x-tick labels, and the latest-print dot (which can land outside the plot
frame) visible when they overflow the viewBox boundary at responsive sizes.

All four plates were missing `overflow: visible` on both elements.

**Fix applied:** Added `overflow: visible` to both the wrapper div and SVG
element CSS in all four plates.

### 2. Y-tick label x offset: `PLOT_X0 - 6` vs canon `PLOT_X0 - 8` (FIXED)

All four plates used `PLOT_X0 - 6` (and in Plate 1, `A_X0 - 6` / `B_X0 - 6`)
as the x coordinate for right-aligned y-axis tick labels. PanelLiveChart uses
`PLOT_X0 - 8`, giving 2px more breathing room between the plot frame and the
tick label's right edge.

**Fix applied:** Changed all y-tick label x coordinates from `- 6` to `- 8`.

### 3. X-tick label y offset: `PLOT_Y1 + 17` vs canon `PLOT_Y1 + 18` (FIXED)

All four plates placed x-tick labels 1px higher than the PanelLiveChart canon
(`PLOT_Y1 + 17` vs `PLOT_Y1 + 18`). Minor but creates visible misalignment when
a PanelLiveChart chart and a fiscal bespoke chart appear on the same page.

**Fix applied:** Changed all x-tick label y coordinates from `+ 17` to `+ 18`.

---

## Plate-1-specific deltas

### 4. Zero-line stroke-width: `1.5` vs canon `1` (FIXED)

Plate 1 used `stroke-width: 1.5` on the zero line. PanelLiveChart and the canon
reference use `stroke-width: 1`. The zero line is intended to be "heavier than
gridlines" in the sense of being full-opacity (not lighter opacity), not
literally wider. At 1px full-opacity it already reads distinctly against the
0.18-opacity gridlines.

**Fix applied:** Changed `.p1tp-chart__zero-line` stroke-width from `1.5` to `1`.

### 5. Panel-title `fill` property missing (FIXED)

`.p1tp-chart__panel-title` had no explicit `fill` property. The SVG inherits
black from the parent SVG's font settings, which produces correct rendering, but
the explicit token (`fill: var(--ink)`) is the canon pattern for all text
elements. Consistency matters for future theming.

**Fix applied:** Added `fill: var(--ink)` to `.p1tp-chart__panel-title`.

---

## Intentional chart-specific extensions (not deltas — no changes)

These were reviewed and confirmed as valid bespoke extensions, not drift:

- **Plate 1 two-panel gutter (`PANEL_GUTTER = 64px`)**: Mode B per-panel axes
  require a wider gutter than the default PanelLiveChart right margin. The 64px
  inter-panel gutter is the correct Mode B spacing so per-panel y-tick labels
  fit. Per `design/design-system.md` §"Small multiples" Mode B (~36-40px). This
  plate at 720px outer width with two panels makes 64px correct given the two
  per-panel axis columns.

- **Plate 2 expense-line dash: `stroke-dasharray: 6 3`**: Canon secondary uses
  `4 2`. The longer dash on Plate 2 is a deliberate editorial extension: revenue
  and expenses are two peer series of equal weight (neither is "secondary" in the
  canonical subordinate sense); the longer dash gives the expense line visual
  distinctness on a 42-year span where short dashes read as noise. Art-director
  should be aware; no change made.

- **Plate 4 annotation values in Plex Mono 600**: The annotation value elements
  (`66.6%`, `28.2%`, `47.2%`) use `font-weight: 600`. These are data values in
  a measurement context (the peak/trough labels), so Plex Mono is correct; the
  600 weight makes them read distinctly against the 400-weight word labels next
  to them. Valid intra-annotation hierarchy.

- **Plate 5 in-gutter tint swatches**: The segment label gutter includes 9x9
  tint swatches with `stroke: var(--ink); stroke-width: 0.5`. This is a
  bespoke stacked-bar convention (not in PanelLiveChart, which handles lines).
  The swatch approach is the correct solution for a multi-segment bar chart
  where end-of-bar labels cannot be vertically resolved from the terminus alone.

---

## Pre-existing contract failures (NOT in wired fiscal plates)

`node scripts/check_chartbook_contract.mjs` reported two pre-existing failures:

1. `src/components/charts/fiscal/Panel4ProvincialDebt.astro:216` — long SVG
   text (63 chars): `"* BC on taxpayer-supported basis; ON, QC, AB on net debt basis."`
   This is in an UNWIRED plate component; it is not rendered on `/fiscal/`.
   
2. `src/components/charts/trade/Panel4TariffState.astro:312` — long SVG text
   (82 chars). Different section, pre-existing.

Neither was introduced by this work. Both should be cleaned up in a separate pass.

---

## Files changed

- `src/components/charts/fiscal/Plate1BalanceTwoPanel.astro`
- `src/components/charts/fiscal/Plate2RevenuesPctGDP.astro`
- `src/components/charts/fiscal/Plate4FederalDebtPctGDP.astro`
- `src/components/charts/fiscal/Plate5IssuanceByInstrument.astro`
