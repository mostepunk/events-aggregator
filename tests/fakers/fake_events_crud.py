from datetime import datetime, timedelta, timezone

from pymongo.asynchronous.database import AsyncDatabase

from tests.fakers.base_faker import FakeBaseCRUD

from app.adapters.db.const import MongoCollections
from app.adapters.schemas.events import EventCreateSchema
from app.entities.event import Event


class FakeEventCRUD(FakeBaseCRUD):
    """EventCRUD."""

    _in = EventCreateSchema
    _out = Event
    _table = MongoCollections.events

    def __init__(self, db: AsyncDatabase):
        super().__init__(db)

    async def get_recent_events(self, hours: int = 24) -> list[Event]:
        since = datetime.now(timezone.utc) - timedelta(hours=hours)
        return await self.get_all(
            filters={"created_at": {"$gte": since}},
            sort=[("created_at", -1)],
        )
