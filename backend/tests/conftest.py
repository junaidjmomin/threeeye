"""Test fixtures for the Third Eye backend."""
import asyncio
import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def auth_headers(client):
    """Return Authorization headers for a logged-in admin user."""
    resp = await client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "admin"},
    )
    if resp.status_code == 200:
        token = resp.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    return {}


@pytest.fixture
async def seeded_vendor(client, auth_headers):
    """Create and return a test vendor."""
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
    if resp.status_code in (200, 201):
        return resp.json()
    list_resp = await client.get("/api/v1/vendors", headers=auth_headers)
    if list_resp.status_code == 200 and list_resp.json():
        return list_resp.json()[0]
    return {"id": "test-id", "name": "Test Vendor"}


@pytest.fixture
async def seeded_alert(client, auth_headers, seeded_vendor):
    """Return the first alert or a placeholder."""
    resp = await client.get("/api/v1/alerts", headers=auth_headers)
    if resp.status_code == 200 and resp.json():
        return resp.json()[0]
    return {"id": "test-alert-id", "status": "new", "severity": "high"}


@pytest.fixture
async def seeded_workflow(client, auth_headers, seeded_vendor):
    """Create and return a test workflow item."""
    resp = await client.post(
        "/api/v1/workflows",
        json={
            "vendorId": seeded_vendor["id"],
            "title": "Test workflow",
            "description": "Test",
            "priority": "medium",
        },
        headers=auth_headers,
    )
    if resp.status_code in (200, 201):
        return resp.json()
    list_resp = await client.get("/api/v1/workflows", headers=auth_headers)
    if list_resp.status_code == 200 and list_resp.json():
        return list_resp.json()[0]
    return {"id": "test-wf-id", "status": "open"}
