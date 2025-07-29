package redis

import (
	"context"
	"errors"
	"fmt"
	"github.com/echo/tgdb/internal/domain/models"
	e "github.com/echo/tgdb/pkg/errors"
	pb "github.com/echo/tgdb/pkg/proto"
	"github.com/echo/tgdb/pkg/protoutils"
	"github.com/google/uuid"
	"github.com/ilyakaznacheev/cleanenv"
	"github.com/redis/go-redis/v9"
	"google.golang.org/protobuf/proto"
	"strconv"
	"strings"
	"time"
)

func getUserKeyID(id uuid.UUID) string {
	key := strings.Builder{}
	key.WriteString("user:")
	key.WriteString(id.String())
	return key.String()
}

func getUserKeyTgID(id int64) string {
	key := strings.Builder{}
	key.WriteString("user:")
	key.WriteString(strconv.FormatInt(id, 10))
	return key.String()
}

func getKeyID(id uuid.UUID) string {
	key := strings.Builder{}
	key.WriteString("id:")
	key.WriteString(id.String())
	return key.String()
}

func getKeyTgID(id int64) string {
	key := strings.Builder{}
	key.WriteString("id:")
	key.WriteString(strconv.FormatInt(id, 10))
	return key.String()
}

func wrapErr(err error) (error, bool) {
	if errors.Is(err, redis.Nil) {
		return fmt.Errorf("%w: %w", e.ErrCacheMiss, err), true
	}
	if err != nil {
		return err, true
	}
	return nil, false
}

type Config struct {
	TTL         time.Duration `env:"REDIS_TTL" env-default:"900s"`
	BulkBackoff time.Duration `env:"REDIS_BULK_BACKOFF" env-default:"5s"`
	BulkMaxSize int           `env:"REDIS_BULK_MAX_SIZE" env-default:"100"`
}

func NewConfig() (*Config, error) {
	cfg := Config{}
	err := cleanenv.ReadEnv(&cfg)
	if err != nil {
		return nil, err
	}
	return &cfg, nil
}

type UserCache struct {
	client redis.UniversalClient
	bulk   *bulkDel
	ttl    time.Duration
	cfg    *Config
}

func NewUserCache(cfg *Config, client redis.UniversalClient) *UserCache {
	return &UserCache{
		client: client,
		bulk:   newBulkDel(cfg, client),
		ttl:    cfg.TTL,
		cfg:    cfg,
	}
}

func (c *UserCache) AddByID(ctx context.Context, user *models.User) error {
	msg := protoutils.FromDTO(user)
	bytes, err := proto.Marshal(msg)
	if err != nil {
		return err
	}

	key := getUserKeyID(user.ID)

	err = c.client.
		Set(ctx, key, bytes, c.ttl).
		Err()
	if err != nil {
		return err
	}

	return nil
}

func (c *UserCache) AddByTgID(ctx context.Context, user *models.User) error {
	msg := protoutils.FromDTO(user)
	bytes, err := proto.Marshal(msg)
	if err != nil {
		return err
	}

	key := getUserKeyTgID(user.TgID)

	err = c.client.
		Set(ctx, key, bytes, c.ttl).
		Err()
	if err != nil {
		return err
	}

	return nil
}

func (c *UserCache) AddID(ctx context.Context, id int64, val uuid.UUID) error {
	key := getKeyTgID(id)

	err := c.client.
		Set(ctx, key, val.String(), c.ttl).
		Err()
	if err != nil {
		return err
	}

	return nil
}

func (c *UserCache) AddTgID(ctx context.Context, id uuid.UUID, val int64) error {
	key := getKeyID(id)

	err := c.client.
		Set(ctx, key, val, c.ttl).
		Err()
	if err != nil {
		return err
	}

	return nil
}

func (c *UserCache) getUser(ctx context.Context, key string) (*models.User, error) {
	bytes, err := c.client.
		Get(ctx, key).
		Bytes()
	if err, fail := wrapErr(err); fail {
		return nil, fmt.Errorf("failed to get user: %w", err)
	}

	msg := pb.User{}
	err = proto.Unmarshal(bytes, &msg)
	if err != nil {
		return nil, fmt.Errorf("failed to unmarshal user: %w", err)
	}

	user := protoutils.ToDTO(&msg)
	return user, nil
}

func (c *UserCache) GetByID(ctx context.Context, id uuid.UUID) (*models.User, error) {
	key := getUserKeyID(id)
	return c.getUser(ctx, key)
}

func (c *UserCache) GetByTgID(ctx context.Context, id int64) (*models.User, error) {
	key := getUserKeyTgID(id)
	return c.getUser(ctx, key)
}

func (c *UserCache) GetID(ctx context.Context, id int64) (uuid.UUID, error) {
	key := getKeyTgID(id)

	var uidStr string
	err := c.client.
		Get(ctx, key).
		Scan(&uidStr)
	if err, fail := wrapErr(err); fail {
		return uuid.Nil, fmt.Errorf("failed to get user id: %w", err)
	}

	return uuid.Parse(uidStr)
}

func (c *UserCache) GetTgID(ctx context.Context, id uuid.UUID) (int64, error) {
	key := getKeyID(id)

	var tgID int64
	err := c.client.
		Get(ctx, key).
		Scan(&tgID)
	if err, fail := wrapErr(err); fail {
		return 0, fmt.Errorf("failed to get user id: %w", err)
	}

	return tgID, nil
}

func (c *UserCache) InvalidateUserID(ctx context.Context, id uuid.UUID) error {
	key := getKeyID(id)
	return c.bulk.Del(ctx, key)
}

func (c *UserCache) InvalidateUserByID(ctx context.Context, id uuid.UUID) error {
	key := getUserKeyID(id)
	return c.bulk.Del(ctx, key)
}

func (c *UserCache) InvalidateUserTgID(ctx context.Context, id int64) error {
	key := getKeyTgID(id)
	return c.bulk.Del(ctx, key)
}

func (c *UserCache) InvalidateUserByTgID(ctx context.Context, id int64) error {
	key := getUserKeyTgID(id)
	return c.bulk.Del(ctx, key)
}
