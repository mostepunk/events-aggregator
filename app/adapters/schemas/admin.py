from datetime import datetime, timedelta, timezone
from enum import Enum

from pydantic import Field

from app.adapters.schemas.base import BaseSchema


class ProfilerLevelEnum(int, Enum):
    # off = 0
    slow = 1
    critical = 2


class ProfilerStartSchema(BaseSchema):
    """Схема для запуска профилировщика.

    Правила валидации:
    - Если level = 2: slowms = None
    - Если level = 1 и slowms = None: slowms = 100
    - Если указаны и till и timeout_minutes: Ошибка
    - Если не указаны не till и не timeout_minutes: timeout_minutes = 10
    """

    level: ProfilerLevelEnum = Field(
        example=ProfilerLevelEnum.slow,
        description="Уровень профилировщика",
    )
    slowms: int | None = Field(
        default=None,
        gt=0,
        example=100,
        description="Минимальное время выполнения в миллисекундах",
    )

    till: datetime | None = Field(
        default=None,
        example=(datetime.now(tz=timezone.utc) + timedelta(minutes=10)).isoformat(),
        description="Время окончания профилирования",
    )

    timeout_minutes: int | None = Field(
        default=None,
        gt=0,
        example=10,
        description="Время ожидания ответа в минутах",
    )
    # TODO: Добавить валидацию


class ProfilerStatusSchema(BaseSchema):
    level: int = Field(
        example=ProfilerLevelEnum.slow,
        description="Уровень профилировщика",
    )
    level_verbose: str = Field(
        example=f"Slow operations only (>100ms)",
        description="Человекочитаемое описание уровня",
    )
    slowms: int = Field(
        example=100,
        description="Минимальное время выполнения в миллисекундах",
    )
    till: datetime | None = Field(
        default=None,
        example=(datetime.now(tz=timezone.utc) + timedelta(minutes=10)).isoformat(),
        description="Время окончания профилирования",
    )
