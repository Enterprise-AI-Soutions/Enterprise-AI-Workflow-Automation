"""n8n integration router."""

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.integrations import n8n_service

router = APIRouter(prefix="/n8n", tags=["n8n"])


class TriggerWebhookRequest(BaseModel):
    webhook_path: str
    payload: dict = {}


class ActivateWorkflowRequest(BaseModel):
    active: bool = True


@router.get("/workflows", summary="List n8n workflows")
async def list_n8n_workflows():
    workflows = await n8n_service.list_workflows()
    return {"workflows": workflows, "count": len(workflows), "demo_mode": not n8n_service.enabled}


@router.post("/trigger", summary="Trigger an n8n webhook")
async def trigger_webhook(request: TriggerWebhookRequest):
    result = await n8n_service.trigger_webhook(request.webhook_path, request.payload)
    return {**result, "demo_mode": not n8n_service.enabled}


@router.get("/executions/{execution_id}", summary="Get n8n execution status")
async def get_n8n_execution(execution_id: str):
    result = await n8n_service.get_execution(execution_id)
    return {**result, "demo_mode": not n8n_service.enabled}


@router.patch("/workflows/{workflow_id}/activate", summary="Activate/deactivate n8n workflow")
async def activate_workflow(workflow_id: str, request: ActivateWorkflowRequest):
    result = await n8n_service.activate_workflow(workflow_id, active=request.active)
    return {**result, "demo_mode": not n8n_service.enabled}


@router.get("/status", summary="n8n integration status")
async def n8n_status():
    return {
        "enabled": n8n_service.enabled,
        "base_url": n8n_service._base_url,
        "demo_mode": not n8n_service.enabled,
    }
