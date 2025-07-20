"""
события разной структуры.
"""

from typing import Any

from app.adapters.schemas.base import BaseInsertSchemaMixin, BaseSchema, DBSchemaMixin
from app.utils.enums import EventLevelEnum


class BaseEventSchema(BaseSchema):
    event_type: str
    event_data: dict[str, Any]
    source: str | None = None
    user_id: str | None = None  # ???
    level: EventLevelEnum = EventLevelEnum.info
    processed: bool = False
    tags: list[str] = []


class EventCreateSchema(BaseInsertSchemaMixin, BaseEventSchema):
    pass


class EventDBSchema(DBSchemaMixin, BaseEventSchema):
    pass
