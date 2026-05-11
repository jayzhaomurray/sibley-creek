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
beziers only - no lifts). The path runs left-to-right as: head MESA
(left, flat-topped) -> throat notch (deepest) -> chin MESA (small flat
plateau) -> Adam's apple notch (shallower) -> body MESA (long flat
plateau, ~head height) -> knees -> foot (rightmost terminus). At the
foot terminus, one MTA red filled circle sits as the brand-signal dot.

The Sleeping Giant is geologically a "formation of mesas and sills"
(Wikipedia) - flat-topped diabase plateaus separated by erosion
notches. v1 and v2 of this mark wrongly treated the silhouette as a
single dominant peak with a long undulating cascade; that failed
recognition. The corrected v3 reads as THREE distinct flat-topped
mesas with TWO notches between them. Flat tops, not pointed peaks.

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
treatment showing the head mesa, the throat notch, and the start of
the chin, at 32 x 32 viewBox with a heavier stroke. See Section 6
below.

---

## 2. Orientation

Head on the LEFT. Foot on the RIGHT. The red accent dot sits at the
rightmost terminus, on the foot.

This is a DELIBERATE FLIP from the canonical Thunder Bay vantage. In
real photographs from Thunder Bay the head is on the RIGHT (Thunder
Bay sits west of the Sibley Peninsula, looking east; north is to the
viewer's left). We flip horizontally so the brand-signal red dot lands
at the rightmost terminus, matching the chart latest-print dot
convention threaded across every visual element on the site.
Recognition of the reclining figure does not depend on cartographic
orientation; the brand-system consistency does. Vignelli would do the
same.

The reader reads left to right (Western reading order). The eye
enters the mark at the head's outboard cliff, climbs onto the head
mesa, drops into the throat notch, climbs the chin, drops into the
Adam's apple notch, climbs onto the long body mesa, descends through
the knees and shin, and lands on the red dot at the foot. The red
dot is the eye's exit point - the brand-signal kicker.

---

## 3. The silhouette anatomy

The path is a simplified Vignelli read of the landform, not a topo
map. The Giant is a multi-mesa formation: THREE distinct flat-topped
plateaus (head, chin, body) separated by TWO erosion notches (throat,
Adam's apple). The recognition handle is the multi-mesa structure
PLUS the deep throat notch PLUS the body's long flat plateau roughly
matching the head's height.

| # | Waypoint | Approx (x, y) | Height above lake (units) | What the reader sees |
|---|----------|---------------|---------------------------|----------------------|
| 1 | Lake baseline (left) | (4, 72) | 0 | The line emerges from the water on the left, behind the head's outboard cliff |
| 2 | Head mesa, west edge | (18, 8) | 64 | The 250m southern cliff face has just landed at the head plateau - sharp cliff |
| 3 | Head mesa, east edge | (43, 8) | 64 | The head's flat plateau (~25 units wide) - flat-topped, NOT pointed |
| 4 | Throat notch bottom | (58, 50) | 22 | The DEEPEST notch in the silhouette; 42-unit plunge from the head |
| 5 | Chin mesa, west edge | (66, 32) | 40 | Small mesa rising out of the throat notch |
| 6 | Chin mesa, east edge | (81, 32) | 40 | Chin's short flat plateau (~15 units wide) |
| 7 | Adam's apple notch bottom | (92, 42) | 30 | Shallower notch than the throat (10-unit drop, vs 42 for throat) |
| 8 | Body mesa, west edge | (108, 12) | 60 | Body plateau begins - height comparable to head, just 4 units lower |
| 9 | Body mesa, east edge | (188, 12) | 60 | Body's long flat plateau (~80 units wide) - the longest mesa, the visual mass |
| 10 | Knee rise | (228, 40) | 32 | Subtle undulation on the descent off the body |
| 11 | Shin descent | (258, 48) | 24 | Gradual descent toward the lake level |
| 12 | Foot terminus | (304, 58) | 14 | Rightmost point - near-flat foot stretch; red dot sits here |

Critical recognition rules:

1. **Three flat-topped mesas**, not one peak. Head, chin, body. v1
   and v2 of this mark wrongly treated the silhouette as a single
   dominant peak with a long cascade. Corrected v3 reads as three
   distinct plateaus.
2. **Two notches**. Throat notch (between head and chin) is deeper
   than Adam's apple notch (between chin and body). The throat
   notch is the silhouette's most dramatic single moment.
3. **Head and body comparable in height** (y=8 vs y=12). The body
   is the widest mesa (~80 units of plateau, the visual mass); the
   head is slightly taller and dramatically more vertical on its
   outboard cliff.
4. **Flat tops, not pointed peaks**. Bezier control points at each
   plateau share the plateau's y-coordinate, enforcing a near-
   horizontal tangent at the top.

The line terminates at the foot (step 12) rather than continuing down
to the lake on the right. This is intentional: terminating at the
foot lets the red dot read as a terminal brand stamp (same logic as
a chart's line terminating at its latest-print dot). The figure is a
silhouette, not a closed shape; the eye does not expect it to land
on the water on the right.

On the LEFT, the line DOES anchor to the lake baseline at (4, 72)
because the head's outboard cliff genuinely rises out of the water.
Asymmetric, but defensible: the left side is where the eye enters
and needs grounding; the right side is where the eye exits on the
brand-signal dot.

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
- **Dot.** ON. The red dot at the chin start is the only red moment
  in the favicon - it threads the publication's accent through the
  browser tab.
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

### Option A (chosen): cropped head mesa + throat notch + chin start

`src/components/brand/SleepingGiantFavicon.astro`. 32 x 32 viewBox.
A single continuous path showing the head's outboard cliff face, the
flat-topped head mesa, the throat notch descent, and the start of the
chin mesa. The red dot sits at the rightmost terminus on the chin
start.

**Why this wins.**

1. **The head mesa + throat notch IS the iconic moment.** Any Thunder
   Bay resident reads the Sleeping Giant by the dramatic cliff face
   and the deep throat notch first. The body plateau is sustained but
   visually quieter at favicon scale; the foot is the brand-signal
   moment but anatomically generic. The head + throat is the
   recognition handle.
2. **It survives the raster.** A 32 x 32 cropped silhouette at 2.25px
   stroke rasterizes to a legible mark at the 16px browser-tab size.
   The full 4:1 multi-mesa silhouette at 32px wide would compress to
   32 x 8 and read as a smudge - and the three-mesa structure cannot
   be legibly compressed into that strip regardless.
3. **It preserves the brand-pattern.** The cropped favicon still
   terminates with a red dot at the rightmost point (the chin start,
   not the foot). The pattern `[line][rightmost red dot]` is intact.
4. **It implies the multi-mesa structure.** Showing the head mesa
   followed by a notch followed by the start of another mesa cues
   the eye that more mesas lie beyond - the favicon is a fragment
   that points at the whole silhouette, not a different silhouette.
5. **Geographic identity preserved.** The favicon still says "Sleeping
   Giant" because the flat-topped cliff + throat notch is the
   silhouette's strongest visual signature. A wordmark `S` would
   erase the place; a bare red dot would erase the figure.

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
The Vignelli simplification is about visual elements (single ink line,
no fill, no decoration), not about segment count; the multi-mesa
structure requires more segments than v1/v2 used. The full path string:

```
M 4 72
C 8 60, 12 20, 18 8
C 26 8, 35 8, 43 8
C 50 8, 54 36, 58 50
C 60 50, 63 36, 66 32
C 72 32, 76 32, 81 32
C 85 32, 89 40, 92 42
C 96 42, 102 18, 108 12
C 135 12, 162 12, 188 12
C 204 14, 218 28, 228 40
C 238 42, 248 44, 258 48
C 266 52, 270 56, 274 58
C 284 58, 294 58, 304 58
```

Segment-by-segment read:

1. `M 4 72` - lake baseline (left edge, behind the head's cliff).
2. `C 8 60, 12 20, 18 8` - sharp cliff rise to head plateau west edge.
3. `C 26 8, 35 8, 43 8` - head mesa plateau (flat top, y=8 throughout).
4. `C 50 8, 54 36, 58 50` - throat notch descent (deepest notch).
5. `C 60 50, 63 36, 66 32` - rise onto chin mesa west edge.
6. `C 72 32, 76 32, 81 32` - chin mesa plateau (flat top, y=32).
7. `C 85 32, 89 40, 92 42` - Adam's apple notch (shallower).
8. `C 96 42, 102 18, 108 12` - rise onto body mesa west edge.
9. `C 135 12, 162 12, 188 12` - body mesa plateau (flat top, y=12).
10. `C 204 14, 218 28, 228 40` - descent off body into the knee rise.
11. `C 238 42, 248 44, 258 48` - knee/shin undulation.
12. `C 266 52, 270 56, 274 58` - shin descent to foot level.
13. `C 284 58, 294 58, 304 58` - foot stretch (flat, y=58 throughout).

Red dot: `<circle cx="304" cy="58" r="3" />` (inline variant) or
`r="4"` (og variant). Filled in `var(--accent)`, no stroke.

### 7.2 Favicon (`SleepingGiantFavicon.astro`)

ViewBox `0 0 32 32`. One M, four cubic-bezier segments, no lifts.
Cropped to head mesa + throat notch + chin start - the three-feature
signature that survives the 16-32px raster.

```
M 2 28
C 3 22, 5 8, 8 4
C 12 4, 16 4, 20 4
C 22 4, 23 16, 24 22
C 25 22, 27 18, 28 16
```

Segment-by-segment read:

1. `M 2 28` - lake baseline (left edge).
2. `C 3 22, 5 8, 8 4` - sharp cliff rise to head plateau west edge.
3. `C 12 4, 16 4, 20 4` - head mesa plateau (flat top, y=4).
4. `C 22 4, 23 16, 24 22` - throat notch descent.
5. `C 25 22, 27 18, 28 16` - rise onto chin start (terminus).

Red dot: `<circle cx="28" cy="16" r="2.5" />`. Filled in `var(--accent)`,
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
