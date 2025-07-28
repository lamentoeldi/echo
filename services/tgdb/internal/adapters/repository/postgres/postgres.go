package postgres

import (
	"context"
	"database/sql"
	"fmt"
	sq "github.com/Masterminds/squirrel"
	"github.com/echo/tgdb/internal/domain/models"
	"github.com/google/uuid"
	"github.com/jackc/pgx/v5/pgxpool"
)

const (
	errPatternAddUser    = "failed to add user: %w"
	errPatternGetUser    = "failed to get user: %w"
	errPatternUpdateUser = "failed to update user: %w"
	errPatternDeleteUser = "failed to delete user: %w"
	errPatternGetUserID  = "failed to get user id: %w"
)

type PgUserRepo struct {
	pool *pgxpool.Pool
}

func NewUserRepo(pool *pgxpool.Pool) (*PgUserRepo, error) {
	return &PgUserRepo{pool: pool}, nil
}

func (p *PgUserRepo) Add(ctx context.Context, user *models.User) error {
	query, args, err := sq.
		Insert("users").
		Columns("id", "tg_id", "tg_username", "lang").
		Values(user.ID, user.TgID, user.TgUsername, user.Language).
		PlaceholderFormat(sq.Dollar).
		ToSql()
	if err != nil {
		return fmt.Errorf(errPatternAddUser, err)
	}

	_, err = p.pool.Exec(ctx, query, args...)
	if err != nil {
		return fmt.Errorf(errPatternAddUser, err)
	}

	return nil
}

func (p *PgUserRepo) GetByID(ctx context.Context, id uuid.UUID) (*models.User, error) {
	query, args, err := sq.
		Select("tg_id", "tg_username", "lang", "created_at").
		From("users").
		Where(sq.Eq{"id": id}).
		PlaceholderFormat(sq.Dollar).
		ToSql()
	if err != nil {
		return nil, fmt.Errorf(errPatternGetUser, err)
	}

	username := sql.NullString{}
	user := &models.User{
		ID: id,
	}

	err = p.pool.
		QueryRow(ctx, query, args...).
		Scan(&user.TgID, &username, &user.Language, &user.CreatedAt)
	if err != nil {
		return nil, fmt.Errorf(errPatternGetUser, err)
	}

	if username.Valid {
		user.TgUsername = username.String
	}

	return user, nil
}

func (p *PgUserRepo) GetByTgID(ctx context.Context, id int64) (*models.User, error) {
	query, args, err := sq.
		Select("id", "tg_username", "lang", "created_at").
		From("users").
		Where(sq.Eq{"tg_id": id}).
		PlaceholderFormat(sq.Dollar).
		ToSql()
	if err != nil {
		return nil, fmt.Errorf(errPatternGetUser, err)
	}

	username := sql.NullString{}
	user := &models.User{
		TgID: id,
	}

	err = p.pool.
		QueryRow(ctx, query, args...).
		Scan(&user.ID, &username, &user.Language, &user.CreatedAt)
	if err != nil {
		return nil, fmt.Errorf(errPatternGetUser, err)
	}

	if username.Valid {
		user.TgUsername = username.String
	}

	return user, nil
}

func (p *PgUserRepo) UpdateByID(ctx context.Context, id uuid.UUID, user *models.UserUpdate) error {
	tmpl := sq.
		Update("users").
		Where(sq.Eq{"id": id})
	if user.TgUsername != "" {
		tmpl = tmpl.
			Set("tg_username", user.TgUsername)
	}
	if user.Language != "" {
		tmpl = tmpl.
			Set("lang", user.Language)
	}
	query, args, err := tmpl.
		PlaceholderFormat(sq.Dollar).
		ToSql()
	if err != nil {
		return fmt.Errorf(errPatternUpdateUser, err)
	}

	_, err = p.pool.Exec(ctx, query, args...)
	if err != nil {
		return fmt.Errorf(errPatternUpdateUser, err)
	}

	return nil
}

func (p *PgUserRepo) UpdateByTgID(ctx context.Context, id int64, user *models.UserUpdate) error {
	tmpl := sq.
		Update("users").
		Where(sq.Eq{"tg_id": id})
	if user.TgUsername != "" {
		tmpl = tmpl.
			Set("tg_username", user.TgUsername)
	}
	if user.Language != "" {
		tmpl = tmpl.
			Set("lang", user.Language)
	}
	query, args, err := tmpl.
		PlaceholderFormat(sq.Dollar).
		ToSql()
	if err != nil {
		return fmt.Errorf(errPatternUpdateUser, err)
	}

	_, err = p.pool.Exec(ctx, query, args...)
	if err != nil {
		return fmt.Errorf(errPatternUpdateUser, err)
	}

	return nil
}

func (p *PgUserRepo) DeleteByID(ctx context.Context, id uuid.UUID) error {
	query, args, err := sq.
		Delete("users").
		Where(sq.Eq{"id": id}).
		PlaceholderFormat(sq.Dollar).
		ToSql()
	if err != nil {
		return fmt.Errorf(errPatternDeleteUser, err)
	}

	_, err = p.pool.Exec(ctx, query, args...)
	if err != nil {
		return fmt.Errorf(errPatternDeleteUser, err)
	}

	return nil
}

func (p *PgUserRepo) DeleteByTgID(ctx context.Context, id int64) error {
	query, args, err := sq.
		Delete("users").
		Where(sq.Eq{"tg_id": id}).
		PlaceholderFormat(sq.Dollar).
		ToSql()
	if err != nil {
		return fmt.Errorf(errPatternDeleteUser, err)
	}

	_, err = p.pool.Exec(ctx, query, args...)
	if err != nil {
		return fmt.Errorf(errPatternDeleteUser, err)
	}

	return nil
}

func (p *PgUserRepo) GetID(ctx context.Context, id int64) (uuid.UUID, error) {
	query, args, err := sq.
		Select("id").
		From("users").
		Where(sq.Eq{"tg_id": id}).
		PlaceholderFormat(sq.Dollar).
		ToSql()
	if err != nil {
		return uuid.Nil, fmt.Errorf(errPatternGetUserID, err)
	}

	uid := uuid.UUID{}
	err = p.pool.
		QueryRow(ctx, query, args...).
		Scan(&uid)
	if err != nil {
		return uuid.Nil, fmt.Errorf(errPatternGetUserID, err)
	}

	return uid, nil
}

func (p *PgUserRepo) GetTgID(ctx context.Context, id uuid.UUID) (int64, error) {
	query, args, err := sq.
		Select("tg_id").
		From("users").
		Where(sq.Eq{"id": id}).
		PlaceholderFormat(sq.Dollar).
		ToSql()
	if err != nil {
		return 0, fmt.Errorf(errPatternGetUserID, err)
	}

	tgID := int64(0)
	err = p.pool.
		QueryRow(ctx, query, args...).
		Scan(&tgID)
	if err != nil {
		return 0, fmt.Errorf(errPatternGetUserID, err)
	}

	return tgID, nil
}
