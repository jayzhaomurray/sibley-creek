"""Deduplication guard for Sibley Creek notifications.

Consults the ledger to decide whether a given dedupe_key has already fired
within the configured window. Returns False (suppress) if it has.

Default deduplication windows
------------------------------
    failure         4 hours   -- same exception class on same entry point
    new_vintage    24 hours   -- same section + asOfISO
    news_feed_update 1 hour   -- same refresh timestamp bucket

Callers can pass within_hours explicitly to override the default.
"""

from __future__ import annotations

from pipeline.notifications.ledger import recent_events

# Default dedup windows by event type (hours)
DEFAULT_WINDOWS: dict[str, float] = {
    "failure": 4.0,
    "new_vintage": 24.0,
    "news_feed_update": 1.0,
}


def should_send(
    dedupe_key: str | None,
    within_hours: float | None = None,
    event_type: str | None = None,
) -> bool:
    """Return True if this event should fire, False if it should be suppressed.

    Suppression condition: a ledger event with the same dedupe_key exists
    within the deduplication window.

    Args:
        dedupe_key:   The deduplication key for this event. None means always send.
        within_hours: Override the window. If None, resolved from event_type using
                      DEFAULT_WINDOWS (defaults to 1.0 if type unknown).
        event_type:   Used to look up the default window when within_hours is None.
    """
    if dedupe_key is None:
        return True

    if within_hours is None:
        within_hours = DEFAULT_WINDOWS.get(event_type or "", 1.0)

    recent = recent_events(within_hours)
    for ev in recent:
        if ev.get("dedupe_key") == dedupe_key:
            return False  # already fired within window

    return True
