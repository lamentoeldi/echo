package postgres

import (
	"context"
	"fmt"
	"github.com/echo/tgdb/internal/domain/models"
	"github.com/echo/tgdb/pkg/log"
	"github.com/echo/tgdb/pkg/postgres/pool"
	"github.com/golang-migrate/migrate/v4"
	"github.com/golang-migrate/migrate/v4/database/pgx/v5"
	"github.com/google/uuid"
	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/jackc/pgx/v5/stdlib"
	"go.uber.org/zap"
	"os"
	"testing"
	"time"
)

func testUser() *models.User {
	return &models.User{
		ID:         uuid.MustParse("2d054519-d300-4233-a1cc-474f25f822d4"),
		TgID:       123456,
		TgUsername: "",
		Language:   "ru",
		CreatedAt:  time.Now(),
	}
}

func testUpdate() *models.UserUpdate {
	return &models.UserUpdate{
		Language: "en",
	}
}

func testCtx(t *testing.T) (context.Context, context.CancelFunc) {
	logger := must(zap.NewDevelopment())
	ctx := log.ContextWithLogger(t.Context(), logger)
	return context.WithTimeout(ctx, 300*time.Millisecond)
}

func checkErr(t *testing.T, err error, wantErr bool) {
	if err != nil && !wantErr {
		t.Errorf("expected no error, got %v", err)
	}
	if err == nil && wantErr {
		t.Errorf("expected error, got nil")
	}
}

func must[T any](v T, err error) T {
	if err != nil {
		panic(err)
	}
	return v
}

func rollbackMigrations(pool *pgxpool.Pool, migrationsDir, dbName string) error {
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

	return m.Down()
}

func TestPgUserRepo_Add(t *testing.T) {
	cases := []struct {
		name    string
		user    *models.User
		wantErr bool
	}{
		{
			name: "success",
			user: testUser(),
		},
	}

	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			ctx := t.Context()
			p, err := pool.New(ctx)
			if err != nil {
				t.Fatal(err)
			}

			t.Cleanup(func() {
				_ = rollbackMigrations(
					p,
					os.Getenv("POSTGRES_MIGRATIONS"),
					os.Getenv("POSTGRES_DB"),
				)
			})

			repo, _ := NewUserRepo(p)

			ctx, cancel := testCtx(t)
			defer cancel()

			err = repo.Add(ctx, tc.user)
			checkErr(t, err, tc.wantErr)
		})
	}
}

func TestPgUserRepo_GetByID(t *testing.T) {
	cases := []struct {
		name    string
		userID  uuid.UUID
		user    *models.User
		wantErr bool
	}{
		{
			name:   "success",
			userID: testUser().ID,
			user:   testUser(),
		},
		{
			name:    "not found",
			userID:  uuid.New(),
			user:    testUser(),
			wantErr: true,
		},
	}

	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			ctx := t.Context()
			p, err := pool.New(ctx)
			if err != nil {
				t.Fatal(err)
			}

			t.Cleanup(func() {
				_ = rollbackMigrations(
					p,
					os.Getenv("POSTGRES_MIGRATIONS"),
					os.Getenv("POSTGRES_DB"),
				)
			})

			repo, _ := NewUserRepo(p)
			err = repo.Add(ctx, tc.user)
			if err != nil {
				t.Fatal(err)
			}

			ctx, cancel := testCtx(t)
			defer cancel()

			_, err = repo.GetByID(ctx, tc.userID)
			checkErr(t, err, tc.wantErr)
		})
	}
}

func TestPgUserRepo_GetByTgID(t *testing.T) {
	cases := []struct {
		name    string
		userID  int64
		user    *models.User
		wantErr bool
	}{
		{
			name:   "success",
			userID: testUser().TgID,
			user:   testUser(),
		},
		{
			name:    "not found",
			userID:  int64(7891011),
			user:    testUser(),
			wantErr: true,
		},
	}

	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			ctx := t.Context()
			p, err := pool.New(ctx)
			if err != nil {
				t.Fatal(err)
			}

			t.Cleanup(func() {
				_ = rollbackMigrations(
					p,
					os.Getenv("POSTGRES_MIGRATIONS"),
					os.Getenv("POSTGRES_DB"),
				)
			})

			repo, _ := NewUserRepo(p)
			err = repo.Add(ctx, tc.user)
			if err != nil {
				t.Fatal(err)
			}

			ctx, cancel := testCtx(t)
			defer cancel()

			_, err = repo.GetByTgID(ctx, tc.userID)
			checkErr(t, err, tc.wantErr)
		})
	}
}

func TestPgUserRepo_UpdateByID(t *testing.T) {
	cases := []struct {
		name    string
		user    *models.User
		userID  uuid.UUID
		update  *models.UserUpdate
		wantErr bool
	}{
		{
			name:   "success",
			user:   testUser(),
			userID: testUser().ID,
			update: testUpdate(),
		},
	}

	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			ctx := t.Context()
			p, err := pool.New(ctx)
			if err != nil {
				t.Fatal(err)
			}

			t.Cleanup(func() {
				_ = rollbackMigrations(
					p,
					os.Getenv("POSTGRES_MIGRATIONS"),
					os.Getenv("POSTGRES_DB"),
				)
			})

			repo, _ := NewUserRepo(p)
			err = repo.Add(ctx, tc.user)
			if err != nil {
				t.Fatal(err)
			}

			ctx, cancel := testCtx(t)
			defer cancel()

			err = repo.UpdateByID(ctx, tc.userID, tc.update)
			checkErr(t, err, tc.wantErr)

			user, err := repo.GetByID(ctx, tc.userID)
			if err != nil {
				t.Fatal(err)
			}

			if user.Language != tc.update.Language {
				t.Errorf("got %q, want %q", user.Language, tc.update.Language)
			}
		})
	}
}

func TestPgUserRepo_UpdateByTgID(t *testing.T) {
	cases := []struct {
		name    string
		user    *models.User
		userID  int64
		update  *models.UserUpdate
		wantErr bool
	}{
		{
			name:   "success",
			user:   testUser(),
			userID: testUser().TgID,
			update: testUpdate(),
		},
	}

	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			ctx := t.Context()
			p, err := pool.New(ctx)
			if err != nil {
				t.Fatal(err)
			}

			t.Cleanup(func() {
				_ = rollbackMigrations(
					p,
					os.Getenv("POSTGRES_MIGRATIONS"),
					os.Getenv("POSTGRES_DB"),
				)
			})

			repo, _ := NewUserRepo(p)
			err = repo.Add(ctx, tc.user)
			if err != nil {
				t.Fatal(err)
			}

			ctx, cancel := testCtx(t)
			defer cancel()

			err = repo.UpdateByTgID(ctx, tc.userID, tc.update)
			checkErr(t, err, tc.wantErr)

			user, err := repo.GetByTgID(ctx, tc.userID)
			if err != nil {
				t.Fatal(err)
			}

			if user.Language != tc.update.Language {
				t.Errorf("got %q, want %q", user.Language, tc.update.Language)
			}
		})
	}
}

func TestPgUserRepo_DeleteByID(t *testing.T) {
	cases := []struct {
		name    string
		user    *models.User
		userID  uuid.UUID
		wantErr bool
	}{
		{
			name:   "success",
			user:   testUser(),
			userID: testUser().ID,
		},
	}

	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			ctx := t.Context()
			p, err := pool.New(ctx)
			if err != nil {
				t.Fatal(err)
			}

			t.Cleanup(func() {
				_ = rollbackMigrations(
					p,
					os.Getenv("POSTGRES_MIGRATIONS"),
					os.Getenv("POSTGRES_DB"),
				)
			})

			repo, _ := NewUserRepo(p)
			err = repo.Add(ctx, tc.user)
			if err != nil {
				t.Fatal(err)
			}

			ctx, cancel := testCtx(t)
			defer cancel()

			err = repo.DeleteByID(ctx, tc.userID)
			checkErr(t, err, tc.wantErr)
		})
	}
}

func TestPgUserRepo_DeleteByTgID(t *testing.T) {
	cases := []struct {
		name    string
		user    *models.User
		userID  int64
		wantErr bool
	}{
		{
			name:   "success",
			user:   testUser(),
			userID: testUser().TgID,
		},
	}

	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			ctx := t.Context()
			p, err := pool.New(ctx)
			if err != nil {
				t.Fatal(err)
			}

			t.Cleanup(func() {
				_ = rollbackMigrations(
					p,
					os.Getenv("POSTGRES_MIGRATIONS"),
					os.Getenv("POSTGRES_DB"),
				)
			})

			repo, _ := NewUserRepo(p)
			err = repo.Add(ctx, tc.user)
			if err != nil {
				t.Fatal(err)
			}

			ctx, cancel := testCtx(t)
			defer cancel()

			err = repo.DeleteByTgID(ctx, tc.userID)
			checkErr(t, err, tc.wantErr)
		})
	}
}

func TestPgUserRepo_GetID(t *testing.T) {
	cases := []struct {
		name     string
		user     *models.User
		userTgID int64
		wantErr  bool
	}{
		{
			name:     "success",
			user:     testUser(),
			userTgID: testUser().TgID,
		},
	}

	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			ctx := t.Context()
			p, err := pool.New(ctx)
			if err != nil {
				t.Fatal(err)
			}

			t.Cleanup(func() {
				_ = rollbackMigrations(
					p,
					os.Getenv("POSTGRES_MIGRATIONS"),
					os.Getenv("POSTGRES_DB"),
				)
			})

			repo, _ := NewUserRepo(p)
			err = repo.Add(ctx, tc.user)
			if err != nil {
				t.Fatal(err)
			}

			ctx, cancel := testCtx(t)
			defer cancel()

			uid, err := repo.GetID(ctx, tc.userTgID)
			checkErr(t, err, tc.wantErr)

			if uid != tc.user.ID {
				t.Errorf("got %d, want %d", uid, tc.user.ID)
			}
		})
	}
}

func TestPgUserRepo_GetTgID(t *testing.T) {
	cases := []struct {
		name    string
		user    *models.User
		userID  uuid.UUID
		wantErr bool
	}{
		{
			name:   "success",
			user:   testUser(),
			userID: testUser().ID,
		},
	}

	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			ctx := t.Context()
			p, err := pool.New(ctx)
			if err != nil {
				t.Fatal(err)
			}

			t.Cleanup(func() {
				_ = rollbackMigrations(
					p,
					os.Getenv("POSTGRES_MIGRATIONS"),
					os.Getenv("POSTGRES_DB"),
				)
			})

			repo, _ := NewUserRepo(p)
			err = repo.Add(ctx, tc.user)
			if err != nil {
				t.Fatal(err)
			}

			ctx, cancel := testCtx(t)
			defer cancel()

			tgID, err := repo.GetTgID(ctx, tc.userID)
			checkErr(t, err, tc.wantErr)

			if tgID != tc.user.TgID {
				t.Errorf("got %d, want %d", tgID, tc.user.ID)
			}
		})
	}
}
