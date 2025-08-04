from datetime import datetime, timedelta
from typing import Any

from pymongo.asynchronous.database import AsyncDatabase

from app import getLogger
from app.adapters.db.cruds.base import BaseCRUD
from app.adapters.schemas.events import EventCreateSchema
from app.entities.event import Event

EVENT_TABLE = "events"
logging = getLogger("EventCRUD")


class EventCRUD(BaseCRUD[EventCreateSchema, Event]):
    """EventCRUD."""

    _in = EventCreateSchema
    _out = Event
    _table = EVENT_TABLE

    def __init__(self, db: AsyncDatabase):
        super().__init__(db)

    async def get_events_by_type(self, event_type: str) -> list[Event]:
        """Получить события по типу.

        Args:
            event_type (str): event_type

        Returns:
            list[Event]:
        """
        return await self.get_all(filters={"event_type": event_type})

    async def get_events_by_user(self, user_id: str) -> list[Event]:
        """Получить события пользователя.

        Args:
            user_id (str): user_id

        Returns:
            list[Event]:
        """
        return await self.get_all(filters={"user_id": user_id})

    async def get_recent_events(self, hours: int = 24) -> list[Event]:
        """Получить последние события за указанное количество часов.

        Args:
            hours (int): hours

        Returns:
            list[Event]:
        """
        since = datetime.utcnow() - timedelta(hours=hours)
        res = await self.get_all(
            filters={"created_at": {"$gte": since}}, sort=[("created_at", -1)]
        )
        logging.debug(f"Table: <{self._table}>. Found {len(res)} events since: {since}")
        return res

    async def aggregate_events_by_type(self) -> list[dict[str, Any]]:
        """Агрегация событий по типам.

        Returns:
            list[dict[str, Any]]:
        """
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
        """Статистика событий по дням.

        Args:
            days (int): days

        Returns:
            list[dict[str, Any]]:
        """
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
        """Отметить событие как обработанное.

        Args:
            event_id (str): event_id

        Returns:
            Event | None:
        """
        return await self.update(event_id, {"processed": True})

    async def get_unprocessed_events(self) -> list[Event]:
        """Получить необработанные события.

        Returns:
            list[Event]:
        """
        return await self.get_all(
            filters={"processed": {"$ne": True}}, sort=[("created_at", 1)]
        )

    async def get_event_types(self) -> list[str]:
        """Получить типы событий.

        Returns:
            list[str]:
        """
        res = await self.table.find({}, {"type": 1, "_id": 0}).distinct("type")
        return res

    async def get_filtered_events(
        self, filter: dict[str, Any], pagination: dict[str, int | None]
    ) -> list[Event]:
        logging.debug(f"Incoming filter: {filter}")
        mongo_filter = {}

        sort_field = filter.pop("sort_field", "created_at")
        sort_order = filter.pop("sort_order", -1)
        sort = [(sort_field, sort_order)]

        if event_type := filter.get("event_type"):
            event_type = event_type.split(",")
            mongo_filter["type"] = {"$in": event_type}

        if filter.get("hours"):
            since = datetime.utcnow() - timedelta(hours=filter["hours"])
            mongo_filter["created_at"] = {"$gte": since}

        logging.debug(
            f"Table: <{self._table}>. Filters: {mongo_filter} Sorting: {sort}"
        )
        res = await self.get_all(
            filters=mongo_filter,
            sort=sort,
            **pagination,
        )
        logging.debug(f"Found {len(res)} events")

        return res
