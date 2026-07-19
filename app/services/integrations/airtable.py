"""Airtable integration service."""

from __future__ import annotations

from typing import Any, Optional

import httpx

from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

_AIRTABLE_BASE_URL = "https://api.airtable.com/v0"
_AIRTABLE_META_URL = "https://api.airtable.com/v0/meta"

_DEMO_RECORDS = [
    {"id": "rec001", "fields": {"Name": "Acme Corp", "Status": "Active", "Revenue": 50000}, "createdTime": "2025-07-01T00:00:00.000Z"},
    {"id": "rec002", "fields": {"Name": "Globex Ltd", "Status": "Lead", "Revenue": 0}, "createdTime": "2025-07-10T00:00:00.000Z"},
]
_DEMO_BASES = [{"id": "appDemoBase001", "name": "CRM Database", "permissionLevel": "create"}]


class AirtableService:
    """Wraps Airtable REST API v0. Falls back to demo data when API key is absent."""

    def __init__(self) -> None:
        self._api_key = settings.AIRTABLE_API_KEY
        self._base_id = settings.AIRTABLE_BASE_ID
        if self._api_key:
            logger.info("Airtable integration enabled (base=%s)", self._base_id or "not set")
        else:
            logger.info("AIRTABLE_API_KEY not set — Airtable running in demo mode")

    @property
    def enabled(self) -> bool:
        return bool(self._api_key)

    def _headers(self) -> dict:
        return {"Authorization": f"Bearer {self._api_key}", "Content-Type": "application/json"}

    # ── Bases ─────────────────────────────────────────────────────────────────

    async def list_bases(self) -> list[dict]:
        if not self.enabled:
            return _DEMO_BASES
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.get(f"{_AIRTABLE_META_URL}/bases", headers=self._headers())
                resp.raise_for_status()
                return resp.json().get("bases", [])
        except Exception as exc:
            logger.error("Airtable list_bases error: %s", exc)
            return _DEMO_BASES

    # ── Records ───────────────────────────────────────────────────────────────

    async def list_records(
        self,
        base_id: str,
        table_id: str,
        max_records: int = 100,
        filter_formula: Optional[str] = None,
    ) -> list[dict]:
        if not self.enabled:
            return _DEMO_RECORDS[:max_records]
        try:
            params: dict[str, Any] = {"maxRecords": max_records}
            if filter_formula:
                params["filterByFormula"] = filter_formula

            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.get(
                    f"{_AIRTABLE_BASE_URL}/{base_id}/{table_id}",
                    headers=self._headers(),
                    params=params,
                )
                resp.raise_for_status()
                return resp.json().get("records", [])
        except Exception as exc:
            logger.error("Airtable list_records error: %s", exc)
            return _DEMO_RECORDS[:max_records]

    async def create_record(self, base_id: str, table_id: str, fields: dict) -> dict:
        if not self.enabled:
            return {"id": "recDEMO_new", "fields": fields, "status": "demo"}
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.post(
                    f"{_AIRTABLE_BASE_URL}/{base_id}/{table_id}",
                    headers=self._headers(),
                    json={"fields": fields},
                )
                resp.raise_for_status()
                return resp.json()
        except Exception as exc:
            logger.error("Airtable create_record error: %s", exc)
            return {"status": "error", "message": str(exc)}

    async def update_record(self, base_id: str, table_id: str, record_id: str, fields: dict) -> dict:
        if not self.enabled:
            return {"id": record_id, "fields": fields, "status": "demo"}
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.patch(
                    f"{_AIRTABLE_BASE_URL}/{base_id}/{table_id}/{record_id}",
                    headers=self._headers(),
                    json={"fields": fields},
                )
                resp.raise_for_status()
                return resp.json()
        except Exception as exc:
            logger.error("Airtable update_record error: %s", exc)
            return {"status": "error", "message": str(exc)}

    async def delete_record(self, base_id: str, table_id: str, record_id: str) -> dict:
        if not self.enabled:
            return {"id": record_id, "deleted": True, "status": "demo"}
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.delete(
                    f"{_AIRTABLE_BASE_URL}/{base_id}/{table_id}/{record_id}",
                    headers=self._headers(),
                )
                resp.raise_for_status()
                return resp.json()
        except Exception as exc:
            logger.error("Airtable delete_record error: %s", exc)
            return {"status": "error", "message": str(exc)}


# Singleton
airtable_service = AirtableService()
