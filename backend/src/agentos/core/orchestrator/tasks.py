"""
Background Celery tasks for AgentOS.

Contains the actual logic that executes agents asynchronously.
"""

import asyncio
from typing import Any, Dict
import structlog
from celery import Task as CeleryTask

from agentos.core.orchestrator.celery_app import celery_app
from agentos.core.orchestrator import service as task_service
from agentos.core.manager.database import engine
from agentos.core.runtime.runtime import AgentRuntime
from agentos.core.orchestrator.models import TaskStatus
from sqlmodel import Session

logger = structlog.get_logger()

class AgentTask(CeleryTask):
    """Custom Task class for debugging or common logic."""
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        logger.error("Celery task failed", task_id=task_id, error=str(exc))

@celery_app.task(
    bind=True,
    base=AgentTask,
    name="agentos.core.orchestrator.tasks.run_agent_task",
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=600,
    max_retries=3,
)
def run_agent_task(self, task_id: str) -> Dict[str, Any]:
    """
    Background task to execute an agent.
    
    1. Fetches task from DB.
    2. Moves to RUNNING.
    3. Runs AgentRuntime.
    4. Updates DB with results/errors.
    """
    logger.info("Starting background agent task", task_id=task_id, retry=self.request.retries)
    
    with Session(engine) as session:
        # 1. Get Task
        db_task = task_service.get_task(session, task_id)
        if not db_task:
            return {"status": "error", "message": f"Task {task_id} not found"}

        # Update retry count in DB if this is a retry
        if self.request.retries > 0:
            db_task.retry_count = self.request.retries
            session.add(db_task)
            session.commit()

        try:
            # 2. Transition to RUNNING
            task_service.update_task_status(session, task_id, TaskStatus.RUNNING.value)
            
            # 3. Initialize Runtime
            # Note: We need to run async code inside a synchronous Celery worker
            loop = asyncio.get_event_loop()
            if loop.is_closed():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            runtime = AgentRuntime()
            
            # Run the agent
            result = loop.run_until_complete(runtime.run(db_task.input))
            
            # 4. Success Completion
            task_service.update_task_status(
                session, 
                task_id, 
                TaskStatus.COMPLETED.value,
                output=result.get("output", ""),
            )
            
            # Update additional metrics
            db_task.model = result.get("model", "")
            db_task.total_tokens = result.get("total_tokens", 0)
            db_task.execution_time_ms = result.get("execution_time_ms", 0.0)
            session.add(db_task)
            session.commit()
            
            return {"status": "success", "run_id": result.get("run_id")}

        except Exception as e:
            logger.error("Background task execution failed", task_id=task_id, error=str(e), retry=self.request.retries)
            
            # If we still have retries left, we don't mark as FAILED yet
            if self.request.retries < self.max_retries:
                # We'll let Celery handle the retry, but we can log it
                raise e
            
            # Final failure
            task_service.update_task_status(
                session, 
                task_id, 
                TaskStatus.FAILED.value,
                error=str(e)
            )
            return {"status": "failed", "error": str(e)}
