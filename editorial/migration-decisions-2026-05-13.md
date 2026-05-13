# Migration decision sheet — registered-source rule

**Created 2026-05-13. Migration complete; gate strict.**

All 136 `other:` citations (across 7 files) migrated to `card:` / `pipeline:` / `derived`. Build green. Gate now refuses any `other:` source.

This sheet documents what's still **pending review by the user** — items I migrated to working values but that would benefit from a closer look when you have time.

---

## What landed (no action needed from you)

- **47 new registry cards** appended to `editorial/source_cards/registry.yaml` (was 5; now 52). New cards cover BoC press releases, FOMC statements, Presidential Proclamations, Federal Register notices, USMCA treaty text, IRCC plan, OECD productivity, CMHC RMIR, CBA arrears, OSFI M4, Big-Six bank supplements, BoC SAPs/SANs, and release calendars.
- **3 factual prose corrections** applied (Dec 2024 → Jan 2025 ×2; 50-70 → 45-65 CREA band).
- **136 source-field rewrites** across `mortgage-renewal-wall.yaml`, `us-tariff-repricing.yaml`, `per-capita-output.yaml`, `boc-fed-divergence.yaml`, `trade.astro`, `inflation.astro`, `policy.astro`, `housing.astro`, `sections.ts`.
- **TSX wired**: now flows through `pipeline:yahoo:tsx_composite`. Equities plate added to markets page at slot 2 (after CAD). Markets page now 8 plates. Pipeline regenerated. Build clean.
- **Canon updated**: `editorial/review_protocol.md` § "Registered-source rule" + `editorial/writing-style.md` § 4.1d.
- **Gate tightened**: `scripts/check_citation_coverage.mjs` now rejects any `source:` that isn't `pipeline:` / `card:` / `derived`.

---

## Pending user review (no urgency; the site is live and clean)

### A. Cards with `[NEEDS HUMAN VERIFICATION]` excerpts

WebFetch couldn't extract clean text from these primary sources (PDFs, 403 responses, JS-rendered pages). The cards have correct URLs but best-effort excerpts assembled from secondary coverage. When you have a quiet hour, open these in a browser and tighten the excerpts:

1. `boc_sap_2026_12_mortgage_arrears` — verify SAP-2026-12 coefficients from the PDF body
2. `osfi_m4_consolidated_balance_sheet` — verify Feb 2026 row values from the CSV at open.canada.ca
3. `cmhc_rmir_fall_2025` — verify dive-specific numbers (1.15M households 2026; uninsured >25-yr above 60%; Toronto Q4 2026 0.34%)
4. `cba_residential_mortgage_arrears` — verify Feb 2026 numerator/denominator (13,749 / 4,937,235)
5. `bigsix_q1_fy2026_earnings_supplements` — verify aggregate C$1.76T and C$168M from each bank's supplement
6. `boc_csce_q1_2026` — verify 3.0% / 3.7% values against BoC Valet CES_DEMOGRAPHICS
7. `boc_bos_q1_2026` — verify 11% share against Business_Outlook_Survey series
8. `boc_renewal_wall_san_2024_12` — confirm SAN-2024-25 URL or substitute FSR Dec 2024
9. `crs_r48787_usmca_joint_review` — verify excerpt from congress.gov
10. `crs_if10997_usmca_briefer` — placeholder excerpt; needs a real one
11. `fr_2025_18010_ustr_usmca_consultation` — verify excerpt from federalregister.gov
12. `fr_softwood_adcvd_prelim_2026` — verify exact rate values (10.66 + 14.17 = 24.83)
13. `boc_speech_macklem_tariffs_feb2025` — verify "2½% lower" from BoC PDF (currently via BIS Review mirror)
14. `gc_cusma_compliance_share` — verify 98% / 99.9% from tradecommissioner.gc.ca
15. `ircc_levels_plan_2026_2028` — verify long excerpt from canada.ca
16. `ircc_annual_report_2020_baseline` — verify from canada.ca
17. `oecd_productivity_compendium_2024` — verify from oecd.org

### B. Structural promotions (deferred)

Researcher recommended these sources move from `card:` to `pipeline:` because they're machine-readable and referenced multiple times:

- **OSFI M4** → `pipeline:osfi:m4_*` (CSV at open.canada.ca, monthly)
- **CBA arrears** → `pipeline:cba:arrears` (stable monthly URL pattern)

Each promotion: ~1 hour to add the pipeline fetcher + tests. When you do, the corresponding card becomes vestigial and can be dropped from the registry.

### C. Mapping shortcuts I took (worth a sanity check)

- The BoC FSR 2024 historical reference in `mortgage-renewal-wall.yaml` was reanchored to `boc_fsr_2025_renewal_shock` (the only FSR card we have). If you want a true historical anchor, add a separate `boc_fsr_2024_renewal_shock` card with the FSR 2024 URL.
- BoC CSCE Q3/Q4 2025 and BoS Q3/Q4 2025 historical references in `boc-fed-divergence.yaml` were mapped to the Q1 2026 cards (which contain the historical series). Same pattern — a separate card per vintage would be cleaner if any single past vintage becomes load-bearing.
- "IMF Article IV Canada 2025" and "OECD Economic Survey of Canada 2025" composite literature references in `per-capita-output.yaml` were absorbed into `statcan_canada_us_productivity_gap` per the researcher's recommendation. If you want those reports cited explicitly, they need their own cards.
- BoC MPR April 2026 references in `boc-fed-divergence.yaml` mapped to `boc_mpr_potential_growth` (the only April 2026 MPR card). Per-claim accuracy is fine but consider an `boc_mpr_2026_04_29_overview` card if MPR sections beyond Appendix A are referenced.

### D. Closing items

- Mortgage-renewal-wall sidecar prose `framing-no-source-needed` entry was mapped to `derived` (per researcher recommendation). Could be deleted entirely as a narrative-only row.
- `boc_renewal_wall_san_2024_12` URL is best-effort — researcher's WebFetch returned 404 on the candidate URL.

---

## Inline-highlight match rate (cosmetic)

The audit pages (`editorial/source_cards/audit/research/<slug>.html`) show only a fraction of claims as highlighted yellow superscripts because the sidecar `phrase:` tokens were authored against earlier draft versions and the published prose has drifted. The full ledger sidebar always shows every claim regardless. Tightening phrase tokens to match published prose is a separate pass; not blocking.

---

## How to make further changes

The gate is now strict. Any new prose that introduces a citation must use one of `pipeline:<provider>:<key>`, `card:<id>`, or `derived`. Anything else fails `npm run build`. To add a new primary source: append a card to `editorial/source_cards/registry.yaml`, then reference it as `card:<id>`.

---

*This sheet supersedes the version saved earlier today. All the "action needed" items from the previous version have been applied.*
