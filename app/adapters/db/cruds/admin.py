from pymongo.asynchronous.database import AsyncDatabase

from app import getLogger
from app.adapters.db.const import MongoCollections
from app.adapters.db.cruds.base import BaseCRUD
from app.adapters.schemas.events import EventCreateSchema
from app.entities.event import Event

logging = getLogger("AdminCRUD")


class AdminCRUD(BaseCRUD[EventCreateSchema, Event]):
    _in = EventCreateSchema
    _out = Event
    _table = MongoCollections.profiler_stat

    def __init__(self, db: AsyncDatabase):
        super().__init__(db)
        self.system = self.db["system.profile"]

    async def is_profiler_enabled(self) -> bool:
        pass

    async def set_profiler(self, value: bool) -> bool:
        pass
