"""GDP back-history chain: 36100390 -> 36100398 -> 36100434.

Produces two outputs:
  1. `gdp_level_chained`: monthly SA GDP level index (1981-01 to present),
     normalised to 1.0 at a reference date. Used for depth + peak detection.
  2. `gdp_breadth_comparator`: monthly count of "coarse sectors contracting
     since peak" across a COMMON bucket set that exists in ALL three tables
     back to 1981. This is the comparator-grade breadth — comparable across
     all four recessions.

Methodology
-----------
Splicing is done on growth rates, not levels, to avoid base-year mismatch
artifacts. At each vintage boundary:

  boundary_month: last month present in the older vintage
  overlap_months: months present in BOTH older and newer vintage

For each common-sector s, we compute the older-to-newer calibration ratio:
  ratio_s = median(newer_level_s / older_level_s) over the overlap period

Then the older vintage is rescaled: older_rescaled_s = older_s * ratio_s
The two rescaled series are concatenated on growth rates (the level-shift
cancels by construction in breadth calculations).

For depth we use the ALL-INDUSTRIES aggregate (single series) where the ratio
is computed on the total and rescaled accordingly.

Common sector mapping
---------------------
The coarse-sector grid is derived from NAICS codes present in all three
tables (36100390 shares most NAICS codes with 36100398/36100434 at the
2-digit level). We use ~13-20 top-level NAICS sectors that are present as
distinct named industries in all three tables.

The exact common set is computed dynamically from the intersection of NAICS
codes, filtered to sectors with parent==None (top-level) or parent=="All
industries" to avoid double-counting.
"""

from __future__ import annotations

import json
import logging
import zipfile
import io
import csv
import re
from pathlib import Path
from typing import NamedTuple

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "data" / "raw"
RW_DIR = RAW_DIR / "recession_watch"

# Current table ZIP (already on disk from recon; check both locations)
_GDP_CURRENT_ZIP_LOCATIONS = [
    RW_DIR / "36100434_raw.zip",
    ROOT / "claude-ref" / "research" / "recession_watch" / "36100434_raw.zip",
]
GDP_CURRENT_CSV = "36100434.csv"


def _find_current_gdp_zip() -> Path:
    """Find the 36100434 ZIP from either pipeline cache or recon directory."""
    for p in _GDP_CURRENT_ZIP_LOCATIONS:
        if p.exists():
            return p
    raise FileNotFoundError(
        f"36100434 ZIP not found. Checked: {[str(p) for p in _GDP_CURRENT_ZIP_LOCATIONS]}. "
        "Place the ZIP in data/raw/recession_watch/."
    )

# Archived tables (fetched by fetch_archived.py)
T390_CSV = RW_DIR / "36100390_sa.csv"
T398_CSV = RW_DIR / "36100398_sa.csv"

# NAICS codes for the top-level sectors we'll use as coarse common buckets.
# These appear in all three tables as DIRECT children of "All industries"
# or as the first level below it. We exclude cross-cutting T-aggregates
# (T001-T018) which are present in 0398 and 0434 but not 0390.
# These 13 codes are the defensible common grid.
COMMON_NAICS_SECTORS = [
    "11",    # Agriculture, forestry, fishing and hunting
    "21",    # Mining and oil and gas extraction
    "22",    # Utilities
    "23",    # Construction
    "31-33", # Manufacturing (note: 36100390 uses "31-33" or "33"; check)
    "41",    # Wholesale trade
    "44-45", # Retail trade
    "48-49", # Transportation and warehousing
    "51",    # Information and cultural industries
    "52",    # Finance and insurance
    "53",    # Real estate and rental and leasing
    "54",    # Professional, scientific and technical services
    "55",    # Management of companies and enterprises
    "56",    # Administrative and support, waste management
    "61",    # Educational services
    "62",    # Health care and social assistance
    "71",    # Arts, entertainment and recreation
    "72",    # Accommodation and food services
    "81",    # Other services (except public administration)
    "91",    # Public administration
]

# Normalised aliases: some tables use different bracket formats
NAICS_ALIASES: dict[str, list[str]] = {
    "31-33": ["31-33", "31", "32", "33"],
    "44-45": ["44-45", "44", "45"],
    "48-49": ["48-49", "48", "49"],
}


class ChainResult(NamedTuple):
    """Output of build_chain()."""
    # Monthly GDP level index (all industries, normalised)
    gdp_level: pd.Series          # index=DatetimeIndex, name="gdp_level"
    # Per-sector monthly levels for breadth computation
    # columns = normalized NAICS codes from COMMON_NAICS_SECTORS
    sector_levels: pd.DataFrame   # index=DatetimeIndex
    # Start date of the chain
    start_date: pd.Timestamp
    # Seam dates where vintages were joined
    seam_dates: list[str]
    # Calibration ratios used at each seam
    calibration_ratios: dict[str, dict[str, float]]


def _load_current_gdp_zip() -> pd.DataFrame:
    """Load 36100434 from the on-disk ZIP.

    Returns DataFrame with columns: date, naics_code, industry_name, value.
    Filtered to Canada SA at SAAR, chained 2017$.
    """
    zip_path = _find_current_gdp_zip()
    rows = []
    with zipfile.ZipFile(zip_path) as z:
        with z.open(GDP_CURRENT_CSV) as f:
            reader = csv.DictReader(io.TextIOWrapper(f, encoding="utf-8-sig"))
            for row in reader:
                if row.get("GEO", "").strip() != "Canada":
                    continue
                if row.get("Seasonal adjustment", "").strip() != "Seasonally adjusted at annual rates":
                    continue
                if row.get("Prices", "").strip() != "Chained (2017) dollars":
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
                naics_raw = row.get("North American Industry Classification System (NAICS)", "").strip()
                match = re.search(r"\[([^\]]+)\]$", naics_raw)
                naics_code = match.group(1) if match else naics_raw
                rows.append({
                    "date": dt,
                    "naics_code": naics_code,
                    "industry_name": naics_raw,
                    "value": value,
                })
    if not rows:
        raise ValueError("No rows loaded from 36100434 ZIP")
    df = pd.DataFrame(rows)
    df["date"] = pd.to_datetime(df["date"])
    return df.sort_values(["date", "naics_code"]).reset_index(drop=True)


def _load_archived_table(path: Path) -> pd.DataFrame:
    """Load an archived table CSV from data/raw/recession_watch/."""
    if not path.exists():
        raise FileNotFoundError(
            f"Archived table not found: {path}. Run fetch_archived.py first."
        )
    df = pd.read_csv(path, parse_dates=["date"])
    df["date"] = pd.to_datetime(df["date"])
    return df


def _normalise_naics(code: str) -> str | None:
    """Normalise a raw NAICS code to our standard form.

    Returns the canonical code if it matches one of the COMMON_NAICS_SECTORS,
    or None if not in the common set.
    """
    code = code.strip()
    if code in COMMON_NAICS_SECTORS:
        return code
    for canonical, aliases in NAICS_ALIASES.items():
        if code in aliases:
            return canonical
    return None


def _extract_sector_pivot(df: pd.DataFrame, common_codes: set[str]) -> pd.DataFrame:
    """Pivot a long-format GDP DataFrame to wide format with common NAICS sectors.

    Returns DataFrame indexed by date, columns = canonical NAICS codes.
    Rows are monthly. Missing industry/months are NaN.
    """
    # Normalise naics_code to canonical form
    df = df.copy()
    df["canonical"] = df["naics_code"].apply(_normalise_naics)
    df = df[df["canonical"].notna() & df["canonical"].isin(common_codes)]

    if df.empty:
        raise ValueError("No rows matching common NAICS sectors found in DataFrame")

    pivot = (
        df.groupby(["date", "canonical"])["value"]
        .mean()  # mean() handles rare duplicates gracefully
        .unstack("canonical")
    )
    return pivot


def _extract_total_level(df: pd.DataFrame) -> pd.Series:
    """Extract the all-industries aggregate level from a GDP DataFrame.

    In 36100434/36100398: naics_code = 'T001', industry_name = 'All industries [T001]'.
    In 36100390: naics_code = 'All industries', industry_name = 'All industries' (no bracket).
    """
    # Priority order: T001 code (434/398) > exact name match (390)
    # Avoid NAICS code "11" (Agriculture) which would be a false match.
    total_434 = df[df["naics_code"] == "T001"].copy()
    if not total_434.empty:
        total_434 = total_434.drop_duplicates("date", keep="first")
        return total_434.set_index("date")["value"].sort_index()

    # Fallback for 36100390: naics_code is the full name "All industries"
    total_390 = df[df["naics_code"] == "All industries"].copy()
    if not total_390.empty:
        total_390 = total_390.drop_duplicates("date", keep="first")
        return total_390.set_index("date")["value"].sort_index()

    # Final fallback: search by industry_name prefix
    total_name = df[df["industry_name"].str.match(r"^All industries(\s*\[|$)")].copy()
    if not total_name.empty:
        total_name = total_name.drop_duplicates("date", keep="first")
        return total_name.set_index("date")["value"].sort_index()

    raise ValueError(
        "Cannot find 'All industries' aggregate in GDP DataFrame. "
        f"Available naics_codes (first 20): {sorted(df['naics_code'].unique()[:20])}"
    )


def _compute_splice_ratio(
    older_series: pd.Series,
    newer_series: pd.Series,
    overlap_start: pd.Timestamp,
    overlap_end: pd.Timestamp,
) -> float:
    """Compute the median ratio newer/older over the overlap period.

    This calibration factor converts older-vintage levels to newer-vintage scale.
    Using median over the overlap (not just a single boundary point) reduces
    sensitivity to one-off revisions.
    """
    older_overlap = older_series.loc[overlap_start:overlap_end].dropna()
    newer_overlap = newer_series.loc[overlap_start:overlap_end].dropna()
    common_idx = older_overlap.index.intersection(newer_overlap.index)
    if len(common_idx) < 3:
        raise ValueError(
            f"Insufficient overlap ({len(common_idx)} months) to calibrate splice. "
            f"Overlap window: {overlap_start} to {overlap_end}"
        )
    ratios = newer_overlap.loc[common_idx] / older_overlap.loc[common_idx]
    ratio = float(ratios.median())
    if not np.isfinite(ratio) or ratio <= 0:
        raise ValueError(f"Invalid splice ratio {ratio}")
    return ratio


def build_chain() -> ChainResult:
    """Build the GDP back-history chain from 1981-01 to present.

    Effective chain: 36100390 (1981-2007, NAICS SA 1997 fixed-weight$)
                  -> 36100434 (1997-present, NAICS SAAR 2017 chained$)

    Note on 36100398: Initially planned as a bridge table, but the SAAR series
    in 36100398 only starts 1997-01 (not 1981-01). The pre-1997 extension is
    therefore provided exclusively by 36100390. The seam is directly
    390 (pre-1997) -> 434 (1997+), calibrated on the 1997-2007 overlap.

    Strategy:
    - One seam only: 36100390 ends 2007-07 and overlaps 36100434 from 1997-01.
    - Calibration: compute median ratio (434/390) over the 1997-01 to 2007-07
      overlap (127 months) — both total level and per common sector.
    - Concatenate: 390-rescaled for 1981-01 to 1996-12, then 434 from 1997-01+.
    - Growth rates are preserved exactly within each segment; the ratio only
      adjusts the level shift at the 1996/1997 seam.
    - Fixed-weight vs chain-weight price convention in 390 vs 434 affects
      levels but not sign-of-growth, which is all that breadth requires.
    """
    # 1. Load tables
    logger.info("Loading 36100434 (current, 1997-present)...")
    df_434 = _load_current_gdp_zip()

    logger.info("Loading 36100390 (archived, 1981-2007)...")
    df_390 = _load_archived_table(T390_CSV)

    # 36100398 loaded only for logging/verification (not used in the chain)
    logger.info("Loading 36100398 (archived, 1997-2012) for verification only...")
    df_398 = _load_archived_table(T398_CSV)

    # 2. Compute overlap window for the single seam
    # 36100390: 1981-01 to 2007-07
    # 36100434: 1997-01 to present
    # Overlap: 1997-01 to 2007-07 = 127 months
    overlap_start = df_434["date"].min()   # 1997-01-01
    overlap_end   = df_390["date"].max()   # 2007-07-01
    logger.info("Single seam (390->434): overlap %s to %s (%d months)",
                overlap_start.date(), overlap_end.date(),
                (overlap_end.year - overlap_start.year) * 12 +
                (overlap_end.month - overlap_start.month) + 1)

    # 3. Splice total level series
    total_390 = _extract_total_level(df_390)
    total_434 = _extract_total_level(df_434)

    ratio_total = _compute_splice_ratio(total_390, total_434, overlap_start, overlap_end)
    logger.info("Total-level splice ratio (390->434): %.6f", ratio_total)

    # Sanity check: the ratio should be >1 since 2017$ > 1997$ nominal scale
    if not (0.5 < ratio_total < 5.0):
        raise RuntimeError(
            f"Suspicious total-level splice ratio {ratio_total:.4f}. "
            "Expected between 0.5 and 5.0. Check that both tables use the "
            "all-industries aggregate and that the price base selection is correct."
        )

    # Rescale 390 to 434 scale
    total_390_adj = total_390 * ratio_total

    # Concatenate: 390-rescaled for pre-1997, then 434 from 1997+
    gdp_level = pd.concat([
        total_390_adj.loc[:"1996-12"],
        total_434.loc["1997-01":],
    ]).sort_index()
    gdp_level = gdp_level[~gdp_level.index.duplicated(keep="last")]
    gdp_level.name = "gdp_level"

    # 4. Build sector-level series for comparator breadth
    # Find common NAICS codes in both 390 and 434
    def _codes_in_table(df: pd.DataFrame) -> set[str]:
        raw_codes = set(df["naics_code"].unique())
        canonical = set()
        for c in raw_codes:
            norm = _normalise_naics(c)
            if norm:
                canonical.add(norm)
        return canonical

    codes_390 = _codes_in_table(df_390)
    codes_434 = _codes_in_table(df_434)
    common_codes = (codes_390 & codes_434) & set(COMMON_NAICS_SECTORS)
    logger.info("Common NAICS sectors across 36100390 and 36100434: %d", len(common_codes))
    logger.info("  -> %s", sorted(common_codes))

    if len(common_codes) < 8:
        raise RuntimeError(
            f"Too few common sectors ({len(common_codes)}) — chain not defensible. "
            "Check COMMON_NAICS_SECTORS vs actual table contents."
        )

    # Extract sector pivots
    pivot_390 = _extract_sector_pivot(df_390, common_codes)
    pivot_434 = _extract_sector_pivot(df_434, common_codes)

    # Align columns to intersection
    common_in_pivots = sorted(pivot_390.columns.intersection(pivot_434.columns))
    if not common_in_pivots:
        raise RuntimeError("No overlapping sector columns in pivots after extraction")

    pivot_390 = pivot_390[common_in_pivots]
    pivot_434 = pivot_434[common_in_pivots]

    # Per-sector splice ratios
    calibration: dict[str, float] = {}
    drop_sectors: list[str] = []

    for sector in common_in_pivots:
        try:
            r = _compute_splice_ratio(
                pivot_390[sector], pivot_434[sector],
                overlap_start, overlap_end,
            )
            calibration[sector] = r
        except ValueError as e:
            logger.warning("Dropping sector %s from common set: %s", sector, e)
            drop_sectors.append(sector)

    for s in drop_sectors:
        common_in_pivots.remove(s)
    pivot_390 = pivot_390[[c for c in common_in_pivots if c in pivot_390.columns]]
    pivot_434 = pivot_434[[c for c in common_in_pivots if c in pivot_434.columns]]

    # Rescale 390 sectors to 434 scale
    for sector in list(pivot_390.columns):
        r = calibration.get(sector, ratio_total)  # fallback to total ratio
        pivot_390[sector] = pivot_390[sector] * r

    # Concatenate sectors
    sector_levels = pd.concat([
        pivot_390.loc[:"1996-12"],
        pivot_434.loc["1997-01":, [c for c in common_in_pivots if c in pivot_434.columns]],
    ]).sort_index()
    sector_levels = sector_levels[~sector_levels.index.duplicated(keep="last")]
    # Keep only columns present in both segments
    sector_levels = sector_levels.dropna(how="all", axis=1)

    # Normalise gdp_level to an index (2000-01 = 1.0)
    ref_date = pd.Timestamp("2000-01-01")
    if ref_date in gdp_level.index:
        norm_val = gdp_level.loc[ref_date]
    else:
        norm_val = gdp_level.iloc[0]
    gdp_level = gdp_level / norm_val

    seam_dates = [str(overlap_start.date()), str(overlap_end.date())]
    calibration_ratios = {
        "seam_390_to_434_total": ratio_total,
        "note": "390 1997-const$ fixed-weight -> 434 2017$ chained; ratio=median(434/390) over 1997-2007",
    }

    logger.info("Chain built: %s to %s (%d months), %d sectors",
                gdp_level.index.min().date(), gdp_level.index.max().date(),
                len(gdp_level), len(sector_levels.columns))

    return ChainResult(
        gdp_level=gdp_level,
        sector_levels=sector_levels,
        start_date=gdp_level.index.min(),
        seam_dates=seam_dates,
        calibration_ratios=calibration_ratios,
    )
