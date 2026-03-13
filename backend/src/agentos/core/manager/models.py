"""
Agent data models for AgentOS.

Defines the Agent table schema using SQLModel (SQLAlchemy + Pydantic hybrid).
This is the core data structure for the Agent Registry.
"""

from datetime import datetime, timezone
from typing import Any
import uuid

from sqlmodel import SQLModel, Field
from pydantic import field_validator


# ---------------------------------------------------------------------------
# Database Model (Table)
# ---------------------------------------------------------------------------

class Agent(SQLModel, table=True):
    """
    Represents a registered agent in the AgentOS platform.
    This model maps directly to the 'agent' table in PostgreSQL.
    """
    __tablename__ = "agent"

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
        description="Unique agent identifier (UUID)",
    )
    name: str = Field(
        index=True,
        description="Human-readable name for the agent",
    )
    description: str = Field(
        default="",
        description="What this agent does",
    )
    version: str = Field(
        default="0.1.0",
        description="Semantic version of this agent",
    )
    model: str = Field(
        default="llama-3.3-70b-versatile",
        description="LLM model this agent uses",
    )
    system_prompt: str = Field(
        default="You are a helpful AI assistant.",
        description="The system prompt that defines this agent's personality",
    )
    temperature: float = Field(
        default=0.7,
        description="LLM sampling temperature",
    )
    tools: str = Field(
        default="[]",
        description="JSON array of tool names this agent can use",
    )
    status: str = Field(
        default="active",
        description="Agent status: active, inactive, archived",
    )
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO 8601 creation timestamp",
    )
    updated_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO 8601 last-updated timestamp",
    )


# ---------------------------------------------------------------------------
# API Schemas (Request / Response — NOT table models)
# ---------------------------------------------------------------------------

class AgentCreate(SQLModel):
    """Schema for creating a new agent (request body)."""
    id: str | None = None
    name: str
    description: str = ""
    version: str = "0.1.0"
    model: str = "llama-3.3-70b-versatile"
    system_prompt: str = "You are a helpful AI assistant."
    temperature: float = 0.7
    tools: str = "[]"

    @field_validator("temperature")
    @classmethod
    def validate_temperature(cls, v: float) -> float:
        if not 0.0 <= v <= 2.0:
            raise ValueError("Temperature must be between 0.0 and 2.0")
        return v


class AgentUpdate(SQLModel):
    """Schema for updating an agent (request body). All fields optional."""
    name: str | None = None
    description: str | None = None
    version: str | None = None
    model: str | None = None
    system_prompt: str | None = None
    temperature: float | None = None
    tools: str | None = None
    status: str | None = None


class AgentResponse(SQLModel):
    """Schema for agent API responses."""
    id: str
    name: str
    description: str
    version: str
    model: str
    system_prompt: str
    temperature: float
    tools: str
    status: str
    created_at: str
    updated_at: str
