"""
Agent API Routes for AgentOS.

Provides RESTful endpoints for managing agents (CRUD operations).
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
import structlog

from agentos.core.manager.database import get_session
from agentos.core.manager.models import AgentCreate, AgentUpdate, AgentResponse
from agentos.core.manager import service
from agentos.services.observability.audit import audit_logger

logger = structlog.get_logger()

router = APIRouter(prefix="/agents", tags=["Agents"])


@router.post("/register", response_model=AgentResponse, status_code=201)
def register_agent(
    agent_data: AgentCreate,
    session: Session = Depends(get_session),
):
    """
    Register a new agent in the AgentOS platform.

    This creates a persistent agent profile with a name, model,
    system prompt, and other configuration. The agent can then
    be used to run tasks via POST /agent/run.
    """
    agent = service.create_agent(session, agent_data)
    
    audit_logger.log_sensitive_action(
        actor="system_api",
        action="agent_registered",
        resource=f"agent:{agent.id}",
        details={"name": agent.name, "version": agent.version}
    )
    
    return agent


@router.get("/", response_model=list[AgentResponse])
def list_agents(
    skip: int = 0,
    limit: int = 100,
    status: str | None = None,
    session: Session = Depends(get_session),
):
    """
    List all registered agents.

    Supports pagination (skip/limit) and filtering by status.
    """
    agents = service.list_agents(session, skip=skip, limit=limit, status=status)
    return agents


@router.get("/{agent_id}", response_model=AgentResponse)
def get_agent(
    agent_id: str,
    session: Session = Depends(get_session),
):
    """
    Get details of a specific agent by its ID.
    """
    agent = service.get_agent(session, agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")
    return agent


@router.put("/{agent_id}", response_model=AgentResponse)
def update_agent(
    agent_id: str,
    agent_data: AgentUpdate,
    session: Session = Depends(get_session),
):
    """
    Update an existing agent's configuration.

    Only the fields you include in the request body will be updated.
    """
    agent = service.update_agent(session, agent_id, agent_data)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")
        
    audit_logger.log_sensitive_action(
        actor="system_api",
        action="agent_updated",
        resource=f"agent:{agent.id}",
        details={"updated_fields": agent_data.model_dump(exclude_unset=True)}
    )
        
    return agent


@router.delete("/{agent_id}", status_code=204)
def delete_agent(
    agent_id: str,
    session: Session = Depends(get_session),
):
    """
    Delete an agent from the registry.
    """
    deleted = service.delete_agent(session, agent_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")
        
    audit_logger.log_sensitive_action(
        actor="system_api",
        action="agent_deleted",
        resource=f"agent:{agent_id}",
        details={}
    )
