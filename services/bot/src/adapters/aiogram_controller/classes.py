from typing import Literal, Optional, Self

from domain.ports.input import (
    AbstractStartUseCase,
    AbstractHelpUseCase,
    AbstractInvalidInputUseCase,
    AbstractSettingsUseCase,
    AbstractVoiceMessageUseCase,
    AbstractErrorResponseUseCase
)
from .start_router import start_router
from .help_router import help_router
from .fallback_router import fallback_router
from .settings_router import settings_router
from .vm_router import vm_router
from .middleware import (
    RequestIDMiddleware,
    StructuredLoggerMiddleware,
    ExceptionHandlerMiddleware,
    BotRequestsCounterMiddleware,
    BotLatencyMiddleware
)

from aiogram import Dispatcher, Bot
from aiogram.fsm.storage.base import BaseStorage
from pydantic import Field, model_validator
from pydantic_settings import BaseSettings
from structlog.stdlib import BoundLogger


class AiogramConfig(BaseSettings):
    bot_token: str = Field()
    bot_api_mode: Literal["long_polling", "webhook"] = Field(default="long_polling")

    webhook_url: Optional[str] = Field()
    webhook_secret: Optional[str] = Field()

    @model_validator(mode="after")
    def validate_webhook_params(self) -> Self:
        if self.bot_api_mode == "long_polling":
            return self

        if self.webhook_url is None or self.webhook_secret is None:
            raise ValueError("webhook params cannot be None in webhook mode")


class AiogramController:
    bot: Bot
    dp: Dispatcher

    def __init__(
        self,
        cfg: AiogramConfig,
        log: BoundLogger,
        fsm_storage: BaseStorage,
        uc_start: AbstractStartUseCase,
        uc_help: AbstractHelpUseCase,
        uc_fallback: AbstractInvalidInputUseCase,
        uc_settings: AbstractSettingsUseCase,
        uc_vm: AbstractVoiceMessageUseCase,
        uc_error: AbstractErrorResponseUseCase,
    ):
        self.log = log
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

        mw_request_id = RequestIDMiddleware()
        mw_log = StructuredLoggerMiddleware(log)
        mw_exception_handler = ExceptionHandlerMiddleware(uc_error)
        mw_latency = BotLatencyMiddleware()
        mw_request_counter = BotRequestsCounterMiddleware()

        self.dp.message.middleware(mw_request_id)
        self.dp.message.middleware(mw_request_counter)
        self.dp.message.middleware(mw_log)
        self.dp.message.middleware(mw_exception_handler)
        self.dp.message.middleware(mw_latency)

    async def start_long_polling(self):
        self.log.info("starting bot api server")
        await self.dp.start_polling(self.bot)
