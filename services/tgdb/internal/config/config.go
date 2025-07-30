package config

import (
	"github.com/ilyakaznacheev/cleanenv"
	"time"
)

type Config struct {
	AppName     string        `env:"APP_NAME" env-default:"tgdb"`
	AppID       string        `env:"APP_ID" env-default:"tgdb"`
	StopTimeout time.Duration `env:"STOP_TIMEOUT" env-default:"10s"`
}

func New() (*Config, error) {
	var cfg Config
	err := cleanenv.ReadEnv(&cfg)
	if err != nil {
		return nil, err
	}

	return &cfg, nil
}
