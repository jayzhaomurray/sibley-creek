"""Smoke test for the diff-aware writer brief module.

Not a pytest case -- a runnable script. Constructs two synthetic
snapshots (prior + new) for an inflation release with intentional
prior-vs-new differences, runs compute_release_diff +
format_brief_for_writer, and asserts the output contains the expected
delta / significance cues. Mirrors the test_cli_subprocess.py convention
already used in this package.

Run:
    python -m pipeline.blurbs.test_diff_brief

Exit codes:
    0 -- all assertions passed
    1 -- one or more assertions failed
"""

from __future__ import annotations

import sys
import traceback

from pipeline.blurbs.diff_brief import (
    compute_release_diff,
    format_brief_for_writer,
)


def _prior_snapshot() -> dict:
    """A prior vintage of the `inflation` section.

    Two indicators:
      - cpi-yoy: prior value 1.8%, history kept inside the 1.5-2.5 band
        (so a 2.3 new print breaks the 24-period high).
      - core-trim-yoy: prior 2.3%, history hovers around 2.3-2.6.
    """
    return {
        "sections_file": {
            "sections": {
                "inflation": {
                    "slug": "inflation",
                    "chartSeriesKey": "cpi-yoy",
                    "prints": [
                        {
                            "key": "cpi-yoy",
                            "indicator": "Headline CPI Y/Y",
                            "value": "1.8%",
                            "valueRaw": 1.8,
                            "priorRaw": 1.9,
                            "asOfISO": "2026-03-01",
                            "spark": [
                                1.9, 2.0, 2.1, 2.0, 1.95, 1.85,
                                1.80, 1.75, 1.70, 1.85, 1.90, 1.95,
                                2.0, 2.05, 2.1, 2.0, 1.95, 1.9,
                                1.85, 1.80, 1.85, 1.90, 1.95, 1.80,
                            ],
                        },
                        {
                            "key": "core-trim-yoy",
                            "indicator": "Core-trim Y/Y",
                            "value": "2.3%",
                            "valueRaw": 2.3,
                            "priorRaw": 2.4,
                            "asOfISO": "2026-03-01",
                            "spark": [
                                # History deliberately spans 2.0-2.6 so a
                                # 2.2 new print is INSIDE the recent range
                                # (neither record-high nor record-low).
                                2.6, 2.55, 2.5, 2.45, 2.0, 2.05,
                                2.3, 2.35, 2.4, 2.45, 2.4, 2.35,
                                2.3, 2.35, 2.4, 2.4, 2.35, 2.3,
                                2.3, 2.35, 2.4, 2.35, 2.4, 2.3,
                            ],
                        },
                    ],
                }
            }
        }
    }


def _current_snapshot() -> dict:
    """The new April 2026 vintage.

    Differences vs prior:
      - cpi-yoy: 1.8% -> 2.3% (+0.5pp). This is the highest reading in
        the 24-period window, which should trigger the record-high cue.
      - core-trim-yoy: 2.3% -> 2.2% (-0.1pp). Small move, neither
        record-high nor record-low. The cue should land in the
        "small tick / effectively flat" framing.
    """
    return {
        "sections_file": {
            "sections": {
                "inflation": {
                    "slug": "inflation",
                    "chartSeriesKey": "cpi-yoy",
                    "prints": [
                        {
                            "key": "cpi-yoy",
                            "indicator": "Headline CPI Y/Y",
                            "value": "2.3%",
                            "valueRaw": 2.3,
                            "priorRaw": 1.8,
                            "asOfISO": "2026-04-01",
                            "spark": [
                                2.0, 2.1, 2.0, 1.95, 1.85,
                                1.80, 1.75, 1.70, 1.85, 1.90, 1.95,
                                2.0, 2.05, 2.1, 2.0, 1.95, 1.9,
                                1.85, 1.80, 1.85, 1.90, 1.95, 1.80, 2.3,
                            ],
                        },
                        {
                            "key": "core-trim-yoy",
                            "indicator": "Core-trim Y/Y",
                            "value": "2.2%",
                            "valueRaw": 2.2,
                            "priorRaw": 2.3,
                            "asOfISO": "2026-04-01",
                            "spark": [
                                2.55, 2.5, 2.45, 2.0, 2.05,
                                2.3, 2.35, 2.4, 2.45, 2.4, 2.35,
                                2.3, 2.35, 2.4, 2.4, 2.35, 2.3,
                                2.3, 2.35, 2.4, 2.35, 2.4, 2.3, 2.2,
                            ],
                        },
                    ],
                }
            }
        }
    }


def _assert(condition: bool, msg: str, failures: list[str]) -> None:
    if not condition:
        failures.append(msg)
        print(f"  FAIL: {msg}", flush=True)
    else:
        print(f"  pass: {msg}", flush=True)


def main() -> int:
    failures: list[str] = []
    print("Computing release diff (inflation, prior vs current)...", flush=True)

    prior = _prior_snapshot()
    current = _current_snapshot()

    diff = compute_release_diff("inflation", prior, current)

    # Structural asserts
    _assert(diff.section_slug == "inflation",
            f"section_slug == inflation (got {diff.section_slug!r})",
            failures)
    _assert(diff.headline_as_of == "2026-04-01",
            f"headline_as_of == 2026-04-01 (got {diff.headline_as_of!r})",
            failures)
    _assert(len(diff.indicators) == 2,
            f"two indicators in diff (got {len(diff.indicators)})",
            failures)

    by_key = {ind.key: ind for ind in diff.indicators}

    # Headline CPI: +0.5pp, record-high in window
    cpi = by_key.get("cpi-yoy")
    if cpi is None:
        failures.append("missing cpi-yoy indicator")
    else:
        _assert(cpi.prior_value == 1.8,
                f"cpi-yoy prior == 1.8 (got {cpi.prior_value!r})",
                failures)
        _assert(cpi.new_value == 2.3,
                f"cpi-yoy new == 2.3 (got {cpi.new_value!r})",
                failures)
        _assert(cpi.delta is not None and abs(cpi.delta - 0.5) < 1e-9,
                f"cpi-yoy delta == +0.5 (got {cpi.delta!r})",
                failures)
        _assert(cpi.direction == "up",
                f"cpi-yoy direction == up (got {cpi.direction!r})",
                failures)
        _assert(cpi.is_record_high_in_window,
                "cpi-yoy is_record_high_in_window == True",
                failures)
        _assert("Highest" in cpi.significance,
                f"cpi-yoy significance mentions 'Highest' "
                f"(got {cpi.significance!r})",
                failures)

    # Core-trim: -0.1pp, no record. Should NOT be record-high or record-low.
    trim = by_key.get("core-trim-yoy")
    if trim is None:
        failures.append("missing core-trim-yoy indicator")
    else:
        _assert(trim.prior_value == 2.3,
                f"core-trim prior == 2.3 (got {trim.prior_value!r})",
                failures)
        _assert(trim.new_value == 2.2,
                f"core-trim new == 2.2 (got {trim.new_value!r})",
                failures)
        _assert(trim.delta is not None and abs(trim.delta - (-0.1)) < 1e-9,
                f"core-trim delta == -0.1 (got {trim.delta!r})",
                failures)
        _assert(trim.direction == "down",
                f"core-trim direction == down (got {trim.direction!r})",
                failures)
        _assert(not trim.is_record_high_in_window,
                "core-trim is_record_high_in_window == False",
                failures)
        _assert(not trim.is_record_low_in_window,
                "core-trim is_record_low_in_window == False",
                failures)

    # Render the brief
    print("\nRendering writer-brief markdown...", flush=True)
    md = format_brief_for_writer(diff)

    _assert("Diff brief: Inflation" in md,
            "brief header includes 'Diff brief: Inflation'",
            failures)
    _assert("2026-04-01" in md,
            "brief includes headline release date 2026-04-01",
            failures)
    _assert("Headline CPI Y/Y" in md,
            "brief includes 'Headline CPI Y/Y' label",
            failures)
    _assert("was 1.8% -> now 2.3%" in md,
            "brief shows 'was 1.8% -> now 2.3%' for headline",
            failures)
    _assert("+0.5pp" in md,
            "brief shows '+0.5pp' delta for headline",
            failures)
    _assert("Highest reading" in md,
            "brief carries 'Highest reading' significance cue for headline",
            failures)
    _assert("HINTS" in md,
            "brief includes the 'HINTS not assertions' disclaimer",
            failures)

    print("\n--- rendered brief ---", flush=True)
    print(md, flush=True)
    print("--- end brief ---\n", flush=True)

    if failures:
        print(f"FAIL: {len(failures)} assertion(s) failed:", flush=True)
        for f in failures:
            print(f"  - {f}", flush=True)
        return 1
    print("PASS: all assertions held.", flush=True)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception:  # noqa: BLE001
        traceback.print_exc()
        raise SystemExit(2)
