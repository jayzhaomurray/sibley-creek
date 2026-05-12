# Wave 5: boc-tracker Chart Coverage Decisions

Editorial-director decisions on the researcher's chart-by-chart inventory
(`research/boc_tracker_chart_inventory.md`). User directive: coverage
parity with boc-tracker (every indicator boc-tracker carries should also
appear on Sibley Creek), not visual replication. Vignelli canon stays.

Author: editorial-director. 2026-05-11.

---

## 1. Executive summary

Of the five new-panel candidates, three are canonized for v1 (EI Regular
Beneficiaries as a new Labour Panel 7, Housing Affordability as a new
Housing Panel 7, CORRA-vs-target as a fold into Policy Panel 4); two are
demoted to folds inside existing panels (Capacity Utilization as a
secondary track on GDP Panel 5 Output Gap; CMA-level Resale Activity as
a toggle on Housing Panel 2 Activity). Eight folds are canonized; four
methodology calls are resolved. Two specialist briefs go out for
chart-builder (the two genuinely new panels), one to backend (EI display
transform; affordability vintage handling), zero to art-director (the
component library and Vignelli canon already cover what these need).

The discipline: section structure stays at six to eight panels; we add
two genuinely new panels (Labour: 6 -> 7; Housing: 6 -> 7) and absorb
everything else into existing canon. The two adds are both central
for cycle calls a P1 reader makes: EI for the cyclical inflection in
labour, affordability for the mortgage-cost transmission in housing.

---

## 2. New-panel decisions (Section A)

### A.1 EI Regular Beneficiaries (Labour)

**Decision: canon now. New Panel 7 in Section 4.3 Labour.**

- **Section:** Labour. The series is the cleanest demand-side mirror of
  vacancy decline and is genuinely missing from the current six-panel
  canon. Pillar served: E (population deceleration vs labour). The
  leading-recession-indicator framing also touches GDP and Policy
  (monetary), but EI's home is Labour.
- **Why a new panel rather than a fold:** EI uptake is a stock series
  with its own level / Y/Y / MoM transforms and its own analytical job
  (cyclical inflection signal that fires before LFS unemployment turns).
  Folding into Panel 4 (Vacancies and slack) would crowd the V/U /
  Beveridge content that already does a different job. The two panels
  are complementary -- vacancies are the supply-side read, EI is the
  demand-side read -- and they belong adjacent, not merged.
- **Data:** `data/raw/ei_regular_beneficiaries.csv` present.
- **Panel scope:** Single-series with level (in thousands) / Y/Y / MoM
  toggle. National only in v1; provincial breakdown defers to deep-dive.
  Annotation: peak-to-trough call-out on the most recent cycle.
- **Cadence:** Monthly, ~80-day lag (StatCan Table 14-10-0011-01).
- **Voice posture:** Mode 2 blurb on each EI release flags the
  divergence (or convergence) between EI uptake and the LFS print that
  preceded it.

### A.2 Housing Affordability (Housing)

**Decision: canon now. New Panel 7 in Section 4.4 Housing.**

- **Section:** Housing. The BoC qualifying-mortgage-payment-to-income
  index is the cleanest summary of "what does carrying a mortgage cost
  right now." Pillar served: A (mortgage renewal wall) and C (housing
  cycle and supply response).
- **Why a new panel rather than a fold:** Panel 5 (Mortgage stack
  snapshot) is a snapshot of the existing book (vintage / term
  composition + arrears); affordability is the flow read for new
  borrowers. The two answer different questions; Panel 5 is "what is the
  stock paying" and affordability is "what would a new borrower pay
  against current income." Folding affordability into Panel 5 would
  blur both.
- **Data:** `data/raw/housing_affordability.csv` present.
- **Panel scope:** Single-series quarterly with the long history visible
  (BoC publishes from 1981). Annotation overlays: tightening / easing
  episodes (1989-1991, 2007-2008, 2022-2024) called out as historical
  anchors -- not current-state claims.
- **Cadence:** Quarterly (BoC Indicators of capacity and inflation
  pressures release).
- **Voice posture:** Mode 2 blurb on quarterly release notes direction
  and the dominant driver (rate move / price move / income move).

### A.3 CORRA vs Overnight Rate spread (Policy / Monetary)

**Decision: canon now as fold into Panel 4 Balance Sheet (not standalone).**

- **Why a fold, not a new panel:** Settlement balances and CORRA
  dispersion are two sides of the same plumbing read. Panel 4 already
  carries the "phase QE / reinvestment / passive QT / floor maintenance"
  framing; CORRA-vs-target is the diagnostic that confirms or falsifies
  the floor-maintenance call. Surfacing them on the same panel is
  analytically correct and keeps Policy at eight panels.
- **Panel 4 scope after the fold:** Panel 4 becomes a two-view panel:
  default view is settlement balances + asset composition (the current
  spec); secondary view (toggle) is CORRA-target spread (20-day
  smoothing, daily series, last 2 years). Both views serve the same
  reader question: is the BoC's chosen floor regime functioning?
- **Data:** `data/raw/corra_daily.csv` and
  `data/raw/overnight_rate_daily.csv` (or `overnight_rate_target.csv`)
  present.
- **Cadence:** Daily refresh on the spread view; weekly refresh on the
  balance-sheet view stays as is.

### A.4 CMA-level Resale Activity (Housing)

**Decision: fold into Panel 2 Activity as a CMA toggle. Not a new panel.**

- **Why a fold:** Panel 2 already carries starts / permits / completions
  -- the activity slate. CMA-level resales (Toronto / Vancouver /
  Calgary) is the same analytical job at a more granular geography. A
  CMA toggle on Panel 2 inherits the right contextual neighbours
  (national starts, permits) without inflating the panel count.
- **Panel 2 scope after the fold:** Default view stays as national
  starts (3mma) + permits + completions. Secondary view (toggle):
  CMA-level resales (TO / VA / CG) at 12M rolling. Methodology note:
  resales are flow not stock; not directly comparable to starts.
- **Data:** `data/raw/crea_resales_toronto.csv`, `_vancouver.csv`,
  `_calgary.csv` present.
- **Trade-off accepted:** CMA-level coverage gets a secondary surface,
  not a hero panel. A P1 reader wanting Toronto resale momentum can
  reach it on Panel 2's toggle; a deeper CMA cut belongs in the housing
  deep-dive (Pillar C).

### A.5 Capacity Utilization (GDP or Labour)

**Decision: fold into GDP Panel 5 Output Gap as a secondary track.
Not a new panel.**

- **Why a fold and why GDP not Labour:** Capacity utilization is a
  slack-side read; it competes for the same analytical job as
  output-gap-from-potential. Surfacing them together on Panel 5 lets a
  reader cross-check the two slack measures directly. Labour's
  Panel 4 (V/U + Beveridge) is doing a different job (worker-side slack);
  capacity utilization is the firm-side complement to potential output,
  which is GDP territory.
- **Panel 5 scope after the fold:** Default view stays as output gap
  (BoC MPR series; see C.1 below). Secondary view (toggle): industrial
  capacity utilization, total + manufacturing, quarterly. Both panels
  are slack measures; the toggle name should make that explicit.
- **Data:** `data/raw/capacity_util_total.csv`,
  `data/raw/capacity_util_mfg.csv` present.
- **Editorial weight:** Moderate. Capacity utilization is more useful
  when manufacturing is the binding constraint; the toggle treatment
  matches its second-tier-but-not-skippable status.

### Cuts and deferrals

- **GDP productivity decomposition (boc-tracker gdp #3 stub).**
  **Skip at basics.** Routes to Pillar D (productivity gap) deep-dive.
- **LFS R-indicators (boc-tracker labour #3 stub).** **Skip at basics.**
  U3 is the canon headline (Section 4.3). R7/R8 expansions defer to
  any future labour-slack deep-dive.
- **Indeed Job Postings (boc-tracker labour #8 stub).** **Skip at
  basics.** JVWS is canon primary; Indeed's value depends on JVWS lag
  becoming an editorial pain point we do not yet feel.
- **CPI 60-component decomposition (boc-tracker inflation #3 stub).**
  **Skip at basics.** Panel 4 SubAggregates carries the aggregate cuts;
  the 60-component view is methodology-page territory.
- **Mortgage Renewal Payment Shock (boc-tracker housing #6).** **Defer.**
  This is a stylized reproduction of a BoC chart for Pillar A. Carry as
  cited static chart inside the Pillar A deep-dive when that ships;
  do not surface at basics layer.

---

## 3. Folds canonized (Section B)

Table of boc-tracker chart concepts that don't get a standalone panel
but extend an existing Sibley panel.

| boc-tracker chart | Sibley panel | Treatment | Refactor? |
|---|---|---|---|
| Output gap (HP-filter) | GDP Panel 5 OutputGap | Methodology swap: use BoC MPR `INDINF_OUTGAPMPR_Q`, not HP-filter; capacity utilization added as secondary toggle | Backend data swap; chart-builder: add toggle |
| Monthly GDP + industry overlays | GDP Panel 2 IndustryVsExpenditure | Adopt the boc-tracker industry-overlay toggle pattern (goods / services / mfg / mining-oil) | Chart-builder: extend toggle set |
| Headline CPI ex-indirect-taxes overlay | Inflation Panel 1 HeadlineCPI | Add ex-indirect-taxes as toggle when StatCan series wired (see C.4) | Phase 2 — gated on data availability |
| BOS distribution buckets | Inflation Panel 5 Expectations | Add as secondary view (toggle) alongside the CSCE consumer 1y/5y default | Chart-builder: add BOS series + toggle |
| Unemployment by age (youth + prime) | Labour Panel 1 LFSHeadline | Add youth and prime-age unemployment as secondary toggle on Panel 1 | Chart-builder: add toggle |
| Prime-age and Youth triplets (participation + employment + unemployment) | Labour Panel 2 PerCapita | Add prime-age and youth triplets as toggles on Panel 2 (denominator-adjusted slack views) | Chart-builder: add toggle; backend has all six series |
| Unit Labour Costs | Labour Panel 3 WageBand | Add ULC as secondary overlay (productivity-adjusted wage read) | Chart-builder: add overlay toggle |
| 5Y mortgage rate vs 5Y GoC + spread | Housing Panel 5 MortgageStack | Add the marginal-borrower cost-of-borrowing series as secondary element on Panel 5 | Chart-builder: extend panel props |
| Peer central bank rates (ECB / BoE / RBA) | Policy Panel 1 OvernightRate | Add as secondary toggle on Panel 1 (default stays BoC + neutral band) | Chart-builder: add multi-line toggle |
| Real policy rate (overnight minus headline CPI) | Policy Panel 1 OvernightRate | Add as secondary transform toggle on Panel 1 | Chart-builder: add transform toggle |
| CORRA vs target spread | Policy Panel 4 BalanceSheet | Add as secondary view (toggle) — settlement balances default, CORRA spread secondary | Chart-builder: add view toggle |
| CMA-level resales (TO/VA/CG) | Housing Panel 2 Activity | Add as secondary CMA-toggle view | Chart-builder: add CMA toggle |
| Capacity utilization (total + mfg) | GDP Panel 5 OutputGap | Add as secondary slack-measure toggle | Chart-builder: add toggle |
| 2Y-10Y yield curve spread | Markets Panel 2 GoCCurve | Surface as transform toggle on Panel 2 (already in scope per canon) | Chart-builder: add toggle if not present |

Net refactor load: chart-builder touches eight panels with toggle or
overlay extensions. Backend touches three panels with new-data wiring
(EI, affordability, CORRA spread derivation). Existing panel structure
holds.

---

## 4. Methodology resolutions (Section C)

### C.1 GDP output gap (Panel 5): BoC MPR series, not HP-filter

**Resolution: Canon stays at BoC MPR `INDINF_OUTGAPMPR_Q` as the
primary series. HP-filter is not the Sibley methodology.**

- Sibley canon was already specified this way in Section 4.1 unit 5;
  this resolution confirms it against the inventory's flagged ambiguity.
- **Fallback handling:** If a BoC MPR cycle does not refresh the output
  gap series on its usual cadence (the BoC sometimes lags), the panel
  shows the last-published BoC estimate with a stale-vintage badge and
  the date of the most recent BoC publication. We do not substitute
  our own HP-filter; we surface the staleness instead. Voice posture:
  "the BoC has not refreshed the output gap since [date]" is a finished
  observation.
- **Implementation note for backend:** Confirm `INDINF_OUTGAPMPR_Q` is
  in pipeline fetch. If not, add to backend wave list.

### C.2 WTI-WCS differential cadence (Markets Panel 4 Energy): monthly

**Resolution: Canon is monthly cadence. Daily differential is not
surfaced.**

- Section 4.6 unit 4 already cautions against the daily differential
  ("noisy, false signals"). This resolution makes the call explicit
  against the inventory's flag.
- **WCS series:** Monthly published cadence. Daily WTI / Brent stay as
  primary lines on Panel 4 with 20-day smoothing per existing canon;
  WCS joins at monthly cadence.
- **Implementation note:** boc-tracker's daily differential treatment
  is not adopted. The interaction between high-frequency WTI and
  monthly WCS belongs in chart-builder's handling of mixed-cadence
  series.

### C.3 BOS distribution buckets (Inflation Panel 5 Expectations)

**Resolution: BOS distribution buckets are added as a secondary view
(toggle) on Panel 5, not a separate panel.**

- Section 4.2 unit 5 already lists "BOS firms expecting >3% as
  primary; BOS distribution buckets as the secondary view." The
  current Panel 5 implementation reportedly covers only the CSCE
  consumer 1y/5y; BOS coverage needs to be added.
- **Panel 5 scope clarified:**
  - Default view: CSCE consumer 1y + 5y (current canon).
  - Toggle 1: BOS firms expecting >3% (single line, the headline
    business expectations measure).
  - Toggle 2: BOS distribution buckets (below 1% / 1-2% / 2-3% /
    above 3%) as four-line stack summing to ~100%.
- **Data:** `bos_dist_*` and `infl_exp_above3` CSVs present.

### C.4 CPI ex-indirect-taxes toggle (Inflation Panel 1)

**Resolution: Add as a toggle on Panel 1, Phase 2 -- gated on the
StatCan series being wired into the pipeline.**

- boc-tracker shipped this as a stub (series not wired); Sibley
  inherits the same gating.
- **Editorial rationale for keeping it in scope at all:** GST/HST
  rate changes and tariff pass-through both move headline CPI through
  the indirect-taxes channel; the ex-indirect-taxes overlay is the
  cleanest way to separate the price-level signal from the tax-policy
  noise. P1 readers will ask for this every time a federal or
  provincial sales-tax adjustment lands.
- **Implementation note:** Backend needs to add the StatCan CPI ex-
  indirect-taxes series (Table 18-10-0004-13 vector v41693242 is the
  likely candidate; researcher to confirm vector). When wired,
  chart-builder adds as toggle on Panel 1.

---

## 5. Per-specialist briefs

### chart-builder (2 briefs — one per new panel)

#### Brief 1: Labour Panel 7 EI Beneficiaries

> New chartbook unit. Section: Labour. Position: Panel 7 (appended
> after Panel 6 Regional Dumbbell). Subject: EI Regular Beneficiaries.
> Series: `ei_regular_beneficiaries.csv` (StatCan Table 14-10-0011-01,
> national, monthly).
>
> Panel type: single-series line chart with transform toggle. Default
> transform: level in thousands (divide raw value by 1000; raw is in
> persons). Alternates: Y/Y percent change; MoM percent change.
>
> Visual canon: Vignelli — uniform tile size matching existing Labour
> panels, no per-chart visual exceptions. Default window: 10 years.
> Annotation: peak-to-trough call-out for the most recent cycle
> (researcher will supply the trough date and value when content
> ships; ship the chart without the annotation if the dating is
> ambiguous at build time).
>
> Interpretation paragraph: writer drafts. Voice: Mode 2 blurb on the
> release; style-editor polishes. Editorial scope of the headline:
> name the direction of EI uptake and whether it confirms or diverges
> from the most recent LFS print.
>
> Cadence: monthly, ~80-day lag. Auto-blurb regenerates on each EI
> release.

#### Brief 2: Housing Panel 7 Affordability

> New chartbook unit. Section: Housing. Position: Panel 7 (appended
> after Panel 6 PopulationToHousingStock). Subject: Housing
> Affordability index. Series: `housing_affordability.csv` (BoC
> qualifying-mortgage-payment-to-income ratio).
>
> Panel type: single-series line chart, quarterly. Default window:
> max range (1981 onward). No transform toggle in v1 — the index
> already is the transformation.
>
> Visual canon: Vignelli — uniform tile size matching existing Housing
> panels. Annotation: shaded bands for historical tightening episodes
> (1989-1991, 2007-2008, 2022-2024) as static reference overlays, not
> current-state classifiers. Researcher will supply exact band start /
> end dates with the brief content.
>
> Interpretation paragraph: writer drafts. Voice: Mode 2 blurb on the
> quarterly release; style-editor polishes. Editorial scope of the
> headline: name the direction and the dominant driver (rate move /
> price move / income move).
>
> Cadence: quarterly (BoC Indicators of capacity and inflation
> pressures release).

#### Folds (no new panels; existing panels gain toggles / overlays)

chart-builder also receives a fold-list (extracted from Section 3
above) to refactor existing panels. These are not separate briefs but
a backlog item: GDP Panel 5 gains capacity-utilization toggle; GDP
Panel 2 gains industry-overlay toggle; Inflation Panel 5 gains BOS
toggles; Labour Panel 1 gains youth/prime-age toggles; Labour Panel 2
gains prime/youth triplet toggles; Labour Panel 3 gains ULC overlay;
Housing Panel 2 gains CMA toggle; Housing Panel 5 gains 5Y mortgage
rate / GoC spread element; Policy Panel 1 gains peer-bank toggle and
real-rate transform; Policy Panel 4 gains CORRA spread toggle.
Sequencing across these folds is coordinator-owned.

### backend (1 brief — covering data prep for the two new panels and
the methodology resolutions)

> Three small wiring items for Wave 5.
>
> 1. **EI Regular Beneficiaries display transform.** Series
>    `ei_regular_beneficiaries.csv` is in persons. Panel 7 Labour
>    consumes a derived `ei_regular_beneficiaries_k` series (raw / 1000)
>    for default display. Y/Y and MoM transforms are standard;
>    chart-builder handles those.
>
> 2. **Housing Affordability vintage handling.** Series
>    `housing_affordability.csv` is quarterly with occasional BoC
>    revisions. Wire vintage stamp into the meta JSON so the panel can
>    surface a "last refreshed [date]" footer; standard pattern.
>
> 3. **CORRA-target spread derived series.** Add a derived series
>    `corra_target_spread = corra_daily - overnight_rate_target` (or
>    against `overnight_rate_daily` if cleaner; researcher confirms which
>    BoC series is the appropriate target leg). Daily cadence; 20-day
>    rolling smoothing applied at panel layer, not at backend.
>
> 4. **GDP output gap series.** Confirm BoC Valet
>    `INDINF_OUTGAPMPR_Q` is in pipeline fetch for GDP Panel 5. If not,
>    add. Methodology resolution C.1 commits to BoC MPR as the
>    canonical output-gap series (not HP-filter).
>
> 5. **CPI ex-indirect-taxes (Phase 2).** Not Wave 5. Note for the
>    backlog: a future wave adds the StatCan ex-indirect-taxes CPI
>    series for Panel 1's overlay toggle. Researcher to identify
>    canonical vector first.

### art-director (no brief this wave)

> No new visual spec needed. Both new panels (Labour Panel 7 EI,
> Housing Panel 7 Affordability) are single-series line charts that
> reuse existing Vignelli-canon panel templates already in the
> component library. Toggle and overlay extensions on the eight
> refactored panels also use existing patterns. Art-director input
> would be required only if a new visual primitive (e.g. dumbbell, phase
> scatter) were being introduced; none is.

### researcher (no separate brief — known follow-ups)

> Three small confirmations for the work above. Not blocking the briefs
> above; can run in parallel.
>
> 1. Confirm the BoC Valet key for `INDINF_OUTGAPMPR_Q` is current
>    (Wave 5 backend item 4).
> 2. Identify the canonical StatCan vector for CPI ex-indirect-taxes
>    (Wave 5 backend item 5, Phase 2).
> 3. Supply peak-to-trough dating for the EI Beneficiaries annotation
>    (chart-builder brief 1) and historical-tightening band dates for
>    Housing Affordability (chart-builder brief 2).

### writer / style-editor (downstream — not yet)

> Two interpretation paragraphs will be needed once the panels build:
> one Mode 2 blurb per new panel. Standard pattern; not a Wave 5 brief
> item.

---

## 6. Open questions for the user

None blocking. Two minor ones for awareness:

1. **Panel 7 nomenclature.** Adding a seventh panel to Labour and
   Housing changes those sections from 6-panel to 7-panel. This is
   within the 6-8 envelope I named for v1, but it does push Labour
   and Housing closer to Policy's 8-panel weight. Flagging in case
   the user prefers a stricter "all sections at 6 panels" discipline,
   in which case EI and Affordability would need to fold into existing
   panels instead. Default position: 7 panels each is the right call;
   both adds carry their own analytical weight.

2. **CPI ex-indirect-taxes timing.** I've gated this on data availability
   (Phase 2). If the user wants to accelerate (researcher prioritises the
   StatCan vector identification, backend wires next sprint), say so;
   otherwise it sits in the backlog.

---

## File paths touched

- This file: `C:\Users\jayzh\projects\macro-research-department\editorial\wave5_boc_tracker_chart_decisions.md`
- Updated: `C:\Users\jayzh\projects\macro-research-department\editorial\dashboard_purpose.md` (Section 4.3 and 4.4 panel counts; changelog entry)
