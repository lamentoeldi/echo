import asyncio
import logging
import sys
from logging import StreamHandler
from signal import SIGINT, SIGTERM

from src.adapters.kafka_controller.consumer import KafkaConsumerConfig, KafkaController
from src.adapters.s3_storage import S3Config, S3StoragePort
from src.adapters.kafka_message_bus import KafkaConfig, KafkaMessageBus
from src.application.usecases import PreprocessUseCase
from src.domain.core import Core
from src.infrastructure.metrics import MetricsServerConfig, MetricsServer
from src.infrastructure.graceful_stop import GracefulStopper

import structlog


def setup_logger(
    name: str = "main",
    level: int = logging.INFO,
    disable_other_loggers: bool = True
) -> structlog.BoundLogger:
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

    s3_cfg = S3Config()
    s3 = S3StoragePort(s3_cfg)

    kafka_mb_cfg = KafkaConfig()
    kafka_mb = KafkaMessageBus(kafka_mb_cfg)

    uc = PreprocessUseCase(core, s3, kafka_mb)

    log = setup_logger()

    metrics_cfg = MetricsServerConfig()
    metrics = MetricsServer(metrics_cfg)

    kafka_cfg = KafkaConsumerConfig()
    kafka = KafkaController(
        cfg=kafka_cfg,
        log=log,
        pp_uc=uc
    )

    stop = GracefulStopper(
        log=log,
        callbacks=[
            kafka.stop,
            metrics.stop,
        ],
        signals=[SIGINT, SIGTERM],
    )

    await asyncio.gather(
        kafka.run(),
        metrics.start(),
        stop.run(),
    )

if __name__ == '__main__':
    asyncio.run(main())
