from time import time

from domain.ports.input import AbstractVoiceMessageUseCase
from domain.models import AudioTranscribedMessage

from aiokafka import AIOKafkaConsumer, ConsumerRecord
from pydantic import Field
from pydantic_settings import BaseSettings
from structlog.stdlib import BoundLogger
from prometheus_client import Counter, Histogram

_latency_buckets = [0.1, 0.5, 1.0, 1.5, 2.5, 5.0]

kafka_consumed = Counter(
    "tg_bot_kafka_consumed",
    "total amount of consumed messages",
)
kafka_errors = Counter(
    "tg_bot_kafka_errors",
    "total amount of kafka consumer errors",
)
kafka_latency = Histogram(
    "tg_bot_kafka_latency",
    "kafka response latency",
    buckets=_latency_buckets,
)


class KafkaConsumerConfig(BaseSettings):
    kafka_bootstrap_servers: list[str] = Field()
    kafka_consumer_group: str = Field()
    kafka_input_topic: str = Field("audio_transcribed_tg")


class KafkaController:
    vm_uc: AbstractVoiceMessageUseCase
    client: AIOKafkaConsumer
    cfg: KafkaConsumerConfig

    def __init__(
        self,
        cfg: KafkaConsumerConfig,
        log: BoundLogger,
        vm_uc: AbstractVoiceMessageUseCase
    ):
        self.cfg = cfg
        self.log = log
        self.vm_uc = vm_uc

        self.client = AIOKafkaConsumer(
            self.cfg.kafka_input_topic,
            bootstrap_servers=self.cfg.kafka_bootstrap_servers,
            group_id=self.cfg.kafka_consumer_group,
            enable_auto_commit=False,
        )

    async def _handle_message(self, msg: ConsumerRecord):
        transcription = (
            AudioTranscribedMessage
            .model_validate_json(msg.value)
        )

        self.log.debug("handling message", message_id=transcription.content.id)

        if transcription.meta.status != "ok":
            await (
                self
                .vm_uc
                .send_error_text(
                    user_id=transcription.content.user_id
                )
            )
            return

        await (
            self
            .vm_uc
            .send_transcription(
                user_id=transcription.content.user_id,
                transcription=transcription.content.transcription
            )
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
