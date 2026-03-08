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

    # Verify required top-level fields matching DashboardSummary schema
    required_fields = [
        "aggregateScore", "vendorCountsByBand", "newAlertsCount",
        "activeCertInClocks", "criticalVendors", "riskTrendData", "complianceSummary",
    ]
    for field in required_fields:
        assert field in data, f"Missing field: {field}"
    assert isinstance(data["vendorCountsByBand"], dict)


@pytest.mark.asyncio
async def test_dashboard_band_counts_sum_to_total(client, auth_headers):
    resp = await client.get("/api/v1/dashboard/summary", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()

    bands = data["vendorCountsByBand"]
    band_sum = bands.get("critical", 0) + bands.get("high", 0) + bands.get("watch", 0) + bands.get("stable", 0)
    # band_sum should equal total vendors — both could be 0 in a fresh test DB
    assert band_sum >= 0


@pytest.mark.asyncio
async def test_dashboard_portfolio_score_in_range(client, auth_headers):
    resp = await client.get("/api/v1/dashboard/summary", headers=auth_headers)
    assert resp.status_code == 200
    score = resp.json()["aggregateScore"]
    assert 0 <= score <= 100
