# Sparkline (Tier-1) canon — y-axis discipline + chrome restraint

Status: blessed 2026-05-11. Authority: art-director + chart-builder, ratified by user (ex-Bloomberg editor) across three iteration rounds.

This doc supplements `design/design-system.md` and `design/canon_reference_panel.md`. The reference-panel doc is **Tier-3 chartbook canon**; it explicitly carves out Tier-1 sparklines as "decorative." That carve-out is now SUPERSEDED. Splash-panel sparklines are not decorative; they are small, disciplined, fully-typeset charts. Their canon lives here.

The implementation reference is `src/components/home/SectionPanel.astro` — the splash mini-chart wrapper. Copy its y-axis behavior for any new sparkline surface.

---

## Why this canon exists

Across one production session the user flagged three distinct sparkline-axis failure modes in sequence:

1. *"trade sparkline y-axis bad units"* — the axis emitted bare numbers like `2300` without indicating whether the unit was millions or billions of CAD; for a -$2.3B trade balance the reader's eye had to guess.
2. *"keep in mind that all the numbers on the y-axis must be in the same units/magnitude"* — earlier code had mixed `M` and `B` suffixes within the same axis depending on each tick's magnitude. Mixed-magnitude axes are unreadable.
3. *"the sparkline y-axes seem kinda fuckin random? like the numbers on the ticks"* — ticks were data-derived (e.g., `2.34%, 1.78%, 1.22%`) rather than rounded to nice round numbers.
4. *"number of decimals on y-axis is also excessive"* — decimals were derived from value magnitude (a 2.5% value rendered "2.50") rather than from the step size.

Each fix landed in `SectionPanel.astro` and each is captured below as a permanent rule. Chart-builder authoring any future sparkline must satisfy ALL of them.

---

## Rules

### S1. Uniform scale across the entire axis

ONE scale factor + suffix applies to every tick on the axis. NEVER mix `M` and `B`, NEVER mix decimal counts, NEVER let some ticks have `%` and others bare numbers.

Implementation: a single `computeAxisScale(yMin, yMax, step, units)` call returns `{factor, suffix, decimals}` that every tick uses. The function reads the units from the pipeline's `units` field and decides ONCE whether the whole axis is in `M`, `B`, `%`, or bare; the suffix is appended ONLY to the topmost tick.

### S2. Nice ticks — rounded steps only

Tick step is rounded to `(1 | 2 | 2.5 | 5) × 10^n` so ticks land on visually round numbers (`2%, 4%, 6%`, not `1.78%, 3.56%, 5.34%`).

Implementation reference: `niceStep(range, targetTicks)` in `SectionPanel.astro`. The algorithm:
1. Roughly divide the data range by (targetTicks - 1) to get the rough step.
2. Find the order-of-magnitude (`10^floor(log10(rough))`).
3. Normalize and round to the nearest of {1, 2, 2.5, 5, 10}.
4. Multiply back by magnitude.

Then `niceTicks(min, max, target=3)` walks from `floor(min/step)*step` to `ceil(max/step)*step` in step increments, capped at 6 ticks to avoid clutter.

### S3. Step-derived decimal precision

Decimals on every tick come from the SCALED STEP, not from the value magnitude.

```
step >= 1      → 0 decimals  ("3")
step >= 0.1    → 1 decimal   ("2.0")
step >= 0.01   → 2 decimals  ("1.40")
step >= 0.001  → 3 decimals  ("0.005")
```

The dumb failure mode this prevents: a 2.5% tick rendered as `"2.50"` because the value happened to be < 10. The step is 0.5; one decimal is correct.

### S4. Auto-scale magnitude when any tick crosses 1000

When the pipeline emits `units: "CAD millions"` and ANY tick on the axis crosses 1000M, the entire axis converts to billions (factor = 1/1000, suffix = `B`) uniformly. Decimals re-derive from the scaled step.

A trade balance series whose ticks would be `-3000M, -1500M, 0M, 1500M, 3000M` becomes `-$3B, -$1.5B, $0, $1.5B, $3B`. Topmost tick carries the `B` suffix.

Below 1000M, the axis stays in millions but decimals revert to 0 (no point in showing "127.5M" — sparkline scale won't make the half-million read).

### S5. Topmost tick carries the unit suffix

Only the topmost tick renders with the suffix (`%`, `B`, `M`). Other ticks render bare. This is the same rule as Tier-3 (canon-compliance checklist rule 5) and it applies identically here.

### S6. FX precision floor

When the unit is `CAD per USD` (i.e., USDCAD), the decimal count is forced to `max(2, decimalsForStep(step))`. A FX series's editorial signal is in the second and third decimal; even a step-derived 1-decimal would lose the read. Same rule applies to any future currency-cross axis.

### S7. No vertical gridlines on sparklines

Sparklines never render vertical gridlines (Tier-3 rule 4 also). Horizontal gridlines at 0.18 ink opacity are permitted but not required at sparkline scale; most sparkline implementations omit them entirely. The latest-print red dot + the line + the topmost tick label is enough chrome.

### S8. Direction tint exception — table triangles ONLY

The canon's "no color for direction" rule (`design/design-system.md` Section 3) has ONE surgical exception: the tiny ▲▼ triangle glyphs in sparkline-adjacent data tables (the splash panel's print rows). At 9-10px these glyphs cannot be parsed by shape alone in peripheral vision; a muted color tint is permitted.

Tokens:
```
--dir-up:   #1B8F4E   (muted forest green; NOT a vibrant signal green)
--dir-down: #C5443E   (muted red; distinct from --accent's #E63946)
```

Rules:
- Applies to text glyphs ▲ ▼ at ≤12px font-size ONLY.
- NEVER applies to chart lines, marks, dots, bars, or any data ink in the chart itself.
- NEVER substitutes for the canon's MTA red latest-print dot.
- The `--dir-down` token is deliberately a different red from `--accent` so the brand-signal red stays unique to the latest-print dot moment.

This is the canon's only color-for-direction allowance. Defending it: at 10px font-size, a black ▲ next to a black ▼ across a six-row table is harder to scan than the eye realizes; the muted tint solves a real readability bug without introducing brand-red elsewhere.

---

## Implementation pattern (the as-built reference)

`src/components/home/SectionPanel.astro` is the canonical implementation. Any new sparkline surface should copy its:

- `niceStep` / `decimalsForStep` / `computeAxisScale` / `fmtTickAt` helpers (lines 87-148 ish).
- The `topmost-tick-carries-suffix` rendering pattern.
- The MTA red latest-print dot at the line's terminal x.
- The direction-tint classes for the triangle glyphs in the adjacent data table.

If a new surface needs sparkline behavior different from the splash, bring a per-surface visual spec to art-director rather than introducing a divergent axis algorithm.

---

## Splash composition restraint — companion rule

Sparklines live inside a panel; the panel itself has its own restraint canon, evolved across the same session.

Cut from the splash panel during the canon's blessing:

1. **Per-tile question deck** ("Is the 2% target being met...?"). Headline questions belong on section pages, not the splash. The splash answers, not asks.
2. **Cadence stamps** ("As of Apr 14, 2026 · Monthly"). The asOf date alone carries the cadence; explicit "Monthly" is redundant chrome.
3. **Chart figcaptions** ("Real GDP, m/m, last 36 months"). The chart's direct label + topmost tick carry the read. A separate caption duplicates.
4. **"Latest 3" count strings** ("LATEST 3" on the Research card). Counts are not editorial information; the rows speak for themselves.
5. **Lorem ipsum or placeholder lede paragraphs**. Visible placeholder copy ships ONLY when it's a deliberate "[ NOT WIRED ]" marker for a data slot; never as fake prose.
6. **Per-tile period stamps** (m/m, q/q, d/d). The delta's comparison window is implied by the chart's cadence; explicit period labels next to every delta clutter.

The pattern: at every iteration the user cut chrome. The Vignelli register's discipline is that every element on the page earns its place. When in doubt, cut.

Chart-builder + frontend-designer authoring new splash surfaces should default to MINIMUM CHROME and add elements only when a specific editorial argument requires them. Adding chrome "for completeness" or "for institutional gravitas" is wrong; the gravitas comes from restraint, not addition.

---

## Indicator naming convention (cross-reference)

The user's iterative renames during the same session ("merch trade balance" → "goods trade balance", "3M MA" → "3mma", "FY YTD" → "FYTD" → simplified to bare "Feb 2026" when FYTD context was unambiguous, "US partner share" → "US export share") establish a naming principle that also belongs in `editorial/writing-style.md`:

**Prefer the term the most relevant reader (Bay Street allocator, BoC reaction-function analyst) uses in conversation, not the source-publisher's full bureaucratic name.**

- StatCan calls it "International merchandise trade." The market calls it "goods trade balance." Use the market's name.
- StatCan emits "three-month moving average" in publications. Sell-side notes write "3mma." Use the sell-side abbreviation.
- The federal accounts publish "Fiscal Year to date" with prepended FY context. When the page surrounding the print already establishes the FYTD context, redundant repetition is chrome; drop to just the period stamp.

Editorial-director and writer should escalate to user when a tradeoff between (formal source name) and (market shorthand) is genuinely ambiguous. Default: market shorthand wins.
