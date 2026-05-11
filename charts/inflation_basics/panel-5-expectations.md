# Panel 5 -- Inflation expectations

Status: v0.1. Author: chart-builder.
Cites `design/basics-layer-template.md` Section 3 and `design/design-
system.md` Section 5.

## What this panel answers

EDR Section 4.2 element 5: CSCE consumer 1-year and 5-year inflation
expectations; BOS firms-expecting-above-3% (and the BOS distribution
buckets as secondary view). Reader leaves knowing whether
expectations are anchored at the BoC target across consumers and
firms.

## Panel chrome

- **Eyebrow:** `EXPECTATIONS` (`series-2` section accent).
- **Title slot:** writer-supplied (e.g., *"Consumer five-year
  expectations sit at 2.5%, the lowest since 2022; firms re-
  anchoring slower."*).
- **Deck:** writer-supplied (e.g., *"The Bank's two-survey check on
  whether the anchor holds: consumers ahead, firms following."*).
- **Vintage stamp** (three lines because two source families):
  ```
  AS OF
  CSCE: Apr 30, 2026 (Q1 2026)
  BOS:  May 3, 2026 (Q1 2026)
  ```
- **Source line:** `Source: Bank of Canada Canadian Survey of
  Consumer Expectations (CSCE) Q1 2026; Bank of Canada Business
  Outlook Survey Q1 2026.`
- **Methodology link:** drawer cites both surveys, distinguishes the
  household sample (CSCE) from the firm sample (BOS), and notes that
  the BOS distribution buckets (below 1, 1-2, 2-3, above 3) are
  separate from CPI breadth (panel 3) -- this is a different
  population's stated expectations, not realized prints.

## Data inputs

| Series                       | Source                                | Catalog key            |
|------------------------------|---------------------------------------|------------------------|
| CSCE consumer 1y             | BoC Valet `CES_C1_SHORT_TERM`         | `infl_exp_consumer_1y` |
| CSCE consumer 5y             | BoC Valet `CES_C1_LONG_TERM`          | `infl_exp_consumer_5y` |
| BOS firms expecting >3%      | BoC Valet `ABOVE3`                    | `infl_exp_above3`      |
| BOS distribution below 1%    | BoC Valet `INDINF_BOSBELOW1_Q`        | `bos_dist_below1`      |
| BOS distribution 1-2%        | BoC Valet `INDINF_BOS1TO2_Q`          | `bos_dist_1to2`        |
| BOS distribution 2-3%        | BoC Valet `INDINF_BOS2TO3_Q`          | `bos_dist_2to3`        |
| BOS distribution above 3%    | BoC Valet `INDINF_BOSOVER3_Q`         | `bos_dist_above3`      |

Backend-engineer ships two tidy frames:
- `csce` -- `{date, cons_1y, cons_5y}`.
- `bos` -- `{date, above3, dist_below1, dist_1to2, dist_2to3,
  dist_above3}`.

## Chart type

**Two stacked sub-charts within the panel** (the EDR's "secondary
view as bucket distribution" makes this a small-multiple-within-a-
panel rather than an overlay):

- **Upper sub-chart:** CSCE consumer 1y and 5y as a two-line time
  series. The headline.
- **Lower sub-chart:** BOS firms-expecting-above-3% as a single
  line, with a thin **stacked-bar inset at the right terminus**
  showing the current distribution (below 1% / 1-2% / 2-3% / above
  3%).

Plot rationale: two `Plot.lineY` charts side-by-side (or stacked).
The stacked-bar inset is a single `Plot.barX` at the line terminus.
Plot handles it; no D3 needed.

Total chart canvas: **432 x 320 CSS px**. Upper: 432 x 140. Lower:
432 x 140. 40px reserved between for the divider rule and the lower-
chart title.

## Axes, colors, labels

### Upper sub-chart (CSCE)

- **X-axis:** quarterly, from 2014 (CSCE inception). About 50
  quarters. Year labels at Q1 only.
- **Y-axis:** percent. Gridlines at 1, 2, 3, 4, 5. Zero line omitted
  (CSCE has not been negative).
- **BoC 2% target line:** same treatment as panels 1-2. Consistency.

Series colors:
- CSCE 1y: `series-1` (#1F4E79, deep blue), 1.75px solid.
- CSCE 5y: `series-1` at 1.25px **dashed `2 2`**, 70% opacity.

The dashed-1y / solid-5y dichotomy is wrong-way-round here because
the 5y is the anchor read. The convention reverses for this panel:
**5y solid (the anchor), 1y dashed (the noisier near-term).** This
is deliberate; flag for art-director.

Direct labels at right termini:
- `1-year` in `series-1` 70% opacity weight 500.
- `5-year` in `series-1` weight 500.

### Lower sub-chart (BOS above-3% + distribution)

- **X-axis:** quarterly, from 2003 (BOS inception, per catalog
  start date). Year labels every 5 years (sparser, longer history).
- **Y-axis:** percent of firms (0 to 100 for the line; the inset
  is a 100% stacked bar).
- Gridlines at 25, 50, 75 in `rule-faint`.

Series colors:
- BOS above-3% line: `series-3` (#5B7553, sage), 1.75px solid. (The
  EDR's primary BOS read.)
- Stacked-bar inset, from top to bottom:
  - `Above 3%`: `#C9772A` (= `series-2`) at 80% opacity. **This is
    the one place outside panel 3 where the section accent appears
    in data**, and it is justified: the inset bucket and the line
    are the same population at the same date; the visual link is
    that they share the highest-bucket color.
  - `2-3%`: `#DDA76A`.
  - `1-2%`: `#F0CDA0`.
  - `Below 1%`: `#FBEBDA`.
  - Each bucket separated by 1px `surface` to keep edges crisp.

Sub-chart title: `FIRMS EXPECTING ABOVE 3%, WITH FULL DISTRIBUTION`
in `label` weight 500 `ink-muted`, 0.04em letter-spacing.

Direct label at line terminus: `Above 3%` in `series-3` weight 500
`label`. Stacked bar bucket labels: right of the bar, `micro`
weight 500 in each bucket's color (or `ink` for legibility on
lightest bucket), one line per bucket.

### Annotations

Two annotations, one per sub-chart:

1. **Upper:** anchored to most recent CSCE 5y point (the anchor
   read). E.g., *"Five-year at 2.5% -- lowest since 2022Q3."*
   Wording owned by writer.

2. **Lower:** anchored to most recent BOS above-3% point. E.g.,
   *"Below the 2021-23 average but above the 2010s norm of ~10%."*
   Wording owned by writer.

### Recession bands

`ink` 6% opacity over 2008Q4-2009Q2 (lower sub-chart only -- CSCE
starts post-GFC) and 2020Q1-Q2 (both sub-charts). Top-edge label on
the 2020 band only in the upper sub-chart; on the 2008-09 band only
in the lower sub-chart (the longer history).

## Latest-print callout

Two big numbers stacked (the CSCE pair is the EDR's anchor):

- **Big number A:** `2.8%` (CSCE 1y). With `1-year` in `label`
  `ink-muted` preceding.
- **Big number B:** `2.5%` (CSCE 5y). With `5-year` in `label`
  `ink-muted` preceding.

Unit line: `Consumer expectations, Q1 2026 (CSCE)`. `body-sm`
`ink-muted`.

Direction row:
```
1-yr: [arrow] -0.1pp vs Q4   |   --
5-yr: [arrow] -0.2pp vs Q4   |   --
BOS firms above 3%: 24%      (-3pp vs Q4)
```

Three compact rows. No consensus pipe -- expectations are not
consensus-anchored. The BOS row's `--` placeholder collapses; only
the delta-vs-prior renders.

## Responsive variants

- **`md` (<960px):** chart widens. Stacked-bar inset stays at the
  terminus.
- **`sm` (<640px):** stacked-bar inset moves from "at the terminus"
  to "below the lower sub-chart" as a separate horizontal stacked
  bar at the full panel width. Direct labels on the line still
  hold; bucket labels move to a single below-bar legend strip.

## Editorial notes for art-director

- **The 5y-solid / 1y-dashed reversal** versus panels 1-2 is the
  panel's most contentious visual choice. Justification: the 5y is
  the anchor read; the 1y is noisy near-term. Convention reversal
  forces the eye to the 5y. Alternative: keep 1y solid, 5y dashed
  for consistency, and use a deck annotation to direct the eye.
  Recommend the reversal; flag.
- **The accent-on-data exception** (the above-3% bucket sharing
  `series-2`) requires art-director approval per design-system.md
  Section 5. Justification is the visual coupling between the BOS
  above-3% line and the same bucket in the inset; the same color
  earns its keep here.
