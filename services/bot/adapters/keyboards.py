from json import load

from services.bot.domain.ports.output import KeyboardProviderPort
from services.bot.domain.models import KeyboardMarkup, KeyboardButton


class KeyboardProvider(KeyboardProviderPort):
    keyboards: dict

    def __init__(self, path: str):
        with open(path, 'r') as f:
            self.keyboards = load(f)

    def get_settings_keyboard(self, lang: str) -> KeyboardMarkup:
        buttons: dict[str, str] = self.keyboards[lang]["kb_settings"]

        kb_buttons: list[KeyboardButton] = []

        for key, val in buttons.items():
            kb_buttons.append(
                KeyboardButton(text=val, callback_data=key)
            )

        return KeyboardMarkup(type="inline", buttons=[kb_buttons])

    def get_languages_keyboard(self) -> KeyboardMarkup:
        languages: list[str] = self.keyboards["kb_languages"]

        kb_buttons: list[KeyboardButton] = []

        for lang in languages:
            kb_buttons.append(
                KeyboardButton(text=lang)
            )

        return KeyboardMarkup(type="reply", buttons=[kb_buttons])
