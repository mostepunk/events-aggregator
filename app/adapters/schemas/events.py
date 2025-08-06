"""
события разной структуры.
"""

from datetime import datetime

from pydantic import Field

from app.adapters.schemas.base import BaseInsertSchemaMixin, BaseSchema, DBSchemaMixin
from app.utils.enums import PirorityLevelEnum


class BaseEventSchema(BaseSchema):
    event_id: str
    type: str
    source: str
    severity: int
    timestamp: datetime
    user_id: str | None = None
    session_id: str | None = None
    trace_id: str | None = None
    payload: dict | None = None
    metadata: dict | None = None


class EventCreateSchema(BaseInsertSchemaMixin, BaseEventSchema):
    expired_at: datetime = Field(
        None,
        description="Время истечения события",
    )


class EventSchema(DBSchemaMixin, BaseEventSchema):
    expired_at: datetime = Field(
        None,
        description="Время истечения события",
    )


class EventsCharacteristicsSchema(BaseSchema):
    event_count: int = Field(10, gt=0, example=10, description="Количество событий")
    is_criticals: bool = Field(
        False, example=False, description="Генерация критичных событий"
    )


class EventsFilterSchema(BaseSchema):
    event_type: str | None = None
    hours: int | None = Field(
        None,
        gt=0,
        example=24,
        description="Период по часам",
    )
    source: str | None = Field(
        None,
        example="auth-service",
        description="Источник событий",
    )
    priority: PirorityLevelEnum | None = None
    sort_field: str | None = "created_at"
    sort_order: int | None = -1


class GeneratedEventsSchema(BaseSchema):
    created_events: EventsCharacteristicsSchema
    created: int
    success: bool
