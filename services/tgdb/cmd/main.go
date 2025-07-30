package main

import (
	"context"
	cm "github.com/echo/tgdb/internal/adapters/cache/metrics"
	"github.com/echo/tgdb/internal/adapters/cache/redis"
	transport "github.com/echo/tgdb/internal/adapters/controllers/grpc"
	rm "github.com/echo/tgdb/internal/adapters/repository/metrics"
	"github.com/echo/tgdb/internal/adapters/repository/postgres"
	"github.com/echo/tgdb/internal/adapters/usecases"
	"github.com/echo/tgdb/internal/config"
	"github.com/echo/tgdb/internal/ports"
	"github.com/echo/tgdb/pkg/interceptors"
	"github.com/echo/tgdb/pkg/log"
	m "github.com/echo/tgdb/pkg/metrics"
	"github.com/echo/tgdb/pkg/otlp"
	"github.com/echo/tgdb/pkg/postgres/pool"
	rdClient "github.com/echo/tgdb/pkg/redis"
	"go.opentelemetry.io/contrib/instrumentation/google.golang.org/grpc/otelgrpc"
	"go.uber.org/zap"
	"google.golang.org/grpc"
	"os/signal"
	"syscall"
)

func main() {
	ctx, cancel := signal.NotifyContext(context.Background(), syscall.SIGINT, syscall.SIGTERM)
	defer cancel()

	logger, _ := log.SetupLogger()
	logger = logger.Named("main")
	defer logger.Sync()

	rd, err := rdClient.NewRedis(nil)
	if err != nil {
		logger.Fatal("redis init failed", zap.Error(err))
	}

	pg, err := pool.New(ctx)
	if err != nil {
		logger.Fatal("pg pool init failed", zap.Error(err))
	}

	cacheCfg, err := redis.NewConfig()

	var cache ports.UserCachePort
	cache = redis.NewUserCache(ctx, cacheCfg, rd, logger.Named("cache-cron"))
	cache = cm.NewUserCacheWithMetrics(cache)

	var repo ports.UserRepoPort
	repo = postgres.NewUserRepo(pg)
	repo = rm.NewUserRepoWithMetrics(repo)

	app, err := usecases.New(repo, cache)
	if err != nil {
		logger.Fatal("usecases init failed", zap.Error(err))
	}

	done := make(chan struct{})
	go func() {
		<-done
		cancel()
	}()

	cfg, err := config.New()
	if err != nil {
		logger.Fatal("config init failed", zap.Error(err))
	}

	tracerStop, err := otlp.InitHttp(ctx, nil)
	if err != nil {
		logger.Fatal("otlp init failed", zap.Error(err))
	}

	s := grpc.NewServer(
		grpc.StatsHandler(otelgrpc.NewServerHandler()),
		grpc.ChainUnaryInterceptor(
			interceptors.UnaryRequestIDInjector(),
			interceptors.UnaryLoggerInjector(logger),
			interceptors.UnaryRequestsCounter(),
			interceptors.UnaryPanicHandler(done),
			interceptors.UnaryErrorHandler(),
			interceptors.UnaryTracer(cfg.AppName, cfg.AppID, logger),
			interceptors.UnaryLatencyCounter(),
		),
	)

	metricsCfg, err := m.NewConfig()
	if err != nil {
		logger.Fatal("metrics config init failed", zap.Error(err))
	}
	metrics := m.NewMetrics(metricsCfg, logger.Named("metrics"))

	controllerCfg, err := transport.NewConfig()
	if err != nil {
		logger.Fatal("transport init failed", zap.Error(err))
	}
	controller, err := transport.New(controllerCfg, s, logger.Named("grpc"), app)
	if err != nil {
		logger.Fatal("transport init failed", zap.Error(err))
	}

	controller.Run()
	metrics.Run()

	<-ctx.Done()

	stopCtx, cancel := context.WithTimeout(context.Background(), cfg.StopTimeout)
	defer cancel()

	controller.Shutdown()
	metrics.Shutdown()
	_ = tracerStop(stopCtx)
}
