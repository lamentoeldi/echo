from abc import ABC, abstractmethod
from io import BytesIO

from src.domain.models import AudioPreprocessedMessage


class StoragePort(ABC):
    @abstractmethod
    async def upload_audio(self, filename: str, audio: BytesIO):
        """
        Uploads an audio file to storage
        :param filename:
        :param audio:
        :return:
        """

    @abstractmethod
    async def download_audio(self, filename: str) -> BytesIO:
        """
        Downloads an audio file from storage
        :param filename:
        """


class MessageBusPort(ABC):
    @abstractmethod
    async def publish_md(self, md: AudioPreprocessedMessage):
        """
        Publishes an audio message metadata to message bus
        :param md:
        :return:
        """
