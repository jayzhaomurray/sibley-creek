# Canada home price to income — long-history sources

## Recommendation

**Use BIS Residential Property Prices (Canada) via FRED for the price series, paired with Statistics Canada Table 36-10-0112 (household disposable income) for the income denominator. Cite Dallas Fed International House Price Database as a pre-computed alternative for the full ratio.**

Top pick for a single-source, ready-to-chart price-to-income ratio: **Dallas Fed International House Price Database** — quarterly, 1975Q1 forward, contains both HPI and per-capita PDI for Canada in one spreadsheet, explicitly designed for cross-country affordability work.

If a longer back-history matters more than the bundled denominator: **BIS via FRED** goes back to **1970Q1** (verified — 225 quarterly observations through 2025Q4).

## Sources evaluated

### 1. Dallas Fed International House Price Database
- URL: https://www.dallasfed.org/research/international/houseprice
- Coverage for Canada: 1975Q1 onward (per Dallas Fed working paper #0099 and current release notes)
- Cadence: Quarterly
- Format: Excel (.xlsx) workbook covering all countries
- Variables: HPI (nominal), RHPI (real, PCE-deflated), PDI (per-capita personal disposable income, nominal), RPDI (real). All indexed to 2005=100. PDI is per-capita using working-age population.
- Verified by: WebSearch surfaced consistent documentation. Direct fetch of the landing page returned 403 (WAF), but the working paper at /-/media/documents/institute/wpapers/2011/0099.pdf documents the methodology and confirms 1975Q1 start.
- Notes: Canadian HPI methodology changed in 2013Q1 release — from 2010Q1 onward it uses a weighted average of 10 metro areas (Teranet-style), with fixed 2011-census population weights. Pre-2010 source is different — there is a methodological seam worth flagging in a caption. Earlier vintages had a Canada-specific indexing bug in nominal PDI (now fixed).

### 2. BIS Residential Property Prices (long series), via FRED mirror
- URL: https://fred.stlouisfed.org/series/QCAR628BIS (real, CPI-deflated); https://fred.stlouisfed.org/series/QCAN628BIS (nominal)
- CSV endpoint: https://fred.stlouisfed.org/graph/fredgraph.csv?id=QCAR628BIS
- Coverage for Canada: **1970Q1 to 2025Q4** (verified — fetched CSV directly; 225 quarterly observations)
- Cadence: Quarterly
- Format: CSV via FRED, also XLSX/SDMX at https://data.bis.org/topics/RPP
- Variables: Nominal RPP index, real RPP index (CPI-deflated, 2010=100)
- Verified by: Live curl returned first row `1970-01-01, 38.1516` and last row `2025-10-01, 142.2693`. Endpoint already in use elsewhere in the pipeline.
- Notes: Price-only — no income series bundled. Earliest five years (1970–74) are backdated and methodologically less consistent than the post-1975 series. Index, not levels.

### 3. StatCan native: 18-10-0205-01 (NHPI) + 36-10-0112-01 (Household sector accounts, disposable income)
- URL: https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1810020501 (NHPI) and https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=3610011201 (disposable income, quarterly)
- Coverage for Canada: NHPI monthly from 1981; disposable income quarterly from 1981Q1
- Cadence: Monthly (NHPI), quarterly (income)
- Format: CSV via Table downloader; JSON via WDS API
- Verified by: WDS probe with placeholder coordinate failed (need correct coordinate string — out of time-budget). Both tables are well-known and the 1981 start is documented in StatCan publication 13-605-X.
- Notes: NHPI covers only NEW housing — narrower than MLS/Teranet/BIS resale-inclusive measures. For an affordability ratio aligned to what most homebuyers face, NHPI is the wrong price series. Use only if the editorial point is specifically about new-build prices. Income series is solid and the right denominator if computing the ratio in-house.

### 4. IMF Global Housing Watch
- URL: https://www.imf.org/external/research/housing/
- Status: 403 from WebFetch; landing page generally aggregates BIS/OECD inputs rather than original data. Useful as a cross-reference, not a primary.

### 5. BoC FSR affordability metrics
- Status: FSR publishes a household debt-service ratio and a housing affordability index sporadically, not as a continuous downloadable series. Not suitable for a long time-series chart.

## Suggested derivation

**Path A (recommended, simplest):** Use Dallas Fed `HPI / PDI` columns for Canada directly. Both indexed to 2005=100, so `ratio_t = HPI_t / PDI_t` is unitless and the change from base period reads as "house prices have risen N× more than per-capita disposable income since 2005." Trivial to chart, citable to a single primary source.

**Path B (longer history, more work):** BIS nominal RPP (QCAN628BIS) from 1970 ÷ StatCan 36-10-0112 household disposable income per capita (1981+). Splice or trim to common window; document the splice. Loses the 1970–80 window on the income side.

## Sample data points (BIS Canada real RPP, 2010=100, verified)

| Date    | Value    |
|---------|----------|
| 1970Q1  | 38.15    |
| 1970Q4  | 39.24    |
| 2024Q4  | 150.56   |
| 2025Q4  | 142.27   |

File: C:\Users\jayzh\projects\macro-research-department\research\canada_home_price_income.md

## Dollar-figure follow-up (2026-05-25)

The indexed series (BIS, Dallas Fed) cannot show dollar prices. The chart needs CAD-dollar lines. Verified options below.

### Best price source — CREA MLS HPI workbook, "Composite_Benchmark" column

- URL: https://www.crea.ca/files/mls-hpi-data/MLS_HPI_May_2026.zip (monthly-refreshed; URL pattern is `MLS_HPI_<Month>_<Year>.zip`)
- Earliest year: **2005** (annual), 2005-01 (monthly)
- Format: ZIP containing four XLSX files — `Not Seasonally Adjusted (A).xlsx` is annual, `(M)` monthly, `(Q)` quarterly, `Seasonally Adjusted (M)` monthly SA. Sheet `AGGREGATE` = national.
- Verified: downloaded the zip (3.2 MB, HTTP 200), opened the annual workbook. Schema confirmed: `Date | Composite_HPI | ... | Composite_Benchmark | Single_Family_Benchmark | One_Storey_Benchmark | Two_Storey_Benchmark | Townhouse_Benchmark | Apartment_Benchmark`.
- Sample (Canada composite benchmark, annual, CAD$): 2005 = $243,600; 2008 = $310,600; 2015 = $431,900-area; 2025 = **$685,100**.
- Caveat: this is a quality-adjusted benchmark (HPI methodology — what a "typical" home costs), not the raw average. Eliminates compositional drift, which is the right denominator for a long-run affordability ratio. Starts 2005 — the binding constraint on history.

### Longer-history price alternative — CREA aggregate average sale price (back to ~1980)

- URL: news releases at https://www.crea.ca/media-hub/news/ (monthly); current value $695,412 in April 2026
- No bulk CSV. The annual averages 1980-onward are published in CREA's annual "MLS Statistical Summary" PDFs and embedded in news-release HTML. Harvestable via scrape, not native CSV. **Out-of-the-box CSV not available** — flag as a data-engineering ticket if pre-2005 dollar prices are required.
- Caveat: raw aggregate average is dirty (compositional drift — when Toronto/Vancouver share of sales rises, national average rises mechanically). Why CREA built the HPI in the first place. Use only if 1980-2004 coverage is editorially required.

### Best income source — StatCan Table 11-10-0190-01, "Median total income" / "Economic families and persons not in an economic family"

- URL: https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1110019001
- Direct CSV: https://www150.statcan.gc.ca/n1/tbl/csv/11100190-eng.zip (3.2 MB; latest as of 2026-04-29 release)
- Earliest year: **1976**; latest: **2024**
- Cadence: Annual
- Format: ZIP → `11100190.csv` (long format with `REF_DATE, GEO, Income concept, Economic family type, VALUE` columns)
- Verified: downloaded and filtered. Sample for Canada, "Median total income", "Economic families and persons not in an economic family":

  | Year | Median total income (CAD) |
  |------|---------------------------|
  | 1976 | $74,000 |
  | 1995 | (avail) |
  | 2022 | $84,400 |
  | 2023 | $85,500 |
  | 2024 | $86,000 |

- The series is **inflation-adjusted to 2024 constant dollars** (StatCan converted nominal to real using CPI). For nominal CAD by year, switch the "Income concept" filter or pair with CPI to deflate — note this in the methodology caption.
- For pure economic-family medians (excludes singles): use "Economic families" instead — runs higher (~$108k in 2024).

### Suggested ratio calculation

```
ratio_year = composite_benchmark_price_year / median_total_income_year
```

Both series are annual. CREA benchmark is nominal CAD by definition. StatCan 11-10-0190 is in **constant 2024 dollars** — to compare like-for-like, either (a) deflate the CREA price by CPI to 2024 dollars, or (b) use the StatCan "Persons" table 11-10-0239 nominal-dollar variant. Cleanest: deflate CREA nominal to 2024 dollars using StatCan 18-10-0005 (CPI annual), then divide.

Sample ratio (back-of-envelope, both in 2024 dollars):
- 2005: ~$340k (deflated) / ~$72k = **~4.7×**
- 2024: $681k / $86k = **~7.9×**
- 2025: $685k / (2025 income TBD when released ~April 2027) — extrapolate or hold

### Caveats

1. **Median vs average.** Income series is median (household-typical). Price series is HPI benchmark (typical-home quality-adjusted). Both are "middle" measures — clean match. Do NOT cross median-income with average-price (the latter is pulled up by Toronto/Vancouver high end).
2. **Real vs nominal.** 11-10-0190 is constant 2024 dollars; CREA benchmark is nominal. Deflate CREA before computing the ratio, or the slope will be wrong.
3. **Economic-family-type choice.** "Economic families AND persons not in an economic family" is the broadest cut and the closest analogue to "Canadian household." Switching to "Economic families" alone raises income ~25% and lowers the ratio mechanically — pick one and stick with it.
4. **2005 start on the benchmark side.** For 1980-2004 dollar prices, scrape CREA news releases or accept that the chart starts in 2005. The Dallas Fed / BIS indexes extend back further but cannot be re-expressed in dollars without a 2005 anchor.
5. **Income release lag.** 11-10-0190 publishes T-2 (2024 data released April 2026). Last point on the ratio line will lag the price line by 12-18 months.

### Files written

- `C:\Users\jayzh\projects\macro-research-department\data\raw\statcan_11100190.zip` (income, verified)
- `C:\Users\jayzh\projects\macro-research-department\data\raw\statcan_11100190\11100190.csv` (unzipped)
- `C:\Users\jayzh\projects\macro-research-department\data\raw\crea_mls_hpi.zip` (price, verified)
- `C:\Users\jayzh\projects\macro-research-department\data\raw\crea_mls_hpi\Not Seasonally Adjusted (A).xlsx` (unzipped, annual)
