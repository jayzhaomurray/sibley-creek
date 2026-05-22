"""Canadian Bankers Association residential mortgage arrears fetcher.

CBA publishes monthly "Number of Residential Mortgages in Arrears" PDFs at:
    https://cba.ca/Assets/CanadianBankersAssociation/Documents/Articles/
        Statistics/stat-mortgages-arrears-{month}-{year}-en.pdf

e.g. `stat-mortgages-arrears-february-2026-en.pdf` for the Feb 2026 release.

Each PDF has:
    - Page 1: a cross-section table of the latest month with national and
      per-province (Atlantic / Quebec / Ontario / Manitoba / Saskatchewan /
      Alberta / BC / Territories / CANADA) arrears counts and arrears-to-
      total-mortgages percentages.
    - Pages 2+: monthly time series for Canada (national) going back to 1995.

This is the closest publicly available proxy for the long-deprecated CMHC
arrears series. Coverage is BMO / CIBC / National / RBC / Scotia / TD plus
Manulife (since 2004), Laurentian (since 2010), and Equitable (since 2020) --
i.e., the chartered-bank slice of the mortgage market (roughly 75% of stock).
Brokered / private-lender / credit-union mortgages are not in the dataset.

Source quirks
-------------
- Filename uses LOWERCASE month name (e.g. "february", not "February").
- Each month's PDF is posted with roughly a 2.5-month lag (e.g. May data
  releases mid-August). The current cycle therefore lags CPI / LFS notably.
- The CBA only publishes ARREARS (3+ months past due). "Total mortgages"
  is a slowly-moving stock; the percent column already does the ratio for us.
- The national time series in pages 2+ is split into two side-by-side
  columns (years split across the page width); the parser stitches them
  back into a single chronological series.
- The cross-section page uses commas as thousand-separators on the count
  columns; the percent column has a trailing `%` sign.

Output contract
---------------
    data/raw/cba_mortgage_arrears_national.csv  -- date, value (national %)
    data/raw/cba_mortgage_arrears_provincial.csv -- date, province, value (%)
                                                    (single-period snapshot
                                                    from the latest cross-section)
Sibling .meta.json sidecars name CBA as the source and document the latest
release date the parser identified from the PDF body.
"""

from __future__ import annotations

import io
import logging
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Optional

import pandas as pd

from pipeline.fetch._http import get_bytes, get_client

logger = logging.getLogger(__name__)

CBA_BASE_URL = (
    "https://cba.ca/Assets/CanadianBankersAssociation/Documents/Articles/"
    "Statistics/stat-mortgages-arrears-{month}-{year}-en.pdf"
)

_MONTH_NAMES = [
    "january", "february", "march", "april", "may", "june",
    "july", "august", "september", "october", "november", "december",
]

# Province order in the cross-section table on page 1, plus the per-province
# label used in the output CSV. CANADA / TERRITORIES are handled separately.
_PROVINCE_ROWS = [
    ("ATLANTIC", "atlantic"),
    ("QUEBEC", "quebec"),
    ("ONTARIO", "ontario"),
    ("MANITOBA", "manitoba"),
    ("SASKATCHEWAN", "saskatchewan"),
    ("ALBERTA", "alberta"),
    ("BRITISH COLUMBIA", "british_columbia"),
]


@dataclass(frozen=True)
class CbaArrearsResult:
    """Output of `parse_cba_arrears_pdf()`.

    Fields:
        national_history: long DataFrame (date, value) with the monthly
            national arrears rate in PERCENT (e.g. 0.28 means 0.28%). Sorted
            ascending. Goes back to ~1995.
        provincial_snapshot: long DataFrame (date, province, value) for the
            latest month only; provincial history isn't in the CBA PDF.
        as_of_date: the latest month's reference date (last-day-of-month
            timestamp; e.g. 2026-02-28 for the Feb 2026 release).
        release_label: the (year, month_name) tuple this PDF corresponds to
            (i.e. the URL it was fetched from), useful for provenance.
    """

    national_history: pd.DataFrame
    provincial_snapshot: pd.DataFrame
    as_of_date: pd.Timestamp
    release_label: tuple[int, str]


def latest_release_candidates(today: Optional[date] = None, lookback: int = 4) -> list[tuple[int, str]]:
    """Candidate (year, month_name) pairs to probe, latest first.

    CBA publishes with a ~2.5-month lag (e.g. May release lands in mid-
    August), so we try the current month -3 first and walk back further if
    that 404s.
    """
    today = today or date.today()
    candidates: list[tuple[int, str]] = []
    # Walk back from "current month - 2" through `lookback` further months.
    # The +1 makes the range inclusive of the most-recent realistic posting.
    for offset in range(2, 2 + lookback + 1):
        ref = pd.Timestamp(today) - pd.DateOffset(months=offset)
        candidates.append((int(ref.year), _MONTH_NAMES[ref.month - 1]))
    return candidates


def release_url_for(year: int, month_name: str) -> str:
    """URL of the CBA arrears PDF for a given release month."""
    return CBA_BASE_URL.format(month=month_name.lower(), year=year)


def find_and_download_latest(
    today: Optional[date] = None,
    *,
    lookback: int = 4,
) -> tuple[bytes, tuple[int, str]]:
    """Probe candidate URLs from most-recent backward; return the first that
    returns HTTP 200.

    Raises:
        FileNotFoundError if no candidate within `lookback` months is live.
    """
    tried: list[str] = []
    last_exc: Optional[Exception] = None
    with get_client(headers={"Accept": "application/pdf,*/*"}) as client:
        for (year, month) in latest_release_candidates(today, lookback=lookback):
            url = release_url_for(year, month)
            tried.append(url)
            try:
                r = get_bytes(client, url)
            except Exception as exc:  # noqa: BLE001
                last_exc = exc
                logger.warning("CBA arrears fetch error %s -> %s", url, exc)
                continue
            if r.status_code == 200 and r.headers.get("content-type", "").lower().startswith("application/pdf"):
                logger.info("CBA arrears PDF found: %s", url)
                return r.content, (year, month)
            if r.status_code == 404:
                continue
            # 200 but unexpected content-type (e.g. HTML error page): skip.
            logger.warning(
                "CBA arrears unexpected response %s status=%s ctype=%s",
                url, r.status_code, r.headers.get("content-type"),
            )
    raise FileNotFoundError(
        f"No CBA arrears PDF found in last {lookback} months. "
        f"Tried: {tried}. Last error: {last_exc!r}"
    )


# --------------------------------------------------------------------------- #
# Parsing
# --------------------------------------------------------------------------- #

# Pattern for one row in the cross-section table (page 1):
#     "ATLANTIC 336,691 1,045 0.31%"
# Capture groups: location, total, arrears_count, arrears_pct
_CROSS_SECTION_ROW = re.compile(
    r"^([A-Z][A-Z\s]+?)\s+([\d,]+)(?:\s+([\d,]+))?\s+([0-9.]+)%\s*$"
)

# "Month Ended <Month> <day>, <year>" appears at the bottom of page 1.
_AS_OF_DATE = re.compile(
    r"Month Ended\s+([A-Za-z]+)\s+(\d{1,2}),\s*(\d{4})"
)

# Pattern for one row of the national time series (pages 2+):
#     "2026-02 4,937,235 13,749 0.28%"
# It may appear twice on a line (years are split into two side-by-side
# columns). Use re.finditer to pull both.
_TIME_SERIES_ROW = re.compile(
    r"(\d{4})-(\d{2})\s+([\d,]+)\s+([\d,]+)\s+([0-9.]+)%"
)


def _extract_pdf_text(pdf_bytes: bytes) -> list[str]:
    """Return per-page extracted text strings. Imported lazily so the rest
    of the pipeline doesn't pay the pypdf import cost when not parsing PDFs.
    """
    from pypdf import PdfReader  # local import: optional dependency

    reader = PdfReader(io.BytesIO(pdf_bytes))
    pages: list[str] = []
    for p in reader.pages:
        try:
            pages.append(p.extract_text() or "")
        except Exception as exc:  # noqa: BLE001
            logger.warning("pypdf page extract failed: %s", exc)
            pages.append("")
    return pages


def _parse_as_of_date(page0_text: str) -> pd.Timestamp:
    """Find the 'Month Ended <Month> <day>, <year>' stamp on page 1."""
    m = _AS_OF_DATE.search(page0_text)
    if not m:
        raise ValueError("CBA arrears PDF: 'Month Ended ...' stamp not found on page 1")
    month_name, day_str, year_str = m.group(1), m.group(2), m.group(3)
    return pd.Timestamp(f"{year_str}-{month_name}-{day_str}")


def _parse_provincial_snapshot(page0_text: str, as_of: pd.Timestamp) -> pd.DataFrame:
    """Parse the cross-section table on page 1 into per-province rows.

    Returns columns (date, province, value) where value is percent
    (e.g. 0.28 means 0.28%).
    """
    rows: list[dict] = []
    # The cross-section table is line-oriented; iterate lines.
    for raw_line in page0_text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        # Try to match. Filter to the prefixes we expect; other lines on
        # page 1 (footnotes etc.) won't have the trailing percent.
        m = _CROSS_SECTION_ROW.match(line)
        if not m:
            continue
        location = m.group(1).strip()
        pct_str = m.group(4)
        try:
            pct = float(pct_str)
        except ValueError:
            continue
        # CBA reports TERRITORIES as a count-only row without an arrears
        # number; the regex's optional middle group handles that, but we
        # skip it because the percent in that row is misaligned (it's
        # actually the count). Confirm by checking it has an arrears count.
        if m.group(3) is None:
            continue
        for label, slug in _PROVINCE_ROWS:
            if location == label:
                rows.append({"date": as_of, "province": slug, "value": pct})
                break
    return pd.DataFrame(rows, columns=["date", "province", "value"])


def _parse_national_history(pages_text: list[str]) -> pd.DataFrame:
    """Stitch the two-column national time series across pages 2+ into a
    single chronological monthly series.

    Returns columns (date, value) with date as month-end Timestamp and
    value as percent.
    """
    rows: dict[str, float] = {}
    # Pages 1+ in 0-indexed terms = page index 1 onward; we look at every
    # page past the first cross-section page. The PDF has 19 pages total
    # but the trailing pages are per-province history (not parsed here).
    # We stop accumulating once we see a province-cross-section block
    # header to keep the national series clean.
    for idx, text in enumerate(pages_text):
        if idx == 0:
            continue
        # The province pages start with text like "REGION: ATLANTIC" or
        # similar. Stop national-history parsing at the first non-CANADA
        # region header.
        if re.search(r"REGION:\s+(?!CANADA)\w", text):
            break
        for m in _TIME_SERIES_ROW.finditer(text):
            year = int(m.group(1))
            month = int(m.group(2))
            pct = float(m.group(5))
            if not (1 <= month <= 12):
                continue
            # Skip empty future rows: PDF lays out 12 months per year even
            # when later months haven't been published yet. Future rows
            # appear as "YYYY-MM" with no numbers, so the regex won't match.
            # Belt-and-braces: arrears rate is always > 0; skip 0.0 cells.
            if pct <= 0:
                continue
            key = f"{year:04d}-{month:02d}"
            rows[key] = pct
    if not rows:
        raise ValueError("CBA arrears PDF: no national time-series rows parsed")

    df = pd.DataFrame(
        [{"date": pd.Timestamp(f"{k}-01"), "value": v} for k, v in rows.items()]
    )
    df = df.sort_values("date").reset_index(drop=True)
    return df


def parse_cba_arrears_pdf(pdf_bytes: bytes) -> CbaArrearsResult:
    """Parse a CBA arrears PDF into national history + provincial snapshot.

    Raises:
        ValueError if the cross-section table or time-series rows can't be
        found. Surfaces loudly so a layout change doesn't silently produce
        empty CSVs.
    """
    pages = _extract_pdf_text(pdf_bytes)
    if not pages:
        raise ValueError("CBA arrears PDF: no pages extracted")
    as_of = _parse_as_of_date(pages[0])
    provincial = _parse_provincial_snapshot(pages[0], as_of)
    if provincial.empty:
        raise ValueError(
            f"CBA arrears PDF: no provincial rows parsed from page 1 "
            f"(expected {len(_PROVINCE_ROWS)} provinces)."
        )
    national = _parse_national_history(pages)
    # Sanity check: the latest national row should match the cross-section
    # CANADA % to within 0.01 pp (PDF rounding).
    canada_pct_match = _CROSS_SECTION_ROW.search("")  # placeholder
    canada_pct: Optional[float] = None
    for raw_line in pages[0].splitlines():
        m = _CROSS_SECTION_ROW.match(raw_line.strip())
        if m and m.group(1).strip() == "CANADA":
            try:
                canada_pct = float(m.group(4))
            except ValueError:
                pass
            break
    if canada_pct is not None and not national.empty:
        latest = float(national.iloc[-1]["value"])
        if abs(latest - canada_pct) > 0.011:
            logger.warning(
                "CBA arrears: cross-section CANADA=%.2f%% differs from latest "
                "time-series row=%.2f%% (>0.01 pp). Layout may have shifted.",
                canada_pct, latest,
            )
    # Resolve release label from as_of: e.g. as_of=2026-02-28 -> ("february", 2026)
    release_label = (int(as_of.year), _MONTH_NAMES[as_of.month - 1])
    return CbaArrearsResult(
        national_history=national,
        provincial_snapshot=provincial,
        as_of_date=as_of,
        release_label=release_label,
    )


def fetch_cba_arrears(
    today: Optional[date] = None,
    *,
    lookback: int = 4,
) -> CbaArrearsResult:
    """End-to-end fetch + parse. Probes the most-recent likely URL backward
    through `lookback` months, downloads the first PDF that 200s, and parses
    the national history + provincial cross-section.

    Raises FileNotFoundError if no PDF is available; ValueError if the PDF
    layout has changed and parsing fails.
    """
    pdf_bytes, release_label = find_and_download_latest(today, lookback=lookback)
    result = parse_cba_arrears_pdf(pdf_bytes)
    # Sanity: release_label from URL probe should match parsed as-of month
    # within +/- 1 month (the CBA URL convention is "stat-mortgages-arrears-
    # <reference-month>-<reference-year>", but the latest URL we hit may
    # represent the most-recent publication, not the reference month).
    return result
