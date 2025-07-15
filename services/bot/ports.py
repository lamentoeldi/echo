from abc import ABC, abstractmethod
from uuid import UUID
from io import BytesIO
from typing import Callable, Union

from typing_extensions import overload

from classes import (
    AudioRawMessage,
    User,
    UserUpdate,
    KeyboardMarkup
)


class BotAPIPort(ABC):
    @abstractmethod
    async def send_text(self, user_id: int, text: str, keyboard: KeyboardMarkup = None):
        """
        Sends a text message to the user.
        :param user_id:
        :param text:
        :param keyboard:
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
    async def publish_audio(self, md: AudioRawMessage):
        """
        Publishes an audio message metadata to message bus
        :param md:
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

    @abstractmethod
    async def get_user(self, key: Union[int, UUID]) -> User:
        """
        Gets a user from the repository by tg id or internal id
        :param key: tg_id or UUID
        :return:
        """
        pass

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

    @abstractmethod
    async def update_user(self, key: Union[int, UUID], update: UserUpdate):
        """
        Updates a user from the repository by tg id or internal id
        :param key: tg_id or UUID
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

    @abstractmethod
    async def get_user_id(self, key: Union[int, UUID]) -> Union[UUID, int]:
        """
        Gets either user UUID by Telegram ID, or Telegram ID by user UUID.

        :param key: Telegram user ID (int) or internal user UUID
        :return: UUID if input is int, or int if input is UUID
        """


class LocalePort(ABC):
    @abstractmethod
    def __call__(self, locale: str) -> Callable[[str], str]:
        """
        Returns func which returns needed locale
        """
        pass
