"""Tests for the CPI basket-weights fetcher. No live API calls."""

from __future__ import annotations

import math

import pandas as pd
import pytest

from pipeline.fetch import cpi_basket, statcan


def _mk_payload(vector_id: int, points: list[tuple[str, float | None]]) -> dict:
    """Helper: build one WDS response item for a vector."""
    return {
        "status": "SUCCESS",
        "object": {
            "responseStatusCode": 0,
            "productId": 1810000701,
            "vectorId": vector_id,
            "vectorDataPoint": [
                {
                    "refPer": d,
                    "value": v,
                    "decimals": 2,
                    "scalarFactorCode": 0,
                    "symbolCode": 0,
                    "statusCode": 0,
                    "releaseTime": "2025-05-16T08:30",
                    "frequencyCode": 18,
                }
                for d, v in points
            ],
        },
    }


def test_major_aggregates_table_is_complete():
    """All editorial-canonical major aggregates have wired vectors."""
    expected = {
        "all_items",
        "food",
        "shelter",
        "energy",
        "goods",
        "services",
        "goods_ex_food_energy",
        "all_items_ex_food_energy",
        "all_items_ex_shelter",
    }
    assert expected.issubset(set(cpi_basket.MAJOR_AGGREGATES))
    # No accidental duplicate vector IDs.
    vids = list(cpi_basket.MAJOR_AGGREGATES.values())
    assert len(vids) == len(set(vids))


def test_fetch_basket_weights_pivots_to_wide_and_preserves_nan(httpx_mock):
    # Build a stub WDS response for every wired aggregate. One aggregate
    # (goods) gets a NaN observation in the latest basket to verify the
    # parser preserves it through to the wide pivot.
    points_2023 = ("2023-01-01", 50.0)
    points_2024 = ("2024-01-01", 51.0)
    points_2024_nan = ("2024-01-01", None)

    payload = []
    for slug, vid in cpi_basket.MAJOR_AGGREGATES.items():
        pts = [points_2023, points_2024_nan if slug == "goods" else points_2024]
        payload.append(_mk_payload(vid, pts))

    httpx_mock.add_response(
        method="POST",
        url=statcan.ENDPOINT_LATEST_N,
        json=payload,
    )

    result = cpi_basket.fetch_basket_weights()

    # long-format: 9 aggregates x 2 cycles = 18 rows
    assert len(result.long) == 2 * len(cpi_basket.MAJOR_AGGREGATES)
    assert set(result.long.columns) == {"date", "aggregate", "weight_pct"}

    # wide: one row per basket cycle, one column per aggregate
    assert len(result.wide) == 2
    assert "date" in result.wide.columns
    for slug in cpi_basket.MAJOR_AGGREGATES:
        assert slug in result.wide.columns

    # NaN preservation: goods 2024-01-01 is NaN
    g2024 = result.wide.loc[
        result.wide["date"] == pd.Timestamp("2024-01-01"), "goods"
    ].iloc[0]
    assert math.isnan(g2024)

    # release_date: max releaseTime across vectors -> 2025-05-16
    assert result.release_date == "2025-05-16"


def test_fetch_basket_weights_rejects_unknown_aggregate():
    with pytest.raises(ValueError, match="Unknown basket aggregate"):
        cpi_basket.fetch_basket_weights(aggregates=["not_a_real_slug"])


def test_fetch_basket_weights_subset(httpx_mock):
    """Caller can request a subset; only those vectors are pulled."""
    subset = ["food", "shelter", "energy"]
    payload = [
        _mk_payload(cpi_basket.MAJOR_AGGREGATES[s], [("2024-01-01", 17.0 if s == "food" else 29.0 if s == "shelter" else 6.0)])
        for s in subset
    ]
    httpx_mock.add_response(
        method="POST",
        url=statcan.ENDPOINT_LATEST_N,
        json=payload,
    )

    result = cpi_basket.fetch_basket_weights(aggregates=subset)

    assert set(result.long["aggregate"]) == set(subset)
    # wide has exactly the subset columns plus date
    assert set(result.wide.columns) == {"date"} | set(subset)
