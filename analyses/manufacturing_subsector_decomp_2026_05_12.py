"""Manufacturing subsector decomposition, 2019 -> 2026.

Pulls StatCan Table 36-10-0434-01 (monthly GDP by industry, chained 2017,
seasonally adjusted at annual rates) at the 3-digit NAICS subsector level
for all 18 manufacturing subsectors that StatCan reports under this table.

For each subsector, computes:
    - Indexed level (Dec 2019 = 100) at the latest available month.
    - Y/Y % change at the latest month.
    - Trough indexed value since Dec 2019, with date.
    - Contribution to the aggregate manufacturing slump:
        weight (subsector's Dec-2019 share of total manufacturing GDP)
        x  pct change from Dec 2019 to latest month.
    The sum of contributions reconstructs the aggregate level change.

Outputs:
    - data/derived/manufacturing_subsector_decomp.csv (the table)
    - prints a Markdown-style ranking to stdout for inclusion in the report.

This is an internal analysis script, run on demand.
"""

from __future__ import annotations

import json
from pathlib import Path

import httpx
import pandas as pd

# Geography=Canada(1), SA=annual rates(1), Prices=Chained 2017(1), NAICS=member
SUBSECTORS = [
    (55,  "Food manufacturing",                                       65201313),
    (65,  "Beverage and tobacco product manufacturing",               65201322),
    (70,  "Textile, clothing and leather product manufacturing",      65201330),
    (73,  "Wood product manufacturing",                               65201336),
    (77,  "Paper manufacturing",                                      65201341),
    (80,  "Printing and related support activities",                  65201351),
    (81,  "Petroleum and coal product manufacturing",                 65201355),
    (84,  "Chemical manufacturing",                                   65201264),
    (92,  "Plastics and rubber products manufacturing",               65201274),
    (95,  "Non-metallic mineral product manufacturing",               65201279),
    (98,  "Primary metal manufacturing",                              65201282),
    (104, "Fabricated metal product manufacturing",                   65201286),
    (113, "Machinery manufacturing",                                  65201289),
    (121, "Computer and electronic product manufacturing",            65201290),
    (127, "Electrical equipment, appliance and component manufacturing", 65201293),
    (132, "Transportation equipment manufacturing",                   65201301),
    (142, "Furniture and related product manufacturing",              65201304),
    (146, "Miscellaneous manufacturing",                              65201307),
]

# Aggregate manufacturing vector (NAICS 54), used for sanity-check reconstruction.
MANUFACTURING_VECTOR = 65201263

WDS_ENDPOINT = "https://www150.statcan.gc.ca/t1/wds/rest/getDataFromVectorsAndLatestNPeriods"


def fetch(vector_ids: list[int], latest_n: int = 100) -> dict[int, pd.Series]:
    body = [{"vectorId": v, "latestN": latest_n} for v in vector_ids]
    with httpx.Client(timeout=120) as c:
        r = c.post(WDS_ENDPOINT, json=body)
    r.raise_for_status()
    out: dict[int, pd.Series] = {}
    for item in r.json():
        if item["status"] != "SUCCESS":
            raise RuntimeError(f"WDS error: {item}")
        obj = item["object"]
        vid = obj["vectorId"]
        pts = obj["vectorDataPoint"]
        s = pd.Series(
            {pd.Timestamp(p["refPer"]): p["value"] for p in pts},
            name=vid,
        ).sort_index()
        out[vid] = s
    return out


def main() -> None:
    vids = [v for _, _, v in SUBSECTORS] + [MANUFACTURING_VECTOR]
    data = fetch(vids, latest_n=120)  # ~10 years

    # Build a wide frame: rows=date, columns=subsector label.
    rows = {label: data[v] for _, label, v in SUBSECTORS}
    df = pd.DataFrame(rows)
    df_total = data[MANUFACTURING_VECTOR].rename("Total manufacturing")
    df = df.join(df_total)

    # Use Dec 2019 as the pre-COVID baseline.
    baseline = pd.Timestamp("2019-12-01")
    latest = df.index.max()
    print(f"Baseline: {baseline.date()}   Latest: {latest.date()}")

    base_row = df.loc[baseline]
    latest_row = df.loc[latest]

    # Indexed level (Dec 2019 = 100).
    idx_latest = (latest_row / base_row) * 100.0

    # Y/Y change at latest month vs same month one year earlier.
    yoy_date = latest - pd.DateOffset(years=1)
    yoy_date_actual = df.index[df.index.get_indexer([yoy_date], method="nearest")][0]
    yoy = (latest_row / df.loc[yoy_date_actual] - 1.0) * 100.0

    # Trough since Dec 2019 (excluding Dec 2019 itself? include).
    post = df.loc[baseline:]
    trough_val = post.min()
    trough_date = post.idxmin()
    trough_idx = (trough_val / base_row) * 100.0

    # Contribution to aggregate manufacturing change, Dec 2019 -> latest.
    # In chained dollars, the aggregate is *approximately* additive of components
    # at the contemporaneous reference period; we report the weighted contribution
    # in percentage-points of the Dec-2019 manufacturing total.
    subsector_labels = [label for _, label, _ in SUBSECTORS]
    mfg_base = base_row["Total manufacturing"]
    delta = latest_row[subsector_labels] - base_row[subsector_labels]
    contrib_pp = (delta / mfg_base) * 100.0   # contribution in pp of total

    out = pd.DataFrame({
        "subsector": subsector_labels,
        "level_dec2019_trillions_c2017": base_row[subsector_labels].values,
        "level_latest_trillions_c2017": latest_row[subsector_labels].values,
        "indexed_dec2019_100_latest": idx_latest[subsector_labels].values,
        "yoy_pct_latest": yoy[subsector_labels].values,
        "trough_indexed": trough_idx[subsector_labels].values,
        "trough_date": [trough_date[s].date().isoformat() for s in subsector_labels],
        "contribution_pp_to_mfg_chg": contrib_pp.values,
        "weight_dec2019_pct": (base_row[subsector_labels] / mfg_base * 100.0).values,
    })
    out = out.sort_values("contribution_pp_to_mfg_chg")

    out_dir = Path(__file__).resolve().parents[1] / "data" / "derived"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "manufacturing_subsector_decomp.csv"
    out.to_csv(out_path, index=False)
    print(f"\nWrote {out_path}")

    print("\nRanked by contribution to manufacturing change (most negative first):")
    print(out.to_string(index=False))

    total_mfg_idx = (latest_row["Total manufacturing"] / mfg_base) * 100.0
    print(f"\nTotal manufacturing indexed (Dec 2019 = 100), {latest.date()}: {total_mfg_idx:.1f}")
    print(f"Sum of subsector contributions (pp of Dec-2019 mfg): {out['contribution_pp_to_mfg_chg'].sum():.2f}")

    # Persist provenance.
    meta = {
        "source_table": "36-10-0434-01",
        "source_url": "https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=3610043401",
        "vectors": {label: v for _, label, v in SUBSECTORS} | {"Total manufacturing": MANUFACTURING_VECTOR},
        "baseline": baseline.date().isoformat(),
        "latest": latest.date().isoformat(),
        "units": "chained 2017 Canadian dollars, trillions, SAAR",
        "computed_at": pd.Timestamp.utcnow().isoformat(),
    }
    (out_dir / "manufacturing_subsector_decomp.meta.json").write_text(
        json.dumps(meta, indent=2), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
