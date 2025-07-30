package interceptors

import (
	"context"
	"go.opentelemetry.io/otel/attribute"
	"go.opentelemetry.io/otel/codes"
	"go.opentelemetry.io/otel/trace"
	"go.uber.org/zap"
	"google.golang.org/grpc"
)

const (
	appNameKey = "app_name"
	appIDKey   = "app_id"
)

func UnaryTracer(appName, appID string, log *zap.Logger) grpc.UnaryServerInterceptor {
	return func(
		ctx context.Context,
		req interface{},
		info *grpc.UnaryServerInfo,
		handler grpc.UnaryHandler,
	) (interface{}, error) {
		span := trace.SpanFromContext(ctx)
		if !span.SpanContext().IsValid() {
			log.Warn("invalid span context")
			return handler(ctx, req)
		}

		reqID := IDFromContext(ctx)
		span.SetAttributes(
			attribute.String(requestIDkey, reqID.String()),
			attribute.String(appNameKey, appName),
			attribute.String(appIDKey, appID),
		)

		res, err := handler(ctx, req)
		if err != nil {
			span.SetStatus(codes.Error, err.Error())
			span.RecordError(err)
		}

		return res, err
	}
}
