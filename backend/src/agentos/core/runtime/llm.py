"""
Multi-Provider LLM Abstraction for AgentOS.

Supports: Groq, OpenAI, Anthropic.
Provider is selected via config (LLM_PROVIDER env var).
"""

import structlog
from langchain_core.language_models.chat_models import BaseChatModel

from agentos.core.runtime.config import config

logger = structlog.get_logger()

# ---------------------------------------------------------------------------
# Model catalogs per provider
# ---------------------------------------------------------------------------

GROQ_MODELS = {
    "llama-3.3-70b-versatile": "Best overall — fast, capable, great for reasoning",
    "llama-3.1-8b-instant": "Ultra-fast — good for simple tasks",
    "mixtral-8x7b-32768": "Strong coding and math — 32k context",
    "gemma2-9b-it": "Google's open model — good instruction following",
}

OPENAI_MODELS = {
    "gpt-4o": "Most capable OpenAI model",
    "gpt-4o-mini": "Fast and affordable",
    "gpt-3.5-turbo": "Legacy — good for simple tasks",
}

ANTHROPIC_MODELS = {
    "claude-sonnet-4-20250514": "Latest Anthropic model",
    "claude-3-5-haiku-20241022": "Fast and affordable",
}

# Merge all for lookup
ALL_MODELS = {**GROQ_MODELS, **OPENAI_MODELS, **ANTHROPIC_MODELS}


# ---------------------------------------------------------------------------
# Provider factory functions
# ---------------------------------------------------------------------------

def _get_groq_llm(model: str, temperature: float, max_tokens: int) -> BaseChatModel:
    """Create a Groq LLM instance."""
    from langchain_groq import ChatGroq

    api_key = config.groq_api_key
    if not api_key:
        raise ValueError("GROQ_API_KEY is not set. Set it in your .env file.")

    return ChatGroq(
        model=model,
        api_key=api_key,
        temperature=temperature,
        max_tokens=max_tokens,
    )


def _get_openai_llm(model: str, temperature: float, max_tokens: int) -> BaseChatModel:
    """Create an OpenAI LLM instance."""
    try:
        from langchain_openai import ChatOpenAI
    except ImportError:
        raise ImportError(
            "langchain-openai is not installed. "
            "Run: uv add langchain-openai"
        )

    api_key = config.openai_api_key
    if not api_key:
        raise ValueError("OPENAI_API_KEY is not set. Set it in your .env file.")

    return ChatOpenAI(
        model=model,
        api_key=api_key,
        temperature=temperature,
        max_tokens=max_tokens,
    )


def _get_anthropic_llm(model: str, temperature: float, max_tokens: int) -> BaseChatModel:
    """Create an Anthropic LLM instance."""
    try:
        from langchain_anthropic import ChatAnthropic
    except ImportError:
        raise ImportError(
            "langchain-anthropic is not installed. "
            "Run: uv add langchain-anthropic"
        )

    api_key = config.anthropic_api_key
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY is not set. Set it in your .env file.")

    return ChatAnthropic(
        model=model,
        api_key=api_key,
        temperature=temperature,
        max_tokens=max_tokens,
    )


# ---------------------------------------------------------------------------
# Provider registry
# ---------------------------------------------------------------------------

PROVIDERS = {
    "groq": _get_groq_llm,
    "openai": _get_openai_llm,
    "anthropic": _get_anthropic_llm,
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_llm(
    model: str | None = None,
    temperature: float | None = None,
    max_tokens: int | None = None,
    provider: str | None = None,
) -> BaseChatModel:
    """
    Factory function to create an LLM instance.

    Args:
        model: Model name (defaults to config.default_model)
        temperature: Sampling temperature (defaults to config.default_temperature)
        max_tokens: Max tokens (defaults to config.default_max_tokens)
        provider: LLM provider — "groq", "openai", or "anthropic"
                  (defaults to config.llm_provider)

    Returns:
        A LangChain-compatible chat model instance
    """
    provider = provider or config.llm_provider
    model = model or config.default_model
    temperature = temperature if temperature is not None else config.default_temperature
    max_tokens = max_tokens if max_tokens is not None else config.default_max_tokens

    # Guard against placeholder values
    if model in ("string", ""):
        model = config.default_model

    if provider not in PROVIDERS:
        raise ValueError(
            f"Unknown provider '{provider}'. "
            f"Supported: {', '.join(PROVIDERS.keys())}"
        )

    logger.info("Initializing LLM", provider=provider, model=model)
    return PROVIDERS[provider](model, temperature, max_tokens)
