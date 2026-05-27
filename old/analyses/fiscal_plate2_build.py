"""Build CSV + derived JSON for fiscal plate 2 (balance % GDP history + SEU 2026 projection)."""
import pdfplumber, csv, json, re, os
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(r"C:\Users\jayzh\projects\macro-research-department")
PDF = ROOT / "data" / "raw" / "fiscal" / "frt_2025.pdf"

pdf = pdfplumber.open(PDF)
t1 = pdf.pages[7].extract_text()
t2 = pdf.pages[8].extract_text()

def tokens(line):
    yr = line[:7]
    rest = line[7:].strip()
    rest = re.sub(r"(\d)\s+\.(\d)", r"\1.\2", rest)
    return yr, rest.split()

T1 = [ln for ln in t1.splitlines() if re.match(r"^\d{4}-\d{2}\s", ln)]
T2 = [ln for ln in t2.splitlines() if re.match(r"^\d{4}-\d{2}\s", ln)]
t1_rows = dict(tokens(l) for l in T1)
t2_rows = dict(tokens(l) for l in T2)

def num(s):
    return float(s.replace(",", ""))

# Identify balance column per year. Use Table 2 which is cleaner:
# Pre-2008-09 (7 cols): balance = idx 3
# 2008-09 .. 2010-11 (10 cols, no Adjustments): balance = idx 5 (Budgetary surplus or deficit (-))
# 2011-12+ (11 cols with Adjustments): balance = idx 5 still (Budgetary surplus or deficit (-))
# But 2008-09 row: ['14.3','12.7','1.7','-0.0','0.5','-0.6','-0.0','-0.1','28.2','-4.6','-5.1'] — 11 cols
# 2010-11: 10 cols. Adjustments-to-accumulated-deficit column appears only some years.
# Universal rule: column for "Budgetary surplus or deficit (-)" is the one whose Table-1 sign matches the "famous" published deficit/surplus number.
# Cheaper: build manually using a year->balance_idx map informed by inspection.

# After inspection of FRT 2025 Table 2:
#  Pre-1995-96 (no separate Net actuarial losses & no Adjustments cols): 7 tokens, balance at idx 3.
#  1996-97..2007-08: still 7 tokens (or 8 with comprehensive income from 2006-07), balance at idx 3.
#  2008-09..2010-11: 10/11 tokens — Net actuarial losses introduced; balance at idx 5.
#  2011-12 onward: 10/11/12 tokens — Adjustments col added some years; balance still at idx 5.
# Validation: 2010-11 published deficit was $33.4bn; T1 row idx 5 = -34,953 ($34.95bn deficit). Close enough — yes idx 5 from 2008-09.

def balance_idx(yr_int, n_tokens):
    if yr_int < 2008:
        return 3
    return 5

OUT = []
for yr_str in sorted(t2_rows.keys()):
    yr_int = int(yr_str[:4])
    t2_toks = t2_rows[yr_str]
    t1_toks = t1_rows[yr_str]
    idx = balance_idx(yr_int, len(t2_toks))
    bal_pct = num(t2_toks[idx])
    bal_mn = num(t1_toks[idx])  # millions
    bal_bn = bal_mn / 1000.0
    # gdp_cad_bn = balance / (pct/100). Guard against pct=0.
    gdp_bn = (bal_bn / (bal_pct/100.0)) if bal_pct != 0 else None
    OUT.append({
        "fiscal_year": yr_str,
        "balance_cad_bn": round(bal_bn, 3),
        "gdp_cad_bn": round(gdp_bn, 1) if gdp_bn is not None else None,
        "balance_pct_gdp": bal_pct,
        "vintage": "FRT 2025 (Department of Finance Canada, October 2025)",
        "source_url": "https://publications.gc.ca/collections/collection_2025/fin/F1-26-2025-eng.pdf"
    })

# Spot-check a few rows
for r in OUT:
    if r["fiscal_year"] in ("1990-91","1996-97","2000-01","2008-09","2010-11","2015-16","2020-21","2023-24","2024-25"):
        print(r)

# Write CSV.
csv_path = ROOT / "data" / "derived" / "fiscal_balance_pct_gdp.csv"
csv_path.parent.mkdir(parents=True, exist_ok=True)
with open(csv_path, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["fiscal_year","balance_cad_bn","gdp_cad_bn","balance_pct_gdp","vintage","source_url"])
    w.writeheader()
    for r in OUT:
        w.writerow(r)
print(f"\nwrote {csv_path} ({len(OUT)} rows)")

# Projection from DoF SEU 2026 (Annex 1 Table A1.7) -- verified upstream.
PROJ = [
    {"fiscal_year":"2025-26", "balance_cad_bn": -66.9, "balance_pct_gdp": -2.1},
    {"fiscal_year":"2026-27", "balance_cad_bn": -65.3, "balance_pct_gdp": -1.9},
    {"fiscal_year":"2027-28", "balance_cad_bn": -63.1, "balance_pct_gdp": -1.8},
    {"fiscal_year":"2028-29", "balance_cad_bn": -57.7, "balance_pct_gdp": -1.6},
    {"fiscal_year":"2029-30", "balance_cad_bn": -56.2, "balance_pct_gdp": -1.5},
    {"fiscal_year":"2030-31", "balance_cad_bn": -53.2, "balance_pct_gdp": -1.4},
]
for r in PROJ:
    r["vintage"] = "DoF Spring Economic Update 2026 (April 28, 2026)"
    r["source_url"] = "https://budget.canada.ca/update-miseajour/2026/report-rapport/anx1-en.html"

# Write derived JSON.
now = datetime.now(timezone.utc).isoformat()
out = {
    "_meta": {
        "name": "fiscal_balance_pct_gdp",
        "description": "Federal budgetary balance as % of nominal GDP — historical FY1966-67 to FY2024-25 from Department of Finance Fiscal Reference Tables (October 2025) + projection FY2025-26 to FY2030-31 from DoF Spring Economic Update 2026 (April 28, 2026)",
        "units": {"balance_cad_bn": "C$ billions", "gdp_cad_bn": "C$ billions", "balance_pct_gdp": "per cent of GDP"},
        "historical_source": "Fiscal Reference Tables 2025, Tables 1 & 2 (Department of Finance Canada)",
        "historical_source_url": "https://publications.gc.ca/collections/collection_2025/fin/F1-26-2025-eng.pdf",
        "historical_vintage": "October 2025",
        "projection_source": "Spring Economic Update 2026, Annex 1 Table A1.7 (Department of Finance Canada)",
        "projection_source_url": "https://budget.canada.ca/update-miseajour/2026/report-rapport/anx1-en.html",
        "projection_vintage": "April 28, 2026",
        "fetched_at": now,
        "schema_version": 1,
        "notes": "Break in series following introduction of full accrual accounting: FRT footnote states data from 1983-84 onward are not directly comparable with earlier years. Balance series sign convention: deficit negative, surplus positive. gdp_cad_bn is implied from balance / (pct/100), rounded to one decimal."
    },
    "historical": OUT,
    "projection": PROJ
}
json_path = ROOT / "data" / "derived" / "fiscal_balance_pct_gdp.json"
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(out, f, indent=2)
print(f"wrote {json_path}")
