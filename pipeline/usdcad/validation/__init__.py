"""USDCAD adversarial validation suite.

Six stress tests for the Phase 3 findings:
  Test 1 -- Placebo / shuffle (permutation test)
  Test 2 -- Synthetic null X matrix
  Test 3 -- Bootstrap null distribution + multiple-testing correction
  Test 4 -- Alternative hold-out windows (alternative regimes)
  Test 5 -- Variable importance robustness (drop top-3 features)
  Test 6 -- Time-series block bootstrap CI on headline hit rates
"""
