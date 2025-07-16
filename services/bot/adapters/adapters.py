from io import BytesIO
from json import loads
from typing import Callable, Dict, Optional, Union, overload
from uuid import UUID

from services.bot.domain.ports.output import (
    LocalePort,
    KeyboardProviderPort,
    StoragePort,
    RepositoryPort
)
from services.bot.domain.models import KeyboardMarkup, KeyboardButton, User, UserUpdate
from services.bot.infrastructure.db.schema import Base, Users

from aioboto3 import Session
from pydantic import Field, computed_field
from pydantic_settings import BaseSettings
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, async_sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.future import select
from sqlalchemy import delete


class JSONLocaleProvider(LocalePort):
    locale: Dict[str, Dict[str, str]]

    def __init__(self, json: str):
        self.locale = loads(json)

    def __call__(self, locale: str) -> Callable[[str], str]:
        locale_dict = self.locale[locale]

        def locale_func(line: str) -> str:
            return locale_dict[line]

        return locale_func


class KeyboardProvider(KeyboardProviderPort):
    keyboards: dict

    def __init__(self, json: str):
        self.keyboards = loads(json)

    def get_settings_keyboard(self, lang: str) -> KeyboardMarkup:
        buttons: dict[str, str] = self.keyboards[lang]["kb_settings"]

        kb_buttons: list[KeyboardButton] = []

        for key, val in buttons.items():
            kb_buttons.append(
                KeyboardButton(text=val, callback_data=key)
            )

        return KeyboardMarkup(type="inline", buttons=[kb_buttons])

    def get_languages_keyboard(self) -> KeyboardMarkup:
        languages: list[str] = self.keyboards["kb_languages"]

        kb_buttons: list[KeyboardButton] = []

        for lang in languages:
            kb_buttons.append(
                KeyboardButton(text=lang)
            )

        return KeyboardMarkup(type="reply", buttons=[kb_buttons])


class S3Config(BaseSettings):
    s3_access_key_id: str = Field()
    s3_secret_access_key: str = Field()
    s3_url: str = Field()

    s3_region: Optional[str] = Field(default="us-east-1")
    s3_session_key: Optional[str] = Field(default=None)


class S3StoragePort(StoragePort):
    config: S3Config
    bucket: str = "audio-raw"

    def __init__(self, config: S3Config):
        self.config = config

    async def upload_audio(self, filename: str, audio: BytesIO):
        sess = Session(
            aws_access_key_id=self.config.s3_access_key_id,
            aws_secret_access_key=self.config.s3_secret_access_key,
            aws_session_token=self.config.s3_session_key,
            region_name=self.config.s3_region,
        )

        async with sess.client("s3", endpoint_url=self.config.s3_url) as s3:
            await s3.upload_fileobj(audio, self.bucket, filename)


class PostgresConfig(BaseSettings):
    pg_host: str = Field()
    pg_port: int = Field()
    pg_user: str = Field()
    pg_password: str = Field()
    pg_db: str = Field()

    @computed_field
    @property
    def dsn(self) -> str:
        return f"postgres://{self.pg_user}:{self.pg_password}@{self.pg_host}:{self.pg_port}/{self.pg_db}"

    @computed_field
    @property
    def orm_async_dsn(self) -> str:
        return f"postgresql+asyncpg://{self.pg_user}:{self.pg_password}@{self.pg_host}:{self.pg_port}/{self.pg_db}"

    @computed_field
    @property
    def orm_sync_dsn(self) -> str:
        return f"postgresql://{self.pg_user}:{self.pg_password}@{self.pg_host}:{self.pg_port}/{self.pg_db}"


class PostgresORMRepository(RepositoryPort):
    config: PostgresConfig
    engine: AsyncEngine
    session_maker: async_sessionmaker

    def __init__(self, config: PostgresConfig):
        self.config = config

        self.run_migrations()

        self.engine = create_async_engine(self.config.orm_async_dsn)
        self.session_maker = async_sessionmaker(self.engine, expire_on_commit=False)

    def run_migrations(self):
        engine = create_engine(self.config.orm_sync_dsn)
        try:
            Base.metadata.create_all(engine)
        finally:
            engine.dispose()

    async def add_user(self, user: User):
        obj = Users.from_user(user)

        async with self.session_maker() as session:
            session.add(obj)
            await session.commit()

    @overload
    async def get_user(self, tg_id: int) -> User:
        """
        Gets a user from the repository by tg id
        :param tg_id:
        :return:
        """

    @overload
    async def get_user(self, user_id: UUID) -> User:
        """
        Gets a user from the repository by id
        :param user_id:
        :return:
        """

    async def get_user(self, key: Union[int, UUID]) -> User:
        if isinstance(key, int):
            query = (
                select(Users)
                .where(Users.tg_id == key)
            )
            async with self.session_maker() as session:
                res = await session.execute(query)
                return res.scalar().to_user()
        elif isinstance(key, UUID):
            query = (
                select(Users)
                .where(Users.id == key)
            )
            async with self.session_maker() as session:
                res = await session.execute(query)
                return res.scalar().to_user()
        else:
            raise TypeError("Invalid key type for get_user")

    @overload
    async def update_user(self, tg_id: int, update: UserUpdate):
        """
        Updates a user from the repository by tg id
        :param tg_id:
        :param update:
        :return:
        """

    @overload
    async def update_user(self, user_id: UUID, update: UserUpdate):
        """
        Updates a user from the repository by tg id
        :param user_id:
        :param update:
        :return:
        """

    async def update_user(self, key: Union[int, UUID], update: UserUpdate):
        if isinstance(key, int):
            query = (
                select(Users)
                .where(Users.tg_id == key)
            )
            async with self.session_maker() as session:
                res = await session.execute(query)
                user: Users = res.scalar()
                if update.tg_username is not None:
                    user.tg_username = update.tg_username
                if update.language is not None:
                    user.language = update.language
                await session.commit()
        elif isinstance(key, UUID):
            query = (
                select(Users)
                .where(Users.id == key)
            )
            async with self.session_maker() as session:
                res = await session.execute(query)
                user: Users = res.scalar()
                if update.tg_username is not None:
                    user.tg_username = update.tg_username
                if update.language is not None:
                    user.language = update.language
                await session.commit()
        else:
            raise TypeError("Invalid key type for get_user")

    async def delete_user(self, tg_id: int):
        query = (
            delete(Users)
            .where(Users.tg_id == tg_id)
        )
        async with self.session_maker() as session:
            await session.execute(query)
            await session.commit()

    @overload
    async def get_user_id(self, tg_id: int) -> UUID:
        """
        Gets user UUID from the repository by Telegram ID.

        :param tg_id: Telegram user ID
        :return: Internal user UUID
        """
        ...

    @overload
    async def get_user_id(self, user_id: UUID) -> int:
        """
        Gets Telegram ID from the repository by internal user UUID.

        :param user_id: Internal user UUID
        :return: Telegram user ID
        """
        ...

    async def get_user_id(self, key: Union[int, UUID]) -> Union[UUID, int]:
        user = await self.get_user(key)
        if isinstance(key, int):
            return user.id
        elif isinstance(key, UUID):
            return user.tg_id
        else:
            raise TypeError("Invalid key type for get_user_id")
