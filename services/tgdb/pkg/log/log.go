package log

import (
	"context"
	"fmt"
	"github.com/ilyakaznacheev/cleanenv"
	"go.uber.org/zap"
	"go.uber.org/zap/zapcore"
)

const (
	loggerKey = "logger"
)

func ContextWithLogger(parent context.Context, logger *zap.Logger) context.Context {
	return context.WithValue(parent, loggerKey, logger)
}

func FromContext(ctx context.Context) *zap.Logger {
	logger := ctx.Value(loggerKey).(*zap.Logger)
	return logger
}

type LoggerConfig struct {
	Level     string `env:"LOG_LEVEL" envDefault:"info"`
	LogFormat string `env:"LOG_FORMAT" envDefault:"json"`
}

func NewConfig() (*LoggerConfig, error) {
	var cfg LoggerConfig
	err := cleanenv.ReadEnv(&cfg)
	if err != nil {
		return nil, err
	}

	return &cfg, nil
}

func SetupLogger() (*zap.Logger, error) {
	cfg, err := NewConfig()
	if err != nil {
		return nil, fmt.Errorf("failed to setup logger: %w", err)
	}

	level := getLogLevel(cfg.Level)
	baseCfg := getBaseConfig(cfg.LogFormat)
	baseCfg.
		Level.
		SetLevel(level)

	return baseCfg.Build()
}

func getBaseConfig(format string) zap.Config {
	switch format {
	case "text":
		return zap.NewDevelopmentConfig()
	case "json":
		return zap.NewProductionConfig()
	}

	return zap.NewProductionConfig()
}

func getLogLevel(level string) zapcore.Level {
	switch level {
	case "debug":
		return zap.DebugLevel
	case "info":
		return zap.InfoLevel
	case "warn":
		return zap.WarnLevel
	case "error":
		return zap.ErrorLevel
	case "fatal":
		return zap.FatalLevel
	}

	return zap.InfoLevel
}
