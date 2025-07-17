from typing import Any

from app.adapters.db.cruds.event import EventCRUD
from app.services.base import BaseService
from app.settings import config

logging = config.logging.get_logger("EventService")


class EventService(BaseService):
    def __init__(self, repository: EventCRUD):
        super().__init__(repository)

    async def create_events(self, data_list: list[dict[str, Any]]):
        logging.debug(f"Start creating events: {len(data_list)}")
        ids = await self.repo.bulk_create(data_list)
        ids = list(map(self.repo.convert_id_to_ObjectId, ids))
        logging.debug(f"Created events: {len(ids)}")
        return await self.repo.get_all({"_id": {"$in": ids}})

    async def get_recent_events(self):
        res = await self.repo.get_recent_events()
        logging.debug(f"Got recent events: {len(res)}")
        return res
