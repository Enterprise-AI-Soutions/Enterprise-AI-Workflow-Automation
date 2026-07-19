"""n8n workflow automation integration."""

from __future__ import annotations

from typing import Any, Optional

import httpx

from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

_DEMO_WORKFLOWS = [
    {"id": "1", "name": "Email Triage", "active": True, "tags": ["email", "ai"]},
    {"id": "2", "name": "Invoice Processing", "active": True, "tags": ["finance", "ai"]},
    {"id": "3", "name": "Meeting Scheduler", "active": False, "tags": ["calendar"]},
]


class N8NService:
    """Triggers and monitors n8n workflows via REST API. Falls back to demo mode if n8n is unavailable."""

    def __init__(self) -> None:
        self._base_url = settings.N8N_BASE_URL.rstrip("/")
        self._api_key = settings.N8N_API_KEY
        if self._api_key:
            logger.info("n8n integration enabled (url=%s)", self._base_url)
        else:
            logger.info("N8N_API_KEY not set — n8n running in demo mode")

    @property
    def enabled(self) -> bool:
        return bool(self._api_key)

    def _headers(self) -> dict:
        return {"X-N8N-API-KEY": self._api_key, "Content-Type": "application/json"}

    async def list_workflows(self) -> list[dict]:
        if not self.enabled:
            return _DEMO_WORKFLOWS
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(f"{self._base_url}/api/v1/workflows", headers=self._headers())
                resp.raise_for_status()
                return resp.json().get("data", [])
        except Exception as exc:
            logger.error("n8n list_workflows error: %s", exc)
            return _DEMO_WORKFLOWS

    async def trigger_webhook(self, webhook_path: str, payload: dict) -> dict:
        """POST to an n8n webhook URL."""
        url = f"{self._base_url}/webhook/{webhook_path}"
        if not self.enabled:
            return {"status": "demo", "message": f"Would POST to {url}", "payload": payload}
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.post(url, json=payload)
                resp.raise_for_status()
                return {"status": "triggered", "response": resp.json()}
        except Exception as exc:
            logger.error("n8n trigger_webhook error: %s", exc)
            return {"status": "error", "message": str(exc)}

    async def get_execution(self, execution_id: str) -> dict:
        if not self.enabled:
            return {"id": execution_id, "status": "demo", "data": {}}
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(
                    f"{self._base_url}/api/v1/executions/{execution_id}",
                    headers=self._headers(),
                )
                resp.raise_for_status()
                return resp.json()
        except Exception as exc:
            logger.error("n8n get_execution error: %s", exc)
            return {"status": "error", "message": str(exc)}

    async def activate_workflow(self, workflow_id: str, active: bool = True) -> dict:
        if not self.enabled:
            return {"status": "demo", "workflowId": workflow_id, "active": active}
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.patch(
                    f"{self._base_url}/api/v1/workflows/{workflow_id}",
                    headers=self._headers(),
                    json={"active": active},
                )
                resp.raise_for_status()
                return resp.json()
        except Exception as exc:
            logger.error("n8n activate_workflow error: %s", exc)
            return {"status": "error", "message": str(exc)}


# Singleton
n8n_service = N8NService()
