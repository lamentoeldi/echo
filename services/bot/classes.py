from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional


class ProcessingError(BaseModel):
    code: int = Field()
    message: str = Field()


class MessageMeta(BaseModel):
    status: str = Field()
    error: ProcessingError = Field()


class AudioRaw(BaseModel):
    id: UUID = Field()
    user_id: UUID = Field()
    duration: int = Field()
    size: int = Field()
    format: str = Field()
    sample_rate: int = Field()
    channels: int = Field()
    source: str = Field()
    timestamp: int = Field()


class AudioTranscribed(BaseModel):
    id: UUID = Field()
    user_id: UUID = Field()
    transcription: str = Field()
    timestamp: int = Field()


class AudioRawMessage(BaseModel):
    """
    Represents an AudioRaw message
    """
    meta: MessageMeta = Field()
    content: AudioRaw = Field()


class AudioTranscribedMessage(BaseModel):
    """
    Represents an AudioTranscribedTg message
    """
    meta: MessageMeta = Field()
    content: AudioRawMessage = Field()


class User(BaseModel):
    id: UUID = Field()
    tg_id: int = Field()
    tg_username: str = Field()
    language: str = Field()


class UserUpdate(BaseModel):
    tg_username: Optional[str] = None
    language: Optional[str] = None
