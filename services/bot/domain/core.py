import io
import time
from uuid import UUID

from services.bot.application.usecases import AbstractCore
from services.bot.domain.models import (
    AudioRawMessage,
    User,
    MessageMeta,
    AudioRaw
)

import soundfile as sf
from uuid6 import uuid7


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

        data, samplerate = sf.read(vm)

        duration_ms = int(len(data) / samplerate * 1000)
        size = vm.getbuffer().nbytes

        channels = 1 if len(data.shape) == 1 else data.shape[1]

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
                sample_rate=samplerate,
                channels=channels,
                source="tg",
                timestamp=time.time_ns()
            )
        )

        return md

    def create_audio_transcription(self, locale_msg: str, transcription: str) -> str:
        return f'{locale_msg}\n\n{transcription}'

    def create_error_text(self, locale_msg: str, error: str) -> str:
        return f'{locale_msg}\n\n{error}'
