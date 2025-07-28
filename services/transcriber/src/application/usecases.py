from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.models import (
    AudioPreprocessedMessage,
    AudioTranscribedMessage,
)
from src.domain.ports.input import AbstractTranscribeAudioUseCase
from src.domain.ports.output import (
    StoragePort,
    MessageBusPort,
    AudioTranscriberPort
)


class AbstractCore(ABC):
    @abstractmethod
    def make_transcription_message(
        self,
        msg_id: UUID,
        user_id: UUID,
        transcription: str,
        dest: str,
    ) -> AudioTranscribedMessage:
        """
        Makes a transcription message
        :param msg_id:
        :param user_id:
        :param transcription:
        :param dest:
        """


class TranscribeAudioUseCase(AbstractTranscribeAudioUseCase):
    def __init__(
        self,
        core: AbstractCore,
        storage: StoragePort,
        transcriber: AudioTranscriberPort,
        broker: MessageBusPort
    ):
        self._core = core
        self._storage = storage
        self._transcriber = transcriber
        self._broker = broker

    async def transcribe_audio(self, md: AudioPreprocessedMessage):
        filename = f"{md.content.id}.wav"
        audio = await self._storage.download_audio(filename)

        transcription = await self._transcriber.transcribe_audio(audio)

        msg = self._core.make_transcription_message(
            msg_id=md.content.id,
            user_id=md.content.user_id,
            transcription=transcription.transcription,
            dest=md.content.source,
        )

        await self._broker.publish_md(msg)
        await self._storage.delete_audio(filename)
