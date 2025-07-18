from domain.models import User

from sqlalchemy import Column, func
from sqlalchemy.dialects.postgresql import UUID, BIGINT, VARCHAR, TIMESTAMP
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs


class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True


class Users(Base):
    __tablename__ = "users"
    id = Column(UUID, primary_key=True, nullable=False, unique=True)
    tg_id = Column(BIGINT, nullable=False, unique=True)
    tg_username = Column(VARCHAR(255))
    lang = Column(VARCHAR(3), default="ru")
    created_at = Column(TIMESTAMP, nullable=False, default=func.now())

    def to_user(self) -> User:
        return User(
            id=self.id,
            tg_id=self.tg_id,
            tg_username=self.tg_username,
            language=self.lang,
        )

    @staticmethod
    def from_user(user: User) -> "Users":
        return Users(
            id=user.id,
            tg_id=user.tg_id,
            tg_username=user.tg_username,
            lang=user.language,
        )
