package grpc

import (
	"context"
	"fmt"
	"github.com/echo/tgdb/internal/domain/models"
	"github.com/echo/tgdb/internal/ports"
	e "github.com/echo/tgdb/pkg/errors"
	pb "github.com/echo/tgdb/pkg/proto"
	"github.com/echo/tgdb/pkg/protoutils"
	"github.com/google/uuid"
	"github.com/ilyakaznacheev/cleanenv"
	"go.uber.org/zap"
	"google.golang.org/grpc"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/status"
	"net"
)

const (
	msgInvalidUUID = "invalid user id"
)

type Config struct {
	Host string `env:"GRPC_HOST" env-default:"0.0.0.0"`
	Port int    `env:"GRPC_PORT" env-default:"50051"`
}

func NewConfig() (*Config, error) {
	cfg := Config{}
	err := cleanenv.ReadEnv(&cfg)
	if err != nil {
		return nil, err
	}

	return &cfg, nil
}

type Controller struct {
	log    *zap.Logger
	cfg    *Config
	server *grpc.Server
	app    ports.UseCasePort
	pb.UnimplementedTgDBServer
}

func New(cfg *Config, server *grpc.Server, log *zap.Logger, app ports.UseCasePort) (*Controller, error) {
	c := &Controller{
		cfg:    cfg,
		server: server,
		log:    log,
		app:    app,
	}

	pb.RegisterTgDBServer(server, c)

	return c, nil
}

func (c *Controller) CreateUser(ctx context.Context, req *pb.CreateUserRequest) (*pb.CreateUserResponse, error) {
	user := protoutils.ToDTO(req.User)
	err := c.app.CreateUser(ctx, user)
	if err != nil {
		return nil, e.New(err)
	}

	return &pb.CreateUserResponse{}, nil
}

func (c *Controller) GetUserByID(ctx context.Context, req *pb.GetUserByIDRequest) (*pb.GetUserByIDResponse, error) {
	uid, err := uuid.Parse(req.GetId())
	if err != nil {
		return nil, status.Error(codes.InvalidArgument, msgInvalidUUID)
	}

	user, err := c.app.GetUserByID(ctx, uid)
	if err != nil {
		return nil, e.New(err)
	}

	res := &pb.GetUserByIDResponse{
		User: protoutils.FromDTO(user),
	}

	return res, nil
}

func (c *Controller) GetUserByTgID(ctx context.Context, req *pb.GetUserByTgIDRequest) (*pb.GetUserByTgIDResponse, error) {
	user, err := c.app.GetUserByTgID(ctx, req.GetTgId())
	if err != nil {
		return nil, e.New(err)
	}

	res := &pb.GetUserByTgIDResponse{
		User: protoutils.FromDTO(user),
	}

	return res, nil
}

func (c *Controller) UpdateUserByID(ctx context.Context, req *pb.UpdateUserByIDRequest) (*pb.UpdateUserByIDResponse, error) {
	uid, err := uuid.Parse(req.GetId())
	if err != nil {
		return nil, status.Error(codes.InvalidArgument, msgInvalidUUID)
	}

	upd := &models.UserUpdate{
		TgUsername: req.GetUpdate().GetTgUsername(),
		Language:   req.GetUpdate().GetLang(),
	}

	err = c.app.UpdateUserByID(ctx, uid, upd)
	if err != nil {
		return nil, e.New(err)
	}

	return &pb.UpdateUserByIDResponse{}, nil
}

func (c *Controller) UpdateUserByTgID(ctx context.Context, req *pb.UpdateUserByTgIDRequest) (*pb.UpdateUserByTgIDResponse, error) {
	upd := &models.UserUpdate{
		TgUsername: req.GetUpdate().GetTgUsername(),
		Language:   req.GetUpdate().GetLang(),
	}

	err := c.app.UpdateUserByTgID(ctx, req.GetTgId(), upd)
	if err != nil {
		return nil, e.New(err)
	}

	return &pb.UpdateUserByTgIDResponse{}, nil
}

func (c *Controller) DeleteUserByID(ctx context.Context, req *pb.DeleteUserByIDRequest) (*pb.DeleteUserByIDResponse, error) {
	uid, err := uuid.Parse(req.GetId())
	if err != nil {
		return nil, status.Error(codes.InvalidArgument, msgInvalidUUID)
	}

	err = c.app.DeleteUserByID(ctx, uid)
	if err != nil {
		return nil, e.New(err)
	}

	return &pb.DeleteUserByIDResponse{}, nil
}

func (c *Controller) DeleteUserByTgID(ctx context.Context, req *pb.DeleteUserByTgIDRequest) (*pb.DeleteUserByTgIDResponse, error) {
	err := c.app.DeleteUserByTgID(ctx, req.GetTgId())
	if err != nil {
		return nil, e.New(err)
	}

	return &pb.DeleteUserByTgIDResponse{}, nil
}

func (c *Controller) GetUserID(ctx context.Context, req *pb.GetUserIDRequest) (*pb.GetUserIDResponse, error) {
	id, err := c.app.GetUserID(ctx, req.GetTgId())
	if err != nil {
		return nil, e.New(err)
	}

	res := &pb.GetUserIDResponse{
		Id: id.String(),
	}

	return res, nil
}

func (c *Controller) GetUserTgID(ctx context.Context, req *pb.GetUserTgIDRequest) (*pb.GetUserTgIDResponse, error) {
	uid, err := uuid.Parse(req.GetId())
	if err != nil {
		return nil, status.Error(codes.InvalidArgument, msgInvalidUUID)
	}

	id, err := c.app.GetUserTgID(ctx, uid)
	if err != nil {
		return nil, e.New(err)
	}

	res := &pb.GetUserTgIDResponse{
		TgId: id,
	}

	return res, nil
}

func (c *Controller) Run() {
	go func() {
		addr := fmt.Sprintf("%s:%d", c.cfg.Host, c.cfg.Port)
		c.log.Info(
			"starting gRPC server",
			zap.String("host", c.cfg.Host),
			zap.Int("port", c.cfg.Port),
		)
		l, err := net.Listen("tcp", addr)
		if err != nil {
			c.log.Fatal("failed to listen", zap.Error(err))
		}

		err = c.server.Serve(l)
		if err != nil {
			c.log.Fatal("failed to listen", zap.Error(err))
		}
	}()
}

func (c *Controller) Shutdown() {
	c.server.GracefulStop()
}
