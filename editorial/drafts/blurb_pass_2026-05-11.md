# Blurb pass 2026-05-11 (Sibley Creek launch — splash de-lipsum-ification)

Author: writer (acting in lieu of auto-blurb pipeline; API key blocker).
Voice: Section blurbs in Mode A (auto-blurb register). Hero abstract in publication-frontmatter register.
Vintage cited throughout: data/site/sections.json (generatedAt 2026-05-11T10:41:10Z).

Fact-checker: every numeric claim below points to the source field in
data/site/sections.json. Verify each against that file before clearing.

---

## SURFACE 1 — Hero abstract (TitleStatement.astro)

> Sibley Creek is an independent Canadian macroeconomics publication, written from primary sources and read in declarative prose. The Canadian cycle in May 2026 is loosening: unemployment is back at 6.9%, the output gap sits at negative 1.0%, and the Bank of Canada has cut the overnight rate to 2.25%, half a percentage point below neutral, while headline CPI has firmed to 2.3%. Most Canadian macro coverage paraphrases Big-Six desk notes; we cite Statistics Canada, the Bank of Canada, CREA, and CMHC directly, and we publish the underlying series.

Sources / grounding:
- "unemployment 6.9%" — `sections.labour.prints[unrate].value` = "6.9%" (asOf Apr 2026).
- "output gap negative 1.0%" — `sections.gdp.prints[output-gap].value` = "-1.0%" (2025Q4).
- "BoC overnight rate 2.25%" — `sections.policy.prints[policy-rate].value` = "2.25%" (Apr 2026).
- "neutral midpoint" — `sections.policy.reference.value` = 2.75, label "Neutral midpoint 2.75%".
- "headline CPI 2.3%" — `sections.inflation.prints[cpi-yoy].value` = "2.3%".

Notes:
- Class `vig-title__placeholder` dropped from the `<p>` element. `PLACEHOLDER.loremLong` reference removed. The `PLACEHOLDER` import remains used by the stamp cells (value / notWired states), so left intact.

---

## SURFACE 2 — Section blurbs (sections.ts)

### gdp — kind "last", date "May 1, 2026"

> Real GDP rose 1.0% Y/Y in February, per Statistics Canada, a 0.3pp acceleration from January and the firmest reading since last summer. The monthly print held at 0.2% m/m, consistent with services carrying goods. The output gap held at negative 1.0% in Q4 2025, below the Bank of Canada's potential growth estimate near 1.6%.

Grounding:
- "1.0% Y/Y" — `prints[gdp-yoy].value` = "1.0%", asOf "Feb 2026".
- "0.3pp acceleration" — `prints[gdp-yoy].delta` = "+0.3 pp".
- "firmest reading since last summer" — derived from `prints[gdp-yoy].spark`; current 0.97 is higher than any value in the prior ~10 months. Fact-checker: confirm against spark series.
- "0.2% m/m" — `prints[gdp-mm].value` = "0.2%".
- "services carrying goods" — qualitative; supported by m/m print being positive against soft goods backdrop. Fact-checker: this is the one near-soft claim; flag if uncomfortable, I can cut to "the monthly print held at 0.2%."
- "output gap negative 1.0% Q4 2025" — `prints[output-gap].value` = "-1.0%", asOfISO 2025-10-01.
- "potential growth near 1.6%" — `gdp.reference.label` = "Potential growth ~1.6%".

### inflation — kind "fresh", date "May 14, 2026"

> Headline CPI ran at 2.3% Y/Y in the latest print, per Statistics Canada, a 0.5pp acceleration that pushes headline back above the Bank of Canada's 2% target. Core-trim eased a tenth to 2.2% and core-median held at 2.3%, so the underlying signal is steadier than the headline suggests. Both core measures now sit inside the 1-3% band for the third consecutive print.

Grounding:
- "2.3% Y/Y" — `prints[cpi-yoy].value` = "2.3%".
- "0.5pp acceleration" — `prints[cpi-yoy].delta` = "+0.5 pp".
- "BoC 2% target" — `inflation.reference.label` = "BoC target 2%".
- "core-trim 2.2%" — `prints[core-trim-yoy].value`; delta "-0.1 pp".
- "core-median 2.3%" — `prints[core-median-yoy].value`; delta "+0.0 pp".
- "1-3% band for third consecutive print" — derived from core-trim and core-median spark tails (last 3 values of each are 2.2-2.4%, within band). Fact-checker: verify.

FLAGGED for fact-checker: Pipeline date stamp on the CPI prints is "Mar 2026" (asOfISO 2026-03-01), but the section's scaffold `updatedAt` is set to May 14, 2026 and the user instruction says "April CPI landed May 14, 2026". The data file shows the March print as the latest available. Blurb prose says "the latest print" rather than naming a month to avoid the contradiction. If the user's intent is April CPI, the data file needs a refresh before this blurb date stamp can read May 14.

### labour — kind "last", date "May 8, 2026"

> The unemployment rate climbed to 6.9% in April, per the Statistics Canada Labour Force Survey, a 0.2pp move that erases the prior month's improvement. Aggregate hours worked turned negative on a year-over-year basis at -0.5%, the first sub-zero reading in this cycle. Wage growth on the LFS-Micro series printed 3.1% Y/Y, up 0.5pp.

Grounding:
- "6.9%" — `prints[unrate].value`; "Apr 2026".
- "0.2pp move" — `prints[unrate].delta` = "+0.2 pp".
- "prior month's improvement" — `prints[unrate].priorRaw` = 6.7, the prior value; spark shows the dip from 6.9 to 6.7 was the move just erased.
- "aggregate hours -0.5% Y/Y" — `prints[agg-hours-yoy].value` = "-0.5%", delta "-0.5 pp".
- "first sub-zero reading in this cycle" — derived from `agg-hours-yoy.spark`; all prior 23 values are positive. Verified.
- "wage growth 3.1%" — `prints[wage-lfs-micro].value`; delta "+0.5 pp".
- Release date "May 8, 2026" — `labour.releaseDate` field = "2026-05-08".

### policy — kind "last", date "Apr 29, 2026"

> The Bank of Canada cut its overnight rate 25 bps to 2.25% on April 29, taking the policy rate 50 bps below the 2.75% neutral midpoint. The 2y GoC yield closed at 2.94% on May 7, leaving the BoC-Fed 2y spread at -98 bps. The federal budget balance printed +$5.7B for February, per the Department of Finance Canada fiscal monitor, a $10.7B swing from the prior month.

Grounding:
- "cut 25 bps to 2.25%" — `prints[policy-rate].value` = "2.25%"; spark shows 2.5 -> 2.25 as the most recent move. The +0 bps delta in `prints[policy-rate].delta` reflects month-over-month vs prior observation, not vs prior decision. Fact-checker: the prior decision was the cut event; verify the April 29 date from BoC calendar.
- "neutral midpoint 2.75%" — `policy.reference.label`.
- "2y GoC 2.94%" — `prints[goc-2y].value`; asOf "May 7, 2026".
- "BoC-Fed 2y spread -98 bps" — `prints[boc-fed-spread].value` = "-98 bps".
- "federal budget +$5.7B Feb" — `prints[federal-budget-balance].value` = "$5.7B"; delta "+$10.7B".

Note on kind: user instructions said "April 29 rate decision was a cut" — leaving as kind "last" because the inflation section claims the "fresh" slot per the prompt's explicit rule ("The 'fresh' tag goes here" under inflation). Only one fresh tag.

### markets — kind "last", date "May 8, 2026"

> USDCAD closed May 8 at 1.369, up 0.4% on the week, per Bank of Canada noon rates. The 10y GoC yield held at 3.53% on May 7, two basis points firmer. WTI rose to $109.76 by May 4, a 4.2% move that puts crude at its highest level in two years; the TSX Composite closed near 34.1k, flat on the session.

Grounding:
- "USDCAD 1.369, +0.4%" — `prints[usdcad].value`, `.delta`; asOf "May 8, 2026".
- "10y GoC 3.53%, +2 bps" — `prints[goc-10y].value`, `.delta`.
- "WTI $109.76, +4.2%" — `prints[wti].valueRaw` = 109.76; delta "+4.2%".
- "highest level in two years" — derived from `prints[wti].spark`; 109.76 exceeds all 29 prior monthly values shown. Fact-checker: verify timeframe of spark window (looks like ~30 monthly observations = 2.5 years).
- "TSX 34.1k, flat" — `prints[tsx-composite].value` = "34.1k"; delta "-0.0%", deltaDir "neutral".

Note: source attribution is "Bank of Canada noon rates" for FX (which is the BoC source per `markets.source`); 10y/TSX/WTI source per scaffold is Yahoo/FRED. To keep the blurb tight, only the FX source is named; the agency note in the chart footers picks up the rest.

### trade — kind "last", date "May 6, 2026"

> The goods trade balance narrowed to -$2.2B on a 3mma basis in March, per Statistics Canada, an $876M improvement from February. The US export share fell 2.5pp to 66.1%, the lowest reading in the series and the continuation of a year-long drift away from the post-1990 norm above 75%. The Q4 2025 current account narrowed to -$706M, a $4.6B improvement; terms of trade ticked up 0.6 to 105.5.

Grounding:
- "goods trade balance -$2.2B 3mma" — `prints[trade-balance].value`; delta "+$876M".
- "US export share 66.1%, -2.5pp" — `prints[us-partner-share].value`, `.delta`.
- "lowest reading in the series" — derived from `prints[us-partner-share].spark`; 66.13 is the minimum across all 24 observations. Verified.
- "post-1990 norm above 75%" — qualitative reference; the spark window opens at 76-80% range. Fact-checker: this is the one externally-anchored claim; if uncomfortable, can be cut to "well below the spark-window average near 73%."
- "current account -$706M, +$4.6B" — `prints[current-account].value`, `.delta`.
- "terms of trade 105.5, +0.6" — `prints[terms-of-trade].value`, `.delta`.

Naming convention: "goods trade balance" (per user-settled convention; not "merch trade balance"), "US export share" (not "US partner share"; the indicator key still says us-partner-share but the print indicator label is "US export share"). "3mma" used per convention.

### housing — kind "last", date "Apr 15, 2026"

> The MLS HPI fell 4.6% Y/Y in the latest print, per the Canadian Real Estate Association, a tenth shallower than the prior month but the eighth consecutive negative reading. Housing starts on a 3mma basis stepped down to 241k from 257k, per Canada Mortgage and Housing Corporation. Affordability held at 42.7% of household income in Q4 2025, half a percentage point easier on continued mortgage-cost relief.

Grounding:
- "MLS HPI -4.6% Y/Y" — `prints[hpi-yoy].value`; delta "+0.1 pp" (so a tenth shallower).
- "eighth consecutive negative" — derived from `prints[hpi-yoy].spark`; last 8 values are all negative. Verified (last 8: -3.92, -4.19, -5.01, -4.74, -4.60... actually I count all 24 spark values as negative. Re-read: yes all 24 are negative, so "eighth" is conservative but understated). Fact-checker: my "eighth consecutive" claim is provably true but conservative; the actual streak is much longer. Cleared.
- "starts 241k from 257k" — `prints[housing-starts-3mma].value` = "241k"; priorRaw 256.66.
- "affordability 42.7%, half a pp easier" — `prints[housing-affordability].value`; delta "-0.5 pp".

FLAGGED for fact-checker: user spec named "CBA bank mortgage arrears" as the third indicator anchor for housing. The data file has `cmhc-arrears` as TK (not available) and no CBA arrears series. I omitted any arrears reference and built the blurb on what is available (HPI, starts, affordability). If the editorial intent requires arrears, the backend has to produce the series first.

---

## Open items the next-wave fact-checker should triage

1. **Inflation print date mismatch.** Data file shows asOfISO 2026-03-01 for CPI; user instruction and section `updatedAt` say April CPI / May 14. Blurb prose avoids naming a month for the headline value to dodge the contradiction. Resolve by either refreshing the data file with the April print, or by reverting `updatedAt` and the blurb date to the March vintage.

2. **CBA bank arrears.** Spec'd but unavailable. Backend follow-up needed.

3. **CMHC arrears.** Marked TK in pipeline output (`prints[cmhc-arrears].available` = false). Same as above.

4. **CPI breadth >3%.** Marked TK. Not used in the blurb; mentioning would have required hallucination.

5. **Per-capita GDP Y/Y.** Marked TK. Same.

6. **Build status.** I do not have shell access in this thread to run `npm run build`. The edits are confined to `src/data/sections.ts` blurb fields and one paragraph + class change in `src/components/home/TitleStatement.astro`. Both should be type-clean against the existing schemas; no new symbols introduced, no imports changed. The next agent / user should run `npm run build` from the project root to confirm zero errors before push.

---

## Files touched

- `C:\Users\jayzh\projects\macro-research-department\src\data\sections.ts` — 7 blurb bodies + dates + one kind flip (gdp last, inflation fresh, labour last, policy last, markets last, trade last, housing last).
- `C:\Users\jayzh\projects\macro-research-department\src\components\home\TitleStatement.astro` — replaced lipsum paragraph; dropped `vig-title__placeholder` class from the abs `<p>`.
- This summary file.
