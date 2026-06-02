from __future__ import annotations

from datetime import date, datetime, timezone
from pathlib import Path

import pandas as pd
import pytest

import pipeline.provisional.goc_yields as goc_yields
from pipeline.io.overlays import apply_series_overlay
from pipeline.provisional.goc_yields import (
    overlay_map_from_payload,
    parse_trading_economics_curve,
    validate_payload,
)


TE_HTML = """
<html><body>
<table>
<tr><td>Canada 10Y</td><td>3.43</td><td>0.014%</td><td>-0.190%</td><td>0.204%</td><td>Jun/01</td></tr>
<tr><td>Canada 2Y</td><td>2.81</td><td>0.033%</td><td>-0.240%</td><td>0.230%</td><td>Jun/01</td></tr>
<tr><td>Canada 30Y</td><td>3.80</td><td>0.003%</td><td>-0.161%</td><td>0.306%</td><td>Jun/01</td></tr>
<tr><td>Canada 5Y</td><td>3.08</td><td>0.029%</td><td>-0.194%</td><td>0.254%</td><td>Jun/01</td></tr>
</table>
</body></html>
"""


def _mock_official_curve(monkeypatch):
    values = {
        "yield_2yr": 2.77,
        "yield_5yr": 3.05,
        "yield_10yr": 3.41,
        "yield_30yr": 3.79,
    }

    def fake_latest(_data_root, series):
        return date(2026, 5, 29), values[series]

    monkeypatch.setattr(goc_yields, "_read_latest_official", fake_latest)


def test_parse_trading_economics_curve_extracts_full_same_date_curve():
    payload = parse_trading_economics_curve(
        TE_HTML,
        fetched_at=datetime(2026, 6, 2, tzinfo=timezone.utc),
    )

    assert payload["asOf"] == "2026-06-01"
    assert payload["values"] == {
        "yield_10yr": 3.43,
        "yield_2yr": 2.81,
        "yield_30yr": 3.80,
        "yield_5yr": 3.08,
    }


def test_validate_payload_accepts_complete_newer_curve(monkeypatch):
    _mock_official_curve(monkeypatch)
    payload = parse_trading_economics_curve(
        TE_HTML,
        fetched_at=datetime(2026, 6, 2, tzinfo=timezone.utc),
    )

    checked = validate_payload(payload, data_root=Path("data"))

    assert checked["status"] == "ok"
    assert checked["violations"] == []


def test_validate_payload_rejects_missing_maturity(monkeypatch):
    _mock_official_curve(monkeypatch)
    payload = parse_trading_economics_curve(
        TE_HTML.replace("Canada 30Y", "Canada 20Y"),
        fetched_at=datetime(2026, 6, 2, tzinfo=timezone.utc),
    )

    checked = validate_payload(payload, data_root=Path("data"))

    assert checked["status"] == "invalid"
    assert any("yield_30yr" in violation for violation in checked["violations"])


def test_validate_payload_rejects_mixed_dates():
    payload = parse_trading_economics_curve(
        TE_HTML.replace("Canada 5Y</td><td>3.08</td><td>0.029%</td><td>-0.194%</td><td>0.254%</td><td>Jun/01",
                        "Canada 5Y</td><td>3.08</td><td>0.029%</td><td>-0.194%</td><td>0.254%</td><td>May/29"),
        fetched_at=datetime(2026, 6, 2, tzinfo=timezone.utc),
    )

    checked = validate_payload(payload)

    assert checked["status"] == "invalid"
    assert any("mixed provisional as-of dates" in violation for violation in checked["violations"])


def test_validate_payload_rejects_large_move_from_official(monkeypatch):
    _mock_official_curve(monkeypatch)
    payload = parse_trading_economics_curve(
        TE_HTML.replace("Canada 10Y</td><td>3.43", "Canada 10Y</td><td>4.50"),
        fetched_at=datetime(2026, 6, 2, tzinfo=timezone.utc),
    )

    checked = validate_payload(payload, data_root=Path("data"))

    assert checked["status"] == "invalid"
    assert any("yield_10yr" in violation and "exceeds" in violation for violation in checked["violations"])


def test_overlay_appends_only_newer_row():
    payload = validate_payload(parse_trading_economics_curve(
        TE_HTML,
        fetched_at=datetime(2026, 6, 2, tzinfo=timezone.utc),
    ))
    overlays = overlay_map_from_payload(payload)
    df = pd.DataFrame([
        {"date": "2026-05-29", "value": 3.41},
    ])
    meta = {"source": "Bank of Canada Valet API", "source_url": "https://example.test", "source_id": "BD.CDN.10YR.DQ.YLD"}

    out, out_meta, info = apply_series_overlay("yield_10yr", df, meta, overlays)

    assert out.iloc[-1]["date"].date().isoformat() == "2026-06-01"
    assert out.iloc[-1]["value"] == pytest.approx(3.43)
    assert info["status"] == "provisional"
    assert out_meta["provisional_overlay"]["canonicalSource"] == "Bank of Canada Valet API"


def test_overlay_ignores_when_official_is_same_date_or_newer():
    payload = validate_payload(parse_trading_economics_curve(
        TE_HTML,
        fetched_at=datetime(2026, 6, 2, tzinfo=timezone.utc),
    ))
    overlays = overlay_map_from_payload(payload)
    df = pd.DataFrame([
        {"date": "2026-06-01", "value": 3.42},
    ])

    out, _, info = apply_series_overlay("yield_10yr", df, {}, overlays)

    assert len(out) == 1
    assert info is None
