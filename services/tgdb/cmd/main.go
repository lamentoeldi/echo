package main

import (
	"context"
	"github.com/echo/tgdb/internal/adapters/cache/redis"
	transport "github.com/echo/tgdb/internal/adapters/controllers/grpc"
	"github.com/echo/tgdb/internal/adapters/repository/postgres"
	"github.com/echo/tgdb/internal/adapters/usecases"
	"github.com/echo/tgdb/pkg/interceptors"
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
	cache := redis.NewUserCache(cacheCfg, rd)

	repo, err := postgres.NewUserRepo(pg)
	if err != nil {
		log.Fatal("repo init failed", zap.Error(err))
	}

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
			interceptors.UnaryPanicHandler(done),
			interceptors.UnaryErrorHandler(),
		),
	)

	controllerCfg, err := transport.NewConfig()
	if err != nil {
		log.Fatal("transport init failed", zap.Error(err))
	}
	controller, err := transport.New(controllerCfg, s, log, app)
	if err != nil {
		log.Fatal("transport init failed", zap.Error(err))
	}

	controller.Run()
	<-ctx.Done()
}
