from dataclasses import dataclass
from datetime import datetime

from app.entities.base import DataBaseEntity


@dataclass
class Event(DataBaseEntity):
    event_id: str
    type: str
    source: str
    severity: int
    timestamp: datetime
    expires_at: datetime

    user_id: str | None = None
    session_id: str | None = None
    trace_id: str | None = None
    payload: dict | None = None
    metadata: dict | None = None
