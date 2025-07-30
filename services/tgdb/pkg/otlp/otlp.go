package otlp

import (
	"context"
	"crypto/tls"
	"fmt"
	"github.com/ilyakaznacheev/cleanenv"
	"go.opentelemetry.io/otel"
	"go.opentelemetry.io/otel/exporters/otlp/otlptrace/otlptracehttp"
	"go.opentelemetry.io/otel/sdk/resource"
	sdktrace "go.opentelemetry.io/otel/sdk/trace"
	semconv "go.opentelemetry.io/otel/semconv/v1.21.0"
)

type Config struct {
	Endpoint    string `env:"TRACER_ENDPOINT"`
	ServiceName string `env:"TRACER_APP_NAME" env-default:"tgdb"`
}

func NewConfig() (*Config, error) {
	var cfg Config
	err := cleanenv.ReadEnv(&cfg)
	if err != nil {
		return nil, err
	}

	return &cfg, nil
}

func InitHttp(ctx context.Context, tlsConfig *tls.Config) (func(ctx context.Context) error, error) {
	cfg, err := NewConfig()
	if err != nil {
		return nil, fmt.Errorf("failed to init otlp tracer: %w", err)
	}

	opts := []otlptracehttp.Option{
		otlptracehttp.WithEndpoint(cfg.Endpoint),
	}

	if tlsConfig != nil {
		opts = append(opts, otlptracehttp.WithTLSClientConfig(tlsConfig))
	} else {
		opts = append(opts, otlptracehttp.WithInsecure())
	}

	exp, err := otlptracehttp.New(ctx, opts...)
	if err != nil {
		return nil, fmt.Errorf("failed to create OTLP HTTP exporter: %w", err)
	}

	tp := sdktrace.NewTracerProvider(
		sdktrace.WithBatcher(exp),
		sdktrace.WithResource(resource.NewWithAttributes(
			semconv.SchemaURL,
			semconv.ServiceName(cfg.ServiceName),
		)),
	)

	otel.SetTracerProvider(tp)

	return tp.Shutdown, nil
}
