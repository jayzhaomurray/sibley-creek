# Data Sources

This file is the editorial-grade audit trail for every upstream data source
wired into the pipeline. For each source we document: where to find the data,
how the API addresses series, the release schedule, units / vintage quirks,
known gotchas, and the .meta.json fields the pipeline records for traceability.

Adding a new source: add a section here BEFORE the fetcher lands.

---

## Statistics Canada — Web Data Service (WDS)

**API base:** `https://www150.statcan.gc.ca/t1/wds/rest/`
**Pipeline module:** `pipeline/fetch/statcan.py`
**Endpoint used:** `getDataFromVectorsAndLatestNPeriods` (POST)
**Authentication:** none required. No published rate limit, but the service
is shared and can return 503 under load — the pipeline retries with
exponential backoff (see `pipeline/fetch/_http.py`).

### Addressing

We address series by **vector ID**, the V-prefixed integer in StatCan tables
(stored without the V prefix in the catalog code). Vectors are stable across
the CANSIM-to-Table-ID migration that completed in 2018; Cube + Coordinate
addressing was the pre-2018 convention and is not stable. To find a vector:

1. Browse to the StatCan table at `www150.statcan.gc.ca/t1/tbl1/en/...`
2. Click on the cell you want
3. The popup shows the vector (format: `V` + 5-10 digits) and the reference
   period

For full table downloads (when the API is the wrong tool for a large
cross-section, e.g. all CPI components), the bulk CSV is available at
`https://www150.statcan.gc.ca/n1/tbl/csv/<table_id_no_dashes>-eng.zip`.

### Release schedule

Headline series follow the published release calendar at
`https://www150.statcan.gc.ca/n1/dai-quo/index-eng.htm`. Common ones:

- **CPI** — monthly, typically the third Tuesday of the month following the
  reference month, 8:30 AM Eastern. Basket weights refresh every five years
  (latest: 2023 weights applied to 2024+ data).
- **Labour Force Survey (LFS)** — monthly, first Friday of the month after
  the reference month, 8:30 AM Eastern.
- **GDP** — monthly (Table 36-10-0434), released roughly 60 days after the
  reference month. Quarterly GDP (Table 36-10-0104) is released ~60 days
  after the reference quarter.
- **Trade** — monthly, ~30-day lag.

### Vintage / revision conventions

- Each release has both a **release_date** (when StatCan published it) and a
  **reference period** (the calendar period the observation describes). Both
  matter; the pipeline records `release_date` in `.meta.json` from the
  `releaseTime` field WDS returns on each observation.
- Revisions: most monthly series revise the prior 1-3 observations on each
  release. LFS revises the prior month only. GDP revises further (often the
  prior two quarters), so the same vector pulled today vs a month ago can
  show different historical values.
- We do **not** preserve vintage history in the pipeline yet. If a story
  requires "what did this look like as of date X," that's a planned
  enhancement — capture the release vintage at fetch time and pin it on
  disk in a vintage-tagged subdirectory.

### Gotchas

- **NaN values are meaningful.** WDS flags structural gaps with
  `statusCode=1` and a null value (e.g. JVWS April-September 2020 was
  suspended during COVID). We preserve NaN rows rather than dropping them
  so chart lines auto-break and rolling means skip via `min_periods`.
- **Suppression rules.** LFS suppresses small-cell counts; some sub-series
  return `statusCode=8` ("suppressed for confidentiality"). Treat as NaN.
- **CPI basket refresh.** The CPI basket updates every five years (2003,
  2009, 2013, 2018, 2023). Cross-basket levels are not strictly comparable;
  YoY changes are because StatCan chains the index across baskets. As of
  the 2022 refresh cycle, StatCan moved to roughly-annual basket-weight
  refreshes; the current 2024 basket applies through ~2029 per StatCan's
  basket-update schedule. Major-aggregate basket weights are wired via
  Table 18-10-0007-01 -- see `pipeline/fetch/cpi_basket.py` and the
  `cpi_basket_weight_*` entries in the StatCan catalog. The consolidated
  long-format and wide-format weights land in
  `data/derived/cpi_basket_weights_canada{,_wide}.csv`.
- **SA vs NSA.** Many series exist in both forms with different vectors.
  Headline CPI SA is `v41690914`; NSA is `v41690973`. Pick deliberately and
  document the choice on each fetcher.
- **HTTP 409 on some vectors.** Empirically observed on some sub-vectors of
  Table 14-10-0287-01. Cause is unclear; treat as a flagged failure and
  fall back to a different vector if available.

### What we record in .meta.json

`source_url` points at the StatCan table (not the WDS endpoint); a fact-
checker resolves the data through StatCan's public-facing table page.
`source_id` is `v<vector_id>`.

---

## Bank of Canada — Valet API

**API base:** `https://www.bankofcanada.ca/valet/`
**Pipeline module:** `pipeline/fetch/boc.py`
**Endpoint used:** `observations/{series_key}/json` (GET)
**Authentication:** none. No documented rate limit; we retry on 429 / 5xx.

### Addressing

Series keys are mixed-format strings:
- **`V`-prefix integers** for legacy CANSIM vectors (e.g. `V39079` = daily
  overnight rate target, post-2009)
- **`STATIC_*` prefixed keys** for long-history static tables (e.g.
  `STATIC_ATABLE_V39079` = monthly overnight rate target, full history)
- **`BD.CDN.*.DQ.YLD`** for benchmark bond yields (e.g. `BD.CDN.2YR.DQ.YLD`)
- **`FVI_*`** for Financial Vulnerability Indicators
- **`INDINF_*`** for Indicators of Inflation Dynamics
- **`CES_*`** for the Canadian Survey of Consumer Expectations
- **`AVG.INTWO`** for CORRA (daily Canadian Overnight Repo Rate Average)

Browse the full list at `https://www.bankofcanada.ca/valet/lists/series/json`.

### Release schedule

- **Policy rate decisions** (Fixed Announcement Dates / FADs) — eight per
  year on dates published in advance. The iCal feed at
  `https://www.bankofcanada.ca/?feed=ical&content_type=upcoming-events`
  carries the schedule; we ingest it as JSON.
- **Daily series** (yields, FX, CORRA) — published end of business day.
- **CPI core measures** (trim, median, common) — released alongside the
  StatCan CPI release, same day.
- **Balance sheet** (Statement of Financial Position) — weekly, Wednesday.
- **CSCE / BOS** — quarterly survey results.

### Vintage / revision conventions

Valet does not return release timestamps the way WDS does — each observation
is just `{d, v}`. We record `fetched_at` as a proxy for "when we knew this"
and let the upstream date stand as both the reference period and (effectively)
the release period. For balance-sheet and CORRA data this is fine; for
quarterly survey data it understates how stale the latest observation can be.

### Gotchas

- **Null values.** Some observations carry `{"v": null}` (e.g. holidays in
  daily series). We drop those rows; the resulting CSV is shorter than the
  raw observation list. The drop count is not currently surfaced — flagged
  for a follow-up enhancement if it matters editorially.
- **QE-era series.** Some balance-sheet sub-lines (reverse repos, etc.)
  only have data from 2020+. Asking for `start_date=1990-01-01` on those
  returns an empty observations list. We currently raise; a fetcher could
  instead return an empty DataFrame with a noted-empty meta.
- **Identical-key gotcha.** `V39079` (daily, post-2009) vs
  `STATIC_ATABLE_V39079` (monthly, full history) both publish "the
  overnight rate target" but at different cadences and date ranges. Pick
  intentionally per chart.

### What we record in .meta.json

`source_url` is the canonical observations endpoint for the series. The
`label` and `description` blocks BoC publishes alongside the data are lifted
into the `notes` field, so a fact-checker sees the BoC-published name of
the series next to the file.

---

## FRED — Federal Reserve Bank of St. Louis

**API base:** `https://api.stlouisfed.org/fred/`
**Pipeline module:** `pipeline/fetch/fred.py`
**Endpoint used:** `series/observations` (GET)
**Authentication:** free API key; set as `FRED_API_KEY` environment variable.
If unset, the build skips all FRED series with a logged warning rather than
failing (see `pipeline.fetch.fred.get_api_key`).

### Addressing

Series IDs are short uppercase strings (e.g. `DGS10`, `VIXCLS`). Discover
via `https://fred.stlouisfed.org/searchresults/?st=<query>`.

### Release schedule

- **Daily series** (US Treasuries DGS2/DGS10, VIX, oil DCOILWTICO/DCOILBRENTEU,
  IG/HY OAS BAMLC0A0CM/BAMLH0A0HYM2) — updated late afternoon ET.
- **Monthly series** (FEDFUNDS) — updated within a few days of the FRBNY
  publication.

### Gotchas

- **Missing values use "."** — pipeline coerces these to drops, not NaN,
  because FRED emits dense "." markers on weekends/holidays for daily series.
- **S&P 500 truncation.** FRED's `SP500` is restricted to the last 10 years
  per S&P Dow Jones licensing. For deeper history use Yahoo (`^GSPC`).
- **LBMA gold discontinued.** `GOLDAMGBD228NLBM` / `GOLDPMGBD228NLBM` were
  discontinued by ICE Benchmark Administration on FRED. Use Yahoo `GC=F`
  (COMEX gold futures front month) as the daily-cadence gold input.
- **Fed funds target composite.** Pre-2008 the Fed targeted a single rate;
  post-Dec-2008 it targets a range. `pipeline.fetch.fred.fetch_fed_funds_target`
  splices FEDFUNDS (pre-2008) with the DFEDTARU/DFEDTARL midpoint (post-2008).

### What we record in .meta.json

`source_url` resolves to `https://fred.stlouisfed.org/series/<series_id>`,
the human-facing series page. `source_id` is the FRED series ID verbatim.

---

## Yahoo Finance — daily closes

**API base:** `https://query1.finance.yahoo.com/v8/finance/chart/<symbol>`
**Pipeline module:** `pipeline/fetch/yahoo.py`
**Authentication:** none, but a browser-like User-Agent is required (the
default pipeline UA gets occasional 401s).

### Why Yahoo

- **TSX Composite (`^GSPTSE`)** — TMX's official S&P/TSX is paid; Yahoo
  is the working free EOD feed.
- **S&P 500 (`^GSPC`)** — Yahoo carries deeper history than FRED's
  truncated `SP500` series.
- **Gold (`GC=F`)** — COMEX gold futures front month, daily close;
  acceptable proxy for the LBMA AM fix at the basics-layer cadence.

### Gotchas

- **Unofficial API.** Schema can change without notice. We pin to the v8
  `chart` endpoint (stable since at least 2020) and validate with pydantic
  at the boundary.
- **Adjusted close.** Where Yahoo exposes adjusted close (`adjclose`), we
  prefer it over raw close (corporate-action safety on equities; benign
  for indices and futures).
- **POSIX timestamps.** Convert with `pd.to_datetime(..., unit="s")`.

### What we record in .meta.json

`source_url` resolves to `https://finance.yahoo.com/quote/<symbol>` with
the caret URL-encoded.

---

## CREA — Canadian Real Estate Association (MLS HPI bulk XLSX)

**Bulk URL:** `https://www.crea.ca/files/mls-hpi-data/MLS_HPI_{Month}_{Year}.zip`
**Pipeline module:** `pipeline/fetch/crea.py`
**Authentication:** none. Standard browser headers acceptable.

### Addressing

The ZIP contains four XLSX files (SA Monthly, NSA Monthly, NSA Quarterly,
NSA Annual). We use **`Seasonally Adjusted (M).xlsx`** per canon 4.4
element 1. Inside that XLSX, each sheet is one geography (e.g.
`GREATER_TORONTO`, `MONTREAL_CMA`, `AGGREGATE`). The canonical CMA mapping
(canon 4.4 names -> CREA sheet names) is in `pipeline/fetch/crea.py:CMA_SHEETS`.

### Release schedule

Monthly, mid-month, ~3 weeks after the reference month closes. CREA back-
revises the prior ~3 months as late-closing sales report in. The fetcher
`crea.find_available_release()` walks back up to 4 months to locate the
most recent 200-OK ZIP if the current-month candidate isn't up yet.

### Gotchas

- **AGGREGATE is methodology context, not a headline.** Canon explicitly
  forbids a national-average headline price; use AGGREGATE only as
  methodology context.
- **CMA boundaries.** Greater Vancouver / Greater Toronto / Montreal CMA
  are board-territory CMA-equivalent, NOT strict StatCan CMA boundaries.
  Document this in any chart caption.

### What we record in .meta.json

`source_url` is the canonical CREA bulk ZIP URL for the named release
(`MLS_HPI_April_2026.zip` etc.). `source_id` is `CREA-HPI-<sheet_name>`.

---

## Department of Finance Canada — Fiscal Monitor

**Issue URL:** `https://www.canada.ca/en/department-finance/services/publications/fiscal-monitor/{YYYY}/{MM}.html`
**Pipeline module:** `pipeline/fetch/dof_fiscal.py`
**Authentication:** none. Standard browser headers acceptable.

### Release schedule

Monthly, with a ~2-month lag (the Feb-2026 reference issue is typically
published in late April 2026). `dof_fiscal.find_available_issue()` walks
back up to 6 months from the candidate URL.

### Addressing

The HTML page carries ~10 tables in stable order:
- Tables 0-1: monthly + YTD budgetary balance, prior-FY vs current-FY columns
- Table 2: budgetary transactions summary (revenues, expenses, balance)
- Tables 3-5: revenue / expense detail
- Tables 7-9: financial source/requirement, financing, debt summary

Federal fiscal year = April to March. The Feb-2026 issue covers April 2025
through February 2026 = FY 2025-26.

### Gotchas

- **No stable table IDs.** Tables are identified by position + contextual
  text (row labels, FY column header). The parser is defensive against
  MultiIndex column shapes when colspans are emitted.
- **All figures in C$ millions.** Preserve millions in CSV; chart code
  rescales to billions for display.
- **Prior-year column always present.** Both years are kept in the parsed
  output.

### What we record in .meta.json

`source_url` is the issue HTML page; `source_id` is `FM-<YYYY>-<MM>` for
the reference period.

---

## Alberta Economic Dashboard

**API base:** `https://api.economicdata.alberta.ca/api/data`
**Pipeline module:** `pipeline/fetch/alberta.py`
**Authentication:** none. No documented rate limit.

### Addressing

Each chart on the public Alberta Economic Dashboard
(`https://economicdashboard.alberta.ca/dashboard/<slug>`) is backed by a
UUID-coded endpoint:

    GET https://api.economicdata.alberta.ca/api/data?code=<uuid>

Response is a JSON array of `{Date, Value, Unit, "Type "}` objects (note
the trailing space on `Type ` -- the pydantic boundary accepts the alias).

Wired UUIDs (probe 2026-05-11):
  - `666e6195-c509-479b-b79f-b95e05536032` -- Natural Gas (monthly, C$/GJ,
    Alberta reference price; AECO-equivalent monthly settle)

### Release schedule

Monthly. Values land with a ~2-3 month lag (Feb 2026 reference month was
the latest as of probe 2026-05-11). Backfill goes to 1988 for natural gas.

### Gotchas

- **Trailing-space key.** The API emits `"Type "` (with trailing space) as
  the observation-type field. The pydantic model declares the field as
  `Type` with `alias="Type "`. If the API ever cleans this up, parsing
  continues to work via `populate_by_name=True`.
- **Weekly bid-week not available here.** Canon 4.6 element 4 asks for
  AECO at weekly bid-week cadence "if achievable"; NGX itself blocks
  anonymous HTTP and requires a paid subscription for daily/weekly
  settlement files. The Alberta Dashboard's monthly Alberta reference
  price is the best free fallback; weekly bid-week defers to v1.5.
- **"AECO" label not explicit.** The series is labeled "Natural Gas" in
  the API response, not "AECO" or "Alberta Reference Price". The mapping
  is established editorially via the Government of Alberta's published
  royalty-calculation methodology; document this in any chart caption.

### What we record in .meta.json

`source_url` is the canonical API URL with the code parameter intact, so
a fact-checker can re-fetch the same series without ambiguity.
`source_id` is `alberta-dashboard:<uuid>`. The dashboard's human-facing
page is recorded in `pipeline/fetch/alberta.py:DASHBOARD_PAGES` for
chart-caption citations.

---

## C.D. Howe Institute -- Business Cycle Council (BCC)

**Source URL:** `https://www.cdhowe.org/council/business-cycle-council`
**Output:** `data/derived/cdhowe_bcc_recessions.json` (hand-curated)
**Authentication:** none. No API; the council publishes communiques as
PDF / HTML on its public site.

### Addressing

The BCC publishes a historical dating list for Canadian recessions plus
periodic communiques re-confirming or revising recent dates. There is no
machine-readable feed; the data is editorially-curated from BCC
communique text.

### Release schedule

The council releases communiques roughly twice yearly, typically after
each pair of quarterly GDP releases. Major rev'-events (e.g. confirming
the start or end of a recession) trigger a communique within a few weeks
of the underlying GDP data landing.

### Vintage / revision conventions

The BCC occasionally re-dates older recessions when new historical data
prompts a revision. Earlier entries in the JSON are treated as stable;
the trailing entry (the open expansion or recession) is the one most
likely to change. Maintainer convention: only edit the last entry when
the BCC issues a new communique; lock the rest.

### Schema (this repository)

```
[{name, start, end, type: "recession" | "expansion"}]
```

- `name`: short editorial label (e.g. `"COVID-19 2020Q1-Q2"`)
- `start`, `end`: ISO YYYY-MM-DD. `end` may be null for the open span.
- `type`: `"recession"` or `"expansion"`. Entries alternate strictly.

### Consumers

- Chart-builder reads this file for recession-band overlays on all
  time-series panels in the GDP and Inflation basics layers.
- The richer cycle-state panel (canon GDP element 6) uses a separate
  chart-internal JSON shape with BCC severity classifications; that
  file is editorial-curated and is not produced by this pipeline.

---

## CBA -- Canadian Bankers Association (mortgage arrears)

**Pipeline module:** `pipeline/fetch/cba_arrears.py`
**Source URL pattern:** `https://cba.ca/Assets/CanadianBankersAssociation/Documents/Articles/Statistics/stat-mortgages-arrears-{month}-{year}-en.pdf`
**Frequency:** monthly, ~2.5-month publication lag.

The CBA publishes monthly "Number of Residential Mortgages in Arrears"
PDFs covering chartered banks (BMO, CIBC, National, RBC, Scotia, TD)
plus Manulife (since 2004), Laurentian (since 2010), and Equitable
(since 2020). Each PDF has a cross-section table for the reference
month (page 1) and full national time-series history back to 1995
(pages 2+).

This is the closest publicly available proxy for the (long-discontinued
on the homepage tile) CMHC arrears series. Coverage is ~75% of the
mortgage stock; brokered / private-lender / credit-union mortgages are
excluded.

**WAF note:** the `cba.ca/mortgages-in-arrears` HTML landing page is
behind a Sucuri WAF that serves a JavaScript-challenge interstitial to
non-browser clients. The `/Assets/...` PDF URLs, however, are served
directly and respond to plain `httpx` GETs with HTTP 200 +
`Content-Type: application/pdf`. The pipeline therefore probes the
direct PDF URL pattern (filename uses LOWERCASE month name) and skips
the HTML page entirely.

**URL probing convention:** `pipeline.fetch.cba_arrears.find_and_download_latest()`
walks back from `today - 2 months` (CBA's typical lag) through a
configurable lookback window, returning the first month whose PDF URL
returns 200. A 404 advances to the next candidate; failure of every
candidate raises `FileNotFoundError`.

**Parsing:** the PDF text extracted by `pypdf` is line-oriented for the
page-1 cross-section (regex match: `LOCATION  TOTAL  ARREARS  PCT%`)
and a side-by-side two-column layout for the national time series
(regex finds every `YYYY-MM <total> <arrears> <pct>%` group). An
upstream layout change would surface as a `ValueError` raised from
`parse_cba_arrears_pdf`, not as a silent partial parse.

**Output files:**
- `data/raw/cba_mortgage_arrears_national.csv` -- monthly national % back to ~1995
- `data/raw/cba_mortgage_arrears_provincial.csv` -- per-province % for the latest month only

CBA does not publish per-province time-series history in the PDF; only
the latest-month cross-section is available without bank-by-bank
disclosures.

---

## Indeed Hiring Lab -- Canada job postings

**Bulk URL:** `https://raw.githubusercontent.com/hiring-lab/job_postings_tracker/master/CA/aggregate_job_postings_CA.csv`
**Pipeline module:** `pipeline/fetch/indeed_hiring_lab.py`
**Catalog:** `pipeline/catalog/indeed_series.py`
**Authentication:** none; GitHub raw, unauthenticated.

### Why Indeed

Indeed Hiring Lab publishes a daily seasonally-adjusted index of Canadian
job postings (Feb 1 2020 = 100). The series is the complement to StatCan
JVWS (Job Vacancy and Wage Survey, monthly) in labour panel-4:

- JVWS is the official measure but monthly, with a roughly 60-day lag.
- JVWS was suspended April-September 2020 during COVID.
- Indeed is daily, weekly-refreshed, and bridges the JVWS suspension
  gap. It is a postings-volume proxy (not vacancies-by-definition), so
  it complements JVWS rather than replacing it.

### Addressing

- **Aggregate Canada:** `aggregate_job_postings_CA.csv` (~188 KB).
- **Provincial breakdown:** `provincial_postings_ca.csv` (~471 KB).
- Repo: `hiring-lab/job_postings_tracker`, default branch **`master`**
  (not `main`). A prior internal reference to `hiring-lab/data` is a
  legacy alias that 404s; pin to `job_postings_tracker`.

### Release schedule

Refreshed weekly, typically Thursdays. We run the aggregate fetch on
the daily-cadence post-close orchestrator (`build_financial.py`); on
the days Indeed has not pushed, the upstream bytes are unchanged and
the orchestrator's commit step in CI is a no-op. No publication
calendar is published; the cadence has been weekly-Thursday for years
but is not contractual.

### Methodology / vintage

- Seasonal adjustment: Deutsche Bundesbank method per the repo's data
  dictionary.
- Two variables per row: `total postings` (canonical index) and
  `new postings` (new posts within the trailing 7 days, leading-
  indicator companion). We extract the SA `total postings` slice as
  the default canonical series; NSA and `new postings` are reachable
  through fetcher kwargs but not registered in the v1 catalog.
- The provincial CSV publishes a single index column (no SA / NSA
  split) and is in long form: `date, province, indeed_job_postings_index`.

### Gotchas

- **Schema validation.** The fetcher asserts the expected upstream
  columns are present and raises ValueError on drift, so a silent
  rename surfaces with a precise diagnostic. Required columns for the
  aggregate: `date, jobcountry, indeed_job_postings_index_SA,
  indeed_job_postings_index_NSA, variable`.
- **CC BY 4.0 attribution.** Cite as `Source: Indeed Hiring Lab`.
- **Monthly companion.** Labour panel-4 reads the monthly cadence
  directly so the chart can overlay JVWS without resampling at the
  chart layer. The orchestrator writes `indeed_postings_ca_monthly.csv`
  as the month-start mean of the daily series alongside the daily file.
- **Rate limit.** GitHub raw enforces a generous unauthenticated quota
  on `raw.githubusercontent.com` (independent of the 60 req/hour
  `api.github.com` cap). At two fetches per daily build we are nowhere
  near the limit; the shared `_http` retry policy handles a transient
  429 if it ever happens.

### What we record in .meta.json

`source_url` resolves to the GitHub blob page
`https://github.com/hiring-lab/job_postings_tracker/blob/master/CA/<file>`.
`source_id` records the repo path. `units` is `"Index, Feb 1 2020 = 100"`.
`reference_period_start` / `reference_period_end` are auto-derived from
the CSV's date column.

---

## (To add as scoped)

### Alberta Economic Dashboard -- Western Canada Select (WCS)

The same Alberta Dashboard API also hosts WCS oil price (separate UUID).
Deferred to v1.5 per canon 4.6 element 4 (WCS monthly cadence acceptable
with the "do not surface daily-comparison differential" caveat). When
added: call `pipeline.fetch.alberta.fetch_dashboard_series(<wcs_uuid>)`
with the WCS UUID; no new code needed beyond a UUID constant.

### BIS — Bank for International Settlements

For peer central bank policy rates (BoE, RBA, etc.). Bulk CSV download
(`WS_CBPOL_csv_flat.zip`); cache once per session to avoid re-fetching.

### CMHC, OSFI, PBO

Bulk Excel / CSV / PDF; lighter-weight Python clients. CMHC arrears and
Rental Market Survey deferred to a future wave; OSFI Bank Financial Data
M4 and PBO Economic and Fiscal Outlook deferred to Wave 3 (bank stability
+ fiscal deep-dive content per canon 4.5b).
