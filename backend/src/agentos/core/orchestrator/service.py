"""
Task CRUD Service for AgentOS.

Provides all database operations for tasks,
including state machine transition enforcement.
"""

from datetime import datetime, timezone

from sqlmodel import Session, select
import structlog

from agentos.core.orchestrator.models import (
    Task,
    TaskCreate,
    TaskUpdate,
    TaskStatus,
    validate_transition,
)

logger = structlog.get_logger()


def create_task(session: Session, task_data: TaskCreate) -> Task:
    """Create a new task in CREATED state."""
    task = Task(**task_data.model_dump())
    session.add(task)
    session.commit()
    session.refresh(task)
    logger.info("Task created", task_id=task.id, agent_id=task.agent_id)
    return task


def get_task(session: Session, task_id: str) -> Task | None:
    """Get a task by ID."""
    return session.get(Task, task_id)


def list_tasks(
    session: Session,
    skip: int = 0,
    limit: int = 100,
    status: str | None = None,
    agent_id: str | None = None,
) -> list[Task]:
    """List tasks with optional filtering."""
    query = select(Task)
    if status:
        query = query.where(Task.status == status)
    if agent_id:
        query = query.where(Task.agent_id == agent_id)
    query = query.order_by(Task.created_at.desc())  # type: ignore
    query = query.offset(skip).limit(limit)
    return list(session.exec(query).all())


def update_task_status(
    session: Session,
    task_id: str,
    new_status: str,
    output: str = "",
    error: str = "",
) -> Task | None:
    """
    Transition a task to a new state.
    Enforces the state machine — invalid transitions are rejected.
    """
    task = session.get(Task, task_id)
    if not task:
        return None

    current = TaskStatus(task.status)
    target = TaskStatus(new_status)

    if not validate_transition(current, target):
        raise ValueError(
            f"Invalid transition: '{current.value}' → '{target.value}'. "
            f"Allowed: {[s.value for s in __import__('agentos.core.orchestrator.models', fromlist=['VALID_TRANSITIONS']).VALID_TRANSITIONS.get(current, [])]}"
        )

    task.status = target.value
    task.updated_at = datetime.now(timezone.utc).isoformat()

    if output:
        task.output = output
    if error:
        task.error = error

    # Mark completion timestamp for terminal states
    if target in (TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED):
        task.completed_at = datetime.now(timezone.utc).isoformat()

    session.add(task)
    session.commit()
    session.refresh(task)
    logger.info(
        "Task status updated",
        task_id=task.id,
        transition=f"{current.value} → {target.value}",
    )
    return task


def delete_task(session: Session, task_id: str) -> bool:
    """Delete a task. Returns True if deleted, False if not found."""
    task = session.get(Task, task_id)
    if not task:
        return False
    session.delete(task)
    session.commit()
    logger.info("Task deleted", task_id=task_id)
    return True
