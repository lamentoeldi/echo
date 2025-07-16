import io
import time
from uuid import UUID

from ..application.usecases import AbstractCore
from ..domain.models import (
    AudioRawMessage,
    User,
    MessageMeta,
    AudioRaw
)

from uuid6 import uuid7
from pydub import AudioSegment


class Core(AbstractCore):
    def create_user(self, tg_id: int, tg_username: str, lang: str) -> User:
        user_id = uuid7()

        user = User(
            id=user_id,
            tg_id=tg_id,
            tg_username=tg_username,
            language=lang,
        )

        return user

    def create_audio_md(self, user_id: UUID, vm: io.BytesIO) -> AudioRawMessage:
        vm.seek(0)

        md_id = uuid7()

        audio = AudioSegment.from_ogg(vm)

        duration_ms = round(audio.duration_seconds) * 1000
        size = vm.getbuffer().nbytes

        md = AudioRawMessage(
            meta=MessageMeta(
                status="ok"
            ),
            content=AudioRaw(
                id=md_id,
                user_id=user_id,
                duration=duration_ms,
                size=size,
                format="ogg",
                sample_rate=audio.frame_rate,
                channels=audio.channels,
                source="tg",
                timestamp=time.time_ns()
            )
        )

        return md

    def create_audio_transcription(self, locale_msg: str, transcription: str) -> str:
        return f'{locale_msg}\n\n{transcription}'

    def create_error_text(self, locale_msg: str, error: str) -> str:
        return f'{locale_msg}\n\n{error}'
