package ports

import (
	"context"
	"github.com/google/uuid"
)
import "github.com/echo/tgdb/internal/domain/models"

type UserCommandPort interface {
	Add(ctx context.Context, user *models.User) error
	UpdateByID(ctx context.Context, id uuid.UUID, user *models.UserUpdate) error
	UpdateByTgID(ctx context.Context, id int64, user *models.UserUpdate) error
	DeleteByID(ctx context.Context, id uuid.UUID) error
	DeleteByTgID(ctx context.Context, id int64) error
}

type UserQueryPort interface {
	GetByID(ctx context.Context, id uuid.UUID) (*models.User, error)
	GetByTgID(ctx context.Context, id int64) (*models.User, error)
	GetID(ctx context.Context, id int64) (uuid.UUID, error)
	GetTgID(ctx context.Context, id uuid.UUID) (int64, error)
}

type UserCachePort interface {
	UserQueryPort
	InvalidateUserID(ctx context.Context, id uuid.UUID) error
	InvalidateUserByID(ctx context.Context, id uuid.UUID) error
	InvalidateUserTgID(ctx context.Context, id int64) error
	InvalidateUserByTgID(ctx context.Context, id int64) error
}
