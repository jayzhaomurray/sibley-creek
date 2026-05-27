# USDCAD Replication Methodology

Implementation id: `chatgpt-codex-2026-05-27`

## Data and Hold-out

I used only `data/processed/usdcad_variables.parquet` and `data/processed/usdcad_targets.parquet`. For each horizon I sorted by date, dropped rows with missing target return or direction for that horizon, and reserved the most recent 20% as a clean hold-out before any filtering, scaling, selection, sign determination, or fitting.

## Sub-choices

- Filter method: Spearman rank correlation against forward log return plus mutual information regression on the training set only.
- Filter threshold: keep a variable if `abs(Spearman rho) >= 0.03` and `p <= 0.10`, or if mutual information is positive and at or above the median positive MI among usable variables. Variables with less than 20% training coverage or fewer than three unique observed values are removed. If fewer than five variables survive, a deterministic top-five rank by univariate evidence is used so the downstream composite remains estimable.
- Imputation: training median imputation. Features with all-missing training values receive zero after the coverage filter removes them.
- Standardization: robust z-score, `(x - training median) / training IQR`, fit on training data only.
- Embedded selection: Elastic Net CV, Boruta-style shadow-variable random forest, and clustered MDA.
- Voting rule: selected features must pass the filter and receive votes from at least two of the three embedded methods. If fewer than three survive, the highest-ranked filtered variables by votes, Spearman strength, Boruta importance, and MDA importance are used as a deterministic fallback.
- Cross-validation: 10 expanding walk-forward folds on the training sample.
- Purge rule: observations in the forecast horizon immediately before each validation block are removed from that fold's training set, so a training label cannot overlap the validation period.
- Embargo: zero extra days after validation because every fold trains only on history before the validation block; the historical-only split already prevents training on post-validation information.
- Sign determination: the final elastic-net coefficient sign defines the feature sign. If all coefficients shrink to zero, Spearman sign is used as a documented fallback.
- Score construction: final selected robust-z features feed a final Elastic Net regression for forward log return. The predicted return is the composite score. Positive means USD/CAD up, i.e. CAD weakening; negative means CAD strengthening.
- Extreme threshold: bottom decile plus top decile of hold-out scores for each horizon, evaluated once.
- Multiple testing correction: approximate Bailey-Lopez de Prado Deflated Sharpe Ratio using the purged-CV annualized Sharpe, the number of CV-predicted observations, and an explicit independent-trial count equal to one final model plus filtered variables plus elastic-net alpha/l1 trials plus Boruta iterations plus MDA clusters.

## Deviations and Practical Approximations

Boruta is implemented directly with shadow variables and random forests rather than through an external Boruta package. Clustered MDA uses absolute-correlation clusters and validation-block permutation decreases in R². The DSR uses the standard normal approximation to the expected maximum Sharpe under multiple independent trials; it is conservative for weak signals but still an approximation because exact independent trial dependence is not observable from this one run.

## Horizon Summary

### Weekly

- Training window: 2005-01-03 to 2022-01-21
- Hold-out window: 2022-01-24 to 2026-04-29
- Features after filter: 28
- Final selected features: A10_slope_spread, A1_2y_spread, A8_goc_2s10s, A9_ust_2s10s, B1_wti, B2_brent, B4_bcpi_total, C4_equity_diff, F14_oecd_cli_can, G1_dxy, G2_reer, I2_dist_200dma, I9_beta_dxy
- Verdict: `do_not_ship`

### Monthly

- Training window: 2005-01-03 to 2022-01-04
- Hold-out window: 2022-01-05 to 2026-04-07
- Features after filter: 32
- Final selected features: A10_slope_spread, A11_real_rate_spread, A1_2y_spread, A8_goc_2s10s, A9_ust_2s10s, B1_wti, B2_brent, B4_bcpi_total, F1_can_cpi_yoy, F3_us_cpi_yoy, F4_cpi_diff, G1_dxy, G2_reer, H2_epu_us, I9_beta_dxy, J3_housing_starts, L4_tips_5y5y
- Verdict: `do_not_ship`

### Quarterly

- Training window: 2005-01-03 to 2021-11-18
- Hold-out window: 2021-11-19 to 2026-02-06
- Features after filter: 34
- Final selected features: B11_ovx, B1_wti, B2_brent, B4_bcpi_total, C1_vix, F14_oecd_cli_can, F5_can_gdp_yoy, F7_can_unemp, F8_us_unemp, G1_dxy, G2_reer, G6_nfci, I1_ret_252d, I2_dist_200dma, I3_rvol_10d, I3_rvol_30d, I3_rvol_60d, J3_housing_starts
- Verdict: `scorecard_only`

