package interceptors

import (
	"context"
	"github.com/prometheus/client_golang/prometheus"
	"google.golang.org/grpc"
	"time"
)

var (
	latencyCounter = prometheus.NewHistogram(prometheus.HistogramOpts{
		Name:    "tgdb_request_latency",
		Help:    "TGDB request latency",
		Buckets: prometheus.DefBuckets,
	})
)

func init() {
	prometheus.MustRegister(latencyCounter)
}

func UnaryLatencyCounter() grpc.UnaryServerInterceptor {
	return func(
		ctx context.Context,
		req any,
		info *grpc.UnaryServerInfo,
		handler grpc.UnaryHandler,
	) (any, error) {
		start := time.Now()
		res, err := handler(ctx, req)
		end := time.Now().Sub(start)

		latencyCounter.Observe(end.Seconds())

		return res, err
	}
}
