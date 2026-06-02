# Recession Watch — Back-History Feasibility Recon

**Question:** How far back can we defensibly build (a) GDP-by-industry breadth and
(b) employment-by-industry breadth, at a coarse common-sector level, to extend the
Recession Watch comparators before the modern NAICS series starts in 1997-01?

**Status:** Feasibility research, not a build. Verified against StatCan WDS API metadata
and primary StatCan/C.D. Howe pages where reachable. Items marked "to confirm" were not
directly verified at member-level.

Date of recon: 2026-06-02.

---

## BOTTOM LINE (answer to Q5)

**GDP-by-industry breadth** can be built defensibly back to **1961-01** at a ~13-sector
SIC level (monthly), with a clean NAICS-on-NAICS bridge available from **1981-01** that
removes the SIC seam entirely for the three most recent recessions. So:

- **NAICS-native breadth (no concordance needed): 1981-01 → present.** Covers
  **4 of 5** CD Howe recessions: 1981-82, 1990-92, 2008-09, 2020. Built by chaining
  archived monthly NAICS GDP table **36-10-0390** (1981-2007) + **36-10-0398** (to 2017)
  + current **36-10-0434** (1997→present). One internal NAICS-vintage seam, not an SIC seam.
- **SIC breadth (concordance needed): 1961-01 → 1997-09** at ~13 broad SIC sectors,
  via archived monthly table **36-10-0378** (CANSIM 379-0007). Bridged to the NAICS era
  through the official **SIC-E 1980 → NAICS 1997** concordance at a coarse ~10-13 common-
  sector level. This reaches the **1974-75** episode (the 5th, oldest comparator) — but
  with the largest caveat (see seams).

**Employment-by-industry breadth** can be built defensibly back to **1976-01** at
**~16 NAICS sectors** (monthly SA), via current table **14-10-0355** (CANSIM 282-0088).
That covers **4 of 5** recessions (1981-82 onward; misses 1974-75 by ~2 years). A
pre-1976 coarse-sector employment extension exists **annually only** in Historical
Statistics of Canada Section D (back to 1946/1961 on SIC) — enough to characterize the
1974-75 labour shape annually, but NOT at monthly breadth resolution.

**Single most promising source to pull for the GDP back-history:**
**StatCan archived table 36-10-0378-01 (CANSIM 379-0007)** — "GDP at factor cost, by
Standard Industrial Classification, 1980 (SIC), monthly", 1961-01 to 1997-09, 908 series,
34 top-level SIC industries. It is the direct monthly predecessor to 36-10-0434, fully
downloadable from the StatCan WDS API, and overlaps the NAICS-era tables (1981-1997) so
the SIC→NAICS bridge can be **empirically calibrated on the overlap**, not just assumed
from the published concordance. Pull this first.

---

## VERDICT TABLE

| Source (table / pub) | Earliest | Frequency | Granularity | Recessions reached | Accessibility | Caveat |
|---|---|---|---|---|---|---|
| **36-10-0378** (CANSIM 379-0007) GDP at factor cost by SIC 1980 | **1961-01** (to 1997-09) | Monthly | 34 top-level SIC industries (~13 broad sectors) | All 5 (1974-75 → 2020), with bridge | WDS API, ARCHIVED but downloadable | Factor cost not basic prices; SIC→NAICS seam; aggregates/components mixed in 908 series |
| **36-10-0390** (CANSIM 379-0019) monthly GDP by NAICS | **1981-01** (to 2007-07) | Monthly | NAICS, 312 members | 1981-82, 1990-92, 2008-09 | WDS API, ARCHIVED | NAICS-native; older vintage / base year vs 0434 |
| **36-10-0398** (CANSIM 379-0027) monthly GDP by NAICS | ~1997 (to ~2017) — to confirm exact start | Monthly | NAICS | 2008-09 | WDS API, ARCHIVED | Bridge vintage between 0390 and 0434 |
| **36-10-0434** (CANSIM 379-0031) GDP by industry, monthly | 1997-01 | Monthly | NAICS ~20 sectors / hundreds detail | 2008-09, 2020 | WDS API, CURRENT | Modern clean series; the 1997 wall we are extending |
| **36-10-0387** (CANSIM 379-0016) Historical index of constant-price GDP by industry | **1919** (to 1971) | **Annual** | Industry (count to confirm) | 1974-75 only annually (ends 1971 — pre-dates it) | WDS API, ARCHIVED | Annual; ends 1971, so does NOT reach 1974-75 monthly |
| **Hist. Stats of Canada Sec. F**, F225-240 Real Domestic Product by industry | ~1935 (to ~1969) | **Annual** | Industry (coarse) | none monthly | StatCan 11-516-X, CSV | Annual; ends ~1969 |
| **14-10-0355** (CANSIM 282-0088) LFS employment by industry | **1976-01** | Monthly SA | ~16 NAICS sectors (21 members) | 1981-82, 1990-92, 2008-09, 2020 | WDS API, CURRENT | NAICS only; starts 1976, misses 1974-75 |
| **Hist. Stats of Canada Sec. D**, D290-317 / D341-354 employment by industry | **1961** (1946 on older SIC) | **Annual** | Coarse SIC major groups | 1974-75 annually | StatCan 11-516-X, CSV | Annual; SIC; establishment survey basis differs from LFS |
| **SIC-E 1980 → NAICS 1997 concordance (2-digit)** | n/a (bridge) | n/a | 18 SIC majors (A-R) ↔ NAICS sectors | enables all | StatCan, ARCHIVED, "contact for alt format" | **Many-to-many**; clean only at ~10-13 super-sectors |
| **CD Howe Commentary 366** (Cross & Bergevin) | dates from 1926 | n/a | dating chronology, not industry data | sets the 5 dates | cdhowe.org PDF | Not an industry dataset; provides peak/trough dates only |

---

## Q1 — Archived monthly real GDP-by-industry under SIC (pre-1997)

**YES — it exists and is downloadable.**

- **Table 36-10-0378-01, formerly CANSIM 379-0007.** Verified via WDS `getCubeMetadata`:
  - Title: "Gross domestic product (GDP) at factor cost, by Standard Industrial
    Classification, 1980 (SIC), monthly"
  - `cubeStartDate` **1961-01-01**, `cubeEndDate` **1997-09-01**, `frequencyCode` 6 (monthly)
  - `nbSeriesCube` **908**, `archiveStatusEn` ARCHIVED (publicly available, no longer updated),
    `releaseTime` 2009-01-19
  - Industry dimension: **34 top-level members**, 227 total. Top-level coarse sectors include:
    Agricultural & related services, Fishing & trapping, Logging & forestry, Mining/quarrying/
    oil wells, Manufacturing, Construction, Transportation & storage, Communication, Other
    utilities, Wholesale trade, Retail trade, Finance/insurance/real estate, Community/business/
    personal services — i.e. ~13 clean broad sectors plus aggregates (Total economy, Business
    sector, Business sector goods/services).
  - **Earliest date = 1961-01**, not 1981 — better than the brief stated as a floor.
  - Unit is **factor cost** (the pre-1997 convention), NOT basic prices. This matters for the
    bridge (basic prices = factor cost + taxes-less-subsidies on production); for *breadth*
    (sign of each sector's growth) the level convention is second-order, but flag it.

- Annual / lower-frequency archived companions (for context, not the monthly build):
  - **36-10-0387** (CANSIM 379-0016) "Historical index of constant price GDP by industry",
    **annual, 1919-1971**. Ends 1971, so does NOT reach 1974-75 even annually at the margin.

## Q2 — SIC→NAICS concordance

**YES — official StatCan concordance exists.** "SIC-E 1980 → NAICS 1997 (2-digit level)",
hosted under statcan.gc.ca/en/subjects/standard/concordances. Structure verified:

- **18 SIC-E 1980 major categories (A through R)** mapping to NAICS 1997 sectors.
- Mapping is **many-to-many** at the published 2-digit level (e.g., one SIC major splits across
  several NAICS; a special "-----" code covers head-office functions classified across all
  industries). It is NOT clean one-to-one at 2-digit.
- **Defensible aggregation level for breadth:** collapse to a **coarse ~10-13 super-sector**
  common grid where the many-to-many edges mostly net out within a super-sector — e.g.:
  Agriculture/primary, Mining & energy, Manufacturing, Construction, Trade (wholesale+retail),
  Transport & warehousing, Information & communication, FIRE, Business/professional services,
  Public & personal services, Utilities. At that level the SIC 13-sector grid and the NAICS
  20-sector grid both reduce cleanly, and the breadth statistic (% of super-sectors contracting)
  is consistent across the seam.
- **Best practice (the reason 0378 is the top pick):** the 1981-1997 overlap between SIC table
  0378 and NAICS table 0390 lets us **empirically calibrate** the super-sector bridge rather
  than rely on the published concordance alone — measure how often the SIC-grid breadth and
  NAICS-grid breadth agree on the same months, and only ship the coarsening level where they do.
- Accessibility caveat: the concordance page is ARCHIVED; download may require "contact us"
  for an alternative format. The mapping logic is visible on-page regardless.

## Q3 — Long-run business-cycle / industry datasets

- **Cross & Bergevin, "Turning Points: Business Cycles in Canada Since 1926"** — C.D. Howe
  Commentary **No. 366, October 2012**. Verified it exists (cdhowe.org PDF; SSRN 2176382 — SSRN
  403'd on fetch; IDEAS/RePEc cdh/commen/366 confirms record). This is a **dating chronology,
  not an industry dataset** — it establishes peak/trough dates reviewed by the C.D. Howe Business
  Cycle Council, combining real GDP with other coincident real-activity indicators. The PDF is a
  binary/image PDF (text not extractable via WebFetch); its underlying monthly inputs are the
  StatCan national-accounts and GDP-by-industry series themselves, i.e. it points back to the
  same 0378/0434 lineage rather than offering a separate downloadable industry series.
  **Use it for the dates, not for the data.** [Mode-3 style: cite as the source of the dates.]
- **Historical Statistics of Canada (StatCan 11-516-X)** — CSV-downloadable:
  - **Section F (GNP/capital/productivity):** series **F225-240 "Real Domestic Product by
    industry," annual, ~1935 to ~1969**, coarse industry. Annual only.
  - These are annual backcasts; useful to *characterize* 1974-75 industry shape annually but
    cannot feed a monthly breadth statistic.
- **No clean downloadable monthly industry backcast before 1961** was found. The monthly wall is
  1961 (0378); everything earlier is annual.

## Q4 — Employment by industry history

- **Confirmed modern series: 14-10-0355 (CANSIM 282-0088)** "Employment by industry, monthly,
  SA". Verified via WDS: `cubeStartDate` **1976-01-01**, monthly, NAICS dimension 21 members
  (~16 named sectors), CURRENT. So LFS employment-by-industry at ~16 sectors back to **1976-01**
  is solid — reaches 1981-82, 1990-92, 2008-09, 2020.
- **Pre-1976:** LFS itself doesn't carry monthly industry detail before 1976 in the modern cube.
  The Historical Statistics of Canada **Section D** carries employment-by-industry on SIC:
  - D290-317 (1961-1975, 1960 SIC) and D341-354 (1961-1975, paid workers, 1960 SIC); older
    D266-289 / D318-340 back to 1946/1931 on 1948 SIC.
  - But these are **annual averages**, and partly from the establishment-based Employment Survey
    (firms with 20+ employees), a different universe than the household LFS. So a pre-1976
    employment-breadth extension to 1974-75 is possible **annually and with a basis caveat**,
    not at monthly resolution.
  - Practical read: **do not** try to push monthly employment breadth before 1976. If 1974-75 is
    wanted on the labour side, present it as an annual coarse-sector snapshot, clearly seamed.

## Five CD Howe recessions — coverage by build

CD Howe Business Cycle Council monthly peak→trough dates (verified via cdhowe.org council pages):
1981-82 (Jun 1981 → Oct/Nov 1982), 1990-92 (Mar 1990 → ~Apr/May 1992),
2008-09 (Oct/Nov 2008 → May 2009), 2020 (Feb 2020 → Apr 2020). The 1974-75 episode sits in the
longer 1926 chronology (Cross-Bergevin) and is the oldest comparator; note Canada's mid-1970s
slowdown is milder and sometimes treated as a growth recession — confirm its exact CD Howe
classification before labelling it the "5th recession" in reader copy.

| Recession | GDP breadth, NAICS-native (1981+) | GDP breadth, SIC-bridged (1961+) | Employment breadth, monthly (1976+) |
|---|---|---|---|
| 1974-75 | no | **yes (SIC, bridged)** | no (annual only) |
| 1981-82 | yes | yes | yes |
| 1990-92 | yes | yes | yes |
| 2008-09 | yes | yes | yes |
| 2020 | yes | yes | yes |

## SEAMS & CAVEATS (ship these with any chart)

1. **The 1997 SIC→NAICS seam** is the main one. Mitigate by (a) coarsening to ~10-13 super-sectors
   and (b) preferring the NAICS-native 0390 chain for 1981+ so the SIC bridge is only load-bearing
   for 1974-75.
2. **Factor cost (0378) vs basic prices (0434/0390).** Affects levels, minimally affects sign-of-
   growth breadth. State the convention.
3. **NAICS-vintage seams within the post-1981 chain** (0390 → 0398 → 0434): different base years /
   chaining vintages. Splice on growth rates, not levels.
4. **908 series in 0378 mix aggregates with components** — must filter to the ~13 clean top-level
   SIC sectors before computing breadth, or breadth is double-counted.
5. **Employment pre-1976 is annual and establishment-based** — different universe from LFS; don't
   splice into the monthly LFS line.
6. **1974-75 classification** — confirm CD Howe treats it as a full recession before headlining it.

---

## SOURCES (primary)

- WDS `getCubeMetadata` for 36100378, 14100355, 36100390 (start/end dates, series counts,
  archive status, industry-member counts) — fetched 2026-06-02.
- StatCan table pages: 3610037801, 3610038701, 3610039001 (statcan.gc.ca tv.action).
- SIC-E 1980 → NAICS 1997 concordance (statcan.gc.ca/en/subjects/standard/concordances/
  sice1980-naics1997_2).
- Historical Statistics of Canada 11-516-X Section F (sectionf/4057751) and Section D
  (sectiond/4057750).
- C.D. Howe Commentary 366 (cdhowe.org/wp-content/uploads/2024/12/Commentary_366_0-2.pdf;
  record at ideas.repec.org/a/cdh/commen/366.html) and Business Cycle Council pages
  (cdhowe.org/council/business-cycle-council).

**To confirm before build:** exact start/end of 36-10-0398; CD Howe classification of 1974-75;
industry-member count of 36-10-0387; whether the concordance CSV is retrievable without contacting
StatCan.
