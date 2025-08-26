from io import BytesIO
from typing import Optional

from aioboto3 import Session
from pydantic import Field
from pydantic_settings import BaseSettings
from structlog.stdlib import BoundLogger

from domain.ports.output import StoragePort


class S3Config(BaseSettings):
    s3_access_key_id: str = Field()
    s3_secret_access_key: str = Field()
    s3_url: str = Field()
    s3_output_bucket: str = Field("audio-raw")

    s3_region: Optional[str] = Field(default="us-east-1")
    s3_session_key: Optional[str] = Field(default=None)


class S3StoragePort(StoragePort):
    def __init__(self, config: S3Config, log: BoundLogger):
        self._cfg = config
        self._log = log

    async def upload_audio(self, filename: str, audio: BytesIO):
        audio.seek(0)

        sess = Session(
            aws_access_key_id=self.config.s3_access_key_id,
            aws_secret_access_key=self.config.s3_secret_access_key,
            aws_session_token=self.config.s3_session_key,
            region_name=self.config.s3_region,
        )

        self._log.debug("uploading audio", key=filename)

        async with sess.client("s3", endpoint_url=self.config.s3_url) as s3:
            await s3.upload_fileobj(audio, self._cfg.s3_output_bucket, filename)

        self._log.debug("audio uploaded", key=filename)
