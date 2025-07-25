import asyncio
from pprint import pprint

from that_depends import Provide, inject

from app.dependencies.containers import Container
from app.services.events_service import EventService
from app.settings import config
from app.utils.data_generator import random_event_data

config.logging.setup_logging()
logging = config.logging.get_logger(__name__)


@inject
async def check_health(service: EventService = Provide[Container.health_service]):
    await service.get_health()


@inject
async def create_events(service: EventService = Provide[Container.event_service]):
    # for event in random_event_data(10):
    #     await service.create_event(event)

    events = list(random_event_data(10))
    await service.create_events(events)


@inject
async def main(service: EventService = Provide[Container.event_service]):
    # await check_health()
    # await create_events()

    res = await service.get_recent_events()
    pprint(f"Found {len(res)} recent events")


asyncio.run(main())
