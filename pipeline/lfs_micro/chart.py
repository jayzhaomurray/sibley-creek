"""Chart: LFS-micro underlying wage growth (ours) vs BoC INDINF_LFSMICRO_M.

matplotlib -> SVG, embedded inline in a minimal self-contained HTML wrapper.
Restrained palette: no gridline clutter, no chartjunk, direct end-labels.
Mirrors pipeline/shadow_rate/chart.py conventions.

Outputs (vintage-stamped):
  work/research/lfs_micro/lfs_micro_<YYYY-MM>.svg
  work/research/lfs_micro/lfs_micro_<YYYY-MM>.html
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # headless
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).parents[2]

# Restrained palette.
_INK = "#1a1a1a"
_OURS = "#c0392b"       # red — ours (composition-adjusted)
_BOC = "#1a1a1a"        # dark — BoC published
_RAW = "#888888"        # grey — raw mean wage growth
_MUTE = "#aaaaaa"

OUT_DIR = PROJECT_ROOT / "work" / "research" / "lfs_micro"


def _load_replication() -> pd.DataFrame:
    csv = PROJECT_ROOT / "data" / "processed" / "lfs_micro_replication.csv"
    df = pd.read_csv(csv, parse_dates=["date"])
    df = df.sort_values("date").reset_index(drop=True)
    return df


def _load_boc() -> pd.DataFrame:
    """Load the BoC benchmark and convert to chart units.

    The BoC publishes INDINF_LFSMICRO_M in log points (100*dlog); our headline
    is geometric percent ((exp(lp)-1)*100). 'value' keeps the published log
    points; 'value_geo' is the lp -> geometric conversion used for plotting so
    both lines are in the same units.
    """
    csv = PROJECT_ROOT / "data" / "raw" / "lfs_micro.csv"
    df = pd.read_csv(csv, parse_dates=["date"])
    df = df.sort_values("date").reset_index(drop=True)
    df["value_geo"] = (np.exp(df["value"].astype(float) / 100.0) - 1.0) * 100.0
    return df


def render_chart(
    svg_path: str | Path | None = None,
    html_path: str | Path | None = None,
    history_start_year: int = 2018,
) -> tuple[Path, Path]:
    """Render the LFS-micro headline chart to SVG + minimal HTML wrapper.

    If svg_path / html_path are None, the output paths are derived from the
    vintage tag of the latest replication month.

    Returns:
        (svg_path, html_path)
    """
    rep = _load_replication()
    boc = _load_boc()

    if rep.empty:
        raise RuntimeError("Replication CSV is empty — run the engine first.")

    vintage_tag = pd.to_datetime(rep["date"]).max().strftime("%Y-%m")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    svg_path = Path(svg_path) if svg_path else OUT_DIR / f"lfs_micro_{vintage_tag}.svg"
    html_path = Path(html_path) if html_path else OUT_DIR / f"lfs_micro_{vintage_tag}.html"

    # Filter to history_start_year
    rep = rep[rep["date"] >= pd.Timestamp(year=history_start_year, month=1, day=1)].copy()
    boc = boc[boc["date"] >= pd.Timestamp(year=history_start_year, month=1, day=1)].copy()

    fig, ax = plt.subplots(figsize=(9.0, 5.0))

    # Mean log-wage growth (geometric mean ratio) — muted background reference
    # NOTE: this is weighted mean log-wage growth, not the LFS headline arithmetic
    # average hourly wage growth. The column is named raw_mean_pct for CSV
    # consumer compatibility; the human-facing label uses the correct description.
    if "raw_mean_pct" in rep.columns:
        ax.plot(
            rep["date"], rep["raw_mean_pct"],
            color=_RAW, lw=1.2, ls=(0, (3, 3)),
            zorder=2, label="mean log-wage growth (geometric, y/y %)",
        )

    # BoC published series (solid dark), converted lp -> geometric so it is
    # in the same units as our headline line.
    ax.plot(
        boc["date"], boc["value_geo"],
        color=_BOC, lw=1.8, solid_capstyle="round",
        zorder=3, label="BoC INDINF_LFSMICRO_M (lp converted to geometric %)",
    )

    # Ours (dashed red — composition-adjusted)
    ax.plot(
        rep["date"], rep["underlying_pct"],
        color=_OURS, lw=1.8, ls=(0, (5, 3)),
        zorder=4, label="underlying wage growth (ours, composition-adj.)",
    )

    # Raw single-month extension past the smoothed line's end. The centered
    # MA3 headline always lags the newest PUMF month by one — on release
    # morning the freshest signal is the unsmoothed point, so draw it as a
    # faint dotted tail with an open marker and its own end-label.
    raw_tail = pd.DataFrame()
    if "underlying_raw_pct" in rep.columns and rep["underlying_pct"].notna().any():
        last_smoothed = rep.loc[rep["underlying_pct"].notna(), "date"].max()
        raw_tail = rep[
            (rep["date"] >= last_smoothed) & rep["underlying_raw_pct"].notna()
        ]
        if len(raw_tail) > 1:
            ax.plot(
                raw_tail["date"], raw_tail["underlying_raw_pct"],
                color=_OURS, lw=1.2, ls=(0, (1, 2)), alpha=0.65,
                zorder=4, label="newest month, single-month (unsmoothed)",
            )
            tail_date = raw_tail["date"].iloc[-1]
            tail_val = raw_tail["underlying_raw_pct"].iloc[-1]
            ax.plot(
                tail_date, tail_val,
                marker="o", ms=4.5, mfc="white", mec=_OURS, mew=1.2,
                zorder=5,
            )
            ax.annotate(
                f"{tail_val:.2f}%",
                xy=(tail_date, tail_val),
                xytext=(6, 0),
                textcoords="offset points",
                color=_OURS, fontsize=9, va="center", alpha=0.8,
            )

    # Direct end-labels
    last_ours_idx = rep["underlying_pct"].dropna().index[-1]
    last_ours_val = rep.loc[last_ours_idx, "underlying_pct"]
    last_ours_date = rep.loc[last_ours_idx, "date"]

    ax.annotate(
        f"{last_ours_val:.2f}%",
        xy=(last_ours_date, last_ours_val),
        xytext=(6, 0),
        textcoords="offset points",
        color=_OURS,
        fontsize=9,
        va="center",
        fontweight="bold",
    )

    last_boc_idx = boc["value_geo"].dropna().index[-1]
    last_boc_val = boc.loc[last_boc_idx, "value_geo"]
    last_boc_date = boc.loc[last_boc_idx, "date"]

    ax.annotate(
        f"{last_boc_val:.2f}%",
        xy=(last_boc_date, last_boc_val),
        xytext=(6, -10),
        textcoords="offset points",
        color=_BOC,
        fontsize=9,
        va="center",
        fontweight="bold",
    )

    # Restraint: drop top/right spines, no grid, sparse ticks
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    ax.spines["left"].set_color(_MUTE)
    ax.spines["bottom"].set_color(_MUTE)
    ax.tick_params(colors=_MUTE, labelsize=8)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.xaxis.set_major_locator(mdates.YearLocator())

    ax.set_ylabel("y/y % change (geometric)", color=_INK, fontsize=9)
    ax.set_title(
        "LFS-micro: composition-adjusted underlying wage growth\n"
        f"O-B replication of BoC SAN 2024-23 | PUMF vintage {vintage_tag}",
        color=_INK, fontsize=10, loc="left", pad=12,
    )
    ax.legend(loc="upper left", frameon=False, fontsize=8)

    fig.tight_layout()
    fig.savefig(svg_path, format="svg")
    plt.close(fig)

    _write_html(svg_path, html_path, rep, boc, vintage_tag)
    return svg_path, html_path


def _write_html(
    svg_path: Path,
    html_path: Path,
    rep: pd.DataFrame,
    boc: pd.DataFrame,
    vintage_tag: str,
) -> None:
    """Wrap the SVG inline in a minimal self-contained HTML page."""
    svg_text = svg_path.read_text(encoding="utf-8")
    lines = [ln for ln in svg_text.splitlines()
             if not ln.lstrip().startswith("<?xml")
             and not ln.lstrip().startswith("<!DOCTYPE")]
    svg_inline = "\n".join(lines)

    # Build table of last 24 months for both series. Same-units comparison:
    # the BoC publishes log points; show the published lp value AND the
    # lp -> geometric conversion; diff is geo minus geo.
    boc_lp_idx = boc.set_index("date")["value"]
    boc_geo_idx = boc.set_index("date")["value_geo"]
    rep_idx = rep.set_index("date")["underlying_pct"].dropna()
    common = rep_idx.index.intersection(boc_lp_idx.index)
    rows_data = sorted(common, reverse=True)[:24]

    rows_html = ""
    for d in rows_data:
        ours = rep_idx.loc[d]
        boc_lp = boc_lp_idx.loc[d]
        boc_geo = boc_geo_idx.loc[d]
        diff = ours - boc_geo
        diff_style = "color:#c0392b" if abs(diff) > 0.3 else ""
        rows_html += (
            f"<tr><td>{d.strftime('%Y-%m')}</td>"
            f"<td>{ours:.3f}</td>"
            f"<td>{boc_lp:.1f}</td>"
            f"<td>{boc_geo:.3f}</td>"
            f"<td style='{diff_style}'>{diff:+.3f}</td></tr>\n"
        )

    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>LFS-micro composition-adjusted wage growth -- {vintage_tag}</title>
<style>
  body {{ font-family: -apple-system, Segoe UI, Helvetica, Arial, sans-serif;
          color:#1a1a1a; max-width: 940px; margin: 2rem auto; padding: 0 1rem;
          line-height: 1.5; }}
  h1 {{ font-size: 1.1rem; font-weight: 600; margin-bottom: .25rem; }}
  .meta {{ color:#888; font-size:.85rem; margin-bottom:1.5rem; }}
  figure {{ margin: 0 0 1.5rem; }}
  table {{ border-collapse: collapse; font-size:.85rem; font-variant-numeric: tabular-nums; }}
  th, td {{ text-align:right; padding:.2rem .7rem; border-bottom:1px solid #eee; }}
  th:first-child, td:first-child {{ text-align:left; }}
  th {{ border-bottom:1px solid #ccc; font-weight:600; }}
  caption {{ text-align:left; font-size:.8rem; color:#888; margin-bottom:.4rem; caption-side:top; }}
  .note {{ font-size:.78rem; color:#888; margin-top:1.5rem; border-top:1px solid #eee; padding-top:.8rem; }}
</style>
</head>
<body>
<h1>LFS-micro: composition-adjusted underlying wage growth</h1>
<div class="meta">
  Oaxaca-Blinder replication of BoC SAN 2024-23 &middot;
  PUMF vintage {vintage_tag} &middot;
  benchmark: BoC Valet INDINF_LFSMICRO_M
</div>
<figure>
{svg_inline}
</figure>
<table>
<caption>Last 24 months: ours vs BoC (same units: geometric y/y %; BoC publishes log points)</caption>
<thead><tr><th>month</th><th>ours % (geo)</th><th>BoC (lp, as published)</th><th>BoC % (lp&rarr;geo)</th><th>diff pp (geo)</th></tr></thead>
<tbody>{rows_html}</tbody>
</table>
<p class="note">
  Internal Sibley Creek research tool. Composition-adjusted underlying wage growth
  from a weighted OLS Oaxaca-Blinder decomposition of log-wage regressions on LFS
  PUMF monthly cross-sections. Methodology: Bounajm, Devakos, and Galassi, BoC
  Staff Analytical Note 2024-23. The dashed red line is our replication (geometric
  percent, (exp(lp)&minus;1)&times;100); the solid black line is the BoC&rsquo;s
  published INDINF_LFSMICRO_M, which the Bank publishes in log points
  (100&times;&Delta;log) and which is converted lp&rarr;geometric here so both
  lines are in the same units. Residual differences reflect PUMF category
  granularity vs the master files, BoC 0.1pp publication rounding, and
  estimation noise. See claude-ref/research/lfs_micro/calibration_report.md.
</p>
</body>
</html>
"""
    html_path.write_text(html, encoding="utf-8")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv=None) -> int:
    import argparse
    parser = argparse.ArgumentParser(description="Render LFS-micro headline chart")
    parser.add_argument("--start-year", type=int, default=2018,
                        help="First year of history to plot (default: 2018)")
    args = parser.parse_args(argv)
    svg, html = render_chart(history_start_year=args.start_year)
    print(f"wrote {svg}")
    print(f"wrote {html}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
