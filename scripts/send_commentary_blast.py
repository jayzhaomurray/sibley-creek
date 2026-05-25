"""Send a personalized blast for a published Sibley Creek commentary.

USAGE
-----
Dry-run (default, safe):
    python scripts/send_commentary_blast.py --commentary cpi-april-2026

Target a specific category of recipients:
    python scripts/send_commentary_blast.py --commentary cpi-april-2026 --category reporter
    python scripts/send_commentary_blast.py --commentary cpi-april-2026 --category subscriber
    python scripts/send_commentary_blast.py --commentary cpi-april-2026 --category all

Preview first N recipients only:
    python scripts/send_commentary_blast.py --commentary cpi-april-2026 --limit 3

Live send (requires explicit flag):
    python scripts/send_commentary_blast.py --commentary cpi-april-2026 --send

Override template for this blast:
    python scripts/send_commentary_blast.py --commentary cpi-april-2026 --send \
        --template-override path/to/custom.md

COMMENTARY METADATA
-------------------
The script resolves commentary metadata from one of two sources, in order:

    1. bylines/commentaries/<slug>/blast_meta.yaml    (per-slug override)
    2. src/data/sections.ts                            (canonical registry)

The TypeScript registry is parsed with a lightweight regex extractor --
no transpilation needed. This is intentional: the registry is the source of
truth and we don't want a parallel YAML file to drift. The regex targets the
literal object literal block for the slug; it is not a general TS parser.

If a per-slug blast_meta.yaml exists, it takes precedence and can override
title, publishedAt, or excerpt (useful if the blast is going out before the
TypeScript registry is updated, or if you want a shorter subject line).

RECIPIENT LIST
--------------
Loaded from business/recipients/recipients.yaml. Only entries with active: true
are included. Entries with active: false are silently skipped (not counted
against the cap). Use --category to narrow to a subset (reporter, subscriber,
friend, internal, or all). Default is all active contacts.

SMTP CREDENTIALS
----------------
Loaded from business/secrets/migadu_smtp.env or env vars:
    MIGADU_USERNAME   full email address (e.g. jay@sibleycreek.ca)
    MIGADU_PASSWORD   mailbox password

The From address is always MIGADU_USERNAME. The script refuses to send
from any other address to protect sender reputation.

DAILY CAP
---------
Migadu Mini: 100 outbound messages/day, counted per recipient.
The script reads business/blast/blast_log.csv, counts sends for today
(UTC date), and refuses if the current batch would exceed 100.

LOG FORMAT
----------
business/blast/blast_log.csv columns:
    sent_at_utc, slug, recipient_email, recipient_name, outlet,
    subject, smtp_response, status

status is one of: sent | dry_run | failed | skipped_cap
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import smtplib
import ssl
import sys
from datetime import datetime, timezone
from email.message import EmailMessage
from pathlib import Path
from typing import Any, Optional

from ruamel.yaml import YAML as _YAML

_yaml_parser = _YAML(typ="safe")

from pydantic import BaseModel, field_validator

# ---------------------------------------------------------------------------
# Repo-root resolution
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent

RECIPIENTS_PATH = REPO_ROOT / "business" / "recipients" / "recipients.yaml"
BLAST_LOG_PATH = REPO_ROOT / "business" / "blast" / "blast_log.csv"
TEMPLATES_DIR = REPO_ROOT / "business" / "blast" / "templates"
DEFAULT_TEMPLATE = TEMPLATES_DIR / "commentary_blast.md"
SMTP_ENV_PATH = REPO_ROOT / "business" / "secrets" / "migadu_smtp.env"
SECTIONS_TS_PATH = REPO_ROOT / "src" / "data" / "sections.ts"
BYLINES_DIR = REPO_ROOT / "bylines" / "commentaries"

MIGADU_SMTP_HOST = "smtp.migadu.com"
MIGADU_SMTP_PORT = 465  # SSL
MIGADU_DAILY_CAP = 100

SITE_BASE_URL = "https://sibleycreek.ca"

LOG_FIELDNAMES = [
    "sent_at_utc",
    "slug",
    "recipient_email",
    "recipient_name",
    "outlet",
    "subject",
    "smtp_response",
    "status",
]


# ---------------------------------------------------------------------------
# Pydantic models — boundary validation
# ---------------------------------------------------------------------------


class Recipient(BaseModel):
    """One entry from recipients.yaml."""

    email: str
    name: str
    category: str  # reporter | subscriber | friend | internal
    tier: Any = None
    source: str = ""
    outlet: Optional[str] = ""
    beat: Optional[str] = ""
    active: bool = False
    notes: Optional[str] = ""
    added: Any = ""  # ruamel.yaml deserializes YYYY-MM-DD as datetime.date; accept either

    @field_validator("name")
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v.strip() or v.strip().startswith("#"):
            # Name was not provided on the form; use empty string to let the
            # template use its own fallback salutation.
            return ""
        return v.strip()

    @field_validator("email")
    @classmethod
    def valid_email(cls, v: str) -> str:
        v = v.strip()
        if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", v):
            raise ValueError(f"not a valid email address: {v!r}")
        return v

    @property
    def first_name(self) -> str:
        """Returns the first word of name, or empty string if name is blank."""
        parts = self.name.strip().split()
        return parts[0] if parts else ""

    @property
    def last_name(self) -> str:
        """Returns everything after the first word of name, or empty string."""
        parts = self.name.strip().split()
        return " ".join(parts[1:]) if len(parts) > 1 else ""


class CommentaryMeta(BaseModel):
    """Resolved metadata for one commentary."""

    slug: str
    title: str
    published_at: str  # YYYY-MM-DD
    excerpt: str
    pdf_path: str       # site-relative, e.g. /research/commentaries/cpi-april-2026.pdf

    @property
    def public_url(self) -> str:
        return f"{SITE_BASE_URL}/research/commentaries/{self.slug}/"

    @property
    def pdf_url(self) -> str:
        return f"{SITE_BASE_URL}{self.pdf_path}"


# ---------------------------------------------------------------------------
# Credential loading
# ---------------------------------------------------------------------------


def _load_env_file(path: Path) -> dict[str, str]:
    """Parse a KEY=VALUE env file, skipping blank lines and # comments."""
    result: dict[str, str] = {}
    if not path.exists():
        return result
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, val = line.partition("=")
        result[key.strip()] = val.strip()
    return result


def load_smtp_credentials() -> tuple[str, str]:
    """Return (username, password) from env file or environment variables.

    Priority: env vars override the file (so CI can inject secrets without
    touching the filesystem).
    """
    file_env = _load_env_file(SMTP_ENV_PATH)

    username = os.environ.get("MIGADU_USERNAME") or file_env.get("MIGADU_USERNAME", "")
    password = os.environ.get("MIGADU_PASSWORD") or file_env.get("MIGADU_PASSWORD", "")

    if not username:
        sys.exit(
            "ERROR: MIGADU_USERNAME not set. "
            "Add it to business/secrets/migadu_smtp.env or export as env var."
        )
    if not password:
        sys.exit(
            "ERROR: MIGADU_PASSWORD not set. "
            "Add it to business/secrets/migadu_smtp.env or export as env var."
        )

    return username, password


# ---------------------------------------------------------------------------
# Commentary metadata resolution
# ---------------------------------------------------------------------------


def _parse_ts_commentary(slug: str) -> Optional[dict]:
    """Extract a single commentary object from sections.ts by slug.

    Uses a targeted regex against the object literal block. This is not
    a general TypeScript parser -- it targets the stable shape of the
    commentaries array in src/data/sections.ts. Fails loudly if the
    shape doesn't match rather than returning bad data.
    """
    source = SECTIONS_TS_PATH.read_text(encoding="utf-8")

    # Find the object block that contains slug: "<slug>"
    # Strategy: locate the slug string, then walk outward to the enclosing { }.
    needle = f'slug: "{slug}"'
    idx = source.find(needle)
    if idx == -1:
        return None

    # Walk backward to find the opening brace of this object
    brace_start = source.rfind("{", 0, idx)
    if brace_start == -1:
        return None

    # Walk forward counting braces to find the matching closing brace
    depth = 0
    pos = brace_start
    while pos < len(source):
        ch = source[pos]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                break
        pos += 1

    block = source[brace_start : pos + 1]

    def extract_str(key: str, text: str) -> Optional[str]:
        # Matches: key: "value" or key:\n  "value" (with possible line continuations)
        # Also handles template literals (backtick) just in case.
        pattern = rf'{key}:\s*["`]([^"`]+)["`]'
        m = re.search(pattern, text, re.DOTALL)
        if m:
            # Collapse internal whitespace for multi-line strings
            return re.sub(r"\s+", " ", m.group(1)).strip()
        return None

    title = extract_str("title", block)
    published_at = extract_str("publishedAt", block)
    pdf_path = extract_str("pdfPath", block)
    excerpt = extract_str("excerpt", block)

    if not all([title, published_at, pdf_path, excerpt]):
        return None

    return {
        "slug": slug,
        "title": title,
        "published_at": published_at,
        "pdf_path": pdf_path,
        "excerpt": excerpt,
    }


def resolve_commentary(slug: str) -> CommentaryMeta:
    """Resolve commentary metadata for the given slug.

    Checks bylines/commentaries/<slug>/blast_meta.yaml first, then falls
    back to parsing src/data/sections.ts. Exits loudly if neither source
    can produce a complete record.
    """
    override_path = BYLINES_DIR / slug / "blast_meta.yaml"
    base: dict = {}

    if override_path.exists():
        raw = _yaml_parser.load(override_path.read_text(encoding="utf-8")) or {}
        base.update(raw)

    # Fill missing fields from sections.ts
    ts_data = _parse_ts_commentary(slug)
    if ts_data:
        for k, v in ts_data.items():
            if k not in base or not base[k]:
                base[k] = v

    required = ["slug", "title", "published_at", "pdf_path", "excerpt"]
    missing = [k for k in required if not base.get(k)]
    if missing:
        sys.exit(
            f"ERROR: Commentary '{slug}' is missing fields: {missing}.\n"
            f"  - Add '{slug}' to src/data/sections.ts, OR\n"
            f"  - Create bylines/commentaries/{slug}/blast_meta.yaml with the missing fields."
        )

    return CommentaryMeta(**{k: base[k] for k in required})


# ---------------------------------------------------------------------------
# Recipient list
# ---------------------------------------------------------------------------


VALID_CATEGORIES = {"reporter", "subscriber", "friend", "internal"}


def load_recipients(
    limit: Optional[int] = None,
    category: Optional[str] = None,
) -> list[Recipient]:
    """Load active recipients from recipients.yaml, filtered by category.

    Args:
        limit: cap to first N recipients after filtering.
        category: one of reporter | subscriber | friend | internal | all | None.
                  None and "all" both mean no category filter.
    """
    if not RECIPIENTS_PATH.exists():
        sys.exit(
            f"ERROR: Recipient list not found at {RECIPIENTS_PATH}.\n"
            f"Expected: business/recipients/recipients.yaml\n"
            f"Run: node scripts/pull_subscribers.mjs  to populate from formsubmit."
        )

    raw = _yaml_parser.load(RECIPIENTS_PATH.read_text(encoding="utf-8")) or []
    if not isinstance(raw, list):
        sys.exit(f"ERROR: {RECIPIENTS_PATH} must be a YAML list of recipient entries.")

    cat_filter = None if (category is None or category == "all") else category
    if cat_filter and cat_filter not in VALID_CATEGORIES:
        sys.exit(
            f"ERROR: Unknown --category '{cat_filter}'. "
            f"Valid values: {', '.join(sorted(VALID_CATEGORIES))}, all"
        )

    recipients: list[Recipient] = []
    errors: list[str] = []

    for i, entry in enumerate(raw):
        if not isinstance(entry, dict):
            continue
        try:
            r = Recipient.model_validate(entry)
        except Exception as exc:
            errors.append(f"  entry[{i}] {entry.get('email', '?')}: {exc}")
            continue
        if not r.active:
            continue
        if cat_filter and r.category != cat_filter:
            continue
        recipients.append(r)

    if errors:
        print("WARNING: Some recipient entries failed validation and were skipped:")
        for e in errors:
            print(e)

    if limit is not None:
        recipients = recipients[:limit]

    return recipients


# ---------------------------------------------------------------------------
# Daily cap check
# ---------------------------------------------------------------------------


def _today_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def count_sends_today() -> int:
    """Count rows in blast_log.csv where status='sent' and date is today (UTC)."""
    if not BLAST_LOG_PATH.exists():
        return 0

    today = _today_utc()
    count = 0
    with BLAST_LOG_PATH.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            sent_at = row.get("sent_at_utc", "")
            status = row.get("status", "")
            if status == "sent" and sent_at.startswith(today):
                count += 1
    return count


def check_daily_cap(batch_size: int) -> int:
    """Check the daily cap. Returns sends_today. Exits if batch would exceed cap."""
    sends_today = count_sends_today()
    if sends_today + batch_size > MIGADU_DAILY_CAP:
        remaining = MIGADU_DAILY_CAP - sends_today
        sys.exit(
            f"ERROR: Daily cap would be exceeded.\n"
            f"  Cap:         {MIGADU_DAILY_CAP}/day\n"
            f"  Sent today:  {sends_today}\n"
            f"  Remaining:   {remaining}\n"
            f"  Batch size:  {batch_size}\n"
            f"Use --limit {remaining} to send to the first {remaining} recipients."
        )
    return sends_today


# ---------------------------------------------------------------------------
# Template rendering
# ---------------------------------------------------------------------------


def load_template(path: Path) -> tuple[str, str]:
    """Parse a template file with a YAML front-matter subject line.

    Returns (subject_template, body_template).

    Front-matter format:
        ---
        subject: Sibley Creek commentary -- {{commentary_title}}
        ---
        <body>
    """
    text = path.read_text(encoding="utf-8")

    if not text.startswith("---"):
        sys.exit(
            f"ERROR: Template {path} must begin with YAML front-matter.\n"
            f"  Expected: ---\\nsubject: <subject line>\\n---\\n<body>"
        )

    parts = text.split("---", maxsplit=2)
    if len(parts) < 3:
        sys.exit(f"ERROR: Template {path} has malformed front-matter (need two '---' delimiters).")

    front = _yaml_parser.load(parts[1]) or {}
    subject_template = front.get("subject", "")
    body_template = parts[2].lstrip("\n")

    if not subject_template:
        sys.exit(f"ERROR: Template {path} front-matter is missing 'subject:' key.")

    return subject_template, body_template


def render(template: str, variables: dict[str, str]) -> str:
    """Replace {{key}} slots with values. Unknown slots are left untouched.

    Post-substitution: collapses runs of 3+ consecutive blank lines to 2,
    so an empty {{notes}} slot doesn't leave a double-blank gap in the body.
    """
    result = template
    for key, val in variables.items():
        result = result.replace("{{" + key + "}}", val)
    # Collapse triple-blank-line runs (empty slot side-effect) to one blank line.
    result = re.sub(r"\n{3,}", "\n\n", result)
    return result


def build_variables(recipient: Recipient, commentary: CommentaryMeta) -> dict[str, str]:
    return {
        "first_name": recipient.first_name,
        "last_name": recipient.last_name,
        "name": recipient.name.strip(),
        "outlet": recipient.outlet or "",
        "commentary_title": commentary.title,
        "commentary_url": commentary.public_url,
        "commentary_pdf_url": commentary.pdf_url,
        "commentary_date": commentary.published_at,
        "commentary_excerpt": commentary.excerpt,
        # notes: rendered as a standalone paragraph when non-empty.
        # Template places {{notes}} on its own line between two blank lines.
        # Non-empty: substitute the content (the surrounding blank lines in the
        # template already provide spacing). Empty: collapse to empty string;
        # post-render cleanup below trims the resulting double-blank-line.
        "notes": (recipient.notes or "").strip(),
    }


# ---------------------------------------------------------------------------
# Send
# ---------------------------------------------------------------------------


def _append_log_row(row: dict) -> None:
    """Append one row to blast_log.csv, creating the file and header if needed."""
    BLAST_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    write_header = not BLAST_LOG_PATH.exists()
    with BLAST_LOG_PATH.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=LOG_FIELDNAMES)
        if write_header:
            writer.writeheader()
        writer.writerow(row)


def send_one(
    *,
    recipient: Recipient,
    commentary: CommentaryMeta,
    subject: str,
    body: str,
    from_address: str,
    smtp_username: str,
    smtp_password: str,
) -> str:
    """Send a single email. Returns the SMTP response string."""
    msg = EmailMessage()
    msg["From"] = f"Jay Zhao-Murray <{from_address}>"
    display = recipient.name.strip() if recipient.name.strip() else recipient.email
    msg["To"] = f"{display} <{recipient.email}>"
    msg["Subject"] = subject
    msg.set_content(body)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(MIGADU_SMTP_HOST, MIGADU_SMTP_PORT, context=context) as server:
        server.login(smtp_username, smtp_password)
        result = server.send_message(msg)
        # send_message returns a dict of refused recipients on partial failure.
        # Empty dict means all accepted.
        if result:
            raise smtplib.SMTPException(f"Refused recipients: {result}")
        return "250 OK"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Send a personalized journalist blast for a Sibley Creek commentary.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--commentary",
        required=True,
        metavar="SLUG",
        help="Commentary slug, e.g. cpi-april-2026. Must exist in sections.ts or blast_meta.yaml.",
    )
    parser.add_argument(
        "--send",
        action="store_true",
        default=False,
        help="Actually send emails. Without this flag the script runs in dry-run mode.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Explicit dry-run flag (equivalent to omitting --send). Renders to stdout.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        metavar="N",
        help="Cap to first N active journalists. Useful for testing.",
    )
    parser.add_argument(
        "--category",
        default="all",
        metavar="CATEGORY",
        help=(
            "Filter recipients by category: reporter | subscriber | friend | internal | all. "
            "Defaults to all (all active recipients)."
        ),
    )
    parser.add_argument(
        "--template-override",
        default=None,
        metavar="PATH",
        help="Path to an alternative template .md file for this blast.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    # Dry-run is the default; --send is required for real sends.
    live = args.send and not args.dry_run

    # --- Resolve commentary ---
    commentary = resolve_commentary(args.commentary)

    # --- Load template ---
    template_path = Path(args.template_override) if args.template_override else DEFAULT_TEMPLATE
    if not template_path.exists():
        sys.exit(f"ERROR: Template not found: {template_path}")
    subject_tmpl, body_tmpl = load_template(template_path)

    # --- Load recipients ---
    recipients = load_recipients(limit=args.limit, category=args.category)
    if not recipients:
        cat_hint = f" with category '{args.category}'" if args.category and args.category != "all" else ""
        sys.exit(
            f"ERROR: No active recipients found{cat_hint} in business/recipients/recipients.yaml.\n"
            f"Flip 'active: true' for the recipients you want to reach, or adjust --category."
        )

    # --- Build messages ---
    messages: list[tuple[Recipient, str, str]] = []
    for r in recipients:
        variables = build_variables(r, commentary)
        subject = render(subject_tmpl, variables)
        body = render(body_tmpl, variables)
        messages.append((r, subject, body))

    # --- Dry-run mode ---
    if not live:
        cat_label = f"  Category:   {args.category}" if args.category else ""
        print(f"[DRY RUN] Commentary: {commentary.slug}")
        print(f"          Title:      {commentary.title}")
        print(f"          URL:        {commentary.public_url}")
        print(f"          Recipients: {len(messages)}")
        if cat_label:
            print(cat_label)
        print()
        for recipient, subject, body in messages:
            print("=" * 72)
            print(f"  TO:       {recipient.name} <{recipient.email}>")
            print(f"  CATEGORY: {recipient.category}")
            print(f"  OUTLET:   {recipient.outlet or '—'}")
            print(f"  SUBJECT:  {subject}")
            print()
            print(body)
            print()
        print("=" * 72)
        print(f"[DRY RUN] {len(messages)} message(s) rendered. Add --send to fire.")

        # Log dry-run entries so history is preserved.
        now = datetime.now(timezone.utc).isoformat()
        for recipient, subject, body in messages:
            _append_log_row({
                "sent_at_utc": now,
                "slug": commentary.slug,
                "recipient_email": recipient.email,
                "recipient_name": recipient.name,
                "outlet": recipient.outlet or "",
                "subject": subject,
                "smtp_response": "",
                "status": "dry_run",
            })
        return

    # --- Live send path ---

    # Load SMTP credentials.
    smtp_username, smtp_password = load_smtp_credentials()

    # The From address must be the authenticated username.
    from_address = smtp_username

    # Daily cap check.
    sends_today = check_daily_cap(len(messages))

    # Confirmation gate.
    cap_after = sends_today + len(messages)
    print()
    print(f"  Commentary : {commentary.title}")
    print(f"  From       : {from_address}")
    print(f"  Recipients : {len(messages)}")
    print(f"  Daily cap  : {cap_after}/{MIGADU_DAILY_CAP} after this batch")
    print()
    for recipient, subject, _ in messages:
        outlet = f" ({recipient.outlet})" if recipient.outlet else ""
        print(f"    {recipient.name} <{recipient.email}>{outlet}")
    print()
    try:
        confirm = input("Continue? [y/N] ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        print("\nAborted.")
        return

    if confirm != "y":
        print("Aborted.")
        return

    # Send loop.
    sent = 0
    failed = 0
    now_iso = datetime.now(timezone.utc).isoformat()

    for recipient, subject, body in messages:
        print(f"  Sending to {recipient.email} ... ", end="", flush=True)
        try:
            smtp_response = send_one(
                recipient=recipient,
                commentary=commentary,
                subject=subject,
                body=body,
                from_address=from_address,
                smtp_username=smtp_username,
                smtp_password=smtp_password,
            )
            print("OK")
            sent += 1
            _append_log_row({
                "sent_at_utc": now_iso,
                "slug": commentary.slug,
                "recipient_email": recipient.email,
                "recipient_name": recipient.name,
                "outlet": recipient.outlet or "",
                "subject": subject,
                "smtp_response": smtp_response,
                "status": "sent",
            })
        except Exception as exc:
            print(f"FAILED: {exc}")
            failed += 1
            _append_log_row({
                "sent_at_utc": now_iso,
                "slug": commentary.slug,
                "recipient_email": recipient.email,
                "recipient_name": recipient.name,
                "outlet": recipient.outlet or "",
                "subject": subject,
                "smtp_response": str(exc),
                "status": "failed",
            })

    print()
    print(f"Done. Sent: {sent}  Failed: {failed}")
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
