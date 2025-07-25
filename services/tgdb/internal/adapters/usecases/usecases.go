package usecases

import (
	"context"
	"errors"
	"github.com/echo/tgdb/internal/domain/models"
	"github.com/echo/tgdb/internal/ports"
	e "github.com/echo/tgdb/pkg/errors"
	"github.com/echo/tgdb/pkg/log"
	"github.com/google/uuid"
	"go.uber.org/zap"
)

const (
	cacheError = "cache error"
)

func logCacheError(ctx context.Context, err error) {
	if err != nil && !errors.Is(err, e.ErrCacheMiss) {
		log.
			FromContext(ctx).
			Warn(cacheError, zap.Error(err))
	}
}

type UseCases struct {
	userRepo  ports.UserRepoPort
	userCache ports.UserCachePort
}

func New(userRepo ports.UserRepoPort, userCache ports.UserCachePort) (*UseCases, error) {
	return &UseCases{
		userRepo:  userRepo,
		userCache: userCache,
	}, nil
}

func (uc *UseCases) CreateUser(ctx context.Context, user *models.User) error {
	return uc.userRepo.Add(ctx, user)
}

func (uc *UseCases) GetUserByID(ctx context.Context, id uuid.UUID) (*models.User, error) {
	user, err := uc.userCache.GetByID(ctx, id)
	logCacheError(ctx, err)

	if err == nil {
		return user, nil
	}

	return uc.userRepo.GetByID(ctx, id)
}

func (uc *UseCases) GetUserByTgID(ctx context.Context, id int64) (*models.User, error) {
	user, err := uc.userCache.GetByTgID(ctx, id)
	logCacheError(ctx, err)

	if err == nil {
		return user, nil
	}

	return uc.userRepo.GetByTgID(ctx, id)
}

func (uc *UseCases) UpdateUserByID(ctx context.Context, id uuid.UUID, update *models.UserUpdate) error {
	err := uc.userRepo.UpdateByID(ctx, id, update)
	if err != nil {
		return err
	}

	err = uc.userCache.InvalidateUserByID(ctx, id)
	logCacheError(ctx, err)

	return nil
}

func (uc *UseCases) UpdateUserByTgID(ctx context.Context, id int64, update *models.UserUpdate) error {
	err := uc.userRepo.UpdateByTgID(ctx, id, update)
	if err != nil {
		return err
	}

	err = uc.userCache.InvalidateUserByTgID(ctx, id)
	logCacheError(ctx, err)

	return nil
}

func (uc *UseCases) DeleteUserByID(ctx context.Context, id uuid.UUID) error {
	err := uc.userRepo.DeleteByID(ctx, id)
	if err != nil {
		return err
	}

	err = uc.userCache.InvalidateUserByID(ctx, id)
	logCacheError(ctx, err)

	return nil
}

func (uc *UseCases) DeleteUserByTgID(ctx context.Context, id int64) error {
	err := uc.userRepo.DeleteByTgID(ctx, id)
	if err != nil {
		return err
	}

	err = uc.userCache.InvalidateUserByTgID(ctx, id)
	logCacheError(ctx, err)

	return nil
}

func (uc *UseCases) GetUserID(ctx context.Context, id int64) (uuid.UUID, error) {
	uid, err := uc.userCache.GetID(ctx, id)
	logCacheError(ctx, err)

	if err == nil {
		return uid, nil
	}

	return uc.userRepo.GetID(ctx, id)
}

func (uc *UseCases) GetUserTgID(ctx context.Context, id uuid.UUID) (int64, error) {
	tgID, err := uc.userCache.GetTgID(ctx, id)
	logCacheError(ctx, err)

	if err == nil {
		return tgID, nil
	}

	return uc.userRepo.GetTgID(ctx, id)
}
