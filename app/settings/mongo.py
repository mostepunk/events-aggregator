from typing import Any

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

    max_pool_size: int = 10  # макс к-во соединений в пуле
    min_pool_size: int = 0  # мин к-во соединений (0 = создавать по требованию)
    max_idle_time_ms: int = 30000  #  время жизни неактивного соединения
    connect_timeout_ms: int = 10000  # таймаут установки соединения
    server_selection_timeout_ms: int = 5000  # таймаут выбора сервера
    socket_timeout_ms: int = 5000  # таймаут операций чтения/записи
    retry_writes: bool = True
    retry_reads: bool = True

    @property
    def uri(self) -> str:
        return (
            f"mongodb://"
            f"{self.username.get_secret_value()}:"
            f"{self.password.get_secret_value()}@"
            f"{self.host}:{self.port}"
        )

    @property
    def pool_settings(self) -> dict[str, Any]:
        return {
            # Connection Pool настройки
            "maxPoolSize": self.max_pool_size,
            "minPoolSize": self.min_pool_size,
            "maxIdleTimeMS": self.max_idle_time_ms,
            # Timeout настройки
            "connectTimeoutMS": self.connect_timeout_ms,
            "serverSelectionTimeoutMS": self.server_selection_timeout_ms,
            "socketTimeoutMS": self.socket_timeout_ms,
            # Надежность
            "retryWrites": self.retry_writes,
            "retryReads": self.retry_reads,
            # Read/Write концерны для консистентности
            "readConcernLevel": "majority",
            "w": "majority",
            "wtimeoutMS": 5000,
            "readPreference": "primaryPreferred",
            # Компрессия для снижения сетевого трафика
            "compressors": "snappy,zlib,zstd",
            # Heartbeat для мониторинга состояния
            "heartbeatFrequencyMS": 10000,
        }
