
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

    # Add OpenTelemetry trace correlation
    try:
        from opentelemetry import trace
        def add_otel_trace_id(_, __, event_dict):
            span = trace.get_current_span()
            if span.get_span_context().is_valid:
                event_dict["trace_id"] = format(span.get_span_context().trace_id, '032x')
                event_dict["span_id"] = format(span.get_span_context().span_id, '016x')
            return event_dict
        processors.insert(1, add_otel_trace_id)
    except ImportError:
        pass

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
