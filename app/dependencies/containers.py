from that_depends import BaseContainer, providers

from app.adapters.db import get_database_injection
from app.adapters.db.cruds.event import EventCRUD
from app.services.events_service import EventService


class Container(BaseContainer):
    db = providers.Resource(get_database_injection)

    events_crud = providers.Factory(EventCRUD, db)
    event_service = providers.Factory(EventService, events_crud)
