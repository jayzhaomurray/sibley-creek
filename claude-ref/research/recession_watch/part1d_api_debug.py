"""
Debug: find the correct WDS endpoint format and probe the bulk CSV approach
for GDP by industry table (36-10-0434-01).

Run from repo root:
    py claude-ref/research/recession_watch/part1d_api_debug.py
"""

from __future__ import annotations

import json
import sys
import urllib.request
import urllib.error
from datetime import datetime

WDS_BASE = "https://www150.statcan.gc.ca/t1/wds/rest"

def try_endpoint(url: str, method: str = "GET", body: bytes | None = None) -> tuple[int, str]:
    headers = {"Accept": "application/json", "User-Agent": "Mozilla/5.0"}
    if body:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            code = resp.getcode()
            raw = resp.read().decode("utf-8", errors="replace")
            return code, raw[:500]
    except urllib.error.HTTPError as e:
        return e.code, str(e)
    except Exception as ex:
        return 0, str(ex)


# Test 1: getSeriesInfoFromVector (GET)
print("Test 1: getSeriesInfoFromVector/{vectorId}")
for url in [
    f"{WDS_BASE}/getSeriesInfoFromVector/65201210",
    f"{WDS_BASE}/getSeriesInfoFromVector/v65201210",
    f"https://www150.statcan.gc.ca/t1/wds/rest/getSeriesInfoFromVector/65201210",
]:
    code, resp = try_endpoint(url)
    print(f"  [{code}] {url[:80]}")
    if code == 200:
        print(f"  -> {resp[:200]}")

# Test 2: getSeriesInfoFromCubePidCoord (GET variant)
print()
print("Test 2: getSeriesInfoFromCubePidCoord as GET")
url = f"{WDS_BASE}/getSeriesInfoFromCubePidCoord/36100434/1.1.1.1"
code, resp = try_endpoint(url)
print(f"  [{code}] {url}")
if code == 200:
    print(f"  -> {resp[:200]}")

# Test 3: getCubeMetadata with no trailing slash and correct pid format
print()
print("Test 3: getCubeMetadata variants")
for url in [
    f"{WDS_BASE}/getCubeMetadata/36100434",
    f"{WDS_BASE}/getCubeMetadata/36100434/",
    f"https://www150.statcan.gc.ca/t1/wds/rest/getCubeMetadata/36100434",
]:
    code, resp = try_endpoint(url)
    print(f"  [{code}] {url}")
    if code == 200:
        print(f"  -> {resp[:200]}")

# Test 4: getAllCubesList (GET) — may reveal the correct API structure
print()
print("Test 4: getAllCubesList")
url = f"{WDS_BASE}/getAllCubesList"
code, resp = try_endpoint(url)
print(f"  [{code}] {url}")
if code == 200:
    print(f"  -> {resp[:300]}")

# Test 5: getChangedCubeList
print()
print("Test 5: getChangedCubeList/{date}")
url = f"{WDS_BASE}/getChangedCubeList/2026-05-01"
code, resp = try_endpoint(url)
print(f"  [{code}] {url}")
if code == 200:
    print(f"  -> {resp[:200]}")

# Test 6: getDataFromVectorsAndLatestNPeriods — the one that WORKS — inspect full response
print()
print("Test 6: Full response from working endpoint (v65201210, latest 1 obs)")
body = json.dumps([{"vectorId": 65201210, "latestN": 1}]).encode()
code, resp = try_endpoint(
    f"{WDS_BASE}/getDataFromVectorsAndLatestNPeriods",
    method="POST", body=body
)
print(f"  [{code}]")
# Print full response to see all available fields
data = json.loads(resp + "...")  if code != 200 else json.loads(resp)
if isinstance(data, list) and data:
    obj = data[0].get("object", {})
    print("  Object keys:", list(obj.keys()))
    print("  Full object (first item):")
    print(json.dumps(obj, indent=2)[:1000])

# Test 7: Check if SeriesTitleEn comes back with latestN > 0
print()
print("Test 7: getDataFromVectorsAndLatestNPeriods latestN=2 — check all fields")
body = json.dumps([{"vectorId": 65201210, "latestN": 2}]).encode()
headers = {"Content-Type": "application/json", "Accept": "application/json"}
req = urllib.request.Request(
    f"{WDS_BASE}/getDataFromVectorsAndLatestNPeriods",
    data=body, headers=headers, method="POST"
)
with urllib.request.urlopen(req, timeout=15) as resp:
    full_data = json.loads(resp.read().decode())
print(json.dumps(full_data[0], indent=2))

print()
print(f"Completed at {datetime.now().isoformat()}")
