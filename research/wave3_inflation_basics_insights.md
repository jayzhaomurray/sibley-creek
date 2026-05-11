# Wave 3, Brief W3-R2 -- Per-Panel Research Pack for Inflation Basics-Layer Prose

Author: researcher
Date: 2026-05-11
Status: research pack for writer (basics-layer Inflation prose, v1)
Scope: Inflation section, basics layer, six panels per EDR Section 4.2.

Sources of record (all primary):
- StatCan The Daily, "Consumer Price Index, March 2026," released April 20, 2026
  ( https://www150.statcan.gc.ca/n1/daily-quotidien/260420/dq260420a-eng.htm )
- StatCan Table 18-10-0004-01 (CPI NSA, monthly index levels, all major sub-aggregates)
- StatCan Table 18-10-0006-01 (CPI SA, monthly index levels)
- StatCan Table 18-10-0007-01 / "An Analysis of the 2024 CPI Basket Update" (62F0014M)
  for basket weights of the eight major components
  ( https://www150.statcan.gc.ca/n1/pub/62f0014m/62f0014m2024004-eng.htm )
- BoC "Consumer Price Index" page for core measures (trim, median, common Y/Y)
  ( https://www.bankofcanada.ca/rates/price-indexes/cpi/ )
- BoC Canadian Survey of Consumer Expectations, Q1 2026, released April 20, 2026
  ( https://www.bankofcanada.ca/2026/04/canadian-survey-of-consumer-expectations-first-quarter-of-2026/ )
- BoC Business Outlook Survey, Q1 2026, released April 20, 2026
  ( https://www.bankofcanada.ca/2026/04/business-outlook-survey-first-quarter-of-2026/ )
- BoC Monetary Policy Report, April 2026, released April 29, 2026
  ( https://www.bankofcanada.ca/publications/mpr/mpr-2026-04-29/ )
- BoC Valet daily series FXUSDCAD (USDCAD); LFS-Micro composition-adjusted wage
  series (via BoC research releases through Valet)
- TD Economics, Canadian CPI March 2026 commentary (cited as a forecaster input
  for the surprise read; not cited in prose)
  ( https://economics.td.com/ca-cpi )
- NBC Weekly Economic Watch, May 8, 2026 (forecaster input only)
  ( https://www.nbc.ca/content/dam/bnc/taux-analyses/analyse-eco/weekly-economic-watch.pdf )

Conventions:
- All values pulled from the project's existing boc-tracker mirrors of the
  above primary sources; the derivation script is
  `analyses/inflation_anchors_2026_05_11.py` (reproducible).
- Y/Y is on the NSA index for headline and major sub-aggregates (StatCan
  convention). M/M and 3M AR are on the SA index for momentum.
- All values are anchored to the March 2026 reference month (most recent
  print as of 2026-05-11). Next CPI release: April 2026 print, scheduled
  for May 19, 2026 per the StatCan release calendar.
- Per the EDR 2026-05-10 consensus-labelling override and Wave 2
  consensus-sourcing memo: "consensus" in this pack means an aggregated
  median of available Big-Six forecaster medians, never a cited authority.
  See `memory/feedback_consensus_labelling.md` note below.

Note on `memory/feedback_consensus_labelling.md`: the briefed file does not
yet exist on disk at the time of this pack. The principle it captures
(unlabeled "consensus" in prose must be sourced and dated) is in effect via
the EDR 2026-05-10 changelog entry and the Wave 2 consensus-sourcing memo
Section 5 Q3 disclosure recommendation. Treat as in force.

---

## Cross-panel methodology callout

### Go/no-go on basket-weighted derivations (services ex-shelter, goods ex-energy) for v1

**Go.** Two construction paths exist; one of them ships in v1.

Background. StatCan's 2024 CPI basket update (released January 2025;
applied from 2025 reporting onward) publishes basket weights only at the
eight-major-component level: Food 16.72%, Shelter 28.57%, Household
operations / furnishings / equipment 13.46%, Clothing and footwear 4.70%,
Transportation 16.78%, Health and personal care 5.18%, Recreation /
education / reading 10.42%, Alcoholic beverages / tobacco / cannabis
4.17% (sums to 100%, weights of 2023 expenditures, applied from 2025).
StatCan does NOT publish a single downloadable special-aggregate weight
table for services, goods, energy, services-ex-shelter, or
goods-ex-energy. The all-items goods, all-items services, and energy
index series exist in Table 18-10-0004-01 but their implicit weights
are not published as a series.

Construction option (a) -- weighted-residual at the major-aggregate
level. Equation:

  ServicesExShelter_idx[t] =
       ( W_services * Services_idx[t]  -  W_shelter * Shelter_idx[t] )
       / ( W_services - W_shelter )

with W_services, W_shelter taken from the major-aggregate weights as
disclosed in StatCan's 2024 basket-update analytic document (62F0014M).
Goods ex-energy is analogous. This is the standard Bank of Canada
construction. Verified-implementable; requires one new fetcher pull of
Table 18-10-0007-01 to capture the major-aggregate weight vintage and
a single derivation step in `analyze.py`. The risk: shelter and energy
weights are not explicitly listed as standalone series in the eight
major components; shelter is a major component (28.57%) but "services"
and "energy" are special aggregates. The major-aggregate weight for
services (and goods, and energy) must be sourced from StatCan's special
aggregate annex inside the basket-update document, which exists but
is one click deeper. Pipeline-engineer needs to capture that annex once
per five years (basket cycle) and re-stamp the vintage on derived
series. Methodology footnote needs to name the basket vintage and the
weight source.

Construction option (b) -- component-bottom-up. Aggregate the relevant
subset of the 60 components in `data/cpi_breadth_mapping.json`
(which already carries the 2024 weights) that fall under services
ex-shelter (or goods ex-energy), using the component weights stored
there. Requires a taxonomy assignment (which of the 60 components
belong to services-ex-shelter, which to goods-ex-energy). The 60
components total ~99% of the basket, so the residual ~1% must be
imputed or noted as the coverage gap. This is a one-time analyst
assignment, then runs forever.

Recommendation for v1: ship **option (a)** -- weighted-residual at the
major-aggregate level. Reasoning: (i) it matches the BoC's published
construction (BoC SWP series of papers on core measures use the same
algebra), (ii) it's one fetcher addition rather than a 60-row taxonomy
exercise, (iii) the basket-vintage stamp is the only revision risk and
it refreshes only every five years. Option (b) is the v1.5 cross-check
to verify the option-(a) construction reproduces sensible values
component-by-component.

Methodology callout language for the basics page (one click away):
"Services excluding shelter and goods excluding energy are derived
aggregates. We construct them as the weighted residual of the all-
services index less the shelter index, and the all-goods index less
the energy index, using major-aggregate basket weights from StatCan
Table 18-10-0007-01 (2024 basket, applied from January 2025; next
basket update due 2030). The construction is reproducible from the
script in `analyses/`; basket-vintage and weight source are stamped
on each derived value."

**Pre-requisite if any panel slips.** Panel 6 (pass-through watch) is
explicitly gated by EDR 4.2 element 6 on Panel 4's derivations
landing. If pipeline-engineer cannot add the basket-weight pull plus
the residual derivation before launch, Panel 6 defers to v1.5 and
Panel 4 falls back to all-services and all-goods directly (with prose
noting "shelter dominates services; energy dominates goods").

---

## Panel 1 -- Headline CPI

### Latest-print anchors (March 2026 reference month)

| Series | Value | Source |
|---|---|---|
| Headline CPI Y/Y, NSA | 2.4% | StatCan Daily 2026-04-20; computed 2.39% from boc-tracker index levels (167.4 vs 163.5) |
| Headline CPI M/M, NSA | 0.9% | StatCan Daily 2026-04-20; computed 0.90% (167.4 vs 165.9) |
| Headline CPI M/M, SA | 0.5% | StatCan Daily 2026-04-20; computed 0.48% (167.3 vs 166.5) |
| Headline CPI 3M AR, SA | 2.9% | Derived; (167.3 / 165.6) ^ 4 - 1 = 2.92% |
| Prior month Feb 2026 Y/Y | 1.8% | StatCan Daily 2026-04-20 |

### Consensus capture (for surprise framing)

| Indicator | Median forecast | Print | Surprise | Vintage |
|---|---|---|---|---|
| Headline CPI Y/Y | ~2.5% | 2.4% | -0.1pp (cooler) | Pre-print Big-Six and Reuters; TD CPI commentary 2026-04-20 cites "slightly less than consensus" |
| Headline CPI M/M | not separately captured | 0.9% | n/a | not consensus-anchored |
| Core trim Y/Y | not separately captured | 2.2% | n/a | BoC release alongside StatCan |
| Core median Y/Y | not separately captured | 2.3% | n/a | BoC release alongside StatCan |

Capture honesty note: as of 2026-05-11 the Big-Six aggregation pipeline
is not yet built; the surprise read here is sourced from TD Economics
commentary ("slightly less than consensus") and from third-party
recaps citing market expectations at ~2.5%. For v1 launch the
researcher recommendation is: anchor the surprise prose to the
NBC + TD + BMO median once those parsers land (Wave 2 memo Section 6)
and label as such; until then, prose should say "below the consensus
range of around 2.5%" with the date stamp on the consensus, not paper
over it as a precise -0.1pp surprise.

### Methodology hover/footnote content

"Headline CPI Y/Y is StatCan's not-seasonally-adjusted all-items
index (Table 18-10-0004-01, V41690973), computed as the 12-month
percent change. M/M (SA) is computed on Table 18-10-0006-01
(V41690914). 3M annualized is the three-month log-change of the
SA index, annualized geometrically: ((index_t / index_{t-3}) ^ 4) - 1.
Consensus is the median of available Big-Six bank forecaster medians
(NBC, TD, BMO at v1 launch; RBC, Scotia, CIBC as they come online).
BoC MPR central projection is the fallback when consensus is
unavailable."

### So what

Headline at 2.4% Y/Y is just above the BoC's 2% target, accelerated
from 1.8% in February. The February print was anomalous on the low
side (consumer carbon levy removal in April 2024 entered the 12-month
window in March 2025 as a base effect; one year on, in March 2026,
that base effect is unwinding). The 3M AR at 2.9% is the more
diagnostic short-window read -- it strips the carbon-levy unwinding
year-over-year base effect and tells you that the underlying
near-term price-change pulse is mildly above target. The April 2026
print (release scheduled May 19) is expected to step higher on energy
pass-through from the Middle East conflict; BoC's April MPR projects
headline peaking near 3% in April. The BoC's reaction function reads
through this as a supply shock, not a demand-driven re-acceleration.

### Evidence

- StatCan Daily 2026-04-20: "The Consumer Price Index (CPI) rose 2.4%
  on a year-over-year basis in March, up from a 1.8% increase in
  February."
- BoC April 2026 MPR: CPI projected to peak at roughly 3% in April
  2026, with the Brent oil assumption at US$90 in Q2 2026 falling to
  US$75 by mid-2027.
- TD Economics CPI commentary 2026-04-20: "headline CPI inflation
  jumped up to 2.4% year-on-year in March, slightly less than
  consensus expectations. ... April's inflation reading is likely to
  head much higher as the dampening effect of the removal of the
  consumer carbon levy falls out of the year-on-year inflation
  calculation."

---

## Panel 2 -- BoC preferred core measures (trim and median lead; common as hover footnote)

### Latest-print anchors (March 2026)

| Measure | Y/Y | 3M AR | Source |
|---|---|---|---|
| CPI-trim | 2.2% | not yet derivable | BoC CPI page; pre-published with StatCan release |
| CPI-median | 2.3% | not yet derivable | BoC CPI page |
| CPI-common (hover/footnote) | 2.6% | not yet derivable | BoC CPI page |
| Trim 12M trajectory | Jul 2025 3.1% -> Sep 3.1% -> Dec 2.7% -> Mar 2026 2.2% | -- | boc-tracker `cpi_trim.csv` |
| Median 12M trajectory | Jul 2025 3.0% -> Sep 3.1% -> Dec 2.6% -> Mar 2026 2.3% | -- | boc-tracker `cpi_median.csv` |

Common (deprioritized): the BoC retains it on the published page but
the framework's policy commentary has emphasized trim and median
since late 2022. Surface in hover or footnote with the note "BoC has
deprioritized CPI-common in policy commentary since late 2022;
included here for historical comparability."

### 3M AR core: methodology gating

The BoC Valet keys (`CPI_TRIM`, `CPI_MEDIAN`, `CPI_COMMON`) publish
Y/Y only. To compute 3M AR on the NSA core index we need the
underlying NSA core index levels (not Y/Y). The pipeline does NOT
yet pull the level series; the data-source probe of 2026-05-09 noted
this as a probe item but did not confirm an available Valet series
for the level. Status as of 2026-05-11: not derivable in v1 unless
pipeline-engineer probes and confirms a Valet level series.

Recommendation for v1: surface core-trim and core-median Y/Y as the
primary; defer 3M AR core to v1.5 with a one-line note in the basics
prose ("3M annualized core readings will be added once the level
series are wired").

### So what

Core trim and median have rolled from a corridor of 3.0-3.1% in
mid-2025 down to 2.2-2.3% in March 2026 -- a ~80bp deceleration in
nine months and now at or fractionally above the 2% target. This is
the basics-layer headline that matters: the underlying-trend
measures have re-anchored close to target. The fact that headline
is sitting above core (2.4% vs trim 2.2%, median 2.3%) is a
classic signal that the marginal price pressure is in components
the core trims out -- energy and food at the moment, given the
Middle East conflict's energy channel.

### Evidence

- BoC CPI page (most-recent values 2026-03-01 reference month):
  CPI-trim 2.2%, CPI-median 2.3%, CPI-common 2.6%.
- TD Economics CPI commentary 2026-04-20: "the official core
  inflation metrics (median and trim), cooled slightly in March to
  2.3% y/y. ... when examining three-month trends, trim and median
  inflation continued to run well below the Bank of Canada's 2%
  target."

---

## Panel 3 -- Breadth (share of basket by Y/Y tier; four-state names retired as forced classification)

### Latest-print anchors (March 2026, weighted by 2024 basket; n=60 components, weight sum=99.0% of basket)

| Tier | Weighted share |
|---|---|
| Y/Y > 3% | 27.2% |
| Y/Y 1-3% | 28.8% |
| Y/Y < 1% | 44.0% |

Sums to 100% by construction (the 1% basket coverage gap is the unmapped sliver
that the 60-component panel does not catch; documented in methodology hover).

### Distribution color (for prose grounding, not for forced classification)

ABOVE 3% (top contributors by weight):
- Recreational equipment and services excl. recreational vehicles (5.84% basket, 9.26% Y/Y)
- Purchase and operation of recreational vehicles (4.57%, 4.95% Y/Y)
- Other cultural and recreational services (2.01%, 3.66% Y/Y)
- Vegetables and vegetable preparations (1.91%, 6.32% Y/Y)
- Inter-city transportation (1.69%, 4.12% Y/Y)
- Watches (1.40%, 26.68% Y/Y -- thin-weight outlier)
- Purchase, leasing and rental of passenger vehicles (1.22%, 5.32% Y/Y)
- Water (1.09%, 5.13% Y/Y)
- Fuel oil and other fuels (1.02%, 26.06% Y/Y -- energy shock channel)
- Food purchased from fast food and take-out restaurants (1.05%, 4.27% Y/Y)

BELOW 1% (top contributors by weight):
- Other owned accommodation expenses (8.37%, -2.66% Y/Y)
- Health care services (7.35%, 0.00% Y/Y)
- Operation of passenger vehicles (2.95%, -0.17% Y/Y)
- Other tobacco products and smokers' supplies (2.94%, -6.78% Y/Y)
- Paper, plastic and aluminum foil supplies (2.13%, 0.24% Y/Y)
- Services related to household furnishings and equipment (1.97%, 0.82% Y/Y)
- Women's clothing (1.91%, -2.71% Y/Y)
- Natural gas (1.51%, -18.06% Y/Y)
- Other household goods and services (1.48%, 0.92% Y/Y)
- Travel services (1.45%, -0.74% Y/Y)

IN 1-3% (top contributors by weight):
- Homeowners' maintenance and repairs (6.84%, 1.67% Y/Y)
- Bakery and cereal products (4.68%, 2.33% Y/Y)
- Local and commuter transportation (3.46%, 2.67% Y/Y)
- Home entertainment equipment, parts and services (2.59%, 1.76% Y/Y)
- Education (2.30%, 2.02% Y/Y)

### Methodology hover/footnote content

"Breadth is the weighted share of the CPI basket whose 12-month
percent change falls into three Y/Y bins. Computed on the 60 published
component indexes (NSA, Table 18-10-0004-01) weighted by 2024 basket
weights (Table 18-10-0007-01, applied from January 2025; mapping is
in `data/cpi_breadth_mapping.json`). Components cover approximately
99% of the basket; the residual ~1% sliver is uncaptured by the
60-component panel and is shown as a footnote. The four-state
narrative typology ('broad-based pressure / softening / clustered /
polarized') was retired in May 2026 as a forced classification;
state names remain available as prose vocabulary where the data
genuinely matches one."

### So what

The headline 2.4% obscures unusually wide dispersion. ~44% of the
basket by weight is below 1% Y/Y (parts of services -- health care,
travel, women's clothing, women's footwear, other owned accommodation;
plus natural gas and tobacco). ~27% is above 3% (food categories, parts
of recreation, water, fuel oil, motor vehicle purchase). Only ~29% sits
in the 1-3% band -- the smallest of the three tiers. This is NOT
"clustered near target." Whether the writer characterizes this as
"polarized" is a judgment call; the data supports the framing, but
the EDR retirement of the four-state typology means the prose should
describe the dispersion (44% / 29% / 27%) directly rather than apply
the label.

### Evidence

- Computed from boc-tracker `data/cpi_components.csv` and weights in
  `data/cpi_breadth_mapping.json`, reproducible via
  `analyses/inflation_anchors_2026_05_11.py` and the per-component
  breakdown in `analyses/inflation_breadth_diag.py`.
- Component weights are from StatCan Table 18-10-0007-01 (2024 basket).
- Empirical baseline percentiles for |tilt| distribution (where tilt =
  share above 3% minus share below 1%) are in
  `C:\Users\jayzh\Documents\boc-tracker\analyses\inflation_distribution.csv`
  (1996-onward monthly panel). Current tilt = 27.2% - 44.0% = -16.8pp,
  i.e., the "below 1%" tail is materially bigger than the "above 3%"
  tail by weight.

---

## Panel 4 -- Sub-aggregates (shelter with MIC decomposed; services, goods, food, energy)

### Latest-print anchors (March 2026; Y/Y on NSA major-aggregate index, Table 18-10-0004-01)

| Sub-aggregate | Y/Y | Source / vector |
|---|---|---|
| Shelter | 1.7% | StatCan v41691050; boc-tracker computed 1.66% |
| Services (all) | 2.5% | StatCan v41691230; boc-tracker computed 2.55% |
| Goods (all) | 2.1% | StatCan v41691222; boc-tracker computed 2.12% |
| Food | 4.0% | StatCan v41690974; boc-tracker computed 3.97% (TD cites 4.4% for groceries) |
| Energy | 3.9% | StatCan v41691239; boc-tracker computed 3.87% |
| Mortgage interest cost (component) | 0.3% | from `cpi_components.csv`; boc-tracker computed 0.28% |

Reconciliation note on the food number: TD's commentary cites
"grocery inflation accelerated to 4.4%". The boc-tracker `cpi_food`
series tracks "Food" as the all-food aggregate (Y/Y 4.0%). The 4.4%
figure is for "Food from stores" (a sub-aggregate). Both are correct
at different aggregation levels; the basics-layer panel uses the
all-food aggregate.

### Derived sub-aggregates -- v1 status

| Series | Status | Notes |
|---|---|---|
| Services excluding shelter | Derivable -- shipping in v1 | Construction option (a) per the methodology callout above |
| Goods excluding energy | Derivable -- shipping in v1 | Construction option (a) per the methodology callout above |

Both are gated on pipeline-engineer adding the major-aggregate weight
pull from Table 18-10-0007-01. The math is the weighted residual; the
analyst script is straightforward; the only operational item is the
fetcher addition.

Approximate values one can compute today using the 2024 basket
major-component weights (Shelter 28.57%; the implied "Services"
all-services special-aggregate weight is approximately ~57% per BoC
construction documents, with "Goods" approximately ~43%, and "Energy"
approximately 6.5% within goods, all subject to verification at the
basket-update annex level):

  ServicesExShelter_Y/Y_approx
    = (0.57 * 2.55 - 0.2857 * 1.66) / (0.57 - 0.2857)
    = (1.4535 - 0.4742) / 0.2843
    = 0.9793 / 0.2843
    = 3.44% (approximate; do NOT cite the exact value -- the
             services weight 0.57 is approximate per the BoC SWP
             construction)

  GoodsExEnergy_Y/Y_approx
    = (0.43 * 2.12 - 0.065 * 3.87) / (0.43 - 0.065)
    = (0.9116 - 0.2516) / 0.365
    = 0.6600 / 0.365
    = 1.81% (approximate)

These approximates are NOT for publication. They are for the writer
to ground expectations: services-ex-shelter is running materially hotter
than the all-services aggregate (because shelter, at 1.7%, drags
all-services down); goods-ex-energy is running cooler than the all-
goods aggregate (because energy, at 3.9%, lifts all-goods up). The
methodology footnote and the pipeline-engineer's final weight values
will refine these numbers before publication.

### Mortgage interest cost decomposition

MIC component Y/Y in March 2026 = 0.28% (boc-tracker `cpi_components.csv`,
"Mortgage interest cost" column). Boost to the all-items by MIC alone
is small at current run-rate; the MIC contribution to shelter is now
mostly bled out following the BoC rate cuts in 2024-2025. The
"shelter ex-MIC" diagnostic that mattered acutely in 2024 has lost
its salience by March 2026 because MIC is no longer the dominant
driver of shelter inflation. Surface the MIC line nonetheless because
it's the single most informative shelter sub-component for the
mortgage-renewal narrative; the hover note can explain that MIC's
contribution has decayed.

### So what

Shelter at 1.7% Y/Y is now BELOW the headline 2.4% and below the
all-services 2.5%. This is a striking reversal from 2023-2024 when
shelter was the dominant driver of above-target inflation. Mortgage
interest cost (within shelter) at 0.3% Y/Y is the explanation:
nearly all of the MIC pressure from the 2022-2023 hiking cycle has
faded as MIC compares against the 2024-2025 peak. Energy at 3.9%
Y/Y and food at 4.0% Y/Y are the marginal pressures right now --
both showing the Middle East energy-shock channel (energy direct,
food via fuel-and-transport pass-through). The basics-layer story:
the composition has rotated from shelter-driven to commodity-driven
inflation, which is the exact composition the BoC's policy
framework reads through.

### Evidence

- StatCan Table 18-10-0004-01 NSA index levels, March 2026 vs
  March 2025 (boc-tracker `cpi_*.csv`).
- TD Economics 2026-04-20 commentary: "grocery inflation
  accelerated to 4.4% from 4.1%, shelter inflation ticked up to
  1.7% from 1.5%, but overall services inflation cooled further to
  2.5% y/y."
- BoC April 2026 MPR: oil price shock is the binding marginal
  pressure on the next-two-quarter inflation path.

---

## Panel 5 -- Inflation expectations

### Latest-print anchors (Q1 2026 release, April 20, 2026)

| Series | Value | Vintage | Source |
|---|---|---|---|
| CSCE 1y mean | 4.0% | Q1 2026 (collected through mid-March, with Middle East war supplement March 26 - April 2) | BoC CSCE Q1 2026 release |
| CSCE 5y mean | 3.0% | Q1 2026 | BoC CSCE Q1 2026 release |
| BOS firms expecting CPI > 3% over 2y | 11% | Q1 2026 | BoC BOS Q1 2026 release |
| BOS dist below 1% | 0% | Q1 2026 | boc-tracker `bos_dist_below1.csv` |
| BOS dist 1-2% | 14% | Q1 2026 | boc-tracker `bos_dist_1to2.csv` |
| BOS dist 2-3% | 72% | Q1 2026 | boc-tracker `bos_dist_2to3.csv` |
| BOS dist above 3% | 11% | Q1 2026 | boc-tracker `bos_dist_above3.csv` |

### Trajectory context (re-anchoring story)

BOS firms-expecting->3% has rolled from a peak of 84% in Q4 2022 to
54% in Q4 2023 (per the boc-tracker verification log), to 23% in Q1
2025, to 16% in Q4 2025, to 11% in Q1 2026. The re-anchoring is
real and visible in primary-source data.

CSCE 1y mean has rolled less dramatically: 4.04% in Q2 2025, 4.10%
in Q4 2025, 3.98% in Q1 2026 -- effectively stuck just below 4%, well
above the survey's historical average. This is the gap between firm
and consumer expectations that the BoC's April 2026 MPR explicitly
calls out.

CSCE 5y mean has cooled: 3.45% in Q2 2025, 3.09% in Q4 2025, 3.02%
in Q1 2026. The 5y has moved closer to the 2% target than the 1y has,
which is the textbook anchoring profile (long-horizon stickiness near
target, short-horizon noise).

### Methodology note

"CSCE is the BoC's quarterly Canadian Survey of Consumer Expectations;
the 1y and 5y values reported here are the survey's mean (not median)
expectation. BOS is the quarterly Business Outlook Survey;
'firms-expecting->3%' is the ABOVE3 series and the four-bucket
distribution sums to 100% by construction. Q1 2026 was collected in
late February / early March 2026 with a special supplement March 26 -
April 2 2026 on the Middle East war."

### So what

Firms have re-anchored: 72% of BOS respondents expect CPI in the
2-3% band over the next two years, only 11% expect >3%. Consumers
have not: CSCE 1y mean is stuck just below 4%, still well above the
survey's historical average and roughly 1.5pp above where firms see
the next 12 months running. The 5y consumer mean at 3.02% has come
down but is still 1pp above target. The BoC's April 2026 MPR reads
the firm anchoring as the load-bearing signal -- it's the channel
through which the central bank judges whether the energy supply shock
risks second-round pricing behaviour. The consumer numbers are
qualified by the survey's well-documented upward bias relative to
realized CPI.

### Evidence

- BoC CSCE Q1 2026 release, 2026-04-20: "consumers' perceptions of
  current inflation and their expectations for inflation over the
  next one and two years were largely unchanged from the previous
  quarter, with inflation expectations having changed little over
  the past 12 months and still being above the survey's historical
  average."
- BoC BOS Q1 2026 release, 2026-04-20.
- Trajectory data from boc-tracker `data/infl_exp_*.csv` and
  `data/bos_dist_*.csv`.

---

## Panel 6 -- Pass-through watch (gated; see EDR 4.2 element 6)

### Latest-print anchors

| Series | Value | Reference period | Source |
|---|---|---|---|
| USDCAD spot, month-end | 1.3575 | 2026-05-01 (last available daily print) | BoC Valet FXUSDCAD; boc-tracker `usdcad.csv` |
| USDCAD Y/Y | -1.25% | end-April 2026 vs end-April 2025 | derived from boc-tracker daily series |
| LFS-Micro composition-adjusted wage Y/Y | 3.1% | 2026-03 reference month | BoC LFS-Micro release; boc-tracker `lfs_micro.csv` |
| Goods Y/Y (placeholder until goods-ex-energy lands) | 2.1% | 2026-03 | StatCan v41691222 |
| Services Y/Y (placeholder until services-ex-shelter lands) | 2.5% | 2026-03 | StatCan v41691230 |

USDCAD context note: the boc-tracker daily series ends at 2026-05-01
(value 1.3575). The April 2026 monthly average should be used for
the Y/Y diagnostic, not the spot-on-last-day; the month-end
convention used in the script (resample "ME" last) is the simpler
pull but introduces single-day variance. Pipeline-engineer should
add the monthly-average BoC FX rate for cleaner Y/Y construction
(Valet has a monthly average key).

### Gating and v1 disposition

Per EDR 4.2 element 6: "Gated on element 4's derived aggregates
landing; if they slip, pass-through defers to v1.5."

Status: element 4's derived aggregates (services ex-shelter, goods
ex-energy) are derivable from the proposed weighted-residual
construction (see methodology callout). If pipeline-engineer can
deliver the basket-weight pull before launch, Panel 6 ships in v1
with the correct right-hand-side series. If the weight pull slips,
Panel 6 defers to v1.5; the basics-layer page ships with five
panels.

### Strip-chart structure (no regression in basics)

Two side-by-side strip charts:
1. USDCAD Y/Y (lagged 12 months) overlaid with goods-ex-energy
   Y/Y. The CAD-lag-12 convention is the textbook pass-through
   window for tradable-goods CPI (see BoC SWP-2014-13 and BoC
   SDP-2019-11 on exchange rate pass-through to Canadian CPI).
2. LFS-Micro composition-adjusted wage Y/Y vs services-ex-shelter
   Y/Y, contemporaneous. The contemporaneous convention reflects
   that labour-cost pass-through into non-shelter services prices
   is closer to coincident than to leading (per BoC SDP-2018-04 on
   wage-price dynamics in services).

No regression on the basics page. The chart shows two lines on each
panel; the interpretation is analyst prose in the blurb.

### So what

USDCAD is roughly flat to mildly stronger Y/Y (CAD up ~1.25% vs USD).
This is mildly disinflationary for imported tradable-goods CPI on a
12-month lag basis; the BoC's April MPR notes the "largely unchanged
Canadian dollar has helped preserve...competitiveness" and means
"higher oil prices are felt more directly by consumers" -- the
flip-side observation that a stable CAD does not buffer the energy-
import shock. On the wage-services side: LFS-Micro at 3.1% Y/Y is
still running ahead of services-ex-shelter (approximately 3.4% on
the rough derivation, both close enough that one cannot call wages
the binding driver of services-ex-shelter inflation right now).

### Evidence

- BoC Valet FXUSDCAD daily series.
- BoC LFS-Micro composition-adjusted wage Y/Y, March 2026 = 3.1%.
- BoC SWP and SDP literature on exchange-rate and wage pass-through
  (cited in methodology footnote, not in basics prose).
- BoC April 2026 MPR opening statement on the CAD-energy-import
  channel.

---

## Cross-cutting writer notes

1. **Surprise framing for Panel 1.** Until the Big-Six aggregation
   pipeline is built, surprise prose should reference the consensus
   range or band rather than a precise point. The cleanest defensible
   phrasing as of 2026-05-11: "below the pre-print consensus of
   around 2.5%" with a date stamp on when consensus was captured.
   Avoid claiming a precise -0.1pp surprise until the pipeline lands.

2. **Consensus labelling.** Every "consensus" reference must carry a
   date and a source class ("Big-Six aggregated median" or "TD
   commentary citing consensus"). The principle from
   `memory/feedback_consensus_labelling.md` (per the brief) is in
   effect even though the memory file itself is not yet on disk;
   it is encoded in the EDR 2026-05-10 changelog and the Wave 2
   memo.

3. **Four-state vocabulary on Panel 3.** The data supports describing
   the current distribution as polarized (~44% below 1%, ~27% above
   3%, only ~29% in the band). But "polarized" must be earned by
   describing the dispersion explicitly, not asserted as a
   classification. Treat the four state names as optional prose
   vocabulary that the writer reaches for only when the data clearly
   matches; describe the numbers regardless.

4. **Shelter / MIC narrative on Panel 4.** The 2023-2024 narrative
   ("MIC is the dominant inflation channel") is now stale by March
   2026. Don't recycle. The current story is: shelter has cooled
   below headline, MIC is essentially extinguished, the marginal
   pressure has rotated to energy + food.

5. **Re-anchoring story on Panel 5.** The BOS firms->3% trajectory
   (84% Q4 2022 -> 11% Q1 2026) is a strong, primary-source-grounded
   re-anchoring narrative. Use it cleanly; it's exactly the kind of
   number a P1 reader did not have in front of them this morning.

6. **Panel 6 caveat language.** If Panel 6 ships in v1 with the
   derived aggregates, the prose must note that pass-through is a
   visual diagnostic, not a regression, and that the literature
   on Canadian pass-through coefficients (BoC SWP / SDP series)
   shows the coefficients are unstable post-2016. One-sentence
   caveat in the basics blurb.

---

## Summary read

All six panels have primary-source-anchored latest-print values
available as of 2026-05-11, with March 2026 as the reference month.
Panels 1, 2, 3, 4, 5 are ready for the writer to draft from. Panel 6
is gated on Panel 4's derived aggregates -- both derivable via
construction option (a), the weighted-residual method, contingent on
pipeline-engineer adding the major-aggregate basket-weight pull from
StatCan Table 18-10-0007-01 (a one-line fetcher addition; the basket
weight refresh is every five years). Recommendation: GO on derivations
for v1; ship the pass-through panel.

The dominant cross-panel story for the writer to weave: headline
sits just above target at 2.4%, core has re-anchored to 2.2-2.3% (at
or fractionally above target), but the composition has rotated
sharply -- shelter has cooled below headline (1.7% Y/Y, MIC
essentially extinguished), while energy (3.9%) and food (4.0%) are
the marginal pressure-points on the back of the Middle East shock.
Firm inflation expectations have re-anchored (BOS firms->3% at 11%,
down from 84% in late 2022); consumer expectations have not (CSCE
1y at 4.0%). Breadth is wide -- ~44% of the basket below 1% Y/Y, ~27%
above 3% -- which is a dispersed distribution, not a clustered one.
The BoC's April 2026 MPR reads through the next-two-quarter energy
shock as supply, not demand, and leaves the policy rate on hold at
2.25%.

End of pack.

---

## Reproducibility

Derivation scripts:
- `C:\Users\jayzh\projects\macro-research-department\analyses\inflation_anchors_2026_05_11.py`
  Latest-print anchor extraction for all six panels.
- `C:\Users\jayzh\projects\macro-research-department\analyses\inflation_breadth_diag.py`
  Per-component breadth breakdown for sanity check.

Data inputs (all from boc-tracker mirrors of primary sources):
- `C:\Users\jayzh\Documents\boc-tracker\data\cpi_all_items.csv` (SA index)
- `C:\Users\jayzh\Documents\boc-tracker\data\cpi_all_items_nsa.csv` (NSA index)
- `C:\Users\jayzh\Documents\boc-tracker\data\cpi_trim.csv`
- `C:\Users\jayzh\Documents\boc-tracker\data\cpi_median.csv`
- `C:\Users\jayzh\Documents\boc-tracker\data\cpi_common.csv`
- `C:\Users\jayzh\Documents\boc-tracker\data\cpi_components.csv` (60-component panel)
- `C:\Users\jayzh\Documents\boc-tracker\data\cpi_breadth_mapping.json` (2024 weights)
- `C:\Users\jayzh\Documents\boc-tracker\data\cpi_shelter.csv`
- `C:\Users\jayzh\Documents\boc-tracker\data\cpi_services.csv`
- `C:\Users\jayzh\Documents\boc-tracker\data\cpi_goods.csv`
- `C:\Users\jayzh\Documents\boc-tracker\data\cpi_food.csv`
- `C:\Users\jayzh\Documents\boc-tracker\data\cpi_energy.csv`
- `C:\Users\jayzh\Documents\boc-tracker\data\infl_exp_consumer_1y.csv`
- `C:\Users\jayzh\Documents\boc-tracker\data\infl_exp_consumer_5y.csv`
- `C:\Users\jayzh\Documents\boc-tracker\data\infl_exp_above3.csv`
- `C:\Users\jayzh\Documents\boc-tracker\data\bos_dist_*.csv`
- `C:\Users\jayzh\Documents\boc-tracker\data\usdcad.csv`
- `C:\Users\jayzh\Documents\boc-tracker\data\lfs_micro.csv`

Pipeline additions needed before v1 launch:
- StatCan Table 18-10-0007-01 major-aggregate basket weights pull
  (one-time per basket cycle; current vintage applies through 2029).
- BoC Valet NSA core index levels (for 3M AR core; v1.5 if not
  delivered by launch).
- BoC monthly-average USDCAD (cleaner Y/Y than month-end last; minor
  refinement).
