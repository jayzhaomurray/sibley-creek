# Pillar E: Per-capita output -- deceleration or weakness?

Owner: researcher. Fact scaffold for writer. Section: Labour.

Framing (sections.ts): "Headline labour print is flattering; per-capita
series is not. Separate the population-deceleration story from cyclical
weakness."

Tier legend: **CANON** = verified primary source, value reproducible from
project data or named StatCan/BoC/IRCC release. **INFERRED** = derived in
this doc with arithmetic from canon series. **OPEN** = needs decision
or further data pull before drafting.

Project data referenced: `data/raw/employment_rate.csv`,
`participation_rate.csv`, `pop_total.csv`, `pop_immigrants.csv`,
`pop_net_npr.csv`, `pop_npr_inflows.csv`, `lf_participation_youth.csv`,
`lf_participation_prime.csv`, `youth_unemployment_rate.csv`,
`prime_age_unemployment_rate.csv`, `job_vacancy_rate.csv`,
`ei_regular_beneficiaries.csv`, `unit_labour_cost.csv`,
`lfs_micro.csv`. All values current to April 2026 LFS / Q4 2025 GDP
/ Q4 2025 productivity vintage.

---

## 1. The headline divergence -- aggregate vs per-capita

**CANON**

- Employment rate (15+, SA) trajectory: 62.4 (Jan-23 cycle peak) ->
  61.3 (Jun-24) -> 60.9 (Jun-25) -> 60.5 (Apr-26). Pre-COVID Dec-19
  baseline = 62.2. April 2026 reading is 1.7 pts below cycle peak and
  1.7 pts below pre-COVID. Source: StatCan Table 14-10-0287; project
  file `data/raw/employment_rate.csv`.
- Participation rate (15+, SA): 65.9 (Jun-23) -> 65.0 (Apr-26).
  90 bps below cycle peak. Source: same table.
- Q4 2025 real GDP per capita: unchanged Q/Q after +0.5% Q/Q in Q3.
  StatCan notes per-capita real GDP has been below its pre-pandemic
  trend for **eight consecutive quarters** as of Fall 2025 review.
  Source: StatCan Daily 2026-02-27 "Gross domestic product, income and
  expenditure, fourth quarter 2025"; StatCan Economic and Social
  Reports 36-28-0001 "Recent developments in the Canadian economy:
  Fall 2025."
- Aggregate real GDP +1.7% in 2025, slowest since 2020. Same StatCan
  Daily release.
- Q4 2025 business sector hours worked -0.1% Q/Q; labour productivity
  -0.1% Q/Q; ULC +0.7% Q/Q. Source: StatCan Daily 2026-03-04 "Labour
  productivity, hourly compensation and unit labour cost, fourth
  quarter 2025."

**INFERRED**

- Working-age (15+) population YoY: pop_total YoY went 3.18% (Q2-24
  peak) -> 0.94% (Q3-25) -> -0.25% (Q1-26). The population baseline
  that mechanically depressed per-capita ratios in 2024 is now
  reversing; the gap between headline and per-capita prints will
  narrow on arithmetic alone over the next 4 quarters. (Derived from
  `data/raw/pop_total.csv`, StatCan Table 17-10-0009.)

---

## 2. The population side -- IRCC plan and StatCan estimates

**CANON**

- IRCC **2026-2028 Immigration Levels Plan** (announced Nov 2025): PR
  admissions stabilized at **380,000/yr for 2026, 2027, 2028**. New
  temporary-resident arrivals capped at **385,000 in 2026** and
  **370,000 in 2027 and 2028**. Within that: international students
  155k (2026) / 150k (2027-28); temporary workers 230k (2026) / 220k
  (2027-28). Stated objective: "return to sustainable immigration
  levels through continued decreases to temporary resident arrivals
  and stabilized permanent resident admissions." Source:
  canada.ca/en/immigration-refugees-citizenship/corporate/mandate/
  corporate-initiatives/levels/supplementary-immigration-levels-2026-
  2028.html.
- Net NPR flow has gone negative for four consecutive quarters in
  project data: Q1-25 -55k, Q2-25 -59k, Q3-25 -176k, Q4-25 -171k.
  Source: StatCan Table 17-10-0040; `data/raw/pop_net_npr.csv`.
- BoC April 2026 MPR: "population growth slowdown is constraining
  demand and weighing on housing activity"; potential output growth
  expected to slow in 2026, recover 2027-2028. Source:
  bankofcanada.ca/publications/mpr/mpr-2026-04-29/.

**INFERRED**

- The Q4-25 pop_total absolute decline (41.65M -> 41.47M, Q3-25 to
  Q1-26) is the first multi-quarter population *contraction* in the
  series back to 1946 outside emigration anomalies. Treat as central
  only if cross-checked against StatCan's quarterly
  demographic estimates release (Table 17-10-0009 official; check for
  revisions).

**OPEN**

- StatCan medium-term population projection vintage (M-series): does
  the most recent projection incorporate the 2026-2028 IRCC plan, or
  the 2025-2027 plan? Affects 2027 per-capita scenario math in
  Section 5.

---

## 3. Cyclical-weakness indicators

**CANON** (all StatCan LFS Table 14-10-0287 unless noted; project CSVs):

- Prime-age (25-54) participation: 88.5 (Apr-26) -- holding near cycle
  high (Jun-23 88.9). Source: `lf_participation_prime.csv`.
- Youth (15-24) participation: 65.5 (Dec-19) -> 65.2 (Jun-23) -> 63.1
  (Jun-24) -> 62.9 (Apr-26). Down 2.3 pts vs pre-COVID, 2.6 pts vs
  cycle peak. Source: `lf_participation_youth.csv`.
- Youth unemployment rate: 14.3% (Apr-26) vs 11-12% range in 2023.
  Prime-age unemployment: 6.0% (Apr-26) vs 4.7-5.0% in 2023. Source:
  `youth_unemployment_rate.csv`, `prime_age_unemployment_rate.csv`.
- Job vacancy rate: 2.6% (Feb-26) -- down from cycle peak of ~5.7%
  (Apr-22), now slightly below 2019 average (~3.2%). Source: StatCan
  Table 14-10-0325 / JVWS; `data/raw/job_vacancy_rate.csv`.
- EI regular beneficiaries: 542k (Feb-26), down from 568k (Nov-25)
  but still elevated vs 2022 lows of ~400k. Source: StatCan Table
  14-10-0011; `data/raw/ei_regular_beneficiaries.csv`.
- ULC index: 131.7 (Q4-25), up from 129.7 (Q4-24). Annual ULC growth
  in 2025 = 1.2%, lowest since 2017. Source: StatCan Table
  36-10-0480 / Daily 2026-03-04.

**INFERRED**

- Participation-side weakness is concentrated in youth (15-24), not
  prime-age. This is consistent with student-permit drawdowns under
  the 2024 NPR cap (international students were ~25% of net new
  labour-force entrants in 2023). If correct, the cyclical/structural
  separation is partially observable: prime-age participation looks
  cyclical-normal; youth participation looks immigration-policy-
  driven.

---

## 4. Decomposition of per-capita employment

Identity: emp/pop = (emp/LF) x (LF/WAP) x (WAP/pop).

**CANON inputs** (Apr-26 vs Jun-23 cycle peak, from project CSVs):

- emp/pop (15+): 60.5 vs 62.3 -> -1.8 pts (-2.9% relative).
- emp/LF = 1 - UR. UR Apr-26 ~6.9% (panel-1 trajectory continues
  from 7.0 range); 1-UR ~93.1 vs ~94.6 in Jun-23.
- LF/WAP = participation rate: 65.0 vs 65.9.
- WAP/pop: not directly in project CSVs; StatCan Table 17-10-0005
  provides 15+ share of total pop. **OPEN**: pull WAP/pop series for
  exact decomposition.

**INFERRED arithmetic** (sign + rough magnitude, NOT precise without
WAP/pop):

- Of the ~1.8 pt drop in emp/pop since Jun-23, roughly: ~1.4 pts from
  emp/LF (rising unemployment, cyclical), ~0.9 pts from LF/WAP
  (falling participation), with WAP/pop a small offsetting positive
  as 15+ share of population rose with immigration. Cyclical and
  participation components dominate; WAP/pop did NOT drive the
  weakness on the way down and won't drive its reversal on the way
  back up.

**OPEN**

- Need clean monthly LF/WAP and WAP/pop split to publish exact
  contribution shares. Writer should NOT commit to percentage-point
  attribution without a derived series in `analyses/`.

---

## 5. Scenarios -- where per-capita employment lands in 2027

**INFERRED, scenario arithmetic. All conditional, mark as such.**

Anchor: emp/pop Apr-26 = 60.5. Pre-COVID Dec-19 = 62.2.

- **Scenario A: population deceleration only.** IRCC 2026-2028 plan
  + observed NPR contraction implies population growth ~0.3-0.6% in
  2026-27 vs 3.1% peak. Holding employment level constant, emp/pop
  mechanically rises ~0.6-0.9 pts over 6 quarters -> ~61.1-61.4 by
  end-2027. Closes roughly half of the gap to pre-COVID without any
  hiring pickup.
- **Scenario B: cyclical recovery only.** If UR retraces to 5.8%
  (early-2024 level) but population grows at IRCC-plan pace,
  emp/pop ~61.6-61.9 by end-2027.
- **Scenario C: both.** Plausible range 62.0-62.5 by end-2027 --
  effectively restoring pre-COVID.

**OPEN**

- Sensitivity to participation: scenarios above assume participation
  recovers ~0.5 pts. If youth participation stays at 63 (international
  student drawdown is sticky), Scenario A and C anchors drop ~0.3
  pts each.

---

## 6. Productivity link to per-capita GDP

Identity: GDP/pop = (GDP/hours) x (hours/emp) x (emp/pop).

**CANON**

- GDP/hours (labour productivity index, business sector): -0.1% Q4-25
  Q/Q; +1.2% in 2025 full year (highest annual gain in several years
  per StatCan release). Source: StatCan Daily 2026-03-04.
- Canada-US productivity gap: see StatCan 36-28-0001/2025012/article
  "The role of firm size in the Canada-US labour productivity gap
  since 2000."
- BoC SDP 2025-8 (Picot-style): temp-foreign-worker / non-permanent
  resident composition shift accounts for material part of measured
  wage growth divergence between temp workers and Canadian-born;
  composition effect is observable in LFS micro. Implication: some
  of measured labour productivity weakness is composition, not
  technology. Source: bankofcanada.ca/2025/05/staff-discussion-
  paper-2025-8/.

**INFERRED**

- The per-capita-GDP weakness ("eight consecutive quarters below
  pre-pandemic trend") is dominated by the emp/pop term, not the
  GDP/hours term. Productivity in 2025 actually grew. The framing
  "Canada has a productivity crisis" understates the role of the
  denominator (population) in the per-capita number.

**OPEN**

- Hours/emp decomposition over 2023-2025: did average hours per
  worker compress (a cyclical tell) or hold? Need a derived series
  from SEPH Table 14-10-0223 or LFS Table 14-10-0036. Project does
  not currently expose hours-per-worker in panel data.

---

## Claim ladder -- central candidates

Ranked by confidence:

1. **(Highest)** Aggregate labour and GDP look OK; per-capita has been
   below pre-pandemic trend for eight straight quarters. Citation:
   StatCan Daily 2026-02-27 GDP Q4-25; 36-28-0001 Fall 2025 review.
2. **(High)** Population growth has flipped from +3.1% YoY peak
   (Q2-24) to -0.25% YoY (Q1-26) on quarterly StatCan estimates --
   the per-capita denominator is now working in the *opposite*
   direction it was in 2024. IRCC 2026-2028 plan locks this in.
   Citation: StatCan Table 17-10-0009; IRCC 2026-2028 supplementary
   info.
3. **(High)** The weakness is concentrated in youth participation and
   employment, not prime-age. Prime-age participation is at cycle
   highs; youth is 2.3 pts below pre-COVID. Citation: project CSVs
   from StatCan Table 14-10-0287.
4. **(Medium)** Per-capita-GDP weakness is more a denominator story
   than a productivity story; labour productivity actually rose 1.2%
   in 2025. Citation: StatCan Daily 2026-03-04.
5. **(Medium)** Under any reasonable 2027 scenario, per-capita
   employment mechanically retraces 0.6-1.5 pts as population growth
   normalizes -- the headline-vs-per-capita divergence is a 2024-25
   story that is closing on its own. Cite as scenario, not forecast.

---

## Chart specifications (writer commissions these inline)

**Chart E-1: "The divergence opens, then closes."**
- Data: total employment (LFS, index Jan-19 = 100) vs emp/pop ratio
  (15+, %); right axis = total pop YoY %.
- Cadence: monthly LFS / quarterly pop.
- Window: Jan 2019 - latest.
- Treatment: dual-line + bar (pop YoY as faded bars). Annotate
  Q2-24 pop-YoY peak and Q1-26 inflection.
- Framework Q: 1, 2.

**Chart E-2: "Youth carries the participation drop."**
- Data: participation rate -- prime-age (25-54) vs youth (15-24),
  indexed to Dec-19 = 0 in pts.
- Cadence: monthly.
- Window: Jan 2019 - latest.
- Treatment: two-line, shared zero baseline = pre-COVID. Shade post
  Sep-23 (student-permit cap announcement).
- Framework Q: 3.

**Chart E-3: "Decomposition of per-capita employment change."**
- Data: stacked-bar contributions from (emp/LF), (LF/WAP),
  (WAP/pop) to YoY change in emp/pop.
- Cadence: quarterly.
- Window: 2019Q1 - latest.
- Treatment: stacked bar with black-dot line for net change.
- Framework Q: 4. **PRECONDITION**: writer must trigger an
  `analyses/per_capita_decomp.py` script first; series does not
  currently exist in panel data.

**Chart E-4: "Where per-capita employment lands in 2027."**
- Data: historical emp/pop + three scenario fan lines (A, B, C from
  Section 5).
- Cadence: monthly historical, quarterly forecast.
- Window: Jan 2015 - Dec 2027.
- Treatment: solid historical line, dashed scenario fans, pre-COVID
  reference line at 62.2. Label clearly as illustrative scenarios,
  not forecasts.
- Framework Q: 5.

**Chart E-5: "It's the denominator, not productivity."**
- Data: real GDP per capita YoY (%) decomposed into GDP/hours,
  hours/emp, emp/pop contributions.
- Cadence: quarterly.
- Window: 2019Q1 - latest.
- Treatment: stacked bar + line.
- Framework Q: 6. **PRECONDITION**: requires hours-per-worker
  derivation from SEPH or LFS supplementary tables.

**Chart E-6: "The NPR wave goes out as fast as it came in."**
- Data: net NPR flow (quarterly), permanent-resident landings
  (quarterly), and IRCC-plan implied trajectory.
- Cadence: quarterly.
- Window: 2018Q1 - 2028Q4 (with plan path).
- Treatment: two stacked bars (PR + net NPR) + dashed plan-implied
  forward line.
- Framework Q: 2.

---

## Source roster (primary only)

- StatCan Table 14-10-0287 (LFS monthly).
- StatCan Table 17-10-0009 (population estimates, quarterly).
- StatCan Table 17-10-0040 (NPR / immigration components).
- StatCan Table 14-10-0325 / JVWS (job vacancies).
- StatCan Table 14-10-0011 (EI beneficiaries).
- StatCan Table 36-10-0104 / 0480 (productivity and ULC).
- StatCan Daily 2026-02-27 (GDP Q4 2025).
- StatCan Daily 2026-03-04 (Productivity Q4 2025).
- StatCan Economic and Social Reports 36-28-0001 (Fall 2025
  developments).
- IRCC 2026-2028 Immigration Levels Plan, supplementary info
  (canada.ca, Nov 2025).
- BoC Monetary Policy Report, April 2026.
- BoC Staff Discussion Paper 2025-8 (Shift in Canadian immigration
  composition and effect on wages, May 2025).
- BoC Staff Analytical Note 2025-14 (Potential output in Canada,
  June 2025).
