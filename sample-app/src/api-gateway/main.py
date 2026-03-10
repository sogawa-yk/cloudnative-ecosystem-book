"""API Gateway service using FastAPI with reverse proxy, metrics, and tracing."""

import asyncio
import logging
import os
import signal
import sys
import time
import uuid

import httpx
import uvicorn
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from prometheus_client import Counter, Gauge, Histogram, generate_latest, CONTENT_TYPE_LATEST
from pythonjsonlogger import json as json_logger

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.propagate import set_global_textmap
from opentelemetry.propagators.composite import CompositePropagator
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.semconv.resource import ResourceAttributes
from opentelemetry.propagators.textmap import DefaultTextMapPropagator
from opentelemetry.trace.propagation import get_current_span

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

PRODUCT_SERVICE_URL = os.getenv("PRODUCT_SERVICE_URL", "http://product-service:8081")
ORDER_SERVICE_URL = os.getenv("ORDER_SERVICE_URL", "http://order-service:8082")
OTEL_EXPORTER_OTLP_ENDPOINT = os.getenv(
    "OTEL_EXPORTER_OTLP_ENDPOINT", "otel-collector.book-observability:4317"
)

# ---------------------------------------------------------------------------
# Structured JSON logging
# ---------------------------------------------------------------------------

logger = logging.getLogger("api-gateway")
logger.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stdout)
formatter = json_logger.JsonFormatter(
    fmt="%(asctime)s %(levelname)s %(name)s %(message)s",
    rename_fields={"asctime": "time", "levelname": "level", "name": "logger"},
)
handler.setFormatter(formatter)
logger.handlers = [handler]

# ---------------------------------------------------------------------------
# Prometheus metrics
# ---------------------------------------------------------------------------

http_requests_total = Counter(
    "http_requests_total",
    "Total number of HTTP requests.",
    ["method", "path", "status"],
)

http_request_duration_seconds = Histogram(
    "http_request_duration_seconds",
    "Duration of HTTP requests in seconds.",
    ["method", "path"],
)

active_connections = Gauge(
    "active_connections",
    "Number of active connections.",
)

# ---------------------------------------------------------------------------
# OpenTelemetry tracing
# ---------------------------------------------------------------------------


def init_tracer_provider() -> TracerProvider:
    """Set up the OpenTelemetry TracerProvider with an OTLP gRPC exporter."""
    resource = Resource.create(
        {
            ResourceAttributes.SERVICE_NAME: "api-gateway",
            ResourceAttributes.SERVICE_VERSION: "1.0.0",
        }
    )

    exporter = OTLPSpanExporter(
        endpoint=OTEL_EXPORTER_OTLP_ENDPOINT,
        insecure=True,
    )

    provider = TracerProvider(resource=resource)
    provider.add_span_processor(BatchSpanProcessor(exporter))

    trace.set_tracer_provider(provider)

    return provider


# ---------------------------------------------------------------------------
# Path normalisation (reduce cardinality for metrics)
# ---------------------------------------------------------------------------


def normalize_path(path: str) -> str:
    """Keep only the route prefix for metric labels."""
    if path.startswith("/api/products"):
        return "/api/products"
    if path.startswith("/api/orders"):
        return "/api/orders"
    return path


# ---------------------------------------------------------------------------
# Reverse-proxy helper
# ---------------------------------------------------------------------------

# A shared httpx.AsyncClient is created at startup and closed at shutdown.
_http_client: httpx.AsyncClient | None = None


async def proxy_request(request: Request, target_base_url: str) -> Response:
    """Forward the incoming request to a backend service and return its response."""
    # Build the target URL preserving path and query string.
    target_url = target_base_url.rstrip("/") + request.url.path
    if request.url.query:
        target_url = f"{target_url}?{request.url.query}"

    # Forward headers (drop Host so the backend receives the correct one).
    headers = dict(request.headers)
    headers.pop("host", None)

    body = await request.body()

    try:
        resp = await _http_client.request(
            method=request.method,
            url=target_url,
            headers=headers,
            content=body,
            timeout=15.0,
        )
    except httpx.HTTPError as exc:
        logger.error(
            "proxy error",
            extra={
                "error": str(exc),
                "target": target_base_url,
                "path": request.url.path,
                "request_id": request.headers.get("X-Request-ID", ""),
            },
        )
        return Response(status_code=502)

    # Return the upstream response, preserving status, headers, and body.
    excluded_headers = {"transfer-encoding", "content-encoding", "content-length"}
    response_headers = {
        k: v for k, v in resp.headers.items() if k.lower() not in excluded_headers
    }

    return Response(
        content=resp.content,
        status_code=resp.status_code,
        headers=response_headers,
    )


# ---------------------------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------------------------

app = FastAPI(title="api-gateway")


# --- Startup / Shutdown ----------------------------------------------------

tracer_provider: TracerProvider | None = None


@app.on_event("startup")
async def startup_event() -> None:
    global _http_client, tracer_provider

    # Initialise tracing.
    tracer_provider = init_tracer_provider()

    # Instrument httpx *before* creating the client.
    HTTPXClientInstrumentor().instrument()

    _http_client = httpx.AsyncClient()

    logger.info("starting api-gateway", extra={"addr": ":8080"})


@app.on_event("shutdown")
async def shutdown_event() -> None:
    global _http_client

    if _http_client is not None:
        await _http_client.aclose()
        _http_client = None

    if tracer_provider is not None:
        tracer_provider.shutdown()

    logger.info("server stopped gracefully")


# --- Middleware ------------------------------------------------------------


@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    """Ensure every request carries an X-Request-ID."""
    request_id = request.headers.get("X-Request-ID")
    if not request_id:
        request_id = str(uuid.uuid4())
        # MutableHeaders allows adding headers to the incoming request scope.
        request.scope["headers"] = [
            *[
                (k, v)
                for k, v in request.scope["headers"]
                if k.lower() != b"x-request-id"
            ],
            (b"x-request-id", request_id.encode()),
        ]

    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    """Record Prometheus metrics and emit a structured access log."""
    # Skip metrics for /health and /metrics endpoints.
    if request.url.path in ("/health", "/metrics"):
        return await call_next(request)

    active_connections.inc()
    start = time.perf_counter()

    try:
        response = await call_next(request)
    except Exception:
        active_connections.dec()
        raise

    duration = time.perf_counter() - start
    active_connections.dec()

    path = normalize_path(request.url.path)
    status_text = str(response.status_code)

    http_requests_total.labels(
        method=request.method, path=path, status=status_text
    ).inc()
    http_request_duration_seconds.labels(method=request.method, path=path).observe(
        duration
    )

    logger.info(
        "request completed",
        extra={
            "method": request.method,
            "path": request.url.path,
            "status": response.status_code,
            "duration_ms": round(duration * 1000, 2),
            "request_id": request.headers.get("X-Request-ID", ""),
        },
    )

    return response


# --- Routes ----------------------------------------------------------------


@app.get("/health")
async def health():
    """Health check endpoint."""
    return JSONResponse({"status": "healthy"})


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )


@app.api_route(
    "/api/products/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"],
)
async def proxy_products(request: Request):
    """Reverse-proxy to product-service."""
    return await proxy_request(request, PRODUCT_SERVICE_URL)


@app.api_route(
    "/api/orders/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"],
)
async def proxy_orders(request: Request):
    """Reverse-proxy to order-service."""
    return await proxy_request(request, ORDER_SERVICE_URL)


# Instrument FastAPI with OpenTelemetry (must be called after routes are defined).
FastAPIInstrumentor.instrument_app(app, excluded_urls="health,metrics")

# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> None:
    """Run the uvicorn server with graceful shutdown support."""
    shutdown_event_obj = asyncio.Event()

    def _signal_handler(sig, _frame):
        logger.info("shutting down server", extra={"signal": signal.Signals(sig).name})
        shutdown_event_obj.set()

    signal.signal(signal.SIGINT, _signal_handler)
    signal.signal(signal.SIGTERM, _signal_handler)

    config = uvicorn.Config(
        app=app,
        host="0.0.0.0",
        port=8080,
        log_level="info",
    )
    server = uvicorn.Server(config)
    server.run()


if __name__ == "__main__":
    main()
