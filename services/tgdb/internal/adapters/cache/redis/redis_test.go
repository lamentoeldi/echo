package redis

import (
	"context"
	"fmt"
	"github.com/echo/tgdb/internal/domain/models"
	"github.com/echo/tgdb/pkg/log"
	"github.com/echo/tgdb/pkg/protoutils"
	redismock "github.com/go-redis/redismock/v9"
	"github.com/google/uuid"
	"go.uber.org/zap"
	"google.golang.org/protobuf/proto"
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

func TestUserCache_AddByID(t *testing.T) {
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

	cfg := &Config{
		TTL: 1 * time.Minute,
	}

	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			db, mock := redismock.NewClientMock()
			defer db.Close()

			cache := NewUserCache(cfg, db)

			key := getUserKeyID(tc.user.ID)
			bytes, _ := proto.Marshal(protoutils.FromDTO(tc.user))

			mock.
				ExpectSet(key, bytes, cfg.TTL).
				SetVal("")

			ctx, cancel := testCtx(t)
			defer cancel()

			err := cache.AddByID(ctx, tc.user)
			checkErr(t, err, tc.wantErr)

			err = mock.ExpectationsWereMet()
			checkErr(t, err, false)
		})
	}
}

func TestUserCache_AddByTgID(t *testing.T) {
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

	cfg := &Config{
		TTL: 1 * time.Minute,
	}

	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			db, mock := redismock.NewClientMock()
			defer db.Close()

			cache := NewUserCache(cfg, db)

			key := getUserKeyTgID(tc.user.TgID)
			bytes, _ := proto.Marshal(protoutils.FromDTO(tc.user))

			mock.
				ExpectSet(key, bytes, cfg.TTL).
				SetVal("")

			ctx, cancel := testCtx(t)
			defer cancel()

			err := cache.AddByTgID(ctx, tc.user)
			checkErr(t, err, tc.wantErr)

			err = mock.ExpectationsWereMet()
			checkErr(t, err, false)
		})
	}
}

func TestUserCache_AddID(t *testing.T) {
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

	cfg := &Config{
		TTL: 1 * time.Minute,
	}

	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			db, mock := redismock.NewClientMock()
			defer db.Close()

			cache := NewUserCache(cfg, db)

			key := getKeyTgID(tc.user.TgID)

			mock.
				ExpectSet(key, tc.user.ID.String(), cfg.TTL).
				SetVal("")

			ctx, cancel := testCtx(t)
			defer cancel()

			err := cache.AddID(ctx, tc.user.TgID, tc.user.ID)
			checkErr(t, err, tc.wantErr)

			err = mock.ExpectationsWereMet()
			checkErr(t, err, false)
		})
	}
}

func TestUserCache_AddTgID(t *testing.T) {
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

	cfg := &Config{
		TTL: 1 * time.Minute,
	}

	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			db, mock := redismock.NewClientMock()
			defer db.Close()

			cache := NewUserCache(cfg, db)

			key := getKeyID(tc.user.ID)

			mock.
				ExpectSet(key, tc.user.TgID, cfg.TTL).
				SetVal("")

			ctx, cancel := testCtx(t)
			defer cancel()

			err := cache.AddTgID(ctx, tc.user.ID, tc.user.TgID)
			checkErr(t, err, tc.wantErr)

			err = mock.ExpectationsWereMet()
			checkErr(t, err, false)
		})
	}
}

func TestUserCache_GetByID(t *testing.T) {
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

	cfg := &Config{
		TTL: 1 * time.Minute,
	}

	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			db, mock := redismock.NewClientMock()
			defer db.Close()

			cache := NewUserCache(cfg, db)

			key := getUserKeyID(tc.user.ID)
			bytes, _ := proto.Marshal(protoutils.FromDTO(tc.user))

			mock.
				ExpectGet(key).
				SetVal(string(bytes))

			ctx, cancel := testCtx(t)
			defer cancel()

			_, err := cache.GetByID(ctx, tc.user.ID)
			checkErr(t, err, tc.wantErr)

			err = mock.ExpectationsWereMet()
			checkErr(t, err, false)
		})
	}
}

func TestUserCache_GetByTgID(t *testing.T) {
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

	cfg := &Config{
		TTL: 1 * time.Minute,
	}

	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			db, mock := redismock.NewClientMock()
			defer db.Close()

			cache := NewUserCache(cfg, db)

			key := getUserKeyTgID(tc.user.TgID)
			bytes, _ := proto.Marshal(protoutils.FromDTO(tc.user))

			mock.
				ExpectGet(key).
				SetVal(string(bytes))

			ctx, cancel := testCtx(t)
			defer cancel()

			_, err := cache.GetByTgID(ctx, tc.user.TgID)
			checkErr(t, err, tc.wantErr)

			err = mock.ExpectationsWereMet()
			checkErr(t, err, false)
		})
	}
}

func TestUserCache_GetID(t *testing.T) {
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

	cfg := &Config{
		TTL: 1 * time.Minute,
	}

	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			db, mock := redismock.NewClientMock()
			defer db.Close()

			cache := NewUserCache(cfg, db)

			key := getKeyTgID(tc.user.TgID)

			mock.
				ExpectGet(key).
				SetVal(tc.user.ID.String())

			ctx, cancel := testCtx(t)
			defer cancel()

			_, err := cache.GetID(ctx, tc.user.TgID)
			checkErr(t, err, tc.wantErr)

			err = mock.ExpectationsWereMet()
			checkErr(t, err, false)
		})
	}
}

func TestUserCache_GetTgID(t *testing.T) {
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

	cfg := &Config{
		TTL: 1 * time.Minute,
	}

	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			db, mock := redismock.NewClientMock()
			defer db.Close()

			cache := NewUserCache(cfg, db)

			key := getKeyID(tc.user.ID)

			mock.
				ExpectGet(key).
				SetVal(fmt.Sprint(tc.user.TgID))

			ctx, cancel := testCtx(t)
			defer cancel()

			_, err := cache.GetTgID(ctx, tc.user.ID)
			checkErr(t, err, tc.wantErr)

			err = mock.ExpectationsWereMet()
			checkErr(t, err, false)
		})
	}
}

func TestUserCache_InvalidateUserByID(t *testing.T) {
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

	cfg := &Config{
		TTL: 1 * time.Minute,
	}

	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			db, mock := redismock.NewClientMock()
			defer db.Close()

			cache := NewUserCache(cfg, db)

			key := getUserKeyID(tc.user.ID)

			mock.
				ExpectDel(key).
				SetVal(1)
			ctx, cancel := testCtx(t)
			defer cancel()

			err := cache.InvalidateUserByID(ctx, tc.user.ID)
			checkErr(t, err, tc.wantErr)

			err = mock.ExpectationsWereMet()
			checkErr(t, err, false)
		})
	}
}

func TestUserCache_InvalidateUserByTgID(t *testing.T) {
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

	cfg := &Config{
		TTL: 1 * time.Minute,
	}

	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			db, mock := redismock.NewClientMock()
			defer db.Close()

			cache := NewUserCache(cfg, db)

			key := getUserKeyTgID(tc.user.TgID)

			mock.
				ExpectDel(key).
				SetVal(1)
			ctx, cancel := testCtx(t)
			defer cancel()

			err := cache.InvalidateUserByTgID(ctx, tc.user.TgID)
			checkErr(t, err, tc.wantErr)

			err = mock.ExpectationsWereMet()
			checkErr(t, err, false)
		})
	}
}

func TestUserCache_InvalidateUserID(t *testing.T) {
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

	cfg := &Config{
		TTL: 1 * time.Minute,
	}

	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			db, mock := redismock.NewClientMock()
			defer db.Close()

			cache := NewUserCache(cfg, db)

			key := getKeyID(tc.user.ID)

			mock.
				ExpectDel(key).
				SetVal(1)
			ctx, cancel := testCtx(t)
			defer cancel()

			err := cache.InvalidateUserID(ctx, tc.user.ID)
			checkErr(t, err, tc.wantErr)

			err = mock.ExpectationsWereMet()
			checkErr(t, err, false)
		})
	}
}

func TestUserCache_InvalidateUserTgID(t *testing.T) {
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

	cfg := &Config{
		TTL: 1 * time.Minute,
	}

	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			db, mock := redismock.NewClientMock()
			defer db.Close()

			cache := NewUserCache(cfg, db)

			key := getKeyTgID(tc.user.TgID)

			mock.
				ExpectDel(key).
				SetVal(1)
			ctx, cancel := testCtx(t)
			defer cancel()

			err := cache.InvalidateUserTgID(ctx, tc.user.TgID)
			checkErr(t, err, tc.wantErr)

			err = mock.ExpectationsWereMet()
			checkErr(t, err, false)
		})
	}
}
