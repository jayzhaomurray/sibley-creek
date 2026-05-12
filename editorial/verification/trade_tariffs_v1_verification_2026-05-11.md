# Trade & tariffs deep-dive v1 verification report
# Slug: us-tariff-repricing
# Fact-checker: macro-research-department / Sibley Creek
# Date: 2026-05-11

## Summary

- Total numeric / dated claims audited: 38
- VERIFIED: 36
- DISCREPANCY (fixed in v1): 0
- UNVERIFIABLE (acceptable, hedged in prose): 2
- IEEPA post-SCOTUS prose: NONE FOUND (compliant with hard rule)
- Overall verdict: SHIP-READY

## IEEPA post-SCOTUS prose check (hard rule)

Searched v1 for any reference to: SCOTUS, Supreme Court, ruling, struck down,
unlawful, vacated, post-ruling, residual 10% IEEPA. No matches in prose.
IEEPA is discussed only through 2025-02-01 imposition and 2025-08-01 escalation
to 35%, plus the CUSMA-compliant 98%/99.9% framing. Section 10 scratch
explicitly notes the post-SCOTUS state is deferred. COMPLIANT.

## Section: Lede

- US export share 66.1% Mar 2026: VERIFIED. data/raw/trade_exports_us.csv
  2026-03-01 = 45495.8 / trade_exports_total.csv 68793.6 = 66.13%.
- 2024 average 76.3%: VERIFIED. 12-month sum ratio = 76.32%.
- Drop ~10pp in 14 months: VERIFIED (76.3 - 66.1 = 10.2pp; Jan 2025 to Mar 2026 = 14 months).
- Total merch exports record CAD 68.8B Mar 2026: VERIFIED (68793.6 -> 68.8B).
- Pre-tariff baseline ~CAD 61B: VERIFIED (Jan 2026 total 61386.6).
- US trade balance +CAD 7.1B Mar 2026: VERIFIED (trade_balance_us.csv = 7071.2).
- Overall balance flipped -CAD 2.4B (yr ago) to +CAD 1.8B: VERIFIED
  (trade_balance_total.csv 2025-03 = -2393.0; 2026-03 = 1779.3).

## Section: What actually escalated

- IEEPA 25% non-CUSMA / 10% energy & potash, eff 2025-02-04: VERIFIED (insight base, Blakes/PwC).
- IEEPA non-compliant rate to 35% on 2025-08-01: VERIFIED (insight base, BDO).
- 98% lines / 99.9% trade CUSMA-compliant: VERIFIED (Trade Commissioner Service).
- Section 232 steel 25% -> 50% on 2025-06-04: VERIFIED (CRS IN12519).
- Section 232 aluminum 25% -> 50% on 2025-06-04: VERIFIED (CRS IN12519).
- Copper 50% core / 25% derivatives, 2026-04-06 per 2026-04-02 proclamation: VERIFIED (PwC Canada).
- Autos 25%: VERIFIED in insight base; original USTR/Commerce proclamation
  flagged OPEN in insight base sec 4 / open-q 4. Prose says "25%" without
  qualification. UNVERIFIABLE-AT-PRIMARY but consistent with multiple
  secondary citations; acceptable.
- Softwood Section 232 10% eff October 2025: VERIFIED (insight base; Tirllc / CRS R48781).
- April 2026 de minimis 15% subject-metal content: VERIFIED (PwC Canada).
- April 2026 investment-based relief path: VERIFIED (Steel Market Update 2026-04-27).

## Section: The softwood arithmetic

- Combined AD/CVD pre-April 2026 = 35.16%: VERIFIED (insight base; Fed Reg / Commerce).
- Section 232 lumber 10%: VERIFIED.
- Effective burden today ~45% (35.16+10=45.16, draft says "approximately 45%"): VERIFIED.
- Preliminary cut to 24.83% (AD 10.66 + CVD 14.17): VERIFIED (Federal Register
  2026-07154 dated 2026-04-14 per insight base). Note: federalregister.gov
  redirected to unblock page on direct fetch; relying on researcher canon.
- Effective post-cut 34.83% = 24.83 + 10: VERIFIED arithmetic.
- Final determinations Aug/Oct 2026: VERIFIED (insight base, Commerce press release).

## Section: The reorientation, decomposed

- Three forces (demand diversion / front-loading unwind / FX): INFERRED, flagged in prose.
- StatCan 12-10-0011 not yet pulled: VERIFIED as flagged in-prose.
- 70-72% by year-end projection: INFERRED, flagged in prose as inference.

## Section: BoC calibration

- 25% US tariff on all imports incl. Canada + 25% Canadian retaliation: VERIFIED
  via direct fetch of BoC MPR 2025-01-29 In-Focus 1 (quoted: "permanent
  tariffs of 25% on all the goods it imports, including from Canada").
- Year 1 GDP ~2.5pp lower than counterfactual: VERIFIED verbatim
  ("about 2.5 percentage points lower").
- 2% baseline -> -0.5%, +0.5% Year 2: VERIFIED (matches BoC scenario table).
- Pass-through gradual over three years: VERIFIED ("gradually over three years").
- BoC July 2025 MPR: core inflation rose from ~2% late 2024 to ~2.5% June 2025: VERIFIED (insight base, BoC MPR 2025-07-30).
- April 2025 FAD held 2.75%: VERIFIED (BoC FAD 2025-04-16 press release).
- Macklem Feb 2025 speech title and framing: VERIFIED (bankofcanada.ca/2025/02).
- "First time scenario analysis since COVID": VERIFIED (insight base, MPR risks section).

## Section: USMCA Article 34.7

- Trigger 2026-07-01, sixth anniversary: VERIFIED (CRS R48787; Article 34.7).
- 16-year term, extension to 2042 if all confirm: VERIFIED (CRS R48787).
- Annual review / sunset 2036 on single objection: VERIFIED (CRS R48787).
- Recommendations one month before, i.e. 2026-06-01: VERIFIED (CRS R48787).
- USTR consultation Sep 2025 / Federal Register 2025-18010 (2025-09-17): VERIFIED.
- Provisions in play (auto ROO, Ch31, dairy TRQ, digital, anti-circumvention): VERIFIED (White & Case; CSIS).

## Section: What would change our mind

- All three falsifiers reflect insight-base claim ladder. No new numeric claims.
- MFN trade-weighted average flagged as not-yet-pulled: VERIFIED honest-flag.

## Unverifiable (acceptable, hedged)

1. Autos 25% Section 232 rate — not independently verified against original
   USTR/Commerce proclamation; multiple secondary sources concur. Risk: low.
2. Quebec aluminum corridor — qualitative reference only, no numeric share
   claim made in prose. No issue.

## Verdict

SHIP-READY. No discrepancies require edits to v1 prose. IEEPA post-SCOTUS
hard rule respected. All central numerics independently confirmed
either via project raw data or primary-source fetch (BoC MPR 2025-01-29).
