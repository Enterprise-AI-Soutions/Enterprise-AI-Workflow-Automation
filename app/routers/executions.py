"""Execution history router."""

from typing import Optional

from fastapi import APIRouter, Query

from app.api.deps import DBSession
from app.models.execution import ExecutionStatus
from app.services.workflow import execution_service
from app.utils.exceptions import NotFoundError
from app.utils.helpers import paginate_meta

router = APIRouter(prefix="/executions", tags=["Executions"])


def _serialize(ex) -> dict:
    return {
        "id": ex.id,
        "workflow_id": ex.workflow_id,
        "status": ex.status,
        "triggered_by": ex.triggered_by,
        "duration_seconds": ex.duration_seconds,
        "input_data": ex.input_data,
        "output_data": ex.output_data,
        "error_message": ex.error_message,
        "created_at": ex.created_at.isoformat() if ex.created_at else None,
    }


@router.get("", summary="List executions")
async def list_executions(
    db: DBSession,
    workflow_id: Optional[str] = Query(None),
    status: Optional[ExecutionStatus] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    executions = await execution_service.list_executions(
        db, workflow_id=workflow_id, status=status, limit=limit, offset=offset
    )
    total = await execution_service.count_executions(db, workflow_id=workflow_id)
    return {
        "data": [_serialize(e) for e in executions],
        "meta": paginate_meta(total, limit, offset),
    }


@router.get("/stats", summary="Execution statistics")
async def execution_stats(db: DBSession):
    return await execution_service.get_stats(db)


@router.get("/{execution_id}", summary="Get execution by ID")
async def get_execution(execution_id: str, db: DBSession):
    ex = await execution_service.get_execution(db, execution_id)
    if not ex:
        raise NotFoundError("Execution", execution_id)
    return _serialize(ex)


@router.get("/{execution_id}/logs", summary="Get execution logs")
async def get_execution_logs(execution_id: str, db: DBSession):
    ex = await execution_service.get_execution(db, execution_id)
    if not ex:
        raise NotFoundError("Execution", execution_id)
    return {"execution_id": execution_id, "status": ex.status, "logs": ex.logs or []}
