from typing import Union, Optional

from domain.models import KeyboardMarkup, RemoveReplyKeyboard
from domain.ports.output import BotAPIPort

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
from structlog.stdlib import BoundLogger


class AiogramBotAPIConfig(BaseSettings):
    bot_token: str = Field()


class AiogramBotAPI(BotAPIPort):
    cfg: AiogramBotAPIConfig
    bot: Bot

    def __init__(self, cfg: AiogramBotAPIConfig, log: BoundLogger):
        self.cfg = cfg
        self.bot = Bot(token=self.cfg.bot_token)
        self._log = log

    def _get_inline_kb(self, markup: KeyboardMarkup) -> InlineKeyboardMarkup:
        self._log.debug("making inline keyboard")
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

    def _get_reply_kb(self, markup: KeyboardMarkup) -> ReplyKeyboardMarkup:
        self._log.debug("making reply keyboard")
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

    def _get_keyboard(self, kb: KeyboardMarkup) -> Union[InlineKeyboardMarkup, ReplyKeyboardMarkup]:
        self._log.debug("getting keyboard")
        if kb.type == "inline":
            return self._get_inline_kb(kb)
        elif kb.type == "reply":
            return self._get_reply_kb(kb)
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

        self._log.debug("sending tg message", user_id=user_id)

        await (
            self
            .bot
            .send_message(
                chat_id=user_id,
                text=text,
                reply_markup=kb
            )
        )

        self._log.debug("message sent", user_id=user_id)
