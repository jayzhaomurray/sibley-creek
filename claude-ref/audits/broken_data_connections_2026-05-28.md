# Broken data connections audit -- 2026-05-28

## Summary

- Total issues found: 14
- Blocker (renders broken on live site): 2
- Important (drift / silent stale): 5
- Minor (orphans / unused outputs): 7

Build: clean (0 errors, 0 warnings). TK guardrail: clean. Slug alignment: clean.
Source audit: 10 length-budget soft-target warnings (editorial, not data-connection issues).
Two sections render "DATA NOT YET WIRED" in the live build: /housing/ plate-3 and /markets/ plate-3.

---

## Issues -- by severity

### BLOCKER

#### Issue 1: Housing plate-3 (sales composite) renders DATA NOT YET WIRED
- **Location:** `src/pages/housing.astro:36-37`, `data/site/panel_data/housing.json` panel-3, `src/components/charts/housing/Panel3SalesComposite.astro:161`
- **What's broken:** `Panel3SalesComposite` requires both `data.primary` (crea_snlr, present) and `data.secondary` (crea_resales, the resale-sales index). Housing `panel-3` has `secondary: null` in the committed JSON. The guard at line 161 of Panel3SalesComposite is `const hasData = salesAllRaw.length > 0 && snlrAllRaw.length > 0;` -- with secondary null, `salesAllRaw` is empty and the chart falls to PanelEmpty.
- **Why it's a blocker:** The live /housing/ page renders "DATA NOT YET WIRED" for plate-3 (inventory/absorption). Confirmed in `dist/housing/index.html`.
- **Root cause:** `data/raw/crea_resales.csv` exists locally (146 rows, last: 2026-02-01) and is gitignored. The committed `housing.json` was built at a time when `build_all_panel_data` ran before `crea_resales.csv` was fetched or before the fetcher populated it. The local build has the data; CI and the deployed artifact do not.
- **Fix:** Force-track `data/raw/crea_resales.csv` in git (same pattern as `data/raw/overnight_rate.csv` and `data/raw/fed_funds.csv`), then re-run `python -m pipeline.io.panel_data` to regenerate `housing.json`, then commit. Alternatively: move the series from `data/raw` into `data/site/panel_data` directly as part of the panel-data build (the canonical approach for any series that has a live chart against it).

#### Issue 2: Markets plate-3 (TSX equities) renders DATA NOT YET WIRED
- **Location:** `src/pages/markets.astro:23`, `data/site/panel_data/markets.json` panel-2, `src/components/charts/markets/Panel2Equities.astro`
- **What's broken:** `markets.json` panel-2 has `primary: null, secondary: null`. `pickPanel(panelDataFile, 2)` returns null because `primary.data` is absent. The plate passes null to `Panel2Equities`, which renders PanelEmpty.
- **Why it's a blocker:** The live /markets/ page renders "DATA NOT YET WIRED" for plate-3 (S&P/TSX). Confirmed in `dist/markets/index.html`.
- **Root cause:** Same pattern as Issue 1. `data/raw/tsx_composite.csv` exists locally (2508 rows, last: 2026-05-19) but is gitignored. The comment in `build_financial.py` at line 430 even documents the prior "2026-05-22 TSX TK incident" -- this is a recurrence. The fix was implemented in the orchestrator (`build_financial.py` now calls `build_site_data` + `build_all_panel_data` at lines 436-439) but the current committed `markets.json` predates that fix running successfully.
- **Fix:** Run `python -m pipeline.build_financial` locally (will re-fetch and regenerate), then commit updated `data/site/panel_data/markets.json`. Long-term: force-track `data/raw/tsx_composite.csv` in git so CI can build the panel_data independently. This series has a live chart; it must be tracked.

---

### IMPORTANT

#### Issue 3: monetary.astro plate-3 uses pickPanel(panelDataFile, 3) but monetary.json has no panel-3
- **Location:** `src/pages/monetary.astro:29`, `data/site/panel_data/monetary.json`
- **What's broken:** `const panel3Data = pickPanel(panelDataFile, 3);` returns null because `monetary.json` has panels: `[panel-1, panel-2, panel-4, panel-5, panel-6, panel-7-alt]` -- no panel-3. `panel3Data` is null.
- **Why it matters:** `panel3Data` is assigned to plate-3 (market path, `chartKey: "policy-panel-2"`). `pickPanel` returns null, so the plate's `data` prop is null. `PolicyPanel2MarketPath` receives null -- whether it renders empty or partially depends on the component's internal guard. Build does not fail; user sees broken or empty chart.
- **Verification needed:** Read `PolicyPanel2MarketPath.astro` to confirm its null guard behavior. `panel2Data` (yield_2yr, panel-2) is correctly wired to plate-3, so this may be a dead variable (panel3Data never used). Confirm by re-reading monetary.astro carefully -- plate-3 `data: panel2Data`, not `panel3Data`. If panel3Data is never assigned to a plate, this is a dead variable with no user-facing impact. **Needs one-line verify.**
- **Fix if confirmed unused:** Delete `const panel3Data = pickPanel(panelDataFile, 3);` from monetary.astro. If it IS assigned to a plate, either add panel-3 to the monetary pipeline spec or rewire the plate to use the correct panel.

#### Issue 4: output.astro fetches panel6Data but assigns it to no plate
- **Location:** `src/pages/output.astro:55`
- **What's broken:** `const panel6Data = pickPanel(panelDataFile, 6);` is declared. The plates array defines only plates 1-5. `panel6Data` is a dead variable -- the fetch runs but the result is discarded.
- **Why it matters:** Silent drift indicator. If a plate for panel-6 (gdp_industry_manufacturing) was planned but never wired, the output page is silently incomplete. The chart component and plate copy may exist elsewhere (e.g., chart-alternatives) but the GDP section doesn't render it.
- **Fix:** Either: (a) add plate-6 to output.astro if the manufacturing panel has a live chart component, or (b) delete the dead variable. Editorial call on whether this plate should ship.

#### Issue 5: policy.json is a fully orphaned panel_data file -- identical schema to monetary.json
- **Location:** `data/site/panel_data/policy.json`
- **What's broken:** No page in `src/pages/` imports `panel_data/policy.json`. Identical panel key structure to `monetary.json` (same six keys). This is the vestige of the /policy/ -> /monetary/ slug rename. The pipeline still builds and commits two identical JSON files.
- **Why it matters:** Two sources of truth for the same data. If someone updates the monetary pipeline spec and regenerates, `monetary.json` updates but `policy.json` does not (or vice versa), creating invisible drift. Also burns CI build time.
- **Fix:** Remove `policy.json` from `pipeline/io/panel_data.py` PanelSpec list (find the `section="policy"` block and delete it). Delete `data/site/panel_data/policy.json` from git. Verify no other file references it.

#### Issue 6: trade.astro uses raw dict lookup (not pickPanel) for panel-9 and panel-7-alt -- bypasses the empty-data guard
- **Location:** `src/pages/trade.astro:23-26`
- **What's broken:** `plate3Data = panelsById["panel-9"] ?? null` and `plate4Data = panelsById["panel-7-alt"] ?? null` bypass `pickPanel`. `pickPanel` guards: returns null if primary.data is empty. The raw dict lookup returns the panel object regardless of whether data is populated. If either panel has an empty `data` array, the chart component receives a non-null but data-empty panel and may render broken axes or an empty chart without the "DATA NOT YET WIRED" guard.
- **Why it matters:** These charts currently have data (verified: panel-9 primary data len=240, panel-7-alt primary data len=240) so this is latent. On any future fetch failure or regeneration where data is empty, the failure mode will be invisible -- no DNYW state, no loud error.
- **Fix:** Replace the raw lookups with `pickPanel(panelDataFile, 9)` and a named-key variant of pickPanel for `panel-7-alt`. Either extend pickPanel to accept a string key, or add a `pickPanelByKey` helper in `panelData.ts`.

---

### MINOR

#### Issue 7: housing.json panel-4 (cpi_rent_yoy) and panel-5 (mortgage_rate_5yr) are orphaned pipeline outputs
- **Location:** `data/site/panel_data/housing.json`, `pipeline/io/panel_data.py` (housing panel-4, panel-5 specs)
- **What's broken:** Both panels are built and committed but no plate in `housing.astro` references them.
- **Fix:** Either wire them to new plates (rent and mortgage-rate plates for the housing section) or remove their PanelSpec entries from `panel_data.py`.

#### Issue 8: inflation.json panel-6 (usdcad_yoy) is an orphaned pipeline output
- **Location:** `data/site/panel_data/inflation.json` panel-6
- **What's broken:** `inflation.astro` defines plates 1-5; panel-6 (usdcad_yoy) is built but never rendered.
- **Fix:** Remove the PanelSpec from the inflation section in `panel_data.py` or wire to a pass-through plate if the series is legitimately part of inflation context.

#### Issue 9: labour.json panel-5 (pop_immigrants) and panel-7 (ei_regular_beneficiaries) are orphaned
- **Location:** `data/site/panel_data/labour.json` panel-5, panel-7
- **What's broken:** `labour.astro` uses panels 1, 2, 3, 4, 6, 8. Panels 5 and 7 are built but not rendered.
- **Fix:** Either wire to plates or remove PanelSpecs. Panel-7 (EI beneficiaries) is a high-value labour indicator that arguably belongs on the section page.

#### Issue 10: markets.json panels 4, 5, 7, 8 are orphaned
- **Location:** `data/site/panel_data/markets.json` panel-4 (yield_2yr duplicate), panel-5 (yield_10yr duplicate), panel-7 (boc_settlement_balances), panel-8 (yield_10yr)
- **What's broken:** `markets.astro` uses panels 1, 2 (DNYW), 3, 6. Four panels are built but never rendered.
- **Fix:** Audit which of these were meant for future plates (boc_settlement_balances at panel-7 seems intentional for a monetary-conditions plate) vs legacy from a prior design. Remove those not on the roadmap.

#### Issue 11: trade.json panels 1, 2, 4, 5, 6, 9-alt are orphaned
- **Location:** `data/site/panel_data/trade.json`
- **What's broken:** trade.astro uses panels 3, 7-alt, 8, 9. Six other panels in the JSON (trade balance, current account, terms of trade, FDI, aluminum destinations alt) are built but not rendered.
- **Fix:** Same as above -- audit roadmap vs legacy, remove unneeded PanelSpecs.

#### Issue 12: output.astro panel6Data is a dead variable (see Issue 4 -- listed here as minor if editorial confirms no plate 6 planned)
- **Location:** `src/pages/output.astro:55`
- **Fix:** Delete `const panel6Data = pickPanel(panelDataFile, 6);` once editorial confirms panel-6 (manufacturing index) is not being added to the GDP section.

#### Issue 13: inflation-panel-0 registered in chartRegistry with null component
- **Location:** `src/layouts/SectionLayout.astro:129`
- **What's broken:** `"inflation-panel-0": null` is a registry entry that maps to no component. Any plate that accidentally uses this chartKey would silently render nothing (the registry lookup returns null, the component is not rendered, no error). Currently no plate uses it. It's a maintenance hazard.
- **Fix:** Remove the entry from chartRegistry and from the ChartKey union type. If it was reserved for a future plate, add a comment outside the registry.

#### Issue 14: Source-audit length-budget soft-target violations (10 items)
- **Location:** Various section plates (see source_audit.mjs output)
- **What's broken:** Not data connections -- editorial length issues. Labour plate-6 title (16W vs 6-14W target), output plate-4 and plate-5 titles (16W, 17W), monetary and output section abstracts (4-5 sentences vs 2-3 target), housing plate-1 blurb (81W vs 40-70W target), splash hero abstract (4 sentences).
- **Why noted here:** Source audit runs as a build step and generates warnings. None are hard-cap failures. Surface for editorial review separately.

---

## Prevention plan

### Build-time gates (catch at build, fail loud)

- **"Committed panel_data null primary" gate:** Add a `scripts/check_panel_data_wired.mjs` script that reads every `data/site/panel_data/*.json`, iterates panels that have `expectedStatus: "WIRED"`, and fails if `primary` is null. Wire into `npm run build` before the Astro build. This would have caught Issues 1 and 2 at commit time.

- **"pickPanel vs raw dict" lint rule:** Add an ESLint rule (or a simple grep in CI) that flags `panelsById["panel-N"]` raw lookups in section pages. All panel access should go through `pickPanel` or an equivalent null-safe helper. This closes the gap in Issue 6.

- **"Dead variable panel fetch" lint rule:** Add a check (could be the same script as above) that cross-references every `const panelNData = pickPanel(...)` declaration against the plates array in the same file. Dead variables (fetched but not assigned to a plate) produce a build warning. Catches Issues 4 and the future recurrence of Issue 12.

### Convention changes (make the failure mode harder to produce)

- **Force-track all series that have live chart components in git.** Current policy: `data/raw/` is gitignored, with explicit force-adds for series needed at build time (overnight_rate.csv, fed_funds.csv are tracked; crea_resales.csv and tsx_composite.csv are not). The rule should be: **any raw series whose slot is bound to a `expectedStatus: "WIRED"` PanelSpec must be force-added.** Add a section to `data/SOURCES.md` listing the tracked-raw-files set and why.

- **Consolidate policy.json into monetary.json in the pipeline.** Remove the `section="policy"` PanelSpec block entirely. The section was renamed; the duplicate build is a maintenance burden. The slug-alignment guardrail already enforces the rename on the frontend.

- **Standardize named-key panel access for non-numeric panel IDs.** `panel-7-alt`, `panel-9-alt` etc. cannot be accessed by number via `pickPanel(file, N)`. Add `pickPanelByKey(file: unknown, key: string): PanelData | null` to `panelData.ts` that wraps the same null-safety logic. Eliminate all raw `panelsById[key]` lookups in section pages.

### Tooling additions (small scripts that close gaps)

- **`scripts/check_panel_data_wired.mjs`:** Scans every `data/site/panel_data/*.json`. For each panel with `expectedStatus: "WIRED"`, asserts `primary !== null && primary.data.length > 0`. Fails build with section + panel ID + null series name. Runs before `astro build`.

- **`scripts/check_orphan_panels.mjs`:** Cross-references panel keys emitted by pipeline (`data/site/panel_data/*.json`) against panel keys actually consumed by section pages (statically parsed from `src/pages/*.astro`). Warns on orphan outputs. Catches Issues 7-11 going forward. Does not fail the build (orphans are a waste, not a user-facing break) but surfaces in CI logs.

- **`scripts/check_raw_tracked.mjs`:** Reads the `pipeline/io/panel_data.py` PanelSpec list, extracts all `SlotSpec("key", "raw", ...)` entries, maps to `data/raw/<key>.csv`, and for each that is not gitignored checks that it appears in `git ls-files`. Fails if a WIRED panel's raw CSV is untracked.

---

## Notes / open questions

1. **Issue 3 (monetary panel3Data)** needs a one-line read of monetary.astro to confirm `panel3Data` is truly a dead variable and not assigned to a plate. If it is dead, the fix is a one-line delete and there is no user-facing impact.

2. **Issues 7-11 (orphan panels)** need editorial direction on which orphan panels are roadmap-intended (e.g., labour panel-7 EI, housing panel-4 rent, markets panel-7 settlement balances) vs genuine legacy cleanup. Do not remove PanelSpecs without editorial sign-off on the plate plan.

3. **Issue 2 (TSX equities DNYW)** is a recurrence of the 2026-05-22 incident the `build_financial.py` comment documents. The orchestrator fix is already in place but the committed JSON predates the fix running. This should be fixed first (highest reader-visible impact on a live section).

4. **data/raw gitignore policy** is the root cause of Issues 1 and 2. The `data/raw/overnight_rate.csv` and `data/raw/fed_funds.csv` precedent (force-tracked) should be extended to every series backing a WIRED panel. The alternative -- rebuilding panel_data in CI -- requires Python dependencies in the CI environment, which is currently not set up for the Astro build step.
