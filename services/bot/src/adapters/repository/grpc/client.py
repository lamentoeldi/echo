from typing import Union, overload
from uuid import UUID

from domain.models import UserUpdate, User
from domain.ports.output import RepositoryPort
from . import tgdb_pb2 as pb
from . import tgdb_pb2_grpc as pb2

import grpc
from pydantic import Field
from pydantic_settings import BaseSettings


class TgDBRepoConfig(BaseSettings):
    host: str = Field(default="tgdb")
    port: int = Field(default=50051)


class TgDBRepo(RepositoryPort):
    def __init__(self, channel: grpc.aio.Channel):
        self._channel = channel
        self._stub = pb2.TgDBStub(self._channel)

    async def add_user(self, user: User):
        req = pb.CreateUserRequest(
            user=pb.User(
                id=str(user.id),
                tg_id=user.tg_id,
                tg_username=user.tg_username,
                lang=user.language
            )
        )
        await self._stub.CreateUser(req)

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

    async def _get_user_by_tg_id(self, tg_id: int) -> User:
        req = pb.GetUserByTgIDRequest(tg_id=tg_id)
        res = await self._stub.GetUserByTgID(req)
        user = res.user

        return User(
            id=user.id,
            tg_id=tg_id,
            tg_username=user.tg_username,
            language=user.lang
        )

    async def _get_user_by_id(self, id: UUID) -> User:
        req = pb.GetUserByIDRequest(id=str(id))
        res = await self._stub.GetUserByID(req)
        user = res.user

        return User(
            id=id,
            tg_id=user.tg_id,
            tg_username=user.tg_username,
            language=user.lang
        )

    async def get_user(self, key: Union[int, UUID]) -> User:
        if isinstance(key, int):
            return await self._get_user_by_tg_id(key)
        elif isinstance(key, UUID):
            return await self._get_user_by_id(key)
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

    async def _update_user_by_tg_id(self, tg_id: int, update: UserUpdate):
        req = pb.UpdateUserByTgIDRequest(
            tg_id=tg_id,
            update=pb.UserUpdate(
                tg_username=update.tg_username,
                lang=update.language
            ),
        )
        await self._stub.UpdateUserByTgID(req)

    async def _update_user_by_id(self, id: UUID, update: UserUpdate):
        req = pb.UpdateUserByIDRequest(
            id=str(id),
            update=pb.UserUpdate(
                tg_username=update.tg_username,
                lang=update.language
            ),
        )
        await self._stub.UpdateUserByID(req)

    async def update_user(self, key: Union[int, UUID], update: UserUpdate):
        if isinstance(key, int):
            return await self._update_user_by_tg_id(key, update)
        elif isinstance(key, UUID):
            return await self._update_user_by_id(key, update)
        else:
            raise TypeError(f"Unsupported key type: {type(key)}")

    async def delete_user(self, tg_id: int):
        req = pb.DeleteUserByTgIDRequest(tg_id=tg_id)
        await self._stub.DeleteUserByTgID(req)

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
        req = pb.GetUserIDRequest(tg_id=tg_id)
        res = await self._stub.GetUserID(req)
        return res.id

    async def _get_tg_id_by_id(self, id: UUID) -> int:
        req = pb.GetUserTgIDRequest(id=str(id))
        res = await self._stub.GetUserTgID(req)
        return res.tg_id

    async def get_user_id(self, key: Union[int, UUID]) -> Union[UUID, int]:
        if isinstance(key, int):
            return await self._get_user_id_by_tg_id(key)
        elif isinstance(key, UUID):
            return await self._get_tg_id_by_id(key)
        else:
            raise TypeError(f"Unsupported key type: {type(key)}")
