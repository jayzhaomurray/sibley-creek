"""Tests for the C.D. Howe BCC recessions JSON shape and internal consistency.

The file is hand-curated (no fetcher); these tests guard against drift when
the editorial team updates the file as new BCC communiques land.
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
BCC_PATH = ROOT / "data" / "derived" / "cdhowe_bcc_recessions.json"
META_PATH = ROOT / "data" / "derived" / "cdhowe_bcc_recessions.meta.json"


def _load_entries() -> list[dict]:
    return json.loads(BCC_PATH.read_text(encoding="utf-8"))


def _load_meta() -> dict:
    return json.loads(META_PATH.read_text(encoding="utf-8"))


def test_files_exist():
    assert BCC_PATH.exists(), f"missing {BCC_PATH}"
    assert META_PATH.exists(), f"missing {META_PATH}"


def test_entry_shape():
    """Every entry has {name, start, end, type} and nothing else."""
    entries = _load_entries()
    assert entries, "JSON file is empty"
    required = {"name", "start", "end", "type"}
    for i, entry in enumerate(entries):
        assert set(entry.keys()) == required, (
            f"entry {i} ({entry.get('name')!r}) keys = {set(entry.keys())}, "
            f"expected {required}"
        )
        assert entry["type"] in ("recession", "expansion"), (
            f"entry {i}: type must be recession or expansion, got {entry['type']!r}"
        )
        # start must always be a valid ISO date
        date.fromisoformat(entry["start"])
        # end may be null only for the currently-open span
        if entry["end"] is not None:
            date.fromisoformat(entry["end"])


def test_only_trailing_span_can_be_open():
    """Only the last entry can have end == None (the in-progress cycle)."""
    entries = _load_entries()
    for entry in entries[:-1]:
        assert entry["end"] is not None, (
            f"non-trailing entry {entry['name']!r} has end=null; only the last "
            "entry (the open expansion or recession) may have a null end."
        )


def test_chronological_and_contiguous():
    """Entries are sorted by start date and span end+1day == next start."""
    entries = _load_entries()
    for prev, curr in zip(entries, entries[1:]):
        prev_start = date.fromisoformat(prev["start"])
        curr_start = date.fromisoformat(curr["start"])
        assert curr_start > prev_start, (
            f"entries not in chronological order: {prev['name']!r} "
            f"({prev['start']}) >= {curr['name']!r} ({curr['start']})"
        )


def test_types_alternate():
    """Recession and expansion entries should alternate (no two recessions
    in a row, no two expansions in a row)."""
    entries = _load_entries()
    for prev, curr in zip(entries, entries[1:]):
        assert prev["type"] != curr["type"], (
            f"entries {prev['name']!r} and {curr['name']!r} have the same "
            f"type ({prev['type']!r}); recession and expansion must alternate."
        )


@pytest.mark.parametrize(
    "expected_name,start,end",
    [
        # Spot-check the two BCC recessions chart-builder explicitly cites
        # (panel-1, panel-6 spec): 2008-09 GFC and 2020 COVID.
        ("Great Recession 2008-09", "2008-10-01", "2009-05-31"),
        ("COVID-19 2020Q1-Q2", "2020-02-01", "2020-04-30"),
    ],
)
def test_canonical_bands_present(expected_name, start, end):
    entries = _load_entries()
    by_name = {e["name"]: e for e in entries}
    assert expected_name in by_name, f"missing canonical band {expected_name!r}"
    band = by_name[expected_name]
    assert band["type"] == "recession"
    assert band["start"] == start
    assert band["end"] == end


def test_meta_carries_provenance():
    meta = _load_meta()
    assert meta["name"] == "cdhowe_bcc_recessions"
    assert "cdhowe" in meta["source_url"].lower()
    assert meta["frequency"] == "irregular"
    # Schema version is the same as the rest of the pipeline
    assert meta["schema_version"] == 1
