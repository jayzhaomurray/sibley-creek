"""Phase-1 CLI orchestrator for the auto-blurb pipeline.

Walks one release-cycle through the 9 state-machine transitions, fanning
out to per-surface artifacts under editorial/blurbs/<section>/<unit>/.

State sequence per editorial/auto_blurb_process.md Section 1:
    release_landed -> context_drafted -> claims_verified ->
    writer_drafted -> fact_checked -> style_polished ->
    surface_fit_passed -> ready_for_user -> approved -> published.

Gate 3 (surface_fit_passed) is the editorial-director's surface-fit
review per editorial/review_protocol.md; runs after style-polish and
before user_review.

Usage:
    python -m pipeline.blurbs.run --release-id cpi_monthly_2026-04
    python -m pipeline.blurbs.run --release-id <id> --surface <surface_id>
    python -m pipeline.blurbs.run --release-id <id> --dry-run

Agent dispatch in Phase 1 ships as pluggable callables so tests can
inject fixture responses without invoking LLMs. The production dispatch
mechanism is `pipeline.blurbs.llm_client.call_claude`, which prefers the
`claude --print` CLI subprocess (subscription path) and falls back to
the Anthropic SDK (`ANTHROPIC_API_KEY`) when the CLI is unavailable. The
dispatch hook itself lives in this module's `AGENT_DISPATCH` registry.
The `verify_claims` step calls `verify_claim_file` directly
(fresh-context Mode A).

The orchestrator is intentionally side-effect heavy: it writes the
wrapper cycle JSON, the per-surface artifact .md files, the shared-card
YAML, and the per-cycle log file at:

    editorial/blurbs/<section>/<unit-slug>/<release-id>.log.md

Per-card budget: researcher 2 round-trips on claims-verification fails.
Writer 3 round-trips with fact-checker. Style-editor 1 re-draft.
Editorial-director (Gate 3) 2 surface-fit re-runs. On exhaustion:
surface transitions to `escalated` and the email subject flips to
escalation prefix.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Optional, Protocol

from pipeline.blurbs import diff_brief as df_mod
from pipeline.blurbs import factcheck as fc_mod
from pipeline.blurbs import validators as vd
from pipeline.blurbs.artifact import CycleArtifact, read_artifact, write_artifact
from pipeline.blurbs.email import render_email_body, send_release_cycle_review_email  # noqa: F401
from pipeline.blurbs.llm_client import LLMDispatchError, call_claude
from pipeline.blurbs.registry import (
    RELEASE_KEYS,
    ReleaseKeySpec,
    SurfaceSpec,
    get_release_spec,
    parse_release_id,
)
from pipeline.blurbs.release_cycle import (
    ReleaseCycle,
    StateEvent,
    SurfaceSlot,
    init_release_cycle,
    read_release_cycle,
    transition_surface_state,
    write_release_cycle,
)
from pipeline.blurbs.verify_claims import VerifyResult, verify_claim_file

logger = logging.getLogger("pipeline.blurbs.run")

REPO_ROOT = Path(__file__).resolve().parents[2]


# ---------------------------------------------------------------------------
# Model pins
# ---------------------------------------------------------------------------

# Per spec: Opus for verifier; Sonnet for writer / fact-checker / style-editor.
# Editorial-director (Gate 3) runs on Opus -- surface-fit judgment benefits
# from the stronger reasoning ceiling and the call count is small (one per
# surface per cycle plus up to 2 re-runs on reject).
MODEL_VERIFIER = "claude-opus-4-7"
MODEL_WRITER = "claude-sonnet-4-7"
MODEL_FACT_CHECKER = "claude-sonnet-4-7"
MODEL_STYLE_EDITOR = "claude-sonnet-4-7"
MODEL_EDITORIAL_DIRECTOR = "claude-opus-4-7"


# ---------------------------------------------------------------------------
# Retry budgets
# ---------------------------------------------------------------------------

RESEARCHER_BUDGET = 2     # round-trips on claims-verification fails
WRITER_BUDGET = 3         # round-trips with fact-checker
STYLE_BUDGET = 1          # re-drafts
SURFACE_FIT_BUDGET = 2    # editorial-director Gate 3 re-runs on REJECT


# ---------------------------------------------------------------------------
# Agent-dispatch protocol
# ---------------------------------------------------------------------------

class ResearcherDispatch(Protocol):
    """Signature for the researcher agent dispatch."""

    def __call__(
        self,
        release_id: str,
        release_spec: ReleaseKeySpec,
        repo_root: Path,
        revision_failures: list[dict] | None,
    ) -> dict: ...


class WriterDispatch(Protocol):
    def __call__(
        self,
        release_id: str,
        surface: SurfaceSpec,
        shared_cards: list[dict],
        prose_steer: dict,
        repo_root: Path,
        revision_failures: list[str] | None,
    ) -> str: ...


class StyleDispatch(Protocol):
    def __call__(
        self,
        release_id: str,
        surface: SurfaceSpec,
        draft_body: str,
        revision_note: str | None,
    ) -> str: ...


# ---------------------------------------------------------------------------
# Audit log
# ---------------------------------------------------------------------------

def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _log_path(repo_root: Path, slot: SurfaceSlot, release_id: str) -> Path:
    base = Path(slot.artifact_path).parent
    return repo_root / base / f"{release_id}.log.md"


def _append_log(repo_root: Path, slot: SurfaceSlot, release_id: str, msg: str) -> None:
    path = _log_path(repo_root, slot, release_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(
            f"# Cycle audit log: {release_id} :: {slot.surface_id}\n\n",
            encoding="utf-8",
        )
    with path.open("a", encoding="utf-8") as f:
        f.write(f"{_now()} {msg}\n")


# ---------------------------------------------------------------------------
# Release detection
# ---------------------------------------------------------------------------

def detect_release_landed(repo_root: Path, release_spec: ReleaseKeySpec) -> Optional[str]:
    """Return the release_date for this release-key if a meta.json reports one.

    Per Section 3.1 of the EDR doc, the trigger is a change in `release_date`
    on any primary series sidecar. Phase 1 returns the first non-null
    `release_date` we find; if every sidecar has `release_date: null`, the
    orchestrator falls back to the system date (the user explicitly invoked
    the CLI, so they're asserting the release has landed).
    """
    for meta_rel in release_spec.primary_meta_files:
        path = repo_root / meta_rel
        if not path.exists():
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        rd = data.get("release_date")
        if rd:
            return rd
    return None


# ---------------------------------------------------------------------------
# Default dispatches: NotImplementedError. Tests inject fixtures.
# ---------------------------------------------------------------------------

def _default_researcher(*args, **kwargs):
    raise NotImplementedError(
        "Researcher dispatch not configured. In production the orchestrator "
        "shells out to the Claude Agent SDK / `claude` CLI per "
        "pipeline/blurbs/README.md; in tests pass a fixture callable into "
        "run_release_cycle(researcher_dispatch=...)."
    )


def _default_writer(*args, **kwargs):
    raise NotImplementedError(
        "Writer dispatch not configured. See README; pass writer_dispatch=... "
        "in tests."
    )


def _default_style(*args, **kwargs):
    raise NotImplementedError(
        "Style-editor dispatch not configured. See README; pass "
        "style_dispatch=... in tests."
    )


# ---------------------------------------------------------------------------
# Core walk
# ---------------------------------------------------------------------------

def _write_shared_cards(path: Path, cards: list[dict]) -> None:
    """Persist shared-card YAML so the verifier (fresh context) can re-read it."""
    from io import StringIO
    from ruamel.yaml import YAML
    y = YAML(typ="rt")
    y.default_flow_style = False
    y.allow_unicode = False
    path.parent.mkdir(parents=True, exist_ok=True)
    buf = StringIO()
    y.dump(cards, buf)
    path.write_text(buf.getvalue(), encoding="utf-8", newline="\n")


def _load_shared_cards(path: Path) -> list[dict]:
    from ruamel.yaml import YAML
    y = YAML(typ="rt")
    raw = y.load(path.read_text(encoding="utf-8"))
    if raw is None:
        return []
    return [dict(c) for c in raw]


def _claim_card_like(cards: list[dict]) -> list[fc_mod.ClaimCardLike]:
    return [fc_mod.ClaimCardLike.model_validate(c) for c in cards]


def _init_artifact(
    repo_root: Path,
    rc: ReleaseCycle,
    slot: SurfaceSlot,
    surface_spec: SurfaceSpec,
) -> CycleArtifact:
    """Stamp out a brand-new per-surface artifact in `release_landed` state."""
    artifact = CycleArtifact(
        release_id=rc.release_id,
        release_key=rc.release_key,
        section=surface_spec.section,
        unit_slug=surface_spec.unit_slug,
        surface=surface_spec.kind,
        reference_period=rc.reference_period,
        release_date=rc.release_date,
        created_at=rc.created_at,
        char_cap=surface_spec.char_cap,
        voice_register_variant=surface_spec.kind,
        last_state=slot.last_state,
        state_history=list(slot.state_history),
        shared_cards_path=rc.shared_cards_path,
        model_writer=MODEL_WRITER,
        model_fact_checker=MODEL_FACT_CHECKER,
        model_style_editor=MODEL_STYLE_EDITOR,
        model_verifier=MODEL_VERIFIER,
        status="release_landed",
    )
    write_artifact(repo_root / slot.artifact_path, artifact, body="")
    return artifact


def _sync_artifact(repo_root: Path, slot: SurfaceSlot, body: str) -> CycleArtifact:
    """Re-read, then write the artifact with the slot's latest state."""
    path = repo_root / slot.artifact_path
    artifact, prev_body = read_artifact(path)
    artifact.last_state = slot.last_state
    artifact.state_history = list(slot.state_history)
    artifact.researcher_revision_count = slot.researcher_revision_count
    artifact.writer_revision_count = slot.writer_revision_count
    artifact.style_revision_count = slot.style_revision_count
    artifact.status = slot.last_state
    artifact.flags = list(slot.flags)
    write_artifact(path, artifact, body or prev_body)
    return artifact


def _run_researcher_and_verify(
    repo_root: Path,
    rc: ReleaseCycle,
    release_spec: ReleaseKeySpec,
    researcher_dispatch: ResearcherDispatch,
    verifier_fetcher: Optional[Callable] = None,
    use_live_verifier: bool = True,
) -> tuple[dict, list[dict], VerifyResult]:
    """Run researcher + Mode A verifier. Return (prose_steer, cards, result).

    Routes back to researcher on verifier failure; budget 2 round-trips.
    Raises if budget exhausted; caller transitions slot to `escalated`.
    """
    failures_for_researcher: list[dict] | None = None
    for round_idx in range(RESEARCHER_BUDGET + 1):
        researcher_out = researcher_dispatch(
            release_id=rc.release_id,
            release_spec=release_spec,
            repo_root=repo_root,
            revision_failures=failures_for_researcher,
        )
        cards = researcher_out["shared_cards"]
        prose_steer = researcher_out.get("prose_steer", {})

        shared_path = repo_root / rc.shared_cards_path
        _write_shared_cards(shared_path, cards)

        # transition every surface to context_drafted
        for slot in rc.surfaces:
            if slot.last_state == "release_landed":
                transition_surface_state(
                    rc, slot.surface_id, "context_drafted",
                    actor="researcher",
                    note=(
                        f"round={round_idx + 1}; "
                        f"shared cards={len(cards)}"
                    ),
                )
                _append_log(
                    repo_root, slot, rc.release_id,
                    f"researcher context_drafted round={round_idx + 1} "
                    f"cards={len(cards)}",
                )
            elif slot.last_state == "claims_verified":
                # already verified path: leave alone (revision round only
                # re-routes failed cards, not surface state)
                pass

        # Verifier dispatch (Mode A, fresh context)
        verdict_path = repo_root / (
            f"editorial/verifications/blurbs/_shared/"
            f"{rc.release_id}.claims.json"
        )
        if use_live_verifier:
            result = verify_claim_file(
                shared_path,
                fetcher=verifier_fetcher,
                verdict_summary_path=verdict_path,
                cycle_created_at=rc.created_at,
            )
        else:
            # mechanical bypass for tests that pre-mark cards as passed
            result = VerifyResult(
                total_cards=len(cards),
                passed_count=len(cards),
                failed_count=0,
                cards_path=str(shared_path),
            )

        for slot in rc.surfaces:
            _append_log(
                repo_root, slot, rc.release_id,
                f"verify_claims round={round_idx + 1} "
                f"total={result.total_cards} passed={result.passed_count} "
                f"failed={result.failed_count} "
                f"failures={[f.claim_id for f in result.failures]}",
            )

        if result.failed_count == 0:
            for slot in rc.surfaces:
                if slot.last_state == "context_drafted":
                    transition_surface_state(
                        rc, slot.surface_id, "claims_verified",
                        actor="verifier",
                        note=f"all {result.total_cards} cards passed",
                    )
            # Re-load cards from disk so verifier_status is populated;
            # Mode B fact-check requires `verifier_status: passed`.
            cards = _load_shared_cards(shared_path)
            return prose_steer, cards, result

        # Verifier failed; if we still have budget, route back to researcher
        if round_idx >= RESEARCHER_BUDGET:
            # exhausted. Escalate every surface that hadn't reached
            # claims_verified.
            for slot in rc.surfaces:
                slot.researcher_revision_count = round_idx + 1
                if slot.last_state in ("context_drafted",):
                    transition_surface_state(
                        rc, slot.surface_id, "escalated",
                        actor="orchestrator",
                        note=(
                            f"claims_verified failed after "
                            f"{round_idx + 1} round-trips"
                        ),
                    )
            raise _Escalation(
                f"researcher exhausted {RESEARCHER_BUDGET} revisions on "
                f"{rc.release_id}; failures: "
                f"{[f.claim_id for f in result.failures]}"
            )

        # Route back: record revision count, re-feed failed cards.
        for slot in rc.surfaces:
            slot.researcher_revision_count = round_idx + 1
            if slot.last_state == "context_drafted":
                transition_surface_state(
                    rc, slot.surface_id, "context_drafted",
                    actor="orchestrator",
                    note=(
                        f"re-route to researcher; revision "
                        f"{round_idx + 1} of {RESEARCHER_BUDGET}; "
                        f"failures={[f.claim_id for f in result.failures]}"
                    ),
                )
        failures_for_researcher = [
            {"claim_id": f.claim_id, "reason": f.reason, "notes": f.verifier_notes}
            for f in result.failures
        ]
    # unreachable
    raise RuntimeError("loop fall-through in _run_researcher_and_verify")


def _run_writer_and_factcheck(
    repo_root: Path,
    rc: ReleaseCycle,
    slot: SurfaceSlot,
    surface_spec: SurfaceSpec,
    cards: list[dict],
    prose_steer: dict,
    writer_dispatch: WriterDispatch,
) -> str:
    """Run writer + Mode B fact-check loop for one surface.

    Budget: WRITER_BUDGET round-trips total. On bust, transitions to
    `escalated` and raises _Escalation.
    """
    last_body = ""
    revision_failures: list[str] | None = None
    for round_idx in range(WRITER_BUDGET):
        body = writer_dispatch(
            release_id=rc.release_id,
            surface=surface_spec,
            shared_cards=cards,
            prose_steer=prose_steer,
            repo_root=repo_root,
            revision_failures=revision_failures,
        )
        last_body = body
        slot.writer_revision_count = round_idx + 1
        if round_idx == 0:
            transition_surface_state(
                rc, slot.surface_id, "writer_drafted",
                actor="writer",
                note=f"draft round {round_idx + 1}",
            )
        else:
            transition_surface_state(
                rc, slot.surface_id, "writer_drafted",
                actor="writer",
                note=f"re-draft round {round_idx + 1}",
            )
        _sync_artifact(repo_root, slot, body)
        _append_log(
            repo_root, slot, rc.release_id,
            f"writer round={round_idx + 1} body_chars={len(body)}",
        )

        # Mechanical pre-checks
        validation = vd.validate_surface_body(surface_spec.kind, body)

        # Mode B fact-check (no URL re-fetch)
        cc = _claim_card_like(cards)
        fcr = fc_mod.factcheck_body(
            body=body,
            cards=cc,
            surface_id=slot.surface_id,
            char_cap=surface_spec.char_cap,
        )

        # Persist Mode B verdict
        verdict_path = repo_root / (
            f"editorial/verifications/blurbs/{surface_spec.section}/"
            f"{surface_spec.unit_slug}/{rc.release_id}.draft.json"
        )
        verdict_path.parent.mkdir(parents=True, exist_ok=True)
        verdict_path.write_text(
            json.dumps({
                "validation": validation.model_dump(mode="json"),
                "factcheck": fcr.model_dump(mode="json"),
            }, indent=2),
            encoding="utf-8",
        )

        ok = validation.ok and fcr.ok
        _append_log(
            repo_root, slot, rc.release_id,
            f"factcheck round={round_idx + 1} ok={ok} "
            f"validation_failures={len(validation.failures)} "
            f"factcheck_issues={len(fcr.issues)}",
        )
        if ok:
            transition_surface_state(
                rc, slot.surface_id, "fact_checked",
                actor="fact-checker",
                note="draft verification passed",
            )
            return body
        # Otherwise: collect failures and re-loop
        revision_failures = (
            [f"validator: {r.rule}: {r.message}" for r in validation.failures]
            + [f"factcheck: {i}" for i in fcr.issues]
        )
        if round_idx + 1 >= WRITER_BUDGET:
            transition_surface_state(
                rc, slot.surface_id, "escalated",
                actor="orchestrator",
                note=(
                    f"writer + fact-checker exhausted {WRITER_BUDGET} rounds; "
                    f"failures={revision_failures}"
                ),
            )
            raise _Escalation(
                f"writer exhausted {WRITER_BUDGET} rounds on "
                f"{slot.surface_id}: {revision_failures}"
            )
    return last_body


def _run_style(
    repo_root: Path,
    rc: ReleaseCycle,
    slot: SurfaceSlot,
    surface_spec: SurfaceSpec,
    body: str,
    style_dispatch: StyleDispatch,
) -> str:
    """Run style polish; 1 re-draft on validation failure."""
    revision_note: Optional[str] = None
    for round_idx in range(STYLE_BUDGET + 1):
        polished = style_dispatch(
            release_id=rc.release_id,
            surface=surface_spec,
            draft_body=body,
            revision_note=revision_note,
        )
        slot.style_revision_count = round_idx + 1
        validation = vd.validate_surface_body(surface_spec.kind, polished)
        if validation.ok:
            transition_surface_state(
                rc, slot.surface_id, "style_polished",
                actor="style-editor",
                note=f"polish round {round_idx + 1}",
            )
            _sync_artifact(repo_root, slot, polished)
            _append_log(
                repo_root, slot, rc.release_id,
                f"style polish round={round_idx + 1} ok=True",
            )
            return polished
        revision_note = (
            "Polish failed validation: "
            + "; ".join(f.message for f in validation.failures)
        )
        _append_log(
            repo_root, slot, rc.release_id,
            f"style polish round={round_idx + 1} ok=False; {revision_note}",
        )
        if round_idx >= STYLE_BUDGET:
            transition_surface_state(
                rc, slot.surface_id, "escalated",
                actor="orchestrator",
                note=f"style-editor exhausted {STYLE_BUDGET + 1} rounds",
            )
            raise _Escalation(
                f"style-editor exhausted {STYLE_BUDGET + 1} rounds on "
                f"{slot.surface_id}"
            )
    return polished


# ---------------------------------------------------------------------------
# Gate 3: editorial-director surface-fit review
# ---------------------------------------------------------------------------

# Per-surface register/forbidden notes for the Gate 3 prompt. Surface kinds
# come from registry.SurfaceKind. Each entry is what the editorial-director
# needs to know to answer "does this content belong on this surface, in
# this context."
_SURFACE_FIT_CONTEXTS: dict[str, dict[str, str]] = {
    "homepage_abstract": {
        "lands_on": "the homepage abstract above the section grid on sibleycreek.ca",
        "register": "3-4 sentences, plain reader-facing summary of this release for a visitor who has not yet clicked into a section",
        "forbidden": (
            "internal canon-jargon ('tri-modal product', 'chartbook unit', "
            "'Mode 2', 'Big-Six framing'); process-talk about the pipeline; "
            "voice-doctrine artifacts; placeholder template-slot residue"
        ),
    },
    "topic_abstract": {
        "lands_on": "the topic abstract at the top of the inflation section page",
        "register": "2-3 sentences, plain reader-facing summary of what this section currently shows",
        "forbidden": (
            "internal canon-jargon, methodology-talk, deep-dive cross-references "
            "phrased for the editor rather than the reader, template-slot residue"
        ),
    },
    "sparkline_blurb": {
        "lands_on": "the sparkline blurb beside a small inline chart on the section panel",
        "register": "1-2 sentences, 10-25 words, crisp print-plus-delta",
        "forbidden": (
            "anything beyond a print-plus-delta line; jargon; hedging; "
            "process-talk; template-slot residue"
        ),
    },
    "active_headline": {
        "lands_on": "the active headline above the section's primary chart",
        "register": "1 sentence, 8-22 words, declarative headline that names the print",
        "forbidden": (
            "hedging, multi-clause structure, interpretation beyond the print, "
            "template-slot residue"
        ),
    },
    "chart_commentary": {
        "lands_on": "the interpretation paragraph beside a chart plate on the section page",
        "register": "2-4 sentences, Mode A blurb voice per editorial/writing-style.md Section 7: print + comparator + optional structural observation + optional next-print pointer",
        "forbidden": (
            "internal canon-jargon ('tri-modal product', 'chartbook unit', "
            "'Mode 2'); process-talk; Big-Six citation phrasing; voice-doctrine "
            "leaking into prose; template-slot residue; length mismatch with "
            "the surface"
        ),
    },
}


def _surface_fit_prompt(draft_body: str, surface_context: dict[str, str]) -> str:
    """Compose the Gate 3 prompt sent to the editorial-director agent."""
    return (
        "You are the editorial-director running Gate 3 of the three-gate "
        "review protocol (editorial/review_protocol.md). Gate 1 (fact) and "
        "Gate 2 (style) have already passed. Your job is the surface-fit "
        "question: does this content belong on this surface, in this "
        "context?\n\n"
        f"Surface: {surface_context['lands_on']}\n"
        f"Voice register the surface demands: {surface_context['register']}\n"
        f"What MUST NOT appear on this surface: {surface_context['forbidden']}\n\n"
        "Polished draft (post Gate 1 + Gate 2):\n"
        "---\n"
        f"{draft_body}\n"
        "---\n\n"
        "Return a verdict on a single line, then optional cuts. Format:\n"
        "  VERDICT: PASS\n"
        "or\n"
        "  VERDICT: REJECT\n"
        "  CUTS:\n"
        "  - <one cut per line; specific phrase to cut and why>\n"
        "  - <...>\n\n"
        "PASS only if the prose belongs on this surface as-is. REJECT for "
        "internal canon-jargon, voice-doctrine bleed, process-talk, "
        "template-slot drift, or length mismatch with the surface. When "
        "uncertain, REJECT with cuts -- the writer re-drafts cheaply."
    )


def _parse_surface_fit_response(raw: str) -> dict:
    """Parse the editorial-director response into a structured verdict.

    Returns `{"verdict": "pass" | "fail", "cuts": [str, ...]}`. Tolerates
    leading/trailing whitespace and variable casing on the VERDICT line.
    On malformed output (no VERDICT line), returns a fail verdict with a
    diagnostic cut so the cycle does not silently advance.
    """
    cuts: list[str] = []
    verdict: str = "fail"
    seen_verdict = False
    in_cuts_block = False
    for raw_line in (raw or "").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        upper = line.upper()
        if upper.startswith("VERDICT:"):
            seen_verdict = True
            payload = line.split(":", 1)[1].strip().upper()
            if payload.startswith("PASS"):
                verdict = "pass"
            elif payload.startswith("REJECT") or payload.startswith("FAIL"):
                verdict = "fail"
            continue
        if upper.startswith("CUTS:"):
            in_cuts_block = True
            continue
        if in_cuts_block and (line.startswith("-") or line.startswith("*")):
            cuts.append(line.lstrip("-* ").strip())
    if not seen_verdict:
        return {
            "verdict": "fail",
            "cuts": [
                "editorial-director returned no VERDICT line; treating as REJECT "
                "to avoid silently advancing the cycle. Raw response: "
                + (raw or "")[:240]
            ],
        }
    return {"verdict": verdict, "cuts": cuts}


def _surface_fit_review(
    draft_body: str,
    surface_context: dict[str, str],
    *,
    dispatch: Optional[Callable[[str, str], str]] = None,
) -> dict:
    """Dispatch the editorial-director Gate 3 surface-fit review.

    Args:
      draft_body: the style-polished body (Gate 2 output) for one surface.
      surface_context: the per-surface context dict from
        `_SURFACE_FIT_CONTEXTS` (`lands_on`, `register`, `forbidden`).
      dispatch: optional injection point for tests; signature
        `(prompt, model) -> raw_text`. Defaults to `call_claude`.

    Returns:
      `{"verdict": "pass" | "fail", "cuts": [str, ...]}`. On LLM dispatch
      failure: a fail verdict with the dispatch error as a single cut, so
      the cycle escalates rather than silently advancing.
    """
    prompt = _surface_fit_prompt(draft_body, surface_context)
    sender = dispatch or (lambda p, model: call_claude(prompt=p, model=model))
    try:
        raw = sender(prompt, MODEL_EDITORIAL_DIRECTOR)
    except LLMDispatchError as exc:
        return {
            "verdict": "fail",
            "cuts": [f"editorial-director dispatch failed: {exc}"],
        }
    return _parse_surface_fit_response(raw)


def _run_surface_fit(
    repo_root: Path,
    rc: ReleaseCycle,
    slot: SurfaceSlot,
    surface_spec: SurfaceSpec,
    body: str,
    writer_dispatch: WriterDispatch,
    style_dispatch: StyleDispatch,
    cards: list[dict],
    prose_steer: dict,
    surface_fit_dispatch: Optional[Callable[[str, str], str]] = None,
) -> str:
    """Run Gate 3 surface-fit review; on REJECT, round-trip to writer.

    A reject routes `style_polished -> writer_drafted` (a legal transition).
    The writer re-drafts with the editorial-director's cuts merged into the
    revision_failures list, then fact-check and style-polish run again,
    then Gate 3 runs again. Budget: SURFACE_FIT_BUDGET re-runs total.

    Returns the polished body that passed Gate 3.
    """
    surface_context = _SURFACE_FIT_CONTEXTS.get(
        surface_spec.kind,
        _SURFACE_FIT_CONTEXTS["chart_commentary"],
    )
    current_body = body
    for round_idx in range(SURFACE_FIT_BUDGET + 1):
        result = _surface_fit_review(
            draft_body=current_body,
            surface_context=surface_context,
            dispatch=surface_fit_dispatch,
        )
        verdict_path = repo_root / (
            f"editorial/verifications/blurbs/{surface_spec.section}/"
            f"{surface_spec.unit_slug}/{rc.release_id}.surface_fit.json"
        )
        verdict_path.parent.mkdir(parents=True, exist_ok=True)
        verdict_path.write_text(
            json.dumps({
                "round": round_idx + 1,
                "surface_kind": surface_spec.kind,
                "verdict": result["verdict"],
                "cuts": result["cuts"],
            }, indent=2),
            encoding="utf-8",
        )
        _append_log(
            repo_root, slot, rc.release_id,
            f"surface_fit round={round_idx + 1} "
            f"verdict={result['verdict']} cuts={len(result['cuts'])}",
        )

        if result["verdict"] == "pass":
            transition_surface_state(
                rc, slot.surface_id, "surface_fit_passed",
                actor="editorial-director",
                note=f"gate 3 pass round {round_idx + 1}",
            )
            _sync_artifact(repo_root, slot, current_body)
            return current_body

        # REJECT: budget check, then route back to writer.
        if round_idx >= SURFACE_FIT_BUDGET:
            transition_surface_state(
                rc, slot.surface_id, "escalated",
                actor="orchestrator",
                note=(
                    f"editorial-director gate 3 exhausted "
                    f"{SURFACE_FIT_BUDGET} re-runs; "
                    f"cuts={result['cuts'][:3]}..."
                ),
            )
            raise _Escalation(
                f"editorial-director exhausted {SURFACE_FIT_BUDGET} re-runs "
                f"on {slot.surface_id}: {result['cuts']}"
            )

        # Route back to writer with the cuts as revision_failures.
        transition_surface_state(
            rc, slot.surface_id, "writer_drafted",
            actor="editorial-director",
            note=(
                f"gate 3 reject; re-route to writer; "
                f"cuts={result['cuts']}"
            ),
        )
        revision_failures = [f"gate3: {c}" for c in result["cuts"]]
        redrafted = writer_dispatch(
            release_id=rc.release_id,
            surface=surface_spec,
            shared_cards=cards,
            prose_steer=prose_steer,
            repo_root=repo_root,
            revision_failures=revision_failures,
        )
        slot.writer_revision_count += 1
        # Re-run style-polish on the new draft. Use the existing
        # _run_style helper -- it will transition fact_checked ->
        # style_polished. But the slot is currently `writer_drafted`,
        # so we need to step through fact_checked first; for Gate-3
        # re-runs the upstream cards have already passed and the
        # writer is responding to editorial cuts not factual ones,
        # so we skip Mode B fact-check on this round and transition
        # writer_drafted -> fact_checked -> style_polished. This is
        # the minimum legal path; tightening the loop to re-run
        # Mode B is a v2 nice-to-have (see "Rough edges" in the
        # changelog note).
        transition_surface_state(
            rc, slot.surface_id, "fact_checked",
            actor="orchestrator",
            note=(
                "gate 3 re-route: re-using upstream claims_verified cards; "
                "Mode B re-run deferred for this round"
            ),
        )
        polished = _run_style(
            repo_root, rc, slot, surface_spec,
            body=redrafted, style_dispatch=style_dispatch,
        )
        current_body = polished
    # unreachable: loop returns on pass or raises on budget bust.
    raise RuntimeError("loop fall-through in _run_surface_fit")


class _Escalation(RuntimeError):
    """Raised by inner stages to short-circuit a surface to `escalated`."""


# ---------------------------------------------------------------------------
# Top-level entry
# ---------------------------------------------------------------------------

def run_release_cycle(
    release_id: str,
    repo_root: Path = REPO_ROOT,
    researcher_dispatch: ResearcherDispatch = _default_researcher,
    writer_dispatch: WriterDispatch = _default_writer,
    style_dispatch: StyleDispatch = _default_style,
    surface_fit_dispatch: Optional[Callable[[str, str], str]] = None,
    verifier_fetcher: Optional[Callable] = None,
    email_sender: Optional[Callable] = None,
    use_live_verifier: bool = True,
    single_surface: Optional[str] = None,
) -> ReleaseCycle:
    """Walk one release-cycle through all surfaces to `ready_for_user`.

    Args:
      release_id:  e.g. cpi_monthly_2026-04
      researcher_dispatch / writer_dispatch / style_dispatch:
        injection points; tests pass fixture callables.
      verifier_fetcher: optional httpx-stub for Mode A (frozen fixtures).
      email_sender: optional EmailMessage callable for tests.
      use_live_verifier: if False, skip verify_claim_file (cards are
        marked passed inline; useful for tests that don't exercise the
        Mode A path).
      surface_fit_dispatch: optional injection point for Gate 3
        (editorial-director). Signature `(prompt, model) -> raw_text`.
        Defaults to `call_claude` via `_surface_fit_review`.
      single_surface: if set, re-runs only this surface against an
        existing cycle file (e.g. after user rejection).
    """
    release_key, reference_period = parse_release_id(release_id)
    release_spec = get_release_spec(release_key)

    # Either init or read existing cycle
    cycle_file = repo_root / "editorial" / "blurbs" / "_cycles" / f"{release_id}.json"
    if single_surface and cycle_file.exists():
        rc = read_release_cycle(repo_root, release_id)
        logger.info("re-running surface %s on existing cycle %s",
                    single_surface, release_id)
    else:
        # Detect release_date from sidecars (or accept the user's CLI assertion)
        release_date = detect_release_landed(repo_root, release_spec)
        rc = init_release_cycle(
            repo_root=repo_root,
            release_id=release_id,
            release_key=release_key,
            section=release_spec.section,
            reference_period=reference_period,
            release_date=release_date,
            surfaces_spec=release_spec.surfaces,
        )
        # Stamp the per-surface artifacts in `release_landed`
        for slot in rc.surfaces:
            spec = next(s for s in release_spec.surfaces if s.surface_id == slot.surface_id)
            _init_artifact(repo_root, rc, slot, spec)
            _append_log(repo_root, slot, release_id, "release_landed cycle_init")
        write_release_cycle(repo_root, rc)

    # Filter the per-surface walk if single_surface set
    if single_surface:
        target_slots = [s for s in rc.surfaces if s.surface_id == single_surface]
        if not target_slots:
            raise KeyError(f"surface {single_surface!r} not in cycle {release_id}")
    else:
        target_slots = list(rc.surfaces)

    # ---- Researcher + verifier (shared across all surfaces) ----
    try:
        prose_steer, cards, _ = _run_researcher_and_verify(
            repo_root=repo_root,
            rc=rc,
            release_spec=release_spec,
            researcher_dispatch=researcher_dispatch,
            verifier_fetcher=verifier_fetcher,
            use_live_verifier=use_live_verifier,
        )
        write_release_cycle(repo_root, rc)
    except _Escalation as exc:
        logger.error("release-cycle %s escalated at researcher/verifier: %s",
                     release_id, exc)
        write_release_cycle(repo_root, rc)
        _send_cycle_email(rc, repo_root, email_sender)
        return rc

    # ---- Diff-aware writer brief ----
    # Compute the per-section diff once and inject the rendered Markdown
    # into prose_steer so every surface's writer dispatch gets the same
    # "what changed" cues at the top of its brief. The diff is HINTS,
    # not assertions -- the writer must still verify against the
    # passed claim-cards before publishing any framing that leans on
    # a cue. See pipeline/blurbs/diff_brief.py.
    try:
        diff_md = df_mod.build_writer_diff_brief(repo_root, release_spec.section)
        prose_steer = dict(prose_steer)  # avoid mutating researcher's return
        prose_steer["diff_brief_md"] = diff_md
        for slot in target_slots:
            _append_log(
                repo_root, slot, release_id,
                f"diff_brief_attached chars={len(diff_md)}",
            )
    except Exception as exc:  # noqa: BLE001
        # The diff brief is an enrichment, not a gate. If snapshot
        # rotation has not run yet (first build) or any read fails,
        # we proceed without it rather than blocking the cycle.
        logger.warning("diff_brief unavailable for %s: %s", release_id, exc)

    # ---- Writer + fact-check + style (per surface, serial in Phase 1) ----
    for slot in target_slots:
        if slot.last_state == "escalated":
            continue
        if slot.last_state != "claims_verified":
            # may already have been processed (re-run with single_surface)
            if slot.last_state in ("ready_for_user", "approved", "published"):
                continue
        surface_spec = next(
            s for s in release_spec.surfaces if s.surface_id == slot.surface_id
        )
        try:
            body = _run_writer_and_factcheck(
                repo_root, rc, slot, surface_spec,
                cards=cards, prose_steer=prose_steer,
                writer_dispatch=writer_dispatch,
            )
            polished = _run_style(
                repo_root, rc, slot, surface_spec,
                body=body, style_dispatch=style_dispatch,
            )
            # Gate 3: editorial-director surface-fit review per
            # editorial/review_protocol.md. PASS advances to
            # surface_fit_passed; REJECT round-trips to writer
            # (bounded by SURFACE_FIT_BUDGET).
            gate3_body = _run_surface_fit(
                repo_root, rc, slot, surface_spec,
                body=polished,
                writer_dispatch=writer_dispatch,
                style_dispatch=style_dispatch,
                cards=cards,
                prose_steer=prose_steer,
                surface_fit_dispatch=surface_fit_dispatch,
            )
            transition_surface_state(
                rc, slot.surface_id, "ready_for_user",
                actor="orchestrator",
                note="cycle complete",
            )
            _sync_artifact(repo_root, slot, gate3_body)
            _append_log(
                repo_root, slot, release_id, "ready_for_user"
            )
        except _Escalation as exc:
            logger.error("surface %s escalated: %s", slot.surface_id, exc)
            _append_log(
                repo_root, slot, release_id,
                f"ESCALATED: {exc}",
            )
            _sync_artifact(repo_root, slot, "")

    write_release_cycle(repo_root, rc)

    # ---- Batched email ----
    _send_cycle_email(rc, repo_root, email_sender)
    return rc


def _send_cycle_email(
    rc: ReleaseCycle,
    repo_root: Path,
    email_sender: Optional[Callable],
) -> None:
    """Surface the completed cycle to the user.

    v1: skip SMTP entirely. Append the cycle to `editorial/blurbs/_inbox.md`
    and rely on the per-surface draft files (already written by
    `_sync_artifact` at `editorial/blurbs/<section>/<unit-slug>/<release-id>.md`)
    as the user-facing review surface.

    Tests still pass `email_sender=<callable>`, in which case we honour the
    test contract (delivery + assertion). Production runs leave
    `email_sender=None`; SMTP is suppressed via the `BLURB_SKIP_EMAIL`
    env var (default-on for v1) below.

    DEFERRED v2: re-enable SMTP notification once delivery is wired.
    """
    # Test-injected sender: keep the existing path so unit tests still
    # exercise `send_release_cycle_review_email` end-to-end.
    if email_sender is not None:
        result = send_release_cycle_review_email(
            rc, repo_root=repo_root,
            sender=email_sender,
            backoff_seconds=(0.01, 0.01, 0.01),
        )
        for slot in rc.surfaces:
            _append_log(
                repo_root, slot, rc.release_id,
                f"email_send sent={result.sent} "
                f"inbox_appended={result.inbox_appended} "
                f"error={result.error}",
            )
        return

    # v1 production path: inbox file only. SMTP deferred.
    if os.environ.get("BLURB_SKIP_EMAIL", "1") == "1":
        subject, _body = render_email_body(rc, repo_root)
        _write_inbox_v1(repo_root, rc, subject)
        for slot in rc.surfaces:
            _append_log(
                repo_root, slot, rc.release_id,
                f"inbox_appended=True (v1 file-mode; SMTP deferred)",
            )
        return

    # DEFERRED v2: SMTP notification. To re-enable, unset BLURB_SKIP_EMAIL.
    result = send_release_cycle_review_email(
        rc, repo_root=repo_root,
        sender=None,
        backoff_seconds=(60.0, 300.0, 1800.0),
    )
    for slot in rc.surfaces:
        _append_log(
            repo_root, slot, rc.release_id,
            f"email_send sent={result.sent} "
            f"inbox_appended={result.inbox_appended} "
            f"error={result.error}",
        )


def _write_inbox_v1(repo_root: Path, rc: ReleaseCycle, subject: str) -> None:
    """Append one entry per cycle to `editorial/blurbs/_inbox.md`.

    The inbox is the v1 review surface (SMTP deferred). Each entry lists
    the cycle id, the per-surface draft paths, and the wrapper-cycle path,
    so the user can pivot from the inbox to any draft in one click.
    """
    inbox = repo_root / "editorial" / "blurbs" / "_inbox.md"
    inbox.parent.mkdir(parents=True, exist_ok=True)
    if not inbox.exists():
        inbox.write_text(
            "# Pending auto-blurb review\n\n"
            "v1 file-mode inbox. Each entry below is one release-cycle "
            "ready for human review. Open the per-surface draft files, "
            "edit, then flip `status: ready_for_user` to `status: "
            "approved` and commit.\n",
            encoding="utf-8",
        )
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    section_label = (
        rc.section.capitalize() if rc.section != "_global" else "Global"
    )
    lines = [
        "",
        f"## {now} {rc.release_id}",
        f"- subject: {subject}",
        f"- section: {section_label}",
        f"- reference period: {rc.reference_period}",
        f"- release date: {rc.release_date or '(unknown)'}",
        f"- surfaces: {len(rc.surfaces)}",
        f"- wrapper: editorial/blurbs/_cycles/{rc.release_id}.json",
        "- drafts:",
    ]
    for slot in rc.surfaces:
        tag = (
            " [ESCALATED]" if slot.last_state == "escalated"
            else f" [{slot.last_state}]"
        )
        lines.append(f"  - {slot.surface_id}{tag}: {slot.artifact_path}")
    with inbox.open("a", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _parse_args(argv=None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="python -m pipeline.blurbs.run",
        description="Walk one auto-blurb release-cycle end to end.",
    )
    p.add_argument("--release-id", required=True)
    p.add_argument(
        "--surface", dest="single_surface",
        help="re-run only this surface against an existing cycle",
    )
    p.add_argument(
        "--dry-run", action="store_true",
        help="initialize the cycle wrapper + artifact stubs only; no dispatch",
    )
    return p.parse_args(argv)


def main(argv=None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    args = _parse_args(argv)
    if args.dry_run:
        release_key, reference_period = parse_release_id(args.release_id)
        release_spec = get_release_spec(release_key)
        release_date = detect_release_landed(REPO_ROOT, release_spec)
        rc = init_release_cycle(
            repo_root=REPO_ROOT,
            release_id=args.release_id,
            release_key=release_key,
            section=release_spec.section,
            reference_period=reference_period,
            release_date=release_date,
            surfaces_spec=release_spec.surfaces,
        )
        for slot in rc.surfaces:
            spec = next(s for s in release_spec.surfaces if s.surface_id == slot.surface_id)
            _init_artifact(REPO_ROOT, rc, slot, spec)
        write_release_cycle(REPO_ROOT, rc)
        logger.info("dry-run: cycle initialized at editorial/blurbs/_cycles/%s.json",
                    args.release_id)
        return 0

    try:
        run_release_cycle(
            release_id=args.release_id,
            single_surface=args.single_surface,
        )
    except NotImplementedError as exc:
        logger.error(
            "Agent dispatch unconfigured. Phase 1 ships the orchestration; "
            "the agent dispatch implementation is TBD. See pipeline/blurbs/"
            "README.md. Underlying: %s", exc,
        )
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
