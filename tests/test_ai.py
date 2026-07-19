"""AI endpoint tests — all run in demo mode (no API key needed)."""

import pytest


@pytest.mark.asyncio
async def test_ai_status(client):
    response = await client.get("/api/v1/ai/status")
    assert response.status_code == 200
    data = response.json()
    assert "enabled" in data
    assert "demo_mode" in data


@pytest.mark.asyncio
async def test_ai_chat_demo_mode(client):
    response = await client.post("/api/v1/ai/chat", json={"message": "Hello, Claude!"})
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert isinstance(data["response"], str)
    assert len(data["response"]) > 0


@pytest.mark.asyncio
async def test_ai_summarize(client):
    response = await client.post("/api/v1/ai/summarize", json={
        "text": "This is a very long document about enterprise AI workflow automation. " * 10,
        "max_words": 100,
    })
    assert response.status_code == 200
    assert "summary" in response.json()


@pytest.mark.asyncio
async def test_ai_classify(client):
    response = await client.post("/api/v1/ai/classify", json={
        "text": "I need help with my invoice",
        "categories": ["Sales", "Support", "Finance", "Other"],
    })
    assert response.status_code == 200
    data = response.json()
    assert "category" in data
    assert data["category"] in ["Sales", "Support", "Finance", "Other", "demo"]


@pytest.mark.asyncio
async def test_ai_extract(client):
    response = await client.post("/api/v1/ai/extract", json={
        "text": "Customer: John Doe, Email: john@acme.com, Amount: $5000",
        "fields": ["customer_name", "email", "amount"],
    })
    assert response.status_code == 200
    data = response.json()
    assert "fields" in data


@pytest.mark.asyncio
async def test_ai_generate_workflow(client):
    response = await client.post("/api/v1/ai/generate-workflow", json={
        "description": "When a new email arrives, classify it and save to Airtable"
    })
    assert response.status_code == 200
    data = response.json()
    assert "steps" in data
    assert isinstance(data["steps"], list)
