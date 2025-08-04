from fastapi import APIRouter, Depends

from app.adapters.schemas.events import (
    EventsCharacteristicsSchema,
    EventSchema,
    EventsFilterSchema,
    GeneratedEventsSchema,
)
from app.adapters.schemas.pagination import PaginationSchema
from app.dependencies.containers import Container
from app.services.events_service import EventService
from app.utils.data_generator import critical_event_generator, random_event_generator

router = APIRouter(prefix="/events", tags=["Events"])


@router.get("/", response_model=list[EventSchema])
async def get_events(
    filter: EventsFilterSchema = Depends(),
    pagination: PaginationSchema = Depends(),
    service: EventService = Depends(Container.event_service),
):
    return await service.get_events_list(
        filter.dict(exclude_unset=True),
        pagination.dict(exclude_unset=True),
    )


@router.get("/types/", response_model=list[str])
async def get_event_types(
    service: EventService = Depends(Container.event_service),
):
    return await service.get_event_types()


@router.post("/gen-test-data/", response_model=GeneratedEventsSchema)
async def gen_events(
    event_characteristics: EventsCharacteristicsSchema,
    service: EventService = Depends(Container.event_service),
):
    if event_characteristics.is_criticals:
        events = list(critical_event_generator(event_characteristics.event_count))
    else:
        events = list(random_event_generator(event_characteristics.event_count))

    res = await service.create_events(events)
    return {
        "created_events": event_characteristics,
        "created": len(res),
        "success": True,
    }
