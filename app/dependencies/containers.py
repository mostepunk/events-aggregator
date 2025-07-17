from that_depends import BaseContainer, providers

from app.adapters.db import get_database_injection
from app.adapters.db.cruds.event import EventCRUD
from app.adapters.db.cruds.health_crud import HealthCRUD
from app.services.events_service import EventService
from app.services.health_service import HealthService


class Container(BaseContainer):
    db = providers.Resource(get_database_injection)

    events_crud = providers.Factory(EventCRUD, db)
    event_service = providers.Factory(EventService, events_crud)

    health_crud = providers.Factory(HealthCRUD, db)
    health_service = providers.Factory(HealthService, health_crud)
