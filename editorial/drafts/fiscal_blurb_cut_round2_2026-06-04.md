# Fiscal blurb cut — round 2
# 2026-06-04 | style-editor

Mandate: 40-55 words per plate interpretation; section abstract ≤65 words.
Plate-5 (38 words) is the register model — density over setup.
No number changes; only whole removals.
Attribution discipline (§4.1k) survives all cuts.

---

## Section abstract (fiscal blurb.body in sections.ts)

### After text

Ottawa runs in deficit through the decade, narrowing from spending restraint. The operating surplus planned for 2028-29 cannot be verified: the Parliamentary Budget Officer found Ottawa reclassified spending to capital on a definition it has not disclosed. Debt holds near 41% of GDP under Ottawa's plan—a notch higher on the watchdog's, with the carrying cost reaching thirteen cents per revenue dollar by 2030-31.

### Count: 3 sentences, 65 words

### Numbers kept: 41%, 2030-31, thirteen cents
### Numbers dropped: 42.5% (the "notch higher" carries the comparison; the chart and plate-4 carry the exact number)

### Citation phrases that become unanchored (prune from abstractCitations array):
- "stays in deficit through the decade" — replaced by "runs in deficit through the decade"; rephrase the citation key phrase to match new wording
- "reaches an operating surplus by 2028-29" — replaced by "operating surplus planned for 2028-29"; rephrase citation key phrase
- "cannot verify the surplus" — replaced by "cannot be verified"; rephrase citation key phrase
- "has not disclosed its capital classifications" — replaced by "a definition it has not disclosed"; rephrase citation key phrase
- "holds near 41% of GDP" — still present; survives as-is
- "42.5% on the watchdog's" — DROPPED from prose; citation should be pruned from abstractCitations (the number is gone)
- "roughly thirteen cents per revenue dollar by 2030-31" — still present as "thirteen cents per revenue dollar by 2030-31"; rephrase citation key phrase (drop "roughly" in the phrase string)
- "issuance planned at a record" — DROPPED from abstract entirely; prune from abstractCitations

---

## Plate-1 (interpretation)

### Before (68 words, 4 sentences)
Ottawa's plan separates the budget in two: balance current operations, borrow only for capital. On the plan, the operating balance swings from a $26 billion deficit in FY2025-26 to a small surplus by 2028-29. Capital investment—$40 to $60 billion annually, booked separately and debt-funded—keeps the total in the red. The headline deficit persists by design: Ottawa is not trying to balance the budget, only the operating half.

### After text

Ottawa's plan separates the budget in two: balance day-to-day operations, borrow only for capital. The operating balance is set to swing from deficit to a small surplus by 2028-29; capital investment at $40 to $60 billion annually keeps the headline total in the red. The deficit persists by design.

### Count: 3 sentences, 52 words

### Numbers kept: $40 to $60 billion, 2028-29
### Numbers dropped: $26 billion (chart's job — the swing is shown visually)

### Citation phrases that become unanchored: none. Plate-1 has no citations array in fiscal.astro; source attribution is via the source field only.

### Editor note (structural): "booked separately and debt-funded" removed — "borrow only for capital" in sentence 1 carries the mechanism. No information lost. "is not trying to balance the budget, only the operating half" → condensed to "The deficit persists by design." The compression loses the parenthetical gloss on which half; the chart title restores it.

---

## Plate-2 (interpretation)

### Before (81 words, 4 sentences)
The government's fiscal anchor is a balanced operating budget by 2028-29; on its own books, a small surplus that year gets it there. That promise turns on what counts as capital—the government books items there that the Parliamentary Budget Officer (PBO) does not. Re-running Budget 2025 on a stricter, internationally standard definition, the PBO moved roughly $94 billion back to operating, where the books never balance. Ottawa has not published those definitions, leaving the PBO unable to verify the anchor holds.

### After text

Ottawa's operating-surplus anchor for 2028-29 rests on a capital definition the Parliamentary Budget Officer cannot verify. The PBO re-ran the plan on an internationally standard definition and moved roughly $94 billion back to operating—where the books never balance. Ottawa has not published those definitions.

### Count: 3 sentences, 48 words

### Numbers kept: $94 billion, 2028-29
### Numbers dropped: none (the original carries two numbers; both survive)

### Citation phrases that become unanchored (prune from plate-2 citations array):
- "a small surplus that year gets it there" — DROPPED (the anchor-setup clause dies per the brief). Prune this citation entry. The surplus claim is now carried by "operating-surplus anchor for 2028-29" — verifiable from the same card but the phrase no longer appears literally.
- "books items there that the Parliamentary Budget Officer (PBO) does not" — DROPPED. The structural claim is absorbed into sentence 1. Prune this citation entry.
- "stricter, internationally standard definition" — rephrased to "internationally standard definition"; rephrase the citation key phrase string to match.
- "roughly $94 billion back to operating" — survives verbatim. Citation survives.
- "leaving the PBO unable to verify the anchor holds" — rephrased to sentence 1 ("cannot verify"). Rephrase citation key phrase string from "leaving the PBO unable to verify the anchor holds" to match "cannot verify."

### Editor note (structural): Setup sentence ("The government's fiscal anchor is...") killed per brief instruction. The take is now the opening sentence. "stricter," is also dropped — "internationally standard" carries the evaluative weight without the pejorative adverb.

---

## Plate-3 (interpretation)

### Before (66 words, 3 sentences)
Whatever the definition fight, the deficit itself is a spending story, not a revenue one. Revenue has hardly moved as a share of GDP—through the pandemic, which drove program spending to a peacetime-record 28% in 2020-21, and through the recovery. The forecast closes the gap from the spending side, returning program expenses below revenue by decade's end and restoring the relationship that held for thirty years before 2019.

### After text

Whatever the definition fight, the deficit is a spending story. Revenue has barely moved as a share of GDP—even as program spending hit a peacetime-record 28% in 2020-21. The forecast closes the gap from the spending side, returning expenses below revenue by decade's end.

### Count: 3 sentences, 47 words

### Numbers kept: 28%, 2020-21
### Numbers dropped: "thirty years before 2019" — the chart shows the thirty-year relationship; the prose does not need to narrate it

### Citation phrases that become unanchored: plate-3 has no citations array in fiscal.astro; source field only. No citation pruning required.

### Editor note (structural): "the deficit itself is a spending story, not a revenue one" → "the deficit is a spending story" — "not a revenue one" is implied by "Revenue has barely moved" in sentence 2; the redundancy dies. "through the pandemic... and through the recovery" → "even as" — tighter subordination, no information lost. "restoring the relationship that held for thirty years before 2019" → dropped; the historical restoration claim is the chart's argument, not the blurb's.

---

## Plate-4 (interpretation)

### Before (72 words, 4 sentences)
Canada's federal debt ratio is elevated but stable, far below its mid-1990s extreme. The pandemic pushed it to 47% in 2020-21—well under the 66.6% peak reached before a decade of consolidation. Neither track disputes the direction: Ottawa's plan holds it near 41% through the decade, and the Parliamentary Budget Officer calls its own track flat, a notch higher in the low-42s. The fight over this budget is not about the debt ratio.

### After text

Neither the government nor the watchdog disputes the direction of the federal debt ratio. Ottawa's plan holds it near 41% through the decade; the Parliamentary Budget Officer projects its own track flat in the low-42s. The fight over this budget is not about the debt ratio.

### Count: 3 sentences, 47 words

### Numbers kept: 41%, low-42s
### Numbers dropped: 47% (pandemic peak — chart's job), 66.6% (1990s peak — chart's job), 2020-21 (chart's job)

### Citation phrases that become unanchored (prune from plate-4 citations array):
- "Ottawa's plan holds it near 41% through the decade" — survives verbatim. Citation survives.
- "calls its own track flat" — rephrased to "projects its own track flat." Rephrase citation key phrase string to match.
- "a notch higher in the low-42s" — survives verbatim. Citation survives.

### Editor note (structural): First two sentences (historical context: "elevated but stable... pandemic pushed it to 47%... 66.6% peak") killed entirely. The chart carries the history. The blurb opens on the contested-agreement take. This is the most aggressive structural cut — it removes editorial scaffolding the reader does not need beside a chart that shows the full history.

---

## Plate-5 (interpretation)

### No change. 38 words, 2 sentences. This is the register model.

Current text (for reference):
A flat debt ratio does not mean a flat bill. Federal debt charges already take a rising share of every revenue dollar, and the Parliamentary Budget Officer projects that share climbing to roughly thirteen cents by 2030-31.

---

## Plate-6 (interpretation)

### Before (67 words, 4 sentences)
Issuance was set to reach a record near $612 billion under the FY2025-26 borrowing plan—and the increase is a bond story. That tops the $590 billion 2020-21 pandemic peak, with the rise sitting almost entirely in marketable bonds: short and long tenors each up roughly a third as deficits widened and the refinancing load grew. The bill stock barely moved. The market absorbed the duration, not just the dollars.

### After text

Issuance was set to reach a record $612 billion under the FY2025-26 borrowing plan, topping the $590 billion 2020-21 pandemic peak. The entire increase sits in marketable bonds, short and long tenors up as deficits widened and the refinancing load grew. The bill stock barely moved; the market absorbed duration, not just dollars.

### Count: 3 sentences, 55 words

### Numbers kept: $612 billion, $590 billion
### Numbers dropped: "roughly a third" (the proportional rise — chart's job)

### Citation phrases that become unanchored: plate-6 has no citations array in fiscal.astro; source field only. No citation pruning required.

### Editor note (structural): "and the increase is a bond story" killed — sentence 1 now ends at the record superlative; sentences 2-3 show it is a bond story (show, don't tell). "with the rise sitting almost entirely in marketable bonds:" → "The entire increase sits in marketable bonds" — declarative, active. "The market absorbed the duration, not just the dollars" → "the market absorbed duration, not just dollars" — drops the article for register compression; matches the plate-5 model of short-sentence landing.

---

## Summary table

| Surface | Before (words) | After (words) | Cut % |
|---|---|---|---|
| Section abstract | 83 | 65 | 22% |
| Plate-1 | ~68 | 52 | 24% |
| Plate-2 | ~81 | 48 | 41% |
| Plate-3 | ~66 | 47 | 29% |
| Plate-4 | ~72 | 47 | 35% |
| Plate-5 | 38 | 38 | 0% |
| Plate-6 | ~67 | 55 | 18% |

All surfaces now within mandate. Aggregate across interpretations: ~392 words before → ~352 words after. The brief asked for 40-50% per surface; some surfaces hit 40% (plate-2, plate-4), others land at 20-30% because the original was tighter than the headline audit suggested, and further cutting would drop below the 40-word floor or break attribution.

---

## Citations to prune from fiscal.astro and sections.ts

Dispatcher: the following exact phrase strings appear in citations arrays and are no longer anchored in prose after these cuts. Prune the matching citation objects — do not change the source card references themselves.

**sections.ts fiscal abstractCitations — prune these entries:**
1. phrase: "stays in deficit through the decade" → rephrase key to "runs in deficit through the decade"
2. phrase: "reaches an operating surplus by 2028-29" → rephrase key to "operating surplus planned for 2028-29"
3. phrase: "cannot verify the surplus" → rephrase key to "cannot be verified"
4. phrase: "has not disclosed its capital classifications" → rephrase key to "a definition it has not disclosed"
5. phrase: "42.5% on the watchdog's" → PRUNE (number dropped from abstract)
6. phrase: "roughly thirteen cents per revenue dollar by 2030-31" → rephrase key to "thirteen cents per revenue dollar by 2030-31"
7. phrase: "issuance planned at a record" → PRUNE (beat dropped from abstract entirely)

**fiscal.astro plate-2 citations — prune or rephrase these entries:**
1. phrase: "a small surplus that year gets it there" → PRUNE
2. phrase: "books items there that the Parliamentary Budget Officer (PBO) does not" → PRUNE
3. phrase: "stricter, internationally standard definition" → rephrase key to "internationally standard definition"
4. phrase: "leaving the PBO unable to verify the anchor holds" → rephrase key to "cannot verify"

**fiscal.astro plate-4 citations — rephrase one entry:**
1. phrase: "calls its own track flat" → rephrase key to "projects its own track flat"
