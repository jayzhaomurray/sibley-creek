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
    - Cross-series derivations (per-capita employment, trade balance 3M MA,
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

import logging
import sys
import traceback
from pathlib import Path
from typing import Callable, Optional

import pandas as pd

from pipeline.catalog import BOC_VALET_SERIES, STATCAN_SERIES
from pipeline.catalog.boc_series import BocSpec
from pipeline.catalog.statcan_series import StatcanSpec, get_url as statcan_url
from pipeline.fetch import alberta, boc, cpi_basket, crea, dof_fiscal, statcan
from pipeline.io import SeriesMeta, build_site_data, write_series
from pipeline.transform import yoy_pct
from pipeline.transform.derivations import (
    headline_yoy,
    partner_share_trajectory,
    per_capita_growth,
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


def derive_per_capita_employment() -> None:
    """Per-capita employment Y/Y, the canon 4.3 element-2 signature.

    Computed as employment_level Y/Y minus pop_total Y/Y (BoC MPR convention,
    per researcher memo Wave 1 brief 1.2). Employment is monthly; population
    is quarterly. We resample population to monthly via forward-fill, since
    population is a slow-moving stock estimate.
    """
    emp = _read_raw("employment_level")
    pop = _read_raw("pop_total")
    if emp is None or pop is None:
        return
    # Forward-fill population to monthly cadence on employment dates.
    pop_m = (
        pop.set_index("date")
        .sort_index()
        .reindex(emp["date"].sort_values(), method="ffill")
        .reset_index()
    )
    pop_m.columns = ["date", "value"]
    out = per_capita_growth(emp, pop_m, periods_per_year=12)
    spec = STATCAN_SERIES["employment_level"]
    meta = SeriesMeta(
        name="employment_per_capita_yoy",
        source="Statistics Canada Web Data Service (derived)",
        source_url=statcan_url(spec),
        source_id="v2062811-minus-v1 (employment_yoy minus pop_total_yoy)",
        units="% (percentage points)",
        frequency="monthly",
        notes=(
            "Per-capita employment growth: employment Y/Y minus population Y/Y. "
            "Population (Table 17-10-0009-01, quarterly) forward-filled to "
            "monthly cadence to align with LFS employment. Per BoC MPR convention."
        ),
        transform="per_capita_growth(periods_per_year=12)",
    )
    write_series(out, meta, DATA_PROCESSED)


def derive_trade_views() -> None:
    """Trade-balance 3M MA + partner-share trajectories (canon 4.7 elements 1, 3)."""
    balance = _read_raw("trade_balance_total")
    if balance is not None:
        ma3 = trade_balance_3m_ma(balance, window=3)
        spec = STATCAN_SERIES["trade_balance_total"]
        meta = SeriesMeta(
            name="trade_balance_total_3m_ma",
            source="Statistics Canada Web Data Service (derived)",
            source_url=statcan_url(spec),
            source_id=f"v{spec.vector_id} (3M MA)",
            units="CAD millions",
            frequency="monthly",
            notes=(
                "Trade balance 3-month moving average. Standard noise-suppression "
                "for monthly trade data per canon 4.7 element 1."
            ),
            transform="moving_average(window=3)",
        )
        write_series(ma3, meta, DATA_PROCESSED)

    # Partner shares: US is the structural-shift line per canon 4.7 element 3.
    # Other partners' shares are derived too, when their raw fetches succeeded.
    exports_total = _read_raw("trade_exports_total")
    imports_total = _read_raw("trade_imports_total")
    partner_targets = [
        ("us", "United States"),
        ("china", "China"),
        ("uk", "United Kingdom"),
        ("japan", "Japan"),
        ("mexico", "Mexico"),
        ("germany", "Germany"),
    ]
    for slug, label in partner_targets:
        for side, total in (("exports", exports_total), ("imports", imports_total)):
            partner = _read_raw(f"trade_{side}_{slug}")
            if partner is None or total is None:
                continue
            share = partner_share_trajectory(partner, total, label_partner=label)
            meta = SeriesMeta(
                name=f"trade_{side}_share_{slug}",
                source="Statistics Canada Web Data Service (derived)",
                source_url=statcan_url(STATCAN_SERIES["trade_balance_total"]),
                source_id=f"share-of-total-{side}-by-partner-{slug}",
                units="% share",
                frequency="monthly",
                notes=f"{label} share of total Canadian {side}. Derived from per-partner / total.",
                transform="partner_share_trajectory",
            )
            write_series(share, meta, DATA_PROCESSED)


# --------------------------------------------------------------------------- #
# Orchestrator
# --------------------------------------------------------------------------- #

def main() -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
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

    # 3) DoF Fiscal Monitor (monthly, ~2-month lag).
    logger.info("--- DoF Fiscal Monitor ---")
    _safe("dof_fiscal_monitor", fetch_dof_fiscal_monitor, failed)

    # 4) CREA MLS HPI (monthly XLSX bulk). Per-geography isolation inside.
    logger.info("--- CREA MLS HPI ---")
    _safe("crea_mls_hpi", fetch_crea_mls_hpi, failed)

    # 5) Alberta Economic Dashboard -- monthly natural-gas price (canon 4.6 element 4).
    logger.info("--- Alberta Dashboard (natural gas) ---")
    _safe("alberta_natural_gas", fetch_alberta_natural_gas, failed)

    # 5b) CPI basket weights (Table 18-10-0007-01). One pull per basket cycle;
    #     output goes to data/derived/ for the pass-through panel (canon 4.2
    #     element 6). Per-aggregate raw CSVs already landed in step 1 via the
    #     StatCan catalog; this step writes the consolidated cross-aggregate view.
    logger.info("--- CPI basket weights ---")
    _safe("cpi_basket_weights", fetch_cpi_basket_weights, failed)

    # 6) Cross-series derivations. Run AFTER fetches so the disk cache is
    #    populated. Each derivation is isolated; failures don't cascade.
    logger.info("--- Derivations ---")
    _safe("derive_cpi_views", derive_cpi_views, failed)
    _safe("derive_per_capita_employment", derive_per_capita_employment, failed)
    _safe("derive_trade_views", derive_trade_views, failed)

    # 7) Site data bundle. Final step: read selected CSV + .meta.json files
    #    and emit data/site/sections.json for the Astro side to import at
    #    build time. Per-section failures are absorbed inside build_site_data
    #    (a missing series yields a sentinel entry, not an exception), so
    #    this step never sinks the whole pipeline build.
    logger.info("--- Site data bundle ---")
    DATA_SITE.mkdir(parents=True, exist_ok=True)
    _safe("build_site_data", lambda: build_site_data(DATA_ROOT), failed)

    if failed:
        logger.error("Build completed with %d failure(s): %s", len(failed), ", ".join(failed))
        return 1
    logger.info("Build completed successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
