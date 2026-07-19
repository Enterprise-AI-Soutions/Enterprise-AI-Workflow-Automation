"""Execution history and log retrieval service."""

from __future__ import annotations

from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.execution import WorkflowExecution, ExecutionStatus
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ExecutionService:
    async def list_executions(
        self,
        db: AsyncSession,
        workflow_id: Optional[str] = None,
        status: Optional[ExecutionStatus] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[WorkflowExecution]:
        q = select(WorkflowExecution).offset(offset).limit(limit).order_by(WorkflowExecution.created_at.desc())
        if workflow_id:
            q = q.where(WorkflowExecution.workflow_id == workflow_id)
        if status:
            q = q.where(WorkflowExecution.status == status)
        result = await db.execute(q)
        return list(result.scalars().all())

    async def get_execution(self, db: AsyncSession, execution_id: str) -> Optional[WorkflowExecution]:
        result = await db.execute(select(WorkflowExecution).where(WorkflowExecution.id == execution_id))
        return result.scalar_one_or_none()

    async def count_executions(self, db: AsyncSession, workflow_id: Optional[str] = None) -> int:
        q = select(func.count()).select_from(WorkflowExecution)
        if workflow_id:
            q = q.where(WorkflowExecution.workflow_id == workflow_id)
        result = await db.execute(q)
        return result.scalar_one()

    async def get_stats(self, db: AsyncSession) -> dict:
        total = await self.count_executions(db)
        success_q = select(func.count()).select_from(WorkflowExecution).where(
            WorkflowExecution.status == ExecutionStatus.SUCCESS
        )
        failed_q = select(func.count()).select_from(WorkflowExecution).where(
            WorkflowExecution.status == ExecutionStatus.FAILED
        )
        success = (await db.execute(success_q)).scalar_one()
        failed = (await db.execute(failed_q)).scalar_one()
        return {
            "total": total,
            "success": success,
            "failed": failed,
            "pending": total - success - failed,
            "success_rate": round(success / total * 100, 1) if total else 0,
        }


execution_service = ExecutionService()
