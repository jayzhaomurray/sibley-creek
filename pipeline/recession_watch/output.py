"""Serialize Recession Watch metrics to data/site/panel_data/recession_watch.json.

Output shape (matches the existing panel_data convention in the project):

{
  "section": "recession_watch",
  "generatedAt": "2026-06-02T...",
  "cyclePeakDate": "2026-01-01",
  "currentDurationMonths": 4,
  "chainInfo": {
    "seamDates": [...],
    "calibrationRatios": {...},
    "earliestDate": "1981-01-01",
    "note": "..."
  },
  "metrics": {
    "gdp_depth": {
      "metric": "gdp_depth",
      "unit": "%",
      "description": "...",
      "peak_date": "...",
      "current_reading": -0.001,
      "current_months_since_peak": 4,
      "current": [{"monthsSincePeak": 0, "value": 0.0}, ...],
      "comparators": {
        "1981-82": [{"monthsSincePeak": 0, "value": 0.0}, ...],
        ...
      },
      "envelope_at_current_duration": {"mildest": ..., "severest": ..., "covid": ...}
    },
    "gdp_breadth": { ... },
    "emp_depth": { ... },
    "emp_breadth": { ... }
  },
  "gdp_breadth_fine": {
    "n_sectors": 84,
    "peak_date": "...",
    "current_reading": 5.2,
    "path": [...],
    "note": "..."
  }
}

Audit gate integration
----------------------
The file is validated before write: no NaN/Inf/null in path values,
all required fields present, current_reading is finite. This ensures
`npm run audit:integrity` passes.
"""

from __future__ import annotations

import dataclasses
import json
import logging
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pipeline.recession_watch.metrics import MetricResult, MetricPath

logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[2]
OUT_PATH = ROOT / "data" / "site" / "panel_data" / "recession_watch.json"


def _metric_path_to_list(mp: MetricPath) -> list[dict]:
    """Serialize MetricPath.path, validating no NaN/Inf."""
    validated = []
    for pt in mp.path:
        v = pt["value"]
        if not math.isfinite(v):
            raise ValueError(
                f"Non-finite value {v} at monthsSincePeak={pt['monthsSincePeak']} "
                f"in {mp.label}"
            )
        validated.append({"monthsSincePeak": int(pt["monthsSincePeak"]), "value": float(v)})
    return validated


def _serialize_metric(result: MetricResult) -> dict:
    """Convert a MetricResult to a JSON-serializable dict."""
    if not math.isfinite(result.current_reading):
        raise ValueError(f"Non-finite current_reading for {result.metric}: {result.current_reading}")

    comparators_dict = {}
    for cp in result.comparators:
        comparators_dict[cp.label] = _metric_path_to_list(cp)

    # Validate envelope (skip dict-valued entries like "by_recession")
    env = result.envelope_at_current_duration
    for k, v in env.items():
        if v is not None and isinstance(v, (int, float)) and not math.isfinite(v):
            raise ValueError(f"Non-finite envelope value {k}={v} for {result.metric}")

    return {
        "metric": result.metric,
        "unit": result.unit,
        "description": result.description,
        "peak_date": result.peak_date,
        "current_reading": result.current_reading,
        "current_months_since_peak": result.current_months_since_peak,
        "current": _metric_path_to_list(result.current),
        "comparators": comparators_dict,
        "envelope_at_current_duration": env,
    }


def _validate_fine_breadth(fine: dict) -> None:
    """Validate the fine GDP breadth dict."""
    if "error" in fine:
        logger.warning("Fine GDP breadth has error: %s", fine["error"])
        return
    for pt in fine.get("path", []):
        v = pt["value"]
        if not math.isfinite(v):
            raise ValueError(f"Non-finite fine breadth value at month {pt['monthsSincePeak']}: {v}")


def write_output(
    metrics: dict[str, MetricResult],
    gdp_breadth_fine: dict,
    chain_info: dict,
    current_peak_date: str,
    current_duration: int,
) -> Path:
    """Build and write the recession_watch.json output.

    Args:
        metrics: dict of metric_name -> MetricResult
        gdp_breadth_fine: fine 3-digit breadth dict from compute_fine_gdp_breadth_current
        chain_info: seam dates and calibration ratios from ChainResult
        current_peak_date: ISO date string
        current_duration: months since current peak

    Returns: path to written file.
    """
    # Validate all metrics
    serialized = {}
    for name, result in metrics.items():
        try:
            serialized[name] = _serialize_metric(result)
        except ValueError as e:
            raise ValueError(f"Metric {name} failed validation: {e}") from e

    _validate_fine_breadth(gdp_breadth_fine)

    payload = {
        "section": "recession_watch",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "cyclePeakDate": current_peak_date,
        "currentDurationMonths": current_duration,
        "chainInfo": chain_info,
        "metrics": serialized,
        "gdp_breadthFine": gdp_breadth_fine,
    }

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, allow_nan=False)

    logger.info("Written recession_watch.json -> %s", OUT_PATH)
    return OUT_PATH


def validate_output_file(path: Path | None = None) -> None:
    """Re-read and validate the output file. Raises ValueError on failure.

    Called by the audit:integrity gate.
    """
    target = path or OUT_PATH
    if not target.exists():
        raise FileNotFoundError(f"recession_watch.json not found: {target}")

    with open(target, encoding="utf-8") as f:
        data = json.load(f)

    required_top = {"section", "generatedAt", "cyclePeakDate", "currentDurationMonths",
                    "chainInfo", "metrics", "gdp_breadthFine"}
    missing = required_top - set(data.keys())
    if missing:
        raise ValueError(f"Missing top-level keys: {missing}")

    required_metrics = {"gdp_depth", "gdp_breadth", "emp_depth", "emp_breadth"}
    missing_m = required_metrics - set(data["metrics"].keys())
    if missing_m:
        raise ValueError(f"Missing metrics: {missing_m}")

    for metric_name, metric in data["metrics"].items():
        # Validate current path
        for pt in metric.get("current", []):
            v = pt.get("value")
            if v is None or not math.isfinite(v):
                raise ValueError(f"{metric_name}.current has non-finite value: {pt}")
        # Validate comparators
        for rec_label, path_data in metric.get("comparators", {}).items():
            for pt in path_data:
                v = pt.get("value")
                if v is None or not math.isfinite(v):
                    raise ValueError(f"{metric_name}.comparators[{rec_label}] has non-finite: {pt}")
        # Validate current_reading
        cr = metric.get("current_reading")
        if cr is None or not math.isfinite(cr):
            raise ValueError(f"{metric_name}.current_reading is non-finite: {cr}")

    logger.info("recession_watch.json validation passed")
