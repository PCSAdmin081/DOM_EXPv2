"""Ops jobs models for tracking job execution."""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import JSON, Index, Text, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from domain_expansion.app.db.base import Base


class JobStatus(str, Enum):
    """Job execution status."""

    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class OpsJob(Base):
    """Operational job execution log.

    Tracks all jobs executed by the runner service.
    """

    __tablename__ = "ops_jobs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    job_type: Mapped[str] = mapped_column(Text, nullable=False, index=True)
    status: Mapped[JobStatus] = mapped_column(
        Text, nullable=False, default=JobStatus.QUEUED, index=True
    )
    requested_by: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, server_default=text("now()"), nullable=False, index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        server_default=text("now()"),
        nullable=False,
    )
    payload: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    result: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    runner_instance: Mapped[str | None] = mapped_column(Text, nullable=True)

    __table_args__ = (
        Index("idx_ops_jobs_status_created", "status", "created_at"),
        Index("idx_ops_jobs_type_created", "job_type", "created_at"),
    )


class OpsJobEvent(Base):
    """Optional detailed event log for ops jobs.

    Provides granular event tracking for job execution.
    """

    __tablename__ = "ops_job_events"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False, index=True
    )
    event_type: Mapped[str] = mapped_column(Text, nullable=False)
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, server_default=text("now()"), nullable=False, index=True
    )
