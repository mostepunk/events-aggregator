from pydantic import Field

from app.adapters.schemas.base import BaseSchema


class ProfilerStartSchema(BaseSchema):
    timeout: int | None = Field(
        None,
        gt=0,
        example=300,
        description="Время ожидания ответа в секундах",
    )
    level: int | None = Field(
        None,
        example=2,
        description="Уровень профилировщика",
    )


class ProfilerStatusSchema(BaseSchema):
    status: str = Field(
        str,
        description="Состояние профилировщика",
        example="Profiler turrned on",
    )
