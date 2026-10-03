# Fiscal section fact pack -- build unblock 2026-10-03

Prepared 2026-10-03 (all web fetches 16:51-16:55 UTC, HTTP 200 unless noted, browser User-Agent via curl).
Purpose: verified inputs for the writer's redraft of the /fiscal/ `tileLine` and `blurb.body` in `src/data/sections.ts`.
Nothing under `src/` was edited.

Conventions: C$ throughout. "FM" = Department of Finance Fiscal Monitor. "SEU" = Spring Economic Update 2026.
Fiscal year runs April to March. Monthly FM results are unaudited and exclude year-end adjustments.
Repo values carry an as-of stamp because a data refresh ran in this tree at 16:50-16:51 UTC while I was working;
I re-read after it finished and the values were unchanged.

---

## 1. Latest Fiscal Monitor: July 2026

| Fact | Value | Source | Suggested `source:` |
|---|---|---|---|
| Latest issue | The Fiscal Monitor - July 2026 (reference month July 2026; FY2026-27, April to July) | https://www.canada.ca/en/department-finance/services/publications/fiscal-monitor/2026/07.html | `pipeline:dof:fiscal_monitor` |
| Publication date | 2026-09-25 (page metadata `dcterms.issued`; also listed 2026-09-25 on the DoF publications page) | same; https://www.canada.ca/en/department-finance/services/publications.html | n/a (not a prose claim) |
| No newer issue exists | `/fiscal-monitor/2026/08.html` returns 404. Index page: August results due "no later than" October 30, 2026 | https://www.canada.ca/en/department-finance/services/publications/fiscal-monitor.html | n/a |
| Year-to-date balance, April-July FY2026-27 | deficit $5.1B (-5,138 $M) | FM July 2026 Highlights + Table 1; repo `data/raw/dof_fiscal_ytd_balance.csv` 2026-07-31 = -5138.0 (as of 2026-10-03 16:54 UTC; meta fetched_at 16:50:58 UTC) | `pipeline:dof:fiscal_monitor` |
| Same period a year earlier, April-July FY2025-26 | deficit $7.8B (-7,787 $M) | FM July 2026 Highlights + Table 1; repo `data/processed/federal_budget_ytd.csv` 2025-07-31 = -7788.0 (as of 16:52 UTC; see mismatch note M1) | `pipeline:dof:fiscal_monitor` (or `card:claim_dof_fm_jul2026_ytd_deficit_narrower`, pending) |
| July 2026 single-month balance | deficit $4.8B (-4,768 $M) | FM July 2026 Highlights + Table 1; repo `data/raw/dof_fiscal_monthly_balance.csv` 2026-07-31 = -4768.0 (as of 16:54 UTC) | `pipeline:dof:fiscal_monitor` |
| July 2025 single-month balance | deficit $1.5B (-1,512 $M) | FM July 2026 Highlights + Table 1; repo `data/raw/federal_budget_balance.csv` 2025-07-31 (as of 16:52 UTC) | `pipeline:dof:fiscal_monitor` |
| Year-to-date balance excluding net actuarial losses | deficit $3.5B (-3,478 $M) vs $6.4B (-6,447 $M) a year earlier | FM July 2026 Highlights + Table 1 (not in repo data) | `pipeline:dof:fiscal_monitor` if cited; otherwise omit |
| Revenues, April-July | $175.5B (175,469 $M), up $12.0B or 7.4% from 163,443 $M | FM July 2026 Table 1 / Table 2; repo `data/raw/dof_fiscal_ytd_summary.csv` revenues_ytd = 175469.0 (as of 16:54 UTC). Growth rate is published on the page, not in the repo | `pipeline:dof:fiscal_monitor` |
| Program expenses excluding net actuarial losses, April-July | $159.0B (158,968 $M), up $7.7B or 5.1% from 151,293 $M | FM July 2026 Table 1 / Table 3 (NOT in repo; see mismatch note M3) | `pipeline:dof:fiscal_monitor` (published-page figure) |
| Public debt charges, April-July | $20.0B (19,979 $M), up $1.4B or 7.4% from 18,597 $M | FM July 2026 Table 1 / Table 3; repo `dof_fiscal_ytd_summary.csv` public_debt_charges_ytd = -19979.0 (stored with a negative sign; as of 16:54 UTC) | `pipeline:dof:fiscal_monitor` |
| Net actuarial losses, April-July | 1,660 $M, up $0.3B or 23.9% from 1,340 $M | FM July 2026 Table 1 / Table 3 | `pipeline:dof:fiscal_monitor` |
| Total expenses, April-July | 180,607 $M, up 5.5% from 171,230 $M | FM July 2026 Table 3; repo `dof_fiscal_ytd_summary.csv` expenses_ytd = 180607.0 | `pipeline:dof:fiscal_monitor` |
| July 2026 month: revenues | $42.8B, up $0.2B or 0.5% | FM July 2026 Highlights / Table 2 | `pipeline:dof:fiscal_monitor` |
| July 2026 month: program expenses ex actuarial | $41.8B, up $2.8B or 7.3% | FM July 2026 Highlights / Table 3 | `pipeline:dof:fiscal_monitor` |
| July 2026 month: public debt charges | 5,371 $M, up $0.5B or 11.3% | FM July 2026 Highlights / Table 3 | `pipeline:dof:fiscal_monitor` |
| Debt charges as share of revenue, April-July FY2026-27 | 11.4% (19,979 / 175,469 = 11.386%) | repo `data/derived/dof_fiscal_ratio_history.csv` 2026-07-31 ratio_pct = 11.386 (panel-2 key `debt_service_ratio`); recomputed by hand from Table 1 | `derived` |
| Same ratio, April-July FY2025-26 | 11.4% (18,597 / 163,443 = 11.378%) -- i.e. unchanged year over year | hand arithmetic on FM July 2026 Table 1 prior-year columns (not stored in repo for this month) | `derived` |

Verbatim sentences confirmed present on the July 2026 page (non-breaking spaces normalised):

- "There was a budgetary deficit of $4.8 billion in July 2026, compared to a deficit of $1.5 billion in July 2025."
- "The government posted a budgetary deficit of $5.1 billion for the April to July period of the 2026-27 fiscal year, compared to a deficit of $7.8 billion reported for the same period of 2025-26."
- "Revenues were up $12.0 billion, or 7.4 per cent, largely reflecting increases in personal income tax revenues, other revenues and GST revenues."
- "Program expenses excluding net actuarial losses were up $7.7 billion, or 5.1 per cent, due mainly to increases in direct program expenses and major transfers to persons"
- "Public debt charges increased by $1.4 billion, or 7.4 per cent, largely reflecting higher average effective interest rates on an increased stock of marketable bonds"

Context the Fiscal Monitor itself gives for the year-to-date comparison (useful if the writer wants a "why"):

- Revenue gain composition (Table 2, April-July, $M): personal income tax 71,037 -> 76,679 (+7.9%); GST 18,853 -> 21,476 (+13.9%); "other revenues" 15,482 -> 20,768 (+34.1%); corporate income tax 32,810 -> 32,416 (-1.2%); customs import duties 4,663 -> 2,925 (-37.3%); energy taxes 1,786 -> 1,265 (-29.2%).
- The page attributes the GST gain to "a return to more historically comparable levels after unusually low revenues in early 2025-26", and the customs decline to "the repeal of countermeasures imposed in response to U.S. tariffs".
- Other revenues (+$5.3B) account for 44% of the $12.0B revenue gain (5,286 / 12,026); the page attributes this to "higher interest and penalties revenues, as well as higher revenues from enterprise Crown corporations and offshore resource revenues".
- Direct program expenses up $7.7B or 11.8%; operating expenses up $4.5B or 11.4%, "largely attributable to a change in the methodology for recording bad debt expense associated with taxes receivable, which has resulted in the recording of expenses earlier in the fiscal year, higher personnel costs, and increased defence spending". That methodology change pulls expense forward within the year, so it flatters nothing and slightly overstates year-to-date spending growth relative to last year's timing.
- Pollution pricing proceeds returned to Canadians down $2.1B or 85.5% (wind-down after the fuel charge ended April 1, 2025).

### Pipeline cross-check against the published page

Matches (repo as of 2026-10-03 16:52-16:54 UTC; `fiscal.json` generatedAt 2026-10-03T16:51:23Z, previous build 00:48Z showed the same values):

- `dof_fiscal_monthly_balance` April-July FY2026-27: -1046, -313, 989, -4768 = published (1,046), (313), 989, (4,768). Match.
- `dof_fiscal_ytd_balance` April-July: -1046, -1359, -370, -5138 = published. Match.
- `dof_fiscal_ytd_summary`: revenues 175469 and total expenses 180607 = published. Match.
- `debt_service_ratio` 2026-07-31 = 11.386 = 19,979 / 175,469. Match.

Mismatches and seams to know about (none changes a rounded headline number):

- **M1. One-million rounding drift in the prior-year year-to-date series.** `data/processed/federal_budget_ytd.csv` is built by cumulatively summing the rounded monthly figures, so it differs from the published year-to-date column by $1M in several months: June 2025 -6276 vs published (6,277); July 2025 -7788 vs (7,787); August 2025 -11068 vs (11,067); December 2025 -26141 vs (26,140); February 2026 -25550 vs (25,549). Both round to $7.8B for July 2025. If a note quotes $ millions, use the published 7,787.
- **M2. Sign convention.** `public_debt_charges_ytd_cad_millions` is stored as -19979 (the page's Table 1 shows expenses as negatives). Magnitude is right; anything that renders it raw will show a negative.
- **M3. "expenses_ytd" is total expenses including net actuarial losses (180,607), not program expenses.** The headline program-expense figure (158,968; +5.1%) and all growth rates are not captured by the pipeline; they exist only on the published page. The 7.4% / 5.1% / 7.4% growth rates in this pack were read from the page.
- **M4. May 2026 is missing from the debt-charges ratio history.** `data/derived/dof_fiscal_ratio_history.csv` jumps from 2026-04-30 to 2026-06-30. Cause: April and May were published as one combined issue ("The Fiscal Monitor - April and May 2026", 2026-07-31) at `/2026/04.html`; `/2026/05.html` returns 404 (checked 16:54 UTC). The balance series do have May.
- **M5. The section's first headline slot is not the Fiscal Monitor.** In `data/site/sections.json` the `fiscal-ytd-balance` print shows "-$66.9B / FY 2025-26 est." (the SEU full-year estimate from `frt_federal_balance_total`), not the April-July figure. So a tileLine about the $5.1B year-to-date deficit will sit above a headline number of -$66.9B. Not wrong, but the writer should know the two differ.

---

## 2. FY2025-26 full-year deficit: freshest official figures

| Fact | Value | Source | Suggested `source:` |
|---|---|---|---|
| Latest Department of Finance estimate, FY2025-26 budgetary balance | deficit $66.9B (2.1% of GDP) | SEU 2026 Annex 1, Table A1.7, published 2026-04-28: https://budget.canada.ca/update-miseajour/2026/report-rapport/anx1-en.html (row verbatim: "Spring Update 2026 budgetary balance -36.3 -66.9 -65.3 -63.1 -57.7 -56.2 -53.2"); repo `data/derived` series `frt_federal_balance_total` 2026-03-31 = -66.9 | `pipeline:dof:fiscal_reference_tables` or `card:claim_dof_deficit_larger_than_handoff_below_pandemic` (existing) |
| Same figure restated in the July 2026 FM | "Actual/projected annual budgetary balance" 2025-26 = (66,858) $M, sourced on the page to Spring Economic Update 2026 | FM July 2026, Chart 2 text version | `pipeline:dof:fiscal_monitor` |
| Preliminary monthly-results total, April 2025-March 2026 | deficit $55.3B (-55,277 $M), vs $43.2B for 2024-25 on the same preliminary basis | FM March 2026, published 2026-05-29, not revised since (dcterms.modified 2026-05-29); the July 2026 FM still shows March year-to-date (55,277). Repo `federal_budget_ytd.csv` 2026-03-31 = -55277.0 | `pipeline:dof:fiscal_monitor` |
| FY2024-25 actual | deficit $36.3B | SEU Table A1.7 first column; FRT 2025 | `pipeline:dof:fiscal_reference_tables` |
| Parliamentary Budget Officer projection, FY2025-26 | deficit $72.0B (2.2% of GDP) | PBO Economic and Fiscal Outlook - June 2026 (RP-2627-002-S), 2026-06-04, report highlights via PBO publications API: "PBO projects the budgetary deficit to increase from $36.3 billion (1.2 per cent of GDP) in 2024-25 to $72.0 billion (2.2 per cent of GDP) in 2025-26". https://www.pbo-dpb.ca/en/publications/RP-2627-002-S--economic-fiscal-outlook-june-2026--perspectives-economiques-financieres-juin-2026 | no existing card carries this number; would need a new card before use |

**Has anything newer than the old copy's figures been published? No final number exists yet.**

- No Annual Financial Report or Fiscal Reference Tables for 2025-26: `/annual-financial-report/2026.html` and `/fiscal-reference-tables/2026.html` both return 404; the DoF publications list shows the most recent as the 2024-25 editions, published 2025-11-07. Last year's timing suggests early November.
- No "final" March Fiscal Monitor with year-end adjustments: the March 2026 issue is unchanged since 2026-05-29.
- So the two FY2025-26 numbers in the old copy ($55.3B preliminary monthly total; $66.9B SEU estimate) are both still the latest of their kind. The gap between them is year-end adjustments not yet booked in the monthly results. The best single figure for "the FY2025-26 deficit" remains the SEU's $66.9B estimate until the Annual Financial Report lands.

**Budget / update since June 2026:**

- Budget 2026 has NOT been tabled. `https://budget.canada.ca/2026/home-accueil-en.html` returns 404. budget.canada.ca states budgets are now delivered in the fall with the update in the spring.
- Pre-budget consultations for Budget 2026 concluded September 8, 2026 (DoF news release dated September 9, 2026: https://www.canada.ca/en/department-finance/news/2026/09/government-of-canada-concludes-pre-budget-consultations-for-budget-2026.html).
- I found no announced tabling date in the 50 most recent DoF news items (back to June 23, 2026). I did not search beyond that feed, so "no date announced" is unverified; "not yet tabled" is verified.
- No fall economic statement is expected under the new calendar (updates moved to spring starting 2026).
- No new PBO Economic and Fiscal Outlook since June 4, 2026 (PBO publications list checked through October 1, 2026). PBO did publish "The Government's Operating Budget Fiscal Anchor" (RP-2627-010-S, 2026-09-24); it assesses the anchor's definitions and carries no new deficit projection in its highlights.
- Therefore the FY2026-27 projected deficit ($65.3B), debt-to-GDP (41.5%) and debt-charges-to-revenue (11.1%) numbers are unchanged from the SEU vintage.
- New measures announced since the SEU that are not in those projections as far as I can tell (I did not find them in SEU Annex 1): the Productivity Mega Deduction, DoF release 2026-09-15 states "The estimated incremental fiscal cost of the measure is $36 billion over five years, beginning in 2026-27"; tariff-response support for workers and businesses announced 2026-08-25; fuel excise tax relief extended 2026-09-02. I did not verify whether any of these were already provisioned in the SEU baseline. Treat as context only; do not write "the deficit will be larger than projected" from this.

---

## 3. Headline slots on the section (annual ratios)

All three come from `data/derived/frt_*.csv`, files last written 2026-06-18, read 2026-10-03 16:52 UTC. None has a newer vintage available; they change when the Annual Financial Report / Fiscal Reference Tables 2026 or Budget 2026 publish.

| Slot (key in `sections.json`) | Shown value | Fiscal year / vintage | Pipeline series | Primary check | Suggested `source:` |
|---|---|---|---|---|---|
| Federal debt, % of GDP (`fiscal-debt-gdp`) | 41.1%; delta shown "-0.1 pp" | FY2025-26 estimate, SEU 2026 (2026-04-28). Prior point 41.2% is FY2024-25 from FRT 2025 | `frt_federal_debt_pct_gdp` (derived) | SEU Table A1.7 "Federal debt 40.7 41.1 41.5 41.8 41.9 41.8 41.6" (2024-25 to 2030-31) -- 41.1 confirmed | `pipeline:dof:fiscal_reference_tables` |
| Program expenses, % of GDP (`fiscal-program-exp-gdp`) | 15.8% (15.81); delta "-0.3 pp" | FY2025-26 estimate, SEU 2026. Prior point 16.1% is FY2024-25 from FRT 2025 | `frt_program_exp_pct_gdp` (derived) | SEU Table A1.7 per cent of GDP row "Program expenses, excluding net actuarial losses 15.8 15.8 15.9 15.6 15.3 15.3 15.1" -- 15.8 confirmed | `pipeline:dof:fiscal_reference_tables` |
| Interest, % of revenue (`fiscal-interest-rev`) | 10.6%; delta "+0.1 pp" | FY2025-26 estimate. Prior point 10.5% is FY2024-25 from FRT 2025 | `frt_debt_charges_pct_revenues` (derived) | SEU Table A1.7: public debt charges 54.0 / budgetary revenues 511.5 = 10.56% -> 10.6 confirmed by arithmetic | `pipeline:dof:fiscal_reference_tables` (value) or `derived` |
| Federal budget balance (`fiscal-ytd-balance`) | -$66.9B; delta "-$30.6B" | FY2025-26 estimate, SEU 2026, vs FY2024-25 actual -36.3 | `frt_federal_balance_total` | SEU Table A1.7 row confirmed | `pipeline:dof:fiscal_reference_tables` |

FY2026-27 projections in the same series, for a forward-looking sentence (all SEU 2026 vintage): debt 41.5% of GDP; program expenses 15.9% of GDP; debt charges 11.1% of revenue (58.7 / 529.6 = 11.08%); deficit $65.3B (1.9% of GDP).

Caveats the writer and fact-checker need:

- **Debt-to-GDP delta crosses vintages.** The slot's "-0.1 pp" compares 41.1% (SEU, April 2026 GDP) with 41.2% (FRT 2025, older GDP). On the SEU's own consistent basis FY2024-25 is 40.7%, so debt-to-GDP ROSE 0.4 pp into FY2025-26 and rises again to 41.5% in FY2026-27. Do not write that debt-to-GDP fell. "Near 41%" or "41.1%" as a level is safe.
- **Program-expense delta has the same seam.** SEU's own FY2024-25 figure is 15.8%, so on a consistent basis the ratio is flat at 15.8%, not down 0.3 pp.
- **The 10.6% forecast point's stated source is PBO, not DoF.** The meta for `frt_debt_charges_pct_revenues` says the forecast segment is PBO Economic and Fiscal Outlook June 2026; the sibling `frt_debt_charges_pct_revenues_dof` (SEU-derived) gives the same 10.6% and 11.1% for FY2025-26 and FY2026-27, so the number holds either way. The old citation note "DoF ... FY2025-26 estimate = 10.6%" is right on the value; they diverge from FY2027-28 on (PBO 11.6% vs DoF 12.0%).
- **Preliminary actuals differ from the estimate.** FM March 2026 preliminary full-year: debt charges 53,707 / revenues 500,017 = 10.7% (repo `dof_fiscal_ratio_history.csv` 2026-03-31 = 10.741). Year-end adjustments will move this.
- **Monthly run-rate is higher than the annual slot.** April-July FY2026-27: 11.4% (see section 1), the same as April-July a year earlier (11.4%).

---

## 4. Source cards

**Existing card `claim_dof_deficit_larger_than_handoff_below_pandemic`** (`editorial/source_cards/_pending/fiscal/claim_dof_deficit_larger_than_handoff_below_pandemic.yaml`), not modified.

- Is its claim still current? **Yes, as literally stated.** "The FY2025-26 federal deficit forecast is larger than the FY2024-25 handoff deficit, but far below the FY2020-21 pandemic deficit": SEU -66.9 vs -36.3 re-confirmed today on the SEU page; no newer DoF figure exists. The -327.7 pandemic figure comes from FRT 2025 (a PDF; I did not re-open it today, but the repo series `frt_federal_balance_total` carries -327.7 and FRT 2025 has not been superseded).
- Is it still the right backing for the opening take? **No.** It describes how FY2025-26 compared with FY2024-25. It says nothing about FY2026-27, which is now the year the section's charts show. Using it to support a present-tense stance claim would be citing last year's widening for this year's stance.
- Housekeeping flags on that card (not fixed, since it awaits Jay's approval): its `excerpt` is a description, not verbatim source text; its anchor `#a4` is not where Table A1.7 sits (the table is under `#a6`); status is `pending_user` with `user_confirmed_at: null`; it lives only in `_pending/` and is not in `registry.yaml`. The citation gate (`node scripts/check_citation_coverage.mjs`) currently passes with it cited (29 strict pass, 0 fail, run 16:54 UTC), though the gate's own code says cards in `_pending/` should be refused -- I did not chase why it is not tripping.

**New cards created (both Tier A, both `status: pending_user`, in `editorial/source_cards/_pending/fiscal/`):**

1. `claim_dof_fm_jul2026_ytd_deficit_narrower` -- April-July FY2026-27 deficit $5.1B vs $7.8B a year earlier. Source: FM July 2026. Excerpt string-matched verbatim against the page fetched today.
2. `claim_dof_seu2026_deficit_2026_27_vs_2025_26` -- SEU projects FY2026-27 deficit $65.3B vs $66.9B for FY2025-26. Source: SEU Annex 1 Table A1.7. Excerpt is the table row, string-matched against the page fetched today.

Both follow the existing card's field layout. Neither is confirmed by Jay, so by the tiered-verification rules the writer should not depend on them until approved. Every number in them is also reachable without a card: the Fiscal Monitor figures via `pipeline:dof:fiscal_monitor`, the SEU figures via `pipeline:dof:fiscal_reference_tables`. Recommended: cite the pipeline sources and treat the cards as optional backing for the take sentence.

---

## 5. Evidence on "Fiscal policy is modestly stimulative" -- numbers only

Year to date (April-July), FY2026-27 vs FY2025-26, $ millions, FM July 2026 Table 1:

| Line | FY2025-26 | FY2026-27 | Change | Effect on balance |
|---|---|---|---|---|
| Revenues | 163,443 | 175,469 | +12,026 (+7.4%) | +12,026 |
| Program expenses ex actuarial | 151,293 | 158,968 | +7,675 (+5.1%) | -7,675 |
| Public debt charges | 18,597 | 19,979 | +1,382 (+7.4%) | -1,382 |
| Net actuarial losses | 1,340 | 1,660 | +320 (+23.9%) | -320 |
| Budgetary balance | -7,787 | -5,138 | +2,649 | check: 12,026 - 7,675 - 1,382 - 320 = 2,649 |

- **The deficit is running NARROWER than the same period last year: $5.1B vs $7.8B, an improvement of $2.6B (2,649 $M), or 34% smaller (2,649 / 7,787).** `derived`
- Excluding net actuarial losses: $3.5B vs $6.4B, narrower by $3.0B (2,969 $M), 46% smaller. `derived`
- Revenue growth (7.4%) is outpacing program-expense growth (5.1%) year to date.
- **The single month of July points the other way: $4.8B deficit vs $1.5B in July 2025, wider by $3.3B (3,256 $M).** In July alone revenues rose 0.5% while program expenses rose 7.3% and debt charges 11.3%. `derived`
- Through June the gap was larger: April-June deficit $0.4B (370 $M) vs $6.3B (6,277 $M), narrower by $5.9B. July gave back $3.3B of that $5.9B.
- Monthly pattern FY2026-27: April -1,046; May -313; June +989 (surplus); July -4,768. Same months FY2025-26: -7,711; -2,194; +3,629; -1,512. Two of four months were better than a year earlier (April and May) and two were worse (June's surplus was smaller, 989 vs 3,629, and July's deficit larger). The whole year-to-date improvement comes from April (+6,665) and May (+1,881); June (-2,640) and July (-3,256) subtracted from it.
- Against the full-year plan: the year-to-date deficit is 7.9% of the SEU's projected FY2026-27 deficit (5,138 / 65,345) one third of the way through the year. Last year at the same point it was 11.6% of the SEU's FY2025-26 estimate (7,787 / 66,858) or 14.1% of the preliminary monthly total (7,787 / 55,277). The federal deficit is heavily back-loaded (March 2026 alone was -29.7B), so the early-year run-rate says little about where the year ends.
- Full-year projections (SEU, April 2026): deficit $65.3B in FY2026-27 vs $66.9B in FY2025-26, i.e. $1.6B smaller; as a share of GDP 1.9% vs 2.1%. Program expenses 15.9% of GDP vs 15.8%; revenues 15.7% vs 15.8%.
- PBO (June 2026) puts FY2025-26 at $72.0B and says its deficits average $4.6B a year above the SEU's over the projection.

What the arithmetic supports, without choosing the take: on realized data the deficit is smaller than a year ago, and on the government's own projection it is roughly flat to slightly smaller as a share of GDP (2.1% to 1.9%). The old justification for "stimulative" (deficit nearly doubling from $36.3B to $66.9B) was a statement about FY2025-26 vs FY2024-25. The comparable FY2026-27 vs FY2025-26 change is a narrowing on both realized and projected measures. A level argument (a deficit near 2% of GDP is still a deficit) remains available; a change argument (the deficit is widening) is not supported by any number above except the single month of July.

---

## What changed since the old copy

Plain-English status of each claim in the existing tileLine and blurb (dated June 16, 2026):

1. **"Fiscal Monitor Mar '26" (heroKicker) and "The March Fiscal Monitor..."** -- outdated. The latest issue is July 2026, published September 25, 2026. Three issues have come out since (April-May combined, June, July).
2. **tileLine "The federal deficit reached $55.3B through March, wider than last year."** -- outdated on both halves. $55.3B is last fiscal year's twelve-month preliminary total. The current fiscal year's figure is $5.1B through July, and it is narrower than last year ($7.8B), not wider. The direction of the comparison has flipped.
3. **"Fiscal policy is modestly stimulative."** -- no longer supported by the citation attached to it. That citation rests on the deficit widening from $36.3B to $66.9B, which is last year's story. This year's data show a narrower deficit year to date and a slightly smaller projected full-year deficit. Whether the stance is still called stimulative is Jay's and the writer's call; the old evidence does not carry it.
4. **"FY2025-26 deficit at $55.3 billion on a cash basis"** -- the number is still the latest preliminary figure (not revised), but it is no longer news, and "cash basis" was never right. The Fiscal Monitor page states verbatim: "The budgetary balance is presented on an accrual basis of accounting, recording government revenues and expenses when they are earned or incurred, regardless of when the cash is received or paid." The $55.3B is the monthly results before post-March year-end adjustments. Drop "cash basis" in any reuse.
5. **"Spring Economic Update estimate is $66.9 billion, up from $36.3 billion the year before"** -- still accurate and still the freshest official full-year figure for FY2025-26 (no Annual Financial Report or Budget 2026 yet). But it describes a year that ended six months ago; if kept, it is background, not the lead.
6. **"Debt is still expected to sit near 41.1% of GDP"** -- the number is still the current FY2025-26 estimate. The current-year projection is 41.5%. Avoid implying it is falling: on a consistent basis it rose from 40.7% and is projected to keep rising to 41.9% by FY2028-29.
7. **"public debt charges are taking 10.6% of revenue"** -- still the FY2025-26 estimate. Fresher readings are higher: 11.1% projected for FY2026-27, and 11.4% actual for April-July 2026 (unchanged from the same months a year earlier).
8. **Citation notes** -- the tileLine note comparing "-55.277bn versus FY2024-25 full-year -43.154bn" and all "Fiscal Monitor March 2026" notes need replacing with July 2026 values. The `updatedAt` and blurb `date` need to move to the redraft date.

## Could not verify

- Whether a Budget 2026 tabling date has been announced (not found in DoF's 50 most recent news items; not searched elsewhere).
- Whether the Productivity Mega Deduction and the August tariff-response package were already provisioned in the SEU baseline.
- The FY2020-21 -$327.7B figure on the existing card was not re-fetched today (FRT 2025 is a PDF already in the repo; value matches the repo series).
- Why the citation gate passes while the existing fiscal card sits in `_pending/`.
- PBO's FY2026-27 deficit figure (the June outlook's highlights give FY2025-26 and FY2030-31 only; I did not open the PDF).
