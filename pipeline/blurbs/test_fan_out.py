"""Smoke test for the fan-out orchestrator.

Not a pytest case -- a runnable script. Constructs a synthetic "CPI
April 2026 released" event, mocks every call_claude dispatch, and
asserts:

  1. detect_affected_surfaces returns >= 8 surfaces for a CPI release
     (section blurb + 5 section-meta + 6 plates + fresh-tag + hero).
  2. Dispatch order respects tiers: tier-4 hero abstract is LAST.
  3. The staging directory is used and is populated before promote.
  4. The promote step succeeds atomically (returns True) and the
     `_fan_out_inbox.md` entry lands.
  5. Rollback path: when one surface raises in the writer mock, the
     staging directory is removed and result.rolled_back is True.

Mocks call_claude end-to-end -- DOES NOT fire a production release
cycle or touch the registry primaries.

Run:
    python -m pipeline.blurbs.test_fan_out

Exit codes:
    0 -- all assertions passed
    1 -- one or more assertions failed
"""

from __future__ import annotations

import shutil
import sys
import traceback
from pathlib import Path
from tempfile import mkdtemp

from pipeline.blurbs.fan_out import (
    ReleaseEvent,
    _staging_root,
    detect_affected_surfaces,
    fan_out_release,
)


SYNTH_PRIOR_BODY = (
    "Headline CPI ran 2.3% Y/Y in March, per Statistics Canada, a 0.5pp "
    "acceleration that pushes headline back above the Bank of Canada's "
    "2% target. Core-trim eased a tenth to 2.2% and core-median held at "
    "2.3%."
)
SYNTH_NEW_BLURB = (
    "Headline CPI eased to 2.1% Y/Y in April, per Statistics Canada, a "
    "0.2pp deceleration that returns headline closer to the 2% target. "
    "Core-trim held at 2.2% and core-median eased a tenth to 2.2%."
)


def _make_event() -> ReleaseEvent:
    return ReleaseEvent(
        release_id="cpi_monthly_2026-04",
        release_key="cpi_monthly",
        section="inflation",
        reference_period="2026-04",
        release_date="2026-05-14",
    )


def _writer_mock_factory(*, fail_surface: str | None = None):
    """Return a writer_dispatch mock that returns deterministic bodies.

    If `fail_surface` is set, raises a RuntimeError when the prompt
    mentions that surface_id (so we can exercise the rollback path).
    """
    call_log: list[str] = []

    def mock(prompt: str, model: str) -> str:
        call_log.append(prompt[:120])
        if fail_surface and fail_surface in prompt:
            raise RuntimeError(f"synthetic writer failure on {fail_surface}")
        # Decide the body based on prompt cues.
        if "blurb_body" in prompt or "inflation.blurb.body" in prompt:
            return SYNTH_NEW_BLURB
        if "tile_line" in prompt or "tileLine" in prompt:
            return "Headline CPI eased to 2.1% in April; core measures held near 2.2%."
        if "hero_kicker" in prompt or "heroKicker" in prompt:
            return "April CPI"
        if "blurb_date" in prompt or "blurb.date" in prompt:
            return "May 14, 2026"
        if "latest_release_label" in prompt or "latestReleaseLabel" in prompt:
            return "Latest: April CPI, May 14"
        if "updated_at" in prompt or "updatedAt" in prompt:
            return "1747200000000"
        if "hero_abstract" in prompt or "_global.hero_abstract" in prompt:
            return (
                "The Canadian cycle is steady. Headline CPI eased to 2.1% in "
                "April, the BoC continues to hold the overnight rate at "
                "2.25%, and unemployment remains at the upper end of the "
                "recent range at 6.9%."
            )
        if "fresh_tag_rotation" in prompt:
            return (
                "Rotation: inflation -> fresh; gdp, labour, housing, policy, "
                "markets, trade -> last."
            )
        # Default: a plate interpretation
        return (
            "Headline CPI eased to 2.1% Y/Y in April, a 0.2pp move that "
            "puts the print one tenth below the 2% target. Core measures "
            "held near 2.2%."
        )

    mock.call_log = call_log  # type: ignore[attr-defined]
    return mock


def _gate3_pass_mock(prompt: str, model: str) -> str:
    """Mock the editorial-director Gate 3 dispatch -- always PASS."""
    return "VERDICT: PASS"


def _assert(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)


def test_detect_affected_surfaces_cpi() -> None:
    event = _make_event()
    plan = detect_affected_surfaces(event)
    surface_ids = [s.surface_id for s in plan.surfaces]
    print(f"  detected {len(plan.surfaces)} surfaces")
    for s in plan.surfaces:
        print(f"    tier={s.tier} {s.surface_id}")
    _assert(
        len(plan.surfaces) >= 8,
        f"expected >= 8 surfaces for CPI release; got {len(plan.surfaces)}",
    )
    _assert(
        "inflation.blurb.body" in surface_ids,
        "section blurb body surface missing",
    )
    _assert(
        "inflation.tileLine" in surface_ids,
        "tileLine surface missing",
    )
    _assert(
        any("interpretation" in s for s in surface_ids),
        "no plate interpretation surfaces detected",
    )
    _assert(
        "_global.fresh_tag_rotation" in surface_ids,
        "fresh-tag rotation surface missing",
    )
    _assert(
        "_global.hero_abstract" in surface_ids,
        "hero abstract surface missing",
    )
    # hero-last: hero abstract is tier 4 and is the last surface in plan
    last_surface = plan.surfaces[-1]
    _assert(
        last_surface.surface_id == "_global.hero_abstract" or last_surface.tier == 4,
        f"hero abstract is not last in plan order; got {last_surface.surface_id}",
    )


def test_detect_affected_surfaces_rate_decision() -> None:
    """BoC rate decision should ripple to Markets' boc-fed-spread plate."""
    event = ReleaseEvent(
        release_id="boc_decision_2026-06-10",
        release_key="boc_decision",
        section="policy",
        reference_period="2026-06-10",
        release_date="2026-06-10",
    )
    plan = detect_affected_surfaces(event)
    surface_ids = [s.surface_id for s in plan.surfaces]
    print(f"  rate-decision plan: {len(plan.surfaces)} surfaces")
    ripple_present = any(
        "markets" in sid and "boc-fed-spread" in sid for sid in surface_ids
    )
    _assert(ripple_present, "cross-section ripple to markets.boc-fed-spread missing")


def test_fan_out_happy_path(tmp_root: Path) -> None:
    event = _make_event()
    writer_mock = _writer_mock_factory()
    result = fan_out_release(
        event,
        repo_root=tmp_root,
        writer_dispatch=writer_mock,
        surface_fit_dispatch=_gate3_pass_mock,
        diff_brief_md="## Diff brief\n_synthetic test_\n",
        prior_bodies={"inflation.blurb.body": SYNTH_PRIOR_BODY},
    )
    print(f"  surfaces_drafted={result.surfaces_drafted} "
          f"surfaces_failed={result.surfaces_failed} "
          f"promoted={result.promoted} rolled_back={result.rolled_back}")
    _assert(
        result.surfaces_drafted >= 8,
        f"expected >= 8 drafted surfaces; got {result.surfaces_drafted}",
    )
    _assert(result.surfaces_failed == 0, f"unexpected failures: {result.error}")
    _assert(result.promoted, f"promote failed: {result.error}")
    _assert(not result.rolled_back, "happy-path should not roll back")

    # hero-last in dispatch order
    hero_idx = result.dispatch_order.index("_global.hero_abstract")
    _assert(
        hero_idx == len(result.dispatch_order) - 1,
        f"hero abstract not last in dispatch_order; idx={hero_idx} "
        f"len={len(result.dispatch_order)}",
    )

    # staging files exist
    staging_dir = _staging_root(tmp_root, event.release_id)
    _assert(
        staging_dir.exists(),
        f"staging dir not created at {staging_dir}",
    )
    plan = detect_affected_surfaces(event)
    # at least one staged file per drafted surface
    staged_files = list(staging_dir.rglob("*"))
    staged_file_count = sum(1 for p in staged_files if p.is_file())
    _assert(
        staged_file_count >= len(plan.surfaces),
        f"expected >= {len(plan.surfaces)} staged files; got {staged_file_count}",
    )

    # inbox entry written
    inbox = tmp_root / "editorial" / "blurbs" / "_fan_out_inbox.md"
    _assert(inbox.exists(), "fan-out inbox file not written")
    inbox_text = inbox.read_text(encoding="utf-8")
    _assert(
        event.release_id in inbox_text,
        f"release_id {event.release_id} not in inbox",
    )


def test_fan_out_rollback_on_writer_failure(tmp_root: Path) -> None:
    event = ReleaseEvent(
        release_id="cpi_monthly_2026-05",
        release_key="cpi_monthly",
        section="inflation",
        reference_period="2026-05",
        release_date="2026-06-14",
    )
    # Force the hero abstract writer to fail (worst-case: very late tier)
    writer_mock = _writer_mock_factory(fail_surface="_global.hero_abstract")
    result = fan_out_release(
        event,
        repo_root=tmp_root,
        writer_dispatch=writer_mock,
        surface_fit_dispatch=_gate3_pass_mock,
        diff_brief_md="## Diff brief\n_synthetic test_\n",
    )
    print(f"  rollback path: rolled_back={result.rolled_back} "
          f"promoted={result.promoted} error={result.error}")
    _assert(
        result.rolled_back,
        "expected rolled_back=True after writer failure",
    )
    _assert(
        not result.promoted,
        "promoted should be False on rollback",
    )
    staging_dir = _staging_root(tmp_root, event.release_id)
    _assert(
        not staging_dir.exists(),
        f"staging dir should be removed on rollback; still at {staging_dir}",
    )


def main() -> int:
    tmp_root_str = mkdtemp(prefix="fan_out_test_")
    tmp_root = Path(tmp_root_str)
    try:
        print("test_detect_affected_surfaces_cpi:")
        test_detect_affected_surfaces_cpi()
        print("  PASS")
        print("test_detect_affected_surfaces_rate_decision:")
        test_detect_affected_surfaces_rate_decision()
        print("  PASS")
        print("test_fan_out_happy_path:")
        test_fan_out_happy_path(tmp_root)
        print("  PASS")
        print("test_fan_out_rollback_on_writer_failure:")
        test_fan_out_rollback_on_writer_failure(tmp_root)
        print("  PASS")
        print("ALL PASS")
        return 0
    except AssertionError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    except Exception:
        print("FAIL: unexpected exception", file=sys.stderr)
        traceback.print_exc()
        return 1
    finally:
        # Best-effort cleanup
        try:
            shutil.rmtree(tmp_root_str, ignore_errors=True)
        except Exception:
            pass


if __name__ == "__main__":
    raise SystemExit(main())
