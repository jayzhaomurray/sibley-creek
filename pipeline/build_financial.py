r"""Daily-cadence Financial-section build.

Decoupled from the main monthly build (`pipeline.build`) because the
Financial section refreshes every North American trading day, not on the
StatCan monthly release cadence (canon 4.6 + the daily "what moved overnight"
absorption, per wave1_data_scope_financial_trade.md Section 1.3).

Schedule
--------
Run post-close, 18:00 ET, to capture:
    - BoC Valet daily series (typically published ~16:30 ET): GoC yields,
      FX, CEER, BCPI, CORRA, etc.
    - FRED daily updates (typically late afternoon ET): US Treasuries, VIX,
      DTWEXBGS, IG/HY OAS, WTI, Brent.
    - Yahoo daily closes: TSX (^GSPTSE), S&P 500 (^GSPC), gold futures (GC=F).
    - Indeed Hiring Lab Canada postings (refreshed weekly; the daily pull is
      a no-op on most days, and the labour panel-4 monthly companion derives
      in-place after the daily lands).

Failure isolation
-----------------
Daily fetches fail more often than monthly StatCan fetches: FRED rate-limits,
Yahoo schema drifts, BoC Valet returns intermittent 5xx. Each series is
wrapped in `_safe()` so one bad ticker does not block the rest. The exit
code is non-zero if anything failed, so the GitHub Actions scheduled run
surfaces the failure list in the UI; the rest of the day's data still
landed on disk.

Run from the repo root with the venv active:

    .\.venv\Scripts\python.exe -m pipeline.build_financial

Output:
    data/raw/<name>.csv          one per upstream series
    data/raw/<name>.meta.json    sidecar metadata
    data/processed/<name>.csv    derivations (GoC-UST spreads, USDCAD pct
                                 deviation, etc.) wired downstream
"""

from __future__ import annotations

import logging
import os
import sys
import traceback
from pathlib import Path
from typing import Callable, Optional

import pandas as pd

from pipeline.catalog import BOC_VALET_SERIES, FRED_SERIES, INDEED_SERIES, YAHOO_SERIES
from pipeline.catalog.boc_series import BocSpec
from pipeline.catalog.fred_series import FredSpec
from pipeline.catalog.indeed_series import IndeedSpec
from pipeline.catalog.yahoo_series import YahooSpec
from pipeline.fetch import boc, fred, indeed_hiring_lab, yahoo
from pipeline.io import SeriesMeta, build_site_data, write_series, write_series_merge
from pipeline.io.panel_data import build_all_panel_data
from pipeline.transform.derivations import goc_ust_spread

ROOT = Path(__file__).resolve().parent.parent
DATA_RAW = ROOT / "data" / "raw"
DATA_PROCESSED = ROOT / "data" / "processed"

logger = logging.getLogger("pipeline.build_financial")


# --------------------------------------------------------------------------- #
# Per-series failure isolation (mirrors pipeline.build._safe)
# --------------------------------------------------------------------------- #

def _safe(label: str, fn: Callable[[], None], failed: list[str]) -> None:
    logger.info("==> %s", label)
    try:
        fn()
    except Exception as exc:  # noqa: BLE001
        logger.error("FAILED: %s -- %s: %s", label, type(exc).__name__, exc)
        logger.debug("traceback:\n%s", traceback.format_exc())
        failed.append(label)


# --------------------------------------------------------------------------- #
# BoC Valet daily-cadence fetch
# --------------------------------------------------------------------------- #

def _boc_daily_fetch_one(spec: BocSpec) -> None:
    """Fetch one daily-cadence BoC Valet entry (yields, FX, CEER, BCPI, CORRA).

    No vintage fallback here -- daily-cadence series are stable Valet keys
    with no MPR-style rotation. If the key fails, surface it as a flagged
    failure.
    """
    result = boc.fetch_series(spec.series_key, start_date=spec.start_date)
    df = result.data.copy()
    if spec.scale != 1.0 and not df.empty:
        df["value"] = df["value"] * spec.scale

    label_block = f" BoC-published label: {result.label!r}." if result.label else ""
    notes = (spec.notes or "") + label_block
    notes = notes.strip() or None

    meta = SeriesMeta(
        name=spec.name,
        source="Bank of Canada Valet API",
        source_url=boc.observations_url(spec.series_key),
        source_id=spec.series_key,
        units=spec.units,
        frequency=spec.frequency,
        notes=notes,
    )
    write_series(df, meta, DATA_RAW)


def run_boc_catalog_daily(failed: list[str]) -> None:
    """Fetch every BoC Valet entry whose cadence is daily.

    Includes: 2y/5y/10y/30y/3m GoC yields, FXUSDCAD + EUR/GBP/JPY crosses,
    CEER family, CORRA, daily overnight rate, BCPI/BCNEI.
    """
    for name, spec in BOC_VALET_SERIES.items():
        if spec.cadence != "daily":
            continue
        _safe(f"boc-daily:{name}", lambda s=spec: _boc_daily_fetch_one(s), failed)


# --------------------------------------------------------------------------- #
# FRED daily-cadence fetch
# --------------------------------------------------------------------------- #

def _fred_fetch_one(spec: FredSpec) -> None:
    """Fetch one FRED series per the catalog spec.

    The composite Fed-funds target (`__COMPOSITE_FED_FUNDS_TARGET__`) is
    dispatched to `fred.fetch_fed_funds_target` rather than the single-series
    call.
    """
    if spec.series_id == "__COMPOSITE_FED_FUNDS_TARGET__":
        df = fred.fetch_fed_funds_target()
        source_url = "https://fred.stlouisfed.org/series/FEDFUNDS"
        source_id = "FEDFUNDS+DFEDTARU+DFEDTARL"
    else:
        result = fred.fetch_series(spec.series_id, start_date=spec.start_date)
        df = result.data
        source_url = fred.series_url(spec.series_id)
        source_id = spec.series_id

    meta = SeriesMeta(
        name=spec.name,
        source="Federal Reserve Bank of St. Louis (FRED)",
        source_url=source_url,
        source_id=source_id,
        units=spec.units,
        frequency=spec.frequency,
        notes=spec.notes or None,
    )
    write_series(df, meta, DATA_RAW)


def run_fred_catalog(failed: list[str]) -> None:
    """Run every FRED catalog entry. Skips silently if FRED_API_KEY is unset.

    Per `pipeline/fetch/fred.py`, the absence of a key raises ValueError;
    we treat that as a logged warning + a single failure entry, so the user
    sees "FRED skipped: no API key" rather than a stack trace.
    """
    if not fred.get_api_key():
        logger.warning("FRED_API_KEY is not set; skipping all %d FRED series", len(FRED_SERIES))
        failed.append("fred:no-api-key")
        return
    for name, spec in FRED_SERIES.items():
        _safe(f"fred:{name}", lambda s=spec: _fred_fetch_one(s), failed)


# --------------------------------------------------------------------------- #
# Yahoo daily-close fetch
# --------------------------------------------------------------------------- #

def _yahoo_fetch_one(spec: YahooSpec) -> None:
    """Fetch one Yahoo symbol and merge-write the result.

    Uses `write_series_merge` rather than `write_series` because Yahoo's
    `range=max` response has been observed to occasionally return a
    mixed-cadence frame (monthly aggregations for older periods, daily
    for the most recent weeks) -- notably on the CL=F / BZ=F oil futures
    symbols. A direct overwrite in that case truncates the on-disk daily
    history. The merge preserves any prior daily rows whose dates Yahoo
    no longer returns, while still picking up new daily rows and any
    upstream-revised values for dates that do appear in the new response.
    """
    # Yahoo silently downsamples `range=max + interval=1d` to quarterly
    # for ^GSPTSE (and likely the other indices) — verified 2026-05-19,
    # ~167 quarterly points returned where daily was expected. Pinning to
    # "10y" returns proper daily. write_series_merge preserves any older
    # daily history already on disk; we only lose pre-2015 history that
    # never landed daily anyway (see corrupted .csv state pre-2026-05-19).
    result = yahoo.fetch_daily_close(spec.symbol, range_="10y")
    df = result.data
    meta = SeriesMeta(
        name=spec.name,
        source="Yahoo Finance (v8 chart API)",
        source_url=yahoo.symbol_url(spec.symbol),
        source_id=spec.symbol,
        units=spec.units,
        frequency="daily",
        notes=(spec.notes or "") + " Adjusted close where Yahoo exposes it, else raw close.",
    )
    write_series_merge(df, meta, DATA_RAW)


def run_yahoo_catalog(failed: list[str]) -> None:
    for name, spec in YAHOO_SERIES.items():
        _safe(f"yahoo:{name}", lambda s=spec: _yahoo_fetch_one(s), failed)


# --------------------------------------------------------------------------- #
# Indeed Hiring Lab daily-cadence fetch
# --------------------------------------------------------------------------- #
#
# Indeed publishes weekly; running daily is fine -- most days the upstream
# bytes are unchanged and the git commit step is a no-op. The aggregate
# fetch lives under build_financial (rather than the monthly orchestrator)
# so it refreshes on the same post-close schedule that already runs FRED,
# Yahoo, and BoC dailies. The downstream monthly mean (consumed by labour
# panel-4) is derived in-place after the daily pull lands.

def _indeed_fetch_one(spec: IndeedSpec) -> None:
    """Fetch one Indeed Hiring Lab catalog entry + write the monthly companion.

    For the aggregate Canada SA total-postings series we additionally write
    a monthly-mean companion (`indeed_postings_ca_monthly`) because the
    labour panel-4 consumes the monthly cadence directly (to align with
    JVWS's monthly cadence). Other variable / measure combinations would
    skip the monthly companion -- panel-4 is the only consumer today.
    """
    result = indeed_hiring_lab.fetch_aggregate_postings(
        variable=spec.variable, measure=spec.measure
    )
    df = result.data

    notes = (
        f"{spec.notes} Source column: {result.source_column}; "
        f"variable={result.variable!r}."
    ).strip()

    meta = SeriesMeta(
        name=spec.name,
        source="Indeed Hiring Lab - Canada job postings",
        source_url=indeed_hiring_lab.aggregate_html_url(),
        source_id=f"hiring-lab/job_postings_tracker/CA/{spec.filename}",
        units=spec.units,
        frequency=spec.cadence,
        notes=notes,
    )
    write_series(df, meta, DATA_RAW)

    # Monthly companion: panel-4 reads `indeed_postings_ca_monthly` directly.
    # Only wire for the canonical SA total-postings spec; skip for any
    # future NSA / new-postings additions.
    if spec.name == "indeed_postings_ca" and spec.measure == "SA" and spec.variable == "total postings":
        monthly = indeed_hiring_lab.aggregate_monthly_mean(df)
        monthly_meta = SeriesMeta(
            name=f"{spec.name}_monthly",
            source="Indeed Hiring Lab - Canada job postings",
            source_url=indeed_hiring_lab.aggregate_html_url(),
            source_id=f"hiring-lab/job_postings_tracker/CA/{spec.filename}",
            units=spec.units,
            frequency="monthly",
            notes=(
                "Indeed Canada postings index, monthly mean of daily SA "
                "values (month-start convention). Derived from "
                f"{spec.name}.csv. Aligns cadence with StatCan JVWS for "
                "labour panel-4 overlay."
            ),
            transform="monthly_mean(daily)",
        )
        write_series(monthly, monthly_meta, DATA_RAW)


def run_indeed_catalog(failed: list[str]) -> None:
    for name, spec in INDEED_SERIES.items():
        _safe(f"indeed:{name}", lambda s=spec: _indeed_fetch_one(s), failed)


# --------------------------------------------------------------------------- #
# Cross-series derivations (Financial-section only)
# --------------------------------------------------------------------------- #

def _read_raw(name: str) -> Optional[pd.DataFrame]:
    path = DATA_RAW / f"{name}.csv"
    if not path.exists():
        logger.warning("derivation skipped: missing raw %s", path.name)
        return None
    df = pd.read_csv(path, parse_dates=["date"])
    return df


def derive_goc_ust_spreads() -> None:
    """Compute GoC-UST 2y and 10y spreads (canon 4.6 element 2).

    BoC publishes Canadian close ~16:30 ET; FRED publishes US Treasury values
    ~15:30 ET. A one-day stagger at month-end is acceptable -- consumed as a
    level trajectory, not arbitrage. Date alignment is inner-join on date.
    """
    pairs = [
        ("yield_2yr", "us_2yr", "goc_ust_spread_2y", "2y"),
        ("yield_10yr", "us_10yr", "goc_ust_spread_10y", "10y"),
    ]
    for goc_name, ust_name, out_name, tenor in pairs:
        goc = _read_raw(goc_name)
        ust = _read_raw(ust_name)
        if goc is None or ust is None:
            continue
        spread = goc_ust_spread(goc, ust)
        meta = SeriesMeta(
            name=out_name,
            source="BoC Valet + FRED (derived)",
            source_url="https://www.bankofcanada.ca/valet/ + https://fred.stlouisfed.org/",
            source_id=f"{goc_name}-minus-{ust_name}",
            units="percentage points",
            frequency="daily",
            notes=(
                f"GoC {tenor} yield minus UST {tenor} yield, aligned on shared "
                "trading days. Per canon 4.6 element 2; one-day stagger possible "
                "at month-end (BoC ~16:30 ET vs FRED ~15:30 ET)."
            ),
            transform="goc_ust_spread",
        )
        write_series(spread, meta, DATA_PROCESSED)


def derive_corra_overnight_spread() -> None:
    """Daily CORRA-vs-overnight-target spread in basis points.

    Per Wave 5 brief (editorial/wave5_boc_tracker_chart_decisions.md, Section 5,
    backend item 3): the Balance Sheet panel (Policy panel-4) carries CORRA-target
    spread as a secondary view, surfacing whether the BoC's floor regime is
    functioning. Spread = CORRA daily - overnight rate (target) daily.

    Inputs:
        data/raw/corra_daily.csv          BoC Valet AVG.INTWO (daily, 2009-01-02 onward)
        data/raw/overnight_rate_daily.csv BoC Valet V39079    (daily, 2009-04-21 onward)

    Mismatch handling: CORRA publishes for every business day; the daily
    overnight rate is also published daily (it changes only on FAD dates but
    BoC carries the prevailing target through non-FAD days). We forward-fill
    the overnight rate onto CORRA's date axis to handle any holiday-day
    asymmetries cleanly, then join and take the difference.

    Output:
        data/processed/corra_overnight_spread_bps.csv
            spread in basis points (CORRA% - target%) * 100. Positive = CORRA
            trades above target (typical for a tight liquidity regime); zero
            or slightly negative = floor-maintenance regime working as
            intended.

    20-day smoothing is applied at the panel layer per editorial brief, NOT
    here. Backend ships the raw daily spread.
    """
    corra = _read_raw("corra_daily")
    target = _read_raw("overnight_rate_daily")
    if corra is None or target is None:
        return
    c = corra.set_index("date")["value"].sort_index().rename("corra")
    t = target.set_index("date")["value"].sort_index().rename("target")
    # Forward-fill the target onto the union date axis so any CORRA-day that
    # falls on a non-publication day of the target leg still resolves.
    union_idx = c.index.union(t.index).sort_values()
    t_ff = t.reindex(union_idx).ffill()
    aligned = pd.concat([c, t_ff.rename("target")], axis=1).dropna()
    spread_bps = ((aligned["corra"] - aligned["target"]) * 100.0).round(2)
    out = spread_bps.reset_index()
    out.columns = ["date", "value"]
    # Restrict to dates CORRA actually publishes (drop any ffill-only rows
    # where CORRA was unavailable).
    out = out[out["date"].isin(corra["date"])].reset_index(drop=True)

    meta = SeriesMeta(
        name="corra_overnight_spread_bps",
        source="Bank of Canada Valet API (derived)",
        source_url="https://www.bankofcanada.ca/valet/observations/AVG.INTWO/json",
        source_id="AVG.INTWO-minus-V39079 (in basis points)",
        units="basis points",
        frequency="daily",
        notes=(
            "Daily CORRA minus daily overnight rate target, in basis points. "
            "Inputs: AVG.INTWO (CORRA daily) and V39079 (overnight rate, daily). "
            "Overnight target forward-filled across non-publication days. "
            "Positive values = CORRA trades above target; near-zero = floor "
            "regime functioning. 20-day smoothing applied at chart layer, not here."
        ),
        transform="(corra_daily - overnight_rate_daily) * 100",
    )
    write_series(out, meta, DATA_PROCESSED)


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

    failed: list[str] = []

    logger.info("--- BoC Valet (daily) ---")
    run_boc_catalog_daily(failed)

    logger.info("--- FRED ---")
    run_fred_catalog(failed)

    logger.info("--- Yahoo Finance ---")
    run_yahoo_catalog(failed)

    logger.info("--- Indeed Hiring Lab ---")
    run_indeed_catalog(failed)

    logger.info("--- Derivations (Financial) ---")
    _safe("derive_goc_ust_spreads", derive_goc_ust_spreads, failed)
    _safe("derive_corra_overnight_spread", derive_corra_overnight_spread, failed)

    # Regenerate downstream site-data JSON so newly-landed daily series
    # (e.g. tsx_composite.csv from Yahoo, yield_2yr.csv from BoC Valet)
    # are immediately reflected in sections.json and panel_data/*.json.
    #
    # Root cause of the 2026-05-22 TSX TK incident: build_financial wrote
    # tsx_composite.csv but never called build_site_data / build_all_panel_data,
    # so sections.json + markets.json carried stale "available: false" / null
    # primary slots until the next full pipeline.build run. These two calls
    # close that gap: the daily financial run is now fully self-contained.
    logger.info("--- Site data bundle (financial refresh) ---")
    _safe("build_site_data", lambda: build_site_data(ROOT / "data"), failed)

    logger.info("--- Panel data bundle (financial refresh) ---")
    _safe("build_panel_data", lambda: build_all_panel_data(ROOT / "data"), failed)

    if failed:
        logger.error("Financial build completed with %d failure(s): %s",
                     len(failed), ", ".join(failed))
        return 1
    logger.info("Financial build completed successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
