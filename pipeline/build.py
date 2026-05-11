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

import logging
import sys
import traceback
from pathlib import Path
from typing import Callable, Optional

import pandas as pd

from pipeline.catalog import BOC_VALET_SERIES, STATCAN_SERIES
from pipeline.catalog.boc_series import BocSpec
from pipeline.catalog.statcan_series import StatcanSpec, get_url as statcan_url
from pipeline.fetch import alberta, boc, cba_arrears, cpi_basket, crea, dof_fiscal, statcan
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

    # 4b) CBA mortgage arrears (PDF, monthly, ~2.5-month lag). Powers the
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

    # 6) Cross-series derivations. Run AFTER fetches so the disk cache is
    #    populated. Each derivation is isolated; failures don't cascade.
    logger.info("--- Derivations ---")
    _safe("derive_cpi_views", derive_cpi_views, failed)
    _safe("derive_cpi_breadth_gt3", derive_cpi_breadth_gt3, failed)
    _safe("derive_gdp_views", derive_gdp_views, failed)
    _safe("derive_gdp_per_capita_yoy", derive_gdp_per_capita_yoy, failed)
    _safe("derive_productivity_views", derive_productivity_views, failed)
    _safe("derive_trade_views", derive_trade_views, failed)
    _safe("derive_terms_of_trade", derive_terms_of_trade, failed)
    _safe("derive_current_account_views", derive_current_account_views, failed)
    _safe("derive_federal_fiscal_ytd", derive_federal_fiscal_ytd, failed)

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

    if failed:
        logger.error("Build completed with %d failure(s): %s", len(failed), ", ".join(failed))
        return 1
    logger.info("Build completed successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
