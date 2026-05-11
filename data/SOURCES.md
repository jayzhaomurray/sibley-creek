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
  YoY changes are because StatCan chains the index across baskets.
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

## (To add as scoped)

### FRED — Federal Reserve Bank of St. Louis

For US comparators (Fed funds target, US Treasury yields, USD/CAD, WTI).
Requires a free `FRED_API_KEY` env var. Boc-tracker has working client code
to lift when editorial-director scopes US comparators.

### Alberta Economic Dashboard

For Western Canada Select oil price. Endpoint:
`https://api.economicdata.alberta.ca/data?table=OilPrices`. No auth.
Returns all oil types in one payload; filter by `Type == "WCS"`.

### BIS — Bank for International Settlements

For peer central bank policy rates (BoE, RBA, etc.). Bulk CSV download
(`WS_CBPOL_csv_flat.zip`); cache once per session to avoid re-fetching.

### CMHC, OSFI, Department of Finance, PBO

Bulk Excel / CSV / PDF; lighter-weight Python clients. Pull as
editorial-director scopes housing finance, regulated entity, and fiscal
sections.
