"""
события разной структуры.
"""

from datetime import datetime

from pydantic import Field

from app.adapters.schemas.base import BaseInsertSchemaMixin, BaseSchema, DBSchemaMixin


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
    pass


class EventDBSchema(DBSchemaMixin, BaseEventSchema):
    pass


class EventsCharacteristicsSchema(BaseSchema):
    event_count: int = Field(10, gt=0, example=10, description="Количество событий")
    is_criticals: bool = Field(
        False, example=False, description="Генерация критичных событий"
    )
