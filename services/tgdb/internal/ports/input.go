package ports

import (
	"context"
	"github.com/echo/tgdb/internal/domain/models"
	"github.com/google/uuid"
)

type UseCasePort interface {
	CreateUser(ctx context.Context, user *models.User) error
	GetUserByID(ctx context.Context, id uuid.UUID) (*models.User, error)
	GetUserByTgID(ctx context.Context, id int64) (*models.User, error)
	UpdateUserByID(ctx context.Context, id uuid.UUID, update *models.UserUpdate) error
	UpdateUserByTgID(ctx context.Context, id int64, update *models.UserUpdate) error
	DeleteUserByID(ctx context.Context, id uuid.UUID) error
	DeleteUserByTgID(ctx context.Context, id int64) error
	GetUserID(ctx context.Context, id int64) (uuid.UUID, error)
	GetUserTgID(ctx context.Context, id uuid.UUID) (int64, error)
}
