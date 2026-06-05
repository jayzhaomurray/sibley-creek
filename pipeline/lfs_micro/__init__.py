"""LFS-micro Oaxaca-Blinder composition-adjusted wage growth engine.

Replicates BoC Staff Analytical Note 2024-23 (Bounajm/Devakos/Galassi):
composition-adjusted y/y wage growth via Oaxaca-Blinder two-fold
decomposition of weighted log-wage regressions on monthly LFS PUMF
cross-sections.

Pipeline:
  1. harmonize.harmonize() -> canonical employee DataFrame
  2. regression.run_wls() -> coefficient vector B_t for month t
  3. decompose.oaxaca_blinder() -> two-fold O-B decomposition
  4. engine.run_engine() -> monthly series of underlying/composition/raw growth

Spec (frozen pydantic model):
  weighted:      bool   - use WLS weights (True) or OLS (False)
  smoothing:     str    - "raw" | "ma3" (3-month centred moving average)
  ob_reference:  str    - "base" | "current" (Oaxaca-Blinder reference period)
  tenure_bins:   list   - bin edges for tenure (default [0,12,36,60,120,inf])
  min_cell_count: int   - minimum observations per cell for inclusion
"""
