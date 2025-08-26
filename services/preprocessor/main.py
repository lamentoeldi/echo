import asyncio
from signal import SIGINT, SIGTERM

from src.adapters.controllers import KafkaConsumerConfig, KafkaController
from src.adapters.storage import S3Config, S3StoragePort
from src.adapters.bus import KafkaConfig, KafkaMessageBus
from src.application.usecases import PreprocessUseCase
from src.domain.core import Core
from src.infrastructure.metrics import MetricsServerConfig, MetricsServer
from src.infrastructure.graceful_stop import GracefulStopper
from src.infrastructure.log import setup_logger, LogConfig


async def main():
    core = Core()

    log_cfg = LogConfig()
    log = setup_logger(
        name=log_cfg.log_name,
        level=log_cfg.get_log_level(),
    )

    s3_cfg = S3Config()
    s3 = S3StoragePort(
        config=s3_cfg,
        log=log,
    )

    kafka_mb_cfg = KafkaConfig()
    kafka_mb = KafkaMessageBus(
        cfg=kafka_mb_cfg,
        log=log,
    )

    uc = PreprocessUseCase(core, s3, kafka_mb)

    metrics_cfg = MetricsServerConfig()
    metrics = MetricsServer(
        cfg=metrics_cfg,
        log=log
    )

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
