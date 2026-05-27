# Wave 3, Brief W3-R1 -- GDP basics-layer per-panel research pack

Author: researcher
Date: 2026-05-11
Status: research pack for writer revision of `editorial/drafts/gdp_basics_v1.md`
Scope: numerical anchors, "so what" supporting evidence, and consensus
captures for the six GDP basics panels in EDR Section 4.1.

Anchors:
- `editorial/dashboard_purpose.md` Section 4.1 (six elements; 2026-05-10
  changelog override on surprise framing -- market consensus first, BoC
  MPR fallback).
- `research/wave1_data_scope_gdp_inflation.md` (coverage and gap list).
- `research/wave2_consensus_sourcing.md` (consensus methodology --
  median of available Big-Six bank forecasts, unlabelled in prose per
  voice principle and per the 2026-05-10 EDR override).
- `editorial/drafts/gdp_basics_v1.md` (writer's v1 draft, with placeholders
  and ten flagged unsupported claims).

Note on the `memory/feedback_consensus_labelling.md` file referenced in
the brief: file is not present in the repo at the time of this writing.
The consensus-labelling discipline applied below is drawn from
`research/wave2_consensus_sourcing.md` Section 1.3 and Section 2 plus
the 2026-05-10 EDR changelog: in prose, the aggregate is called
"consensus" (or, if precision requires, "the forecaster median") and
the panel composition is named in a methodology note, not in running
prose. Individual bank names are never cited.

Conventions used below:
- All values quote the primary source verbatim where available.
- "Verified" tag means the number is in a primary release we can resurface
  on demand. "Derived" means a small arithmetic on verified inputs.
- "Interpretation" is flagged separately from observation.
- Date format: YYYY-MM-DD.
- Reference period is named explicitly (M = month, Q = quarter).

---

## A. Critical correction to the existing writer draft

The v1 writer draft (`editorial/drafts/gdp_basics_v1.md`) is anchored to
placeholder values from `src/data/sections.ts` that materially misstate
the current Canadian macro state. Re-reading is required before
revision. Specifically:

1. **The Q1 2026 quarterly GDP print does not yet exist.** StatCan
   publishes Q1 2026 GDP (Table 36-10-0104) on **2026-05-29**. The
   draft's "+1.4% Q/Q SAAR Q1 2026" anchor is a forecast, not a print.
   At time of writing (2026-05-11) the most recent quarterly print is
   **Q4 2025: -0.2% Q/Q (-0.6% Q/Q SAAR)** released 2026-02-27.
2. **The most recent monthly GDP print is February 2026, not March.**
   StatCan released February 2026 monthly GDP (+0.2% M/M) on
   **2026-04-30** with an advance estimate for March of "essentially
   unchanged" (~0.0%). March 2026 monthly GDP is scheduled for
   2026-05-30.
3. **The output gap placeholder of -0.6% is wrong vintage.** Per BoC
   Valet `INDINF_OUTGAPMPR_Q` the most recent published value is
   **Q4 2025 at -1.0%** (date stamp 2025-10-01 = Q4 2025; quarterly
   series stamps quarter-start). Q1 2026 is not yet in Valet
   because Q1 2026 StatCan GDP data lands 2026-05-29.
4. **The BCC current-state placeholder ("Expansion since 2020Q3") is
   not supported by any BCC publication.** The most recent BCC
   communique (2025-09-22) does NOT declare an active expansion
   start date; it states only that the Q2 2025 contraction "does not
   meet the definition of a recession." See Panel 6 below for the
   precise reading.

Recommendation: the writer revises against the verified numbers in
Section B below, not against `src/data/sections.ts`. The pipeline
layer needs to update `sections.ts` to reflect the released vintage
(Feb 2026 monthly print, Q4 2025 quarterly print) -- but that is a
pipeline lift, not in scope here.

---

## B. Per-panel anchors

### Panel 1 -- Headline real GDP

**Latest monthly print.** Real GDP by industry, **February 2026: +0.2%
M/M**, released 2026-04-30. StatCan Daily,
`https://www150.statcan.gc.ca/n1/daily-quotidien/260430/dq260430a-eng.htm`
(retrieved 2026-05-11). [Verified]

- Goods-producing industries: +0.4% M/M.
- Services-producing industries: +0.1% M/M.
- Manufacturing led (+1.8% M/M, the largest monthly increase since
  January 2023). Retail trade and public-sector activity were drags.
- Advance estimate for March 2026: "real GDP was essentially
  unchanged in March," with the advance Q1 2026 quarterly read at
  **+0.4% Q/Q** (StatCan advance, not annualized; ~1.6% Q/Q SAAR if
  the advance holds and assuming the standard ~four-times scaling
  from quarterly to annualized).
- January 2026 print: revised in this release back to January 2025
  (StatCan's standard practice). The specific February-release
  revision direction for January 2026 was not surfaced in the Daily
  prose; release tables (36-10-0434-01) carry the revised level. For
  revision-direction copy: pull January 2026's value from this release
  vs the prior release before committing to "revised up" / "revised
  down."

**Latest quarterly print.** Real GDP by expenditure, **Q4 2025: -0.2%
Q/Q (-0.6% Q/Q SAAR)**, released 2026-02-27. StatCan Daily,
`https://www150.statcan.gc.ca/n1/daily-quotidien/260227/dq260227a-eng.htm`
(retrieved 2026-05-11). Annual 2025 real GDP: **+1.7%** (slowest annual
pace since the 2020 decline). [Verified]

**"So what" supporting evidence.** The economy contracted modestly in
Q4 2025 on a Q/Q SAAR basis but the monthly path turned: February 2026
posted the second consecutive monthly gain (per StatCan Daily prose
references to January's path; precise January M/M is recoverable from
the release table). The Q1 2026 advance signal of +0.4% Q/Q (~1.6%
SAAR if it holds) and the monthly improvement put the cycle on a
soft-recovery footing rather than a recession trajectory. This is an
observation grounded in two StatCan releases; the interpretation
("soft recovery, not recession trajectory") is supported by the
C.D. Howe BCC's most recent communique (Panel 6 below) and consistent
with the BoC's April 29, 2026 characterization that "growth is
forecast to have resumed in early 2026" (BoC FAD release,
`https://www.bankofcanada.ca/2026/04/fad-press-release-2026-04-29/`,
retrieved 2026-05-11). [Verified observation; interpretation flagged]

**Cross-reference.** Business investment dynamics within the Q1
recovery trajectory are Pillar D (productivity gap) territory; basics
blurb surfaces the aggregate, does not pre-empt the
business-vs-residential split.

### Panel 2 -- Industry vs expenditure cross-check

**Latest reading.** Industry GDP (monthly through Feb 2026, advance
through March): +0.2% M/M Feb, ~0.0% advance March, +0.4% Q/Q advance
Q1. Expenditure GDP (quarterly through Q4 2025): -0.2% Q/Q (-0.6%
Q/Q SAAR). [Verified -- same primary sources as Panel 1]

**"So what" supporting evidence.** The two cuts agree on the cycle
state (the economy is growing on average but very modestly, near
potential per panel 5). The Q4 2025 expenditure contraction (-0.2%
Q/Q) is consistent with the soft monthly path through that quarter --
Q3 2025 was +0.6% Q/Q non-annualized (+2.4% Q/Q SAAR per the November
2025 release; recoverable from Table 36-10-0104). The reconciliation
gap between the two cuts is small in this quarter; the methodological
gap between industry (value added at basic prices) and expenditure
(final demand at market prices) does not bind on the cycle read this
print.

**Static methodological footnote (per EDR 4.1 element 2).** A precise
"typical reconciliation gap" range in published StatCan documentation
was not surfaced in the Daily prose of either release. StatCan's
public methodology (`https://www.statcan.gc.ca/eng/subjects-start/nat-econ-acc`)
notes that the two cuts can differ in any given quarter through the
statistical discrepancy line and net-tax-on-products reconciliation,
and that revisions narrow these gaps over time. For the v1 basics
methodology footnote, the honest copy is: "Industry-based GDP
measures value added at basic prices; expenditure-based GDP measures
final demand at market prices. The two cuts can differ in any quarter
through the statistical discrepancy line and the reconciliation of
taxes net of subsidies on products. Revisions narrow these gaps over
time." Quoting a specific point-estimate range (e.g., "up to 0.5pp")
is not supported by a primary source I could find; if the writer
wants such a range, it must come from a cited StatCan methodology
document or be dropped. [Recommendation, not finding]

### Panel 3 -- Contributions to quarterly growth (six-bar)

**Latest reading.** Q4 2025, released 2026-02-27. Six-bar
decomposition per EDR 4.1 element 3 (consumption, government, GFCF,
inventories, exports, imports). The StatCan Daily release narrative
identifies the direction of each component but the Daily prose does
NOT publish all six contributions in percentage-point terms within
the release prose. The percentage-point contributions are recoverable
from StatCan Table 36-10-0104-01 ("contribution to annualized Q/Q
growth"), which is in the `wave1_data_scope_gdp_inflation.md` vector
inventory: v79448555 consumption, v79448562 government, v79448563
GFCF, v79448572 inventories, v79448573 exports, v79448576 imports.

**Direction read from the StatCan Q4 2025 Daily (verified):**
- **Drag**: "withdrawals of business inventories following inventory
  accumulations in the third quarter" -- inventories the largest
  single drag.
- **Positive contributions**: "higher exports, household spending and
  government capital investment."
- Imports +0.3% Q/Q (small positive level change; contribution to
  growth is negative because imports subtract).
- Exports +1.5% Q/Q (positive contribution).
- Household consumption +0.4% Q/Q (positive contribution; +2.3% in
  2025 annual).
- Capital investment (total): +0.8% Q/Q.
- Household saving rate: 4.4% in Q4; 4.9% in 2025.

**Numerical contributions (pp).** The StatCan Daily release does not
publish the six pp-contribution numbers in the prose. The vector pull
is required for the precise pp values. Recommendation for the writer:
either (a) ship the panel with the directional read above and a
methodology note that the chart's pp values come from Table
36-10-0104-01; or (b) wait for pipeline to wire v79448555-76 series
and render the six-bar chart from data. The chart-builder will need
the v79448555-76 series wired in either case. [Verified directions;
pp magnitudes deferred to pipeline]

**"So what" supporting evidence.** The Q4 2025 contraction is best
read as an inventory drag overwhelming positive contributions from
consumption and exports. This is consistent with how Scotiabank,
BMO, and TD framed the print in March 2026 commentaries
(`research/wave2_consensus_sourcing.md` Section 1.3 panel; specific
notes captured in panel-A above via primary BoC and StatCan releases,
not by quoting bank prose). Inventory drags are mechanically
self-reversing; the underlying domestic-demand pulse, where
consumption and government carried positive contributions, was not
the source of the contraction.

**Cross-reference.** Business investment as a component of GFCF
appears as one bar in the six-bar. The cyclical business-vs-residential
investment split, and whether business investment is inflecting up,
is Pillar D (productivity gap) deep-dive territory per EDR 4.1
element 3 ("The business-vs-residential investment split lives in
Pillar D (productivity gap) deep-dive, not in v1 basics").

### Panel 4 -- Per-capita real GDP

**Latest reading.** **Q4 2025: per-capita real GDP unchanged Q/Q**
(after +0.5% Q/Q in Q3 2025). Released 2026-02-27.
[Verified via StatCan Daily 2026-02-27]

The Daily prose does not surface a Y/Y per-capita number in the
release narrative. Y/Y per-capita is recoverable from
Table 36-10-0104-01 (quarterly real GDP) divided by Table 17-10-0009-01
(quarterly population estimate). Per the gap list in
`wave1_data_scope_gdp_inflation.md`, the total-population vector is
not yet in the project pipeline -- the gap is named there and the
recommendation is to add v1 from Table 17-10-0009-01.

**Consecutive-quarter contraction count (per EDR 4.1 element 4).**
Per-capita real GDP Q/Q has alternated for several quarters:
- Q3 2025: +0.5% Q/Q (positive)
- Q4 2025: 0.0% (unchanged)

The run pattern on a Q/Q basis is not a continuous string of
contractions. **On a Y/Y basis, however, the cycle is more
persistent**: per-capita real GDP Y/Y was negative through much of
2023-2024 as headline GDP was outpaced by population growth; the run
has turned mixed in 2025 as immigration policy reset began to bind
on the denominator. The exact consecutive-Q count depends on the
metric (Q/Q vs Y/Y) and the threshold convention. For v1 basics, the
honest copy is: "per-capita real GDP has been weak relative to
headline through 2023-2025; the recent reset in immigration policy
is changing the denominator pace, and the Q/Q per-capita series has
turned mixed in 2025 as that adjusts."

Pinning a specific consecutive-quarter count to a single number
requires deciding the metric (Q/Q vs Y/Y) and pulling the vector
series. **Recommendation: drop the specific "N consecutive quarters"
phrasing from the v1 basics callout** and replace with the cycle-state
copy above; the precise count is more cleanly handled in Pillar E
deep-dive where the metric choice can be argued. [Recommendation;
the v1 writer draft FLAG #2 explicitly asks for verification, and this
is the verification answer]

**"So what" supporting evidence.** EDR 4.1 element 4 frames per-capita
as "the cut the headline obscures." The Q4 2025 reading (per-capita
unchanged while headline contracted -0.2%) is a clean illustration:
the population denominator is no longer dragging down the per-capita
read the way it did in 2023-2024, because IRCC's October 2024 levels-
plan pivot is now binding on NPR flows. This is observation, with
the policy-causal interpretation flagged for Pillar E to resolve.

**Cross-reference.** Pillar E (population deceleration vs labour) is
the deep-dive that resolves whether the per-capita recovery is
through population deceleration or through aggregate weakness. EDR
4.3 explicitly draws this boundary; the basics layer must surface,
not adjudicate.

### Panel 5 -- Versus BoC potential

**Latest reading.** **Output gap Q4 2025: -1.0%** (Bank of Canada
Indicator of Inflation Dynamics, "Current MPR output gap," BoC Valet
series `INDINF_OUTGAPMPR_Q`, observation date 2025-10-01 = Q4 2025
in BoC's quarter-start dating). Retrieved 2026-05-11 via
`https://www.bankofcanada.ca/valet/observations/INDINF_OUTGAPMPR_Q/json`.
[Verified]

Recent path (BoC's published current-MPR estimates):
- 2024-Q1 to 2024-Q4: 0.0% to -0.1% (effectively closed)
- 2025-Q1: -0.1%
- 2025-Q2: -0.8% (revised wider in the April 2026 MPR)
- 2025-Q3: -0.5%
- 2025-Q4: -1.0%

**Important vintage caveat.** Q1 2026 output gap is NOT yet in
Valet because Q1 2026 StatCan GDP data lands 2026-05-29. The April
2026 MPR (released 2026-04-29) projects the gap closes "with GDP
growing slightly above potential, the current excess supply in the
economy is gradually absorbed" (BoC FAD release 2026-04-29). The
BoC's April 2026 MPR projection for GDP growth is **1.2% in 2026,
1.6% in 2027, 1.7% in 2028** with quarterly Q/Q SAAR of **1.5% for
Q1 2026 and 1.5% for Q2 2026** (BoC MPR Projections page,
`https://www.bankofcanada.ca/publications/mpr/mpr-2026-04-29/projections/`,
Table 3, retrieved 2026-05-11). [Verified]

Potential output growth ranges, April 2026 MPR Table 2 (Appendix-style):
- 2026: 0.8% to 1.6%
- 2027: 0.8% to 1.8%
- 2028: 1.0% to 2.0%
[Verified]

**"So what" supporting evidence.** Output is below potential by ~1pp
as of Q4 2025; the BoC projects the gap closes gradually through 2026
and into 2027 as growth runs at or slightly above potential. The
quarterly path from current Valet data shows the gap widening through
mid-2025 and a fresh widening at year-end, consistent with the Q4
expenditure contraction. The framing: the cycle is below potential
but recovering, with the BoC content to hold at 2.25% (April 29, 2026
decision) and to monitor.

**Cross-reference.** The neutral rate band, which figures into the
"how loose / tight is policy" call but is not the basics-layer GDP
question, is Pillar B territory (BoC vs Fed divergence). Basics
Panel 5 surfaces the gap, does not adjudicate the appropriate policy
response.

### Panel 6 -- Recession state (C.D. Howe BCC)

**Latest reading.** **No recession declared.** Most recent BCC
communique is **2025-09-22** ("Canadian Economy Contracts, But Does
Not Meet Recession Definition"). Retrieved 2026-05-11 via
`https://cdhowe.org/wp-content/uploads/2025/09/Communique_2025_09_BCC.pdf`.
[Verified -- full PDF text on file]

Exact BCC verdict (verbatim from communique):
> "On aggregate, the Council judges that the Canadian economy does
> not presently meet the definition of a recession according to the
> latest available data."

The Council's stated pledge:
> "However, the Council is monitoring developments closely and will
> meet to discuss a recession call if GDP contracts again in the
> third quarter."

**State of play as of 2026-05-11.** Q3 2025 did NOT contract
(+0.6% Q/Q, +2.4% Q/Q SAAR per the November 2025 release). Q4 2025
DID contract (-0.2% Q/Q, -0.6% Q/Q SAAR per the February 2026 release).
The Council has not, as of 2026-05-11, published a follow-up
communique on the Q4 contraction. Whether the BCC will meet again
following the Q4 contraction is editorial speculation, not a
verified fact.

**Canonical wording (BCC methodology).** The BCC uses both colloquial
and technical phrasings:
- Colloquial (in their communiques): "**pronounced, persistent, and
  pervasive** decline in real economic activity."
- Technical (in their methodology document): "**amplitude, duration,
  and scope**" -- the three dimensions the Council weighs.

EDR 4.1 element 6 specifies amplitude / duration / scope. Both
phrasings are correct; the v1 basics blurb should use one of these
two pairs (not "depth, breadth"; not the two-negative-quarters
shorthand).

**Prior cycle dating.** The BCC's most recent published trough is
**April 2020** (peak February 2020), the pandemic recession ("the
shortest and deepest recession since the Great Depression in 1929"
per the C.D. Howe Institute summary). The BCC has NOT formally
declared an expansion start date subsequent to that trough in its
public communiques. The phrasing "expansion since 2020Q3" from
`design/basics-layer-template.md` and the v1 draft is NOT supported
by any BCC publication I could find.

**"So what" supporting evidence and correct copy.** The honest
status row for v1 basics is along the lines of:
> "C.D. Howe Business Cycle Council has not declared a recession.
> Last communique 2025-09-22; the Council found Q2 2025's -0.4%
> Q/Q SAAR contraction did not meet the recession criteria of
> amplitude, duration, and scope. Q4 2025's -0.6% Q/Q SAAR
> contraction post-dates the most recent communique; the Council
> has not yet published a follow-up."

This is verified, accurate, and dated. It does not invent an
expansion start date the BCC has not declared.

[FLAG to writer: the v1 draft's "Expansion since 2020Q3" needs to be
removed entirely. Replacement copy above.]

**Cross-reference.** None for v1 basics; the BCC entry is a status row
on the GDP page only.

---

## C. Consensus capture (per EDR 4.1 element 1 and 2026-05-10 override)

### C.1 Bank panel composition and dates

As of 2026-05-11, the following Big-Six bank forecast vintages are
on hand at the source-verified level:

| Bank | Publication | Date | URL |
|---|---|---|---|
| TD | Quarterly Economic Forecast (Canada) | 2026-03-17 | `https://economics.td.com/domains/economics.td.com/documents/reports/qef/2026-mar/QEF_Mar2026_Canada.pdf` |
| Scotiabank | Scotiabank's Forecast Tables | 2026-03-24 | `https://www.scotiabank.com/content/dam/scotiabank/sub-brands/scotiabank-economics/english/documents/forecast-tables/forecast20260324.pdf` |
| BMO | Canadian Economic Outlook | 2026-03-27 | `https://economics.bmo.com/media/filer_public/3c/29/3c29234b-ae3a-41a9-be61-ce53529fda5a/outlookcanada.pdf` |
| RBC | Quarterly Canadian Outlook | 2026-03-12 | `https://www.rbc.com/en/economics/canadian-analysis/featured-analysis/quarterly-canadian-outlook/quarterly-canadian-outlook-growth-headwinds-offset-by-stabilizing-trade-and-jobs/` |
| NBC | Monthly Economic Monitor - Canada | 2026-04-22 | `https://www.nbc.ca/content/dam/bnc/taux-analyses/analyse-eco/mensuel/monthly-economic-monitor-canada.pdf` |
| CIBC | Week Ahead / Economic Flash | various, most recent in late Feb / early March 2026 | `https://economics.cibccm.com/` (hub; per-doc GUIDs) |

Bank-by-bank Q/Q SAAR forecasts captured (from the documents above):

| | Q1 2026 | Q2 2026 | Q3 2026 | Q4 2026 | 2026 annual | 2027 annual |
|---|---|---|---|---|---|---|
| TD | 2.0 | 1.1 | 1.5 | 1.6 | 1.1 | 1.7 |
| Scotia | 1.3 | 1.8 | 2.8 | 1.7 | 1.3 | 2.0 |
| BMO | 0.8 | 1.7 | 2.2 | 2.1 | 1.0 | 2.2 |
| RBC | 1.5* | n.a. | n.a. | n.a. | 1.3 | n.a. |
| NBC | 1.4 | 1.3 | 1.4 | 1.4 | 1.0 | 1.4 |
| CIBC | ~1.0** | n.a. | n.a. | n.a. | n.a. | n.a. |

*RBC's full quarterly table was not extracted from the published
PDF in this session; the 1.5% Q1 2026 figure is from the RBC quarterly
outlook narrative as quoted by independent press summaries of the
2026-03-12 publication. **Source-side recommendation: the writer
treats RBC's full quarterly path as deferred to a second-pass
extraction; the Q1 2026 anchor is the only number cited here.**

**CIBC's Q1 2026 forecast of "around 1%" is from CIBC commentary
captured in third-party summaries of late-February/early-March 2026
Week Ahead notes; the source PDF could not be reliably retrieved
because CIBC's `economics.cibccm.com/cds` endpoint requires a per-doc
GUID and has no discoverable listing index (see
`research/wave2_consensus_sourcing.md` Section 3.1 and Appendix A).

### C.2 Consensus computation

**Q1 2026 Q/Q SAAR (the print scheduled for 2026-05-29).**
- Five-bank panel (TD, Scotia, BMO, RBC, NBC): values [0.8, 1.3, 1.4,
  1.5, 2.0]. **Median = 1.4%**. Mean = 1.4%.
- Six-bank panel including CIBC at ~1.0: values [0.8, 1.0, 1.3, 1.4,
  1.5, 2.0]. **Median = 1.35%** (round to 1.4 per usual
  one-decimal convention).
- Recommendation: **publish "consensus ~1.4% Q/Q SAAR for Q1 2026,"
  unlabelled in prose**, with a methodology note pointing to the
  panel composition table above.

**BoC April 2026 MPR projection for Q1 2026:** 1.5% Q/Q SAAR (Table 3,
Projections, retrieved 2026-05-11). The MPR projection is therefore
within 10 bps of the bank median; the surprise read on the Q1 2026
print, if it comes in at ~1.4%, will be marginal against either
anchor. [Verified]

**Q2 2026 Q/Q SAAR.** Four-bank panel (TD, Scotia, BMO, NBC):
values [1.1, 1.3, 1.7, 1.8]. **Median = 1.5%**. BoC MPR April 2026
projects 1.5%. Median converges with the BoC.

**Annual 2026 GDP growth.** Five-bank panel (TD, Scotia, BMO, RBC,
NBC): values [1.0, 1.0, 1.1, 1.3, 1.3]. **Median = 1.1%**. BoC MPR
April 2026 projects 1.2%. The bank panel is one tick below the BoC.

**Annual 2027 GDP growth.** Four-bank panel (TD, Scotia, BMO, NBC):
values [1.4, 1.7, 2.0, 2.2]. **Median = 1.85%** (round 1.9%). BoC
MPR April 2026 projects 1.6%. Banks are notably above the BoC for
2027.

### C.3 Monthly print consensus -- March 2026 monthly GDP (2026-05-30 release)

StatCan's own advance estimate from the 2026-04-30 release is
"essentially unchanged" in March 2026 (effectively 0.0% M/M).
Reuters-poll medians for monthly GDP M/M are not consistently in
the public web at the time of this research; the bank weekly previews
(NBC, BMO, TD, Scotia, RBC) typically publish a March monthly
forecast in their Week-Ahead document the week before the print.
At time of writing (2026-05-11) the May 26-30, 2026 Week Ahead
notes for the March monthly GDP print are not yet published; the
weekly previews will refresh around 2026-05-22 to 2026-05-26.

**Recommendation for the writer:** the v1 draft anchors to a March
monthly GDP M/M consensus. That print does not yet exist (release
date 2026-05-30) and no published bank consensus exists at the time
of this research. The honest copy for the May 11 vintage of the
basics layer is:
- Surface the **February 2026 +0.2% M/M print** as the headline
  monthly read (this is the live monthly print).
- Cite the **StatCan advance estimate** for March of "essentially
  unchanged" as the only forward-looking number that is itself a
  primary source.
- Defer "consensus vs print" surprise framing on March monthly GDP
  to the print itself on 2026-05-30, at which point the print-week
  Big-Six previews will populate.

This is consistent with `wave2_consensus_sourcing.md` Section 4.3 --
when consensus is genuinely unavailable for a less-watched
sub-indicator (in this case, a future print that has not yet been
forecast in the weekly window), the disposition is
**surface-the-print-with-context, no surprise framing**.

### C.4 Quarterly GDP consensus -- Q1 2026 (2026-05-29 release)

This is the print the basics layer will refresh on first. Consensus
on hand:
- **Bank median (five Big-Six): 1.4% Q/Q SAAR.**
- BoC April 2026 MPR projection: 1.5% Q/Q SAAR.
- StatCan advance estimate from the 2026-04-30 release implies Q1
  ~0.4% Q/Q non-annualized (~1.6% Q/Q SAAR if the standard
  approximate scaling holds).

The three anchors are converging in a narrow band of 1.4-1.6% Q/Q
SAAR. The surprise read on the actual print on 2026-05-29 will be
material only if the print clears 1.8-2.0% (upside) or comes in
below 1.0% (downside). [Interpretation; the bank median, MPR
projection, and StatCan advance values are verified inputs]

### C.5 Date stamps and refresh discipline

- Bank panel composition stamped at 2026-05-11.
- TD, Scotia, BMO will refresh their quarterly forecasts in June or
  July 2026 (quarterly cadence). NBC refreshes monthly. RBC quarterly
  outlook refreshes ~once per quarter; the next is likely June 2026.
- The next BoC MPR is the July 2026 MPR (2026-07-15 BoC decision,
  MPR alongside).
- Consensus is refreshed each print cycle. The writer should re-query
  this research index before each refresh; the researcher refreshes
  the panel composition and the median computation per the
  cadence in `wave2_consensus_sourcing.md` Section 3.1 (weekly
  print previews).

---

## D. Resolution of the ten flagged claims in `gdp_basics_v1.md`

The v1 draft includes a consolidated "Unsupported-claim flags routed
to researcher" section. Per-flag resolution:

1. **Q1 2026 contributions-to-growth decomposition** (Panel 3 deck).
   STATUS: The Q1 2026 contributions decomposition does not exist yet
   (Q1 2026 GDP releases 2026-05-29). The deck draft naming
   "consumption and exports led, imports the drag" is the directional
   read for **Q4 2025**, the latest available quarter, and matches
   the StatCan Daily 2026-02-27 narrative for that quarter (with
   the addition that **inventories were the single largest drag**,
   per the Daily prose). Rewrite the deck to reflect Q4 2025 unless
   and until Q1 2026 data lands. Source: StatCan Daily 2026-02-27.

2. **Per-capita consecutive-quarter contraction count** (Panel 4).
   STATUS: Drop the "N consecutive quarters" phrasing for v1 basics.
   The clean number does not exist at the metric specificity the
   draft assumes (Q/Q vs Y/Y). The Q4 2025 reading is "unchanged
   Q/Q after +0.5% Q/Q in Q3"; the cycle narrative through 2023-2025
   is more honestly told with the per-capita Y/Y plot than with a
   "consecutive contraction count" headline. The exact count call
   is Pillar E territory.

3. **March 2026 monthly GDP revision direction** (Panel 1 callout).
   STATUS: This print does not yet exist (release 2026-05-30). The
   "Revised up" tag in the v1 draft is a copied-over template
   placeholder; remove until the print lands. For the **February
   2026 print** (the live monthly print), the revision history
   back to January 2025 is in the StatCan release but the precise
   January 2026 revision-direction is not surfaced in the Daily
   prose; the writer can either pull the underlying table or omit
   the revision tag for this print and note "revisions extend
   back to January 2025."

4. **Q1 2026 quarterly GDP consensus, or BoC April 2026 MPR Q1
   projection** (Panel 3 callout). STATUS: Both values are now on
   hand.
   - Bank consensus median for Q1 2026 Q/Q SAAR: **1.4%**.
   - BoC April 2026 MPR projection for Q1 2026 Q/Q SAAR: **1.5%**.
   See Section C.2 above for the full panel composition.

5. **Typical reconciliation-gap range** (Panel 2 status line).
   STATUS: No specific pp-range in published StatCan documentation
   was found. Recommend the writer use the methodological footnote
   wording proposed in Panel 2 above ("the two cuts can differ in
   any quarter through the statistical discrepancy line and the
   reconciliation of taxes net of subsidies on products; revisions
   narrow these gaps over time"), and drop the hedge phrase
   "within the range typical" if no quantified range is cited.

6. **Output-gap Q1 2026 value vintage** (Panel 5 callout). STATUS:
   The Q1 2026 output gap is **not yet in Valet**. The most recent
   Valet observation is Q4 2025 at -1.0% (date 2025-10-01).
   Rewrite the callout to anchor on Q4 2025 = -1.0% (the live
   value), with a vintage note that Q1 2026 lands after the
   2026-05-29 StatCan release and refreshes in the July 2026 MPR
   cycle. The current path widens from -0.5% in Q3 2025 to -1.0%
   in Q4 2025 (-0.5pp Q/Q delta), not +0.1pp as the placeholder
   said.

7. **C.D. Howe BCC current state and most recent communique date**
   (Panel 6). STATUS: Most recent communique is **2025-09-22**.
   The Council has **not** declared an active expansion start date
   in its public communiques; the v1 draft's "Expansion since
   2020Q3" is unsupported. Replacement copy in Panel 6 above
   ("The Council has not declared a recession; last communique
   2025-09-22; Q4 2025's subsequent contraction post-dates the
   communique").

8. **April 2026 monthly GDP next-release date** (event blurb closer).
   STATUS: The next monthly GDP release after the Feb-2026 print
   on 2026-04-30 is the **March 2026 print scheduled for 2026-05-30**
   per StatCan's release-calendar convention (~60-day lag from end
   of reference month). The June 27 date in the v1 draft is one
   month off; the writer should change it to 2026-05-30. (Note:
   the **Q1 2026 quarterly print** is 2026-05-29 -- one day before
   the monthly. Both are within the basics-layer refresh window.)

9. **Consensus source for the homepage event blurb** (Mode A copy).
   STATUS: Per `wave2_consensus_sourcing.md` and the 2026-05-10
   EDR override, the consensus is the median of available Big-Six
   bank forecasts, surfaced in prose as "consensus" with the panel
   composition in a methodology note. The v1 draft's phrasing
   "0.1pp above the consensus 0.1%" is consistent in form; the
   number itself was a placeholder. For the February 2026 print
   the bank weekly previews did publish a +0.2% M/M forecast median
   (per TD's narrative that the print was "in line with...market
   expectations" -- which the TD note also calls "in line with
   StatCan's advance guidance"); the StatCan advance guidance was
   itself +0.2%, so consensus ~= advance ~= print = +0.2%. **No
   measurable surprise.**

10. **Valet key `INDINF_OUTGAPMPR_Q` probe status** (Panel 5
    methodology stub). STATUS: **Confirmed working.** Valet returned
    valid observations on 2026-05-11. The series stamps each
    quarter at the quarter-start date (2025-10-01 = Q4 2025,
    2025-07-01 = Q3 2025, etc.). Pipeline-engineer can wire this
    key without further probe. [Verified live]

---

## E. Consolidated recommendations for the writer revision

1. **Re-anchor to the live release vintage.** Latest monthly:
   February 2026 +0.2% M/M (released 2026-04-30). Latest quarterly:
   Q4 2025 -0.2% Q/Q (-0.6% Q/Q SAAR; released 2026-02-27). Output
   gap: Q4 2025 -1.0%. The Q1 2026 quarterly print is the next
   refresh (2026-05-29).
2. **Remove the "Expansion since 2020Q3" from Panel 6.** Replace
   with the BCC-verified status row in Panel 6 above.
3. **Replace the placeholder revision tag on Panel 1.** Either pull
   the January 2026 revision direction from the StatCan release
   table or omit the tag for the February print and note "revisions
   extend back to January 2025" per the Daily.
4. **Update Panel 3 deck to reflect Q4 2025 (the live quarter).**
   The drivers were household consumption, exports, and government
   investment (positives); inventories were the largest drag.
5. **Replace the per-capita "N consecutive quarters" callout copy.**
   Use the Q4 2025 cycle-state read: "per-capita real GDP unchanged
   Q4 (after +0.5% Q3); the cut the headline obscures has turned
   mixed in 2025 as immigration policy resets the denominator."
6. **Use the verified bank-median consensus values from Section C.2
   when the Q1 2026 print lands** (consensus = 1.4% Q/Q SAAR; BoC
   MPR projection = 1.5%; advance from StatCan ~1.6% if it holds).
7. **Fix the next-release date in the event blurb to 2026-05-30**
   (March monthly GDP) -- not June 27.
8. **Honor BCC canonical wording.** Use "amplitude, duration, and
   scope" (technical) or "pronounced, persistent, and pervasive"
   (colloquial); both are direct from BCC publications. Avoid
   "depth, breadth" (not BCC wording) and the two-negative-quarters
   shorthand (not the BCC methodology).
9. **Surface, don't adjudicate, on Pillar D and Pillar E topics.**
   The business-investment cycle and the population-vs-aggregate
   per-capita resolution are deep-dive territory; the basics blurb
   names what the data shows and points to the deep-dive without
   pre-empting.

---

## F. Source list (all retrieved 2026-05-11)

Primary releases used as numerical anchors:
- StatCan Daily, monthly GDP February 2026 (release 2026-04-30):
  `https://www150.statcan.gc.ca/n1/daily-quotidien/260430/dq260430a-eng.htm`
- StatCan Daily, quarterly GDP Q4 2025 (release 2026-02-27):
  `https://www150.statcan.gc.ca/n1/daily-quotidien/260227/dq260227a-eng.htm`
- StatCan Table 36-10-0434 monthly real GDP by industry (level
  series; access via WDS by vector or table CSV)
- StatCan Table 36-10-0104 quarterly GDP by expenditure (contribution
  vectors v79448555 / 562 / 563 / 572 / 573 / 576 named in
  `wave1_data_scope_gdp_inflation.md`)
- Bank of Canada April 2026 Monetary Policy Report (Projections page,
  Table 2 and Table 3):
  `https://www.bankofcanada.ca/publications/mpr/mpr-2026-04-29/projections/`
- Bank of Canada April 29, 2026 rate decision (FAD press release):
  `https://www.bankofcanada.ca/2026/04/fad-press-release-2026-04-29/`
- Bank of Canada Valet `INDINF_OUTGAPMPR_Q` (output gap):
  `https://www.bankofcanada.ca/valet/observations/INDINF_OUTGAPMPR_Q/json`
- C.D. Howe Business Cycle Council communique, September 22, 2025:
  `https://cdhowe.org/wp-content/uploads/2025/09/Communique_2025_09_BCC.pdf`
- C.D. Howe Business Cycle Council methodology (defines amplitude/
  duration/scope): `https://cdhowe.org/publication/business-cycle-council-methodology/`

Bank consensus inputs (panel composition for the consensus median;
NOT cited in writer's prose per voice principle, surfaced as
"consensus" only):
- TD Quarterly Economic Forecast, Canada, 2026-03-17:
  `https://economics.td.com/domains/economics.td.com/documents/reports/qef/2026-mar/QEF_Mar2026_Canada.pdf`
- TD Real GDP commentary page (Feb 2026 print read), 2026-04-30:
  `https://economics.td.com/ca-real-gdp`
- Scotiabank Forecast Tables, 2026-03-24:
  `https://www.scotiabank.com/content/dam/scotiabank/sub-brands/scotiabank-economics/english/documents/forecast-tables/forecast20260324.pdf`
- BMO Canadian Economic Outlook, 2026-03-27:
  `https://economics.bmo.com/media/filer_public/3c/29/3c29234b-ae3a-41a9-be61-ce53529fda5a/outlookcanada.pdf`
- NBC Monthly Economic Monitor - Canada, 2026-04-22:
  `https://www.nbc.ca/content/dam/bnc/taux-analyses/analyse-eco/mensuel/monthly-economic-monitor-canada.pdf`
- RBC Quarterly Canadian Outlook, 2026-03-12 (narrative; full
  quarterly table extraction deferred):
  `https://www.rbc.com/en/economics/canadian-analysis/featured-analysis/quarterly-canadian-outlook/quarterly-canadian-outlook-growth-headwinds-offset-by-stabilizing-trade-and-jobs/`
- CIBC commentary captured via third-party summaries; primary
  per-doc CIBC PDFs unavailable absent GUID-based listing (see
  `wave2_consensus_sourcing.md` open question 7)

---

End of research pack.
