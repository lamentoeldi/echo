from io import BytesIO
from json import loads
from typing import Callable, Dict, Optional

from services.bot.domain.ports.output import (
    LocalePort,
    KeyboardProviderPort,
    StoragePort
)
from services.bot.domain.models import KeyboardMarkup, KeyboardButton

from aioboto3 import Session
from pydantic import Field
from pydantic_settings import BaseSettings


class JSONLocaleProvider(LocalePort):
    locale: Dict[str, Dict[str, str]]

    def __init__(self, json: str):
        self.locale = loads(json)

    def __call__(self, locale: str) -> Callable[[str], str]:
        locale_dict = self.locale[locale]

        def locale_func(line: str) -> str:
            return locale_dict[line]

        return locale_func


class KeyboardProvider(KeyboardProviderPort):
    keyboards: dict

    def __init__(self, json: str):
        self.keyboards = loads(json)

    def get_settings_keyboard(self, lang: str) -> KeyboardMarkup:
        buttons: dict[str, str] = self.keyboards[lang]["kb_settings"]

        kb_buttons: list[KeyboardButton] = []

        for key, val in buttons.items():
            kb_buttons.append(
                KeyboardButton(text=val, callback_data=key)
            )

        return KeyboardMarkup(type="inline", buttons=[kb_buttons])

    def get_languages_keyboard(self) -> KeyboardMarkup:
        languages: list[str] = self.keyboards["kb_languages"]

        kb_buttons: list[KeyboardButton] = []

        for lang in languages:
            kb_buttons.append(
                KeyboardButton(text=lang)
            )

        return KeyboardMarkup(type="reply", buttons=[kb_buttons])


class S3Config(BaseSettings):
    s3_access_key_id: str = Field()
    s3_secret_access_key: str = Field()
    s3_url: str = Field()

    s3_region: Optional[str] = Field(default="us-east-1")
    s3_session_key: Optional[str] = Field(default=None)


class S3StoragePort(StoragePort):
    config: S3Config
    bucket: str = "audio-raw"

    def __init__(self, config: S3Config):
        self.config = config

    async def upload_audio(self, filename: str, audio: BytesIO):
        sess = Session(
            aws_access_key_id=self.config.s3_access_key_id,
            aws_secret_access_key=self.config.s3_secret_access_key,
            aws_session_token=self.config.s3_session_key,
            region_name=self.config.s3_region,
        )

        async with sess.client("s3", endpoint_url=self.config.s3_url) as s3:
            await s3.upload_fileobj(audio, self.bucket, filename)
