"""New-vintage detector for Sibley Creek panel data.

Compares freshly-written panel_data/<section>.json files against the last
git-committed versions. When a macro-classified series advances its asOfISO,
fires one notification per affected section (batched if multiple panels
advanced in the same refresh).

Series classification rule
---------------------------
A series slot is classified 'macro' if its source falls in:
    StatCan, Bank of Canada (non-daily Valet), CMHC, IMF, PBO, DoF, CREA,
    Alberta Economic Dashboard, CBA arrears, CPI basket data.

A series slot is classified 'financial' (excluded from vintage notifications) if:
    - It comes from Yahoo Finance (yfinance)
    - It comes from FRED US-comparator series
    - It is a BoC Valet DAILY-cadence feed (yields, FX, CORRA, BCPI)

Rule implementation: panel_data sections are used as the classification proxy.
The 'markets' and 'financial' sections contain almost exclusively financial
series; all other sections (inflation, labour, output, housing, trade,
monetary, fiscal) are macro. This avoids maintaining a per-series allowlist
at the cost of slightly over-notifying if a financial comparator lands in a
non-financial section panel -- which is acceptable (the notification is
harmless, just slightly noisy for a known-edge-case).

Formally: any section NOT in FINANCIAL_SECTIONS triggers vintage notifications.

If you add a new section that is predominantly financial, add it to
FINANCIAL_SECTIONS below.
"""

from __future__ import annotations

import json
import logging
import subprocess
from pathlib import Path
from typing import Optional

from pipeline.notifications.send import send_notification

logger = logging.getLogger("pipeline.notifications.vintage")

ROOT = Path(__file__).resolve().parents[2]
PANEL_DATA_DIR = ROOT / "data" / "site" / "panel_data"

# Sections whose data is predominantly financial (daily, market-price series).
# Vintage notifications are suppressed for these.
FINANCIAL_SECTIONS: frozenset[str] = frozenset({"markets", "financial"})

_BODY_TEMPLATE = """\
WHAT HAPPENED
New macro data landed on the /{section}/ section. The following panel(s)
advanced their data vintage during this refresh:

{series_lines}

WHAT VISITORS SEE
The /{section}/ section now reflects the updated data. Charts and blurbs
on that page have already been rebuilt with the new numbers.

WHAT TO DO
Review the /{section}/ page to confirm charts render correctly. Check
whether any blurb copy has drifted from the new numbers (Phase 2 will
automate this; for now it is a manual spot-check).

DETAILS
section: {section}
updated_panels: {panel_count}
refresh_timestamp: {refresh_ts}
page: https://sibleycreek.ca/{section}/
"""


def _git_show_panel(section: str) -> Optional[dict]:
    """Return the last-committed panel_data/<section>.json as a dict, or None."""
    rel_path = f"data/site/panel_data/{section}.json"
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


def _read_current_panel(section: str) -> Optional[dict]:
    path = PANEL_DATA_DIR / f"{section}.json"
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _extract_slots(panel_data: dict) -> dict[str, str]:
    """Extract {panel_id:slot_key -> asOfISO} from a panel_data dict.

    Traverses panels -> each panel's primary/secondary/tertiary/extras slots.
    Returns a flat dict keyed by "<panel_id>:<slot>" -> asOfISO string.
    """
    slots: dict[str, str] = {}
    panels = panel_data.get("panels", {})
    for panel_id, panel in panels.items():
        if not isinstance(panel, dict):
            continue
        for slot_name in ("primary", "secondary", "tertiary"):
            slot = panel.get(slot_name)
            if isinstance(slot, dict):
                as_of = slot.get("asOfISO")
                if as_of:
                    slots[f"{panel_id}:{slot_name}"] = as_of
        extras = panel.get("extras")
        if isinstance(extras, list):
            for i, extra in enumerate(extras):
                if isinstance(extra, dict):
                    as_of = extra.get("asOfISO")
                    if as_of:
                        slots[f"{panel_id}:extra_{i}"] = as_of
    return slots


def check_and_notify_new_vintages(refresh_ts: str) -> int:
    """Check all macro section panel files for asOfISO advances; notify per section.

    Args:
        refresh_ts: ISO timestamp of this pipeline refresh (used in notification body).

    Returns:
        Number of notifications fired.
    """
    if not PANEL_DATA_DIR.exists():
        logger.warning("panel_data dir not found: %s", PANEL_DATA_DIR)
        return 0

    fired = 0

    for json_path in sorted(PANEL_DATA_DIR.glob("*.json")):
        section = json_path.stem
        if section in FINANCIAL_SECTIONS:
            continue

        current = _read_current_panel(section)
        if current is None:
            continue

        prior = _git_show_panel(section)
        if prior is None:
            # First time this file exists in git -- no baseline to compare.
            # Do not fire on first appearance to avoid a flood on initial deploy.
            logger.debug("vintage check: no prior commit for %s; skipping", section)
            continue

        current_slots = _extract_slots(current)
        prior_slots = _extract_slots(prior)

        advanced: list[tuple[str, str, str]] = []
        for slot_key, new_as_of in current_slots.items():
            old_as_of = prior_slots.get(slot_key)
            if old_as_of and new_as_of > old_as_of:
                advanced.append((slot_key, old_as_of, new_as_of))

        if not advanced:
            continue

        # Find a representative new asOfISO for the dedupe key
        max_new_as_of = max(a[2] for a in advanced)
        dedupe_key = f"new_vintage:{section}:{max_new_as_of}"

        # Format series lines for body
        series_lines = "\n".join(
            f"  {slot}: {old} -> {new}"
            for slot, old, new in advanced
        )

        # Derive a human label for the subject (e.g. April 2026 from 2026-04-01)
        try:
            from datetime import datetime
            dt = datetime.fromisoformat(max_new_as_of.split("T")[0])
            period_label = dt.strftime("%B %Y")
        except Exception:  # noqa: BLE001
            period_label = max_new_as_of[:7]

        subject = f"New {section} data is live ({period_label})"
        body = _BODY_TEMPLATE.format(
            section=section,
            series_lines=series_lines,
            panel_count=len(advanced),
            refresh_ts=refresh_ts,
        )

        try:
            sent = send_notification(
                event_type="new_vintage",
                severity="review",
                subject=subject,
                body=body,
                dedupe_key=dedupe_key,
                details={
                    "section": section,
                    "advanced_slots": [
                        {"slot": s, "from": o, "to": n}
                        for s, o, n in advanced
                    ],
                    "refresh_ts": refresh_ts,
                },
            )
            if sent:
                fired += 1
                logger.info(
                    "vintage notification fired: section=%s panels=%d max_asOf=%s",
                    section, len(advanced), max_new_as_of,
                )
        except Exception as exc:  # noqa: BLE001
            logger.error("vintage notification failed for %s: %s", section, exc)

    return fired
