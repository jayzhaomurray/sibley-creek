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

from pipeline.io.format import (
    ValueKind,
    fmt_delta as _canon_fmt_delta,
    fmt_value as _canon_fmt_value,
)

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
        positive_is_good:   editorial semantic flag describing whether an
                            upward move in this series is "good" (True),
                            "bad" (False), or ambient/no-side (None).
                            NOT used to drive `deltaDir` -- per
                            design-system.md Section 4 the glyph encodes
                            direction-of-change, not direction-of-goodness.
                            Preserved on the config because a future
                            editorial "WORSE / BETTER / UNCHANGED" stamp
                            (separate from the directional glyph) will
                            consume it.
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
    # Delta-comparator window. "prior" picks the prior row (default; right
    # for monthly/quarterly cadence). "w/w" picks the row nearest 7 calendar
    # days back from the latest observation (right for daily series like
    # FX, yields, commodities -- d/d moves are noise; w/w is the macro read).
    # When "w/w", the displayed delta string is suffixed " w/w".
    delta_window: str = "prior"


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
        # Daily series: compare to ~7 calendar days ago, not yesterday.
        delta_window="w/w",
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
        print_indicator="Goods trade balance, 3mma",
        as_of_format="month-year",
        delta_kind="level",
        positive_is_good=True,  # surplus widening reads positive
    ),
}


# --------------------------------------------------------------------------- #
# Supporting prints (the homepage tile carries the load-bearing print PLUS
# 2-3 supporting prints per section, per editorial canon in src/data/sections.ts).
#
# Each entry is shaped like a stripped-down SectionConfig:
#   key                  -> matches the canon `key` on SectionPrint in sections.ts
#   indicator            -> human-readable label rendered above the value
#   primary_series       -> base CSV slug for the value (no .csv suffix)
#   primary_dir          -> initial tier to look in ("raw"|"processed"|"derived")
#   unit_display / value_decimals / delta_decimals / delta_unit / delta_kind
#                        -> render conventions (same semantics as SectionConfig)
#   as_of_format         -> "month-year" | "quarter" | "date"
#   transform            -> optional inline derivation; one of:
#                             None              (use the raw series value as-is)
#                             "yoy"             (yoy_pct on the loaded series)
#                             "mom"             (pct_change(1) * 100)
#                             "3m_ma"           (3-month moving average)
#                             "partner_share"   (primary / secondary * 100)
#                             "spread_bps"      (primary - secondary, label as bp)
#                             "ratio_pct"       (primary * 100; for decimal ratios)
#   secondary_series     -> required when transform needs a denominator/other side
#                             ("partner_share" => denominator; "spread_bps" => other side)
#
# Order matters: supporting prints are appended after the primary in the
# section's prints[] array, in the order declared below.
# --------------------------------------------------------------------------- #

@dataclass(frozen=True)
class SupportingPrintSpec:
    """One supporting print (non-load-bearing) for a homepage section tile."""

    key: str
    indicator: str
    primary_series: str
    primary_dir: str
    unit_display: str
    value_decimals: int
    delta_decimals: int
    delta_unit: str
    delta_kind: str  # "pp" | "level" | "bps" | "pct"
    as_of_format: str  # "month-year" | "quarter" | "date"
    transform: Optional[str] = None  # None | "yoy" | "mom" | "3m_ma" | "partner_share" | "spread_bps" | "ratio_pct"
    secondary_series: Optional[str] = None
    secondary_dir: Optional[str] = None
    notes: Optional[str] = None  # free-form for the audit trail; not rendered
    # See SectionConfig.delta_window. "prior" default = iloc[-2] (1 step
    # back in the series' native cadence). "w/w" = row nearest 7 calendar
    # days back from the latest observation. Markets daily series should
    # use "w/w" so the tile delta reads as a macro move, not day-trader
    # noise.
    delta_window: str = "prior"


# Per-section supporting prints. Each tuple is ordered; the homepage tile
# renders them in declaration order, after the section's load-bearing print.
# An entry whose primary CSV is not on disk yields a sentinel print with TK
# strings (we still emit the row so the tile layout doesn't shift around).
SUPPORTING_PRINTS: dict[str, tuple[SupportingPrintSpec, ...]] = {
    "gdp": (
        SupportingPrintSpec(
            key="gdp-mm",
            indicator="Real GDP, m/m",
            primary_series="gdp_monthly",
            primary_dir="raw",
            unit_display="%",
            value_decimals=1,
            delta_decimals=1,
            delta_unit="pp",
            delta_kind="pp",
            as_of_format="month-year",
            transform="mom",
            notes="MoM % on the StatCan monthly real-GDP level (Table 36-10-0434-01).",
        ),
        # gdp-percap-yoy and output-gap require series not yet in pipeline
        # (pop_total quarterly, BoC MPR output gap). Declared so the print
        # row renders TK rather than being silently dropped from the tile.
        SupportingPrintSpec(
            key="gdp-percap-yoy",
            indicator="Per-capita GDP, y/y",
            primary_series="gdp_per_capita_yoy",
            primary_dir="processed",
            unit_display="%",
            value_decimals=1,
            delta_decimals=1,
            delta_unit="pp",
            delta_kind="pp",
            as_of_format="quarter",
            transform=None,
            notes=(
                "Quarterly real GDP per capita, Y/Y % change. Derived in "
                "pipeline.build.derive_gdp_per_capita_yoy from gdp_quarterly "
                "(v62305752) divided by pop_total (v1, Table 17-10-0009-01)."
            ),
        ),
        SupportingPrintSpec(
            key="output-gap",
            indicator="Output gap",
            primary_series="output_gap_mpr",
            primary_dir="raw",
            unit_display="%",
            value_decimals=1,
            delta_decimals=1,
            delta_unit="pp",
            delta_kind="pp",
            as_of_format="quarter",
            transform=None,
            notes=(
                "BoC MPR output gap (INDINF_OUTGAPMPR_Q), quarterly %. Canonical "
                "per Wave 5 methodology resolution C.1; not an HP-filter."
            ),
        ),
    ),
    "inflation": (
        # BoC publishes the trim/median series as Y/Y % already; the raw
        # CSV is in percent (no transform needed). cpi_trim.csv first values
        # are ~3.0, confirming this is the published Y/Y.
        SupportingPrintSpec(
            key="core-trim-yoy",
            indicator="Core-trim, y/y",
            primary_series="cpi_trim",
            primary_dir="raw",
            unit_display="%",
            value_decimals=1,
            delta_decimals=1,
            delta_unit="pp",
            delta_kind="pp",
            as_of_format="month-year",
            transform=None,
        ),
        SupportingPrintSpec(
            key="core-median-yoy",
            indicator="Core-median, y/y",
            primary_series="cpi_median",
            primary_dir="raw",
            unit_display="%",
            value_decimals=1,
            delta_decimals=1,
            delta_unit="pp",
            delta_kind="pp",
            as_of_format="month-year",
            transform=None,
        ),
        SupportingPrintSpec(
            key="cpi-breadth-gt3",
            indicator="CPI breadth >3%",
            primary_series="cpi_breadth_gt3",
            primary_dir="processed",
            unit_display="%",
            value_decimals=1,
            delta_decimals=1,
            delta_unit="pp",
            delta_kind="pp",
            as_of_format="month-year",
            transform=None,
            notes=(
                "Share of the 60-component CPI basket (2024 weights) with Y/Y "
                "inflation > 3%. Derived in pipeline.build.derive_cpi_breadth_gt3 "
                "from data/raw/cpi_components.csv and data/derived/"
                "cpi_component_weights_canada.json."
            ),
        ),
    ),
    "labour": (
        SupportingPrintSpec(
            key="agg-hours-yoy",
            indicator="Aggregate hours, y/y",
            primary_series="aggregate_hours",
            primary_dir="raw",
            unit_display="%",
            value_decimals=1,
            delta_decimals=1,
            delta_unit="pp",
            delta_kind="pp",
            as_of_format="month-year",
            transform="yoy",
            notes="YoY % on raw monthly aggregate hours level (StatCan v4391505).",
        ),
        SupportingPrintSpec(
            key="wage-lfs-micro",
            indicator="Wage growth (LFS-Micro)",
            primary_series="lfs_micro",
            primary_dir="raw",
            unit_display="%",
            value_decimals=1,
            delta_decimals=1,
            delta_unit="pp",
            delta_kind="pp",
            as_of_format="month-year",
            transform=None,
            notes="BoC publishes LFS-Micro as Y/Y % already; no transform needed.",
        ),
        SupportingPrintSpec(
            key="emp-rate",
            indicator="Employment rate",
            primary_series="employment_rate",
            primary_dir="raw",
            unit_display="%",
            value_decimals=1,
            delta_decimals=1,
            delta_unit="pp",
            delta_kind="pp",
            as_of_format="month-year",
            transform=None,
            notes=(
                "Employment-to-population ratio (per-capita employment). Statistics "
                "Canada LFS Table 14-10-0287, v2062817; Canada total, 15+, SA."
            ),
        ),
        # EI Regular Beneficiaries (Wave 5 brief: Labour Panel 7 home; surfaced
        # on the homepage tile as a Y/Y supporting print for the cyclical-
        # inflection signal). StatCan Table 14-10-0011 v64549350; CSV stores
        # raw counts in persons. Y/Y % is the canonical headline transform on
        # the tile (Panel 7 default-view is level in thousands; the tile uses
        # Y/Y because three-digit thousands look noisy in a small row).
        SupportingPrintSpec(
            key="ei-regular-beneficiaries-yoy",
            indicator="EI regular beneficiaries, y/y",
            primary_series="ei_regular_beneficiaries",
            primary_dir="raw",
            unit_display="%",
            value_decimals=1,
            delta_decimals=1,
            delta_unit="pp",
            delta_kind="pp",
            as_of_format="month-year",
            transform="yoy",
            notes=(
                "Y/Y % change in EI regular benefits recipients (StatCan v64549350, "
                "Canada total SA). Demand-side cyclical-inflection signal; uptake "
                "tends to lead LFS unemployment by ~1-2 months. Wave 5 add."
            ),
        ),
    ),
    "housing": (
        SupportingPrintSpec(
            key="housing-starts-3mma",
            indicator="Housing starts, 3mma",
            primary_series="housing_starts",
            primary_dir="raw",
            unit_display="k",  # render as e.g. "240k" (thousands of SAAR units)
            value_decimals=0,
            delta_decimals=0,
            delta_unit="k",
            delta_kind="level",
            as_of_format="month-year",
            transform="3m_ma",
            notes="3-month MA of raw monthly housing starts (units SAAR); displayed in thousands.",
        ),
        SupportingPrintSpec(
            key="cmhc-arrears",
            indicator="Bank mortgage arrears",
            primary_series="cba_mortgage_arrears_national",
            primary_dir="raw",
            unit_display="%",
            value_decimals=2,
            delta_decimals=2,
            delta_unit="pp",
            delta_kind="pp",
            as_of_format="month-year",
            transform=None,
            notes=(
                "Residential mortgage arrears rate, Canada, monthly (Canadian "
                "Bankers Association DB50). Covers chartered banks plus "
                "Manulife / Laurentian / Equitable -- the chartered-bank slice "
                "(~75% of mortgage stock). Closest available proxy for the "
                "discontinued CMHC arrears series. Cadence: monthly with "
                "~2.5-month publication lag. Fetched via pipeline.fetch."
                "cba_arrears. The print key remains 'cmhc-arrears' (preserved "
                "for editorial-canon continuity in src/data/sections.ts) but "
                "the indicator label is 'Bank mortgage arrears' because the "
                "underlying series is CBA, not CMHC."
            ),
        ),
        # months-inventory dropped: CREA does not publish a national MOI series
        # in any free / scriptable channel (their stats portal is dashboard-
        # only), and BoC Valet's CREA bundle (FVI_CREA_*) does not include MOI.
        # Derivation from active listings / sales requires a new fetcher; the
        # existing crea_snlr.csv (sales-to-new-listings ratio) covers the same
        # tightness signal and is already plumbed elsewhere. Dropped 2026-05-11
        # rather than ship a TK; the housing tile renders one fewer supporting
        # row.
        # Housing affordability (Wave 5 brief: Housing Panel 7 home; surfaced
        # on the homepage tile as the level of the BoC qualifying-payment-to-
        # income ratio). BoC INDINF_AFFORD_Q, quarterly. Source value is a
        # decimal ratio (e.g. 0.43 = 43% of household income required to carry
        # qualifying mortgage payment); rendered as % on the tile.
        SupportingPrintSpec(
            key="housing-affordability",
            indicator="Housing affordability",
            primary_series="housing_affordability",
            primary_dir="raw",
            unit_display="%",
            value_decimals=1,
            delta_decimals=1,
            delta_unit="pp",
            delta_kind="pp",
            as_of_format="quarter",
            transform="ratio_pct",
            notes=(
                "BoC qualifying-mortgage-payment-to-income ratio, quarterly. "
                "Source value is a decimal ratio (0.43 = 43%); transform "
                "'ratio_pct' multiplies by 100 for tile display. Wave 5 add."
            ),
        ),
    ),
    "policy": (
        SupportingPrintSpec(
            key="goc-2y",
            indicator="2y GoC yield",
            primary_series="yield_2yr",
            primary_dir="raw",
            unit_display="%",
            value_decimals=2,
            delta_decimals=0,
            delta_unit="bps",
            delta_kind="bps",
            as_of_format="date",
            transform=None,
        ),
        SupportingPrintSpec(
            key="boc-fed-spread",
            indicator="BoC-Fed spread, 2y",
            primary_series="yield_2yr",
            primary_dir="raw",
            unit_display="bps",  # render as e.g. "-150 bps"
            value_decimals=0,
            delta_decimals=0,
            delta_unit="bps",
            # "level" delta_kind (not "bps"): the spread_bps transform already
            # converts to basis points, so delta is a straight difference in
            # bps. delta_kind='bps' would multiply by 100 again.
            delta_kind="level",
            as_of_format="date",
            transform="spread_bps",
            secondary_series="us_2yr",
            secondary_dir="raw",
            notes="GoC 2y minus UST 2y, in basis points. Inner-joined on date.",
        ),
        # Federal budget balance (FY YTD): the DoF Fiscal Monitor headline
        # framing. Single-month balance is too noisy (one-month seasonality
        # dominates); FY-to-date cumulative is what Fiscal Monitor commentary
        # and Big-Six economics desks actually cite. Comparison is the same
        # FY-YTD figure one fiscal year prior (e.g. "FY26 YTD through Feb
        # vs FY25 YTD through Feb"), NOT month-over-month (which collapses
        # to the current month's monthly balance and re-introduces the
        # noise we're trying to suppress).
        #
        # The chart reference rule (dashed line at 2.75% on the policy-rate
        # sparkline) is preserved separately via SECTION_CONFIGS['policy']
        # .reference_value=2.75.
        #
        # primary_series='federal_budget_ytd' is the cumsum-within-FY view
        # derived in pipeline.build.derive_federal_fiscal_ytd(). Source CSV
        # is in CAD millions; renderer rescales to billions via
        # unit_display='B'.
        SupportingPrintSpec(
            key="federal-budget-balance",
            indicator="Federal budget balance (FYTD)",
            primary_series="federal_budget_ytd",
            primary_dir="processed",
            unit_display="B",
            value_decimals=1,
            delta_decimals=1,
            delta_unit="B",
            delta_kind="level",
            as_of_format="month-year",
            transform="fy_ytd_yoy",
            notes=(
                "Cumulative federal budgetary balance, fiscal-year-to-date "
                "(Canadian FY = April-March reset). Latest value is current-FY "
                "YTD through the most recent reported month; comparator is the "
                "prior FY's YTD through the SAME month (not the prior month). "
                "DoF Fiscal Monitor headline framing. CAD millions on disk -> "
                "CAD billions on tile. Source: DoF Fiscal Monitor, ~2-month "
                "lag, derived in pipeline.build.derive_federal_fiscal_ytd."
            ),
        ),
    ),
    "markets": (
        SupportingPrintSpec(
            key="goc-10y",
            indicator="10y GoC yield",
            primary_series="yield_10yr",
            primary_dir="raw",
            unit_display="%",
            value_decimals=2,
            delta_decimals=0,
            delta_unit="bps",
            delta_kind="bps",
            as_of_format="date",
            transform=None,
            delta_window="w/w",
        ),
        SupportingPrintSpec(
            key="tsx-composite",
            indicator="TSX Composite",
            primary_series="tsx_composite",
            primary_dir="raw",
            unit_display="",
            value_decimals=0,
            delta_decimals=1,
            delta_unit="%",
            delta_kind="pct",
            as_of_format="date",
            transform=None,
            delta_window="w/w",
            notes=(
                "S&P/TSX Composite price index (Yahoo ^GSPTSE). Lands daily via "
                "pipeline.build_financial. NB: Yahoo's range='max' silently switches "
                "to monthly resolution for index symbols; sp500 and gold_futures have "
                "the same quirk. For dense daily history use range='5y' or '10y'."
            ),
        ),
        SupportingPrintSpec(
            key="wti",
            indicator="WTI",
            primary_series="wti",
            primary_dir="raw",
            unit_display="",  # rendered as e.g. "71.4"
            value_decimals=1,
            delta_decimals=1,
            delta_unit="%",
            delta_kind="pct",
            as_of_format="date",
            transform=None,
            delta_window="w/w",
        ),
    ),
    "trade": (
        SupportingPrintSpec(
            key="current-account",
            indicator="Current account",
            primary_series="current_account_balance",
            primary_dir="raw",
            unit_display="B",
            value_decimals=1,
            delta_decimals=1,
            delta_unit="B",
            delta_kind="level",
            as_of_format="quarter",
            transform=None,
            notes=(
                "Headline quarterly current-account balance (StatCan Table "
                "36-10-0018-01 v61915304, SA, C$ millions on disk -> C$ billions "
                "on tile). Stacked-bar decomposition (goods/services/primary/"
                "secondary) lives in the trade Panel 2 panel_data slot."
            ),
        ),
        SupportingPrintSpec(
            key="us-partner-share",
            indicator="US export share",
            primary_series="trade_exports_us",
            primary_dir="raw",
            unit_display="%",
            value_decimals=1,
            delta_decimals=1,
            delta_unit="pp",
            delta_kind="pp",
            as_of_format="month-year",
            transform="partner_share",
            secondary_series="trade_exports_total",
            secondary_dir="raw",
            notes="Share of US in total Canadian merchandise exports (customs basis), monthly SA.",
        ),
        SupportingPrintSpec(
            key="terms-of-trade",
            indicator="Terms of trade",
            primary_series="terms_of_trade",
            primary_dir="processed",
            unit_display="",
            value_decimals=1,
            delta_decimals=1,
            delta_unit="",
            delta_kind="level",
            as_of_format="quarter",
            transform=None,
            notes=(
                "Terms-of-trade index = exports IPI / imports IPI x 100. Derived "
                "from StatCan Table 36-10-0106 (GDP price indexes, quarterly SA) "
                "in pipeline.build.derive_terms_of_trade. National-accounts "
                "convention; covers all merchandise + services (distinct from "
                "BoC commodity ToT, which is BCPI-derived)."
            ),
        ),
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


def _resolve_value_kind(unit_display: str, value_decimals: int) -> ValueKind:
    """Map (unit_display, value_decimals) -> canonical formatter kind.

    Heuristics:
      'B'   -> currency_cad (CAD millions on disk, billions on display)
      '%'   -> rate_level if value_decimals >= 2 (yields, policy rate)
               else percent (Y/Y series, 1 decimal)
      'bps' -> basis_points
      'k'   -> count (raw values already in thousands on disk)
      ''    -> fx if value_decimals >= 3 (USDCAD)
               else index_level (TSX, WTI, terms-of-trade)
    """
    if unit_display == "B":
        return "currency_cad"
    if unit_display == "%":
        return "rate_level" if value_decimals >= 2 else "percent"
    if unit_display == "bps":
        return "basis_points"
    if unit_display == "k":
        # Disk values are already scaled to thousands (e.g. housing_starts).
        return "count_thousands"
    if unit_display == "":
        return "fx" if value_decimals >= 3 else "index_level"
    return "percent"


def _resolve_delta_kind(unit_display: str, delta_kind: str) -> ValueKind:
    """Map the legacy delta_kind enum -> canonical formatter kind."""
    if delta_kind == "bps":
        return "basis_points"
    if delta_kind == "pct":
        return "percent"
    if delta_kind == "level":
        if unit_display == "B":
            return "currency_cad"
        if unit_display == "k":
            return "count_thousands"
        if unit_display == "":
            return "index_level"
        if unit_display == "bps":
            # Spread already in bps; delta is a straight bps difference.
            return "basis_points"
        return "percent_pp"
    # "pp" | "yoy"
    return "percent_pp"


def _format_value(v: float, cfg: SectionConfig) -> str:
    """Render the headline value per the section's unit conventions."""
    kind = _resolve_value_kind(cfg.unit_display, cfg.value_decimals)
    return _canon_fmt_value(v, kind=kind, decimals=cfg.value_decimals)


def _format_delta(latest: float, prior: float, cfg: SectionConfig) -> str:
    """Compute and render the delta string in the section's preferred units.

    When `cfg.delta_window == "w/w"`, the period suffix is appended to the
    rendered string ("+0.4% w/w"). The convention follows Bay Street / FT
    practice: monthly and quarterly prints carry their period implicitly
    in the asOf stamp ("Mar 2026", "2025Q4") so a bare delta reads as m/m
    or q/q; daily prints (asOf "May 8, 2026") leave the comparator window
    ambiguous, so the delta must name it.
    """
    kind = _resolve_delta_kind(cfg.unit_display, cfg.delta_kind)
    if cfg.delta_kind == "bps":
        diff = (latest - prior) * 100.0
    elif cfg.delta_kind == "pct":
        if prior == 0:
            base = _canon_fmt_delta(0.0, kind="percent", decimals=cfg.delta_decimals)
            return f"{base} w/w" if cfg.delta_window == "w/w" else base
        diff = (latest / prior - 1.0) * 100.0
    else:
        diff = latest - prior
    base = _canon_fmt_delta(diff, kind=kind, decimals=cfg.delta_decimals)
    return f"{base} w/w" if cfg.delta_window == "w/w" else base


def _resolve_delta_dir(latest: float, prior: float, cfg: SectionConfig) -> str:
    """Map delta sign to editorial direction (pos/neg/neutral).

    Per design-system.md Section 4 (the direction-by-glyph canon): the
    glyph encodes direction-of-CHANGE, not direction-of-goodness. A rise
    in inflation, unemployment, or USDCAD all render with the up-triangle
    because the value went up. The `positive_is_good` flag on the catalog
    is preserved for future editorial features (e.g. a separate
    WORSE/BETTER/UNCHANGED semantic stamp) but it MUST NOT drive
    `deltaDir`.

    Tolerance: a delta whose magnitude is below half the last printed
    decimal is treated as 'neutral' so the tile does not render
    "+0.0 pp" or "-0.0 pp" next to an up/down triangle. The comparison
    is done in the SAME UNITS the delta is displayed in (pp, %, bps, or
    billions), so the threshold and the rendered string agree.
    """
    if cfg.delta_kind == "bps":
        # Displayed as "+/-X bps" with delta_decimals=0 by convention; the
        # smallest visible motion is 1 bps, so half-step is 0.5 bps.
        diff_display = (latest - prior) * 100.0
        threshold = 0.5 * (10 ** -cfg.delta_decimals)
    elif cfg.delta_kind == "pct":
        if prior == 0:
            return "neutral"
        diff_display = (latest / prior - 1.0) * 100.0
        threshold = 0.5 * (10 ** -cfg.delta_decimals)
    elif cfg.delta_kind == "level" and cfg.unit_display == "B":
        # Trade balance: stored in CAD millions, displayed in CAD billions.
        # Compare in billions so the threshold matches the printed decimal.
        diff_display = (latest - prior) / 1000.0
        threshold = 0.5 * (10 ** -cfg.delta_decimals)
    else:
        # "pp" | "yoy" | "level" (non-B units): displayed difference is in
        # the same units as the raw values.
        diff_display = latest - prior
        threshold = 0.5 * (10 ** -cfg.delta_decimals)
    if abs(diff_display) < threshold:
        return "neutral"
    return "pos" if diff_display > 0 else "neg"


def _format_as_of(d: pd.Timestamp, kind: str) -> str:
    """Render a reference period stamp."""
    if kind == "date":
        return d.strftime("%b %-d, %Y") if hasattr(d, "strftime") and _supports_dash(d) \
            else d.strftime("%b %d, %Y").replace(" 0", " ")
    if kind == "quarter":
        return f"{d.year}Q{((d.month - 1) // 3) + 1}"
    if kind == "fy-ytd-month":
        # Canadian federal fiscal year runs April-March. The FY label takes
        # the END year of the FY (FY26 = April 2025 through March 2026).
        # A row dated 2026-02-28 falls in FY26; 2025-05-31 also FY26;
        # 2025-03-31 falls in FY25. Format: "FYTD Feb 26" (compact;
        # the FY-end-year short tag disambiguates which FY the YTD covers).
        if d.month >= 4:
            fy_end_year = d.year + 1
        else:
            fy_end_year = d.year
        fy_short = fy_end_year % 100
        return f"FYTD {d.strftime('%b')} {fy_short:02d}"
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
# Supporting print helpers
# --------------------------------------------------------------------------- #

def _format_value_for_spec(v: float, spec) -> str:
    """Render a single value per a spec-like object's unit conventions.

    `spec` is either a SectionConfig or a SupportingPrintSpec; both expose
    `unit_display` and `value_decimals`. Routes through the canonical
    formatter (pipeline.io.format) so output matches the homepage tile
    and the chart-builder frontend formatter exactly.
    """
    kind = _resolve_value_kind(spec.unit_display, spec.value_decimals)
    return _canon_fmt_value(v, kind=kind, decimals=spec.value_decimals)


def _format_delta_for_spec(latest: float, prior: float, spec) -> str:
    """Render a delta per the spec's delta_kind / delta_unit.

    Routes through the canonical formatter. Mirrors _format_delta but
    accepts a SupportingPrintSpec (or SectionConfig). When the spec's
    `delta_window == "w/w"`, the period suffix is appended.
    """
    kind = _resolve_delta_kind(spec.unit_display, spec.delta_kind)
    if spec.delta_kind == "bps":
        diff = (latest - prior) * 100.0
    elif spec.delta_kind == "pct":
        if prior == 0:
            base = _canon_fmt_delta(0.0, kind="percent", decimals=spec.delta_decimals)
            return f"{base} w/w" if getattr(spec, "delta_window", "prior") == "w/w" else base
        diff = (latest / prior - 1.0) * 100.0
    else:
        diff = latest - prior
    base = _canon_fmt_delta(diff, kind=kind, decimals=spec.delta_decimals)
    return f"{base} w/w" if getattr(spec, "delta_window", "prior") == "w/w" else base


def _resolve_delta_dir_for_spec(latest: float, prior: float, spec) -> str:
    """Direction-of-change classification for a supporting-print spec.

    Same canon as _resolve_delta_dir: glyph encodes change direction, with
    a half-decimal neutrality threshold so 0.0 doesn't sit next to a glyph.
    """
    kind = spec.delta_kind
    if kind == "bps":
        diff_display = (latest - prior) * 100.0
    elif kind == "pct":
        if prior == 0:
            return "neutral"
        diff_display = (latest / prior - 1.0) * 100.0
    elif kind == "level" and spec.unit_display == "B":
        diff_display = (latest - prior) / 1000.0
    elif kind == "level" and spec.unit_display == "k":
        # Already in thousands; no rescale needed.
        diff_display = latest - prior
    else:
        diff_display = latest - prior
    threshold = 0.5 * (10 ** -spec.delta_decimals)
    if abs(diff_display) < threshold:
        return "neutral"
    return "pos" if diff_display > 0 else "neg"


def _apply_supporting_transform(
    spec: SupportingPrintSpec,
    primary: _LoadedSeries,
    secondary: Optional[_LoadedSeries],
) -> Optional[pd.DataFrame]:
    """Apply spec.transform to the loaded primary (+optional secondary) and
    return a DataFrame with columns [date, value] suitable for sparkline /
    latest-value extraction.

    Returns None on a transform error (logged); the caller emits TK.
    """
    df = primary.data.sort_values("date").reset_index(drop=True)
    if df.empty:
        return None
    transform = spec.transform
    if transform is None:
        return df
    s = df.set_index("date")["value"].sort_index()
    try:
        if transform == "yoy":
            out = s.pct_change(12) * 100.0
        elif transform == "mom":
            out = s.pct_change(1) * 100.0
        elif transform == "3m_ma":
            out = s.rolling(3, min_periods=3).mean()
        elif transform == "fy_ytd_yoy":
            # Pass-through on the spark/series shape: the underlying CSV is
            # already the FY-YTD cumulative balance. The "prior" comparator
            # for the latest value is resolved date-wise (12 months back =
            # same FY-YTD-month one fiscal year prior) inside
            # _build_supporting_print, not here.
            out = s
        elif transform == "partner_share":
            if secondary is None or secondary.data.empty:
                return None
            t = secondary.data.set_index("date")["value"].sort_index()
            joined = pd.concat([s.rename("p"), t.rename("t")], axis=1).dropna()
            out = (joined["p"] / joined["t"]) * 100.0
        elif transform == "ratio_pct":
            # Multiply a decimal ratio by 100 to render as a percent on the
            # tile (e.g. BoC housing affordability index is 0.43 -> 43.0%).
            out = s * 100.0
        elif transform == "spread_bps":
            # Result remains in PERCENT (not bps yet); formatting layer
            # multiplies by 100 when delta_kind=='bps'. For consistent
            # rendering, we return the percent difference and let
            # _format_value_for_spec/unit_display='bps' multiply.
            # But our renderer expects raw percent for delta_kind='bps'
            # (value*100 happens only in delta render, not value render).
            # So convert to bps here for the displayed value.
            if secondary is None or secondary.data.empty:
                return None
            t = secondary.data.set_index("date")["value"].sort_index()
            joined = pd.concat([s.rename("p"), t.rename("t")], axis=1).dropna()
            # Multiply by 100 to convert pp -> bps so the value renders directly.
            out = (joined["p"] - joined["t"]) * 100.0
        else:
            logger.warning("site_data: unknown transform %r on %s", transform, spec.key)
            return None
    except Exception as exc:  # noqa: BLE001
        logger.warning("site_data: transform %r failed on %s: %s: %s",
                       transform, spec.key, type(exc).__name__, exc)
        return None
    out_df = out.dropna().reset_index()
    out_df.columns = ["date", "value"]
    return out_df


def _build_supporting_print(spec: SupportingPrintSpec, data_root: Path) -> dict:
    """Build one supporting print entry, or a TK sentinel if data is missing.

    Always returns a dict with the SectionPrint shape; tile layout never
    shifts. Missing/unavailable data is conveyed via value/delta='TK' and
    an `available: False` flag so the loader can recognize the sentinel.
    """
    primary = _read_series(spec.primary_series, spec.primary_dir, data_root)
    secondary: Optional[_LoadedSeries] = None
    if spec.secondary_series is not None:
        secondary = _read_series(
            spec.secondary_series,
            spec.secondary_dir or spec.primary_dir,
            data_root,
        )
        if secondary is None:
            primary = None  # spread / partner-share needs both sides

    if primary is None or primary.data.empty:
        return {
            "key": spec.key,
            "indicator": spec.indicator,
            "value": "TK",
            "delta": "TK",
            "deltaDir": "neutral",
            "asOf": "TK",
            "spark": [],
            "available": False,
            "note": spec.notes,
        }

    df = _apply_supporting_transform(spec, primary, secondary)
    if df is None or df.empty or len(df) < 2:
        return {
            "key": spec.key,
            "indicator": spec.indicator,
            "value": "TK",
            "delta": "TK",
            "deltaDir": "neutral",
            "asOf": "TK",
            "spark": [],
            "available": False,
            "note": spec.notes or "transform yielded fewer than 2 observations",
        }

    latest_row = df.iloc[-1]
    latest_val = float(latest_row["value"])
    latest_date = pd.Timestamp(latest_row["date"])

    # Prior-comparator selection. Most transforms use iloc[-2] (the prior
    # observation in the cadence). Overrides:
    #   - fy_ytd_yoy: same calendar month one year prior (DoF Fiscal Monitor
    #     headline framing).
    #   - delta_window="w/w": row nearest 7 calendar days back (right for
    #     daily series like FX, yields, commodities).
    # Each falls back to iloc[-2] if the target lookback point isn't on
    # disk with sufficient proximity.
    if spec.transform == "fy_ytd_yoy":
        prior_date_target = latest_date - pd.DateOffset(years=1)
        date_diff = (df["date"] - prior_date_target).abs()
        nearest_idx = int(date_diff.idxmin())
        if date_diff.iloc[nearest_idx] <= pd.Timedelta(days=3):
            prior_val = float(df.iloc[nearest_idx]["value"])
        else:
            prior_val = float(df.iloc[-2]["value"])
    elif spec.delta_window == "w/w":
        prior_date_target = latest_date - pd.Timedelta(days=7)
        date_diff = (df["date"] - prior_date_target).abs()
        nearest_idx = int(date_diff.idxmin())
        # Sanity: must be within +/- 2 days of the 7-day target and must
        # be at least 4 calendar days back (otherwise it's effectively a
        # d/d move). Fall back to iloc[-2] if either gate fails.
        nearest_row_date = pd.Timestamp(df.iloc[nearest_idx]["date"])
        gap_days = abs((latest_date - nearest_row_date).days)
        if date_diff.iloc[nearest_idx] <= pd.Timedelta(days=2) and gap_days >= 4:
            prior_val = float(df.iloc[nearest_idx]["value"])
        else:
            prior_val = float(df.iloc[-2]["value"])
    else:
        prior_val = float(df.iloc[-2]["value"])

    # Spark sampling: use the primary's frequency (transforms preserve
    # cadence, except spread_bps + partner_share which fall to the joined
    # cadence; both inputs share cadence in practice, so primary meta wins).
    frequency = (primary.meta.get("frequency") or "monthly").lower()
    spark = _sample_spark(df, frequency)

    return {
        "key": spec.key,
        "indicator": spec.indicator,
        "value": _format_value_for_spec(latest_val, spec),
        "delta": _format_delta_for_spec(latest_val, prior_val, spec),
        "deltaDir": _resolve_delta_dir_for_spec(latest_val, prior_val, spec),
        "asOf": _format_as_of(latest_date, spec.as_of_format),
        "spark": spark,
        "valueRaw": latest_val,
        "priorRaw": prior_val,
        "asOfISO": latest_date.date().isoformat(),
        "available": True,
    }


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
    latest_val = float(latest_row["value"])
    latest_date = pd.Timestamp(latest_row["date"])

    # Prior-comparator selection. Default is iloc[-2] (1 step back in the
    # native cadence). delta_window="w/w" picks the row nearest 7 calendar
    # days back -- right for daily series (FX, yields, commodities) where
    # d/d moves are noise and w/w is the macro read. Falls back to iloc[-2]
    # if the 7-day-back point isn't on disk with enough proximity.
    if cfg.delta_window == "w/w":
        prior_date_target = latest_date - pd.Timedelta(days=7)
        date_diff = (df["date"] - prior_date_target).abs()
        nearest_idx = int(date_diff.idxmin())
        nearest_row_date = pd.Timestamp(df.iloc[nearest_idx]["date"])
        gap_days = abs((latest_date - nearest_row_date).days)
        if date_diff.iloc[nearest_idx] <= pd.Timedelta(days=2) and gap_days >= 4:
            prior_val = float(df.iloc[nearest_idx]["value"])
        else:
            prior_val = float(df.iloc[-2]["value"])
    else:
        prior_val = float(df.iloc[-2]["value"])

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

    # Append supporting prints declared in SUPPORTING_PRINTS[cfg.slug].
    # Each supporting print is wrapped in try/except so one missing series
    # doesn't sink the others. A missing series yields a TK-sentinel print
    # so the tile layout (one row per canon key) stays stable.
    prints: list[dict] = [print_entry]
    for supporting in SUPPORTING_PRINTS.get(cfg.slug, ()):
        try:
            prints.append(_build_supporting_print(supporting, data_root))
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                "site_data: supporting print %s/%s failed: %s: %s",
                cfg.slug, supporting.key, type(exc).__name__, exc,
            )
            prints.append({
                "key": supporting.key,
                "indicator": supporting.indicator,
                "value": "TK",
                "delta": "TK",
                "deltaDir": "neutral",
                "asOf": "TK",
                "spark": [],
                "available": False,
                "note": f"build failed: {type(exc).__name__}: {exc}",
            })

    return {
        "slug": cfg.slug,
        "chartSeriesKey": cfg.chart_series_key,
        "prints": prints,
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
