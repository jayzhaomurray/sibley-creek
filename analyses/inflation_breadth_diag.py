"""Diagnostic breakdown of breadth shares for sanity check.

Shows which components fall above 3%, in 1-3%, and below 1% in the
latest reference month, with their basket weight contribution.
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

BOC = Path(r"C:\Users\jayzh\Documents\boc-tracker\data")


def main() -> None:
    mapping = json.loads((BOC / "cpi_breadth_mapping.json").read_text())
    comp = pd.read_csv(BOC / "cpi_components.csv", parse_dates=["date"]).set_index("date")
    yoy = comp.pct_change(12) * 100
    last = yoy.iloc[-1].dropna()
    ref = yoy.index[-1].date()

    wt_lookup = {m["name"]: m["wt_value"] for m in mapping}
    rows = []
    for name, val in last.items():
        w = wt_lookup.get(name)
        if w is None:
            continue
        rows.append({"component": name, "yoy": val, "weight": w})
    df = pd.DataFrame(rows).sort_values("yoy", ascending=False).reset_index(drop=True)

    print(f"Reference month: {ref}")
    print(f"Total weight covered: {df['weight'].sum():.2f}")
    print()
    print("ABOVE 3% Y/Y (sorted):")
    above = df[df["yoy"] > 3.0]
    print(above.to_string(index=False, formatters={"yoy": "{:6.2f}".format, "weight": "{:5.2f}".format}))
    print(f"\n  Above-3 weight sum: {above['weight'].sum():.2f}")

    print()
    print("BELOW 1% Y/Y (sorted, ascending shown):")
    below = df[df["yoy"] < 1.0].sort_values("yoy")
    print(below.to_string(index=False, formatters={"yoy": "{:6.2f}".format, "weight": "{:5.2f}".format}))
    print(f"\n  Below-1 weight sum: {below['weight'].sum():.2f}")

    print()
    print("IN 1-3% Y/Y (sorted):")
    inb = df[(df["yoy"] >= 1.0) & (df["yoy"] <= 3.0)]
    print(inb.to_string(index=False, formatters={"yoy": "{:6.2f}".format, "weight": "{:5.2f}".format}))
    print(f"\n  In-band weight sum: {inb['weight'].sum():.2f}")


if __name__ == "__main__":
    main()
