from pymongo.asynchronous.database import AsyncDatabase

from app.adapters.db.cruds.base import BaseCRUD
from app.adapters.schemas.events import EventCreateSchema, EventDBSchema

EVENT_TABLE = "events"


class EventCRUD(BaseCRUD[EventCreateSchema, EventDBSchema, EVENT_TABLE]):
    _in_schema = EventCreateSchema
    _out_schema = EventDBSchema
    _table = EVENT_TABLE

    def __init__(self, db: AsyncDatabase):
        super().__init__(db)
