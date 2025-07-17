from pydantic_settings import BaseSettings as _BaseSettings
from pydantic_settings import SettingsConfigDict

from app.utils.enums import EnvironmentEnum


class BaseSettings(_BaseSettings):
    environment: EnvironmentEnum = EnvironmentEnum.local
    debug: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def is_dev(self):
        return self.environment in (EnvironmentEnum.dev, EnvironmentEnum.local)
