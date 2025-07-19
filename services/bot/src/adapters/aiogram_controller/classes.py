from typing import Literal, Optional, Self

from domain.ports.input import (
    AbstractStartUseCase,
    AbstractHelpUseCase,
    AbstractInvalidInputUseCase,
    AbstractSettingsUseCase,
    AbstractVoiceMessageUseCase,
    AbstractErrorResponseUseCase
)
from .handlers import (
    start_router,
    help_router,
    settings_router,
    fallback_router,
    vm_router
)
from .middleware import (
    RequestIDMiddleware,
    StructuredLoggerMiddleware,
    ExceptionHandlerMiddleware,
    BotRequestsCounterMiddleware,
    BotLatencyMiddleware,
    GracefulStopMiddleware
)

from aiogram import Dispatcher, Bot
from aiogram.fsm.storage.base import BaseStorage
from pydantic import Field, model_validator
from pydantic_settings import BaseSettings
from structlog.stdlib import BoundLogger


class AiogramConfig(BaseSettings):
    bot_token: str = Field()
    bot_api_mode: Literal["long_polling", "webhook"] = Field(default="long_polling")

    webhook_secret: Optional[str] = None
    webhook_host: Optional[str] = None
    webhook_port: Optional[int] = None

    @model_validator(mode="after")
    def validate_webhook_params(self) -> Self:
        if self.bot_api_mode == "long_polling":
            return self

        if self.bot_api_mode != "webhook":
            raise ValueError("invalid bot api mode")

        if self.webhook_secret is None or self.webhook_host is None or self.webhook_port is None:
            raise ValueError("webhook params cannot be None in webhook mode")


class AiogramController:
    cfg: AiogramConfig
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
        self.cfg = cfg
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

        self.mw_graceful_stop = GracefulStopMiddleware()
        self.mw_request_id = RequestIDMiddleware()
        self.mw_log = StructuredLoggerMiddleware(log)
        self.mw_exception_handler = ExceptionHandlerMiddleware(uc_error)
        self.mw_latency = BotLatencyMiddleware()
        self.mw_request_counter = BotRequestsCounterMiddleware()

        self.dp.message.middleware(self.mw_graceful_stop)
        self.dp.message.middleware(self.mw_request_id)
        self.dp.message.middleware(self.mw_request_counter)
        self.dp.message.middleware(self.mw_log)
        self.dp.message.middleware(self.mw_exception_handler)
        self.dp.message.middleware(self.mw_latency)

    async def _start_long_polling(self):
        self.log.info("starting tg bot api long polling")
        await self.dp.start_polling(self.bot)

    async def _stop_long_polling(self):
        self.log.info("stopping tg bot api long polling")
        await self.dp.stop_polling()
        await self.mw_graceful_stop.wait()

    async def _start_webhook(self):
        # to be implemented
        pass

    async def _stop_webhook(self):
        # to be implemented
        pass

    async def start(self):
        if self.cfg.bot_api_mode == "long_polling":
            await self._start_long_polling()
        elif self.cfg.bot_api_mode == "webhook":
            await self._start_webhook()
        else:
            raise ValueError("bot_api_mode must be 'long_polling' or 'webhook'")

    async def stop(self):
        if self.cfg.bot_api_mode == "long_polling":
            await self._stop_long_polling()
        elif self.cfg.bot_api_mode == "webhook":
            await self._stop_webhook()
        else:
            raise ValueError("bot_api_mode must be 'long_polling' or 'webhook'")
