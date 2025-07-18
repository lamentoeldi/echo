from typing import Dict, Callable
from json import load
import os

from domain.ports.output import LocalePort


class JSONLocaleProvider(LocalePort):
    locale: Dict[str, Dict[str, str]]

    def __init__(self, path: str):
        self.locale = {}
        for filename in os.listdir(path):
            if filename.endswith(".json"):
                filepath = os.path.join(path, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = load(f)
                key = os.path.splitext(filename)[0]
                self.locale[key] = data

    def __call__(self, locale: str) -> Callable[[str], str]:
        locale_dict = self.locale[locale]

        def locale_func(line: str) -> str:
            return locale_dict[line]

        return locale_func
