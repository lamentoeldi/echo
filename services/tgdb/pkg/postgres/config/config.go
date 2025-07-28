/*
Package config

This package contains functions to create pgx.ConnConfig and  pgxpool.Config from environment variables
*/
package config

import (
	"errors"
	"fmt"
	"github.com/ilyakaznacheev/cleanenv"
	"github.com/jackc/pgx/v5/pgxpool"
)

var (
	errInvalidMaxSize  = errors.New("pool max size must be >= 1")
	errInvalidMinSize  = errors.New("pool min size must be >= 1")
	errInvalidPoolSize = errors.New("min size must not exceed max size")
)

type Config struct {
	Host          string `env:"POSTGRES_HOST" env-default:"localhost"`
	Port          int    `env:"POSTGRES_PORT" env-default:"5432"`
	User          string `env:"POSTGRES_USER" env-default:"postgres"`
	Password      string `env:"POSTGRES_PASSWORD"`
	DBName        string `env:"POSTGRES_DB" env-default:"postgres"`
	MigrationsDir string `env:"POSTGRES_MIGRATIONS" env-default:"/migrations"`
	MinPoolSize   int32  `env:"MIN_POOL_SIZE" env-default:"5"`
	MaxPoolSize   int32  `env:"MAX_POOL_SIZE" env-default:"10"`

	*pgxpool.Config
}

func NewConfig() (*Config, error) {
	var cfg Config
	err := cleanenv.ReadEnv(&cfg)
	if err != nil {
		return nil, err
	}

	connStr := fmt.Sprintf(
		"postgres://%s:%s@%s:%d/%s",
		cfg.User,
		cfg.Password,
		cfg.Host,
		cfg.Port,
		cfg.DBName,
	)

	cfg.Config, err = pgxpool.ParseConfig(connStr)
	if err != nil {
		return nil, err
	}

	cfg.Config.MinConns = cfg.MinPoolSize
	cfg.Config.MaxConns = cfg.MaxPoolSize

	return &cfg, nil
}
