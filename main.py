import asyncio
from pprint import pprint
from uuid import uuid4

from app.adapters.db import get_database, init_mongodb
from app.adapters.db.cruds.event import EventCRUD
from app.adapters.schemas.events import EventCreateSchema
from app.services.events_service import EventService


def event_data():
    data = {
        "event_type": "notification",
        "event_data": {"username": "Pupkin", "redirect_url": "https://example.com"},
        "user_id": str(uuid4()),
        "source": "email",
        "level": "info",
        "tags": ["tag1", "tag2"],
    }
    return EventCreateSchema(**data)


async def main():
    await init_mongodb()

    async with get_database() as db:
        service = EventService(EventCRUD(db))

        data = [event_data().dict() for _ in range(10)]
        res = await service.create_events(data)
        pprint(data)


asyncio.run(main())
