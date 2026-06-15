"""Prophylactic gate: every data input the pipeline DECLARES must be git-tracked.

Why this exists
---------------
`data/raw/*` is gitignored (raw fetches are reproducible). The pipeline reads
CSVs from several paths, and a file that exists on a developer's disk but was
never force-added to git is INVISIBLE in a clean checkout (CI, a fresh
worktree). The build then silently degrades -- a dropped supporting print
re-renders as a canon "TK" and freezes the deploy at the leakage gate.

This exact class has bitten the project three times (2026-05-11 alt-chart
readCsv ENOENT; 2026-06-12 labour regional CSVs; 2026-06-15 current-account).
The first two were patched per-instance. This gate patches the CLASS for the
`build_site_data` read path: it enumerates the data inputs the pipeline
DECLARES -- every section's primary series (`SECTION_CONFIGS`) and every
supporting print (`SUPPORTING_PRINTS`) -- and asserts each one is git-tracked.

The check is on TRACKED-NESS, not on-disk existence. That is deliberate: it is
the CI-relevant question, and because `git ls-files` counts staged additions, a
developer who adds a new series locally trips this gate (the file is on disk but
untracked) and is told to `git add -f` BEFORE the bad state ever reaches a
commit or CI. The bug becomes catchable locally, before push, instead of
surfacing only in CI hours later as a frozen deploy.

Panel `source_files` reads are covered separately by
`scripts/check_raw_tracked.mjs`; direct Astro `readCsv()` reads fail loud
(ENOENT) at astro-build time. Together those three cover the read surface.

Run standalone:  python -m pipeline.io.input_tracking
Wired into:      pipeline.build_financial and pipeline.build (run before
                 build_site_data, so a bad input never produces a committed
                 sections.json).
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from pipeline.io.site_data import SECTION_CONFIGS, SUPPORTING_PRINTS


class UntrackedInputError(RuntimeError):
    """A declared pipeline input CSV is not git-tracked. See module docstring."""


def declared_print_inputs() -> list[tuple[str, str, str]]:
    """All data inputs the build_site_data print layer declares.

    Returns (series_name, preferred_dir, where) tuples. `where` is a
    human label for the failure message (e.g. "primary:trade",
    "supporting:trade/current-account").
    """
    inputs: list[tuple[str, str, str]] = []
    for cfg in SECTION_CONFIGS.values():
        inputs.append((cfg.primary_series, cfg.primary_dir, f"primary:{cfg.slug}"))
    for slug, specs in SUPPORTING_PRINTS.items():
        for spec in specs:
            inputs.append(
                (spec.primary_series, spec.primary_dir, f"supporting:{slug}/{spec.key}")
            )
            if spec.secondary_series is not None:
                inputs.append(
                    (
                        spec.secondary_series,
                        spec.secondary_dir or spec.primary_dir,
                        f"supporting-secondary:{slug}/{spec.key}",
                    )
                )
    return inputs


def _git_tracked_data_files() -> set[str]:
    """Set of git-tracked paths under data/ (forward-slash, repo-relative).

    Includes staged additions, so `git add -f`'d-but-uncommitted files count
    as tracked -- the fix takes effect immediately, no commit required.
    """
    out = subprocess.run(
        ["git", "ls-files", "data"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    return set(out.split())


def _candidate_paths(series: str, preferred_dir: str) -> list[str]:
    """Tiers _read_series searches, in order: preferred then the rest."""
    tiers = [preferred_dir] + [
        t for t in ("processed", "derived", "raw") if t != preferred_dir
    ]
    return [f"data/{t}/{series}.csv" for t in tiers]


def find_untracked_inputs() -> list[tuple[str, str, str]]:
    """Declared inputs whose CSV is tracked in NO tier. Each tuple is
    (series, where, suggested_force_add_path)."""
    tracked = _git_tracked_data_files()
    missing: list[tuple[str, str, str]] = []
    for series, preferred_dir, where in declared_print_inputs():
        candidates = _candidate_paths(series, preferred_dir)
        if not any(c in tracked for c in candidates):
            missing.append((series, where, candidates[0]))
    return missing


def verify_print_inputs_tracked() -> None:
    """Raise UntrackedInputError if any declared print input is untracked.

    Call before build_site_data in the pipeline entrypoints.
    """
    missing = find_untracked_inputs()
    if not missing:
        return
    lines = [
        "Declared pipeline input CSV(s) are NOT git-tracked. In a clean checkout "
        "(CI / fresh worktree) these are absent, so build_site_data silently drops "
        "the print, which re-renders as a canon 'TK' and freezes the deploy at the "
        "reader-copy leakage gate. Force-add each file (data/raw/* is gitignored):",
        "",
    ]
    for series, where, path in missing:
        meta = path.replace(".csv", ".meta.json")
        lines.append(f"  [{where}] {series}")
        lines.append(f"      git add -f {path} {meta}")
    lines.append("")
    lines.append(
        "If the series lives in processed/ or derived/ rather than raw/, adjust the "
        "path accordingly. Then re-run the pipeline so sections.json regenerates with "
        "the real value."
    )
    raise UntrackedInputError("\n".join(lines))


def main() -> int:
    try:
        verify_print_inputs_tracked()
    except UntrackedInputError as exc:
        print(f"[check_input_tracking] FAIL:\n{exc}")
        return 1
    count = len(declared_print_inputs())
    print(
        f"[check_input_tracking] OK: all {count} declared print input(s) are git-tracked."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
