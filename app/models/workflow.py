"""Workflow ORM model."""

import uuid
from enum import Enum as PyEnum
from typing import Optional

from sqlalchemy import JSON, String, Text, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.services.database.base import Base, TimestampMixin


class WorkflowStatus(str, PyEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    DRAFT = "draft"
    ARCHIVED = "archived"


class TriggerType(str, PyEnum):
    WEBHOOK = "webhook"
    SCHEDULE = "schedule"
    MANUAL = "manual"
    EMAIL = "email"
    EVENT = "event"


class Workflow(Base, TimestampMixin):
    __tablename__ = "workflows"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[WorkflowStatus] = mapped_column(
        SAEnum(WorkflowStatus), default=WorkflowStatus.DRAFT, nullable=False
    )
    trigger_type: Mapped[TriggerType] = mapped_column(
        SAEnum(TriggerType), default=TriggerType.MANUAL, nullable=False
    )
    trigger_config: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    steps: Mapped[Optional[list]] = mapped_column(JSON, nullable=True, default=list)
    tags: Mapped[Optional[list]] = mapped_column(JSON, nullable=True, default=list)
    n8n_workflow_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    created_by: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)

    # Relationships
    executions: Mapped[list["WorkflowExecution"]] = relationship(  # noqa: F821
        back_populates="workflow", cascade="all, delete-orphan", lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<Workflow id={self.id} name={self.name!r} status={self.status}>"
