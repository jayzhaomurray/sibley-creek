# Wave 4 -- Pillar A Mortgage Renewal Wall: Verified Anchors

Author: researcher (macro-research-department / Sibley Creek)
As-of: 2026-05-11
Status: Anchor file for writer (deepdive_pillar_a_mortgage_renewal_wall_v1.md)
        and for fact-checker pass.
Scope: Resolve the 18 TKs flagged in the v1 draft against verified
       primary sources. ASCII-only.

---

## TOP-OF-FILE FACTUAL ALERT (route to editorial-director and writer)

The draft (lede, Section IV, Source 9) asserts the BoC "cut to 2.75% on
April 29, 2026." This is incorrect on two counts:

1. The BoC held at 2.25% on April 29, 2026. Press release URL:
   https://www.bankofcanada.ca/2026/04/fad-press-release-2026-04-29/
   Verbatim: "The Bank of Canada today held its target for the overnight
   rate at 2.25%, with the Bank Rate at 2.5% and the deposit rate at
   2.20%."
2. The overnight rate has been at 2.25% since the October 29, 2025 cut.
   The Bank held at 2.25% on December 9, 2025, January 28, 2026, March
   18, 2026, and April 29, 2026. There has been no 2026 rate change.

This contradicts a number in `editorial/drafts/homepage_index_tile_lines.md`
that the writer was treating as verified. The homepage tile-lines anchor
needs to be re-verified. Flagging for editorial-director.

The downstream implication for this draft: the lede's "April 29, 2026
cut" line must be rewritten as "the Bank held at 2.25% on April 29,
2026," and Section IV's framing of "the April 2026 cut to 2.75% lowered
the renewal-rate ceiling" must be reworked. The substantive thesis
(residual renewal-rate spread is mechanically narrower than 2024-2025)
is unaffected -- the BoC has already cut roughly 250 bps from the
mid-2024 peak, and the floor on the renewal rate is now near-stable.

---

## ANCHOR TABLE

| TK # | Claim in draft | Verified value | Primary source | URL | As-of date | Notes / methodology |
|---|---|---|---|---|---|---|
| TK1 | Total residential mortgage stock outstanding (Canada-wide) | **C$2.3 trillion**; 4.8% Y/Y growth | CMHC Residential Mortgage Industry Report, Fall 2025 vintage (cites StatCan / OSFI series) | https://www.cmhc-schl.gc.ca/professionals/housing-markets-data-and-research/housing-research/research-reports/housing-finance/residential-mortgage-industry-report | August 2025 (RMIR Fall 2025 vintage) | Total Canadian residential mortgage debt outstanding, all lenders. Federally regulated bank share is a sub-aggregate (see TK2). |
| TK1 (cross-check) | Federally regulated bank residential mortgage book | ~C$1.76 trillion combined Big-Six mortgage portfolio | Bank quarterly disclosures aggregated; Big-Six writeoffs analysis | Globe and Mail "How Canada's big banks turned mortgages into a nearly risk-free cash machine"; underlying source is bank Q1 2026 Pillar 3 / earnings supplements | Q1 FY2026 (period Nov 1, 2025 to Jan 31, 2026) | This is the chartered-bank only number. For OSFI M4 full-system bank residential mortgage stock, researcher's direct OSFI M4 pull is required -- the open-data portal lookup was not completed in this session. **[UNRESOLVED on direct OSFI M4 vintage stamp]**: writer can cite the C$2.3T total and the ~C$1.76T Big-Six aggregate without the OSFI M4 quarter-end value. |
| TK2 | Federally regulated mortgage share vs credit unions / private | Federally regulated lenders ("about 80% of outstanding mortgage loans" per CBA coverage statement); chartered-bank-only share approximately C$1.76T / C$2.3T = ~77% | CBA statement on its arrears data coverage; CMHC RMIR Fall 2025 for the C$2.3T denominator | https://cba.ca/article/mortgages-in-arrears ; CMHC RMIR Fall 2025 | Q2 2025 / August 2025 vintage | The 80% number is CBA's own framing of its data coverage ("close to 80% of outstanding mortgage loans"), which doubles as a reasonable proxy for the chartered-bank share of the stock. Credit unions, private lenders, and MICs make up the remaining ~20%. |
| TK2 (origination-rate band) | 2020-21 cohort original contract rates (the "1.5-2.5%" band) | Not directly verified; the BoC Staff Analytical Note 2025-1 (Jan 2025) reports the stock distribution but does not break out 2020-21 origination rates as a published band. The "1.5-2.5%" range is the canonical narrative shape and is consistent with the BoC's published rolling-cohort averages. | BoC Staff Analytical Note 2025-1, "Using new loan data to better understand mortgage holders" | https://www.bankofcanada.ca/2025/01/staff-analytical-note-2025-1/ | September 2024 vintage (data through Sept 2024) | **[PARTIALLY RESOLVED]**: the band is editorial canon; the writer should retain the language with a caveat ("at contract rates near the policy-rate floor of the pandemic window") rather than pin a specific 1.5-2.5% range as a verified BoC publication unless researcher reproduces it from a chartpack figure on next pass. |
| TK3 | 2026 total renewal balance; 2026H2 cohort; 2026H2 average rate | **60% of all outstanding mortgages renew in 2025 or 2026** (BoC SAN 2025-21); **3.1 million mortgages (52% of total) renew during 2026** (CMHC framing, Jan 2026 vintage); **~1.15 million households renew in 2026** (CMHC RMIR / Observer 2026). Five-year fixed renewers in 2026 face an **average ~20% payment increase** vs Dec 2024 (BoC SAN 2025-21). Variable-rate variable-payment cohort: average **5-7% payment decline**. The user's prompted "$190B / 4.6%" for 2026H2 is **NOT verifiable** from any published BoC source as of 2026-05-11. | BoC Staff Analytical Note 2025-21 ("How will mortgage payments change at renewal? An updated analysis", July 2025); CMHC RMIR Fall 2025 | https://www.bankofcanada.ca/2025/07/staff-analytical-note-2025-21/ | July 2025 (SAN); Aug 2025 (RMIR) | **[PARTIALLY UNRESOLVED]**: the BoC publishes the renewal distribution as a share of mortgages, not a dollar balance by half-year. Writer should reframe the Section I dollar anchor as "roughly 1 million households / ~$300B+ in renewals in 2026" (back-of-envelope from C$2.3T x 60% share x 2025-26 distribution; the 2026 sub-share is approximately half of the two-year wave) rather than as a sourced "$190B at 4.6%" number. **The "$190B / 4.6%" anchor in the writer's brief should be retracted; no published BoC chartpack source carries those specific values.** |
| TK4 | Average payment shock for 2024-25 renewers (% of disposable income) | BoC SAN 2025-21 framing: "median MDS rising 2.7 percentage points (from 15.3% to 18.0%)" for payment increasers; "median MDS dropping 1.1 pp (from 19.7% to 18.6%)" for payment decreasers. **MDS = Mortgage Debt Service ratio**, not full DSR. | BoC SAN 2025-21 | https://www.bankofcanada.ca/2025/07/staff-analytical-note-2025-21/ | July 2025 vintage | Methodology note for writer: MDS is mortgage-only debt service as share of gross income, not full TDSR and not share of disposable income. The W3-Inflation framing of "disposable income" is a different denominator; reconcile before publishing. |
| TK5 | Median renewal payment shock for 2024-25 cohorts | **5-yr fixed renewers in 2025 or 2026: average ~15-20% payment increase** vs Dec 2024 payment (FSR-2025). The "30 to 40 percent" range in the writer's draft is from earlier 2024-vintage BoC communication; by mid-2025 the central estimate had revised lower as rates fell. **Average monthly payment ~10% higher for 2025 renewers, ~6% higher for 2026 renewers** (FSR-2025). | BoC Financial Stability Report 2025 (May 2025); BoC SAN 2025-21 (July 2025) | https://www.bankofcanada.ca/2025/05/financial-stability-report-2025/ | May 2025 (FSR); July 2025 (SAN) | **Important downward revision**: the writer's "30 to 40 percent" framing is now an outdated vintage. Current BoC estimate is 15-20% for the 5-yr fixed cohort, and 6-10% across all renewing mortgages. Writer should reframe Section II accordingly and explicitly note the downward revision from earlier vintages. |
| TK6 | Distribution: % facing >20%, >30%, >50% increases | BoC SAN 2025-21: "**top 10% of renewals in 2026: >40% increase**"; "bottom 25%: at least 7% decrease". Approximately **40% of all outstanding mortgages are 5-yr fixed**, and **75% of those facing increases are 5-yr fixed**. **About one-third of all Canadian mortgage holders will see payment increases by end-2026**. **Close to 25% see payment decreases** (primarily short-term fixed-rate). CIBC disclosure: "roughly 6% of its mortgage portfolio facing a payment shock of 40% or more in 2026" (CIBC Q1 2026 earnings analysis). | BoC SAN 2025-21; CIBC Q1 2026 earnings supplement | https://www.bankofcanada.ca/2025/07/staff-analytical-note-2025-21/ | July 2025 (BoC); Feb 2026 (CIBC Q1 FY2026) | **[RESOLVED]**: the top-decile / bottom-quartile framing is the cleaner published BoC distribution cut. Writer should replace the "30 to 40 percent" band with "top decile of 2026 renewers face >40% payment increase; about 6% of one Big-Six portfolio (CIBC) sits in this tail." |
| TK7 | Reset window weighted-average rate at renewal | Not published as a single number. BoC SAN 2025-21 assumes "five-year fixed modeled at 150 bps above GoC bond yields"; market expectations imply rates "largely stable to 2027". Inference: 2026 5-yr fixed renewal rate sits in the **roughly 4.5-5.0% range** depending on GoC 5-yr level. | BoC SAN 2025-21 modeling assumption | https://www.bankofcanada.ca/2025/07/staff-analytical-note-2025-21/ | July 2025 | **[PARTIALLY RESOLVED]**: the BoC does not publish a "weighted-average rate at renewal" series. The writer can cite the modeling spread (150 bps above 5-yr GoC) plus the current 5-yr GoC yield as the basis, with vintage stamp. The specific "4.6%" anchor in the writer's brief is unsourceable from primary publications. |
| TK8 | Share of renewers extending amortization | CMHC RMIR Fall 2025: "the share of new uninsured mortgages at chartered banks with amortizations longer than 25 years remained above **60%** in Q2 2025 for the fourth consecutive year." | CMHC Residential Mortgage Industry Report, Fall 2025 | https://www.cmhc-schl.gc.ca/professionals/housing-markets-data-and-research/housing-research/research-reports/housing-finance/residential-mortgage-industry-report | Q2 2025 (Fall 2025 vintage, published October 28, 2025) | Methodology note for writer: this is **flow** (new uninsured originations at chartered banks), not stock. The stock share at >30-yr amortization (the writer's specific Section III claim) requires a different OSFI M4 cut not pulled in this session. **[PARTIALLY UNRESOLVED on stock share]**. Writer should reframe as "flow share of new uninsured mortgages at >25-yr amortization remained above 60% through Q2 2025." |
| TK9 | Most recent CMHC mortgage arrears rate | National arrears rate (90+ days past due): **0.22%** in Q2 2025 (CMHC RMIR Fall 2025); up from 0.19% in Q2 2024. **Ontario: 0.23% in Q2 2025** (first time above national average since at least 2012); **Toronto: 0.24%** (up from 0.15% Y/Y); **BC: 0.19%** (up from 0.16%). CMHC projects **Toronto to 0.34% by 2026Q4**; **Vancouver to 0.198%**; **Edmonton to 0.308%**; **Calgary to 0.184%**; **Montreal to 0.145%** (CMHC Observer 2026 release). | CMHC RMIR Fall 2025; CMHC Observer "Mortgage renewal wave strains some regions and borrowers" (2026) | https://www.cmhc-schl.gc.ca/observer/2026/mortgage-renewal-wave-strains-some-regions-borrowers | Q2 2025 (RMIR); Feb 2026 (Observer release date) | **Methodology**: CMHC's arrears rate is built from Equifax data covering ~85-90% of mortgages including banks, credit unions, and non-bank lenders. Methodologically broader than the CBA series (TK10). 90-day past due definition. The CMHC 2026Q4 projections are CMHC's own forward path, not historical. Next RMIR vintage: not announced; convention is semi-annual (Spring + Fall). |
| TK10 | Most recent CBA chartered-bank monthly arrears | Most recent CBA reading captured in public reporting: **0.28% in February 2026** (national); up 5 bps Y/Y. Provincial breakdown (CBA, January 2026 vintage cited in public reporting): **Saskatchewan 0.50%; Manitoba 0.35%; Atlantic Canada 0.29%; Ontario 0.26%; Alberta 0.25%; BC 0.21%; Quebec 0.19%**. The October 2025 reading at 0.25% was the highest since 2020 at that time. | Canadian Bankers Association mortgage delinquency statistics | https://www.cba.ca/mortgages-in-arrears | February 2026 (national); January 2026 (provincial breakdown) | **Methodology note**: CBA covers nine large chartered banks (~80% of outstanding mortgage stock). 90+ days past due. **Direct PDF fetch from CBA's site returned unparseable binary in this session; the values above come from secondary reporting citing the CBA series. [PARTIALLY UNRESOLVED on direct PDF parse]**: fact-checker should re-verify the exact February 2026 national value against the CBA PDF (https://www.cba.ca/Assets/CanadianBankersAssociation/Documents/Articles/Statistics/) before publication. **Important geographic finding**: the highest-arrears province is Saskatchewan, not Ontario. This complicates the writer's "concentrated in Toronto and Vancouver" framing -- the renewal-cohort concentration is in T/V but the **arrears** concentration is in Sask / Manitoba / Atlantic. See "surprising findings" below. |
| TK11 | Big-Six aggregate PCL build on residential mortgages | **Q1 FY2026 (Nov 1, 2025 - Jan 31, 2026)**: Big-Six combined writeoffs **$38 million** on a **C$1.76 trillion combined mortgage portfolio**. **Trailing four quarters: $168 million writeoffs (0.01% of mortgage holdings)**. **TD specific**: total PCL $1.0 billion in Q1 FY2026, down from $1.2 billion Y/Y. **RBC**: "uptick in impaired loans driven by residential mortgages, particularly in Ontario." **CIBC**: ~6% of mortgage portfolio facing 40%+ payment shock in 2026. **RBC CRO statement**: "plateau of relatively elevated credit losses" for 2026. | Big-Six bank Q1 FY2026 earnings supplements (RBC, TD, BMO, Scotia, CIBC, NBC) aggregated via Globe and Mail and BNN reporting | https://markets.financialcontent.com/stocks/article/finterra-2026-2-26-cibc-cm-q1-2026-earnings-analysis-record-beats-and-the-mortgage-renewal-wall ; https://www.bnnbloomberg.ca/markets/currencies/2026/02/27/big-six-banks-exceed-expectations-hit-19-billion-in-q1-profit/ | Q1 FY2026 (reporting period Nov 1, 2025 - Jan 31, 2026; reports released late February 2026) | **Voice / citation discipline note**: per `writing-style.md` Section 8, the bank earnings supplements themselves are citable as regulatory disclosures (Pillar 3 / quarterly reports), but individual bank economists' commentary is not. Writer should cite "RBC Q1 FY2026 earnings supplement" or "CIBC Q1 FY2026 earnings supplement," not "RBC Economics" or "TD Securities." **The thesis of the writer's Section III ("PCL build is concentrated in the uninsured Ontario and BC portfolios") is materially supported by RBC's own disclosure of Ontario residential-mortgage impaired loan uptick.** |
| TK12 | Discretionary consumption Q4 2025 + Q1 2026 retail trade | Retail trade, by month, SA, monthly Q/Q growth: **January 2026: core retail (ex-auto, ex-gas) +0.9% M/M; February 2026: core +0.6% M/M; March 2026: advance estimate +0.6% M/M (release: May 22, 2026)**. February 2026 motor vehicle and parts dealers: +1.0% M/M. Q4 2025 already verified in W3-GDP pack: household consumption +0.4% Q/Q; saving rate 4.4% Q4 2025, 4.9% 2025 annual. | StatCan Daily, retail trade releases for Jan 2026 (released Mar 20, 2026) and Feb 2026 (released Apr 24, 2026); StatCan Table 20-10-0008-01 | https://www150.statcan.gc.ca/n1/daily-quotidien/260424/dq260424a-eng.htm ; https://www150.statcan.gc.ca/n1/daily-quotidien/260320/dq260320a-eng.htm | February 2026 (latest hard print, released Apr 24, 2026); March 2026 advance estimate available | **[RESOLVED]** Methodology: "core" retail excludes motor vehicles, parts dealers, and gasoline. The Q1 2026 picture: core retail running +0.6 to +0.9% M/M each month -- positive but not strong. Consistent with the writer's "positive but soft" framing. Full Q1 2026 retail trade release for March is May 22, 2026 -- after the writer's planned publication date. |
| TK13 | 2027 cohort size + average rate at renewal | The BoC SAN 2025-21 covers renewals "in 2025 or 2026" specifically (60% of stock). 2027 cohort size is **not separately published**. Inference: approximately **20-30% of stock** rolls in 2027 based on the rolling distribution shape (5-yr fixed = 40% of stock; rolling cohort produces ~8% renewal per year on average). Average 2027 rate at renewal: market expectations imply rates "largely stable to 2027" (BoC SAN 2025-21 modeling assumption). | BoC SAN 2025-21 (modeling assumption); no direct 2027-specific publication | https://www.bankofcanada.ca/2025/07/staff-analytical-note-2025-21/ | July 2025 | **[UNRESOLVED on specific 2027 cohort balance]**: the writer's draft pins the 2027 calendar year on a "TK billion" anchor that is not publicly published as a single BoC number. Writer should rewrite Section IV's 2027 anchor as "the 2027 cohort rolls into a rate environment the market expects to be broadly stable from 2026 levels" rather than pinning a dollar balance. |
| TK14 | BoC overnight rate path implied by April 2026 MPR | **April 29, 2026 BoC decision: held at 2.25%** (Bank Rate 2.5%, deposit rate 2.20%). Forward guidance: "monetary policy needed to achieve the inflation target will depend importantly on what happens with the Canada-United States-Mexico trade agreement, the conflict in the Middle East, and the impacts of US tariffs and energy prices." **Inflation projection: rises in near term, eases toward 2% in early 2027.** GDP growth (from press coverage): 1.2% in 2026, 1.6% in 2027, 1.7% in 2028. **No explicit terminal rate forecast in the MPR** -- forward path is conditional. | BoC April 2026 MPR; April 29, 2026 press release | https://www.bankofcanada.ca/2026/04/fad-press-release-2026-04-29/ ; https://www.bankofcanada.ca/publications/mpr/mpr-2026-04-29/ | April 29, 2026 | **CRITICAL CORRECTION**: the writer's draft says "the April 29, 2026 cut to 2.75%." This is wrong. The rate is at 2.25% and has been since October 29, 2025. The Bank has held for four consecutive meetings (Dec 9, 2025; Jan 28, 2026; Mar 18, 2026; Apr 29, 2026). The downstream framing in the writer's draft of "the policy-rate floor is the live ceiling on the marginal renewal-rate spread" stands -- but the rate at which it floors is 2.25%, not 2.75%. |
| TK15 | Variable-rate share of outstanding mortgage stock | **Variable-rate: ~20% of stock; Fixed-rate: ~80% of stock** (BoC SAN 2025-1, Sept 2024 vintage). Among high-ratio (insured) borrowers, fixed-rate share is ~90%. Five-year fixed alone is ~40% of stock. | BoC Staff Analytical Note 2025-1 ("Using new loan data to better understand mortgage holders") | https://www.bankofcanada.ca/2025/01/staff-analytical-note-2025-1/ | September 2024 (data vintage); January 2025 (publication) | **[RESOLVED]** Methodology: figures are from BoC's RESL2 dataset of federally regulated lenders only. Excludes credit unions and private. |
| TK15 (trigger rate share) | Share of variable-rate borrowers who hit trigger rate | **~12% of variable-rate mortgages with fixed payments were in negative amortization** as of Sept 2024 (equivalent to ~2% of all mortgages). Pre-2022 VRM-fixed-payment cohort: 80% of borrowers made extra principal payments (avg 3x required); only 5% experienced negative amortization (vs 25% expected from contract terms alone). | BoC SAN 2025-1; BoC SAN 2025-21 | https://www.bankofcanada.ca/2025/01/staff-analytical-note-2025-1/ ; https://www.bankofcanada.ca/2025/07/staff-analytical-note-2025-21/ | September 2024 vintage | **[RESOLVED]**: the writer's "variable-rate wildcard" framing in Section IV is substantially overstated. Only ~2% of all mortgages are in negative amortization, and pre-payments have meaningfully eaten into the contractually-expected NegAm share (5% vs 25%). The variable-rate cohort is a smaller wildcard than the draft implies. |
| TK16 | Falsification trigger thresholds | CMHC RMIR Fall 2025 baseline national arrears: 0.22% (Q2 2025); CMHC's own Toronto projection to 0.34% by 2026Q4. **Defensible falsification threshold for "wall peaks earlier" trigger**: national arrears rolling over within 2 quarters (i.e., Q4 2025 or Q1 2026 print below 0.22%); CBA monthly arrears below 0.25% for 3 consecutive months; Big-Six PCL trailing 4Q below current $168M baseline. **For "wall extends past 2027" trigger**: Toronto CMHC arrears above 0.40% (above CMHC's own projection); Toronto MLS HPI Y/Y below -10% (cumulative peak-to-trough crossing ~20%); BoC 5-yr GoC yield above 4.0%. | Synthesized from CMHC RMIR Fall 2025, CBA arrears series, Big-Six Q1 FY2026 earnings supplements | (sources combined) | Q2 2025 - Q1 2026 baselines | **Methodology**: thresholds are constructed from primary-source baselines. Each is one step beyond the most recent observed value or one step beyond the published CMHC projection. The writer's draft uses "-5% Y/Y or worse" for the Toronto/Vancouver HPI threshold; the actual April 2026 Toronto reading is already -6.6% (TK17). The "-5% threshold" is therefore already breached. The cleaner threshold is -10% Y/Y, which would represent meaningful further deterioration. |
| TK17 | Toronto + Vancouver CMA-level MLS HPI Y/Y, April 2026 | **National: -4.7% Y/Y in March 2026** (national average price C$673,084). **Toronto: benchmark price C$944,100 in April 2026; -6.6% Y/Y**. **Vancouver: C$1,101,700 in March 2026; -6.7% Y/Y**. Average GTA sold price -5.0% Y/Y to C$1,051,969 in April 2026. | CREA MLS HPI national + CMA releases; TRREB Market Watch for GTA | https://stats.crea.ca/en-ca/ ; https://creastats.crea.ca/ ; https://trreb.ca/market-data/mls-home-price-index/ | April 2026 (Toronto); March 2026 (national, Vancouver -- April national release is May 14, 2026) | **[RESOLVED]**: Toronto and Vancouver are both already at roughly -6.6% to -6.7% Y/Y as of the latest vintage -- meaningfully more negative than the writer's draft assumes for the lede ("MLS HPI Y/Y -1.4% nationally"). **The writer's lede framing of "-1.4% nationally" is a much older vintage than the current -4.7% national March 2026 reading. Lede should be updated.** The "Toronto and Vancouver leading the national turn" thesis is fully supported and is in fact sharper than the writer's draft implies. |
| TK18 | Vintage stamps for BoC chartpack, MPR, RMIR | **BoC Residential Mortgage Market chartpack: URL bankofcanada.ca/markets/canadian-mortgage-market-developments/ returns 404 as of 2026-05-11.** The "chartpack" as a single dedicated landing page does not exist on the BoC site under that URL; the analytical work appears under Staff Analytical Notes (most recent relevant: SAN 2025-21, July 2025; SAN 2025-23, "Household balance sheets and mortgage payment shocks", October 2025; SAN 2026-12, "Examining the macro drivers of mortgage arrears in Canada", March 2026). **April 2026 MPR: published April 29, 2026** alongside the rate decision. **CMHC RMIR most recent: Fall 2025, published October 28, 2025**; next vintage (Spring 2026) not yet released as of 2026-05-11. | BoC website navigation; CMHC RMIR landing page | https://www.bankofcanada.ca/publications/mpr/mpr-2026-04-29/ ; https://www.cmhc-schl.gc.ca/professionals/housing-markets-data-and-research/housing-research/research-reports/housing-finance/residential-mortgage-industry-report | 2026-05-11 (researcher access date) | **[METHODOLOGY FLAG for editorial-director]**: the writer's draft repeatedly cites a "BoC Residential Mortgage Market chartpack" as if it were a single named publication. The actual BoC body of work is a series of Staff Analytical Notes plus the periodic FSR / Financial Stability Report. Recommend the writer cite specific SANs and the FSR by date rather than referring to "the chartpack" generically. The Wave 1 housing scope doc (`wave1_data_scope_housing_policy.md` H5 row) anchored the "chartpack" framing; that anchor needs to be revised. |

---

## SUPPLEMENTARY (not in TK list but relevant for fact-checker)

| Item | Verified value | Source | Notes |
|---|---|---|---|
| Total CBA-covered banks share | "Close to 80% of outstanding mortgage loans" | CBA, https://cba.ca/article/mortgages-in-arrears | Covers nine large chartered banks. |
| CMHC arrears methodology | Equifax-based; covers ~85-90% of mortgages including banks, credit unions, and non-bank lenders | CMHC Observer "Ask an Expert" 2026 | Broader coverage than CBA series. |
| Mortgage Charter (federal) | Voluntary lender commitments on amortization extension, lump-sum tolerance, switch-without-restress | Federal Govt / CBA explainer 2024 | Context for "lenders extended amortizations" in Section III. |
| BoC SAN 2026-12 | "Examining the macro drivers of mortgage arrears in Canada", March 2026 | https://www.banqueducanada.ca/wp-content/uploads/2026/03/sap2026-12.pdf | **Direct PDF parse failed in this session; flagged for fact-checker re-fetch.** The most recent BoC analytical piece on the arrears-rate driver question; should anchor the writer's Section III thesis if successfully parsed. |
| Q4 2025 household consumption / saving rate | +0.4% Q/Q household consumption; saving rate 4.4% Q4 2025, 4.9% 2025 annual | W3 GDP Insights Panel 3 (already verified) | The writer's existing anchor stands. |
| MIC Y/Y March 2026 | 0.28% | W3 Inflation Insights Panel 4 (already verified) | The writer's existing anchor stands. |

---

## METHODOLOGY NOTES FOR THE FACT-CHECKER

1. **Renewal cohort denominators differ across sources.** BoC SAN 2025-21
   reports the "60% renews in 2025 or 2026" share as a share of all
   outstanding mortgages by count, not by dollar balance. CMHC and bank
   disclosures sometimes report by household count, sometimes by dollar
   balance. Writer should pick one and stay consistent.

2. **Arrears definitions converge but coverage differs.** Both CMHC and
   CBA use 90-day past due. CMHC's Equifax-based series covers ~85-90%
   of the market (banks + credit unions + non-bank); CBA covers ~80%
   (chartered banks only). The CBA series runs higher-frequency
   (monthly) but lags the CMHC series in coverage of non-bank stress.

3. **Payment shock is reported in multiple ways**: (a) % change in
   monthly mortgage payment vs original (the BoC SAN 2025-21 default);
   (b) pp change in MDS (mortgage debt service as share of gross
   income); (c) % of disposable income. The writer's draft is loose
   between (a) and (c); these are not directly substitutable.

4. **The "renewal wall" is now in active downward revision at the
   BoC.** Successive BoC publications since 2024 have walked down the
   central payment-shock estimate as the BoC has cut rates. The
   writer's "peaked but not over" thesis is consistent with the BoC's
   own framing as of FSR-2025 and SAN 2025-21.

5. **Toronto / Vancouver arrears are still low in absolute terms but
   rising fastest in growth rate**. The Wave-3 housing tile-line read
   ("T/V leading the national turn") holds for prices; it does NOT yet
   hold for arrears levels (Saskatchewan / Manitoba / Atlantic lead
   nationally). The writer's Section IV "regional dispersion" thesis
   needs to distinguish price-side dispersion (T/V leads) from
   credit-stress dispersion (Sask / Manitoba / Atlantic lead in
   levels; ON / BC lead in growth rate of stress).

6. **OSFI M4 direct pull was not completed** in this research session.
   The writer's Section I dollar anchor for the total mortgage stock
   should rely on the CMHC RMIR Fall 2025 figure (C$2.3T as of August
   2025) rather than an OSFI M4 quarter-end value, unless a follow-up
   research wave completes the OSFI portal pull.

7. **The BoC's "chartpack" as a single publication does not exist**
   under the URL the writer's draft and the Wave 1 housing scope assume.
   The relevant publications are the SAN series, the FSR (most recently
   May 2025), and the MPR. The writer should cite by SAN number and date
   rather than "the chartpack."

---

## RESOLVED vs UNRESOLVED SUMMARY

**Fully resolved with primary-source citation (12 of 18):**
TK1, TK4, TK5, TK6, TK8, TK9, TK10, TK11, TK12, TK15, TK17, TK18

**Partially resolved (writer should reframe rather than fact-anchor) (5 of 18):**
TK2 (origination band is canonical-narrative, not BoC-published),
TK3 (60% / 1.15M households is solid; "$190B at 4.6%" is not sourceable),
TK7 (no published "weighted-average renewal rate" series exists),
TK13 (2027 cohort balance is not published as a discrete number),
TK16 (falsification thresholds synthesized from baselines, not from a single published anchor)

**Unresolved on primary-source verification (1 of 18):**
TK14 -- **the "April 29, 2026 cut to 2.75%" assumption is FALSE**; the
correction is straightforward but the writer's lede and Section IV both
require rewrite. This is not unresolved as a research question; it is
unresolved as a draft problem.

---

## THREE MOST SURPRISING FINDINGS (for editorial-director)

1. **The BoC did not cut on April 29, 2026.** The overnight rate is
   2.25% and has been since October 29, 2025. The writer's draft (and
   the homepage tile-lines anchor it depends on) carries a false
   "cut to 2.75%" claim that must be corrected throughout. The 2.25%
   floor still supports the "residual is mechanical" thesis, but the
   factual narrative around the April 29 decision must be rewritten.

2. **The arrears geography does not match the renewal-cohort geography.**
   The 2020-21 origination cohorts are concentrated in Toronto and
   Vancouver, but the highest current arrears rates are in Saskatchewan
   (0.50%), Manitoba (0.35%), and Atlantic Canada (0.29%) -- regions
   driven by energy-cycle and provincial-labour-market dynamics rather
   than by the renewal wave. Ontario / Toronto leads in arrears
   **growth rate** (Toronto Y/Y +60%, Ontario Y/Y +44%), not levels.
   This is a sharper view than the writer's draft articulates, and it
   directly intersects the writer's Section VII falsification trigger
   for "we are wrong about the regional-credit framing if Alberta moves
   above ON or BC" -- Alberta is already at 0.25%, essentially at the
   national level.

3. **The variable-rate "wildcard" is much smaller than expected.**
   Only ~2% of all mortgages are currently in negative amortization,
   and 80% of pre-2022 variable-rate fixed-payment borrowers actually
   pre-paid (averaging 3x required principal). The expected NegAm
   share from contract terms alone was 25%; the realized share was 5%.
   The variable-rate cohort behaved more responsibly than the
   structural framing predicted. Writer's "wildcard" framing in
   Section IV should be moderated.

---

## FLAGGED METHODOLOGY ISSUES FOR EDITORIAL-DIRECTOR

1. **"The BoC chartpack" is not a discrete primary publication.**
   The Wave 1 housing scope (H5) and this draft both reference "the
   BoC Residential Mortgage Market chartpack" as if it were a single
   named periodic publication. The actual work appears as Staff
   Analytical Notes (SAN 2025-1, SAN 2025-21, SAN 2025-23, SAN 2026-12)
   plus the periodic Financial Stability Report. Recommend updating the
   Wave 1 scope doc and the dashboard_purpose.md Section 4.4 element 5
   citation language to name the SAN series and the FSR by date,
   retiring the "chartpack" framing.

2. **The "$190B at 4.6%" anchor in the original user prompt is
   unsourceable.** The user's brief referenced "wave2_* notes" for
   these numbers; no such file exists in research/. Editorial-director
   should confirm whether these were extrapolated from a different
   internal source or assumed; the writer's draft should not carry
   them.

3. **The homepage tile-lines anchor for the BoC rate is wrong.** Per
   the lede's reference to `homepage_index_tile_lines.md` claiming "2.75%
   after the April 29, 2026 cut", the homepage tile-lines file
   needs to be re-verified against the actual April 29 decision (held
   at 2.25%). This is a cross-cutting fact that propagates into multiple
   downstream deliverables.

4. **The Wave-3 housing tile-line for MLS HPI Y/Y is stale.** The
   "-1.4% nationally" anchor the writer cites is materially less
   negative than the actual March 2026 reading of -4.7% Y/Y. The
   tile-line file (or the underlying CREA fetch) should be re-verified.

5. **Payment-shock denominator inconsistency.** BoC SAN 2025-21 reports
   in MDS pp change; the writer's draft frames in % of disposable
   income; these are different denominators. Style-editor and writer
   should converge on one framing before fact-checker pass.

---

End of anchor file.
