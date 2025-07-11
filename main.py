import asyncio
from pprint import pprint
from uuid import uuid4

from that_depends import Provide, inject

from app.adapters.schemas.events import EventCreateSchema
from app.dependencies.containers import Container
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


@inject
async def main(service: EventService = Provide[Container.event_service]):
    # data = [event_data().dict() for _ in range(10)]
    # await service.create_events(data)

    res = await service.get_recent_events()
    pprint(res)


asyncio.run(main())
