# Homepage index-tile lines -- one editorial sentence per section

Author: writer (macro-research-department).
Date: 2026-05-11.
Status: v1 draft for editorial-director scope review and style-editor voice polish.

Spec (per art-director Path C): 12-16 words each, active voice, declarative,
names the latest dated print, sentence-case, no hedging, no Big-Six
citations. Each line is what the tile says about the section right now
based on the latest print -- not the section's evergreen headline question.

Voice register: panel-page deck voice from the GDP / Inflation basics
drafts. Short, declarative, numerate. No clichés, no marketing copy.

Anchors:
- `editorial/writing-style.md` (Mode A-adjacent; declarative deck voice).
- `editorial/dashboard_purpose.md` Section 4 (headline questions for
  reference -- NOT used as the tile lines).
- `research/wave3_gdp_basics_insights.md` (GDP anchors).
- `research/wave3_inflation_basics_insights.md` (Inflation anchors).
- `src/data/sections.ts` (placeholder anchors for sections without
  Wave-3 research coverage).

---

## GDP
Real GDP rose 0.2% in February 2026, but the quarterly cut contracted 0.2% in Q4 2025.
Word count: 16

## Inflation
Headline CPI ticked up to 2.4% in March 2026, with core measures holding near target.
Word count: 15

## Labour
Unemployment held at 6.1% in April 2026, while per-capita employment kept falling on a yearly basis.
Word count: 16

## Housing
MLS HPI fell 1.4% year-over-year in April 2026, with the national benchmark still in negative territory.
Word count: 16

## Policy
The Bank of Canada cut 25 basis points to 2.75% on April 29, 2026.
Word count: 14

## Markets
USDCAD closed at 1.378 on May 9, 2026, with the loonie drifting weaker through the spring.
Word count: 16

## Trade
Canada's merchandise trade balance posted a $2.3-billion deficit in March 2026, extending the run of deficits.
Word count: 16

---

## Source insights drawn from

- **GDP**. February 2026 monthly print +0.2% M/M and Q4 2025 quarterly
  -0.2% Q/Q are both verified in `research/wave3_gdp_basics_insights.md`
  Section B. The two-cut framing (monthly path turning while quarterly
  contracted) matches the page-lede draft in `gdp_basics_v1.md`.
- **Inflation**. March 2026 headline 2.4% Y/Y, ticked up from 1.8% in
  February as the carbon-levy base effect unwound; core-trim 2.2% and
  core-median 2.3% holding close to the 2% target. All verified in
  `research/wave3_inflation_basics_insights.md` Panels 1 and 2.
- **Labour**. Unemployment 6.1% April 2026 and per-capita employment
  Y/Y still negative are the prompt-supplied placeholders; the
  per-capita-still-negative framing aligns with EDR Section 4.3
  element 2 and the Pillar E deep-dive scope (per-capita-vs-aggregate
  divergence).
- **Housing**. MLS HPI Y/Y -1.4% April 2026 is the prompt-supplied
  placeholder; the sparkline in `src/data/sections.ts` shows the series
  crossed through zero and has been sliding for roughly a year, which
  grounds the "still in negative territory" tail.
- **Policy**. BoC overnight rate 2.75% with the April 29 cut is
  confirmed by the `sections.ts` fresh blurb dated 2026-04-29 ("The
  Bank cut 25 bps as expected") and by the BoC FAD release
  (`https://www.bankofcanada.ca/2026/04/fad-press-release-2026-04-29/`)
  cited in `research/wave3_gdp_basics_insights.md` Panel 1. April was
  a cut, not a hold; the placeholder is accurate.
- **Markets**. USDCAD 1.378 May 9, 2026 is the prompt-supplied
  placeholder; the sparkline in `src/data/sections.ts` walks 1.348 ->
  1.378 over 24 daily observations, which grounds "drifting weaker
  through the spring" as a directional statement.
- **Trade**. Merchandise trade balance -$2.3B March 2026 is the
  prompt-supplied placeholder; the sparkline in `src/data/sections.ts`
  shows roughly 12 consecutive monthly deficits, which grounds
  "extending the run of deficits" as a directional statement.

---

## Flagged unsupported claims / verification asks

1. **Inflation -- shelter framing in the prompt anchor conflicts with
   Wave-3 research.** The prompt's anchor reads "shelter doing most of
   the work." Wave-3 inflation research (`Panel 4`) verifies the
   opposite for March 2026: shelter cooled to 1.7% Y/Y, below the 2.4%
   headline and below all-services at 2.5%, with mortgage interest cost
   "essentially extinguished" at 0.3% Y/Y. The marginal pressure points
   are energy (3.9%) and food (4.0%). The draft above uses the
   research-verified framing ("core measures holding near target")
   instead of the prompt's shelter framing. Researcher / editorial-
   director: confirm the prompt anchor is a stale placeholder and the
   research is canonical for the March 2026 print.

2. **Labour -- the 6.1% April 2026 unemployment rate is a prompt
   placeholder.** The prompt invites adjustment if a real anchor
   differs. No Wave-3 labour research pack is on file at the time of
   this draft, so the line ships against the placeholder. Verification
   ask routed to researcher: confirm 6.1% April 2026 against the May 2,
   2026 LFS release (`src/data/sections.ts` `updatedAt` and the "last"
   blurb dated 2026-05-02 imply the LFS has landed).

3. **Labour -- "per-capita employment kept falling on a yearly basis"
   is the prompt's directional anchor.** The exact Y/Y per-capita
   employment value is not pinned to a verified number in the Wave-3
   GDP per-capita research (which addresses GDP per-capita, not
   employment per-capita). The line uses directional language. Verifier
   ask: pull employment-per-capita Y/Y for April 2026 from StatCan
   Table 14-10-0287-01 / 17-10-0009-01 derivation before this line
   ships.

4. **Housing -- "still in negative territory" is grounded in the
   sparkline trajectory in `src/data/sections.ts`, not in a verified
   Wave-3 research pack.** No Wave-3 housing research has been routed
   to the writer. Verifier ask: confirm the MLS HPI Y/Y April 2026
   value (-1.4%) and the consecutive-monthly-negative-print count
   against the CREA April 2026 release before the line ships.

5. **Markets -- "drifting weaker through the spring" is grounded in
   the daily-series sparkline (1.348 -> 1.378 over the displayed
   window) in `src/data/sections.ts`.** No Wave-3 markets research
   pack on file. The cleanest verifiable framing on the spot value is
   the percentile-classifier read ("80th percentile of the post-1990
   distribution" per the section blurb dated 2026-05-03), but
   percentile claims require a research-pack verification of the
   distribution baseline -- the draft avoids the percentile language
   to stay within what the prompt's anchor supports.

6. **Trade -- "extending the run of deficits" is grounded in the
   24-month sparkline in `src/data/sections.ts` (roughly 12
   consecutive monthly deficits).** No Wave-3 trade research pack on
   file. Verifier ask: confirm the consecutive-deficit count against
   StatCan Table 12-10-0119-01 before this line ships.

7. **Policy -- the line names the rate level and the cut date, not
   the cumulative cycle context.** The directional framing in
   `sections.ts` ("dropped the line about needing more evidence on
   services inflation") is a richer read but pushes past the 16-word
   limit and toward editorializing. The current line is plain
   declarative on the verifiable fact (cut of 25 bps to 2.75% on
   April 29, 2026); the cycle context belongs in the section page
   deck, not the tile line.

End of v1 draft.
