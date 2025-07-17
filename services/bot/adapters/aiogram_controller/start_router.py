from services.bot.domain.ports.input import AbstractStartUseCase

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

start_router = Router(name=__name__)


@start_router.message(CommandStart())
async def handle_start(msg: Message, uc_start: AbstractStartUseCase):
    await uc_start.handle_start(
        tg_id=msg.from_user.id,
        tg_username=msg.from_user.username,
    )
