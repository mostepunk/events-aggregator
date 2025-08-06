from datetime import datetime, timedelta

from app import getLogger
from app.settings import config

logging = getLogger("TTL")


def get_ttl_days_by_severity(severity: int | None) -> int:
    """Вычисляет количество дней хранения события.

    Args:
        severity (int): Уровень события

    Returns:
        int:
    """
    if severity is None:
        return config.mongo.expire_at_ttl_days_low

    try:
        severity = int(severity)
    except ValueError:
        logging.warning(f"Invalid severity value: {severity}")
        return config.mongo.expire_at_ttl_days_low

    if severity >= 8:
        return config.mongo.expire_at_ttl_days_critical

    elif severity >= 5:
        return config.mongo.expire_at_ttl_days_medium

    else:
        return config.mongo.expire_at_ttl_days_low


def calculate_expires_at_by_severity(severity: int | None) -> datetime:
    """Вычисляет дату удаления события.

    Args:
        severity (int): Уровень события

    Returns:
        datetime:
    """
    ttl_days = get_ttl_days_by_severity(severity)
    return datetime.utcnow() + timedelta(days=ttl_days)
