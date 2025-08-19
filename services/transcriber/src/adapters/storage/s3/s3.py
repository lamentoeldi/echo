from io import BytesIO
from typing import Optional

from aioboto3 import Session
from pydantic import Field
from pydantic_settings import BaseSettings
from structlog.stdlib import BoundLogger

from src.domain.ports.output import StoragePort


class S3Config(BaseSettings):
    s3_access_key_id: str = Field()
    s3_secret_access_key: str = Field()
    s3_url: str = Field()

    s3_region: Optional[str] = Field(default="us-east-1")
    s3_session_key: Optional[str] = Field(default=None)


class S3StoragePort(StoragePort):
    config: S3Config
    input_bucket: str = "audio-preprocessed"

    def __init__(self, config: S3Config, log: BoundLogger):
        self.config = config
        self._log = log

    async def download_audio(self, filename: str) -> BytesIO:
        stream = BytesIO()

        sess = Session(
            aws_access_key_id=self.config.s3_access_key_id,
            aws_secret_access_key=self.config.s3_secret_access_key,
            aws_session_token=self.config.s3_session_key,
            region_name=self.config.s3_region,
        )

        self._log.debug("downloading audio", key=filename)

        async with sess.client("s3", endpoint_url=self.config.s3_url) as s3:
            await s3.download_fileobj(self.input_bucket, filename, stream)

        self._log.debug("audio downloaded")

        stream.seek(0)
        return stream

    async def delete_audio(self, filename: str):
        sess = Session(
            aws_access_key_id=self.config.s3_access_key_id,
            aws_secret_access_key=self.config.s3_secret_access_key,
            aws_session_token=self.config.s3_session_key,
            region_name=self.config.s3_region,
        )

        self._log.debug("deleting audio", key=filename)

        async with sess.client("s3", endpoint_url=self.config.s3_url) as s3:
            await s3.delete_object(Bucket=self.input_bucket, Key=filename)

        self._log.debug("audio deleted", key=filename)
