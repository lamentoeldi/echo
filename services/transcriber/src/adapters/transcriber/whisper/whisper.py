import asyncio
from io import BytesIO
from tempfile import NamedTemporaryFile

from src.domain.ports.output import AudioTranscriberPort
from src.domain.models import TranscribedAudio

from whisper import load_model
from pydantic import Field
from pydantic_settings import BaseSettings


class WhisperConfig(BaseSettings):
    whisper_model: str = Field(default="base")
    whisper_max_workers: int = Field(default=1)


class WhisperAudioTranscriberAdapter(AudioTranscriberPort):
    def __init__(self, cfg: WhisperConfig):
        self._cfg = cfg
        self._model = load_model(self._cfg.whisper_model)
        self._sem = asyncio.Semaphore(self._cfg.whisper_max_workers)

    async def transcribe_audio(self, audio: BytesIO) -> str:
        audio.seek(0)

        with NamedTemporaryFile(mode="wb", suffix=".wav") as f:
            f.write(audio.read())
            f.flush()

            async with self._sem:
                loop = asyncio.get_event_loop()
                res = await loop.run_in_executor(None, self._model.transcribe, f.name)

            return TranscribedAudio(
                transcription=res["text"]
            )
