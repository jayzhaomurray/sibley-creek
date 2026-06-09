"""Market-implied policy path from three-month CORRA futures (Montreal Exchange).

The shadow-rate tool produces a RULE-implied path (ToTEM III on MPR projections).
This module produces the contemporaneous MARKET-implied path, scraped from the
Montreal Exchange three-month CORRA futures quote table (symbol CRA). The two are
the interesting object to compare: the MPR forecast is itself conditioned on a
market-implied rate path, so rule-vs-market divergence isolates the part of the
rule's prescription that the market is NOT already pricing.

Pipeline
--------
1.  Scrape https://www.m-x.ca/en/trading/data/quotes?symbol=CRA — a plain HTML
    table, one row per quarterly contract month (Mar/Jun/Sep/Dec), out to
    ~Dec 2028. Columns: Month, Bid, Ask, Settl. price, Net change, Open int., Vol.
    One polite request via the repo's shared httpx client.

2.  Implied 3-month CORRA for a contract = 100 - settlement price (standard
    IMM 100-minus-rate quote convention).

3.  Contract-month -> reference-quarter mapping. A three-month CORRA future
    references the compounding window that BEGINS at the contract month's IMM
    date and runs ~three months forward (a "March 2026" future compounds CORRA
    from mid-March to mid-June 2026). We therefore map the contract to the
    calendar quarter that BEGINS at the contract month:

        March  YYYY -> YYYY Q2   (Apr-Jun, the window the Mar contract covers)
        June   YYYY -> YYYY Q3
        Sept   YYYY -> YYYY Q4
        Dec    YYYY -> (YYYY+1) Q1

    This aligns the futures-implied rate with the quarter over which it is the
    prevailing overnight rate, which is the quarter the shadow path also labels.

4.  CORRA -> target-rate adjustment. CORRA is an overnight *funding* rate that
    trades a few bp around the Bank's target for the overnight rate. We estimate
    a constant spread = mean(CORRA_daily - overnight_target) over the trailing
    60 business days (Valet AVG.INTWO daily CORRA vs the processed overnight
    target series), and define:

        implied_target = implied_corra - spread

    Typical spread magnitude is small (~ -5 to 0 bp; CORRA usually sits at or a
    hair above target). Documented in the methodology note.

5.  Output: data/raw/corra_futures_curve.csv (+ .meta.json sidecar, ADR-0002
    style) and a MarketPath dataclass for charting / stdout.

Graceful failure: ANY scrape or fetch error returns None with a one-line
warning. Nothing downstream breaks — the chart simply omits the market line and
run.py prints a skip notice.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Optional

import pandas as pd
from bs4 import BeautifulSoup

from pipeline.fetch._http import get_client, get_text
from pipeline.io import SeriesMeta, write_series

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).parents[2]

CRA_QUOTES_URL = "https://www.m-x.ca/en/trading/data/quotes?symbol=CRA"
CORRA_VALET_KEY = "AVG.INTWO"  # daily CORRA; see pipeline/catalog/boc_series.py
OVERNIGHT_TARGET_CSV = (
    PROJECT_ROOT / "data" / "processed" / "overnight_rate_target.csv"
)
OUT_DIR = PROJECT_ROOT / "data" / "raw"
OUT_NAME = "corra_futures_curve"

SPREAD_WINDOW_DAYS = 60  # trailing business days for the CORRA-minus-target mean

# Contract-month name -> month number. The CRA table prints full month names.
_MONTHS = {
    "january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6,
    "july": 7, "august": 8, "september": 9, "october": 10, "november": 11,
    "december": 12,
}


@dataclass(frozen=True)
class MarketContract:
    """One quarterly CORRA-futures contract, converted to an implied policy rate."""

    contract: str        # e.g. "March 2026" (as printed on the exchange)
    quarter: str         # reference quarter 'YYYYQn' (see module mapping)
    settlement: float    # exchange settlement price
    implied_corra: float # 100 - settlement
    implied_target: float  # implied_corra - spread


@dataclass(frozen=True)
class MarketPath:
    """The full market-implied policy path plus the spread adjustment used."""

    contracts: list[MarketContract]
    spread: float            # mean(CORRA - target) over the trailing window, in %
    spread_window_days: int
    fetched_at: str

    def by_quarter(self) -> dict[str, float]:
        """quarter 'YYYYQn' -> implied target rate (%)."""
        return {c.quarter: c.implied_target for c in self.contracts}


# --------------------------------------------------------------------------- #
# Pure helpers (unit-tested directly)
# --------------------------------------------------------------------------- #
def implied_corra_from_settlement(settlement: float) -> float:
    """3-month CORRA implied by an IMM-quoted futures settlement = 100 - price."""
    return 100.0 - settlement


def contract_to_quarter(contract_month: int, contract_year: int) -> str:
    """Map a contract month/year to the calendar quarter it covers, 'YYYYQn'.

    A three-month CORRA future references the compounding window beginning at the
    contract month's IMM date. We assign it the calendar quarter that begins at
    that month:

        Mar -> Q2,  Jun -> Q3,  Sep -> Q4,  Dec -> Q1 (of the next year)

    Non-quarterly months are tolerated (rounded to their own calendar quarter)
    but the CRA listings are quarterly in practice.
    """
    # The window begins ~at the contract month; the covered quarter is the one
    # starting one month after the IMM month (Mar IMM -> Apr-Jun = Q2).
    start_month = contract_month + 1
    year = contract_year
    if start_month > 12:
        start_month -= 12
        year += 1
    qn = (start_month - 1) // 3 + 1
    return f"{year}Q{qn}"


def parse_cra_table(html: str) -> list[tuple[str, float]]:
    """Parse the CRA quotes HTML -> list of (contract_label, settlement_price).

    Reads the single quotes table, keys columns off the header row so a column
    re-order upstream does not silently mis-read, and skips any row whose
    settlement cell is blank or non-numeric.
    """
    soup = BeautifulSoup(html, "lxml")
    table = soup.find("table")
    if table is None:
        raise ValueError("no <table> found on the CRA quotes page")

    headers = [th.get_text(strip=True).lower() for th in table.select("thead th")]
    if not headers:
        raise ValueError("CRA quotes table has no header row")

    def _col(*needles: str) -> int:
        for i, h in enumerate(headers):
            if all(n in h for n in needles):
                return i
        raise ValueError(f"CRA table missing a column matching {needles}; got {headers}")

    month_i = _col("month")
    settl_i = _col("settl")

    out: list[tuple[str, float]] = []
    for tr in table.select("tbody tr"):
        cells = [td.get_text(strip=True) for td in tr.find_all(["td", "th"])]
        if len(cells) <= max(month_i, settl_i):
            continue
        label = cells[month_i]
        raw = cells[settl_i].replace(",", "")
        try:
            settlement = float(raw)
        except (TypeError, ValueError):
            continue
        if not label:
            continue
        out.append((label, settlement))

    if not out:
        raise ValueError("CRA quotes table parsed but yielded no contract rows")
    return out


def _label_to_month_year(label: str) -> Optional[tuple[int, int]]:
    """'March 2026' -> (3, 2026). Returns None on an unrecognized label."""
    parts = label.strip().split()
    if len(parts) < 2:
        return None
    month = _MONTHS.get(parts[0].lower())
    try:
        year = int(parts[-1])
    except ValueError:
        return None
    if month is None:
        return None
    return month, year


def compute_spread(
    corra: pd.DataFrame,
    target: pd.DataFrame,
    window_days: int = SPREAD_WINDOW_DAYS,
) -> float:
    """Mean(CORRA - overnight target) over the trailing ``window_days`` obs, in %.

    ``corra`` and ``target`` are long frames with columns (date, value). The
    target series is monthly/step (constant between FAD changes); we forward-fill
    it onto the CORRA daily dates, take the last ``window_days`` CORRA obs, and
    average the difference. A positive result means CORRA traded above target.
    """
    c = corra[["date", "value"]].copy()
    t = target[["date", "value"]].copy()
    c["date"] = pd.to_datetime(c["date"], errors="coerce")
    t["date"] = pd.to_datetime(t["date"], errors="coerce")
    c = c.dropna(subset=["date"]).sort_values("date")
    t = t.dropna(subset=["date"]).sort_values("date")
    if c.empty or t.empty:
        raise ValueError("empty CORRA or target series for spread computation")

    merged = pd.merge_asof(
        c, t, on="date", direction="backward", suffixes=("_corra", "_target")
    )
    merged = merged.dropna(subset=["value_target"])
    if merged.empty:
        raise ValueError("no overlapping CORRA/target dates for spread computation")

    tail = merged.tail(window_days)
    return float((tail["value_corra"] - tail["value_target"]).mean())


# --------------------------------------------------------------------------- #
# Orchestration
# --------------------------------------------------------------------------- #
def _fetch_cra_html() -> str:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "macro-research-department/0.1 (+https://github.com/jayzhaomurray/macro-research-department)"
        ),
        "Accept": "text/html,application/xhtml+xml",
        "Accept-Language": "en-CA,en;q=0.9",
    }
    with get_client(headers=headers) as client:
        return get_text(client, CRA_QUOTES_URL)


def _fetch_spread() -> float:
    """Compute the CORRA-minus-target spread from Valet CORRA + processed target."""
    from pipeline.fetch import boc  # local import keeps module import side-effect-free

    corra = boc.fetch_series(CORRA_VALET_KEY, start_date="2025-01-01").data
    target = pd.read_csv(OVERNIGHT_TARGET_CSV)
    return compute_spread(corra, target, window_days=SPREAD_WINDOW_DAYS)


def fetch_market_path(write: bool = True) -> Optional[MarketPath]:
    """Fetch + build the market-implied policy path. Returns None on any failure.

    Args:
        write: if True (default), persist data/raw/corra_futures_curve.csv and its
            .meta.json sidecar. Set False for dry/test contexts.

    Returns:
        A MarketPath, or None if the scrape / spread fetch / parse failed (a
        one-line warning is printed; nothing downstream breaks).
    """
    try:
        html = _fetch_cra_html()
        rows = parse_cra_table(html)
        spread = _fetch_spread()
    except Exception as exc:  # noqa: BLE001 — graceful degradation is the contract
        print(f"WARNING: market-implied path unavailable ({type(exc).__name__}: {exc}); "
              f"chart will render without it.")
        logger.warning("market path fetch failed: %s", exc, exc_info=True)
        return None

    contracts: list[MarketContract] = []
    for label, settlement in rows:
        my = _label_to_month_year(label)
        if my is None:
            continue
        month, year = my
        quarter = contract_to_quarter(month, year)
        implied_corra = implied_corra_from_settlement(settlement)
        contracts.append(
            MarketContract(
                contract=label,
                quarter=quarter,
                settlement=settlement,
                implied_corra=round(implied_corra, 4),
                implied_target=round(implied_corra - spread, 4),
            )
        )

    if not contracts:
        print("WARNING: market-implied path: no usable contracts after parsing; "
              "chart will render without it.")
        return None

    fetched_at = datetime.now(timezone.utc).isoformat()
    path = MarketPath(
        contracts=contracts,
        spread=round(spread, 6),
        spread_window_days=SPREAD_WINDOW_DAYS,
        fetched_at=fetched_at,
    )

    if write:
        try:
            _write_curve(path)
        except Exception as exc:  # noqa: BLE001
            logger.warning("market path write failed: %s", exc, exc_info=True)
            print(f"WARNING: could not write {OUT_NAME}.csv ({exc}); "
                  "in-memory path still returned.")

    return path


def _write_curve(path: MarketPath) -> None:
    df = pd.DataFrame(
        {
            "contract": [c.contract for c in path.contracts],
            "quarter": [c.quarter for c in path.contracts],
            "settlement": [c.settlement for c in path.contracts],
            "implied_corra": [c.implied_corra for c in path.contracts],
            "implied_target": [c.implied_target for c in path.contracts],
            "fetched_at": [path.fetched_at for _ in path.contracts],
        }
    )
    meta = SeriesMeta(
        name=OUT_NAME,
        source="Montreal Exchange (TMX) — three-month CORRA futures (symbol CRA)",
        source_url=CRA_QUOTES_URL,
        source_id="TMX CRA quotes table; CORRA daily AVG.INTWO (BoC Valet)",
        units="%",
        frequency="quarterly",
        fetched_at=path.fetched_at,
        notes=(
            "Market-implied policy path. implied_corra = 100 - settlement; "
            f"implied_target = implied_corra - spread, where spread = "
            f"{path.spread:+.4f}% = mean(CORRA - overnight target) over the "
            f"trailing {path.spread_window_days} business days "
            "(Valet AVG.INTWO vs data/processed/overnight_rate_target.csv). "
            "Contract month -> reference quarter: the quarter beginning at the "
            "contract month (Mar->Q2, Jun->Q3, Sep->Q4, Dec->next-year Q1)."
        ),
        transform="corra_futures_implied_policy_path",
    )
    # The curve is keyed by reference quarter, not a calendar date; point the
    # period-derivation at the fetched_at timestamp so write_series doesn't try
    # to parse '2026Q2' as a date (and emit a noisy fallback warning).
    write_series(df, meta, OUT_DIR, date_col="fetched_at")
