import os
from typing import Dict, List

from app.adapters.db.const import MongoCollections


def get_ttl_seconds() -> int:
    """Получение TTL из переменных окружения (в секундах)"""
    ttl_days = int(os.getenv("EVENTS_TTL_DAYS", "30"))
    return ttl_days * 24 * 60 * 60


def get_events_indexes() -> List[Dict]:
    """Определение индексов для коллекции events"""
    return [
        # 1. Основной составной индекс для мониторинга и фильтрации
        {
            "keys": [("type", 1), ("timestamp", -1), ("severity", -1)],
            # "name": "idx_type_timestamp_severity",
        },
        # 2. Индекс для пользовательской активности
        {
            "keys": [("user_id", 1), ("timestamp", -1)],
            # "name": "idx_user_timestamp",
        },
        # 3. Индекс для трейсинга и отладки
        {
            "keys": [("trace_id", 1)],
            # "name": "idx_trace_id",
        },
        # 4. Индекс для анализа по источникам
        {
            "keys": [("source", 1), ("timestamp", -1)],
            # "name": "idx_source_timestamp",
        },
        # 5. TTL индекс для автоматического удаления старых событий
        {
            "keys": [("expires_at", 1)],
            # "name": "idx_expires_at_ttl",
            "expireAfterSeconds": 0,  # Использует значение из поля expires_at
        },
        # 6. Индекс для поиска по session_id (для анализа сессий)
        {
            "keys": [("session_id", 1), ("timestamp", -1)],
            # "name": "idx_session_timestamp",
        },
        # 7. Составной индекс для фильтрации критичных событий по времени
        {
            "keys": [("severity", -1), ("timestamp", -1)],
            # "name": "idx_severity_timestamp",
        },
        # 8. Текстовый индекс для поиска по содержимому (создается последним)
        {
            "keys": [("payload", "text"), ("metadata", "text"), ("type", "text")],
            # "name": "idx_fulltext_search",
            # "default_language": "russian",
            "default_language": "english",
        },
    ]


def get_rules_indexes() -> List[Dict]:
    """Определение индексов для коллекции rules"""
    return [
        # 1. Индекс для быстрого поиска активных правил
        {
            "keys": [("enabled", 1), ("priority", -1)],
            # "name": "idx_enabled_priority",
        },
        # 2. Индекс для поиска правил по типу события
        {
            "keys": [("conditions.type", 1)],
            # "name": "idx_conditions_type",
        },
    ]


def get_metrics_indexes() -> List[Dict]:
    """Определение индексов для коллекции metrics"""
    return [
        # 1. Основной индекс для временных рядов метрик
        {
            "keys": [("metric_type", 1), ("timestamp", -1)],
            # "name": "idx_metric_type_timestamp",
        },
        # 2. Составной индекс для группировки по измерениям
        {
            "keys": [
                ("dimensions.event_type", 1),
                ("dimensions.source", 1),
                ("timestamp", -1),
            ],
            # "name": "idx_dimensions_timestamp",
        },
        # 3. TTL для метрик (обычно хранятся дольше событий)
        {
            "keys": [("expires_at", 1)],
            # "name": "idx_metrics_expires_at_ttl",
            "expireAfterSeconds": 0,
        },
    ]


def get_users_indexes() -> List[Dict]:
    """Определение индексов для коллекции users"""
    return [
        # 1. Уникальный индекс для user_id
        {
            "keys": [("user_id", 1)],
            # "name": "idx_user_id_unique",
            "unique": True,
        },
        # 2. Индекс для поиска по email
        {
            "keys": [("email", 1)],
            # "name": "idx_email",
        },
        # 3. Индекс для фильтрации по роли
        {
            "keys": [("role", 1)],
            # "name": "idx_role",
        },
    ]


def get_index_metrics_indexes() -> List[Dict]:
    """Индексы для служебной коллекции метрик индексов"""
    return [
        {
            "keys": [("collection_name", 1), ("created_at", -1)],
            # "name": "idx_collection_created",
        },
        {
            "keys": [("operation_type", 1), ("created_at", -1)],
            # "name": "idx_operation_created",
        },
    ]


# Основная конфигурация всех индексов
COLLECTIONS_INDEXES: Dict[str, List[Dict]] = {
    MongoCollections.events: get_events_indexes(),
    # MongoCollections.rules: get_rules_indexes(),
    # MongoCollections.metrics: get_metrics_indexes(),
    # MongoCollections.users: get_users_indexes(),
    MongoCollections.index_metrics: get_index_metrics_indexes(),
}


# Справочная информация для документации
INDEXES_DOCUMENTATION = {
    MongoCollections.events: {
        "idx_type_timestamp_severity": "Основной индекс для фильтрации событий по типу, времени и критичности",
        "idx_user_timestamp": "Поиск событий конкретного пользователя за период",
        "idx_trace_id": "Трейсинг - поиск всех событий по trace_id",
        "idx_source_timestamp": "Анализ событий по источникам за период",
        "idx_expires_at_ttl": "TTL индекс для автоматического удаления старых событий",
        "idx_fulltext_search": "Полнотекстовый поиск по содержимому событий",
    }
}
