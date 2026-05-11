# Sleeping Giant mark - canon

Status: blessed. Author: art-director. Last updated: 2026-05-11.

The Sleeping Giant mark is Sibley Creek's canonical brand identity
element. This document codifies the asset, the variants, where it
appears, at what size, with what stroke weight, with or without the
red accent dot.

The mark is the off-site brand signal: every OG social card preview,
every browser-tab favicon, every masthead instance carries the place
the publication is named after. The Sibley Peninsula's Sleeping Giant
is not a decorative flourish; it is the publication's geographic
identity, threaded into the visual system.

---

## 1. The asset

`src/components/brand/SleepingGiantMark.astro` is the canonical
component. A single Astro component, inline SVG, zero client JS.

The silhouette is **one continuous SVG path** (one `M`, then cubic
beziers only - no lifts). The path runs left-to-right as: head (left)
to chest plateau to knees to foot (rightmost terminus). At the foot
terminus, one MTA red filled circle sits as the brand-signal dot.

The component takes three props:

- `size` (number, default `120`) - pixel width. Height is `size / 4`
  from the 4:1 viewBox aspect.
- `variant` (`"inline" | "og"`, default `"inline"`) - drives stroke
  width (1.5px inline, 2px og) and dot radius (3px inline, 4px og).
- `withAccent` (boolean, default `true`) - toggle the red dot. Set
  false only for pure-ink exports.

The viewBox is `0 0 320 80` (4:1 wide landscape). The silhouette
echoes the actual landform: a reclining figure read horizontally,
much wider than tall.

A separate favicon component lives at
`src/components/brand/SleepingGiantFavicon.astro`. The favicon is
NOT a scaled-down version of the canonical mark - it is a cropped
treatment showing only the head and Adam's Apple, at 32 x 32 viewBox
with a heavier stroke. See Section 6 below.

---

## 2. Orientation

Head on the LEFT. Foot on the RIGHT. The red accent dot sits at the
rightmost terminus, on the foot.

This is a DELIBERATE FLIP from the canonical Thunder Bay vantage. The
reason is brand-system consistency, not cartography: every visual
element on Sibley Creek's site has a single red moment at the right
end of the line (the chart latest-print dot, the colophon rule with
the red preceding the publication mark, etc.). The Sleeping Giant
mark obeys the same discipline. Recognition of the reclining figure
does not depend on the cartographic orientation; the brand-system
consistency does. Vignelli would do the same.

The reader reads left to right (Western reading order). The eye
enters the mark at the head's cliff, traces along the chest plateau,
descends past the knees and shin, and lands on the red dot at the
foot. The red dot is the eye's exit point - the brand-signal kicker.

---

## 3. The silhouette anatomy

The path is a simplified Vignelli read of the landform, not a topo
map. Six anatomical waypoints, head to foot:

| # | Waypoint | Approx (x, y) | What the reader sees |
|---|----------|---------------|----------------------|
| 1 | Lake baseline (north) | (4, 72)   | The line emerges from the water on the left |
| 2 | Head peak / cliff apex | (32, 10)  | The apex of the mark - sharp rise to the highest point |
| 3 | Throat dip (Adam's Apple notch bottom) | (78, 38) | A clear dip; the silhouette's most recognizable single feature |
| 4 | Adam's Apple bump | (96, 30)  | A small bump above the notch |
| 5 | Chest plateau | (122-170, 18) | Long sustained near-apex; the broad chest |
| 6 | Knee rise | (228, 22)  | A second peak, smaller than the chest |
| 7 | Foot mesa terminus | (304, 46)  | Rightmost point - dot sits here |

The line terminates at the foot (step 7) rather than continuing down
to the lake on the right. This is intentional: terminating at the
foot lets the red dot read as a terminal brand stamp (same logic as
a chart's line terminating at its latest-print dot). The figure is a
silhouette, not a closed shape; the eye does not expect it to land
on the water on the right.

On the LEFT, the line DOES anchor to the lake baseline at (4, 72)
because the head's cliff face genuinely rises out of the water on the
north side. Asymmetric, but defensible: the left side is where the
eye enters and needs grounding; the right side is where the eye exits
on the brand-signal dot.

---

## 4. Variants

Two variants ship from one component. Both consume the same path
data; they differ only in stroke width and dot radius.

| Variant | Stroke | Dot radius | Default size | Use case |
|---------|--------|------------|--------------|----------|
| `inline` | 1.5px | 3px | 120px wide | Masthead-inline; small brand stamps |
| `og`     | 2px   | 4px | 480-600px wide | OG social card; 404 hero; large-surface marks |

Stroke width is set as a CSS custom property (`--mark-stroke`) on
the SVG element, so consuming surfaces can override per-instance if
a genuine exception arises. The default values cover all current
surfaces.

`vector-effect: non-scaling-stroke` on the path keeps the line at
its specified weight regardless of CSS-driven scale, matching the
canon-reference chart line.

---

## 5. Placement canon

Where the mark appears on the site, at what size, with what variant,
with the red dot on or off.

### 5.1 Site masthead (`VignelliMasthead.astro`)

- **Variant.** `inline`.
- **Size.** 120px wide (30px tall from the 4:1 aspect).
- **Stroke.** 1.5px (inline default).
- **Dot.** ON. The red dot at the rightmost terminus is the single
  brand-signal moment in the masthead. The wordmark itself stays in
  pure ink Manrope Black.
- **Position.** Inline immediately to the LEFT of the `SIBLEY CREEK`
  wordmark, on the same baseline. The dot at the right end of the mark
  sits roughly 6-10px to the left of the first letter `S` of the
  wordmark. Reader scans: `[head][chest][foot+dot] SIBLEY CREEK`.
- **Negative space.** 12px minimum of clear paper between the mark
  and any neighbour (the wordmark on the right; the page edge / hero
  rule on the left).
- **Weight discipline.** The mark's 1.5px stroke is LIGHTER than the
  wordmark's Manrope Black letter strokes. The mark supports the
  wordmark; the wordmark is the typographic moment. If the mark's
  stroke ever competes with the wordmark for the reader's eye, drop
  the mark's stroke to 1.25px.
- **One brand-signal moment.** Because the mark ships a red dot in
  the masthead, the masthead's rail (currently disabled, prop preserved)
  must NOT introduce a second red moment when it returns. The mark's
  dot is the masthead's red.

### 5.2 OG social card

- **Variant.** `og`.
- **Size.** 480-600px wide (120-150px tall).
- **Stroke.** 2px.
- **Dot.** ON.
- **Position.** Top of the card or aligned to the wordmark per the
  OG card template. Specific placement to be locked when the OG
  template ships (deferred; not in this dispatch).

### 5.3 404 hero / brand pages

- **Variant.** `og`.
- **Size.** 480-600px wide.
- **Stroke.** 2px.
- **Dot.** ON.
- **Position.** Centered horizontally on the 404 page, sitting above
  the `Page not found` headline. The 404 is the rare page where the
  mark stands alone (no wordmark adjacent), and the og variant's
  heavier stroke and larger dot read at the hero scale the page calls
  for.

### 5.4 Favicon

- **Component.** `src/components/brand/SleepingGiantFavicon.astro`
  (NOT the canonical mark - see Section 6).
- **Size.** 32 x 32. Browser rasterizes to 16 x 16 for the tab; the
  SVG carries enough stroke weight to survive the downsample.
- **Dot.** ON. The red dot at the Adam's Apple bump is the only
  red moment in the favicon - it threads the publication's accent
  through the browser tab.
- **Position.** Used as `/favicon.svg` (and fallback `/favicon.ico`
  rasterized from the same source) via the standard HTML link
  element in `BaseLayout`. Frontend-designer owns the wiring; not
  in this dispatch's scope.

### 5.5 Print stationery / monochrome exports

- **Variant.** `og` or `inline` per surface.
- **Dot.** OFF (`withAccent={false}`). Print and monochrome exports
  use the pure-ink silhouette without the brand-signal red, because
  the red typically renders unevenly in monochrome reproduction and
  the dot's brand-signal moment depends on chromatic contrast against
  the pure-ink line. Pure ink with no red is a deliberate "this is
  the monochrome treatment" variant.

---

## 6. Favicon recommendation - the call

**Recommendation: ship the cropped-head favicon (option A below). Do
not ship the full silhouette at favicon scale; do not ship a
wordmark-letter S; do not ship a bare red dot.**

### Option A (chosen): cropped head + Adam's Apple

`src/components/brand/SleepingGiantFavicon.astro`. 32 x 32 viewBox.
A single continuous path showing only the head's cliff face, the
peak, the face descent, the throat notch, and the Adam's Apple bump.
The red dot sits at the rightmost terminus on the bump.

**Why this wins.**

1. **The head IS the iconic moment.** Any Thunder Bay resident reads
   the Sleeping Giant by the cliff face plus the Adam's Apple notch
   first. The chest plateau is sustained but visually quieter; the
   foot is the brand-signal moment but anatomically generic. The
   head is the recognition handle.
2. **It survives the raster.** A 32 x 32 cropped silhouette at 2.25px
   stroke rasterizes to a legible mark at the 16px browser-tab size.
   The full 4:1 silhouette at 32px wide would compress to 32 x 8 and
   read as a smudge.
3. **It preserves the brand-pattern.** The cropped favicon still
   terminates with a red dot at the rightmost point (the Adam's Apple
   bump, not the foot). The pattern `[line][rightmost red dot]` is
   intact.
4. **Geographic identity preserved.** The favicon still says "Sleeping
   Giant" because the cliff + notch is the silhouette's strongest
   visual signature. A wordmark `S` would erase the place; a bare red
   dot would erase the figure.

### Option B (rejected): wordmark letter `S`

A Manrope Black `S` in pure ink. Cheap to produce. Reads as "Sibley"
or "Sibley Creek." But it loses the geographic anchor entirely - the
publication is named after a place, and the brand mark is the place.
A letter mark is a different brand register (logo-as-letter, like the
NYT `T` or the New Yorker monocle). Rejecting because the Sleeping
Giant is non-negotiable as the brand's geographic identity.

### Option C (rejected): bare red dot

A single MTA red filled circle on pure paper. Maximally minimal. But
this is the chart's latest-print-dot signal, not a publication mark.
A red dot in a browser tab would read as a notification badge, not
as a brand. Rejecting for register confusion.

---

## 7. The actual SVG path data (for review)

### 7.1 Canonical mark (`SleepingGiantMark.astro`)

ViewBox `0 0 320 80`. One M, twelve cubic-bezier segments, no lifts.
The full path string:

```
M 4 72
C 10 56, 14 32, 22 18
C 26 12, 30 8, 34 10
C 40 12, 48 18, 56 24
C 64 30, 72 36, 78 38
C 84 38, 90 34, 96 30
C 104 26, 112 22, 122 20
C 138 17, 154 17, 170 18
C 184 20, 194 24, 202 28
C 210 30, 218 28, 228 22
C 236 19, 244 22, 252 28
C 262 33, 272 38, 282 42
C 292 45, 300 46, 304 46
```

Red dot: `<circle cx="304" cy="46" r="3" />` (inline variant) or
`r="4"` (og variant). Filled in `var(--accent)`, no stroke.

### 7.2 Favicon (`SleepingGiantFavicon.astro`)

ViewBox `0 0 32 32`. One M, four cubic-bezier segments, no lifts.

```
M 2 28
C 4 22, 6 14, 8 8
C 9 5, 11 5, 12 7
C 14 10, 16 14, 18 18
C 20 19, 22 17, 26 14
```

Red dot: `<circle cx="26" cy="14" r="2.5" />`. Filled in `var(--accent)`,
no stroke.

---

## 8. Negative-space rules

The mark sits on pure paper. The component itself ships no background,
no fill, no border - portability is by design. Negative space lives in
the consuming surface.

- **Minimum clear-space around the mark.** A clear band of paper at
  least 0.5 viewBox-heights deep (40 viewBox-units, ~10% of the mark's
  width) on every side. At 120px wide that's a ~15px clear band - no
  type, no rule, no chrome may intrude.
- **No box, no frame, no badge.** The mark NEVER renders inside a
  rounded-rect, a circle, a card, or any other enclosing shape. Pure
  silhouette on pure paper.
- **No drop shadow, no inner glow, no outline.** The Vignelli register
  forbids any non-typographic chrome. The line is the line; the dot is
  the dot.
- **No tint.** The line is pure ink (`#000000`) at all sizes. The dot
  is pure MTA red (`#E63946`) at all sizes. Neither color is softened,
  warmed, or tinted under any circumstances.

---

## 9. Misuse - what NOT to do

Each entry below is a real failure mode this canon prevents.

- **Do not flip the mark vertically.** The Giant reclines on its back;
  flipped vertically he reclines on his stomach, which is a different
  landform and not Sibley Peninsula.
- **Do not flip the mark horizontally.** Head LEFT, foot RIGHT. A
  flipped mark puts the dot on the head, breaking the rightmost-red
  pattern that threads through every visual element on the site.
- **Do not rotate the mark.** The Giant reclines horizontally; a
  rotated Giant is upright, which is the Tower (a Tarot card), not the
  Sleeping Giant.
- **Do not fill the silhouette.** No black-fill, no gradient, no tint
  inside the line. Pure silhouette = one line. Filling the figure
  turns the mark into an icon-with-mass, which is a different visual
  register.
- **Do not duplicate the red dot.** One red dot per mark. Adding a
  second dot (e.g. at the head, "for symmetry") doubles the brand-
  signal moment and breaks the chart-canon mirror.
- **Do not separate the dot from the line.** The dot sits at the line's
  rightmost terminus. Floating it elsewhere on the canvas (above the
  chest, below the foot, etc.) breaks the terminal-stamp logic.
- **Do not redraw the silhouette per surface.** One path, two variants
  (inline / og). All surfaces consume the same component. If a surface
  needs different proportions, bring it to art-director.
- **Do not place the mark on a colored ground.** The mark only renders
  on pure paper (`#FFFFFF`). Any colored background (even a near-white
  cream) breaks the Vignelli register the mark depends on.

---

## 10. Relationship to the chart canon

The mark is the canon-reference chart's visual logic applied to a
brand asset, not a chart. Specifically:

- **The continuous pure-ink line** is the canon-reference chart's
  1.5px (or 2px) `var(--ink)` data line. Same color, same family of
  stroke weights. The reader reads one as a place, the other as a
  measurement; both are the same kind of single black line on white
  paper.
- **The MTA red dot at the rightmost terminus** is the canon-reference
  chart's `var(--accent)` latest-print dot. Same color, same range of
  radii (3-4px). The reader's eye lands on the same brand stamp at the
  right end of every visual element on the site.
- **The reclining figure orientation (head left, foot right)** is the
  chart's time-series orientation (past left, present right). Both
  signal "the eye exits with the red dot."
- **The pure paper ground** is the chart's `var(--paper)` canvas.
  Both objects sit on the same paper, with no card pillow, no
  background tint, no border.

The mark and the chart are not the same object, but they share the
same visual grammar. A reader who has internalized the chart canon
reads the mark fluently on first encounter, and vice versa. This is
the cohesion rule (design-system.md Section 10) extended to the brand
layer.

---

## 11. Open questions / deferred decisions

- **OG social card template.** The mark's placement, scale, and
  framing inside the OG card are deferred until the OG card template
  itself ships. When that template is authored, the mark consumes
  variant `og` at 480-600px wide.
- **Print and stationery.** Not currently in scope. If/when a print
  letterhead is authored, `withAccent={false}` is the default for
  monochrome reproduction; consider a separate "print variant" only
  if reproduction quality of the red dot proves unreliable.
- **PWA manifest icons.** The favicon component's silhouette also
  serves as the source for any PWA manifest icons at 192 / 512. The
  manifest wiring is frontend-designer's call when PWA becomes a
  decision; not in scope here.
