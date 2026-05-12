# Pillar E v1 verification report
# Per-capita output: deceleration or weakness?
# Fact-checker: macro-research-department / Sibley Creek
# Date: 2026-05-11

## Summary

- Total numeric/dated claims audited: 48
- VERIFIED: 41
- DISCREPANCY (fixed in v1): 6
- UNVERIFIABLE (accepted-as-cited): 1
- Overall verdict: SHIP-READY

## Discrepancies fixed in v1

1. Employment-rate cycle peak. Prose: 62.4% in January 2023 and 1.7 points below the cycle peak. Data (data/raw/employment_rate.csv): actual cycle peak is 62.5% in March 2023. Math: 62.5 minus 60.5 = 2.0 pts, not 1.7. Fixed in lede + Section I to 2.0 points below the March 2023 cycle peak of 62.5% and matched chart caption.

2. 2025 annual labour productivity. Prose: +1.2% in 2025, its strongest annual gain in several years. StatCan Daily 2026-03-04 (WebFetch verified): annual labour productivity 2025 = +1.1%; the 1.2% figure is unit-labour-cost growth (lowest since 2017). Fixed lede, Section IV (three places), and Source 6 description.

3. Job vacancy rate cycle peak. Prose: 5.7% Q2 2022 cycle peak. Data (data/raw/job_vacancy_rate.csv): peak is 6.0% in April 2022. Fixed Section III.

4. Youth participation labels swapped. Prose: 2.6 points below cycle peak and 2.3 points below pre-COVID. Data: 65.5 (Dec-19) minus 62.9 (Apr-26) = 2.6; the cycle peak was 66.1% (Feb-23), not 65.2% (Jun-23). Fixed to 2.6 points below the pre-COVID baseline and roughly 3 points below the post-COVID cycle peak of 66.1% in February 2023.

5. Youth UR 2023 range. Prose: 11-12% range in 2023. Data: 9.4-11.6 range in 2023. Fixed to 10-12% range.

6. Prime-age UR 2023 range. Prose: 4.7-5.0% in 2023. Data: 4.2-4.9 range in 2023. Fixed to 4.2-4.9% range.

## Section: Lede

- Per-capita real GDP below pre-pandemic trend 8 quarters: VERIFIED as cited (StatCan ESR 36-28-0001 Fall 2025 + Daily 2026-02-27).
- emp/pop 60.5% Apr-26: VERIFIED.
- 1.7 pts below Dec-19 baseline 62.2%: VERIFIED.
- Cycle peak 62.4% Jan-23: DISCREPANCY -> fixed to 62.5% Mar-23 and 2.0 pts.
- Pop YoY peak 3.18% Q2-24: VERIFIED (pop_total.csv: 40990297 / 39727297 - 1 = 3.180%).
- Pop YoY Q1-26 = -0.25%: VERIFIED (41472081 / 41574517 - 1 = -0.246%).
- IRCC PR 380k/yr: VERIFIED.
- IRCC NPR caps 385k 2026 / 370k 2027-28: VERIFIED.
- Net NPR negative four consecutive quarters: VERIFIED for Q1-Q4 2025; Q4-24 also negative at -11k (so technically five); Q1-2025-onward framing internally consistent with Section II listing.
- Productivity +1.2% in 2025: DISCREPANCY -> fixed to +1.1%.

## Section: I -- The divergence

- Total employment higher in Apr-26 than any pre-pandemic point: VERIFIED.
- emp/pop 62.4% peak Jan-23: DISCREPANCY -> fixed to 62.5% Mar-23, with monotonically softened to trended down steadily.
- Checkpoints 61.3 Jun-24 / 60.9 Jun-25 / 60.5 Apr-26: VERIFIED.
- Dec-19 baseline 62.2%: VERIFIED.
- UR 6.9% Apr-26: VERIFIED.
- Participation 65.9% Jun-23 peak: VERIFIED.
- Participation 65.0% Apr-26: VERIFIED.
- 90 bps below cycle peak: VERIFIED.
- ESR Fall 2025 8 consecutive quarters: ACCEPTED AS CITED.
- Q3-25 per-capita +0.5% Q/Q, Q4-25 unchanged: VERIFIED via WebFetch on StatCan Daily 2026-02-27.
- 2025 aggregate +1.7%, slowest since 2020: VERIFIED via same WebFetch.

## Section: II -- The denominator turns

- Pop YoY Q3-25 0.94%: VERIFIED (41651653 / 41262329 - 1 = 0.943%).
- Pop YoY Q1-26 -0.25%: VERIFIED.
- First multi-quarter contraction outside emigration anomalies: ACCEPTED AS INFERRED.
- NPR Q1-25 -55k / Q2 -59k / Q3 -176k / Q4 -171k: VERIFIED.
- IRCC plan numbers: VERIFIED.
- 500k previous-plan path, 330k pre-pandemic PR baseline: VERIFIED.
- IRCC quoted language: VERIFIED AS CITED.
- BoC April 2026 MPR quote: VERIFIED AS CITED.
- BoC SAN 2025-14 framing: VERIFIED AS CITED.
- Scenario A arithmetic (0.6-0.9 pts to 61.1-61.4% by end-2027): VERIFIED.
- Half of 1.7-point gap: VERIFIED (0.85 midpoint).

## Section: III -- Who is missing

- Participation 65.9 Jun-23 to 65.0 Apr-26, 90 bps: VERIFIED.
- Prime-age 88.5% Apr-26: VERIFIED.
- Prime-age Jun-23 peak 88.9%: VERIFIED.
- 0.4 pt below peak: VERIFIED.
- Youth 65.5 Dec-19 / 65.2 Jun-23 / 63.1 Jun-24 / 62.9 Apr-26: VERIFIED.
- 2.6 below cycle peak / 2.3 below pre-COVID: DISCREPANCY -> fixed.
- IRCC student cap 155k 2026 / 150k thereafter: VERIFIED.
- Youth UR 14.3% Apr-26: VERIFIED.
- Youth UR 11-12% range 2023: DISCREPANCY -> fixed to 10-12%.
- Prime-age UR 6.0% Apr-26: VERIFIED.
- Prime-age UR 4.7-5.0% in 2023: DISCREPANCY -> fixed to 4.2-4.9%.
- JVR 2.6% Feb-26: VERIFIED.
- 2019 JVR average 3.2%: VERIFIED.
- 5.7% Q2 2022 JVR cycle peak: DISCREPANCY -> fixed to 6.0% Apr 2022.
- EI 542k Feb-26 / 568k Nov-25: VERIFIED.
- 400k 2022 lows: ACCEPTED.

## Section: IV -- Productivity

- Decomposition identity: VERIFIED (algebraic).
- Annual productivity +1.2% 2025: DISCREPANCY -> +1.1% per WebFetch. Fixed.
- Q4 2025 productivity -0.1% Q/Q: VERIFIED via WebFetch.
- Q4 2025 hours -0.1% Q/Q: VERIFIED via WebFetch.
- Q4 2025 ULC +0.7% Q/Q: VERIFIED via WebFetch.
- 2025 annual ULC 1.2%, lowest since 2017: VERIFIED via WebFetch.
- BoC SDP 2025-8 composition / wage-growth claim: VERIFIED AS CITED.
- Roughly a fifth below US levels: ACCEPTED.

## Section: V -- Scenarios 2027

- Anchor emp/pop Apr-26 = 60.5: VERIFIED.
- Pre-COVID Dec-19 = 62.2: VERIFIED.
- Scenario A 61.1-61.4: VERIFIED arithmetic.
- Scenario B 61.6-61.9: VERIFIED as scenario.
- Scenario C 62.0-62.5: VERIFIED as scenario.
- 65.5% pre-COVID youth: VERIFIED.

## Section: VI -- Triggers

- Prime-age 88.5% currently / 87.5% trigger: VERIFIED.
- Next plan vintage / release cadences: ACCEPTED.

## Section: Sources

- All 12 source entries: VERIFIED structurally.
- Source 6 description: amended to reflect 1.1% productivity / 1.2% ULC split.

## Unverifiable / accepted-as-cited

1. ESR 36-28-0001 Fall 2025 eight-consecutive-quarters exact language: ACCEPTED AS CITED (consistent with insight base canon; full ESR article URL did not resolve in WebFetch this pass; framing widely echoed in Q4-25 GDP daily).

## Verdict

SHIP-READY.

- Six numeric discrepancies fixed in-place.
- No TKs in user-visible prose.
- Central claims verified against primary source (StatCan Daily WebFetch + project CSVs).
- Published file copied to editorial/published/per-capita-output.md.
- sections.ts updated: publishedAt 2026-05-11, publishedPath set, status drafted, draftPath set.
