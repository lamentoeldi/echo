package interceptors

import (
	"context"
	"errors"
	e "github.com/echo/tgdb/pkg/errors"
	"github.com/echo/tgdb/pkg/log"
	"github.com/prometheus/client_golang/prometheus"
	"go.uber.org/zap"
	"google.golang.org/grpc"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/status"
)

var (
	errorsCounter = prometheus.NewCounter(prometheus.CounterOpts{
		Name: "tgdb_total_errors",
		Help: "TGDB total errors",
	})
)

func init() {
	prometheus.MustRegister(errorsCounter)
}

func UnaryErrorHandler() grpc.UnaryServerInterceptor {
	return func(
		ctx context.Context,
		req any,
		info *grpc.UnaryServerInfo,
		handler grpc.UnaryHandler,
	) (any, error) {
		res, err := handler(ctx, req)
		if err == nil {
			return res, nil
		}
		errorsCounter.Inc()
		log.
			FromContext(ctx).
			Error("error handling request",
				zap.Error(err),
				zap.String("method", info.FullMethod),
			)

		var appErr *e.Error
		if errors.As(err, &appErr) {
			return nil, status.Errorf(appErr.GRPCCode(), appErr.PublicMessage())
		}

		return nil, status.Error(codes.Internal, "internal server error")
	}
}
