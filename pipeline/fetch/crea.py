"""CREA MLS Home Price Index bulk-XLSX fetcher.

CREA publishes the MLS Home Price Index (HPI) as a monthly ZIP archive under
    https://www.crea.ca/files/mls-hpi-data/MLS_HPI_{MonthToken}_{Year}.zip

The archive contains four XLSX files (Seasonally Adjusted Monthly, NSA Monthly,
NSA Quarterly, NSA Annual). Per dashboard_purpose section 4.4 element 1 we use
the SA monthly file. Each sheet inside the XLSX is a geography, with columns
for Composite, Single-Family, One/Two-Storey, Townhouse, Apartment as both
HPI (index, 2005=100) and Benchmark (dollar price).

CMA mapping (dashboard_purpose 4.4 names -> CREA sheet names; verified
2026-05-10, re-verified against the Sept_2026 ZIP on 2026-10-03):
    Toronto    -> GREATER_TORONTO
    Vancouver  -> GREATER_VANCOUVER
    Montreal   -> MONTREAL_CMA
    Calgary    -> CALGARY
    Ottawa     -> OTTAWA
    Edmonton   -> EDMONTON
    (National) -> AGGREGATE

Source quirks:
    - The ZIP filename carries the RELEASE month, not the reference month:
      "MLS_HPI_May_2026.zip" was posted mid-May 2026 with data through
      April 2026. Cadence is monthly, mid-month.
    - The month token in the filename is NOT stable. Through May 2026 CREA
      used the full English month name ("MLS_HPI_May_2026.zip"); by the
      August 2026 release it had switched to abbreviations, inconsistently
      ("MLS_HPI_Aug_2026.zip", then "MLS_HPI_Sept_2026.zip"; "Sep_2026"
      404s). The June and July 2026 files do not resolve under any spelling
      we know of. A fetcher that only guessed full month names kept
      re-downloading the May ZIP every day from June to September 2026 and
      reported success; the housing price series sat frozen at an April
      reference month until the May file aged out of the lookback window
      and the build finally failed (2026-10-01).
    - Because of that, discovery is page-first: the "Accept and download
      data" button on the HPI tool page (HPI_TOOL_PAGE_URL) points at the
      current ZIP. The dated-URL guess (all known month spellings) is only
      the fallback if the page layout changes.
    - Whatever discovery finds, `check_release_freshness()` compares the
      latest reference month inside the workbook against the calendar and
      raises if the file is two or more release cycles behind. Do not widen
      the lookback to make a failure go away.
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
import re
import zipfile
from dataclasses import dataclass
from datetime import date
from email.utils import parsedate_to_datetime
from typing import Optional
from urllib.parse import urljoin

import httpx
import pandas as pd

from pipeline.fetch._http import get_bytes, get_client

CREA_BASE_URL = "https://www.crea.ca/files/mls-hpi-data"
# Page whose "Accept and download data" button links the current ZIP.
HPI_TOOL_PAGE_URL = "https://www.crea.ca/housing-market-stats/mls-home-price-index/hpi-tool/"

# Freshness contract. With a mid-month release for the prior month, the latest
# reference month is normally 1 calendar month behind today (after the release)
# or 2 (before it). 3 means one release is late or was missed: warn. More than
# 3 means we are two or more release cycles behind: fail loudly.
WARN_REFERENCE_LAG_MONTHS = 3
MAX_REFERENCE_LAG_MONTHS = 3

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


class CreaStaleReleaseError(RuntimeError):
    """The newest CREA ZIP we can find is too old to be the current release."""


@dataclass(frozen=True)
class CreaRelease:
    """One downloaded CREA MLS HPI ZIP plus where it came from."""

    zip_bytes: bytes
    label: str                 # filename token, e.g. "Sept_2026" / "May_2026"
    url: str
    published: Optional[date]  # HTTP Last-Modified of the ZIP, if the server sent one
    discovered_via: str        # "page" | "dated-url-guess"


@dataclass(frozen=True)
class CreaFetchResult:
    """One geography's HPI cut.

    `data` is a long-format DataFrame with columns: date, value, where value
    is the Composite HPI SA index. Additional Composite-Benchmark dollar
    figures are kept in `benchmark_data` for callers who want the level cut.
    """

    geography: str
    sheet_name: str
    release_label: str  # e.g. "Sept_2026"
    data: pd.DataFrame
    benchmark_data: pd.DataFrame


# --------------------------------------------------------------------------- #
# Release discovery
# --------------------------------------------------------------------------- #

_ZIP_HREF_RE = re.compile(
    r"""href\s*=\s*["']([^"']*MLS_HPI_([A-Za-z]+_\d{4})\.zip)["']""",
    re.IGNORECASE,
)


def release_url_for(release_label: str) -> str:
    """Canonical ZIP URL for a filename label such as "Sept_2026"."""
    return f"{CREA_BASE_URL}/MLS_HPI_{release_label}.zip"


def parse_release_label(label: str) -> Optional[date]:
    """Map "Sept_2026" / "May_2026" / "Aug_2026" to date(year, month, 1), else None."""
    m = re.fullmatch(r"([A-Za-z]{3,9})_(\d{4})", label.strip())
    if not m:
        return None
    token = m.group(1).lower()
    for i, name in enumerate(_MONTH_NAMES, start=1):
        # Any 3+ letter prefix of the month name: "Sep", "Sept", "September".
        if name.lower().startswith(token):
            return date(int(m.group(2)), i, 1)
    return None


def month_label_variants(year: int, month: int) -> list[str]:
    """Every filename month spelling CREA has been seen to use, likeliest first."""
    full = _MONTH_NAMES[month - 1]
    tokens = [full, full[:3]]
    if month == 9:
        tokens.append("Sept")
    labels: list[str] = []
    for t in tokens:
        label = f"{t}_{year}"
        if label not in labels:
            labels.append(label)
    return labels


def extract_zip_links(html: str, *, base_url: str = HPI_TOOL_PAGE_URL) -> list[tuple[str, str]]:
    """Pull (absolute_url, label) for every MLS_HPI_*.zip link in the page HTML.

    Ordered newest release first where labels parse; unparseable labels keep
    document order after the parseable ones.
    """
    found: list[tuple[str, str]] = []
    for href, label in _ZIP_HREF_RE.findall(html):
        item = (urljoin(base_url, href), label)
        if item not in found:
            found.append(item)
    parsed = [(parse_release_label(lbl), url, lbl) for url, lbl in found]
    dated = sorted((p for p in parsed if p[0] is not None), key=lambda p: p[0], reverse=True)
    undated = [p for p in parsed if p[0] is None]
    return [(url, lbl) for _, url, lbl in dated + undated]


def _published_date(response: httpx.Response) -> Optional[date]:
    raw = response.headers.get("last-modified")
    if not raw:
        return None
    try:
        return parsedate_to_datetime(raw).date()
    except (TypeError, ValueError):
        return None


def _is_zip(response: httpx.Response) -> bool:
    # Missing files come back as a 404 JSON/HTML shell; also guard against a
    # 200 that is not actually an archive by checking the ZIP magic bytes.
    return response.status_code == 200 and response.content[:2] == b"PK"


def _discover_from_page(client: httpx.Client) -> Optional[CreaRelease]:
    """Follow the download button on the HPI tool page. None if it yields nothing."""
    try:
        page = get_bytes(client, HPI_TOOL_PAGE_URL)
    except Exception as exc:  # noqa: BLE001
        logger.warning("CREA HPI tool page fetch failed: %s", exc)
        return None
    if page.status_code != 200:
        logger.warning("CREA HPI tool page returned HTTP %d", page.status_code)
        return None
    links = extract_zip_links(page.text)
    if not links:
        logger.warning(
            "CREA HPI tool page has no MLS_HPI_*.zip link (layout changed?): %s",
            HPI_TOOL_PAGE_URL,
        )
        return None
    for url, label in links:
        try:
            r = get_bytes(client, url)
        except Exception as exc:  # noqa: BLE001
            logger.warning("CREA ZIP linked from page failed to download (%s): %s", url, exc)
            continue
        if _is_zip(r):
            return CreaRelease(r.content, label, url, _published_date(r), "page")
        logger.warning("CREA ZIP linked from page is not a ZIP (HTTP %d): %s", r.status_code, url)
    return None


def _discover_by_guess(
    client: httpx.Client, today: date, lookback: int
) -> tuple[Optional[CreaRelease], list[str], Optional[Exception]]:
    """Walk back month by month, newest first, trying every known spelling."""
    tried: list[str] = []
    last_error: Optional[Exception] = None
    for offset in range(lookback + 1):
        ref = pd.Timestamp(today) - pd.DateOffset(months=offset)
        for label in month_label_variants(ref.year, ref.month):
            url = release_url_for(label)
            tried.append(url)
            try:
                r = get_bytes(client, url)
            except Exception as exc:  # noqa: BLE001
                last_error = exc
                logger.warning("CREA fetch attempt failed for %s: %s", label, exc)
                continue
            if _is_zip(r):
                release = CreaRelease(r.content, label, url, _published_date(r), "dated-url-guess")
                return release, tried, last_error
    return None, tried, last_error


def find_available_release(today: Optional[date] = None, *, lookback: int = 4) -> CreaRelease:
    """Locate and download the current CREA MLS HPI ZIP.

    Page-first: read the download link off the HPI tool page. If the page is
    unreachable or carries no usable link, fall back to guessing dated URLs
    from today back through `lookback` months, trying every known month
    spelling.

    Finding a ZIP is not proof it is current; callers must run
    `check_release_freshness()` on the parsed data. Raises FileNotFoundError
    if neither path yields a ZIP.
    """
    today = today or date.today()
    # The shared client advertises Accept: application/json; the page is HTML.
    with get_client(headers={"Accept": "text/html,application/zip,*/*"}) as client:
        release = _discover_from_page(client)
        if release is not None:
            logger.info("CREA release found via page: %s (%s)", release.label, release.url)
            return release
        logger.warning("CREA page discovery failed; falling back to dated-URL guess")
        release, tried, last_error = _discover_by_guess(client, today, lookback)
        if release is not None:
            logger.info("CREA release found via dated-URL guess: %s", release.label)
            return release
    raise FileNotFoundError(
        f"No CREA MLS HPI ZIP found. Page {HPI_TOOL_PAGE_URL} yielded no usable link "
        f"and no dated URL resolved in the last {lookback + 1} months. "
        f"Tried: {tried}. Last error: {last_error!r}"
    )


# --------------------------------------------------------------------------- #
# Freshness guard
# --------------------------------------------------------------------------- #

def reference_lag_months(latest_reference: date, today: date) -> int:
    """Whole calendar months between the latest reference month and today."""
    return (today.year - latest_reference.year) * 12 + (today.month - latest_reference.month)


def check_release_freshness(
    latest_reference: date, *, today: Optional[date] = None, label: str = ""
) -> int:
    """Raise CreaStaleReleaseError if the data is two or more release cycles old.

    `latest_reference` is the last reference month with a value in the
    workbook, not the filename label: a ZIP that merely exists is exactly
    what went unnoticed in 2026. Returns the lag in months and logs a WARNING
    at one missed cycle.
    """
    today = today or date.today()
    lag = reference_lag_months(latest_reference, today)
    if lag > MAX_REFERENCE_LAG_MONTHS:
        raise CreaStaleReleaseError(
            f"CREA MLS HPI is stale: newest ZIP found ({label or 'unknown label'}) ends at "
            f"reference month {latest_reference:%Y-%m}, {lag} months behind {today.isoformat()} "
            f"(normal is 1-2, tolerated {MAX_REFERENCE_LAG_MONTHS}). CREA has probably changed "
            f"the download URL or filename scheme again; check {HPI_TOOL_PAGE_URL}. "
            "Do not widen the lookback."
        )
    if lag >= WARN_REFERENCE_LAG_MONTHS:
        logger.warning(
            "CREA MLS HPI release %s ends at %s, %d months behind today; one release "
            "looks late or missed. The build will fail if it slips another month.",
            label, f"{latest_reference:%Y-%m}", lag,
        )
    return lag


# --------------------------------------------------------------------------- #
# Workbook parsing
# --------------------------------------------------------------------------- #

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

    missing = [c for c in ("Composite_HPI_SA", "Composite_Benchmark_SA") if c not in raw.columns]
    if missing:
        raise ValueError(
            f"CREA sheet {sheet_name!r} missing column(s) {missing}; got {list(raw.columns)}"
        )

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


def latest_reference_month(result: CreaFetchResult) -> date:
    """Last reference month carrying a non-null HPI value for this geography."""
    valued = result.data.dropna(subset=["value"])
    if valued.empty:
        raise ValueError(f"CREA sheet {result.sheet_name!r} has no HPI values")
    return pd.Timestamp(valued["date"].max()).date()
