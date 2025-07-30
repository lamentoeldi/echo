package redis

import (
	"context"
	"github.com/redis/go-redis/v9"
	"go.uber.org/zap"
	"sync"
	"time"
)

type bulkDel struct {
	cfg   *Config
	log   *zap.Logger
	redis redis.UniversalClient

	queue []string
	mu    sync.Mutex
}

func newBulkDel(cfg *Config, log *zap.Logger, redis redis.UniversalClient) *bulkDel {
	bulk := &bulkDel{
		cfg:   cfg,
		log:   log,
		redis: redis,
		queue: make([]string, 0, cfg.BulkMaxSize),
	}

	return bulk
}

func (bd *bulkDel) startCron(ctx context.Context) {
	go func() {
		ticker := time.NewTicker(bd.cfg.BulkBackoff)
		defer ticker.Stop()

		for {
			select {
			case <-ticker.C:
				err := bd.Flush(ctx)
				if err != nil {
					bd.log.Error("failed to flush cache", zap.Error(err))
				}
			case <-ctx.Done():
				return
			}
		}
	}()
}

func (bd *bulkDel) Flush(ctx context.Context) error {
	if len(bd.queue) < 1 {
		return nil
	}

	bd.mu.Lock()
	defer bd.mu.Unlock()

	err := bd.redis.Del(ctx, bd.queue...).Err()
	if err != nil {
		return err
	}

	bd.queue = make([]string, 0, bd.cfg.BulkMaxSize)
	return nil
}

func (bd *bulkDel) Del(ctx context.Context, keys ...string) (err error) {
	if len(keys)+len(bd.queue) >= bd.cfg.BulkMaxSize {
		err = bd.Flush(ctx)
	}

	bd.mu.Lock()
	defer bd.mu.Unlock()

	bd.queue = append(bd.queue, keys...)
	return
}
