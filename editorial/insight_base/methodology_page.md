# Methodology page: insight base

Owner: researcher. For writer use only -- this file is fact scaffold,
not prose. Every claim about Sibley Creek's data sourcing, refresh
cadence, revisions discipline, and editorial process that lands on
/methodology/ should trace back to a row in this file.

Tier definitions (same as `about_page.md`):
- **CANON** -- documented in a committed project file
  (editorial/, design/, src/, pipeline/, data/SOURCES.md). Writer can
  state directly.
- **INFERRED FROM SESSION CONTEXT** -- supplied in the present task
  brief; not in committed canon. Writer should hedge or omit.
- **OPEN** -- needs editorial-director decision before drafting.

Anchors read:
- `data/SOURCES.md` (per-source documentation, pipeline-side)
- `pipeline/io/site_data.py` (section-to-vector mapping)
- `pipeline/fetch/__init__.py` and `pipeline/fetch/<source>.py` (each
  source's actual fetcher)
- `editorial/dashboard_purpose.md` Section 6 (cadence canon) and
  Section 7 (voice -> sourcing rules)
- `editorial/writing-style.md` Section 8 (consensus + surprise prose)
- `editorial/auto_blurb_process.md` (Mode 2 pipeline architecture)

---

## 1. The data sources Sibley Creek actually uses

**Important distinction.** The user task brief named **nine** primary
sources (StatCan, BoC, CREA, DoF Canada, CBA, OSFI, CMHC, FRED, Yahoo
Finance). The pipeline today wires **seven** of those plus Alberta
Economic Dashboard, plus C.D. Howe BCC as a hand-curated input. OSFI
and CMHC are **deferred to a future wave** per `data/SOURCES.md`
("CMHC, OSFI, PBO ... CMHC arrears and Rental Market Survey deferred
to a future wave; OSFI Bank Financial Data M4 ... deferred to Wave
3"). Treat the methodology page as accurate to the live pipeline,
not aspirational.

### 1.1 Currently wired (the live tracker)

All entries below are **CANON** -- grounded in `data/SOURCES.md` and
`pipeline/fetch/*.py`.

| Source | What we pull | Cadence | Module |
|---|---|---|---|
| **Statistics Canada (StatCan)** | CPI (headline + BoC core trim/median; sub-aggregates), Labour Force Survey (unemployment, employment, participation, wages), monthly GDP by industry (Table 36-10-0434), quarterly GDP by expenditure (Table 36-10-0104), merchandise trade balance, housing starts, CMA-level population, the CPI basket-weight table (18-10-0007-01) | Monthly (CPI, LFS, GDP, trade); quarterly (GDP by expenditure, current account); five-yearly basket-refresh cycle | `pipeline/fetch/statcan.py` (WDS endpoint `getDataFromVectorsAndLatestNPeriods`, vector-ID addressing) |
| **Bank of Canada (BoC) Valet** | Overnight rate target (V39079; STATIC_ATABLE_V39079 for long history), benchmark bond yields (2y/5y/10y/30y GoC), USDCAD spot, CORRA, CSCE consumer expectations, BOS firm expectations, output gap (`INDINF_OUTGAPMPR_Q`), commodity price indices (BCPI, BCNE), Financial Vulnerability Indicators | Daily for yields/FX/CORRA; quarterly for survey series; event-driven for rate decisions (eight per year on Fixed Announcement Dates); weekly for balance-sheet series | `pipeline/fetch/boc.py` (`/observations/{series_key}/json`) |
| **FRED (Federal Reserve Bank of St. Louis)** | US Treasury yields (DGS2, DGS10), Fed funds target (FEDFUNDS / DFEDTARU+DFEDTARL midpoint), VIX (VIXCLS), IG and HY corporate OAS (BAMLC0A0CM, BAMLH0A0HYM2), oil prices (DCOILWTICO, DCOILBRENTEU) | Daily for daily series; monthly for FEDFUNDS | `pipeline/fetch/fred.py` |
| **Yahoo Finance** | TSX Composite (`^GSPTSE`), S&P 500 (`^GSPC`), COMEX gold front-month (`GC=F`) | Daily close | `pipeline/fetch/yahoo.py` |
| **CREA (Canadian Real Estate Association)** | MLS HPI -- national + six CMA aggregates (Toronto, Vancouver, Montreal, Calgary, Ottawa, Edmonton), Seasonally Adjusted Monthly XLSX | Monthly, ~3-week lag from reference month | `pipeline/fetch/crea.py` (bulk XLSX ZIP) |
| **Department of Finance Canada -- Fiscal Monitor** | Federal monthly + YTD budgetary balance, revenues, expenses, debt-service charges, financial source/requirement | Monthly, ~2-month publication lag | `pipeline/fetch/dof_fiscal.py` (HTML scrape) |
| **Canadian Bankers Association (CBA)** | National monthly residential mortgage arrears (% of stock), provincial cross-section for the latest month | Monthly, ~2.5-month publication lag. Covers chartered banks (BMO, CIBC, NBC, RBC, Scotia, TD) plus Manulife/Laurentian/Equitable -- roughly 75% of stock; brokered / private / credit-union excluded | `pipeline/fetch/cba_arrears.py` (PDF parse) |
| **Alberta Economic Dashboard** | Alberta natural-gas reference price (AECO-equivalent monthly settle); WCS oil price deferred | Monthly | `pipeline/fetch/alberta.py` |
| **C.D. Howe Business Cycle Council** | Canadian recession dating (hand-curated from BCC communiques) | Roughly twice yearly; communique-driven | `data/derived/cdhowe_bcc_recessions.json` (editorial-curated, no fetcher) |

### 1.2 Deferred (referenced in canon, not yet wired)

**CANON-grounded as deferred** (per `data/SOURCES.md` "To add as
scoped" section and `pipeline/fetch/__init__.py` deferral notes):

- **OSFI** -- Bank Financial Data (uninsured residential mortgage
  exposure, CET1 ratios). Deferred to Wave 3 per `data/SOURCES.md`.
- **CMHC** -- Arrears (RMIR) and Rental Market Survey. Deferred to a
  future wave per `data/SOURCES.md`.
- **PBO (Parliamentary Budget Officer)** -- Economic and Fiscal
  Outlook. Deferred per `data/SOURCES.md`.
- **BIS** -- peer central bank policy rates (BoE, RBA, ECB).
  Deferred per `pipeline/fetch/__init__.py` Wave 3 / v1.5 note.

Writer guidance: the methodology page should describe the sources that
are actually live. Listing OSFI and CMHC as "sources we use" today is
not honest. Two options:

1. **List only live sources** on /methodology/ -- the seven plus
   Alberta plus C.D. Howe. This is the conservative path.
2. **List live sources + a "coming next" note** that names OSFI, CMHC,
   PBO, BIS as planned additions. This is the more transparent path
   and aligns with the publication's "show your work" principle.

Strongly recommend option 2: it earns the methodology page's voice and
matches the "honest about what we do not yet know" canon.

## 2. Cadence per indicator class

**CANON** (`editorial/dashboard_purpose.md` Section 6 +
`data/SOURCES.md`):

The 2026 Canadian release calendar that anchors Sibley Creek:

- **BoC fixed announcement dates 2026**: Jan 28, Mar 18, Apr 29, Jun
  10, Jul 15, Sep 2, Oct 28, Dec 9. (`dashboard_purpose.md` Section 6.)
- **Monetary Policy Report (MPR)**: alongside Jan, Apr, Jul, Oct rate
  decisions.
- **LFS**: first Friday of the month after the reference month, 8:30
  AM ET. (`data/SOURCES.md`.)
- **CPI**: typically the third Tuesday of the month after the
  reference month, 8:30 AM ET. (`data/SOURCES.md`.)
- **Monthly GDP by industry** (Table 36-10-0434): ~60-day lag after
  reference month.
- **Quarterly GDP by expenditure** (Table 36-10-0104): ~60 days after
  reference quarter.
- **BoC Summary of Deliberations**: two weeks after each rate
  decision.
- **Financial System Review**: typically May and November.
- **Federal Budget**: Feb-Mar.
- **Fall Economic Statement**: Nov-Dec.
- **Fiscal Monitor**: monthly with two-month lag.
- **Trade**: monthly, ~30-day lag.
- **CREA HPI**: monthly, ~3-week lag.

**Tracker cadence by section** (`dashboard_purpose.md` Section 6):

| Section | Cadence | Primary trigger |
|---|---|---|
| GDP | Monthly + quarterly | StatCan monthly GDP by industry; quarterly GDP by expenditure |
| Inflation | Monthly | StatCan CPI (mid-month) |
| Labour | Monthly | LFS (first Friday); SEPH; quarterly population estimates |
| Housing | Monthly | StatCan housing starts; CREA MLS HPI; CMHC arrears (deferred -- use CBA arrears as proxy) |
| Policy (Monetary) | Event-driven | BoC rate decisions, MPR, Summary of Deliberations, FSR |
| Policy (Fiscal) | Monthly + event | DoF Fiscal Monitor; Budget; FES; PBO; provincial budgets |
| Markets | Daily + weekly synthesis | BoC Valet daily series; weekly close summary |
| Trade | Monthly + event | StatCan merchandise trade; quarterly current account; USMCA / 232 / 301 events |

**Annual peak periods** (`dashboard_purpose.md` Section 6): Federal
Budget (Feb-Mar), provincial budget season (Feb-May), Fall Economic
Statement (Nov-Dec), USMCA review / Section 232/301 windows. Cadence
ramps; the site publishes off the listed cycle when these are live.

## 3. Revision and vintage discipline

**CANON** (`data/SOURCES.md` "Vintage / revision conventions" per
source) + **CANON-by-implication** (no editorial doc explicitly
states the "show latest vintage as-is" policy, but the pipeline
behaviour does):

- **Each release has both a `release_date` and a `reference period`.**
  StatCan's WDS surfaces both via `releaseTime` and the observation
  date. The pipeline records `release_date` in the per-series
  `.meta.json` sidecar. (`data/SOURCES.md` StatCan section;
  `pipeline/fetch/statcan.py`.)
- **Monthly series typically revise the prior 1-3 observations** on
  each release.
- **LFS revises only the prior month.**
- **GDP revises further** (often the prior two quarters), so the
  same vector pulled today vs a month ago can show different
  historical values.
- **The site shows the latest StatCan/BoC vintage as-is and does not
  silently restate prior values.** Revisions flow through on the next
  pipeline build. (Pipeline behaviour; not stated as such in any
  editorial doc, but consistent with the project's "show your work"
  canon. **OPEN**: editorial-director can ratify or refine this
  statement.)
- **Vintage history is not yet preserved.** Per `data/SOURCES.md`:
  "We do not preserve vintage history in the pipeline yet. If a
  story requires 'what did this look like as of date X,' that's a
  planned enhancement -- capture the release vintage at fetch time
  and pin it on disk in a vintage-tagged subdirectory."
- **CPI basket refresh** (`data/SOURCES.md` StatCan section): the
  basket updates every five years (2003, 2009, 2013, 2018, 2023; with
  the 2022 cycle StatCan moved toward roughly-annual basket-weight
  refreshes; the 2024 basket applies through ~2029). Cross-basket
  levels are not strictly comparable; Y/Y changes are because StatCan
  chains the index across baskets.
- **CREA back-revises ~3 prior months** as late-closing sales report
  in.
- **Each new Public Accounts release (typically December)** restates
  the prior fiscal year for the Fiscal Monitor.

Writer guidance: the revisions section of /methodology/ should make
two clear points: (1) StatCan and BoC revise their own data, and the
site reflects the latest vintage on each rebuild; (2) the site does
NOT silently restate or backfill prior published commentary -- the
chart updates to current vintage; the published blurb attached to the
chart at the time it shipped is the read-of-the-day for that release.
Point 2 is INFERRED-by-implication from the auto-blurb process; flag
to editorial-director if writer wants to state it strongly.

## 4. What "TK" markers mean

**CANON** (`src/data/sections.ts` placeholder rows and the comment
block at lines 1-43; `pipeline/io/site_data.py` "Failure policy"
section at lines 44-53):

- "TK" appears in print rows on the homepage and section pages when a
  primary series CSV is missing or malformed -- the loader cannot
  fill the row with real data.
- TK is a **visible gap, not a fake number**. The reader sees "TK"
  rather than a stale or fabricated value.
- TK is expected during v1 ship while series are being progressively
  wired. The current sections.ts comment block names this explicitly:
  "TK markers here are visible only when the pipeline payload is
  unavailable" (e.g. the headline-CPI row for Inflation; the
  unemployment-rate row for Labour). When pipeline data lands, the
  loader overwrites the TK scaffold.
- The pipeline's per-section construction is wrapped in try/except:
  "if a section's primary series CSV is missing or malformed, we emit
  a sentinel entry with the section's slug, an `error` string
  explaining what was missing, and an empty prints[] list. The
  frontend can render the existing placeholder content for that
  slot." (`pipeline/io/site_data.py` lines 44-53.)

Writer guidance: the methodology page should disclose what TK means.
Recommended phrasing direction (not prose): "TK is a placeholder for
data not yet wired. You will see it on tiles where a primary series
is missing; we leave the gap visible rather than fill it with a stale
or fabricated number."

## 5. The auto-blurb pipeline (Mode 2)

**CANON** (`editorial/auto_blurb_process.md` Sections 1 + 1.1 + 1.2;
`editorial/dashboard_purpose.md` Sections 3 Mode 2, 7 voice, 9
success criterion 3):

High-level overview only; the methodology page does not need to
detail the full state machine.

- Mode 2 = automated event blurbs. A short interpretation paragraph
  (two to four sentences) is generated against a release-triggered
  template when a key data print lands.
- The cycle has multiple roles: researcher drafts a structured
  release-context note with verified claim-cards; a separate verifier
  re-fetches every primary-source URL and locates each claim verbatim
  in the source text; writer drafts the blurb; fact-checker validates
  against the verified cards; style-editor polishes voice;
  **editorial review (human) gates publish**.
- **The human-review gate stays.** "Eventually fully automated on
  the data-fetch side; the human review gate stays."
  (`dashboard_purpose.md` Section 3 Mode 2.) Reinforced as success
  criterion 3 in Section 9: "Mode 2 (auto-blurb) is operating on at
  least three sections... with each blurb passing human review before
  publish. The human review gate stays; full automation of the
  data-fetch side is the path, not the destination."
- **Currently built but not yet running live.** (INFERRED FROM
  SESSION CONTEXT, user brief: "currently built but not yet running
  live." Also consistent with the success criteria in
  `dashboard_purpose.md` Section 9 which sets November 2026 as the
  target for Mode 2 operating on three sections, and with the
  `editorial/blurbs/_inbox.md` referenced in the auto-blurb process
  doc as the user's review queue.)

Writer guidance: the methodology page should state honestly that Mode
2 is built and gated on editorial approval before publish. It should
NOT claim Mode 2 is live or that blurbs are being routinely produced
today. If the writer wants a forward-looking line ("we are turning
this on across Inflation, Labour, and Policy in 2026"), that mirrors
canon success-criterion 3 and is safe.

## 6. Voice rules that affect methodology disclosure

**CANON** (`editorial/dashboard_purpose.md` Section 7;
`editorial/writing-style.md` Sections 1 and 8):

These are voice rules the methodology page itself must obey and that
its content can describe.

- **Primary-source citation only.** Sibley Creek cites Statistics
  Canada, the Bank of Canada, OSFI, CMHC, the Department of Finance,
  the PBO, provincial finance ministries, C.D. Howe BCC, IRPP, BIS,
  IMF Article IV Canada, OECD Economic Surveys.
- **Big-Six economics desks are not cited as authority.** RBC, TD,
  BMO, Scotia, CIBC, National Bank are read daily as competitors.
  They are measured against, not quoted as a view.
- **Big-Six numbers MAY enter as aggregated "consensus" input.**
  (`writing-style.md` Section 8.) Market consensus (Bloomberg /
  Reuters median, or aggregated forecaster median where the paid feed
  is unavailable) is a derived numerical input to surprise framing.
  The aggregated number enters as a comparator; individual desks do
  not enter as voices.
- **BoC MPR central projection is the fallback** when market consensus
  is genuinely unavailable. The MPR is a citation, not just an input;
  named directly and dated.
- **Methodology one click away** on every constructed chart.
  ("Show your work." `dashboard_purpose.md` Section 7.)
- **No black boxes.** Success criterion 7
  (`dashboard_purpose.md` Section 9): "For every constructed chart, a
  methodology note explains the construction, the data vintage, and
  the sensitivity to key assumptions."

Writer guidance: the methodology page is the natural place to state
the consensus / Big-Six distinction explicitly. Recommended structure:
a short paragraph that says (a) Sibley Creek cites primary sources,
(b) we read Big-Six bank notes daily but do not quote them, (c) when
a market consensus number is the natural comparator on a print, we
report the aggregated forecaster median as a number, not as a view.

## 7. The chartbook unit (editorial atom)

**CANON** (`editorial/dashboard_purpose.md` Sections 3, 4, 7;
`editorial/writing-style.md` Section 7):

Useful to ground the methodology page in.

- The **chartbook unit** = one chart paired with a 2-to-4-sentence
  interpretation paragraph. This is "the publication's editorial
  atom" (`dashboard_purpose.md` Section 3 Surface 2).
- The atom is the same in Mode 2 (auto-blurb on a fresh print) and
  Mode 3 (deep-dive prose scaffolded by atoms).
- "Strip away the chart and the paragraph should still read as a
  defensible sentence about Canada; strip away the paragraph and the
  chart should still be legible. They are co-equal."
  (`dashboard_purpose.md` Section 7.)

Writer note: the methodology page does not need to invoke the
"chartbook unit" term explicitly, but the underlying principle --
chart and paragraph are co-equal, every interpretation paragraph
sits next to its supporting chart -- is useful context.

## 8. Reproducibility / analytical scripts

**CANON** (`dashboard_purpose.md` Section 7 "Show your work" and
Section 9 success criterion 7):

- Constructed series have a methodology note "one click away."
- For every constructed chart, a methodology note explains the
  construction, the data vintage, and the sensitivity to key
  assumptions.
- Reproducible analysis scripts live in `analyses/` (e.g.
  `analyses/usdcad_percentile_2026_05_11.py`,
  `analyses/inflation_anchors_2026_05_11.py`). This convention exists
  in repo and matches the researcher-role brief at the project root.

## 9. Pipeline build cadence (the rebuild rhythm)

**OPEN.** No editorial doc states the rebuild rhythm explicitly.
`pipeline/io/site_data.py` is the build module; it emits
`data/site/sections.json` consumed by the Astro build. The README at
project root or a separate `pipeline/README.md` (if it exists) would
be the canon source for "the site rebuilds at X cadence." Defer to
editorial-director / backend-engineer for the disclosed rebuild
rhythm if the methodology page needs to state it. Alternative: the
methodology page can stay silent on rebuild rhythm and instead state
that each section refreshes when its primary release lands.

## 10. Open questions for the writer

- **OSFI / CMHC framing.** Do we list them as deferred (recommended)
  or omit until wired? Decision needed from editorial-director.
- **Rebuild-cadence disclosure** (Section 9 above). Decision needed.
- **Vintage-restatement policy** (Section 3, the "show latest
  vintage as-is" statement). Recommended to canonize so the
  methodology page can state it directly.
- **The BoC MPR mention.** The methodology page can mention the MPR
  as a primary source and as the consensus fallback; it does NOT need
  to enumerate every MPR section the site pulls from. The chartbook
  units themselves cite per-panel.
- **Tone for the auto-blurb section.** Recommended honest framing:
  "built, gated, ramping" rather than "live across the dashboard."
  Decision needed if writer wants a stronger statement.

---

End of methodology-page insight base. Researcher will update this
file as canon evolves and as OSFI / CMHC / PBO / BIS get wired.
