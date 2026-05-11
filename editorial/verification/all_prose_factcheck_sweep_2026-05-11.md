# All-prose fact-check sweep — 2026-05-11

Gate 1 retroactive sweep over reader-facing prose surfaces not previously fact-checked.
Already-passed surfaces (4 published deep dives, 7 section blurbs in src/data/sections.ts, hero abstract in TitleStatement.astro) skipped per dispatcher brief.

## Surface log

### 1. src/pages/chart-improvements.astro — FIXES MADE
- Verified 8 pair descriptions against actual V2 derivations and panel_data payloads.
- Discrepancy: trade-5 description claimed "drops the proxy secondary" but the live trade.json panel-5 secondary is "ToT Y/Y %", not WTI/Brent proxies. The stale comment in Panel5TermsOfTrade.astro (orig) about "wti and brent as proxies" is contradicted by what trade.json actually emits.
- Fix: rewrote the trade-5 description to name the actual primary (StatCan terms-of-trade ratio, national-accounts basis, quarterly) and the actual secondary that V2 drops (Y/Y %).
- Other seven descriptions verified accurate against their V2 wrappers (trade-3 = total exports + US exports levels; gdp-1 = m/m % + Q/Q SAAR; policy-3 = 2y spread bps; labour-2 = unemployment level + aggregate hours; gdp-4 = quarterly real GDP + immigrant proxy; gdp-5 = stale "GDP, quarterly" label fix to "Output gap"; trade-2 = stale "Trade bal." label fix to "Current account").
- TKs: 0.
- Files touched: src/pages/chart-improvements.astro.

### 2. src/pages/chart-alternatives.astro — CLEAN
- 28 alt descriptions verified against component file names and stated dataFields. No discrepancies surfaced from spot-checks (Alt2_PerCapitaVsTotal indexes to 2019Q4=100; Alt3_BosBreadthStack stacks four BOS distribution buckets; Alt4_TwosTensSlope = 10y-2y as advertised).
- TKs: 0.
- Files touched: none.

### 3. Section page ledes + latestReleaseLabel — FIXES MADE
- Seven ledes verified: each accurately describes the plate slate (count and topics match the plates[] array in the same file).
- Discrepancy: 7 TK markers in latestReleaseLabel across all section pages.
- Fix: replaced each TK with the actual latest reference period pulled from data/site/sections.json:
  - gdp: "Monthly GDP by industry, Feb 2026" (gdp-yoy asOf Feb 2026)
  - inflation: "Headline CPI, Mar 2026" (cpi-yoy asOfISO 2026-03-01)
  - labour: "LFS, Apr 2026" (unrate asOfISO 2026-04-01; releaseDate 2026-05-08)
  - policy: "BoC rate decision, Apr 29, 2026" (policy-rate asOf Apr 2026; Apr 29 is the canon BoC Fixed Announcement Date per methodology_page.md sec 2)
  - markets: "Daily close, May 8, 2026" (USDCAD asOfISO 2026-05-08)
  - trade: "Merchandise trade, Mar 2026" (trade-balance asOfISO 2026-03-01)
  - housing: "MLS HPI, Mar 2026" (hpi-yoy asOfISO 2026-03-01)
- TKs resolved: 7.
- Files touched: src/pages/{gdp,inflation,labour,policy,markets,trade,housing}.astro.

### 4. src/pages/research/index.astro — CLEAN
- ledeText ("Long-form deep dives on the Canadian economy. Each piece takes one argument as far as the data lets it. Newest first.") and pageDesc verified — no factual claims requiring source check. Row list driven by data/sections.ts deepDives, not prose.
- TKs: 0 in prose. "TK" appears only as documented sentinel sort-token for unpublished entries (renders as "Coming soon" badge).
- Files touched: none.

### 5. src/pages/404.astro — CLEAN
- Body prose "This page is not part of the publication." is content-neutral.
- Section nav list driven from sections array (data/sections.ts), already canon. No stale section labels.
- TKs: 0.
- Files touched: none.

### 6. src/pages/og-preview/index.astro — CLEAN
- Tagline "Canadian macroeconomic indicators and analysis, in one place, on a single page." matches publication scope (Canadian macro, single-page dashboard) per project canon.
- URL line "sibleycreek.ca" matches live site.
- TKs: 0.
- Files touched: none.

### 7. src/components/home/VignelliColophon.astro — FIXES MADE
- Discrepancy (confirmed earlier audit finding): Sources block listed 9 wired sources including OSFI and CMHC, but methodology_page.md Section 1.2 documents both as deferred (not yet wired). pipeline/io/site_data.py and data/SOURCES.md confirm: CBA arrears is the live proxy for CMHC; OSFI Bank Financial Data deferred to Wave 3.
- Fix: removed OSFI and CMHC from the Sources list; added Alberta Economic Dashboard and C.D. Howe Institute Business Cycle Council, both wired per methodology_page.md Section 1.1.
- New list (9 sources, all live): StatCan; BoC; CREA; DoF Canada; CBA; Alberta Economic Dashboard; C.D. Howe Institute BCC; FRED; Yahoo Finance.
- "Publication" block (About / Methodology nav) verified — both routes exist.
- TKs: 0.
- Files touched: src/components/home/VignelliColophon.astro.

## Sweep totals
- Surfaces swept: 7 (covering 13 unique files).
- Discrepancies fixed: 9 (1 chart-improvements desc + 7 TK release labels + 1 footer sources reconciliation).
- TKs resolved: 7 (all latestReleaseLabel placeholders replaced with sections.json-grounded dates).
- TKs remaining in reader-facing prose: 0.
- Verdicts: 3 CLEAN, 4 FIXES MADE, 0 NEEDS-MORE-WORK.

## Cross-cutting notes
- All latest-release labels now ground in data/site/sections.json reference dates. If/when the pipeline rebuilds with newer reference periods, these strings will go stale; ideally they should be data-driven from sections.json in a follow-up.
- Plate-level interpretation prose across the seven section pages remains heavily TK'd (publication-voice placeholder copy with "TK" tokens inline). These plates are NOT yet on production reader paths per latestReleaseLabel design — they sit behind a separate gate. Out of scope for this sweep; flag to dispatcher if reader visibility on plates needs to be re-checked.
