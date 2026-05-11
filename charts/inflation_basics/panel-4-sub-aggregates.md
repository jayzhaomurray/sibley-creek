# Panel 4 -- Sub-aggregates

Status: v0.1. Author: chart-builder.
Cites `design/basics-layer-template.md` Section 3 and `design/design-
system.md` Section 5.

## What this panel answers

EDR Section 4.2 element 4: shelter (with mortgage interest cost
decomposed out via Table 18-10-0004-01), services ex-shelter, goods
ex-energy, food, energy. Reader leaves knowing which sub-aggregates
are pulling the headline up or down.

## Gating note

EDR explicitly gates this panel: "the ex- aggregates are basket-
weighted derivations and ship in v1 only if a reproducible analysis
script with methodology note is in place; otherwise v1 shows
all-services and all-goods directly with prose noting the dominant
sub-component."

This spec presents **both variants**: the preferred build (with
ex-aggregates) and the v1-fallback (all-services + all-goods).

## Panel chrome

- **Eyebrow:** `SUB-AGGREGATES` (`series-2` section accent).
- **Title slot:** writer-supplied (e.g., *"Shelter remains the
  dominant driver; energy is now a drag for the second consecutive
  month."*).
- **Deck:** writer-supplied (e.g., *"Excluding mortgage interest,
  shelter prints 3.8% -- still high, but the cooling is real."*).
- **Vintage stamp:**
  ```
  AS OF
  Apr 16, 2026
  Reference: Mar 2026
  ```
- **Source line:** `Source: Statistics Canada Table 18-10-0004-01;
  shelter ex-mortgage-interest decomposition by macro-research-
  department.`
- **Methodology link:** non-trivial if ex-aggregates ship. Drawer
  contents: basket weights, weighted-aggregation arithmetic for ex-
  energy goods and ex-shelter services, mortgage-interest sub-
  decomposition for shelter ex-MIC.

## Data inputs

### Preferred build (gated)

| Series                       | Source                                    | Catalog key                 |
|------------------------------|-------------------------------------------|-----------------------------|
| Shelter Y/Y                  | v41691050                                 | `cpi_shelter`               |
| Shelter ex-mortgage-interest | Derived (shelter minus weighted MIC)      | (backend transform)         |
| Mortgage interest cost Y/Y   | v41691093                                 | `cpi_mortgage_interest`     |
| Services ex-shelter Y/Y      | Derived (services minus weighted shelter) | (backend transform)         |
| Goods ex-energy Y/Y          | Derived (goods minus weighted energy)     | (backend transform)         |
| Food Y/Y                     | v41690974                                 | `cpi_food`                  |
| Energy Y/Y                   | v41691239                                 | `cpi_energy`                |

### v1 fallback

| Series              | Source       | Catalog key      |
|---------------------|--------------|------------------|
| Shelter Y/Y         | v41691050    | `cpi_shelter`    |
| All-services Y/Y    | v41691230    | `cpi_services`   |
| All-goods Y/Y       | v41691222    | `cpi_goods`      |
| Food Y/Y            | v41690974    | `cpi_food`       |
| Energy Y/Y          | v41691239    | `cpi_energy`     |

Backend-engineer ships a tidy frame
`{date, shelter, shelter_ex_mic, mic, services_ex_shelter, goods_ex_energy,
food, energy}` (or the v1 fallback subset).

## Chart type

**Small-multiple horizontal bar chart of latest values, paired with a
small inset shelter-decomposition strip.**

Plot rationale: this is exactly the case `Plot.barX` was designed
for. The shelter inset is a second small `Plot.barX` plotted at
half-height. Direct labels via `Plot.text`. No D3 needed.

Total chart canvas: **432 x 280 CSS px**. Upper section (sub-
aggregates ranked bar chart): 432 x 200. Lower section (shelter
decomposition inset): 432 x 60. 20px reserved between for the
divider rule and the inset title.

### Upper: ranked horizontal bar chart

One bar per sub-aggregate, **ranked by absolute Y/Y deviation from
2%** (the most-divergent-from-target sits at the top). Each bar
extends from a centered 2% axis (not zero) to its current Y/Y
value. The 2%-centered axis is the editorial choice: it shows
deviation from target, which is the question the reader asks of a
sub-aggregate.

### Lower: shelter decomposition inset

Two thin horizontal bars stacked:
- `Shelter ex-MIC` (the EDR's preferred read)
- `Mortgage interest cost`

This isolates the rate-sensitive component the EDR calls out.

## Axes, colors, labels

### Upper sub-canvas axes

- **X-axis:** percent Y/Y, anchored at 2% (the BoC target). Gridlines
  at -2%, 0%, 2%, 4%, 6%, 8% in `rule-faint`. The **2% line is
  rendered solid 1px `ink-muted`** -- it is the reference axis. The
  **0% line is rendered 1px `rule` dashed `2 2`** -- secondary
  reference.
- **Y-axis:** no axis line. Category labels float to the left of
  each bar in `body-sm` `ink`.

### Lower sub-canvas axes

- Same x-axis treatment as upper for consistency. Gridlines drop to
  the 2% and 0% reference only.
- Y-axis: two category labels (`Shelter ex-MIC`, `MIC`) left of each
  bar.

### Series colors

Bars colored by **direction of deviation from 2%**, using semantic
palette per design-system.md Section 4 consensus-color rule
(direction-of-print, not editorial valence):

- Y/Y > 2.5%: `neg` (#B23A2F) fill at 80% opacity, 1px `neg` upper
  edge. (Above target.)
- Y/Y in [1.5%, 2.5%]: `neutral-soft` (#DDE0E4) fill, 1px `neutral`
  edge. (Near target.)
- Y/Y < 1.5%: `pos` (#1F6B3A) fill at 80% opacity, 1px `pos` upper
  edge. (Below target.)

The cut-points (1.5/2.5) are the EDR's de-facto comfort band -- they
mirror the BoC's 1-3% control band collapsed inward by 0.5pp to
catch "drifting from target" before "out of band."

### Direct labels and annotations

- **Category label (left of bar):** `body-sm` weight 400 `ink`.
  E.g., `Shelter`, `Services ex-shelter`, `Goods ex-energy`,
  `Food`, `Energy`.
- **Value label (right of bar):** `mono-sm` (14px Plex Mono) weight
  400 `ink`. E.g., `+4.2%`, `-0.6%`. Sits 4px past the bar terminus.
- **Weight subscript** (small): `mono-xs` `ink-faint` italic, in
  parentheses. E.g., `(weight 28%)` for shelter. Renders only if
  basket weights ship (preferred build). The weight subscript is the
  page's most direct "show your work" affordance -- it tells the
  reader what the bar is worth in the headline.

### Inset section

Lower-canvas title (above the two thin bars): `SHELTER, DECOMPOSED`
in `label` weight 500 `ink-muted`, 0.04em letter-spacing. Tells the
reader what they are looking at.

The `MIC` bar carries a callout when the value is sharply different
from `Shelter ex-MIC`: `body-sm` italic `ink-muted`, e.g.,
*"Mortgage interest cost adds 1.4pp to shelter's headline; the rest
is rent and owned-accommodation."* Wording owned by writer.

## Recession bands

No recession bands -- this is a snapshot-of-latest chart, not a time
series. The window is one month.

## Latest-print callout

Per template Section 3, "Panel without a callout" treatment. There
is no single headline number; the chart itself is the callout. The
callout slot collapses to an **editorial status line** in `body-sm`
Inter weight 500 `ink`:

> *Shelter and food remain above the BoC's 1-3% band; energy
> contributes negatively for the second consecutive month.*

Wording owned by writer. Structure (one short editorial sentence)
locked here.

## v1 fallback rendering

When ex-aggregates are unavailable:

- Upper canvas shows: `Shelter`, `Services`, `Goods`, `Food`,
  `Energy`. Five bars.
- Lower canvas: same shelter decomposition (this does not require
  derived ex-aggregates -- it requires only `cpi_shelter` and
  `cpi_mortgage_interest`, both of which are catalog-registered and
  verified).
- Methodology drawer flags that ex-aggregates ship in v1.5.
- Title slot writer-wording flags the all-services / all-goods read.

## Responsive variants

- **`md` (<960px):** chart widens. Weight subscripts stay.
- **`sm` (<640px):** chart compresses. Weight subscripts collapse to
  a single right-aligned column header `Wt.` and a column of
  numbers, instead of inline. The shelter decomposition inset
  remains -- it is the most important affordance on the panel and
  must not drop on mobile.

## Editorial notes for art-director

- The 2%-centered axis is the panel's strongest editorial choice.
  Zero-centered would also work and would read more conventionally,
  but it would make the "above target" / "below target" affordance
  weaker. Recommend 2%-centered; flag for art-director.
- The 1.5%/2.5% color cut-points are derived (not in the EDR
  explicitly). They mirror the BoC's 1-3% control band collapsed
  inward. If editorial wants the harder 1%/3% cut to match the
  breadth panel, swap; spec would update consistently.
- Weight subscripts are the panel's "show your work" detail. They
  matter most on shelter (~28% weight makes its 4.2% print worth
  ~1.2pp of headline). Recommend keeping them prominent.
