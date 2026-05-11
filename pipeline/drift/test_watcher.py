"""Smoke tests for the drift watcher.

We stand up a synthetic mini-repo (registry + two CSV sources + one JSON
panel-data file) in a tmp directory, run the watcher, and assert:
  * the claim within threshold classifies as ``clear``,
  * the claim beyond threshold classifies as ``drift_flagged``,
  * the JSON-panel source resolver works end-to-end,
  * a missing file classifies as ``data_missing`` (not a crash),
  * the alert file is written with the expected content.
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from pipeline.drift.claims_registry import load_claims_registry
from pipeline.drift.watcher import (
    check_drift,
    render_alert,
    run_watcher,
)


REGISTRY_YAML = """\
pillars:
  - slug: smoke-pillar
    title: "Smoke pillar"
    published_at: "2026-05-11"
    claims:
      - id: S1
        text: "Headline unemployment at 6.9%."
        data_source: "data/raw/unemployment_rate.csv -> last row"
        published_value: 6.9
        unit: "%"
        threshold: 0.5
      - id: S2
        text: "Mortgage interest cost Y/Y at 0.28%."
        data_source: "data/site/panel_data/inflation.json -> panels[?key=='cpi_mortgage_interest_yoy'].value"
        published_value: 0.28
        unit: "%"
        threshold: 0.30
      - id: S3
        text: "Some series that does not exist on disk."
        data_source: "data/raw/does_not_exist.csv -> last row"
        published_value: 1.0
        unit: "%"
        threshold: 0.1
"""


def _scaffold_repo(tmp_path: Path) -> Path:
    """Create a synthetic project tree under tmp_path and return its root."""
    (tmp_path / "editorial" / "drift").mkdir(parents=True)
    (tmp_path / "data" / "raw").mkdir(parents=True)
    (tmp_path / "data" / "site" / "panel_data").mkdir(parents=True)

    (tmp_path / "editorial" / "drift" / "load_bearing_claims.yml").write_text(
        REGISTRY_YAML, encoding="utf-8"
    )

    # S1 source: current value 7.0% -> delta +0.1 (within threshold 0.5)
    (tmp_path / "data" / "raw" / "unemployment_rate.csv").write_text(
        "date,value\n2026-03-01,6.8\n2026-04-01,7.0\n",
        encoding="utf-8",
    )

    # S2 source: a minimal panel JSON. Current value 1.20 -> delta +0.92
    # (beyond threshold 0.30 -> drift_flagged).
    panel_doc = {
        "section": "inflation",
        "generatedAt": "2026-05-11T00:00:00+00:00",
        "panels": {
            "panel-1": {
                "primary": {
                    "key": "cpi_all_items_yoy",
                    "data": [
                        {"date": "2026-03-01", "value": 2.32},
                    ],
                },
                "extras": [
                    {
                        "key": "cpi_mortgage_interest_yoy",
                        "data": [
                            {"date": "2026-02-01", "value": 0.95},
                            {"date": "2026-03-01", "value": 1.20},
                        ],
                    }
                ],
            }
        },
    }
    (tmp_path / "data" / "site" / "panel_data" / "inflation.json").write_text(
        json.dumps(panel_doc), encoding="utf-8"
    )

    return tmp_path


def test_load_registry(tmp_path: Path) -> None:
    repo = _scaffold_repo(tmp_path)
    claims = load_claims_registry(
        repo / "editorial" / "drift" / "load_bearing_claims.yml"
    )
    assert [c.id for c in claims] == ["S1", "S2", "S3"]
    assert all(c.pillar_slug == "smoke-pillar" for c in claims)
    assert claims[0].threshold == 0.5


def test_check_drift_within_threshold(tmp_path: Path) -> None:
    repo = _scaffold_repo(tmp_path)
    claims = load_claims_registry(
        repo / "editorial" / "drift" / "load_bearing_claims.yml"
    )
    s1 = next(c for c in claims if c.id == "S1")
    result = check_drift(s1, repo)
    assert result.status == "clear"
    assert result.current_value == 7.0
    assert result.current_as_of == "2026-04-01"
    assert abs(result.delta - 0.1) < 1e-9


def test_check_drift_beyond_threshold_json_panel(tmp_path: Path) -> None:
    repo = _scaffold_repo(tmp_path)
    claims = load_claims_registry(
        repo / "editorial" / "drift" / "load_bearing_claims.yml"
    )
    s2 = next(c for c in claims if c.id == "S2")
    result = check_drift(s2, repo)
    assert result.status == "drift_flagged"
    assert result.current_value == 1.20
    assert result.current_as_of == "2026-03-01"
    assert abs(result.delta - 0.92) < 1e-9


def test_check_drift_data_missing(tmp_path: Path) -> None:
    repo = _scaffold_repo(tmp_path)
    claims = load_claims_registry(
        repo / "editorial" / "drift" / "load_bearing_claims.yml"
    )
    s3 = next(c for c in claims if c.id == "S3")
    result = check_drift(s3, repo)
    assert result.status == "data_missing"
    assert result.current_value is None
    assert result.delta is None
    assert result.note is not None


def test_run_watcher_writes_alert(tmp_path: Path) -> None:
    repo = _scaffold_repo(tmp_path)
    alert_path, results = run_watcher(
        registry_path="editorial/drift/load_bearing_claims.yml",
        repo_root=repo,
        alerts_dir="editorial/drift/alerts",
        run_date=date(2026, 5, 11),
    )
    assert alert_path.exists()
    assert alert_path.name == "2026-05-11.md"

    content = alert_path.read_text(encoding="utf-8")
    assert "Drift watcher report" in content
    assert "smoke-pillar/S2" in content
    assert "Drift flagged" in content
    assert "Data missing" in content
    # The clear claim should appear in the per-pillar roll-up.
    assert "S1" in content

    statuses = {r.claim.id: r.status for r in results}
    assert statuses == {
        "S1": "clear",
        "S2": "drift_flagged",
        "S3": "data_missing",
    }


def test_render_alert_no_drift_message() -> None:
    """When no drift and no missing data, the alert still writes a 'clear' note."""
    from pipeline.drift.claims_registry import Claim
    from pipeline.drift.watcher import DriftResult

    c = Claim(
        pillar_slug="x",
        pillar_title="X",
        pillar_published_at="2026-05-11",
        id="X1",
        text="t",
        data_source="data/raw/unemployment_rate.csv -> last row",
        published_value=1.0,
        unit="%",
        threshold=0.5,
    )
    r = DriftResult(
        claim=c,
        status="clear",
        current_value=1.1,
        current_as_of="2026-04-01",
        delta=0.1,
        note=None,
    )
    out = render_alert([r], date(2026, 5, 11))
    assert "All claims within threshold" in out
    assert "No drift detected" in out
