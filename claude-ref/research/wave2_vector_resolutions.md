# Wave 2 Vector Resolutions

Resolution of six StatCan probe failures from the backend 2026-05-11 pipeline run.

Method: WDS `getCubeMetadata` to walk dimension hierarchies, `getSeriesInfoFromCubePidCoord` to resolve dimension-member coordinates to vector IDs, and `getDataFromVectorsAndLatestNPeriods` for validation receipts. Probe results documented for each failed vector.

All endpoints reached at https://www150.statcan.gc.ca/t1/wds/rest/ on 2026-05-11.

---

## 1. Why each probe failed

| Backend ID            | Suspected vector | Probe result                                                                                                          | Conclusion                |
| --------------------- | ---------------- | --------------------------------------------------------------------------------------------------------------------- | ------------------------- |
| ca_goods_income       | v121079          | `getSeriesInfoFromVector` returns `responseStatusCode: 4` (vector does not exist)                                     | Stale/incorrect guess     |
| ca_services_income    | v121080          | `responseStatusCode: 4`                                                                                               | Stale/incorrect guess     |
| ca_primary_income     | v121081          | `responseStatusCode: 4`                                                                                               | Stale/incorrect guess     |
| ca_secondary_income   | v121082          | `responseStatusCode: 4`                                                                                               | Stale/incorrect guess     |
| pop_cma_toronto       | v91101001        | `responseStatusCode: 4`                                                                                               | Vector never existed      |
| aggregate_hours       | v53013087        | Resolves but to `Fraser South Health Service Delivery Area, BC; 20-34 yrs; Females; COPD` (product 13-10-0451) — wrong table entirely | Misidentified vector      |
| lfs_on_unemployment_rate | v2062825      | Resolves to `Canada; Participation rate; Men+; 15+; SA` (product 14-10-0287) — wrong characteristic, wrong gender, and Canada not Ontario | Misidentified vector |

The `v121079`-`v121082` series numbers correspond to the legacy CANSIM table 376-0001/0002 vintage; they were retired when the BOP move to the present 36-10-00xx product family happened, so any probe against them now returns "vector not found."

Vector `v91101001` is not a valid StatCan vector — likely a transcription error.

---

## 2. Resolution table

### Current account balances (annual table 36-10-0014)

Table 36-10-0014 - "Balance of international payments, current account and capital account, annual" - frequency 12, archive status CURRENT, runs 1981-2025.

Dimension layout:
- Dim1 Geography: 1 = Canada
- Dim2 Receipts/Payments/Balances: 3 = Balances
- Dim3 Current account and capital account: 3 = Goods, 5 = Services, 11 = Primary income, 17 = Secondary income
- Dim4 Countries or regions: 1 = All countries

Series labels confirmed `Canada;Balances;{Goods|Services|Primary income|Secondary income};All countries`. UOM is `$millions` (memberUomCode 81, scalar factor 6 in some metadata, decimals 0).

| Backend ID            | Coordinate                | Resolved Vector | Sample value (annual)         |
| --------------------- | ------------------------- | --------------- | ----------------------------- |
| ca_goods_income       | 1.3.3.1.0.0.0.0.0.0       | v61914625       | 2025: -31,101 ; 2024: -7,174  |
| ca_services_income    | 1.3.5.1.0.0.0.0.0.0       | v61914635       | 2025: +3,669 ; 2024: +1,476   |
| ca_primary_income     | 1.3.11.1.0.0.0.0.0.0      | v61914683       | 2025: +3,404 ; 2024: -7,058   |
| ca_secondary_income   | 1.3.17.1.0.0.0.0.0.0      | v61914731       | 2025: -6,378 ; 2024: -2,218   |

Note for backend: the `ca_*_income` label is misleading. Dim2 = 3 returns the BALANCE (net = receipts minus payments), not just receipts. If the backend variable was intended to mean "net trade in goods" then v61914625 is correct. If it was intended to mean "goods exports/receipts only," use Dim2 = 1 (different vector).

#### Quarterly alternative (table 36-10-0016)

Same dimension layout. Use these if the pipeline frequency is quarterly:

| Backend ID            | Coordinate                | Resolved Vector | Sample value (Q4 2025)        |
| --------------------- | ------------------------- | --------------- | ----------------------------- |
| ca_goods_income (Q)   | 1.3.3.1.0.0.0.0.0.0       | v61915093       | 2025Q4: -187 ; 2025Q3: -15,256|
| ca_services_income (Q)| 1.3.5.1.0.0.0.0.0.0       | v61915103       | 2025Q4: +3,256 ; 2025Q3: +3,803|
| ca_primary_income (Q) | 1.3.11.1.0.0.0.0.0.0      | v61915151       | 2025Q4: +3,309 ; 2025Q3: +3,843|
| ca_secondary_income (Q)| 1.3.17.1.0.0.0.0.0.0     | v61915199       | 2025Q4: -1,325 ; 2025Q3: -1,795|

---

### Toronto CMA population (table 17-10-0148, was 17-10-0135)

Table 17-10-0135 is ARCHIVED (2016 boundaries, last refPer 2022-07-01) — that is why v91101001 (and any current Toronto CMA pop probe against 17-10-0135) fails. The successor is `17-10-0148-01` ("Population estimates, July 1, by census metropolitan area and census agglomeration, 2021 boundaries"), CURRENT, runs 2001-2025.

Dim layout:
- Dim1 Geography: 22 = Toronto (CMA), Ontario
- Dim2 Gender: 1 = Total - gender
- Dim3 Age group: 1 = All ages

| Backend ID         | Coordinate              | Resolved Vector | Sample value (July 1)         |
| ------------------ | ----------------------- | --------------- | ----------------------------- |
| pop_cma_toronto    | 22.1.1.0.0.0.0.0.0.0    | v1589887692     | 2025: 7,108,874 ; 2024: 7,109,866 |

Validation: history pulled (6 periods) shows 6.49M (2020) -> 6.47M (2021, pandemic dip) -> 6.59M -> 6.84M -> 7.11M (2024) -> 7.11M (2025). The -992 YoY change in 2025 is consistent with the federal immigration policy reset; not a data error. Release time `2026-01-14T08:30` confirms this is the most recent annual revision.

Other CMAs (in case backend has the same problem for Montreal/Vancouver/Calgary/Ottawa-Gatineau):

| CMA                          | MemberID | Vector       | 2025 pop  |
| ---------------------------- | -------- | ------------ | --------- |
| Montreal (CMA), QC           | 14       | v1589878032  | (verified resolvable; coord 14.1.1.0.0.0.0.0.0.0) |
| Ottawa-Gatineau (CMA), ON/QC | 15       | v1589930472  | (coord 15.1.1.0.0.0.0.0.0.0) |
| Toronto (CMA), ON            | 22       | v1589887692  | 7,108,874 |
| Calgary (CMA), AB            | 37       | v1589908737  | (coord 37.1.1.0.0.0.0.0.0.0) |
| Vancouver (CMA), BC          | 44       | v1589917707  | (coord 44.1.1.0.0.0.0.0.0.0) |

---

### Aggregate hours worked (table 14-10-0289)

Table 14-10-0289 - "Actual hours worked at main job by industry, monthly, seasonally adjusted, last 5 months" - frequency 6, CURRENT, runs 1976-01 through 2026-04. The "last 5 months" label refers to the publication display; the underlying vector is continuous from 1976.

Dim layout:
- Dim1 Geography: 1 = Canada
- Dim2 NAICS: 1 = Total actual hours worked, all industries
- Dim3 Statistics: 1 = Estimate

| Backend ID       | Coordinate              | Resolved Vector | Sample value (Apr 2026)              |
| ---------------- | ----------------------- | --------------- | ------------------------------------ |
| aggregate_hours  | 1.1.1.0.0.0.0.0.0.0     | v4391505        | Apr-2026: 676,455.9 ; Mar-2026: 676,780.5 |

Units: thousands of hours (memberUomCode 152, scalar factor 3, decimals 1). Series title: `Canada;Total actual hours worked, all industries;Estimate`. Data type implicit in cube = SA.

Note: the probed `v53013087` was a completely unrelated BC health series (product 13-10-0451). The backend's vector-ID mapping for `aggregate_hours` should be updated to v4391505.

---

### Provincial unemployment rate (table 14-10-0287)

Table 14-10-0287 - "Labour force characteristics, monthly, seasonally adjusted and trend-cycle" - frequency 6, CURRENT, runs 1976-01 through 2026-04.

The probed `v2062825` returned `Canada; Participation rate; Men+; 15+; SA` (coord 1.8.2.1.1.1.0.0.0.0) — not Ontario, not unemployment rate, not Total-gender. So the backend either mis-typed the vector ID or pulled a stale mapping.

Correct coordinate template for a provincial unemployment rate, Total-gender, 15+, Estimate, SA:
`{GEO}.7.1.1.1.1.0.0.0.0`

Dim layout:
- Dim1 Geography: 1 = Canada, 6 = Quebec, 7 = Ontario, 10 = Alberta, 11 = British Columbia
- Dim2 Labour force characteristics: 7 = Unemployment rate
- Dim3 Gender: 1 = Total - Gender
- Dim4 Age group: 1 = 15 years and over
- Dim5 Statistics: 1 = Estimate
- Dim6 Data type: 1 = Seasonally adjusted

| Backend ID                  | Geo | Coordinate              | Resolved Vector | Sample value (Apr 2026) | Mar 2026 |
| --------------------------- | --- | ----------------------- | --------------- | ----------------------- | -------- |
| lfs_ca_unemployment_rate    | 1   | 1.7.1.1.1.1.0.0.0.0     | v2062815        | 6.9                     | 6.7      |
| lfs_qc_unemployment_rate    | 6   | 6.7.1.1.1.1.0.0.0.0     | v2063760        | 6.2                     | 5.4      |
| lfs_on_unemployment_rate    | 7   | 7.7.1.1.1.1.0.0.0.0     | v2063949        | 7.5                     | 7.6      |
| lfs_ab_unemployment_rate    | 10  | 10.7.1.1.1.1.0.0.0.0    | v2064516        | 7.0                     | 6.5      |
| lfs_bc_unemployment_rate    | 11  | 11.7.1.1.1.1.0.0.0.0    | v2064705        | 6.8                     | 6.7      |

All five series titles confirmed by `getSeriesInfoFromCubePidCoord`: `{Geo};Unemployment rate;Total - Gender;15 years and over;Estimate;Seasonally adjusted`. memberUomCode 239 = "Rate" (unitless percentage), decimals 1. The level-vs-rate problem reported by backend disappears because we are now explicitly selecting Dim2 = 7 (Unemployment rate) rather than Dim2 = 6 (Unemployment, which is a level in thousands of persons).

If the backend wants the non-SA version, change Dim6 to 2; if it wants Trend-cycle, change Dim6 to 3 (different vectors will resolve).

---

## 3. Summary action list for backend

```text
ca_goods_income          -> v61914625 (annual, $M)
ca_services_income       -> v61914635
ca_primary_income        -> v61914683
ca_secondary_income      -> v61914731
   (quarterly alts: 61915093/61915103/61915151/61915199 from table 36-10-0016)

pop_cma_toronto          -> v1589887692 (table 17-10-0148; old 17-10-0135 archived)

aggregate_hours          -> v4391505 (table 14-10-0289, SA monthly, thousands of hours)

lfs_ca_unemployment_rate -> v2062815
lfs_qc_unemployment_rate -> v2063760
lfs_on_unemployment_rate -> v2063949
lfs_ab_unemployment_rate -> v2064516
lfs_bc_unemployment_rate -> v2064705
```

## 4. Provenance

- Cube metadata pulled via POST `/t1/wds/rest/getCubeMetadata` for productIds 36100014, 36100016, 36100019, 17100135, 17100148, 14100289, 14100287.
- Coordinate-to-vector resolution via POST `/t1/wds/rest/getSeriesInfoFromCubePidCoord`.
- Sample values via POST `/t1/wds/rest/getDataFromVectorsAndLatestNPeriods` with latestN=2 (and latestN=6 for Toronto CMA history check).
- Failed-probe diagnosis via POST `/t1/wds/rest/getSeriesInfoFromVector` on v121079, v121080, v121081, v121082, v91101001, v53013087, v2062825 — first five returned `responseStatusCode: 4` (vector not found); the last two resolved to unrelated series.
- Run date: 2026-05-11.
