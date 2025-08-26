import copy
import time
from typing import Any

from pymongo.asynchronous.database import AsyncDatabase

from app import getLogger
from app.adapters.db.const import MongoCollections
from app.adapters.db.index.index_status import IndexCreationStats
from app.adapters.db.index.indexes import COLLECTIONS_INDEXES
from app.utils.enums import IndexStatusEnum

logging = getLogger("IndexManager")


class IndexManager:
    """IndexManager.

    Инициализация и создание индексов.
    """

    def __init__(self, db: AsyncDatabase):
        self.db = db
        self.log_table = self.db[MongoCollections.index_metrics]

    async def initialize_all_indexes(self) -> dict[str, Any]:
        """Инициализация всех индексов.

        Returns:
            dict[str, Any]:
        """
        statistic = {}
        for collection, configs in COLLECTIONS_INDEXES.items():
            result = await self.create_indexes_for_collection(collection, configs)
            statistic[collection] = result
        return statistic

    async def create_indexes_for_collection(
        self,
        table: str,
        index_configs: list[dict[str, Any]],
    ):
        """Создание индексов для определенной коллекции.

        Args:
            table (str): имя коллекции
            index_configs (list[dict[str, Any]]): список конфигов индексов
        """
        collection = self.db[table]
        # Заглушка, если понадобится дропнуть все индексы
        # return await collection.drop_indexes()
        existing_indexes: dict[str, Any] = await collection.index_information()
        creation_error: str | None = None
        stats = IndexCreationStats(self.db, table)

        for config in index_configs:
            start_time = time.time()
            try:
                status: IndexStatusEnum | None = await self._create_index(
                    collection, existing_indexes, table, config
                )
            except Exception as err:
                logging.error(f"Failed to create index: {err}")
                status = IndexStatusEnum.error
                creation_error = str(err)

            duration = time.time() - start_time
            index_name = config.get("name") or self._generate_index_name(
                table, config["keys"]
            )
            if status is None:
                # Ключи для индекса не были переданы
                continue

            await stats.handle_status(
                status,
                index_name,
                duration,
                config,
                creation_error,
            )
        return stats.to_dict()

    async def _create_index(
        self,
        collection: AsyncDatabase,
        existing_indexes: dict[str, Any],
        table: str,
        config: dict[str, Any],
    ) -> IndexStatusEnum | None:
        """Проверка и создание индекса.

        Args:
            collection (AsyncDatabase): подключение к коллекции
            existing_indexes (dict[str, Any]): существующие индексы
            table (str): имя коллекции
            config (dict[str, Any]): конфиг индекса

        Returns:
            IndexStatusEnum | None: Статус создания, либо None, если ключи для индекса не были переданы
        """
        _config = copy.deepcopy(config)

        if (keys := _config.pop("keys", None)) is None:
            logging.warning(f"No keys in index config: {_config}")
            return None

        name = _config.get("name") or self._generate_index_name(table, keys)
        _config["name"] = name

        if name in existing_indexes:
            return IndexStatusEnum.skipped

        is_text_index = _config.pop("_text_index", False)
        if is_text_index:
            await self._drop_existing_text_indexes(collection, existing_indexes)

        index_name = await collection.create_index(keys, background=True, **_config)
        logging.info(f"Created index: {index_name}")
        return IndexStatusEnum.created

    async def _drop_existing_text_indexes(
        self, collection: AsyncDatabase, existing_indexes: dict
    ) -> None:
        """Удаляет все существующие text индексы в коллекции.

        Т.к. MongoDB имеет ограничение в один текстовый индекс.
        Как выход из положения:
        - Создать отдельный поисковый движок используя Elasticsearch
        Но для этого надо дублировать данные в момент записи в MongoDB
        И отправлять их в Elasticsearch

        Args:
            collection (AsyncDatabase): подключение к коллекции
            existing_indexes (dict[str, Any]): существующие индексы
        """
        for index_name, index_info in existing_indexes.items():
            # Проверяем является ли индекс текстовым
            index_key = dict(index_info.get("key"))
            if any(value == "text" for value in index_key.values()):

                logging.info(f"Dropping existing text index: {index_name}")
                await collection.drop_index(index_name)

    @staticmethod
    def _generate_index_name(collection_name: str, keys: list[tuple[str, int]]) -> str:
        """Генерация имени индекса на основе названия коллекции и ключей.

        collection_name = "events"
        keys = [("enabled", 1), ("priority", -1)],
        => "idx_events_enabled_priority"

        Args:
            collection_name (str): название коллекции
            keys (list[tuple[str, int]]): список ключей

        Returns:
            str: имя индекса
        """
        key_names = "_".join([key[0] for key in keys])
        return f"idx_{collection_name}_{key_names}"
