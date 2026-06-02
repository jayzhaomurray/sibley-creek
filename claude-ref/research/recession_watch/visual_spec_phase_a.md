# Recession Watch — Visual Spec (Phase A)

Authored by art-director, 2026-06-02. Single source of truth for chart-builder + frontend-designer. Spec-only; not yet folded into `design/canon_reference_panel.md` (do that after redline ratification). Accepted defaults (main Claude, 2026-06-02): keep COVID on depth charts clipped+annotated; all four comparators equal weight (envelope); standing top-level page; resting-state callout suppressed.

---

## 1. The chart type — cycle-on-cycle overlay (new canon)

A small-multiple set of four time-aligned overlay charts. Each plots **months since the cycle peak** (x) against a metric (y), with four historical recession paths drawn faint and the current episode drawn bold on top. The reader's whole job is one glance: **does the bold current line sit inside/below the grey envelope, or stay shallow/narrow above it?** Every visual decision serves that single read.

Inherits Tier-3 canon (720×405 viewBox, hairline frame, Plex Mono y-ticks, Manrope x-ticks, gridlines at 0.18 ink). Does NOT inherit the standard multi-series dash rule — differentiation here is comparator-vs-current (one bold + a faint cohort), carried by weight+opacity.

### 1.1 The four charts
| # | Chart | y-metric | y-direction | y-range |
|---|-------|----------|-------------|---------|
| 1 | GDP depth | Real GDP, % change since peak | negative-going (0 at top) | truncated −6%, COVID off-scale |
| 2 | GDP breadth | % of industries contracting | 0–100, up=worse | 0–100 |
| 3 | Employment depth | Employment, % change since peak | negative-going | truncated, COVID off-scale; tune floor to data |
| 4 | Employment breadth | % of industries shedding jobs | 0–100, up=worse | 0–100 |

### 1.2 X-axis — months since peak
- x = 0 at cycle peak, running forward. Domain 0–36 months.
- 1px pure-ink **x=0 PEAK line**, full opacity, heavier than gridlines. Labelled once `PEAK` (micro-caps Manrope 600 11px, 0.18em) top-left above plot.
- X-ticks Manrope 400 12px every 6 months: `0 6 12 18 24 30 36`. Axis unit lives in the eyebrow (`MONTHS SINCE CYCLE PEAK`), not on ticks.
- No vertical gridlines except the x=0 peak line.

### 1.3 Y-axis
- **Depth:** y in %, 0 at top, negative below. Topmost tick `0%`, lower `-2 -4 -6`. Horizontal 1px full-opacity ink line at y=0 (the "at peak / no drawdown" reference the current line hugs in the resting state).
- **Breadth:** y = %, 0 bottom, 100 top. Ticks `0/25/50/75/100%`. Dashed 1px ink reference at 50% (`4 2` dash), label `50% — half contracting` Manrope 600 12px at right.
- Y-ticks IBM Plex Mono 400 12px, pure ink, right-aligned in left gutter.

## 2. Line treatment — comparator cohort vs current
### 2.1 Comparators (the envelope)
- Pure ink, **1px**, `vector-effect: non-scaling-stroke`, `stroke-opacity: 0.28`. Solid, no dash, no markers, no labels. Four at 0.28 read as a grey *range*, not four things.
### 2.2 Current episode (protagonist)
- Pure ink, **2px**, full opacity, `vector-effect: non-scaling-stroke`.
- Single **MTA red #E63946** terminal dot, 4px radius, filled, at the leading end ("you are here, now"). The one red per chart.
- Direct label `Now` (wording→writer) Manrope 600 13px ink, 10px right of dot.
- z-order: current line draws last among data (above cohort, below frame); red dot above current line.
### 2.3 Comparator labelling — DECISION: do NOT label the four lines individually.
- One envelope label per chart, `Past recessions` (wording→writer), Manrope 400 13px ink in clear white space; single 1px ink leader (no arrowhead) only if needed.
- Individual-recession ID lives in the methodology note + native SVG `<title>` on hover. Optional "highlighted comparator" variant (promote e.g. 2008-09 to 0.55 opacity + label) — NOT default.

## 3. Color discipline
One red per chart (current terminal dot), nothing else. Cohort = pure-ink-at-opacity, not a grey hex. No direction tints. The published commentary's red-negative-bars treatment does NOT port here.

## 4. COVID scale problem (depth charts) — DECISION: truncate + off-scale mark.
COVID GDP depth ≈ −13%; others −2% to −5%. Do NOT broken-axis, log-scale, or let COVID set the floor.
- Depth y-floor **−6%** (ticks `0 -2 -4 -6`); employment-depth floor tuned to its data.
- COVID path drawn at 1px/0.28 up to where it exits the floor, then SVG-clipped at the −6% frame edge.
- At clip point: small downward caret `▾` (ink, 0.28) at COVID's x, plus Manrope 400 11px ink annotation BELOW the frame in the x-tick band: `2020 low −13%` (wording→writer).

## 5. Per-chart chrome
- viewBox 720×405, `preserveAspectRatio="xMidYMid meet"`, wrapper `aspect-ratio: 16/9`.
- 1px ink hairline frame; 3–4 gridlines at 0.18 ink; x=0 PEAK line + y=0/50% reference per §1.3.
- Plex Mono y-ticks, Manrope x-ticks, unit on topmost tick only.
- **Chart title:** Manrope 800 19px, sentence-form, terminal period, names the finding, one verb (voice→writer). State-dependent — must read true whether the current line hugs the top (no recession) or dives into the envelope. Pipeline-swappable slot; design reserves the space.
- Eyebrow `MONTHS SINCE CYCLE PEAK` Manrope 600 13px micro-caps 0.22em.
- Native `<title>` on current points (date+value) and on comparator lines (recession name) for zero-JS hover ID.
- **Conditional current-reading callout:** rendered ONLY when the current line enters the envelope (e.g. below −1% depth / above 40% breadth — exact trigger = chart-builder + editorial). Suppressed in the resting state. Manrope 400 15px + 600 anchor word, 1px ink leader ending 7px short of the red dot.

## 6. Design for the resting state (common case = no recession)
Default rendering: current line is a short bold stub hugging the y=0 top line, high above a grey envelope fanning down-and-away. This is information, not absence: "at peak; recessions live down there; we're not in one."
- Do NOT auto-zoom the y-axis to the current line. Axis stays fixed at full comparator range always (−6% depth, 0–100 breadth). A fixed axis is what makes the gap legible; auto-zoom would make a 0.3% wobble look like a cliff (dishonest).
- The `Now` red dot near top-left is the focal point of the resting state.
- Conditional callout stays suppressed; the page status element carries the verdict in words.

## 7. The page
### 7.1 Register — boutique single-instrument (like Atlanta Fed GDPNow), not dashboard-grid. One page-length instrument: headline verdict → four-chart evidence → methodology. Calm, vertical, white space, one idea.
### 7.2 Composition (top→bottom)
- SECTION/MASTHEAD kicker (micro-caps, section-number numeral in MTA red); `Recession Watch` display-xl 800; 1px ink rule.
- **VERDICT slot:** one-line current verdict (copy→writer). Manrope 200 ExtraLight ~24px, max ~40ch, breaks across ≤2 lines. `AS OF <date>` Plex Mono micro-caps stamp right-aligned. RESERVE 2-line height (don't let layout jump between a 1-line all-clear and a 2-line fired verdict). 1px ink rule.
- **2×2 grid** of the four charts.
- **METHODOLOGY/footnote zone.**
- 2px MTA red colophon rule + publication mark.
### 7.3 The 2×2 grid — DECISION.
- Left column = depth, right column = breadth; top row = GDP, bottom row = employment. Columns answer "how deep/how broad," rows answer "output/jobs."
- Shared identical x-domain (0–36) + identical x=0 peak line across all four. Breadth panels share 0–100 exactly; depth panels share −6% floor IF employment-depth data supports it (else Mode B per-panel y). **Every panel carries its own y-tick labels regardless** (Mode B non-negotiable).
- 1px pure-ink hairline cross dividing rows and columns. Column gap ≥36px for per-panel y-tick gutter.
- One source line at the bottom of the whole grid. Per-chart eyebrows stay per chart.
- Narrow viewport: collapse to 1-column stack in reading order 1→2→3→4. Charts keep 16:9, don't reflow internally.
### 7.4 Verdict slot
- Single editorial line (copy→writer). Manrope 200 ~24px pure ink, max ~40ch. AS OF stamp Plex Mono micro-caps. State-dependent; reserve 2-line height. **NO traffic-light, gauge, or status-color chip — verdict is words. Explicitly forbidden: green/amber/red recession-risk indicator.**
### 7.5 Methodology zone (mandatory — derived/multi-source/bridged instrument)
Ordering: (1) each metric in one plain sentence ("Breadth = share of tracked industries whose output fell over the month"); (2) the four comparators named + peak dates (1981-82, 1990-92, 2008-09, 2020) + CD Howe dating source; (3) formulas in plain variable names, no symbols; (4) COVID off-scale note; (5) data vintage + seams ("NAICS-era recessions" — Phase A is NAICS-native, no SIC seam yet). Manrope 400 15px defs, Plex Mono inline values, micro-caps `METHODOLOGY`/`COMPARATORS`/`SOURCES` sub-eyebrows 0.22em. Reader-facing → passes the three gates.
### 7.6 Relation to site
- Same masthead/colophon/type/hairline vocab. Its own surface (not chartbook, not homepage panel). No FIGURE/PLATE eyebrows. Standing top-level `RECESSION WATCH` masthead-kicker, section-number numeral in MTA red. Cross-link from the published 2-quarter commentary ("Part 2 — the live tracker"); standard ink link, red on hover; no cross-link inside chart blurbs.

## 9. Build order
1. frontend scaffolds `recession-watch.astro`: kicker, verdict slot (reserved 2-line height), 2×2 grid wrapper with cross-hairline, methodology zone, colophon.
2. chart-builder builds GDP depth FIRST (has the scale problem; de-risks the rest) → art-director redline.
3. After redline: breadth + the two employment charts to the same pattern.
4. Methodology prose + verdict + chart titles → writer → three gates.
5. Full page → art-director redline.

## Open judgment calls (defaults accepted unless Jay vetoes)
1. COVID on depth — KEEP clipped+annotated (default). 2. Highlighted comparator — all four equal (default). 3. Section vs standing — STANDING page (editorial: /recession-watch/). 4. Employment-depth y-floor — tune to data. 5. Resting-state callout — suppressed (default).
