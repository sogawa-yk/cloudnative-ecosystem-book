FROM golang:1.22-alpine AS builder
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 go build -o /api-gateway .

FROM gcr.io/distroless/static:nonroot
COPY --from=builder /api-gateway /api-gateway
USER nonroot:nonroot
EXPOSE 8080
ENTRYPOINT ["/api-gateway"]
