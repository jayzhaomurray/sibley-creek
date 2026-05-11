# Wave 2, Brief 2A.5 -- Labour basics-layer methodology notes

Author: researcher
Date: 2026-05-10
Status: methodology notes and structured-data specs for the basics-layer Labour section.
Scope: methodology and data specs only. No prose drafts; no chart visuals. ASCII-only.

Anchors:
- Editorial canon: `editorial/dashboard_purpose.md` Section 4.3 (updated 2026-05-10:
  per-capita signature panel, four-province dumbbell, no demographics subheading,
  IRCC-plan annotation logic).
- Wave 1 memo: `research/wave1_data_scope_labour_demographics.md` Section D
  (construction watchlist).
- boc-tracker verification: `Documents/boc-tracker/markdown-files/verification/labour.md`
  (NAIRU framing, V/U-band conventions, 3M-MA decision record).

Conventions used throughout:
- Y/Y = year-over-year percent change, defined as 100 * (x_t / x_{t-12} - 1) for
  monthly series and 100 * (x_t / x_{t-4} - 1) for quarterly. Both sides of the
  ratio are levels in the same vintage; we do not mix vintages within a Y/Y.
- "Subtractive form" for per-capita = (Y/Y of numerator) - (Y/Y of denominator).
  This is the BoC MPR convention and what the EDR endorses.
- "SA" = seasonally adjusted by the source agency (StatCan in all cases here).
  "NSA" = not seasonally adjusted. Our pipeline does not perform its own seasonal
  adjustment in v1.
- "3M MA" = simple three-period trailing arithmetic mean ending at the reference
  month: MA3_t = (x_t + x_{t-1} + x_{t-2}) / 3. Right-aligned. We do not center.
- Period naming: monthly LFS reference periods are the StatCan-published month
  (e.g. "2026-04" = April 2026 LFS print released first Friday of May 2026).
- All StatCan vector IDs are WDS integers; "V-prefix" variants quoted in StatCan
  text are the same identifier.

---

## 1. Per-capita employment-growth and per-capita-hours-growth (subtractive form)

### 1.1 Definitions

We compute two per-capita growth measures for the signature panel:

```
per_capita_employment_growth_yoy_t  =  emp_yoy_t  -  pop_yoy_t
per_capita_hours_growth_yoy_t       =  hours_yoy_t  -  pop_yoy_t
```

Where:
- `emp_yoy_t`     = Y/Y growth in LFS total employment (15+), SA, monthly.
- `hours_yoy_t`   = Y/Y growth in LFS aggregate hours worked (employees + self-employed,
                    main job, total, SA, monthly).
- `pop_yoy_t`     = Y/Y growth in StatCan population estimate, quarterly, total Canada,
                    interpolated to monthly (see Section 1.3 below).

The subtractive form is the BoC MPR convention. It is mathematically a first-order
approximation to the exact multiplicative form
((1 + e) / (1 + p) - 1), and the approximation error is small at the growth rates
we are working with: at e = 3.0% and p = 2.5%, the subtractive answer is 0.50
percentage points and the exact answer is 0.488 percentage points -- a 1.2-bp
gap. We accept this for basics-layer presentation. The deep-dive (Pillar E) may
elect to use the exact form for headline calls; the basics layer does not.

### 1.2 Data inputs

| Quantity              | StatCan table         | Vector ID  | Cadence  | Notes                                  |
|-----------------------|-----------------------|------------|----------|----------------------------------------|
| Employment level      | 14-10-0287-01         | v2062811   | Monthly  | Total employed, 15+, both sexes, SA    |
| Aggregate hours       | 14-10-0289-01         | TBD probe  | Monthly  | Total actual hours worked, all jobs, SA |
| Total population      | 17-10-0009-01         | TBD probe  | Quarterly| Canada total, both sexes, all ages     |

All three vector IDs above are flagged in the Wave 1 memo Section C as
construction-gap inputs requiring pipeline-engineer probes. The methodology
below assumes those probes resolve; if a probe returns an unexpected series
(as happened with the 17-10-0009 prior attempt), we flag and re-scope.

### 1.3 Population interpolation to monthly

LFS employment and aggregate hours print monthly; StatCan total-population
estimates print quarterly (reference dates Q1 = April 1, Q2 = July 1, Q3 =
October 1, Q4 = January 1 of the following year). For per-capita growth at
monthly frequency we need a monthly population path.

Method: **linear interpolation between adjacent quarterly reference dates**,
applied to the level (not the growth rate), then Y/Y computed on the
interpolated monthly series. Formally, for a month m at fractional position
f in [0, 1] between quarterly reference dates q and q+1:

```
pop_m  =  pop_q  +  f * (pop_{q+1} - pop_q)
```

Y/Y is then `100 * (pop_m / pop_{m-12} - 1)`.

Rationale: population is a stock that moves smoothly; linear interpolation is
the standard convention in BoC working papers when monthly per-capita
constructions are reported (see BoC Staff Working Paper 2024-14 footnote on
per-capita output construction). We do not use cubic or spline interpolation
in v1 because the resulting Y/Y is identical to two decimal places and the
methodology is harder to explain.

**Open-quarter handling.** Between the latest published quarterly population
estimate and the LFS reference month, we extend the population path by
linear extrapolation of the most recent quarter-over-quarter change. This is
flagged in the methodology footnote as an assumption; the gap is at most two
months (LFS publishes about 7 days after reference month end; StatCan
population estimates publish about 90 days after reference quarter end). The
per-capita Y/Y at month t is therefore "preliminary, conditional on the next
population release" for at most two months of any twelve-month look-back; this
is acceptable basics-layer practice and consistent with BoC's MPR per-capita
tables, which carry the same lag.

### 1.4 Construction script location and reproducibility

Script: `analyses/per_capita_labour.py` (to be authored once pipeline probes
resolve). Inputs: the three CSVs named in 1.2. Outputs:
`data/processed/per_capita_employment_yoy.csv` and
`data/processed/per_capita_hours_yoy.csv`, each with columns
`(date, value, vintage)`. The script's docstring states the methodology
verbatim from this note; methodology drift between this note and the script
is fact-checker territory.

### 1.5 Presentation in basics layer

Per EDR 4.3 element 2, the panel is a side-by-side small-multiples view:
- Left: `emp_yoy` (line) and `per_capita_employment_yoy` (line) on a shared y-axis.
- Right: `hours_yoy` (line) and `per_capita_hours_yoy` (line) on a shared y-axis.

Default window: 5 years (matching the rest of the section's panels). The
basics-layer blurb surfaces the *divergence* between aggregate and per-capita;
it does not adjudicate cause (population deceleration vs aggregate weakness).
That adjudication is Pillar E.

### 1.6 What this is not

- Not a productivity measure. Output / hours is a different ratio (lives in
  GDP / Pillar D).
- Not a labour-utilization measure. Employment / population is the
  employment rate, computed and shown separately in panel 1.
- Not a "true" per-worker series. Per-capita = per-population (denominator
  is total population, not labour force). The denominator choice matters when
  participation is moving; we explicitly use population because that is the
  EDR's framing of the headline question (per-capita output, per-capita hours)
  and the BoC MPR convention.

---

## 2. V/U 3M-MA convention with Canadian-calibrated historical-anchor bands

### 2.1 Definition

```
V/U_t  =  vacancy_rate_t  /  unemployment_rate_t
V/U_MA3_t  =  (V/U_t + V/U_{t-1} + V/U_{t-2}) / 3
```

Where:
- `vacancy_rate_t`     = JVWS job-vacancy rate, NSA, monthly (StatCan
                         14-10-0371-01, vector v1212389365).
- `unemployment_rate_t`= LFS unemployment rate, SA, monthly (StatCan
                         14-10-0287-01, vector v2062815).

The dashboard convention is **3-month moving average, not 12-month**. The
boc-tracker verification record (labour.md Claim 3) measured the cyclical
peak lags:

| Smoothing window | 2022 V/U peak value | Peak date     | Lag vs raw NSA peak |
|------------------|---------------------|---------------|---------------------|
| Raw NSA          | 0.99                | June 2022     | 0                   |
| 3M MA            | approx 0.96         | August 2022   | 2 months            |
| 12M MA           | 0.86                | January 2023  | 7 months            |

The 12M MA lag of 7 months is too large relative to the duration of
policy-relevant cyclical episodes (the 2022 overheat lasted roughly 12
months end-to-end). 3M MA removes the residual NSA seasonal pattern with
an acceptable 2-month lag. Decision: 3M MA at basics-layer.

### 2.2 The SA / NSA mix

Note that JVWS is NSA-only (StatCan does not publish a SA companion series for
job vacancies at the national headline level), while the LFS unemployment rate
is SA. The ratio therefore mixes seasonal conventions. We accept this with
two mitigations:
1. The 3M MA partially absorbs the residual NSA seasonal pattern in vacancies.
2. The methodology note attached to the panel states the SA / NSA mix
   explicitly; the chart legend labels the vacancy rate as "NSA, 3M MA".

We do not seasonally adjust JVWS ourselves in v1. Doing so would introduce a
methodology surface that differs from the StatCan-published vacancy series; the
basics-layer cost-benefit is wrong.

### 2.3 Canadian-calibrated bands -- historical anchor, NOT current-state classifier

Per boc-tracker labour.md Claim 3, the bands are:

| Band              | Calibration narrative                                          |
|-------------------|----------------------------------------------------------------|
| V/U < 0.30        | Slack (anchored to 2015-2017 oil-shock period and 2020 trough) |
| 0.30 <= V/U < 0.45 | Below balance                                                  |
| 0.45 <= V/U < 0.60 | Approaching balance / starting to be tight (2018-2019 BoC      |
|                   | tightening cycle anchor)                                       |
| 0.60 <= V/U < 0.80 | Tight                                                          |
| V/U >= 0.80       | Exceptionally tight (anchored to 2022 post-COVID peak;         |
|                   | Canadian raw peak 0.99 vs 12M MA peak 0.86 vs 3M MA peak 0.96) |

**These are historical anchors, not current-state claims.** The basics-layer
prose convention: when V/U is in the 0.45-0.60 band, the prose may say "in the
range associated with the 2018-2019 BoC tightening cycle." The prose does not
say "the labour market is tight" without qualifying against the post-COVID
Beveridge-curve shift (Section 3.4 below).

The bands are Canadian-calibrated, not US-transferred. The US JOLTS V/U
peaked near 2.0 in 2022 versus Canada's 0.99; importing US thresholds
("V/U > 1 = tight") to Canada systematically overstates tightness. This was
the documented propagation defect resolved in boc-tracker on 2026-05-09; the
defect must not recur here.

### 2.4 Caveats to surface in methodology note

1. JVWS series begins 2015. No pre-2015 V/U is available from StatCan;
   academic reconstructions (e.g. Fortin CLEF 070-2024 regional Beveridge
   curves) are deep-dive material.
2. JVWS has a structural gap April-September 2020 when StatCan suspended
   fieldwork. The COVID-period V/U trough is unobservable in JVWS and
   visible only in Indeed-Canada postings; the basics-layer prose should
   not claim a JVWS-derived COVID trough.
3. The Beveridge curve shifted outward post-COVID. Any V/U value at a given
   unemployment rate is now consistent with a different matching-efficiency
   state than the pre-COVID locus implied. This is a standing caveat on
   the bands; it is not a reason to re-calibrate them mid-cycle.

### 2.5 NAIRU framing

The basics-layer Labour blurb does not anchor on a fixed NAIRU. The verified
position (boc-tracker labour.md Claim 1):
- The BoC does not publish a point-estimate NAIRU. Macklem has explicitly
  said "maximum sustainable employment is not directly measurable and is
  determined largely by non-monetary factors that can change through time."
- The IMF Article IV (July 2024) published a Canadian NAIRU estimate of 6.0%.
  We use this as a *soft reference*, not a hard threshold. The basics-layer
  prose may say "above the IMF's 6% NAIRU reference" when the data support
  it; it does not say "above NAIRU" as if NAIRU were known.
- OECD publishes a country-NAIRU table (latest accessible Canada figure
  6.24%, 2022 vintage); citable as a secondary soft anchor.

The NAIRU concept is tracked because peer institutions still use it
(OECD, IMF, ECB, Fed); the BoC's deprioritization is a methodology stance
to note in passing, not a reason to drop the concept from the basics layer.

---

## 3. Beveridge-curve panel construction

### 3.1 Inputs and transforms

```
x-axis:  unemployment_rate_t,  LFS SA monthly  (Table 14-10-0287-01 v2062815)
y-axis:  vacancy_rate_t,       JVWS NSA monthly (Table 14-10-0371-01 v1212389365)
```

**Smoothing.** Both axes are smoothed with 3M MA (right-aligned) before
plotting. This matches the V/U convention in Section 2 and produces a
visibly less noisy locus than raw NSA on vacancy.

### 3.2 Trail length

Most recent 12 months as a connected path; the latest month highlighted as
a single emphasized point. Prior history (Series start 2015 through the
trail's start) shown as faded background points, color-coded by year so the
post-COVID outward shift is visually obvious.

The 12-month trail is the right length because:
- Shorter (e.g. 3-month) trails don't show enough motion to read the
  direction of the cyclical move.
- Longer (e.g. 24-month) trails overlap on themselves visibly during the
  2022-2024 round-trip, which is unreadable.
- 12 months is the standard convention in BoC and BLS Beveridge-curve
  visualizations.

### 3.3 Reuse of boc-tracker construction

The existing boc-tracker `_build_beveridge_curve_panel` (in `build.py`)
already implements this with the right axes and the 3M MA smoothing. The
chart at `Documents/boc-tracker/analyses/beveridge_curve_canada.html` is
the working reference. Date range: May 2015 through Feb 2026; U range
4.97%-13.50%; V range 0%-5.90%. Re-use the construction; do not re-invent.

### 3.4 Methodology note attached to panel

One-click methodology note copy (specification, not prose draft):
1. Inputs: LFS unemployment rate (SA) and JVWS vacancy rate (NSA), both
   3M-MA smoothed.
2. Trail: most recent 12 months as a connected path; latest month emphasized.
3. Background: prior history 2015-present shown faded, color-coded by year.
4. Standing caveat: the Beveridge curve has shifted outward post-COVID; a
   point on today's curve is not directly comparable to a point at the same
   unemployment rate on the 2015-2019 curve.
5. Structural gap: vacancy data Apr-Sep 2020 omitted (JVWS fieldwork
   suspended).

### 3.5 What we do not do in v1 basics

- We do not fit a Beveridge curve (matching-function regression). Deep-dive
  territory (Pillar E or labour-DD).
- We do not estimate the efficient unemployment rate u* = sqrt(u * v).
  Deep-dive territory; cited as theoretical anchor only.
- We do not show a regional Beveridge curve (CLEF 070-2024 Fortin work).
  Deep-dive territory.

---

## 4. IRCC levels-plan structured-data spec

### 4.1 Why this exists as a JSON file

The IRCC levels plan is editorial data, not pipeline data. It is published
annually each November (typically the first Tuesday of November) as a press
release and supplementary document, not as a programmatic API series. The
basics-layer chart annotations (per EDR 4.3 element 5) read off this file;
the editorial team refreshes it on each November plan release.

File location: `data/ircc_levels_plan.json`.
Maintenance: editorial; refreshed on each November IRCC plan release.
Read by: chart annotation logic in the supply-trajectory panel (element 5)
and the companion target-table widget below it.

### 4.2 JSON schema

The file is an array of plan-vintage objects. One object per IRCC plan
release. Object shape:

```json
{
  "plan_vintage": "2025-2027",
  "release_date": "2024-10-24",
  "source_url": "https://www.canada.ca/en/immigration-refugees-citizenship/news/notices/supplementary-immigration-levels-2025-2027.html",
  "structural_break": true,
  "structural_break_note": "First plan to cut PR targets year-over-year and introduce explicit NPR caps. Pivot from the post-COVID levels-plan trajectory.",
  "years": [
    {
      "year": 2025,
      "pr_target_total": 395000,
      "pr_target_by_category": {
        "economic": 232150,
        "family": 94500,
        "refugee_protected_person": 58350,
        "humanitarian_other": 10000
      },
      "npr_target_total": 673650,
      "npr_target_by_category": {
        "international_students": 305900,
        "international_mobility_program": 285750,
        "temporary_foreign_worker_program": 82000
      },
      "npr_share_of_population_target_pct": null,
      "notes": "PR target 395,000 -- cut from 500,000 in prior plan."
    },
    {
      "year": 2026,
      "pr_target_total": 380000,
      "pr_target_by_category": {
        "economic": 229750,
        "family": 88000,
        "refugee_protected_person": 55350,
        "humanitarian_other": 6900
      },
      "npr_target_total": 516600,
      "npr_target_by_category": {
        "international_students": 305900,
        "international_mobility_program": 153000,
        "temporary_foreign_worker_program": 57700
      },
      "npr_share_of_population_target_pct": 5.0,
      "notes": "NPR share-of-population target introduced (5%)."
    },
    {
      "year": 2027,
      "pr_target_total": 365000,
      "pr_target_by_category": {
        "economic": 225350,
        "family": 81000,
        "refugee_protected_person": 54350,
        "humanitarian_other": 4300
      },
      "npr_target_total": 543600,
      "npr_target_by_category": {
        "international_students": 305900,
        "international_mobility_program": 175000,
        "temporary_foreign_worker_program": 62700
      },
      "npr_share_of_population_target_pct": 5.0,
      "notes": "End of plan horizon."
    }
  ]
}
```

### 4.3 Field-by-field specification

| Field                                | Type            | Required | Notes                                                                 |
|--------------------------------------|-----------------|----------|-----------------------------------------------------------------------|
| `plan_vintage`                       | string          | yes      | Format "YYYY-YYYY" using the horizon endpoints (e.g. "2025-2027").    |
| `release_date`                       | string (ISO)    | yes      | YYYY-MM-DD of the IRCC public announcement.                            |
| `source_url`                         | string (URL)    | yes      | Direct link to canada.ca notice or PDF, archived if possible.          |
| `structural_break`                   | boolean         | yes      | True when the plan represents a policy-direction pivot from the prior |
|                                      |                 |          | vintage. Author-discretion; documented in `structural_break_note`.    |
| `structural_break_note`              | string \| null  | yes      | One-sentence rationale when `structural_break` is true; else null.    |
| `years`                              | array of objects| yes      | One element per plan year. Standard plan length = 3 years.            |
| `years[].year`                       | integer         | yes      | Calendar year.                                                        |
| `years[].pr_target_total`            | integer         | yes      | Permanent-resident admissions target, all categories.                  |
| `years[].pr_target_by_category`      | object          | yes      | Keys: `economic`, `family`, `refugee_protected_person`, `humanitarian_other`. Integer values. Must sum to within rounding of `pr_target_total`. |
| `years[].npr_target_total`           | integer         | yes      | Non-permanent-resident inflows target. Pre-2024 plans may have `null` here -- NPR targets were not published before the Oct 2024 plan. |
| `years[].npr_target_by_category`     | object \| null  | yes      | Keys: `international_students`, `international_mobility_program`, `temporary_foreign_worker_program`. Null for plans that did not target NPRs by category. |
| `years[].npr_share_of_population_target_pct` | number \| null | yes | NPR-share-of-population target where IRCC publishes one (introduced in the Oct 2024 plan, target 5%). Null otherwise. |
| `years[].notes`                      | string \| null  | yes      | One-sentence editorial note for chart annotation.                     |

### 4.4 Read-side contract

The chart annotation logic reads `ircc_levels_plan.json` and produces:

1. A vertical dated annotation at each `release_date` on the
   supply-trajectory chart, labelled with the plan vintage and a short
   indicator of the headline PR target (e.g. "Oct 2024: 2025-2027 plan, PR
   target cut to 395k").
2. The `structural_break: true` plans get a heavier annotation style (per
   art-director's call on the visual treatment).
3. The companion target-table widget below the chart reads the most-recent
   plan's `years` array and renders three rows (current plan year, next
   year, year after) showing `pr_target_total` and `npr_target_total` with
   `plan_vintage` and `release_date` as the table caption.

### 4.5 Validation rules

The pipeline does not write this file but should validate it on read.
Required checks:
1. `pr_target_by_category` values sum to `pr_target_total` (tolerance: 100
   admissions, to absorb IRCC's own rounding).
2. `npr_target_by_category` values sum to `npr_target_total` when both are
   non-null.
3. `release_date` falls in the calendar year before the first year in
   `years` (IRCC plans are published the November before the first plan
   year).
4. `plan_vintage` endpoints match `years[0].year` and `years[-1].year`.
5. No two objects in the array share the same `release_date`.

Violations are warnings, not errors -- the chart still renders. The
warnings surface in the fact-checker's daily check.

### 4.6 Backfill scope

The file ships with at least three vintages so the chart annotations have
historical depth:
- 2023-2025 plan (released November 2022).
- 2024-2026 plan (released November 2023).
- 2025-2027 plan (released October 2024) -- the structural-break pivot.

The Nov 2026 IRCC release will add the 2026-2028 plan (or, less likely,
a revised 2025-2027 update). The editorial refresh at that point appends
one object to the array; prior objects are not edited.

### 4.7 Sources for the backfill

- 2025-2027 plan: https://www.canada.ca/en/immigration-refugees-citizenship/news/notices/supplementary-immigration-levels-2025-2027.html
- 2024-2026 plan: https://www.canada.ca/en/immigration-refugees-citizenship/news/2023/11/notice---supplementary-information-for-the-2024-2026-immigration-levels-plan.html
- 2023-2025 plan: https://www.canada.ca/en/immigration-refugees-citizenship/news/notices/supplementary-immigration-levels-2023-2025.html

Backfill values must be transcribed from these primary sources, not from
secondary summaries. The transcribed JSON should be cross-checked against
the IRCC press release at first read; subsequent reads are stable
(IRCC does not retroactively edit prior plans).

---

## 5. Four-province dumbbell -- first-cut spec

### 5.1 Provinces and data

Four largest provinces by population: Ontario (ON), Quebec (QC), Alberta
(AB), British Columbia (BC). Matches the four-province cut used for
Policy 4.5 fiscal sub-surface, and parallels Housing 4.4's six-CMA logic.

Data: StatCan Table 14-10-0287-03 (LFS by province, monthly SA). The
unemployment rate is the displayed series for the dumbbell. Vector IDs
per province (to be confirmed by pipeline probe):

| Province | Series                | Vector ID (probe) |
|----------|-----------------------|-------------------|
| ON       | Unemployment rate, SA | v2063810 (probe)  |
| QC       | Unemployment rate, SA | v2063624 (probe)  |
| AB       | Unemployment rate, SA | v2064178 (probe)  |
| BC       | Unemployment rate, SA | v2064270 (probe)  |
| Canada   | Unemployment rate, SA | v2062815 (confirmed) |

All probe IDs are best-guess from the Table 14-10-0287-03 dimension
structure and must be verified against the actual WDS response by
pipeline-engineer before chart wiring.

### 5.2 National-rate overlay convention -- concurrent, not trailing

**Decision: concurrent national rate, not trailing.**

The four-province dumbbell shows two points per province: current month
unemployment rate, and the value 12 months ago. The national rate is
overlaid as a horizontal reference line at the **concurrent month's value**
(not the 12-month-ago value).

Rationale:
1. The current month is the prevailing state-of-the-section read; the
   dumbbell's job is to show *dispersion around current state*. A
   trailing national rate would index the chart to a stale level and
   confuse the dispersion read.
2. The 12-months-ago endpoints on each province bar are the historical
   anchor for the per-province move; they do not need an overlay to be
   readable.
3. The "loosening fastest" call-out (Section 5.3) is computed from
   12-month changes per province, with the national 12-month change as
   the comparator -- that comparison lives in the call-out text, not in
   a second overlay line on the chart.

A single concurrent national line keeps the chart legible. If the
art-director's call demands a second reference line at the 12-month-ago
national value, that's an aesthetic decision and is fine; the
methodology choice is which is the *primary* reference, and primary
is concurrent.

### 5.3 "Loosening fastest" call-out -- computation

```
delta_pct_pts_t  =  ur_t  -  ur_{t-12}
```

Computed per province p in {ON, QC, AB, BC} and for Canada national. The
"loosening fastest" province is `argmax_p delta_pct_pts`. The "tightening
fastest" province (if any province's delta is negative beyond a small
tolerance) is `argmin_p delta_pct_pts`.

Tolerance: a province qualifies for the call-out only if
`|delta_pct_pts| >= 0.3` percentage points. Below 0.3 pp the move is
within LFS month-to-month noise (LFS unemployment-rate provincial
standard errors are typically 0.2-0.3 pp at one month, somewhat smaller
on 12-month differences but still material) and the call-out is not
warranted.

The call-out text in the basics-layer blurb pulls the province name and
the delta value: e.g. "Alberta's unemployment rate has risen 0.8
percentage points over the past year, the most among the four largest
provinces." The fact-checker cross-references the call-out against
the computed CSV. No call-out fires when all four provinces' deltas
fall below the 0.3 pp tolerance band.

### 5.4 Construction script

Script: `analyses/provincial_dispersion.py`. Inputs: the five vectors
in Section 5.1. Output:
`data/processed/provincial_unemployment_dispersion.csv` with columns
`(date, province, ur_current, ur_12m_ago, delta_pct_pts, national_ur)`.

Default chart window: current month only (the dumbbell is a
point-in-time view, not a time series). The CSV retains the full history
so the editorial team can scrub backwards if needed.

### 5.5 What we do not do in v1 basics

- No ten-province bar chart. Clutter and revisits the EDR consolidation
  decision.
- No five-province cut adding Manitoba or Saskatchewan. The
  Prairie-vs-Central divergence story is Pillar E adjacent and is not
  forced into basics.
- No prime-age unemployment by province. Deep-dive material.
- No provincial vacancy or wage data in this panel. Wage band is national
  only (per EDR 4.3 element 3); vacancy is national only (per EDR 4.3
  element 4).

---

## Open questions for editorial-director

1. **Population interpolation when the underlying quarterly print is
   itself revised.** StatCan revises quarterly population estimates with
   each new quarterly release plus at the post-Census benchmark. The
   monthly interpolated path therefore shifts when a new quarterly print
   lands. Do we (a) restate prior-month per-capita values silently, (b)
   carry a vintage stamp on each monthly per-capita observation, or (c)
   freeze prior-month values and accept a small discontinuity at the
   first month after a new quarterly population print? Recommendation:
   option (b), vintage stamp -- consistent with how the BoC MPR
   per-capita tables handle revisions. Confirm.

2. **NPR pre-2024 backfill.** The 2023-2025 and 2024-2026 IRCC plans did
   not publish category-level NPR targets in the same structured form as
   the 2025-2027 plan (the 2024 plan was the first to introduce explicit
   NPR caps). For backfill, do we (a) record `npr_target_total: null`
   and `npr_target_by_category: null` for those years, with a note in
   `structural_break_note` on the 2025-2027 plan flagging the new
   category, or (b) reconstruct rough NPR aggregates from realized flows
   at the time of plan release? Recommendation: (a) -- the methodology
   surface stays clean and the structural-break narrative is preserved.
   Confirm.

3. **3M-MA application to V/U vs ratio-of-MAs.** Two computationally
   different conventions: smooth the ratio (`MA3(V/U)`) or take the
   ratio of smoothed series (`MA3(V) / MA3(U)`). They differ by terms
   that are second-order in the deviations from the mean and are visually
   indistinguishable on the 2015-2026 sample. Default
   recommendation: smooth the ratio (`MA3(V/U)`), matching the
   boc-tracker prior. Confirm or override.

4. **0.3 pp tolerance on the four-province "loosening fastest"
   call-out.** Derived from a rough LFS provincial standard-error scale;
   the call-out tolerance should be tightened (to 0.5 pp) if we want a
   higher bar before firing the call-out in basics-layer prose. Confirm
   or adjust.

5. **Beveridge-curve smoothing axis symmetry.** Confirm both axes get
   3M MA (current proposal). Alternative is to smooth only the noisier
   vacancy axis. Symmetric smoothing is cleaner; asymmetric smoothing
   introduces a subtle path artefact at cyclical turning points.

End of memo.
