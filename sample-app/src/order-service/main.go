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
	"strings"
	"syscall"
	"time"

	_ "github.com/lib/pq"
	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promhttp"
	"go.opentelemetry.io/contrib/instrumentation/net/http/otelhttp"
	"go.opentelemetry.io/otel"
	"go.opentelemetry.io/otel/exporters/otlp/otlptrace/otlptracegrpc"
	"go.opentelemetry.io/otel/sdk/resource"
	sdktrace "go.opentelemetry.io/otel/sdk/trace"
	semconv "go.opentelemetry.io/otel/semconv/v1.24.0"
	"go.opentelemetry.io/otel/trace"
)

// Order represents an order in the system.
type Order struct {
	ID        int     `json:"id"`
	ProductID int     `json:"product_id"`
	Quantity  int     `json:"quantity"`
	Total     float64 `json:"total"`
	Status    string  `json:"status"`
}

// ProductResponse represents the response from product-service.
type ProductResponse struct {
	ID    int     `json:"id"`
	Name  string  `json:"name"`
	Price float64 `json:"price"`
}

var (
	db     *sql.DB
	logger *slog.Logger
	tracer trace.Tracer

	productServiceURL string

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
	logger = slog.New(slog.NewJSONHandler(os.Stdout, &slog.HandlerOptions{Level: slog.LevelInfo}))
	slog.SetDefault(logger)

	productServiceURL = getEnv("PRODUCT_SERVICE_URL", "http://product-service:8081")

	// Initialize OpenTelemetry
	tp, err := initTracer()
	if err != nil {
		logger.Error("failed to initialize tracer", "error", err)
		os.Exit(1)
	}
	defer func() {
		ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
		defer cancel()
		if err := tp.Shutdown(ctx); err != nil {
			logger.Error("failed to shutdown tracer provider", "error", err)
		}
	}()

	tracer = otel.Tracer("order-service")

	// Connect to PostgreSQL
	if err := connectDB(); err != nil {
		logger.Error("failed to connect to database", "error", err)
		os.Exit(1)
	}
	defer db.Close()

	// Auto-create orders table
	if err := createTable(); err != nil {
		logger.Error("failed to create orders table", "error", err)
		os.Exit(1)
	}

	// Set up HTTP routes
	mux := http.NewServeMux()
	mux.HandleFunc("/api/orders/", ordersHandler)
	mux.HandleFunc("/health", healthHandler)
	mux.Handle("/metrics", promhttp.Handler())

	// Wrap with OpenTelemetry HTTP instrumentation
	handler := otelhttp.NewHandler(mux, "order-service")

	srv := &http.Server{
		Addr:    ":8082",
		Handler: handler,
	}

	// Graceful shutdown
	done := make(chan os.Signal, 1)
	signal.Notify(done, os.Interrupt, syscall.SIGTERM)

	go func() {
		logger.Info("starting order-service", "port", 8082)
		if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			logger.Error("server failed", "error", err)
			os.Exit(1)
		}
	}()

	<-done
	logger.Info("shutting down server")

	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()

	if err := srv.Shutdown(ctx); err != nil {
		logger.Error("server shutdown failed", "error", err)
	}
	logger.Info("server stopped")
}

func initTracer() (*sdktrace.TracerProvider, error) {
	endpoint := getEnv("OTEL_EXPORTER_OTLP_ENDPOINT", "otel-collector.book-observability:4317")

	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	exporter, err := otlptracegrpc.New(ctx,
		otlptracegrpc.WithEndpoint(endpoint),
		otlptracegrpc.WithInsecure(),
	)
	if err != nil {
		return nil, fmt.Errorf("failed to create OTLP exporter: %w", err)
	}

	res, err := resource.New(ctx,
		resource.WithAttributes(
			semconv.ServiceNameKey.String("order-service"),
			semconv.ServiceVersionKey.String("1.0.0"),
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

	return tp, nil
}

func connectDB() error {
	host := getEnv("DATABASE_HOST", "localhost")
	port := getEnv("DATABASE_PORT", "5432")
	dbname := getEnv("DATABASE_NAME", "orders")
	user := getEnv("DATABASE_USER", "postgres")
	password := getEnv("DATABASE_PASSWORD", "postgres")

	dsn := fmt.Sprintf("host=%s port=%s user=%s password=%s dbname=%s sslmode=disable",
		host, port, user, password, dbname)

	var err error
	db, err = sql.Open("postgres", dsn)
	if err != nil {
		return fmt.Errorf("failed to open database: %w", err)
	}

	db.SetMaxOpenConns(25)
	db.SetMaxIdleConns(5)
	db.SetConnMaxLifetime(5 * time.Minute)

	if err := db.Ping(); err != nil {
		return fmt.Errorf("failed to ping database: %w", err)
	}

	logger.Info("connected to database", "host", host, "port", port, "database", dbname)
	return nil
}

func createTable() error {
	query := `
	CREATE TABLE IF NOT EXISTS orders (
		id SERIAL PRIMARY KEY,
		product_id INTEGER NOT NULL,
		quantity INTEGER NOT NULL,
		total NUMERIC(10,2) NOT NULL,
		status VARCHAR(50) NOT NULL DEFAULT 'pending'
	)`
	_, err := db.Exec(query)
	if err != nil {
		return fmt.Errorf("failed to create table: %w", err)
	}
	logger.Info("orders table ready")
	return nil
}

func ordersHandler(w http.ResponseWriter, r *http.Request) {
	start := time.Now()
	requestID := r.Header.Get("X-Request-ID")
	if requestID != "" {
		w.Header().Set("X-Request-ID", requestID)
	}

	// Route: /api/orders/ or /api/orders/{id}
	path := strings.TrimPrefix(r.URL.Path, "/api/orders/")
	path = strings.TrimSuffix(path, "/")

	var status int
	var metricPath string

	if path == "" {
		// /api/orders/
		metricPath = "/api/orders/"
		switch r.Method {
		case http.MethodGet:
			status = listOrders(w, r)
		case http.MethodPost:
			status = createOrder(w, r)
		default:
			status = http.StatusMethodNotAllowed
			writeError(w, status, "method not allowed")
		}
	} else {
		// /api/orders/{id}
		metricPath = "/api/orders/{id}"
		if r.Method != http.MethodGet {
			status = http.StatusMethodNotAllowed
			writeError(w, status, "method not allowed")
		} else {
			id, err := strconv.Atoi(path)
			if err != nil {
				status = http.StatusBadRequest
				writeError(w, status, "invalid order id")
			} else {
				status = getOrder(w, r, id)
			}
		}
	}

	duration := time.Since(start).Seconds()
	httpRequestsTotal.WithLabelValues(r.Method, metricPath, strconv.Itoa(status)).Inc()
	httpRequestDuration.WithLabelValues(r.Method, metricPath).Observe(duration)

	logger.Info("request completed",
		"method", r.Method,
		"path", r.URL.Path,
		"status", status,
		"duration_ms", time.Since(start).Milliseconds(),
		"request_id", requestID,
	)
}

func listOrders(w http.ResponseWriter, r *http.Request) int {
	ctx := r.Context()
	ctx, span := tracer.Start(ctx, "db.query.list_orders")
	defer span.End()

	rows, err := db.QueryContext(ctx, "SELECT id, product_id, quantity, total, status FROM orders ORDER BY id")
	if err != nil {
		logger.Error("failed to query orders", "error", err)
		writeError(w, http.StatusInternalServerError, "failed to query orders")
		return http.StatusInternalServerError
	}
	defer rows.Close()

	orders := make([]Order, 0)
	for rows.Next() {
		var o Order
		if err := rows.Scan(&o.ID, &o.ProductID, &o.Quantity, &o.Total, &o.Status); err != nil {
			logger.Error("failed to scan order", "error", err)
			writeError(w, http.StatusInternalServerError, "failed to read order")
			return http.StatusInternalServerError
		}
		orders = append(orders, o)
	}
	if err := rows.Err(); err != nil {
		logger.Error("rows iteration error", "error", err)
		writeError(w, http.StatusInternalServerError, "failed to read orders")
		return http.StatusInternalServerError
	}

	writeJSON(w, http.StatusOK, orders)
	return http.StatusOK
}

func createOrder(w http.ResponseWriter, r *http.Request) int {
	ctx := r.Context()

	var req struct {
		ProductID int `json:"product_id"`
		Quantity  int `json:"quantity"`
	}
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		writeError(w, http.StatusBadRequest, "invalid request body")
		return http.StatusBadRequest
	}
	if req.ProductID <= 0 || req.Quantity <= 0 {
		writeError(w, http.StatusBadRequest, "product_id and quantity must be positive")
		return http.StatusBadRequest
	}

	// Fetch product price from product-service
	product, err := fetchProduct(ctx, req.ProductID)
	if err != nil {
		logger.Error("failed to fetch product", "product_id", req.ProductID, "error", err)
		writeError(w, http.StatusBadGateway, "failed to fetch product information")
		return http.StatusBadGateway
	}

	total := product.Price * float64(req.Quantity)

	// Insert order into database
	ctx, span := tracer.Start(ctx, "db.insert.order")
	defer span.End()

	var order Order
	err = db.QueryRowContext(ctx,
		"INSERT INTO orders (product_id, quantity, total, status) VALUES ($1, $2, $3, $4) RETURNING id, product_id, quantity, total, status",
		req.ProductID, req.Quantity, total, "pending",
	).Scan(&order.ID, &order.ProductID, &order.Quantity, &order.Total, &order.Status)
	if err != nil {
		logger.Error("failed to insert order", "error", err)
		writeError(w, http.StatusInternalServerError, "failed to create order")
		return http.StatusInternalServerError
	}

	logger.Info("order created", "order_id", order.ID, "product_id", order.ProductID, "total", order.Total)
	writeJSON(w, http.StatusCreated, order)
	return http.StatusCreated
}

func getOrder(w http.ResponseWriter, r *http.Request, id int) int {
	ctx := r.Context()
	ctx, span := tracer.Start(ctx, "db.query.get_order")
	defer span.End()

	var order Order
	err := db.QueryRowContext(ctx,
		"SELECT id, product_id, quantity, total, status FROM orders WHERE id = $1", id,
	).Scan(&order.ID, &order.ProductID, &order.Quantity, &order.Total, &order.Status)
	if err == sql.ErrNoRows {
		writeError(w, http.StatusNotFound, "order not found")
		return http.StatusNotFound
	}
	if err != nil {
		logger.Error("failed to query order", "error", err)
		writeError(w, http.StatusInternalServerError, "failed to query order")
		return http.StatusInternalServerError
	}

	writeJSON(w, http.StatusOK, order)
	return http.StatusOK
}

func fetchProduct(ctx context.Context, productID int) (*ProductResponse, error) {
	ctx, span := tracer.Start(ctx, "http.client.get_product")
	defer span.End()

	url := fmt.Sprintf("%s/api/products/%d", productServiceURL, productID)

	// Use OTel-instrumented HTTP client for context propagation
	client := &http.Client{
		Timeout:   10 * time.Second,
		Transport: otelhttp.NewTransport(http.DefaultTransport),
	}

	req, err := http.NewRequestWithContext(ctx, http.MethodGet, url, nil)
	if err != nil {
		return nil, fmt.Errorf("failed to create request: %w", err)
	}

	resp, err := client.Do(req)
	if err != nil {
		return nil, fmt.Errorf("failed to call product-service: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("product-service returned status %d", resp.StatusCode)
	}

	var product ProductResponse
	if err := json.NewDecoder(resp.Body).Decode(&product); err != nil {
		return nil, fmt.Errorf("failed to decode product response: %w", err)
	}

	return &product, nil
}

func healthHandler(w http.ResponseWriter, r *http.Request) {
	start := time.Now()
	requestID := r.Header.Get("X-Request-ID")
	if requestID != "" {
		w.Header().Set("X-Request-ID", requestID)
	}

	status := "healthy"
	code := http.StatusOK

	if err := db.Ping(); err != nil {
		status = "unhealthy"
		code = http.StatusServiceUnavailable
		logger.Error("health check failed", "error", err)
	}

	writeJSON(w, code, map[string]string{
		"status":  status,
		"service": "order-service",
	})

	httpRequestsTotal.WithLabelValues(r.Method, "/health", strconv.Itoa(code)).Inc()
	httpRequestDuration.WithLabelValues(r.Method, "/health").Observe(time.Since(start).Seconds())
}

func writeJSON(w http.ResponseWriter, status int, data interface{}) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	json.NewEncoder(w).Encode(data)
}

func writeError(w http.ResponseWriter, status int, message string) {
	writeJSON(w, status, map[string]string{"error": message})
}

func getEnv(key, defaultValue string) string {
	if v := os.Getenv(key); v != "" {
		return v
	}
	return defaultValue
}
