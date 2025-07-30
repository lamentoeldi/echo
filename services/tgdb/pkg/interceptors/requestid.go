package interceptors

import (
	"context"
	"github.com/google/uuid"
	"google.golang.org/grpc"
)

const (
	requestIDkey = "request_id"
)

func ContextWithRequestID(parent context.Context, id uuid.UUID) context.Context {
	return context.WithValue(parent, requestIDkey, id)
}

func IDFromContext(ctx context.Context) uuid.UUID {
	return ctx.Value(requestIDkey).(uuid.UUID)
}

func UnaryRequestIDInjector() grpc.UnaryServerInterceptor {
	return func(
		ctx context.Context,
		req any,
		info *grpc.UnaryServerInfo,
		handler grpc.UnaryHandler,
	) (any, error) {
		id, _ := uuid.NewV7()
		ctx = ContextWithRequestID(ctx, id)
		return handler(ctx, req)
	}
}
