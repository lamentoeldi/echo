# Stage 1: Build
FROM golang:1.24.3-alpine3.21 AS build

WORKDIR /app

COPY go.mod .
COPY go.sum .

RUN go mod download && go mod verify

COPY . .

RUN CGO_ENABLED=0 GOOS=linux go build -o app ./cmd/main.go

# Stage 2: Image
FROM alpine:3.21

WORKDIR /app

COPY db/migrations/tg /migrations
COPY --from=build /app/app /app/app

ENTRYPOINT ["/app/app"]