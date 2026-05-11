# Panel 6 -- Pass-through watch

Status: v0.1. Author: chart-builder.
Cites `design/basics-layer-template.md` Section 3 and `design/design-
system.md` Section 5.

## What this panel answers

EDR Section 4.2 element 6: side-by-side strip-chart panel,
(USDCAD Y/Y vs goods-ex-energy CPI Y/Y) and (LFS-Micro wage growth
vs services-ex-shelter CPI Y/Y). **No regression in basics; the
interpretation is analyst prose.** Reader leaves with a visual
correlation read on whether external (FX) and internal (wage)
pass-through channels are co-moving with the relevant CPI sub-
aggregates.

## Gating note

EDR explicitly gates this panel: "gated on element 4's derived
aggregates landing; if they slip, pass-through defers to v1.5."

This spec defaults to the **preferred build with derived ex-
aggregates**. If element 4 ships only the v1 fallback, this panel
ships as a placeholder (see Editorial notes).

## Panel chrome

- **Eyebrow:** `PASS-THROUGH WATCH` (`series-2` section accent).
- **Title slot:** writer-supplied (e.g., *"FX pass-through into goods
  prices remains muted; wage pass-through into services is the
  active channel."*).
- **Deck:** writer-supplied (e.g., *"Two channels by which the
  underlying drivers of Canadian inflation transmit -- one external,
  one internal."*).
- **Vintage stamp** (three lines because two cadences):
  ```
  AS OF
  CPI: Apr 16, 2026 (Mar 2026)
  FX:  Apr 30, 2026 (monthly avg)
  ```
- **Source line:** `Source: Statistics Canada Table 18-10-0004-01;
  Bank of Canada Valet FXUSDCAD; Bank of Canada LFS-Micro
  composition-adjusted wages; macro-research-department
  construction of ex-aggregates.`
- **Methodology link:** non-trivial drawer. Contents: USDCAD Y/Y
  construction (monthly average of daily close, then year-over-year);
  LFS-Micro composition-adjustment note (cite BoC methodology);
  derived ex-aggregate construction (cross-ref panel 4 drawer); the
  explicit "no regression" note -- the chart is a visual co-movement
  read, not a fitted relationship.

## Data inputs

| Series                       | Source                                | Catalog key              |
|------------------------------|---------------------------------------|--------------------------|
| USDCAD daily close           | BoC Valet `FXUSDCAD`                  | `fxusdcad`               |
| USDCAD Y/Y (monthly)         | Derived (monthly avg, then Y/Y)       | (backend transform)      |
| Goods ex-energy CPI Y/Y      | Derived (panel 4 transform)           | (backend transform)      |
| LFS-Micro wage growth Y/Y    | BoC Valet `INDINF_LFSMICRO_M`         | `lfs_micro`              |
| Services ex-shelter CPI Y/Y  | Derived (panel 4 transform)           | (backend transform)      |

Backend-engineer ships two tidy frames:
- `fx_passthrough` -- `{date, usdcad_yoy, goods_ex_energy_yoy}`.
- `wage_passthrough` -- `{date, lfs_micro_yoy, services_ex_shelter_yoy}`.

## Chart type

**Two side-by-side strip charts, dual-axis on each strip.**

Each strip is a two-line time series with two y-axes:
- Strip A (FX channel): USDCAD Y/Y (left axis) + goods-ex-energy
  CPI Y/Y (right axis).
- Strip B (Wage channel): LFS-Micro wage Y/Y (left axis) +
  services-ex-shelter CPI Y/Y (right axis).

Plot rationale: Plot supports dual-axis time series via two
`Plot.lineY` marks with separate y-scales declared on the marks
(or via `Plot.plot({y: ..., y2: ...})`). The side-by-side at panel
width is a small-multiple layout, which `Plot.facet` or two
juxtaposed `Plot.plot()` calls handle. No D3 needed for this layout.

Total chart canvas: **432 x 200 CSS px**. Two strips side-by-side
with 16px gutter: each strip is 208 x 200. Strips are 2:1 aspect --
squat, by design.

## Axes, colors, labels

### Per-strip axes

- **X-axis:** monthly, last **7 years** (84 months). Annual labels
  in January.
- **Left y-axis (the "driver"):** percent. Range tuned to series:
  - USDCAD Y/Y: typically -15% to +15%.
  - LFS-Micro wage Y/Y: typically -2% to +8%.
- **Right y-axis (the "CPI sub-aggregate"):** percent. Range tuned:
  - Goods ex-energy CPI Y/Y: typically -2% to +8%.
  - Services ex-shelter CPI Y/Y: typically 0% to +6%.
- Gridlines: 4 in `rule-faint`, anchored to the **left axis** only.
  The right axis ticks are unlabeled grid; right-axis tick values
  appear as floating labels at right-gutter only.
- Zero line: rendered at 1px `ink-muted` on the left axis when the
  driver crosses zero (always the case for USDCAD Y/Y, sometimes
  for wages).
- **2% target line on the right axis** for both strips. Same
  treatment as other panels (`ink-faint` dashed `4 2`). Right-
  gutter rotated label `BoC 2% target` in `micro`.

### Series colors

- **Driver line (left axis):** `series-2` (#C9772A, burnt orange).
  This is the second place outside panel 3 where data uses the
  section accent. Justified: the editorial argument of this panel is
  that the driver is the lead and the CPI is the response;
  highlighting the driver with the section accent makes the read
  obvious. 1.75px solid.
- **CPI response line (right axis):** `series-1` (#1F4E79, deep
  blue), 1.75px solid.

### Direct labels

At the right termini of each line in each strip:
- Strip A: `USDCAD Y/Y` in `series-2` weight 500 `label`;
  `Goods ex-energy` in `series-1` weight 500 `label`.
- Strip B: `Wage Y/Y` in `series-2` weight 500 `label`;
  `Services ex-shelter` in `series-1` weight 500 `label`.

Strip titles (centered above each strip): `EXTERNAL: FX PASS-
THROUGH` and `INTERNAL: WAGE PASS-THROUGH`. `label` weight 500
`ink-muted`, 0.04em letter-spacing.

### Annotations

One annotation per strip, anchored to the most recent date,
describing the current co-movement state. Wording owned by writer
(e.g., *"USDCAD weakened 4% over the year; goods ex-energy
unchanged."* and *"Wages cooling but services ex-shelter holding
above 3%."*). `body-sm` weight 400 `ink-muted`, single-elbow leader
to either driver or response line.

**No regression line, no scatter, no R-squared.** Per EDR, this
panel does not regress. Visual co-movement is the read.

### Recession bands

`ink` 6% opacity over 2020Q1-Q2 in both strips. Top-edge label only
on left strip's band (to avoid noise on the small canvases).

## Latest-print callout

Per template Section 3, "Panel without a callout" treatment. There
is no single headline number; the panel itself is the editorial
read. The callout slot collapses to an **editorial status line** in
`body-sm` Inter weight 500 `ink`:

> *FX pass-through quiet; wage channel is the live one. Both
> consistent with the BoC's MPR pass-through assumptions as of April
> 2026.*

Wording owned by writer; structure (two short clauses) locked here.

## v1 placeholder rendering (if gated out)

If derived ex-aggregates from panel 4 are not available:

- Both strips render as empty `surface-sunk` rectangles with a
  centered annotation: *"Pass-through panel ships with v1.5,
  pending basket-weight reproducibility for ex-energy and ex-
  shelter aggregates."*
- Vintage stamp shows the gating decision date.
- Editorial status line in the callout slot: *"Pass-through analysis
  defers to v1.5."*

Backend-engineer confirms before render.

## Responsive variants

- **`md` (<960px):** strips remain side-by-side but tighten to ~280
  each at body-column width.
- **`sm` (<640px):** strips **stack vertically** inside the panel.
  Each strip widens to full panel-content width (~340px). Strip
  titles move from "above" to "left-aligned at top of strip."
  Annotations preserved.

## Editorial notes for art-director

- **Side-by-side at desktop, stacked on mobile** is the spec's
  default per README open question 4. Confirm.
- **Accent-on-data appears twice** on the page now: panel 3 (tilt
  marker) and this panel (driver line). Both are deliberate
  editorial choices: panel 3 makes an argument about a single
  data point; panel 6 makes an argument that the driver leads. Per
  design-system.md, this needs art-director sign-off. Two accent-
  on-data exceptions on one page is the upper limit -- a third
  would dilute the convention.
- **Dual-axis is the panel's structural risk.** Dual-axis charts
  read deceptively when scales are not tuned. The annotation text
  must do the work of saying what to compare; the chart itself
  cannot be trusted to make the comparison obvious. The "no
  regression" rule from EDR is the right discipline; without it,
  readers would over-interpret co-movement.
