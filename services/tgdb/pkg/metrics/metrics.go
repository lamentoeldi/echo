package metrics

import (
	"context"
	"fmt"
	"github.com/ilyakaznacheev/cleanenv"
	"github.com/prometheus/client_golang/prometheus/promhttp"
	"go.uber.org/zap"
	"net/http"
	"time"
)

type Config struct {
	Host string `env:"METRICS_HOST" env-default:"0.0.0.0"`
	Port int    `env:"METRICS_PORT" env-default:"9090"`
}

func NewConfig() (*Config, error) {
	var cfg Config
	err := cleanenv.ReadEnv(&cfg)
	if err != nil {
		return nil, err
	}

	return &cfg, nil
}

type Metrics struct {
	cfg    *Config
	logger *zap.Logger
	server *http.Server
}

func NewMetrics(cfg *Config, log *zap.Logger) *Metrics {
	server := &http.Server{
		Addr: fmt.Sprintf("%s:%d", cfg.Host, cfg.Port),
	}

	return &Metrics{
		cfg:    cfg,
		logger: log,
		server: server,
	}
}

func (m *Metrics) Run() {
	go func() {
		m.server.Handler = promhttp.Handler()
		m.logger.Info(fmt.Sprintf("starting metrics server on %s:%d", m.cfg.Host, m.cfg.Port))
		err := m.server.ListenAndServe()
		if err != nil {
			m.logger.Error("failed to start metrics server", zap.Error(err))
		}
	}()
}

func (m *Metrics) Shutdown() {
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	_ = m.server.Shutdown(ctx)
}
