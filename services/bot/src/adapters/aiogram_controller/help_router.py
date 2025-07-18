from domain.ports.input import AbstractHelpUseCase

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

help_router = Router(name=__name__)


@help_router.message(Command("help"))
async def handle_help(message: Message, uc_help: AbstractHelpUseCase):
    await uc_help.handle_help(message.from_user.id)
