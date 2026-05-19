# Gate 1 verdict — April 2026 inflation refresh

**Status: PASS WITH MECHANICAL FIXES (one framing item to user)**

Verification cycle: 2026-05-19 (April 2026 CPI release day).
Drafts verified: `src/data/sections.ts` (inflation blurb), `src/pages/inflation.astro` (plates 1, 2, 3, 4). Plate 5 unchanged this cycle (quarterly).

---

## Verified claims

### Plate 1 / splash blurb / abstract

| Claim | Expected | Actual | Pass |
| --- | --- | --- | --- |
| Headline CPI NSA Y/Y April | 2.8% | 2.815% → 2.8% | yes |
| Headline CPI NSA Y/Y March | 2.4% | 2.385% → 2.4% | yes |
| m/m NSA April | 0.4% | from PDF (pipeline slot pending) | yes |
| m/m SA April | 0.3% | from PDF (SA refresh lag) | yes |
| Consensus 3.1% Y/Y | 3.1 | CIBC Week Ahead, Bloomberg consensus | yes |
| Consensus 0.6% m/m NSA | 0.6 | same source | yes |
| 1-3% control band | mandate | card:boc_inflation_mandate | yes |

### Plate 2 (cores)

| Claim | Expected | Actual | Pass |
| --- | --- | --- | --- |
| Core-trim Y/Y April | 2.0% | 2.0 (StatCan v108785715) | yes |
| Core-median Y/Y April | 2.1% | 2.1 (StatCan v108785714) | yes |
| Trim -0.2pp Mar->Apr | -0.2pp | 2.2 -> 2.0 | yes |
| Median -0.2pp Mar->Apr | -0.2pp | 2.3 -> 2.1 | yes |
| Both lower than 3 months ago (Jan) | true | trim Jan 2.4 -> Apr 2.0 (-0.4); median Jan 2.5 -> Apr 2.1 (-0.4) | yes |
| Within a tenth of 2% target | true | trim 0.0 away; median 0.1 away | yes |

### Plate 3 (breadth) - mechanical refresh applied

The writer drafted against the stale boc-tracker March value (28%). After the components daily-fetch landed (this cycle), the canonical March = 30.47% -> 30%, April = 29.43% -> 29%. Plate now displays April with the March -> April narrowing.

| Claim (post-fix) | Expected | Actual | Pass |
| --- | --- | --- | --- |
| 29% of basket Y/Y > 3% in April | 29% | 29.43% -> 29% | yes |
| March's 30% | 30% | 30.47% -> 30% | yes |
| 2022 peak > two-thirds | >66.7% | 68.76% (Sept 2022); Jul-Sep all >67% | yes |
| asOf Apr 2026 | true | updated from "Mar 2026" | yes |

### Plate 4 (sub-aggregates)

| Claim | Expected | Actual | Pass |
| --- | --- | --- | --- |
| Energy Y/Y April | 19.2% | 19.223 -> 19.2 | yes |
| Shelter Y/Y April | 1.8% | 1.766 -> 1.8 | yes |
| Shelter "fourth straight month <2%" | 4 months | Jan 1.7, Feb 1.5, Mar 1.7, Apr 1.8 - all <2 | yes |
| Services Y/Y April | 1.7% | 1.651 -> 1.7 (down from 2.5 Mar) | yes |
| Food Y/Y April | 3.5% | 3.496 -> 3.5 (down from 4.0 Mar) | yes |
| Goods Y/Y April | 4.4% | 4.423 -> 4.4 (up from 2.1 Mar) | yes |
| Energy delta +15.4pp | +15.4pp | 19.222 - 3.873 = 15.35 -> 15.4 (round-half-up) | yes |

### Editorial-direction alignment

- Plate 1 title "Headline CPI rose to 2.8% in April on higher gasoline prices" - data direction matches (energy +19.2%, headline +0.4pp). Pass.
- Plate 2 title "Core measures ticked down in April" - both cores -0.2pp from March. Pass.
- Plate 3 title "Breadth remains narrow, with 29% of the basket running above 3%" - data direction matches (narrowed from 30% -> 29%). Pass.
- Plate 4 title "Gas and energy drove April's lift while the rest of the basket stayed soft" - energy dominant (+19.2%), services/food retreated, shelter unchanged, goods up but goods-ex-energy implication holds. Pass.

---

## Mechanical fixes applied

1. `src/pages/inflation.astro` plate-3: full plate refresh - title 28% -> 29%, asOf Mar -> Apr 2026, interp text rewritten to lead with April + show March context, callout 28% -> 29% with -1pp delta, citation array updated with April data points + 2022 peak enumeration (Sept 2022 = 68.76%).
2. Pipeline source swap for plate-2 chart: cores now resolve from StatCan vectors (v108785715 trim, v108785714 median, v108785713 common) rather than BoC Valet (this swap was made earlier in the session; the chart on plate 2 will now reflect April values on the next site rebuild).
3. Pipeline daily-fetch added for cpi_components.csv (replaces one-time boc-tracker lift); breadth derivations now refresh same-morning as headline.

## Source cards created

1. `card:economist_consensus_april_2026_cpi` - Tier A, primary verified from CIBC Week Ahead May 18-22 2026 (Bloomberg-sourced consensus column). Verbatim excerpt captured.
2. `card:iran_oil_conflict_2026_05` - Tier B placeholder. Has one credible secondary (CIBC, cross-author confirmation in same publication). **Needs jzm `user_confirmed_at` before Gate 3.** Also: the writer used `card:wsj_iran_oil_war_2026_05` as the source slug; I renamed to `iran_oil_conflict_2026_05` (no source from WSJ available yet, and "conflict" matches the more technical CIBC framing).

## Citation-slot rename required

The writer's citations reference `card:wsj_iran_oil_war_2026_05` (3 places: plate 1, plate 4, sections.ts abstract). The card was created as `iran_oil_conflict_2026_05`. Two options:

- **Option A**: update the three citation references to point to `iran_oil_conflict_2026_05` (mechanical, can be auto-applied).
- **Option B**: keep the citation slug `wsj_iran_oil_war_2026_05` and rename the card to match. This commits to the framing word "war."

Recommend Option A. It also leaves the prose phrase ("war in Iran" / similar) as a separate user-veto item below.

---

## One item for user veto (framing, not mechanical)

**"war in Iran" vs "conflict in Iran"** - the writer's prose uses "war in Iran" (matching Jay's PDF commentary). CIBC and Bloomberg analysts use "conflict in Iran" / "conflict in the Middle East" / "Strait of Hormuz impasse." Both are defensible; "war" is colloquial / editorial, "conflict" is the formal analyst register.

- **Stay with "war in Iran"**: matches Jay's PDF byline voice. Punchier. Defensible since the user already framed it this way in their own published commentary.
- **Soften to "conflict in Iran"**: matches the more technical register used by major-bank research. Lower regret if the situation de-escalates or is later reclassified.

Default: keep "war" (author's voice = source of truth) unless user wants the softer framing.

---

## No failures

All numeric claims verify against primary data after the mechanical fixes above. No claim couldn't be verified. No claim contradicted the data.

---

## Next gates

Drafts ready for Gate 2 (style-editor). Gate 3 (editorial-director surface-fit) blocked on user veto of the "war" framing - but the rest of the prose can proceed to Gate 2 independently; user veto changes one phrase across three surfaces.
