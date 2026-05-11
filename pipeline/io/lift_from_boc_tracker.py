"""One-shot copy of boc-tracker CSVs into data/raw/, with .meta.json sidecars.

Context
-------
boc-tracker (`C:/Users/jayzh/Documents/boc-tracker/data/`) holds 104 flat
date/value CSVs produced by `boc-tracker/fetch.py`. Sibley Creek's existing
fetchers reproduce a subset of these from the same upstream sources; for
panels that need the additional series, lifting the CSVs directly avoids
re-implementing the fetchers and re-hitting WDS / Valet / FRED. boc-tracker
has no .meta.json sidecars, so this script also fabricates them from the
hard-coded provenance lookup below (ground truth was read out of
boc-tracker/fetch.py on 2026-05-11).

Failure policy
--------------
- Existing `data/raw/<name>.csv` files are NEVER overwritten.
- If a name has no provenance entry in PROVENANCE, we fall back to a
  best-guess inferred source from the slug prefix; frequency is inferred
  from the CSV's date deltas. The .meta.json `notes` field flags this so
  a fact-checker can correct it.

Run from the repo root with the venv active:

    .\\.venv\\Scripts\\python.exe -m pipeline.io.lift_from_boc_tracker
"""

from __future__ import annotations

import json
import logging
import shutil
import statistics
import sys
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Optional

import pandas as pd

logger = logging.getLogger("pipeline.io.lift_from_boc_tracker")

ROOT = Path(__file__).resolve().parents[2]
SIBLEY_RAW = ROOT / "data" / "raw"
BOC_TRACKER_DATA = Path("C:/Users/jayzh/Documents/boc-tracker/data")

LIFTED_AT = date(2026, 5, 11).isoformat()


# --------------------------------------------------------------------------- #
# Provenance catalog
# --------------------------------------------------------------------------- #
#
# Source of truth was boc-tracker/fetch.py STATSCAN_SERIES / BOC_VALET_SERIES /
# FRED_SERIES / BIS_CBPOL_SERIES dictionaries, plus the Alberta Economic
# Dashboard wcs fetcher and the Indeed Hiring Lab fetcher. Read from
# `C:/Users/jayzh/Documents/boc-tracker/fetch.py` on 2026-05-11.

STATCAN_TABLE_URL = "https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid={pid}"


@dataclass(frozen=True)
class Provenance:
    source: str
    source_id: str
    source_url: str
    units: str
    frequency: str
    notes: Optional[str] = None


def _statcan(pid: str, vector: int, units: str, frequency: str, notes: Optional[str] = None) -> Provenance:
    return Provenance(
        source="Statistics Canada Web Data Service",
        source_id=f"v{vector}",
        source_url=STATCAN_TABLE_URL.format(pid=pid),
        units=units,
        frequency=frequency,
        notes=notes,
    )


def _boc(series_key: str, units: str, frequency: str, notes: Optional[str] = None) -> Provenance:
    return Provenance(
        source="Bank of Canada Valet API",
        source_id=series_key,
        source_url=f"https://www.bankofcanada.ca/valet/observations/{series_key}/json",
        units=units,
        frequency=frequency,
        notes=notes,
    )


def _fred(series_id: str, units: str, frequency: str, notes: Optional[str] = None) -> Provenance:
    return Provenance(
        source="Federal Reserve Economic Data (FRED)",
        source_id=series_id,
        source_url=f"https://fred.stlouisfed.org/series/{series_id}",
        units=units,
        frequency=frequency,
        notes=notes,
    )


def _bis_cbpol(country: str, units: str, frequency: str, notes: Optional[str] = None) -> Provenance:
    return Provenance(
        source="Bank for International Settlements - CBPOL",
        source_id=f"WS_CBPOL:{country}",
        source_url="https://data.bis.org/static/bulk/WS_CBPOL_csv_flat.zip",
        units=units,
        frequency=frequency,
        notes=notes,
    )


def _alberta(table: str, type_label: str, units: str, frequency: str, notes: Optional[str] = None) -> Provenance:
    return Provenance(
        source="Government of Alberta - Economic Dashboard API",
        source_id=f"alberta-dashboard:{table}:{type_label}",
        source_url=f"https://api.economicdata.alberta.ca/data?table={table}",
        units=units,
        frequency=frequency,
        notes=notes,
    )


def _indeed(units: str, frequency: str, notes: Optional[str] = None) -> Provenance:
    return Provenance(
        source="Indeed Hiring Lab - Canada job postings",
        source_id="hiring-lab/data/CA/aggregate_job_postings_CA.csv",
        source_url="https://raw.githubusercontent.com/hiring-lab/data/master/CA/aggregate_job_postings_CA.csv",
        units=units,
        frequency=frequency,
        notes=notes,
    )


# StatCan PIDs grouped per fetch.py comments. Values: (pid, vector, units, frequency, note?).
PROVENANCE: dict[str, Provenance] = {
    # ---- Inflation ----
    "cpi_all_items": _statcan("1810000601", 41690914, "Index, 2002=100", "monthly", "All-items CPI, Canada, SA."),
    "cpi_all_items_nsa": _statcan("1810000401", 41690973, "Index, 2002=100", "monthly", "All-items CPI, Canada, NSA."),
    "cpi_services": _statcan("1810000401", 41691230, "Index, 2002=100", "monthly", "CPI Services, Canada, NSA."),
    "cpi_food": _statcan("1810000401", 41690974, "Index, 2002=100", "monthly", "CPI Food, Canada, NSA."),
    "cpi_energy": _statcan("1810000401", 41691239, "Index, 2002=100", "monthly", "CPI Energy, Canada, NSA."),
    "cpi_goods": _statcan("1810000401", 41691222, "Index, 2002=100", "monthly", "CPI Goods, Canada, NSA."),
    "cpi_shelter": _statcan("1810000401", 41691050, "Index, 2002=100", "monthly", "CPI Shelter, Canada, NSA."),
    "cpi_components": _statcan("1810000401", 0, "Index, 2002=100 (per-component)", "monthly",
        "Wide-format CSV: date x component for the 60-series CPI breadth basket. "
        "Per-component vector IDs in boc-tracker/data/cpi_breadth_mapping.json."),
    # BoC core CPI (Valet)
    "cpi_trim": _boc("CPI_TRIM", "%", "monthly", "CPI-trim, Y/Y %."),
    "cpi_median": _boc("CPI_MEDIAN", "%", "monthly", "CPI-median, Y/Y %."),
    "cpi_common": _boc("CPI_COMMON", "%", "monthly", "CPI-common, Y/Y %."),
    "cpix": _boc("ATOM_V41693242", "%", "monthly", "CPIX (excl. 8 volatile), Y/Y %."),
    "cpixfet": _boc("STATIC_CPIXFET", "%", "monthly", "CPIXFET (excl. food and energy), Y/Y %."),
    # ---- Inflation expectations ----
    "infl_exp_consumer_1y": _boc("CES_C1_SHORT_TERM", "%", "quarterly",
        "CSCE 1-year-ahead consumer inflation expectation, % (mean)."),
    "infl_exp_consumer_5y": _boc("CES_C1_LONG_TERM", "%", "quarterly",
        "CSCE 5-year-ahead consumer inflation expectation, % (mean)."),
    "infl_exp_above3": _boc("ABOVE3", "% of firms", "quarterly",
        "BOS: % of firms expecting inflation > 3% over next 2 years."),
    "bos_dist_below1": _boc("INDINF_BOSBELOW1_Q", "% of firms", "quarterly", "BOS: % expecting CPI < 1%."),
    "bos_dist_1to2": _boc("INDINF_BOS1TO2_Q", "% of firms", "quarterly", "BOS: % expecting CPI 1-2%."),
    "bos_dist_2to3": _boc("INDINF_BOS2TO3_Q", "% of firms", "quarterly",
        "BOS: % expecting CPI 2-3% (target-consistent bucket)."),
    "bos_dist_above3": _boc("INDINF_BOSOVER3_Q", "% of firms", "quarterly", "BOS: % expecting CPI > 3%."),
    # ---- GDP ----
    "gdp_monthly": _statcan("3610043401", 65201210, "C$ trillions, chained 2017", "monthly",
        "Monthly real GDP, all industries, chained 2017 dollars, SAAR. boc-tracker pre-scaled C$ millions to C$ trillions (x1e-6)."),
    "gdp_industry_goods": _statcan("3610043401", 65201211, "C$ trillions, chained 2017", "monthly",
        "Goods-producing industries; boc-tracker pre-scaled millions to trillions."),
    "gdp_industry_services": _statcan("3610043401", 65201212, "C$ trillions, chained 2017", "monthly",
        "Services-producing industries; boc-tracker pre-scaled millions to trillions."),
    "gdp_industry_manufacturing": _statcan("3610043401", 65201263, "C$ trillions, chained 2017", "monthly",
        "Manufacturing; boc-tracker pre-scaled millions to trillions."),
    "gdp_industry_mining_oil": _statcan("3610043401", 65201236, "C$ trillions, chained 2017", "monthly",
        "Mining, quarrying, and oil and gas extraction; boc-tracker pre-scaled millions to trillions."),
    "gdp_quarterly": _statcan("3610010401", 62305752, "C$ millions, chained 2017", "quarterly",
        "Quarterly real GDP, expenditure-based, chained 2017 dollars, SAAR."),
    "gdp_total_contribution": _statcan("3610010401", 79448580, "pp", "quarterly",
        "Total GDP at market prices: contribution to annualized Q/Q growth, percentage points."),
    "gdp_contrib_consumption": _statcan("3610010401", 79448555, "pp", "quarterly",
        "Household final consumption contribution to Q/Q SAAR growth."),
    "gdp_contrib_govt": _statcan("3610010401", 79448562, "pp", "quarterly",
        "Government final consumption contribution to Q/Q SAAR growth."),
    "gdp_contrib_investment": _statcan("3610010401", 79448563, "pp", "quarterly",
        "Gross fixed capital formation contribution to Q/Q SAAR growth."),
    "gdp_contrib_inventories": _statcan("3610010401", 79448572, "pp", "quarterly",
        "Change in inventories contribution to Q/Q SAAR growth."),
    "gdp_contrib_exports": _statcan("3610010401", 79448573, "pp", "quarterly",
        "Exports of goods and services contribution to Q/Q SAAR growth."),
    "gdp_contrib_imports": _statcan("3610010401", 79448576, "pp", "quarterly",
        "Imports contribution to Q/Q SAAR growth. boc-tracker stored with scale_factor=-1 so positive = imports fell (MPR/StatCan presentation convention)."),
    # ---- Labour ----
    "unemployment_rate": _statcan("1410028701", 2062815, "%", "monthly", "Unemployment rate, Canada 15+, SA."),
    "employment_rate": _statcan("1410028701", 2062817, "%", "monthly", "Employment rate, Canada 15+, SA."),
    "participation_rate": _statcan("1410028701", 2062816, "%", "monthly", "Participation rate, Canada 15+, SA."),
    "unemployment_level": _statcan("1410028701", 2062814, "Millions of persons", "monthly",
        "Unemployment level (thousands of persons in source); boc-tracker pre-scaled thousands to millions (x0.001)."),
    "job_vacancy_rate": _statcan("1410037101", 1212389365, "%", "monthly",
        "Job vacancy rate, Canada total, NSA. (No monthly SA series exists; smooth with 12M MA at chart layer.)"),
    "job_vacancy_level": _statcan("1410037101", 1212389364, "Millions of persons", "monthly",
        "Job vacancies count, Canada total, NSA; boc-tracker pre-scaled persons to millions (x1e-6)."),
    "unit_labour_cost": _statcan("3610020601", 1409159, "Index, SA", "quarterly",
        "Unit labour cost, business sector, Canada, quarterly SA."),
    "lfs_wages_all": _statcan("1410032002", 105812645, "CAD/hour", "monthly",
        "LFS average hourly wages, all employees 15+, Canada, SA."),
    "lfs_wages_permanent": _statcan("1410032002", 105812715, "CAD/hour", "monthly",
        "LFS average hourly wages, permanent employees, Canada, SA."),
    "seph_earnings": _statcan("1410022301", 79311153, "CAD/week", "monthly",
        "SEPH average weekly earnings, all employees, Canada, SA."),
    "lfs_micro": _boc("INDINF_LFSMICRO_M", "%", "monthly",
        "BoC LFS-Micro composition-adjusted wage growth, Y/Y %."),
    "youth_unemployment_rate": _statcan("1410028701", 2062842, "%", "monthly",
        "Unemployment rate, ages 15-24, SA."),
    "prime_age_unemployment_rate": _statcan("1410028701", 2062950, "%", "monthly",
        "Unemployment rate, ages 25-54, SA."),
    "lf_participation_prime": _statcan("1410028701", 2062951, "%", "monthly", "Participation rate, 25-54, SA."),
    "lf_employment_prime": _statcan("1410028701", 2062952, "%", "monthly",
        "Employment rate, 25-54, SA. Note: V2062952 previously returned HTTP 409 from WDS; may be empty / stale in source."),
    "lf_participation_youth": _statcan("1410028701", 2062843, "%", "monthly", "Participation rate, 15-24, SA."),
    "lf_employment_youth": _statcan("1410028701", 2062844, "%", "monthly", "Employment rate, 15-24, SA."),
    "capacity_util_total": _statcan("1610035901", 4331081, "%", "quarterly",
        "Total industrial capacity utilization, Canada, SA."),
    "capacity_util_mfg": _statcan("1610035901", 4331088, "%", "quarterly",
        "Manufacturing capacity utilization, Canada, SA."),
    "ei_regular_beneficiaries": _statcan("1410000501", 64549350, "Persons", "monthly",
        "EI regular benefits recipients, Canada, SA."),
    "indeed_postings_ca": _indeed("Index, Feb 1 2020 = 100", "daily",
        "Indeed Hiring Lab Canada total postings index, SA, daily. Used as a complementary read on JVWS, especially across the JVWS Apr-Sep 2020 COVID suspension."),
    "indeed_postings_ca_monthly": _indeed("Index, Feb 1 2020 = 100", "monthly",
        "Indeed Canada postings index, monthly mean of daily SA values (month-start convention)."),
    # ---- Housing ----
    "housing_starts": _statcan("3410015801", 52300157, "Units (thousands), SAAR", "monthly",
        "Housing starts, Canada total, SAAR (in thousands)."),
    "new_housing_price_index": _statcan("1810020501", 111955442, "Index, Dec 2016 = 100", "monthly",
        "New Housing Price Index, Canada total, NSA."),
    "residential_permits": _statcan("3410029201", 1675119646, "CAD thousands", "monthly",
        "Total residential building permits, value SA."),
    "units_under_construction": _statcan("3410015801", 52300170, "Units (thousands), SAAR", "monthly",
        "Units under construction, Canada total, SAAR. Tier 2 vector ID (inferred from magnitude; getSeriesInfoFromVector unavailable)."),
    "crea_mls_hpi": _boc("FVI_CREA_MLS_HPI_CANADA", "Index, 2019=100", "monthly",
        "CREA MLS HPI, all of Canada (BoC Financial Vulnerability Indicators bundle)."),
    "housing_affordability": _boc("INDINF_AFFORD_Q", "Index", "quarterly",
        "BoC housing affordability index, quarterly."),
    "mortgage_rate_5yr": _boc("V80691335", "%", "weekly",
        "5-year conventional mortgage rate."),
    "crea_resales": _boc("FVI_CREA_HOUSE_RESALE_INDEXED_CANADA", "Index", "monthly",
        "CREA residential resales, indexed; BoC FVI bundle."),
    "crea_snlr": _boc("FVI_CREA_HOUSE_SALES_TO_NEW_LISTINGS_CANADA", "%", "monthly",
        "CREA sales-to-new-listings ratio."),
    "crea_resales_toronto": _boc("FVI_HOUSE_RESALES_12M_TORONTO", "Resales (12M rolling)", "monthly",
        "Toronto 12M rolling resales; BoC FVI."),
    "crea_resales_vancouver": _boc("FVI_HOUSE_RESALES_12M_VANCOUVER", "Resales (12M rolling)", "monthly",
        "Vancouver 12M rolling resales; BoC FVI."),
    "crea_resales_calgary": _boc("FVI_HOUSE_RESALES_12M_CALGARY", "Resales (12M rolling)", "monthly",
        "Calgary 12M rolling resales; BoC FVI."),
    # ---- Trade ----
    "trade_exports_us": _statcan("1210011901", 87008898, "CAD millions, SA", "monthly",
        "Exports to the US, customs basis, SA."),
    "trade_imports_us": _statcan("1210011901", 87008782, "CAD millions, SA", "monthly",
        "Imports from the US, customs basis, SA."),
    "trade_balance_us": _statcan("1210011901", 87008985, "CAD millions, SA", "monthly",
        "Trade balance with the US, BOP basis, SA."),
    "trade_exports_total": _statcan("1210011901", 87008897, "CAD millions, SA", "monthly",
        "Exports to all countries, customs basis, SA."),
    "trade_imports_total": _statcan("1210011901", 87008781, "CAD millions, SA", "monthly",
        "Imports from all countries, customs basis, SA."),
    "trade_balance_total": _statcan("1210011901", 87008984, "CAD millions, SA", "monthly",
        "Trade balance, all countries, BOP basis, SA."),
    # ---- Population components ----
    "pop_immigrants": _statcan("1710004001", 29850342, "Persons", "quarterly",
        "Immigrants, Canada total."),
    "pop_emigrants": _statcan("1710004001", 29850343, "Persons", "quarterly",
        "Emigrants, Canada total."),
    "pop_net_emigration": _statcan("1710004001", 1566834788, "Persons", "quarterly",
        "Net emigration, Canada total."),
    "pop_net_npr": _statcan("1710004001", 29850346, "Persons", "quarterly",
        "Net non-permanent residents, Canada total."),
    "pop_npr_inflows": _statcan("1710004001", 1566834758, "Persons", "quarterly",
        "Non-permanent resident inflows, Canada total."),
    # ---- Yields and rates (BoC Valet) ----
    "yield_2yr": _boc("BD.CDN.2YR.DQ.YLD", "%", "daily", "2-yr GoC benchmark bond yield."),
    "yield_5yr": _boc("BD.CDN.5YR.DQ.YLD", "%", "daily", "5-yr GoC benchmark bond yield."),
    "yield_10yr": _boc("BD.CDN.10YR.DQ.YLD", "%", "daily", "10-yr GoC benchmark bond yield."),
    "yield_30yr": _boc("BD.CDN.LONG.DQ.YLD", "%", "daily", "30-yr GoC benchmark bond yield."),
    "corra_daily": _boc("AVG.INTWO", "%", "daily", "CORRA - Canadian Overnight Repo Rate Average."),
    "overnight_rate": _boc("STATIC_ATABLE_V39079", "%", "monthly",
        "BoC overnight rate target, monthly (long history)."),
    "overnight_rate_daily": _boc("V39079", "%", "daily",
        "BoC overnight rate target, daily (post-2009-04-21)."),
    # ---- BoC balance sheet ----
    "boc_total_assets": _boc("V36610", "CAD billions", "weekly",
        "Total assets; boc-tracker pre-scaled millions to billions (x0.001)."),
    "boc_goc_bonds": _boc("V36613", "CAD billions", "weekly",
        "GoC bonds held outright; pre-scaled to billions."),
    "boc_settlement_balances": _boc("V36636", "CAD billions", "weekly",
        "Settlement balances (Payments Canada member deposits); pre-scaled to billions."),
    "boc_tbills": _boc("V36612", "CAD billions", "weekly",
        "Treasury bills (asset side); pre-scaled to billions."),
    "boc_repos": _boc("V44201362", "CAD billions", "weekly",
        "Securities purchased under resale agreements (BoC lending cash); pre-scaled to billions."),
    "boc_advances": _boc("V36634", "CAD billions", "weekly",
        "Advances (Standing Liquidity Facility, etc.); pre-scaled to billions."),
    "boc_total_liabilities": _boc("V36624", "CAD billions", "weekly",
        "Total liabilities and equity; pre-scaled to billions."),
    "boc_banknotes": _boc("V36625", "CAD billions", "weekly",
        "Notes in circulation; pre-scaled to billions."),
    "boc_goc_deposits": _boc("V36628", "CAD billions", "weekly",
        "Government of Canada deposits; pre-scaled to billions."),
    "boc_reverse_repos": _boc("V1203435186", "CAD billions", "weekly",
        "Securities sold under repurchase agreements (BoC borrowing cash); QE-era only, starts 2020-07-29; pre-scaled to billions."),
    # ---- FRED ----
    "us_2yr": _fred("DGS2", "%", "daily", "2-yr US Treasury constant maturity."),
    "usdcad": _fred("DEXCAUS", "CAD per USD", "daily", "USD/CAD exchange rate."),
    "wti": _fred("DCOILWTICO", "USD/barrel", "daily", "WTI crude oil."),
    "brent": _fred("DCOILBRENTEU", "USD/barrel", "daily", "Brent crude oil."),
    "ecb_rate": _fred("ECBDFR", "%", "weekly", "ECB deposit facility rate."),
    "fed_funds": _fred("FEDFUNDS+DFEDTARU+DFEDTARL", "%", "daily",
        "Fed funds target midpoint: FEDFUNDS monthly pre-2008, (DFEDTARU+DFEDTARL)/2 daily post-2008-12-16."),
    # ---- BIS CBPOL ----
    "boe_rate": _bis_cbpol("GB", "%", "daily", "Bank of England Bank Rate."),
    "rba_rate": _bis_cbpol("AU", "%", "daily", "RBA cash rate target."),
    # ---- Alberta Economic Dashboard ----
    "wcs": _alberta("OilPrices", "WCS", "USD/barrel", "monthly",
        "Western Canada Select crude price."),
}


# --------------------------------------------------------------------------- #
# Frequency inference
# --------------------------------------------------------------------------- #

def _infer_frequency(csv_path: Path) -> str:
    """Infer cadence from the median consecutive-date delta in the CSV.

    Buckets:
        delta <= 1.5 days   -> "daily"
        2..10 days          -> "weekly"
        11..45 days         -> "monthly"
        46..180 days        -> "quarterly"
        > 180 days          -> "annual"
        unknown / empty     -> "irregular"
    """
    try:
        df = pd.read_csv(csv_path, parse_dates=[0])
    except Exception:
        return "irregular"
    if df.empty or len(df) < 2:
        return "irregular"
    dates = pd.to_datetime(df.iloc[:, 0], errors="coerce").dropna().sort_values()
    if len(dates) < 2:
        return "irregular"
    deltas = (dates.diff().dropna().dt.days).tolist()
    if not deltas:
        return "irregular"
    median = statistics.median(deltas)
    if median <= 1.5:
        return "daily"
    if median <= 10:
        return "weekly"
    if median <= 45:
        return "monthly"
    if median <= 180:
        return "quarterly"
    return "annual"


def _slug_inferred_provenance(slug: str, frequency: str) -> Provenance:
    """Fall back: best-guess source from the slug prefix.

    Flagged in the meta.json `notes` so a fact-checker can correct it.
    """
    if slug.startswith("cpi_"):
        guess_source = "Statistics Canada (inferred from slug; not in PROVENANCE catalog)"
        guess_units = "Index, 2002=100"
    elif slug.startswith("boc_") or slug.startswith("yield_") or slug.startswith("corra") or slug.startswith("overnight"):
        guess_source = "Bank of Canada (inferred from slug; not in PROVENANCE catalog)"
        guess_units = "%"
    elif slug.startswith("crea_"):
        guess_source = "CREA via BoC FVI (inferred from slug; not in PROVENANCE catalog)"
        guess_units = "Index / count"
    elif slug.startswith("gdp_"):
        guess_source = "Statistics Canada GDP (inferred from slug; not in PROVENANCE catalog)"
        guess_units = "Chained 2017 dollars or pp"
    elif slug.startswith("trade_"):
        guess_source = "Statistics Canada Merchandise Trade (inferred from slug; not in PROVENANCE catalog)"
        guess_units = "CAD millions, SA"
    elif slug.startswith("pop_"):
        guess_source = "Statistics Canada Population components (inferred from slug; not in PROVENANCE catalog)"
        guess_units = "Persons"
    elif slug.startswith("bos_"):
        guess_source = "Bank of Canada Business Outlook Survey (inferred from slug)"
        guess_units = "% of firms"
    elif slug.startswith("infl_exp_"):
        guess_source = "Bank of Canada inflation expectations (inferred from slug)"
        guess_units = "%"
    elif slug.startswith("lfs_") or slug in {"unemployment_rate", "employment_rate", "participation_rate"}:
        guess_source = "Statistics Canada Labour Force Survey (inferred from slug)"
        guess_units = "% or hours / dollars"
    else:
        guess_source = "Unknown - inferred from slug (not in PROVENANCE catalog)"
        guess_units = "Unknown"
    return Provenance(
        source=guess_source,
        source_id=slug,
        source_url="",  # null sentinel: ASCII empty string
        units=guess_units,
        frequency=frequency,
        notes=(
            "Provenance inferred from slug; original boc-tracker fetch.py entry "
            "was NOT found in PROVENANCE catalog. Fact-check required."
        ),
    )


# --------------------------------------------------------------------------- #
# Per-series lift
# --------------------------------------------------------------------------- #

def _build_meta(slug: str, csv_path: Path) -> dict:
    """Construct the .meta.json payload for a single boc-tracker CSV."""
    df = pd.read_csv(csv_path, parse_dates=[0])
    ref_start: Optional[str] = None
    ref_end: Optional[str] = None
    if not df.empty:
        dates = pd.to_datetime(df.iloc[:, 0], errors="coerce").dropna()
        if not dates.empty:
            ref_start = dates.min().date().isoformat()
            ref_end = dates.max().date().isoformat()

    inferred_freq = _infer_frequency(csv_path)

    prov = PROVENANCE.get(slug)
    if prov is None:
        prov = _slug_inferred_provenance(slug, inferred_freq)

    fetched_at = datetime.now(timezone.utc).isoformat()
    notes = prov.notes
    if prov.frequency != inferred_freq:
        suffix = f" Inferred cadence from CSV: {inferred_freq}."
        notes = (notes or "") + suffix

    meta = {
        "name": slug,
        "source": prov.source,
        "source_url": prov.source_url or None,
        "source_id": prov.source_id,
        "units": prov.units,
        "frequency": prov.frequency,
        "fetched_at": fetched_at,
        "release_date": None,
        "reference_period_start": ref_start,
        "reference_period_end": ref_end,
        "notes": notes,
        "transform": None,
        "schema_version": 1,
        "lifted_from": "boc-tracker",
        "lifted_at": LIFTED_AT,
    }
    return meta


def lift_all(
    source_dir: Path = BOC_TRACKER_DATA,
    target_dir: Path = SIBLEY_RAW,
    overwrite: bool = False,
) -> tuple[list[str], list[str], list[str]]:
    """Copy CSVs from boc-tracker to data/raw/.

    Returns: (copied, skipped_collision, missing_provenance)
        copied:              slugs newly copied + meta-written
        skipped_collision:   slugs that already exist in target_dir (overwrite=False)
        missing_provenance:  slugs that had to fall back to inferred provenance
    """
    target_dir.mkdir(parents=True, exist_ok=True)
    copied: list[str] = []
    skipped: list[str] = []
    missing: list[str] = []

    for csv_path in sorted(source_dir.glob("*.csv")):
        slug = csv_path.stem
        out_csv = target_dir / f"{slug}.csv"
        out_meta = target_dir / f"{slug}.meta.json"
        if out_csv.exists() and not overwrite:
            skipped.append(slug)
            continue
        shutil.copy2(csv_path, out_csv)
        meta = _build_meta(slug, csv_path)
        if slug not in PROVENANCE:
            missing.append(slug)
        out_meta.write_text(json.dumps(meta, indent=2, sort_keys=False), encoding="utf-8")
        copied.append(slug)

    return copied, skipped, missing


def main() -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    if not BOC_TRACKER_DATA.exists():
        logger.error("boc-tracker data directory not found: %s", BOC_TRACKER_DATA)
        return 1
    copied, skipped, missing = lift_all()
    logger.info("Lifted %d CSV(s); skipped %d collision(s); %d missing provenance.",
                len(copied), len(skipped), len(missing))
    if missing:
        logger.info("Slugs with inferred provenance: %s", ", ".join(missing))
    if skipped:
        logger.info("Collisions (kept Sibley copy): %s", ", ".join(skipped))
    return 0


if __name__ == "__main__":
    sys.exit(main())
