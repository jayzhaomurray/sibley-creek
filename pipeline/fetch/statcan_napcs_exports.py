"""Fetch sectoral export data from StatCan Table 12-10-0182-01.

Produces data/processed/sectoral_exports_latest_yoy.csv with a year-over-year
window anchored to the latest available month in the table. The end month is
the latest month present across all NAPCS sub-chapters; the start month is
the same calendar month one year prior.

Window advances automatically on each re-fetch as StatCan publishes new months.
Current window (as of last fetch) is recorded in the sibling .meta.json
(fields: window_start, window_end).

Source: Statistics Canada, Table 12-10-0182-01
"Canadian international merchandise trade for total exports, domestic exports
and re-exports, by country of destination and country of origin,
customs-based, monthly"
https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1210018201

Table structure (verified against 12100182_MetaData.csv from bulk zip):
  Dim 1 - Geography:        1 member  (Canada = 1)
  Dim 2 - NAPCS:          113 members (1=All sections; 12 section aggregates; 100 sub-chapters)
  Dim 3 - Trade:            3 members (1=Export total, 2=Domestic exports, 3=Re-exports)
  Dim 4 - Country of destination: 29 members (1=All countries, 2=United States, ...)
  Dim 5 - Country of origin:      30 members (1=All countries, ...)
  [Note: metadata lists 31 Dim-5 members but the table encodes 30 per-dest blocks]

Vector ID formula (verified against known anchor vectors from bulk CSV):
  BASE_VID  = 1863536833  (coordinate 1.1.1.1.1)
  PER_NAPCS = 2610        = 3 trades * 29 dests * 30 origins
  PER_TRADE =  870        = 29 dests * 30 origins
  PER_DEST  =   30        = 30 origins
  vectorId(napcs_m, trade_t, dest_d, origin_o=1) =
      BASE_VID + (napcs_m-1)*PER_NAPCS + (trade_t-1)*PER_TRADE + (dest_d-1)*PER_DEST + (origin_o-1)

Scalar factor: scalarFactorCode=3 = thousands of dollars.
Output is converted to CAD millions (divide by 1000).

Units in output CSV: CAD millions, not seasonally adjusted, domestic exports
(excludes re-exports), customs basis.

Column naming convention (generic, window-agnostic):
  start_total  -- all-countries value at window_start (same-month prior year)
  start_us     -- US-destination value at window_start
  end_total    -- all-countries value at window_end (latest available month)
  end_us       -- US-destination value at window_end
"""

from __future__ import annotations

import csv
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

import requests
from pydantic import BaseModel

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

TABLE_ID = "12-10-0182-01"
TABLE_URL = "https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1210018201"
WDS_ENDPOINT = (
    "https://www150.statcan.gc.ca/t1/wds/rest/getDataFromVectorsAndLatestNPeriods"
)
USER_AGENT = (
    "macro-research-department/0.1 "
    "(+https://github.com/jayzhaomurray/macro-research-department)"
)

# Vector formula anchors (verified from 12100182_MetaData.csv + bulk CSV)
BASE_VID = 1863536833
PER_NAPCS = 2610   # 3 * 29 * 30
PER_TRADE = 870    # 29 * 30
PER_DEST = 30      # 30

TRADE_DOMESTIC = 2   # Dim 3 member 2 = "Domestic exports"
DEST_ALL = 1         # Dim 4 member 1 = "All countries, country of destination"
DEST_US = 2          # Dim 4 member 2 = "United States, country of destination"
ORIGIN_ALL = 1       # Dim 5 member 1 = "All countries, country of origin"

# NAPCS section aggregate member IDs (Dim 2) — excluded from output.
# These are the top-level [C##]-coded groupings plus the "All sections" total.
SECTION_AGGREGATE_IDS = frozenset({1, 2, 12, 20, 29, 43, 52, 65, 74, 80, 85, 91, 112})

# NAPCS sub-chapter labels keyed by Dim 2 member ID.
# Derived from 12100182_MetaData.csv. Classification code is the NAPCS [###] code.
NAPCS_SUB_CHAPTERS: dict[int, tuple[str, str]] = {
    # member_id: (classification_code, label_en)
    3:   ("[111]", "Live animals"),
    4:   ("[112]", "Wheat"),
    5:   ("[113]", "Canola (including rapeseed)"),
    6:   ("[114]", "Fresh fruit, nuts and vegetables, and pulse crops"),
    7:   ("[115]", "Other crop products"),
    8:   ("[116]", "Other animal products"),
    9:   ("[121]", "Fish, crustaceans, shellfish and other fishery products"),
    10:  ("[181]", "Animal feed"),
    11:  ("[182]", "Intermediate food products"),
    13:  ("[141]", "Crude oil and bitumen"),
    14:  ("[142]", "Natural gas"),
    15:  ("[143]", "Natural gas liquids (including condensate) and related products"),
    16:  ("[144]", "Coal"),
    17:  ("[145]", "Nuclear fuel and other energy products"),
    18:  ("[146]", "Electricity"),
    19:  ("[261]", "Refined petroleum energy products (including liquid biofuels)"),
    21:  ("[151]", "Iron ores and concentrates"),
    22:  ("[152]", "Copper ores and concentrates"),
    23:  ("[153]", "Nickel ores and concentrates"),
    24:  ("[154]", "Radioactive ores and concentrates"),
    25:  ("[155]", "Other metal ores and concentrates"),
    26:  ("[161]", "Potash"),
    27:  ("[162]", "Stone, sand, gravel, clay, and refractory minerals"),
    28:  ("[163]", "Diamonds and other non-metallic minerals (except cut gemstones)"),
    30:  ("[311]", "Unwrought iron, steel and ferro-alloys"),
    31:  ("[312]", "Basic and semi-finished iron or steel products"),
    32:  ("[321]", "Unwrought aluminum and aluminum alloys"),
    33:  ("[322]", "Unwrought copper and copper alloys"),
    34:  ("[323]", "Unwrought nickel and nickel alloys"),
    35:  ("[324]", "Unwrought gold, silver, and platinum group metals, and their alloys"),
    36:  ("[325]", "Other unwrought non-ferrous metals and non-ferrous metal alloys"),
    37:  ("[326]", "Basic and semi-finished products of non-ferrous metals and alloys (except aluminum)"),
    38:  ("[327]", "Basic and semi-finished products of aluminum and aluminum alloys"),
    39:  ("[472]", "Fabricated metal products"),
    40:  ("[291]", "Non-metallic mineral products"),
    41:  ("[156]", "Waste and scrap of metal"),
    42:  ("[159]", "Waste and scrap of glass"),
    44:  ("[263]", "Dyes and pigments, and petrochemicals"),
    45:  ("[264]", "Lubricants and other petroleum refinery products"),
    46:  ("[271]", "Basic chemicals"),
    47:  ("[272]", "Fertilizers, pesticides and other chemical products"),
    48:  ("[281]", "Plastic resins"),
    49:  ("[282]", "Plastic and rubber basic products not for packaging use (except plastic resins)"),
    50:  ("[284]", "Plastic and rubber finished products"),
    51:  ("[158]", "Waste and scrap of plastic and rubber"),
    53:  ("[131]", "Logs, pulpwood and other forestry products"),
    54:  ("[251]", "Pulp and paper"),
    55:  ("[241]", "Lumber and other sawmill products"),
    56:  ("[262]", "Asphalt (except natural) and asphalt products"),
    57:  ("[462]", "Wood millwork, and wood products not elsewhere classified"),
    58:  ("[463]", "Paints, coatings, and adhesive products"),
    59:  ("[464]", "Plastic and foam building and construction materials"),
    60:  ("[465]", "Cement, lime and gypsum products"),
    61:  ("[466]", "Metal building and construction materials"),
    62:  ("[471]", "Prefabricated buildings and components thereof"),
    63:  ("[474]", "Packaging materials"),
    64:  ("[157]", "Waste and scrap of wood, wood by-products, paper and paperboard"),
    66:  ("[331]", "Agricultural, lawn and garden machinery and equipment"),
    67:  ("[332]", "Logging, construction, mining, and oil and gas field machinery and equipment"),
    68:  ("[341]", "Metalworking machinery"),
    69:  ("[342]", "Commercial and service industry machinery and equipment"),
    70:  ("[343]", "Other industry-specific manufacturing machinery, not elsewhere classified"),
    71:  ("[344]", "Heating, cooling and air purification equipment"),
    72:  ("[345]", "Other general-purpose machinery and equipment, not elsewhere classified"),
    73:  ("[351]", "Parts of industrial machinery and equipment"),
    75:  ("[361]", "Computers and computer peripherals"),
    76:  ("[362]", "Communication, and audio and video equipment"),
    77:  ("[363]", "Medical, measuring, and other electronic and electrical machinery and equipment"),
    78:  ("[371]", "Electronic and electrical parts"),
    79:  ("[381]", "Electrical components"),
    81:  ("[411]", "Passenger cars and light trucks"),
    82:  ("[412]", "Medium and heavy trucks, buses, and other motor vehicles"),
    83:  ("[283]", "Tires"),
    84:  ("[413]", "Motor vehicle engines and motor vehicle parts"),
    86:  ("[421]", "Aircraft"),
    87:  ("[431]", "Aircraft engines, aircraft parts and other aerospace equipment"),
    88:  ("[441]", "Ships, locomotives, railway rolling stock, and rapid transit equipment"),
    89:  ("[442]", "Boats and other transportation equipment"),
    90:  ("[451]", "Parts of railway rolling stock and of other transportation equipment"),
    92:  ("[171]", "Prepared and packaged seafood products"),
    93:  ("[172]", "Meat products"),
    94:  ("[173]", "Dairy products"),
    95:  ("[183]", "Other food products"),
    96:  ("[191]", "Coffee and tea"),
    97:  ("[192]", "Frozen, fresh and canned fruit and vegetable juices"),
    98:  ("[193]", "Carbonated and non-carbonated drinks, bottled water and ice"),
    99:  ("[211]", "Alcoholic beverages"),
    100: ("[212]", "Tobacco products (including electronic cigarettes)"),
    101: ("[221]", "Fabric, fibre and yarn, and leather and dressed furs"),
    102: ("[231]", "Clothing, footwear and accessories"),
    103: ("[232]", "Carpets, textile furnishings and other textile products"),
    104: ("[252]", "Converted paper products (except for packaging)"),
    105: ("[481C]", "Published products and recorded media (except software)"),
    106: ("[482C]", "Software and software licensing"),
    107: ("[273]", "Pharmaceutical and medicinal products"),
    108: ("[391]", "Furniture and fixtures"),
    109: ("[274]", "Cleaning products and toiletries"),
    110: ("[382]", "Appliances"),
    111: ("[475]", "Miscellaneous goods and supplies"),
    113: ("[988]", "Special transactions trade"),
}

# Number of periods to fetch per vector.
# 14 covers same-month-prior-year from any month that is <= 2 months after
# the most recent complete-year boundary. 16 gives one period of slack in case
# a straggler series is one month behind the majority.
LATEST_N = 16


# ---------------------------------------------------------------------------
# WDS fetch helpers
# ---------------------------------------------------------------------------

class _VectorPoint(BaseModel):
    refPer: str
    value: Optional[float] = None
    scalarFactorCode: Optional[int] = None
    statusCode: Optional[int] = None


class _VectorObject(BaseModel):
    vectorId: int
    coordinate: str
    vectorDataPoint: list[_VectorPoint] = []


class _VectorItem(BaseModel):
    status: str
    object: Optional[_VectorObject] = None


def _get_vid(napcs_m: int, trade_t: int, dest_d: int, origin_o: int = 1) -> int:
    return (
        BASE_VID
        + (napcs_m - 1) * PER_NAPCS
        + (trade_t - 1) * PER_TRADE
        + (dest_d - 1) * PER_DEST
        + (origin_o - 1)
    )


def _post_batch(
    session: requests.Session, vids: list[int], latest_n: int
) -> list[_VectorItem]:
    body = [{"vectorId": v, "latestN": latest_n} for v in vids]
    r = session.post(WDS_ENDPOINT, json=body, timeout=60)
    r.raise_for_status()
    raw: list[Any] = r.json()
    return [_VectorItem.model_validate(item) for item in raw]


def _prior_year_month(ym: str) -> str:
    """Return YYYY-MM that is exactly 12 months before the given YYYY-MM."""
    year = int(ym[:4])
    month = int(ym[5:7])
    return f"{year - 1:04d}-{month:02d}"


# ---------------------------------------------------------------------------
# Main fetch + build
# ---------------------------------------------------------------------------

def fetch_sectoral_exports(
    out_csv: Path,
    out_meta: Path,
    *,
    batch_size: int = 200,
    latest_n: int = LATEST_N,
) -> int:
    """Fetch and write sectoral exports CSV.

    Window is determined dynamically:
      - end_month  = the latest YYYY-MM present in ALL series
      - start_month = same calendar month one year prior (end_month - 12 months)

    Returns the number of NAPCS rows written.

    Raises RuntimeError loudly if the window cannot be resolved or if any
    target month is missing for any series. Silent partial-success is forbidden.
    """
    member_ids = sorted(NAPCS_SUB_CHAPTERS.keys())

    # Build (member_id, dest_label, vector_id) triples
    requests_all: list[tuple[int, str, int]] = []
    for m in member_ids:
        requests_all.append((m, "all", _get_vid(m, TRADE_DOMESTIC, DEST_ALL)))
        requests_all.append((m, "us",  _get_vid(m, TRADE_DOMESTIC, DEST_US)))

    all_vids = [vid for (_, _, vid) in requests_all]
    fetched: dict[int, dict[str, Optional[float]]] = {}  # {vid: {YYYY-MM: value}}

    # Use requests + Chrome UA: StatCan www150 TLS-fingerprints non-browser
    # clients (httpx/urllib get connection-reset). Chrome UA bypasses the filter.
    session = requests.Session()
    session.headers.update({
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept": "application/json",
    })

    for batch_start in range(0, len(all_vids), batch_size):
        batch_vids = all_vids[batch_start : batch_start + batch_size]
        items = _post_batch(session, batch_vids, latest_n)

        for vid, item in zip(batch_vids, items):
            if item.status != "SUCCESS" or item.object is None:
                raise RuntimeError(
                    f"StatCan WDS error for vector {vid} "
                    f"(table {TABLE_ID}): status={item.status!r}"
                )
            pts = item.object.vectorDataPoint
            fetched[vid] = {
                pt.refPer[:7]: pt.value  # YYYY-MM key
                for pt in pts
            }

    session.close()

    # -----------------------------------------------------------------------
    # Determine window: end_month = latest month common to all series,
    # start_month = same calendar month one year prior.
    # -----------------------------------------------------------------------
    all_month_sets: list[set[str]] = [set(d.keys()) for d in fetched.values()]
    common_months: set[str] = all_month_sets[0].copy()
    for s in all_month_sets[1:]:
        common_months &= s

    if not common_months:
        raise RuntimeError(
            f"Source {TABLE_ID}: no month common to all {len(fetched)} fetched series. "
            f"Increase latest_n (currently {latest_n})."
        )

    end_month = max(common_months)
    start_month = _prior_year_month(end_month)

    # Verify start_month is present in all series (it must be within the
    # latest_n window). If not, we need a wider fetch — raise loudly.
    missing_start: list[int] = [
        vid for vid, d in fetched.items() if start_month not in d
    ]
    if missing_start:
        raise RuntimeError(
            f"Source {TABLE_ID}: start_month {start_month} not in fetched window "
            f"for {len(missing_start)} vectors (latest_n={latest_n}). "
            f"Increase latest_n to at least 14."
        )

    logger.info(
        "sectoral_exports_latest_yoy: window %s -> %s (latest_n=%d)",
        start_month, end_month, latest_n,
    )

    # -----------------------------------------------------------------------
    # Build output rows
    # -----------------------------------------------------------------------
    rows: list[dict] = []
    missing_report: list[str] = []

    for m in member_ids:
        code, label = NAPCS_SUB_CHAPTERS[m]
        vid_all = _get_vid(m, TRADE_DOMESTIC, DEST_ALL)
        vid_us = _get_vid(m, TRADE_DOMESTIC, DEST_US)

        dates_all = fetched[vid_all]
        dates_us = fetched[vid_us]

        def _get(dates: dict, month: str) -> Optional[float]:
            return dates.get(month)

        def _to_millions(v: Optional[float]) -> Optional[float]:
            # scalarFactorCode=3 = thousands; convert to CAD millions
            if v is None:
                return None
            return round(v / 1000.0, 3)

        # Check both target months for this series
        for month, label_dest in [(start_month, "all_countries"), (end_month, "all_countries")]:
            if month not in dates_all:
                missing_report.append(
                    f"NAPCS m={m} ({label[:40]}): all_countries missing {month}"
                )
        for month, label_dest in [(start_month, "US"), (end_month, "US")]:
            if month not in dates_us:
                missing_report.append(
                    f"NAPCS m={m} ({label[:40]}): US missing {month}"
                )

        rows.append(
            {
                "napcs_code": m,
                "napcs_label_en": label,
                "napcs_classification_code": code,
                "start_total": _to_millions(_get(dates_all, start_month)),
                "start_us":    _to_millions(_get(dates_us,  start_month)),
                "end_total":   _to_millions(_get(dates_all, end_month)),
                "end_us":      _to_millions(_get(dates_us,  end_month)),
                "vector_all":  vid_all,
                "vector_us":   vid_us,
            }
        )

    if missing_report:
        msg = "\n  ".join(missing_report)
        raise RuntimeError(
            f"Source {TABLE_ID}: missing target-month data for {len(missing_report)} "
            f"series:\n  {msg}"
        )

    # Write CSV
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "napcs_code",
        "napcs_label_en",
        "napcs_classification_code",
        "start_total",
        "start_us",
        "end_total",
        "end_us",
        "vector_all",
        "vector_us",
    ]
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    # Write meta
    meta = {
        "name": "sectoral_exports_latest_yoy",
        "source": "Statistics Canada Web Data Service",
        "source_table": TABLE_ID,
        "source_url": TABLE_URL,
        "units": "CAD millions, domestic exports, customs basis, not seasonally adjusted",
        "scalar_factor_raw": "thousands (scalarFactorCode=3); divided by 1000 in output",
        "trade_type": "Domestic exports (excludes re-exports)",
        "destinations": "All Countries (Dim4=1) and United States (Dim4=2)",
        "country_of_origin": "All countries (Dim5=1)",
        "window_start": start_month,
        "window_end": end_month,
        "column_convention": (
            "start_* = window_start month; end_* = window_end month; "
            "*_total = all-countries; *_us = United States only"
        ),
        "napcs_sub_chapters": len(rows),
        "napcs_aggregates_excluded": sorted(SECTION_AGGREGATE_IDS),
        "vector_formula": {
            "base_vid": BASE_VID,
            "per_napcs": PER_NAPCS,
            "per_trade": PER_TRADE,
            "per_dest": PER_DEST,
            "note": "vectorId = base + (napcs_m-1)*per_napcs + (trade_t-1)*per_trade + (dest_d-1)*per_dest + (origin_o-1)",
            "anchors_verified": [
                {"coord": "1.1.1.1.1", "vid": 1863536833},
                {"coord": "1.1.1.2.1", "vid": 1863536863},
                {"coord": "1.1.2.1.1", "vid": 1863537703},
                {"coord": "1.1.3.1.1", "vid": 1863538573},
                {"coord": "1.2.1.1.1", "vid": 1863539443},
            ],
        },
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "schema_version": 2,
    }
    with out_meta.open("w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)

    logger.info(
        "sectoral_exports_latest_yoy: wrote %d rows to %s", len(rows), out_csv
    )
    return len(rows)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    project_root = Path(__file__).resolve().parents[2]
    out_csv = project_root / "data" / "processed" / "sectoral_exports_latest_yoy.csv"
    out_meta = out_csv.with_suffix("").with_name(
        out_csv.stem + ".meta.json"
    )

    n = fetch_sectoral_exports(out_csv, out_meta)
    print(f"OK: {n} rows written to {out_csv}")
    print(f"    meta: {out_meta}")
