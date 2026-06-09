"""Tests for the market-implied path overlay (CORRA futures). Mocked HTTP only.

Run with the repo venv:
    .venv/Scripts/python.exe -m pytest pipeline/shadow_rate/test_market_path.py -q
"""

from __future__ import annotations

import re

import pandas as pd
import pytest

from pipeline.shadow_rate import market_path as mp


# --------------------------------------------------------------------------- #
# Sample HTML mirroring the live CRA quotes table structure
# --------------------------------------------------------------------------- #
SAMPLE_CRA_HTML = """
<html><body>
<table>
  <thead><tr>
    <th>Month</th><th>Bid price</th><th>Ask price</th><th>Settl. price</th>
    <th>Net change</th><th>Open int.</th><th>Vol.</th>
  </tr></thead>
  <tbody>
    <tr><td>March 2026</td><td>97.7150</td><td>97.7175</td><td>97.7175</td>
        <td>0</td><td>252,781</td><td>0</td></tr>
    <tr><td>June 2026</td><td>97.7150</td><td>97.7200</td><td>97.7150</td>
        <td>0</td><td>230,063</td><td>0</td></tr>
    <tr><td>September 2026</td><td>97.6050</td><td>97.6150</td><td>97.6100</td>
        <td>0</td><td>234,876</td><td>0</td></tr>
    <tr><td>December 2026</td><td>97.4050</td><td>97.4250</td><td>97.4050</td>
        <td>0</td><td>329,141</td><td>0</td></tr>
    <tr><td>March 2027</td><td>97.1950</td><td>97.2450</td><td>97.2250</td>
        <td>0</td><td>242,345</td><td>0</td></tr>
    <tr><td>Bad row</td><td></td><td></td><td>n/a</td><td></td><td></td><td></td></tr>
  </tbody>
</table>
</body></html>
"""


# --------------------------------------------------------------------------- #
# Pure arithmetic: price -> implied rate
# --------------------------------------------------------------------------- #
def test_implied_corra_from_settlement():
    assert mp.implied_corra_from_settlement(97.7175) == pytest.approx(2.2825)
    assert mp.implied_corra_from_settlement(100.0) == pytest.approx(0.0)
    assert mp.implied_corra_from_settlement(96.9800) == pytest.approx(3.02)


# --------------------------------------------------------------------------- #
# Contract-month -> reference-quarter mapping
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize(
    "month,year,expected",
    [
        (3, 2026, "2026Q2"),   # March -> Apr-Jun = Q2
        (6, 2026, "2026Q3"),   # June  -> Jul-Sep = Q3
        (9, 2026, "2026Q4"),   # Sept  -> Oct-Dec = Q4
        (12, 2026, "2027Q1"),  # Dec   -> Jan-Mar next year = Q1
        (12, 2028, "2029Q1"),  # year rollover
    ],
)
def test_contract_to_quarter(month, year, expected):
    assert mp.contract_to_quarter(month, year) == expected


def test_label_to_month_year():
    assert mp._label_to_month_year("March 2026") == (3, 2026)
    assert mp._label_to_month_year("December 2028") == (12, 2028)
    assert mp._label_to_month_year("garbage") is None
    assert mp._label_to_month_year("Smarch 2026") is None


# --------------------------------------------------------------------------- #
# HTML parsing
# --------------------------------------------------------------------------- #
def test_parse_cra_table_keys_off_headers_and_skips_bad_rows():
    rows = mp.parse_cra_table(SAMPLE_CRA_HTML)
    # 5 good rows; the "Bad row" with non-numeric settlement is dropped.
    assert len(rows) == 5
    assert rows[0] == ("March 2026", 97.7175)
    assert rows[-1] == ("March 2027", 97.2250)


def test_parse_cra_table_raises_when_no_table():
    with pytest.raises(ValueError, match="no <table>"):
        mp.parse_cra_table("<html><body><p>nope</p></body></html>")


def test_parse_cra_table_column_reorder_is_tolerated():
    """Settlement is keyed by header text, so a column re-order still reads right."""
    html = """
    <table><thead><tr>
      <th>Settl. price</th><th>Month</th><th>Vol.</th>
    </tr></thead><tbody>
      <tr><td>97.5000</td><td>June 2027</td><td>0</td></tr>
    </tbody></table>
    """
    rows = mp.parse_cra_table(html)
    assert rows == [("June 2027", 97.5000)]


# --------------------------------------------------------------------------- #
# Spread adjustment math
# --------------------------------------------------------------------------- #
def test_compute_spread_mean_over_window():
    corra = pd.DataFrame(
        {"date": pd.date_range("2026-05-01", periods=5, freq="D"),
         "value": [2.30, 2.28, 2.26, 2.26, 2.24]}
    )
    target = pd.DataFrame({"date": ["2026-01-01"], "value": [2.25]})
    spread = mp.compute_spread(corra, target, window_days=5)
    # mean([0.05,0.03,0.01,0.01,-0.01]) = 0.018
    assert spread == pytest.approx(0.018)


def test_compute_spread_respects_window_and_stepwise_target():
    corra = pd.DataFrame(
        {"date": pd.date_range("2026-04-01", periods=4, freq="D"),
         "value": [3.00, 2.80, 2.50, 2.50]}
    )
    # Target steps down mid-window; merge_asof(backward) picks the prevailing step.
    target = pd.DataFrame(
        {"date": ["2026-01-01", "2026-04-03"], "value": [3.00, 2.50]}
    )
    # window=2 keeps only the last two CORRA obs, both after the 2.50 step.
    spread = mp.compute_spread(corra, target, window_days=2)
    assert spread == pytest.approx(0.0)


# --------------------------------------------------------------------------- #
# End-to-end build (HTTP + spread mocked)
# --------------------------------------------------------------------------- #
def _mock_valet_corra(httpx_mock):
    httpx_mock.add_response(
        method="GET",
        url=re.compile(r".*/valet/observations/.*"),
        json={
            "terms": {"url": "..."},
            "seriesDetail": {"AVG.INTWO": {"label": "CORRA", "description": "CORRA"}},
            "observations": [
                {"d": "2026-05-01", "AVG.INTWO": {"v": "2.26"}},
                {"d": "2026-05-02", "AVG.INTWO": {"v": "2.26"}},
                {"d": "2026-05-03", "AVG.INTWO": {"v": "2.27"}},
            ],
        },
    )


def test_fetch_market_path_end_to_end(httpx_mock, monkeypatch, tmp_path):
    # CRA page
    httpx_mock.add_response(
        method="GET",
        url=re.compile(r".*m-x\.ca.*symbol=CRA.*"),
        text=SAMPLE_CRA_HTML,
    )
    _mock_valet_corra(httpx_mock)
    # Pin a known target so the spread is deterministic.
    target_csv = tmp_path / "overnight_rate_target.csv"
    pd.DataFrame({"date": ["2026-01-01"], "value": [2.25]}).to_csv(target_csv, index=False)
    monkeypatch.setattr(mp, "OVERNIGHT_TARGET_CSV", target_csv)
    monkeypatch.setattr(mp, "OUT_DIR", tmp_path / "raw")

    path = mp.fetch_market_path(write=True)
    assert path is not None
    by_q = path.by_quarter()
    # March 2026 contract -> 2026Q2; implied_corra = 100 - 97.7175 = 2.2825.
    # spread = mean([0.01,0.01,0.02]) = 0.0133...; implied_target = corra - spread.
    assert "2026Q2" in by_q
    assert path.spread == pytest.approx(0.013333, abs=1e-5)
    assert by_q["2026Q2"] == pytest.approx(2.2825 - 0.013333, abs=1e-4)
    # CSV + sidecar written.
    assert (tmp_path / "raw" / "corra_futures_curve.csv").exists()
    assert (tmp_path / "raw" / "corra_futures_curve.meta.json").exists()


def test_fetch_market_path_graceful_failure_returns_none(monkeypatch, capsys):
    # The CRA fetch raises (e.g. network error after retries are exhausted);
    # everything must degrade to None with a one-line warning, nothing else.
    import httpx

    def _boom():
        raise httpx.ConnectError("boom")

    monkeypatch.setattr(mp, "_fetch_cra_html", _boom)

    path = mp.fetch_market_path(write=False)
    assert path is None
    out = capsys.readouterr().out
    assert "market-implied path unavailable" in out


def test_chart_renders_without_market_line(tmp_path, monkeypatch):
    """Graceful-failure path: market=None -> render_chart still produces files."""
    from datetime import date

    from pipeline.shadow_rate import chart as chart_mod
    from pipeline.shadow_rate.model import PathStep, ShadowResult

    # Minimal ShadowResult + params stub.
    steps = [
        PathStep(quarter="2026Q2", rate=2.25, gap=-0.5, infl_tp4=2.0,
                 gdp_growth=1.2, potential=1.2),
        PathStep(quarter="2026Q3", rate=2.30, gap=-0.4, infl_tp4=2.0,
                 gdp_growth=1.2, potential=1.2),
    ]
    res = ShadowResult(seed_quarter="2026Q2", seed_rate=2.25, steps=steps,
                       core_cpi_path={}, gdp_path={}, potential_path={}, gap_path={})

    class _P:
        neutral_range_low = 2.25
        neutral_range_high = 3.25
        verified = True
        mpr_publication_date = date(2026, 4, 29)

    svg = tmp_path / "c.svg"
    html = tmp_path / "c.html"
    # market=None must not raise and must produce both outputs.
    out_svg, out_html = chart_mod.render_chart(res, _P(), svg, html, market=None)
    assert out_svg.exists() and out_html.exists()
    # The SVG must not carry the dotted market series; the static HTML note's
    # pre-existing "market-implied rate path" phrase is unrelated and expected.
    assert "CORRA futures" not in out_svg.read_text(encoding="utf-8")
    assert "The dotted line is the market-implied policy path" not in \
        out_html.read_text(encoding="utf-8")


def test_chart_renders_market_line_when_provided(tmp_path):
    """When a MarketPath is supplied, the dotted series + footnote appear."""
    from datetime import date

    from pipeline.shadow_rate import chart as chart_mod
    from pipeline.shadow_rate.model import PathStep, ShadowResult

    steps = [
        PathStep(quarter="2026Q2", rate=2.25, gap=-0.5, infl_tp4=2.0,
                 gdp_growth=1.2, potential=1.2),
        PathStep(quarter="2026Q3", rate=2.30, gap=-0.4, infl_tp4=2.0,
                 gdp_growth=1.2, potential=1.2),
    ]
    res = ShadowResult(seed_quarter="2026Q2", seed_rate=2.25, steps=steps,
                       core_cpi_path={}, gdp_path={}, potential_path={}, gap_path={})

    class _P:
        neutral_range_low = 2.25
        neutral_range_high = 3.25
        verified = True
        mpr_publication_date = date(2026, 4, 29)

    market = mp.MarketPath(
        contracts=[
            mp.MarketContract("March 2026", "2026Q2", 97.72, 2.28, 2.27),
            mp.MarketContract("June 2026", "2026Q3", 97.70, 2.30, 2.29),
        ],
        spread=0.01,
        spread_window_days=60,
        fetched_at="2026-06-05T00:00:00+00:00",
    )

    svg = tmp_path / "c.svg"
    html = tmp_path / "c.html"
    chart_mod.render_chart(res, _P(), svg, html, market=market)
    assert "CORRA futures" in svg.read_text(encoding="utf-8")
    assert "The dotted line is the market-implied policy path" in \
        html.read_text(encoding="utf-8")
