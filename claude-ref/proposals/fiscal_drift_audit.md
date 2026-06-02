# Fiscal page — chart drift punch-list (cohesion audit)

Art-director cohesion audit, 2026-06-02. NOT a re-spec. Each item names what
the live reference charts do, what the fiscal plates do instead, and the
exact token/value fix. Ranked most-visible-first.

## Root cause (read this first)

The live GDP / inflation plates all render through one shared engine:
`src/components/charts/_shared/PanelLiveChart.astro`. That engine IS the house
style — every token below is pinned there. The five fiscal plates
(`fiscal/Plate1..5*.astro`) each **re-implement their own SVG + their own
`<style>` block from scratch** and drifted on a dozen tokens in the copy.
The drift is systematic and identical across all five plates (same wrong
values in each `<style>`), because they were authored as a set off a spec
rather than against the engine's CSS.

Two of the five (Plate2 line, Plate3 line) are close enough in form that
they could in principle delegate to `PanelLiveChart`; the bar/stacked plates
(Plate1, Plate5) and the dual-line forecast plate cannot, so they must be
hand-corrected. **The fix for every item below is: match the exact token in
`PanelLiveChart.astro`'s `<style>` block.** I give the literal value each
time so chart-builder needn't cross-reference.

These plates also still carry `[TITLE TK]`, `[CAPTION TK]`, `[ANNO TK]`
placeholders — those are the writer/review pipeline's job, NOT this audit.
But see Item 9: several are rendering inside the SVG canvas where they read
as broken chrome, and at least one (`[CAPTION TK: Expenses]`) overflows the
frame.

---

## P0 — most visible drift

### 1. Tick labels are dimmed with opacity; canon ticks are full-strength pure ink

- **Reference:** `PanelLiveChart` `.canon-chart__ytick-label` and
  `.canon-chart__xtick-label` are `fill: var(--ink)` at **full opacity** (no
  `opacity` property at all). Pure black, 12px. This is canon (design-system
  §3 — "if a thing should be quieter, drop its weight, not its hue"; the
  Vignelli register has no dimmed ink).
- **Drift (all 5 plates):** every fiscal y-tick and x-tick label carries
  `opacity: 0.7`, and x-tick *marks* carry `opacity: 0.4`. The axis furniture
  reads visibly gray and washed-out next to the crisp black ticks on the GDP
  and inflation pages. This is the single most legible difference when the
  fiscal page is scrolled next to inflation.
- **Fix:** delete `opacity: 0.7;` from every `*-chart__ytick-label` and
  `*-chart__xtick-label` rule, and delete `opacity: 0.4;` from every
  `*-chart__xtick` (tick-mark) rule, across Plate1–5. Ticks render at full
  `var(--ink)`.

### 2. Tick font sizes are off (11px / mixed); canon is uniform 12px

- **Reference:** `PanelLiveChart` — y-tick **12px** Plex Mono, x-tick **12px**
  Manrope. Both 12px, weight 400.
- **Drift:** fiscal x-tick labels are **11px** (Plate1–5), and the
  latest-actual numeric labels are **11px** (canon equivalent — the direct/
  reference labels — run 12–13px). The fiscal pages read one notch smaller and
  more timid than the reference.
- **Fix:** set every `*-chart__xtick-label` to `font-size: 12px`. Y-ticks are
  already 12px — leave. (Latest-actual numeric label size handled in Item 6.)

### 3. The "Forecast" label uses a non-canon treatment (`font-variant: small-caps` + dimmed)

- **Reference:** there is **no** "Forecast" label anywhere in the live GDP /
  inflation set, so there's no exact prior — but the canon equivalent is the
  recession-band label (`.canon-chart__recession-label`): Manrope **11px,
  weight 600 (`--fw-semibold`), `letter-spacing: 0.18em`, full-opacity
  `var(--ink)`, real uppercase** (the string is literally `RECESSION
  (2020Q1-Q2)` in caps). That is the canon pattern for a margin-anchored
  chart-furniture label.
- **Drift (all 5 plates):** the "Forecast" label uses `font-variant:
  small-caps` (a faux-caps rendering, NOT how any other label on the site is
  set — the site uses real uppercase strings + tracking), `letter-spacing:
  0.14em` (canon is 0.18em), and `opacity: 0.55` (canon margin labels are
  full-strength ink). In the screenshots this renders as the small-caps
  "Forecast" top-right — it does not match the recession label's weight,
  tracking, or strength, and `small-caps` is foreign to the system.
- **Fix:** retreat the "Forecast" label to the recession-label token exactly:
  - Remove `font-variant: small-caps`.
  - Set the rendered string to uppercase (`FORECAST`) in the markup, OR
    `text-transform: uppercase` in CSS.
  - `font-weight: 600`, `font-size: 11px`, `letter-spacing: 0.18em`,
    `fill: var(--ink)`, **delete `opacity: 0.55`**.
  This makes the forecast divider read as the same class of object as the
  recession-band label, which is the closest house precedent.

### 4. Forecast divider is a new convention with no live precedent — confirm and align weight

- **Reference:** the canon "event line" treatment (design-system §3,
  "Event lines") is **1px solid pure ink, dashed `4 2`**, with a micro label
  above the plot. The recession marker on GDP Plate3 (`RECESSION
  (2020Q1-Q2)`) is the live exemplar of a vertical-region annotation, and it
  uses a **shaded band**, not a dashed vertical rule.
- **Drift (all 5 plates):** the forecast divider is `stroke-dasharray: 4 3`
  (canon dash is `4 2`) at `stroke-opacity: 0.40`. The dash period is off and
  the line is dimmed.
- **Fix:** align the dash to canon: `stroke-dasharray: 4 2`. The 0.40 opacity
  on the *rule itself* is acceptable as event-line restraint (it's a structural
  divider, not data) — keep it, but make it consistent: all five plates must
  use the identical value. (The label above it is fixed in Item 3.) This is
  the one genuinely new convention on the fiscal page; flagging it so it gets
  ratified rather than drifting further. The dashed-vertical-divider read is
  legitimate and clean; just lock dash to `4 2`.

---

## P1 — visible on close read

### 5. Latest-actual numeric label: font + placement diverge from canon direct-label

- **Reference:** `PanelLiveChart` direct labels (`.canon-chart__direct-label`)
  are Manrope **13px, weight 600**, pure ink, sat in the right gutter at the
  line terminus. The latest *value* on the live charts is conveyed by the red
  dot + the y-axis; there is no separate floating numeric callout on the GDP /
  inflation lines.
- **Drift:** fiscal plates float a Plex Mono **11px** numeric label directly
  above/beside the red dot (e.g. `-$36.3B` on Plate1, `16.1%` on Plate3,
  `$1,482B` on Plate5). The Plex Mono choice for a *value* is correct (it is a
  measurement). But the **11px size is too small** vs the 12–13px chart-label
  ladder, and on Plate2 it produces two stacked red dots with `16.6%` / `16.1%`
  values crammed together mid-plot.
- **Fix:**
  - Set every `*-chart__latest-label` to `font-size: 12px` (Plex Mono 400,
    tabular — keep). This matches the y-tick mono size and reads as the same
    data class.
  - Keep the placement convention (numeric label adjacent to red dot) — it is a
    reasonable house extension since these long-history charts benefit from a
    printed latest value. But on **Plate2** (two near-coincident dots at 16.6 /
    16.1), the two labels collide; nudge the lower label down so the gap is
    ≥12px (the canon `LABEL_MIN_DY` stack guard), or drop one to the direct
    terminus label.

### 6. Direct terminus labels overflow the frame / are placeholders rendering as data

- **Reference:** direct labels sit in the **96px right gutter** (`M_R = 96` in
  `PanelLiveChart`) so a label like `Core-median` clears the plot frame
  cleanly. Manrope 13px 600.
- **Drift:** Plate2 (`M_R = ?`), Plate3 (`M_R = 80`) — the right margins are
  narrower than canon's 96, and the terminus labels are placeholder strings
  (`[CAPTION TK]`, `[CAPTION TK: Expenses]`) that **overflow past the right
  edge of the SVG** (visible clipped in NEW_fiscal_plate2 and plate3). On
  Plate2 the two-line `[CAPTION TK` / `[CAPTION TK` stack runs off-canvas.
- **Fix:**
  - Set `M_R = 96` on every fiscal line plate (Plate2, Plate3, Plate4) to match
    canon and give the terminus label its gutter. (Bar plates Plate1/Plate5
    use right-gutter series labels — set those `M_R` to fit the longest series
    label, "Operating" / "T-bills", at the canon direct-label size.)
  - Terminus label typography: Manrope **13px** (currently 12px on Plate3's
    `term-label`), weight 600, `fill: var(--ink)`. Match
    `.canon-chart__direct-label`.
  - The placeholder *wording* is the writer's job — but the slot must be sized
    so real copy lands in-gutter, not clipped.

### 7. Annotation value uses weight 600 mono; canon anchor-word treatment differs

- **Reference:** canon annotations (design-system §5 Tier-3 "Annotations") are
  Manrope `body-sm` (15px) weight 400, weight 600 only on the inline anchor
  word, pure ink; leader lines 1px pure ink, **no opacity dimming**, ending 4px
  short of the datum.
- **Drift (Plate3, Plate4):** the COVID-spike annotation renders `[ANNO TK]`
  in Manrope 11px `opacity: 0.7` plus a value `28.1%` in **Plex Mono 11px
  weight 600**, with a leader line at `stroke-opacity: 0.45`. Three drifts:
  annotation text is dimmed (canon is full ink), it's 11px (canon 15px / or at
  minimum the 12px chart ladder), and the leader line is dimmed (canon leader
  is full 1px pure ink).
- **Fix:**
  - Annotation label: `font-size: 12px` minimum (13px preferred to match the
    direct-label ladder), `font-weight: 400`, **delete `opacity: 0.7`**, full
    `var(--ink)`.
  - Annotation value: keep Plex Mono (it's a number) but at `font-size: 12px`;
    weight 600 is acceptable as the "anchor" emphasis.
  - Leader line: **delete `stroke-opacity: 0.45`** → full 1px pure ink, per
    `.canon-chart__reference-rule` strength conventions (reference rules are
    full-strength; only the *gridlines* are dimmed). End 4px short of the datum
    (currently 5px — minor, align to 4).

### 8. Series / segment labels (bar + stacked plates) dimmed with stepped opacities

- **Reference:** there is no live multi-segment bar chart in the GDP/inflation
  reference set, but the canon multi-series label treatment (`PanelLiveChart`
  `.canon-chart__direct-label-secondary`) is Manrope **13px, weight 400, full
  `var(--ink)`** — recession into the page is done by *weight/dash on the
  data*, never by dimming the label.
- **Drift (Plate1, Plate5):** the in-gutter segment labels use a stepped
  opacity ladder to fake hierarchy: Plate1 `Operating` at `opacity: 0.85` /
  `Capital` at 0.7; Plate5 `Bonds` 0.85 / `T-bills` 0.75 / `Retail` 0.6. This
  is hue-softening-by-opacity, which the canon explicitly forbids — hierarchy
  is weight, not opacity.
- **Fix:** drop all `opacity` from `*-seg-label-*` rules. Encode hierarchy by
  **weight** instead: primary segment label weight 600, secondary/tertiary
  weight 400 (mirroring the direct-label / direct-label-secondary split). All
  at 13px, full `var(--ink)`. The *texture* of the bars (solid / hatch) already
  carries the categorical distinction — the labels don't need to be dimmed too.

---

## P2 — lower visibility, still fix for full cohesion

### 9. Placeholder `[...TK]` strings rendering inside the SVG canvas read as broken chrome

- **Reference:** the live engine never renders a placeholder *inside* the
  plot. Placeholder copy on the site uses the `--ink-placeholder` (#8A8A8A)
  treatment (design-system §3.5) and lives in the chartbook unit's prose slots,
  not on the canvas.
- **Drift:** `[ANNO TK]`, `[CAPTION TK]`, `[CAPTION TK: Expenses]` are rendered
  as live SVG `<text>` in pure or near-pure ink, so they read as real (broken)
  chart labels rather than as obvious empty slots. Plate3's
  `[CAPTION TK: Expenses]` overflows the frame (see Item 6).
- **Fix (visual treatment only — wording is writer's job):** until the writer
  fills these, any on-canvas placeholder `<text>` should render in
  `fill: var(--ink-placeholder)` (#8A8A8A) so it reads as a typeset empty slot,
  not as shipped chart furniture. This also prevents a placeholder accidentally
  reading as a real annotation in review screenshots. (Better: gate them to not
  render at all when the value is a TK string, per the §3.5 enrich-to-null
  pattern — but the minimum fix is the placeholder ink color.)

### 10. Geometry margins diverge from canon (causes the gutter-overflow in Item 6)

- **Reference:** `PanelLiveChart` margins are pinned: `M_L=56, M_R=96, M_T=44,
  M_B=40`. These are canon and shared by GDP Panel1 and PanelCanonReference.
- **Drift:** fiscal plates use ad-hoc margins — Plate1 `52/60/36/38`, Plate3
  `44/80/36/38`. Smaller right gutter (60–80 vs 96) is why terminus/series
  labels clip; smaller top margin (36 vs 44) crowds the "Forecast" label
  against the frame.
- **Fix:** move every fiscal plate to the canon margin set `M_L=56, M_R=96,
  M_T=44, M_B=40` unless a specific plate has a documented reason to differ
  (e.g. Plate1's signed `-340` y-labels may want `M_L=56` exactly — that's the
  canon value anyway). Bar plates can keep a tuned `M_L` if wider numeric
  y-labels demand it, but `M_R=96` and `M_T=44` should be universal so the
  forecast label and gutter labels have canon room.

### 11. X-axis tick label format — `'84` apostrophe-year is a new convention; confirm

- **Reference:** GDP/inflation x-ticks render full 4-digit years (`2024`,
  `2025`, `2026`) in Manrope 12px. The mini-charts use EARLIEST/asOf stamps,
  not year ticks.
- **Drift:** fiscal plates render `'84`, `'89`, … `'31` (apostrophe + 2-digit).
  On a 40-year span this is defensible — full 4-digit years every 5 years would
  be fine too, but `'84` is tighter and reads cleanly. This is a *reasonable*
  divergence driven by the long horizontal axis, NOT a drift to correct
  blindly.
- **Fix / decision:** keep the `'YY` short-year format for the long-history
  fiscal plates (it's the right call for a 40-year axis), but make it
  **consistent**: all five plates use `'YY`, set at the corrected 12px full-ink
  tick treatment from Items 1–2. Do NOT mix `'84` short-year on the long plates
  with anything else. The fiscal-year-vs-calendar-year question (FY1984 labeled
  `'84`) is an editorial/data-labeling call for editorial-director, not a visual
  drift — flag it to them, but visually `'YY` is fine.

### 12. Number formatting on the balance plate — confirm `$B` suffix convention

- **Reference:** canon (design-system §2 "Units stay with their number":
  `$1.2B` not `$1.2 B`). The y-tick formatter in `format.ts` handles currency
  scaling; topmost tick carries the unit.
- **Drift:** Plate1 topmost y-tick reads `+40B` (no `$`), intermediate ticks
  bare numbers (`-40`, `-80`…), and the latest-actual label reads `-$36.3B`
  (with `$`). So the *axis* uses `B` and the *callout* uses `$…B` — slightly
  inconsistent. Plate5 uses `1,600B` on the axis and `$1,482B` on the callout.
- **Fix (minor, consistency):** put the currency mark on the **topmost y-tick
  only** to match the "unit on the top tick" canon: `+$40B` (Plate1),
  `$1,600B` (Plate5); leave intermediate ticks as bare scaled numbers. The
  callout keeps `$…B`. This makes the axis self-document its unit the way the
  inflation `%`-on-top-tick does, and the callout's `$` then reads as
  consistent with the axis's top-tick `$`.

---

## Summary table for chart-builder

| # | Item | Files | One-line fix |
|---|------|-------|--------------|
| 1 | Dimmed tick labels/marks | Plate1–5 | Delete `opacity: 0.7` on tick labels, `opacity: 0.4` on tick marks → full ink |
| 2 | Tick font size | Plate1–5 | x-tick labels 11px → 12px |
| 3 | "Forecast" label treatment | Plate1–5 | Remove `small-caps`; uppercase string, 600 weight, 0.18em tracking, full ink |
| 4 | Forecast divider dash | Plate1–5 | `4 3` → `4 2`; keep 0.40 stroke-opacity, make uniform |
| 5 | Latest-actual numeric label | Plate1–5 | 11px → 12px Plex Mono; de-collide Plate2's two dots |
| 6 | Terminus labels clip | Plate2–4 | `M_R=96`; term label 12→13px Manrope 600 |
| 7 | Annotation + leader dimmed | Plate3, Plate4 | Delete label `opacity: 0.7` + leader `stroke-opacity: 0.45`; 11→12px |
| 8 | Segment labels opacity-stepped | Plate1, Plate5 | Drop opacity; hierarchy by weight (600/400), 13px full ink |
| 9 | On-canvas TK placeholders | Plate1–5 | Render TK `<text>` in `--ink-placeholder` (#8A8A8A) or gate to null |
| 10 | Non-canon margins | Plate1–5 | Move to `M_L=56 M_R=96 M_T=44 M_B=40` |
| 11 | `'YY` x-tick format | Plate1–5 | Keep `'YY` (right for 40yr axis); make uniform; FY-label is editorial's call |
| 12 | `$B` axis/callout consistency | Plate1, Plate5 | `$` on topmost y-tick only |

The fastest path: items 1–4, 7, 8 are pure `<style>`-block edits (delete
opacity lines, fix font-sizes, fix the forecast-label rule, fix the dash) and
clear ~80% of the visible drift in one pass across the five files. Items 5, 6,
10 are geometry/placement. The principle behind all of them is one sentence:
**these plates dimmed their chrome with opacity and shrank it 1px; canon chrome
is full-strength pure ink at 12px, and hierarchy comes from weight, never from
fading the ink.**
