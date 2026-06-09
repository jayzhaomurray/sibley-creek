"""The porcupine: every historical vintage's rule-implied path overlaid as a
thin grey quill against the realized overnight-rate history.

matplotlib -> SVG, embedded inline in a minimal self-contained HTML wrapper with
the forecast-skill metrics table beneath it. Same restraint as ``chart.py``: no
gridline clutter, a single neutral-range band, sparse furniture.

Outputs:
    work/research/shadow_rate/backtest/boc_shadow_backtest.svg
    work/research/shadow_rate/backtest/boc_shadow_backtest.html
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # headless
import matplotlib.pyplot as plt
import pandas as pd

from pipeline.shadow_rate.model import ShadowResult


PROJECT_ROOT = Path(__file__).parents[2]
OUT_DIR = PROJECT_ROOT / "work" / "research" / "shadow_rate" / "backtest"
ACTUAL_CSV = PROJECT_ROOT / "data" / "processed" / "overnight_rate_target.csv"

# Restrained palette (matches chart.py).
_INK = "#1a1a1a"
_HISTORY = "#1a1a1a"
_QUILL = "#888888"
_BAND = "#3a6ea5"
_ELB = "#b0392b"
_MUTE = "#888888"
_MARKET = "#7fb3d5"  # muted light blue for the MPS median expected paths

# Neutral band the porcupine shades (the published neutral-rate range; fixed
# light shade per the brief).
NEUTRAL_LOW = 2.25
NEUTRAL_HIGH = 3.25
ELB_FLOOR = 0.25
HISTORY_START = date(2020, 1, 1)


def _quarter_to_date(q: str) -> date:
    year = int(q[:4])
    qn = int(q[5])
    return date(year, (qn - 1) * 3 + 1, 1)


def _quarter_of_iso(iso: str) -> str:
    """'2024-04-10' -> '2024Q2' (calendar quarter containing the date)."""
    d = date.fromisoformat(iso)
    return f"{d.year}Q{(d.month - 1) // 3 + 1}"


def _load_history(start: date = HISTORY_START) -> pd.DataFrame:
    df = pd.read_csv(ACTUAL_CSV)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"]).sort_values("date")
    df = df[df["date"] >= pd.Timestamp(start)]
    return df.reset_index(drop=True)


def render_backtest_chart(
    pairs: list[tuple[dict, ShadowResult]],
    metrics: pd.DataFrame,
    svg_path: str | Path | None = None,
    html_path: str | Path | None = None,
    surveys: dict[str, dict] | None = None,
) -> tuple[Path, Path]:
    """Render the porcupine chart (SVG) + HTML wrapper with the metrics table.

    ``surveys`` maps survey quarter -> MPS record. When supplied, each vintage's
    matched Market Participants Survey median path is overlaid as a thin dotted
    light-blue line (same transparency spirit as the grey rule quills), with a
    single legend entry. When None, only the rule quills are drawn.
    """
    svg_path = Path(svg_path) if svg_path else OUT_DIR / "boc_shadow_backtest.svg"
    html_path = Path(html_path) if html_path else OUT_DIR / "boc_shadow_backtest.html"
    svg_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.parent.mkdir(parents=True, exist_ok=True)

    hist = _load_history()
    fig, ax = plt.subplots(figsize=(9.0, 5.0))

    # Neutral-range band (light shade).
    ax.axhspan(NEUTRAL_LOW, NEUTRAL_HIGH, color=_BAND, alpha=0.08, zorder=0)
    if not hist.empty:
        ax.text(
            hist["date"].iloc[0], (NEUTRAL_LOW + NEUTRAL_HIGH) / 2,
            f"neutral range {NEUTRAL_LOW:.2f}-{NEUTRAL_HIGH:.2f}",
            color=_BAND, fontsize=8, va="center", ha="left", alpha=0.9,
        )

    # ELB floor (dashed).
    ax.axhline(ELB_FLOOR, color=_ELB, lw=1.0, ls=(0, (4, 3)), alpha=0.7, zorder=1)
    if not hist.empty:
        ax.text(
            hist["date"].iloc[-1], ELB_FLOOR, " ELB 0.25",
            color=_ELB, fontsize=7, va="bottom", ha="right", alpha=0.8,
        )

    # The quills: each vintage path a thin, slightly transparent grey line
    # starting at its seed quarter.
    quill_label_used = False
    for _d, res in pairs:
        xs = [_quarter_to_date(s.quarter) for s in res.steps]
        ys = [s.rate for s in res.steps]
        ax.plot(
            xs, ys, color=_QUILL, lw=0.8, alpha=0.45, zorder=2,
            label=None if quill_label_used else "rule-implied paths (vintages)",
        )
        quill_label_used = True

    # Matched MPS median expected paths: thin DOTTED light-blue lines, drawn at
    # the survey's published (sparse) points so the overlay shows exactly what the
    # market expected. Same transparency spirit as the grey quills; one legend
    # entry shared across all matched surveys.
    surveys = surveys or {}
    from datetime import date as _date

    market_label_used = False
    for d, _res in pairs:
        if d.get("_live"):
            continue
        mpr_date = d.get("mpr_date")
        if not mpr_date:
            continue
        q = _quarter_of_iso(mpr_date)
        rec = surveys.get(q)
        if not rec or not rec.get("path"):
            continue
        pts = sorted(rec["path"], key=lambda p: _quarter_to_date(p[0]))
        xs = [_quarter_to_date(qq) for qq, _r in pts]
        ys = [r for _qq, r in pts]
        ax.plot(
            xs, ys, color=_MARKET, lw=0.9, ls=(0, (1, 2)), alpha=0.7, zorder=3,
            label=None if market_label_used else "market expected path (MPS median)",
        )
        market_label_used = True

    # Realized overnight rate, solid black, on top.
    if not hist.empty:
        ax.plot(hist["date"], hist["value"], color=_HISTORY, lw=1.8,
                solid_capstyle="round", zorder=4, label="overnight rate (actual)")

    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    ax.spines["left"].set_color(_MUTE)
    ax.spines["bottom"].set_color(_MUTE)
    ax.tick_params(colors=_MUTE, labelsize=8)
    ax.set_ylabel("policy rate (%)", color=_INK, fontsize=9)
    ax.set_title(
        "BoC rule-implied shadow rate — vintage backtest\n"
        "ToTEM III rule on each MPR's projections vs realized overnight rate",
        color=_INK, fontsize=11, loc="left", pad=12,
    )
    ax.legend(loc="upper left", frameon=False, fontsize=8)

    fig.tight_layout()
    fig.savefig(svg_path, format="svg")
    plt.close(fig)

    n_matched = 0
    for d, _res in pairs:
        if d.get("_live"):
            continue
        mpr_date = d.get("mpr_date")
        if mpr_date and surveys.get(_quarter_of_iso(mpr_date)):
            n_matched += 1

    _write_html(svg_path, html_path, pairs, metrics, n_matched)
    return svg_path, html_path


def _metrics_table_html(metrics: pd.DataFrame) -> str:
    def cell(v, p=3):
        return "&mdash;" if pd.isna(v) else f"{v:.{p}f}"

    has_market = "mae_market" in metrics.columns
    rows = []
    for _, r in metrics.iterrows():
        dir_cell = "&mdash;" if pd.isna(r["dir_hit_rate"]) else f"{r['dir_hit_rate']:.2f}"
        if has_market:
            n_mkt = "&mdash;" if pd.isna(r["n_market"]) else f"{int(r['n_market'])}"
            market_cells = (
                f"<td>{cell(r['mae_market'])}</td>"
                f"<td>{cell(r['skill_rule_vs_market'])}</td>"
                f"<td>{n_mkt}</td>"
            )
        else:
            market_cells = ""
        rows.append(
            f"<tr><td>{int(r['horizon_q'])}</td><td>{int(r['n'])}</td>"
            f"<td>{cell(r['bias'])}</td><td>{cell(r['mae'])}</td>"
            f"<td>{cell(r['mae_rw'])}</td><td>{cell(r['skill'])}</td>"
            f"{market_cells}"
            f"<td>{dir_cell}</td></tr>"
        )
    return "".join(rows)


def _write_html(
    svg_path: Path,
    html_path: Path,
    pairs: list[tuple[dict, ShadowResult]],
    metrics: pd.DataFrame,
    n_matched: int = 0,
) -> None:
    svg_text = svg_path.read_text(encoding="utf-8")
    lines = [ln for ln in svg_text.splitlines()
             if not ln.lstrip().startswith("<?xml")
             and not ln.lstrip().startswith("<!DOCTYPE")]
    svg_inline = "\n".join(lines)

    n_vintages = len(pairs)
    rows = _metrics_table_html(metrics)
    has_market = "mae_market" in metrics.columns
    market_headers = (
        "<th>MAE&nbsp;mkt</th><th>skill&nbsp;vs&nbsp;mkt</th><th>n&nbsp;mkt</th>"
        if has_market else ""
    )
    market_caption = " vs MPS market median" if has_market else ""

    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>BoC rule-implied shadow rate — vintage backtest</title>
<style>
  body {{ font-family: -apple-system, Segoe UI, Helvetica, Arial, sans-serif;
          color:#1a1a1a; max-width: 940px; margin: 2rem auto; padding: 0 1rem;
          line-height: 1.5; }}
  h1 {{ font-size: 1.15rem; font-weight: 600; margin-bottom: .25rem; }}
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
<h1>BoC rule-implied shadow rate &mdash; vintage backtest</h1>
<div class="meta">
  ToTEM III rule (TR-119) on each historical MPR's projections &middot;
  {n_vintages} vintage{"s" if n_vintages != 1 else ""} overlaid &middot;
  realized overnight rate sampled at quarter-end
</div>
<figure>
{svg_inline}
</figure>
<table>
<caption>Forecast-skill metrics: rule-implied path vs random-walk benchmark{market_caption}</caption>
<thead><tr><th>horizon (q)</th><th>n</th><th>bias</th><th>MAE</th>
<th>MAE&nbsp;rw</th><th>skill</th>{market_headers}<th>dir&nbsp;hit</th></tr></thead>
<tbody>{rows}</tbody>
</table>
<p class="note">
  Internal Sibley Creek research tool. Each grey quill is the ToTEM III
  rule-implied policy path on one MPR vintage's published projections, starting
  at that MPR's seed quarter; the solid black line is the realized overnight
  rate. <em>bias</em> = mean (implied &minus; actual); <em>skill</em> = MAE of
  the rule / MAE of a no-change random walk (&lt;1 means the rule beats random
  walk); <em>dir hit</em> = directional hit-rate at the 2-quarter horizon. This
  is NOT a recovery of the Bank's actual internal conditioning path; the MPR
  forecast is itself conditioned on a market-implied rate path and the Bank's
  internal path carries judgmental add-factors.
</p>
<p class="note">
  Dotted light-blue lines are the median expected overnight-rate path from the
  Bank of Canada <a href="https://www.bankofcanada.ca/publications/market-participants-survey/">Market
  Participants Survey</a> (MPS), matched to each MPR vintage by reference quarter
  ({n_matched} matched). The MPS polls ~30 market participants on their policy-rate
  expectations and is published roughly two weeks AFTER the corresponding MPR, so
  the survey already reflects that MPR's decision &mdash; a small information
  advantage over the rule. <em>MAE&nbsp;mkt</em> = MAE of the matched MPS median
  path; <em>skill vs mkt</em> = MAE of the rule / MAE of the survey on the shared
  (market-available) cells (&lt;1 means the rule beats the market's median
  expectation); <em>n&nbsp;mkt</em> = cells in that subset. This answers whether
  the rule adds information beyond market expectations.
</p>
</body>
</html>
"""
    html_path.write_text(html, encoding="utf-8")
