# Multi-category monochrome bars — visual-identity ruling + spec

Status: art-director ruling. Author: art-director. Date: 2026-06-02.
Scope: Plate 1 forecast panel (operating vs capital) and Plate 5 (issuance:
bills / notes / bonds). First multi-category bars in the publication.
Side-by-side render: texture version (current) vs the recommended version
below. Jay picks on review.

---

## 1. THE RULING

**Use a GREY-TINT INK-DENSITY RAMP, not texture. Categories separate by tint
level on a pure-ink base; weight + position carry hierarchy; the dashed
divider alone carries forecast.**

Drop the hatch and cross-hatch. They are the wrong language for this
publication for four reasons that all point the same way:

**1. The canon already blessed an ink-density ramp for category separation —
this is not a new invention.** Inflation Panel 3 (Breadth) was ratified
(`canon_reference_panel.md` Q1, 2026-05-11) with three bands distinguished by
ink density — `above-3% = 100% ink`, `target band = 35% ink`, `below-1% =
12% ink` — composed as opacity on `--ink`. The decision text is explicit: "ink
density reads as editorial weight" and "the eye correctly weights the largest
deviation heaviest." That is a categorical-separation-by-tint precedent
sitting live on a section page right now. A grey ramp on fiscal bars is the
*same move*, not a departure. Texture, by contrast, has no canon precedent
anywhere in the system.

**2. The "drop weight, not hue" rule is satisfied — a tint ramp is the literal
embodiment of it.** The canon's hardest line (`design-system.md` §3 neutrals;
`canon_reference_panel.md` multi-series adaptation) is "if a thing should be
quieter, drop its weight, never its hue." Main Claude's read is correct and
worth stating precisely: that rule governs HIERARCHY (quieting a secondary
thing) — and an ink-density ramp *is* weight-dropping rendered in fill. A grey
tint is monochrome by definition; it recruits zero hue. It is the most
canon-native way to say "these are the same kind of object, ranked." Texture
introduces a NEW visual dimension (pattern frequency) that exists nowhere else
in the system — no chart, no rule, no chrome uses hatching. It reads as
imported from a different design language (engineering blueprint / patent
drawing), which is exactly Jay's "too different from what we've done before"
instinct. He is right.

**3. Texture is busy and it muddies the data-ink ratio (Tufte, §1 lineage).**
Cross-hatch at chartbook scale fills a bar with ~40-50 hairline strokes. Every
one of those strokes is non-data ink. On a 6-7 bar stacked chart that is
hundreds of decorative strokes competing with the gridlines (themselves ink at
0.18) and the zero line. The Knoll-catalogue plate (§1) is defined by ink
spent only where it carries information. A flat 55%-ink rectangle carries the
"middle category" signal with a fraction of the ink and none of the moiré
shimmer that hatching produces when the SVG is scaled to a retina viewport.

**4. The monochrome-tint ramp IS the Economist / FT register for serious
mono bar charts — the reference lane we actually sit in.** When the Economist
or FT run a strictly monochrome stacked bar (no color budget that week), they
ramp tints of one ink, darkest-to-lightest, never hatch. Hatching is a 1980s
photocopier-era affordance for when you genuinely could not print grey. We can
print grey. Using texture is solving a problem we do not have.

**Verdict: pure grey-tint ramp for both charts. No hybrid-with-texture, no
hatch retained anywhere.** (The "hybrid" option — solid ink primary + one grey
secondary — is just the 2-category case of the ramp, so it is subsumed below,
not a separate language.)

One caveat worth naming so it does not get lost: a tint ramp must NEVER be
recruited to mean "forecast / less certain." That was the earlier
texture-vs-tint worry and it remains valid — a lighter bar must not read as
"smaller / provisional." Here the ramp encodes CATEGORY (operating vs capital;
bills vs notes vs bonds), and **the forecast signal stays exclusively the
dashed divider + FORECAST label, unchanged.** Every category keeps its same
tint across the actual/forecast boundary. This is the clean separation of
concerns: tint = which category, divider = which era.

---

## 2. THE EXACT SPEC (implementable)

### 2.1 The ink-density ramp values

All tints are pure `--ink` (`#000000`) with a composed `fill-opacity`. This
keeps the token surface monochrome (canon §3: compose opacity at the call
site, never reify a grey hex) and exactly mirrors the blessed Breadth-panel
mechanism. **Do not introduce a `--ink-grey` token; do not use
`--ink-placeholder` (#8A8A8A) — that token is reserved for placeholder copy
only and must not leak onto data marks.**

Ramp stops (the canonical fiscal-bar density ladder):

| Stop      | `fill-opacity` on `--ink` | Renders as (on white) | Role                          |
|-----------|---------------------------|-----------------------|-------------------------------|
| INK       | `1.00`                    | pure black            | Primary / lead category       |
| MID       | `0.55`                    | ~middle grey          | Secondary category            |
| FAINT     | `0.28`                    | light grey            | Tertiary category             |

`0.55` and `0.28` are chosen to (a) sit clearly distinct from each other and
from solid ink at chartbook scale, (b) stay distinct from the 0.18 gridline
opacity so a faint bar never reads as "gridline," and (c) echo the Breadth
ladder's spirit (it used 1.0 / 0.35 / 0.12; fiscal bars are larger filled
areas read against gridlines, so the two lower stops are nudged up to 0.55 /
0.28 to hold separation against the 0.18 grid). A bar segment must always read
as heavier than a gridline; 0.28 > 0.18 with margin.

**Hairline separator (mandatory for stacked bars).** Because adjacent stacked
segments now differ only by tint (not texture), give every segment a **1px
`--paper` (white) stroke** so the boundary between two grey segments stays
crisp and does not visually merge. `stroke: var(--paper); stroke-width: 1;`.
This is the standard mono-stacked-bar move (FT does exactly this) and costs
nothing. For the Plate 1 signed bars (operating/capital are vertically
stacked from zero) the same white hairline applies between the operating and
capital segments.

### 2.2 Order mapping: DARK → LIGHT, primary-first

**Category order maps dark→light, with the editorially-primary category at
INK (darkest).** Rationale: ink density reads as editorial weight (the
blessed Breadth rationale). The category the reader's eye should land on first
gets the most ink. Lighter = more contextual / supporting. This is the
publication's consistent grammar (heaviest ink = the thing that matters most),
now applied to fill instead of stroke-weight.

**2-category case — Plate 1 (operating vs capital):**

| Category   | Stop | `fill-opacity` | Why                                                        |
|------------|------|----------------|------------------------------------------------------------|
| Operating  | INK  | `1.00`         | The editorial protagonist — operating balance is the structural story (swings to surplus by FY2028-29). Solid black. |
| Capital    | MID  | `0.55`         | The drag / context segment. Mid-grey. |

(The 2-category case uses INK + MID only; FAINT is unused. This is exactly the
"solid ink primary + one grey secondary" hybrid main Claude floated — it is
the 2-category ramp, so it is the same rule, not an exception.)

**3-category case — Plate 5 (bills / notes / bonds), stacked bottom→top:**

The stack order is fixed by the data (bills bottom, notes middle, bonds top).
The tint assignment is by **editorial weight, not stack position** — and bonds
is the lead instrument (the long-end issuance is the story for a macro
reader), so:

| Segment | Stack position | Stop  | `fill-opacity` |
|---------|----------------|-------|----------------|
| Bonds   | top            | INK   | `1.00`         |
| Bills   | bottom         | MID   | `0.55`         |
| Notes   | middle         | FAINT | `0.28`         |

Wait — that puts FAINT (lightest) physically between INK and MID, which reads
awkwardly (lightest sandwiched). **Override for stacked bars: when categories
stack, the tint must also descend monotonically with stack position so the
stack reads as a clean dark→light (or light→dark) gradient top-to-bottom.** A
non-monotonic tint stack (dark / light / mid) looks like a rendering bug.

**Final Plate 5 assignment — monotonic, darkest at top:**

| Segment | Stack position | Stop  | `fill-opacity` | Render        |
|---------|----------------|-------|----------------|---------------|
| Bonds   | top            | INK   | `1.00`         | pure black    |
| Notes   | middle         | MID   | `0.55`         | mid grey      |
| Bills   | bottom         | FAINT | `0.28`         | light grey    |

This satisfies both grammars at once: bonds (the lead instrument) is darkest,
AND the stack ramps cleanly dark→light from top to bottom. Bills being the
largest bucket by volume but lightest in tint is correct — volume is encoded
by segment HEIGHT (the data), tint encodes editorial lead, and the two are
allowed to differ (height carries magnitude, tint carries "look here first").

**Rule of thumb for any future stacked multi-category bar: tint descends
monotonically with stack height (darkest on top), and the editorially-lead
category should be arranged to sit at the dark end.** For non-stacked grouped
bars (side-by-side, like Plate 1's operating/capital if ever rendered as a
group rather than a signed stack), monotonicity is not required — assign INK
to primary, MID to secondary purely by editorial weight.

### 2.3 What stays exactly as-is

- **Forecast signal:** dashed divider (`stroke-dasharray: 4 2`,
  `stroke-opacity: 0.40`, 1px ink) + uppercase FORECAST label (Manrope 600,
  11px, 0.18em). UNCHANGED. Tint never signals forecast.
- **Gridlines** 0.18 ink, **zero line** 1.5px full ink, **frame** 1px ink,
  **ticks** Plex Mono 12px / Manrope 12px, **right-gutter segment labels**
  (Manrope 13px, weight 600 for lead / 400 for others) — all unchanged.
- **No red dot** (canon R2: bars never carry the latest-point dot). Plate 5's
  Plex Mono `$526B` numeric callout above the last actual bar stays.
- **Right-gutter category labels keep weight-contrast hierarchy** (lead
  category 600, others 400). The label weight and the bar tint now reinforce
  each other: the darkest bar is named in the heaviest label. Good.

### 2.4 Implementation deltas (for the chart-builder, alt version only)

Plate 5 (`Plate5IssuanceByInstrument.astro`) — replace the `<defs>` patterns
and the three bar fills:
- Delete the `<pattern id="p5-hatch-bills">` and `<pattern id="p5-cross-notes">`.
- `.p5iss-chart__bar-bonds` → `fill: var(--ink); fill-opacity: 1; stroke: var(--paper); stroke-width: 1;`
- `.p5iss-chart__bar-notes` → `fill: var(--ink); fill-opacity: 0.55; stroke: var(--paper); stroke-width: 1;`
- `.p5iss-chart__bar-bills` → `fill: var(--ink); fill-opacity: 0.28; stroke: var(--paper); stroke-width: 1;`
- Update the aria-label texture words ("hatch / cross-hatch / solid") to tint
  words ("light grey / mid grey / black") — this is a11y description, not
  reader prose.

Plate 1 two-panel (`Plate1BalanceTwoPanel.astro`) — Panel B composition:
- Delete `<pattern id="p1tp-capex-hatch">`.
- `.p1tp-chart__bar-solid` (operating + Panel-A totals) → `fill: var(--ink); fill-opacity: 1;` (Panel A totals stay solid ink; they are single-category).
- `.p1tp-chart__bar-capex` → rename concept to `--bar-mid`: `fill: var(--ink); fill-opacity: 0.55; stroke: var(--paper); stroke-width: 1;`
- Add the white hairline between the operating and capital segments in Panel B
  (the `stroke: var(--paper)` on each segment rect handles this).
- Update aria-label "cross-hatch" → "mid grey."

---

## 3. CANON STATUS — SPEC NOW, RATIFY AFTER JAY PICKS

**Hold the formal canon write-in until Jay picks on the side-by-side.** Do NOT
edit `canon_reference_panel.md` yet. Reason: this is the publication's first
multi-category bar and the user's standing pattern is show-then-ratify ("bad
versions get tagged and left in place; improved versions live alongside; user
picks on review"). Texture is being rendered alongside specifically so Jay can
see the two. Writing canon before he has looked would pre-empt his call.

**The moment Jay picks the grey ramp, this becomes canon** as a new rule in
`canon_reference_panel.md`, drafted as:

> **Multi-category monochrome bars.** Categories in a stacked or grouped bar
> separate by ink-density tint on `--ink`, never by texture/hatching, never by
> hue. Ramp stops: INK `fill-opacity 1.0` (lead), MID `0.55` (secondary),
> FAINT `0.28` (tertiary). Stacked segments ramp monotonically with stack
> height (darkest on top); the editorially-lead category sits at the dark end.
> Stacked segments carry a 1px `--paper` hairline separator. Tint encodes
> category, never forecast — the dashed divider remains the sole forecast
> signal. Reserve `--ink-placeholder` for placeholder copy; never use it on
> data. Precedent: Inflation Panel 3 Breadth (Q1).

That draft is ready to paste on the green light.

---

## 4. THE TWO LITTLE PROBLEMS ON Plate1BalanceTwoPanel

### (a) Panel B carries a FORECAST label + dashed divider, but the panel is
essentially all-forecast — redundant and confusing.

Confirmed from the code: Panel B's zoom window is
`["2024-25", "2025-26", ... "2030-31"]` — that is ONE actual bar (FY2024-25,
total only, no opex/capex split) followed by six forecast bars. The divider
sits after the first bar and the FORECAST label sits at the top. So the label
is telling the reader "almost everything you see is forecast," which is not the
useful framing — and the lone actual bar is a different object (a total, not an
operating/capital split) sitting next to six split bars, which reads as
inconsistent.

**Fix — drop the lone actual bar AND drop the divider + FORECAST label from
Panel B.** Make Panel B a clean, all-forecast composition panel:

- Change `ZOOM_FYS` to start at FY2025-26: `["2025-26", "2026-27", "2027-28",
  "2028-29", "2029-30", "2030-31"]` (six forecast bars, every one an
  operating/capital split — visually consistent).
- Remove the Panel-B divider (`bDividerX`) and the Panel-B FORECAST label
  entirely. With no actual bar in the panel there is no boundary to mark.
- Signal "this whole panel is the projection" in the **panel title** instead
  (the title slot is already a TK placeholder; writer will fill it — e.g. a
  title that names the forecast window). The era-signal moves from an in-plot
  label to the panel title, which is where a small-multiple's scope belongs.
- The FY2024-25 actual total is NOT lost to the reader — it lives in Panel A
  (the full history panel), which is exactly where the last actual belongs.
  Panel B's job is the forward composition; Panel A's job is the long actual
  record. Clean division of labour.

Net: Panel A = the history (actuals + a forecast tail with ITS divider +
FORECAST label, which is correct there because A genuinely spans the
boundary). Panel B = pure forecast composition, no divider, no label, scope
named in the title. The redundancy is gone.

### (b) Panel proportions / titles.

- **Proportions read well — keep the 62/38 width split.** Panel A (the long
  FY1983-84→FY2030-31 history, ~48 bars including the COVID -$327B spike) needs
  the width; Panel B (now 6 forecast bars) reads fine in the narrower 38%. The
  `PANEL_GUTTER = 64` is enough to seat Panel B's left y-ticks without
  colliding with Panel A's frame. No change.
- **One real fix on titles: the per-panel title slots sit at `PLOT_Y0 - 22`
  (y=22) while the FORECAST label sits at `PLOT_Y0 - 6` (y=38) and the
  Panel-A divider's label is in the same band.** With Panel A keeping its
  FORECAST label, confirm the Panel-A title and the Panel-A FORECAST label do
  not collide horizontally — the title is left-anchored at `A_X0` and the
  FORECAST label is anchored at `aDividerX + 6` (mid-panel), so they clear
  horizontally. Fine. But once Panel B loses its FORECAST label, Panel B's
  title has the whole top band to itself — good.
- **Title typography:** the slots are Manrope 600 12px (`--panel-title`),
  rendered as `[PANEL A TITLE TK]` / `[PANEL B TITLE TK]` in
  `--ink-placeholder` until writer fills them. That matches the small-multiples
  canon (§5.3: "each panel's title in `label` size, pure ink, 600 weight, sits
  above"). 12px vs the canon's 13px `label` — bump to 13px to match the
  canon-reference small-multiples title size. Minor; do it while in the file.
- **Both panel titles must be real before ship** (writer, through the three
  gates). The TK placeholders are fine for the comparison render; they cannot
  ship live (no-TK rule).

---

## 5. SUMMARY FOR THE RENDER

Build the alt version of both plates with:
- Plate 5: bonds INK 1.0 / notes MID 0.55 / bills FAINT 0.28, 1px white
  hairline between segments, patterns deleted.
- Plate 1 Panel B: operating INK 1.0 / capital MID 0.55, 1px white hairline,
  pattern deleted; ZOOM_FYS starts FY2025-26; Panel-B divider + FORECAST label
  removed; titles bumped to 13px.
- Forecast signal unchanged everywhere (dashed divider + FORECAST label in
  Panel A and Plate 5).

Render alongside the current texture version. Jay picks. On green light, paste
the §3 rule into `canon_reference_panel.md`.
