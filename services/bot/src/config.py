from pydantic_settings import BaseSettings
from pydantic import Field


class BotConfig(BaseSettings):
    default_locale: str = Field()
