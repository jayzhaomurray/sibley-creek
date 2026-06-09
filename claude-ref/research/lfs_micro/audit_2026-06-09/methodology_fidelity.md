# LFS-Micro Methodology Fidelity Audit

- **Date:** 2026-06-09
- **Auditor:** researcher (methodology-fidelity dispatch)
- **Scope:** AUDIT ONLY — no code or data modified.
- **Benchmark publication:** Bounajm, F., T. Devakos and G. Galassi, "Beyond the averages:
  Measuring underlying wage growth using Labour Force Survey microdata," Bank of Canada
  Staff Analytical Note 2024-23 (October 2024).
  URL: https://www.bankofcanada.ca/2024/10/staff-analytical-note-2024-23/
  (DOI 10.34989/san-2024-23 resolves to this HTML page; the note is published in full as
  HTML. The guessed PDF path `/wp-content/uploads/2024/10/san2024-23.pdf` returns 404.)
- **Benchmark series:** BoC Valet `INDINF_LFSMICRO_M` (y/y %, monthly, published to 1 decimal).
- **Our implementation:** `pipeline/lfs_micro/` (spec.py, regression.py, decompose.py,
  engine.py, run.py) + `pipeline/lfs_pumf/harmonize.py`, on the LFS PUMF.
- **Claimed fit audited against:** RMSE 0.118pp, corr 0.9966, max miss 0.29pp, n=123
  (calibration_report.md, "Recalibration on clean data (2026-06-05 PM)": RMSE 0.1178,
  corr 0.9966, max 0.286pp — claims check out against the internal record).

All note citations below were fetched 2026-06-09 from the URL above. The note has no
page numbers in HTML form; citations reference section names and footnote numbers.

---

## Headline finding: the premise of the audit brief is wrong, in our favour

**The Bank's primary LFS-Micro measure is built on the PUMF, not the confidential master
files.** The note states the PUMF is "timely and publicly available, which allows other
users to reproduce our results" (Data and methodology section), and uses the master files
only for robustness checks: the non-permanent-resident classification check and the
new-survey-entrants check (footnote 11), plus the occupation-homogenization discussion
(footnote 12: "a few variables are coded differently in the PUMF than in the master
files... We made all other definitions consistent between the PUMF and the master files").

Consequence: the residual 0.118pp RMSE **cannot be attributed to PUMF-vs-master data
differences**. We are running on the same input file the Bank runs on. Whatever residual
remains is spec, vintage, or reporting-convention difference — i.e., in principle
closable. (The internal calibration_report.md "Notes" section already records this
correctly; the audit brief's premise was stale.)

---

## Divergence table

Legend for divergence type: **faithful** / **forced-by-PUMF-limitation** /
**deliberate-choice** / **possible-error** / **note-silent** (the note does not specify;
our choice resolved by calibration or judgment).

| # | Dimension | BoC note says (citation) | Our code does | Divergence type | Expected effect on fit |
|---|-----------|--------------------------|---------------|-----------------|------------------------|
| 1 | **Data file** | PUMF for the main measure; master files for robustness only (Data and methodology; footnotes 3, 4, 11, 12) | LFS PUMF, hist/ annual bundles + monthly zips (`pipeline/lfs_pumf/download.py`) | **faithful** | None — same input data. Eliminates the presumed "master-file gap." |
| 2 | **Wage variable** | "usual hourly earnings of employees at their main job before taxes and deductions and including tips and commissions" (Data and methodology) | PUMF `HRLYEARN`/100 (exactly that variable per StatCan codebook); positive-wage filter (`harmonize.py::_apply_employee_filter`) | **faithful** | None. HRLYEARN is not top-coded in current vintages (phase0 spike: max $250/hr, freq 1). |
| 3 | **Sample** | Employees at main job; no stated age restriction; public and private both in (sector is a covariate) | `lfsstat ∈ {1,2}` AND `cowmain ∈ {1,2}` AND `hrlyearn > 0`; no age restriction; both sectors in | **faithful** | None. COWMAIN {1,2} = public/private employees, excludes self-employed incl. incorporated-with-paid-help (cowmain=3), matching "employees." |
| 4 | **Dependent variable** | "log of wages" — semi-log preferred for fit (footnote 9) | `np.log(wage)` (`regression.py::run_wls`) | **faithful** | None. |
| 5 | **Regression timing** | "period-by-period regressions of wages on workers' characteristics" — separate cross-sections (Data and methodology) | One WLS per month, two regressions per y/y pair (t, t−12) on a union category universe (`engine.py::_compute_one_yoy`) | **faithful** | None. |
| 6 | **Covariate list** | Footnote 5 (verbatim): "occupation, educational attainment, job tenure, age, gender, multiple-job holding status, unionization status, full- versus part-time status, province of residence, permanent versus temporary status, marital status and immigration status... Additionally... industry, public versus private sector status, establishment size and firm size (available only since 2006)." | All 16 present in `REGRESSOR_GROUPS` (regression.py): noc_43, educ, tenure_bin, age_12, gender, union_status, ftptmain, prov, permtemp, marstat, immig, naics_21, cowmain_pub, estsize, mjh, firmsize | **faithful** (complete coverage) | None at list level. Granularity differences below. |
| 7 | **Occupation granularity** | "two-digit version of the 2021 National Occupation Classification system, which is the classification available in the master files"; occupation is "particularly difficult to homogenize" between PUMF and master (footnote 12) | PUMF `NOC_43` (43 sub-major groups, NOC 2021) | **faithful-with-caveat** | Small. The PUMF's 43-group variable is the closest public analogue to the 2-digit (45-group) NOC the Bank standardized on; footnote 12 implies they harmonized PUMF↔master to a common occupation coding, which on the PUMF side can only be NOC_43 or coarser. A couple of merged groups vs the master 2-digit could leave a few-bps residual in the occupation composition term. |
| 8 | **Age granularity** | "age" — granularity unspecified (footnote 5) | PUMF `AGE_12` (12 five-year groups) | **note-silent** | Negligible. On PUMF the Bank had the same 12-group variable available (master has single years, but the main measure is PUMF-based). |
| 9 | **Tenure treatment** | "job tenure" — functional form and binning unspecified (footnote 5) | PUMF `TENURE` (continuous months 1–240, capped at 240) binned to 5 brackets [0,12,36,60,120,∞) (`harmonize.py::_bin_tenure`; `spec.tenure_bins`) | **deliberate-choice** (note-silent) | Probably the largest single remaining covariate-spec uncertainty. If the Bank entered tenure continuously, in logs, or with finer bins, both the tenure composition term and the residual coefficients shift slightly. Phase-0 spike showed 240 month-dummies ≈ 5 bins in R² ("negligible R² impact"), so expected effect is small — likely single-digit bps on RMSE — but this is testable (see Recommendations). PUMF's 240-month cap is moot given the 120m+ top bracket. |
| 10 | **Survey weights in regression** | Not stated. Only: both file types "include the main survey variables and the weights required to reproduce key statistics, including average wage growth" (Data and methodology) | WLS with `FINALWT` (sqrt-weight scaling, `regression.py`); weighted means for E(X) and E(log W) | **note-silent**, resolved by calibration | Weighted E(X) is forced (population shares are meaningless unweighted). Weighted vs unweighted **coefficients** was calibrated: weighted clearly better (calibration grid, 2026-06-05). Supports the conclusion the Bank weights. No evidence of hours-weighting anywhere in the note; we correctly do not hours-weight. |
| 11 | **Decomposition formula** | ΔE(W_t) = [E(X_{t+1})−E(X_t)]′B_t (Composition) + E(X_t)′(B_{t+1}−B_t) (Underlying) + [E(X_{t+1})−E(X_t)]′(B_{t+1}−B_t) (Interaction), with t the earlier period (Data and methodology, displayed equation) | `ob_reference="base"`: Composition = ΔX′B_{t−12}, Underlying = X_{t−12}′ΔB (`decompose.py::oaxaca_blinder`) | **faithful** | None. The note's B_t and E(X_t) are *base-period* quantities (t is the earlier period; t+1 the later). Our "base" reference is an exact match. **Flag (doc, not code):** `spec.py`'s docstring says "the note doesn't specify explicitly. Calibration picks." This is a misreading — the note's equation DOES pin the reference to base. Calibration happened to pick base anyway (Δ vs current ≈ 0.001pp), so no numerical consequence, but the docstring and the calibration framing should not claim ambiguity. |
| 12 | **Interaction term** | "very small and is excluded from our results" (text at the decomposition; cf. footnote 9 on non-additivity) | Two-fold decomposition; interaction computed only as a diagnostic, excluded from headline (`decompose.py`) | **faithful** | None. |
| 13 | **Growth horizon (y/y construction)** | Equation written generically for t→t+1; the published series and all charts are year-over-year. Whether the Bank decomposes t vs t−12 directly or chains higher-frequency decompositions is **not stated** | Direct t vs t−12 decomposition, one y/y pair per month (`engine.py::_subtract_12_months`) | **note-silent**, empirically resolved | Direct y/y is near-certainly what the Bank does: chaining 12 monthly decompositions would compound composition drift differently and could not produce corr 0.9966 against our direct construction. Residual risk ~nil. |
| 14 | **Log-points → percent conversion** | Not stated. Footnote 9: with logs, "average wage growth is no longer exactly the sum of Micro-LFS wage growth and compositional effects" — consistent with components reported in log-difference form | `pct = (exp(lp) − 1) × 100` (`engine.py::_convert_lp_to_pct`) | **possible-error** — the single most actionable open item | Potentially material relative to the remaining RMSE. At lp = 0.035 (3.5% growth), exp()−1 reports 3.562% vs 3.5% for lp×100 — a level-dependent +0.06pp wedge. If the Bank reports 100×Δlog (a common convention, and one reading of footnote 9), our exp()−1 convention injects a systematic positive bias that grows with the wage-growth level. The calibration tables show a positive mean residual (+0.10 to +0.12pp avg over recent 12 months in the MA3-era tables), consistent in sign. **Cheap test:** recompute the fit with `underlying_pct = lp × 100`; if RMSE drops and the level-correlation of residuals vanishes, this closes a real chunk of the gap. |
| 15 | **Smoothing** | None mentioned for the monthly series | `smoothing="raw"` (no smoothing) after 2026-06-05 recalibration; MA3 retired | **faithful** | None. Roughness diagnostics (std of m/m changes 0.295 BoC vs 0.293 ours; change autocorr ≈ 0 both) independently confirm the BoC series is unsmoothed. |
| 16 | **2006 outlier-detection correction** | Footnote 8: StatCan's 2023 LFS revision changed outlier detection, artificially driving up wage growth in H1 2006; "We correct for this in the methodology for LFS-Micro" | No 2006 correction; no outlier trimming at all | **faithful within our window** | None for 2016+ (our replication window). Two caveats: (a) if we ever extend the series pre-2016, the 2006 correction must be implemented; (b) the footnote's phrasing leaves a small ambiguity about whether the Bank applies any *ongoing* wage-outlier treatment beyond the 2006 episode — the corr 0.9966 says not materially, but it is unverifiable from the note text. |
| 17 | **Sample period** | Series history from 1997–98 (Table 1 covers 1998Q2 onward) | 2016-01 onward (2015 base year), by design ("release-morning PUMF tool; not a full-history replication" — run.py meta notes) | **deliberate-choice** | None on the overlap window; fit stats are computed on the overlap only. |
| 18 | **Thin-cell handling** | Not mentioned | `min_cell_count=30` drop + pair-local union rule for category universes | **deliberate-choice** (our addition) | Measured: union-vs-intersection sensitivity max 0.003pp on the series (calibration_report.md, 2026-06-05). Inconsequential. |
| 19 | **Wage carry-forward imputation** | Footnotes 2 and 11: respondents not re-asked wages unless employment changes; wage carried forward; ~two-thirds update at least once in 6 months | Nothing — this is a property of the input data, identical in our PUMF and theirs | **faithful** (shared data artifact) | None vs the BoC series (both inherit the same lag); relevant only for interpreting the measure against true wage dynamics. |
| 20 | **Reporting precision of benchmark** | Valet `INDINF_LFSMICRO_M` published to 1 decimal place (e.g., 3.5, 3.2 — confirmed by every value in the calibration tables) | Full precision | structural, not a divergence | Rounding of the benchmark alone contributes ~0.029pp to measured RMSE (uniform ±0.05 → σ = 0.05/√3). Net of rounding, true spec RMSE ≈ √(0.118² − 0.029²) ≈ 0.114pp. This is an irreducible floor unless the Bank publishes more decimals. |

---

## Misreadings flagged (highest-value findings)

1. **Audit brief / project framing: "the Bank uses confidential master files" — wrong.**
   The note is explicit that the main measure is PUMF-based for reproducibility; master
   files appear only in robustness checks (footnotes 3, 4, 11, 12). This inverts the
   verdict logic: the residual is NOT a data gap, it is a spec/reporting gap.

2. **`spec.py` docstring: "Both are valid; the note doesn't specify explicitly.
   Calibration picks" (re: ob_reference) — misreading.** The note's displayed equation
   prices the composition effect at base-period coefficients B_t and underlying growth at
   base-period characteristics E(X_t) (t = earlier period). The reference IS specified:
   base. We landed on base via calibration, so the code is right for a
   partially-documented reason. Doc fix only.

3. **exp()−1 conversion treated as settled — it is not.** engine.py asserts the
   conversion "matches" the BoC scale, but the note never says how log components are
   converted to percent, and footnote 9's non-additivity remark reads most naturally as
   components reported in log-difference form. The sign and level-dependence of our
   residuals are consistent with the Bank reporting 100×Δlog. Untested to date.

---

## Verdict

**The 0.118pp RMSE is NOT explained by PUMF-vs-master data differences — the Bank uses
the same PUMF we do.** The replication is spec-faithful on every dimension the note pins
down: sample, wage variable, log specification, period-by-period regressions, the full
16-covariate list, base-reference two-fold Oaxaca-Blinder with the interaction excluded,
direct y/y horizon, and no smoothing.

The remaining 0.118pp decomposes into, in rough order of expected size:

1. **Benchmark rounding floor: ~0.029pp** (BoC publishes 1 decimal) — irreducible.
2. **Log-points→percent convention (item 14): plausibly up to ~0.05pp of systematic,
   level-dependent bias** if the Bank reports 100×Δlog and we report exp()−1. This is
   the one remaining lever that is both cheap to test and plausibly material.
3. **Tenure functional form (item 9) and occupation coding (item 7): small**, likely
   single-digit bps each.
4. **Vintage effects**: the Bank computes each month on the then-current PUMF; our
   hist/ bundles are the Feb 2025 revised re-release. Pre-2025 BoC values were computed
   on pre-revision vintages and (per the divergence diagnosis) the BoC has not restated
   its published history — unavoidable without real-time vintages.

**Recommended next test (one run, no recalibration grid needed):** recompute fit with
`underlying_pct = underlying_lp × 100` instead of `(exp(lp)−1)×100`, and regress the
current residuals on the BoC level. If RMSE improves and the level-dependence of
residuals disappears, adopt lp×100 as the reporting convention and re-document. If not,
the exp()−1 convention stands and the residual is rounding + vintage + minor covariate
form — i.e., effectively at the floor.

Also recommended (doc-only): correct the `spec.py` ob_reference docstring and the
calibration report's "reference convention" line to record that the note's equation
specifies the base reference.
