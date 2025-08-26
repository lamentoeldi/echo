import asyncio
from signal import SIGINT, SIGTERM
from logging import DEBUG

from src.adapters.controllers import (
    AiogramConfig, AiogramController,
    KafkaConsumerConfig, KafkaController
)
from src.adapters.botapi.aiogram import (
    AiogramBotAPIConfig, AiogramBotAPI
)
from src.adapters.bus.kafka import (
    KafkaConfig, KafkaMessageBus
)
from src.adapters.repository.grpc import (
    TgDBRepoConfig, TgDBRepo
)
from src.adapters.keyboards import KeyboardProvider
from src.adapters.locale import JSONLocaleProvider
from src.adapters.storage import (
    S3Config, S3StoragePort
)
from src.application.usecases import (
    StartUseCase,
    HelpUseCase,
    SettingsUseCase,
    InvalidInputUseCase,
    VoiceMessageUseCase,
    ErrorResponseUseCase,
    UserBlockedBotUseCase
)
from src.domain.core import Core
from src.config import BotConfig
from src.infrastructure.metrics import MetricsServerConfig, MetricsServer
from src.infrastructure.graceful_stop import GracefulStopper
from src.infrastructure.log import setup_logger, LogConfig

from aiogram.fsm.storage.memory import MemoryStorage
from grpc.aio import insecure_channel


async def main():
    core = Core()

    log_cfg = LogConfig()
    log = setup_logger(
        name=log_cfg.log_name,
        level=log_cfg.get_log_level(),
    )

    bot_cfg = BotConfig()

    locale = JSONLocaleProvider("src/locales")
    keyboards = KeyboardProvider("src/keyboards/keyboards.json")

    tgdb_cfg = TgDBRepoConfig()
    ch = insecure_channel(f"{tgdb_cfg.tgdb_host}:{tgdb_cfg.tgdb_port}")
    tgdb_repo = TgDBRepo(
        channel=ch,
        log=log,
    )

    aiogram_bot_api_cfg = AiogramBotAPIConfig()
    bot = AiogramBotAPI(
        cfg=aiogram_bot_api_cfg,
        log=log,
    )

    kafka_producer_cfg = KafkaConfig()
    kafka_producer = KafkaMessageBus(
        cfg=kafka_producer_cfg,
        log=log,
    )

    s3_cfg = S3Config()
    s3 = S3StoragePort(
        config=s3_cfg,
        log=log,
    )

    uc_start = StartUseCase(
        config=bot_cfg,
        core=core,
        locale=locale,
        repo=tgdb_repo,
        bot=bot,
    )

    uc_help = HelpUseCase(
        repo=tgdb_repo,
        locale=locale,
        bot=bot,
    )

    uc_settings = SettingsUseCase(
        core=core,
        repo=tgdb_repo,
        bot=bot,
        locale=locale,
        kb=keyboards,
    )

    uc_fallback = InvalidInputUseCase(
        locale=locale,
        repo=tgdb_repo,
        bot=bot,
    )

    uc_vm = VoiceMessageUseCase(
        core=core,
        repo=tgdb_repo,
        bot=bot,
        locale=locale,
        storage=s3,
        broker=kafka_producer,
    )

    uc_error = ErrorResponseUseCase(
        repo=tgdb_repo,
        locale=locale,
        bot=bot,
    )

    uc_block = UserBlockedBotUseCase(
        repo=tgdb_repo,
    )

    fsm_storage = MemoryStorage()

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
        uc_block=uc_block,
    )

    kafka_consumer_cfg = KafkaConsumerConfig()
    kafka_consumer = KafkaController(
        cfg=kafka_consumer_cfg,
        log=log,
        vm_uc=uc_vm
    )

    metrics_cfg = MetricsServerConfig()
    metrics = MetricsServer(cfg=metrics_cfg, log=log)

    stopper = GracefulStopper(
        log=log,
        signals=[
            SIGINT,
            SIGTERM
        ],
        callbacks=[
            kafka_consumer.stop,
            aiogram_controller.stop,
            metrics.stop,
        ],
        stop_timeout=bot_cfg.shutdown_timeout
    )

    await asyncio.gather(
        kafka_consumer.run(),
        aiogram_controller.start(),
        metrics.start(),
        stopper.run()
    )


if __name__ == '__main__':
    asyncio.run(main())
