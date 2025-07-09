from datetime import datetime
from typing import Any, Dict, Generic, List, TypeVar

from bson.objectid import ObjectId
from pymongo.asynchronous.database import AsyncDatabase
from pymongo.results import DeleteResult, InsertOneResult, UpdateResult

from app.adapters.schemas.base import BaseSchema
from app.entities.base import BaseEntity
from app.utils.type_hints import ItemID

S_in = TypeVar("S_in", bound=BaseSchema)
S_out = TypeVar("S_out", bound=BaseEntity)


class BaseCRUD(Generic[S_in, S_out]):
    _in: type[S_in]
    _out: type[S_out]
    _table: str

    def __init__(self, db: AsyncDatabase):
        self.db = db
        self.table = self.db[self._table]

    async def create(self, data: S_in | dict[str, Any]) -> S_out:
        if not data:
            # TODO: raise exception NotFoundError
            return None

        if isinstance(data, self._in):
            data = data.dict()

        item: InsertOneResult = await self.table.insert_one(data)

        created_doc = await self.table.find_one({"_id": item.inserted_id})
        if not created_doc:
            # TODO: raise exception DataNotCreated
            raise RuntimeError("Failed to retrieve created document")

        return self._out.from_dict(created_doc)

    async def get_by_id(self, item_id: ItemID) -> S_out:
        item_id = self.convert_id_to_ObjectId(item_id)
        item = await self.table.find_one({"_id": item_id})
        if not item:
            # TODO: raise exception NotFoundError
            return None

        return self._out.from_dict(item)

    async def get_all(
        self,
        filters: dict[str, Any] | None = None,
        limit: int | None = None,
        offset: int | None = None,
        sort: list[tuple[str, int]] | None = None,
    ) -> list[S_out]:
        cursor = self.table.find(filters or {})

        if sort:
            cursor = cursor.sort(sort)

        if limit is not None and offset is not None:
            cursor = cursor.skip(offset).limit(limit)
            documents = await cursor.to_list(length=limit)
        else:
            documents = await cursor.to_list(length=limit or None)

        return [self._out.from_dict(doc) for doc in documents]

    async def update(self, item_id: ItemID, data: dict[str, Any]) -> S_out:
        item_id = self.convert_id_to_ObjectId(item_id)
        data["updated_at"] = datetime.utcnow()

        result: UpdateResult = await self.table.update_one(
            {"_id": item_id},
            {"$set": data},
        )
        if result.matched_count == 0:
            return None

        return await self.get_by_id(item_id)

    async def delete(self, item_id: ItemID) -> bool:
        item_id = self.convert_id_to_ObjectId(item_id)
        result: DeleteResult = await self.table.delete_one({"_id": item_id})
        return result.deleted_count > 0

    async def count(self, filters: dict[str, Any] | None = None) -> int:
        """Подсчитывает количество документов"""
        return await self.table.count_documents(filters or {})

    async def exists(self, item_id: ItemID) -> bool:
        """Проверяет существование документа"""
        object_id = self.convert_id_to_ObjectId(item_id)
        count = await self.table.count_documents({"_id": object_id}, limit=1)
        return count > 0

    async def bulk_create(self, data_list: List[Dict[str, Any]]) -> List[str]:
        """Массовое создание документов"""
        if not data_list:
            return []

        result = await self.table.insert_many(data_list)
        return [str(obj_id) for obj_id in result.inserted_ids]

    @staticmethod
    def convert_id_to_ObjectId(item_id: ItemID) -> ObjectId:
        if isinstance(item_id, str):
            return ObjectId(item_id)
        return item_id
