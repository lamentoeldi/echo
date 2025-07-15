from abc import ABC, abstractmethod
from uuid import UUID
from io import BytesIO

from typing_extensions import overload

from classes import AudioRawMessage, User, UserUpdate


class BotAPIPort(ABC):
    @abstractmethod
    async def send_text(self, user_id: int, text: str):
        """
        Sends a text message to the user.
        :param user_id:
        :param text:
        :return:
        """
        pass


class StoragePort(ABC):
    @abstractmethod
    async def upload_audio(self, filename: str, audio: BytesIO):
        """
        Uploads an audio file to storage
        :param filename:
        :param audio:
        :return:
        """
        pass


class MessageBusPort(ABC):
    @abstractmethod
    async def publish_audio(self, audio: AudioRawMessage):
        """
        Publishes an audio message metadata to message bus
        :param audio:
        :return:
        """
        pass


class RepositoryPort(ABC):
    @abstractmethod
    async def add_user(self, user: User):
        """
        Adds a user to the repository
        :param user:
        :return:
        """
        pass

    @abstractmethod
    @overload
    async def get_user(self, tg_id: int) -> User:
        """
        Gets a user from the repository by tg id
        :param tg_id:
        :return:
        """
        pass

    @abstractmethod
    async def get_user(self, user_id: UUID) -> User:
        """
        Gets a user from the repository by id
        :param user_id:
        :return:
        """
        pass

    @abstractmethod
    @overload
    async def update_user(self, tg_id: int, update: UserUpdate):
        """
        Updates a user from the repository by tg id
        :param tg_id:
        :param update:
        :return:
        """
        pass

    @abstractmethod
    async def update_user(self, user_id: UUID, update: UserUpdate):
        """
        Updates a user from the repository by tg id
        :param user_id:
        :param update:
        :return:
        """
        pass

    @abstractmethod
    async def delete_user(self, tg_id: int) -> User:
        """
        Deletes a user from the repository by tg id
        :param tg_id:
        :return:
        """
        pass

    @abstractmethod
    @overload
    async def get_user_id(self, tg_id: int) -> UUID:
        """
        Gets user uuid from the repository by tg id
        :param tg_id:
        :return:
        """
        pass

    @abstractmethod
    async def get_user_id(self, user_id: UUID) -> int:
        """
        Gets user tg id from the repository by id
        :param user_id:
        :return:
        """
        pass
