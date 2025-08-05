import asyncio
from typing import Optional

from pymongo import AsyncMongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

from app import getLogger
from app.settings import config

logging = getLogger("MongoConnectionPool")


class MongoConnectionPool:
    """Синглтон для управления подключением к MongoDB

    Обеспечивает эффективное использование connection pool
    """

    _instance: Optional["MongoConnectionPool"] = None
    _client: Optional[AsyncMongoClient] = None
    _database = None
    _is_connected: bool = False

    def __new__(cls) -> "MongoConnectionPool":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def connect(self) -> None:
        """Устанавливает соединение с MongoDB с настройкой connection pool"""

        if self._is_connected:
            logging.warning("Already connected to MongoDB")
            return

        try:
            self._client = AsyncMongoClient(
                config.mongo.uri, **config.mongo.pool_settings
            )
            self._database = self._client[config.mongo.db_name]

            await self._ping_database()
            self._is_connected = True

            logging.info(
                f"Successfully connected to MongoDB: {config.mongo.db_name}, "
                f"Pool size: {config.mongo.min_pool_size}-{config.mongo.max_pool_size}"
            )

        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logging.exception(f"Failed to connect to MongoDB: {e}")
            await self.disconnect()
            raise
        except Exception as e:
            logging.exception(f"Unexpected error during MongoDB connection: {e}")
            await self.disconnect()
            raise

    async def _ping_database(self) -> None:
        """
        Проверяет соединение с базой данных
        Использует команду ping для валидации подключения
        """
        try:
            result = await asyncio.wait_for(
                self._client.admin.command("ping"), timeout=5.0
            )
            if result.get("ok") != 1:
                raise ConnectionFailure("Ping command failed")

        except asyncio.TimeoutError:
            raise ConnectionFailure("Database ping timeout")
        except Exception as e:
            raise ConnectionFailure(f"Database ping failed: {e}")

    async def disconnect(self) -> None:
        """
        Закрывает все соединения в пуле
        Должен вызываться при завершении приложения
        """
        if self._client:
            await self._client.close()
            await asyncio.sleep(0.1)

        self._client = None
        self._database = None
        self._is_connected = False
        logging.info("Disconnected from MongoDB")

    @property
    def database(self):
        """
        Возвращает объект базы данных
        Проверяет наличие активного соединения
        """
        if not self._is_connected or self._database is None:
            raise RuntimeError("Database not connected. Call connect() first.")
        return self._database

    @property
    def client(self) -> AsyncMongoClient:
        """Возвращает клиент MongoDB для прямого доступа"""
        if not self._is_connected or self._client is None:
            raise RuntimeError("Client not connected. Call connect() first.")
        return self._client

    async def get_connection_stats(self) -> dict:
        """
        Возвращает статистику connection pool
        Полезно для мониторинга и отладки
        """
        if self._client is None:
            return {"status": "disconnected"}

        try:
            server_status = await self._database.command("serverStatus")
            connections = server_status.get("connections", {})

            return {
                "status": "connected",
                "current_connections": connections.get("current", 0),
                "available_connections": connections.get("available", 0),
                "total_created": connections.get("totalCreated", 0),
                "pool_settings": {
                    "max_pool_size": self._client.options.pool_options.max_pool_size,
                    "min_pool_size": self._client.options.pool_options.min_pool_size,
                },
            }
        except Exception as e:
            logging.error(f"Failed to get connection stats: {e}")
            return {"status": "error", "error": str(e)}

    async def health_check(self) -> bool:
        """
        Проверка состояния подключения
        Возвращает True если соединение активно
        """
        if not self._is_connected:
            return False

        try:
            await self._ping_database()
            return True
        except Exception as e:
            logging.warning(f"Health check failed: {e}")
            return False
