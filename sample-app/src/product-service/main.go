package main

import (
	"context"
	"database/sql"
	"encoding/json"
	"fmt"
	"log/slog"
	"net/http"
	"os"
	"os/signal"
	"strconv"
	"syscall"
	"time"

	"github.com/google/uuid"
	_ "github.com/lib/pq"
	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promhttp"
	"go.opentelemetry.io/contrib/instrumentation/net/http/otelhttp"
	"go.opentelemetry.io/otel"
	"go.opentelemetry.io/otel/attribute"
	"go.opentelemetry.io/otel/exporters/otlp/otlptrace/otlptracegrpc"
	"go.opentelemetry.io/otel/sdk/resource"
	sdktrace "go.opentelemetry.io/otel/sdk/trace"
	semconv "go.opentelemetry.io/otel/semconv/v1.24.0"
	"go.opentelemetry.io/otel/trace"
)

// Product represents a product entity.
type Product struct {
	ID    int     `json:"id"`
	Name  string  `json:"name"`
	Price float64 `json:"price"`
}

var (
	db     *sql.DB
	logger *slog.Logger
	tracer trace.Tracer

	httpRequestsTotal = prometheus.NewCounterVec(
		prometheus.CounterOpts{
			Name: "http_requests_total",
			Help: "Total number of HTTP requests.",
		},
		[]string{"method", "path", "status"},
	)

	httpRequestDuration = prometheus.NewHistogramVec(
		prometheus.HistogramOpts{
			Name:    "http_request_duration_seconds",
			Help:    "Duration of HTTP requests in seconds.",
			Buckets: prometheus.DefBuckets,
		},
		[]string{"method", "path"},
	)
)

func init() {
	prometheus.MustRegister(httpRequestsTotal)
	prometheus.MustRegister(httpRequestDuration)
}

func main() {
	logger = slog.New(slog.NewJSONHandler(os.Stdout, nil))
	slog.SetDefault(logger)

	// Initialize OpenTelemetry
	shutdown, err := initTracer()
	if err != nil {
		logger.Error("failed to initialize tracer", "error", err)
		os.Exit(1)
	}
	defer shutdown(context.Background())

	tracer = otel.Tracer("product-service")

	// Connect to PostgreSQL
	if err := connectDB(); err != nil {
		logger.Error("failed to connect to database", "error", err)
		os.Exit(1)
	}
	defer db.Close()

	// Auto-create table
	if err := createTable(); err != nil {
		logger.Error("failed to create table", "error", err)
		os.Exit(1)
	}

	// Set up HTTP routes
	mux := http.NewServeMux()
	mux.HandleFunc("/api/products/", productsHandler)
	mux.HandleFunc("/health", healthHandler)
	mux.Handle("/metrics", promhttp.Handler())

	// Wrap with OpenTelemetry HTTP instrumentation
	handler := otelhttp.NewHandler(mux, "product-service")
	// Wrap with request ID middleware
	handler2 := requestIDMiddleware(handler)

	srv := &http.Server{
		Addr:    ":8081",
		Handler: handler2,
	}

	// Graceful shutdown
	done := make(chan os.Signal, 1)
	signal.Notify(done, os.Interrupt, syscall.SIGTERM)

	go func() {
		logger.Info("starting product-service", "port", 8081)
		if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			logger.Error("server error", "error", err)
			os.Exit(1)
		}
	}()

	<-done
	logger.Info("shutting down server")

	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	if err := srv.Shutdown(ctx); err != nil {
		logger.Error("server shutdown error", "error", err)
	}
	logger.Info("server stopped")
}

func initTracer() (func(context.Context) error, error) {
	endpoint := os.Getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
	if endpoint == "" {
		endpoint = "otel-collector.book-observability:4317"
	}

	ctx := context.Background()

	exporter, err := otlptracegrpc.New(ctx,
		otlptracegrpc.WithEndpoint(endpoint),
		otlptracegrpc.WithInsecure(),
	)
	if err != nil {
		return nil, fmt.Errorf("failed to create OTLP exporter: %w", err)
	}

	res, err := resource.New(ctx,
		resource.WithAttributes(
			semconv.ServiceNameKey.String("product-service"),
		),
	)
	if err != nil {
		return nil, fmt.Errorf("failed to create resource: %w", err)
	}

	tp := sdktrace.NewTracerProvider(
		sdktrace.WithBatcher(exporter),
		sdktrace.WithResource(res),
	)
	otel.SetTracerProvider(tp)

	return tp.Shutdown, nil
}

func getEnv(key, defaultValue string) string {
	if v := os.Getenv(key); v != "" {
		return v
	}
	return defaultValue
}

func connectDB() error {
	host := getEnv("DATABASE_HOST", "localhost")
	port := getEnv("DATABASE_PORT", "5432")
	dbname := getEnv("DATABASE_NAME", "products")
	user := getEnv("DATABASE_USER", "postgres")
	password := getEnv("DATABASE_PASSWORD", "")

	dsn := fmt.Sprintf("host=%s port=%s user=%s password=%s dbname=%s sslmode=disable",
		host, port, user, password, dbname)

	var err error
	db, err = sql.Open("postgres", dsn)
	if err != nil {
		return fmt.Errorf("failed to open database: %w", err)
	}

	if err := db.Ping(); err != nil {
		return fmt.Errorf("failed to ping database: %w", err)
	}

	logger.Info("connected to database", "host", host, "port", port, "database", dbname)
	return nil
}

func createTable() error {
	query := `
		CREATE TABLE IF NOT EXISTS products (
			id SERIAL PRIMARY KEY,
			name TEXT NOT NULL,
			price DOUBLE PRECISION NOT NULL
		)
	`
	_, err := db.Exec(query)
	if err != nil {
		return fmt.Errorf("failed to create products table: %w", err)
	}
	logger.Info("products table ready")
	return nil
}

func requestIDMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		requestID := r.Header.Get("X-Request-ID")
		if requestID == "" {
			requestID = uuid.New().String()
		}
		w.Header().Set("X-Request-ID", requestID)
		ctx := context.WithValue(r.Context(), contextKeyRequestID, requestID)
		next.ServeHTTP(w, r.WithContext(ctx))
	})
}

type contextKey string

const contextKeyRequestID = contextKey("requestID")

func getRequestID(ctx context.Context) string {
	if v, ok := ctx.Value(contextKeyRequestID).(string); ok {
		return v
	}
	return ""
}

func productsHandler(w http.ResponseWriter, r *http.Request) {
	// Route: /api/products/ or /api/products/{id}
	path := r.URL.Path
	// Extract ID from path if present
	const prefix = "/api/products/"
	idStr := ""
	if len(path) > len(prefix) {
		idStr = path[len(prefix):]
	}

	if idStr == "" {
		switch r.Method {
		case http.MethodGet:
			listProducts(w, r)
		case http.MethodPost:
			createProduct(w, r)
		default:
			writeError(w, r, http.StatusMethodNotAllowed, "method not allowed")
		}
	} else {
		id, err := strconv.Atoi(idStr)
		if err != nil {
			writeError(w, r, http.StatusBadRequest, "invalid product ID")
			return
		}
		switch r.Method {
		case http.MethodGet:
			getProduct(w, r, id)
		default:
			writeError(w, r, http.StatusMethodNotAllowed, "method not allowed")
		}
	}
}

func listProducts(w http.ResponseWriter, r *http.Request) {
	ctx := r.Context()
	start := time.Now()

	ctx, span := tracer.Start(ctx, "db.query.listProducts")
	rows, err := db.QueryContext(ctx, "SELECT id, name, price FROM products ORDER BY id")
	span.End()

	if err != nil {
		logger.Error("failed to query products", "error", err, "requestID", getRequestID(ctx))
		writeError(w, r, http.StatusInternalServerError, "failed to query products")
		return
	}
	defer rows.Close()

	products := make([]Product, 0)
	for rows.Next() {
		var p Product
		if err := rows.Scan(&p.ID, &p.Name, &p.Price); err != nil {
			logger.Error("failed to scan product", "error", err, "requestID", getRequestID(ctx))
			writeError(w, r, http.StatusInternalServerError, "failed to scan product")
			return
		}
		products = append(products, p)
	}
	if err := rows.Err(); err != nil {
		logger.Error("rows iteration error", "error", err, "requestID", getRequestID(ctx))
		writeError(w, r, http.StatusInternalServerError, "failed to read products")
		return
	}

	writeJSON(w, r, http.StatusOK, products)
	duration := time.Since(start).Seconds()
	httpRequestDuration.WithLabelValues(r.Method, "/api/products/").Observe(duration)
}

func createProduct(w http.ResponseWriter, r *http.Request) {
	ctx := r.Context()
	start := time.Now()

	var p Product
	if err := json.NewDecoder(r.Body).Decode(&p); err != nil {
		writeError(w, r, http.StatusBadRequest, "invalid request body")
		return
	}

	ctx, span := tracer.Start(ctx, "db.exec.createProduct",
		trace.WithAttributes(
			attribute.String("product.name", p.Name),
			attribute.Float64("product.price", p.Price),
		),
	)
	err := db.QueryRowContext(ctx,
		"INSERT INTO products (name, price) VALUES ($1, $2) RETURNING id",
		p.Name, p.Price,
	).Scan(&p.ID)
	span.End()

	if err != nil {
		logger.Error("failed to insert product", "error", err, "requestID", getRequestID(ctx))
		writeError(w, r, http.StatusInternalServerError, "failed to create product")
		return
	}

	logger.Info("product created", "id", p.ID, "name", p.Name, "requestID", getRequestID(ctx))
	writeJSON(w, r, http.StatusCreated, p)
	duration := time.Since(start).Seconds()
	httpRequestDuration.WithLabelValues(r.Method, "/api/products/").Observe(duration)
}

func getProduct(w http.ResponseWriter, r *http.Request, id int) {
	ctx := r.Context()
	start := time.Now()

	var p Product
	ctx, span := tracer.Start(ctx, "db.query.getProduct",
		trace.WithAttributes(attribute.Int("product.id", id)),
	)
	err := db.QueryRowContext(ctx,
		"SELECT id, name, price FROM products WHERE id = $1", id,
	).Scan(&p.ID, &p.Name, &p.Price)
	span.End()

	if err == sql.ErrNoRows {
		writeError(w, r, http.StatusNotFound, "product not found")
		duration := time.Since(start).Seconds()
		httpRequestDuration.WithLabelValues(r.Method, "/api/products/{id}").Observe(duration)
		return
	}
	if err != nil {
		logger.Error("failed to query product", "error", err, "id", id, "requestID", getRequestID(ctx))
		writeError(w, r, http.StatusInternalServerError, "failed to query product")
		return
	}

	writeJSON(w, r, http.StatusOK, p)
	duration := time.Since(start).Seconds()
	httpRequestDuration.WithLabelValues(r.Method, "/api/products/{id}").Observe(duration)
}

func healthHandler(w http.ResponseWriter, r *http.Request) {
	start := time.Now()

	status := "ok"
	code := http.StatusOK
	if err := db.Ping(); err != nil {
		status = "unhealthy"
		code = http.StatusServiceUnavailable
		logger.Error("health check failed", "error", err)
	}

	writeJSON(w, r, code, map[string]string{"status": status})
	duration := time.Since(start).Seconds()
	httpRequestDuration.WithLabelValues(r.Method, "/health").Observe(duration)
}

func writeJSON(w http.ResponseWriter, r *http.Request, status int, data interface{}) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	if err := json.NewEncoder(w).Encode(data); err != nil {
		logger.Error("failed to encode response", "error", err)
	}
	httpRequestsTotal.WithLabelValues(r.Method, normalizePath(r.URL.Path), strconv.Itoa(status)).Inc()
}

func writeError(w http.ResponseWriter, r *http.Request, status int, message string) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	resp := map[string]string{"error": message}
	if err := json.NewEncoder(w).Encode(resp); err != nil {
		logger.Error("failed to encode error response", "error", err)
	}
	httpRequestsTotal.WithLabelValues(r.Method, normalizePath(r.URL.Path), strconv.Itoa(status)).Inc()
}

func normalizePath(path string) string {
	const prefix = "/api/products/"
	if len(path) > len(prefix) {
		return "/api/products/{id}"
	}
	return path
}
