FROM golang:1.22-alpine AS builder
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 go build -o /product-service .

FROM gcr.io/distroless/static:nonroot
COPY --from=builder /product-service /product-service
USER nonroot:nonroot
EXPOSE 8081
ENTRYPOINT ["/product-service"]
