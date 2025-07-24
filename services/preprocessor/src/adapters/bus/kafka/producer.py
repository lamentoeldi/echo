from src.domain.ports.output import MessageBusPort
from src.domain.models import AudioPreprocessedMessage

from pydantic import Field
from pydantic_settings import BaseSettings
from aiokafka import AIOKafkaProducer


class KafkaConfig(BaseSettings):
    kafka_bootstrap_servers: list[str] = Field()


class KafkaMessageBus(MessageBusPort):
    cfg: KafkaConfig

    def __init__(self, cfg: KafkaConfig):
        self.cfg = cfg

    async def publish_md(self, md: AudioPreprocessedMessage):
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
