# Chart editorial-quality audit -- Tier-3, all sections

Author: art-director. Date: 2026-05-11. Status: PROPOSAL (per memory:
audit outputs are recommendations, not commits; user vetoes the Top 10
list per-item before chart-builder implements).

This is NOT a canon-compliance audit. The canon audit passed clean (44/44
wrappers around `PanelLiveChart` / `PanelEmpty`). This is the EDITORIAL
audit: does each chart use the right shape for its data, does it answer
the section's headline question, and does it sit at the visual register
of the publication? An allocator at OTPP / CPPIB scans the page before
8am; if a chart reads as dashboard filler, it is.

Scoring lens:
- **KEEP** -- the chart shape fits the data, answers the headline
  question, sits at register. May still benefit from a hand-tuned
  annotation later, but the editorial bones are right.
- **IMPROVE** -- the chart is structurally correct but underwired: a
  series exists in the pipeline that would sharpen the editorial read
  and the wrapper is not asking for it. Most often: secondary series
  that should be primary, multi-CMA / multi-province set that already
  sits on disk but ships as one line, derived transform that should be
  ordered from backend.
- **REPLACE** -- the chart shape is wrong for the data + argument. A
  line for a categorical 6-province distribution. A level for a
  flow-vs-flow comparison. A continuous time series for a snapshot.

The two GATED-empty panels (Inflation 6, Trade 4) and the four
PanelEmpty placeholders (Markets 3 / 5 / 6, Trade 6) are scored
separately and are not candidates for visual improvement in this wave;
they need backend data first.

---

## GDP -- headline question: "Is the Canadian economy at potential, growing, or contracting?"

### Panel 1 -- gdp/Panel1HeadlineGDP.astro
**What it shows now.** Monthly GDP level + quarterly GDP level (both
indexed-trillions of chained CAD), 60mo window.
**Score: REPLACE.** The headline question is about *growth rates*, not
levels. A reader staring at a smoothly-rising level line cannot tell
whether Canada is at potential, growing, or contracting -- the editorial
argument is invisible in the shape. Per editorial canon 4.1 element 1
the chart wants "m/m % bars + Q/Q SAAR line." Pipeline emits the level
series; the m/m and Q/Q-SAAR transforms need to land in the JSON, or
the panel can compute them inline. **Without growth-rate transforms,
the section's hero chart fails to answer the section's headline
question.** Field to drive: derive `mom_pct` and `qoq_saar` from
`gdp_monthly` / `gdp_quarterly` level series.

### Panel 2 -- gdp/Panel2IndustryVsExpenditure.astro
**What it shows.** Industry GDP level + expenditure GDP level, two
lines overlaid (they trace each other nearly perfectly because they
ARE the same thing measured two ways).
**Score: REPLACE.** Two near-identical level lines do not tell the
reader anything about where the cuts agree and where they diverge. The
editorial argument is the *gap* between the two cuts (the statistical
discrepancy). Render the *difference* (industry minus expenditure as a
% of GDP) as a single line oscillating around zero. Field to drive:
compute `(gdp_industry - gdp_expenditure) / gdp_expenditure` as a new
series; this is a clean editorial read on reconciliation noise that a
P1 allocator actually scans. As-is the panel is decoratively present
but informationally empty.

### Panel 3 -- gdp/Panel3Contributions.astro
**What it shows.** Single line of "total contribution to Q/Q SAAR
growth" (which is just GDP growth restated as a line) OR a PanelEmpty
hatch when total-contrib is absent.
**Score: REPLACE.** Editorial canon explicitly calls for a six-bar
divergent decomposition (consumption / government / GFCF / inventories
/ exports / imports). A single line that re-traces GDP growth tells
the reader nothing about contributions. This is the canon's Q9
("categorical bar charts need a PanelBarChart"). Until that companion
component ships, the honest move is PanelEmpty with a "decomposition
gated on per-component pipeline" reason. Currently sometimes renders
as a line, which is wrong. Field to drive: per-component contributions
(consumption_contrib, govt_contrib, gfcf_contrib, inventories_contrib,
exports_contrib, imports_contrib) -- not yet emitted.

### Panel 4 -- gdp/Panel4PerCapita.astro
**What it shows.** Real GDP quarterly level (trillions) + population
proxy (persons in millions of immigrants). Two unrelated levels
overlaid; the per-capita arithmetic is not happening in the chart.
**Score: REPLACE.** This is the signature deep-dive question (Pillar
E). A two-level overlay where neither axis IS per-capita misses the
editorial point entirely. The chart should render `gdp_quarterly /
population_total` as a single Y/Y % line, with the headline real-GDP
Y/Y as a dashed secondary -- the divergence between aggregate growth
(flattering) and per-capita growth (flat-to-negative for 8+ consecutive
quarters) is THE editorial argument of the section. Field to drive:
derive `gdp_per_capita_yoy`.

### Panel 5 -- gdp/Panel5OutputGap.astro
**What it shows.** Quarterly real GDP level (chained trillions).
**Score: REPLACE.** Canon calls for the BoC's `INDINF_OUTGAPMPR_Q`
output-gap series as primary (a % oscillating around zero -- the
canonical "are we at potential" chart with a zero-line reference rule).
Rendering raw GDP level instead is a category miss: the GDP level
contains no signal about the gap to potential. Until the BoC series
lands, the honest fallback is capacity utilization (already on disk as
`capacity_util_total`, %) with a zero-deviation-from-trend frame.
Field to drive: `output_gap_mpr` from BoC Valet, or fallback
`capacity_util_total` rendered as deviation-from-80%-mean.

### Panel 6 -- gdp/Panel6RecessionState.astro
**What it shows.** Business-sector productivity per hour, Y/Y.
**Score: REPLACE.** Productivity is not a recession-state proxy. The
panel's editorial argument is the C.D. Howe BCC recession-state strip
(categorical state: expansion / recession / recovery). A productivity
line in this slot misleads the reader about what they're looking at.
Until BCC data is wired, the honest move is PanelEmpty. If the slot
must render something, the closest substantive substitute is
Wright-Quah / 2-quarter-real-GDP-contraction strip computed from
`gdp_quarterly` (categorical: contracting / expanding) -- not
productivity. Field to drive: derive `recession_state` categorical
from existing GDP quarterly series, OR PanelEmpty.

---

## Inflation -- headline question: "Is the 2% target being met, and on what measures and what breadth?"

### Panel 1 -- inflation/Panel1HeadlineCPI.astro
**What it shows.** Headline CPI Y/Y line, 60mo, 2% target dashed
reference rule. Single canon-correct primary.
**Score: KEEP.** This is the cleanest panel in the publication. Line
shape is correct for a continuous Y/Y measure. Reference rule at 2%
makes the editorial argument visible in the shape (every visit of the
line relative to the rule). One light fix to consider later: an
annotation pinning the most recent print's distance from target (Phase
2 hand-tuned callout). Otherwise as-is.

### Panel 2 -- inflation/Panel2CoreTrio.astro
**What it shows.** Core-trim Y/Y solid + Core-median Y/Y dashed
secondary. 2% reference rule.
**Score: KEEP.** Both series share units (%) and frame, the secondary
dash convention is canon, the 2% rule anchors the editorial argument.
The "trio" filename is mildly misleading (Common is suppressed by
editorial decision in canon 4.2 element 2; only two lines render) but
the chart is honest. Could be IMPROVE'd later by adding a Manrope
annotation flagging "third month inside 1-3% band" once the writer
brief lands. Not a top-10 item.

### Panel 3 -- inflation/Panel3Breadth.astro
**What it shows.** PanelEmpty (the share-of-basket >3% derivation is
not on disk).
**Score: GATED.** Empty state is correct -- the editorial argument is
a 3-band stacked area (>3% / 1-3% / <1%), which needs a
`PanelAreaChart` companion or bespoke implementation AND the basket-
weighted derivation. Not in this wave. Field to drive: derive
`cpi_share_above_3pct`, `cpi_share_target`, `cpi_share_below_1pct`
from `cpi_components`.

### Panel 4 -- inflation/Panel4SubAggregates.astro
**What it shows.** Shelter CPI Y/Y as a single line + 2% reference
rule.
**Score: REPLACE.** Editorial canon calls for a *ranked horizontal
bar chart of sub-aggregate Y/Y* (shelter / services-ex-shelter / goods
ex-energy / food / energy). A single shelter line obscures the cross-
sectional read on which components are running hot vs target. This is
the second-most-load-bearing chart in inflation after headline -- a
P1 allocator wants to see at a glance "where in the basket is the
heat." Field to drive: per-aggregate Y/Y series (`cpi_shelter_yoy`
exists; need `cpi_services_yoy`, `cpi_goods_yoy`, `cpi_food_yoy`,
`cpi_energy_yoy`). Then ranked bar chart. Gated on PanelBarChart
companion landing.

### Panel 5 -- inflation/Panel5Expectations.astro
**What it shows.** CSCE consumer 1y solid + 5y dashed. Both Y/Y %,
2% reference rule.
**Score: KEEP.** Correct shape (two continuous expectation series),
correct canon treatment (solid/dashed), correct reference rule. BOS
firms-expecting->3% toggle is deferred per canon -- acceptable. Could
be improved with annotation flagging "5y at 2% for X consecutive
prints" once writer drafts.

### Panel 6 -- inflation/Panel6PassThrough.astro
**What it shows.** PanelEmpty (gated on basket-weighted ex-aggregate
CPI derivations).
**Score: GATED.** Correct stance -- bespoke side-by-side strip-chart
needed, gated on 4 derivations. Not in this wave.

---

## Labour -- headline question: "How tight is the labour market, and is per-capita output recovering?"

### Panel 1 -- labour/Panel1LFSHeadline.astro
**What it shows.** Unemployment rate solid + employment rate dashed.
Both %, share an axis.
**Score: KEEP.** Two correctly-paired indicators in canon-compliant
treatment. Could be IMPROVE'd with a dashed reference rule at 6.0%
(rough mid-cycle u-rate) but that's a writer decision. The chart
shape is right.

### Panel 2 -- labour/Panel2PerCapita.astro
**What it shows.** Unemployment level (millions of persons) + aggregate
hours (thousands of hours). Two raw level series with no per-capita
arithmetic happening on the canvas.
**Score: REPLACE.** This is the labour section's signature chart per
editorial canon 4.3 -- it's WHERE the headline question resolves. The
chart should be a small-multiple pair: (employment Y/Y vs employment
per-capita Y/Y) and (aggregate hours Y/Y vs per-capita hours Y/Y). As
shipped it surfaces two raw levels that say nothing about the per-
capita divergence. Field to drive: derive `employment_yoy`,
`employment_per_capita_yoy`, `agg_hours_yoy`, `per_capita_hours_yoy`.
Until then, a single line of `aggregate_hours_yoy` is a better stand-
in than raw level. **This is one of the top-10 fixes -- a chart that
ought to carry the section's editorial argument carrying instead two
unrelated levels.**

### Panel 3 -- labour/Panel3WageBand.astro
**What it shows.** LFS-all CAD/hour + LFS-permanent CAD/hour, two
nearly-identical level lines.
**Score: IMPROVE.** The pipeline has FOUR wage series available
(`lfs_wages_all`, `lfs_wages_permanent`, `seph_earnings`, `lfs_micro`)
plus `cpi_services_yoy` as the real-wage anchor -- the canonical "wage
band" composition. The wrapper asks for two only. Either (a) compute
Y/Y on all four and render as a band (min/max ribbon + median line) per
the canon 4.3 element 3 "wage band" frame, or (b) at minimum render
LFS-Micro (the BoC-preferred composition-adjusted series) as primary
with services CPI Y/Y as the comparator dashed line. Field to drive:
derive `wage_yoy_min`, `wage_yoy_max`, `wage_yoy_median` across the
four wage series; or just promote `lfs_micro` to primary. The current
"two indistinguishable lines" treatment is dashboard filler.

### Panel 4 -- labour/Panel4VacanciesSlack.astro
**What it shows.** Job vacancy rate (%) + vacancy level (millions of
persons). Units mismatch -- live chart suppresses the level line, ships
as single-series vacancy rate.
**Score: IMPROVE.** Pipeline emits `job_vacancy_rate` AND
`unemployment_rate` (already on disk under panel-4's tertiary). The
canonical editorial chart is the V/U ratio (vacancies / unemployment),
which would render cleanly as a single line oscillating around
historical norm. As shipped, the chart is a vacancy-rate-only line,
which doesn't answer the "tightness" question -- tightness is V/U, not
V alone. Field to drive: derive `vacancy_to_unemployment_ratio` from
the two existing series.

### Panel 5 -- labour/Panel5IRCCSupplyTrajectory.astro
**What it shows.** PR inflows (persons, quarterly) + Net NPR (persons,
quarterly). Two flow series in same units.
**Score: KEEP.** Shape is right (two flow series, same units). The
big-bang structural-break-October-2024 IRCC policy reversal is
naturally visible in the Net NPR series. Could be IMPROVE'd with a
hand-tuned annotation pin at Oct 2024 with the policy-change anchor
word, and with the IRCC levels-plan-target overlay -- both deferred
per panel comments. Not a top-10 item but a strong candidate for
Phase 2 annotation work.

### Panel 6 -- labour/Panel6RegionalDumbbell.astro
**What it shows.** Ontario u-rate + Quebec u-rate, both as continuous
time-series lines.
**Score: REPLACE.** This is the most editorially-wrong chart in the
publication. The wrapper filename literally says "Dumbbell" -- the
canonical chart is a horizontal dumbbell across ON / QC / AB / BC with
the national rate, comparing current vs 12-months-ago to surface the
"loosening fastest" call-out. Rendering two continuous lines instead:
(a) doesn't permit cross-sectional read, (b) doesn't show the
12-month delta, (c) misses 50% of the data on disk (AB + BC + national
ARE in panel-6 JSON; the wrapper just doesn't ask for them). Field to
drive: all five series (`lfs_on_unemployment_rate`,
`lfs_qc_unemployment_rate`, `lfs_ab_unemployment_rate`,
`lfs_bc_unemployment_rate`, `lfs_ca_unemployment_rate`) -- they're
already on disk. Gated on a `PanelDumbbellChart` companion component;
the data is ready, the chart-type isn't built. Highest-priority
REPLACE in the audit.

### Panel 7 -- labour/Panel7EIBeneficiaries.astro
**What it shows.** EI regular beneficiaries (persons) as a single
line, 60mo.
**Score: KEEP.** Right shape for a single continuous demand-side
mirror series. Note that the unit "Persons" reads at scale 1.4M-1.7M
on the y-axis, which is fine in canon. Could be IMPROVE'd with Y/Y
transform toggle per the panel comment, but the level series carries
the editorial argument (inflection point) directly. Acceptable as-is.

---

## Housing -- headline question: "Is the rate-sensitive sector amplifying or dampening policy?"

### Panel 1 -- housing/Panel1Prices.astro
**What it shows.** National MLS HPI Y/Y, single line.
**Score: IMPROVE.** All SIX CMAs (Toronto, Vancouver, Montreal,
Calgary, Ottawa, Edmonton) are on disk in panel-1 JSON. The wrapper
asks for the national line only. The editorial canon (4.4 element 1)
specifically calls out "national plus six CMAs" -- because the
dispersion across CMAs IS the story (Toronto / Vancouver leading the
drift while Calgary / Edmonton hold). A single national line averages
the geographic story away. Field to drive: the six CMA Y/Y series
already in panel-1.extras; render as a small-multiple grid OR as a
fan of pure-ink lines with two named (T/V) anchored and the others
faded to 30% opacity. Either is a top-10 fix -- the data is on the
shelf, the chart is asking for less than it could.

### Panel 2 -- housing/Panel2Activity.astro
**What it shows.** Housing starts SAAR (units) + under-construction
(units, thousands). Units mismatch suppresses the secondary line, so
in practice this renders as a single starts line.
**Score: IMPROVE.** Pipeline emits `housing_starts` AND
`residential_permits` (panel-2 tertiary; CAD thousands). Permits are
the leading indicator on starts and that's the editorial argument --
canon 4.4 element 2 names permits as the lead. Editorial value: render
permits as primary (the lead) + starts as dashed secondary (the lag),
with attention on the gap. Alternatively keep starts as primary and
add the 3mma overlay (smoothing) which is more conservative. Either
is more editorial than the current "single line of starts."

### Panel 3 -- housing/Panel3Inventory.astro
**What it shows.** SNLR (%) + resales index (different units, so
secondary is suppressed). Renders as SNLR single line.
**Score: KEEP.** SNLR is the canonical "buyer's vs seller's market"
balance indicator and a single line tells the story (above 0.65 =
seller's market, below 0.40 = buyer's market). Could be IMPROVE'd by
adding TWO reference rules (the 0.40 and 0.65 thresholds) since SNLR
is a regime-classifier indicator -- those reference rules would
visibly anchor the editorial read. Worth flagging but low-priority.

### Panel 4 -- housing/Panel4Rent.astro
**What it shows.** CPI rent Y/Y + CPI rented accommodation Y/Y. Both
%, same axis.
**Score: KEEP.** Two related Y/Y % rent measures, correctly paired.
The slight divergence between the two measures (one captures owners-
equivalent, one captures actual rented stock) is editorially
interesting. Acceptable as-is.

### Panel 5 -- housing/Panel5MortgageStack.astro
**What it shows.** 5yr conventional mortgage rate, single line.
**Score: IMPROVE.** Editorial canon 4.4 element 5 names a secondary:
"5Y mortgage rate / 5Y GoC spread as the marginal-borrower cost-of-
borrowing read." Pipeline emits `mortgage_rate_5yr` and Markets
section has `yield_5yr` -- but the spread derivation isn't shipped.
The 5y mortgage rate alone is not THE editorial argument; the SPREAD
to the 5y GoC is the policy-transmission read (it widens when banks
hold underwriting margin against deteriorating credit). Field to
drive: derive `mortgage_5y_goc_spread = mortgage_rate_5yr -
yield_5yr`, render alongside the level. Not gating the chart shape;
adding the editorial second layer.

### Panel 6 -- housing/Panel6PopulationStock.astro
**What it shows.** PR inflows (persons) single line. Secondary is
suppressed (units mismatch with starts).
**Score: REPLACE.** "Immigrant inflows" is not the
"population-to-housing-stock ratio" the canon calls for. The chart in
its current form is a duplicate of Labour Panel 5 (same PR inflow
series). The editorial argument is the RATIO of population (numerator)
to housing stock (denominator) by CMA -- a supply-response indicator.
The denominator is not on disk; the canon-stamped fix is PanelEmpty
with a "stock denominator gated on StatCan 36-10-0688" reason. As
shipped the panel is a copy of Labour's immigration line, which is
editorially confusing on a Housing page. Field to drive: housing
stock per CMA, then ratio.

### Panel 7 -- housing/Panel7Affordability.astro
**What it shows.** BoC housing affordability index, quarterly, 1981
onward (windowMonths=600).
**Score: KEEP.** The 50-year window is exactly right for an
affordability index -- a P1 allocator wants the 1989-91 spike and
2007-08 spike as historical anchors for the 2022-24 peak. Strong
chart, correctly framed. Could be IMPROVE'd with the three shaded
tightening-episode bands (1989-91 / 2007-08 / 2022-24) per panel
comment when researcher supplies dates.

---

## Policy -- headline question: "What is the policy stance, and is it consistent with the cycle?"

### Panel 1 -- policy/Panel1OvernightRate.astro
**What it shows.** Overnight rate monthly (primary) + daily overnight
rate (secondary). Same series sampled at two cadences.
**Score: IMPROVE.** Two cuts of THE SAME SERIES is editorially empty
-- monthly and daily of the policy rate are functionally identical.
The canon-named secondary toggles are (a) peer central bank rates
(ECB / BoE / RBA / Fed) and (b) real policy rate (overnight minus CPI
Y/Y). At minimum render peer-Fed rate as a dashed secondary -- that
overlay carries the BoC-Fed divergence story directly. Pipeline has
`overnight_rate` and Policy panel-3 has US 2y; ideally we'd want
fed-funds-target. Field to drive: source `fed_funds_target` (FRED
DFEDTAR or similar) and overlay as dashed secondary. Otherwise the
chart is a wasted hero slot.

### Panel 2 -- policy/Panel2MarketPath.astro
**What it shows.** 2y GoC (primary) + overnight rate (secondary).
Both %, correctly paired.
**Score: KEEP.** This IS the canonical "market path vs policy" frame
-- 2y yield as the term-structure read on expectations sitting above
or below the spot policy rate tells the reader where the curve sees
the BoC going. Correctly canon-paired. Could be hand-tuned with an
annotation at the latest 2y-O/N gap.

### Panel 3 -- policy/Panel3BoCFedSpread.astro
**What it shows.** 2y Canada solid + 2y US dashed. Both daily %.
**Score: REPLACE.** Canon 4.5 element 3 names the editorial argument:
"current level, distribution context (P50/P80/P95/P99 from 35+ years),
regime classification." The chart that answers this is the SPREAD
itself (Canada minus US, single line crossing zero), with historical
percentile reference rules. Two parallel yield lines obscure the
spread; the reader has to do the arithmetic visually. Field to drive:
derive `boc_fed_2y_spread = yield_2yr_ca - us_2yr`, render as single
line with zero-line reference rule. **This is Pillar B deep-dive
territory and the section's editorial hook -- it needs to land
sharply.**

### Panel 4 -- policy/Panel4BalanceSheet.astro
**What it shows.** Settlement balances + total assets, both CAD
billions, weekly.
**Score: KEEP.** Two related balance-sheet components in same units,
canon-paired. The settlement-balances-vs-assets visual carries the QT
phase story (assets running off, settlement balances declining). Could
be IMPROVE'd with the CORRA-vs-target secondary toggle per canon (data
is on disk: `corra_overnight_spread_bps` in panel-4 extras) -- but
unit mismatch (bps vs CAD billions) makes it a true view-switch, not
an overlay. Defer to Phase 2.

### Panel 5 -- policy/Panel5FederalTrajectory.astro
**What it shows.** Monthly fiscal balance (primary, CAD millions) +
YTD fiscal balance (secondary, CAD millions). Same units.
**Score: KEEP.** Two views of the same fiscal trajectory (monthly
print + YTD cumulative), correctly paired. The monthly is noisy and
the YTD smooths it -- both are editorially defensible reads. Could be
IMPROVE'd by promoting YTD as primary (it's the read the writer
actually anchors on in the blurb) and monthly as dashed secondary.
Minor.

### Panel 6 -- policy/Panel6FiscalStanceCycle.astro
**What it shows.** Capacity utilization (%, quarterly), single line.
**Score: REPLACE.** The chart is labeled "fiscal stance vs cycle" but
shows ONLY the cycle proxy (capacity util) with no fiscal-stance
counterpart -- the editorial argument (does fiscal lean WITH or
AGAINST the cycle?) is invisible. Canon names IMF CAPB as the fiscal
read; Sibley does not construct CAPB and the IMF series is annual.
Honest fix: render capacity utilization as the cycle proxy AND the
DoF fiscal YTD as a normalized secondary (z-scored on its own
history), so the reader can SEE whether fiscal direction agrees with
or fights the cycle. Field to drive: `capacity_util_total` (have) +
`dof_fiscal_ytd_balance` (have) -- both already on disk, need
inline z-score normalization in the wrapper or backend.

---

## Markets -- headline question: "What external winds are pushing on Canadian inflation, growth, and the CAD?"

### Panel 1 -- markets/Panel1CAD.astro
**What it shows.** USDCAD spot (primary) + USDCAD BoC (secondary).
Same series from two sources (FRED + BoC).
**Score: REPLACE.** Same-series-twice is editorially empty. Canon 4.6
element 1 names: "USDCAD level + BoC nominal effective index (CEER) +
USDCAD percentile classifier (P50/P80/P95/P99 since 1990) as stress
classification." Minimum fix: render USDCAD with horizontal reference
rules at P80 / P95 (e.g. 1.40 / 1.45) to surface the stress regime
visually. Stretch fix: add CEER as a dashed secondary to show whether
USDCAD weakness is USD-strength or CAD-weakness. Field to drive: CEER
(`boc_ceer` not on disk yet -- request); percentile bands derived
from `usdcad` history.

### Panel 2 -- markets/Panel2GoCCurve.astro
**What it shows.** 2y GoC (primary) + 5y GoC (secondary). Daily %.
**Score: IMPROVE.** Pipeline emits 2y / 5y / 10y / 30y. The wrapper
asks for 2 of 4. Editorial argument is the curve shape -- 2s10s
inversion specifically. Either render all four with weight-and-dash
discipline (a clean fan), or compute and render the 2s10s spread as a
single line with zero-line reference rule (cleaner editorial: tells
the reader directly whether curve is inverted). The 2s10s frame is
the canonical recession-prelude indicator a P1 allocator scans. Field
to drive: derive `goc_2s10s = yield_10yr - yield_2yr`. Strong top-10
candidate.

### Panel 3 -- markets/Panel3CreditSpreads.astro
**Score: GATED.** PanelEmpty until US IG/HY OAS lands. Correct.

### Panel 4 -- markets/Panel4Energy.astro
**What it shows.** WTI (primary) + Brent (secondary). Both USD/bbl,
daily.
**Score: KEEP.** Two related oil benchmarks in same units. Standard
energy chart. Could be IMPROVE'd with WCS as monthly dashed third
series (canon 4.6 element 4 calls for it; `wcs` is on disk in panel-4
tertiary at monthly cadence). The WTI-Brent spread doesn't drive
Canada much; the WTI-WCS spread is the editorially-relevant one for
oil sands realizations. But canon explicitly cautions against
"daily-comparison differential." Acceptable as-is; WCS overlay is a
stretch improvement.

### Panel 5 -- markets/Panel5BankStability.astro
**Score: GATED.** PanelEmpty until Big-Six PCL / CET1 data lands.
Correct.

### Panel 6 -- markets/Panel6FCI.astro
**Score: GATED.** PanelEmpty until FCI composite lands. Correct.

---

## Trade -- headline question: "Is Canada's external position structurally shifting under US repricing?"

### Panel 1 -- trade/Panel1TradeBalance.astro
**What it shows.** Trade balance (primary) + 3mma (secondary). Both
CAD millions.
**Score: KEEP.** Monthly + 3mma of the same series is the canonical
"raw print + smoothing" frame; correct for a noisy monthly trade
series. Zero-line crossing is the editorial argument and reads
clearly. Acceptable.

### Panel 2 -- trade/Panel2CurrentAccount.astro
**What it shows.** Monthly trade balance (primary) + quarterly
goods+income (secondary). Different cadences.
**Score: REPLACE.** Editorial argument is current-account
decomposition (goods + services + primary income + secondary income).
Pipeline has all four sub-balances on disk: `ca_goods_balance_q`,
`ca_services_balance_q`, `ca_primary_income_q`, `ca_secondary_income_q`
plus `current_account_balance` headline. As shipped, the chart shows
monthly merch trade (which is panel-1's job) instead of the quarterly
CA decomposition. Field to drive: render `current_account_balance` as
primary + goods balance as dashed secondary (or stacked-area
decomposition once a `PanelAreaChart` companion lands). Currently the
panel is duplicative of Panel 1.

### Panel 3 -- trade/Panel3PartnerShares.astro
**What it shows.** Total exports (CAD millions) + exports to US (CAD
millions). Both levels.
**Score: REPLACE.** Editorial canon 4.7 element 3 names "the
structural-shift narrative is the rolling US share trajectory."
Showing two LEVELS doesn't show the share. The reader cannot eyeball
"US share is at 66% and falling" from two parallel rising level lines.
Field to drive: derive `us_share_of_exports = trade_exports_us /
trade_exports_total`, render as single % line. This is THE chart for
the section's headline question (structural shift under US repricing).
Top-10 fix.

### Panel 4 -- trade/Panel4TariffState.astro
**Score: GATED.** PanelEmpty (editorial table, not a series).
Correct.

### Panel 5 -- trade/Panel5TermsOfTrade.astro
**What it shows.** WTI + Brent (USD/barrel) as proxies for terms of
trade.
**Score: IMPROVE.** Pipeline emits `terms_of_trade` (the actual
StatCan index, 2017=100, quarterly) and `terms_of_trade_yoy` (Y/Y %)
in panel-5 JSON. The wrapper asks for WTI / Brent (the proxies). Use
the actual series. Render `terms_of_trade` (primary) with `wti`
overlay (dashed secondary) as the higher-frequency leading line per
canon. Field to drive: `terms_of_trade` -- already on disk, wrapper
just doesn't ask for it. Quick win.

### Panel 6 -- trade/Panel6FDIBySector.astro
**Score: GATED.** PanelEmpty until FDI series lands. Correct.

---

## Score totals

- **KEEP:** 14 (Inflation 1, 2, 5; Labour 1, 5, 7; Housing 3, 4, 7;
  Policy 2, 4, 5; Markets 4; Trade 1)
- **IMPROVE:** 9 (Labour 3, 4; Housing 1, 2, 5; Policy 1; Markets 1,
  2; Trade 5)
- **REPLACE:** 14 (GDP 1, 2, 3, 4, 5, 6; Inflation 4; Labour 2, 6;
  Housing 6; Policy 3, 6; Trade 2, 3)
- **GATED-empty (correct, not in this wave):** 7 (Inflation 3, 6;
  Markets 3, 5, 6; Trade 4, 6)

The 14 REPLACE flags are concentrated in GDP (all six are flagged --
the section is the weakest in the publication editorially because the
pipeline emits levels and the canon wants growth-rate / contribution /
gap derivations that haven't been derived yet). GDP is the section
that most needs a backend wave.

---

## Top 10 charts to fix tonight (prioritized)

Ordered by editorial impact times ease of fix. Each is a concrete
chart-builder brief with the data field that drives it.

### 1. Labour Panel 6 -- the section's regional-dispersion chart, currently 2 lines, should be 4-province dumbbell
Filename: `src/components/charts/labour/Panel6RegionalDumbbell.astro`.
**Editorial impact:** highest single-chart impact in the audit. The
filename literally says "Dumbbell" and the data for all four provinces
+ national rate is on disk under `panel-6` (primary `lfs_on_*`,
secondary `lfs_qc_*`, tertiary `lfs_ab_*`, extras `lfs_bc_*`,
`lfs_ca_*`). The current 2-line render answers nothing the headline
question asks. **Brief:** build `PanelDumbbellChart.astro` companion
(horizontal dumbbell: 4 rows ON / QC / AB / BC, x-axis u-rate %, two
markers per row -- current vs 12-months-ago, connector line between,
national rate as a vertical reference rule). Canon ink + MTA red
treatment per `canon_reference_panel.md` rules 1-3.

### 2. Trade Panel 3 -- US partner share, currently 2 levels, should be 1 share line
Filename: `src/components/charts/trade/Panel3PartnerShares.astro`.
**Editorial impact:** THE chart for the section's headline question
("structurally shifting under US repricing"). The structural shift is
literally invisible in the current chart. **Brief:** wrapper should
expose `data.primary.data` as a *derived* series:
`{date, value: trade_exports_us / trade_exports_total * 100}` per
month. Single % line with a y-axis around 60-80%. Pin the historical
norm (75-80% pre-2020) with a dashed reference rule. The post-2020
drift below 70% then becomes the visual editorial argument.

### 3. GDP Panel 1 -- headline GDP, currently levels, should be growth rates
Filename: `src/components/charts/gdp/Panel1HeadlineGDP.astro`.
**Editorial impact:** the section's hero chart fails to answer the
section's headline question. **Brief:** derive `mom_pct =
(gdp_monthly[t] / gdp_monthly[t-1] - 1) * 100` inline in the wrapper
and pass as `primary`; derive `qoq_saar = ((gdp_quarterly[t] /
gdp_quarterly[t-1])^4 - 1) * 100` as `secondary`. Single zero-line
reference rule. The recession band overlay (March-May 2020) is
visible in the resulting m/m series and carries the editorial argument
about the cycle directly. This is the section's hero -- if it lands,
the rest of GDP follows.

### 4. Housing Panel 1 -- HPI national, currently 1 line, should be 6 CMAs
Filename: `src/components/charts/housing/Panel1Prices.astro`.
**Editorial impact:** canon explicitly names "national plus six CMAs"
and ALL SIX CMAs are on disk in panel-1 extras
(`crea_hpi_toronto_yoy`, ..._vancouver, ..._montreal, ..._calgary,
..._ottawa, ..._edmonton). The dispersion is the story (T/V negative,
Calgary positive). **Brief:** render national line as solid pure-ink
primary + 6 CMA lines as 1px pure-ink at 30% opacity, with two named
direct labels (Toronto + Vancouver -- the load-bearing pair on the
downside). MTA red dot on the latest national print. Zero-line
reference rule.

### 5. Policy Panel 3 -- BoC-Fed spread, currently 2 yield lines, should be spread line
Filename: `src/components/charts/policy/Panel3BoCFedSpread.astro`.
**Editorial impact:** Pillar B deep-dive's section anchor. Two
parallel yield lines obscure the spread. **Brief:** derive
`boc_fed_2y_spread[t] = yield_2yr_ca[t] - us_2yr[t]` (align by date,
forward-fill where needed). Render as single line with zero-line at
strong-opacity ink. Reference rules at +50 / -50 bps as
distribution-context anchors (canon names P50/P80/P95/P99 -- defer
formal percentiles to Phase 2; the +/-50 bps anchors capture the rough
regime).

### 6. Markets Panel 2 -- GoC curve, currently 2 lines, should be 2s10s spread
Filename: `src/components/charts/markets/Panel2GoCCurve.astro`.
**Editorial impact:** 2s10s inversion is the canonical recession-
prelude indicator a P1 allocator scans daily. Pipeline has all four
tenors on disk. **Brief:** derive `goc_2s10s[t] = yield_10yr[t] -
yield_2yr[t]`. Render as single line with prominent zero-line. Window
60 months. Recession band over 2020Q1-Q2 visible. The inversion of
2022-2024 becomes the dominant visual feature and answers the section
question directly.

### 7. Inflation Panel 4 -- shelter only, should be ranked sub-aggregate bar
Filename: `src/components/charts/inflation/Panel4SubAggregates.astro`.
**Editorial impact:** the second-most-load-bearing chart in inflation
(after headline). Reader wants "where in the basket is the heat" at a
glance. **Brief:** requires `PanelBarChart` companion (per canon Q9).
For tonight, the cheaper fix is to broaden the line render: keep
`cpi_shelter_yoy` as primary, add the dominant sub-component as
dashed secondary -- BUT this is a stretch given units. Better: route
to PanelEmpty with "ranked bar gated on PanelBarChart + 4
sub-aggregate Y/Y derivations" reason, until the bar component lands.
Recommend GATED fallback rather than half-fix. Add to the
PanelBarChart Phase 2 spec.

### 8. Trade Panel 5 -- terms of trade, currently WTI/Brent proxies, should be actual ToT
Filename: `src/components/charts/trade/Panel5TermsOfTrade.astro`.
**Editorial impact:** quick honesty win. The actual StatCan ToT index
is on disk under panel-5 (`terms_of_trade`, Index 2017=100,
quarterly). Currently we ship oil proxies and the editorial title
makes a promise the chart doesn't keep. **Brief:** swap primary from
WTI to `terms_of_trade`, swap secondary from Brent to
`terms_of_trade_yoy` OR `wti` (BoC's BCPI as the high-frequency
leading line if/when it's wired). One-line change in the wrapper:
the data is right there.

### 9. Labour Panel 2 -- per-capita signature chart, currently 2 raw levels, should show per-capita Y/Y
Filename: `src/components/charts/labour/Panel2PerCapita.astro`.
**Editorial impact:** signature chart of the section per canon 4.3.
The per-capita-vs-aggregate divergence is the labour-market editorial
argument for 2025-26 (population deceleration vs cyclical weakness --
Pillar E deep-dive). Currently two raw levels with no per-capita
arithmetic. **Brief:** derive `agg_hours_yoy` from existing
`aggregate_hours` (Y/Y on raw level), render as primary single line.
Stretch: derive `per_capita_hours_yoy = aggregate_hours / population`
Y/Y as dashed secondary -- requires aligning monthly hours with
quarterly population (forward-fill or simple monthly interpolation).
Even the primary-only fix (Y/Y of hours) is a clean editorial line.

### 10. GDP Panel 4 -- per-capita GDP, currently 2 raw levels, should be per-capita Y/Y
Filename: `src/components/charts/gdp/Panel4PerCapita.astro`.
**Editorial impact:** Pillar D deep-dive's anchor chart. The
flattering-headline-vs-soft-per-capita divergence is the call. **Brief:**
derive `gdp_per_capita_yoy = (gdp_quarterly / population) y/y`. Render
as primary; render headline `gdp_quarterly_yoy` as dashed secondary
for divergence visibility. Zero-line reference rule. The 8+
consecutive negative-prints record on the per-capita series becomes
the visual argument. Even without secondary, the per-capita Y/Y line
alone is a strong upgrade on two unrelated levels.

---

## Notes on the Top 10 ordering

Items 1, 4, 6, 7 are gated on companion components or chart-type
extensions (PanelDumbbellChart, multi-series fan render with named
direct labels on a subset, 2s10s spread axis with reference rules,
PanelBarChart). Items 2, 3, 5, 8, 9, 10 are derive-and-render fixes
that the current wrapper architecture can handle (the wrapper can do
the per-date arithmetic before passing primary/secondary to
PanelLiveChart).

If the chart-builder agent has bandwidth for only the wrapper-level
fixes tonight: do 2, 3, 5, 8, 9, 10. Items 1, 4, 6, 7 want a
follow-on wave with the companion components built first.

If the agent does ALL ten in this wave, the section pages will read
notably sharper -- in particular, GDP, Trade, and Labour will move
from "honest about its limits" to "answers the section question."

End of audit.
