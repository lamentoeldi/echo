package metrics

import (
	"context"
	"github.com/echo/tgdb/internal/domain/models"
	"github.com/echo/tgdb/internal/ports"
	"github.com/google/uuid"
	"github.com/prometheus/client_golang/prometheus"
	"time"
)

var (
	totalRepoCalls = prometheus.NewCounter(prometheus.CounterOpts{
		Name: "tgdb_db_total_calls",
		Help: "Total number of calls to the database",
	})
	totalRepoErrors = prometheus.NewCounter(prometheus.CounterOpts{
		Name: "tgdb_db_total_errors",
		Help: "Total number of errors from the database",
	})
	repoLatency = prometheus.NewSummary(prometheus.SummaryOpts{
		Name: "tgdb_db_repo_latency",
		Help: "Total time taken to execute the repository",
	})
)

func init() {
	prometheus.MustRegister(totalRepoCalls, totalRepoErrors, repoLatency)
}

func updateWithMetrics[T, E any](
	f func(context.Context, T, E) error,
	ctx context.Context,
	arg1 T, arg2 E,
) error {
	totalRepoCalls.Inc()

	start := time.Now()
	err := f(ctx, arg1, arg2)
	end := time.Now().Sub(start)

	defer repoLatency.Observe(end.Seconds())

	if err != nil {
		totalRepoErrors.Inc()
	}

	return err
}

func deleteWithMetrics[T any](
	f func(context.Context, T) error,
	ctx context.Context,
	arg T,
) error {
	totalRepoCalls.Inc()

	start := time.Now()
	err := f(ctx, arg)
	end := time.Now().Sub(start)

	defer repoLatency.Observe(end.Seconds())

	if err != nil {
		totalRepoErrors.Inc()
	}

	return err
}

func getWithMetrics[T, E any](
	f func(context.Context, T) (E, error),
	ctx context.Context,
	arg T,
) (E, error) {
	totalRepoCalls.Inc()

	start := time.Now()
	res, err := f(ctx, arg)
	end := time.Now().Sub(start)

	defer repoLatency.Observe(end.Seconds())

	if err != nil {
		totalRepoErrors.Inc()
	}

	return res, err
}

type UserRepoWithMetrics struct {
	repo ports.UserRepoPort
}

func NewUserRepoWithMetrics(repo ports.UserRepoPort) *UserRepoWithMetrics {
	return &UserRepoWithMetrics{repo: repo}
}

func (up *UserRepoWithMetrics) Add(ctx context.Context, user *models.User) error {
	totalRepoCalls.Inc()

	start := time.Now()
	err := up.repo.Add(ctx, user)
	end := time.Now().Sub(start)

	defer repoLatency.Observe(end.Seconds())

	if err != nil {
		totalRepoErrors.Inc()
	}

	return err
}

func (up *UserRepoWithMetrics) UpdateByID(ctx context.Context, id uuid.UUID, user *models.UserUpdate) error {
	return updateWithMetrics(up.repo.UpdateByID, ctx, id, user)
}

func (up *UserRepoWithMetrics) UpdateByTgID(ctx context.Context, id int64, user *models.UserUpdate) error {
	return updateWithMetrics(up.repo.UpdateByTgID, ctx, id, user)
}

func (up *UserRepoWithMetrics) DeleteByID(ctx context.Context, id uuid.UUID) error {
	return deleteWithMetrics(up.repo.DeleteByID, ctx, id)
}

func (up *UserRepoWithMetrics) DeleteByTgID(ctx context.Context, id int64) error {
	return deleteWithMetrics(up.repo.DeleteByTgID, ctx, id)
}

func (up *UserRepoWithMetrics) GetByID(ctx context.Context, id uuid.UUID) (*models.User, error) {
	return getWithMetrics(up.repo.GetByID, ctx, id)
}

func (up *UserRepoWithMetrics) GetByTgID(ctx context.Context, id int64) (*models.User, error) {
	return getWithMetrics(up.repo.GetByTgID, ctx, id)
}

func (up *UserRepoWithMetrics) GetID(ctx context.Context, id int64) (uuid.UUID, error) {
	return getWithMetrics(up.repo.GetID, ctx, id)
}

func (up *UserRepoWithMetrics) GetTgID(ctx context.Context, id uuid.UUID) (int64, error) {
	return getWithMetrics(up.repo.GetTgID, ctx, id)
}
