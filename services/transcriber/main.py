import asyncio
from signal import SIGINT, SIGTERM

from src.domain.core import Core
from src.adapters.controllers import KafkaController, KafkaConsumerConfig
from src.adapters.bus import KafkaConfig, KafkaMessageBus
from src.adapters.storage import S3Config, S3StoragePort
from src.adapters.transcriber import WhisperConfig, WhisperAudioTranscriberAdapter
from src.infrastructure import (
    MetricsServerConfig, MetricsServer,
    GracefulStopper
)
from src.infrastructure.log import setup_logger
from src.application import TranscribeAudioUseCase


async def main():
    core = Core()

    kafka_producer_cfg = KafkaConfig()
    kafka_producer = KafkaMessageBus(kafka_producer_cfg)

    s3_cfg = S3Config()
    s3 = S3StoragePort(s3_cfg)

    whisper_cfg = WhisperConfig()
    whisper = WhisperAudioTranscriberAdapter(whisper_cfg)

    log = setup_logger()

    metrics_cfg = MetricsServerConfig()
    metrics = MetricsServer(log=log, cfg=metrics_cfg)

    uc = TranscribeAudioUseCase(
        core=core,
        storage=s3,
        broker=kafka_producer,
        transcriber=whisper,
    )

    kafka_consumer_cfg = KafkaConsumerConfig()
    kafka_consumer = KafkaController(
        log=log,
        cfg=kafka_consumer_cfg,
        ta_uc=uc,
    )

    stopper = GracefulStopper(
        log=log,
        callbacks=[
            metrics.stop,
            kafka_consumer.stop,
        ],
        signals=[SIGINT, SIGTERM],
    )

    await asyncio.gather(
        metrics.start(),
        kafka_consumer.run(),
        stopper.run(),
    )


if __name__ == '__main__':
    asyncio.run(main())
