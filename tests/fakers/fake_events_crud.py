from datetime import datetime, timedelta

from pymongo.asynchronous.database import AsyncDatabase

from tests.fakers.base_faker import FakeBaseCRUD

from app.adapters.schemas.events import EventCreateSchema
from app.entities.event import Event

EVENT_TABLE = "events"


class FakeEventCRUD(FakeBaseCRUD):
    """EventCRUD."""

    _in = EventCreateSchema
    _out = Event
    _table = EVENT_TABLE

    def __init__(self, db: AsyncDatabase):
        super().__init__(db)

    async def get_recent_events(self, hours: int = 24) -> list[Event]:
        since = datetime.utcnow() - timedelta(hours=hours)
        return await self.get_all(
            filters={"created_at": {"$gte": since}},
            sort=[("created_at", -1)],
        )
