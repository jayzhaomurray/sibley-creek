# USDCAD Replication Methodology v2

Implementation id: `chatgpt-codex-v2-2026-05-27`

This rerun corrects the known v1 and Sibley audit issues without overwriting prior outputs.

## Corrections

- Extreme thresholds are now fit on training composite scores and applied unchanged to hold-out.
- Hold-out imputation, scaling, sign determination, selection, and thresholding use no hold-out information.
- Score construction is a single coherent signed robust-z composite for both CV and hold-out.
- DSR is now a probability-style Bailey-Lopez de Prado approximation using per-period Sharpe, skew/kurtosis adjustment, and `n_trials = input features + embedded selection families`.
- Sharpe annualization uses `sqrt(252 / horizon_days)`.
- Clustered MDA uses direction-hit decrease rather than R2 decrease.

## Sub-choices

- Filter: training-only Spearman plus mutual information; `abs(rho) >= 0.03 and p <= 0.10`, or MI above median positive MI; coverage must be at least 20%.
- Embedded selection: Elastic Net CV, shadow-variable Boruta approximation with hit-rate threshold, and correlation-clustered MDA.
- Voting: at least two of three embedded votes; deterministic top-ranked fallback if fewer than three survive.
- CV: 10 expanding purged walk-forward folds on training data. CV uses final selected variables but fold-local scaling and signs, so it is a post-selection diagnostic. Hold-out is the binding test.
- Sign determination: Spearman sign on training data for final model; fold-local Spearman signs for CV.
- Score: mean of selected robust-z variables after multiplying by training-derived signs. Positive predicts USD/CAD up/CAD weakening.

## Horizon Summary

### Weekly

- Hold-out: 2022-01-24 to 2026-04-29
- Selected features: B1_wti, B2_brent, B4_bcpi_total, C4_equity_diff, F7_can_unemp, F8_us_unemp, G1_dxy, G2_reer
- Aggregate hit: 47.2%
- Extreme hit: 51.3% vs middle 45.5%
- Verdict: `do_not_ship`

### Monthly

- Hold-out: 2022-01-05 to 2026-04-07
- Selected features: A10_slope_spread, A1_2y_spread, A8_goc_2s10s, A9_ust_2s10s, B1_wti, B2_brent, B4_bcpi_total, F1_can_cpi_yoy, F3_us_cpi_yoy, F4_cpi_diff, F7_can_unemp, F8_us_unemp, G1_dxy, G2_reer
- Aggregate hit: 46.0%
- Extreme hit: 49.3% vs middle 45.2%
- Verdict: `do_not_ship`

### Quarterly

- Hold-out: 2021-11-19 to 2026-02-06
- Selected features: B1_wti, B2_brent, B4_bcpi_total, F1_can_cpi_yoy, F3_us_cpi_yoy, F4_cpi_diff, F5_can_gdp_yoy, F7_can_unemp, F8_us_unemp, G1_dxy, G2_reer
- Aggregate hit: 63.2%
- Extreme hit: 63.5% vs middle 63.1%
- Verdict: `scorecard_only`

