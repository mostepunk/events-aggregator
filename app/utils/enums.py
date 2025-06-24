from app.utils.base_enum import StrEnum


class EventLevelEnum(StrEnum):
    info = "info", "информация"
    warning = "warning", "предупреждение"
    error = "error", "ошибка"
    critical = "critical", "критическая"
