"""
Part 1b: GDP industry granularity probe.
Uses the WDS batch vector endpoint (which works) rather than getCubeMetadata (404).

Strategy: probe known vectors for ~20 sector aggregates in Table 36-10-0434-01
then probe a set of likely 3-digit NAICS sub-sector vectors to establish
what depth is actually available.

Run from repo root:
    py claude-ref/research/recession_watch/part1b_gdp_industry_probe.py
"""

from __future__ import annotations

import json
import sys
import urllib.request
import urllib.error
from datetime import datetime

WDS_BASE = "https://www150.statcan.gc.ca/t1/wds/rest"
ENDPOINT_LATEST_N = f"{WDS_BASE}/getDataFromVectorsAndLatestNPeriods"


def batch_fetch(vector_ids: list[int], latest_n: int = 3) -> dict[int, dict | None]:
    """Fetch latest N periods for a batch of vector IDs. Returns {vid: obj_or_None}."""
    body = [{"vectorId": vid, "latestN": latest_n} for vid in vector_ids]
    data = json.dumps(body).encode()
    req = urllib.request.Request(
        ENDPOINT_LATEST_N, data=data,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            results = json.loads(resp.read().decode())
    except (urllib.error.HTTPError, urllib.error.URLError) as e:
        print(f"  ERROR fetching batch: {e}", file=sys.stderr)
        return {vid: None for vid in vector_ids}

    out = {}
    for item in results:
        status = item.get("status", "")
        obj = item.get("object", {})
        vid = obj.get("vectorId")
        if vid and status == "SUCCESS":
            pts = obj.get("vectorDataPoint", [])
            out[vid] = {"title": obj.get("SeriesTitleEn", ""), "pts": pts}
        elif vid:
            out[vid] = None
    return out


# ---------------------------------------------------------------------------
# Known vectors from the catalog (Table 36-10-0434-01, SA monthly)
# ---------------------------------------------------------------------------
known_vectors = {
    65201210: "All industries",
    65201211: "Goods-producing industries",
    65201212: "Services-producing industries",
    65201236: "Mining, quarrying, oil and gas (NAICS 21)",
    65201263: "Manufacturing (NAICS 31-33)",
}

print("=" * 70)
print("PART 1: GDP by industry (36-10-0434-01) — known catalog vectors")
print("=" * 70)
results = batch_fetch(list(known_vectors.keys()))
for vid, label in known_vectors.items():
    r = results.get(vid)
    if r:
        latest = r["pts"][-1] if r["pts"] else None
        title = r["title"] or label
        date_str = latest["refPer"] if latest else "?"
        val = latest["value"] if latest else "?"
        print(f"  v{vid}: {label}")
        print(f"    Latest: {date_str} = {val}")
    else:
        print(f"  v{vid}: {label} -> FAILED")

# ---------------------------------------------------------------------------
# Probe a range of vector IDs near the known ones to find more sub-sectors
# The catalog has v65201210 (all industries), v65201211 (goods), v65201212 (services)
# v65201236 (mining), v65201263 (manufacturing)
# StatCan typically assigns contiguous blocks — probe v65201213 through v65201280
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("PART 1: Probing vector range v65201213 to v65201280 for sub-sectors")
print("=" * 70)

PROBE_START = 65201213
PROBE_END   = 65201290
BATCH_SIZE  = 30

found_sectors: list[tuple[int, str, str, float | None]] = []

for batch_start in range(PROBE_START, PROBE_END, BATCH_SIZE):
    batch_end = min(batch_start + BATCH_SIZE, PROBE_END)
    vids = list(range(batch_start, batch_end))
    res = batch_fetch(vids, latest_n=2)
    for vid in vids:
        r = res.get(vid)
        if r and r["pts"]:
            pts = r["pts"]
            latest_pt = pts[-1]
            refper = latest_pt.get("refPer", "?")
            val = latest_pt.get("value")
            title = r.get("title", "")
            found_sectors.append((vid, title, refper, val))

if found_sectors:
    print(f"  Found {len(found_sectors)} active vectors in range:")
    for vid, title, refper, val in sorted(found_sectors, key=lambda x: x[0]):
        print(f"  v{vid}: [{refper}={val}] {title}")
else:
    print("  No active vectors found in range v65201213-v65201289")

# Try a wider scan if nothing found — maybe the sub-sectors are not contiguous
print()
print("=" * 70)
print("PART 1: Extended scan v65201230 to v65201350 in batches")
print("=" * 70)

found_sectors2: list[tuple[int, str, str, float | None]] = []
for batch_start in range(65201230, 65201360, BATCH_SIZE):
    batch_end = min(batch_start + BATCH_SIZE, 65201360)
    vids = list(range(batch_start, batch_end))
    res = batch_fetch(vids, latest_n=2)
    for vid in vids:
        r = res.get(vid)
        if r and r["pts"]:
            pts = r["pts"]
            latest_pt = pts[-1]
            refper = latest_pt.get("refPer", "?")
            val = latest_pt.get("value")
            title = r.get("title", "")
            found_sectors2.append((vid, title, refper, val))

if found_sectors2:
    print(f"  Found {len(found_sectors2)} active vectors in extended range:")
    for vid, title, refper, val in sorted(found_sectors2, key=lambda x: x[0]):
        print(f"  v{vid}: [{refper}={val}] {title}")
else:
    print("  No additional vectors found in extended range")

# ---------------------------------------------------------------------------
# LFS Employment by industry — probe Table 14-10-0023-01
# This table: "Employment by industry, monthly, seasonally adjusted"
# Known NAICS aggregates in LFS: ~16 major sectors
# v2062811 = total employment from 14-10-0287-01
# Let's probe known employment-by-industry vectors
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("PART 1: LFS employment by industry (Table 14-10-0023-01)")
print("  Probing vector range near known LFS vectors")
print("=" * 70)

# The LFS by-industry SA monthly table is 14-10-0023-01
# StatCan standard 16 NAICS sectors used in LFS:
# 1. Agriculture (NAICS 11)
# 2. Forestry, fishing, mining, quarrying, oil and gas (NAICS 21+22+113+114+115+212)
# 3. Utilities (NAICS 22)
# 4. Construction (NAICS 23)
# 5. Manufacturing (NAICS 31-33)
# 6. Wholesale and retail trade (NAICS 41, 44-45)
# 7. Transportation and warehousing (NAICS 48-49)
# 8. Finance, insurance, real estate, rental and leasing (NAICS 52-53)
# 9. Professional, scientific and technical services (NAICS 54)
# 10. Business, building and other support services (NAICS 55-56)
# 11. Educational services (NAICS 61)
# 12. Health care and social assistance (NAICS 62)
# 13. Information, culture and recreation (NAICS 51, 71)
# 14. Accommodation and food services (NAICS 72)
# 15. Other services (NAICS 81)
# 16. Public administration (NAICS 91)

# Try probing some candidate vectors for SA LFS by-industry
# From boc-tracker and known WDS patterns, SA LFS employment by industry
# for Canada lives around v2062870-2062900 range in 14-10-0023
lfs_probe_ranges = [
    range(2062820, 2062870),
    range(2062870, 2062920),
    range(2062920, 2062960),
]

lfs_found = []
for r in lfs_probe_ranges:
    vids = list(r)
    res = batch_fetch(vids, latest_n=2)
    for vid in vids:
        obj = res.get(vid)
        if obj and obj["pts"]:
            pts = obj["pts"]
            latest_pt = pts[-1]
            refper = latest_pt.get("refPer", "?")
            val = latest_pt.get("value")
            title = obj.get("title", "")
            lfs_found.append((vid, title, refper, val))

if lfs_found:
    print(f"  Found {len(lfs_found)} active LFS vectors in probed ranges:")
    for vid, title, refper, val in sorted(lfs_found, key=lambda x: x[0]):
        print(f"  v{vid}: [{refper}={val}] {title}")
else:
    print("  No LFS by-industry vectors found in probed ranges")
    print("  NOTE: 14-10-0023-01 SA employment by industry vectors may not be")
    print("  accessible via the batch vector endpoint. They may require the bulk")
    print("  CSV download approach instead.")

print()
print(f"Completed at {datetime.now().isoformat()}")
