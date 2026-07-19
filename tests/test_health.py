"""Health endpoint tests."""

import pytest


@pytest.mark.asyncio
async def test_health_returns_200(client):
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "integrations" in data
    assert "claude_ai" in data["integrations"]
    assert "google_workspace" in data["integrations"]
    assert "airtable" in data["integrations"]
    assert "n8n" in data["integrations"]


@pytest.mark.asyncio
async def test_ping(client):
    response = await client.get("/api/v1/health/ping")
    assert response.status_code == 200
    assert response.json() == {"ping": "pong"}
