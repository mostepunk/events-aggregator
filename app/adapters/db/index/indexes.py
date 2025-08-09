from typing import Dict, List

from app.adapters.db.const import MongoCollections


def get_events_indexes() -> List[Dict]:
    """Определение индексов для коллекции events"""
    return [
        # 1. Основной составной индекс для мониторинга и фильтрации
        {"keys": [("type", 1), ("timestamp", -1), ("severity", -1)]},
        # 2. Индекс для пользовательской активности
        {"keys": [("user_id", 1), ("timestamp", -1)]},
        # 3. Индекс для трейсинга и отладки
        {"keys": [("trace_id", 1)]},
        # 4. Индекс для анализа по источникам
        {"keys": [("source", 1), ("timestamp", -1)]},
        # 5. TTL индекс для автоматического удаления старых событий
        {
            "keys": [("expires_at", 1)],
            "expireAfterSeconds": 0,  # Использует значение из поля expires_at
        },
        # 6. Индекс для поиска по session_id (для анализа сессий)
        {"keys": [("session_id", 1), ("timestamp", -1)]},
        # 7. Составной индекс для фильтрации критичных событий по времени
        {"keys": [("severity", -1), ("timestamp", -1)]},
        # 8. Текстовый индекс для поиска по содержимому (создается последним)
        {
            "keys": [("payload", "text"), ("metadata", "text"), ("type", "text")],
            "name": "idx_events_full_text_search",
            # "default_language": "russian",
            "default_language": "english",
        },
    ]


def get_rules_indexes() -> List[Dict]:
    """Определение индексов для коллекции rules"""
    return [
        # 1. Индекс для быстрого поиска активных правил
        {"keys": [("enabled", 1), ("priority", -1)]},
        # 2. Индекс для поиска правил по типу события
        {"keys": [("conditions.type", 1)]},
    ]


def get_metrics_indexes() -> List[Dict]:
    """Определение индексов для коллекции metrics"""
    return [
        # 1. Основной индекс для временных рядов метрик
        {"keys": [("metric_type", 1), ("timestamp", -1)]},
        # 2. Составной индекс для группировки по измерениям
        {
            "keys": [
                ("dimensions.event_type", 1),
                ("dimensions.source", 1),
                ("timestamp", -1),
            ],
        },
        # 3. TTL для метрик (обычно хранятся дольше событий)
        {
            "keys": [("expires_at", 1)],
            "expireAfterSeconds": 0,
        },
    ]


def get_users_indexes() -> List[Dict]:
    """Определение индексов для коллекции users"""
    return [
        # 1. Уникальный индекс для user_id
        {"keys": [("user_id", 1)], "unique": True},
        # 2. Индекс для поиска по email
        {"keys": [("email", 1)]},
        # 3. Индекс для фильтрации по роли
        {"keys": [("role", 1)]},
    ]


def get_index_metrics_indexes() -> List[Dict]:
    """Индексы для служебной коллекции метрик индексов"""
    return [
        {"keys": [("collection_name", 1), ("created_at", -1)]},
        {"keys": [("operation_type", 1), ("created_at", -1)]},
    ]


# Основная конфигурация всех индексов
COLLECTIONS_INDEXES: Dict[str, List[Dict]] = {
    MongoCollections.events: get_events_indexes(),
    # MongoCollections.rules: get_rules_indexes(),
    # MongoCollections.users: get_users_indexes(),
    MongoCollections.index_metrics: get_index_metrics_indexes(),
}
