"""
Sahm threshold decision-aid chart generator.
Produces:
  work/charts/sahm_threshold_judge.svg
  work/charts/sahm_threshold_judge.png  (1440x810 via cairosvg or sharp fallback)

Methodology: gap = 3-month moving average of SA unemployment rate
             minus trailing-12-month minimum of that 3mma.
             Identical to part2_sahm_calibration.py.

Run from repo root:
    py claude-ref/research/recession_watch/gen_sahm_threshold_chart.py

Dependencies: standard library only for SVG.
For PNG: cairosvg (pip install cairosvg) OR system rsvg-convert.
Falls back to noting the absence if neither is available.
"""

from __future__ import annotations

import csv
import sys
import subprocess
from datetime import datetime, date
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parents[3]
URATE_PATH = REPO_ROOT / "data" / "raw" / "unemployment_rate.csv"
SVG_OUT    = REPO_ROOT / "work" / "charts" / "sahm_threshold_judge.svg"
PNG_OUT    = REPO_ROOT / "work" / "charts" / "sahm_threshold_judge.png"


# ---------------------------------------------------------------------------
# Data helpers (verbatim from part2_sahm_calibration.py)
# ---------------------------------------------------------------------------
def load_csv(path: Path) -> list[tuple[date, float]]:
    rows = []
    with open(path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            d = datetime.strptime(row["date"], "%Y-%m-%d").date()
            v = row["value"]
            if v and v.strip():
                rows.append((d, float(v)))
    rows.sort(key=lambda x: x[0])
    return rows


def rolling_mean(series: list[float], window: int) -> list[float | None]:
    out: list[float | None] = []
    for i in range(len(series)):
        if i < window - 1:
            out.append(None)
        else:
            out.append(sum(series[i - window + 1 : i + 1]) / window)
    return out


def rolling_min(series: list[float | None], window: int) -> list[float | None]:
    out: list[float | None] = []
    for i in range(len(series)):
        if series[i] is None:
            out.append(None)
            continue
        vals = [v for v in series[max(0, i - window + 1) : i + 1] if v is not None]
        out.append(min(vals) if vals else None)
    return out


# ---------------------------------------------------------------------------
# Compute Sahm gap
# ---------------------------------------------------------------------------
urate_data = load_csv(URATE_PATH)
dates_u = [r[0] for r in urate_data]
vals_u  = [r[1] for r in urate_data]

ma3   = rolling_mean(vals_u, 3)
min12 = rolling_min(ma3, 12)

gap_series: list[tuple[date, float]] = []
for i in range(len(dates_u)):
    if ma3[i] is not None and min12[i] is not None:
        gap_series.append((dates_u[i], ma3[i] - min12[i]))

# Sanity checks
def check(label: str, got: float, expected: float, tol: float = 0.002) -> None:
    if abs(got - expected) > tol:
        print(f"  MISMATCH {label}: got {got:.4f}, expected {expected:.4f}")
        sys.exit(1)
    print(f"  OK {label}: {got:.4f}")

gap_by_date = {d: g for d, g in gap_series}
print("Sanity checks against part2_sahm_calibration.py recon table:")
check("2025-03 gap", gap_by_date[date(2025, 3, 1)], 0.633)
check("2026-04 gap", gap_by_date[date(2026, 4, 1)], 0.133)
print()

# COVID peak
covid_pts = [(d, g) for d, g in gap_series if date(2020, 1, 1) <= d <= date(2020, 12, 1)]
covid_peak_date, covid_peak_gap = max(covid_pts, key=lambda x: x[1])
print(f"COVID peak gap: {covid_peak_gap:.2f}pp on {covid_peak_date}")


# ---------------------------------------------------------------------------
# Chart geometry
# ---------------------------------------------------------------------------
# ViewBox 720 x 405
W, H = 720, 405

# Margins (px within the 720x405 viewBox)
ML = 44   # left  — room for y-tick labels
MR = 80   # right — room for threshold labels
MT = 52   # top   — room for title + subtitle
MB = 44   # bottom — x-ticks + source line

PLOT_W = W - ML - MR   # 596
PLOT_H = H - MT - MB   # 309

# Y axis: 0 to 2.0 pp (clip COVID spike)
Y_MIN = 0.0
Y_MAX = 2.0
Y_TICKS = [0.0, 0.5, 1.0, 1.5, 2.0]

# X axis: 1977-01 to 2026-12 (full data span rounded to decade boundaries + 1 year padding)
X_START = date(1977, 1, 1)
X_END   = date(2026, 12, 1)
X_SPAN_MONTHS = (X_END.year - X_START.year) * 12 + (X_END.month - X_START.month)

X_DECADE_TICKS = [1980, 1990, 2000, 2010, 2020]

# CD Howe recession bands (peak, trough) — same as calibration script
CD_HOWE = [
    (date(1981, 6, 1),  date(1982, 10, 1)),
    (date(1990, 3, 1),  date(1992, 5, 1)),
    (date(2008, 10, 1), date(2009, 5, 1)),
    (date(2020, 2, 1),  date(2020, 4, 1)),
]

# Candidate threshold lines
THRESHOLDS = [
    (0.5,  "0.5  US default"),
    (0.6,  "0.6"),
    (0.8,  "0.8"),
    (1.1,  "1.1"),
    (1.4,  "1.4"),
]

# Colors
INK          = "#15171A"
INK_FAINT    = "#6B7280"
INK_HAIRLINE = "rgba(21,23,26,0.15)"
REC_FILL     = "rgba(21,23,26,0.06)"
RED          = "#E63946"
THRESH_STROKE = "#9CA3AF"   # mid-grey, subordinate


def date_to_x(d: date) -> float:
    months = (d.year - X_START.year) * 12 + (d.month - X_START.month)
    return ML + (months / X_SPAN_MONTHS) * PLOT_W


def val_to_y(v: float) -> float:
    clamped = max(Y_MIN, min(Y_MAX, v))
    frac = (clamped - Y_MIN) / (Y_MAX - Y_MIN)
    return MT + PLOT_H - frac * PLOT_H


PLOT_TOP    = MT
PLOT_BOTTOM = MT + PLOT_H
PLOT_LEFT   = ML
PLOT_RIGHT  = ML + PLOT_W


# ---------------------------------------------------------------------------
# Build SVG
# ---------------------------------------------------------------------------
lines: list[str] = []

def emit(s: str) -> None:
    lines.append(s)

emit('<?xml version="1.0" encoding="UTF-8"?>')
emit(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
     f'preserveAspectRatio="xMidYMid meet" width="{W}" height="{H}" '
     f'style="background:#FFFFFF;font-family:Manrope,sans-serif;">')

# Font defs — no @import (web fonts won't load in rasterizer anyway; system fallbacks apply)
emit('<defs>')
emit('  <style>')
emit('    text { font-family: Manrope, sans-serif; }')
emit('    .mono { font-family: "IBM Plex Mono", monospace; }')
emit('  </style>')
emit('  <!-- clip path to keep line inside plot area -->')
emit(f'  <clipPath id="plot-clip">')
emit(f'    <rect x="{PLOT_LEFT}" y="{PLOT_TOP}" width="{PLOT_W}" height="{PLOT_H}" />')
emit(f'  </clipPath>')
emit('</defs>')


# ---------------------------------------------------------------------------
# Recession bands
# ---------------------------------------------------------------------------
emit('<!-- Recession bands -->')
for peak, trough in CD_HOWE:
    x1 = date_to_x(peak)
    x2 = date_to_x(trough)
    emit(f'<rect x="{x1:.2f}" y="{PLOT_TOP}" width="{x2-x1:.2f}" height="{PLOT_H}" fill="{REC_FILL}" />')


# ---------------------------------------------------------------------------
# Threshold lines (behind the gap line, subordinate styling)
# ---------------------------------------------------------------------------
emit('<!-- Threshold lines -->')
for thresh_val, thresh_label in THRESHOLDS:
    ty = val_to_y(thresh_val)
    # dashed: 4px on, 2px off
    emit(f'<line x1="{PLOT_LEFT}" y1="{ty:.2f}" x2="{PLOT_RIGHT}" y2="{ty:.2f}" '
         f'stroke="{THRESH_STROKE}" stroke-width="1" stroke-dasharray="4 2" />')
    # label at right terminus
    emit(f'<text x="{PLOT_RIGHT + 5}" y="{ty + 4:.2f}" '
         f'font-family="IBM Plex Mono, monospace" font-size="9" fill="{INK_FAINT}" '
         f'text-anchor="start">{thresh_label}</text>')


# ---------------------------------------------------------------------------
# Horizontal gridlines at Y ticks (non-zero, very faint)
# ---------------------------------------------------------------------------
emit('<!-- Y gridlines -->')
for ytick in Y_TICKS:
    if ytick == Y_MIN:
        continue
    gy = val_to_y(ytick)
    emit(f'<line x1="{PLOT_LEFT}" y1="{gy:.2f}" x2="{PLOT_RIGHT}" y2="{gy:.2f}" '
         f'stroke="{INK}" stroke-opacity="0.08" stroke-width="1" />')


# ---------------------------------------------------------------------------
# Plot frame: bottom rule (1px hairline) + left rule
# ---------------------------------------------------------------------------
emit('<!-- Plot frame -->')
emit(f'<line x1="{PLOT_LEFT}" y1="{PLOT_BOTTOM}" x2="{PLOT_RIGHT}" y2="{PLOT_BOTTOM}" '
     f'stroke="{INK}" stroke-width="1" />')
emit(f'<line x1="{PLOT_LEFT}" y1="{PLOT_TOP}" x2="{PLOT_LEFT}" y2="{PLOT_BOTTOM}" '
     f'stroke="{INK}" stroke-width="1" />')


# ---------------------------------------------------------------------------
# Y-axis tick labels
# ---------------------------------------------------------------------------
emit('<!-- Y axis tick labels -->')
for ytick in Y_TICKS:
    ty = val_to_y(ytick)
    label = f"{ytick:.1f}"
    emit(f'<text x="{PLOT_LEFT - 6}" y="{ty + 4:.2f}" '
         f'font-family="IBM Plex Mono, monospace" font-size="9" fill="{INK_FAINT}" '
         f'text-anchor="end">{label}</text>')
    # tick mark
    emit(f'<line x1="{PLOT_LEFT - 3}" y1="{ty:.2f}" x2="{PLOT_LEFT}" y2="{ty:.2f}" '
         f'stroke="{INK_FAINT}" stroke-width="1" />')


# ---------------------------------------------------------------------------
# X-axis decade ticks
# ---------------------------------------------------------------------------
emit('<!-- X axis decade ticks -->')
for yr in X_DECADE_TICKS:
    tx = date_to_x(date(yr, 1, 1))
    emit(f'<line x1="{tx:.2f}" y1="{PLOT_BOTTOM}" x2="{tx:.2f}" y2="{PLOT_BOTTOM + 4}" '
         f'stroke="{INK_FAINT}" stroke-width="1" />')
    emit(f'<text x="{tx:.2f}" y="{PLOT_BOTTOM + 14}" '
         f'font-family="IBM Plex Mono, monospace" font-size="9" fill="{INK_FAINT}" '
         f'text-anchor="middle">{yr}</text>')


# ---------------------------------------------------------------------------
# Gap line (clipped at Y_MAX) — 1.5px solid ink, with clip-path
# ---------------------------------------------------------------------------
emit('<!-- Sahm gap line -->')

# Build polyline points, clipping values > Y_MAX to Y_MAX
# But we need to break the line where data jumps off-scale and re-enters
# Strategy: build segments; when above Y_MAX, clip y to PLOT_TOP (top of frame).
# Because the COVID spike is a brief blip, we just clip vertically (no line break),
# which visually shows the line running to the top of the frame during the spike.

pts: list[str] = []
for d, g in gap_series:
    if d < X_START or d > X_END:
        continue
    px = date_to_x(d)
    py = val_to_y(g)   # val_to_y already clamps to [Y_MIN, Y_MAX]
    pts.append(f"{px:.2f},{py:.2f}")

emit(f'<polyline points="{" ".join(pts)}" '
     f'fill="none" stroke="{INK}" stroke-width="1.5" stroke-linejoin="round" stroke-linecap="round" '
     f'clip-path="url(#plot-clip)" />')


# ---------------------------------------------------------------------------
# COVID off-scale annotation
# (annotate near the 2020 recession band — to the right of it, at top)
# ---------------------------------------------------------------------------
emit('<!-- COVID annotation -->')
# Place annotation to the right of the 2020 band, near the top
covid_band_right = date_to_x(date(2020, 4, 1))
ann_x = covid_band_right + 5
ann_y = PLOT_TOP + 28   # below the 2.0 tick, clear of right-edge threshold labels
covid_peak_rounded = round(covid_peak_gap, 1)
emit(f'<text x="{ann_x:.2f}" y="{ann_y:.2f}" '
     f'font-family="IBM Plex Mono, monospace" font-size="8" fill="{INK_FAINT}" '
     f'text-anchor="start">2020: {covid_peak_rounded}pp (off scale)</text>')


# ---------------------------------------------------------------------------
# Latest-value red dot (2026-04)
# ---------------------------------------------------------------------------
emit('<!-- Latest value red dot -->')
latest_date, latest_gap = gap_series[-1]
ldx = date_to_x(latest_date)
ldy = val_to_y(latest_gap)
emit(f'<circle cx="{ldx:.2f}" cy="{ldy:.2f}" r="3.5" fill="{RED}" />')


# ---------------------------------------------------------------------------
# Title + subtitle
# ---------------------------------------------------------------------------
emit('<!-- Title -->')
# Title: sentence-form, terminal period, 11px bold Manrope
title_y = 18
emit(f'<text x="{PLOT_LEFT}" y="{title_y}" '
     f'font-family="Manrope, sans-serif" font-size="11" font-weight="700" fill="{INK}" '
     f'text-anchor="start">'
     f'Where each threshold fires: the Canadian Sahm gap.'
     f'</text>')

# Subtitle: micro-caps IBM Plex Mono, 8px, ink-faint
subtitle_y = 31
emit(f'<text x="{PLOT_LEFT}" y="{subtitle_y}" '
     f'font-family="IBM Plex Mono, monospace" font-size="8" fill="{INK_FAINT}" '
     f'text-anchor="start" letter-spacing="0.04em">'
     f'UNEMPLOYMENT-RATE SAHM GAP, PP — 3-MO AVG LESS TRAILING-12-MO MIN'
     f'</text>')


# ---------------------------------------------------------------------------
# Source line (below plot)
# ---------------------------------------------------------------------------
emit('<!-- Source line -->')
source_y = H - 6
source_text = (
    "SOURCE: Statistics Canada Table 14-10-0287 (LFS unemployment rate). "
    "Recession dates: C.D. Howe Institute Business Cycle Council. "
    "Sahm gap: Sibley Creek calculations."
)
emit(f'<text x="{PLOT_LEFT}" y="{source_y}" '
     f'font-family="IBM Plex Mono, monospace" font-size="7.5" fill="{INK_FAINT}" '
     f'text-anchor="start">{source_text}</text>')


emit('</svg>')

svg_text = "\n".join(lines)

SVG_OUT.parent.mkdir(parents=True, exist_ok=True)
SVG_OUT.write_text(svg_text, encoding="utf-8")
print(f"SVG written: {SVG_OUT}")


# ---------------------------------------------------------------------------
# PNG rasterization (1440x810 = 2x)
# ---------------------------------------------------------------------------
scale = 2.0  # 720 * 2 = 1440, 405 * 2 = 810

png_ok = False

# Try cairosvg
try:
    import cairosvg  # type: ignore
    cairosvg.svg2png(
        url=str(SVG_OUT),
        write_to=str(PNG_OUT),
        output_width=int(W * scale),
        output_height=int(H * scale),
    )
    print(f"PNG written via cairosvg: {PNG_OUT}  ({int(W*scale)}x{int(H*scale)})")
    png_ok = True
except (ImportError, OSError, Exception):
    pass

# Try node + sharp (available in this Astro project)
if not png_ok:
    try:
        node_script = (
            "const sharp=require('sharp'),fs=require('fs');"
            f"const svg=fs.readFileSync('{str(SVG_OUT).replace(chr(92), '/')}');"
            f"sharp(svg).resize({int(W*scale)},{int(H*scale)}).png().toFile('{str(PNG_OUT).replace(chr(92), '/')}',(_,i)=>i?console.log('ok',i):process.exit(1));"
        )
        result = subprocess.run(
            ["node", "-e", node_script],
            capture_output=True, text=True, cwd=str(REPO_ROOT),
        )
        if result.returncode == 0:
            print(f"PNG written via node/sharp: {PNG_OUT}  ({int(W*scale)}x{int(H*scale)})")
            png_ok = True
        else:
            print("node/sharp error:", result.stderr[:200])
    except FileNotFoundError:
        pass

# Try rsvg-convert (system)
if not png_ok:
    try:
        result = subprocess.run(
            ["rsvg-convert", "-w", str(int(W * scale)), "-h", str(int(H * scale)),
             "-o", str(PNG_OUT), str(SVG_OUT)],
            capture_output=True,
        )
        if result.returncode == 0:
            print(f"PNG written via rsvg-convert: {PNG_OUT}  ({int(W*scale)}x{int(H*scale)})")
            png_ok = True
    except FileNotFoundError:
        pass

# Try Inkscape
if not png_ok:
    try:
        result = subprocess.run(
            ["inkscape", "--export-type=png",
             f"--export-filename={PNG_OUT}",
             f"--export-width={int(W * scale)}",
             str(SVG_OUT)],
            capture_output=True,
        )
        if result.returncode == 0:
            print(f"PNG written via Inkscape: {PNG_OUT}  ({int(W*scale)}x{int(H*scale)})")
            png_ok = True
    except FileNotFoundError:
        pass

if not png_ok:
    print("NOTE: No rasterizer found (cairosvg / rsvg-convert / inkscape).")
    print("  Install cairosvg:  pip install cairosvg")
    print("  The SVG is pixel-perfect; open in a browser and export at 2x if needed.")
