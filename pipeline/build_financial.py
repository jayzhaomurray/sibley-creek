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

from pipeline.catalog import BOC_VALET_SERIES, FRED_SERIES, YAHOO_SERIES
from pipeline.catalog.boc_series import BocSpec
from pipeline.catalog.fred_series import FredSpec
from pipeline.catalog.yahoo_series import YahooSpec
from pipeline.fetch import boc, fred, yahoo
from pipeline.io import SeriesMeta, write_series
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
    result = yahoo.fetch_daily_close(spec.symbol, range_="max")
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
    write_series(df, meta, DATA_RAW)


def run_yahoo_catalog(failed: list[str]) -> None:
    for name, spec in YAHOO_SERIES.items():
        _safe(f"yahoo:{name}", lambda s=spec: _yahoo_fetch_one(s), failed)


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

    logger.info("--- Derivations (Financial) ---")
    _safe("derive_goc_ust_spreads", derive_goc_ust_spreads, failed)

    if failed:
        logger.error("Financial build completed with %d failure(s): %s",
                     len(failed), ", ".join(failed))
        return 1
    logger.info("Financial build completed successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
