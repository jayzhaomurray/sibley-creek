# LFS-micro Calibration Report

Generated: 2026-06-05 06:08 UTC

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

## NAICS spot-check

NAICS_21 codes are identical between 2015-01 and 2026-04 — Feb 2025 re-release consistently applied NAICS 2022 throughout history.

- Early month: 2015-01
- Late month:  2026-04
- Consistent:  True

## Runtime

Full refresh (download + harmonize + 8-spec grid): 2164 seconds

## Notes

- Composition effect captures employment-share shifts across categories.
- Underlying wage growth = wage-return changes for a fixed worker mix.
- BoC SAN 2024-23 uses y/y % on the same PUMF data; near-exact replication
  is achievable since we use the same source. Residual divergence comes from
  exact spec choices (reference convention, smoothing, bin granularity).
- Log-point to percent conversion: pct = (exp(log_pt) - 1) * 100.
  For values near 3-4%, this differs from raw log-points by <0.1pp.
