"""Auto-blurb pipeline package (Phase 1).

Orchestrates the multi-agent flow per editorial/auto_blurb_process.md
Sections 1-3 and 9.

Public surface (Phase 1):
    - release_cycle.ReleaseCycle, SurfaceSlot, SurfaceState
    - artifact.CycleArtifact, read_artifact, write_artifact, transition_state
    - registry.RELEASE_KEYS
    - validators.validate_surface_body
    - factcheck.extract_numeric_tokens, verify_token (Mode B helpers)
    - verify_claims.verify_claim_file (Mode A dispatch hook)
    - email.send_release_cycle_review_email
    - run.main  (CLI entry point)
"""

from __future__ import annotations

__all__ = [
    "release_cycle",
    "artifact",
    "registry",
    "validators",
    "factcheck",
    "verify_claims",
    "email",
    "run",
    "approve_cycle",
    "diff_brief",
]
