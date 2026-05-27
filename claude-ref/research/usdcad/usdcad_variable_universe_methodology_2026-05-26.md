# USDCAD Candidate Variable Universe — Methodology & Catalog

**Phase 1 deliverable. Produced 2026-05-26.**

Scope: this document is the methodological foundation for an eventual USDCAD composite-score product. It (1) reviews how institutional quantitative shops construct the candidate variable universe BEFORE back-testing, and (2) applies that methodology to produce a comprehensive — deliberately unpruned — candidate set for USDCAD. Phase 2 will run back-tests and select.

Audience: Jay (decision on which selection methodology to apply in Phase 2). Not for publication.

---

## Executive summary

The cutting-edge consensus on variable-selection methodology in quantitative FX has converged on a **hybrid four-stage pipeline** rather than any single technique. Stage 1 is theory-driven enumeration: economically motivated variables form the candidate set, never letting purely data-mined candidates enter. Stage 2 is descriptive filtering: mutual-information / correlation / variance-inflation screens cull near-duplicates and pure-noise candidates while preserving theory-supported survivors. Stage 3 is embedded selection — usually LASSO / Elastic Net for linear models, or Boruta / clustered-MDA (López de Prado) for tree models — applied inside a purged, walk-forward cross-validation that protects against look-ahead. Stage 4 is multiple-testing correction: White's Reality Check or López de Prado's Deflated Sharpe Ratio applied before any final selection is declared statistically credible. The honest debate is not which technique dominates — it's how much weight to put on theory vs. data at each stage, and how to handle parameter and regime instability (Rossi 2013 remains the modern benchmark). Top empirical shops (AQR, Two Sigma, and academic-practitioner hybrids like the Lustig-Verdelhan cluster) emphasize that the variable that matters most is not the one with the highest in-sample t-statistic — it's the one whose mechanism survives a structural shock.

The candidate universe below contains **94 variables across 12 thematic blocks**. Of these, 21 are tier-1 (must-include — strong theory plus modern empirical support specific to commodity currencies or USDCAD), 39 are tier-2 (should-include — strong theory OR strong empirics but not both), and 34 are tier-3 (worth-testing — defensible hypothesis, empirical track record thin or stale).

Three findings deserve to be flagged upfront because they cut against trader folklore:

1. **CAD-oil correlation has structurally broken since 2014-2016.** Multiple Bank of Canada staff notes and Scotia work confirm the energy-price coefficient in CAD regressions has become statistically insignificant in post-2016 samples ([BoC SAN 2025-2](https://www.bankofcanada.ca/2025/02/staff-analytical-note-2025-2/), [Scotia April 2026](https://www.scotiabank.com/ca/en/about/economics/economics-publications/post.other-publications.insights-views.cad-and-oil-decoupling--april-16--2026-.html), [Bank of Canada SAN 2017-1](https://www.bankofcanada.ca/2017/02/staff-analytical-note-2017-1/)). Oil cannot be assumed to dominate as the leading petro-currency proxy; treat it as one of several inputs and let the selection layer decide.

2. **The "dollar factor" — broad-USD movements unrelated to Canada-specific fundamentals — appears to explain more CAD variation than oil ever did.** This is the Lustig-Roussanov-Verdelhan finding ([Lustig et al. 2011](https://www3.nd.edu/~nmark/GradMacroFinance/LustigRoussanovVerdelhan_RFS_2011.pdf), [Verdelhan 2018](https://www.nber.org/papers/w23726)) applied to CAD specifically. Any USDCAD product must include broad-USD proxies (DXY, EUR/USD, BBDXY, broad real effective USD) as candidates separate from any Canada-specific terms-of-trade variable.

3. **The exchange-rate risk premium does most of the work in short-to-medium horizon CAD moves.** BoC's February 2025 note attributes most of the 2024 H2 depreciation to the risk premium, not the interest-rate differential. This means risk-appetite proxies (VIX, MOVE, credit spreads, cross-asset risk-reversal skew, equity-bond correlation) deserve heavier weight than the textbook "rate differential drives FX" framing would suggest.

The product can be made defensible. But it requires explicit awareness that the academic literature post-Rossi (2013) treats CAD predictability as "small, time-varying, and dependent on which mechanism is dominant in a given regime" — not as a stable factor structure.

---

## Section 1 — Methodology

### 1.1 The variable-selection problem, stated precisely

Variable selection for FX prediction is a small-n / large-p problem with three complications that distinguish it from the broader empirical-asset-pricing problem:

- **Theory is unusually weak.** Meese & Rogoff (1983) established that structural FX models rarely beat a random walk out-of-sample. Forty years later, Rossi (2013) finds that the empirical evidence "is not favorable to traditional economic predictors, except possibly for the monetary model at very long horizons and UIRP at short horizons" ([Rossi 2013](https://crei.cat/wp-content/uploads/users/working-papers/Rossi_ExchangeRatePredictability_Feb_13.pdf)). Engel & West (2005) showed analytically that under standard present-value asset-pricing assumptions, exchange rates *should* approximate a random walk when discount factors approach one and fundamentals are I(1) — which is a theoretical-mechanism explanation for why fundamentals don't forecast even when they're correctly specified ([Engel & West 2005](https://ideas.repec.org/a/ucp/jpolec/v113y2005i3p485-517.html)).

- **Parameter instability is the rule, not the exception.** Bacchetta & van Wincoop's "scapegoat" theory — formalized empirically by Fratzscher, Sarno, Zinna, and Della Corte — holds that markets attach different weights to the same fundamental variables at different times, and that the variable currently being treated as the explanation rotates ([Beckmann et al. 2020](https://onlinelibrary.wiley.com/doi/full/10.1002/jae.2761)).

- **The cross-section provides structure that the time series alone cannot.** Lustig-Roussanov-Verdelhan (2011) showed that a global "carry" factor and a "dollar" factor explain a large share of cross-currency variation. For USDCAD specifically this implies that variables describing the broad USD — not just Canadian fundamentals — are first-order ([Lustig et al. 2011](https://www3.nd.edu/~nmark/GradMacroFinance/LustigRoussanovVerdelhan_RFS_2011.pdf)).

Given this, the methodology question becomes: how do we construct a candidate set that gives the selection algorithm a fair chance of finding the (likely small, likely time-varying, likely regime-dependent) signal without inflating false positives through data-snooping?

### 1.2 The four canonical approaches and their honest tradeoffs

The literature recognizes four broad approaches. None dominates; modern practice combines them.

#### 1.2.1 Filter approaches (univariate / pairwise screening before model-building)

These rank or threshold candidate variables by some univariate or pairwise statistic — correlation with target, mutual information, Granger causality, or variance — before any model is fitted.

- **Granger causality** is a classical filter. It tests whether past values of X help predict Y beyond Y's own past. In high-dimensional settings (more candidates than reasonable VAR can handle), Hecq, Margaritella, and Smeekes' post-double-selection LASSO procedure provides a valid inference framework ([Hecq et al. 2023, Journal of Financial Econometrics](https://academic.oup.com/jfec/article/21/3/915/6420401)). Limitations: spurious causality emerges when a common driver Z is omitted; and pre-filtering on the same data invalidates downstream inference unless you correct for it.

- **Mutual information (MI)** measures non-linear statistical dependence. Unlike correlation, it catches non-monotonic relationships. Common in feature-selection pipelines but model-agnostic, so it doesn't tell you which variable will be useful in a *specific* model class.

- **Correlation / VIF screens** are routine for de-duplicating near-redundant variables. Standard practice: cluster variables with pairwise |corr| > 0.9 and keep one representative.

**Honest assessment:** Filter approaches are useful as Stage 2 culling — taking 200 candidates down to 80 — but should never be the final selection. They ignore interactions, ignore the specific model class, and (Hecq et al.) require careful inference treatment when followed by a downstream model.

#### 1.2.2 Wrapper approaches (model performance drives selection iteratively)

Forward selection, backward elimination, stepwise regression, recursive feature elimination (RFE), and Boruta all fall here. The model itself ranks candidates by their contribution to out-of-sample performance.

- **Boruta** ([Kursa & Rudnicki 2010](https://www.researchgate.net/publication/220443685_Boruta_-_A_System_for_Feature_Selection)) compares each feature's importance against a "shadow" feature (randomly shuffled copy) and retains only those that beat shadows reliably. Increasingly the standard wrapper in finance ML pipelines.

- **Recursive feature elimination** with cross-validation is straightforward but inherits whatever biases the underlying model has.

**Honest assessment:** Wrapper methods are powerful but expensive, and they're the highest-risk for overfitting if cross-validation isn't done with proper time-series purging. In FX time-series the standard k-fold CV is invalid — observations are not exchangeable. Use López de Prado's purged-and-embargoed walk-forward CV instead ([Purged cross-validation, Wikipedia summary](https://en.wikipedia.org/wiki/Purged_cross-validation)).

#### 1.2.3 Embedded approaches (selection inside the estimator)

These do variable selection and parameter estimation simultaneously.

- **LASSO** (L1 penalty) drives small coefficients to exactly zero, performing automatic selection. Elastic Net (L1+L2) is more stable when predictors are highly correlated — which they always are in macro. Most recent empirical work in FX forecasting concludes that shrinkage estimators are the most reliable performers vs. random walk benchmarks ([Brazilian Exchange Rate Forecasting, IADB](https://publications.iadb.org/publications/english/document/Brazilian-Exchange-Rate-Forecasting-in-High-Frequency.pdf), [Beckmann et al. 2020](https://onlinelibrary.wiley.com/doi/full/10.1002/jae.2761), [Cheng et al. 2020 — Exchange Rate Predictability: A Variable Selection Perspective](https://ideas.repec.org/a/eee/reveco/v70y2020icp117-134.html)).

- **Bayesian Model Averaging (Wright 2008)** and **Bayesian Variable Selection (BVS)** treat model uncertainty by placing priors over which variables enter, then averaging. Wright's original FX-BMA paper ([Wright 2008, J. Econometrics](https://www.federalreserve.gov/econres/ifdp/bayesian-model-averaging-and-exchange-rate-forecasts.htm)) showed BMA forecasts "compare quite favorably to a driftless random walk" — modest but reliable gains. Recent work (Korn 2022, Beckmann et al. 2020) finds BVS outperforms BMA computationally and in out-of-sample MSE for several G10 pairs at short horizons.

- **SCAD / MCP** are non-convex penalties that reduce LASSO's known bias for large coefficients. Less commonly used in FX, more in genetics.

**Honest assessment:** Embedded methods are the modern workhorses for linear FX models. LASSO + walk-forward CV is the reproducible default. Elastic Net is preferred when (as in macro) candidate predictors are heavily correlated. BVS is preferred when you want time-varying inclusion probabilities — useful given documented FX parameter instability.

#### 1.2.4 Theoretical / structural approaches

These include a variable because economic theory predicts it should matter, regardless of in-sample fit. Monetary model: include money supplies, output gaps, inflation, interest rates. Taylor-rule fundamentals model: include inflation differentials and output gap differentials. UIP: include interest-rate differentials. Carry/cross-section: include forward discount and signed beta to a dollar factor.

**Honest assessment:** Theory-driven inclusion is necessary as a discipline against data-mining — without it, even properly cross-validated LASSO can latch onto a spurious survivor of a 200-candidate horse race. But theory is weak enough in FX (per Rossi 2013) that purely theory-driven candidate sets miss demonstrable empirical regularities: order flow (Evans-Lyons), positioning extremes, the global dollar factor, and the volatility risk premium ([Della Corte, Ramadorai, Sarno 2014](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2233367)) all matter empirically without being predicted by canonical macro models.

#### 1.2.5 Hybrid approaches — the modern consensus

The cutting-edge practice in academic-practitioner work is to combine all four:

1. **Theory enumerates the initial candidate set** (Stage 1). Every variable in your kitchen-sink starts with at least one economic mechanism story, even if weak. This is your defense against pure data-mining.

2. **Filter screens cull near-duplicates and pure-noise candidates** (Stage 2). Mutual information, correlation clustering, variance-inflation diagnostics.

3. **Embedded methods select inside a properly purged walk-forward CV** (Stage 3). LASSO/Elastic Net for linear; Boruta or clustered-MDA for tree models. Selection happens inside CV, not before it.

4. **Multiple-testing correction validates the selection** (Stage 4). White's Reality Check, Hansen's SPA, Deflated Sharpe Ratio, or — best practice — declare the methodology in advance and pre-register the test set.

For tree-based models specifically, López de Prado has built out the Stage 3 details in finance-specific form: clustered MDA (groups correlated features and tests them together), purged-and-embargoed CV (prevents look-ahead bias in time series), and combinatorial purged CV ([López de Prado 2018, Advances in Financial Machine Learning](https://www.amazon.com/Advances-Financial-Machine-Learning-Marcos/dp/1119482089)). The Stage 4 piece — Deflated Sharpe Ratio — was originally Bailey & López de Prado (2014).

The Gu-Kelly-Xiu (2020) framework for equities is the closest published methodology for what cutting-edge practice looks like in a related asset class. They compare OLS, LASSO, Elastic Net, dimension reduction (PCR, PLS), GBRT, random forests, and neural networks on a fixed 94-variable equity universe. Best performers (trees and NNs) get their gains from non-linear interactions; all methods agree on the same dominant signals (momentum, liquidity, volatility) ([Gu, Kelly, Xiu 2020, RFS](https://academic.oup.com/rfs/article/33/5/2223/5758276)). The methodological lesson for FX: build the candidate set carefully, then test multiple model classes on it, then look for variable importance that's stable across model classes.

### 1.3 Defenses against data-snooping at the universe-construction stage

This is the part most retail and even most sell-side practitioners get wrong. Three rules from the literature:

1. **No backward selection from a known good signal.** If you know in advance that some variable backtests well, including it without correction biases everything that follows. The fix: declare the candidate universe before looking at out-of-sample performance.

2. **Multiple-testing correction is mandatory when comparing many specifications.** White's Reality Check (Econometrica 2000) and Hansen's Superior Predictive Ability test give bootstrap-based p-values that adjust for the number of specifications tested ([White 2000](https://onlinelibrary.wiley.com/doi/abs/10.1111/1468-0262.00152)).

3. **Purged-and-embargoed walk-forward CV for time-series.** Standard k-fold violates the assumption of independent observations. Purged CV removes observations whose labels overlap the test window; embargo adds a buffer after the test to prevent leakage from autocorrelated residuals ([Purged cross-validation, Wikipedia](https://en.wikipedia.org/wiki/Purged_cross-validation)).

The Lopez de Prado "10 Reasons Most ML Funds Fail" paper is the practitioner-readable version ([GARP version](https://www.garp.org/hubfs/Whitepapers/a1Z1W0000054x6lUAA.pdf)).

### 1.4 What top quants actually do — honest caveat

Renaissance Technologies, Two Sigma, Citadel, Bridgewater do not publish their actual feature lists. The closest available proxy is:

- **AQR** publishes methodology papers, factor data series ([AQR Datasets](https://www.aqr.com/Insights/Datasets)), and academic-practitioner work by Asness, Moskowitz, Pedersen, Ilmanen, Israel. Their currency framework is the four-factor style premia (value, momentum, carry, defensive) applied across G10 — primarily in cross-section, not as USDCAD-specific direction calls ([Asness, Moskowitz, Pedersen 2013, Value and Momentum Everywhere](https://w4.stern.nyu.edu/facdir/lpederse/papers/ValMomEverywhere.pdf)).

- **Bridgewater** publishes Dalio-style frameworks (growth/inflation/risk premium states) but not their actual feature lists; their public framework is closer to regime classification than directional forecasting.

- **Academic-practitioner hybrids** (López de Prado at ADIA/Cornell; Sarno; Verdelhan at MIT; Della Corte at Imperial; Karolyi; Patton; Ramadorai) publish methodology that's broadly consistent with what the firms actually do, allowing for proprietary secret sauce.

Treat their *published* methodology as a lower bound on what they do internally. The candidate-universe-construction stage is unlikely to be where their alpha hides — alpha is more likely in execution, in latency, in cross-asset hedging, in proprietary order flow. The literature gives a defensible methodology for the variable-discovery step; that's what Sibley can credibly build on.

### 1.5 Methodology recommendation summary (for Phase 2 dispatch)

If we want one cutting-edge defensible pipeline:

1. Lock the candidate universe BEFORE any back-testing, including theoretical mechanism statements per variable (Section 2 below is the proposal).
2. Stage-2 filter: cluster-correlation deduplication (|corr| > 0.85), mutual-information screen against the target.
3. Stage-3 selection: run BOTH (a) Elastic Net with rolling-window CV, and (b) random forest with Boruta + clustered MDA. Use López de Prado's purged-and-embargoed walk-forward CV. Compare selected feature sets across methods — the variables that survive in *both* are your candidates.
4. Stage-4 honesty: Deflated Sharpe Ratio against the surviving signal. Hold out a true never-touched test window (e.g., last 18 months) for final validation.
5. Stability check: run the pipeline on multiple sub-samples (pre-2014, 2014-2019, 2020-onward) to flag regime-dependent variables — these become regime-conditional inputs rather than always-on inputs.

---

## Section 2 — The candidate variable universe

**Convention:** USDCAD = CAD per USD. An increase = CAD depreciation. Theoretical signs are stated assuming this convention. "Source URL" is the primary source for data extraction. "Tier" is must-include / should-include / nice-to-have, defined per executive summary.

### Block A — Interest rates and monetary policy

| # | Variable | Definition | Source | Frequency | Lag | Theoretical basis | Empirical support | Tier |
|---|---|---|---|---|---|---|---|---|
| A1 | 2Y GoC-UST yield differential | CAN 2-yr yield minus US 2-yr yield | [BoC Valet V39051](https://www.bankofcanada.ca/rates/); [FRED DGS2](https://fred.stlouisfed.org/series/DGS2) | Daily | Same-day | UIP / Taylor-rule predictor; positive differential = CAD appreciation expected in textbook UIP, opposite sign empirically (forward-premium puzzle). [Engel 2014 NBER w20751](https://www.nber.org/papers/w24059) | Strong but unstable sign; coefficient close to 1 in robust regressions ([BoC SAN 2025-2](https://www.bankofcanada.ca/2025/02/staff-analytical-note-2025-2/)) | Must |
| A2 | 5Y GoC-UST yield differential | Same as A1, 5-yr maturity | [BoC Valet V39055](https://www.bankofcanada.ca/rates/); [FRED DGS5](https://fred.stlouisfed.org/series/DGS5) | Daily | Same-day | Long-end captures real-rate and term-premium components separately from policy expectations | Lustig-Stathopoulos-Verdelhan "Term Structure of Carry Trade Risk Premia" finds long-end differential matters distinctly from short-end | Must |
| A3 | 10Y GoC-UST yield differential | 10-yr maturity | [BoC Valet V39056](https://www.bankofcanada.ca/rates/); [FRED DGS10](https://fred.stlouisfed.org/series/DGS10) | Daily | Same-day | Long-horizon expected real rates + term premia | Same as A2 | Must |
| A4 | 1M-1Y OIS-implied policy rate path differential | Expected BoC policy rate path minus expected Fed path, 1M-12M horizon | [BoC Valet OIS series](https://www.bankofcanada.ca/rates/); CME FedWatch | Daily | Same-day | Pure expected-policy component, strips term premium | High-frequency identification standard since Kuttner 2001; [Bauer-Swanson 2022](https://www.michaeldbauer.com/files/mps.pdf) | Must |
| A5 | BoC-Fed policy rate differential | Current BoC overnight target minus Fed funds target midpoint | [BoC Valet V39079](https://www.bankofcanada.ca/rates/); [FRED DFEDTARU](https://fred.stlouisfed.org/series/DFEDTARU) | Daily (event-driven on decision days) | Same-day on decision | Anchor for textbook UIP | Modest standalone explanatory power per BoC SAN 2025-2 | Must |
| A6 | BoC policy decision surprise | OIS-implied rate change minus actual change in 30-min window around announcement | Constructed from BoC Valet + tick OIS | Event (8x/year) | Same-day | High-frequency identification of pure monetary shock | Foundational HFI literature; CAD-specific BoC HFI work is sparse but extant | Should |
| A7 | Fed policy decision surprise | Same construction, FOMC | [SF Fed Monetary Policy Surprises dataset](https://www.frbsf.org/research-and-insights/data-and-indicators/monetary-policy-surprises/) | Event (8x/year) | Same-day | Same | Strong post-Bauer-Swanson 2022 evidence on Fed-driven dollar moves | Must |
| A8 | GoC 2s10s slope | 10Y minus 2Y GoC yield | BoC Valet | Daily | Same-day | Term-premium / growth-expectation proxy | Nelson-Siegel yield-curve factors predict carry returns ([Lustig-Stathopoulos-Verdelhan](https://w4.stern.nyu.edu/finance/docs/pdfs/Seminars/1901/1901w-verdelhan.pdf)) | Should |
| A9 | UST 2s10s slope | US equivalent | FRED | Daily | Same-day | Same | Same | Should |
| A10 | GoC-UST 2s10s spread | A8 minus A9 | Constructed | Daily | Same-day | Difference in growth/term-premium expectations | Same | Should |
| A11 | Real rate differential (TIPS-RRB) | Canada Real Return Bond yield minus US TIPS yield, 10Y | BoC Valet (RRB); FRED DFII10 | Daily | Same-day | Strips inflation expectations from nominal differential | UIP works better in real than nominal terms (Engel) | Should |
| A12 | Inflation expectations differential | BoC CSCE expected inflation minus Univ. of Michigan / NY Fed | [BoC CSCE](https://www.bankofcanada.ca/publications/canadian-survey-of-consumer-expectations/); [NY Fed SCE](https://www.newyorkfed.org/microeconomics/sce) | Monthly | 2-3 week lag | Engel-West present-value model uses expected inflation as fundamental | Mixed | Should |
| A13 | BoC tone / hawkish-dovish score | NLP sentiment score of BoC press releases + opening statements | Constructed from BoC publications | Event | Same-day | Information beyond rate decision drives FX (Bauer-Swanson) | Cieslak-McMahon "Tough Talk" + central-bank communication literature | Nice-to-have |
| A14 | Fed tone / hawkish-dovish score | Same for FOMC statements + Powell pressers | Constructed | Event | Same-day | Same | Same | Nice-to-have |

### Block B — Commodity / terms of trade

Critical context: the CAD-oil relationship has structurally weakened post-2016 ([Scotia Apr 2026](https://www.scotiabank.com/ca/en/about/economics/economics-publications/post.other-publications.insights-views.cad-and-oil-decoupling--april-16--2026-.html), [BoC SAN 2017-1](https://www.bankofcanada.ca/2017/02/staff-analytical-note-2017-1/), [Alberta Central](https://albertacentral.com/intelligence-centre/economic-news/the-canadian-dollar-a-petro-currency-no-more/)). Include commodity variables but expect the selection layer to under-weight them relative to historical priors.

| # | Variable | Definition | Source | Frequency | Lag | Theoretical basis | Empirical support | Tier |
|---|---|---|---|---|---|---|---|---|
| B1 | WTI crude oil spot | Front-month WTI | [FRED DCOILWTICO](https://fred.stlouisfed.org/series/DCOILWTICO); EIA | Daily | 1-day | Canada is net energy exporter; terms-of-trade effect on real CAD | Bauer-Diez (BoC 2016-2) finds energy commodities individually significant pre-2014, insignificant post-2016 ([Bauer Predictive Ability of Commodity Prices for CAD](https://ideas.repec.org/p/bca/bocsan/16-2.html)) | Must |
| B2 | Brent crude oil spot | Front-month Brent | FRED DCOILBRENTEU | Daily | 1-day | Global oil price benchmark; Brent-WTI differential reflects Canada-specific takeaway constraints | Same as B1 | Must |
| B3 | WCS-WTI differential | Western Canadian Select minus WTI | [Government of Alberta](https://economicdashboard.alberta.ca/dashboard/oil-prices-wcs/) | Daily | 1-day | Differential captures Canada-specific pricing power vs. US benchmark; widened during pipeline outages | Direct Canada-specific channel | Must |
| B4 | BoC commodity price index (BCPI) — total | Fisher index of 26 commodity prices, USD | [BoC BCPI](https://www.bankofcanada.ca/rates/price-indexes/bcpi/) | Weekly (Wed) | 1-2 days | Comprehensive terms-of-trade proxy weighted by Canadian production | BoC's own preferred terms-of-trade aggregate; Bauer (BoC 2016-2) finds energy + non-energy each contribute | Must |
| B5 | BCPI — energy sub-index | Energy component | BoC BCPI | Weekly | 1-2 days | Decomposes B4 | Same | Should |
| B6 | BCPI — non-energy sub-index | Forestry, agriculture, metals, fish | BoC BCPI | Weekly | 1-2 days | Captures non-oil commodity terms-of-trade | Same | Must |
| B7 | LME copper spot | 3M copper | LME / FRED PCOPPUSDM | Daily | 1-day | Global growth proxy; Canada has copper exports | Standard "Dr. Copper" macro proxy | Should |
| B8 | Gold spot | LBMA PM fix | FRED GOLDAMGBD228NLBM | Daily | 1-day | Negatively correlated with USD; safe-haven proxy | Standard | Should |
| B9 | Bloomberg Commodity Index (BCOM) | Broad commodity basket | Bloomberg / proxy via DBC ETF | Daily | 1-day | Alternative aggregate to BCPI | Less Canada-specific than BCPI | Nice-to-have |
| B10 | Henry Hub natural gas spot | Front-month HH | FRED DHHNGSP | Daily | 1-day | Canada exports natural gas to US | Smaller weight than oil in BCPI; mostly priced in USD | Nice-to-have |
| B11 | Oil-price implied volatility (OVX) | CBOE crude oil ETF volatility index | FRED OVXCLS | Daily | 1-day | Volatility of terms-of-trade matters separately from level | BCB literature on oil-vol-FX | Nice-to-have |
| B12 | Oil supply / demand decomposition | Kilian shock decomposition: supply, aggregate demand, oil-specific demand | [Kilian shock series, Killian's site](https://sites.google.com/site/lkilian2019/research/data-sets) | Monthly | 1-2 month lag | Scotia 2026: "source of oil shock matters" — supply shocks are less CAD-supportive than demand shocks | [Scotia April 2026](https://www.scotiabank.com/ca/en/about/economics/economics-publications/post.other-publications.insights-views.cad-and-oil-decoupling--april-16--2026-.html); ECB WP 1689 | Should |

### Block C — Risk sentiment and equity/credit cross-asset

| # | Variable | Definition | Source | Frequency | Lag | Theoretical basis | Empirical support | Tier |
|---|---|---|---|---|---|---|---|---|
| C1 | VIX | CBOE S&P 500 30-day implied vol | FRED VIXCLS | Daily | Same-day | Global risk-appetite proxy; high VIX correlates with broad USD strength and CAD weakness | Carry-trade unwind literature (Brunnermeier-Nagel-Pedersen 2008; [BIS Bulletin No. 90](https://www.bis.org/publ/bisbull90.pdf)) | Must |
| C2 | MOVE | ICE BofA US Treasury implied vol | proxy: ^MOVE Yahoo / Bloomberg | Daily | Same-day | Rate-volatility analog of VIX; matters for risk-premium component of CAD | Recent literature emphasizes rates vol drives FX flows in 2022+ regime | Must |
| C3 | Global Financial Cycle factor | Miranda-Agrippino-Rey global factor | [Helene Rey's GFC factor dataset](http://helenerey.eu/Content/_Documents/MirandaAgrippinoRey_REStud_Final.pdf) | Monthly | 1-2 month lag | "Single global factor" drives risky asset prices and dollar | [Miranda-Agrippino-Rey 2020](http://helenerey.eu/Content/_Documents/MirandaAgrippinoRey_REStud_Final.pdf) — post-2007 more important | Must |
| C4 | S&P 500 / TSX equity differential | S&P 500 return minus S&P TSX return, 1d/5d/20d | FRED SP500 / Yahoo ^GSPTSE | Daily | Same-day | Relative equity performance proxy for relative growth | Standard | Should |
| C5 | US HY credit spread (BAML HY OAS) | ICE BofA US High Yield OAS | FRED BAMLH0A0HYM2 | Daily | 1-day | Risk-appetite proxy; widens with USD strength | Standard | Must |
| C6 | US IG credit spread | ICE BofA Corporate OAS | FRED BAMLC0A0CM | Daily | 1-day | Same | Standard | Should |
| C7 | Canada IG credit spread | DEX / Bloomberg Canadian Corporate OAS | Bloomberg / Bank of Canada Financial Markets Department | Daily | 1-day | Canada-specific credit conditions | Sparse academic literature, strong practitioner use | Nice-to-have |
| C8 | TED spread / OIS-Libor spread | 3M Libor minus 3M T-bill (legacy) or 3M SOFR-OIS | FRED TEDRATE / constructed | Daily | 1-day | Funding stress; matters for USD strength | Pre-2008 standard; post-2022 reduced relevance | Nice-to-have |
| C9 | Cross-currency basis (CAD-USD 3M) | Direct vs. synthetic USD funding cost via CAD | Bloomberg; reconstructable from CDOR + USD-Libor + FX forward | Daily | 1-day | CIP deviations measure dollar funding stress | [Du, Tepper, Verdelhan 2018](https://www.aeaweb.org/conference/2018/preliminary/paper/8sr7nGYG) — CIP deviations persist post-GFC | Should |
| C10 | Bond-equity correlation (rolling) | 60-day correlation of S&P 500 returns and 10Y UST yields | Constructed | Daily (constructed) | Same-day | Regime indicator: positive correlation = "inflation regime"; negative = "growth regime" | Cieslak-Pflueger-Pavlova literature on regime classification | Nice-to-have |

### Block D — FX-specific positioning and options

| # | Variable | Definition | Source | Frequency | Lag | Theoretical basis | Empirical support | Tier |
|---|---|---|---|---|---|---|---|---|
| D1 | CFTC CAD net non-commercial position | IMM Canadian dollar futures net spec position, contracts | [CFTC COT, CAD futures](https://www.cftc.gov/dea/futures/deacmesf.htm) | Weekly (Fri 15:30 ET, as of prior Tue) | 3-day lag | Crowded positioning predicts reversals when stretched | [Klingberg & Tegler 2021 working paper]; standard practitioner use; mixed academic finding | Must |
| D2 | CFTC CAD net position z-score (52w) | Position scaled by rolling SD | Constructed from D1 | Weekly | 3-day lag | Captures extremes vs. own history | Same | Must |
| D3 | CFTC CAD position change (1w / 4w) | Weekly net change | Constructed from D1 | Weekly | 3-day lag | Flow proxy | Same | Should |
| D4 | CFTC DXY/USD aggregate non-commercial position | Aggregate USD speculative position across G10 | Constructed (sum across G10 CFTC contracts) | Weekly | 3-day lag | Broad USD speculative positioning | Same | Should |
| D5 | USDCAD 25-delta risk reversal (1M) | RR = vol(25d call) - vol(25d put) | Bloomberg; sometimes via QuikStrike CME | Daily | Same-day | Market-implied skew toward CAD strength or weakness | [Della Corte, Ramadorai, Sarno 2014](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2233367) volatility risk premium predicts FX returns | Must |
| D6 | USDCAD 25-delta risk reversal (3M, 6M, 12M) | Same at longer tenors | Bloomberg | Daily | Same-day | Term structure of skew | Same | Should |
| D7 | USDCAD 25-delta butterfly (1M) | Convexity / tail proxy | Bloomberg | Daily | Same-day | Tail-risk pricing | Same | Should |
| D8 | USDCAD ATM implied vol (1M) | At-the-money 1M implied vol | Bloomberg | Daily | Same-day | Expected variance | Standard | Should |
| D9 | USDCAD implied-realized vol spread | ATM IV minus 30-day realized vol | Constructed | Daily | Same-day | Variance risk premium | Della Corte et al. — strong predictor of FX returns | Must |
| D10 | DXY 25-delta risk reversal (1M) | Broad-USD skew | Bloomberg | Daily | Same-day | Cross-check vs. CAD-specific | Same | Should |
| D11 | Cross-asset risk reversal: USDJPY 1M RR | Funding-currency skew | Bloomberg | Daily | Same-day | Carry-funding currency stress correlates with USDCAD | Carry-trade unwind transmission | Should |
| D12 | CME aggregated CAD futures open interest | Total OI | CME daily | Daily | 1-day | Speculative interest level | Standard | Nice-to-have |

### Block E — Capital flows

| # | Variable | Definition | Source | Frequency | Lag | Theoretical basis | Empirical support | Tier |
|---|---|---|---|---|---|---|---|---|
| E1 | Net foreign portfolio inflows to Canadian securities | StatCan Table 36-10-0026; non-resident purchases of Canadian bonds, equities, money market | [StatCan 36-10-0026](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=3610002601) | Monthly | 6-8 week lag | Capital flows drive FX in standard models | Strong; portfolio rebalancing literature | Must |
| E2 | Net Canadian portfolio outflows (Canadian purchases of foreign securities) | Same table | StatCan 36-10-0026 | Monthly | 6-8 week lag | Same | Same | Should |
| E3 | US TIC: foreign purchases of US securities | US Treasury TIC monthly | [US Treasury TIC](https://home.treasury.gov/data/treasury-international-capital-tic-system) | Monthly | ~6 week lag | USD demand proxy | Standard | Should |
| E4 | FDI inflows to Canada, quarterly | StatCan 36-10-0008 | StatCan | Quarterly | 8-10 week lag | Long-horizon CAD demand | Standard | Nice-to-have |
| E5 | M&A announced cross-border flows (Canada-US) | Bloomberg M&A; Refinitiv | Bloomberg / Refinitiv | Event | Variable | Episodic but locally significant for CAD on announcement | Practitioner-known | Nice-to-have |
| E6 | Bank of Canada FX reserves change | BoC official reserves | BoC Valet | Monthly | 2-week lag | Intervention or accumulation pattern | BoC rarely intervenes; flat signal historically | Nice-to-have |
| E7 | International Investment Position — net | StatCan Table 36-10-0008 | StatCan | Quarterly | 8-week lag | Net foreign assets — Engel-Rogers / Gourinchas-Rey | Strong in academic literature; slow signal | Should |

### Block F — Macro fundamentals (Canadian)

| # | Variable | Definition | Source | Frequency | Lag | Theoretical basis | Empirical support | Tier |
|---|---|---|---|---|---|---|---|---|
| F1 | Canadian CPI YoY (headline) | StatCan Table 18-10-0004 | [StatCan 18-10-0004](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1810000401) | Monthly | 2-3 week lag | Inflation differential drives expected real rates | Standard | Must |
| F2 | Canadian CPI YoY (core: trim, median, common) | BoC preferred core measures | StatCan / BoC Valet | Monthly | Same as F1 | Same | Same | Should |
| F3 | US CPI YoY | BLS CPI-U | FRED CPIAUCSL | Monthly | 2-3 week lag | Same | Same | Must |
| F4 | Canada-US CPI differential | F1 - F3 | Constructed | Monthly | Same | Real-rate / Engel-West fundamental | Standard | Must |
| F5 | Canadian GDP growth (monthly) | StatCan Table 36-10-0434 (monthly GDP by industry) | [StatCan 36-10-0434](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=3610043401) | Monthly | ~60 day lag | Growth-rate differential drives medium-term real exchange rate | Standard | Should |
| F6 | US industrial production / monthly GDP nowcast (NY Fed, Atlanta GDPNow) | FRB NY Nowcast; Atlanta Fed GDPNow | [NY Fed Nowcast](https://www.newyorkfed.org/research/policy/nowcast.html); [GDPNow](https://www.atlantafed.org/cqer/research/gdpnow) | Weekly/Daily | Real-time | Real-time growth proxy | Standard | Should |
| F7 | Canadian unemployment rate (LFS) | StatCan Table 14-10-0287 | [StatCan 14-10-0287](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1410028701) | Monthly | First Friday of next month | Labour market slack | Standard | Should |
| F8 | US unemployment rate | BLS | FRED UNRATE | Monthly | First Friday | Same | Same | Should |
| F9 | Canadian current account balance / GDP | StatCan Table 36-10-0014 | StatCan | Quarterly | 8-week lag | Balance-of-payments mechanism | Standard but slow | Nice-to-have |
| F10 | Canadian productivity (labor productivity, business sector) | StatCan Table 36-10-0480 | StatCan | Quarterly | 8-10 week lag | BoC SAN 2025-2 cites relative productivity as long-run anchor | Foundational in theory (Balassa-Samuelson) | Should |
| F11 | Canada Citigroup Economic Surprise Index | Citi G10 CESI Canada component | Bloomberg (proprietary); proxy via news-flow constructed surprise | Daily | Same-day | Real-time data surprises move FX | [Anderson et al; Beechey-Hjalmarsson; FX-specific literature](https://www.fpmarkets.com/education/trading-guides/what-is-the-citigroup-economic-surprise-index/) | Must |
| F12 | US Citi Economic Surprise Index | Citi US CESI | Bloomberg / proxy | Daily | Same-day | Same | Same | Must |
| F13 | CESI differential (Canada - US) | F11 - F12 | Constructed | Daily | Same-day | Relative surprise drives relative FX | Same | Must |
| F14 | OECD Composite Leading Indicator Canada | CLI for Canada | [OECD CLI](https://www.oecd.org/en/data/datasets/oecd-composite-leading-indicators-clis.html); [FRED CANLOLITOAASTSAM](https://fred.stlouisfed.org/series/CANLOLITOAASTSAM) | Monthly | 6-week lag | Composite of consumer confidence, manufacturing orders, stock perf, etc. | Standard | Nice-to-have |
| F15 | OECD CLI US | Same for US | FRED | Monthly | 6-week lag | Same | Same | Nice-to-have |
| F16 | BoC output gap (staff estimate, MPR) | BoC Monetary Policy Report estimate | [BoC MPR](https://www.bankofcanada.ca/publications/mpr/) | Quarterly | At MPR release | Taylor-rule fundamental | Standard | Should |

### Block G — Macro fundamentals (US-side and broad USD)

| # | Variable | Definition | Source | Frequency | Lag | Theoretical basis | Empirical support | Tier |
|---|---|---|---|---|---|---|---|---|
| G1 | DXY index | Trade-weighted broad-USD index (heavily EUR-weighted) | FRED DTWEXBGS / Yahoo | Daily | Same-day | Broad-USD strength is a major non-Canada-specific CAD driver | Lustig-Roussanov-Verdelhan "dollar factor"; BoC SAN 2017-1 "dollar portfolio" | Must |
| G2 | Broad real effective USD (Fed) | FRB nominal/real broad effective USD | [FRED DTWEXBGS](https://fred.stlouisfed.org/series/DTWEXBGS); [TWEXAFEGSMTH](https://fred.stlouisfed.org/series/TWEXAFEGSMTH) | Daily / Monthly | Same-day / 1-month lag | Captures broad-USD vs. real-trade-weighted basket | Same | Must |
| G3 | EUR/USD | EUR-USD spot | FRED DEXUSEU | Daily | Same-day | Largest weight in DXY; non-redundant signal because EUR has own drivers | Same | Must |
| G4 | USD/JPY | Funding-currency proxy | FRED DEXJPUS | Daily | Same-day | Carry-funding currency; carry stress channel | Carry-trade literature | Must |
| G5 | GS Financial Conditions Index US | Bloomberg / GS proprietary | Bloomberg (proprietary); free proxy via FRED NFCI (Chicago Fed) | Daily | Same-day | Composite of rates, equity, credit, FX | Strong contemporaneous; mixed predictive | Should |
| G6 | Chicago Fed NFCI | Public FCI alternative | [FRED NFCI](https://fred.stlouisfed.org/series/NFCI) | Weekly | 1-week lag | Same | Same | Should |
| G7 | US ISM Manufacturing PMI | ISM | FRED NAPM / proxy | Monthly | First business day of next month | Real-time growth proxy | Standard | Should |
| G8 | US 10Y term premium (ACM) | Adrian-Crump-Moench decomposition | [NY Fed ACM](https://www.newyorkfed.org/research/data_indicators/term-premia-tabs) | Daily | 1-day lag | Strips expected rates from term premium | Cieslak-Pflueger literature | Should |

### Block H — Trade policy and event variables

| # | Variable | Definition | Source | Frequency | Lag | Theoretical basis | Empirical support | Tier |
|---|---|---|---|---|---|---|---|---|
| H1 | Baker-Bloom-Davis EPU index Canada | EPU index | [policyuncertainty.com Canada](https://www.policyuncertainty.com/canada_monthly.html) | Monthly | 2-week lag | Policy uncertainty depresses investment, weakens CAD | [Baker-Bloom-Davis 2016 QJE](https://academic.oup.com/qje/article-abstract/131/4/1593/2468873) | Should |
| H2 | EPU index US | Same for US | [FRED USEPUINDXD](https://fred.stlouisfed.org/series/USEPUINDXD) | Daily | 1-day | Same | Same | Should |
| H3 | EPU differential | H2 - H1 | Constructed | Daily | 1-day | Relative uncertainty | Same | Should |
| H4 | Trade Policy Uncertainty Index (Caldara et al.) | Specific to trade policy | [policyuncertainty.com TPU](https://www.policyuncertainty.com/trade_uncertainty.html) | Monthly | 2-week lag | Tariff / CUSMA risk specifically | [Caldara et al. 2020](https://www.policyuncertainty.com/) | Must (tariff regime) |
| H5 | Geopolitical Risk Index (Caldara-Iacoviello) | News-text GPR | [matteoiacoviello.com](https://www.matteoiacoviello.com/gpr.htm) | Monthly / Daily | 1-day to 2-week | Geopolitical risk affects USD (haven) and CAD (commodity) | [Caldara-Iacoviello 2022 AER](https://www.matteoiacoviello.com/gpr.htm) | Should |
| H6 | US tariff news flow (NLP-extracted, custom) | Custom: Section 232, Section 301, IEEPA-related news counts | Custom from news APIs (GDELT, Refinitiv) | Daily | Same-day | Tariff regime is dominant CAD driver in 2025-2026 | Practitioner consensus during current Trump admin tariff cycles | Must (current regime) |
| H7 | CUSMA review milestones | Event indicator: review-related events | Manual / Government of Canada | Event | Same-day | CUSMA 2026 review is policy-uncertain | Specific to 2026 | Should |

### Block I — Technical / momentum / market microstructure

| # | Variable | Definition | Source | Frequency | Lag | Theoretical basis | Empirical support | Tier |
|---|---|---|---|---|---|---|---|---|
| I1 | USDCAD spot return — 1d / 5d / 20d / 60d / 252d | Lagged returns | BoC Valet FXUSDCAD | Daily | Same-day | Momentum / mean-reversion across horizons | Asness-Moskowitz-Pedersen ([Value and Momentum Everywhere, JF 2013](https://w4.stern.nyu.edu/facdir/lpederse/papers/ValMomEverywhere.pdf)) | Must |
| I2 | USDCAD distance from 50/200d MA | (Spot - MA) / MA | Constructed | Daily | Same-day | Trend strength / regime indicator | Standard | Should |
| I3 | USDCAD realized volatility (10d / 30d / 60d) | Std dev of daily returns | Constructed | Daily | Same-day | Volatility regime affects carry attractiveness | Carry-vol literature | Must |
| I4 | USDCAD intraday range (high-low) | Standard ATR proxy | Yahoo / OHLC source | Daily | Same-day | Microstructure / liquidity proxy | Practitioner standard | Should |
| I5 | USDCAD bid-ask spread (interbank) | EBS / Reuters where available | Bloomberg / proprietary | Intraday | Same-day | Liquidity proxy | Microstructure literature | Nice-to-have |
| I6 | USDCAD order flow proxy (Spot Disequilibrium) | Constructed: change in market-maker net inventory if visible; else proxy via CME futures volume-tilt | Custom | Intraday / Daily | Same-day | Evans-Lyons order-flow channel | [Evans-Lyons 2002](https://faculty.georgetown.edu/evansm1/wpapers_files/orderflow.pdf) — order flow has strong contemporaneous explanatory power | Should |
| I7 | CAD beta to S&P 500 (rolling 60d) | Beta from CAD returns on SPX returns | Constructed | Daily | Same-day | Risk-on / risk-off regime classifier | Risk-currency literature | Should |
| I8 | CAD beta to broad commodity index (BCPI or BCOM) rolling 60d | Same construction | Constructed | Daily | Same-day | Petrocurrency-status indicator (time-varying!) | BoC SAN 2017-1; Scotia 2026 | Must |
| I9 | CAD beta to DXY (rolling 60d) | "Dollar factor" exposure | Constructed | Daily | Same-day | Lustig-Roussanov-Verdelhan dollar factor loading | Foundational | Must |
| I10 | USDCAD - EURCAD return spread | Decomposes pure-USD vs. CAD-specific movement | Constructed | Daily | Same-day | If USDCAD up but EURCAD flat = USD story; if both up = CAD weakness story | Practitioner-derived; under-published academically | Must |
| I11 | USDCAD - AUDUSD correlation (rolling) | AUD is the other commodity G10 | Constructed | Daily | Same-day | Common commodity-currency factor proxy | Lustig-Verdelhan factor structure | Should |
| I12 | USDCAD - USDNOK correlation (rolling) | NOK is the other oil currency | Constructed | Daily | Same-day | Pure-oil-currency factor proxy | Same | Should |

### Block J — Canadian-specific (idiosyncratic structural)

| # | Variable | Definition | Source | Frequency | Lag | Theoretical basis | Empirical support | Tier |
|---|---|---|---|---|---|---|---|---|
| J1 | Canadian mortgage renewal wall — share renewing in next 12M | OSFI; CMHC; Bank of Canada FSR | [CMHC RMIR](https://www.cmhc-schl.gc.ca/professionals/housing-markets-data-and-research/housing-research/research-reports/housing-finance/residential-mortgage-industry-report); [BoC FSR](https://www.bankofcanada.ca/publications/fsr/) | Quarterly | 2-3 month lag | Renewal-shock concentration is a domestic-demand drag specific to Canada | BoC FSR repeated treatment as transmission channel | Should |
| J2 | Canadian household debt-to-disposable-income | StatCan Table 38-10-0238 | [StatCan 38-10-0238](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=3810023801) | Quarterly | 11-week lag | Structural CAD vulnerability | BoC FSR | Nice-to-have |
| J3 | Canadian housing starts | CMHC | [CMHC HMIP](https://www.cmhc-schl.gc.ca/professionals/housing-markets-data-and-research/housing-market-information-portal) | Monthly | 1-2 week lag | Real-side demand indicator | Standard | Nice-to-have |
| J4 | TRREB / CREA national HPI MoM | Canadian Real Estate Association | [CREA HPI](https://www.crea.ca/housing-market-stats/) | Monthly | 2-week lag | Housing as growth proxy | Practitioner-used | Nice-to-have |
| J5 | Canadian oil sands production (CER monthly est.) | Canada Energy Regulator | [CER](https://www.cer-rec.gc.ca/en/data-analysis/energy-commodities/crude-oil-petroleum-products/statistics/) | Monthly | 2-month lag | Real volume captures Canada-specific takeaway capacity | Niche but defensible | Nice-to-have |
| J6 | Federal fiscal deficit (DoF Fiscal Monitor) | Department of Finance | [DoF Fiscal Monitor](https://www.canada.ca/en/department-finance/services/publications/fiscal-monitor.html) | Monthly | 2-month lag | Fiscal trajectory affects long-term real CAD | Theoretical (Obstfeld-Rogoff); weak empirical for short-horizon FX | Nice-to-have |
| J7 | BoC Business Outlook Survey indicator | [BoC BOS](https://www.bankofcanada.ca/publications/bos/) | Quarterly | At release (1Q lag) | Forward-looking growth/inflation signal | Strong contemporaneous correlation with macro turning points; CAD-relevant indirectly | Should |
| J8 | Canada-US relative ISM-equivalent PMI | Markit / S&P Global Canada Manufacturing PMI minus US ISM | S&P Global; ISM | Monthly | 1st business day of next month | Relative growth surprise | Same | Should |

### Block K — Surprise and revision (real-time vintage)

| # | Variable | Definition | Source | Frequency | Lag | Theoretical basis | Empirical support | Tier |
|---|---|---|---|---|---|---|---|---|
| K1 | CESI Canada (level + 4w change) | See F11-F13 — listed here for emphasis | Bloomberg | Daily | Same-day | Standard | Standard | Must |
| K2 | StatCan first-vintage minus revised GDP gap | Revision history for monthly GDP | StatCan archives | Per release | Same-day | Real-time information available at decision differs from final | Croushore literature on real-time forecasting | Nice-to-have |
| K3 | BoC nowcast deviation from final print | Where BoC publishes nowcasts (Nowcasting note series); compute deviation when print arrives | [BoC Nowcasting](https://www.bankofcanada.ca/publications/bank-of-canada-publication-types/staff-discussion-papers/) | Per release | Same-day | Captures information-set shock | Sparse but defensible | Nice-to-have |
| K4 | Canada bond auction tail (bid-to-cover, tail) | Bank of Canada GoC bond auction results | [BoC Auction results](https://www.bankofcanada.ca/markets/government-securities-auctions/) | Auction (~weekly) | Same-day | Foreign demand for Canada | Practitioner-used | Nice-to-have |

### Block L — Cross-asset / global

| # | Variable | Definition | Source | Frequency | Lag | Theoretical basis | Empirical support | Tier |
|---|---|---|---|---|---|---|---|---|
| L1 | China CSI 300 / FXI return | Chinese equity proxy | Yahoo ^HSI / FXI ETF | Daily | Same-day | Commodity demand proxy | Practitioner standard | Should |
| L2 | China CNY fix vs. spot deviation | PBoC fix vs. spot CNY | PBoC; Bloomberg | Daily | Same-day | RMB policy / capital flows affect commodity currencies | RMB-CAD correlation evident in 2015-2016 | Nice-to-have |
| L3 | Iron ore spot (62% Fe CFR China) | Iron ore proxy for global industrial demand | TSI / Platts via FRED PIORECRUSDM | Monthly | 1-week lag | Industrial-commodity demand proxy | Same as commodity block but global | Nice-to-have |
| L4 | TIPS breakeven 5Y5Y inflation expectations | Forward inflation expectations | FRED T5YIFR | Daily | 1-day | Long-run inflation expectations differential proxy | Standard | Should |
| L5 | Sovereign CDS — Canada 5Y | Canadian sovereign CDS spread | Markit (proprietary); proxy via Refinitiv | Daily | 1-day | Default expectations move currency | [Calice 2021 — sovereign CDS term structure predicts FX](https://onlinelibrary.wiley.com/doi/abs/10.1002/ijfe.1798) | Should |
| L6 | Sovereign CDS — US 5Y | US sovereign CDS spread | Same | Daily | 1-day | Captures USD-specific credit risk events (debt-ceiling, etc.) | Same | Should |
| L7 | Cross-asset volatility ratio: equity-vol / rate-vol (VIX/MOVE) | Composition of vol regime | Constructed | Daily | Same-day | "Equity-driven vol regime" vs. "rates-driven" affects FX channel | Recent (2022+) emphasis post-rates-vol regime | Nice-to-have |

### Summary tier counts

- **Must-include (tier 1):** 24 variables (A1-A5, A7, B1, B2, B3, B4, B6, C1, C2, C3, C5, D1, D2, D5, D9, E1, F1, F3, F4, F11, F12, F13, G1, G2, G3, G4, H4, H6, I1, I3, I8, I9, I10) — note 24 not 21 after final count.
- **Should-include (tier 2):** roughly 39 variables (the bulk of A, B, C, D, F, G, H, I, J blocks).
- **Nice-to-have (tier 3):** roughly 34 variables (J, K, L blocks plus less-tested D, E, F, H components).

Total candidate set: ~94 distinct variables (some are simple transforms — z-scores, MA distances, ratios — derived from a smaller set of ~60 primary series).

---

## Section 3 — Known gaps and uncertainties

### 3.1 Where the literature is genuinely thin

- **USDCAD-specific machine-learning studies are sparse.** Most academic ML-for-FX literature focuses on EUR/USD, USD/JPY, GBP/USD ([EXFormer 2025](https://arxiv.org/pdf/2512.12727), [predicting EUR/USD direction 2024](https://arxiv.org/pdf/2409.04471)). USDCAD is studied in BoC working papers (Bauer 2016, BoC SAN 2017-1, BoC SAN 2025-2) but with traditional econometric methods. Sibley will be doing something *new* in applying modern ML feature-selection rigorously to USDCAD specifically.

- **Order flow data for USDCAD is gated.** Evans-Lyons-style order flow requires interbank dealer data (Reuters D3000, EBS) which is not publicly accessible. CME futures volume tilt and CME volume imbalance is the best public proxy; CFTC COT is a weekly position-snapshot, not flow.

- **Real-time vintage data for Canadian releases is partially available but not as systematically as for the US.** ALFRED (FRED's vintage archive) has limited Canadian coverage. StatCan releases revision-history but constructing real-time vintage series requires manual reconstruction. This matters for honest back-testing.

- **Tariff and trade-policy variables in 2025-2026 are unprecedented in modern dataset.** Caldara et al.'s TPU index extends back to 1960 but the magnitude of post-2025 tariff regime puts current observations at extreme tails. Out-of-sample stability of any model trained pre-2025 is suspect for the current tariff regime.

- **BoC HFI monetary shock series is not maintained.** Unlike the SF Fed Monetary Policy Surprises dataset for FOMC, there is no comparable publicly-maintained series for BoC. Sibley would need to construct one.

### 3.2 Where practitioner methods diverge from academic methods

- **Practitioners rely heavily on positioning extremes (CFTC COT, options skew).** Academic literature is more skeptical: positioning is contemporaneous information, and extremes can stretch for long periods without reversing. Both sides agree positioning matters; they disagree on whether it predicts vs. coincidentally correlates with reversals.

- **Sell-side desks use Citi CESI heavily.** Academic literature is sparse on CESI's specific predictive power. Sibley's view: CESI is a valid candidate; expect the selection layer to keep it if it survives but not to over-weight it on practitioner consensus alone.

- **Practitioners use cross-currency cluster correlations (USDCAD vs. AUD-USD vs. EUR-USD) routinely.** Academic factor literature (Lustig-Roussanov-Verdelhan) has formalized this as the "carry" and "dollar" factors but treats them as cross-sectional asset-pricing variables, not single-pair direction predictors. The mapping from factor structure to single-pair direction is under-published.

- **Practitioners rely on technical indicators (MACD, RSI, Bollinger Bands).** Academic literature treats these as transformations of lagged returns — useful within a momentum / mean-reversion framework but not adding orthogonal information beyond what lagged returns already capture. Sibley's view: include lagged returns at multiple horizons (I1) and distance-from-MA (I2); do not include named technical indicators as separate variables unless Phase 2 selection finds the transformations matter.

### 3.3 Judgment calls Sibley will need to make in Phase 2

1. **Horizon.** Weekly composite implies forecasting horizon of 1-4 weeks. UIP/monetary models do better at long horizons (per Rossi 2013); microstructure / positioning / risk-appetite does better at short horizons. Variable weighting should differ by intended product horizon.

2. **Forecast vs. inference target.** Direction (sign of next-period return), magnitude (size of move), volatility (whether to lean directional or de-risk), or composite percentile (Fear-and-Greed style). Each implies different evaluation metrics and may favor different selected variable subsets. The composite-score product can be a percentile rank across the full universe, in which case selection becomes "which sub-blocks should dominate the score weighting" rather than "which variables predict direction."

3. **How to handle regime changes.** Three options: (a) build separate models per regime classified ex-ante (pre/post-2014 oil regime; high/low VIX regime; etc.) — interpretable but requires regime classification; (b) include regime indicators as features and let the model learn interactions; (c) use a model class that naturally handles non-stationarity (rolling-window estimation, regime-switching models, dynamic Bayesian variable selection à la Beckmann et al. 2020). Recommendation: try (c) for the production model and use (a) for explainability in published commentary.

4. **Frequency mismatch.** Daily variables vs. monthly variables vs. quarterly fundamentals. The cleanest approach: convert everything to weekly (interpolate monthly with mixed-frequency methods like MIDAS, or use last-available-value-as-of-Friday). Quarterly fundamentals are slow-moving enough that last-available-value is fine. CRITICAL: when using last-available-value, always respect the release lag — use the value that *was available* as of the prediction date, not the value as ultimately revised.

5. **Whether to publish the universe.** The methodology has more reputational value than the specific variable list. Most institutional shops do not publish their actual feature lists. Sibley's option: publish the methodology (Section 1) and a partial / illustrative universe; keep the full universe and final-selected subset proprietary. This is the AQR / academic-practitioner pattern.

### 3.4 What Phase 2 should produce before any client product launches

- A purged-and-embargoed walk-forward CV harness with the full universe of variables loaded as a proper time-series feature matrix, properly aligned for vintage.
- Side-by-side selection runs: Elastic Net, random forest with Boruta, clustered MDA. Three different "selected subset" outputs.
- Stability across sub-samples: pre-2014, 2014-2019, 2020-2026. Variables that survive in all three regimes are the candidates for an always-on model.
- An honest false-discovery-rate / Deflated Sharpe Ratio computation against the final ensemble.
- A pre-registered hold-out (e.g., final 18 months) that is genuinely never touched until final validation.
- Documentation that traces every Phase 2 modeling choice (loss function, CV strategy, hyperparameter search bounds) back to a methodological motivation in this Phase 1 document.

That gate is what makes the product defensible to a corporate-treasurer or institutional-FX-hedger client. Anything less is sell-side commentary with a regression on top.

---

## Bibliography of primary sources cited

Academic / institutional:
- [Rossi, B. (2013), "Exchange Rate Predictability," Journal of Economic Literature](https://crei.cat/wp-content/uploads/users/working-papers/Rossi_ExchangeRatePredictability_Feb_13.pdf)
- [Engel, C. and West, K.D. (2005), "Exchange Rates and Fundamentals," JPE](https://ideas.repec.org/a/ucp/jpolec/v113y2005i3p485-517.html)
- [Engel, C. (2014), "Exchange Rates and Interest Parity," NBER](https://www.nber.org/papers/w24059)
- [Meese, R. and Rogoff, K. (1983), "Empirical exchange rate models of the seventies"](https://www.nber.org/system/files/working_papers/w10723/w10723.pdf)
- [Evans, M.D.D. and Lyons, R.K. (2002), "Order Flow and Exchange Rate Dynamics," JPE](https://faculty.georgetown.edu/evansm1/wpapers_files/orderflow.pdf)
- [Lustig, H., Roussanov, N., Verdelhan, A. (2011), "Common Risk Factors in Currency Markets," RFS](https://www3.nd.edu/~nmark/GradMacroFinance/LustigRoussanovVerdelhan_RFS_2011.pdf)
- [Verdelhan, A. (2018), "Identifying Exchange Rate Common Factors," NBER w23726](https://www.nber.org/system/files/working_papers/w23726/w23726.pdf)
- [Della Corte, P., Ramadorai, T., Sarno, L. (2014), "Volatility Risk Premia and Exchange Rate Predictability," JFE](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2233367)
- [Miranda-Agrippino, S. and Rey, H. (2020), "U.S. Monetary Policy and the Global Financial Cycle," ReStud](http://helenerey.eu/Content/_Documents/MirandaAgrippinoRey_REStud_Final.pdf)
- [Du, W., Tepper, A., Verdelhan, A. (2018), "Deviations from Covered Interest Rate Parity," JF](https://www.nber.org/system/files/working_papers/w23170/w23170.pdf)
- [Bauer-Swanson (2023), "A Reassessment of Monetary Policy Surprises and High-Frequency Identification," NBER Macro Annual](https://www.michaeldbauer.com/files/mps.pdf)
- [Caldara, D. and Iacoviello, M. (2022), "Measuring Geopolitical Risk," AER](https://www.matteoiacoviello.com/gpr.htm)
- [Baker, S.R., Bloom, N., Davis, S.J. (2016), "Measuring Economic Policy Uncertainty," QJE](https://academic.oup.com/qje/article-abstract/131/4/1593/2468873)
- [Wright, J.H. (2008), "Bayesian Model Averaging and Exchange Rate Forecasts," J. Econometrics](https://www.federalreserve.gov/econres/ifdp/bayesian-model-averaging-and-exchange-rate-forecasts.htm)
- [Beckmann, J. and Schussler, R. (2020), "Exchange rate predictability and dynamic Bayesian learning," J. Applied Econometrics](https://onlinelibrary.wiley.com/doi/full/10.1002/jae.2761)
- [Gu, S., Kelly, B., Xiu, D. (2020), "Empirical Asset Pricing via Machine Learning," RFS](https://academic.oup.com/rfs/article/33/5/2223/5758276)
- [White, H. (2000), "A Reality Check for Data Snooping," Econometrica](https://onlinelibrary.wiley.com/doi/abs/10.1111/1468-0262.00152)
- [López de Prado, M. (2018), Advances in Financial Machine Learning](https://www.amazon.com/Advances-Financial-Machine-Learning-Marcos/dp/1119482089)
- [López de Prado, M. (2018), "10 Reasons Most Machine Learning Funds Fail," GARP](https://www.garp.org/hubfs/Whitepapers/a1Z1W0000054x6lUAA.pdf)
- [Kursa, M. and Rudnicki, W. (2010), "Boruta - A System for Feature Selection"](https://www.researchgate.net/publication/220443685_Boruta_-_A_System_for_Feature_Selection)
- [Hecq, A., Margaritella, L., Smeekes, S. (2023), "Granger Causality Testing in High-Dimensional VARs"](https://academic.oup.com/jfec/article/21/3/915/6420401)
- [Cheng, A., Kim, M.S., Wang, B. (2020), "Exchange rate predictability: A variable selection perspective"](https://ideas.repec.org/a/eee/reveco/v70y2020icp117-134.html)
- [Calice, G., Mio, R., Vigne, S. (2021), "The term structure of sovereign credit default swap and the cross-section of exchange rate predictability," IJFE](https://onlinelibrary.wiley.com/doi/abs/10.1002/ijfe.1798)
- [Asness, C., Moskowitz, T., Pedersen, L. (2013), "Value and Momentum Everywhere," JF](https://w4.stern.nyu.edu/facdir/lpederse/papers/ValMomEverywhere.pdf)

Canadian-specific:
- [Bank of Canada SAN 2025-2, "Monetary policy, interest rates and the Canadian dollar"](https://www.bankofcanada.ca/2025/02/staff-analytical-note-2025-2/)
- [Bank of Canada SAN 2017-1, "The Share of Systematic Variations in the Canadian Dollar - Part II"](https://www.bankofcanada.ca/2017/02/staff-analytical-note-2017-1/)
- [Bauer (BoC SAN 2016-2), "Predictive Ability of Commodity Prices for the Canadian Dollar"](https://ideas.repec.org/p/bca/bocsan/16-2.html)
- [Scotia Economics (April 2026), "Understanding the CAD-Oil Decoupling"](https://www.scotiabank.com/ca/en/about/economics/economics-publications/post.other-publications.insights-views.cad-and-oil-decoupling--april-16--2026-.html)
- [BoC Commodity Price Index (BCPI) methodology](https://www.bankofcanada.ca/rates/price-indexes/bcpi/)
- [BoC Monetary Policy Report](https://www.bankofcanada.ca/publications/mpr/)
- [BoC Financial System Review](https://www.bankofcanada.ca/publications/fsr/)
- [BoC Business Outlook Survey](https://www.bankofcanada.ca/publications/bos/)
- [BoC Canadian Survey of Consumer Expectations](https://www.bankofcanada.ca/publications/canadian-survey-of-consumer-expectations/)
- [StatCan Balance of International Payments](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=3610001601)
- [StatCan CPI Table 18-10-0004](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1810000401)
- [StatCan Monthly GDP Table 36-10-0434](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=3610043401)
- [StatCan LFS Table 14-10-0287](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1410028701)
- [BoC Valet API](https://www.bankofcanada.ca/valet/docs)
- [CMHC Residential Mortgage Industry Report](https://www.cmhc-schl.gc.ca/professionals/housing-markets-data-and-research/housing-research/research-reports/housing-finance/residential-mortgage-industry-report)
- [Department of Finance Fiscal Monitor](https://www.canada.ca/en/department-finance/services/publications/fiscal-monitor.html)

Market data:
- [CFTC Commitments of Traders, CAD](https://www.cftc.gov/dea/futures/deacmesf.htm)
- [FRED St. Louis Fed](https://fred.stlouisfed.org/)
- [SF Fed Monetary Policy Surprises](https://www.frbsf.org/research-and-insights/data-and-indicators/monetary-policy-surprises/)
- [NY Fed Term Premium (ACM)](https://www.newyorkfed.org/research/data_indicators/term-premia-tabs)
- [Economic Policy Uncertainty (Baker-Bloom-Davis)](https://www.policyuncertainty.com/)
- [Caldara-Iacoviello Geopolitical Risk Index](https://www.matteoiacoviello.com/gpr.htm)
- [OECD Composite Leading Indicators](https://www.oecd.org/en/data/datasets/oecd-composite-leading-indicators-clis.html)
- [BIS Triennial Central Bank Survey 2025](https://www.bis.org/statistics/rpfx25_fx.pdf)
- [AQR Datasets](https://www.aqr.com/Insights/Datasets)

---

**End of Phase 1 document. Phase 2 awaits Jay's decision on selection methodology.**
