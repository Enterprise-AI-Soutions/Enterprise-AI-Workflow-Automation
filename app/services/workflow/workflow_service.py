"""Workflow business logic service."""

from __future__ import annotations

import time
import uuid
from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.workflow import Workflow, WorkflowStatus, TriggerType
from app.models.execution import WorkflowExecution, ExecutionStatus
from app.utils.logger import get_logger

logger = get_logger(__name__)


class WorkflowService:
    """CRUD and orchestration logic for Workflows."""

    # ── Workflow CRUD ──────────────────────────────────────────────────────────

    async def list_workflows(
        self,
        db: AsyncSession,
        status: Optional[WorkflowStatus] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Workflow]:
        q = select(Workflow).offset(offset).limit(limit).order_by(Workflow.created_at.desc())
        if status:
            q = q.where(Workflow.status == status)
        result = await db.execute(q)
        return list(result.scalars().all())

    async def get_workflow(self, db: AsyncSession, workflow_id: str) -> Optional[Workflow]:
        result = await db.execute(select(Workflow).where(Workflow.id == workflow_id))
        return result.scalar_one_or_none()

    async def create_workflow(self, db: AsyncSession, data: dict) -> Workflow:
        workflow = Workflow(
            id=str(uuid.uuid4()),
            name=data["name"],
            description=data.get("description"),
            status=WorkflowStatus(data.get("status", WorkflowStatus.DRAFT)),
            trigger_type=TriggerType(data.get("trigger_type", TriggerType.MANUAL)),
            trigger_config=data.get("trigger_config"),
            steps=data.get("steps", []),
            tags=data.get("tags", []),
        )
        db.add(workflow)
        await db.flush()
        await db.refresh(workflow)
        logger.info("Workflow created: %s (%s)", workflow.name, workflow.id)
        return workflow

    async def update_workflow(self, db: AsyncSession, workflow_id: str, data: dict) -> Optional[Workflow]:
        workflow = await self.get_workflow(db, workflow_id)
        if not workflow:
            return None
        for field in ("name", "description", "status", "trigger_type", "trigger_config", "steps", "tags"):
            if field in data:
                val = data[field]
                if field == "status":
                    val = WorkflowStatus(val)
                if field == "trigger_type":
                    val = TriggerType(val)
                setattr(workflow, field, val)
        await db.flush()
        await db.refresh(workflow)
        return workflow

    async def delete_workflow(self, db: AsyncSession, workflow_id: str) -> bool:
        workflow = await self.get_workflow(db, workflow_id)
        if not workflow:
            return False
        await db.delete(workflow)
        return True

    async def count_workflows(self, db: AsyncSession) -> int:
        result = await db.execute(select(func.count()).select_from(Workflow))
        return result.scalar_one()

    # ── Execution ─────────────────────────────────────────────────────────────

    async def execute_workflow(
        self,
        db: AsyncSession,
        workflow_id: str,
        input_data: Optional[dict] = None,
        triggered_by: str = "api",
    ) -> Optional[WorkflowExecution]:
        workflow = await self.get_workflow(db, workflow_id)
        if not workflow:
            return None

        execution = WorkflowExecution(
            id=str(uuid.uuid4()),
            workflow_id=workflow_id,
            status=ExecutionStatus.RUNNING,
            input_data=input_data or {},
            logs=[{"timestamp": time.time(), "level": "info", "message": f"Execution started by {triggered_by}"}],
            triggered_by=triggered_by,
        )
        db.add(execution)
        await db.flush()

        start = time.time()
        try:
            # In a full implementation, this would delegate to the n8n_service
            # or run steps inline. Here we simulate success.
            output = {"message": "Workflow executed successfully", "steps_run": len(workflow.steps or [])}
            execution.status = ExecutionStatus.SUCCESS
            execution.output_data = output
            execution.logs.append({"timestamp": time.time(), "level": "info", "message": "Execution completed"})
        except Exception as exc:
            execution.status = ExecutionStatus.FAILED
            execution.error_message = str(exc)
            execution.logs.append({"timestamp": time.time(), "level": "error", "message": str(exc)})
            logger.error("Workflow %s execution failed: %s", workflow_id, exc)
        finally:
            execution.duration_seconds = round(time.time() - start, 3)
            await db.flush()
            await db.refresh(execution)

        return execution


workflow_service = WorkflowService()
