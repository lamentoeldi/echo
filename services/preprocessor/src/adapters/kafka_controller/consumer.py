from time import time

from src.domain.ports.input import AbstractPreprocessUseCase
from src.domain.models import AudioRawMessage

from aiokafka import AIOKafkaConsumer, ConsumerRecord
from pydantic import Field
from pydantic_settings import BaseSettings
from structlog.stdlib import BoundLogger
from prometheus_client import Counter, Histogram

_latency_buckets = [0.1, 0.5, 1.0, 1.5, 2.5, 5.0]

kafka_consumed = Counter(
    "ap_kafka_consumed",
    "total amount of consumed messages",
)
kafka_errors = Counter(
    "ap_kafka_errors",
    "total amount of kafka consumer errors",
)
kafka_latency = Histogram(
    "ap_kafka_latency",
    "kafka response latency",
    buckets=_latency_buckets,
)


class KafkaConsumerConfig(BaseSettings):
    kafka_bootstrap_servers: list[str] = Field()
    kafka_consumer_group: str = Field()


class KafkaController:
    pp_uc: AbstractPreprocessUseCase
    client: AIOKafkaConsumer
    cfg: KafkaConsumerConfig

    def __init__(
        self,
        cfg: KafkaConsumerConfig,
        log: BoundLogger,
        pp_uc: AbstractPreprocessUseCase
    ):
        self.cfg = cfg
        self.log = log
        self.pp_uc = pp_uc

        topic = "audio_raw"

        self.client = AIOKafkaConsumer(
            topic,
            bootstrap_servers=self.cfg.kafka_bootstrap_servers,
            group_id=self.cfg.kafka_consumer_group,
            enable_auto_commit=False,
        )

    async def _handle_message(self, msg: ConsumerRecord):
        md = (
            AudioRawMessage
            .model_validate_json(msg.value)
        )

        self.log.debug("handling message", message_id=md.content.id)

        if md.meta.status != "ok":
            raise RuntimeError("the fuck is the error")

        await (
            self
            .pp_uc
            .preprocess_audio(md.content)
        )

    async def run(self):
        try:
            self.log.info("starting kafka consumer")

            await (
                self
                .client
                .start()
            )

            async for msg in self.client:
                kafka_consumed.inc()
                start = time()
                await self._handle_message(msg)
                end = time() - start
                kafka_latency.observe(end)

                await (
                    self
                    .client
                    .commit()
                )

        finally:
            await (
                self
                .client
                .stop()
            )

    async def stop(self):
        self.log.info("stopping kafka consumer")
        await self.client.stop()