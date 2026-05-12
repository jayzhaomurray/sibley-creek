"""Yahoo Finance symbol catalog.

Used where FRED is either licence-restricted (S&P 500 deep history),
discontinued (LBMA gold), or unavailable (TSX Composite). Per dashboard_purpose
section 4.6 element 4 (energy) and the daily-cadence Financial-section
absorption of "what moved overnight" elements.

Yahoo's API is unofficial; expect occasional schema drift. The fetcher in
`pipeline.fetch.yahoo` validates with pydantic at the boundary and the build
isolates per-symbol failures so one bad symbol doesn't sink the daily refresh.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class YahooSpec:
    name: str
    symbol: str
    units: str
    section: str
    cadence: str
    notes: str = ""


YAHOO_SERIES: dict[str, YahooSpec] = {
    "tsx_composite": YahooSpec(
        name="tsx_composite", symbol="^GSPTSE",
        units="Index", section="financial", cadence="daily",
        notes="S&P/TSX Composite price index. Daily close. Yahoo is the working free EOD feed.",
    ),
    "sp500": YahooSpec(
        name="sp500", symbol="^GSPC",
        units="Index", section="financial", cadence="daily",
        notes="S&P 500 price index. Deeper history than FRED SP500 (licence-truncated to 10y).",
    ),
    "gold_futures": YahooSpec(
        name="gold_futures", symbol="GC=F",
        units="USD/oz", section="financial", cadence="daily",
        notes=(
            "COMEX gold futures front month. Replaces FRED LBMA gold series "
            "(GOLDAMGBD228NLBM/GOLDPMGBD228NLBM) which were discontinued. "
            "Acceptable proxy for the LBMA AM fix at the basics-layer cadence."
        ),
    ),
    "wti": YahooSpec(
        name="wti", symbol="CL=F",
        units="USD/barrel", section="financial", cadence="daily",
        notes=(
            "NYMEX WTI crude front-month futures. Daily close, no publish "
            "lag. Replaces FRED DCOILWTICO (Cushing spot) which publishes "
            "weekly with a ~7-day lag; the dashboard needs same-day prints."
        ),
    ),
    "brent": YahooSpec(
        name="brent", symbol="BZ=F",
        units="USD/barrel", section="financial", cadence="daily",
        notes=(
            "ICE Brent crude front-month futures. Daily close, no publish "
            "lag. Replaces FRED DCOILBRENTEU (Europe spot) which publishes "
            "with the same ~7-day weekly lag as DCOILWTICO."
        ),
    ),
}
