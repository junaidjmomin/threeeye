"""Tests for authentication endpoints — login, JWT, RBAC."""
import pytest


@pytest.mark.asyncio
async def test_login_returns_token(client):
    """POST /api/v1/auth/login with valid credentials returns access_token."""
    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "admin@thirdeye.io", "password": "thirdeye_admin"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_invalid_credentials(client):
    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "admin@thirdeye.io", "password": "wrongpassword"},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_get_me_requires_auth(client):
    resp = await client.get("/api/v1/auth/me")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_get_me_with_valid_token(client, auth_headers):
    resp = await client.get("/api/v1/auth/me", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "username" in data or "email" in data


@pytest.mark.asyncio
async def test_protected_endpoint_requires_auth(client):
    resp = await client.get("/api/v1/vendors")
    assert resp.status_code == 401
