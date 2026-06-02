"""
Part 1e: Probe Table 36-10-0434-01 by coordinate (industry dimension 2)
to count and classify available NAICS industries.

Coord structure: Geo.Industry.Prices.SeasonalAdj.0.0.0.0.0.0
  Geo=1 (Canada), Prices=1 (basic prices), SA=1 (seasonally adjusted)

Probe industry dim 2 from 1 to 300 in batches to find the full set of
industry codes that have data.

Also probe LFS 14-10-0023-01 for industry dim structure.

Run from repo root:
    py claude-ref/research/recession_watch/part1e_coord_probe.py
"""

from __future__ import annotations

import json
import sys
import urllib.request
import urllib.error
from datetime import datetime

WDS_BASE = "https://www150.statcan.gc.ca/t1/wds/rest"
ENDPOINT_LATEST_N = f"{WDS_BASE}/getDataFromVectorsAndLatestNPeriods"
COORD_ENDPOINT = f"{WDS_BASE}/getDataFromCubePidCoordAndLatestNPeriods"


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
        print(f"  POST error: {e}", file=sys.stderr)
        return []


def batch_by_vector(vids: list[int], latest_n: int = 1) -> dict[int, dict | None]:
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
        if vid and status == "SUCCESS" and obj.get("vectorDataPoint"):
            out[vid] = {"coord": coord, "pts": obj["vectorDataPoint"]}
    return out


# ---------------------------------------------------------------------------
# Strategy: We know the active vector IDs from the earlier probe.
# Extract their coordinates using the batch endpoint, which returns 'coordinate'.
# This maps each vector to its industry dimension position.
# ---------------------------------------------------------------------------

print("=" * 70)
print("Extracting coordinates for all known GDP industry vectors")
print("=" * 70)

# All active GDP vectors found in earlier scan
all_gdp_vids = [
    65201210, 65201211, 65201212, 65201213, 65201216, 65201219, 65201220,
    65201221, 65201222, 65201223, 65201224, 65201225, 65201227, 65201229,
    65201230, 65201231, 65201232, 65201233, 65201234, 65201235, 65201236,
    65201237, 65201238, 65201239, 65201240, 65201241, 65201242, 65201243,
    65201244, 65201245, 65201246, 65201247, 65201248, 65201249, 65201250,
    65201251, 65201252, 65201253, 65201254, 65201255, 65201256, 65201257,
    65201258, 65201259, 65201260, 65201261, 65201262, 65201263, 65201264,
    65201265, 65201266, 65201267, 65201268, 65201269, 65201270, 65201271,
    65201272, 65201273, 65201274, 65201275, 65201276, 65201277, 65201278,
    65201279, 65201282, 65201283, 65201284, 65201285, 65201286, 65201287,
    65201288, 65201289, 65201290, 65201291, 65201292, 65201293, 65201294,
    65201295, 65201296, 65201297, 65201301, 65201304, 65201307, 65201308,
    65201309, 65201310, 65201311, 65201312, 65201313, 65201322, 65201330,
    65201336, 65201341, 65201342, 65201343, 65201344, 65201345, 65201346,
    65201348, 65201349, 65201350, 65201351, 65201355, 65201356, 65201357,
    65201358, 65201359,
]

# Fetch in batches of 50
coords_map: dict[int, str] = {}
for i in range(0, len(all_gdp_vids), 50):
    batch = all_gdp_vids[i:i+50]
    result = batch_by_vector(batch, latest_n=1)
    for vid, obj in result.items():
        if obj:
            coords_map[vid] = obj["coord"]

print(f"  Got coordinates for {len(coords_map)} vectors")
print()

# Parse industry dimension (dim 2) from each coordinate
# Coord format: "1.IND.PRICE.SA.0.0.0.0.0.0"
# Filter to SA (dim4=1) and basic prices (dim3=1) and Canada (dim1=1)

# Group by industry dimension value
industry_dim: dict[int, list[int]] = {}  # ind_code -> [vector_ids]
for vid, coord in sorted(coords_map.items()):
    parts = coord.split(".")
    if len(parts) >= 4:
        try:
            geo, ind, price, sa = int(parts[0]), int(parts[1]), int(parts[2]), int(parts[3])
            if geo == 1 and price == 1 and sa == 1:  # Canada, basic prices, SA
                if ind not in industry_dim:
                    industry_dim[ind] = []
                industry_dim[ind].append(vid)
        except (ValueError, IndexError):
            pass

print(f"  SA + basic prices industry codes found: {sorted(industry_dim.keys())}")
print(f"  Count: {len(industry_dim)} distinct industry dimension values")
print()
print("  Industry dim code -> vector ID(s):")
for ind_code in sorted(industry_dim.keys()):
    vids = industry_dim[ind_code]
    print(f"  [{ind_code:>4}]: v{vids[0]} (+ {len(vids)-1} others)")

# How many of these are "leaf" nodes (appear to be 3-digit NAICS or finer)?
# The industry dimension in 36-10-0434 includes aggregates + sub-aggregates.
# StatCan publishes approx 300 series in this table based on the user guide.
# The total count tells us if 3-digit diffusion is feasible.
print()
print(f"  Total SA+basic-prices industry dimension positions: {len(industry_dim)}")
print()
print("  This represents the maximum number of industry components")
print("  available for a GDP diffusion index.")

# ---------------------------------------------------------------------------
# LFS employment by industry — extract coordinates from known active vectors
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("LFS employment by industry — coordinate analysis")
print("=" * 70)

# All active LFS vectors found in earlier probe
lfs_vids = [
    2062811,  # known total
    2062820, 2062821, 2062822, 2062823, 2062824, 2062825, 2062826,
    2062827, 2062828, 2062829, 2062830, 2062831, 2062832, 2062833,
    2062834, 2062835, 2062836, 2062837, 2062838, 2062839, 2062840,
    2062841, 2062842, 2062843, 2062844, 2062845, 2062846, 2062847,
    2062848, 2062849, 2062850, 2062851, 2062852, 2062853, 2062854,
    2062855, 2062856, 2062857, 2062858, 2062859, 2062860, 2062861,
    2062862, 2062863, 2062864, 2062865, 2062868, 2062869, 2062870,
    2062871, 2062872, 2062873, 2062874, 2062877, 2062878, 2062879,
    2062880, 2062881, 2062882, 2062883, 2062886, 2062887, 2062888,
    2062889, 2062890, 2062891, 2062892, 2062895, 2062896, 2062897,
    2062898, 2062899, 2062900, 2062901, 2062904, 2062905, 2062906,
    2062907, 2062908, 2062909, 2062910, 2062913, 2062914, 2062915,
    2062916, 2062917, 2062918, 2062919, 2062920, 2062921, 2062922,
    2062923, 2062924, 2062925, 2062926, 2062927, 2062928, 2062929,
    2062930, 2062931, 2062932, 2062933, 2062934, 2062935, 2062936,
    2062937, 2062938, 2062939, 2062940, 2062941, 2062942, 2062943,
    2062944, 2062945, 2062946, 2062947, 2062948, 2062949, 2062950,
    2062951, 2062952, 2062953, 2062954, 2062955, 2062956, 2062957,
    2062958, 2062959,
]

lfs_coords: dict[int, str] = {}
for i in range(0, len(lfs_vids), 50):
    batch = lfs_vids[i:i+50]
    result = batch_by_vector(batch, latest_n=1)
    for vid, obj in result.items():
        if obj:
            lfs_coords[vid] = obj["coord"]

print(f"  Got coordinates for {len(lfs_coords)} LFS vectors")
print()
print("  Sample of coordinates (first 20):")
for vid, coord in list(sorted(lfs_coords.items()))[:20]:
    print(f"  v{vid}: coord={coord}")

# Count distinct industry dimension values for LFS
# LFS 14-10-0287 structure: Geo.Statistics.Gender.Age.Estimate.SeasonalAdj
# Let's see what dimension structure LFS uses
print()
print("  Unique coordinate dimension counts:")
if lfs_coords:
    # Count the number of dimensions
    sample_coord = list(lfs_coords.values())[0]
    num_dims = len(sample_coord.split("."))
    print(f"  Number of dimensions: {num_dims}")
    print()

    # The table 14-10-0287 has: Geo.Statistics.Gender.Age.Estimate.SA
    # statistics dim 2: unemployment rate, employment rate, etc.
    # Industry LFS is Table 14-10-0023 or 14-10-0355
    # Let me check what productId these vectors belong to
    for vid, coord in list(sorted(lfs_coords.items()))[:5]:
        print(f"  v{vid}: coord={coord}")

print()
print(f"Completed at {datetime.now().isoformat()}")
