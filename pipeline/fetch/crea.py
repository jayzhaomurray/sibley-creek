"""CREA MLS Home Price Index bulk-XLSX fetcher.

CREA publishes the MLS Home Price Index (HPI) as a monthly ZIP archive at
    https://www.crea.ca/files/mls-hpi-data/MLS_HPI_{Month}_{Year}.zip

The archive contains four XLSX files (Seasonally Adjusted Monthly, NSA Monthly,
NSA Quarterly, NSA Annual). Per dashboard_purpose section 4.4 element 1 we use
the SA monthly file. Each sheet inside the XLSX is a geography, with columns
for Composite, Single-Family, One/Two-Storey, Townhouse, Apartment as both
HPI (index, 2005=100) and Benchmark (dollar price).

CMA mapping (dashboard_purpose 4.4 names -> CREA sheet names; verified 2026-05-10):
    Toronto    -> GREATER_TORONTO
    Vancouver  -> GREATER_VANCOUVER
    Montreal   -> MONTREAL_CMA
    Calgary    -> CALGARY
    Ottawa     -> OTTAWA
    Edmonton   -> EDMONTON
    (National) -> AGGREGATE

Source quirks:
    - File naming uses the most recent release month + year, e.g.
      "MLS_HPI_April_2026.zip" for the April-2026 release. The cadence is
      monthly with a ~3-week lag (CREA publishes mid-month for the prior
      month's reference period).
    - CREA back-revises ~3 prior months as late-closing sales report in.
    - The Aggregate sheet is a CREA-constructed national composite; per the
      canon ("no national-average headline number"), use AGGREGATE only as
      methodology context, NOT as the headline price.
    - Greater Vancouver / Greater Toronto / Montreal CMA are the
      board-territory CMA-equivalent definitions; not the strict StatCan
      Census Metropolitan Area boundaries. Document this in any chart caption.
"""

from __future__ import annotations

import io
import logging
import zipfile
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Optional

import pandas as pd

from pipeline.fetch._http import get_client

CREA_BASE_URL = "https://www.crea.ca/files/mls-hpi-data"

logger = logging.getLogger(__name__)

# Canonical geography labels per dashboard_purpose 4.4 -> CREA sheet names.
CMA_SHEETS: dict[str, str] = {
    "canada": "AGGREGATE",
    "toronto": "GREATER_TORONTO",
    "vancouver": "GREATER_VANCOUVER",
    "montreal": "MONTREAL_CMA",
    "calgary": "CALGARY",
    "ottawa": "OTTAWA",
    "edmonton": "EDMONTON",
}

_MONTH_NAMES = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]


@dataclass(frozen=True)
class CreaFetchResult:
    """One geography's HPI cut.

    `data` is a long-format DataFrame with columns: date, value, where value
    is the Composite HPI SA index. Additional Composite-Benchmark dollar
    figures are kept in `benchmark_data` for callers who want the level cut.
    """

    geography: str
    sheet_name: str
    release_label: str  # e.g. "April_2026"
    data: pd.DataFrame
    benchmark_data: pd.DataFrame


def latest_release_url(today: Optional[date] = None) -> tuple[str, str]:
    """Guess the URL of the most recent CREA MLS HPI ZIP release.

    Returns (url, release_label). The current convention is that the file
    posted on day D names the most-recent COMPLETED reference period, which
    is typically one calendar month behind D. We probe the current candidate
    first; if the current-month file isn't up yet, the caller falls back to
    the prior month via `find_available_release()`.
    """
    today = today or date.today()
    # CREA publishes mid-month for the prior month's reference. By mid-month,
    # the current calendar month's file isn't named yet — use prior month.
    if today.day < 15:
        # Prior month
        m = today.month - 1 or 12
        y = today.year if today.month != 1 else today.year - 1
    else:
        m, y = today.month, today.year
    label = f"{_MONTH_NAMES[m - 1]}_{y}"
    return f"{CREA_BASE_URL}/MLS_HPI_{label}.zip", label


def find_available_release(today: Optional[date] = None, *, lookback: int = 4) -> tuple[bytes, str]:
    """Locate and download the most recent existing CREA release.

    Walks back from today's likely-current release through `lookback` months,
    returning the first ZIP that exists (HTTP 200). Raises if none of the
    candidates are available.
    """
    today = today or date.today()
    tried: list[str] = []
    last_error: Optional[Exception] = None
    with get_client() as client:
        for offset in range(lookback + 1):
            ref = pd.Timestamp(today) - pd.DateOffset(months=offset)
            label = f"{_MONTH_NAMES[ref.month - 1]}_{ref.year}"
            url = f"{CREA_BASE_URL}/MLS_HPI_{label}.zip"
            tried.append(url)
            try:
                r = client.get(url)
                if r.status_code == 200:
                    logger.info("CREA release found: %s", label)
                    return r.content, label
            except Exception as exc:  # noqa: BLE001
                last_error = exc
                logger.warning("CREA fetch attempt failed for %s: %s", label, exc)
                continue
    raise FileNotFoundError(
        f"No CREA MLS HPI ZIP found in last {lookback + 1} months. "
        f"Tried: {tried}. Last error: {last_error!r}"
    )


def fetch_sheet(zip_bytes: bytes, sheet_name: str) -> pd.DataFrame:
    """Extract one sheet from the SA-monthly XLSX inside a CREA ZIP.

    Returns the raw wide-format DataFrame as published by CREA. Use
    `to_long_form()` to pivot to the standard date/value contract.
    """
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
        target = "Seasonally Adjusted (M).xlsx"
        if target not in zf.namelist():
            raise FileNotFoundError(
                f"Expected {target!r} inside CREA ZIP; got {zf.namelist()}"
            )
        with zf.open(target) as f:
            df = pd.read_excel(f, sheet_name=sheet_name, engine="openpyxl")
    if "Date" not in df.columns:
        raise ValueError(
            f"CREA sheet {sheet_name!r} missing 'Date' column; got {list(df.columns)}"
        )
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df = df.dropna(subset=["Date"]).sort_values("Date").reset_index(drop=True)
    return df


def fetch_geography(zip_bytes: bytes, geography: str, release_label: str) -> CreaFetchResult:
    """Fetch a Composite-HPI-SA series for one named geography.

    `geography` must be one of the keys in CMA_SHEETS.
    """
    geography_norm = geography.strip().lower()
    if geography_norm not in CMA_SHEETS:
        raise KeyError(
            f"Unknown geography {geography!r}; supported: {sorted(CMA_SHEETS)}"
        )
    sheet_name = CMA_SHEETS[geography_norm]
    raw = fetch_sheet(zip_bytes, sheet_name)

    hpi = raw[["Date", "Composite_HPI_SA"]].rename(
        columns={"Date": "date", "Composite_HPI_SA": "value"}
    )
    benchmark = raw[["Date", "Composite_Benchmark_SA"]].rename(
        columns={"Date": "date", "Composite_Benchmark_SA": "value"}
    )
    return CreaFetchResult(
        geography=geography_norm,
        sheet_name=sheet_name,
        release_label=release_label,
        data=hpi.reset_index(drop=True),
        benchmark_data=benchmark.reset_index(drop=True),
    )


def release_url_for(release_label: str) -> str:
    """Human-readable URL for .meta.json provenance."""
    return f"{CREA_BASE_URL}/MLS_HPI_{release_label}.zip"
