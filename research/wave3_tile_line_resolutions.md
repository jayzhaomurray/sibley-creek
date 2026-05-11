# Wave 3 -- Homepage Tile Line Flag Resolutions

Author: researcher
Date: 2026-05-11
Scope: resolve 7 unsupported-claim flags from writer's
`editorial/drafts/homepage_index_tile_lines.md` v1 draft, using primary
sources only.

ASCII-only. Verbatim attestations are in quoted form. All percentile,
Y/Y, and run-count derivations are reproducible from scripts named
inline. The writer-facing instruction is in the "Recommended revision
to writer" row per flag.

Confidence flag legend:
- VERIFIED -- primary-source value or derivation reproducible end-to-end
  from a script in `analyses/` or directly quoted from a primary source.
- STRONG  -- primary-source numbers in hand; some interpretive
  judgement (e.g. choice of denominator) acknowledged in caveat.
- WEAK    -- partial source coverage; the writer should hedge.

---

## Flag 1. Inflation -- shelter framing for March 2026

**Question.** Is "shelter doing most of the work" accurate for the
March 2026 CPI print? If not, who is doing the work?

**Primary source(s) consulted.**
- StatCan The Daily, "Consumer Price Index, March 2026," released
  April 20, 2026. URL:
  https://www150.statcan.gc.ca/n1/daily-quotidien/260420/dq260420a-eng.htm
- W3-R2 inflation research pack
  (`research/wave3_inflation_basics_insights.md`, Panel 4).

**Resolved values.**
- Headline CPI Y/Y, March 2026: 2.4% (StatCan Daily 2026-04-20).
- Shelter Y/Y: 1.7% (BELOW headline; BELOW all-services 2.5%).
- Food (all) Y/Y: 4.0%; Food purchased from stores 4.4%.
- Energy Y/Y: 3.9% (gasoline the lead sub-component).
- Mortgage interest cost Y/Y: 0.3% ("essentially extinguished").
- Verbatim StatCan attestation on what is leading inflation:
  "Driving faster price growth in headline inflation were higher
  prices for energy, especially gasoline, due to the conflict in
  the Middle East."

**Interpretation.**
The prompt's "shelter doing most of the work" framing is stale by
roughly 12 months. As of March 2026 the composition has rotated:
shelter has cooled below headline (1.7% Y/Y), MIC contribution is
near zero, and the marginal pressure points are energy (gasoline
pass-through from the Middle East conflict) and food.

**Recommended revision to writer.**
The writer's current line ("with core measures holding near target")
is defensible -- core trim 2.2% and core median 2.3% are at or
fractionally above the 2% target per Panel 2. An equally defensible
alternative that names the actual driver:
"Headline CPI ticked up to 2.4% in March 2026 as gasoline and food
pulled the basket higher."
Do not use "shelter doing the work" for this print.

**W3-R2 canonical-finding status.**
Confirmed canonical for the March 2026 reference month. The prompt's
shelter-driven framing was a stale anchor (likely carried forward from
the 2023-2024 narrative); it should be retired everywhere it appears
in the v1 draft, including the Inflation section blurb in
`src/data/sections.ts` (the "April CPI" blurb body line "Shelter is
still doing most of the work, with mortgage interest cost the largest
single contributor" is inconsistent with the March 2026 primary
source).

**Confidence:** VERIFIED.

---

## Flag 2. Labour -- UR for April 2026

**Question.** Is the unemployment rate 6.1% in April 2026 (placeholder
in writer's draft and in `src/data/sections.ts`)?

**Primary source(s) consulted.**
- StatCan The Daily, "Labour Force Survey, April 2026," released
  May 8, 2026. URL:
  https://www150.statcan.gc.ca/n1/daily-quotidien/260508/dq260508a-eng.htm
- Cross-check: `C:\Users\jayzh\Documents\boc-tracker\data\unemployment_rate.csv`
  and `employment_rate.csv` -- both updated through April 2026.

**Resolved values.**
- Release date: May 8, 2026 (the prompt and `src/data/sections.ts`
  said May 2, 2026 -- that date is also wrong).
- Unemployment rate, April 2026: **6.9%** (NOT 6.1%).
- Verbatim: "Employment was little changed in April (-18,000; -0.1%)"
  and the unemployment rate rose 0.2 pp to 6.9%.
- Employment level, April 2026: 21,034,000.
- Monthly employment change: -18,000 (-0.1%).
- Participation rate: 65.0% (up 0.1 pp m/m, down 0.3 pp Y/Y).
- Employment rate: 60.5% (down 0.1 pp m/m, down 0.3 pp Y/Y).
- Y/Y employment change: +67,000 (+0.3%).

**Interpretation.**
The 6.1% placeholder is off by 0.8 percentage points. The line as
drafted is materially wrong on the headline number. The release date
in `src/data/sections.ts` (May 2, 2026, encoded as
`Date.UTC(2026, 4, 2, 8, 30)`) is also wrong; the actual release was
May 8, 2026.

**Recommended revision to writer.**
Replace 6.1% with 6.9% and re-anchor the line. Suggested edit:
"Unemployment climbed to 6.9% in April 2026, while the
employment-to-population ratio kept slipping on a yearly basis."
(See Flag 3 below for the supporting employment-rate Y/Y number.)

Both the section blurb body in `src/data/sections.ts` and the tile
line need to be re-anchored against 6.9%. The 6.1% number appears
nowhere in the recent labour series; the trough has been 6.5%
(January 2026); see `boc-tracker/data/unemployment_rate.csv`.

**Confidence:** VERIFIED.

---

## Flag 3. Labour -- per-capita employment Y/Y direction

**Question.** Is per-capita employment falling Y/Y in April 2026? By
how much?

**Primary source(s) consulted.**
- StatCan The Daily, "Labour Force Survey, April 2026" (URL above).
- StatCan The Daily, "Canada's population estimates, fourth quarter
  2025," released March 18, 2026. URL:
  https://www150.statcan.gc.ca/n1/daily-quotidien/260318/dq260318b-eng.htm
- W2 Labour methodology
  (`research/wave2_labour_methodology.md` Section 1).
- boc-tracker mirror `data/employment_rate.csv` (15+ population
  denominator, StatCan SA).

**Resolved values.**
Two defensible expressions of per-capita employment Y/Y are available
for April 2026:

(a) **Employment rate Y/Y change** (cleanest single number,
    matches StatCan's published convention):
  - Employment rate, April 2026: 60.5%
  - Employment rate, April 2025: 60.8%
  - Y/Y change: **-0.3 percentage points** (still falling)
  - Verbatim from StatCan: "The rate was down 0.3 percentage points
    on a year-over-year basis in April."

(b) **Subtractive form** per W2 labour methodology Section 1.1
    (emp_yoy - pop_yoy), using the 15+ population denominator:
    StatCan does not publish 15+ population Y/Y directly in this
    release; total population Y/Y for January 2026 was -0.2% per
    StatCan Daily 2026-03-18. The subtractive form using total
    population gives:
      emp_yoy(Apr 2026) - pop_yoy(Q4 2025)
      = +0.3% - (-0.2%)
      = +0.5 pp
    This number is **positive** because the 15+-population proxy
    via total-population is dragged down by the NPR-driven decline
    in total population. The 15+ population denominator (which
    excludes the under-15 sub-population, where natural-increase
    dynamics differ) likely produced a different value; without the
    explicit Apr-over-Apr 15+ population estimate, the subtractive
    form is misleading at the April 2026 reference month.

**Interpretation.**
The cleanest single number for "per-capita employment kept falling
Y/Y" is the **employment rate Y/Y change of -0.3 pp** -- StatCan
publishes it directly, it uses the correct 15+ denominator, and it
is the verbatim attestation in the May 8 release. The subtractive-
form derivation using total population gives a misleading
positive number because total population (denominator includes
under-15s and reflects NPR-driven decline) is not the LFS
denominator.

**Recommended revision to writer.**
- Use the employment-rate-Y/Y framing, not the per-capita-employment
  language. Suggested: "the employment rate kept slipping on a
  yearly basis."
- If the writer wants per-capita-employment language explicitly, the
  defensible anchor is the employment rate (which IS the per-15+-
  capita employment ratio); the subtractive form using total
  population should not be used for this reference month.
- The cross-section panel deep-dive (Pillar E) should resolve which
  denominator the section uses canonically; for the tile line, the
  employment-rate framing is unambiguous and primary-source-published.

**Caveat to surface in methodology footnote (writer's note, not on
the tile).**
Total Canadian population fell -0.2% Y/Y as of January 1, 2026
(StatCan, March 18, 2026 release) -- driven by NPR outflows. This
makes the subtractive-form per-capita employment metric
counterintuitively positive when total population is the denominator.
The W2 methodology specifies total population as the LFS denominator
for per-capita measures (BoC MPR convention); the April 2026 numbers
suggest the convention should be revisited or annotated. Pillar E
DD scope.

**Confidence:** STRONG. (Employment-rate Y/Y is VERIFIED. Subtractive-
form direction is sensitive to denominator choice; the writer should
use the employment-rate framing to avoid the denominator ambiguity.)

---

## Flag 4. Housing -- MLS HPI Y/Y for April 2026

**Question.** What is the MLS HPI Y/Y for April 2026? Is the
placeholder -1.4% correct?

**Primary source(s) consulted.**
- CREA national release index page:
  https://stats.crea.ca/en-ca/ (April 16, 2026 release with March
  2026 data) and https://creastats.crea.ca/en-ca/.
- CREA 2026 publication schedule.
- boc-tracker mirror `data/crea_mls_hpi.csv` (through Feb 2026).

**Resolved values.**
- **The April 2026 CREA release does not yet exist as of 2026-05-11.**
  The next CREA national statistics release is scheduled for
  **May 14, 2026** -- three days after the writer's draft date.
- Latest available CREA print is for March 2026 (released April 16,
  2026):
  - National Composite MLS HPI Y/Y: **-4.7%** (NSA).
  - M/M change: -0.4%.
  - Average price: $673,084 (down 0.8% Y/Y, NSA).
- Verbatim CREA: "The non-seasonally adjusted National Composite
  MLS HPI was down 4.7% compared to March 2025."

**Consecutive-negative-print count.**
- boc-tracker mirror's MLS HPI (SA) Y/Y has been negative every
  month from **April 2024 through February 2026** -- 23 consecutive
  months of negative Y/Y as of the last boc-tracker observation.
- CREA's NSA series shows the same directional pattern (the agency
  has been reporting negative Y/Y prints since around the same
  window).
- The series has NOT shallowed toward zero -- the most recent CREA
  release (March 2026) at -4.7% is the deepest Y/Y decline in the
  current run.

**Interpretation.**
The "-1.4% April 2026" anchor is incorrect on two counts:
1. April 2026 has not been published yet (the April-data CREA release
   lands May 14, 2026).
2. The latest published Y/Y (-4.7%, March 2026) is materially deeper
   than -1.4%.

**Recommended revision to writer.**
- If the tile line ships before May 14, 2026, anchor to the
  March 2026 print: "MLS HPI fell 4.7% year-over-year in March
  2026, with the national benchmark deep in negative territory."
- If the tile line can wait until May 14, 2026, anchor to the actual
  April print once released.
- The "still in negative territory" tail is well-supported on the
  consecutive-negative-print history (23 months and counting).

**Confidence:** VERIFIED for March 2026 (-4.7% Y/Y); the April 2026
value cannot be sourced because the release has not landed.

---

## Flag 5. Markets -- USDCAD percentile vs post-1990 distribution

**Question.** What percentile does the latest USDCAD print sit at
versus the daily distribution since 1990?

**Primary source(s) consulted.**
- BoC Valet FXUSDCAD daily series (current methodology, 2017
  onward).
- boc-tracker mirror `data/usdcad.csv` (curated daily series
  1990-01-02 through 2026-05-01 with the legacy noon-rate
  IEXE0101 stitched to FXUSDCAD at the April 2017 methodology
  break).
- Reproducible derivation:
  `analyses/usdcad_percentile_2026_05_11.py` and
  `analyses/usdcad_percentile_addendum.py`.

**Resolved values.**
Latest USDCAD observations and their post-1990 empirical percentile
rank (N = 9,118 daily observations from 1990-01-02 through
2026-05-01):

| Date         | Value  | Post-1990 percentile |
|--------------|--------|----------------------|
| 2026-05-01   | 1.3575 | 67.3                 |
| 2026-05-08*  | 1.3686 | 72.3                 |

*Valet FXUSDCAD 2026-05-08 close; latest business day available.
2026-05-09 is a Saturday -- there is no May 9 BoC FX print.

Reference quantile points from the post-1990 distribution:
- q=0.50 (median): 1.3072
- q=0.75: 1.3745
- q=0.80: 1.3887
- q=0.90: 1.4815
- q=0.95: 1.5386

**Interpretation.**
The Markets section blurb in `src/data/sections.ts` claims
"USDCAD is sitting at the 80th percentile of the post-1990
distribution" -- the actual percentile at the May 8 close is
~72nd, and at the May 1 close (the last boc-tracker observation)
is ~67th. The 80th-percentile claim is wrong on the current spot:
the 80th-percentile reference value is 1.3887, well above
either the May 1 (1.3575) or May 8 (1.3686) close.

Note the "USDCAD closed at 1.378 on May 9, 2026" anchor in both
the writer's tile-line draft and the placeholder layer in
`src/data/sections.ts` is doubly wrong:
- May 9, 2026 is a Saturday; BoC does not publish FX on weekends.
- Even at a hypothetical 1.378 spot value, the percentile is ~77th,
  below the 80th percentile threshold cited in the section blurb.

**Recommended revision to writer.**
If the writer wants the percentile-classifier framing, the
defensible version on the May 8 close is:
"USDCAD closed at 1.3686 on May 8, 2026 -- around the 72nd
percentile of its post-1990 distribution."

(Word count of that exact line: 16 -- within spec. Note the
deliberate avoidance of the "80th percentile" assertion in the
section blurb; that claim is not supported at current spot.)

**Confidence:** VERIFIED (derivation is reproducible from
the script and the boc-tracker mirror; methodology break at
April 2017 between IEXE0101 and FXUSDCAD acknowledged but
immaterial for distribution-percentile context).

---

## Flag 6. Trade -- consecutive-deficit count and March 2026 value

**Question.** What is the actual March 2026 merchandise trade
balance? What is the consecutive-monthly-deficit run as of the
most recent print?

**Primary source(s) consulted.**
- StatCan The Daily, "Canadian international merchandise trade,
  March 2026," released May 5, 2026. URL:
  https://www150.statcan.gc.ca/n1/daily-quotidien/260505/dq260505a-eng.htm
- Prior monthly releases (Sept 2025 to Feb 2026) for the run-up
  history.
- boc-tracker mirror `data/trade_balance_total.csv`.

**Resolved values.**

| Month     | Trade balance     | Comment                               |
|-----------|-------------------|---------------------------------------|
| Sep 2025  | +$0.5B (surplus)  | Original $153M; boc-tracker mirror $482M (revised) |
| Oct 2025  | -$0.9B            | Deficit run begins                    |
| Nov 2025  | -$2.4B            |                                       |
| Dec 2025  | -$0.8B            |                                       |
| Jan 2026  | -$3.2B            |                                       |
| Feb 2026  | -$5.1B            | "Largest deficit since August 2025"   |
| Mar 2026  | **+$1.8B (surplus)** | **Run breaks**                     |

Verbatim from StatCan Daily 2026-05-05: "This is the first trade
surplus since September 2025."

**Interpretation.**
The writer's "March merch trade balance widened to -$2.3B,
with auto and energy pulling in opposite directions" is wrong
on two counts:
1. The March 2026 print is a $1.8B SURPLUS, not a -$2.3B deficit.
2. The run of monthly deficits was Oct 2025 - Feb 2026 (five
   consecutive months), and it BROKE in March 2026 -- not extended.

The placeholder values in `src/data/sections.ts` for the Trade
section (Mar 2026 -$2.3B, "extending the run of deficits") are
both materially wrong.

**Recommended revision to writer.**
Replace with the actual print and the actual narrative:
"Merch trade flipped to a $1.8B surplus in March 2026, breaking a
five-month run of deficits."
(Word count: 14, within spec.)

The "auto and energy pulling in opposite directions" detail in
the `sections.ts` blurb body needs to be re-anchored against the
actual March data; the May 5 release identifies the export-side
gain as the driver of the surplus (exports +8.5% M/M; imports
-1.6% M/M).

**Confidence:** VERIFIED.

---

## Flag 7. Markets -- weekly cadence / direction of trend

**Question.** Is "drifting weaker through the spring" supported by
the BoC daily USDCAD over the past 90 days?

**Primary source(s) consulted.**
- BoC Valet FXUSDCAD daily, 2026-02-09 through 2026-05-08
  (fetched via Valet observations endpoint).
- boc-tracker mirror `data/usdcad.csv` (same series; ends
  2026-05-01).
- Reproducible derivation:
  `analyses/usdcad_percentile_2026_05_11.py`.

**Resolved values.**
90-day window (boc-tracker mirror, calendar 2026-02-02 through
2026-05-01):
- Open: 1.3677 (2026-02-02)
- Close: 1.3575 (2026-05-01)
- 90-day high: 1.3953 (2026-03-31)
- 90-day low: 1.3533 (2026-02-10)
- Net change open-to-close: -0.0102 (-0.75%)
- Latest vs 90-day high: -0.0378 (-2.71%)

Spring window (March 1 - May 1):
- Open: 1.3705 (2026-03-02)
- Close: 1.3575 (2026-05-01)
- Spring high: 1.3953 (2026-03-31)
- Spring low: 1.3562 (2026-03-10)
- Net spring change: -0.0130 (-0.95%, CAD strengthened)

Valet extension to May 8: USDCAD = 1.3686 (the close at the spring's
end has retraced part of the strengthening).

**Interpretation.**
"Drifting weaker through the spring" is the OPPOSITE of what the
data shows. From the open of the spring window (1.3705 on March 2)
to the most recent boc-tracker observation (1.3575 on May 1), the
CAD STRENGTHENED -- USDCAD fell roughly 1%. The spring high (1.3953)
was at the very end of March, and the rate has been mean-reverting
since.

The sparkline in `src/data/sections.ts` (1.348 -> 1.378 over 24
points) does show a weakening pattern, but those values do not
match the actual BoC FXUSDCAD daily series for the past month --
they appear to be a synthetic placeholder, not a real series.
boc-tracker's last 24 daily observations (April 1 - May 1 2026)
walk 1.3888 -> 1.3575 -- a CAD-strengthening pattern.

**Recommended revision to writer.**
Replace "drifting weaker through the spring" with a percentile or
mean-revert framing that the data actually supports. Two options:

Option A (percentile classifier, defensible):
"USDCAD closed at 1.3686 on May 8, 2026 -- around the 72nd
percentile of its post-1990 distribution."

Option B (mean-revert framing):
"USDCAD closed at 1.3686 on May 8 after retracing from a March 31
spring high of 1.3953."

Either option avoids the "drifting weaker" claim, which is not
supported by the primary-source daily series.

**Confidence:** VERIFIED (the direction of trend is unambiguous in
the 90-day boc-tracker daily series; the "drifting weaker"
characterization is contradicted by the data).

---

## Per-flag summary table

| Flag | Topic              | Placeholder        | Verified value       | Confidence |
|------|--------------------|--------------------|----------------------|------------|
| 1    | Inflation framing  | "shelter doing the work" | Shelter 1.7% (below headline); energy 3.9% + food 4.0% leading | VERIFIED |
| 2    | Labour UR Apr 2026 | 6.1% (May 2)       | 6.9% (May 8 release) | VERIFIED   |
| 3    | Per-capita emp Y/Y | "kept falling"     | Emp rate -0.3 pp Y/Y | STRONG     |
| 4    | MLS HPI Apr 2026   | -1.4%              | Apr not yet released; Mar -4.7% Y/Y; consecutive negative since Apr 2024 | VERIFIED (Mar print) |
| 5    | USDCAD percentile  | 80th               | 67th (May 1) / 72nd (May 8) | VERIFIED |
| 6    | Trade Mar 2026     | -$2.3B, "extending" | +$1.8B surplus, broke 5-month run | VERIFIED |
| 7    | Markets cadence    | "drifting weaker"  | CAD strengthened ~1% from spring open; 90d high 1.3953 Mar 31 | VERIFIED |

**Unresolved flags:** none. All seven flags have a primary-source
anchor; for flag 4, the April 2026 CREA print is not yet released
(scheduled May 14, 2026), so the writer's choice is between (a)
re-anchoring to March 2026 -4.7% Y/Y, or (b) holding the tile-line
draft pending the May 14 release.

---

## Cross-cutting note: stale data in `src/data/sections.ts`

The placeholder values in `src/data/sections.ts` for several sections
are materially wrong against today's primary sources:

- **Labour.** Encodes Apr 2026 UR = 6.1%, release date May 2; actual
  6.9%, release May 8. Both numbers in the section's `prints` array
  and the blurb body need re-anchoring.
- **Housing.** Encodes Apr 2026 HPI Y/Y = -1.4%; actual March 2026
  print is -4.7% Y/Y, and April 2026 print not yet released.
- **Markets.** Encodes May 9, 2026 USDCAD = 1.378 (Saturday, no
  print); actual May 8 close = 1.3686. The blurb's "80th percentile
  of the post-1990 distribution" claim is unsupported at current
  spot.
- **Trade.** Encodes March 2026 trade balance at -$2.3B; actual is
  **+$1.8B surplus**.
- **Inflation.** Encodes "Shelter is still doing most of the work,
  with mortgage interest cost the largest single contributor" --
  contradicted by W3-R2 Panel 4 (shelter 1.7% Y/Y, MIC 0.3% Y/Y).

These corrections need to flow to whoever owns the backend data
pipeline (per the file header, backend-engineer). The writer's
tile-line v1 draft is downstream of these placeholders; the
tile-line accuracy will track the data-layer accuracy once those
flow through.

---

## Reproducibility

Primary-source URLs:
- https://www150.statcan.gc.ca/n1/daily-quotidien/260420/dq260420a-eng.htm (CPI Mar 2026)
- https://www150.statcan.gc.ca/n1/daily-quotidien/260508/dq260508a-eng.htm (LFS Apr 2026)
- https://www150.statcan.gc.ca/n1/daily-quotidien/260318/dq260318b-eng.htm (Population Q4 2025)
- https://www150.statcan.gc.ca/n1/daily-quotidien/260505/dq260505a-eng.htm (Trade Mar 2026)
- https://www150.statcan.gc.ca/n1/daily-quotidien/260402/dq260402a-eng.htm (Trade Feb 2026)
- https://www150.statcan.gc.ca/n1/daily-quotidien/251211/dq251211b-eng.htm (Trade Sep 2025)
- https://stats.crea.ca/en-ca/ (CREA Mar 2026 release; April 16, 2026)

Derivation scripts:
- `analyses/usdcad_percentile_2026_05_11.py` -- USDCAD post-1990
  percentile + 90-day direction stats.
- `analyses/usdcad_percentile_addendum.py` -- percentile for the
  May 8 Valet close (1.3686) and other candidate spot values.

Data inputs (boc-tracker mirrors of primary sources):
- `C:\Users\jayzh\Documents\boc-tracker\data\usdcad.csv` (1990-2026, daily)
- `C:\Users\jayzh\Documents\boc-tracker\data\unemployment_rate.csv` (LFS)
- `C:\Users\jayzh\Documents\boc-tracker\data\employment_rate.csv` (LFS)
- `C:\Users\jayzh\Documents\boc-tracker\data\trade_balance_total.csv` (StatCan 12-10-0011-01)
- `C:\Users\jayzh\Documents\boc-tracker\data\crea_mls_hpi.csv` (CREA, through Feb 2026)

End of pack.
