"""USDCAD Phase 3 pipeline orchestrator.

Phase 3 corrections applied:
  - Sign-assignment look-ahead eliminated (signs from first half of training data only)
  - True 20% hold-out reserved before any model fitting, evaluated exactly once
  - All variable selection confined to training 80%
  - HTML diagnostics updated with hold-out section and transformation audit

Run this to execute the full Phase 3 pipeline:
  1. Data acquisition (all free-source variables, skip with --skip-acquisition)
  2. Target construction (3 horizon returns)
  3. Full Phase 3 methodology stack per horizon
  4. HTML diagnostic companions (overwrite existing work/research/usdcad/*.html)
  5. Findings summary (overwrites work/research/usdcad/usdcad_findings_summary_2026-05-26.md)

Usage:
    python -m pipeline.usdcad.run
    python -m pipeline.usdcad.run --skip-acquisition   # reuse existing data

Environment:
    FRED_API_KEY -- required for FRED-sourced variables. Set in env or .env file.

Time estimate: ~20-40 minutes for full run (data acquisition + model fitting).
"""

from __future__ import annotations

import json
import logging
import os
import sys
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

# Add project root to path
project_root = Path(__file__).parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


def run_full_pipeline(skip_acquisition: bool = False) -> None:
    """Run the full USDCAD Phase 2 pipeline."""
    from pipeline.usdcad.acquire import run_acquisition, build_targets
    from pipeline.usdcad.model import run_all_horizons
    from pipeline.usdcad.diagnose import generate_all_diagnostics

    # Step 1: Data acquisition
    if not skip_acquisition:
        logger.info("=== STEP 1: Data acquisition ===")
        try:
            panel = run_acquisition()
            logger.info("Acquisition complete: %d features, %d rows", len(panel.columns), len(panel))
        except Exception as e:
            logger.error("Acquisition failed: %s", e, exc_info=True)
            raise
    else:
        logger.info("Skipping acquisition (skip_acquisition=True)")

    # Step 2: Target construction
    logger.info("=== STEP 2: Target construction ===")
    try:
        targets = build_targets()
        logger.info("Targets built: %d rows", len(targets))
    except Exception as e:
        logger.error("Target construction failed: %s", e, exc_info=True)
        raise

    # Step 3: Methodology stack
    logger.info("=== STEP 3: Methodology stack (all horizons) ===")
    results = run_all_horizons()
    logger.info("Methodology complete for %d horizons", len(results))

    for horizon, hr in results.items():
        v = hr.validation
        logger.info(
            "  %s: %d features -> %d selected | CV hit=%.1f%% | HO hit=%.1f%% | DSR=%.2f",
            horizon, hr.n_features_input, len(hr.selection.final_selected),
            v.cv_hit_rate * 100, v.holdout_hit_rate * 100, v.dsr,
        )

    # Step 4: HTML diagnostics
    logger.info("=== STEP 4: HTML diagnostic companions (Phase 3) ===")
    try:
        generate_all_diagnostics(results)
    except Exception as e:
        logger.error("Diagnostic generation failed: %s", e, exc_info=True)

    # Step 5: Findings summary
    logger.info("=== STEP 5: Findings summary ===")
    _write_findings_summary(results)

    # Step 6: Pickle model results for adversarial validation suite
    _save_results_pickle(results)

    logger.info("=== Phase 3 pipeline complete ===")
    logger.info("  data/processed/usdcad_model_results.pkl")
    logger.info("Outputs:")
    logger.info("  data/raw/usdcad/         -- raw variable CSVs")
    logger.info("  data/processed/usdcad_variables.parquet")
    logger.info("  data/processed/usdcad_targets.parquet")
    for h in ["weekly", "monthly", "quarterly"]:
        logger.info("  work/research/usdcad/usdcad_diagnostic_%s_2026-05-26.html", h)
    logger.info("  work/research/usdcad/usdcad_findings_summary_2026-05-26.md")


def _save_results_pickle(results: dict) -> None:
    """Pickle HorizonResult objects for use by the adversarial validation suite.

    The pickle includes the full HorizonResult (X_train, X_holdout, score arrays,
    feature_signs, validation metrics) so the validation suite does not need to
    re-run the pipeline for post-hoc tests (Tests 3 and 6).
    """
    import pickle
    pkl_path = project_root / "data" / "processed" / "usdcad_model_results.pkl"
    pkl_path.parent.mkdir(parents=True, exist_ok=True)
    with open(pkl_path, "wb") as f:
        pickle.dump(results, f, protocol=pickle.HIGHEST_PROTOCOL)
    logger.info("Model results pickled: %s", pkl_path)


def _write_findings_summary(results: dict) -> None:
    """Write Phase 3 terse findings summary."""
    out = project_root / "work" / "research" / "usdcad" / "usdcad_findings_summary_2026-05-26.md"
    out.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "# USDCAD Phase 3 — Findings Summary",
        "",
        "**Produced:** 2026-05-26",
        "**Status:** Internal analytical work product. Not for publication.",
        "**Phase 3 corrections:** Sign-assignment look-ahead eliminated; true 20% hold-out evaluated once.",
        "",
        "---",
        "",
        "## Executive answer",
        "",
        "Phase 2 had one correctness bug: Spearman signs for the composite score were computed",
        "on the full dataset (including test data), creating mild in-sample alignment that inflated",
        "the CV hit rate. Phase 3 fixes this and adds a genuine 20% hold-out.",
        "",
        "The hold-out result is the only number that can be cited to subscribers.",
        "",
    ]

    for horizon, hr in results.items():
        v = hr.validation
        s = hr.selection
        lines.extend([
            f"---",
            "",
            f"## {horizon.capitalize()} horizon ({hr.horizon_h} business days)",
            "",
            f"**Training period:** {hr.X_train.index.min().date()} to {hr.X_train.index.max().date()} "
            f"({len(hr.X_train)} rows)",
            f"**Hold-out period:** {v.holdout_start_date} to {v.holdout_end_date} "
            f"({v.holdout_n_obs} rows)",
            "",
            "### CV performance (training 80%, corrected signs)",
            "",
            f"- Features selected: {len(s.final_selected)} of {hr.n_features_input} candidates (2/3-vote)",
            f"- CV hit rate: {v.cv_hit_rate:.1%} (corrected; Phase 2 number is not comparable)",
            f"- CV OOS R^2: {v.cv_r2_oos:.4f}",
            f"- Deflated Sharpe Ratio: {v.dsr:.2f} (0.95+ = credible after {v.n_trials} trials)",
            f"- Training extreme edge: {v.hit_rate_extreme:.1%} vs {v.hit_rate_middle:.1%} "
            f"({(v.hit_rate_extreme - v.hit_rate_middle)*100:+.1f}pp, {v.n_extreme_obs} obs)",
            "",
            "### Hold-out performance (the honest number)",
            "",
            f"- **Overall hit rate: {v.holdout_hit_rate:.1%}** (n={v.holdout_n_obs})",
            f"- **R^2: {v.holdout_r2:.4f}**",
            f"- **Sharpe: {v.holdout_sharpe:.2f}**",
            f"- **Extremes: {v.holdout_hit_rate_extreme:.1%} vs {v.holdout_hit_rate_middle:.1%}** "
            f"({(v.holdout_hit_rate_extreme - v.holdout_hit_rate_middle)*100:+.1f}pp, "
            f"{v.holdout_n_extreme_obs} extreme obs)",
            "",
            "**Regime breakdown (training):**",
            "",
        ])
        for reg, stats_r in v.regime_stats.items():
            lines.append(f"- {reg}: hit {stats_r['hit_rate']:.1%}, R^2 {stats_r['r2']:.4f} (n={stats_r['n_obs']})")
        lines.extend([
            "",
            "**Selected features:** " + ", ".join(s.final_selected),
            "",
            hr.honest_assessment,
            "",
        ])

    lines.extend([
        "---",
        "",
        "## Data gaps (unchanged from Phase 2)",
        "",
        "- **Citi CESI differential** (Bloomberg): most important missing variable.",
        "  Every major FX desk uses CESI. Biggest gap vs institutional-grade model.",
        "- **USDCAD options data** (Bloomberg): risk reversals and implied vol (D5-D9) --",
        "  strongest USDCAD-specific signals per Della Corte-Ramadorai-Sarno (2014).",
        "- **CFTC COT positioning** (D1-D3): CAD net speculative positioning. CFTC URL changed.",
        "- **StatCan portfolio flow vectors**: E1-E2 fetched but require post-processing.",
        "- **Tariff NLP**: H6 (GDELT tariff news) deferred -- high value for 2025-2026 regime.",
        "",
        "## What Phase 3 has established",
        "",
        "1. The sign-assignment bug from Phase 2 is fixed. CV results are now reliable.",
        "2. The hold-out test is the new baseline for any product claim.",
        "3. Transformation audit (Section 12 of each diagnostic HTML) documents every variable's",
        "   transformation explicitly. The one deliberate stationarity compromise (commodity price",
        "   levels) is noted and justified by the cointegration literature.",
        "4. Phase 4 robustness checks: winsorization; commodity returns vs levels; walk-forward signs.",
        "",
        "## Product positioning (post-Phase 3)",
        "",
        "See honest_assessment sections per horizon above. The hold-out result determines",
        "which of three positions applies: (a) scorecard + trade ideas at extremes,",
        "(b) scorecard only (no predictive claim), (c) hold pending more data.",
        "",
        "---",
        "",
        "**Diagnostic companions** (Phase 3, overwrite Phase 2 files):",
        "- `work/research/usdcad/usdcad_diagnostic_weekly_2026-05-26.html`",
        "- `work/research/usdcad/usdcad_diagnostic_monthly_2026-05-26.html`",
        "- `work/research/usdcad/usdcad_diagnostic_quarterly_2026-05-26.html`",
        "",
        "**Methodology paper:** `claude-ref/research/usdcad/usdcad_methodology_paper_2026-05-26.md`",
    ])

    out.write_text("\n".join(lines), encoding="utf-8")
    logger.info("Findings summary written: %s", out)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="USDCAD Phase 2 pipeline")
    parser.add_argument("--skip-acquisition", action="store_true",
                        help="Skip data fetch (use existing data/processed files)")
    args = parser.parse_args()
    run_full_pipeline(skip_acquisition=args.skip_acquisition)
