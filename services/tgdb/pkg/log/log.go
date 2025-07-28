package log

import (
	"context"
	"go.uber.org/zap"
)

const (
	loggerKey = "logger"
)

func ContextWithLogger(parent context.Context, logger *zap.Logger) context.Context {
	return context.WithValue(parent, loggerKey, logger)
}

func FromContext(ctx context.Context) *zap.Logger {
	logger := ctx.Value(loggerKey).(*zap.Logger)
	return logger
}
