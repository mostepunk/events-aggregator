from datetime import datetime, timezone
from enum import Enum

from pydantic import Field

from app.adapters.schemas.base import BaseSchema


class ProfilerLevelEnum(int, Enum):
    off = 0
    slow = 1
    critical = 2


class ProfilerStartSchema(BaseSchema):
    """
    {
      "level": 2,                           # обязательный: 0/1/2
      "slowms": 100,                        # опционально для level=1
      # Взаимоисключающие параметры времени:
      "timeout_minutes": 10,                # ИЛИ минуты
      "till": "2025-08-26T14:30:00Z"       # ИЛИ точное время
    }
    """

    level: ProfilerLevelEnum = Field(
        example=ProfilerLevelEnum.off,
        description="Уровень профилировщика",
    )
    slowms: int | None = Field(
        None,
        gt=0,
        example=100,
        description="Минимальное время выполнения в миллисекундах",
    )

    till: str | None = Field(
        None,
        example=datetime.now(tz=timezone.utc).isoformat(),
        description="Время окончания профилирования",
    )

    timeout_minutes: int | None = Field(
        None,
        gt=0,
        example=10,
        description="Время ожидания ответа в минутах",
    )
    # TODO: Добавить валидацию


class ProfilerStatusSchema(BaseSchema):
    status: str = Field(
        str,
        description="Состояние профилировщика",
        example="Profiler turrned on",
    )
