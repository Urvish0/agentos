"""
LLM Model Configuration Models for AgentOS.

Allows dynamic registration of custom models and API keys.
"""

from typing import Optional
import uuid
from sqlmodel import SQLModel, Field

class LLMModelConfig(SQLModel, table=True):
    """
    Stores custom LLM models registered by the user.
    """
    __tablename__ = "llm_model_config"

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
    )
    name: str = Field(index=True, unique=True, description="Human-readable model name (e.g. LLaMA-3)")
    model_id: str = Field(description="The actual model identifier (e.g. llama3, gpt-4-turbo)")
    provider: str = Field(description="The provider: openai, anthropic, groq, or ollama")
    api_key: Optional[str] = Field(default=None, description="Optional API key for this model")
    base_url: Optional[str] = Field(default=None, description="Optional custom base URL (e.g. for Ollama)")
    description: Optional[str] = Field(default=None)

class LLMModelCreate(SQLModel):
    name: str
    model_id: str
    provider: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    description: Optional[str] = None
