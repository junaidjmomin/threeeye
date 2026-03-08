"""Tests for workflow lifecycle endpoints."""
import pytest


@pytest.mark.asyncio
async def test_list_workflows(client, auth_headers):
    resp = await client.get("/api/v1/workflows", headers=auth_headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


@pytest.mark.asyncio
async def test_create_workflow(client, auth_headers, seeded_vendor):
    resp = await client.post(
        "/api/v1/workflows",
        json={
            "vendorId": seeded_vendor["id"],
            "title": "Investigate open ports",
            "description": "Shodan detected 3 high-risk open ports",
            "priority": "high",
        },
        headers=auth_headers,
    )
    assert resp.status_code in (200, 201)
    data = resp.json()
    assert data["title"] == "Investigate open ports"
    assert data["status"] == "open"


@pytest.mark.asyncio
async def test_update_workflow_status(client, auth_headers, seeded_workflow):
    wf_id = seeded_workflow["id"]
    resp = await client.patch(
        f"/api/v1/workflows/{wf_id}",
        json={"status": "in_progress", "assignedTo": "risk-team@bank.in"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "in_progress"


@pytest.mark.asyncio
async def test_complete_workflow(client, auth_headers, seeded_workflow):
    wf_id = seeded_workflow["id"]
    resp = await client.patch(
        f"/api/v1/workflows/{wf_id}",
        json={"status": "completed"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "completed"
