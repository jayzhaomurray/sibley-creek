# Panel 2 -- BoC preferred core trio

Status: v0.1. Author: chart-builder.
Cites `design/basics-layer-template.md` Section 3 and `design/design-
system.md` Section 5.

## What this panel answers

EDR Section 4.2 element 2: BoC core-trim and core-median lead as the
preferred pair; core-common shown as historical anchor with the
deprioritized-since-2022 note. Reader leaves knowing what the BoC's
own preferred measures say about underlying inflation.

## Panel chrome

- **Eyebrow:** `BOC PREFERRED CORE` (`series-2` section accent).
- **Title slot:** writer-supplied (e.g., *"Trim and median converged
  to 2.8% in March -- the narrowest gap since 2021."*).
- **Deck:** writer-supplied (e.g., *"Common, which the Bank
  deprioritized in late 2022, sits below the active pair."*).
- **Vintage stamp:**
  ```
  AS OF
  Apr 16, 2026
  Reference: Mar 2026
  ```
- **Source line:** `Source: Bank of Canada Valet CPI_TRIM,
  CPI_MEDIAN, CPI_COMMON.`
- **Methodology link:** non-trivial drawer. Contents: each measure's
  construction in one paragraph (trim = 20% tail trim each side,
  median = weighted-median component, common = factor extraction);
  BoC's late-2022 deprioritization of common with cite to the
  October 2022 MPR; a one-line note that 3M annualized core is
  shipped only if NSA core levels are recoverable from Valet
  (probe-pending per EDR).

## Data inputs

| Series                | Source                       | Frequency | Catalog key   |
|-----------------------|------------------------------|-----------|---------------|
| CPI core-trim Y/Y     | BoC Valet `CPI_TRIM`         | Monthly   | `cpi_trim`    |
| CPI core-median Y/Y   | BoC Valet `CPI_MEDIAN`       | Monthly   | `cpi_median`  |
| CPI core-common Y/Y   | BoC Valet `CPI_COMMON`       | Monthly   | `cpi_common`  |
| 3M AR (if NSA levels) | Derived from NSA core levels | Monthly   | (probe-pending) |

Backend-engineer ships a tidy frame `{date, trim, median, common,
trim_3m_ar?, median_3m_ar?}`. The `?` columns are gated on the
probe.

## Chart type

**Two-line lead + faded historical anchor.**

Plot rationale: Observable Plot's `Plot.lineY` handles all three
series cleanly. The "faded" treatment for common is just an opacity
property. Direct labels via `Plot.text`. No D3 needed.

## Axes, colors, labels

### Axes

- **X-axis:** monthly, last **6 years** (72 months) -- intentionally
  longer than panel 1 to show the 2022-2024 core peak and the
  divergence between trim/median and common.
- **Y-axis:** percent. Gridlines at 1, 2, 3, 4, 5 (rule-faint). Zero
  line omitted (core measures have not been negative in window).
- **BoC 2% target line:** 1px `ink-faint` dashed `4 2`. Same
  treatment as panel 1 -- consistency across the page.

### Series colors

- **Core-trim Y/Y:** `series-3` (#5B7553, sage), 1.75px solid.
- **Core-median Y/Y:** `series-4` (#7A3E65, plum), 1.75px solid.
- **Core-common Y/Y:** `series-7` (#4A4F57, slate), **1.25px solid at
  30% opacity (always-visible ghost line).** Per the README open
  question -- this is the recommended treatment, pending art-director
  confirmation.

### Direct labels

At line termini:
- `Trim` in `series-3` weight 500 `label`.
- `Median` in `series-4` weight 500 `label`.
- `Common` in `series-7` 60% opacity weight 500 `label`, with a
  `micro` italic subscript below: `BoC-deprioritized since late 2022`.
  Subscript wrapped at the right gutter; if it would overflow, the
  subscript renders inside a hover tooltip on the `Common` label
  instead.

### Annotations

Two annotations:

1. **Most recent convergence/divergence call**, anchored to the right
   terminus of trim and median. White-space placement above or below
   depending on which is higher. Wording owned by writer.

2. **The 2022 peak callout** -- a one-line annotation on the highest
   point of trim or median (whichever peaked higher) in the window,
   with date and value. `body-sm` weight 400 `ink-muted`. This is a
   historical anchor for the reader who is scanning the panel; it is
   not load-bearing on the latest print.

### Recession bands

`ink` 6% opacity over 2020Q1-Q2. Top-edge label only on this band.

## Latest-print callout

Two big numbers stacked tight (the trim+median pair is the EDR's
preferred lead):

- **Big number A:** `Trim 2.8%`. `display-md` serif weight 600
  tabular, with `Trim` in `label` `ink-muted` preceding the value.
- **Big number B:** `Median 2.7%`. Same treatment.
- **Unit:** `year-over-year, March 2026`. Single line below the
  pair.
- **Direction row:**
  ```
  Trim:   [arrow] -0.1pp vs Feb   |   Below consensus by 0.1pp[c]
  Median: [arrow] -0.1pp vs Feb   |   In line with consensus[c]
  ```
  Two compact rows. If panel width forces a single row, the trim row
  wins and median collapses to `(Median: -0.1pp vs Feb)` in
  `ink-muted`.

## Responsive variants

- **`md` (<960px):** panel widens to body-column. Both rows of the
  callout fit comfortably.
- **`sm` (<640px):** common line stays visible but loses its subscript
  (becomes hover-only on the legend swatch). Both trim and median
  keep direct labels; common's label collapses to a single-letter
  glyph `C.` at terminus.

## Editorial notes for art-director

- The 30%-opacity always-visible common line is the proposed answer
  to the EDR's "faded historical anchor with deprioritized note"
  brief. The alternative is hover-only (load-on-interaction), but
  that asks too much of the reader who is scanning -- the
  deprioritization itself is information they should see, even if
  they do not investigate it.
- If the 3M AR probe fails, the spec degrades to Y/Y only. No
  placeholder strip; the page reads cleanly with two solid lines and
  the ghost.
