# Panel 1 -- Headline CPI

Status: v0.1. Author: chart-builder.
Cites `design/basics-layer-template.md` Section 3 and 9 (template),
`design/design-system.md` Section 5 (chart aesthetic).

## What this panel answers

EDR Section 4.2 element 1: latest headline CPI Y/Y and 3-month
annualized; print with surprise vs market consensus. The reader leaves
this panel knowing where headline inflation is and whether it surprised.

## Panel chrome

- **Eyebrow:** `HEADLINE CPI` (label, all-caps, 0.08em letter-spacing,
  `series-2` section accent).
- **Title slot:** writer-supplied active-voice sentence (e.g.,
  *"Headline CPI eased to 2.1% in March, in line with consensus."*).
  `display-sm` (23px serif weight 600 `ink`). Two-line max.
- **Deck:** writer-supplied one-sentence "so what" (e.g., *"The
  three-month annualized pace sits below the year-over-year for the
  third consecutive month -- the disinflation is recent, not stale."*).
  `body-sm` italic `ink-muted`.
- **Vintage stamp** (top-right):
  ```
  AS OF
  Apr 16, 2026
  Reference: Mar 2026
  ```
- **Source line:** `Source: Statistics Canada Table 18-10-0006-01;
  consensus via Bloomberg.`
- **Methodology link:** right-aligned. Drawer is trivial (single
  StatCan vector, no construction); content: vector 41690914 (SA), SA
  methodology pointer, release cadence.

## Data inputs

| Series                | Source                                   | Frequency | Catalog key            |
|-----------------------|------------------------------------------|-----------|------------------------|
| Headline CPI Y/Y      | StatCan v41690914 (SA, 18-10-0006-01)    | Monthly   | `cpi_all_items`        |
| Headline CPI 3M AR    | Derived from same SA index               | Monthly   | (transform; backend)   |
| Market consensus Y/Y  | Bloomberg/Reuters median (or aggregated) | Per print | (per-release input)    |
| BoC MPR fallback      | MPR central CPI projection               | Quarterly | (fallback only)        |

Backend-engineer ships these as a single tidy frame with columns
`{date, yoy, mom3_ar, consensus_yoy, vintage_yoy_prior}`. The
3M-annualized is `((index_t / index_{t-3})^4 - 1) * 100`. The chart
consumes it; it does not compute.

## Chart type

**Dual-line time series on shared y-axis.**
- Line A: headline CPI Y/Y -- the primary read.
- Line B: headline CPI 3M annualized -- the leading-direction read.

Plot rationale: this is a textbook dual-line time series with direct
labels. Observable Plot's `Plot.lineY` + `Plot.text` covers it in 30
lines. No D3 needed.

## Axes, colors, labels

### Axes

- **X-axis:** monthly, last **5 years** (60 months). January year-tick
  labels (`micro` `ink-faint`); intermediate months unlabelled.
- **Y-axis:** percent. Gridlines at 0, 1, 2, 3, 4, 5 (rule-faint).
  Zero line at 1px `ink-muted` (rendered because CPI Y/Y has been
  negative briefly in this window).
- **BoC 2% target line:** 1px `ink-faint` dashed `4 2`, full width.
  Right-gutter rotated label `BoC 2% target` in `micro` `ink-faint`.

### Series colors

- Y/Y line: `series-1` (#1F4E79, deep blue), 1.75px solid.
- 3M AR line: `series-1` at 1.25px, **dashed `2 2`**, 70% opacity.
  Same hue, recessive treatment -- the Y/Y is the headline; the 3M AR
  is its companion.

### Direct labels

At the right terminus of each line:
- `Y/Y` in `series-1` weight 500, `label` (13px).
- `3M annualized` in `series-1` 70% opacity weight 500, `label`.

If a line ends in negative territory, the labels stack to avoid
overlap; if Y/Y > 3M AR (the disinflation case), labels separate
naturally.

### Annotations

One annotation, anchored to the most recent monthly print, in white
space above or below the terminus depending on direction:

```
   * Mar 2026: +2.1%
     consensus: +2.1% [c]
```

`body-sm` Inter weight 400 `ink` for the date+value; weight 500 on
the verb in the second clause. Leader: 1px `ink-muted` single-elbow,
ending 4px short of the data point. Wording owned by writer; the
above is a placeholder.

### Recession bands

`ink` 6% opacity over 2020Q1-Q2 (the only recession in the 5-year
window). Top-edge label `Recession (2020Q1-Q2, C.D. Howe BCC)` in
`micro` `ink-faint`.

### Revision marker (per template Section 5)

If StatCan's prior-vintage Y/Y for the previous month was revised:
open 4px circle at the prior value in `series-1` 1px stroke
transparent fill; 1px `ink-faint` dashed `2 2` connecting line to the
current filled marker (3px circle, `series-1`). Renders only on the
single most-recently-revised point; older revisions absorbed silently.

## Latest-print callout

Below the chart, before the source rule:

- **Big number:** latest Y/Y, e.g., `2.1%`. `display-md` (28px) serif
  weight 600 tabular `ink`.
- **Unit:** `year-over-year, March 2026`. `body-sm` Inter `ink-muted`.
- **Direction row:**
  ```
  [arrow] -0.2pp vs Feb    |    In line with consensus[c]   [Unrevised]
  ```
  - Arrow: Lucide `arrow-down`, 14px, in `pos` (#1F6B3A) when the
    print is below the prior on a disinflation read. **Per design-
    system.md Section 4 (consensus-color rule), the color encodes the
    direction of the print relative to expectations, not editorial
    valence.** So: -0.2pp on inflation = a downward print, which renders
    in `neg` (data direction, not editorial). The "good news for
    inflation" framing is for the writer's deck, not the color.
  - Pipe in `ink-faint`.
  - `In line with` verb per the template's mechanical rule
    (|delta vs anchor| within +/-0.05pp).
  - `[c]` subscript -- `mono-xs` 12px Plex Mono `ink-faint` below
    baseline -0.25em, hover tooltip per template Section 4.
  - `[Unrevised]` tag in `label` weight 500 `ink-faint`.

## Responsive variants

- **`md`/`sm` (<960px):** chart scales to ~600px wide at body-column
  width. 5-year window holds. All labels stay.
- **`sm` (<640px):** chart compresses to ~340px wide. The 3M AR line
  drops its direct label (only Y/Y labelled at terminus); a small
  legend swatch appears below the chart instead. Year labels every 2
  years.

## Editorial notes for art-director

- This is the entry panel; it sets the visual register for the rest
  of the page. Restraint above all -- it is a two-line chart.
- The BoC 2% target line is a soft typographic event, not a feature.
  It should be barely-visible; the reader's eye finds it because they
  are looking for it.
