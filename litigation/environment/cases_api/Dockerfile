# Build stage
FROM golang:1.21-alpine AS builder
WORKDIR /app
COPY go.mod main.go ./
COPY internal ./internal
RUN CGO_ENABLED=0 go build -o /cases-api .

# Run stage
FROM alpine:3.19
RUN apk add --no-cache curl
WORKDIR /app
COPY --from=builder /cases-api .
EXPOSE 5000
CMD ["/app/cases-api"]
