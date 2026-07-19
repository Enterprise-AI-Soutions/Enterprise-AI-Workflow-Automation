"""Workflow CRUD and execution router."""

from typing import Optional

from fastapi import APIRouter, Query, status
from fastapi.responses import JSONResponse

from app.api.deps import DBSession
from app.models.workflow import WorkflowStatus, TriggerType
from app.services.workflow import workflow_service
from app.utils.exceptions import NotFoundError
from app.utils.helpers import paginate_meta

router = APIRouter(prefix="/workflows", tags=["Workflows"])


def _serialize(wf) -> dict:
    return {
        "id": wf.id,
        "name": wf.name,
        "description": wf.description,
        "status": wf.status,
        "trigger_type": wf.trigger_type,
        "trigger_config": wf.trigger_config,
        "steps": wf.steps,
        "tags": wf.tags,
        "n8n_workflow_id": wf.n8n_workflow_id,
        "created_at": wf.created_at.isoformat() if wf.created_at else None,
        "updated_at": wf.updated_at.isoformat() if wf.updated_at else None,
        "execution_count": len(wf.executions) if wf.executions else 0,
    }


@router.get("", summary="List all workflows")
async def list_workflows(
    db: DBSession,
    status: Optional[WorkflowStatus] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    workflows = await workflow_service.list_workflows(db, status=status, limit=limit, offset=offset)
    total = await workflow_service.count_workflows(db)
    return {
        "data": [_serialize(w) for w in workflows],
        "meta": paginate_meta(total, limit, offset),
    }


@router.post("", status_code=status.HTTP_201_CREATED, summary="Create a workflow")
async def create_workflow(payload: dict, db: DBSession):
    workflow = await workflow_service.create_workflow(db, payload)
    return _serialize(workflow)


@router.get("/{workflow_id}", summary="Get workflow by ID")
async def get_workflow(workflow_id: str, db: DBSession):
    workflow = await workflow_service.get_workflow(db, workflow_id)
    if not workflow:
        raise NotFoundError("Workflow", workflow_id)
    return _serialize(workflow)


@router.put("/{workflow_id}", summary="Update a workflow")
async def update_workflow(workflow_id: str, payload: dict, db: DBSession):
    workflow = await workflow_service.update_workflow(db, workflow_id, payload)
    if not workflow:
        raise NotFoundError("Workflow", workflow_id)
    return _serialize(workflow)


@router.delete("/{workflow_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a workflow")
async def delete_workflow(workflow_id: str, db: DBSession):
    deleted = await workflow_service.delete_workflow(db, workflow_id)
    if not deleted:
        raise NotFoundError("Workflow", workflow_id)


@router.post("/{workflow_id}/execute", summary="Execute a workflow")
async def execute_workflow(workflow_id: str, db: DBSession, payload: Optional[dict] = None):
    execution = await workflow_service.execute_workflow(
        db, workflow_id, input_data=payload or {}, triggered_by="api"
    )
    if not execution:
        raise NotFoundError("Workflow", workflow_id)
    return {
        "execution_id": execution.id,
        "workflow_id": execution.workflow_id,
        "status": execution.status,
        "duration_seconds": execution.duration_seconds,
        "output": execution.output_data,
        "error": execution.error_message,
    }
