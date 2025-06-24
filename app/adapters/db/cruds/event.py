from datetime import datetime, timedelta
from typing import Any

from pymongo.asynchronous.database import AsyncDatabase

from app.adapters.db.cruds.base import BaseCRUD
from app.adapters.schemas.events import EventCreateSchema
from app.entities.event import Event

EVENT_TABLE = "events"


class EventCRUD(BaseCRUD[EventCreateSchema, Event]):
    _in_schema = EventCreateSchema
    _out_schema = Event
    _table = EVENT_TABLE

    def __init__(self, db: AsyncDatabase):
        super().__init__(db)

    async def get_events_by_type(self, event_type: str) -> list[Event]:
        """Получить события по типу"""
        return await self.get_all(filters={"event_type": event_type})

    async def get_events_by_user(self, user_id: str) -> list[Event]:
        """Получить события пользователя"""
        return await self.get_all(filters={"user_id": user_id})

    async def get_recent_events(self, hours: int = 24) -> list[Event]:
        """Получить последние события за указанное количество часов"""
        since = datetime.utcnow() - timedelta(hours=hours)
        return await self.get_all(
            filters={"created_at": {"$gte": since}}, sort=[("created_at", -1)]
        )

    async def aggregate_events_by_type(self) -> list[dict[str, Any]]:
        """Агрегация событий по типам"""
        pipeline = [
            {
                "$group": {
                    "_id": "$event_type",
                    "count": {"$sum": 1},
                    "last_event": {"$max": "$created_at"},
                }
            },
            {"$sort": {"count": -1}},
        ]

        cursor = await self.table.aggregate(pipeline)
        return await cursor.to_list(length=None)

    async def aggregate_daily_statistics(self, days: int = 7) -> list[dict[str, Any]]:
        """Статистика событий по дням"""
        since = datetime.utcnow() - timedelta(days=days)

        pipeline = [
            {"$match": {"created_at": {"$gte": since}}},
            {
                "$group": {
                    "_id": {
                        "year": {"$year": "$created_at"},
                        "month": {"$month": "$created_at"},
                        "day": {"$dayOfMonth": "$created_at"},
                    },
                    "count": {"$sum": 1},
                    "types": {"$addToSet": "$event_type"},
                }
            },
            {"$sort": {"_id": 1}},
        ]

        cursor = await self.table.aggregate(pipeline)
        return await cursor.to_list(length=None)

    async def mark_as_processed(self, event_id: str) -> Event | None:
        """Отметить событие как обработанное"""
        return await self.update(event_id, {"processed": True})

    async def get_unprocessed_events(self) -> list[Event]:
        """Получить необработанные события"""
        return await self.get_all(
            filters={"processed": {"$ne": True}}, sort=[("created_at", 1)]
        )
