# Imputing the JVWS Apr–Sep 2020 gap with Indeed Hiring Lab

**Status:** research pass, not promoted to production.
**Run by:** `pipeline.research.indeed_jvws_imputation`
**Date:** 2026-05-11

## Plain-English summary (read this first)

StatCan's JVWS vacancy rate is missing six monthly observations (Apr–Sep 2020) because the survey was paused at the start of the pandemic. Indeed Hiring Lab's CA postings index covers that window. Over the **67 months of overlap** (Oct 2020 → Feb 2026, plus Feb–Mar 2020), a simple linear regression of JVWS on the Indeed index gives **R² = 0.81, RMSE = 0.47 pp, MAE = 0.35 pp**. The fit is **good on average but has clear regime structure**: residuals are systematically positive in 2020–22 (JVWS ran above what Indeed implied during the post-COVID rebuild) and systematically negative in 2024–26 (cooling). Durbin–Watson = 0.40 confirms strong residual autocorrelation.

The imputed trough is **1.45% in May 2020**, climbing to **2.30% by Sep 2020**. That shape is qualitatively right — vacancies collapse, then recover ahead of the JVWS resumption value of 3.9% in Oct 2020. An alternative index-scaling check (anchored to Mar 2020 JVWS = 3.2) puts the values 0.4–0.5 pp higher (1.87 → 2.67). The two methods agree on direction but disagree on level.

**My recommendation:** the fit is publishable *with* a methodology footnote, but the trough is the part most likely to be wrong, and that's the most narratively important part. The chart-level call depends on what the Beveridge curve is trying to show. See "Recommendation" at the end.

## Specification

OLS in levels on monthly data:

```
JVWS_vacancy_rate_t = a + b · Indeed_index_t  +  ε_t
```

Indeed series: `data/raw/indeed_postings_ca_monthly.csv` — Indeed Hiring Lab CA aggregate job postings (Feb 1 2020 = 100), daily collapsed to monthly mean before this script reads it.

JVWS series: `data/raw/job_vacancy_rate.csv` — StatCan Table 14-10-0325, vector v1212389365, monthly vacancy rate (% of labour force).

Overlap window: months where **both** series are observed = Feb 2020, Mar 2020, and Oct 2020 → Feb 2026 = 67 observations.

I considered but rejected:

- **Month-of-year fixed effects.** Both series are seasonally adjusted at source. Adding them risked overfitting on 67 obs.
- **First-differences regression.** Cleaner residuals theoretically, but the gap is six contiguous missing observations, so chaining first-difference predictions over the gap compounds error and pulls the imputed series back to wherever the chain starts. Levels regression sidesteps this.
- **ARIMA / state-space.** Overkill for a six-point fill where the simpler model already hits R² > 0.8.

## Fit quality

| Metric | Value |
|---|---|
| n | 67 |
| Intercept a | -0.523 |
| Slope b | 0.03675 |
| R² | 0.806 |
| MAE | 0.352 pp |
| RMSE | 0.466 pp |
| Durbin–Watson | 0.40 |

R² and MAE meet the brief's "ship-it" threshold (R² > 0.7, clean residuals). **DW = 0.40 does not** — that's strong positive autocorrelation, visible in `04_residuals.png` as two long sign runs (positive 2020–22, negative 2024–26). The residuals are not white noise; they're regime-structured.

## Imputed values

| Month | Indeed index | OLS imputation | Index-scaling alt |
|---|---|---|---|
| 2020-04 | 57.6 | **1.59** | 2.00 |
| 2020-05 | 53.8 | **1.45** | 1.87 |
| 2020-06 | 60.8 | **1.71** | 2.11 |
| 2020-07 | 67.9 | **1.97** | 2.36 |
| 2020-08 | 72.6 | **2.15** | 2.52 |
| 2020-09 | 76.8 | **2.30** | 2.67 |

Pre-pause anchor: Mar 2020 JVWS = 3.20. Post-pause anchor: Oct 2020 JVWS = 3.90.

## Honest caveats

1. **Extrapolation at the low end.** The lowest Indeed value in the fit sample is 82 (Oct 2020); we are pushing the model down to 54 (May 2020). Five of the six gap months sit *below* the fit support. Whatever non-linearity exists at the very bottom of the vacancy distribution, the OLS line cannot see it.

2. **Regime instability.** The relationship between JVWS and Indeed shifted across the sample. In 2020Q4–2021, JVWS climbed *faster* than Indeed implied (residuals up to +1.4 pp), consistent with broad labour-market re-opening pulling all-sector vacancies up faster than the Indeed-coverage tilt toward services. In 2024–26, JVWS is falling *faster* than Indeed implies (residuals around -0.7 to -0.85 pp). The Apr–Sep 2020 window sits at the regime boundary — it is plausibly in a third regime (collapse) not represented in the fit at all.

3. **Coverage mismatch.** Indeed indexes posting *volume* on its own platform, which over-weights services and tech relative to JVWS's all-employer vacancy *stock*. This is the structural reason the fit is not 1:1 across cycles.

4. **Stock vs flow.** JVWS measures vacancy *stock* (positions open on the reference day). Indeed measures *postings active* (a flow-leaning concept). In a sudden labour-demand collapse, postings can fall faster than stock (employers pull listings before formally cancelling roles). The imputed trough of 1.45% may therefore be **too low** — the actual JVWS stock at the time may not have fallen as far as the Indeed flow suggests.

5. **No standard errors on the imputed points.** RMSE of 0.47 pp gives a rough ±1 pp confidence band on any individual prediction. For a Beveridge-curve visualisation, that's wide enough to matter at the scale where we're plotting.

## Recommendation

**Two defensible options:**

- **A. Use the imputed series with a clear annotation.** Plot the Apr–Sep 2020 points as open markers or in a distinct colour and add a chart note: "Apr–Sep 2020 imputed from Indeed Hiring Lab CA postings (R²=0.81 on Oct-2020 → present); StatCan JVWS paused." This makes the chart visually complete and the pandemic loose-quadrant excursion readable, at the cost of asking the reader to trust the imputation for the most extreme part of the move.

- **B. Leave the gap, label it as a gap.** Most defensible on first-principles terms; matches how the BLS/StatCan houses themselves handle the pause. The chart caption notes that vacancies were not surveyed during the deepest part of the COVID labour shock; the unemployment spike to 13% stands alone in the U-half of the plot.

If the Beveridge curve is positioned as **a quantitative artefact people will read levels from**, choose B. If it's positioned as **a narrative chart where the shape of the COVID excursion is the point**, choose A — the imputed shape (sharp drop, fast partial recovery) is qualitatively right even if the trough level is uncertain.

My lean is A with an annotation, because the alternative (skipping the trough entirely) actually *understates* the pandemic story in a way that's also misleading. But this is an editorial call, not a statistical one.

## Files

- Script: `pipeline/research/indeed_jvws_imputation.py`
- Derived CSV: `data/derived/jvws_vacancy_rate_imputed.csv` (columns: `date`, `jvws`, `indeed`, `jvws_imputed`, `imputation_source` ∈ {`observed`, `imputed_ols_levels`, `missing`})
- Plots: `editorial/research/indeed_jvws_imputation/0{1..5}_*.png`
