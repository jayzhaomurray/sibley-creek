# Gate 3 verdict (surface fit) -- monetary redraft, 2026-10-03

Reviewed: Gate 2 text in `monetary_draft.md`, the monetary block in `src/data/sections.ts` (lines 448-531), all of
`src/pages/monetary.astro`, and the four chart components under `src/components/charts/policy/`.
Nothing under `src/` and nothing in `monetary_draft.md` was edited.

Overall: PASS, conditional on trims T1 to T4 below. All are cuts or word swaps; none adds a claim.
T1 and T2 change cited text, so their citation `phrase` strings need the matching edit (given with each).

## Verdict per surface

| Surface | Verdict | Reason |
|---|---|---|
| Stamps (heroKicker, latest release, updatedAt, plate 1 asOf) | PASS | September decision is still the latest; next is October 28. |
| Tile line | PASS with trim T1 | Ends on a preposition with no object; reads as cut off on a cold homepage read. |
| Section abstract | PASS | Answers the header question in five words, then gives the two facts behind it. Plates extend it; none contradicts it. |
| Plate 1 | PASS | Title is the decision's finding; the October 28 line is useful to this reader, not filler. |
| Plate 2 | PASS with trim T2 | Third sentence narrates a series this chart does not draw. |
| Plate 3 | PASS | Title is exactly what the chart shows. |
| Plate 4 | PASS with flag F1 | Right level of detail (two sentences, both visible on the chart). Callout disagrees with the title. |
| Plate 5 | PASS with trim T3, flag F2 | Callout carries an internal date tag. The overnight repo rate sentence stays. |

## Notes on the five checks

1. Abstract and plates. The abstract's take ("on hold, with the pressure pointing up") is carried by plates 1 and 3 and
   supported by plate 2. Plate 3 repeats the abstract's 3.27% and 102 bps, which is correct: the abstract is the
   summary, plate 3 is where the chart is. Plates 4 and 5 are outside the abstract; that is fine, since the header
   question is about stance and the balance sheet is supporting detail.
2. Tile line. A reader can work out that the yield sits above 2.25%, but the sentence stops mid-thought. "Higher" is a
   complete comparative and needs no object. See T1.
3. Plates 4 and 5. Not implementation detail. Each is two sentences, each number is visible on its chart, no cause is
   asserted. The overnight repo rate sentence on plate 5 is not drawn on that chart, but it is the one line that tells
   this page's reader why the plumbing matters (the rate the Bank targets is trading above target). Keep it. Without
   it the body only restates the title.
4. Jargon. No internal terms, method talk or process statements in the redraft. "Repos", "GoC", "BoC", "Fed" are said
   aloud by this reader. Two leftovers in source lines and one in a callout are method talk; see T3, S1, S2.
5. Stale leftovers: see the last section.

## Trims (exact text)

**T1. Tile line** (`sections.ts`, tileLine)
- Before: `BoC held at 2.25% a seventh time, but 2y GoCs at 3.27% sit a full point above.`
- After: `BoC held at 2.25% a seventh time, but 2y GoCs at 3.27% sit a full point higher.`
- 79 characters, 17 words; inside the 90-character and 20-word caps.
- Citation phrase `a full point above` becomes `a full point higher`.

**T2. Plate 2 body, cut the third sentence** (`monetary.astro`, plate-2)
- Cut: `The Canada-US 2-year spread has widened too, to -151 bps on October 1; before this September it had not been that wide since March 2025.`
- Body after: `The BoC-Fed policy gap stands at -175 bps, 25 bps wider than in August. The Fed raised its target range to 3.75 to 4.00% on September 16, its first change since a cut in December 2025, while the BoC held at 2.25% for a seventh straight decision.`
- Remove the two citation entries for `-151 bps on October 1` and `before this September it had not been that wide since March 2025`.
- With the Oct 1 figure gone, set plate 2 `asOf` to `Sep 2026` (not `Oct 1, 2026`), matching the chart's last monthly point.
- Why: the chart draws the two policy rates and their gap only. The 2-year spread still shows in the section's
  headline numbers strip.

**T3. Plate 5 callout delta**
- Before: `Above Jan-2025 $50-70 bn range`
- After: `Above $50-70 bn operating range`
- Why: "Jan-2025" is the date of the speech that set the range; a reader cannot decode it.

**T4. Plate 2 source line** (`monetary.astro` lines 73-75, not in the redraft)
- Before: `Bank of Canada Valet (overnight rate target, monthly); FRED DFF (fed funds effective, daily resampled to monthly last). Canada-US 2y spread derived in chart, percentage points.`
- After: `Bank of Canada Valet (overnight rate target); Federal Reserve (federal funds target range, upper bound).`
- Why: the chart does not draw a 2-year spread, and per Gate 1 it plots the top of the Fed target range, not the
  effective rate. "Daily resampled to monthly last" and "derived in chart" are method talk. Fact-checker to confirm
  the series wording in the delta check.

## Flags (larger than a trim; recommendations)

**F1. Plate 4 callout contradicts its title.** Title says repos are moving the balance sheet; the callout still
features the bond share (56%). Recommended swap, using only numbers already in the body:
```ts
    callout: {
      value: "$65.9 bn",
      unit: "Repos",
      delta: "Up $18.4 bn in two weeks to Sep 30",
      direction: "neutral",
    },
```
Not a blocker; ship as drafted if the dispatcher prefers no callout change today.

**F2. Plate 5 title treats $50 to 70 billion as the Bank's current range.** Gate 1 did not look for a revision later
than the January 2025 speech. One search by the fact-checker before ship; if revised, the title and callout fail.

**F3. Plates 4 and 5 describe one event from two sides** (repos up $18.4 billion, settlement balances up $20.4 billion,
same two weeks) without saying so. A later writer pass could link them in one clause; it needs a sourced cause, so it
is not for today.

**F4. `blurb.date`.** Keep `Oct 3, 2026`.

## Stale strings left on the page outside the redraft

| # | Location | Current | Fix |
|---|---|---|---|
| S1 | `monetary.astro` L73-75, plate 2 `source` | Names a 2-year spread the chart does not draw and the wrong Fed series | T4 above |
| S2 | `monetary.astro` L49, plate 1 `source` | `Bank of Canada rate decision and Monetary Policy Report, latest vintage.` | Cut `, latest vintage` (September had no report; "vintage" is pipeline talk) |
| S3 | `monetary.astro` L68, plate 2 `asOf` | `Jun 2026` | `Sep 2026` (see T2; draft says `Oct 1, 2026`) |
| S4 | `monetary.astro` L97, plate 3 `source` | `...MPR market-implied curve, latest vintage.` | Already replaced in the draft's paste block; confirm it is pasted |
| S5 | `sections.ts` L477-479 code comment | `currently 2.25% Apr 2026` | Not reader-facing; no action |

Nothing else on the page is hand-set to July values: plates 3, 4 and 5 have no hand-set `asOf` (derived from data),
chart components carry no dated annotations, and the neutral-range band on the plate 1 chart (2.25 to 3.25%) is
still current. Every other July or August string (L38-46, L53-59, L79-85, L93-105, L113-132, L140-162, and
`sections.ts` L455-474, L518-529) sits inside a block the draft replaces whole.

Off this page: `src/pages/policy.astro` plate 7 still cites the Fed range as 3.50 to 3.75% (Gate 1 already noted it).
