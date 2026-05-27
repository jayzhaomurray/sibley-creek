"""USDCAD adversarial validation runner.

Loads Phase 3 model results from pickle, runs all 6 tests,
writes the markdown report to work/research/usdcad/.

Usage:
    python -m pipeline.usdcad.validation.run

Flags:
    --tests 1,3,6        run only specified tests (default: all)
    --seeds 0,7,42       override seeds for Test 1 (default: 0,7,42,137,999)
    --n-bootstrap 5000   bootstrap iterations for Tests 3+6 (default: 5000/10000)
    --fast               reduced scope: 3 seeds T1, 1 sim T2, 1000 bootstrap T3/T6
                         (for quicker iteration; mark report as FAST MODE)
"""

from __future__ import annotations

import argparse
import logging
import pickle
import sys
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s -- %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

_project_root = Path(__file__).parents[4]
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))


def _load_phase3_results() -> dict:
    """Load pickled Phase 3 HorizonResult objects.

    Falls back to running the pipeline inline if no pickle exists.
    The inline run uses --skip-acquisition (requires data/processed/ to be populated).
    """
    pkl_path = _project_root / "data" / "processed" / "usdcad_model_results.pkl"
    if pkl_path.exists():
        with open(pkl_path, "rb") as f:
            results = pickle.load(f)
        logger.info("Loaded Phase 3 results from pickle: %s", list(results.keys()))
        return results

    logger.warning(
        "No pickle found at %s. Running Phase 3 pipeline inline "
        "(skip-acquisition). This will take ~9 minutes.", pkl_path
    )
    from pipeline.usdcad.model import run_all_horizons
    results = run_all_horizons()

    # Save the pickle for future runs
    import pickle as _pickle
    pkl_path.parent.mkdir(parents=True, exist_ok=True)
    with open(pkl_path, "wb") as f:
        _pickle.dump(results, f, protocol=_pickle.HIGHEST_PROTOCOL)
    logger.info("Pipeline complete; pickle saved to %s", pkl_path)
    return results


def _run_all_tests(
    phase3_results: dict,
    test_ids: list[int],
    seeds: list[int],
    n_bootstrap_t3: int,
    n_bootstrap_t6: int,
    n_sims_t2: int,
) -> dict:
    """Run selected tests and return results dict."""
    from pipeline.usdcad.validation.adversarial import (
        run_test1_placebo,
        run_test2_synthetic_null,
        run_test3_bootstrap_null,
        run_test4_alt_holdouts,
        run_test5_drop_top_features,
        run_test6_block_bootstrap_ci,
    )

    all_results = {}

    if 1 in test_ids:
        logger.info(">>> Running Test 1: Placebo / shuffle (%d seeds)", len(seeds))
        all_results["test1"] = run_test1_placebo(phase3_results, seeds=seeds)

    if 2 in test_ids:
        logger.info(">>> Running Test 2: Synthetic null X (%d sims)", n_sims_t2)
        all_results["test2"] = run_test2_synthetic_null(phase3_results, n_sims=n_sims_t2)

    if 3 in test_ids:
        logger.info(">>> Running Test 3: Bootstrap null distribution (%d iterations)", n_bootstrap_t3)
        all_results["test3"] = run_test3_bootstrap_null(phase3_results, n_bootstrap=n_bootstrap_t3)

    if 4 in test_ids:
        logger.info(">>> Running Test 4: Alternative hold-out windows")
        all_results["test4"] = run_test4_alt_holdouts(phase3_results)

    if 5 in test_ids:
        logger.info(">>> Running Test 5: Drop top-3 features")
        all_results["test5"] = run_test5_drop_top_features(phase3_results)

    if 6 in test_ids:
        logger.info(">>> Running Test 6: Block bootstrap CIs (%d iterations)", n_bootstrap_t6)
        all_results["test6"] = run_test6_block_bootstrap_ci(
            phase3_results, n_bootstrap=n_bootstrap_t6
        )

    return all_results


def _write_report(
    all_results: dict,
    phase3_results: dict,
    fast_mode: bool,
    output_path: Path,
) -> None:
    """Write the adversarial validation markdown report."""
    from pipeline.usdcad.validation.report import build_report
    text = build_report(all_results, phase3_results, fast_mode=fast_mode)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(text, encoding="utf-8")
    logger.info("Report written: %s", output_path)


def main() -> None:
    parser = argparse.ArgumentParser(description="USDCAD adversarial validation")
    parser.add_argument(
        "--tests", type=str, default="1,2,3,4,5,6",
        help="Comma-separated test IDs to run (default: all)"
    )
    parser.add_argument(
        "--seeds", type=str, default="0,7,42,137,999",
        help="Comma-separated seeds for Test 1"
    )
    parser.add_argument(
        "--n-bootstrap", type=int, default=None,
        help="Bootstrap iterations for Tests 3 and 6"
    )
    parser.add_argument(
        "--fast", action="store_true",
        help="Fast mode: fewer seeds/sims/iterations for quick iteration"
    )
    args = parser.parse_args()

    test_ids = [int(x.strip()) for x in args.tests.split(",")]
    seeds = [int(x.strip()) for x in args.seeds.split(",")]

    if args.fast:
        seeds = seeds[:3]
        n_sims_t2 = 1
        n_bootstrap_t3 = 1000
        n_bootstrap_t6 = 1000
        logger.info("FAST MODE: reduced scope")
    else:
        n_sims_t2 = 3
        n_bootstrap_t3 = args.n_bootstrap or 10000
        n_bootstrap_t6 = args.n_bootstrap or 5000

    phase3_results = _load_phase3_results()

    logger.info("Running tests: %s", test_ids)
    all_results = _run_all_tests(
        phase3_results,
        test_ids=test_ids,
        seeds=seeds,
        n_bootstrap_t3=n_bootstrap_t3,
        n_bootstrap_t6=n_bootstrap_t6,
        n_sims_t2=n_sims_t2,
    )

    output_path = (
        _project_root / "work" / "research" / "usdcad"
        / "usdcad_adversarial_validation_2026-05-26.md"
    )
    _write_report(all_results, phase3_results, fast_mode=args.fast, output_path=output_path)
    logger.info("=== Adversarial validation complete ===")
    logger.info("Report: %s", output_path)


if __name__ == "__main__":
    main()
