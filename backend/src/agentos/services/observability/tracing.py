from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.semconv.resource import ResourceAttributes
import os

def setup_tracing(service_name: str = "agentos-backend", endpoint: str = None) -> None:
    """
    Configures OpenTelemetry tracing for AgentOS.
    Sends traces to an OTLP collector if an endpoint is provided, 
    otherwise falls back to Console output in development.
    """
    
    resource = Resource.create({
        ResourceAttributes.SERVICE_NAME: service_name,
        ResourceAttributes.SERVICE_VERSION: "0.1.0",
        "deployment.environment": os.getenv("ENV", "development")
    })

    provider = TracerProvider(resource=resource)
    
    if endpoint or os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT"):
        # Export to OTLP collector (Jaeger, Langfuse, Loki, etc.)
        exporter = OTLPSpanExporter(endpoint=endpoint or os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT"))
        processor = BatchSpanProcessor(exporter)
    else:
        # Development: Export to Console
        exporter = ConsoleSpanExporter()
        processor = BatchSpanProcessor(exporter)

    provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)

def get_tracer(name: str = "agentos"):
    """Returns a tracer instance."""
    return trace.get_tracer(name)
