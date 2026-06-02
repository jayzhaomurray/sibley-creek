"""
Part 1c: Resolve titles for GDP and LFS industry vectors using the
WDS getSeriesInfoFromVector endpoint (GET, not POST).

Run from repo root:
    py claude-ref/research/recession_watch/part1c_title_resolve.py
"""

from __future__ import annotations

import json
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime

WDS_BASE = "https://www150.statcan.gc.ca/t1/wds/rest"


def get_series_info(vector_id: int) -> dict | None:
    """GET /getSeriesInfoFromVector/{vectorId}"""
    url = f"{WDS_BASE}/getSeriesInfoFromVector/{vector_id}"
    req = urllib.request.Request(
        url,
        headers={"Accept": "application/json"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
            if data.get("status") == "SUCCESS":
                return data.get("object", {})
            return None
    except Exception:
        return None


def resolve_titles(vector_ids: list[int], label: str) -> list[tuple[int, str, str]]:
    """Returns [(vid, cube_title, series_title), ...]"""
    results = []
    for i, vid in enumerate(vector_ids):
        if i > 0 and i % 10 == 0:
            time.sleep(0.5)  # gentle rate limiting
        info = get_series_info(vid)
        if info:
            cube = info.get("cubeTitleEn", "")
            series = info.get("SeriesTitleEn", "")
            results.append((vid, cube, series))
        else:
            results.append((vid, "?", "?"))
    return results


# ---------------------------------------------------------------------------
# GDP by industry — resolve a key subset
# ---------------------------------------------------------------------------
print("=" * 70)
print("GDP by industry (36-10-0434-01) — resolving titles for key vectors")
print("=" * 70)

# From the probe: the ~20 sector aggregates (by magnitude) appear to be:
# Large: v65201213(1.9T), v65201211(goods 585B), v65201212(services 1.76T)
# v65201216(440B), v65201219(383B), v65201227(483B), v65201258(166B)
# v65201263(mfg 199B), v65201236(mining 119B)
# Let's resolve the top aggregates + a sample of fine-grained ones

gdp_key_vectors = [
    65201210,  # All industries (known)
    65201211,  # Goods-producing (known)
    65201212,  # Services-producing (known)
    65201213,  # ~1.9T -- likely "Total value added" or similar aggregate
    65201216,  # 440B
    65201219,  # 383B
    65201220,  # 92B
    65201221,  # 106B
    65201222,  # 143B
    65201225,  # 161B
    65201227,  # 483B
    65201229,  # 46B
    65201236,  # Mining/oil (known)
    65201237,  # 77B
    65201238,  # 37B
    65201254,  # 48B
    65201258,  # 166B
    65201259,  # 53B
    65201263,  # Manufacturing (known)
    65201290,  # 14B
    65201358,  # 129B -- may be finance/real-estate
]

print(f"  Resolving {len(gdp_key_vectors)} vectors (with rate limiting)...")
gdp_titles = resolve_titles(gdp_key_vectors, "GDP")
for vid, cube, series in gdp_titles:
    print(f"  v{vid}: {series}")

# Count total distinct industry depth
print()
print("  All confirmed active GDP vectors in range 65201210-65201360:")
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
print(f"  Total active vectors found: {len(all_gdp_vids)}")

# ---------------------------------------------------------------------------
# LFS employment by industry — resolve a sample
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("LFS employment by industry — resolving titles for key vectors")
print("=" * 70)

# From the probe: many vectors in 2062820-2062959 range
# The values are in thousands. Looking at magnitudes:
# v2062917=29788 (~30M?) seems too large for employment...
# Actually employment_level (total) = 21033.7 thousands in April 2026
# So 29788 would be some other series (maybe all-gender combined, all-age)
# v2062820=11081 (~11M) could be a major sector or provincial cut
# Let's resolve a sample of larger-magnitude ones

lfs_key_vectors = [
    2062811,  # Total employment (known)
    2062820,  # 11081K
    2062821,  # 9578K
    2062827,  # 17481K
    2062828,  # 10677K
    2062890,  # 2672K
    2062891,  # 2059K
    2062917,  # 29788K
    2062918,  # 19477K
    2062919,  # 18356K
    2062920,  # 15879K
    2062926,  # 14692K
    2062927,  # 10313K
    2062935,  # 15096K
    2062936,  # 9164K
    2062944,  # 16817K
    2062945,  # 14881K
]

print(f"  Resolving {len(lfs_key_vectors)} LFS vectors...")
lfs_titles = resolve_titles(lfs_key_vectors, "LFS")
for vid, cube, series in lfs_titles:
    print(f"  v{vid}: {series}")
    if "industry" in series.lower() or "NAICS" in series or "employm" in series.lower():
        print(f"    -> INDUSTRY SERIES (cube: {cube})")

print()
print(f"Completed at {datetime.now().isoformat()}")
