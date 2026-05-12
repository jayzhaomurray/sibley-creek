"""Drift watcher main entry.

Reads the tracked claims registry, resolves each claim's data source
to a current value, classifies drift, and writes a dated markdown alert
to ``editorial/drift/alerts/<date>.md``.

Run via ``python -m pipeline.drift.watcher``.

The watcher is purely deterministic -- no LLM calls. A drift flag is a
prompt for a human to decide whether the affected pillar needs a
re-review (which is a separate writing task).
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from dataclasses import dataclass
from datetime import date as date_type
from datetime import datetime
from pathlib import Path
from typing import Literal

from pipeline.drift.claims_registry import (
    DEFAULT_REGISTRY_PATH,
    Claim,
    iter_claims_by_pillar,
    load_claims_registry,
    parse_data_source,
)

# Status taxonomy for a drift check.
Status = Literal["clear", "drift_flagged", "data_missing"]

DEFAULT_ALERTS_DIR = Path("editorial/drift/alerts")


@dataclass(frozen=True)
class DriftResult:
    """The outcome of comparing one claim's published value to current data."""

    claim: Claim
    status: Status
    current_value: float | None
    current_as_of: str | None
    delta: float | None
    note: str | None  # populated when status == "data_missing"

    @property
    def abs_delta(self) -> float | None:
        return None if self.delta is None else abs(self.delta)


def _resolve_path(repo_root: Path, rel: str) -> Path:
    """Resolve a data_source relative path against the repo root."""
    return (repo_root / rel).resolve()


def _read_csv_last_row(path: Path) -> tuple[float, str]:
    """Return (value, date) from the last data row of a two-column CSV."""
    with path.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.reader(fh)
        rows = [r for r in reader if r]
    if len(rows) < 2:
        raise ValueError(f"{path}: no data rows")
    header, *data = rows
    if [c.strip().lower() for c in header[:2]] != ["date", "value"]:
        raise ValueError(
            f"{path}: expected header 'date,value', got {header[:2]!r}"
        )
    last = data[-1]
    if len(last) < 2:
        raise ValueError(f"{path}: last row malformed: {last!r}")
    return float(last[1]), last[0]


def _read_json_panel(path: Path, key: str) -> tuple[float, str]:
    """Return (value, date) from the latest point in a panel-data series.

    The panel-data files are written by ``pipeline/io/panel_data.py``;
    structure is ``{"panels": {"panel-N": {"primary"|"secondary"|...: {...series...} or [series, ...]}}}``.
    Each series has ``{"key": ..., "data": [{"date": ..., "value": ...}, ...]}``.
    """
    doc = json.loads(path.read_text(encoding="utf-8"))
    panels = doc.get("panels")
    if not isinstance(panels, dict):
        raise ValueError(f"{path}: missing 'panels' object")

    for panel in panels.values():
        if not isinstance(panel, dict):
            continue
        for slot in ("primary", "secondary", "tertiary", "extras"):
            v = panel.get(slot)
            candidates: list[dict] = []
            if isinstance(v, dict):
                candidates = [v]
            elif isinstance(v, list):
                candidates = [item for item in v if isinstance(item, dict)]
            for series in candidates:
                if series.get("key") != key:
                    continue
                data = series.get("data") or []
                if not data:
                    raise ValueError(
                        f"{path}: series {key!r} has empty data array"
                    )
                last = data[-1]
                return float(last["value"]), str(last["date"])

    raise KeyError(f"{path}: series key {key!r} not found in any panel")


def fetch_current_value(
    claim: Claim, repo_root: Path
) -> tuple[float, str] | None:
    """Resolve ``claim.data_source`` to (current_value, as_of_date).

    Returns ``None`` if the underlying file is missing or malformed (the
    watcher then classifies the claim as ``data_missing`` rather than
    crashing the whole report).
    """
    kind, rel_path, key = parse_data_source(claim.data_source)
    abs_path = _resolve_path(repo_root, rel_path)
    if not abs_path.exists():
        return None
    try:
        if kind == "csv_last_row":
            return _read_csv_last_row(abs_path)
        elif kind == "json_panel":
            assert key is not None
            return _read_json_panel(abs_path, key)
        else:
            return None
    except (ValueError, KeyError, json.JSONDecodeError):
        return None


def check_drift(claim: Claim, repo_root: Path) -> DriftResult:
    """Compare current value to published value; classify."""
    fetched = fetch_current_value(claim, repo_root)
    if fetched is None:
        return DriftResult(
            claim=claim,
            status="data_missing",
            current_value=None,
            current_as_of=None,
            delta=None,
            note=(
                f"could not resolve data_source {claim.data_source!r}; "
                "file missing or malformed"
            ),
        )
    current_value, as_of = fetched
    delta = current_value - claim.published_value
    status: Status = (
        "drift_flagged" if abs(delta) > claim.threshold else "clear"
    )
    return DriftResult(
        claim=claim,
        status=status,
        current_value=current_value,
        current_as_of=as_of,
        delta=delta,
        note=None,
    )


def _format_value(v: float | None, unit: str) -> str:
    if v is None:
        return "n/a"
    if unit in ("%", "pp"):
        return f"{v:.2f}{unit}"
    if unit == "bps":
        return f"{v:.0f} bps"
    if unit == "level":
        return f"{v:.4f}"
    return f"{v:.2f} {unit}"


def _format_delta(d: float | None, unit: str) -> str:
    if d is None:
        return "n/a"
    sign = "+" if d >= 0 else ""
    if unit in ("%", "pp"):
        return f"{sign}{d:.2f} {unit}"
    if unit == "bps":
        return f"{sign}{d:.0f} bps"
    if unit == "level":
        return f"{sign}{d:.4f}"
    return f"{sign}{d:.2f} {unit}"


def render_alert(results: list[DriftResult], run_date: date_type) -> str:
    """Render a markdown alert from a list of drift results."""
    flagged = [r for r in results if r.status == "drift_flagged"]
    missing = [r for r in results if r.status == "data_missing"]
    clear = [r for r in results if r.status == "clear"]

    lines: list[str] = []
    lines.append(f"# Drift watcher report -- {run_date.isoformat()}")
    lines.append("")
    lines.append(
        f"Checked {len(results)} tracked claims across "
        f"{len(iter_claims_by_pillar([r.claim for r in results]))} pillars."
    )
    lines.append("")
    lines.append(
        f"- Clear: {len(clear)}"
    )
    lines.append(
        f"- Drift flagged: {len(flagged)}"
    )
    lines.append(
        f"- Data missing: {len(missing)}"
    )
    lines.append("")

    if flagged:
        lines.append("## Drift flagged")
        lines.append("")
        for r in flagged:
            c = r.claim
            lines.append(f"### {c.qualified_id} -- {c.pillar_title}")
            lines.append("")
            lines.append(f"> {c.text}")
            lines.append("")
            lines.append(
                f"- Published value: {_format_value(c.published_value, c.unit)} "
                f"(as of {c.pillar_published_at})"
            )
            lines.append(
                f"- Current value: {_format_value(r.current_value, c.unit)} "
                f"(as of {r.current_as_of})"
            )
            lines.append(
                f"- Delta: {_format_delta(r.delta, c.unit)}"
                f" (threshold {_format_value(c.threshold, c.unit)})"
            )
            lines.append(
                f"- Recommended action: review pillar **{c.pillar_slug}**;"
                f" cite {c.id} has drifted beyond threshold."
            )
            lines.append("")

    if missing:
        lines.append("## Data missing")
        lines.append("")
        for r in missing:
            c = r.claim
            lines.append(
                f"- **{c.qualified_id}** -- {r.note}"
            )
        lines.append("")

    if not flagged and not missing:
        lines.append("All claims within threshold. No drift detected.")
        lines.append("")

    lines.append("## All claims, by pillar")
    lines.append("")
    grouped = iter_claims_by_pillar([r.claim for r in results])
    by_qid: dict[str, DriftResult] = {r.claim.qualified_id: r for r in results}
    for slug, claims in grouped.items():
        title = claims[0].pillar_title if claims else slug
        lines.append(f"### {slug}")
        lines.append(f"*{title}*  ")
        lines.append(f"Published: {claims[0].pillar_published_at}")
        lines.append("")
        for c in claims:
            r = by_qid[c.qualified_id]
            status_marker = {
                "clear": "OK",
                "drift_flagged": "FLAG",
                "data_missing": "MISS",
            }[r.status]
            lines.append(
                f"- [{status_marker}] **{c.id}**: published "
                f"{_format_value(c.published_value, c.unit)} -> current "
                f"{_format_value(r.current_value, c.unit)} "
                f"(delta {_format_delta(r.delta, c.unit)}; threshold "
                f"{_format_value(c.threshold, c.unit)})"
            )
        lines.append("")

    return "\n".join(lines)


def run_watcher(
    registry_path: Path | str = DEFAULT_REGISTRY_PATH,
    repo_root: Path | str | None = None,
    alerts_dir: Path | str = DEFAULT_ALERTS_DIR,
    run_date: date_type | None = None,
) -> tuple[Path, list[DriftResult]]:
    """Run the watcher end-to-end. Returns (alert_path, results)."""
    if repo_root is None:
        repo_root = Path(__file__).resolve().parents[2]
    repo_root = Path(repo_root)

    registry_path = Path(registry_path)
    if not registry_path.is_absolute():
        registry_path = repo_root / registry_path

    alerts_dir = Path(alerts_dir)
    if not alerts_dir.is_absolute():
        alerts_dir = repo_root / alerts_dir

    if run_date is None:
        run_date = datetime.now().date()

    claims = load_claims_registry(registry_path)
    results = [check_drift(c, repo_root) for c in claims]

    alerts_dir.mkdir(parents=True, exist_ok=True)
    alert_path = alerts_dir / f"{run_date.isoformat()}.md"
    alert_path.write_text(render_alert(results, run_date), encoding="utf-8")
    return alert_path, results


def _summarize_stdout(results: list[DriftResult], alert_path: Path) -> None:
    """Print a one-line-per-status summary to stdout for the operator."""
    flagged = sum(1 for r in results if r.status == "drift_flagged")
    missing = sum(1 for r in results if r.status == "data_missing")
    clear = sum(1 for r in results if r.status == "clear")
    print(f"drift watcher: {len(results)} claims checked")
    print(f"  clear={clear} drift_flagged={flagged} data_missing={missing}")
    print(f"  alert: {alert_path}")
    if flagged:
        print("  FLAGS:")
        for r in results:
            if r.status == "drift_flagged":
                print(
                    f"    {r.claim.qualified_id}: "
                    f"published={r.claim.published_value} "
                    f"current={r.current_value} "
                    f"delta={r.delta}"
                )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m pipeline.drift.watcher",
        description="Compare published deep-dive claims to current data.",
    )
    parser.add_argument(
        "--registry",
        default=str(DEFAULT_REGISTRY_PATH),
        help="path to the claims registry YAML (default: %(default)s)",
    )
    parser.add_argument(
        "--alerts-dir",
        default=str(DEFAULT_ALERTS_DIR),
        help="directory to write the dated alert markdown to",
    )
    args = parser.parse_args(argv)

    alert_path, results = run_watcher(
        registry_path=args.registry,
        alerts_dir=args.alerts_dir,
    )
    _summarize_stdout(results, alert_path)
    # Exit non-zero if any drift flagged, so cron/CI can react.
    return 1 if any(r.status == "drift_flagged" for r in results) else 0


if __name__ == "__main__":
    sys.exit(main())
