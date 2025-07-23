from abc import ABC, abstractmethod

from src.domain.models import AudioRaw


class AbstractPreprocessUseCase(ABC):
    @abstractmethod
    async def preprocess_audio(self, md: AudioRaw):
        """
        Performs audio data preprocessing.
        """
