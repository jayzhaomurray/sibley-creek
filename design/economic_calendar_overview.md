# Economic-calendar frame — `/overview/`

**Status:** v1 spec, 2026-05-23. Implements Path A (investing.com iframe inside a
Sibley Creek frame). Path B (own-built calendar) is a separate later project; do
not anticipate it in this spec.

**Scope rule:** we style only what is OUTSIDE the iframe. Investing.com's table
typography is a known visual cost (see §7). The frame's job is to read as a
deliberate Sibley Creek section so the iframe lands as a quoted instrument, not
a third-party paste-in. Bloomberg uses the same widget on their news pages; we
are operating in that register.

---

## 1. Section header

**Decision: `Week ahead.`**

Two words, terminal period (matches chart-plate title canon — see
`writing-style.md` Sec 4.2). Reasoning: the widget is configured to
`calType=week`; the header should describe the window the table shows, not a
generic noun ("Economic calendar") or an editorial promise ("Coming up", which
implies curation we are not providing — the iframe lists every Canada/US
high-importance release verbatim from investing.com).

Rejected alternatives:
- "Economic calendar" — accurate but bureaucratic; doesn't signal week.
- "Coming up" — sets an editorial expectation the iframe can't deliver.
- "Releases" — too narrow (the calendar also lists speeches, auctions, decisions).

If Path B ships and we layer in curated annotations, revisit. For Path A,
"Week ahead." is the honest label.

## 2. Section header typography + spacing

Use the existing section-eyebrow + section-H2 vocabulary from
`SectionPanel.astro` / `TitleStatement.astro` — no new register.

```
.cal__eyebrow                                .cal__h
font-family: var(--font-sans)                font-family: var(--font-sans)
font-weight: 600                             font-weight: 800
font-size: 10px                              font-size: 22px
letter-spacing: 0.22em                       letter-spacing: -0.01em
text-transform: uppercase                    line-height: 1.05
color: var(--ink)                            color: var(--ink)
content: "Figure 9."                         content: "Week ahead."
fig-n in var(--accent), weight 800           margin: 6px 0 0
```

Figure number follows the chartbook count. If/when the 8th fiscal panel lands,
the calendar becomes Figure 9 (it sits below the grid — see §6 — so it is
always last regardless of grid count).

Header band height: matches `.vig-panel__head` — 10px padding-bottom + 1px
hairline-bottom under the H2 (mirrors the in-panel head treatment, scaled to
the section width). This is the rhythm the chartbook already uses; the calendar
inherits it so the eye reads "next chartbook unit" not "embed".

## 3. Container styling

**Borderless on left/right, 1px black hairline top and bottom.** The
chartbook grid above closes with `border-bottom: 1px solid var(--ink)` on its
last row of cells; the calendar section opens with its own `border-top` and
closes with `border-bottom`, both `1px solid var(--ink)`. The two hairlines
sit flush — no visual gap, no double-rule.

Why not a fully-bordered box (matching the chartbook cells)? Because the
iframe's own internal padding + investing.com chrome already creates an
inset visual edge. Wrapping it in a four-sided hairline reads as a card
inside a card. The chartbook grid earns its four-sided rule because its
cells share edges; a standalone embed below the grid earns only the two
horizontal rules that continue the page's hairline rhythm.

Vertical spacing: `margin-top: 32px` between the chartbook grid's
bottom-hairline and the calendar's eyebrow (matches `.vig-title`
`padding-block: 32px 28px` rhythm). Internal padding above the iframe
(between H2 hairline and iframe top): `padding-top: 20px`. Internal padding
below iframe (between iframe and attribution): `padding-top: 14px`. Section
ends with `padding-bottom: 28px` then the closing hairline.

## 4. Responsive sizing

**Width:** override the iframe's hardcoded `width="650"` to `width: 100%`
via CSS on the iframe element. The container is the standard `--col-page`
shell (1240px max, gutter-padded), so on desktop the iframe stretches to
~1140px usable width; on tablet ~720px; on phone the page gutter shrinks it
to ~328px at iPhone SE width.

**Height:** keep `height="467"` as the HTML attribute (investing.com's
recommended default), override via CSS to a fluid clamp:

```css
.cal__frame {
  width: 100%;
  height: clamp(520px, 64vh, 640px);
  border: 0;
  display: block;
}
```

Reasoning: investing.com's widget renders ~10-12 high-importance Canada+US
events in a typical week. At their row height (~32-36px) plus the
datepicker/timezone control band (~64px) plus column headers (~36px),
~520px shows roughly 12 rows without internal scroll on a normal week.
`64vh` gives a comfortable read on laptops; the 640px ceiling keeps the
calendar from dominating the viewport on tall monitors. The widget itself
provides an internal scrollbar past the fixed height, which is fine — it
appears only on heavier release weeks (FOMC + payrolls + CPI clustering)
and reads as "more below," not as overflow.

**Mobile behavior:** at <480px the widget compresses its columns
automatically; the `flags` and `importance` columns stay readable, `actual`
/ `forecast` / `previous` get narrower. We do not hide columns — the table
is investing.com's, not ours. We do bump `.cal__frame` min-height to
`540px` at narrow widths so the timezone/datepicker band doesn't crowd the
first event row. No horizontal scroll on the iframe element; the widget
handles its own internal layout.

## 5. Attribution styling

Investing.com's terms require the exact wording, link target, and link
text. We restyle the wrapper only.

```css
.cal__attribution {
  margin: 14px 0 0;
  font-family: var(--font-sans);
  font-weight: 600;
  font-size: 10px;
  line-height: 1.4;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: var(--ink);
}
.cal__attribution a {
  color: var(--ink);
  text-decoration: none;
  border-bottom: 1px solid var(--ink);
}
.cal__attribution a:hover {
  color: var(--accent);
  border-bottom-color: var(--accent);
}
.cal__attribution a:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: 3px;
}
```

This matches the splash colophon / Knoll-catalogue credit-line register:
small-caps, wide-tracked, ink-black, deliberate. Hover follows the
site-wide convention (accent ink + accent underline) so the link reads as
ours, not as a vendor signature. Drop the `<span>` wrapper inside their
`<div class="poweredBy">`; keep the `<a>` exactly as their terms require.
Replace the class `poweredBy` with `cal__attribution` on the wrapping div —
the terms govern wording + link, not class names.

## 6. Placement on `/overview/`

**Below the 7-panel chartbook grid, full-width within `--col-page`.** Not
sidebar, not interleaved. The grid is the data instrument; the calendar is
a release schedule. They are different read tasks and the page's vertical
rhythm should reflect that.

Concrete layout coords (in `src/pages/overview.astro`):

```astro
<article class="home">
  <TitleStatement dateLine={longDate} />
  <section class="home__grid" ...> {/* 7 or 8 panels */} </section>
  <section class="cal" aria-labelledby="cal-h">
    <header class="cal__head">
      <p class="cal__eyebrow">
        <span class="cal__fig">Figure</span>
        <span class="cal__fig-n">9.</span>
      </p>
      <h2 id="cal-h" class="cal__h">Week ahead.</h2>
    </header>
    <iframe class="cal__frame" src="..." title="Canada and US economic releases, this week, high importance only" />
    <div class="cal__attribution">
      Real Time Economic Calendar provided by
      <a href="https://ca.Investing.com/">Investing.com Canada</a>.
    </div>
  </section>
</article>
```

Stable across the fiscal-panel refactor: when the grid expands to 8
panels, the calendar shifts to Figure 9 without any other change. If the
grid expands further (it won't in v1), the calendar's figure number
increments; the layout doesn't move.

Add `title` attribute on the iframe (above) for accessibility — investing.com
omits one by default.

## 7. Visual cost acknowledgment

**Inside the iframe:** investing.com's Arial/sans typography, their
light-gray row dividers, their country-flag bitmaps, their orange-bull /
red-bear importance icons (3 bulls for high importance), their blue link
hover. None of this is overridable. The widget is roughly the visual
register of a Bloomberg Terminal subwindow embedded in a Vignelli page —
the contrast is the honest cost of shipping a release calendar without
building one.

**What the frame buys us:** the header, the hairlines, the attribution,
and the placement read as deliberate Sibley Creek. A reader scanning the
page sees a chartbook grid + a release schedule, both framed in the same
typographic vocabulary; the iframe's interior is clearly a quoted source.
This is the same pattern Bloomberg uses on bloomberg.com/markets/economic-calendar.
Do not attempt to mask the typography mismatch with overlay CSS, faux
borders, or color overrides on the iframe element — they will fail at
unpredictable iframe-internal sizes and read worse than honest framing.

**When to revisit:** if/when Path B ships (own calendar, primary-source
StatsCan + BEA + Treasury release feeds), the frame stays; the iframe
swaps for a native component built to chartbook canon. Frame is forward-
compatible.

---

## Tokens used (no new tokens introduced)

- `--ink` (#000000), `--paper` (#FFFFFF), `--accent` (#E63946)
- `--font-sans` (Manrope), `--font-mono` (IBM Plex Mono) — mono not used here
- `--col-page` (1240px), `--gutter-mobile` / `--gutter-desktop`

## Acceptance check (for frontend-designer)

1. Header reads "Figure 9. / Week ahead." in the chartbook eyebrow + H2 register.
2. Hairlines: 1px top, 1px bottom, none on sides. No double-rule with the grid above.
3. Iframe fills the page column at all widths; height clamps 520-640px.
4. Attribution restyled in Manrope SemiBold uppercase 0.18em tracking, ink-on-paper, accent on hover.
5. Section title attribute on iframe present for screen readers.
6. No CSS attempts to reach inside the iframe (no `filter:`, no overlay).
