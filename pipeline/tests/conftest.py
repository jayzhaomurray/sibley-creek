"""Shared pytest fixtures for the pipeline tests.

We use pytest-httpx to mock the HTTP layer; no test ever hits a live API.
A live-API "smoke" check belongs in a separate scheduled CI job, not in unit tests.
"""

from __future__ import annotations

import pytest


# Re-export the httpx_mock fixture name so individual tests can simply request
# `httpx_mock` without importing the plugin explicitly. (pytest-httpx provides
# the fixture automatically once installed, but this file exists so future
# shared fixtures have a home.)


@pytest.fixture
def sample_statcan_payload():
    """A minimal but realistic StatCan WDS response for vector 41690914 (CPI SA)."""
    return [
        {
            "status": "SUCCESS",
            "object": {
                "responseStatusCode": 0,
                "productId": 1810000601,
                "coordinate": "2.1.0.0.0.0.0.0.0.0",
                "vectorId": 41690914,
                "vectorDataPoint": [
                    {
                        "refPer": "2026-01-01",
                        "refPer2": "",
                        "refPerRaw": "2026-01-01",
                        "refPerRaw2": "",
                        "value": 161.5,
                        "decimals": 1,
                        "scalarFactorCode": 0,
                        "symbolCode": 0,
                        "statusCode": 0,
                        "releaseTime": "2026-02-18T08:30",
                        "frequencyCode": 6,
                    },
                    {
                        "refPer": "2026-02-01",
                        "refPer2": "",
                        "refPerRaw": "2026-02-01",
                        "refPerRaw2": "",
                        "value": 161.8,
                        "decimals": 1,
                        "scalarFactorCode": 0,
                        "symbolCode": 0,
                        "statusCode": 0,
                        "releaseTime": "2026-03-18T08:30",
                        "frequencyCode": 6,
                    },
                    {
                        "refPer": "2026-03-01",
                        "refPer2": "",
                        "refPerRaw": "2026-03-01",
                        "refPerRaw2": "",
                        "value": None,
                        "decimals": 1,
                        "scalarFactorCode": 0,
                        "symbolCode": 1,
                        "statusCode": 1,
                        "releaseTime": "2026-04-15T08:30",
                        "frequencyCode": 6,
                    },
                ],
            },
        }
    ]


@pytest.fixture
def sample_valet_payload():
    """A minimal Valet observations response for the overnight-rate-target series."""
    return {
        "terms": {"url": "https://www.bankofcanada.ca/terms/"},
        "seriesDetail": {
            "STATIC_ATABLE_V39079": {
                "label": "Target for the overnight rate",
                "description": "Bank of Canada target for the overnight rate",
                "dimension": {"key": "d", "name": "date"},
            }
        },
        "observations": [
            {"d": "2024-12-31", "STATIC_ATABLE_V39079": {"v": "3.25"}},
            {"d": "2025-01-31", "STATIC_ATABLE_V39079": {"v": "3.00"}},
            {"d": "2025-02-28", "STATIC_ATABLE_V39079": {"v": "3.00"}},
            {"d": "2025-03-31", "STATIC_ATABLE_V39079": {"v": None}},  # gap; should be dropped
        ],
    }
