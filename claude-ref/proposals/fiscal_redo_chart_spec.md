# Fiscal page — five new chart plates: art-director visual spec

## Revision 2 — defect fixes + forecast convention change (2026-06-02)

This revision supersedes the convention and three plate specs below after
Jay reviewed the rendered plates on dev and benchmarked them against a
Desjardins fiscal note. **Decision: KEEP single-series (no vintage overlay);
fix the rendered defects; move forecast treatment to the Desjardins
convention.** Where this revision conflicts with Sections A–F below, this
revision governs; the superseded passages are marked inline.

### R2.0 What changed and why — at a glance

| # | What | Why |
|---|---|---|
| R2.1 | **Forecast convention replaced.** Drop dotted forecast lines and hatched forecast bars entirely. New convention = one **vertical dashed divider** at the actual/forecast boundary + a small **`Forecast`** label above the projection region. Data line/bars stay **one consistent style** across the boundary. | Jay benchmarked Desjardins, which never dots lines or hatches bars. The divider + label carries the forecast signal; the trace itself stays honest and continuous. This supersedes the A.8 dotted/hatched convention and **applies retroactively** to the existing drift panels (`Panel2BalancePctGDP`, `Panel6DebtToGDP`) — they migrate to this divider convention, no longer to `1 3` dotted. |
| R2.2 | **Plate 5 (issuance) becomes history-only.** Drop the partial T-bill forecast bars from the stacked total. No forecast divider on this plate. | Only T-bills had a forecast; bonds and retail were history-only, so the stacked-total forecast bars cratered ~$1,480B → ~$280B, reading as an 80% debt collapse. You cannot honestly stack a total when only one segment has a forecast. |
| R2.3 | **Plates 2 & 3 abandon the forced shared axis.** Each chart gets a **tight axis fitted to its own data** (Desjardins discipline). Expenses must show the FY21 COVID spike (~28%) **honestly, un-clipped**. | The forced shared 12–26% axis clipped the COVID expense spike at the 26% ceiling (a visual lie) and squished revenue (14–16.6%) into a flat line in the bottom third. The matched-pair shared-scale rule (old C/Plate 3) is **revoked.** See R2.5 for the merge-vs-separate recommendation. |
| R2.4 | **Plate 1 (balance) must plot the budget-balance TOTAL, with history.** No all-forecast chart. Balance total is the headline (Desjardins Graph 1 = balance bars from a zero line); the operating/capital split is the secondary composition read. | The rendered plate was all-forecast (FY24-25 opex null) and showed opex/capex diverging around zero but never plotted the deficit total the chart is about. Backend is adding `frt_federal_balance_total` ($B, FRT history + SEU forecast). |
| R2.5 | **Latest-actual value gets a numeric data label** on every plate (Desjardins labels the current value). Numeric labels are data, not prose — fine to author. | Desjardins convention; helps the reader anchor the latest real number at the divider. |

### R2.1 The new forecast convention (CANON — replaces A.1, A.2, A.6, A.8)

The forecast signal is carried by **chrome at the boundary**, not by texture
on the data. The data trace — line or bars — renders in **one consistent
style across the entire x-domain**, history and forecast identical.

**The divider (required on every projected chart):**

| Property | Value |
|---|---|
| Form | Single **vertical dashed line**, full plot height (`PLOT_Y0` → `PLOT_Y1`). |
| Stroke | `var(--ink)`, `stroke-width: 1`, `stroke-dasharray: 4 3`, `stroke-opacity: 0.40`. |
| Position | At the x of the **boundary** — render it in the gutter between the last actual and first forecast period. For lines: at the x of the first forecast period. For bars: centered in the gap between the last actual bar and first forecast bar. |
| Z-order | Behind the data, above the gridlines. |

**The label (required):**

| Property | Value |
|---|---|
| Text | `Forecast` (title case, one word). `[ANNO TK]` if the writer wants different wording; default `Forecast`. |
| Type | Manrope 600, 11px, micro-caps, `0.14em` tracking, pure ink @ `opacity: 0.55`. |
| Placement | Above the plot frame, in the **projection region** (right of the divider), `text-anchor: start`, anchored at `dividerX + 6`, baseline `PLOT_Y0 - 6`. The label sits over the forecast zone so its position reinforces which side is projected. |

**The trace — one consistent style across the boundary:**

- **Lines:** `stroke: var(--ink)`, `stroke-width: 1.5`, **solid, end to end.** No
  dotting, no weight change at the seam. One continuous solid line.
- **Bars:** `fill: var(--ink)` solid, no stroke, **end to end.** No hatch, no
  outline, no opacity tint on forecast bars. One consistent bar treatment.
- **No projection-zone wash.** The divider + label is the whole signal; a wash
  is redundant ink. (This also removes the A.4/A.6 wash exception for stacked
  bars — not needed once forecast bars look identical to actuals.)

**Red latest-print dot — KEEP (this was good).** One 4px MTA-red dot at the
**last real datapoint** (line: on the last actual vertex; bar: centered on the
top of the last actual bar). This is the one red moment on the chart and it
marks "here is the last real number." It sits just left of (or on) the divider.

**Latest-actual numeric label — NEW.** Place a numeric data label at the last
actual point: Plex Mono 400, 12px, pure ink, positioned just above/beside the
red dot without colliding with it (lines: above-left of the vertex; bars:
above the bar top, above the red dot). Value formatted to the series'
precision (e.g. `-$61.9B`, `16.6%`). This is the single on-canvas number
besides the axis; do not also label forecast-terminus values unless the writer
asks. Numeric, so it is data not prose — author it directly, no TK.

**Retroactive scope.** The existing `Panel2BalancePctGDP` and `Panel6DebtToGDP`
panels must migrate to THIS convention (solid trace across the boundary +
vertical divider @ `4 3`/0.40 + `Forecast` label + red latest dot + latest
numeric label), dropping their grandfathered `5 3` dotted forecast segments and
Panel6's zone wash. Queue this with the five-plate build, not a separate sweep.

### R2.2 Plate 5 — history-only (replaces C/Plate 5 forecast handling)

Build Plate 5 as a **history-only** stacked-bar composition. **Drop the
partial T-bill forecast bars from the stacked total** — they made the total
crater because bonds and retail had no forecast. No vertical divider, no
`Forecast` label on this plate. State in the component header that the
actuals-only scope is **intentional** (only one instrument had a forecast;
stacking a partial-forecast total is dishonest), so a reviewer does not read
the missing divider as a dropped convention.

Everything else in C/Plate 5 stands: stacked bars (not area), 2–3 instrument
buckets differentiated by **texture not hue** (solid / hatch / dot-screen),
$B level, nice round ticks, **tight axis fitted to the actuals only** (no more
headroom reserved for a forecast that no longer renders). Red latest dot
centered on the top of the last (most recent actual) stacked bar; latest-total
numeric label above it per R2.5.

### R2.3 Plates 2 & 3 — tight independent axes (replaces the matched-pair shared-scale rule in C/Plate 3)

The forced shared y-domain is **revoked.** Each chart is fitted **tight to its
own data** with nice round ticks (Desjardins discipline):

- **Plate 2 (revenues):** domain hugs the revenue range (≈ 14%–17%; let the
  data set it, nice 1pp strides, topmost tick `%`). The line should fill the
  plot vertically, not sit in the bottom third.
- **Plate 3 (program expenses):** the domain **must reach the true FY21 COVID
  peak (~28%) un-clipped.** No ceiling that clips the spike. Fit the axis so
  the spike reaches its real top with a hair of headroom (e.g. ~13%–30%, nice
  strides). The spike is the chart's most important honest feature; never
  clamp it.

Geometry (viewBox, margins, x-domain, gridline count, divider x) may still
**rhyme** between the two for a designed-pair feel, but the **y-domains are now
independent.** Do not pin a shared y-domain constant.

### R2.5 Plates 2 & 3 — recommend MERGE into one two-line chart

**Recommendation: merge revenues + program expenses into a single
two-line chart on one shared axis** (the standard way to show the
deficit gap), and retire the two-separate-plates layout for this pair.

Rationale:

- The deficit IS the vertical gap between revenue and expense as a share of
  GDP. On two separate tight-axis charts with **different** y-domains, that gap
  is no longer readable by eye — the whole reason the gap matters is lost. The
  old spec tried to preserve the gap with a forced shared axis; that produced
  the squish/clip defect. A single chart with **both lines on one honest axis**
  is the correct resolution: the gap is the shaded/visible distance between the
  two lines, directly legible, and the axis fits both series tightly without
  clipping (the combined range ≈ 14%–30% to contain expenses' COVID spike).
- This is the Desjardins / standard fiscal convention for the revenue-expense
  picture, and it spends one plate instead of two.

**Two-line treatment (monochrome discipline, no second hue):**

| Element | Treatment |
|---|---|
| Revenue line | `var(--ink)`, 1.5px solid. Direct terminus label `[CAPTION TK: Revenue]`, Manrope 600. |
| Expense line | `var(--ink)`, 1.5px solid. Differentiate from revenue by **a direct terminus label + a small inline label at a mid-segment node**, not by color or dash — but if the two lines weave and a single end-label is ambiguous, the **secondary** line (expenses) may take a 1.5px **long-dash `6 3`** to separate the pair. Lines differ by **label-first, dash-as-fallback** — never hue. (Per multi-series adaptation in `canon_reference_panel.md`.) |
| The gap | Optional faint `rgba(21,23,26,0.05)` fill **between** the two lines where expense > revenue (the deficit region), as a single neutral wash — this is the one wash permitted because it encodes the editorial quantity (the gap), not chrome. Bring the fill density to art-director on first render; default is no fill, lines only, if the gap reads cleanly. |
| Forecast | One vertical divider + `Forecast` label per R2.1, shared by both lines (same boundary x). |
| Red + numeric | Red latest dot + numeric label on **each** line's last actual point (two dots, two numbers — both are real latest values; this does not over-spend red because each marks a distinct series' latest actual). |

If editorial-director prefers to keep two separate plates for page-rhythm
reasons, fall back to R2.3 (two tight independent-axis charts) — but the
**recommended** build is the single merged two-line chart. Flag the choice to
editorial-director; default to merge.

### R2.4 Plate 1 — balance total is the headline, with history (replaces C/Plate 1 form)

Build to the new backend series `frt_federal_balance_total` ($B, FRT history +
SEU forecast). The **budget-balance total is the primary, history-bearing
read** (Desjardins Graph 1 = balance as bars from a zero line). Do **not** ship
an all-forecast chart.

**Form decision — balance-total bars from a zero line (primary), with the
operating/capital split as composition:**

- **Primary:** signed vertical bars per fiscal year = **total budgetary
  balance** (deficit below zero, surplus above), solid ink, from a structural
  zero line (1.5px ink, full opacity). This is the deficit number the chart is
  about; it spans **history + forecast** in one consistent bar style (R2.1).
- **Composition (secondary):** show the operating/capital split as the
  **internal segmentation of each balance bar** — i.e. each total-balance bar
  is a signed stack of operating + capital segments, differentiated by
  **texture not hue** (operating = solid ink; capital = hairline cross-hatch /
  dot-screen). The segment heights sum to the total bar, so the headline total
  and the composition are the same shape read two ways. Direct in-gutter labels
  name `Operating` / `Capital` with weight contrast.
- **If the texture stack proves too busy** at render (the capital segment is
  often small), fall back to: solid balance-total bars as the headline, plus a
  **thin operating-balance line overlay** (1.5px, distinct via a `6 3` dash and
  a direct label) so the operating-vs-total divergence is visible without
  segmenting every bar. Bring this call to art-director on first render. Either
  way, the **total balance is the dominant shape**, not the components.

**Forecast:** one vertical divider + `Forecast` label per R2.1 at the FRT/SEU
boundary. Forecast bars render identical to actual bars (solid ink, no hatch).

**Red + numeric:** red latest dot centered on the top edge of the **last actual
balance bar**; latest-balance numeric label above it per R2.5 (e.g. `-$61.9B`).

**Unit:** $ billions (the bifurcated frame is debated in dollar terms). Zero
line is structural. y in `$NNB` signed, fitted tight to the data with nice
strides, topmost tick carries the unit.

Old C/Plate 1's diverging two-texture stack stands as the composition idea, but
the **total balance must be the readable headline shape and history must be
present** — those two corrections govern over any conflicting detail below.

---

Status: draft for chart-builder. Author: art-director. Date: 2026-06-02.
Authority: subordinate to `design/design-system.md` (Vignelli canon) and
`design/canon_reference_panel.md` (Tier-3 worked example). Where this spec
is silent, those documents govern.

Scope: five new Tier-3 plates appended below the existing fiscal plates.
Nothing is removed in this pass. This spec also **establishes the
history -> forecast rendering convention as reusable canon** (Section A),
because the existing fiscal panels drifted on the dash pattern and the
break-marker treatment and we are about to add five more charts that must
not re-drift.

All reader-facing copy (titles, captions, annotation wording) is a
placeholder here. The writer authors it through the three gates. Slots are
marked `[TITLE TK]` / `[CAPTION TK]` / `[ANNO TK]`.

---

## A. The history -> forecast convention (SUPERSEDED by R2.1 — see top of file)

> **SUPERSEDED 2026-06-02 by R2.1.** The dotted-line / hatched-bar convention
> defined in this Section A (and summarized in A.8) is REVOKED. Forecast is now
> signalled by a vertical dashed divider + `Forecast` label only; the data
> trace stays one consistent style across the boundary. Read R2.1 at the top of
> this file and ignore the dotted/hatched mechanics below. The latest-print red
> dot (A.2/A.6) survives. Section A is retained only for the build-history
> record.

This is the single most important deliverable. It must be reusable: every
fiscal plate that carries a DoF/PBO projection inherits it verbatim, and any
future projected chart in any section copies it. Define it once, here.

### A.0 Why we are pinning this now

The two shipped fiscal line panels (`Panel2BalancePctGDP`,
`Panel6DebtToGDP`) already invented a forecast treatment, and they already
disagree:

- Proj line: both use `stroke-dasharray: 5 3` (good — keep this).
- Break separator: Panel2 uses `2 3` at 0.35 opacity; Panel6 uses `3 3` at
  0.4 opacity (drift).
- Projection zone wash: Panel6 has a `rgba(21,23,26,0.03)` wash + a
  "SEU 2026 projection" label; Panel2 has neither, using end-of-line
  "Historical" / "Projection (SEU 2026)" labels instead (drift).

Five more charts will compound the drift unless we pin one convention. The
rules below are that convention. The two existing panels are **conformant
enough to leave in place** for now (their proj dash already matches); a
later sweep aligns their break-marker and zone treatment to A.3/A.4. Do not
touch them in this pass.

### A.1 The core idea

History is rendered **solid**; forecast is rendered **dotted**, in the
**same pure-ink hue, at a lighter stroke weight**. The eye reads one
continuous trace whose texture changes at the handoff — never two differently
*colored* series. Hue is never recruited to mark forecast (canon: hue is
brand, not data). Texture (solid vs dotted) and weight do the work.

### A.2 LINE charts — exact treatment

| Element | Treatment |
|---|---|
| History line | `stroke: var(--ink)`, `stroke-width: 1.5`, solid, `stroke-linejoin/linecap: round`, `vector-effect: non-scaling-stroke`. |
| Forecast line | `stroke: var(--ink)`, `stroke-width: 1.25`, **`stroke-dasharray: 1 3`** (a true dotted rhythm, not a dash), `stroke-linecap: round` (so each dot renders as a circle, not a tick), `vector-effect: non-scaling-stroke`. |
| Handoff continuity | The forecast path **starts at the last actual point** (shares the junction vertex), so there is no visual gap at the seam. Build the forecast path with the last actual as its first `M` vertex. |
| Handoff marker | The junction point (last actual = first forecast) carries the **single MTA red latest-print dot**, 4px radius, filled, no stroke. This is the one red moment on the chart and it sits exactly at the history/forecast seam — which is editorially perfect: "here is the last real number; everything right of here is a projection." |

**Decision — dotted, not dashed, for lines.** The brief asks for the
forecast "dotted." Honor that literally and use it to *differentiate from
the existing dashed precedent on purpose*: `1 3` round-cap dots read as
"projected / not-yet-real" more legibly than the `5 3` dash, and the dot
rhythm visually rhymes with the latest-print dot at the seam. The existing
two panels' `5 3` dash is grandfathered; new canon going forward is `1 3`
dotted. When the alignment sweep happens, the two existing panels migrate
to `1 3` too.

### A.3 The forecast handoff — vertical rule (REQUIRED on every projected chart)

A single **vertical hairline** marks where actuals end and projection begins.

| Property | Value |
|---|---|
| Stroke | `var(--ink)`, `stroke-width: 1`, `stroke-dasharray: 2 3`, `stroke-opacity: 0.30` |
| Position | At the x of the **first forecast period** (the junction year). Drawn full plot height, `PLOT_Y0` to `PLOT_Y1`. |
| Z-order | Behind the data line, above the gridlines. |
| Label | Above the plot frame, one short stamp. Manrope 600, 11px, micro-caps, `0.18em` tracking, pure ink at `opacity: 0.55`, `text-anchor: start`, anchored at `breakX + 4`, baseline `PLOT_Y0 - 6`. Literal: **`FORECAST`** (one word; not "SEU 2026 projection" — the vintage lives in the source line, not on the canvas). `[ANNO TK]` only if the writer wants different wording; default `FORECAST`. |

Pin these constants so all five plates match. Name them in the component
header comment as the shared forecast constants.

### A.4 No projection-zone wash by default

The Panel6 `rgba(21,23,26,0.03)` zone tint is **dropped from the new
canon.** The vertical rule + dotted line already carry the handoff; the wash
is redundant ink that fights the Tufte data-ink ratio. (Panel6 keeps its
wash until the alignment sweep; new plates do not add one.) One exception:
**stacked-composition charts** (Plates 1 and 5) where the dotted-line device
is unavailable — there the forecast bars need their own texture cue, handled
in A.6 below, and a faint zone wash is permitted as a secondary reinforcement
(see A.6).

### A.5 Direct labels at the terminus (lines)

One direct end-of-line label per trace, per canon Rule 10 (Manrope 600 13px
pure ink). Because history and forecast are one trace, there is **one**
direct label, at the forecast terminus, naming the series — e.g.
`[CAPTION TK: series name]`. Do **not** label both "Historical" and
"Projection" as two end-of-line stamps (Panel2's approach); that reads as a
two-series legend, which the single-trace device explicitly avoids. The
`FORECAST` stamp above the break rule is what tells the reader the right
segment is projected; the terminus label names the indicator.

### A.6 BAR charts — forecast treatment (Plates 1 and 5, and any bar plate)

Bars cannot go "dotted" cleanly, so the forecast cue is **outline + texture**,
not opacity-alone (opacity drift is what made the existing operating-balance
panels inconsistent). The convention:

| Bar kind | Fill | Stroke |
|---|---|---|
| Actual / historical bar | `fill: var(--ink)` (solid black), no stroke. | — |
| Forecast / projected bar | `fill: none` **with a hairline hatch** OR `fill: var(--ink)` at `fill-opacity: 0.32` — **choose hatch (preferred)**. | `stroke: var(--ink)`, `stroke-width: 1`, solid outline. |

**Decision — hatch the forecast bars.** Define one SVG `<pattern>` (a 45°
hairline hatch: 1px pure-ink lines, `stroke-opacity` ~0.9, spaced ~5px) and
fill forecast bars with it, plus a 1px solid pure-ink outline. Reasoning:

1. A hatched, outlined bar reads unmistakably as "estimated, not measured" —
   it is the bar-chart analogue of the dotted line, both being broken-texture
   ink on white.
2. Pure opacity-tint (the `0.32`/`0.45` the existing panels use) reads as
   "smaller / less important," not "projected," and tints drift in value
   between authors. A hatch is a categorical signal, not a magnitude signal.
3. It stays strictly monochrome — pure ink on white, no hue.

The fallback `fill-opacity: 0.32` solid is the documented escape hatch only
if a hatch pattern proves too busy at a given bar width; bring that call back
to art-director. Default is hatch.

For bar charts, also draw the **A.3 vertical break rule + `FORECAST` stamp**
at the first forecast period (it sits in the gutter between the last actual
bar and the first forecast bar). On stacked-composition bar charts (Plates 1
and 5), a faint `rgba(21,23,26,0.03)` zone wash right of the break rule is
**permitted** as secondary reinforcement, since the per-segment hatch can be
visually subtle in a stack — this is the one place A.4's no-wash default is
relaxed.

**Latest/handoff red on bars.** The single MTA red moment on a bar chart is
the **last actual bar's top edge is not red** — instead, place the 4px MTA
red dot centered on the top of the **last actual bar** (the equivalent of the
line's latest-print dot). Do not red-fill an entire bar (that would read as a
data category, and it burns the one-red-per-chart budget on a full shape).
Exception: a single editorially-anchored bar (e.g. the fiscal-anchor year in
the existing Panel4) may take a red fill — but that is a bespoke editorial
call, signed per-panel, not the default. Default for these five = red dot on
the last actual bar's top.

### A.7 Accessibility + hover

Every data point (actual and forecast) carries a native SVG `<title>` via a
transparent hit-area `<circle>` (lines) or the bar `<rect>`'s own `<title>`
(bars). Forecast points' titles are suffixed `(projected)` or `(SEU 2026
proj.)`. `aria-label` on the `<svg>` names the indicator, the actual window,
the forecast window + vintage, and the latest actual value. Zero client JS.

### A.8 Convention summary (the reusable canon, one block)

```
FORECAST CONVENTION (fiscal + any projected chart)
  Lines:
    history  -> ink 1.5 solid
    forecast -> ink 1.25 dotted (stroke-dasharray 1 3, round cap)
    forecast path starts at last actual vertex (no seam gap)
  Bars:
    history  -> ink solid fill, no stroke
    forecast -> ink hairline hatch fill + 1px ink solid outline
  Handoff (both):
    vertical rule at first forecast x: ink 1px, dasharray 2 3, opacity 0.30
    stamp above frame: "FORECAST", Manrope 600 11px micro-caps 0.18em, ink @0.55
  Red moment (both):
    one 4px MTA red dot at the last-actual point
    (line: on the junction vertex; bar: centered on last-actual bar top)
  No projection-zone wash (exception: stacked-composition bar charts may add
    a faint rgba(21,23,26,0.03) wash right of the break rule)
  Direct label: ONE terminus label naming the indicator (not Hist/Proj pair)
```

---

## B. Shared treatment across all five plates

- **Tier:** Tier-3 workhorse, hand-tuned per `canon_reference_panel.md`.
  None of these is a hero. viewBox `720 x 405`, `aspect-ratio: 16/9`,
  `preserveAspectRatio="xMidYMid meet"`, 1px pure-ink hairline plot frame.
- **Color:** Data is pure ink (`var(--ink)`) only. The fiscal section accent
  is `--section-accent-fiscal` — but per canon it appears **only on chrome
  off-canvas** (the plate-number numeral in the chartbook eyebrow), **never
  on data.** The only on-canvas color is the single MTA red latest/handoff
  dot. (Note: `design-system.md` Section 3 currently lists section accents
  for the original 7 sections; `--section-accent-fiscal` is the 8th-section
  token — confirm it resolves in `tokens.css`; if absent, eyebrow plate
  numeral falls back to `--accent` like every other plate numeral, which is
  fine. Flagged for token housekeeping, not a blocker.)
- **Axes:** Y-tick labels Plex Mono 400 12px pure ink @0.7 opacity,
  right-aligned in the left gutter, topmost tick carries the unit (`%`, `$NNB`).
  X-tick labels Manrope 400 12px pure ink @0.7. 3–5 gridlines, ink @0.18
  `stroke-opacity`, horizontal only. Zero line (where data crosses zero) at
  1.5px pure ink, full opacity, heavier than gridlines.
- **Title voice:** sentence-form, terminal period, one verb, names the
  finding (writing-style.md Sec 4.2). All `[TITLE TK]` — writer authors
  through the gates. Candidate phrasings below are direction-only, not final.
- **Annotations:** words not sentences (canon). Hand-placed in white space.
  All wording `[ANNO TK]`.
- **Source line / methodology:** lives on the chartbook unit, NOT inside the
  SVG. Charts that compute a ratio (% of GDP) carry the methodology note per
  `design-system.md` "Methodology discipline."

---

## C. Plate-by-plate specs

### Plate 1 — Budget balance: operating vs capital composition

**Editorial job:** show the deficit/surplus over time AND make the
operating/capital split visible (the Carney bifurcated-budget frame).
History + forecast.

**Form decision — stacked bars to the balance, with a balance line overlay.**
Recommended construction:

- **Stacked vertical bars per fiscal year**, one bar = total budgetary
  balance, decomposed into two stacked segments: **operating balance** and
  **capital balance**. Because both can be negative (deficits), use a
  **diverging stack around the zero line**: operating-deficit segment grows
  downward from zero, capital-deficit segment stacks below it (same downward
  direction); any surplus segment grows upward. This is a signed stacked bar.
- Segment differentiation **without a second hue**: operating segment =
  solid ink fill; capital segment = ink at a **distinct hairline hatch**
  (different angle from the forecast hatch — e.g. operating solid, capital
  cross-hatch / dot-screen). The two segments differ by **texture**, not
  color. Direct in-gutter labels name them (`Operating` / `Capital`),
  Manrope 600/400 weight contrast.
- This is a **two-category composition**, which is the canon's
  weight/texture-differentiation case, NOT a forbidden multi-color chart.
  Two textures + a zero line is legible and stays monochrome.

**Why not grouped bars or a line + area:** grouped bars lose the "they
compose the total" reading, which is the whole point of the bifurcated frame.
A balance line with a composition area underneath was considered, but with
both components frequently negative the area fills collide visually below
zero; the signed stacked bar is the honest, legible form.

**Forecast:** apply A.6 (hatched/outlined forecast bars + break rule +
`FORECAST` stamp). Because this is a textured stack, the capital-segment
hatch and the forecast hatch must be visually distinguishable — resolve by
making **forecast = outline-only emphasis** (1px solid ink outline on each
segment, segment interior keeps its actual/operating-vs-capital texture but
at reduced density right of the break). Bring the exact pattern set to
art-director after a first render; this is the one plate where texture
layering needs an eyes-on tuning pass.

**Unit:** $ billions (level) — the bifurcated frame is debated in dollar
terms (the ~$94B PBO reclassification figure). Keep it in $B, not % of GDP,
so it reads against the policy debate. Zero line is structural here.

**Axes:** y in `$NNB` (signed; e.g. `-60`, `-40`, `-20`, `0`, `+20`,
top tick `+20B`). x = fiscal years, label every 2nd year + terminal.

**Title direction (TK):** names the operating/capital divergence or the
anchor. `[TITLE TK]`.

**Note on existing components:** `Panel5OperatingCapital` (placeholder,
grouped DoF-vs-PBO bars) and `Panel4OperatingBalance` (operating-balance
bars) already exist and overlap this editorial territory. This Plate 1 is the
**composition** view (opex + capex compose the balance), which neither
existing panel does. Editorial-director resolves whether Plate 1 supersedes
or sits alongside them; that is not an art-direction call. Build Plate 1 as
specified; flag the overlap.

---

### Plate 2 — Federal revenues, % of GDP

**Form:** single-series line, long history + forecast. Pure A.2 line
treatment.

**Unit:** % of GDP. y-axis fitted to the historical range with nice round
ticks (likely ~14%–18% band; let the data set the domain, nice 1pp or 2pp
strides, topmost tick carries `%`).

**Forecast:** dotted line + break rule + `FORECAST` stamp + single red
handoff dot. Direct terminus label names the series.

**Annotations:** at most one or two reference points (`[ANNO TK]`), words
only. Restraint — a clean revenue ratio line does not need heavy annotation.

**Title direction (TK):** names where revenue-to-GDP sits / trends.

---

### Plate 3 — Federal program expenses, % of GDP

**Form:** single-series line, long history + forecast. **Matched pair with
Plate 2** — they sit adjacent and must read as a designed pair.

**The matched-pair rule (Plates 2 & 3):**

- **Identical geometry:** same viewBox, same margins, same x-domain (same
  start year, same forecast horizon), same gridline count.
- **Shared y-axis scale IF the magnitudes are comparable.** Revenues and
  program expenses are both in the mid-teens % of GDP, so **force an
  identical y-domain across both plates** (e.g. both 12%–26%, or whatever
  envelope contains both series with headroom). This lets the reader compare
  the two charts by eye — the gap between the lines across the two plates is
  the deficit, and an honest shared scale makes that legible. This is the
  small-multiples **Mode A** discipline applied across two adjacent
  single-panel plates.
- Identical forecast treatment, identical break-rule x (same junction year),
  identical `FORECAST` stamp.
- The only thing that differs is the data and the indicator name on the
  terminus label.

**Do not** render them as a literal two-panel small-multiple in one
component unless editorial-director wants them fused; the brief says five
separate plates, so build two components that share a pinned geometry +
y-domain constant block. Document the shared constants in both headers.

**Title direction (TK):** Plate 3 names where program-expense-to-GDP sits /
trends; ideally the pair's titles rhyme structurally (writer's call).

---

### Plate 4 — Federal debt, % of GDP

**Form:** single-series line, long history + forecast. Pure A.2 line.

**Overlap flag:** `Panel6DebtToGDP` already renders federal debt % of GDP
(1980→2031, SEU 2026). This Plate 4 likely **supersedes or duplicates** it.
Two options for chart-builder + editorial-director:

1. **Preferred:** treat Plate 4 as the A.2/A.8-conformant **replacement** for
   Panel6 — rebuild Panel6's render layer to the new dotted-forecast canon
   (migrate `5 3` dash → `1 3` dotted, drop the zone wash, align the break
   rule to A.3, keep the verified data constants and annotations). This kills
   the drift rather than adding a sixth near-duplicate.
2. If editorial wants the old Panel6 left untouched this pass, build Plate 4
   fresh to A.8 and tag Panel6 for the later alignment sweep.

Either way, Plate 4's data is the existing verified `fiscal_debt_to_gdp.json`
+ SEU 2026 projection. Keep the four durable reference annotations (1990s
peak, pre-GFC trough, COVID peak, latest actual) — words + value only.

**Unit:** % of GDP, y-domain ~20%–75% (Panel6's existing nice 10pp ticks are
correct), topmost tick `%`.

**Title direction (TK).**

---

### Plate 5 — Debt issuance by instrument

**Editorial job:** composition of gross issuance (or stock) over time across
2–3 instrument buckets — e.g. **treasury bills / marketable bonds** (+ a
third like green bonds / retail if the data supports it). Composition over
time.

**Form decision — stacked bars, not stacked area.**

- **Stacked vertical bars per fiscal year**, segments = instrument buckets.
- Reasoning: issuance is a discrete annual (or quarterly) program quantity,
  not a continuous flow; bars read as "this much was issued this period,"
  which is the correct mental model. Stacked area implies a continuous
  interpolated quantity between periods, which misrepresents a discrete
  issuance program. Tufte/Vignelli honesty: bars for discrete quantities.
- 2–3 segments differentiated by **texture, not hue** (the canon line):
  bottom segment (largest, e.g. marketable bonds) = solid ink; next
  (treasury bills) = hairline hatch; third (if present) = denser dot-screen
  or cross-hatch. Direct in-gutter or terminus labels name each bucket with
  weight contrast. Three textures is the practical ceiling for legibility —
  if the data needs a 4th bucket, group the smallest into "Other."

**Forecast:** if issuance has a projected horizon (Debt Management Strategy
forward plan), apply A.6 bar-forecast treatment + break rule + `FORECAST`
stamp + faint zone wash (permitted exception, A.4). If issuance is
actuals-only with no forecast, no break rule — but state that explicitly in
the component header so a reviewer knows the omission is intentional, not a
missed convention.

**Unit:** $ billions gross issuance (level). Stacked total is the program
size; y-domain fitted with nice round ticks, topmost `$NNB`.

**Latest red moment:** 4px MTA red dot centered on the **top of the last
actual stacked bar** (the total-issuance terminus).

**Title direction (TK):** names the issuance mix shift (e.g. toward/away from
bills vs bonds).

---

## D. Texture/pattern library to define once (chart-builder)

To keep all five (and future) plates consistent, define these SVG
`<pattern>` / dash constants once and reuse. Suggested shared definitions
(exact IDs chart-builder's call):

| Token | Definition | Used for |
|---|---|---|
| Forecast line dot | `stroke-dasharray: 1 3`, round cap, 1.25px ink | every projected line |
| Forecast bar hatch | 45° hairline hatch, 1px ink @~0.9, ~5px pitch | projected bars |
| Composition texture A | solid ink fill | largest stack segment |
| Composition texture B | 45° hairline hatch (distinct angle from forecast hatch, e.g. -45°) | 2nd stack segment |
| Composition texture C | dot-screen or cross-hatch | 3rd stack segment |
| Break rule | vertical, `stroke-dasharray: 2 3`, 1px ink @0.30 | forecast handoff |
| Break stamp | `FORECAST`, Manrope 600 11px micro-caps 0.18em, ink @0.55 | forecast handoff |

The forecast-bar hatch and the composition-segment hatch **must be visually
distinguishable** (different angle and/or pitch) wherever both appear on one
chart (Plates 1 and 5). This is the one layering risk in the set; resolve it
with an eyes-on render pass before sign-off.

---

## E. Build order recommendation

1. **Plate 2 + Plate 3 together** (matched pair, simplest, establishes the
   A.2 line + A.3 handoff canon cleanly on single series). These two
   calibrate the dotted-forecast convention.
2. **Plate 4** (third single-series line; decide Panel6 supersede vs fresh).
3. **Plate 5** (stacked-bar composition + bar-forecast).
4. **Plate 1 last** (signed diverging stack + texture layering — the hardest;
   benefits from the texture library being settled by Plates 5 and the
   pair).

Each plate comes back to art-director for a redline pass before PR
(per `canon_reference_panel.md` order-of-operations step 7), with particular
attention on Plates 1 and 5 texture legibility.

---

## F. Open items flagged (not blockers)

1. `--section-accent-fiscal` token existence in `tokens.css` — confirm or let
   plate numeral fall back to `--accent`.
2. Existing `Panel2BalancePctGDP` / `Panel6DebtToGDP` carry the grandfathered
   `5 3` dash + zone wash; queue an alignment sweep to migrate them to the
   A.8 convention once the five new plates land.
3. Editorial-director to resolve Plate 1 vs existing `Panel4OperatingBalance`
   / `Panel5OperatingCapital` overlap, and Plate 4 vs `Panel6DebtToGDP`
   supersede decision. These are content-architecture calls, not
   art-direction.
4. Data availability for Plate 5 third instrument bucket and forecast horizon
   — backend/researcher to confirm; spec degrades gracefully to 2 buckets /
   actuals-only.
