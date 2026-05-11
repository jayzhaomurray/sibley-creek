"""Tests for the Alberta Economic Dashboard fetcher. No live API calls."""

from __future__ import annotations

import re

import pandas as pd
import pytest

from pipeline.fetch import alberta


# A minimal payload matching the live shape observed on probe 2026-05-11.
# Note the trailing space on "Type " -- the parser must tolerate it.
SAMPLE_PAYLOAD = [
    {"Date": "2025-12-01T00:00:00", "Type ": "NatGas", "Unit": "$CDN/GJ", "Value": 2.71},
    {"Date": "2026-01-01T00:00:00", "Type ": "NatGas", "Unit": "$CDN/GJ", "Value": 2.46},
    {"Date": "2026-02-01T00:00:00", "Type ": "NatGas", "Unit": "$CDN/GJ", "Value": 1.95},
    # Simulated null-value row; should be dropped on parse.
    {"Date": "2026-03-01T00:00:00", "Type ": "NatGas", "Unit": "$CDN/GJ", "Value": None},
]


def test_fetch_dashboard_series_parses_observations(httpx_mock):
    httpx_mock.add_response(
        method="GET",
        url=re.compile(r"https://api\.economicdata\.alberta\.ca/api/data\?code=.*"),
        json=SAMPLE_PAYLOAD,
    )

    result = alberta.fetch_dashboard_series(alberta.NATURAL_GAS_UUID)

    # Null-value row dropped: 4 in -> 3 out.
    assert len(result.data) == 3
    assert list(result.data.columns) == ["date", "value"]
    # Monotonically increasing dates.
    assert (result.data["date"].diff().dropna() > pd.Timedelta(0)).all()
    # Round-trip a numeric value.
    assert result.data["value"].iloc[-1] == pytest.approx(1.95)
    # Units + label hoisted out of the first observation.
    assert result.units == "$CDN/GJ"
    assert result.type_label == "NatGas"
    assert result.series_code == alberta.NATURAL_GAS_UUID


def test_fetch_dashboard_series_raises_on_empty_payload(httpx_mock):
    httpx_mock.add_response(
        method="GET",
        url=re.compile(r"https://api\.economicdata\.alberta\.ca/api/data\?code=.*"),
        json=[],
    )
    with pytest.raises(ValueError, match="no rows"):
        alberta.fetch_dashboard_series("not-a-real-uuid")


def test_fetch_dashboard_series_raises_on_non_list_payload(httpx_mock):
    # If the API ever flips to a wrapped envelope we want to fail loud rather
    # than silently misparse. ValueError is the boundary signal.
    httpx_mock.add_response(
        method="GET",
        url=re.compile(r"https://api\.economicdata\.alberta\.ca/api/data\?code=.*"),
        json={"error": "unexpected envelope"},
    )
    with pytest.raises(ValueError, match="no rows"):
        alberta.fetch_dashboard_series("not-a-real-uuid")


def test_fetch_dashboard_series_raises_on_malformed_row(httpx_mock):
    httpx_mock.add_response(
        method="GET",
        url=re.compile(r"https://api\.economicdata\.alberta\.ca/api/data\?code=.*"),
        # Row 1 is a bare string instead of a dict -- not a valid observation.
        json=[{"Date": "2026-01-01T00:00:00", "Value": 1.0}, "not-a-dict"],
    )
    with pytest.raises(ValueError, match="not a dict"):
        alberta.fetch_dashboard_series("not-a-real-uuid")


def test_series_url_format():
    url = alberta.series_url(alberta.NATURAL_GAS_UUID)
    assert url == (
        "https://api.economicdata.alberta.ca/api/data"
        f"?code={alberta.NATURAL_GAS_UUID}"
    )


def test_fetch_natural_gas_price_uses_correct_uuid(httpx_mock):
    """Sanity check that the convenience wrapper dispatches to the right code."""
    httpx_mock.add_response(
        method="GET",
        url=re.compile(r"https://api\.economicdata\.alberta\.ca/api/data\?code=.*"),
        json=SAMPLE_PAYLOAD,
    )
    result = alberta.fetch_natural_gas_price()
    assert result.series_code == alberta.NATURAL_GAS_UUID
