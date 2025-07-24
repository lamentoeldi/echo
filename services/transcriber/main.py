import asyncio
import logging
import sys
import warnings
from logging import StreamHandler
from signal import SIGINT, SIGTERM

from src.domain.core import Core
from src.adapters import (
    KafkaConfig, KafkaMessageBus,
    KafkaController, KafkaConsumerConfig,
    S3Config, S3StoragePort,
    WhisperConfig, WhisperAudioTranscriberAdapter
)
from src.infrastructure import (
    MetricsServerConfig, MetricsServer,
    GracefulStopper
)
from src.application import TranscribeAudioUseCase

import structlog


def setup_logger(
    name: str = "main",
    level: int = logging.INFO,
    disable_other_loggers: bool = True
) -> structlog.BoundLogger:
    warnings.filterwarnings("ignore", category=UserWarning)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False

    handler = StreamHandler(sys.stdout)
    handler.setLevel(level)
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.handlers = [handler]

    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.stdlib.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.make_filtering_bound_logger(level),
        cache_logger_on_first_use=True,
    )

    if disable_other_loggers:
        for other_name in logging.root.manager.loggerDict:
            if not other_name.startswith(name):
                other_logger = logging.getLogger(other_name)
                other_logger.setLevel(logging.CRITICAL + 1)
                other_logger.propagate = False

    return structlog.get_logger(name)


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
