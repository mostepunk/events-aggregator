from typing import Any

from app.services.base import BaseService


class EventService(BaseService):
    async def create_events(self, data_list: list[dict[str, Any]]):
        return await self.repo.bulk_create(data_list)
