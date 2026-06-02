# Provisional GoC yield overlay shadow plan

Date: 2026-06-02
Owner: Codex initial implementation; Claude should audit before live use.

## Problem

The daily markets and monetary panels can show incoherent as-of dates when
official Bank of Canada GoC benchmark yields lag other market sources. On
2026-06-02, BoC selected benchmark yields stopped at 2026-05-29 while USDCAD
and TSX had 2026-06-01 prints and oil could show 2026-06-02. The site must not
publish that as a coherent daily market read.

Jay's chosen compromise:

- keep Bank of Canada as canonical historical source;
- scrape a free public market page only for the newest missing GoC curve row;
- never write scraped values into `data/raw/yield_*.csv`;
- trial the approach in shadow mode before any live wiring.

## Safety architecture

1. BoC remains canonical history.
   - `data/raw/yield_2yr.csv`, `yield_5yr.csv`, `yield_10yr.csv`, and
     `yield_30yr.csv` remain BoC Valet only.
   - Provisional values must never be merged into those CSVs.

2. Scraped latest lives in a quarantine artifact.
   - Runtime artifact: `data/provisional/goc_yields_latest.json`.
   - It records source, source URL, fetch time, as-of date, values,
     validation status, and violations.

3. Shadow output is separate from live site output.
   - Shadow site bundle: `data/site_shadow/sections.json`.
   - Shadow panel bundle: `data/site_shadow/panel_data/*.json`.
   - The normal deploy path still reads `data/site/sections.json` and
     `data/site/panel_data/*.json`.

4. Overlay is in-memory only.
   - Panel and section builders can receive a series overlay map.
   - Overlay rows are appended only to the builder's in-memory dataframe.
   - On-disk canonical series are not modified.

5. Provisional curve must be complete.
   - Required maturities: 2y, 5y, 10y, 30y.
   - All values must share one as-of date.
   - Values must be finite and inside sane yield ranges.
   - A provisional value cannot be older than the official BoC row it would
     overlay.
   - Large moves versus the last official row fail closed until manually
     reviewed.

6. Replacement rule.
   - When BoC later publishes the same date, BoC wins.
   - A future reconciliation pass should compare provisional vs BoC and flag
     material differences, but the canonical history still remains BoC.

## Current source candidate

Trading Economics Canada bond pages expose a same-page curve table for Canada
2Y, 5Y, 10Y, and 30Y with date labels. This is suitable for shadow probing.
It is not an official historical source and must remain explicitly provisional.

## Implementation sequence

1. Add `pipeline/provisional/goc_yields.py`.
   - Fetch Trading Economics bond page.
   - Parse the Canada curve table from rendered text.
   - Validate complete same-date curve.
   - Write `data/provisional/goc_yields_latest.json`.

2. Add optional overlay support to `pipeline/io/site_data.py`.
   - Existing callers behave exactly as before.
   - Shadow caller can append provisional `yield_*` rows in memory.

3. Add optional overlay support to `pipeline/io/panel_data.py`.
   - Existing callers behave exactly as before.
   - Shadow caller can write panel JSONs under `data/site_shadow/panel_data`.

4. Add `pipeline/provisional/shadow_goc_yields.py`.
   - Load/validate provisional artifact.
   - Build `data/site_shadow/sections.json`.
   - Build `data/site_shadow/panel_data/*.json`.
   - Write a small comparison report.

5. Keep live feature flag off.
   - No `.github/workflows/*` live-use wiring in this stage.
   - No `USE_PROVISIONAL_GOC_YIELDS` live path until Jay approves shadow output
     and Claude audits.

## Claude audit target

Before live use, audit for:

- any path where scraped values can contaminate `data/raw/yield_*.csv`;
- mixed-date leakage in sections or panels;
- partial-curve acceptance;
- bad parser acceptance if the Trading Economics page layout changes;
- missing provenance or reader-visible ambiguity;
- whether the current validation threshold is too loose or too tight.
