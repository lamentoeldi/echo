from uuid import UUID
from typing import Optional

from pydantic import BaseModel, Field


class ProcessingError(BaseModel):
    code: int = Field()
    message: str = Field()


class MessageMeta(BaseModel):
    status: str = Field()
    error: Optional[ProcessingError] = None


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


class AudioRawMessage(BaseModel):
    """
    Represents an AudioRaw message
    """
    meta: MessageMeta = Field()
    content: AudioRaw = Field()


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
