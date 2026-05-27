"""
Addendum: compute percentile for the May 8, 2026 BoC Valet close (1.3686).
boc-tracker mirror ends 2026-05-01 (1.3575). The Valet FXUSDCAD series shows
2026-05-08 = 1.3686. Latest available business-day close is May 8, 2026
(May 9 is a Saturday; no print).
"""

import csv

CSV_PATH = r"C:\Users\jayzh\Documents\boc-tracker\data\usdcad.csv"

with open(CSV_PATH, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    values = [float(row["value"]) for row in reader if row["value"]]

sorted_v = sorted(values)
n = len(sorted_v)

def pct_rank(sorted_values, x):
    lo, hi = 0, len(sorted_values)
    while lo < hi:
        mid = (lo + hi) // 2
        if sorted_values[mid] <= x:
            lo = mid + 1
        else:
            hi = mid
    return 100.0 * lo / len(sorted_values)

# Check several candidate "latest" values that have been discussed.
for v in [1.3575, 1.3611, 1.3617, 1.3625, 1.3635, 1.3686, 1.378]:
    print(f"  Value {v:.4f}: percentile rank = {pct_rank(sorted_v, v):.1f}")
