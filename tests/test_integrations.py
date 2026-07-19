"""Integration endpoint tests — all run in demo mode."""

import pytest


@pytest.mark.asyncio
async def test_google_status(client):
    resp = await client.get("/api/v1/google/status")
    assert resp.status_code == 200
    assert "enabled" in resp.json()


@pytest.mark.asyncio
async def test_gmail_list_messages(client):
    resp = await client.get("/api/v1/google/gmail/messages")
    assert resp.status_code == 200
    data = resp.json()
    assert "messages" in data
    assert isinstance(data["messages"], list)


@pytest.mark.asyncio
async def test_gmail_send_demo(client):
    resp = await client.post("/api/v1/google/gmail/send", json={
        "to": "test@example.com",
        "subject": "Test",
        "body": "Hello",
    })
    assert resp.status_code == 200
    assert "status" in resp.json()


@pytest.mark.asyncio
async def test_calendar_list_events(client):
    resp = await client.get("/api/v1/google/calendar/events")
    assert resp.status_code == 200
    assert "events" in resp.json()


@pytest.mark.asyncio
async def test_airtable_status(client):
    resp = await client.get("/api/v1/airtable/status")
    assert resp.status_code == 200
    assert "enabled" in resp.json()


@pytest.mark.asyncio
async def test_airtable_list_bases(client):
    resp = await client.get("/api/v1/airtable/bases")
    assert resp.status_code == 200
    assert "bases" in resp.json()


@pytest.mark.asyncio
async def test_n8n_status(client):
    resp = await client.get("/api/v1/n8n/status")
    assert resp.status_code == 200
    assert "enabled" in resp.json()


@pytest.mark.asyncio
async def test_n8n_list_workflows(client):
    resp = await client.get("/api/v1/n8n/workflows")
    assert resp.status_code == 200
    assert "workflows" in resp.json()
