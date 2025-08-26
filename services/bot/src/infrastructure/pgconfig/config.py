from pydantic import Field, computed_field
from pydantic_settings import BaseSettings


class PostgresConfig(BaseSettings):
    pg_host: str = Field()
    pg_port: int = Field()
    pg_user: str = Field()
    pg_password: str = Field()
    pg_db: str = Field()
    pg_pool_min_size: int = Field(1)
    pg_pool_max_size: int = Field(5)
    pg_timeout: int = Field(15)

    @computed_field
    @property
    def dsn(self) -> str:
        return f"postgres://{self.pg_user}:{self.pg_password}@{self.pg_host}:{self.pg_port}/{self.pg_db}"

    @computed_field
    @property
    def orm_async_dsn(self) -> str:
        return f"postgresql+asyncpg://{self.pg_user}:{self.pg_password}@{self.pg_host}:{self.pg_port}/{self.pg_db}"

    @computed_field
    @property
    def orm_sync_dsn(self) -> str:
        return f"postgresql://{self.pg_user}:{self.pg_password}@{self.pg_host}:{self.pg_port}/{self.pg_db}"
