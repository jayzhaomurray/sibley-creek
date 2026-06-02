"""Provisional latest Government of Canada yield overlay.

Bank of Canada Valet remains the canonical history for GoC benchmark yields.
This module only fetches/parses a public market page for the newest missing
curve row and writes a quarantined artifact under data/provisional/.

Run:
    python -m pipeline.provisional.goc_yields
"""

from __future__ import annotations

import argparse
import calendar
import json
import logging
import math
import re
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Optional

import pandas as pd
from bs4 import BeautifulSoup

from pipeline.fetch._http import get_client, get_text

ROOT = Path(__file__).resolve().parents[2]
DATA_ROOT = ROOT / "data"
DEFAULT_OUTPUT = DATA_ROOT / "provisional" / "goc_yields_latest.json"
DEFAULT_OUTPUT_REL = "data/provisional/goc_yields_latest.json"

TRADING_ECONOMICS_SOURCE = "Trading Economics"
TRADING_ECONOMICS_CANADA_2Y_URL = "https://tradingeconomics.com/canada/2-year-note-yield"
TRADING_ECONOMICS_SOURCE_ID = "canada-bond-curve-page"

REQUIRED_GOC_YIELDS: dict[str, str] = {
    "yield_2yr": "Canada 2Y",
    "yield_5yr": "Canada 5Y",
    "yield_10yr": "Canada 10Y",
    "yield_30yr": "Canada 30Y",
}

TENOR_TO_SERIES = {label.split()[1]: series for series, label in REQUIRED_GOC_YIELDS.items()}
YIELD_RANGE = (0.0, 25.0)
MAX_OFFICIAL_TO_PROVISIONAL_MOVE_PP = 0.75

_CURVE_LINE_RE = re.compile(
    r"\bCanada\s+(?P<tenor>2Y|5Y|10Y|30Y)\b\s+"
    r"(?P<value>-?\d+(?:\.\d+)?)"
    r".*?\b(?P<date>[A-Z][a-z]{2}/\d{2})\b"
)

logger = logging.getLogger("pipeline.provisional.goc_yields")


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _parse_month_day(token: str, fetched_at: datetime) -> date:
    month_token, day_token = token.split("/", 1)
    month_lookup = {name.lower(): i for i, name in enumerate(calendar.month_abbr) if name}
    month = month_lookup[month_token.lower()]
    day = int(day_token)
    fetched_date = fetched_at.date()
    candidate = date(fetched_date.year, month, day)
    if candidate > fetched_date + timedelta(days=7):
        candidate = date(fetched_date.year - 1, month, day)
    return candidate


def parse_trading_economics_curve(html: str, *, fetched_at: Optional[datetime] = None) -> dict[str, Any]:
    """Parse Canada 2Y/5Y/10Y/30Y latest yields from a Trading Economics page.

    The page includes a Canada bond table in rendered text, for example:
        Canada 10Y 3.43 0.014% -0.190% 0.204% Jun/01

    Returns a provisional payload. Validation is a separate step so the caller
    can persist both the parsed values and any reasons they are not usable.
    """
    fetched_at = fetched_at or _now_utc()
    soup = BeautifulSoup(html, "lxml")
    text = " ".join(soup.get_text("\n").split())
    observations: dict[str, dict[str, Any]] = {}

    for match in _CURVE_LINE_RE.finditer(text):
        series = TENOR_TO_SERIES[match.group("tenor")]
        observations[series] = {
            "label": REQUIRED_GOC_YIELDS[series],
            "date": _parse_month_day(match.group("date"), fetched_at).isoformat(),
            "value": float(match.group("value")),
            "raw": match.group(0),
        }

    values = {series: ob["value"] for series, ob in observations.items()}
    dates = {ob["date"] for ob in observations.values()}
    as_of = next(iter(dates)) if len(dates) == 1 else None

    return {
        "schemaVersion": 1,
        "name": "goc_yields_latest",
        "status": "parsed",
        "source": TRADING_ECONOMICS_SOURCE,
        "sourceUrl": TRADING_ECONOMICS_CANADA_2Y_URL,
        "sourceId": TRADING_ECONOMICS_SOURCE_ID,
        "sourceKind": "scraped-public-page",
        "fetchedAt": fetched_at.isoformat(),
        "asOf": as_of,
        "values": values,
        "observations": observations,
        "violations": [],
        "notes": (
            "Provisional latest GoC curve row scraped from a public market page. "
            "BoC Valet remains canonical history; do not write these values into data/raw/yield_*.csv."
        ),
    }


def fetch_trading_economics_curve() -> dict[str, Any]:
    """Fetch and parse the current Trading Economics Canada bond curve page."""
    fetched_at = _now_utc()
    headers = {"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"}
    with get_client(headers=headers) as client:
        html = get_text(client, TRADING_ECONOMICS_CANADA_2Y_URL)
    return parse_trading_economics_curve(html, fetched_at=fetched_at)


def _read_latest_official(data_root: Path, series: str) -> tuple[Optional[date], Optional[float]]:
    path = data_root / "raw" / f"{series}.csv"
    if not path.exists():
        return None, None
    try:
        df = pd.read_csv(path, parse_dates=["date"])
    except Exception as exc:  # noqa: BLE001
        logger.warning("failed to read official %s: %s: %s", path, type(exc).__name__, exc)
        return None, None
    if df.empty or "date" not in df.columns or "value" not in df.columns:
        return None, None
    df = df.dropna(subset=["date", "value"]).sort_values("date")
    if df.empty:
        return None, None
    row = df.iloc[-1]
    return pd.Timestamp(row["date"]).date(), float(row["value"])


def validate_payload(
    payload: dict[str, Any],
    *,
    data_root: Optional[Path] = None,
    target_date: Optional[date] = None,
    max_move_pp: float = MAX_OFFICIAL_TO_PROVISIONAL_MOVE_PP,
) -> dict[str, Any]:
    """Validate a parsed provisional GoC yield payload.

    Mutates and returns a shallow copy with status `ok` or `invalid`.
    """
    checked = dict(payload)
    observations = dict(payload.get("observations") or {})
    values = dict(payload.get("values") or {})
    violations: list[str] = list(payload.get("violations") or [])

    missing = [series for series in REQUIRED_GOC_YIELDS if series not in observations]
    if missing:
        violations.append(f"missing required maturities: {', '.join(missing)}")

    dates: set[str] = set()
    for series, label in REQUIRED_GOC_YIELDS.items():
        ob = observations.get(series)
        if not ob:
            continue
        ob_date = ob.get("date")
        if ob_date:
            dates.add(str(ob_date))
        else:
            violations.append(f"{series}: missing observation date")
        value = values.get(series, ob.get("value"))
        try:
            fv = float(value)
        except (TypeError, ValueError):
            violations.append(f"{series}: non-numeric value {value!r}")
            continue
        if math.isnan(fv) or math.isinf(fv):
            violations.append(f"{series}: non-finite value {value!r}")
            continue
        lo, hi = YIELD_RANGE
        if fv < lo or fv > hi:
            violations.append(f"{series}: value {fv:.4g} outside sane range [{lo}, {hi}]")
        checked.setdefault("values", {})[series] = fv

    if len(dates) > 1:
        violations.append(f"mixed provisional as-of dates: {', '.join(sorted(dates))}")
        as_of = None
    elif len(dates) == 1:
        as_of = next(iter(dates))
    else:
        as_of = None
    checked["asOf"] = as_of

    if target_date is not None and as_of != target_date.isoformat():
        violations.append(f"asOf={as_of} does not match target_date={target_date.isoformat()}")

    if data_root is not None and as_of is not None:
        as_of_date = date.fromisoformat(as_of)
        official_latest: dict[str, dict[str, Any]] = {}
        for series in REQUIRED_GOC_YIELDS:
            official_date, official_value = _read_latest_official(Path(data_root), series)
            official_latest[series] = {"date": official_date.isoformat() if official_date else None, "value": official_value}
            if official_date is None or official_value is None:
                continue
            if series not in checked.get("values", {}):
                continue  # Already recorded as missing/non-numeric above.
            if as_of_date <= official_date:
                violations.append(
                    f"{series}: provisional date {as_of_date.isoformat()} is not newer than official BoC date {official_date.isoformat()}"
                )
            provisional_value = float(checked["values"][series])
            move = abs(provisional_value - official_value)
            if move > max_move_pp:
                violations.append(
                    f"{series}: provisional move {move:.2f} pp versus latest official BoC value exceeds {max_move_pp:.2f} pp"
                )
        checked["officialLatest"] = official_latest

    checked["violations"] = violations
    checked["status"] = "ok" if not violations else "invalid"
    return checked


def write_payload(payload: dict[str, Any], output_path: Path = DEFAULT_OUTPUT) -> Path:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=False), encoding="utf-8")
    return output_path


def load_payload(path: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def overlay_map_from_payload(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Convert a validated payload into the overlay map consumed by builders."""
    if payload.get("status") != "ok":
        raise ValueError(f"provisional GoC payload is not ok: {payload.get('violations')}")
    as_of = payload.get("asOf")
    if not as_of:
        raise ValueError("provisional GoC payload has no asOf date")
    overlays: dict[str, dict[str, Any]] = {}
    values = payload.get("values") or {}
    for series in REQUIRED_GOC_YIELDS:
        overlays[series] = {
            "date": as_of,
            "value": float(values[series]),
            "source": payload.get("source"),
            "sourceUrl": payload.get("sourceUrl"),
            "sourceId": payload.get("sourceId"),
            "sourceKind": payload.get("sourceKind"),
            "artifactPath": payload.get("artifactPath") or DEFAULT_OUTPUT_REL,
            "fetchedAt": payload.get("fetchedAt"),
            "status": "provisional",
        }
    return overlays


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Fetch provisional latest GoC yields.")
    parser.add_argument("--data-root", type=Path, default=DATA_ROOT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--target-date", type=lambda s: date.fromisoformat(s), default=None)
    parser.add_argument("--allow-invalid", action="store_true", help="Write artifact and exit 0 even if validation fails.")
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    payload = fetch_trading_economics_curve()
    payload = validate_payload(payload, data_root=args.data_root, target_date=args.target_date)
    out = write_payload(payload, args.output)

    if payload["status"] == "ok":
        logger.info("wrote valid provisional GoC yields: %s asOf=%s", out, payload.get("asOf"))
        return 0

    logger.error("wrote invalid provisional GoC yields: %s violations=%s", out, payload.get("violations"))
    return 0 if args.allow_invalid else 1


if __name__ == "__main__":
    raise SystemExit(main())
