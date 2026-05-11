"""Tests for the StatCan WDS client. No live API calls."""

from __future__ import annotations

import math

import pandas as pd
import pytest

from pipeline.fetch import statcan


def test_fetch_vector_parses_observations(httpx_mock, sample_statcan_payload):
    httpx_mock.add_response(
        method="POST",
        url=statcan.ENDPOINT_LATEST_N,
        json=sample_statcan_payload,
    )

    result = statcan.fetch_vector(41690914, latest_n=600)

    assert result.vector_id == 41690914
    # NaN-preserving: 3 input observations -> 3 output rows
    assert len(result.data) == 3
    assert list(result.data.columns) == ["date", "value"]
    # Dates sorted ascending
    assert (result.data["date"].diff().dropna() > pd.Timedelta(0)).all()
    # NaN preserved for the gap observation
    assert math.isnan(result.data["value"].iloc[-1])
    # Real values preserved
    assert result.data["value"].iloc[0] == pytest.approx(161.5)
    # release_date pinned from the most-recent observation's releaseTime
    assert result.release_date == "2026-04-15"


def test_fetch_vector_raises_on_non_success(httpx_mock):
    httpx_mock.add_response(
        method="POST",
        url=statcan.ENDPOINT_LATEST_N,
        json=[{"status": "INVALID_VECTOR_ID"}],
    )
    with pytest.raises(ValueError, match="StatCan WDS error"):
        statcan.fetch_vector(999999999)


def test_fetch_vectors_batches_request(httpx_mock):
    httpx_mock.add_response(
        method="POST",
        url=statcan.ENDPOINT_LATEST_N,
        json=[
            {
                "status": "SUCCESS",
                "object": {
                    "vectorId": 1,
                    "vectorDataPoint": [
                        {"refPer": "2025-01-01", "value": 10.0},
                    ],
                },
            },
            {
                "status": "SUCCESS",
                "object": {
                    "vectorId": 2,
                    "vectorDataPoint": [
                        {"refPer": "2025-01-01", "value": 20.0},
                    ],
                },
            },
        ],
    )

    results = statcan.fetch_vectors([1, 2], latest_n=10)

    assert set(results) == {1, 2}
    assert results[1].data["value"].iloc[0] == 10.0
    assert results[2].data["value"].iloc[0] == 20.0


def test_table_url_strips_dashes():
    # StatCan's tv.action URL uses the bare table ID without the trailing -01 suffix:
    # table 18-10-0006-01 -> pid=1810000601
    url = statcan.table_url("18-10-0006-01")
    assert url == "https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1810000601"
