"""Build shadow site data using provisional latest GoC yields.

This command never writes canonical raw CSVs and never writes live site JSON.
It emits:
    data/site_shadow/sections.json
    data/site_shadow/panel_data/*.json
    data/site_shadow/provisional_goc_yields_report.json

Run:
    python -m pipeline.provisional.shadow_goc_yields
"""

from __future__ import annotations

import argparse
import json
import logging
from datetime import date
from pathlib import Path
from typing import Any, Optional

from pipeline.io.panel_data import build_all_panel_data, validate_panel_data_file
from pipeline.io.site_data import build_site_data
from pipeline.provisional.goc_yields import (
    DATA_ROOT,
    DEFAULT_OUTPUT,
    REQUIRED_GOC_YIELDS,
    fetch_trading_economics_curve,
    load_payload,
    overlay_map_from_payload,
    validate_payload,
    write_payload,
)

logger = logging.getLogger("pipeline.provisional.shadow_goc_yields")


def _read_json(path: Path) -> Optional[dict[str, Any]]:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _display_path(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root.parent))
    except ValueError:
        return str(path)


def _find_print(section_payload: Optional[dict[str, Any]], print_key: str) -> Optional[dict[str, Any]]:
    if not section_payload:
        return None
    for item in section_payload.get("prints", []):
        if item.get("key") == print_key:
            return item
    return None


def _slot_entries(panel: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
    entries: list[tuple[str, dict[str, Any]]] = []
    for slot_name in ("primary", "secondary", "tertiary"):
        slot = panel.get(slot_name)
        if slot:
            entries.append((slot_name, slot))
    for idx, slot in enumerate(panel.get("extras", [])):
        if slot:
            entries.append((f"extra[{idx}]", slot))
    return entries


def _compare_sections(live_path: Path, shadow_path: Path) -> list[dict[str, Any]]:
    live = _read_json(live_path)
    shadow = _read_json(shadow_path)
    if not live or not shadow:
        return []

    changes: list[dict[str, Any]] = []
    for section, section_payload in shadow.get("sections", {}).items():
        for item in section_payload.get("prints", []):
            overlays = item.get("provisionalOverlays") or []
            if not overlays:
                continue
            live_item = _find_print(live.get("sections", {}).get(section), item.get("key"))
            changes.append({
                "bundle": "sections",
                "section": section,
                "printKey": item.get("key"),
                "indicator": item.get("indicator"),
                "liveAsOfISO": live_item.get("asOfISO") if live_item else None,
                "shadowAsOfISO": item.get("asOfISO"),
                "liveValueRaw": live_item.get("valueRaw") if live_item else None,
                "shadowValueRaw": item.get("valueRaw"),
                "provisionalOverlays": overlays,
            })
    return changes


def _compare_panel_data(live_dir: Path, shadow_dir: Path) -> list[dict[str, Any]]:
    changes: list[dict[str, Any]] = []
    for shadow_file in sorted(shadow_dir.glob("*.json")):
        section = shadow_file.stem
        shadow = _read_json(shadow_file)
        live = _read_json(live_dir / shadow_file.name)
        if not shadow:
            continue
        live_panels = (live or {}).get("panels", {})
        for panel_id, panel in shadow.get("panels", {}).items():
            live_panel = live_panels.get(panel_id, {})
            live_slots = dict(_slot_entries(live_panel))
            for slot_name, slot in _slot_entries(panel):
                overlay = slot.get("provisionalOverlay")
                if not overlay:
                    continue
                live_slot = live_slots.get(slot_name)
                changes.append({
                    "bundle": "panel_data",
                    "section": section,
                    "panel": panel_id,
                    "slot": slot_name,
                    "key": slot.get("key"),
                    "liveAsOfISO": live_slot.get("asOfISO") if live_slot else None,
                    "shadowAsOfISO": slot.get("asOfISO"),
                    "liveValue": (live_slot.get("data") or [{}])[-1].get("value") if live_slot else None,
                    "shadowValue": (slot.get("data") or [{}])[-1].get("value"),
                    "provisionalOverlay": overlay,
                })
    return changes


def _collect_panel_integrity_violations(panel_dir: Path) -> list[str]:
    violations: list[str] = []
    for path in sorted(panel_dir.glob("*.json")):
        violations.extend(validate_panel_data_file(path))
    return violations


def build_shadow(
    *,
    data_root: Path = DATA_ROOT,
    artifact_path: Path = DEFAULT_OUTPUT,
    out_root: Optional[Path] = None,
    target_date: Optional[date] = None,
    probe_first: bool = False,
) -> Path:
    data_root = Path(data_root)
    artifact_path = Path(artifact_path)
    out_root = Path(out_root) if out_root is not None else data_root / "site_shadow"

    if probe_first:
        payload = fetch_trading_economics_curve()
    else:
        payload = load_payload(artifact_path)
    payload = validate_payload(payload, data_root=data_root, target_date=target_date)
    payload["artifactPath"] = _display_path(artifact_path, data_root)
    write_payload(payload, artifact_path)
    if payload.get("status") != "ok":
        raise RuntimeError(f"provisional GoC payload invalid: {payload.get('violations')}")

    overlays = overlay_map_from_payload(payload)
    out_root.mkdir(parents=True, exist_ok=True)
    sections_path = out_root / "sections.json"
    panel_dir = out_root / "panel_data"

    build_site_data(data_root, out_path=sections_path, series_overlays=overlays)
    build_all_panel_data(data_root, out_dir=panel_dir, series_overlays=overlays, validate=False)
    panel_integrity_violations = _collect_panel_integrity_violations(panel_dir)

    report = {
        "schemaVersion": 1,
        "status": "ok",
        "provisionalArtifact": _display_path(artifact_path, data_root),
        "shadowSections": _display_path(sections_path, data_root),
        "shadowPanelDataDir": _display_path(panel_dir, data_root),
        "overlaySeries": sorted(REQUIRED_GOC_YIELDS),
        "provisional": payload,
        "panelIntegrityViolations": panel_integrity_violations,
        "changes": _compare_sections(data_root / "site" / "sections.json", sections_path)
        + _compare_panel_data(data_root / "site" / "panel_data", panel_dir),
    }
    report_path = out_root / "provisional_goc_yields_report.json"
    report_path.write_text(json.dumps(report, indent=2, sort_keys=False), encoding="utf-8")
    logger.info("wrote provisional GoC shadow report: %s", report_path)
    return report_path


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Build shadow data/site bundle with provisional GoC yields.")
    parser.add_argument("--data-root", type=Path, default=DATA_ROOT)
    parser.add_argument("--artifact", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--out-root", type=Path, default=None)
    parser.add_argument("--target-date", type=lambda s: date.fromisoformat(s), default=None)
    parser.add_argument("--probe-first", action="store_true", help="Fetch provisional GoC yields before shadow build.")
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    try:
        report_path = build_shadow(
            data_root=args.data_root,
            artifact_path=args.artifact,
            out_root=args.out_root,
            target_date=args.target_date,
            probe_first=args.probe_first,
        )
    except Exception as exc:  # noqa: BLE001
        logger.error("shadow build failed: %s: %s", type(exc).__name__, exc)
        return 1
    logger.info("shadow build complete: %s", report_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
