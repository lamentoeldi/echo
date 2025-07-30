package interceptors

import (
	"context"
	"github.com/echo/tgdb/pkg/log"
	"go.uber.org/zap"
	"google.golang.org/grpc"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/status"
)

func UnaryPanicHandler(done chan<- struct{}) grpc.UnaryServerInterceptor {
	return func(
		ctx context.Context,
		req any,
		info *grpc.UnaryServerInfo,
		handler grpc.UnaryHandler,
	) (_ any, outErr error) {
		defer func() {
			r := recover()
			if err, ok := r.(error); ok {
				log.
					FromContext(ctx).
					Error("panic occurred",
						zap.Error(err),
						zap.String("method", info.FullMethod),
						zap.Stack("stacktrace"),
					)
				outErr = status.Error(codes.Internal, "internal error")
				done <- struct{}{}
			}
		}()

		return handler(ctx, req)
	}
}
