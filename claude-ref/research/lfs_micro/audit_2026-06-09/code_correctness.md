# LFS-micro code-correctness audit — 2026-06-09

Adversarial audit of `pipeline/lfs_micro/` (branch `lfs-micro`). Scope: WLS mechanics,
Oaxaca-Blinder math, engine cache integrity, y/y assembly, calibration honesty, test suite.
All claims below were verified by independent computation, not by reading comments or tests.
Scratch scripts: `claude-ref/research/lfs_micro/audit_2026-06-09/scratch/`
(`exp_synthetic.py`, `exp_calib_cache.py`, `exp_rankdef_meanx.py`). No production code,
data, or cache was modified (confirmed via `git status` + cache mtimes after all runs).

## Verdict

The statistics are correct. No BLOCKER. One MAJOR (a forward-looking cache-invalidation
gap, not a present-data error), four MINOR, six NOTEs. The three historical bug fixes are
real and complete. The headline calibration claims reproduce exactly from the production
CSVs with correct date alignment.

---

## Severity-ranked findings

### MAJOR-1: Engine cache is not invalidated by harmonization/regression CODE changes

Evidence: `pipeline/lfs_micro/run.py:151-214` (`_load_cache`). Cache hits require matching
(a) spec fields `weighted` / `ob_reference` / `min_cell_count`, (b) the sorted regressor
set, (c) SHA-256 fingerprints of the two RAW parquets. Nothing keys on the harmonization
logic: `harmonize.py` recoding (e.g. the hardcoded tenure bins at `harmonize.py:243`
`_bin_tenure`, wage filters, category recodes) runs at compute time on the raw parquet, so
a code change there alters results without changing any cache key. Old months stay cached
under the old methodology while new months compute under the new one — a silently mixed
series. There is also no force-recompute flag: `--rebuild` only rewrites outputs from
cache (`run.py:680`), and `--force-download` re-fetches parquets whose content (and hence
SHA-256) is typically identical. The only remedy is manually deleting
`data/raw/lfs_pumf/_engine_cache/`, which is undocumented in the CLI help.

How verified: code path trace + the F-series sandbox probes (below) which confirm exactly
which fields participate in invalidation. Current outputs are NOT affected (no such code
change has occurred since the cache was last fully rebuilt on 2026-06-05); the regressor-
set guard does catch the most common change class (adding/removing a regressor).

Suggested fix (not applied — read-only audit): embed a methodology version constant (or a
hash of `harmonize.py` + `regression.py` source) in each cache entry and compare on load.

### MINOR-1: `Spec.tenure_bins` is dead configuration with misleading documentation

Evidence: `spec.py:28-33` documents tenure_bins as a calibration parameter and claims
"changing bins invalidates existing parquet caches (re-harmonize needed)";
`harmonize.py:243` uses module-level hardcoded `_bin_tenure` — the spec value is never
threaded through. It is also excluded from cache invalidation (`run.py:173`). Changing it
is a silent no-op, while `make_workbook.py:459` prints it in params_meta as if active.
Verified by grep: zero consumers outside spec.py itself and the workbook label.

### MINOR-2: Workbook params_meta ships stale MA3 boilerplate contradicting the raw spec

Evidence: `make_workbook.py:476-478` ("MA3 timing convention: ... Most recent non-NaN
headline = newest_PUMF_month - 1") and `:494-496` ("Caveat: MA3 smoothing ... applied ...
before y/y differencing") are unconditional rows, two rows below `SPEC: smoothing = raw`
(`:456`). Under the recalibrated raw spec both rows are false (headline = newest month,
no MA applied); the caveat text additionally misstates even the old MA3 (it was applied to
the y/y log-point series, not before y/y differencing — `engine.py:357-366`). Jay opens
this workbook; the metadata sheet misdescribes the series.

### MINOR-3: `_print_summary` can print a cross-month diff

Evidence: `run.py:808-815`. `diff = last["underlying_pct"] - boc_latest_val` compares our
latest month against BoC's latest month. The guard (`if last_date in boc...index`)
suppresses it in the current state (ours runs 2 months ahead of BoC), but if BoC were ever
ahead of the PUMF the printed "Difference (ours minus BoC)" would compare different months.
Stdout cosmetics only; the CSV is unaffected.

### MINOR-4: `_load_cache` docstring still describes the superseded file-size fingerprint

Evidence: `run.py:157-158` ("file-size fingerprint mismatch") vs the actual SHA-256
implementation at `run.py:121-148`. Stale documentation on a security-relevant mechanism.

### NOTE-1: Thin-category counting is sequential, not global

`regression.py:225-255`: counts for later regressor groups are taken on rows already
filtered by earlier groups' thin-cat drops, so `min_cell_count` is not a global per-
category guarantee. Deterministic (fixed REGRESSOR_GROUPS order) and inconsequential at
LFS sample sizes.

### NOTE-2: Union universe keeps sub-threshold cells in one month

`regression.py:235-237`: when a universe is supplied, per-month thin-cell thresholds are
not re-applied — a category with ≥30 obs in month t but 1-29 in t-12 stays in. Known and
sensitivity-tested by the project (Phase C: intersection-rule delta 0.003pp).

### NOTE-3: Rank detection uses unpivoted QR

`regression.py:321-335` / `:349-370`: unpivoted QR diag with relative 1e-12 threshold is
exact for the realistic failure mode (exact dummy collinearity / all-zero columns —
verified below) but a near-collinear column flagged by lstsq's SVD rank could in principle
escape the QR loop, leaving lstsq's min-norm solution silently. Mitigated: any resulting
col_names mismatch between months raises in `engine.py:258-263` / `decompose.py:98-102`
and `run.py:408-414` converts that to a hard abort (fail-closed, no silent gap).

### NOTE-4: Headline = two-fold "underlying"; C + U ≠ total by the interaction term

`decompose.py:120-130`: composition + underlying + interaction == total_fitted (identity,
verified to 1e-14). The interaction (ΔX'ΔB) is excluded from the headline by design and
written to the CSV (`interaction_pct`; observed magnitudes ≤0.05pp). Standard two-fold
O-B; not a bug.

### NOTE-5: Grid-search overfitting risk is low

`calibrate.py:93-107`: 8 candidates over 3 binary knobs, scored on RMSE vs the BoC target
over n≈123 months. With 3 effective binary degrees of freedom the selection cannot
meaningfully overfit, and the chosen spec (weighted WLS, unsmoothed, base reference) is
also the methodological default. The MA3→raw reversal was driven by independent roughness
diagnostics (m/m change std + change autocorrelation), which I reproduced (below), not by
RMSE alone. `min_cell_count` was never searched (fixed at 30).

### NOTE-6: Calibration-report top section is stale by design

`calibration_report.md` opens with the pre-correction grid ("WINNER ma3, RMSE 0.4856").
The operative numbers are in the final section ("Recalibration on clean data: raw RMSE
0.1178, corr 0.9966, n=123"), which matches my independent recompute exactly. The spec.py
comment cites 0.1181/n=122 — a one-month-older vintage of the same computation. Consistent
with the project's tag-and-keep convention, but a reader stopping at the top table gets
superseded numbers.

---

## Verification detail

### 1. WLS mechanics (regression.py) — CORRECT

- sqrt(w) row-scaling + `lstsq` is applied consistently; means/R² computed on the
  UNSCALED design with original weights (`run.py` of regression: lines 179-192).
- Independent ground truth: multi-categorical synthetic (n=5,000, 3 groups, random
  weights 0.5-5.0, noise σ=0.3) — coefficients match the normal-equations solution
  (X'WX)⁻¹X'Wy to max|diff| < 1e-8; weighted R² matches to 1e-10 (exp_synthetic B).
- Dummy encoding: deterministic order (intercept, then REGRESSOR_GROUPS order, sorted
  categories within group, first dropped as baseline). Verified col_names exactly.
- Known-answer recovery: two-group no-noise case recovers intercept=log(25),
  β=log(20/25) to 1e-10 (exp_synthetic A1).

### 2. Oaxaca-Blinder (decompose.py) — CORRECT

- Pure composition shift, constant within-group wages: underlying = -1e-15 ≈ 0;
  composition = Δshare·β exactly; total_fitted == raw_mean_change (perfect fit case);
  group contributions sum to composition to 1e-14 (A1).
- Pure wage growth, constant composition: underlying = log(1.03) exact; composition = 0;
  interaction = 0 (A2).
- No silent re-basing: B_ref/X_ref selected once from the named reference period
  (`decompose.py:113-118`); weights drive mean_X (weighted-share check A3: 4x-weighted
  rows → share 0.8 exact).

### 3. The three "fixed" bugs — all fixes REAL and COMPLETE

1. **pytest cache poisoning**: `_engine_cache_dir()` derived from `_RAW_PUMF_DIR` at call
   time (`run.py:103-111`); tests patch the module attr to tmp_path
   (`test_lfs_micro_run.py:93-95` et al.). Ran the FULL suite today; all 125 production
   cache entries retain 2026-06-05 mtimes — untouched.
2. **Row misalignment under thin-category pruning**: y and weights are derived from the
   post-filter frame (`regression.py:142-156`). Adversarial test: 10 poison rows
   (wage=$1000, thin category) prepended to the frame — coefficients and R² byte-identical
   to a never-poisoned fit; n_obs exact (exp_synthetic C). The old bug (R²≈0.004 collapse)
   cannot reproduce.
3. **Rank-deficiency scaled-matrix return**: `_fix_rank_deficiency` returns the pruned
   UNSCALED DataFrame (`regression.py:338-346`). Isolated test with weights 5.0/1.0 and a
   forced all-zero universe column: mean_X equals true weighted shares (0.285714 exact),
   intercept share = 1.0, coefficients and R² correct (exp_rankdef_meanx.py).

### 4. Engine/run cache and assembly — SOUND

Sandbox probes (exp_calib_cache F1-F10, `_RAW_PUMF_DIR` patched to scratch): valid entry
loads; same-size content tamper of current OR base parquet → miss (real SHA-256, not
size); missing parquet → miss; implausible row (n=325, R²=0.09) refused at save with
RuntimeError; hand-planted implausible entry WITH valid fingerprints → rejected by the
plausibility gate (fail-closed both directions); spec-field change → miss; regressor-set
change → miss; legacy entry without fingerprints → miss; entry missing n/R² keys → miss
(defaults of 0 fail the gate). Assembly (`run.py:266-341`): calendar-gap check raises
before any smoothing; months keyed uniquely by YYYY-MM (no duplication path); string
date sort is correct for ISO dates. Disappearing-category month pair (category present in
t-12, absent in t) routed through `_apply_common_column_pruning` produces conformable
months and underlying = 2.5e-14 under constant within-group wages (exp_synthetic D).
May-2026 row: under the raw spec the newest month carries full headline values directly
(verified present in the production CSV, 2026-05 row).

### 5. Calibration honesty (calibrate.py) — CONFIRMED, alignment correct

Recomputed directly from `data/processed/lfs_micro_replication.csv` vs
`data/raw/lfs_micro.csv` (BoC INDINF_LFSMICRO_M, through 2026-03, no internal gaps):

| lag (months) | n | RMSE (pp) | MAE (pp) | corr |
|---|---|---|---|---|
| -1 | 124 | 0.3021 | 0.2343 | 0.9544 |
| **0** | **123** | **0.1178** | **0.0935** | **0.9966** |
| +1 | 122 | 0.3183 | 0.2523 | 0.9476 |

Lag 0 reproduces the reported figures exactly and both off-by-one alignments are ~2.7x
worse — the alignment is right, not luck. Roughness claim also reproduces: std of m/m
changes 0.294pp (BoC) vs 0.292pp (ours, raw) — consistent with the BoC series being
unsmoothed and with dropping MA3.

### 6. Test suite

`python -m pytest` (repo venv, pytest.ini testpaths=pipeline/tests): **277 passed, 0
failed** (claimed 276 — one test added since the claim). LFS-specific subset
(7 files): 86 passed.
