from typing import Dict, Callable
from json import loads

from services.bot.domain.ports.output import LocalePort


class JSONLocaleProvider(LocalePort):
    locale: Dict[str, Dict[str, str]]

    def __init__(self, json: str):
        self.locale = loads(json)

    def __call__(self, locale: str) -> Callable[[str], str]:
        locale_dict = self.locale[locale]

        def locale_func(line: str) -> str:
            return locale_dict[line]

        return locale_func
