from io import BytesIO
from typing import Optional

from aioboto3 import Session
from pydantic import Field
from pydantic_settings import BaseSettings

from src.domain.ports.output import StoragePort


class S3Config(BaseSettings):
    s3_access_key_id: str = Field()
    s3_secret_access_key: str = Field()
    s3_url: str = Field()

    s3_region: Optional[str] = Field(default="us-east-1")
    s3_session_key: Optional[str] = Field(default=None)


class S3StoragePort(StoragePort):
    config: S3Config
    input_bucket: str = "audio-raw"
    output_bucket: str = "audio-preprocessed"

    def __init__(self, config: S3Config):
        self.config = config

    async def upload_audio(self, filename: str, audio: BytesIO):
        audio.seek(0)

        sess = Session(
            aws_access_key_id=self.config.s3_access_key_id,
            aws_secret_access_key=self.config.s3_secret_access_key,
            aws_session_token=self.config.s3_session_key,
            region_name=self.config.s3_region,
        )

        async with sess.client("s3", endpoint_url=self.config.s3_url) as s3:
            await s3.upload_fileobj(audio, self.output_bucket, filename)

    async def download_audio(self, filename: str) -> BytesIO:
        stream = BytesIO()

        sess = Session(
            aws_access_key_id=self.config.s3_access_key_id,
            aws_secret_access_key=self.config.s3_secret_access_key,
            aws_session_token=self.config.s3_session_key,
            region_name=self.config.s3_region,
        )

        async with sess.client("s3", endpoint_url=self.config.s3_url) as s3:
            await s3.download_fileobj(self.input_bucket, filename, stream)

        stream.seek(0)
        return stream
