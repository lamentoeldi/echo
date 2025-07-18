from typing import Union, overload
from uuid import UUID

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings
from sqlalchemy import create_engine
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, async_sessionmaker
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError

from services.bot.domain.models import User, UserUpdate
from services.bot.domain.ports.output import RepositoryPort
from services.bot.infrastructure.db.schema import Base, Users


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
            try:
                session.add(obj)
                await session.commit()
            except IntegrityError as err:  # ignore 23505 pg error cause ON CONFLICT cannot be used via alchemy
                if err.code != "gkpj":
                    raise err

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
