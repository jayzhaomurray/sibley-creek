"""Tests for the CPI component-level fetcher (breadth analysis inputs).

Regression coverage for the 2026-07-20 CI incident: `MAPPING_PATH` used to
be a hardcoded absolute path onto the author's local machine
(`C:/Users/jayzh/Documents/boc-tracker/...`), which does not exist on any
CI runner. Every scheduled `build-data-daily` run raised FileNotFoundError
here from 2026-05-20 through 2026-07-17 -- and because `pipeline.build`
fails the whole build on any single fetcher failure, this alone blocked
every data refresh for two months. Fixed by vendoring the mapping into
`pipeline/catalog/cpi_breadth_mapping.json` and resolving it relative to
this file. These tests guard against reintroducing a machine-local path.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from pipeline.fetch import cpi_components


def test_mapping_path_is_repo_relative():
    """MAPPING_PATH must resolve inside this repo, not a user-specific path.

    Catches any regression back to a hardcoded absolute path that happens
    to exist on one machine and nowhere else (the actual root cause of the
    2026-05-20..2026-07-17 CI outage).
    """
    repo_root = Path(__file__).resolve().parents[2]
    assert cpi_components.MAPPING_PATH.is_relative_to(repo_root), (
        f"MAPPING_PATH ({cpi_components.MAPPING_PATH}) escapes the repo root "
        f"({repo_root}). It must live under pipeline/catalog/, not a "
        "developer's local filesystem, or CI will fail again."
    )
    assert cpi_components.MAPPING_PATH.exists(), (
        "Vendored mapping file is missing; restore "
        "pipeline/catalog/cpi_breadth_mapping.json from git history."
    )


def test_load_mapping_default_path_has_full_schema():
    mapping = cpi_components.load_mapping()
    assert len(mapping) >= cpi_components.MIN_VECTOR_COUNT
    for entry in mapping:
        assert "name" in entry
        assert "cpi_vector" in entry
        assert isinstance(entry["cpi_vector"], int)


def test_load_mapping_missing_file_raises(tmp_path):
    missing = tmp_path / "does_not_exist.json"
    with pytest.raises(FileNotFoundError, match="CPI breadth mapping not found"):
        cpi_components.load_mapping(mapping_path=missing)


def test_load_mapping_rejects_too_few_entries(tmp_path):
    bad = tmp_path / "too_short.json"
    bad.write_text("[{\"name\": \"x\", \"cpi_vector\": 1}]", encoding="utf-8")
    with pytest.raises(ValueError, match="expected a list of >="):
        cpi_components.load_mapping(mapping_path=bad)


def test_load_mapping_rejects_missing_required_keys(tmp_path):
    entries = [{"name": f"Component {i}"} for i in range(60)]  # missing cpi_vector
    bad = tmp_path / "missing_keys.json"
    import json

    bad.write_text(json.dumps(entries), encoding="utf-8")
    with pytest.raises(ValueError, match="missing required key"):
        cpi_components.load_mapping(mapping_path=bad)
