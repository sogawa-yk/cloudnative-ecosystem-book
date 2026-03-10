"""Order Service - FastAPI-based microservice for order management."""

import logging
import os
import signal
import sys
import time
import uuid
from contextlib import asynccontextmanager
from decimal import Decimal

import httpx
import psycopg2
import psycopg2.pool
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.semconv.resource import ResourceAttributes
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from pydantic import BaseModel
from pythonjsonlogger import json as json_logger

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DATABASE_HOST = os.getenv("DATABASE_HOST", "localhost")
DATABASE_PORT = os.getenv("DATABASE_PORT", "5432")
DATABASE_NAME = os.getenv("DATABASE_NAME", "orders")
DATABASE_USER = os.getenv("DATABASE_USER", "postgres")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD", "postgres")
PRODUCT_SERVICE_URL = os.getenv("PRODUCT_SERVICE_URL", "http://product-service:8081")
OTEL_ENDPOINT = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "otel-collector.book-observability:4317")
PORT = int(os.getenv("PORT", "8082"))

# ---------------------------------------------------------------------------
# Structured JSON Logging
# ---------------------------------------------------------------------------

logger = logging.getLogger("order-service")
logger.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stdout)
formatter = json_logger.JsonFormatter(
    fmt="%(asctime)s %(levelname)s %(name)s %(message)s",
    rename_fields={"asctime": "time", "levelname": "level", "name": "logger"},
)
handler.setFormatter(formatter)
logger.handlers = [handler]

# ---------------------------------------------------------------------------
# Prometheus Metrics
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

# ---------------------------------------------------------------------------
# OpenTelemetry Tracing
# ---------------------------------------------------------------------------

resource = Resource.create({ResourceAttributes.SERVICE_NAME: "order-service",
                            ResourceAttributes.SERVICE_VERSION: "1.0.0"})

tracer_provider = TracerProvider(resource=resource)
otlp_exporter = OTLPSpanExporter(endpoint=OTEL_ENDPOINT, insecure=True)
tracer_provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
trace.set_tracer_provider(tracer_provider)

tracer = trace.get_tracer("order-service")

# Instrument outgoing httpx calls
HTTPXClientInstrumentor().instrument()

# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------

db_pool: psycopg2.pool.ThreadedConnectionPool | None = None


def connect_db() -> psycopg2.pool.ThreadedConnectionPool:
    """Create a threaded connection pool to PostgreSQL."""
    pool = psycopg2.pool.ThreadedConnectionPool(
        minconn=2,
        maxconn=25,
        host=DATABASE_HOST,
        port=DATABASE_PORT,
        dbname=DATABASE_NAME,
        user=DATABASE_USER,
        password=DATABASE_PASSWORD,
    )
    logger.info("connected to database",
                extra={"host": DATABASE_HOST, "port": DATABASE_PORT, "database": DATABASE_NAME})
    return pool


def create_table() -> None:
    """Auto-create the orders table if it does not exist."""
    conn = db_pool.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS orders (
                    id SERIAL PRIMARY KEY,
                    product_id INTEGER NOT NULL,
                    quantity INTEGER NOT NULL,
                    total NUMERIC(10,2) NOT NULL,
                    status VARCHAR(50) NOT NULL DEFAULT 'pending'
                )
            """)
            conn.commit()
        logger.info("orders table ready")
    finally:
        db_pool.putconn(conn)


# ---------------------------------------------------------------------------
# Pydantic Models
# ---------------------------------------------------------------------------

class OrderCreate(BaseModel):
    product_id: int
    quantity: int


class OrderResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    total: float
    status: str


# ---------------------------------------------------------------------------
# Application Lifespan (startup / shutdown)
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    global db_pool
    # Startup
    db_pool = connect_db()
    create_table()
    logger.info("starting order-service", extra={"port": PORT})
    yield
    # Shutdown
    logger.info("shutting down server")
    if db_pool:
        db_pool.closeall()
    tracer_provider.shutdown()
    logger.info("server stopped")


app = FastAPI(title="order-service", lifespan=lifespan)

# Instrument FastAPI with OpenTelemetry
FastAPIInstrumentor.instrument_app(app)

# ---------------------------------------------------------------------------
# Middleware – X-Request-ID & Metrics
# ---------------------------------------------------------------------------

@app.middleware("http")
async def request_middleware(request: Request, call_next):
    start = time.time()

    # X-Request-ID propagation
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    request.state.request_id = request_id

    response: Response = await call_next(request)

    response.headers["X-Request-ID"] = request_id

    duration = time.time() - start
    path = request.url.path
    method = request.method
    status = str(response.status_code)

    # Normalize path for metrics
    metric_path = path
    if path.startswith("/api/orders/") and path != "/api/orders/":
        metric_path = "/api/orders/{id}"

    http_requests_total.labels(method=method, path=metric_path, status=status).inc()
    http_request_duration_seconds.labels(method=method, path=metric_path).observe(duration)

    logger.info("request completed",
                extra={"method": method, "path": path, "status": int(response.status_code),
                       "duration_ms": int(duration * 1000), "request_id": request_id})

    return response


# ---------------------------------------------------------------------------
# Helper – fetch product from product-service
# ---------------------------------------------------------------------------

async def fetch_product(product_id: int) -> dict:
    """Call product-service to retrieve product details."""
    with tracer.start_as_current_span("http.client.get_product"):
        url = f"{PRODUCT_SERVICE_URL}/api/products/{product_id}"
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url)
        if resp.status_code != 200:
            raise HTTPException(status_code=502,
                                detail="failed to fetch product information")
        return resp.json()


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/api/orders/", response_model=list[OrderResponse])
async def list_orders():
    """List all orders."""
    with tracer.start_as_current_span("db.query.list_orders"):
        conn = db_pool.getconn()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT id, product_id, quantity, total, status FROM orders ORDER BY id")
                rows = cur.fetchall()
        finally:
            db_pool.putconn(conn)

    return [
        OrderResponse(id=r[0], product_id=r[1], quantity=r[2], total=float(r[3]), status=r[4])
        for r in rows
    ]


@app.post("/api/orders/", response_model=OrderResponse, status_code=201)
async def create_order(order_in: OrderCreate):
    """Create a new order."""
    if order_in.product_id <= 0 or order_in.quantity <= 0:
        raise HTTPException(status_code=400, detail="product_id and quantity must be positive")

    product = await fetch_product(order_in.product_id)
    price = product.get("price", 0)
    total = round(price * order_in.quantity, 2)

    with tracer.start_as_current_span("db.insert.order"):
        conn = db_pool.getconn()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO orders (product_id, quantity, total, status) "
                    "VALUES (%s, %s, %s, %s) RETURNING id, product_id, quantity, total, status",
                    (order_in.product_id, order_in.quantity, total, "pending"),
                )
                row = cur.fetchone()
                conn.commit()
        finally:
            db_pool.putconn(conn)

    order = OrderResponse(id=row[0], product_id=row[1], quantity=row[2],
                          total=float(row[3]), status=row[4])
    logger.info("order created",
                extra={"order_id": order.id, "product_id": order.product_id, "total": order.total})
    return order


@app.get("/api/orders/{order_id}", response_model=OrderResponse)
async def get_order(order_id: int):
    """Get a single order by ID."""
    with tracer.start_as_current_span("db.query.get_order"):
        conn = db_pool.getconn()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT id, product_id, quantity, total, status FROM orders WHERE id = %s",
                    (order_id,),
                )
                row = cur.fetchone()
        finally:
            db_pool.putconn(conn)

    if row is None:
        raise HTTPException(status_code=404, detail="order not found")

    return OrderResponse(id=row[0], product_id=row[1], quantity=row[2],
                         total=float(row[3]), status=row[4])


@app.get("/health")
async def health():
    """Health check – verifies database connectivity."""
    try:
        conn = db_pool.getconn()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
        finally:
            db_pool.putconn(conn)
        return {"status": "healthy", "service": "order-service"}
    except Exception:
        logger.error("health check failed")
        return JSONResponse(status_code=503,
                            content={"status": "unhealthy", "service": "order-service"})


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    data = generate_latest()
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn

    # Handle SIGTERM for graceful shutdown
    signal.signal(signal.SIGTERM, lambda *_: sys.exit(0))

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=PORT,
        log_level="info",
    )
