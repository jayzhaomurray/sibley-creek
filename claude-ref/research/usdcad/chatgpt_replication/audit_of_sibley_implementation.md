# Audit of Sibley USDCAD Implementation

Scope: reviewed only `pipeline/usdcad/model.py`, `pipeline/usdcad/acquire.py`, `work/research/usdcad/usdcad_findings_summary_2026-05-26.md`, and the prior `chatgpt_replication` implementation/results/methodology files requested for comparison.

## 1. Bugs found in `pipeline/usdcad/model.py`

### 1. Full-sample imputation and feature coverage before the hold-out split

- Function / lines: `build_model_dataset`, lines 153-162.
- What it does: Drops low-coverage columns and fills missing feature values using medians computed on the full dataset before `split_train_holdout` is called.
- Why it is a bug: The hold-out distribution is used during missingness screening and imputation fitting. The prompt explicitly forbids using hold-out data for imputation fitting or variable selection. This is leakage, even though it is feature-only leakage rather than target leakage.
- Expected effect: Moderate. It can change which variables are eligible and can alter the values fed to selection/scoring, especially for sparse variables. It will not by itself explain all of a +10pp to +15pp extreme-hit divergence, but it contaminates every reported hold-out metric.
- Fix: Split first. Fit coverage rules and imputation values on `X_train` only. Apply those fitted columns/medians to `X_holdout`.

### 2. CV splitter is not expanding walk-forward and validates only a small early slice

- Function / lines: `run_purged_walforward_cv`, lines 332-368, especially 347-358.
- What it does: Uses `train_idx = range(train_end - min_train, train_end - horizon_h)`, which creates a rolling fixed-width training window, not an expanding window. For weekly data, `test_size` is only 21 rows, so 10 folds validate roughly 210 observations near the beginning of the training sample, not the full training history.
- Why it is a bug: The comments and methodology claim walk-forward expanding CV. The implementation materially differs and makes CV performance and hyperparameter selection dependent on early-2006/2007 style regimes for weekly/monthly.
- Expected effect: Severe for CV numbers and embedded Elastic Net selection. Indirectly moderate to severe for hold-out, because selected variables can be regime-biased.
- Fix: Use expanding training indices `0 .. val_start - horizon_h`, and distribute validation folds across the whole training sample.

### 3. Elastic Net CV standardization leaks validation-fold distribution

- Function / lines: `run_elasticnet_selection`, lines 382-402.
- What it does: Standardizes the entire training matrix once using full-training mean/std, then passes those standardized values into `ElasticNetCV` with CV splits.
- Why it is a bug: Each validation fold contributes to the scaler used for that same fold. The framework forbids standardization fitting on validation data.
- Expected effect: Moderate. Directional hit rates may move a few points; feature selection can change where sparse/unstable variables are near the penalty boundary.
- Fix: Wrap imputation/scaling/model fitting in a fold-local pipeline, or manually fit scaler on each fold's training indices only.

### 4. MDA is not clustered MDA and ignores the purged CV splits

- Function / lines: `run_mda_selection`, lines 445-474.
- What it does: Fits one random forest on the first 80% of the training sample and computes vanilla permutation importance on the last 20%. The `splits` argument is unused. There is no clustering, purge, or embargo.
- Why it is a bug: The required method is clustered MDA. Also, for overlapping h-day returns, the boundary between the 80% fit block and 20% test block needs purging. This implementation lets training labels overlap the MDA validation period.
- Expected effect: Moderate to severe. MDA contributes one of the three votes, so non-purged vanilla importance can admit variables that would fail a proper clustered/purged MDA.
- Fix: Build correlation clusters, fit on purged walk-forward folds, permute whole clusters in validation blocks, and aggregate fold-level accuracy/R2 decreases.

### 5. Validation CV and hold-out evaluate different models

- Function / lines: `run_validation`, lines 770-819 versus 911-925.
- What it does: CV predictions come from a fold-fitted Elastic Net model. Hold-out predictions come from `compute_score_with_fixed_signs`, an equal-weight signed z-score composite. These are not the same scoring model.
- Why it is a bug: The reported CV hit rate/Sharpe/DSR are not validating the same object whose hold-out hit rate is reported. This breaks the model-selection narrative and makes the CV-to-hold-out comparison incoherent.
- Expected effect: Severe. This is a primary reason their hold-out hit rates diverge from mine: my hold-out score is the final Elastic Net prediction/fallback from the selected variables, while theirs is a separate equal-weight signed composite.
- Fix: Choose one score definition. If the product score is equal-weight signed z-score, CV must evaluate that same score using fold-local signs/scalers. If the model is Elastic Net, hold-out must use the final trained Elastic Net with training-fitted preprocessing.

### 6. Hold-out score standardization is fitted on the hold-out itself

- Function / lines: `compute_score_with_fixed_signs`, lines 679-715, especially 706-708; called for hold-out at lines 912-915.
- What it does: Computes `(X_sel - X_sel.mean()) / X_sel.std()` using whatever dataset is being scored. For hold-out, the mean/std are fitted on the entire hold-out period.
- Why it is a bug: The hold-out is used during standardization fitting. The prompt explicitly says the hold-out must never be used for standardization fitting. This is transductive feature leakage and is especially damaging for an extreme-reading product because it changes the relative contribution of each variable using future hold-out distribution information.
- Expected effect: Severe for extreme-reading metrics. It can materially change which observations land in top/bottom deciles and can flip/attenuate the score contribution of regime-shifted variables. This is one of the best explanations for the weekly +14.8pp extreme edge versus my +1.3pp edge.
- Fix: Fit the composite scaler on training data only, preferably within each CV fold for CV and on full training for hold-out. Apply those fixed means/stds or robust medians/IQRs to hold-out.

### 7. Training extreme-reading analysis is in-sample contaminated

- Function / lines: `determine_signs_first_half`, lines 507-520; `run_validation`, lines 811-859.
- What it does: Signs are estimated on the first half of training, then the training extreme hit rate is computed on the full training sample, including the same first half.
- Why it is a bug: The training extreme metric includes observations used to choose feature signs. It is not out-of-sample even within training.
- Expected effect: Moderate. It mainly inflates/contaminates the "training extreme edge" claims, not the hold-out claims.
- Fix: For training diagnostics, evaluate only on the second half after sign estimation, or compute fold-local signs in walk-forward validation.

### 8. Sharpe annualization is wrong for multi-day overlapping forecast returns

- Function / lines: `run_validation`, lines 817-819 and 932-935.
- What it does: Multiplies the mean/std of h-day strategy returns by `sqrt(252)` for every horizon.
- Why it is a bug: The returns being scored are 5d/21d/63d forward returns. Annualization should at least use `sqrt(252 / h)`, and even that overstates precision because returns overlap.
- Expected effect: Severe for reported Sharpe, not hit rate. Weekly Sharpe is inflated by about `sqrt(5) = 2.24x`, monthly by `sqrt(21) = 4.58x`, quarterly by `sqrt(63) = 7.94x`. Their quarterly hold-out Sharpe of 4.78 is not comparable to my 0.03.
- Fix: Use `sqrt(252 / horizon_h)` and disclose overlap; preferably compute on non-overlapping returns as a robustness check.

### 9. DSR is materially under-corrected and inconsistently defined

- Function / lines: `compute_deflated_sharpe_ratio`, lines 649-676; called at lines 823-828; trial count set in `run_horizon`, line 1089.
- What it does: Uses `n_trials = n_input`, i.e. 42 variables screened, and passes `cv_sharpe / sqrt(252)` into the DSR function. It ignores Elastic Net alpha/l1 trials, Boruta iterations, MDA trials/clusters, and alternative score definitions.
- Why it is a bug: Bailey-Lopez de Prado DSR is intended to correct for the number of independent trials in the research process, not just the raw number of variables. The code also mixes annualized and daily Sharpe conventions in a way that makes the output hard to interpret. The findings summary then treats `DSR=1.00` as credible.
- Expected effect: Severe for significance claims. It makes the quarterly CV signal look much more defensible than it is.
- Fix: Use an explicit trial count covering filter variables, Elastic Net hyperparameter grid, Boruta/shadow trials, and MDA clusters/folds. Keep Sharpe units consistent.

### 10. CV uses standard k-fold inside each walk-forward fold

- Function / lines: `run_validation`, lines 783-795, especially `cv=5` at line 787.
- What it does: Inside each walk-forward fold, it uses `ElasticNetCV(cv=5)`.
- Why it is a bug/suspect choice: The prompt says standard k-fold is invalid here. Although this inner CV only touches the historical training block for that outer fold, it still tunes hyperparameters using non-time-ordered folds with overlapping labels.
- Expected effect: Moderate for CV predictions and selected coefficients.
- Fix: Use purged walk-forward splits inside the fold training block, or carry hyperparameters selected from the outer training-only selection stage.

### 11. Reported CV R2 and hit rate are fold means, not aggregate OOS metrics

- Function / lines: `run_validation`, lines 798-809.
- What it does: Computes per-fold R2/hit, then reports the simple mean of folds.
- Why it is a bug/suspect choice: The summary labels these as CV OOS metrics. If folds differ in size or target variance, simple averaging is not the same as pooled out-of-sample performance.
- Expected effect: Minor to moderate. It will not explain the large weekly extreme divergence, but it adds noise and makes the metric non-comparable to pooled results.
- Fix: Store all OOS predictions and compute pooled R2/hit rate over all validation observations.

### 12. R2 is computed on an arbitrary uncalibrated composite scale

- Function / lines: `run_validation`, lines 927-930; `compute_score_with_fixed_signs`, lines 704-715.
- What it does: Compares forward log returns directly to an equal-weight z-score composite.
- Why it is a bug/suspect choice: A z-score score is not calibrated to return units. The huge negative R2 values in the findings summary are a symptom, not an interpretable predictive R2.
- Expected effect: Severe for R2 interpretation, negligible for sign hit rate.
- Fix: Either report rank/sign metrics only for the composite, or fit a training-only calibration from score to return before computing R2.

### 13. `np.sign(0)` can create invalid "neutral" predictions and feature signs

- Function / lines: `determine_signs_first_half`, lines 511-514; hit-rate code at lines 803 and 923-925.
- What it does: A zero Spearman rho produces sign `0.0`, and a zero score/prediction produces predicted sign `0`.
- Why it is a bug/suspect choice: Direction labels are `-1/+1`. A neutral sign is counted as a miss, but this behavior is undocumented and unstable for near-zero scores.
- Expected effect: Minor.
- Fix: Map zero signs deterministically to `+1` or use a no-trade bucket that is excluded/reported separately.

## 2. Bugs found in `pipeline/usdcad/acquire.py`

### 1. Monthly macro data are likely shifted from the observation-period date, not the release date

- Function / lines: `_align_daily` / `_align_monthly`, lines 91-118; examples `F3_us_cpi_yoy` lines 691-702, `F8_us_unemp` lines 745-753, `F14/F15 OECD CLI` lines 757-777, `G2_reer` lines 871-879.
- What it does: Reindexes monthly FRED observations to a daily business-day calendar, forward-fills from the observation date, then shifts by a fixed number of business days.
- Why it is a bug: FRED monthly observations are usually dated to the reference period, often the first day of the month, not the public release date. Shifting January CPI by 15 business days from January 1 can expose January CPI in late January, before the mid-February release. Unemployment and CLI have similar period-date/release-date problems.
- Expected effect: Severe for any selected macro variables. This can create genuine look-ahead in the processed data. It does not explain the divergence between my results and theirs if both used the same processed parquet, but it does undermine both implementations unless the upstream raw files already contain release dates.
- Fix: Use actual release calendars/vintages, or shift from period end by a conservative release lag. Document each source's date convention.

### 2. Monthly/quarterly alignment forward-fills before lagging

- Function / lines: `_align_daily`, lines 106-112; `_align_monthly`, lines 115-118; `_align_quarterly`, lines 121-124.
- What it does: Forward-fills the unlagged observation and then shifts the filled daily series.
- Why it is a bug/suspect choice: This is only equivalent to lag-then-fill for perfectly regular period-start data. For irregular release-dated series, holidays, or missing observations, it can create incorrect availability windows.
- Expected effect: Minor to moderate depending on source. For macro period-date series, the bigger issue is the wrong anchor date above.
- Fix: Convert each observation to its actual availability date first, then reindex and forward-fill from that availability date.

### 3. Same-day market closes are treated as known on the prediction date

- Function / lines: examples `C1_vix` lines 397-420, `C4_equity_diff` lines 438-449, `G1/G3/G4` lines 790-836, technical block `fetch_block_i` lines 1024-1088, `L1_fxi_ret` lines 1128-1138.
- What it does: Uses same-date closes/returns with `lag_bdays=0`.
- Why it is a bug/suspect choice: If the model is meant to produce a signal before the close on date `t`, same-day close-based values are not known. If the model is explicitly run after all relevant market closes, this is acceptable. The code does not state the prediction timestamp.
- Expected effect: Moderate for technical and risk variables. It can improve short-horizon weekly results if same-day close information is effectively allowed.
- Fix: Define the signal timestamp. If the signal is generated before the close, shift these variables one business day.

### 4. CFTC COT lag is documented but not applied

- Function / lines: `fetch_block_d`, lines 519-532.
- What it does: The comment says CFTC has a Friday release with approximately 3-day lag from Tuesday data, but `s_net` is built directly from the reported `date` and forward-filled without shifting.
- Why it is a bug: If the CFTC file date is the Tuesday "as of" date, the Tuesday-Friday values are leaked before publication.
- Expected effect: Severe if COT variables enter the model. In the provided 49-feature dataset they do not appear, so this is not a direct cause of the reported divergence.
- Fix: Put the observation on its public release date before forward-fill, or shift by the documented release lag.

### 5. Event alignment with `ffill_limit=0` will fail

- Function / lines: `fetch_block_a`, line 220, via `_align_daily` lines 91-112.
- What it does: Calls `_align_daily(df7, ffill_limit=0)` for the Fed surprise series.
- Why it is a bug: Pandas forward-fill `limit=0` is invalid in current pandas. The surrounding `try` catches the exception, so the variable silently disappears.
- Expected effect: Minor for this comparison because A7 is not in the provided 49-feature dictionary.
- Fix: For event variables, reindex without forward-fill or set non-event days to zero explicitly.

### 6. `G6_nfci` is weekly but aligned as monthly

- Function / lines: `fetch_block_g`, lines 840-848.
- What it does: Calls `_align_monthly(nfci.data, lag_bdays=5)` for a weekly NFCI series.
- Why it is a bug/suspect choice: Weekly data should have a weekly release/availability convention, not a 23-business-day monthly fill limit.
- Expected effect: Minor to moderate. It can carry stale NFCI values longer than intended and affect monthly/quarterly selection, where NFCI is selected in both teams' pipelines.
- Fix: Implement `_align_weekly` with source-appropriate release lag and fill limit.

### 7. Business-day index uses wall-clock "today"

- Function / lines: `_bdc_index`, lines 86-88; panel write in `run_acquisition`, lines 1273-1287; targets in `build_targets`, lines 1205-1218.
- What it does: Builds the panel through `pd.Timestamp.today()`.
- Why it is a bug/suspect choice: Re-running acquisition on a different date changes row count, terminal missingness, and hold-out boundary. Reproducibility depends on run date.
- Expected effect: Minor for backtests away from the end date; moderate for "latest 20%" hold-out boundaries.
- Fix: Pin an `end_date` parameter and write it into metadata.

## 3. Numerical reconciliation

All hit rates below are hold-out values. "Edge" is extreme hit rate minus middle hit rate.

| Horizon | Metric | Their report | My result | Delta |
|---|---:|---:|---:|---:|
| Weekly | Aggregate hit | 52.7% | 45.4% | +7.3pp |
| Weekly | Extreme hit | 64.6% | 46.4% | +18.2pp |
| Weekly | Middle hit | 49.8% | 45.1% | +4.7pp |
| Weekly | Extreme edge | +14.8pp | +1.3pp | +13.5pp |
| Monthly | Aggregate hit | 57.7% | 43.9% | +13.8pp |
| Monthly | Extreme hit | 70.4% | 58.6% | +11.8pp |
| Monthly | Middle hit | 54.6% | 40.2% | +14.4pp |
| Monthly | Extreme edge | +15.8pp | +18.4pp | -2.6pp |
| Quarterly | Aggregate hit | 58.8% | 50.2% | +8.6pp |
| Quarterly | Extreme hit | 70.1% | 66.7% | +3.4pp |
| Quarterly | Middle hit | 55.9% | 46.1% | +9.8pp |
| Quarterly | Extreme edge | +14.2pp | +20.6pp | -6.4pp |

### Why the weekly divergence is so large

The weekly divergence is not plausibly explained by ordinary random-seed noise. Their selected weekly feature set is different from mine, and their hold-out score is a different object:

- Their weekly score uses equal-weight signed z-scores from `compute_score_with_fixed_signs` (lines 704-715), while mine uses a final Elastic Net prediction/fallback from training-fitted robust-scaled selected variables.
- Their hold-out z-scores are standardized on the hold-out itself (lines 706-708 called from 912-915). Mine fits the scaler on the training set and applies it to hold-out.
- Their embedded selection is affected by full-sample imputation (lines 153-162), non-expanding early-window CV (lines 347-358), fold-leaky Elastic Net scaling (lines 382-387), and non-purged non-clustered MDA (lines 445-469).
- Their CV metrics validate an Elastic Net but the reported weekly hold-out extreme edge is produced by the separate equal-weight composite. This means the weekly "+14.8pp" is not the out-of-sample performance of the CV-validated model.

The most direct code-level account for weekly +14.8pp versus my +1.3pp is therefore: different score definition plus hold-out-fitted score standardization, with feature selection altered by the CV/MDA bugs. The hold-out self-standardization is especially relevant for extremes because it changes cross-feature scaling using the full 2022-2026 hold-out distribution before identifying top/bottom deciles.

### Other divergences

Monthly and quarterly also diverge in aggregate hit rate. The same bugs apply, but the edge comparison differs because my monthly/quarterly middle buckets were much weaker while my extreme buckets were closer to theirs. Their monthly and quarterly Sharpe numbers are also not comparable because of the `sqrt(252)` annualization bug; those Sharpe claims should be discounted heavily.

## 4. Methodology divergences, not necessarily bugs

- Feature coverage threshold: They drop features with less than 40% full-sample coverage; I used 20% training coverage plus uniqueness screens. Their 40% threshold is defensible as a stability choice, but computing it before the hold-out split is wrong.
- Filter threshold: They use Spearman `p < 0.15` or MI above the 10th percentile. I used `abs(rho) >= 0.03 and p <= 0.10`, or MI above the median positive MI. Their filter is looser; both are defensible as sub-choices if applied training-only, but theirs likely admits more noise.
- Granger: They compute a simplified Granger p-value but do not filter on it. This is harmless but adds no real protection.
- Standardization: They use mean/std; I used robust median/IQR. Both can be defensible. Their bug is fitting standardization on the scored dataset, including hold-out.
- Sign determination: They use first-half training Spearman signs. I use final Elastic Net coefficient signs, with Spearman fallback only when coefficients collapse. Their choice is defensible for a simple macro score, but then CV should validate that same signed-score procedure.
- Score construction: They use equal-weight signed z-scores. I use fitted Elastic Net predicted return. Both are plausible product-score choices. The bug is that their CV and hold-out evaluate different score definitions.
- CV fold geometry: They claim purged walk-forward with embargo. My folds are expanding walk-forward with a pre-validation purge and no post-validation embargo because training is historical only. Their implementation is rolling fixed-window and validates only a small early subset, so this is not just a defensible divergence.
- MDA: They claim clustered MDA. I implemented correlation-clustered permutation MDA over walk-forward validation folds. Their code performs ordinary permutation importance on one non-purged split, so this is a clear methodology violation.
- DSR trial count: They use raw feature count. I included filter variables, Elastic Net grid trials, Boruta iterations, and MDA clusters. Mine is more defensible for multiple-testing correction.
- Extreme threshold: Both use top decile plus bottom decile of hold-out scores. This is comparable in definition, but their underlying score is hold-out-standardized and mine is training-standardized/fitted.

## 5. Verdict per horizon

### Weekly

The weekly hit-rate claims cannot be trusted as stated. The +14.8pp extreme edge is produced by a hold-out-self-standardized equal-weight composite that is not the same model validated in CV, after feature selection affected by non-expanding CV and non-purged MDA. I would not cite the weekly extreme edge to subscribers.

### Monthly

The monthly hit-rate claims also cannot be trusted as stated. The aggregate and extreme hit rates may reflect a real regime-specific directional relationship, but the same score-standardization, model-mismatch, MDA, and Sharpe/DSR bugs apply. The reported 2.20 Sharpe is especially overstated because it is annualized as if 21-day forward returns were daily returns.

### Quarterly

The quarterly hit-rate claims are directionally less divergent at extremes, but still cannot be trusted as stated. The DSR=1.00 claim is under-corrected, the 4.78 Sharpe is inflated by roughly `sqrt(63)`, and the hold-out contains only about 17 non-overlapping quarterly observations. At most, this is a fragile scorecard lead, not a validated trade-idea signal.

## 6. Confidence

Confidence: 4/5. The main bugs are visible directly in the reviewed code and line up with the numerical divergences: hold-out-fitted standardization, model mismatch between CV and hold-out, non-expanding CV, non-clustered/non-purged MDA, and wrong Sharpe/DSR scaling. I am not at 5/5 because I did not read the forbidden diagnostic/run/validation files or rerun their pipeline end-to-end, and some acquisition lag issues depend on the exact date semantics of upstream raw files.
