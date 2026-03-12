"""
Centralized Runtime Configuration for AgentOS.

Uses Pydantic Settings to load config from .env, environment variables,
or defaults. This is the single source of truth for all runtime settings.
"""

from pydantic_settings import BaseSettings
from pydantic import Field


class RuntimeConfig(BaseSettings):
    """
    All runtime configuration for AgentOS.
    Values are loaded from environment variables / .env file.
    """

    # --- API ---
    api_host: str = Field(default="127.0.0.1", description="API server host")
    api_port: int = Field(default=8000, description="API server port")
    debug: bool = Field(default=True, description="Enable debug mode / auto-reload")

    # --- Database ---
    database_url: str = Field(
        default="postgresql+psycopg2://agentos:agentos_password@localhost:5432/agentos_db",
        description="PostgreSQL connection URL",
    )

    # --- Redis ---
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL",
    )

    # --- Qdrant ---
    qdrant_url: str = Field(
        default="http://localhost:6333",
        description="Qdrant vector DB URL",
    )

    # --- LLM ---
    llm_provider: str = Field(
        default="groq",
        description="LLM provider: groq, openai, or anthropic",
    )
    groq_api_key: str = Field(
        default="",
        description="Groq API key",
    )
    openai_api_key: str = Field(
        default="",
        description="OpenAI API key (for future use)",
    )
    anthropic_api_key: str = Field(
        default="",
        description="Anthropic API key (for future use)",
    )
    default_model: str = Field(
        default="llama-3.3-70b-versatile",
        description="Default LLM model name",
    )
    default_temperature: float = Field(
        default=0.7,
        description="Default LLM temperature",
    )
    default_max_tokens: int = Field(
        default=4096,
        description="Default max tokens for LLM response",
    )

    # --- Runtime ---
    request_timeout: int = Field(
        default=60,
        description="Max seconds for an agent run before timeout",
    )
    max_retries: int = Field(
        default=3,
        description="Max retries on transient LLM failures",
    )

    # --- MCP ---
    mcp_servers_config: str = Field(
        default="{}",
        description="JSON configuration for MCP servers to connect on startup",
    )

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }


# Singleton — import this from anywhere
config = RuntimeConfig()
