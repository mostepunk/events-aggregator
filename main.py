import asyncio
from uuid import uuid4

from that_depends import Provide, inject

from app.adapters.schemas.events import EventCreateSchema
from app.dependencies.containers import Container
from app.services.events_service import EventService
from app.settings import config
from app.utils.data_generator import random_event_data

config.logging.setup_logging()
logging = config.logging.get_logger(__name__)


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
async def check_health(service: EventService = Provide[Container.health_service]):
    await service.get_health()


@inject
async def create_events(service: EventService = Provide[Container.event_service]):
    # data = [event_data().dict() for _ in range(10)]
    # await service.create_events(data)

    for event in random_event_data(10):
        await service.create_event(event)
    # await service.create_events(data)


@inject
async def main(service: EventService = Provide[Container.event_service]):
    # await check_health()
    await create_events()

    # res = await service.get_recent_events()
    # pprint(res)


asyncio.run(main())
