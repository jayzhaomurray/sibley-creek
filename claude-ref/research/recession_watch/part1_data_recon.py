"""
Part 1: Data availability recon for Recession Watch.

Probes StatCan WDS to count 3-digit NAICS industries available in
Table 36-10-0434-01 (monthly GDP by industry) and to count LFS
employment-by-industry sectors available in Table 14-10-0355-01.

Run from repo root:
    py claude-ref/research/recession_watch/part1_data_recon.py
"""

from __future__ import annotations

import json
import sys
import urllib.request
import urllib.error
from datetime import datetime

WDS_BASE = "https://www150.statcan.gc.ca/t1/wds/rest"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def wds_post(endpoint: str, body: list) -> dict:
    url = f"{WDS_BASE}/{endpoint}"
    data = json.dumps(body).encode()
    req = urllib.request.Request(
        url, data=data,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        print(f"  HTTP {e.code} on {url}", file=sys.stderr)
        return {}


def wds_get(path: str) -> dict:
    url = f"{WDS_BASE}/{path}"
    req = urllib.request.Request(
        url, headers={"Accept": "application/json"}, method="GET"
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        print(f"  HTTP {e.code} on {url}", file=sys.stderr)
        return {}


# ---------------------------------------------------------------------------
# 1. GDP by industry (Table 36-10-0434-01) — count industry dimensions
# ---------------------------------------------------------------------------
print("=" * 70)
print("PART 1a: GDP by industry Table 36-10-0434-01 — industry hierarchy")
print("=" * 70)

gdp_meta = wds_get("getCubeMetadata/36100434")
if not gdp_meta:
    print("  ERROR: could not retrieve cube metadata for 36-10-0434-01")
else:
    dims = gdp_meta.get("object", {}).get("dimension", [])
    print(f"  Dimensions returned: {len(dims)}")
    for d in dims:
        dim_id = d.get("dimensionPositionId")
        dim_name = d.get("dimensionNameEn", "")
        members = d.get("member", [])
        print(f"  Dim {dim_id}: '{dim_name}' — {len(members)} members")
        if "NAICS" in dim_name or "industr" in dim_name.lower() or "Industr" in dim_name:
            # Show first 5 and last 5 members to understand the structure
            print(f"    First 10 members:")
            for m in members[:10]:
                print(f"      {m.get('memberId')}: {m.get('memberNameEn', '')}")
            if len(members) > 10:
                print(f"    ... ({len(members) - 10} more)")
                print(f"    Last 5 members:")
                for m in members[-5:]:
                    print(f"      {m.get('memberId')}: {m.get('memberNameEn', '')}")

# ---------------------------------------------------------------------------
# 2. LFS employment by industry (Table 14-10-0355-01) — sector count
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("PART 1b: LFS employment by industry Table 14-10-0355-01")
print("=" * 70)

lfs_ind_meta = wds_get("getCubeMetadata/14100355")
if not lfs_ind_meta:
    print("  ERROR: could not retrieve cube metadata for 14-10-0355-01")
    # Try alternate table 14-10-0023-01 (seasonally adjusted by NAICS)
    print("  Trying alternate: 14-10-0023-01")
    lfs_ind_meta = wds_get("getCubeMetadata/14100023")

if lfs_ind_meta:
    dims = lfs_ind_meta.get("object", {}).get("dimension", [])
    cube_title = lfs_ind_meta.get("object", {}).get("cubeTitleEn", "")
    print(f"  Cube title: {cube_title}")
    for d in dims:
        dim_id = d.get("dimensionPositionId")
        dim_name = d.get("dimensionNameEn", "")
        members = d.get("member", [])
        print(f"  Dim {dim_id}: '{dim_name}' — {len(members)} members")
        if "industr" in dim_name.lower() or "NAICS" in dim_name or "sector" in dim_name.lower():
            print(f"    All industry members:")
            for m in members:
                print(f"      {m.get('memberId')}: {m.get('memberNameEn', '')}")

# Also check 14-10-0022-01 which is the standard LFS by industry (not seasonally adjusted)
print()
print("  Checking 14-10-0022-01 (LFS employment by industry NSA):")
lfs_nsa = wds_get("getCubeMetadata/14100022")
if lfs_nsa:
    cube_title = lfs_nsa.get("object", {}).get("cubeTitleEn", "")
    print(f"  Cube title: {cube_title}")
    dims = lfs_nsa.get("object", {}).get("dimension", [])
    for d in dims:
        dim_id = d.get("dimensionPositionId")
        dim_name = d.get("dimensionNameEn", "")
        members = d.get("member", [])
        print(f"  Dim {dim_id}: '{dim_name}' — {len(members)} members")
        if "industr" in dim_name.lower() or "sector" in dim_name.lower():
            for m in members:
                print(f"      {m.get('memberId')}: {m.get('memberNameEn', '')}")

# ---------------------------------------------------------------------------
# 3. Verify aggregate_hours (already in pipeline — just confirm vector)
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("PART 1c: Aggregate hours worked (Table 14-10-0289-01, v4391505)")
print("=" * 70)
resp = wds_post("getDataFromVectorsAndLatestNPeriods", [{"vectorId": 4391505, "latestN": 5}])
if isinstance(resp, list) and resp:
    obj = resp[0]
    status = obj.get("status")
    pts = obj.get("object", {}).get("vectorDataPoint", [])
    print(f"  Status: {status}, latest 5 points: {[(p.get('refPer'), p.get('value')) for p in pts]}")
else:
    print("  ERROR fetching v4391505")

# ---------------------------------------------------------------------------
# 4. GDP industry sub-detail probe — how many series are SA monthly in table?
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("PART 1d: GDP sector count — probe specific 3-digit NAICS vectors")
print("  (SA monthly, Table 36-10-0434-01)")
print("=" * 70)

# Key known vectors from the pipeline catalog (SA, monthly, chained 2017$):
# v65201210 = all industries total
# v65201211 = goods-producing
# v65201212 = service-producing
# v65201263 = manufacturing (NAICS 31-33)
# v65201236 = mining, quarrying, oil and gas (NAICS 21)

# Try to probe deeper sub-sectors by using getCubeMetadata to count
# members along the industry dimension
print("  Checking dimension structure for industry depth in 36-10-0434-01...")

# Additional vector probes for known sub-sectors
probe_vectors = {
    65201210: "All industries",
    65201211: "Goods-producing industries",
    65201212: "Services-producing industries",
    65201236: "Mining, quarrying, oil and gas (NAICS 21)",
    65201263: "Manufacturing (NAICS 31-33)",
}

# Try a few more sub-sectors via coordinate guesses
# Coordinate structure in 36-10-0434: Geo.Industry.Prices.SeasonalAdj
# Coord 1.X.1.1 for Canada, industry X, basic prices, SA
# Probe: construction (NAICS 23), retail trade (NAICS 44-45), finance (NAICS 52)
# Use getSeriesInfoFromCubePidCoord to probe
candidate_coords = [
    (36100434, "1.4.1.1", "Construction (NAICS 23) - coord guess"),
    (36100434, "1.5.1.1", "Wholesale trade (NAICS 41) - coord guess"),
    (36100434, "1.6.1.1", "Retail trade (NAICS 44-45) - coord guess"),
    (36100434, "1.7.1.1", "Trans/warehousing (NAICS 48-49) - coord guess"),
    (36100434, "1.8.1.1", "Finance/insurance (NAICS 52) - coord guess"),
]

print("  Probing candidate 3-digit sub-sector coordinates:")
for pid, coord, label in candidate_coords:
    body = [{"productId": pid, "coordinate": coord}]
    result = wds_post("getSeriesInfoFromCubePidCoord", body)
    if isinstance(result, list) and result:
        status = result[0].get("status", "?")
        title = result[0].get("object", {}).get("SeriesTitleEn", "") if status == "SUCCESS" else ""
        vid = result[0].get("object", {}).get("vectorId", "") if status == "SUCCESS" else ""
        print(f"  {coord}: [{status}] {title} (v{vid})")
    else:
        print(f"  {coord}: [{label}] no response")

print()
print(f"  Completed at {datetime.now().isoformat()}")
