from uuid import UUID
from typing import Optional

from pydantic import BaseModel, Field


class ProcessingError(BaseModel):
    code: int = Field()
    message: str = Field()


class MessageMeta(BaseModel):
    status: str = Field()
    error: Optional[ProcessingError] = None


class AudioPreprocessed(BaseModel):
    id: UUID = Field()
    user_id: UUID = Field()
    duration: int = Field()
    size: int = Field()
    channels: int = Field()
    source: str = Field()
    timestamp: int = Field()


class AudioPreprocessedMessage(BaseModel):
    """
    Represents an AudioPreprocessed message
    """
    meta: MessageMeta = Field()
    content: AudioPreprocessed = Field()


class AudioTranscribed(BaseModel):
    id: UUID = Field()
    user_id: UUID = Field()
    transcription: str = Field()
    timestamp: int = Field()


class AudioTranscribedMessage(BaseModel):
    """
    Represents an AudioTranscribedTg message
    """
    meta: MessageMeta = Field()
    content: AudioTranscribed = Field()
    source: str = Field(exclude=True)


class TranscribedAudio(BaseModel):
    transcription: str = Field()
