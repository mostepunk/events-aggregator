from datetime import datetime, timezone

from pymongo.asynchronous.database import AsyncDatabase

from app import getLogger
from app.adapters.db.const import MongoCollections
from app.utils.enums import IndexStatusEnum

logging = getLogger("IndexCreationStats")


class IndexCreationStats:
    """Инкапсулирует логику подсчета и хранения статистики"""

    def __init__(self, db: AsyncDatabase, collection_name: str):
        self.log_table = db[MongoCollections.index_metrics]
        self.collection_name = collection_name

        self.created_count = 0
        self.skipped_count = 0
        self.failed_count = 0
        self.created_indexes = []
        self.skipped_indexes = []
        self.failed_indexes = []

    async def handle_status(
        self,
        status: str,
        index_name: str,
        duration: float,
        config: dict,
        error: str = None,
    ):
        # Обработка статуса индекса
        if status == IndexStatusEnum.created:
            self.add_created(index_name)
            await self._log_index_operation(
                status, index_name, duration, config["keys"]
            )

        elif status == IndexStatusEnum.skipped:
            self.add_skipped(index_name)

        elif status == IndexStatusEnum.error:
            self.add_failed(index_name)
            await self._log_index_operation(
                status, index_name, duration, config["keys"], error
            )

    def add_created(self, index_name: str):
        self.created_count += 1
        self.created_indexes.append(index_name)

    def add_skipped(self, index_name: str):
        self.skipped_count += 1
        self.skipped_indexes.append(index_name)

    def add_failed(self, index_name: str):
        self.failed_count += 1
        self.failed_indexes.append(index_name)

    def to_dict(self) -> dict:
        return {
            "created": self.created_count,
            "skipped": self.skipped_count,
            "failed": self.failed_count,
            "created_indexes": self.created_indexes,
            "skipped_indexes": self.skipped_indexes,
            "failed_indexes": self.failed_indexes,
        }

    async def _log_index_operation(
        self,
        status: str,
        index_name: str,
        duration: float,
        keys: list,
        error: str = None,
    ):
        log_data = {
            "collection_name": self.collection_name,
            "index_name": index_name,
            "status": status,
            "duration": duration,
            "keys": keys,
            "created_at": datetime.now(timezone.utc),
        }

        if error:
            log_data["error"] = error

        await self.log_table.insert_one(log_data)
