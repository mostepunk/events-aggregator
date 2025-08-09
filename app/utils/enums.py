from enum import unique

from app.utils.base_enum import StrEnum


class EventLevelEnum(StrEnum):
    info = "info", "информация"
    warning = "warning", "предупреждение"
    error = "error", "ошибка"
    critical = "critical", "критическая"


@unique
class EnvironmentEnum(StrEnum):
    prod: str = "PROD", "production"
    dev: str = "DEV", "development"
    local: str = "LOCAL", "local"


class LogLevelEnum(StrEnum):
    notset = "NOTSET", "не установлен"
    debug = "DEBUG", "отладка"
    info = "INFO", "информация"
    warning = "WARNING", "предупреждение"
    error = "ERROR", "ошибка"
    critical = "CRITICAL", "критическая"


class BrokerTypeEnum(StrEnum):
    redis = "redis", "Redis"
    kafka = "kafka", "Kafka"
    rabbit = "rabbit", "Rabbit MQ"


class NotificationTypeEnum(StrEnum):
    email = "email", "Email"
    sms = "sms", "SMS"


class PirorityLevelEnum(StrEnum):
    low = "low", "Низкий"
    medium = "medium", "Средний"
    high = "high", "Высокий"


class IndexStatusEnum(StrEnum):
    created = "created", "создан"
    skipped = "skipped", "пропущен"
    error = "error", "ошибка"
