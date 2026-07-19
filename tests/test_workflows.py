"""Workflow CRUD endpoint tests."""

import pytest


WORKFLOW_PAYLOAD = {
    "name": "Test Email Triage",
    "description": "Triages incoming emails using Claude",
    "status": "draft",
    "trigger_type": "email",
    "tags": ["email", "ai"],
    "steps": [
        {"step": 1, "name": "Gmail Trigger", "type": "gmail_trigger"},
        {"step": 2, "name": "Classify", "type": "claude_classify"},
        {"step": 3, "name": "Route", "type": "condition"},
    ],
}


@pytest.mark.asyncio
async def test_list_workflows_empty(client):
    response = await client.get("/api/v1/workflows")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "meta" in data


@pytest.mark.asyncio
async def test_create_workflow(client):
    response = await client.post("/api/v1/workflows", json=WORKFLOW_PAYLOAD)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == WORKFLOW_PAYLOAD["name"]
    assert data["status"] == "draft"
    assert data["trigger_type"] == "email"
    assert "id" in data
    return data["id"]


@pytest.mark.asyncio
async def test_get_workflow(client):
    # Create first
    create_resp = await client.post("/api/v1/workflows", json=WORKFLOW_PAYLOAD)
    wf_id = create_resp.json()["id"]

    response = await client.get(f"/api/v1/workflows/{wf_id}")
    assert response.status_code == 200
    assert response.json()["id"] == wf_id


@pytest.mark.asyncio
async def test_get_workflow_not_found(client):
    response = await client.get("/api/v1/workflows/nonexistent-id")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_workflow(client):
    create_resp = await client.post("/api/v1/workflows", json=WORKFLOW_PAYLOAD)
    wf_id = create_resp.json()["id"]

    response = await client.put(f"/api/v1/workflows/{wf_id}", json={"status": "active", "name": "Updated Name"})
    assert response.status_code == 200
    assert response.json()["status"] == "active"
    assert response.json()["name"] == "Updated Name"


@pytest.mark.asyncio
async def test_execute_workflow(client):
    create_resp = await client.post("/api/v1/workflows", json=WORKFLOW_PAYLOAD)
    wf_id = create_resp.json()["id"]

    response = await client.post(f"/api/v1/workflows/{wf_id}/execute", json={"test_input": "hello"})
    assert response.status_code == 200
    data = response.json()
    assert "execution_id" in data
    assert data["workflow_id"] == wf_id
    assert data["status"] in ("success", "failed", "pending")


@pytest.mark.asyncio
async def test_delete_workflow(client):
    create_resp = await client.post("/api/v1/workflows", json=WORKFLOW_PAYLOAD)
    wf_id = create_resp.json()["id"]

    del_resp = await client.delete(f"/api/v1/workflows/{wf_id}")
    assert del_resp.status_code == 204

    get_resp = await client.get(f"/api/v1/workflows/{wf_id}")
    assert get_resp.status_code == 404
