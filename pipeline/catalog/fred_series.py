"""FRED series catalog.

Per dashboard_purpose section 4.6, the v1 basics-layer Financial section uses
FRED for US comparators only, with explicit Canadian-spread blind-spot caveats:
    - DGS10:        US 10y Treasury (canon 4.6 element 2 -- GoC-UST 10y spread)
    - VIXCLS:       VIX, US equity vol (weekly cross-asset synthesis)
    - DTWEXBGS:     Broad trade-weighted USD index (weekly DXY-vs-risk read)
    - BAMLC0A0CM:   ICE BofA US IG OAS (canon 4.6 element 3 -- IG risk-appetite proxy)
    - BAMLH0A0HYM2: ICE BofA US HY OAS (canon 4.6 element 3 -- HY risk-appetite proxy)
    - DGS2:         US 2y Treasury (canon 4.6 element 2 -- GoC-UST 2y spread)
    - DCOILWTICO:   WTI crude (Section 4.6 element 4, daily)
    - DCOILBRENTEU: Brent crude (Section 4.6 element 4, daily)
    - Fed funds target: composite (FEDFUNDS pre-2008; DFEDTARU/L midpoint post)

LBMA gold (GOLDAMGBD228NLBM, GOLDPMGBD228NLBM) was discontinued by ICE Benchmark
Administration on FRED. We use Yahoo `GC=F` (COMEX gold futures front month) as
the daily-cadence gold input -- registered in yahoo_series.py.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FredSpec:
    name: str
    series_id: str
    start_date: str
    units: str
    frequency: str
    section: str
    cadence: str
    notes: str = ""


FRED_SERIES: dict[str, FredSpec] = {
    "us_2yr":   FredSpec("us_2yr",   "DGS2",  "1990-01-01", "%", "daily", "financial", "daily",
                          notes="US 2-yr Treasury constant maturity; daily, NY close."),
    "us_10yr":  FredSpec("us_10yr",  "DGS10", "1990-01-01", "%", "daily", "financial", "daily",
                          notes="US 10-yr Treasury constant maturity; canonical comparator for GoC-UST 10y spread."),
    "vix":      FredSpec("vix",      "VIXCLS","1990-01-01", "Index", "daily", "financial", "daily",
                          notes="CBOE Volatility Index; daily close. US-only -- no liquid Canadian equivalent."),
    "dxy_broad": FredSpec("dxy_broad","DTWEXBGS","2006-01-01", "Index, Jan 2006=100", "daily", "financial", "daily",
                          notes="Federal Reserve broad trade-weighted dollar index; preferred over ICE DXY for Canada-relevant FX read."),
    "us_ig_oas":  FredSpec("us_ig_oas",  "BAMLC0A0CM", "1996-12-01", "bp", "daily", "financial", "daily",
                            notes="ICE BofA US Corporate Index OAS. Canadian IG OAS blind spot (no free source); use as global risk-appetite proxy per canon 4.6 element 3."),
    "us_hy_oas":  FredSpec("us_hy_oas",  "BAMLH0A0HYM2", "1996-12-01", "bp", "daily", "financial", "daily",
                            notes="ICE BofA US High Yield Index OAS."),
    # WTI and Brent migrated to Yahoo (CL=F / BZ=F) on 2026-05-11. FRED's
    # DCOILWTICO and DCOILBRENTEU publish weekly with a ~7-day lag, which
    # left the Markets section showing oil prints 5-7 days stale relative
    # to USDCAD / GoC daily yields. Yahoo futures close daily with no lag.
    # See pipeline.catalog.yahoo_series for the replacement specs.
    "ecb_rate": FredSpec("ecb_rate", "ECBDFR", "1999-01-01", "%", "daily", "policy", "daily",
                          notes="ECB deposit facility rate; daily."),
    # Fed funds target is composite — handled by pipeline.fetch.fred.fetch_fed_funds_target.
    # Registered here as a sentinel; the orchestrator dispatches the composite.
    "fed_funds": FredSpec("fed_funds", "__COMPOSITE_FED_FUNDS_TARGET__", "1990-01-01", "%", "daily", "policy", "daily",
                          notes="Composite: FEDFUNDS monthly pre-2008 + DFEDTARU/DFEDTARL midpoint post-2008."),
}
