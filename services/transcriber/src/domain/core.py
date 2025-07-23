from uuid import UUID
from time import time_ns

from domain.models import (
    MessageMeta,
    AudioTranscribed,
    AudioTranscribedMessage,
)
from src.application.usecases import AbstractCore


class Core(AbstractCore):
    def make_transcription_message(
        self,
        msg_id: UUID,
        user_id: UUID,
        transcription: str,
        dest: str
    ) -> AudioTranscribedMessage:
        meta = MessageMeta(
            status="ok"
        )
        content = AudioTranscribed(
            id=msg_id,
            user_id=user_id,
            transcription=transcription,
            timestamp=time_ns(),
        )

        return AudioTranscribedMessage(
            content=content,
            meta=meta,
            source=dest
        )
