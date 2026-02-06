import logging

try:
    from opentelemetry import trace
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import SimpleSpanProcessor, ConsoleSpanExporter
    OTEL_AVAILABLE = True
except Exception:
    OTEL_AVAILABLE = False


def setup_tracing(service_name: str = "cryptswarm"):
    """Initialize basic OpenTelemetry tracing with a console exporter.

    If OpenTelemetry packages are not installed, this becomes a no-op and logs a warning.
    """
    if not OTEL_AVAILABLE:
        logging.warning("OpenTelemetry not available; tracing disabled")
        return

    resource = Resource.create({"service.name": service_name})
    provider = TracerProvider(resource=resource)
    processor = SimpleSpanProcessor(ConsoleSpanExporter())
    provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)
    logging.info("Tracing initialized (ConsoleSpanExporter)")
