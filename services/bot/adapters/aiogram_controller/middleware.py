from typing import Callable, Dict, Awaitable, Any

from services.bot.domain.ports.input import AbstractErrorResponseUseCase

from structlog.stdlib import BoundLogger
from aiogram import BaseMiddleware
from aiogram.types import Message
from uuid6 import uuid7


class RequestIDMiddleware(BaseMiddleware):
    """
    Request ID provider middleware.
    Provides UUID request id via handler context.
    """

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        request_id = uuid7()
        data["request_id"] = request_id

        return await handler(event, data)


class StructuredLoggerMiddleware(BaseMiddleware):
    """
    Structured logging middleware.
    Logs requests, provides logger via handler context.
    """
    logger: BoundLogger

    def __init__(self, logger: BoundLogger):
        self.logger = logger

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        log = self.logger.new()

        if data.get("request_id") is not None:
            log = log.bind(
                request_id=str(data["request_id"]),
                user_id=str(event.from_user.id),
            )

        data["log"] = log

        log.debug("received request")

        return await handler(event, data)


class ExceptionHandlerMiddleware(BaseMiddleware):
    """
    Exception handler middleware.
    Handles exceptions raised inside handlers, logs them and sends error response back to user.
    """
    def __init__(self, uc: AbstractErrorResponseUseCase):
        self.uc = uc

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        try:
            return await handler(event, data)
        except Exception as err:
            if data.get("log") is not None:
                log: BoundLogger = data["log"]
                log.error(str(err))
                await self.uc.handle_error(event.from_user.id)
            else:
                raise err
