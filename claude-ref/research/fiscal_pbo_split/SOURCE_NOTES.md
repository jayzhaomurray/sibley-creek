# Fiscal PBO-split plate -- source notes for the chart-ready data

Researcher deliverable. Compiled 2026-06-04. Feeds a new federal-fiscal chart
plate on the DoF-vs-PBO operating/capital classification dispute. Companion to:
- `operating_balance_dof_vs_pbo.csv` (year-by-year operating-balance series)
- `capital_reclassification_totals.csv` (the $94bn wedge)

Builds on already-verified base (do NOT re-verify these from scratch):
- `editorial/source_cards/_pending/fiscal/pbo_operating_capital_reclassification_nov_2025.yaml` (Tier A)
- `editorial/source_cards/_pending/fiscal/dof_operating_balance_projection.yaml` (Tier A)
- `data/derived/fiscal_operating_capital.json`, `data/derived/fiscal_dof_operating_balance.json`
- `claude-ref/research/fiscal_redo/source_and_series.md` Indicator 1

## THE CRITICAL CAVEAT -- read before building the chart (vintage mismatch)

The two operating-balance series are NOT on the same vintage and are NOT a clean
year-by-year delta:

- **DoF operating balance** = Spring Economic Update 2026, Annex 1, Table A1.5
  (tabled 28 Apr 2026). FY2025-26 -> FY2030-31. This is the FRESHER DoF vintage.
- **PBO recast operating balance** = PBO "Budget 2025: Issues for Parliamentarians,"
  RP-2526-017-S (14 Nov 2025). FY2024-25 -> FY2029-30. PBO recast **Budget 2025**
  (Nov 2025), NOT the SEU 2026.

PBO did publish a set of SEU 2026 assessments (NT-2627-001-S economic/fiscal track,
NT-2627-002-S fiscal anchors/sustainability, NT-2627-003-S capital priorities), but
**none of them republishes a year-by-year SEU operating-balance recast**. NT-2627-002-S
addresses debt-to-GDP, long-run sustainability, and the interest burden (10.6% ->
13.2% of revenues by 2030-31) -- not an operating-balance reclassification. So the
only published PBO year-by-year operating-balance recast is the Budget 2025 one.

**Consequence for the chart.** A naive overlay reads "DoF says +0.9 in 2028-29, PBO
says -18.1 in 2028-29" -- but those two numbers are from different DoF vintages
(SEU 2026 vs Budget 2025). The gap is therefore a COMPOUND of (a) the genuine
classification dispute AND (b) ~$11.5bn of better fiscal news DoF booked between
Budget 2025 and the SEU. Do not present the year-by-year vertical distance as if it
were purely the classification effect.

The cleanest honest framings, in order of preference:

1. **Carry the dispute on the $94bn cumulative wedge (vintage-clean), and show the
   DoF operating-balance line on its own fresh vintage with the anchor crossing.**
   The $94bn and the PBO recast operating deficits are BOTH from the single Budget
   2025 vintage -- internally consistent. The DoF SEU operating-balance line is the
   government's freshest stated track. Annotate the vintage seam explicitly.

2. **Hold BOTH operating-balance lines on the Budget 2025 vintage** for a true
   same-vintage head-to-head. BLOCKED: DoF's Budget-2025 year-by-year operating
   balance was never press-extractable (only the SEU 2026 A1.5 version is verified).
   Do NOT reconstruct it -- the operating balance is not a simple revenues-minus-
   expenses subtraction (see "A1.5 is not a naive subtraction" below). If a future
   human pull of Budget 2025 Annex 1 surfaces the A1.5-equivalent table, this becomes
   the preferred construction.

3. If the chart shows the PBO recast line against the DoF line, **label the PBO line
   explicitly as "PBO recast of Budget 2025" and the DoF line as "DoF, Spring Update
   2026,"** with a one-line note that the vintages differ. The editorial point --
   under PBO's definition the operating books never reach balance -- survives the
   vintage caveat, because PBO's recast operating deficit is still -17.6bn in
   2029-30 (its last year), nowhere near zero, while DoF reaches +0.9 by 2028-29.

## A1.5 is not a naive subtraction (why we cite the stated row, not a derivation)

The SEU A1.5 operating balance does NOT equal (budgetary revenues - day-to-day
operating expenses). Check 2025-26: 511.5 - 544.3 = -32.8, but the stated operating
balance is -26.4. The ~6.4 difference is the "capital investments (revenues)" line
(6.5 in 2025-26): DoF nets capital-related revenues back in. The published A1.5
operating-balance row is the authoritative figure. **Cite the stated row; do not
reconstruct it.** (This also means a writer cannot derive an alternative operating
balance from the revenue/expense rows without replicating DoF's exact netting.)

## What PBO says is misclassified as capital (verified categories)

From RP-2526-017-S, the categories PBO removes from Budget 2025's capital line and
returns to operating (per `fiscal_redo/source_and_series.md` Indicator 1, which
WebFetched the PBO publication 2026-06-02):
- **Corporate income-tax expenditures** (tax measures booked as capital support)
- **Investment tax credits**
- **Operating subsidies**

PBO applies a conventional / international capital definition (the source card notes
the IMF GFS 2014 standard) -- capital = spending that produces a durable public
asset, not tax expenditures or subsidies. NOTE: defence and housing are part of the
broader Build-Big envelope and appear in PBO's SEU capital-priorities assessment
(NT-2627-003-S), but the specific RECLASSIFIED-OUT categories the $94bn rests on are
the three above (corporate tax expenditures, ITCs, operating subsidies). Do NOT
assert "defence and housing reclassified" -- that is not what the $94bn figure is
built on. The verified misclassification categories are the tax-expenditure /
subsidy items.

PBO recommendation (same report): establish an independent expert body to determine
which spending qualifies as capital. (Useful editorial colour; attribute to PBO.)

## The editorial point survives the caveats

- DoF's own (freshest) track: operating balance crosses zero in **2028-29 (+0.9)**,
  exactly the fiscal-anchor year, and runs to +6.1 by 2030-31. The anchor is met
  ONLY under the government's own capital definition.
- PBO's recast (Budget 2025 vintage): operating deficit is **-18.1 in 2028-29 and
  -17.6 in 2029-30** -- never reaches balance over the published horizon.
- The wedge is ~**$94bn cumulative** over six years (~30% of the reported capital
  total), driven by tax expenditures / ITCs / operating subsidies PBO says are not
  genuine capital.

So the anchor "being met" is contingent on the classification the PBO disputes.
That contingency -- not a clean "DoF +0.9 vs PBO -18.1 in the same year" subtraction
-- is the verified, defensible take.

## Numbers the writer may cite (all primary-sourced)

| Claim | Value | Source |
|---|---|---|
| DoF operating balance, 2028-29 (anchor year) | +$0.9bn | SEU 2026 Annex 1 Table A1.5 |
| DoF operating balance, 2025-26 | -$26.4bn | SEU 2026 Annex 1 Table A1.5 |
| DoF operating balance, 2030-31 | +$6.1bn | SEU 2026 Annex 1 Table A1.5 |
| PBO recast operating deficit, 2028-29 | -$18.1bn | PBO RP-2526-017-S |
| PBO recast operating deficit, 2029-30 (last yr) | -$17.6bn | PBO RP-2526-017-S |
| Capital reclassification wedge (cumulative) | ~$94bn (~30%) | PBO RP-2526-017-S |
| DoF reported capital, 2024-25 to 2029-30 | $311.5bn | PBO RP-2526-017-S (reproduces Budget 2025) |
| PBO recast capital, 2024-25 to 2029-30 | $217.3bn | PBO RP-2526-017-S |
| Capital path endpoints (Budget 2025) | $32.2bn (24-25) -> $59.6bn (29-30) | PBO RP-2526-017-S |

## Verification status of THIS deliverable (honest)

- All values are carried from Tier-A source cards verified by direct WebFetch in
  prior sessions (24-25 May and 2 June 2026): PBO RP-2526-017-S HTML and SEU 2026
  Annex 1 HTML were both fetched and parsed then, with multi-secondary triangulation
  on the PBO side (PBO press release + thedeepdive + thehub + Investment Executive).
- I could NOT re-fetch the primaries in THIS session (WebFetch unavailable in the
  environment). No number here is newly invented; every figure traces to an existing
  Tier-A card or the fiscal_redo Indicator 1 working file. Before this plate ships,
  the fact-checker should re-confirm the two primaries are still live and unrevised
  (the SEU 2026 vintage will be superseded by Budget 2026 when it tables).
- $311.3bn vs $311.5bn: the fiscal_redo file reads $311.3bn from PBO's text; the
  source card and PBO press release read $311.5bn. The $94bn gap and ~30% hold under
  either. Use $311.5bn (the press-release figure) or round to ~$311bn.

---

## ADDENDUM 2026-06-04: PBO Economic and Fiscal Outlook - June 2026 (RP-2627-002-S)

Fetched by main Claude (dispatcher) 2026-06-04 from
https://www.pbo-dpb.ca/en/publications/RP-2627-002-S--economic-fiscal-outlook-june-2026--perspectives-economiques-financieres-juin-2026
(released 2026-06-04; cross-checked against Globe and Mail + BNN Bloomberg same-day coverage).

**Effect on this plate's sources:**
- The June 2026 EFO does NOT update the operating/capital recast. RP-2526-017-S
  (Nov 14, 2025) REMAINS the latest published PBO position on the classification
  dispute. PBO states an independent assessment of the government's operating-balance
  anchor will come in a future report. Freshest-vintage check: PASS as of 2026-06-04.
- DoF side: same-day coverage benchmarks PBO against the Spring Economic Update
  (April 28, 2026) — confirms SEU is still the latest DoF document (no Budget 2026
  supersession). Freshest-vintage check: PASS as of 2026-06-04.

**New citable numbers (supersede Sept 2025 EFO baseline):**
- 2025-26 budgetary deficit: $72.0bn (2.2% of GDP) vs DoF SEU $66.9bn
- Deficits average $4.6bn/yr above the SEU track over the projection horizon;
  drivers: lower personal income tax revenues + higher program expenses,
  partially offset by lower public debt charges
- Federal debt-to-GDP: 41.3% (2025-26) rising to 42.5% (2030-31)
- Federal debt level by 2030-31: $1.66T (vs SEU $1.629T)
- 2030-31 deficit: $58.2bn
- PDF: https://distribution-a617274656661637473.pbo-dpb.ca/2073136cc439c15f9cc5917e1db1ed23bef0aa72a4a8a1751a1c650913a5fa10

**Surfaces affected:** plate-4 (debt/GDP "trajectory is flat" needs DoF attribution
+ PBO 42.5% counterpoint) and the section blurb's "holds near 41%" clause.
Writer touch dispatched 2026-06-04; re-gates with the rest.

---

## ADDENDUM 2026-06-04 (evening): Budget 2025 AS-PRESENTED operating track (Table 4)

Fetched by main Claude from RP-2526-017-S PDF (pp. 6-7), same-vintage pair for the
plate-2 redesign (Jay-approved: "same books, two definitions"):

Table 4 — Day-to-day operating balance, $B, FY2024-25 -> 2029-30:
- Budget 2025 as presented:      -4.1, -33.0, -8.7, -5.5, +1.7, +3.0  (crosses zero FY2028-29)
- Same budget, PBO definition:   -10.5, -45.8, -25.3, -23.3, -18.1, -17.6  (never balances)
- Per-year gaps: 6.4, 12.8, 16.6, 17.8, 19.8, 20.6 -> cumulative 94.0 ~= the $94B wedge.
  The annotation is now the literal sum of visible pair-gaps. No vintage mismatch remains.

Table 3 cross-check: capital totals 311.6 (B2025) vs 217.4 (PBO defn) — matches card
values 311.5/217.3 within rounding.

PDF: https://distribution-a617274656661637473.pbo-dpb.ca/190ba7d3612031a7e15f5b45833a685e0e579add5a40fc0d2730ef043aeea0b1
Page URL: https://www.pbo-dpb.ca/en/publications/RP-2526-017-S--budget-2025-issues-parliamentarians--budget-2025-enjeux-parlementaires

VINTAGE NOTE: plate-2 now deliberately uses Budget 2025 (Nov 2025) for BOTH series —
the only same-vintage two-definition pair in existence. Freshest-vintage rule satisfied
per-claim: the CURRENT plan's operating track (SEU Apr 2026) lives on plate-1; the
definition dispute exists only in the Nov 2025 pair. Vintage drift between the two is
~$1.2bn/yr avg (NT-2627-002-S) vs a definitional gap of ~$15-20bn/yr.
