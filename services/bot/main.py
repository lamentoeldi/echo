import asyncio
import logging
import sys
from logging import StreamHandler, DEBUG

from src.adapters import (
    AiogramConfig,
    AiogramController
)
from src.adapters import (
    AiogramBotAPIConfig, AiogramBotAPI,
    KafkaConfig, KafkaMessageBus,
    KafkaConsumerConfig, KafkaController,
    PostgresConfig, PostgresORMRepository,
    KeyboardProvider, JSONLocaleProvider,
    S3Config, S3StoragePort
)
from src.application.usecases import (
    StartUseCase,
    HelpUseCase,
    SettingsUseCase,
    InvalidInputUseCase,
    VoiceMessageUseCase,
    ErrorResponseUseCase
)
from src.domain.core import Core
from src.config import BotConfig
from src.infrastructure.metrics import MetricsServerConfig, MetricsServer

import structlog
from aiogram.fsm.storage.memory import MemoryStorage


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

    bot_cfg = BotConfig()

    locale = JSONLocaleProvider("src/locales")
    keyboards = KeyboardProvider("src/keyboards/keyboards.json")

    pg_cfg = PostgresConfig()
    pg_repo = PostgresORMRepository(pg_cfg)

    aiogram_bot_api_cfg = AiogramBotAPIConfig()
    bot = AiogramBotAPI(aiogram_bot_api_cfg)

    kafka_producer_cfg = KafkaConfig()
    kafka_producer = KafkaMessageBus(kafka_producer_cfg)

    s3_cfg = S3Config()
    s3 = S3StoragePort(s3_cfg)

    uc_start = StartUseCase(
        config=bot_cfg,
        core=core,
        locale=locale,
        repo=pg_repo,
        bot=bot,
    )

    uc_help = HelpUseCase(
        repo=pg_repo,
        locale=locale,
        bot=bot,
    )

    uc_settings = SettingsUseCase(
        core=core,
        repo=pg_repo,
        bot=bot,
        locale=locale,
        kb=keyboards,
    )

    uc_fallback = InvalidInputUseCase(
        locale=locale,
        repo=pg_repo,
        bot=bot,
    )

    uc_vm = VoiceMessageUseCase(
        core=core,
        repo=pg_repo,
        bot=bot,
        locale=locale,
        storage=s3,
        broker=kafka_producer,
    )

    uc_error = ErrorResponseUseCase(
        repo=pg_repo,
        locale=locale,
        bot=bot,
    )

    fsm_storage = MemoryStorage()

    log = setup_logger(level=DEBUG)

    aiogram_cfg = AiogramConfig()
    aiogram_controller = AiogramController(
        cfg=aiogram_cfg,
        log=log,
        fsm_storage=fsm_storage,
        uc_start=uc_start,
        uc_help=uc_help,
        uc_settings=uc_settings,
        uc_fallback=uc_fallback,
        uc_vm=uc_vm,
        uc_error=uc_error,
    )

    kafka_consumer_cfg = KafkaConsumerConfig()
    kafka_consumer = KafkaController(
        cfg=kafka_consumer_cfg,
        log=log,
        vm_uc=uc_vm
    )

    metrics_cfg = MetricsServerConfig()
    metrics = MetricsServer(cfg=metrics_cfg, log=log)

    await asyncio.gather(
        kafka_consumer.run(),
        aiogram_controller.start_long_polling(),
        metrics.start()
    )


if __name__ == '__main__':
    asyncio.run(main())
