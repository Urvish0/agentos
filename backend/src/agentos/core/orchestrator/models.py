"""
Task Orchestration Models for AgentOS.

Defines the Task table, state machine, and API schemas.
Tasks represent units of work assigned to agents.
"""

from datetime import datetime, timezone
from enum import Enum
import uuid

from sqlmodel import SQLModel, Field
from pydantic import field_validator


# ---------------------------------------------------------------------------
# Task State Machine
# ---------------------------------------------------------------------------

class TaskStatus(str, Enum):
    """
    Allowed task states and their lifecycle:

        CREATED → QUEUED → RUNNING → COMPLETED
                                   → FAILED
                          RUNNING → PAUSED → RUNNING (resume)
        Any state → CANCELLED
    """
    CREATED = "created"
    QUEUED = "queued"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


# Valid state transitions: current_state → [allowed_next_states]
VALID_TRANSITIONS: dict[TaskStatus, list[TaskStatus]] = {
    TaskStatus.CREATED:   [TaskStatus.QUEUED, TaskStatus.RUNNING, TaskStatus.CANCELLED],
    TaskStatus.QUEUED:    [TaskStatus.RUNNING, TaskStatus.CANCELLED],
    TaskStatus.RUNNING:   [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.PAUSED, TaskStatus.CANCELLED],
    TaskStatus.PAUSED:    [TaskStatus.RUNNING, TaskStatus.CANCELLED],
    TaskStatus.COMPLETED: [],   # Terminal state
    TaskStatus.FAILED:    [TaskStatus.QUEUED],  # Can be retried → re-queued
    TaskStatus.CANCELLED: [],   # Terminal state
}


def validate_transition(current: TaskStatus, target: TaskStatus) -> bool:
    """Check if a state transition is allowed."""
    return target in VALID_TRANSITIONS.get(current, [])


# ---------------------------------------------------------------------------
# Database Model (Table)
# ---------------------------------------------------------------------------

class Task(SQLModel, table=True):
    """
    Represents a task (unit of work) in the AgentOS platform.
    Maps to the 'task' table in PostgreSQL.
    """
    __tablename__ = "task"

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
        description="Unique task identifier (UUID)",
    )
    agent_id: str = Field(
        index=True,
        description="ID of the agent assigned to this task",
    )
    parent_task_id: str | None = Field(
        default=None,
        index=True,
        description="ID of the parent task that delegated this task",
    )
    input: str = Field(
        description="The user's input or goal for this task",
    )
    status: str = Field(
        default=TaskStatus.CREATED.value,
        index=True,
        description="Current task state",
    )
    output: str = Field(
        default="",
        description="The agent's output / result",
    )
    error: str = Field(
        default="",
        description="Error message if task failed",
    )
    model: str = Field(
        default="",
        description="LLM model used for this task",
    )
    total_tokens: int = Field(
        default=0,
        description="Total tokens consumed",
    )
    execution_time_ms: float = Field(
        default=0.0,
        description="Execution time in milliseconds",
    )
    retry_count: int = Field(
        default=0,
        description="Number of retry attempts",
    )
    trace_id: str | None = Field(
        default=None,
        description="OpenTelemetry Trace identifier",
    )
    max_retries: int = Field(
        default=3,
        description="Maximum allowed retries",
    )
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO 8601 creation timestamp",
    )
    updated_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO 8601 last-updated timestamp",
    )
    completed_at: str = Field(
        default="",
        description="ISO 8601 completion timestamp",
    )


# ---------------------------------------------------------------------------
# API Schemas (Request / Response)
# ---------------------------------------------------------------------------

class TaskCreate(SQLModel):
    """Schema for creating a new task."""
    agent_id: str
    input: str


class TaskUpdate(SQLModel):
    """Schema for updating task status (used internally and by API)."""
    status: str | None = None
    output: str | None = None
    error: str | None = None

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str | None) -> str | None:
        if v is not None and v not in [s.value for s in TaskStatus]:
            raise ValueError(
                f"Invalid status '{v}'. "
                f"Allowed: {[s.value for s in TaskStatus]}"
            )
        return v


class TaskResponse(SQLModel):
    """Schema for task API responses."""
    id: str
    agent_id: str
    parent_task_id: str | None = None
    input: str
    status: str
    output: str
    error: str
    model: str
    total_tokens: int
    execution_time_ms: float
    retry_count: int
    max_retries: int
    trace_id: str | None = None
    created_at: str
    updated_at: str
    completed_at: str
