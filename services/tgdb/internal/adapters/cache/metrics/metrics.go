package metrics

import (
	"context"
	"errors"
	"github.com/echo/tgdb/internal/domain/models"
	"github.com/echo/tgdb/internal/ports"
	e "github.com/echo/tgdb/pkg/errors"
	"github.com/google/uuid"
	"github.com/prometheus/client_golang/prometheus"
	"time"
)

var (
	totalCacheCallsCounter = prometheus.NewCounter(prometheus.CounterOpts{
		Name: "tgdb_cache_total_calls",
		Help: "Number of calls made to tgdb cache",
	})
	totalCacheHitsCounter = prometheus.NewCounter(prometheus.CounterOpts{
		Name: "tgdb_cache_total_hits",
		Help: "Total number of cache hits",
	})
	totalCacheMissesCounter = prometheus.NewCounter(prometheus.CounterOpts{
		Name: "tgdb_cache_total_cache_misses",
		Help: "Total number of cache misses",
	})
	totalCacheEvictionsCounter = prometheus.NewCounter(prometheus.CounterOpts{
		Name: "tgdb_cache_total_cache_evictions",
		Help: "Total number of cache evictions",
	})
	totalCacheErrorsCounter = prometheus.NewCounter(prometheus.CounterOpts{
		Name: "tgdb_cache_total_cache_errors",
		Help: "Total number of cache errors",
	})
	cacheLatencyCounter = prometheus.NewHistogram(prometheus.HistogramOpts{
		Name:    "tgdb_cache_latency",
		Help:    "Latency of cache calls",
		Buckets: prometheus.DefBuckets,
	})
)

func init() {
	prometheus.MustRegister(totalCacheCallsCounter)
	prometheus.MustRegister(totalCacheHitsCounter)
	prometheus.MustRegister(totalCacheMissesCounter)
	prometheus.MustRegister(totalCacheEvictionsCounter)
	prometheus.MustRegister(totalCacheErrorsCounter)
	prometheus.MustRegister(cacheLatencyCounter)
}

func withCacheCounters[T, E any](
	f func(context.Context, T) (E, error),
	ctx context.Context,
	arg T,
) (E, error) {
	totalCacheCallsCounter.Inc()

	start := time.Now()
	res, err := f(ctx, arg)
	end := time.Now().Sub(start)

	defer cacheLatencyCounter.Observe(end.Seconds())

	if errors.Is(err, e.ErrCacheMiss) {
		totalCacheMissesCounter.Inc()
		return res, err
	}
	if err != nil {
		totalCacheErrorsCounter.Inc()
		return res, err
	}

	totalCacheHitsCounter.Inc()
	return res, nil
}

func withEvictionCounters[T any](
	f func(context.Context, T) error,
	ctx context.Context,
	arg T,
) error {
	totalCacheCallsCounter.Inc()
	totalCacheEvictionsCounter.Inc()

	start := time.Now()
	err := f(ctx, arg)
	end := time.Now().Sub(start)

	if err != nil {
		totalCacheErrorsCounter.Inc()
	}

	defer cacheLatencyCounter.Observe(end.Seconds())

	return err
}

type UserCacheWithMetrics struct {
	cache ports.UserCachePort
}

func NewUserCacheWithMetrics(cache ports.UserCachePort) *UserCacheWithMetrics {
	return &UserCacheWithMetrics{cache: cache}
}

func (uc *UserCacheWithMetrics) GetByID(ctx context.Context, id uuid.UUID) (*models.User, error) {
	return withCacheCounters(uc.cache.GetByID, ctx, id)
}

func (uc *UserCacheWithMetrics) GetByTgID(ctx context.Context, id int64) (*models.User, error) {
	return withCacheCounters(uc.cache.GetByTgID, ctx, id)
}

func (uc *UserCacheWithMetrics) GetID(ctx context.Context, id int64) (uuid.UUID, error) {
	return withCacheCounters(uc.cache.GetID, ctx, id)
}

func (uc *UserCacheWithMetrics) GetTgID(ctx context.Context, id uuid.UUID) (int64, error) {
	return withCacheCounters(uc.cache.GetTgID, ctx, id)
}

func (uc *UserCacheWithMetrics) AddByID(ctx context.Context, user *models.User) error {
	totalCacheCallsCounter.Inc()

	start := time.Now()
	err := uc.cache.AddByID(ctx, user)
	end := time.Now().Sub(start)

	if err != nil {
		totalCacheErrorsCounter.Inc()
	}

	defer cacheLatencyCounter.Observe(end.Seconds())

	return err
}

func (uc *UserCacheWithMetrics) AddByTgID(ctx context.Context, user *models.User) error {
	totalCacheCallsCounter.Inc()

	start := time.Now()
	err := uc.cache.AddByTgID(ctx, user)
	end := time.Now().Sub(start)

	if err != nil {
		totalCacheErrorsCounter.Inc()
	}

	defer cacheLatencyCounter.Observe(end.Seconds())

	return err
}

func (uc *UserCacheWithMetrics) AddID(ctx context.Context, key int64, val uuid.UUID) error {
	totalCacheCallsCounter.Inc()

	start := time.Now()
	err := uc.cache.AddID(ctx, key, val)
	end := time.Now().Sub(start)

	if err != nil {
		totalCacheErrorsCounter.Inc()
	}

	defer cacheLatencyCounter.Observe(end.Seconds())

	return err
}

func (uc *UserCacheWithMetrics) AddTgID(ctx context.Context, key uuid.UUID, val int64) error {
	totalCacheCallsCounter.Inc()

	start := time.Now()
	err := uc.cache.AddTgID(ctx, key, val)
	end := time.Now().Sub(start)

	if err != nil {
		totalCacheErrorsCounter.Inc()
	}

	defer cacheLatencyCounter.Observe(end.Seconds())

	return err
}

func (uc *UserCacheWithMetrics) InvalidateUserID(ctx context.Context, id uuid.UUID) error {
	return withEvictionCounters(uc.cache.InvalidateUserID, ctx, id)
}

func (uc *UserCacheWithMetrics) InvalidateUserByID(ctx context.Context, id uuid.UUID) error {
	return withEvictionCounters(uc.cache.InvalidateUserByID, ctx, id)
}

func (uc *UserCacheWithMetrics) InvalidateUserTgID(ctx context.Context, id int64) error {
	return withEvictionCounters(uc.cache.InvalidateUserTgID, ctx, id)
}

func (uc *UserCacheWithMetrics) InvalidateUserByTgID(ctx context.Context, id int64) error {
	return withEvictionCounters(uc.cache.InvalidateUserByTgID, ctx, id)
}
