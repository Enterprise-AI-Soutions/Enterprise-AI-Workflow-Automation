"""Google Sheets endpoint tests — run in demo mode without credentials."""

import pytest


@pytest.mark.asyncio
async def test_sheets_status(client):
    resp = await client.get("/api/v1/google/sheets/status")
    assert resp.status_code == 200
    data = resp.json()
    assert "enabled" in data
    assert "demo_mode" in data


@pytest.mark.asyncio
async def test_list_spreadsheets(client):
    resp = await client.get("/api/v1/google/sheets")
    assert resp.status_code == 200
    data = resp.json()
    assert "spreadsheets" in data
    assert isinstance(data["spreadsheets"], list)
    assert data["count"] == len(data["spreadsheets"])


@pytest.mark.asyncio
async def test_create_spreadsheet(client):
    resp = await client.post("/api/v1/google/sheets", json={
        "title": "Test Spreadsheet",
        "sheet_names": ["Data", "Logs"],
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "spreadsheetId" in data
    assert "spreadsheetUrl" in data


@pytest.mark.asyncio
async def test_get_spreadsheet(client):
    resp = await client.get("/api/v1/google/sheets/demo_spreadsheet_001")
    assert resp.status_code == 200
    data = resp.json()
    assert "spreadsheetId" in data
    assert "sheets" in data
    assert isinstance(data["sheets"], list)


@pytest.mark.asyncio
async def test_read_values(client):
    resp = await client.get("/api/v1/google/sheets/demo_spreadsheet_001/values/Sheet1!A1:E10")
    assert resp.status_code == 200
    data = resp.json()
    assert "values" in data
    assert "headers" in data
    assert isinstance(data["values"], list)


@pytest.mark.asyncio
async def test_write_values(client):
    resp = await client.put(
        "/api/v1/google/sheets/demo_spreadsheet_001/values/Sheet1!A1",
        json={
            "values": [
                ["Name", "Email", "Status"],
                ["Alice", "alice@test.com", "Active"],
            ]
        }
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "updatedRows" in data


@pytest.mark.asyncio
async def test_append_rows(client):
    resp = await client.post(
        "/api/v1/google/sheets/demo_spreadsheet_001/append",
        json={"values": [["New User", "new@test.com", "Lead"]]}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "updates" in data or "status" in data


@pytest.mark.asyncio
async def test_clear_range(client):
    resp = await client.delete("/api/v1/google/sheets/demo_spreadsheet_001/values/Sheet1!A5:E10")
    assert resp.status_code == 200
    data = resp.json()
    assert "clearedRange" in data or "status" in data


@pytest.mark.asyncio
async def test_batch_read(client):
    resp = await client.post(
        "/api/v1/google/sheets/demo_spreadsheet_001/batch-read",
        json={"ranges": ["Sheet1!A1:C5", "Leads!A:D"]}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "ranges" in data
    assert isinstance(data["ranges"], list)


@pytest.mark.asyncio
async def test_ai_fill(client):
    resp = await client.post(
        "/api/v1/google/sheets/demo_spreadsheet_001/ai-fill",
        json={
            "headers": ["Name", "Email", "Company"],
            "prompt": "B2B SaaS leads",
            "rows": 3,
        }
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "rows_written" in data
    assert "headers" in data


@pytest.mark.asyncio
async def test_format_headers(client):
    resp = await client.post(
        "/api/v1/google/sheets/demo_spreadsheet_001/format-headers",
        params={"sheet_id": 0}
    )
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_health_includes_sheets(client):
    """Health check should now include google_sheets integration status."""
    resp = await client.get("/api/v1/health")
    assert resp.status_code == 200
    data = resp.json()
    assert "google_sheets" in data["integrations"]
    assert "enabled" in data["integrations"]["google_sheets"]
