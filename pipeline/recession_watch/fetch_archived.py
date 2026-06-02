"""Fetch archived StatCan GDP-by-industry tables for the GDP back-history chain.

Tables fetched:
  36100390  GDP at basic prices by NAICS, monthly, 1981-01 to 2007-07
  36100398  GDP at basic prices by NAICS, monthly, 1981-01 to 2012-10

The current table (36100434) is already on disk at data/raw/*.zip (via the
recon process) and loaded directly by the chain module.

Download approach: StatCan's dtl!downloadDbLoadingData endpoint, which serves
CSV data for archived tables that no longer appear in the WDS REST API. We
request SA + chained prices for Canada, all industry members.

Caching: files are saved to data/raw/recession_watch/ as <pid>_sa.csv with a
sibling .meta.json. Re-runs skip download if the file exists (archive tables
do not update). Pass force=True to re-fetch.
"""

from __future__ import annotations

import csv
import io
import json
import logging
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import pandas as pd
import requests

logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "data" / "raw" / "recession_watch"
OUT_DIR.mkdir(parents=True, exist_ok=True)

STATCAN_BASE = "https://www150.statcan.gc.ca"
DOWNLOAD_EP = f"{STATCAN_BASE}/t1/tbl1/en/dtl!downloadDbLoadingData-nonTraduit.action"

# Table configurations
# Keys: pid (numeric str), sa_dim, sa_member, price_dim, price_member, industry_dim, n_industries
# These are derived from the getCubeMetaData output verified in recon.
TABLE_CONFIGS = {
    "36100390": {
        "pid_str": "3610039001",
        "label": "GDP basic prices NAICS 1981-2007 (1997 const $, fixed-weight)",
        # dim1=geo(1=Canada), dim2=SA(2=SAAR), dim3=prices(1=1997 constant $), dim4=industries(1..312)
        # IMPORTANT: price member 1 ("1997 constant dollars" = fixed-weight) goes back to 1981.
        # Price member 2 ("Chained 1997 dollars" = chain-weighted) starts only 1997.
        # We use member 1 for the back-history chain; for breadth, sign of growth is what
        # matters, not the level convention. Noted in chain seam metadata.
        "geo_dim": 1, "geo_member": 1,
        "sa_dim": 2, "sa_member": 2,
        "price_dim": 3, "price_member": 1,   # 1997 constant dollars (member 1) — covers 1981+
        "industry_dim": 4, "n_industries": 312,
        "industry_col": "North American Industry Classification System (NAICS)",
        "sa_col": "Seasonal adjustment",
        "sa_val": "Seasonally adjusted at annual rates",
    },
    "36100398": {
        "pid_str": "3610039801",
        "label": "GDP basic prices NAICS 1981-2012 (2002 chained $)",
        # dim1=geo(1=Canada), dim2=SA(1=SAAR), dim3=prices(1=Chained 2002$), dim4=industries(1..303)
        "geo_dim": 1, "geo_member": 1,
        "sa_dim": 2, "sa_member": 1,
        "price_dim": 3, "price_member": 1,   # Chained 2002 dollars (member 1)
        "industry_dim": 4, "n_industries": 303,
        "industry_col": "North American Industry Classification System (NAICS)",
        "sa_col": "Seasonal adjustment",
        "sa_val": "Seasonally adjusted at annual rates",
    },
}


def _build_selected_members(config: dict) -> str:
    """Build the URL-encoded selectedMembers parameter for all industries.

    selectedMembers is a JSON array of arrays, one per dimension.
    Each inner array lists the member IDs (1-indexed) to include.
    """
    n = config["n_industries"]
    dims = {
        config["geo_dim"]: [config["geo_member"]],
        config["sa_dim"]: [config["sa_member"]],
        config["price_dim"]: [config["price_member"]],
        config["industry_dim"]: list(range(1, n + 1)),
    }
    # Build array indexed 1..max_dim_id
    max_dim = max(dims)
    members_array = [dims.get(i, []) for i in range(1, max_dim + 1)]
    return urllib.parse.quote(json.dumps(members_array))


def _download_table(pid: str, config: dict, session: requests.Session) -> bytes:
    """Download full CSV for an archived table.

    The latestN parameter controls how many recent periods to fetch per series.
    StatCan's downloadDbLoadingData treats latestN=0 as "0 rows" rather than
    "all rows" — so we use a large number (1000) to capture the full history
    of any archived table. The longest archived table we chain (36100390: 1981
    to 2007) has 318 months; 1000 comfortably covers it.
    """
    selected = _build_selected_members(config)
    url = (
        f"{DOWNLOAD_EP}"
        f"?pid={config['pid_str']}"
        f"&latestN=1000"       # large enough to capture full archived history
        f"&startDate="
        f"&endDate="
        f"&csvLocale=en"
        f"&selectedMembers={selected}"
        f"&checkedLevels="
    )
    logger.info("Fetching %s (%s) ...", pid, config["label"])
    resp = session.get(url, timeout=300, verify=False)
    resp.raise_for_status()
    return resp.content


def _parse_csv_to_df(raw: bytes, config: dict) -> pd.DataFrame:
    """Parse the raw downloaded CSV into a tidy DataFrame.

    Returns columns: date (datetime), naics_code (str), industry_name (str),
    value (float), vector (str).
    Filters to SA + the correct price base only (defensive — download is already
    filtered by dimension selection, but the CSV may include aggregate rows with
    different SA labels depending on StatCan rendering).
    """
    text = raw.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text))
    rows = []
    sa_col = config["sa_col"]
    sa_val = config["sa_val"]
    ind_col = config["industry_col"]

    for row in reader:
        # Keep only SA rows
        if row.get(sa_col, "").strip() != sa_val:
            continue
        ref = row.get("REF_DATE", "").strip()
        if not ref:
            continue
        # StatCan REF_DATE for monthly = "YYYY-MM"
        try:
            dt = datetime.strptime(ref, "%Y-%m").replace(day=1)
        except ValueError:
            continue
        val_str = row.get("VALUE", "").strip()
        if not val_str:
            continue
        try:
            value = float(val_str)
        except ValueError:
            continue
        naics_raw = row.get(ind_col, "").strip()
        # Extract NAICS code from brackets: "Oil and gas extraction [211]" -> "211"
        # For 36100390 top-level names like "All industries", no brackets exist —
        # keep the full name as the code so chain.py can match on industry_name.
        import re
        match = re.search(r"\[([^\]]+)\]$", naics_raw)
        naics_code = match.group(1) if match else naics_raw
        rows.append({
            "date": dt,
            "naics_code": naics_code,
            "industry_name": naics_raw,
            "value": value,
            "vector": row.get("VECTOR", "").strip(),
        })

    if not rows:
        raise ValueError(f"No SA rows found in downloaded CSV")

    df = pd.DataFrame(rows)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values(["date", "naics_code"]).reset_index(drop=True)
    return df


def _write_output(pid: str, df: pd.DataFrame, config: dict, fetched_at: str) -> Path:
    """Write to data/raw/recession_watch/<pid>_sa.csv + sibling .meta.json."""
    csv_path = OUT_DIR / f"{pid}_sa.csv"
    df.to_csv(csv_path, index=False)

    meta = {
        "source": "Statistics Canada (archived table)",
        "table_id": pid,
        "pid_str": config["pid_str"],
        "label": config["label"],
        "fetched_at": fetched_at,
        "reference_period_start": str(df["date"].min().date()),
        "reference_period_end": str(df["date"].max().date()),
        "n_rows": len(df),
        "n_industries": df["naics_code"].nunique(),
        "price_note": config["label"],
    }
    meta_path = OUT_DIR / f"{pid}_sa.meta.json"
    meta_path.write_text(json.dumps(meta, indent=2))
    logger.info("Wrote %s (%d rows, %d industries) -> %s",
                pid, len(df), df["naics_code"].nunique(), csv_path)
    return csv_path


def fetch_archived_tables(pids: list[str] | None = None, force: bool = False) -> dict[str, Path]:
    """Fetch and cache archived GDP industry tables.

    Args:
        pids: list of table IDs to fetch (default: all configured).
        force: re-download even if cached file exists.

    Returns:
        dict mapping pid -> csv Path.
    """
    if pids is None:
        pids = list(TABLE_CONFIGS)

    session = requests.Session()
    session.headers.update({"User-Agent": "macro-research-department/1.0 research pipeline"})

    results: dict[str, Path] = {}
    for pid in pids:
        if pid not in TABLE_CONFIGS:
            raise ValueError(f"Unknown table: {pid}. Known: {list(TABLE_CONFIGS)}")
        config = TABLE_CONFIGS[pid]
        csv_path = OUT_DIR / f"{pid}_sa.csv"
        meta_path = OUT_DIR / f"{pid}_sa.meta.json"

        if csv_path.exists() and meta_path.exists() and not force:
            logger.info("Cache hit: %s -> %s", pid, csv_path)
            results[pid] = csv_path
            continue

        fetched_at = datetime.now(timezone.utc).isoformat()
        raw = _download_table(pid, config, session)
        df = _parse_csv_to_df(raw, config)
        _write_output(pid, df, config, fetched_at)
        results[pid] = csv_path

    return results


def load_cached_table(pid: str) -> pd.DataFrame:
    """Load a previously fetched and cached archived table."""
    csv_path = OUT_DIR / f"{pid}_sa.csv"
    if not csv_path.exists():
        raise FileNotFoundError(
            f"Cached file not found: {csv_path}. Run fetch_archived_tables() first."
        )
    df = pd.read_csv(csv_path, parse_dates=["date"])
    return df


if __name__ == "__main__":
    import warnings
    warnings.filterwarnings("ignore")
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    paths = fetch_archived_tables()
    for pid, p in paths.items():
        print(f"  {pid}: {p}")
