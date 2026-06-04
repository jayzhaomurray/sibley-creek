"""The shadow-rate model: interpolation, gap evolution, t+4 lookup, rule iteration.

All mechanical and documented. The policy rule (ToTEM III, TR-119 Table 2.3):

    R_{t+1} = rho * R_t
              + (1 - rho) * [ R*_nom + phi_pi * (pi_hat_{t+4} - target) + phi_gap * gap_t ]

floored at the BoC's stated effective lower bound (ELB). Quarterly steps.

Inputs are merged from the punch-in workbook (see inputs.py). This module turns
the sparse MPR rows into dense quarterly paths, then iterates the rule from the
MPR quarter (R_0 = current overnight rate) forward to 2028Q4.
"""

from __future__ import annotations

from dataclasses import dataclass

from pipeline.shadow_rate.inputs import ShadowInputs


# --------------------------------------------------------------------------- #
# Quarter arithmetic helpers
# --------------------------------------------------------------------------- #
def quarter_to_ord(q: str) -> int:
    """'2026Q2' -> integer ordinal (year*4 + (quarter-1)). Monotonic in time."""
    year = int(q[:4])
    qn = int(q[5])
    return year * 4 + (qn - 1)


def ord_to_quarter(o: int) -> str:
    """Inverse of quarter_to_ord."""
    year, qn = divmod(o, 4)
    return f"{year}Q{qn + 1}"


def quarter_year(q: str) -> int:
    return int(q[:4])


def quarter_of_date(d) -> str:
    """Calendar quarter containing date d, as 'YYYYQn'."""
    qn = (d.month - 1) // 3 + 1
    return f"{d.year}Q{qn}"


# --------------------------------------------------------------------------- #
# Path construction
# --------------------------------------------------------------------------- #
def build_core_cpi_path(inp: ShadowInputs, last_ord: int) -> dict[int, float]:
    """Dense quarterly core-CPI y/y path keyed by quarter ordinal.

    Quarterly rows are placed directly. Between the last directly-given
    quarterly value and the first q4q4 anchor (and between successive anchors)
    we linearly interpolate quarter-by-quarter. Beyond the final anchor we hold
    at the final anchor value. Coverage runs through last_ord inclusive.
    """
    # Known points (ordinal -> value), from every quarterly row regardless of
    # anchor_type (both 'quarterly' and 'q4q4' rows are true quarterly obs).
    known: dict[int, float] = {}
    for r in inp.quarterly:
        known[quarter_to_ord(r.quarter)] = r.core_cpi_yoy_forecast

    return _interp_hold(known, last_ord)


def _interp_hold(known: dict[int, float], last_ord: int) -> dict[int, float]:
    """Fill a dense path: piecewise-linear between known points, hold past the last.

    Quarters before the first known point are not produced (the model never
    looks earlier than the MPR quarter, and the t+4 lookups only reach forward).
    """
    if not known:
        raise ValueError("no known points to interpolate")
    ks = sorted(known)
    first, last_known = ks[0], ks[-1]
    end = max(last_ord, last_known)

    out: dict[int, float] = {}
    for o in range(first, end + 1):
        if o in known:
            out[o] = known[o]
            continue
        if o > last_known:
            out[o] = known[last_known]  # hold
            continue
        # find bracketing known points
        lo = max(k for k in ks if k <= o)
        hi = min(k for k in ks if k >= o)
        span = hi - lo
        frac = (o - lo) / span
        out[o] = known[lo] + frac * (known[hi] - known[lo])
    return out


def build_gdp_path(inp: ShadowInputs, first_ord: int, last_ord: int) -> dict[int, float]:
    """Dense quarterly GDP q/q-annualized path keyed by quarter ordinal.

    Direct q/q annualized where the quarterly sheet gives it. Missing quarters
    of a calendar year are filled by the **residual rule** so the year stays
    consistent with its published Q4/Q4 anchor:

        remaining_rate = (4*q4q4_anchor - sum(direct_rates_this_year)) / n_missing

    applied equally to every missing quarter of that year. This rests on the
    arithmetic-mean approximation of the compounding identity: a year's Q4/Q4
    growth ~= the mean of its four q/q-annualized rates (exact under summation,
    a close approximation under compounding). So filling the missing quarters at
    the residual makes the four quarters average the anchor.

    Years with NO direct quarters reduce to the old constant fill (the residual
    with zero known terms is the anchor itself) — this is the single general rule.

    Fail closed: a year that needs filling but has no Q4/Q4 anchor raises. If a
    year has all four quarters direct (n_missing == 0) the anchor is ignored.
    """
    direct: dict[int, float] = {}
    for r in inp.quarterly:
        if r.gdp_growth_qq_ann_forecast is not None:
            direct[quarter_to_ord(r.quarter)] = r.gdp_growth_qq_ann_forecast

    year_q4q4: dict[int, float] = {}
    for a in inp.annual:
        if a.gdp_q4q4 is not None:
            year_q4q4[a.year] = a.gdp_q4q4

    # Per-year residual fill for missing quarters: sum the year's direct rates
    # over ALL four quarters of the year (not just those in the build window),
    # and count missing quarters over all four, so the residual matches the
    # anchor identity regardless of where [first_ord, last_ord] is clipped.
    year_residual: dict[int, float] = {}
    for o in range(first_ord, last_ord + 1):
        if o in direct:
            continue
        yr = o // 4
        if yr in year_residual:
            continue
        year_start = yr * 4
        known_sum = 0.0
        n_missing = 0
        for qo in range(year_start, year_start + 4):
            if qo in direct:
                known_sum += direct[qo]
            else:
                n_missing += 1
        if n_missing == 0:
            # All four quarters direct: the anchor is ignored (cannot be needed
            # — this branch only runs for a missing quarter, so n_missing >= 1).
            continue
        if yr not in year_q4q4:
            raise ValueError(
                f"no GDP growth available for {ord_to_quarter(o)}: a missing "
                f"quarter needs filling but year {yr} has no Q4/Q4 anchor"
            )
        year_residual[yr] = (4.0 * year_q4q4[yr] - known_sum) / n_missing

    out: dict[int, float] = {}
    for o in range(first_ord, last_ord + 1):
        if o in direct:
            out[o] = direct[o]
        else:
            out[o] = year_residual[o // 4]
    return out


def build_potential_path(inp: ShadowInputs, first_ord: int, last_ord: int) -> dict[int, float]:
    """Dense quarterly potential-growth path = midpoint of that year's range."""
    year_mid: dict[int, float] = {a.year: a.potential_growth_mid for a in inp.annual}
    out: dict[int, float] = {}
    for o in range(first_ord, last_ord + 1):
        yr = o // 4
        if yr not in year_mid:
            raise ValueError(
                f"no potential-growth range for year {yr} "
                f"(quarter {ord_to_quarter(o)})"
            )
        out[o] = year_mid[yr]
    return out


# --------------------------------------------------------------------------- #
# Rule iteration
# --------------------------------------------------------------------------- #
@dataclass
class PathStep:
    """One projected quarter of the shadow path."""

    quarter: str
    rate: float           # R_t at this quarter (the policy rate)
    gap: float            # output gap entering the rule at this quarter
    infl_tp4: float       # pi_hat_{t+4} used in the rule update producing the NEXT rate
    gdp_growth: float     # q/q annualized GDP growth applied this quarter
    potential: float      # potential growth this quarter


@dataclass
class ShadowResult:
    seed_quarter: str
    seed_rate: float
    steps: list[PathStep]            # projected quarters (seed quarter + forward path)
    core_cpi_path: dict[int, float]
    gdp_path: dict[int, float]
    potential_path: dict[int, float]
    gap_path: dict[int, float]


def run_model(inp: ShadowInputs, end_quarter: str = "2028Q4") -> ShadowResult:
    """Iterate the policy rule from the MPR quarter to end_quarter inclusive.

    The seed quarter is the calendar quarter containing the MPR publication
    date. R_0 = current_overnight_rate at that quarter. The first projected step
    is the next quarter; iteration ends at end_quarter.
    """
    p = inp.params
    seed_q = quarter_of_date(p.mpr_publication_date)
    seed_ord = quarter_to_ord(seed_q)
    end_ord = quarter_to_ord(end_quarter)
    if end_ord <= seed_ord:
        raise ValueError(f"end_quarter {end_quarter} not after seed {seed_q}")

    # Output-gap anchor: the BoC staff output-gap estimate at its last published
    # quarter. The gap path STARTS here and rolls forward mechanically to the
    # seed (MPR) quarter and on through the horizon. Fail closed: the anchor must
    # not be after the seed quarter (we roll forward, never back).
    anchor_q = p.output_gap_anchor_quarter
    anchor_ord = quarter_to_ord(anchor_q)
    if anchor_ord > seed_ord:
        raise ValueError(
            f"output_gap_anchor_quarter {anchor_q} is after the seed quarter "
            f"{seed_q}; the gap rolls forward from the anchor, so the anchor must "
            f"be at or before the seed."
        )

    # Inflation must be available out to the LAST update's t+4 lookup. The final
    # rate produced is at end_ord, set by the update at (end_ord - 1) which reads
    # inflation at (end_ord - 1 + converge). Build with headroom.
    horizon = p.inflation_converge_quarters
    # Need inflation out to the terminal quarter's own t+4 lookup (for the
    # reported infl_tp4 column), which is the furthest forward read.
    last_infl_ord = end_ord + horizon
    core = build_core_cpi_path(inp, last_infl_ord)
    # GDP / potential must cover from the anchor quarter forward, since the gap
    # roll-forward reads growth and potential at every quarter from the anchor on.
    # build_*_path raise (fail closed) if a quarter is not covered by the data.
    gdp = build_gdp_path(inp, anchor_ord, end_ord)
    potential = build_potential_path(inp, anchor_ord, end_ord)

    # Gap path: seed at the published anchor quarter = anchor value; evolve by
    # gap_{t+1} = gap_t + (gdp_growth_{t+1} - potential_{t+1})/4 — the gap at
    # t+1 reflects growth DURING quarter t+1 relative to potential. Rolling
    # forward from the anchor through the seed quarter and on to end_ord.
    gap_path: dict[int, float] = {anchor_ord: p.output_gap_anchor_value}
    for o in range(anchor_ord, end_ord):
        gap_path[o + 1] = gap_path[o] + (gdp[o + 1] - potential[o + 1]) / 4.0

    # Rate iteration. R_0 = the actual overnight rate at the MPR quarter.
    steps: list[PathStep] = []
    seed_rate = p.current_overnight_rate
    rate = seed_rate
    for o in range(seed_ord, end_ord + 1):
        # core path was built with headroom out to the last update's t+4 lookup,
        # so this is always present (held at the final anchor past the horizon).
        infl_tp4 = core[o + horizon]
        steps.append(
            PathStep(
                quarter=ord_to_quarter(o),
                rate=rate,
                gap=gap_path[o],
                infl_tp4=infl_tp4,
                gdp_growth=gdp[o],
                potential=potential[o],
            )
        )
        if o < end_ord:
            rate = _rule_step(
                rate=rate,
                infl_tp4=infl_tp4,
                gap=gap_path[o],
                p=p,
            )

    return ShadowResult(
        seed_quarter=seed_q,
        seed_rate=seed_rate,
        steps=steps,
        core_cpi_path=core,
        gdp_path=gdp,
        potential_path=potential,
        gap_path=gap_path,
    )


def _rule_step(rate: float, infl_tp4: float, gap: float, p) -> float:
    """One application of the (floored) policy rule."""
    target_level = (
        p.neutral_nominal_mid
        + p.phi_pi * (infl_tp4 - p.inflation_target)
        + p.phi_gap * gap
    )
    raw = p.rho * rate + (1.0 - p.rho) * target_level
    return max(raw, p.elb_floor)
