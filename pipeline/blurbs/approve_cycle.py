"""Bulk-approve a release-cycle's surfaces.

Usage:
    python -m pipeline.blurbs.approve_cycle --release-id <id> --all

Flips every surface's `last_state` from `ready_for_user` to `approved`
on the wrapper, and rewrites every per-surface artifact's status field +
state_history accordingly. Stamps `approved_by_at` per Section 5 of the
EDR doc.

Non-bulk approval (per-surface) is also supported via repeated invocation
with --surface <id> or by manual edit in VS Code.
"""

from __future__ import annotations

import argparse
import logging
from datetime import datetime, timezone
from pathlib import Path

from pipeline.blurbs.artifact import read_artifact, write_artifact
from pipeline.blurbs.release_cycle import (
    StateEvent,
    StateTransitionError,
    read_release_cycle,
    transition_surface_state,
    write_release_cycle,
)

logger = logging.getLogger("pipeline.blurbs.approve_cycle")

REPO_ROOT = Path(__file__).resolve().parents[2]


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def approve_cycle(
    repo_root: Path,
    release_id: str,
    all_surfaces: bool = False,
    surface_ids: list[str] | None = None,
) -> dict:
    rc = read_release_cycle(repo_root, release_id)
    targets: list[str]
    if all_surfaces:
        targets = [s.surface_id for s in rc.surfaces]
    elif surface_ids:
        targets = surface_ids
    else:
        raise ValueError("must pass --all or --surface <id>")

    approved: list[str] = []
    skipped: list[tuple[str, str]] = []
    stamp = _now()
    for sid in targets:
        slot = next((s for s in rc.surfaces if s.surface_id == sid), None)
        if slot is None:
            skipped.append((sid, "not in cycle"))
            continue
        if slot.last_state != "ready_for_user":
            skipped.append((sid, f"state={slot.last_state}"))
            continue
        try:
            transition_surface_state(
                rc, sid, "approved",
                actor="user",
                note=f"bulk-approve at {stamp}",
            )
        except StateTransitionError as exc:
            skipped.append((sid, str(exc)))
            continue
        # write through to the artifact file
        artifact_path = repo_root / slot.artifact_path
        if artifact_path.exists():
            artifact, body = read_artifact(artifact_path)
            artifact.last_state = "approved"
            artifact.status = "approved"
            artifact.approved_by_at = stamp
            artifact.state_history.append(StateEvent(
                state="approved",
                timestamp=stamp,
                actor="user",
                note="bulk-approve",
            ))
            write_artifact(artifact_path, artifact, body)
        approved.append(sid)
    write_release_cycle(repo_root, rc)
    return {
        "release_id": release_id,
        "approved": approved,
        "skipped": skipped,
        "stamp": stamp,
    }


def _parse_args(argv=None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="python -m pipeline.blurbs.approve_cycle",
        description="Bulk-approve a release-cycle's surfaces.",
    )
    p.add_argument("--release-id", required=True)
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--all", action="store_true", help="approve every surface")
    g.add_argument(
        "--surface", action="append", dest="surfaces",
        help="approve a specific surface (repeatable)",
    )
    return p.parse_args(argv)


def main(argv=None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    args = _parse_args(argv)
    result = approve_cycle(
        REPO_ROOT,
        release_id=args.release_id,
        all_surfaces=args.all,
        surface_ids=args.surfaces,
    )
    logger.info("approved: %s", result["approved"])
    if result["skipped"]:
        logger.info("skipped: %s", result["skipped"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
