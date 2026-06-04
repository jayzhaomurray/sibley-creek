"""CLI entry point for the BoC shadow-rate tool.

    python -m pipeline.shadow_rate.run [--xlsx PATH] [--force-unverified]

Parses the punch-in workbook, runs the rule, writes the output series
(data/processed/boc_shadow_rate.csv + sidecar via write_series), renders the
chart (SVG + HTML), and prints the quarterly path to stdout.

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
from pipeline.shadow_rate.model import run_model  # noqa: E402
from pipeline.shadow_rate.output_sheet import write_output_sheet  # noqa: E402


DEFAULT_XLSX = (
    project_root / "work" / "research" / "shadow_rate" / "boc_shadow_inputs_2026Q2.xlsx"
)
OUT_DATA = project_root / "data" / "processed"
OUT_CHART_DIR = project_root / "work" / "research" / "shadow_rate"
SVG_OUT = OUT_CHART_DIR / "boc_shadow_path_2026-04.svg"
HTML_OUT = OUT_CHART_DIR / "boc_shadow_path_2026-04.html"

TRANSFORM = "totem3_taylor_rule_shadow_path"


def _quarter_to_date(q: str) -> str:
    """'YYYYQn' -> ISO first-of-quarter date string."""
    year = int(q[:4])
    qn = int(q[5])
    month = (qn - 1) * 3 + 1
    return f"{year}-{month:02d}-01"


def _print_table(res, p) -> None:
    print()
    print(f"Seed quarter {res.seed_quarter} @ {res.seed_rate:.2f}%  ->  end "
          f"{res.steps[-1].quarter}")
    print(f"Output-gap anchor: {p.output_gap_anchor_quarter} = "
          f"{p.output_gap_anchor_value:+.2f}pp  (BoC Valet INDINF_OUTGAPMPR_Q, "
          f"last published obs; rolled forward to seed)")
    print(f"{'quarter':<9}{'rate%':>8}{'gap pp':>9}{'pi t+4%':>9}"
          f"{'gdp qq%':>9}{'pot%':>7}")
    print("-" * 51)
    for s in res.steps:
        print(f"{s.quarter:<9}{s.rate:>8.3f}{s.gap:>9.3f}{s.infl_tp4:>9.3f}"
              f"{s.gdp_growth:>9.2f}{s.potential:>7.2f}")
    print()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="BoC shadow policy rate (ToTEM III rule on the latest MPR)")
    parser.add_argument("--xlsx", default=str(DEFAULT_XLSX),
                        help="punch-in workbook path")
    parser.add_argument("--force-unverified", action="store_true",
                        help="emit a watermarked draft even when verified=FALSE")
    parser.add_argument("--end-quarter", default="2028Q4",
                        help="last projected quarter (default 2028Q4)")
    args = parser.parse_args(argv)

    inp = parse_workbook(args.xlsx)
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
    _print_table(res, p)

    draft = not p.verified
    if draft:
        print("(draft: verified=FALSE; outputs carry an UNVERIFIED watermark / "
              "note)\n")

    # --- output series ---
    df = pd.DataFrame(
        {
            "date": [_quarter_to_date(s.quarter) for s in res.steps],
            "quarter": [s.quarter for s in res.steps],
            "shadow_rate": [round(s.rate, 4) for s in res.steps],
            "output_gap": [round(s.gap, 4) for s in res.steps],
            "core_cpi_tp4": [round(s.infl_tp4, 4) for s in res.steps],
            "gdp_growth_qq_ann": [round(s.gdp_growth, 4) for s in res.steps],
            "potential_growth": [round(s.potential, 4) for s in res.steps],
        }
    )
    notes = (
        f"ToTEM III estimated policy rule (TR-119 Table 2.3: rho={p.rho}, "
        f"phi_pi={p.phi_pi}, phi_gap={p.phi_gap}) applied to the April 2026 MPR. "
        f"Seed {res.seed_quarter} @ {res.seed_rate:.2f}% (actual overnight rate). "
        f"ELB floor {p.elb_floor}. Neutral midpoint "
        f"{p.neutral_nominal_mid:.2f} ({p.neutral_range_low}-{p.neutral_range_high}). "
        f"Coherence reading of the Bank's published outputs, not advice."
    )
    if draft:
        notes = "UNVERIFIED DRAFT — seed transcription not yet checked. " + notes

    meta = SeriesMeta(
        name="boc_shadow_rate",
        source="Sibley Creek internal — BoC ToTEM III rule on MPR projections",
        source_url="https://www.bankofcanada.ca/publications/mpr/mpr-2026-04-29/",
        source_id="MPR Apr-2026 (Tables 2 & 3) + BoC Technical Report 119",
        units="%",
        frequency="quarterly",
        release_date=p.mpr_publication_date.isoformat(),
        notes=notes,
        transform=TRANSFORM,
    )
    csv_path, meta_path = write_series(df, meta, OUT_DATA, date_col="date")
    print(f"wrote {csv_path}")
    print(f"wrote {meta_path}")

    # --- chart ---
    svg_path, html_path = render_chart(res, p, SVG_OUT, HTML_OUT)
    print(f"wrote {svg_path}")
    print(f"wrote {html_path}")

    # --- live-formula calc sheet embedded back into the punch-in workbook ---
    out = write_output_sheet(args.xlsx, res, p)
    if out.used_companion:
        print(
            f"workbook locked by Excel — calc sheet written to companion file "
            f"{out.path}; close Excel and re-run to embed the 'calc' sheet "
            f"directly in {args.xlsx}"
        )
    else:
        print(f"wrote 'calc' sheet into {out.path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
