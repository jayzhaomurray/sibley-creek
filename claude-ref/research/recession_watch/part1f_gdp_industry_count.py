"""
Part 1f: Determine true GDP industry count in 36-10-0434-01 by probing
via coordinate systematically (dim2 = industry, SA, basic prices, Canada).

Coord: 1.{industry}.1.1.0.0.0.0.0.0
Probe industry dim from 1 to 400 in batches using getDataFromCubePidCoordAndLatestNPeriods.

Run from repo root:
    py claude-ref/research/recession_watch/part1f_gdp_industry_count.py
"""

from __future__ import annotations

import json
import sys
import urllib.request
import urllib.error
from datetime import datetime

WDS_BASE = "https://www150.statcan.gc.ca/t1/wds/rest"
CUBE_COORD_ENDPOINT = f"{WDS_BASE}/getDataFromCubePidCoordAndLatestNPeriods"


def post_cube_coords(pid: int, coords: list[str], latest_n: int = 1) -> dict[str, dict | None]:
    """Fetch latest N for a list of coordinate strings in a given cube."""
    body = [{"productId": pid, "coordinate": c, "latestN": latest_n} for c in coords]
    data = json.dumps(body).encode()
    req = urllib.request.Request(
        CUBE_COORD_ENDPOINT, data=data,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            results = json.loads(resp.read().decode())
    except Exception as e:
        print(f"  POST error: {e}", file=sys.stderr)
        return {c: None for c in coords}

    out: dict[str, dict | None] = {}
    for item in results:
        status = item.get("status", "")
        obj = item.get("object", {})
        coord = obj.get("coordinate", "")
        if status == "SUCCESS" and obj.get("vectorDataPoint"):
            pts = obj["vectorDataPoint"]
            vid = obj.get("vectorId")
            out[coord] = {"vid": vid, "pts": pts}
        else:
            out[coord] = None
    return out


# ---------------------------------------------------------------------------
# Probe Table 36-10-0434-01: industry dimension 1 to 400, SA, basic prices
# Coordinate: 1.{ind}.1.1.0.0.0.0.0.0
# ---------------------------------------------------------------------------
print("=" * 70)
print("Probing Table 36-10-0434-01 industry dimension (coord 1.IND.1.1)")
print("=" * 70)

PID = 36100434
BATCH_SIZE = 50
found_industries: list[tuple[str, int, float]] = []  # (coord, vid, latest_value)

for batch_start in range(1, 401, BATCH_SIZE):
    batch_end = min(batch_start + BATCH_SIZE, 401)
    coords = [f"1.{ind}.1.1.0.0.0.0.0.0" for ind in range(batch_start, batch_end)]
    results = post_cube_coords(PID, coords, latest_n=1)
    for coord, obj in results.items():
        if obj and obj.get("pts"):
            pts = obj["pts"]
            val = pts[-1].get("value") if pts else None
            vid = obj.get("vid")
            if val is not None:
                found_industries.append((coord, vid or 0, val))
    print(f"  Batch {batch_start}-{batch_end-1}: found {sum(1 for c in coords if results.get(c))} active")

print()
print(f"  Total active industry coordinates found: {len(found_industries)}")
print()
print("  Active coordinates (industry dim positions with data):")
for coord, vid, val in sorted(found_industries, key=lambda x: int(x[0].split(".")[1])):
    ind_num = int(coord.split(".")[1])
    print(f"  [{ind_num:>4}] coord={coord} v{vid} latest={val:.0f}")

# Summary
print()
print("  Summary:")
print(f"  Total industry positions in 36-10-0434-01 (SA, basic prices): {len(found_industries)}")
print()
print("  Interpretation:")
if len(found_industries) <= 25:
    print("  -> Roughly 20-sector level (2-digit NAICS aggregates)")
    print("  -> 3-digit NAICS diffusion NOT available in this SA table")
elif len(found_industries) <= 60:
    print("  -> Intermediate depth (3-digit NAICS sub-sectors)")
    print("  -> GDP diffusion feasible at this granularity")
else:
    print("  -> Deep sub-sector detail (3-digit or finer)")
    print("  -> GDP diffusion index is richly feasible")

print()
print(f"Completed at {datetime.now().isoformat()}")
