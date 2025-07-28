package models

import (
	"github.com/google/uuid"
	"time"
)

type User struct {
	ID         uuid.UUID `json:"id" bson:"id"`
	TgID       int64     `json:"tg_id" bson:"tg_id"`
	TgUsername string    `json:"tg_username" bson:"tg_username"`
	Language   string    `json:"lang" bson:"lang"`
	CreatedAt  time.Time `json:"created_at" bson:"created_at"`
}

type UserUpdate struct {
	TgUsername string `json:"tg_username" bson:"tg_username"`
	Language   string `json:"lang" bson:"lang"`
}
