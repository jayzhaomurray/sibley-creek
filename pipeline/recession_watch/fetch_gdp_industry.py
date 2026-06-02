"""Extract 3-digit NAICS GDP industry series from 36100434 for fine breadth.

The ZIP is already on disk (claude-ref/research/recession_watch/36100434_raw.zip).
This module identifies ~84 leaf-level 3-digit NAICS industries (excluding
parent-aggregate rows) and returns a wide pivot suitable for the fine
current-detail breadth computation.

Leaf identification: a NAICS code is a leaf if no other code in the table
has it as a parent. We implement this by building the parent-child tree
from the coordinate field and keeping only terminal nodes.

NOTE: This is 1997+ only. Not used for cycle-on-cycle comparators.
"""

from __future__ import annotations

import csv
import io
import json
import logging
import re
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[2]
RW_DIR = ROOT / "data" / "raw" / "recession_watch"
RW_DIR.mkdir(parents=True, exist_ok=True)

ZIP_LOCATIONS = [
    RW_DIR / "36100434_raw.zip",
    ROOT / "claude-ref" / "research" / "recession_watch" / "36100434_raw.zip",
]

OUT_CSV = RW_DIR / "gdp_3digit_naics_sa.csv"
OUT_META = RW_DIR / "gdp_3digit_naics_sa.meta.json"

# T-aggregate codes to always exclude (cross-cutting, not NAICS sectors)
T_CODES_EXCLUDE = {"T001", "T002", "T003", "T004", "T005", "T006", "T007",
                   "T008", "T009", "T010", "T011", "T012", "T013", "T014",
                   "T015", "T016", "T017", "T018"}


def _find_zip() -> Path:
    for p in ZIP_LOCATIONS:
        if p.exists():
            return p
    raise FileNotFoundError(f"36100434_raw.zip not found. Locations checked: {ZIP_LOCATIONS}")


def _parse_gdp_zip_sa(zip_path: Path) -> pd.DataFrame:
    """Parse 36100434 ZIP, keeping only Canada SA chained 2017$ rows."""
    rows = []
    with zipfile.ZipFile(zip_path) as z:
        csv_names = [n for n in z.namelist() if n.endswith(".csv") and "MetaData" not in n]
        csv_name = csv_names[0]
        with z.open(csv_name) as f:
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
                naics_raw = row.get(
                    "North American Industry Classification System (NAICS)", ""
                ).strip()
                coord = row.get("COORDINATE", "").strip()
                vector = row.get("VECTOR", "").strip()
                match = re.search(r"\[([^\]]+)\]$", naics_raw)
                naics_code = match.group(1) if match else ""
                rows.append({
                    "date": dt,
                    "naics_code": naics_code,
                    "industry_name": naics_raw,
                    "coordinate": coord,
                    "value": value,
                    "vector": vector,
                })
    if not rows:
        raise ValueError("No SA rows found in 36100434 ZIP")
    df = pd.DataFrame(rows)
    df["date"] = pd.to_datetime(df["date"])
    return df


def _identify_leaf_codes(df: pd.DataFrame) -> list[str]:
    """Identify leaf NAICS codes (codes that are not parents of other codes).

    Uses the COORDINATE field structure: in 36100434, the coordinate is
    "1.{dim2}.1.1.0..." where dim2 is the industry member index.
    Instead of parsing coordinates, we infer parent-child from the NAICS
    code hierarchy directly.

    Strategy:
      - Extract all NAICS codes (bracket content)
      - A code X is a parent if any other code Y starts with X (and Y != X)
        and both are numeric/hyphenated
      - Leaf = not a parent; also exclude T-codes and aggregates

    For codes like "31-33" (Manufacturing), sub-codes "311", "312", etc.
    are children. "31-33" itself would be a parent if any "31x" exists.
    """
    # Get unique codes (non-empty, non-T)
    all_codes = set(df["naics_code"].unique())
    all_codes = {c for c in all_codes if c and c not in T_CODES_EXCLUDE}

    # Special multi-code ranges: 31-33, 44-45, 48-49 are aggregates
    range_codes = {"31-33", "44-45", "48-49", "11A", "11", "21"}

    # Determine which codes are parents
    # A code P is a parent of code C if:
    #   len(C) > len(P) and C starts with P (for simple numeric codes)
    #   or C is a sub-code of a range (e.g. C="311" is under "31-33")
    def is_parent_of(p: str, c: str) -> bool:
        if p == c or not p or not c:
            return False
        # T-codes are always top-level aggregates
        if p.startswith("T") or c.startswith("T"):
            return False
        # Simple prefix: "21" is parent of "211", "212"
        if c.startswith(p) and len(c) > len(p):
            return True
        # Range: "31-33" covers codes starting with 31, 32, 33
        if "-" in p:
            parts = p.split("-")
            if len(parts) == 2:
                try:
                    lo, hi = int(parts[0]), int(parts[1])
                    # Extract numeric prefix of c of same length as range parts
                    prefix_len = len(parts[0])
                    if len(c) >= prefix_len:
                        try:
                            prefix = int(c[:prefix_len])
                            if lo <= prefix <= hi:
                                return True
                        except ValueError:
                            pass
                except ValueError:
                    pass
        return False

    parents = set()
    code_list = list(all_codes)
    for i, p in enumerate(code_list):
        for c in code_list:
            if is_parent_of(p, c):
                parents.add(p)
                break

    leaves = [c for c in all_codes if c not in parents and c not in T_CODES_EXCLUDE]

    # Also exclude pure range codes (they are definitely aggregates)
    leaves = [c for c in leaves if "-" not in c or c not in range_codes]

    # Further filter: keep only codes with reasonable coverage
    # (present for at least 60 months = 5 years)
    code_counts = df[df["naics_code"].isin(leaves)].groupby("naics_code")["date"].nunique()
    leaves = [c for c in leaves if code_counts.get(c, 0) >= 60]

    leaves.sort()
    logger.info("Identified %d leaf NAICS codes for fine GDP breadth", len(leaves))
    return leaves


def fetch_gdp_3digit_pivot(force: bool = False) -> pd.DataFrame:
    """Load 36100434 leaf-industry pivot for fine breadth computation.

    Returns: DataFrame indexed by date, columns = NAICS leaf codes.
    Cached to data/raw/recession_watch/gdp_3digit_naics_sa.csv.
    """
    if OUT_CSV.exists() and OUT_META.exists() and not force:
        logger.info("Cache hit: GDP 3-digit NAICS -> %s", OUT_CSV)
        df = pd.read_csv(OUT_CSV, parse_dates=["date"], index_col="date")
        return df

    zip_path = _find_zip()
    logger.info("Parsing 36100434 for 3-digit NAICS breadth from %s ...", zip_path)

    df = _parse_gdp_zip_sa(zip_path)
    leaf_codes = _identify_leaf_codes(df)

    # Pivot to wide
    df_leaf = df[df["naics_code"].isin(leaf_codes)].copy()
    pivot = (
        df_leaf.groupby(["date", "naics_code"])["value"]
        .mean()
        .unstack("naics_code")
    )

    pivot.to_csv(OUT_CSV)

    meta = {
        "source": "Statistics Canada, Table 36-10-0434-01",
        "table_id": "36100434",
        "description": "Monthly SA real GDP at 3-digit NAICS leaf industries, Canada, chained 2017$",
        "frequency": "monthly",
        "reference_period_start": str(pivot.index.min().date()),
        "reference_period_end": str(pivot.index.max().date()),
        "n_leaf_industries": len(leaf_codes),
        "leaf_codes": leaf_codes,
        "processed_at": datetime.now(timezone.utc).isoformat(),
        "note": "1997+ only. Not comparable across recession eras. Fine breadth = current-detail only.",
    }
    OUT_META.write_text(json.dumps(meta, indent=2))
    logger.info("GDP 3-digit pivot: %d industries, %s to %s",
                len(leaf_codes), pivot.index.min().date(), pivot.index.max().date())
    return pivot


if __name__ == "__main__":
    import warnings
    warnings.filterwarnings("ignore")
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    pivot = fetch_gdp_3digit_pivot(force=True)
    print(f"Pivot shape: {pivot.shape}")
    print(f"Date range: {pivot.index.min().date()} to {pivot.index.max().date()}")
    print(f"Sample codes: {list(pivot.columns[:10])}")
