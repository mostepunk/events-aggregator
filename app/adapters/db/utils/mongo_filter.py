from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from app.utils.enums import PirorityLevelEnum


@dataclass(frozen=True, slots=True)
class EventFilters:
    event_type: Optional[str] = None
    source: Optional[str] = None
    hours: Optional[int] = None
    priority: Optional[PirorityLevelEnum] = None
    search: Optional[str] = None
    sort_field: str = "created_at"
    sort_order: int = -1

    def to_mongo_filter(self) -> dict[str, Any]:
        """Преобразует в MongoDB фильтр"""
        mongo_filter = {}

        if self.event_type:
            mongo_filter["type"] = {"$in": self.event_type.split(",")}

        if self.source:
            mongo_filter["source"] = {"$in": self.source.split(",")}

        if self.hours:
            since = datetime.now(timezone.utc) - timedelta(hours=self.hours)
            mongo_filter["created_at"] = {"$gte": since}

        if self.priority:
            mongo_filter.update(self._get_severity_filter())

        if self.search:
            mongo_filter["$text"] = {"$search": self.search}

        return mongo_filter

    def _get_severity_filter(self) -> dict:
        severity_map = {
            PirorityLevelEnum.low: {"severity": {"$lte": 3}},
            PirorityLevelEnum.medium: {"severity": {"$gte": 4, "$lte": 6}},
            PirorityLevelEnum.high: {"severity": {"$gte": 7}},
        }
        return severity_map.get(self.priority, {})

    @property
    def sort_options(self) -> list[tuple[str, int]]:
        return [(self.sort_field, self.sort_order)]
