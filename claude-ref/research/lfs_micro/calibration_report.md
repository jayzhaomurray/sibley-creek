# LFS-micro Calibration Report

Generated: 2026-06-05 05:32 UTC

## Calibration grid results

Benchmark: BoC Valet `INDINF_LFSMICRO_M` (y/y %, monthly)
Overlap window: 2016-01 onwards (PUMF y/y starts 2016 with 2015 base year)

| weighted | smoothing | ob_reference | RMSE | MAE | corr | n |
|----------|-----------|--------------|------|-----|------|---|
| True | raw | base | 0.7234 | 0.2032 | 0.8493 | 101 |
| True | raw | current | 0.7328 | 0.2086 | 0.848 | 101 |
| True | ma3 | base | 0.4195 | 0.2277 | 0.9392 | 100 | **WINNER**
| True | ma3 | current | 0.4232 | 0.2296 | 0.9401 | 100 |
| False | raw | base | 0.7359 | 0.3344 | 0.8413 | 101 |
| False | raw | current | 0.7601 | 0.3401 | 0.8393 | 101 |
| False | ma3 | base | 0.5155 | 0.328 | 0.9065 | 100 |
| False | ma3 | current | 0.5312 | 0.3309 | 0.9066 | 100 |

## Winning Spec

- weighted: True
- smoothing: ma3
- ob_reference: base
- min_cell_count: 30

RMSE: 0.4195 pp
MAE:  0.2277 pp
corr: 0.9392
Overlap: 2016-02-01 to 2025-04-01 (n=100)

## Last 12 months comparison (ours vs BoC)

| date | ours | BoC | diff |
|------|------|-----|------|
| 2024-02-01 | 3.73 | 3.6 | +0.130 |
| 2024-03-01 | 3.613 | 3.4 | +0.213 |
| 2024-04-01 | 3.696 | 3.6 | +0.096 |
| 2024-05-01 | 5.981 | 3.9 | +2.081 |
| 2024-06-01 | 6.149 | 4.3 | +1.849 |
| 2024-07-01 | 6.215 | 4.1 | +2.115 |
| 2024-08-01 | 4.098 | 4.1 | -0.002 |
| 2024-09-01 | 4.191 | 3.9 | +0.291 |
| 2024-10-01 | 4.154 | 4.3 | -0.146 |
| 2024-11-01 | 4.058 | 3.8 | +0.258 |
| 2024-12-01 | 4.854 | 3.6 | +1.254 |
| 2025-04-01 | 3.486 | 3.5 | -0.014 |

## NAICS spot-check

NAICS_21 codes are identical between 2015-01 and 2026-04 — Feb 2025 re-release consistently applied NAICS 2022 throughout history.

- Early month: 2015-01
- Late month:  2026-04
- Consistent:  True

## Runtime

Full refresh (download + harmonize + 8-spec grid): 1997 seconds

## Notes

- Composition effect captures employment-share shifts across categories.
- Underlying wage growth = wage-return changes for a fixed worker mix.
- BoC SAN 2024-23 uses y/y % on the same PUMF data; near-exact replication
  is achievable since we use the same source. Residual divergence comes from
  exact spec choices (reference convention, smoothing, bin granularity).
- Log-point to percent conversion: pct = (exp(log_pt) - 1) * 100.
  For values near 3-4%, this differs from raw log-points by <0.1pp.
