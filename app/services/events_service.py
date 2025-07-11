from typing import Any

from app.services.base import BaseService


class EventService(BaseService):
    async def create_events(self, data_list: list[dict[str, Any]]):
        ids = await self.repo.bulk_create(data_list)
        ids = list(map(self.repo.convert_id_to_ObjectId, ids))
        return await self.repo.get_all({"_id": {"$in": ids}})

    async def get_recent_events(self):
        return await self.repo.get_recent_events()
