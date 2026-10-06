"""Models returned by the backend execution-management routes."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel


class Execution(BaseModel):
    execution_id: str
    internal_id: str | None = None
    agent_id: str | None = None
    agent_version: str | None = None
    principal_id: str | None = None
    principal_type: str | None = None
    status: str | None = None
    created_at: datetime | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    timeout_at: datetime | None = None
    context: dict[str, Any] | None = None
    output: dict[str, Any] | None = None
    error: str | None = None


class ExecutionStep(BaseModel):
    id: str | None = None
    execution_id: str | None = None
    sequence: int
    step_type: str | None = None
    action: str | None = None
    actor_id: str | None = None
    actor_type: str | None = None
    status: str | None = None
    timestamp: datetime | None = None
    input_hash: str | None = None
    output_hash: str | None = None


class ExecutionApproval(BaseModel):
    id: str | None = None
    request_id: str | None = None
    decision: str | None = None
    approver_id: str | None = None
    decided_at: datetime | None = None
