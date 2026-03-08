"""Tests for alert status transitions."""
import pytest


@pytest.mark.asyncio
async def test_list_alerts(client, auth_headers):
    resp = await client.get("/api/v1/alerts", headers=auth_headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


@pytest.mark.asyncio
async def test_list_alerts_filter_by_severity(client, auth_headers):
    resp = await client.get(
        "/api/v1/alerts",
        params={"severity": "critical"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    for alert in resp.json():
        assert alert["severity"] == "critical"


@pytest.mark.asyncio
async def test_update_alert_status(client, auth_headers, seeded_alert):
    alert_id = seeded_alert["id"]
    resp = await client.patch(
        f"/api/v1/alerts/{alert_id}/status",
        json={"status": "acknowledged"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "acknowledged"


@pytest.mark.asyncio
async def test_alert_status_progression(client, auth_headers, seeded_alert):
    """new → acknowledged → assigned → resolved."""
    alert_id = seeded_alert["id"]
    for status in ("acknowledged", "assigned", "resolved"):
        resp = await client.patch(
            f"/api/v1/alerts/{alert_id}/status",
            json={"status": status},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == status


@pytest.mark.asyncio
async def test_alert_invalid_status(client, auth_headers, seeded_alert):
    alert_id = seeded_alert["id"]
    resp = await client.patch(
        f"/api/v1/alerts/{alert_id}/status",
        json={"status": "invalid_status"},
        headers=auth_headers,
    )
    assert resp.status_code == 422
