# Trade section redraft -- Gate 3 verdict (surface fit, 2026-10-03)

Reviewed: final text in `trade_draft.md` (post Gate 1 and Gate 2), the `slug: "trade"` block of
`src/data/sections.ts`, all of `src/pages/trade.astro`, and the plate/as-of handling in
`src/layouts/SectionLayout.astro`. Nothing under `src/` and nothing in `trade_draft.md` was edited.

Not checked: I did not run the build, and I did not open the rendered page. The as-of finding
below is read from the layout code, not from pixels. I did not confirm whether any build gate or
visual baseline counts plates.

## Verdict per surface

| Surface | Verdict | Action |
|---|---|---|
| Stamps (comment, updatedAt, heroKicker, blurb.date) | PASS | none |
| Splash tile line | PASS | none |
| Section abstract | PASS | none (take change stays with Jay) |
| Plate 01 title | FAIL | retitle (trim below) |
| Plate 01 body, callout, source line | PASS | none |
| Plate 02 (whole plate) | FAIL | hide until the August release re-points the chart |
| Plate 03 label, title, body, callout | PASS | none |
| Plate 04 title, body, labels | PASS | add a hand-set as-of stamp (below) |

## 1. Abstract

Reads as a direct answer to "Is Canada's trade pivot working?": a take, the mechanism, two reasons
to discount it. A reader can use it. Length is right for the slot. No jargon, no method talk, no
basis explanation. PASS.

### Contradiction A: "more than doubled over that year" (abstract) against "barely moved in the year to May" (plate 02 title)

Reads as a contradiction. Both are true (July to July against May to May), and plate 02 is dated,
but a reader scrolling from the abstract hits the same quantity with the opposite result two
screens down, and plate 02 gives no reason for the difference (the sentences that explained it
were cut at Gate 2 because their support was cut at Gate 1). Worse, plate 02's title undercuts the
abstract's own take: "gold flatters it" rests on the doubling.

No cut to the abstract fixes this without removing the support for "gold flatters it". The
smallest fix is to hide plate 02 (item 3). With plate 02 hidden the abstract needs no change.

### Contradiction B: "owed as much to weaker US sales as to new buyers" (abstract) against "came from weaker US sales, not gold" (plate 01 title)

Reads as an inconsistency, not a flat contradiction. The abstract splits the credit; the title
gives all of it to weaker US sales. Plate 01's own body sides with the abstract ("sales elsewhere
reached their highest in data back to 1997"). The abstract was softened at Gate 2 for exactly this
reason and the title was left behind.

Trim, plate 01 title:

Before:
```
July's drop in the US export share came from weaker US sales, not gold.
```
After:
```
The US export share fell in July even as gold shipments dropped.
```

This is the Gate 2 alternative (flag F2-2), built only from text Gate 1 verified (precious-metals
exports fell 20.5% in July; the share fell 1.69 points). It keeps the "not gold" finding, which
holds on every basis, and drops the half that does not. 12 words, 64 characters, terminal period.
It is reworded, so it goes back through Gate 1 as a delta check per the re-gating rule; no new
figure is involved.

## 2. Tile line

PASS. It stands alone, carries one finding and two numbers, and matches the tile it sits on
(kicker "July balance", prefix "Trade balance", a balance bar chart). The tile reporting the
surplus while the abstract argues diversification is the normal split between the two surfaces:
the tile reports the print, the abstract answers the question. The closing clause ("as exports to
the US fell") is the bridge between them.

## 3. Plate 02: hide

Does not earn its place today. Four reasons, any two of which would be enough:

1. The body is one sentence that restates the title with two figures attached.
2. The title contradicts the abstract (Contradiction A) with no explanation left on the page.
3. The scatter draws about 100 sectors; the prose describes one dot.
4. The "C$5.0 billion" the chart draws has since been revised to about C$5.1 billion (Gate 1 F-C),
   so the plate is describing a superseded vintage.

How to hide. The page has no `hidden` flag; plates render from the `plates` array in
`src/pages/trade.astro`, and the plate index in the header and the item count in the structured
data are both derived from that array. So:

- Comment out the `plate-2` object (lines 53-71), leaving it in the file to restore on Oct 6.
- Plate numbers are hand-set strings, so renumber to avoid a visible gap: line 74 `number: "03"`
  -> `"02"`, line 101 `number: "04"` -> `"03"`. Leave the `id` values (`plate-3`, `plate-4`) alone
  so existing anchors keep working.
- `const plate2Data` (line 22) becomes unused; leave it or comment it out with the plate.

That is a block comment plus two string edits, not one line, but it is clean. Risk to check on the
build: any gate or visual baseline that expects four plates on /trade/. I did not verify this.

If hiding turns out not to be possible today, the fallback is to keep the Gate 2 text as is and
add `asOf: "May 2026"` to the plate (see item 6). That keeps the plate honest about its date but
does not resolve Contradiction A. I do not recommend it.

## 4. Plate 04: keep

Earns its place. The title turns the chart's fixed May window into the finding: the chart shows
the aluminum swing, the body says it was one month and gives the July reading. The July-to-July
sentence is dated in the prose and gives the reader the current picture the chart cannot. It also
supports the abstract's take rather than fighting it. PASS, with the as-of fix in item 6.

## 5. Jargon, method talk, promises the page no longer keeps

- No internal jargon, method talk or basis explanation in any redrafted prose.
- "Tariff-exposed sectors" (plate 04 `indicator` line 103 and `plateIndexLabel` line 104): keep.
  It names why these five sectors are grouped, it does not promise tariff analysis, and Gate 1
  re-verified it today (F-F). The body's "five export sectors" needs the label to explain the
  selection. If Jay wants zero tariff wording on the page, the neutral swap is "Five export
  sectors" in both places; that is a judgment call, not a required fix.
- Section kicker ("Exports, imports, and the terms by which Canada sells its work."): no tariff
  promise. Leave.
- `pageDescription` (line 125) ends "and trade reorientation under tariffs". Search copy, still
  topically accurate. Optional trim if zero tariff wording is wanted: cut " under tariffs".
- Plate 03 body at 32 words and two sentences is the right size for what it says. Nothing is
  filling a slot.

## 6. Leftover hand-set strings outside the redraft

`src/pages/trade.astro`:

- Plates 02 and 04 (objects starting lines 53 and 99) set no `asOf`. The layout then derives the
  stamp from the plate's live data (`panel-8` and `panel-7-alt`), which now runs to July 2026. The
  stamp would say July beside a chart drawn at May. Fix: add `asOf: "May 2026",` to plate 04 (and
  to plate 02 if it is kept). This is a hand-set override the layout already supports. Confirm on
  the rendered page.
- Line 57, plate 02 `indicator`: carries a math symbol and "NAPCS sub-chapter" in reader-facing
  text. Predates the redraft. Moot if the plate is hidden; fix when the plate returns.
- Line 77 `"Gold corridor"`: banned word. Already replaced by "Gold route" in the draft; make sure
  the paste includes it.
- Lines 85-86, plate 03 callout: the layout appends a derived date to `unitPrefix`, and `delta` is
  also a date ("July 2026"), so the callout may show the date twice. Predates the redraft (same
  with "May 2026"). Not blocking; check on the rendered page.
- Plate 03 callout `unitPrefix` and `indicator` (lines 76, 85) say "PGM". Predates the redraft;
  labels, not prose. Leave.

`src/data/sections.ts`:

- Lines 679, 680, 682, 732: covered by the draft's stamp table.
- Lines 688-689: the old `tileLineCitations` cite tables 12-10-0119-01 and 12-10-0121-01; the
  draft replaces the whole array. Make sure the old entries do not survive the paste.

`src/layouts/SectionLayout.astro` line 378: the structured-data modified date defaults to
2026-05-20 because `trade.astro` passes no `dateModified`. Not reader-visible, affects every
section page, out of scope here. Noting only.

## Summary of required changes before promote

1. Plate 01 title: retitle as above, then Gate 1 delta check.
2. Plate 02: hide (comment out, renumber 03 -> 02 and 04 -> 03).
3. Plate 04: add `asOf: "May 2026",`.

For Jay's veto, unchanged from earlier gates: the take moving from "Not really" to "It has started to".
