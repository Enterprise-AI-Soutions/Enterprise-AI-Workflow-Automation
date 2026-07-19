"""Airtable router."""

from typing import Optional

from fastapi import APIRouter, Query
from pydantic import BaseModel

from app.services.integrations import airtable_service
from app.config import settings

router = APIRouter(prefix="/airtable", tags=["Airtable"])


class CreateRecordRequest(BaseModel):
    fields: dict


class UpdateRecordRequest(BaseModel):
    fields: dict


@router.get("/bases", summary="List Airtable bases")
async def list_bases():
    bases = await airtable_service.list_bases()
    return {"bases": bases, "demo_mode": not airtable_service.enabled}


@router.get("/bases/{base_id}/tables/{table_id}/records", summary="List records in a table")
async def list_records(
    base_id: str,
    table_id: str,
    max_records: int = Query(100, ge=1, le=1000),
    filter_formula: Optional[str] = Query(None),
):
    records = await airtable_service.list_records(
        base_id=base_id, table_id=table_id, max_records=max_records, filter_formula=filter_formula
    )
    return {"records": records, "count": len(records), "demo_mode": not airtable_service.enabled}


@router.post("/bases/{base_id}/tables/{table_id}/records", summary="Create a record")
async def create_record(base_id: str, table_id: str, request: CreateRecordRequest):
    result = await airtable_service.create_record(base_id=base_id, table_id=table_id, fields=request.fields)
    return {**result, "demo_mode": not airtable_service.enabled}


@router.patch("/bases/{base_id}/tables/{table_id}/records/{record_id}", summary="Update a record")
async def update_record(base_id: str, table_id: str, record_id: str, request: UpdateRecordRequest):
    result = await airtable_service.update_record(
        base_id=base_id, table_id=table_id, record_id=record_id, fields=request.fields
    )
    return {**result, "demo_mode": not airtable_service.enabled}


@router.delete("/bases/{base_id}/tables/{table_id}/records/{record_id}", summary="Delete a record")
async def delete_record(base_id: str, table_id: str, record_id: str):
    result = await airtable_service.delete_record(base_id=base_id, table_id=table_id, record_id=record_id)
    return {**result, "demo_mode": not airtable_service.enabled}


@router.get("/status", summary="Airtable integration status")
async def airtable_status():
    return {
        "enabled": airtable_service.enabled,
        "configured_base": settings.AIRTABLE_BASE_ID,
        "demo_mode": not airtable_service.enabled,
    }
