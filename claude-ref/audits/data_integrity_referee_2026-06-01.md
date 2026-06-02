# Data Integrity Referee Audit — 2026-06-01

Adversarial audit of Codex's integrity-gate additions, layered on Claude's earlier
`52a6ece` gate. All claims verified against actual `git diff` and by running tests
independently. No model summaries trusted without file-level confirmation.

---

## Verdict: Recurrence Prevented — YES

The recurrence path (bad/stale daily market data committed to master and deployed) is
closed. Both workflows now fail before commit on any integrity violation. The Python gate
raises on violation; the JS gate exits non-zero. Both are wired before the commit step
with `continue-on-error` removed.

---

## Biggest Remaining Risk

**Sections.json gate has no sane-range check on print values.** If a data source returns
a finite-but-absurd value (e.g., WTI = 999.0), the sections.json check would pass (only
NaN/Infinity are caught there). The panel_data gate catches it via sane ranges before
commit — so the recurrence is still blocked — but there is a gap in the sections.json
coverage that is not immediately obvious. Mitigated by redundancy; not a blocker.

---

## Per-Question Verdicts

**Q1 — Can any scheduled refresh still commit bad data before the integrity gate fails?**
NO. Both `build-financial-daily.yml` and `build-monthly.yml` have `continue-on-error`
removed from build and integrity steps. The Python build calls `build_all_panel_data` via
`_safe()`; `build_all_panel_data` raises `RuntimeError` on violations; `_safe` catches
it, appends to `failed`, and `main()` returns 1. Workflow step exits non-zero, subsequent
steps (including commit) are skipped. The gate is before commit on every path, including
build-monthly. **CLEAN.**

**Q2 — Can stale-but-valid daily market/yield data still ship silently?**
NO. `FAIL_ON_STALE = True` and `STALENESS_FAIL_SERIES` is populated with all 13
daily market/yield series. Both Python and JS gates use `shouldFailStaleness(key)` /
`key in STALENESS_FAIL_SERIES` to fail-close on those series. A frozen fetcher raises at
fetch time (`ValueError` from `fetch_series`), fails the build step, and no commit
happens. If the fetcher succeeds but returns stale-dated data, the business-day staleness
check catches it at `build_all_panel_data`. **CLEAN.**

**Q3 — Are the JS gate and Python validator consistent?**
YES, with one structural note. Both have identical `STALENESS_FAIL_SERIES` sets (13
series). Both use the same business-day vs calendar-day distinction keyed on `freq ==
"daily"`. The JS gate additionally checks `sections.json` print values (NaN/Infinity +
staleness) — the Python gate does not have a counterpart for sections.json, but
`build_site_data` is also wrapped in `_safe` and a bad sections.json would be caught by
the panel_data gate which validates the same underlying raw CSVs. One divergence: the
sections.json gate has no sane-range check (JS or Python); panel_data gate does. This is
a gap, not a contradiction. **MOSTLY CONSISTENT — nit on sections.json sane-range gap.**

**Q4 — Are staleness thresholds defensible?**
YES. Business-day counting is correct and verified:
- `_business_days_since` counts the interval (as_of_date, today) exclusive on both ends,
  skipping weekends and a 17-holiday North American calendar.
- `businessDaysSince` in JS uses the same loop structure; verified to be equivalent.
- No off-by-one: confirmed via direct execution for May 29 → June 3 (returns 2 business
  days; correct).
- `daily` threshold = 3 business days. A Friday close is 1bd stale on Monday, 2bd on
  Tuesday, 3bd on Wednesday (fails on Thursday). Adequate for daily series.
- Monthly/quarterly thresholds loosened (105d, 220d) to accommodate reference-period
  stamping. These are calendar days, which is correct since `asOfISO` for StatCan
  series marks the reference period end, not the publication date.
- Holiday detection verified: Victoria Day 2026 = May 18, Memorial Day 2026 = May 25 —
  both correctly identified. `test_business_day_age_skips_market_holidays` passes.
**CLEAN.**

**Q5 — Does sections.json coverage catch the live failure mode?**
PARTIALLY. The live failure mode was null/NaN/stale values in the `overview/markets`
print + sparkline slots. The JS `checkSectionsPayload` now checks `sections.sections[*].prints[*].valueRaw` and `.priorRaw` for NaN/Infinity, checks `.spark[]` values, and
checks staleness for the 6 series in `SECTION_PRINT_SERIES`. The mapping is correct:
`goc-2y` → `yield_2yr`, `usdcad` → `fxusdcad`, etc. Keys confirmed against actual
`sections.json` structure (`data['sections']['markets']['prints'][*]['key']`). However,
no sane-range check on `.valueRaw`. See Q3. **MOSTLY — nit on sane range.**

**Q6 — Trailing-latest nulls blocked, historical gaps allowed?**
YES. `_check_slot_integrity` explicitly checks only `data[-1].value is None` (trailing),
not mid-series nulls. Mid-series nulls are allowed (StatCan suppression). A null-then-
stale-repeat-value scenario does not fool the gate: the stale date would be caught by
the staleness check before any carry-forward value matters. `_df_to_records` maps Inf/NaN
to None before writing, so the trailing-null check will catch those at the boundary.
**CLEAN.**

**Q7 — FRED merge behavior — regression or data-loss risk?**
LOW. `write_series_merge` is a union-merge that keeps old rows where the date is not in
the new fetch, then appends all new rows. Bad partial responses (fewer rows than on disk)
preserve on-disk history. Bad values for EXISTING dates DO overwrite old values — correct
by design, since upstream revisions should take priority. NaT rows from unparseable old
CSV dates are kept and sorted last (NaT sorts to tail in pandas); the trailing-null check
would catch a resulting bad last record. `test_write_series_merge_*` suite has 4 tests
covering no-existing-file, disjoint dates, overlap-prefer-new, and preserve-dropped-dates.
**CLEAN — no regression introduced.**

**Q8 — Remaining NaN/Infinity emission paths in transforms?**
No uncovered paths found. `timeseries.py`: all four public transform functions route
through `_replace_inf()` which calls `.replace([np.inf, -np.inf], np.nan)`. `derivations.py`:
`partner_share_trajectory` now guards `total != 0` (Codex fix). `goc_ust_spread` uses
subtraction only. `per_capita_growth` and `headline_yoy` route through `yoy_pct` which is
guarded. `panel_data.py` labour flow rates: explicit `u_t <= 0` and `employment <= 0`
guards before every division. And `_df_to_records` converts any remaining Inf/NaN to None
at the serialization boundary. **CLEAN.**

**Q9 — Are new tests meaningful? What negative case is missing?**
Tests are meaningful and would actually fail on regression:
- `test_df_to_records_never_emits_nan_or_infinity`: asserts exact output `{"value": None}`.
- `test_validate_panel_data_fails_stale_daily_market_series`: uses `today=date(2026,6,2)`
  and fixture with `asOfISO=2026-05-25` (5 business days old > threshold 3). Would fail if
  staleness logic regressed.
- `test_business_day_age_skips_market_holidays`: `_business_days_since(May22, May27) == 1`
  with May 25 as Memorial Day. Would fail if holiday set regressed.
- `test_validate_panel_data_allows_slow_reference_period_series`: confirms slow monthly
  series are NOT failed.
- `test_validate_panel_data_fails_trailing_null`: confirms trailing null fires.
- `test_percent_transforms_replace_zero_denominator_inf_with_nan`: asserts no inf in
  output of all four transform functions.
- `test_partner_share_trajectory_drops_zero_denominator`: direct drop verification.

**Missing negative case:** No test for the scenario where a series IS in
`STALENESS_FAIL_SERIES` but has an OVERRIDE threshold (e.g., `goc_ust_spread_2y` override
= 10). There is no test confirming that the override is applied (instead of the default 3)
for a fail-closed series. If the override lookup were accidentally dropped, the gate would
become too tight (3 business days for a derived spread series). **Should-fix.**

**Q10 — Did Codex clobber pre-existing dirty files?**
NO. Codex's changes are exactly scoped to the 10 declared files. Additional dirty files
in the working tree (`tests/visual/__snapshots__/`, `data/raw/indeed_*`,
`data/derived/ff_calendar_cache.xml`) are from a pipeline data refresh run, not from
Codex's edits. Pre-existing dirty files (`CLAUDE.md`, `editorial/source_cards/audit/*.html`,
`data/derived/news_feed_cache.json`) are untouched. **CLEAN.**

---

## Fixes Made

None. No code changes required. The gate is sound. The sections.json sane-range gap and
the missing override-threshold test are documented above as should-fix and nit respectively,
but neither represents a recurrence path.

---

## Tests Run

```
py -m pytest pipeline/tests/test_transform.py \
              pipeline/tests/test_build_derivations.py \
              pipeline/tests/test_panel_data_integrity.py -v

# Result: 33 passed in 1.54s (Python 3.14.4, pytest 8.4.2)

npm run audit:integrity
# Result: OK: 9 file(s) passed integrity check (5 staleness warnings — all correctly
# classified as warn-only slow macro releases)
```

---

## Files Inspected

- `.github/workflows/build-financial-daily.yml` (git diff + full file)
- `.github/workflows/build-monthly.yml` (git diff)
- `scripts/check_panel_data_integrity.mjs` (git diff, key sections)
- `pipeline/io/panel_data.py` (git diff; `_check_slot_integrity`, `_business_days_since`,
  `_market_holidays`, `build_all_panel_data`, `validate_panel_data_file`, `_df_to_records`)
- `pipeline/io/meta.py` (`write_series_merge`, `_merge_by_date`, `SeriesMeta`)
- `pipeline/fetch/fred.py` (git diff + `fetch_series` full)
- `pipeline/fetch/_http.py` (retry/error handling)
- `pipeline/build_financial.py` (git diff; `_safe`, `main`, `_fred_fetch_one`)
- `pipeline/build.py` (`build_all_panel_data` call)
- `pipeline/transform/derivations.py` (git diff + full)
- `pipeline/transform/timeseries.py` (`_replace_inf`, all public functions)
- `pipeline/tests/test_panel_data_integrity.py` (full)
- `pipeline/tests/fixtures/panel_integrity/stale_daily.json`
- `pipeline/tests/fixtures/panel_integrity/slow_monthly.json`
- `data/site/sections.json` (structure inspection, market/monetary print keys)
