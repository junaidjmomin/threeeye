"""Tests for dashboard summary aggregation endpoint."""
import pytest


@pytest.mark.asyncio
async def test_dashboard_summary_requires_auth(client):
    resp = await client.get("/api/v1/dashboard/summary")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_dashboard_summary_shape(client, auth_headers):
    resp = await client.get("/api/v1/dashboard/summary", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()

    # Verify required top-level fields
    required_fields = [
        "totalVendors", "criticalCount", "highCount",
        "watchCount", "stableCount", "openAlerts",
        "portfolioScore",
    ]
    for field in required_fields:
        assert field in data, f"Missing field: {field}"


@pytest.mark.asyncio
async def test_dashboard_band_counts_sum_to_total(client, auth_headers):
    resp = await client.get("/api/v1/dashboard/summary", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()

    total = data["totalVendors"]
    band_sum = (
        data["criticalCount"]
        + data["highCount"]
        + data["watchCount"]
        + data["stableCount"]
    )
    assert band_sum == total, f"Band counts {band_sum} != totalVendors {total}"


@pytest.mark.asyncio
async def test_dashboard_portfolio_score_in_range(client, auth_headers):
    resp = await client.get("/api/v1/dashboard/summary", headers=auth_headers)
    assert resp.status_code == 200
    score = resp.json()["portfolioScore"]
    assert 0 <= score <= 100
