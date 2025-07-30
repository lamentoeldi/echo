package interceptors

import (
	"context"
	"github.com/echo/tgdb/pkg/log"
	"go.uber.org/zap"
	"google.golang.org/grpc"
)

func UnaryLoggerInjector(baseLogger *zap.Logger) grpc.UnaryServerInterceptor {
	return func(
		ctx context.Context,
		req any,
		info *grpc.UnaryServerInfo,
		handler grpc.UnaryHandler,
	) (any, error) {
		reqID := IDFromContext(ctx)
		logger := baseLogger.
			With(zap.String(requestIDkey, reqID.String()))

		ctx = log.ContextWithLogger(ctx, logger)

		logger.Debug("received request")
		return handler(ctx, req)
	}
}
