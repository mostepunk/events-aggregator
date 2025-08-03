from fastapi import APIRouter, Depends

from app.dependencies.containers import Container
from app.services.events_service import EventService
from app.utils.data_generator import random_event_generator

router = APIRouter(prefix="/events", tags=["Events"])


@router.get("/")
async def get_events(
    hours: int = 24,
    service: EventService = Depends(Container.event_service),
):
    return await service.get_recent_events(hours)


@router.get("/gen-test-data/")
async def gen_events(
    event_count: int = 10,
    service: EventService = Depends(Container.event_service),
):
    events = list(random_event_generator(event_count))
    return await service.create_events(events)

