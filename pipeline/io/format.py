"""Canonical value formatter for site-level + panel-level emitted strings.

Single source of truth for turning raw numeric values into short, human-
readable strings with strict character caps. Both the Python pipeline
(this module) and the TypeScript frontend (src/components/charts/_shared/
format.ts) implement the SAME rule set in parallel. Treat this docstring
as the spec; chart-builder mirrors it.

Why the caps matter
-------------------
The 96px right-gutter on chart frames (PanelLiveChart) accommodates roughly
6-7 characters of Plex Mono at 12px before spilling beyond the frame. Tile
readouts on the homepage have similar real estate. The formatter trades
precision for fit: when a raw input would produce a long string we (in
order) scale to a larger unit, drop decimals, and finally trim the sign
prefix. We never emit scientific notation, never long index-level strings
like "34,077.76", and never silently spill past the gutter.

Character caps (hard contract)
------------------------------
- headline value (fmt_value):       max 8 chars
- delta (fmt_delta):                max 8 chars
- axis tick label (fmt_tick):       max 6 chars
- direct end-of-line series label:  max 10 chars (chart-builder-only)

Kinds (the `kind` discriminator on the public API)
--------------------------------------------------
'percent'        Y/Y or M/M percent series in % space (CPI Y/Y, unrate,
                 HPI Y/Y, GDP Y/Y). Renders as "2.3%", "-4.6%". 1 decimal.
'percent_pp'     Delta in percentage points. Always signed. "+0.5 pp",
                 "-0.2 pp". 1 decimal.
'basis_points'   Delta in bps. Always integer signed. "+25 bps", "-100 bps".
'rate_level'     Yield / policy rate level. 2 decimals when < 10, 1 decimal
                 otherwise. "2.25%", "12.4%".
'currency_cad'   CAD millions on the wire, scaled to billions for display.
                 "$5.7B", "-$2.2B". Sign baked into the number.
'fx'             FX cross. 4 significant digits. "1.369", "0.732".
'index_level'    Index point or wide integer (TSX, CPI level, productivity
                 index). Scales to k/M when >= 10,000. "34.1k", "108.5".
'count'          Counts in persons / units (EI beneficiaries, housing
                 starts when given raw counts). "1.16M", "455k", "240".
'ratio'          Decimal ratio rendered as %. Input 0.43 -> "43.0%". 1
                 decimal.

Scaling rules (canonical)
-------------------------
COUNTS (`count`)
  abs < 1_000           -> "N" (no decimals)
  1_000 <= abs < 1e6    -> "Nk" with one decimal trimmed when trailing zero,
                           i.e. "1.2k", "455k"
  1e6 <= abs < 1e9      -> "N.NM"
  abs >= 1e9            -> "N.NB"

CURRENCY (`currency_cad`, input is in CAD millions by convention)
  abs(value) >= 1000    -> "$N.NB" (billions, one decimal)
  abs(value) >= 1       -> "$NM"   (whole millions; one decimal IF caller
                                    asked decimals=1 and result fits)
  abs(value) <  1       -> "$N.NM"

PERCENT (`percent`, `ratio`)
  Values are in 0-100 range (or rendered to that scale by the caller).
  1 decimal by default. Never scientific.

PERCENTAGE POINTS (`percent_pp`)
  Always signed. 1 decimal. " pp" suffix with one space.

BASIS POINTS (`basis_points`)
  Integer. Always signed. " bps" suffix with one space.

FX (`fx`)
  3 decimals when 1 <= abs < 10 ("1.369"); 4 decimals when abs < 1.

INDEX LEVEL (`index_level`)
  abs < 1_000           -> "N.N" (one decimal)
  1_000 <= abs < 10_000 -> "N,NNN" (comma-grouped, no decimals)
  abs >= 10_000         -> "NN.Nk"  (e.g. 34,078 -> "34.1k")
  abs >= 1e6            -> "N.NM"

Width budget enforcement
------------------------
After scaling, if the resulting string still exceeds the kind's cap, we:
  1. Reduce decimals by 1 (one pass).
  2. If still too long, strip the leading "+" on positives (negatives keep
     their "-"; the visual spec treats unsigned positives as readable when
     a sign is omitted to fit).
  3. As a last resort, escalate to the next scaling tier (k -> M -> B).
We never emit an empty string for a real number; we never emit scientific.

Tick labels
-----------
Axis ticks usually omit the unit suffix; the canon is "topmost y-tick
carries the unit, the rest are bare numbers". Callers pass `is_top=True`
to opt the topmost tick into the unit suffix.
"""

from __future__ import annotations

import math
from typing import Literal, Optional

ValueKind = Literal[
    "percent",
    "percent_pp",
    "basis_points",
    "rate_level",
    "currency_cad",
    "fx",
    "index_level",
    "count",
    "count_thousands",
    "ratio",
]

# Hard caps from the visual spec. fmt_value / fmt_delta / fmt_tick enforce.
HEADLINE_CAP = 8
DELTA_CAP = 8
TICK_CAP = 6
LABEL_CAP = 10  # informational; chart-builder mirrors


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #

def _is_nan(v) -> bool:
    try:
        return v is None or math.isnan(float(v))
    except (TypeError, ValueError):
        return True


def _trim_trailing_zero(s: str) -> str:
    """For mantissa-style strings like '1.0k' -> '1k'. Only used in count
    scaling per the canon (k abbreviations look better without ".0")."""
    if "." not in s:
        return s
    head, _, tail = s.partition(".")
    # Tail looks like 'Nk' or 'NM' or 'NB' or 'N' followed by suffix
    # Split into digit-portion and any suffix
    digits = ""
    suffix = ""
    for i, ch in enumerate(tail):
        if ch.isdigit():
            digits += ch
        else:
            suffix = tail[i:]
            break
    if digits and digits.rstrip("0") == "":
        return f"{head}{suffix}"
    return s


def _fmt_signed(value: float, decimals: int) -> str:
    """Format value with sign always shown ('+' for positives, '-' for negs)."""
    if value >= 0:
        return f"+{value:.{decimals}f}"
    return f"{value:.{decimals}f}"


def _scale_count(value: float, decimals: int = 1) -> str:
    """Scale a count to k / M / B per the canon. Unsigned magnitude."""
    av = abs(value)
    sign = "-" if value < 0 else ""
    if av < 1_000:
        return f"{sign}{av:.0f}"
    if av < 1_000_000:
        s = f"{av / 1_000:.{decimals}f}k"
        return f"{sign}{_trim_trailing_zero(s)}"
    if av < 1_000_000_000:
        s = f"{av / 1_000_000:.{decimals}f}M"
        return f"{sign}{_trim_trailing_zero(s)}"
    s = f"{av / 1_000_000_000:.{decimals}f}B"
    return f"{sign}{_trim_trailing_zero(s)}"


def _scale_currency_cad(value_millions: float, decimals: int = 1) -> str:
    """Scale a CAD-millions value to a $-prefixed display string.

    Sign is baked into the number, e.g. -$2.2B. Caller specifies decimals
    for the billion-scale case; whole-millions render without decimals.
    """
    av = abs(value_millions)
    sign = "-" if value_millions < 0 else ""
    if av >= 1_000:
        # Billions
        s = f"{av / 1_000:.{decimals}f}B"
        return f"{sign}${s}"
    if av >= 1:
        # Millions; integer for compactness
        s = f"{av:.0f}M"
        return f"{sign}${s}"
    # Sub-million; render to 1-decimal million
    s = f"{av:.1f}M"
    return f"{sign}${s}"


def _scale_index_level(value: float, decimals: int = 1) -> str:
    """Scale an index level. <1000 keeps decimals; 1000-9999 comma-grouped
    integer; >=10_000 abbreviates to k; >=1e6 to M.

    Scaled tiers (k, M) force at least 1 decimal so a value like 34,077
    renders as "34.1k" rather than "34k" -- the brief's canonical rule.
    """
    av = abs(value)
    sign = "-" if value < 0 else ""
    if av < 1_000:
        return f"{sign}{av:.{decimals}f}"
    if av < 10_000:
        return f"{sign}{av:,.0f}"
    scaled_decimals = max(decimals, 1)
    if av < 1_000_000:
        return f"{sign}{av / 1_000:.{scaled_decimals}f}k"
    return f"{sign}{av / 1_000_000:.{scaled_decimals}f}M"


def _enforce_cap(s: str, cap: int, *, allow_strip_plus: bool = True) -> str:
    """If `s` is over `cap`, try to fit by trimming the leading '+' sign.
    Returns s unchanged if it already fits, or no further trimming is safe.

    This is the last-resort tightener; the caller-side scaling rules above
    do most of the work. We never silently truncate digits — better to lose
    the explicit '+' than to corrupt the value.
    """
    if len(s) <= cap:
        return s
    if allow_strip_plus and s.startswith("+"):
        return s[1:]
    return s


# --------------------------------------------------------------------------- #
# Public API
# --------------------------------------------------------------------------- #

def fmt_value(
    value: Optional[float],
    *,
    kind: ValueKind,
    decimals: Optional[int] = None,
) -> str:
    """Format a headline value (the big readout in a panel/tile).

    Returns a short, human-readable string respecting HEADLINE_CAP (8 chars).
    Returns "TK" for None or NaN inputs (canonical missing-data sentinel).

    `decimals` overrides the per-kind default when supplied; otherwise the
    canon default for the kind applies.
    """
    if _is_nan(value):
        return "TK"
    v = float(value)

    if kind == "percent":
        d = 1 if decimals is None else decimals
        s = f"{v:.{d}f}%"
    elif kind == "percent_pp":
        d = 1 if decimals is None else decimals
        s = f"{_fmt_signed(v, d)} pp"
    elif kind == "basis_points":
        s = f"{_fmt_signed(v, 0)} bps"
    elif kind == "rate_level":
        if abs(v) < 10:
            d = 2 if decimals is None else decimals
        else:
            d = 1 if decimals is None else decimals
        s = f"{v:.{d}f}%"
    elif kind == "currency_cad":
        d = 1 if decimals is None else decimals
        s = _scale_currency_cad(v, decimals=d)
    elif kind == "fx":
        if abs(v) < 1:
            d = 4 if decimals is None else decimals
        else:
            d = 3 if decimals is None else decimals
        s = f"{v:.{d}f}"
    elif kind == "index_level":
        d = 1 if decimals is None else decimals
        s = _scale_index_level(v, decimals=d)
    elif kind == "count":
        d = 1 if decimals is None else decimals
        s = _scale_count(v, decimals=d)
    elif kind == "count_thousands":
        # Input is ALREADY scaled to thousands (e.g. housing_starts on disk
        # stores 246 to mean 246_000 units SAAR). Append the "k" suffix
        # without further scaling unless the magnitude crosses into M-range.
        d = 0 if decimals is None else decimals
        av = abs(v)
        sign = "-" if v < 0 else ""
        if av >= 1_000:
            # 1,234 (thousands) = 1.23M units
            mag = max(d, 1)
            s = f"{sign}{av / 1_000:.{mag}f}M"
        else:
            s = f"{sign}{av:.{d}f}k"
    elif kind == "ratio":
        # Input is a decimal ratio; multiply by 100 and render as percent.
        d = 1 if decimals is None else decimals
        s = f"{v * 100.0:.{d}f}%"
    else:
        raise ValueError(f"fmt_value: unknown kind {kind!r}")

    return _enforce_cap(s, HEADLINE_CAP)


def fmt_delta(
    delta: Optional[float],
    *,
    kind: ValueKind,
    decimals: Optional[int] = None,
    neutral_threshold: Optional[float] = None,
) -> str:
    """Format a signed delta string respecting DELTA_CAP (8 chars).

    Returns "" when `delta` is None or NaN. Otherwise always emits a sign.

    `neutral_threshold` allows the caller to clamp small drifts to "+0..."
    without changing the sign convention; below the threshold we still
    emit a string (so the field is never empty) but the caller decides
    the deltaDir glyph separately.
    """
    if _is_nan(delta):
        return ""
    v = float(delta)

    if kind == "percent":
        d = 1 if decimals is None else decimals
        s = f"{_fmt_signed(v, d)}%"
    elif kind == "percent_pp":
        d = 1 if decimals is None else decimals
        s = f"{_fmt_signed(v, d)} pp"
    elif kind == "basis_points":
        s = f"{_fmt_signed(v, 0)} bps"
    elif kind == "rate_level":
        # A delta on a rate level: typically rendered in bps. But if caller
        # passes 'rate_level' explicitly for the delta, honour: signed %.
        d = 2 if decimals is None else decimals
        s = f"{_fmt_signed(v, d)}%"
    elif kind == "currency_cad":
        d = 1 if decimals is None else decimals
        av = abs(v)
        sign = "+" if v >= 0 else "-"
        if av >= 1_000:
            mag = f"{av / 1_000:.{d}f}B"
        elif av >= 1:
            mag = f"{av:.0f}M"
        else:
            mag = f"{av:.1f}M"
        s = f"{sign}${mag}"
    elif kind == "fx":
        d = 3 if decimals is None else decimals
        s = _fmt_signed(v, d)
    elif kind == "index_level":
        # Delta on an index: pct change usually; raw point change when small.
        d = 1 if decimals is None else decimals
        s = _fmt_signed(v, d)
    elif kind == "count":
        d = 1 if decimals is None else decimals
        av = abs(v)
        sign = "+" if v >= 0 else "-"
        if av < 1_000:
            mag = f"{av:.0f}"
        elif av < 1_000_000:
            mag = _trim_trailing_zero(f"{av / 1_000:.{d}f}k")
        elif av < 1_000_000_000:
            mag = _trim_trailing_zero(f"{av / 1_000_000:.{d}f}M")
        else:
            mag = _trim_trailing_zero(f"{av / 1_000_000_000:.{d}f}B")
        s = f"{sign}{mag}"
    elif kind == "count_thousands":
        d = 0 if decimals is None else decimals
        av = abs(v)
        sign = "+" if v >= 0 else "-"
        if av >= 1_000:
            mag = max(d, 1)
            s = f"{sign}{av / 1_000:.{mag}f}M"
        else:
            s = f"{sign}{av:.{d}f}k"
    elif kind == "ratio":
        d = 1 if decimals is None else decimals
        # Treat ratio deltas as percentage-point moves (post-multiplication).
        s = f"{_fmt_signed(v * 100.0, d)} pp"
    else:
        raise ValueError(f"fmt_delta: unknown kind {kind!r}")

    return _enforce_cap(s, DELTA_CAP)


def fmt_tick(
    value: Optional[float],
    *,
    kind: ValueKind,
    is_top: bool = False,
    decimals: Optional[int] = None,
) -> str:
    """Format an axis tick label respecting TICK_CAP (6 chars).

    Same scaling rules as fmt_value but the unit suffix (%, bps, pp) is
    only shown on the topmost tick by canon. Pass `is_top=True` for that
    one tick; all others render the bare number.
    """
    if _is_nan(value):
        return ""
    v = float(value)

    if kind in ("percent", "ratio"):
        d = 1 if decimals is None else decimals
        if kind == "ratio":
            v = v * 100.0
        s = f"{v:.{d}f}{'%' if is_top else ''}"
    elif kind == "percent_pp":
        d = 1 if decimals is None else decimals
        s = f"{v:.{d}f}{' pp' if is_top else ''}"
    elif kind == "basis_points":
        s = f"{int(round(v))}{' bps' if is_top else ''}"
    elif kind == "rate_level":
        d = 2 if (decimals is None and abs(v) < 10) else (1 if decimals is None else decimals)
        s = f"{v:.{d}f}{'%' if is_top else ''}"
    elif kind == "currency_cad":
        d = 1 if decimals is None else decimals
        base = _scale_currency_cad(v, decimals=d)
        # Strip the '$' for non-top ticks; keep for top.
        if not is_top and base.startswith("$"):
            s = base[1:]
        elif not is_top and base.startswith("-$"):
            s = "-" + base[2:]
        else:
            s = base
    elif kind == "fx":
        d = 3 if decimals is None else decimals
        s = f"{v:.{d}f}"
    elif kind == "index_level":
        d = 1 if decimals is None else decimals
        s = _scale_index_level(v, decimals=d)
    elif kind == "count":
        d = 1 if decimals is None else decimals
        s = _scale_count(v, decimals=d)
    elif kind == "count_thousands":
        d = 0 if decimals is None else decimals
        av = abs(v)
        sign = "-" if v < 0 else ""
        if av >= 1_000:
            mag = max(d, 1)
            s = f"{sign}{av / 1_000:.{mag}f}M"
        else:
            s = f"{sign}{av:.{d}f}{'k' if is_top else ''}"
    else:
        raise ValueError(f"fmt_tick: unknown kind {kind!r}")

    return _enforce_cap(s, TICK_CAP)


# --------------------------------------------------------------------------- #
# Compatibility shim: map the legacy site_data spec fields onto the new API.
# --------------------------------------------------------------------------- #

def kind_for_unit(
    unit_display: str,
    delta_unit: str,
    delta_kind: str,
) -> tuple[ValueKind, ValueKind]:
    """Translate the legacy (unit_display, delta_unit, delta_kind) triple on
    SectionConfig / SupportingPrintSpec to (value_kind, delta_kind) on the
    new formatter API.

    Returns (kind_for_value, kind_for_delta).
    """
    # Value kind first.
    if unit_display == "B":
        value_kind: ValueKind = "currency_cad"
    elif unit_display == "%":
        value_kind = "percent"
    elif unit_display == "bps":
        value_kind = "basis_points"
    elif unit_display == "k":
        value_kind = "count"
    elif unit_display == "":
        # Bare number -- FX or index. Heuristic: delta_kind 'pct' on a bare
        # number suggests FX/equity. Default to 'fx' for sub-10 values,
        # 'index_level' otherwise. The site_data layer keeps a per-spec
        # override via the caller.
        value_kind = "index_level"
    else:
        value_kind = "percent"

    # Delta kind.
    if delta_kind == "bps":
        delta_k: ValueKind = "basis_points"
    elif delta_kind == "pct":
        delta_k = "percent"
    elif delta_kind == "level":
        if unit_display == "B":
            delta_k = "currency_cad"
        elif unit_display == "k":
            delta_k = "count"
        elif unit_display == "":
            delta_k = "index_level"
        elif unit_display == "%":
            delta_k = "percent_pp"
        else:
            delta_k = "percent_pp"
    elif delta_kind == "pp":
        delta_k = "percent_pp"
    else:  # "yoy"
        delta_k = "percent_pp"
    return value_kind, delta_k
