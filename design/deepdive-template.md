# Deep-Dive Template

Status: v1.0. Author: art-director.
Last updated: 2026-05-11.

This document specifies the visual template for **Sibley Creek deep-dive
essays** - the publication's third surface, after the homepage dashboard
(Vignelli panel grid) and the topic-page chartbook. Deep dives are where
the publication's voice arrives at length: 1500-3000 words of argument
scaffolded by hand-tuned charts, pull-quotes, footnotes, and a related
rail.

All tokens cited here are defined in `design/design-system.md`
(Appendix A). All visual rules cited here extend, not override, the
Vignelli canon. Where this template introduces new structure (pull-
quote pattern, side-margin footnote, related rail), the Vignelli
discipline still binds: pure paper, pure ink, single MTA red accent,
Manrope weight-contrast hierarchy, Plex Mono for measurements,
hairlines in pure black, no italic, no decoration.

This template **does not modify** `design/design-system.md` (the canon)
or `design/chartbook-template.md` (the topic-page spec). It is a third
surface with its own grammar, sharing the same typographic system.

---

## 0. Reference lineage

The deep-dive page descends from a different exemplar than the
chartbook. Where the chartbook unit comes from the Knoll catalogue
plate (an indicator, a chart, a caption), the deep-dive comes from:

- **The Vignelli book interior** - the way `Design: Vignelli` (Rizzoli,
  1990) and `Vignelli: From A to Z` (2007) treated long-form essay
  spreads. Body in a single sans family, ExtraLight quotations hung in
  generous margin, plates set into the column with their own
  hairline-framed eyebrow, Roman numeral section breaks.
- **Massimo Vignelli's Pirelli, Knoll, and Heller catalogue essays
  (1960s-1970s)** - the way an essay opening band carried a kicker,
  a deck, and a byline before the body began; the way a pull-quote
  could interrupt the body with a 200-weight hung phrase that re-stated
  the argument without restating it.
- **Edward Tufte, _Beautiful Evidence_ (2006)** - the Tufte sidenote
  pattern. Footnotes set in the right margin at the line they reference,
  not collected at the foot of the page. The deep-dive template offers
  sidenotes as the primary footnote treatment on viewports wide enough
  to support them, and falls back to a foot-of-page block on narrow
  viewports.
- **The Pudding long-form essays (mid-2020s)** - the way inline charts
  in a long-form data piece have more annotation surface than charts
  in a chartbook, because they carry the argument across a paragraph
  break rather than sitting next to a static interpretation cell. The
  deep-dive inline chart is larger, more annotated, and more
  hand-tuned than its chartbook cousin.
- **NYT Upshot long-reads (the 2017-2023 vintage)** - the convention
  of section-of-section hierarchy (Roman-numeral sub-headlines within
  a single piece) that lets a 2500-word argument breathe.

The deep-dive is **the publication's voice at length**. The chartbook
is the publication's view of one section's state. The homepage is the
publication's masthead. Three surfaces, one typographic system.

---

## 1. Aesthetic ambition

A reader who lands on a Sibley Creek deep-dive should feel they have
opened a Swiss-school **monograph**, not a blog post and not a
research note. The page should breathe. The body column should sit
in a 680px well surrounded by white. The masthead should recede the
moment the body begins. The Roman numerals between sections should
read as chapter markers in a printed essay, not as design ornament.

The pull-quotes should land like the ones in a Vignelli book - hung
in the margin at 200 weight, large enough to read at a glance from
across a room, light enough that they do not compete with the body
prose. The sidenotes should read like Tufte's: a measurement, a
citation, a parenthetical clarification that does not interrupt the
sentence.

The reader should finish the piece and, if they printed it, have a
document they could file. That is the bar.

---

## 2. Page structure (top to bottom)

```
+------------------------------------------------------------+
| [site masthead]                                             |  VignelliMasthead.astro
| --------------------------------------------------------    |  1px hairline
+------------------------------------------------------------+
| [status + version stamp row]                                |  one-line micro
| --------------------------------------------------------    |  1px hairline
+------------------------------------------------------------+
| [deep-dive header band]                                     |  new: DeepDiveHeader.astro
|   - kicker row                                              |
|   - title (display-xl, 800)                                 |
|   - deck (Manrope 200, large)                               |
|   - byline + date + reading-time stamp                      |
|   ====================================================      |  2px hairline (band close)
+------------------------------------------------------------+
| [essay body]                                                |
|   I. Section one                                            |
|     Body paragraphs ...                                     |
|     [Inline chart with elaborate annotations]               |
|     Body paragraphs ...                                     |
|     [Pull-quote, hung in margin]                            |
|     Body paragraphs ...                                     |
|   ---------------------------------------------             |  1px hairline (section break)
|   II. Section two                                           |
|     Body paragraphs ...                                     |
|     [Inline chart]                                          |
|     ...                                                     |
|   ---------------------------------------------             |
|   III. Section three                                        |
|     ...                                                     |
+------------------------------------------------------------+
| [citations block]                                           |  Sources at end
| --------------------------------------------------------    |  1px hairline
+------------------------------------------------------------+
| [related rail]                                              |  cross-references
+------------------------------------------------------------+
| [page footer]                                               |
+------------------------------------------------------------+
```

A deep-dive page is exactly: masthead + status stamp + header band +
essay body (with embedded inline charts, pull-quotes, sidenotes) +
citations + related rail + footer. No homepage panel grid. No plate
index (the deep-dive is one essay, not a chartbook). No chartbook
units in the body (the inline chart is a different atom).

---

## 3. Status + version stamp row

Sits between the masthead and the header band. A single line of
publication metadata before the editorial band begins.

```
DRAFTED 2026-05-08 | SHIPPED 2026-05-11 | UPDATED 2026-05-11 v1.1
================================================================
```

- **Stamp content:** three tokens separated by pipe glyphs (`|`) in
  pure ink at `opacity: 0.32` with 10px horizontal margin on each side.
  - `DRAFTED <YYYY-MM-DD>` - first internal draft.
  - `SHIPPED <YYYY-MM-DD>` - first public publish.
  - `UPDATED <YYYY-MM-DD> v<n.n>` - latest revision. Optional; omit
    if the piece has not been revised post-ship.
- **Typography:** Plex Mono 400 at 11px, line-height 1.4, `0.04em`
  tracking, pure ink. Tabular nums.
- **Label-stamp form:** the leading word (`DRAFTED`, `SHIPPED`,
  `UPDATED`) renders in Manrope 600 micro-caps at 10px, `0.18em`
  tracking, pure ink; the date and version body in Plex Mono per
  above. The same label-vs-body pattern as the chartbook eyebrow's
  `AS OF` stamp.
- **Closing rule:** 1px black hairline below the row.
- **Padding:** 12px top + 12px bottom inside the rule pair.
- **Editorial discipline:** the three timestamps are typographic
  facts, not decorations. If a piece is `DRAFTED` only (i.e. not yet
  shipped), the page renders in a publicly visible "Drafted" state
  and the kicker in the header band carries `DRAFT` as a fourth
  token (see Section 4.1).

---

## 4. Deep-dive header band

New component: `src/components/section/DeepDiveHeader.astro`.

Distinct from `SectionPageHeader.astro` (the chartbook header). The
chartbook header opens a topic page; the deep-dive header opens an
essay. Different kicker shape, different headline treatment, no
plate index.

### Anatomy

```
SIBLEY CREEK | DEEP DIVE | I | INFLATION                         <- kicker (10px micro-caps, accent pillar letter)
================================================================ <- 1px hairline

When did Canada lose its            <- title h1 (display-xl, 800, 40-56px clamp, -0.018em)
2% target?

A 12-month forensic of the    <- deck (Manrope 200 ExtraLight, 22-28px clamp, +0.0em)
moments that broke the
inflation anchor.

BY THE EDITORIAL DESK | MAY 11, 2026 | 11 MIN READ               <- byline (Plex Mono 11px + Manrope 600 micro-caps prefixes)
================================================================ <- 2px hairline (band close)
```

### 4.1 Kicker row

Four tokens, left-aligned, separated by `|` pipe glyphs in pure ink
at `opacity: 0.32` with 10px horizontal margin on each side.

- **Publication token:** `SIBLEY CREEK`. Manrope 600 micro-caps at
  10px, `0.22em` tracking, pure ink.
- **Format token:** `DEEP DIVE`. Manrope 600 micro-caps at 10px,
  `0.22em` tracking, pure ink.
- **Pillar letter token:** `I` (or `II`, `III`, etc.) - the Roman
  numeral assigned to the deep-dive in the publication's editorial
  ledger. Manrope **800** at 10px, `0.22em` tracking, in `--accent`
  (signal red). This is the deep-dive's brand-signal moment in the
  kicker, parallel to the chartbook's `SECTION 3 OF 7` numeral
  rendering in accent.
- **Section name token:** the parent section in uppercase (e.g.
  `INFLATION`, `LABOUR`, `POLICY`). Manrope **800** micro-caps at
  10px, `0.22em` tracking, pure ink. Heavier than the publication
  and format tokens so the eye lands on which section the deep-dive
  belongs to.
- **Optional `DRAFT` token:** if the piece is unshipped (the status
  row shows only `DRAFTED`, no `SHIPPED`), a fifth token `DRAFT`
  appends to the kicker in `--accent` 800 micro-caps. The reader
  recognizes immediately they are reading an unfinished argument.

The row sits 18px from the closing rule of the status stamp and
18px above the hairline that opens the title band.

### 4.2 Title

The deep-dive's editorial headline. A question, a declaration, or a
named argument.

- Manrope **800**, size `clamp(40px, 5.5vw, 56px)`, line-height
  1.05, letter-spacing `-0.018em`, pure ink. Renders as `<h1>`.
- Max-width: 22ch (forces editorial line breaks; same discipline as
  the chartbook headline question).
- **Title at display-xl** in the design-system scale; for deep dives
  the title may climb above `display-xl` (40px) toward 56px to honor
  the long-form ambition. The 22ch line-length discipline keeps the
  large size from feeling shouty.
- **No period** at the end of a question. **No full stop** on a
  declarative title that wraps to a single line. **Period only** on a
  declarative title that runs two or more lines (where the period
  reads as the close of a complete sentence rather than as a stop on
  a heading).
- Sits 18px below the title-band opening hairline.

### 4.3 Deck

Italic-substitute deck under the title. Vignelli's principle: italic
is not in the toolkit; quietness comes from dropping weight, not
slanting.

- Manrope **200** (ExtraLight), size `clamp(22px, 2.6vw, 28px)`,
  line-height 1.40, letter-spacing `0` (natural tracking), pure ink.
  Renders as a `<p class="deepdive-deck">` immediately after the
  `<h1>`.
- Max-width: 36ch.
- **The Vignelli weight-contrast moment of the header:** an 800
  title (48-56px) against a 200 deck (22-28px). The reader's eye
  reads "title -> deck" as a hierarchy carried entirely by weight
  and proportion, without italic, without color shift.
- Sits 24px below the title.
- Wording owned by `writer`. Editorial rule: the deck is one
  sentence, declarative, and **never repeats words from the title**.
  If the title is "When did Canada lose its 2% target?", the deck is
  "A 12-month forensic of the moments that broke the inflation
  anchor." not "Why Canada lost its 2% target."

### 4.4 Byline + date + reading-time stamp

A single line of metadata under the deck.

- Three tokens, left-aligned, separated by `|` pipe glyphs in pure
  ink at `opacity: 0.32` with 10px horizontal margin on each side.
- **Byline token:** `BY` prefix (Manrope 600 micro-caps 10px,
  `0.18em` tracking, pure ink) + author body in Plex Mono 400 at
  12px, pure ink. e.g. `BY THE EDITORIAL DESK` (the publication's
  default) or `BY A. RESEARCHER`. The author name renders in Plex
  Mono not Manrope because, like an `AS OF` stamp, an author is a
  vintage to a moment (this piece, this argument, this date) - Plex
  Mono signals "fixed in time."
- **Date token:** Plex Mono 400 at 12px, pure ink, tabular nums.
  e.g. `MAY 11, 2026`. No prefix label - the typographic shape (Plex
  Mono caps date) is unambiguous.
- **Reading-time token:** Plex Mono 400 at 12px, pure ink, tabular
  nums + `MIN READ` suffix in Manrope 600 micro-caps 10px, `0.18em`
  tracking. e.g. `11 MIN READ`. Calculated at build time from word
  count (~240 wpm baseline).
- Sits 28px below the deck.

### 4.5 Closing rule

A 2px black hairline 28px below the byline. Same weight as the
chartbook header's section-close rule. The 2px weight is reserved
for major band transitions in the system.

---

## 5. Essay body

The deep-dive body is the publication's load-bearing prose surface.
It sits in the `--col-body` 680px well, left-anchored in the page's
1240px container with the right margin reserved (on `lg+` viewports)
for sidenote rendering.

### 5.1 Body type scale

| Element                       | Scale token  | Family   | Weight | Size | Line height | Notes |
|-------------------------------|--------------|----------|--------|------|-------------|-------|
| Opening lede (first paragraph)| `body-lg`    | Manrope  | 200    | 19px | 1.55        | The first paragraph of the body, set in ExtraLight as a Vignelli "drop-cap-equivalent." Quiet weight signals "this is the entry, not the argument yet." |
| Body paragraphs               | `body`       | Manrope  | 400    | 17px | 1.55        | The default body weight. ~64-66 characters per line at 680px width. |
| Inline emphasis (`<strong>`)  | `body`       | Manrope  | 600    | 17px | 1.55        | Weight contrast is the emphasis device; no italic, no color. |
| Sub-section headline (h2)     | `display-md` | Manrope  | 800    | 28px | 1.20        | Roman-numeral section opener title. See 5.3. |
| Sub-sub headline (h3, rare)   | `display-sm` | Manrope  | 800    | 23px | 1.25        | Used only when a section legitimately has nested structure. |
| Pull-quote                    | `display-md` | Manrope  | 200    | 28px | 1.30        | ExtraLight at display size - the signature Vignelli pull-quote pattern. See 5.4. |
| Inline chart caption          | `body-sm`    | Manrope  | 400    | 15px | 1.50        | Captions match the chartbook interpretation prose size, so a reader's eye reads chart-adjacent copy as the same kind of object across surfaces. |
| Sidenote / footnote body      | `mono-xs`    | Plex Mono| 400    | 12px | 1.40        | See 5.6. |
| Citation source name          | `label`      | Manrope  | 600    | 13px | 1.40        | Small-caps with `0.18em` tracking. See 5.7. |
| Citation body                 | `mono-xs`    | Plex Mono| 400    | 12px | 1.45        | See 5.7. |

**Body width: 680px** (`--col-body`). The body column is **not**
narrower than the chartbook prose column - the deep-dive's prose is
the publication's voice, and the publication's voice gets the
canonical body column.

**Paragraph spacing:** 24px (`--s-5`) between paragraphs. No
first-line indent. No drop caps (the ExtraLight lede paragraph does
the entry-emphasis work that a drop cap would do in a print
broadsheet).

**Numbers in body prose:** Manrope 400 with `font-feature-settings:
"tnum"` enabled globally. Plex Mono is reserved for chart axes,
table cells, callout big numbers, sidenote bodies, and stamps - not
for inline numbers in prose.

### 5.2 First paragraph (the lede)

The opening paragraph of the essay body is rendered with a different
weight than the rest of the body. Treated as a Vignelli weight-
contrast moment.

- Manrope **200** (ExtraLight) at 19px, line-height 1.55, pure ink.
  Max-width 680px (the body column).
- Sits immediately under the header band's 2px closing rule, with
  48px top margin (`--s-7`) above it.
- Subsequent body paragraphs return to Manrope 400 at 17px.
- The lede paragraph is the entry. It restates nothing from the
  title or deck; it sets the scene. Wording owned by `writer`.

### 5.3 Section breaks (Roman numerals)

Sub-sections within the essay are introduced by a Roman numeral
opener. The deep-dive's sectioning device.

```
                                                                  <- 64px breathing room (--s-7 + --s-3)
I.   The anchor held until April                                  <- Roman numeral + sub-section title
-----------------------------------------------------------------  <- 1px black hairline, full body-column width
                                                                  <- 24px breathing room

Body paragraphs ...
```

- **Roman numeral:** rendered in Plex Mono **600** at 13px,
  `0.12em` tracking, in `--accent` (signal red). Tabular nums (so
  `I.`, `II.`, `III.`, `IV.`, `IX.` align to a common baseline).
  Followed by `.` and 16px horizontal whitespace (`--s-4`) before
  the sub-section title begins.
  - **Mono not Manrope:** the Roman numeral is the deep-dive's
    "plate number" equivalent - a structural stamp, not a heading.
    Plex Mono signals "this is metadata about the section, not
    part of the running title." Same logic as `PLATE 01` rendering
    in mono on the chartbook eyebrow.
  - **Accent red:** matches the chartbook's plate-number color and
    the deep-dive header kicker's pillar-letter color. The reader
    threads accent moments down the page.
- **Sub-section title:** Manrope **800** at 28px (`display-md`),
  line-height 1.20, letter-spacing `-0.012em`, pure ink. Max-width
  32ch.
- **Hairline rule:** 1px pure black, full body-column width (680px),
  sits 12px (`--s-3`) below the title line and 24px (`--s-5`)
  above the first body paragraph of the new section.
- **Breathing room above:** 64px (composed: `--s-7` + `--s-3` or
  hand-set as `clamp(56px, 6vw, 80px)`). The Roman numeral break is
  a major rhythm event in the essay; it earns generous white space.
- **Editorial rule:** sub-section titles are short (~3-7 words),
  declarative, and follow the chartbook title rule of ending with a
  period only when they read as a complete sentence.

### 5.4 Pull-quotes

The Vignelli pull-quote pattern. ExtraLight Manrope at display size,
hung in the margin or set as a banded interruption between
paragraphs.

#### 5.4.1 Hung pull-quote (default, `lg+` viewports)

Hangs in the right margin (the same column the sidenotes use), at
the line of the body where the quote sits in the editorial flow.

```
Body paragraph runs in the 680px well as           A 12-month
normal. The pull-quote hangs in the                forensic of the
right margin, baseline-aligned with                moments that
the start of this paragraph. The                   broke the
reader's eye lands on the                          inflation anchor.
margin moment without
losing the body line.
```

- **Typography:** Manrope **200** (ExtraLight) at 28px
  (`display-md`), line-height 1.30, letter-spacing `0`, pure ink.
- **Width:** 240px (sidenote-rail width); right-aligned within the
  rail.
- **Placement:** baseline-aligned with the body paragraph it
  punctuates. The quote does not get its own y-position; it sits
  where the body flow places it.
- **Decoration:** no quotation marks. No dropped indent. No accent
  color. The 200 weight and the margin position are the entire
  treatment.
- **Length:** 1-3 short clauses, ~12 words max. The quote restates
  a phrase from the surrounding paragraph in a stripped, memorable
  form - the way a Vignelli book pull-quote does.

#### 5.4.2 Banded pull-quote (mobile fallback + dramatic moments)

When the viewport is `< lg` (no sidenote rail), or when an
editorial-director designates a quote as a "dramatic" interruption
(rare, at most once per essay), the pull-quote renders as a banded
interruption between body paragraphs.

```
Body paragraph closes here.

================================================================  <- 1px black hairline
A 12-month forensic of the moments              <- Manrope 200 at 36px, max-width 36ch, centered
that broke the inflation anchor.
================================================================  <- 1px black hairline

Body paragraph continues here.
```

- **Typography:** Manrope **200** at 36px on `lg+` viewports (one
  step up from the hung version because the banded quote owns its
  vertical space), `clamp(28px, 4vw, 36px)` on smaller viewports.
  Line-height 1.30, pure ink.
- **Width:** max 36ch, centered within the 680px body column.
- **Hairlines:** 1px pure black, top and bottom, full body-column
  width. Sits 32px above and 32px below the quote text.
- **Spacing:** 48px (`--s-7`) of breathing room above the top rule
  and below the bottom rule, separating the banded quote from
  adjacent paragraphs.

### 5.5 Inline charts

The deep-dive's inline chart is a distinct atom from the chartbook
chart. It is larger, more annotated, and carries the argument across
a paragraph break.

#### 5.5.1 Geometry

- **Viewport width:** **breaks out of the 680px body column**, into
  the wider 960px frame (between body width and `--col-wide` 1040px).
  The chart sits centered within the body track but its plot can
  exceed the body-column width on `lg+` viewports - the deep-dive's
  charts breathe.
- **Aspect ratio:** 5:3 default; 16:9 for time-series with sparse
  vertical range; 1:1 for scatter or pass-through plots.
- **Plot area:** ~860 x 500 typical (the chartbook plot is ~432 x
  243; deep-dive plot is roughly double the linear scale).
- **Hand-tuned per chart.** Each inline chart is an Astro component
  in `src/components/charts/deepdive/<slug>/<panelName>.astro` with
  its own SVG geometry. No generic deep-dive chart component.

#### 5.5.2 Anatomy

```
FIGURE 1. | Headline CPI vs 2% target, 2020-2026                 <- eyebrow row (matches chartbook eyebrow)
================================================================  <- 1px hairline

+--------------------------------------------------------+
|                                                        |
|   The "anchor held" period            The break        |  <- inline annotations
|   <----- 2020-2022 ----->     <--- 2022 forward --->   |     (Manrope 400 body-sm,
|                                                        |     leader lines 1px pure ink)
|   [chart plot with hand-tuned annotations,             |
|    pure-ink line, 1.5px stroke, accent latest dot,     |
|    annotations sit in white space with leader lines]   |
|                                                        |
|   2% target reference rule (dashed pure ink)           |
+--------------------------------------------------------+

Figure 1. Headline CPI year-over-year change vs the BoC's 2%       <- caption
target. The 2022 break in the anchor is the load-bearing
observation in this piece.

SOURCE:  Statistics Canada Table 18-10-0004-01.                    <- source line

(body resumes 24px below)
```

- **Eyebrow row:** identical anatomy to the chartbook unit eyebrow
  (Section 3 of `chartbook-template.md`), except:
  - Stamp word is `FIGURE`, not `PLATE`. The deep-dive's argument is
    figured (the chart illustrates a point in the prose), not plated
    (a static indicator card). Wording difference; visual treatment
    identical.
  - The numeral renders in `--accent` 800 weight Plex Mono, same as
    chartbook plate numerals.
  - The chart name (e.g. `Headline CPI vs 2% target, 2020-2026`) in
    Manrope 600 at 11px, not uppercase.
- **Plot frame:** 1px pure black hairline (the canonical chart
  frame).
- **Annotations - typography:** Manrope **400** at 15px (`body-sm`)
  for annotation prose, weight 600 on the inline "anchor word." Pure
  ink. **Larger than chartbook annotations** (which run at
  `body-sm` 400 too but in a tighter 360px interpretation column);
  on a deep-dive chart, the annotation has room to be a complete
  sentence, not a label.
- **Annotations - placement:** hand-tuned. Annotations sit in the
  plot's white space, never over data. If white space is unavailable,
  the chart needs more margin. Leader lines: 1px pure black, no
  arrowhead, straight or single-elbow, ending 4px short of the
  anchored point.
- **Annotation length budget:** up to ~25 words per annotation
  (chartbook annotations are ~12 words max). The deep-dive chart can
  carry an explanatory annotation; the chartbook chart carries only
  an identifying annotation.
- **Latest-point dot:** 4-5px filled circle in `--accent` (same
  treatment as chartbook charts; slightly larger to scale with the
  larger plot).
- **Caption:** sits **below** the chart, 16px (`--s-4`) below the
  plot frame, Manrope 400 at 15px (`body-sm`), max-width 680px (the
  body column - the caption returns to body-column width even when
  the chart breaks out to the wider track). The caption opens with
  `Figure 1.` in Manrope 600 micro-caps (matching the eyebrow stamp).
- **Source line:** identical to chartbook source line. Plex Mono
  11px body, Manrope 600 10px `SOURCE:` prefix at `0.18em` tracking.
  16px below the caption.
- **Surrounding prose:** 2-3 paragraphs before the chart introduce
  what the figure will show; 2-3 paragraphs after the chart unpack
  what the figure showed. The chart is **load-bearing on the
  argument**, not decorative. If a reader could remove the chart
  and the argument still flows, the chart is decoration and should
  be cut.

#### 5.5.3 What this differs from the chartbook chart

Same Vignelli rules apply (pure ink line, accent latest-point dot,
1px hairline frame, no hue on direction). The differences are:

| Dimension              | Chartbook chart            | Deep-dive chart                     |
|------------------------|----------------------------|-------------------------------------|
| Plot size              | ~432 x 243                 | ~860 x 500                          |
| Annotation length      | ~12 words max              | ~25 words per annotation            |
| Annotation count       | 1-2 per chart              | 2-5 per chart                       |
| Interpretation surface | Adjacent 360px column      | Surrounding 2-6 paragraphs of body  |
| Caption                | None (the title row carries) | Yes, below the plot, 15px Manrope |
| Hand-tuning intensity  | Per-section convention     | Per-figure bespoke                  |

### 5.6 Footnotes / sidenotes

Two treatments: side-margin sidenotes (default on `lg+` viewports)
and foot-of-piece footnotes (default on smaller viewports + print).

#### 5.6.1 Inline marker

Wherever a footnote attaches in the body, the marker renders in the
body flow as:

- Superscript Plex Mono 400 digit at `0.75em` of body size, no
  brackets, in **`--accent`** (signal red). The marker is the
  deep-dive's per-sentence brand-signal moment. It catches the eye
  without interrupting the line.
- Tabular nums (so `1`, `10`, `100` align in adjacent sentences).
- No hover affordance other than the canonical link hover (text +
  underline color transition to `--accent`, but since the marker is
  already accent, on hover its `text-decoration-color` becomes
  pure ink as the inverse signal).

#### 5.6.2 Sidenote rendering (default, `lg+` viewports)

On viewports `>= 1200px` (where the page container has room for a
240px right rail beside the 680px body column), the footnote
renders **inline in the margin at the line it references**.

```
Body paragraph runs in the well. The reference{^1}     {^1} Plex Mono 12px sidenote body
sits inline. The sidenote appears in the right            sits in the right rail, top-aligned
margin at this line, top-aligned with this line.          with the marker line. Pure ink.
The body keeps reading.
```

- **Placement:** 240px wide right rail, baseline-aligned to within
  4px of the marker's text-line top.
- **Marker (in the rail):** the same superscript digit in `--accent`
  600 weight Plex Mono at 11px, no superscript shift (in the rail it
  sits on the line, not above).
- **Body:** Plex Mono 400 at 12px (`mono-xs`), line-height 1.45,
  pure ink. Tabular nums.
- **Length:** any. Sidenotes can be 1 line or 5 lines; they
  position-aware-flow to avoid overlapping each other.
- **Hairline:** none. Sidenotes do not get frames; they sit in
  white space.

#### 5.6.3 Footnote rendering (small viewports + print)

On viewports `< 1200px`, and on print, the footnote collects at the
foot of the piece (just above the citations block).

```
NOTES                                                       <- micro-caps heading
================================================================

1   Plex Mono 12px footnote body. Hanging indent so the     <- one footnote per row
    digit aligns and the wrapped text aligns under itself.

2   Second footnote. Tabular digits so multi-digit
    numbers (10, 100) hang correctly.
```

- **Heading:** `NOTES` in Manrope 600 micro-caps at 10px, `0.22em`
  tracking, pure ink. 1px black hairline below.
- **Items:** Plex Mono 400 at 12px for the digit, Manrope 400 at
  15px for the text. Hanging indent at 32px.
- **Backref:** each footnote ends with a small `up arrow` glyph
  (`U+2191`) in `--accent`, rendered as an `<a>` back to the marker
  in the body. Clicking returns the reader.

### 5.7 Citations

A primary source list at the end of the piece. Distinct from
footnotes (which carry parenthetical notes); citations carry the
publication's data and reference bibliography.

```
SOURCES                                                     <- micro-caps heading
================================================================

STATISTICS CANADA            Table 18-10-0004-01, Consumer Price Index
                             by major component, monthly. Retrieved 2026-05-10.

BANK OF CANADA               Monetary Policy Report, April 2026, pp. 12-18.

INTERNATIONAL MONETARY FUND  World Economic Outlook, April 2026 update,
                             "Inflation dynamics in advanced economies."
```

- **Heading:** `SOURCES` in Manrope 600 micro-caps at 10px,
  `0.22em` tracking, pure ink. 1px black hairline below.
- **Two-column form:**
  - **Source name (left column, ~200px):** Manrope 600 micro-caps
    at 13px (`label`), `0.18em` tracking, pure ink. e.g.
    `STATISTICS CANADA`, `BANK OF CANADA`, `INTERNATIONAL MONETARY
    FUND`. Tabular alignment so all source names sit on the same
    left edge.
  - **Citation body (right column, fills remaining body column):**
    Plex Mono 400 at 12px (`mono-xs`), line-height 1.45, pure ink.
    Tabular nums. Includes table/document identifier, page
    reference, retrieval date.
- **No italic on titles.** Italic is retired across the system. A
  document title within a citation body renders in Plex Mono 400
  (the same weight as the rest of the citation body); a
  publication name (e.g. `Monetary Policy Report`) renders in Plex
  Mono 600 weight (the inline weight-contrast emphasis device).
- **Row separator:** 12px (`--s-3`) vertical gap between rows. No
  rule between rows (the rules would compete with the section
  hairlines above and below).
- **No URLs in citations.** A live data source link, if needed,
  attaches to the source name as the linked text (canonical link
  treatment: text-decoration underline in pure ink, hover transitions
  to `--accent`).

---

## 6. Related rail

At the foot of the piece, above the page footer. Cross-references to
other deep dives and to the load-bearing topic page that grounds this
piece.

```
================================================================  <- 1px hairline

RELATED                                                       <- micro-caps heading

+----------------------------+ +----------------------------+ +----------------------------+
| SIBLEY CREEK | DEEP DIVE   | | SIBLEY CREEK | DEEP DIVE   | | SIBLEY CREEK | TOPIC PAGE |
|                            | |                            | |                            |
| Why labour didn't loosen   | | The OIS curve as a         | | Inflation                  |
| when it should have        | | political artifact         | |                            |
|                            | |                            | | Is Canadian inflation      |
| II | LABOUR | MAY 04, 2026 | | IV | POLICY | APR 27, 2026 | | returning to target?       |
| 9 MIN READ                 | | 14 MIN READ                | |                            |
|                            | |                            | | LATEST: APRIL CPI          |
+----------------------------+ +----------------------------+ +----------------------------+
```

- **Heading:** `RELATED` in Manrope 600 micro-caps at 10px,
  `0.22em` tracking, pure ink. 1px black hairline above (separating
  related rail from citations). 24px below the rule.
- **Card grid:** 3 cards on `lg+` viewports (CSS grid `repeat(3, 1fr)`,
  24px gap). Drops to 1-column stack on `< 720px` viewports. 2-up
  on tablet.
- **Card content (deep-dive related):**
  - **Top kicker:** `SIBLEY CREEK | DEEP DIVE` in Manrope 600 micro-
    caps at 9.5px, `0.22em` tracking, pure ink. 1px hairline below
    kicker (within the card, separating kicker from title).
  - **Title:** Manrope **800** at 18px (between `body-lg` and
    `display-sm`), line-height 1.20, letter-spacing `-0.008em`, pure
    ink. Max 2 lines (CSS line-clamp 2). 16px (`--s-4`) above the
    title, 16px below.
  - **Bottom kicker:** pillar letter (accent red 800, Plex Mono) +
    section name (Manrope 800 micro-caps) + date (Plex Mono 11px).
    Same anatomy as the deep-dive kicker, scaled to card.
  - **Reading time:** below the kicker, Plex Mono 11px + `MIN READ`
    micro-caps suffix.
- **Card content (topic-page related):**
  - **Top kicker:** `SIBLEY CREEK | TOPIC PAGE` in micro-caps.
  - **Section name:** Manrope 800 at 22px, `display-sm`-ish, the
    section's name (e.g. `Inflation`).
  - **Headline question:** the topic page's headline question in
    Manrope 200 at 15px, max 2 lines (matches the lede pattern
    used in chartbook headers - 800 section name + 200 question is
    the chartbook header in miniature).
  - **Latest stamp:** `LATEST: APRIL CPI` in Manrope 600 micro-caps
    at 9.5px, `0.18em` tracking, pure ink.
- **Card frame:** 1px pure black hairline border on all four sides.
  No fill (`--paper`), no shadow, no radius. 24px internal padding.
- **Card hover:** entire card background transitions to `--ink`
  (pure black), all text inverts to `--paper` (white). 80ms linear.
  Same hover treatment as the chartbook plate-index cell. Reads as
  "you can click here."
- **Card focus:** 2px `--accent` outline inset (`outline-offset:
  -2px`), no transition.
- **Editorial discipline:** the related rail surfaces **at most 3
  items**: 2 deep dives + 1 topic page, or 3 deep dives if the
  piece is genuinely standalone from any topic page. The
  load-bearing topic page (the one most relevant to this deep-dive's
  argument) is always included unless explicitly suppressed.

---

## 7. Print-friendly variant

Deep dives may be printed. The Vignelli register is print-native -
hairlines survive, MTA red survives, white space is generous - so
the print variant is mostly the screen variant with three
adjustments.

### 7.1 Sidenotes -> footnotes

Print does not have a 1200px viewport with a side rail. The CSS
print stylesheet (`@media print`) collapses the sidenote rail and
re-renders all sidenotes as a foot-of-piece footnote block (Section
5.6.3 treatment).

### 7.2 Page breaks

- `@media print { h1, h2 { break-after: avoid; } }` - prevents an
  orphaned Roman-numeral sub-section title at the bottom of a
  printed page.
- `@media print { figure.deepdive-chart { break-inside: avoid; } }`
  - prevents a chart from splitting across pages.
- `@media print { .deepdive-pullquote, .deepdive-pullquote-banded {
  break-inside: avoid; } }` - prevents a pull-quote from splitting.

### 7.3 Color

The MTA red `--accent` survives in print. Modern color laser printers
render it adequately; black-only printers render it as a mid-gray
which is acceptable for the brand-signal moments (latest-print dot,
Roman numeral, figure number) because the brand role is structural,
not encoding direction. Direction is encoded by glyph (per the
canon), so no information is lost if accent collapses to gray.

### 7.4 What is dropped in print

- The status stamp row (`DRAFTED / SHIPPED / UPDATED`). Print readers
  are by definition reading the version they printed; the timestamp
  is screen metadata.
- The hover state on related-rail cards. Print is non-interactive.
- The masthead's nav. Print readers do not need site navigation.

The site masthead's **wordmark** is retained at the top of the print
output - the reader knows what publication produced the document.

### 7.5 What is kept in print

- The header band (kicker, title, deck, byline). Full editorial
  framing.
- All Roman-numeral section breaks with their hairline rules.
- All inline charts at full annotation density.
- All pull-quotes in banded form (the hung form collapses to banded
  in print, since print has no margin rail).
- All footnotes (the sidenote -> footnote collapse).
- All citations.
- The related rail (rendered as a static list of titles + kickers;
  cards become rows separated by hairlines).

---

## 8. ASCII mockup of one deep-dive page (full rendering)

The following is a representative single-page rendering of a deep-dive
to this spec, showing the masthead, status stamp, header band, body
with inline chart, section break, pull-quote, sidenote, footnote
marker, citations, and related rail.

```
================================================================================
SIBLEY CREEK    Inflation   GDP   Labour   Housing   Policy   Markets   Trade
================================================================================

DRAFTED 2026-05-08 | SHIPPED 2026-05-11 | UPDATED 2026-05-11 v1.1
--------------------------------------------------------------------------------

SIBLEY CREEK | DEEP DIVE | I | INFLATION
================================================================================

When did Canada lose its
2% target?

A 12-month forensic of the
moments that broke the
inflation anchor.

BY THE EDITORIAL DESK | MAY 11, 2026 | 11 MIN READ
================================================================================


    For most of the 2010s the Bank of Canada's 2% target functioned as an
    anchor: prices drifted within a one-percentage-point band, expectations
    sat where the target said they should sit, and the policy rate moved
    in increments small enough that the economy could absorb them. That
    period is now over. The question this piece asks is not whether the
    anchor will return - the consensus says it will - but when, precisely,
    it was lost, and what the data tell us about why.



I.   The anchor held until April                                          <- I. in Plex Mono 600
--------------------------------------------------------------------------     accent red
                                                                          <- 1px hairline

The clearest reading of the breakdown begins not in 2022 but in the         (^1)  <- sidenote marker
twelve months before. Through 2021 the headline CPI print averaged          accent red
2.8% year-over-year - elevated, but plausibly transitory, and within
the 1-3% control band the Bank tolerates around the 2% target. The
3-month annualized series, which moves faster than the y/y, was
already running hotter; the 6-month annualized, faster still. By
the time the April 2022 print landed at 6.7%, the anchor had been
slipping for the better part of a year and the surprise was that
the surprise was a surprise.


+--------------------------------------------------------------------+
|  FIGURE 1. | Headline CPI vs 2% target, 2020-2026                  |
|  =================================================================|
|                                                                   |
|   The "anchor held" period          The break             Now     |
|   <----- 2020-2022 ----->    <----- 2022-2024 ----->    <- 2025-> |
|                                                                   |
|       +-------------------------------------------------+         |
|       |                                                 |         |
|     8%|                          .--..                  |         |
|       |                       .-'    '-.                |         |
|     6%|                    .-'         '-.              |         |
|       |                .-'              '-..            |         |
|     4%|             .-'                    '-.          |         |
|       |          .-'                          '-..      |         |
|     2%|. . . . -' . . . . . . . . . . . . . . . .'-..__@| <-- accent
|       |     -'                                          |  red dot
|     0%+-------------------------------------------------+         |
|         2020      2021      2022      2023    2024  2026         |
|                                                                   |
|         2% target reference rule (dashed pure ink)                |
+--------------------------------------------------------------------+

Figure 1.  Headline CPI year-over-year change vs the BoC's 2% target.
           The 2022 break in the anchor is the load-bearing observation
           in this piece.

SOURCE:    Statistics Canada Table 18-10-0004-01.


This is the shape the argument has to fit. The headline number broke
in 2022. The core measures - trim, median, common - broke earlier and
held the break for longer.{^2}                                              <- footnote marker
                                                                              accent red



                                  ====
                          A 12-month forensic of the
                          moments that broke the
                          inflation anchor.
                                  ====
                                                                          <- banded pull-quote
                                                                             Manrope 200 / 36px
                                                                             centered, 1px rules above
                                                                             and below



The story of the break has been told as a supply story - global energy,
container shipping, a war. That story is incomplete. The data tell a
domestic story too, and the domestic story is what determines when, and
by how much, the anchor returns.



II.  Three breaks, not one                                                <- II. in Plex Mono 600
--------------------------------------------------------------------------     accent red

The headline number is the one the public reads, but the Bank reads three.
Each of CPI-trim, CPI-median, and CPI-common is constructed to strip a
different kind of noise; together they triangulate the underlying signal.
Through 2022, all three accelerated, but at different speeds and from
different starting points...

[body continues, more paragraphs, second inline chart, third section break,
 closing paragraphs]

================================================================================

SOURCES
================================================================================

STATISTICS CANADA            Table 18-10-0004-01, Consumer Price Index by
                             major component, monthly. Retrieved 2026-05-10.

                             Table 18-10-0256-01, Consumer Price Index by
                             product group, monthly, percentage change.

BANK OF CANADA               Monetary Policy Report, April 2026, pp. 12-18.

                             Summary of Governing Council deliberations,
                             April 16, 2026 decision.

INTERNATIONAL MONETARY FUND  World Economic Outlook, April 2026 update,
                             "Inflation dynamics in advanced economies."


================================================================================

RELATED

+----------------------------+ +----------------------------+ +----------------------------+
| SIBLEY CREEK | DEEP DIVE   | | SIBLEY CREEK | DEEP DIVE   | | SIBLEY CREEK | TOPIC PAGE |
| ------------------------   | | ------------------------   | | ------------------------   |
|                            | |                            | |                            |
| Why labour didn't loosen   | | The OIS curve as a         | | Inflation                  |
| when it should have        | | political artifact         | |                            |
|                            | |                            | | Is Canadian inflation      |
| II | LABOUR | MAY 04, 2026 | | IV | POLICY | APR 27, 2026 | | returning to target?       |
| 9 MIN READ                 | | 14 MIN READ                | |                            |
|                            | |                            | | LATEST: APRIL CPI          |
+----------------------------+ +----------------------------+ +----------------------------+


================================================================================

(page footer follows)
```

---

## 9. Component implementation map

Frontend-designer will implement these. Names follow production
conventions:

| Component                                                       | Role                                                  |
|-----------------------------------------------------------------|-------------------------------------------------------|
| `src/components/section/DeepDiveHeader.astro`                   | The header band (kicker, title, deck, byline).        |
| `src/components/section/DeepDiveStatusStamp.astro`              | The status row (DRAFTED / SHIPPED / UPDATED).         |
| `src/components/section/DeepDiveSectionBreak.astro`             | The Roman-numeral sub-section opener.                 |
| `src/components/section/DeepDivePullQuote.astro`                | Both hung and banded variants (prop-selected).        |
| `src/components/section/DeepDiveSidenote.astro`                 | Inline sidenote (with print fallback).                |
| `src/components/section/DeepDiveCitations.astro`                | The two-column sources block.                         |
| `src/components/section/DeepDiveRelatedRail.astro`              | The 3-card cross-reference rail.                      |
| `src/components/charts/deepdive/<slug>/<panel>.astro`           | One Astro file per inline chart, hand-tuned.          |

The chartbook components (`SectionPageHeader.astro`, `ChartbookUnit.astro`)
**are not consumed** by the deep-dive page. Different surface, different
grammar. The wider site components (`VignelliMasthead.astro`,
`VignelliColophon.astro`) are consumed unchanged.

---

## 10. Open questions for frontend-designer

The implementer should raise back to art-director before deciding
unilaterally on any of these:

1. **Sidenote breakpoint.** I have specified `>= 1200px` as the sidenote
   threshold (above which the 240px right rail appears). If the page
   container's wider track is genuinely 1240px with 40px gutters, there
   is exactly 240px of room to the right of the 680px body column on
   the 1240px container - but only if the body column is left-anchored,
   not centered. Confirm the body column is **left-anchored** within the
   container on `lg+`, with sidenote rail to its right. If
   editorial-director wants the body centered for aesthetic balance,
   the sidenotes need to fall back to foot-of-piece footnotes
   everywhere, which is a real loss; raise back.
2. **Hung pull-quote interleaving with sidenotes.** The hung pull-quote
   and the sidenote share the right rail. If a pull-quote and a
   sidenote both anchor to the same paragraph, they will collide. The
   editorial discipline is "one or the other per paragraph, not both,"
   but the implementer needs a collision-detection or a
   editorial-warn pattern. Propose: surface a build-time warning if
   a paragraph contains both a `<DeepDivePullQuote>` and a
   `<DeepDiveSidenote>` child. Decision flagged.
3. **Banded pull-quote vs section-break hairline visual conflict.** A
   banded pull-quote and a Roman-numeral section break both use full-
   body-column 1px hairlines. If the editorial flow places a banded
   pull-quote immediately before or after a section break, the page
   gets four hairlines in close proximity (section-break rule, pull-
   quote top rule, pull-quote bottom rule, next section's break rule).
   Recommend: the editorial discipline is to never place a banded
   pull-quote within 64px of a section break. Document this in the
   editorial canon; do not enforce in code.
4. **Inline chart breakout width.** I have specified ~860px plot width
   on `lg+` viewports (the chart breaks out of the 680px body column).
   Verify the 1240px container has room for this breakout on the
   left as well as the right - the chart should center under the body
   column, not align-left-to-body-and-overflow-right. If the layout
   reserves the right rail for sidenotes/pull-quotes only, the chart
   may need to align-left-to-body and have a shorter max width
   (~960px). Raise back when implementing the first deep-dive page so
   we tune to the actual grid.
5. **Reading-time calculation.** The byline includes a `MIN READ`
   token. Compute at build time from the rendered word count of the
   essay body at 240 wpm baseline, rounded to nearest integer. If the
   piece contains inline charts that take meaningful reader time, add
   a flat 30s per chart to the calculation. This is a content-pipeline
   concern; raise back if the integration is non-trivial.
6. **Related rail manual curation vs automatic.** v1: the related rail
   is manually curated per piece (editorial-director chooses the 2-3
   cross-references). v2 may use tag-based automatic surfacing. Keep
   the v1 prop interface simple: `relatedItems: RelatedRef[]` where
   each ref is `{ kind: 'deep-dive' | 'topic-page', slug: string,
   overrideTitle?: string }`.

---

## 11. Coherence check against the canon

Self-audit that the deep-dive template does not violate
`design/design-system.md`:

| Canon rule                                              | Deep-dive compliance                                                                 |
|---------------------------------------------------------|--------------------------------------------------------------------------------------|
| Pure white paper, pure black ink                        | All surfaces `--paper` / `--ink`. No fill. No tint other than 6% recession wash on charts. |
| Manrope as the only sans family                         | Title, deck, body, sub-headings, pull-quotes, captions all Manrope.                  |
| Plex Mono for measurements only                         | Stamps, sidenote bodies, citation bodies, Roman numerals, latest-release stamp, byline date. |
| Single accent (`--accent` MTA red)                      | Pillar letter in kicker, Roman numeral, figure number numeral, latest-point dot, footnote marker, focus rings. No data direction use. |
| Weight contrast is the hierarchy device                 | 800 title vs 200 deck. 800 sub-section title vs 400 body. 400 body vs 600 inline strong. 200 hung pull-quote vs 400 surrounding body. |
| No italic                                               | Deck is ExtraLight, not italic. Source titles in citations are Plex Mono 600, not italic. No italic anywhere. |
| Direction by glyph, not color                           | No data direction encoding in the deep-dive template; charts inherit Vignelli direction rules. |
| 1px black hairlines                                     | Status stamp closing rule, kicker closing rule, section-break rule, chart eyebrow rule, plot frame, citations rule, related rail opening rule. |
| 2px black hairlines for major-band close                | Header band closing rule (one per page, matches chartbook).                          |
| No drop shadows / gradients / radii                     | Related rail cards: 1px border, 0px radius, no shadow. Matches chartbook plate index. |
| No icons except Lucide fallback                         | No icons used in this template. ASCII glyphs only (pipe, back-arrow up `U+2191` for footnote return). |
| No animations except link / hover / disclosure          | Card hover ink-invert (80ms linear) matches chartbook plate-index. No entrance animation, no scroll trigger. |
| Body column max 680px                                   | Body confirmed at 680px. Inline chart breaks out to ~860px; caption returns to 680px. |
| 60-68 character body line; 22-32 character headlines    | Body at 680px hits ~64ch. Title max-width 22ch. Sub-section title max-width 32ch.     |

No canon violations. The deep-dive template is a third surface, not a
redefinition.

---

End of deep-dive template v1.0.
