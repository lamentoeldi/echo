from services.bot.domain.ports.input import (
    AbstractStartUseCase,
    AbstractHelpUseCase,
    AbstractInvalidInputUseCase,
    AbstractSettingsUseCase,
    AbstractVoiceMessageUseCase
)
from .start_router import start_router
from .help_router import help_router
from .fallback_router import fallback_router
from .settings_router import settings_router
from .vm_router import vm_router

from aiogram import Dispatcher, Bot
from aiogram.fsm.storage.base import BaseStorage
from pydantic import Field
from pydantic_settings import BaseSettings


class AiogramConfig(BaseSettings):
    bot_token: str = Field()
    webhook_url: str = Field()
    webhook_secret: str = Field()


class AiogramController:
    bot: Bot
    dp: Dispatcher

    def __init__(
        self,
        cfg: AiogramConfig,
        fsm_storage: BaseStorage,
        uc_start: AbstractStartUseCase,
        uc_help: AbstractHelpUseCase,
        uc_fallback: AbstractInvalidInputUseCase,
        uc_settings: AbstractSettingsUseCase,
        uc_vm: AbstractVoiceMessageUseCase,
    ):
        self.bot = Bot(cfg.bot_token)
        self.dp = Dispatcher(
            storage=fsm_storage,
            uc_start=uc_start,
            uc_help=uc_help,
            uc_fallback=uc_fallback,
            uc_settings=uc_settings,
            uc_vm=uc_vm,
        )
        self.dp.include_routers(
            start_router,
            help_router,
            settings_router,
            vm_router,
            fallback_router,
        )

    async def start_long_polling(self):
        await self.dp.start_polling(self.bot)
