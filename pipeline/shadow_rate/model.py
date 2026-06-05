"""The shadow-rate model: interpolation, gap evolution, t+4 lookup, rule iteration.

All mechanical and documented. The policy rule (ToTEM III, TR-119 Table 2.3):

    R_{t+1} = rho * R_t
              + (1 - rho) * [ R*_nom + phi_pi * (pi_hat_{t+4} - target) + phi_gap * gap_t ]

floored at the BoC's stated effective lower bound (ELB). Quarterly steps.

Inputs are merged from the punch-in workbook (see inputs.py). This module turns
the sparse MPR rows into dense quarterly paths, then iterates the rule from the
MPR quarter (R_0 = current overnight rate) forward to the workbook's
projection_end_quarter.
"""

from __future__ import annotations

from dataclasses import dataclass

from pipeline.shadow_rate.inputs import ShadowInputs


# The forward inflation-lookup distance is part of the RULE'S DEFINITION, not a
# user input. TR-119 Table 2.3's inflation term is the four-quarter-ahead mean
# (1/4)*Sum_{j=1..4} E_t pi_{t+j}, approximated here by the single t+4 forecast;
# changing it would silently redefine the rule, so it is fixed in code.
RULE_INFLATION_HORIZON_Q = 4


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


def run_model(inp: ShadowInputs, end_quarter: str | None = None) -> ShadowResult:
    """Iterate the policy rule from the MPR quarter to end_quarter inclusive.

    The seed quarter is the calendar quarter containing the MPR publication
    date. R_0 = current_overnight_rate at that quarter. The first projected step
    is the next quarter; iteration ends at end_quarter.

    ``end_quarter`` defaults to the workbook's ``projection_end_quarter`` param,
    so the horizon travels with the vintage. Callers may still override it.
    """
    p = inp.params
    if end_quarter is None:
        end_quarter = p.projection_end_quarter
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
    horizon = RULE_INFLATION_HORIZON_Q
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


# --------------------------------------------------------------------------- #
# Sensitivity band (corner reruns over published input ranges)
# --------------------------------------------------------------------------- #
@dataclass
class BandResult:
    """Per-quarter min/max envelope of the rule path across input-range corners.

    ``lo`` / ``hi`` are keyed by quarter string and span the same quarters as
    the central ``ShadowResult.steps``. ``central`` carries the central-case
    rate for convenience (lo <= central <= hi every quarter).
    """

    lo: dict[str, float]
    hi: dict[str, float]
    central: dict[str, float]


def _run_corner(
    inp: ShadowInputs,
    end_quarter: str | None,
    *,
    neutral_mid: float,
    potential_pick: str,
) -> dict[str, float]:
    """Rerun the rule path holding neutral at ``neutral_mid`` and potential at
    each year's range low/high (``potential_pick`` in {'low','high'}).

    Only the two sensitivity drivers move; core CPI, GDP anchors, the gap anchor
    and every coefficient stay at the central case. Returns {quarter: rate}.

    Implementation reuses ``run_model`` by building a shallow-modified inputs
    bundle: neutral range collapsed to the chosen midpoint, and every annual
    row's potential range collapsed to its low or high endpoint (so the
    potential-path midpoint equals that endpoint and the gap evolves
    accordingly).
    """
    p = inp.params
    params2 = p.model_copy(update={
        "neutral_range_low": neutral_mid,
        "neutral_range_high": neutral_mid,
    })
    annual2 = []
    for a in inp.annual:
        pick = a.potential_growth_low if potential_pick == "low" else a.potential_growth_high
        annual2.append(a.model_copy(update={
            "potential_growth_low": pick,
            "potential_growth_high": pick,
        }))
    inp2 = ShadowInputs(quarterly=list(inp.quarterly), annual=annual2, params=params2)
    res = run_model(inp2, end_quarter=end_quarter)
    return {s.quarter: s.rate for s in res.steps}


def run_band(inp: ShadowInputs, end_quarter: str | None = None) -> BandResult:
    """Mechanical uncertainty band from the 4 corners of the published ranges.

    Corners = {neutral_low, neutral_high} x {potential low, potential high},
    where the neutral pick is a single number applied as the neutral midpoint,
    and the potential pick is applied consistently to ALL years (each year's
    own range endpoint). Per quarter, lo/hi = min/max rate across the 4 corner
    paths.

    Sign logic (documented, not relied on by the code): lower potential -> growth
    exceeds potential more -> the output gap closes faster -> higher rates. So
    the high-rate corner pairs neutral_high with potential_low, and the low-rate
    corner pairs neutral_low with potential_high — but we take min/max over all
    four explicitly rather than assume the ordering, which is robust to the ELB
    floor flattening one corner.

    Core CPI and all other inputs stay at the central case.
    """
    p = inp.params
    if end_quarter is None:
        end_quarter = p.projection_end_quarter
    corners = []
    for neutral_mid in (p.neutral_range_low, p.neutral_range_high):
        for potential_pick in ("low", "high"):
            corners.append(_run_corner(
                inp, end_quarter,
                neutral_mid=neutral_mid, potential_pick=potential_pick,
            ))

    central = {s.quarter: s.rate for s in run_model(inp, end_quarter=end_quarter).steps}
    quarters = list(central.keys())
    lo = {q: min(c[q] for c in corners) for q in quarters}
    hi = {q: max(c[q] for c in corners) for q in quarters}
    return BandResult(lo=lo, hi=hi, central=central)


# --------------------------------------------------------------------------- #
# Annual-average GDP cross-check (coherence diagnostic)
# --------------------------------------------------------------------------- #
@dataclass
class AnnualAvgCheck:
    """One year's implied-vs-published annual-average GDP growth comparison."""

    year: int
    implied: float
    published: float | None
    diff: float | None        # implied - published (None if no published value)
    approximate: bool         # True if the prior-year level path is incomplete
    tripped: bool             # |diff| > tolerance (False when published is None)


ANNUAL_AVG_TOL = 0.15  # pp; rounding ~0.05 + within-year fill-shape slack


def annual_average_crosscheck(
    inp: ShadowInputs,
    end_quarter: str | None = None,
    tolerance: float = ANNUAL_AVG_TOL,
) -> list[AnnualAvgCheck]:
    """Compare the engine's implied annual-average GDP growth to published.

    From the constructed quarterly q/q-annualized GDP path we compound a level
    index, then compute each year's annual-average growth = mean(level over the
    4 quarters of that year) / mean(level over the 4 quarters of the prior year)
    - 1, expressed in percent.

    Honest handling of the 2025 seam: the MPR gives only 2025Q3/Q4 q/q growth, so
    the 2025 level path (the denominator for 2026's average) is incomplete. We
    construct a 2025 level path from the available quarters (treating 2025Q1/Q2
    as flat at the 2025Q2 level implied by carrying the index back through the two
    known growth rates), which makes the 2026 implied average APPROXIMATE. Years
    whose full prior-year quarterly path is constructed from anchors (2027, 2028)
    are EXACT in this sense and form the strict check; 2026 is reported but
    flagged ``approximate=True``.

    Published annual-AVERAGE growth comes from the annual sheet's
    ``gdp_annual_avg`` column (MPR Table 2). Returns one AnnualAvgCheck per
    horizon year that has a published value.
    """
    p = inp.params
    if end_quarter is None:
        end_quarter = p.projection_end_quarter
    seed_year = p.mpr_publication_date.year
    # Build the GDP path from the earliest quarterly row's year (to capture the
    # 2025 seam) through the horizon end.
    first_q_ord = min(quarter_to_ord(r.quarter) for r in inp.quarterly)
    end_ord = quarter_to_ord(end_quarter)
    gdp = build_gdp_path(inp, first_q_ord, end_ord)

    # Compound a quarterly level index. Start the index at 100 at the first
    # available quarter; each q/q-annualized rate g implies a one-quarter level
    # growth of (1 + g/100)**0.25.
    ords = sorted(gdp)
    level: dict[int, float] = {}
    lvl = 100.0
    level[ords[0]] = lvl
    for o in ords[1:]:
        g = gdp[o]
        lvl = lvl * (1.0 + g / 100.0) ** 0.25
        level[o] = lvl

    first_year = ords[0] // 4
    # year -> list of quarter levels present
    def year_levels(yr: int) -> list[float]:
        return [level[o] for o in range(yr * 4, yr * 4 + 4) if o in level]

    published_by_year = {
        a.year: a.gdp_annual_avg
        for a in inp.annual
        if getattr(a, "gdp_annual_avg", None) is not None
    }

    checks: list[AnnualAvgCheck] = []
    for yr in range(seed_year, end_ord // 4 + 1):
        prior = year_levels(yr - 1)
        cur = year_levels(yr)
        if len(cur) < 4 or not prior:
            continue
        # Approximate when the prior year's quarterly level path is incomplete
        # (fewer than 4 quarters available — the 2025 seam case for yr=2026).
        approximate = len(prior) < 4 or (yr - 1) == first_year and len(prior) < 4
        # Prior-year mean: if incomplete, use the available quarters (honest
        # approximation; flagged).
        prior_mean = sum(prior) / len(prior)
        cur_mean = sum(cur) / len(cur)
        implied = (cur_mean / prior_mean - 1.0) * 100.0
        pub = published_by_year.get(yr)
        diff = None if pub is None else implied - pub
        tripped = diff is not None and abs(diff) > tolerance
        if pub is None:
            continue
        checks.append(AnnualAvgCheck(
            year=yr, implied=round(implied, 4), published=pub,
            diff=round(diff, 4) if diff is not None else None,
            approximate=approximate, tripped=tripped,
        ))
    return checks
