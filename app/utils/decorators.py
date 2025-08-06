from datetime import datetime
from functools import wraps
from typing import Callable

from app import getLogger
from app.adapters.db.utils.expire import calculate_expires_at_by_severity

logging = getLogger(__name__)


def insert_dates(data):
    if isinstance(data, dict):
        data["created_at"] = data.get("created_at", datetime.now())
        data["updated_at"] = data.get("updated_at", datetime.now())
        data["expired_at"] = data.get(
            "expired_at",
            calculate_expires_at_by_severity(data.get("severity")),
        )
    return data


def insert_created_updated(func: Callable):
    """Декоратор для вставки даты создания и обновления

    Используется для создания документа.
    """

    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        for arg in args:
            if isinstance(arg, (list, tuple)):
                for item in arg:
                    insert_dates(item)
            else:
                insert_dates(arg)

        data = await func(self, *args, **kwargs)
        return data

    return wrapper
