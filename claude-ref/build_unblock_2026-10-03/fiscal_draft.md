# Fiscal section redraft -- build unblock 2026-10-03

Writer draft. Nothing under `src/` was edited. Sole fact source: `claude-ref/build_unblock_2026-10-03/fiscal_facts.md`.
Status 2026-10-03: Gate 1 (fact-check) and Gate 2 (style) done; verdicts at the foot of this file. Gate 3 (surface fit) done 2026-10-03: PASS on all surfaces, no copy edits; verdict at the foot of this file. Sections A, B4 and C2 hold the final paste-ready text. The abstract's opener was reworked at Gate 2, so sections "NEW CLAIMS INTRODUCED" and "Flags" below describe the writer's original draft and are kept as history only.

---

## A. Splash tile line

File: `src/data/sections.ts`, `slug: "fiscal"` block, `tileLine` (~line 547)

Current (71 characters):

```
The federal deficit reached $55.3B through March, wider than last year.
```

New, FINAL after Gate 1 delta (80 characters by script, 13 words; brief limit 80). Supersedes the 73-character "The federal deficit was $5.1B through July, narrower than a year earlier.":

```
This fiscal year's deficit was $5.1B through July, narrower than a year earlier.
```

Replacement text:

```ts
    tileLine:
      "This fiscal year's deficit was $5.1B through July, narrower than a year earlier.",
    tileLineCitations: [
      { phrase: "$5.1B through July", source: "pipeline:dof:fiscal_monitor", note: "DoF Fiscal Monitor July 2026 (published 2026-09-25): budgetary balance, April to July FY2026-27 = -C$5,138M, rounded to $5.1B. 'This fiscal year' = FY2026-27, April 2026 to March 2027." },
      { phrase: "narrower than a year earlier", source: "pipeline:dof:fiscal_monitor", note: "DoF Fiscal Monitor July 2026 Table 1: April to July FY2026-27 deficit C$5,138M versus C$7,787M for April to July FY2025-26; 7,787 - 5,138 = 2,649, i.e. C$2.6bn narrower." },
    ],
```

---

## B. Section abstract and stamps

File: `src/data/sections.ts`, `slug: "fiscal"` block

### B1. Code comment + `updatedAt` (~lines 540-541)

Current:

```ts
    // Fiscal Monitor Mar 2026 is the latest monthly issue in the pipeline.
    updatedAt: Date.UTC(2026, 5, 16, 16, 5),
```

New:

```ts
    // Fiscal Monitor July 2026 (published 2026-09-25) is the latest monthly issue in the pipeline.
    updatedAt: Date.UTC(2026, 8, 25, 16, 5),
```

Note (Gate 1 correction, 2026-10-03): the writer's placeholder `Date.UTC(2026, 9, 3, 17, 0)` was replaced with the Fiscal Monitor's publication date, 2026-09-25 (month index 8 = September; page metadata `dcterms.issued` = 2026-09-25, confirmed on a live fetch). `updatedAt` tracks the data release, not the prose (`scripts/check_prose_vintage.mjs` header; `blurb.date` carries the prose vintage and stays Oct 3). The page publishes no time of day, so 16:05 UTC is the time-of-day convention the block already used, not an observed publication time.

### B2. `heroKicker` (~line 544)

Current:

```ts
    heroKicker: "Fiscal Monitor Mar '26",
```

New:

```ts
    heroKicker: "Fiscal Monitor Jul '26",
```

### B3. `blurb.date` (~line 593)

Current:

```ts
      date: "Jun 16, 2026",
```

New:

```ts
      date: "Oct 3, 2026",
```

### B4. `blurb.body` (~line 595)

Current (324 characters):

```
Fiscal policy is modestly stimulative. The March Fiscal Monitor put the FY2025-26 deficit at $55.3 billion on a cash basis, while the Spring Economic Update estimate is $66.9 billion, up from $36.3 billion the year before. Debt is still expected to sit near 41.1% of GDP, but public debt charges are taking 10.6% of revenue.
```

New, FINAL after Gate 2 (301 characters, 48 words, 3 sentences):

```
Fiscal policy is holding roughly steady. Ottawa projects a $65.3 billion deficit this fiscal year, close to last year's $66.9 billion. Through July the shortfall was $5.1 billion, narrower than a year earlier as revenue outgrew program spending, but four months settle little and July alone was wider.
```

Structure: take (the stance is roughly unchanged) / mechanism (the planned full-year deficit is about the size of last year's) / landing (the year to date is running narrower, but four months, with the latest one wider, do not change the read). Three dollar figures: $65.3 billion, $66.9 billion, $5.1 billion.

Replacement text:

```ts
    blurb: {
      kind: "last",
      date: "Oct 3, 2026",
      body:
        "Fiscal policy is holding roughly steady. Ottawa projects a $65.3 billion deficit this fiscal year, close to last year's $66.9 billion. Through July the shortfall was $5.1 billion, narrower than a year earlier as revenue outgrew program spending, but four months settle little and July alone was wider.",
    },
    abstractCitations: [
      { phrase: "holding roughly steady", source: "derived", note: "Analytical read on the planned CHANGE in the headline deficit: FY2026-27 projection C$65.3bn versus FY2025-26 estimate C$66.9bn (Spring Economic Update 2026 Annex 1 Table A1.7, same vintage), 66.9 - 65.3 = C$1.6bn, 1.9% versus 2.1% of GDP. Takes no view on whether a deficit of that size is loose. Gate 1 caveat: on the balance before net actuarial losses the projection widens, -55.3 to -65.2 (about 0.3 points of GDP); adding back the C$6.7bn reclassified out of program expenses it is -62.0 to -65.2. The claim holds on the headline balance and on the reclassification-adjusted balance, not on the unadjusted before-actuarial-losses balance (Gate 1 delta verdict, item 1)." },
      { phrase: "$65.3 billion deficit this fiscal year", source: "pipeline:dof:fiscal_reference_tables", note: "Spring Economic Update 2026 Annex 1 Table A1.7 budgetary balance row: FY2026-27 = -C$65.3bn (frt_federal_balance_total). 'This fiscal year' = FY2026-27, April 2026 to March 2027." },
      { phrase: "last year's $66.9 billion", source: "pipeline:dof:fiscal_reference_tables", note: "Spring Economic Update 2026 Annex 1 Table A1.7 budgetary balance row, same vintage: FY2025-26 estimate = -C$66.9bn. An estimate, not final until the Annual Financial Report." },
      { phrase: "$5.1 billion", source: "pipeline:dof:fiscal_monitor", note: "DoF Fiscal Monitor July 2026 (published 2026-09-25): budgetary balance, April to July FY2026-27 = -C$5,138M." },
      { phrase: "narrower than a year earlier", source: "pipeline:dof:fiscal_monitor", note: "DoF Fiscal Monitor July 2026 Table 1: April to July FY2026-27 deficit C$5,138M versus C$7,787M for April to July FY2025-26; 7,787 - 5,138 = 2,649, i.e. C$2.6bn narrower." },
      { phrase: "revenue outgrew program spending", source: "pipeline:dof:fiscal_monitor", note: "DoF Fiscal Monitor July 2026, April to July: revenues C$175,469M versus C$163,443M, up 7.4%; program expenses excluding net actuarial losses C$158,968M versus C$151,293M, up 5.1%. Growth rates are the published-page figures." },
      { phrase: "four months", source: "derived", note: "The fiscal year starts April 1; the July 2026 Fiscal Monitor covers April, May, June, July = 4 months." },
      { phrase: "July alone was wider", source: "derived", note: "DoF Fiscal Monitor July 2026: July 2026 deficit C$4,768M versus July 2025 deficit C$1,512M; 4,768 - 1,512 = C$3,256M wider." },
    ],
```

Writer's pre-Gate-2 body, superseded (315 characters), kept for the record:

```
Fiscal policy is still loose, but it has stopped loosening. Ottawa projects a $65.3 billion deficit this fiscal year, slightly below last year's, and through July the shortfall was $5.1 billion against $7.8 billion a year earlier as revenue outgrew program spending. Four months settle little: July alone was wider.
```

### B5. Alternative openers (SUPERSEDED at Gate 2: the opener now carries the stance of alternative 1, reworded; kept as history)

Writer's original recommended opener: "Fiscal policy is still loose, but it has stopped loosening."
Why this one: it separates level from direction, which is what the evidence does. The level claim rests on a deficit near 2% of GDP; the direction claim rests on both the projection and the realized year-to-date figures. It does not need four months of data to hold, because the projection alone carries it.

Alternative 1, neutral stance:

```
Fiscal policy is on hold: this year's deficit is planned at about the size of last year's.
```

Supports it: $65.3 billion projected versus $66.9 billion. Takes no view on whether a deficit of that size is loose. Safest reading; weakest take. If used, rewrite sentence 2 to drop the repeated comparison (for example: "Ottawa projects $65.3 billion against last year's $66.9 billion, and through July the shortfall was ...").

Alternative 2, tightening stance:

```
Fiscal policy is tightening at the margin, with the deficit running below last year's pace.
```

Supports it: year-to-date $5.1 billion versus $7.8 billion; projection 1.9% versus 2.1% of GDP. Risk: this leans hardest on four months of data in a year where the latest month was wider and where last year more than half the preliminary deficit landed in March alone. I do not recommend it.

Swapping an opener changes the body length: alternative 1 adds 31 characters (346 total, over the 324 budget unless sentence 2 is trimmed as noted); alternative 2 adds 32 (347 total, over budget; would need a cut).

---

## C. Chart plates, `src/pages/fiscal.astro`

Read in full. **No plate needs redrafting.** None of the five plates describes the March 2026 Fiscal Monitor or FY2025-26 year-to-date results as the latest reading; all five are built on Spring Economic Update 2026 projections or Parliamentary Budget Officer documents, which the fact pack confirms are still the current vintage (no Budget 2026, no Annual Financial Report, no new PBO outlook since June 4).

Left untouched:

| Plate | Title | Why it stands |
|---|---|---|
| 01 Operating balance | "Ottawa plans to balance day-to-day spending and borrow only for capital." | Spring Economic Update projections; unchanged vintage. |
| 02 Capital, disputed | "The budget watchdog says the government misclassifies operating costs as capital." | PBO recast of Budget 2025; no newer PBO projection. |
| 03 Revenue vs spending | "As spending falls, revenues hold flat." | Spring Economic Update projections to 2030-31; unchanged. |
| 04 Debt and carrying cost | "Debt rises modestly, but servicing costs climb faster." | Annual series; vintage unchanged (but see flag 3). |
| 05 Issuance by instrument | "Gross issuance is set to ease." | 2026-27 plan versus 2025-26; "last year" still reads correctly. |

Also left: `latestReleaseLabel="Spring Update, April 2026"` on the `SectionLayout` call. It names the vintage the plates are built on and carried that value while the March Fiscal Monitor was the latest monthly issue, so it is not stale by the same test. See flag 4.

### C2. Plate 4 minimal fix (added at Gate 2 from Gate 1 open flag 3)

File: `src/pages/fiscal.astro`, `id: "plate-4"` block, `interpretation` (line 143) and first `citations` entry (line 146). Not applied; exact replacement recorded here.

`interpretation`, old:

```
Debt-to-GDP sits at 41.2% and is set to rise by about 1 to 2 percentage points. But debt servicing costs will rise faster: interest payments will rise from 10 to 13 cents per revenue dollar by 2030-31.
```

`interpretation`, new:

```
Debt-to-GDP sits near 41% and is set to rise by about 1 to 2 percentage points. But debt servicing costs will rise faster: interest payments will rise from 10 to 13 cents per revenue dollar by 2030-31.
```

First citation entry, old:

```ts
      { phrase: "Debt-to-GDP sits at 41.2%", source: "pipeline:fiscal:panel-9", note: "frt_federal_debt_pct_gdp: FY2024-25 last actual is 41.2%." },
```

First citation entry, new:

```ts
      { phrase: "Debt-to-GDP sits near 41%", source: "pipeline:fiscal:panel-9", note: "frt_federal_debt_pct_gdp: FY2025-26 estimate is 41.1%, rounded in prose to near 41%." },
```

The other three citation entries on the plate do not quote the changed words and stay as they are.

---

## Source list

All from `fiscal_facts.md`: section 1 (July 2026 Fiscal Monitor table), section 2 (FY2025-26 figures, no newer budget), section 3 (FY2026-27 projections), section 5 (stance arithmetic), "What changed since the old copy".

Cards: none cited. The two new pending cards were not used. The existing card `claim_dof_deficit_larger_than_handoff_below_pandemic` is no longer cited anywhere in the fiscal block, because the redraft makes no claim about last year's widening.

## NEW CLAIMS INTRODUCED (all need Gate 1)

1. April-to-July FY2026-27 deficit $5.1B (tile line and abstract).
2. "narrower than a year earlier" / "$7.8 billion a year earlier".
3. "$65.3 billion deficit this fiscal year" (projection, FY2026-27).
4. "slightly below last year's" ($65.3B versus $66.9B).
5. "revenue outgrew program spending" (7.4% versus 5.1%).
6. "Four months" (countable: April, May, June, July).
7. "July alone was wider" ($4.8B versus $1.5B).
8. Stance: "still loose" (level, 1.9% of GDP) and "has stopped loosening" (direction).

## Flags

1. **"Still loose" is a judgment, not a verified fact.** The pack verifies the deficit level (1.9% of GDP) and says a level argument "remains available"; it does not verify that the level is stimulative. The citation note says so. Publisher's call; alternatives in B5.
2. **Measures announced since the Spring Economic Update** (the September deduction measure, August tariff-response support, fuel-tax relief extension) may not be in the $65.3 billion projection. The pack could not verify this, so the draft says "projects" and asserts nothing about them. If they are outside the baseline, "has stopped loosening" weakens. Budget 2026 timing is also unverified and not mentioned.
3. **Plate 04 seam (pre-existing, not introduced by this release).** "Debt-to-GDP sits at 41.2%" is the FY2024-25 figure on the older GDP basis; on the Spring Economic Update's own basis that year is 40.7% and FY2025-26 is 41.1%. Not a Fiscal Monitor claim, so left alone under this brief, but worth a separate look.
4. **Page stamp versus tile.** `latestReleaseLabel` says "Spring Update, April 2026" while `heroKicker` will say "Fiscal Monitor Jul '26". And the tile line ($5.1B year to date) will sit above a headline print of -$66.9B (FY2025-26 estimate). Neither is wrong; both may read oddly side by side.
5. **Citation mechanics.** The 7.4% and 5.1% growth rates and the program-expense figure exist only on the published page, not in the repo data, so the `pipeline:dof:fiscal_monitor` citation for "revenue outgrew program spending" cannot be resolved from the pipeline. "Four months" is cited as `derived` with the enumeration in the note; there is no enumeration card for it. The FY2026-27 values are cited to `pipeline:dof:fiscal_reference_tables` as the pack suggests, although the figure originates in the Spring Economic Update.
6. **`updatedAt` time of day** is a placeholder (17:00 UTC); adjust at wiring. [Resolved at Gate 1: now `Date.UTC(2026, 8, 25, 16, 5)`, see B1.]
7. Character counts were done by hand; re-run the length gate. [Resolved at Gate 1: counts confirmed by script, see verdict.]

---

## Gate 1 verdict (fact-check, 2026-10-03)

Sources checked first-hand today: July 2026 Fiscal Monitor on canada.ca (live fetch: highlights sentences, Table 1, publication date; Chart 2 text and page metadata read from the copy saved at 16:51 UTC, because canada.ca reset my later direct connections); Spring Economic Update 2026 Annex 1 Table A1.7 on budget.canada.ca (live fetch); budget.canada.ca home and `/2026/` (live fetch); repo `data/raw/dof_fiscal_*.csv`, `data/raw/federal_budget_balance.csv`, `data/processed/federal_budget_ytd.csv`, `data/derived/frt_*.csv`.

### Verdict per surface

| Surface | Verdict |
|---|---|
| A. Tile line | PASS |
| B4. Abstract, sentences 2 and 3 (all numbers, periods, comparisons) | PASS |
| B4. Abstract, sentence 1 ("still loose, but it has stopped loosening") | PASS WITH FLAG: holds on the headline balance, does not hold on the balance before net actuarial losses. Publisher decision, see open flag 1. |
| B1-B3 stamps | PASS after one correction (`updatedAt`) |
| Citation arrays | PASS |
| C. Plates (untouched) | No plate cites the Fiscal Monitor (confirmed). One pre-existing inconsistency on plate 4, see open flag 3. |

### Claim-by-claim

| Claim | Primary figure | Result |
|---|---|---|
| "$5.1B through July" / "$5.1 billion" | April to July 2026-27 budgetary balance -5,138 $M (Table 1); repo `dof_fiscal_ytd_balance` 2026-07-31 = -5138 | Verified |
| "$7.8 billion a year earlier" | April to July 2025-26 = -7,787 $M (Table 1). Repo `federal_budget_ytd` shows -7788 (cumulated rounded months); both round to 7.8 | Verified |
| "narrower than a year earlier" | 7,787 - 5,138 = 2,649 $M narrower. The prose never states the gap, so the 2.6 (unrounded) versus 2.7 (7.8 - 5.1) rounding question does not arise in reader copy | Verified |
| "$65.3 billion deficit this fiscal year" | Table A1.7 budgetary balance 2026-27 = -65.3; repo `frt_federal_balance_total` = -65.3. Restated as (65,345) $M in the July Fiscal Monitor, Chart 2 | Verified |
| "slightly below last year's" | Same table, same vintage: 2025-26 = -66.9. 66.9 - 65.3 = 1.6, i.e. 2.4% smaller; 2.1% versus 1.9% of GDP. "Slightly" is fair. Both are estimates; 2025-26 is not final until the Annual Financial Report | Verified |
| "revenue outgrew program spending" | Revenues 163,443 to 175,469 = +12,026 = +7.36%. Program expenses excluding net actuarial losses 151,293 to 158,968 = +7,675 = +5.07%. Page states 7.4 and 5.1 per cent. Holds in per cent and in dollars, and also against total expenses (+5.5%) | Verified |
| "Four months" | April, May, June, July = 4 | Verified |
| "July alone was wider" | July 2026 -4,768 versus July 2025 -1,512; 3,256 $M wider. Also true read as July versus the prior three months combined (-370) | Verified |
| Tile framing direction | Year-to-date gap was 5.9bn narrower through June and 2.6bn narrower through July: shrinking but still narrower. "Narrower" matches the data; the abstract discloses July | Aligned |

### Corrections applied

1. `updatedAt`: `Date.UTC(2026, 9, 3, 17, 0)` replaced with `Date.UTC(2026, 8, 25, 16, 5)` (publication date 2026-09-25; time of day not published, prior convention kept).

No digit, period or phrase corrections were needed.

### Citation and length mechanics (computed by script, gate regexes from `scripts/source_audit.mjs`)

- Tile line: 73 characters, 12 words, 1 sentence. Caps: 90 characters, 20 words, 1 sentence. Within budget.
- Abstract: 315 characters, 50 words, 3 sentences. Caps: 105 words, 5 sentences (soft target 45-75 words, 2-3 sentences). Within budget, no warning. The gate has no character cap for abstracts; the "324" in B5 is the old copy's length, not a budget.
- All 11 citation phrases are exact substrings of their prose, each occurring once.
- All sources are accepted forms: `pipeline:dof:fiscal_monitor`, `pipeline:dof:fiscal_reference_tables` (both already used in the live fiscal block), `derived`. No `card:` source, so nothing from `_pending/` is cited.
- Draft text is ASCII-only.

### Open flags

1. **"Stopped loosening" depends on which balance is read (publisher decision).**
   - Supports it: headline deficit 66.9 to 65.3 (2.1% to 1.9% of GDP); year to date 7.8 to 5.1, and 6.4 to 3.5 before net actuarial losses.
   - Does not support it: Table A1.7 "budgetary balance before net actuarial losses" goes from -55.3 in 2025-26 to -65.2 in 2026-27, about 9.9bn WIDER (the Fiscal Monitor's Chart 2 shows the same pair: 55,301 and 65,215). The headline narrows only because net actuarial losses drop from 11.6 to 0.1. Of that 11.6, the update says 6.7 was reclassified out of direct program expenses; adding it back still leaves 62.0 to 65.2, wider. Program expenses are projected up 4.5% (512.8 to 536.1; 15.8% to 15.9% of GDP) against revenues up 3.5% (511.5 to 529.6; 15.8% to 15.7% of GDP).
   - So: a headline deficit roughly flat year over year is consistent with "stopped loosening"; the underlying projection is not. "Still loose" rests only on the level (a deficit of 1.9% of GDP); no number here tests it either way.
   - If the publisher wants an opener that survives both readings, the writer's alternative 1 ("on hold ... about the size of last year's") does. Not rewritten here.
   - The citation note for "it has stopped loosening" is accurate as far as it goes but omits the before-actuarial-losses figures; add them if the opener stays.
2. **Nothing official supersedes $65.3 billion.** Budget 2026 is not tabled (`budget.canada.ca/2026/` returns 404; no fall statement under the new calendar). The July Fiscal Monitor, published 2026-09-25, still carries (65,345) sourced to the Spring Economic Update. "Ottawa projects" is acceptable. The September 15 deduction measure (stated cost 36bn over five years from 2026-27) postdates the projection; no official document restates the deficit to include it.
3. **Plate 4, pre-existing, not introduced by this draft.** "Debt-to-GDP sits at 41.2%" is the 2024-25 figure on the older GDP basis. The section's own headline print shows 41.1% (2025-26 estimate), and the update's consistent basis gives 40.7 / 41.1 / 41.5 for 2024-25 / 2025-26 / 2026-27. From 41.2 the stated rise would be 0.7 to 1.4 points, not "about 1 to 2". Minimal fix: change the prose and its citation phrase to "Debt-to-GDP sits near 41%" and repoint the note to the 2025-26 estimate of 41.1%; the rest of the sentence then matches its own note (0.8 and 1.9 points). Softer, same plate: "from 10 to 13 cents" starts from 2024-25 (10.5); the current-year readings are 10.6 estimated, 11.1 projected, 11.4 realized April to July.
4. **Plate 3 sits in mild tension with the abstract, not contradiction.** Title "As spending falls, revenues hold flat." describes shares of GDP to 2030-31; the abstract's "revenue outgrew program spending" describes four realized months in dollars. No fix required.
5. **Splash side effect of the stamp.** `updatedAt` selects the homepage hero (maximum across sections). The next-latest is 2026-09-04, so with either 2026-09-25 or the writer's 2026-10-03 the fiscal section becomes the hero, charting `fiscal-ytd-balance` (-66.9bn, 2025-26 estimate) above a tile line about 5.1bn. Confirm that is wanted before wiring.
6. **Not re-verified today:** the PBO note of 2026-09-24 on the operating-budget anchor was checked at highlights level only (no new figures there); plate 2's 94bn was not re-opened.

---

## Gate 2 verdict (style polish, 2026-10-03)

Scope: tile line, section abstract, plate 4 minimal fix. Voice and structure only. No fact, number, date or comparison was added; every figure in the final text appears in the writer's draft or the Gate 1 verdict. Nothing under `src/` was edited.

### Final text

Tile line (unchanged):

```
The federal deficit was $5.1B through July, narrower than a year earlier.
```

Abstract:

```
Fiscal policy is holding roughly steady. Ottawa projects a $65.3 billion deficit this fiscal year, close to last year's $66.9 billion. Through July the shortfall was $5.1 billion, narrower than a year earlier as revenue outgrew program spending, but four months settle little and July alone was wider.
```

### Counts

Counted by hand, character by character (this role has no script runner). Re-run the length gate at wiring.

| Surface | Characters | Limit in brief | Words | Sentences |
|---|---|---|---|---|
| Tile line | 73 | 80 | 12 | 1 |
| Abstract | 301 (40 + 93 + 166, plus 2 spaces) | 324 | 48 | 3 |

Abstract word target is 45 to 75; 48 lands inside it. Before: 315 characters, 50 words.

### Changes, before and after

1. **Opener (non-mechanical, required by the brief).**
   - Before: "Fiscal policy is still loose, but it has stopped loosening."
   - After: "Fiscal policy is holding roughly steady."
   - Why: Gate 1 found "stopped loosening" fails on the balance before net actuarial losses. The level judgment "still loose" goes with it: the required stance takes no view on the level, and Gate 1 noted no number tests it. Also removes the balanced two-part flourish. Does not use "on hold" (monetary abstract opens with it) or "tightening".
2. **Sentence 2 (non-mechanical).**
   - Before: "Ottawa projects a $65.3 billion deficit this fiscal year, slightly below last year's, and through July ..."
   - After: "Ottawa projects a $65.3 billion deficit this fiscal year, close to last year's $66.9 billion."
   - Why: this sentence is now the mechanism for the take, so it stands on its own and shows the comparison once, with both figures. "Slightly below" argued direction, which the new opener no longer claims; "close to" argues size. $66.9 billion is the Gate 1 verified FY2025-26 estimate.
3. **Year-to-date clause (non-mechanical: one number cut).**
   - Before: "through July the shortfall was $5.1 billion against $7.8 billion a year earlier as revenue outgrew program spending."
   - After: "Through July the shortfall was $5.1 billion, narrower than a year earlier as revenue outgrew program spending,"
   - Why: adding $66.9 billion would have made four dollar figures; the guide asks for a take grounded by few numbers. $7.8 billion is the one the argument needs least. The direction is kept in words, matching the tile line.
4. **Landing (mechanical).**
   - Before: "Four months settle little: July alone was wider."
   - After: "... but four months settle little and July alone was wider."
   - Why: joined to the year-to-date sentence so the caveat qualifies the fact it belongs to, and the abstract stays at three sentences. Both halves kept: they are what stops a reader from taking the narrower year to date as a turn.
5. **Tile line: no change.** Already one plain sentence, one number, 73 characters.
6. **Plate 4 (mechanical, from Gate 1 open flag 3):** "sits at 41.2%" becomes "sits near 41%"; citation phrase and note updated. Exact old and new text in section C2.

### Citation entries

- Removed: "Fiscal policy is still loose", "it has stopped loosening", "slightly below last year's", "$7.8 billion a year earlier" (their phrases no longer exist in the prose).
- Added: "holding roughly steady" (derived), "last year's $66.9 billion" (same table as the $65.3 billion entry), "narrower than a year earlier" (same entry as the tile line's).
- Changed: "Four months" to "four months" (now mid-sentence, lower case).
- Unchanged: "$65.3 billion deficit this fiscal year", "$5.1 billion", "revenue outgrew program spending", "July alone was wider".
- All 8 abstract phrases and both tile phrases are exact substrings of their prose, each occurring once (checked by eye).

### Checklist (editorial/writing-style.md)

| Check | Tile line | Abstract |
|---|---|---|
| Length | PASS, 73 of 80 | PASS, 301 of 324; 3 sentences, 48 words |
| 4.1b answers the header question; not a recital | n/a | PASS: sentence 1 answers "What is Canada's fiscal policy stance?" |
| 4.1i take, mechanism, landing | n/a | PASS: sentence 2 says why the stance is steady; sentence 3 handles the one fact that could argue otherwise and says why it does not yet |
| Stands alone | PASS | PASS: "this fiscal year", "last year's" and "through July" need no other surface |
| Grounding numbers | 1 | 3 ($65.3 billion, $66.9 billion, $5.1 billion). The guide's 4.1b says two at most; the brief says about three, and the live abstracts run three or more |
| Signpost or setup sentences; publication's own method | PASS, none | PASS, none |
| Source attribution in prose | PASS, none | PASS: "Ottawa projects" names the actor and marks the figure as a projection; no publisher or document is named |
| Deep-dive cross-links | PASS, none | PASS, none |
| Banned words ("corridor", the L-B compound, cliches, hedging tics) | PASS | PASS |
| Math symbols, "per cent" | PASS | PASS |
| Acronym test | PASS | PASS, none used |
| Dollar style | PASS, "$5.1B" | PASS, "billion" spelled out |
| Echo of the monetary abstract ("On hold.") | n/a | PASS: full-sentence opener, different words |
| ASCII only | PASS | PASS |

### Flags for writer, fact-checker or publisher

1. **The level judgment is gone.** The abstract no longer says whether policy is loose, only that it is not changing much. That follows the brief. If the publisher wants a level read back in, it needs a claim Gate 1 has not verified.
2. **"Roughly steady" is still a headline-balance reading.** It survives the before-actuarial-losses measure only as "about the same size" (Gate 1 open flag 1 says the alternative-1 framing survives both readings). I did not strengthen it. New wording in the delta ("holding roughly steady", "close to") reuses verified figures only, but under the house rule a redraft re-enters Gate 1; the delta is small.
3. **Spelling.** The guide prefers "programme" for policy initiatives. "Program spending" is kept: it is the budget term for a spending category, not a named initiative, and the citation phrase depends on it.
4. **Plate 4, outside this brief.** With the fix applied the blurb still uses "rise" three times in two sentences. A tidy-up would be a separate polish; I did not touch it. Gate 1's softer point on "from 10 to 13 cents" also remains open.
5. **Citation mechanics.** "last year's $66.9 billion" is cited to `pipeline:dof:fiscal_reference_tables` on the strength of Gate 1's reading of Table A1.7; confirm at wiring that the slot carries the FY2025-26 value.

---

## Gate 3 verdict (surface fit, 2026-10-03)

Scope: does each piece belong on its surface, in its context. Read for context: `src/data/sections.ts` (fiscal block, the other seven tile lines and abstracts, `splashHero`), `src/pages/fiscal.astro`, `src/pages/index.astro`, `src/pages/overview.astro`, `src/data/site_data_loader.ts`, `src/components/home/SectionPanel.astro`, `data/site/sections.json` (fiscal prints). No copy was edited at this gate. Nothing under `src/` was touched.

### Verdict per surface

| Surface | Verdict | Reason |
|---|---|---|
| A. Tile line (dashboard panel on `/overview/`) | PASS | One sentence, one number, the latest print and its direction: the same shape as the other seven tile lines. No jargon, no method talk. One follow-up, below. |
| B4. Section abstract (`/fiscal/` lede) | PASS | Sentence 1 answers "What is Canada's fiscal policy stance?" directly. Sentences 2 and 3 give the reason and the one fact that could argue otherwise. Nothing internal, nothing about how the publication works, no filler. 48 words is right for a lede above five plates. |
| B1-B3 stamps | PASS | `heroKicker` and `updatedAt` name the July Fiscal Monitor and its release date; `blurb.date` is the prose date. See homepage finding: the kicker currently renders nowhere. |
| C2. Plate 4 ("sits near 41%") | PASS | Rounder figure suits a caption that sits beside a chart showing the exact value, and it now agrees with the section's own 41.1% print. |

### Check 1: abstract against the plates beneath it

No plate title contradicts the abstract. The abstract is about this fiscal year; the plates are about the multi-year plan (operating balance to 2028-29, the capital dispute, shares of GDP to 2030-31, debt, issuance). They read as "where we are now" followed by "where the plan goes", which is the right order for this page.

- Plate 3 ("As spending falls, revenues hold flat.") against "revenue outgrew program spending": different measures and horizons (shares of GDP over five years versus dollars over four months). The abstract's "Through July" scopes its claim, so a reader is not misled. No change.
- Plate 5 ("down from last year's $603 billion") and the abstract ("last year's $66.9 billion") use "last year" the same way. Consistent.
- The kicker promises the operating-balance commitment and the reclassification dispute; the abstract mentions neither. Acceptable: the header question is about stance, plates 1 and 2 carry those two subjects immediately below, and the old abstract did not mention them either.

### Check 2: tile line beside the other tiles

Stands alone. Follow-up, not a blocker: on the dashboard panel the line sits directly under the readout "Federal budget balance -$66.9B, FY 2025-26 est." The old line ($55.3B through March) was the same fiscal year as that readout; the new one is the next fiscal year, four months in, so a reader sees -$66.9B and $5.1B in one panel with only "through July" to tell them apart. The readout carries its own period label, so this is not wrong, and a macro reader knows the fiscal year starts in April. Recommended fix if it bothers on the live page (needs a quick Gate 1 and 2 pass, so not applied here): "This fiscal year's deficit was $5.1B through July, narrower than a year earlier." (77 characters; both citation phrases stay exact substrings; "this fiscal year" already appears in the abstract.)

### Check 3: cuts

None needed. No internal vocabulary, no statement about the publication's own process, no source-naming in prose ("Ottawa projects" names the actor, not a document), no template slot filled for its own sake.

### Check 4: homepage lead

The new `updatedAt` does not change any homepage lead, because no page has one.

- `src/pages/index.astro` is a fixed marketing page (slogan, "How we work", three showcases, advisory, subscribe). It does not rank sections; its carousel runs in array order.
- `src/pages/overview.astro` renders the eight panels in array order.
- `src/components/HeroTile.astro` and `pickHeroSection()` in `site_data_loader.ts` are the old lead-section mechanism. Neither is imported by any page. `pickHeroSection()` also reads the pipeline's `updatedAt` from `sections.json`, not the hand stamp in `sections.ts`.
- So Gate 1 open flag 5 does not apply to the live site. The hand stamp reaches readers only as the `/fiscal/` page's modified date (and feeds `scripts/check_prose_vintage.mjs`). `heroKicker` is read only by the unmounted HeroTile.

Hand-authored hero text that does exist: `splashHero.abstract` in `sections.ts` (~line 1371), shown at the top of `/overview/` by `TitleStatement.astro`. It is about oil prices falling as the Strait of Hormuz standoff eases, with citations dated to late June 2026. It is not tied to any section, so the fiscal update does not make it mismatched. It is three months old and reads as current ("The story now is ..."); not rechecked here and not rewritten. Also static: `public/showcase/dashboard.png` and `chartbook-fiscal.png` on the homepage are screenshots and will keep showing the old fiscal copy until re-shot.

### Check 5: debt-to-GDP and debt charges dropped from the abstract

Acceptable tightening, not a loss. The header asks about stance; the debt ratio and the interest bill are about sustainability, a different question. Both are still on the page: plate 4 is devoted to them, and the dashboard panel prints both. In the old abstract they were a third topic bolted onto the end; the new one stays on the question asked.

### Other notes for wiring (not blockers)

1. `latestReleaseLabel="Spring Update, April 2026"` on `/fiscal/` now sits above a lede that discusses July data. Same condition existed with the March Fiscal Monitor. It is accurate for the plates; worth a look at how it renders next to the new lede once built.
2. Gate 2's rewording of the opener and sentence 2 used only Gate 1 verified figures; under the house rule the delta still goes back through Gate 1 before wiring (Gate 2 flag 2).

---

## Gate 1 delta verdict (fact-check of reworded text only, 2026-10-03)

Scope: the Gate 2 rewording of the abstract and the Gate 3 proposed tile line. Figures were verified at the first Gate 1 pass and not re-fetched; arithmetic, lengths and citation substrings were re-run by script. Nothing under `src/` was edited.

| Item | Verdict |
|---|---|
| 1. "Fiscal policy is holding roughly steady" | PASS WITH FLAG |
| 2. "close to last year's $66.9 billion" | PASS |
| 3. "narrower than a year earlier as revenue outgrew program spending" | PASS |
| 4. Proposed tile line, and both length limits | PASS |
| 5. Citation phrases and notes | PASS after two mechanical edits |

### Item 1

Three readings of the planned change from FY2025-26 to FY2026-27 (Spring Economic Update Table A1.7):

| Measure | FY2025-26 | FY2026-27 | Change | "Roughly steady"? |
|---|---|---|---|---|
| Headline budgetary balance | -66.9 | -65.3 | 1.6bn narrower (2.1% to 1.9% of GDP as published) | Yes |
| Before net actuarial losses, with the 6.7bn reclassified out of program expenses added back | -62.0 | -65.2 | 3.2bn wider | Yes |
| Before net actuarial losses, as published | -55.3 | -65.2 | 9.9bn wider (about 0.3 points of GDP) | Contestable: a widening of about 0.3 points of GDP |

The opener is true on two of the three readings and the next sentence names the measure it rests on (the headline deficit, both figures shown), so it is not a fail. The flag: "fiscal policy" is a wider subject than the headline deficit, and the as-published before-actuarial-losses balance, which is closer to what the government decides, widens by about C$10bn. A reader who knows that table could call the opener generous.

Smallest change that is true on every measure, if the publisher wants it: scope the opener to the headline deficit, "The headline federal deficit is holding roughly steady." (316 characters in total, within 324; the citation phrase "holding roughly steady" stays an exact substring). Not applied: it changes the take from a stance read to a deficit read, which is a framing decision.

### Item 2

Both figures are from the budgetary balance row of Table A1.7, same vintage; repo `frt_federal_balance_total` carries -66.9 (2025-26) and -65.3 (2026-27), both marked as non-actual. $66.9 billion is an estimate until the Annual Financial Report. The prose does not call it final: "last year's $66.9 billion" sits in a sentence governed by "projects", and the dashboard readout labels it "est.". Acceptable as written. "Close to" is fair: 1.6bn apart, 2.4%.

### Item 3

Year to date: 5,138 versus 7,787, 2,649 narrower. Revenue +7.36% (page: 7.4), program spending +5.07% (page: 5.1); revenue rose 12,026 against 7,675 for program spending, so the claim holds in per cent and in dollars. "As" reads as explanation and the arithmetic supports it.

### Item 4

"This fiscal year's deficit was $5.1B through July, narrower than a year earlier." Accurate: the April to July figure belongs to FY2026-27, the current fiscal year, and the comparison is the same four months of FY2025-26. Dropping "federal" loses nothing inside the fiscal panel. Framing direction still matches the data (narrower year to date, gap shrinking in July, which the abstract discloses).

Lengths by script: tile line 80 characters, 13 words (limit 80: at the limit, no room for any added character; Gate 3's "77" was a hand count). Abstract 301 characters, 48 words, 3 sentences (limit 324). ASCII only.

### Item 5

By script: both tile phrases and all 8 abstract phrases are exact substrings of the final prose, each occurring once. Notes match the prose. Mechanical edits made in this file:

1. Section A: tile line replaced with the new wording in the display block and the `tileLine` string; "This fiscal year" definition added to the first tile citation note. Both citation phrases unchanged.
2. Section B4: the "holding roughly steady" note now states the before-actuarial-losses figures on both the as-published and reclassification-adjusted basis, and no longer claims the framing survives every reading.

The Gate 2 "Final text" block still shows the old tile line; it is history. Sections A and B4 are the paste-ready text.
