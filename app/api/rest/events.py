from fastapi import APIRouter, Depends

from app.adapters.schemas.events import EventsCharacteristicsSchema, EventsFilterSchema
from app.adapters.schemas.pagination import PaginationSchema
from app.dependencies.containers import Container
from app.services.events_service import EventService
from app.utils.data_generator import critical_event_generator, random_event_generator

router = APIRouter(prefix="/events", tags=["Events"])


@router.get("/")
async def get_events(
    filter: EventsFilterSchema = Depends(),
    pagination: PaginationSchema = Depends(),
    service: EventService = Depends(Container.event_service),
):
    return await service.get_events_list(
        filter.dict(exclude_unset=True),
        pagination.dict(exclude_unset=True),
    )


@router.get("/types/")
async def get_event_types(
    service: EventService = Depends(Container.event_service),
):
    return await service.get_event_types()


@router.post("/gen-test-data/")
async def gen_events(
    event_characteristics: EventsCharacteristicsSchema,
    service: EventService = Depends(Container.event_service),
):
    if event_characteristics.is_criticals:
        events = list(critical_event_generator(event_characteristics.event_count))
    else:
        events = list(random_event_generator(event_characteristics.event_count))

    return await service.create_events(events)
