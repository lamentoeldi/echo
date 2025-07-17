import asyncio

from services.bot.adapters.aiogram_controller import (
    AiogramConfig,
    AiogramController
)
from services.bot.adapters import (
    AiogramBotAPI,
    KafkaConfig, KafkaMessageBus,
    KafkaConsumerConfig, KafkaController,
    PostgresConfig, PostgresORMRepository,
    KeyboardProvider, JSONLocaleProvider,
    S3Config, S3StoragePort
)
from services.bot.application.usecases import (
    StartUseCase,
    HelpUseCase,
    SettingsUseCase,
    InvalidInputUseCase,
    VoiceMessageUseCase
)
from services.bot.domain.core import Core
from services.bot.config import BotConfig

from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import Bot


async def main():
    core = Core()

    bot_cfg = BotConfig()

    locale = JSONLocaleProvider("./locales")
    keyboards = KeyboardProvider("./keyboards/keyboards.json")

    pg_cfg = PostgresConfig()
    pg_repo = PostgresORMRepository(pg_cfg)

    bot = AiogramBotAPI(Bot(bot_cfg.bot_token))

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

    fsm_storage = MemoryStorage()

    aiogram_cfg = AiogramConfig()
    aiogram_controller = AiogramController(
        aiogram_cfg,
        fsm_storage,
        uc_start=uc_start,
        uc_help=uc_help,
        uc_settings=uc_settings,
        uc_fallback=uc_fallback,
        uc_vm=uc_vm,
    )

    kafka_consumer_cfg = KafkaConsumerConfig()
    kafka_consumer = KafkaController(kafka_consumer_cfg, uc_vm)

    await asyncio.gather(
        kafka_consumer.run(),
        aiogram_controller.start_long_polling()
    )


if __name__ == '__main__':
    asyncio.run(main())
