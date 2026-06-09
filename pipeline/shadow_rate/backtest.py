"""Shadow-rate backtest: run the ToTEM III rule on historical MPR vintages and
score the rule-implied paths against realized overnight-rate history.

This is an *informational* tool, not a publication gate. It takes the hand
transcribed historical MPR vintage dicts (``pipeline.shadow_rate.vintages``),
plus the current live workbook, runs each through the read-only engine
(``model.run_model``), and computes forecast-skill metrics versus a random-walk
benchmark at horizons of 1, 2, 4 and 8 quarters.

The engine (``inputs.py`` / ``model.py``) is reused read-only. This module only
adapts the vintage dicts into ``ShadowInputs`` and scores the resulting paths;
it never mutates the engine's behaviour.

Vintage dict schema (FIXED — the transcription agents emit exactly this):

    {
      "mpr_date": "2022-04-13",                # ISO publication date
      "projection_end_quarter": "2024Q4",
      "neutral_range": (2.0, 3.0),
      "output_gap_range": (-0.75, 0.25),
      "output_gap_quarter": "2022Q1",          # quarter the gap statement refers to
      "current_overnight_rate": 1.0,           # target ON on the MPR date (post-decision)
      "quarterly": [                            # sparse; near-term + Q4/Q4 anchor rows
        {"quarter": "2022Q1", "core_cpi_yoy": 3.2, "total_cpi_yoy": 5.8, "gdp_qq_ann": 3.0},
        {"quarter": "2022Q4", "core_cpi_yoy": 2.8, "total_cpi_yoy": 4.5},
      ],
      "annual": [
        {"year": 2022, "potential_low": 1.2, "potential_high": 2.0,
         "gdp_q4q4": 3.8, "gdp_annual_avg": 4.2},
      ],
      "core_concept": "trim_median_avg",
      "source_url": "https://...",
      "notes": "",
    }

Market-expectation benchmark (MPS)
----------------------------------
Alongside the rule and the random-walk benchmark, each MPR vintage is scored
against the Bank of Canada's Market Participants Survey (MPS) median expected
overnight-rate path.

- Source: https://www.bankofcanada.ca/publications/market-participants-survey/
  (transcribed in ``vintages/market_paths.py``). The MPS polls ~30 market
  participants quarterly on their policy-rate expectations; the Bank publishes
  the median path. The survey programme launched with the 2023Q1 survey, so
  vintages before then have no market path.
- Matching convention: a vintage is paired with the MPS of the SAME calendar
  quarter as its MPR (e.g. the Apr-2024 MPR -> the 2024Q1 survey). The MPS is
  released ~2 weeks AFTER the corresponding MPR, so the survey already reflects
  that MPR's decision and projection. This is a small information advantage in
  the survey's favour — the comparison is deliberately stacked against the rule.
- The sparse published survey points are interpolated LINEARLY across quarter
  ordinals (no extrapolation beyond the published span) to evaluate the market
  expectation at seed+h. ``MAE_market`` and ``skill_rule_vs_market`` =
  MAE_rule / MAE_market are computed ONLY over the vintage-horizon cells where
  both a matched market value and a realized actual exist (``n_market``), so the
  ratio is like-for-like; ``MAE_rule`` over the full random-walk subset is
  unchanged.
- Framing: ``skill_rule_vs_market`` answers whether the mechanical ToTEM III
  rule adds information BEYOND market expectations. A value >= 1 means the
  survey's median already matches or beats the rule, so the rule does not add
  forecasting value over simply reading the market — which is the expected
  result, since the survey is a direct, post-decision forecast of the policy
  rate while the rule is a mechanical mapping from the MPR's macro projections.

CLI:
    python -m pipeline.shadow_rate.backtest
"""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

import pandas as pd

from pipeline.shadow_rate.inputs import (
    AnnualRow,
    Params,
    QuarterlyRow,
    ShadowInputs,
)
from pipeline.shadow_rate.model import (
    ShadowResult,
    ord_to_quarter,
    quarter_of_date,
    quarter_to_ord,
    run_model,
)
from pipeline.shadow_rate.vintages import ALL_VINTAGES

try:
    from pipeline.shadow_rate.vintages.market_paths import MARKET_PATHS
except Exception as _exc:  # missing/broken transcription -> backtest still runs
    print(f"[backtest] no MPS market paths available: "
          f"{type(_exc).__name__}: {_exc}")
    MARKET_PATHS = []


PROJECT_ROOT = Path(__file__).parents[2]
WORKBOOK_DIR = PROJECT_ROOT / "work" / "research" / "shadow_rate"
OUT_DATA = PROJECT_ROOT / "data" / "processed"
ACTUAL_CSV = PROJECT_ROOT / "data" / "processed" / "overnight_rate_target.csv"

OUT_CHART_DIR = WORKBOOK_DIR / "backtest"
BACKTEST_CSV = OUT_DATA / "boc_shadow_backtest.csv"
BACKTEST_META = OUT_DATA / "boc_shadow_backtest.meta.json"

HORIZONS = (1, 2, 4, 8)
DIRECTION_HORIZON = 2  # quarters; hit-rate uses the seed+2 move


# --------------------------------------------------------------------------- #
# Vintage dict -> ShadowInputs adapter
# --------------------------------------------------------------------------- #
def vintage_to_inputs(d: dict) -> ShadowInputs:
    """Construct a validated ``ShadowInputs`` from a historical vintage dict.

    Maps the compact vintage schema onto the engine's pydantic models exactly:

    - ``neutral_range`` (lo, hi) -> ``neutral_range_low`` / ``neutral_range_high``
    - ``output_gap_range`` midpoint -> ``output_gap_anchor_value``, anchored at
      ``output_gap_quarter`` (``output_gap_anchor_quarter``)
    - quarterly ``core_cpi_yoy`` -> ``core_cpi_yoy_forecast``,
      ``total_cpi_yoy`` -> ``total_cpi_yoy_reference``,
      ``gdp_qq_ann`` -> ``gdp_growth_qq_ann_forecast``
    - ``anchor_type`` is inferred: a quarter ending in Q4 is a ``q4q4`` anchor,
      otherwise ``quarterly`` (matches how the engine consumes the rows).
    - annual ``potential_low``/``potential_high``/``gdp_q4q4``/``gdp_annual_avg``
      pass through directly.

    ``verified=True`` is set unconditionally: this is an informational backtest,
    not a publication gate, so the unverified-watermark gate does not apply. The
    engine's fail-closed pydantic validation remains the backstop for bad data.

    Missing optional fields are tolerated (default to ``None``); missing required
    fields raise via pydantic, which the caller (``run_all``) catches and skips.
    """
    src = d.get("source_url", "") or d.get("notes", "") or "historical MPR vintage"

    # GDP-only rows: some MPR tables print recent-quarter GDP with no CPI column.
    # QuarterlyRow requires a core value, but the rule never READS core for
    # quarters before the seed (t+4 lookups start at seed+4) or before the first
    # real core point (interpolation doesn't produce earlier quarters). So for
    # rows missing core that sit strictly before BOTH, fill a placeholder equal
    # to the first real core value — provably never consumed by the rule.
    # A GDP-only row at or after either boundary is a data problem: fail closed.
    from pipeline.shadow_rate.model import quarter_of_date, quarter_to_ord
    from datetime import date as _date

    rows = d.get("quarterly", [])
    seed_ord = quarter_to_ord(quarter_of_date(_date.fromisoformat(d["mpr_date"])))
    core_ords = [quarter_to_ord(str(r["quarter"]).strip())
                 for r in rows if r.get("core_cpi_yoy") is not None]
    if not core_ords:
        raise ValueError(f"vintage {d.get('mpr_date')}: no core CPI values at all")
    first_core_ord = min(core_ords)
    first_core_val = next(r["core_cpi_yoy"] for r in rows
                          if r.get("core_cpi_yoy") is not None
                          and quarter_to_ord(str(r["quarter"]).strip()) == first_core_ord)

    quarterly: list[QuarterlyRow] = []
    for r in rows:
        q = str(r["quarter"]).strip()
        anchor = "q4q4" if q[5] == "4" else "quarterly"
        core = r.get("core_cpi_yoy")
        if core is None:
            if quarter_to_ord(q) < min(seed_ord, first_core_ord):
                core = first_core_val  # pre-seed placeholder, never read by the rule
            else:
                raise ValueError(
                    f"vintage {d.get('mpr_date')}: GDP-only row at {q} is not "
                    f"strictly before the seed and first core point — cannot "
                    f"safely placeholder its core value"
                )
        quarterly.append(
            QuarterlyRow(
                quarter=q,
                core_cpi_yoy_forecast=core,
                total_cpi_yoy_reference=r.get("total_cpi_yoy"),
                gdp_growth_qq_ann_forecast=r.get("gdp_qq_ann"),
                anchor_type=anchor,
                source_ref=src,
            )
        )

    annual: list[AnnualRow] = []
    for a in d.get("annual", []):
        annual.append(
            AnnualRow(
                year=int(a["year"]),
                potential_growth_low=a["potential_low"],
                potential_growth_high=a["potential_high"],
                gdp_q4q4=a.get("gdp_q4q4"),
                gdp_annual_avg=a.get("gdp_annual_avg"),
                source_ref=src,
            )
        )

    neutral_lo, neutral_hi = d["neutral_range"]
    gap_lo, gap_hi = d["output_gap_range"]
    gap_mid = (gap_lo + gap_hi) / 2.0

    params = Params(
        mpr_publication_date=date.fromisoformat(d["mpr_date"]),
        projection_end_quarter=d["projection_end_quarter"],
        current_overnight_rate=d["current_overnight_rate"],
        output_gap_anchor_quarter=d["output_gap_quarter"],
        output_gap_anchor_value=gap_mid,
        neutral_range_low=neutral_lo,
        neutral_range_high=neutral_hi,
        verified=True,
    )

    return ShadowInputs(quarterly=quarterly, annual=annual, params=params)


# --------------------------------------------------------------------------- #
# Live workbook (current vintage)
# --------------------------------------------------------------------------- #
def _newest_workbook() -> Path | None:
    """Newest punch-in workbook, or None if none exist. Ignores ``~$`` locks."""
    candidates = sorted(
        p for p in WORKBOOK_DIR.glob("boc_shadow_inputs_*.xlsx")
        if not p.name.startswith("~$")
    )
    return candidates[-1] if candidates else None


def _live_vintage_dict(inp: ShadowInputs, xlsx: Path) -> dict:
    """A minimal vintage-style dict describing the live workbook, for reporting.

    Only the fields the backtest reporting / CSV uses are populated; this is a
    label record, not a full transcription.
    """
    p = inp.params
    return {
        "mpr_date": p.mpr_publication_date.isoformat(),
        "projection_end_quarter": p.projection_end_quarter,
        "neutral_range": (p.neutral_range_low, p.neutral_range_high),
        "output_gap_range": (p.output_gap_anchor_value, p.output_gap_anchor_value),
        "output_gap_quarter": p.output_gap_anchor_quarter,
        "current_overnight_rate": p.current_overnight_rate,
        "source_url": str(xlsx),
        "notes": f"live workbook {xlsx.name}",
        "_live": True,
    }


def run_all() -> list[tuple[dict, ShadowResult]]:
    """Run every vintage (historical + live workbook) through the engine.

    Returns a list of ``(vintage_dict, ShadowResult)`` pairs. A vintage that
    fails validation or model construction prints its error and is skipped
    (the run continues). The live current-vintage workbook is loaded via
    ``inputs.parse_workbook`` (newest ``boc_shadow_inputs_*.xlsx``, ignoring
    ``~$`` locks) and appended last; if no workbook is present that step is
    silently skipped.
    """
    out: list[tuple[dict, ShadowResult]] = []

    for d in ALL_VINTAGES:
        label = d.get("mpr_date", "<unknown>")
        if d.get("exclude"):
            print(f"[backtest] excluding vintage {label}: {d.get('exclude_reason', 'flagged')}")
            continue
        try:
            inp = vintage_to_inputs(d)
            res = run_model(inp)
        except Exception as exc:
            print(f"[backtest] skipping vintage {label}: {type(exc).__name__}: {exc}")
            continue
        out.append((d, res))

    # Live current vintage from the newest workbook.
    xlsx = _newest_workbook()
    if xlsx is not None:
        # Imported lazily so the historical path never needs the workbook parser.
        from pipeline.shadow_rate.inputs import parse_workbook

        try:
            inp = parse_workbook(xlsx)
            res = run_model(inp)
            out.append((_live_vintage_dict(inp, xlsx), res))
        except Exception as exc:
            print(f"[backtest] skipping live workbook {xlsx.name}: "
                  f"{type(exc).__name__}: {exc}")
    else:
        print(f"[backtest] no live workbook found in {WORKBOOK_DIR}; "
              f"running historical vintages only")

    return out


# --------------------------------------------------------------------------- #
# Realized overnight-rate series (quarter-end sampling)
# --------------------------------------------------------------------------- #
def load_actual_by_quarter(csv_path: Path = ACTUAL_CSV) -> dict[int, float]:
    """Realized overnight-rate target sampled at quarter-END, keyed by ordinal.

    The source CSV is monthly (date,value). For each calendar quarter we take
    the value of its last available month (quarter-end), which is the policy
    rate in effect at the close of the quarter — the natural comparison point
    for a quarter-indexed projection.
    """
    df = pd.read_csv(csv_path)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"]).sort_values("date")

    by_q: dict[int, tuple[pd.Timestamp, float]] = {}
    for ts, val in zip(df["date"], df["value"]):
        qn = (ts.month - 1) // 3 + 1
        o = ts.year * 4 + (qn - 1)
        prev = by_q.get(o)
        if prev is None or ts > prev[0]:
            by_q[o] = (ts, float(val))
    return {o: v for o, (_, v) in by_q.items()}


# --------------------------------------------------------------------------- #
# Market-expectation paths (Bank of Canada Market Participants Survey)
# --------------------------------------------------------------------------- #
# Matching convention: each MPR vintage is paired with the MPS of the SAME
# calendar quarter (e.g. the Apr-2024 MPR -> the 2024Q1 survey). The MPS is
# published ~2 weeks AFTER the corresponding MPR, so the survey's median path
# already reflects that MPR's decision and projection — a small information
# advantage in the market path's favour, noted in the methodology section.
# Vintages before the first published survey (2023Q1) have no market path.
def _surveys_by_quarter() -> dict[str, dict]:
    """MARKET_PATHS keyed by survey reference quarter ('YYYYQn' -> record)."""
    return {rec["survey"]: rec for rec in MARKET_PATHS}


def market_path_by_ord(rec: dict) -> dict[int, float]:
    """Dense quarterly median-rate path (ordinal -> rate) from a sparse survey.

    The MPS publishes a sparse set of (quarter, median-rate) points. We
    interpolate LINEARLY across quarter ordinals between consecutive published
    points and evaluate at every integer quarter in the published span. Quarters
    before the first point or after the last point are NOT extrapolated (the
    survey makes no claim there), so a horizon falling outside the published span
    simply has no market value and is dropped from MAE_market.

    Returns {} for an empty/degenerate path.
    """
    pts = sorted(
        (quarter_to_ord(q), float(r)) for q, r in rec.get("path", [])
    )
    if not pts:
        return {}
    dense: dict[int, float] = {}
    for (o0, r0), (o1, r1) in zip(pts, pts[1:]):
        span = o1 - o0
        for o in range(o0, o1):
            frac = (o - o0) / span if span else 0.0
            dense[o] = r0 + (r1 - r0) * frac
        dense[o1] = r1
    # Single-point path: just that point.
    dense.setdefault(pts[0][0], pts[0][1])
    return dense


def match_market_path(vintage: dict, surveys: dict[str, dict]) -> dict | None:
    """The MPS record matching a vintage's MPR quarter, or None if none exists.

    The vintage's MPR date determines its calendar quarter; we look up the survey
    of that same quarter. The live workbook (``_live``) is never matched (its
    seed quarter may post-date the latest survey).
    """
    if vintage.get("_live"):
        return None
    mpr_date = vintage.get("mpr_date")
    if not mpr_date:
        return None
    from datetime import date as _date

    try:
        q = quarter_of_date(_date.fromisoformat(mpr_date))
    except (ValueError, TypeError):
        return None  # non-ISO / synthetic label -> no match
    return surveys.get(q)


# --------------------------------------------------------------------------- #
# Metrics
# --------------------------------------------------------------------------- #
def _implied_by_ord(res: ShadowResult) -> dict[int, float]:
    """Rule-implied rate keyed by quarter ordinal, over the projected path."""
    return {quarter_to_ord(s.quarter): s.rate for s in res.steps}


def compute_metrics(
    pairs: list[tuple[dict, ShadowResult]],
    actual_by_q: dict[int, float],
    surveys: dict[str, dict] | None = None,
) -> pd.DataFrame:
    """Per-horizon forecast-skill metrics across the supplied vintage paths.

    For each vintage with seed ordinal ``s`` and each horizon ``h``:

      - implied(s+h)  : rule-implied rate at the projected quarter s+h
      - actual(s+h)   : realized quarter-end rate at s+h (skip if unavailable)
      - rule error    : implied(s+h) - actual(s+h)
      - random-walk   : the no-change forecast holds actual(s) flat, so its
                        error is actual(s) - actual(s+h)
      - market(s+h)   : the matched MPS median path interpolated at s+h, if a
                        same-quarter survey exists and s+h lies in its published
                        span (else this vintage-horizon has no market value)

    Aggregated per horizon over the vintages where both actual(s) and
    actual(s+h) exist:

      - bias        : mean rule error
      - mae         : mean |rule error|
      - mae_rw      : mean |random-walk error|
      - skill       : mae / mae_rw   (< 1 means the rule beats random walk)
      - n           : vintages contributing (rule-vs-rw subset)
      - mae_market  : mean |market error| over the cells where a matched market
                      value exists AND actual(s+h) exists
      - mae_rule_m  : mean |rule error| over that SAME market-available subset
                      (so the ratio below is a like-for-like comparison)
      - skill_rule_vs_market : mae_rule_m / mae_market  (< 1 means the rule beats
                      the market's median expectation on the shared cells)
      - n_market    : cells contributing to the market comparison
      - dir_hit     : directional hit-rate at horizon DIRECTION_HORIZON only —
                      sign(implied(s+H) - seed_rate) vs sign(actual(s+H) -
                      actual(s)); blank for other horizons.

    ``surveys`` maps survey quarter -> MPS record (``_surveys_by_quarter()``);
    when None (or empty) the market columns are all NaN/0 and the rule-vs-rw
    metrics are unchanged.

    Returns a tidy DataFrame, one row per horizon.
    """
    surveys = surveys or {}
    # Pre-compute, per vintage, its matched dense market path (ord -> rate).
    market_dense: dict[int, dict[int, float]] = {}
    for i, (d, _res) in enumerate(pairs):
        rec = match_market_path(d, surveys)
        market_dense[i] = market_path_by_ord(rec) if rec else {}
    # Pre-compute directional hit-rate at the fixed DIRECTION_HORIZON.
    dir_hits = 0
    dir_total = 0
    for _d, res in pairs:
        s = quarter_to_ord(res.seed_quarter)
        implied = _implied_by_ord(res)
        tgt = s + DIRECTION_HORIZON
        if s not in actual_by_q or tgt not in actual_by_q or tgt not in implied:
            continue
        seed_rate = res.seed_rate
        implied_move = implied[tgt] - seed_rate
        actual_move = actual_by_q[tgt] - actual_by_q[s]
        # A flat actual move (no policy change) is a hit only if the rule also
        # implied no move; use sign equality including the zero case.
        if _sign(implied_move) == _sign(actual_move):
            dir_hits += 1
        dir_total += 1
    dir_rate = (dir_hits / dir_total) if dir_total else float("nan")

    rows = []
    for h in HORIZONS:
        errs: list[float] = []
        rw_errs: list[float] = []
        # Market comparison subset: cells where a matched market value AND the
        # realized actual both exist. We collect the rule error and market error
        # on the SAME cells so the ratio is like-for-like.
        m_rule_errs: list[float] = []
        m_mkt_errs: list[float] = []
        for i, (_d, res) in enumerate(pairs):
            s = quarter_to_ord(res.seed_quarter)
            implied = _implied_by_ord(res)
            tgt = s + h
            if tgt not in implied:
                continue
            if s not in actual_by_q or tgt not in actual_by_q:
                continue
            rule_err = implied[tgt] - actual_by_q[tgt]
            errs.append(rule_err)
            rw_errs.append(actual_by_q[s] - actual_by_q[tgt])
            mkt = market_dense.get(i, {})
            if tgt in mkt:
                m_rule_errs.append(rule_err)
                m_mkt_errs.append(mkt[tgt] - actual_by_q[tgt])
        n = len(errs)
        n_market = len(m_mkt_errs)
        mae_market = (sum(abs(e) for e in m_mkt_errs) / n_market) if n_market else float("nan")
        mae_rule_m = (sum(abs(e) for e in m_rule_errs) / n_market) if n_market else float("nan")
        skill_rvm = (mae_rule_m / mae_market) if (n_market and mae_market > 0) else float("nan")
        if n == 0:
            rows.append({
                "horizon_q": h, "n": 0, "bias": float("nan"),
                "mae": float("nan"), "mae_rw": float("nan"),
                "skill": float("nan"),
                "mae_market": mae_market, "mae_rule_m": mae_rule_m,
                "skill_rule_vs_market": skill_rvm, "n_market": n_market,
                "dir_hit_rate": dir_rate if h == DIRECTION_HORIZON else float("nan"),
            })
            continue
        mae = sum(abs(e) for e in errs) / n
        mae_rw = sum(abs(e) for e in rw_errs) / n
        bias = sum(errs) / n
        skill = (mae / mae_rw) if mae_rw > 0 else float("nan")
        rows.append({
            "horizon_q": h,
            "n": n,
            "bias": bias,
            "mae": mae,
            "mae_rw": mae_rw,
            "skill": skill,
            "mae_market": mae_market,
            "mae_rule_m": mae_rule_m,
            "skill_rule_vs_market": skill_rvm,
            "n_market": n_market,
            "dir_hit_rate": dir_rate if h == DIRECTION_HORIZON else float("nan"),
        })
    return pd.DataFrame(rows)


def _sign(x: float) -> int:
    """Sign with a small dead-band so float noise around zero reads as no-move."""
    if x > 1e-9:
        return 1
    if x < -1e-9:
        return -1
    return 0


# --------------------------------------------------------------------------- #
# Long-format path frame (for CSV)
# --------------------------------------------------------------------------- #
def paths_long_frame(pairs: list[tuple[dict, ShadowResult]]) -> pd.DataFrame:
    """Long-format frame: one row per (vintage, projected quarter, implied rate)."""
    records = []
    for d, res in pairs:
        vintage_date = d.get("mpr_date", res.seed_quarter)
        for s in res.steps:
            records.append({
                "vintage_date": vintage_date,
                "quarter": s.quarter,
                "implied_rate": round(s.rate, 4),
            })
    return pd.DataFrame(records, columns=["vintage_date", "quarter", "implied_rate"])


# --------------------------------------------------------------------------- #
# Printing
# --------------------------------------------------------------------------- #
def print_vintage_lines(pairs: list[tuple[dict, ShadowResult]]) -> None:
    print("=== Shadow-rate backtest: per-vintage paths ===")
    if not pairs:
        print("  (no vintages — neither fragments nor a live workbook were found)")
        print()
        return
    for d, res in pairs:
        vd = d.get("mpr_date", "?")
        live = " [live]" if d.get("_live") else ""
        print(f"  {vd}{live}  seed {res.seed_quarter} @ {res.seed_rate:.2f}%  "
              f"->  {res.steps[-1].quarter} terminal implied "
              f"{res.steps[-1].rate:.2f}%")
    print()


def print_metrics(metrics: pd.DataFrame) -> None:
    print("=== Forecast-skill metrics (rule vs random walk vs MPS market) ===")
    has_market = "mae_market" in metrics.columns
    print(f"{'h(q)':>5}{'n':>5}{'bias':>9}{'MAE':>9}{'MAE_rw':>9}"
          f"{'skill':>9}{'MAE_mkt':>9}{'sk_vs_mkt':>10}{'n_mkt':>6}{'dir_hit':>9}")
    print("-" * 80)
    for _, r in metrics.iterrows():
        def f(v, w=9, p=3):
            return (" " * w) if pd.isna(v) else f"{v:>{w}.{p}f}"
        dir_s = "" if pd.isna(r["dir_hit_rate"]) else f"{r['dir_hit_rate']:>9.2f}"
        dir_s = dir_s if dir_s else " " * 9
        mae_mkt = f(r["mae_market"]) if has_market else " " * 9
        sk_mkt = f(r["skill_rule_vs_market"], w=10) if has_market else " " * 10
        n_mkt = (f"{int(r['n_market']):>6}" if has_market and not pd.isna(r["n_market"])
                 else " " * 6)
        print(f"{int(r['horizon_q']):>5}{int(r['n']):>5}"
              f"{f(r['bias'])}{f(r['mae'])}{f(r['mae_rw'])}{f(r['skill'])}"
              f"{mae_mkt}{sk_mkt}{n_mkt}{dir_s}")
    print()
    print("skill = MAE_rule / MAE_rw (<1 beats random walk). bias = mean "
          f"(implied - actual). dir_hit at h={DIRECTION_HORIZON} only.")
    print("MAE_mkt = MAE of the matched MPS median path; sk_vs_mkt = "
          "MAE_rule / MAE_mkt on the shared (market-available) cells only "
          "(<1 means the rule beats the survey's median expectation); "
          "n_mkt = cells in that subset.")
    print()


# --------------------------------------------------------------------------- #
# CSV + sidecar
# --------------------------------------------------------------------------- #
def write_backtest_csv(long_df: pd.DataFrame) -> tuple[Path, Path]:
    """Write the long-format path CSV + a hand-built .meta.json (ADR-0002 shape).

    ``write_series`` derives the reference period from a ``date`` column and is
    geared to a single date/value series; the backtest CSV is a long
    (vintage_date, quarter, implied_rate) frame. We therefore write the CSV
    directly and hand-build a sidecar consistent with the SeriesMeta schema so
    the on-disk contract (a sibling .meta.json answering "where did this come
    from") still holds.
    """
    OUT_DATA.mkdir(parents=True, exist_ok=True)
    long_df.to_csv(BACKTEST_CSV, index=False)

    from datetime import datetime, timezone

    vintages = sorted(long_df["vintage_date"].unique().tolist()) if not long_df.empty else []
    meta = {
        "name": "boc_shadow_backtest",
        "source": "Sibley Creek internal — BoC rule-implied shadow rate backtest "
                  "(ToTEM III rule on historical MPR projections)",
        "source_url": "https://www.bankofcanada.ca/publications/mpr/",
        "source_id": "Historical MPR vintages (Tables 2 & 3) + BoC Technical Report 119",
        "units": "%",
        "frequency": "quarterly",
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "release_date": None,
        "reference_period_start": vintages[0] if vintages else None,
        "reference_period_end": vintages[-1] if vintages else None,
        "notes": (
            "Long-format rule-implied policy paths, one row per "
            "(vintage_date, quarter, implied_rate). Each vintage is the ToTEM "
            "III estimated rule (TR-119 Table 2.3) run on that MPR's published "
            "projections via the read-only shadow_rate engine. Informational "
            "backtest, not a publication gate. Realized comparison uses "
            "overnight_rate_target.csv sampled at quarter-end."
        ),
        "transform": "totem3_taylor_rule_shadow_path_backtest",
        "schema_version": 1,
    }
    BACKTEST_META.write_text(json.dumps(meta, indent=2, sort_keys=False))
    return BACKTEST_CSV, BACKTEST_META


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def main(argv: list[str] | None = None) -> int:
    pairs = run_all()
    actual_by_q = load_actual_by_quarter()

    print_vintage_lines(pairs)
    surveys = _surveys_by_quarter()
    metrics = compute_metrics(pairs, actual_by_q, surveys)
    print_metrics(metrics)

    long_df = paths_long_frame(pairs)
    csv_path, meta_path = write_backtest_csv(long_df)
    print(f"wrote {csv_path}")
    print(f"wrote {meta_path}")

    # Render the porcupine chart + embedded metrics table.
    from pipeline.shadow_rate.backtest_chart import render_backtest_chart

    svg_path, html_path = render_backtest_chart(pairs, metrics, surveys=surveys)
    print(f"wrote {svg_path}")
    print(f"wrote {html_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
