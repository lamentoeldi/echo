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

type UserRepoPort interface {
	UserCommandPort
	UserQueryPort
}

type UserCachePort interface {
	UserQueryPort
	// InvalidateUserID deletes uuid -> int entry
	InvalidateUserID(ctx context.Context, id uuid.UUID) error
	// InvalidateUserByID deletes uuid -> models.User entry
	InvalidateUserByID(ctx context.Context, id uuid.UUID) error
	// InvalidateUserTgID deletes int -> uuid entry
	InvalidateUserTgID(ctx context.Context, id int64) error
	// InvalidateUserByTgID deletes int -> models.User entry
	InvalidateUserByTgID(ctx context.Context, id int64) error
}
