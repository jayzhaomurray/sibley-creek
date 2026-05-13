# macro-research-department - Design System

Status: v1.0, living document. Author: art-director.
Last updated: 2026-05-11.

This is the visual constitution. Every page, chart, and component cites this
document. Frontend-designer and chart-builder implement to this spec. When a
constraint forces deviation, raise it back to art-director - do not silently
relax the bar.

---

## Changelog

- **v1.0 (2026-05-11) - Vignelli canonicalization.** Full rewrite. The
  publication has chosen the Vignelli register as its production identity:
  pure white paper, pure black ink, a single MTA red accent, Manrope as the
  only sans family (weight contrast as hierarchy), IBM Plex Mono for data,
  direction encoded by glyph not color, 1px pure-black hairline rules. The
  prior FT / warm-paper / burgundy / Source Serif register (v0.1 - v0.2) is
  retired. All production code in `src/styles/tokens.css`,
  `src/styles/base.css`, and `src/components/**` has already migrated; this
  document is the matching canon. The basics-layer-template and hero-chart-
  spec are deprecated; the chartbook-template.md replaces them.
- v0.2 (2026-05-11): Added mini-chart spec (Section 5.1) and per-section
  mini-chart matrix (5.2). Index-tile component spec (6.1).
- v0.1 (2026-05-11): Initial canon - FT / warm-paper / Source Serif
  register. Retired in v1.0.

---

## 1. Visual identity statement

**Reference lane: Massimo Vignelli, Josef Mueller-Brockmann, Lella Vignelli,
the Knoll catalogues, the NYC Subway Diagram, Edward Tufte's data-ink
discipline.**

We are an editorial-grade Canadian macro research dashboard set in the
Vignelli register. The page is paper-white, the ink is pure black, the rules
are hairline, and one signal red carries every brand-accent moment we
permit. Type is one sans family (Manrope) across the entire page, with
weight contrast - not size, not italic, not color - doing the hierarchy
work. Numerical data is set in IBM Plex Mono so the reader knows at a
glance that what they are reading is a measurement, not a designed
flourish. Direction is encoded by ASCII glyph (up-pointing triangle,
down-pointing triangle, em dash). Hue is never a direction; it is reserved
for the publication's voice.

The reader is a serious adult - a policy analyst, a journalist, a Bay
Street economist, an informed citizen. They came for one chart and one
paragraph that tell them something true about the Canadian economy. The
page should feel like it was **set, not assembled**: the same care a 1960s
Knoll catalogue showed for a chair specification, we show for a CPI print.

**Lineage.** The decisions in this document descend from a specific
typographic tradition:

- **Massimo Vignelli** - the discipline of using a single sans family
  across an entire system (Helvetica for him, Manrope for us). The belief
  that designers do not need decoration to design well; they need
  restraint and proportion. The 1972 NYC Subway Diagram is the spiritual
  exemplar: one accent color (MTA red, our `--accent`), one hairline rule
  vocabulary, one weight-contrast hierarchy, no extra ink. Vignelli's own
  Unimark identity for the MTA - the way a single red moment carries the
  brand across an otherwise monochrome diagram - is the rule we live by.
- **Josef Mueller-Brockmann** - the Swiss grid, the modular spacing
  scale, the rejection of decorative typography. The 4/8/16/24/32/64/128
  scale we use is a direct Mueller-Brockmann descendant.
- **Lella Vignelli** - the partnership's eye for proportion at small
  sizes: how a 10px micro-cap eyebrow with `0.22em` tracking can carry the
  same authority as a 40px headline if its proportions are right.
- **The Knoll catalogues (1950s-1970s)** - the model for the chartbook
  unit. Each catalogue page was: an indicator name, a plate number, a
  specification table, a single photographic plate, a source line. We
  borrow that anatomy wholesale for the section pages: a plate number
  (`PLATE 01`), an indicator name, a chart, a prose interpretation, a
  source line.
- **The NYC Subway Diagram (1972)** - the one-accent rule. MTA red
  (#E63946) is reserved for **brand-signal moments only**: the figure
  number in a panel eyebrow, the latest-print dot on a chart, the focus
  ring on keyboard navigation, the hover transition on a link, the
  selection highlight. Never on data direction. Never on chrome.
- **Edward Tufte, _The Visual Display of Quantitative Information_** -
  the data-ink ratio. Every mark on a chart earns its place. Gridlines
  are anchors, not features. Axis chrome is the hairline minimum that
  conveys range. Annotations, when they exist, sit in white space - they
  do not overlay data.

**What this commits us to:**

- **Pure white paper, pure black ink.** No warm paper. No near-black.
  `#FFFFFF` and `#000000`. The page is not a print broadsheet; it is a
  Swiss typographic specification.
- **Manrope, one family, full weight ladder.** 200 (ExtraLight) for ledes
  and decks; 400 (Regular) for body and table data; 600 (SemiBold) for
  micro-caps eyebrows and chart labels; 800 (ExtraBold) for headlines and
  emphasis; 900 (Black) for the wordmark. **Weight contrast is the
  hierarchy device** - we do not promote a thought by making it larger
  or coloring it red; we promote it by making it heavier.
- **IBM Plex Mono for data only.** Numeric values in tables and callouts,
  stamps (`AS OF`, `LATEST RELEASE`), plate numbers in mono caps. Plex
  Mono signals: this is a measurement, not a designed number.
- **One accent color, used sparingly.** MTA red `#E63946`. Brand-signal
  moments only (see Section 3 for the full rules). Never on data.
- **1px pure-black hairlines.** Between sections, between table rows,
  around chart frames, between panels. No warm grays; no taupe; no rule
  weight other than 1px (or 2px for a section-closing rule).
- **Direction by glyph, not color.** Up-pointing triangle (`U+25B2`),
  down-pointing triangle (`U+25BC`), em dash (`U+2014`). Pos/neg
  green/red are retired for direction encoding.
- **Light mode only, v1.** Dark mode is deferred.

**What this commits us against:**

- No serif. No italic except true emphasis (and even then, weight
  contrast is preferred). No multiple sans families.
- No warm paper. No off-white. No cream. No paper texture overlay.
- No green for positive, no red for negative. Hue is brand, not data.
- No drop shadows. No gradients. No glassmorphism. No card-radius
  pillows.
- No icon-driven navigation. No emoji in UI. No decorative chart marks.
- No entrance animations. No staggered reveals. No hover-only data.
  No parallax. No number tickers.

**Exemplars (what to study, and what to take from each):**

- **Massimo Vignelli + Unimark, NYC Subway Diagram (1972).** Take: the
  one-accent rule, the hairline rule vocabulary, the willingness to let
  a single red moment carry the brand across an otherwise monochrome
  system.
- **Vignelli Associates, Knoll furniture catalogues (1967-1979).** Take:
  the plate anatomy. A plate number, an indicator name, a specification,
  one image (one chart), a source line. Nothing else on the page.
- **Josef Mueller-Brockmann, _Grid Systems in Graphic Design_ (1981).**
  Take: the modular spacing scale; the discipline of column-based
  layout; the rejection of arbitrary white space.
- **Edward Tufte, _The Visual Display of Quantitative Information_
  (1983).** Take: data-ink ratio; small multiples discipline; the rule
  that every annotation must anchor to a specific datum.
- **A. M. Cassandre / Roger Excoffon, mid-century French rail and
  shipping posters.** Take (in spirit, not literally): the courage to
  let typography do the visual work without illustration.

We are **not** FT (too warm, too serif). **Not** The Economist (red on
everything). **Not** Bloomberg Terminal (too dense, too dark). **Not** NYT
Upshot (too journalistic-warm). We sit closest to a Swiss-school exhibition
catalogue: the IBM annual report Paul Rand designed; the Unimark MTA
specification; the Knoll showroom guide.

---

## 2. Typography

**One sans family. Weight contrast is the hierarchy device. Mono for
data.**

### Families

- **Sans (the only display + body family):**
  `"Manrope", "Helvetica Neue", Helvetica, Arial, sans-serif`
  - Open-source humanist sans. Ships an ExtraLight (200) through Black
    (900) range, which is precisely what the Vignelli weight-contrast
    hierarchy requires.
  - Used for every text element on the page: wordmark, headline,
    headline-question, lede, deck, body, label, eyebrow, axis tick,
    direct chart label, source line prefix, button.
  - Token: `--font-sans`.

- **Mono (data only):**
  `"IBM Plex Mono", ui-monospace, "SFMono-Regular", Menlo, Consolas, monospace`
  - Plex Mono pairs visually with Manrope (both humanist proportions).
  - Used for: numeric table cells, the readout value in a homepage
    panel, the latest-release stamp, the source line citation body, the
    plate number on a chartbook eyebrow, the `AS OF` body, the as-of
    body in any panel eyebrow.
  - Plex Mono signals to the reader: "what you are reading is a
    measurement, vintaged to a specific moment." Never used decoratively.
  - Token: `--font-mono`.

- **Serif (deprecated, aliased to sans):**
  `--font-serif` resolves to the same value as `--font-sans` so any
  legacy component that still references it falls back to Manrope
  cleanly. **Do not introduce new references to `--font-serif`.** The
  serif register is retired in v1.0.

### Weight ladder - the hierarchy

Weights are doing the work that size, italic, and color would do in a less
disciplined system. The ladder, in order of editorial promotion:

| Weight | Token (legacy alias)             | Role                                                   |
|--------|----------------------------------|--------------------------------------------------------|
| 200    | `--fw-extralight`                | Lede paragraphs, deck under headlines, lorem placeholders. The "quiet" weight that signals "this is context, not the lead." |
| 400    | `--fw-regular`                   | Body prose, table data, axis tick labels, direct chart labels.        |
| 600    | `--fw-medium` / `--fw-semibold`  | Micro-caps eyebrows (with letter-spacing), chart prose interpretation `<strong>`, kicker tokens, table headers, button labels, source-line "Source:" prefix. |
| 800    | `--fw-extrabold`                 | Headlines (display-xl through display-sm), section headline question, the plate number numeral after the word "PLATE", emphasized indicator names in the primary print row of a table.   |
| 900    | (not tokenized; inline)          | The site wordmark (`SIBLEY CREEK`) only. Reserved.     |

**Promotion rule.** To draw a reader's eye to a phrase, **first try weight
contrast** (bump a Regular run to SemiBold, or a SemiBold to ExtraBold). If
weight contrast is not enough, **only then** consider an accent-red token
(the brand-signal class). Italic is not in the toolkit. Color is not in the
toolkit (for non-brand emphasis).

### Scale

Modular scale at ratio 1.20 (minor third), base 16px. Capped on both ends.

| Token        | Size  | Line height | Default weight | Family role | Role                                            |
|--------------|-------|-------------|----------------|-------------|-------------------------------------------------|
| `display-xl` | 40px  | 1.10        | 800            | Sans        | Page hero headline (one per page max).          |
| `display-lg` | 33px  | 1.15        | 800            | Sans        | Section opener.                                 |
| `display-md` | 28px  | 1.20        | 800            | Sans        | Chartbook unit title, hero panel title.         |
| `display-sm` | 23px  | 1.25        | 800            | Sans        | Indicator panel headline, callout big number.   |
| `deck`       | 19px  | 1.45        | 200            | Sans        | Deck / lede under a headline (ExtraLight).      |
| `body-lg`    | 19px  | 1.55        | 400            | Sans        | Lede paragraph in body flow.                    |
| `body`       | 17px  | 1.55        | 400            | Sans        | Default body copy.                              |
| `body-sm`    | 15px  | 1.50        | 400            | Sans        | Chartbook interpretation prose; captions.       |
| `label`      | 13px  | 1.40        | 600            | Sans        | Eyebrow micro-caps, chart axis label.           |
| `micro`      | 12px  | 1.40        | 600            | Sans        | Source-line prefix, footnotes, tick labels.     |
| `mono-sm`    | 14px  | 1.45        | 400            | Mono        | Table numeric column.                           |
| `mono-xs`    | 12px  | 1.40        | 400            | Mono        | Stamp body, source citation body, plate-number numeral, table micro stamp. |

### Letter-spacing rules

The Vignelli register is precise about tracking; these are not negotiable.

- **Display sizes (`display-xl`, `display-lg`, `display-md`,
  `display-sm`):** tight tracking. `-0.018em` to `-0.005em` depending on
  size, larger sizes tracked tighter. The `display-xl` headline runs at
  `-0.015em`; the `display-md` chartbook title at `-0.012em`. **Tight on
  display.**
- **Body (`body`, `body-sm`, `body-lg`):** natural tracking. `0`.
- **Micro-caps eyebrows (`label`, `micro` when set in `text-transform:
  uppercase`):** **generous tracking, `0.18em` to `0.22em`.** This is
  the signature Vignelli move - tight display, generous micro-caps. The
  eyebrow `SECTION 1 OF 7 | INFLATION` is set at `0.22em` tracking; the
  source-line prefix `SOURCE:` at `0.18em`; the figure-number eyebrow
  `FIGURE 1.` at `0.22em`.
- **Wordmark (the site name, set in 900 Black):** `0.16em` tracking,
  uppercase, 16px.
- **Plex Mono data:** natural tracking (`0`). Never tracked.

### Treatment rules

- **Numbers in body prose use Manrope with tabular figures.** Manrope
  ships `font-feature-settings: "tnum"`; we enable it globally in
  `:root`. Prevents column shimmy in numeric paragraphs.
- **Numbers in tables use Plex Mono.** Right-aligned, tabular,
  weight 400.
- **Numbers in callouts (the big-number readout on a panel) use Plex
  Mono** at 30px regular, tabular. This is the one place where the
  callout value reads bigger than its surrounding caption - the Plex
  Mono regular at 30px holds the eye without needing 800 weight.
- **Units stay with their number.** `2.3%` not `2.3 %`. `$1.2B` not
  `$1.2 B`. `25 bps` joined with a regular space.
- **Italic is retired.** No italic deck, no italic emphasis. Where
  emphasis is needed, promote weight. The legacy `.deck` utility was
  italic serif in v0.x; it is now ExtraLight sans (200).
- **All caps is reserved for eyebrow labels** (`KICKER`, `SECTION`,
  `AS OF`, `LATEST RELEASE`, `PLATE`, `SOURCE`, `FIGURE`) at `micro` or
  `label` size with `0.18em - 0.22em` tracking. Never for headlines.
  Never for body.
- **Line length: 60-68 characters for body prose, 22-32 characters for
  headlines.** Enforced via `max-width` on text columns and headline
  elements - not via per-element widths. The section headline question
  is constrained to ~22ch so it breaks editorially.

---

## 3. Color palette

**One serious neutral system (pure white + pure black), one signal red
accent. Light mode only in v1.**

### Light mode only - justification

Dark mode doubles the design and test surface. For an editorial site whose
primary reading mode is daytime desktop, the cost is not justified at v1.
The Vignelli register is **defined** by its paper-white ground; a "dark
Vignelli" would be a different system. Revisit at v2 only if reader
analytics show meaningful evening reading.

### Neutrals - the page

| Token          | Hex       | Role                                                  |
|----------------|-----------|-------------------------------------------------------|
| `--paper`      | `#FFFFFF` | Page background. Pure white. The Vignelli ground.     |
| `--surface`    | `#FFFFFF` | Cards, chart canvases. Identical to paper - we are not layering surfaces; everything sits on paper. |
| `--surface-sunk` | `#FFFFFF` | Reserved for legacy components; resolves to paper.   |
| `--ink`        | `#000000` | Primary text. Pure black, **not warm-black**. Mueller-Brockmann would be appalled by a near-black on a paper-white system. |
| `--ink-muted`  | `#000000` | Aliased to ink. The Vignelli canon does not soften ink; if a thing should be quieter, drop its weight (200) instead of its hue. |
| `--ink-faint`  | `#000000` | Aliased to ink. Where a true faint chrome rendering is needed (e.g. the pipe separator between nav labels), compose **opacity** (e.g. `opacity: 0.32`) onto the pure-black token at the call site. |
| `--rule`       | `#000000` | Rule lines, table borders, panel edges. 1px hairlines in pure black.  |
| `--rule-faint` | `#000000` | Aliased to rule. There is no "faint rule" in the Vignelli register; if a rule should be quieter, it should not exist.  |

**Why pure white (`#FFFFFF`):** the Vignelli register **is** the paper-white
register. Any warmth in the page color (cream, off-white, ivory) instantly
breaks the system. The page reads as a Swiss specification, not as a print
broadsheet.

**Why pure black (`#000000`):** weight contrast carries the entire
hierarchy; we cannot afford to soften ink with a warm-black hex, because
then a 200 ExtraLight at 12px against a near-black background loses
legibility on a low-contrast display. Pure black at every weight remains
legible. The reader's eye does the softening, by tracking weight.

**The `--ink-faint` opacity-composition pattern.** In a few places the
visual chrome genuinely benefits from a tinted gray: the pipe separator
between masthead nav labels, the eyebrow separator pipe in section
headers, the cap rule between an indicator and a value in a callout
row. The pattern is: **use the `--ink-faint` token (which resolves to
pure black) and apply CSS `opacity` at the call site** to soften it -
typically `0.32` for a "visible restraint" chrome and `0.5` for a
subtler hint. This pattern keeps the token surface monochrome (so a
future token revision can give `--ink-faint` a real tinted value without
code change) while letting individual chrome elements be quieter.

**Decision flagged:** the all-pure-black token surface forces every
"placeholder" or "muted" rendering to hand-code a mid-gray (e.g. the
`#8A8A8A` hard-coded in `SectionPanel.astro` `.vig-panel__placeholder`).
We have considered reifying a proper mid-gray token (e.g. `--ink-gray:
#8A8A8A`) but elected to keep the all-black token surface as the
discipline and let placeholder ink be a hard-coded escape hatch. See
"Decisions flagged" at the end of this document.

### Accent - signal red

| Token            | Hex       | Role                                                           |
|------------------|-----------|----------------------------------------------------------------|
| `--accent`       | `#E63946` | Signal red (MTA red, Vignelli). Brand-signal moments only.      |
| `--accent-soft`  | `#FAD4D7` | Reserved for legacy compositions; not used on the production homepage. |

**MTA red (#E63946):** Vignelli's red for the 1972 NYC Subway Diagram is
the canonical reference. We use a slightly warmer rendering tuned for
sRGB screens, but it sits within the same family. One accent color, used
**only on brand-signal moments**:

- **The latest-print dot on a chart.** A 3px filled circle in `--accent`
  marks "where we are now" on the homepage panel mini-charts. This is
  the **single use of `--accent` on data**, and it is decorative
  signage rather than data encoding - the dot's *position* is the data;
  the dot's *color* says "this is the latest, brand-signed point."
- **The figure number in a panel eyebrow.** `FIGURE 1.` - the
  numeral `1.` renders in `--accent` 800 weight; the word "Figure"
  renders in pure ink 600 weight. The contrast says "this is the figure
  we are talking about" - a brand stamp.
- **The plate number in a chartbook unit eyebrow.** `PLATE 01` - the
  `01` renders in `--accent`; the word "Plate" in pure ink. Same logic
  as the figure number.
- **The section number in a section page header kicker.** In `SECTION
  3 OF 7`, the `3` renders in `--accent` 800; the rest is pure ink 600.
- **Focus rings on keyboard navigation.** `outline: 2px solid
  var(--accent)` with `outline-offset: 3px`. The signal red is the
  publication's accessibility tell - keyboard users see the brand color
  the moment focus lands.
- **Link hover.** Link text and underline transition to `--accent` on
  hover. 100ms ease-out. The publication's voice gently surfaces on
  reader intent.
- **Selection highlight.** `::selection { background-color: var(--accent);
  color: var(--paper); }`. The brand red marks what the reader has
  chosen.
- **Key kicker stamps and one-token accents** in research-note eyebrows
  (e.g. the word `INDEPENDENT` in `RESEARCH NOTE | CANADIAN MACRO |
  INDEPENDENT` renders in accent red to surface the publication's
  editorial stance).
- **The colophon / publication-mark closing rule.** A single 2px MTA red
  hairline sits directly above the publication mark in the site footer
  (`VignelliColophon.astro` `.vig-col__rule--signal`). Functions as the
  brand-signal kicker for the colophon - the last red moment a reader
  meets on the page, mirroring the plate-number / figure-number stamp at
  the top. Threads the brand across the full scroll. This is the only
  rule on the site (other than the latest-point dot, the focus ring, and
  the selection highlight) that is permitted to be red; ordinary table
  rules, plot frames, section dividers, and masthead hairlines remain
  pure ink. See Section 3.6.

**Never used on data direction.** Pos/neg encoding is glyph-driven (see
Section 4). A chart line is **never** red unless the chart is making a
brand-signal statement (and the only chart we currently do that on is the
latest-point dot, which is a 3px ornament, not a data stroke).

**Never used adjacently to itself.** If two accent-red moments would
collide visually (e.g. a figure number eyebrow next to a focus ring on
a link), one of them retreats to pure ink for that surface.

### Semantic / data tokens (retained, retired for direction)

| Token            | Hex (resolved) | Role                                              |
|------------------|----------------|---------------------------------------------------|
| `--pos`          | `#000000`      | Aliased to ink. **Retired for direction encoding.** |
| `--pos-soft`     | `#FFFFFF`      | Aliased to paper. Retired.                          |
| `--neg`          | `#000000`      | Aliased to ink. **Retired for direction encoding.** |
| `--neg-soft`     | `#FFFFFF`      | Aliased to paper. Retired.                          |
| `--neutral`      | `#000000`      | Aliased to ink.                                     |
| `--neutral-soft` | `#FFFFFF`      | Aliased to paper.                                   |

**The Vignelli direction rule:** direction is encoded by **glyph** -
`U+25B2` (up-pointing triangle) for positive, `U+25BC` (down-pointing
triangle) for negative, `U+2014` (em dash) for neutral / unchanged. The
glyph renders in **pure ink (`#000000`)** at all times. The hue red /
green / amber traffic-light convention is retired across the system.

The `--pos` / `--neg` tokens remain defined (resolving to ink and paper)
for two narrow reasons:
1. Legacy components that still reference them fall back cleanly.
2. A future need for true semantic color (e.g. error states in a form,
   not data direction) can rehydrate these tokens without code-rewrite.

We **do not** use `--pos` / `--neg` on data marks for direction. Ever.

### Categorical chart series (retained for multi-series charts)

The categorical palette below is retained for future multi-series section-
page charts (Phase 2 work). On the homepage and the current section
chartbook units, charts are **single series**, drawn in `--ink` (pure
black) with an `--accent` latest-point dot. Multi-series charts that
need to distinguish two or more lines consume the palette below; in
practice the first two are the workhorse pair.

| Token         | Hex       | Notes                                            |
|---------------|-----------|--------------------------------------------------|
| `--series-1`  | `#1F4E79` | Deep blue. First series.                         |
| `--series-2`  | `#C9772A` | Burnt orange. Second series.                     |
| `--series-3`  | `#5B7553` | Sage green. Tertiary.                            |
| `--series-4`  | `#7A3E65` | Plum. Quaternary.                                |
| `--series-5`  | `#3F7D7C` | Teal.                                            |
| `--series-6`  | `#8A6A2C` | Olive gold.                                      |
| `--series-7`  | `#4A4F57` | Slate. "Other" / "Canada average" / context line. |

**Default series color on a single-series chart in the Vignelli register
is `--ink` (#000000)**, not `--series-1`. The categorical palette is for
multi-series charts where the eye needs to distinguish; single-series
charts read better as black-on-white. **Latest-point dot is always
`--accent` (#E63946), regardless of line color.**

### Section accents (retained, off the homepage)

Each section has a categorical token assigned for Phase 2 section-page
wayfinding (e.g. a section's plate eyebrow may pick up its own hue, or
a multi-series section chart may consume its assigned token for the
primary series). **The homepage panel grid does NOT consume these on
chrome** - Vignelli is one accent (signal red) only on the homepage.

| Section   | Token                          | Resolves to            |
|-----------|--------------------------------|------------------------|
| GDP       | `--section-accent-gdp`         | `--series-1` deep blue |
| Inflation | `--section-accent-inflation`   | `--accent` signal red  |
| Labour    | `--section-accent-labour`      | `--series-3` sage      |
| Housing   | `--section-accent-housing`     | `--series-2` orange    |
| Policy    | `--section-accent-policy`      | `--series-4` plum      |
| Markets   | `--section-accent-markets`     | `--series-5` teal      |
| Trade     | `--section-accent-trade`       | `--series-6` olive     |

### Recession / event shading

- **Recession bands:** ink at 6% opacity, rendered as
  `rgba(21, 23, 26, 0.06)` (the legacy near-black hex chosen for its
  visual quietness at 6% - using pure-black at 6% reads slightly heavier
  in practice). Sits behind gridlines and behind data. Reads as a tint,
  never as a block.
- **Recession labels:** at chartbook scale, labeled at top of band in
  `micro` size pure ink 600 weight, e.g. `Recession (2008Q4-2009Q2)`.
  Only label the most recent or most relevant recession in any chart.
  At mini-chart scale (panel grid), no label - the tint reads as
  context for the pattern-matching reader.
- **Event lines:** 1px solid pure ink, dashed `4 2`, with a `micro`
  label sitting above the plot area. Reserved for editorial moments
  (e.g. a rate decision, a release date).

### 3.5 Placeholder ink treatment

**The canon for any rendered string that is NOT real data: "TK",
"Coming soon", "[ NOT WIRED ]", "DATA NOT YET WIRED", lorem-ipsum
stamps, empty editorial slots.**

Before this section existed, five production components each
hard-coded their own mid-gray (`#8A8A8A` in `SectionPanel.astro`,
`TitleStatement.astro`, `DeepDivePanel.astro`, `VignelliColophon.astro`,
and `PanelEmpty.astro`), or composed opacity onto `--ink-faint`. The
result was that placeholder ink read consistently to a reader but was
unauditable in code: a grep for `#8A8A8A` found some uses, a grep for
`opacity` found others, and the QA sweep on 2026-05-11 found a sixth
component (`DeepDivePanel`'s "Coming soon" stamp) that had silently
dropped to pure ink because its `--tk` class rule was never written.
This section closes the gap.

**The token.** Placeholder ink is a real token:

```
--ink-placeholder: #8A8A8A;
```

Defined in `src/styles/tokens.css` alongside the other neutrals. The
hex `#8A8A8A` is the mid-gray that balances against pure ink on a
paper-white ground without competing with weight contrast for the
reader's eye - lighter and the placeholder dissolves into the page;
darker and it reads as real text dimmed. We do NOT compose opacity on
`--ink-faint` for placeholder copy; opacity-composition is reserved
for chrome (the masthead nav pipes, the eyebrow separators) where the
goal is "visible restraint." Placeholder copy is a different
information class - it says "this is a slot waiting for data" - and
deserves its own token.

**The application rules.** Any rendered placeholder string uses
`color: var(--ink-placeholder)`. Two typographic treatments, one per
slot kind:

- **Date / value / stamp slot** (e.g. an `AS OF` body, a callout
  value, a latest-release stamp, a deep-dive published date):
  Plex Mono at the slot's normal size, weight 400, micro-caps
  treatment if the surrounding stamp uses one (`text-transform:
  uppercase`, `letter-spacing: 0.14em`). Canonical literal:
  `[ NOT WIRED ]`. The brackets are part of the stamp; they read as a
  typeset placeholder, not as a bug.
- **Sentence slot** (e.g. a homepage abstract lede, a plate
  interpretation paragraph, a deep-dive teaser dek): Manrope at the
  slot's normal size, weight 200 (ExtraLight). The ExtraLight weight
  substitutes for the italic the Vignelli register forbids and signals
  "this is placeholder prose," matching the existing lorem-ipsum
  treatment on the homepage abstract.

The mid-gray + weight-200 / mono-400 combination is the only treatment
permitted for placeholder copy. No opacity stacking, no second gray,
no near-black-at-50%-opacity. One token, two slot kinds.

**The detection gate.** Placeholder detection happens at the data
boundary, not at the consuming component. The single gate is
`enrichPrint` in `src/data/site_data_loader.ts`: any incoming string
equal to:

- `"TK"` (the journalism convention; the pipeline emits this for
  not-yet-wired values),
- any `PLACEHOLDER.*` constant from `site_data_loader.ts` itself
  (`PLACEHOLDER.value`, `PLACEHOLDER.notWired`,
  `PLACEHOLDER.nextReleaseNotWired`, `PLACEHOLDER.statusPending`),
- or an empty string (`""`),

is coerced to `null` at the enrichment step. The component then
receives `null` for the field and renders the canonical placeholder
stamp (`[ NOT WIRED ]` or `Coming soon`, per slot kind) in
`--ink-placeholder`.

**Components MUST NOT pattern-match placeholder strings themselves.**
The component layer renders `value` as data when it is a string and as
a placeholder when it is `null`. Period. If a component finds itself
checking `value === "TK"`, the bug is in the loader, not in the
component - the gate has leaked. The 2026-05-11 QA found exactly this
pattern across `ChartbookUnit`, `SectionPanel`, and the seven
`src/pages/{slug}.astro` plate definitions; the fix is to tighten the
gate, not to teach more components about "TK."

**Canonical class.** Components consume a single shared class:

```
.placeholder-tk {
  color: var(--ink-placeholder);
  font-family: var(--font-mono);
  font-weight: 400;
  letter-spacing: 0.14em;
  text-transform: uppercase;
}

.placeholder-prose {
  color: var(--ink-placeholder);
  font-weight: 200;
}
```

`.placeholder-tk` for date / value / stamp slots; `.placeholder-prose`
for sentence-length slots. Both live in `src/styles/base.css` (or the
equivalent global stylesheet) - NOT re-declared per component.

**Migration path.** The five components currently shipping their own
`#8A8A8A` literal (listed above) migrate to the shared class. The
`DeepDivePanel` `.vig-dd__stamp-body--tk` rule that was missing
entirely gets the same shared class. New components use
`var(--ink-placeholder)` directly or consume `.placeholder-tk` /
`.placeholder-prose`; they do NOT hard-code `#8A8A8A`.

### 3.6 The ninth permitted MTA red moment - colophon / publication-mark rule

The bulleted list earlier in this Section 3 ("Accent - signal red")
enumerates the brand-signal moments permitted to render in MTA red.
The 2026-05-11 QA flagged a ninth use: `VignelliColophon.astro`
ships a 2px MTA red rule directly above the publication mark
(`.vig-col__rule--signal`), which is not in the original eight-moment
list. Decision: **keep, canonize.**

**Rationale.** The colophon rule is functionally a section-close
brand-signal moment. It mirrors the plate-number stamp at the top of
a section page (a red numeral against ink) by giving the page a red
closing gesture against ink - one accent at the start of the page,
one accent at the end, ink in between. The single red threaded across
the full scroll is a Vignelli discipline (the NYC Subway Diagram does
exactly this: one red moment per geographic region of the map). Drop
the rule and the page ends in pure ink only, which reads as a missing
gesture once the eye has registered the red stamps at the top.

**Constraints on this use.**

- **One rule per page.** The colophon rule is the page's terminal red
  moment; no second red rule may appear elsewhere on the page (e.g. a
  red divider between sections, a red underline on a heading). This
  is identical to the discipline on every other red moment: one of
  each kind per surface.
- **2px stroke, not 1px.** The colophon rule is the only
  intentionally-heavier-than-hairline ink moment on the site (the
  closing 2px black rule under a section's plate index is the only
  other 2px ink moment, per `chartbook-template.md`). The 2px weight
  reads as "section close" rather than "table divider." The colophon
  rule consumes the same 2px weight in red.
- **Position.** Directly above the publication mark in the site
  footer. Not at the top of the footer, not between footer columns -
  immediately preceding the publication signature, so the eye reads
  `[red rule][publication mark]` as one closing kicker pair.
- **No other footer red.** The footer's nav links, copyright stamp,
  next-release stamp, and source roll all render in pure ink. The
  rule is the only red moment in the footer.

**The complete permitted set is therefore nine moments:** latest-print
dot, figure-number numeral, plate-number numeral, section-number
kicker, focus ring, link hover, selection highlight, brand-kicker
tokens (`INDEPENDENT`, `PROUDLY CANADIAN`), and the colophon /
publication-mark closing rule. Every other red use is a violation
and should be flagged in QA.

### 3.7 The tenth permitted MTA red moment - Sleeping Giant mark foot-dot

The 2026-05-11 brand-mark dispatch canonizes a tenth permitted MTA
red moment: **the single MTA red filled circle at the foot terminus
of the Sleeping Giant brand mark** (`SleepingGiantMark.astro`,
`SleepingGiantFavicon.astro`). One dot per mark instance, at the
rightmost end of the silhouette's continuous-line path.

**Rationale.** The Sleeping Giant mark is the publication's
geographic identity element - it appears in the masthead, the OG
social card, the favicon, and the 404 hero. The foot-dot is
functionally the same brand-signal moment as a chart's latest-print
dot: a single MTA red filled circle at the rightmost terminus of a
pure-ink line. The mirror is intentional. Every visual element on
the site ends with one red moment at the right:

- A chart line ends with the MTA red latest-print dot at the
  rightmost data point (Section 5.3, canon-reference Rule 2).
- A page ends with the 2px MTA red rule above the colophon (Section
  3.6).
- The brand mark ends with the MTA red dot at the foot terminus.

The discipline of one terminal red per object is the publication's
visual signature - the Vignelli "one accent threaded through" applied
across charts, page chrome, AND the brand layer.

**Constraints on this use.**

- **One dot per mark.** Each rendered instance of the Sleeping Giant
  mark carries exactly one red dot, at the rightmost path terminus.
  No second dot at the head, no dot at the chest, no auxiliary marks.
- **3-4px radius scale.** 3px on the inline-masthead variant (matches
  the canon-reference chart's mini-chart dot scale); 4px on the og
  variant (matches the chartbook-scale dot range, 3-5px). The favicon
  variant uses 2.5px to fit the 32 x 32 viewBox.
- **`withAccent={false}` is the documented exception.** Monochrome
  surfaces (print stationery, embossed mock-ups, SVG-mask exports)
  may suppress the dot. The default is on.
- **Position - rightmost terminus.** The dot anchors at the foot
  terminus of the silhouette path. Floating the dot anywhere else on
  the canvas - above the chest, below the foot, at the head - is a
  violation.

**The complete permitted set is therefore ten moments:** latest-print
dot, figure-number numeral, plate-number numeral, section-number
kicker, focus ring, link hover, selection highlight, brand-kicker
tokens, colophon / publication-mark closing rule, and the Sleeping
Giant mark foot-dot. Every other red use is a violation and should
be flagged in QA.

The full canon for the mark itself lives in
`design/sleeping-giant-mark.md` (placement, sizing, variants, the
SVG path data, misuse cases).

---

## 4. Direction-by-glyph rule

**The Vignelli direction rule.** Direction (positive / negative / neutral
change) is encoded by an ASCII triangle glyph in pure ink. Color does not
encode direction.

| Direction | Glyph (Unicode)  | Codepoint | Role                                         |
|-----------|------------------|-----------|----------------------------------------------|
| Positive  | up-pointing triangle (filled, `U+25B2`) | `U+25B2`   | Positive change. Higher value. Growth.       |
| Negative  | down-pointing triangle (filled, `U+25BC`) | `U+25BC`   | Negative change. Lower value. Contraction.   |
| Neutral   | em dash (`U+2014`)                       | `U+2014`   | No change. As expected. Flat.                |

**Render at default text weight in pure ink.** The glyph is part of the
typographic flow; it sits inline with the numeric delta. e.g.
`U+25B2 +0.2pp` or `U+25BC -0.1pp` or `U+2014 0.0pp`.

**Rationale.** Three problems with hue-encoded direction:

1. **Color blindness.** Red-green deuteranopia and protanopia affect ~8%
   of men; the convention is genuinely user-hostile without redundant
   encoding. Glyph encoding is fully accessible at the data layer.
2. **Brand collision.** Our brand is `--accent` (signal red). A red used
   on data direction (negative) collides semantically with red used on
   brand-signal (latest-print dot, focus ring). Either we accept the
   collision and the reader has to context-switch, or we encode
   differently. We chose the latter.
3. **Editorial register.** Hue-coded directions read as a trading
   dashboard. The Vignelli register is a research publication. A glyph
   reads as typography; typography is what a research publication does.

**Edge case:** when a directional badge is needed at small size (e.g. in
a table row), the glyph renders at the table's data weight (Plex Mono
400). It is not stylized further.

---

## 5. Chart visual rules

Three chart tiers, each a distinct object with its own discipline.
Confusing tiers is the most common failure mode.

### Tier 1 - Sparkline (~160 x 40 inline, decorative)

Production component: `src/components/Sparkline.astro`.

- **Role.** Decorative line accompanying a number elsewhere on the page.
  The sparkline supports the number; the number is the story.
- **Geometry.** Hand-rolled SVG, 160 x 40 viewBox, stretched into a
  consumer-defined aspect-ratio box.
- **Shape rules.** One series, line only (no area fill). 1.25px stroke,
  rounded line-join, vector-effect non-scaling-stroke to keep weight
  constant under non-uniform scaling.
- **Color.** Default `--ink-muted` (which resolves to pure ink). Accent
  variant available (`--accent`) for the rare case where a sparkline is
  a brand-signal moment. No section accent.
- **Last-point dot.** 3px diameter in the same color as the line.
- **No chrome.** No axes, no gridlines, no labels, no tooltips. The
  consumer renders the value to the right of the sparkline at
  `mono-sm`. No source line, no annotation.

### Tier 2 - Mini-chart (~248 x 72, single-series with light chrome)

Production component: `src/components/charts/MiniChart.astro`.

- **Role.** The chart object that lives on a homepage **panel** (Section
  6) and on small contextual surfaces. Reads "at glance" - one series,
  one shape, light chrome.
- **Geometry.** 248 x 72 viewBox, with a 32px right gutter reserved for
  the optional direct-label of the final value. Vector-effect
  non-scaling-stroke throughout.
- **Shape rules.** One series. 1.25px stroke. No area fill. Reference
  rule (1px dashed in `--rule`, which is pure ink) optional, max one,
  for a single editorial anchor (e.g. the 2% CPI target). Recession
  band optional, ink at 6% opacity. Last-point dot 3px in series color.
- **Color tier.** Two tiers:
  - `data-first` -> `--series-1` (deep blue). Used when the line's
    shape is itself the story.
  - `ambient` -> `--ink-muted` (pure ink). Used when the latest number
    leads and the line is context.
  - **Production note:** on the current homepage panel grid
    (`SectionPanel.astro`), the primary chart renders in pure
    black with an `--accent` (signal red) latest-point dot, overriding
    the abstract MiniChart color tiers. The Vignelli register prefers
    black-line / red-dot on the homepage; the MiniChart's blue and
    slate tiers remain available for non-homepage uses.
- **Chrome.** 1px x-axis rule along the bottom of the plot area in
  pure ink. No tick marks, no x-axis date labels (the consumer surface
  carries the date stamp in its eyebrow). No y-axis line, no y-axis
  tick labels EXCEPT the optional direct-label of the final value to
  the right of the last-point dot.
- **What it does NOT have.** No title, no deck, no annotations, no
  leader lines, no legend, no hover tooltip, no source line. Those
  live on the parent surface.

### Tier 3 - Full chart (chartbook scale)

Production components: `src/components/charts/inflation/Panel*.astro`,
`src/components/charts/gdp/Panel*.astro`,
`src/components/charts/labour/Panel*.astro`,
`src/components/charts/housing/Panel*.astro`,
`src/components/charts/policy/Panel*.astro`,
`src/components/charts/markets/Panel*.astro`,
`src/components/charts/trade/Panel*.astro`.

- **Role.** The chart object that carries an editorial argument. Lives
  inside a `ChartbookUnit` (Section 6) on a section page.
- **Geometry.** viewBox `720 x 405` (16:9). **All non-sparkline charts
  share these dimensions, with no exceptions** (categorical / snapshot /
  dumbbell / composite — same canvas). Wrapper element carries
  `aspect-ratio: 16 / 9`. The 720-unit width is the chartbook column;
  the 405-unit height locks every section page into a single rhythm.
  Internal sub-canvas heights (composite charts) and row spacing
  (categorical / dumbbell) are tightened to fit the canon canvas
  rather than allowed to grow their own viewBox. See
  `design/canon_reference_panel.md` Q3 for the override rationale.
- **Shape rules.** Single series by default; multi-series permitted
  when the editorial point requires it (e.g. CPI headline + 3M
  annualized). Line in pure ink at 1.5px stroke; secondary series in
  `--ink` at 1px (or in `--accent` if the section has an editorial
  color, with explicit art-director approval). No area fills except
  the diverging zero-band treatment for series that cross zero (e.g.
  trade balance) - and even that is monochrome (a 6% ink wash on the
  negative side, no positive fill).
- **Color rule.** **One color on data per chart, plus a latest-point
  dot.** The default is: pure ink line + `--accent` latest-point dot.
  Multi-series exceptions: the secondary series uses 1px ink with a
  dashed pattern to recede, not a second color. Section-page wayfinding
  is carried by the section accent in the eyebrow only (Phase 2).
- **Chrome.**
  - Hairline 1px black plot frame (a rectangle around the plot area).
  - 3-4 horizontal gridlines in pure ink at low opacity (compose via
    `stroke-opacity` or `opacity` at the call site - the canonical
    treatment is 1px black at 100% for axis-anchor lines and 0.5px or
    1px with stroke-opacity 0.2 for gridlines; chart-builder hand-tunes
    per panel).
  - Y-axis tick labels right-aligned in left gutter, Manrope 400 at
    `micro` size, pure ink. Topmost tick carries the unit (e.g. `4%`).
  - X-axis tick labels below the plot area, Manrope 400 at `micro`
    size, pure ink, 3-5 ticks max.
  - Latest-point marker: 3-5px filled circle in `--accent`. The
    publication's brand stamp on the latest print.
  - Direct labels at series terminus, Manrope 600 at `label` size, in
    pure ink. Replaces legends.
- **Annotations.**
  - **Typography.** Manrope at `body-sm` (15px), weight 400 normally,
    weight 600 for the inline "anchor word." Color pure ink.
  - **Leader lines.** 1px pure ink, no arrowhead. Straight or single-
    elbow. End 4px short of the data point.
  - **Placement.** Hand-tuned. Annotations sit in white space, never
    over data. If white space is unavailable, the chart needs more
    margin.
  - **Length: words, not sentences.** Canvas annotations are limited
    to a word or two — labels for periods, marks, or thresholds.
    "Pandemic", "Pre-pandemic average", "Forecast", "BoC target",
    "Latest". **NEVER full sentences, never sub-clauses, never
    narrated implications.** If an annotation has a verb, it's a
    sentence — cut it. Explanations of what the geometry shows belong
    in the chart blurb, not on the canvas. The picture tells the
    story; the canvas does not narrate it. (User-codified 2026-05-12
    after Plate 2 wage chart shipped a two-line sentence annotation
    duplicating the headline.) Exception: deep-dive hero charts that
    anchor a piece can carry one editorial callout — even there,
    prefer phrases over sentences.
  - **Wording.** Owned by `writer`. Visual treatment owned here.
- **Hover.** A native SVG `<title>` element on each data point gives
  date + value in the browser's default tooltip. No custom hover
  tooltip, no crosshair, no animated reveal. Zero client JS.
- **Label placement: no-overlap canon.** A Tier-3 panel can render up
  to six families of label (primary direct, secondary direct, y-tick,
  x-tick, recession-band, reference-rule). The legal placements,
  collision pixel-thresholds, and suppression hierarchy are specified
  in `design/canon_reference_panel.md` Section "Label placement rules
  (no-overlap canon)." Implemented in
  `src/components/charts/_shared/PanelLiveChart.astro`. Headline rule:
  no two labels overlap; the suppression hierarchy is unit-tick >
  primary direct > recession label > secondary direct > reference-rule
  label > non-unit y-tick > annotation callout.

### Hero chart - deprecated

The "homepage hero chart" concept is **retired in v1.0**. The Vignelli
homepage uses a panel grid: each of the 7 sections renders as a
`SectionPanel` with a tier-2 mini-chart embedded. There is no
single-chart hero. `HeroChart.astro` survives in the codebase as a
mini-chart variant; new work should consume `MiniChart.astro` or build
a section-specific panel chart.

### Axis treatment summary

Across all tiers:
- **Pure ink** for axis lines and tick marks (no warm grays).
- **Tick marks 3-4px outward,** never inward.
- **Y-axis line:** omitted (gridlines do the work) except where the plot
  has a hairline frame - then the frame's left edge is the y-axis.
- **X-axis line:** 1px pure ink along the bottom of the plot.
- **Zero line:** when the data crosses zero, draw the zero line in 1px
  pure ink at 100% opacity, slightly heavier than gridlines.
- **Axis titles:** almost never. Unit goes on the topmost y-tick. If a
  title is needed to understand the chart, the chart title is failing.

### Gridline treatment

- **Horizontal only.** Vertical gridlines never (exception: small
  multiples with shared x-axis time anchor).
- **Color: pure ink at low opacity** (compose `stroke-opacity: 0.15` to
  `0.20` at the call site). The token surface stays monochrome; opacity
  carries the quietness.
- **Density: 3-5 gridlines.** More reads as noise.
- **Zero line is heavier than gridlines** (full opacity).

### Small multiples

When a story needs multiples, the chartbook unit renders a 2-up, 3-up,
or grid layout. **Two modes exist — pick the right one for the data,
and always tick every panel that has its own scale.**

**Mode A — peer comparison (shared y-axis).** Use when the panels carry
comparable magnitudes that the reader is meant to read against each
other. Examples: CPI headline / core trim / core median; provincial
unemployment rates; per-CMA HPI Y/Y. Every panel scales identically so
eye-comparison is honest.
- Identical y-axis range (forced).
- Identical x-axis range (forced).
- Y-tick labels appear in the **leftmost column only**; other columns
  read off the shared scale.
- Topmost tick of the leftmost column's top cell carries the unit.

**Mode B — component decomposition (per-panel y-axis).** Use when the
panels carry **disparate magnitudes** (e.g. balance-sheet components
where one is $220bn and another is $0; aggregate vs.\ thin sub-series)
and shared scaling would flatten the smaller series into invisibility.
Each panel reads on its own scale.
- Per-panel y-axis range, fitted to that panel's data.
- Identical x-axis range (forced) — time anchor stays shared.
- **Every panel gets its own y-tick labels.** Reader cannot infer the
  scale by transitive lookup; without per-panel ticks the smaller
  panels become unreadable. This is the non-negotiable for Mode B.
- Unit suffix on the topmost tick of the leftmost-column cells only
  (since units are uniform); other panels' topmost ticks are numbers
  alone.
- Column gap must be wide enough (~36-40px in a 720-wide viewBox) to
  fit the per-panel y-tick labels in the gutter between cells.

**When in doubt, ask: would the reader compare values across panels by
eye?** If yes (CPI 2.1% vs 2.4%): Mode A. If no, because the values
live on different scales (Total assets $219bn vs Advances $0bn):
Mode B.

**Shared across both modes:**
- A 1px ink hairline separates the panels.
- Each panel's title in `label` size, pure ink, 600 weight, sits above.
- One source line at the bottom of the whole grid, not per panel.

### Aggregate-vs-component overlay

When a chart shows BOTH a big-picture aggregate AND the components
that add up to it — Canada's unemployment rate alongside each
province; the national MLS HPI alongside individual CMAs; total GDP
alongside its industry breakdown; total CPI alongside sub-aggregates
— the question is which line is the star and which is the supporting
cast.

**Convention: the component is the protagonist, the aggregate is the
reference.** Reasoning: when someone is looking at the BC panel, they
are not there to find out what Canada's number is — they are there to
see where BC sits relative to it. The aggregate's role is context,
not signal.

Treatment within each panel:

- **Component** (province, CMA, industry, sub-aggregate): 1.5px solid
  ink line. Latest data point in MTA red — the protagonist's terminal
  accent.
- **Aggregate** (Canada, national, total): 1px dashed ink line at
  55-60% opacity. **No red dot at the terminus.** The faint dashed
  treatment immediately tells the eye "this is just context; pay
  attention to the solid line."

Opacity at 55-60% rather than 50% because at quarter-panel size in a
4-up grid (the recurring small-multiples case), 50% fades into the
gridlines and the reference disappears.

This rule applies inside small multiples (where it composes cleanly
with the small-multiples grid) AND inside single-panel aggregate-vs-
component charts (e.g. a national rate with its largest two CMAs
overlaid).

Live exemplars where this rule applies:
- Labour P5 — provincial unemployment small multiples, Canada as
  dashed reference (the convention's anchor case).
- Housing P1 — MLS HPI national + six CMAs, when reworked.
- Output P3 — services vs goods Y/Y (each side is its own
  component; no separate aggregate, so the rule doesn't apply here).

The rule does NOT apply when both series are peers of equal editorial
weight (e.g. core-trim and core-median — both are core measures, no
hierarchy). In that case use the canonical primary / secondary
treatment from `PanelLiveChart`.

### Methodology discipline (derived-rate / decomposition / indexed charts)

Charts that compute anything beyond a direct pull of a published series
— a derived rate, a decomposition, an indexed series, a smoothed
measure — carry methodology risk. The chart-builder citing a formula
from memory and shipping is the failure mode the user has caught
repeatedly: the formula may not match the cited source, or it may
match the source but not the labelled quantity. Either way the
sophisticated reader checks and loses trust.

Hard rule: every such chart ships with a methodology note that
includes, in this order:

1. **The conceptual definition** — one plain-English sentence
   naming what the chart computes. "Probability that an unemployed
   person exits unemployment within the month." Not symbols. Not
   formulas. The concept first.

2. **The formula in plain variable names** — never math symbols in
   the reader-facing note. "1 minus (long-duration unemployed next
   month ÷ unemployed this month)." Not "1 − u^l_{t+1} / u_t". The
   user reads the formula to check that the chart computes what they
   think it does; symbols slow that check.

3. **The source** — the paper, table, methodology page, or canonical
   reference the formula derives from. Cite it directly. If the
   chart-builder synthesised from multiple sources, name them.

4. **Any simplification vs the source's canonical method**, named
   explicitly. Closed-form approximation vs numerical solve.
   Discrete probabilities vs continuous-time hazards. Stocks-only
   vs microdata-derived flows. If the simplification biases the
   result, name the direction of the bias.

The methodology note belongs at minimum in the chart's source line.
For methodology-heavy plates (flow decompositions, deflated ratios,
contribution decompositions), the note also belongs on a public
methodology page that the source line links to.

The verification step that produces the note is part of authoring,
not part of post-review. Chart-builder agent file (`.claude/agents/
chart-builder.md`) carries the operational discipline under
"Methodology verification."

User-codified 2026-05-13 after a Shimer-style separation/finding
rate decomposition shipped with formulas the chart-builder cited
from memory; the user independently replicated the math in Excel
from raw StatCan data and the numbers matched, but the round trip
took multiple turns because verification happened at review rather
than at authoring.

### Hand-tuning approach

The Vignelli register is anti-template. **Every chart is hand-tuned by
chart-builder against an art-director per-chart visual spec.** Generic
chart components are forbidden; each panel is its own Astro component
with its own SVG geometry and its own annotation hand-placement. The
target is the Knoll catalogue plate, not the Tableau dashboard.

---

## 6. Component visual language

### 6.1 Index-tile / homepage panel

Production component: `src/components/home/SectionPanel.astro`.

The homepage renders 7 panels in a 2- or 3-column grid (one per
section). Each panel is a self-contained piece of evidence: a figure
number, an indicator name, a headline question, a mini-chart, a callout
readout, and a 4-row indicators table.

**Anatomy (top to bottom):**

```
+-------------- panel (paper, no fill, no border)  --------------+
| FIGURE 1.                                  Monthly           |
| Inflation                                                    |
| ----------------------------------------------------------    |  <- 1px black
| Question paragraph (200 weight, 14px, max 56ch).             |
|                                                              |
| [ Chart (320 x 110 inline SVG, 1px black plot frame,         |  Headline indicator name (10px micro-caps)
|   pure-black line, 3px MTA red latest-point dot,             |  Latest value (Plex Mono 30px regular)
|   3 mono y-ticks, EARLIEST / asOf x-axis stamps) ]           |  Delta with U+25B2/U+25BC glyph + as-of stamp
|                                                              |
| Fig. 1. Indicator name, recent history. Last obs marked.     |
|                                                              |
| ----------------------------------------------------------    |  <- 1px black
| INDICATOR             VALUE     CHANGE       AS OF           |
| ----------------------------------------------------------    |
| Indicator 1           2.3%     U+25B2 +0.1   Apr 2026         |
| Indicator 2           ...                                    |
| Indicator 3           ...                                    |
| Indicator 4           ...                                    |
+--------------------------------------------------------------+
```

**Discipline.**
- **Panel background:** `--paper` (pure white). No fill, no card pillow.
- **Panel frame:** none. Rules between sections of the panel carry the
  structure. Adjacent panels are separated by the parent grid gap, not
  by panel borders.
- **Figure eyebrow:** `FIGURE` in micro-caps 600 ink + numeral in 800
  `--accent` (signal red). The figure number is a brand stamp.
- **Section heading:** Manrope 800 at 22px, pure ink, line-height 1.05,
  underline on hover (border-bottom, not text-decoration).
- **Headline question:** Manrope 200 (ExtraLight) at 14px, pure ink,
  max-width 56ch. The Vignelli weight-contrast moment: the 200 question
  against the 800 heading above.
- **Chart:** 320 x 110 viewBox, 1px black plot frame, pure-black 1.5px
  line, 3-tick y-axis (Plex Mono 8px), x-axis EARLIEST / asOf stamps in
  Manrope 600 micro-caps. 3px MTA red latest-point dot (the only
  non-ink color in the panel chrome).
- **Readout (right column of the body, on md+):**
  - Indicator label: 10px micro-caps 600.
  - Value: Plex Mono 30px regular (the "data is a measurement" moment).
  - Delta row: glyph + Plex Mono value + as-of stamp in 10px micro-caps
    on the right. Glyph in pure ink, regardless of direction.
- **Indicators table:** 4 rows, 1px black hairlines between rows.
  Header row in 9.5px micro-caps 600. Data rows in Plex Mono regular
  for values and deltas. The primary row's indicator name gets 800
  weight; its value stays Plex Mono regular (weight contrast is at the
  name, not the value).

### 6.2 Chartbook unit

Production component: `src/components/section/ChartbookUnit.astro`.

Used on every section page. One unit = one indicator. See
`design/chartbook-template.md` for the full anatomy and per-section
adaptations.

### 6.3 Section page header

Production component: `src/components/section/SectionPageHeader.astro`.

Used at the top of every section page below the masthead. See
`design/chartbook-template.md` for the full spec.

### 6.4 Site masthead

Production component: `src/components/home/VignelliMasthead.astro`.

- **Wordmark:** Manrope 900 Black at 16px, uppercase, `0.16em` tracking.
  Left of a flex row.
- **Primary nav:** 7 section labels, micro-caps 600 at 11px, `0.12em`
  tracking, pipe separators in `--ink-faint` at `opacity: 0.32`. Active
  section underlined via border-bottom.
- **Closing rule:** 1px pure black hairline.

### 6.5 Data tables

- **Header row:** 9.5-10px micro-caps 600 in pure ink, `0.16em` to
  `0.22em` tracking. 1px black bottom rule.
- **Data rows:** Manrope 400 for text columns, Plex Mono 400 for
  numeric columns. 1px black rule between rows.
- **No zebra striping.** Period.
- **Numeric columns right-aligned, tabular nums** (`font-variant-
  numeric: tabular-nums`).
- **Primary row** (the indicator that drives the panel's headline)
  gets its indicator-name cell in 800 weight; its value cell stays
  Plex Mono 400. Hierarchy through weight at the name, not at the data.
- **Sort indicator (when needed):** ASCII glyph (`U+25B2` / `U+25BC`)
  in pure ink at the column header, never a colored icon.

### 6.6 Callouts - deprecated

The legacy `Callout.astro` (background `--surface-sunk`, 4px left rule
in accent) is **dropped from the canon.** The Vignelli register does
not use background-filled callouts. Where a callout is needed, the
equivalent is: a weight-contrast paragraph (Manrope 800 emphasis word
inside a Manrope 400 sentence), or a discrete `body-sm` paragraph
preceded by a 1px hairline rule. The component remains in the codebase
for legacy pages but new work does not use it.

### 6.7 Citations and source lines

- **Source line under a chart:** Plex Mono 11px regular for the citation
  body, preceded by a Manrope 10px micro-caps 600 `SOURCE:` prefix with
  `0.18em` tracking. Pure ink throughout.
- **Inline citation marker:** superscript Plex Mono digit in pure ink,
  no brackets. The marker is a typographic event, not an icon.
- **Footnote block at page bottom:**
  - Heading: `SOURCES` or `NOTES` in micro-caps 600.
  - Items: Plex Mono 12px for the digit, Manrope 15px for the text,
    hanging indent.

### 6.8 Latest-release stamp

Used in section page headers and any "this data is current as of" moment.
Two parts:
- **Label:** `LATEST RELEASE` in Manrope 10px micro-caps 600, `0.22em`
  tracking, pure ink.
- **Body:** `April CPI, released May 14, 2026` in Plex Mono 12px regular,
  pure ink. Tabular nums.

### 6.9 Buttons

- **Primary:** `--ink` background, `--paper` text, no border-radius
  (`--radius-card: 0`), padding `s-3 s-5`. Hover: background transitions
  to `--accent`.
- **Secondary:** transparent background, 1px `--ink` border, ink text.
  Hover: background `--ink`, text `--paper`.
- **Tertiary / link:** underlined inline link in `--ink`. Hover: text
  and underline transition to `--accent`.
- **No gradients. No shadows. No radii.** The 0px radius is a Vignelli
  rule; rounded buttons are a UI-product affordance, not an editorial
  one.

---

## 7. Density and rhythm

### Grid

- **16-column conceptual grid** for layouts that need precision; in
  practice most layouts use the `.container` track (max 1240px) with
  internal flex / grid. The 12-column grid of v0.x is retired in favor
  of a flexible 16-column model.
- **Body column max-width: 680px** (`--col-body`). ~64-66 characters at
  body size.
- **Wide column max-width: 1040px** (`--col-wide`). For chart units
  that breathe past the body column.
- **Page max-width: 1240px** (`--col-page`). 40px gutter desktop,
  24px gutter mobile.

### Spacing scale

Mueller-Brockmann modular. Base 4px.

| Token  | Value | Use                                              |
|--------|-------|--------------------------------------------------|
| `s-0`  | 0     | -                                                |
| `s-1`  | 4px   | Inline glyph-to-label, tight micro               |
| `s-2`  | 8px   | Chart tick to label, table cell padding-y        |
| `s-3`  | 12px  | Label to value, dense list rows                  |
| `s-4`  | 16px  | Default paragraph spacing, panel internal        |
| `s-5`  | 24px  | Between body paragraphs, chartbook source margin |
| `s-6`  | 32px  | Chartbook body grid gap                          |
| `s-7`  | 48px  | Between sections within a page                   |
| `s-8`  | 72px  | Major section break                              |
| `s-9`  | 112px | Page top / bottom, before footer                 |

Larger compound rhythms (e.g. 64px between a section header and the
first chartbook unit) compose from `s-7 + s-3` or are hand-set per
template - the scale above is the atomic unit.

### Breakpoints

| Token | Min width | Notes                                       |
|-------|-----------|---------------------------------------------|
| `sm`  | 0         | Mobile. Single column.                       |
| `md`  | 640px     | Larger phones, small tablets.                |
| `lg`  | 960px     | Tablet landscape, small laptop.              |
| `xl`  | 1200px    | Desktop default.                             |
| `2xl` | 1440px    | Large desktop. Margin grows, content does not. |

---

## 8. Iconography

**Text-first. ASCII glyphs preferred over icon fonts.**

The Vignelli register treats icons as a failure mode. If a thing can be
named with a word, it gets a word. If a direction can be encoded by an
ASCII triangle, no SVG icon is needed.

**Where we use ASCII glyphs:**
- Direction: `U+25B2` / `U+25BC` / `U+2014`.
- Pipe separator in nav and eyebrows: `|` (regular ASCII pipe).
- Sort indicator: `U+25B2` / `U+25BC`.
- En dash for ranges: `U+2013`.
- Em dash for emphasis / pauses / placeholders: `U+2014`.

**Where we do not use icons:**
- Navigation labels. The word is the label.
- Section eyebrows. The figure number is a stamp; no decorative icon.
- Chart annotations. Typography carries the annotation; no info-icon.
- Buttons. Text-only.
- Status indicators. A typographic stamp, not a colored dot.

**The single icon-set fallback** for genuinely necessary icons (e.g. an
external-link affordance, an expand-collapse on a disclosure) is
**Lucide** at 16px, stroke-width 1.5, color pure ink. Imported per-glyph,
never as a bulk set. Used sparingly.

**No emoji.** Anywhere. In shipped UI. (Per the user's repository
instructions: ASCII-only.)

---

## 9. Motion and interaction

**Restrained. Motion serves comprehension, never decoration.**

### What we animate

- **Link hover:** 100ms ease-out color + text-decoration-color
  transition to `--accent`.
- **Button hover:** 100ms ease-out background-color transition.
- **Underline border on mark/nav-link hover:** 80ms linear.
- **Tooltip reveal on chart hover:** native browser SVG `<title>`
  tooltip - no JS, no fade.
- **Disclosure expand/collapse:** 200ms ease-in-out height transition.

### What we never animate

- **Entrance animations on page load.** The page renders and is there.
  No fade-up paragraphs. No staggered card reveals.
- **Number tickers / count-up.** A number is a measurement.
- **Scroll-triggered chart redraws** as the default. Scrollytelling, if
  done, is a deliberate format choice for a specific feature, not the
  default.
- **Hover effects on non-interactive elements.**
- **Parallax. Ever.**
- **Focus rings.** Instant. `outline: 2px solid var(--accent); outline-
  offset: 3px;` with no transition.

### Reduced motion

`prefers-reduced-motion: reduce` collapses all durations to 0.01ms via
the global rule in `base.css`. Disclosure becomes instant; hover color
transitions become instant; scrollytelling fallback to a stacked,
all-revealed layout.

---

## 10. Cohesion rules

How charts and surrounding page share design language. When a chart
feels native to its page rather than pasted in, this section is doing
its job.

- **The chart's plot frame is the same 1px black hairline as the panel
  table's row dividers and the section header's closing rule.** One
  hairline vocabulary across the entire page.
- **The chart's tick labels are the same Plex Mono regular as the
  table's numeric column.** A reader's eye reading a y-tick reads
  the same family weight and style as a reader reading a table cell -
  the chart's number reads as a measurement, the table's number reads
  as a measurement, they are the same kind of object.
- **The chart's direct label is the same Manrope 600 micro-caps as the
  eyebrow.** A "PLATE 01" in the eyebrow and a "CPI YoY" at the line
  terminus are visually the same kind of stamp.
- **The chart's latest-point dot is the same `--accent` signal red as
  the plate-number numeral in the eyebrow.** The brand-signal moment
  threads across the panel.
- **The chart's recession band is the same 6% ink wash as any other
  background tint on the page.** One wash treatment.
- **The chart's prose interpretation is the same Manrope 400 body-sm
  as the panel's lede.** Chart-adjacent prose reads as continuous
  with chart-non-adjacent prose; the chart and the prose are one
  object.
- **The chart's source line is the same Plex Mono 11px as the section's
  citation block.** Source attribution is a single typographic ritual,
  not a chart-specific affordance.

If a chart and its surrounding page feel like two objects, the
cohesion has failed. Fix at the chart's typographic chrome (axis
labels, direct labels, source line), not at the page's container.

---

## 11. Decisions flagged for the user

- **Mid-gray token (resolved 2026-05-11).** Placeholder ink is now a
  real token: `--ink-placeholder: #8A8A8A`, defined in
  `src/styles/tokens.css`. Five production components were
  hard-coding `#8A8A8A` literally and one (`DeepDivePanel`) had
  dropped to pure ink because its `--tk` class rule was missing - the
  QA sweep made the cost of "hard-coded escape hatch" visible enough
  to canonize the token. Application rules and detection-gate
  discipline are in Section 3.5. The other `--ink-*` tokens
  (`--ink`, `--ink-muted`, `--ink-faint`, `--rule`, `--rule-faint`)
  remain aliased to pure black; the opacity-composition pattern still
  carries the rare chrome cases (masthead nav pipes, eyebrow
  separators).
- **MTA red rendering.** `#E63946` is the production rendering. It is
  slightly warmer than the canonical 1972 MTA red (closer to a 1960s
  Knoll catalogue red than a transit-signage red). If editorial wants
  a cooler / more orthodox MTA red (e.g. `#EE352E` or `#D7202F`), this
  is a one-token swap; no other code needs to change.
- **Section accents on chartbook pages.** The Vignelli homepage uses
  one accent only (`--accent`). Section pages may pick up their
  assigned `--section-accent-*` token on the plate-number eyebrow and
  primary chart series (Phase 2). The decision of "homepage = one
  accent, section pages = per-section accent" is a deliberate split;
  if editorial wants total uniformity (one accent everywhere, even on
  section pages), say so and the `--section-accent-*` tokens collapse
  to `--accent`.
- **The categorical chart palette.** `--series-1` through `--series-7`
  retain their pre-Vignelli hex values (deep blue, burnt orange, etc.)
  Phase 2 section-page multi-series charts will consume them. If
  editorial wants the categorical palette to also Vignelli-ize
  (monochrome with weight / dash-pattern distinctions instead of
  hue), this is a Phase 2 decision and should be raised before the
  first multi-series section chart lands.
- **Callout component retirement.** `Callout.astro` is deprecated in
  the canon but remains in the codebase. New work should not use it.
  We have not flagged it for deletion because Phase 2 may revive a
  callout pattern with a Vignelli-compatible treatment (e.g. a 1px
  ink top + bottom rule sandwich with no fill).

---

## Appendix A - Token summary (the production reality)

```
/* Color: neutrals */
--paper:           #FFFFFF;
--surface:         #FFFFFF;
--surface-sunk:    #FFFFFF;
--ink:             #000000;
--ink-muted:       #000000;
--ink-faint:       #000000;
--rule:            #000000;
--rule-faint:      #000000;
--ink-placeholder: #8A8A8A;  /* Section 3.5 - placeholder copy only */

/* Color: accent (signal red, MTA / Vignelli) */
--accent:       #E63946;
--accent-soft:  #FAD4D7;

/* Color: semantic (retired for direction; defined for legacy) */
--pos:          #000000;
--pos-soft:     #FFFFFF;
--neg:          #000000;
--neg-soft:     #FFFFFF;
--neutral:      #000000;
--neutral-soft: #FFFFFF;

/* Color: categorical chart series (Phase 2 multi-series) */
--series-1:     #1F4E79;
--series-2:     #C9772A;
--series-3:     #5B7553;
--series-4:     #7A3E65;
--series-5:     #3F7D7C;
--series-6:     #8A6A2C;
--series-7:     #4A4F57;

/* Color: section accents (Phase 2 section-page wayfinding) */
--section-accent-gdp:       var(--series-1);
--section-accent-inflation: var(--accent);
--section-accent-labour:    var(--series-3);
--section-accent-housing:   var(--series-2);
--section-accent-policy:    var(--series-4);
--section-accent-markets:   var(--series-5);
--section-accent-trade:     var(--series-6);

/* Spacing */
--s-0: 0;
--s-1: 4px;  --s-2: 8px;  --s-3: 12px; --s-4: 16px;
--s-5: 24px; --s-6: 32px; --s-7: 48px; --s-8: 72px; --s-9: 112px;

/* Type families */
--font-sans:  "Manrope", "Helvetica Neue", Helvetica, Arial, sans-serif;
--font-serif: var(--font-sans);  /* aliased for legacy */
--font-mono:  "IBM Plex Mono", ui-monospace, "SFMono-Regular", Menlo, Consolas, monospace;

/* Type weights */
--fw-extralight: 200;
--fw-regular:    400;
--fw-medium:     600;
--fw-semibold:   600;
--fw-extrabold:  800;
/* Black (900) is reserved for the wordmark only; not tokenized. */

/* Layout */
--col-body:        680px;
--col-wide:        1040px;
--col-page:        1240px;
--gutter-desktop:  40px;
--gutter-mobile:   24px;

/* Borders */
--radius-card:  0;
--border-hair:  1px;

/* Motion */
--dur-fast:        100ms;
--dur-tooltip:     120ms;
--dur-disclosure:  200ms;
--ease-out:        cubic-bezier(0.22, 1, 0.36, 1);
--ease-in-out:     cubic-bezier(0.65, 0, 0.35, 1);
```

---

## Appendix B - Component map (what is real, what is deprecated)

**Production (live in v1.0):**
- `src/components/home/VignelliMasthead.astro`
- `src/components/home/TitleStatement.astro`
- `src/components/home/SectionPanel.astro`
- `src/components/home/DeepDivePanel.astro`
- `src/components/home/VignelliColophon.astro`
- `src/components/section/SectionPageHeader.astro`
- `src/components/section/ChartbookUnit.astro`
- `src/components/charts/MiniChart.astro`
- `src/components/charts/inflation/Panel1HeadlineCPI.astro`
- `src/components/charts/inflation/Panel2CoreTrio.astro`
- `src/components/charts/inflation/Panel3Breadth.astro`
- `src/components/charts/inflation/Panel4SubAggregates.astro`
- `src/components/charts/inflation/Panel5Expectations.astro`
- `src/components/charts/inflation/Panel6PassThrough.astro`
- `src/components/charts/gdp/Panel1HeadlineGDP.astro` ... `Panel6RecessionState.astro`
- `src/components/charts/labour/Panel1LFSHeadline.astro` ... `Panel6RegionalDumbbell.astro`
- `src/components/Sparkline.astro` (tier 1 sparkline; in use)

**Deprecated (in codebase but not part of the v1.0 canon; new work
should not use):**
- `src/components/charts/HeroChart.astro` - the hero-chart concept is
  retired; this component remains as a mini-chart variant for legacy
  pages.
- `src/components/Callout.astro` - background-filled callout; the
  Vignelli register does not use it.
- `src/components/Blurb.astro`, `Card.astro`, `Kicker.astro`,
  `SectionTile.astro`, `CompactTile.astro`, `DeepDiveCard.astro`,
  `HeroTile.astro` - pre-Vignelli scaffolding. Some may be revived in
  Phase 2 with Vignelli-compatible treatments; others are slated for
  removal.
- `src/components/experiments/**` - the experiments dir is the design
  R&D playground; not production.
