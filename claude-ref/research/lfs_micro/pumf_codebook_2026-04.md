# LFS PUMF Codebook Reference — 2026-04 vintage
# Source: Documents/LFS_PUMF_EPA_FGMD_codebook.csv inside lfs_2026_04_CSV.zip
# Catalogue: 71M0001X / 2021001
# Data file: pub0426.csv (112,707 rows x 60 columns)
# Codebook extracted: 2026-06-05

---

## Dataset overview

| Attribute | Value |
|-----------|-------|
| Rows (April 2026) | 112,707 |
| Columns | 60 |
| Universe | All respondents 15+ in 10 provinces |
| Weight variable | FINALWT (standard final weight, 1–99999) |
| HRLYEARN encoding | **Two decimals implied** — divide raw integer by 100 to get dollars |
| Sex/gender variable | **GENDER** (not SEX). SEX variable absent from post-2022 PUMFs. |

---

## HRLYEARN — Usual hourly wages

| Field | Value |
|-------|-------|
| Universe | Currently employed employees (COWMAIN in {1,2,3}) |
| Raw range | 000001–999999 (two decimals implied) |
| Dollar range | $0.01–$9,999.99 |
| Missing code | blank / NaN |
| Codebook note | "Before taxes and other deductions. Includes tips, commission and bonuses. Two decimals implied." |

**2026-04 empirics (paid employees, LFSSTAT 1–2, COWMAIN 1–2):**

| Stat | Raw | Dollars |
|------|-----|---------|
| N with positive HRLYEARN | 55,933 | — |
| Min | 714 | $7.14 |
| Median | 3,100 | $31.00 |
| Max | 25,000 | $250.00 |
| Max value frequency | 1 (0.002%) | — |

**Top-coding:** Max value $250.00/hr appears once. No mass at ceiling — **not top-coded in any meaningful sense** as of April 2026. The top-10 most frequent values cluster around round-dollar amounts ($25, $20, $30, $18, $22 etc.) — consistent with employer rounding, not top-coding.

**Units note for pipeline:** Store HRLYEARN raw as-is; divide by 100 in the transform layer. Log-regression uses log(raw) identically (differs only by additive constant log(100)).

---

## Model variable dictionary

Variables used in BoC SAN 2024-23 style composition-adjusted wage regression.

### HRLYEARN — Usual hourly wages
- Dtype: float64
- Universe: Employees only (COWMAIN 1–3, LFSSTAT 1–2)
- Codes: 000001–999999 (two decimals implied = cents); blank = not applicable
- Missing among paid employees: 0.0%

### FINALWT — Standard final weight
- Dtype: int64
- Universe: All respondents
- Codes: 1–99999
- Missing: 0.0%
- Note: Use as regression weight (WLS). Not bootstrapped bootstrap weights (not included in PUMF — use 500-replicate design if SE estimates needed; not required for point estimates).

### LFSSTAT — Labour force status
- Dtype: int64
- Universe: All respondents
- Codes: 1=Employed at work, 2=Employed absent, 3=Unemployed, 4=Not in labour force
- Employee filter: LFSSTAT in {1, 2}
- April 2026 counts: {1: 59,474, 2: 5,013, 3: 4,863, 4: 43,357}

### COWMAIN — Class of worker, main job
- Dtype: float64
- Universe: Currently employed or worked past 12 months
- Codes:
  - 1 = Public sector employees
  - 2 = Private sector employees
  - 3 = Self-employed incorporated, with paid help
  - 4 = Self-employed incorporated, no paid help
  - 5 = Self-employed unincorporated, with paid help
  - 6 = Self-employed unincorporated, no paid help
  - 7 = Unpaid family worker
  - blank = Not applicable
- Paid employee filter: COWMAIN in {1, 2} (excludes self-employed and unpaid)
- April 2026 counts: {1: 17,045, 2: 46,193, 3: 2,075, 4: 2,026, 5: 422, 6: 4,387, 7: 61}
- Note: COWMAIN=3 (self-employed incorporated with paid help) may have HRLYEARN; BoC SAN methodology excludes self-employed. Use {1,2} only for pure employee sample.

### GENDER — Gender of respondent
- Dtype: int64
- Universe: All respondents
- Codes: 1=Men+, 2=Women+
- Note: Replaced SEX variable from January 2022 onwards. LFS population controls based on sex at birth up to Dec 2021; gender from Jan 2022. SEX not present in post-2022 PUMF. **Historical files (pre-2022 via hist/) use SEX variable (1=Male, 2=Female) — harmonize on join.**
- Missing among paid employees: 0.0%

### AGE_12 — Five-year age group
- Dtype: int64
- Universe: All respondents
- Codes: 01–12
  - 01=15–19, 02=20–24, 03=25–29, 04=30–34, 05=35–39, 06=40–44
  - 07=45–49, 08=50–54, 09=55–59, 10=60–64, 11=65–69, 12=70+
- Missing among paid employees: 0.0%

### EDUC — Highest educational attainment
- Dtype: int64
- Universe: All respondents
- Codes: 0–6
  - 0=0 to 8 years, 1=Some high school, 2=High school graduate
  - 3=Some postsecondary, 4=Postsecondary certificate/diploma
  - 5=Bachelor's degree, 6=Above bachelor's degree
- Missing among paid employees: 0.0%

### TENURE — Job tenure with current employer
- Dtype: float64
- Universe: Currently employed only
- Codes: 001–240 (months); blank = not applicable
- n_distinct: 240 (continuous in months)
- Missing among paid employees: 0.0%
- **Pipeline note:** Treat as continuous or bin into tenure brackets. Do NOT use as categorical with 240 dummies — causes rank issues and over-parameterization. Recommended bins: <12m, 12–23m, 24–59m, 60–119m, 120m+.

### NOC_10 — Occupation (10 major groups)
- Dtype: float64
- Universe: Currently employed or worked past 12 months
- Codes: 01–10 (based on NOC 2021 labour variant)
  - 01=Management, 02=Business/finance/admin, 03=Natural/applied sciences
  - 04=Health, 05=Education/law/social/community/govt, 06=Art/culture/recreation/sport
  - 07=Sales and service, 08=Trades/transport/equipment, 09=Natural resources/agriculture
  - 10=Manufacturing and utilities
- Missing among paid employees: 0.0%
- **CRITICAL:** NOC_10 and NOC_43 are hierarchically nested. Including both causes rank deficiency (9 redundant columns). Use **NOC_43 only** for wage regression (R²=0.616 vs 0.556 for NOC_10 only).

### NOC_43 — Occupation (43 sub-major groups)
- Dtype: float64
- Universe: Currently employed or worked past 12 months
- n_distinct: 43 (codes 01–43, based on NOC 2021)
- Missing among paid employees: 0.0%
- **Use this, not NOC_10, for wage regression.**

### NAICS_21 — Industry of main job (21 groups)
- Dtype: float64
- Universe: Currently employed or worked past 12 months
- Codes: 01–21 (based on NAICS 2022 labour variant)
  - 01=Agriculture, 02=Forestry/logging, 03=Fishing/hunting/trapping
  - 04=Mining/quarrying/oil/gas, 05=Utilities, 06=Construction
  - 07=Manufacturing durable, 08=Manufacturing non-durable
  - 09=Wholesale trade, 10=Retail trade, 11=Transportation/warehousing
  - 12=Finance/insurance, 13=Real estate/rental, 14=Professional/scientific/technical
  - 15=Business/building/support services, 16=Educational services
  - 17=Health care/social assistance, 18=Information/culture/recreation
  - 19=Accommodation/food services, 20=Other services, 21=Public administration
- Missing among paid employees: 0.0%

### UNION — Union status
- Dtype: float64
- Universe: Currently employed employees
- Codes: 1=Union member, 2=Not member but covered by collective agreement, 3=Non-unionized
- Missing among paid employees: 0.0%

### FTPTMAIN — Full/part-time status at main job
- Dtype: float64
- Universe: Currently employed only
- Codes: 1=Full-time (30+ hrs/week), 2=Part-time (<30 hrs/week); blank=N/A
- Missing among paid employees: 0.0%

### MJH — Single or multiple jobholder
- Dtype: float64
- Universe: Currently employed only
- Codes: 1=Single jobholder (incl. job changers), 2=Multiple jobholder; blank=N/A
- Missing among paid employees: 0.0%

### PERMTEMP — Job permanency
- Dtype: float64
- Universe: Currently employed employees
- Codes: 1=Permanent, 2=Temporary seasonal, 3=Temporary term/contract, 4=Temporary casual/other
- Missing among paid employees: 0.0%

### MARSTAT — Marital status
- Dtype: int64
- Universe: All respondents
- Codes: 1=Married, 2=Common-law, 3=Widowed, 4=Separated, 5=Divorced, 6=Single never married
- Missing among paid employees: 0.0%

### IMMIG — Immigrant status
- Dtype: int64
- Universe: All respondents
- Codes: 1=Immigrant landed ≤10 years ago, 2=Immigrant landed >10 years ago, 3=Non-immigrant
- Missing among paid employees: 0.0%

### ESTSIZE — Establishment size
- Dtype: float64
- Universe: Currently employed employees
- Codes: 1=<20 employees, 2=20–99, 3=100–500, 4=>500; blank=N/A
- Missing among paid employees: 0.0%
- Note: FIRMSIZE (field 40) is a parallel variable including single-location firms. Use ESTSIZE.

### PROV — Province
- Dtype: int64
- Universe: All respondents
- Codes: 10=NL, 11=PEI, 12=NS, 13=NB, 24=QC, 35=ON, 46=MB, 47=SK, 48=AB, 59=BC
- Missing among paid employees: 0.0%
- Note: Territories (YT, NT, NWT) not in LFS PUMF.

### SURVYEAR / SURVMNTH — Survey year/month
- Dtype: int64
- Codes: SURVYEAR=four-digit year; SURVMNTH=01–12
- Use for vintage identification when combining annual hist/ bundles.

---

## Missing value conventions

**The LFS PUMF uses blank (NaN in pandas) as the universal not-applicable code.** There are no numeric sentinel codes (no 6/9/99 = not stated) in this vintage. Variables are restricted by universe — e.g., HRLYEARN is blank for non-employees, TENURE is blank for non-employed, etc.

| Pattern | Meaning |
|---------|---------|
| NaN / blank | Not applicable (respondent not in variable's universe) |
| Numeric codes | Valid responses only — no embedded missing codes |

**Exception:** A handful of variables use a sentinel within their range:
- TENURE: codebook lists "001–240 months, blank=N/A" — no 999 sentinel
- HRLYEARN: "000001–999999, blank=N/A" — no sentinel

**Pipeline implication:** `df[col].isna()` is the correct missing check. No need to recode numeric sentinels.

---

## Variable drift vs. historical PUMF (2024 annual vs 2026-04)

Column count: **identical** (60 columns). No columns added or removed between hist/2024 (Feb 2025 re-release) and 2026-04. Code ranges also match on spot check.

**One known harmonization issue:** GENDER vs SEX across the 2022 redesign boundary:
- Pre-Jan 2022: variable is `SEX` (codes 1=Male, 2=Female)
- Post-Jan 2022: variable is `GENDER` (codes 1=Men+, 2=Women+)
- The Feb 2025 re-release of hist/2011–2024 **backfilled GENDER** — verified: hist/2024-Jun has GENDER, not SEX. Harmonization across the full 2015–2025 history should use GENDER throughout if using the hist/ bundles.

---

## Files inside lfs_2026_04_CSV.zip

| File | Size (uncompressed) |
|------|---------------------|
| pub0426.csv | 12,394,401 bytes (data) |
| Documents/LFS_PUMF_EPA_FGMD_codebook.csv | 38,603 bytes |
| Documents/LFS_PUMF_EPA_FGMD_codebook_formatted.xlsx | 34,228 bytes |
| Documents/LFS_PUMF_EPA_FGMD_recordlayout.csv | 1,093 bytes |
| Documents/UserGuide_LFS_PUMF_2025_ENG.pdf | 772,391 bytes |
| Documents/GuidedelUtilisateur_FMGD_EPA_2025_FRA.pdf | 939,125 bytes |
| Documents/Note to LFS PUMF Users_2025.docx | 16,928 bytes |
| Documents/Note aux utilisateurs du FMGD de l EPA_2025 .docx | 17,336 bytes |
| Documents/LFS_PUMF_FGMD_EPA_README_LISEZ MOI.txt | 87 bytes |
