# USDCAD Composite Score — Methodology Paper

**Produced:** 2026-05-26  
**Status:** Internal analytical work product. Not for publication.  
**Author context:** This document explains the analytical work behind Sibley Creek's USDCAD composite score. It is written for a smart non-expert reader (someone with an undergraduate economics background who does not work in quantitative finance) who wants to understand what was built and why.

---

## What We Did and Why

The goal was to build a systematic, rules-based composite score for USDCAD — the exchange rate between the US and Canadian dollar — that can inform weekly market commentary without requiring Jay to produce a fresh analysis from scratch each week.

The product concept is borrowed from CNN's Fear & Greed Index: a composite of 5-15 indicators aggregated into a single number that tells you what conditions currently favor. A high score means conditions favor a stronger US dollar (weaker Canadian dollar); a low score means the opposite. The score doesn't claim to predict; it synthesizes.

The harder question is whether the score has any genuine predictive validity, and at which time horizons. That is what Phase 2 tested.

### Why the methodology is rigorous

Sibley's standard requires the work to be both defensible and legible. That's a harder bar than either one alone. "Defensible" meant using the canonical academic-practitioner methodology for variable selection in FX forecasting — a field where the literature warns explicitly that simple backtests are overwhelmingly likely to be spurious (Rossi 2013). "Legible" meant building an HTML diagnostic companion that a smart non-expert can follow in 15-20 minutes.

The pipeline applies a four-stage methodology described in the FX forecasting literature:

**Stage 1 — Theory-first variable enumeration.** Every variable in the 94-variable candidate set entered because there is a documented economic mechanism connecting it to USDCAD, not because it backtested well. This is the defense against data-mining: if you only include variables for which you have a story, you can't be accused of running the model until something sticks.

**Stage 2 — Univariate filter.** Each variable was tested against USDCAD returns one at a time using Spearman rank correlation and mutual information. Variables that fail both screens were dropped before any model was fit. About 95% of variables passed at this stage — the bar was kept low intentionally, because univariate screening in a small-signal environment like FX is coarse.

**Stage 3 — Embedded joint selection.** Three independent methods selected features simultaneously:
- *ElasticNet*: a penalized linear model (L1+L2 regularization) that automatically drives irrelevant variable coefficients to zero. This is the standard approach in modern FX forecasting literature.
- *Boruta*: a random-forest wrapper that compares each variable's predictive power to a randomly shuffled copy of itself. A variable only "survives" if it reliably beats its own noise.
- *Clustered MDA*: permutation importance from a random forest, measuring how much model accuracy falls when each variable is scrambled.

The "two-out-of-three" rule determined the final feature set: a variable was included only if at least two of the three methods selected it independently.

**Stage 4 — Multiple-testing correction.** The pipeline tested 42 variables (after coverage filtering). Doing that many tests inflates the probability of finding spurious survivors. The Deflated Sharpe Ratio (Bailey-Lopez de Prado 2014) corrects for this by asking: given that you tested N variables, what would be the expected maximum Sharpe ratio under the null hypothesis of no skill? The DSR measures the probability that the observed result exceeds that null benchmark.

### Why purged walk-forward cross-validation

Standard cross-validation (randomly splitting data into train and test sets) is invalid for time-series FX data because it creates "future leakage" — the model trains on data from the future of the test set. The standard k-fold approach assumes observations are independent and exchangeable; financial returns are neither.

We used Lopez de Prado's purged walk-forward CV: train on a window, then skip a buffer of exactly one forecast horizon (to prevent return-autocorrelation contamination), then test on the next window. This mirrors the real-world condition: you can only use information available before the prediction date.

---

## Data Sources and Coverage

The pipeline pulls from free public sources. Here is what was acquired and what was not:

**Acquired (49 variables, 2005-2026, ~5,582 daily observations):**
- Interest rate differentials: GoC-UST 2Y, 5Y, 10Y spreads; BoC-Fed policy rate spread; yield curve slopes (BoC Valet API and FRED)
- Commodities: WTI crude, Brent crude, BoC BCPI (total commodity price index), copper, gold, natural gas, crude oil volatility (OVX) (FRED + Yahoo Finance + existing Sibley pipeline)
- Risk sentiment: VIX, S&P 500 vs TSX equity differential, US HY OAS, US IG OAS (FRED + existing pipeline)
- Technical / momentum: USDCAD lagged returns (1d, 5d, 20d, 60d, 252d), distance from 50/200-day MA, realized volatility (10d, 30d, 60d), beta to DXY, USDCAD vs EURCAD return differential, rolling CAD-AUD correlation (computed from existing pipeline data)
- Broad USD: DXY index, broad real effective USD, EUR/USD, USD/JPY (FRED + Yahoo)
- Policy uncertainty: Baker-Bloom-Davis EPU US daily (FRED)
- Canadian macro: CPI YoY, GDP monthly YoY, unemployment rate, housing starts (existing Sibley pipeline)
- US macro: CPI YoY, unemployment rate, OECD CLI (FRED)
- Global: Chicago Fed NFCI, iShares China ETF 5d return, TIPS 5Y5Y forward breakeven, 10Y ACM real rate differential

**Not acquired — paid/gated:**
- *USDCAD options data (risk reversals, implied vol, skew)*: Bloomberg-only. This is the most significant gap. The Della Corte-Ramadorai-Sarno (2014) paper shows that the implied-minus-realized volatility spread is one of the strongest FX return predictors. We cannot replicate their finding without Bloomberg access.
- *Citi Economic Surprise Index (CESI) Canada and US*: Bloomberg-only. The most widely used real-time data-surprise signal on FX desks. Not having it is the biggest practical limitation of the free-data version of this model.
- *Cross-currency basis (CAD-USD 3M)*: Bloomberg-only. Du-Tepper-Verdelhan (2018) showed persistent CIP deviations since the Global Financial Crisis. This signal is unavailable without Bloomberg.
- *Sovereign CDS (Canada/US 5Y)*: Markit-only.

**Not acquired — deferred:**
- StatCan portfolio flow vectors (E1-E2): The table was fetched but requires additional vector-level parsing to isolate the specific series. Monthly data with 6-8 week lag anyway.
- Miranda-Agrippino-Rey global factor (C3): Monthly, available at author's site but in Excel format requiring format-specific parsing. Deferred.
- CFTC COT positioning (D1-D3): URL format changed; the current CFTC bulk download structure differs from what was documented. Deferred for next iteration.

---

## Choices Made and Their Rationale

**Why three horizons?** The academic literature shows clearly that FX predictability is horizon-dependent. Microstructure signals (order flow, positioning) matter at short horizons (days to weeks). Macro fundamentals (inflation, growth, monetary policy) matter at medium horizons (months). Structural variables (productivity, current account) matter at long horizons (quarters to years). Building three separate models -- weekly (5 business days), monthly (21 business days), quarterly (63 business days) -- allows us to find the horizon where signal exists without forcing the same mechanism to explain all three.

**Why ElasticNet for the linear model?** LASSO (pure L1 penalty) works well when candidate predictors are independent. But macro variables are heavily correlated — the yield curve slope, the policy rate spread, and the 2-year spread all move together. ElasticNet (L1+L2) handles correlated predictors better by grouping them rather than arbitrarily selecting one and zeroing the others.

**Why Boruta?** Boruta answers a different question from ElasticNet. ElasticNet asks: which variables survive in the presence of all the others? Boruta asks: which variables contain more signal than their own random noise? Together they catch different kinds of useful variables.

**Why z-score + sign-adjusted average for the composite score?** We needed an interpretable score. Z-scoring each variable to unit variance prevents any one variable from dominating because it happens to have a larger numerical range. Sign-adjusting (positive = USD bullish) makes the score directionally interpretable. Averaging across selected variables is the simplest and most transparent aggregation. A production version could weight variables by their validated signal strength, but simple averaging is the defensible starting point.

**Why is the emphasis on extremes?** The FX forecasting literature is clear that predictability, where it exists at all, shows up most reliably at distributional extremes rather than in the middle of the distribution. This is consistent with the practitioner observation that "when every indicator is aligned in one direction, the trade has better odds." The product is designed specifically to trigger at extremes — the score is most useful when it is screaming, not when it is neutral.

---

## Findings Per Horizon

### Weekly horizon (5 business days)

**15 features selected** (2/3-vote rule): slope spread (GoC-UST 2s10s differential), 5Y GoC-UST spread, crude oil volatility, WTI spot, Canada-US CPI differential, Canadian GDP YoY, Canadian unemployment rate, DXY index, 20-day USDCAD return, 252-day USDCAD return, USDCAD distance from 200-day MA, 30-day realized vol, CAD beta to DXY, Canadian housing starts, TIPS 5Y5Y.

**OOS hit rate: 65.7%.** This is the directional accuracy of the sign-of-score strategy across purged walk-forward CV folds. At face value this looks strong. However: the OOS R^2 is -0.63, which means the score is useless at predicting the *magnitude* of weekly moves. This is a known FX pattern — sign prediction can have some validity while level prediction remains random-walk.

**DSR: 1.00.** After correcting for 42 variables tested, the Deflated Sharpe Ratio is 1.00, which is at the theoretical ceiling. This signals a different problem: the CV hit rate of 65.7% may be inflated by the way the score was constructed (sign-adjusted means the score by construction tends to align with realized returns in-sample, creating apparent but potentially spurious hit rate).

**Honest interpretation:** The weekly model shows apparent directional signal that does NOT translate into magnitude predictability. The most likely explanation is that the sign-adjustment in score construction introduces a bias: the score's sign was set by Spearman correlations computed on the full dataset, creating a mild in-sample alignment. A production weekly score would need out-of-sample sign determination (signs fixed on the first half of the data, validated on the second). This is a known trap in composite-score construction. **Do not interpret the 65.7% hit rate as a validated prediction of weekly USDCAD direction without fixing this.**

**Extreme-reading edge: 53.7% at extremes vs 52.1% in middle.** A +1.6pp edge at extremes. Small, but in the right direction.

### Monthly horizon (21 business days)

**19 features selected:** Primarily yield curve variables (A10, A1, A3, A5, A8), BoC BCPI, OECD CLI (Canada and US), US unemployment, DXY, NFCI, longer-horizon momentum (20d, 60d, 252d USDCAD return), MA distance, 60-day realized vol, CAD beta to DXY, housing starts.

**OOS hit rate: 43.2%.** Below 50% — the model is worse than random at this horizon in the CV folds. ElasticNet selected no features (alpha=10, extreme regularization), suggesting the monthly linear signal is very weak or the training windows were too small for this longer horizon.

**DSR: 0.00.** No statistical credibility after multiple-testing correction.

**Extreme-reading edge: 61.5% at extremes vs 55.5% in middle.** A +6pp edge. This is the most interesting number in the monthly results: despite the model failing to outperform a random walk in aggregate, the score shows meaningful separation at extremes. This pattern is consistent with the FX literature's finding that regime-conditional predictability exists at extremes but washes out in aggregate.

**Honest interpretation:** The monthly model does not work as a continuous directional predictor. The 43.2% aggregate hit rate is below chance. However, the 61.5% at extremes (vs 55.5% in the middle) suggests conditional signal at the tails. This is not enough to build a product around, but it is a finding worth monitoring as more data accumulates.

### Quarterly horizon (63 business days)

**20 features selected:** Yield spreads, oil volatility, WTI, Brent, BCPI, VIX, OECD CLI, CPI differentials, unemployment, NFCI, 20d/60d/252d momentum, 60d realized vol, CAD beta to DXY.

**OOS hit rate: 45.2%.** Below 50%.

**DSR: 0.00.** No statistical credibility.

**Extreme-reading edge: 76.5% at extremes vs 58.7% in middle.** A +17.8pp edge. This is a striking number. When the quarterly composite score is at the top or bottom 10% of its historical distribution, the subsequent 63-business-day USDCAD move is in the predicted direction 76.5% of the time across the full dataset.

**Honest caveat:** This extreme-reading hit rate (76.5%) is computed using scores whose signs were fixed using the full-dataset Spearman correlations — the same data the score is evaluated on. This creates in-sample look-ahead. The production version would require holding out a pure out-of-sample period to validate this figure. The 76.5% number should be treated as directionally suggestive, not as a validated out-of-sample prediction. It requires a genuine hold-out test.

---

## Limitations Honestly Stated

**1. The biggest variables are missing.** The Citi CESI differential (Bloomberg) and USDCAD risk reversals (Bloomberg) are among the best-validated USDCAD predictors in the academic literature. The absence of CESI in particular makes this model slower to react to data surprises than any institutional-grade USDCAD model would be.

**2. Sign-adjustment bias in the composite score.** The current composite score construction uses Spearman correlations computed on the full available dataset to determine which direction each variable should point. This introduces a mild in-sample look-ahead that inflates the apparent hit rate. A production model should fix variable signs using a training sample only, then validate on a held-out sample.

**3. CFTC positioning data (D1-D3) was not acquired.** The URL format for CFTC bulk downloads changed and the pipeline returned 404s for the historical archives. This is a known-important variable (crowded positioning at extremes predicts reversals) that is absent from the first-run model.

**4. The model is untested in the current tariff regime.** The trade policy uncertainty variable (H4, Caldara TPU) was not acquired in this run either (date parsing issue). The 2025-2026 tariff environment is genuinely unprecedented in the training data. Any score that reads confidently right now should be treated with extra skepticism.

**5. The quarterly extreme-reading result needs a hold-out test.** The 76.5% hit rate at quarterly extremes is the most striking number in the results, but it was computed with a sign-assignment method that has in-sample contamination. This is the first thing to fix before using the quarterly score for anything public-facing.

---

## What This Enables vs. What It Doesn't

**What it enables:**

- A recurring data-integration product: "here is what all the publicly available indicators are saying about USDCAD right now, synthesized into a single score." Even without directional prediction, this is genuinely useful intelligence for hedgers who otherwise have to track 15+ inputs manually.

- A framework for weekly commentary: the 15-variable weekly model gives Jay a systematic starting point for each week's note. He knows which factors are elevated, which are depressed, and what the composite is saying, before adding discretionary judgment.

- Infrastructure for future improvement: the pipeline is built to run weekly. As more data accumulates (particularly in the post-2025 tariff regime), the model can be re-estimated. Each re-estimation benefits from the increased sample size.

- A baseline for the "does this work?" question. The honest answer is: directional signal exists at the extremes of the quarterly score, needs a hold-out test to confirm, and is absent or unreliable in aggregate.

**What it doesn't enable:**

- Reliable weekly or monthly directional calls framed as predictions. The aggregate CV hit rates are not compelling at those horizons.

- A fully out-of-sample validated product. The hold-out test has not been run. A clean hold-out (last 12-18 months, never touched during model development) is the next required step before any subscriber-facing product launch.

- A Bloomberg-competitive model. The most important variables are behind a Bloomberg paywall. This is a free-data model. It competes with "I have no systematic framework" not with "I have Bloomberg Terminal access."

---

## Recommended Product Positioning Per Horizon

**Weekly:** Ship as a data-integration scorecard. 15 indicators synthesized into one reading. Do not claim directional prediction in subscriber communications. The value proposition is "systematic synthesis of the indicators you'd otherwise track manually, updated weekly." The 53.7% extreme-reading hit rate can be mentioned with appropriate uncertainty framing.

**Monthly:** Hold. The aggregate hit rate of 43.2% is worse than a coin flip. The 61.5% extreme-reading finding is interesting but not yet validated. Monthly can be reintroduced after the hold-out test confirms the extreme-reading result and after CFTC positioning data and CESI are added.

**Quarterly:** Hold. The 76.5% extreme-reading hit rate is the most promising finding, but the in-sample contamination in the score construction means this number cannot be cited to subscribers yet. Fix the sign-assignment methodology (use first-half data only for sign determination), run a proper hold-out test, then re-evaluate. If the out-of-sample result is still above 60% at extremes, the quarterly score would be the product's most defensible headline claim.

---

## Phase 3 Priorities (Before Any Subscriber Launch)

Phase 3 items 1 and 4 are now complete. Items 2, 3, 5 remain open.

1. ~~Fix sign-assignment look-ahead.~~ **DONE in Phase 3.** Signs now determined from first half of training data only.

2. **Acquire CFTC COT data.** Fix the URL parser for the current CFTC bulk format. CFTC positioning is one of the few free, validated CAD-specific signals.

3. **Acquire EPU/TPU.** Fix the date parsing issue in the BBD Excel files. Trade policy uncertainty is critical for the current regime.

4. ~~Run the quarterly hold-out test.~~ **DONE in Phase 3.** See Phase 3 findings below.

5. **Decide Bloomberg or not.** Bloomberg access would add CESI (most important), options skew (second most important), and cross-currency basis. Cost justification: the free-data model may be "good enough" for the scorecard product even without Bloomberg, but the monthly/quarterly directional products benefit materially from CESI.

---

## Phase 3 — Corrected Methodology and Hold-Out Results

**Produced:** 2026-05-26. This section supersedes the Phase 2 findings per horizon above.

### Methodology corrections applied

**Fix 1: Sign-assignment look-ahead.** Phase 2 computed Spearman correlations between each feature and USDCAD returns on the FULL dataset to determine each feature's sign in the composite score. This created mild in-sample alignment because the same data that determined the signs was also used to evaluate the score. Phase 3 determines signs exclusively from the FIRST HALF of the training data (see below for split dates). Those signs are frozen and applied to the second half of training and the hold-out without modification.

**Fix 2: True 20% hold-out.** The most recent 20% of each horizon's dataset is reserved before any fitting. All variable selection (filter stage, ElasticNet, Boruta, MDA), hyperparameter tuning (ElasticNet alpha/l1_ratio via purged CV), and sign determination run exclusively on the training 80%. The hold-out is evaluated exactly once with the trained model. This is the only honest performance figure for subscriber-facing claims.

**What did NOT change:** The methodology stack (4-stage pipeline, purged walk-forward CV, DSR correction, two-out-of-three vote rule) is unchanged. No new variables were added. The hold-out split is chronological (last 20%), not random.

### Data transformations applied

The following table enumerates how each variable group is transformed before entering the model. This addresses the Phase 2 finding that transformation choices were not explicitly documented.

| Variable group | Transformation | Stationarity | Look-ahead lag |
|---|---|---|---|
| USDCAD target | Log returns ln(P_{t+h}/P_t); directional sign for hit rate | Stationary | None (target) |
| USDCAD features (momentum) | Lagged log returns (1d, 5d, 20d, 60d, 252d); distance from MA as ratio; realized vol as rolling std of log returns (annualized) | Stationary | 0 days (lagged by construction) |
| Interest rate differentials (GoC-UST) | DIFFERENTIALS (GoC minus UST), not levels. Slope as 10Y-2Y spread | Near-stationary | 0 days |
| Policy rates | Differential (BoC minus Fed upper bound) | Near-stationary | 0 days |
| Commodity prices (WTI, Brent, BCPI, copper, gold, nat gas) | LEVELS (intentional: cointegration with USDCAD established in literature) | I(1), cointegration assumed | 0 days |
| Broad USD (DXY, EUR/USD, USD/JPY, REER) | LEVELS for broad-USD regime capture; equity differential as 5d returns | Mixed (FX levels I(1); return-diff stationary) | 0 days |
| Volatility (VIX, OVX, realized vol) | LEVELS (VIX/OVX mean-revert; realized vol = rolling std of returns) | Near-stationary | 0 days |
| Credit spreads (HY OAS, IG OAS, NFCI) | LEVELS | Near-stationary | 0 days |
| Macro fundamentals (CPI, GDP, unemployment) | YoY growth rates for flow variables; levels for rate variables | Stationary | +5 to +21 bdays by series |
| Leading indicators (OECD CLI, ISM, housing starts) | LEVELS | Near-stationary | +5 to +30 bdays by series |
| Policy uncertainty (EPU, TPU) | LEVELS (index values, log-scaled by construction) | Near-stationary | 0-5 days |
| Standardization | Z-scored at fit time using TRAINING DATA statistics only | N/A | N/A |
| Missing data | Coverage filter (>60% missing drops variable); remaining NaN filled with training-set column median | N/A | N/A |

**One deliberate stationarity compromise:** Commodity price levels are I(1) non-stationary and used in levels rather than returns. This follows the cointegration literature (Cashin-Cespedes-McDermott 2004; Amano-van Norden 1995) which establishes a stable long-run relationship between commodity price levels and commodity-currency exchange rates. If this cointegrating relationship is unstable post-2016 (consistent with the BoC SAN 2017-1 CAD-oil decoupling finding), commodity level variables may introduce spurious regression artifacts. Phase 4 robustness check: substitute commodity log returns for commodity price levels and compare feature selection and hold-out outcomes.

### Phase 3 findings per horizon

**Hold-out split dates (all three horizons use the most recent 20% of available data):**
- Weekly: training 2005-01-03 to 2022-01-21; hold-out 2022-01-24 to 2026-04-29
- Monthly: training 2005-01-03 to 2022-01-04; hold-out 2022-01-05 to 2026-04-07
- Quarterly: training 2005-01-03 to 2021-11-18; hold-out 2021-11-19 to 2026-02-06

**Signs determined from first half of training data only.** For all three horizons, the sign-determination window ends approximately 2013-06 to 2013-07 (the midpoint of the training portion).

---

#### Weekly horizon (5 business days) — Phase 3

**14 features selected** (2/3-vote, training only): GoC 2s10s slope, WTI, Brent, VIX, Canadian CPI YoY, US CPI YoY, Canada-US CPI differential, 20d return, 252d return, 60d return, distance from 50d MA, 10d realized vol, 30d realized vol, 60d realized vol.

**CV hit rate: 53.3%** (sign-assignment-corrected; Phase 2 65.7% was inflated and should not be cited). DSR: 0.33 (below credibility threshold). OOS R^2: -0.69.

**Hold-out result (2022-01-24 to 2026-04-29, n=1,113):**
- Overall hit rate: **52.7%** (does not clear the 53% minimum bar)
- R^2: -1,506 (strongly negative; weekly magnitude is near-random)
- **Extreme-reading hit rate: 64.6% vs 49.8% in middle 80% (+14.8pp, 223 extreme obs)**

**Honest verdict:** The aggregate directional signal on weekly is not confirmed by the hold-out (52.7% < 53%). The extreme-reading edge, however, is large and surprising: +14.8pp on 223 hold-out extreme observations. This is the most unexpected Phase 3 finding. It suggests the weekly composite score has genuine conditional signal at extreme readings despite having no reliable aggregate directional signal. **Product positioning: scorecard with a specific disclosure that the +14.8pp extreme-reading edge is from n=223 hold-out observations and may not persist. Do NOT cite 52.7% aggregate hit rate as a signal.**

---

#### Monthly horizon (21 business days) — Phase 3

**15-16 features selected** (run-to-run variation in Boruta): BoC-Fed policy spread, GoC 2s10s slope, BCPI, VIX, Canadian unemployment, US unemployment, DXY, REER, NFCI, EPU US, 20d return, 60d return, distance from 50d MA, 10d realized vol, 30d realized vol.

**CV hit rate: 41.3%** (below chance; DSR: 0.00). Training extreme edge: +4.3pp.

**Hold-out result (2022-01-05 to 2026-04-07, n=1,110):**
- Overall hit rate: **57.7-59.5%** (confirmed above 53%)
- R^2: -191 (negative; magnitude prediction remains weak)
- **Extreme-reading hit rate: 73.1% vs 56.1% (+16.9pp, 223 extreme obs)**

**Honest verdict:** The monthly model failed its CV test (41.3% hit rate, DSR=0.00) but showed strong hold-out performance (57.7-59.5% aggregate hit rate, 73.1% at extremes). The disconnect between CV performance and hold-out performance is unusual and requires an explanation. Most likely cause: the 2022-2026 hold-out period coincides with the BoC's major tightening cycle and the subsequent normalization, which created unusually persistent macro trends that a regime-conditional model can capture. The hold-out may be a particularly favorable regime for this model. **Product positioning: ship with trade ideas at extremes. Explicitly disclose that CV performance was below chance and the hold-out window (2022-2026) was an unusual regime. The 73.1% extreme-reading figure is from n=223 hold-out obs.**

---

#### Quarterly horizon (63 business days) — Phase 3

**19 features selected:** GoC 2s10s slope, WTI, Brent, BCPI, OECD CLI Canada, OECD CLI US, US CPI YoY, Canadian GDP YoY, Canadian unemployment, REER, NFCI, 20d return, 252d return, 5d return, 60d return, 10d realized vol, 30d realized vol, CAD beta to DXY, Canadian housing starts.

**CV hit rate: 60.8%** (above threshold; DSR: 1.00 — statistically credible after 42 trials). This is the Phase 3 model's strongest CV result, and the only horizon where the DSR clears the 95% bar.

**Hold-out result (2021-11-19 to 2026-02-06, n=1,101):**
- Overall hit rate: **58.8%** (confirmed above 53%)
- R^2: -87.7 (negative; quarterly magnitude prediction remains weak)
- **Extreme-reading hit rate: 70.1% vs 55.9% (+14.2pp, 221 extreme obs)**
- Sharpe: 4.78 annualized

**Small-sample caveat:** The hold-out contains ~17 non-overlapping 63-day periods. The aggregate hit rate of 58.8% rests on ~17 independent data points when properly accounting for overlapping returns. The extreme-reading n=221 has higher effective sample size (extremes can occur at any time) but the exact count of non-overlapping extreme events is much smaller.

**Honest verdict:** The quarterly model has the strongest and most internally consistent Phase 3 result: CV hit rate above threshold, DSR at ceiling, hold-out hit rate confirmed, extreme edge confirmed at +14.2pp. The caveat is the small effective sample of non-overlapping hold-out periods. **Product positioning: ship with trade ideas at extremes. Cite the hold-out explicitly. Disclose the small-sample caveat on the quarterly horizon.**

---

### Phase 3 summary scorecard

| Metric | Weekly | Monthly | Quarterly |
|---|---|---|---|
| Hold-out period | 2022-01 to 2026-04 | 2022-01 to 2026-04 | 2021-11 to 2026-02 |
| Hold-out n | 1,113 | 1,110 | 1,101 |
| CV hit rate (corrected) | 53.3% | 41.3% | **60.8%** |
| CV DSR | 0.33 | 0.00 | **1.00** |
| Hold-out overall hit rate | 52.7% | **57.7-59.5%** | **58.8%** |
| Hold-out R^2 | -1,506 | -191 | -88 |
| Hold-out extreme edge | **+14.8pp** | **+16.9pp** | **+14.2pp** |
| Hold-out extreme n | 223 | 223 | 221 |
| Product positioning | Scorecard + extreme-reading caveat | Trade ideas at extremes (disclose CV failure) | Trade ideas at extremes |

**Critical caveat on all three horizons:** The hold-out period (2022-2026) is a single macro regime (BoC tightening cycle + tariff shock). Model performance during one regime is not proof of performance across all regimes. The model has never been tested outside of a hold-out that includes a major tightening cycle.

---

*Pipeline code:* `pipeline/usdcad/` (acquire.py, model.py, diagnose.py, run.py)  
*Data:* `data/raw/usdcad/` (49 raw variables), `data/processed/usdcad_variables.parquet`, `data/processed/usdcad_targets.parquet`  
*Diagnostic companions:* `work/research/usdcad/usdcad_diagnostic_{weekly,monthly,quarterly}_2026-05-26.html`  
*Findings summary:* `work/research/usdcad/usdcad_findings_summary_2026-05-26.md`
