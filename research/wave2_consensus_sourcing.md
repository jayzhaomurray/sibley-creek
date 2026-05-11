# Wave 2 -- Consensus data sourcing for the surprise-framing override

Author: researcher
Date: 2026-05-10, revised 2026-05-11 (Big-Six URL sampling pass)
Status: scoping memo. No construction. No pipeline code touched.

Scope: per the 2026-05-10 EDR override (changelog entry of the same date),
the basics layer of GDP (Section 4.1 element 1), Inflation (Section 4.2
element 1), and Labour (Section 4.3 element 1) now anchors the
surprise-vs-expectation read to **market consensus first**, with the BoC
MPR central projection as the fallback when consensus is genuinely
unavailable. This memo scopes the practical data-sourcing question for
three prints: Canadian CPI, monthly GDP / quarterly GDP, and LFS.

Anchors:
- `editorial/dashboard_purpose.md` Sections 4.1, 4.2, 4.3 element 1 plus
  changelog (2026-05-10 override entry).
- Voice principle on Big-Six sourcing (Section 7): "Big-Six economics
  desks are competitors, not sources" -- applies to citation as authority,
  not to aggregating forecaster numbers as derived consensus inputs.

Conventions used below:
- "Paid feed" = closed-API or subscription-only access.
- "Free pipeline" = scrapable or downloadable without a paid licence at
  weekly-or-better cadence using only publicly available URLs.
- "Surprise" = print minus expectation, expressed in the print's native
  units (pp for rates, percent for growth, persons for jobs). The
  expectation enters as a number, not as a cited authority. The dashboard
  surfaces the surprise, attributes the expectation to "consensus" or
  "BoC MPR" as appropriate, and does not paraphrase any Big-Six note.

---

## 1. Inventory of consensus sources

The market produces several distinct objects that all get called
"consensus." They are not interchangeable.

### 1.1 Bloomberg Economist Survey (ECO function)

- **What it is.** Bloomberg's curated panel of contributing economists
  submits a forecast for each scheduled North American macro release.
  Bloomberg publishes median, mean, high, low, and the panel size for
  each indicator. This is the number Bloomberg's headline "Actual vs
  Survey" line refers to.
- **Coverage.** All major Canadian releases. CPI: headline M/M, headline
  Y/Y, core measures (trim, median, common). GDP: monthly real GDP M/M,
  quarterly real GDP Q/Q SAAR, sometimes Y/Y. LFS: net change in
  employment, unemployment rate, participation rate, wage growth.
  Panel sizes typically 15-25 for Canada-specific releases.
- **Recency.** Updated continuously up to the morning of the release.
  Locked at print time. Historical median series accessible back ~15
  years for the major releases.
- **Licensing.** Bloomberg Terminal or BPipe subscription. Closed.
  Republication of the median number in our prose is not a licensing
  violation if we are reporting a fact ("consensus was X"); republishing
  the panel composition or individual contributor names is.
- **Free-pipeline accessibility.** None directly. The median is
  routinely quoted in third-party press (Reuters wire stories, Globe
  ROB, Bloomberg's own free-tier articles) but those quotes lag the
  release by hours and are not always present.

### 1.2 Reuters poll medians

- **What it is.** Reuters runs its own pre-release poll of Canadian
  economists for major prints. The wire publishes the median, mean,
  range, and number of respondents in a story usually published 1-3
  business days before the print.
- **Coverage.** Canadian CPI (headline Y/Y, plus core trim and core
  median), monthly GDP M/M, quarterly GDP Q/Q SAAR, LFS net change and
  unemployment rate, BoC rate decisions. Panel size 20-40. Reuters
  also runs a quarterly Canadian macro survey (full-year GDP, year-end
  unemployment, year-end CPI) which feeds the medium-horizon
  expectations rather than print surprise.
- **Recency.** Published ~1-3 business days before the print. No mid-week
  revision once published.
- **Licensing.** Reuters Eikon / Refinitiv subscription for direct API.
  But the wire story is routinely republished free at the Reuters
  consumer site (reuters.com), the Globe ROB, BNN Bloomberg, and
  investing.com. The median number is widely surfaced.
- **Free-pipeline accessibility.** Moderate. Reuters wire URLs are
  predictable but not stable enough for automated scrape; the wire
  republication on Globe ROB / Reuters consumer site is HTML and
  scrapable but the URL changes per story. Realistic capture path =
  search by indicator name + month within the 48-hour pre-print window.
  Manual capture is reliable; automated capture requires per-story
  parsing.

### 1.3 Aggregated Big-Six bank forecasts (RBC, TD, BMO, Scotia, CIBC,
NBC)

- **What it is.** Each Big-Six bank's economics desk publishes its
  forecast for upcoming Canadian releases in a weekly preview document
  (variously called Week Ahead, Weekly Economic Watch, Daily Points,
  Talking Points, etc.) and / or a monthly forecast table. The
  "aggregated Big-Six forecast" is a simple median or mean of the six
  bank numbers, computed by us. This is the workhorse Canadian
  consensus when Bloomberg / Reuters are unavailable, and is what most
  Canadian financial press cites when no paid poll is referenced.
- **Coverage.** All six banks publish forecasts for: Canadian CPI
  (headline M/M and Y/Y at minimum; core trim and core median for at
  least four of six in print-week previews); monthly GDP M/M; quarterly
  GDP Q/Q SAAR; LFS net change and unemployment rate. Some also publish
  participation rate, hours, and wages. Per-bank publication and format:
    - RBC: "Financial Markets Daily" (PDF, daily), "Canadian Analysis"
      page, "Monthly Forecast Update" (PDF, monthly).
    - TD: "Canadian Quarterly Economic Forecast" (HTML and PDF,
      quarterly), "Canadian Weekly Bottom Line" (PDF, weekly),
      print-specific commentary on `economics.td.com` (HTML, per-print).
    - BMO: "Talking Points" (PDF, daily), "Focus" (PDF, weekly),
      "North American Outlook" (PDF, monthly forecast tables), per-
      country forecast PDFs (Canada, US, Provinces).
    - Scotia: "Global Week Ahead" (PDF, weekly, by Derek Holt),
      "Forecast Snapshot" (PDF, monthly), "Scotia Flash" (HTML+PDF,
      event-driven on Canadian prints).
    - CIBC: "The Week Ahead" (PDF, weekly, accessed via
      `economics.cibccm.com/cds` permalink URLs), "Forecast Update"
      (PDF, monthly), "Economic Flash" (PDF, event-driven on prints),
      "In Focus" (PDF, weekly thematic).
    - NBC: "Weekly Economic Watch" (PDF, weekly, stable URL at
      `www.nbc.ca/content/dam/bnc/taux-analyses/analyse-eco/`),
      "Monthly Economic Monitor - Canada" (PDF, monthly), "Monthly
      Fixed Income Monitor" (PDF, monthly with BoC-path forecasts).
- **Methodology for aggregation.** Standard practice in Canadian
  financial journalism is the median across the six. Mean is also
  defensible and slightly less robust to one outlier; the difference
  on a six-point panel is usually 1-2 bps. We adopt the median for
  publication and store both internally.
- **Recency.** Each bank publishes its weekly preview Friday afternoon
  or Monday morning for the coming week's prints. Monthly forecast
  tables refresh ~10 business days after each quarter's start; some
  banks update mid-quarter on major data surprises.
- **Licensing.** All six banks publish these PDFs on the open public
  web with no login required. The documents themselves carry the bank's
  copyright and a disclaimer; quoting an explicit point forecast for
  the purpose of computing an aggregated median, and citing the
  aggregate as "Big-Six median (RBC, TD, BMO, Scotia, CIBC, NBC)",
  is conventional fair use in Canadian financial publishing. We do
  not republish the bank notes themselves, we do not paraphrase their
  prose commentary in our prose, and we do not name the individual
  forecaster -- only the aggregate. This is the disposition the
  voice principle endorses: aggregated input, not cited authority.
- **Free-pipeline accessibility.** High. All six are publicly
  downloadable PDFs at stable enough URLs to script. Specifics
  in Section 3.

### 1.4 MNI / Action Economics

- **What it is.** Two North-American specialty firms that run pre-
  release economist polls for Canadian releases. MNI's poll is the
  one quoted by some institutional terminals as the "MNI median."
  Action Economics aggregates a smaller panel.
- **Coverage.** Major Canadian releases (CPI, GDP, LFS). Smaller panel
  than Bloomberg / Reuters (typically 5-15 economists for Canada).
- **Recency.** Pre-release.
- **Licensing.** Paid subscription. Republication of the median number
  in press is rare for Canadian prints.
- **Free-pipeline accessibility.** Effectively none.

### 1.5 C.D. Howe Monetary Policy Council

- **What it is.** A standing council of Canadian economists convened
  by the C.D. Howe Institute. Publishes a recommendation for each BoC
  fixed-announcement date (overnight rate level for the coming
  decision and the decision after). Also publishes a six-to-twenty-
  four-month rate-path recommendation. Not a forecast of prints; a
  policy recommendation that aggregates the policy views of senior
  Canadian economists.
- **Coverage.** BoC overnight rate only. Not CPI, GDP, or LFS prints.
- **Relevance to this memo.** Out of scope for surprise framing on
  CPI / GDP / LFS prints. Belongs in the Policy section's basics-layer
  surface for BoC rate decisions (Section 4.5 monetary sub-surface).
  Flagged here for completeness and to confirm it is not the right
  tool for this job.
- **Licensing.** Free. Published on cdhowe.org.

### 1.6 BoC MPR central projection (the fallback)

- **What it is.** The central projection table in the most recent
  Monetary Policy Report. Published quarterly (Jan, Apr, Jul, Oct).
  Numbers: real GDP growth quarterly path (Q/Q SAAR), CPI total
  inflation quarterly path (Y/Y), often with a labour-market
  reference in prose.
- **Coverage.** Quarterly path projections. The MPR does NOT publish
  monthly GDP forecasts, monthly CPI forecasts, monthly LFS forecasts,
  or quarterly unemployment-rate forecasts. The MPR's projection
  surface is coarser than the print surface.
- **Recency.** Updates four times a year. Between MPRs, the projection
  is stale relative to the data flow.
- **Licensing.** Free. Primary citation.
- **Why fallback, not primary.** Two reasons. First, granularity:
  the MPR projects quarterly aggregates; a monthly CPI surprise
  needs a monthly expectation, which the MPR does not publish.
  Second, staleness: an October MPR projection is six weeks old by
  the time the December CPI prints, and the projection is built off
  data the BoC had through mid-October -- it does not move with the
  weekly flow that market consensus reflects. The MPR remains the
  right anchor for medium-horizon framing ("Q4 CPI is tracking 0.3pp
  hotter than the BoC's April-MPR projection") and for prints where
  no consensus exists.

---

## 2. Practical recommendation per print

The disposition below assumes we do not have a paid Bloomberg or
Reuters feed in v1, and that the basics layer must refresh on the
publication's stated cadence (Section 6 of the EDR) without manual
intervention beyond once-weekly editorial capture. All three prints
share the same recommended architecture, with print-specific notes.

### 2.1 Canadian CPI (Section 4.2 element 1)

**Primary anchor (recommended).** Aggregated Big-Six median for
headline CPI Y/Y, headline CPI M/M, and the BoC's two preferred core
measures (trim and median). Computed from the six banks' weekly
preview PDFs as published in the print-week window.

**Tier-2 anchor (preferred-if-captured).** Reuters poll median,
captured from the Reuters wire story or Globe ROB republication in
the 48-hour pre-print window. When present, both numbers appear in
the methodology note; the surprise is shown against the Big-Six
median (since it is reliably captured) and the Reuters median is
noted as a consistency check. Where the two diverge by more than 5
bps on Y/Y headline, the blurb prose flags the dispersion.

**Fallback.** BoC MPR central projection for the print's reference
quarter. Stale by construction; cited explicitly when used ("vs the
April MPR central projection for Q2 CPI").

**Failure mode.** All six bank PDFs unavailable within 24 hours of
the print AND no Reuters poll. This is the regime where we fall to
MPR. In practice this has not happened in 15+ years of Canadian
print cadence.

**Quarterly vs monthly granularity.** The MPR projects quarterly Y/Y
paths. The Big-Six and Reuters polls publish monthly point forecasts.
For the basics-layer presentation of the monthly print, only the
monthly-granularity consensus is appropriate. The MPR fallback for
a monthly print is genuinely awkward and requires the writer to
state "the most recent quarter the MPR explicitly projects is X;
this month's print falls in that quarter."

### 2.2 Monthly GDP / Quarterly GDP (Section 4.1 element 1)

**Primary anchor (recommended).** Aggregated Big-Six median for
monthly real GDP M/M and quarterly real GDP Q/Q SAAR. Same capture
path as CPI: the six banks' weekly preview PDFs.

**Tier-2 anchor.** Reuters poll median, when published. Reuters
polls quarterly GDP reliably; monthly GDP somewhat less reliably
(some months no poll is published). Capture path same as CPI.

**Fallback.** BoC MPR central projection. For monthly GDP the
fallback is awkward (MPR projects quarterly Q/Q SAAR; monthly print
requires the writer to translate). For quarterly GDP the fallback
is clean -- the MPR's quarterly path is directly comparable. This
is one of the two prints where the MPR fallback is reasonably
serviceable.

**Note on the "advance" estimate.** StatCan publishes an advance
indicator with the monthly GDP release for the following month.
Some Big-Six previews quote a separate forecast for the advance
indicator alongside the headline print. Where the advance forecast
is published by enough banks (4+ of 6), include it; otherwise treat
as derived prose commentary.

### 2.3 LFS (Section 4.3 element 1)

**Primary anchor (recommended).** Aggregated Big-Six median for net
change in employment (jobs) and unemployment rate. These are the
two numbers all six banks reliably publish. Where 4+ banks also
publish participation rate or hours, include those as secondary
surprise reads.

**Tier-2 anchor.** Reuters poll median for net change in jobs and
unemployment rate. Reuters polls LFS reliably each month.

**Fallback.** BoC MPR central projection -- and here the fallback
is genuinely poor. The MPR does not publish a monthly LFS forecast,
does not publish a monthly unemployment-rate path, and references
labour conditions in prose more than in projection tables. Where the
MPR projects an annual-average unemployment rate, that is the only
serviceable fallback, and it is too coarse to surface as a print
surprise. **Recommendation: when consensus is genuinely unavailable
for LFS, drop the surprise framing entirely and surface only the
print itself with the prior-month and Y/Y context.** Do not force
the MPR fallback when the MPR doesn't speak at the print's
frequency.

### 2.4 Cross-print: the editorial outcome

For all three prints, the realistic state is: aggregated Big-Six
median is the primary anchor we can actually capture; Reuters poll
is a consistency check; MPR is the fallback for CPI and quarterly
GDP and is awkward-or-inappropriate for monthly GDP and LFS. The
2026-05-10 override does not require us to use the same anchor
across the three prints in every state; it requires market consensus
first, with MPR fallback when consensus is genuinely unavailable.
The above respects that.

---

## 3. Pipeline implications

A scoping note for backend-engineer. We do not touch `pipeline/` here.
The realistic capture difficulty for each surface:

### 3.1 Big-Six bank PDFs

| Bank | Publication | URL pattern | Format | Capture difficulty |
|---|---|---|---|---|
| RBC | Financial Markets Daily | `rbc.com/en/thought-leadership/economics/` hub; per-doc PDFs behind a redirect from listing card. Tested guess of stable `fmd_en.pdf` returns 404. | PDF | Medium-High. Hub URL is stable; per-PDF URL is dynamic per issue and requires HTML parsing of the hub. |
| RBC | Monthly Forecast Update | Same hub | PDF | Medium. Monthly cadence; same hub-parse path; easier to schedule. |
| TD | Weekly Bottom Line | `economics.td.com/ca-publications` listing; per-doc PDF | PDF | Medium. Listing page is HTML; per-PDF link discoverable per issue. |
| TD | Quarterly Economic Forecast | `economics.td.com/ca-quarterly-economic-forecast` | HTML + PDF | **Low**. Stable URL. Confirmed 2026-05-11: current issue dated 2026-03-17, landing page links to forecast-table sub-pages. |
| BMO | Focus / Talking Points / per-issue PDFs | `economics.bmo.com/en/publications/` listing | PDF | Medium. Listing requires HTML parsing for current per-issue PDF. |
| BMO | Forecast tables (Canada, US, Provinces, International, Commodities) | `economics.bmo.com/media/filer_public/<hash>/outlook<region>.pdf` direct PDF in Quick Links | PDF | **Low**. Confirmed 2026-05-11: direct PDF URLs visible in Quick Links section for US, Provinces, International, Commodities forecast tables. Per-hash URL is stable across issues; content refreshes in place. Canada-specific outlook PDF link was not fully exposed in the page sample and needs a second pass to confirm. |
| Scotia | Global Week Ahead, Daily Points, Scotia Flash | `scotiabank.com/ca/en/about/economics/economics-publications.html` listing; per-publication direct landing pages tested (`/economics-publications/the-global-week-ahead.html`) returned 404 | HTML cards (PDF on click) | Medium. Confirmed 2026-05-11: listing is HTML card grid, per-issue URL embedded in card; no global stable per-publication landing URL. Per-issue HTML parse required. |
| CIBC | Week Ahead / Forecast Update | `economics.cibccm.com/cds?id=<guid>` per-doc permalinks | PDF | Medium. Confirmed 2026-05-11: hub URL without query parameter returns HTTP 400; `economicsweb/cds` and `economicsweb/` variants return 404. The `cds?id=<guid>` permalink is the only viable form, and current-issue discovery is not solvable without either a listing-page scrape (path unknown) or a feed/RSS source we have not yet identified. **Open question**: confirm whether CIBC publishes a listing index or RSS at v1 scoping time before committing to CIBC inclusion. |
| NBC | Weekly Economic Watch | `www.nbc.ca/content/dam/bnc/taux-analyses/analyse-eco/weekly-economic-watch.pdf` | PDF | **Low**. Confirmed 2026-05-11: URL returns a 1.8MB PDF response with NBC publication metadata. Stable URL points at the current issue; same DAM-path pattern expected for Monthly Economic Monitor Canada and Monthly Fixed Income Monitor (URL forms to be probed in v1 scope). |

**The general capture path.** For each bank: (1) scrape the
publications listing page to find the URL of the current-week
preview PDF; (2) download the PDF; (3) extract forecast tables
using a PDF-text library (pdfplumber, pdfminer.six, or pypdf with
table support). Forecast tables in these documents follow stable
layouts -- typically a calendar-style table with date, indicator,
prior-month value, and "BMO" / "RBC" / "TD" forecast columns.

**The hard parts.**
- PDF table extraction is reliable for grid-based tables (TD, NBC
  monthly monitor) and unreliable for free-form layouts. Per-bank
  parser code is unavoidable -- this is not a single-template job.
- The forecast appears with different labels per bank ("BMO", "RBC
  Forecast", "Our Call", "NBF estimate"). Per-bank label mapping is
  required.
- Some banks publish two indicators of interest in two different
  documents (e.g. CPI in Week Ahead, jobs in a separate Flash). The
  scraper must know which document carries which forecast.
- The Reuters poll wire story has no stable URL. Capture is either
  manual (editorial paste) or requires a search-then-parse step
  per release. Realistic: manual capture for v1, automated if we
  add a Reuters Eikon feed later.

**Cadence.** Weekly preview PDFs publish Friday afternoon for the
coming week. A Friday-evening or Saturday-morning batch fetch covers
all six banks for the coming week's prints. Monthly forecast tables
refresh ~10 business days after each quarter's start.

**Realistic v1 scope.** After the 2026-05-11 URL sampling pass, the
revised v1 capture candidate set is **NBC + TD + BMO**: NBC has a
fully stable DAM PDF URL; TD has a stable HTML+PDF landing page for
its quarterly forecast; BMO has stable hash-permalink PDFs for its
regional forecast tables (US, Provinces, International, Commodities --
Canada-specific path still to be confirmed). CIBC is **demoted** from
the previous v1 candidate list because the hub URL pattern
(`economics.cibccm.com/cds`) requires per-doc GUIDs and has no
discoverable listing index from outside, pending an RSS / feed find.
RBC and Scotia require per-issue HTML parsing of their listing pages
and are second-pass work. Fall back to **manual editorial capture**
of the other three banks until parsers are verified. A three-bank
median is statistically defensible for a basics-layer surprise read
provided we name the source ("TD, BMO, NBC median") and not
"Big-Six median" -- the label has to be honest. Once parsers for the
remaining three are in, promote the label.

**Versioning.** Each forecast capture must be stamped with the bank,
publication name, publication date, and the URL the PDF was
downloaded from, so the fact-checker can audit. This is the
researcher-side discipline; the pipeline only needs to preserve
those four fields end-to-end.

### 3.2 Reuters poll

Realistic v1 disposition: **manual editorial capture.** Once per
release-week, the editorial-director or writer pastes the Reuters
median number from the wire story into the research index with the
URL of the story. Automation is a v1.5 lift requiring a Reuters
search-and-parse component and not worth the effort if the
Big-Six aggregate is already serving as primary anchor.

### 3.3 BoC MPR fallback

Already a primary source we cite elsewhere. No new capture required.
The MPR projection numbers live in the research index as a small
versioned object stamped with the MPR vintage (e.g. "Apr 2026 MPR
Table 1") and updated quarterly on each MPR release. The writer
queries the same object for the surprise read when consensus is
unavailable.

---

## 4. Fallback policy

The 2026-05-10 override makes BoC MPR projection the fallback when
consensus is genuinely unavailable. We need to be specific about when
that condition obtains.

### 4.1 Consensus is captured -- use it

For CPI (headline + cores), monthly GDP, quarterly GDP, LFS net
change, and LFS unemployment rate, the aggregated Big-Six median is
captured every print week. **This is the steady state for the three
prints named in the override.** The fallback case for these prints
is rare and corresponds to the pipeline being broken, not to a
data-availability gap.

### 4.2 Consensus is genuinely unavailable -- use MPR

A consensus median is "genuinely unavailable" when:
- None of the Big-Six published a forecast for the indicator in the
  current print cycle (e.g., a less-watched sub-indicator). For CPI
  headline / cores, monthly GDP, quarterly GDP, LFS net change, and
  unemployment rate, this does not occur in practice.
- The pipeline fails to capture the bank PDFs in the print window
  AND no Reuters median has been manually captured. Operational
  failure; the response is to fix the pipeline, not to publish a
  stale-MPR surprise. Editorial-director's call on whether the
  basics-layer ships without a surprise read in that print cycle.

### 4.3 Prints where consensus does not exist (the MPR-steady-state cases)

These are not among the three prints covered by the 2026-05-10
override, but are scoped here for completeness so future Wave 2 work
on other sections knows the disposition:

- **Sub-indicators inside the CPI release** (e.g., shelter-ex-mortgage-
  interest, services-ex-shelter, breadth metrics): no consensus
  exists. MPR is too coarse to project these. Surface the print
  itself with prior-month and Y/Y context; no surprise framing.
- **GDP contributions and per-capita GDP**: no consensus exists for
  the decomposition. Surface the print; the BoC reaction in the next
  MPR cycle is editorial commentary, not surprise framing.
- **Wage band measures, vacancy rates, JVWS prints**: no Reuters or
  Bloomberg poll. Some banks forecast wages; aggregated Big-Six
  median is the only consensus surface that exists. Use where
  available; surface without surprise where unavailable.
- **CMHC arrears, FDI, current account, terms of trade, partner-share
  series**: no consensus. MPR does not project. Print-only.
- **Provincial budgets, Fiscal Monitor**: PBO baseline and previous
  vintage are the comparator. Not consensus territory.

For these less-watched prints, the fallback policy is not MPR-vs-
consensus but **surface-the-print-with-context, no surprise framing**.
The MPR fallback is steady state only for headline indicators the MPR
explicitly projects -- which on the three-print list of this memo
means quarterly GDP and CPI headline Y/Y on a quarterly average basis.

---

## 5. Open questions for editorial-director

These are the calls where this researcher would want the EDR to
decide before backend-engineer scopes the capture pipeline:

1. **Three-bank vs six-bank median for v1.** Do we ship the basics
   layer with a three-bank (NBC + TD + BMO, post-2026-05-11
   sampling) median labelled accurately while the other three
   parsers come online, or wait for all six? Recommendation: ship
   the three-bank median at v1, relabel to Big-Six median once the
   other three are verified. But this is an editorial call about
   how transparent we want to be in the early-issue versions about
   the panel composition.

2. **Reuters poll: manual or automated v1.** Manual capture is
   reliable and low-effort if the editorial-director or writer is
   already opening Reuters / Globe ROB on print mornings. Automated
   capture is a non-trivial lift. Recommendation: manual for v1, no
   automation work scoped. The aggregated Big-Six median is the
   primary anchor; Reuters is the consistency check; the consistency
   check does not need to be automated. EDR confirms?

3. **Disclosure of the consensus methodology.** The principle file we
   were asked to read (`memory/feedback_consensus_input_vs_citation.md`)
   does not exist in the repo; the principle itself is captured in
   the 2026-05-10 changelog entry. We will need a public methodology
   note on the dashboard explaining "consensus = aggregated Big-Six
   median (RBC, TD, BMO, Scotia, CIBC, NBC), refreshed weekly from
   each desk's published economics weekly". That note both honors
   show-your-work (voice principle) and pre-empts any reader
   confusion about why we cite "consensus" when the voice principle
   says we don't cite Big-Six. EDR sign-off on the wording is
   needed once the note is drafted -- not in this memo's scope, but
   flagged.

4. **Granularity mismatch on monthly prints when MPR is fallback.**
   When consensus is genuinely unavailable for a monthly CPI or
   monthly GDP print, the MPR's quarterly projection is the only
   anchor, and the writer has to translate. Do we publish a
   surprise read in that state at all, or do we drop the surprise
   framing for that print cycle and surface only the print with
   context? Recommendation: drop the surprise framing for the
   cycle and say so explicitly in the blurb ("consensus capture
   missed this week; MPR projects 2.1% Q/Q SAAR for the quarter
   this print falls in, equivalent to roughly 0.17% M/M if evenly
   distributed -- not a meaningful surprise comparison"). EDR
   call on whether even that level of inference is acceptable, or
   whether silence is cleaner.

5. **LFS unemployment rate surprise.** All six banks publish a
   forecast for the LFS unemployment rate, but the surprise is
   often within a tenth of a percentage point of the consensus
   (LFS U/R is sticky). Is a tenth-of-a-point surprise material
   enough to surface as the basics-layer headline surprise read?
   Recommendation: yes -- the LFS U/R reaction is the political-
   economy variable in Canada (BoC reaction function, leadership
   debate), so even a small surprise matters. But this is style,
   and the style-editor will want a view too.

6. **MNI / Action Economics.** Should we attempt to acquire either
   feed at v1.5? Marginal benefit over Big-Six median is small for
   Canadian prints; cost is real. Recommendation: no, not in the
   v1 or v1.5 lift. Re-evaluate at v2 if a Bloomberg / Reuters
   institutional feed becomes available -- at which point the
   Bloomberg / Reuters median directly replaces the Big-Six
   aggregate as primary anchor and the Big-Six aggregate becomes
   the consistency check.

7. **CIBC discoverability.** After 2026-05-11 sampling, the
   `economics.cibccm.com/cds` hub returns HTTP 400 without a GUID
   query parameter, and no listing index is visible from outside.
   Realistic options: (a) defer CIBC from v1 capture and accept a
   five-bank ceiling at parser maturity; (b) attempt manual editorial
   capture of CIBC's Week Ahead PDF GUIDs once per print cycle; (c)
   ask CIBC for RSS or a JSON listing endpoint via institutional
   contact. Recommendation: (b) for v1, (c) as a follow-up;
   acceptable to defer CIBC parser to post-v1. EDR call on whether
   it is acceptable to call the median "Big-Five median (RBC, TD,
   BMO, Scotia, NBC)" if CIBC discoverability stalls, since the
   panel is then five not six and the label has to be honest.

8. **BMO Canada-forecast PDF.** The 2026-05-11 sampling found that
   BMO publishes direct-PDF forecast tables for US, Provinces,
   International, and Commodities at stable `/media/filer_public/<hash>`
   URLs; the Canada-specific forecast PDF link was not fully visible
   in the page sample. Operational follow-up before backend-engineer
   scopes the BMO scraper: confirm the Canada-forecast PDF URL by a
   second sampling pass or by HTML-inspecting the Quick Links block.
   This is a verification task, not an editorial call -- flagged here
   because v1 capture from BMO depends on the Canada forecast being
   the right document, not US/International outlook.

---

## 6. Summary recommendation in one paragraph

For all three prints covered by the 2026-05-10 override (CPI,
monthly and quarterly GDP, LFS), the practical primary anchor is
the **aggregated Big-Six median** computed from the six banks'
publicly accessible weekly preview PDFs; the **Reuters poll
median** when manually captured is a consistency check; the **BoC
MPR central projection** is the fallback for the small number of
print cycles where the pipeline fails to capture bank PDFs and no
Reuters median is on hand. The MPR's quarterly granularity makes
it a clean fallback for quarterly GDP, a serviceable fallback for
quarterly-average CPI Y/Y, an awkward fallback for monthly CPI and
monthly GDP, and an inappropriate anchor for LFS (the MPR does
not project LFS at the print's frequency). Realistic v1 scope:
ship with a three-bank median (NBC + TD + BMO -- the 2026-05-11
sampling pass found these three have the cleanest URL patterns,
demoting CIBC from the previous draft list because its hub URL
requires per-doc GUIDs with no discoverable listing) and a manual
Reuters consistency check; bring the other three banks online
iteratively. The voice-principle
disposition holds: the bank forecasts enter as derived numerical
inputs that get aggregated into "consensus", and "consensus" is
the label that appears in our prose -- never any individual
bank's name as cited authority.

---

## Appendix A. Big-Six URL sampling log, 2026-05-11

For audit: URLs probed during the 2026-05-11 revision pass, with
outcome. WebFetch was the tool; status reflects what the live URL
returned at sampling time.

| Bank | URL probed | Status | Note |
|---|---|---|---|
| NBC | `www.nbc.ca/content/dam/bnc/taux-analyses/analyse-eco/weekly-economic-watch.pdf` | 200 (PDF) | 1.8MB PDF returned; NBC publication metadata embedded. Stable. |
| TD | `economics.td.com/ca-quarterly-economic-forecast` | 200 (HTML) | Current issue dated 2026-03-17. Quarterly cadence. Links to sub-pages for forecast tables. Stable landing page. |
| RBC | `www.rbc.com/en/thought-leadership/economics/` | 200 (HTML) | Hub page lists Canadian Analysis, US Analysis, Monthly Forecast Update, 10-Min Take, Financial Markets Daily. No stable per-publication URLs visible from hub copy. |
| RBC | `www.rbc.com/en/thought-leadership/economics/fmd_en.pdf` | 404 | Guessed stable PDF path inferred from hub-page link reference; does not resolve. RBC capture requires per-issue HTML parse. |
| BMO | `economics.bmo.com/en/publications/` | 200 (HTML) | Listing hub. Quick Links block contains direct PDF URLs for US, Provinces, International, Commodities outlook tables: `/media/filer_public/<hash>/outlook<region>.pdf` pattern. Canada-specific link not fully exposed in the sample. |
| Scotia | `www.scotiabank.com/ca/en/about/economics/economics-publications.html` | 200 (HTML) | Card-grid listing. Daily Points, Global Week Ahead, Scotia Flash visible. Per-publication URLs embedded in cards; no global stable per-publication landing. |
| Scotia | `www.scotiabank.com/ca/en/about/economics/economics-publications/the-global-week-ahead.html` | 404 | Tested guess at a stable per-publication landing; does not resolve. |
| CIBC | `economics.cibccm.com/cds` | 400 | Hub URL requires query parameter. |
| CIBC | `economics.cibccm.com/economicsweb/cds` | 404 | Alternate path guess; does not resolve. |
| CIBC | `economics.cibccm.com/economicsweb/` | 404 | Alternate hub guess; does not resolve. |

URLs marked 200 are accessible and the description in Section 3.1
of this memo reflects content visible on that page on 2026-05-11.
URLs marked 404 / 400 are documented here so future passes do not
re-probe the same dead paths. No paid feed or authenticated source
was used for any sampling above; all probes were anonymous GETs.

---

End of memo.
