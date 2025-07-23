from src.domain.ports.output import MessageBusPort
from src.domain.models import AudioTranscribedMessage

from pydantic import Field
from pydantic_settings import BaseSettings
from aiokafka import AIOKafkaProducer


class KafkaConfig(BaseSettings):
    kafka_bootstrap_servers: list[str] = Field()


class KafkaMessageBus(MessageBusPort):
    cfg: KafkaConfig

    def __init__(self, cfg: KafkaConfig):
        self.cfg = cfg

    @staticmethod
    def _get_topic(source: str) -> str:
        sources = {"tg"}

        if source not in sources:
            raise RuntimeError(f"Source {source} is not supported")

        return f"audio_transcribed_{source}"

    async def publish_md(self, md: AudioTranscribedMessage):
        topic = self._get_topic(md.source)

        async with (AIOKafkaProducer(bootstrap_servers=self.cfg.kafka_bootstrap_servers) as producer):
            await (
                producer
                .send(
                    topic=topic,
                    value=md.model_dump_json(
                        exclude_none=True
                    )
                    .encode("utf-8"))
            )
