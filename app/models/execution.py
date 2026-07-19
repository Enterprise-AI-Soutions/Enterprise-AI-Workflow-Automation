"""WorkflowExecution ORM model."""

import uuid
from enum import Enum as PyEnum
from typing import Optional

from sqlalchemy import JSON, String, Text, Float, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.services.database.base import Base, TimestampMixin


class ExecutionStatus(str, PyEnum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"


class WorkflowExecution(Base, TimestampMixin):
    __tablename__ = "workflow_executions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    workflow_id: Mapped[str] = mapped_column(String(36), ForeignKey("workflows.id"), nullable=False, index=True)
    status: Mapped[ExecutionStatus] = mapped_column(
        SAEnum(ExecutionStatus), default=ExecutionStatus.PENDING, nullable=False
    )
    input_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    output_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    logs: Mapped[Optional[list]] = mapped_column(JSON, nullable=True, default=list)
    duration_seconds: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    triggered_by: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Relationships
    workflow: Mapped["Workflow"] = relationship(back_populates="executions")  # noqa: F821

    def __repr__(self) -> str:
        return f"<WorkflowExecution id={self.id} workflow_id={self.workflow_id} status={self.status}>"
