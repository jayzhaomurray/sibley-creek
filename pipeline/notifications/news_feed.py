"""News-feed update detector for Sibley Creek Phase 1 monitoring.

Diffs the current news_feed_cache.json against the last git-committed version.
If new items appear, fires one batched notification per refresh cycle (not per
item). Dedupe key is bounded by the refresh timestamp, so the same set of new
items does not fire twice if the pipeline re-runs before the commit lands.

Cache location: data/derived/news_feed_cache.json
Format: {"generatedAt": "<ISO>", "items": [...]}
Each item has: title, link, pubDate, source, reporter (optional)
"""

from __future__ import annotations

import json
import logging
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from pipeline.notifications.send import send_notification

logger = logging.getLogger("pipeline.notifications.news_feed")

ROOT = Path(__file__).resolve().parents[2]
NEWS_CACHE_PATH = ROOT / "data" / "derived" / "news_feed_cache.json"

_BODY_TEMPLATE = """\
WHAT HAPPENED
{count} new story/stories appeared in the On Our Radar feed during this
refresh cycle.

WHAT VISITORS SEE
The /research/ or splash news feed now includes these new items. They are
live on the site after this build completes.

WHAT TO DO
Nothing immediate. Spot-check that no clearly off-topic story slipped
through the source filters.

DETAILS
new_item_count: {count}
refresh_timestamp: {refresh_ts}

New items:
{item_lines}
"""


def _git_show_cache() -> Optional[dict]:
    """Return the last-committed news_feed_cache.json as a dict, or None."""
    rel_path = "data/derived/news_feed_cache.json"
    try:
        result = subprocess.run(
            ["git", "show", f"HEAD:{rel_path}"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode != 0:
            return None
        return json.loads(result.stdout)
    except (subprocess.SubprocessError, json.JSONDecodeError, OSError):
        return None


def _read_current_cache() -> Optional[dict]:
    if not NEWS_CACHE_PATH.exists():
        return None
    try:
        return json.loads(NEWS_CACHE_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _item_links(data: dict) -> set[str]:
    """Return the set of item links (deduplicated by URL) from a cache dict."""
    items = data.get("items", []) if isinstance(data, dict) else []
    return {item.get("link", "") for item in items if item.get("link")}


def _format_item(item: dict) -> str:
    title = item.get("title", "(no title)")
    source = item.get("source", "")
    reporter = item.get("reporter", "")
    pub = item.get("pubDate", "")
    byline = f" by {reporter}" if reporter else ""
    date_str = ""
    if pub:
        try:
            # pubDate may be RFC-2822; try to parse it
            from email.utils import parsedate_to_datetime
            dt = parsedate_to_datetime(pub)
            date_str = f" ({dt.strftime('%Y-%m-%d')})"
        except Exception:  # noqa: BLE001
            date_str = f" ({pub[:16]})"
    return f"  [{source}]{byline}{date_str}: {title}"


def check_and_notify_news_feed(refresh_ts: str) -> int:
    """Check news_feed_cache.json for new items vs last commit; notify if found.

    Args:
        refresh_ts: ISO timestamp of this pipeline refresh.

    Returns:
        1 if a notification was fired, 0 otherwise.
    """
    current = _read_current_cache()
    if current is None:
        logger.debug("news_feed check: cache file not found; skipping")
        return 0

    prior = _git_show_cache()
    if prior is None:
        # First appearance in git -- no baseline.
        logger.debug("news_feed check: no prior commit; skipping")
        return 0

    current_links = _item_links(current)
    prior_links = _item_links(prior)
    new_links = current_links - prior_links

    if not new_links:
        return 0

    # Find the new item dicts
    all_items = current.get("items", [])
    new_items = [it for it in all_items if it.get("link", "") in new_links]

    # Dedupe key: the refresh timestamp bucket (floor to minute)
    ts_bucket = refresh_ts[:16]  # e.g. "2026-05-28T14:32"
    dedupe_key = f"news_feed:{ts_bucket}"

    item_lines = "\n".join(_format_item(it) for it in new_items[:20])
    if len(new_items) > 20:
        item_lines += f"\n  ... and {len(new_items) - 20} more"

    body = _BODY_TEMPLATE.format(
        count=len(new_items),
        refresh_ts=refresh_ts,
        item_lines=item_lines,
    )

    subject = f"{len(new_items)} new story/stories on the radar feed"

    try:
        sent = send_notification(
            event_type="news_feed_update",
            severity="fyi",
            subject=subject,
            body=body,
            dedupe_key=dedupe_key,
            details={
                "new_item_count": len(new_items),
                "new_links": list(new_links)[:20],
                "refresh_ts": refresh_ts,
            },
        )
        if sent:
            logger.info(
                "news_feed notification fired: %d new items at %s",
                len(new_items), refresh_ts,
            )
            return 1
    except Exception as exc:  # noqa: BLE001
        logger.error("news_feed notification failed: %s", exc)

    return 0
