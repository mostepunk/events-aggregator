from fastapi import Depends

from app import getLogger
from app.adapters.schemas.events import BaseEventSchema
from app.adapters.schemas.notifications import NotificationSchema
from app.dependencies.containers import Container
from app.services.events_service import EventService
from app.settings import config

logging = getLogger("Broker")


router = config.broker.router_instance


@router.subscriber(config.broker.incoming_event_channel)
async def handle_incoming_message(
    message: BaseEventSchema,
    service: EventService = Depends(Container.event_service),
):
    logging.debug("Received message")
    res = await service.create_event(message.dict())
    logging.debug(f"Created event: {res._id}")


@router.publisher(config.broker.outgoing_notify_channel, schema=NotificationSchema)
async def send_message(message: NotificationSchema):
    logging.debug(f"Sending message: {message}")
