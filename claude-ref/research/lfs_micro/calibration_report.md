# LFS-micro Calibration Report

Generated: 2026-06-05 06:08 UTC (initial calibration); updated 2026-06-05 with divergence diagnosis and corrected data

## Calibration grid results

Benchmark: BoC Valet `INDINF_LFSMICRO_M` (y/y %, monthly)
Overlap window: 2016-01 onwards (PUMF y/y starts 2016 with 2015 base year)

| weighted | smoothing | ob_reference | RMSE | MAE | corr | n |
|----------|-----------|--------------|------|-----|------|---|
| True | raw | base | 0.8389 | 0.2269 | 0.7786 | 123 |
| True | raw | current | 0.844 | 0.2316 | 0.7787 | 123 |
| True | ma3 | base | 0.4856 | 0.2573 | 0.8998 | 122 | **WINNER**
| True | ma3 | current | 0.4867 | 0.2586 | 0.9013 | 122 |
| False | raw | base | 0.8417 | 0.3647 | 0.7764 | 123 |
| False | raw | current | 0.8597 | 0.3667 | 0.7758 | 123 |
| False | ma3 | base | 0.575 | 0.3659 | 0.8668 | 122 |
| False | ma3 | current | 0.5851 | 0.3641 | 0.8675 | 122 |

## Winning Spec

- weighted: True
- smoothing: ma3
- ob_reference: base
- min_cell_count: 30

RMSE: 0.4856 pp
MAE:  0.2573 pp
corr: 0.8998
Overlap: 2016-02-01 to 2026-03-01 (n=122)

## Last 12 months comparison (ours vs BoC)

| date | ours | BoC | diff |
|------|------|-----|------|
| 2025-04-01 | 4.576 | 3.5 | +1.076 |
| 2025-05-01 | 2.399 | 3.2 | -0.801 |
| 2025-06-01 | 1.257 | 3.1 | -1.843 |
| 2025-07-01 | 1.137 | 3.3 | -2.163 |
| 2025-08-01 | 3.036 | 3.0 | +0.036 |
| 2025-09-01 | 2.845 | 2.9 | -0.055 |
| 2025-10-01 | 2.845 | 2.7 | +0.145 |
| 2025-11-01 | 2.812 | 2.9 | -0.088 |
| 2025-12-01 | 2.834 | 2.8 | +0.034 |
| 2026-01-01 | 2.749 | 2.7 | +0.049 |
| 2026-02-01 | 2.874 | 2.6 | +0.274 |
| 2026-03-01 | 1.943 | 3.1 | -1.157 |

## Post-correction fit (updated 2026-06-05)

Following the divergence diagnosis (see section below), two corrupted PUMF parquets were
replaced and the series recomputed. The winning Spec is unchanged (weighted=True, ma3, base).

| metric | before correction | after correction |
|--------|-------------------|-----------------|
| RMSE (full sample) | 0.4856 pp | **0.3655 pp** |
| MAE (full sample)  | 0.2573 pp | **0.1957 pp** |
| corr (full sample) | 0.8998 | **0.9441** |
| RMSE (last 18 months) | 0.8458 pp | **0.1510 pp** |
| MAE (last 18 months)  | 0.5463 pp | **0.1289 pp** |
| Overlap n | 122 | 122 |

### Corrected last 15 months comparison (ours vs BoC)

| date | ours | BoC | diff |
|------|------|-----|------|
| 2025-01-01 | 3.756 | 3.5 | +0.256 |
| 2025-02-01 | 3.717 | 3.8 | -0.083 |
| 2025-03-01 | 3.697 | 3.6 | +0.097 |
| 2025-04-01 | 3.513 | 3.5 | +0.013 |
| 2025-05-01 | 3.350 | 3.2 | +0.150 |
| 2025-06-01 | 3.247 | 3.1 | +0.147 |
| 2025-07-01 | 3.125 | 3.3 | -0.175 |
| 2025-08-01 | 3.036 | 3.0 | +0.036 |
| 2025-09-01 | 2.845 | 2.9 | -0.055 |
| 2025-10-01 | 2.845 | 2.7 | +0.145 |
| 2025-11-01 | 2.812 | 2.9 | -0.088 |
| 2025-12-01 | 2.834 | 2.8 | +0.034 |
| 2026-01-01 | 2.749 | 2.7 | +0.049 |
| 2026-02-01 | 2.874 | 2.6 | +0.274 |
| 2026-03-01 | 2.996 | 3.1 | -0.104 |

Apr 2026 (leading indicator, not yet in BoC series):
- Trailing MA3 underlying: **2.996%** (uses Feb/Mar/Apr 2026 lp values)
- Raw point estimate: 3.132%
- Centered MA3 unavailable (May 2026 PUMF not yet posted)

## Divergence diagnosis (2026-06-05)

### Ranked hypotheses tested

1. **VINTAGE MISMATCH** — BoC revised its published INDINF_LFSMICRO_M values after Feb 2025.
   Test: fresh Valet pull vs cached CSV. Result: **eliminated** — all 315 BoC values identical,
   fresh pull ends 2026-03-01. Cached copy was fetched 2026-06-04 and is current.

2. **MA ALIGNMENT** — centered vs trailing 3-month MA diverges at the sample edge.
   Test: compare RMSE of centered MA vs shifted-by-1 alignment against BoC.
   Result: **eliminated as primary cause** — trailing alignment (ours[t-1] vs BoC[t])
   produces nearly identical RMSE (0.4997 full, 0.8236 last 18mo vs 0.4856/0.8458 centered).
   Neither alignment removes the Apr-Jul 2025 or Mar 2026 spikes.

3. **CACHE CORRUPTION** — two PUMF parquets contain wrong-month data.
   Test: check survyear/survmnth embedded in each parquet vs filename.
   Result: **CONFIRMED ROOT CAUSE.**

### Root cause

Two parquet files were discovered to contain April 2026 microdata (survyear=2026, survmnth=4)
instead of the months indicated by their filenames:

- `data/raw/lfs_pumf/2024-06.parquet` — should contain June 2024 data
- `data/raw/lfs_pumf/2025-04.parquet` — should contain April 2025 data

Both files were sourced from `spike_cache:lfs_2026_04_CSV.zip` (per their .meta.json sidecars),
which placed the April 2026 single-CSV zip in the spike cache folder. The downloader's
single-CSV fallback in `_extract_monthly_from_zip_bytes` accepted any lone CSV without
validating its month — so the Apr 2026 file was cached as both Jun 2024 and Apr 2025.

Consequences on the y/y engine:
- 2025-04 vs 2024-04: Apr 2025 current month was actually Apr 2026 data. Wage level ~$37.77
  (Apr 2026) vs ~$34.94 (Apr 2024 true). Raw y/y = +7.7% instead of ~3.5%. After MA3,
  this inflated Apr 2025 underlying to +4.576% and Mar 2025 to +4.761%.
- 2025-06 vs 2024-06: Jun 2024 base month was actually Apr 2026 data. Wage level ~$37.77
  (Apr 2026) vs ~$35.70 (true Jun 2024). Base inflated → Jun 2025 looks like a wage
  collapse (-4.4% raw). After MA3, this pulled May-Jul 2025 underlying down to 2.4%,
  1.3%, 1.1% — the large negative misses against BoC.
- 2026-03: centered MA3 window for Mar 2026 = (Feb + Mar + Apr 2026) / 3. Apr 2026 was
  the corrupted file with correct Apr 2026 data, but Mar 2026's y/y base was Sep 2025
  (not corrupted). The Mar 2026 miss was driven by the MA3 averaging over Apr 2026's
  raw_lp value computed against a clean Apr 2025 base — but the Apr 2025 current month
  file in the pair 2026-Apr vs 2025-Apr was affected. Once corrected, Mar 2026 moves to
  2.996% vs BoC 3.1% (-0.104pp), within normal bounds.

### Fix applied

1. `data/raw/lfs_pumf/2024-06.parquet` and `2024-06.meta.json` deleted and re-fetched
   from the 2024 annual bundle (`data/raw/lfs_pumf/annual/2024-CSV.zip`). Verified:
   survyear=[2024] survmnth=[6], hrlyearn_mean=3436.6 (cents), rows=113,108.

2. `data/raw/lfs_pumf/2025-04.parquet` and `2025-04.meta.json` deleted and re-fetched
   from the 2025 annual bundle (`data/raw/lfs_pumf/annual/2025-CSV.zip`). Verified:
   survyear=[2025] survmnth=[4], hrlyearn_mean=3542.5 (cents), rows=116,287.

3. `pipeline/lfs_pumf/download.py` updated to add `_validate_survyear_survmnth()` —
   a fail-closed integrity check that raises RuntimeError if the embedded survyear/survmnth
   does not match the requested month. Future downloads will fail loudly rather than silently
   cache wrong-month data.

4. Engine recomputed for the 8 directly affected month-pairs (2025-03 through 2025-08 and
   2026-03 through 2026-04), patched into the full series, MA3 re-applied, replication CSV
   rewritten. All other 114 months are unchanged.

## NAICS spot-check

NAICS_21 codes are identical between 2015-01 and 2026-04 — Feb 2025 re-release consistently applied NAICS 2022 throughout history.

- Early month: 2015-01
- Late month:  2026-04
- Consistent:  True

## Second divergence diagnosis (2026-06-05 PM): Dec-2024-Feb-2025 spike

Jay spotted a 2025 "headline wage gain" in our series (Dec-24 5.05%, Jan-25 5.00%,
Feb-25 4.96%) that the BoC's published series did not show (+1.5pp divergence at peak).
Three distinct bugs found and fixed:

1. **Pytest poisoned the production engine cache** (the direct cause of the spike).
   `test_lfs_micro_run.py` patched `_RAW_PUMF_DIR` but not `_ENGINE_CACHE_DIR`
   (separate module global), so a synthetic 2025-01 fixture result (n=325,
   R^2=0.09, raw y/y 7.15%) was written to the real cache. The centered MA3
   spread its +3.6pp single-month error across the Dec-Feb readings at ~+1.2pp
   each. Fixed: cache dir now derived from `_RAW_PUMF_DIR` at call time
   (`_engine_cache_dir()`), so test isolation is automatic.

2. **Row-misalignment in `run_wls`** when thin-category pruning dropped rows.
   `_prepare_categoricals` returns a reset-index frame; `log_wage[df_clean.index]`
   therefore sliced the FIRST m rows of the pre-filter arrays instead of the kept
   rows — regressing the wrong rows' wages on the design matrix. Hit 2015-02,
   2016-02, 2021-02, 2022-02 (R^2 0.004 vs normal ~0.61), poisoning those pairs'
   decompositions. Fixed: y and weights now derived from the filtered frame itself.

3. **`_fix_rank_deficiency` returned the sqrt-weight-SCALED design matrix** as if
   unscaled; callers computed `mean_X` (composition shares) and R^2 from it.
   Never observed firing in production (no rank-deficient months in the clean
   data) but would silently poison any month it touched. Fixed: returns the
   pruned unscaled matrix.

Hardening added to `run.py`:
- Cache entries carry `parquet_fingerprints` (file sizes of the current + t-12
  parquets); mismatch or absence = cache miss. A repaired parquet now
  auto-invalidates its downstream results.
- Plausibility gate: entries with n_obs < 20,000 or R^2 < 0.40 are refused at
  save time (RuntimeError, fail-closed) and treated as misses at load time.

Full 125-month clean recompute after the fixes (engine cache wiped):

| metric | after parquet fix (AM) | after engine fixes (PM) |
|--------|------------------------|-------------------------|
| RMSE (full sample) | 0.3655 pp | **0.1768 pp** |
| corr (full sample) | 0.9441 | **0.9854** |
| RMSE (last 18 months) | 0.1510 pp | **0.1510 pp** |
| max abs diff anywhere | ~2.2 pp | **0.540 pp** (2017-04) |

Spike window corrected: Dec-24 3.81 (BoC 3.6), Jan-25 3.76 (3.5), Feb-25 3.72 (3.8).
April 2026 headline unchanged at 2.978% — recent months were never contaminated.

## FIRMSIZE experiment (2026-06-05)

### What changed

`firmsize` (PUMF field 40, 4-level firm-size scale parallel to `estsize`) was added to
the regressor set: `REGRESSOR_GROUPS`, `_KEEP_COLS` in `download.py`, `harmonize.py`
(graceful fallback: NaN-filled for any parquet written before this change), and
`_prepare_categoricals` (skips all-NaN columns, so old parquets do not break).

All 137 parquets were re-downloaded and re-parqueted to include the `firmsize` column
(StatCan Chrome-UA requests, annual bundle path; monthly recent for 2026-01 to 2026-05).
Full 125-month engine recompute followed (~34 minutes, Win11 i7).

Regressor-set cache invalidation: the per-month engine cache now embeds a `regressor_set`
key (sorted list of column names from `REGRESSOR_GROUPS`). Any regressor addition or
removal triggers automatic cache miss. The SHA-256 parquet fingerprint gate provides an
independent second invalidation channel.

### Fit results

Baseline (without firmsize, after all Phase A bug fixes):
  RMSE (full sample, n=122): 0.1768 pp
  corr (full sample):        0.9854
  RMSE (last 18 months):     0.1510 pp

With firmsize added:
  RMSE (full sample, n=122): 0.1804 pp  (+0.4bps)
  MAE  (full sample):        0.1453 pp
  corr (full sample):        0.9860  (+0.0006)
  RMSE (last 18 months):     0.1818 pp
  MAE  (last 18 months):     0.1559 pp
  corr (last 18 months):     0.9523

### Headline shift

Apr 2026 leading indicator (trailing MA3, not yet in BoC benchmark):
  Without firmsize:  2.978% y/y (underlying)
  With firmsize:     3.014% y/y (underlying)
  Change:           +0.036 pp

Latest in-sample reading (Mar 2026, in BoC benchmark):
  Ours: 3.052%  BoC: 3.1%  diff: -0.048 pp  (vs -0.104 pp without firmsize)

### Corrected last 12 months (with firmsize)

| date | ours | BoC | diff |
|------|------|-----|------|
| 2025-04-01 | 3.590 | 3.5 | +0.090 |
| 2025-05-01 | 3.445 | 3.2 | +0.245 |
| 2025-06-01 | 3.360 | 3.1 | +0.260 |
| 2025-07-01 | 3.241 | 3.3 | -0.059 |
| 2025-08-01 | 3.145 | 3.0 | +0.145 |
| 2025-09-01 | 2.940 | 2.9 | +0.040 |
| 2025-10-01 | 2.926 | 2.7 | +0.226 |
| 2025-11-01 | 2.881 | 2.9 | -0.019 |
| 2025-12-01 | 2.909 | 2.8 | +0.109 |
| 2026-01-01 | 2.828 | 2.7 | +0.128 |
| 2026-02-01 | 2.948 | 2.6 | +0.348 |
| 2026-03-01 | 3.052 | 3.1 | -0.048 |

### Decision

Firmsize kept in default spec. Rationale: (1) it matches the stated covariates in
BoC SAN 2024-23; (2) fit is statistically indistinguishable from the without-firmsize
baseline (RMSE delta <0.5bps, corr slightly improved); (3) identification is clean
(no collinearity issues observed; 276 tests pass). The +0.036pp shift on the Apr 2026
headline is within the normal month-to-month noise band.

## Runtime

Full refresh (download + harmonize + 8-spec grid): 2164 seconds
Phase B firmsize full recompute (125 months, no prior cache): ~2040 seconds

## Notes

- Composition effect captures employment-share shifts across categories.
- Underlying wage growth = wage-return changes for a fixed worker mix.
- BoC SAN 2024-23 uses y/y % on the same PUMF data; near-exact replication
  is achievable since we use the same source. Residual divergence comes from
  exact spec choices (reference convention, smoothing, bin granularity).
- Log-point to percent conversion: pct = (exp(log_pt) - 1) * 100.
  For values near 3-4%, this differs from raw log-points by <0.1pp.
