package protoutils

import (
	"github.com/echo/tgdb/internal/domain/models"
	pb "github.com/echo/tgdb/pkg/proto"
	"github.com/google/uuid"
	"time"
)

func ToDTO(user *pb.User) *models.User {
	if user == nil {
		return nil
	}

	var username string
	if user.TgUsername != nil {
		username = *user.TgUsername
	}

	return &models.User{
		ID:         uuid.MustParse(user.Id),
		TgID:       user.TgId,
		TgUsername: username,
		Language:   user.Lang,
		CreatedAt:  time.Unix(user.CreatedAt, 0),
	}
}

func FromDTO(user *models.User) *pb.User {
	if user == nil {
		return nil
	}

	var username *string
	if user.TgUsername != "" {
		username = &user.TgUsername
	}

	return &pb.User{
		Id:         user.ID.String(),
		TgId:       user.TgID,
		TgUsername: username,
		Lang:       user.Language,
		CreatedAt:  user.CreatedAt.Unix(),
	}
}
