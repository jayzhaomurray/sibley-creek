"""Batched release-cycle review email.

One email per release-cycle (not per surface) in Phase 1. Body shape per
Section 5 of editorial/auto_blurb_process.md, expanded to list every
surface's polished body in turn.

Required env vars:
    SMTP_HOST    -- relay host
    SMTP_PORT    -- relay port (int)
    SMTP_USER    -- SASL username (optional; some relays accept anon)
    SMTP_PASS    -- SASL password (optional)
    SMTP_FROM    -- envelope/from address (defaults to SMTP_USER)
    BLURB_REVIEW_TO -- the recipient (defaults to jayzhaomurray@outlook.com)

Failure policy: 3 retries with exponential backoff (1m, 5m, 30m caps cut
to 1s/5s/30s for unit-test smoothness; production uses the larger waits
when invoked from the CLI). On exhaustion, append to
`editorial/blurbs/_inbox.md` and surface the failure to caller.
"""

from __future__ import annotations

import logging
import os
import smtplib
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from email.message import EmailMessage
from pathlib import Path
from typing import Callable, Optional

from pipeline.blurbs.artifact import read_artifact
from pipeline.blurbs.release_cycle import ReleaseCycle

logger = logging.getLogger("pipeline.blurbs.email")


_DEFAULT_TO = "jayzhaomurray@outlook.com"


@dataclass
class EmailResult:
    sent: bool
    inbox_appended: bool
    error: Optional[str]
    subject: str
    body: str


# ---------------------------------------------------------------------------
# Body rendering
# ---------------------------------------------------------------------------

def _bullet_line(label: str, value: str) -> str:
    return f"{label:<11}{value}"


def render_email_body(rc: ReleaseCycle, repo_root: Path) -> tuple[str, str]:
    """Render (subject, body) for a release-cycle email."""
    section_label = rc.section.capitalize() if rc.section != "_global" else "Global"
    subject = (
        f"Auto-blurb ready for review: {section_label} "
        f"{_human_release_key(rc.release_key)} {rc.reference_period}"
    )

    if rc.has_escalation:
        subject = (
            f"Auto-blurb escalation: stage failed for {rc.release_id}"
        )

    lines: list[str] = []
    lines.append(f"Release:    {rc.release_id}")
    lines.append(f"Section:    {section_label}")
    lines.append(f"Reference:  {rc.reference_period}")
    lines.append(f"Release at: {rc.release_date or '(unknown)'}")
    lines.append(f"Created:    {rc.created_at}")
    lines.append("")
    lines.append(f"Surfaces in this cycle: {len(rc.surfaces)}")
    lines.append("")
    lines.append("=" * 60)

    for slot in rc.surfaces:
        path = repo_root / slot.artifact_path
        state_tag = f"[{slot.last_state}]"
        if slot.last_state == "escalated":
            state_tag = "[ESCALATED]"
        lines.append("")
        lines.append(f"-- {slot.surface_id} {state_tag} --")
        lines.append(f"Path: {slot.artifact_path}")
        try:
            artifact, body = read_artifact(path)
        except FileNotFoundError:
            lines.append("(artifact file missing; pipeline error)")
            continue
        except Exception as exc:
            lines.append(f"(could not read artifact: {exc})")
            continue
        cap = artifact.char_cap
        body_text = body.strip()
        lines.append(f"Char cap: {cap}; body length: {len(body_text)}")
        if artifact.flags:
            lines.append(f"Flags: {artifact.flags}")
        else:
            lines.append("Flags: none")
        lines.append("")
        lines.append(body_text)
        lines.append("")

    lines.append("=" * 60)
    lines.append("")
    lines.append("To approve as-is for each surface:")
    lines.append("  set status: ready_for_user -> status: approved,")
    lines.append("  commit on main. (See pipeline/blurbs/approve_cycle.py for")
    lines.append("  the --release-id <id> --all bulk-approve shortcut.)")
    lines.append("")
    lines.append("Wrapper cycle file:")
    lines.append(f"  editorial/blurbs/_cycles/{rc.release_id}.json")
    body = "\n".join(lines) + "\n"
    return subject, body


def _human_release_key(release_key: str) -> str:
    pretty = {
        "cpi_monthly":   "Headline CPI",
        "lfs_monthly":   "LFS",
        "boc_rate_decision": "BoC rate decision",
    }
    return pretty.get(release_key, release_key)


# ---------------------------------------------------------------------------
# SMTP send (3 retries, exponential backoff)
# ---------------------------------------------------------------------------

def _build_message(subject: str, body: str, to_addr: str, from_addr: str) -> EmailMessage:
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = from_addr
    msg["To"] = to_addr
    msg.set_content(body)
    return msg


def _send_via_smtp(
    msg: EmailMessage,
    host: str,
    port: int,
    user: Optional[str],
    password: Optional[str],
) -> None:
    if port == 465:
        with smtplib.SMTP_SSL(host, port, timeout=30) as srv:
            if user:
                srv.login(user, password or "")
            srv.send_message(msg)
    else:
        with smtplib.SMTP(host, port, timeout=30) as srv:
            srv.ehlo()
            try:
                srv.starttls()
                srv.ehlo()
            except smtplib.SMTPException:
                pass
            if user:
                srv.login(user, password or "")
            srv.send_message(msg)


def _append_inbox(repo_root: Path, rc: ReleaseCycle, subject: str) -> None:
    inbox = repo_root / "editorial" / "blurbs" / "_inbox.md"
    inbox.parent.mkdir(parents=True, exist_ok=True)
    if not inbox.exists():
        inbox.write_text("# Pending auto-blurb review\n\n", encoding="utf-8")
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    line = (
        f"\n## {now} {rc.release_id}\n"
        f"- subject: {subject}\n"
        f"- surfaces: {len(rc.surfaces)}\n"
        f"- wrapper: editorial/blurbs/_cycles/{rc.release_id}.json\n"
    )
    with inbox.open("a", encoding="utf-8") as f:
        f.write(line)


def send_release_cycle_review_email(
    rc: ReleaseCycle,
    repo_root: Path,
    sender: Optional[Callable[[EmailMessage], None]] = None,
    sleep_fn: Callable[[float], None] = time.sleep,
    backoff_seconds: tuple[float, float, float] = (60.0, 300.0, 1800.0),
) -> EmailResult:
    """Render + send. On 3 SMTP failures, append to _inbox.md instead.

    Args:
      sender: optional callable for tests (overrides SMTP). Receives a fully
        rendered EmailMessage.
      sleep_fn: sleep injection point for tests.
      backoff_seconds: (1m, 5m, 30m) default; tests override to fast.
    """
    subject, body = render_email_body(rc, repo_root)
    to_addr = os.environ.get("BLURB_REVIEW_TO", _DEFAULT_TO)
    from_addr = os.environ.get("SMTP_FROM") or os.environ.get(
        "SMTP_USER", "macro-research-bot@localhost"
    )
    msg = _build_message(subject, body, to_addr, from_addr)

    if sender is not None:
        # injected sender path (tests + locally-stubbed environments)
        last_err: Optional[str] = None
        for attempt, wait in enumerate(backoff_seconds, start=1):
            try:
                sender(msg)
                return EmailResult(
                    sent=True, inbox_appended=False, error=None,
                    subject=subject, body=body,
                )
            except Exception as exc:
                last_err = f"attempt {attempt}: {type(exc).__name__}: {exc}"
                logger.warning("email send failed (%s); backing off %ss", last_err, wait)
                if attempt < len(backoff_seconds):
                    sleep_fn(wait)
        _append_inbox(repo_root, rc, subject)
        return EmailResult(
            sent=False, inbox_appended=True, error=last_err,
            subject=subject, body=body,
        )

    # Live SMTP path
    host = os.environ.get("SMTP_HOST")
    if not host:
        _append_inbox(repo_root, rc, subject)
        return EmailResult(
            sent=False, inbox_appended=True,
            error="SMTP_HOST not set; appended to _inbox.md",
            subject=subject, body=body,
        )
    port = int(os.environ.get("SMTP_PORT", "587"))
    user = os.environ.get("SMTP_USER")
    password = os.environ.get("SMTP_PASS")

    last_err = None
    for attempt, wait in enumerate(backoff_seconds, start=1):
        try:
            _send_via_smtp(msg, host, port, user, password)
            return EmailResult(
                sent=True, inbox_appended=False, error=None,
                subject=subject, body=body,
            )
        except Exception as exc:
            last_err = f"attempt {attempt}: {type(exc).__name__}: {exc}"
            logger.warning("SMTP attempt %d failed: %s", attempt, last_err)
            if attempt < len(backoff_seconds):
                sleep_fn(wait)
    _append_inbox(repo_root, rc, subject)
    return EmailResult(
        sent=False, inbox_appended=True, error=last_err,
        subject=subject, body=body,
    )
