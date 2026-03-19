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
    Create a new task for an agent and automatically trigger background execution.
    The task transitions from created -> queued and is sent to Celery.
    """
    # Verify the agent exists
    agent = agent_service.get_agent(session, task_data.agent_id)
    if not agent:
        raise HTTPException(
            status_code=404,
            detail=f"Agent '{task_data.agent_id}' not found. Register an agent first.",
        )
    
    # 1. Create in 'created' state
    task = service.create_task(session, task_data)
    
    # 2. Transition to 'queued'
    task = service.update_task_status(session, task.id, "queued")
    
    # 3. Trigger background execution via Celery
    # Use task.id as the Celery ID so we can revoke it easily later
    from agentos.core.orchestrator.tasks import run_agent_task
    run_agent_task.apply_async(args=[task.id], task_id=task.id)
    
    logger.info("Task enqueued for background execution", task_id=task.id)
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


@router.post("/{task_id}/cancel", response_model=TaskResponse)
def cancel_task(
    task_id: str,
    session: Session = Depends(get_session),
):
    """
    Cancel a running or queued task.
    This will terminate the background worker process if the task is running.
    """
    try:
        task = service.cancel_task(session, task_id)
        if not task:
            raise HTTPException(status_code=404, detail=f"Task '{task_id}' not found")
        return task
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# ---- Log Streaming (SSE) ----

import asyncio
from fastapi.responses import StreamingResponse
import json

@router.get("/{id}/logs/stream")
async def stream_task_logs(id: str, session: Session = Depends(get_session)):
    """
    Stream task progress and logs via SSE.
    Polls DB every 0.5s for fast feedback on quick-completing tasks.
    """
    async def log_generator():
        last_status = ""
        last_output = ""
        polls = 0
        max_polls = 600  # 5 minutes max (600 * 0.5s)
        
        while polls < max_polls:
            polls += 1
            try:
                from agentos.core.manager.database import engine
                from sqlmodel import Session as DBSession
                with DBSession(engine) as s:
                    from agentos.core.orchestrator.service import get_task as g_task
                    task = g_task(s, id)
                    if not task:
                        yield f"data: {json.dumps({'error': 'Task not found'})}\n\n"
                        break
                    
                    current_status = task.status or ""
                    current_output = task.output or ""
                    current_error = task.error or ""
                    ts = str(task.updated_at) if task.updated_at else None
                    
                    # Emit status changes
                    if current_status != last_status:
                        last_status = current_status
                        yield f"data: {json.dumps({'status': current_status, 'timestamp': ts})}\n\n"
                    
                    # Emit output changes (new or updated output)
                    if current_output and current_output != last_output:
                        last_output = current_output
                        yield f"data: {json.dumps({'output': current_output, 'timestamp': ts})}\n\n"
                    
                    # Emit errors
                    if current_error:
                        yield f"data: {json.dumps({'error': current_error, 'timestamp': ts})}\n\n"
                    
                    # If terminal state, send final output + terminate
                    if current_status in ("completed", "failed", "cancelled"):
                        # Small delay to ensure client processes the output event
                        await asyncio.sleep(0.3)
                        yield f"data: {json.dumps({'info': 'Session terminated'})}\n\n"
                        break
                        
            except Exception as e:
                logger.error("SSE generator error", error=str(e), task_id=id)
                yield f"data: {json.dumps({'error': f'Stream error: {str(e)}'})}\n\n"
                break
            
            await asyncio.sleep(0.5)  # Poll every 0.5s for fast feedback
            
    return StreamingResponse(log_generator(), media_type="text/event-stream")


@router.get("/{id}/trace")
def get_task_trace(id: str, session: Session = Depends(get_session)):
    """
    Get the OpenTelemetry trace ID and UI URL for a task.
    """
    task = service.get_task(session, id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if not task.trace_id:
        raise HTTPException(status_code=400, detail="No trace available for this task")
    return {
        "task_id": id,
        "trace_id": task.trace_id,
        "trace_url": f"http://localhost:16686/trace/{task.trace_id}"
    }
