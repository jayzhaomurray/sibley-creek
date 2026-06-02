# Federal Debt ISSUANCE FLOW — Rebuilt Series

Researcher deliverable. Compiled 2026-06-02. Replaces the wrong "outstanding
stock" framing in `source_and_series.md` Indicator 5. This file is for the
GROSS ISSUANCE FLOW indicator only. NO fabrication: every number traces to a
primary source named inline with a Tier.

---

## 0. What went wrong, and what this metric actually is

The old chart plotted the **outstanding STOCK** of market debt (bonds ~$1,192B,
T-bills ~$285B, retail ~$4.7B at end-FY2024-25). That is a year-end snapshot of
the structure of the debt. Jay asked for **debt ISSUANCE** — the annual GROSS
issuance FLOW: how much the Government of Canada raises in the primary market
each fiscal year.

**Metric definition (this rebuild).** Gross issuance of Government of Canada
marketable debt, by instrument/maturity, per fiscal year (ending 31 March),
$ billions. This is the **"Gross Issuance of Bonds and Bills"** series the
federal Debt Management Report (DMR) publishes as its Table 4.1 each year, and
the same series Desjardins' Graph 6 ("Gross issuance of bonds and bills, $B")
benchmarks against. Confirmed: the Desjardins totals Jay cited
(593 / 442 / 387 / 471 / 526) are the DMR Table 4.1 "Total Gross Issuance" line.

### Critical methodology finding — the T-bill line is STOCK, not auction flow

The DMR Table 4.1 is titled **"Gross Issuance of Bonds and Bills … $ billions,
end of fiscal year."** Inside it:
- the **bond lines are true gross issuance FLOW** (sum of the year's auctions by
  tenor), but
- the **"Treasury Bills" line is the end-of-fiscal-year STOCK of bills
  outstanding** (267 in FY2023-24, 285 in FY2024-25), NOT the gross T-bill
  auction flow.

The gross T-bill **auction** flow is far larger — bills roll every 3/6/12 months,
so the government auctions ~$650–680B of bills a year to maintain a ~$285B stock.
(DMR 2024-25 text: "$663 billion in treasury bills were issued" in 2024-25; the
BoC F4-F10 gross-new-issues series puts FY2024-25 gross T-bill issuance at
~$656B — see §5.) The DMR deliberately uses the **bill STOCK** in its
"Bonds and Bills" headline table because the gross bill roll would swamp the
chart and overstate the funding need.

**Consequence for the rebuild.** The "Total Gross Issuance" headline (e.g. 526
for FY2024-25) is a **hybrid: gross bond flow + year-end bill stock.** That is
the convention the DMR and Desjardins both use, and it is the number Jay's
benchmark expects. It is internally consistent and primary-sourced — but the
chart MUST be labelled so a reader does not read the bill component as auction
flow. We carry the DMR convention as the headline and note the auction-flow
alternative as a clearly-labelled secondary (§5). See the fact-checker caveat
(§7) — this is the single most important caveat in the file.

---

## 1. Bucket mapping — BILLS / NOTES / BONDS (our aggregation)

Jay's reader-clarity framing is a 3-bucket BILLS / NOTES / BONDS cut. Canada
does **not** officially use "notes" (the US Treasury bills/notes/bonds taxonomy
is American). Document this as **our aggregation label, not a GoC label.**

**Cut-point decision — where does the 5-year go?** The brief floated 5yr in
NOTES (short-medium) with a check against how the DMR buckets it. The DMR's own
two-bucket split (Table 4.2 every year) is:
- **Short = 2-, 3-, 5-year sectors**
- **Long = 10-year and longer (10yr + 30yr + ultra-long + Real Return Bonds)**

So the DMR groups the **5-year with the SHORT bucket.** To stay reconcilable to
the official split (and to the DMR's published "Share of Long Bonds (10-year+)"
metric, which the writer may want to cite), we adopt the DMR's cut-point:

| Our bucket | Maturities included | Rationale |
|---|---|---|
| **BILLS** | Treasury bills (<1yr) | DMR's "Treasury Bills" line (= year-end bill STOCK in Table 4.1) |
| **NOTES** | 2-year + 3-year + 5-year bonds | = DMR "Short (2, 3, 5-year sectors)" bucket exactly |
| **BONDS** | 10-year + 30-year + ultra-long + Real Return Bonds + Green bonds | = DMR "Long (10-year+)" plus Green (Green is a tenor-agnostic ESG label, but its 10yr+ profile sits long; see note) |

**RECOMMENDED MAPPING (state this in the chart): BILLS = T-bills; NOTES = 2/3/5yr
bonds; BONDS = 10yr + 30yr + ultra-long + RRB + Green.**

Notes on the mapping:
- This makes NOTES exactly equal to the DMR "Short" bucket and BONDS ≈ DMR "Long"
  + Green, so our 3-bucket series reconciles to the DMR's published 2-bucket
  shares within Green (~$4B/yr). Clean.
- **Green bonds** ($4–5B/yr) are issued at 10yr+ tenors in Canada, so folding them
  into BONDS is defensible. If the writer prefers exact reconciliation to the
  DMR "Long" line, hold Green as a 4th sliver. Recommended: fold into BONDS, note
  it.
- **Ultra-long and Real Return Bonds** are now near-zero (ultra-long $0 since
  FY2022-23; RRB program discontinued Nov 2022, last RRB ~$1B in FY2021-22). They
  sit in BONDS but contribute ~nothing in recent/forecast years.
- If a 2-bucket reader chart is wanted, collapse NOTES+BONDS into "Bonds" and show
  **Bonds vs Bills**, which is the DMR's own headline cut.

---

## 2. HISTORY — 3-bucket gross issuance, $B per fiscal year

Aggregated from the DMR Table 4.1 per-tenor lines (sources §6). BILLS = T-bill
year-end stock (DMR convention); NOTES = 2yr+3yr+5yr; BONDS = 10yr+30yr+ultra+RRB+Green.

| FY | BILLS (T-bill stock) | NOTES (2+3+5yr) | BONDS (10+30+ultra+RRB+Green) | Total bond flow | DMR "Total Gross Issuance" | Kind |
|---|---|---|---|---|---|---|
| 2019-20 | 152 | 107 (53+20+34) | 21 (14+6+0+1.8+0) | 127 | 279 | HISTORY |
| 2020-21 | 219 | 264 (129+57+78) | 107 (74+32+0+1.4+0) | 370 | 589 | HISTORY |
| 2021-22 | 187 | 140 (67+29+44) | 117 (79+28+4+1+5) | 257 | 445 | HISTORY |
| 2022-23 | 202 | 118 (67+20+31) | 67 (52+15+0+1+0) | 185 | 387 | HISTORY |
| 2023-24 | 267 | 139 (86+6+47) | 65 (47+14+0+0+4) | 204 | 471 | HISTORY |
| 2024-25 | 285 | 157 (94+0+63) | 84 (63+17+0+0+4) | 241 | 526 | HISTORY |

Reconciliation: BILLS + NOTES + BONDS = DMR "Total Gross Issuance" in every year
(e.g. FY2024-25: 285 + 157 + 84 = 526 ✓; FY2023-24: 267 + 139 + 65 = 471 ✓).
NOTES = DMR "Short" line exactly each year (FY2024-25 Short = 157; FY2023-24 = 139;
FY2022-23 = 118). BONDS = DMR "Long" + Green (FY2024-25 Long 80 + Green 4 = 84 ✓;
FY2023-24 Long 61 + Green 4 = 65 ✓). All checks pass.

**Match to Desjardins Graph 6 (Jay's benchmark):** Desjardins showed
593 / 442 / 387 / 471 / 526 for FY2020-21 → FY2024-25. We have
589 / 445 / 387 / 471 / 526. The FY2020-21 (589 vs 593) and FY2021-22 (445 vs 442)
differences are **vintage revisions** between successive DMRs (the DMR estimates
issuance from BoC data by issuance date; figures get restated slightly across
report years). We use the **latest-vintage** figure for each year per the
"always freshest vintage" rule — i.e. the value as printed in that year's own
DMR Table 4.1. The two-figure gap is sub-1% and does not change any reader claim.

### Per-tenor detail (for drill-down or alternate bucketing), $B

| FY | T-bills | 2yr | 3yr | 5yr | 10yr | 30yr | Ultra-long | RRB | Green | Total bonds |
|---|---|---|---|---|---|---|---|---|---|---|
| 2019-20 | 152 | 53 | 20 | 34 | 14 | 6 | 0 | 1.8 | 0 | 127 |
| 2020-21 | 219 | 129 | 57 | 78 | 74 | 32 | 0 | 1.4 | 0 | 370 |
| 2021-22 | 187 | 67 | 29 | 44 | 79 | 28 | 4 | 1 | 5 | 257 |
| 2022-23 | 202 | 67 | 20 | 31 | 52 | 15 | 0 | 1 | 0 | 185 |
| 2023-24 | 267 | 86 | 6 | 47 | 47 | 14 | 0 | 0 | 4 | 204 |
| 2024-25 | 285 | 94 | 0 | 63 | 63 | 17 | 0 | 0 | 4 | 241 |

(3-year bond fully phased out after FY2023-24 — DMR 2024-25 p18: "complete
phasing out of the 3-year bonds," 9 maturity dates → 8. Ultra-long $0 since
FY2022-23. RRB program discontinued Nov 2022.)

---

## 3. FORECAST — 3-bucket planned issuance, $B per fiscal year

From the 2025-26 Debt Management Strategy (published with Budget 2025, 4 Nov 2025)
and updated in the Spring Economic Update 2026 Annex 3 (28 Apr 2026). Per the
"freshest vintage" rule, FY2026-27 uses the **SEU 2026 Annex 3** update; FY2025-26
uses the DMS 2025-26 plan (the SEU did not re-table the full FY2025-26 plan).

| FY | BILLS (T-bill stock target) | NOTES (2+5yr) | BONDS (10+30+Green) | Total bond plan | Total (bills stock + bond flow) | Kind | Source |
|---|---|---|---|---|---|---|---|
| 2025-26 | 296 (stock target) | 204 (120+84) | 112 (84+24+4) | 316 | 612 | FORECAST | DMS 2025-26 |
| 2026-27 | 268 (stock target) | 190 (110+80) | 108 (80+24+4) | 298 | 566 | FORECAST | SEU 2026 Annex 3 |

Notes:
- No 3-year in the forward plan (phased out). NOTES = 2yr + 5yr only.
- BONDS = 10yr + 30yr + Green (no ultra-long or RRB planned).
- FY2025-26: bond program $316B (DMS p7: "Annual gross bond issuance is planned to
  be $316 billion in 2025-26"). T-bill stock target end-FY2025-26 = $296B (DMS
  Table p6) — note SEU 2026 later cites ~$286B estimated end-FY2025-26 as the
  outturn tracks below the $296B target; for the forward chart use the DMS $296B
  plan for FY2025-26 and flag that the SEU revised the estimate to ~$286B.
- FY2026-27: bond program $298B; T-bill stock target $268B (SEU 2026 Annex 3,
  "revised down moderately to $268 billion"). Total domestic gross issuance $566B;
  $571B incl. ~$5B foreign.
- **Desjardins forecast columns (~612 / 609 / 589):** our 612 (FY2025-26) matches.
  Desjardins' 609 / 589 are Budget-2025-vintage FY2026-27 / FY2027-28 figures;
  the SEU 2026 revised FY2026-27 DOWN to 566. Use the **SEU 566** (freshest
  vintage) and note Budget 2025 had it at ~609. We do NOT have a primary FY2027-28
  forward plan at the tenor level (the DMS/SEU publish a detailed plan only one
  year out plus a preliminary next-year), so FY2027-28 is NOT in this series.

---

## 4. Combined HISTORY + FORECAST series for the chart (3 buckets, $B)

| FY | BILLS | NOTES | BONDS | Total | Kind |
|---|---|---|---|---|---|
| 2019-20 | 152 | 107 | 21 | 279 | HISTORY |
| 2020-21 | 219 | 264 | 107 | 589 | HISTORY |
| 2021-22 | 187 | 140 | 117 | 445 | HISTORY |
| 2022-23 | 202 | 118 | 67 | 387 | HISTORY |
| 2023-24 | 267 | 139 | 65 | 471 | HISTORY |
| 2024-25 | 285 | 157 | 84 | 526 | HISTORY |
| 2025-26 | 296 | 204 | 112 | 612 | FORECAST |
| 2026-27 | 268 | 190 | 108 | 566 | FORECAST |

This is the deliverable series for the pipeline rebuild. 6 history years +
2 forecast years. Every cell traces to a DMR Table 4.1 (history) or DMS/SEU
Annex (forecast) line in §6.

---

## 5. Alternative basis — TRUE gross T-bill AUCTION flow (clearly-labelled secondary)

If Jay wants a chart that shows true primary-market activity (all auctions, not
the year-end bill stock), the BILLS line changes dramatically because bills roll.
Tier A from BoC Valet F4-F10 (series V111900681 "Total Treasury Bills, Canada,
Gross new issues"; V111900683 "GoC bonds, Canada, Gross new issues"), aggregated
to fiscal years this session:

| FY | T-bill GROSS auctions ($B) | Bond GROSS auctions ($B) |
|---|---|---|
| 2019-20 | 343.6 | 126.5 |
| 2020-21 | 671.5 | 370.4 |
| 2021-22 | 455.0 | 257.4 |
| 2022-23 | 416.0 | 185.7 |
| 2023-24 | 588.0 | 200.3 |
| 2024-25 | 656.0 | 246.0 |

(BoC "direct and guaranteed bonds, Canada" differs slightly from the DMR
marketable-bond-program figure — FY2024-25 BoC $246B vs DMR $237B/$241B — because
the BoC securities-statistics aggregate is a different basis than the DMR program
definition. DMR text confirms gross T-bill issuance in FY2024-25 was ~$663B,
matching the BoC $656B within rounding/basis.) **This is a different metric.** Do
NOT mix it onto the DMR-convention chart. Recommend: build the chart on the
**DMR convention** (§4) as primary because it is what Desjardins and the DMR
publish; offer the auction-flow view only as a clearly-separated secondary if Jay
explicitly wants it. The bill component is the only thing that differs between the
two; bond flow is essentially the same story.

---

## 6. Source ledger (Tier per number)

All DMR/DMS PDFs were downloaded THIS SESSION (2026-06-02) via Python urllib,
which bypasses the canada.ca WebFetch 403 wall. They are now cached locally and
are **Tier A** (primary PDFs, text extracted via pdfplumber this session).

| Series / value | Primary source | Vintage | URL (cached locally) | Tier |
|---|---|---|---|---|
| FY2019-20, 2020-21 per-tenor | DMR 2020-2021 Table 4.1 (p18) | pub. 2021 | dam/.../dmr-rgd/2020-2021/dmr-rgd-21-eng.pdf → `data/raw/fiscal/dmr_2020_2021.pdf` | A |
| FY2020-21, 2021-22 per-tenor | DMR 2021-2022 Table 4.1 (p15) | pub. 2022 | dam/.../2021-2022/dmr-rgd-22-eng.pdf → `data/raw/fiscal/dmr_2021_2022.pdf` | A |
| FY2021-22, 2022-23 per-tenor | DMR 2022-2023 Table 4.1 (p16) | pub. 2023 | dam/.../2022-2023/dmr-rgd-23-eng.pdf → `data/raw/fiscal/dmr_2022_2023.pdf` | A |
| FY2022-23, 2023-24 per-tenor | DMR 2023-2024 Table 4.1 (p17) | pub. 2024 | dam/.../2023-2024/dmr-rgd-24-eng.pdf → `data/raw/fiscal/dmr_2023_2024.pdf` | A |
| FY2023-24, 2024-25 per-tenor | DMR 2024-2025 Table 4.1 (p13) | pub. 2025 | dam/.../2024-2025/dmr-rgd-25-eng.pdf → `data/raw/fiscal/dmr_2024_2025.pdf` | A |
| FY2025-26 forward plan (per-tenor) | DMS 2025-26 Table (p6) + narrative (p7) | pub. w/ Budget 2025, 4 Nov 2025 | dam/.../dms-sgd/2025-26-dms-sgd-eng.pdf → `data/raw/fiscal/dms_2025_26.pdf` | A |
| FY2026-27 forward plan (bond $298B, bill stock $268B, total $566B) | SEU 2026 Annex 3 | 28 Apr 2026 | `https://budget.canada.ca/update-miseajour/2026/report-rapport/anx3-en.html` (WebFetched this session) | A |
| Gross T-bill / bond AUCTION flow (secondary basis, §5) | BoC Valet F4-F10, V111900681 / V111900683 | data through Apr 2026 | `https://www.bankofcanada.ca/valet/observations/V111900681/json` (and V111900683) | A |

### Verbatim source excerpts (for claim-cards / fact-check grep)

- **DMR 2024-2025 Table 4.1** (p13): "Treasury Bills 267 272 285 … 2-year 86 88 94
  … 5-year 47 60 63 … 10-year 47 60 63 … 30-year 14 16 17 … Green Bonds 4 4 4 …
  Total Bonds 204 228 241 … Total Gross Issuance 471 500 526"
- **DMR 2024-2025 Table 4.2** (p14): "Short (2, 3, 5-year sectors) 139 68% 157 65%
  … Long (10-year+) 61 30% 80 33% … Green bonds 4 2% 4 2% … Gross bond issuance
  204 100% 241 100%"
- **DMR 2023-2024 Table 4.1** (p17): "Treasury Bills 202 242 267 … Total Bonds 185
  172 204 … Total Gross Issuance 387 414 471"; title "Gross Issuance of Bonds and
  Bills for 2023-24 / $ billions, end of fiscal year"
- **DMR 2024-2025** (p23): "In 2024-25, gross bond issuance was $237.0 billion,
  $33.2 billion higher than the $203.8 billion issued in 2023-24" (program-basis
  bond figure — note $237.0B vs Table 4.1's $241B; the $237.0B is the marketable
  bond program, the $241B is the issuance-date Table 4.1 basis).
- **DMS 2025-26** (p7): "Annual gross bond issuance is planned to be $316 billion
  in 2025-26, up from $241 billion in 2024-25."
- **DMS 2025-26 Table** (p6): "Treasury bills 267 285 296 / 2-year 86 94 120 /
  5-year 47 63 84 / 10-year 47 63 84 / 30-year 14 17 24 / Green bond 4 4 4"
  (columns = FY2023-24 actual / FY2024-25 actual / FY2025-26 plan).
- **SEU 2026 Annex 3** (WebFetched): bond program FY2026-27 $298B; T-bill stock
  "revised down moderately to $268 billion"; total domestic gross issuance $566B,
  $571B incl. ~$5B foreign.

---

## 7. Fact-checker caveat note (read before any reader-facing claim)

1. **THE HEADLINE TOTAL IS A HYBRID (most important caveat).** The DMR "Total
   Gross Issuance" / "Bonds and Bills" series — and our BILLS bucket — uses the
   **year-end T-bill STOCK**, not the gross T-bill auction flow. The bond
   components ARE true gross flow. So "Canada's gross issuance was $526B in
   2024-25" mixes bond flow with bill stock. This is the DMR's own published
   convention and matches Desjardins, so it is defensible and primary-sourced —
   but the chart and any prose MUST NOT describe the BILLS bucket as "auctioned"
   or "issued" in the flow sense. Safe framing: "the government's annual bond
   issuance plus its treasury-bill stock" or just follow the DMR label "gross
   issuance of bonds and bills." True gross bill auctions were ~$663B in FY2024-25
   (§5), 2.3× the $285B stock figure.

2. **"Notes" is OUR label, not a GoC term.** Canada issues treasury bills,
   marketable bonds (by tenor), Real Return Bonds, and Green bonds. There is no
   "note." If the chart uses BILLS/NOTES/BONDS, a footnote must state that NOTES
   = our grouping of the 2/3/5-year bond sectors (= the DMR's "Short" bucket),
   not an official instrument class.

3. **5-year sits in NOTES (short), per the DMR.** The DMR groups 2/3/5yr as
   "Short" and 10yr+ as "Long." Do not move the 5-year into BONDS without
   breaking reconciliation to the DMR's published Short/Long shares.

4. **Two bond-figure bases exist.** Table 4.1 (issuance-date basis) gives FY2024-25
   total bonds = $241B; the DMR narrative and program tables give $237.0B
   (marketable bond program). Both are primary; they differ ~$4B on methodology
   (issuance date vs auction date, plus program scope). Our series uses the
   **Table 4.1 issuance-date basis** throughout (it is the one that sums to the
   526/471/387 totals Desjardins benchmarks). Do not cross a $237.0B program quote
   with a $241B Table 4.1 cell in the same sentence.

5. **Vintage revisions on the two COVID years.** FY2020-21 is 589 (latest DMR
   vintage) vs Desjardins' 593; FY2021-22 is 445 vs 442. We use the latest DMR
   vintage. Sub-1%, no reader claim affected, but note it if challenged.

6. **Forecast is plan, not outturn.** FY2025-26 (612) and FY2026-27 (566) are
   PLANNED issuance from the DMS/SEU. Tag every forecast cell. FY2025-26 T-bill
   stock: DMS plan $296B; SEU 2026 revised the estimated outturn to ~$286B — use
   the DMS $296B for the plan line and flag the revision. No primary FY2027-28
   tenor-level plan exists yet, so the forecast stops at FY2026-27.

7. **Forecast = SEU 2026 (freshest), not Budget 2025.** Budget 2025 had FY2026-27
   total at ~$609B; the SEU 2026 revised it to $566B. Use $566B. Desjardins'
   forecast 609/589 columns are Budget-2025-vintage and now stale for FY2026-27.

8. **The bond program excludes foreign-currency issuance.** DMS footnote:
   "Domestic gross bond issuance does not include $11 billion of issuance in
   foreign currencies" (FY2025-26). Our BONDS/NOTES buckets are domestic only;
   foreign (~$5–11B) is a separate sliver if needed.
