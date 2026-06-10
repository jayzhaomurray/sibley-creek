"""Core notification sender for Sibley Creek Phase 1 monitoring.

Sends email via SMTP using credentials from environment variables.
Writes to a dry-run file instead of sending when SIBLEY_NOTIFICATIONS_DRY_RUN=1.

Required environment variables (same naming pattern as pipeline/blurbs/email.py)
----------------------------------------------------------------------------------
    SMTP_HOST   -- relay host (e.g. smtp.gmail.com)
    SMTP_PORT   -- relay port as integer (e.g. 587 for STARTTLS, 465 for SSL)
    SMTP_USER   -- SASL username / login
    SMTP_PASS   -- SASL password
    SMTP_FROM   -- envelope from address (defaults to jayzhaomurray@gmail.com)

Optional
---------
    SIBLEY_NOTIFICATIONS_DRY_RUN=1
        Writes the email to data/derived/notification_dry_run.txt instead of
        sending. Safe for CI/CD runs; first real send must be a manual pipeline
        invocation with dry-run unset.

    SIBLEY_NOTIFICATIONS_DISABLED_TYPES=failure,new_vintage
        Comma-separated list of event types to suppress completely.
        Useful for silencing noisy types during an incident.

Subject-line prefix mapping
----------------------------
    fyi             -> [Sibley Creek Update]
    review          -> [Sibley Creek Review]
    alert           -> [Sibley Creek Alert]
    action_required -> [Sibley Creek Action Required]

Body format (phone-readable in 5 seconds)
------------------------------------------
    WHAT HAPPENED
    <one paragraph>

    WHAT VISITORS SEE
    <one paragraph>

    WHAT TO DO
    <one paragraph; "Nothing immediate." if no action needed>

    DETAILS
    <key: value pairs; timestamps; relevant links>

Failure policy
--------------
On SMTP error: logs the error, appends to ledger with sent=False detail,
re-raises so the caller can decide whether to propagate. Does NOT silently
swallow SMTP failures.
"""

from __future__ import annotations

import logging
import os
import smtplib
from datetime import datetime, timezone
from email.message import EmailMessage
from pathlib import Path
from typing import Any, Optional

from pipeline.notifications.dedupe import should_send
from pipeline.notifications.ledger import append_event

logger = logging.getLogger("pipeline.notifications.send")

ROOT = Path(__file__).resolve().parents[2]
DRY_RUN_PATH = ROOT / "data" / "derived" / "notification_dry_run.txt"

_DEFAULT_FROM = "jayzhaomurray@gmail.com"
_DEFAULT_TO = "jayzhaomurray@gmail.com"

_SEVERITY_PREFIX: dict[str, str] = {
    "fyi": "Update",
    "review": "Review",
    "alert": "Alert",
    "action_required": "Action Required",
}


def _disabled_types() -> set[str]:
    raw = os.environ.get("SIBLEY_NOTIFICATIONS_DISABLED_TYPES", "")
    return {t.strip() for t in raw.split(",") if t.strip()}


def _build_subject(severity: str, human_subject: str) -> str:
    prefix = _SEVERITY_PREFIX.get(severity, "Update")
    return f"[Sibley Creek {prefix}] {human_subject}"


def _send_smtp(subject: str, body: str) -> None:
    host = os.environ["SMTP_HOST"]
    port = int(os.environ["SMTP_PORT"])
    user = os.environ.get("SMTP_USER", "")
    password = os.environ.get("SMTP_PASS", "")
    from_addr = os.environ.get("SMTP_FROM", _DEFAULT_FROM)
    to_addr = _DEFAULT_TO

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = from_addr
    msg["To"] = to_addr
    msg.set_content(body)

    if port == 465:
        with smtplib.SMTP_SSL(host, port) as server:
            if user:
                server.login(user, password)
            server.send_message(msg)
    else:
        with smtplib.SMTP(host, port) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            if user:
                server.login(user, password)
            server.send_message(msg)


def _write_dry_run(subject: str, body: str) -> None:
    DRY_RUN_PATH.parent.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    with DRY_RUN_PATH.open("a", encoding="utf-8") as fh:
        fh.write(f"\n{'='*72}\n")
        fh.write(f"DRY-RUN @ {ts}\n")
        fh.write(f"Subject: {subject}\n")
        fh.write(f"To: {_DEFAULT_TO}\n")
        fh.write(f"{'='*72}\n")
        fh.write(body)
        fh.write("\n")
    logger.info("dry-run: email written to %s", DRY_RUN_PATH)


def send_notification(
    event_type: str,
    severity: str,
    subject: str,
    body: str,
    dedupe_key: Optional[str] = None,
    details: Optional[dict[str, Any]] = None,
) -> bool:
    """Send one notification email and record it in the event ledger.

    Args:
        event_type:   "failure" | "new_vintage" | "news_feed_update"
        severity:     "fyi" | "review" | "alert" | "action_required"
        subject:      Human subject line (without severity prefix).
        body:         Full email body (the WHAT HAPPENED / VISITORS / TODO /
                      DETAILS structure).
        dedupe_key:   Optional key for deduplication. None = always send.
        details:      Optional dict of type-specific metadata stored in ledger.

    Returns:
        True if the notification was sent (or dry-run written).
        False if suppressed (disabled type or dedup).

    Raises:
        smtplib.SMTPException: on delivery failure.

    Note:
        If SMTP_HOST / SMTP_PORT are unset and dry-run is off, the send is
        skipped cleanly with a logged warning (returns False, ledger entry
        error="smtp-not-configured"). The notification channel being
        unconfigured must never crash or mask the pipeline failure it is
        trying to report (observed in CI: KeyError 'SMTP_HOST' ERROR-logged
        on every failed build-financial-daily run, 2026-05-30..06-09).
    """
    # Check disabled types
    if event_type in _disabled_types():
        logger.info(
            "notification suppressed (type disabled): type=%s subject=%s",
            event_type, subject,
        )
        return False

    # Deduplication check
    if not should_send(dedupe_key, event_type=event_type):
        logger.info(
            "notification suppressed (dedupe): key=%s type=%s",
            dedupe_key, event_type,
        )
        return False

    full_subject = _build_subject(severity, subject)
    dry_run = os.environ.get("SIBLEY_NOTIFICATIONS_DRY_RUN", "0") == "1"

    # SMTP-not-configured guard: skip cleanly instead of raising KeyError.
    # CI does not have SMTP secrets configured; an unconfigured channel is a
    # warning condition, not an error -- erroring here pollutes the log of
    # the underlying failure this notification is reporting.
    if not dry_run and not (os.environ.get("SMTP_HOST") and os.environ.get("SMTP_PORT")):
        logger.warning(
            "notification skipped (SMTP not configured: SMTP_HOST/SMTP_PORT "
            "unset): type=%s severity=%s subject=%s",
            event_type, severity, full_subject,
        )
        append_event({
            "type": event_type,
            "severity": severity,
            "subject": full_subject,
            "body_preview": body[:200],
            "dedupe_key": dedupe_key,
            "details": details or {},
            "sent": False,
            "dry_run": dry_run,
            "error": "smtp-not-configured",
        })
        return False

    sent = False
    error_msg: Optional[str] = None

    try:
        if dry_run:
            _write_dry_run(full_subject, body)
            sent = True
        else:
            _send_smtp(full_subject, body)
            sent = True
            logger.info("notification sent: type=%s severity=%s subject=%s",
                        event_type, severity, full_subject)
    except Exception as exc:  # noqa: BLE001
        error_msg = f"{type(exc).__name__}: {exc}"
        logger.error("notification FAILED: type=%s error=%s subject=%s",
                     event_type, error_msg, full_subject)
        raise

    finally:
        # Record in ledger regardless of send outcome so audit trail is complete
        append_event({
            "type": event_type,
            "severity": severity,
            "subject": full_subject,
            "body_preview": body[:200],
            "dedupe_key": dedupe_key,
            "details": details or {},
            "sent": sent,
            "dry_run": dry_run,
            "error": error_msg,
        })

    return sent
