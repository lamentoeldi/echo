package grpc

import (
	"context"
	"fmt"
	"github.com/echo/tgdb/internal/domain/models"
	"github.com/echo/tgdb/internal/ports"
	pb "github.com/echo/tgdb/pkg/proto"
	"github.com/echo/tgdb/pkg/protoutils"
	"github.com/google/uuid"
	"go.uber.org/zap"
	"google.golang.org/grpc"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/status"
	"net"
)

type Config struct {
	Host string `env:"GRPC_HOST" envDefault:"0.0.0.0"`
	Port int    `env:"GRPC_PORT" envDefault:"50051"`
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

func (s *Controller) CreateUser(ctx context.Context, req *pb.CreateUserRequest) (*pb.CreateUserResponse, error) {
	user := protoutils.ToDTO(req.User)
	err := s.app.CreateUser(ctx, user)
	if err != nil {
		return nil, status.Error(codes.Internal, err.Error())
	}

	return &pb.CreateUserResponse{}, nil
}

func (s *Controller) GetUserByID(ctx context.Context, req *pb.GetUserByIDRequest) (*pb.GetUserByIDResponse, error) {
	uid, err := uuid.Parse(req.GetId())
	if err != nil {
		return nil, status.Error(codes.InvalidArgument, err.Error())
	}

	user, err := s.app.GetUserByID(ctx, uid)
	if err != nil {
		return nil, status.Error(codes.Internal, err.Error())
	}

	res := &pb.GetUserByIDResponse{
		User: protoutils.FromDTO(user),
	}

	return res, nil
}

func (s *Controller) GetUserByTgID(ctx context.Context, req *pb.GetUserByTgIDRequest) (*pb.GetUserByTgIDResponse, error) {
	user, err := s.app.GetUserByTgID(ctx, req.GetTgId())
	if err != nil {
		return nil, status.Error(codes.Internal, err.Error())
	}

	res := &pb.GetUserByTgIDResponse{
		User: protoutils.FromDTO(user),
	}

	return res, nil
}

func (s *Controller) UpdateUserByID(ctx context.Context, req *pb.UpdateUserByIDRequest) (*pb.UpdateUserByIDResponse, error) {
	uid, err := uuid.Parse(req.GetId())
	if err != nil {
		return nil, status.Error(codes.InvalidArgument, err.Error())
	}

	upd := &models.UserUpdate{
		TgUsername: req.GetUpdate().GetTgUsername(),
		Language:   req.GetUpdate().GetLang(),
	}

	err = s.app.UpdateUserByID(ctx, uid, upd)
	if err != nil {
		return nil, status.Error(codes.Internal, err.Error())
	}

	return &pb.UpdateUserByIDResponse{}, nil
}

func (s *Controller) UpdateUserByTgID(ctx context.Context, req *pb.UpdateUserByTgIDRequest) (*pb.UpdateUserByTgIDResponse, error) {
	upd := &models.UserUpdate{
		TgUsername: req.GetUpdate().GetTgUsername(),
		Language:   req.GetUpdate().GetLang(),
	}

	err := s.app.UpdateUserByTgID(ctx, req.GetTgId(), upd)
	if err != nil {
		return nil, status.Error(codes.Internal, err.Error())
	}

	return &pb.UpdateUserByTgIDResponse{}, nil
}

func (s *Controller) DeleteUserByID(ctx context.Context, req *pb.DeleteUserByIDRequest) (*pb.DeleteUserByIDResponse, error) {
	uid, err := uuid.Parse(req.GetId())
	if err != nil {
		return nil, status.Error(codes.InvalidArgument, err.Error())
	}

	err = s.app.DeleteUserByID(ctx, uid)
	if err != nil {
		return nil, status.Error(codes.Internal, err.Error())
	}

	return &pb.DeleteUserByIDResponse{}, nil
}

func (s *Controller) DeleteUserByTgID(ctx context.Context, req *pb.DeleteUserByTgIDRequest) (*pb.DeleteUserByTgIDResponse, error) {
	err := s.app.DeleteUserByTgID(ctx, req.GetTgId())
	if err != nil {
		return nil, status.Error(codes.Internal, err.Error())
	}

	return &pb.DeleteUserByTgIDResponse{}, nil
}

func (s *Controller) GetUserID(ctx context.Context, req *pb.GetUserIDRequest) (*pb.GetUserIDResponse, error) {
	id, err := s.app.GetUserID(ctx, req.GetTgId())
	if err != nil {
		return nil, status.Error(codes.Internal, err.Error())
	}

	res := &pb.GetUserIDResponse{
		Id: id.String(),
	}

	return res, nil
}

func (s *Controller) GetUserTgID(ctx context.Context, req *pb.GetUserTgIDRequest) (*pb.GetUserTgIDResponse, error) {
	uid, err := uuid.Parse(req.GetId())
	if err != nil {
		return nil, status.Error(codes.InvalidArgument, err.Error())
	}

	id, err := s.app.GetUserTgID(ctx, uid)
	if err != nil {
		return nil, status.Error(codes.Internal, err.Error())
	}

	res := &pb.GetUserTgIDResponse{
		TgId: id,
	}

	return res, nil
}

func (s *Controller) Run() {
	go func() {
		addr := fmt.Sprintf("%s:%d", s.cfg.Host, s.cfg.Port)
		l, err := net.Listen("tcp", addr)
		if err != nil {
			s.log.Fatal("failed to listen", zap.Error(err))
		}

		err = s.server.Serve(l)
		if err != nil {
			s.log.Fatal("failed to listen", zap.Error(err))
		}
	}()
}

func (s *Controller) Shutdown() {
	s.server.GracefulStop()
}
