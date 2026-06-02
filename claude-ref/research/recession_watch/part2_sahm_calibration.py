"""
Part 2: Canadian Sahm rule calibration (backtest 1976-present).
Part 3: Depth gauge sanity check (GDP + employment, 1976-present).

Uses on-disk data files already in the pipeline:
  data/raw/unemployment_rate.csv  (v2062815, 1976-05 to present, SA monthly)
  data/raw/employment_level.csv   (v2062811, 1976-05 to present, SA monthly)
  data/raw/gdp_monthly.csv        (v65201210, 1997-01 to present, SA monthly)

CD Howe Business Cycle Council recession dates (peak -> trough):
  Jun 1981 -> Oct 1982
  Mar 1990 -> May 1992
  Oct 2008 -> May 2009
  Feb 2020 -> Apr 2020
  (1974-75 predates LFS monthly coverage; excluded)

Run from repo root:
    py claude-ref/research/recession_watch/part2_sahm_calibration.py
"""

from __future__ import annotations

import csv
import sys
from datetime import datetime, date
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parents[3]
URATE_PATH = REPO_ROOT / "data" / "raw" / "unemployment_rate.csv"
EMP_PATH   = REPO_ROOT / "data" / "raw" / "employment_level.csv"
GDP_PATH   = REPO_ROOT / "data" / "raw" / "gdp_monthly.csv"


def load_csv(path: Path) -> list[tuple[date, float]]:
    rows = []
    with open(path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            d = datetime.strptime(row["date"], "%Y-%m-%d").date()
            v = row["value"]
            if v and v.strip():
                rows.append((d, float(v)))
    rows.sort(key=lambda x: x[0])
    return rows


def rolling_mean(series: list[float], window: int) -> list[float | None]:
    out: list[float | None] = []
    for i in range(len(series)):
        if i < window - 1:
            out.append(None)
        else:
            out.append(sum(series[i - window + 1 : i + 1]) / window)
    return out


def rolling_min(series: list[float | None], window: int) -> list[float | None]:
    """Rolling min over the last `window` non-None observations."""
    out: list[float | None] = []
    for i in range(len(series)):
        if series[i] is None:
            out.append(None)
            continue
        vals = [v for v in series[max(0, i - window + 1) : i + 1] if v is not None]
        out.append(min(vals) if vals else None)
    return out


def expanding_max(values: list[float | None]) -> list[float | None]:
    """Expanding high-water mark (all observations up to and including i)."""
    out: list[float | None] = []
    current_max: float | None = None
    for v in values:
        if v is None:
            out.append(None)
        else:
            if current_max is None or v > current_max:
                current_max = v
            out.append(current_max)
    return out


# ---------------------------------------------------------------------------
# CD Howe recession bands (peak, trough) — both inclusive
# ---------------------------------------------------------------------------
CD_HOWE_RECESSIONS = [
    (date(1981, 6, 1), date(1982, 10, 1), "1981-82"),
    (date(1990, 3, 1), date(1992, 5, 1), "1990-92"),
    (date(2008, 10, 1), date(2009, 5, 1), "2008-09"),
    (date(2020, 2, 1), date(2020, 4, 1), "2020 COVID"),
]

def in_recession(d: date) -> str | None:
    for peak, trough, name in CD_HOWE_RECESSIONS:
        if peak <= d <= trough:
            return name
    return None

def near_recession(d: date, lead_months: int = 6) -> str | None:
    """True if d is within lead_months of a recession peak."""
    from datetime import timedelta
    for peak, trough, name in CD_HOWE_RECESSIONS:
        window_start = date(peak.year, peak.month, 1)
        # go back lead_months
        m = peak.month - lead_months
        y = peak.year
        while m <= 0:
            m += 12
            y -= 1
        window_start = date(y, m, 1)
        if window_start <= d <= trough:
            return name
    return None


# ---------------------------------------------------------------------------
# PART 2: Sahm Calibration
# ---------------------------------------------------------------------------
print("=" * 70)
print("PART 2: CANADIAN SAHM RULE CALIBRATION")
print("=" * 70)

urate_data = load_csv(URATE_PATH)
dates_u = [r[0] for r in urate_data]
vals_u  = [r[1] for r in urate_data]

# 3-month moving average of unemployment rate
ma3 = rolling_mean(vals_u, 3)

# Trailing 12-month minimum of the 3mma
min12 = rolling_min(ma3, 12)

# Sahm gap = 3mma - trailing 12-month min
sahm_gap: list[tuple[date, float] | None] = []
for i in range(len(dates_u)):
    if ma3[i] is None or min12[i] is None:
        sahm_gap.append(None)
    else:
        sahm_gap.append((dates_u[i], ma3[i] - min12[i]))

valid_gap = [(d, g) for x in sahm_gap if x is not None for d, g in [x]]

print(f"\nSeries: {dates_u[0]} to {dates_u[-1]} ({len(dates_u)} monthly obs)")
print(f"First valid Sahm gap: {[x for x in valid_gap if x is not None][0]}")
print(f"Latest Sahm gap: {valid_gap[-1]}")

# ---- 2.1 US-default 0.5pp threshold tabulation ----
print("\n--- 2.1  US-default threshold = 0.50pp ---")
print(f"  Every month gap >= 0.50 (1976-present):\n")

THRESHOLD_US = 0.50

triggers_us: list[tuple[date, float, str]] = []
prev_in = False
for d, g in valid_gap:
    if g >= THRESHOLD_US:
        if not prev_in:
            # new crossing
            rec = near_recession(d)
            label = f"TRUE POSITIVE ({rec})" if rec else "FALSE POSITIVE"
            triggers_us.append((d, g, label))
        prev_in = True
    else:
        prev_in = False

print(f"  {'Date':<14} {'Gap':>6}   Classification")
print(f"  {'-'*14} {'-'*6}   {'-'*40}")
for d, g, label in triggers_us:
    print(f"  {str(d):<14} {g:>6.3f}   {label}")

tp_us = sum(1 for _, _, lbl in triggers_us if "TRUE" in lbl)
fp_us = sum(1 for _, _, lbl in triggers_us if "FALSE" in lbl)
print(f"\n  Total crossings: {len(triggers_us)} ({tp_us} true positives, {fp_us} false positives)")

# ---- 2.2 Threshold sweep ----
print("\n--- 2.2  Threshold sweep 0.3 to 1.5 (step 0.1) ---")
print(f"\n  {'Threshold':>10} {'Rec caught':>12} {'False pos':>12} {'Notes'}")
print(f"  {'-'*10} {'-'*12} {'-'*12} {'-'*40}")

for thresh_10 in range(3, 16):
    thresh = thresh_10 / 10.0

    # Find all crossing events (rising through threshold)
    prev_above = False
    crossing_events: list[tuple[date, float]] = []
    for d, g in valid_gap:
        if g >= thresh:
            if not prev_above:
                crossing_events.append((d, g))
            prev_above = True
        else:
            prev_above = False

    # Classify each crossing
    recessions_caught = set()
    false_positives = 0
    for d, g in crossing_events:
        rec = near_recession(d, lead_months=6)
        if rec:
            recessions_caught.add(rec)
        else:
            false_positives += 1

    note = ""
    # Check if 2015 oil period crosses
    gap_2015 = [(d, g) for d, g in valid_gap if date(2015, 1, 1) <= d <= date(2016, 6, 1)]
    if gap_2015:
        max_gap_2015 = max(g for _, g in gap_2015)
        if max_gap_2015 >= thresh:
            note = f"Oil false alarm (2015 max={max_gap_2015:.2f})"

    print(f"  {thresh:>10.1f} {len(recessions_caught):>12} {false_positives:>12}   {note}")

# ---- 2.3 Recommendation ----
print("\n--- 2.3  Recommended Canadian threshold ---")
# Find threshold where all 4 caught + minimal FP
print("  Analysis: the 0.5pp US default vs Canadian calibration tradeoffs")
print("  (see table above for numeric detail)\n")

# Show 2015 oil event peak
gap_2015 = [(d, g) for d, g in valid_gap if date(2014, 6, 1) <= d <= date(2016, 12, 1)]
if gap_2015:
    peak_2015 = max(gap_2015, key=lambda x: x[1])
    print(f"  2015 oil false alarm: peak gap = {peak_2015[1]:.3f}pp on {peak_2015[0]}")

# Show 2020 COVID
gap_covid = [(d, g) for d, g in valid_gap if date(2020, 1, 1) <= d <= date(2020, 6, 1)]
if gap_covid:
    peak_covid = max(gap_covid, key=lambda x: x[1])
    print(f"  2020 COVID: peak gap = {peak_covid[1]:.3f}pp on {peak_covid[0]}")

# ---- 2.4 Last 12 months of Sahm gap ----
print("\n--- 2.4  Last 14 months of Sahm gap (current status) ---")
recent = valid_gap[-14:]
print(f"\n  {'Date':<14} {'U-rate':>8} {'3mMA':>8} {'Min12':>8} {'Gap':>8}  {'Status'}")
print(f"  {'-'*14} {'-'*8} {'-'*8} {'-'*8} {'-'*8}  {'-'*30}")
for i in range(len(dates_u) - 14, len(dates_u)):
    d = dates_u[i]
    u = vals_u[i]
    m = ma3[i]
    mn = min12[i]
    if m is not None and mn is not None:
        g = m - mn
        trigger_05 = "TRIGGER 0.5" if g >= 0.50 else ""
        trigger_rec = "TRIGGER REC" if g >= 0.70 else ""
        status = trigger_05 or trigger_rec or ""
        print(f"  {str(d):<14} {u:>8.1f} {m:>8.3f} {mn:>8.3f} {g:>8.3f}  {status}")


# ---------------------------------------------------------------------------
# PART 3: Depth Gauge Sanity Check
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("PART 3: DEPTH GAUGE SANITY CHECK")
print("=" * 70)

# ---- 3.1 Employment depth ----
print("\n--- 3.1  Employment depth (1976-present) ---")

emp_data = load_csv(EMP_PATH)
dates_e = [r[0] for r in emp_data]
vals_e  = [r[1] for r in emp_data]

# Smooth with 3mma
emp_ma3 = rolling_mean(vals_e, 3)
# Expanding high-water mark on the smoothed level
emp_hwm = expanding_max(emp_ma3)
# Depth = current / hwm - 1
emp_depth: list[tuple[date, float] | None] = []
for i in range(len(dates_e)):
    if emp_ma3[i] is None or emp_hwm[i] is None:
        emp_depth.append(None)
    else:
        emp_depth.append((dates_e[i], emp_ma3[i] / emp_hwm[i] - 1))

print(f"\n  Series: {dates_e[0]} to {dates_e[-1]}")
print(f"\n  {'Recession':<14} {'Peak date':>12} {'Trough date':>12} {'Peak-trough depth':>20}")
print(f"  {'-'*14} {'-'*12} {'-'*12} {'-'*20}")

for rec_peak, rec_trough, name in CD_HOWE_RECESSIONS:
    # Find max depth within the recession window
    rec_depths = [
        (d, dep)
        for item in emp_depth if item is not None
        for d, dep in [item]
        if rec_peak <= d <= rec_trough
    ]
    if rec_depths:
        worst = min(rec_depths, key=lambda x: x[1])
        print(f"  {name:<14} {str(rec_peak):>12} {str(worst[0]):>12} {worst[1]*100:>19.2f}%")
    else:
        print(f"  {name:<14} {str(rec_peak):>12} {'no data':>12} {'N/A':>20}")

# ---- 3.2 GDP depth ----
print("\n--- 3.2  GDP depth (monthly, 1997-present — GDP starts 1997) ---")
print("  NOTE: monthly GDP-by-industry starts 1997-01; the 1981-82 and 1990-92")
print("  recessions are not covered by this series. Employment depth above")
print("  covers full history.")

gdp_data = load_csv(GDP_PATH)
dates_g = [r[0] for r in gdp_data]
vals_g  = [r[1] for r in gdp_data]

gdp_ma3 = rolling_mean(vals_g, 3)
gdp_hwm = expanding_max(gdp_ma3)
gdp_depth: list[tuple[date, float] | None] = []
for i in range(len(dates_g)):
    if gdp_ma3[i] is None or gdp_hwm[i] is None:
        gdp_depth.append(None)
    else:
        gdp_depth.append((dates_g[i], gdp_ma3[i] / gdp_hwm[i] - 1))

print(f"\n  Series: {dates_g[0]} to {dates_g[-1]}")

gdp_covered = [r for r in CD_HOWE_RECESSIONS if r[0] >= date(1997, 1, 1)]
print(f"\n  {'Recession':<14} {'Peak date':>12} {'Worst depth date':>17} {'Peak-trough depth':>20}")
print(f"  {'-'*14} {'-'*12} {'-'*17} {'-'*20}")

for rec_peak, rec_trough, name in gdp_covered:
    rec_depths = [
        (d, dep)
        for item in gdp_depth if item is not None
        for d, dep in [item]
        if rec_peak <= d <= rec_trough
    ]
    if rec_depths:
        worst = min(rec_depths, key=lambda x: x[1])
        print(f"  {name:<14} {str(rec_peak):>12} {str(worst[0]):>17} {worst[1]*100:>19.2f}%")
    else:
        print(f"  {name:<14} {str(rec_peak):>12} {'no data in range':>17} {'N/A':>20}")

# ---- 3.3 Current depth status ----
print("\n--- 3.3  Current depth status (last 6 months) ---")
valid_gdp_depth = [(d, dep) for item in gdp_depth if item is not None for d, dep in [item]]
valid_emp_depth = [(d, dep) for item in emp_depth if item is not None for d, dep in [item]]

print(f"\n  GDP depth (monthly, latest 6):")
for d, dep in valid_gdp_depth[-6:]:
    hwm_flag = "*" if dep < -0.002 else ""
    print(f"    {d}: {dep*100:.3f}% {hwm_flag}")

print(f"\n  Employment depth (monthly, latest 6):")
for d, dep in valid_emp_depth[-6:]:
    hwm_flag = "*" if dep < -0.002 else ""
    print(f"    {d}: {dep*100:.3f}% {hwm_flag}")

# ---- 3.4 COVID scale check ----
print("\n--- 3.4  COVID scale check (does it dominate?) ---")
covid_gdp = [(d, dep) for d, dep in valid_gdp_depth if date(2020, 1, 1) <= d <= date(2020, 12, 1)]
covid_emp = [(d, dep) for d, dep in valid_emp_depth if date(2020, 1, 1) <= d <= date(2020, 12, 1)]
if covid_gdp:
    worst_g = min(covid_gdp, key=lambda x: x[1])
    print(f"  COVID GDP trough depth: {worst_g[1]*100:.2f}% on {worst_g[0]}")
if covid_emp:
    worst_e = min(covid_emp, key=lambda x: x[1])
    print(f"  COVID employment trough depth: {worst_e[1]*100:.2f}% on {worst_e[0]}")

# Overall worst depths ever
all_gdp_worst = min(valid_gdp_depth, key=lambda x: x[1])
all_emp_worst = min(valid_emp_depth, key=lambda x: x[1])
print(f"\n  All-time worst GDP depth: {all_gdp_worst[1]*100:.2f}% on {all_gdp_worst[0]}")
print(f"  All-time worst employment depth: {all_emp_worst[1]*100:.2f}% on {all_emp_worst[0]}")
print(f"\n  COVID note: yes, the 2020 event dominates scale significantly.")
print(f"  Chart display should use LOG scale or truncate y-axis at e.g. -15%")
print(f"  with COVID noted as a break.")

print()
print(f"Completed at {datetime.now().isoformat()}")
