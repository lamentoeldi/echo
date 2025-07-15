from pydantic_settings import BaseSettings
from pydantic import Field


class BotConfig(BaseSettings):
    bot_token: str = Field()
    webhook_secret: str = Field()
