from json import loads
from typing import Callable, Dict

from ..domain.ports.output import LocalePort, KeyboardProviderPort
from ..domain.models import KeyboardMarkup, KeyboardButton


class JSONLocaleProvider(LocalePort):
    locale: Dict[str, Dict[str, str]]

    def __init__(self, json: str):
        self.locale = loads(json)

    def __call__(self, locale: str) -> Callable[[str], str]:
        locale_dict = self.locale[locale]

        def locale_func(line: str) -> str:
            return locale_dict[line]

        return locale_func


class KeyboardProvider(KeyboardProviderPort):
    keyboards: dict

    def __init__(self, json: str):
        self.keyboards = loads(json)

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
