"""
Agent CRUD Service for AgentOS.

Provides all database operations for agents.
This is the "business logic" layer between the API routes and the database.
"""

from datetime import datetime, timezone

from sqlmodel import Session, select
import structlog

from agentos.core.manager.models import Agent, AgentCreate, AgentUpdate

logger = structlog.get_logger()


def create_agent(session: Session, agent_data: AgentCreate) -> Agent:
    """Register a new agent in the database."""
    agent = Agent(**agent_data.model_dump())
    session.add(agent)
    session.commit()
    session.refresh(agent)
    logger.info("Agent created", agent_id=agent.id, name=agent.name)
    return agent


def get_agent(session: Session, agent_id: str) -> Agent | None:
    """Get an agent by ID. Returns None if not found."""
    return session.get(Agent, agent_id)


def list_agents(
    session: Session,
    skip: int = 0,
    limit: int = 100,
    status: str | None = None,
) -> list[Agent]:
    """List all agents, with optional filtering by status."""
    query = select(Agent)
    if status:
        query = query.where(Agent.status == status)
    query = query.offset(skip).limit(limit)
    return list(session.exec(query).all())


def update_agent(
    session: Session,
    agent_id: str,
    agent_data: AgentUpdate,
) -> Agent | None:
    """Update an existing agent. Returns None if not found."""
    agent = session.get(Agent, agent_id)
    if not agent:
        return None

    # Only update fields that were explicitly provided
    update_fields = agent_data.model_dump(exclude_unset=True)
    for field, value in update_fields.items():
        setattr(agent, field, value)

    # Always update the timestamp
    agent.updated_at = datetime.now(timezone.utc).isoformat()

    session.add(agent)
    session.commit()
    session.refresh(agent)
    logger.info("Agent updated", agent_id=agent.id, fields=list(update_fields.keys()))
    return agent


def delete_agent(session: Session, agent_id: str) -> bool:
    """Delete an agent. Returns True if deleted, False if not found."""
    agent = session.get(Agent, agent_id)
    if not agent:
        return False

    session.delete(agent)
    session.commit()
    logger.info("Agent deleted", agent_id=agent_id)
    return True
