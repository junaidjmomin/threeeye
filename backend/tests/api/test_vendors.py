"""Tests for vendor CRUD endpoints."""
import pytest


@pytest.mark.asyncio
async def test_list_vendors_requires_auth(client):
    resp = await client.get("/api/v1/vendors")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_list_vendors(client, auth_headers):
    resp = await client.get("/api/v1/vendors", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_list_vendors_filter_by_band(client, auth_headers, seeded_vendor):
    resp = await client.get(
        "/api/v1/vendors",
        params={"band": "critical"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    vendors = resp.json()
    for v in vendors:
        assert v["riskBand"] == "critical"


@pytest.mark.asyncio
async def test_get_vendor_by_id(client, auth_headers, seeded_vendor):
    vendor_id = seeded_vendor["id"]
    resp = await client.get(f"/api/v1/vendors/{vendor_id}", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == vendor_id


@pytest.mark.asyncio
async def test_get_vendor_not_found(client, auth_headers):
    resp = await client.get(
        "/api/v1/vendors/00000000-0000-0000-0000-000000000000",
        headers=auth_headers,
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_create_vendor(client, auth_headers):
    resp = await client.post(
        "/api/v1/vendors",
        json={
            "name": "Test Vendor Ltd",
            "tier": "standard",
            "category": "Technology",
            "compositeScore": 65,
        },
        headers=auth_headers,
    )
    assert resp.status_code in (200, 201)
    data = resp.json()
    assert data["name"] == "Test Vendor Ltd"


@pytest.mark.asyncio
async def test_trigger_rescore(client, auth_headers, seeded_vendor):
    vendor_id = seeded_vendor["id"]
    resp = await client.post(
        f"/api/v1/vendors/{vendor_id}/rescore",
        headers=auth_headers,
    )
    assert resp.status_code in (200, 202)
