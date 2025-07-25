package pool

import (
	"context"
	"os"
	"testing"
	"time"
)

func init() {
	_ = os.Setenv("DB_HOST", "localhost")
	_ = os.Setenv("DB_PORT", "5432")
	_ = os.Setenv("DB_NAME", "postgres")
	_ = os.Setenv("DB_USER", "postgres")
	_ = os.Setenv("DB_PASSWORD", "test")
	_ = os.Setenv("SSL_MODE", "disable")

	_ = os.Setenv("MIN_SIZE", "1")
	_ = os.Setenv("MAX_SIZE", "1")
}

func TestNew(t *testing.T) {
	testTime := 10 * time.Second

	ctx, cancel := context.WithTimeout(context.Background(), testTime)
	defer cancel()

	pool, err := New(ctx)
	if err != nil {
		t.Fatal(err)
	}
	defer pool.Close()

	err = pool.Ping(ctx)
	if err != nil {
		t.Fatal(err)
	}
}

func TestNewWithMigrations(t *testing.T) {
	testTime := 10 * time.Second

	ctx, cancel := context.WithTimeout(context.Background(), testTime)
	defer cancel()

	pool, err := New(ctx)
	if err != nil {
		t.Fatal(err)
	}
	defer pool.Close()

	err = pool.Ping(ctx)
	if err != nil {
		t.Fatal(err)
	}
}
