package interceptors

import (
	"context"
	"github.com/prometheus/client_golang/prometheus"
	"google.golang.org/grpc"
)

var (
	totalRequestsCounter = prometheus.NewCounter(prometheus.CounterOpts{
		Name: "tgdb_total_requests",
		Help: "TGDB total requests",
	})
	inflightRequestsCounter = prometheus.NewGauge(prometheus.GaugeOpts{
		Name: "tgdb_inflight_requests",
		Help: "TGDB inflight requests",
	})
)

func init() {
	prometheus.MustRegister(totalRequestsCounter)
}

func UnaryRequestsCounter() grpc.UnaryServerInterceptor {
	return func(
		ctx context.Context,
		req any,
		info *grpc.UnaryServerInfo,
		handler grpc.UnaryHandler,
	) (any, error) {
		totalRequestsCounter.Inc()

		inflightRequestsCounter.Inc()
		res, err := handler(ctx, req)
		defer inflightRequestsCounter.Dec()

		return res, err
	}
}
