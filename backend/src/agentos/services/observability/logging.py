
import logging
import sys
import structlog
from typing import Any

def setup_logging(level: str = "INFO", json_format: bool = False) -> None:
    """
    Configures structured logging for AgentOS.
    In development, it uses pretty console output.
    In production (json_format=True), it outputs structured JSON.
    """
    
    # Standard library logging configuration
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, level.upper()),
    )

    processors: list[Any] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.format_exc_info,
        structlog.processors.TimeStamper(fmt="iso"),
    ]

    if json_format:
        # Production: JSON output
        processors.append(structlog.processors.JSONRenderer())
    else:
        # Development: Pretty console output
        processors.append(structlog.dev.ConsoleRenderer(colors=True))

    structlog.configure(
        processors=processors,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

logger = structlog.get_logger()
