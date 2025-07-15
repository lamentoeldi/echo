import io
from abc import ABC, abstractmethod


class StartUseCase(ABC):
    @abstractmethod
    async def handle_start(self, tg_id: int, tg_username: str):
        """
        To handle /start command
        Registers user in system, returns greeting message text
        :param tg_id:
        :param tg_username:
        :return:
        """
        pass


class HelpUseCase(ABC):
    @abstractmethod
    async def handle_help(self, tg_id: int, tg_username: str):
        """
        To handle /help command
        Sends help message
        :param tg_id:
        :param tg_username:
        :return:
        """
        pass


class InvalidInputUseCase(ABC):
    @abstractmethod
    async def handle_invalid_input(self):
        """
        To handle invalid input
        Send invalid input message
        :return:
        """
        pass


class SettingsUseCase(ABC):
    @abstractmethod
    async def handle_settings(self):
        """
        To handle /settings command
        Sends keyboard with bot settings
        :return:
        """
        pass

    @abstractmethod
    async def change_language(self, user_id: int, new_lang: str):
        """
        To change language
        :param user_id:
        :param new_lang:
        :return:
        """
        pass


class VoiceMessageUseCase(ABC):
    @abstractmethod
    async def start_vm_handling(self, user_id: int, audio: io.BytesIO):
        """
        To start processing voice message
        Tries to start processing, sends status (ok/error) back to user
        :param user_id:
        :param audio:
        :return:
        """
        pass

    @abstractmethod
    async def send_transcription(self, user_id: int, transcription: str):
        """
        Sends transcription back to user after processing voice message
        :param user_id:
        :param transcription:
        :return:
        """
        pass

    @abstractmethod
    async def send_error_text(self, user_id: int, error: str):
        """
        Sends error message back to user after processing voice message if failed
        :param user_id:
        :param error:
        :return:
        """
        pass
