"""
Part 1g: Decode the LFS employment by industry structure from 14-10-0287-01
coordinates, and probe 14-10-0355-01 and 14-10-0023-01 for by-industry employment.

The earlier probe found vectors 2062820-2062959 are all in 14-10-0287-01
(the main LFS summary table). The coordinates show:
  dim2 = statistics type (3=employed persons, etc.)
  dim3 = industry OR age grouping
  dim4 = age/gender

We need employment by INDUSTRY. Let's decode dim3 for employed persons (dim2=3).

Also: the StatCan LFS-by-industry table is actually 14-10-0355-01 or 14-10-0023-01
(these get 404 on getCubeMetadata but may work on the coord endpoint).

Run from repo root:
    py claude-ref/research/recession_watch/part1g_lfs_industry_decode.py
"""

from __future__ import annotations

import json
import sys
import urllib.request
import urllib.error
from datetime import datetime

WDS_BASE = "https://www150.statcan.gc.ca/t1/wds/rest"
ENDPOINT_LATEST_N = f"{WDS_BASE}/getDataFromVectorsAndLatestNPeriods"
CUBE_COORD_ENDPOINT = f"{WDS_BASE}/getDataFromCubePidCoordAndLatestNPeriods"


def post_json(url: str, body: list, timeout: int = 30) -> list:
    data = json.dumps(body).encode()
    req = urllib.request.Request(
        url, data=data,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        print(f"  POST error on {url}: {e}", file=sys.stderr)
        return []


def batch_vectors(vids: list[int], latest_n: int = 1) -> dict[int, dict | None]:
    if not vids:
        return {}
    body = [{"vectorId": vid, "latestN": latest_n} for vid in vids]
    results = post_json(ENDPOINT_LATEST_N, body)
    out = {}
    for item in results:
        status = item.get("status", "")
        obj = item.get("object", {})
        vid = obj.get("vectorId")
        coord = obj.get("coordinate", "")
        pid = obj.get("productId")
        if vid and status == "SUCCESS" and obj.get("vectorDataPoint"):
            out[vid] = {
                "coord": coord, "pid": pid,
                "pts": obj["vectorDataPoint"]
            }
    return out


def post_cube_coords(pid: int, coords: list[str], latest_n: int = 1) -> dict[str, dict | None]:
    body = [{"productId": pid, "coordinate": c, "latestN": latest_n} for c in coords]
    results = post_json(CUBE_COORD_ENDPOINT, body, timeout=30)
    out: dict[str, dict | None] = {}
    for item in results:
        status = item.get("status", "")
        obj = item.get("object", {})
        coord = obj.get("coordinate", "")
        if status == "SUCCESS" and obj.get("vectorDataPoint"):
            pts = obj["vectorDataPoint"]
            vid = obj.get("vectorId")
            val = pts[-1].get("value") if pts else None
            out[coord] = {"vid": vid, "val": val}
        else:
            out[coord] = None
    return out


# ---------------------------------------------------------------------------
# PART A: Decode LFS 14-10-0287-01 employment by industry
# dim2=3 = Employed persons, dim4=1 = Total age, dim5=1=Estimate, dim6=1=SA
# dim3 = industry dimension
# Probe dim3 from 1 to 50
# ---------------------------------------------------------------------------
print("=" * 70)
print("A: Probing 14-10-0287-01 employment by industry (dim3=industry)")
print("   Coord: 1.3.{IND}.1.1.1 = employed persons, total-gender, SA")
print("=" * 70)

# The total employment vector v2062811 has coord 1.3.1.1.1.1 where dim3=1=all industries
# Probing dim3 2-50 for employed persons, all ages, all gender, SA, estimate
PID_287 = 14100287

lfs_industry_sectors = []
for batch_start in range(1, 51, 10):
    batch_end = min(batch_start + 10, 51)
    coords = [f"1.3.{ind}.1.1.1.0.0.0.0" for ind in range(batch_start, batch_end)]
    results = post_cube_coords(PID_287, coords, latest_n=2)
    for coord in coords:
        obj = results.get(coord)
        ind_num = int(coord.split(".")[2])
        if obj and obj.get("val") is not None:
            vid = obj.get("vid")
            val = obj.get("val")
            lfs_industry_sectors.append((ind_num, coord, vid, val))
            print(f"  [{ind_num:>3}] v{vid} {val:.1f}k")

print()
print(f"  Found {len(lfs_industry_sectors)} employed-persons sector positions in 14-10-0287-01")

# ---------------------------------------------------------------------------
# PART B: Probe Table 14-10-0023-01 (LFS employment by industry, SA)
# This is the dedicated by-industry table
# Coord structure may differ: Geo.Industry.Gender.Age.Estimate.SA
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("B: Probing Table 14-10-0023-01 — LFS by industry SA")
print("   Coord: 1.{IND}.1.1.1.1")
print("=" * 70)

PID_023 = 14100023
lfs_023_sectors = []
for batch_start in range(1, 101, 20):
    batch_end = min(batch_start + 20, 101)
    coords = [f"1.{ind}.1.1.1.1.0.0.0.0" for ind in range(batch_start, batch_end)]
    results = post_cube_coords(PID_023, coords, latest_n=2)
    for coord in coords:
        obj = results.get(coord)
        ind_num = int(coord.split(".")[1])
        if obj and obj.get("val") is not None:
            vid = obj.get("vid")
            val = obj.get("val")
            lfs_023_sectors.append((ind_num, coord, vid, val))

if lfs_023_sectors:
    print(f"  Found {len(lfs_023_sectors)} sectors in 14-10-0023-01:")
    for ind_num, coord, vid, val in lfs_023_sectors:
        print(f"  [{ind_num:>3}] v{vid} {val:.1f}")
else:
    print("  No data found in 14-10-0023-01 via coord endpoint")

# ---------------------------------------------------------------------------
# PART C: Probe Table 14-10-0355-01 (LFS employment by industry, SA)
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("C: Probing Table 14-10-0355-01 — LFS employment by industry SA")
print("=" * 70)

PID_355 = 14100355
lfs_355_sectors = []
for batch_start in range(1, 101, 20):
    batch_end = min(batch_start + 20, 101)
    coords = [f"1.{ind}.1.1.1.1.0.0.0.0" for ind in range(batch_start, batch_end)]
    results = post_cube_coords(PID_355, coords, latest_n=2)
    for coord in coords:
        obj = results.get(coord)
        ind_num = int(coord.split(".")[1])
        if obj and obj.get("val") is not None:
            vid = obj.get("vid")
            val = obj.get("val")
            lfs_355_sectors.append((ind_num, coord, vid, val))

if lfs_355_sectors:
    print(f"  Found {len(lfs_355_sectors)} sectors in 14-10-0355-01:")
    for ind_num, coord, vid, val in lfs_355_sectors:
        print(f"  [{ind_num:>3}] v{vid} {val:.1f}")
else:
    print("  No data found in 14-10-0355-01 via coord endpoint")

# ---------------------------------------------------------------------------
# PART D: Cross-check — probe productId for the LFS vectors we already have
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("D: Which productId do the LFS 2062820+ vectors belong to?")
print("=" * 70)

# Fetch first 5 with full info to see productId
sample_vids = [2062820, 2062827, 2062890, 2062917, 2062935]
res = batch_vectors(sample_vids, latest_n=1)
for vid, obj in res.items():
    if obj:
        print(f"  v{vid}: productId={obj['pid']} coord={obj['coord']} val={obj['pts'][0]['value'] if obj['pts'] else '?'}")

# ---------------------------------------------------------------------------
# PART E: Probe 14-10-0379-01 and 14-10-0378-01 — SA LFS employment by industry
# These are newer StatCan releases
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("E: Probing newer LFS by-industry tables (14-10-0379, 14-10-0378)")
print("=" * 70)

for pid in [14100379, 14100378]:
    found = []
    for batch_start in range(1, 51, 10):
        batch_end = min(batch_start + 10, 51)
        coords = [f"1.{ind}.1.1.1.1.0.0.0.0" for ind in range(batch_start, batch_end)]
        results = post_cube_coords(pid, coords, latest_n=2)
        for coord in coords:
            obj = results.get(coord)
            if obj and obj.get("val") is not None:
                ind_num = int(coord.split(".")[1])
                found.append((ind_num, obj.get("vid"), obj.get("val")))
    if found:
        print(f"  PID {pid}: found {len(found)} sectors")
        for ind_num, vid, val in found[:10]:
            print(f"    [{ind_num}] v{vid} {val:.1f}")
    else:
        print(f"  PID {pid}: no data via coord probe")

print()
print(f"Completed at {datetime.now().isoformat()}")
