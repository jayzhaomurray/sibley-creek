# Open Graph card - `public/og-default.png`

Status: blessed. Author: art-director. 2026-05-11.
Implementer: frontend-designer. Implementation pattern: Astro page at
`/og-preview/` rendered at exact 1200x630, then Playwright screenshot to
`public/og-default.png`.

This is the FIRST visual impression a LinkedIn reader (audience: 2-3k
econ-world professionals) gets of Sibley Creek when the launch post
crosses their feed. The unfurl must read at thumbnail scale (LinkedIn
renders it ~552px wide on desktop, ~344px on mobile), and at full size
the Vignelli register must be immediately legible.

The card is a STATIC default - one image, used by every page until per-
article OG cards are authored. Treat it as the publication's marquee.

---

## 0. Reference grounding

Consulted before authoring:

- **Longreads** (`https://longreads.com/`) - their `og:image` is an
  article-specific photo card sized 1024x597 (close to the 1.91:1
  canonical). The takeaway is that editorial publications routinely
  ship per-article OG cards, but a DEFAULT site card needs to be a
  publication-identity statement, not an article statement.
- **Financial Times / The Economist** - WebFetch blocked by their bot
  filters; from prior knowledge, both ship a logotype-on-flat-field
  default OG (FT pink ground + masthead wordmark; Economist red ground
  + masthead wordmark + tagline rail). The pattern is: BRAND MARK +
  WORDMARK + ONE-LINE EDITORIAL POSITIONING, on a single flat ground,
  with generous negative space. Sibley Creek inverts the colour (white
  paper, not coloured) but keeps the same rhetorical structure.
- **Vignelli register, per `design/design-system.md`**: pure paper,
  pure ink, one accent moment, Manrope ladder, no chrome that doesn't
  earn its place. The OG card is the same page-design register
  scaled to a 1200x630 thumbnail.

The default OG card is a PUBLICATION COVER, not an article hero. Its
job is "this is Sibley Creek" + "this is what we cover" - the
LinkedIn equivalent of a magazine cover, not a magazine illustration.

---

## 1. Canvas

| Property | Value |
|---|---|
| Dimensions | 1200 x 630 px (1.91:1, LinkedIn/Twitter/Facebook canonical) |
| Background | Pure white `#FFFFFF` (`var(--paper)`) |
| Color space | sRGB; PNG output |
| Safe area | Nothing load-bearing within 40px of any edge. LinkedIn crops a small bezel on some surfaces (a few px on each side); the wordmark, mark, and tagline must clear that crop. |
| Outer rule | NO rounded corners, NO drop shadow, NO outer border. LinkedIn/Twitter draw their own card frame; we ship a clean rectangle. |

---

## 2. Composition - the call

**Two-zone vertical composition. Top zone is the brand mark sitting as
a hero (full-width framing element). Bottom zone is the wordmark +
tagline lockup, left-aligned.**

The Sleeping Giant mark sits as a FOCAL HERO at the top of the card,
centered horizontally, not as a tiny inline mark next to the wordmark.
Rationale: at the LinkedIn-thumbnail crop, an inline mark next to a
SIBLEY CREEK wordmark would shrink the mark to ~30-40 effective pixels
of width on screen and the multi-mesa silhouette would smudge. As a
hero, the mark gets ~720px of width on canvas (~330px on a desktop
LinkedIn unfurl thumbnail, ~206px on mobile) - enough to read the
three mesas and the red foot dot at every render size.

The wordmark sits BELOW the mark, not beside it. This is a deliberate
break from the masthead's inline lockup: the masthead is read with
intent at full page width, but the OG card is glanced at thumbnail
scale and the hero-mark composition reads as a publication cover at
thumb scale.

### 2.1 Vertical zone layout (from top)

| Zone | y-range | Height | Contents |
|---|---|---|---|
| Top margin (clear paper) | 0 - 110 | 110px | empty |
| Mark hero | 110 - 290 | 180px (4:1 of 720px wide) | Sleeping Giant mark, centered |
| Inter-zone clear paper | 290 - 410 | 120px | empty - this is the "magazine cover gutter" |
| Wordmark | 410 - 478 | ~68px tall (cap height of 64px wordmark) | "SIBLEY CREEK" |
| Tagline | 478+24 - 510 | ~28px tall | Tagline line |
| Hairline rule | 540 | 1px | optional - see Section 5.1 |
| Source line | 555 - 580 | ~14px tall | "sibleycreek.ca" micro-caps |
| Bottom margin (clear paper) | 580 - 630 | 50px | empty |

All vertical numbers are exact px positions on the 1200x630 canvas.
The implementer renders to these exact pixel rails - no auto-flow, no
flex-grow gaps. Determinism is the brief.

---

## 3. The Sleeping Giant mark - hero

Render via the canonical component, no re-authoring:

```astro
<SleepingGiantMark size={720} variant="og" />
```

- **Component.** `src/components/brand/SleepingGiantMark.astro`.
- **Variant.** `og` (2px stroke, 4px red foot dot - per canon Section 4 of `design/sleeping-giant-mark.md`).
- **Size.** `720` (width in px). Height auto-derives to 180px from the 4:1 viewBox aspect.
- **withAccent.** default `true`. The red foot dot at (304, 58) in the SVG's local 320x80 coordinate space MUST render. This is the card's one and only accent moment.
- **Position.** Centered horizontally. `left: 240px, top: 110px, width: 720px, height: 180px`. (`(1200 - 720) / 2 = 240`.)
- **Background.** Pure paper underneath. No card, no box, no shadow.
- **Stroke check.** At 720px wide rendered to a 552px-wide LinkedIn thumbnail, the 2px stroke composites to ~1.5 effective px - still legible. At the 344px mobile thumbnail, ~0.95px - the limit of legibility, but vector-effect: non-scaling-stroke (per the component) preserves it through the Playwright raster.

The mark is the publication. Treat it like the FT pink or the Economist red - the single most recognizable visual element on the card.

---

## 4. Wordmark - "SIBLEY CREEK"

| Property | Value |
|---|---|
| Text | `SIBLEY CREEK` (literal string; the masthead uses `text-transform: uppercase` on the source `site.name = "Sibley Creek"`. For the OG renderer, hardcode the all-caps string to remove any text-transform indirection at screenshot time.) |
| Font family | `var(--font-sans)` -> Manrope |
| Font weight | 900 (Black) - matches the masthead's `.vig-mast__mark` weight |
| Font size | **64px** (4x the masthead's 16px - significant scale-up for the hero register, but not so large it crowds the tagline). |
| Letter-spacing | `0.16em` - identical to the masthead |
| Line height | 1 (no leading; this is a single line) |
| Color | Pure ink `#000000` (`var(--ink)`) |
| Text transform | none (string is already uppercase in source) |
| Position | Left-aligned. `left: 80px, top: 410px`. The 80px left margin matches the page-frame breathing room and clears the LinkedIn crop. |
| Baseline alignment | The wordmark sits on a baseline at y=474 (top + ~64px cap height). |

The wordmark is left-aligned, not centered, because:
1. The mark above is centered as a hero; the wordmark left-aligned creates a deliberate compositional tension (centered top, flush-left below). This is a Knoll-catalogue move - axes of alignment that don't all share the same gravity.
2. Left-alignment leaves the right side of the lower zone for either a small `sibleycreek.ca` URL stamp or pure paper - both legitimate Vignelli moves.

---

## 5. Tagline / deck

The `site.tagline` field in `src/data/sections.ts` currently reads
`"Canadian macro"` - a deliberate two-word category rail for the
masthead. For the OG card, that's TOO TERSE: this is the publication's
one-shot impression to a cold LinkedIn reader, and "Canadian macro"
on its own under SIBLEY CREEK reads more like a tag than a position.

**Recommendation: author a longer OG-specific tagline. The site
tagline stays as-is at "Canadian macro" for the masthead rail; the OG
card carries a longer editorial-positioning line.**

### 5.1 The OG tagline - the call

> **`Canadian macroeconomic indicators and analysis, in one place, on a single page.`**

Twelve words. Names: what the publication covers (Canadian macro
indicators + analysis), the editorial promise (singularity - one
place, one page - which is the entire dashboard concept distilled),
and implies the register (declarative, no hedge, no marketing).

Alternative if the recommended line tests long at render: the existing
`site.description` field reads
`"Sibley Creek - Canadian macroeconomic indicators and analysis. A
reading-first dashboard for analysts, policymakers, and serious
citizens."` - too long for one line at 26px, but its first sentence
("Canadian macroeconomic indicators and analysis.") is the fallback.

### 5.2 Tagline rendering

| Property | Value |
|---|---|
| Font family | `var(--font-sans)` -> Manrope |
| Font weight | 400 (Regular) - NOT ExtraLight 200. At a 1.91:1 thumbnail composited down, ExtraLight 200 will dissolve into the paper and the tagline will read as a vague shape. Regular 400 holds at the LinkedIn mobile thumbnail. |
| Font size | **26px** |
| Letter-spacing | `0` (default) - tracking only on the all-caps wordmark above |
| Line height | 1.3 |
| Color | Pure ink `#000000`. NOT muted, NOT a gray. Vignelli tokens collapse `--ink-muted` and `--ink-faint` to `#000000` anyway, so authored grays drift off-canon. |
| Position | Left-aligned, sharing the wordmark's `left: 80px` axis. Top: 478 + 24 = `502px` (24px gap below wordmark baseline). Single line - max width should be ~1040px to stay 80px from the right edge; the recommended copy at 26px Regular Manrope measures ~720px, well within. |
| Text transform | none |

---

## 6. Source line (optional chrome - the call: include)

A micro-caps `sibleycreek.ca` stamp at the bottom-left, sitting below
the tagline. Justification: the OG card is the thing a LinkedIn
reader sees BEFORE clicking. A visible URL in the card itself reduces
friction (reader knows where they're going) and reads as editorial
self-confidence - the publication signs its work.

| Property | Value |
|---|---|
| Text | `sibleycreek.ca` |
| Font family | `var(--font-sans)` -> Manrope |
| Font weight | 600 (SemiBold) - matches the masthead nav-label register |
| Font size | **13px** (matches `--fs-label`) |
| Letter-spacing | `0.14em` |
| Line height | 1 |
| Color | Pure ink `#000000` |
| Text transform | uppercase. Render as `SIBLEYCREEK.CA`. |
| Position | `left: 80px, baseline at y: 575px` (so the cap-top sits ~565, baseline 575, clear of the 50px bottom safe area). |

### 6.1 Hairline rule above source line - the call: NO

I considered a 1px black hairline above `SIBLEYCREEK.CA` (mirroring
the masthead's underline rule). Rejected: the wordmark already
provides the hierarchic anchor, the rule would add chrome that
doesn't earn its place against the Vignelli restraint rule, and at
LinkedIn-thumb scale a 1px hairline becomes a sub-pixel sliver that
muddies more than it organizes. Skip the rule.

---

## 7. Anti-chrome (what NOT to add)

The Vignelli register forbids any of the following on this card:

- NO eyebrow strap (e.g. "INDEPENDENT - CANADIAN MACRO"). The wordmark + tagline + URL already lock the positioning; an eyebrow above the mark would be a fourth typographic register competing for attention.
- NO additional red. The brand mark's foot dot is the single accent moment. Do not introduce a red rule, a red eyebrow tick, a red dot on the wordmark, or a red URL color. Per canon (`design/sleeping-giant-mark.md` Section 8): one red dot, never more.
- NO photograph, NO illustration, NO chart preview, NO data screenshot. The default OG is a publication identity card, not an article hero. Per-article OGs (future scope) can carry article-specific data viz; the default carries the brand.
- NO date stamp, NO edition number, NO "As of [date]" eyebrow. The default OG image is served from `public/og-default.png` and cached by LinkedIn for weeks; any date on it goes stale instantly. Date stamps belong on per-page OG cards generated at build time.
- NO drop shadow, NO inner glow, NO gradient, NO tint, NO texture, NO grain. Pure paper, pure ink, pure red dot.
- NO rounded corners on anything. Zero radius.

---

## 8. Implementation - notes for frontend-designer

### 8.1 The pattern

Create a single Astro page at `src/pages/og-preview/index.astro`. The
page renders the card at exactly 1200x630, with absolute pixel
positioning, then a Playwright (or `playwright/chromium` via Astro's
build step) screenshot captures the rendered DOM to
`public/og-default.png`.

### 8.2 HTML structure (suggested)

```astro
---
import SleepingGiantMark from "../../components/brand/SleepingGiantMark.astro";
---
<!doctype html>
<html lang="en-CA">
<head>
  <meta charset="utf-8" />
  <meta name="robots" content="noindex, nofollow" />
  <link rel="stylesheet" href="/src/styles/fonts.css" />
  <link rel="stylesheet" href="/src/styles/tokens.css" />
  <style>
    html, body { margin: 0; padding: 0; background: #FFFFFF; }
    .og-card {
      position: relative;
      width: 1200px;
      height: 630px;
      background: #FFFFFF;
      overflow: hidden;
    }
    .og-card__mark {
      position: absolute;
      left: 240px;
      top: 110px;
      width: 720px;
      height: 180px;
    }
    .og-card__wordmark {
      position: absolute;
      left: 80px;
      top: 410px;
      font-family: var(--font-sans);
      font-weight: 900;
      font-size: 64px;
      line-height: 1;
      letter-spacing: 0.16em;
      color: #000000;
    }
    .og-card__tagline {
      position: absolute;
      left: 80px;
      top: 502px;
      font-family: var(--font-sans);
      font-weight: 400;
      font-size: 26px;
      line-height: 1.3;
      color: #000000;
    }
    .og-card__url {
      position: absolute;
      left: 80px;
      top: 565px;
      font-family: var(--font-sans);
      font-weight: 600;
      font-size: 13px;
      line-height: 1;
      letter-spacing: 0.14em;
      text-transform: uppercase;
      color: #000000;
    }
  </style>
</head>
<body>
  <div class="og-card">
    <div class="og-card__mark">
      <SleepingGiantMark size={720} variant="og" />
    </div>
    <div class="og-card__wordmark">SIBLEY CREEK</div>
    <div class="og-card__tagline">
      Canadian macroeconomic indicators and analysis, in one place, on a single page.
    </div>
    <div class="og-card__url">sibleycreek.ca</div>
  </div>
</body>
</html>
```

Notes:
- All sizes are in absolute px so the Playwright screenshot is deterministic. No `rem`, no `em`, no viewport units.
- `meta name="robots" content="noindex, nofollow"` keeps the preview page out of search results. The page is a build artifact, not a public destination.
- The page MUST NOT be linked from the production nav, sitemap, footer, or any internal route. It exists for the screenshot pipeline only.
- Add `Disallow: /og-preview/` to `public/robots.txt` if it doesn't already include the path.
- The Astro page should NOT extend `BaseLayout` - it needs to be a bare HTML document with no nav, no footer, no global chrome bleeding into the screenshot. Inline `<style>` is fine; this is a one-shot render surface, not a production page.

### 8.3 Playwright screenshot recipe

```js
// scripts/build-og-image.mjs (suggested)
import { chromium } from "playwright";

const browser = await chromium.launch();
const page = await browser.newPage({
  viewport: { width: 1200, height: 630 },
  deviceScaleFactor: 1, // 1x raster - sharp at the 1200x630 canonical size
});
await page.goto("http://localhost:4321/og-preview/", { waitUntil: "networkidle" });
// Wait for Manrope to finish loading before screenshotting.
await page.evaluate(() => document.fonts.ready);
await page.screenshot({
  path: "public/og-default.png",
  type: "png",
  clip: { x: 0, y: 0, width: 1200, height: 630 },
});
await browser.close();
```

Run this against a local `astro dev` server (or a built preview). Wire it into the build pipeline as a one-time generator (NOT every build - the image is static; regenerate only when the OG content changes).

### 8.4 Font-loading determinism

The Playwright screenshot must wait for Manrope 400 and Manrope 900 to load before capturing, or the screenshot will fall back to Helvetica Neue / Arial and the wordmark register will collapse. The recipe above uses `document.fonts.ready` for that; verify in the rendered PNG that the wordmark is heavy-stroked Manrope Black, not a generic sans.

### 8.5 BaseLayout meta tag

`src/layouts/BaseLayout.astro` already references `/og-default.png`. After Playwright writes the file to `public/og-default.png`, the LinkedIn crawler should resolve it on next fetch. LinkedIn caches OG previews aggressively (7+ days); use the LinkedIn Post Inspector (`https://www.linkedin.com/post-inspector/`) to force a re-crawl after the file lands. Twitter has a similar Card Validator (`https://cards-dev.twitter.com/validator`).

---

## 9. Acceptance checklist

Frontend-designer / art-director reviews against:

- [ ] Exactly 1200 x 630 px, PNG, sRGB.
- [ ] Pure white background, no tint, no off-white.
- [ ] Sleeping Giant mark renders at 720x180 centered horizontally, with the red foot dot visible at the rightmost terminus.
- [ ] Wordmark renders as Manrope 900 / 64px / 0.16em letter-spacing, all caps, left-aligned at x=80.
- [ ] Tagline renders as Manrope 400 / 26px / single line, left-aligned at x=80, below the wordmark.
- [ ] Source URL renders as Manrope 600 / 13px / 0.14em uppercase, left-aligned at x=80.
- [ ] No second red anywhere on the card.
- [ ] No chrome, no shadow, no rule, no border, no badge, no rounded corner.
- [ ] At 552px LinkedIn-desktop thumbnail size, the mark's three mesas are still legible and the wordmark is readable.
- [ ] At 344px LinkedIn-mobile thumbnail size, the wordmark is readable and the red foot dot is visible.
- [ ] `public/robots.txt` disallows `/og-preview/`, OR the `/og-preview/` page carries `noindex` (per Section 8.2 it does).

---

## 10. Open questions / deferred

- **Per-article OG cards.** Out of scope for this dispatch. When section pages or deep dives ship their own OG cards, the same template (mark hero + wordmark + article-specific deck + source) is the natural starting point - swap the tagline for the article title, add a small section eyebrow, keep the mark.
- **Dark mode OG.** LinkedIn does not render OG cards in dark mode; the unfurl is always on the LinkedIn surface colour. No dark variant needed.
- **Animated OG.** Twitter supports animated WebP/GIF OG cards. The Vignelli register forbids motion chrome; do not animate.
