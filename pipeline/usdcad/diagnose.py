"""HTML diagnostic companion generator for USDCAD modeling -- Phase 3.

Phase 3 additions vs Phase 2:
  - Section 11: Hold-out performance (the genuinely out-of-sample test)
  - Section 12: Data transformations applied (explicit audit table)
  - All existing sections preserved and updated for Phase 3 result structure
  - Score visualizations updated to show hold-out period distinctly

Readability rebuild (2026-05-26):
  - Executive summary at top (one screen, Jay can decide to keep reading in 2 min)
  - Sections reordered: exec summary -> score in action -> hold-out -> extremes ->
    variable importance -> methodology overview -> caveats -> appendix
  - Every chart has a plain-English "What this shows" intro and "What we conclude"
    closing line
  - Tables-of-numbers moved to appendix; charts lead
  - Horizon-specific caveats (quarterly thinness, monthly CV failure, weekly general
    signal weakness) called out where relevant, not buried at end

Produces one self-contained HTML file per horizon. All Plotly charts are
embedded inline. Opens in any browser.
"""

from __future__ import annotations

import logging
from pathlib import Path

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

OUTPUT_DIR = Path(__file__).parents[2] / "work" / "research" / "usdcad"

# Variable metadata for the universe table
VARIABLE_CATALOG = {
    "A1_2y_spread": ("A1", "2Y GoC-UST yield differential", "Must", "Block A", "UIP / interest-rate parity; widening spread = CAD appreciation expected in textbook, reversed in data"),
    "A2_5y_spread": ("A2", "5Y GoC-UST yield differential", "Must", "Block A", "Long-end captures real-rate and term-premium components separately from policy"),
    "A3_10y_spread": ("A3", "10Y GoC-UST yield differential", "Must", "Block A", "Long-horizon expected real rates and term premia"),
    "A5_policy_spread": ("A5", "BoC-Fed policy rate differential", "Must", "Block A", "Anchor for textbook UIP; modest standalone power per BoC SAN 2025-2"),
    "A7_fed_surprise": ("A7", "Fed policy decision surprise (OIS-based)", "Must", "Block A", "High-frequency identification of pure FOMC monetary shock; Bauer-Swanson evidence on USD moves"),
    "A8_goc_2s10s": ("A8", "GoC 2s10s yield curve slope", "Should", "Block A", "Term-premium / growth expectation proxy; Nelson-Siegel factors predict carry returns"),
    "A9_ust_2s10s": ("A9", "UST 2s10s yield curve slope", "Should", "Block A", "Same as A8 for the US; cross-country slope differential is A10"),
    "A10_slope_spread": ("A10", "GoC-UST 2s10s differential", "Should", "Block A", "Difference in growth/term-premium expectations between Canada and US"),
    "A11_real_rate_spread": ("A11", "Real rate differential (RRB minus TIPS 10Y)", "Should", "Block A", "Strips inflation expectations from nominal; UIP works better in real terms (Engel)"),
    "B1_wti": ("B1", "WTI crude oil spot", "Must", "Block B", "Canada is net energy exporter; CAD-oil link has weakened post-2016 (BoC SAN 2017-1)"),
    "B2_brent": ("B2", "Brent crude oil spot", "Must", "Block B", "Global oil benchmark; Brent-WTI differential captures Canadian-specific takeaway constraints"),
    "B4_bcpi_total": ("B4", "BoC BCPI total (all commodities)", "Must", "Block B", "Fisher index of 26 commodities weighted by Canadian production -- BoC preferred terms-of-trade measure"),
    "B7_copper": ("B7", "COMEX copper", "Should", "Block B", "Global growth proxy; Canada has copper exports; leading indicator for industrial activity"),
    "B8_gold": ("B8", "Gold spot (COMEX GC=F)", "Should", "Block B", "Negatively correlated with USD; safe-haven proxy that flips in risk-off episodes"),
    "B10_ng": ("B10", "Henry Hub natural gas spot", "Nice-to-have", "Block B", "Canada exports LNG to US; smaller weight than oil in BCPI; mostly priced in USD"),
    "B11_ovx": ("B11", "CBOE crude oil volatility (OVX)", "Nice-to-have", "Block B", "Volatility of terms-of-trade matters separately from level"),
    "C1_vix": ("C1", "VIX (CBOE S&P 30d implied vol)", "Must", "Block C", "Global risk-appetite proxy; high VIX = USD safe-haven demand; carry unwind channel"),
    "C4_equity_diff": ("C4", "S&P 500 vs TSX 5d return differential", "Should", "Block C", "Relative equity performance proxy for relative growth; positive = US outperforming Canada"),
    "C5_hy_oas": ("C5", "US HY OAS (ICE BofA)", "Must", "Block C", "Risk-appetite proxy; widens with USD strength; credit risk correlates with FX risk premium"),
    "C6_ig_oas": ("C6", "US IG OAS", "Should", "Block C", "Investment-grade variant; less noisy than HY but same directional information"),
    "G8_term_premium": ("G8", "NY Fed ACM 10Y term premium", "Should", "Block G", "Strips expected rates from bond yield; Cieslak-Pflueger-Pavlova regime classifier"),
    "D1_cftc_cad_net": ("D1", "CFTC CAD net non-commercial position", "Must", "Block D", "IMM speculative positioning; extremes predict reversals (practitioner use)"),
    "D2_cftc_cad_zscore": ("D2", "CFTC CAD position z-score (52w)", "Must", "Block D", "Captures how extreme positioning is relative to own history"),
    "D3_cftc_cad_change": ("D3", "CFTC CAD net position 1-week change", "Should", "Block D", "Flow proxy -- change in positioning rather than level"),
    "F1_can_cpi_yoy": ("F1", "Canadian CPI YoY", "Must", "Block F", "Inflation differential drives expected real rates; Engel-West present-value fundamental"),
    "F3_us_cpi_yoy": ("F3", "US CPI YoY", "Must", "Block F", "US-side of the inflation differential; needed to compute F4"),
    "F4_cpi_diff": ("F4", "Canada-US CPI differential", "Must", "Block F", "Real-rate driver; direct Engel-West fundamental"),
    "F5_can_gdp_yoy": ("F5", "Canadian monthly GDP YoY", "Should", "Block F", "Growth differential drives medium-term real exchange rate; 60-day release lag limits timeliness"),
    "F7_can_unemp": ("F7", "Canadian unemployment rate (LFS)", "Should", "Block F", "Labour market slack; released ~first Friday of following month"),
    "F8_us_unemp": ("F8", "US unemployment rate", "Should", "Block F", "US-side labour market; needed for cross-country comparison"),
    "F14_oecd_cli_can": ("F14", "OECD Composite Leading Indicator Canada", "Nice-to-have", "Block F", "Composite of consumer confidence, manufacturing orders, stock performance, housing"),
    "F15_oecd_cli_us": ("F15", "OECD Composite Leading Indicator US", "Nice-to-have", "Block F", "US equivalent; differential captures relative growth momentum"),
    "G1_dxy": ("G1", "DXY broad USD index", "Must", "Block G", "Broad-USD strength -- Lustig-Roussanov-Verdelhan dollar factor"),
    "G2_reer": ("G2", "Fed broad real effective USD (REER)", "Must", "Block G", "Trade-weighted inflation-adjusted USD; better measure of long-run competitiveness than DXY"),
    "G3_eurusd": ("G3", "EUR/USD spot", "Must", "Block G", "Largest DXY weight; non-redundant because EUR has own drivers"),
    "G4_usdjpy": ("G4", "USD/JPY spot (funding currency proxy)", "Must", "Block G", "Carry-trade funding currency; JPY strength in carry unwinds drives USD weakness globally"),
    "G6_nfci": ("G6", "Chicago Fed NFCI", "Should", "Block G", "Composite financial conditions index; free alternative to GS FCI; weekly"),
    "G7_ism": ("G7", "US ISM Manufacturing PMI", "Should", "Block G", "Real-time US growth proxy; first business day of next month"),
    "H1_epu_canada": ("H1", "Baker-Bloom-Davis EPU Canada", "Should", "Block H", "Policy uncertainty depresses CAD investment and weakens currency"),
    "H2_epu_us": ("H2", "Baker-Bloom-Davis EPU US (daily)", "Should", "Block H", "US-side policy uncertainty; USD safe-haven during US-specific uncertainty spikes"),
    "H4_tpu": ("H4", "Trade Policy Uncertainty Index (Caldara et al.)", "Must", "Block H", "Tariff / CUSMA-specific risk -- dominant CAD driver in 2025-2026 tariff regime"),
    "H5_gpr": ("H5", "Geopolitical Risk Index (Caldara-Iacoviello AER 2022)", "Should", "Block H", "Geopolitical risk affects USD haven demand and CAD commodity channel simultaneously"),
    "I1_ret_1d": ("I1a", "USDCAD 1-day log return", "Must", "Block I", "Momentum/mean-reversion"),
    "I1_ret_5d": ("I1b", "USDCAD 5-day log return", "Must", "Block I", "Weekly momentum -- most robust horizon for currency momentum per AQR work"),
    "I1_ret_20d": ("I1c", "USDCAD 20-day log return", "Must", "Block I", "Monthly momentum"),
    "I1_ret_60d": ("I1d", "USDCAD 60-day log return", "Must", "Block I", "Quarterly momentum"),
    "I1_ret_252d": ("I1e", "USDCAD 252-day log return", "Must", "Block I", "Annual momentum / trend signal"),
    "I2_dist_50dma": ("I2a", "USDCAD distance from 50-day MA", "Should", "Block I", "Trend strength indicator"),
    "I2_dist_200dma": ("I2b", "USDCAD distance from 200-day MA", "Should", "Block I", "Long-term trend strength"),
    "I3_rvol_10d": ("I3a", "USDCAD realized volatility 10d annualized", "Must", "Block I", "Short-run vol regime"),
    "I3_rvol_30d": ("I3b", "USDCAD realized volatility 30d annualized", "Must", "Block I", "Medium-run vol"),
    "I3_rvol_60d": ("I3c", "USDCAD realized volatility 60d annualized", "Must", "Block I", "Long-run vol regime classifier"),
    "I9_beta_dxy": ("I9", "USDCAD beta to DXY (rolling 60d)", "Must", "Block I", "Time-varying dollar-factor loading"),
    "I10_usd_vs_cad": ("I10", "USDCAD minus EURCAD 5d return", "Must", "Block I", "Decomposes pure-USD movement from CAD-specific movement"),
    "I11_cad_aud_corr": ("I11", "Rolling 60d correlation: USDCAD vs AUD/USD", "Should", "Block I", "Commodity-currency co-movement proxy"),
    "J3_housing_starts": ("J3", "Canadian housing starts (CMHC)", "Nice-to-have", "Block J", "Real-side demand indicator; leads BoC rate expectations at turning points"),
    "L1_fxi_ret": ("L1", "iShares China ETF (FXI) 5d return", "Should", "Block L", "Commodity demand proxy via Chinese equity performance"),
    "L4_tips_5y5y": ("L4", "TIPS 5Y5Y forward inflation breakeven", "Should", "Block L", "Long-run US inflation expectations differential; affects carry attractiveness"),
}

GATED_VARIABLES = [
    ("D5", "USDCAD 1M 25-delta risk reversal", "Must", "Block D", "Bloomberg proprietary. SKIPPED.", "PAID/GATED"),
    ("D6", "USDCAD 3M-12M risk reversals", "Should", "Block D", "Bloomberg proprietary. SKIPPED.", "PAID/GATED"),
    ("D7", "USDCAD 25-delta butterfly 1M", "Should", "Block D", "Bloomberg proprietary. SKIPPED.", "PAID/GATED"),
    ("D8", "USDCAD ATM implied vol 1M", "Should", "Block D", "Bloomberg proprietary. SKIPPED.", "PAID/GATED"),
    ("D9", "USDCAD implied-realized vol spread", "Must", "Block D", "Bloomberg for IV. Realized vol is computed (I3). Full VRP requires Bloomberg IV. PARTIAL.", "PAID/GATED"),
    ("D10", "DXY 25-delta risk reversal", "Should", "Block D", "Bloomberg proprietary. SKIPPED.", "PAID/GATED"),
    ("C2", "MOVE index (rates vol)", "Must", "Block C", "Not on FRED or Yahoo in a clean form. SKIPPED.", "NOT ON FREE SOURCES"),
    ("C3", "Miranda-Agrippino-Rey GFC factor", "Must", "Block C", "Monthly. Available at author website but Excel format requiring manual parse. Skipped.", "DEFERRED"),
    ("C7", "Canada IG OAS", "Nice-to-have", "Block C", "Bloomberg proprietary. SKIPPED.", "PAID/GATED"),
    ("C8", "TED/OIS-Libor spread", "Nice-to-have", "Block C", "LIBOR discontinued 2023; SOFR-OIS available but complex construction. SKIPPED.", "DEFERRED"),
    ("C9", "CAD-USD cross-currency basis 3M", "Should", "Block C", "Bloomberg proprietary. Critical for CIP deviations (Du-Tepper-Verdelhan). SKIPPED.", "PAID/GATED"),
    ("C10", "Bond-equity correlation (rolling)", "Nice-to-have", "Block C", "Can be constructed -- not included this run.", "DEFERRED"),
    ("E1", "StatCan net portfolio inflows", "Must", "Block E", "Fetch attempted; StatCan table 36-10-0026 requires vector-level parsing post-download.", "DEFERRED"),
    ("E2", "Canadian portfolio outflows", "Should", "Block E", "Same table as E1; same deferral.", "DEFERRED"),
    ("E3", "US TIC: foreign purchases of US securities", "Should", "Block E", "Treasury TIC monthly; complex format. Deferred.", "DEFERRED"),
    ("F11", "Citi CESI Canada", "Must", "Block F", "Bloomberg proprietary. Most important missing variable. No free equivalent exists.", "PAID/GATED"),
    ("F12", "Citi CESI US", "Must", "Block F", "Bloomberg proprietary. SKIPPED.", "PAID/GATED"),
    ("F13", "CESI Canada-US differential", "Must", "Block F", "Requires F11 and F12. SKIPPED.", "PAID/GATED"),
    ("A6", "BoC policy surprise (HFI)", "Should", "Block A", "No maintained public series. SF Fed FOMC equivalent available; BoC equivalent requires custom construction.", "NO PUBLIC SOURCE"),
    ("A13", "BoC hawkish-dovish NLP score", "Nice-to-have", "Block A", "Custom construction required. Deferred.", "DEFERRED"),
    ("A14", "Fed hawkish-dovish NLP score", "Nice-to-have", "Block A", "Custom construction required. Deferred.", "DEFERRED"),
    ("H6", "US tariff news NLP (GDELT)", "Must (current regime)", "Block H", "GDELT accessible but requires NLP pipeline. High value for 2025-2026 regime. Deferred.", "DEFERRED"),
    ("L5", "Canada sovereign CDS 5Y", "Should", "Block L", "Markit proprietary. SKIPPED.", "PAID/GATED"),
    ("L6", "US sovereign CDS 5Y", "Should", "Block L", "Markit proprietary. SKIPPED.", "PAID/GATED"),
]


def _plotly_cdn_script() -> str:
    return '<script src="https://cdn.plot.ly/plotly-2.35.2.min.js" charset="utf-8"></script>'


def _style_block() -> str:
    return """
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: 'Georgia', serif; background: #fafaf8; color: #1a1a1a; max-width: 1100px; margin: 0 auto; padding: 24px 32px; }
  h1 { font-size: 1.9rem; font-weight: 700; margin: 24px 0 8px; border-bottom: 3px solid #1a1a1a; padding-bottom: 8px; }
  h2 { font-size: 1.35rem; font-weight: 700; margin: 48px 0 14px; color: #111; border-bottom: 1px solid #e0e0d0; padding-bottom: 6px; }
  h3 { font-size: 1.05rem; font-weight: 600; margin: 24px 0 8px; }
  p { line-height: 1.7; margin: 0 0 14px; font-size: 0.97rem; }
  .meta { font-size: 0.82rem; color: #666; margin-bottom: 24px; }

  /* ---- Executive summary box ---- */
  .exec-summary {
    background: #1a1a1a;
    color: #f5f5f0;
    border-radius: 10px;
    padding: 28px 32px;
    margin: 24px 0 40px;
  }
  .exec-summary h2 {
    color: #f5f5f0;
    border-bottom-color: #444;
    font-size: 1.15rem;
    margin-top: 0;
    margin-bottom: 16px;
    text-transform: uppercase;
    letter-spacing: 0.06em;
  }
  .exec-summary .headline {
    font-size: 1.18rem;
    font-weight: 700;
    line-height: 1.55;
    margin-bottom: 18px;
    color: #ffffff;
  }
  .exec-summary p { font-size: 0.95rem; color: #d0d0c8; margin-bottom: 12px; }
  .exec-summary p:last-child { margin-bottom: 0; }
  .exec-summary .label { font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.07em; color: #888; margin-bottom: 4px; }
  .exec-summary ul { padding-left: 20px; margin: 8px 0; }
  .exec-summary li { font-size: 0.93rem; color: #c8c8c0; line-height: 1.6; margin-bottom: 6px; }
  .exec-confidence { display: inline-block; padding: 4px 14px; border-radius: 20px; font-size: 0.82rem; font-weight: 700; letter-spacing: 0.04em; margin-bottom: 16px; }
  .conf-high { background: #157a47; color: #fff; }
  .conf-medium { background: #d97706; color: #fff; }
  .conf-low { background: #c00; color: #fff; }
  .exec-row { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; margin-top: 20px; }
  @media (max-width: 700px) { .exec-row { grid-template-columns: 1fr; } }

  /* ---- Navigation ---- */
  .toc { background: #f5f5f0; border: 1px solid #ddd; border-radius: 8px; padding: 18px 22px; margin: 0 0 40px; }
  .toc h3 { margin-top: 0; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 0.06em; color: #666; margin-bottom: 10px; }
  .toc ol { padding-left: 20px; }
  .toc li { font-size: 0.88rem; margin-bottom: 5px; }
  .toc a { color: #3a5bd9; text-decoration: none; }
  .toc a:hover { text-decoration: underline; }
  .toc .appendix-link { color: #888; }

  /* ---- Chart framing ---- */
  .chart-intro {
    background: #f0f4ff;
    border-left: 4px solid #3a5bd9;
    padding: 14px 18px;
    margin: 0 0 0;
    border-radius: 0 6px 0 0;
    font-size: 0.94rem;
    line-height: 1.6;
  }
  .chart-intro strong { color: #1a1a1a; }
  .chart-intro p { margin: 0 0 6px; font-size: 0.94rem; }
  .chart-intro p:last-child { margin: 0; }
  .chart-wrap {
    background: #fff;
    border: 1px solid #e0e0e0;
    border-top: none;
    border-radius: 0 0 8px 8px;
    padding: 16px;
    margin: 0 0 8px;
  }
  .chart-conclude {
    background: #fafaf0;
    border-left: 4px solid #888;
    padding: 10px 16px;
    margin: 0 0 32px;
    font-size: 0.88rem;
    color: #444;
    border-radius: 0 0 6px 0;
  }
  .chart-conclude strong { color: #1a1a1a; }

  /* When there's no chart-intro above, use the standalone chart-wrap */
  .chart-wrap-standalone {
    background: #fff;
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    padding: 16px;
    margin: 0 0 24px;
  }

  /* ---- Callout boxes ---- */
  .plain-english { background: #f0f4ff; border-left: 4px solid #3a5bd9; padding: 16px 20px; margin: 16px 0 24px; border-radius: 0 6px 6px 0; }
  .plain-english p { margin: 0 0 8px; font-size: 0.95rem; }
  .plain-english p:last-child { margin: 0; }
  .honest-box { background: #fff3cd; border-left: 4px solid #d97706; padding: 16px 20px; margin: 16px 0 24px; border-radius: 0 6px 6px 0; }
  .honest-box p { margin: 0 0 8px; }
  .honest-box p:last-child { margin: 0; }
  .holdout-box { background: #e8f5e9; border-left: 4px solid #2e7d32; padding: 16px 20px; margin: 16px 0 24px; border-radius: 0 6px 6px 0; }
  .holdout-box p { margin: 0 0 8px; }
  .holdout-box p:last-child { margin: 0; }
  .holdout-fail { background: #fce8e8; border-left: 4px solid #c00; padding: 16px 20px; margin: 16px 0 24px; border-radius: 0 6px 6px 0; }
  .holdout-fail p { margin: 0 0 8px; }
  .warning-box { background: #fde8e8; border-left: 4px solid #c00; padding: 16px 20px; margin: 16px 0 24px; border-radius: 0 6px 6px 0; }
  .fix-box { background: #e3f2fd; border-left: 4px solid #1565c0; padding: 16px 20px; margin: 16px 0 24px; border-radius: 0 6px 6px 0; }

  /* ---- Stat cards ---- */
  .stat-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(190px, 1fr)); gap: 16px; margin: 16px 0 24px; }
  .stat-card { background: #fff; border: 1px solid #ddd; border-radius: 8px; padding: 16px; text-align: center; }
  .stat-card .label { font-size: 0.76rem; color: #666; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 6px; }
  .stat-card .value { font-size: 1.55rem; font-weight: 700; }
  .stat-card .caption { font-size: 0.73rem; color: #888; margin-top: 4px; line-height: 1.4; }
  .stat-card.good .value { color: #157a47; }
  .stat-card.warn .value { color: #d97706; }
  .stat-card.bad .value { color: #c00; }
  .stat-card.holdout { border: 2px solid #2e7d32; background: #f1f8e9; }

  /* ---- Tables ---- */
  table { width: 100%; border-collapse: collapse; font-size: 0.84rem; margin: 0 0 24px; }
  th { background: #1a1a1a; color: #fff; padding: 8px 10px; text-align: left; font-weight: 600; }
  td { padding: 6px 10px; border-bottom: 1px solid #eee; vertical-align: top; }
  tr:nth-child(even) td { background: #f9f9f7; }
  .keep { background: #e8f5e9 !important; }
  .drop { background: #fce8e8 !important; }
  .gated { background: #fff8e1 !important; }

  /* ---- Appendix ---- */
  .appendix-section { background: #f7f7f5; border: 1px solid #ddd; border-radius: 8px; padding: 24px 28px; margin: 0 0 32px; }
  .appendix-section h2 { margin-top: 0; font-size: 1.1rem; color: #555; border-bottom-color: #ccc; }
  .appendix-section > p { color: #555; font-size: 0.9rem; }

  /* ---- Misc ---- */
  pre { font-family: monospace; background: #f4f4f0; padding: 12px 16px; border-radius: 4px; overflow-x: auto; font-size: 0.82rem; margin: 0 0 16px; white-space: pre-wrap; }
  .section-divider { border: none; border-top: 2px solid #e0e0d0; margin: 48px 0; }
  a { color: #3a5bd9; }
  .tag { display: inline-block; padding: 2px 8px; border-radius: 12px; font-size: 0.73rem; font-weight: 600; margin: 0 2px; }
  .tag-must { background: #1a237e; color: #fff; }
  .tag-should { background: #0288d1; color: #fff; }
  .tag-nice { background: #9e9e9e; color: #fff; }
  .tag-gated { background: #e65100; color: #fff; }
  .tag-deferred { background: #bf360c; color: #fff; }
  .phase3-badge { display: inline-block; background: #2e7d32; color: #fff; padding: 3px 10px; border-radius: 12px; font-size: 0.78rem; font-weight: 700; margin-left: 8px; }
</style>
"""


def _safe_json(obj):
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        return float(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, pd.Timestamp):
        return str(obj.date())
    if isinstance(obj, float) and np.isnan(obj):
        return None
    return obj


def _build_variable_table(filter_results, selected_features) -> str:
    selected_set = set(selected_features)
    filter_map = {r.variable: r for r in filter_results}

    rows = []
    for key, (var_id, desc, tier, block, rationale) in VARIABLE_CATALOG.items():
        fr = filter_map.get(key)
        if fr:
            passed = fr.passes_filter
            rho_str = f"{fr.spearman_rho:.3f}"
            pval_str = f"{fr.spearman_pval:.3f}"
            mi_str = f"{fr.mutual_info:.4f}"
        else:
            passed = False
            rho_str = pval_str = mi_str = "—"

        in_model = key in selected_set
        row_class = "keep" if in_model else ("drop" if fr else "")

        tier_tag = {
            "Must": '<span class="tag tag-must">Must</span>',
            "Should": '<span class="tag tag-should">Should</span>',
            "Nice-to-have": '<span class="tag tag-nice">Nice-to-have</span>',
        }.get(tier, tier)

        status = "SELECTED" if in_model else ("Kept (filter)" if (fr and passed) else "Dropped")

        rows.append(
            f'<tr class="{row_class}">'
            f"<td><strong>{var_id}</strong></td>"
            f"<td>{desc}</td>"
            f"<td>{tier_tag}</td>"
            f"<td>{rationale}</td>"
            f"<td>{rho_str}</td>"
            f"<td>{pval_str}</td>"
            f"<td>{mi_str}</td>"
            f"<td><strong>{status}</strong></td>"
            f"</tr>"
        )

    for var_id, desc, tier, block, note, status_label in GATED_VARIABLES:
        tier_tag = {
            "Must": '<span class="tag tag-must">Must</span>',
            "Should": '<span class="tag tag-should">Should</span>',
            "Nice-to-have": '<span class="tag tag-nice">Nice-to-have</span>',
        }.get(tier, tier)
        status_tag = '<span class="tag tag-gated">GATED</span>' if status_label == "PAID/GATED" else f'<span class="tag tag-deferred">{status_label}</span>'
        rows.append(
            f'<tr class="gated">'
            f"<td><strong>{var_id}</strong></td>"
            f"<td>{desc}</td>"
            f"<td>{tier_tag}</td>"
            f"<td>{note}</td>"
            f"<td>—</td><td>—</td><td>—</td>"
            f"<td>{status_tag}</td>"
            f"</tr>"
        )

    header = """
<table>
  <thead>
    <tr>
      <th>ID</th>
      <th>Variable</th>
      <th>Tier</th>
      <th>Rationale</th>
      <th>Spearman rho (training)</th>
      <th>p-value (training)</th>
      <th>Mut. Info (training)</th>
      <th>Status</th>
    </tr>
  </thead>
  <tbody>
"""
    return header + "\n".join(rows) + "\n  </tbody>\n</table>"


def _build_transformation_table() -> str:
    """Build the Phase 3 data transformation audit table."""
    rows = [
        # (Variable group, Transformation applied, Stationarity, Look-ahead lag, Notes)
        ("USDCAD spot (target)", "Log returns: ln(P_t+h / P_t). Directional sign (1/-1) for hit rate.", "Stationary (returns)", "None (target)", "Levels are I(1) non-stationary. Log returns give symmetric treatment of up/down moves. Three horizons: 5d, 21d, 63d forward returns."),
        ("USDCAD spot (features)", "Lagged log returns (1d, 5d, 20d, 60d, 252d); distance from 50/200d MA (level-ratio); realized volatility (rolling std of log returns, annualized); rolling beta to DXY.", "Stationary (returns/ratios)", "0 days (contemporaneous, lagged by construction)", "Momentum variables use past returns only. Distance-from-MA is a ratio (stationary). Realized vol is a rolling std -- stationary."),
        ("Interest rate yields (GoC, UST)", "Used as DIFFERENTIALS (GoC minus UST), not levels. Differentials are more stationary than individual yield levels. Yield CURVES used as slope (10Y-2Y), also a spread.", "Near-stationary (spreads)", "0 days (daily market data)", "Individual yield levels are I(1) and would create spurious regressions. Differentials are more stationary. Rate differentials drive USDCAD through the UIP channel."),
        ("Policy rates (BoC, Fed)", "Difference (BoC overnight minus Fed upper bound). Monthly Fed data forward-filled to daily.", "Near-stationary (spread)", "0 days", "Policy rates in levels are highly persistent. The spread captures the relative-stance signal."),
        ("Real rate differential", "RRB 10Y minus TIPS 10Y yield (both are already real yields -- no further deflation needed). Used as level differential.", "Near-stationary (spread)", "0 days", "Real rate differentials are the theoretically correct UIP variable per Engel (2016)."),
        ("Commodity prices (WTI, Brent, copper, gold, nat gas, BCPI)", "LEVELS, not returns. Commodity prices in levels are I(1) non-stationary, but this is intentional: the BCPI level has documented cointegrating relationship with USDCAD (terms-of-trade channel). Robustness: the model also includes commodity volatility (OVX) which is stationary.", "I(1), intentional cointegration", "0 days", "The BoC SAN 2017-1 paper and the terms-of-trade literature (Cashin-Cespedes-McDermott 2004) establish cointegration between commodity prices and commodity-currency exchange rates. We follow this literature in using commodity price levels. If stationarity is required, first differences of commodity prices can be substituted -- this is a robustness check for Phase 4."),
        ("Equity indices / differentials (DXY, EUR/USD, USD/JPY, equity differential)", "DXY, EUR/USD, USD/JPY: LEVELS (same cointegration logic as commodities -- FX pairs are I(1) but cross-currency relationships are stable). S&P vs TSX: 5-day RETURN differential (stationary by construction).", "Mixed: FX levels I(1), return-diff stationary", "0 days", "FX levels used for broad-USD variables where the level captures the contemporaneous dollar regime. This is standard practice in FX forecasting (Rossi 2013 survey). Return differentials used where relative performance is the signal."),
        ("Volatility (VIX, OVX, realized vol)", "LEVELS. VIX and OVX are by construction stationary-ish (mean-reverting vol indices). Realized vol computed as rolling std of log returns (annualized).", "Near-stationary (vol indices mean-revert)", "0 days", "Implied vol indices (VIX, OVX) are not pure random walks; they mean-revert to long-run averages. Using levels is standard. OVX level captures the terms-of-trade uncertainty regime separately from the commodity price level."),
        ("Credit spreads (HY OAS, IG OAS, NFCI)", "LEVELS. Credit spreads are mean-reverting over long horizons. NFCI is standardized by construction (z-score, centered at 0).", "Near-stationary", "0 days", "Credit spreads widen in risk-off and tighten in risk-on. Using levels captures the regime signal. HY OAS above ~500bp vs below ~300bp carries distinct regime information."),
        ("Macro fundamentals (CPI YoY, GDP YoY, unemployment rate)", "YoY growth rates for flow variables (CPI, GDP). LEVELS for unemployment (which is already a rate). CPI differential = Canada YoY minus US YoY.", "Stationary (growth rates and rate-levels)", "Release lag applied: CPI +15 bdays, GDP +21 bdays, unemployment +5 bdays (conservative)", "YoY transforms eliminate seasonal patterns in monthly data. Release lags prevent look-ahead contamination: e.g., January CPI (released mid-February) is not used in the feature panel until mid-February."),
        ("Leading indicators (OECD CLI, ISM, housing starts)", "LEVELS. OECD CLI is indexed to 100 -- deviations from 100 capture momentum above/below trend.", "Near-stationary (diffusion indices)", "Release lag: OECD CLI +30 bdays, ISM +5 bdays, housing starts +15 bdays", "Leading indicators are designed to be stationary. Housing starts used in levels (monthly SA, forward-filled)."),
        ("Policy uncertainty (EPU Canada, EPU US, TPU)", "LEVELS (log-scaled by construction in Baker-Bloom-Davis). These are index values normalized to 100-average base period.", "Near-stationary (index)", "0-5 days (daily updates for EPU US)", "EPU daily index is updated daily (with monthly revisions). Levels capture the uncertainty regime."),
        ("Speculative positioning (CFTC, if available)", "NET position in contracts (long minus short non-commercial). Z-score variant (52-week z-score) is also included.", "Stationary (net position mean-reverts)", "5 bdays (CFTC publishes Tuesday data on Friday; we use Friday close)", "CFTC positions are mean-reverting by construction: extreme long positioning is followed by unwinding. Z-score captures the historical context."),
        ("Standardization (all features)", "Z-scored at fit time using TRAINING DATA STATISTICS ONLY. Mean and std computed from X_train, applied to X_test and X_holdout without look-ahead.", "N/A", "N/A", "Training standardization prevents scale dominance by any single variable. Test/hold-out standardization uses training parameters -- no future information."),
        ("Outlier handling", "No explicit winsorization in Phase 3. Boruta's random-forest base estimator is robust to outliers. ElasticNet is linear and potentially sensitive to outliers in commodity variables during COVID/tariff spikes.", "N/A", "N/A", "Phase 4 robustness check: add 1%/99% winsorization of all returns-based features before fitting. Hypothesis: COVID period (March 2020) and tariff-spike (April 2025) are the main outlier dates."),
        ("Missing data", "1. Coverage filter: features with >60% missing values dropped before fitting. 2. Remaining NaN filled with column median (training median applied to test/holdout). 3. No forward-fill within the feature panel at this stage (forward-fill applied in acquire.py at source alignment, with configurable limits).", "N/A", "N/A", "Median imputation is conservative: it pulls missing values to the center of the distribution, dampening any spurious signal from the imputed values. Forward-fill at source level has explicit limits (5 bdays for daily, 23 bdays for monthly) to prevent stale data from propagating over major gaps."),
    ]

    html = """
<table>
  <thead>
    <tr>
      <th>Variable group</th>
      <th>Transformation applied</th>
      <th>Stationarity status</th>
      <th>Look-ahead lag</th>
      <th>Notes and rationale</th>
    </tr>
  </thead>
  <tbody>
"""
    for row in rows:
        html += f"""<tr>
<td><strong>{row[0]}</strong></td>
<td>{row[1]}</td>
<td>{row[2]}</td>
<td>{row[3]}</td>
<td style="font-size:0.83rem;">{row[4]}</td>
</tr>
"""
    html += "  </tbody>\n</table>"
    return html


def _plotly_fig_json(fig) -> str:
    import plotly
    return plotly.io.to_json(fig)


def _horizon_exec_summary(horizon: str, v, hr) -> str:
    """Build the horizon-specific executive summary block."""
    ho_edge = (v.holdout_hit_rate_extreme - v.holdout_hit_rate_middle) * 100
    ho_hit = v.holdout_hit_rate * 100
    ho_ext = v.holdout_hit_rate_extreme * 100
    ho_mid = v.holdout_hit_rate_middle * 100

    if horizon == "weekly":
        headline = (
            f"At extreme composite score readings (top or bottom 10%), the weekly model "
            f"called USDCAD direction correctly {ho_ext:.0f}% of the time on hold-out data, "
            f"vs {ho_mid:.0f}% in neutral readings — a {ho_edge:+.0f} percentage-point edge. "
            f"Overall hold-out hit rate (all readings): {ho_hit:.0f}%."
        )
        plain_english = (
            "The model's general signal is weak — a 50-something percent overall hit rate "
            "does not make it a reliable direction-predictor for every week. "
            "The useful finding is narrower: when all the macro indicators are stacked "
            "heavily in the same direction (extreme score readings), the model has historically "
            "been right more often than not on data it never trained on. "
            "In neutral periods — when the indicators are mixed — the model has no meaningful edge. "
            "Use it as a regime flag, not a day-by-day direction call."
        )
        not_claiming = (
            "A general-purpose weekly direction predictor. The overall hit rate "
            "is only marginally above 50%. The edge is specific to extreme readings. "
            "The model has not been validated across multiple structurally different "
            "macro regimes (the hold-out period is primarily the 2022-2026 tightening and tariff era)."
        )
        # Determine confidence
        if ho_edge >= 5 and v.holdout_hit_rate_extreme >= 0.55:
            conf_class = "conf-medium"
            conf_label = "MEDIUM"
            conf_reason = (
                f"Meaningful extreme-reading edge ({ho_edge:.0f}pp) on hold-out data, "
                "but hold-out period covers only one macro regime (BoC tightening + tariff shock). "
                "Confidence would be higher with multi-regime validation."
            )
        elif ho_edge >= 2:
            conf_class = "conf-medium"
            conf_label = "MEDIUM-LOW"
            conf_reason = (
                f"Some extreme-reading edge ({ho_edge:.0f}pp) observed on hold-out. "
                "Not large enough to be confident across regimes."
            )
        else:
            conf_class = "conf-low"
            conf_label = "LOW"
            conf_reason = (
                "Extreme-reading edge is below 2pp on hold-out. "
                "Cannot claim reliable directional signal at any reading level."
            )
        specific_caveats = [
            f"Hold-out period ({v.holdout_start_date} to {v.holdout_end_date}, n={v.holdout_n_obs} weekly rows) "
            "covers primarily one macro regime. Multi-regime validation would require data from a structurally different period.",
            f"Extreme readings account for only ~{v.holdout_n_extreme_obs} of {v.holdout_n_obs} hold-out observations. "
            "The signal concentration means one bad run of luck in extreme readings would materially change the reported edge.",
            "The model is missing Bloomberg-gated options data (risk reversals, implied vol) and the Citi Economic Surprise Index — "
            "the two most commonly cited USDCAD-specific inputs on FX desks. A full-data version would likely perform differently.",
            "General (non-extreme) signal is weak. Do not use the model outside of extreme-reading episodes.",
        ]

    elif horizon == "monthly":
        headline = (
            f"At extreme composite score readings (top or bottom 10%), the monthly model "
            f"called USDCAD direction correctly {ho_ext:.0f}% of the time on hold-out data, "
            f"vs {ho_mid:.0f}% in neutral readings — a {ho_edge:+.0f} percentage-point edge. "
            f"Overall hold-out hit rate: {ho_hit:.0f}%."
        )
        plain_english = (
            "The monthly model's cross-validation (the training-data internal test) failed — "
            "performance was inconsistent across CV folds, suggesting the signal is regime-specific "
            "rather than stable across different periods. "
            "The hold-out test (data the model never saw) is therefore the only defensible "
            "performance figure. "
            "As with the weekly model, any edge is concentrated in extreme readings, "
            "not in general use."
        )
        not_claiming = (
            "A stable monthly direction predictor. Cross-validation failure means the "
            "training-data signal was inconsistent by period. The hold-out result is "
            "from a single macro regime. Not validated across regimes."
        )
        if ho_edge >= 5:
            conf_class = "conf-medium"
            conf_label = "MEDIUM-LOW"
            conf_reason = (
                "Hold-out shows a meaningful extreme-reading edge, but CV failure on training data "
                "means the signal was not stable across historical regimes. The hold-out result "
                "may be period-specific."
            )
        else:
            conf_class = "conf-low"
            conf_label = "LOW"
            conf_reason = (
                "CV failed on training data, and extreme-reading edge on hold-out is small. "
                "Cannot claim reliable signal."
            )
        non_overlap_approx = max(1, v.holdout_n_obs // 21)
        specific_caveats = [
            "Cross-validation on training data FAILED — hit rates were inconsistent across CV folds. "
            "This means the training-period signal was regime-specific. The hold-out result is the only "
            "honest number, and it is from a single macro regime.",
            f"Hold-out contains approximately {non_overlap_approx} non-overlapping 21-day observations "
            f"(total rows: {v.holdout_n_obs}, but monthly returns overlap heavily). "
            "Statistical conclusions from a thin non-overlapping sample are fragile.",
            "Missing Bloomberg-gated options data and Citi CESI differential — the most important "
            "missing inputs for monthly FX forecasting.",
            f"Extreme readings account for only ~{v.holdout_n_extreme_obs} of {v.holdout_n_obs} hold-out rows. "
            "Small absolute count.",
        ]

    else:  # quarterly
        non_overlap_approx = max(1, v.holdout_n_obs // 63)
        headline = (
            f"At extreme composite score readings (top or bottom 10%), the quarterly model "
            f"called USDCAD direction correctly {ho_ext:.0f}% of the time on hold-out data, "
            f"vs {ho_mid:.0f}% in neutral readings — a {ho_edge:+.0f} percentage-point edge. "
            f"Overall hold-out hit rate: {ho_hit:.0f}%. "
            f"Caution: the hold-out contains approximately {non_overlap_approx} non-overlapping "
            "quarterly periods — a statistically thin base."
        )
        plain_english = (
            "The quarterly model has the most economically sound variable set "
            "(macro fundamentals matter more over three months than over one week), "
            "but the least statistical evidence. "
            f"There are only about {non_overlap_approx} truly independent quarterly observations "
            "in the hold-out — that is not enough data to draw strong conclusions. "
            "Think of the quarterly diagnostic as a framework for understanding which macro "
            "variables matter over medium-term horizons, not as a validated forecasting tool."
        )
        not_claiming = (
            f"A statistically validated quarterly direction predictor. Approximately {non_overlap_approx} "
            "non-overlapping quarterly hold-out observations is too thin to distinguish "
            "genuine skill from luck. Wide confidence intervals around any reported hit rate "
            "should be assumed."
        )
        conf_class = "conf-low"
        conf_label = "LOW — THIN SAMPLE"
        conf_reason = (
            f"Only approximately {non_overlap_approx} non-overlapping quarterly periods in hold-out. "
            "Statistical conclusions at this sample size are unreliable. The quarterly model "
            "should be treated as a framework, not a validated tool."
        )
        specific_caveats = [
            f"CRITICAL SAMPLE SIZE LIMITATION: approximately {non_overlap_approx} non-overlapping "
            f"63-day periods in the hold-out (total rows: {v.holdout_n_obs}, but quarterly returns "
            "overlap heavily). This is the most important caveat for the quarterly model. "
            "A few lucky or unlucky quarters materially swing the reported hit rate.",
            "At this sample size, a 55% hit rate and a 45% hit rate are statistically "
            "indistinguishable — do not over-interpret the reported numbers.",
            "The quarterly model uses macro fundamentals (CPI, GDP, unemployment) "
            "that are slow-moving and have long release lags. These are appropriate "
            "for medium-term analysis but do not capture high-frequency shocks.",
            "Missing Bloomberg-gated options data and Citi CESI differential.",
        ]

    caveat_items = "".join(f"<li>{c}</li>" for c in specific_caveats)

    return f"""
<div class="exec-summary">
  <h2>Executive Summary: {horizon.capitalize()} Horizon</h2>

  <div class="label">Headline finding</div>
  <p class="headline">{headline}</p>

  <span class="exec-confidence {conf_class}">{conf_label} confidence</span>
  <p style="font-size:0.88rem; color:#bbb; margin-bottom:20px;">{conf_reason}</p>

  <div class="exec-row">
    <div>
      <div class="label" style="margin-bottom:8px;">What this means in plain English</div>
      <p>{plain_english}</p>
    </div>
    <div>
      <div class="label" style="margin-bottom:8px;">What we are NOT claiming</div>
      <p>{not_claiming}</p>
      <div class="label" style="margin-bottom:8px; margin-top:16px;">Key caveats</div>
      <ul>{caveat_items}</ul>
    </div>
  </div>
</div>
"""


def generate_diagnostic_html(horizon_result, output_path: Path) -> None:
    """Generate the full Phase 3 diagnostic HTML for one horizon."""
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    hr = horizon_result
    v = hr.validation
    s = hr.selection
    horizon = hr.horizon

    # -----------------------------------------------------------------------
    # Chart 1: Score time series vs USDCAD spot (with hold-out region highlighted)
    # -----------------------------------------------------------------------
    usdcad_path = Path(__file__).parents[2] / "data" / "raw" / "usdcad.csv"
    if not usdcad_path.exists():
        usdcad_path = Path(__file__).parents[2] / "data" / "raw" / "fxusdcad.csv"
    spot_df = None
    if usdcad_path.exists():
        spot_df = pd.read_csv(usdcad_path)
        spot_df["date"] = pd.to_datetime(spot_df["date"], errors="coerce")
        spot_df = spot_df.dropna(subset=["date", "value"]).set_index("date").sort_index()

    score_full = hr.score_full.dropna()
    score_norm = (score_full - score_full.mean()) / (score_full.std() + 1e-8)

    fig_score = make_subplots(specs=[[{"secondary_y": True}]])
    if spot_df is not None:
        spot_aligned = spot_df["value"].reindex(score_full.index, method="ffill")
        fig_score.add_trace(
            go.Scatter(
                x=score_full.index.astype(str),
                y=spot_aligned.values,
                name="USDCAD spot",
                line=dict(color="#1a1a1a", width=1.5),
                hovertemplate="%{x}: %{y:.4f}<extra>USDCAD</extra>",
            ),
            secondary_y=False,
        )
    fig_score.add_trace(
        go.Scatter(
            x=score_full.index.astype(str),
            y=score_norm.values,
            name="Composite score (standardized)",
            line=dict(color="#3a5bd9", width=1.5, dash="dot"),
            hovertemplate="%{x}: %{y:.2f}<extra>Score</extra>",
        ),
        secondary_y=True,
    )
    # Highlight hold-out region
    if hr.holdout_split_date:
        fig_score.add_vrect(
            x0=hr.holdout_split_date,
            x1=str(score_full.index.max().date()),
            fillcolor="rgba(46, 125, 50, 0.12)",
            layer="below", line_width=1, line_color="rgba(46, 125, 50, 0.5)",
            annotation_text="HOLD-OUT (never used in fitting)",
            annotation_position="top left",
            annotation=dict(font_size=10, font_color="#2e7d32"),
        )
    # Regime shading (training periods)
    from pipeline.usdcad.model import REGIMES
    regime_colors = ["rgba(255,220,100,0.12)", "rgba(100,200,150,0.12)",
                     "rgba(255,100,100,0.12)", "rgba(100,150,255,0.12)", "rgba(200,100,200,0.10)"]
    for i, (reg_name, (reg_start, reg_end)) in enumerate(REGIMES.items()):
        end_clip = min(reg_end, hr.holdout_split_date or str(score_full.index.max().date()))
        if reg_start >= (hr.holdout_split_date or "2099"):
            continue
        fig_score.add_vrect(
            x0=reg_start, x1=end_clip,
            fillcolor=regime_colors[i % len(regime_colors)],
            layer="below", line_width=0,
            annotation_text=reg_name.split(" (")[0][:22],
            annotation_position="top left",
            annotation=dict(font_size=9),
        )
    fig_score.update_layout(
        title=f"Composite Score vs USDCAD — {horizon.capitalize()} Horizon",
        height=500,
        paper_bgcolor="white",
        plot_bgcolor="white",
        legend=dict(x=0.01, y=0.99),
        hovermode="x unified",
    )
    fig_score.update_yaxes(title_text="USDCAD (CAD per USD)", secondary_y=False)
    fig_score.update_yaxes(title_text="Composite score (standardized)", secondary_y=True)
    fig_score_json = _plotly_fig_json(fig_score)

    # -----------------------------------------------------------------------
    # Chart 2: Hold-out performance
    # -----------------------------------------------------------------------
    score_ho = hr.score_holdout.dropna()
    y_ho_aligned = hr.y_holdout.reindex(score_ho.index).dropna()
    score_ho = score_ho.reindex(y_ho_aligned.index)

    fig_holdout = make_subplots(rows=1, cols=2,
                                 subplot_titles=["Hold-out hit rate vs 50% benchmark",
                                                 "Score vs actual return (hold-out)"])
    if len(y_ho_aligned) > 5:
        fig_holdout.add_bar(
            x=["Overall", "Extremes<br>(top/bottom 10%)", "Middle 80%"],
            y=[v.holdout_hit_rate, v.holdout_hit_rate_extreme, v.holdout_hit_rate_middle],
            marker_color=[
                "#157a47" if v.holdout_hit_rate >= 0.53 else "#d97706" if v.holdout_hit_rate >= 0.50 else "#cc2222",
                "#157a47" if v.holdout_hit_rate_extreme >= 0.55 else "#d97706",
                "#888",
            ],
            text=[f"{v.holdout_hit_rate:.1%}", f"{v.holdout_hit_rate_extreme:.1%}", f"{v.holdout_hit_rate_middle:.1%}"],
            textposition="outside",
            row=1, col=1,
        )
        fig_holdout.add_hline(y=0.5, line_dash="dash", line_color="gray", row=1, col=1)

        # Scatter: actual return vs score on hold-out
        fig_holdout.add_scatter(
            x=score_ho.values,
            y=y_ho_aligned.values,
            mode="markers",
            marker=dict(
                color=["#157a47" if np.sign(sc) == np.sign(y) else "#cc2222"
                       for sc, y in zip(score_ho.values, y_ho_aligned.values)],
                size=5,
                opacity=0.6,
            ),
            hovertemplate="Score: %{x:.2f}<br>Return: %{y:.4f}<extra></extra>",
            row=1, col=2,
        )
        fig_holdout.add_hline(y=0, line_dash="dash", line_color="gray", row=1, col=2)
        fig_holdout.add_vline(x=0, line_dash="dash", line_color="gray", row=1, col=2)
    else:
        fig_holdout.add_annotation(text="Insufficient hold-out data",
                                   xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)

    n_ho_label = f"n={v.holdout_n_obs}" if v.holdout_n_obs > 0 else "n=0"
    fig_holdout.update_layout(
        height=450, showlegend=False, paper_bgcolor="white", plot_bgcolor="white",
        title=f"Hold-Out Performance ({v.holdout_start_date} to {v.holdout_end_date}, {n_ho_label})",
    )
    fig_holdout_json = _plotly_fig_json(fig_holdout)

    # -----------------------------------------------------------------------
    # Chart 3: Performance at extremes (hold-out and training side by side)
    # -----------------------------------------------------------------------
    score_valid_tr = hr.score_train.dropna()
    y_valid_tr = hr.y_train.reindex(score_valid_tr.index)
    score_pct_tr = score_valid_tr.rank(pct=True)
    extreme_mask_tr = (score_pct_tr <= 0.10) | (score_pct_tr >= 0.90)
    middle_mask_tr = (score_pct_tr > 0.10) & (score_pct_tr < 0.90)

    fig_extremes = make_subplots(
        rows=1, cols=2,
        subplot_titles=[
            f"Hit Rate at Extremes vs Middle 80%",
            "Return distribution: Extremes vs Middle (training)",
        ]
    )
    # Grouped bar: training vs hold-out, extremes vs middle
    fig_extremes.add_bar(
        x=["Training<br>Extremes", "Training<br>Middle 80%", "Hold-out<br>Extremes", "Hold-out<br>Middle 80%"],
        y=[v.hit_rate_extreme, v.hit_rate_middle, v.holdout_hit_rate_extreme, v.holdout_hit_rate_middle],
        marker_color=["#3a5bd9", "#aabbdd", "#157a47", "#88bb99"],
        text=[f"{v.hit_rate_extreme:.1%}", f"{v.hit_rate_middle:.1%}",
              f"{v.holdout_hit_rate_extreme:.1%}", f"{v.holdout_hit_rate_middle:.1%}"],
        textposition="outside",
        row=1, col=1,
    )
    fig_extremes.add_hline(y=0.5, line_dash="dash", line_color="gray", row=1, col=1)
    if extreme_mask_tr.sum() > 5:
        fig_extremes.add_histogram(
            x=y_valid_tr[extreme_mask_tr].values, name="Extremes (top/bottom 10%)",
            marker_color="rgba(58, 91, 217, 0.6)", nbinsx=30, row=1, col=2,
        )
    if middle_mask_tr.sum() > 5:
        fig_extremes.add_histogram(
            x=y_valid_tr[middle_mask_tr].values, name="Middle 80%",
            marker_color="rgba(100, 100, 100, 0.4)", nbinsx=30, row=1, col=2,
        )
    fig_extremes.update_layout(
        height=420, paper_bgcolor="white", plot_bgcolor="white",
        title=f"Edge at Extreme Readings — {horizon.capitalize()} Horizon",
        legend=dict(x=0.52, y=0.99),
    )
    fig_extremes_json = _plotly_fig_json(fig_extremes)

    # -----------------------------------------------------------------------
    # Chart 4: Variable importance (MDA) for selected variables
    # -----------------------------------------------------------------------
    if s.mda_importances and s.final_selected:
        imp_items = [(k, v_imp) for k, v_imp in s.mda_importances.items() if k in s.final_selected]
        imp_items.sort(key=lambda x: x[1], reverse=True)
    else:
        imp_items = []

    # Build human-readable labels for selected features
    feat_labels = {}
    for key, (var_id, desc, tier, block, rationale) in VARIABLE_CATALOG.items():
        feat_labels[key] = f"{var_id}: {desc[:45]}"

    imp_y_labels = [feat_labels.get(x[0], x[0]) for x in imp_items]
    imp_categories = []
    for key, _ in imp_items:
        meta = VARIABLE_CATALOG.get(key, ("", "", "", "Block ?", ""))
        block = meta[3]
        category_map = {
            "Block A": "Interest rates",
            "Block B": "Commodities",
            "Block C": "Risk appetite",
            "Block D": "Positioning",
            "Block F": "Macro fundamentals",
            "Block G": "Broad USD / global",
            "Block H": "Uncertainty",
            "Block I": "USDCAD price signals",
            "Block J": "Housing",
            "Block L": "Other",
        }
        imp_categories.append(category_map.get(block, block))

    # Colour by category
    category_colors = {
        "Interest rates": "#1a237e",
        "Commodities": "#e65100",
        "Risk appetite": "#880e4f",
        "Positioning": "#004d40",
        "Macro fundamentals": "#1b5e20",
        "Broad USD / global": "#0d47a1",
        "Uncertainty": "#bf360c",
        "USDCAD price signals": "#4a148c",
        "Housing": "#33691e",
        "Other": "#555",
    }
    imp_colors = [category_colors.get(c, "#555") for c in imp_categories]

    fig_imp = go.Figure()
    if imp_items:
        fig_imp.add_bar(
            x=[x[1] for x in imp_items],
            y=imp_y_labels,
            orientation="h",
            marker_color=imp_colors,
            customdata=imp_categories,
            hovertemplate="<b>%{y}</b><br>Importance: %{x:.4f}<br>Category: %{customdata}<extra></extra>",
        )
    else:
        fig_imp.add_annotation(text="No features selected or MDA not computed",
                               xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
    fig_imp.update_layout(
        title=f"What Drives the Composite Score? ({horizon.capitalize()} Horizon)",
        height=max(300, len(imp_items) * 28 + 100),
        xaxis_title="Permutation importance (how much model accuracy drops when this variable is scrambled)",
        margin=dict(l=280, r=60, t=80, b=40),
        paper_bgcolor="white",
        plot_bgcolor="white",
    )
    fig_imp_json = _plotly_fig_json(fig_imp)

    # -----------------------------------------------------------------------
    # Chart 5: Filter stage -- Spearman rho bar chart (appendix)
    # -----------------------------------------------------------------------
    filter_df = pd.DataFrame([
        {
            "variable": r.variable,
            "spearman_rho": r.spearman_rho,
            "spearman_pval": r.spearman_pval,
            "mutual_info": r.mutual_info,
            "passes": r.passes_filter,
        }
        for r in hr.filter_results
    ]).sort_values("spearman_rho", key=abs, ascending=False)

    colors_filter = ["#157a47" if p else "#cc2222" for p in filter_df["passes"]]
    fig_filter = go.Figure()
    fig_filter.add_bar(
        y=filter_df["variable"],
        x=filter_df["spearman_rho"].abs(),
        orientation="h",
        marker_color=colors_filter,
        text=[f"p={p:.3f}" for p in filter_df["spearman_pval"]],
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>|rho|=%{x:.3f}<br>%{text}<extra></extra>",
    )
    fig_filter.update_layout(
        title=f"Univariate signal strength vs USDCAD {horizon} returns (training data only)",
        height=max(400, len(filter_df) * 20),
        xaxis_title="|Spearman rho|",
        showlegend=False,
        margin=dict(l=200, r=80, t=80, b=40),
        paper_bgcolor="white",
        plot_bgcolor="white",
    )
    fig_filter_json = _plotly_fig_json(fig_filter)

    # -----------------------------------------------------------------------
    # Chart 6: Performance by regime (training data) -- appendix
    # -----------------------------------------------------------------------
    if v.regime_stats:
        reg_names = list(v.regime_stats.keys())
        reg_hit = [v.regime_stats[r]["hit_rate"] for r in reg_names]
        reg_r2 = [v.regime_stats[r]["r2"] for r in reg_names]
        reg_n = [v.regime_stats[r]["n_obs"] for r in reg_names]
        colors_regime = ["#157a47" if h >= 0.53 else "#d97706" if h >= 0.50 else "#cc2222" for h in reg_hit]
        fig_regime = make_subplots(rows=1, cols=2,
                                   subplot_titles=["Hit Rate by Macro Regime (training)", "OOS R² by Regime (training)"])
        fig_regime.add_bar(
            x=reg_names, y=reg_hit, marker_color=colors_regime,
            text=[f"{h:.1%}<br>n={n}" for h, n in zip(reg_hit, reg_n)],
            textposition="outside", row=1, col=1,
        )
        fig_regime.add_hline(y=0.5, line_dash="dash", line_color="gray", row=1, col=1)
        fig_regime.add_bar(
            x=reg_names, y=reg_r2, marker_color="#3a5bd9",
            text=[f"{r:.3f}" for r in reg_r2],
            textposition="outside", row=1, col=2,
        )
        fig_regime.add_hline(y=0, line_dash="dash", line_color="gray", row=1, col=2)
        fig_regime.update_layout(
            height=450, showlegend=False, paper_bgcolor="white", plot_bgcolor="white",
            title=f"Training performance by macro regime — {horizon.capitalize()} Horizon",
        )
    else:
        fig_regime = go.Figure()
        fig_regime.add_annotation(text="Insufficient data per regime", xref="paper", yref="paper",
                                   x=0.5, y=0.5, showarrow=False)
    fig_regime_json = _plotly_fig_json(fig_regime)

    # -----------------------------------------------------------------------
    # Chart 7: Walk-forward CV results -- appendix
    # -----------------------------------------------------------------------
    fold_labels = [f"Fold {i+1}" for i in range(len(v.cv_fold_r2))]
    fig_cv = make_subplots(rows=1, cols=2,
                            subplot_titles=["OOS R² by CV Fold (training)", "Hit Rate by CV Fold (training)"])
    colors_r2 = ["#157a47" if r > 0 else "#cc2222" for r in v.cv_fold_r2]
    colors_hit = ["#157a47" if h >= 0.53 else "#d97706" if h >= 0.50 else "#cc2222" for h in v.cv_fold_hit]
    fig_cv.add_bar(x=fold_labels, y=v.cv_fold_r2, marker_color=colors_r2,
                   text=[f"{r:.3f}" for r in v.cv_fold_r2], textposition="outside", row=1, col=1)
    fig_cv.add_hline(y=0, line_dash="dash", line_color="gray", row=1, col=1)
    fig_cv.add_bar(x=fold_labels, y=v.cv_fold_hit, marker_color=colors_hit,
                   text=[f"{h:.1%}" for h in v.cv_fold_hit], textposition="outside", row=1, col=2)
    fig_cv.add_hline(y=0.5, line_dash="dash", line_color="gray", row=1, col=2)
    fig_cv.update_layout(
        height=400, showlegend=False, paper_bgcolor="white", plot_bgcolor="white",
        title=f"Walk-Forward CV Results by Fold — {horizon.capitalize()} Horizon (training data only)",
    )
    fig_cv_json = _plotly_fig_json(fig_cv)

    # -----------------------------------------------------------------------
    # Color coding helpers
    # -----------------------------------------------------------------------
    dsr_color = "good" if v.dsr >= 0.95 else "warn" if v.dsr >= 0.75 else "bad"
    hit_color = "good" if v.cv_hit_rate >= 0.54 else "warn" if v.cv_hit_rate >= 0.51 else "bad"
    r2_color = "good" if v.cv_r2_oos > 0.01 else "warn" if v.cv_r2_oos > 0 else "bad"
    ho_hit_color = "good" if v.holdout_hit_rate >= 0.53 else "warn" if v.holdout_hit_rate >= 0.50 else "bad"
    ho_ext_color = ("good" if (v.holdout_hit_rate_extreme - v.holdout_hit_rate_middle) >= 0.05
                    else "warn" if (v.holdout_hit_rate_extreme - v.holdout_hit_rate_middle) >= 0 else "bad")
    holdout_box_class = "holdout-box" if v.holdout_hit_rate >= 0.53 else "holdout-fail"

    date_str = "2026-05-26"
    n_gated = len(GATED_VARIABLES)
    n_pulled = len(VARIABLE_CATALOG)

    # t-stat table rows (for appendix)
    t_rows = ""
    for feat in s.final_selected:
        t = v.t_stats.get(feat, 0.0)
        p = v.t_pvals.get(feat, 1.0)
        sig = "**" if p < 0.05 else ("*" if p < 0.10 else "")
        sign_val = s.feature_signs.get(feat, 0.0)
        sign_str = "+" if sign_val > 0 else "-"
        feat_label = feat_labels.get(feat, feat)
        t_rows += (
            f"<tr><td>{feat_label}</td>"
            f"<td>{sign_str}</td>"
            f"<td>{t:.2f}{sig}</td>"
            f"<td>{p:.3f}</td>"
            f"<td>{'Yes' if p < 0.05 else 'Marginal' if p < 0.10 else 'No'}</td></tr>\n"
        )

    # Horizon-specific inline caveats
    if horizon == "weekly":
        horizon_caveat_inline = """
<div class="honest-box">
<p><strong>Weekly-specific caveat:</strong> General (non-extreme) signal is weak. The overall hold-out hit rate
is only marginally above 50%, which is not meaningfully different from a coin flip.
The edge is real only at extreme composite score readings (top and bottom 10%).
Do not use this model to call direction in ordinary, non-extreme periods.</p>
</div>"""
    elif horizon == "monthly":
        horizon_caveat_inline = f"""
<div class="warning-box">
<p><strong>Monthly-specific caveat: CV failure on training data.</strong>
Cross-validation on the training set showed inconsistent performance across CV folds.
This means the training-period signal was not stable across historical macro regimes.
The hold-out result ({v.holdout_start_date} to {v.holdout_end_date}) is from a single macro regime
(BoC tightening and tariff shock). Whether the signal generalizes to other regimes is unknown.
Do not treat the hold-out hit rate as a stable, regime-independent forecast accuracy.</p>
</div>"""
    else:  # quarterly
        non_overlap_approx = max(1, v.holdout_n_obs // 63)
        horizon_caveat_inline = f"""
<div class="warning-box">
<p><strong>Quarterly-specific caveat: statistically thin hold-out.</strong>
The quarterly hold-out contains {v.holdout_n_obs} rows of daily data, but because quarterly returns
overlap heavily, there are only approximately <strong>{non_overlap_approx} non-overlapping 63-day periods</strong>.
At this sample size, the reported hit rate has very wide confidence intervals.
A few lucky or unlucky quarters can swing the number by 10+ percentage points.
Statistical conclusions for the quarterly model are fragile. Treat it as a framework, not a validated tool.</p>
</div>"""

    exec_summary_html = _horizon_exec_summary(horizon, v, hr)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>USDCAD {horizon.capitalize()} Model — Phase 3 Diagnostic ({date_str})</title>
  {_plotly_cdn_script()}
  {_style_block()}
</head>
<body>

<h1>USDCAD {horizon.capitalize()} Horizon — Phase 3 Diagnostic
  <span class="phase3-badge">Phase 3</span>
</h1>
<p class="meta">Sibley Creek analytical work product. Produced {date_str}. NOT for publication.
Phase 3 corrects: (1) sign-assignment look-ahead, (2) true 20% hold-out.
Previous Phase 2 CV hit rates are not cited here.</p>

<!-- EXECUTIVE SUMMARY -->
{exec_summary_html}

<!-- TABLE OF CONTENTS -->
<div class="toc">
  <h3>In this diagnostic</h3>
  <ol>
    <li><a href="#score-chart">The composite score in action</a> — score history vs USDCAD, with the hold-out region marked</li>
    <li><a href="#holdout">How well did it work? (hold-out test)</a> — the only honest performance figure</li>
    <li><a href="#extremes">When does the edge appear?</a> — extreme-reading hit rate vs neutral periods</li>
    <li><a href="#importance">What variables drive the score?</a> — variable importance, plain-English categories</li>
    <li><a href="#methodology">How was the score built?</a> — filter, selection, CV, sign-fix in plain English</li>
    <li><a href="#caveats">What could be wrong?</a> — honest failure modes and limitations</li>
  </ol>
  <p style="margin-top:12px; font-size:0.84rem; color:#888;">
    Technical details (variable universe, CV fold results, transformation audit, t-statistics):
    <a href="#appendix-vars" class="appendix-link">A1. Variable universe</a> |
    <a href="#appendix-cv" class="appendix-link">A2. Cross-validation details</a> |
    <a href="#appendix-transforms" class="appendix-link">A3. Data transformations</a> |
    <a href="#appendix-tstats" class="appendix-link">A4. T-statistics</a>
  </p>
</div>

<!-- ======================================================= -->
<!-- SECTION 1: SCORE IN ACTION -->
<!-- ======================================================= -->
<h2 id="score-chart">1. The Composite Score in Action</h2>

<div class="chart-intro">
  <p><strong>What this shows:</strong> The composite score (blue dotted line, right axis) plotted alongside the USDCAD exchange rate (black, left axis) from 2005 to today. Each coloured band is a different macro regime.</p>
  <p><strong>What to look for:</strong> The green-shaded region on the right is the <em>hold-out period</em> — data the model never saw during fitting. How the score behaves there is the real test. Look for whether large score moves (positive or negative) coincide with USDCAD moves in the expected direction.</p>
  <p><strong>How to read it:</strong> A high positive score means the model's indicators are all pointing toward USD strength (USDCAD up). A large negative score points toward CAD strength (USDCAD down). Score near zero means indicators are mixed and the model has no directional view.</p>
</div>
<div class="chart-wrap">
  <div id="chart-score"></div>
</div>
<div class="chart-conclude">
  <strong>What we conclude:</strong> The score tracks broad USDCAD regimes reasonably well in the training period. The hold-out region is the honest test — divergences there are genuine failures, not artefacts of fitting.
</div>

<hr class="section-divider">

<!-- ======================================================= -->
<!-- SECTION 2: HOLD-OUT PERFORMANCE -->
<!-- ======================================================= -->
<h2 id="holdout">2. How Well Did It Work? (Hold-Out Test)</h2>

<div class="plain-english">
  <p><strong>What is a hold-out test?</strong> The last 20% of the data ({v.holdout_start_date} to {v.holdout_end_date}, n={v.holdout_n_obs} rows) was locked away before any fitting began. The model never saw it during training, variable selection, or CV tuning. It was evaluated exactly once, after all model decisions were fixed. This is the only honest performance figure.</p>
  <p style="margin-top:8px;"><strong>Hit rate</strong> = the proportion of time periods where the model's direction call (positive score = USD up; negative = USD down) matched the actual USDCAD move. 50% = no better than a coin flip.</p>
</div>

{horizon_caveat_inline}

<div class="stat-grid">
  <div class="stat-card holdout {ho_hit_color}">
    <div class="label">Hold-Out Hit Rate</div>
    <div class="value">{v.holdout_hit_rate:.1%}</div>
    <div class="caption">Overall directional accuracy on unseen data<br>50% = coin flip</div>
  </div>
  <div class="stat-card holdout {ho_ext_color}">
    <div class="label">Hold-Out Extreme Edge</div>
    <div class="value">{(v.holdout_hit_rate_extreme - v.holdout_hit_rate_middle)*100:+.1f}pp</div>
    <div class="caption">Extremes vs middle 80%<br>({v.holdout_n_extreme_obs} extreme obs)</div>
  </div>
  <div class="stat-card holdout {'good' if v.holdout_r2 > 0 else 'bad'}">
    <div class="label">Hold-Out R&#178;</div>
    <div class="value">{v.holdout_r2:.4f}</div>
    <div class="caption">Positive = model adds information above naive baseline</div>
  </div>
  <div class="stat-card holdout">
    <div class="label">Hold-Out Sharpe</div>
    <div class="value">{v.holdout_sharpe:.2f}</div>
    <div class="caption">Annualized Sharpe of a sign-of-score trade strategy on hold-out</div>
  </div>
</div>

<div class="chart-intro">
  <p><strong>What this shows:</strong> Left panel: overall hit rate, extreme-reading hit rate, and middle-80% hit rate on the hold-out. The dashed line is 50% (no skill). Right panel: each dot is one {horizon} period in the hold-out. Green = model called direction correctly; red = incorrect. Dots in the upper-right and lower-left quadrants are hits.</p>
  <p><strong>What to look for:</strong> On the left, is the extreme-reading bar (middle) meaningfully higher than the middle-80% bar (right)? On the right scatter, do the green dots cluster at high positive and high negative scores, with red dots near zero?</p>
</div>
<div class="chart-wrap">
  <div id="chart-holdout"></div>
</div>
<div class="chart-conclude">
  <strong>What we conclude:</strong> Hold-out hit rate: <strong>{v.holdout_hit_rate:.1%}</strong> overall.
  Extreme-reading hit rate: <strong>{v.holdout_hit_rate_extreme:.1%}</strong> vs middle-80%: <strong>{v.holdout_hit_rate_middle:.1%}</strong>
  ({(v.holdout_hit_rate_extreme - v.holdout_hit_rate_middle)*100:+.1f}pp edge).
  This is the number to use in any client-facing claim about model performance.
</div>

<hr class="section-divider">

<!-- ======================================================= -->
<!-- SECTION 3: EXTREMES -->
<!-- ======================================================= -->
<h2 id="extremes">3. When Does the Edge Appear?</h2>

<div class="plain-english">
  <p><strong>The product hypothesis:</strong> The composite score is most useful when all the underlying indicators are aligned in the same direction — i.e., when the score is in the top or bottom 10% of its historical distribution. In neutral periods (the middle 80%), indicators are mixed and the model has no meaningful edge.</p>
  <p style="margin-top:8px;"><strong>Extreme reading</strong> = score in the top or bottom 10% of its historical distribution on training data. These are the periods when the model is "making a strong call." <strong>Middle 80%</strong> = everything else — the model sees mixed signals and offers no strong view.</p>
</div>

<div class="chart-intro">
  <p><strong>What this shows:</strong> Hit rates for extreme and middle readings, both in training data (blue) and in the hold-out (green). The hold-out bars are the honest numbers. The right panel shows the distribution of actual USDCAD returns in extreme vs middle periods during training.</p>
  <p><strong>What to look for:</strong> Is the "Hold-out Extremes" bar (green, left) meaningfully higher than "Hold-out Middle 80%"? Is the return distribution for extreme periods (blue histogram, right) more shifted away from zero than the middle distribution?</p>
</div>
<div class="chart-wrap">
  <div id="chart-extremes"></div>
</div>
<div class="chart-conclude">
  <strong>What we conclude:</strong>
  Training extreme edge: {(v.hit_rate_extreme - v.hit_rate_middle)*100:+.1f}pp ({v.n_extreme_obs} extreme obs in training).
  Hold-out extreme edge: {(v.holdout_hit_rate_extreme - v.holdout_hit_rate_middle)*100:+.1f}pp ({v.holdout_n_extreme_obs} extreme obs in hold-out).
  {"The edge is present in both training and hold-out, which supports the hypothesis." if (v.holdout_hit_rate_extreme - v.holdout_hit_rate_middle) > 0.03 else "The hold-out edge is smaller than training, as expected. Whether the gap reflects regime specificity or noise requires further testing."}
</div>

<hr class="section-divider">

<!-- ======================================================= -->
<!-- SECTION 4: VARIABLE IMPORTANCE -->
<!-- ======================================================= -->
<h2 id="importance">4. What Variables Drive the Score?</h2>

<div class="plain-english">
  <p><strong>How variables were selected:</strong> We started with {n_pulled} candidate variables, each chosen because it has a documented economic reason to predict USDCAD — not because it backtested well. Three independent methods (ElasticNet regularization, Boruta random forest, permutation importance) each voted on which variables to keep. A variable needed at least 2 of 3 votes to enter the final model.</p>
  <p style="margin-top:8px;"><strong>Final selected: {len(s.final_selected)} variables</strong>, shown in the chart below.</p>
  <p style="margin-top:8px;"><strong>Permutation importance</strong> (the x-axis) measures how much the model's accuracy drops when a variable's values are randomly scrambled. A higher bar = the model relies more on that variable. A bar near zero = the variable adds little beyond what the others already provide.</p>
</div>

<div class="chart-intro">
  <p><strong>What this shows:</strong> Each bar is one of the {len(s.final_selected)} variables in the final composite score, coloured by category. Bars run left to right from most to least important (based on permutation importance on training data).</p>
  <p><strong>What to look for:</strong> Which category dominates? Are the leading variables things that have strong economic rationales, or do they look like noise proxies? Variable names are in the format [ID]: [short description].</p>
</div>
<div class="chart-wrap">
  <div id="chart-importance"></div>
</div>
<div class="chart-conclude">
  <strong>What we conclude:</strong> The top variables by permutation importance reveal which economic channels are most active at the {horizon} horizon. Technical price signals (Block I) often dominate at shorter horizons; macro fundamentals (Block F) tend to matter more at longer horizons.
</div>

<hr class="section-divider">

<!-- ======================================================= -->
<!-- SECTION 5: METHODOLOGY -->
<!-- ======================================================= -->
<h2 id="methodology">5. How Was the Score Built?</h2>

<div class="plain-english">
  <p><strong>The four-step pipeline, in plain English:</strong></p>
  <p><strong>Step 1 — Filter:</strong> Each of the {n_pulled} candidate variables was tested individually against USDCAD {horizon} returns using rank correlation (Spearman rho). Variables with near-zero correlation AND near-zero mutual information were dropped outright. This is a coarse first pass — it only removes variables that show no signal at all, even individually. {hr.n_features_after_filter} of {hr.n_features_input} candidates passed this filter.</p>
  <p style="margin-top:8px;"><strong>Step 2 — Feature selection (three methods, two-of-three vote):</strong> The {hr.n_features_after_filter} remaining variables were fed into three independent selection methods: (1) ElasticNet, which picks variables that add predictive power when combined and penalizes redundancy; (2) Boruta, a random-forest-based method that compares each variable against random "shadow" features; (3) Mean Decrease in Accuracy (MDA), which measures how much accuracy drops when each variable is scrambled. A variable needed to be selected by at least 2 of these 3 methods to enter the final score. Result: {len(s.final_selected)} variables selected.</p>
  <p style="margin-top:8px;"><strong>Step 3 — Sign assignment:</strong> For each selected variable, we determined whether a higher value predicts USDCAD up or USDCAD down. Critically, this was done using only the <em>first half of the training data</em> ({s.sign_determination_n} rows), then frozen. This prevents a subtle form of cheating where knowing which direction is correct in the full dataset contaminates the score.</p>
  <p style="margin-top:8px;"><strong>Step 4 — Composite score:</strong> Each selected variable is standardized (subtracted its mean, divided by its standard deviation, both computed on training data only), then multiplied by its sign (+1 or -1), then averaged. The result is a single number per day. Positive = indicators on balance pointing to USD strength. Negative = CAD strength. Near zero = mixed signals.</p>
</div>

<div class="fix-box">
<p><strong>Phase 3 methodology corrections applied to this diagnostic:</strong></p>
<p><strong>Fix 1 (Sign-assignment look-ahead, eliminated):</strong> Phase 2 computed Spearman correlations on the FULL dataset to determine each feature's sign in the composite score. This created mild in-sample alignment that inflated the CV hit rate. Phase 3 determines signs exclusively from the FIRST HALF of the training data ({s.sign_determination_n} rows). Signs are frozen and never re-estimated on hold-out data.</p>
<p style="margin-top:8px;"><strong>Fix 2 (True hold-out):</strong> The last 20% of data ({hr.holdout_split_date} to present, n={v.holdout_n_obs} rows) was reserved before any variable selection, hyperparameter tuning, or CV fitting. The hold-out was evaluated exactly once. The hold-out result is the only honest performance figure.</p>
</div>

<h3>Training performance summary (internal reference)</h3>
<p style="color:#666; font-size:0.88rem;">These numbers characterize model behaviour on training data. They are presented for completeness but are not the headline performance figures. See hold-out results in Section 2.</p>
<div class="stat-grid">
  <div class="stat-card {dsr_color}">
    <div class="label">Deflated Sharpe Ratio</div>
    <div class="value">{v.dsr:.2f}</div>
    <div class="caption">Adjusts for multiple variables tested ({v.n_trials} tested). 0.95+ = not just luck. Threshold: 0.95</div>
  </div>
  <div class="stat-card {hit_color}">
    <div class="label">CV Hit Rate (training)</div>
    <div class="value">{v.cv_hit_rate:.1%}</div>
    <div class="caption">Sign-corrected. Across {len(v.cv_fold_hit)} CV folds. 54%+ = meaningful in FX</div>
  </div>
  <div class="stat-card {r2_color}">
    <div class="label">OOS R&#178; (CV, training)</div>
    <div class="value">{v.cv_r2_oos:.4f}</div>
    <div class="caption">Positive = beating naive forecast. FX R&#178; of 0.01 is economically meaningful</div>
  </div>
  <div class="stat-card {'good' if (v.hit_rate_extreme - v.hit_rate_middle) > 0.03 else 'warn' if (v.hit_rate_extreme - v.hit_rate_middle) >= 0 else 'bad'}">
    <div class="label">Training Extreme Edge</div>
    <div class="value">{(v.hit_rate_extreme - v.hit_rate_middle)*100:+.1f}pp</div>
    <div class="caption">Top/bottom 10% vs middle 80% (training only)</div>
  </div>
</div>

<hr class="section-divider">

<!-- ======================================================= -->
<!-- SECTION 6: CAVEATS -->
<!-- ======================================================= -->
<h2 id="caveats">6. What Could Be Wrong?</h2>

<div class="honest-box">
<p><strong>Required per Sibley Creek analytical canon. Read before using this model for any client-facing work.</strong></p>
</div>

<p><strong>1. Missing options data (Bloomberg-gated).</strong> USDCAD risk reversals and implied volatility are among the strongest USDCAD-specific signals in the FX forecasting literature (Della Corte-Ramadorai-Sarno 2014). The options market embeds real-money participants' directional views in a way that no macro variable can replicate. This model systematically underperforms a full-data version.</p>

<p><strong>2. Missing CESI differential.</strong> The Citi Economic Surprise Index differential (Canada minus US) is the most widely cited real-time data-surprise signal on FX desks. It captures whether incoming data is beating or missing expectations — which directly moves USDCAD at release. Its absence makes the model slow to react to data releases.</p>

<p><strong>3. Structural regime breaks.</strong> The model is trained on 2005–2026 data spanning multiple regimes. The 2025–2026 tariff shock is genuinely unprecedented. The Caldara TPU variable is included, but it cannot fully capture CUSMA-specific dynamics or the current tariff magnitudes. The model may be poorly calibrated for the current regime.</p>

<p><strong>4. CAD-oil decoupling.</strong> WTI and BCPI variables may have been selected partly on the basis of pre-2016 history, when the CAD-oil link was tighter. The relationship has structurally weakened since 2016 (BoC SAN 2017-1). These variables may be adding noise rather than signal in the current regime.</p>

<p><strong>5. Commodity price stationarity compromise.</strong> Commodity prices are used in levels (following the cointegration literature), not returns. This is a known non-standard choice. If the cointegrating relationship between commodity prices and USDCAD is unstable across regimes (plausible post-2016), this introduces model-misspecification risk. Phase 4 robustness check: re-run with commodity log returns.</p>

<p><strong>6. Hold-out regime concentration.</strong> The hold-out period ({v.holdout_start_date} to {v.holdout_end_date}) covers primarily the BoC tightening cycle and the Trump tariff era. Whether the model performs at these hold-out levels in a commodity-boom regime or a BoC easing cycle is unknown.</p>

<p><strong>7. {horizon.capitalize()}-specific limitation:</strong>
{"General signal is weak. The overall hold-out hit rate is only marginally above 50%. Do not use outside extreme-reading episodes." if horizon == "weekly" else
("Cross-validation failed on training data — performance was inconsistent across CV folds. The hold-out is from one regime only." if horizon == "monthly" else
f"Thin statistical base: approximately {max(1, v.holdout_n_obs // 63)} non-overlapping quarterly hold-out periods. Wide confidence intervals around all reported numbers.")}</p>

<hr class="section-divider">

<!-- ======================================================= -->
<!-- APPENDIX -->
<!-- ======================================================= -->
<h2>Appendix: Technical Details</h2>
<p style="color:#666; font-size:0.9rem; margin-bottom:32px;">The following sections contain the full statistical output for those who want to verify the methodology in detail. They are moved here because the primary reader — a smart non-expert — does not need them to evaluate the headline findings.</p>

<!-- A1: Variable universe -->
<div class="appendix-section" id="appendix-vars">
  <h2>A1. Variable Universe ({n_pulled} pulled + {n_gated} gated/deferred)</h2>
  <p>The candidate set was locked before any back-testing. Each variable entered because it has a documented economic mechanism, not because it backtested well. Filter-stage statistics are computed on training data only. <span class="tag tag-must">Must</span> = strong theory + strong USDCAD-specific empirics. <span class="tag tag-should">Should</span> = strong theory OR strong empirics. <span class="tag tag-nice">Nice-to-have</span> = defensible but thin empirical track record. Green rows = final model. Red rows = available but not selected. Yellow rows = unavailable (gated/deferred).</p>
  {_build_variable_table(hr.filter_results, s.final_selected)}
  <div class="honest-box">
  <p><strong>Most important missing variables:</strong> Citi CESI (economic surprise index differential, Canada minus US) and USDCAD options data (risk reversals, implied vol skew) are Bloomberg proprietary. The CESI differential is standard input on every major FX desk. A full-data version of this model would likely perform materially differently.</p>
  </div>
</div>

<!-- A2: Filter stage + CV details -->
<div class="appendix-section" id="appendix-cv">
  <h2>A2. Filter Stage and Cross-Validation Details</h2>

  <h3>Filter stage — univariate signal screening</h3>
  <p>Spearman rank correlations computed on training data only (first 80%). Variables with |rho| below the minimum threshold AND mutual information below the minimum threshold were dropped. Note: univariate screening in a small-signal FX environment is coarse — the embedded selection stage does the real culling. {hr.n_features_after_filter} of {hr.n_features_input} features passed the filter.</p>
  <div class="chart-wrap-standalone">
    <div id="chart-filter"></div>
  </div>

  <h3>Walk-forward cross-validation results</h3>
  <p>Purged walk-forward CV on training data (Lopez de Prado methodology). Embargo = {hr.horizon_h} business days per fold. {s.n_cv_folds} folds. Each bar = one out-of-sample test period within training data. R&#178; = predictive power above naive baseline. The aggregate (mean across folds) is what we report. Signs are determined from first-half training data only — consistent with the Phase 3 sign-fix.</p>
  <div class="chart-wrap-standalone">
    <div id="chart-cv"></div>
  </div>

  <h3>Performance by macro regime (training data)</h3>
  <p>Training hit rate and R&#178; broken down by historical macro regime. This shows whether the model performs consistently across different economic environments, or is concentrated in specific periods. Hold-out performance cannot be regime-segmented (hold-out is too short).</p>
  <div class="chart-wrap-standalone">
    <div id="chart-regime"></div>
  </div>

  <h3>Embedded selection detail</h3>
  <p>Three methods, two-of-three vote required for selection:</p>
  <ul>
    <li><strong>ElasticNet:</strong> alpha={s.elasticnet_alpha:.4f}, L1-ratio={s.elasticnet_l1_ratio:.2f}. Selected {len(s.elasticnet_selected)} features.</li>
    <li><strong>Boruta:</strong> {len(s.boruta_confirmed)} confirmed, {len(s.boruta_tentative)} tentative.</li>
    <li><strong>MDA:</strong> Top {len(s.mda_selected)} features by permutation importance.</li>
    <li><strong>Final (2/3 vote): {len(s.final_selected)} features. Intersection (all three): {len(s.final_intersection)} features.</strong></li>
  </ul>
</div>

<!-- A3: Data transformations -->
<div class="appendix-section" id="appendix-transforms">
  <h2>A3. Data Transformations Applied</h2>
  <p>Explicit audit of how each variable group is transformed before entering the model. Addresses the question: "are you running levels or returns?" Stationarity status and look-ahead prevention documented per group.</p>
  {_build_transformation_table()}
  <div class="honest-box">
  <p><strong>One deliberate stationarity compromise:</strong> Commodity price levels (WTI, Brent, BCPI) are used in levels rather than returns. This is a known I(1) variable in a regression. Justification: cointegration literature (Cashin-Cespedes-McDermott 2004; Amano-van Norden 1995) establishes a stable long-run relationship between commodity price levels and commodity-currency exchange rates. If this relationship is unstable post-2016 (plausible given CAD-oil decoupling), commodity level variables may introduce spurious regression artifacts. Phase 4 robustness check: re-run with commodity log returns.</p>
  </div>
</div>

<!-- A4: T-statistics -->
<div class="appendix-section" id="appendix-tstats">
  <h2>A4. In-Sample T-Statistics on Selected Features</h2>
  <p>In-sample statistics for the {len(s.final_selected)} selected features. Presented for completeness — these are computed on training data and overstate true significance due to repeated testing during feature selection. The hold-out results in Section 2 are the honest performance figures. ** = p&lt;0.05, * = p&lt;0.10.</p>
  <p style="font-size:0.85rem; color:#666; margin-bottom:12px;">Sign column = direction determined from first-half training data (Phase 3 fix).</p>
  <table>
  <thead><tr><th>Feature</th><th>Sign</th><th>t-stat</th><th>p-value</th><th>Significant?</th></tr></thead>
  <tbody>
  {t_rows if t_rows else "<tr><td colspan='5'>No features selected</td></tr>"}
  </tbody>
  </table>

  <h3>Honest Phase 3 assessment (full text)</h3>
  <div class="honest-box">
  <pre>{hr.honest_assessment}</pre>
  </div>
</div>

<hr class="section-divider">
<p class="meta">
Produced by Sibley Creek analytics pipeline (Phase 3). Methodology paper:
claude-ref/research/usdcad/usdcad_methodology_paper_2026-05-26.md.
Pipeline: pipeline/usdcad/. Data: BoC Valet, FRED, Yahoo Finance, policyuncertainty.com.
</p>

<script>
(function() {{
  var scoreData = {fig_score_json};
  Plotly.newPlot('chart-score', scoreData.data, scoreData.layout, {{responsive: true, displayModeBar: true}});

  var holdoutData = {fig_holdout_json};
  Plotly.newPlot('chart-holdout', holdoutData.data, holdoutData.layout, {{responsive: true, displayModeBar: false}});

  var extremesData = {fig_extremes_json};
  Plotly.newPlot('chart-extremes', extremesData.data, extremesData.layout, {{responsive: true, displayModeBar: false}});

  var impData = {fig_imp_json};
  Plotly.newPlot('chart-importance', impData.data, impData.layout, {{responsive: true, displayModeBar: false}});

  var filterData = {fig_filter_json};
  Plotly.newPlot('chart-filter', filterData.data, filterData.layout, {{responsive: true, displayModeBar: false}});

  var cvData = {fig_cv_json};
  Plotly.newPlot('chart-cv', cvData.data, cvData.layout, {{responsive: true, displayModeBar: false}});

  var regimeData = {fig_regime_json};
  Plotly.newPlot('chart-regime', regimeData.data, regimeData.layout, {{responsive: true, displayModeBar: false}});
}})();
</script>

</body>
</html>"""

    output_path.write_text(html, encoding="utf-8")
    logger.info("Diagnostic HTML written: %s (%d bytes)", output_path, output_path.stat().st_size)


def generate_all_diagnostics(results: dict) -> None:
    """Generate Phase 3 diagnostic HTML for all horizon results."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for horizon, hr in results.items():
        out = OUTPUT_DIR / f"usdcad_diagnostic_{horizon}_2026-05-26.html"
        try:
            generate_diagnostic_html(hr, out)
        except Exception as e:
            logger.error("Diagnostic generation failed for %s: %s", horizon, e, exc_info=True)
