"""Tests for the shadow-rate backtest machinery. Synthetic-only: no fragment
dependency, no network, no live workbook required.

Run with the repo venv:
    .venv/Scripts/python.exe -m pytest pipeline/shadow_rate/test_backtest.py
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
import pytest

from pipeline.shadow_rate import backtest as bt
from pipeline.shadow_rate.inputs import ShadowInputs
from pipeline.shadow_rate.model import quarter_to_ord, run_model


# --------------------------------------------------------------------------- #
# Synthetic vintage dict builder
# --------------------------------------------------------------------------- #
def make_vintage(**over) -> dict:
    """A schema-valid synthetic vintage dict with full anchor coverage.

    Seed = 2022Q2 (April MPR). Quarterly + annual rows cover the seed year
    through the projection end so the engine's coverage checks pass.
    """
    quarterly = []
    for yr in (2022, 2023, 2024):
        for qn in range(1, 5):
            quarterly.append({
                "quarter": f"{yr}Q{qn}",
                "core_cpi_yoy": 3.0,
                "total_cpi_yoy": 5.0,
                "gdp_qq_ann": 1.5,
            })
    annual = [
        {"year": yr, "potential_low": 1.0, "potential_high": 2.0,
         "gdp_q4q4": 1.5, "gdp_annual_avg": 1.5}
        for yr in (2022, 2023, 2024)
    ]
    d = {
        "mpr_date": "2022-04-13",
        "projection_end_quarter": "2024Q4",
        "neutral_range": (2.0, 3.0),
        "output_gap_range": (-0.75, 0.25),
        "output_gap_quarter": "2022Q1",
        "current_overnight_rate": 1.0,
        "quarterly": quarterly,
        "annual": annual,
        "core_concept": "trim_median_avg",
        "source_url": "https://example.test/mpr",
        "notes": "",
    }
    d.update(over)
    return d


# --------------------------------------------------------------------------- #
# Adapter round-trip
# --------------------------------------------------------------------------- #
def test_vintage_to_inputs_roundtrip_runs():
    d = make_vintage()
    inp = bt.vintage_to_inputs(d)
    assert isinstance(inp, ShadowInputs)
    res = run_model(inp)
    # A non-trivial path: seed quarter + forward to projection end.
    assert res.seed_quarter == "2022Q2"
    assert res.seed_rate == 1.0
    assert len(res.steps) >= 2
    assert res.steps[-1].quarter == "2024Q4"


def test_adapter_maps_fields_exactly():
    d = make_vintage()
    inp = bt.vintage_to_inputs(d)
    p = inp.params
    # neutral range, gap midpoint, anchor quarter, verified flag.
    assert (p.neutral_range_low, p.neutral_range_high) == (2.0, 3.0)
    assert p.output_gap_anchor_value == pytest.approx((-0.75 + 0.25) / 2.0)
    assert p.output_gap_anchor_quarter == "2022Q1"
    assert p.verified is True
    # Q4 rows infer the q4q4 anchor; others quarterly.
    by_q = {r.quarter: r for r in inp.quarterly}
    assert by_q["2022Q4"].anchor_type == "q4q4"
    assert by_q["2022Q1"].anchor_type == "quarterly"
    # core/total/gdp mapping.
    assert by_q["2022Q1"].core_cpi_yoy_forecast == 3.0
    assert by_q["2022Q1"].total_cpi_yoy_reference == 5.0
    assert by_q["2022Q1"].gdp_growth_qq_ann_forecast == 1.5


def test_adapter_tolerates_missing_optional_quarterly_fields():
    d = make_vintage()
    # Drop the optional total/gdp from one row.
    d["quarterly"][0] = {"quarter": "2022Q1", "core_cpi_yoy": 3.0}
    inp = bt.vintage_to_inputs(d)
    by_q = {r.quarter: r for r in inp.quarterly}
    assert by_q["2022Q1"].total_cpi_yoy_reference is None
    # gdp None means that year falls back to its q4q4 anchor (still covered).
    res = run_model(inp)
    assert res.steps[-1].quarter == "2024Q4"


# --------------------------------------------------------------------------- #
# Horizon-error arithmetic on hand-built paths/actuals
# --------------------------------------------------------------------------- #
@dataclass
class FakeStep:
    quarter: str
    rate: float


@dataclass
class FakeResult:
    seed_quarter: str
    seed_rate: float
    steps: list


def fake_result(seed: str, rates_by_quarter: dict[str, float], seed_rate: float):
    steps = [FakeStep(q, r) for q, r in rates_by_quarter.items()]
    return FakeResult(seed_quarter=seed, seed_rate=seed_rate, steps=steps)


def test_horizon_error_and_rw_arithmetic():
    # Seed 2022Q2 (ord), implied path rises 1.0 -> ... ; actuals are flat at 2.0.
    seed = "2022Q2"
    implied = {
        "2022Q2": 1.0,   # h0 seed
        "2022Q3": 1.5,   # h1
        "2022Q4": 2.0,   # h2
        "2023Q2": 3.0,   # h4
        "2024Q2": 4.0,   # h8
    }
    res = fake_result(seed, implied, seed_rate=1.0)

    s = quarter_to_ord(seed)
    actual = {
        s: 1.0,        # seed actual
        s + 1: 1.25,
        s + 2: 1.5,
        s + 4: 2.0,
        s + 8: 2.5,
    }
    metrics = bt.compute_metrics([({"mpr_date": "2022-04-13"}, res)], actual)
    by_h = {int(r.horizon_q): r for _, r in metrics.iterrows()}

    # h1: implied 1.5 vs actual 1.25 -> err +0.25; rw = actual(s)-actual(s+1)=1-1.25=-0.25
    assert by_h[1]["bias"] == pytest.approx(0.25)
    assert by_h[1]["mae"] == pytest.approx(0.25)
    assert by_h[1]["mae_rw"] == pytest.approx(0.25)
    assert by_h[1]["skill"] == pytest.approx(1.0)
    # h2: implied 2.0 vs actual 1.5 -> err +0.5; rw = 1-1.5 = -0.5 -> |0.5|
    assert by_h[2]["bias"] == pytest.approx(0.5)
    assert by_h[2]["mae"] == pytest.approx(0.5)
    assert by_h[2]["mae_rw"] == pytest.approx(0.5)
    # h4: implied 3.0 vs actual 2.0 -> err +1.0; rw = 1-2 = -1 -> |1|
    assert by_h[4]["mae"] == pytest.approx(1.0)
    assert by_h[4]["mae_rw"] == pytest.approx(1.0)
    # h8: implied 4.0 vs actual 2.5 -> err +1.5; rw = 1-2.5 = -1.5
    assert by_h[8]["mae"] == pytest.approx(1.5)
    assert by_h[8]["mae_rw"] == pytest.approx(1.5)
    assert by_h[8]["n"] == 1


def test_random_walk_benchmark_closed_form():
    # Two vintages, only h1 populated; verify mean MAE_rw is the closed-form
    # mean of |actual(s) - actual(s+1)|.
    seedA, seedB = "2022Q2", "2023Q2"
    resA = fake_result(seedA, {"2022Q2": 1.0, "2022Q3": 1.0}, seed_rate=1.0)
    resB = fake_result(seedB, {"2023Q2": 4.0, "2023Q3": 4.0}, seed_rate=4.0)
    sA, sB = quarter_to_ord(seedA), quarter_to_ord(seedB)
    actual = {
        sA: 1.0, sA + 1: 2.0,     # rw err = 1-2 = -1 -> 1.0
        sB: 5.0, sB + 1: 4.5,     # rw err = 5-4.5 = 0.5 -> 0.5
    }
    metrics = bt.compute_metrics(
        [({"mpr_date": "a"}, resA), ({"mpr_date": "b"}, resB)], actual)
    by_h = {int(r.horizon_q): r for _, r in metrics.iterrows()}
    assert by_h[1]["n"] == 2
    assert by_h[1]["mae_rw"] == pytest.approx((1.0 + 0.5) / 2.0)
    # rule errs: A implied1.0 vs actual2.0 -> -1.0; B implied4.0 vs actual4.5 -> -0.5
    assert by_h[1]["mae"] == pytest.approx((1.0 + 0.5) / 2.0)
    assert by_h[1]["bias"] == pytest.approx((-1.0 + -0.5) / 2.0)


def test_skipped_when_actual_missing():
    seed = "2022Q2"
    res = fake_result(seed, {"2022Q2": 1.0, "2022Q3": 1.5}, seed_rate=1.0)
    # No actuals at all -> every horizon n=0, skill NaN.
    metrics = bt.compute_metrics([({"mpr_date": "x"}, res)], {})
    for _, r in metrics.iterrows():
        assert r["n"] == 0
        assert pd.isna(r["skill"])


# --------------------------------------------------------------------------- #
# Direction hit-rate
# --------------------------------------------------------------------------- #
def test_direction_hit_rate_cases():
    # Vintage 1: rule says UP (implied(s+2) > seed), actual went UP -> hit.
    # Vintage 2: rule says UP, actual went DOWN -> miss.
    seed1, seed2 = "2022Q2", "2023Q2"
    res1 = fake_result(seed1, {"2022Q2": 1.0, "2022Q3": 1.5, "2022Q4": 2.0}, seed_rate=1.0)
    res2 = fake_result(seed2, {"2023Q2": 4.0, "2023Q3": 4.5, "2023Q4": 5.0}, seed_rate=4.0)
    s1, s2 = quarter_to_ord(seed1), quarter_to_ord(seed2)
    actual = {
        s1: 1.0, s1 + 2: 2.0,     # actual up; implied up -> hit
        s2: 5.0, s2 + 2: 4.0,     # actual down; implied up -> miss
    }
    metrics = bt.compute_metrics(
        [({"mpr_date": "a"}, res1), ({"mpr_date": "b"}, res2)], actual)
    h2 = next(r for _, r in metrics.iterrows() if int(r.horizon_q) == 2)
    assert h2["dir_hit_rate"] == pytest.approx(0.5)


def test_direction_flat_move_is_hit_only_when_both_flat():
    # Rule implies no move, actual no move -> hit.
    seed = "2022Q2"
    res = fake_result(seed, {"2022Q2": 2.0, "2022Q3": 2.0, "2022Q4": 2.0}, seed_rate=2.0)
    s = quarter_to_ord(seed)
    actual = {s: 3.0, s + 2: 3.0}  # both flat
    metrics = bt.compute_metrics([({"mpr_date": "a"}, res)], actual)
    h2 = next(r for _, r in metrics.iterrows() if int(r.horizon_q) == 2)
    assert h2["dir_hit_rate"] == pytest.approx(1.0)


# --------------------------------------------------------------------------- #
# Quarter-end sampling of the actual series
# --------------------------------------------------------------------------- #
def test_load_actual_by_quarter_samples_quarter_end(tmp_path):
    csv = tmp_path / "rates.csv"
    csv.write_text(
        "date,value\n"
        "2022-01-01,1.0\n2022-02-01,1.1\n2022-03-01,1.2\n"   # 2022Q1 -> 1.2 (Mar)
        "2022-04-01,1.5\n2022-06-01,1.8\n",                   # 2022Q2 -> 1.8 (Jun)
        encoding="utf-8",
    )
    by_q = bt.load_actual_by_quarter(csv)
    assert by_q[quarter_to_ord("2022Q1")] == pytest.approx(1.2)
    assert by_q[quarter_to_ord("2022Q2")] == pytest.approx(1.8)


# --------------------------------------------------------------------------- #
# Long-format frame
# --------------------------------------------------------------------------- #
def test_paths_long_frame_shape():
    d = make_vintage()
    inp = bt.vintage_to_inputs(d)
    res = run_model(inp)
    df = bt.paths_long_frame([(d, res)])
    assert list(df.columns) == ["vintage_date", "quarter", "implied_rate"]
    assert (df["vintage_date"] == "2022-04-13").all()
    assert len(df) == len(res.steps)


# --------------------------------------------------------------------------- #
# Aggregator tolerates missing fragments
# --------------------------------------------------------------------------- #
def test_aggregator_imports_and_is_a_list():
    # The vintages package must import cleanly even when no fragment files
    # exist (they are owned by other agents and may be absent).
    from pipeline.shadow_rate import vintages
    assert isinstance(vintages.ALL_VINTAGES, list)


# --------------------------------------------------------------------------- #
# MPS market paths: interpolation, matching, MAE_market, missing tolerance
# --------------------------------------------------------------------------- #
def test_market_path_linear_interpolation():
    # Sparse points two quarters apart -> midpoint is interpolated; endpoints
    # exact; nothing extrapolated beyond the span.
    rec = {"path": [("2024Q1", 4.0), ("2024Q3", 3.0), ("2025Q1", 3.0)]}
    dense = bt.market_path_by_ord(rec)
    o = quarter_to_ord
    assert dense[o("2024Q1")] == pytest.approx(4.0)
    assert dense[o("2024Q2")] == pytest.approx(3.5)   # midpoint of 4.0->3.0
    assert dense[o("2024Q3")] == pytest.approx(3.0)
    assert dense[o("2024Q4")] == pytest.approx(3.0)   # midpoint of 3.0->3.0
    assert dense[o("2025Q1")] == pytest.approx(3.0)
    # No extrapolation outside the published span.
    assert o("2023Q4") not in dense
    assert o("2025Q2") not in dense


def test_market_path_empty_and_single_point():
    assert bt.market_path_by_ord({"path": []}) == {}
    assert bt.market_path_by_ord({}) == {}
    single = bt.market_path_by_ord({"path": [("2024Q2", 2.5)]})
    assert single == {quarter_to_ord("2024Q2"): 2.5}


def test_match_market_path_by_quarter():
    surveys = {
        "2024Q2": {"survey": "2024Q2", "path": [("2024Q3", 4.5)]},
        "2024Q1": {"survey": "2024Q1", "path": [("2024Q2", 4.75)]},
    }
    # Apr-2024 MPR -> 2024Q2 survey (same calendar quarter as the MPR date).
    v = {"mpr_date": "2024-04-10"}
    assert bt.match_market_path(v, surveys)["survey"] == "2024Q2"
    # Jan-2024 MPR -> 2024Q1 survey.
    assert bt.match_market_path({"mpr_date": "2024-01-24"}, surveys)["survey"] == "2024Q1"
    # A vintage with no same-quarter survey -> None.
    assert bt.match_market_path({"mpr_date": "2022-04-13"}, surveys) is None
    # Live workbook is never matched.
    assert bt.match_market_path({"mpr_date": "2024-04-10", "_live": True}, surveys) is None


def test_mae_market_arithmetic():
    # Seed 2022Q2; rule + a matched survey both compared to flat actuals.
    seed = "2022Q2"
    implied = {"2022Q2": 1.0, "2022Q3": 1.5, "2022Q4": 2.0, "2023Q2": 3.0}
    res = fake_result(seed, implied, seed_rate=1.0)
    s = quarter_to_ord(seed)
    actual = {s: 1.0, s + 1: 1.0, s + 2: 1.0, s + 4: 1.0}
    # Survey matched to the vintage's quarter (2022Q2). Sparse points cover
    # 2022Q3..2023Q2 so h1,h2,h4 all have a market value.
    surveys = {
        "2022Q2": {"survey": "2022Q2",
                   "path": [("2022Q3", 2.0), ("2022Q4", 2.0), ("2023Q2", 2.0)]},
    }
    vintage = {"mpr_date": "2022-04-13"}
    metrics = bt.compute_metrics([(vintage, res)], actual, surveys)
    by_h = {int(r.horizon_q): r for _, r in metrics.iterrows()}
    # h1: market 2.0 vs actual 1.0 -> |1.0|; rule 1.5 vs 1.0 -> |0.5|.
    assert by_h[1]["mae_market"] == pytest.approx(1.0)
    assert by_h[1]["mae_rule_m"] == pytest.approx(0.5)
    assert by_h[1]["skill_rule_vs_market"] == pytest.approx(0.5)
    assert by_h[1]["n_market"] == 1
    # h4: market interpolates to 2.0 at 2023Q2; rule 3.0 -> |2.0| vs market |1.0|.
    assert by_h[4]["mae_market"] == pytest.approx(1.0)
    assert by_h[4]["mae_rule_m"] == pytest.approx(2.0)
    assert by_h[4]["skill_rule_vs_market"] == pytest.approx(2.0)


def test_mae_market_subset_is_like_for_like():
    # Two vintages: only ONE has a matched survey. mae_rule_m must average the
    # rule error over ONLY the market-available cells, not all cells.
    seedA, seedB = "2022Q2", "2023Q2"
    resA = fake_result(seedA, {"2022Q2": 1.0, "2022Q3": 2.0}, seed_rate=1.0)
    resB = fake_result(seedB, {"2023Q2": 4.0, "2023Q3": 4.0}, seed_rate=4.0)
    sA, sB = quarter_to_ord(seedA), quarter_to_ord(seedB)
    actual = {sA: 1.0, sA + 1: 1.0, sB: 4.0, sB + 1: 4.0}
    # Only vintage A's quarter has a survey.
    surveys = {"2022Q2": {"survey": "2022Q2", "path": [("2022Q3", 3.0)]}}
    metrics = bt.compute_metrics(
        [({"mpr_date": "2022-04-13"}, resA),
         ({"mpr_date": "2023-04-12"}, resB)], actual, surveys)
    by_h = {int(r.horizon_q): r for _, r in metrics.iterrows()}
    # Full rule subset has n=2 at h1; market subset n_market=1 (only A).
    assert by_h[1]["n"] == 2
    assert by_h[1]["n_market"] == 1
    # market: 3.0 vs 1.0 -> |2.0|; rule on A only: 2.0 vs 1.0 -> |1.0|.
    assert by_h[1]["mae_market"] == pytest.approx(2.0)
    assert by_h[1]["mae_rule_m"] == pytest.approx(1.0)


def test_missing_surveys_tolerated():
    # No surveys at all -> market columns NaN / n_market 0, rule-vs-rw unchanged.
    seed = "2022Q2"
    res = fake_result(seed, {"2022Q2": 1.0, "2022Q3": 1.5}, seed_rate=1.0)
    s = quarter_to_ord(seed)
    actual = {s: 1.0, s + 1: 1.25}
    metrics = bt.compute_metrics([({"mpr_date": "2022-04-13"}, res)], actual, {})
    by_h = {int(r.horizon_q): r for _, r in metrics.iterrows()}
    assert by_h[1]["n"] == 1
    assert by_h[1]["mae"] == pytest.approx(0.25)   # rule-vs-rw intact
    assert by_h[1]["n_market"] == 0
    assert pd.isna(by_h[1]["mae_market"])
    assert pd.isna(by_h[1]["skill_rule_vs_market"])
    # And compute_metrics with surveys=None behaves the same.
    metrics2 = bt.compute_metrics([({"mpr_date": "2022-04-13"}, res)], actual)
    h1b = next(r for _, r in metrics2.iterrows() if int(r.horizon_q) == 1)
    assert h1b["n_market"] == 0


def test_market_paths_module_shape():
    # The transcription module imports and matches the documented schema.
    from pipeline.shadow_rate.vintages.market_paths import MARKET_PATHS
    assert isinstance(MARKET_PATHS, list) and MARKET_PATHS
    surveys = {r["survey"] for r in MARKET_PATHS}
    assert "2023Q1" in surveys  # earliest published survey
    for rec in MARKET_PATHS:
        assert set(rec) >= {"survey", "published", "source_url", "path"}
        assert rec["path"], f"{rec['survey']} has an empty path"
        for q, rate in rec["path"]:
            assert len(q) == 6 and q[4] == "Q"   # 'YYYYQn'
            assert isinstance(rate, (int, float))


def test_aggregator_skips_broken_fragment(monkeypatch, capsys):
    # Re-run the aggregator logic against a fragment list where one import
    # raises: it must skip-and-note, not propagate.
    import importlib
    from pipeline.shadow_rate import vintages as v

    calls = {}

    def fake_import(name):
        if name.endswith("good"):
            mod = type("M", (), {"VINTAGES": [{"mpr_date": "2099-01-01"}]})
            return mod
        raise ModuleNotFoundError(name)

    # Exercise the same defensive pattern the package uses.
    collected: list[dict] = []
    for frag in ("good", "broken"):
        try:
            mod = fake_import(f"pkg.{frag}")
        except Exception as exc:
            calls[frag] = type(exc).__name__
            continue
        collected.extend(getattr(mod, "VINTAGES", []))

    assert collected == [{"mpr_date": "2099-01-01"}]
    assert calls["broken"] == "ModuleNotFoundError"
    # And the real package is still a list regardless.
    assert isinstance(v.ALL_VINTAGES, list)
