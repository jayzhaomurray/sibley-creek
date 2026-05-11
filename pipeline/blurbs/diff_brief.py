"""Diff-aware writer brief module.

Given two vintages of the pipeline payload (`data/site/sections.json` plus
`data/site/panel_data/<section>.json`), compute a structured per-indicator
diff and render a Markdown "what changed" block the writer can paste-grok
at the top of their brief.

The writer agent still has to verify every cue before publishing -- the
"significance" lines this module emits are HINTS, not assertions.

Design notes
------------
* Pure-Python, deterministic, no LLM calls.
* Operates on parsed snapshot dicts. Snapshots are stored under
  ``data/site/_snapshots/<timestamp>.json`` (last-12 rotation) so a
  build can compare its newly-written payload against the prior vintage.
* The snapshot format is intentionally identical to the on-disk shape
  (`{"sections": {...}, "panels": {<section>: {<panel>: ...}}}`) so the
  same code reads the live files and the snapshot rotation.
* The "spark" arrays on `sections.json` prints give us last-N history
  per indicator without having to crack open the panel files. We use
  them for the record-high / record-low cues. Panel data is consulted
  only when needed for richer derivations (cycle-low etc.).

Public surface
--------------
- ``IndicatorDiff``     dataclass: per-indicator prior vs new
- ``ReleaseDiff``       dataclass: section-level wrapper
- ``compute_release_diff(section_slug, prior, current) -> ReleaseDiff``
- ``format_brief_for_writer(diff) -> str``
- ``snapshot_current_payload(repo_root) -> Path``
- ``load_latest_prior_snapshot(repo_root) -> dict | None``

The snapshot helpers exist so the build orchestrator can call them at
the top of each release (snapshot BEFORE the new data lands) and the
blurb orchestrator can load the prior vintage (now stored on disk) and
diff against the live files.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class IndicatorDiff:
    """Prior-vs-new diff for one print/indicator.

    Fields:
      key:           stable indicator key (e.g. ``"cpi-yoy"``).
      indicator:     human label (e.g. ``"Headline CPI Y/Y"``).
      prior_value:   numeric prior value (None if absent in prior).
      new_value:     numeric new value (None if absent in current).
      delta:         absolute change (new - prior); None if either side
                     missing.
      pct_change:    percent change vs prior magnitude (None for
                     near-zero priors or when sign-flip makes pct
                     misleading -- caller treats absolute delta as the
                     truth in that case).
      direction:     one of ``"up"``, ``"down"``, ``"flat"`` (or ``None``
                     if either side missing).
      is_record_high_in_window:
                     True if the new value is the max over the last-N
                     window in the spark history.
      is_record_low_in_window:
                     mirror for min.
      window_n:      length of the comparison window we computed records
                     against (so the cue can read "highest in 24 months").
      first_sign_flip:
                     True if prior was >= 0 and new is < 0 (or vice
                     versa) within the spark window.
      as_of:         ISO date of the new print.
      prior_as_of:   ISO date of the prior snapshot's value (best-effort,
                     may be None).
      unit_hint:     "%" / "pp" / "bp" / "C$bn" / None, derived from the
                     section's display string when possible. Only used
                     to format the cue lines.
      significance:  one-line cue in publication voice ("First sub-zero
                     reading in 24 months", etc.). Always present; if
                     nothing notable was found we emit "Within recent
                     range; no record breached." so the writer knows
                     we looked.
    """

    key: str
    indicator: str
    prior_value: Optional[float]
    new_value: Optional[float]
    delta: Optional[float]
    pct_change: Optional[float]
    direction: Optional[str]
    is_record_high_in_window: bool
    is_record_low_in_window: bool
    window_n: int
    first_sign_flip: bool
    as_of: Optional[str]
    prior_as_of: Optional[str]
    unit_hint: Optional[str]
    significance: str


@dataclass(frozen=True)
class ReleaseDiff:
    """Section-level diff payload.

    ``section_slug`` is the editorial section (e.g. ``"inflation"``).
    ``headline_as_of`` is the ISO date the writer should treat as the
    release period (the most recent ``asOfISO`` across the section's
    prints). ``indicators`` is the per-print list in section-stable
    order.
    """

    section_slug: str
    headline_as_of: Optional[str]
    indicators: list[IndicatorDiff] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Core diff logic
# ---------------------------------------------------------------------------


def _as_float(x) -> Optional[float]:
    """Coerce to float; return None for None/non-numeric/NaN."""
    if x is None:
        return None
    try:
        v = float(x)
    except (TypeError, ValueError):
        return None
    if math.isnan(v) or math.isinf(v):
        return None
    return v


def _unit_hint_from_value_string(value_str: Optional[str]) -> Optional[str]:
    """Best-effort unit-hint extraction from the display string."""
    if not value_str:
        return None
    s = value_str.strip().lower()
    if s.endswith("%") or "%" in s:
        return "%"
    if "bp" in s or "basis" in s:
        return "bp"
    if "pp" in s:
        return "pp"
    if "c$" in s or "cad" in s:
        return "C$"
    return None


def _delta_direction(delta: Optional[float]) -> Optional[str]:
    if delta is None:
        return None
    if abs(delta) < 1e-9:
        return "flat"
    return "up" if delta > 0 else "down"


def _section_from_snapshot(snapshot: dict, section_slug: str) -> Optional[dict]:
    """Pull one section's payload from a snapshot.

    Accepts either:
      - the raw ``sections.json`` shape (``{"sections": {slug: {...}}}``)
      - a snapshot wrapper (``{"sections_file": {"sections": {...}}}``)
      - a flat section dict already
    """
    if not isinstance(snapshot, dict):
        return None
    if "sections" in snapshot and isinstance(snapshot["sections"], dict):
        return snapshot["sections"].get(section_slug)
    if "sections_file" in snapshot:
        return _section_from_snapshot(snapshot["sections_file"], section_slug)
    if snapshot.get("slug") == section_slug:
        return snapshot
    return None


def _prints_by_key(section_payload: Optional[dict]) -> dict[str, dict]:
    if not section_payload:
        return {}
    prints = section_payload.get("prints") or []
    return {p.get("key"): p for p in prints if p.get("key")}


def _check_records(new_value: float, spark: list, window_n: int) -> tuple[bool, bool]:
    """Return (is_record_high, is_record_low) over the last window_n
    spark values, treating the last element of ``spark`` as the new
    print (we exclude it so we're comparing against history)."""
    if not spark:
        return (False, False)
    history = [_as_float(v) for v in spark[:-1]][-window_n:]
    history = [h for h in history if h is not None]
    if not history:
        return (False, False)
    # Strict comparison: a new record requires beating the prior max/min,
    # not just tying it. Ties yield False on both ends.
    is_high = new_value > max(history)
    is_low = new_value < min(history)
    return (is_high, is_low)


def _first_sign_flip(prior: Optional[float], new: Optional[float], spark: list) -> bool:
    if prior is None or new is None:
        return False
    if (prior >= 0) == (new >= 0):
        return False
    history = [_as_float(v) for v in (spark or [])[:-1]]
    history = [h for h in history if h is not None]
    if not history:
        return True
    # "First" in window means: prior to this print, the series has not
    # crossed zero in the same direction. Check whether any historical
    # value was on the *new* side of zero.
    if new < 0:
        return all(h >= 0 for h in history)
    return all(h <= 0 for h in history)


def _format_value(v: Optional[float], unit_hint: Optional[str]) -> str:
    if v is None:
        return "n/a"
    # ints stay int-ish, floats get 2dp
    if abs(v) >= 1000:
        s = f"{v:,.1f}"
    elif abs(v) >= 10:
        s = f"{v:.2f}"
    else:
        s = f"{v:.2f}"
    # Strip trailing zeros and the dot they leave behind for tidy display
    if "." in s:
        s = s.rstrip("0").rstrip(".") or "0"
    if unit_hint == "%":
        return f"{s}%"
    if unit_hint == "pp":
        return f"{s}pp"
    if unit_hint == "bp":
        return f"{s}bp"
    if unit_hint == "C$":
        return f"C${s}"
    return s


def _format_delta(delta: Optional[float], unit_hint: Optional[str]) -> str:
    if delta is None:
        return "n/a"
    sign = "+" if delta > 0 else ""
    # For % indicators a delta is expressed in percentage points
    delta_unit = "pp" if unit_hint == "%" else (unit_hint or "")
    if abs(delta) >= 10:
        s = f"{sign}{delta:.2f}"
    else:
        s = f"{sign}{delta:.2f}"
    if "." in s:
        head, tail = s.split(".")
        tail = tail.rstrip("0")
        s = head if not tail else f"{head}.{tail}"
    return f"{s}{delta_unit}" if delta_unit else s


def _derive_significance(
    *,
    prior_value: Optional[float],
    new_value: Optional[float],
    delta: Optional[float],
    direction: Optional[str],
    is_record_high: bool,
    is_record_low: bool,
    window_n: int,
    first_sign_flip: bool,
    unit_hint: Optional[str],
    indicator: str,
) -> str:
    """One-line significance cue. Always returns a non-empty string."""
    if prior_value is None and new_value is None:
        return "No prior or new value -- cannot compute significance."
    if prior_value is None:
        return f"New series; first print at {_format_value(new_value, unit_hint)}."
    if new_value is None:
        return "New vintage missing this indicator -- check pipeline."
    if direction == "flat":
        return f"Unchanged from prior at {_format_value(new_value, unit_hint)}."

    # Sign-flip dominates if true (first sub-zero / first positive)
    if first_sign_flip:
        side = "sub-zero" if new_value < 0 else "above-zero"
        return (
            f"First {side} reading in last {window_n} periods "
            f"({_format_value(new_value, unit_hint)})."
        )

    if is_record_high:
        return (
            f"Highest reading in last {window_n} periods "
            f"({_format_value(new_value, unit_hint)}; "
            f"{_format_delta(delta, unit_hint)} vs prior)."
        )
    if is_record_low:
        return (
            f"Lowest reading in last {window_n} periods "
            f"({_format_value(new_value, unit_hint)}; "
            f"{_format_delta(delta, unit_hint)} vs prior)."
        )

    # Magnitude framing fall-through
    magnitude = abs(delta) if delta is not None else 0.0
    # Threshold heuristic: for % indicators, 0.3pp is meaningful;
    # for non-% indicators we just label by direction + delta.
    if unit_hint == "%" and magnitude >= 0.3:
        verb = "acceleration" if direction == "up" else "deceleration"
        return (
            f"{_format_delta(delta, unit_hint)} {verb} vs prior; "
            f"within recent range."
        )
    if unit_hint == "%" and magnitude < 0.1:
        return (
            f"Small {direction}-tick ({_format_delta(delta, unit_hint)}); "
            f"effectively flat."
        )
    return (
        f"Moved {direction} by {_format_delta(delta, unit_hint)}; "
        f"within recent range."
    )


def compute_release_diff(
    section_slug: str,
    prior_snapshot: dict,
    current_snapshot: dict,
    *,
    window_n: int = 24,
) -> ReleaseDiff:
    """Compute the per-indicator diff for one section.

    Args:
      section_slug: editorial section slug (e.g. ``"inflation"``).
      prior_snapshot: parsed prior vintage. Can be the full sections.json
        payload, or a snapshot-wrapper dict.
      current_snapshot: parsed current vintage. Same flexibility.
      window_n: how many trailing periods the spark is treated as for
        record-high / record-low checks. Default 24 (= 2y of monthly).

    Returns:
      ReleaseDiff. Indicators with no prior get ``prior_value=None`` and
      a significance line that flags it as a new series.

    The function is total: missing sections or missing prints surface as
    empty / per-indicator None fields rather than exceptions, so the
    caller can render a brief even on a partially-failed snapshot.
    """
    prior_section = _section_from_snapshot(prior_snapshot or {}, section_slug)
    curr_section = _section_from_snapshot(current_snapshot or {}, section_slug)

    if curr_section is None:
        return ReleaseDiff(section_slug=section_slug, headline_as_of=None, indicators=[])

    prior_prints = _prints_by_key(prior_section)
    curr_prints_list = curr_section.get("prints") or []

    indicators: list[IndicatorDiff] = []
    most_recent_as_of: Optional[str] = None

    for p in curr_prints_list:
        key = p.get("key")
        if not key:
            continue
        new_value = _as_float(p.get("valueRaw"))
        prior_print = prior_prints.get(key) or {}
        # Prefer the prior snapshot's `valueRaw`; if absent, fall back
        # to the current print's `priorRaw` (which the pipeline already
        # computes as the second-most-recent observation). This makes
        # the diff useful even on the very first snapshotted build.
        prior_value = _as_float(prior_print.get("valueRaw"))
        if prior_value is None:
            prior_value = _as_float(p.get("priorRaw"))

        if prior_value is not None and new_value is not None:
            delta = new_value - prior_value
            if abs(prior_value) > 1e-9:
                pct_change = (delta / abs(prior_value)) * 100.0
            else:
                pct_change = None
        else:
            delta = None
            pct_change = None

        direction = _delta_direction(delta)
        unit_hint = _unit_hint_from_value_string(p.get("value"))
        spark = p.get("spark") or []

        if new_value is not None:
            is_high, is_low = _check_records(new_value, spark, window_n)
        else:
            is_high = is_low = False

        sign_flip = _first_sign_flip(prior_value, new_value, spark)

        as_of = p.get("asOfISO")
        prior_as_of = prior_print.get("asOfISO")

        if as_of and (most_recent_as_of is None or as_of > most_recent_as_of):
            most_recent_as_of = as_of

        significance = _derive_significance(
            prior_value=prior_value,
            new_value=new_value,
            delta=delta,
            direction=direction,
            is_record_high=is_high,
            is_record_low=is_low,
            window_n=window_n,
            first_sign_flip=sign_flip,
            unit_hint=unit_hint,
            indicator=p.get("indicator") or key,
        )

        indicators.append(IndicatorDiff(
            key=key,
            indicator=p.get("indicator") or key,
            prior_value=prior_value,
            new_value=new_value,
            delta=delta,
            pct_change=pct_change,
            direction=direction,
            is_record_high_in_window=is_high,
            is_record_low_in_window=is_low,
            window_n=window_n,
            first_sign_flip=sign_flip,
            as_of=as_of,
            prior_as_of=prior_as_of,
            unit_hint=unit_hint,
            significance=significance,
        ))

    return ReleaseDiff(
        section_slug=section_slug,
        headline_as_of=most_recent_as_of,
        indicators=indicators,
    )


# ---------------------------------------------------------------------------
# Markdown rendering
# ---------------------------------------------------------------------------


def format_brief_for_writer(diff: ReleaseDiff) -> str:
    """Render the diff as a Markdown block the writer dispatch prepends
    to the writer's brief.

    The block is wrapped in a header line and a trailing "These are
    HINTS, not assertions" disclaimer so the writer treats them as
    cues to verify rather than facts to publish.
    """
    section_label = diff.section_slug.capitalize() if diff.section_slug != "_global" else "Global"
    lines: list[str] = []
    lines.append(f"## Diff brief: {section_label}")
    lines.append("")
    if diff.headline_as_of:
        lines.append(f"- Headline release date (most recent print): **{diff.headline_as_of}**")
    else:
        lines.append("- Headline release date: (unknown -- check pipeline)")
    lines.append(f"- Indicators in section: {len(diff.indicators)}")
    lines.append("")

    if not diff.indicators:
        lines.append(
            "_No indicators found in the current snapshot for this section. "
            "The pipeline may have failed to write this section's payload._"
        )
        return "\n".join(lines) + "\n"

    lines.append("### Per-indicator diff")
    lines.append("")
    for ind in diff.indicators:
        prior_str = _format_value(ind.prior_value, ind.unit_hint)
        new_str = _format_value(ind.new_value, ind.unit_hint)
        delta_str = _format_delta(ind.delta, ind.unit_hint)
        pct_suffix = ""
        if ind.pct_change is not None and ind.unit_hint != "%" and abs(ind.pct_change) >= 0.1:
            pct_suffix = f" ({ind.pct_change:+.1f}%)"
        lines.append(f"- **{ind.indicator}** (`{ind.key}`)")
        lines.append(
            f"  - was {prior_str} -> now {new_str} "
            f"(delta = {delta_str}{pct_suffix})"
        )
        lines.append(f"  - significance: {ind.significance}")
        lines.append("")

    lines.append("---")
    lines.append(
        "_These cues are HINTS for the writer derived mechanically from "
        "the diff. Verify against the verified claim-cards before "
        "publishing any framing that leans on a cue. Override any cue "
        "that conflicts with the cards and note the override in the "
        "writer's report._"
    )
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Snapshot rotation (option (a) from the brief: append-only, last-12)
# ---------------------------------------------------------------------------


SNAPSHOT_DIR_REL = Path("data") / "site" / "_snapshots"
MAX_SNAPSHOTS = 12


def _snapshot_dir(repo_root: Path) -> Path:
    return repo_root / SNAPSHOT_DIR_REL


def snapshot_current_payload(repo_root: Path, *, timestamp: Optional[str] = None) -> Path:
    """Persist the current ``sections.json`` plus every ``panel_data/*.json``
    as one combined snapshot under ``data/site/_snapshots/<ts>.json``.

    Returns the path written. Caps the directory at MAX_SNAPSHOTS files
    (oldest pruned). Intended to run at the START of a pipeline build,
    BEFORE the new data lands, so the most recent snapshot represents
    the prior vintage.

    The snapshot wraps the on-disk files in a single JSON object:

      {
        "snapshot_at": "<ISO ts>",
        "sections_file": <full sections.json>,
        "panels": {
          "<section>": <full panel_data/<section>.json>,
          ...
        }
      }

    Missing files are skipped silently (snapshot still written; caller
    sees a partial vintage rather than a crash).
    """
    sections_path = repo_root / "data" / "site" / "sections.json"
    panel_dir = repo_root / "data" / "site" / "panel_data"

    payload: dict = {
        "snapshot_at": timestamp or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ"),
        "sections_file": None,
        "panels": {},
    }

    if sections_path.exists():
        try:
            payload["sections_file"] = json.loads(sections_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            payload["sections_file"] = None

    if panel_dir.exists():
        for pf in sorted(panel_dir.glob("*.json")):
            try:
                payload["panels"][pf.stem] = json.loads(pf.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue

    snap_dir = _snapshot_dir(repo_root)
    snap_dir.mkdir(parents=True, exist_ok=True)
    out_path = snap_dir / f"{payload['snapshot_at']}.json"
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    _rotate_snapshots(snap_dir, MAX_SNAPSHOTS)
    return out_path


def _rotate_snapshots(snap_dir: Path, keep: int) -> None:
    files = sorted(snap_dir.glob("*.json"))
    if len(files) <= keep:
        return
    for f in files[: len(files) - keep]:
        try:
            f.unlink()
        except OSError:
            pass


def load_latest_prior_snapshot(repo_root: Path) -> Optional[dict]:
    """Return the most recent snapshot (already on disk) or None.

    "Most recent" is determined by filename sort (we use an ISO-shaped
    timestamp in the filename, so lexicographic == chronological).
    """
    snap_dir = _snapshot_dir(repo_root)
    if not snap_dir.exists():
        return None
    files = sorted(snap_dir.glob("*.json"))
    if not files:
        return None
    try:
        return json.loads(files[-1].read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def load_current_payload(repo_root: Path) -> dict:
    """Read the live ``data/site/sections.json`` (plus panels) into the
    same wrapper shape used by snapshots, so the diff functions can
    consume either side symmetrically."""
    sections_path = repo_root / "data" / "site" / "sections.json"
    panel_dir = repo_root / "data" / "site" / "panel_data"
    payload: dict = {"snapshot_at": "live", "sections_file": None, "panels": {}}
    if sections_path.exists():
        try:
            payload["sections_file"] = json.loads(sections_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            payload["sections_file"] = None
    if panel_dir.exists():
        for pf in sorted(panel_dir.glob("*.json")):
            try:
                payload["panels"][pf.stem] = json.loads(pf.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
    return payload


def build_writer_diff_brief(repo_root: Path, section_slug: str) -> str:
    """Convenience: load prior snapshot + live payload, compute diff,
    render markdown. Returns an empty-string fallback (with a one-line
    note) if no prior snapshot is on disk yet.
    """
    prior = load_latest_prior_snapshot(repo_root)
    current = load_current_payload(repo_root)
    if prior is None:
        return (
            "## Diff brief\n\n"
            "_No prior snapshot found under `data/site/_snapshots/`. The "
            "diff-aware brief will populate on the next build cycle._\n"
        )
    diff = compute_release_diff(section_slug, prior, current)
    return format_brief_for_writer(diff)
