from typing import Any

from app import getLogger
from app.adapters.db.cruds.event import EventCRUD
from app.services.base import BaseService

logging = getLogger("EventService")


class EventService(BaseService):
    def __init__(self, repository: EventCRUD):
        super().__init__(repository)

    async def create_event(self, event: dict[str, Any]):
        logging.debug(f"Start creating event. Type: {event.get('type')}")
        return await self.repo.create(event)

    async def create_events(self, data_list: list[dict[str, Any]]):
        logging.debug(f"Start creating events: {len(data_list)}")
        ids = await self.repo.bulk_create(data_list)
        ids = list(map(self.repo.convert_id_to_ObjectId, ids))
        logging.debug(f"Created events: {len(ids)}")
        res = await self.repo.get_all({"_id": {"$in": ids}})
        return [event.to_dict() for event in res]

    async def get_recent_events(self, hours: int = 24):
        res = await self.repo.get_recent_events(hours)
        logging.debug(f"Got recent events: {len(res)}")
        return [event.to_dict() for event in res]
