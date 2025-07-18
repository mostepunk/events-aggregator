from contextlib import asynccontextmanager

from .mongo_client import MongoConnectionPool
from app import getLogger

logging = getLogger(__name__)
mongo_pool = MongoConnectionPool()


@asynccontextmanager
async def get_database():
    """
    Контекстный менеджер для получения базы данных
    Не создает новых соединений - использует существующий пул
    """
    try:
        yield mongo_pool.database
    except Exception as e:
        logging.error(f"Database operation error: {e}")
        raise


async def get_database_injection():
    """Получение соединения для DI."""
    # TODO: костыль, который уедет в startup
    await init_mongodb()
    logging.info(f"Get database connection: {mongo_pool.database}")
    try:
        yield mongo_pool.database
    except Exception as e:
        logging.error(f"Database operation error: {e}")
        raise


async def init_mongodb() -> None:
    """Инициализация MongoDB при старте приложения"""
    await mongo_pool.connect()


async def close_mongodb() -> None:
    """Закрытие соединения при завершении приложения"""
    await mongo_pool.disconnect()


# Пример использования в коде приложения
async def example_usage():
    """Пример правильного использования connection pool"""

    # В startup приложения
    await init_mongodb()

    # В бизнес-логике
    async with get_database() as db:
        collection = db.events
        result = await collection.find_one({"type": "login"})

    # Проверка состояния
    stats = await mongo_pool.get_connection_stats()
    print(f"Connection stats: {stats}")

    # При завершении приложения
    await close_mongodb()


__all__ = [
    "mongo_pool",
    "get_database",
    "init_mongodb",
    "close_mongodb",
]
