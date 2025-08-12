"""
события разной структуры.
"""

from datetime import datetime

from pydantic import Field, model_validator

from app.adapters.db.utils.expire import calculate_expires_at_by_severity
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
    expires_at: datetime = Field(
        None,
        description="Время истечения события",
    )

    @model_validator(mode="before")
    def validate_expires_at(cls, values):
        if values.get("expires_at") is None:
            values["expires_at"] = (
                calculate_expires_at_by_severity(values.get("severity")),
            )
        return values


class EventSchema(DBSchemaMixin, BaseEventSchema):
    expires_at: datetime = Field(
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
    search: str | None = None


class GeneratedEventsSchema(BaseSchema):
    created_events: EventsCharacteristicsSchema
    created: int
    success: bool
