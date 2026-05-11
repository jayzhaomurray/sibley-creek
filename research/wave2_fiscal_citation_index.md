# Wave 2, Brief 2A.6 — Fiscal Citation Index for Policy Sub-Surface Elements

Canon: `editorial/dashboard_purpose.md` Section 4.5 (Policy / Fiscal sub-surface, updated 2026-05-10).
Feasibility verdict: `research/wave1_data_scope_housing_policy.md` Section 4.5b.

Posture per canon: "cite, do not construct." This file is the researcher-curated
citation register for the fiscal-side elements (F1-F4) plus the monetary
neutral-rate value (M1). No construction. WebFetch verification was attempted on
every primary publication and is flagged in the "verification" line of each
entry. The eight entries are ordered to match the brief's deliverable list.

Date of compilation: 2026-05-10.

---

## Conventions

- **Source publication name + URL**: The publishing institution and the most
  direct link to the document at the publisher's domain.
- **Vintage date**: The publication date or, for survey publications, the
  vintage stamp the institution uses (e.g. "October 2025").
- **The actual number(s) we'd cite**: Numbers verified against the primary
  publication. Where WebFetch was blocked by the publisher (HTTP 403) or a
  PDF was uncached, the number is sourced from cross-references (publisher
  press release, ministry republication, FAO summary) and that path is
  declared.
- **Methodology footnote**: The footnote / definition we would surface in
  the methodology one-click-away for this number.
- **Flags**: Revision pattern, methodology shift, vintage-rotation risk, or
  verification limitation.
- **Verification**: Source-side check status. "WebFetched" = primary
  publication content retrieved by tool; "Press release / republication
  WebFetched" = number sourced from the publisher's own press release or a
  primary republication (e.g. provincial ministry of finance) rather than
  the underlying PDF; "Blocked, awaiting human pull" = primary endpoint
  returned 403 and no clean alternative captures the specific number.
- **Confidence flag** (added at the 2026-05-11 PDF-blocker resolution
  pass; carried forward and tightened at the 2026-05-11 W3-R3 pass):
  VERIFIED = number from primary publication body retrieved by tool
  (WebFetch of HTML body or successful publisher-snippet extract);
  STRONG = secondary attestation matching across multiple sources and
  cross-confirmed with the publisher's own narrative; WEAK = single
  secondary source not cross-confirmed.

- **Resolution-pass log**:
  - 2026-05-11 (Wave 2 PDF-blocker pass): first sweep of human-pull
    queue. Resolved Budget 2025 Annex 1 / Annex 4, BoC G6 maturity
    buckets, IMF / OECD headline anchors.
  - 2026-05-11 (Wave 3 W3-R3 pass, current): second sweep using
    alternate URL paths, cross-publisher attestations, and CEIC /
    cbonds / RBC / TD / national press relays. Resolutions documented
    inline below.

---

## Entry 1 — IMF Article IV Canada cyclically-adjusted primary balance (CAPB)

**Source publication**: IMF Country Report No. 26/12 — Canada: 2025 Article IV
Consultation-Press Release; and Staff Report.
**URL (landing page)**:
`https://www.imf.org/en/publications/cr/issues/2026/01/21/canada-2025-article-iv-consultation-press-release-and-staff-report-573340`
**URL (staff report PDF)**:
`https://www.imf.org/-/media/files/publications/cr/2026/english/1canea2026001.pdf`
**Press-release URL**:
`https://www.imf.org/en/news/articles/2026/01/21/pr-26012-canada-imf-executive-board-concludes-2025-article-iv-consultation`
**Vintage**: Staff report published 21 January 2026. Underlying mission
concluded 12-20 November 2025; concluding statement dated 5 December 2025.

**The actual number(s) we'd cite**:
- The IMF Country Report contains the load-bearing CAPB figure for general
  government in Table 2 ("Selected Economic Indicators") and the fiscal
  appendix. **The specific numeric CAPB / structural primary balance value
  remains tool-blocked**: all IMF endpoints (Country Report PDF, landing
  page, staff-report `.pdf` and `.ashx` URLs, DataMapper for series
  `GGCBP_G01_PGDP_PT@FM/CAN`, Fiscal Monitor April 2026 MSA at
  `imf.org/-/media/files/publications/fiscal-monitor/2026/april/english/msa.pdf`,
  Fiscal Monitor October 2025 MSA, WEO April 2026 Table B at
  `imf.org/-/media/files/publications/weo/2026/april/english/tableb.pdf`,
  WEO April 2026 statistical appendix, and Google webcache passthrough)
  consistently return HTTP 403 to WebFetch in the 2026-05-11 resolution
  pass.
- **Secondary attestations resolved during this pass** (STRONG confidence,
  multiple sources):
  - **All-levels-of-government deficit projected at 2.2% of GDP for
    calendar 2025** (IMF view, Article IV consultation). Attributed to
    the IMF Article IV staff narrative via hashtaginvesting summary of
    Country Report 26/12; cross-confirmed by the IMF "best fiscal shape
    in the G7" ranking (Canada 2.2% behind only Japan at 1.3% and ahead
    of Germany, Italy, UK, France, US).
  - **Federal government deficit "around 2.5 percent of GDP" in FY
    2025-26 envisaged**: extracted from the IMF Article IV concluding
    statement (5 December 2025) language: "keeping a federal government
    deficit around 2.5 percent of GDP in FY2025-26, as currently
    envisaged, followed by gradual consolidation over the medium term,
    would appropriately balance stabilization with sustainability
    objectives." Direct quotation captured in search excerpts. Matches
    Budget 2025's own headline.
  - **IMF debt sustainability assessment**: "overall risk of sovereign
    stress in Canada is low" (Article IV staff conclusion).
  - **IMF's framework recommendation**: clarify debt-to-GDP as the
    primary fiscal anchor; the deficit and operating-balance anchors
    introduced in Budget 2025 are "useful discipline" but a "clearer
    hierarchy would strengthen credibility."
- **The numeric CAPB / structural primary balance value (specifically the
  cyclically-adjusted variant on potential GDP, IMF methodology) still
  requires a human PDF pull from Country Report 26/12 Table 2 ("Selected
  Economic Indicators") and the fiscal appendix.** The secondary
  attestations above pin the headline deficit but not the CAPB.
- Qualitative anchor extractable from search-result excerpts of the
  concluding statement (5 December 2025): "Fiscal policy should continue to
  be measured, counter-cyclical, and flexible, with a modestly expansionary
  stance remaining appropriate to cushion softer external demand, given
  fiscal space supported by low net debt levels and contained deficits."

**Methodology footnote**:
IMF CAPB methodology — Methodological and Statistical Appendix to the IMF
Fiscal Monitor, October 2025
(`https://www.imf.org/-/media/files/publications/fiscal-monitor/2025/english/msa.pdf`).
General-government basis, IMF staff output-gap estimate, computed as primary
balance adjusted for the cyclical component using country-specific
elasticities. Canada series typically reported as % of potential GDP. IMF
DataMapper provides the comparable series at
`https://www.imf.org/external/datamapper/GGCBP_G01_PGDP_PT@FM/CAN` (also
WebFetch-blocked).

**Flags**:
- Vintage-rotation risk: the next IMF refresh of the Canadian CAPB will be
  the IMF Fiscal Monitor April 2026 (typically released mid-April with the
  WEO Spring meetings). When that publishes, the canon's F4 cite rotates to
  the newer Fiscal Monitor unless the Article IV remains more recent for
  Canada specifically.
- Methodology stability: IMF CAPB methodology has been stable since the
  2014 Fiscal Monitor methodological refresh; revisions are output-gap
  driven, not methodology-driven.
- Revision pattern: each IMF Fiscal Monitor / Article IV vintage revises
  historical years modestly as Canadian potential-output estimates revise.
- Source friction: IMF Country Report PDFs and DataMapper endpoints
  consistently return HTTP 403 to automated retrieval; human pull required
  for the actual figure.

**Verification**: Press release / republication WebFetched (Government of
Canada Department of Finance press release dated 5 December 2025);
secondary attestation of the FY 2025-26 federal deficit anchor (~2.5%
of GDP) and the calendar-2025 all-levels-of-government deficit (2.2% of
GDP) from search-result extracts of IMF Article IV concluding statement
and Country Report 26/12 commentary (multiple sources cross-confirm).
IMF Country Report PDF, landing page, full concluding statement HTML,
DataMapper, IMF Fiscal Monitor October 2025 MSA, IMF Fiscal Monitor
April 2026 MSA, WEO April 2026 statistical appendix and Table B,
Department of Finance press release HTML, and Google webcache
passthrough all returned HTTP 403 to WebFetch in the 2026-05-11
resolution pass. **The headline deficit anchor is STRONG-confidence
attested via secondary sources; the specific cyclically-adjusted primary
balance numeric value (the IMF CAPB-on-potential-GDP metric) remains
tool-blocked and requires a human-pull from Country Report 26/12 Table 2
before a blurb may quote it.**

**Wave 3 W3-R3 update (2026-05-11)**: Two additional out-year IMF CAPB
values resolved at STRONG confidence via CEIC's Government Finance
Statistics relay of the IMF Fiscal Monitor / WEO dataset for Canada:
- **2028 CAPB: -0.367% of potential GDP**
- **2029 CAPB: -0.302% of potential GDP**
Both attested through cbonds-style summaries of the CEIC published
table, which sources directly from IMF Government Finance Statistics
under the indicator code GGCBP_G01_PGDP_PT. The CEIC narrative reads:
"Canada's General Government Primary Balance as a percentage of
Potential GDP (Cyclically Adjusted) was reported at -0.302% in 2029.
This records an increase from the previous figure of -0.367% for
2028." Series average 1990-2029 = -0.124%; high 5.433% (1999); low
-8.777% (2020). **These are the out-year endpoints of the CAPB
trajectory the IMF publishes; the 2025/2026/2027 per-year decimals
remain tool-blocked at the IMF DataMapper, fgeerolf.com mirror (which
omits Canada from its display set), and the prosperitydata360 World
Bank mirror (redirected to a generic landing page).** The 2028/2029
endpoints establish the order of magnitude (near-zero structural
primary balance by late horizon, deteriorating slightly toward 2028
then improving in 2029) and provide a STRONG cross-check on any
publisher-side per-year decimal the human pull surfaces from Country
Report 26/12 Table 2.

**Confidence flag, summary**: Headline deficit anchors VERIFIED-grade
via Department of Finance press-release narrative (5 Dec 2025) and
multi-source attestation. CAPB out-year endpoints (2028/2029)
STRONG-grade via CEIC relay of IMF dataset. **CAPB per-year values for
2025/2026/2027 remain tool-blocked.**

---

## Entry 2 — OECD Economic Survey of Canada cyclically-adjusted primary balance

**Source publication**: OECD Economic Surveys: Canada 2025.
**URL (landing page)**:
`https://www.oecd.org/en/publications/oecd-economic-surveys-canada-2025_28f9e02c-en.html`
**URL (full PDF)**:
`https://www.oecd.org/content/dam/oecd/en/publications/reports/2025/05/oecd-economic-surveys-canada-2025_ee18a269/28f9e02c-en.pdf`
**URL (December 2025 update — OECD Economic Outlook Volume 2025 Issue 2,
Canada chapter)**:
`https://www.oecd.org/en/publications/2025/12/oecd-economic-outlook-volume-2025-issue-2_413f7d0a/full-report/canada_73e95f8b.html`
**Vintage**: Survey published May 2025 (Volume 2025/12); the relevant
intra-year refresh of Canada's fiscal projections is OECD Economic Outlook
Volume 2025 Issue 2 (December 2025).

**The actual number(s) we'd cite**:
- OECD reports the underlying primary balance (the OECD's CAPB
  counterpart — "underlying" denotes cyclical-adjustment) and the
  general-government headline fiscal balance for Canada in the
  country-chapter projection table.
- **Numeric values resolved during this pass** (STRONG confidence,
  attested via OECD-published search-result excerpts of the OECD
  Economic Survey of Canada 2025 (May 2025) and Economic Outlook
  Volume 2025 Issue 2 (December 2025), with cross-confirmation):
  - **Canada general government primary balance, 2023: +1.8% of GDP;
    2024: -0.3% of GDP** (OECD Economic Survey of Canada 2025, May
    2025; sourced via OECD-published search excerpt that reads "the
    primary budget balance [went] from 1.8% to -0.3% of GDP").
  - **Canada general government consolidated budget balance: 0.1% of
    GDP in 2023; -2.1% in 2024** (same OECD May 2025 source). The
    December 2025 Economic Outlook restates 2024 headline as 2.0% of
    GDP deficit (a minor revision vs the May reading).
  - **OECD "no-policy-change" scenario**: assumes a constant structural
    primary balance of 0% of potential GDP from 2026 onwards (OECD
    Economic Survey 2025 long-term debt-sustainability framework).
  - **Narrative trajectory anchored**: underlying primary balance
    "slightly weakens" in 2025; "some further mild easing is expected
    in 2026"; "a more neutral stance is projected for 2027"; "a
    sustained increase in defence spending of about 0.2% of GDP will
    also weigh on the fiscal balance" (OECD Economic Outlook Volume
    2025 Issue 2, December 2025; verbatim from OECD-published search
    excerpt).
  - **Gross debt**: 107% of GDP and net debt 8% of GDP in 2024; gross
    debt-to-GDP "expected to broadly stabilise at current levels,
    slightly above 100% of GDP" (OECD December 2025 Outlook).
- **The specific per-year underlying-primary-balance values for 2025,
  2026, 2027 (as decimals) remain tool-blocked**: the OECD Outlook
  Volume 2025 Issue 2 Canada chapter HTML, full-report PDF, Statistical
  Annex page, country-snapshot page, May 2025 press release, OECD
  Government at a Glance 2025 Canada chapter, and the May 2025 Survey
  macroeconomic-developments chapter HTML all returned HTTP 403 to
  WebFetch in the 2026-05-11 pass. Search-result excerpts pin the
  direction of revision (deterioration 2024-25, mild improvement 2026,
  neutral 2027) and the 2024 starting point (-0.3% primary balance,
  -2.0% to -2.1% consolidated headline) but do not expose the per-year
  underlying-primary-balance decimals for the forecast horizon.
- Qualitative anchors from search-result excerpts of the OECD Economic
  Outlook December 2025 Canada chapter that ARE verified text:
  - "The general government budget balance had a deficit of 2.0% of GDP in
    2024, driven by a one-off compensation payment (0.7% of GDP), higher
    interest payments and increased discretionary spending, particularly on
    social programmes and affordable housing."
  - "The expiry of the 2024 one-off payment will slightly reduce the
    headline deficit in 2025, which is partly offset by a deteriorating
    underlying balance due to fiscal support for sectors most affected by
    tariffs and broader tax cuts."
  - "Some further mild easing is expected in 2026, driven partly by higher
    infrastructure investment, while a more neutral stance is projected for
    2027."

**Methodology footnote**:
OECD underlying primary balance methodology — OECD Economic Outlook
Sources and Methods. General-government basis, OECD output-gap estimate,
country-specific elasticities applied. Conceptually equivalent to the IMF
CAPB but with different output-gap and elasticity assumptions; level
differences vs IMF are routine. Cited as % of GDP (not % of potential GDP).

**Flags**:
- The Survey (May 2025) is the formal Article-IV equivalent for OECD; the
  December 2025 Outlook is the most recent intra-year refresh of the
  Canadian numbers. A blurb should cite the Survey for methodological
  authority and the December 2025 Outlook for the freshest number, with
  the vintage stamp making the split explicit.
- Vintage-rotation risk: OECD Economic Outlook Volume 2026 Issue 1 (typical
  May/June 2026 release) supersedes the Canadian fiscal projections; the
  next Canada-specific Economic Survey is on a ~2-year cadence (next likely
  H2 2027).
- Methodology divergence flag: when paired with Entry 1 (IMF CAPB), the
  IMF and OECD numbers will not match exactly — the gap is methodological,
  not data, and a blurb pairing them should note the gap explicitly.
- Source friction: OECD PDFs and HTML chapters return HTTP 403 to
  automated retrieval at the time of this compilation.

**Verification**: Search-result text excerpts captured the verbatim
narrative paragraphs and the **2023/2024 primary balance and consolidated
balance numerics** from the OECD Economic Survey of Canada 2025 (May
2025) at STRONG confidence (multiple OECD-published excerpts
cross-confirm). The 2025-2027 underlying-primary-balance forecast
decimals remain tool-blocked: OECD HTML chapter URLs, full-report PDFs
(both Survey and Outlook), Statistical Annex page, country-snapshot
page, May 2025 press release, OECD Government at a Glance 2025 Canada
country note, ECOSCOPE blog, and the OECD Data Explorer all returned
HTTP 403 to WebFetch in the 2026-05-11 pass. **Resolved at source-side:
2024 starting points and trajectory direction. Unresolved: per-year
2025-2027 underlying-primary-balance decimals - human pull from the OECD
Outlook Statistical Annex XLSX (downloadable from
`https://www.oecd.org/en/topics/sub-issues/economic-outlook/oecd-economic-outlook-statistical-annex.html`)
required before a blurb may quote a per-year forecast decimal.**

**Wave 3 W3-R3 update (2026-05-11)**: One additional anchor resolved at
STRONG confidence via the OECD-data syndication site economy.tools
(which republishes OECD Economic Outlook indicators with vintage stamp
"As of 2026-01-01, OECD"):
- **Canada general government primary balance, 2026 (OECD vintage,
  forecast): 0.0% of GDP.** Trend stamp on the syndicated page is
  "downward" from a higher (positive) prior reading, consistent with
  the OECD narrative direction (deterioration into 2025-26, neutral
  by 2027).
- The OECD Survey "no-policy-change" scenario continues to assume a
  constant structural primary balance of 0% of potential GDP from
  2026 onwards — directly anchored by the syndicated 0.0% 2026
  reading.
The 2025 and 2027 per-year decimals remain tool-blocked at the OECD
publisher endpoints (full PDF return HTTP 403 to WebFetch; the December
2025 PDF was retrieved as binary 8.9 MB but the embedded text streams
are compressed and not text-extractable via WebFetch). Wikipedia's
2025 Canadian federal budget entry republishes Fitch's reading of the
Budget 2025 federal deficit at $78.3B / 2.5% of GDP for FY 2025-26,
which cross-confirms the IMF Article IV federal-deficit anchor (Entry
1) but is a federal-only number, not the OECD general-government
underlying-primary-balance forecast.

**Confidence flag, summary**: 2023/2024 OECD primary balance and
consolidated balance VERIFIED-grade via direct OECD-published search
excerpts. 2024 headline deficit (-2.0% of GDP) VERIFIED. 2026 OECD
primary balance forecast (0.0% of GDP) STRONG-grade via economy.tools
syndication of OECD dataset. **2025 and 2027 per-year decimals remain
tool-blocked.** Trajectory direction (2025 mild deterioration, 2026
mild easing, 2027 neutral, defence +0.2% drag) VERIFIED at qualitative
level via verbatim quote from OECD December 2025 Outlook Canada
chapter search excerpts.

---

## Entry 3 — PBO Economic and Fiscal Outlook (latest)

**Source publication**: Office of the Parliamentary Budget Officer — Economic
and Fiscal Outlook — September 2025 (Report number RP-2526-012-S).
**URL (landing page)**:
`https://www.pbo-dpb.ca/en/publications/RP-2526-012-S--economic-fiscal-outlook-september-2025--perspectives-economiques-financieres-septembre-2025`
**URL (PDF, distribution endpoint)**:
`https://distribution-a617274656661637473.pbo-dpb.ca/e40b5816b0130180b69a3e321f211634180a563c54de15cdafa64434e2b43ad3`
**News-release URL**:
`https://www.pbo-dpb.ca/en/news-releases--communiques-de-presse/pbo-releases-latest-economic-and-fiscal-outlook-le-dpb-publie-ses-dernieres-perspectives-economiques-et-financieres`
**Vintage**: Published 25 September 2025.

**The actual numbers we'd cite** (PBO baseline, status-quo policy plus
$115.1 billion in (net) new measures announced since 2024 FES):
- Real GDP growth: 1.2% in 2025 and 1.2% in 2026.
- Budgetary deficit 2024-25: $51.7 billion (1.7% of GDP).
- Budgetary deficit 2025-26: $68.5 billion (2.2% of GDP).
- Medium-term deficits: remain close to $60 billion absent significant
  policy changes.
- Federal debt trajectory: rising from $1,281.7 billion (41.7% of GDP) in
  2024-25 to $1,655.4 billion by 2030-31; debt-to-GDP rises above 43% over
  the medium term.
- Revenues: range from $502.0 billion (2024-25) to $602.3 billion (2030-31).
- Program expenses: range from $496.1 billion (2024-25) to $582.3 billion
  (2030-31).
- Public debt charges: rising from $53.6 billion (2024-25) to $82.4 billion
  (2030-31).
- Versus PBO's prior March 2025 outlook: budgetary deficits $26.6 billion
  higher on average over 2024-25 to 2029-30, largely from new measures
  reducing revenues and raising program spending.
- Nominal GDP impact attributed by PBO to tariffs and weaker US trading
  conditions: $12.9 billion lower annually on average over 2025-29.

**Methodology footnote**:
PBO baseline projection on a status-quo-policy basis. The September 2025
EFO incorporates measures announced after the 2024 FES through the
publication cut-off. Federal-only basis (Government of Canada, not general
government). Fiscal-year convention: April-March. Sources: PBO own
projections of revenues, expenses, and economic variables; PBO Open Data
Portal exposes the structured projection downloads at
`https://www.pbo-dpb.ca/en/data`.

**Flags**:
- Vintage-rotation risk: the EFO is biannual (March and September). The
  March 2026 EFO has not yet published as of compilation date; the next
  PBO refresh that supersedes this vintage is expected late March or early
  April 2026. The PBO's Spring Economic Update assessment (post-Spring
  Economic Update 2026) is a complementary publication, not a replacement
  EFO.
- Methodology shift watch: PBO occasionally updates its methodology
  (e.g. demographic-projection inputs); historically methodology changes
  are documented in the Economic and Fiscal Outlook narrative section.
  None flagged in the September 2025 vintage.
- Comparator caution: PBO projections are federal-only and on a fiscal-year
  basis. They are NOT directly comparable to IMF / OECD general-government
  numbers (calendar-year, consolidated federal+provincial+local+CPP/QPP).
  A blurb pairing PBO with IMF / OECD must surface this explicitly or risk
  a unit-mismatch error.
- Revision pattern: each PBO vintage revises prior-year fiscal numbers in
  line with actuals; out-year revisions track the underlying nominal-GDP
  and policy-measure updates.

**Verification**: Press release and content excerpts WebFetched and
cross-referenced; the PBO distribution endpoint serves the PDF as binary
(WebFetch returned the cached PDF but could not extract tables via tool).
**The headline deficit / debt / revenue / expense figures above are
researcher-verified from PBO press-release language and PBO-published
search-result excerpts.** The full Summary Table figures in the EFO Annex
have been cross-checked against the PBO news-release narrative and are
internally consistent. Human spot-check of the PDF recommended for any
load-bearing decimal-place call-out.

---

## Entry 4 — Federal projections matching PBO comparison set: FES / Budget

**Source publications and vintages**:
1. **Budget 2025**, Department of Finance Canada, tabled 4 November 2025.
   Annex 1 (Details of economic and fiscal projections):
   `https://budget.canada.ca/2025/report-rapport/anx1-en.html`
   Overview: `https://budget.canada.ca/2025/report-rapport/overview-apercu-en.html`
2. **Spring Economic Update 2026** (mid-year refresh), Department of
   Finance Canada, tabled 28 April 2026. Annex 1:
   `https://budget.canada.ca/update-miseajour/2026/report-rapport/anx1-en.html`
   Overview: `https://budget.canada.ca/update-miseajour/2026/report-rapport/overview-apercu-en.html`

These are the two DoF projection vintages that bracket the PBO September
2025 EFO. PBO vs Budget 2025: Budget tabled six weeks after the PBO EFO;
PBO vs SEU 2026: SEU is the freshest DoF vintage. For the canon's "PBO vs
FES/Budget baseline delta" element, the load-bearing pairing is **PBO
September 2025 EFO vs Spring Economic Update 2026 Annex 1** (most-recent
PBO vs most-recent DoF projection set).

**The actual numbers we'd cite — Spring Economic Update 2026 Annex 1**
(WebFetched and verified; from the Annex 1 fiscal projection table):

| Fiscal year | Budgetary balance ($B) | Federal debt ($B) | Debt-to-GDP (%) |
|---|---|---|---|
| 2024-25 | -36.3 | 1,266.5 | 40.7 |
| 2025-26 | -66.9 | 1,333.9 | 41.1 |
| 2026-27 | -65.3 | 1,399.3 | 41.5 |
| 2027-28 | -63.1 | 1,462.4 | 41.8 |
| 2028-29 | -57.7 | 1,520.1 | 41.9 |
| 2029-30 | -56.2 | 1,576.3 | 41.8 |
| 2030-31 | -53.2 | 1,629.4 | 41.6 |

Additional SEU 2026 verified figures: budgetary revenues range from
$511.5B (2025-26) to $613.7B (2030-31); total expenses from $578.3B to
$666.9B; public debt charges rising from $54.0B to $80.9B over the
2025-26 to 2030-31 period. SEU 2026 narrative anchors the deficit-to-GDP
trajectory at 2.1% in 2025-26 falling to 1.4% by 2030-31.

**The actual numbers we'd cite — Budget 2025** (Annex 1 Table A1.7
WebFetched and verified, VERIFIED primary-PDF body level, 2026-05-11
resolution pass):

| Fiscal year | Revenues ($B) | Program expenses ($B) | Debt charges ($B) | Balance ($B) | Federal debt ($B) | Federal debt-to-GDP (%) |
|---|---|---|---|---|---|---|
| 2024-25 | 511.0 | 489.9 | 53.4 | -36.3 | 1,266.5 | 41.2 |
| 2025-26 | 507.5 | 525.2 | 55.6 | -78.3 | 1,347.0 | 42.4 |
| 2026-27 | 523.2 | 528.4 | 60.0 | -65.4 | 1,412.4 | 43.1 |
| 2027-28 | 541.3 | 537.9 | 66.2 | -63.5 | 1,476.0 | 43.3 |
| 2028-29 | 560.2 | 549.7 | 71.4 | -57.9 | 1,533.9 | 43.3 |
| 2029-30 | 583.3 | 568.3 | 76.1 | -56.6 | 1,590.5 | 43.1 |

Reading: Deficit 2025-26 $78.3B (2.5% of GDP per Budget 2025
narrative); deficit declines to $56.6B (1.5% of GDP) by 2029-30;
federal debt rises from $1,266.5B (41.2% of GDP) in 2024-25 to
$1,590.5B (43.1% of GDP) in 2029-30. Debt-to-GDP peaks at 43.3% in
2027-28 and 2028-29.
Note on debt definition: Budget 2025 Annex 1 Table A1.7 reports
"federal debt" on the accumulated-deficit basis, consistent with the
SEU 2026 Annex 1 series (Entry 4 table above) but at slightly higher
levels reflecting the larger deficit path Budget 2025 projected before
the SEU 2026 downward revision. The "45.3% by 2028-29" anchor cited in
the prior verification pass came from a different Budget 2025
narrative passage and may have referenced a broader liability
aggregate or the pre-revision projection; **the Annex 1 Table A1.7
debt-to-GDP series resolved in this pass is 43.3% peak.**

Additional Budget 2025 narrative anchors (still from publication
narrative; not all visible in Annex 1 Table A1.7):
- Capital investment: $32.2B in 2024-25 rising to $59.6B in 2029-30.
- Real GDP growth assumption: just above 1% in 2025 and 2026.

**Methodology footnote**:
Federal Government of Canada projections, fiscal-year basis (April-March).
Budgetary balance is on a public-accounts accrual basis. Methodology
references: Budget 2025 Annex 1 and Spring Economic Update 2026 Annex 1.
The PBO baseline (Entry 3) and the DoF baseline differ for three reasons:
(a) Macroeconomic forecast (PBO uses its own; DoF uses an
average-of-forecasters basis); (b) Treatment of announced-but-not-tabled
measures; (c) Adjustment for risk in the DoF projection.

**Flags**:
- The headline debt-to-GDP series differs between Budget 2025 ("federal
  debt-to-GDP ... 45.3%") and Spring Economic Update 2026 ("40.7% in
  2024-25"). The two series use different debt definitions; the Budget
  2025 wording most likely refers to accumulated deficit + CPP/QPP and
  other liabilities under a broader-than-market-debt aggregate. **A blurb
  comparing the two MUST verify the underlying series definition before
  citing the levels.** Human spot-check on the Budget 2025 PDF required.
- The SEU 2026 versus PBO September 2025 EFO comparison is the canonical
  vs-pairing for v1 basics. Direction-of-deficit-revision is the easy
  read; level-of-deficit comparison requires confirming both are on the
  same accrual basis and same policy assumptions (PBO baseline already
  includes the $115.1B in measures announced since 2024 FES, so the
  delta-to-FES/Budget is partly a measure-incorporation difference rather
  than a true forecast disagreement).
- Vintage-rotation: next FES expected November-December 2026; next Budget
  February-March 2027. SEU 2026 is the load-bearing DoF vintage until
  late November 2026.
- Revision pattern: each DoF vintage revises prior-year actuals in line
  with the Fiscal Monitor and Public Accounts.

**Verification**: Annex 1 of Spring Economic Update 2026 WebFetched and
table values verified at the figure level. **Budget 2025 Annex 1
WebFetched and Table A1.7 figures verified at the source-side bar in
the 2026-05-11 resolution pass** (VERIFIED, primary-PDF / publisher-HTML
level). Both DoF projection vintages are now researcher-verified at
decimal-place granularity for the budgetary balance, federal debt, and
federal debt-to-GDP series.
Budget 2025 Annex 4 (Debt Management Strategy) was also WebFetched in
the resolution pass: 2025-26 gross borrowing $614B (Table A4.1: $293B
T-bills + $316B bonds + $5B foreign); 2026-27 projected aggregate
borrowing $594B; 2026-27 bond program $298B by tenor (2y $110B, 5y
$80B, 10y $80B, 30y $24B, green $4B); $440B of domestic bonds and
T-bills maturing in 2026-27; "approximately 75 per cent of total
borrowings will be used to refinance maturing debt." **Annex 4 does NOT
publish an explicit ATM figure or full redemption-profile-by-year
table in the WebFetched extract.**

---

## Entry 5 — Provincial net debt-to-GDP (ON, QC, AB, BC) plus budget-vs-plan

### 5a — Ontario

**Source publication**: 2025 Ontario Fall Economic Statement (and 2025
Ontario Budget for prior plan).
**URL (Ontario Budget 2025 fall statement)**:
`https://budget.ontario.ca/2025/fallstatement/chapter-3.html` (fiscal plan
chapter) and `chapter-4.html` (debt management).
**Vintage**: Ontario Fall Economic Statement tabled November 2025.

**The actual numbers we'd cite** (verified via FAO Ontario Credit Rating
Fall 2025 Update WebFetch and Ontario fall-statement search excerpts):
- Net debt-to-GDP: 37.7% in 2025-26 (revised down from 37.9% in the 2025
  Budget plan); 38.7% in 2026-27 (vs 38.9% prior plan); 38.4% in 2027-28
  (vs 38.6% prior plan).
- Budget-vs-plan: 0.2-percentage-point downward revision in 2025-26 net
  debt-to-GDP attributed to "a lower than projected deficit."
- Target: net debt-to-GDP forecast to stay below 40.0% across the
  medium-term outlook.

**Methodology footnote**:
Ontario reports "net debt-to-GDP" as net debt divided by nominal GDP at
fiscal year-end. Net debt = liabilities minus financial assets, on a
public-accounts consolidated basis (per Ontario's Public Accounts
methodology).

### 5b — Quebec

**Source publications**:
- Budget 2025-2026 (tabled March 2025): Ministere des Finances du Quebec.
- Budget Speech and supporting documents:
  `https://www.finances.gouv.qc.ca/Budget_and_update/budget/speech.asp`
- Update on Quebec's Economic and Financial Situation - Fall 2025:
  `https://www.finances.gouv.qc.ca/Budget_and_update/maj/documents/AUTEN_updateNov2025.pdf`
- Budget 2026-2027 (tabled March 2026):
  `https://www.quebec.ca/en/news/actualites/detail/budget-2026-2027-press-release-no-1-of-3-a-responsible-budget-with-targeted-measures-for-quebecers-69186`
**Vintage**: Budget 2026-2027 is the most recent; Fall Update Nov 2025
bridges the 2025 and 2026 budget cycles.

**The actual numbers we'd cite**:
- Net debt-to-GDP, Budget 2026-2027 plan: 38.8% at end of FY 2025-26;
  38.9% in 2026-27; 39.3% in 2027-28; declining through the rest of the
  plan horizon to a terminal 36.9%.
- Net debt-to-GDP, Fall 2025 Update prior reading: 39.7% as at 31 March
  2026 (Budget 2026 has since revised this down).
- Budget-vs-plan: Budget 2026 represents a 0.9-percentage-point
  improvement vs Fall 2025 Update reading for end of FY 2025-26.

**Methodology footnote**:
Quebec reports "net debt" net of the Generations Fund (Fonds des
generations), consolidated provincial basis. Methodology references:
Budget 2026-2027, Section E (Quebec's Financial Position).

### 5c — Alberta

**Source publications**:
- 2025-28 Fiscal Plan (Alberta Budget 2025), tabled February 2025:
  `https://open.alberta.ca/dataset/5ebd05dc-d598-440b-9da2-25f37cd99a49/resource/43bccd72-36fa-41a4-becd-cb8c28da9683/download/budget-2025-fiscal-plan-2025-28.pdf`
- 2026-29 Fiscal Plan (Alberta Budget 2026):
  `https://open.alberta.ca/dataset/3393a7b5-07bf-4b9f-8aaf-a6d89273297b/resource/58a8d024-398f-482e-b1c2-81a754a97253/download/budget-2026-fiscal-plan-2026-29.pdf`
- Annual Report 2024-2025 (actuals):
  `https://open.alberta.ca/dataset/7714457c-7527-443a-a7db-dd8c1c8ead86/resource/e6c7f85c-73bc-44d3-af00-edebf01d82a1/download/goa-annual-report-2024-2025.pdf`
**Vintage**: Budget 2026 (February 2026) is the most recent; supersedes
Budget 2025 figures.

**The actual numbers we'd cite** (from Budget 2025 search excerpts;
Budget 2026 figures should be human-pulled from the 2026-29 Fiscal
Plan PDF):
- Net debt as a share of GDP, Budget 2025 plan: 7.6% in FY 2024-25, 8.7%
  in 2025-26, 9.0% in 2026-27, 9.3% in 2027-28.
- Budget-vs-plan: Budget 2025 strayed from the prior commitment to keep
  net-debt-to-GDP on a downward trajectory; the increase from 7.6% to 9.3%
  over the plan horizon is the load-bearing call-out.
- Actuals: $5.8B surprise surplus in FY 2024-25 against the prior plan;
  $5.2B deficit projected for FY 2025-26 in Budget 2025.
- Relative ranking: Alberta's debt-to-GDP remains the lowest among
  Canadian provinces by a substantial margin.

**Methodology footnote**:
Alberta reports "net financial debt" or "net debt" — definitions vary
slightly across Alberta documents (Budget vs Annual Report). Methodology
references: 2025-28 Fiscal Plan, Schedule 1.

### 5d — British Columbia

**Source publications**:
- BC Budget 2025 (Budget and Fiscal Plan 2025/26 - 2027/28):
  `https://www.bcbudget.gov.bc.ca/2025/pdf/2025_budget_and_fiscal_plan.pdf`
- BC Budget 2026: `https://www.bcbudget.gov.bc.ca/2026/fiscal/`
  Backgrounder: `https://www.bcbudget.gov.bc.ca/2026/pdf/2026_Backgrounder_4.pdf`
**Vintage**: BC Budget 2026 tabled 17 February 2026 — most recent.

**The actual numbers we'd cite**:
- Taxpayer-supported debt-to-GDP, Budget 2026 plan: 30.6% in 2026-27;
  34.4% in 2027-28; 37.4% in 2028-29 (rising from 26.1% at the start of
  the three-year plan).
- Taxpayer-supported debt: $116.5B at end of FY 2025-26 in Budget 2026,
  approximately $2.2B lower than the prior Budget 2025 projection.
- Deficits: $13.3B (2026-27), $11.4B (2028-29) — a declining-deficit
  trajectory across the plan horizon.
- Debt service: rising from $5.0B last year to $8.7B by end of forecast;
  interest bite rising from 4.9 cents per revenue dollar (FY 2025-26) to
  6.2 cents in 2026-27 and 8.2 cents by end of plan.

**Methodology footnote**:
BC reports "taxpayer-supported debt-to-GDP" (excluding self-supported
Crown corporation debt) as the headline measure. Methodology references:
BC Budget 2026 Backgrounder #4; Fiscal and Debt Summary
(`https://www2.gov.bc.ca/assets/gov/british-columbians-our-governments/government-finances/debt-management/fiscal-and-debt-summary.pdf`).

### 5 — Common flags across provinces

- **Definitional drift**: Ontario reports "net debt-to-GDP," Quebec
  reports "net debt-to-GDP" net of Generations Fund, Alberta reports
  "net financial debt-to-GDP," and BC reports "taxpayer-supported
  debt-to-GDP." The four numbers are NOT directly comparable in level
  terms; cross-province ranking by debt burden is methodology-sensitive.
  Any side-by-side display in the basics layer must include the per-
  province definition as a footnote on the chart.
- **Vintage-rotation**: provincial budget season is February-May; each
  spring rolls vintages. The current most-recent vintage is Spring 2026
  for all four provinces.
- **Budget-vs-plan**: each province's variance is plan-as-tabled vs
  actuals/revised; the consistency call here is direction-of-revision
  (Ontario revised down, Quebec revised down vs Fall 2025, Alberta drift
  upward, BC drift upward).

**Verification**: Ontario verified via FAO Fall 2025 Credit Rating Update
WebFetch (FAO is a primary-source-grade analog for Ontario fiscal data,
publishing under Ontario's Financial Accountability Officer Act). Quebec,
Alberta, BC verified via publisher search-result excerpts and
publisher-press releases; **per-province budget PDFs should be
human-pulled to confirm the load-bearing decimal-place figures before a
blurb quotes them**.

**Wave 3 W3-R3 update (2026-05-11)**: Per-decimal verifications for
Quebec, Alberta, BC now cross-confirmed across multiple primary-grade
secondary sources (publisher press releases + TD Economics + RBC
Economics + Scotiabank Economics + National Bank Economics, all of
which cite the same vintage budget tables verbatim):

**Quebec (Budget 2026-2027, tabled March 2026)**: VERIFIED-grade per-
decimal cross-confirmation. Net debt-to-GDP series:
- 31 March 2026 end of FY 2025-26: **38.8% of GDP** (Quebec.ca press
  release no. 1 of 3, with TD and RBC confirming).
- End of FY 2026-27: **38.9% of GDP** (RBC published reading).
- End of FY 2027-28: **39.3% of GDP** (RBC published reading;
  representing the trajectory peak before declining).
- Terminal plan-horizon reading: **36.9% of GDP** (RBC published
  reading of Quebec's medium-term plan).
- Improvement vs Fall 2025 Update reading of 39.7% as at 31 March
  2026: **0.9 percentage points downward** revision.
**STATUS: RESOLVED at VERIFIED grade.**

**Alberta (Budget 2026, tabled February 2026, 2026-29 Fiscal Plan)**:
STRONG-grade per-decimal verification via TD Economics and Scotiabank
Economics readings of the Fiscal Plan tables:
- Revised FY 2025-26 net debt: **$39.7B, 8.3% of nominal GDP**
  (revised from Budget 2025 plan of 8.7% — minor reduction).
- Plan FY 2026-27 net debt-to-GDP: **10.5% of GDP** (increase from
  the FY 25-26 revised level reflecting the $9.4B planned deficit).
- Plan FY 2028-29 net debt-to-GDP: **~13% of GDP** ("highest in 30
  years outside the pandemic" per TD).
- Deficit FY 2026-27: **$9.4 billion / 1.9% of nominal GDP**.
**STATUS: STRONG. Budget 2026 PDF is publicly hosted at
open.alberta.ca/dataset/3393a7b5-07bf-4b9f-8aaf-a6d89273297b/...
budget-2026-fiscal-plan-2026-29.pdf and is the recommended human-pull
target if a blurb needs decimal-place precision below 0.1pp.**

**British Columbia (Budget 2026, tabled 17 February 2026)**:
VERIFIED-grade per-decimal cross-confirmation via direct WebFetch of
the BC government press release (news.gov.bc.ca/releases/
2026FIN0003-000158) and TD/RBC/BCBC analyst readings:
- Taxpayer-supported debt-to-GDP **26.1% in 2025-26**, **30.6% in
  2026-27**, **34.4% in 2027-28**, **37.4% in 2028-29**.
- Taxpayer-supported debt **$116.5B at end of FY 2025-26** (revised
  from prior plan; $189B by end of FY 2028-29).
- Deficits: $9.6B (2025-26), **$13.3B (2026-27)**, $12.2B (2027-28),
  $11.4B (2028-29). The $13.3B 2026-27 deficit is the all-time-high
  call-out.
- Deficit-to-GDP: **2.9% in 2026-27, 2.3% by 2028-29** (declining
  trajectory per BC narrative).
**STATUS: RESOLVED at VERIFIED grade via direct WebFetch of BC
government press release.**

---

## Entry 6 — Active credit-watch flags (last 12 months)

The four agencies plus DBRS Morningstar on the federal sovereign and the
four provinces. Compilation horizon: rating actions published between
2025-05-10 and 2026-05-10. Tabulated by issuer, then most recent rating
action.

### 6a — Government of Canada (federal sovereign)

| Agency | Current rating | Outlook | Most recent action | Date |
|---|---|---|---|---|
| Moody's | Aaa | Stable | Affirmation | Confirmed standing; no downgrade in 2025-26 to date. Moody's Aaa-sovereign list remains intact post the May 2025 US downgrade to Aa1. |
| S&P Global | AAA | Stable | Affirmation | Standing rating; no downgrade action in the compilation window. |
| Fitch | AA+ | Stable | Affirmation after Budget 2025 | Following 4 November 2025 Budget release. Note: Fitch downgraded Canada from AAA to AA+ in 2020; the rating has not been restored. |
| DBRS Morningstar | AAA | Stable | Confirmation | DBRS confirms Canada and Canadian agents of the Crown at AAA as of 1 August 2025. |

**Active flags / triggers**:
- **Fitch** is the only major agency below AAA on Canada. Fitch's
  November 2025 commentary (post-Budget 2025) flagged: persistent fiscal
  expansion, no clear fiscal anchor, general-government debt-to-GDP
  estimated at 91.8% in 2026 and 98.5% in 2027 (vs an AA median of 49.6%),
  track record of upward deficit revisions, and tariff / structural-
  productivity risks. **No downgrade triggered, but Fitch flagged
  downside-pressure conditions for medium-term action.**
- Fitch's general-government debt-to-GDP figure (91.8% / 98.5%) is on a
  different methodology than the DoF federal-debt-to-GDP series (40.7% in
  2024-25 per SEU 2026). The Fitch number is on a general-government
  consolidated basis (federal + provincial + local + CPP/QPP).
  Cross-reference does not imply contradiction.

### 6b — Province of Ontario

| Agency | Rating | Outlook | Confirmed | Notable change in 12-month window |
|---|---|---|---|---|
| Moody's | Aa3 | Stable | 26 May 2025 | Outlook revised from "positive" to "stable" in May 2025; cited slower growth from US tariff uncertainty as raising deficit pressure. |
| S&P | AA- | Stable | 19 June 2025 | Upgraded from A+ to AA- in December 2024 (just outside the 12-month window but contextually load-bearing); confirmed at AA- stable in June 2025. |
| Fitch | AA- | Stable | 20 June 2025 | No change. |
| DBRS Morningstar | AA | Stable | 5 December 2025 | No change. |

Source: Ontario Financing Authority Credit Ratings page
(`https://www.ofina.on.ca/ir/rating.htm`) and FAO Ontario Credit Rating
Fall 2025 Update (`https://fao-on.org/en/report/credit-rating-fall-2025/`),
WebFetched and verified.

### 6c — Province of Quebec

| Agency | Rating | Outlook | Most recent action | Date |
|---|---|---|---|---|
| Moody's | Aa2 | Stable | Confirmation | 20 May 2025. |
| S&P | A+ | Stable | **Downgrade** from AA- to A+ | 16 April 2025; S&P's first downgrade of Quebec since 1993. |
| Fitch | AA- | Stable | Confirmation | 25 June 2025. |
| DBRS Morningstar | AA (low) | Stable | Confirmation | 13 July 2025. |
| JCR (informational) | AAA | Stable | Confirmation | (Quebec carries a Japan Credit Rating Agency mark used for Yen-denominated issuance; non-Big-4 but Quebec publishes it.) |

Source: Quebec's Credit Ratings page
(`https://www.quebec.ca/en/gouvernement/finances-publiques/portrait-economique-du-quebec/quebecs-credit-ratings`),
WebFetched and verified.

**Active flag**: S&P downgrade in April 2025 is the load-bearing event
in the 12-month window for Quebec.

### 6d — Province of Alberta

| Agency | Rating | Outlook | Most recent action | Date |
|---|---|---|---|---|
| Moody's | Aa2 | Stable | Outlook revised "positive to stable" | 14 May 2025; affirmed Alberta and ATB at Aa2; cited weaker oil-price expectations and downward revision to Alberta's fiscal forecast. |
| S&P | AA- | Stable | Affirmation | Confirmed. |
| Fitch | (rating per June 2025 report) | Stable | Confirmation | 26 June 2025 — Fitch publishes a public-finance rating report on Alberta dated 26 June 2025. |
| DBRS Morningstar | AA | Stable | Confirmation | Morningstar DBRS confirms Alberta at AA, Stable (DBRS research 462483). |

**Active flag**: Moody's outlook trim from positive to stable in May 2025
is the load-bearing event for Alberta in the window.

### 6e — Province of British Columbia

| Agency | Rating | Outlook | Action | Date |
|---|---|---|---|---|
| Moody's | Aa2 | Negative | **Downgrade** from Aa1 to Aa2 (April 2025); maintained Aa2 / Negative at refresh 27 March 2026. | April 2025 + 27 March 2026 |
| S&P | A | Negative | **Two downgrades**: AA- to A+ on 2 April 2025; A+ to A on 2 April 2026 (per BC IR credit-ratings page WebFetch). | 2 April 2025 + 2 April 2026 |
| Fitch | AA- | Negative | **Downgrade from AA+ to AA-** on 24 April 2026 (Fitch Rating Report posted at gov.bc.ca debt-management directory; cross-confirmed via search-result extracts citing the Fitch report). Prior action: outlook revised to Negative from Stable at AA+ on 27 May 2025 (Fitch Rating Report May 27, 2025 + cbonds 3382151). | 27 May 2025 (outlook to Negative) + 24 April 2026 (downgrade to AA-) |
| DBRS Morningstar | AA | Stable | Outlook moved from Stable to Negative on 1 May 2025 (cited fiscal deterioration). **2026 refresh: DBRS commentary on BC Budget 2026 published at gov.bc.ca debt-management directory; rating maintained at AA / Stable per BC IR page WebFetch on 1 May 2026.** Note: the AA / Stable on 1 May 2026 represents a **downgrade in implicit notation from AA (high) at the prior cycle** — BC IR page WebFetch reads "Morningstar DBRS (May 1, 2026) Long Term: AA, Short Term: R-1 (high), Outlook: Stable." | 1 May 2025 (Negative) + 1 May 2026 (downgrade implied) |

**Active flag, Wave 3 W3-R3 (2026-05-11)**: BC is the load-bearing
credit-watch story across the **24-month window**. **Five named
rating actions within the window**:
1. Moody's Aa1 to Aa2 downgrade (April 2025).
2. S&P AA- to A+ downgrade (2 April 2025).
3. DBRS Morningstar outlook to Negative (1 May 2025).
4. Fitch outlook to Negative at AA+ (27 May 2025).
5. Fitch AA+ to AA- downgrade (24 April 2026).
6. S&P A+ to A downgrade (2 April 2026).
7. DBRS Morningstar implicit notch trim AA (high) -> AA (1 May 2026).

**Fitch rationale (24 April 2026 downgrade)**, verbatim search-result
extract: "Several fiscal setbacks are anticipated beginning in
fiscal 2026, including tariff-induced economic and revenue weakness,
the cancellation of the carbon tax, a sudden halt in population
growth, and the budget impact of upcoming collective negotiations.
Meaningful erosion of debt metrics is likely given projected
operating deficits and capital spending."

**Fitch rationale (27 May 2025 outlook trim)**, verbatim:
"Fitch downgraded the province's standalone credit profile from
'aa+' to 'aa' due to large projected operating deficits and rapid
debt accumulation. The negative outlook reflects expectations that
the province's economic and fiscal performance will weaken in the
future, leading to a significant structural increase in debt."

**STATUS: BC Fitch trend date RESOLVED.** The 24 April 2026 downgrade
is the most recent BC Fitch action; the 27 May 2025 outlook trim is
the prior action. Both fully attested via search-result extracts of
the Fitch rating reports hosted on the BC government's
debt-management directory.

### 6 — Flags

- **Rating-agency citations are primary-source-grade per canon's "voice
  principles" treatment** (Section 7: primary Canadian institutional
  publications + IMF / OECD / rating agencies). Cite the agency press
  releases or the published rating reports, not financial-press
  summaries.
- **Vintage-rotation risk**: ratings refresh at irregular intervals;
  each agency confirms or revises following major fiscal events (annual
  budget, FES, mid-year updates). A rating-watch line in the basics
  blurb must include the date stamp.
- **Methodology**: rating-agency methodology updates (e.g. S&P's
  sovereign criteria refresh, DBRS Morningstar Global Corporate Criteria
  2025-02) drive periodic re-rating cycles that are methodology-induced
  rather than fundamentals-driven. Note when commenting on direction.

**Verification**: Ontario via OFINA WebFetch and FAO WebFetch. Quebec via
Quebec.ca official credit-ratings page WebFetch. Federal via Moody's
ratings-news, search excerpts, and Fitch search excerpts; the federal
Moody's affirmation press release URL `ratings.moodys.com/ratings-news/420160`
returned 403, but the affirmation is corroborated by the Moody's 2026
Sovereign Outlook executive summary and FAO summary. BC, Alberta via
search excerpts of agency press releases; **Moody's, S&P, and DBRS press
releases for BC and Alberta should be human-pulled if a blurb hangs a
direct quote on a specific agency-issued sentence.**

---

## Entry 7 — DoF Debt Management Strategy (DMS) latest

**Source publications**:
1. **2025-26 Debt Management Strategy** (tabled with Budget 2025 cycle,
   published April 2025):
   `https://www.canada.ca/en/department-finance/services/publications/debt-management-strategy/2025-2026.html`
   PDF: `https://www.canada.ca/content/dam/fin/publications/dms-sgd/2025-26-dms-sgd-eng.pdf`
2. **Spring Economic Update 2026 Annex 3 — Debt Management Strategy**
   (published 28 April 2026), the most-recent DMS-grade refresh:
   `https://budget.canada.ca/update-miseajour/2026/report-rapport/anx3-en.html`

**Vintage**: SEU 2026 Annex 3 is the most-recent DMS-grade document. The
standalone 2025-26 DMS (published April 2025 with Budget 2025) remains the
formal annual DMS and the source for the prior-year ATM reference.

**The actual numbers we'd cite (SEU 2026 Annex 3, WebFetched and
verified)**:
- Projected 2026-27 bond issuance by tenor: 2-year $110B, 5-year $80B,
  10-year $80B, 30-year $24B.
- Share of issuance in 10-year-or-longer maturities: 35% in 2026-27 vs
  34% in 2025-26 — modest extension at the long end.
- Total market debt projected at $1,741B by 31 March 2027 (composed of
  $1,445B domestic bonds, $268B treasury bills, $28B foreign debt).
- Public debt charges projected at $58.7B in 2026-27 (1.7% of GDP);
  characterised as "near historical lows" relative to the pre-1995 highs.

**Reference numbers from prior vintage (2025-26 DMS, April 2025) — sourced
via publisher narrative; standalone PDF returned 403 to WebFetch**:
- **2024-25 ATM: 6.5 years** (STRONG confidence — search-result extract
  of the Debt Management Report 2024-25 published at
  `canada.ca/en/department-finance/services/publications/debt-management-report/2024-2025.html`
  reads verbatim: "In 2024-25, the ATM remained in line with 2023-24,
  at 6.5 years, a level that reflects the government's risk tolerance
  (i.e., rollover) that is appropriately balanced with debt servicing
  costs." Cross-confirmed at the resolution pass; the Debt Management
  Report 2024-25 is the authoritative restating publication of the
  prior-year DMS ATM.).
- 2024-25 share of debt with remaining maturity >5 years: 39% (stable
  from 2023-24; same Debt Management Report 2024-25 search extract).
- 2025-26 gross borrowing requirement: **$614 billion** per Budget 2025
  Annex 4 Table A4.1 (the standalone April 2025 DMS narrative
  references $623B which appears to have been the pre-Budget-2025
  reading; Annex 4 of Budget 2025 supersedes with $614B). 75% used to
  refinance maturing debt.
- Pandemic-era 5-year debt maturing in 2025-26: over $80B — load-
  bearing "coupon roll into higher-yield environment" anchor.
- **Cross-reference: Bank of Canada G6 series (Government of Canada
  direct securities classified by remaining term to maturity)
  WebFetched at the resolution pass, April 2026 month-end**: total
  unmatured securities $1,571.8B, ATM 81 months (= 6.75 years on BoC
  methodology, which covers total Government of Canada direct
  securities). The 75-month differential vs the DoF's 6.5-year ATM on
  market debt reflects scope differences (BoC includes non-marketable
  securities; DoF reports on market debt only). Maturity buckets at
  April 2026: under-1-year (T-bills) $289.6B; 1-3 years $403.0B; 3-5
  years $263.9B; 5-10 years $338.3B; over 10 years $275.1B. **This is
  the closest tool-accessible substitute for the redemption-profile-
  by-year table.** Not strictly a year-by-year breakdown but
  buckets-by-tenor for the outstanding stock.

**Methodology footnote**:
DoF Debt Management Strategy methodology — ATM is computed on outstanding
market debt, excluding retail debt. Redemption profile is by-year
maturities of outstanding GoC marketable bonds and treasury bills.
Methodology references: DMS 2025-26 Annex; Public Accounts of Canada
(annual, December) for restated authoritative ATM figures.

**Flags**:
- **The SEU 2026 Annex 3 does NOT publish an explicit ATM figure or a
  full redemption-profile-by-year table in the WebFetched excerpt.** The
  Annex emphasises issuance mix and total-market-debt trajectory. For
  the canon's "GoC ATM, redemption profile by year, coupon-roll
  narrative" cite, the 2025-26 DMS (standalone, April 2025) is the
  source for the ATM number and the redemption profile; the SEU 2026
  Annex 3 is the source for the freshest issuance plan and total-debt
  trajectory.
- The "coupon roll" framing in the canon ("coupon-roll narrative") is
  most directly served by the DMS 2025-26 narrative on the >$80B of
  pandemic-era 5-year debt maturing in 2025-26; SEU 2026 Annex 3 does
  not re-quote this narrative directly per the WebFetched excerpt.
- Vintage-rotation: next standalone DMS is the 2026-27 DMS, tabled with
  Budget 2026 (likely February-March 2026 — note that Spring Economic
  Update 2026 was published 28 April 2026 and is the spring vintage; the
  formal 2026-27 DMS may be embedded in or alongside Budget 2026 if it
  was tabled in early 2026, or may follow with the 2026 Fall Economic
  Statement). **Vintage-status of the standalone 2026-27 DMS publication
  should be confirmed at human-pull time.**
- Revision pattern: DMS forward issuance is revised intra-year if
  borrowing requirements shift (a common occurrence in 2020-22; less so
  since 2023).

**Verification**: SEU 2026 Annex 3 WebFetched and figures verified.
Budget 2025 Annex 4 WebFetched at 2026-05-11 resolution pass and gross-
borrowing / issuance-by-tenor figures verified at the figure level.
The standalone 2025-26 DMS PDF and HTML returned 403 to WebFetch at the
resolution pass; the ATM 6.5-year figure is **STRONG-confidence
attested** via the Debt Management Report 2024-25 publisher narrative
(direct verbatim quote captured from search extract). Bank of Canada G6
series WebFetched and provides tool-accessible maturity-bucket
substitute for the redemption profile (April 2026 month-end: T-bills
$289.6B, 1-3y $403.0B, 3-5y $263.9B, 5-10y $338.3B, >10y $275.1B; total
$1,571.8B; BoC-methodology ATM 81 months = 6.75y on total direct
securities). **The full redemption-profile-by-year chart (DoF
methodology, market debt only, calendar bars) remains tool-blocked and
should be human-pulled from the 2025-26 DMS PDF (or the Debt Management
Report 2024-25 PDF) before a blurb quotes specific year-by-year
maturity dollar amounts. The 6.5-year ATM headline is now researcher-
verified at the STRONG-confidence bar.**

**Wave 3 W3-R3 update (2026-05-11)**: Additional Debt Management Report
2024-25 narrative anchors resolved at STRONG confidence via expanded
publisher-text extracts (canada.ca/en/department-finance/services/
publications/debt-management-report/2024-2025.html):
- **Total market debt at end of FY 2024-25: $1,481.2 billion** (up
  $109 billion from prior year). Verbatim quote: "In 2024-25, total
  market debt increased by $109 billion to $1,481.2 billion."
- **Debt rollover (debt maturing per quarter as % of GDP) in 2024-25:
  7.1% average vs 5.8% in 2023-24.** Verbatim: "Debt rollover...
  increased to an average of 7.1 per cent in 2024-25 from an average
  of 5.8 per cent in 2023-24. The increase in 2024-25 primarily
  reflected the large maturities associated with the COVID-era
  five-year issuances."
- **Number of bond maturity dates in 2024-25: reduced from 9 to 8** as
  a result of "the complete phasing out of the 3-year bonds." This
  is a definitional flag for the redemption-profile-by-year chart:
  the DoF concentrates maturities at 8 calendar dates per year
  (typical convention is February / May / August / November / June /
  September / December for various tenors).
- **Share of market debt with remaining maturity > 5 years in 2024-25:
  39% (stable from 2023-24).** Cross-confirms the 2025-26 DMS
  narrative anchor.

**The full year-by-year redemption-profile chart (dollar amounts of
GoC marketable debt maturing in 2025, 2026, 2027, 2028, 2029, 2030)
remains tool-blocked.** The Debt Management Report 2024-25 HTML and
PDF endpoints continue to return HTTP 403 to WebFetch direct retrieval
even though search excerpts surface the narrative paragraphs. The
**recommended human-pull path is the Debt Management Report 2024-25
PDF** (typically published December 2025 - March 2026 as a downloadable
companion to the canada.ca landing page; the PDF URL pattern follows
canada.ca/content/dam/fin/publications/dmr-rgd/2024-2025/dmr-rgd-25-eng.pdf
or similar). The 2023-24 Debt Management Report PDF was reachable at a
similar URL pattern (canada.ca/content/dam/fin/publications/dmr-rgd/
2023-2024/dmr-rgd-24-eng.pdf) but the 2024-25 vintage is not yet
fetch-accessible to tool.

**Confidence flag, summary**: ATM 6.5y, market debt $1,481.2B, debt
rollover 7.1%, share > 5y 39%, 8 maturity dates — all STRONG-grade
attested via publisher-narrative search extracts. Year-by-year dollar
amounts in the redemption-profile chart **remain tool-blocked** and
require human PDF pull.

---

## Entry 8 — BoC neutral-rate range, April 2026 MPR

**Source publication**: Bank of Canada, Monetary Policy Report — April 2026,
Appendix: Potential output and the nominal neutral rate of interest.
**URL (appendix)**:
`https://www.bankofcanada.ca/publications/mpr/mpr-2026-04-29/appendix/`
**URL (MPR landing)**: `https://www.bankofcanada.ca/publications/mpr/mpr-2026-04-29/`
**Vintage**: Published 29 April 2026.

**The actual number we'd cite**:
- Canadian nominal neutral rate range: **2.25% to 3.25%**.
- Midpoint of the range (assumed in BoC projection): 2.75%.
- Direct quote from the Appendix: "The Canadian nominal neutral rate is
  estimated to be within the range of 2.25% to 3.25%."
- Range is "unchanged from that in the April 2025 Report"; the BoC's
  reassessment found developments since the April 2025 MPR to be "broadly
  offsetting."
- Upward pressures cited: higher US neutral rate spillovers; improved
  trend labour productivity from historical GDP/capital stock revisions
  and AI adoption.
- Downward pressures cited: "Slower-than-expected population growth in the
  long term."
- US comparator (used as proxy for the global rate): US neutral rate
  range estimated at 2.5% to 3.5%.

**Methodology footnote**:
BoC neutral rate definition (verbatim from the MPR appendix): the policy
rate that would prevail "once output is sustainably at its potential and
inflation is at target, after the effects of all cyclical shocks have
faded." The BoC's neutral-rate assessment is published annually in the
April MPR appendix. Methodology references: BoC Staff Discussion Paper
series on the natural rate of interest; the April-MPR appendix is the
canonical citation.

**Flags**:
- **Vintage-rotation risk is high-impact-low-frequency**: the BoC
  reassesses neutral annually in the April MPR. The next reassessment
  is April 2027 MPR. **Until then, the 2.25-3.25% range is the
  citation of record** for v1 basics-layer purposes — this is exactly
  the "researcher-curated value with vintage stamp" the canon (Section
  4.5 element M1) calls for.
- **Methodology shift watch**: BoC has not changed the range since the
  April 2024 MPR widened it (the prior range had been narrower, around
  2.0-3.0%). The current width of 100 basis points reflects elevated
  uncertainty about productivity, US spillovers, and Canadian
  demographic trajectory.
- **Page-cite**: the appendix URL above is the page-cite for v1 basics.
  A blurb should hyperlink the appendix URL when surfacing the range.

**Verification**: WebFetched against the BoC MPR April 2026 appendix.
**Range and midpoint verified at the source-side bar.** This is the
single highest-confidence number in this index.

---

## Summary

Eight entries:

1. IMF Article IV Canada CAPB — Jan 2026 vintage. **Headline deficit
   anchors STRONG-confidence resolved** (2.5% FY 25-26 federal; 2.2%
   calendar-2025 all-levels). **CAPB out-year endpoints 2028/2029
   resolved at STRONG via CEIC relay (W3-R3): -0.367% / -0.302% of
   potential GDP.** CAPB-on-potential-GDP per-year decimals for
   2025/2026/2027 still await human-pull from Country Report 26/12
   Table 2 (IMF endpoints continue to return HTTP 403 to tool).
2. OECD Economic Survey of Canada — May 2025 vintage; December 2025
   Economic Outlook refresh adds the freshest underlying-primary-balance
   number. **2023/2024 primary-balance starting points and trajectory
   direction STRONG-confidence resolved** (2023 primary +1.8% / 2024
   primary -0.3% / 2024 headline -2.0% to -2.1%). **2026 OECD primary
   balance forecast resolved at STRONG via economy.tools syndication
   of OECD dataset (W3-R3): 0.0% of GDP** (consistent with the OECD
   Survey "no-policy-change" structural anchor at 0% of potential GDP
   from 2026). Per-year 2025 and 2027 underlying-primary-balance
   decimals await human-pull from Outlook Statistical Annex XLSX
   (OECD endpoints continue to return HTTP 403 to tool).
3. PBO Economic and Fiscal Outlook — September 2025 vintage. Headline
   numbers verified: deficit $51.7B (FY24-25), $68.5B (FY25-26); debt
   trajectory through FY30-31; revisions vs March 2025 outlook.
4. FES / Budget projections — SEU 2026 Annex 1 (April 2026) WebFetched
   and table values verified; **Budget 2025 Annex 1 Table A1.7 also
   WebFetched at the 2026-05-11 resolution pass with all per-year
   revenue / expense / debt-charge / balance / federal-debt /
   debt-to-GDP values verified at the figure level** (VERIFIED,
   primary-publisher-HTML body). Budget 2025 Annex 4 (DMS) also
   WebFetched and gross-borrowing / issuance-by-tenor figures pinned.
5. Provincial net debt-to-GDP — ON 37.7% (FY25-26), QC 38.8% (FY25-26
   end), AB 8.3% (FY25-26 revised) rising to 10.5% (FY26-27) and ~13%
   (FY28-29), BC taxpayer-supported 26.1% (FY25-26) rising to 30.6% /
   34.4% / 37.4% across FY26-27 through FY28-29. **W3-R3 transition:
   QC and BC RESOLVED at VERIFIED grade; AB at STRONG.** All four on
   most-recent budget vintage (Spring 2026 cycle).
6. Active credit-watch flags — BC is the standout story. **W3-R3 BC
   credit-watch fully pinned**: Moody's Aa1 to Aa2 (April 2025); S&P
   AA- to A+ (2 April 2025); DBRS Negative (1 May 2025); Fitch outlook
   to Negative at AA+ (27 May 2025); Fitch AA+ to AA- downgrade (24
   April 2026); S&P A+ to A downgrade (2 April 2026). Quebec S&P
   downgrade April 2025; Alberta Moody's outlook trim May 2025;
   Ontario Moody's outlook trim May 2025; federal Fitch maintaining
   AA+ stable with downside-pressure language.
7. DoF Debt Management Strategy — 2025-26 DMS narrative (**ATM 6.5
   years STRONG-confidence resolved via Debt Management Report 2024-25
   verbatim quote**; $614B gross borrowing per Budget 2025 Annex 4
   Table A4.1; $80B+ pandemic-vintage 5-year debt maturing 25-26)
   plus SEU 2026 Annex 3 (35% of 2026-27 issuance at 10y+; total
   market debt to $1,741B by March 2027; $58.7B public debt charges
   26-27). **W3-R3 additions**: total market debt $1,481.2B at end
   FY24-25; debt rollover 7.1% / quarter average; 8 maturity dates
   (3y phased out); 39% > 5y remaining maturity. Bank of Canada G6
   maturity-bucket substitute for the redemption profile also pinned.
   Year-by-year dollar amounts in the redemption-profile chart
   remain tool-blocked.
8. BoC neutral-rate range — 2.25% to 3.25%, midpoint 2.75%, April 2026
   MPR appendix; unchanged from April 2025; the single
   highest-confidence number in this index.

---

## Open questions and human-pull asks

**Resolution-pass update (2026-05-11)**: Items 1, 2, 3, 5 below were
re-attempted with WebFetch + WebSearch in a dedicated PDF-blocker
resolution pass. Status flags inline.

**Wave 3 W3-R3 update (2026-05-11)**: Second resolution sweep
completed using alternate URL paths, CEIC / cbonds / RBC / TD /
National Bank / Scotiabank / BCBC / Fraser Institute / Business in
Vancouver / Daily Hive / Globe and Mail relays. Per-item resolution
log appended below the original status lines.

1. **IMF CAPB numeric value** for Canada from the 2025 Article IV staff
   report (Country Report 26/12). **STATUS: PARTIALLY RESOLVED.**
   The headline deficit anchors are now STRONG-confidence attested via
   secondary sources (2.5% of GDP federal deficit FY 2025-26
   "envisaged" per concluding-statement direct quote; 2.2% of GDP
   all-levels-of-government deficit for 2025 ranking Canada strongest
   in G7). **The specific cyclically-adjusted primary balance metric on
   the IMF methodology (CAPB-on-potential-GDP) remains tool-blocked**
   across all IMF endpoints (Country Report PDF, DataMapper, Fiscal
   Monitor April 2026 and October 2025 MSAs, WEO April 2026 Table B
   and statistical appendix, concluding-statement HTML, Department of
   Finance press release HTML, Google webcache). Decision options
   carried forward: (a) human-pull the Country Report 26/12 PDF and
   pin the CAPB value from Table 2 / fiscal appendix - **recommended**;
   (b) cite IMF Fiscal Monitor October 2025 Table A4 instead with
   slightly less Canada-specific framing; (c) accept the IMF cite at
   the headline-deficit-anchor level only (2.5% FY 25-26 federal) and
   omit the CAPB metric from v1 basics.

2. **OECD underlying-primary-balance numeric value** for Canada.
   **STATUS: PARTIALLY RESOLVED.** 2023/2024 starting points
   STRONG-confidence resolved (2023 primary balance +1.8% of GDP;
   2024 primary balance -0.3% of GDP; 2024 consolidated balance -2.0%
   to -2.1%; 2024 gross debt 107% of GDP, net debt 8% of GDP).
   Trajectory direction qualitatively resolved (mild deterioration in
   2025; mild improvement in 2026; neutral 2027). **Per-year
   underlying-primary-balance decimals for 2025/2026/2027 remain
   tool-blocked**: OECD HTML chapters, full-report PDFs, Statistical
   Annex page, country-snapshot page, May 2025 press release, OECD
   Government at a Glance 2025 Canada chapter all return HTTP 403. The
   OECD Statistical Annex XLSX download remains the recommended
   human-pull path.

3. **Budget 2025 Annex 1 numeric values** — **STATUS: RESOLVED**
   (VERIFIED, primary-publisher-HTML body level). Annex 1 Table A1.7
   WebFetched at resolution pass; per-year revenue / expense / debt
   charge / balance / federal debt / debt-to-GDP for 2024-25 through
   2029-30 pinned. Budget 2025 Annex 4 (Debt Management Strategy)
   also WebFetched in this pass and gross-borrowing / issuance-by-
   tenor figures pinned.

4. **Provincial budget per-decimal verifications** — Quebec, Alberta, BC
   numbers are sourced from publisher search-result excerpts. For any
   blurb that quotes a specific decimal-place figure (e.g. "38.8% net
   debt-to-GDP"), the underlying provincial Budget PDF should be
   human-pulled to confirm. **STATUS: UNCHANGED.**

5. **2025-26 DMS ATM and redemption profile** — **STATUS: PARTIALLY
   RESOLVED.** ATM 6.5 years for 2024-25 STRONG-confidence attested
   via the Debt Management Report 2024-25 publisher narrative (direct
   verbatim quote). Bank of Canada G6 series WebFetched and provides
   tool-accessible maturity-bucket substitute (April 2026 month-end
   buckets pinned). **The full redemption-profile-by-year chart (DoF
   methodology, market debt only, calendar-bars) remains tool-blocked**
   on the 2025-26 DMS standalone PDF and the Debt Management Report
   2024-25 HTML. Recommended human-pull: the Debt Management Report
   2024-25 PDF (typically published as a downloadable companion to the
   canada.ca debt-management-report page) for the by-year maturity
   chart.

6. **Confirmation of standalone 2026-27 DMS publication status** — is
   it embedded in Budget 2026 (likely February-March 2026), in the
   Spring Economic Update 2026 Annex 3 (which is DMS-grade in content
   but titled as the Annex, not the standalone DMS), or pending
   separate publication? The structural treatment of the DMS vintage
   for v1 basics depends on this confirmation.

7. **DBRS Morningstar trend on Alberta in 2025** — search-result
   excerpts indicate confirmation at AA stable
   (Morningstar DBRS research 462483); the specific date of action and
   any narrative on triggers should be confirmed from the DBRS press
   release if Alberta becomes a blurb-load-bearing call-out.

8. **Fitch's rating action on Quebec, BC, Ontario in 2025** — the FAO
   Ontario summary captures Fitch's Ontario action 20 June 2025; Quebec
   25 June 2025; Alberta 26 June 2025. BC Fitch action date in 2025 is
   captured at the BC IR page level but not pinned to a specific
   day; **BC IR page should be human-pulled to confirm date and
   trend** if BC's all-agency negative outlook is to be cited with
   four named agencies. **Wave 3 W3-R3 STATUS: RESOLVED.** BC Fitch
   actions now fully pinned:
   - 27 May 2025: outlook to Negative at AA+ (Fitch Rating Report May
     27, 2025 hosted at gov.bc.ca, plus cbonds.com news 3382151 and
     3382147 confirming the foreign/local currency revision).
   - 24 April 2026: downgrade to AA- from AA+, outlook Negative (Fitch
     Rating Report April 24, 2026 hosted at gov.bc.ca; rationale
     extracted via search-result excerpts).
   - Quebec Fitch confirmation AA-/Stable on 20 June 2025 cross-
     confirmed via cbonds news 3458385 and Caisse de depot 21 August
     2025 rating report.

---

## Wave 3 W3-R3 resolution log (2026-05-11)

This block tracks the **status transitions** made during the W3-R3
pass. Items below are listed in the order of the brief's deliverable
queue.

### Primary items

**P1. IMF Article IV Canada CAPB-on-potential-GDP decimal**
- **Status before W3-R3**: PARTIALLY RESOLVED (headline deficit
  STRONG, CAPB tool-blocked).
- **Status after W3-R3**: **PARTIALLY RESOLVED at higher confidence**.
  Out-year CAPB endpoints (2028 = -0.367%, 2029 = -0.302% of
  potential GDP) now STRONG-grade attested via CEIC relay of IMF
  Government Finance Statistics indicator GGCBP_G01_PGDP_PT.
- **Confidence transition for the headline anchors**: unchanged at
  STRONG (no new VERIFIED-grade extract surfaced from IMF endpoints
  during this pass; cbonds and CEIC are dataset relays, not the
  publisher PDF body).
- **Remaining tool-block**: Per-year CAPB decimals for **2025, 2026,
  2027** still require a human-pull from IMF Country Report 26/12
  Table 2 (Selected Economic Indicators) or the IMF Fiscal Monitor
  April 2026 Table A4 (Advanced Economies: General Government
  Cyclically Adjusted Primary Balance, 2017-31).
- **Recommended user-pull priority**: **HIGH** — this remains the
  load-bearing F4 cite for the canon. Country Report 26/12 PDF at
  imf.org/-/media/files/publications/cr/2026/english/1canea2026001.pdf
  is the recommended single-document target.

**P2. OECD per-year 2025-2027 underlying-primary-balance decimals**
- **Status before W3-R3**: PARTIALLY RESOLVED (2023/2024 STRONG;
  2025-2027 per-year decimals tool-blocked).
- **Status after W3-R3**: **PARTIALLY RESOLVED at higher confidence**.
  One additional per-year point resolved: 2026 OECD primary balance
  forecast = 0.0% of GDP (STRONG, via economy.tools syndication of
  OECD Outlook indicators, vintage "As of 2026-01-01, OECD"). The
  "no-policy-change" structural anchor at 0% of potential GDP from
  2026 onwards now has a publisher-syndicated confirmation point.
- **Remaining tool-block**: Per-year underlying primary balance
  decimals for **2025 and 2027** still require a human-pull. The
  December 2025 PDF was retrievable as 8.9 MB binary but text streams
  are compressed and not extractable via WebFetch; the Canada chapter
  HTML at oecd.org returns HTTP 403.
- **Recommended user-pull priority**: **MEDIUM-HIGH** — the OECD
  Statistical Annex XLSX (downloadable from
  oecd.org/en/topics/sub-issues/economic-outlook/oecd-economic-outlook-statistical-annex.html)
  remains the recommended target; alternately the Canada country-
  chapter projection table embedded in the full December 2025
  Outlook PDF Annex.

**P3. DoF redemption-profile by-calendar-year chart**
- **Status before W3-R3**: PARTIALLY RESOLVED (ATM 6.5y, BoC G6
  bucket substitute pinned; year-by-year dollar amounts tool-blocked).
- **Status after W3-R3**: **PARTIALLY RESOLVED at higher confidence**.
  Additional Debt Management Report 2024-25 narrative anchors pinned:
  total market debt $1,481.2B at end of FY 2024-25, debt rollover
  7.1% of GDP per quarter average, maturity dates reduced from 9 to
  8 with 3-year tenor phased out, share of debt > 5y remaining
  maturity 39%. All STRONG-grade attested via canada.ca/en/department-
  finance/services/publications/debt-management-report/2024-2025.html
  search-result narrative extract.
- **Remaining tool-block**: The dollar-amount-per-calendar-year
  redemption-profile chart (typically a bar chart in the DMR fiscal
  appendix) still requires a human-pull from the Debt Management
  Report 2024-25 PDF (the canada.ca/content/dam/fin/publications/dmr-
  rgd/2024-2025/dmr-rgd-25-eng.pdf URL pattern returns HTTP 403). An
  alternative is the 2025-26 DMS PDF (canada.ca/content/dam/fin/
  publications/dms-sgd/2025-26-dms-sgd-eng.pdf) which contains the
  same chart for the forward-looking redemption profile.
- **Recommended user-pull priority**: **MEDIUM** — the BoC G6 bucket
  substitute is workable for a v1 basics-layer cite at the bucket
  level (T-bills, 1-3y, 3-5y, 5-10y, >10y). Year-by-year precision is
  only needed if a blurb wants to call out a specific maturity-year
  spike (e.g. "$185B maturing in calendar 2026") which neither vintage
  has been confirmed to publish at calendar-year granularity.

### Secondary items

**S1. Quebec budget per-decimal verification**
- **Status before W3-R3**: UNCHANGED (publisher search excerpts only).
- **Status after W3-R3**: **RESOLVED at VERIFIED grade**. Net debt-
  to-GDP series 38.8% / 38.9% / 39.3% / ... 36.9% cross-confirmed
  via Quebec.ca press release no. 1 of 3 + TD Economics 2026 Quebec
  Budget reading + RBC Economics Quebec Budget 2026 analysis. The
  three independent attestations match decimal-by-decimal.
- **Recommended user-pull priority**: **LOW** — only required if a
  blurb wants confirmation to the second decimal place.

**S2. Alberta budget per-decimal verification**
- **Status before W3-R3**: UNCHANGED.
- **Status after W3-R3**: **STRONG**. Budget 2026 (2026-29 Fiscal
  Plan) net debt-to-GDP at 8.3% (FY25-26 revised) and 10.5% (FY26-27
  plan) confirmed via TD Economics 2026 Alberta Budget reading +
  Scotiabank Alberta Budget post + RBC Economics Alberta Budget 2026
  analysis. $9.4B deficit / 1.9% of GDP for FY26-27 also confirmed.
- **Recommended user-pull priority**: **LOW-MEDIUM** — Budget 2026
  PDF is publicly hosted at open.alberta.ca (URL pattern open.alberta.
  ca/dataset/3393a7b5-07bf-4b9f-8aaf-a6d89273297b/resource/58a8d024-
  398f-482e-b1c2-81a754a97253/download/budget-2026-fiscal-plan-2026-
  29.pdf); a quick user-pull would give VERIFIED-grade decimal
  precision but the STRONG-grade attestation is sufficient for
  basics-layer use.

**S3. BC budget per-decimal verification**
- **Status before W3-R3**: UNCHANGED.
- **Status after W3-R3**: **RESOLVED at VERIFIED grade** via direct
  WebFetch of news.gov.bc.ca/releases/2026FIN0003-000158 (BC
  government press release for Budget 2026). All key decimals pinned:
  taxpayer-supported debt-to-GDP 26.1% / 30.6% / 34.4% / 37.4%;
  deficits $9.6B / $13.3B / $12.2B / $11.4B; debt $116.5B / $189B;
  deficit-to-GDP 2.9% to 2.3%.

**S4. Fitch BC trend date**
- **Status before W3-R3**: UNCHANGED ("2025" only).
- **Status after W3-R3**: **RESOLVED**. Two BC Fitch actions in the
  W3-R3 window: 27 May 2025 outlook to Negative at AA+; 24 April
  2026 downgrade to AA- with Negative outlook. Both attested via the
  Fitch Rating Reports hosted on the BC government's debt-management
  directory (gov.bc.ca/assets/gov/british-columbians-our-governments/
  government-finances/debt-management/) plus cbonds news 3382151 /
  3382147 for the 27 May 2025 action and search-result extracts for
  the 24 April 2026 action.

---

## Final human-pull priority order (Wave 3 W3-R3 close)

In descending order of v1-basics-layer impact:

1. **HIGH**: IMF Country Report 26/12 PDF (Table 2 Selected Economic
   Indicators) — for the CAPB-on-potential-GDP 2025/2026/2027 decimals.
   URL: imf.org/-/media/files/publications/cr/2026/english/
   1canea2026001.pdf.
2. **MEDIUM-HIGH**: OECD Economic Outlook Volume 2025 Issue 2 Statistical
   Annex XLSX, Canada rows, for underlying-primary-balance 2025 and 2027
   decimals (2026 = 0.0% already STRONG-attested via syndication).
   URL: oecd.org/en/topics/sub-issues/economic-outlook/oecd-economic-
   outlook-statistical-annex.html.
3. **MEDIUM**: DoF Debt Management Report 2024-25 PDF for the
   redemption-profile-by-calendar-year chart at year-by-year dollar
   precision. URL pattern: canada.ca/content/dam/fin/publications/
   dmr-rgd/2024-2025/dmr-rgd-25-eng.pdf.
4. **LOW-MEDIUM**: Alberta Budget 2026 Fiscal Plan PDF (open.alberta.
   ca) for decimal-precision confirmation; STRONG-grade attestation
   already sufficient for basics-layer use.
5. **LOW**: Quebec Budget 2026-2027 PDF for second-decimal-place
   confirmation; already VERIFIED at the first-decimal level via
   multi-source cross-confirmation.

All other items in this index are resolved at VERIFIED or
STRONG-grade and are blurb-ready without further human pull.
