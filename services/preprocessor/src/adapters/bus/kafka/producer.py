from src.domain.ports.output import MessageBusPort
from src.domain.models import AudioPreprocessedMessage

from pydantic import Field
from pydantic_settings import BaseSettings
from aiokafka import AIOKafkaProducer
from structlog.stdlib import BoundLogger


class KafkaConfig(BaseSettings):
    kafka_bootstrap_servers: list[str] = Field()


class KafkaMessageBus(MessageBusPort):
    cfg: KafkaConfig

    def __init__(self, cfg: KafkaConfig, log: BoundLogger):
        self.cfg = cfg
        self._log = log

    async def publish_md(self, md: AudioPreprocessedMessage):
        self._log.debug("publishing message", message_id=md.content.id)

        async with (AIOKafkaProducer(bootstrap_servers=self.cfg.kafka_bootstrap_servers) as producer):
            await (
                producer
                .send(
                    topic="audio_preprocessed",
                    value=md.model_dump_json(
                        exclude_none=True
                    )
                    .encode("utf-8"))
            )

        self._log.debug("message published", message_id=md.content.id)
