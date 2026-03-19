"""
Multi-Provider LLM Abstraction for AgentOS.

Supports: Groq, OpenAI, Anthropic.
Provider is selected via config (LLM_PROVIDER env var).
"""

import structlog
from langchain_core.language_models.chat_models import BaseChatModel

from agentos.core.runtime.config import config
from agentos.core.runtime.llm_models import LLMModelConfig
from sqlmodel import Session, select
from agentos.core.manager.database import engine

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

def _get_groq_llm(model: str, temperature: float, max_tokens: int, api_key: str | None = None) -> BaseChatModel:
    """Create a Groq LLM instance."""
    from langchain_groq import ChatGroq

    api_key = api_key or config.groq_api_key
    if not api_key:
        raise ValueError("GROQ_API_KEY is not set. Set it in your .env file or register a custom model with a key.")

    return ChatGroq(
        model=model,
        api_key=api_key,
        temperature=temperature,
        max_tokens=max_tokens,
    )


def _get_openai_llm(model: str, temperature: float, max_tokens: int, api_key: str | None = None, base_url: str | None = None) -> BaseChatModel:
    """Create an OpenAI LLM instance."""
    from langchain_openai import ChatOpenAI

    api_key = api_key or config.openai_api_key
    if not api_key:
        raise ValueError("OPENAI_API_KEY is not set. Set it in your .env file or register a custom model with a key.")

    return ChatOpenAI(
        model=model,
        api_key=api_key,
        base_url=base_url,
        temperature=temperature,
        max_tokens=max_tokens,
    )


def _get_anthropic_llm(model: str, temperature: float, max_tokens: int, api_key: str | None = None) -> BaseChatModel:
    """Create an Anthropic LLM instance."""
    from langchain_anthropic import ChatAnthropic

    api_key = api_key or config.anthropic_api_key
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY is not set. Set it in your .env file or register a custom model with a key.")

    return ChatAnthropic(
        model=model,
        api_key=api_key,
        temperature=temperature,
        max_tokens=max_tokens,
    )

def _get_ollama_llm(model: str, temperature: float, max_tokens: int, base_url: str | None = None) -> BaseChatModel:
    """Create an Ollama (Local) LLM instance."""
    from langchain_ollama import ChatOllama
    return ChatOllama(
        model=model,
        temperature=temperature,
        base_url=base_url or "http://localhost:11434"
    )


# ---------------------------------------------------------------------------
# Provider registry
# ---------------------------------------------------------------------------

PROVIDERS = {
    "groq": _get_groq_llm,
    "openai": _get_openai_llm,
    "anthropic": _get_anthropic_llm,
    "ollama": _get_ollama_llm,
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

    # 1. Search in hardcoded models
    custom_model_data = None
    if model not in ALL_MODELS:
        # 2. Search in custom DB models
        with Session(engine) as s:
            custom_model_data = s.exec(select(LLMModelConfig).where(LLMModelConfig.name == model)).first()
            if custom_model_data:
                provider = custom_model_data.provider
                model = custom_model_data.model_id
                logger.info("Using custom model from DB", name=custom_model_data.name, provider=provider)

    if provider not in PROVIDERS:
        raise ValueError(
            f"Unknown provider '{provider}'. "
            f"Supported: {', '.join(PROVIDERS.keys())}"
        )

    logger.info("Initializing LLM", provider=provider, model=model)
    
    # Inject custom credentials if available
    api_key = custom_model_data.api_key if custom_model_data else None
    base_url = custom_model_data.base_url if custom_model_data else None
    
    if provider == "ollama":
        return _get_ollama_llm(model, temperature, max_tokens, base_url)
    
    return PROVIDERS[provider](model, temperature, max_tokens, api_key=api_key)
