"""LFS PUMF downloader.

Downloads Statistics Canada LFS PUMF monthly cross-sections via two URL patterns:

  Recent (last ~3 months):
    https://www150.statcan.gc.ca/n1/pub/71m0001x/2021001/{YYYY-MM}-CSV.zip

  Historical annual bundles (2015-present):
    https://www150.statcan.gc.ca/n1/pub/71m0001x/2021001/hist/{YYYY}-CSV.zip
    Each zip contains 12 monthly CSVs named pub{MM}{YY}.csv.

Resolution logic: for a requested month M, try the recent monthly URL first.
On 404 (or any non-200), fall back to extracting from the annual bundle.
Annual bundles are cached at data/raw/lfs_pumf/annual/{YYYY}-CSV.zip.

Output: data/raw/lfs_pumf/{YYYY-MM}.parquet (trimmed to needed columns) +
        data/raw/lfs_pumf/{YYYY-MM}.meta.json sidecar.

Idempotent: if the parquet already exists, returns the cached path without
re-fetching. Pass force=True to overwrite.

IMPORTANT: StatCan www150.statcan.gc.ca uses TLS fingerprinting to block
non-browser clients. httpx and urllib fail at the handshake. Only requests
with a Chrome User-Agent passes. This module is intentionally isolated so
the rest of the pipeline continues using httpx.
"""

from __future__ import annotations

import io
import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import pandas as pd
import requests

# ---------------------------------------------------------------------------
# Paths and URLs
# ---------------------------------------------------------------------------

_PROJECT_ROOT = Path(__file__).parents[2]
_RAW_DIR = _PROJECT_ROOT / "data" / "raw" / "lfs_pumf"
_ANNUAL_DIR = _RAW_DIR / "annual"

_MONTHLY_URL = (
    "https://www150.statcan.gc.ca/n1/pub/71m0001x/2021001/{YYYY-MM}-CSV.zip"
)
_ANNUAL_URL = (
    "https://www150.statcan.gc.ca/n1/pub/71m0001x/2021001/hist/{YYYY}-CSV.zip"
)

# Chrome UA required to pass StatCan's TLS fingerprint filter (spike finding).
_BROWSER_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)

_TIMEOUT_SEC = 120  # large files; 2024 annual = 32 MB

# ---------------------------------------------------------------------------
# Columns to retain from the raw CSV (keeps parquet size manageable)
# ---------------------------------------------------------------------------

# All columns needed for harmonize.py + the engine. Keeping SURVYEAR/SURVMNTH
# for vintage identification when combining months from annual bundles.
_KEEP_COLS = [
    "survyear", "survmnth",
    "lfsstat", "cowmain",
    "hrlyearn", "finalwt",
    "gender",
    "age_12",
    "educ",
    "tenure",
    "noc_43",
    "naics_21",
    "union",
    "ftptmain",
    "mjh",
    "permtemp",
    "marstat",
    "immig",
    "estsize",
    "prov",
]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_month(
    year: int,
    month: int,
    force: bool = False,
) -> Path:
    """Return the parquet path for the requested PUMF month, downloading if needed.

    Args:
        year:  Four-digit year (e.g. 2026).
        month: Integer month 1-12.
        force: If True, re-download even if the parquet is already cached.

    Returns:
        Path to the .parquet file.

    Raises:
        RuntimeError: If the month cannot be fetched from either URL pattern.
    """
    _RAW_DIR.mkdir(parents=True, exist_ok=True)
    _ANNUAL_DIR.mkdir(parents=True, exist_ok=True)

    parquet_path = _RAW_DIR / f"{year:04d}-{month:02d}.parquet"
    if parquet_path.exists() and not force:
        return parquet_path

    df, source_url, fetched_at = _fetch_month_df(year, month)
    df = _trim_columns(df)

    # Integrity check: survyear/survmnth must match the requested month.
    # This catches spike-cache contamination and single-CSV fallback mis-extraction.
    _validate_survyear_survmnth(df, year, month, source_url)

    df.to_parquet(parquet_path, index=False, engine="pyarrow")
    _write_meta(parquet_path, year, month, source_url, fetched_at, len(df))

    return parquet_path


def latest_available_month(
    start_year: int = 2026,
    start_month: Optional[int] = None,
    lookback: int = 6,
) -> tuple[int, int]:
    """Probe backwards from start_year/start_month to find the newest PUMF month.

    Tries the monthly URL first (HEAD request to avoid downloading the full zip),
    then the annual bundle. Probes up to `lookback` months backwards.

    Args:
        start_year:  Year to start probing from (default: current year).
        start_month: Month to start from (default: current month).
        lookback:    Number of months to probe backwards before giving up.

    Returns:
        (year, month) of the newest available PUMF.

    Raises:
        RuntimeError: If no available month is found within lookback range.
    """
    if start_month is None:
        now = datetime.now()
        start_year = now.year
        start_month = now.month

    session = _make_session()

    year, month = start_year, start_month
    for _ in range(lookback):
        if _probe_monthly_url(session, year, month) or _probe_annual_bundle(session, year):
            return year, month
        # step back one month
        month -= 1
        if month == 0:
            month = 12
            year -= 1

    raise RuntimeError(
        f"No PUMF month found within {lookback} months before "
        f"{start_year:04d}-{start_month:02d}. "
        "StatCan may be delayed or URL patterns have changed."
    )


def get_month_from_spike_cache(year: int, month: int) -> Optional[Path]:
    """Return the parquet path if already cached, including spike cache, else None.

    Checks the standard cache first, then looks for a zip in the spike folder
    and extracts from it if found. Used during development to avoid re-downloading.
    """
    _RAW_DIR.mkdir(parents=True, exist_ok=True)
    parquet_path = _RAW_DIR / f"{year:04d}-{month:02d}.parquet"
    if parquet_path.exists():
        return parquet_path

    # Check spike folder for a cached zip
    spike_dir = _RAW_DIR / "_spike"
    if not spike_dir.exists():
        return None

    # Try monthly zip in spike cache
    for candidate in spike_dir.glob("*.zip"):
        try:
            df = _extract_monthly_from_zip_bytes(candidate.read_bytes(), year, month)
            if df is not None:
                df = _trim_columns(df)
                df.to_parquet(parquet_path, index=False, engine="pyarrow")
                _write_meta(
                    parquet_path, year, month,
                    source_url=f"spike_cache:{candidate.name}",
                    fetched_at=datetime.now(timezone.utc).isoformat(),
                    n_rows=len(df),
                )
                return parquet_path
        except Exception:
            continue

    return None


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _make_session() -> requests.Session:
    """Create a requests session with the browser User-Agent."""
    session = requests.Session()
    session.headers.update({"User-Agent": _BROWSER_UA})
    return session


def _probe_monthly_url(session: requests.Session, year: int, month: int) -> bool:
    """HEAD-probe the monthly URL; return True if it returns 200."""
    url = _MONTHLY_URL.format(**{"YYYY-MM": f"{year:04d}-{month:02d}"})
    try:
        r = session.head(url, timeout=15, allow_redirects=True)
        return r.status_code == 200
    except Exception:
        return False


def _probe_annual_bundle(session: requests.Session, year: int) -> bool:
    """HEAD-probe the annual bundle URL; return True if it returns 200."""
    url = _ANNUAL_URL.format(YYYY=year)
    try:
        r = session.head(url, timeout=15, allow_redirects=True)
        return r.status_code == 200
    except Exception:
        return False


def _fetch_month_df(
    year: int,
    month: int,
) -> tuple[pd.DataFrame, str, str]:
    """Download and return the raw DataFrame for the requested month.

    Returns:
        (df, source_url, fetched_at_iso)

    Raises:
        RuntimeError if neither URL pattern works.
    """
    session = _make_session()
    fetched_at = datetime.now(timezone.utc).isoformat()

    # --- Try the recent monthly URL first ---
    monthly_url = _MONTHLY_URL.format(**{"YYYY-MM": f"{year:04d}-{month:02d}"})
    try:
        r = session.get(monthly_url, timeout=_TIMEOUT_SEC)
        if r.status_code == 200 and r.content[:2] == b"PK":
            df = _extract_monthly_from_zip_bytes(r.content, year, month)
            if df is not None:
                return df, monthly_url, fetched_at
    except requests.RequestException:
        pass

    # --- Fall back to annual bundle ---
    annual_url = _ANNUAL_URL.format(YYYY=year)
    annual_zip_path = _ANNUAL_DIR / f"{year:04d}-CSV.zip"

    # Use cached annual zip if available (content-addressed: re-fetch only if missing)
    if not annual_zip_path.exists():
        r = session.get(annual_url, timeout=_TIMEOUT_SEC)
        if r.status_code != 200:
            raise RuntimeError(
                f"PUMF fetch failed for {year:04d}-{month:02d}.\n"
                f"  Monthly URL {monthly_url} -> not 200\n"
                f"  Annual URL  {annual_url} -> HTTP {r.status_code}\n"
                f"StatCan may be down or URL patterns have changed."
            )
        if r.content[:2] != b"PK":
            raise RuntimeError(
                f"Annual bundle {annual_url} returned non-zip content. "
                "StatCan response format may have changed."
            )
        annual_zip_path.write_bytes(r.content)

    annual_bytes = annual_zip_path.read_bytes()
    df = _extract_monthly_from_zip_bytes(annual_bytes, year, month)
    if df is None:
        raise RuntimeError(
            f"Month {year:04d}-{month:02d} not found inside annual bundle "
            f"{annual_url}. Expected file named like pub{month:02d}{str(year)[2:]}.csv."
        )
    return df, annual_url, fetched_at


def _extract_monthly_from_zip_bytes(
    zip_bytes: bytes,
    year: int,
    month: int,
) -> Optional[pd.DataFrame]:
    """Extract the per-month CSV from a zip file's bytes and return a DataFrame.

    The file naming convention inside the zip is pub{MM}{YY}.csv, e.g.:
      pub0126.csv  for January 2026
      pub1224.csv  for December 2024

    For a monthly zip (one CSV inside), also accepts any single .csv entry.

    Returns None if no matching CSV is found.
    """
    yy = str(year)[2:]  # last two digits of year
    target_name = f"pub{month:02d}{yy}.csv"

    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
        names = zf.namelist()
        # CSV entries can be at the top level OR nested one directory deep
        # (e.g. 2025 annual bundle stores: "2025-CSV.zip/pub0125.csv").
        # Normalise by taking the basename of each path entry.
        csv_names = [n for n in names if n.lower().endswith(".csv")
                     and not n.lower().startswith("documents")]

        # Exact match on basename (ignore any leading directory component)
        matched = None
        for n in csv_names:
            basename = n.split("/")[-1]
            if basename.lower() == target_name.lower():
                matched = n
                break

        # For a monthly zip with a single CSV, accept any single CSV entry.
        # NOTE: this fallback does NOT validate the filename — survyear/survmnth
        # integrity check in get_month() catches contamination after extraction.
        if matched is None and len(csv_names) == 1:
            matched = csv_names[0]

        if matched is None:
            return None

        with zf.open(matched) as f:
            df = pd.read_csv(f, low_memory=False)

    # Normalize column names to lowercase
    df.columns = df.columns.str.lower()
    return df


def _trim_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Retain only the columns needed by harmonize.py + engine.

    Missing columns are silently ignored here — harmonize.py will catch them
    with a fail-closed check.
    """
    keep = [c for c in _KEEP_COLS if c in df.columns]
    return df[keep].copy()


def _validate_survyear_survmnth(
    df: pd.DataFrame,
    year: int,
    month: int,
    source_url: str,
) -> None:
    """Fail-closed check: survyear and survmnth must match the requested month.

    The single-CSV fallback in _extract_monthly_from_zip_bytes accepts any CSV
    when the target filename is missing — this can silently yield a different
    month's data (e.g. Apr 2026 data written as Jun 2024 or Apr 2025).

    Raises:
        RuntimeError: if the embedded year/month does not match.
    """
    if "survyear" not in df.columns or "survmnth" not in df.columns:
        # Cannot validate — trust the filename (old PUMF formats pre-2015 may lack these)
        return

    actual_years = df["survyear"].dropna().unique().tolist()
    actual_months = df["survmnth"].dropna().unique().tolist()

    year_ok = len(actual_years) == 1 and int(actual_years[0]) == year
    month_ok = len(actual_months) == 1 and int(actual_months[0]) == month

    if not (year_ok and month_ok):
        raise RuntimeError(
            f"PUMF integrity check failed for {year:04d}-{month:02d}.\n"
            f"  Source: {source_url}\n"
            f"  Expected survyear={year} survmnth={month}.\n"
            f"  Got     survyear={actual_years} survmnth={actual_months}.\n"
            f"This is typically caused by the single-CSV fallback extracting the wrong "
            f"month from a cached spike zip, or StatCan serving a different month. "
            f"Delete the cached annual zip and retry, or pass force=True."
        )


def _write_meta(
    parquet_path: Path,
    year: int,
    month: int,
    source_url: str,
    fetched_at: str,
    n_rows: int,
) -> None:
    """Write a .meta.json sidecar alongside the parquet file."""
    meta = {
        "source": "Statistics Canada LFS PUMF (catalogue 71M0001X/2021001)",
        "source_url": source_url,
        "source_id": f"LFS PUMF {year:04d}-{month:02d}",
        "reference_period": f"{year:04d}-{month:02d}",
        "fetched_at": fetched_at,
        "n_rows_full_sample": n_rows,
        "columns_retained": _KEEP_COLS,
        "units": "Microdata (individual respondents); HRLYEARN in raw cents (divide by 100 for dollars)",
        "hrlyearn_encoding": "Two decimals implied: raw 3100 = $31.00/hr",
        "schema_version": 1,
    }
    meta_path = parquet_path.with_suffix(".meta.json")
    meta_path.write_text(json.dumps(meta, indent=2))
