from abc import ABC, abstractmethod
from io import BytesIO

from src.domain.models import AudioTranscribedMessage, TranscribedAudio


class StoragePort(ABC):
    @abstractmethod
    async def download_audio(self, filename: str) -> BytesIO:
        """
        Downloads an audio file from storage
        :param filename:
        """

    @abstractmethod
    async def delete_audio(self, filename: str):
        """
        Deletes an audio file from storage
        :param filename:
        :return:
        """


class MessageBusPort(ABC):
    @abstractmethod
    async def publish_md(self, md: AudioTranscribedMessage):
        """
        Publishes an audio message metadata to message bus
        :param md:
        :return:
        """


class AudioTranscriberPort(ABC):
    @abstractmethod
    async def transcribe_audio(self, audio: BytesIO) -> TranscribedAudio:
        """
        Transcribes an audio file
        :param audio:
        :return:
        """
