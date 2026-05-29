# Build Gates: Wired-Panel Prevention Layer

Added 2026-05-28 after the broken-data-connections audit found /housing/ plate-3
and /markets/ plate-3 rendering "DATA NOT YET WIRED" on the live site. The root
cause was a class of failure: raw CSVs gitignored + committed panel_data JSONs
with null primary data. These gates prevent that class from recurring.

## Scripts

### check_panel_data_wired.mjs -- hard pre-build gate

**When it fires:** Before `astro build`, as part of `npm run build`.
**What it catches:** Any panel key referenced by a section page via `pickPanel()`
or `pickPanelByKey()` that resolves to a null or empty primary series in the
committed `data/site/panel_data/<section>.json`.
**Exit behavior:** Exit 1 with the section, page file, panel key, and reason.
Exit 0 silently if all referenced panels are wired.
**npm script:** `npm run audit:wired`

This is the primary guard against the class of failure described above. If it
fires, the fix is one of:
- Run the pipeline to regenerate panel_data (requires raw CSVs to be present)
- Force-track the missing raw CSV: `git add -f data/raw/<file>.csv`

### check_orphan_panels.mjs -- warning-only audit

**When it fires:** On demand. NOT wired into `npm run build`.
**What it catches:** Panel keys present in `data/site/panel_data/<section>.json`
that are NOT referenced by any section page. These are panels the pipeline builds
but no page renders.
**Exit behavior:** Always exits 0. Prints WARN lines for each orphan panel.
**npm script:** `npm run audit:orphans`

Useful for catching stale pipeline output after a page refactor, or for
identifying panels-in-progress that haven't been wired into a page yet. Does not
block CI; it is a maintainer inspection tool.

### check_raw_tracked.mjs -- hard pre-build gate

**When it fires:** Before `check_panel_data_wired`, as part of `npm run build`.
**What it catches:** Any disk-resident source file (raw CSV, processed CSV,
derived JSON) that backs a wired panel's `source_files` list but is NOT tracked
by git. This is the root-cause failure mode: a raw CSV added locally but never
force-tracked means CI cannot build the panel.
**Exit behavior:** Exit 1, listing each missing file, which panel needs it, and
the fix command (`git add -f <path>`). Exit 0 silently if all source files are
tracked.
**npm script:** `npm run audit:raw-tracked`

**How it works:** The pipeline emits a `source_files` field on each panel in
`data/site/panel_data/<section>.json` (added to `pipeline/io/panel_data.py`).
The field is a sorted list of project-root-relative paths
(e.g. `["data/raw/crea_resales.csv", "data/raw/crea_snlr.csv"]`). The script
reads that field for every wired panel and calls `git ls-files <path>` to
confirm tracking. Panels with no disk-resident files (empty `source_files`)
are skipped -- nothing to verify.

**Source classification:** `_resolve_slot_path()` walks the same tier-fallback
order as the slot reader (preferred tier first, then processed/derived/raw).
Labour-flow derived slots resolve to their three hardcoded raw input CSVs via
`LABOUR_FLOW_SOURCE_FILES`. BoC Valet, FRED, and IMF series that land on disk
as raw CSVs are captured automatically if the file exists. Slots not yet on
disk (un-wired panels) contribute nothing and do not cause false failures.

This gate closes the root-cause gap that `check_panel_data_wired.mjs` only
catches at the symptom layer (null primary data). If a new series is fetched
and its raw CSV is not force-tracked, this gate fails before the site ever
renders a broken panel.

## Convention: raw CSVs backing WIRED panels

Any raw series that backs a WIRED panel (a panel referenced by a section page)
must satisfy one of these two conditions:

  (a) The raw CSV is force-tracked in git: `git add -f data/raw/<file>.csv`
      This ensures CI has the data it needs to build the panel without running
      the full fetch pipeline.

  (b) The series is materialized directly into the committed panel_data JSON
      during the pipeline run. If panel_data is committed with non-null
      primary.data, CI does not need the raw CSV at all.

**This is an interim operational compromise.** The current CI environment does
not deterministically re-run the Python pipeline (fetch + build) on every deploy.
Because the pipeline is not idempotent in CI, raw CSVs must be committed as a
substitute for a live pipeline run.

The end state -- when CI can fetch from upstream sources and fully rebuild
panel_data reliably -- is that raw CSVs do NOT need to be committed. The pipeline
rebuilds them on each deploy. When that migration happens, remove the raw CSV
force-tracks from git and update this document.

## Access pattern: pickPanelByKey

`pickPanelByKey(panelDataFile, "panel-7-alt")` is the canonical access pattern
for panels whose keys are not plain numeric (i.e., keys that `pickPanel(N)` cannot
express). Raw `panelsById["panel-7-alt"]` lookups are banned because they bypass
the null-safety logic in the helper and silently pass a potentially-unwired panel
object into the chart component.

If you add a new panel with a non-numeric key to a section page, use
`pickPanelByKey`. The `check_panel_data_wired.mjs` script parses both
`pickPanel(panelDataFile, N)` and `pickPanelByKey(panelDataFile, "key")` patterns.
It does NOT parse raw `panelsById[key]` lookups -- they are invisible to the gate.
