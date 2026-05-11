"""Build the homepage data bundle the Astro side consumes at build time.

This module reads selected CSV + .meta.json files from data/processed/ and
data/derived/ (with a sensible fallback into data/raw/ for series the
pipeline does not transform), extracts the per-section homepage tile fields
the frontend needs, and emits a single JSON file at:

    data/site/sections.json

The frontend `src/data/sections.ts` keeps editorial canon -- slug, label,
accentVar, kicker, headlineQuestion, cadence, tileLine, blurb -- and reads
the data layer (this module's output) only for the values that change with
each pipeline run: prints[], updatedAt, asOf stamps, sparklines, and the
optional reference rules (CPI 2%, Policy 2.75% neutral midpoint, etc.).

The expected swap on the frontend side is mechanical:

    import siteData from "../../data/site/sections.json";
    // merge siteData[section.slug] into each entry in the existing
    // `sections` array, preserving the editorial canon fields.

Section-to-vector mapping (audit target for editorial-director)
---------------------------------------------------------------
gdp        -> data/processed/gdp_monthly_yoy.csv  (if landed)  | reference: 1.6 (potential growth midpoint, BoC MPR)
inflation  -> data/processed/cpi_all_items_yoy.csv             | reference: 2.0 (BoC target)
labour     -> data/raw/lfs_ca_unemployment_rate.csv            | reference: None (no consensus NAIRU on the tile)
housing    -> data/processed/crea_hpi_canada_yoy.csv (if landed)| reference: 0.0 (nominal zero -- price level stationarity)
policy     -> data/raw/overnight_rate_target.csv               | reference: 2.75 (BoC neutral-rate midpoint, Apr 2026 MPR)
markets    -> data/raw/fxusdcad.csv                            | reference: None (ambient color only)
trade      -> data/processed/trade_balance_total_3m_ma.csv (if landed)
                                                               | reference: 0.0 (balance neutral)

Sparkline sampling convention
-----------------------------
- monthly  series: last 24 months                          (e.g. inflation, labour, housing, trade)
- quarterly series: last 8 quarters                         (e.g. gdp_quarterly, output_gap_mpr)
- daily    series: weekly-sampled, last 30 weeks            (e.g. markets / fxusdcad)
- weekly   series: last 30 weeks                            (e.g. yield_10yr if used)

Sampling functions live in `_sample_spark()` below; the convention is
data-driven from the series' frequency tag in .meta.json so a future
re-routing (e.g. switching markets to GoC 10y) does not require new code.

Failure policy
--------------
Per-section construction is wrapped in try/except: if a section's primary
series CSV is missing or malformed, we emit a sentinel entry with the
section's slug, an `error` string explaining what was missing, and an empty
prints[] list. The frontend can render the existing placeholder content for
that slot. Loud-fail at the orchestrator level is the wrong design here
because v1 may legitimately ship before every section's series has landed
(e.g. CREA HPI lags the CPI / LFS pipeline by several days).
"""

from __future__ import annotations

import json
import logging
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import pandas as pd

logger = logging.getLogger("pipeline.io.site_data")

SCHEMA_VERSION = 1

# Canon section slugs, ordered by the frontend's `sections[]` array. The
# frontend's `SectionSlug` type matches this list exactly; tests assert that.
SECTION_SLUGS: tuple[str, ...] = (
    "gdp",
    "inflation",
    "labour",
    "housing",
    "policy",
    "markets",
    "trade",
)


# --------------------------------------------------------------------------- #
# Per-section configuration
# --------------------------------------------------------------------------- #

@dataclass(frozen=True)
class SectionConfig:
    """Maps a homepage section to the pipeline series that feeds its tile.

    Fields:
        slug:               canon section slug (matches src/data/sections.ts)
        primary_series:     filename slug (without .csv) of the lead series;
                            this drives the tile value, delta, sparkline,
                            and updatedAt timestamp.
        primary_dir:        which data tier to look in first
                            ("processed" | "derived" | "raw"). The reader
                            falls through to the other two if the file is
                            missing in the preferred tier.
        unit_display:       what to render next to the value, e.g. "%",
                            "bps", "" (for FX). Distinct from the meta.json
                            `units` string, which is the canonical
                            measurement label.
        value_decimals:     number of decimals in the displayed value.
        delta_decimals:     number of decimals in the displayed delta.
        delta_unit:         "pp" (percentage points) or "%" (percent change)
                            or "bps" (basis points) or "" (raw).
        reference_value:    the analytical reference rule plotted on the tile
                            sparkline (e.g. 2.0 for the BoC CPI target).
        reference_label:    a short label for the reference rule
                            (e.g. "Target 2%", "Neutral 2.75%").
        chart_series_key:   matches `chartSeriesKey` in src/data/sections.ts
                            so the hero chart can route to the correct
                            series. Must match a `key` in prints[] below.
        print_key:          the `key` slot on the lead SectionPrint entry.
        print_indicator:    the human-readable "indicator" label rendered
                            above the value on the tile. Matches the existing
                            frontend phrasing.
        as_of_format:       how to format the most-recent reference period
                            into the `asOf` string ("month-year" | "date" |
                            "quarter").
        delta_kind:         "level" -> delta = latest - prior (units = unit_display)
                            "yoy"   -> delta = latest - 12mo-prior (pp; only meaningful
                                        for percent series; equivalent to "level" with prior=lag(12))
                            "pp"    -> delta = latest - prior, force "pp" label
                            "bps"   -> delta = (latest - prior) * 100, label "bps"
                            "pct"   -> delta = (latest / prior - 1) * 100, label "%"
        positive_is_good:   for deltaDir resolution. True means an increase
                            is "pos" (e.g. employment up). False means a
                            decrease is "pos" (e.g. unemployment down,
                            inflation cooling). None means "neutral always"
                            (the editorial reading on FX, yields, etc).
    """

    slug: str
    primary_series: str
    primary_dir: str  # "processed" | "derived" | "raw"
    unit_display: str
    value_decimals: int
    delta_decimals: int
    delta_unit: str
    reference_value: Optional[float]
    reference_label: Optional[str]
    chart_series_key: str
    print_key: str
    print_indicator: str
    as_of_format: str
    delta_kind: str
    positive_is_good: Optional[bool]


# Editorial mapping. Editorial-director audits this block when scoping each
# section's load-bearing tile value. Adjustments here propagate to the JSON
# output without code changes elsewhere.
SECTION_CONFIGS: dict[str, SectionConfig] = {
    "gdp": SectionConfig(
        slug="gdp",
        primary_series="gdp_monthly_yoy",
        primary_dir="processed",
        unit_display="%",
        value_decimals=1,
        delta_decimals=1,
        delta_unit="pp",
        reference_value=1.6,
        reference_label="Potential growth ~1.6%",
        chart_series_key="gdp-yoy",
        print_key="gdp-yoy",
        print_indicator="Real GDP, y/y",
        as_of_format="month-year",
        delta_kind="pp",
        positive_is_good=True,
    ),
    "inflation": SectionConfig(
        slug="inflation",
        primary_series="cpi_all_items_yoy",
        primary_dir="processed",
        unit_display="%",
        value_decimals=1,
        delta_decimals=1,
        delta_unit="pp",
        reference_value=2.0,
        reference_label="BoC target 2%",
        chart_series_key="cpi-yoy",
        print_key="cpi-yoy",
        print_indicator="Headline CPI, y/y",
        as_of_format="month-year",
        delta_kind="pp",
        positive_is_good=False,
    ),
    "labour": SectionConfig(
        slug="labour",
        # Researcher resolution pending on whether to aggregate provincials
        # or use the national LFS UR. Wire the national LFS UR (v2062815)
        # for v1; the provincials are also on disk if needed for a more
        # nuanced read later.
        primary_series="lfs_ca_unemployment_rate",
        primary_dir="raw",
        unit_display="%",
        value_decimals=1,
        delta_decimals=1,
        delta_unit="pp",
        reference_value=None,
        reference_label=None,
        chart_series_key="unrate",
        print_key="unrate",
        print_indicator="Unemployment rate",
        as_of_format="month-year",
        delta_kind="pp",
        positive_is_good=False,
    ),
    "housing": SectionConfig(
        slug="housing",
        primary_series="crea_hpi_canada_yoy",
        primary_dir="processed",
        unit_display="%",
        value_decimals=1,
        delta_decimals=1,
        delta_unit="pp",
        reference_value=0.0,
        reference_label="Nominal zero",
        chart_series_key="hpi-yoy",
        print_key="hpi-yoy",
        print_indicator="MLS HPI, y/y",
        as_of_format="month-year",
        delta_kind="pp",
        positive_is_good=None,  # housing direction is ambient color in v1
    ),
    "policy": SectionConfig(
        slug="policy",
        primary_series="overnight_rate_target",
        primary_dir="processed",
        unit_display="%",
        value_decimals=2,
        delta_decimals=0,
        delta_unit="bps",
        reference_value=2.75,
        reference_label="Neutral midpoint 2.75%",
        chart_series_key="policy-rate",
        print_key="policy-rate",
        print_indicator="BoC overnight rate",
        as_of_format="month-year",
        delta_kind="bps",
        # Easing (rate cut) reads as "pos" in the editorial frame on policy
        # when the cycle is restrictive; that is the v1 framing and matches
        # the existing src/data/sections.ts placeholder ("deltaDir: 'pos'"
        # on the -25 bps print).
        positive_is_good=False,
    ),
    "markets": SectionConfig(
        slug="markets",
        primary_series="fxusdcad",
        primary_dir="raw",
        unit_display="",  # FX renders as a bare number, e.g. "1.378"
        value_decimals=3,
        delta_decimals=1,
        delta_unit="%",
        reference_value=None,
        reference_label=None,
        chart_series_key="usdcad",
        print_key="usdcad",
        print_indicator="USDCAD",
        as_of_format="date",
        delta_kind="pct",
        # CAD weakening (USDCAD up) is editorial "neg" by convention --
        # imports more expensive, hits CPI pass-through. Matches the
        # existing placeholder.
        positive_is_good=False,
    ),
    "trade": SectionConfig(
        slug="trade",
        primary_series="trade_balance_total_3m_ma",
        primary_dir="processed",
        unit_display="B",  # rendered as e.g. "-$2.3B"
        value_decimals=1,
        delta_decimals=1,
        delta_unit="B",
        reference_value=0.0,
        reference_label="Balance neutral",
        chart_series_key="trade-balance",
        print_key="trade-balance",
        print_indicator="Merch trade balance, 3M MA",
        as_of_format="month-year",
        delta_kind="level",
        positive_is_good=True,  # surplus widening reads positive
    ),
}


# --------------------------------------------------------------------------- #
# Disk readers
# --------------------------------------------------------------------------- #

@dataclass
class _LoadedSeries:
    """A series read off disk with its sidecar meta."""

    name: str
    data: pd.DataFrame  # columns: date, value
    meta: dict
    source_path: Path  # the CSV path actually loaded from


def _read_series(
    name: str,
    preferred_dir: str,
    data_root: Path,
) -> Optional[_LoadedSeries]:
    """Find `<name>.csv` in data/<preferred_dir>/ first; fall through to
    the other tiers in order: processed -> derived -> raw.

    Returns None if the file is not on disk anywhere. Surfaces a logger
    warning so the build log shows which series were missing.
    """
    tiers = [preferred_dir] + [t for t in ("processed", "derived", "raw") if t != preferred_dir]
    for tier in tiers:
        csv_path = data_root / tier / f"{name}.csv"
        meta_path = data_root / tier / f"{name}.meta.json"
        if csv_path.exists():
            try:
                df = pd.read_csv(csv_path, parse_dates=["date"])
            except Exception as exc:  # noqa: BLE001
                logger.warning(
                    "site_data: failed to parse %s: %s: %s",
                    csv_path, type(exc).__name__, exc,
                )
                return None
            # Drop rows where value is NaN -- never feed a NaN to the tile.
            if "value" in df.columns:
                df = df.dropna(subset=["value"]).reset_index(drop=True)
            meta: dict = {}
            if meta_path.exists():
                try:
                    meta = json.loads(meta_path.read_text(encoding="utf-8"))
                except Exception as exc:  # noqa: BLE001
                    logger.warning(
                        "site_data: failed to parse meta %s: %s: %s",
                        meta_path, type(exc).__name__, exc,
                    )
                    meta = {}
            return _LoadedSeries(name=name, data=df, meta=meta, source_path=csv_path)
    logger.warning("site_data: series '%s' not found in any data tier", name)
    return None


# --------------------------------------------------------------------------- #
# Sampling / formatting
# --------------------------------------------------------------------------- #

def _sample_spark(df: pd.DataFrame, frequency: str) -> list[float]:
    """Down-sample a series to the per-frequency sparkline shape.

        monthly    -> last 24 points
        quarterly  -> last 8 points
        weekly     -> last 30 points
        daily      -> weekly-resampled, last 30 points

    Returns a plain list[float] suitable for JSON serialization. Empty
    input yields an empty list.
    """
    if df.empty or "value" not in df.columns:
        return []
    freq = (frequency or "").lower()
    if freq == "daily":
        # Resample to weekly (Friday close); take the last value of each week.
        s = df.set_index("date")["value"].sort_index()
        weekly = s.resample("W-FRI").last().dropna()
        sliced = weekly.tail(30)
    elif freq == "quarterly":
        s = df.set_index("date")["value"].sort_index()
        sliced = s.tail(8)
    elif freq == "weekly":
        s = df.set_index("date")["value"].sort_index()
        sliced = s.tail(30)
    else:  # monthly / annual / irregular / unknown -> default monthly window
        s = df.set_index("date")["value"].sort_index()
        sliced = s.tail(24)
    return [float(v) for v in sliced.tolist() if not _is_nan(v)]


def _is_nan(v: float) -> bool:
    try:
        return math.isnan(float(v))
    except (TypeError, ValueError):
        return True


def _format_value(v: float, cfg: SectionConfig) -> str:
    """Render the headline value per the section's unit conventions."""
    if cfg.unit_display == "B":
        # Trade balance: CAD millions on disk -> CAD billions on tile,
        # with sign baked into the value.
        billions = v / 1000.0
        sign = "-" if billions < 0 else ""
        return f"{sign}${abs(billions):.{cfg.value_decimals}f}B"
    if cfg.unit_display == "%":
        return f"{v:+.{cfg.value_decimals}f}%" if v < 0 else f"{v:.{cfg.value_decimals}f}%"
    if cfg.unit_display == "":
        return f"{v:.{cfg.value_decimals}f}"
    return f"{v:.{cfg.value_decimals}f}{cfg.unit_display}"


def _format_delta(latest: float, prior: float, cfg: SectionConfig) -> str:
    """Compute and render the delta string in the section's preferred units."""
    if cfg.delta_kind == "bps":
        bps = (latest - prior) * 100.0
        sign = "+" if bps >= 0 else ""
        return f"{sign}{bps:.0f} bps"
    if cfg.delta_kind == "pct":
        pct = (latest / prior - 1.0) * 100.0
        sign = "+" if pct >= 0 else ""
        return f"{sign}{pct:.{cfg.delta_decimals}f}%"
    if cfg.delta_kind == "level":
        diff = latest - prior
        if cfg.unit_display == "B":
            diff_b = diff / 1000.0
            sign = "+" if diff_b >= 0 else ""
            return f"{sign}${diff_b:.{cfg.delta_decimals}f}B"
        sign = "+" if diff >= 0 else ""
        return f"{sign}{diff:.{cfg.delta_decimals}f}{cfg.delta_unit}"
    # "pp" or "yoy" -> pp delta
    diff = latest - prior
    sign = "+" if diff >= 0 else ""
    return f"{sign}{diff:.{cfg.delta_decimals}f} pp"


def _resolve_delta_dir(latest: float, prior: float, cfg: SectionConfig) -> str:
    """Map delta sign to editorial direction (pos/neg/neutral).

    Treats a delta below the format threshold as 'neutral' to keep the
    tile from rendering "+0.0 pp" with a green chevron.
    """
    if cfg.positive_is_good is None:
        return "neutral"
    diff = latest - prior
    # Threshold: smaller than 1/2 the last printed decimal.
    threshold = 0.5 * (10 ** -cfg.delta_decimals)
    if cfg.delta_kind == "bps":
        # Compare in bps space
        threshold = 0.5  # 0.5 bps
        diff = (latest - prior) * 100.0
    elif cfg.delta_kind == "pct":
        threshold = 0.5 * (10 ** -cfg.delta_decimals)
        if prior == 0:
            return "neutral"
        diff = (latest / prior - 1.0) * 100.0
    if abs(diff) < threshold:
        return "neutral"
    if cfg.positive_is_good:
        return "pos" if diff > 0 else "neg"
    return "pos" if diff < 0 else "neg"


def _format_as_of(d: pd.Timestamp, kind: str) -> str:
    """Render a reference period stamp."""
    if kind == "date":
        return d.strftime("%b %-d, %Y") if hasattr(d, "strftime") and _supports_dash(d) \
            else d.strftime("%b %d, %Y").replace(" 0", " ")
    if kind == "quarter":
        return f"{d.year}Q{((d.month - 1) // 3) + 1}"
    # "month-year"
    return d.strftime("%b %Y")


def _supports_dash(d: pd.Timestamp) -> bool:
    """%-d is POSIX; on Windows we get an error. Test once."""
    try:
        d.strftime("%-d")
        return True
    except (ValueError, AttributeError):
        return False


# --------------------------------------------------------------------------- #
# Section builders
# --------------------------------------------------------------------------- #

def _build_section(cfg: SectionConfig, data_root: Path) -> dict:
    """Construct one section's homepage payload, or an error sentinel."""
    loaded = _read_series(cfg.primary_series, cfg.primary_dir, data_root)
    if loaded is None or loaded.data.empty:
        return {
            "slug": cfg.slug,
            "chartSeriesKey": cfg.chart_series_key,
            "prints": [],
            "updatedAt": None,
            "error": f"primary series '{cfg.primary_series}' not on disk",
            "primarySeries": cfg.primary_series,
        }

    df = loaded.data.sort_values("date").reset_index(drop=True)
    if len(df) < 2:
        return {
            "slug": cfg.slug,
            "chartSeriesKey": cfg.chart_series_key,
            "prints": [],
            "updatedAt": None,
            "error": f"primary series '{cfg.primary_series}' has fewer than 2 observations",
            "primarySeries": cfg.primary_series,
        }

    latest_row = df.iloc[-1]
    prior_row = df.iloc[-2]
    latest_val = float(latest_row["value"])
    prior_val = float(prior_row["value"])
    latest_date = pd.Timestamp(latest_row["date"])

    frequency = (loaded.meta.get("frequency") or "monthly").lower()
    spark = _sample_spark(df, frequency)

    print_entry: dict = {
        "key": cfg.print_key,
        "indicator": cfg.print_indicator,
        "value": _format_value(latest_val, cfg),
        "delta": _format_delta(latest_val, prior_val, cfg),
        "deltaDir": _resolve_delta_dir(latest_val, prior_val, cfg),
        "asOf": _format_as_of(latest_date, cfg.as_of_format),
        "spark": spark,
        # Raw numeric scalars too, for any chart consumer that needs them
        # without re-parsing the formatted strings.
        "valueRaw": latest_val,
        "priorRaw": prior_val,
        "asOfISO": latest_date.date().isoformat(),
    }

    reference: Optional[dict] = None
    if cfg.reference_value is not None:
        reference = {
            "value": cfg.reference_value,
            "label": cfg.reference_label or "",
        }

    # updatedAt: epoch milliseconds. Prefer the meta's release_date when
    # present (this is when StatCan / BoC actually published); fall back
    # to the most recent observation's date when release_date is null.
    updated_at_ms = _resolve_updated_at_ms(loaded.meta, latest_date)

    return {
        "slug": cfg.slug,
        "chartSeriesKey": cfg.chart_series_key,
        "prints": [print_entry],
        "reference": reference,
        "updatedAt": updated_at_ms,
        "primarySeries": cfg.primary_series,
        "source": loaded.meta.get("source"),
        "sourceUrl": loaded.meta.get("source_url"),
        "sourceId": loaded.meta.get("source_id"),
        "units": loaded.meta.get("units"),
        "frequency": frequency,
        "releaseDate": loaded.meta.get("release_date"),
    }


def _resolve_updated_at_ms(meta: dict, latest_date: pd.Timestamp) -> int:
    """Resolve the section's `updatedAt` to epoch milliseconds (UTC).

    Order of preference:
        1. meta.release_date (the publisher's release timestamp -- the
           date the data point became public knowledge).
        2. meta.fetched_at   (the date we pulled it; second-best proxy).
        3. latest observation's reference date (worst case).

    The frontend uses this for hero-selection (the most recently updated
    section is rendered as the hero).
    """
    candidates: list[str] = []
    if meta.get("release_date"):
        candidates.append(str(meta["release_date"]))
    if meta.get("fetched_at"):
        candidates.append(str(meta["fetched_at"]))
    for cand in candidates:
        try:
            ts = pd.Timestamp(cand)
            if ts.tzinfo is None:
                ts = ts.tz_localize("UTC")
            return int(ts.timestamp() * 1000)
        except (ValueError, TypeError):
            continue
    # Fall back to the latest observation date (treated as UTC midnight).
    ts = pd.Timestamp(latest_date).tz_localize("UTC") if latest_date.tzinfo is None else latest_date
    return int(ts.timestamp() * 1000)


# --------------------------------------------------------------------------- #
# Public entry point
# --------------------------------------------------------------------------- #

def build_site_data(
    data_root: Path,
    out_path: Optional[Path] = None,
) -> dict:
    """Build the homepage data bundle and write it to disk.

    Args:
        data_root: the project's `data/` directory (contains raw/, processed/,
                   derived/, and will receive `site/sections.json`).
        out_path:  optional override for the output file. Default is
                   `<data_root>/site/sections.json`.

    Returns:
        The dict that was written (useful for tests / inspection without
        re-reading the file).
    """
    data_root = Path(data_root)
    if out_path is None:
        out_path = data_root / "site" / "sections.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    sections: dict[str, dict] = {}
    for slug in SECTION_SLUGS:
        cfg = SECTION_CONFIGS[slug]
        try:
            sections[slug] = _build_section(cfg, data_root)
        except Exception as exc:  # noqa: BLE001
            logger.error(
                "site_data: section '%s' construction failed: %s: %s",
                slug, type(exc).__name__, exc,
            )
            sections[slug] = {
                "slug": slug,
                "chartSeriesKey": cfg.chart_series_key,
                "prints": [],
                "updatedAt": None,
                "error": f"construction failed: {type(exc).__name__}: {exc}",
                "primarySeries": cfg.primary_series,
            }

    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "sections": sections,
    }
    out_path.write_text(json.dumps(payload, indent=2, sort_keys=False), encoding="utf-8")
    logger.info("site_data: wrote %s (%d sections)", out_path, len(sections))
    return payload
