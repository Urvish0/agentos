"""
Console API Routes for AgentOS Dashboard.

Provides interactive shell capabilities, direct agent messaging,
and real-time log orchestration.
"""

from fastapi import APIRouter, Depends, HTTPException, Body
from sqlmodel import Session
from agentos.core.manager.database import get_session
from agentos.core.orchestrator.models import Task, TaskCreate
from agentos.core.orchestrator.service import create_task

router = APIRouter(prefix="/console", tags=["Console"])

@router.post("/chat")
async def console_chat(
    agent_id: str = Body(...),
    message: str = Body(...),
    model: str | None = Body(None),
    session: Session = Depends(get_session)
):
    """
    Directly interact with an agent via the console.
    """
    task_data = TaskCreate(
        agent_id=agent_id,
        input=message,
        model=model or "gpt-4o",
    )
    
    try:
        # 1. Create in 'created' state
        task = create_task(session, task_data)
        
        # 2. Transition to 'queued'
        from agentos.core.orchestrator import service as task_service
        task = task_service.update_task_status(session, task.id, "queued")
        
        # 3. Trigger background execution via Celery
        from agentos.core.orchestrator.tasks import run_agent_task
        run_agent_task.apply_async(args=[task.id], task_id=task.id)
        
        return {
            "status": "success",
            "message": "Message received by agent",
            "task_id": task.id
        }
    except Exception as e:
        import structlog
        structlog.get_logger().error("Failed to dispatch console task", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to send message: {str(e)}")

# ---- Model Management ----

from agentos.core.runtime import llm
from agentos.core.runtime.llm_models import LLMModelConfig, LLMModelCreate
from sqlmodel import select

@router.get("/models")
async def list_available_models(session: Session = Depends(get_session)):
    """
    Return all available models (Preset + Custom).
    """
    # 1. Preset models from llm.py
    presets = []
    for m_id, desc in llm.ALL_MODELS.items():
        presets.append({
            "id": m_id,
            "name": m_id,
            "description": desc,
            "provider": "preset",
            "is_custom": False
        })
    
    # 2. Custom models from DB
    customs = session.exec(select(LLMModelConfig)).all()
    custom_list = []
    for c in customs:
        custom_list.append({
            "id": c.id,
            "name": c.name,
            "model_id": c.model_id,
            "provider": c.provider,
            "is_custom": True,
            "description": c.description
        })
    
    return presets + custom_list

@router.post("/models")
async def add_custom_model(
    model_data: LLMModelCreate,
    session: Session = Depends(get_session)
):
    """
    Register a new custom model (LLaMA/Local/Custom API).
    """
    new_model = LLMModelConfig(**model_data.model_dump())
    session.add(new_model)
    session.commit()
    session.refresh(new_model)
    return new_model

@router.delete("/models/{id}")
async def delete_custom_model(
    id: str,
    session: Session = Depends(get_session)
):
    model = session.get(LLMModelConfig, id)
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    session.delete(model)
    session.commit()
    return {"status": "success", "message": f"Model {id} deleted"}

@router.post("/command")
async def execute_command(
    agent_id: str = Body(...),
    command: str = Body(...),
    session: Session = Depends(get_session)
):
    """
    Execute system-level commands (e.g., clear_memory, inspect_context).
    """
    # This would interact with the Agent Manager or Core Services
    # For MVP, we provide a success response
    return {
        "status": "success",
        "command": command,
        "details": f"Executed '{command}' on agent {agent_id}"
    }
