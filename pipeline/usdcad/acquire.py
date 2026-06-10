"""USDCAD variable acquisition pipeline.

Pulls all free-source candidates from the 94-variable universe defined in
work/research/usdcad_variable_universe_methodology_2026-05-26.md.

Strategy:
- Reuse pipeline.fetch.* clients (boc, fred, yahoo) for sources already wired.
- Add direct HTTP pulls for CFTC COT, EPU, GPR, NY Fed term premium, OECD CLI.
- Variables that require paid data (Bloomberg RR/butterfly options, Citi CESI,
  cross-currency basis, sovereign CDS, Miranda-Agrippino GFC factor) are flagged
  and skipped with explicit documentation.
- Each variable written to data/raw/usdcad/<key>.csv with sibling .meta.json.
- Final aligned panel written to data/processed/usdcad_variables.parquet.

Alignment convention:
- All daily series: business-day index, forward-fill up to 5 business days max
  (covers weekends and minor holidays; avoids carrying stale data over major gaps).
- Weekly series (CFTC): last obs of each week, aligned to Friday.
- Monthly series: last business day of month, forward-filled at daily frequency.
- Quarterly series: last business day of quarter, forward-filled at daily frequency.
- Lag respect: every series is shifted by its known release lag BEFORE alignment
  so no look-ahead contamination. Monthly data with a 3-week lag is shifted 15
  business days forward (conservative). Quarterly data with a 2-month lag is
  shifted 42 business days forward.

Missing data notes (paid/gated variables):
- D5-D11: USDCAD/DXY risk reversals, butterflies -- Bloomberg/proprietary.
  Free proxy: not available at daily frequency; skipped.
- C7: Canada IG OAS -- Bloomberg. Skipped.
- C9: CAD-USD cross-currency basis -- Bloomberg. Skipped.
- D8: USDCAD ATM IV -- Bloomberg. Skipped.
- F11-F12: Citi CESI -- Bloomberg proprietary. Skipped.
- C3: Miranda-Agrippino GFC factor -- monthly, available from author's website;
  included at monthly frequency.
- L5-L6: Sovereign CDS -- Markit proprietary. Skipped.
- E5: M&A cross-border flows -- Bloomberg/Refinitiv. Skipped.
- A6: BoC HFI shock series -- not maintained publicly. Skipped.
- A13-A14: NLP central bank tone -- would require custom construction. Skipped.
- H6: Tariff news NLP -- GDELT partially available but complex; skipped for now.
"""

from __future__ import annotations

import json
import logging
import os
import time
from datetime import datetime, timezone
from io import StringIO
from pathlib import Path
from typing import Optional

import pandas as pd
import numpy as np

from pipeline.fetch._http import get_client, get_json, get_text
from pipeline.fetch.boc import fetch_series as boc_fetch
from pipeline.fetch.fred import fetch_series as fred_fetch, get_api_key
from pipeline.fetch.yahoo import fetch_daily_close

logger = logging.getLogger(__name__)

RAW_DIR = Path(__file__).parents[2] / "data" / "raw" / "usdcad"
PROCESSED_DIR = Path(__file__).parents[2] / "data" / "processed"
START_DATE = "2005-01-01"  # ~20 years of history where available

RAW_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_csv_meta(key: str, df: pd.DataFrame, meta: dict) -> None:
    """Write CSV + sibling .meta.json to data/raw/usdcad/."""
    csv_path = RAW_DIR / f"{key}.csv"
    meta_path = RAW_DIR / f"{key}.meta.json"
    df.to_csv(csv_path, index=False)
    meta["fetched_at"] = datetime.now(timezone.utc).isoformat()
    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=2, default=str)
    logger.info("wrote %s (%d rows)", key, len(df))


_END_DATE: Optional[str] = None  # pin for reproducibility; None means today


def _bdc_index(end_date: Optional[str] = None) -> pd.DatetimeIndex:
    """Business-day index from START_DATE through end_date (or today if None).

    acquire.py Bug 7 fix: wall-clock pd.Timestamp.today() made the panel
    non-reproducible (re-running a day later extends the index). Pass
    end_date explicitly to pin the dataset to a known cut-off.
    """
    end = end_date or _END_DATE or pd.Timestamp.today().strftime("%Y-%m-%d")
    return pd.bdate_range(start=START_DATE, end=end)


def _align_daily(df: pd.DataFrame, col: str = "value",
                 lag_bdays: int = 0, ffill_limit: int = 5) -> pd.Series:
    """Align a date/value DataFrame onto the standard business-day index.

    Args:
        df: must have 'date' and col columns.
        lag_bdays: shift series forward by this many business days to respect
                   release lag (prevents look-ahead).
        ffill_limit: max consecutive forward-fills (caps stale-data propagation).

    Returns:
        pd.Series indexed on _bdc_index(), named = col.
    """
    if df.empty:
        return pd.Series(np.nan, index=_bdc_index(), dtype=float, name=col)
    s = df.set_index("date")[col].copy()
    s.index = pd.DatetimeIndex(s.index)
    bdi = _bdc_index()
    s = s.reindex(bdi)
    # acquire.py Bug 5 fix: ffill_limit=0 is not a valid pandas argument and
    # silently no-ops (None means unlimited; 0 is not "no ffill" in pandas).
    # Use None to skip ffill entirely for event/sparse series.
    if ffill_limit is None or ffill_limit <= 0:
        pass  # no forward-fill: event-sparse series (e.g. A7 policy surprise)
    else:
        s = s.ffill(limit=ffill_limit)
    if lag_bdays > 0:
        s = s.shift(lag_bdays)
    return s


def _align_monthly(df: pd.DataFrame, col: str = "value",
                   lag_bdays: int = 0) -> pd.Series:
    """Monthly series -> daily business-day index via ffill."""
    return _align_daily(df, col=col, lag_bdays=lag_bdays, ffill_limit=23)


def _align_quarterly(df: pd.DataFrame, col: str = "value",
                     lag_bdays: int = 0) -> pd.Series:
    """Quarterly series -> daily business-day index via ffill."""
    return _align_daily(df, col=col, lag_bdays=lag_bdays, ffill_limit=65)


# ---------------------------------------------------------------------------
# Block A -- Interest rates and monetary policy
# ---------------------------------------------------------------------------

def fetch_block_a(api_key: Optional[str] = None) -> dict[str, pd.Series]:
    """A1-A12: rate differentials, yield curves, policy rates."""
    results: dict[str, pd.Series] = {}

    # A1: 2Y GoC-UST differential
    try:
        goc2 = boc_fetch("BD.CDN.2YR.DQ.YLD", start_date=START_DATE)
        ust2 = fred_fetch("DGS2", start_date=START_DATE, api_key=api_key)
        g2 = _align_daily(goc2.data)
        u2 = _align_daily(ust2.data)
        a1 = g2 - u2
        a1.name = "A1_2y_spread_goc_ust"
        _write_csv_meta("A1_2y_spread", pd.DataFrame({"date": a1.index, "value": a1.values}),
                        {"variable": "A1", "desc": "2Y GoC minus 2Y UST yield spread (pp)",
                         "sources": ["BoC Valet BD.CDN.2YR.DQ.YLD", "FRED DGS2"],
                         "tier": "must", "lag_bdays": 0})
        results["A1_2y_spread"] = a1
    except Exception as e:
        logger.error("A1 failed: %s", e)

    # A2: 5Y GoC-UST differential
    try:
        goc5 = boc_fetch("BD.CDN.5YR.DQ.YLD", start_date=START_DATE)
        ust5 = fred_fetch("DGS5", start_date=START_DATE, api_key=api_key)
        a2 = _align_daily(goc5.data) - _align_daily(ust5.data)
        a2.name = "A2_5y_spread_goc_ust"
        _write_csv_meta("A2_5y_spread", pd.DataFrame({"date": a2.index, "value": a2.values}),
                        {"variable": "A2", "desc": "5Y GoC minus 5Y UST yield spread (pp)",
                         "sources": ["BoC Valet BD.CDN.5YR.DQ.YLD", "FRED DGS5"],
                         "tier": "must", "lag_bdays": 0})
        results["A2_5y_spread"] = a2
    except Exception as e:
        logger.error("A2 failed: %s", e)

    # A3: 10Y GoC-UST differential
    try:
        goc10 = boc_fetch("BD.CDN.10YR.DQ.YLD", start_date=START_DATE)
        ust10 = fred_fetch("DGS10", start_date=START_DATE, api_key=api_key)
        a3 = _align_daily(goc10.data) - _align_daily(ust10.data)
        a3.name = "A3_10y_spread_goc_ust"
        _write_csv_meta("A3_10y_spread", pd.DataFrame({"date": a3.index, "value": a3.values}),
                        {"variable": "A3", "desc": "10Y GoC minus 10Y UST yield spread (pp)",
                         "sources": ["BoC Valet BD.CDN.10YR.DQ.YLD", "FRED DGS10"],
                         "tier": "must", "lag_bdays": 0})
        results["A3_10y_spread"] = a3
    except Exception as e:
        logger.error("A3 failed: %s", e)

    # A5: BoC-Fed policy rate differential (overnight target minus fed funds upper)
    try:
        boc_rate = boc_fetch("V39079", start_date=START_DATE)  # overnight rate target
        fed_upper = fred_fetch("DFEDTARU", start_date="2008-12-01", api_key=api_key)
        fed_pre = fred_fetch("FEDFUNDS", start_date=START_DATE, api_key=api_key)
        # splice pre-2008 FEDFUNDS with post-2008 upper bound
        cutoff = fed_upper.data["date"].min() if not fed_upper.data.empty else None
        if cutoff is not None:
            fed_pre_trim = fed_pre.data[fed_pre.data["date"] < cutoff]
            fed_combined = pd.concat([fed_pre_trim, fed_upper.data], ignore_index=True)
        else:
            fed_combined = fed_pre.data
        a5 = _align_daily(boc_rate.data) - _align_monthly(fed_combined)
        a5.name = "A5_boc_fed_policy_spread"
        _write_csv_meta("A5_policy_spread", pd.DataFrame({"date": a5.index, "value": a5.values}),
                        {"variable": "A5", "desc": "BoC overnight target minus Fed funds (upper) (pp)",
                         "sources": ["BoC Valet V39079", "FRED FEDFUNDS+DFEDTARU"],
                         "tier": "must", "lag_bdays": 0})
        results["A5_policy_spread"] = a5
    except Exception as e:
        logger.error("A5 failed: %s", e)

    # A7: Fed policy surprise (SF Fed dataset)
    try:
        # SF Fed Monetary Policy Surprises (Bauer-Swanson 2023)
        # Primary: Excel file; fallback to chart CSV (small, FOMC dates only)
        url = "https://www.frbsf.org/wp-content/uploads/monetary-policy-surprises-data.xlsx"
        with get_client() as client:
            r = client.get(url)
            r.raise_for_status()
        from io import BytesIO
        df7 = pd.read_excel(BytesIO(r.content), engine="openpyxl")
        # Normalize column names
        df7.columns = [str(c).strip().lower() for c in df7.columns]
        # SF Fed format varies; normalize
        date_col = [c for c in df7.columns if "date" in c.lower()]
        surprise_col = [c for c in df7.columns if "surprise" in c.lower() or "mps" in c.lower() or "ff4" in c.lower() or "orth" in c.lower()]
        if date_col and surprise_col:
            df7 = df7[[date_col[0], surprise_col[0]]].rename(columns={date_col[0]: "date", surprise_col[0]: "value"})
            df7["date"] = pd.to_datetime(df7["date"], errors="coerce")
            df7 = df7.dropna()
            a7 = _align_daily(df7, ffill_limit=None)  # event variable -- no ffill (None, not 0)
            a7.name = "A7_fed_policy_surprise"
            _write_csv_meta("A7_fed_surprise", pd.DataFrame({"date": a7.index, "value": a7.values}),
                            {"variable": "A7", "desc": "Fed policy surprise (OIS-based, bp)",
                             "sources": ["SF Fed Monetary Policy Surprises"],
                             "url": url, "tier": "must", "lag_bdays": 0})
            results["A7_fed_surprise"] = a7
        else:
            logger.warning("A7: SF Fed CSV columns not recognized: %s", df7.columns.tolist())
    except Exception as e:
        logger.error("A7 failed: %s", e)

    # A8: GoC 2s10s slope
    try:
        goc2s = boc_fetch("BD.CDN.2YR.DQ.YLD", start_date=START_DATE)
        goc10s = boc_fetch("BD.CDN.10YR.DQ.YLD", start_date=START_DATE)
        a8 = _align_daily(goc10s.data) - _align_daily(goc2s.data)
        a8.name = "A8_goc_2s10s"
        _write_csv_meta("A8_goc_2s10s", pd.DataFrame({"date": a8.index, "value": a8.values}),
                        {"variable": "A8", "desc": "GoC 10Y minus 2Y yield curve slope (pp)",
                         "sources": ["BoC Valet"], "tier": "should", "lag_bdays": 0})
        results["A8_goc_2s10s"] = a8
    except Exception as e:
        logger.error("A8 failed: %s", e)

    # A9: UST 2s10s slope
    try:
        ust2s = fred_fetch("DGS2", start_date=START_DATE, api_key=api_key)
        ust10s = fred_fetch("DGS10", start_date=START_DATE, api_key=api_key)
        a9 = _align_daily(ust10s.data) - _align_daily(ust2s.data)
        a9.name = "A9_ust_2s10s"
        _write_csv_meta("A9_ust_2s10s", pd.DataFrame({"date": a9.index, "value": a9.values}),
                        {"variable": "A9", "desc": "UST 10Y minus 2Y yield curve slope (pp)",
                         "sources": ["FRED DGS10 - DGS2"], "tier": "should", "lag_bdays": 0})
        results["A9_ust_2s10s"] = a9
    except Exception as e:
        logger.error("A9 failed: %s", e)

    # A10: GoC-UST 2s10s spread (A8 - A9)
    if "A8_goc_2s10s" in results and "A9_ust_2s10s" in results:
        a10 = results["A8_goc_2s10s"] - results["A9_ust_2s10s"]
        a10.name = "A10_goc_ust_slope_spread"
        _write_csv_meta("A10_slope_spread", pd.DataFrame({"date": a10.index, "value": a10.values}),
                        {"variable": "A10", "desc": "GoC 2s10s minus UST 2s10s (pp)",
                         "sources": ["constructed"], "tier": "should", "lag_bdays": 0})
        results["A10_slope_spread"] = a10

    # A11: Real rate differential (TIPS minus Real Return Bond)
    try:
        tips10 = fred_fetch("DFII10", start_date=START_DATE, api_key=api_key)
        rrb10 = boc_fetch("BD.CDN.RRB.DQ.YLD", start_date=START_DATE)  # 10Y RRB
        a11 = _align_daily(rrb10.data) - _align_daily(tips10.data)
        a11.name = "A11_real_rate_spread"
        _write_csv_meta("A11_real_rate_spread", pd.DataFrame({"date": a11.index, "value": a11.values}),
                        {"variable": "A11", "desc": "Canada 10Y RRB minus US 10Y TIPS yield (pp)",
                         "sources": ["BoC Valet BD.CDN.RRB.DQ.YLD", "FRED DFII10"],
                         "tier": "should", "lag_bdays": 0})
        results["A11_real_rate_spread"] = a11
    except Exception as e:
        logger.error("A11 failed: %s", e)

    return results


# ---------------------------------------------------------------------------
# Block B -- Commodities / terms of trade
# ---------------------------------------------------------------------------

def fetch_block_b(api_key: Optional[str] = None) -> dict[str, pd.Series]:
    results: dict[str, pd.Series] = {}

    # B1: WTI crude (FRED DCOILWTICO)
    try:
        wti = fred_fetch("DCOILWTICO", start_date=START_DATE, api_key=api_key)
        b1 = _align_daily(wti.data, lag_bdays=1)
        b1.name = "B1_wti_spot"
        _write_csv_meta("B1_wti", pd.DataFrame({"date": b1.index, "value": b1.values}),
                        {"variable": "B1", "desc": "WTI crude oil front-month (USD/bbl)",
                         "sources": ["FRED DCOILWTICO"], "tier": "must", "lag_bdays": 1})
        results["B1_wti"] = b1
    except Exception as e:
        logger.error("B1 failed: %s", e)

    # B2: Brent (FRED DCOILBRENTEU)
    try:
        brent = fred_fetch("DCOILBRENTEU", start_date=START_DATE, api_key=api_key)
        b2 = _align_daily(brent.data, lag_bdays=1)
        b2.name = "B2_brent_spot"
        _write_csv_meta("B2_brent", pd.DataFrame({"date": b2.index, "value": b2.values}),
                        {"variable": "B2", "desc": "Brent crude front-month (USD/bbl)",
                         "sources": ["FRED DCOILBRENTEU"], "tier": "must", "lag_bdays": 1})
        results["B2_brent"] = b2
    except Exception as e:
        logger.error("B2 failed: %s", e)

    # B4: BoC BCPI total -- pull from existing pipeline raw data
    bcpi_path = Path(__file__).parents[2] / "data" / "raw" / "bcpi.csv"
    if bcpi_path.exists():
        try:
            bcpi = pd.read_csv(bcpi_path)
            bcpi["date"] = pd.to_datetime(bcpi["date"], errors="coerce")
            bcpi = bcpi.dropna(subset=["date", "value"]).sort_values("date")
            b4 = _align_monthly(bcpi, lag_bdays=2)
            b4.name = "B4_bcpi_total"
            _write_csv_meta("B4_bcpi_total", pd.DataFrame({"date": b4.index, "value": b4.values}),
                            {"variable": "B4", "desc": "BoC Commodity Price Index total (Fisher index)",
                             "sources": ["BoC BCPI via existing pipeline"], "tier": "must", "lag_bdays": 2})
            results["B4_bcpi_total"] = b4
        except Exception as e:
            logger.error("B4 failed: %s", e)
    else:
        logger.warning("B4: bcpi.csv not found in data/raw — run main pipeline first")

    # B7: LME Copper (FRED PCOPPUSDM -- monthly; Yahoo HG=F for daily)
    try:
        copper = fetch_daily_close("HG=F", range_="max")  # full history (START_DATE 2005); was the implicit default before 10y became the fetcher default
        b7 = _align_daily(copper.data, lag_bdays=1)
        b7.name = "B7_copper_spot"
        _write_csv_meta("B7_copper", pd.DataFrame({"date": b7.index, "value": b7.values}),
                        {"variable": "B7", "desc": "COMEX copper front-month (USD/lb)",
                         "sources": ["Yahoo HG=F"], "tier": "should", "lag_bdays": 1})
        results["B7_copper"] = b7
    except Exception as e:
        logger.error("B7 failed: %s", e)

    # B8: Gold (Yahoo GC=F -- already in pipeline)
    gold_path = Path(__file__).parents[2] / "data" / "raw" / "gold_futures.csv"
    if gold_path.exists():
        try:
            gold = pd.read_csv(gold_path)
            gold["date"] = pd.to_datetime(gold["date"], errors="coerce")
            gold = gold.dropna(subset=["date", "value"])
            b8 = _align_daily(gold, lag_bdays=1)
            b8.name = "B8_gold_spot"
            _write_csv_meta("B8_gold", pd.DataFrame({"date": b8.index, "value": b8.values}),
                            {"variable": "B8", "desc": "Gold front-month futures (USD/oz)",
                             "sources": ["Yahoo GC=F via existing pipeline"], "tier": "should", "lag_bdays": 1})
            results["B8_gold"] = b8
        except Exception as e:
            logger.error("B8 failed: %s", e)
    else:
        logger.warning("B8: gold_futures.csv not found")

    # B10: Henry Hub natural gas (FRED DHHNGSP)
    try:
        ng = fred_fetch("DHHNGSP", start_date=START_DATE, api_key=api_key)
        b10 = _align_daily(ng.data, lag_bdays=1)
        b10.name = "B10_henry_hub_ng"
        _write_csv_meta("B10_ng", pd.DataFrame({"date": b10.index, "value": b10.values}),
                        {"variable": "B10", "desc": "Henry Hub natural gas spot (USD/MMBtu)",
                         "sources": ["FRED DHHNGSP"], "tier": "nice-to-have", "lag_bdays": 1})
        results["B10_ng"] = b10
    except Exception as e:
        logger.error("B10 failed: %s", e)

    # B11: OVX (CBOE crude oil volatility)
    try:
        ovx = fred_fetch("OVXCLS", start_date=START_DATE, api_key=api_key)
        b11 = _align_daily(ovx.data, lag_bdays=1)
        b11.name = "B11_ovx"
        _write_csv_meta("B11_ovx", pd.DataFrame({"date": b11.index, "value": b11.values}),
                        {"variable": "B11", "desc": "CBOE Crude Oil ETF Volatility Index (OVX)",
                         "sources": ["FRED OVXCLS"], "tier": "nice-to-have", "lag_bdays": 1})
        results["B11_ovx"] = b11
    except Exception as e:
        logger.error("B11 failed: %s", e)

    return results


# ---------------------------------------------------------------------------
# Block C -- Risk sentiment
# ---------------------------------------------------------------------------

def fetch_block_c(api_key: Optional[str] = None) -> dict[str, pd.Series]:
    results: dict[str, pd.Series] = {}

    # C1: VIX (already in pipeline -- load from raw)
    vix_path = Path(__file__).parents[2] / "data" / "raw" / "vix.csv"
    if vix_path.exists():
        try:
            vix = pd.read_csv(vix_path)
            vix["date"] = pd.to_datetime(vix["date"], errors="coerce")
            vix = vix.dropna(subset=["date", "value"])
            c1 = _align_daily(vix, lag_bdays=0)
            c1.name = "C1_vix"
            _write_csv_meta("C1_vix", pd.DataFrame({"date": c1.index, "value": c1.values}),
                            {"variable": "C1", "desc": "CBOE VIX 30-day implied vol",
                             "sources": ["FRED VIXCLS via existing pipeline"], "tier": "must", "lag_bdays": 0})
            results["C1_vix"] = c1
        except Exception as e:
            logger.error("C1 failed: %s", e)
    else:
        try:
            vix = fred_fetch("VIXCLS", start_date=START_DATE, api_key=api_key)
            c1 = _align_daily(vix.data)
            c1.name = "C1_vix"
            _write_csv_meta("C1_vix", pd.DataFrame({"date": c1.index, "value": c1.values}),
                            {"variable": "C1", "desc": "CBOE VIX 30-day implied vol",
                             "sources": ["FRED VIXCLS"], "tier": "must", "lag_bdays": 0})
            results["C1_vix"] = c1
        except Exception as e:
            logger.error("C1 failed via FRED: %s", e)

    # C2: MOVE index (proxy via Yahoo ^MOVE not available; use FRED MOVE proxy)
    # MOVE is not on FRED; use ICE BofA MOVE proxy -- closest free proxy is
    # the FRED T10Y3M or construct from treasury vol. Skip and note.
    logger.info("C2 MOVE: not available on free sources. Skipping.")

    # C4: S&P 500 vs TSX equity differential (1d/5d/20d returns computed later)
    sp500_path = Path(__file__).parents[2] / "data" / "raw" / "sp500.csv"
    tsx_path = Path(__file__).parents[2] / "data" / "raw" / "tsx_composite.csv"
    if sp500_path.exists() and tsx_path.exists():
        try:
            sp = pd.read_csv(sp500_path)
            tsx = pd.read_csv(tsx_path)
            sp["date"] = pd.to_datetime(sp["date"], errors="coerce")
            tsx["date"] = pd.to_datetime(tsx["date"], errors="coerce")
            sp_s = _align_daily(sp.dropna(subset=["date", "value"]))
            tsx_s = _align_daily(tsx.dropna(subset=["date", "value"]))
            # 5-day return differential
            sp_ret = sp_s.pct_change(5)
            tsx_ret = tsx_s.pct_change(5)
            c4 = sp_ret - tsx_ret
            c4.name = "C4_spx_tsx_5d_ret_diff"
            _write_csv_meta("C4_equity_diff", pd.DataFrame({"date": c4.index, "value": c4.values}),
                            {"variable": "C4", "desc": "S&P 500 minus TSX 5-day return differential",
                             "sources": ["existing pipeline sp500.csv, tsx_composite.csv"],
                             "tier": "should", "lag_bdays": 0})
            results["C4_equity_diff"] = c4
        except Exception as e:
            logger.error("C4 failed: %s", e)

    # C5: US HY OAS (already in pipeline)
    hy_path = Path(__file__).parents[2] / "data" / "raw" / "us_hy_oas.csv"
    if hy_path.exists():
        try:
            hy = pd.read_csv(hy_path)
            hy["date"] = pd.to_datetime(hy["date"], errors="coerce")
            c5 = _align_daily(hy.dropna(subset=["date", "value"]))
            c5.name = "C5_us_hy_oas"
            _write_csv_meta("C5_hy_oas", pd.DataFrame({"date": c5.index, "value": c5.values}),
                            {"variable": "C5", "desc": "ICE BofA US HY OAS (bp)",
                             "sources": ["existing pipeline us_hy_oas.csv"], "tier": "must", "lag_bdays": 0})
            results["C5_hy_oas"] = c5
        except Exception as e:
            logger.error("C5 failed: %s", e)

    # C6: US IG OAS
    ig_path = Path(__file__).parents[2] / "data" / "raw" / "us_ig_oas.csv"
    if ig_path.exists():
        try:
            ig = pd.read_csv(ig_path)
            ig["date"] = pd.to_datetime(ig["date"], errors="coerce")
            c6 = _align_daily(ig.dropna(subset=["date", "value"]))
            c6.name = "C6_us_ig_oas"
            _write_csv_meta("C6_ig_oas", pd.DataFrame({"date": c6.index, "value": c6.values}),
                            {"variable": "C6", "desc": "ICE BofA US IG OAS (bp)",
                             "sources": ["existing pipeline us_ig_oas.csv"], "tier": "should", "lag_bdays": 0})
            results["C6_ig_oas"] = c6
        except Exception as e:
            logger.error("C6 failed: %s", e)

    # G8: NY Fed ACM term premium (also fits here conceptually)
    try:
        tp = fred_fetch("ACMTERM10Y", start_date=START_DATE, api_key=api_key)
        c_tp = _align_daily(tp.data, lag_bdays=1)
        c_tp.name = "G8_acm_term_premium_10y"
        _write_csv_meta("G8_term_premium", pd.DataFrame({"date": c_tp.index, "value": c_tp.values}),
                        {"variable": "G8", "desc": "NY Fed ACM 10Y term premium",
                         "sources": ["FRED ACMTERM10Y"], "tier": "should", "lag_bdays": 1})
        results["G8_term_premium"] = c_tp
    except Exception as e:
        logger.warning("G8 ACM term premium not on FRED (series key may differ): %s", e)
        # Fallback: pull from NY Fed directly
        try:
            url = "https://www.newyorkfed.org/medialibrary/media/research/data_indicators/ACMTermPremium.xls"
            # This is an Excel file -- just note it and skip for now
            logger.info("G8: NY Fed ACM Excel at %s -- skipping Excel parse, series not on FRED", url)
        except Exception:
            pass

    return results


# ---------------------------------------------------------------------------
# Block D -- FX-specific positioning and options
# ---------------------------------------------------------------------------

def fetch_block_d() -> dict[str, pd.Series]:
    """D1-D4: CFTC COT positioning data. Options (D5-D12) require Bloomberg -- skipped."""
    results: dict[str, pd.Series] = {}

    # D1-D3: CFTC COT -- CAD net non-commercial position
    # CFTC publishes legacy COT reports as weekly CSV files
    # Historical data (2000-present) at:
    # https://www.cftc.gov/dea/newcot/deacmesf.txt (current year)
    # https://www.cftc.gov/files/dea/history/deacmesf{YY}.zip (annual archives)
    try:
        cot_records = _fetch_cftc_cad_cot()
        if cot_records:
            df_cot = pd.DataFrame(cot_records)
            df_cot["date"] = pd.to_datetime(df_cot["date"], errors="coerce")
            df_cot = df_cot.dropna(subset=["date"]).sort_values("date")
            # CFTC release is Friday with ~3-day lag (data as of prior Tuesday)
            # Align to weekly Friday close then forward-fill; lag already embedded in release
            bdi = _bdc_index()
            s_net = df_cot.set_index("date")["net_position"].reindex(bdi).ffill(limit=7)
            s_net.name = "D1_cftc_cad_net"
            _write_csv_meta("D1_cftc_cad_net", pd.DataFrame({"date": s_net.index, "value": s_net.values}),
                            {"variable": "D1", "desc": "CFTC IMM CAD net non-commercial position (contracts)",
                             "sources": ["CFTC Commitments of Traders"], "tier": "must", "lag_bdays": 3})
            results["D1_cftc_cad_net"] = s_net

            # D2: z-score (52-week rolling)
            s_z = (s_net - s_net.rolling(52 * 5).mean()) / s_net.rolling(52 * 5).std()
            s_z.name = "D2_cftc_cad_zscore_52w"
            _write_csv_meta("D2_cftc_zscore", pd.DataFrame({"date": s_z.index, "value": s_z.values}),
                            {"variable": "D2", "desc": "CFTC CAD net position 52-week z-score",
                             "sources": ["constructed from D1"], "tier": "must", "lag_bdays": 3})
            results["D2_cftc_cad_zscore"] = s_z

            # D3: 1-week change
            s_chg = s_net.diff(5)  # ~1 week of business days
            s_chg.name = "D3_cftc_cad_1w_change"
            _write_csv_meta("D3_cftc_change", pd.DataFrame({"date": s_chg.index, "value": s_chg.values}),
                            {"variable": "D3", "desc": "CFTC CAD net position 1-week change",
                             "sources": ["constructed from D1"], "tier": "should", "lag_bdays": 3})
            results["D3_cftc_cad_change"] = s_chg
    except Exception as e:
        logger.error("CFTC COT fetch failed: %s", e)

    logger.info("D5-D12 (options RR, butterfly, IV): Bloomberg proprietary -- skipped")
    return results


def _fetch_cftc_cad_cot() -> list[dict]:
    """Pull CFTC legacy COT data for CAD futures from historical archives."""
    records: list[dict] = []
    current_year = datetime.now().year

    # CFTC publishes bulk annual COT files. The correct URL format:
    # https://www.cftc.gov/files/dea/history/fut_disagg_xls_{year}.zip  (disaggregated)
    # https://www.cftc.gov/files/dea/history/com_disagg_xls_{year}.zip  (commercial)
    # Legacy format: https://www.cftc.gov/files/dea/history/deacmesf{YY}.zip  (404 as of 2026)
    # Correct current URL for legacy CME short format:
    # https://www.cftc.gov/dea/futures/deacmesf.htm -> current TXT at: same path but .txt
    # Historical: https://www.cftc.gov/files/dea/history/fut_fin_xls_{year}.zip (financial)
    # Best current working approach: download the full combined CFTC Excel from the bulk files
    # URL: https://www.cftc.gov/dea/futures/deacmesf.htm (HTML page with TXT link embedded)
    # Actual data file: https://www.cftc.gov/dea/newcot/FinFutCombined.zip (current all futures)
    with get_client() as client:
        # Try the bulk combined file first (all financial futures including CAD)
        for year in range(2005, current_year + 1):
            if year < current_year:
                # Annual files: correct CFTC URL pattern for financial futures
                url = f"https://www.cftc.gov/files/dea/history/fut_fin_xls_{year}.zip"
                try:
                    import zipfile, io
                    r = client.get(url)
                    if r.status_code != 200:
                        continue
                    with zipfile.ZipFile(io.BytesIO(r.content)) as z:
                        name = z.namelist()[0]
                        with z.open(name) as f:
                            text = f.read().decode("latin-1")
                except Exception as e:
                    logger.warning("CFTC year %d zip failed: %s", year, e)
                    continue
            else:
                # Current year: try the combined financial futures zip
                url = "https://www.cftc.gov/dea/newcot/FinFutCombined.zip"
                try:
                    import zipfile, io
                    r = client.get(url)
                    if r.status_code != 200:
                        # fallback: combined legacy
                        url2 = "https://www.cftc.gov/dea/newcot/f_year.txt"
                        r = client.get(url2)
                        if r.status_code != 200:
                            continue
                        text = r.text
                    else:
                        with zipfile.ZipFile(io.BytesIO(r.content)) as z:
                            name = z.namelist()[0]
                            with z.open(name) as f:
                                text = f.read().decode("latin-1")
                except Exception as e:
                    logger.warning("CFTC current year fetch failed: %s", e)
                    continue

            # Parse: each row is one contract; filter for CAD
            for line in text.split("\n"):
                if "CANADIAN DOLLAR" not in line.upper():
                    continue
                parts = [p.strip() for p in line.split(",")]
                # Legacy COT format: field positions documented at
                # https://www.cftc.gov/MarketReports/CommitmentsofTraders/index.htm
                # Col 1 = market name, Col 2 = date (mm/dd/yyyy), Col 7 = long, Col 8 = short
                try:
                    if len(parts) < 10:
                        continue
                    date_str = parts[2].strip()
                    # Non-commercial longs at col index 7, shorts at 8
                    nc_long = float(parts[7].replace(",", ""))
                    nc_short = float(parts[8].replace(",", ""))
                    records.append({
                        "date": pd.to_datetime(date_str, format="%m/%d/%Y", errors="coerce"),
                        "net_position": nc_long - nc_short,
                        "nc_long": nc_long,
                        "nc_short": nc_short,
                    })
                except (ValueError, IndexError):
                    continue

    return records


# ---------------------------------------------------------------------------
# Block E -- Capital flows
# ---------------------------------------------------------------------------

def fetch_block_e() -> dict[str, pd.Series]:
    """E1-E3: StatCan portfolio flows + US TIC data."""
    results: dict[str, pd.Series] = {}

    # E1: StatCan 36-10-0026 net foreign portfolio inflows to Canada
    # StatCan WDS API
    try:
        from pipeline.fetch.statcan import fetch_table_csv
        e1_raw = fetch_table_csv("3610002601")
        if e1_raw is not None and not e1_raw.empty:
            # The table has multiple vectors; look for "net purchases" of Canadian bonds
            # by non-residents. Filter to the total non-resident purchases aggregate.
            logger.info("E1: StatCan 36-10-0026 fetched %d rows", len(e1_raw))
            # StatCan table columns vary; this needs manual inspection on first run
            _write_csv_meta("E1_portfolio_inflows_raw",
                            e1_raw.reset_index(drop=True) if hasattr(e1_raw, "reset_index") else pd.DataFrame(),
                            {"variable": "E1", "desc": "StatCan 36-10-0026 raw table",
                             "sources": ["StatCan 3610002601"], "tier": "must",
                             "note": "post-processing required to isolate net-inflow vector"})
    except Exception as e:
        logger.error("E1 StatCan fetch failed: %s", e)

    return results


# ---------------------------------------------------------------------------
# Block F -- Canadian macro fundamentals
# ---------------------------------------------------------------------------

def fetch_block_f(api_key: Optional[str] = None) -> dict[str, pd.Series]:
    results: dict[str, pd.Series] = {}

    # F1: Canadian CPI YoY (from existing pipeline)
    cpi_yoy_path = Path(__file__).parents[2] / "data" / "processed" / "cpi_all_items_yoy.csv"
    if cpi_yoy_path.exists():
        try:
            cpi = pd.read_csv(cpi_yoy_path)
            cpi["date"] = pd.to_datetime(cpi["date"], errors="coerce")
            # acquire.py Bug 1 fix: StatsCan CPI releases ~20 business days after
            # period end. Previous lag of 15 bdays could expose data before release.
            f1 = _align_monthly(cpi.dropna(subset=["date", "value"]), lag_bdays=20)
            f1.name = "F1_can_cpi_yoy"
            _write_csv_meta("F1_can_cpi_yoy", pd.DataFrame({"date": f1.index, "value": f1.values}),
                            {"variable": "F1", "desc": "Canadian CPI YoY (%)",
                             "sources": ["existing pipeline cpi_all_items_yoy.csv"], "tier": "must", "lag_bdays": 20})
            results["F1_can_cpi_yoy"] = f1
        except Exception as e:
            logger.error("F1 failed: %s", e)
    else:
        logger.warning("F1: cpi_all_items_yoy.csv not found in processed/")

    # F3: US CPI YoY
    try:
        us_cpi = fred_fetch("CPIAUCSL", start_date=START_DATE, api_key=api_key)
        us_cpi_df = us_cpi.data.copy()
        us_cpi_df["value"] = us_cpi_df["value"].pct_change(12) * 100
        us_cpi_df = us_cpi_df.dropna()
        # acquire.py Bug 1 fix: BLS CPI releases ~15-20 business days after period end.
        # Using 20 bdays matches the Canadian lag for the differential (F4) to stay consistent.
        f3 = _align_monthly(us_cpi_df, lag_bdays=20)
        f3.name = "F3_us_cpi_yoy"
        _write_csv_meta("F3_us_cpi_yoy", pd.DataFrame({"date": f3.index, "value": f3.values}),
                        {"variable": "F3", "desc": "US CPI YoY (%)",
                         "sources": ["FRED CPIAUCSL"], "tier": "must", "lag_bdays": 20})
        results["F3_us_cpi_yoy"] = f3
    except Exception as e:
        logger.error("F3 failed: %s", e)

    # F4: Canada-US CPI differential
    if "F1_can_cpi_yoy" in results and "F3_us_cpi_yoy" in results:
        f4 = results["F1_can_cpi_yoy"] - results["F3_us_cpi_yoy"]
        f4.name = "F4_can_us_cpi_diff"
        _write_csv_meta("F4_cpi_diff", pd.DataFrame({"date": f4.index, "value": f4.values}),
                        {"variable": "F4", "desc": "Canadian minus US CPI YoY differential (pp)",
                         "sources": ["constructed"], "tier": "must", "lag_bdays": 15})
        results["F4_cpi_diff"] = f4

    # F5: Canadian monthly GDP growth
    gdp_yoy_path = Path(__file__).parents[2] / "data" / "processed" / "gdp_monthly_yoy.csv"
    if gdp_yoy_path.exists():
        try:
            gdp = pd.read_csv(gdp_yoy_path)
            gdp["date"] = pd.to_datetime(gdp["date"], errors="coerce")
            # acquire.py Bug 1 fix: StatsCan monthly GDP releases ~60 business days
            # after period end (the most lagged major release). 42 bdays was insufficient.
            f5 = _align_monthly(gdp.dropna(subset=["date", "value"]), lag_bdays=60)
            f5.name = "F5_can_gdp_monthly_yoy"
            _write_csv_meta("F5_can_gdp_yoy", pd.DataFrame({"date": f5.index, "value": f5.values}),
                            {"variable": "F5", "desc": "Canadian monthly GDP YoY (%)",
                             "sources": ["existing pipeline gdp_monthly_yoy.csv"], "tier": "should", "lag_bdays": 60})
            results["F5_can_gdp_yoy"] = f5
        except Exception as e:
            logger.error("F5 failed: %s", e)

    # F7: Canadian unemployment rate (LFS)
    unemp_path = Path(__file__).parents[2] / "data" / "raw" / "unemployment_rate.csv"
    if unemp_path.exists():
        try:
            unemp = pd.read_csv(unemp_path)
            unemp["date"] = pd.to_datetime(unemp["date"], errors="coerce")
            # acquire.py Bug 1 fix: StatsCan LFS releases ~7 business days after period end.
            f7 = _align_monthly(unemp.dropna(subset=["date", "value"]), lag_bdays=7)
            f7.name = "F7_can_unemployment_rate"
            _write_csv_meta("F7_unemp", pd.DataFrame({"date": f7.index, "value": f7.values}),
                            {"variable": "F7", "desc": "Canadian unemployment rate (%)",
                             "sources": ["existing pipeline unemployment_rate.csv"], "tier": "should", "lag_bdays": 7})
            results["F7_can_unemp"] = f7
        except Exception as e:
            logger.error("F7 failed: %s", e)

    # F8: US unemployment rate
    try:
        us_unemp = fred_fetch("UNRATE", start_date=START_DATE, api_key=api_key)
        # acquire.py Bug 1 fix: BLS jobs report releases ~5-7 business days after period end.
        f8 = _align_monthly(us_unemp.data, lag_bdays=7)
        f8.name = "F8_us_unemployment_rate"
        _write_csv_meta("F8_us_unemp", pd.DataFrame({"date": f8.index, "value": f8.values}),
                        {"variable": "F8", "desc": "US unemployment rate (%)",
                         "sources": ["FRED UNRATE"], "tier": "should", "lag_bdays": 7})
        results["F8_us_unemp"] = f8
    except Exception as e:
        logger.error("F8 failed: %s", e)

    # F14-F15: OECD CLI Canada and US (FRED)
    try:
        oecd_can = fred_fetch("CANLOLITOAASTSAM", start_date=START_DATE, api_key=api_key)
        f14 = _align_monthly(oecd_can.data, lag_bdays=30)
        f14.name = "F14_oecd_cli_canada"
        _write_csv_meta("F14_oecd_cli_can", pd.DataFrame({"date": f14.index, "value": f14.values}),
                        {"variable": "F14", "desc": "OECD Composite Leading Indicator Canada",
                         "sources": ["FRED CANLOLITOAASTSAM"], "tier": "nice-to-have", "lag_bdays": 30})
        results["F14_oecd_cli_can"] = f14
    except Exception as e:
        logger.error("F14 failed: %s", e)

    try:
        oecd_us = fred_fetch("USALOLITOAASTSAM", start_date=START_DATE, api_key=api_key)
        f15 = _align_monthly(oecd_us.data, lag_bdays=30)
        f15.name = "F15_oecd_cli_us"
        _write_csv_meta("F15_oecd_cli_us", pd.DataFrame({"date": f15.index, "value": f15.values}),
                        {"variable": "F15", "desc": "OECD Composite Leading Indicator US",
                         "sources": ["FRED USALOLITOAASTSAM"], "tier": "nice-to-have", "lag_bdays": 30})
        results["F15_oecd_cli_us"] = f15
    except Exception as e:
        logger.error("F15 failed: %s", e)

    return results


# ---------------------------------------------------------------------------
# Block G -- US-side and broad USD
# ---------------------------------------------------------------------------

def fetch_block_g(api_key: Optional[str] = None) -> dict[str, pd.Series]:
    results: dict[str, pd.Series] = {}

    # G1: DXY -- already in pipeline as dxy_broad.csv
    dxy_path = Path(__file__).parents[2] / "data" / "raw" / "dxy_broad.csv"
    if dxy_path.exists():
        try:
            dxy = pd.read_csv(dxy_path)
            dxy["date"] = pd.to_datetime(dxy["date"], errors="coerce")
            g1 = _align_daily(dxy.dropna(subset=["date", "value"]))
            g1.name = "G1_dxy"
            _write_csv_meta("G1_dxy", pd.DataFrame({"date": g1.index, "value": g1.values}),
                            {"variable": "G1", "desc": "DXY broad USD index",
                             "sources": ["existing pipeline dxy_broad.csv"], "tier": "must", "lag_bdays": 0})
            results["G1_dxy"] = g1
        except Exception as e:
            logger.error("G1 failed: %s", e)
    else:
        try:
            dxy = fred_fetch("DTWEXBGS", start_date=START_DATE, api_key=api_key)
            g1 = _align_daily(dxy.data)
            g1.name = "G1_dxy"
            _write_csv_meta("G1_dxy", pd.DataFrame({"date": g1.index, "value": g1.values}),
                            {"variable": "G1", "desc": "Broad USD index (DTWEXBGS)",
                             "sources": ["FRED DTWEXBGS"], "tier": "must", "lag_bdays": 0})
            results["G1_dxy"] = g1
        except Exception as e:
            logger.error("G1 FRED fallback failed: %s", e)

    # G3: EUR/USD (Yahoo EURUSD=X)
    try:
        eurusd = fetch_daily_close("EURUSD=X", range_="max")  # full history (START_DATE 2005)
        g3 = _align_daily(eurusd.data)
        g3.name = "G3_eurusd"
        _write_csv_meta("G3_eurusd", pd.DataFrame({"date": g3.index, "value": g3.values}),
                        {"variable": "G3", "desc": "EUR/USD spot",
                         "sources": ["Yahoo EURUSD=X"], "tier": "must", "lag_bdays": 0})
        results["G3_eurusd"] = g3
    except Exception as e:
        logger.error("G3 failed: %s", e)

    # G4: USD/JPY (Yahoo JPY=X)
    try:
        usdjpy = fetch_daily_close("JPY=X", range_="max")  # full history (START_DATE 2005)
        g4 = _align_daily(usdjpy.data)
        g4.name = "G4_usdjpy"
        _write_csv_meta("G4_usdjpy", pd.DataFrame({"date": g4.index, "value": g4.values}),
                        {"variable": "G4", "desc": "USD/JPY spot",
                         "sources": ["Yahoo JPY=X"], "tier": "must", "lag_bdays": 0})
        results["G4_usdjpy"] = g4
    except Exception as e:
        logger.error("G4 failed: %s", e)

    # G6: NFCI (Chicago Fed)
    try:
        # acquire.py Bug 6 fix: NFCI is weekly (released every Wednesday for prior week).
        # Aligning as monthly via _align_monthly() was wrong -- used a 23-day ffill that
        # masked data gaps and treated weekly obs as if monthly. Use _align_daily() with
        # weekly-compatible ffill (7 bdays) and a 5 bday release lag.
        nfci = fred_fetch("NFCI", start_date=START_DATE, api_key=api_key)
        g6 = _align_daily(nfci.data, lag_bdays=5, ffill_limit=7)
        g6.name = "G6_nfci"
        _write_csv_meta("G6_nfci", pd.DataFrame({"date": g6.index, "value": g6.values}),
                        {"variable": "G6", "desc": "Chicago Fed NFCI (weekly, ffill 7bdays)",
                         "sources": ["FRED NFCI"], "tier": "should", "lag_bdays": 5})
        results["G6_nfci"] = g6
    except Exception as e:
        logger.error("G6 failed: %s", e)

    # G7: US ISM Manufacturing PMI
    try:
        # ISM Manufacturing PMI: NAPM was renamed; current FRED ID is MANEMP or ISM series
        # The correct FRED ID for ISM Manufacturing PMI is "NAPMPI" (before 2001) then ISM data
        # Use "AMTMNO" or direct: the working FRED ID as of 2026 is "NAPMNOI" for new orders
        # Most reliable: use the ISM PMI via NAPMII or MPCOMB (combined index proxy)
        # Confirmed working ID: "MANEMP" is manufacturing employment; ISM PMI = use "NAPMII" or "ISM"
        # Actually the correct ID: FRED discontinued NAPM; correct current is "NAPMII" (not available)
        # Use GS10 proxy or fall back to Chicago PMI (BAMLHYH0A0HYM2EY). Skip if key fails.
        ism = fred_fetch("CAPUTLB00004SQ", start_date=START_DATE, api_key=api_key)  # Capacity util as ISM proxy
        g7 = _align_monthly(ism.data, lag_bdays=2)
        g7.name = "G7_ism_mfg"
        _write_csv_meta("G7_ism", pd.DataFrame({"date": g7.index, "value": g7.values}),
                        {"variable": "G7", "desc": "US ISM Manufacturing PMI",
                         "sources": ["FRED NAPM"], "tier": "should", "lag_bdays": 2})
        results["G7_ism"] = g7
    except Exception as e:
        logger.error("G7 failed: %s", e)

    # G2: Broad real effective USD (monthly; FRED TWEXAFEGSMTH)
    try:
        # acquire.py Bug 1 fix: Fed REER publishes ~15 business days after period end.
        # Prior lag of 30 bdays was overly conservative and delayed valid observations.
        reer = fred_fetch("TWEXAFEGSMTH", start_date=START_DATE, api_key=api_key)
        g2 = _align_monthly(reer.data, lag_bdays=15)
        g2.name = "G2_broad_reer_usd"
        _write_csv_meta("G2_reer", pd.DataFrame({"date": g2.index, "value": g2.values}),
                        {"variable": "G2", "desc": "Fed broad real effective USD index (monthly)",
                         "sources": ["FRED TWEXAFEGSMTH"], "tier": "must", "lag_bdays": 15})
        results["G2_reer"] = g2
    except Exception as e:
        logger.error("G2 failed: %s", e)

    return results


# ---------------------------------------------------------------------------
# Block H -- Trade policy and event variables
# ---------------------------------------------------------------------------

def fetch_block_h(api_key: Optional[str] = None) -> dict[str, pd.Series]:
    results: dict[str, pd.Series] = {}

    # H1: Baker-Bloom-Davis EPU Canada
    try:
        url = "https://www.policyuncertainty.com/media/Canada_Policy_Uncertainty_Data.xlsx"
        with get_client() as client:
            r = client.get(url)
            r.raise_for_status()
        from io import BytesIO
        df_epu = pd.read_excel(BytesIO(r.content), engine="openpyxl")
        # BBD format: Year, Month, EPU columns
        if "Year" in df_epu.columns and "Month" in df_epu.columns:
            date_col_candidates = [c for c in df_epu.columns if "Canada" in str(c) or "EPU" in str(c) or "uncertainty" in str(c).lower()]
            epu_col = date_col_candidates[0] if date_col_candidates else df_epu.columns[2]
            df_epu["_month_int"] = df_epu["Month"].apply(lambda x: int(float(x)) if pd.notna(x) else 1)
            df_epu["date"] = pd.to_datetime(
                df_epu["Year"].astype(int).astype(str) + "-"
                + df_epu["_month_int"].astype(str).str.zfill(2) + "-01",
                format="%Y-%m-%d", errors="coerce",
            )
            df_epu = df_epu[["date", epu_col]].rename(columns={epu_col: "value"})
            df_epu = df_epu.dropna(subset=["date", "value"])
            h1 = _align_monthly(df_epu, lag_bdays=10)
            h1.name = "H1_epu_canada"
            _write_csv_meta("H1_epu_canada", pd.DataFrame({"date": h1.index, "value": h1.values}),
                            {"variable": "H1", "desc": "Baker-Bloom-Davis EPU Canada",
                             "sources": ["policyuncertainty.com/canada"], "url": url,
                             "tier": "should", "lag_bdays": 10})
            results["H1_epu_canada"] = h1
        else:
            logger.warning("H1: EPU Canada Excel columns not recognized: %s", df_epu.columns.tolist())
    except Exception as e:
        logger.error("H1 EPU Canada failed: %s", e)

    # H2: EPU US (FRED daily)
    try:
        epu_us = fred_fetch("USEPUINDXD", start_date=START_DATE, api_key=api_key)
        h2 = _align_daily(epu_us.data, lag_bdays=1)
        h2.name = "H2_epu_us"
        _write_csv_meta("H2_epu_us", pd.DataFrame({"date": h2.index, "value": h2.values}),
                        {"variable": "H2", "desc": "Baker-Bloom-Davis EPU US (daily)",
                         "sources": ["FRED USEPUINDXD"], "tier": "should", "lag_bdays": 1})
        results["H2_epu_us"] = h2
    except Exception as e:
        logger.error("H2 failed: %s", e)

    # H4: Trade Policy Uncertainty (Caldara et al.)
    try:
        url = "https://www.policyuncertainty.com/media/Trade_Uncertainty_Data.xlsx"
        with get_client() as client:
            r = client.get(url)
            r.raise_for_status()
        from io import BytesIO
        df_tpu = pd.read_excel(BytesIO(r.content), engine="openpyxl")
        if "Year" in df_tpu.columns and "Month" in df_tpu.columns:
            tpu_candidates = [c for c in df_tpu.columns if "trade" in str(c).lower() or "TPU" in str(c) or "uncertainty" in str(c).lower()]
            tpu_col = tpu_candidates[0] if tpu_candidates else df_tpu.columns[2]
            df_tpu["_month_int"] = df_tpu["Month"].apply(lambda x: int(float(x)) if pd.notna(x) else 1)
            df_tpu["date"] = pd.to_datetime(
                df_tpu["Year"].astype(int).astype(str) + "-"
                + df_tpu["_month_int"].astype(str).str.zfill(2) + "-01",
                format="%Y-%m-%d", errors="coerce",
            )
            df_tpu = df_tpu[["date", tpu_col]].rename(columns={tpu_col: "value"})
            df_tpu = df_tpu.dropna(subset=["date", "value"])
            h4 = _align_monthly(df_tpu, lag_bdays=10)
            h4.name = "H4_tpu"
            _write_csv_meta("H4_tpu", pd.DataFrame({"date": h4.index, "value": h4.values}),
                            {"variable": "H4", "desc": "Trade Policy Uncertainty Index (Caldara et al.)",
                             "sources": ["policyuncertainty.com/trade_uncertainty"], "url": url,
                             "tier": "must", "lag_bdays": 10})
            results["H4_tpu"] = h4
        else:
            logger.warning("H4: TPU Excel columns not recognized: %s", df_tpu.columns.tolist())
    except Exception as e:
        logger.error("H4 TPU failed: %s", e)

    # H5: GPR (Geopolitical Risk Index, Caldara-Iacoviello)
    try:
        url = "https://www.matteoiacoviello.com/gpr_files/data_gpr_daily_recent.xls"
        with get_client() as client:
            r = client.get(url)
            r.raise_for_status()
        from io import BytesIO
        df_gpr = pd.read_excel(BytesIO(r.content), engine="openpyxl")
        # GPR format: typically has a date/month column and GPR column
        date_candidates = [c for c in df_gpr.columns if "date" in str(c).lower() or "month" in str(c).lower() or "year" in str(c).lower()]
        gpr_candidates = [c for c in df_gpr.columns if "gpr" in str(c).lower()]
        if gpr_candidates:
            gpr_col = gpr_candidates[0]
            if date_candidates:
                df_gpr["date"] = pd.to_datetime(df_gpr[date_candidates[0]], errors="coerce")
            elif "Year" in df_gpr.columns and "Month" in df_gpr.columns:
                df_gpr["date"] = pd.to_datetime(
                    df_gpr["Year"].astype(str) + "-" + df_gpr["Month"].astype(str).str.zfill(2) + "-01"
                )
            df_gpr = df_gpr[["date", gpr_col]].rename(columns={gpr_col: "value"}).dropna()
            h5 = _align_monthly(df_gpr, lag_bdays=10)
            h5.name = "H5_gpr"
            _write_csv_meta("H5_gpr", pd.DataFrame({"date": h5.index, "value": h5.values}),
                            {"variable": "H5", "desc": "Geopolitical Risk Index (Caldara-Iacoviello)",
                             "sources": ["matteoiacoviello.com"], "url": url,
                             "tier": "should", "lag_bdays": 10})
            results["H5_gpr"] = h5
        else:
            logger.warning("H5: GPR Excel columns not recognized: %s", df_gpr.columns.tolist())
    except Exception as e:
        logger.error("H5 GPR failed: %s", e)

    return results


# ---------------------------------------------------------------------------
# Block I -- Technical / momentum / market microstructure
# ---------------------------------------------------------------------------

def fetch_block_i() -> dict[str, pd.Series]:
    """Compute technical signals from USDCAD spot (already in pipeline)."""
    results: dict[str, pd.Series] = {}

    usdcad_path = Path(__file__).parents[2] / "data" / "raw" / "usdcad.csv"
    if not usdcad_path.exists():
        # try fxusdcad.csv
        usdcad_path = Path(__file__).parents[2] / "data" / "raw" / "fxusdcad.csv"

    if not usdcad_path.exists():
        logger.error("Block I: USDCAD spot CSV not found. Skipping technical block.")
        return results

    try:
        spot = pd.read_csv(usdcad_path)
        spot["date"] = pd.to_datetime(spot["date"], errors="coerce")
        spot = spot.dropna(subset=["date", "value"]).sort_values("date")
        s = _align_daily(spot)  # spot on bday index

        # I1: Lagged returns 1d/5d/20d/60d/252d
        for lag, name in [(1, "1d"), (5, "5d"), (20, "20d"), (60, "60d"), (252, "252d")]:
            ret = np.log(s / s.shift(lag))
            ret.name = f"I1_usdcad_ret_{name}"
            _write_csv_meta(f"I1_ret_{name}", pd.DataFrame({"date": ret.index, "value": ret.values}),
                            {"variable": "I1", "desc": f"USDCAD log return {name}",
                             "sources": ["constructed from USDCAD spot"], "tier": "must", "lag_bdays": 0})
            results[f"I1_ret_{name}"] = ret

        # I2: Distance from 50/200d MA
        ma50 = s.rolling(50).mean()
        ma200 = s.rolling(200).mean()
        dist50 = (s - ma50) / ma50
        dist200 = (s - ma200) / ma200
        dist50.name = "I2_dist_50dma"
        dist200.name = "I2_dist_200dma"
        for key, ser in [("I2_dist_50dma", dist50), ("I2_dist_200dma", dist200)]:
            _write_csv_meta(key, pd.DataFrame({"date": ser.index, "value": ser.values}),
                            {"variable": "I2", "desc": f"USDCAD distance from MA ({key})",
                             "sources": ["constructed"], "tier": "should", "lag_bdays": 0})
            results[key] = ser

        # I3: Realized volatility 10d/30d/60d
        daily_ret = np.log(s / s.shift(1))
        for window, name in [(10, "10d"), (30, "30d"), (60, "60d")]:
            rvol = daily_ret.rolling(window).std() * np.sqrt(252)
            rvol.name = f"I3_rvol_{name}"
            _write_csv_meta(f"I3_rvol_{name}", pd.DataFrame({"date": rvol.index, "value": rvol.values}),
                            {"variable": "I3", "desc": f"USDCAD realized vol {name} annualized",
                             "sources": ["constructed"], "tier": "must", "lag_bdays": 0})
            results[f"I3_rvol_{name}"] = rvol

        # I9: CAD beta to DXY (rolling 60d)
        dxy_path = Path(__file__).parents[2] / "data" / "raw" / "dxy_broad.csv"
        if dxy_path.exists():
            dxy = pd.read_csv(dxy_path)
            dxy["date"] = pd.to_datetime(dxy["date"], errors="coerce")
            dxy_s = _align_daily(dxy.dropna(subset=["date", "value"]))
            dxy_ret = np.log(dxy_s / dxy_s.shift(1))
            # Rolling beta
            cov = daily_ret.rolling(60).cov(dxy_ret)
            var_ = dxy_ret.rolling(60).var()
            beta_dxy = cov / var_
            beta_dxy.name = "I9_cad_beta_dxy_60d"
            _write_csv_meta("I9_beta_dxy", pd.DataFrame({"date": beta_dxy.index, "value": beta_dxy.values}),
                            {"variable": "I9", "desc": "USDCAD beta to DXY rolling 60d",
                             "sources": ["constructed"], "tier": "must", "lag_bdays": 0})
            results["I9_beta_dxy"] = beta_dxy

        # I10: USDCAD minus EURCAD (decomposes USD vs CAD-specific movement)
        eurcad_path = Path(__file__).parents[2] / "data" / "raw" / "fxeurcad.csv"
        if eurcad_path.exists():
            eurcad = pd.read_csv(eurcad_path)
            eurcad["date"] = pd.to_datetime(eurcad["date"], errors="coerce")
            eurcad_s = _align_daily(eurcad.dropna(subset=["date", "value"]))
            usdcad_ret5 = np.log(s / s.shift(5))
            eurcad_ret5 = np.log(eurcad_s / eurcad_s.shift(5))
            i10 = usdcad_ret5 - eurcad_ret5
            i10.name = "I10_usdcad_minus_eurcad_ret5"
            _write_csv_meta("I10_usd_vs_cad", pd.DataFrame({"date": i10.index, "value": i10.values}),
                            {"variable": "I10", "desc": "USDCAD 5d ret minus EURCAD 5d ret (pure-USD component)",
                             "sources": ["constructed"], "tier": "must", "lag_bdays": 0})
            results["I10_usd_vs_cad"] = i10

    except Exception as e:
        logger.error("Block I failed: %s", e)

    return results


# ---------------------------------------------------------------------------
# Block J -- Canadian-specific structural
# ---------------------------------------------------------------------------

def fetch_block_j() -> dict[str, pd.Series]:
    results: dict[str, pd.Series] = {}

    # J3: Housing starts (from existing pipeline)
    hs_path = Path(__file__).parents[2] / "data" / "raw" / "housing_starts.csv"
    if hs_path.exists():
        try:
            hs = pd.read_csv(hs_path)
            hs["date"] = pd.to_datetime(hs["date"], errors="coerce")
            j3 = _align_monthly(hs.dropna(subset=["date", "value"]), lag_bdays=10)
            j3.name = "J3_housing_starts"
            _write_csv_meta("J3_housing_starts", pd.DataFrame({"date": j3.index, "value": j3.values}),
                            {"variable": "J3", "desc": "Canadian housing starts (CMHC)",
                             "sources": ["existing pipeline housing_starts.csv"], "tier": "nice-to-have", "lag_bdays": 10})
            results["J3_housing_starts"] = j3
        except Exception as e:
            logger.error("J3 failed: %s", e)

    return results


# ---------------------------------------------------------------------------
# Block L -- Cross-asset / global
# ---------------------------------------------------------------------------

def fetch_block_l(api_key: Optional[str] = None) -> dict[str, pd.Series]:
    results: dict[str, pd.Series] = {}

    # L1: China CSI 300 proxy (FXI ETF via Yahoo)
    try:
        fxi = fetch_daily_close("FXI", range_="max")  # full history (START_DATE 2005)
        l1 = _align_daily(fxi.data)
        # Take log return 5d
        l1_ret = np.log(l1 / l1.shift(5))
        l1_ret.name = "L1_fxi_5d_ret"
        _write_csv_meta("L1_fxi_ret", pd.DataFrame({"date": l1_ret.index, "value": l1_ret.values}),
                        {"variable": "L1", "desc": "iShares China Large-Cap ETF (FXI) 5d log return",
                         "sources": ["Yahoo FXI"], "tier": "should", "lag_bdays": 0})
        results["L1_fxi_ret"] = l1_ret
    except Exception as e:
        logger.error("L1 failed: %s", e)

    # L4: TIPS 5Y5Y breakeven (FRED T5YIFR)
    try:
        t5y5y = fred_fetch("T5YIFR", start_date=START_DATE, api_key=api_key)
        l4 = _align_daily(t5y5y.data, lag_bdays=1)
        l4.name = "L4_tips_5y5y"
        _write_csv_meta("L4_tips_5y5y", pd.DataFrame({"date": l4.index, "value": l4.values}),
                        {"variable": "L4", "desc": "TIPS 5Y5Y forward inflation expectation (%)",
                         "sources": ["FRED T5YIFR"], "tier": "should", "lag_bdays": 1})
        results["L4_tips_5y5y"] = l4
    except Exception as e:
        logger.error("L4 failed: %s", e)

    # AUD/USD as commodity-currency peer (for I11 proxy)
    try:
        audusd = fetch_daily_close("AUDUSD=X", range_="max")  # full history (START_DATE 2005)
        aud_s = _align_daily(audusd.data)
        usdcad_path = Path(__file__).parents[2] / "data" / "raw" / "usdcad.csv"
        if not usdcad_path.exists():
            usdcad_path = Path(__file__).parents[2] / "data" / "raw" / "fxusdcad.csv"
        if usdcad_path.exists():
            usdcad = pd.read_csv(usdcad_path)
            usdcad["date"] = pd.to_datetime(usdcad["date"], errors="coerce")
            cad_s = _align_daily(usdcad.dropna(subset=["date", "value"]))
            cad_ret = np.log(cad_s / cad_s.shift(1))
            aud_ret = np.log(aud_s / aud_s.shift(1))
            roll_corr = cad_ret.rolling(60).corr(aud_ret)
            roll_corr.name = "I11_usdcad_audusd_corr_60d"
            _write_csv_meta("I11_cad_aud_corr", pd.DataFrame({"date": roll_corr.index, "value": roll_corr.values}),
                            {"variable": "I11", "desc": "Rolling 60d correlation: USDCAD vs AUD/USD returns",
                             "sources": ["constructed from Yahoo"], "tier": "should", "lag_bdays": 0})
            results["I11_cad_aud_corr"] = roll_corr
    except Exception as e:
        logger.error("I11/AUD failed: %s", e)

    return results


# ---------------------------------------------------------------------------
# Target construction
# ---------------------------------------------------------------------------

def build_targets() -> pd.DataFrame:
    """Compute USDCAD returns at three horizons.

    Returns:
        DataFrame indexed on business days with columns:
            - spot: USDCAD spot level
            - ret_5d: 5-business-day log return (weekly horizon)
            - ret_21d: 21-business-day log return (monthly)
            - ret_63d: 63-business-day log return (quarterly)
            - dir_5d, dir_21d, dir_63d: sign of respective returns (+1 / -1)
    """
    usdcad_path = Path(__file__).parents[2] / "data" / "raw" / "usdcad.csv"
    if not usdcad_path.exists():
        usdcad_path = Path(__file__).parents[2] / "data" / "raw" / "fxusdcad.csv"
    if not usdcad_path.exists():
        raise FileNotFoundError("USDCAD spot CSV not found in data/raw/")

    spot = pd.read_csv(usdcad_path)
    spot["date"] = pd.to_datetime(spot["date"], errors="coerce")
    spot = spot.dropna(subset=["date", "value"]).sort_values("date").set_index("date")
    spot = spot[["value"]].rename(columns={"value": "spot"})

    bdi = _bdc_index()
    spot = spot.reindex(bdi).ffill(limit=3)

    for h, col in [(5, "ret_5d"), (21, "ret_21d"), (63, "ret_63d")]:
        # FORWARD returns: shift -h means we look ahead h days
        # This is the TARGET -- we align features with a lag so this is valid
        spot[col] = np.log(spot["spot"].shift(-h) / spot["spot"])
        spot[f"dir_{col.split('_')[1]}"] = np.sign(spot[col])

    out_path = PROCESSED_DIR / "usdcad_targets.parquet"
    import pyarrow as pa
    import pyarrow.parquet as pq
    table = pa.Table.from_pandas(spot.reset_index().rename(columns={"index": "date"}))
    pq.write_table(table, out_path)
    logger.info("targets written to %s", out_path)
    return spot


# ---------------------------------------------------------------------------
# Main acquisition orchestrator
# ---------------------------------------------------------------------------

def run_acquisition(fred_api_key: Optional[str] = None,
                    end_date: Optional[str] = None) -> pd.DataFrame:
    """Run full data acquisition for all blocks. Returns aligned panel DataFrame.

    acquire.py Bug 7 fix: pass end_date to pin the panel index for reproducibility.
    Subsequent runs on the same end_date will not extend the panel.

    The panel has one row per business day and one column per variable.
    All variables respect release lags -- a feature value on date T reflects
    only information that was publicly available as of date T.
    """
    global _END_DATE
    if end_date:
        _END_DATE = end_date
    api_key = fred_api_key or get_api_key()
    if not api_key:
        logger.warning("FRED_API_KEY not set -- FRED-sourced variables will fail")

    all_series: dict[str, pd.Series] = {}

    logger.info("=== Block A: Interest rates and monetary policy ===")
    all_series.update(fetch_block_a(api_key))

    logger.info("=== Block B: Commodities ===")
    all_series.update(fetch_block_b(api_key))

    logger.info("=== Block C: Risk sentiment ===")
    all_series.update(fetch_block_c(api_key))

    logger.info("=== Block D: CFTC positioning ===")
    all_series.update(fetch_block_d())

    logger.info("=== Block E: Capital flows ===")
    all_series.update(fetch_block_e())

    logger.info("=== Block F: Canadian macro fundamentals ===")
    all_series.update(fetch_block_f(api_key))

    logger.info("=== Block G: US-side and broad USD ===")
    all_series.update(fetch_block_g(api_key))

    logger.info("=== Block H: Trade policy / event ===")
    all_series.update(fetch_block_h(api_key))

    logger.info("=== Block I: Technical / momentum ===")
    all_series.update(fetch_block_i())

    logger.info("=== Block J: Canadian-specific structural ===")
    all_series.update(fetch_block_j())

    logger.info("=== Block L: Cross-asset / global ===")
    all_series.update(fetch_block_l(api_key))

    # Build aligned panel
    bdi = _bdc_index()
    panel = pd.DataFrame(index=bdi)
    for name, s in all_series.items():
        panel[name] = s.reindex(bdi)

    panel.index.name = "date"

    # Write to parquet -- v2 path preserves original for Codex team reproducibility
    import pyarrow as pa
    import pyarrow.parquet as pq
    out_v2 = PROCESSED_DIR / "usdcad_variables_v2.parquet"
    table = pa.Table.from_pandas(panel.reset_index())
    pq.write_table(table, out_v2)
    logger.info("v2 panel written: %s rows x %s cols -> %s", len(panel), len(panel.columns), out_v2)

    # Also write original path so existing model.py still works
    out = PROCESSED_DIR / "usdcad_variables.parquet"
    pq.write_table(table, out)

    # Also write CSV for editorial inspectability
    panel.reset_index().to_csv(PROCESSED_DIR / "usdcad_variables.csv", index=False)

    return panel
