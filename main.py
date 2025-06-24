import asyncio
from pprint import pprint
from uuid import uuid4

from app.adapters.db import get_database, init_mongodb
from app.adapters.db.cruds.event import EventCRUD
from app.adapters.schemas.events import EventCreateSchema


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
        crud = EventCRUD(db)

        # data = event_data()
        # item = await crud.create(data)
        # print(item)

        # data = [event_data().dict() for _ in range(10)]
        # res = await crud.bulk_create(data)
        # print(f"Created {len(res)} events: {res}")

        items = await crud.get_unprocessed_events()
        print(f"Found {len(items)} events")
        pprint(items)


asyncio.run(main())
