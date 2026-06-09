"""CLI entry point for the BoC shadow-rate tool.

    python -m pipeline.shadow_rate.run [--xlsx PATH] [--force-unverified]

With no --xlsx, the newest boc_shadow_inputs_<YYYY>Q<n>.xlsx workbook is used.
Parses the punch-in workbook, runs the rule, writes the output series — both the
stable current-vintage data/processed/boc_shadow_rate.csv and a vintage-stamped
copy boc_shadow_rate_<YYYY-MM>.csv (each + sidecar) so successive MPRs accumulate
— renders the vintage-stamped chart (boc_shadow_path_<YYYY-MM>.svg/html), and
prints the quarterly path to stdout. The projection horizon and all vintage
stamps derive from the workbook (projection_end_quarter, mpr_publication_date).

Refuses to run (exit non-zero) when the workbook is unverified unless
--force-unverified is passed, in which case it emits a watermarked draft.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

project_root = Path(__file__).parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import pandas as pd  # noqa: E402

from pipeline.io import SeriesMeta, write_series  # noqa: E402
from pipeline.shadow_rate.chart import render_chart  # noqa: E402
from pipeline.shadow_rate.inputs import parse_workbook  # noqa: E402
from pipeline.shadow_rate.market_path import fetch_market_path  # noqa: E402
from pipeline.shadow_rate.model import (  # noqa: E402
    annual_average_crosscheck,
    run_band,
    run_model,
)
from pipeline.shadow_rate.output_sheet import write_output_sheet  # noqa: E402


WORKBOOK_DIR = project_root / "work" / "research" / "shadow_rate"
OUT_DATA = project_root / "data" / "processed"
OUT_CHART_DIR = WORKBOOK_DIR

# Stable name for the CURRENT vintage's output series (any future site wiring
# reads this). Per-vintage copies accumulate alongside it.
CURRENT_SERIES_NAME = "boc_shadow_rate"

TRANSFORM = "totem3_taylor_rule_shadow_path"


def _newest_workbook() -> Path:
    """Pick the lexically newest punch-in workbook in the workbook dir.

    Naming convention boc_shadow_inputs_<YYYY>Q<n>.xlsx sorts correctly
    lexically (year then quarter), so the max() is the latest vintage. Excel
    lock/temp files (``~$...``) are excluded.
    """
    candidates = sorted(
        p for p in WORKBOOK_DIR.glob("boc_shadow_inputs_*.xlsx")
        if not p.name.startswith("~$")
    )
    if not candidates:
        raise FileNotFoundError(
            f"no boc_shadow_inputs_*.xlsx workbook found in {WORKBOOK_DIR}"
        )
    return candidates[-1]


def _quarter_to_date(q: str) -> str:
    """'YYYYQn' -> ISO first-of-quarter date string."""
    year = int(q[:4])
    qn = int(q[5])
    month = (qn - 1) * 3 + 1
    return f"{year}-{month:02d}-01"


def _print_table(res, p, band) -> None:
    mpr_label = p.mpr_publication_date.strftime("%B %Y")
    print()
    print("=== BoC rule-implied shadow rate "
          f"(ToTEM III rule on {mpr_label} MPR projections) ===")
    print(f"Seed quarter {res.seed_quarter} @ {res.seed_rate:.2f}%  ->  end "
          f"{res.steps[-1].quarter}")
    print(f"Output-gap anchor: {p.output_gap_anchor_quarter} = "
          f"{p.output_gap_anchor_value:+.2f}pp  (BoC Valet INDINF_OUTGAPMPR_Q, "
          f"last published obs; rolled forward to seed)")
    print(f"{'quarter':<9}{'rate%':>8}{'band_lo':>9}{'band_hi':>9}"
          f"{'gap pp':>9}{'pi t+4%':>9}{'gdp qq%':>9}{'pot%':>7}")
    print("-" * 69)
    for s in res.steps:
        print(f"{s.quarter:<9}{s.rate:>8.3f}{band.lo[s.quarter]:>9.3f}"
              f"{band.hi[s.quarter]:>9.3f}{s.gap:>9.3f}{s.infl_tp4:>9.3f}"
              f"{s.gdp_growth:>9.2f}{s.potential:>7.2f}")
    print()
    print("Band: min/max rate across the 4 corners of "
          "{neutral_low,neutral_high} x {potential low,high} (central case core "
          "CPI / GDP / gap anchor). See methodology Section 9.")
    print()


def _print_crosscheck(checks) -> None:
    """Print the annual-average GDP coherence diagnostic (WARN, never fails)."""
    if not checks:
        return
    print("Annual-average GDP cross-check (implied from constructed quarterly "
          "path vs MPR Table 2 published):")
    for c in checks:
        flag = "  *** WARN |diff|>0.15pp ***" if c.tripped else ""
        approx = " (approx: prior-year level path incomplete)" if c.approximate else ""
        pub = "n/a" if c.published is None else f"{c.published:.2f}"
        diff = "n/a" if c.diff is None else f"{c.diff:+.3f}"
        print(f"  {c.year}: implied {c.implied:.3f}  published {pub}  "
              f"diff {diff}pp{flag}{approx}")
    print("  (coherence diagnostic only — does not fail the run.)")
    print()


def _print_market(market, res) -> None:
    """Print the market-implied path beside the rule path over shared quarters."""
    if market is None:
        print("Market-implied path (CORRA futures): unavailable "
              "(fetch failed or --no-market); chart omits the dotted line.\n")
        return
    rule_by_q = {s.quarter: s.rate for s in res.steps}
    by_q = market.by_quarter()
    shared = [s.quarter for s in res.steps if s.quarter in by_q]
    print("Market-implied policy path (three-month CORRA futures, Montreal "
          "Exchange):")
    print(f"  CORRA->target spread (trailing {market.spread_window_days} bus. days): "
          f"{market.spread:+.4f} pp  (implied_target = implied_corra - spread)")
    print(f"  {'quarter':<9}{'mkt tgt%':>10}{'rule%':>9}{'rule-mkt':>10}"
          f"   contract")
    print("  " + "-" * 56)
    contract_by_q = {c.quarter: c.contract for c in market.contracts}
    for q in shared:
        mkt = by_q[q]
        rule = rule_by_q[q]
        print(f"  {q:<9}{mkt:>10.3f}{rule:>9.3f}{rule - mkt:>+10.3f}"
              f"   {contract_by_q.get(q, '')}")
    extra = [c for c in market.contracts if c.quarter not in rule_by_q]
    if extra:
        tail = ", ".join(f"{c.quarter} {c.implied_target:.2f}%" for c in extra)
        print(f"  (futures extend beyond the rule horizon: {tail})")
    print("  rule-mkt > 0 => the rule prescribes a higher rate than the market "
          "prices.\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="BoC rule-implied shadow rate (ToTEM III rule on the latest MPR)")
    parser.add_argument("--xlsx", default=None,
                        help="punch-in workbook path "
                             "(default: newest boc_shadow_inputs_<YYYY>Q<n>.xlsx)")
    parser.add_argument("--force-unverified", action="store_true",
                        help="emit a watermarked draft even when verified=FALSE")
    parser.add_argument("--end-quarter", default=None,
                        help="last projected quarter "
                             "(default: workbook projection_end_quarter)")
    parser.add_argument("--no-market", action="store_true",
                        help="skip the market-implied (CORRA futures) overlay "
                             "fetch (offline runs / tests)")
    args = parser.parse_args(argv)

    xlsx = Path(args.xlsx) if args.xlsx else _newest_workbook()
    inp = parse_workbook(xlsx)
    p = inp.params

    if not p.verified and not args.force_unverified:
        print(
            "ERROR: workbook is marked verified=FALSE.\n"
            "  Jay must check every transcribed cell against the MPR PDF and set\n"
            "  verified=TRUE in the params sheet before a real run.\n"
            "  To emit a watermarked DRAFT for eyeballing, re-run with "
            "--force-unverified.",
            file=sys.stderr,
        )
        return 2

    res = run_model(inp, end_quarter=args.end_quarter)
    band = run_band(inp, end_quarter=args.end_quarter)
    checks = annual_average_crosscheck(inp, end_quarter=args.end_quarter)
    _print_table(res, p, band)
    _print_crosscheck(checks)

    # Market-implied path (CORRA futures): fetched after the model, before the
    # chart. Any scrape/fetch failure returns None and the chart degrades cleanly.
    market = None if args.no_market else fetch_market_path()
    _print_market(market, res)

    draft = not p.verified
    if draft:
        print("(draft: verified=FALSE; outputs carry an UNVERIFIED watermark / "
              "note)\n")

    # --- output series ---
    df = pd.DataFrame(
        {
            "date": [_quarter_to_date(s.quarter) for s in res.steps],
            "value": [round(s.rate, 4) for s in res.steps],
            "band_lo": [round(band.lo[s.quarter], 4) for s in res.steps],
            "band_hi": [round(band.hi[s.quarter], 4) for s in res.steps],
            "quarter": [s.quarter for s in res.steps],
            "shadow_rate": [round(s.rate, 4) for s in res.steps],
            "output_gap": [round(s.gap, 4) for s in res.steps],
            "core_cpi_tp4": [round(s.infl_tp4, 4) for s in res.steps],
            "gdp_growth_qq_ann": [round(s.gdp_growth, 4) for s in res.steps],
            "potential_growth": [round(s.potential, 4) for s in res.steps],
        }
    )
    # Vintage stamp derived from the MPR publication date (e.g. "2026-04").
    pub = p.mpr_publication_date
    vintage_tag = f"{pub.year:04d}-{pub.month:02d}"
    mpr_label = pub.strftime("%B %Y")  # e.g. "April 2026"
    mpr_url = f"https://www.bankofcanada.ca/publications/mpr/mpr-{pub.isoformat()}/"

    notes = (
        f"BoC rule-implied shadow rate: ToTEM III estimated policy rule (TR-119 "
        f"Table 2.3: rho={p.rho}, phi_pi={p.phi_pi}, phi_gap={p.phi_gap}) on the "
        f"{mpr_label} MPR projections with transparent interpolation assumptions. "
        f"Seed {res.seed_quarter} @ {res.seed_rate:.2f}% (actual overnight rate). "
        f"ELB floor {p.elb_floor}. Neutral midpoint "
        f"{p.neutral_nominal_mid:.2f} ({p.neutral_range_low}-{p.neutral_range_high}). "
        f"band_lo/band_hi columns = min/max across the 4 corners of the published "
        f"neutral x potential-growth ranges. NOT the Bank's actual internal "
        f"conditioning path (judgment add-factors; MPR is conditioned on a "
        f"market-implied rate path)."
    )
    if draft:
        notes = "UNVERIFIED DRAFT — seed transcription not yet checked. " + notes

    def _meta(name: str) -> SeriesMeta:
        return SeriesMeta(
            name=name,
            source="Sibley Creek internal — BoC rule-implied shadow rate (ToTEM III rule on MPR projections)",
            source_url=mpr_url,
            source_id=f"MPR {pub.strftime('%b-%Y')} (Tables 2 & 3) + BoC Technical Report 119",
            units="%",
            frequency="quarterly",
            release_date=p.mpr_publication_date.isoformat(),
            notes=notes,
            transform=TRANSFORM,
        )

    # Stable CURRENT-vintage series (for any future site wiring) ...
    csv_path, meta_path = write_series(df, _meta(CURRENT_SERIES_NAME), OUT_DATA,
                                       date_col="date")
    print(f"wrote {csv_path}")
    print(f"wrote {meta_path}")
    # ... plus a vintage-stamped copy (+sidecar) so successive MPRs accumulate
    # into a track record instead of overwriting each other.
    vintage_name = f"{CURRENT_SERIES_NAME}_{vintage_tag}"
    v_csv_path, v_meta_path = write_series(df, _meta(vintage_name), OUT_DATA,
                                           date_col="date")
    print(f"wrote {v_csv_path}")
    print(f"wrote {v_meta_path}")

    # --- chart (vintage-stamped filenames) ---
    svg_out = OUT_CHART_DIR / f"boc_shadow_path_{vintage_tag}.svg"
    html_out = OUT_CHART_DIR / f"boc_shadow_path_{vintage_tag}.html"
    svg_path, html_path = render_chart(res, p, svg_out, html_out, band=band,
                                       market=market)
    print(f"wrote {svg_path}")
    print(f"wrote {html_path}")

    # --- live-formula calc sheet embedded back into the punch-in workbook ---
    out = write_output_sheet(xlsx, res, p)
    if out.used_companion:
        print(
            f"workbook locked by Excel — calc sheet written to companion file "
            f"{out.path}; close Excel and re-run to embed the 'calc' sheet "
            f"directly in {xlsx}"
        )
    else:
        print(f"wrote 'calc' sheet into {out.path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
