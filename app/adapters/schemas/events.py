from typing import Any

from app.adapters.schemas.base import (BaseInsertSchemaMixin, BaseSchema,
                                       DBSchemaMixin)


class BaseEventSchema(BaseSchema):
    event_type: str
    event_data: dict[str, Any]


class EventCreateSchema(BaseInsertSchemaMixin, BaseEventSchema):
    pass


class EventDBSchema(DBSchemaMixin, BaseEventSchema):
    pass
