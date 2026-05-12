# Pillar E deep dive -- Per-capita output: deceleration or weakness? -- v1 draft

Author: writer (macro-research-department / Sibley Creek).
Style polish: style-editor. Chart inserts: chart-builder.
Date: 2026-05-11.
Status: v1 draft. Mode 3 deep-dive register per
`editorial/dashboard_purpose.md` Section 7 and
`editorial/writing-style.md` Section 1. ASCII-only.

Anchors:
- Insight base: `editorial/insight_base/pillar_e_per_capita_output.md`.
  Tier legend: CANON / INFERRED / OPEN.
- Editorial canon: `editorial/dashboard_purpose.md` Section 5 (Pillar E
  framing), Section 7 (Mode 3 register).
- Voice: `editorial/writing-style.md` Section 1 (chief-economist
  prose), Section 2 (numbers and dates), Section 4 (institution
  names), Section 8 (citation discipline).
- Productivity link: `src/pages/gdp.astro` Productivity plate
  ("structural Canadian fight" framing).

Thesis: The per-capita weakness of 2024-2025 is dominated by the
denominator -- population -- and the denominator is now mechanically
reversing. The forward path to restoring per-capita employment and
per-capita output does not require a productivity miracle; it
requires the IRCC 2026-2028 plan to hold and the prime-age labour
market not to break. Productivity remains the structural fight, but
it is not the fight that explains the last three years.

Charts wired into this draft:
1. Chart E-1: aggregate employment vs employment-rate divergence with
   population YoY (`/charts/pillar-e/divergence_opens_closes.svg`).
   Inserted at the close of the Lede.
2. Chart E-6: net NPR flow + PR landings against IRCC plan trajectory
   (`/charts/pillar-e/npr_wave.svg`). Inserted inside Section II.
3. Chart E-2: prime-age vs youth participation, indexed to pre-COVID
   (`/charts/pillar-e/youth_carries_participation.svg`). Inserted
   inside Section III.
4. Chart E-5: per-capita GDP decomposed into GDP/hours, hours/emp,
   emp/pop (`/charts/pillar-e/denominator_not_productivity.svg`).
   Inserted inside Section IV.
5. Chart E-4: scenario fan for emp/pop landing in 2027
   (`/charts/pillar-e/scenarios_2027.svg`). Inserted inside Section V.

Two insight-base charts (E-3 decomposition and the formal version of
E-5 with hours-per-worker derivation) are marked OPEN in the insight
base and are not author-commissioned in this v1.

---

## 1. Page header copy

- Title (deep-dive voice; sentence case; declarative):

  **The per-capita weakness is mostly a denominator story, and the denominator is turning**

- Deck (one sentence; sets the question and the answer):

  *Canada's per-capita output has run below pre-pandemic trend for
  eight straight quarters, but the arithmetic that drove the gap open
  is now closing it on its own; the structural fight that remains is
  productivity, not population.*

- Date stamp: *Published 2026-05-11. Data vintage: Statistics Canada
  Labour Force Survey, April 2026 (released May 9, 2026); Statistics
  Canada Daily, "Gross domestic product, income and expenditure,
  fourth quarter 2025" (February 27, 2026); Statistics Canada Daily,
  "Labour productivity, hourly compensation and unit labour cost,
  fourth quarter 2025" (March 4, 2026); Statistics Canada Economic
  and Social Reports 36-28-0001, "Recent developments in the
  Canadian economy: Fall 2025"; quarterly population estimates
  (Table 17-10-0009, Q1 2026); IRCC 2026-2028 Immigration Levels
  Plan (November 2025); Bank of Canada Monetary Policy Report (April
  29, 2026); Bank of Canada Staff Discussion Paper 2025-8 (May 2025)
  and Staff Analytical Note 2025-14 (June 2025).*

---

## 2. Lede

> Two Canadian labour-market stories have run in parallel since 2023,
> and they say different things. The headline story is that the
> economy added jobs through the entire tightening cycle and through
> the easing cycle that followed: total employment is higher today
> than it was at any point before 2024. The per-capita story is that
> Canadians, on average, are working less and producing less than
> they were before the pandemic. Real GDP per capita has been below
> its pre-pandemic trend for eight consecutive quarters as of the Q4
> 2025 vintage; the employment rate stood at 60.5% in April 2026, 2.0
> points below the March 2023 cycle peak of 62.5% and 1.7 points below
> the December 2019 baseline of 62.2%.
>
> The standard reading of this divergence is that Canada has a
> productivity crisis. That reading is partly right and importantly
> incomplete. Per-capita output is a ratio, and ratios have
> numerators and denominators. From 2022 through mid-2024, the
> denominator grew at a pace Canada had not seen in seven decades:
> total population growth peaked at 3.18% year-over-year in Q2 2024,
> almost entirely on non-permanent-resident inflows. The employment
> base could not keep up arithmetically; per-capita ratios fell even
> as aggregate employment rose. That mechanic is now running in
> reverse. The IRCC 2026-2028 Immigration Levels Plan, announced in
> November 2025, holds permanent-resident admissions at 380,000 a
> year and caps temporary-resident arrivals at 385,000 in 2026
> and 370,000 in 2027 and 2028. Net non-permanent-resident flow has
> already been negative for four consecutive quarters. Population
> growth has fallen from 3.18% YoY in Q2 2024 to -0.25% YoY in Q1
> 2026.
>
> This piece argues three things. First, the per-capita output gap
> that opened over 2023-2025 was dominated by the population
> denominator, not by collapsing productivity; Canadian business-sector
> labour productivity rose 1.1% in 2025, with unit-labour-cost growth
> at 1.2% -- the lowest annual ULC growth since 2017. Second, the participation-side weakness inside
> the per-capita employment ratio is concentrated almost entirely in
> the youth cohort, and youth participation tracks the international-
> student-permit cycle; prime-age participation sits at cycle highs.
> Third, under any reasonable set of 2026-2028 assumptions, the
> per-capita employment ratio retraces a meaningful share of its
> 2023-2026 decline on population arithmetic alone, before any
> hiring pickup. The denominator that opened the gap is now closing
> it.
>
> None of that vacates the productivity question. Canada's per-hour
> output remains roughly a fifth below the United States and has not
> closed the gap meaningfully in two decades; that is the structural
> fight. It is, however, a different fight from the one the
> per-capita-GDP series was running over 2024 and 2025. The data
> have changed faster than the framing.

![Aggregate employment is at all-time highs, but the employment rate has fallen 2.0 points since the March 2023 cycle peak; the divergence opened as population growth peaked above 3% YoY in 2024 and is now closing as YoY growth has turned negative.](/charts/pillar-e/divergence_opens_closes.svg)

*Total employment (LFS, index Jan 2019 = 100, left axis) and
employment-population ratio for the 15+ population (%, left axis),
overlaid against total population YoY % change (right axis,
quarterly bars). Monthly LFS data and quarterly population
estimates, January 2019 through April 2026 (LFS) / Q1 2026
(population). Source: Statistics Canada, Labour Force Survey Table
14-10-0287-01; Quarterly Population Estimates Table 17-10-0009-01.*

Voice notes:
- Lede holds the central claim: per-capita weakness is
  primarily a denominator story (insight base claim ladder #1, #2,
  #4). Productivity-as-structural-fight framing acknowledges the
  ongoing question while distinguishing it from what drove
  2023-2025.
- "Almost entirely on non-permanent-resident inflows" is the
  loose paraphrase of the 2022-24 NPR composition shift; the
  specific quantification belongs in Section II.

---

## 3. Section I -- The divergence

What the headline series and the per-capita series have done since
2019, and why they have diverged.

> Three series tell the divergence cleanly. The first is total
> employment: through the 2022-2023 tightening cycle, the
> mid-2024-to-late-2025 easing cycle, and the BoC's four consecutive
> holds at 2.25% from October 2025 through April 2026, total
> employment in Canada kept rising. The Labour Force Survey shows
> the level of employment higher in April 2026 than at any
> pre-pandemic point. By the standard read of a labour-market
> aggregate, Canada was not in a recession.
>
> The second is the employment rate. The share of the 15+ population
> with a job peaked at 62.5% in March 2023 and has trended down
> steadily since: 61.3% by June 2024, 60.9% by June 2025, and 60.5%
> in April 2026. The pre-COVID December 2019 baseline was 62.2%. By
> April 2026 the employment rate was 2.0 points below the cycle peak
> and 1.7 points below the pre-pandemic baseline -- a deeper gap than
> the headline unemployment rate of 6.9% suggested in isolation. The
> participation rate followed a similar arc, peaking at 65.9% in June
> 2023 and falling to 65.0% by April 2026, 90 bps below cycle peak.
>
> The third series is per-capita real GDP. Statistics Canada's
> Economic and Social Reports review for Fall 2025 noted that real
> GDP per capita had been below its pre-pandemic trend for eight
> consecutive quarters at that point. The Q4 2025 release, published
> February 27, 2026, showed per-capita real GDP unchanged
> quarter-over-quarter after a +0.5% Q/Q reading in Q3 2025, with
> aggregate real GDP for 2025 at +1.7% -- the slowest annual print
> outside 2020. By the per-capita measure, the average Canadian was
> producing less in 2025 than in 2019. By the aggregate measure,
> Canada was growing.
>
> Both readings are correct. They diverge because the population
> base they share grew at a pace Canada had not run in seven decades.
> The Quarterly Population Estimates (Table 17-10-0009) put total
> population YoY growth at 3.18% in Q2 2024 -- a peak rate higher
> than anything in the post-war series outside the immediate
> post-war years themselves. The labour market could keep adding
> jobs in aggregate and still lose ground per person, because
> per-person is a ratio against a denominator that was running ahead
> of any plausible hiring pace.

---

## 4. Section II -- The denominator turns

What the IRCC 2026-2028 plan does, what the NPR series has already
done, and how fast the gap closes on arithmetic alone.

> The denominator is no longer running ahead. Quarterly population
> estimates from Statistics Canada show YoY total population growth
> at 0.94% in Q3 2025 and -0.25% in Q1 2026 -- the first
> multi-quarter outright contraction in the post-war series outside
> emigration anomalies. Net non-permanent-resident flow, the
> component that drove the 2022-2024 surge, has printed negative for
> four consecutive quarters: -55k in Q1 2025, -59k in Q2, -176k in
> Q3, and -171k in Q4. The composition of Canadian population growth
> has inverted within eighteen months.
>
> The policy framework underpinning that inversion is the IRCC
> 2026-2028 Immigration Levels Plan, announced in November 2025.
> Permanent-resident admissions are stabilized at 380,000 a year
> across 2026, 2027, and 2028 -- below the 500,000 path under the
> previous plan but above the pre-pandemic baseline of roughly
> 330,000. Temporary-resident arrivals are capped at 385,000 in 2026
> and 370,000 in 2027 and 2028, with sub-caps of 155,000
> international students in 2026 and 150,000 in 2027-28, and 230,000
> temporary workers in 2026 and 220,000 in 2027-28. The stated
> objective, in the government's own language, is "to return to
> sustainable immigration levels through continued decreases to
> temporary resident arrivals and stabilized permanent resident
> admissions." It is a multi-year framework, and it sets the
> trajectory of the per-capita denominator through the end of 2028.
>
> The Bank of Canada has taken the framework on board. The April
> 2026 Monetary Policy Report notes that "population growth slowdown
> is constraining demand and weighing on housing activity" and that
> potential output growth is expected to slow in 2026 and recover in
> 2027-2028 as the immigration trajectory normalizes. Bank of Canada
> Staff Analytical Note 2025-14 on potential output decomposes the
> labour-input contribution to potential growth and shows how
> sensitive the medium-term path is to the trajectory of working-age
> population growth specifically.

![Net non-permanent-resident flow has been negative for four consecutive quarters; the IRCC 2026-2028 plan locks in the slower trajectory through 2028.](/charts/pillar-e/npr_wave.svg)

*Permanent-resident landings (quarterly bars, stacked below zero
when net) and net non-permanent-resident flow (quarterly bars),
2018Q1 through 2025Q4 actuals, with IRCC plan-implied trajectory
2026Q1 through 2028Q4 shown as a dashed forward line. Source:
Statistics Canada Table 17-10-0040; Immigration, Refugees and
Citizenship Canada, "2026-2028 Immigration Levels Plan,
supplementary information," November 2025.*

> The arithmetic of the closing gap is straightforward, and
> deserves naming directly. If population growth runs at roughly
> 0.3-0.6% in 2026-2027 (consistent with the IRCC plan and the NPR
> contraction already underway) and employment grows even modestly
> -- say at 0.5-1.0% over the same window -- the employment rate
> rises mechanically by roughly 0.6 to 0.9 points over the next six
> quarters. That alone closes roughly half of the 1.7-point gap
> between April 2026's 60.5% reading and the pre-COVID 62.2%
> baseline. None of that requires a hiring boom, an investment
> renaissance, or a productivity inflection. It requires the
> population denominator to behave the way the IRCC plan says it
> will. The plan vintage is the forward variable this turns on.

---

## 5. Section III -- Who is missing from the labour force

Why the participation-rate component of the per-capita weakness is
almost entirely a youth story, not a prime-age story.

> Inside the falling employment rate sits a falling participation
> rate -- the share of the 15+ population that is either working or
> looking for work. Participation peaked at 65.9% in June 2023 and
> sat at 65.0% in April 2026. The 90-bps decline matters for the
> per-capita employment ratio, and it has been read as evidence of
> cyclical discouragement: workers giving up on the search as the
> labour market softens. The disaggregated data tell a different
> story.
>
> Prime-age (25-54) participation in April 2026 was 88.5% -- 0.4
> points below the June 2023 cycle peak of 88.9% and well above the
> pre-COVID range. Among the cohort that does the structural work in
> the Canadian labour force, the participation rate is essentially
> at a cycle high. Youth (15-24) participation tells the opposite
> story: 65.5% in December 2019, 65.2% in June 2023, 63.1% in June
> 2024, and 62.9% in April 2026 -- 2.6 points below the pre-COVID
> baseline and roughly 3 points below the post-COVID cycle peak of
> 66.1% in February 2023. Almost the entire decline in the aggregate
> participation rate over 2023-2026 sits in the youth cohort.

![Prime-age participation is essentially at a cycle high; youth participation is 2.6 points below its pre-COVID baseline. The aggregate participation decline is almost entirely a youth story.](/charts/pillar-e/youth_carries_participation.svg)

*Participation rate, prime-age (25-54) and youth (15-24), indexed
to December 2019 = 0 in percentage points. Monthly, January 2019
through April 2026. Shaded region from September 2023 marks the
international-student-permit cap announcement. Source: Statistics
Canada, Labour Force Survey Table 14-10-0287-01.*

> The youth cohort is also the cohort most exposed to the
> international-student-permit cycle. International students entering
> Canada under study permits become labour-force participants in the
> youth age range; when student-permit inflows surge, youth
> participation rises mechanically, and when they contract, it
> falls. The IRCC 2026-2028 plan caps international-student arrivals
> at 155,000 in 2026 and 150,000 thereafter, well below the
> 2022-2023 inflow rates. The drawdown in youth participation since
> mid-2024 is consistent in shape and timing with the student-permit
> contraction, and inconsistent with a cyclical-discouragement story
> that would have hit prime-age participation harder.
>
> The youth unemployment rate has also risen sharply -- 14.3% in
> April 2026 against a 10-12% range in 2023. The prime-age
> unemployment rate stands at 6.0%, up from a 4.2-4.9% range in 2023;
> that is a real cyclical move, but a smaller one in relative terms,
> and the prime-age cohort has continued to be drawn into the labour
> force rather than discouraged out of it. The job vacancy rate has
> fallen to 2.6% as of February 2026 (StatCan Table 14-10-0325) --
> below the 2019 average of roughly 3.2% and well off the 6.0%
> April 2022 cycle peak. EI regular beneficiaries sit at 542,000 in
> February 2026, off November 2025's 568,000 but well above the
> 400,000 lows of 2022. The labour market has loosened; it has not
> broken.
>
> That distinction matters for the forward read. The
> participation-side decline embedded in the per-capita employment
> ratio reflects an immigration-policy adjustment in the youth
> cohort, not a structural loss of attachment in the prime-age
> cohort. As the NPR wave unwinds, the youth participation rate
> normalizes against a smaller youth population base. The prime-age
> cohort -- which does most of the per-capita-output work -- never
> left.

---

## 6. Section IV -- Productivity, properly placed

Per-capita output decomposed: how much of the 2023-2025 weakness was
GDP/hours, how much was hours/employee, how much was the
employment-population ratio.

> Per-capita GDP decomposes algebraically into three terms:
> GDP-per-hour (labour productivity), hours-per-employed-person
> (intensive margin), and the employment-population ratio
> (extensive margin). The standard popular framing assigns the bulk
> of Canadian per-capita weakness to the first term, on the strength
> of the well-known long-running productivity gap with the United
> States. The 2023-2025 decomposition does not support that
> assignment.
>
> Labour productivity in the Canadian business sector rose 1.1% in
> 2025, per the Statistics Canada productivity release of March 4,
> 2026; over the same year, unit labour costs grew 1.2% -- the
> lowest annual ULC growth rate since 2017. The quarterly print for
> Q4 2025 was -0.1% Q/Q on business-sector productivity, with hours
> worked also -0.1% Q/Q and unit labour costs +0.7% Q/Q -- a softer
> quarter, but inside the post-2022 range and well off the negative
> readings of 2022-2023. Over the full 2023-2025 window, GDP-per-hour
> was not the term that pulled per-capita output below trend; the
> employment-population ratio was.
>
> Bank of Canada Staff Discussion Paper 2025-8, published in May
> 2025, sharpens the point in a useful direction. The paper
> documents that a material share of the measured divergence in
> wage growth between temporary foreign workers / non-permanent
> residents and Canadian-born workers reflects compositional
> change in the non-permanent-resident share of the workforce. The
> implication for productivity measurement is direct: a fraction of
> what looked like productivity weakness in 2022-2024 was a
> composition effect from a rapid shift in workforce mix toward
> lower-experience, lower-tenure non-permanent-resident workers in
> lower-output-per-hour roles. As that compositional shift reverses,
> measured productivity should improve mechanically -- and the 2025
> +1.1% productivity print is consistent with that mechanical
> improvement having begun.

![Per-capita GDP decomposed: the employment-population ratio carried the 2023-2025 weakness; GDP-per-hour did not.](/charts/pillar-e/denominator_not_productivity.svg)

*Real GDP per capita, YoY % change, decomposed into contributions
from GDP-per-hour (labour productivity), hours-per-employed-person
(intensive margin), and employment-population ratio (extensive
margin). Quarterly, 2019Q1 through 2025Q4. Stacked bar with line
overlay for net YoY change. Source: Statistics Canada Tables
36-10-0480-01 (productivity), 14-10-0036-01 (hours), 14-10-0287-01
(employment), and 17-10-0009-01 (population). Author calculations.
Hours-per-worker derivation marked as preliminary; see methodology
note.*

> The structural Canadian productivity gap remains. Canadian
> business-sector productivity is roughly a fifth below US levels
> and has not closed meaningfully in two decades; the StatCan
> Economic and Social Reports article on firm-size composition (and
> the longer literature on capital deepening, R&D intensity, and
> the small-firm productivity wedge) points to a slow-moving set of
> structural causes that policy has visibly struggled to address.
> That fight is real. It is also a multi-decade fight, not a
> two-year one, and reading the 2023-2025 per-capita-GDP series as
> the productivity-crisis signal it has often been claimed to be
> overstates what the series tells us. The denominator did most of
> the work. Productivity in 2025 actually grew, by 1.1%.
>
> Distinguishing the two questions is the central editorial point.
> Per-capita output below pre-pandemic trend over 2024-2025 is a
> story about how fast the population denominator grew relative to
> what the employment base could absorb. The longer-run productivity
> gap with peer economies is a separate story about capital,
> firm-size distribution, and innovation intensity. Treating them as
> a single narrative -- "Canada has a productivity crisis, and
> per-capita GDP is the evidence" -- conflates them and assigns the
> wrong policy lever to the wrong problem.

---

## 7. Section V -- Where the per-capita employment rate lands in 2027

Three scenarios, all conditional on inputs that are now reasonably
well-defined.

> The forward arithmetic on the per-capita employment ratio is
> tractable enough to take seriously, if it is framed as scenario
> rather than forecast. Three readings are useful.
>
> Scenario A is population deceleration only. Holding employment at
> its April 2026 level and letting population grow at 0.3-0.6%
> through end-2027 -- broadly consistent with the IRCC plan and the
> observed NPR contraction -- raises the employment rate by roughly
> 0.6 to 0.9 points over six quarters, to a range of 61.1-61.4% by
> end-2027. That closes roughly half of the gap to the pre-COVID
> 62.2% baseline without any hiring pickup at all. It is the pure
> denominator effect.
>
> Scenario B is cyclical recovery only. If the unemployment rate
> retraces to its early-2024 level of around 5.8% but population
> grows at the IRCC-plan pace, the employment rate lands in a
> 61.6-61.9% range by end-2027 -- a more substantial recovery, but
> still short of the pre-COVID baseline.
>
> Scenario C combines the two. Plausible: if both the denominator
> normalizes per the plan and the unemployment rate retraces toward
> the early-2024 level, the employment rate sits in a 62.0-62.5%
> range by end-2027 -- effectively at, or modestly above, the
> pre-COVID baseline.

![Scenario fan for the employment-population ratio through 2027: population deceleration alone closes roughly half the gap; combined with cyclical recovery, the ratio retraces to pre-COVID.](/charts/pillar-e/scenarios_2027.svg)

*Employment-population ratio (15+, %), monthly historical January
2015 through April 2026, with three illustrative scenario fans
through December 2027: Scenario A (population deceleration only),
Scenario B (cyclical recovery only), Scenario C (both). Pre-COVID
December 2019 reference line at 62.2%. Source: Statistics Canada
Labour Force Survey Table 14-10-0287-01 (historical); author
illustrative scenarios per assumptions in text. Labelled
explicitly as scenarios, not forecasts.*

> Two sensitivities matter. The first is youth participation: if
> the international-student drawdown is stickier than the IRCC
> plan's headline numbers suggest, and youth participation holds at
> 63% rather than retracing toward its pre-COVID 65.5%, the
> Scenario A and C end-points drop by roughly 0.3 points each. The
> second is the prime-age participation rate: it is currently at
> cycle highs, and a meaningful retracement would pull all three
> scenarios down. Prime-age participation is the variable to watch
> for cyclical reversal; youth participation is the variable to
> watch for immigration-policy follow-through.
>
> Read together, the scenarios make a narrower claim than a
> single point forecast. Under any reasonable parameterization of
> the inputs that are now reasonably well-defined -- the IRCC plan,
> the observed NPR contraction, a labour market that loosens but
> does not break -- the per-capita employment ratio retraces a
> material share of its 2023-2026 decline within six quarters. The
> headline-versus-per-capita divergence is a 2024-2025 story that is
> mechanically closing on its own.

---

## 8. Section VI -- What would change our mind

Contingent payoff. If X, then Y.

> Three triggers fire against this thesis; each is observable in
> series that publish before the end of 2026.
>
> *If* prime-age (25-54) participation falls below 87.5% on a
> three-month moving-average basis (currently 88.5%), *then* the
> framing here is wrong in an important way. A prime-age
> participation move of that size would say the labour-market
> softening has begun to detach prime-age workers from job search --
> the cyclical-discouragement story that the youth-driven aggregate
> participation decline so far has not supported. In that case the
> per-capita weakness has rotated from being primarily a population
> story to being primarily a labour-market-detachment story, and
> the forward path becomes considerably worse than the scenarios in
> Section V imply.
>
> *If* the IRCC 2026-2028 plan is revised upward in either the
> permanent-resident or the temporary-resident sub-cap before the
> next plan vintage (2027-2029, conventionally announced in
> November 2026), *then* the denominator-closes-the-gap mechanic
> weakens proportionally. The plan vintage is the forward variable
> this piece turns on; if the plan changes, the arithmetic in
> Section II changes with it.
>
> *If* labour productivity prints two consecutive negative quarterly
> Q/Q readings in the business-sector series after the 2025 annual
> recovery, *then* the composition-effect reversal documented in BoC
> SDP 2025-8 is being overwhelmed by something else -- and the
> productivity question moves back toward the centre of the
> per-capita story. The Statistics Canada productivity release is
> quarterly; the next two prints (Q1 2026, expected June 2026; Q2
> 2026, expected September 2026) are the cheapest test.
>
> The single cheapest test of the central thesis is the next
> Quarterly Population Estimates release (Table 17-10-0009, Q2 2026
> vintage, expected late September 2026). If the population
> contraction observed in Q4 2025 and Q1 2026 reverses sharply --
> say, back above +1.5% YoY total population growth -- the IRCC
> plan is not binding the way Section II claims, and the
> denominator side of the story unwinds. If the population series
> continues at or near zero YoY, the mechanic in Section II is
> doing exactly what the plan vintage implies it should.

---

## 9. Sources + footnotes

Primary citations. Big-Six bank economics notes are not cited as
views; the Bank of Canada, Statistics Canada, and Immigration,
Refugees and Citizenship Canada are the institutions this question
turns on.

1. **Statistics Canada, Labour Force Survey, Table 14-10-0287-01.**
   Monthly. Employment, unemployment, participation, and
   employment-population ratios by age and sex. Vintage: April 2026
   release (May 9, 2026). Cited for employment-rate trajectory,
   prime-age and youth participation, and the youth-versus-prime-age
   disaggregation.

2. **Statistics Canada, Quarterly Population Estimates, Table
   17-10-0009-01.** Quarterly. Total population and components of
   change. Vintage: Q1 2026 release. Cited for the population YoY
   trajectory from +3.18% in Q2 2024 to -0.25% in Q1 2026.

3. **Statistics Canada, Components of Population Change Table
   17-10-0040-01.** Quarterly. Net non-permanent-resident flow.
   Cited for the four-quarter negative-NPR sequence (Q1 2025 -55k
   through Q4 2025 -171k).

4. **Statistics Canada Daily, "Gross domestic product, income and
   expenditure, fourth quarter 2025."** Published February 27,
   2026. Cited for the eight-consecutive-quarters per-capita-GDP
   characterization, the Q4 2025 unchanged Q/Q per-capita print,
   and the +1.7% 2025 aggregate-GDP annual figure.

5. **Statistics Canada Economic and Social Reports 36-28-0001,
   "Recent developments in the Canadian economy: Fall 2025."**
   Cited for the per-capita-GDP-below-trend characterization at the
   eight-consecutive-quarters mark.

6. **Statistics Canada Daily, "Labour productivity, hourly
   compensation and unit labour cost, fourth quarter 2025."**
   Published March 4, 2026. Cited for the Q4 2025 quarterly prints
   (productivity -0.1% Q/Q, hours -0.1% Q/Q, ULC +0.7% Q/Q), the
   2025 annual +1.1% productivity figure, and the 2025 +1.2% annual
   unit-labour-cost growth (lowest since 2017).

7. **Statistics Canada Tables 36-10-0480-01, 14-10-0036-01, and
   14-10-0325-01.** Productivity and unit labour cost; total hours
   worked; job vacancies. Cited as data sources for the
   decomposition chart (E-5) and the JVWS vacancy-rate figure.

8. **Statistics Canada Table 14-10-0011-01.** Employment Insurance
   regular beneficiaries. Cited for the 542k February 2026 reading
   versus the 568k November 2025 reading and the 400k 2022 lows.

9. **Immigration, Refugees and Citizenship Canada, "2026-2028
   Immigration Levels Plan, supplementary information."** Published
   November 2025. URL pattern: canada.ca/en/immigration-refugees-
   citizenship/corporate/mandate/corporate-initiatives/levels/
   supplementary-immigration-levels-2026-2028.html. Cited for the
   380,000 annual PR target, the 385k / 370k / 370k temporary-
   resident caps, and the international-student and
   temporary-worker sub-caps.

10. **Bank of Canada, Monetary Policy Report.** April 29, 2026.
    Cited for the population-growth-slowdown language and the
    potential-output trajectory framing for 2026-2028.

11. **Bank of Canada, Staff Discussion Paper 2025-8.** May 2025.
    Cited for the compositional decomposition of measured wage
    growth between non-permanent-resident and Canadian-born workers
    and the implication for measured productivity.

12. **Bank of Canada, Staff Analytical Note 2025-14.** "Potential
    output in Canada." June 2025. Cited for the labour-input
    contribution to potential growth and the sensitivity of the
    medium-term path to working-age population growth.

Note on citation discipline (per `editorial/writing-style.md`
Section 8 and `editorial/dashboard_purpose.md` Section 1): the Bank
of Canada, Statistics Canada, and IRCC are the anchor
institutions. Where consensus-forecaster numbers appear in
scenario framing, they are aggregated and unattributed by bank
name; no Big-Six economics note is cited as an authoritative view.

---

End of v1 draft.
