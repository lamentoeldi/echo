from typing import Union, overload
from uuid import UUID

import asyncpg

from src.domain.models import UserUpdate, User
from src.infrastructure.pgconfig import PostgresConfig
from src.domain.ports.output import RepositoryPort


class PostgresRepo(RepositoryPort):
    def __init__(self, config: PostgresConfig):
        self._cfg = config
        self._timeout = config.pg_timeout
        self._pool = asyncpg.create_pool(
            dsn=self._cfg.postgres_dsn,
            min_size=self._cfg.pg_pool_min_size,
            max_size=self._cfg.pg_pool_max_size,
        )

    async def add_user(self, user: User):
        query = "INSERT INTO users (id, tg_id, tg_username, lang) VALUES ($1, $2, $3, $4)"
        await self._pool.execute(
            user.id, user.tg_id, user.tg_username, user.language,
            query=query,
            timeout=self._timeout,
        )

    @overload
    async def get_user(self, tg_id: int) -> User:
        """
        Gets a user from the repository by tg id
        :param tg_id:
        :return:
        """
        pass

    @overload
    async def get_user(self, user_id: UUID) -> User:
        """
        Gets a user from the repository by id
        :param user_id:
        :return:
        """
        pass

    async def _get_user_by_id(self, id: UUID) -> User:
        query = "SELECT tg_id, tg_username, lang FROM users WHERE id = $1"
        row = await self._pool.fetchrow(
            id,
            query=query,
            timeout=self._timeout,
        )
        return User(
            id=id,
            tg_id=row.tg_id,
            tg_username=row.tg_username,
            language=row.lang,
        )

    async def _get_user_by_tg_id(self, tg_id: int) -> User:
        query = "SELECT id, tg_username, lang FROM users WHERE id = $1"
        row = await self._pool.fetchrow(
            id,
            query=query,
            timeout=self._timeout,
        )
        return User(
            id=UUID(row.id),
            tg_id=tg_id,
            tg_username=row.tg_username,
            language=row.lang,
        )

    async def get_user(self, key: Union[int, UUID]) -> User:
        if isinstance(key, UUID):
            return await self._get_user_by_id(key)
        elif isinstance(key, int):
            return await self._get_user_by_tg_id(key)
        else:
            raise TypeError(f"Unsupported key type: {type(key)}")

    @overload
    async def update_user(self, tg_id: int, update: UserUpdate):
        """
        Updates a user from the repository by tg id
        :param tg_id:
        :param update:
        :return:
        """
        pass

    @overload
    async def update_user(self, user_id: UUID, update: UserUpdate):
        """
        Updates a user from the repository by tg id
        :param user_id:
        :param update:
        :return:
        """
        pass

    async def _update_user_by_id(self, id: UUID, upd: UserUpdate):
        idx = 1
        query = "UPDATE users SET "
        upd_strings: list[str] = []
        values: list = []

        if upd.tg_username is not None:
            upd_strings.append(f"tg_username = ${idx}")
            values.append(upd.tg_username)
            idx += 1
        if upd.language is not None:
            upd_strings.append(f"language = ${idx}")
            values.append(upd.language)
            idx += 1

        if not upd_strings:
            return

        query += ", ".join(upd_strings)
        query += f" WHERE id = ${idx}"
        values.append(id)

        await self._pool.execute(
            *values,
            query=query,
            timeout=self._timeout,
        )

    async def _update_user_by_tg_id(self, tg_id: int, upd: UserUpdate):
        idx = 1
        query = "UPDATE users SET "
        upd_strings: list[str] = []
        values: list = []

        if upd.tg_username is not None:
            upd_strings.append(f"tg_username = ${idx}")
            values.append(upd.tg_username)
            idx += 1
        if upd.language is not None:
            upd_strings.append(f"language = ${idx}")
            values.append(upd.language)
            idx += 1

        if not upd_strings:
            return

        query += ", ".join(upd_strings)
        query += f" WHERE tg_id = ${idx}"
        values.append(tg_id)

        await self._pool.execute(
            *values,
            query=query,
            timeout=self._timeout,
        )

    async def update_user(self, key: Union[int, UUID], update: UserUpdate):
        if isinstance(key, UUID):
            await self._update_user_by_id(key, update)
        elif isinstance(key, int):
            await self._update_user_by_tg_id(key, update)
        else:
            raise TypeError(f"Unsupported key type: {type(key)}")

    async def delete_user(self, tg_id: int):
        query = "DELETE FROM users WHERE tg_id = $1"
        await self._pool.execute(
            tg_id,
            query=query,
            timeout=self._timeout,
        )

    @overload
    async def get_user_id(self, tg_id: int) -> UUID:
        """
        Gets user UUID from the repository by Telegram ID.

        :param tg_id: Telegram user ID
        :return: Internal user UUID
        """

    @overload
    async def get_user_id(self, user_id: UUID) -> int:
        """
        Gets Telegram ID from the repository by internal user UUID.

        :param user_id: Internal user UUID
        :return: Telegram user ID
        """

    async def _get_user_id_by_tg_id(self, tg_id: int) -> UUID:
        query = "SELECT id FROM users WHERE tg_id = $1"
        user_id = await self._pool.fetchval(
            tg_id,
            query=query,
            timeout=self._timeout,
        )
        return UUID(user_id)

    async def _get_tg_id_by_user_id(self, user_id: UUID) -> int:
        query = "SELECT tg_id FROM users WHERE id = $1"
        tg_id = await self._pool.fetchval(
            user_id,
            query=query,
            timeout=self._timeout,
        )
        return int(tg_id)

    async def get_user_id(self, key: Union[int, UUID]) -> Union[UUID, int]:
        if isinstance(key, int):
            return await self._get_user_id_by_tg_id(key)
        elif isinstance(key, UUID):
            return await self._get_tg_id_by_user_id(key)
        else:
            raise TypeError(f"Unsupported key type: {type(key)}")
