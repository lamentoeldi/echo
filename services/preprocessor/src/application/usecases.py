from abc import ABC, abstractmethod
from io import BytesIO
from typing import Tuple

from src.domain.models import AudioRaw, AudioPreprocessed, AudioPreprocessedMessage, MessageMeta
from src.domain.ports.input import AbstractPreprocessUseCase
from src.domain.ports.output import StoragePort, MessageBusPort


class AbstractCore(ABC):
    @abstractmethod
    async def preprocess_audio(self, md: AudioRaw, audio: BytesIO) -> Tuple[AudioPreprocessed, BytesIO]:
        """
        Performs audio data preprocessing.
        """


class PreprocessUseCase(AbstractPreprocessUseCase):
    def __init__(
        self,
        core: AbstractCore,
        storage: StoragePort,
        broker: MessageBusPort,
    ):
        self.core = core
        self.storage = storage
        self.broker = broker

    async def preprocess_audio(self, md: AudioRaw):
        filename = f"{md.id}.{md.format}"
        stream = await self.storage.download_audio(filename=filename)

        out_md, out_stream = await self.core.preprocess_audio(md, stream)

        out_filename = f"{out_md.id}.wav"
        await self.storage.upload_audio(filename=out_filename, audio=out_stream)

        msg = AudioPreprocessedMessage(
            content=out_md,
            meta=MessageMeta(
                status="ok"
            )
        )

        await self.broker.publish_md(msg)
        await self.storage.delete_audio(filename=filename)
