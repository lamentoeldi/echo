from typing import Union, Optional

from services.bot.domain.models import KeyboardMarkup, RemoveReplyKeyboard
from services.bot.domain.ports.output import BotAPIPort

from aiogram import Bot
from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton as ReplyKeyboardButton,
    ReplyKeyboardRemove
)
from pydantic import Field
from pydantic_settings import BaseSettings


class AiogramBotAPIConfig(BaseSettings):
    bot_token: str = Field()


class AiogramBotAPI(BotAPIPort):
    cfg: AiogramBotAPIConfig
    bot: Bot

    def __init__(self, cfg: AiogramBotAPIConfig):
        self.cfg = cfg
        self.bot = Bot(token=self.cfg.bot_token)

    @staticmethod
    def _get_inline_kb(markup: KeyboardMarkup) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=btn.text,
                        callback_data=btn.callback_data or btn.text
                    )
                    for btn in row
                ]
                for row in markup.buttons
            ]
        )

    @staticmethod
    def _get_reply_kb(markup: KeyboardMarkup) -> ReplyKeyboardMarkup:
        return ReplyKeyboardMarkup(
            keyboard=[
                [
                    ReplyKeyboardButton(text=btn.text)
                    for btn in row
                ]
                for row in markup.buttons
            ],
            resize_keyboard=True
        )

    @staticmethod
    def _get_keyboard(kb: KeyboardMarkup) -> Union[InlineKeyboardMarkup, ReplyKeyboardMarkup]:
        if kb.type == "inline":
            return AiogramBotAPI._get_inline_kb(kb)
        elif kb.type == "reply":
            return AiogramBotAPI._get_reply_kb(kb)
        else:
            raise ValueError(f"Unknown keyboard type: {kb.type}")

    async def send_text(
        self,
        user_id: int,
        text: str,
        keyboard: Optional[Union[KeyboardMarkup, RemoveReplyKeyboard]] = None
    ):
        kb: Optional[Union[InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove]] = None
        if isinstance(keyboard, KeyboardMarkup):
            kb = self._get_keyboard(keyboard)
        if isinstance(keyboard, RemoveReplyKeyboard):
            kb = ReplyKeyboardRemove()

        await (
            self
            .bot
            .send_message(
                chat_id=user_id,
                text=text,
                reply_markup=kb
            )
        )
