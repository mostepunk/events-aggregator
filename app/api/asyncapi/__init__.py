from . import events
from app.settings import config

async_api_router = config.broker.router_instance


async_api_router.include_router(events.router)
