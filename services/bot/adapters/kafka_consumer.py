from services.bot.domain.ports.input import AbstractVoiceMessageUseCase
from services.bot.domain.models import AudioTranscribedMessage, AudioTranscribed

from aiokafka import AIOKafkaConsumer, ConsumerRecord
from pydantic import Field
from pydantic_settings import BaseSettings


class KafkaConsumerConfig(BaseSettings):
    kafka_bootstrap_servers: list[str] = Field()
    kafka_consumer_group: str = Field()


class KafkaController:
    vm_uc: AbstractVoiceMessageUseCase
    client: AIOKafkaConsumer
    cfg: KafkaConsumerConfig

    def __init__(self, cfg: KafkaConsumerConfig, vm_uc: AbstractVoiceMessageUseCase):
        self.cfg = cfg
        self.vm_uc = vm_uc

        topic = "audio_transcribed_tg"

        self.client = AIOKafkaConsumer(
            topic,
            bootstrap_servers=self.cfg.kafka_bootstrap_servers,
            group_id=self.cfg.kafka_consumer_group,
            enable_auto_commit=False,
        )

    async def _handle_message(self, msg: ConsumerRecord):
        transcription = (
            AudioTranscribedMessage
            .model_validate_json(msg.value)
        )

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
            await (
                self
                .client
                .start()
            )

            async for msg in self.client:
                await self._handle_message(msg)
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
