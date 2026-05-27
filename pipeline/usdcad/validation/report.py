"""USDCAD adversarial validation -- report builder.

Converts test result dataclasses into the final markdown document.
Each section follows the spec: what it tests, expected, found, verdict.
Final section: per-horizon overall verdict with ship/hold/scorecard-only call.
"""

from __future__ import annotations

import math
from typing import Any


def _fmt(v: float, pct: bool = False, dp: int = 1) -> str:
    """Format a float cleanly; handle nan."""
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return "n/a"
    if pct:
        return f"{v:.{dp}%}"
    return f"{v:.{dp}f}"


def _hit_str(v: float) -> str:
    return _fmt(v, pct=True)


def _edge_str(v: float) -> str:
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return "n/a"
    sign = "+" if v >= 0 else ""
    return f"{sign}{v:.1f}pp"


# ---------------------------------------------------------------------------
# Section builders
# ---------------------------------------------------------------------------

def _section_test1(t1: dict, phase3: dict) -> str:
    lines = [
        "## Test 1: Placebo / Shuffle Test",
        "",
        "**What it tests:** The target vector Y (USDCAD returns) is randomly shuffled "
        "while X is kept intact. The full pipeline -- filter, selection, sign determination, "
        "CV, hold-out -- runs end-to-end on the shuffled data. Under a correctly specified "
        "pipeline with no data leakage, shuffled Y should produce no edge: hit rates ~50%, "
        "DSR near zero, extreme edges near zero.",
        "",
        "**Expected:** All horizons return null results across all seeds.",
        "",
        "**Failure condition:** Any horizon showing holdout hit rate > 55% or extreme "
        "edge > +5pp on shuffled Y indicates a methodological source of spurious signal "
        "that survives even when the X-Y relationship is destroyed.",
        "",
    ]

    if not t1:
        lines.append("*Test 1 was not run.*\n")
        return "\n".join(lines)

    for horizon in ["weekly", "monthly", "quarterly"]:
        r = t1.get(horizon)
        if not r:
            continue

        lines.append(f"### {horizon.capitalize()}")
        lines.append("")
        lines.append(f"Real Phase 3 numbers: holdout hit={_hit_str(r.real_holdout_hit_rate)}, "
                     f"extreme edge={_edge_str(r.real_extreme_edge_pp)}, DSR={_fmt(r.real_dsr)}")
        lines.append("")
        lines.append(f"Shuffled Y results ({len(r.seeds_tested)} seeds: {r.seeds_tested}):")
        lines.append("")
        lines.append("| Seed | CV hit | HO hit | Extreme edge | DSR |")
        lines.append("|------|--------|--------|--------------|-----|")
        for i, seed in enumerate(r.seeds_tested):
            if i < len(r.seed_results):
                res = r.seed_results[i]
                lines.append(
                    f"| {seed} | {_hit_str(res['cv_hit_rate'])} | "
                    f"{_hit_str(res['holdout_hit_rate'])} | "
                    f"{_edge_str(res['holdout_extreme_edge_pp'])} | "
                    f"{_fmt(res['cv_dsr'])} |"
                )
        lines.append("")
        lines.append(f"Null distribution summary: "
                     f"max holdout hit={_hit_str(r.max_null_holdout_hit)}, "
                     f"max extreme edge={_edge_str(r.max_null_extreme_edge_pp)}")
        lines.append("")
        lines.append(f"**Verdict:** {r.verdict}")
        lines.append("")

    return "\n".join(lines)


def _section_test2(t2: dict, phase3: dict) -> str:
    lines = [
        "## Test 2: Synthetic Null X Matrix",
        "",
        "**What it tests:** X is replaced by a covariance-preserving simulation "
        "(Cholesky draw matching the empirical mean and covariance of the real X). "
        "The simulated X has the same statistical signature as the real X but no "
        "actual relationship to USDCAD returns. The real Y is kept intact. "
        "The full pipeline runs end-to-end.",
        "",
        "**Expected:** No edge. If edge appears, the pipeline has a structural bias "
        "that can manufacture signal from the cross-correlation structure of X alone, "
        "independent of any X-to-Y relationship.",
        "",
        "**Failure condition:** Holdout hit > 55% or extreme edge > +5pp on synthetic X.",
        "",
    ]

    if not t2:
        lines.append("*Test 2 was not run.*\n")
        return "\n".join(lines)

    for horizon in ["weekly", "monthly", "quarterly"]:
        r = t2.get(horizon)
        if not r:
            continue

        lines.append(f"### {horizon.capitalize()}")
        lines.append("")
        lines.append(f"Real Phase 3 numbers: holdout hit={_hit_str(r.real_holdout_hit_rate)}, "
                     f"extreme edge={_edge_str(r.real_extreme_edge_pp)}")
        lines.append("")
        lines.append(f"Synthetic null results ({r.n_sims} simulations):")
        lines.append("")
        lines.append("| Sim | CV hit | HO hit | Extreme edge |")
        lines.append("|-----|--------|--------|--------------|")
        for i, res in enumerate(r.sim_results):
            lines.append(
                f"| {i} | {_hit_str(res['cv_hit_rate'])} | "
                f"{_hit_str(res['holdout_hit_rate'])} | "
                f"{_edge_str(res['holdout_extreme_edge_pp'])} |"
            )
        lines.append("")
        lines.append(f"**Verdict:** {r.verdict}")
        lines.append("")

    return "\n".join(lines)


def _section_test3(t3: dict) -> str:
    lines = [
        "## Test 3: Bootstrap Null Distribution and P-values",
        "",
        "**What it tests:** For each horizon's headline extreme-reading hit rate, "
        "build the empirical null distribution under H0 (fair coin flip: Binomial(n, 0.5)) "
        "using 10,000 bootstrap samples. Report the one-sided p-value for the observed "
        "hit rate. Apply Bonferroni (x3 for three horizons) and Holm corrections.",
        "",
        "**Expected:** At least one horizon's extreme hit rate is statistically "
        "distinguishable from H0 after multiple-testing correction. If none survive "
        "correction, the headline numbers are not defensible as statistical claims.",
        "",
        "**Note on sample size:** The n (~221-223) is the count of extreme hold-out "
        "observations (top/bottom 10% of score readings). These are daily observations "
        "but the test statistic is directional accuracy, which is closer to independent "
        "than the raw return series. Block bootstrap (Test 6) provides the autocorrelation-"
        "robust version of this inference.",
        "",
    ]

    if not t3:
        lines.append("*Test 3 was not run.*\n")
        return "\n".join(lines)

    lines.append("| Horizon | Observed | n extreme | Raw p | Bonferroni p | Holm p | 95% null CI |")
    lines.append("|---------|----------|-----------|-------|--------------|--------|-------------|")

    for horizon in ["weekly", "monthly", "quarterly"]:
        r = t3.get(horizon)
        if not r:
            continue
        ci_str = (f"[{_hit_str(r.ci_95_lower)}, {_hit_str(r.ci_95_upper)}]"
                  if not math.isnan(r.ci_95_lower) else "n/a")
        lines.append(
            f"| {horizon.capitalize()} | {_hit_str(r.observed_value)} | {r.n_extreme_obs} | "
            f"{_fmt(r.raw_pvalue, dp=4)} | {_fmt(r.bonferroni_pvalue, dp=4)} | "
            f"{_fmt(r.holm_pvalue, dp=4)} | {ci_str} |"
        )

    lines.append("")

    for horizon in ["weekly", "monthly", "quarterly"]:
        r = t3.get(horizon)
        if r and r.verdict:
            lines.append(f"**{horizon.capitalize()} verdict:** {r.verdict}")
            lines.append("")

    return "\n".join(lines)


def _section_test4(t4: dict, phase3: dict) -> str:
    lines = [
        "## Test 4: Alternative Hold-out Windows",
        "",
        "**What it tests:** The Phase 3 hold-out is a single macro regime "
        "(2022-2026: BoC tightening cycle + tariff shock). Three alternative hold-out "
        "windows test whether the edge generalizes across different regimes:",
        "",
        "- 2008-2012: Global financial crisis and early recovery",
        "- 2014-2018: Oil price collapse, CAD-oil regime, US tightening cycle",
        "- 2018-2022: Pre-COVID, COVID dislocation, post-COVID normalization",
        "",
        "**Expected:** If the edge is real and general, it should appear in at "
        "least 2 of the 3 alternative windows (with variance). If it only appears "
        "in 2022-2026, the result is regime-specific.",
        "",
        "**Failure condition:** Edge appears in fewer than 2 of the 3 alternative "
        "windows for any horizon that Phase 3 claimed signal.",
        "",
    ]

    if not t4:
        lines.append("*Test 4 was not run.*\n")
        return "\n".join(lines)

    for horizon in ["weekly", "monthly", "quarterly"]:
        window_results = t4.get(horizon, [])
        if not window_results:
            continue

        hr = phase3.get(horizon)
        real_ho_hit = hr.validation.holdout_hit_rate if hr else float("nan")
        real_edge = (
            (hr.validation.holdout_hit_rate_extreme - hr.validation.holdout_hit_rate_middle) * 100
            if hr else float("nan")
        )

        lines.append(f"### {horizon.capitalize()}")
        lines.append("")
        lines.append(
            f"Phase 3 baseline (2022-2026): holdout hit={_hit_str(real_ho_hit)}, "
            f"extreme edge={_edge_str(real_edge)}"
        )
        lines.append("")
        lines.append("| Window | HO hit | Extreme edge | Extreme n | CV hit | DSR | Verdict |")
        lines.append("|--------|--------|--------------|-----------|--------|-----|---------|")
        for r in window_results:
            lines.append(
                f"| {r.window_name} | {_hit_str(r.holdout_hit_rate)} | "
                f"{_edge_str(r.holdout_extreme_edge_pp)} | {r.holdout_n_extreme} | "
                f"{_hit_str(r.cv_hit_rate)} | {_fmt(r.cv_dsr)} | {r.verdict[:60]}... |"
                if len(r.verdict) > 60 else
                f"| {r.window_name} | {_hit_str(r.holdout_hit_rate)} | "
                f"{_edge_str(r.holdout_extreme_edge_pp)} | {r.holdout_n_extreme} | "
                f"{_hit_str(r.cv_hit_rate)} | {_fmt(r.cv_dsr)} | {r.verdict} |"
            )
        lines.append("")

        # Count how many windows showed edge
        edge_count = sum(
            1 for r in window_results
            if (not math.isnan(r.holdout_hit_rate) and
                (r.holdout_hit_rate >= 0.53 or r.holdout_extreme_edge_pp >= 5.0))
        )
        total = len([r for r in window_results if not math.isnan(r.holdout_hit_rate)])

        if total == 0:
            summary_verdict = "All windows errored or insufficient data."
        elif edge_count >= 2:
            summary_verdict = (
                f"ROBUST across regimes: {edge_count}/{total} alternative windows show edge. "
                "The claim is not regime-specific."
            )
        elif edge_count == 1:
            summary_verdict = (
                f"PARTIALLY ROBUST: {edge_count}/{total} alternative windows show edge. "
                "The Phase 3 2022-2026 result may have regime-specific amplification."
            )
        else:
            summary_verdict = (
                f"NOT ROBUST: {edge_count}/{total} alternative windows show edge. "
                "The Phase 3 result appears to be specific to the 2022-2026 regime."
            )

        lines.append(f"**{horizon.capitalize()} summary:** {summary_verdict}")
        lines.append("")

    return "\n".join(lines)


def _section_test5(t5: dict) -> str:
    lines = [
        "## Test 5: Variable Importance Robustness",
        "",
        "**What it tests:** The top-3 features by MDA importance are removed from X "
        "entirely. The full pipeline re-runs on the reduced feature set. If the model "
        "still finds edge without its most important variables, the signal is broad-based. "
        "If edge disappears, the claim rests on 1-3 specific variables which may "
        "themselves be spurious.",
        "",
        "**Expected:** At least some reduction in edge (removing the most predictive "
        "variables must hurt), but not complete collapse. An edge that requires exactly "
        "its top 3 variables to survive is fragile.",
        "",
    ]

    if not t5:
        lines.append("*Test 5 was not run.*\n")
        return "\n".join(lines)

    for horizon in ["weekly", "monthly", "quarterly"]:
        r = t5.get(horizon)
        if not r:
            continue

        lines.append(f"### {horizon.capitalize()}")
        lines.append("")
        lines.append(f"Top-3 features dropped: {r.top3_features}")
        lines.append("")
        lines.append("| Configuration | HO hit | Extreme edge |")
        lines.append("|---------------|--------|--------------|")
        lines.append(
            f"| With top-3 (Phase 3) | {_hit_str(r.with_top3_holdout_hit)} | "
            f"{_edge_str(r.with_top3_extreme_edge_pp)} |"
        )
        lines.append(
            f"| Without top-3 | {_hit_str(r.without_top3_holdout_hit)} | "
            f"{_edge_str(r.without_top3_extreme_edge_pp)} |"
        )
        lines.append("")
        lines.append(
            f"Change: hit rate {_edge_str(r.hit_delta_pp)}, "
            f"extreme edge {_edge_str(r.edge_delta_pp)}"
        )
        lines.append("")
        lines.append(f"**Verdict:** {r.verdict}")
        lines.append("")

    return "\n".join(lines)


def _section_test6(t6: dict) -> str:
    lines = [
        "## Test 6: Time-Series Block Bootstrap Confidence Intervals",
        "",
        "**What it tests:** Standard bootstrap assumes independence between observations. "
        "FX returns are autocorrelated, especially at daily frequency with overlapping "
        "return windows. The Politis-Romano stationary block bootstrap preserves local "
        "autocorrelation structure when resampling. Block sizes are set to 2x the "
        "forecast horizon (weekly: 10, monthly: 42, quarterly: 126).",
        "",
        "**Expected:** 95% CIs whose lower bound is above 50% for horizons where "
        "Phase 3 claims signal. If the CI lower bound falls below 50%, the headline "
        "number is not statistically distinguishable from a coin flip under "
        "autocorrelation-robust inference.",
        "",
    ]

    if not t6:
        lines.append("*Test 6 was not run.*\n")
        return "\n".join(lines)

    lines.append("| Horizon | Observed hit | n extreme | Block size | 95% CI lower | 95% CI upper | CI above 50%? |")
    lines.append("|---------|--------------|-----------|------------|--------------|--------------|---------------|")

    for horizon in ["weekly", "monthly", "quarterly"]:
        r = t6.get(horizon)
        if not r:
            continue
        ci_lower_str = _hit_str(r.ci_95_lower) if not math.isnan(r.ci_95_lower) else "n/a"
        ci_upper_str = _hit_str(r.ci_95_upper) if not math.isnan(r.ci_95_upper) else "n/a"
        above = "YES" if r.ci_lower_above_50pct else "NO"
        lines.append(
            f"| {horizon.capitalize()} | {_hit_str(r.observed_extreme_hit_rate)} | "
            f"{r.n_extreme_obs} | {r.block_size} | {ci_lower_str} | {ci_upper_str} | {above} |"
        )

    lines.append("")

    for horizon in ["weekly", "monthly", "quarterly"]:
        r = t6.get(horizon)
        if r and r.verdict:
            lines.append(f"**{horizon.capitalize()} verdict:** {r.verdict}")
            lines.append("")

    return "\n".join(lines)


def _section_overall_verdict(
    all_results: dict,
    phase3: dict,
) -> str:
    """Synthesize all test results into a per-horizon ship/hold verdict."""

    # Pull all test results
    t1 = all_results.get("test1", {})
    t2 = all_results.get("test2", {})
    t3 = all_results.get("test3", {})
    t4 = all_results.get("test4", {})
    t5 = all_results.get("test5", {})
    t6 = all_results.get("test6", {})

    lines = [
        "## Overall Verdict by Horizon",
        "",
        "Each test is scored: PASS / FAIL / INCONCLUSIVE / NOT RUN.",
        "Ship calls follow the most conservative outcome.",
        "",
    ]

    for horizon in ["weekly", "monthly", "quarterly"]:
        lines.append(f"### {horizon.capitalize()}")
        lines.append("")

        hr = phase3.get(horizon)
        if hr:
            v = hr.validation
            lines.append(
                f"Phase 3 headline: CV hit={_hit_str(v.cv_hit_rate)}, "
                f"HO hit={_hit_str(v.holdout_hit_rate)}, "
                f"extreme edge={_edge_str((v.holdout_hit_rate_extreme - v.holdout_hit_rate_middle)*100)}, "
                f"DSR={_fmt(v.dsr)}"
            )
            lines.append("")

        # Score each test
        test_scores: list[tuple[str, str, str]] = []  # (test_name, score, note)

        # Test 1
        r1 = t1.get(horizon)
        if r1:
            score = "FAIL" if r1.any_seed_shows_edge else "PASS"
            note = (f"Max null HO hit={_hit_str(r1.max_null_holdout_hit)}, "
                    f"max extreme edge={_edge_str(r1.max_null_extreme_edge_pp)}")
            test_scores.append(("T1 Placebo", score, note))

        # Test 2
        r2 = t2.get(horizon)
        if r2:
            any_synth_edge = (
                max(r2.null_holdout_hit_rates, default=0.5) > 0.55
                or max(r2.null_extreme_edges_pp, default=0.0) > 5.0
            )
            score = "FAIL" if any_synth_edge else "PASS"
            note = (f"Max null HO hit={_hit_str(max(r2.null_holdout_hit_rates, default=0.5))}, "
                    f"max extreme edge={_edge_str(max(r2.null_extreme_edges_pp, default=0.0))}")
            test_scores.append(("T2 Synthetic null", score, note))

        # Test 3
        r3 = t3.get(horizon)
        if r3:
            import math as _math
            if _math.isnan(r3.holm_pvalue):
                score = "INCONCLUSIVE"
                note = "Insufficient extreme observations"
            elif r3.holm_pvalue < 0.05:
                score = "PASS"
                note = f"Holm p={_fmt(r3.holm_pvalue, dp=4)}"
            elif r3.bonferroni_pvalue < 0.05:
                score = "BORDERLINE"
                note = f"Bonferroni p={_fmt(r3.bonferroni_pvalue, dp=4)}, Holm p={_fmt(r3.holm_pvalue, dp=4)}"
            elif r3.raw_pvalue < 0.05:
                score = "MARGINAL"
                note = f"Raw p={_fmt(r3.raw_pvalue, dp=4)}, does not survive correction"
            else:
                score = "FAIL"
                note = f"Raw p={_fmt(r3.raw_pvalue, dp=4)}, not significant"
            test_scores.append(("T3 Bootstrap p-val", score, note))

        # Test 4
        window_results = t4.get(horizon, [])
        if window_results:
            import math as _math
            valid = [r for r in window_results if not _math.isnan(r.holdout_hit_rate)]
            edge_count = sum(
                1 for r in valid
                if r.holdout_hit_rate >= 0.53 or r.holdout_extreme_edge_pp >= 5.0
            )
            if len(valid) == 0:
                score = "INCONCLUSIVE"
                note = "All windows errored"
            elif edge_count >= 2:
                score = "PASS"
                note = f"{edge_count}/{len(valid)} alternative windows show edge"
            elif edge_count == 1:
                score = "BORDERLINE"
                note = f"{edge_count}/{len(valid)} alternative windows show edge"
            else:
                score = "FAIL"
                note = f"{edge_count}/{len(valid)} alternative windows show edge -- regime-specific"
            test_scores.append(("T4 Alt holdouts", score, note))

        # Test 5
        r5 = t5.get(horizon)
        if r5:
            import math as _math
            if _math.isnan(r5.without_top3_holdout_hit):
                score = "INCONCLUSIVE"
                note = "Test failed to run"
            elif r5.without_top3_holdout_hit >= 0.53 or r5.without_top3_extreme_edge_pp >= 5.0:
                score = "PASS"
                note = (f"Edge survives: HO hit={_hit_str(r5.without_top3_holdout_hit)}, "
                        f"edge={_edge_str(r5.without_top3_extreme_edge_pp)} without top-3")
            else:
                score = "FAIL"
                note = (f"Edge collapses: HO hit={_hit_str(r5.without_top3_holdout_hit)}, "
                        f"edge={_edge_str(r5.without_top3_extreme_edge_pp)} without top-3")
            test_scores.append(("T5 Drop top-3", score, note))

        # Test 6
        r6 = t6.get(horizon)
        if r6:
            import math as _math
            if _math.isnan(r6.ci_95_lower):
                score = "INCONCLUSIVE"
                note = "Insufficient extreme observations"
            elif r6.ci_lower_above_50pct:
                score = "PASS"
                note = f"95% CI [{_hit_str(r6.ci_95_lower)}, {_hit_str(r6.ci_95_upper)}] above 50%"
            else:
                score = "FAIL"
                note = f"95% CI [{_hit_str(r6.ci_95_lower)}, {_hit_str(r6.ci_95_upper)}] straddles 50%"
            test_scores.append(("T6 Block bootstrap", score, note))

        # Print scorecard
        lines.append("| Test | Result | Note |")
        lines.append("|------|--------|------|")
        for name, score, note in test_scores:
            lines.append(f"| {name} | **{score}** | {note} |")
        lines.append("")

        # Overall ship call
        fails = [s for _, s, _ in test_scores if s == "FAIL"]
        passes = [s for _, s, _ in test_scores if s == "PASS"]
        borderlines = [s for _, s, _ in test_scores if s in ("BORDERLINE", "MARGINAL")]
        run_count = len(test_scores)

        # Ship logic: T1 or T2 FAIL = do not ship regardless of anything else
        # (those tests detect remaining leakage)
        t1_fail = any(s == "FAIL" and n == "T1 Placebo" for n, s, _ in test_scores)
        t2_fail = any(s == "FAIL" and n == "T2 Synthetic null" for n, s, _ in test_scores)

        if t1_fail or t2_fail:
            ship_call = (
                "DO NOT SHIP AS PREDICTIVE PRODUCT: Test 1 (placebo) or Test 2 (synthetic null) "
                "indicates remaining methodological leakage. The claimed edge survives when the "
                "X-Y relationship is destroyed, which means it is a pipeline artifact, not signal. "
                "Fix the methodology before any public-facing product launch."
            )
        elif len(fails) >= 3:
            ship_call = (
                f"DO NOT SHIP: {len(fails)}/{run_count} tests failed. "
                "The claimed edge does not hold up under adversarial stress testing. "
                "Present as scorecard (data synthesis) only, with no predictive framing."
            )
        elif len(fails) >= 2:
            ship_call = (
                f"SCORECARD ONLY: {len(fails)}/{run_count} tests failed. "
                "The edge is not robust enough to justify predictive product framing. "
                "Ship as a data-synthesis scorecard. Do not cite hit rates to subscribers."
            )
        elif len(fails) == 1 and len(passes) >= 3:
            ship_call = (
                f"SHIP WITH CAVEATS: {len(passes)}/{run_count} tests pass, {len(fails)} fail. "
                "Moderate robustness. Ship with explicit disclosure of the failing test, "
                "the regime caveat (2022-2026 hold-out), and the n=~220 extreme-obs sample size. "
                "Frame as 'preliminary evidence of conditional signal' not 'validated predictor'."
            )
        elif len(fails) == 0 and len(passes) >= 4:
            ship_call = (
                f"SHIP WITH STANDARD CAVEATS: {len(passes)}/{run_count} tests pass. "
                "The edge survives adversarial stress testing. "
                "Standard caveats apply: n=~220 extreme obs, one macro regime (2022-2026), "
                "missing Bloomberg signals (CESI, risk reversals)."
            )
        else:
            n_inconclusive = sum(1 for _, s, _ in test_scores if s == "INCONCLUSIVE")
            ship_call = (
                f"INCONCLUSIVE: {len(passes)} pass, {len(fails)} fail, "
                f"{n_inconclusive} inconclusive of {run_count} tests run. "
                "Insufficient evidence to make a ship/hold call. "
                "Address inconclusives before launch decision."
            )

        lines.append(f"**Ship call: {ship_call}**")
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Report builder
# ---------------------------------------------------------------------------

def build_report(
    all_results: dict,
    phase3_results: dict,
    fast_mode: bool = False,
) -> str:
    """Assemble the full adversarial validation report."""

    t1 = all_results.get("test1", {})
    t2 = all_results.get("test2", {})
    t3 = all_results.get("test3", {})
    t4 = all_results.get("test4", {})
    t5 = all_results.get("test5", {})
    t6 = all_results.get("test6", {})

    header_lines = [
        "# USDCAD Phase 3 -- Adversarial Validation Report",
        "",
        "**Produced:** 2026-05-26",
        "**Status:** Internal analytical work product. Not for distribution.",
        "",
    ]

    if fast_mode:
        header_lines += [
            "> **FAST MODE:** This report used a reduced computational budget "
            "(fewer seeds/sims/bootstrap iterations). Results are indicative, not final. "
            "Re-run without --fast for the full report before any launch decision.",
            "",
        ]

    header_lines += [
        "## Context",
        "",
        "Phase 2 had a sign-assignment look-ahead bias (65.7% weekly hit rate was a pipeline "
        "artifact). Phase 3 fixed this and added a true 20% chronological hold-out. "
        "The Phase 3 headline numbers are: weekly extreme 64.6%, monthly extreme 70.4-73.1%, "
        "quarterly extreme 70.1% (all from n=~221-223 hold-out extreme observations).",
        "",
        "This suite adversarially stress-tests those findings. Six tests, each designed to "
        "detect a different class of methodological artifact. An honest report: failures are "
        "reported as failures. This document determines whether the Phase 3 findings justify "
        "a predictive product or scorecard-only framing.",
        "",
        "---",
        "",
    ]

    sections = [
        "\n".join(header_lines),
        _section_test1(t1, phase3_results),
        "---\n",
        _section_test2(t2, phase3_results),
        "---\n",
        _section_test3(t3),
        "---\n",
        _section_test4(t4, phase3_results),
        "---\n",
        _section_test5(t5),
        "---\n",
        _section_test6(t6),
        "---\n",
        _section_overall_verdict(all_results, phase3_results),
        "",
        "---",
        "",
        "*Report generated by `pipeline/usdcad/validation/run.py`.*",
        "*Phase 3 results loaded from `data/processed/usdcad_model_results.pkl`.*",
        "",
    ]

    return "\n".join(sections)
