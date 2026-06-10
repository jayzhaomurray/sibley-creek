r"""BoC decision-day live monitor — a local dashboard for reaction commentary.

LAUNCH (one command, from the repo root):

    .venv\Scripts\python.exe -m pipeline.tools.boc_live_monitor

That starts a localhost HTTP server on http://127.0.0.1:8787, kicks off
background poll loops, and opens the default browser to the page. Options:

    --port N        listen on a different port (default 8787)
    --no-browser    don't auto-open the browser (for testing / re-attach)

What it shows (all free sources):

    1. Market-implied policy path — front 3M CORRA futures contracts from the
       Montreal Exchange free quotes page (symbol CRA), converted to implied
       policy rates via the same logic as pipeline/shadow_rate/market_path.py
       (100 - price, minus the trailing CORRA-target spread when available).
    2. USDCAD — Yahoo Finance USDCAD=X, the genuinely live tile.
    3. GoC bond futures — MX symbols CGZ (2y), CGF (5y), CGB (10y), front
       contract by open interest. NOTE: price UP = yields DOWN (the tiles
       annotate this so direction is never misread live).
    4. S&P/TSX Composite (^GSPTSE) and WTI (CL=F) — context tiles.

The killer feature: a FREEZE BASELINE button. Click it the moment the
decision drops; from then on every tile shows the change SINCE the baseline
alongside the change on the day, so the reaction ("USDCAD +0.4% since the
decision, Dec implied path +6 bp") reads straight off the screen. The
baseline lives in browser localStorage — it survives a page reload and a
server restart. CLEAR resets it.

Latency honesty (non-negotiable): every tile carries its own latency tag
(Yahoo ~live-to-15-min; MX free quotes ~15-min delayed), the exchange quote
time where available, and a fetched-at stamp in ET. If a poll fails, the
tile flips to a visible STALE state showing the last-good timestamp — it
never silently freezes on an old number.

Source quirks (verified live 2026-06-10):

    - MX quotes table: the displayed "Settl. price" is the PRIOR session's
      settlement; intraday last = settle + net change (verified across CRA /
      CGB / CGZ / CGF rows). We derive last from settle + net.
    - MX front months near expiry go quote-dead (bid/ask 0, tiny OI) while
      the next contract carries ~30x the open interest. Bond-future tiles
      therefore select the ACTIVE contract by max open interest, not row 1.
    - Yahoo v8 chart meta carries regularMarketPrice / chartPreviousClose /
      regularMarketTime — one request per symbol per cycle, no candle parse.

Politeness: Yahoo polls every ~20s, MX every ~120s (it's 15-min-delayed
anyway), one request per symbol per cycle, 1s spacing between MX symbols,
all through the repo's shared httpx client (pipeline/fetch/_http.py).

This is an internal operator tool: it never writes to data/, is not part of
build.py, and serves only on 127.0.0.1.
"""

from __future__ import annotations

import argparse
import copy
import json
import sys
import threading
import time
import webbrowser
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from zoneinfo import ZoneInfo

PROJECT_ROOT = Path(__file__).parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from bs4 import BeautifulSoup  # noqa: E402

from pipeline.fetch._http import get_client, get_json, get_text  # noqa: E402
from pipeline.fetch.yahoo import YAHOO_CHART_URL, YAHOO_HEADERS  # noqa: E402
from pipeline.shadow_rate.market_path import (  # noqa: E402
    _label_to_month_year,
    contract_to_quarter,
    implied_corra_from_settlement,
)

ET = ZoneInfo("America/Toronto")

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
DEFAULT_PORT = 8787
YAHOO_POLL_S = 20
MX_POLL_S = 120
MX_SYMBOL_SPACING_S = 1.0
N_CRA_CONTRACTS = 4

# key, yahoo symbol, display label, decimal places
YAHOO_TILES = [
    ("usdcad", "USDCAD=X", "USDCAD", 4),
    ("tsx", "^GSPTSE", "S&P/TSX Composite", 0),
    ("wti", "CL=F", "WTI crude (front)", 2),
]

# key, MX symbol, display label
MX_BOND_TILES = [
    ("cgz", "CGZ", "CGZ &mdash; 2y GoC future"),
    ("cgf", "CGF", "CGF &mdash; 5y GoC future"),
    ("cgb", "CGB", "CGB &mdash; 10y GoC future"),
]

MX_QUOTES_URL = "https://www.m-x.ca/en/trading/data/quotes?symbol={sym}"
MX_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "macro-research-department/0.1 "
        "(+https://github.com/jayzhaomurray/macro-research-department)"
    ),
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "en-CA,en;q=0.9",
}

_MONTH_ABBR = {
    1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "Jun",
    7: "Jul", 8: "Aug", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec",
}

# ---------------------------------------------------------------------------
# Shared state (pollers write, HTTP handler reads; guarded by _LOCK)
# ---------------------------------------------------------------------------
_LOCK = threading.Lock()
STATE: dict = {
    "yahoo": {},        # key -> tile dict
    "mx": {},           # 'cra' + bond keys -> tile dict
    "spread": None,     # CORRA-minus-target spread (%) or None if unavailable
    "spread_note": "fetching trailing CORRA-target spread...",
}


def _now_et() -> str:
    return datetime.now(ET).strftime("%H:%M:%S")


def _epoch_to_et(epoch: float | int | None) -> str | None:
    if not epoch:
        return None
    return datetime.fromtimestamp(int(epoch), ET).strftime("%H:%M:%S")


def _short_label(label: str) -> str:
    """'September 2026' -> 'Sep-26'. Falls back to the raw label."""
    my = _label_to_month_year(label)
    if my is None:
        return label
    month, year = my
    return f"{_MONTH_ABBR[month]}-{year % 100:02d}"


# ---------------------------------------------------------------------------
# Fetchers
# ---------------------------------------------------------------------------
def fetch_yahoo_quote(symbol: str) -> tuple[float, float | None, int | None]:
    """One symbol -> (last price, previous close, exchange quote time epoch).

    Uses the v8 chart meta block (regularMarketPrice etc.) rather than the
    candle arrays — one cheap request, and the meta price is the freshest
    number Yahoo exposes on the free endpoint.
    """
    url = f"{YAHOO_CHART_URL}/{symbol}"
    params = {"interval": "1m", "range": "1d"}
    with get_client(headers=YAHOO_HEADERS) as client:
        payload = get_json(client, url, params=params)
    result = (payload.get("chart") or {}).get("result") or []
    if not result:
        raise ValueError(f"Yahoo returned no result for {symbol!r}")
    meta = result[0].get("meta") or {}
    price = meta.get("regularMarketPrice")
    if price is None:
        raise ValueError(f"Yahoo meta missing regularMarketPrice for {symbol!r}")
    prev = meta.get("chartPreviousClose") or meta.get("previousClose")
    return float(price), (float(prev) if prev is not None else None), meta.get("regularMarketTime")


def parse_mx_table(html: str) -> list[dict]:
    """Parse an MX quotes page -> rows with label/bid/ask/settle/net/oi.

    Same defensive pattern as market_path.parse_cra_table (that function only
    returns settlements; the live monitor also needs net change + open
    interest, hence this wider sibling). Columns are keyed off the header row
    so an upstream re-order fails loudly instead of mis-reading.
    """
    soup = BeautifulSoup(html, "lxml")
    table = soup.find("table")
    if table is None:
        raise ValueError("no <table> found on the MX quotes page")
    headers = [th.get_text(strip=True).lower() for th in table.select("thead th")]
    if not headers:
        raise ValueError("MX quotes table has no header row")

    def _col(*needles: str) -> int:
        for i, h in enumerate(headers):
            if all(n in h for n in needles):
                return i
        raise ValueError(f"MX table missing a column matching {needles}; got {headers}")

    idx = {
        "label": _col("month"),
        "bid": _col("bid"),
        "ask": _col("ask"),
        "settle": _col("settl"),
        "net": _col("net", "change"),
        "oi": _col("open", "int"),
    }

    def _num(cells: list[str], i: int) -> float | None:
        try:
            return float(cells[i].replace(",", ""))
        except (TypeError, ValueError, IndexError):
            return None

    rows: list[dict] = []
    for tr in table.select("tbody tr"):
        cells = [td.get_text(strip=True) for td in tr.find_all(["td", "th"])]
        if len(cells) <= max(idx.values()):
            continue
        label = cells[idx["label"]]
        settle = _num(cells, idx["settle"])
        if not label or settle is None:
            continue
        rows.append(
            {
                "label": label,
                "bid": _num(cells, idx["bid"]),
                "ask": _num(cells, idx["ask"]),
                "settle": settle,
                "net": _num(cells, idx["net"]) or 0.0,
                "oi": _num(cells, idx["oi"]) or 0.0,
            }
        )
    if not rows:
        raise ValueError("MX quotes table parsed but yielded no rows")
    return rows


def fetch_mx_rows(symbol: str) -> list[dict]:
    url = MX_QUOTES_URL.format(sym=symbol)
    with get_client(headers=MX_HEADERS) as client:
        html = get_text(client, url)
    return parse_mx_table(html)


# ---------------------------------------------------------------------------
# Tile builders
# ---------------------------------------------------------------------------
def build_cra_tile(rows: list[dict]) -> dict:
    """Front CORRA contracts -> implied-rate strip.

    last = prior settle + net change (MX free-page convention, verified).
    implied 3M CORRA = 100 - last. The CORRA-target spread adjustment is
    applied client-side from STATE['spread'] so that freeze-baseline deltas
    are computed on the raw implied CORRA (the constant spread cancels in
    deltas and can't jump if the spread fetch lands after a freeze).
    day_chg_bp = -net * 100 (price up = implied rate down).
    """
    usable = [r for r in rows if (r["oi"] or 0) > 0]
    contracts = []
    for r in usable[:N_CRA_CONTRACTS]:
        last = r["settle"] + r["net"]
        my = _label_to_month_year(r["label"])
        quarter = contract_to_quarter(*my) if my else None
        contracts.append(
            {
                "label": r["label"],
                "short": _short_label(r["label"]),
                "quarter": quarter,
                "last": round(last, 4),
                "implied_corra": round(implied_corra_from_settlement(last), 4),
                "day_chg_bp": round(-r["net"] * 100, 2),
                "oi": int(r["oi"]),
            }
        )
    if not contracts:
        raise ValueError("CRA table had no contracts with open interest")
    return {"contracts": contracts}


def build_bond_tile(rows: list[dict]) -> dict:
    """Active contract (max open interest) -> price + day change."""
    active = max(rows, key=lambda r: r["oi"] or 0)
    if (active["oi"] or 0) <= 0:
        raise ValueError("no MX bond contract with open interest")
    last = active["settle"] + active["net"]
    return {
        "contract": active["label"],
        "short": _short_label(active["label"]),
        "last": round(last, 3),
        "prev_settle": round(active["settle"], 3),
        "day_chg": round(active["net"], 3),
        "oi": int(active["oi"]),
    }


# ---------------------------------------------------------------------------
# Poll loops (daemon threads). On failure a tile keeps its last-good payload
# but flips ok=False with the error string -> fail-visible, never silent.
# ---------------------------------------------------------------------------
def _store(section: str, key: str, fresh: dict | None, label: str, error: str | None) -> None:
    with _LOCK:
        prev = STATE[section].get(key, {})
        if fresh is not None:
            tile = fresh
            tile["ok"] = True
            tile["error"] = None
            tile["last_good_et"] = _now_et()
        else:
            tile = dict(prev) if prev else {}
            tile["ok"] = False
            tile["error"] = error
        tile["key"] = key
        tile.setdefault("label", label)
        tile["fetched_at_et"] = _now_et()
        STATE[section][key] = tile


def _poll_yahoo_loop() -> None:
    while True:
        for key, symbol, label, _dp in YAHOO_TILES:
            try:
                price, prev, qt = fetch_yahoo_quote(symbol)
                day_chg = (price - prev) if prev else None
                day_pct = (price / prev - 1) * 100 if prev else None
                _store("yahoo", key, {
                    "label": label,
                    "symbol": symbol,
                    "price": price,
                    "prev_close": prev,
                    "day_chg": day_chg,
                    "day_pct": round(day_pct, 4) if day_pct is not None else None,
                    "quote_time_et": _epoch_to_et(qt),
                }, label, None)
            except Exception as exc:  # noqa: BLE001 — tile-level fail-visible
                _store("yahoo", key, None, label, f"{type(exc).__name__}: {exc}")
                print(f"[{_now_et()}] WARN yahoo {symbol}: {type(exc).__name__}: {exc}")
        time.sleep(YAHOO_POLL_S)


def _poll_mx_loop() -> None:
    while True:
        try:
            tile = build_cra_tile(fetch_mx_rows("CRA"))
            tile["label"] = "Market-implied policy path"
            _store("mx", "cra", tile, "Market-implied policy path", None)
        except Exception as exc:  # noqa: BLE001
            _store("mx", "cra", None, "Market-implied policy path",
                   f"{type(exc).__name__}: {exc}")
            print(f"[{_now_et()}] WARN mx CRA: {type(exc).__name__}: {exc}")
        for key, symbol, label in MX_BOND_TILES:
            time.sleep(MX_SYMBOL_SPACING_S)
            try:
                tile = build_bond_tile(fetch_mx_rows(symbol))
                tile["label"] = label
                _store("mx", key, tile, label, None)
            except Exception as exc:  # noqa: BLE001
                _store("mx", key, None, label, f"{type(exc).__name__}: {exc}")
                print(f"[{_now_et()}] WARN mx {symbol}: {type(exc).__name__}: {exc}")
        time.sleep(MX_POLL_S)


def _fetch_spread_once() -> None:
    """Best-effort one-shot CORRA-minus-target spread (Valet + processed CSV).

    If it fails (offline Valet, missing processed file) the CRA tile shows
    unadjusted implied CORRA and SAYS SO — never a silent wrong basis.
    """
    try:
        from pipeline.shadow_rate.market_path import _fetch_spread
        spread = round(_fetch_spread(), 4)
        with _LOCK:
            STATE["spread"] = spread
            STATE["spread_note"] = (
                f"target-adjusted: implied CORRA {spread * 100:+.1f} bp "
                "(trailing 60d CORRA-target mean)"
            )
        print(f"[{_now_et()}] CORRA-target spread: {spread * 100:+.2f} bp")
    except Exception as exc:  # noqa: BLE001
        with _LOCK:
            STATE["spread"] = None
            STATE["spread_note"] = (
                "UNADJUSTED implied 3M CORRA (spread fetch failed: "
                f"{type(exc).__name__})"
            )
        print(f"[{_now_et()}] WARN spread fetch failed: {exc}")


# ---------------------------------------------------------------------------
# HTTP server
# ---------------------------------------------------------------------------
class _Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802 — http.server API
        if self.path in ("/", "/index.html"):
            body = PAGE_HTML.encode("utf-8")
            self._send(200, "text/html; charset=utf-8", body)
        elif self.path.startswith("/data"):
            with _LOCK:
                snapshot = copy.deepcopy(STATE)
            snapshot["server_time_et"] = _now_et()
            body = json.dumps(snapshot).encode("utf-8")
            self._send(200, "application/json", body)
        else:
            self._send(404, "text/plain", b"not found")

    def _send(self, status: int, ctype: str, body: bytes) -> None:
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args) -> None:  # quiet the per-request spam
        return


# ---------------------------------------------------------------------------
# Page (single self-contained document; polls /data every 5s)
# ---------------------------------------------------------------------------
PAGE_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>BoC decision-day live monitor</title>
<style>
  :root {
    --bg: #0d1117; --panel: #161b22; --edge: #2d333b;
    --txt: #e6edf3; --dim: #8b949e; --faint: #586069;
    --up: #3fb950; --dn: #f85149; --flat: #8b949e;
    --amber: #d29922; --accent: #58a6ff;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { background: var(--bg); color: var(--txt);
         font: 14px/1.45 "Segoe UI", system-ui, sans-serif; padding: 14px 18px; }
  .mono { font-family: Consolas, "Cascadia Mono", monospace; }

  header { display: flex; align-items: baseline; gap: 16px; flex-wrap: wrap;
           margin-bottom: 12px; }
  header h1 { font-size: 15px; letter-spacing: 2px; font-weight: 600;
              text-transform: uppercase; color: var(--accent); }
  #clock { font-family: Consolas, monospace; font-size: 15px; color: var(--dim); }
  #conn { font-size: 12px; color: var(--dim); }
  #conn.bad { color: var(--dn); font-weight: 700; }
  .spacer { flex: 1; }
  button { background: var(--panel); color: var(--txt); border: 1px solid var(--edge);
           border-radius: 6px; padding: 7px 16px; font: 600 13px "Segoe UI", sans-serif;
           cursor: pointer; }
  button:hover { border-color: var(--accent); }
  #freezeBtn { background: #1f6feb; border-color: #1f6feb; }
  #freezeBtn:hover { background: #388bfd; }
  #clearBtn { display: none; }

  #frozenBanner { display: none; margin-bottom: 12px; padding: 7px 14px;
    border: 1px solid var(--amber); border-radius: 6px; color: var(--amber);
    font-weight: 600; font-size: 13px; letter-spacing: 0.5px; }

  .grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; }
  .tile { background: var(--panel); border: 1px solid var(--edge); border-radius: 8px;
          padding: 12px 14px; min-height: 128px; position: relative; }
  .tile.wide { grid-column: span 4; }
  .tile.feature { grid-column: span 2; border-color: #1f6feb55; }
  .tile.stale { border-color: var(--dn); }
  .tile-head { display: flex; align-items: baseline; gap: 8px; margin-bottom: 6px; }
  .tname { font-size: 12px; font-weight: 700; letter-spacing: 1px;
           text-transform: uppercase; color: var(--dim); }
  .lat { margin-left: auto; font-size: 10.5px; color: var(--faint);
         border: 1px solid var(--edge); border-radius: 4px; padding: 1px 6px;
         white-space: nowrap; }
  .big { font-family: Consolas, "Cascadia Mono", monospace; font-size: 34px;
         font-weight: 600; line-height: 1.1; }
  .feature .big { font-size: 46px; }
  .sub { font-size: 11px; color: var(--faint); margin-top: 1px; }
  .deltas { margin-top: 7px; font-family: Consolas, monospace; font-size: 14px; }
  .deltas .row { display: flex; gap: 8px; }
  .deltas .tag { color: var(--faint); font-size: 11.5px; min-width: 92px;
                 padding-top: 2px; }
  .up { color: var(--up); } .dn { color: var(--dn); } .flat { color: var(--flat); }
  .bl { color: var(--amber); }
  .stamp { margin-top: 8px; font-size: 10.5px; color: var(--faint);
           font-family: Consolas, monospace; }
  .stale-msg { margin-top: 6px; font-size: 11.5px; color: var(--dn);
               font-family: Consolas, monospace; font-weight: 600; }

  /* CRA strip */
  .strip { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px;
           margin-top: 4px; }
  .cell { background: #0d1117; border: 1px solid var(--edge); border-radius: 6px;
          padding: 8px 10px; }
  .cell .c-label { font-size: 12px; font-weight: 700; color: var(--accent);
                   font-family: Consolas, monospace; }
  .cell .c-q { font-size: 10px; color: var(--faint); margin-left: 6px; }
  .cell .c-rate { font-family: Consolas, monospace; font-size: 27px;
                  font-weight: 600; margin-top: 2px; }
  .cell .c-delta { font-family: Consolas, monospace; font-size: 12.5px;
                   margin-top: 2px; }
  .footnote { margin-top: 8px; font-size: 10.5px; color: var(--faint); }
</style>
</head>
<body>
<header>
  <h1>BoC decision-day live monitor</h1>
  <span id="clock" class="mono">--:--:-- ET</span>
  <span id="conn">connecting...</span>
  <span class="spacer"></span>
  <button id="freezeBtn">FREEZE BASELINE (decision drop)</button>
  <button id="clearBtn">CLEAR BASELINE</button>
</header>
<div id="frozenBanner"></div>
<div class="grid" id="grid"><div class="tile wide">loading...</div></div>

<script>
"use strict";
const LS_KEY = "boc_monitor_baseline_v1";
let latest = null;
let baseline = null;
try { baseline = JSON.parse(localStorage.getItem(LS_KEY)); } catch (e) {}

const $ = id => document.getElementById(id);

function fmt(v, dp) {
  if (v === null || v === undefined || isNaN(v)) return "--";
  return v.toLocaleString("en-CA", {minimumFractionDigits: dp, maximumFractionDigits: dp});
}
function sgn(v, dp, suffix) {
  if (v === null || v === undefined || isNaN(v)) return "--";
  if (v === 0) v = Math.abs(v);  // kill "-0.0" displays
  return (v > 0 ? "+" : "") + fmt(v, dp) + (suffix || "");
}
function cls(v) { return v > 0 ? "up" : (v < 0 ? "dn" : "flat"); }

function deltaRows(tagDay, htmlDay, htmlBase) {
  let h = '<div class="deltas"><div class="row"><span class="tag">' + tagDay +
          '</span><span>' + htmlDay + '</span></div>';
  if (baseline) {
    h += '<div class="row"><span class="tag bl">since decision</span><span>' +
         (htmlBase || '<span class="flat">--</span>') + '</span></div>';
  }
  return h + '</div>';
}

function stampLine(t) {
  let s = "";
  if (t.quote_time_et) s += "quote " + t.quote_time_et + " ET &middot; ";
  s += "fetched " + (t.fetched_at_et || "--") + " ET";
  return '<div class="stamp">' + s + '</div>';
}

function staleBlock(t) {
  if (t.ok) return "";
  return '<div class="stale-msg">STALE &mdash; last good ' +
         (t.last_good_et || "never") + ' ET<br>' + (t.error || "") + '</div>';
}

function yahooTile(t, opts) {
  if (!t) return "";
  const dp = opts.dp;
  let baseHtml = null;
  if (baseline && baseline.vals[t.key] != null && t.price != null) {
    const d = t.price - baseline.vals[t.key];
    const p = (t.price / baseline.vals[t.key] - 1) * 100;
    baseHtml = '<span class="' + cls(d) + '">' + sgn(p, 2, "%") +
               (opts.pips ? " (" + sgn(d * 10000, 0, " pips") + ")" : " (" + sgn(d, dp) + ")") +
               '</span>';
  }
  const dayHtml = t.day_pct == null ? '<span class="flat">--</span>'
    : '<span class="' + cls(t.day_pct) + '">' + sgn(t.day_pct, 2, "%") +
      (opts.pips ? " (" + sgn(t.day_chg * 10000, 0, " pips") + ")" : " (" + sgn(t.day_chg, dp) + ")") +
      '</span>';
  return '<div class="tile' + (opts.feature ? " feature" : "") + (t.ok ? "" : " stale") + '">' +
    '<div class="tile-head"><span class="tname">' + t.label + '</span>' +
    '<span class="lat">~live&ndash;15-min &middot; Yahoo</span></div>' +
    '<div class="big">' + fmt(t.price, dp) + '</div>' +
    deltaRows("vs prev close", dayHtml, baseHtml) +
    stampLine(t) + staleBlock(t) + '</div>';
}

function bondTile(t) {
  if (!t) return "";
  let baseHtml = null;
  if (baseline && baseline.vals[t.key] != null && t.last != null) {
    const d = t.last - baseline.vals[t.key];
    baseHtml = '<span class="' + cls(d) + '">' + sgn(d, 3) +
               ' px</span> <span class="flat">(yields ' + (d > 0 ? "&darr;" : (d < 0 ? "&uarr;" : "flat")) + ')</span>';
  }
  const dayHtml = '<span class="' + cls(t.day_chg) + '">' + sgn(t.day_chg, 3) +
    ' px</span> <span class="flat">(yields ' + (t.day_chg > 0 ? "&darr;" : (t.day_chg < 0 ? "&uarr;" : "flat")) + ')</span>';
  return '<div class="tile' + (t.ok ? "" : " stale") + '">' +
    '<div class="tile-head"><span class="tname">' + t.label + '</span>' +
    '<span class="lat">~15-min delayed &middot; MX</span></div>' +
    '<div class="big">' + fmt(t.last, 3) + '</div>' +
    '<div class="sub">' + (t.short || "") + ' &middot; prev settle ' + fmt(t.prev_settle, 3) +
    ' &middot; price &uarr; = yields &darr;</div>' +
    deltaRows("vs prev settle", dayHtml, baseHtml) +
    stampLine(t) + staleBlock(t) + '</div>';
}

function craTile(t, spread, spreadNote) {
  if (!t) return "";
  const adj = spread == null ? 0 : spread;
  let cells = "";
  (t.contracts || []).forEach(c => {
    const rate = c.implied_corra - adj;
    let baseHtml = "";
    if (baseline && baseline.cra && baseline.cra[c.short] != null) {
      const dbp = (c.implied_corra - baseline.cra[c.short]) * 100;
      baseHtml = '<div class="c-delta"><span class="bl">decision </span>' +
                 '<span class="' + cls(dbp) + '">' + sgn(dbp, 1, " bp") + '</span></div>';
    }
    cells += '<div class="cell"><span class="c-label">' + c.short + '</span>' +
      '<span class="c-q">' + (c.quarter || "") + '</span>' +
      '<div class="c-rate">' + fmt(rate, 2) + '%</div>' +
      '<div class="c-delta"><span style="color:var(--faint)">day </span>' +
      '<span class="' + cls(c.day_chg_bp) + '">' + sgn(c.day_chg_bp, 1, " bp") + '</span></div>' +
      baseHtml + '</div>';
  });
  return '<div class="tile wide' + (t.ok ? "" : " stale") + '">' +
    '<div class="tile-head"><span class="tname">Market-implied policy path &mdash; 3M CORRA futures (front ' +
    (t.contracts || []).length + ')</span>' +
    '<span class="lat">~15-min delayed &middot; Montreal Exchange</span></div>' +
    '<div class="strip">' + cells + '</div>' +
    '<div class="footnote">implied rate = 100 &minus; price &middot; ' + (spreadNote || "") +
    ' &middot; rate &darr; = market pricing MORE easing</div>' +
    stampLine(t) + staleBlock(t) + '</div>';
}

function render() {
  if (!latest) return;
  const y = latest.yahoo || {}, m = latest.mx || {};
  let h = "";
  h += craTile(m.cra, latest.spread, latest.spread_note);
  h += yahooTile(y.usdcad, {dp: 4, pips: true, feature: true});
  h += bondTile(m.cgz);
  h += bondTile(m.cgb);
  h += yahooTile(y.tsx, {dp: 0});
  h += bondTile(m.cgf);
  h += yahooTile(y.wti, {dp: 2});
  $("grid").innerHTML = h;

  $("freezeBtn").style.display = baseline ? "none" : "inline-block";
  $("clearBtn").style.display = baseline ? "inline-block" : "none";
  const banner = $("frozenBanner");
  if (baseline) {
    banner.style.display = "block";
    banner.innerHTML = "BASELINE FROZEN " + baseline.ts_et +
      " ET &mdash; every tile now shows change since the decision alongside change on the day";
  } else {
    banner.style.display = "none";
  }
}

function freeze() {
  if (!latest) { alert("No data yet - wait for tiles to populate."); return; }
  const vals = {}, cra = {};
  const y = latest.yahoo || {}, m = latest.mx || {};
  Object.keys(y).forEach(k => { if (y[k].price != null) vals[k] = y[k].price; });
  ["cgz", "cgf", "cgb"].forEach(k => { if (m[k] && m[k].last != null) vals[k] = m[k].last; });
  if (m.cra && m.cra.contracts) m.cra.contracts.forEach(c => { cra[c.short] = c.implied_corra; });
  baseline = {ts_et: latest.server_time_et, ts_ms: Date.now(), vals: vals, cra: cra};
  localStorage.setItem(LS_KEY, JSON.stringify(baseline));
  render();
}
function clearBaseline() {
  baseline = null;
  localStorage.removeItem(LS_KEY);
  render();
}
$("freezeBtn").addEventListener("click", freeze);
$("clearBtn").addEventListener("click", clearBaseline);

async function tick() {
  try {
    const r = await fetch("/data", {cache: "no-store"});
    latest = await r.json();
    $("conn").textContent = "server ok";
    $("conn").className = "";
    $("clock").textContent = latest.server_time_et + " ET";
    render();
  } catch (e) {
    $("conn").textContent = "SERVER UNREACHABLE - numbers below are frozen";
    $("conn").className = "bad";
  }
}
tick();
setInterval(tick, 5000);
</script>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description="BoC decision-day live monitor")
    ap.add_argument("--port", type=int, default=DEFAULT_PORT)
    ap.add_argument("--no-browser", action="store_true")
    args = ap.parse_args(argv)

    threading.Thread(target=_poll_yahoo_loop, daemon=True).start()
    threading.Thread(target=_poll_mx_loop, daemon=True).start()
    threading.Thread(target=_fetch_spread_once, daemon=True).start()

    url = f"http://127.0.0.1:{args.port}"
    server = ThreadingHTTPServer(("127.0.0.1", args.port), _Handler)
    print(f"BoC live monitor serving at {url}  (Ctrl+C to stop)")
    print("Tiles: CRA implied path, USDCAD, CGZ/CGF/CGB, TSX, WTI")
    print(f"Polls: Yahoo every {YAHOO_POLL_S}s, MX every {MX_POLL_S}s")
    if not args.no_browser:
        threading.Timer(0.8, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("stopped.")


if __name__ == "__main__":
    main()
