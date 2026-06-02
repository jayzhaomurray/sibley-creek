# Recession Watch — Scoping Recon
**Date:** 2026-06-01
**Author:** backend-engineer (Claude)
**Status:** Analysis only. No production pipeline modules built.

---

## LOCKED METHODOLOGY

Two timely monthly sources only: real GDP by industry (StatCan 36-10-0434, value-added at basic prices, monthly) and the Labour Force Survey (monthly). Organized around three gauges + a trigger:

- **DEPTH** = deviation from the true cyclical peak. Compute as: smooth the level with a 3-month moving average, take the expanding high-water mark (highest smoothed level up to that month; it resets upward at each new high), depth = current smoothed level / high-water mark - 1. No fixed lookback window. Applied to monthly GDP and to employment.
- **DURATION** = months since the last high-water mark was set, while depth remains below a small start threshold (~ -0.2%). Measures time-below-peak, NOT consecutive monthly declines.
- **DIFFUSION** = share of industries above their level 6 months ago; 50 = neutral line. GDP diffusion across 3-digit NAICS industries; employment diffusion across LFS sectors.
- **TRIGGER** = a recalibrated Canadian Sahm rule (see Part 2). Unemployment rate is also a top-line print.

Note for the methodology page: monthly GDP-by-industry is basic prices vs the expenditure GDP at market prices used elsewhere; they track closely but aren't identical.

---

## PART 1 — DATA AVAILABILITY RECON

### Methodology note on API probing

The StatCan WDS `getCubeMetadata` and `getSeriesInfoFromVector` endpoints currently return HTTP 404 for these tables. The `getDataFromCubePidCoordAndLatestNPeriods` batch endpoint exists but returns only the all-industries aggregate for 36-10-0434. The working approach is the bulk CSV download — both tables were downloaded directly and parsed from the 6.7MB and 7.6MB ZIPs respectively. All counts below are from primary source verification, not API inference.

---

### Series 1: Real GDP by industry, monthly (36-10-0434-01)

| Field | Value |
|---|---|
| Table | 36-10-0434-01 (CANSIM 379-0031) |
| Vector (all-industries headline) | v65201210 |
| History start | 1997-01-01 |
| Current end | 2026-03-01 |
| Release lag | ~60 days (last business day of month, T+2 months) |
| Frequency | Monthly |
| Seasonal adjustment | SA at annual rates (chained 2017$) |
| Units | C$ millions (chained 2017$); pipeline scales to C$ trillions |
| In pipeline | YES — `data/raw/gdp_monthly.csv` (catalog `gdp_monthly`, v65201210) |
| Sub-sector CSVs in pipeline | goods (v65201211), services (v65201212), manufacturing (v65201263), mining/oil (v65201236) |

**Industry granularity — CRITICAL finding:**

Bulk CSV download confirms the table publishes **249 unique SA industry series** for Canada. These span:

| NAICS level | Count |
|---|---|
| T-aggregate codes (T001-T018, cross-cutting) | 11 |
| 2-digit sectors | ~20 |
| 3-digit sub-sectors | ~84 |
| 4-digit industries | ~65 |
| 5-digit sub-industries | ~13 |
| Alphanumeric variants | ~56 |

**3-digit NAICS GDP diffusion is feasible.** The table contains the full NAICS hierarchy at SA monthly frequency. A diffusion index at the 3-digit level would draw on approximately 84 distinct 3-digit industries (e.g. Oil and gas extraction [211], Iron ore mining [21221], Manufacturing by sub-sector, etc.). After removing parent-aggregate rows to avoid double-counting, a diffusion index of ~84 true 3-digit leaf industries is achievable. Alternatively, targeting the ~20 2-digit sector aggregates is simpler and still meaningful.

**Feasibility verdict: 3-digit GDP diffusion IS FEASIBLE.** Requires bulk CSV fetcher (not WDS vector API); bulk download is ~6.7MB. History starts 1997-01 only, which means the 1981-82 and 1990-92 recessions cannot be backtested for the GDP diffusion gauge.

---

### Series 2: LFS unemployment rate, monthly SA

| Field | Value |
|---|---|
| Table | 14-10-0287-01 |
| Vector | v2062815 |
| History start | 1976-05-01 |
| Current end | 2026-04-01 |
| Release lag | ~3 weeks after reference month |
| Frequency | Monthly |
| Seasonal adjustment | SA |
| Units | % |
| In pipeline | YES — `data/raw/unemployment_rate.csv` (catalog `unemployment_rate`) |

600 monthly observations, 1976-05 to 2026-04. Full Sahm backtest coverage.

---

### Series 3: LFS employment level, total + by industry

**Total employment level (SA monthly):**

| Field | Value |
|---|---|
| Table | 14-10-0287-01 |
| Vector | v2062811 |
| History start | 1976-05-01 |
| Current end | 2026-04-01 |
| Units | Millions (pipeline scales from thousands) |
| In pipeline | YES — `data/raw/employment_level.csv` |

**Employment by industry (SA monthly) — Table 14-10-0355-01:**

Bulk CSV download (14-10-0355-01) confirms **21 SA industry categories** for Canada, including total and 2 aggregates (goods/services), yielding **16 named NAICS sub-sectors** usable for diffusion:

1. Agriculture [111-112, 1100, 1151-1152]
2. Forestry, fishing, mining, quarrying, oil and gas [21, 113-114, 1153, 2100]
3. Utilities [22]
4. Construction [23]
5. Manufacturing [31-33]
6. Wholesale trade [41]
7. Retail trade [44-45]
8. Transportation and warehousing [48-49]
9. Finance, insurance, real estate, rental and leasing [52-53]
10. Professional, scientific and technical services [54]
11. Business, building and other support services [55-56]
12. Educational services [61]
13. Health care and social assistance [62]
14. Information, culture and recreation [51, 71]
15. Accommodation and food services [72]
16. Other services (except public administration) [81]
17. Public administration [91]

(Wholesale and retail trade [41, 44-45] is also available as a combined series.)

**History start: 1976-01-01.** Full backtest coverage including all four CD Howe recessions.

**Employment diffusion granularity verdict: 16-sector diffusion ONLY.** This is not 3-digit NAICS. The LFS suppresses sub-sector employment for reliability reasons. A 16-sector diffusion index is meaningful and consistent with how the CD Howe Council monitors breadth of employment decline. This is **not** a surprise — it is the structural limit of LFS monthly SA publication.

**Employment table NOT yet in pipeline.** 14-10-0355-01 needs a new bulk CSV fetcher for the diffusion use case. The existing pipeline has total employment level (v2062811) and goods/services employment only from 14-10-0287-01 (3 positions), not the 16-sector breakdown. The per-sector series do exist as individual WDS vectors (e.g. manufacturing employment SA is available as a separate vector — see the boc-tracker lift inventory) but the full 16-sector set is not yet wired.

---

### Series 4: LFS total actual hours worked, monthly SA

| Field | Value |
|---|---|
| Table | 14-10-0289-01 |
| Vector | v4391505 |
| History start | ~1976 (full LFS history) |
| Current end | 2026-04-01 |
| Units | Thousands of hours |
| In pipeline | YES — `data/raw/aggregate_hours.csv` (catalog `aggregate_hours`) |

Confirmed live via API: April 2026 = 676,455.9k hours. Useful as an ancillary recession depth indicator (hours drop before headcount in downturns) but not one of the four primary gauges in the locked methodology.

---

### Summary table

| Series | Table | Vector(s) | History | Lag | In pipeline? |
|---|---|---|---|---|---|
| Real GDP monthly (total) | 36-10-0434-01 | v65201210 | 1997-01 | ~60d | YES |
| GDP sub-aggregates (goods, svc, mfg, mining) | 36-10-0434-01 | v65201211-12, 63, 36 | 1997-01 | ~60d | YES (4 series) |
| GDP 3-digit NAICS (249 SA series) | 36-10-0434-01 | bulk CSV | 1997-01 | ~60d | NO (new bulk fetcher needed) |
| Unemployment rate SA | 14-10-0287-01 | v2062815 | 1976-05 | ~3w | YES |
| Employment level total SA | 14-10-0287-01 | v2062811 | 1976-05 | ~3w | YES |
| Employment by 16 sectors SA | 14-10-0355-01 | bulk CSV / ~16 vectors | 1976-01 | ~3w | NO (new fetcher needed) |
| Hours worked total SA | 14-10-0289-01 | v4391505 | ~1976 | ~3w | YES |

---

## PART 2 — CANADIAN SAHM CALIBRATION

Analysis uses `data/raw/unemployment_rate.csv` (v2062815, 600 obs, 1976-05 to 2026-04). Sahm gap = 3-month moving average of U-rate minus its trailing 12-month minimum. CD Howe recession dates used as benchmark; 1974-75 recession excluded (predates LFS monthly SA coverage).

### 2.1 US-default 0.5pp threshold

Every month the gap crosses 0.5pp (rising through), 1976-present:

| Date | Gap (pp) | Classification |
|---|---|---|
| 1977-02 | 0.600 | FALSE POSITIVE |
| 1980-04 | 0.533 | FALSE POSITIVE |
| 1981-10 | 0.667 | TRUE POSITIVE (1981-82) |
| 1990-02 | 0.500 | TRUE POSITIVE (1990-92) |
| 1990-07 | 0.500 | TRUE POSITIVE (1990-92) |
| 1992-05 | 0.500 | TRUE POSITIVE (1990-92) |
| 1993-06 | 0.500 | FALSE POSITIVE |
| 1996-10 | 0.500 | FALSE POSITIVE |
| 2001-12 | 0.767 | FALSE POSITIVE |
| 2008-12 | 0.567 | TRUE POSITIVE (2008-09) |
| 2020-03 | 1.000 | TRUE POSITIVE (2020 COVID) |
| 2023-10 | 0.500 | FALSE POSITIVE |

**Total crossings: 12 (6 true positives, 6 false positives).** The 0.5pp threshold over-triggers significantly in Canada. Three of the false positives (1990-07, 1992-05 counts as true but fires late in recession; 1993-06 is post-recession) reflect the 1990-92 recession being unusually prolonged. The 2001-12 false positive is notable — Canada did not have a formal recession in 2001, but the gap hit 0.77pp, likely driven by the tech/9-11 export shock. The 2023-10 trigger (gap=0.50, right at the threshold) came during the 2023-24 labour market softening without a recession.

### 2.2 Threshold sweep

| Threshold (pp) | Recessions caught (of 4) | False positives | Notes |
|---|---|---|---|
| 0.3 | 4 | 9 | 2015 oil alarm (peak=0.40) |
| 0.4 | 4 | 7 | 2015 oil alarm (peak=0.40) |
| 0.5 | 4 | 6 | US default; over-triggers |
| 0.6 | 4 | 7 | Note: re-triggers within 1990-92 |
| 0.7 | 4 | 5 | |
| 0.8 | 4 | 4 | |
| 0.9 | 4 | 5 | |
| 1.0 | 4 | 5 | |
| 1.1 | 4 | 1 | Significant improvement |
| 1.2 | 4 | 1 | |
| 1.3 | 4 | 1 | |
| 1.4 | 4 | 0 | All 4 caught, zero false positives |
| 1.5 | 4 | 0 | |

The sharp improvement between 0.8-1.0 pp (5 false positives) and 1.1 pp (1 false positive) is driven by eliminating the 2001 and 2023 triggers. At 1.4 pp all four recessions are caught with zero false positives. However, 1.4 pp fires AFTER the recession is underway (late-cycle confirm, not early warning).

### 2.3 Recommended Canadian threshold

**Recommendation: 0.8pp as the alert threshold; 1.2pp as the high-conviction signal.**

Rationale:
- **0.8pp** catches all 4 recessions, reduces false positives to 4 (vs 6 at 0.5pp), and provides a meaningful lead/coincident signal. The four false positives at 0.8pp are the 1977 post-1975 softening, the 1980 cycle (which the CD Howe dates as not a full recession but was a genuine sharp slowdown), the 1993-06 post-recession echo, and one more. For a "watch" function (alerting, not declaring), 0.8pp is appropriate.
- **1.2pp** eliminates all but one false positive and catches all four recessions. The remaining false positive is the 2001 event. 1.2pp is the high-conviction companion signal — when both 0.8pp and 1.2pp are triggered, declaration confidence is high.
- The tradeoff: higher thresholds fire later in recessions. At 1.4pp the signal is essentially a contemporaneous confirmation, not a warning.

**2015 oil false alarm:** The 2015-16 oil shock period peaked at a Sahm gap of 0.40pp (January 2016). Below any threshold in the recommended range. The 2015 episode does NOT trigger the Canadian Sahm at 0.5pp or above — in contrast to what might be expected.

**2026 status:** The Sahm gap peaked at 0.633pp in March 2025, crossed 0.5pp for four consecutive months (March-June 2025), then declined. As of April 2026 the gap is 0.133pp — below alert threshold. The gap triggered the US-default 0.5pp threshold in early 2025 but has since retreated. A Canadian-calibrated 0.8pp threshold was NOT triggered. This means the Recession Watch indicator for the Sahm gauge currently reads: **not triggered** (gap at 0.13pp, well below 0.8pp).

### 2.4 Last 14 months of Sahm gap

| Date | U-rate | 3mMA | Min12 | Gap | Status |
|---|---|---|---|---|---|
| 2025-03 | 6.8 | 6.700 | 6.067 | 0.633 | ALERT (>0.5pp) |
| 2025-04 | 6.9 | 6.767 | 6.200 | 0.567 | ALERT (>0.5pp) |
| 2025-05 | 7.0 | 6.900 | 6.300 | 0.600 | ALERT (>0.5pp) |
| 2025-06 | 6.9 | 6.933 | 6.367 | 0.567 | ALERT (>0.5pp) |
| 2025-07 | 6.9 | 6.933 | 6.467 | 0.467 | below threshold |
| 2025-08 | 7.1 | 6.967 | 6.500 | 0.467 | |
| 2025-09 | 7.1 | 7.033 | 6.567 | 0.467 | |
| 2025-10 | 6.9 | 7.033 | 6.667 | 0.367 | |
| 2025-11 | 6.6 | 6.867 | 6.667 | 0.200 | |
| 2025-12 | 6.8 | 6.767 | 6.667 | 0.100 | |
| 2026-01 | 6.5 | 6.633 | 6.633 | 0.000 | |
| 2026-02 | 6.7 | 6.667 | 6.633 | 0.033 | |
| 2026-03 | 6.7 | 6.633 | 6.633 | 0.000 | |
| 2026-04 | 6.9 | 6.767 | 6.633 | 0.133 | |

The U-rate was effectively reset to a new 12-month low of 6.5% in January 2026, which collapsed the gap to zero. The April 2026 uptick to 6.9% has nudged the gap back to 0.13pp — trivial. **The Canadian Sahm is not flashing any warning signal as of April 2026.**

---

## PART 3 — DEPTH GAUGE SANITY CHECK

Analysis uses on-disk CSVs: `data/raw/gdp_monthly.csv` (1997-01 to 2026-03) and `data/raw/employment_level.csv` (1976-05 to 2026-04). Depth = (3mma of level / expanding high-water mark of 3mma) - 1.

### 3.1 Employment depth across all four CD Howe recessions

All four recessions covered (1976 history).

| Recession | CD Howe Peak | Max depth date | Peak-to-trough depth |
|---|---|---|---|
| 1981-82 | 1981-06 | 1982-10 | -4.80% |
| 1990-92 | 1990-03 | 1992-05 | -3.02% |
| 2008-09 | 2008-10 | 2009-05 | -1.71% |
| 2020 COVID | 2020-02 | 2020-04 | -7.37% |

The method correctly identifies all four troughs as occurring at or near the official CD Howe trough dates. The 1981-82 recession was deeper in employment terms than 1990-92 (unusual — typically 1990-92 is cited as more severe, but 1982 was characterized by sharper job losses in the goods sector). The 2008-09 recession shows a modest -1.71% depth, consistent with the relatively mild Canadian experience versus the US. COVID shows -7.37% peak-to-trough on the 3mma, which is large but smaller than the instantaneous drop because the 3mma smoothing dampens the April 2020 spike.

### 3.2 GDP depth (2008-09 and 2020 only; 1997 history start)

The 1981-82 and 1990-92 recessions predate the monthly GDP-by-industry series (1997-01 start). GDP depth for those two must rely on quarterly expenditure GDP or the employment depth gauge as a proxy.

| Recession | CD Howe Peak | Max depth date | Peak-to-trough depth |
|---|---|---|---|
| 2008-09 | 2008-10 | 2009-05 | -4.36% |
| 2020 COVID | 2020-02 | 2020-04 | -8.17% |

The method correctly identifies the 2009-05 trough for the 2008-09 recession (consistent with CD Howe's official trough designation). For COVID, the 2020-04 trough on the 3mma basis slightly lags the most acute point — the instantaneous GDP drop was concentrated in March-April 2020 but the 3mma trough lands in June 2020 (-13.03%) as shown below.

### 3.3 Current depth status (as of latest data)

**GDP depth (monthly, latest 6 months):**

| Date | Depth |
|---|---|
| 2025-10 | -0.072% |
| 2025-11 | -0.087% |
| 2025-12 | -0.116% |
| 2026-01 | -0.069% |
| 2026-02 | 0.000% (at HWM) |
| 2026-03 | -0.001% |

GDP is essentially at its high-water mark as of March 2026. The DEPTH gauge reads near zero — no signal.

**Employment depth (monthly, latest 6 months):**

| Date | Depth |
|---|---|
| 2025-11 | 0.000% (at HWM) |
| 2025-12 | 0.000% |
| 2026-01 | 0.000% |
| 2026-02 | -0.156% |
| 2026-03 | -0.305% |
| 2026-04 | -0.443% |

Employment has slipped below its high-water mark in recent months, reaching -0.44% in April 2026. This is below the -0.2% start threshold that triggers DURATION counting — the duration clock is ticking. However -0.44% is shallow relative to recession thresholds (all four CD Howe recessions reached at least -1.7%).

### 3.4 COVID scale — does it dominate the depth chart?

| Measure | COVID trough depth | Date |
|---|---|---|
| GDP depth (3mma) | -13.03% | 2020-06 |
| Employment depth (3mma) | -13.24% | 2020-06 |

Yes — COVID dominates scale. The all-time worst depth for both GDP and employment is COVID 2020. The four "normal" recessions are -1.7% to -4.8% for employment and ~-4.4% for 2008-09 GDP. The depth chart will require axis truncation or a break notation for COVID. **Recommendation:** truncate y-axis at -8% with a note indicating the COVID trough is off-scale (annotated with -13%), or use a logarithmic scale.

---

## FEASIBILITY VERDICT

| Component | Feasibility | What's needed |
|---|---|---|
| DEPTH (GDP) | Ready | Uses existing `gdp_monthly.csv`; no new fetch |
| DEPTH (employment) | Ready | Uses existing `employment_level.csv`; no new fetch |
| DURATION | Ready | Derived from depth; no new fetch |
| TRIGGER (Sahm) | Ready | Uses existing `unemployment_rate.csv`; no new fetch |
| DIFFUSION (GDP, 3-digit) | Feasible with build | New bulk CSV fetcher for 36-10-0434 (6.7MB ZIP); ~249 SA series. History 1997+ only |
| DIFFUSION (employment, 16-sector) | Feasible with build | New bulk CSV fetcher for 14-10-0355 (7.6MB ZIP); 16 SA sectors. History 1976+ |

**Three of the four gauges are ready to build now using on-disk data.** Only the DIFFUSION gauge requires new fetchers. The diffusion gauges are the methodologically richest component but also the most infrastructure-intensive.

**Recommended phase order:**
1. Phase A (now): TRIGGER + DEPTH + DURATION using existing pipeline data
2. Phase B (next): Employment DIFFUSION (14-10-0355 bulk fetcher; 16 sectors; clean SA history to 1976)
3. Phase C (later): GDP DIFFUSION (36-10-0434 bulk fetcher; 249 series; note 1997-only history)

**Key design constraints to carry into production build:**
- GDP diffusion index must exclude aggregate/parent rows to avoid double-counting. Use only terminal leaf nodes in the NAICS hierarchy from 36-10-0434.
- Employment diffusion must use the 16 named sectors from 14-10-0355-01, not the goods/services split from 14-10-0287-01.
- The Sahm threshold for the published tracker should be **0.8pp** (alert) with a note that the US-default 0.5pp is shown as a comparison series.
- COVID 2020 must be handled explicitly in depth/duration charts — the expanding high-water mark correctly treats the post-COVID recovery as a new expansion from the COVID trough, so current GDP depth correctly reads near-zero (GDP recovered fully). Employment is slightly below its pre-COVID high-water mark only because the recovery slowed in 2024-25.
- The basic-prices vs market-prices distinction is real but operationally minor for a recession-detection purpose. The methodology page should note it; the tracker need not dual-publish.
