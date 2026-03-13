"""
Celery configuration for AgentOS.

Initializes the Celery app with Redis as the broker and backend.
"""

from celery import Celery
from dotenv import load_dotenv
from agentos.core.runtime.config import config
from agentos.services.observability.logging import setup_logging
from agentos.services.observability.tracing import setup_tracing

# Load .env into os.environ so OpenTelemetry can read OTEL_EXPORTER_OTLP_ENDPOINT
load_dotenv()

# Initialize observability for the Celery worker
setup_logging()
setup_tracing()

# Initialize Celery

# broker: Where messages are sent (Redis)
# backend: Where results are stored (Redis)
celery_app = Celery(
    "agentos",
    broker=config.redis_url,
    backend=config.redis_url,
    include=["agentos.core.orchestrator.tasks"]
)

# Optional: Configure more Celery settings
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes max
)

if __name__ == "__main__":
    celery_app.start()
