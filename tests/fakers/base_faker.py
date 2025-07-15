from typing import Any, Dict, List, TypeVar

from bson.objectid import ObjectId
from pymongo.asynchronous.database import AsyncDatabase

from app.adapters.db.cruds.base import BaseCRUD
from app.adapters.schemas.base import BaseSchema
from app.entities.base import BaseEntity
from app.utils.type_hints import ItemID

S_in = TypeVar("S_in", bound=BaseSchema)
S_out = TypeVar("S_out", bound=BaseEntity)


class FakeBaseCRUD(BaseCRUD):
    _in = S_in
    _out = S_out
    _table = str
    called_count = 0

    def __init__(self, db: AsyncDatabase):
        self.data: list[dict[str, Any]] = []

    def create_id(self):
        return ObjectId()

    async def create(self, data: _in | dict[str, Any]):
        pass

    async def get_by_id(self, item_id: ItemID) -> S_out:
        self.called_count += 1
        item_id = self.convert_id_to_ObjectId(item_id)

        for item in self.data:
            if item["_id"] == item_id:
                return self._out.from_dict(item)

        return None

    async def _get_by_id(self, item_id: ItemID) -> S_out:
        """Внутренний метод для тестирования."""
        item_id = self.convert_id_to_ObjectId(item_id)

        for item in self.data:
            if item["_id"] == item_id:
                return self._out.from_dict(item)

        return None

    async def get_all(
        self,
        filters: dict[str, Any] | None = None,
        limit: int | None = None,
        offset: int | None = None,
        sort: list[tuple[str, int]] | None = None,
    ) -> list[S_out]:

        self.called_count += 1
        result = []
        if "_id" in filters:
            if "$in" in filters["_id"]:
                result = [await self._get_by_id(id) for id in filters["_id"]["$in"]]

        elif "created_at" in filters:
            since = filters["created_at"]["$gte"]
            result = [
                self._out.from_dict(item)
                for item in self.data
                if item["created_at"] >= since
            ]

        return result

    async def update(self, item_id: ItemID, data: dict[str, Any]) -> S_out:
        pass

    async def delete(self, item_id: ItemID) -> bool:
        pass

    async def count(self, filters: dict[str, Any] | None = None) -> int:
        pass

    async def exists(self, item_id: ItemID) -> bool:
        pass

    async def bulk_create(self, data_list: List[Dict[str, Any]]) -> List[str]:
        """Массовое создание документов
        При создании каждого документа, надо присвоить ему _id
        """
        self.called_count += 1
        for item in data_list:
            item["_id"] = self.create_id()

        self.data.extend(data_list)
        print(self.data)
        return [str(item["_id"]) for item in data_list]
