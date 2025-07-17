from services.bot.domain.ports.input import AbstractSettingsUseCase
from .states import Settings

from aiogram import Router, Bot
from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

settings_router = Router(name=__name__)


@settings_router.message(Command("settings"))
async def handle_settings(msg: Message, uc_settings: AbstractSettingsUseCase):
    await uc_settings.handle_settings(msg.from_user.id)


@settings_router.callback_query()
async def handle_change_language_1(query: CallbackQuery, state: FSMContext, uc_settings: AbstractSettingsUseCase):
    await uc_settings.change_language(query.from_user.id)
    await state.set_state(Settings.choosing_language)


@settings_router.message(Settings.choosing_language)
async def set_language(msg: Message, state: FSMContext, uc_settings: AbstractSettingsUseCase):
    await uc_settings.set_language(msg.from_user.id, msg.text)
    await state.clear()
