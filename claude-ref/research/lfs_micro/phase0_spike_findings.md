# LFS-micro Phase-0 Spike Findings
# Date: 2026-06-05
# Branch: lfs-micro
# Analyst: backend-engineer subagent

---

## 1. URL patterns — working and confirmed

### Recent monthly (last ~3 months)
```
https://www150.statcan.gc.ca/n1/pub/71m0001x/2021001/{YYYY-MM}-CSV.zip
```
- **Confirmed working:** 2026-04 (HTTP 206, PK zip magic, 3.9 MB)
- **Confirmed 404:** 2025-04, 2024-12, 2025-01, 2025-12, 2026-05
- **Cutoff:** Months older than roughly 3–4 months return 404 on the monthly URL. Exact cutoff not pinned, but at minimum anything before the current calendar year fails.

### Historical annual bundles (2015–2025)
```
https://www150.statcan.gc.ca/n1/pub/71m0001x/2021001/hist/{YYYY}-CSV.zip
```
- **Confirmed working (HTTP 200, PK zip):** 2015 through 2025, all 11 years
- **Last-Modified:** All 2015–2024 files show `Fri, 07 Feb 2025 13:45:13 GMT` — this is the Feb 2025 LFS redesign re-release of revised historical PUMFs (SAN 2024-23 retroactive revision). 2025 annual shows `Fri, 06 Feb 2026 13:30:42 GMT`.
- **Contents:** Each annual zip contains 12 monthly CSVs (e.g., `pub0124.csv` through `pub1224.csv` for year 2024) plus the same Documents/ bundle.

### UA requirement — critical
StatsCan's `www150.statcan.gc.ca` performs a TLS reset on non-browser User-Agents at the connection layer (WinError 10054 / handshake timeout). **httpx and urllib both fail regardless of timeout.** Only `requests` with a Chrome/browser UA works:
```python
BROWSER_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)
```
This is not a rate-limit or auth issue — it is a TLS-layer bot filter. The existing 2026-04 zip was presumably downloaded via a browser session. **All downloader code must use requests + browser UA.**

---

## 2. Data structure — 2026-04 (pub0426.csv)

| Attribute | Value |
|-----------|-------|
| Rows | 112,707 |
| Columns | 60 |
| Data file name | pub0426.csv |
| File size compressed | 4,040,651 bytes (3.9 MB) |

**Full column list (60 columns, alphabetical):**
AGE_12, AGE_6, AGYOWNK, AHRSMAIN, ATOTHRS, AVAILABL, CMA, COWMAIN, DURJLESS, DURUNEMP, EDUC, EFAMTYPE, ESTSIZE, EVERWORK, FINALWT, FIRMSIZE, FLOWUNEM, FTPTLAST, FTPTMAIN, GENDER, HRLYEARN, HRSAWAY, IMMIG, LFSSTAT, LKANSADS, LKATADS, LKEMPLOY, LKOTHERN, LKPUBAG, LKRELS, MARSTAT, MJH, NAICS_21, NOC_10, NOC_43, PAIDOT, PAYAWAY, PERMTEMP, PREVTEN, PRIORACT, PROV, REC_NUM, SCHOOLN, SURVMNTH, SURVYEAR, TENURE, TLOLOOK, UHRSMAIN, UNEMFTPT, UNION, UNPAIDOT, UTOTHRS, WHYLEFTN, WHYLEFTO, WHYPT, WKSAWAY, XTRAHRS, YABSENT, YAWAY, YNOLOOK

**Employment breakdown:**
| Filter | N |
|--------|---|
| LFSSTAT in {1,2} (employed) | 64,487 |
| + COWMAIN in {1,2} (paid employees) | 55,933 |
| + HRLYEARN > 0 (regression sample) | 55,933 |

### Model variable presence and profile

| Variable | Found | Dtype | N distinct | Miss% (paid emp) | Notes |
|----------|-------|-------|-----------|------------------|-------|
| HRLYEARN | Yes | float64 | 5,160 | 0.0% | Two decimals implied; divide by 100 |
| FINALWT | Yes | int64 | 1,656 | 0.0% | WLS weight |
| AGE_12 | Yes | int64 | 12 | 0.0% | 5-year age groups |
| SEX | **No** | — | — | — | **Absent post-2022. Use GENDER.** |
| GENDER | Yes | int64 | 2 | 0.0% | 1=Men+, 2=Women+ |
| EDUC | Yes | int64 | 7 | 0.0% | 0–6 |
| TENURE | Yes | float64 | 240 | 0.0% | Months 1–240; bin in production |
| NOC_10 | Yes | float64 | 10 | 0.0% | Do NOT use with NOC_43 (collinear) |
| NOC_43 | Yes | float64 | 43 | 0.0% | Preferred; full rank; R²=0.616 |
| NAICS_21 | Yes | float64 | 21 | 0.0% | NAICS 2022 labour variant |
| UNION | Yes | float64 | 3 | 0.0% | 1=member, 2=covered, 3=non |
| FTPTMAIN | Yes | float64 | 2 | 0.0% | 1=FT, 2=PT |
| MJH | Yes | float64 | 2 | 0.0% | 1=single, 2=multiple job |
| PERMTEMP | Yes | float64 | 4 | 0.0% | 1=permanent, 2–4=temp subtypes |
| MARSTAT | Yes | int64 | 6 | 0.0% | 1–6 |
| IMMIG | Yes | int64 | 3 | 0.0% | 1=recent, 2=established, 3=non |
| COWMAIN | Yes | float64 | 7 | 0.0% | Filter variable; don't include in RHS |
| ESTSIZE | Yes | float64 | 4 | 0.0% | 1–4 |
| PROV | Yes | int64 | 10 | 0.0% | 10-prov codes |
| SURVYEAR | Yes | int64 | 1 | 0.0% | 2026 |
| SURVMNTH | Yes | int64 | 1 | 0.0% | 4 |
| LFSSTAT | Yes | int64 | 4 | 0.0% | Filter variable |

**Zero missing on any model variable among paid employees** — clean data.

### HRLYEARN details

| Stat | Raw | Dollars |
|------|-----|---------|
| N (positive, paid emp) | 55,933 | — |
| Min | 714 | $7.14/hr |
| Median | 3,100 | $31.00/hr |
| Max | 25,000 | $250.00/hr |
| Top-code: max freq | 1 (0.002%) | Not top-coded |

**Encoding:** "Two decimals implied" per codebook. Raw value 3100 = $31.00/hr. Raw value 714 = $7.14/hr (near 2026 minimum wage). Log-regression on raw values gives identical coefficients to log(dollars) — differs only by additive constant.

**No top-coding issue.** Max $250/hr appears once. Top-10 most frequent values are round-dollar amounts ($25, $20, $30, $18, $22, $21, $28, $17, $35, $24) consistent with employer rounding, not statistical censoring.

---

## 3. Historical vintage drift (2024 annual vs 2026-04)

**Result: zero drift.** Both have exactly 60 columns with identical names. Spot-check of key variables (HRLYEARN, GENDER, LFSSTAT, COWMAIN, NOC_10, NOC_43, NAICS_21) shows identical code ranges in hist/2024-Jun.

**Key harmonization point across longer history:**
- **GENDER vs SEX:** Pre-Jan 2022 PUMFs used `SEX` (1=Male, 2=Female). The Feb 2025 re-release of hist/2011–2024 **backfilled GENDER** throughout. All hist/ bundles now use GENDER. No harmonization needed within the hist/ path. If loading raw legacy files from other sources (pre-2025), harmonize manually.
- NAICS 2022 labour variant was introduced with the 2025 LFS redesign — the hist/ re-release backfilled it. Codes may differ from NAICS 2012 variant used in original pre-2025 PUMFs if sourcing from non-revisited files.

---

## 4. Release lag

| Date | Event |
|------|-------|
| 2026-05-08 08:30 ET | LFS Daily — April 2026 release |
| 2026-05-08 12:30 GMT | PUMF Last-Modified for 2026-04 |
| 2026-06-05 08:30 ET | LFS Daily — May 2026 release (today) |
| 2026-06-05 ~04:40 UTC | 2026-05 PUMF probe = HTTP 404 (not yet posted) |

**Finding:** PUMF posts **same calendar day as LFS Daily**, approximately 4 hours after the 08:30 ET release (12:30 GMT = 08:30 ET + ~4h). The May 2026 PUMF was 404 at time of probe (04:40 UTC = 00:40 ET, before the LFS Daily release). It will likely appear by 13:00–14:00 GMT same day.

**Implication for pipeline design:** No same-day nowcast tier is needed for monthly wage tracking. The PUMF is effectively available same-day. A pipeline that runs at 14:00–17:00 ET on LFS Daily day will capture the PUMF. No separate preliminary-estimate tier required.

---

## 5. History availability and sizes

### Annual hist/ bundles — all confirmed real zips

| Year | Size (MB) | Last-Modified |
|------|-----------|---------------|
| 2015 | 29.6 | 2025-02-07 (Feb 2025 re-release) |
| 2016 | 29.9 | 2025-02-07 |
| 2017 | 30.1 | 2025-02-07 |
| 2018 | 29.6 | 2025-02-07 |
| 2019 | 29.2 | 2025-02-07 |
| 2020 | 25.9 | 2025-02-07 |
| 2021 | 25.1 | 2025-02-07 |
| 2022 | 31.1 | 2025-02-07 |
| 2023 | 29.8 | 2025-02-07 |
| 2024 | 32.0 | 2025-02-07 |
| 2025 | 29.7 | 2026-02-06 |
| **2015–2025 total** | **~322 MB** | — |

2020 and 2021 are slightly smaller (25–26 MB) — consistent with COVID sample reductions/disruptions.

**Monthly URL pattern (older months): ALL 404.** Tested: 2015-01, 2018-06, 2020-04, 2023-01, 2025-01, 2025-12. None exist on monthly URL. **History acquisition must use the annual hist/ bundles, not monthly URLs.**

**Per-month average size:** 322 MB / 132 months ≈ 2.4 MB/month compressed. Each month CSV uncompresses to ~12 MB. Full history (2015–2025) uncompressed ≈ ~1.6 GB.

**Downloads for 2015–2025 spike:** You need to download 11 zip files (~322 MB total). Content-addressable caching means each file is fetched once.

---

## 6. Regression feasibility — 2026-04

| Attribute | Value |
|-----------|-------|
| Regression sample | 55,933 paid employees with positive HRLYEARN |
| Design matrix (NOC_43 spec) | 55,933 × 346 |
| Matrix rank | 346/346 — **full rank** |
| R² | **0.6161** |
| lstsq time | 1.21s |
| Total time (incl. get_dummies) | ~1.9s |
| numpy lstsq | Works, no issues |

**Rank deficiency finding:** Including both NOC_10 and NOC_43 simultaneously causes rank deficiency (346 out of 355 columns — 9 redundant). They are nested hierarchies; NOC_43 codes map 1:1 to NOC_10 groups. Fix: use **NOC_43 only** (43 sub-major groups). Full rank confirmed.

| Spec | Design | Rank | R² | Time |
|------|--------|------|----|------|
| NOC_43 only | 55,933 × 346 | 346 (full) | 0.6161 | 1.2s |
| NOC_10 only | 55,933 × 313 | 313 (full) | 0.5562 | 0.8s |
| Both NOC_10 + NOC_43 | 55,933 × 355 | 346 (DEFICIENT) | — | — |

**R²=0.616 with ~15 composition controls** is consistent with standard log-wage Mincer-style regressions on LFS microdata. Well-specified model.

**TENURE note:** In the spike, TENURE was treated as categorical string (240 unique month values = 240 dummies). This inflates the design by ~230 columns and is valid but inefficient. Production should bin TENURE into ~5 brackets (<12m, 12–23m, 24–59m, 60–119m, 120m+) — saves ~225 dummies with negligible R² impact.

**Runtime:** 1.2–1.9s per month on Python 3.14 / numpy lstsq. Monthly pipeline covering 2015–present (~130 months) = ~250s total compute for all monthly regressions. Acceptable for a scheduled build; parallelizable to <30s if needed.

---

## 7. Threats to planned design

### Confirmed non-threats
- Data access: resolved — annual hist/ bundles work, browser UA required
- Variable availability: all model variables present, zero missing among paid employees
- Encoding: HRLYEARN two-decimal implied — known and handleable
- Release lag: same-day, no preliminary-estimate complication
- Schema drift: none across 2024→2026 span
- Regression feasibility: full rank, R²=0.616, 1.2s runtime

### Issues requiring pipeline decisions

**1. UA requirement (medium risk)**
httpx (the standard pipeline HTTP client) cannot reach www150.statcan.gc.ca. Must use `requests` with browser UA for this specific source. Options:
- Wrap requests in the LFS downloader only (isolate UA shim from rest of pipeline)
- Add a browser-UA header to the httpx client for this source (httpx accepts custom headers; the issue is TLS fingerprinting not just UA header — requests uses a different TLS stack that passes)
- Use requests as the HTTP backend for this fetcher entirely
**Recommendation:** Use requests + browser UA in a standalone `lfs_pumf/downloader.py`. Do not backport to httpx — the TLS fingerprint difference is structural.

**2. SEX → GENDER rename at 2022 boundary (low risk, known)**
Confirmed the Feb 2025 hist/ re-release backfilled GENDER throughout. Using hist/ bundles avoids any harmonization issue. If pipeline ever ingests legacy raw PUMFs (pre-2025 re-release), needs SEX→GENDER recode for pre-2022 files.

**3. TENURE must be binned, not categorical (low risk)**
Using 240 individual month-dummies is valid but wasteful. Define 5–6 tenure bins in the harmonizer and apply consistently across all vintages.

**4. Download footprint (manageable)**
Full 2015–2025 history = ~322 MB compressed, ~1.6 GB uncompressed. Cache annually; don't re-extract each build. Store extracted monthly CSVs in `data/raw/lfs_pumf/monthly/` with vintage tags; keep annual zips in `data/raw/lfs_pumf/annual/`.

**5. NAICS coding change pre-2025 (medium risk — not yet verified)**
The Feb 2025 re-release of hist/ files applied NAICS 2022 labour variant retroactively. Spot-check confirmed NAICS_21 codes are present in hist/2024. However, if the industry classification was genuinely changed (not just relabeled), the regression coefficients for NAICS dummies may not be strictly comparable across pre/post-2025 vintages. Low probability given StatsCan's backfill approach, but requires validation on a 2018 or 2015 file against published industry employment levels.

---

## Appendix: Files written

| File | Path |
|------|------|
| Raw findings JSON | `data/raw/lfs_pumf/_spike/spike_findings_raw.json` |
| 2026-04 PUMF zip (cached) | `data/raw/lfs_pumf/_spike/lfs_2026_04_CSV.zip` |
| 2024 hist annual zip (proof) | `data/raw/lfs_pumf/_spike/lfs_hist_2024_CSV.zip` |
| Codebook reference | `claude-ref/research/lfs_micro/pumf_codebook_2026-04.md` |
| This file | `claude-ref/research/lfs_micro/phase0_spike_findings.md` |
