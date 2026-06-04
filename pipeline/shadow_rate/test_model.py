"""Tests for the shadow-rate model. Math locked before I/O. No HTTP.

Run with the repo venv:
    .venv/Scripts/python.exe -m pytest pipeline/shadow_rate/test_model.py
"""

from __future__ import annotations

from datetime import date

import pytest

from pipeline.shadow_rate.inputs import (
    AnnualRow,
    Params,
    QuarterlyRow,
    ShadowInputs,
)
from pipeline.shadow_rate import model as m


# --------------------------------------------------------------------------- #
# Fixture builders
# --------------------------------------------------------------------------- #
def make_params(**over) -> Params:
    base = dict(
        mpr_publication_date=date(2026, 4, 29),
        current_overnight_rate=2.25,
        output_gap_anchor_quarter="2026Q2",
        output_gap_anchor_value=-0.5,
        neutral_range_low=2.25,
        neutral_range_high=3.25,
        rho=0.85,
        phi_pi=4.65,
        phi_gap=0.40,
        inflation_target=2.0,
        inflation_converge_quarters=4,
        elb_floor=0.25,
        verified=False,
    )
    base.update(over)
    return Params(**base)


def const_inputs(core=2.0, gdp=1.2, potential=1.2, gap_low=0.0, gap_high=0.0,
                 anchor_quarter="2026Q2",
                 years=(2025, 2026, 2027, 2028, 2029, 2030), **pover) -> ShadowInputs:
    """Inputs with constant core CPI and GDP=potential everywhere (flat gap).

    ``gap_low``/``gap_high`` keep the old call sites working: their midpoint is
    the output-gap anchor value, anchored (by default) at the 2026Q2 seed quarter.
    """
    quarterly = []
    for yr in years:
        for qn in range(1, 5):
            quarterly.append(
                QuarterlyRow(
                    quarter=f"{yr}Q{qn}",
                    core_cpi_yoy_forecast=core,
                    total_cpi_yoy_reference=None,
                    gdp_growth_qq_ann_forecast=gdp,
                    anchor_type="q4q4" if qn == 4 else "quarterly",
                    source_ref="test",
                )
            )
    annual = [
        AnnualRow(
            year=yr,
            potential_growth_low=potential,
            potential_growth_high=potential,
            gdp_q4q4=gdp,
            source_ref="test",
        )
        for yr in years
    ]
    params = make_params(
        output_gap_anchor_quarter=anchor_quarter,
        output_gap_anchor_value=(gap_low + gap_high) / 2.0,
        **pover,
    )
    return ShadowInputs(quarterly=quarterly, annual=annual, params=params)


# --------------------------------------------------------------------------- #
# Quarter arithmetic
# --------------------------------------------------------------------------- #
def test_quarter_roundtrip():
    for q in ["2025Q1", "2026Q2", "2028Q4", "2030Q3"]:
        assert m.ord_to_quarter(m.quarter_to_ord(q)) == q


def test_quarter_ordering():
    assert m.quarter_to_ord("2026Q3") - m.quarter_to_ord("2026Q2") == 1
    assert m.quarter_to_ord("2027Q1") - m.quarter_to_ord("2026Q4") == 1


def test_quarter_of_date():
    assert m.quarter_of_date(date(2026, 4, 29)) == "2026Q2"
    assert m.quarter_of_date(date(2026, 1, 15)) == "2026Q1"
    assert m.quarter_of_date(date(2026, 12, 31)) == "2026Q4"


# --------------------------------------------------------------------------- #
# Steady-state fixed point
# --------------------------------------------------------------------------- #
def test_steady_state_fixed_point():
    """Constant inputs: rate converges to neutral + phi_pi*(pi-target) + phi_gap*gap.

    With core=target and gap=0, the fixed point is exactly the neutral midpoint,
    and seeding there means the rate never moves.
    """
    inp = const_inputs(core=2.0, gdp=1.2, potential=1.2, gap_low=0.0, gap_high=0.0,
                       current_overnight_rate=2.75)  # = neutral midpoint
    res = m.run_model(inp, end_quarter="2028Q4")
    for step in res.steps:
        assert step.rate == pytest.approx(2.75, abs=1e-9)


def test_steady_state_fixed_point_with_inflation_gap():
    """Constant core above target, gap=0 -> fixed point above neutral."""
    inp = const_inputs(core=3.0, gdp=1.2, potential=1.2, gap_low=0.0, gap_high=0.0)
    # fixed point R* = 2.75 + 4.65*(3.0-2.0) + 0.4*0 = 7.40
    fp = 2.75 + 4.65 * 1.0
    inp2 = const_inputs(core=3.0, gdp=1.2, potential=1.2, gap_low=0.0, gap_high=0.0,
                        current_overnight_rate=fp)
    res = m.run_model(inp2, end_quarter="2028Q4")
    for step in res.steps:
        assert step.rate == pytest.approx(fp, abs=1e-9)


# --------------------------------------------------------------------------- #
# One-step closed form
# --------------------------------------------------------------------------- #
def test_one_step_closed_form():
    inp = const_inputs(core=3.0, gdp=1.2, potential=1.2, gap_low=0.0, gap_high=0.0,
                       current_overnight_rate=2.25)
    res = m.run_model(inp, end_quarter="2028Q4")
    # First update: target_level = 2.75 + 4.65*(3-2) + 0.4*0 = 7.40
    # R_1 = 0.85*2.25 + 0.15*7.40 = 1.9125 + 1.11 = 3.0225
    assert res.steps[0].rate == pytest.approx(2.25, abs=1e-12)
    assert res.steps[1].rate == pytest.approx(0.85 * 2.25 + 0.15 * 7.40, abs=1e-12)


# --------------------------------------------------------------------------- #
# Geometric inertia approach
# --------------------------------------------------------------------------- #
def test_geometric_inertia_approach():
    """With constant target_level T and gap=0, the gap to T shrinks by rho each step."""
    inp = const_inputs(core=3.0, gdp=1.2, potential=1.2, gap_low=0.0, gap_high=0.0,
                       current_overnight_rate=2.25)
    res = m.run_model(inp, end_quarter="2028Q4")
    T = 2.75 + 4.65 * 1.0  # 7.40
    rho = 0.85
    prev_gap = None
    for step in res.steps:
        g = T - step.rate
        if prev_gap is not None and abs(prev_gap) > 1e-9:
            assert g / prev_gap == pytest.approx(rho, abs=1e-9)
        prev_gap = g


# --------------------------------------------------------------------------- #
# Gap identity
# --------------------------------------------------------------------------- #
def test_gap_identity():
    """+1pp growth above potential -> gap rises +0.25/quarter."""
    inp = const_inputs(core=2.0, gdp=2.2, potential=1.2, gap_low=0.0, gap_high=0.0)
    res = m.run_model(inp, end_quarter="2028Q4")
    seed_ord = m.quarter_to_ord(res.seed_quarter)
    g0 = res.gap_path[seed_ord]
    g1 = res.gap_path[seed_ord + 1]
    assert g1 - g0 == pytest.approx(0.25, abs=1e-9)
    g2 = res.gap_path[seed_ord + 2]
    assert g2 - g1 == pytest.approx(0.25, abs=1e-9)


# --------------------------------------------------------------------------- #
# Anchor + roll-forward to the seed quarter
# --------------------------------------------------------------------------- #
def _seed_inputs(anchor_quarter="2025Q4", anchor_value=-1.0, **pover) -> ShadowInputs:
    """The April-2026-MPR seed-data shape: GDP 2025Q3=2.4, Q4=-0.6, 2026Q1/Q2=1.5;
    potential 2025=2.3, 2026=1.2. Used to exercise the anchor roll-forward."""
    quarterly = []
    for q, core, gdp in [
        ("2025Q3", 3.1, 2.4),
        ("2025Q4", 2.8, -0.6),
        ("2026Q1", 2.4, 1.5),
        ("2026Q2", 2.1, 1.5),
    ]:
        quarterly.append(QuarterlyRow(quarter=q, core_cpi_yoy_forecast=core,
                                       total_cpi_yoy_reference=None,
                                       gdp_growth_qq_ann_forecast=gdp,
                                       anchor_type="quarterly", source_ref="t"))
    for q, core in [("2026Q4", 2.0), ("2027Q4", 2.2), ("2028Q4", 2.0)]:
        quarterly.append(QuarterlyRow(quarter=q, core_cpi_yoy_forecast=core,
                                       total_cpi_yoy_reference=None,
                                       gdp_growth_qq_ann_forecast=None,
                                       anchor_type="q4q4", source_ref="t"))
    annual = [
        AnnualRow(year=2025, potential_growth_low=2.3, potential_growth_high=2.3,
                  gdp_q4q4=None, source_ref="t"),
        AnnualRow(year=2026, potential_growth_low=0.8, potential_growth_high=1.6,
                  gdp_q4q4=1.8, source_ref="t"),
        AnnualRow(year=2027, potential_growth_low=0.8, potential_growth_high=1.8,
                  gdp_q4q4=1.4, source_ref="t"),
        AnnualRow(year=2028, potential_growth_low=1.0, potential_growth_high=2.0,
                  gdp_q4q4=1.9, source_ref="t"),
    ]
    params = make_params(output_gap_anchor_quarter=anchor_quarter,
                         output_gap_anchor_value=anchor_value, **pover)
    return ShadowInputs(quarterly=quarterly, annual=annual, params=params)


def test_anchor_roll_forward_to_seed():
    """Anchor 2025Q4=-1.0 rolls forward to seed 2026Q2=-0.85 on the seed data.

    2026Q1 = -1.0 + (1.5 - 1.2)/4 = -0.925
    2026Q2 = -0.925 + (1.5 - 1.2)/4 = -0.85
    """
    inp = _seed_inputs(anchor_quarter="2025Q4", anchor_value=-1.0)
    res = m.run_model(inp, end_quarter="2028Q4")
    aord = m.quarter_to_ord("2025Q4")
    assert res.gap_path[aord] == pytest.approx(-1.0, abs=1e-9)
    assert res.gap_path[m.quarter_to_ord("2026Q1")] == pytest.approx(-0.925, abs=1e-9)
    assert res.gap_path[m.quarter_to_ord("2026Q2")] == pytest.approx(-0.85, abs=1e-9)
    # the seed (MPR) quarter's gap entering the rule is the rolled-forward value
    assert res.steps[0].quarter == "2026Q2"
    assert res.steps[0].gap == pytest.approx(-0.85, abs=1e-9)


def test_anchor_before_available_data_fails_closed():
    """Anchor at 2025Q2 has no potential-growth / GDP coverage (annual starts
    2025 but GDP quarterly only from 2025Q3) -> build raises, fail closed."""
    # 2025Q2 has no direct GDP and 2025 has no gdp_q4q4 anchor -> build_gdp_path raises.
    inp = _seed_inputs(anchor_quarter="2025Q2", anchor_value=-0.8)
    with pytest.raises(ValueError):
        m.run_model(inp, end_quarter="2028Q4")


# --------------------------------------------------------------------------- #
# ELB clamp
# --------------------------------------------------------------------------- #
def test_elb_clamp():
    """Deeply negative inflation drives the rule below ELB; output clamps at floor."""
    inp = const_inputs(core=-3.0, gdp=1.2, potential=1.2, gap_low=-5.0, gap_high=-5.0,
                       current_overnight_rate=2.25)
    res = m.run_model(inp, end_quarter="2028Q4")
    # later steps should hit the floor and never go below it
    assert min(s.rate for s in res.steps) >= 0.25 - 1e-12
    assert res.steps[-1].rate == pytest.approx(0.25, abs=1e-9)


# --------------------------------------------------------------------------- #
# Hold-at-target beyond final anchor
# --------------------------------------------------------------------------- #
def test_hold_beyond_final_anchor():
    """t+4 inflation lookups past the last known quarter hold the final value."""
    # Build inputs whose last quarterly/anchor row is 2028Q4 = 2.0, and check
    # that the path past it holds 2.0.
    quarterly = []
    # near-term quarterly through 2026Q2
    for q, v in [("2025Q3", 3.1), ("2025Q4", 2.8), ("2026Q1", 2.4), ("2026Q2", 2.1)]:
        quarterly.append(QuarterlyRow(quarter=q, core_cpi_yoy_forecast=v,
                                       total_cpi_yoy_reference=None,
                                       gdp_growth_qq_ann_forecast=1.5,
                                       anchor_type="quarterly", source_ref="t"))
    for q, v in [("2026Q4", 2.0), ("2027Q4", 2.2), ("2028Q4", 2.0)]:
        quarterly.append(QuarterlyRow(quarter=q, core_cpi_yoy_forecast=v,
                                       total_cpi_yoy_reference=None,
                                       gdp_growth_qq_ann_forecast=None,
                                       anchor_type="q4q4", source_ref="t"))
    annual = [
        AnnualRow(year=2025, potential_growth_low=2.3, potential_growth_high=2.3,
                  gdp_q4q4=None, source_ref="t"),
        AnnualRow(year=2026, potential_growth_low=0.8, potential_growth_high=1.6,
                  gdp_q4q4=1.8, source_ref="t"),
        AnnualRow(year=2027, potential_growth_low=0.8, potential_growth_high=1.8,
                  gdp_q4q4=1.4, source_ref="t"),
        AnnualRow(year=2028, potential_growth_low=1.0, potential_growth_high=2.0,
                  gdp_q4q4=1.9, source_ref="t"),
    ]
    inp = ShadowInputs(quarterly=quarterly, annual=annual, params=make_params())
    last = m.build_core_cpi_path(inp, m.quarter_to_ord("2030Q4"))
    # everything past 2028Q4 holds 2.0
    for o in range(m.quarter_to_ord("2029Q1"), m.quarter_to_ord("2030Q4") + 1):
        assert last[o] == pytest.approx(2.0, abs=1e-9)


# --------------------------------------------------------------------------- #
# Linear interpolation between Q4/Q4 anchors
# --------------------------------------------------------------------------- #
def test_linear_interpolation_midpoint():
    """2026Q2=2.1 -> 2026Q4=2.0 should put 2026Q3 at 2.05 (exact midpoint)."""
    quarterly = [
        QuarterlyRow(quarter="2026Q2", core_cpi_yoy_forecast=2.1,
                     total_cpi_yoy_reference=None, gdp_growth_qq_ann_forecast=1.5,
                     anchor_type="quarterly", source_ref="t"),
        QuarterlyRow(quarter="2026Q4", core_cpi_yoy_forecast=2.0,
                     total_cpi_yoy_reference=None, gdp_growth_qq_ann_forecast=None,
                     anchor_type="q4q4", source_ref="t"),
    ]
    annual = [AnnualRow(year=2026, potential_growth_low=0.8, potential_growth_high=1.6,
                        gdp_q4q4=1.8, source_ref="t")]
    inp = ShadowInputs(quarterly=quarterly, annual=annual, params=make_params())
    path = m.build_core_cpi_path(inp, m.quarter_to_ord("2026Q4"))
    assert path[m.quarter_to_ord("2026Q3")] == pytest.approx(2.05, abs=1e-9)


def test_linear_interpolation_three_quarter_span():
    """2027Q4=2.2 -> 2028Q4=2.0 across 4 quarters; 2028Q2 sits halfway at 2.10."""
    quarterly = [
        QuarterlyRow(quarter="2027Q4", core_cpi_yoy_forecast=2.2,
                     total_cpi_yoy_reference=None, gdp_growth_qq_ann_forecast=None,
                     anchor_type="q4q4", source_ref="t"),
        QuarterlyRow(quarter="2028Q4", core_cpi_yoy_forecast=2.0,
                     total_cpi_yoy_reference=None, gdp_growth_qq_ann_forecast=None,
                     anchor_type="q4q4", source_ref="t"),
    ]
    annual = [AnnualRow(year=2028, potential_growth_low=1.0, potential_growth_high=2.0,
                        gdp_q4q4=1.9, source_ref="t")]
    inp = ShadowInputs(quarterly=quarterly, annual=annual, params=make_params())
    path = m.build_core_cpi_path(inp, m.quarter_to_ord("2028Q4"))
    # 2027Q4=2.2, 2028Q1=2.15, 2028Q2=2.10, 2028Q3=2.05, 2028Q4=2.0
    assert path[m.quarter_to_ord("2028Q1")] == pytest.approx(2.15, abs=1e-9)
    assert path[m.quarter_to_ord("2028Q2")] == pytest.approx(2.10, abs=1e-9)
    assert path[m.quarter_to_ord("2028Q3")] == pytest.approx(2.05, abs=1e-9)


# --------------------------------------------------------------------------- #
# Constant-rate GDP fill within anchor years
# --------------------------------------------------------------------------- #
def test_gdp_constant_fill_within_year():
    quarterly = [
        QuarterlyRow(quarter="2026Q1", core_cpi_yoy_forecast=2.4,
                     total_cpi_yoy_reference=None, gdp_growth_qq_ann_forecast=1.5,
                     anchor_type="quarterly", source_ref="t"),
        QuarterlyRow(quarter="2026Q2", core_cpi_yoy_forecast=2.1,
                     total_cpi_yoy_reference=None, gdp_growth_qq_ann_forecast=1.5,
                     anchor_type="quarterly", source_ref="t"),
        QuarterlyRow(quarter="2026Q4", core_cpi_yoy_forecast=2.0,
                     total_cpi_yoy_reference=None, gdp_growth_qq_ann_forecast=None,
                     anchor_type="q4q4", source_ref="t"),
    ]
    annual = [AnnualRow(year=2026, potential_growth_low=0.8, potential_growth_high=1.6,
                        gdp_q4q4=1.8, source_ref="t")]
    inp = ShadowInputs(quarterly=quarterly, annual=annual, params=make_params())
    gdp = m.build_gdp_path(inp, m.quarter_to_ord("2026Q1"), m.quarter_to_ord("2026Q4"))
    assert gdp[m.quarter_to_ord("2026Q1")] == pytest.approx(1.5)
    assert gdp[m.quarter_to_ord("2026Q2")] == pytest.approx(1.5)
    # Q3 and Q4 (no direct value) -> year anchor 1.8
    assert gdp[m.quarter_to_ord("2026Q3")] == pytest.approx(1.8)
    assert gdp[m.quarter_to_ord("2026Q4")] == pytest.approx(1.8)


def test_potential_midpoint():
    inp = const_inputs()
    annual = [
        AnnualRow(year=2026, potential_growth_low=0.8, potential_growth_high=1.6,
                  gdp_q4q4=1.8, source_ref="t"),
    ]
    inp2 = ShadowInputs(quarterly=inp.quarterly, annual=annual + inp.annual[2:],
                        params=inp.params)
    pot = m.build_potential_path(inp2, m.quarter_to_ord("2026Q1"),
                                 m.quarter_to_ord("2026Q4"))
    for qn in range(1, 5):
        assert pot[m.quarter_to_ord(f"2026Q{qn}")] == pytest.approx(1.2)


# --------------------------------------------------------------------------- #
# Fail-closed validation
# --------------------------------------------------------------------------- #
def test_validation_rejects_bad_quarter():
    with pytest.raises(Exception):
        QuarterlyRow(quarter="2026-Q2", core_cpi_yoy_forecast=2.0,
                     total_cpi_yoy_reference=None, gdp_growth_qq_ann_forecast=None,
                     anchor_type="quarterly", source_ref="t")


def test_validation_rejects_bad_anchor_type():
    with pytest.raises(Exception):
        QuarterlyRow(quarter="2026Q2", core_cpi_yoy_forecast=2.0,
                     total_cpi_yoy_reference=None, gdp_growth_qq_ann_forecast=None,
                     anchor_type="annual", source_ref="t")


def test_validation_rejects_inverted_neutral_range():
    with pytest.raises(Exception):
        make_params(neutral_range_low=3.25, neutral_range_high=2.25)


def test_validation_rejects_out_of_bounds_anchor_value():
    with pytest.raises(Exception):
        make_params(output_gap_anchor_value=-99.0)


def test_validation_rejects_unparseable_anchor_quarter():
    with pytest.raises(Exception):
        make_params(output_gap_anchor_quarter="2025-Q4")


def test_validation_rejects_anchor_after_seed():
    """Fail closed: an anchor quarter AFTER the MPR seed quarter is rejected,
    because the gap rolls forward from the anchor to the seed (never backward)."""
    inp = const_inputs(anchor_quarter="2027Q1")  # seed is 2026Q2
    with pytest.raises(ValueError):
        m.run_model(inp, end_quarter="2028Q4")


def test_validation_rejects_out_of_bounds_rho():
    with pytest.raises(Exception):
        make_params(rho=1.5)


def test_validation_rejects_empty_source_ref():
    with pytest.raises(Exception):
        AnnualRow(year=2026, potential_growth_low=0.8, potential_growth_high=1.6,
                  gdp_q4q4=1.8, source_ref="   ")


def test_validation_rejects_no_q4q4_anchor():
    quarterly = [
        QuarterlyRow(quarter="2026Q2", core_cpi_yoy_forecast=2.1,
                     total_cpi_yoy_reference=None, gdp_growth_qq_ann_forecast=1.5,
                     anchor_type="quarterly", source_ref="t"),
    ]
    annual = [AnnualRow(year=2026, potential_growth_low=0.8, potential_growth_high=1.6,
                        gdp_q4q4=1.8, source_ref="t")]
    with pytest.raises(Exception):
        ShadowInputs(quarterly=quarterly, annual=annual, params=make_params())


# --------------------------------------------------------------------------- #
# xlsx round-trip
# --------------------------------------------------------------------------- #
def test_xlsx_roundtrip(tmp_path):
    """make_workbook -> parse_workbook reproduces the seeded params."""
    from pipeline.shadow_rate.make_workbook import build_workbook
    from pipeline.shadow_rate.inputs import parse_workbook

    xlsx = tmp_path / "rt.xlsx"
    build_workbook(str(xlsx))
    inp = parse_workbook(str(xlsx))
    assert inp.params.mpr_publication_date == date(2026, 4, 29)
    assert inp.params.verified is False
    assert inp.params.neutral_range_low == pytest.approx(2.25)
    assert inp.params.neutral_range_high == pytest.approx(3.25)
    # model runs end-to-end on the seeded workbook
    res = m.run_model(inp, end_quarter="2028Q4")
    assert res.seed_quarter == "2026Q2"
    assert res.steps[0].rate == pytest.approx(inp.params.current_overnight_rate)


# --------------------------------------------------------------------------- #
# Output sheet written back into the workbook
# --------------------------------------------------------------------------- #
def test_output_sheet_written_and_decomposition(tmp_path):
    """write_output_sheet adds an 'output' sheet (first), preserves inputs, and
    its decomposition arithmetic matches the model's rule step."""
    from openpyxl import load_workbook

    from pipeline.shadow_rate.inputs import parse_workbook
    from pipeline.shadow_rate.make_workbook import build_workbook
    from pipeline.shadow_rate.output_sheet import SHEET_NAME, write_output_sheet

    xlsx = tmp_path / "wb.xlsx"
    build_workbook(str(xlsx))
    inp = parse_workbook(str(xlsx))
    p = inp.params
    res = m.run_model(inp, end_quarter="2028Q4")

    # snapshot input-sheet values before writing the output sheet
    wb0 = load_workbook(str(xlsx))
    before = {
        name: [r for r in wb0[name].iter_rows(values_only=True)]
        for name in ("quarterly", "annual", "params")
    }
    wb0.close()

    out = write_output_sheet(str(xlsx), res, p)
    assert out.used_companion is False
    assert out.path == xlsx

    wb = load_workbook(str(xlsx))
    try:
        # output sheet exists and is first
        assert SHEET_NAME in wb.sheetnames
        assert wb.sheetnames[0] == SHEET_NAME
        # input sheets preserved (values unchanged) and still present
        for name in ("quarterly", "annual", "params"):
            assert name in wb.sheetnames
            after = [r for r in wb[name].iter_rows(values_only=True)]
            assert after == before[name]

        ws = wb[SHEET_NAME]
        # header block: UNVERIFIED DRAFT cell present (seeded workbook is FALSE)
        flat = [c.value for row in ws.iter_rows(values_only=True) for c in
                [type("X", (), {"value": v})() for v in row]]
        cells = [v for row in ws.iter_rows(values_only=True) for v in row]
        assert any(v == "UNVERIFIED DRAFT" for v in cells)
        assert any(isinstance(v, str) and "TR-119 Table 2.3" in v for v in cells)
        assert any(isinstance(v, str) and v.startswith("Run:") for v in cells)
        assert any(isinstance(v, str) and "model.py" in v for v in cells)

        # locate the table header row, then the 2026Q3 quarter would be the first
        # projected step; verify decomposition of the SEED row (2026Q2) matches.
        header_idx = None
        for i, row in enumerate(ws.iter_rows(values_only=True), start=1):
            if row and row[0] == "quarter":
                header_idx = i
                break
        assert header_idx is not None

        # first data row = seed quarter (2026Q2)
        rows = list(ws.iter_rows(min_row=header_idx + 1, values_only=True))
        seed_row = rows[0]
        assert seed_row[0] == res.seed_quarter

        seed_step = res.steps[0]
        infl_term = p.phi_pi * (seed_step.infl_tp4 - p.inflation_target)
        gap_term = p.phi_gap * seed_step.gap
        bracket = p.neutral_nominal_mid + infl_term + gap_term
        inertia = p.rho * seed_step.rate
        step_val = (1.0 - p.rho) * bracket + p.rho * seed_step.rate

        assert seed_row[1] == pytest.approx(round(seed_step.rate, 4), abs=1e-9)
        assert seed_row[6] == pytest.approx(round(infl_term, 4), abs=1e-9)
        assert seed_row[7] == pytest.approx(round(gap_term, 4), abs=1e-9)
        assert seed_row[8] == pytest.approx(round(bracket, 4), abs=1e-9)
        assert seed_row[9] == pytest.approx(round(inertia, 4), abs=1e-9)
        assert seed_row[10] == pytest.approx(round(step_val, 4), abs=1e-9)
        # the step result here equals the NEXT step's rate (no ELB binding)
        assert step_val == pytest.approx(res.steps[1].rate, abs=1e-9)
    finally:
        wb.close()


def test_output_sheet_companion_on_lock(tmp_path, monkeypatch):
    """If save raises PermissionError (workbook locked), a companion file is
    written instead and used_companion is True."""
    from pipeline.shadow_rate.inputs import parse_workbook
    from pipeline.shadow_rate.make_workbook import build_workbook
    from pipeline.shadow_rate import output_sheet as osheet

    xlsx = tmp_path / "boc_shadow_inputs_2026Q2.xlsx"
    build_workbook(str(xlsx))
    inp = parse_workbook(str(xlsx))
    res = m.run_model(inp, end_quarter="2028Q4")

    real_save = osheet.load_workbook(str(xlsx)).save  # not used; just for type
    calls = {"n": 0}
    orig_save = type(osheet.load_workbook(str(xlsx))).save

    def fake_save(self, path):
        calls["n"] += 1
        # raise only for the primary (inputs) path, succeed for companion
        if str(path).endswith("boc_shadow_inputs_2026Q2.xlsx"):
            raise PermissionError("locked by Excel")
        return orig_save(self, path)

    monkeypatch.setattr(type(osheet.load_workbook(str(xlsx))), "save", fake_save)
    out = osheet.write_output_sheet(str(xlsx), res, inp.params)
    assert out.used_companion is True
    assert out.path.name == "boc_shadow_output_2026Q2.xlsx"
    assert out.path.exists()
