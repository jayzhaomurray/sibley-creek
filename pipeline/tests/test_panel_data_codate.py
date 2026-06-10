"""Tests for co-dated slot alignment (markets curve maturities).

Fact-check gate item B3 (2026-06-09): the curve prose stamps the GoC 2y/5y/10y
with ONE date (the 10-year's latest). BoC Valet can publish one maturity a day
behind the others; in that state the sentence would assert a close on a date
that maturity never printed. panel_data.py resolves this by trimming the group
to its most recent COMMON date -- degrade gracefully (one day stale at worst),
never fail the daily build over a benign publish lag.

All fixtures live in tmp_path. Tests never touch production data/ caches
(see feedback: tests must not touch production caches, 2026-06-05).
"""

from __future__ import annotations

import json
from pathlib import Path

from pipeline.io.panel_data import (
    CO_DATED_SLOT_GROUPS,
    _align_co_dated_slots,
    build_section_payload,
)


CURVE_GROUP = ("yield_2yr", "yield_5yr", "yield_10yr")


def _slot(key: str, dates: list[str], start: float = 3.0) -> dict:
    return {
        "key": key,
        "label": key,
        "tier": "raw",
        "data": [
            {"date": d, "value": round(start + 0.01 * i, 4)}
            for i, d in enumerate(dates)
        ],
        "unit": "%",
        "frequency": "daily",
        "asOfISO": dates[-1],
        "source": "Bank of Canada",
    }


# --------------------------------------------------------------------------- #
# _align_co_dated_slots unit tests
# --------------------------------------------------------------------------- #

def test_codate_canary_curve_group_registered():
    """The markets curve panel must stay registered for co-dating."""
    assert CO_DATED_SLOT_GROUPS.get(("markets", "panel-3")) == CURVE_GROUP


def test_aligned_group_is_left_untouched():
    dates = ["2026-06-04", "2026-06-05", "2026-06-08"]
    panel = {
        "primary": _slot("yield_2yr", dates),
        "secondary": _slot("yield_5yr", dates),
        "tertiary": _slot("yield_10yr", dates),
        "extras": [],
    }
    before = json.dumps(panel, sort_keys=True)

    _align_co_dated_slots(panel, CURVE_GROUP, section="markets", panel_id="panel-3")

    assert json.dumps(panel, sort_keys=True) == before
    assert "coDatedAlignment" not in panel


def test_lagging_maturity_trims_group_to_common_date():
    """y2 a day behind: 5y/10y lose their 06-08 row; all three end 06-05."""
    full = ["2026-06-04", "2026-06-05", "2026-06-08"]
    lagged = ["2026-06-04", "2026-06-05"]
    panel = {
        "primary": _slot("yield_2yr", lagged),
        "secondary": _slot("yield_5yr", full),
        "tertiary": _slot("yield_10yr", full),
        "extras": [_slot("yield_30yr", full)],  # NOT in group; must keep 06-08
    }

    _align_co_dated_slots(panel, CURVE_GROUP, section="markets", panel_id="panel-3")

    for name in ("primary", "secondary", "tertiary"):
        assert panel[name]["data"][-1]["date"] == "2026-06-05"
        assert panel[name]["asOfISO"] == "2026-06-05"
    # Out-of-group extra is untouched -- alignment is group-scoped.
    assert panel["extras"][0]["data"][-1]["date"] == "2026-06-08"

    flag = panel["coDatedAlignment"]
    assert flag["alignedTo"] == "2026-06-05"
    assert flag["trimmedFrom"] == {
        "yield_5yr": "2026-06-08",
        "yield_10yr": "2026-06-08",
    }
    assert sorted(flag["group"]) == sorted(CURVE_GROUP)


def test_mid_series_gap_aligns_to_max_of_intersection():
    """y5 has 06-08 but is MISSING 06-05; common date is still 06-05-less.

    Intersection logic, not min-of-latest: trimming to a date a member does
    not actually have would leave its latest() on yet another date.
    """
    panel = {
        "primary": _slot("yield_2yr", ["2026-06-03", "2026-06-04", "2026-06-05"]),
        "secondary": _slot("yield_5yr", ["2026-06-03", "2026-06-04", "2026-06-08"]),
        "tertiary": _slot("yield_10yr", ["2026-06-03", "2026-06-04", "2026-06-05"]),
        "extras": [],
    }

    _align_co_dated_slots(panel, CURVE_GROUP, section="markets", panel_id="panel-3")

    # max(intersection) = 2026-06-04: the latest date ALL THREE printed.
    for name in ("primary", "secondary", "tertiary"):
        assert panel[name]["data"][-1]["date"] == "2026-06-04"
    assert panel["coDatedAlignment"]["alignedTo"] == "2026-06-04"


def test_single_member_present_is_noop():
    panel = {
        "primary": _slot("yield_2yr", ["2026-06-05"]),
        "secondary": None,
        "tertiary": None,
        "extras": [],
    }
    _align_co_dated_slots(panel, CURVE_GROUP, section="markets", panel_id="panel-3")
    assert "coDatedAlignment" not in panel
    assert panel["primary"]["data"][-1]["date"] == "2026-06-05"


def test_empty_intersection_leaves_data_untouched():
    """Zero overlap (pathological): no trim, no flag; loud log only."""
    panel = {
        "primary": _slot("yield_2yr", ["2026-06-04"]),
        "secondary": _slot("yield_5yr", ["2026-06-05"]),
        "tertiary": _slot("yield_10yr", ["2026-06-08"]),
        "extras": [],
    }
    _align_co_dated_slots(panel, CURVE_GROUP, section="markets", panel_id="panel-3")
    assert "coDatedAlignment" not in panel
    assert panel["primary"]["data"][-1]["date"] == "2026-06-04"
    assert panel["tertiary"]["data"][-1]["date"] == "2026-06-08"


# --------------------------------------------------------------------------- #
# End-to-end through build_section_payload (synthetic data_root in tmp_path)
# --------------------------------------------------------------------------- #

def _write_series(data_root: Path, key: str, dates: list[str], start: float) -> None:
    raw = data_root / "raw"
    raw.mkdir(parents=True, exist_ok=True)
    lines = ["date,value"] + [
        f"{d},{round(start + 0.01 * i, 4)}" for i, d in enumerate(dates)
    ]
    (raw / f"{key}.csv").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (raw / f"{key}.meta.json").write_text(
        json.dumps({
            "name": key,
            "source": "Bank of Canada",
            "source_url": "https://www.bankofcanada.ca/valet/",
            "units": "%",
            "frequency": "daily",
        }),
        encoding="utf-8",
    )


def test_build_section_payload_codates_markets_curve(tmp_path: Path):
    """Valet publishes the 2y one day behind: the emitted markets.json curve
    panel must end on the common date for all three maturities, and carry the
    coDatedAlignment record the integrity gate WARNs on."""
    full = ["2026-06-03", "2026-06-04", "2026-06-05", "2026-06-08"]
    lagged = full[:-1]  # 2y missing 06-08

    _write_series(tmp_path, "yield_2yr", lagged, 2.80)
    _write_series(tmp_path, "yield_5yr", full, 3.10)
    _write_series(tmp_path, "yield_10yr", full, 3.45)
    _write_series(tmp_path, "yield_30yr", full, 3.80)

    payload = build_section_payload("markets", tmp_path)
    panel = payload["panels"]["panel-3"]

    assert "error" not in panel
    for name in ("primary", "secondary", "tertiary"):
        assert panel[name]["data"][-1]["date"] == "2026-06-05"
        assert panel[name]["asOfISO"] == "2026-06-05"
    # 30y is on the chart but never date-stamped in prose; keeps its own date.
    assert panel["extras"][0]["key"] == "yield_30yr"
    assert panel["extras"][0]["data"][-1]["date"] == "2026-06-08"

    flag = panel["coDatedAlignment"]
    assert flag["alignedTo"] == "2026-06-05"
    assert set(flag["trimmedFrom"]) == {"yield_5yr", "yield_10yr"}


def test_build_section_payload_aligned_curve_has_no_flag(tmp_path: Path):
    """All maturities co-dated (the normal day): no flag, no trim."""
    full = ["2026-06-04", "2026-06-05", "2026-06-08"]
    for key, start in [("yield_2yr", 2.80), ("yield_5yr", 3.10),
                       ("yield_10yr", 3.45), ("yield_30yr", 3.80)]:
        _write_series(tmp_path, key, full, start)

    payload = build_section_payload("markets", tmp_path)
    panel = payload["panels"]["panel-3"]

    assert "coDatedAlignment" not in panel
    for name in ("primary", "secondary", "tertiary"):
        assert panel[name]["data"][-1]["date"] == "2026-06-08"
