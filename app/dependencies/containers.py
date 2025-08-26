from that_depends import BaseContainer, providers

from app.adapters.db import get_database_injection
from app.adapters.db.cruds.admin import AdminCRUD
from app.adapters.db.cruds.event import EventCRUD
from app.adapters.db.cruds.health_crud import HealthCRUD
from app.services.admin_service import AdminService
from app.services.events_service import EventService
from app.services.health_service import HealthService


class Container(BaseContainer):
    db = providers.Resource(get_database_injection)

    events_crud = providers.Factory(EventCRUD, db)
    event_service = providers.Factory(EventService, events_crud)

    health_crud = providers.Factory(HealthCRUD, db)
    health_service = providers.Factory(HealthService, health_crud)

    admin_crud = providers.Factory(AdminCRUD, db)
    admin_service = providers.Factory(AdminService, admin_crud)
