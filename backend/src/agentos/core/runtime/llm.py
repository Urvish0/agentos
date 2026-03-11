"""
LLM Provider Abstraction for AgentOS.

Currently supports Groq (open-source models).
Designed to be easily extensible to other providers.
"""

import os
from langchain_groq import ChatGroq
from langchain_core.language_models.chat_models import BaseChatModel
import structlog

logger = structlog.get_logger()

# Available Groq models (as of March 2026)
GROQ_MODELS = {
    "llama-3.3-70b-versatile": "Best overall — fast, capable, great for reasoning",
    "llama-3.1-8b-instant": "Ultra-fast — good for simple tasks",
    "mixtral-8x7b-32768": "Strong coding and math — 32k context",
    "gemma2-9b-it": "Google's open model — good instruction following",
}

DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "llama-3.3-70b-versatile")


def get_llm(
    model: str | None = None,
    temperature: float = 0.7,
    max_tokens: int = 4096,
    api_key: str | None = None,
) -> BaseChatModel:
    """
    Factory function to create an LLM instance.

    Args:
        model: Model name (defaults to DEFAULT_MODEL env var)
        temperature: Sampling temperature (0.0 = deterministic, 1.0 = creative)
        max_tokens: Maximum tokens in response
        api_key: Groq API key (defaults to GROQ_API_KEY env var)

    Returns:
        A LangChain-compatible chat model instance
    """
    model = model or DEFAULT_MODEL
    # Guard against Swagger UI placeholder values or empty strings
    if model in ("string", ""):
        model = DEFAULT_MODEL
    api_key = api_key or os.getenv("GROQ_API_KEY")

    if not api_key:
        raise ValueError(
            "GROQ_API_KEY is not set. "
            "Set it in your .env file or pass it directly."
        )

    logger.info("Initializing LLM", provider="groq", model=model)

    return ChatGroq(
        model=model,
        api_key=api_key,
        temperature=temperature,
        max_tokens=max_tokens,
    )
