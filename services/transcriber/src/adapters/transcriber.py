from io import BytesIO
from tempfile import NamedTemporaryFile

from src.domain.ports.output import AudioTranscriberPort

from whisper import load_model
from pydantic import Field
from pydantic_settings import BaseSettings


class WhisperConfig(BaseSettings):
    model: str = Field(default="base")


class WhisperAudioTranscriberAdapter(AudioTranscriberPort):
    def __init__(self, cfg: WhisperConfig):
        self.cfg = cfg
        self.model = load_model(self.cfg.model)

    async def transcribe_audio(self, audio: BytesIO) -> str:
        audio.seek(0)

        with NamedTemporaryFile(mode="wb", suffix=".wav") as f:
            f.write(audio.read())
            f.flush()

            res = self.model.transcribe(audio=f.name)
            return res["text"]
