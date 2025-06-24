from dataclasses import dataclass, field
from typing import Any

from app.entities.base import BaseEntity
from app.utils.enums import EventLevelEnum


@dataclass
class Event(BaseEntity):
    event_type: str
    event_data: dict[str, Any]
    user_id: str | None = None
    source: str | None = None
    level: EventLevelEnum = EventLevelEnum.info
    processed: bool = False
    tags: list[str] = field(default_factory=list)
