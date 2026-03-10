import logging
import os
import signal
import sys
import time
import uuid

import psycopg2
import psycopg2.extras
import uvicorn
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.semconv.resource import ResourceAttributes
from opentelemetry.trace import StatusCode
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from pydantic import BaseModel
from pythonjsonlogger import jsonlogger

# ---------------------------------------------------------------------------
# Logging (structured JSON)
# ---------------------------------------------------------------------------

log_handler = logging.StreamHandler(sys.stdout)
formatter = jsonlogger.JsonFormatter(
    fmt="%(asctime)s %(levelname)s %(name)s %(message)s",
    rename_fields={"asctime": "time", "levelname": "level", "name": "logger"},
)
log_handler.setFormatter(formatter)

logger = logging.getLogger("product-service")
logger.setLevel(logging.INFO)
logger.addHandler(log_handler)
logger.propagate = False

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

# ---------------------------------------------------------------------------
# OpenTelemetry tracing
# ---------------------------------------------------------------------------

def init_tracer() -> TracerProvider:
    endpoint = os.getenv(
        "OTEL_EXPORTER_OTLP_ENDPOINT",
        "otel-collector.book-observability:4317",
    )
    resource = Resource.create({ResourceAttributes.SERVICE_NAME: "product-service"})
    provider = TracerProvider(resource=resource)
    exporter = OTLPSpanExporter(endpoint=endpoint, insecure=True)
    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)
    return provider


tracer_provider = init_tracer()
tracer = trace.get_tracer("product-service")

# ---------------------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------------------

def get_env(key: str, default: str = "") -> str:
    return os.getenv(key, default)


def connect_db():
    """Return a new psycopg2 connection."""
    conn = psycopg2.connect(
        host=get_env("DATABASE_HOST", "localhost"),
        port=int(get_env("DATABASE_PORT", "5432")),
        dbname=get_env("DATABASE_NAME", "products"),
        user=get_env("DATABASE_USER", "postgres"),
        password=get_env("DATABASE_PASSWORD", ""),
    )
    conn.autocommit = True
    return conn


db_conn: psycopg2.extensions.connection = None  # type: ignore[assignment]


def ensure_db():
    """Return the global database connection, reconnecting if necessary."""
    global db_conn
    if db_conn is None or db_conn.closed:
        db_conn = connect_db()
        logger.info(
            "connected to database",
            extra={
                "host": get_env("DATABASE_HOST", "localhost"),
                "port": get_env("DATABASE_PORT", "5432"),
                "database": get_env("DATABASE_NAME", "products"),
            },
        )
    return db_conn


def create_table():
    conn = ensure_db()
    with conn.cursor() as cur:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS products (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                price DOUBLE PRECISION NOT NULL
            )
            """
        )
    logger.info("products table ready")


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------

class ProductCreate(BaseModel):
    name: str
    price: float


class Product(BaseModel):
    id: int
    name: str
    price: float


# ---------------------------------------------------------------------------
# Path normalisation (for metrics labels)
# ---------------------------------------------------------------------------

def normalize_path(path: str) -> str:
    prefix = "/api/products/"
    if len(path) > len(prefix):
        return "/api/products/{id}"
    return path


# ---------------------------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------------------------

app = FastAPI(title="product-service")


@app.on_event("startup")
def startup_event():
    create_table()


@app.on_event("shutdown")
def shutdown_event():
    global db_conn
    if db_conn and not db_conn.closed:
        db_conn.close()
        logger.info("database connection closed")
    tracer_provider.shutdown()
    logger.info("tracer provider shut down")


# ---------------------------------------------------------------------------
# Middleware: X-Request-ID
# ---------------------------------------------------------------------------

@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    request.state.request_id = request_id
    response: Response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/health")
def health():
    start = time.time()
    try:
        conn = ensure_db()
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
        status_text = "ok"
        code = 200
    except Exception as exc:
        logger.error("health check failed", extra={"error": str(exc)})
        status_text = "unhealthy"
        code = 503

    duration = time.time() - start
    http_request_duration_seconds.labels(method="GET", path="/health").observe(duration)
    http_requests_total.labels(method="GET", path="/health", status=str(code)).inc()

    if code != 200:
        return JSONResponse(content={"status": status_text}, status_code=code)
    return {"status": status_text}


@app.get("/metrics")
def metrics():
    data = generate_latest()
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)


@app.get("/api/products/")
def list_products(request: Request):
    start = time.time()
    request_id = getattr(request.state, "request_id", "")

    with tracer.start_as_current_span("db.query.listProducts") as span:
        try:
            conn = ensure_db()
            with conn.cursor() as cur:
                cur.execute("SELECT id, name, price FROM products ORDER BY id")
                rows = cur.fetchall()
        except Exception as exc:
            logger.error(
                "failed to query products",
                extra={"error": str(exc), "requestID": request_id},
            )
            span.set_status(StatusCode.ERROR, str(exc))
            http_requests_total.labels(
                method="GET", path="/api/products/", status="500"
            ).inc()
            raise HTTPException(status_code=500, detail="failed to query products")

    products = [Product(id=r[0], name=r[1], price=r[2]) for r in rows]

    duration = time.time() - start
    http_request_duration_seconds.labels(method="GET", path="/api/products/").observe(
        duration
    )
    http_requests_total.labels(
        method="GET", path="/api/products/", status="200"
    ).inc()
    return products


@app.post("/api/products/", status_code=201)
def create_product(product: ProductCreate, request: Request):
    start = time.time()
    request_id = getattr(request.state, "request_id", "")

    with tracer.start_as_current_span(
        "db.exec.createProduct",
        attributes={
            "product.name": product.name,
            "product.price": product.price,
        },
    ) as span:
        try:
            conn = ensure_db()
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO products (name, price) VALUES (%s, %s) RETURNING id",
                    (product.name, product.price),
                )
                new_id = cur.fetchone()[0]
        except Exception as exc:
            logger.error(
                "failed to insert product",
                extra={"error": str(exc), "requestID": request_id},
            )
            span.set_status(StatusCode.ERROR, str(exc))
            http_requests_total.labels(
                method="POST", path="/api/products/", status="500"
            ).inc()
            raise HTTPException(status_code=500, detail="failed to create product")

    created = Product(id=new_id, name=product.name, price=product.price)
    logger.info(
        "product created",
        extra={"id": created.id, "name": created.name, "requestID": request_id},
    )

    duration = time.time() - start
    http_request_duration_seconds.labels(method="POST", path="/api/products/").observe(
        duration
    )
    http_requests_total.labels(
        method="POST", path="/api/products/", status="201"
    ).inc()
    return created


@app.get("/api/products/{product_id}")
def get_product(product_id: int, request: Request):
    start = time.time()
    request_id = getattr(request.state, "request_id", "")

    with tracer.start_as_current_span(
        "db.query.getProduct",
        attributes={"product.id": product_id},
    ) as span:
        try:
            conn = ensure_db()
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT id, name, price FROM products WHERE id = %s",
                    (product_id,),
                )
                row = cur.fetchone()
        except Exception as exc:
            logger.error(
                "failed to query product",
                extra={
                    "error": str(exc),
                    "id": product_id,
                    "requestID": request_id,
                },
            )
            span.set_status(StatusCode.ERROR, str(exc))
            http_requests_total.labels(
                method="GET", path="/api/products/{id}", status="500"
            ).inc()
            raise HTTPException(status_code=500, detail="failed to query product")

    if row is None:
        duration = time.time() - start
        http_request_duration_seconds.labels(
            method="GET", path="/api/products/{id}"
        ).observe(duration)
        http_requests_total.labels(
            method="GET", path="/api/products/{id}", status="404"
        ).inc()
        raise HTTPException(status_code=404, detail="product not found")

    product = Product(id=row[0], name=row[1], price=row[2])

    duration = time.time() - start
    http_request_duration_seconds.labels(
        method="GET", path="/api/products/{id}"
    ).observe(duration)
    http_requests_total.labels(
        method="GET", path="/api/products/{id}", status="200"
    ).inc()
    return product


# ---------------------------------------------------------------------------
# Instrument FastAPI with OpenTelemetry
# ---------------------------------------------------------------------------

FastAPIInstrumentor.instrument_app(app)

# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    def handle_signal(signum, frame):
        logger.info("received shutdown signal", extra={"signal": signum})
        sys.exit(0)

    signal.signal(signal.SIGTERM, handle_signal)
    signal.signal(signal.SIGINT, handle_signal)

    logger.info("starting product-service", extra={"port": 8081})
    uvicorn.run(app, host="0.0.0.0", port=8081, log_level="info")
