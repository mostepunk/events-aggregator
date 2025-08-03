from faststream.redis.fastapi import RedisRouter
from pydantic import SecretStr
from pydantic_settings import SettingsConfigDict

from app.settings.base import BaseSettings
from app.utils.enums import BrokerTypeEnum


class BrokerSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="broker_")

    type: BrokerTypeEnum = BrokerTypeEnum.redis

    host: str = "localhost"
    port: int = 6379

    username: SecretStr | None = None
    password: SecretStr | None = None

    incoming_event_channel: str = "events-channel"
    outgoing_notify_channel: str = "notify-channel"

    @property
    def engine(self) -> str:
        if self.type == BrokerTypeEnum.redis:
            return "redis://"

        if self.type == BrokerTypeEnum.rabbit:
            return "amqp://"

        if self.type == BrokerTypeEnum.kafka:
            return ""

    @property
    def uri(self):
        if self.username is None or self.password is None:
            credentials = ""
        else:
            credentials = f"{self.username.get_secret_value()}:"
            credentials += f"{self.password.get_secret_value()}@"

        return SecretStr(f"{self.engine}{credentials}{self.host}:{self.port}")

    @property
    def router_instance(self):
        if self.type == BrokerTypeEnum.redis:
            return RedisRouter(self.uri.get_secret_value())

    def broker_instance(self):
        if self.type == BrokerTypeEnum.redis:
            return RedisBroker(self.uri.get_secret_value())
