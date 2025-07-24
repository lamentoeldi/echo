from time import time
from asyncio import Semaphore

from src.domain.ports.input import AbstractTranscribeAudioUseCase
from src.domain.models import AudioPreprocessedMessage

from aiokafka import AIOKafkaConsumer, ConsumerRecord
from pydantic import Field
from pydantic_settings import BaseSettings
from structlog.stdlib import BoundLogger
from prometheus_client import Counter, Histogram

_latency_buckets = [0.1, 0.5, 1.0, 1.5, 2.5, 5.0]

kafka_consumed = Counter(
    "transcriber_kafka_consumed",
    "total amount of consumed messages",
)
kafka_errors = Counter(
    "transcriber_kafka_errors",
    "total amount of kafka consumer errors",
)
kafka_latency = Histogram(
    "transcriber_kafka_latency",
    "kafka response latency",
    buckets=_latency_buckets,
)


class KafkaConsumerConfig(BaseSettings):
    kafka_bootstrap_servers: list[str] = Field()
    kafka_consumer_group: str = Field()
    kafka_workers: int = Field(default=1)


class KafkaController:
    _ta_uc: AbstractTranscribeAudioUseCase
    _client: AIOKafkaConsumer
    _cfg: KafkaConsumerConfig

    def __init__(
        self,
        cfg: KafkaConsumerConfig,
        log: BoundLogger,
        ta_uc: AbstractTranscribeAudioUseCase,
    ):
        self._cfg = cfg
        self._log = log
        self._ta_uc = ta_uc

        topic = "audio_preprocessed"

        self._client = AIOKafkaConsumer(
            topic,
            bootstrap_servers=self._cfg.kafka_bootstrap_servers,
            group_id=self._cfg.kafka_consumer_group,
            enable_auto_commit=False,
        )

    async def _handle_message(self, msg: ConsumerRecord):
        md = (
            AudioPreprocessedMessage
            .model_validate_json(msg.value)
        )

        self._log.debug("handling message", message_id=md.content.id)

        if md.meta.status != "ok":
            raise RuntimeError("the fuck is the error")

        await (
            self
            ._ta_uc
            .transcribe_audio(md)
        )

    async def run(self):
        try:
            self._log.info("starting kafka consumer")

            await (
                self
                ._client
                .start()
            )

            async for msg in self._client:
                kafka_consumed.inc()
                start = time()
                await self._handle_message(msg)
                end = time() - start
                kafka_latency.observe(end)

                await (
                    self
                    ._client
                    .commit()
                )

        finally:
            await (
                self
                ._client
                .stop()
            )

    async def stop(self):
        self._log.info("stopping kafka consumer")
        await self._client.stop()
