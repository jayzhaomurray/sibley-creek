r"""Pipeline build orchestrator: fetch -> transform -> write.

This is the Python half of the two-step build (see ARCHITECTURE.md ADR-0004).
It does not render the website; it prepares data files that the Astro side
reads at `npm run build` time.

Run from the repo root with the venv active:

    .\.venv\Scripts\python.exe -m pipeline.build

Output:
    data/raw/<name>.csv          one per upstream series, untransformed
    data/raw/<name>.meta.json    sidecar metadata
    data/processed/<name>.csv    transformed views consumed by the site
    data/processed/<name>.meta.json

Scope of this orchestrator
--------------------------
This entry point handles the monthly/quarterly/annual cadences:
    - StatCan WDS series (GDP, Inflation, Labour, Housing, Trade) per
      `pipeline/catalog/statcan_series.py`.
    - BoC Valet series with monthly/weekly/quarterly cadence (CPI core,
      output gap, expectations, balance sheet, mortgage rates) per
      `pipeline/catalog/boc_series.py` filtered to non-daily cadence.
    - DoF Fiscal Monitor (monthly, ~2-month lag) per `pipeline/fetch/dof_fiscal.py`.
    - CREA MLS HPI bulk (monthly) per `pipeline/fetch/crea.py`.
    - Cross-series derivations (per-capita employment, trade balance 3mma,
      partner-share trajectories, terms-of-trade companion, etc.) per
      `pipeline/transform/derivations.py`.

The daily-cadence Financial section lives in `pipeline/build_financial.py`
and runs on a separate post-close schedule (18:00 ET). See that module's
docstring for the rationale.

Failure policy
--------------
Each series fetch is isolated via `_safe()`. A single source going down logs
an error and continues; existing CSVs on disk are preserved so a downstream
build can still proceed with stale data. At the end, the script exits
non-zero if any task failed, so CI surfaces the failure in the run UI.
"""

from __future__ import annotations

import argparse
import logging
import os
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Optional

import pandas as pd


def datetime_now_iso() -> str:
    """ISO-formatted current UTC timestamp; isolated so tests can monkeypatch."""
    return datetime.now(timezone.utc).isoformat()

from pipeline.catalog import BOC_VALET_SERIES, IMF_SERIES, STATCAN_SERIES
from pipeline.catalog.boc_series import BocSpec
from pipeline.catalog.imf_series import ImfSpec
from pipeline.catalog.statcan_series import StatcanSpec, get_url as statcan_url
from pipeline.fetch import alberta, boc, cba_arrears, cpi_basket, cpi_components, crea, dof_fiscal, imf_weo, statcan
from pipeline.io import SeriesMeta, build_site_data, write_series
from pipeline.io.panel_data import build_all_panel_data
from pipeline.transform import yoy_pct
from pipeline.transform.derivations import (
    headline_yoy,
    partner_share_trajectory,
    six_month_annualized,
    trade_balance_3m_ma,
)

ROOT = Path(__file__).resolve().parent.parent
DATA_ROOT = ROOT / "data"
DATA_RAW = DATA_ROOT / "raw"
DATA_PROCESSED = DATA_ROOT / "processed"
DATA_DERIVED = DATA_ROOT / "derived"
DATA_SITE = DATA_ROOT / "site"

logger = logging.getLogger("pipeline.build")


# --------------------------------------------------------------------------- #
# Per-series failure isolation
# --------------------------------------------------------------------------- #

def _safe(label: str, fn: Callable[[], None], failed: list[str]) -> None:
    """Run `fn()`, catch and log any exception, append `label` to `failed`.

    Mirrors boc-tracker's `_safe()` pattern: one bad upstream does not sink
    the whole build. Stack traces go to DEBUG so the INFO log stays scannable.
    """
    logger.info("==> %s", label)
    try:
        fn()
    except Exception as exc:  # noqa: BLE001 - capture-and-report all
        logger.error("FAILED: %s -- %s: %s", label, type(exc).__name__, exc)
        logger.debug("traceback:\n%s", traceback.format_exc())
        failed.append(label)


# --------------------------------------------------------------------------- #
# StatCan catalog runner
# --------------------------------------------------------------------------- #

def _statcan_fetch_one(spec: StatcanSpec) -> Optional[pd.DataFrame]:
    """Fetch one StatCan vector per the catalog spec and write raw CSV+meta.

    Returns the raw DataFrame for downstream callers that want to chain a
    transform (e.g. compute Y/Y in-process and write to data/processed/).
    Returns None if WDS responds SUCCESS-but-empty (callers can decide how
    to treat that; we treat it as a soft failure).
    """
    result = statcan.fetch_vector(spec.vector_id, latest_n=600)
    df = result.data.copy()
    if df.empty:
        logger.warning("statcan vector v%d returned SUCCESS but no data", spec.vector_id)
        return None
    if spec.scale != 1.0:
        df["value"] = df["value"] * spec.scale

    meta = SeriesMeta(
        name=spec.name,
        source="Statistics Canada Web Data Service",
        source_url=statcan_url(spec),
        source_id=f"v{spec.vector_id}",
        units=spec.units,
        frequency=spec.frequency,
        release_date=result.release_date,
        notes=spec.notes or None,
    )
    write_series(df, meta, DATA_RAW)
    return df


def run_statcan_catalog(failed: list[str], sections: Optional[set[str]] = None) -> None:
    """Iterate the StatCan catalog. Optionally filter to a subset of sections.

    The full catalog is the source of editorial truth (researcher and
    editorial-director scoped these). Failures are isolated per-series so
    one bad probe-pending vector doesn't sink the rest.
    """
    for name, spec in STATCAN_SERIES.items():
        if sections is not None and spec.section not in sections:
            continue
        _safe(f"statcan:{name}", lambda s=spec: _statcan_fetch_one(s), failed)


# --------------------------------------------------------------------------- #
# BoC Valet catalog runner (non-daily only; daily lives in build_financial.py)
# --------------------------------------------------------------------------- #

def _boc_fetch_one(spec: BocSpec) -> Optional[pd.DataFrame]:
    """Fetch one BoC Valet series with optional MPR-vintage fallback.

    If `spec.vintage_fallbacks` is set, we try the primary key first and then
    walk the fallback list, returning the first key that yields observations.
    Per-series probe outcomes are documented in pipeline/catalog/boc_series.py.
    """
    candidates: list[str] = [spec.series_key]
    if spec.vintage_fallbacks:
        # Drop duplicates while preserving order
        seen = {spec.series_key}
        for k in spec.vintage_fallbacks:
            if k not in seen:
                candidates.append(k)
                seen.add(k)

    last_exc: Optional[Exception] = None
    chosen_key: Optional[str] = None
    fetch_result = None
    for key in candidates:
        try:
            fetch_result = boc.fetch_series(key, start_date=spec.start_date)
            chosen_key = key
            if key != spec.series_key:
                logger.info("boc %s: used vintage fallback %s", spec.name, key)
            break
        except Exception as exc:  # noqa: BLE001
            last_exc = exc
            logger.warning("boc %s: candidate %s failed: %s", spec.name, key, exc)
            continue

    if fetch_result is None or chosen_key is None:
        raise RuntimeError(
            f"All BoC Valet candidates exhausted for {spec.name}: {candidates}. "
            f"Last error: {last_exc!r}"
        )

    df = fetch_result.data.copy()
    if spec.scale != 1.0 and not df.empty:
        df["value"] = df["value"] * spec.scale

    label_block = (
        f" BoC-published label: {fetch_result.label!r}." if fetch_result.label else ""
    )
    notes = (spec.notes or "") + label_block
    notes = notes.strip() or None

    meta = SeriesMeta(
        name=spec.name,
        source="Bank of Canada Valet API",
        source_url=boc.observations_url(chosen_key),
        source_id=chosen_key,
        units=spec.units,
        frequency=spec.frequency,
        notes=notes,
    )
    write_series(df, meta, DATA_RAW)
    return df


def run_boc_catalog_non_daily(failed: list[str]) -> None:
    """Fetch every BoC Valet entry whose cadence is NOT daily.

    Daily-cadence entries (yields, FX, CEER, CORRA, BCPI/BCNEI) are run by
    `pipeline.build_financial.run_boc_catalog_daily()` on a separate schedule.
    """
    for name, spec in BOC_VALET_SERIES.items():
        if spec.cadence == "daily":
            continue
        _safe(f"boc:{name}", lambda s=spec: _boc_fetch_one(s), failed)


# --------------------------------------------------------------------------- #
# IMF WEO DataMapper catalog
# --------------------------------------------------------------------------- #

def _imf_fetch_one(spec: ImfSpec) -> Optional[pd.DataFrame]:
    """Fetch one IMF WEO DataMapper series and write raw CSV + .meta.json.

    Returns the raw DataFrame for downstream callers, or None if the API
    returns no data for this indicator/country combination.
    """
    result = imf_weo.fetch_indicator(spec.indicator_id, country=spec.country)
    df = result.data.copy()
    if df.empty:
        logger.warning("imf_weo: %s/%s returned empty DataFrame", spec.indicator_id, spec.country)
        return None

    meta = SeriesMeta(
        name=spec.name,
        source="IMF World Economic Outlook (DataMapper API)",
        source_url=imf_weo.observations_url(spec.indicator_id, spec.country),
        source_id=f"IMF-WEO/{spec.indicator_id}/{spec.country}",
        units=spec.units,
        frequency=spec.frequency,
        notes=spec.notes or None,
    )
    write_series(df, meta, DATA_RAW)
    return df


def run_imf_catalog(failed: list[str]) -> None:
    """Fetch all IMF WEO series registered in pipeline/catalog/imf_series.py."""
    for name, spec in IMF_SERIES.items():
        _safe(f"imf:{name}", lambda s=spec: _imf_fetch_one(s), failed)


# --------------------------------------------------------------------------- #
# DoF Fiscal Monitor
# --------------------------------------------------------------------------- #

def fetch_dof_fiscal_monitor() -> None:
    """Find and parse the most recent DoF Fiscal Monitor issue.

    Walks back up to 6 months until a 200-OK page is found, then writes two
    headline series (monthly_balance + ytd_balance) plus an issue-summary CSV
    with revenues / expenses / public debt charges YTD scalars.
    """
    html_bytes, ref_year, ref_month = dof_fiscal.find_available_issue(lookback_months=6)
    issue = dof_fiscal.parse_issue(html_bytes, ref_year, ref_month)

    monthly_meta = SeriesMeta(
        name="dof_fiscal_monthly_balance",
        source="Department of Finance Canada -- Fiscal Monitor",
        source_url=issue.url,
        source_id=f"FM-{issue.reference_year}-{issue.reference_month:02d}",
        units="CAD millions",
        frequency="monthly",
        notes=(
            f"Federal monthly budgetary balance, current FY {issue.fiscal_year_label}. "
            f"Issue published for reference period through {ref_year}-{ref_month:02d}. "
            "Source publishes in C$ millions; scale to billions for chart display."
        ),
    )
    write_series(issue.monthly_balance, monthly_meta, DATA_RAW)

    ytd_meta = SeriesMeta(
        name="dof_fiscal_ytd_balance",
        source="Department of Finance Canada -- Fiscal Monitor",
        source_url=issue.url,
        source_id=f"FM-{issue.reference_year}-{issue.reference_month:02d}",
        units="CAD millions",
        frequency="monthly",
        notes=(
            f"Federal fiscal-YTD balance through each month, FY {issue.fiscal_year_label}. "
            "Cumulative from April (FY start). Source publishes in C$ millions."
        ),
    )
    write_series(issue.ytd_balance, ytd_meta, DATA_RAW)

    # Continuous monthly balance series spanning prior FY + current FY.
    # The Fiscal Monitor monthly-balance table carries both FY columns; we
    # concatenate them so the Policy supporting-print row has 12-24 months of
    # history (enough for a sparkline). CAD millions.
    federal_balance_meta = SeriesMeta(
        name="federal_budget_balance",
        source="Department of Finance Canada -- Fiscal Monitor",
        source_url=issue.url,
        source_id=f"FM-{issue.reference_year}-{issue.reference_month:02d}",
        units="CAD millions",
        frequency="monthly",
        notes=(
            f"Federal monthly budgetary balance, continuous series spanning prior FY "
            f"and current FY {issue.fiscal_year_label}. Prior-FY months are finalized; "
            f"current-FY months reported through {ref_year}-{ref_month:02d}. "
            "Source publishes in C$ millions; scale to billions for tile display."
        ),
    )
    write_series(issue.monthly_balance_two_fy, federal_balance_meta, DATA_RAW)

    # Issue summary: revenues, expenses, public debt charges YTD scalars.
    # Stored as a one-row CSV keyed by issue reference date so it's append-
    # friendly across future issues if needed.
    issue_date = pd.Timestamp(year=ref_year, month=ref_month, day=1) + pd.offsets.MonthEnd(0)
    summary_df = pd.DataFrame([{
        "date": issue_date,
        "revenues_ytd_cad_millions": issue.revenues_ytd,
        "expenses_ytd_cad_millions": issue.expenses_ytd,
        "public_debt_charges_ytd_cad_millions": issue.public_debt_charges_ytd,
        "fiscal_year_label": issue.fiscal_year_label,
    }])
    summary_meta = SeriesMeta(
        name="dof_fiscal_ytd_summary",
        source="Department of Finance Canada -- Fiscal Monitor",
        source_url=issue.url,
        source_id=f"FM-{issue.reference_year}-{issue.reference_month:02d}",
        units="CAD millions (per-column)",
        frequency="monthly",
        notes=(
            "One-row YTD summary parsed from Fiscal Monitor Table 2 (budgetary "
            "transactions summary). NaN values indicate the parser did not find "
            "a matching row label on this issue; check raw HTML for layout drift."
        ),
    )
    write_series(summary_df, summary_meta, DATA_RAW)


# --------------------------------------------------------------------------- #
# CREA MLS HPI (monthly bulk XLSX)
# --------------------------------------------------------------------------- #

CREA_GEOGRAPHIES = ("canada", "toronto", "vancouver", "montreal", "calgary", "ottawa", "edmonton")


def fetch_crea_mls_hpi() -> None:
    """Pull the latest CREA MLS HPI ZIP and extract Composite SA HPI for the
    seven canon geographies (per dashboard_purpose 4.4 element 1).

    Each geography writes:
        data/raw/crea_hpi_<geo>.csv (+ .meta.json) -- raw monthly HPI level
        data/processed/crea_hpi_<geo>_yoy.csv      -- Y/Y % change
        data/processed/crea_hpi_<geo>_6m_ar.csv    -- 6-month annualized
    """
    zip_bytes, release_label = crea.find_available_release(lookback=4)
    for geo in CREA_GEOGRAPHIES:
        # Each geography is its own _safe call so one bad sheet doesn't kill others.
        def _do(geo_local: str = geo) -> None:
            result = crea.fetch_geography(zip_bytes, geo_local, release_label)
            raw_meta = SeriesMeta(
                name=f"crea_hpi_{geo_local}",
                source="Canadian Real Estate Association -- MLS HPI",
                source_url=crea.release_url_for(release_label),
                source_id=f"CREA-HPI-{result.sheet_name}",
                units="Index, 2005=100 (Composite HPI, SA)",
                frequency="monthly",
                release_date=release_label.replace("_", "-01-")[:10] if release_label else None,
                notes=(
                    f"CREA Composite HPI SA, geography '{geo_local}' "
                    f"(sheet {result.sheet_name!r}); release {release_label}. "
                    "CMAs are board-territory CMA-equivalent, not StatCan CMA boundaries."
                ),
            )
            write_series(result.data, raw_meta, DATA_RAW)

            # YoY % change (canon 4.4 element 1: "Y/Y and 6-month annualized")
            yoy = headline_yoy(result.data, periods_per_year=12)
            yoy_meta = SeriesMeta(
                name=f"crea_hpi_{geo_local}_yoy",
                source=raw_meta.source,
                source_url=raw_meta.source_url,
                source_id=raw_meta.source_id,
                units="%",
                frequency="monthly",
                notes="Year-over-year % change in Composite HPI SA. Derived.",
                transform="yoy_pct(periods_per_year=12)",
            )
            write_series(yoy, yoy_meta, DATA_PROCESSED)

            # 6-month annualized rate (canon 4.4 element 1)
            six_m = six_month_annualized(result.data, periods_per_year=12)
            six_m_meta = SeriesMeta(
                name=f"crea_hpi_{geo_local}_6m_ar",
                source=raw_meta.source,
                source_url=raw_meta.source_url,
                source_id=raw_meta.source_id,
                units="% (annualized)",
                frequency="monthly",
                notes="6-month annualized rate of change in Composite HPI SA. Derived.",
                transform="annualize_period_growth(period_lag=6, periods_per_year=12)",
            )
            write_series(six_m, six_m_meta, DATA_PROCESSED)
        # Per-geography safe wrapper:
        try:
            _do()
        except Exception as exc:  # noqa: BLE001
            logger.error("FAILED: crea_hpi_%s -- %s: %s", geo, type(exc).__name__, exc)
            logger.debug("traceback:\n%s", traceback.format_exc())
            raise


# --------------------------------------------------------------------------- #
# CBA mortgage arrears (PDF, monthly, ~2.5-month lag)
# --------------------------------------------------------------------------- #

def fetch_cba_mortgage_arrears() -> None:
    """Pull the latest CBA arrears PDF and emit national + provincial CSVs.

    Output:
        data/raw/cba_mortgage_arrears_national.csv    -- monthly national %
            arrears rate going back to ~1995.
        data/raw/cba_mortgage_arrears_provincial.csv  -- per-province %
            for the latest month only (cross-section snapshot).

    Replaces the (deprecated, never-landed) CMHC arrears placeholder. CBA
    covers chartered banks plus Manulife, Laurentian, and Equitable; that
    is most of the mortgage stock (~75%) but excludes credit-union and
    private-lender mortgages. The series is the closest publicly available
    proxy for the long-deprecated CMHC arrears series.
    """
    result = cba_arrears.fetch_cba_arrears(lookback=4)

    # National monthly history
    release_year, release_month = result.release_label
    release_url = cba_arrears.release_url_for(release_year, release_month)
    national_meta = SeriesMeta(
        name="cba_mortgage_arrears_national",
        source="Canadian Bankers Association",
        source_url=release_url,
        source_id=f"CBA-DB50-NATIONAL/{release_year}-{release_month}",
        units="% (arrears 3+ months / total mortgages)",
        frequency="monthly",
        release_date=result.as_of_date.date().isoformat(),
        notes=(
            "Residential mortgage arrears rate, Canada, monthly. Reporting "
            "banks: BMO, CIBC, National, RBC, Scotia, TD, Manulife (since "
            "2004), Laurentian (since 2010), Equitable (since 2020). Arrears "
            "definition: mortgages 3+ months past due / total mortgages "
            "(per CBA DB50 PUBLIC table). Closest available proxy for the "
            "discontinued CMHC arrears series. Cadence: monthly with a "
            "~2.5-month publication lag. Parsed from CBA PDF on each "
            "pipeline run; see pipeline.fetch.cba_arrears."
        ),
    )
    write_series(result.national_history, national_meta, DATA_RAW)

    # Provincial cross-section snapshot (latest month only -- CBA only
    # publishes the cross-section table in each release, not provincial
    # history; the latest snapshot is still useful for the regional read).
    provincial_meta = SeriesMeta(
        name="cba_mortgage_arrears_provincial",
        source="Canadian Bankers Association",
        source_url=release_url,
        source_id=f"CBA-DB50-PROVINCIAL/{release_year}-{release_month}",
        units="% (arrears 3+ months / total mortgages)",
        frequency="snapshot",
        release_date=result.as_of_date.date().isoformat(),
        notes=(
            "Per-province residential mortgage arrears rate, Canada, latest "
            "month only (cross-section snapshot from page 1 of the CBA PDF). "
            "Provinces: atlantic, quebec, ontario, manitoba, saskatchewan, "
            "alberta, british_columbia. CBA does not publish provincial "
            "monthly history; the cross-section is the only granular cut "
            "available without bank-by-bank disclosures."
        ),
    )
    write_series(result.provincial_snapshot, provincial_meta, DATA_RAW)


# --------------------------------------------------------------------------- #
# CPI basket weights (StatCan Table 18-10-0007-01, basket-cycle cadence)
# --------------------------------------------------------------------------- #

def fetch_cpi_basket_weights() -> None:
    """Fetch major-aggregate CPI basket weights and write a consolidated view.

    The per-aggregate vectors land via the StatCan catalog run (as
    `cpi_basket_weight_*` raw CSVs); this step lifts those into one
    cross-aggregate CSV under `data/derived/` for chart-builder.

    Output:
        data/derived/cpi_basket_weights_canada.csv
            long-format: columns date | aggregate | weight_pct
        data/derived/cpi_basket_weights_canada_wide.csv
            wide-format: one row per basket cycle, one column per aggregate
        Both get a sibling .meta.json with full provenance to Table 18-10-0007.
    """
    result = cpi_basket.fetch_basket_weights()
    if result.long.empty:
        raise RuntimeError(
            "cpi_basket: WDS returned no data for any major aggregate; "
            "likely basket-table reorganization (e.g. 2024 basket retiring)."
        )

    long_meta = SeriesMeta(
        name="cpi_basket_weights_canada",
        source="Statistics Canada Web Data Service",
        source_url=cpi_basket.TABLE_URL,
        source_id=(
            "Table 18-10-0007-01 vectors: "
            + ", ".join(f"{slug}=v{vid}" for slug, vid in cpi_basket.MAJOR_AGGREGATES.items())
        ),
        units="Weight share, % (basket link month prices)",
        frequency="annual",
        release_date=result.release_date,
        notes=(
            "Major-aggregate CPI basket weights, Canada, distribution to selected "
            "geographies, weight at basket link month prices. Long-format. Current "
            "2024 basket applies through ~2029 (next refresh per StatCan basket "
            "update schedule). all_items row is always 100.00 by construction. "
            "services_ex_shelter is omitted because StatCan publishes NULL at this "
            "cube slice; derive as services - shelter at the chart layer."
        ),
        transform="major_aggregates_basket_weights",
    )
    write_series(result.long, long_meta, DATA_DERIVED)

    wide_meta = SeriesMeta(
        name="cpi_basket_weights_canada_wide",
        source=long_meta.source,
        source_url=long_meta.source_url,
        source_id=long_meta.source_id,
        units=long_meta.units,
        frequency=long_meta.frequency,
        release_date=long_meta.release_date,
        notes=(
            "Same data as cpi_basket_weights_canada (long-format) but pivoted: "
            "one row per basket cycle, one column per aggregate. Provided for "
            "chart-builder convenience; either view is equally authoritative."
        ),
        transform="major_aggregates_basket_weights:pivoted",
    )
    write_series(result.wide, wide_meta, DATA_DERIVED)


# --------------------------------------------------------------------------- #
# CPI components (60-vector wide-format pull for breadth derivations)
# --------------------------------------------------------------------------- #

def fetch_and_write_cpi_components() -> None:
    """Fetch 60 per-component NSA CPI levels and write the wide-format CSV.

    Replaces the one-time boc-tracker lift (2026-05-11) with a daily fetch
    keyed off the same 60-vector mapping. Output shape is unchanged so the
    two breadth derivations (`derive_cpi_breadth_gt3`,
    `derive_cpi_breadth_band`) consume it without modification.
    """
    result = cpi_components.fetch_cpi_components()

    meta = SeriesMeta(
        name="cpi_components",
        source="Statistics Canada Web Data Service",
        source_url=cpi_components.TABLE_URL,
        source_id=result.source_id,
        units="Index, 2002=100 (per-component)",
        frequency="monthly",
        release_date=result.release_date,
        notes=(
            "Wide-format CSV: date x component for the 60-series CPI breadth "
            "basket. Per-component vector IDs in boc-tracker/data/"
            "cpi_breadth_mapping.json. Fetched daily via StatCan WDS (replaces "
            "the one-time 2026-05-11 lift from boc-tracker)."
        ),
        transform=None,
    )
    write_series(result.wide, meta, DATA_RAW)


# --------------------------------------------------------------------------- #
# Alberta Economic Dashboard -- AECO-equivalent natural gas (monthly)
# --------------------------------------------------------------------------- #

def fetch_alberta_natural_gas() -> None:
    """Fetch the Alberta reference natural-gas price (monthly, C$/GJ).

    Canon 4.6 element 4 calls for AECO at "weekly bid-week summary if
    achievable, else defer to v1.5". The NGX bid-week summary is gated
    behind a subscription / login and is not feasible from CI. The Alberta
    Economic Dashboard publishes a monthly Alberta reference price that
    is the AECO-equivalent monthly settle, fetched at the same shape as
    the existing WCS pattern. Cadence label is preserved as "monthly" in
    the .meta.json so chart code can flag the v1 cadence limitation.
    """
    result = alberta.fetch_natural_gas_price()
    notes_block = (
        "Alberta reference natural-gas price (C$/GJ), monthly. Used by the "
        "Government of Alberta for royalty calculations; the price tracks "
        "AECO C bid-week settles month-over-month. Canon 4.6 element 4 v1 "
        "fallback: weekly NGX bid-week is gated behind subscription and "
        "defers to v1.5. Alberta API label: "
        f"{result.type_label!r}."
    )
    meta = SeriesMeta(
        name="natural_gas_alberta",
        source="Government of Alberta -- Economic Dashboard API",
        source_url=alberta.series_url(alberta.NATURAL_GAS_UUID),
        source_id=f"alberta-dashboard:{alberta.NATURAL_GAS_UUID}",
        units=result.units or "C$/GJ",
        frequency="monthly",
        notes=notes_block,
    )
    write_series(result.data, meta, DATA_RAW)


# --------------------------------------------------------------------------- #
# Cross-series derivations
# --------------------------------------------------------------------------- #

def _read_raw(name: str) -> Optional[pd.DataFrame]:
    path = DATA_RAW / f"{name}.csv"
    if not path.exists():
        logger.warning("derivation skipped: missing raw %s", path.name)
        return None
    df = pd.read_csv(path, parse_dates=["date"])
    return df


def derive_cpi_views() -> None:
    """Compute Y/Y for headline CPI (SA and NSA) and key sub-aggregates.

    The raw monthly index series come from the StatCan catalog. We write the
    derived views into data/processed/. Per canon 4.2 the headline is Y/Y +
    3-month annualized; we add Y/Y for v1 and defer 3M-AR to the analytical
    layer (it is a one-liner on top of the level, included as a sibling
    transform here for completeness).
    """
    targets = [
        ("cpi_all_items", "headline CPI (SA)"),
        ("cpi_all_items_nsa", "headline CPI (NSA)"),
        ("cpi_shelter", "shelter CPI"),
        ("cpi_services", "services CPI"),
        ("cpi_goods", "goods CPI"),
        ("cpi_energy", "energy CPI"),
        ("cpi_food", "food CPI"),
        ("cpi_rented_accommodation", "rented accommodation CPI"),
        ("cpi_rent", "rent CPI"),
        ("cpi_owned_accommodation", "owned accommodation CPI"),
        ("cpi_mortgage_interest", "mortgage interest CPI"),
    ]
    for slug, label in targets:
        raw = _read_raw(slug)
        if raw is None:
            continue
        yoy = headline_yoy(raw, periods_per_year=12)
        spec = STATCAN_SERIES[slug]
        meta = SeriesMeta(
            name=f"{slug}_yoy",
            source="Statistics Canada Web Data Service",
            source_url=statcan_url(spec),
            source_id=f"v{spec.vector_id}",
            units="%",
            frequency="monthly",
            notes=f"Year-over-year % change in {label}. Derived from raw index.",
            transform="yoy_pct(periods_per_year=12)",
        )
        write_series(yoy, meta, DATA_PROCESSED)

    # m/m derivation for NSA headline only. Same input as Y/Y but periods=1.
    # Matches the m/m number StatCan publishes in The Daily commentary; used
    # in inflation plate-1 prose ("0.4% unadjusted" April 2026).
    raw_nsa = _read_raw("cpi_all_items_nsa")
    if raw_nsa is not None:
        ss = raw_nsa.set_index("date")["value"].sort_index()
        mm = (ss.pct_change(1) * 100).dropna().reset_index()
        mm.columns = ["date", "value"]
        spec_nsa = STATCAN_SERIES["cpi_all_items_nsa"]
        meta_mm = SeriesMeta(
            name="cpi_all_items_nsa_mm",
            source="Statistics Canada Web Data Service",
            source_url=statcan_url(spec_nsa),
            source_id=f"v{spec_nsa.vector_id}",
            units="%",
            frequency="monthly",
            notes="Month-over-month % change in headline CPI (NSA). Matches the StatCan-published m/m print on each CPI release.",
            transform="pct_change(periods=1)*100",
        )
        write_series(mm, meta_mm, DATA_PROCESSED)


def derive_cpi_services_ex_shelter_yoy() -> None:
    """Y/Y % change in basket-weighted services CPI ex-shelter.

    The Inflation Panel 6 pass-through panel (canon 4.2 element 6) right-pane
    pairs LFS-Micro composition-adjusted wage growth against services-ex-shelter
    CPI Y/Y; the Labour Panel 3 wage band uses the same series as the cleaner
    real-wage anchor (services-ex-shelter is composition-stable against wage
    composition-adjusted readings; total services contains shelter, which moves
    with policy-rate cycles independently of underlying services-price drift).

    Two routes to the output and the choice between them matters:

      Route A ("level-then-Y/Y", standard):
        For each month t, compute a synthetic ex-shelter services level
            L_t = (w_services * services_index_t - w_shelter * shelter_index_t)
                  / (w_services - w_shelter)
        using the basket cycle in force at month t (StatCan refreshes weights
        on a basket-cycle cadence; the latest 2024 basket applies forward).
        Then Y/Y_t = (L_t / L_{t-12} - 1) * 100.

      Route B ("subtract weighted Y/Ys"):
        yoy_t = (w_services * yoy_services_t - w_shelter * yoy_shelter_t)
                / (w_services - w_shelter).

    Route A is the StatCan / BoC convention for ex-aggregate price indices
    (the published all-items-ex-shelter and core-CPI variants are all level-
    then-Y/Y). Route B differs slightly because the weights at month t apply
    to LEVELS in B but to GROWTH RATES at month t-12 vs t in A, and the
    basket cycle in force at t-12 may differ from the cycle in force at t
    (Route A keeps the t-cycle for both endpoints by reconstructing the
    same-cycle level; Route B implicitly mixes cycles).

    We implement Route A. Weights come from `cpi_basket_weights_canada.csv`
    (long-format date | aggregate | weight_pct); the cycle in force at any
    month t is the latest cycle_start_date <= t.

    Inputs:
        data/raw/cpi_services.csv       NSA index level (StatCan v41691230)
        data/raw/cpi_shelter.csv        NSA index level (StatCan v41691050)
        data/derived/cpi_basket_weights_canada.csv
            long-format weights from cpi_basket.fetch_basket_weights()

    Output:
        data/processed/cpi_services_ex_shelter_yoy.csv  date,value (%)
    """
    services = _read_raw("cpi_services")
    shelter = _read_raw("cpi_shelter")
    if services is None or shelter is None:
        logger.warning(
            "derive_cpi_services_ex_shelter_yoy skipped: services=%s shelter=%s",
            services is not None, shelter is not None,
        )
        return

    weights_path = DATA_DERIVED / "cpi_basket_weights_canada.csv"
    if not weights_path.exists():
        logger.warning(
            "derive_cpi_services_ex_shelter_yoy skipped: missing %s "
            "(run fetch_cpi_basket_weights first)",
            weights_path,
        )
        return
    w_long = pd.read_csv(weights_path, parse_dates=["date"])
    w_services = (
        w_long[w_long["aggregate"] == "services"]
        .set_index("date")["weight_pct"].sort_index()
    )
    w_shelter = (
        w_long[w_long["aggregate"] == "shelter"]
        .set_index("date")["weight_pct"].sort_index()
    )
    if w_services.empty or w_shelter.empty:
        logger.warning(
            "derive_cpi_services_ex_shelter_yoy: basket weights missing services/shelter rows"
        )
        return

    # Align index levels on date.
    s = services.set_index("date")["value"].sort_index()
    h = shelter.set_index("date")["value"].sort_index()
    joined = pd.concat([s.rename("services"), h.rename("shelter")], axis=1).dropna()
    if joined.empty:
        logger.warning("derive_cpi_services_ex_shelter_yoy: no overlapping months")
        return

    # For each month, pick the basket cycle whose start_date is the latest
    # cycle <= month. asof() is the natural primitive here; both weight
    # series are sorted by date and basket cycles are discrete refresh dates.
    ws = w_services.reindex(
        w_services.index.union(joined.index)
    ).sort_index().ffill().reindex(joined.index)
    wh = w_shelter.reindex(
        w_shelter.index.union(joined.index)
    ).sort_index().ffill().reindex(joined.index)

    # Synthetic ex-shelter level: weighted residual normalized by the
    # ex-shelter weight share so the result reads as a like-for-like CPI
    # sub-index (i.e. a level whose Y/Y is interpretable as inflation).
    # Denominator (ws - wh) is the basket share of services-ex-shelter; in
    # the current 2024 basket this is ~33pp (services ~46 minus shelter ~28).
    denom = ws - wh
    if (denom <= 0).any():
        logger.warning(
            "derive_cpi_services_ex_shelter_yoy: non-positive ex-shelter weight share "
            "in some basket cycles; check basket_weights_canada.csv"
        )
    level = (ws * joined["services"] - wh * joined["shelter"]) / denom
    level = level.dropna()
    if len(level) < 13:
        logger.warning(
            "derive_cpi_services_ex_shelter_yoy: insufficient history for Y/Y (n=%d)",
            len(level),
        )
        return

    yoy = (level.pct_change(12) * 100.0).dropna()
    out = yoy.reset_index()
    out.columns = ["date", "value"]

    spec_services = STATCAN_SERIES["cpi_services"]
    spec_shelter = STATCAN_SERIES["cpi_shelter"]
    meta = SeriesMeta(
        name="cpi_services_ex_shelter_yoy",
        source="Statistics Canada Web Data Service (derived)",
        source_url=statcan_url(spec_services),
        source_id=(
            f"v{spec_services.vector_id}-minus-weighted-v{spec_shelter.vector_id}"
            "-basket-link-month-weights"
        ),
        units="%",
        frequency="monthly",
        notes=(
            "Year-over-year % change in basket-weighted services CPI excluding "
            "shelter. Synthetic ex-shelter level reconstructed per basket cycle "
            "from StatCan Table 18-10-0007-01 weights "
            "(cpi_basket_weights_canada.csv): "
            "L_t = (w_services_t * services_index_t - w_shelter_t * shelter_index_t) "
            "/ (w_services_t - w_shelter_t). Y/Y is the standard 12-month % change "
            "on L. Route choice ('level-then-Y/Y' vs 'subtract weighted Y/Ys'): we "
            "use level-then-Y/Y per StatCan / BoC convention for published "
            "ex-aggregate CPI variants. The two routes differ when basket cycles "
            "change within the 12-month comparison window; level-then-Y/Y holds "
            "the current-month cycle constant across both endpoints. Inputs: "
            "cpi_services (NSA, v41691230) and cpi_shelter (NSA, v41691050)."
        ),
        transform="basket_weighted_services_minus_shelter_level_then_yoy(periods_per_year=12)",
    )
    write_series(out, meta, DATA_PROCESSED)


def derive_cpi_breadth_gt3() -> None:
    """Share of CPI basket (weighted) with Y/Y inflation above 3%.

    Classical "breadth" measure: for each month, compute each of the 60
    published CPI components' Y/Y % change, then sum the 2024-basket
    weights of those components whose Y/Y > 3%. Output is the weighted
    share (in %) of the basket experiencing inflation above the upper
    edge of the BoC 1-3% control band.

    Inputs:
        data/raw/cpi_components.csv        -- wide-format index levels,
                                              one column per component
        data/derived/cpi_component_weights_canada.json
                                           -- mapping of component name to
                                              2024 basket weight (% share)

    Output:
        data/processed/cpi_breadth_gt3.csv
            columns: date, value (% of basket with Y/Y > 3%)

    Weights are normalized over the 60 components we have (they sum to
    ~99% of the all-items basket; the small residual is excluded minor
    sub-aggregates). Normalization ensures the output is bounded [0, 100].
    A component is included in a month only if both its current value AND
    its 12-month-prior value are present (otherwise Y/Y is undefined and
    we drop that month-component pair from the denominator too, to avoid
    biasing the share toward 0 in months with sparse coverage).
    """
    import json as _json

    components = _read_raw("cpi_components")
    if components is None:
        return
    weights_path = DATA_DERIVED / "cpi_component_weights_canada.json"
    if not weights_path.exists():
        logger.warning("derive_cpi_breadth_gt3 skipped: missing %s", weights_path)
        return
    mapping = _json.loads(weights_path.read_text(encoding="utf-8"))
    weights = {x["name"]: float(x["wt_value"]) for x in mapping}

    components = components.sort_values("date").reset_index(drop=True)
    components = components.set_index("date")
    # Keep only columns we have weights for. Surface a warning if any
    # weight name isn't in the components frame (layout drift).
    matched_cols = [c for c in components.columns if c in weights]
    missing_names = sorted(set(weights) - set(components.columns))
    if missing_names:
        logger.warning(
            "derive_cpi_breadth_gt3: %d weight names not in cpi_components: %s",
            len(missing_names), missing_names[:3],
        )
    if not matched_cols:
        logger.warning("derive_cpi_breadth_gt3: no overlapping components")
        return

    # Y/Y % per component (component levels are NSA index, 2002=100).
    yoy = components[matched_cols].pct_change(periods=12) * 100.0

    # For each month: per-component validity mask = both current and 12-mo
    # prior present (i.e. yoy is not NaN). Numerator = sum of weights where
    # yoy > 3 AND valid. Denominator = sum of weights where valid. Output =
    # numerator / denominator * 100 (already in percent because weights are %).
    w = pd.Series(weights)[matched_cols]
    valid = yoy.notna()
    gt3 = yoy.gt(3.0) & valid
    num = gt3.mul(w, axis=1).sum(axis=1)
    den = valid.mul(w, axis=1).sum(axis=1)
    share = (num / den) * 100.0
    share = share.replace([float("inf"), -float("inf")], pd.NA).dropna()

    out = share.reset_index()
    out.columns = ["date", "value"]

    meta = SeriesMeta(
        name="cpi_breadth_gt3",
        source="Statistics Canada Web Data Service (derived)",
        source_url="https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1810000401",
        source_id="cpi_components_yoy_basket_weighted_share_gt_3pct",
        units="% (share of weighted basket with Y/Y > 3%)",
        frequency="monthly",
        notes=(
            "Share of the 60-component CPI basket (2024 weights) with Y/Y "
            "inflation greater than 3%. Numerator and denominator both "
            "restricted to components with non-missing Y/Y so coverage gaps "
            "don't bias the share. Output is a percent (0-100); the BoC "
            "control-band upper edge is 3%, so this metric reads how broad "
            "the above-band inflation pulse is. Sources: cpi_components.csv "
            "(per-component NSA index levels) and cpi_component_weights_"
            "canada.json (lifted from boc-tracker; StatCan 2024 basket)."
        ),
        transform="basket_weighted_share(yoy>3, normalize_over_valid)",
    )
    write_series(out, meta, DATA_PROCESSED)


def derive_cpi_breadth_band() -> None:
    """CPI breadth: share of basket with Y/Y above 3 and below 1 percent.

    Ports the boc-tracker calculation (analyze.py lines ~88-104). Distinct
    from `derive_cpi_breadth_gt3()`, which produces a different "share of
    valid components" metric used by the inflation tile supporting print.
    This derivation feeds the inflation Panel 3 breadth chart.

    Algorithm (matches boc-tracker exactly):

      1. Load per-component weights from cpi_component_weights_canada.json.
      2. Load wide-format per-component CPI levels from cpi_components.csv.
      3. Keep only components whose first valid observation is on or before
         1995-01-01 (deep-history filter; sloughs off newer subindexes that
         would distort the historical-average band).
      4. Normalize the surviving weights to sum to 1.
      5. Compute per-component Y/Y % change.
      6. above3 = sum over components of weight x I(yoy > 3) x 100  (% of basket)
         below1 = sum over components of weight x I(yoy < 1) x 100  (% of basket)
      7. Drop months where any kept component has a missing Y/Y (the all-NaN
         filter; protects against partial-release windows biasing the share).
      8. 1996-2019 historical averages serve as reference lines on the chart.

    Outputs:
        data/processed/cpi_breadth_above3.csv  - monthly date, value (%)
        data/processed/cpi_breadth_below1.csv  - monthly date, value (%)
        data/derived/cpi_breadth_band_metadata.json
            { "historical_avg_above3_1996_2019": float,
              "historical_avg_below1_1996_2019": float,
              "components_kept": int,
              "weights_normalized_from": float,
              "as_of_date": "YYYY-MM-DD",
              "latest_above3": float,
              "latest_below1": float,
              "source": "...", "source_url": "...", "generated_at": ISO }

    Boc-tracker leaves the original component coverage at the 1995-01-01
    cutoff intentionally: this is the same component set the historical
    averages are computed against, so changing it would invalidate the
    1996-2019 reference lines. Do NOT relax this without re-checking
    `editorial/methodology.md`.
    """
    import json as _json

    components = _read_raw("cpi_components")
    if components is None:
        return
    weights_path = DATA_DERIVED / "cpi_component_weights_canada.json"
    if not weights_path.exists():
        logger.warning("derive_cpi_breadth_band skipped: missing %s", weights_path)
        return
    mapping = _json.loads(weights_path.read_text(encoding="utf-8"))
    weights = pd.Series(
        {m["name"]: float(m["wt_value"]) for m in mapping if m.get("wt_value") is not None}
    )

    components = components.sort_values("date").reset_index(drop=True)
    components = components.set_index("date")

    # Deep-history filter: first valid index on or before 1995-01-01.
    cutoff = pd.Timestamp("1995-01-01")
    keep = [
        c for c in components.columns
        if c in weights.index and components[c].first_valid_index() is not None
        and components[c].first_valid_index() <= cutoff
    ]
    if not keep:
        logger.warning("derive_cpi_breadth_band: no components pass the 1995-01-01 filter")
        return

    comp = components[keep]
    w = weights.reindex(keep).fillna(0.0)
    w_sum_pre = float(w.sum())
    if w_sum_pre <= 0:
        logger.warning("derive_cpi_breadth_band: sum of kept weights is non-positive")
        return
    w = w / w.sum()

    yoy_c = comp.pct_change(periods=12) * 100.0
    above3 = yoy_c.gt(3.0).multiply(w, axis=1).sum(axis=1) * 100.0
    below1 = yoy_c.lt(1.0).multiply(w, axis=1).sum(axis=1) * 100.0
    valid = yoy_c.notna().all(axis=1)
    above3 = above3[valid]
    below1 = below1[valid]
    if above3.empty:
        logger.warning("derive_cpi_breadth_band: no months with full component coverage")
        return

    # Historical averages over 1996-2019 (BoC inflation-targeting era through
    # the COVID break). Used as reference bands on the chart.
    ha_above = float(above3.loc["1996":"2019"].mean())
    ha_below = float(below1.loc["1996":"2019"].mean())
    latest_date = above3.index.max()
    latest_above3 = float(above3.loc[latest_date])
    latest_below1 = float(below1.loc[latest_date])

    def _series_to_df(s: pd.Series) -> pd.DataFrame:
        out = s.reset_index()
        out.columns = ["date", "value"]
        return out

    notes_common = (
        f"Boc-tracker port (analyze.py 2026-05-11 vintage). Components kept = "
        f"{len(keep)} (those with first_valid_index <= 1995-01-01, intersected "
        f"with cpi_component_weights_canada.json). Weights renormalised over "
        f"the kept set; original weight sum was {w_sum_pre:.2f} of 100. "
        f"Monthly rows dropped when any kept component is missing its 12-mo "
        f"prior observation (the all-valid mask). Historical reference: "
        f"1996-2019 averages are {ha_above:.2f}% (above3) and {ha_below:.2f}% (below1)."
    )

    above_meta = SeriesMeta(
        name="cpi_breadth_above3",
        source="Statistics Canada Web Data Service (derived)",
        source_url="https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1810000401",
        source_id="cpi_components_yoy_basket_weighted_share_gt_3pct_bocrecipe",
        units="% of weighted basket",
        frequency="monthly",
        notes=(
            "Share of the CPI basket (weighted) with Y/Y inflation above 3%. "
            + notes_common
        ),
        transform="basket_weighted_share(yoy>3, deep_history_1995_filter)",
    )
    write_series(_series_to_df(above3), above_meta, DATA_PROCESSED)

    below_meta = SeriesMeta(
        name="cpi_breadth_below1",
        source="Statistics Canada Web Data Service (derived)",
        source_url="https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1810000401",
        source_id="cpi_components_yoy_basket_weighted_share_lt_1pct_bocrecipe",
        units="% of weighted basket",
        frequency="monthly",
        notes=(
            "Share of the CPI basket (weighted) with Y/Y inflation below 1%. "
            + notes_common
        ),
        transform="basket_weighted_share(yoy<1, deep_history_1995_filter)",
    )
    write_series(_series_to_df(below1), below_meta, DATA_PROCESSED)

    # Companion scalar payload: historical averages + provenance for the
    # chart's reference bands. Lives in data/derived/ so panel_data can
    # surface it without inventing a CSV-shaped wrapper for two scalars.
    DATA_DERIVED.mkdir(parents=True, exist_ok=True)
    band_meta = {
        "name": "cpi_breadth_band_metadata",
        "source": "Statistics Canada Web Data Service (derived)",
        "source_url": "https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1810000401",
        "source_id": "cpi_breadth_band_historical_averages_1996_2019",
        "units": "% of weighted basket",
        "frequency": "monthly",
        "components_kept": len(keep),
        "weights_unnormalised_sum_pct": w_sum_pre,
        "deep_history_cutoff": cutoff.date().isoformat(),
        "historical_window_start": "1996-01-01",
        "historical_window_end": "2019-12-31",
        "historical_avg_above3_1996_2019": ha_above,
        "historical_avg_below1_1996_2019": ha_below,
        "as_of_date": latest_date.date().isoformat(),
        "latest_above3": latest_above3,
        "latest_below1": latest_below1,
        "n_observations": int(len(above3)),
        "generated_at": datetime_now_iso(),
        "notes": notes_common,
    }
    (DATA_DERIVED / "cpi_breadth_band_metadata.json").write_text(
        _json.dumps(band_meta, indent=2, sort_keys=False) + "\n",
        encoding="utf-8",
    )


def derive_gdp_views() -> None:
    """Compute Y/Y for the monthly real-GDP series (Table 36-10-0434-01).

    The headline tile (site_data.py SECTION_CONFIGS['gdp']) reads
    `gdp_monthly_yoy` from data/processed/. Source vector is monthly real GDP,
    chained 2017$, SAAR. We derive Y/Y % change via the standard
    `headline_yoy()` wrapper over `yoy_pct(periods_per_year=12)`.
    """
    raw = _read_raw("gdp_monthly")
    if raw is None:
        return
    yoy = headline_yoy(raw, periods_per_year=12)
    spec = STATCAN_SERIES["gdp_monthly"]
    meta = SeriesMeta(
        name="gdp_monthly_yoy",
        source="Statistics Canada Web Data Service",
        source_url=statcan_url(spec),
        source_id=f"v{spec.vector_id}",
        units="%",
        frequency="monthly",
        notes=(
            "Year-over-year % change in monthly real GDP (Table 36-10-0434-01, "
            "chained 2017$, SAAR). Derived from the raw level series."
        ),
        transform="yoy_pct(periods_per_year=12)",
    )
    write_series(yoy, meta, DATA_PROCESSED)


def derive_gdp_per_capita_yoy() -> None:
    """Quarterly per-capita real GDP, Y/Y % change.

    Inputs:
        data/raw/gdp_quarterly.csv -- quarterly real GDP (C$ millions chained
                                       2017, SAAR), StatCan v62305752.
        data/raw/pop_total.csv     -- quarterly total population (persons),
                                       StatCan v1 from Table 17-10-0009-01.

    Output:
        data/processed/gdp_per_capita_yoy.csv
            date,value -- Y/Y % change in real GDP per capita.

    Why quarterly: pop_total is quarterly; aligning monthly GDP would require
    a forward-fill/interpolation that introduces sawtooth noise. The Per-capita
    GDP, Y/Y supporting print (Housing... actually GDP) renders the quarterly
    cadence stamp ("2025Q4"); this matches the cadence of the underlying
    StatCan population vintage.
    """
    gdp = _read_raw("gdp_quarterly")
    pop = _read_raw("pop_total")
    if gdp is None or pop is None:
        return
    g = gdp.set_index("date")["value"].sort_index()
    p = pop.set_index("date")["value"].sort_index()
    # Inner-join on quarter-start dates.
    joined = pd.concat([g.rename("gdp"), p.rename("pop")], axis=1).dropna()
    if joined.empty:
        logger.warning("derive_gdp_per_capita_yoy: no overlapping quarterly observations")
        return
    # GDP / population -> per-capita level (units: chained-2017 C$ per person,
    # scaled by GDP's units; we don't render the level so absolute scale is
    # immaterial. Only the Y/Y % matters for the tile).
    per_cap = (joined["gdp"] / joined["pop"]).dropna()
    yoy = per_cap.pct_change(4) * 100.0  # 4 quarters = Y/Y
    yoy = yoy.dropna()
    if yoy.empty:
        logger.warning("derive_gdp_per_capita_yoy: insufficient history for Y/Y")
        return
    out = yoy.reset_index()
    out.columns = ["date", "value"]

    spec_g = STATCAN_SERIES["gdp_quarterly"]
    spec_p = STATCAN_SERIES["pop_total"]
    meta = SeriesMeta(
        name="gdp_per_capita_yoy",
        source="Statistics Canada Web Data Service (derived)",
        source_url=statcan_url(spec_g),
        source_id=f"v{spec_g.vector_id}-divided-by-v{spec_p.vector_id}",
        units="%",
        frequency="quarterly",
        notes=(
            "Year-over-year % change in real GDP per capita, quarterly. Derived "
            "from quarterly real GDP (v62305752, chained 2017 C$, SAAR) divided "
            "by quarterly total population (v1, Table 17-10-0009-01). Y/Y % is "
            "computed on the per-capita level using a 4-quarter lag."
        ),
        transform="yoy_pct(periods_per_year=4) on gdp_quarterly/pop_total",
    )
    write_series(out, meta, DATA_PROCESSED)


def derive_productivity_views() -> None:
    """Compute Y/Y % change for the quarterly business-sector labour productivity index.

    Source: StatCan Table 36-10-0206-01 v1409153 ("Canada;Business sector;Labour
    productivity"), quarterly SA index. The raw level lands at
    data/raw/productivity_business_per_hour.csv via the StatCan catalog run;
    here we derive Y/Y (periods_per_year=4) for chart consumption.

    Feeds GDP Panel 6 (productivity overlay replacing the recession-state proxy).
    """
    raw = _read_raw("productivity_business_per_hour")
    if raw is None:
        return
    yoy = headline_yoy(raw, periods_per_year=4)
    spec = STATCAN_SERIES["productivity_business_per_hour"]
    meta = SeriesMeta(
        name="productivity_business_per_hour_yoy",
        source="Statistics Canada Web Data Service",
        source_url=statcan_url(spec),
        source_id=f"v{spec.vector_id}",
        units="%",
        frequency="quarterly",
        notes=(
            "Year-over-year % change in business-sector labour productivity index "
            "(Table 36-10-0206-01, quarterly SA, 2017=100). Derived from the raw "
            "level series. Per BoC convention, business-sector output per hour is "
            "the headline competitiveness read."
        ),
        transform="yoy_pct(periods_per_year=4)",
    )
    write_series(yoy, meta, DATA_PROCESSED)


def derive_terms_of_trade() -> None:
    """Quarterly terms-of-trade index = exports IPI / imports IPI x 100.

    Per StatCan national-accounts convention. Inputs land in data/raw/ via the
    StatCan catalog run (tot_exports_ipi v62307276, tot_imports_ipi v62307279,
    both from Table 36-10-0106 GDP price indexes). The ratio writes to
    data/processed/terms_of_trade.csv and feeds the Trade Panel 5 read and
    the trade supporting-print "terms-of-trade".

    Companion Y/Y view also lands in processed/ for chart consumption.
    """
    exports = _read_raw("tot_exports_ipi")
    imports = _read_raw("tot_imports_ipi")
    if exports is None or imports is None:
        return
    e = exports.set_index("date")["value"].sort_index()
    i = imports.set_index("date")["value"].sort_index()
    joined = pd.concat([e.rename("e"), i.rename("i")], axis=1).dropna()
    tot = (joined["e"] / joined["i"] * 100.0).dropna()
    tot_df = tot.reset_index()
    tot_df.columns = ["date", "value"]

    spec_e = STATCAN_SERIES["tot_exports_ipi"]
    spec_i = STATCAN_SERIES["tot_imports_ipi"]
    meta = SeriesMeta(
        name="terms_of_trade",
        source="Statistics Canada Web Data Service (derived)",
        source_url=statcan_url(spec_e),
        source_id=f"v{spec_e.vector_id}-divided-by-v{spec_i.vector_id}-times-100",
        units="Index, 2017=100",
        frequency="quarterly",
        notes=(
            "Terms-of-trade index = exports IPI / imports IPI x 100. National-"
            "accounts ToT per StatCan Table 36-10-0106 conventions. Quarterly SA. "
            "Inputs: tot_exports_ipi (v62307276) and tot_imports_ipi (v62307279)."
        ),
        transform="exports_ipi/imports_ipi*100",
    )
    write_series(tot_df, meta, DATA_PROCESSED)

    # Y/Y % change companion -- standard chart consumption view.
    yoy = headline_yoy(tot_df, periods_per_year=4)
    yoy_meta = SeriesMeta(
        name="terms_of_trade_yoy",
        source=meta.source,
        source_url=meta.source_url,
        source_id=meta.source_id,
        units="%",
        frequency="quarterly",
        notes="Year-over-year % change in the terms-of-trade index. Derived.",
        transform="yoy_pct(periods_per_year=4) on terms_of_trade",
    )
    write_series(yoy, yoy_meta, DATA_PROCESSED)


def derive_federal_fiscal_ytd() -> None:
    """Within-FY cumulative federal budgetary balance, monthly.

    Inputs:
        data/raw/federal_budget_balance.csv -- continuous monthly balance
            spanning prior FY + current FY (CAD millions, prior-FY finalized
            + current-FY months-to-date).

    Output:
        data/processed/federal_budget_ytd.csv
            date,value -- FY-YTD cumulative balance through each calendar
            month-end, in CAD millions. The cumulative sum RESETS at each
            Canadian fiscal-year boundary (April-March).

    Rationale: the Policy supporting-print row reads FY-YTD (DoF Fiscal
    Monitor headline framing), and compares the latest point to the same
    month one fiscal year prior (so the reader sees "FY26 YTD through Feb
    vs FY25 YTD through Feb"). Per-tile transform code is kept simple by
    pre-deriving the cumulative series here; the print's transform just
    picks the right comparator (latest minus same-month-prior-FY).
    """
    monthly = _read_raw("federal_budget_balance")
    if monthly is None:
        return
    df = monthly.copy()
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").reset_index(drop=True)
    # Canadian federal FY runs April-March. Group by FY-start year: a row
    # whose calendar month is >= April belongs to FY-start=calendar year;
    # Jan-Mar rows belong to FY-start=calendar year - 1.
    fy_start = df["date"].dt.year.where(df["date"].dt.month >= 4, df["date"].dt.year - 1)
    df["_fy_start"] = fy_start
    df["value"] = df.groupby("_fy_start")["value"].cumsum()
    out = df[["date", "value"]].reset_index(drop=True)

    meta = SeriesMeta(
        name="federal_budget_ytd",
        source="Department of Finance Canada -- Fiscal Monitor (derived)",
        source_url="https://www.canada.ca/en/department-finance/services/publications/fiscal-monitor",
        source_id="federal_budget_balance:cumsum-by-fy",
        units="CAD millions",
        frequency="monthly",
        notes=(
            "Federal fiscal-YTD cumulative budgetary balance, monthly. Derived "
            "from raw/federal_budget_balance.csv by cumulative-summing within "
            "each Canadian federal fiscal year (April-March reset). Spans prior "
            "FY (full 12 months, finalized) + current FY (months-to-date), so "
            "the latest point's same-month-of-prior-FY comparator is reliably "
            "12 calendar months back. Used by the Policy supporting-print row "
            "'federal-budget-balance' to render FY-YTD vs prior-FY-YTD-at-same-"
            "month -- DoF Fiscal Monitor headline framing."
        ),
        transform="cumsum_within_fy(start_month=4)",
    )
    write_series(out, meta, DATA_PROCESSED)


def derive_current_account_views() -> None:
    """Sanity-check that the quarterly current-account components reconcile to
    the headline balance, and emit a derived sum for chart-builder convenience.

    The headline `current_account_balance` (v61915304) IS the StatCan-published
    sum, so we keep that authoritative. This step writes a sibling
    `current_account_components_sum.csv` (sum of the four sub-component balances)
    so chart-builder can verify reconciliation visually and reuse the same
    cadence inputs for stacked-bar panels. Tolerance to discrepancy is built
    into the chart-side compare, not enforced here.
    """
    parts = [
        ("ca_goods_balance_q", "Goods"),
        ("ca_services_balance_q", "Services"),
        ("ca_primary_income_q", "Primary income"),
        ("ca_secondary_income_q", "Secondary income"),
    ]
    loaded: dict[str, pd.DataFrame] = {}
    for slug, _label in parts:
        df = _read_raw(slug)
        if df is None:
            return
        loaded[slug] = df
    aligned = None
    for slug, df in loaded.items():
        s = df.set_index("date")["value"].sort_index().rename(slug)
        aligned = s if aligned is None else pd.concat([aligned, s], axis=1)
    total = aligned.sum(axis=1, min_count=4).dropna()
    out = total.reset_index()
    out.columns = ["date", "value"]
    spec = STATCAN_SERIES["current_account_balance"]
    meta = SeriesMeta(
        name="current_account_components_sum",
        source="Statistics Canada Web Data Service (derived)",
        source_url=statcan_url(spec),
        source_id="ca_goods+services+primary+secondary (quarterly SA balances)",
        units="C$ millions",
        frequency="quarterly",
        notes=(
            "Sum of the four current-account sub-component balances: goods + "
            "services + primary income + secondary income. Should reconcile "
            "to the headline current_account_balance (v61915304) to within "
            "statistical discrepancy. Useful for chart-side stacked-bar layouts."
        ),
        transform="sum_components",
    )
    write_series(out, meta, DATA_PROCESSED)


def derive_trade_views() -> None:
    """Trade-balance 3mma + partner-share trajectories (canon 4.7 elements 1, 3)."""
    balance = _read_raw("trade_balance_total")
    if balance is not None:
        ma3 = trade_balance_3m_ma(balance, window=3)
        spec = STATCAN_SERIES["trade_balance_total"]
        meta = SeriesMeta(
            name="trade_balance_total_3m_ma",
            source="Statistics Canada Web Data Service (derived)",
            source_url=statcan_url(spec),
            source_id=f"v{spec.vector_id} (3mma)",
            units="CAD millions",
            frequency="monthly",
            notes=(
                "Trade balance 3-month moving average. Standard noise-suppression "
                "for monthly trade data per canon 4.7 element 1."
            ),
            transform="moving_average(window=3)",
        )
        write_series(ma3, meta, DATA_PROCESSED)

    # Partner shares: customs-basis, unadjusted. Table 12-10-0011-01.
    # Denominator = all-countries customs total (trade_exports/imports_all_customs).
    # Slug pattern: trade_{exports|imports}_{iso3} / trade_{exports|imports}_all_customs.
    # The old probe-pending slugs (trade_exports_china, trade_exports_uk, etc.)
    # pointed at wrong-table placeholder IDs; they have been replaced in the
    # catalog by the verified 12-10-0011-01 entries with ISO-3 suffixes.
    exports_total_customs = _read_raw("trade_exports_all_customs")
    imports_total_customs = _read_raw("trade_imports_all_customs")
    partner_targets_iso3 = [
        ("us_customs", "United States"),
        ("chn", "China"),
        ("gbr", "United Kingdom"),
        ("jpn", "Japan"),
        ("mex", "Mexico"),
        ("deu", "Germany"),
        ("fra", "France"),
        ("nld", "Netherlands"),
        ("kor", "South Korea"),
        ("ind", "India"),
        ("aus", "Australia"),
        ("idn", "Indonesia"),
        ("sgp", "Singapore"),
        ("sau", "Saudi Arabia"),
        ("twn", "Taiwan"),
        ("hkg", "Hong Kong"),
    ]
    for iso_slug, label in partner_targets_iso3:
        for side, total in (
            ("exports", exports_total_customs),
            ("imports", imports_total_customs),
        ):
            partner = _read_raw(f"trade_{side}_{iso_slug}")
            if partner is None or total is None:
                continue
            share = partner_share_trajectory(partner, total, label_partner=label)
            meta = SeriesMeta(
                name=f"trade_{side}_share_{iso_slug}",
                source="Statistics Canada Web Data Service (derived)",
                source_url=statcan_url(STATCAN_SERIES["trade_exports_all_customs"]),
                source_id=(
                    f"trade_{side}_{iso_slug}/trade_{side}_all_customs "
                    "(customs basis, unadjusted, Table 12-10-0011-01)"
                ),
                units="% share",
                frequency="monthly",
                notes=(
                    f"{label} share of total Canadian {side} (customs basis, "
                    "unadjusted). Derived: per-country series / all-countries "
                    "customs total. Source: Table 12-10-0011-01. Resolved 2026-05-14."
                ),
                transform="partner_share_trajectory",
            )
            write_series(share, meta, DATA_PROCESSED)


def derive_labour_force_ex_npr() -> None:
    """Monthly Canadian labour force, excluding non-permanent residents.

    Powers the Labour Panel 7 EI-claimants ratio chart: claimants /
    labour-force-ex-NPRs. The NPR-driven 2022-2024 population surge
    inflated every population-scaled labour denominator; deflating it
    isolates the cyclical signal in the EI series.

    Method (v1 -- simplest defensible path):
        1. NPR stock is approximated as the cumulative sum of quarterly
           net-NPR flows from 1946 forward (StatCan v29850346, Table
           17-10-0040-01). Pre-1970 NPR programs were near-zero so the
           1946=0 anchor is a low-cost approximation. Cumulative sum to
           Q4 2025 reads ~2.5M, which matches StatCan's published NPR
           stock (~3M peak mid-2024, ~2.5-2.7M after the federal cap)
           to within ~0.3M -- the residual reflects emigration of former
           NPRs and definitional drift across the 80-year window. Good
           enough for a denominator adjustment whose purpose is to remove
           the FIRST-ORDER NPR effect from labour-force growth.
        2. Labour force is computed as unemployment_level /
           (unemployment_rate / 100). That is the LFS identity LF = U / u
           and lets us derive monthly LF without a separate fetch of
           employment_level (which is in the catalog but adds nothing
           the rate+level pair don't already encode).
        3. NPR share of total population is computed quarterly
           (npr_stock_q / pop_total_q) and forward-filled to monthly to
           align with the monthly LFS frame. Within-quarter constancy is
           a reasonable approximation -- the population denominator
           moves slowly and the NPR stock estimate is itself quarterly.
        4. labour_force_ex_npr = LF x (1 - npr_share_of_pop).

    The KEY APPROXIMATION is step 4: we assume NPRs participate in the
    labour force at the SAME rate as the non-NPR population. Empirically
    NPR participation runs higher than the headline (skewed toward
    prime-age working entrants), so this method slightly OVER-DEFLATES
    the labour force and the EI ratio it powers will be slightly
    OVER-stated vs the truth. That is acceptable for the v1 chart frame
    (the cyclical inflection signal dominates the level error) and the
    direction of the bias is documented here and in the meta.notes.

    A future v2 could (a) fetch StatCan Table 14-10-0083 for monthly LF
    by immigrant status and read NPR labour force directly, or (b)
    apply a fixed 75% NPR participation rate to the NPR stock. Both
    add complexity for a second-order correction; deferred per the
    user's "without boiling the ocean" framing.

    Inputs:
        data/raw/pop_net_npr.csv          quarterly net NPR flows (persons).
        data/raw/pop_total.csv            quarterly total population (persons).
        data/raw/unemployment_level.csv   monthly U level (millions of persons).
        data/raw/unemployment_rate.csv    monthly u rate (%, 15+).

    Output:
        data/processed/labour_force_ex_npr.csv
            date,value -- monthly labour force ex-NPRs, MILLIONS of persons.
    """
    npr_flow = _read_raw("pop_net_npr")
    pop = _read_raw("pop_total")
    u_level = _read_raw("unemployment_level")
    u_rate = _read_raw("unemployment_rate")
    if any(x is None for x in (npr_flow, pop, u_level, u_rate)):
        logger.warning(
            "derive_labour_force_ex_npr skipped: missing inputs (npr_flow=%s pop=%s u_level=%s u_rate=%s)",
            npr_flow is not None, pop is not None,
            u_level is not None, u_rate is not None,
        )
        return

    # Step 1: NPR stock = cumulative net-NPR flows from 1946 forward (quarterly).
    nf = npr_flow.set_index("date")["value"].sort_index().dropna()
    npr_stock_q = nf.cumsum().rename("npr_stock")

    # Step 2: monthly LF from the LFS identity LF = U / u. unemployment_level
    # is on disk in MILLIONS; unemployment_rate is in PERCENT.
    ul = u_level.set_index("date")["value"].sort_index().dropna()
    ur = u_rate.set_index("date")["value"].sort_index().dropna()
    lfs = pd.concat([ul.rename("u_level"), ur.rename("u_rate")], axis=1).dropna()
    if lfs.empty:
        logger.warning("derive_labour_force_ex_npr: no overlap between u_level and u_rate")
        return
    # Guard against zero rate (would never happen in practice but be defensive).
    lf = (lfs["u_level"] / (lfs["u_rate"] / 100.0)).replace([float("inf"), float("-inf")], pd.NA).dropna()
    lf = lf.rename("labour_force_millions")

    # Step 3: NPR share of total population, quarterly, then ffill to monthly.
    pt = pop.set_index("date")["value"].sort_index().dropna()
    pt_persons = pt.rename("pop_total_persons")
    q_joined = pd.concat([npr_stock_q, pt_persons], axis=1).dropna()
    if q_joined.empty:
        logger.warning("derive_labour_force_ex_npr: no overlap between npr_stock and pop_total")
        return
    npr_share_q = (q_joined["npr_stock"] / q_joined["pop_total_persons"]).rename("npr_share")
    # Forward-fill the quarterly share onto the monthly LFS index.
    npr_share_m = npr_share_q.reindex(
        npr_share_q.index.union(lf.index)
    ).sort_index().ffill().reindex(lf.index)

    # Step 4: deflate. Drop any leading rows where ffill could not yet supply
    # a share (LFS history pre-dates the first quarterly NPR observation).
    aligned = pd.concat([lf, npr_share_m.rename("npr_share")], axis=1).dropna()
    if aligned.empty:
        logger.warning("derive_labour_force_ex_npr: no overlap after monthly alignment")
        return
    lf_ex = (aligned["labour_force_millions"] * (1.0 - aligned["npr_share"])).dropna()

    out = lf_ex.reset_index()
    out.columns = ["date", "value"]

    # Provenance: pop_net_npr / pop_npr_inflows were lifted from boc-tracker
    # and are NOT in STATCAN_SERIES, so we read source_id directly from their
    # on-disk .meta.json sidecars rather than the catalog.
    spec_pop = STATCAN_SERIES["pop_total"]
    spec_ul = STATCAN_SERIES["unemployment_level"]
    spec_ur = STATCAN_SERIES["unemployment_rate"]
    try:
        import json as _json
        npr_meta = _json.loads((DATA_RAW / "pop_net_npr.meta.json").read_text(encoding="utf-8"))
        npr_vector = npr_meta.get("source_id", "v?")
    except Exception:
        npr_vector = "v29850346"  # documented fallback per pop_net_npr.meta.json
    meta = SeriesMeta(
        name="labour_force_ex_npr",
        source="Statistics Canada Web Data Service (derived)",
        source_url=statcan_url(spec_ul),
        source_id=(
            f"derived: LF=v{spec_ul.vector_id}/v{spec_ur.vector_id}; "
            f"npr_share=cumsum({npr_vector})/v{spec_pop.vector_id}"
        ),
        units="Millions of persons",
        frequency="monthly",
        notes=(
            "Monthly Canadian labour force, ex non-permanent residents. "
            "Derivation: LF = unemployment_level / (unemployment_rate / 100); "
            "npr_share = cumulative_sum(pop_net_npr from 1946 forward) / "
            "pop_total (quarterly, ffilled to monthly); "
            "labour_force_ex_npr = LF * (1 - npr_share). "
            "KEY APPROXIMATION: assumes NPR labour-force participation equals "
            "the headline participation rate. Empirically NPR participation is "
            "higher (prime-age skew), so this slightly OVER-deflates LF and any "
            "ratio using it as a denominator (e.g. EI claimants / LF-ex-NPR) "
            "will be slightly OVER-stated. The 1946=0 NPR-stock anchor is also "
            "approximate; cumulative net flows to Q4 2025 read ~2.5M vs StatCan "
            "published NPR stock ~2.5-2.7M post-cap (~3M peak mid-2024). For "
            "the v1 cyclical-inflection chart these biases are second-order. "
            "A v2 could pull Table 14-10-0083 LFS-by-immigrant-status directly."
        ),
        transform="labour_force_ex_npr_v1 (uniform-participation approximation)",
    )
    write_series(out, meta, DATA_PROCESSED)


def derive_boc_fed_spread_monthly() -> None:
    """BoC overnight-rate-target minus Fed funds target upper-bound, monthly, bps.

    Aggregation rule (per editorial/_derived_slot_queue.yaml 2026-05-13):
        For each calendar month M:
          1. BoC value  = last row in overnight_rate_target.csv falling in M
             (series is monthly; month-end alignment avoids intra-month
             transients on sequential BoC/Fed announcement days).
          2. Fed value  = last daily observation in fed_funds.csv falling in M
             (series is daily; last trading day of month picked by groupby.last).
          3. spread_bps = (BoC_pp - Fed_pp) * 100

    Inputs:
        data/raw/overnight_rate_target.csv  -- monthly, BoC overnight rate (%)
        data/raw/fed_funds.csv              -- daily, Fed funds target upper bound (%)

    Output:
        data/processed/boc_fed_spread_monthly.csv
            date, value -- month-start ISO dates, spread in basis points (signed).
    """
    boc_df = _read_raw("overnight_rate_target")
    fed_df = _read_raw("fed_funds")
    if boc_df is None or fed_df is None:
        logger.warning(
            "derive_boc_fed_spread_monthly skipped: missing inputs "
            "(overnight_rate_target=%s fed_funds=%s)",
            boc_df is not None,
            fed_df is not None,
        )
        return

    # Month-end last-observation alignment for both series.
    boc_df["_ym"] = boc_df["date"].dt.to_period("M")
    fed_df["_ym"] = fed_df["date"].dt.to_period("M")

    boc_me = (
        boc_df.sort_values("date")
        .groupby("_ym")["value"]
        .last()
        .rename("boc")
    )
    fed_me = (
        fed_df.sort_values("date")
        .groupby("_ym")["value"]
        .last()
        .rename("fed")
    )

    merged = pd.concat([boc_me, fed_me], axis=1).dropna()
    if merged.empty:
        logger.warning("derive_boc_fed_spread_monthly: no overlapping months")
        return

    spread = ((merged["boc"] - merged["fed"]) * 100).rename("value")
    # Represent each month as its month-start date (YYYY-MM-01) for consistency
    # with the existing monthly series convention on disk.
    out = spread.reset_index()
    out["date"] = out["_ym"].dt.to_timestamp("s")  # 's' = start of period
    out = out[["date", "value"]].sort_values("date").reset_index(drop=True)

    meta = SeriesMeta(
        name="boc_fed_spread_monthly",
        source="Bank of Canada Valet API / US Federal Reserve (derived)",
        source_url="https://www.bankofcanada.ca/valet/observations/group/INDINF_RATES/json",
        source_id="derived: overnight_rate_target - fed_funds (upper bound)",
        units="basis points",
        frequency="monthly",
        notes=(
            "BoC overnight rate target minus Fed funds target upper bound, "
            "expressed in basis points (pp x 100). Month-end last-observation "
            "alignment: for BoC the monthly series has one row per month; for "
            "Fed the daily series is sampled at the last trading day of each month. "
            "Negative values indicate BoC rate is below Fed rate. "
            "Derivation materialized 2026-05-13 per editorial/_derived_slot_queue.yaml."
        ),
        transform="boc_fed_spread_monthly: (overnight_rate_target - fed_funds) * 100",
    )
    write_series(out, meta, DATA_PROCESSED)


def derive_sectoral_exports_by_destination() -> None:
    """Sum NAPCS sub-components per tariff-exposed sector; compute non-US residual.

    Inputs (data/raw/):
        exports_steel_unwrought_all / _us   (NAPCS 30, C$M)
        exports_steel_semifin_all   / _us   (NAPCS 31, C$M)
        exports_aluminum_unwrought_all / _us (NAPCS 32, C$M)
        exports_aluminum_semifin_all   / _us (NAPCS 38, C$M)
        exports_softwood_all / _us           (NAPCS 55, C$M)
        exports_autos_cars_all / _us         (NAPCS 81, C$M)
        exports_autos_parts_all / _us        (NAPCS 84, C$M)
        exports_copper_all / _us             (NAPCS 33, C$M)

    All raw series: Table 12-10-0182-01, NSA monthly, C$ millions.

    Outputs (data/processed/):
        exports_steel_us.csv          exports_steel_nonus.csv
        exports_aluminum_us.csv       exports_aluminum_nonus.csv
        exports_softwood_us.csv       exports_softwood_nonus.csv
        exports_autos_us.csv          exports_autos_nonus.csv
        exports_copper_us.csv         exports_copper_nonus.csv

    All outputs: C$ millions, NSA monthly, date/value.

    Architecture note:
      Non-US = total (all countries) - US. The non-US residual is derived
      rather than fetched because WDS does not publish a "rest-of-world"
      partner aggregate at the NAPCS sub-chapter level. The derivation is
      exact for any month where both total and US series are non-null.
    """
    _TABLE_URL = "https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1210018201"

    def _sum_components(slugs: list[str]) -> Optional[pd.DataFrame]:
        """Align multiple raw C$M series on date and return their monthly sum."""
        series_list = []
        for slug in slugs:
            df = _read_raw(slug)
            if df is None:
                return None
            series_list.append(df.set_index("date")["value"].sort_index().rename(slug))
        aligned = pd.concat(series_list, axis=1)
        total = aligned.sum(axis=1, min_count=len(slugs)).dropna()
        out = total.reset_index()
        out.columns = ["date", "value"]
        return out

    def _nonus(all_df: pd.DataFrame, us_df: pd.DataFrame) -> pd.DataFrame:
        """Non-US = total minus US, inner-joined on date."""
        a = all_df.set_index("date")["value"].sort_index()
        u = us_df.set_index("date")["value"].sort_index()
        joined = pd.concat([a.rename("all"), u.rename("us")], axis=1).dropna()
        residual = (joined["all"] - joined["us"]).rename("value")
        out = residual.reset_index()
        out.columns = ["date", "value"]
        return out

    def _write_pair(
        sector: str,
        us_df: pd.DataFrame,
        nonus_df: pd.DataFrame,
        source_ids: str,
    ) -> None:
        base_meta = dict(
            source="Statistics Canada Web Data Service (derived)",
            source_url=_TABLE_URL,
            units="C$ millions",
            frequency="monthly",
        )
        write_series(
            us_df,
            SeriesMeta(
                name=f"exports_{sector}_us",
                notes=(
                    f"Canadian merchandise exports of {sector}, to United States, "
                    "NSA monthly, C$ millions. Summed from NAPCS sub-components and "
                    "scaled from C$ thousands (scalarFactorCode=3). "
                    f"Source vectors: {source_ids}. Table 12-10-0182-01. "
                    "Derived 2026-05-14."
                ),
                source_id=f"{source_ids}:US",
                **base_meta,
            ),
            DATA_PROCESSED,
        )
        write_series(
            nonus_df,
            SeriesMeta(
                name=f"exports_{sector}_nonus",
                notes=(
                    f"Canadian merchandise exports of {sector}, to non-US destinations, "
                    "NSA monthly, C$ millions. Derived as (all-countries total) minus "
                    "(United States). "
                    f"Source vectors: {source_ids}. Table 12-10-0182-01. "
                    "Derived 2026-05-14."
                ),
                source_id=f"{source_ids}:non-US",
                transform="all_countries_total - united_states",
                **base_meta,
            ),
            DATA_PROCESSED,
        )

    # --- Steel (NAPCS 30 + NAPCS 31) ---
    steel_all = _sum_components(["exports_steel_unwrought_all", "exports_steel_semifin_all"])
    steel_us = _sum_components(["exports_steel_unwrought_us", "exports_steel_semifin_us"])
    if steel_all is not None and steel_us is not None:
        _write_pair("steel", steel_us, _nonus(steel_all, steel_us),
                    "v1863612523+v1863615133 (all) / v1863612553+v1863615163 (US)")
    else:
        logger.warning("derive_sectoral_exports: steel components missing from raw/")

    # --- Aluminum (NAPCS 32 + NAPCS 38) ---
    alum_all = _sum_components(["exports_aluminum_unwrought_all", "exports_aluminum_semifin_all"])
    alum_us = _sum_components(["exports_aluminum_unwrought_us", "exports_aluminum_semifin_us"])
    if alum_all is not None and alum_us is not None:
        _write_pair("aluminum", alum_us, _nonus(alum_all, alum_us),
                    "v1863617743+v1863633403 (all) / v1863617773+v1863633433 (US)")
    else:
        logger.warning("derive_sectoral_exports: aluminum components missing from raw/")

    # --- Softwood lumber (NAPCS 55, single sub-chapter) ---
    softwood_all = _read_raw("exports_softwood_all")
    softwood_us = _read_raw("exports_softwood_us")
    if softwood_all is not None and softwood_us is not None:
        _write_pair("softwood", softwood_us, _nonus(softwood_all, softwood_us),
                    "v1863677773 (all) / v1863677803 (US)")
    else:
        logger.warning("derive_sectoral_exports: softwood components missing from raw/")

    # --- Autos (NAPCS 81 + NAPCS 84) ---
    autos_all = _sum_components(["exports_autos_cars_all", "exports_autos_parts_all"])
    autos_us = _sum_components(["exports_autos_cars_us", "exports_autos_parts_us"])
    if autos_all is not None and autos_us is not None:
        _write_pair("autos", autos_us, _nonus(autos_all, autos_us),
                    "v1863745633+v1863753463 (all) / v1863745663+v1863753493 (US)")
    else:
        logger.warning("derive_sectoral_exports: autos components missing from raw/")

    # --- Copper (NAPCS 33, single sub-chapter) ---
    # NAPCS 33 = "Unwrought copper and copper alloys" (HS 7401-7403).
    # Confirmed 2026-05-14 via POST getSeriesInfoFromCubePidCoord.
    # Section 232 tariff exposure since April 2026 copper proclamation.
    copper_all = _read_raw("exports_copper_all")
    copper_us = _read_raw("exports_copper_us")
    if copper_all is not None and copper_us is not None:
        _write_pair("copper", copper_us, _nonus(copper_all, copper_us),
                    "v1863620353 (all) / v1863620383 (US)")
    else:
        logger.warning("derive_sectoral_exports: copper components missing from raw/")


def derive_gold_exports() -> None:
    """Write editorial-labelled gold/PGM export series from NAPCS 35 raw vectors.

    Inputs (data/raw/):
        exports_gold_total  (NAPCS 35, all countries, C$M)
        exports_gold_us     (NAPCS 35, US, C$M)
        exports_gold_uk     (NAPCS 35, UK, C$M)

    NAPCS 35 = "Unwrought gold, silver, and platinum group metals, and their
    alloys" (HS 7106 + 7108 + 7110). No finer gold-only NAPCS cut exists in
    the WDS-accessible trade tables.

    Outputs (data/processed/):
        exports_gold_total.csv
        exports_gold_us.csv
        exports_gold_uk.csv

    All in C$ millions, NSA monthly. The raw vectors already land in data/raw/
    via run_statcan_catalog; this derivation copies them to processed/ with
    editorial metadata (source_id with the HS/NAPCS mapping note, editorially
    accurate units label). This allows the panel_data layer to reference the
    processed/ tier consistently with all other sectoral export outputs.
    """
    _TABLE_URL = "https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1210018201"

    for slug, label, vid in [
        ("exports_gold_total", "all countries", "v1863625573"),
        ("exports_gold_us",    "United States", "v1863625603"),
        ("exports_gold_uk",    "United Kingdom", "v1863625693"),
    ]:
        df = _read_raw(slug)
        if df is None:
            logger.warning("derive_gold_exports: %s missing from raw/", slug)
            continue
        meta = SeriesMeta(
            name=slug,
            source="Statistics Canada Web Data Service",
            source_url=_TABLE_URL,
            source_id=(
                f"{vid} — NAPCS 35 (Unwrought gold, silver, and platinum group "
                f"metals), {label}, Table 12-10-0182-01. scalarFactorCode=3 "
                "(C$ thousands in raw; scale=0.001 applied at fetch -> C$M)."
            ),
            units="C$ millions",
            frequency="monthly",
            notes=(
                f"Canadian merchandise exports of unwrought gold, silver, and "
                f"platinum group metals (NAPCS 35, HS 7106/7108/7110), to "
                f"{label}. NSA monthly, C$ millions. Table 12-10-0182-01. "
                "No finer gold-only sub-chapter available in WDS at this "
                "partner-country granularity. UK (London Bullion Market) "
                "typically absorbs 90-97% of Canada's all-countries total."
            ),
        )
        write_series(df, meta, DATA_PROCESSED)


def derive_aluminum_by_partner() -> None:
    """Sum NAPCS 32 + NAPCS 38 per partner country; write aluminum export series.

    Inputs (data/raw/):
        exports_aluminum_unwrought_{iso3}  (NAPCS 32, per partner, C$M)
        exports_aluminum_semifin_{iso3}    (NAPCS 38, per partner, C$M)

    Partners: usa (existing), gbr, chn, jpn, deu, kor, fra, nld, bel, mex, ind, sgp.
    The US totals (unwrought_all / _us, semifin_all / _us) already feed
    derive_sectoral_exports_by_destination; this function adds the per-partner
    split for the non-US distribution view.

    Output (data/processed/):
        exports_aluminum_{iso3}.csv   for each partner above

    All in C$ millions, NSA monthly.

    Coverage gap: UAE, Qatar, Kuwait, Bahrain, Oman are NOT in Table
    12-10-0182-01's partner dimension (same 29-partner list as Table
    12-10-0011-01 minus a few swaps). Data confirms aluminum flows to these
    markets are negligible (<$1M/month typically).
    """
    _TABLE_URL = "https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1210018201"

    # iso3 -> (napcs32_slug, napcs38_slug, vector_pair_label)
    # Note: "usa" is intentionally omitted. exports_aluminum_us is already
    # produced by derive_sectoral_exports_by_destination() in processed/.
    # Adding a duplicate exports_aluminum_usa would create a confusing
    # split in the catalog. Panel-9-alt references exports_aluminum_us directly.
    partners: dict[str, tuple[str, str, str]] = {
        "gbr": (
            "exports_aluminum_unwrought_gbr",
            "exports_aluminum_semifin_gbr",
            "v1863617863+v1863633523",
        ),
        "chn": (
            "exports_aluminum_unwrought_chn",
            "exports_aluminum_semifin_chn",
            "v1863617803+v1863633463",
        ),
        "jpn": (
            "exports_aluminum_unwrought_jpn",
            "exports_aluminum_semifin_jpn",
            "v1863617893+v1863633553",
        ),
        "deu": (
            "exports_aluminum_unwrought_deu",
            "exports_aluminum_semifin_deu",
            "v1863617923+v1863633583",
        ),
        "kor": (
            "exports_aluminum_unwrought_kor",
            "exports_aluminum_semifin_kor",
            "v1863617953+v1863633613",
        ),
        "fra": (
            "exports_aluminum_unwrought_fra",
            "exports_aluminum_semifin_fra",
            "v1863618013+v1863633673",
        ),
        "nld": (
            "exports_aluminum_unwrought_nld",
            "exports_aluminum_semifin_nld",
            "v1863618043+v1863633703",
        ),
        "bel": (
            "exports_aluminum_unwrought_bel",
            "exports_aluminum_semifin_bel",
            "v1863618073+v1863633733",
        ),
        "mex": (
            "exports_aluminum_unwrought_mex",
            "exports_aluminum_semifin_mex",
            "v1863617833+v1863633493",
        ),
        "ind": (
            "exports_aluminum_unwrought_ind",
            "exports_aluminum_semifin_ind",
            "v1863618253+v1863633913",
        ),
        "sgp": (
            "exports_aluminum_unwrought_sgp",
            "exports_aluminum_semifin_sgp",
            "v1863618523+v1863634183",
        ),
    }

    country_labels = {
        "gbr": "United Kingdom",
        "chn": "China",            "jpn": "Japan",
        "deu": "Germany",          "kor": "South Korea",
        "fra": "France",           "nld": "Netherlands",
        "bel": "Belgium",          "mex": "Mexico",
        "ind": "India",            "sgp": "Singapore",
    }

    for iso3, (slug32, slug38, vids) in partners.items():
        df32 = _read_raw(slug32)
        df38 = _read_raw(slug38)
        if df32 is None or df38 is None:
            logger.warning(
                "derive_aluminum_by_partner: %s components missing from raw/ "
                "(slug32=%s present=%s, slug38=%s present=%s)",
                iso3, slug32, df32 is not None, slug38, df38 is not None,
            )
            continue

        s32 = df32.set_index("date")["value"].sort_index().rename("napcs32")
        s38 = df38.set_index("date")["value"].sort_index().rename("napcs38")
        aligned = pd.concat([s32, s38], axis=1)
        total = aligned.sum(axis=1, min_count=2).dropna().rename("value")
        out = total.reset_index()
        out.columns = ["date", "value"]

        country_name = country_labels[iso3]
        slug_out = f"exports_aluminum_{iso3}"
        meta = SeriesMeta(
            name=slug_out,
            source="Statistics Canada Web Data Service (derived)",
            source_url=_TABLE_URL,
            source_id=(
                f"{vids} — NAPCS 32+38 (aluminum), {country_name}, "
                "Table 12-10-0182-01."
            ),
            units="C$ millions",
            frequency="monthly",
            notes=(
                f"Canadian merchandise exports of aluminum (NAPCS 32 unwrought + "
                f"NAPCS 38 semi-finished), to {country_name}. NSA monthly, "
                f"C$ millions. Derived as sum of sub-components. "
                f"Source vectors: {vids}. Table 12-10-0182-01."
            ),
            transform="napcs32 + napcs38",
        )
        write_series(out, meta, DATA_PROCESSED)


def derive_gold_price_monthly() -> None:
    """Resample daily gold futures closes to monthly (last trading day of month).

    Input:  data/raw/gold_futures.csv  (GC=F daily close, USD/oz)
    Output: data/processed/gold_price_monthly.csv  (USD/oz, monthly)

    The daily series is fetched by pipeline.build_financial (Yahoo GC=F).
    This derivation produces the monthly companion for the Trade panel-9 chart,
    which wants gold price on the same time axis as the monthly StatCan trade
    series. Using month-end last observation is standard for commodity price
    time-series alignment with monthly trade data.

    We read from raw/ directly (not via _read_raw which defaults to the statcan
    catalog) because gold_futures is a Yahoo series, not a StatCan series.
    """
    raw_path = DATA_RAW / "gold_futures.csv"
    if not raw_path.exists():
        logger.warning("derive_gold_price_monthly: gold_futures.csv not found in raw/")
        return

    try:
        df = pd.read_csv(raw_path, parse_dates=["date"])
    except Exception as exc:  # noqa: BLE001
        logger.warning("derive_gold_price_monthly: failed to read gold_futures.csv: %s", exc)
        return

    if df.empty or "date" not in df.columns or "value" not in df.columns:
        logger.warning("derive_gold_price_monthly: gold_futures.csv empty or missing columns")
        return

    df = df.sort_values("date").dropna(subset=["value"])
    # Resample to monthly using last observation in each calendar month
    df = df.set_index("date")
    monthly = df["value"].resample("ME").last().dropna()
    # Shift index from month-end to first of month for consistent date keying
    # with StatCan monthly series (which use YYYY-MM-01 convention)
    monthly.index = monthly.index.to_period("M").to_timestamp()
    out = monthly.reset_index()
    out.columns = ["date", "value"]

    meta = SeriesMeta(
        name="gold_price_monthly",
        source="Yahoo Finance (v8 chart API) — GC=F (COMEX gold futures front month)",
        source_url="https://finance.yahoo.com/quote/GC%3DF",
        source_id="GC=F (COMEX gold futures front month), monthly last-obs resample",
        units="USD/oz",
        frequency="monthly",
        notes=(
            "COMEX gold futures (GC=F) front-month price, monthly, USD per troy ounce. "
            "Derived from daily close series (data/raw/gold_futures.csv) by taking the "
            "last trading-day close of each calendar month. Date keyed to first of "
            "month for alignment with StatCan monthly trade series. Replaces FRED LBMA "
            "series (GOLDAMGBD228NLBM) which was discontinued by ICE Benchmark "
            "Administration. Acceptable proxy at the monthly editorial cadence."
        ),
        transform="last_obs_per_calendar_month(gold_futures daily)",
    )
    write_series(out, meta, DATA_PROCESSED)


def derive_tariff_state_fixture() -> None:
    """Emit a static JSON fixture for the Trade Panel 4 tariff-state visualization.

    The tariff stack is an editorially-maintained log, not a time series. The
    source cards that document each US trade action affecting Canada already live
    in `editorial/source_cards/registry.yaml`; this step extracts the tariff-
    relevant cards and serializes them into a structured JSON at
    `data/derived/tariff_state.json` so the Panel4TariffState chart component
    can consume a machine-readable payload rather than hard-coding rows inline.

    The fixture schema:

        {
          "generated_at": "...",
          "as_of": "YYYY-MM-DD",
          "rows": [
            {
              "id":             <registry card id>,
              "label":          <short human label>,
              "rate_pct":       <primary rate as number>,
              "rate_label":     <display string, e.g. "50%">,
              "sector":         <sector string, e.g. "Steel & aluminum">,
              "mechanism":      <"Section 232" | "IEEPA" | "USMCA" | ...>,
              "effective_date": "YYYY-MM-DD",
              "status":         "in_force" | "suspended" | "under_review",
              "source_url":     <card url>,
              "excerpt":        <verbatim excerpt from primary source>,
              "notes":          <optional string>
            },
            ...
          ]
        }

    Panel4TariffState.astro will be built by chart-builder to consume this
    fixture via the panel's `metadata` key (wired through metadata_path in
    the PanelSpec). When the chart component is built it should render a
    ranked-row table or stack visualization from `data.metadata.rows`.
    """
    import json as _json

    registry_path = ROOT / "editorial" / "source_cards" / "registry.yaml"
    if not registry_path.exists():
        logger.warning("derive_tariff_state_fixture skipped: registry.yaml not found at %s", registry_path)
        return

    try:
        from ruamel.yaml import YAML as _YAML
        _yaml = _YAML()
        _yaml.preserve_quotes = True
        registry = _yaml.load(registry_path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        logger.warning("derive_tariff_state_fixture: failed to parse registry.yaml: %s", exc)
        return

    sources = registry.get("sources", [])

    # Card IDs that represent tariff/trade-action entries for the plate.
    TARIFF_CARD_MAP = {
        "eo_14193_ieepa_canada_2025": {
            "label": "IEEPA — general goods 25%, energy 10%",
            "sector": "All goods (USMCA non-compliant)",
            "mechanism": "IEEPA",
            "rate_pct": 35,           # as-amended by eo_14193_amendment_35pct below
            "rate_label": "25% -> 35%",
            "status": "in_force",
        },
        "eo_14193_amendment_35pct": {
            "label": "IEEPA amendment — general goods raised to 35%",
            "sector": "All goods (USMCA non-compliant)",
            "mechanism": "IEEPA",
            "rate_pct": 35,
            "rate_label": "35%",
            "status": "in_force",
        },
        "pp_section_232_steel_alum_50pct": {
            "label": "Section 232 — steel & aluminum 50%",
            "sector": "Steel & aluminum",
            "mechanism": "Section 232",
            "rate_pct": 50,
            "rate_label": "50%",
            "status": "in_force",
        },
        "pp_section_232_metals_copper_2026": {
            "label": "Section 232 — steel, aluminum, copper reinforced at 50%",
            "sector": "Steel, aluminum & copper",
            "mechanism": "Section 232",
            "rate_pct": 50,
            "rate_label": "50% (core); 25% (derivatives)",
            "status": "in_force",
        },
        "pp_10908_section_232_autos": {
            "label": "Section 232 — autos & parts 25%",
            "sector": "Autos & auto parts",
            "mechanism": "Section 232",
            "rate_pct": 25,
            "rate_label": "25%",
            "status": "in_force",
        },
        "pp_10976_section_232_lumber": {
            "label": "Section 232 — softwood lumber 10%, furniture/cabinets 25%",
            "sector": "Lumber & wood products",
            "mechanism": "Section 232",
            "rate_pct": 10,
            "rate_label": "10% lumber; 25% furniture/cabinets",
            "status": "in_force",
        },
        "usmca_article_34_7": {
            "label": "USMCA Article 34.7 — joint review July 1, 2026",
            "sector": "All USMCA-compliant goods",
            "mechanism": "USMCA",
            "rate_pct": None,
            "rate_label": "Review pending",
            "status": "under_review",
        },
    }

    # Index registry cards by id for O(1) lookup.
    card_index = {c.get("id"): c for c in sources if isinstance(c, dict)}

    rows = []
    display_order = [
        "pp_section_232_metals_copper_2026",   # most recent steel/alum/copper update
        "pp_section_232_steel_alum_50pct",
        "pp_10908_section_232_autos",
        "pp_10976_section_232_lumber",
        "eo_14193_amendment_35pct",
        "eo_14193_ieepa_canada_2025",
        "usmca_article_34_7",
    ]
    for card_id in display_order:
        card = card_index.get(card_id)
        if card is None:
            logger.warning("derive_tariff_state_fixture: card id=%s not found in registry", card_id)
            continue
        meta = TARIFF_CARD_MAP.get(card_id, {})
        verified_value = card.get("verified_value", {}) or {}
        # For autos (pp_10908), effective_date_autos is the autos effective date.
        effective_date = (
            str(verified_value.get("effective_date", ""))
            or str(verified_value.get("effective_date_autos", ""))
            or str(verified_value.get("signed_date", ""))
            or ""
        )
        rows.append({
            "id": card_id,
            "label": meta.get("label", card.get("title", card_id)),
            "rate_pct": meta.get("rate_pct"),
            "rate_label": meta.get("rate_label", ""),
            "sector": meta.get("sector", ""),
            "mechanism": meta.get("mechanism", ""),
            "effective_date": effective_date,
            "status": meta.get("status", "in_force"),
            "source_url": card.get("url", ""),
            "excerpt": card.get("excerpt", ""),
            "verified_at": str(card.get("verified_at", "")),
            "verification_tier": card.get("verification_tier", ""),
        })

    # Most-recent effective_date among in-force rows as the fixture as_of.
    in_force_dates = [
        r["effective_date"] for r in rows
        if r["status"] == "in_force" and r["effective_date"]
    ]
    as_of = max(in_force_dates) if in_force_dates else datetime_now_iso()[:10]

    fixture = {
        "name": "tariff_state",
        "generated_at": datetime_now_iso(),
        "as_of": as_of,
        "source": "editorial/source_cards/registry.yaml (tariff-action cards)",
        "notes": (
            "Editorially-maintained tariff-state log derived from verified source cards. "
            "Each row corresponds to a primary-verified US trade action affecting Canada. "
            "Update registry.yaml to add new actions; this fixture re-generates on each build. "
            "Chart component: src/components/charts/trade/Panel4TariffState.astro."
        ),
        "rows": rows,
    }

    DATA_DERIVED.mkdir(parents=True, exist_ok=True)
    out_path = DATA_DERIVED / "tariff_state.json"
    out_path.write_text(_json.dumps(fixture, indent=2, default=str) + "\n", encoding="utf-8")
    logger.info("tariff_state fixture: %d rows -> %s", len(rows), out_path)


# --------------------------------------------------------------------------- #
# Orchestrator
# --------------------------------------------------------------------------- #

def _parse_build_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="python -m pipeline.build",
        description="Run the macro-research-department data pipeline.",
    )
    p.add_argument(
        "--fan-out",
        action="store_true",
        help=(
            "After the data refresh, detect a release event (content-hash "
            "change on a primary series sidecar vs the rotated snapshot) "
            "and fan-out a fresh-cascade through every affected surface "
            "(section blurb, tileLine, plate interpretations, fresh-tag "
            "rotation, hero abstract). Default OFF for manual local "
            "rebuilds so the user is not surprised by writer dispatches; "
            "CI / scheduled runs set the GITHUB_ACTIONS env var (or pass "
            "--fan-out explicitly) which flips this to ON automatically."
        ),
    )
    p.add_argument(
        "--no-fan-out",
        action="store_true",
        help=(
            "Force the fan-out OFF even in CI. Useful for data-only "
            "rebuilds that should not retrigger LLM dispatches."
        ),
    )
    return p.parse_args(argv)


def main(argv: Optional[list[str]] = None) -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    args = _parse_build_args(argv)
    DATA_RAW.mkdir(parents=True, exist_ok=True)
    DATA_PROCESSED.mkdir(parents=True, exist_ok=True)
    DATA_DERIVED.mkdir(parents=True, exist_ok=True)

    failed: list[str] = []

    # 1) StatCan catalog (GDP, Inflation, Labour, Housing, Trade) -- skip
    #    daily/financial. Each series is isolated per _safe().
    logger.info("--- StatCan WDS catalog ---")
    run_statcan_catalog(failed)

    # 2) BoC Valet non-daily (CPI core, policy rate monthly, expectations,
    #    output gap, balance sheet, mortgage rates).
    logger.info("--- BoC Valet (non-daily) ---")
    run_boc_catalog_non_daily(failed)

    # 3) IMF WEO DataMapper (annual, general-government fiscal stance).
    #    Policy panel-7-alt: fed_deficit_to_gdp + fed_net_debt_to_gdp slots.
    #    Scope caveat: general government (federal + provincial + local),
    #    NOT federal-only. Noted in .meta.json and data/SOURCES.md.
    logger.info("--- IMF WEO DataMapper ---")
    run_imf_catalog(failed)

    # 4) DoF Fiscal Monitor (monthly, ~2-month lag).
    logger.info("--- DoF Fiscal Monitor ---")
    _safe("dof_fiscal_monitor", fetch_dof_fiscal_monitor, failed)

    # 5) CREA MLS HPI (monthly XLSX bulk). Per-geography isolation inside.
    logger.info("--- CREA MLS HPI ---")
    _safe("crea_mls_hpi", fetch_crea_mls_hpi, failed)

    # 5b) CBA mortgage arrears (PDF, monthly, ~2.5-month lag). Powers the
    #     housing supporting print `cmhc-arrears` (renamed to "Bank mortgage
    #     arrears" because CBA != CMHC; CBA is the chartered-bank slice).
    logger.info("--- CBA mortgage arrears ---")
    _safe("cba_mortgage_arrears", fetch_cba_mortgage_arrears, failed)

    # 5) Alberta Economic Dashboard -- monthly natural-gas price (canon 4.6 element 4).
    logger.info("--- Alberta Dashboard (natural gas) ---")
    _safe("alberta_natural_gas", fetch_alberta_natural_gas, failed)

    # 5b) CPI basket weights (Table 18-10-0007-01). One pull per basket cycle;
    #     output goes to data/derived/ for the pass-through panel (canon 4.2
    #     element 6). Per-aggregate raw CSVs already landed in step 1 via the
    #     StatCan catalog; this step writes the consolidated cross-aggregate view.
    logger.info("--- CPI basket weights ---")
    _safe("cpi_basket_weights", fetch_cpi_basket_weights, failed)

    # 5c) CPI components (60-vector wide-format) -- must run BEFORE derivations,
    #     which consume data/raw/cpi_components.csv. Replaces the one-time
    #     boc-tracker lift with a daily StatCan fetch (2026-05-19).
    logger.info("--- CPI components ---")
    _safe("cpi_components", fetch_and_write_cpi_components, failed)

    # 6) Cross-series derivations. Run AFTER fetches so the disk cache is
    #    populated. Each derivation is isolated; failures don't cascade.
    logger.info("--- Derivations ---")
    _safe("derive_cpi_views", derive_cpi_views, failed)
    _safe("derive_cpi_services_ex_shelter_yoy", derive_cpi_services_ex_shelter_yoy, failed)
    _safe("derive_cpi_breadth_gt3", derive_cpi_breadth_gt3, failed)
    _safe("derive_cpi_breadth_band", derive_cpi_breadth_band, failed)
    _safe("derive_gdp_views", derive_gdp_views, failed)
    _safe("derive_gdp_per_capita_yoy", derive_gdp_per_capita_yoy, failed)
    _safe("derive_productivity_views", derive_productivity_views, failed)
    _safe("derive_trade_views", derive_trade_views, failed)
    _safe("derive_terms_of_trade", derive_terms_of_trade, failed)
    _safe("derive_current_account_views", derive_current_account_views, failed)
    _safe("derive_federal_fiscal_ytd", derive_federal_fiscal_ytd, failed)
    _safe("derive_labour_force_ex_npr", derive_labour_force_ex_npr, failed)
    _safe("derive_boc_fed_spread_monthly", derive_boc_fed_spread_monthly, failed)
    _safe("derive_sectoral_exports_by_destination", derive_sectoral_exports_by_destination, failed)
    _safe("derive_gold_exports", derive_gold_exports, failed)
    _safe("derive_aluminum_by_partner", derive_aluminum_by_partner, failed)
    _safe("derive_gold_price_monthly", derive_gold_price_monthly, failed)
    _safe("derive_tariff_state_fixture", derive_tariff_state_fixture, failed)

    # 6b) Snapshot the PRIOR vintage of data/site/* before step 7
    #     overwrites it. This feeds the diff-aware writer brief (see
    #     pipeline/blurbs/diff_brief.py). Last-12 rotation keeps disk
    #     usage bounded. Failures here do not block the build.
    logger.info("--- Snapshot prior site-data vintage ---")
    try:
        from pipeline.blurbs.diff_brief import snapshot_current_payload
        snap_path = snapshot_current_payload(ROOT)
        logger.info("snapshot written: %s", snap_path)
    except Exception as exc:  # noqa: BLE001
        logger.warning("snapshot step failed (non-fatal): %s", exc)

    # 7) Site data bundle. Final step: read selected CSV + .meta.json files
    #    and emit data/site/sections.json for the Astro side to import at
    #    build time. Per-section failures are absorbed inside build_site_data
    #    (a missing series yields a sentinel entry, not an exception), so
    #    this step never sinks the whole pipeline build.
    logger.info("--- Site data bundle ---")
    DATA_SITE.mkdir(parents=True, exist_ok=True)
    _safe("build_site_data", lambda: build_site_data(DATA_ROOT), failed)

    # 8) Per-section panel data bundle (data/site/panel_data/<section>.json).
    #    Mirrors the Props interfaces of each src/components/charts/<section>/
    #    Panel*.astro file; chart-builder consumes the JSON at build time.
    #    Per-panel failures fall back to a sentinel slot, not an exception.
    logger.info("--- Panel data bundle ---")
    _safe("build_panel_data", lambda: build_all_panel_data(DATA_ROOT), failed)

    # 9) Optional: fan-out cascade. Detects whether a release event
    #    landed (content-hash change on a primary series sidecar vs the
    #    snapshot taken in step 6b) and, if so, cascades that release
    #    through every affected surface (section blurb, tileLine, plate
    #    interpretations, fresh-tag rotation, hero abstract). Default
    #    behaviour:
    #      - CI / scheduled runs (GITHUB_ACTIONS env var set): ON.
    #      - Manual local run: OFF, unless --fan-out is passed.
    #      - --no-fan-out forces OFF regardless of CI.
    #    The fan-out itself is failure-isolated; a dispatch error logs
    #    and the build still exits on the data-side failed list.
    auto_on = bool(os.environ.get("GITHUB_ACTIONS"))
    fan_out_enabled = (args.fan_out or auto_on) and not args.no_fan_out
    if fan_out_enabled:
        logger.info("--- Fan-out cascade ---")
        try:
            from pipeline.blurbs.fan_out import (
                detect_release_event,
                fan_out_release,
            )
            event = detect_release_event(ROOT)
            if event is None:
                logger.info(
                    "fan_out: no release event detected (no sidecar "
                    "release_date newer than snapshot); nothing to do.",
                )
            else:
                logger.info(
                    "fan_out: cascade trigger -- release_id=%s "
                    "release_key=%s section=%s release_date=%s",
                    event.release_id, event.release_key,
                    event.section, event.release_date,
                )
                result = fan_out_release(event, repo_root=ROOT)
                logger.info(
                    "fan_out: drafted=%d failed=%d promoted=%s error=%s",
                    result.surfaces_drafted, result.surfaces_failed,
                    result.promoted, result.error,
                )
                if not result.promoted:
                    failed.append("fan_out_release")
        except Exception as exc:  # noqa: BLE001
            logger.error("FAILED: fan_out -- %s: %s", type(exc).__name__, exc)
            logger.debug("traceback:\n%s", traceback.format_exc())
            failed.append("fan_out")

    if failed:
        logger.error("Build completed with %d failure(s): %s", len(failed), ", ".join(failed))
        return 1
    logger.info("Build completed successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
