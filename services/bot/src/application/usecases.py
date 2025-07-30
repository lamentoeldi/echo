import io
from abc import ABC, abstractmethod
from uuid import UUID
from typing import Optional

from domain.ports.input import (
    AbstractStartUseCase,
    AbstractHelpUseCase,
    AbstractSettingsUseCase,
    AbstractInvalidInputUseCase,
    AbstractVoiceMessageUseCase,
    AbstractErrorResponseUseCase,
    AbstractUserBlockedBotUseCase
)
from domain.ports.output import (
    RepositoryPort,
    LocalePort,
    BotAPIPort,
    MessageBusPort,
    StoragePort,
    KeyboardProviderPort
)
from domain.models import (
    UserUpdate,
    User,
    AudioRawMessage,
    RemoveReplyKeyboard
)
from domain.exceptions import AlreadyExists
from config import BotConfig

from structlog.stdlib import BoundLogger


class AbstractCore(ABC):
    @abstractmethod
    def create_user(self, tg_id: int, tg_username: str, lang: str) -> User:
        """
        Creates a new user
        :param tg_id:
        :param tg_username:
        :param lang:
        :return:
        """
        pass

    @abstractmethod
    def create_audio_md(self, user_id: UUID, audio: io.BytesIO) -> AudioRawMessage:
        """
        Creates an audio md object
        :return:
        """
        pass

    @abstractmethod
    def create_audio_transcription(self, locale_msg: str, transcription: str) -> str:
        """
        Creates an audio transcription message with markup
        :param locale_msg:
        :param transcription:
        :return:
        """
        pass

    @abstractmethod
    def create_error_text(self, locale_msg: str, error: str) -> str:
        """
        Creates an error text message with markup
        :param locale_msg:
        :param error:
        :return:
        """
        pass


class StartUseCase(AbstractStartUseCase):
    def __init__(
        self,
        config: BotConfig,
        core: AbstractCore,
        repo: RepositoryPort,
        locale: LocalePort,
        bot: BotAPIPort
    ):
        self.config = config
        self.core = core
        self.repo = repo
        self.locale = locale
        self.bot = bot

    async def handle_start(self, tg_id: int, tg_username: Optional[str]):
        default_lang = (
            self
            .config
            .default_locale
        )

        greeting = (
            self
            .locale
            (default_lang)
            ("greeting")
        )

        await (
            self
            .bot
            .send_text
            (tg_id, greeting)
        )

        user = (
            self
            .core
            .create_user
            (tg_id, tg_username, default_lang)
        )

        try:
            await (
                self
                .repo
                .add_user(user)
            )
        except AlreadyExists:
            pass


class HelpUseCase(AbstractHelpUseCase):
    def __init__(
        self,
        repo: RepositoryPort,
        locale: LocalePort,
        bot: BotAPIPort
    ):
        self.repo = repo
        self.locale = locale
        self.bot = bot

    async def handle_help(self, tg_id: int):
        lang = ((
            await
            self
            .repo
            .get_user(tg_id))
            .language
        )

        await (
            self
            .bot
            .send_text(
                tg_id, self.locale(lang)("help")
            )
        )


class SettingsUseCase(AbstractSettingsUseCase):
    def __init__(
        self,
        core: AbstractCore,
        repo: RepositoryPort,
        locale: LocalePort,
        bot: BotAPIPort,
        kb: KeyboardProviderPort
    ):
        self.core = core
        self.repo = repo
        self.locale = locale
        self.bot = bot
        self.kb = kb

    async def handle_settings(self, tg_id: int):
        lang = ((
            await
            self
            .repo
            .get_user(tg_id))
            .language
        )

        kb = (
            self
            .kb
            .get_settings_keyboard(lang)
        )

        await (
            self
            .bot
            .send_text(
                tg_id, self.locale(lang)("settings"), kb
            )
        )

    async def change_language(self, tg_id: int):
        lang = ((
            await
            self
            .repo
            .get_user(tg_id))
            .language
        )

        kb = (
            self
            .kb
            .get_languages_keyboard()
        )

        await (
            self
            .bot
            .send_text(
                tg_id, self.locale(lang)("change_language"), kb
            )
        )

    async def set_language(self, tg_id: int, new_lang: str):
        lang = ((
            await
            self
            .repo
            .get_user(tg_id))
            .language
        )

        await (
            self
            .bot
            .send_text(
                tg_id, self.locale(lang)("language_set"), RemoveReplyKeyboard()
            )
        )

        upd = UserUpdate(language=new_lang)
        await (
            self
            .repo
            .update_user(tg_id, upd)
        )


class InvalidInputUseCase(AbstractInvalidInputUseCase):
    def __init__(
        self,
        locale: LocalePort,
        bot: BotAPIPort,
        repo: RepositoryPort,
    ):
        self.locale = locale
        self.bot = bot
        self.repo = repo

    async def handle_invalid_input(self, tg_id: int):
        lang = ((
            await
            self
            .repo
            .get_user(tg_id))
            .language
        )

        await (
            self
            .bot
            .send_text(tg_id, self.locale(lang)("invalid_input"))
        )


class VoiceMessageUseCase(AbstractVoiceMessageUseCase):
    def __init__(
        self,
        core: AbstractCore,
        bot: BotAPIPort,
        repo: RepositoryPort,
        locale: LocalePort,
        broker: MessageBusPort,
        storage: StoragePort
    ):
        self.core = core
        self.bot = bot
        self.repo = repo
        self.locale = locale
        self.broker = broker
        self.storage = storage

    async def start_vm_handling(self, tg_id: int, audio: io.BytesIO):
        audio.seek(0)

        user = await (
            self
            .repo
            .get_user(tg_id)
        )

        md = (
            self
            .core
            .create_audio_md(user.id, audio)
        )

        filename = f"{md.content.id}.ogg"

        await (
            self
            .storage
            .upload_audio(filename, audio)
        )

        await (
            self
            .broker
            .publish_audio(md)
        )

        await (
            self
            .bot
            .send_text(tg_id, self.locale(user.language)("vm_accepted"))
        )

    async def send_transcription(self, user_id: UUID, transcription: str):
        user = await (
            self
            .repo
            .get_user(user_id)
        )

        msg = (
            self
            .core
            .create_audio_transcription(
                self.locale(user.language)("transcription_success"), transcription
            )
        )

        await (
            self
            .bot
            .send_text(user.tg_id, msg)
        )

    async def send_error_text(self, user_id: UUID):
        user = await (
            self
            .repo
            .get_user(user_id)
        )

        msg = (
            self
            .core
            .create_error_text(
                self.locale(user.language)("transcription_error"), self.locale(user.language)("vm_error")
            )
        )

        await (
            self
            .bot
            .send_text(user.tg_id, msg)
        )


class ErrorResponseUseCase(AbstractErrorResponseUseCase):
    def __init__(
        self,
        repo: RepositoryPort,
        locale: LocalePort,
        bot: BotAPIPort,
    ):
        self.repo = repo
        self.locale = locale
        self.bot = bot

    async def handle_error(self, tg_id: int):
        user = await (
            self
            .repo
            .get_user(tg_id)
        )

        await self.bot.send_text(tg_id, self.locale(user.language)("error"))


class UserBlockedBotUseCase(AbstractUserBlockedBotUseCase):
    def __init__(
        self,
        repo: RepositoryPort,
    ):
        self._repo = repo

    async def handle(self, tg_id: int):
        await self._repo.delete_user(tg_id)
