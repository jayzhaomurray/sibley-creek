"""Durable event ledger for Sibley Creek notification history.

Append-only JSON array at data/derived/notification_events.json.
Each record is an event dict matching the schema below. The ledger
is the authoritative source for deduplication and audit queries.

Record schema
-------------
{
  "id":           "evt_<8-char hex>",
  "timestamp":    "<ISO 8601 UTC>",
  "type":         "failure" | "new_vintage" | "news_feed_update",
  "severity":     "fyi" | "review" | "alert" | "action_required",
  "subject":      "<email subject line without prefix>",
  "body_preview": "<first 200 chars of body>",
  "dedupe_key":   "<string or null>",
  "details":      { ... type-specific ... }
}

File location: data/derived/notification_events.json
Relative to repo root (two parents up from this file).
"""

from __future__ import annotations

import json
import logging
import os
import secrets
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger("pipeline.notifications.ledger")

ROOT = Path(__file__).resolve().parents[2]
LEDGER_PATH = ROOT / "data" / "derived" / "notification_events.json"


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load() -> list[dict]:
    if not LEDGER_PATH.exists():
        return []
    try:
        raw = LEDGER_PATH.read_text(encoding="utf-8").strip()
        if not raw:
            return []
        return json.loads(raw)
    except (OSError, json.JSONDecodeError) as exc:
        logger.warning("ledger read error (treating as empty): %s", exc)
        return []


def _save(events: list[dict]) -> None:
    LEDGER_PATH.parent.mkdir(parents=True, exist_ok=True)
    LEDGER_PATH.write_text(
        json.dumps(events, indent=2, ensure_ascii=True),
        encoding="utf-8",
    )


def _make_id() -> str:
    return "evt_" + secrets.token_hex(4)


def append_event(event_dict: dict[str, Any]) -> dict[str, Any]:
    """Append one event record to the ledger and return it with id + timestamp.

    Caller may omit 'id' and 'timestamp'; they are stamped here.
    'body_preview' is auto-truncated to 200 chars from 'body' if present.
    """
    record: dict[str, Any] = {
        "id": _make_id(),
        "timestamp": _now_iso(),
    }
    record.update(event_dict)
    # Ensure id/timestamp are ours even if caller passed them
    record["id"] = record.get("id") or _make_id()
    record["timestamp"] = record.get("timestamp") or _now_iso()

    # Auto-derive body_preview from body if not supplied
    if "body_preview" not in record and "body" in record:
        record["body_preview"] = str(record["body"])[:200]

    events = _load()
    events.append(record)
    _save(events)
    return record


def recent_events(within_hours: float) -> list[dict]:
    """Return all ledger events whose timestamp falls within the last N hours."""
    cutoff = datetime.now(timezone.utc) - timedelta(hours=within_hours)
    events = _load()
    result = []
    for ev in events:
        try:
            ts = datetime.fromisoformat(ev["timestamp"].replace("Z", "+00:00"))
            if ts >= cutoff:
                result.append(ev)
        except (KeyError, ValueError):
            continue
    return result
