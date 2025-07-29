package main

import (
	"context"
	cm "github.com/echo/tgdb/internal/adapters/cache/metrics"
	"github.com/echo/tgdb/internal/adapters/cache/redis"
	transport "github.com/echo/tgdb/internal/adapters/controllers/grpc"
	rm "github.com/echo/tgdb/internal/adapters/repository/metrics"
	"github.com/echo/tgdb/internal/adapters/repository/postgres"
	"github.com/echo/tgdb/internal/adapters/usecases"
	"github.com/echo/tgdb/internal/ports"
	"github.com/echo/tgdb/pkg/interceptors"
	m "github.com/echo/tgdb/pkg/metrics"
	"github.com/echo/tgdb/pkg/postgres/pool"
	rdClient "github.com/echo/tgdb/pkg/redis"
	"go.uber.org/zap"
	"google.golang.org/grpc"
	"os/signal"
	"syscall"
)

func main() {
	ctx, cancel := signal.NotifyContext(context.Background(), syscall.SIGINT, syscall.SIGTERM)
	defer cancel()

	log, _ := zap.NewProduction()
	defer log.Sync()

	rd, err := rdClient.NewRedis(nil)
	if err != nil {
		log.Fatal("redis init failed", zap.Error(err))
	}

	pg, err := pool.New(ctx)
	if err != nil {
		log.Fatal("pg pool init failed", zap.Error(err))
	}

	cacheCfg, err := redis.NewConfig()

	var cache ports.UserCachePort
	cache = redis.NewUserCache(cacheCfg, rd)
	cache = cm.NewUserCacheWithMetrics(cache)

	var repo ports.UserRepoPort
	repo = postgres.NewUserRepo(pg)
	repo = rm.NewUserRepoWithMetrics(repo)

	app, err := usecases.New(repo, cache)
	if err != nil {
		log.Fatal("usecases init failed", zap.Error(err))
	}

	done := make(chan struct{})
	go func() {
		<-done
		cancel()
	}()

	s := grpc.NewServer(
		grpc.ChainUnaryInterceptor(
			interceptors.UnaryRequestIDInjector(),
			interceptors.UnaryLoggerInjector(log),
			interceptors.UnaryRequestsCounter(),
			interceptors.UnaryPanicHandler(done),
			interceptors.UnaryErrorHandler(),
			interceptors.UnaryLatencyCounter(),
		),
	)

	metricsCfg, err := m.NewConfig()
	if err != nil {
		log.Fatal("metrics config init failed", zap.Error(err))
	}
	metrics := m.NewMetrics(metricsCfg, log)

	controllerCfg, err := transport.NewConfig()
	if err != nil {
		log.Fatal("transport init failed", zap.Error(err))
	}
	controller, err := transport.New(controllerCfg, s, log, app)
	if err != nil {
		log.Fatal("transport init failed", zap.Error(err))
	}

	controller.Run()
	metrics.Run()
	<-ctx.Done()
	controller.Shutdown()
	metrics.Shutdown()
}
