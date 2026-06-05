"""Chart: actual overnight-rate history (solid) + shadow path (dashed).

matplotlib -> SVG, embedded inline in a minimal self-contained HTML wrapper.
Vignelli-ish restraint: no gridline clutter, no chartjunk, one neutral-range
band, direct end-labels. When the workbook is unverified, a diagonal watermark
states the path is a draft.
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

# Restrained palette.
_INK = "#1a1a1a"
_HISTORY = "#1a1a1a"
_SHADOW = "#c0392b"
_BAND = "#3a6ea5"
_MUTE = "#888888"


def _quarter_to_date(q: str) -> date:
    """Map 'YYYYQn' to the first day of that quarter (for x-axis placement)."""
    year = int(q[:4])
    qn = int(q[5])
    month = (qn - 1) * 3 + 1
    return date(year, month, 1)


def _load_history(history_start_year: int = 2015) -> pd.DataFrame:
    csv = PROJECT_ROOT / "data" / "processed" / "overnight_rate_target.csv"
    df = pd.read_csv(csv)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"]).sort_values("date")
    df = df[df["date"] >= pd.Timestamp(year=history_start_year, month=1, day=1)]
    return df.reset_index(drop=True)


def render_chart(
    res: ShadowResult,
    params,
    svg_path: str | Path,
    html_path: str | Path,
    history_start_year: int = 2015,
    band=None,
) -> tuple[Path, Path]:
    """Render the shadow-path chart to SVG + a minimal HTML wrapper.

    ``band`` (optional ``BandResult``) shades a light min/max envelope around the
    dashed central path — the sensitivity band over the published neutral x
    potential-growth range corners.
    """
    svg_path = Path(svg_path)
    html_path = Path(html_path)
    svg_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.parent.mkdir(parents=True, exist_ok=True)

    hist = _load_history(history_start_year)
    shadow_x = [_quarter_to_date(s.quarter) for s in res.steps]
    shadow_y = [s.rate for s in res.steps]

    fig, ax = plt.subplots(figsize=(9.0, 5.0))

    # Neutral-range band.
    ax.axhspan(
        params.neutral_range_low,
        params.neutral_range_high,
        color=_BAND,
        alpha=0.08,
        zorder=0,
    )
    ax.text(
        hist["date"].iloc[0],
        (params.neutral_range_low + params.neutral_range_high) / 2,
        f"neutral range {params.neutral_range_low:.2f}-{params.neutral_range_high:.2f}",
        color=_BAND,
        fontsize=8,
        va="center",
        ha="left",
        alpha=0.9,
    )

    # History (solid).
    ax.plot(hist["date"], hist["value"], color=_HISTORY, lw=1.8,
            solid_capstyle="round", zorder=3, label="overnight rate (actual)")

    # Sensitivity band (light fill between corner min/max), under the line.
    if band is not None:
        band_lo = [band.lo[s.quarter] for s in res.steps]
        band_hi = [band.hi[s.quarter] for s in res.steps]
        ax.fill_between(shadow_x, band_lo, band_hi, color=_SHADOW, alpha=0.10,
                        lw=0, zorder=2, label="range-corner band")

    # Shadow path (dashed), anchored at the seed quarter.
    ax.plot(shadow_x, shadow_y, color=_SHADOW, lw=1.8, ls=(0, (5, 3)),
            zorder=4, label="rule-implied shadow path")
    ax.scatter([shadow_x[0]], [shadow_y[0]], color=_SHADOW, s=18, zorder=5)

    # Direct end-label for the shadow path.
    ax.annotate(
        f"{shadow_y[-1]:.2f}%",
        xy=(shadow_x[-1], shadow_y[-1]),
        xytext=(6, 0),
        textcoords="offset points",
        color=_SHADOW,
        fontsize=9,
        va="center",
        fontweight="bold",
    )
    ax.annotate(
        f"MPR {res.seed_quarter}\n{shadow_y[0]:.2f}%",
        xy=(shadow_x[0], shadow_y[0]),
        xytext=(-8, 14),
        textcoords="offset points",
        color=_SHADOW,
        fontsize=8,
        va="bottom",
        ha="right",
    )

    # Restraint: drop top/right spines, no grid, sparse ticks.
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    ax.spines["left"].set_color(_MUTE)
    ax.spines["bottom"].set_color(_MUTE)
    ax.tick_params(colors=_MUTE, labelsize=8)
    ax.set_ylabel("policy rate (%)", color=_INK, fontsize=9)
    mpr_label = params.mpr_publication_date.strftime("%B %Y")
    ax.set_title(
        "BoC rule-implied shadow rate\n"
        f"ToTEM III rule on {mpr_label} MPR projections",
        color=_INK, fontsize=11, loc="left", pad=12,
    )
    ax.legend(loc="upper left", frameon=False, fontsize=8)

    # Watermark when unverified.
    if not params.verified:
        ax.text(
            0.5, 0.5,
            "UNVERIFIED — seed transcription not yet checked",
            transform=ax.transAxes,
            fontsize=15,
            color=_MUTE,
            alpha=0.35,
            ha="center",
            va="center",
            rotation=20,
            zorder=10,
        )

    fig.tight_layout()
    fig.savefig(svg_path, format="svg")
    plt.close(fig)

    _write_html(svg_path, html_path, res, params)
    return svg_path, html_path


def _write_html(svg_path: Path, html_path: Path, res: ShadowResult, params) -> None:
    """Wrap the SVG inline in a minimal self-contained HTML page."""
    svg_text = svg_path.read_text(encoding="utf-8")
    # strip XML prolog/doctype so the SVG embeds cleanly inline
    lines = [ln for ln in svg_text.splitlines()
             if not ln.lstrip().startswith("<?xml")
             and not ln.lstrip().startswith("<!DOCTYPE")]
    svg_inline = "\n".join(lines)

    status = (
        "<span style='color:#c0392b;font-weight:600'>UNVERIFIED DRAFT</span>"
        if not params.verified
        else "<span style='color:#2a7'>verified</span>"
    )

    mpr_label = params.mpr_publication_date.strftime("%B %Y")

    rows = "".join(
        f"<tr><td>{s.quarter}</td><td>{s.rate:.3f}</td><td>{s.gap:.3f}</td>"
        f"<td>{s.infl_tp4:.3f}</td></tr>"
        for s in res.steps
    )

    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>BoC rule-implied shadow rate — {res.seed_quarter}</title>
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
<h1>BoC rule-implied shadow rate</h1>
<div class="meta">
  ToTEM III rule (TR-119) on {mpr_label} MPR projections &middot;
  status: {status} &middot; seed {res.seed_quarter} @ {res.seed_rate:.2f}%
</div>
<figure>
{svg_inline}
</figure>
<table>
<caption>Projected quarterly path (rate, output gap, t+4 core inflation used)</caption>
<thead><tr><th>quarter</th><th>rate %</th><th>gap pp</th><th>&pi; t+4 %</th></tr></thead>
<tbody>{rows}</tbody>
</table>
<p class="note">
  Internal Sibley Creek research tool. This is the ToTEM III rule-implied policy
  path on the {mpr_label} MPR projections with transparent interpolation
  assumptions &mdash; NOT a recovery of the Bank's actual internal conditioning
  path. The MPR forecast is itself conditioned on a market-implied rate path, and
  the Bank's internal path carries judgmental add-factors; rule coefficients were
  estimated 1993Q4-2015Q4. The shaded band is the mechanical sensitivity envelope
  across the published neutral and potential-growth range corners. See the
  methodology note in claude-ref/research/shadow_rate/.
</p>
</body>
</html>
"""
    html_path.write_text(html, encoding="utf-8")
