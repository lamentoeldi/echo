from abc import ABC, abstractmethod

from src.domain.models import AudioPreprocessedMessage


class AbstractTranscribeAudioUseCase(ABC):
    @abstractmethod
    async def transcribe_audio(self, md: AudioPreprocessedMessage):
        """
        Transcribes audio
        :param md:
        :return:
        """
