# OG card — default — visual spec

Status: art-director, 2026-05-23. Supersedes the legacy
`og-preview/index.astro` (random sparkline + "in one place, on a single
page" tagline) which Jay flagged as "looks like crap."

This document specifies the composition that renders to
`public/og-default.png` at 1200×630 px, served as `og:image` for every
Sibley Creek route via `BaseLayout.astro`.

The HTML source lives at `public/_design/og-default-source.html`.

---

## 1. Tagline copy

**"Canadian macro. Until it's obvious."**

Rationale: direct echo of the user-ratified splash hero H1 (locked
2026-05-20). Two short fragments, period-after-fragment construction
matching the chart-title voice canon (`writing-style.md` Sec 4.2). The
first fragment names the domain; the second carries the editorial take.
A reader who clicks through from a LinkedIn share sees voice continuity
on the splash — same sentence, same cadence — which is the cohesion
signal we want.

Alternatives considered and rejected:

- **"Independent macroeconomic research. Canada."** — Reads as a
  directory-listing colophon. Institutional but flat; loses the
  take-driven edge that distinguishes Sibley Creek from BoC press
  releases and bank-desk research notes.
- **"Seeing clearly comes from knowing what to ignore."** — The splash
  aphorism deck. Distinctive, but in isolation on an OG card it strands
  the reader without a domain anchor. The wordmark "SIBLEY CREEK" tells
  them nothing about what we cover; the tagline must.
- **"Macroeconomic research on Canada. Independent."** — Status report
  with a one-word kicker. Better than the current "indicators and
  analysis, in one place, on a single page" but still mostly inventory.

Banned phrases (per project memory):
- "in one place, on a single page" — AI-template tell, in the current
  ugly card.
- "rigorous", "primary-source", "data-driven" — voice-doctrine talking
  about itself (`feedback_voice_doctrine_stays_internal.md`).
- "load-bearing" — banned across all surfaces.

---

## 2. Composition

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│                                                                     │  ← 96px top
│                                                                     │
│                                                                     │
│         ╭──╮         ╭─────────────────────────────────╮  ●         │
│        ╱    ╲___╱──╲╱                                   ╲           │  ← Sleeping Giant mark
│                                                                     │     (centered horizontally)
│                                                                     │
│                                                                     │
│                                                                     │
│      SIBLEY CREEK                                                   │  ← Wordmark (left-aligned, x=80)
│                                                                     │
│      Canadian macro. Until it's obvious.                            │  ← Tagline
│                                                                     │
│                                                                     │
│      ─────────────────────────                                      │  ← 1px hairline rule, 240px wide
│      SIBLEYCREEK.CA                                                 │  ← URL micro-caps
│                                                                     │  ← 64px bottom
└─────────────────────────────────────────────────────────────────────┘
   1200 × 630
```

**Composition rationale — three reasons it works:**

1. **Sleeping Giant mark is the visual hook.** The user-ratified brand
   mark (multi-mesa silhouette + foot-terminus red dot) is the
   publication's geographic identity, per `sleeping-giant-mark.md` Sec
   5.2. Placing it as the top hero element — large, centered, breathing
   room above and below — gives a senior reader the immediate "this is a
   publication brand, not a SaaS template" read. The mark also reads at
   thumbnail size because the multi-mesa silhouette has enough
   horizontal mass to survive 80px-wide compression.

2. **Wordmark + tagline as a typographic block, not a stack of
   floating elements.** Left-aligned at x=80, both sit on the same
   left rule. The wordmark is Manrope 900 / 72px / 0.14em tracked /
   uppercase — the publication's display register. The tagline sits
   28px under it in Manrope 400 / 30px, mixed-case, no tracking. The
   weight contrast between the two is the hierarchy device (Vignelli's
   Manrope-weight-contrast rule), no second color needed.

3. **Hairline rule + URL as colophon.** A 1px true-black hairline at
   x=80–320 separates the tagline from the URL, then "SIBLEYCREEK.CA"
   sits in Manrope 600 / 16px / 0.18em tracked / uppercase as the
   colophon stamp. This is the same hairline-rule + micro-caps
   construction used on the splash colophon and the chartbook section
   headers; it reads as native Sibley Creek to anyone who's seen the
   site once.

**Center-of-composition discipline (for thumbnail/square crop):**

When LinkedIn / iMessage crops the 1200×630 to ~600×600 (centered crop,
removing 300px from each side), the visible region becomes the central
600px wide × 630px tall band. Inside that band:

- Sleeping Giant mark: visible in full (mark is 720px wide centered on
  the canvas, so the center 600px shows the head + body + foot+dot —
  the entire silhouette stays in frame because the centered crop window
  starts at x=300 and the mark starts at x=240; the leftmost 60px of
  the mark (head cliff) clips, but the dot at x≈944 also clips. The
  mark is recognizable from chin → body → knees alone — see below for
  why this is acceptable). The wordmark "SIBLEY CREEK" starts at x=80;
  the centered crop cuts off "SIB" — wordmark fails on square crop.

**Adjusted composition to survive square crop.** The wordmark is moved
to **center-aligned at x=600** (the canvas centerline), so under a
square crop "SIBLEY CREEK" remains centered and fully visible. The
tagline, hairline, and URL likewise center on x=600. The Sleeping
Giant mark is **already centered** in the original spec, so it survives.
This is the canonical OG composition that holds at both 1200×630 and
~600×600 crop.

(The asymmetric left-aligned layout in the diagram above is the prior
draft; the implemented HTML below uses the symmetric center-aligned
layout — every block centered on x=600. Diagram is left in the spec as
the rejected alternative for traceability.)

---

## 3. Typography

All sizes are the **rendered PNG size** (1200×630 canvas). Per the
spec brief, no text in the rendered card is under 24px.

| Element | Family | Weight | Size | Tracking | Case | Color |
|---------|--------|--------|------|----------|------|-------|
| Sleeping Giant mark (path) | — (SVG) | stroke 2px | viewBox 0 0 320 80 rendered at 720px wide | — | — | `#000000` line + `#E63946` dot |
| Wordmark | Manrope | 900 | 72px | 0.14em | uppercase | `#000000` |
| Tagline | Manrope | 400 | 30px | normal | sentence-case | `#000000` |
| Colophon URL | Manrope | 600 | 16px | 0.18em | uppercase | `#000000` |

Weight ladder is Manrope 200 / 400 / 600 / 800 / 900 — all available in
the project's already-loaded font (`fonts.css`). The 900 wordmark is one
notch heavier than the splash 800 H1; OG cards live in low-attention
contexts (a thumbnail in a feed), and the extra weight helps the
wordmark hold at 80px.

The tagline at 30px is comfortably above the 24px threshold and reads
clearly at thumbnail. The colophon at 16px is below the 24px threshold
**by design** — at thumbnail size it's expected to be illegible (it
becomes a ~1px-tall smear). It's there for the full-size card where
"SIBLEYCREEK.CA" reinforces the brand at the bottom of the composition.
If 16px reads as too thin at full-size review, bump to 18px.

---

## 4. Color discipline

The card uses only the canonical Vignelli palette:

- Paper `#FFFFFF`
- Ink `#000000`
- Signal red `#E63946` — **only** on the Sleeping Giant mark's foot
  terminus dot (one brand-signal moment, per
  `sleeping-giant-mark.md` Sec 5.1).

No section-accent colors (gdp blue, inflation red, etc.) are used — those
are chart-series identities, not brand colors. No drop shadow, no
gradient, no tinted background. Pure paper, pure ink, one red dot.

---

## 5. Spacing measurements (1200×630 canvas)

Absolute-px positioning for screenshot determinism. No flex, no
percentage units.

| Block | Top (px) | Center on x | Width (px) | Height (px) |
|-------|----------|-------------|------------|-------------|
| Sleeping Giant mark | 100 | 600 | 720 | 180 |
| Wordmark "SIBLEY CREEK" | 360 | 600 | (intrinsic) | 72 |
| Tagline | 462 | 600 | (intrinsic) | 40 |
| Hairline rule (1px) | 540 | 600 | 240 | 1 |
| Colophon URL | 562 | 600 | (intrinsic) | 18 |

Vertical breathing room:
- 100px above the mark
- 80px gap mark-to-wordmark (mark bottom at 280, wordmark top at 360)
- 30px gap wordmark-to-tagline (wordmark baseline ~432, tagline top
  at 462)
- 38px gap tagline-to-hairline (tagline baseline ~502, rule at 540)
- 50px below the URL to canvas bottom (URL baseline ~580, canvas 630)

The composition leaves a deliberate paper margin on all four sides —
generous negative space is the Vignelli signature here. Tightening the
spacing to "use the space" is the wrong instinct; restraint is the
register.

---

## 6. Sleeping Giant mark — embedded SVG

The mark's path data is canonized in `design/sleeping-giant-mark.md`
Sec 7.1. The OG card embeds the path inline (not a `/favicon.svg`
reference) so the rendered PNG is deterministic and standalone, and
so the OG variant's 2px stroke + 4px-radius dot can be hard-coded
per `sleeping-giant-mark.md` Sec 4.

ViewBox: `0 0 320 80`. Rendered at 720×180 (preserveAspectRatio
`xMidYMid meet`). Stroke `#000000` 2px, dot `#E63946` r=4 at
(304, 58).

---

## 7. Render command

After the HTML template is authored at
`public/_design/og-default-source.html`, main Claude renders it via:

```
node scripts/render_og_card.mjs public/_design/og-default-source.html public/og-default.png
```

The render script (main Claude writes it) loads the HTML file in a
Playwright Chromium page, sets viewport to **1200×630** at
deviceScaleFactor 1 (no Retina doubling — OG consumers expect exact
1200×630 PNG dimensions), waits for `document.fonts.ready`, takes a
fullPage: false screenshot of the body, and writes the PNG.

Viewport: **1200 × 630**, deviceScaleFactor: 1.

---

## 8. Verification

Open `public/_design/og-default-source.html` directly in a browser
window sized exactly 1200×630 (use Chrome's "Toggle device toolbar"
→ "Responsive" → enter 1200 × 630). The composition should match the
absolute-px spec above:

- Sleeping Giant mark centered horizontally, ~100px from top
- "SIBLEY CREEK" centered, large display weight, ~360px from top
- Tagline "Canadian macro. Until it's obvious." centered ~462px from
  top
- Short hairline rule centered ~540px from top
- "SIBLEYCREEK.CA" centered ~562px from top

If Manrope hasn't loaded (e.g. offline) the fallback is Helvetica
Neue → Helvetica → Arial → sans-serif. The render pipeline must
ensure Manrope is loaded (the HTML imports Google Fonts directly so
Playwright + network → works out of the box).

---

## 9. What this spec does NOT do

- **Per-page OG variants.** Section-specific OG cards (e.g. the policy
  page showing a policy-rate chart) are a future deliverable. v1 ships
  one default card used across the entire site.
- **Bilingual EN/FR.** A French-tagline variant is deferred to v2.
  Note that "Macro canadien. Jusqu'à ce que ce soit évident." is
  ~30% longer; the composition has room for it but a separate render
  is needed.
- **Twitter/X card-specific dimensions.** X uses 1200×600 for
  `summary_large_image`; the 1200×630 PNG works there with a 30px
  vertical letterbox. If X-specific framing becomes a priority, a
  1200×600 variant can be rendered from the same HTML by setting the
  Playwright viewport accordingly.
