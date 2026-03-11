"""
Task API Routes for AgentOS.

Provides RESTful endpoints for task lifecycle management.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
import structlog

from agentos.core.manager.database import get_session
from agentos.core.orchestrator.models import TaskCreate, TaskUpdate, TaskResponse
from agentos.core.orchestrator import service
from agentos.core.manager import service as agent_service

logger = structlog.get_logger()

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post("/create", response_model=TaskResponse, status_code=201)
def create_task(
    task_data: TaskCreate,
    session: Session = Depends(get_session),
):
    """
    Create a new task for an agent.

    The task starts in 'created' state. To execute it,
    transition it to 'queued' and then 'running'.
    """
    # Verify the agent exists
    agent = agent_service.get_agent(session, task_data.agent_id)
    if not agent:
        raise HTTPException(
            status_code=404,
            detail=f"Agent '{task_data.agent_id}' not found. Register an agent first.",
        )
    task = service.create_task(session, task_data)
    return task


@router.get("/", response_model=list[TaskResponse])
def list_tasks(
    skip: int = 0,
    limit: int = 100,
    status: str | None = None,
    agent_id: str | None = None,
    session: Session = Depends(get_session),
):
    """
    List all tasks with optional filters.
    """
    tasks = service.list_tasks(
        session, skip=skip, limit=limit, status=status, agent_id=agent_id
    )
    return tasks


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: str,
    session: Session = Depends(get_session),
):
    """Get details of a specific task."""
    task = service.get_task(session, task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task '{task_id}' not found")
    return task


@router.patch("/{task_id}/status", response_model=TaskResponse)
def update_task_status(
    task_id: str,
    update: TaskUpdate,
    session: Session = Depends(get_session),
):
    """
    Transition a task to a new state.

    Enforces the state machine:
    - created → queued → running → completed / failed
    - running → paused → running (resume)
    - Any state → cancelled
    - failed → queued (retry)
    """
    if not update.status:
        raise HTTPException(status_code=400, detail="'status' field is required")

    try:
        task = service.update_task_status(
            session,
            task_id,
            new_status=update.status,
            output=update.output or "",
            error=update.error or "",
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if not task:
        raise HTTPException(status_code=404, detail=f"Task '{task_id}' not found")
    return task


@router.delete("/{task_id}", status_code=204)
def delete_task(
    task_id: str,
    session: Session = Depends(get_session),
):
    """Delete a task."""
    deleted = service.delete_task(session, task_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Task '{task_id}' not found")
