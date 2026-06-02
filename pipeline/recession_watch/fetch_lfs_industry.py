"""Fetch LFS employment by 16 industry sectors (Table 14-10-0355-01).

This table is current (not archived), so we use the bulk ZIP approach:
the ZIP is already on disk at claude-ref/research/recession_watch/14100355_raw.zip
from the recon phase. This module reads it and writes a tidy CSV to
data/raw/recession_watch/lfs_by_industry_sa.csv.

The 16 sector names (mapped from the CSV):
  Agriculture [111-112, 1100, 1151-1152]
  Forestry, fishing, mining, quarrying, oil and gas [21, 113-114, 1153, 2100]
  Utilities [22]
  Construction [23]
  Manufacturing [31-33]
  Wholesale and retail trade [41, 44-45]      <- combined; we split to Wholesale + Retail below
  Transportation and warehousing [48-49]
  Finance, insurance, real estate, rental and leasing [52-53]
  Professional, scientific and technical services [54]
  Business, building and other support services [55-56]
  Educational services [61]
  Health care and social assistance [62]
  Information, culture and recreation [51, 71]
  Accommodation and food services [72]
  Other services (except public administration) [81]
  Public administration [91]

NOTE: The table provides both "Wholesale and retail trade" combined AND
separate "Wholesale trade [41]" and "Retail trade [44-45]" from a later
member ID. We use the 16 that exclude aggregates (goods-producing sector,
services-producing sector, total) to give a consistent breadth denominator.

The source ZIP is in claude-ref/ (the recon directory); we also check
the pipeline's canonical output location first.
"""

from __future__ import annotations

import csv
import io
import json
import logging
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[2]
RW_DIR = ROOT / "data" / "raw" / "recession_watch"
RW_DIR.mkdir(parents=True, exist_ok=True)

# Source ZIP locations (checked in order)
ZIP_LOCATIONS = [
    RW_DIR / "14100355_raw.zip",
    ROOT / "claude-ref" / "research" / "recession_watch" / "14100355_raw.zip",
]

OUT_CSV = RW_DIR / "lfs_by_industry_sa.csv"
OUT_META = RW_DIR / "lfs_by_industry_sa.meta.json"

# The 16 named sector NAICS codes for breadth (exclude Total, Goods sector,
# Services sector, Wholesale+Retail combined — we keep the separate W+R if available,
# or the combined if not).
SECTOR_16_NAMES = [
    "Agriculture [111-112, 1100, 1151-1152]",
    "Forestry, fishing, mining, quarrying, oil and gas [21, 113-114, 1153, 2100]",
    "Utilities [22]",
    "Construction [23]",
    "Manufacturing [31-33]",
    "Transportation and warehousing [48-49]",
    "Finance, insurance, real estate, rental and leasing [52-53]",
    "Professional, scientific and technical services [54]",
    "Business, building and other support services [55-56]",
    "Educational services [61]",
    "Health care and social assistance [62]",
    "Information, culture and recreation [51, 71]",
    "Accommodation and food services [72]",
    "Other services (except public administration) [81]",
    "Public administration [91]",
]

# Include Wholesale and Retail trade — prefer split if available, else combined
TRADE_COMBINED = "Wholesale and retail trade [41, 44-45]"
TRADE_WHOLESALE = "Wholesale trade [41]"
TRADE_RETAIL = "Retail trade [44-45]"


def _find_zip() -> Path:
    """Locate the 14100355 ZIP file."""
    for p in ZIP_LOCATIONS:
        if p.exists():
            return p
    raise FileNotFoundError(
        f"14100355_raw.zip not found in: {[str(p) for p in ZIP_LOCATIONS]}. "
        "Place the ZIP from the recon in data/raw/recession_watch/ or "
        "claude-ref/research/recession_watch/."
    )


def _parse_lfs_zip(zip_path: Path) -> pd.DataFrame:
    """Parse 14100355 bulk ZIP into a tidy DataFrame.

    Returns: date, sector_name, value (thousands, SA), vector
    Filtered to: Canada, Estimate, Seasonally adjusted.
    """
    rows = []
    with zipfile.ZipFile(zip_path) as z:
        # Find the main CSV (not metadata)
        csv_names = [n for n in z.namelist() if n.endswith(".csv") and "MetaData" not in n]
        if not csv_names:
            raise ValueError(f"No data CSV found in {zip_path}")
        csv_name = csv_names[0]

        with z.open(csv_name) as f:
            reader = csv.DictReader(io.TextIOWrapper(f, encoding="utf-8-sig"))
            for row in reader:
                if row.get("GEO", "").strip() != "Canada":
                    continue
                if row.get("Statistics", "").strip() != "Estimate":
                    continue
                if row.get("Data type", "").strip() != "Seasonally adjusted":
                    continue

                ref = row.get("REF_DATE", "").strip()
                val_str = row.get("VALUE", "").strip()
                if not ref or not val_str:
                    continue
                try:
                    dt = pd.Timestamp(ref + "-01")
                    value = float(val_str)
                except (ValueError, Exception):
                    continue

                sector = row.get("North American Industry Classification System (NAICS)", "").strip()
                vector = row.get("VECTOR", "").strip()
                rows.append({
                    "date": dt,
                    "sector_name": sector,
                    "value": value,
                    "vector": vector,
                })

    if not rows:
        raise ValueError("No SA Estimate rows found in 14100355")
    df = pd.DataFrame(rows)
    df["date"] = pd.to_datetime(df["date"])
    return df.sort_values(["date", "sector_name"]).reset_index(drop=True)


def _select_16_sectors(df: pd.DataFrame) -> pd.DataFrame:
    """Filter to the 16 breadth sectors plus handle the trade split."""
    available = set(df["sector_name"].unique())

    # Determine trade sectors to include
    if TRADE_WHOLESALE in available and TRADE_RETAIL in available:
        trade_include = [TRADE_WHOLESALE, TRADE_RETAIL]
        logger.info("Using split Wholesale + Retail trade (2 sectors)")
    elif TRADE_COMBINED in available:
        trade_include = [TRADE_COMBINED]
        logger.info("Using combined Wholesale+Retail trade (1 sector)")
    else:
        trade_include = []
        logger.warning("No trade sectors found in LFS data")

    target = SECTOR_16_NAMES + trade_include
    df_16 = df[df["sector_name"].isin(target)].copy()

    missing = set(target) - set(df_16["sector_name"].unique())
    if missing:
        logger.warning("Missing LFS sectors: %s", missing)

    logger.info("LFS sectors selected: %d", df_16["sector_name"].nunique())
    return df_16


def fetch_lfs_by_industry(force: bool = False) -> Path:
    """Extract and cache LFS employment by 16 sectors.

    Returns path to the written CSV.
    """
    if OUT_CSV.exists() and OUT_META.exists() and not force:
        logger.info("Cache hit: LFS by industry -> %s", OUT_CSV)
        return OUT_CSV

    zip_path = _find_zip()
    logger.info("Parsing 14100355 from %s ...", zip_path)

    df_all = _parse_lfs_zip(zip_path)
    df_16 = _select_16_sectors(df_all)

    df_16.to_csv(OUT_CSV, index=False)

    meta = {
        "source": "Statistics Canada, Table 14-10-0355-01",
        "source_url": "https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1410035501",
        "table_id": "14100355",
        "description": "LFS employment by 16 SA industry sectors, Canada, monthly",
        "frequency": "monthly",
        "reference_period_start": str(df_16["date"].min().date()),
        "reference_period_end": str(df_16["date"].max().date()),
        "n_sectors": df_16["sector_name"].nunique(),
        "sectors": sorted(df_16["sector_name"].unique().tolist()),
        "units": "Persons in thousands (SA)",
        "source_zip": str(zip_path),
        "processed_at": datetime.now(timezone.utc).isoformat(),
    }
    OUT_META.write_text(json.dumps(meta, indent=2))
    logger.info("LFS by industry: %d sectors, %s to %s -> %s",
                df_16["sector_name"].nunique(),
                df_16["date"].min().date(),
                df_16["date"].max().date(),
                OUT_CSV)
    return OUT_CSV


def load_lfs_sector_pivot() -> pd.DataFrame:
    """Load LFS sectors as a wide DataFrame (date x sector_name).

    Runs fetch_lfs_by_industry() if not cached.
    """
    fetch_lfs_by_industry()
    df = pd.read_csv(OUT_CSV, parse_dates=["date"])
    pivot = (
        df.groupby(["date", "sector_name"])["value"]
        .mean()
        .unstack("sector_name")
    )
    return pivot


if __name__ == "__main__":
    import warnings
    warnings.filterwarnings("ignore")
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    p = fetch_lfs_by_industry(force=True)
    print(f"Written: {p}")
    pivot = load_lfs_sector_pivot()
    print(f"Pivot shape: {pivot.shape}")
    print(f"Date range: {pivot.index.min().date()} to {pivot.index.max().date()}")
    print(f"Sectors: {list(pivot.columns)}")
