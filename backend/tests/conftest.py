"""Test fixtures for the Third Eye backend."""
import asyncio

import pytest
from httpx import ASGITransport, AsyncClient


def _run(coro):
    """Run a coroutine in a new event loop (safe to call outside async context)."""
    return asyncio.run(coro)


async def _setup_db():
    """Create tables and seed admin user once before any tests run."""
    from sqlalchemy import select

    import app.models  # noqa: F401 — registers all models with Base.metadata
    from app.core.database import Base, async_session_factory, engine
    from app.core.security import hash_password
    from app.models.user import User

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_factory() as session:
        result = await session.execute(select(User).where(User.email == "admin@thirdeye.io"))
        if result.scalar_one_or_none() is None:
            admin = User(
                email="admin@thirdeye.io",
                hashed_password=hash_password("thirdeye_admin"),
                full_name="Test Admin",
                role="admin",
                is_active=True,
            )
            session.add(admin)
            await session.commit()


def pytest_sessionstart(session):
    """Create DB schema and seed data before any test runs."""
    _run(_setup_db())


@pytest.fixture
async def client():
    from app.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def auth_headers(client):
    """Return Authorization headers for a logged-in admin user."""
    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "admin@thirdeye.io", "password": "thirdeye_admin"},
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
