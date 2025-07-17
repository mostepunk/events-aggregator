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
