from pydantic import SecretStr
from pydantic_settings import SettingsConfigDict

from app.settings.base import BaseSettings


class MongoDBSettings(BaseSettings):

    model_config = SettingsConfigDict(env_prefix="mongodb_")

    host: str = "localhost"
    port: int = 27017
    db_name: str = "events_aggregator"
    password: SecretStr = "mongo"
    username: SecretStr = "mongo"

    @property
    def uri(self) -> str:
        return f"mongodb://{self.username.get_secret_value()}:{self.password.get_secret_value()}@{self.host}:{self.port}"
