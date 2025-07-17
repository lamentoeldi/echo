from services.bot.domain.ports.input import AbstractInvalidInputUseCase

from aiogram import Router
from aiogram.types import Message

fallback_router = Router(name=__name__)


@fallback_router.message()
async def handle_fallback(msg: Message, uc_fallback: AbstractInvalidInputUseCase):
    await uc_fallback.handle_invalid_input(msg.from_user.id)
