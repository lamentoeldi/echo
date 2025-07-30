package usecases

import (
	"context"
	"errors"
	"fmt"
	"github.com/echo/tgdb/internal/domain/models"
	e "github.com/echo/tgdb/pkg/errors"
	"github.com/echo/tgdb/pkg/log"
	"github.com/echo/tgdb/pkg/mock"
	"github.com/google/uuid"
	"go.uber.org/mock/gomock"
	"go.uber.org/zap"
	"testing"
	"time"
)

var (
	repoErr  = fmt.Errorf("repo err")
	cacheErr = fmt.Errorf("cache err")
)

func testUser() *models.User {
	return &models.User{
		ID:         uuid.MustParse("2d054519-d300-4233-a1cc-474f25f822d4"),
		TgID:       123456,
		TgUsername: "",
		Language:   "en",
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

func checkErr(t *testing.T, err, expectedErr error) {
	if !errors.Is(err, expectedErr) {
		t.Errorf("expected error [%v], got [%v]", expectedErr, err)
	}
}

func must[T any](v T, err error) T {
	if err != nil {
		panic(err)
	}
	return v
}

func TestUseCases_CreateUser(t *testing.T) {
	cases := []struct {
		name        string
		user        *models.User
		repoCalls   int
		cacheCalls  int
		repoErr     error
		cacheErr    error
		expectedErr error
	}{
		{
			name:       "success",
			user:       testUser(),
			repoCalls:  1,
			cacheCalls: 1,
		},
		{
			name:        "repo err",
			user:        testUser(),
			repoErr:     repoErr,
			expectedErr: repoErr,
			repoCalls:   1,
		},
		{
			name:       "cache err",
			user:       testUser(),
			cacheErr:   cacheErr,
			repoCalls:  1,
			cacheCalls: 1,
		},
	}

	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			ctrl := gomock.NewController(t)

			userRepo := mock.NewMockUserRepoPort(ctrl)
			userRepo.
				EXPECT().
				Add(gomock.Any(), tc.user).
				Times(tc.repoCalls).
				Return(tc.repoErr)

			userCache := mock.NewMockUserCachePort(ctrl)
			userCache.
				EXPECT().
				AddByTgID(gomock.Any(), tc.user).
				Times(tc.cacheCalls).
				Return(tc.cacheErr)

			uc, _ := New(userRepo, userCache)

			ctx, cancel := testCtx(t)
			defer cancel()

			err := uc.CreateUser(ctx, tc.user)
			checkErr(t, err, tc.expectedErr)
		})
	}
}

func TestUseCases_GetUserByID(t *testing.T) {
	cases := []struct {
		name          string
		user          *models.User
		repoCalls     int
		cacheGetCalls int
		cacheAddCalls int
		repoErr       error
		cacheErr      error
		expectedErr   error
	}{
		{
			name:          "success, cache hit",
			user:          testUser(),
			cacheGetCalls: 1,
		},
		{
			name:          "success, cache miss",
			user:          testUser(),
			cacheGetCalls: 1,
			cacheAddCalls: 1,
			repoCalls:     1,
			cacheErr:      e.ErrCacheMiss,
		},
		{
			name:          "repo err, cache miss",
			user:          testUser(),
			cacheGetCalls: 1,
			repoCalls:     1,
			cacheErr:      e.ErrCacheMiss,
			repoErr:       repoErr,
			expectedErr:   repoErr,
		},
	}

	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			ctrl := gomock.NewController(t)

			userRepo := mock.NewMockUserRepoPort(ctrl)
			userRepo.
				EXPECT().
				GetByID(gomock.Any(), tc.user.ID).
				Times(tc.repoCalls).
				Return(tc.user, tc.repoErr)

			userCache := mock.NewMockUserCachePort(ctrl)
			userCache.
				EXPECT().
				AddByID(gomock.Any(), tc.user).
				Times(tc.cacheAddCalls).
				Return(tc.cacheErr)
			userCache.
				EXPECT().
				GetByID(gomock.Any(), tc.user.ID).
				Times(tc.cacheGetCalls).
				Return(tc.user, tc.cacheErr)

			uc, _ := New(userRepo, userCache)

			ctx, cancel := testCtx(t)
			defer cancel()

			_, err := uc.GetUserByID(ctx, tc.user.ID)
			checkErr(t, err, tc.expectedErr)
		})
	}
}

func TestUseCases_GetUserByTgID(t *testing.T) {
	cases := []struct {
		name          string
		user          *models.User
		repoCalls     int
		cacheGetCalls int
		cacheAddCalls int
		repoErr       error
		cacheErr      error
		expectedErr   error
	}{
		{
			name:          "success, cache hit",
			user:          testUser(),
			cacheGetCalls: 1,
		},
		{
			name:          "success, cache miss",
			user:          testUser(),
			cacheGetCalls: 1,
			cacheAddCalls: 1,
			repoCalls:     1,
			cacheErr:      e.ErrCacheMiss,
		},
		{
			name:          "repo err, cache miss",
			user:          testUser(),
			cacheGetCalls: 1,
			repoCalls:     1,
			cacheErr:      e.ErrCacheMiss,
			repoErr:       repoErr,
			expectedErr:   repoErr,
		},
	}

	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			ctrl := gomock.NewController(t)

			userRepo := mock.NewMockUserRepoPort(ctrl)
			userRepo.
				EXPECT().
				GetByTgID(gomock.Any(), tc.user.TgID).
				Times(tc.repoCalls).
				Return(tc.user, tc.repoErr)

			userCache := mock.NewMockUserCachePort(ctrl)
			userCache.
				EXPECT().
				AddByTgID(gomock.Any(), tc.user).
				Times(tc.cacheAddCalls).
				Return(tc.cacheErr)
			userCache.
				EXPECT().
				GetByTgID(gomock.Any(), tc.user.TgID).
				Times(tc.cacheGetCalls).
				Return(tc.user, tc.cacheErr)

			uc, _ := New(userRepo, userCache)

			ctx, cancel := testCtx(t)
			defer cancel()

			_, err := uc.GetUserByTgID(ctx, tc.user.TgID)
			checkErr(t, err, tc.expectedErr)
		})
	}
}

func TestUseCases_UpdateUserByID(t *testing.T) {
	cases := []struct {
		name        string
		user        *models.User
		update      *models.UserUpdate
		repoCalls   int
		cacheCalls  int
		repoErr     error
		cacheErr    error
		expectedErr error
	}{
		{
			name:       "success",
			user:       testUser(),
			update:     testUpdate(),
			repoCalls:  1,
			cacheCalls: 1,
		},
		{
			name:        "repo err",
			user:        testUser(),
			update:      testUpdate(),
			repoCalls:   1,
			repoErr:     repoErr,
			expectedErr: repoErr,
		},
	}

	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			ctrl := gomock.NewController(t)

			userRepo := mock.NewMockUserRepoPort(ctrl)
			userRepo.
				EXPECT().
				UpdateByID(gomock.Any(), tc.user.ID, tc.update).
				Times(tc.repoCalls).
				Return(tc.repoErr)

			userCache := mock.NewMockUserCachePort(ctrl)
			userCache.
				EXPECT().
				InvalidateUserByID(gomock.Any(), tc.user.ID).
				Times(tc.cacheCalls).
				Return(tc.cacheErr)

			uc, _ := New(userRepo, userCache)

			ctx, cancel := testCtx(t)
			defer cancel()

			err := uc.UpdateUserByID(ctx, tc.user.ID, tc.update)
			checkErr(t, err, tc.expectedErr)
		})
	}
}

func TestUseCases_UpdateUserByTgID(t *testing.T) {
	cases := []struct {
		name        string
		user        *models.User
		update      *models.UserUpdate
		repoCalls   int
		cacheCalls  int
		repoErr     error
		cacheErr    error
		expectedErr error
	}{
		{
			name:       "success",
			user:       testUser(),
			update:     testUpdate(),
			repoCalls:  1,
			cacheCalls: 1,
		},
		{
			name:        "repo err",
			user:        testUser(),
			update:      testUpdate(),
			repoCalls:   1,
			repoErr:     repoErr,
			expectedErr: repoErr,
		},
	}

	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			ctrl := gomock.NewController(t)

			userRepo := mock.NewMockUserRepoPort(ctrl)
			userRepo.
				EXPECT().
				UpdateByTgID(gomock.Any(), tc.user.TgID, tc.update).
				Times(tc.repoCalls).
				Return(tc.repoErr)

			userCache := mock.NewMockUserCachePort(ctrl)
			userCache.
				EXPECT().
				InvalidateUserByTgID(gomock.Any(), tc.user.TgID).
				Times(tc.cacheCalls).
				Return(tc.cacheErr)

			uc, _ := New(userRepo, userCache)

			ctx, cancel := testCtx(t)
			defer cancel()

			err := uc.UpdateUserByTgID(ctx, tc.user.TgID, tc.update)
			checkErr(t, err, tc.expectedErr)
		})
	}
}

func TestUseCases_DeleteUserByID(t *testing.T) {
	cases := []struct {
		name        string
		user        *models.User
		repoCalls   int
		cacheCalls  int
		repoErr     error
		cacheErr    error
		expectedErr error
	}{
		{
			name:       "success",
			user:       testUser(),
			repoCalls:  1,
			cacheCalls: 1,
		},
		{
			name:        "repo err",
			user:        testUser(),
			repoCalls:   1,
			repoErr:     repoErr,
			expectedErr: repoErr,
		},
	}

	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			ctrl := gomock.NewController(t)

			userRepo := mock.NewMockUserRepoPort(ctrl)
			userRepo.
				EXPECT().
				DeleteByID(gomock.Any(), tc.user.ID).
				Times(tc.repoCalls).
				Return(tc.repoErr)

			userCache := mock.NewMockUserCachePort(ctrl)
			userCache.
				EXPECT().
				InvalidateUserByID(gomock.Any(), tc.user.ID).
				Times(tc.cacheCalls).
				Return(tc.cacheErr)

			uc, _ := New(userRepo, userCache)

			ctx, cancel := testCtx(t)
			defer cancel()

			err := uc.DeleteUserByID(ctx, tc.user.ID)
			checkErr(t, err, tc.expectedErr)
		})
	}
}

func TestUseCases_DeleteUserByTgID(t *testing.T) {
	cases := []struct {
		name        string
		user        *models.User
		repoCalls   int
		cacheCalls  int
		repoErr     error
		cacheErr    error
		expectedErr error
	}{
		{
			name:       "success",
			user:       testUser(),
			repoCalls:  1,
			cacheCalls: 1,
		},
		{
			name:        "repo err",
			user:        testUser(),
			repoCalls:   1,
			repoErr:     repoErr,
			expectedErr: repoErr,
		},
	}

	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			ctrl := gomock.NewController(t)

			userRepo := mock.NewMockUserRepoPort(ctrl)
			userRepo.
				EXPECT().
				DeleteByTgID(gomock.Any(), tc.user.TgID).
				Times(tc.repoCalls).
				Return(tc.repoErr)

			userCache := mock.NewMockUserCachePort(ctrl)
			userCache.
				EXPECT().
				InvalidateUserByTgID(gomock.Any(), tc.user.TgID).
				Times(tc.cacheCalls).
				Return(tc.cacheErr)

			uc, _ := New(userRepo, userCache)

			ctx, cancel := testCtx(t)
			defer cancel()

			err := uc.DeleteUserByTgID(ctx, tc.user.TgID)
			checkErr(t, err, tc.expectedErr)
		})
	}
}

func TestUseCases_GetUserID(t *testing.T) {
	cases := []struct {
		name          string
		user          *models.User
		repoCalls     int
		cacheGetCalls int
		cacheAddCalls int
		repoErr       error
		cacheErr      error
		expectedErr   error
	}{
		{
			name:          "success, cache hit",
			user:          testUser(),
			cacheGetCalls: 1,
		},
		{
			name:          "success, cache miss",
			user:          testUser(),
			cacheGetCalls: 1,
			cacheAddCalls: 1,
			repoCalls:     1,
			cacheErr:      e.ErrCacheMiss,
		},
		{
			name:          "repo err, cache miss",
			user:          testUser(),
			cacheGetCalls: 1,
			repoCalls:     1,
			cacheErr:      e.ErrCacheMiss,
			repoErr:       repoErr,
			expectedErr:   repoErr,
		},
	}

	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			ctrl := gomock.NewController(t)

			userRepo := mock.NewMockUserRepoPort(ctrl)
			userRepo.
				EXPECT().
				GetID(gomock.Any(), tc.user.TgID).
				Times(tc.repoCalls).
				Return(tc.user.ID, tc.repoErr)

			userCache := mock.NewMockUserCachePort(ctrl)
			userCache.
				EXPECT().
				AddID(gomock.Any(), tc.user.TgID, tc.user.ID).
				Times(tc.cacheAddCalls).
				Return(tc.cacheErr)
			userCache.
				EXPECT().
				GetID(gomock.Any(), tc.user.TgID).
				Times(tc.cacheGetCalls).
				Return(tc.user.ID, tc.cacheErr)

			uc, _ := New(userRepo, userCache)

			ctx, cancel := testCtx(t)
			defer cancel()

			_, err := uc.GetUserID(ctx, tc.user.TgID)
			checkErr(t, err, tc.expectedErr)
		})
	}
}

func TestUseCases_GetUserTgID(t *testing.T) {
	cases := []struct {
		name          string
		user          *models.User
		repoCalls     int
		cacheGetCalls int
		cacheAddCalls int
		repoErr       error
		cacheErr      error
		expectedErr   error
	}{
		{
			name:          "success, cache hit",
			user:          testUser(),
			cacheGetCalls: 1,
		},
		{
			name:          "success, cache miss",
			user:          testUser(),
			cacheGetCalls: 1,
			cacheAddCalls: 1,
			repoCalls:     1,
			cacheErr:      e.ErrCacheMiss,
		},
		{
			name:          "repo err, cache miss",
			user:          testUser(),
			cacheGetCalls: 1,
			repoCalls:     1,
			cacheErr:      e.ErrCacheMiss,
			repoErr:       repoErr,
			expectedErr:   repoErr,
		},
	}

	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			ctrl := gomock.NewController(t)

			userRepo := mock.NewMockUserRepoPort(ctrl)
			userRepo.
				EXPECT().
				GetTgID(gomock.Any(), tc.user.ID).
				Times(tc.repoCalls).
				Return(tc.user.TgID, tc.repoErr)

			userCache := mock.NewMockUserCachePort(ctrl)
			userCache.
				EXPECT().
				AddTgID(gomock.Any(), tc.user.ID, tc.user.TgID).
				Times(tc.cacheAddCalls).
				Return(tc.cacheErr)
			userCache.
				EXPECT().
				GetTgID(gomock.Any(), tc.user.ID).
				Times(tc.cacheGetCalls).
				Return(tc.user.TgID, tc.cacheErr)

			uc, _ := New(userRepo, userCache)

			ctx, cancel := testCtx(t)
			defer cancel()

			_, err := uc.GetUserTgID(ctx, tc.user.ID)
			checkErr(t, err, tc.expectedErr)
		})
	}
}
