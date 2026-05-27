"""
USDCAD percentile vs. post-1990 distribution -- one-shot derivation.

Date: 2026-05-11
Author: researcher
Purpose: resolve flag 5 / flag 7 from W3 homepage-tile-line resolutions.

Inputs:
  C:/Users/jayzh/Documents/boc-tracker/data/usdcad.csv
    -- daily USDCAD series 1990-01-02 through 2026-05-01 (last business day
       on or before today, 2026-05-11). Source: BoC Valet FXUSDCAD (current
       methodology, 2017+) stitched onto BoC legacy noon rate IEXE0101
       (1990-2017), as curated in the boc-tracker pipeline.

Outputs (printed to stdout):
  - Latest observed value with date.
  - Empirical percentile rank of the latest value across all daily
    observations from 1990-01-02 onward.
  - Quantile reference points (5/10/25/50/75/80/90/95) of the post-1990
    distribution for context.
  - 90-day trailing direction stat: change in spot from t-90 calendar days
    to latest, and from rolling-window max to latest.

Caveats:
  - Methodology break April 2017: BoC retired noon rate in favour of the
    daily-average FX rate. The two are not identical but for a percentile-
    distribution context the methodology gap is small relative to the
    range of historical variation.
  - The post-1990 distribution mixes regimes: free-float CAD, two oil-shock
    booms (2008, 2014), and the post-COVID period. The percentile is a
    summary stat, not a regime-conditioned read.
"""

import csv
from datetime import date, timedelta

CSV_PATH = r"C:\Users\jayzh\Documents\boc-tracker\data\usdcad.csv"


def load_series(path):
    series = []
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            d = row["date"]
            v = row["value"]
            if not v:
                continue
            series.append((d, float(v)))
    return series


def percentile_rank(sorted_values, x):
    # Empirical CDF percentile rank: fraction of observations <= x.
    n = len(sorted_values)
    # Binary search for the rightmost insertion point.
    lo, hi = 0, n
    while lo < hi:
        mid = (lo + hi) // 2
        if sorted_values[mid] <= x:
            lo = mid + 1
        else:
            hi = mid
    return 100.0 * lo / n


def quantile(sorted_values, q):
    n = len(sorted_values)
    idx = q * (n - 1)
    lo = int(idx)
    hi = min(lo + 1, n - 1)
    frac = idx - lo
    return sorted_values[lo] * (1 - frac) + sorted_values[hi] * frac


def main():
    series = load_series(CSV_PATH)
    print(f"Total observations: {len(series)}")
    print(f"First: {series[0]}")
    print(f"Last : {series[-1]}")
    print()

    values = [v for (_, v) in series]
    sorted_v = sorted(values)

    latest_date, latest_v = series[-1]
    pct = percentile_rank(sorted_v, latest_v)
    print(
        f"Latest value {latest_v:.4f} on {latest_date} sits at the {pct:.1f}th "
        f"percentile of the post-1990 daily distribution (N={len(values)})."
    )
    print()

    print("Quantile reference (post-1990 daily distribution):")
    for q in (0.05, 0.10, 0.25, 0.50, 0.75, 0.80, 0.90, 0.95):
        print(f"  q={q:.2f}: {quantile(sorted_v, q):.4f}")
    print()

    # Direction read: latest vs ~90 calendar days ago.
    last_date_str, last_v = series[-1]
    last_date_obj = date.fromisoformat(last_date_str)
    target = last_date_obj - timedelta(days=90)
    # Find the closest series date >= target.
    ref_idx = 0
    for i, (d, _) in enumerate(series):
        if date.fromisoformat(d) >= target:
            ref_idx = i
            break
    ref_date, ref_v = series[ref_idx]
    print(
        f"90-day window: from {ref_date} ({ref_v:.4f}) to {last_date_str} "
        f"({last_v:.4f}). Change: {last_v - ref_v:+.4f} "
        f"({100*(last_v-ref_v)/ref_v:+.2f}%)."
    )

    # Max and min over the 90-day window.
    window = [(d, v) for (d, v) in series if date.fromisoformat(d) >= target]
    win_max_date, win_max_v = max(window, key=lambda x: x[1])
    win_min_date, win_min_v = min(window, key=lambda x: x[1])
    print(
        f"90-day max: {win_max_v:.4f} on {win_max_date}; "
        f"min: {win_min_v:.4f} on {win_min_date}."
    )
    print(
        f"Latest vs 90-day max: {last_v - win_max_v:+.4f} "
        f"({100*(last_v-win_max_v)/win_max_v:+.2f}%)."
    )

    # Spring window (March-May 2026) direction check.
    spring_window = [
        (d, v) for (d, v) in series if "2026-03-01" <= d <= "2026-05-01"
    ]
    if spring_window:
        spring_open_d, spring_open_v = spring_window[0]
        spring_close_d, spring_close_v = spring_window[-1]
        spring_max_d, spring_max_v = max(spring_window, key=lambda x: x[1])
        spring_min_d, spring_min_v = min(spring_window, key=lambda x: x[1])
        print()
        print(
            f"Spring 2026 window (Mar 1 - May 1): "
            f"open {spring_open_v:.4f} on {spring_open_d}, "
            f"close {spring_close_v:.4f} on {spring_close_d}."
        )
        print(
            f"  Spring high {spring_max_v:.4f} ({spring_max_d}); "
            f"spring low {spring_min_v:.4f} ({spring_min_d})."
        )
        print(
            f"  Net spring change: {spring_close_v - spring_open_v:+.4f} "
            f"({100*(spring_close_v-spring_open_v)/spring_open_v:+.2f}%). "
            f"(Negative = CAD strengthened.)"
        )


if __name__ == "__main__":
    main()
