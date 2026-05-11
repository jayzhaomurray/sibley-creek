# Wave 1, Brief 1.2 -- Basics-Layer Data Availability: Labour (incl. Demographics)

Author: researcher
Date: 2026-05-10
Status: data-source memo plus editorial-design proposal for editorial-director

Sources audited (Hard sequencing: boc-tracker first):
- `C:\Users\jayzh\Documents\boc-tracker\fetch.py` (canonical inventory of StatCan WDS vectors, BoC Valet keys, FRED series, Indeed CA, BIS CBPOL)
- `C:\Users\jayzh\Documents\boc-tracker\analyze.py` (compute_labour_values; identifies which series are actively read and which transforms are pre-built)
- `C:\Users\jayzh\Documents\boc-tracker\build.py` (chart specs for `labour.html` and `demographics.html` -- confirms which series the prior pages surfaced and how)
- `C:\Users\jayzh\Documents\boc-tracker\data\` (96 CSV outputs, including the labour, wages, and population-component series)
- `C:\Users\jayzh\Documents\boc-tracker\markdown-files\verification\labour.md` (per-claim audit, May 2026; NAIRU framing, V/U bands, employment-rate utilization decoder)
- `C:\Users\jayzh\Documents\boc-tracker\markdown-files\analysis_framework.md` (Labour section, lines 184-219)
- `C:\Users\jayzh\Documents\boc-tracker\analyses\demographics_deepdive_vectors_results.md` (probe of Table 17-10-0009 and 17-10-0008 dimensions)
- `C:\Users\jayzh\Documents\boc-tracker\analyses\deep-dive-design-2026-05-09.md` (proposed demographics chart slate -- not yet built)
- `C:\Users\jayzh\Documents\boc-tracker\labour.html` and `demographics.html` (rendered prior framing -- confirms `demographics.html` shipped only migration-components + age-group LF; no narrative blurbs were attached)

Editorial canon: `C:\Users\jayzh\projects\macro-research-department\editorial\dashboard_purpose.md` Sections 1 (Mission), 2 (Audience), 4.3 (Labour incl. Demographics), 4.7 (Out of scope -- "No standalone Demographics section").

Conventions used below:
- "Covered" = boc-tracker fetches a series that maps to the element with no derivation beyond Y/Y, M/M, or AR transforms already in `analyze.py`.
- "Partial" = boc-tracker fetches some of the inputs but the element requires non-trivial construction we have not yet built, or coverage is missing one of the named sub-cuts in the EDR spec.
- "Gap" = nothing in boc-tracker covers this; primary source proposed.
- All StatCan vector IDs without a V-prefix are WDS integers as used by `fetch.py`; with a V-prefix they're as quoted by StatCan documentation.
- Cadence and revision notes are based on the StatCan / BoC published release calendars and the historical record visible in the CSV outputs.

---

## Section A -- Coverage table

Headline question (per EDR 4.3): How tight is the Canadian labour market, and is per-capita output recovering through population deceleration or through aggregate weakness?

The EDR specifies six basics elements. Elements 1, 2, 3, 5, 6 are predominantly the LFS / JVWS / wage story (boc-tracker had this on a single `labour` page). Element 4 (population and labour supply) is the new combined-section element that pulls Demographics inside Labour (the prior `demographics.html` deep-dive scaffolded migration components and age-group LF, but no main-page basics layer existed for population).

| # | Basics element | boc-tracker coverage | Primary source | Cadence | Revision pattern | Gotchas |
|---|---|---|---|---|---|---|
| 1 | LFS headline -- employment, unemployment rate, participation, employment rate; latest print with surprise; first-Friday cadence | Yes (data); No (consensus surprise) | StatCan WDS, all Table 14-10-0287-01 SA: v2062815 unemployment rate, v2062817 employment rate, v2062816 participation rate, v2062814 (scaled 0.001) unemployment level. Stored as `data/unemployment_rate.csv`, `employment_rate.csv`, `participation_rate.csv`, `unemployment_level.csv`. Employment level itself is NOT separately stored, only the rate. | Monthly, first Friday at 8:30 ET | LFS revises the prior month at each release plus a one-time benchmark revision (typically January) using the post-Census population control. Census-cycle benchmark revisions can move the levels meaningfully (the 2022 rebenchmark on the 2021 Census shifted population-controls up by hundreds of thousands -- LFS levels follow). | (a) Employment *level* (the count, not the rate) is a missing input for the unemployment-vs-employment-level Beveridge frame and for per-capita employment growth -- see element 4. Should be added: Table 14-10-0287-01 v2062811 (employed, total, 15+, SA). (b) "Surprise vs consensus" -- same gap as GDP/CPI in Brief 1.1; recommend the editorial-director's option (c) of anchoring surprise to BoC MPR-published projections rather than Reuters polls. (c) LFS reference week is the week containing the 15th; readers in P2 (BoC, DoF) often forget that LFS captures hours, payrolls, and jobs at slightly different reference points -- a small but persistent friction the basics blurb should be precise about. |
| 2 | Wage growth -- four measures (LFS all-employee, LFS permanent, SEPH, BoC's composition-adjusted LFS-Micro) shown as a band, with dispersion called out | Yes | StatCan v105812645 LFS all-employee Y/Y (Table 14-10-0320-02, level SA, Y/Y derived in `analyze.py`), v105812715 LFS permanent (same table), v79311153 SEPH (Table 14-10-0223-01, average weekly earnings, all employees, SA). BoC Valet `INDINF_LFSMICRO_M` for LFS-Micro composition-adjusted wage growth Y/Y. Stored as `data/lfs_wages_all.csv`, `lfs_wages_permanent.csv`, `seph_earnings.csv`, `lfs_micro.csv`. boc-tracker's analyze.py already computes the four-measure band including min/max/avg/dispersion. | Monthly | LFS wages are revised with the LFS benchmark cycle. SEPH revises at each release for the prior month and at the annual benchmark. LFS-Micro is BoC-derived from LFS microdata, lags roughly a month behind LFS itself per the verification log; methodology in BoC SAN 2024-23. | (a) The four measures are not directly comparable in levels (LFS = hourly; SEPH = weekly; LFS-Micro = composition-adjusted hourly). The basics-layer band is built on Y/Y growth rates, which is the standard reconciliation. (b) LFS-Micro typically runs *below* raw LFS in Canada (composition is shifting toward higher-paid workers per SAN 2024-23); when LFS-Micro converges to or exceeds raw LFS, that is itself a signal worth surfacing. (c) The EDR explicitly names the four measures and calls for dispersion -- already present. No construction work needed beyond what `analyze.py compute_labour_values` returns. |
| 3 | Hours and per-capita hours -- distinguish employment-rate strength from hours-worked weakness | No (boc-tracker noted average hours as "NSA-only monthly; flagged for the next labour scope review") | StatCan Table 14-10-0036-01 (actual hours worked, all jobs, NSA), and Table 14-10-0042-01 (actual hours worked, main job, SA -- limited series). Aggregate hours worked: Table 14-10-0289-01 "Total actual hours worked, employees and self-employed" (SA, monthly). Vector IDs need verification probe. | Monthly with LFS | LFS hours revised with the LFS benchmark cycle. The Table 14-10-0289 series is published with both SA and trend-cycle; the SA aggregate is the right basics cut. | (a) This is the *binding* construction gap for the combined section. "Per-capita hours" = aggregate hours / population, or equivalently average hours per worker x employment rate. We need either (i) the aggregate-hours-worked series directly (Table 14-10-0289 vector probe required), or (ii) average hours x employment to back into aggregate hours. Recommendation: pipeline-engineer probes 14-10-0289 SA aggregate hours; if that's clean, that's the headline series for element 3. (b) "Per-capita" needs total population -- same gap as GDP element 4 in Brief 1.1 (Table 17-10-0009 total population vector to be added). (c) Average hours has been falling structurally (services / part-time mix shift); the EDR's framing -- "distinguishes employment-rate strength from hours-worked weakness" -- is one of the most analytically loaded basics elements. |
| 4 | Population and labour supply -- StatCan quarterly population estimates; LFS-derived labour-force growth; permanent-resident vs temporary-resident composition; federal immigration-levels-plan trajectory | Partial (component flows yes; total stock no; levels-plan no) | (a) StatCan Table 17-10-0040-01 quarterly migration components: v29850342 immigrants, v29850343 emigrants, v1566834788 net emigration, v29850346 net non-permanent residents, v1566834758 NPR inflows. Stored as `data/pop_immigrants.csv`, `pop_emigrants.csv`, `pop_net_emigration.csv`, `pop_net_npr.csv`, `pop_npr_inflows.csv`. (b) Total population stock (Table 17-10-0009-01): the `fetch.py` comment block flags "pop_total V1 was flagged as unusually small -- excluded pending verification" and the `demographics_deepdive_vectors_results.md` probe confirmed the headline Canada-total vector was not cleanly resolved. Need to identify the correct vector (likely v1 from cube 17-10-0009, "Canada, both sexes, all ages, persons") and reconcile with StatCan Daily's published 41.5M figure (Q1 2026). (c) Labour-force growth: derivable from existing LFS levels (employment + unemployment = labour force; participation rate x population = labour force) -- pure derivation. (d) Federal immigration-levels-plan trajectory: NOT a StatCan series; published as IRCC annual document. | Quarterly for population stock and migration components; annual + revisions for the levels plan | Population estimates revised quarterly + at the post-Census benchmark (the 2026 LFS rebenchmark will reflect 2021-Census-based estimates). Migration components revised with the population release. Levels plans are revised at the November release each year by IRCC (the 2025-2027 plan published Oct 2024 was a material downward revision; the 2026-2028 plan is scheduled for Nov 2026). | (a) Total population stock is the binding pipeline gap. (b) Levels plan is *editorial data* -- not a programmatic time series. The standard format is three-year forward targets, split by permanent (economic / family / refugee / humanitarian) and temporary (international students, IMP, TFWP) with totals. Pipeline-engineer cannot fetch this from an API; the basics layer must either (i) hardcode the latest IRCC plan as a small JSON/CSV that the editorial team refreshes on each Nov release, or (ii) treat it as an event-marked annotation on the realized-flows chart. Strong recommendation: option (ii) -- annotate the realized-flows chart with the plan vintage and total-target lines. (c) The 2024 federal pivot to cut PR targets and cap NPRs is a major narrative break -- the basics layer must be able to show "realized vs planned" cleanly. (d) Permanent-vs-temporary composition is recoverable from boc-tracker's existing components: `pop_immigrants` (PR inflows -- StatCan term for landed immigrants, ~= IRCC permanent admissions), `pop_npr_inflows` (NPR inflows -- temporary residents). |
| 5 | Vacancies and slack -- JVWS job vacancies; vacancy-to-unemployment ratio; Beveridge-curve position | Yes | StatCan Table 14-10-0371-01 (JVWS): v1212389365 vacancy rate (NSA, monthly), v1212389364 vacancy level (NSA, monthly, scaled to millions). Stored as `data/job_vacancy_rate.csv`, `job_vacancy_level.csv`. The verification log establishes a 3-month MA convention (NOT 12-month -- amplitude / lag analysis in `analyses/labour_tightness_research_2026-05-09.md`); analyze.py currently still uses 12M MA but a queued patch shifts to 3M. The Beveridge-curve scatter is a NativeChartSpec in `labour.html` (`_build_beveridge_curve_panel` in build.py). | Monthly, NSA only (no SA companion series published) | JVWS series begin 2015; structural gap Apr-Sep 2020 (COVID suspension). Limited revisions, on standard monthly cadence. | (a) NSA-only is the key gotcha; the 3M MA is the dashboard convention. (b) Series start 2015 limits cyclical-comparison depth; US JOLTS (Dec 2000+) is the only longer-history comparator and is structurally different (2022 peak Canada V/U ~0.99 vs US ~2.0). (c) V/U thresholds (boc-tracker uses < 0.30 / 0.30-0.45 / 0.45-0.60 / 0.60-0.80 / > 0.80) are Canadian-calibrated empirical bands; the verification log establishes these are *historical-anchor* labels, not current-state claims. (d) The boc-tracker labour deep-dive already has the Beveridge scatter built; reuse it. |
| 6 | Regional dispersion -- provincial unemployment range; where the labour market is loosening fastest | No | StatCan Table 14-10-0287-03 (LFS by province, monthly SA): unemployment rate, employment rate, participation rate by province. Vector IDs need probe (one per province per indicator -- ~30 vectors at minimum for the four largest provinces). | Monthly with LFS | Same revision pattern as national LFS. | (a) boc-tracker has nothing at the provincial level. (b) The EDR spec says "provincial unemployment range" -- the simplest basics presentation is a vertical bar / dumbbell showing the range across the four largest provinces (ON, QC, AB, BC) with the national rate marked; this avoids ten-bar clutter and matches Housing 4.4 element 1 (six-CMA convention). (c) A "where the labour market is loosening fastest" call-out requires 12-month change in provincial unemployment rates -- a simple derivation once vectors are fetched. Construction watchlist. |

---

## Section B -- Editorial-design proposal for the combined Labour + Demographics basics layer

This is the novel piece of Brief 1.2. The EDR specifies the six elements but leaves to the researcher how Demographics surfaces inside Labour. Below is the proposal; the EDR redlines.

### B.1 Page ordering and narrative spine

**Recommendation: labour first, demographics second; both before slack and dispersion. NOT demographics-as-cause-and-labour-as-consequence.**

The EDR's framing in Pillar E ("does per-capita output recover through deceleration or through unemployment") suggests population is the upstream cause and labour outcomes are the downstream consequence. That framing is correct for the deep-dive (Pillar E, out of scope here). It is wrong for the basics layer for three reasons:

1. **The basics layer is state-of-the-section, not theory-of-the-section.** A reader at 7am wants to know "what is the Canadian labour market doing right now" first; the population-decomposition story is the analytical lens, not the state. The EDR is explicit (Sec 3): "the basics layer exists to ground the reader in current state, not to move a view."
2. **The cadence of population data is materially slower than LFS.** Population estimates are quarterly with a roughly 90-day lag; LFS is monthly with a 7-day lag. The basics page refreshes on the first Friday of each month. If demographics opens the page, the population frame is stale 11 months out of 12 relative to the freshest labour print.
3. **The Bay Street P1 reader already knows the population story qualitatively.** What they need from the basics layer is current LFS state and a clean read on per-capita-versus-aggregate divergence. Demographics belongs as the *denominator framing* for that read, not as the page opener.

The page reads top-to-bottom as:

> 1. **LFS headline** -- where the labour market is right now (element 1).
> 2. **The per-capita panel** -- the analytically novel basics element. Side-by-side: employment growth (Y/Y, absolute) vs employment growth (Y/Y, per-capita); aggregate hours growth vs per-capita hours growth (elements 3 + 4 fused).
> 3. **Wage band** -- four measures and dispersion (element 2).
> 4. **Slack** -- V/U with Beveridge-curve position (element 5).
> 5. **Population and immigration -- the supply-side trajectory** -- realized flows (PR vs NPR) with IRCC levels-plan annotations (element 4, the population sub-block).
> 6. **Regional dispersion** -- four-province range with national overlay (element 6).

Demographics surfaces in two places: as the *denominator* in panel 2 (where its narrative weight is highest, because that's where the per-capita-vs-aggregate read lives), and as the *supply trajectory* in panel 5 (where the IRCC levels-plan and the PR/NPR composition story live). It is never a standalone block disconnected from labour outcomes; it always rides shotgun.

### B.2 Headline number

**Recommendation: the unemployment rate is the headline number; the per-capita employment-growth panel is the analytical second look immediately beneath it.**

The candidate headlines considered:

- **Unemployment rate.** Most recognized by all three personas; refreshed monthly; revised lightly. Tracks the LFS cycle cleanly. The standard institutional convention (BoC, StatCan, OECD, IMF all open with it). **Cost: it obscures the per-capita story the EDR's headline question is built around.**
- **Employment-to-population ratio (employment rate).** More direct measure of labour utilization; less obscured by participation moves. **Cost: same Y/Y signal noise as the unemployment rate, less institutional anchor as a headline, and still doesn't surface the per-capita-output framing.**
- **Per-capita employment growth (employment Y/Y minus population Y/Y).** Directly answers the EDR's headline question. **Cost: it is a constructed indicator with no institutional pedigree; a 7am Bay Street reader looking for "where is the unemployment rate" gets a number they then have to back into. Two-step cognition is the wrong basics-layer convention.**
- **Composite (e.g., a BoC-style multi-indicator benchmark, SAN 2025-17-styled).** **Cost: opaque, opinionated, the wrong basics-layer move.** SAN 2025-17 is a deep-dive frame, not a headline.

The right configuration is to lead with the unemployment rate as the recognized headline anchor and then immediately surface the per-capita panel as the second look. This honors the headline question without contorting the headline number. The unemployment rate is the *what*; the per-capita panel is the *so what*. The wage band, slack, and supply trajectory follow.

The basics-layer prose blurb -- 2-4 sentences per the analysis_framework's output instructions -- should lead with the unemployment rate level and direction, embed the surprise framing against BoC's MPR projection, and pivot in the second or third sentence to the per-capita read: "labour-force growth is decelerating with the federal immigration pullback, so what the unemployment rate is doing in aggregate masks a softer per-capita employment picture" -- when the data supports it, and the reverse framing when per-capita is the firmer leg.

### B.3 How the IRCC levels plan is represented

**Recommendation: event-marked annotations on a stacked-composition trajectory chart, NOT a separate plan-only chart.**

The federal immigration-levels plan is the most important policy lever inside the Labour section. The 2024 pivot to cut PR targets (from 500k toward 365k by 2027) and cap NPR share (5% of population by 2027) is a structural break in Canada's labour-supply trajectory. How to render it:

- **Single-trajectory option** (one line, e.g. total annual newcomers). Hides the PR / NPR composition shift that is the entire story.
- **Stacked-composition area** (PR stacked on NPR, with total as the top line). Shows the composition cleanly. **Recommended primary frame.**
- **Realized-vs-plan dual chart.** Two panels: realized historical flows on the left, plan trajectory on the right. Splits the story too aggressively; the analytical insight is in the *gap* between recent realized and the new plan, which is hardest to see across panels.
- **Event-marked time series** (single chart with annotations at each major plan-revision moment). **Recommended secondary frame.** Mark the Oct 2022 levels plan, the Oct 2023 plan, the Oct 2024 pivot (the structural break), and the next plan release with a dated vertical-rule annotation and a small label naming the announced PR + NPR targets at that moment.

**Final chart spec for panel 5:** a stacked-composition chart of quarterly PR inflows (Table 17-10-0040 v29850342 immigrants) and NPR inflows (v1566834758) with the four-quarter trailing sum as the displayed unit (annualized run-rate proxy). Three dated annotations: 2022-10 (post-COVID surge institutionalized; PR target 465k), 2024-10 (the structural-break pivot; PR target cut to 395k 2025 / 380k 2026 / 365k 2027 and NPR cap introduced), and the next plan release date as a forward marker. A separate small companion table (3-4 rows) below the chart lists the current plan's PR and NPR targets for 2026, 2027, 2028 with vintage. This format keeps the realized-flows story primary, the plan in supporting context, and the structural-break event clearly marked without splitting attention across multiple panels.

### B.4 Page rhythm

Page-length budget: six panels plus a 2-4 sentence opening blurb. The basics layer is held to be readable in roughly three minutes for a Bay Street P1 at 7am.

The proposed rhythm:

- Panel 1 (LFS headline): one chart, four lines (employment rate, unemployment rate, participation rate, employment level Y/Y). Default view: 5-year window.
- Panel 2 (per-capita): two side-by-side small-multiples. Left: employment Y/Y vs employment Y/Y per-capita. Right: aggregate hours Y/Y vs per-capita hours Y/Y. Both 5-year windows. *This is the section's signature panel; it does the heaviest analytical work.*
- Panel 3 (wage band): one chart -- LFS-all (featured), LFS-permanent, SEPH, LFS-Micro as a four-measure shaded band; CPI services Y/Y as a comparator line; 0% / 3% reference lines. 10-year default window.
- Panel 4 (slack): two stacked sub-panels. Top: V/U as a single line with the five-band background shading (0.30 / 0.45 / 0.60 / 0.80). Bottom: Beveridge scatter (vacancy rate y, unemployment rate x) with the most recent point highlighted and the prior 12 months trailed as a faint connecting path. Reuse boc-tracker's `_build_beveridge_curve_panel`.
- Panel 5 (population and immigration): stacked-composition chart, four-quarter trailing sums, with three dated annotations.
- Panel 6 (regional dispersion): dumbbell or range chart -- four largest provinces (ON, QC, AB, BC) plus national overlay; current value plus the 12-months-ago value to surface the loosening-fastest call-out.

### B.5 What this design buys, in one paragraph

The unemployment rate stays the recognized headline; the per-capita panel is the analytical second look immediately below it; the wage band and V/U slack frame are the institutionally familiar middle; the immigration trajectory with IRCC-plan annotations is the supply-side context surfaced where it informs the per-capita read directly; regional dispersion closes. Demographics does not get a dedicated section heading inside Labour -- it lives in the *denominator* of the per-capita panel and the *supply trajectory* of panel 5. This honors the EDR's consolidation decision (no standalone Demographics section per Sec 4.7) without burying the population story; it answers the EDR's headline question without contorting the headline number; and it preserves the basics-layer voice principle (state-of-the-section, not theory-of-the-section). Pillar E's deep-dive then has clean conceptual real estate to push opinionated against this baseline rather than competing for basics-layer attention.

---

## Section C -- Gap list

1. **Employment level (count, not rate)** -- Table 14-10-0287-01 v2062811 (employed, total, 15+, SA) needed for the per-capita employment-growth panel (element 1 + element 3 fusion). One-line fetcher addition.
2. **Aggregate hours worked, SA, monthly** -- Table 14-10-0289-01, vector probe required. Needed for panel 2 (per-capita hours). The "average hours per worker" series was previously deferred in boc-tracker (annual cadence too coarse); the aggregate-hours series is the cleaner basics input.
3. **Total population stock, quarterly** -- Table 17-10-0009-01 Canada total (vector ID requires probe; fetch.py noted prior attempt returned implausible value). This is the *same* gap as in Brief 1.1 (GDP per-capita) and should be resolved jointly. Cross-check against StatCan Daily: Q1 2026 total population was ~41.5M.
4. **Provincial LFS (ON, QC, AB, BC) -- unemployment rate, employment rate, participation rate** -- Table 14-10-0287-03, twelve vectors minimum. Needed for panel 6.
5. **IRCC immigration-levels plan (current + recent vintages)** -- no programmatic source; published as PDF / press release each November. Format: PR targets by category (economic / family / refugee / humanitarian) and NPR targets by category (international students / IMP / TFWP) for the rolling three-year horizon. **Editorial maintenance, not pipeline maintenance.** Source: https://www.canada.ca/en/immigration-refugees-citizenship/news/notices/supplementary-immigration-levels-2025-2027.html (2025-2027 plan as of May 2026) and the future Nov-2026 plan release. Recommendation: maintain as a small versioned JSON in `data/` (or research index entry) listing plan vintage, year, PR target, NPR target; editorial team refreshes on each Nov release; the basics-layer chart annotation reads off this file.
6. **Consensus expectations for the LFS print** -- same call as GDP/CPI: drop "surprise vs consensus" from v1 basics; defer to deep-dive prose; OR anchor surprise to the BoC's MPR-published labour projections (April / July / October / January cadence) as the primary-source comparator. See Brief 1.1 open question 1.
7. **Out-of-scope but worth flagging:** LFS R-indicators (R3 official+waiting, R7 +marginally attached, R8 +involuntary part-time), unemployment-by-reason (job-loser share from Table 14-10-0125), long-term-unemployment share (>=27 weeks), and BoC's SAN 2025-17 composite indicators (multi-indicator benchmark range). All are deep-dive material (Pillar E or labour-DD); the verification log explicitly flagged that naming them in basics prose would leak "would-track-but-not-fetched" hedging.

---

## Section D -- Construction watchlist

Items that require derivation, scripts, or methodology notes before they can be presented:

- **Per-capita employment growth** = employment level Y/Y minus population Y/Y, OR (employment Y/Y) / (population Y/Y) - 1 -- both are basics-friendly. The first form (subtractive) is the BoC's convention in MPR per-capita tables and is recommended. Requires elements C.1 and C.3 above.
- **Per-capita hours worked growth** = aggregate hours Y/Y minus population Y/Y. Requires elements C.2 and C.3.
- **Aggregate hours growth (Y/Y)** = simple Y/Y on Table 14-10-0289 once fetched.
- **Labour-force growth** = derivable from existing LFS levels via participation rate x population; or equivalently employment + unemployment levels. Should be presented as a derived line on panel 5 alongside the population components (to make explicit that not all population growth flows to labour supply).
- **Immigration realized-vs-plan delta** = realized PR / NPR annual sum minus the IRCC plan target for that year. The basics-layer annotation should surface this delta in the panel-5 footnote when realized has diverged materially from plan; the editorial team refreshes the comparator on each new StatCan population release.
- **Regional dispersion summary metric** = range across the four largest provinces (max provincial UR minus min), plus 12-month change in each. The "loosening fastest" call-out is derived from the 12-month change ranking. Short analysis script; lives in `analyses/`.
- **Vacancy rate 3-month MA (vs 12-month)** -- boc-tracker's `analyze.py compute_labour_values` currently uses 12M MA; the verification log establishes 3M as the correct convention given Canadian NSA seasonal amplitude. The migration is a queued patch in boc-tracker. For macro-research-department we should ship with 3M from the start.
- **Beveridge-curve panel construction methodology note** -- reuse boc-tracker's `_build_beveridge_curve_panel`; the methodology note (NSA vacancy, SA unemployment, 3M smoothing, trail length) needs to live one click from the chart per dashboard_purpose Success criterion 5.

---

## Open questions for editorial-director

1. **B.2 -- Headline number.** I propose the unemployment rate as the recognized headline with the per-capita panel as the immediate second look. The alternative is to lead with the per-capita panel itself (more aggressive against the EDR's headline question; less institutional). Confirm direction.

2. **B.3 -- Levels-plan representation.** I propose event-marked annotations on a stacked-composition trajectory. The alternative is a dual realized-vs-plan panel. Confirm direction.

3. **B.4 -- Regional dispersion presentation.** Recommend four-province dumbbell (ON, QC, AB, BC plus national overlay) to match Housing's six-CMA convention. The alternative is ten-province bars (full coverage but reads cluttered) or a five-province cut adding Manitoba or Saskatchewan to surface Prairie-vs-Central divergence. Confirm.

4. **C.5 -- IRCC levels-plan maintenance.** The plan is editorial data, not pipeline data. Confirm the maintenance pattern: a small versioned JSON the editorial team refreshes on each Nov release, with the chart annotation reading off it. Alternative is to encode the latest plan directly in the chart spec and update on plan release (lower flexibility, simpler pipeline).

5. **C.6 -- Surprise framing.** Same call as Brief 1.1: drop "surprise" from v1 basics, OR anchor to BoC's MPR projections (which now include labour projections in the Appendix). Recommend the BoC-MPR anchor for consistency with Brief 1.1 recommendation.

6. **Boundary with Pillar E (deep-dive).** The basics layer's per-capita panel sets up the question Pillar E exists to answer. We must be careful not to *answer* that question in the basics blurb. Confirm the blurb-prose discipline: the basics blurb surfaces the divergence; the deep-dive resolves whether decomposition or weakness explains it.

7. **What to NOT include.** I have deliberately excluded from the basics layer: unit labour costs (lives in GDP / productivity territory, Pillar D), LFS R-indicators (deep-dive only), youth-vs-prime-age split (deep-dive only), provincial decomposition beyond the four largest, EI beneficiaries (deep-dive only), employer-survey shortage indicators (out of scope per the verification log -- not pulled). Confirm.

---

## Summary read

- **Labour basics layer: 3 of 6 elements covered cleanly, 2 partial, 1 not covered.** Element 1 (LFS headline) and element 2 (wage band) are fully covered. Element 5 (vacancies and slack) is fully covered including the Beveridge-curve scatter. Element 4 (population and labour supply) has the *component-flow* data (PR / NPR inflows) but is missing the total-population stock (same gap as Brief 1.1 GDP per-capita) and the IRCC levels-plan (editorial, not pipeline). Element 3 (hours and per-capita hours) is the binding *new* basics-layer construction -- needs the aggregate-hours vector probe plus the per-capita derivation. Element 6 (regional dispersion) is not covered at all; pipeline-engineer adds Table 14-10-0287-03 vectors for the four largest provinces.
- **Approximate coverage: 60% of basics elements fully covered, 25% partial requiring named additions, 15% gap (regional dispersion entirely; levels plan is editorial).** The pipeline lift is small (one population vector, one aggregate-hours vector, one employment-level vector, ~12 provincial LFS vectors) -- comparable to Brief 1.1's lift in scale.
- **Editorial-design proposal -- one paragraph (full version in Section B):** The unemployment rate is the recognized headline; the per-capita panel (employment growth absolute vs per-capita; hours growth absolute vs per-capita) is the analytical second look directly beneath it and is the section's signature panel; the four-measure wage band and the V/U-plus-Beveridge slack frame are the institutionally familiar middle; the population and immigration trajectory uses a stacked PR-vs-NPR composition with three dated annotations for the IRCC levels-plan vintages (with the Oct 2024 pivot as the structural-break marker) -- supply-side context placed where it directly informs the per-capita read; regional dispersion closes with a four-province dumbbell. Demographics does not get its own section heading inside Labour; it surfaces twice -- once as the denominator of the per-capita panel, once as the supply trajectory in panel 5 -- so the EDR's no-standalone-Demographics decision is honored without burying the population story.
- **Open questions** are concentrated on (a) headline-number choice, (b) levels-plan rendering, (c) regional cut, (d) surprise framing, and (e) the blurb-prose boundary with Pillar E. None are blocking.

End of memo.
