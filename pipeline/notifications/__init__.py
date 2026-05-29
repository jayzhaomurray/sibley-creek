"""Sibley Creek notification substrate (Phase 1).

Phase 1 is pure monitoring: detect failures, new data vintages, and
news-feed updates; write a durable event ledger; send email. No commits,
no review UI, no branch mutations.

Public API
----------
    from pipeline.notifications import send_notification, append_event, should_send

Event types
-----------
    failure         -- unhandled exception in a pipeline entry point
    new_vintage     -- asOfISO advanced on a macro data series
    news_feed_update -- new items in data/derived/news_feed_cache.json

Severity taxonomy (subject-line prefix)
----------------------------------------
    fyi              -> [Sibley Creek Update]
    review           -> [Sibley Creek Review]
    alert            -> [Sibley Creek Alert]
    action_required  -> [Sibley Creek Action Required]

Series classification rule (macro vs financial)
------------------------------------------------
Series from StatCan, BoC, CMHC, IMF, PBO, DoF are classified 'macro'.
Series from yfinance (Yahoo), FRED, or any BoC Valet daily-rate feed
are classified 'financial'. Only macro series trigger new_vintage
notifications. This rule is encoded in pipeline.notifications.vintage
and is findable here for reference.

Silence a type via env var:
    SIBLEY_NOTIFICATIONS_DISABLED_TYPES=failure,new_vintage

Dry-run mode (no actual email sent, writes to a file instead):
    SIBLEY_NOTIFICATIONS_DRY_RUN=1
"""

from pipeline.notifications.send import send_notification
from pipeline.notifications.ledger import append_event, recent_events
from pipeline.notifications.dedupe import should_send

__all__ = [
    "send_notification",
    "append_event",
    "recent_events",
    "should_send",
]
