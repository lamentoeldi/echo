from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional, Literal, List


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
    content: AudioTranscribed = Field()


class User(BaseModel):
    """
    Represents bot User
    """
    id: UUID = Field()
    tg_id: int = Field()
    tg_username: Optional[str] = Field()
    language: str = Field()


class UserUpdate(BaseModel):
    """
    Represents Updates for repository
    """
    tg_username: Optional[str] = None
    language: Optional[str] = None


class KeyboardButton(BaseModel):
    """
    Abstracts tg keyboard button
    """
    text: str = Field()
    callback_data: Optional[str] = None


class KeyboardMarkup(BaseModel):
    """
    Abstracts tg keyboard markup
    """
    type: Literal["inline", "reply"]
    buttons: List[List[KeyboardButton]]
