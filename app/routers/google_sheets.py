"""Google Sheets router."""

from __future__ import annotations

from typing import Any, List, Optional

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from app.services.integrations.google_sheets import google_sheets_service
from app.services.ai import claude_service

router = APIRouter(prefix="/google/sheets", tags=["Google Sheets"])


# ── Schemas ───────────────────────────────────────────────────────────────────

class WriteValuesRequest(BaseModel):
    values: List[List[Any]] = Field(..., description="2D array of cell values")
    value_input_option: str = Field("USER_ENTERED", description="USER_ENTERED | RAW")


class AppendRowsRequest(BaseModel):
    values: List[List[Any]] = Field(..., description="Rows to append")
    value_input_option: str = Field("USER_ENTERED")


class CreateSpreadsheetRequest(BaseModel):
    title: str = Field(..., min_length=1, description="Spreadsheet title")
    sheet_names: Optional[List[str]] = Field(None, description="Optional list of sheet tab names")


class BatchReadRequest(BaseModel):
    ranges: List[str] = Field(..., min_length=1, description="List of A1 notation ranges")


class BatchUpdateRequest(BaseModel):
    requests: List[dict] = Field(..., description="Raw Sheets API batchUpdate request objects")


class AiFillRequest(BaseModel):
    prompt: str = Field(..., min_length=5, description="Describe what data to generate")
    rows: int = Field(5, ge=1, le=50, description="Number of data rows to generate")
    headers: List[str] = Field(..., min_length=1, description="Column headers for the generated data")


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("", summary="List spreadsheets from Drive")
async def list_spreadsheets(max_results: int = Query(20, ge=1, le=100)):
    """List all Google Sheets files accessible in Drive."""
    sheets = await google_sheets_service.list_spreadsheets(max_results=max_results)
    return {"spreadsheets": sheets, "count": len(sheets), "demo_mode": not google_sheets_service.enabled}


@router.post("", summary="Create a new spreadsheet")
async def create_spreadsheet(request: CreateSpreadsheetRequest):
    """Create a new Google Sheets spreadsheet."""
    result = await google_sheets_service.create_spreadsheet(
        title=request.title, sheet_names=request.sheet_names
    )
    return {**result, "demo_mode": not google_sheets_service.enabled}


@router.get("/{spreadsheet_id}", summary="Get spreadsheet metadata")
async def get_spreadsheet(spreadsheet_id: str):
    """Get spreadsheet info including all sheet tab names."""
    result = await google_sheets_service.get_spreadsheet(spreadsheet_id)
    sheets = [
        {"sheetId": s["properties"]["sheetId"], "title": s["properties"]["title"]}
        for s in result.get("sheets", [])
    ]
    return {
        "spreadsheetId": result.get("spreadsheetId"),
        "title": result.get("properties", {}).get("title"),
        "url": result.get("spreadsheetUrl"),
        "sheets": sheets,
        "demo_mode": not google_sheets_service.enabled,
    }


@router.get("/{spreadsheet_id}/values/{range_notation:path}", summary="Read values from a range")
async def read_values(
    spreadsheet_id: str,
    range_notation: str,
    value_render_option: str = Query("FORMATTED_VALUE", description="FORMATTED_VALUE | UNFORMATTED_VALUE | FORMULA"),
):
    """Read cell values from a range. Use A1 notation e.g. `Sheet1!A1:E10`"""
    result = await google_sheets_service.read_values(
        spreadsheet_id, range_notation, value_render_option=value_render_option
    )
    rows = result.get("values", [])
    headers = rows[0] if rows else []
    data_rows = rows[1:] if len(rows) > 1 else []
    return {
        **result,
        "row_count": len(rows),
        "column_count": len(headers),
        "headers": headers,
        "data_rows": data_rows,
        "demo_mode": not google_sheets_service.enabled,
    }


@router.post("/{spreadsheet_id}/batch-read", summary="Read multiple ranges at once")
async def batch_read(spreadsheet_id: str, request: BatchReadRequest):
    """Read multiple A1 notation ranges in a single API call."""
    result = await google_sheets_service.batch_read(spreadsheet_id, request.ranges)
    return {"spreadsheetId": spreadsheet_id, "ranges": result, "demo_mode": not google_sheets_service.enabled}


@router.put("/{spreadsheet_id}/values/{range_notation:path}", summary="Write values to a range")
async def write_values(spreadsheet_id: str, range_notation: str, request: WriteValuesRequest):
    """Overwrite cells in the specified range."""
    result = await google_sheets_service.write_values(
        spreadsheet_id, range_notation, request.values, request.value_input_option
    )
    return {**result, "demo_mode": not google_sheets_service.enabled}


@router.post("/{spreadsheet_id}/append", summary="Append rows to a sheet")
async def append_rows(spreadsheet_id: str, request: AppendRowsRequest):
    """Append new rows to the end of a table in the spreadsheet."""
    result = await google_sheets_service.append_rows(
        spreadsheet_id, "Sheet1", request.values, request.value_input_option
    )
    return {**result, "demo_mode": not google_sheets_service.enabled}


@router.delete("/{spreadsheet_id}/values/{range_notation:path}", summary="Clear a range")
async def clear_range(spreadsheet_id: str, range_notation: str):
    """Clear all values in the specified range (keeps formatting)."""
    result = await google_sheets_service.clear_range(spreadsheet_id, range_notation)
    return {**result, "demo_mode": not google_sheets_service.enabled}


@router.post("/{spreadsheet_id}/format-headers", summary="Format header row")
async def format_header_row(spreadsheet_id: str, sheet_id: int = Query(0)):
    """Apply bold styling and frozen row to the first row of a sheet."""
    result = await google_sheets_service.format_header_row(spreadsheet_id, sheet_id=sheet_id)
    return {**result, "demo_mode": not google_sheets_service.enabled}


@router.post("/{spreadsheet_id}/add-sheet", summary="Add a new sheet tab")
async def add_sheet(spreadsheet_id: str, sheet_title: str = Query(...)):
    """Add a new sheet tab to an existing spreadsheet."""
    result = await google_sheets_service.add_sheet(spreadsheet_id, sheet_title)
    return {**result, "demo_mode": not google_sheets_service.enabled}


@router.post("/{spreadsheet_id}/batch-update", summary="Raw Sheets batchUpdate")
async def batch_update(spreadsheet_id: str, request: BatchUpdateRequest):
    """Send raw Sheets API batchUpdate requests (for advanced formatting, merges, etc.)."""
    result = await google_sheets_service.batch_update(spreadsheet_id, request.requests)
    return {**result, "demo_mode": not google_sheets_service.enabled}


@router.post("/{spreadsheet_id}/ai-fill", summary="AI-generate sheet data")
async def ai_fill(spreadsheet_id: str, request: AiFillRequest):
    """
    Use Claude AI to generate structured tabular data and write it into the spreadsheet.
    Useful for creating seed data, test datasets, or report templates.
    """
    system_prompt = (
        "You are a data generation assistant. Generate realistic, varied tabular data. "
        "Return ONLY a JSON array of arrays (rows). No headers, no explanation, no code fences. "
        "Each inner array must have exactly the same number of elements as the headers provided."
    )

    user_message = (
        f"Generate {request.rows} rows of realistic data for a spreadsheet with these columns: "
        f"{', '.join(request.headers)}.\n"
        f"Context: {request.prompt}\n"
        f"Return a JSON array of {request.rows} arrays, each with {len(request.headers)} values."
    )

    import json

    raw = await claude_service.chat(user_message, system_prompt=system_prompt)
    try:
        # Try to parse Claude's response as JSON
        data_rows = json.loads(raw)
        if not isinstance(data_rows, list):
            raise ValueError("Not a list")
    except Exception:
        # Fallback: generate placeholder data
        data_rows = [
            [f"Sample {i+1} - {h}" for h in request.headers]
            for i in range(request.rows)
        ]

    # Write headers + data to the spreadsheet
    all_values = [request.headers] + data_rows
    write_result = await google_sheets_service.write_values(
        spreadsheet_id, "Sheet1!A1", all_values
    )

    # Apply header formatting
    await google_sheets_service.format_header_row(spreadsheet_id, sheet_id=0)

    return {
        "spreadsheetId": spreadsheet_id,
        "headers": request.headers,
        "rows_written": len(data_rows),
        "write_result": write_result,
        "demo_mode": not google_sheets_service.enabled,
        "ai_demo_mode": not claude_service.enabled,
    }


@router.get("/status", summary="Google Sheets integration status")
async def sheets_status():
    return {
        "enabled": google_sheets_service.enabled,
        "demo_mode": not google_sheets_service.enabled,
    }
