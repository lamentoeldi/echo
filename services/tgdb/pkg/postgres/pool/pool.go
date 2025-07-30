/*
Package pool

This package contains common functions to work with pgxpool.Pool
*/
package pool

import (
	"context"
	"errors"
	"fmt"
	"github.com/echo/tgdb/pkg/postgres/config"
	"github.com/golang-migrate/migrate/v4"
	"github.com/golang-migrate/migrate/v4/database/pgx/v5"
	_ "github.com/golang-migrate/migrate/v4/source/file"
	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/jackc/pgx/v5/stdlib"
)

// New creates pgxpool.Pool and runs migrations if location provided
func New(ctx context.Context) (*pgxpool.Pool, error) {
	cfg, err := config.NewConfig()
	if err != nil {
		return nil, err
	}

	pool, err := pgxpool.NewWithConfig(ctx, cfg.Config)
	if err != nil {
		return nil, err
	}

	if cfg.MigrationsDir != "" {
		err := runMigrations(pool, cfg.MigrationsDir, cfg.DBName)
		if err != nil {
			return nil, err
		}
	}

	return pool, nil
}

func runMigrations(pool *pgxpool.Pool, migrationsDir, dbName string) error {
	db := stdlib.OpenDBFromPool(pool)
	driver, err := pgx.WithInstance(db, &pgx.Config{})
	if err != nil {
		return err
	}
	m, err := migrate.NewWithDatabaseInstance(
		fmt.Sprintf("file://%s", migrationsDir),
		dbName,
		driver,
	)
	if err != nil {
		return err
	}

	err = m.Up()
	if err != nil && !errors.Is(err, migrate.ErrNoChange) {
		return err
	}

	return nil
}
