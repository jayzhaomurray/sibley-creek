"""Inflation basics-layer anchor extraction for Wave 3 brief W3-R2.

Computes per-panel latest-print anchors for Inflation section v1 basics:
  Panel 1: Headline CPI -- Y/Y, M/M (SA), 3M AR (SA)
  Panel 2: Core measures (core-trim, core-median, core-common Y/Y)
  Panel 3: Breadth -- share of basket (weighted) above 3%, 1-3%, below 1%
  Panel 4: Sub-aggregates -- shelter (with MIC decomposed), services, goods, food, energy
  Panel 5: Inflation expectations -- CSCE 1y/5y, BOS distribution
  Panel 6: Pass-through inputs -- USDCAD Y/Y, LFS-Micro wage Y/Y

Also produces a go/no-go diagnostic on basket-weighted derivations of:
  - services ex-shelter Y/Y
  - goods ex-energy Y/Y

ASCII-only output. No emojis. Source data is read from boc-tracker's
data/ folder. Outputs CSV summaries to this folder.

Methodology notes:
  - Y/Y on the NSA index for headline (BoC / StatCan convention; SA Y/Y
    is approximately equal but NSA is the published reference).
  - M/M on SA index.
  - 3M AR on SA index using last three monthly growth rates compounded:
        ((index[t]/index[t-3])^(12/3) - 1) * 100
  - Breadth uses NSA component index Y/Y, weighted by 2024 basket weights
    from boc-tracker's cpi_breadth_mapping.json (StatCan Table 18-10-0007).
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

BOC = Path(r"C:\Users\jayzh\Documents\boc-tracker\data")
OUT = Path(__file__).resolve().parent


def load_series(name: str) -> pd.Series:
    df = pd.read_csv(BOC / f"{name}.csv", parse_dates=["date"])
    df = df.set_index("date").sort_index()
    col = df.columns[0]
    return df[col].rename(name)


def latest_yoy(s: pd.Series) -> tuple[pd.Timestamp, float]:
    yoy = s.pct_change(12) * 100
    yoy = yoy.dropna()
    return yoy.index[-1], float(yoy.iloc[-1])


def latest_mom(s: pd.Series) -> tuple[pd.Timestamp, float]:
    mom = s.pct_change(1) * 100
    mom = mom.dropna()
    return mom.index[-1], float(mom.iloc[-1])


def latest_3m_ar(s: pd.Series) -> tuple[pd.Timestamp, float]:
    """Three-month annualized growth (geometric)."""
    ar3 = ((s / s.shift(3)) ** (12.0 / 3.0) - 1.0) * 100.0
    ar3 = ar3.dropna()
    return ar3.index[-1], float(ar3.iloc[-1])


def latest_value(s: pd.Series) -> tuple[pd.Timestamp, float]:
    s2 = s.dropna()
    return s2.index[-1], float(s2.iloc[-1])


def main() -> None:
    print("=" * 72)
    print("INFLATION BASICS LAYER -- LATEST-PRINT ANCHORS")
    print("Run date: 2026-05-11 | Source: boc-tracker/data/")
    print("=" * 72)

    # ---------------------------------------------------------
    # Panel 1: Headline CPI (SA + NSA), Y/Y / M/M / 3M AR
    # ---------------------------------------------------------
    cpi_sa = load_series("cpi_all_items")
    cpi_nsa = load_series("cpi_all_items_nsa")

    d1, yoy_nsa = latest_yoy(cpi_nsa)
    d2, yoy_sa = latest_yoy(cpi_sa)
    d3, mom_sa = latest_mom(cpi_sa)
    d4, ar3_sa = latest_3m_ar(cpi_sa)

    print()
    print("PANEL 1: Headline CPI")
    print(f"  NSA Y/Y       : {yoy_nsa:.2f}%   (ref month {d1.date()})")
    print(f"  SA  Y/Y       : {yoy_sa:.2f}%   (ref month {d2.date()})")
    print(f"  SA  M/M       : {mom_sa:.2f}%   (ref month {d3.date()})")
    print(f"  SA  3M AR     : {ar3_sa:.2f}%   (ref month {d4.date()})")

    # ---------------------------------------------------------
    # Panel 2: Core measures (already published Y/Y)
    # ---------------------------------------------------------
    trim = load_series("cpi_trim")
    median = load_series("cpi_median")
    common = load_series("cpi_common")
    cpix = load_series("cpix")
    cpixfet = load_series("cpixfet")

    print()
    print("PANEL 2: Core measures (Y/Y; pre-published by BoC)")
    for name, s in [
        ("core-trim", trim),
        ("core-median", median),
        ("core-common", common),
        ("CPIX", cpix),
        ("CPIXFET", cpixfet),
    ]:
        d, v = latest_value(s)
        print(f"  {name:<13}: {v:.2f}%   (ref month {d.date()})")

    # ---------------------------------------------------------
    # Panel 3: Breadth shares (weighted)
    # ---------------------------------------------------------
    mapping = json.loads((BOC / "cpi_breadth_mapping.json").read_text())
    comp = pd.read_csv(BOC / "cpi_components.csv", parse_dates=["date"]).set_index("date")
    yoy_comp = comp.pct_change(12) * 100
    last = yoy_comp.iloc[-1].dropna()
    last_date = yoy_comp.index[-1]

    wt_lookup = {m["name"]: m["wt_value"] for m in mapping}
    rows = []
    for name, val in last.items():
        w = wt_lookup.get(name)
        if w is None:
            continue
        rows.append({"component": name, "yoy": val, "weight": w})
    bdf = pd.DataFrame(rows)

    total_w = bdf["weight"].sum()
    share_above3 = bdf.loc[bdf["yoy"] > 3.0, "weight"].sum() / total_w * 100
    share_in13 = bdf.loc[(bdf["yoy"] >= 1.0) & (bdf["yoy"] <= 3.0), "weight"].sum() / total_w * 100
    share_below1 = bdf.loc[bdf["yoy"] < 1.0, "weight"].sum() / total_w * 100

    print()
    print(f"PANEL 3: Breadth (weighted by 2024 basket; n={len(bdf)} components, "
          f"weight sum={total_w:.1f} of ~100)")
    print(f"  Reference month: {last_date.date()}")
    print(f"  Share > 3%     : {share_above3:.1f}%")
    print(f"  Share 1-3%     : {share_in13:.1f}%")
    print(f"  Share < 1%     : {share_below1:.1f}%")
    print(f"  (Above-3 plus in-band plus below-1 sums to "
          f"{share_above3 + share_in13 + share_below1:.1f}%)")

    # ---------------------------------------------------------
    # Panel 4: Sub-aggregates -- Y/Y from NSA major series
    # ---------------------------------------------------------
    print()
    print("PANEL 4: Sub-aggregates (Y/Y on NSA index)")
    for name in ["cpi_shelter", "cpi_services", "cpi_goods", "cpi_food", "cpi_energy"]:
        s = load_series(name)
        d, yoy = latest_yoy(s)
        print(f"  {name:<14}: {yoy:.2f}%   (ref month {d.date()})")

    # ---------------------------------------------------------
    # Mortgage interest cost (MIC) component from the 60-component panel
    # ---------------------------------------------------------
    mic_name = "Mortgage interest cost"
    if mic_name in comp.columns:
        mic_series = comp[mic_name].dropna()
        mic_yoy = mic_series.pct_change(12).dropna() * 100
        print(f"  MIC (component): {mic_yoy.iloc[-1]:.2f}%   (ref month {mic_yoy.index[-1].date()})")

    # ---------------------------------------------------------
    # Go/no-go: derive services ex-shelter and goods ex-energy
    # ---------------------------------------------------------
    print()
    print("DERIVATION GO/NO-GO -- services ex-shelter, goods ex-energy")
    print()
    print("Requirement: basket-weighted residual aggregate from published")
    print("all-services and all-goods less named sub-component, using basket")
    print("weights from StatCan Table 18-10-0007-01.")
    print()
    print("Inputs we have in boc-tracker today:")
    print("  - cpi_services (all-services NSA index)         : yes")
    print("  - cpi_goods    (all-goods NSA index)            : yes")
    print("  - cpi_shelter  (all-shelter NSA index)          : yes")
    print("  - cpi_energy   (all-energy NSA index)           : yes")
    print("  - basket weights for major aggregates           : NOT in cpi_breadth_mapping")
    print("    (the mapping covers 60 *components* under the all-items basket,")
    print("     not the major-aggregate weights for services / goods / shelter / energy)")
    print()
    print("Construction options:")
    print("  (a) Weighted-residual: ServicesExShelter_idx = "
          "(W_S * Services_idx - W_Sh * Shelter_idx) / (W_S - W_Sh)")
    print("      Requires the *current* basket weights for services and shelter")
    print("      from Table 18-10-0007. Routine StatCan WDS pull, not yet in fetch.py.")
    print("  (b) Component-bottom-up: aggregate the relevant subset of the 60")
    print("      components in cpi_breadth_mapping that fall under services-ex-shelter")
    print("      (and goods-ex-energy), using the 2024 weights already stored.")
    print("      Requires a taxonomy assignment: which of the 60 components belong to")
    print("      services-ex-shelter vs goods-ex-energy. Not yet documented.")
    print()
    print("Recommendation: see methodology callout in the research index.")

    # ---------------------------------------------------------
    # Panel 5: Inflation expectations
    # ---------------------------------------------------------
    print()
    print("PANEL 5: Inflation expectations")
    csce1 = load_series("infl_exp_consumer_1y")
    csce5 = load_series("infl_exp_consumer_5y")
    above3 = load_series("infl_exp_above3")
    bos_below1 = load_series("bos_dist_below1")
    bos_1to2 = load_series("bos_dist_1to2")
    bos_2to3 = load_series("bos_dist_2to3")
    bos_above3 = load_series("bos_dist_above3")
    for name, s in [
        ("CSCE 1y mean", csce1),
        ("CSCE 5y mean", csce5),
        ("BOS firms expecting CPI > 3% over 2y (ABOVE3)", above3),
        ("BOS dist <1%", bos_below1),
        ("BOS dist 1-2%", bos_1to2),
        ("BOS dist 2-3%", bos_2to3),
        ("BOS dist >3%", bos_above3),
    ]:
        d, v = latest_value(s)
        print(f"  {name:<46}: {v:.2f}   (ref {d.date()})")

    # ---------------------------------------------------------
    # Panel 6: Pass-through inputs
    # ---------------------------------------------------------
    print()
    print("PANEL 6: Pass-through panel inputs")

    # USDCAD: daily; compute month-end Y/Y
    usd = pd.read_csv(BOC / "usdcad.csv", parse_dates=["date"]).set_index("date").sort_index()
    usd_m = usd["value"].resample("ME").last()
    usd_yoy = usd_m.pct_change(12).dropna() * 100
    print(f"  USDCAD month-end             : {usd_m.iloc[-1]:.4f}   (last {usd_m.index[-1].date()})")
    print(f"  USDCAD Y/Y                   : {usd_yoy.iloc[-1]:.2f}%  (last {usd_yoy.index[-1].date()})")

    # LFS-Micro wage Y/Y (already in Y/Y units per boc-tracker docs)
    micro = load_series("lfs_micro")
    d, v = latest_value(micro)
    print(f"  LFS-Micro wage Y/Y           : {v:.2f}%  (ref {d.date()})")

    # Goods Y/Y, Services Y/Y as the pass-through right-hand side proxies
    d, g_yoy = latest_yoy(load_series("cpi_goods"))
    print(f"  Goods Y/Y (proxy)            : {g_yoy:.2f}%  (ref {d.date()})")
    d, s_yoy = latest_yoy(load_series("cpi_services"))
    print(f"  Services Y/Y (proxy)         : {s_yoy:.2f}%  (ref {d.date()})")

    print()
    print("Note: pass-through panel target series are goods-ex-energy and")
    print("services-ex-shelter; the goods/services Y/Y above are shown as")
    print("placeholder proxies until those derivations land. If derivations")
    print("slip to v1.5 the pass-through panel slips with them (per EDR 4.2 element 6).")

    print()
    print("=" * 72)
    print("End of anchor extraction.")
    print("=" * 72)


if __name__ == "__main__":
    main()
