"""Kill-test: petrocurrency channel, 2000-present.

Spec: claude-ref/research/usdcad/piece_scope.md Test 1.

Two competing narratives:
  St-Arnaud (flows): post-2014 capital discipline -> USD revenue never converts
                     to CAD -> link severed structurally.
  Scotiabank (shocks): channel intact; post-shale oil moves are supply-driven;
                       demand-driven rallies should still work.

Classifier:
  oil weekly return > +1%  AND  SPX weekly return > 0  -> demand rally ("good news")
  oil weekly return > +1%  AND  SPX weekly return <= 0 -> supply rally ("bad news")
  |oil weekly return| <= 1% -> unclassified (dead zone)
  oil weekly return < -1%  AND  SPX < 0               -> demand-driven decline
  oil weekly return < -1%  AND  SPX >= 0               -> supply-driven decline

CAD strength: cad_ret = -pct_change(DEXCAUS)
  DEXCAUS is CAD per USD (e.g. 1.35 = CAD 1.35 buys USD 1.00).
  When USD weakens (CAD strengthens), DEXCAUS falls, pct_change is negative,
  so negating gives a positive cad_ret. Sign check: 2007 saw sharp CAD
  appreciation -- cumulative cad_ret should show a sustained rise through
  2007-2008 peak.

Break date: 2014-07-01 (oil-price collapse begins mid-2014).
Robustness: break at 2015-01, 2016-01; dead zone 2%; Wed-Wed weeks.

Outputs:
  work/research/usdcad/killtest_petrocurrency_trade.png
  work/research/usdcad/killtest_rolling_demand_beta.png
  claude-ref/research/usdcad/kill_test_results.md
"""

from __future__ import annotations

import io
import json
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import httpx
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
from scipy import stats

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = Path(__file__).resolve().parent / "data"
WORK_DIR = PROJECT_ROOT / "work" / "research" / "usdcad"
RESULTS_DIR = PROJECT_ROOT / "claude-ref" / "research" / "usdcad"

DATA_DIR.mkdir(parents=True, exist_ok=True)
WORK_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# HTTP helpers (reuse project conventions: httpx, retry on 5xx/429)
# ---------------------------------------------------------------------------
TIMEOUT = httpx.Timeout(60.0, connect=15.0)

# Stooq blocks non-browser user-agents on its CSV endpoint.
BROWSER_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)
PROJECT_UA = "macro-research-department/kill_test (+https://github.com/jayzhaomurray/macro-research-department)"

FRED_BASE_URL = "https://api.stlouisfed.org/fred/series/observations"


def _get_text(url: str, *, params: Optional[dict] = None,
              max_retries: int = 4, browser_ua: bool = False) -> str:
    """GET -> text; retry on 5xx/429/network errors up to max_retries."""
    ua = BROWSER_UA if browser_ua else PROJECT_UA
    headers = {"User-Agent": ua, "Accept": "text/csv,text/plain,*/*"}
    delay = 2.0
    last_exc: Exception = RuntimeError("no attempt made")
    for attempt in range(1, max_retries + 2):
        try:
            with httpx.Client(timeout=TIMEOUT, headers=headers, follow_redirects=True) as client:
                r = client.get(url, params=params)
            if r.status_code == 429 or 500 <= r.status_code < 600:
                log.warning("HTTP %s on attempt %d; sleeping %.0fs", r.status_code, attempt, delay)
                import time; time.sleep(delay)
                delay = min(delay * 2, 60)
                continue
            r.raise_for_status()
            return r.text
        except (httpx.ConnectError, httpx.ReadTimeout, httpx.RemoteProtocolError) as exc:
            last_exc = exc
            log.warning("Network error attempt %d: %s", attempt, exc)
            import time; time.sleep(delay)
            delay = min(delay * 2, 60)
    raise RuntimeError(f"Failed after {max_retries + 1} attempts: {last_exc}") from last_exc


def _get_json_with_retry(url: str, *, params: Optional[dict] = None,
                         max_retries: int = 4) -> dict:
    """GET -> JSON; retry on 5xx/429/network errors."""
    headers = {"User-Agent": PROJECT_UA, "Accept": "application/json"}
    delay = 2.0
    last_exc: Exception = RuntimeError("no attempt made")
    for attempt in range(1, max_retries + 2):
        try:
            with httpx.Client(timeout=TIMEOUT, headers=headers, follow_redirects=True) as client:
                r = client.get(url, params=params)
            if r.status_code == 429 or 500 <= r.status_code < 600:
                log.warning("HTTP %s on attempt %d; sleeping %.0fs", r.status_code, attempt, delay)
                import time; time.sleep(delay)
                delay = min(delay * 2, 60)
                continue
            r.raise_for_status()
            return r.json()
        except (httpx.ConnectError, httpx.ReadTimeout, httpx.RemoteProtocolError) as exc:
            last_exc = exc
            log.warning("Network error attempt %d: %s", attempt, exc)
            import time; time.sleep(delay)
            delay = min(delay * 2, 60)
    raise RuntimeError(f"Failed after {max_retries + 1} attempts: {last_exc}") from last_exc


# ---------------------------------------------------------------------------
# Fetch helpers with disk cache
# ---------------------------------------------------------------------------

def _cache_path(name: str) -> Path:
    return DATA_DIR / name


def _fetch_fred_csv(series_id: str, cache_file: str) -> pd.DataFrame:
    """Fetch a FRED series via the JSON API (requires FRED_API_KEY env var).

    Cache: observations saved as CSV on disk; re-uses cache if present.
    Falls back to FRED JSON API because the no-key CSV endpoint is blocked
    by FRED when called without a browser session cookie.
    """
    path = _cache_path(cache_file)
    if path.exists():
        log.info("FRED %s: using cache %s", series_id, path.name)
        df = pd.read_csv(path)
        df["date"] = pd.to_datetime(df["date"])
        return df

    api_key = os.environ.get("FRED_API_KEY")
    if not api_key:
        raise RuntimeError(
            f"FRED_API_KEY not set; required to fetch {series_id}. "
            "Set the env var or pre-populate the cache CSV."
        )

    url = FRED_BASE_URL
    params = {
        "series_id": series_id,
        "api_key": api_key,
        "file_type": "json",
        "observation_start": "1999-01-01",
    }
    log.info("FRED %s: fetching via JSON API", series_id)
    payload = _get_json_with_retry(url, params=params)

    observations = payload.get("observations", [])
    records = []
    for ob in observations:
        if ob.get("value") in (".", "", None):
            continue
        try:
            records.append({"date": ob["date"], "value": float(ob["value"])})
        except (TypeError, ValueError, KeyError):
            continue

    if not records:
        raise RuntimeError(f"FRED {series_id}: no valid observations returned.")

    df = pd.DataFrame(records)
    df["date"] = pd.to_datetime(df["date"])
    df = df.dropna().sort_values("date").reset_index(drop=True)

    # Cache to CSV
    df.to_csv(path, index=False)
    _write_meta(path, source_url=f"https://fred.stlouisfed.org/series/{series_id}", series_id=series_id)

    log.info("FRED %s: %d obs, %s to %s", series_id, len(df),
             df["date"].iloc[0].date(), df["date"].iloc[-1].date())
    return df


def _fetch_yahoo_spx(cache_file: str) -> pd.DataFrame:
    """Fetch S&P 500 daily close from Yahoo Finance v8 chart API.

    Uses the same endpoint and browser UA as pipeline/fetch/yahoo.py.
    Yahoo carries full history (max range) for ^GSPC back to ~1928.
    Stooq now requires a paid API key (changed from when spec was written).
    """
    path = _cache_path(cache_file)
    if path.exists():
        log.info("Yahoo ^GSPC: using cache %s", path.name)
        df = pd.read_csv(path)
        df["date"] = pd.to_datetime(df["date"])
        return df

    symbol = "^GSPC"
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
    # Use explicit period1/period2 (Unix timestamps) instead of range="max".
    # Yahoo compresses very long daily histories to ~168 monthly points when
    # using range="max" with interval="1d". Explicit timestamps force true daily.
    import calendar
    period1 = int(calendar.timegm((1999, 12, 31, 0, 0, 0)))   # 1999-12-31
    period2 = int(calendar.timegm((2027, 1, 1, 0, 0, 0)))     # far future
    params = {
        "interval": "1d",
        "period1": period1,
        "period2": period2,
        "includeAdjustedClose": "true",
    }
    headers = {
        "User-Agent": BROWSER_UA,
        "Accept": "application/json",
    }
    log.info("Yahoo ^GSPC: fetching via v8 chart API (period1=%d period2=%d)", period1, period2)

    delay = 2.0
    payload = None
    for attempt in range(1, 5):
        try:
            with httpx.Client(timeout=TIMEOUT, headers=headers, follow_redirects=True) as client:
                r = client.get(url, params=params)
            if r.status_code == 429 or 500 <= r.status_code < 600:
                import time; time.sleep(delay)
                delay = min(delay * 2, 60)
                continue
            r.raise_for_status()
            payload = r.json()
            break
        except (httpx.ConnectError, httpx.ReadTimeout) as exc:
            log.warning("Yahoo attempt %d error: %s", attempt, exc)
            import time; time.sleep(delay)
            delay = min(delay * 2, 60)

    if payload is None:
        raise RuntimeError("Yahoo ^GSPC: all fetch attempts failed.")

    chart = payload.get("chart", {})
    if chart.get("error"):
        raise RuntimeError(f"Yahoo chart error: {chart['error']}")
    results = chart.get("result")
    if not results:
        raise RuntimeError("Yahoo ^GSPC: no result in response.")

    result = results[0]
    timestamps = result.get("timestamp", [])
    quotes = result.get("indicators", {}).get("quote", [{}])
    closes = quotes[0].get("close", []) if quotes else []

    # Prefer adjusted close
    adj_block = result.get("indicators", {}).get("adjclose", [])
    if adj_block and isinstance(adj_block, list) and "adjclose" in adj_block[0]:
        adj = adj_block[0]["adjclose"]
        if isinstance(adj, list) and len(adj) == len(closes):
            closes = adj

    if len(timestamps) != len(closes):
        raise RuntimeError(
            f"Yahoo ^GSPC length mismatch: {len(timestamps)} ts vs {len(closes)} closes"
        )

    df = pd.DataFrame({
        "date": pd.to_datetime(timestamps, unit="s", utc=True).tz_convert(None).normalize(),
        "value": closes,
    })
    df = df.dropna(subset=["value"]).sort_values("date").reset_index(drop=True)
    if df.empty:
        raise RuntimeError("Yahoo ^GSPC: no valid observations after parsing.")

    df.to_csv(path, index=False)
    _write_meta(path, source_url="https://finance.yahoo.com/quote/%5EGSPC", series_id="^GSPC_YAHOO")

    log.info("Yahoo ^GSPC: %d obs, %s to %s", len(df),
             df["date"].iloc[0].date(), df["date"].iloc[-1].date())
    return df


def _write_meta(data_path: Path, *, source_url: str, series_id: str) -> None:
    meta = {
        "source_url": source_url,
        "series_id": series_id,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "cache_file": data_path.name,
    }
    meta_path = data_path.with_suffix(".meta.json")
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")


# ---------------------------------------------------------------------------
# Resample daily -> weekly (Friday close)
# ---------------------------------------------------------------------------

def _to_weekly_friday(df: pd.DataFrame, value_col: str = "value") -> pd.DataFrame:
    """Resample daily series to weekly Friday closes.

    Takes the last valid observation in each week ending Friday.
    """
    s = df.set_index("date")[value_col]
    # 'W-FRI' anchors each period to Friday
    weekly = s.resample("W-FRI").last().dropna()
    weekly.name = value_col
    return weekly.reset_index()


def _to_weekly_wednesday(df: pd.DataFrame, value_col: str = "value") -> pd.DataFrame:
    """Resample daily series to weekly Wednesday closes (robustness check)."""
    s = df.set_index("date")[value_col]
    weekly = s.resample("W-WED").last().dropna()
    weekly.name = value_col
    return weekly.reset_index()


# ---------------------------------------------------------------------------
# Classifier
# ---------------------------------------------------------------------------

def classify_weeks(
    oil_ret: pd.Series,
    spx_ret: pd.Series,
    dead_zone_pct: float = 1.0,
) -> pd.Series:
    """Classify each week by oil-shock origin.

    Returns a Series with values:
      'demand_rally'    oil > +dz%  AND  spx > 0
      'supply_rally'    oil > +dz%  AND  spx <= 0
      'demand_decline'  oil < -dz%  AND  spx < 0
      'supply_decline'  oil < -dz%  AND  spx >= 0
      'unclassified'    |oil| <= dz%
    """
    dz = dead_zone_pct / 100.0
    cond_oil_up = oil_ret > dz
    cond_oil_dn = oil_ret < -dz

    result = pd.Series("unclassified", index=oil_ret.index)
    result[cond_oil_up & (spx_ret > 0)] = "demand_rally"
    result[cond_oil_up & (spx_ret <= 0)] = "supply_rally"
    result[cond_oil_dn & (spx_ret < 0)] = "demand_decline"
    result[cond_oil_dn & (spx_ret >= 0)] = "supply_decline"
    return result


# ---------------------------------------------------------------------------
# OLS beta helper
# ---------------------------------------------------------------------------

def _ols_beta(x: pd.Series, y: pd.Series) -> tuple[float, float, int]:
    """Simple OLS: y = a + b*x. Returns (beta, r_squared, n)."""
    mask = x.notna() & y.notna()
    x_, y_ = x[mask].values, y[mask].values
    n = len(x_)
    if n < 5:
        return float("nan"), float("nan"), n
    slope, intercept, r, p, se = stats.linregress(x_, y_)
    return float(slope), float(r ** 2), n


# ---------------------------------------------------------------------------
# 2x2 table
# ---------------------------------------------------------------------------

def build_2x2_table(
    df: pd.DataFrame,
    break_date: str,
    *,
    dead_zone: float = 1.0,
) -> pd.DataFrame:
    """Build the demand vs supply x pre/post break 2x2 table.

    Columns: regime, period, avg_cad_ret_pct, n_weeks, beta_cad_on_oil, r2
    """
    df = df.copy()
    break_ts = pd.Timestamp(break_date)
    df["period"] = np.where(df["date"] <= break_ts, "pre_break", "post_break")
    df["regime"] = classify_weeks(df["oil_ret"], df["spx_ret"], dead_zone_pct=dead_zone)

    rows = []
    for regime in ("demand_rally", "supply_rally"):
        for period in ("pre_break", "post_break"):
            mask = (df["regime"] == regime) & (df["period"] == period)
            sub = df[mask]
            n = len(sub)
            if n == 0:
                rows.append({
                    "regime": regime, "period": period,
                    "avg_cad_ret_pct": float("nan"),
                    "n_weeks": 0,
                    "beta_cad_on_oil": float("nan"),
                    "r2": float("nan"),
                })
                continue
            avg = float(sub["cad_ret"].mean() * 100)
            beta, r2, _ = _ols_beta(sub["oil_ret"], sub["cad_ret"])
            rows.append({
                "regime": regime, "period": period,
                "avg_cad_ret_pct": round(avg, 4),
                "n_weeks": n,
                "beta_cad_on_oil": round(beta, 4),
                "r2": round(r2, 4),
            })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Sign check: 2007 CAD appreciation episode
# ---------------------------------------------------------------------------

def sign_check(df: pd.DataFrame) -> str:
    """Verify CAD sign convention.

    CAD peaked against USD around late 2007 / early 2008 (parity and through).
    Cumulative cad_ret over 2007 should be substantially positive.
    """
    yr = df[(df["date"].dt.year == 2007)]
    cum_2007 = float(yr["cad_ret"].sum() * 100)
    check = "PASS" if cum_2007 > 3.0 else "FAIL"
    return f"Sign check 2007 cumulative cad_ret = {cum_2007:.2f}% [{check}] (expected >3% for CAD appreciation episode)"


# ---------------------------------------------------------------------------
# Chart 1: cumulative CAD return in demand vs supply oil rally weeks
# ---------------------------------------------------------------------------

def plot_cumulative_petrocurrency(df: pd.DataFrame, out_path: Path) -> None:
    break_date = pd.Timestamp("2014-07-01")

    demand = df[df["regime"] == "demand_rally"].copy()
    supply = df[df["regime"] == "supply_rally"].copy()

    # Cumulative sum of cad_ret (in pct) over rally weeks only
    # Resorted by date; cumsum tracks the running equity curve of "buy CAD on these weeks"
    demand = demand.sort_values("date")
    supply = supply.sort_values("date")

    demand_cum = demand.set_index("date")["cad_ret"].cumsum() * 100
    supply_cum = supply.set_index("date")["cad_ret"].cumsum() * 100

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(demand_cum.index, demand_cum.values,
            color="#1a1a2e", lw=1.8, label="Demand-driven rally weeks (oil up + SPX up)")
    ax.plot(supply_cum.index, supply_cum.values,
            color="#888888", lw=1.2, alpha=0.7, label="Supply-driven rally weeks (oil up + SPX dn)")
    ax.axvline(break_date, color="#cc3333", lw=1.0, ls="--", label="2014-07-01 break")
    ax.axhline(0, color="black", lw=0.5, ls="-")

    ax.set_title(
        "Cumulative CAD return in demand-driven vs supply-driven oil rally weeks",
        fontsize=12, pad=10
    )
    ax.set_ylabel("Cumulative CAD return (pct, sum of weekly moves)", fontsize=9)
    ax.set_xlabel("")
    ax.legend(fontsize=8, loc="upper left")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.xaxis.set_major_locator(mdates.YearLocator(2))
    fig.autofmt_xdate(rotation=30)

    # Annotate 2021 reopening rally (key discriminating episode per spec)
    ax.annotate("2021 reopening", xy=(pd.Timestamp("2021-06-01"), demand_cum.asof(pd.Timestamp("2021-06-01"))),
                xytext=(pd.Timestamp("2019-01-01"),
                        demand_cum.asof(pd.Timestamp("2021-06-01")) + 2),
                fontsize=7, arrowprops=dict(arrowstyle="->", lw=0.6), color="#444")

    fig.tight_layout()
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    log.info("Saved chart 1: %s", out_path)


# ---------------------------------------------------------------------------
# Chart 2: 3-year rolling beta of cad_ret on oil_ret (demand weeks only)
# ---------------------------------------------------------------------------

def plot_rolling_demand_beta(df: pd.DataFrame, out_path: Path, window_weeks: int = 156) -> None:
    """3-year rolling window = 156 weeks. Uses only demand-rally weeks."""
    break_date = pd.Timestamp("2014-07-01")
    demand = df[df["regime"] == "demand_rally"].copy().sort_values("date")

    # Rolling OLS: for each date, take preceding `window_weeks` demand-rally observations
    betas = []
    dates = []
    for i in range(window_weeks, len(demand)):
        window = demand.iloc[i - window_weeks: i]
        x = window["oil_ret"].values
        y = window["cad_ret"].values
        mask = np.isfinite(x) & np.isfinite(y)
        if mask.sum() < 20:
            continue
        slope, _, r, _, _ = stats.linregress(x[mask], y[mask])
        betas.append(slope)
        dates.append(demand.iloc[i]["date"])

    if not betas:
        log.warning("Rolling beta: insufficient demand-rally weeks for rolling window.")
        return

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(dates, betas, color="#1a1a2e", lw=1.5, label=f"3-yr rolling beta (n={window_weeks} demand-rally wks)")
    ax.axhline(0, color="black", lw=0.5)
    ax.axvline(break_date, color="#cc3333", lw=1.0, ls="--", label="2014-07-01 break")

    ax.set_title(
        "3-year rolling beta: CAD return on oil return (demand-rally weeks only)",
        fontsize=12, pad=10
    )
    ax.set_ylabel("Beta (cad_ret / oil_ret)", fontsize=9)
    ax.legend(fontsize=8)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.xaxis.set_major_locator(mdates.YearLocator(2))
    fig.autofmt_xdate(rotation=30)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    log.info("Saved chart 2: %s", out_path)


# ---------------------------------------------------------------------------
# Results markdown writer
# ---------------------------------------------------------------------------

def _table_row(row: dict) -> str:
    return (
        f"| {row['regime']:20s} | {row['period']:12s} "
        f"| {row['avg_cad_ret_pct']:+.4f}% "
        f"| {row['n_weeks']:6d} "
        f"| {row['beta_cad_on_oil']:+.4f} "
        f"| {row['r2']:.4f} |"
    )


def _format_table(tbl: pd.DataFrame, caption: str) -> str:
    header = (
        f"\n### {caption}\n\n"
        "| regime               | period       | avg_cad_ret/wk | n_weeks "
        "| beta_cad_on_oil | r2     |\n"
        "|----------------------|--------------|----------------|---------|"
        "-----------------|--------|\n"
    )
    rows = "\n".join(_table_row(r) for _, r in tbl.iterrows())
    return header + rows + "\n"


def write_results(
    main_table: pd.DataFrame,
    robust_tables: list[tuple[str, pd.DataFrame]],
    sign_check_str: str,
    df: pd.DataFrame,
    run_ts: str,
    out_path: Path,
) -> None:
    """Write all results to a markdown file."""

    # Verdict logic
    # Look at demand_rally post_break row
    post_demand = main_table[
        (main_table["regime"] == "demand_rally") & (main_table["period"] == "post_break")
    ]
    pre_demand = main_table[
        (main_table["regime"] == "demand_rally") & (main_table["period"] == "pre_break")
    ]

    verdict = "MURKY"
    verdict_detail = "Signal is ambiguous; inspect charts."
    if not post_demand.empty and not pre_demand.empty:
        post_avg = float(post_demand["avg_cad_ret_pct"].iloc[0])
        pre_avg = float(pre_demand["avg_cad_ret_pct"].iloc[0])
        post_n = int(post_demand["n_weeks"].iloc[0])
        post_beta = float(post_demand["beta_cad_on_oil"].iloc[0])
        pre_beta = float(pre_demand["beta_cad_on_oil"].iloc[0])

        small_sample_flag = ""
        if post_n < 40:
            small_sample_flag = (
                f"\n\n**SMALL SAMPLE WARNING: post-2014 demand-rally weeks = {post_n} "
                f"(< 40). Statistical inference is unreliable.**"
            )

        if post_avg < 0.05 and post_beta < 0.05:
            verdict = "CLEARLY DEAD"
            verdict_detail = (
                f"Post-break demand-rally avg cad_ret = {post_avg:+.4f}% per week "
                f"(beta = {post_beta:+.4f}); pre-break avg = {pre_avg:+.4f}% "
                f"(beta = {pre_beta:+.4f}). "
                "CAD no longer responds to demand-driven oil rallies. St-Arnaud narrative supported."
            )
        elif post_avg > 0.15 and post_beta > 0.15:
            verdict = "CLEARLY ALIVE"
            verdict_detail = (
                f"Post-break demand-rally avg cad_ret = {post_avg:+.4f}% per week "
                f"(beta = {post_beta:+.4f}); pre-break avg = {pre_avg:+.4f}% "
                f"(beta = {pre_beta:+.4f}). "
                "CAD still responds to demand-driven oil rallies. Scotiabank narrative supported."
            )
        else:
            verdict = "MURKY"
            verdict_detail = (
                f"Post-break demand-rally avg cad_ret = {post_avg:+.4f}% per week "
                f"(beta = {post_beta:+.4f}); pre-break avg = {pre_avg:+.4f}% "
                f"(beta = {pre_beta:+.4f}). "
                "Attenuation visible but not a clean break; inspect rolling-beta chart."
            )
    else:
        small_sample_flag = ""

    # Bucket counts
    regime_counts = df["regime"].value_counts().to_dict()

    lines = [
        "# Kill-test results: petrocurrency channel",
        f"\nRun: {run_ts}  |  Break date: 2014-07-01  |  Dead zone: 1%  |  Weekly freq: Friday",
        "",
        "## Data sources",
        "- USDCAD: FRED DEXCAUS (CAD per USD), daily, converted to CAD-strength return: cad_ret = -pct_change(DEXCAUS)",
        "- WTI oil: FRED DCOILWTICO, daily",
        "- S&P 500: Yahoo Finance ^GSPC v8 chart API (Stooq now requires paid key), daily",
        "- All resampled to weekly Friday close",
        "",
        "## Sign check",
        sign_check_str,
        "",
        "## Week counts by bucket",
        "```",
        *[f"  {k:25s}: {v}" for k, v in sorted(regime_counts.items())],
        "```",
    ]

    lines.append(_format_table(main_table, "Main 2x2: break at 2014-07-01, dead zone 1%, Friday weeks"))

    for caption, tbl in robust_tables:
        lines.append(_format_table(tbl, caption))

    lines += [
        "",
        "## Verdict",
        f"**{verdict}**",
        "",
        verdict_detail,
        small_sample_flag if post_demand.shape[0] > 0 and int(post_demand["n_weeks"].iloc[0]) < 40 else "",
        "",
        "## Charts",
        f"- `work/research/usdcad/killtest_petrocurrency_trade.png` -- cumulative CAD return by regime",
        f"- `work/research/usdcad/killtest_rolling_demand_beta.png` -- 3-yr rolling beta, demand weeks",
    ]

    out_path.write_text("\n".join(lines), encoding="utf-8")
    log.info("Results written: %s", out_path)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    run_ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ")
    log.info("=== kill_test.py start %s ===", run_ts)

    # ---- Fetch raw daily data ----
    log.info("Fetching USDCAD (FRED DEXCAUS)...")
    usdcad_raw = _fetch_fred_csv("DEXCAUS", "fred_DEXCAUS.csv")

    log.info("Fetching WTI oil (FRED DCOILWTICO)...")
    wti_raw = _fetch_fred_csv("DCOILWTICO", "fred_DCOILWTICO.csv")

    log.info("Fetching S&P 500 (Yahoo ^GSPC)...")
    spx_raw = _fetch_yahoo_spx("yahoo_spx.csv")

    # ---- Resample to weekly Friday ----
    usdcad_w = _to_weekly_friday(usdcad_raw)
    wti_w = _to_weekly_friday(wti_raw)
    spx_w = _to_weekly_friday(spx_raw)

    usdcad_w.columns = ["date", "usdcad"]
    wti_w.columns = ["date", "oil"]
    spx_w.columns = ["date", "spx"]

    # ---- Merge on date (inner join on weekly Friday dates) ----
    df = (
        usdcad_w.merge(wti_w, on="date", how="inner")
                .merge(spx_w, on="date", how="inner")
    )
    df = df[df["date"] >= pd.Timestamp("2000-01-01")].copy()
    df = df.sort_values("date").reset_index(drop=True)

    # ---- Compute returns ----
    # cad_ret = -pct_change(DEXCAUS): CAD strength (positive = CAD appreciated)
    df["cad_ret"] = -(df["usdcad"].pct_change())
    df["oil_ret"] = df["oil"].pct_change()
    df["spx_ret"] = df["spx"].pct_change()

    # Drop first row (NaN returns) and any remaining NaN rows
    df = df.dropna(subset=["cad_ret", "oil_ret", "spx_ret"]).reset_index(drop=True)

    log.info("Weekly dataset: %d obs, %s to %s",
             len(df), df["date"].iloc[0].date(), df["date"].iloc[-1].date())

    # ---- Sign check ----
    sign_str = sign_check(df)
    log.info(sign_str)

    # ---- Classify weeks ----
    df["regime"] = classify_weeks(df["oil_ret"], df["spx_ret"], dead_zone_pct=1.0)

    # ---- Main 2x2 table ----
    main_table = build_2x2_table(df, "2014-07-01", dead_zone=1.0)
    log.info("\nMain 2x2 table:\n%s", main_table.to_string(index=False))

    # ---- Robustness ----
    robust_tables: list[tuple[str, pd.DataFrame]] = []

    # 1. Dead zone 2%
    df_dz2 = df.copy()
    df_dz2["regime"] = classify_weeks(df_dz2["oil_ret"], df_dz2["spx_ret"], dead_zone_pct=2.0)
    robust_tables.append(
        ("Robustness: dead zone 2%, break 2014-07-01, Friday weeks",
         build_2x2_table(df_dz2, "2014-07-01", dead_zone=2.0))
    )

    # 2. Wednesday-Wednesday weeks
    usdcad_ww = _to_weekly_wednesday(usdcad_raw)
    wti_ww = _to_weekly_wednesday(wti_raw)
    spx_ww = _to_weekly_wednesday(spx_raw)
    usdcad_ww.columns = ["date", "usdcad"]
    wti_ww.columns = ["date", "oil"]
    spx_ww.columns = ["date", "spx"]
    df_wed = (
        usdcad_ww.merge(wti_ww, on="date", how="inner")
                  .merge(spx_ww, on="date", how="inner")
    )
    df_wed = df_wed[df_wed["date"] >= pd.Timestamp("2000-01-01")].copy()
    df_wed["cad_ret"] = -(df_wed["usdcad"].pct_change())
    df_wed["oil_ret"] = df_wed["oil"].pct_change()
    df_wed["spx_ret"] = df_wed["spx"].pct_change()
    df_wed = df_wed.dropna(subset=["cad_ret", "oil_ret", "spx_ret"]).reset_index(drop=True)
    df_wed["regime"] = classify_weeks(df_wed["oil_ret"], df_wed["spx_ret"], dead_zone_pct=1.0)
    robust_tables.append(
        ("Robustness: Wednesday weeks, dead zone 1%, break 2014-07-01",
         build_2x2_table(df_wed, "2014-07-01", dead_zone=1.0))
    )

    # 3. Break date sensitivity
    for break_date in ("2015-01-01", "2016-01-01"):
        robust_tables.append(
            (f"Robustness: Friday weeks, dead zone 1%, break {break_date}",
             build_2x2_table(df, break_date, dead_zone=1.0))
        )

    # ---- Charts ----
    chart1_path = WORK_DIR / "killtest_petrocurrency_trade.png"
    chart2_path = WORK_DIR / "killtest_rolling_demand_beta.png"
    plot_cumulative_petrocurrency(df, chart1_path)
    plot_rolling_demand_beta(df, chart2_path)

    # ---- Results file ----
    results_path = RESULTS_DIR / "kill_test_results.md"
    write_results(
        main_table=main_table,
        robust_tables=robust_tables,
        sign_check_str=sign_str,
        df=df,
        run_ts=run_ts,
        out_path=results_path,
    )

    # ---- Summary to stdout ----
    print("\n" + "=" * 70)
    print("KILL TEST SUMMARY")
    print("=" * 70)
    print(sign_str)
    print("\nBucket counts:")
    for k, v in sorted(df["regime"].value_counts().items()):
        flag = " <-- SMALL SAMPLE WARNING" if k == "demand_rally" and v < 40 else ""
        print(f"  {k:25s}: {v}{flag}")
    print("\nMain 2x2 table:")
    print(main_table.to_string(index=False))
    print("=" * 70)

    # Verdict
    post_demand = main_table[
        (main_table["regime"] == "demand_rally") & (main_table["period"] == "post_break")
    ]
    pre_demand = main_table[
        (main_table["regime"] == "demand_rally") & (main_table["period"] == "pre_break")
    ]
    if not post_demand.empty:
        post_avg = float(post_demand["avg_cad_ret_pct"].iloc[0])
        post_beta = float(post_demand["beta_cad_on_oil"].iloc[0])
        pre_avg = float(pre_demand["avg_cad_ret_pct"].iloc[0])
        pre_beta = float(pre_demand["beta_cad_on_oil"].iloc[0])
        post_n = int(post_demand["n_weeks"].iloc[0])
        if post_avg < 0.05 and post_beta < 0.05:
            v = "CLEARLY DEAD"
        elif post_avg > 0.15 and post_beta > 0.15:
            v = "CLEARLY ALIVE"
        else:
            v = "MURKY"
        print(f"\nVERDICT: {v}")
        print(f"  pre-break demand-rally: avg={pre_avg:+.4f}%/wk, beta={pre_beta:+.4f}, n={int(pre_demand['n_weeks'].iloc[0])}")
        print(f"  post-break demand-rally: avg={post_avg:+.4f}%/wk, beta={post_beta:+.4f}, n={post_n}")
        if post_n < 40:
            print(f"  ** SMALL SAMPLE: post-break demand-rally weeks = {post_n} **")
    print("=" * 70)
    print(f"\nCharts:")
    print(f"  {chart1_path}")
    print(f"  {chart2_path}")
    print(f"\nFull results: {results_path}")


if __name__ == "__main__":
    main()
