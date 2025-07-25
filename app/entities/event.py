from dataclasses import dataclass
from datetime import datetime

from app.entities.base import BaseEntity


@dataclass
class Event(BaseEntity):
    event_id: str
    type: str
    source: str
    severity: int
    timestamp: datetime
    user_id: str | None = None
    session_id: str | None = None
    trace_id: str | None = None
    payload: dict | None = None
    metadata: dict | None = None
