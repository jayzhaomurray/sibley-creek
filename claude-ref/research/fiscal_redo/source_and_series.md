# Federal Fiscal Page Redo — Source & Series Foundation

Researcher deliverable. Compiled 2026-06-02. Canada-first, federal (Government
of Canada) only. This is the data foundation the backend pipeline and
chart-builder build from. Every number traces to a primary source named inline.

## Top-line vintage findings (read first — corrects a brief assumption)

- **The operating/capital framing was introduced in BUDGET 2025, not a separate
  "Budget 2026."** Budget 2025 was tabled **4 November 2025** (the federal budget
  moved to a fall cadence). There is no document titled "Budget 2026" as of
  2026-06-02. Jay's "Budget 2026" maps to the **current budget cycle**, whose
  freshest official vintage is the **Spring Economic Update 2026 (SEU 2026),
  tabled 28 April 2026.** I use the actual document names throughout.
  Verified: Budget 2025 overview confirms it "adopt[ed] a new growth-oriented
  approach... underscored by the shift in the composition of spending" with two
  fiscal anchors (operating balance balanced by 2028-29; declining deficit-to-GDP).
  (`https://budget.canada.ca/2025/report-rapport/overview-apercu-en.html`)

- **Use SEU 2026 Annex 1 as the PRIMARY forward profile** for revenues, expenses,
  balance, debt, debt-to-GDP, operating balance, and capital investment. It is the
  freshest DoF projection and supersedes Budget 2025 Annex 1.
  (`https://budget.canada.ca/update-miseajour/2026/report-rapport/anx1-en.html`)

- **Use the Fiscal Reference Tables October 2025 (FRT 2025) as the PRIMARY long
  %GDP and instrument-stock history.** FRT 2025 carries actuals through FY2024-25.
  Local cached copy verified at `data/raw/fiscal/frt_2025.pdf` (65 pp); table text
  extracted via pypdf this session. Landing page
  `https://www.canada.ca/en/department-finance/services/publications/fiscal-reference-tables/2025.html`
  and the dam PDF both **403 to WebFetch** — the cached PDF is the working copy;
  flag for a human re-pull if decimals are challenged.

- **GDP denominator caveat (critical for fact-checkers):** the FRT 2025 %GDP
  series and the SEU 2026 / Budget 2025 %GDP series use **different nominal-GDP
  vintages**. FRT 2025 reports FY2024-25 federal debt at **41.2% of GDP (actual)**;
  Budget 2025 Annex 1 projected FY2024-25 at **42.4%**; SEU 2026 Annex 1 reports
  FY2024-25 at **40.7%**. Same dollar debt (~$1,266.5B), three different ratios,
  because the GDP denominator was revised between vintages. **Never mix a level
  from one vintage with a ratio from another.** When charting a continuous
  history-into-forecast %GDP line, splice FRT actuals (through FY2024-25) to SEU
  2026 forecasts (FY2025-26 on) ONLY with a vintage-seam note, or hold the entire
  line on a single vintage and accept the level offset.

- **Accounting-basis breaks (FRT footnotes, apply to every %GDP and level series):**
  (a) Full accrual accounting introduced 1983-84 — pre-1983-84 not comparable.
  (b) FY2019-20: "Net actuarial losses" split into a separate expense category;
  FY2008-09 to FY2018-19 reclassified. (c) FY2017-18: discount-rate methodology
  change for unfunded future benefits, restated FY2008-09 to FY2016-17. (d) Apr
  2022: PS 3280 (Asset Retirement Obligations) raised the accumulated deficit by
  $5,379M. (e) FY2022-23: financial-instruments standard added remeasurement
  gains/losses (excluded from the budgetary balance) and a $2,563M opening-balance
  adjustment. The COVID step (FY2019-20 31.2% → FY2020-21 47.2% of GDP debt) is
  real, not a basis break.

---

# Indicator 1 — Budget balance: operating (opex) vs capital (capex)

## Metric definition
Federal budgetary balance ($B, fiscal year ending 31 March), decomposed under
Budget 2025's Capital Budgeting Framework into:
- **Operating balance** = budgetary revenues minus operating expenses (day-to-day
  spending + public debt charges + net actuarial losses), EXCLUDING capital
  investment. Surplus/(deficit).
- **Capital investment** = spending the government classifies as contributing to
  capital formation. The operating balance plus (minus) capital investment
  reconciles to the total budgetary balance.

## Primary source (official DoF series)
- **Spring Economic Update 2026, Annex 1** — Tables A1.4 (capital investments),
  A1.5 (operating balance), A1.7 (summary statement of transactions). Tabled
  28 April 2026. `https://budget.canada.ca/update-miseajour/2026/report-rapport/anx1-en.html`
  (WebFetched and verified this session.)
- Framing origin / fiscal anchors: Budget 2025 overview, 4 Nov 2025.
  `https://budget.canada.ca/2025/report-rapport/overview-apercu-en.html`

## Series — DoF official (SEU 2026 Annex 1). Units: $B.

| Fiscal year | Total balance | Operating balance (A1.5) | Capital investment (A1.4) | Kind |
|---|---|---|---|---|
| 2024-25 | -36.3 | n/a (pre-framework actual) | n/a | HISTORY |
| 2025-26 | -66.9 | -26.4 | 40.5 | FORECAST |
| 2026-27 | -65.3 | -10.5 | 54.9 | FORECAST |
| 2027-28 | -63.1 | -5.2 | 57.9 | FORECAST |
| 2028-29 | -57.7 | 0.9 | 58.6 | FORECAST |
| 2029-30 | -56.2 | 4.5 | 60.6 | FORECAST |
| 2030-31 | -53.2 | 6.1 | 59.3 | FORECAST |

Reconciliation note: operating balance + (−capital investment) ≈ total balance,
within rounding (e.g. 2026-27: −10.5 − 54.9 = −65.4 vs −65.3 reported). The SEU
intro chart 0.8 rounds these to operating deficit 26 / capital 41 / total 67 for
2025-26, etc. The Annex 1 decimals above are the authoritative version.
SEU narrative: the operating balance reaches balance/surplus by FY2028-29 (the
first fiscal anchor); by FY2028-29 "the deficit will entirely support capital
investments."

## Long balance history ($ and %GDP) — FRT 2025
Total budgetary balance as % of GDP is available back to 1966-67 in **FRT 2025
Table 2** ("Fiscal transactions, per cent of GDP", `data/raw/fiscal/frt_2025.pdf`
p.10). Budgetary balance %GDP column (= "Budgetary surplus or deficit excluding
net actuarial losses" pre-2008-09; "Budgetary surplus/deficit (-)" with actuarial
from 2008-09): recent actuals — FY2019-20 −1.7, FY2020-21 −14.8 (COVID),
FY2021-22 −3.6, FY2022-23 −1.2, FY2023-24 −2.1, FY2024-25 −1.2. (All % of GDP,
FRT 2025 vintage.) The dollar balance for FY2024-25 actual is **−$36.3B**
(reconciles to SEU/Budget 2025 actual and Table 15 accumulated-deficit change).

## PBO reclassification dispute (capture both framings; DoF is PRIMARY)
- **Primary PBO source:** PBO, "Budget 2025: Issues for Parliamentarians,"
  report RP-2526-017-S, published 14 Nov 2025.
  `https://www.pbo-dpb.ca/en/publications/RP-2526-017-S--budget-2025-issues-parliamentarians--budget-2025-enjeux-parlementaires`
  (WebFetched and verified this session.)
- **The dispute:** Budget 2025 classifies **$311.3B** of capital investment over
  FY2024-25 to FY2029-30. PBO, applying conventional/international capital
  definitions (excluding corporate income-tax expenditures, investment tax
  credits, and operating subsidies), counts **$217.3B** — **~$94B (≈30%) lower.**
- **Operating-balance consequence:** DoF's framework shows the operating balance
  reaching surplus over FY2026-27 to FY2029-30 (absent new measures) and balanced
  by FY2028-29 with measures. PBO: "Based on our definition, the operating balance
  in Budget 2025 would remain in a deficit position over 2024-25 to 2029-30."
- **PBO recommendation:** establish an independent expert body to determine which
  spending qualifies as capital. (Same report.)
- **Editorial handling:** primary chart series = DoF official operating/capital
  split. The PBO ~$94B reclassification is a contested-definition annotation, not
  a competing primary series. If the page shows a "PBO view" it must be framed as
  *PBO argues* (Mode 3), not as the truth of the split.

## Caveats for fact-checker
- Operating-balance and capital-investment lines exist ONLY from FY2025-26 forward
  (the framework is new; no pre-2025 official back-series). Do not fabricate
  pre-2025 operating/capital points.
- SEU 2026 intro chart (0.8) rounds to whole $B; Annex 1 tables carry the decimals.
  Cite Annex 1 for any decimal call-out.
- The $311.3B vs $217.3B figures are PBO's stated government/PBO totals over
  FY2024-25 to FY2029-30 (six years). Budget 2025 elsewhere cites "$1 trillion in
  total investment over five years" — that is a broader public+private leverage
  claim, NOT the federal capital line; do not conflate.

---

# Indicator 2 — Federal revenues as % of GDP

## Metric definition
Federal budgetary revenues divided by nominal GDP, fiscal year. Public Accounts
basis (accrual).

## Primary sources
- **Long history:** FRT 2025 **Table 2** (per cent of GDP), `data/raw/fiscal/frt_2025.pdf`
  p.10. Actuals 1966-67 → FY2024-25.
- **Forward profile:** SEU 2026 Annex 1 (revenue $B series, divide by SEU nominal
  GDP; SEU narrative states revenues run **15.6–16.4% of GDP** across the horizon).
  `https://budget.canada.ca/update-miseajour/2026/report-rapport/anx1-en.html`

## Series — FRT 2025 Table 2, Revenues (% of GDP), recent actuals (HISTORY)

| FY | Rev %GDP | FY | Rev %GDP |
|---|---|---|---|
| 2008-09 | 14.3 | 2017-18 | 14.5 |
| 2009-10 | 14.0 | 2018-19 | 14.9 |
| 2010-11 | 14.4 | 2019-20 | 14.4 |
| 2011-12 | 13.9 | 2020-21 | 14.3 |
| 2012-13 | 13.9 | 2021-22 | 16.3 |
| 2013-14 | 14.2 | 2022-23 | 15.7 |
| 2014-15 | 14.0 | 2023-24 | 15.7 |
| 2015-16 | 14.7 | 2024-25 | 16.6 |
| 2016-17 | 14.4 |  |  |

Full back-series to 1966-67 is in the table (e.g. 1966-67 15.0, peak ~18.9 in
1974-75, trough ~13.9 in 2011-12 and 2012-13). Pull the full column from the PDF
when building the long chart.

## Series — revenue dollars (SEU 2026 Annex 1 Table A1.7), for forward %GDP
Revenues ($B): FY2024-25 511.0 (HIST) · 2025-26 511.5 · 2026-27 529.6 ·
2027-28 546.8 · 2028-29 565.9 · 2029-30 589.8 · 2030-31 613.7 (all FORECAST from
2025-26). To express forward %GDP, divide by SEU nominal GDP (SEU narrative band:
15.6–16.4%). If the backend wants exact forecast %GDP decimals, pull SEU Annex 1
nominal-GDP row in the human re-pull.

## Caveats
- FRT %GDP (16.6% FY2024-25) and SEU forward %GDP (≈16.4% FY2025-26 band) use
  different GDP vintages — see top-line caveat. For a clean long line, anchor
  history on FRT and forecast on SEU, with a seam note.
- Revenue %GDP is procyclical (commodity/corporate-tax sensitive); the FY2021-22
  jump to 16.3% reflects post-COVID nominal-GDP and corporate-tax surge.

---

# Indicator 3 — Federal program expenses as % of GDP

## Recommendation: use PROGRAM EXPENSES (ex-debt-charges), not total expenses
Program expenses excluding net actuarial losses is the cleaner reader indicator
for "how big is government spending." It isolates discretionary + transfer
spending from the debt-service burden, which is rate-driven and better shown as
its own series (the interest-bite ratio). Total expenses conflates a policy
choice (programs) with a financing cost (debt charges). **Recommend the primary
line = program expenses excluding net actuarial losses, % of GDP**, with total
expenses available as a secondary/stacked reference and public debt charges as a
distinct sub-series.

## Metric definition
Program expenses excluding net actuarial losses ÷ nominal GDP, fiscal year,
Public Accounts basis. "Program expenses" = total expenses minus public debt
charges (and, from FY2008-09, separately tracking net actuarial losses).

## Primary sources
- **Long history:** FRT 2025 **Table 8** ("Expenses, per cent of GDP"),
  `data/raw/fiscal/frt_2025.pdf` p.16. Columns: total program expenses; net
  actuarial losses; total program expenses incl. actuarial; public debt charges;
  total expenses. Actuals to FY2024-25.
- **Forward profile:** SEU 2026 Annex 1 Table A1.7 (program-expenses-ex-actuarial
  $B series). SEU narrative: total expenses run **17.0–17.8% of GDP** over horizon.

## Series — FRT 2025 Table 8, recent actuals (% of GDP, HISTORY)

| FY | Program exp (excl actuarial) | Total program exp (incl actuarial) | Public debt charges | Total expenses |
|---|---|---|---|---|
| 2018-19 | 14.4 | 14.4 | 1.0 | 15.5 |
| 2019-20 | 15.1 | 15.1 | 1.1 | 16.1 |
| 2020-21 | 28.1 | 28.1 | 0.9 | 29.0 |
| 2021-22 | 18.9 | 18.9 | 1.0 | 19.9 |
| 2022-23 | 15.7 | 15.7 | 1.2 | 16.9 |
| 2023-24 | 16.2 | 16.2 | 1.6 | 17.8 |
| 2024-25 | 16.1 | 16.1 | 1.7 | 17.8 |

(Table 8's "Total program expenses" column already nets actuarial losses into the
program line for these years; the standalone "Net actuarial losses" sub-column is
0.1–0.7 of GDP in recent years. The FY2024-25 0.1 net-actuarial reading sits
inside the 16.1 program figure.) Full back-series to 1966-67 in the PDF (program
expenses %GDP ranged ~11.8 in 1999-00 to the 28.1 COVID spike).

## Series — program-expense dollars (SEU 2026 Annex 1 Table A1.7), for forward %GDP
Program expenses excl. net actuarial losses ($B): FY2024-25 489.9 (HIST) ·
2025-26 512.8 · 2026-27 536.1 · 2027-28 543.9 · 2028-29 555.9 · 2029-30 575.4 ·
2030-31 591.6 (FORECAST). Total expenses ($B): 547.3 / 578.3 / 595.0 / 609.9 /
623.7 / 645.9 / 666.9. Public debt charges ($B): 53.4 / 54.0 / 58.7 / 65.7 /
71.6 / 75.7 / 80.9. Divide by SEU nominal GDP for forward %GDP (SEU band: total
expenses 17.0–17.8%).

## Caveats
- The FY2008-09 reclassification of net actuarial losses means the program-expense
  series before/after 2008-09 is on a slightly different composition; the FRT
  footnote covers it. Showing program-expenses-ex-actuarial gives the most
  consistent long line.
- COVID FY2020-21 (28.1% of GDP) is a genuine spike, not a basis break — annotate.
- If the page also wants the debt-service story, use FRT Table 13: public debt
  charges as % of revenues (the "interest bite") was **10.5% in FY2024-25**, up
  from 5.9% in FY2021-22 — a cleaner narrative metric than PDC %GDP.

---

# Indicator 4 — Federal debt as % of GDP

## Recommendation: use FEDERAL DEBT = ACCUMULATED DEFICIT
This is the federal government's own headline measure and what every Budget /
FES / SEU and the FRT report as "federal debt-to-GDP." It is the accumulated
deficit (total liabilities minus total assets, i.e. net debt minus net
non-financial assets). **Use this for the reader-facing %GDP indicator** because
(a) it is the official headline, (b) it is what the fiscal anchors and all the
forward projections are stated against, and (c) it is consistently available
back to 1966-67. Net debt (liabilities minus financial assets only) and gross
debt are available in FRT Table 15 as secondary references, but they are not the
headline and would confuse a reader who sees "federal debt-to-GDP" quoted
everywhere else at the accumulated-deficit level.

Definitional ladder (FRT 2025 Table 15, FY2024-25, $M):
- Total liabilities: 2,182,336
- Net debt (liabilities − financial assets 788,750): 1,393,586
- Accumulated deficit / "federal debt" (net debt − non-financial assets 127,102):
  **1,266,484** ≈ the headline **$1,266.5B**.

## Metric definition
Federal debt (accumulated deficit) ÷ nominal GDP, fiscal year ending 31 March.
Federal-only — excludes provincial/territorial/local and CPP/QPP. NOT comparable
to general-government gross debt (the IMF/OECD/Fitch ~100%+ figures).

## Primary sources
- **Long history (%GDP):** FRT 2025 **Table 2**, accumulated-deficit %GDP column,
  `data/raw/fiscal/frt_2025.pdf` p.10. Actuals to FY2024-25.
- **Long history (levels):** FRT 2025 **Table 15**, accumulated-deficit $M column,
  p.23.
- **Forward profile:** SEU 2026 Annex 1 Table A1.7 (federal debt $B and %GDP).

## Series — FRT 2025 Table 2, federal debt (accumulated deficit) as % of GDP (HISTORY)

| FY | %GDP | FY | %GDP | FY | %GDP |
|---|---|---|---|---|---|
| 2006-07 | 31.2 | 2013-14 | 32.9 | 2020-21 | 47.2 |
| 2007-08 | 29.0 | 2014-15 | 31.5 | 2021-22 | 45.0 |
| 2008-09 | 28.2 | 2015-16 | 31.9 | 2022-23 | 41.1 |
| 2009-10 | 33.4 | 2016-17 | 32.2 | 2023-24 | 42.1 |
| 2010-11 | 33.4 | 2017-18 | 31.4 | 2024-25 | 41.2 |
| 2011-12 | 33.4 | 2018-19 | 30.7 |  |  |
| 2012-13 | 34.0 | 2019-20 | 31.2 |  |  |

Full back-series to 1966-67 in the PDF (post-accrual era from 1983-84: peak
**66.6% in 1994-95**, trough **28.2% in 2008-09** pre-GFC, COVID peak 47.2% in
2020-21). The 1994-95 peak is the true historical high of the post-accrual
series — usable for a "highest since" superlative with the 1983-84 basis-break
caveat.

## Series — SEU 2026 Annex 1 (forward, FORECAST from FY2025-26)
Federal debt ($B): 2024-25 1,266.5 (HIST) · 2025-26 1,333.9 · 2026-27 1,399.3 ·
2027-28 1,462.4 · 2028-29 1,520.1 · 2029-30 1,576.3 · 2030-31 1,629.4.
Federal debt (% of GDP, SEU vintage): 2024-25 40.7 (HIST) · 2025-26 41.1 ·
2026-27 41.5 · 2027-28 41.8 · 2028-29 41.9 · 2029-30 41.8 · 2030-31 41.6.

## Vintage reconciliation (fact-checker MUST read)
FY2024-25 federal debt is ~$1,266.5B in all three vintages (level agrees). The
%GDP differs purely on the GDP denominator:
- FRT 2025 (actual, Oct-2025 GDP vintage): **41.2%**
- SEU 2026 Annex 1 (Apr-2026 vintage): **40.7%**
- Budget 2025 Annex 1 (Nov-2025 projection): **42.4%** (and the cached
  `data/derived/fiscal_debt_to_gdp.csv` carries the full Budget 2025 Chart A1.5
  long-term path peaking 43.3% in FY2027-28/2028-29).
For the rebuilt page: anchor the long actual line on **FRT 2025 Table 2** and the
forward line on **SEU 2026 Annex 1**, with a one-line vintage-seam note. Do NOT
splice the Budget 2025 Chart A1.5 (the existing derived CSV) into a chart that
also uses FRT actuals — the denominators differ and the seam would show a
spurious 1.5pp jump at the actual/forecast boundary.

## Caveats
- Accounting-basis breaks per the top-line list apply to the debt %GDP and level
  series. The FY2021-22 +$5,379M (ARO) and FY2022-23 +$2,563M (financial
  instruments) opening-balance adjustments slightly lift the accumulated-deficit
  level relative to a pure prior-year-plus-deficit walk.
- Federal debt %GDP ≠ general-government debt %GDP. Fitch's ~91.8%/98.5% and the
  OECD's ~107% gross figures are consolidated general-government; do not place
  them on the same axis as the ~41% federal accumulated-deficit line.

---

# Indicator 5 — Federal debt issuance by instrument, aggregated

## Canadian taxonomy (corrects the brief's "notes")
Canada does **not** issue "notes" the way the US Treasury does (US bills/notes/bonds
by tenor). The Canadian instrument taxonomy is:
1. **Treasury bills** (incl. cash-management bills) — money-market, <1yr.
2. **Marketable bonds** — nominal + Real Return Bonds (RRB program now in run-off)
   + Green bonds; domestic (C$) and a small foreign-currency tranche.
3. **Retail debt** — Canada Savings Bonds / Canada Premium Bonds (program wound
   down; a small residual stock remains, ~$4.7B and shrinking).
(FRT Table 16 footnotes: "Foreign marketable bonds" includes Canada bills, Canada
notes and Euro medium-term notes — these are the foreign-currency funding
instruments, distinct from the domestic program. "Retail debt" = CSB/CPB.)

## Recommendation: TWO primary buckets, with a third minor bucket
Cleanest reader scheme: **Treasury bills vs Marketable bonds**, with a small
**Retail + foreign** residual if a third slice is wanted. Bonds dominate; bills
are the rollover/short-funding layer; retail is a vanishing tail.

## Recommendation: show OUTSTANDING STOCK as the primary indicator
Jay's "issuance" is ambiguous. Recommend the **outstanding stock by instrument**
as the primary chart: it is a clean, additive, end-of-year-snapshot series that
shows the structure of the federal debt and is directly comparable across years.
Gross issuance (annual auction flow) is a secondary "activity" series — large and
volatile because T-bills roll many times a year, so gross-issuance totals
overstate the funding need and are harder for a reader to interpret. Show stock
as primary; offer gross bond issuance as a secondary flow series if desired.

## Primary sources
- **Outstanding stock by instrument (history):** FRT 2025 **Table 16**
  ("Unmatured debt held by outside parties"), `data/raw/fiscal/frt_2025.pdf` p.24.
  Actuals to FY2024-25. Cross-check: Bank of Canada G6/banking statistics.
- **Gross issuance flow + forward plan:** Debt Management Report 2024-2025
  (actuals) `https://www.canada.ca/en/department-finance/services/publications/debt-management-report/2024-2025.html`;
  SEU 2026 Annex 3 (forward bond program + T-bill stock target)
  `https://budget.canada.ca/update-miseajour/2026/report-rapport/anx3-en.html`
  (WebFetched and verified this session).

## Series — outstanding stock by instrument, FRT 2025 Table 16 ($M, end of FY, HISTORY)

| FY | Domestic mktable bonds | Foreign mktable bonds | Total bonds | Treasury bills | Retail debt | Total unmatured (held by outside parties) |
|---|---|---|---|---|---|---|
| 2018-19 | 569,169 | 16,015 | 585,184 | 134,300 | 1,237 | 733,392 |
| 2019-20 | 596,540 | 15,941 | 612,481 | 151,867 | 497 | 776,906 |
| 2020-21 | 875,023 | 15,427 | 890,450 | 218,800 | 299 | 1,128,808 |
| 2021-22 | 1,030,634 | 14,451 | 1,045,085 | 187,400 | — | 1,249,957 |
| 2022-23 | 1,037,890 | 15,988 | 1,053,878 | 201,800 | — | 1,265,040 |
| 2023-24 | 1,081,399 | 21,131 | 1,102,530 | 267,400 | — | 1,376,822 |
| 2024-25 | 1,163,045 | 29,383 | 1,192,428 | 285,200 | 4,681 | 1,485,887 |

(Table 16 "Total" includes Pension Plan bonds, other unmatured debt, amortized-cost
adjustments, and nets the government's own holdings; the three reader buckets —
total bonds, T-bills, retail — do not sum exactly to Total because of those small
residual columns. For a clean 2-bucket reader chart, use Total marketable bonds vs
Treasury bills; retail is negligible.) Recommended display buckets, FY2024-25:
**marketable bonds $1,192.4B; treasury bills $285.2B; retail $4.7B.**

## Series — gross issuance flow (Debt Management Report 2024-2025, actuals)
- FY2024-25 gross **bond** issuance: **$237.0B** (vs $203.8B in FY2023-24);
  48 nominal bond auctions (vs 49 prior year).
- FY2024-25 change in domestic market debt stock: +$109.3B total, comprising
  +$81.7B marketable bonds (C$), +$19.3B treasury & cash-management bills,
  +$8.3B foreign-currency marketable debt. Domestic market debt stock end
  FY2024-25: **$1,481.2B.**
  (Source: Debt Management Report 2024-2025, DoF.)

## Series — forward issuance plan (SEU 2026 Annex 3, FORECAST)
- **2025-26** (estimate): total domestic issuance ~$603B; marketable bond program
  ~$317B (2yr $120B, 5yr $84B, 10yr $84B, 30yr $24B, green $5B); T-bill stock
  end-year ~$286B.
- **2026-27** (plan): total domestic issuance ~$566B (~$571B incl. ~$5B foreign);
  bond program **$298B** (2yr $110B, 5yr $80B, 10yr $80B, 30yr $24B, green $4B);
  T-bill stock target ~$268B (revised down from $291B budgeted). Foreign-currency
  bond issuance up to ~$5B CAD-equiv. Retail refinancing $0B.
  (Source: SEU 2026 Annex 3.)

## Caveats
- **Stock vs flow are different stories** — label the chart explicitly. Stock =
  structure of the debt (end-of-year snapshot). Gross issuance = annual auction
  activity (T-bills roll, so gross flow >> net change). Recommend stock as primary.
- FRT Table 16 is "held by outside parties" and nets the government's own
  holdings; the Debt Management Report uses "domestic market debt stock" ($1,481.2B
  FY2024-25) which is a slightly different aggregate from FRT Table 16's $1,485.9B
  Total. Both are primary; pick one basis per chart and label it.
- Retail debt (CSB/CPB) is a wound-down program; the $4.7B FY2024-25 reading is a
  residual and trending to zero. Fine to fold into an "other" slice.
- Real Return Bonds: the RRB program was discontinued (no new issuance since 2022);
  a residual stock matures out. Not a forward bucket.

---

# Source ledger (for source_cards / fact-check)

| # | Indicator | Primary source | Vintage / date | URL | Verify status this session |
|---|---|---|---|---|---|
| 1 | Operating/capital split (forward) | SEU 2026 Annex 1 (A1.4/A1.5/A1.7) | 28 Apr 2026 | budget.canada.ca/update-miseajour/2026/report-rapport/anx1-en.html | WebFetched, verified |
| 1 | Op/capital framing + anchors | Budget 2025 overview | 4 Nov 2025 | budget.canada.ca/2025/report-rapport/overview-apercu-en.html | WebFetched, verified |
| 1 | PBO ~$94B reclassification | PBO RP-2526-017-S | 14 Nov 2025 | pbo-dpb.ca/en/publications/RP-2526-017-S--budget-2025-issues-parliamentarians... | WebFetched, verified |
| 1 | Balance %GDP long history | FRT 2025 Table 2 | Oct 2025 | data/raw/fiscal/frt_2025.pdf p.10 | pypdf extract; canada.ca HTML/PDF 403 to WebFetch — flag human re-pull |
| 2 | Revenues %GDP history | FRT 2025 Table 2 | Oct 2025 | (same PDF) | pypdf extract |
| 2 | Revenues forward | SEU 2026 Annex 1 A1.7 | 28 Apr 2026 | (SEU Annex 1) | WebFetched, verified |
| 3 | Program/total expenses %GDP history | FRT 2025 Table 8 | Oct 2025 | data/raw/fiscal/frt_2025.pdf p.16 | pypdf extract |
| 3 | Expenses forward | SEU 2026 Annex 1 A1.7 | 28 Apr 2026 | (SEU Annex 1) | WebFetched, verified |
| 3 | Interest bite (PDC/revenue) | FRT 2025 Table 13 | Oct 2025 | data/raw/fiscal/frt_2025.pdf p.21 | pypdf extract |
| 4 | Federal debt %GDP history | FRT 2025 Table 2 | Oct 2025 | (same PDF p.10) | pypdf extract |
| 4 | Debt levels / net-debt ladder | FRT 2025 Table 15 | Oct 2025 | data/raw/fiscal/frt_2025.pdf p.23 | pypdf extract |
| 4 | Debt forward | SEU 2026 Annex 1 A1.7 | 28 Apr 2026 | (SEU Annex 1) | WebFetched, verified |
| 5 | Instrument stock history | FRT 2025 Table 16 | Oct 2025 | data/raw/fiscal/frt_2025.pdf p.24 | pypdf extract |
| 5 | Gross issuance actuals | Debt Management Report 2024-2025 | 2025 | canada.ca/.../debt-management-report/2024-2025.html | search-verified; canada.ca 403 to WebFetch — flag human re-pull of decimals |
| 5 | Forward issuance plan | SEU 2026 Annex 3 | 28 Apr 2026 | budget.canada.ca/update-miseajour/2026/report-rapport/anx3-en.html | WebFetched, verified |

## Verification flags / open items (for the writer/fact-checker, no fabrication)
1. **canada.ca 403 wall:** FRT 2025 landing/PDF and the Debt Management Report
   2024-2025 both 403 to WebFetch. FRT numbers here are extracted from the locally
   cached `data/raw/fiscal/frt_2025.pdf` (a primary PDF, Tier A by provenance);
   DMR gross-issuance figures ($237.0B bonds, $1,481.2B stock, +$109.3B) are
   search-verified, **Tier B pending a human PDF re-pull** of the DMR before any
   reader-facing decimal call-out.
2. **SEU Annex 1 forecast %GDP decimals** for revenues/expenses: the dollar series
   is verified; the per-year forward %GDP decimals require the SEU Annex 1
   nominal-GDP row (SEU narrative bands given: rev 15.6–16.4%, total exp 17.0–17.8%).
   Pull the GDP row if the chart needs exact forward %GDP points.
3. **No pre-2025 operating/capital back-series exists** — do not invent one.
4. **Vintage-seam discipline** on every %GDP line (FRT actuals vs SEU forecast use
   different GDP denominators; ~41.2% vs ~40.7% at the FY2024-25 boundary).

---

# Follow-up: forecast denominators + issuance series

Compiled 2026-06-02 (follow-up session). Resolves the two blocking items
flagged in "Verification flags / open items" #2 (SEU forward %GDP denominator)
and finalizes Indicator 5 (issuance/stock series).

## ITEM 1 — SEU 2026 nominal-GDP projection (the forward %GDP denominator)

### Provenance / tier
- **Tier A.** SEU 2026 Annex 1 (`anx1-en.html`) WebFetched live this session
  (2026-06-02) — the nominal-GDP level row is in the economic-projection detail
  (the document's economic outlook table; the row label renders as **"Nominal
  GDP level (billions of dollars)"**). The same figures are corroborated
  independently by the **PBO Assessment of the Spring Economic Update**
  (`NT-2627-001-S`, HTML, WebFetched this session,
  `https://www.pbo-dpb.ca/en/publications/NT-2627-001-S--pbo-assessment-spring-economic-update-economic-fiscal-track...`),
  which quotes the SEU's own nominal-GDP track. (The PBO PDF distribution copy
  is a binary stream that WebFetch could not parse — corroboration is from the
  PBO HTML, not the PDF.)
- **Triangulation (third, independent):** I backed the GDP denominator out
  arithmetically from the SEU's OWN two published federal-debt rows (debt $B ÷
  debt %GDP × 100, both from SEU Annex 1 Table A1.7, same vintage). The
  back-out reproduces the stated nominal-GDP figures to within ~0.1% and, when
  fed back through, reproduces the SEU's published debt-%GDP column **exactly**
  (41.1 / 41.5 / 41.8 / 41.9 / 41.8 / 41.6). This closes the vintage-seam risk
  I flagged: numerator and denominator are provably from the same vintage.

### Critical finding — fiscal-year ratio uses the CALENDAR-year-START GDP
The SEU reports nominal GDP on a **calendar-year** basis but computes its
**fiscal-year** %GDP ratios against the **calendar-year that the fiscal year
begins in**. Verified by the back-out (left column = my fiscal-GDP back-out
from the debt rows; right column = SEU stated calendar GDP):

| Fiscal year | Back-out GDP ($B) from debt rows | SEU stated nominal GDP ($B), calendar yr | Calendar yr used |
|---|---|---|---|
| 2025-26 | 3,245.5 | **3,243** | 2025 |
| 2026-27 | 3,371.8 | **3,372** | 2026 |
| 2027-28 | 3,498.6 | **3,496** | 2027 |
| 2028-29 | 3,627.9 | **3,630** | 2028 |
| 2029-30 | 3,771.1 | **3,772** | 2029 |
| 2030-31 | 3,916.8 | **3,917** | 2030 |

So the denominator for FY2025-26 is calendar-2025 nominal GDP ($3,243B), for
FY2026-27 is calendar-2026 ($3,372B), and so on. **Use these stated calendar
figures as the denominator** — they are the SEU's own and reproduce its
published ratios exactly. Do NOT shift them forward a year.

(FY2024-25 is HISTORY, anchored on FRT 2025 Table 2, not on the SEU forecast
segment — so it does not need an SEU GDP denominator. For completeness, the
back-out implies ~$3,112B for the FY2024-25 fiscal denominator, but that is a
derived figure, not an SEU-stated one; do not plot the forecast segment back
into 2024-25.)

### Real GDP growth / GDP inflation context (SEU Annex 1 + PBO HTML, Tier A)
Real GDP growth (%): 2025 1.7 · 2026 1.1 · 2027 1.9 · 2028 1.9 · 2029 1.9 ·
2030 1.8. GDP-inflation context: nominal GDP revised UP vs Budget 2025 (~+$31B/yr
avg over 2025-2029) on higher near-term GDP inflation from higher energy/oil
prices. (Not needed for the %GDP plates; recorded for the narrative.)

### Computed forward %GDP series (numerator / denominator / ratio — fact-checker re-derivable)

All numerators are SEU 2026 Annex 1 Table A1.7 ($B, from the main file above).
Denominator = SEU stated nominal GDP ($B) per the table above. Ratio = numerator
÷ denominator × 100. **FORECAST years only (FY2025-26 → FY2030-31).** History
(through FY2024-25) stays anchored on FRT 2025 Table 2 per the main file.

**Total revenues, % of GDP (forecast):**

| FY | Revenue $B (A1.7) | Nominal GDP $B (SEU) | Rev %GDP (computed) |
|---|---|---|---|
| 2025-26 | 511.5 | 3,243 | 15.77 |
| 2026-27 | 529.6 | 3,372 | 15.71 |
| 2027-28 | 546.8 | 3,496 | 15.64 |
| 2028-29 | 565.9 | 3,630 | 15.59 |
| 2029-30 | 589.8 | 3,772 | 15.64 |
| 2030-31 | 613.7 | 3,917 | 15.67 |

(Inside the SEU's stated 15.6–16.4% revenue band. Note: revenue %GDP DIPS at
the forecast boundary — FRT FY2024-25 actual is 16.6% on the FRT vintage; the
SEU FY2025-26 forecast is 15.8% — partly a genuine projected decline and partly
the FRT-vs-SEU GDP-vintage offset. Flag the seam.)

**Program expenses excl. net actuarial losses, % of GDP (forecast):**

| FY | Program exp $B (A1.7) | Nominal GDP $B (SEU) | Prog-exp %GDP (computed) |
|---|---|---|---|
| 2025-26 | 512.8 | 3,243 | 15.81 |
| 2026-27 | 536.1 | 3,372 | 15.90 |
| 2027-28 | 543.9 | 3,496 | 15.56 |
| 2028-29 | 555.9 | 3,630 | 15.31 |
| 2029-30 | 575.4 | 3,772 | 15.25 |
| 2030-31 | 591.6 | 3,917 | 15.10 |

(Program expense declines from ~15.9% toward ~15.1% as nominal GDP outgrows the
restrained spending track — this is the SEU's fiscal-consolidation arithmetic.)

**For reference — total expenses %GDP (forecast), if a secondary line is wanted:**
547.3→17.59 (24-25, hist FRT 17.8) · 578.3/3243=17.83 · 595.0/3372=17.65 ·
609.9/3496=17.44 · 623.7/3630=17.18 · 645.9/3772=17.12 · 666.9/3917=17.03.
(Inside the SEU's stated 17.0–17.8% total-expense band — confirms the
denominator is right.)

**Federal debt (accumulated deficit), % of GDP (forecast) — RECOMPUTE matches SEU exactly:**

| FY | Debt $B (A1.7) | Nominal GDP $B (SEU) | Debt %GDP (computed) | SEU published |
|---|---|---|---|---|
| 2025-26 | 1,333.9 | 3,243 | 41.13 | 41.1 |
| 2026-27 | 1,399.3 | 3,372 | 41.50 | 41.5 |
| 2027-28 | 1,462.4 | 3,496 | 41.83 | 41.8 |
| 2028-29 | 1,520.1 | 3,630 | 41.88 | 41.9 |
| 2029-30 | 1,576.3 | 3,772 | 41.79 | 41.8 |
| 2030-31 | 1,629.4 | 3,917 | 41.60 | 41.6 |

The exact reproduction of the SEU's published debt-%GDP column is the proof the
denominator is correct and same-vintage. **For the debt %GDP forecast line,
prefer the SEU's own published ratios (41.1 / 41.5 / 41.8 / 41.9 / 41.8 / 41.6)
rather than the recomputed decimals — they are the primary-stated values and
differ only in the second decimal from rounding.**

### Plotting guidance (forecast-dotted segments)
- **Revenues and program expenses:** the SEU publishes the $B numerators but
  NOT a per-year %GDP row for these two; the %GDP forecast is OUR derivation
  (numerator from A1.7, denominator from the SEU GDP row). It is therefore a
  **derived value** — the writer needs BOTH atom cards (the $B level AND the
  GDP denominator) verified before citing any single forecast %GDP point in
  prose. The chart can plot the dotted segment; a prose call-out of e.g.
  "revenues fall to 15.6% of GDP by 2028-29" needs the derivation card.
- **Federal debt:** the SEU publishes the %GDP row directly — use it as-is
  (Tier A, no derivation needed).
- **Vintage seam, all three:** history is FRT 2025 (Oct-2025 GDP vintage),
  forecast is SEU (Apr-2026 GDP vintage). The denominators differ. At the
  FY2024-25/FY2025-26 boundary the debt line steps from FRT 41.2% (actual) to
  SEU 41.1% (forecast) — a ~0.1pp seam that is benign for debt but the revenue
  seam (16.6% → 15.8%) is larger and MUST carry a one-line vintage-seam note so
  the reader does not read the entire drop as a policy event.

## ITEM 2 — Issuance series finalization (outstanding stock by instrument)

### Confirmed recommendation
**OUTSTANDING STOCK by instrument is the primary indicator** (not gross-issuance
flow). Confirmed. Rationale unchanged from the main file: stock is a clean,
additive, end-of-fiscal-year snapshot of the structure of the federal debt;
gross issuance overstates funding need because T-bills roll many times a year.

### Bucket scheme — confirmed 3-bucket (collapsible to 2)
**Marketable bonds (domestic + foreign) / Treasury bills / Retail + other.**
Marketable bonds dominate; T-bills are the short-funding layer; retail is a
vanishing tail (CSB/CPB wound down). For a 2-bucket reader chart, collapse to
**Marketable bonds vs Treasury bills** and drop retail (negligible from
FY2021-22 on).

### Provenance / tier
- **Tier A by provenance.** All values from the locally cached primary PDF
  `data/raw/fiscal/frt_2025.pdf`, **FRT 2025 Table 16** ("Unmatured debt held by
  outside parties"), extracted via pypdf. The canada.ca landing page and dam PDF
  both 403 to WebFetch (documented in the main file); the cached PDF is the
  working copy. **Flag a human PDF re-pull to confirm decimals before any
  reader-facing exact call-out** (consistent with the main file's standing flag).

### Clean multi-year series — FRT 2025 Table 16 ($M, end of fiscal year, HISTORY)

10-year window (FY2015-16 → FY2024-25). Three reader buckets plus the
reconciling Total. **The three buckets do NOT sum to "Total unmatured" —** the
Total also includes Canada Pension Plan bonds, other unmatured debt, and
amortized-cost/own-holdings adjustments. For a clean stacked reader chart use the
three buckets and label the total separately, or use the 2-bucket
(bonds + bills) view.

| FY | Marketable bonds (dom+foreign) $M | Treasury bills $M | Retail debt $M | Total unmatured (outside parties) $M |
|---|---|---|---|---|
| 2015-16 | 487,714 | 138,100 | 5,302 | 640,909 |
| 2016-17 | 504,653 | 136,663 | 5,138 | 654,895 |
| 2017-18 | 545,317 | 110,738 | 4,725 | 668,738 |
| 2018-19 | 585,184 | 134,300 | 1,237 | 733,392 |
| 2019-20 | 612,481 | 151,867 | 497 | 776,906 |
| 2020-21 | 890,450 | 218,800 | 299 | 1,128,808 |
| 2021-22 | 1,045,085 | 187,400 | — | 1,249,957 |
| 2022-23 | 1,053,878 | 201,800 | — | 1,265,040 |
| 2023-24 | 1,102,530 | 267,400 | — | 1,376,822 |
| 2024-25 | 1,192,428 | 285,200 | 4,681 | 1,485,887 |

Notes on the series:
- FY2018-19 → FY2024-25 rows are carried over verbatim from the main file's
  Indicator 5 table (same FRT Table 16). FY2015-16 → FY2017-18 are added here to
  reach a 10-year window; these three years should be **confirmed on the human
  PDF re-pull** — they were read from the same pypdf extract but were not in the
  main file's published subset, so treat the three earliest rows as **Tier A
  pending re-pull confirmation** (slightly lower confidence than the
  already-published FY2018-19+ rows).
- "Marketable bonds" = domestic + foreign combined (the main file splits them:
  FY2024-25 = 1,163,045 domestic + 29,383 foreign = 1,192,428). For the reader
  chart, combined is cleaner; keep the split available as a drill-down.
- Retail debt (CSB/CPB): a wound-down program. The FY2021-22→FY2023-24 zeros and
  the FY2024-25 $4,681M reading reflect program closure and a small residual/
  reclassification; trending to zero. Fold into "other" or drop in the 2-bucket
  view. **Confirm the FY2024-25 $4,681M retail figure on re-pull** — it rises
  from zero, which is unusual for a wound-down program and may be a
  reclassification line in Table 16.
- Recommended display headline, FY2024-25: **marketable bonds $1,192.4B;
  treasury bills $285.2B; retail $4.7B.**

### Forward profile — does one exist?
**Partial — a forward STOCK profile exists for T-bills only; the bond program
is published as a forward FLOW (gross issuance), not a forward stock.**
- **T-bill stock (forward, Tier A — SEU 2026 Annex 3, WebFetched main session):**
  end-FY2025-26 ~$286B; end-FY2026-27 target ~$268B (revised down from $291B
  budgeted). These are forward STOCK points — usable to extend the T-bill stock
  line one-to-two years into FORECAST.
- **Marketable-bond program (forward, Tier A — SEU 2026 Annex 3):** published as
  a gross bond PROGRAM, not an end-year stock: FY2025-26 ~$317B, FY2026-27 $298B.
  This is FLOW, not stock — it CANNOT be plotted on the stock line. To get a
  forward bond STOCK you would need to walk opening stock + gross issuance −
  maturities, which the SEU does not tabulate. **Do not derive a forward bond
  stock; the bond stock series is HISTORY-ONLY.**
- **Conclusion for the chart:** the outstanding-stock-by-instrument chart is
  **history-only for marketable bonds and retail**, with an **optional 1–2 year
  forward dotted segment for the T-bill stock only** (from the SEU Annex 3
  targets). Cleanest honest treatment: plot all three buckets as history through
  FY2024-25 and stop; if a forward element is wanted, add only the T-bill target
  point(s) as a dotted extension, clearly labelled as a stock target, not a
  full forward stack.

### Caveats for fact-checker (Item 2)
- Stock vs flow: the chart is STOCK. The SEU Annex 3 bond numbers are FLOW
  (gross program). Do not mix them onto the stock line.
- FRT Table 16 "held by outside parties" ($1,485.9B FY2024-25 Total) ≠ Debt
  Management Report "domestic market debt stock" ($1,481.2B FY2024-25) — different
  aggregates; pick one basis per chart and label it. The three-bucket reader
  series here is on the FRT Table 16 basis.
- The three earliest rows (FY2015-16 → FY2017-18) and the FY2024-25 retail
  $4,681M figure are the two re-pull-confirmation items.
